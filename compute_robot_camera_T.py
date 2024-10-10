import cv2
from scipy.spatial.transform import Rotation as R
import numpy as np

def load_aruco_poses(filename):
    poses = []
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip().strip('[]')  # Remove brackets and whitespace
            if line:
                pose = list(map(float, line.split()))  # Split on whitespace
                poses.append(pose)
    return np.array(poses)

def load_robot_poses(filename):
    poses = []
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip().strip('[]')  # Remove brackets and whitespace
            if line:
                pose = list(map(float, line.split(',')))  # Split by comma
                poses.append(pose)
    return np.array(poses)

# Load ArUco (camera frame) and robot (base frame) poses
aruco_poses = load_aruco_poses('pose_data/aruco_poses.txt')
robot_poses = load_robot_poses('pose_data/robot_poses.txt')

# Extract translation and rotation vectors
aruco_translations = aruco_poses[:, :3]  # ArUco translation in camera frame
aruco_rotations = aruco_poses[:, 3:]     # ArUco rotations (Euler angles) in camera frame
robot_translations = robot_poses[:, :3]  # TCP translation in robot base frame
robot_rotations = robot_poses[:, 3:]     # TCP rotations (Euler angles) in robot base frame

# Convert Euler angles to rotation matrices
aruco_rot_matrices = np.array([R.from_euler('xyz', rot).as_matrix() for rot in aruco_rotations])
robot_rot_matrices = np.array([R.from_euler('xyz', rot).as_matrix() for rot in robot_rotations])

# Perform hand-eye calibration to find transformation from camera to robot base frame
R_cam2base, t_cam2base = cv2.calibrateHandEye(
    R_gripper2base=robot_rot_matrices, t_gripper2base=robot_translations,
    R_target2cam=aruco_rot_matrices, t_target2cam=aruco_translations
)

# Display the results
print("Rotation Matrix from Camera to Robot Base:")
print(R_cam2base)
print("\nTranslation Vector from Camera to Robot Base:")
print(t_cam2base)
