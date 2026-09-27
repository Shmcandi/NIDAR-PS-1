# NIDAR RescueSwarm — System Constants & Hardware Memory Map

**Classification:** Global Hardware & System Parameters Reference  
**Scope:** Flight Controllers, Companion Computers, Docker Containers, Ground Station  

---

## 1. MAVLink System Identifiers (SYSIDs)

| Node | System ID (`SYSID_THISMAV`) | Component ID | Hardware Platform |
| :--- | :--- | :--- | :--- |
| **Drone 1 (AI Scout Quad)** | **1** | 1 | NVIDIA Jetson Orin Nano Super + Pixhawk 2.4.8 |
| **Drone 2 (Delivery Hexa)** | **2** | 1 | Raspberry Pi 5 + Pixhawk 2.4.8 |
| **Ground Control Station (GCS)** | **255** | 190 | Linux Laptop (QGroundControl / MAVProxy) |

---

## 2. Linux Device Nodes & Inter-Process Communication

| Device / Path | Node | Subsystem / Role | Description |
| :--- | :--- | :--- | :--- |
| `/dev/video0` | Drone 1 | Role 1 (Vision) | Arducam IMX477 CSI/V4L2 camera capture stream |
| `/dev/ttyACM0` | Drone 1 | Role 4 (Geolocation) | Jetson USB-to-UART bridge to Pixhawk FC (`921600` baud) |
| `/dev/ttyAMA0` | Drone 2 | Role 3 (Delivery) | Raspberry Pi 5 UART to Pixhawk FC (`921600` baud) |
| `/dev/shm/scout_detections` | Drone 1 | Role 1 $\leftrightarrow$ Role 4 | Zero-copy POSIX shared memory ring buffer (32 bytes/rec) |
| `/dev/gpiochip4` | Drone 2 | Role 3 (Delivery) | Raspberry Pi 5 RP1 GPIO controller |

---

## 3. Raspberry Pi 5 GPIO Pin Mappings (Role 3 Delivery)

| GPIO Pin (BCM) | Physical Header Pin | Function | Electrical Logic |
| :--- | :--- | :--- | :--- |
| **GPIO 17** | Pin 11 | Bay 1 Micro-Switch | Pulled-Up Input: `LOW` = Package Present, `HIGH` = Dropped |
| **GPIO 27** | Pin 13 | Bay 2 Micro-Switch | Pulled-Up Input: `LOW` = Package Present, `HIGH` = Dropped |
| **GPIO 22** | Pin 15 | Bay 3 Micro-Switch | Pulled-Up Input: `LOW` = Package Present, `HIGH` = Dropped |
| **GPIO 23** | Pin 16 | Bay 4 Micro-Switch | Pulled-Up Input: `LOW` = Package Present, `HIGH` = Dropped |
| **GPIO 24** | Pin 18 | Bay 5 Micro-Switch | Pulled-Up Input: `LOW` = Package Present, `HIGH` = Dropped |
| **GPIO 25** | Pin 22 | 12V Acoustic Siren Relay | Active-High Output: `HIGH` = Relay Energized / Siren On |

---

## 4. Operational Altitudes & Flight Parameters

| Parameter | Drone 1 (Scout) | Drone 2 (Delivery) | Units |
| :--- | :--- | :--- | :--- |
| **Survey / Transit Altitude** | 30.0 | 20.0 | meters AGL |
| **Payload Release Altitude** | N/A | 3.0 | meters AGL |
| **Deconflicted RTL Altitude** | **20.0** | **15.0** | meters AGL |
| **Cruise Speed** | 10.0 | 8.0 | m/s |
| **Max Ascent Speed** | 2.5 | 2.0 | m/s |
| **Precision Descent Speed** | N/A | 0.8 | m/s |

---

## 5. RF & Radio Constants

| Parameter | 433 MHz MAVLink Mesh | 5.8 GHz Analog FPV |
| :--- | :--- | :--- |
| **Modulation / Protocol** | SiK Firmware (FHSS) | Analog NTSC/PAL FM |
| **Network ID (`NET_ID`)** | 25 | N/A |
| **Channel Count** | 50 Hopping Channels | Drone 1: CH1 (5705 MHz), Drone 2: CH2 (5725 MHz) |
| **Baud Rate (Air)** | 57,600 baud | N/A |
| **TX Power** | 500 mW (Air) / 1000 mW (GCS) | 350 mW |
