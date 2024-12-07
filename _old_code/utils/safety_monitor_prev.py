import pyrealsense2 as rs
import cv2
import mediapipe as mp
import numpy as np
import math
from abfilter import ABFilter
from typing import Union, Tuple

from mediapipe.framework.formats import landmark_pb2


class RobotSafetyMonitor:
    def __init__(self, safety_distance=0.5, color_res=(1280, 720), depth_res=(1280, 720), fps=15):
        self.safety_distance = safety_distance
        self.sphere_center_fixtures = [-0.72302, -0.42781, 2.03305] # in camera frame
        self.sphere_center_home = [-0.48186, -0.11395, 1.00219]
        self.sphere_center_place = [-0.48186, -0.11395, 1.40219]


        self.robot_pose_state = 0 # 0 -> home, 1 -> fixtures, 2 -> place
        self.min_distance_array = []

        self.sphere_radius = 0.05
        self.pipeline = rs.pipeline()
        self.config = rs.config()

        # Configure the RealSense camera streams
        self.config.enable_stream(rs.stream.color, color_res[0], color_res[1], rs.format.bgr8, fps)
        self.config.enable_stream(rs.stream.depth, depth_res[0], depth_res[1], rs.format.z16, fps)

        self.align_to = rs.stream.color
        self.align = rs.align(self.align_to)

        # Initialize MediaPipe Pose
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose()
        self.mp_drawing = mp.solutions.drawing_utils

        # Start the camera stream
        self.pipeline.start(self.config)

        # Set up OpenCV window
        cv2.namedWindow('Pose Detection', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Pose Detection', 1280, 720)

        self.filter = ABFilter(alpha=0.1,beta=0.05,dt=1/30)


    def stop_monitoring(self):
        """Stop the pipeline."""
        self.pipeline.stop()


    @staticmethod
    def calculate_distance(point1, point2):
        """Calculates the Euclidean distance between two 3D points."""
        return math.sqrt(
            (point1[0] - point2[0]) ** 2 +
            (point1[1] - point2[1]) ** 2 +
            (point1[2] - point2[2]) ** 2
        )


    def calculate_distance_to_sphere(self, point):
        """Calculate distance from a point to the surface of the sphere."""
        distance_to_center = np.linalg.norm(np.array(point) - self.sphere_center)
        distance_to_surface = abs(distance_to_center - self.sphere_radius)
        return distance_to_surface

    def _normalized_to_pixel_coordinates(
        normalized_x: float, normalized_y: float, image_width: int,
        image_height: int) -> Union[None, Tuple[int, int]]:
        """Converts normalized value pair to pixel coordinates."""

        # Checks if the float value is between 0 and 1.
        def is_valid_normalized_value(value: float) -> bool:
            return (value > 0 or math.isclose(0, value)) and (value < 1 or
                                                            math.isclose(1, value))

        if not (is_valid_normalized_value(normalized_x) and
                is_valid_normalized_value(normalized_y)):
            # TODO: Draw coordinates even if it's outside of the image bounds.
            return None
        x_px = min(math.floor(normalized_x * image_width), image_width - 1)
        y_px = min(math.floor(normalized_y * image_height), image_height - 1)
        return x_px, y_px
    
    def draw_tcp_on_image(self, tcp_coords, depth_intrin, color_image):
        """Draws the TCP on the image at the correct pixel coordinates."""
        tcp_pixel_coords = rs.rs2_project_point_to_pixel(depth_intrin, tcp_coords)
        tcp_x, tcp_y = int(tcp_pixel_coords[0]), int(tcp_pixel_coords[1])
        height, width, _ = color_image.shape

        if 0 <= tcp_x < width and 0 <= tcp_y < height:
            cv2.circle(color_image, (tcp_x, tcp_y), 10, (0, 0, 255), -1)  # Red circle
            cv2.putText(color_image, "TCP", (tcp_x + 15, tcp_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    def rotation_matrix_from_euler_XYZ(roll, pitch, yaw, degrees=False):
        """
        Creates a rotation matrix from roll, pitch, and yaw (Euler angles).

        Parameters:
        roll (float): Rotation around the X-axis.
        pitch (float): Rotation around the Y-axis.
        yaw (float): Rotation around the Z-axis.
        degrees (bool): If True, the angles are in degrees. Otherwise, in radians.

        Returns:
        numpy.ndarray: A 3x3 rotation matrix.
        """
        if degrees:
            roll = np.radians(roll)
            pitch = np.radians(pitch)
            yaw = np.radians(yaw)
        
        # Rotation matrix around X-axis (roll)
        Rx = np.array([
            [1, 0, 0],
            [0, np.cos(roll), -np.sin(roll)],
            [0, np.sin(roll), np.cos(roll)]
        ])
        
        # Rotation matrix around Y-axis (pitch)
        Ry = np.array([
            [np.cos(pitch), 0, np.sin(pitch)],
            [0, 1, 0],
            [-np.sin(pitch), 0, np.cos(pitch)]
        ])
        
        # Rotation matrix around Z-axis (yaw)
        Rz = np.array([
            [np.cos(yaw), -np.sin(yaw), 0],
            [np.sin(yaw), np.cos(yaw), 0],
            [0, 0, 1]
        ])
        
        return Rz @ Ry @ Rx # Combined rotation matrix: R = Rz * Ry * Rx

    def transform_R(self, rotation, degrees=False):
        """
        Creates a 6x6 transformation matrix for rotational motion.

        Parameters:
        rotation (tuple): A tuple (roll, pitch, yaw) for the rotation in radians (or degrees if specified).
        degrees (bool): Set to True if the rotation angles are given in degrees.

        Returns:
        numpy.ndarray: A 6x6 transformation matrix.
        """
        # Convert Euler angles to a 3x3 rotation matrix
        R = self.rotation_matrix_from_euler_XYZ(*rotation, degrees=degrees)

        # Create the 6x6 transformation matrix
        R_mat = np.zeros((6, 6))  # Initialize a 6x6 matrix of zeros
        R_mat[:3, :3] = R         # Top-left 3x3 block is R
        R_mat[3:, 3:] = R         # Bottom-right 3x3 block is R

        return R_mat

    def set_robot_tcp(self, b_p_tcp):
        """Sets the TCP coordinates with respect to the camera frame"""
        w_t_b = np.array([-0.276, 0.024, -0.035, 0, 0, 0]) # Translation (x, y, z)
        w_R_b = transform_R([0, 180, 67.5], degrees=True)  # Rotation (roll, pitch, yaw) in degrees

        w_p_tcp = w_R_b @ b_p_tcp + w_t_b # Transforming tcp into world frame

        #Camera transform
        c_T_w = np.array([[ 0.51970216,  0.854174,    0.01645907, -0.53570101],
                        [-0.59055939,  0.34525865,  0.72936413,  0.40769184],
                        [ 0.61733134, -0.38878397,  0.68387034,  1.36497584],
                        [ 0,           0,           0,           1,        ]])
        c_R_w = np.zeros((6, 6))
        c_R_w[:3, :3] = c_T_w[:3,:3]
        c_R_w[3:, 3:] = c_T_w[:3,:3]
        c_t_w = np.zeros(6)
        c_t_w[:3] = c_T_w[:3, 3]

        c_p_tcp = c_R_w @ w_p_tcp + c_t_w # Transforming tcp into camera frame

        self.tcp_coords = c_p_tcp[:3]

    def calculate_human_robot_distance(
        self, poses, depth_frame, color_image
    ):
        """Calculate the minimum distance between the human and the robot"""
        min_distance = float("inf")
        if poses.pose_landmarks:
            height, width, _ = color_image.shape

            depth_intrin = depth_frame.profile.as_video_stream_profile().intrinsics


            # Check distance for each human landmark
            for id, landmark in enumerate(poses.pose_landmarks.landmark):
                if id >= 24:  # Ignore leg landmarks
                    break

                cx, cy = self.filter.filter((landmark.x, landmark.y))
                cx = int(cx * width)
                cy = int(cy * height)

                # Ensure the coordinates are within the bounds of the image
                if 0 <= cx < width and 0 <= cy < height:
                    depth_value = depth_frame.get_distance(cx, cy)
                    human_coords = rs.rs2_deproject_pixel_to_point(
                        depth_intrin, [cx, cy], depth_value
                    )

                    self.set_robot_tcp(self.robot_controller.get_tcp_pose())
                    distance = math.dist(human_coords, self.tcp_coords)
                    min_distance = min(
                        min_distance, distance
                    )  # Track the minimum distance

        print(f"Distance: {min_distance}")

        return min_distance

    def monitor_safety(self, patch_coords_list):
        """Runs the main loop for safety monitoring and returns the minimum distance to the sphere."""
        if self.robot_pose_state == 1:
            self.sphere_center = self.sphere_center_fixtures
        elif self.robot_pose_state == 2:
            self.sphere_center = self.sphere_center_place
        else:
            self.sphere_center = self.sphere_center_home

        # Get frames from the RealSense camera
        frames = self.pipeline.wait_for_frames()
        aligned_frames = self.align.process(frames)

        depth_frame = aligned_frames.get_depth_frame()
        color_frame = aligned_frames.get_color_frame()

        if not depth_frame or not color_frame:
            return float('inf')  # No frames available, return a large distance

        # Convert RealSense frames to numpy arrays
        color_image = np.asanyarray(color_frame.get_data())
        depth_image = np.asanyarray(depth_frame.get_data())

        # Convert color image to RGB for MediaPipe processing
        rgb_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb_image)

        min_distance = float('inf')  # Initialize min_distance with a high value
        too_close = False
        height, width, _ = color_image.shape


        hcx = int(abs(self.sphere_center_home[0] * width))
        hcy = int(abs(self.sphere_center_home[1] * height))

        print((hcx,hcy))

        cv2.circle(color_image, (100,100), 10, (0,0,255), 1)

        if results.pose_landmarks:
            # Draw the landmarks on the image
            self.mp_drawing.draw_landmarks(
                color_image,
                results.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS,
                self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=3),
                self.mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2, circle_radius=3),
            )

            # Get robot TCP coordinates
            depth_intrin = depth_frame.profile.as_video_stream_profile().intrinsics


            # Check distance for each human landmark
            for id, landmark in enumerate(results.pose_landmarks.landmark):
                if id >= 24:  # Ignore leg landmarks
                    break

                #cx, cy = self.filter.filter((landmark.x, landmark.y))

                cx = min(math.floor(landmark.x* width), width - 1)
                cy = min(math.floor(landmark.y* height), height - 1)

                #cx = int(cx * width)
                #cy = int(cy * height)
                

                # Ensure the coordinates are within the bounds of the image
                if 0 <= cx < width and 0 <= cy < height:
                    depth_value = depth_frame.get_distance(cx, cy)
                    human_coords = rs.rs2_deproject_pixel_to_point(depth_intrin, [cx, cy], depth_value)

                    self.draw_tcp_on_image(self.sphere_center, depth_intrin, color_image)

                    distance = self.calculate_human_robot_distance(landmark.poses, depth_frame, )
                    min_distance = min(min_distance, distance)  # Track the minimum distance

                    # Display the distance for each landmark
                    cv2.putText(color_image, f"D:{distance:0.2f}m", (cx, cy),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 1, cv2.LINE_AA)

                    #print(distance)
                    # Check if robot is too close to human
                    if distance < self.safety_distance:
                        too_close = True

            if too_close:
                print("Robot too close to human! Slowing down...")

        # Colors for each patch (you can customize the colors for each rectangle)
        colors = [(0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 255, 0), (0, 255, 255), (255, 0, 255)]  # Green, Blue, Red, Yellow

        # Draw rectangles for each patch
        for i, patch_coords in enumerate(patch_coords_list):
            x, y, w, h = patch_coords
            cv2.rectangle(color_image, (x, y), (x + w, y + h), colors[i], 2)

        # Draw the vertical line in the middle of the image, showing only the bottom 20 pixels
        center_x = width // 2
        line_start_y = height - 50  # Start 20 pixels from the bottom
        line_end_y = height          # End at the bottom of the image
        cv2.line(color_image, (center_x, line_start_y), (center_x, line_end_y), (245, 66, 209), 4)    # Blue line

        # Display the image
        cv2.imshow('Pose Detection', color_image)

        # Exit if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            terminate = True
        else:
            terminate = False

        self.min_distance_array.append(min_distance)

        return too_close, min_distance, cv2.cvtColor(color_image, cv2.COLOR_RGB2GRAY), depth_image, terminate



if __name__ == "__main__":
    s = RobotSafetyMonitor()

    patch_coords_list = [
        (335, 365, 20, 15), 
        (295, 390, 20, 15), 
        (260, 415, 20, 15), 
        (225, 445, 20, 15),
        (195, 500, 20, 15),
        (160, 525, 20, 15),
    ]

    while True:
        s.monitor_safety(patch_coords_list)
