# AUBO SDK Connection Guide

## Understanding the SDK Architecture

### Two Different Connection Methods:

1. **AUBO Python/C++ SDK (Traditional)**: 
   - Connects to port **8899** on the robot
   - Uses the `libpyauboi5` library (Python) or C++ SDK
   - Example from manual: `robot.connect(ip='192.168.1.10', port=8899)`

2. **AUBO ROS2 Driver (Real-time Control)**:
   - Connects to ports **30004** (RPC) and **30010** (RTDE)
   - Uses the newer SDK version (0.24.1-rc.3)
   - Required for real-time 200-500Hz control loop

## Current Problem

Based on the netstat output from your robot terminal screenshot:
- Port **11211** is listening (memcached - monitoring only)
- Ports **8899**, **30004**, **30010** are NOT listening
- This means the SDK server is not running on your robot

## Solution: Enable SDK Server on Robot

### Option 1: Check Robot Web Interface
1. Access the robot's web interface at `http://192.168.1.10`
2. Look for settings to enable "Remote Control" or "SDK Server"
3. Enable external control interface

### Option 2: Check Teach Pendant (AUBOPE)
1. On the teach pendant interface (PID 2918 process)
2. Navigate to Settings → External Communication
3. Enable "SDK Server" or "Remote Control Mode"
4. Configure network settings if needed

### Option 3: Check for SDK Server Process
The robot should have a service/process for the SDK server. Common names:
- `aubo-sdk-server`
- `aubo_rpc_server`
- `aubo_rtde_server`

Try checking on the robot terminal:
```bash
ps aux | grep -i sdk
ps aux | grep -i rpc
ps aux | grep -i rtde
```

### Option 4: Start SDK Manually (if available)
If there's a script to start the SDK:
```bash
# Look for startup scripts in robot
ls /opt/aubo/
ls /usr/local/aubo/
# Or check systemd services
systemctl status aubo-sdk
systemctl start aubo-sdk
```

## Testing Connection from Your Laptop

### Python SDK Test (Port 8899)
```python
#!/usr/bin/env python3
import sys
sys.path.append('/home/raushan/robotics/aubo/AUBO SDK Package/SDK packages/For Linux OS/libpyauboi5-v1.5.1.x64-for-python3.x/python3.x')

from robotcontrol import *

# Initialize
logger_init()
Auboi5Robot.initialize()

# Create robot instance
robot = Auboi5Robot()
robot.create_context()

# Try to connect
ret = robot.connect('192.168.1.10', 8899)
if ret == RobotErrorType.RobotError_SUCC:
    print("✓ Connected successfully to port 8899!")
    
    # Get robot status
    ret = robot.get_robot_state()
    print(f"Robot state: {ret}")
    
    robot.disconnect()
else:
    print(f"✗ Connection failed with error: {ret}")
    print("SDK server not running on robot!")

# Cleanup
robot.destory_context()
Auboi5Robot.uninitialize()
```

### Test if Port 8899 is Open
```bash
# Test if port 8899 is reachable
nc -zv 192.168.1.10 8899
# Or
telnet 192.168.1.10 8899
```

### Test if Ports 30004/30010 are Open (for ROS2 Driver)
```bash
nc -zv 192.168.1.10 30004
nc -zv 192.168.1.10 30010
```

## ROS2 Driver Requirements

The `aubo_ros2_driver` uses the newer SDK version and requires:
- **Port 30004**: RPC interface for commands
- **Port 30010**: RTDE (Real-Time Data Exchange) for high-frequency data

These are different from the traditional port 8899 used by older SDK.

## Next Steps

1. **Find how to enable SDK on your Aubo i10 robot**
   - Check robot documentation
   - Access teach pendant settings
   - Contact Aubo support if needed

2. **Verify ports are listening**:
   ```bash
   ssh aubo@192.168.1.10  # or access robot terminal
   netstat -tuln | grep -E '8899|30004|30010'
   ```

3. **Once SDK is enabled**, retry the ROS2 driver:
   ```bash
   ros2 launch aubo_ros2_driver aubo_control.launch.py \
       aubo_type:=aubo_i10 \
       robot_ip:=192.168.1.10 \
       use_fake_hardware:=false
   ```

## Important Notes

- The auboControllerServer (PID 2870) is the main controller but doesn't expose SDK ports by default
- Port 11211 (memcached) is for internal monitoring, not for external control
- The SDK server must be explicitly enabled on the robot for external control
- Some robot configurations disable external control for safety reasons

## Reference Files

- Python SDK: `/home/raushan/robotics/aubo/AUBO SDK Package/SDK packages/For Linux OS/libpyauboi5-v1.5.1.x64-for-python3.x/`
- C++ SDK: `/home/raushan/robotics/aubo/AUBO SDK Package/SDK packages/For Linux OS/aubo-sdk-CPP-example/`
- Manuals: `/home/raushan/robotics/aubo/AUBO SDK Package/Manuals/`
- ROS2 Driver: `/home/raushan/robotics/aubo/aubo_ros2_driver/`
