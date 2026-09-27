# NIDAR Competition Rules, Air-Gap Standards & Failsafe Policies

**Document:** Competition Compliance, Failsafe Architecture & Protocol Enforcement  
**Applicability:** Full Fleet (Drone 1 Scout, Drone 2 Delivery, Ground Station SYSID 255)  

---

## 1. Rule 5 — Absolute Zero External Network & Air-Gap Compliance

### 1.1 Regulatory Mandate
> **Rule 5 Absolute Prohibition:** Teams shall not rely on GSM, LTE, 5G, public Wi-Fi, internet connectivity, or cloud-based communication. Any active cellular radio, internet connection, or external network handshake detected during the mission results in **immediate team disqualification**.

### 1.2 rfkill Enforcement & Network Hardware Locking
All computing nodes (Jetson Orin Nano, Raspberry Pi 5, GCS Laptop) must enforce hard air-gap isolation before arming:
1. **Physical Removal:** No cellular modems, LTE dongles, or Wi-Fi dongles attached to any USB port.
2. **Kernel rfkill Block:** Executed at system boot via systemd:
   ```bash
   rfkill block all
   ```
3. **Interface Teardown:**
   ```bash
   ip link set wlan0 down 2>/dev/null || true
   ip link set eth0 down 2>/dev/null || true
   ```
4. **Pre-Flight Air-Gap Verification Command:**
   ```bash
   rfkill list
   # Expected output: Soft blocked: yes / Hard blocked: yes for Wireless LAN and Bluetooth
   ```

### 1.3 Permitted RF Communication Links Only
- **Command & Telemetry:** 433 MHz Point-to-Multipoint SiK Radio Mesh (Closed local MAVLink protocol, baud rate 57,600).
- **Situational Awareness Video (Rule 4):** 5.8 GHz Analog FPV Video Transmitters (Boscam CH1 / CH2, non-overlapping channels).

---

## 2. Zero Manual Intervention Protocol

### 2.1 Autonomous Operation Mandate
From the moment the initial mission start command (`AUTO` mode trigger) is sent at T-00:00:
- **No manual steering:** Pilot sticks on RC transmitters must remain centered.
- **No manual target tagging:** GCS operators are forbidden from clicking on video streams to guide drones or confirm survivor positions.
- **No manual payload triggers:** Drop mechanisms must be actuated solely by companion computer onboard state machines.
- **Human Pilot Role:** The human pilot holds the RC transmitter exclusively as a safety observer with finger resting on the emergency hardware RTL / Kill switch.

---

## 3. Deconflicted Return-To-Launch (RTL) Altitudes

To prevent mid-air collisions in the event of simultaneous low battery, geofence breach, or mission completion:

| Vehicle | System ID | Search / Cruise Alt | RTL Failsafe Altitude | Separation Margin |
| :--- | :--- | :--- | :--- | :--- |
| **Drone 1 (Scout Quad)** | `SYSID: 1` | 30.0 m AGL | **20.0 m AGL** | $+5.0\text{ m}$ vertical buffer |
| **Drone 2 (Delivery Hexa)** | `SYSID: 2` | 20.0 m AGL | **15.0 m AGL** | Safe vertical tier |

**Flight Controller Parameters:**
- Drone 1 Pixhawk: `RTL_ALT = 2000` (20 meters in cm)
- Drone 2 Pixhawk: `RTL_ALT = 1500` (15 meters in cm)

When both drones trigger RTL simultaneously, Drone 1 cruises over Drone 2 with a strict 5.0-meter vertical separation corridor, completely eliminating mid-air collision hazards over the launch pad.

---

## 4. Flight Controller Failsafes Matrix

| Failsafe Condition | ArduPilot Parameter | Threshold | Autopilot Action | Operator Override |
| :--- | :--- | :--- | :--- | :--- |
| **Battery Critical Low** | `BATT_FS_CRT_ACT` | $< 10.0\%$ capacity | Emergency Land Immediately | None |
| **Battery Warning Low** | `BATT_FS_LOW_ACT` | $< 15.0\%$ capacity | Return-To-Launch (RTL) | Manual RC takeover |
| **Telemetry Link Loss** | `FS_GCS_ENABL` | No heartbeat for 15s | Autonomous RTL | RC Link still active |
| **RC Transmitter Loss** | `FS_THR_ENABLE` | PWM loss for 500ms | Autonomous RTL | Auto |
| **Geofence Boundary Breach** | `FENCE_TYPE = 3` | Transgress polygon | Auto-Brake + RTL | None |
| **GPS EKF Variance** | `FS_EKF_ACTION` | Compass/GPS variance $> 0.8$ | Altitude Hold / Land | Manual PosHold |
| **Motor Loss (Hexacopter)** | `MOT_FAIL_SAFE` | RPM anomaly on 1 arm | 5-Motor Asymmetric RTL | Auto |

---

## 5. Offline Docker Standards (`pull_policy: never`)

In strict compliance with Rule 5, runtime environments must not attempt network communication:
1. **Never Pull Images at Runtime:**
   All `docker-compose.yml` services must declare:
   ```yaml
   pull_policy: never
   ```
2. **Local Image Pre-Loading:**
   All container images (`scout-vision:latest`, `scout-geolocation:latest`, `delivery-mission:latest`) are built in the workshop and stored in local Docker daemon storage prior to field entry.
3. **No External Package Managers on Boot:**
   No `pip install`, `apt update`, or network package fetching is permitted in container entrypoints or systemd units.
