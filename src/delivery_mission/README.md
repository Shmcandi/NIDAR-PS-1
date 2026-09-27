# Role 3: Precision Delivery & Automation Subsystem

## Overview
The Delivery Mission controller runs aboard **Drone 2 (Raspberry Pi 5 Hexacopter, SYSID: 2)**. It controls the 5-bay medical parcel magazine rack, guides low-altitude precision hover, and executes an automated drop sequence with hardware verification.

## Core Features
1. **3m Precision Descent:** Arrives at 20m AGL transit altitude, then descends to exactly 3.0m AGL above the target.
2. **5-Second Unstable Hover Abort:** If GPS/wind disturbance causes drift exceeding thresholds for > 5.0 seconds, descent is automatically aborted and the vehicle climbs back to 20m.
3. **Alternating CG Bay Sequence `[1, 5, 2, 4, 3]`:** Dispenses packages from opposite ends towards the center to maintain the hexacopter's Center of Gravity (CG).
4. **GPIO Micro-Switch Verification:** Pins 17, 27, 22, 23, and 24 verify physical release of each package.
5. **Roll-Wiggle Unjamming:** If a switch indicates a stuck package, the drone executes a ±10° roll oscillation maneuver to dislodge the payload before retrying.
6. **Anti-Bounce Throttle Compensation:** Instantly applies downward collective compensation to prevent ground-effect ballooning upon releasing 200g of weight.
7. **12V Acoustic Siren:** Fires relay on GPIO 25 for 2.0s post-drop to alert ground survivors.
8. **Deconflicted RTL:** Returns at 15m AGL (deconflicted with Scout Drone 1 at 20m AGL).

## Running the Mission Node
```bash
python3 delivery_mission_node.py
```
