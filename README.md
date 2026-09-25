# NIDAR-PS-1
ROLLS



-------------------------------------------------------------------------------------------------------------------------------------------------

## 💻 Software & Autonomy Sub-Team
 
### 1. Edge AI Pipeline Architect
* **Domain:** Computer Vision / Edge Computing
* **Hardware/Software:** Primary edge AI processor, daylight optical camera, computer vision model.
* **Core Responsibilities:** 
  * Train and deploy a high-speed object-detection AI model optimized for a bird's-eye perspective.
  * Configure the model to run locally on the scout drone's onboard processor to achieve high frame rates with sub-20ms latency.
  * Extract 2D pixel coordinates and confidence scores for the 5 survivors in real time without triggering thermal throttling on the compute module.

-------------------------------------------------------------------------------------------------------------------------------------------------

### 2. Autopilot, Drop Automation and Failsafes Engineer
* **Domain:** Flight Controls / Embedded Systems
* **Hardware/Software:** Flight controllers, payload release servos, acoustic warning device, automation scripts.
* **Core Responsibilities:** 
  * Program automation scripts on the delivery drone's flight controller to trigger the mechanical servos sequentially upon reaching a target coordinate, cleanly releasing the 200g medical parcels.
  * Automate a post-drop sequence to trigger the onboard acoustic siren to alert survivors.
  * Configure mandatory failsafes: automatic braking at the geofence boundary, and auto-return-to-launch (RTL) upon low battery or telemetry signal loss.

-------------------------------------------------------------------------------------------------------------------------------------------------

### 3. Edge AI and Colourimetry Lead, Scout Bravo
* **Domain:** Image Processing / Computer Vision
* **Hardware/Software:** Secondary edge AI processor, non-IR filtered camera sensor, image processing algorithms.
* **Core Responsibilities:** 
  * Manage the computer vision pipeline for the secondary camera sensor (which lacks an infrared filter).
  * Write color-correction and preprocessing algorithms to neutralize the severe daylight tint caused by the missing IR filter.
  * Ensure the AI model accurately identifies human silhouettes across highly shaded or high-contrast lighting environments.
-------------------------------------------------------------------------------------------------------------------------------------------------

### 4. Geolocation Engine and Target Deduplication Specialist
* **Domain:** Photogrammetry / Spatial Algorithms
* **Hardware/Software:** Satellite navigation (GNSS) modules, telemetry data, trigonometric algorithms.
* **Core Responsibilities:** 
  * Write the photogrammetry algorithm that projects 2D image pixel coordinates into absolute, real-world GPS coordinates (Latitude, Longitude, Altitude) using the drone's altitude and camera pitch.
  * Implement a spatial filtering algorithm to deduplicate targets as the scout circles the area.
  * Ensure the final delivery queue contains exactly 5 unique locations to prevent the delivery drone from visiting the same survivor twice.

---

-------------------------------------------------------------------------------------------------------------------------------------------------

### 5. Airframe Builder and Propulsion Lead
* **Domain:** Mechanical Engineering / Aerodynamics
* **Hardware/Software:** Heavy-lift multirotor frame, agile scout frame, brushless motors, electronic speed controllers, 3D-printed materials.
* **Core Responsibilities:** 
  * Fabricate and structurally assemble the carbon-fiber airframes for both the heavy-lift delivery drone and the agile scout drone.
  * Install the brushless motors, propellers, and speed controllers to ensure proper thrust-to-weight ratios.
  * Design, 3D print, and mechanically assemble the underslung servo-actuated payload magazine for the five 200g medical parcels.

-------------------------------------------------------------------------------------------------------------------------------------------------

### 6. Avionics and Power Distribution Lead
* **Domain:** Electrical Engineering / Power Systems
* **Hardware/Software:** Power distribution boards, high-capacity flight batteries, step-down voltage regulators, anti-vibration mounts.
* **Core Responsibilities:** 
  * Design and solder the main power distribution boards to handle high-voltage flight batteries.
  * Wire step-down voltage regulators to deliver clean, isolated power to flight controllers, edge AI processors, cameras, and servos, preventing mid-air voltage drops.
  * Mount the sensitive flight controllers on damping pads to reduce IMU/gyro vibration noise.

-------------------------------------------------------------------------------------------------------------------------------------------------

### 7. RF Hardware and Wiring Integration Lead
* **Domain:** Radio Frequency (RF) Engineering / Hardware Integration
* **Hardware/Software:** Local telemetry transceivers, analog video transmitters, antennas, shielding.
* **Core Responsibilities:** 
  * Install and precisely position the RF telemetry transceivers and analog video transmitters on both drones.
  * Manage wire routing and antenna placement to keep RF components separated from high-current power cables, eliminating electromagnetic interference (EMI).

-------------------------------------------------------------------------------------------------------------------------------------------------

### 8. Cybersecurity, RF Defence and Ground Control Station Engineer
* **Domain:** Network Security / Ground Operations
* **Hardware/Software:** Operator laptop, ground control dashboard software, telemetry protocol encryption.
* **Core Responsibilities:** 
  * Configure the single-operator dashboard to display live drone telemetry, the 5-target coordinate queue, and video feeds on a single screen.
  * Set up the offline radio network protocol to prevent packet collisions between the active drones.
  * Implement telemetry encryption to prevent replay attacks or hijacked flight commands.
  * Disable all external network hardware (Wi-Fi/Bluetooth) on the ground station to guarantee strict compliance with zero-internet environment rules.

-------------------------------------------------------------------------------------------------------------------------------------------------

## 🔄 System Pipeline & Interconnections

1. **Hardware Foundation:** The `Airframe Builder` constructs the physical chassis. The `Avionics Lead` integrates the power distribution to keep all components alive without brownouts. The `RF Hardware Lead` then mounts the radios, coordinating with Avionics to avoid EMI interference.
2. **Flight & Ground Comm Setup:** The `Autopilot Engineer` programs the flight controllers to govern the hardware, while the `Cybersecurity Engineer` locks down the ground laptop and encrypts the RF telemetry links, creating a secure bridge between the ground and the sky.
3. **In-Flight AI Loop:** The two `Edge AI Leads` process camera feeds locally on the drones to find the 5 survivors. They pass raw pixel data to the `Geolocation Specialist`, who converts those pixels into real-world GPS coordinates and filters out duplicates.
4. **Autonomous Execution:** The `Geolocation Specialist` securely transmits the 5 verified coordinates to the delivery drone. The `Autopilot Engineer's` scripts take over, flying the heavy-lift drone to the targets and triggering the servos to drop the payload.
