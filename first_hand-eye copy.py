import pyrealsense2 as rs
import cv2
import numpy as np
from scipy.spatial.transform import Rotation as R

# Set global print options
np.set_printoptions(precision=5, suppress=True)

def Rodrigues(rvec, R):
    r = R.from_rotvec(rvec)
    R[:] = r.as_matrix()

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
    _, rvec, tvec = cv2.solvePnP(obj_points, image_points, np.eye(3), None)
    
    return tvec.flatten()

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
            
            marker_size_meters = 0.06  # Marker size
            distance, rvec, tvec = calculate_distance_and_pose(marker_size_meters, img_width, img_height, corners)

            size_in_image = np.linalg.norm(np.array(topLeft) - np.array(topRight))
            print(f"Marker ID: {markerID}, Size in image: {size_in_image:.2f} pixels, Distance: {distance:.2f} meters")
            print(f"Center: ({cX}, {cY}), rvec: {rvec.flatten()}, tvec: {tvec.flatten()}")

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
    _, rvec, tvec = cv2.solvePnP(obj_points, image_points, np.eye(3), None)

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

        print("Pose: ", pose)
        cv2.imshow("RealSense Image", detected_markers)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break

finally:
    pipeline.stop()

cv2.destroyAllWindows()
