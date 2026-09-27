# Role 1: Edge AI Pipeline Architect (Scout Vision)

## Overview
The Scout Vision subsystem runs aboard **Drone 1 (Jetson Orin Nano Super, SYSID: 1)**. It captures 1080p aerial frames from the nadir-facing Arducam IMX477 camera, executes TensorRT INT8 YOLOv8 inference, and writes detected survivor coordinates directly into a POSIX shared memory ring buffer.

## Architecture
- **Camera Ingestion:** Hardware-accelerated GStreamer pipeline via `/dev/video0`.
- **Inference Engine:** TensorRT INT8 quantized model achieving **30+ FPS** with **< 20ms end-to-end latency**.
- **Inter-Process Communication:** POSIX Shared Memory ring buffer mounted at `/dev/shm/scout_detections`.
- **Packet Structure:** Exactly 32 bytes per detection record:
  - `double timestamp` (8 bytes)
  - `float32 u` (4 bytes) - centroid horizontal pixel
  - `float32 v` (4 bytes) - centroid vertical pixel
  - `float32 w` (4 bytes) - bounding box width
  - `float32 h` (4 bytes) - bounding box height
  - `float32 confidence` (4 bytes) - detection score [0.0 - 1.0]
  - `uint32 class_id` (4 bytes) - class ID (0 = human/survivor)

## Running the Vision Node
```bash
python3 vision_node.py --camera /dev/video0 --engine /opt/models/yolov8s_sar_int8.engine
```

For synthetic or testing environments:
```bash
python3 vision_node.py --mock
```
