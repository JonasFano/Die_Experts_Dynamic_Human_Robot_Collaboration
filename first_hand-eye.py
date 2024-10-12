import pyrealsense2 as rs
import rtde_receive
import cv2
import numpy as np
from scipy.spatial.transform import Rotation as R
import os

# Set global print options
np.set_printoptions(precision=5, suppress=True)

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

def calculate_marker_position(marker_id, corners, ids, marker_size_meters, img_width, img_height):
    marker_indices = np.where(ids == marker_id)[0]
    if len(marker_indices) == 0:
        return None
    
    marker_corners = corners[marker_indices[0]]
    marker_corners = marker_corners.reshape((4, 2))
    obj_points = np.array([[0, 0, 0],
                            [marker_size_meters, 0, 0],
                            [marker_size_meters, marker_size_meters, 0],
                            [0, marker_size_meters, 0]], dtype=np.float32)
    image_points = np.array(marker_corners, dtype=np.float32)
    _, rvec, tvec = cv2.solvePnP(obj_points, image_points, cameraMatrix, None)
    
    return tvec.flatten(), rvec.flatten()

def aruco_display(corners, ids, rejected, image, img_width, img_height):
    pose = None 
    if len(corners) > 0:
        ids = ids.flatten()
        
        for (markerCorner, markerID) in zip(corners, ids):
            corners = markerCorner.reshape((4, 2))
            (topLeft, topRight, bottomRight, bottomLeft) = corners

            topRight = (int(topRight[0]), int(topRight[1]))
            bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
            bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
            topLeft = (int(topLeft[0]), int(topLeft[1]))

            cv2.line(image, topLeft, topRight, (0, 255, 0), 2)
            cv2.line(image, topRight, bottomRight, (0, 255, 0), 2)
            cv2.line(image, bottomRight, bottomLeft, (0, 255, 0), 2)
            cv2.line(image, bottomLeft, topLeft, (0, 255, 0), 2)

            cX = int((topLeft[0] + bottomRight[0]) / 2.0)
            cY = int((topLeft[1] + bottomRight[1]) / 2.0)

            cv2.circle(image, (cX, cY), 4, (0, 0, 255), -1)
            
            marker_size_meters = 0.02  # Marker size
            distance, rvec, tvec = calculate_distance_and_pose(marker_size_meters, img_width, img_height, corners)

            tvec = tvec.flatten()
            rvec = rvec.flatten()
            pose = np.hstack((tvec, rvec))

            cv2.putText(image, f"Distance: {distance:.2f}m", (cX - 50, cY - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

    return image, pose

def calculate_distance_and_pose(marker_size_meters, img_width, img_height, marker_corners):
    focal_length_px = max(img_width, img_height)
    size_in_image = np.linalg.norm(marker_corners[0] - marker_corners[2])
    distance = (marker_size_meters * focal_length_px) / size_in_image

    obj_points = np.array([[0, 0, 0],
                            [marker_size_meters, 0, 0],
                            [marker_size_meters, marker_size_meters, 0],
                            [0, marker_size_meters, 0]], dtype=np.float32)
    image_points = np.array(marker_corners, dtype=np.float32)
    _, rvec, tvec = cv2.solvePnP(obj_points, image_points, cameraMatrix, None)

    return distance, rvec, tvec

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

# Create the camera matrix from intrinsic parameters
cameraMatrix = np.array([[intrinsics.fx, 0, intrinsics.ppx],
                         [0, intrinsics.fy, intrinsics.ppy],
                         [0, 0, 1]], dtype=np.float32)

# RTDE Interface
rtde_r = rtde_receive.RTDEReceiveInterface("192.168.1.100")

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
        h, w, _ = img.shape

        width = 1000
        height = int(width * (h / w))
        img_resized = cv2.resize(img, (width, height), interpolation=cv2.INTER_CUBIC)

        detector = cv2.aruco.ArucoDetector(arucoDict, arucoParams)
        corners, ids, rejected = detector.detectMarkers(img_resized)

        detected_markers, pose = aruco_display(corners, ids, rejected, img_resized, w, h)

        cv2.imshow("RealSense Image", detected_markers)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break

        if key == ord("s"):
            robot_pose = rtde_r.getActualTCPPose()
            print("Saving data...")

            if pose is not None:
                # Prepare file paths
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
