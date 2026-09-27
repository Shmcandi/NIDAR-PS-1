"""
POSIX Shared Memory Zero-Copy IPC Ring Buffer for Scout Detections.

Transfers detections between:
  Role 1 (Container: scout-vision) -> Role 4 (Container: scout-geolocation)
Path: /dev/shm/scout_detections
Packet Size: Exactly 32 bytes per detection record.
"""

import os
import mmap
import struct
import time
from typing import List, Optional, Tuple, NamedTuple

SHM_PATH_DEFAULT = "/dev/shm/scout_detections"
FALLBACK_SHM_NAME = "scout_detections"

# Packet Format (32 bytes per detection):
# double timestamp (8 bytes)
# float32 u (4 bytes) - centroid horizontal pixel
# float32 v (4 bytes) - centroid vertical pixel
# float32 w (4 bytes) - bounding box width
# float32 h (4 bytes) - bounding box height
# float32 confidence (4 bytes) - detection score [0.0 - 1.0]
# uint32 class_id (4 bytes) - target class (0 = human/survivor)
RECORD_FORMAT = "=d5fI"
RECORD_SIZE = struct.calcsize(RECORD_FORMAT)
assert RECORD_SIZE == 32, f"Expected 32 bytes, got {RECORD_SIZE}"

# Header Format (64 bytes aligned):
# uint32 magic (0x4E494441 == 'NIDA')
# uint32 version (1)
# uint32 capacity (number of slots)
# uint32 record_size (32)
# uint64 write_head (monotonically increasing counter)
# uint64 read_head (monotonically increasing counter)
# 32 bytes reserved padding
HEADER_FORMAT = "=IIIIQQ32s"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
assert HEADER_SIZE == 64, f"Expected 64 bytes header, got {HEADER_SIZE}"
MAGIC_ID = 0x4E494441
DEFAULT_CAPACITY = 2048


class DetectionRecord(NamedTuple):
    timestamp: float
    u: float
    v: float
    w: float
    h: float
    confidence: float
    class_id: int

    def pack(self) -> bytes:
        return struct.pack(
            RECORD_FORMAT,
            self.timestamp,
            self.u,
            self.v,
            self.w,
            self.h,
            self.confidence,
            self.class_id,
        )

    @classmethod
    def unpack(cls, buffer: bytes, offset: int = 0) -> "DetectionRecord":
        vals = struct.unpack_from(RECORD_FORMAT, buffer, offset)
        return cls(*vals)


class ShmRingBufferWriter:
    """Zero-copy ring buffer producer writing detections to shared memory."""

    def __init__(self, path: str = SHM_PATH_DEFAULT, capacity: int = DEFAULT_CAPACITY):
        self.path = path
        self.capacity = capacity
        self.total_size = HEADER_SIZE + (self.capacity * RECORD_SIZE)
        self._fd: Optional[int] = None
        self._mmap: Optional[mmap.mmap] = None
        self._write_head = 0
        self._initialize_shm()

    def _initialize_shm(self):
        parent_dir = os.path.dirname(self.path)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)

        self._fd = os.open(self.path, os.O_CREAT | os.O_RDWR | os.O_TRUNC, 0o666)
        os.ftruncate(self._fd, self.total_size)
        self._mmap = mmap.mmap(self._fd, self.total_size, access=mmap.ACCESS_WRITE)

        # Write initial header
        header_bytes = struct.pack(
            HEADER_FORMAT,
            MAGIC_ID,
            1,
            self.capacity,
            RECORD_SIZE,
            0,
            0,
            b"\x00" * 32,
        )
        self._mmap[0:HEADER_SIZE] = header_bytes
        self._mmap.flush()

    def write_detection(
        self,
        u: float,
        v: float,
        w: float,
        h: float,
        confidence: float,
        class_id: int = 0,
        timestamp: Optional[float] = None,
    ) -> int:
        if timestamp is None:
            timestamp = time.time()

        rec = DetectionRecord(timestamp, u, v, w, h, confidence, class_id)
        slot_index = self._write_head % self.capacity
        offset = HEADER_SIZE + (slot_index * RECORD_SIZE)

        self._mmap[offset : offset + RECORD_SIZE] = rec.pack()
        self._write_head += 1

        # Atomically update write_head in header
        struct.pack_into("=Q", self._mmap, 16, self._write_head)
        return self._write_head

    def write_batch(self, detections: List[Tuple[float, float, float, float, float, int]]) -> int:
        ts = time.time()
        for u, v, w, h, conf, cid in detections:
            self.write_detection(u, v, w, h, conf, cid, timestamp=ts)
        return self._write_head

    def close(self):
        if self._mmap is not None:
            self._mmap.flush()
            self._mmap.close()
            self._mmap = None
        if self._fd is not None:
            os.close(self._fd)
            self._fd = None


class ShmRingBufferReader:
    """Zero-copy consumer reading detections from shared memory."""

    def __init__(self, path: str = SHM_PATH_DEFAULT):
        self.path = path
        self._fd: Optional[int] = None
        self._mmap: Optional[mmap.mmap] = None
        self.capacity = DEFAULT_CAPACITY
        self._read_head = 0
        self._connect()

    def _connect(self) -> bool:
        if not os.path.exists(self.path):
            return False
        try:
            self._fd = os.open(self.path, os.O_RDWR)
            file_size = os.path.getsize(self.path)
            if file_size < HEADER_SIZE:
                return False
            self._mmap = mmap.mmap(self._fd, file_size, access=mmap.ACCESS_READ | mmap.ACCESS_WRITE)
            magic, version, capacity, rec_size, w_head, r_head, _ = struct.unpack_from(
                HEADER_FORMAT, self._mmap, 0
            )
            if magic != MAGIC_ID:
                raise ValueError(f"Invalid SHM Magic Header: {hex(magic)}")
            self.capacity = capacity
            self._read_head = w_head  # Start at latest or 0
            return True
        except Exception:
            return False

    def is_connected(self) -> bool:
        return self._mmap is not None

    def read_new_detections(self, max_count: int = 100) -> List[DetectionRecord]:
        if not self.is_connected():
            if not self._connect():
                return []

        w_head = struct.unpack_from("=Q", self._mmap, 16)[0]
        if w_head <= self._read_head:
            return []

        # Avoid reading beyond capacity behind write head
        if w_head - self._read_head > self.capacity:
            self._read_head = w_head - self.capacity

        results = []
        count = 0
        while self._read_head < w_head and count < max_count:
            slot = self._read_head % self.capacity
            offset = HEADER_SIZE + (slot * RECORD_SIZE)
            rec = DetectionRecord.unpack(self._mmap, offset)
            results.append(rec)
            self._read_head += 1
            count += 1

        # Update read_head in header
        struct.pack_into("=Q", self._mmap, 24, self._read_head)
        return results

    def close(self):
        if self._mmap is not None:
            self._mmap.close()
            self._mmap = None
        if self._fd is not None:
            os.close(self._fd)
            self._fd = None
