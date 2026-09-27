
## 1. End-to-End 2-Drone Topology

```text
=============================================================================================
                     DRONE 1: SCOUT QUADCOPTER (Jetson Orin Nano | SYSID: 1)
=============================================================================================
[ RGB Camera ] ──(/dev/video0)──► ┌──────────────────────────────────────────────┐
                                  │ Container: scout-vision (Role 1)             │
                                  │ • TensorRT INT8 Inference (30+ FPS)          │
                                  └──────────────────────┬───────────────────────┘
                                                         │
                                      POSIX Shared Memory (/dev/shm/scout_detections)
                                      Zero-Copy Ring Buffer (32 Bytes per detection)
                                                         │
                                                         ▼
[ Flight Controller ] ◄──(UART /dev/ttyACM0)──► ┌────────────────────────────────┐
  • Search Grid & PIDs    (921600 Baud MAVLink) │ Container: scout-geolocation   │
  • 5.8GHz Analog VTX ───────────────────┐      │ (Role 4)                       │
         │                               │      │ • Time-Sync Attitude Buffer    │
         │ (TELEM 1)                     │      │ • Pixel-to-GPS Ray-Casting     │
         ▼                               │      │ • 2.5m DBSCAN + 5-Target TSP   │
  [ 433MHz Radio ]                       │      └────────────────────────────────┘
         │                               │
=========│===============================│===================================================
         │ (433MHz TDM Encrypted Link)   │ (5.8GHz Analog Video)
         ▼                               ▼
=============================================================================================
                     GROUND CONTROL STATION - LAPTOP (SYSID: 255 | Role 8)
=============================================================================================
  [ Master 433MHz Radio ]                [ 5.8GHz Receiver + USB Capture Card ]
         │                                               │
         └──────────────► ┌──────────────────────────────┴───────────────────────┐
                          │ Air-Gapped GCS Dashboard (QGroundControl / MAVProxy) │
                          │ • HMAC-SHA256 Packet Verification                    │
                          │ • Live Video, 5-Target Queue & Drop Status Alerts    │
                          └──────────────────────────────┬───────────────────────┘
                                                         │
=========┌───────────────────────────────────────────────┘===================================
         │ (433MHz TDM Encrypted Link - Ordered 5-Waypoint Route)
         ▼
=============================================================================================
                   DRONE 2: DELIVERY HEXACOPTER (Raspberry Pi 5 | SYSID: 2)
=============================================================================================
  [ 433MHz Radio ]
         │ (TELEM 1)
         ▼
[ Flight Controller ] ◄──(UART /dev/ttyAMA0)──► ┌────────────────────────────────┐
  • Heavy-Lift PIDs       (921600 Baud MAVLink) │ Container: delivery-mission    │
  • Dynamic Mass Scaling                        │ (Role 3)                       │
         │                                      │ • 3m Precision Descent Logic   │
         ├──(AUX PWM 1-5)──► [ 5x Bay Servos ]  │ • Alternating CG Drop Sequence │
         │                                      │ • Bounce Cut & Roll-Unjam      │
         │                                      └────────┬──────────────────┬────┘
         │                                               │                  │
         └─────────────── [ 5x Drop Micro-Switches ] ────┘                  ▼
                           (GPIO Inputs: /dev/gpiochip4)           [ 12V Siren Relay ]
                                                                    (GPIO 25 Output)
