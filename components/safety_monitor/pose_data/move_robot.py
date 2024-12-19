from utils.robot_controller import RobotController
import numpy as np

ROBOT_IP = "192.168.1.100"
robot_controller = RobotController(ROBOT_IP)

# Define the target joint positions
positions = [
    np.array([2.43, -130.48, 95.77, 304.95, 269.33, 261.24]), # Intermediata/home position
    np.array([-35.01, -73.70, 84.80, 256.20, 269.29, 261.24]), # Place position
    np.array([68.05, -66.47, 87.16, 250.25, 270.29, 271.17]),  # Above pick up 1. component
    np.array([68.53, -64.05, 90.21, 244.84, 270.31, 271.68]),  # Pick up 1. component
    np.array([68.05, -70.09, 66.97, 274.06, 270.22, 271.07]),  # Above pick up 1. component when grasped
    np.array([69.07, -74.42, 98.29, 247.50, 270.32, 272.54]),  # Above pick up 2. component
    np.array([69.03, -71.71, 102.11, 240.99, 270.32, 272.53]), # Pick up 2. component
    np.array([69.07, -79.10, 78.95, 271.52, 270.26, 272.43]),  # Above pick up 2. component when grasped
    np.array([69.50, -83.71, 111.47, 242.33, 270.32, 272.55]), # Above pick up 3. component
    np.array([69.50, -80.99, 114.47, 236.61, 270.32, 272.57]), # Pick up 3. component
    np.array([69.50, -89.82, 91.32, 268.59, 270.26, 272.43]),  # Above pick up 3. component when grasped
    np.array([69.61, -92.89, 119.87, 243.11, 270.32, 272.71]), # Above pick up 4. component
    np.array([69.78, -88.92, 123.92, 235.09, 270.32, 272.93]), # Pick up 4. component
    np.array([69.62, -98.70, 99.53, 269.27, 270.26, 272.59])   # Above pick up 4. component when grasped
]


home_pose = np.array([-0.14066618616650417, -0.1347854199496408, 0.5007380032923527, -0.29084513888394903, 3.12302361256465, 0.021555350542996385])
robot_controller.move_to_cartesian_pose(home_pose, velocity=0.05, acceleration=0.3, blend=0)

# # File path for saving TCP poses
# output_file = 'tcp_poses.txt'
# # Loop through each target position
# for position in positions:
#     if robot_controller.move_to_position(position):
#         # Get TCP pose after reaching each position
#         tcp_pose = robot_controller.get_tcp_pose()
#         print("Reached position:", position)
#         print("TCP Pose:", tcp_pose)
        
#         # Append TCP pose to the file
#         with open(output_file, 'a') as file:
#             file.write(" ".join(map(str, tcp_pose)) + "\n")
#     else:
#         print("Failed to move to position:", position)

# print(f"TCP poses saved to {output_file}")
