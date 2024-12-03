import pyrealsense2 as rs
import rtde_receive
import cv2
import numpy as np
from scipy.spatial.transform import Rotation as R
import os

# Set global print options
np.set_printoptions(precision=5, suppress=True)

MARKER_SIZE_METERS = 0.057

# Camera position and orientation in the world frame (update these values as per your setup)
CAMERA_TRANSLATION = np.array([0, 0, 0])  # Replace with the actual camera position in world coordinates
CAMERA_ROTATION = R.from_euler('xyz', [0, 0, 0]).as_matrix()  # Replace with actual camera orientation in world coordinates

# Transformation from camera to world frame
T_CAMERA_TO_WORLD = np.eye(4)
T_CAMERA_TO_WORLD[:3, :3] = CAMERA_ROTATION
T_CAMERA_TO_WORLD[:3, 3] = CAMERA_TRANSLATION

def Rodrigues(rvec):
    """ Convert rotation vector to rotation matrix. """
    r = R.from_rotvec(rvec)
    return r.as_matrix()

def create_transformation_matrix(translation, rotation):
    """ Create a transformation matrix from translation and rotation. """
    R_matrix = Rodrigues(rotation)
    T_matrix = np.eye(4)
    T_matrix[:3, :3] = R_matrix
    T_matrix[:3, 3] = translation
    return T_matrix

def calculate_marker_position(marker_id, corners, ids):
    marker_indices = np.where(ids == marker_id)[0]
    if len(marker_indices) == 0:
        return None

    marker_corners = corners[marker_indices[0]].reshape((4, 2))
    obj_points = np.array([[0, 0, 0],
                           [MARKER_SIZE_METERS, 0, 0],
                           [MARKER_SIZE_METERS, MARKER_SIZE_METERS, 0],
                           [0, MARKER_SIZE_METERS, 0]], dtype=np.float32)
    image_points = np.array(marker_corners, dtype=np.float32)
    _, rvec, tvec = cv2.solvePnP(obj_points, image_points, cameraMatrix, dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE)
    
    return tvec.flatten(), rvec.flatten()

def calculate_reprojection_error(obj_points, image_points, rvec, tvec, cameraMatrix, dist_coeffs):
    reproj_points, _ = cv2.projectPoints(obj_points, rvec, tvec, cameraMatrix, dist_coeffs)
    error = np.mean(np.linalg.norm(image_points - reproj_points.squeeze(), axis=1))
    return error

def aruco_display(corners, ids, rejected, image):
    pose_world = None  # Pose in the world frame
    if len(corners) > 0:
        ids = ids.flatten()
        
        for (markerCorner, markerID) in zip(corners, ids):
            corners = markerCorner.reshape((4, 2))
            obj_points = np.array([[0, 0, 0],
                                   [MARKER_SIZE_METERS, 0, 0],
                                   [MARKER_SIZE_METERS, MARKER_SIZE_METERS, 0],
                                   [0, MARKER_SIZE_METERS, 0]], dtype=np.float32)
            image_points = np.array(corners, dtype=np.float32)

            # SolvePnP to find pose relative to the camera
            _, rvec, tvec = cv2.solvePnP(obj_points, image_points, cameraMatrix, dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE)

            # Convert to transformation matrix (camera frame)
            T_marker_to_camera = create_transformation_matrix(tvec, rvec)

            # Compute marker pose in the world frame
            T_marker_to_world = np.dot(T_CAMERA_TO_WORLD, T_marker_to_camera)

            # Extract translation and rotation from the world-frame transformation matrix
            t_world = T_marker_to_world[:3, 3]
            r_world = R.from_matrix(T_marker_to_world[:3, :3]).as_rotvec()

            pose_world = np.hstack((t_world, r_world))

            # Visualize marker and display pose in the image
            (topLeft, topRight, bottomRight, bottomLeft) = corners
            topLeft, topRight = tuple(map(int, topLeft)), tuple(map(int, topRight))
            bottomRight, bottomLeft = tuple(map(int, bottomRight)), tuple(map(int, bottomLeft))

            # Draw the marker outline
            cv2.line(image, topLeft, topRight, (0, 255, 0), 2)
            cv2.line(image, topRight, bottomRight, (0, 255, 0), 2)
            cv2.line(image, bottomRight, bottomLeft, (0, 255, 0), 2)
            cv2.line(image, bottomLeft, topLeft, (0, 255, 0), 2)

            # Draw center point
            cX = int((topLeft[0] + bottomRight[0]) / 2.0)
            cY = int((topLeft[1] + bottomRight[1]) / 2.0)
            cv2.circle(image, (cX, cY), 4, (0, 0, 255), -1)

            # Display the world frame pose on the image
            cv2.putText(image, f"World Pose: {t_world.round(3)}", (cX - 50, cY - 20), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

    return image, pose_world

# Initialize ArUco detector
arucoDict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_250)
arucoParams = cv2.aruco.DetectorParameters()

# Configure depth and color streams from RealSense camera
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)  # Color stream

# Start streaming from RealSense
pipeline.start(config)

# Get the color stream profile to access intrinsic parameters
profile = pipeline.get_active_profile()
color_stream = profile.get_stream(rs.stream.color)
intrinsics = color_stream.as_video_stream_profile().get_intrinsics()

# Create the camera matrix and fetch distortion coefficients
cameraMatrix = np.array([[intrinsics.fx, 0, intrinsics.ppx],
                         [0, intrinsics.fy, intrinsics.ppy],
                         [0, 0, 1]], dtype=np.float32)
dist_coeffs = np.array(intrinsics.coeffs, dtype=np.float32)

# RTDE Interface
#rtde_r = rtde_receive.RTDEReceiveInterface("192.168.1.100")

# Create directories for saving data
os.makedirs("pose_data", exist_ok=True)

try:
    while True:
        # Wait for frames from the RealSense camera
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()

        if not color_frame:
            continue

        # Convert RealSense frame to numpy array
        img = np.asanyarray(color_frame.get_data())
        detector = cv2.aruco.ArucoDetector(arucoDict, arucoParams)
        corners, ids, rejected = detector.detectMarkers(img)

        detected_markers, pose = aruco_display(corners, ids, rejected, img)

        cv2.imshow("RealSense Image", detected_markers)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break

        if key == ord("p"):
            print(pose)

        if key == ord("s"):
            robot_pose = rtde_r.getActualTCPPose()
            print("Saving data...")

            if pose is not None:
                robot_filename = os.path.join("pose_data", "robot_poses.txt")
                aruco_filename = os.path.join("pose_data", "aruco_poses.txt")

                # Write the robot pose to file
                with open(robot_filename, "a") as f_robot:
                    f_robot.write(f"{np.array(robot_pose)}\n")

                # Write the ArUco pose to file
                with open(aruco_filename, "a") as f_aruco:
                    f_aruco.write(f"{np.array(pose)}\n")

                print("Data saved successfully.")
            else:
                print("No pose detected.")
finally:
    pipeline.stop()

cv2.destroyAllWindows()
