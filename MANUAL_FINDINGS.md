# AUBO Robot Manual Findings - Enabling Motion Control

## Key Discovery: Robot Service States

According to the SDK-Python Manual (page 18-19), the robot has different **service states** that must be checked:

### Robot Service States:
```
0 = ROBOT_SERVICE_READY      - Ready (not yet started)
1 = ROBOT_SERVICE_STARTING   - Starting up
2 = ROBOT_SERVICE_WORKING    - Working (ready for motion!)
3 = ROBOT_SERVICE_CLOSING    - Shutting down
4 = ROBOT_SERVICE_CLOSED     - Closed/powered off
5 = ROBOT_SERVICE_FAULT_POWER - Power fault
6 = ROBOT_SERVICE_FAULT_BRAKE - Brake fault
7 = ROBOT_SERVICE_FAULT_NO_ROBOT - No robot connected
```

### **CRITICAL ISSUE IDENTIFIED:**
- `robot.get_robot_state()` returns **0** in our tests
- State **0 = ROBOT_SERVICE_READY** means the robot is ready but **NOT YET WORKING**
- **State 2 = ROBOT_SERVICE_WORKING** is required for motion commands!
- After calling `robot_startup()`, we need to wait for state to change from 0 → 1 → 2

## Manual Mode vs Linkage Mode (User Manual Chapter 7.4)

### Manual Mode:
- Default mode for single robot operation
- External IO signals from linkage mode are **ignored**
- Robot controlled **only** through teach pendant or SDK
- This is the mode we're using (MODE button NOT pressed)

### Linkage Mode:
- For coordinated operation with external devices/multiple robots
- Requires MODE MANUAL/LINKAGE button to be **pressed** (button state changes)
- Enables external IO control (LI00-LI05 inputs, LO00-LO03 outputs)
- Can run without teach pendant (press "TEACH PENDANT ENABLE/DISABLE" button)

### Teach Pendant Enable/Disable Button:
- Located on **front panel** of control box
- Purpose: Allow unplugging teach pendant in linkage mode
- When pressed: Teach pendant and its emergency stop are disabled
- We should **NOT** press this button when using teach pendant

## Operational Mode (Safety Feature - Section 8.4.9)

Two operational modes available via safety input:

1. **Normal Mode** (default):
   - External enabling device input is ignored
   - Robot operates normally

2. **Verification Mode**:
   - External enabling device must be active
   - Used for safety verification during commissioning

## Robot Startup Procedure (User Manual Chapter 9)

### Correct Power-On Sequence:
1. **Turn on control box power switch** (ON position)
   - Wait for "POWER" indicator to light up on front panel

2. **Select working mode**:
   - Use MODE MANUAL/LINKAGE button on control box
   - **Manual Mode**: Button in default (out) position
   - **Linkage Mode**: Button pressed in

3. **Wait for "STANDBY" indicator** to light up (important!)

4. **Power on teach pendant**:
   - Press power button on teach pendant for ~1 second
   - Blue LED will appear
   - Teach pendant screen will light up

5. **Login to AUBOPE software** on teach pendant

6. **Use SDK to startup robot**:
   - Call `robot_startup(collision=6)` via SDK
   - **Wait for service state to become 2 (WORKING)**
   - Only then can motion commands be executed

## Working Mode Settings (SDK Manual page 21)

### Two Working Modes:
- **0 = Simulation Mode**: For testing without real robot movement
- **1 = Real Robot Mode**: For actual robot control

### SDK Functions:
- `set_work_mode(mode)` - Set the mode (0 or 1)
- `get_work_mode()` - Get current mode

**Note**: This is different from Manual/Linkage mode on control box!

## Why Our Motion Commands Fail (Error 10023)

### Root Cause:
Our test shows:
```
Robot state: 0 (ROBOT_SERVICE_READY)
Work mode: 1 (real robot)
```

**The problem**: State 0 means robot is READY but not WORKING!

### Solution:
1. Check service state after `robot_startup()`
2. Wait for state to transition: 0 → 1 → 2
3. Only attempt motion when state == 2 (ROBOT_SERVICE_WORKING)
4. The SDK function to check state is: `get_robot_service_state()` (not `get_robot_state()`)

## Additional Notes from Manual

### Force Control (Optional):
- Can be enabled in Safety Config page of AUBOPE software
- "Enable Force Control in Non-Stop State" checkbox
- Required for force control in Linkage mode

### Emergency Stop Behavior:
- Teach pendant emergency stop is always active (unless teach pendant disabled)
- External emergency stop can be connected via safety IO
- Robot will not move if any emergency stop is active

### Collision Detection:
- Collision class: 0-10 (set in `robot_startup()`)
- Higher number = more sensitive
- We're using 6 (moderate sensitivity)

## Recommended Next Steps

1. **Update test script to check service state**:
   ```python
   # After robot_startup()
   service_state = robot.get_robot_service_state()
   while service_state != 2:  # Wait for WORKING state
       time.sleep(0.5)
       service_state = robot.get_robot_service_state()
   ```

2. **Verify STANDBY indicator** is lit on control box before running tests

3. **Check teach pendant** is properly logged in to AUBOPE software

4. **Ensure no emergency stops** are active (check teach pendant screen for errors)

5. **Try initializing profile after confirming WORKING state**

## Reference
- AUBO-i5 & CB-M User Manual V4.5.13 (Chapter 7.4, 8.4.9, Chapter 9)
- SDK-Python_Manual_EN_V1.0 (Functions 37, 43, 44, 45)
