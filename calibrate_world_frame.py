import cv2
import numpy as np
import pyrealsense2 as rs

# Function to get camera intrinsics from RealSense
def get_intrinsics_from_realsense():
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)
    
    # Start streaming
    profile = pipeline.start(config)
    intrinsics = profile.get_stream(rs.stream.color).as_video_stream_profile().get_intrinsics()
    pipeline.stop()
    
    # Extract intrinsics
    camera_matrix = np.array([
        [intrinsics.fx, 0, intrinsics.ppx],
        [0, intrinsics.fy, intrinsics.ppy],
        [0, 0, 1]
    ])
    dist_coeffs = np.zeros(5)  # RealSense intrinsics often don't include distortion coefficients
    return camera_matrix, dist_coeffs

# Retrieve intrinsics
camera_matrix, dist_coeffs = get_intrinsics_from_realsense()

# Chessboard parameters
chessboard_size = (6, 9)  # Replace with your chessboard's inner corner dimensions (columns, rows)
square_size = 0.022  # Replace with your square size in meters
avg_frame_size = 100

# Generate the 3D points of the chessboard corners in the world frame
objp = np.zeros((chessboard_size[0] * chessboard_size[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:chessboard_size[0], 0:chessboard_size[1]].T.reshape(-1, 2)
objp *= square_size  # Scale by the square size

# Initialize RealSense pipeline to capture images
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)
pipeline.start(config)

# List to store last 5 transformation matrices
transformation_matrices = []
corners_list = []

try:
    print("Press 'q' to quit.")
    
    while True:
        # Wait for a frame and capture it
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        if not color_frame:
            print("Failed to capture color frame from RealSense camera.")
            continue
        
        # Convert RealSense frame to OpenCV format
        color_image = np.asanyarray(color_frame.get_data())
        gray = cv2.cvtColor(color_image, cv2.COLOR_BGR2GRAY)
        
        # Find the chessboard corners
        ret, corners = cv2.findChessboardCorners(gray, chessboard_size, cv2.CALIB_CB_FAST_CHECK)
        
        if ret:
            # Refine corner positions
            corners_refined = cv2.cornerSubPix(
                gray, corners, (11, 11), (-1, -1),
                criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
            )

            corners_list.append(corners_refined)
            
            # Solve for the camera pose
            retval, rvec, tvec = cv2.solvePnP(objp, corners_refined, camera_matrix, dist_coeffs)
            
            # Convert rotation vector to rotation matrix
            rotation_matrix, _ = cv2.Rodrigues(rvec)
            
            # Construct the transformation matrix
            transformation_matrix = np.eye(4)
            transformation_matrix[:3, :3] = rotation_matrix
            transformation_matrix[:3, 3] = tvec.T

            # Store the transformation matrix for averaging
            transformation_matrices.append(transformation_matrix)
            
            # Keep only the last 5 matrices
            if len(transformation_matrices) > avg_frame_size:
                transformation_matrices.pop(0)
            
            # Compute the average transformation matrix if we have 5 matrices
            if len(transformation_matrices) == avg_frame_size:
                avg_transformation_matrix = np.mean(transformation_matrices, axis=0)
                print("\nAverage Camera-to-World Transformation Matrix:")
                print(avg_transformation_matrix)
            
            # Visualize the corners as the average of the last 5 frames (if enough frames are available)
            if len(corners_list) > avg_frame_size:
                corners_list.pop(0)

            if len(corners_list) == avg_frame_size:
                cv2.drawChessboardCorners(color_image, chessboard_size, np.mean(corners_list, axis=0), ret)
            
            # Project the world origin (0,0,0) into the image
            world_origin_3d = np.array([[0, 0, 0]], dtype=np.float32)
            img_points, _ = cv2.projectPoints(world_origin_3d, rvec, tvec, camera_matrix, dist_coeffs)
            img_points = img_points.astype(int)

            # Draw the origin on the image (as a red point)
            cv2.circle(color_image, tuple(img_points[0][0]), 5, (0, 0, 255), -1)

        # Show the live camera feed with corners and origin visualized
        cv2.imshow("RealSense Camera", color_image)
        
        # Wait for a key press
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):  # 'q' key to quit
            print("Exiting...")
            break

finally:
    # Stop the RealSense pipeline and close OpenCV windows
    pipeline.stop()
    cv2.destroyAllWindows()


[[ 0.51970216  0.854174    0.01645907 -0.53570101]
 [-0.59055939  0.34525865  0.72936413  0.40769184]
 [ 0.61733134 -0.38878397  0.68387034  1.36497584]
 [ 0.          0.          0.          1.        ]]