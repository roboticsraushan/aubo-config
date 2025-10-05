#!/usr/bin/env python3
"""
Simple motion test using Aubo SDK on port 8899.
This is a minimal test to verify motion capability.
"""
import sys
import time

sys.path.insert(0, '/home/raushan/robotics/aubo/AUBO SDK Package/SDK packages/For Linux OS/libpyauboi5-v1.5.1.x64-for-python3.x/python3.x')

from robotcontrol import *

def main():
    print("=" * 60)
    print("Aubo Robot Simple Motion Test")
    print("=" * 60)
    
    # Safety check
    response = input("\n⚠️  WARNING: This will move the robot!\nType 'YES' to continue: ")
    if response != 'YES':
        print("Test cancelled.")
        return
    
    # Initialize
    logger_init()
    Auboi5Robot.initialize()
    robot = Auboi5Robot()
    robot.create_context()
    
    try:
        # Connect
        print("\n1. Connecting to robot...")
        ret = robot.connect('192.168.1.10', 8899)
        if ret != RobotErrorType.RobotError_SUCC:
            print(f"✗ Connection failed: {ret}")
            return
        print("✓ Connected")
        
        # Get robot state
        print("\n2. Checking robot state...")
        state = robot.get_robot_state()
        print(f"   Service state: {state}")
        print(f"   States: 0=READY, 1=STARTING, 2=WORKING, 3=CLOSING, 4=CLOSED")
        
        # Check work mode
        work_mode = robot.get_work_mode()
        print(f"   Work mode: {work_mode} (0=simulation, 1=real)")
        
        # Get current position
        print("\n3. Reading current position...")
        waypoint = robot.get_current_waypoint()
        if waypoint and 'joint' in waypoint:
            current = [float(j) for j in waypoint['joint']]
            print(f"   Joints (rad): {[f'{j:.4f}' for j in current]}")
            print(f"   Joints (deg): {[f'{j*57.2958:.2f}' for j in current]}")
        else:
            print(f"   Waypoint data: {waypoint}")
            return
        
        # Startup robot (enables power)
        print("\n4. Starting robot (enabling power)...")
        ret = robot.robot_startup(collision=6)
        if ret != RobotErrorType.RobotError_SUCC:
            print(f"✗ Startup failed: {ret}")
            print("   Robot may already be powered on or in error state.")
        else:
            print("✓ Robot startup command sent")
        
        # Wait for robot to reach WORKING state (critical!)
        print("\n   Waiting for service state to become WORKING (state=2)...")
        max_wait = 10  # seconds
        start_time = time.time()
        service_state = robot.get_robot_state()
        while time.time() - start_time < max_wait:
            service_state = robot.get_robot_state()
            print(f"   Service state: {service_state} ", end='')
            if service_state == 2:  # ROBOT_SERVICE_WORKING
                print("✓ WORKING!")
                break
            elif service_state == 1:  # ROBOT_SERVICE_STARTING
                print("(STARTING...)")
            elif service_state == 0:  # ROBOT_SERVICE_READY
                print("(READY, waiting for startup...)")
            else:
                print(f"(Unexpected state {service_state})")
            time.sleep(0.5)
        else:
            print(f"\n   ⚠️  TIMEOUT: Robot did not reach WORKING state!")
            print(f"   Current service state: {service_state}")
            print("\n   DIAGNOSIS:")
            print("   - The robot is powered on but not in operational state")
            print("   - Check the teach pendant screen for error messages")
            print("   - Verify the STANDBY indicator is lit on control box")
            print("   - Try manually starting a program on teach pendant")
            print("   - The robot may need to be enabled via teach pendant first")
            print("\n   Cannot proceed with motion test.")
            return
        
        time.sleep(1)
        
        # Initialize motion profile
        print("\n5. Initializing motion profile...")
        robot.init_profile()
        
        # Set very conservative speeds
        print("\n6. Setting motion parameters (very slow)...")
        robot.set_joint_maxvelc((0.2, 0.2, 0.2, 0.2, 0.2, 0.2))  # 0.2 rad/s
        robot.set_joint_maxacc((0.3, 0.3, 0.3, 0.3, 0.3, 0.3))   # 0.3 rad/s²
        print("✓ Parameters set")
        
        # Try a very small motion on joint 5
        print("\n7. Moving joint 5 by 0.5 rad (28.65°)...")
        target = list(current)
        target[4] += 0.5  # Very small move
        
        print(f"   From: {[f'{j:.4f}' for j in current]}")
        print(f"   To:   {[f'{j:.4f}' for j in target]}")
        
        # Try with issync=False (asynchronous mode)
        print("\n   Attempting move_joint (async mode)...")
        try:
            ret = robot.move_joint(tuple(target), issync=False)
            print(f"   move_joint returned: {ret}")
        except Exception as move_err:
            print(f"   ✗ move_joint exception: {move_err}")
            ret = None
        
        if ret == RobotErrorType.RobotError_SUCC:
            print("✓ Motion command accepted!")
            print("   Waiting 5 seconds for completion...")
            time.sleep(5)
            
            # Check final position
            final_waypoint = robot.get_current_waypoint()
            if final_waypoint and 'joint' in final_waypoint:
                final = [float(j) for j in final_waypoint['joint']]
                print(f"   Final: {[f'{j:.4f}' for j in final]}")
                print(f"   Moved: {final[4] - current[4]:.4f} rad ({(final[4]-current[4])*57.2958:.2f}°)")
            
            # Move back
            print("\n8. Moving back to original position...")
            ret = robot.move_joint(tuple(current))
            if ret == RobotErrorType.RobotError_SUCC:
                print("✓ Return motion accepted!")
                time.sleep(5)
                print("✓ Motion test complete!")
            else:
                print(f"✗ Return motion failed: {ret}")
        else:
            print(f"✗ Motion failed: {ret}")
            print("   Error code 10023 usually means:")
            print("   - Robot is in wrong mode (check teach pendant)")
            print("   - Safety limits exceeded")
            print("   - Robot needs to be enabled manually first")
        
        # Shutdown
        print("\n9. Shutting down robot...")
        robot.robot_shutdown()
        
    except Exception as e:
        print(f"\n✗ Exception: {e}")
        import traceback
        traceback.print_exc()
        try:
            robot.robot_shutdown()
        except:
            pass
    
    finally:
        print("\n10. Disconnecting...")
        robot.disconnect()
        try:
            robot.destory_context()
        except:
            pass
        Auboi5Robot.uninitialize()
        print("✓ Done")

if __name__ == '__main__':
    main()
