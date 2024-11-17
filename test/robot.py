import rtde_control
import rtde_receive
import time
import math
import numpy as np
import sys


def interpolate_joint_positions(q_start, q_end, num_points=10):
    """
    Interpolate between two sets of joint positions (in degrees), independently for each joint.
    
    Parameters:
    q_start (list): The starting joint positions (in degrees).
    q_end (list): The ending joint positions (in degrees).
    num_points (int): The number of interpolation points (default is 10).
    
    Returns:
    list: A list of interpolated joint positions.
    """
    q_start = np.array(q_start)
    q_end = np.array(q_end)
    
    # Generate num_points linearly spaced values between 0 and 1
    t_values = np.linspace(0, 1, num_points)[:, np.newaxis]  # Reshape for broadcasting
    
    # Perform linear interpolation for each joint separately
    interpolated_positions = q_start + t_values * (q_end - q_start)
    
    # Convert to list of lists (each inner list represents joint positions at an interpolation step)
    return interpolated_positions.tolist()


# Connect to the robot
robot_ip = "192.168.1.100"  # Replace with your robot's IP address
rtde_c = rtde_control.RTDEControlInterface(robot_ip)
rtde_r = rtde_receive.RTDEReceiveInterface(robot_ip)


# Define 10 reachable and safe positions (x, y, z, rx, ry, rz in meters and radians)
# Ensure these positions are within the robot's workspace and avoid joint limits
#p1 = [-0.586, 0.036, -0.303, 2.9, 0.2, 0.2]  # Position 1
#p2 = [-0.2, -0.42, -0.2, 2.54, 1.7, 0.2]  # Position 2

speed = 0.20

home_pose = np.array([-0.14066618616650417, -0.1347854199496408, 0.50, -1.7173584058437448, 2.614817123624442, 0.015662793265223476])


p1 = np.array([-0.68066618616650417, -0.1347854199496408, 0.50, -1.7173584058437448, 2.614817123624442, 0.015662793265223476])



positions = interpolate_joint_positions(home_pose, p1, num_points=5)

 # First movement
print("Starting first moveL")
rtde_c.moveL(p1, speed=0.5, acceleration=0.75, asynchronous=True)
time.sleep(1)  # Allow some movement time
rtde_c.stopL(0.85)  # Smooth deceleration
print("First moveL stopped")

# Second movement
print("Starting second moveL")
rtde_c.moveL(p1, speed=0.5, acceleration=0.75, asynchronous=True)
time.sleep(1)  # Allow some movement time
#rtde_c.stopL(0.5)  # Smooth deceleration
print("Second moveL stopped")

# Third movement
print("Starting third moveL")
rtde_c.moveL(p1, speed=0.5, acceleration=0.75, asynchronous=True)
time.sleep(1)  # Allow some movement time
#rtde_c.stopL(0.5)  # Smooth deceleration
print("Third moveL stopped")


rtde_c.moveL(home_pose, speed=0.5, acceleration=0.75)



exit()

# Fluent movement through positions
try:
    for idx, point in enumerate(positions):
        print(f"Moving to position {idx + 1}: {point}")
        rtde_c.moveL(point, speed=0.5, acceleration=0.75, asynchronous=False)  # Synchronous movement ensures no conflict

        # Adjust speed dynamically after reaching the point
        if idx < len(positions) - 1:  # Avoid stopping after the last point
            rtde_c.speedStop(0.5)  # Smooth deceleration
            print(f"Adjusted speed at position {idx + 1}")

finally:
    # Move back to home position
    print("Returning to home position")
    rtde_c.moveL(home_pose, speed=0.5, acceleration=0.75)
    rtde_c.stopScript()
    rtde_c.disconnect()
    print("Disconnected from the robot.")
exit()


print(f"Interpolated positions: {positions}")

for pos in positions:
    print(f"Moving to position: {pos}")
    rtde_c.moveL(pos, asynchronous=False)

print("Moving to home position")
rtde_c.moveL(home_pose, speed=0.50, acceleration=0.5)  # Linear move
#rtde_c.moveL(p1, speed=0.25, acceleration=0.5)  # Linear move


exit()

# Move to each position
try:
    for i in range(1,6):
        print(f"Moving to position: {i}")
        for deg in p1:
            print(deg)
        radians_positions = [math.radians(deg) for deg in p1]
        rtde_c.moveJ(radians_positions, speed=speed, acceleration=0.5)
    
        #rtde_c.moveJ(p1, speed=0.25, acceleration=0.5)  # Linear move
        p1[0] += 0.1
        #speed -= 0.09
finally:
    rtde_c.disconnect()
    print("Disconnected from the robot.")
