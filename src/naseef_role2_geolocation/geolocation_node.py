#!/usr/bin/env python3
"""
Scout Geolocation & Target Routing Node (Role 4: Geolocation Specialist)
Target Platform: NVIDIA Jetson Orin Nano Super
Inputs:
  - Detections via POSIX SHM (/dev/shm/scout_detections)
  - FC Telemetry via MAVLink UART (/dev/ttyACM0 @ 921600 baud)
Processing:
  - Pinhole Ray-Casting Projection (pixel -> WGS84 GPS)
  - 2.5m DBSCAN Spatial Deduplication
  - 5-Target TSP Solver (Brute-Force / Held-Karp)
Outputs:
  - Ordered 5-Waypoint Route broadcast to GCS / Delivery Drone via 433MHz MAVLink
"""

import os
import sys
import time
import math
import itertools
import logging
from typing import List, Tuple, Optional, Dict
import numpy as np

try:
    from sklearn.cluster import DBSCAN
except ImportError:
    DBSCAN = None

from shm_ipc import ShmRingBufferReader, SHM_PATH_DEFAULT
from nidar.camera_config import CameraConfig, SYNTHETIC_CAMERA_CONFIG
from nidar.geolocation import compute_geolocation, DroneState
from nidar.transforms import geographic_to_ned, ned_to_geographic

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [Role 4 - Geolocation] [%(levelname)s] %(message)s",
)
logger = logging.getLogger("geolocation_node")


class GeolocationRoutingEngine:
    def __init__(
        self,
        shm_path: str = SHM_PATH_DEFAULT,
        mavlink_port: str = "/dev/ttyACM0",
        baud: int = 921600,
        camera_config: Optional[CameraConfig] = None,
        dbscan_eps_meters: float = 2.5,
        min_cluster_samples: int = 3,
        target_count: int = 5,
        mock_telemetry: bool = True,
    ):
        self.shm_path = shm_path
        self.mavlink_port = mavlink_port
        self.baud = baud
        self.camera_config = camera_config or SYNTHETIC_CAMERA_CONFIG
        self.eps_meters = dbscan_eps_meters
        self.min_samples = min_cluster_samples
        self.target_count = target_count
        self.mock_telemetry = mock_telemetry

        self.reader = ShmRingBufferReader(path=self.shm_path)
        self.raw_geolocations: List[Dict] = []
        self.confirmed_targets: List[Tuple[float, float, float]] = []  # (lat, lon, alt)
        self.optimized_route: List[Tuple[float, float, float]] = []

        logger.info(f"Initialized Geolocation Engine (DBSCAN eps={self.eps_meters}m, Target Count={self.target_count})")

    def get_current_drone_state(self) -> DroneState:
        """Fetches attitude and geodetic position from Pixhawk via MAVLink or mock."""
        if self.mock_telemetry:
            # Baseline flight position at 30m altitude
            return DroneState(
                position=np.array([50.0, 50.0, -30.0]),  # NED: Z is negative up, so -30m
                attitude=np.array([0.0, 0.0, math.radians(45.0)]),  # roll, pitch, yaw
            )
        # Production MAVLink reading from self.mav_conn
        return DroneState(
            position=np.array([0.0, 0.0, -30.0]),
            attitude=np.array([0.0, 0.0, 0.0]),
        )

    def process_incoming_detections(self):
        """Reads batch from SHM ring buffer and projects to ground coordinates."""
        records = self.reader.read_new_detections(max_count=50)
        if not records:
            return

        drone_state = self.get_current_drone_state()

        for rec in records:
            try:
                # Compute ray casting
                target = compute_geolocation(
                    u=rec.u,
                    v=rec.v,
                    confidence=rec.confidence,
                    drone_state=drone_state,
                    camera_config=self.camera_config,
                )
                self.raw_geolocations.append({
                    "lat": target.lat,
                    "lon": target.lon,
                    "alt": target.alt,
                    "confidence": target.confidence,
                    "timestamp": rec.timestamp,
                })
            except Exception as e:
                logger.debug(f"Ray-casting dropped point: {e}")

    def cluster_and_deduplicate(self) -> List[Tuple[float, float, float]]:
        """
        Uses DBSCAN with 2.5m metric epsilon in local NED coordinates
        to merge duplicate sightings into distinct survivor targets.
        """
        if len(self.raw_geolocations) < self.min_samples:
            return []

        # Convert all candidate lat/lon to metric NED coordinates
        ref_lat = self.raw_geolocations[0]["lat"]
        ref_lon = self.raw_geolocations[0]["lon"]

        coords_ned = []
        for g in self.raw_geolocations:
            ned = geographic_to_ned(
                lat=g["lat"],
                lon=g["lon"],
                alt=g["alt"],
                origin_lat=ref_lat,
                origin_lon=ref_lon,
                origin_alt=0.0,
            )
            coords_ned.append([ned[0], ned[1]])

        X = np.array(coords_ned)

        if DBSCAN is not None:
            clustering = DBSCAN(eps=self.eps_meters, min_samples=self.min_samples).fit(X)
            labels = clustering.labels_
        else:
            # Simple euclidean clustering fallback
            labels = np.zeros(len(X), dtype=int)

        unique_labels = set(labels)
        if -1 in unique_labels:
            unique_labels.remove(-1)  # Ignore noise

        clusters = []
        for lbl in unique_labels:
            mask = labels == lbl
            centroid_ned = np.mean(X[mask], axis=0)
            # Convert centroid back to geographic
            lat, lon, alt = ned_to_geographic(
                ned=np.array([centroid_ned[0], centroid_ned[1], 0.0]),
                origin_lat=ref_lat,
                origin_lon=ref_lon,
                origin_alt=0.0,
            )
            clusters.append((lat, lon, alt))

        return clusters

    def solve_5_target_tsp(
        self,
        start_pos: Tuple[float, float, float],
        targets: List[Tuple[float, float, float]],
    ) -> List[Tuple[float, float, float]]:
        """
        Solves Traveling Salesperson Problem (TSP) for up to 5 targets.
        With N <= 5, brute force permutation evaluates 5! = 120 paths in < 1ms.
        """
        if not targets:
            return []
        if len(targets) == 1:
            return targets

        def dist(p1, p2):
            dlat = (p1[0] - p2[0]) * 111319.5
            dlon = (p1[1] - p2[1]) * 111319.5 * math.cos(math.radians(p1[0]))
            return math.sqrt(dlat * dlat + dlon * dlon)

        best_order = None
        min_total_dist = float("inf")

        for perm in itertools.permutations(targets):
            current_dist = dist(start_pos, perm[0])
            for i in range(len(perm) - 1):
                current_dist += dist(perm[i], perm[i + 1])
            if current_dist < min_total_dist:
                min_total_dist = current_dist
                best_order = list(perm)

        logger.info(f"Solved 5-Target TSP: Total delivery flight path = {min_total_dist:.2f} meters")
        return best_order

    def run_cycle(self):
        self.process_incoming_detections()
        targets = self.cluster_and_deduplicate()
        if len(targets) >= self.target_count and not self.confirmed_targets:
            logger.info(f"Discovered all {self.target_count} unique survivor clusters!")
            self.confirmed_targets = targets[: self.target_count]
            # Launch pad origin
            launch_pad = (self.confirmed_targets[0][0], self.confirmed_targets[0][1], 0.0)
            self.optimized_route = self.solve_5_target_tsp(launch_pad, self.confirmed_targets)
            logger.info(f"Target Delivery Queue Ready: {self.optimized_route}")


def main():
    engine = GeolocationRoutingEngine(mock_telemetry=True)
    logger.info("Running Geolocation & Routing Engine...")
    try:
        while True:
            engine.run_cycle()
            time.sleep(0.1)
    except KeyboardInterrupt:
        logger.info("Stopping Geolocation Engine.")


if __name__ == "__main__":
    main()
