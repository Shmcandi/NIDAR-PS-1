# Product Requirements Document (PRD): 2-Drone RescueSwarm

## 1. Mission Overview
An autonomous, zero-network, heterogeneous 2-drone swarm (1 Scout Drone + 1 Delivery Drone) designed to search a designated zone, locate exactly 5 human survivors, and deliver five 200g medical payload kits within a 30-minute window.

## 2. Core System Constraints
* **Zero External Network:** Strictly no GSM, LTE, 5G, Wi-Fi, or cloud processing. All compute and communication must run locally onboard and over local UHF radio links.
* **Zero Manual Intervention:** Once autonomous flight begins, human operators cannot manually steer, click targets, or trigger payload drops.
* **Setup Time:** The entire ground station and swarm initialization must take less than 5 minutes by a maximum of 2 operators.
* **Weight & Footprint:** Combined fleet weight under 25 kg; takeoff and landing restricted to a 12x12 ft pad.

## 3. Functional Requirements by Role
* **Scout Vision (Role 1):** Detect human shapes from top-down camera feeds at 30+ FPS with under 20ms latency.
* **Geolocation & Routing (Role 4):** Convert 2D detections into 3D GPS coordinates, deduplicate repeated sightings into 5 unique targets, and generate the shortest delivery route.
* **Flight & Safety (Role 2):** Execute autonomous grid search on Drone 1, waypoint navigation on Drone 2, and automatic Return-to-Launch (RTL) failsafes.
* **Precision Delivery (Role 3):** Execute low-altitude hover, center-of-gravity balanced 5-bay payload release, anti-bounce throttle compensation, jam recovery, and siren activation.
* **Ground Station (Role 8):** Display live telemetry, video feed, and drop confirmation alerts on a single air-gapped operator dashboard.
