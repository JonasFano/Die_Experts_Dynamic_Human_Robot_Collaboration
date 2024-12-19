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
                pose = list(map(float, line.split()))  # Split by comma
                poses.append(pose)
    return np.array(poses)


if __name__ == "__main__":
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


    # Perform hand-eye calibration the other way around to find transformation from robot base to camera
    R_robot2cam, t_robot2cam = cv2.calibrateHandEye(
        R_gripper2base=aruco_rot_matrices, t_gripper2base=aruco_translations,  # ArUco as gripper-to-base
        R_target2cam=robot_rot_matrices, t_target2cam=robot_translations        # Robot as target-to-camera
    )

    # Display the results
    print("Rotation Matrix from Robot Base to Camera:")
    print(R_robot2cam)
    print("\nTranslation Vector from Robot Base to Camera:")
    print(t_robot2cam)



    # TCP_in_robot_base = [-0.45329, 0.0338, 0.76916]
    TCP_in_robot_base = [-0.66082, -0.00275,  0.80091]

    # Construct the transformation matrix
    T_robot2cam = np.eye(4)  # Start with a 4x4 identity matrix
    T_robot2cam[:3, :3] = R_robot2cam  # Set the rotation part
    T_robot2cam[:3, 3] = t_robot2cam.flatten()  # Set the translation part

    TCP_in_camera_frame = np.dot(T_robot2cam, np.append(TCP_in_robot_base, 1))

    # Extract the position of the TCP in the camera frame
    tcp_position_in_camera = TCP_in_camera_frame[:3]

    # actual_tcp_in_camera = [-0.2443, -0.04195, 0.74734]
    actual_tcp_in_camera = [-0.11651, -0.11284,  0.82633]

    # Output the result
    print("TCP position in the camera frame (x, y, z):", tcp_position_in_camera)
    print("Actual TCP in robot base frame: ", TCP_in_robot_base)
    print("Actual TCP in camera frame: ", actual_tcp_in_camera)