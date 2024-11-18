import pyrealsense2 as rs
import cv2
import mediapipe as mp
from scipy.spatial.transform import Rotation as R
import numpy as np
import math
import os
import time  # Import time for delay
from abfilter import ABFilter

class RobotSafetyMonitor:
    def __init__(self, safety_distance=0.5, sphere_center=(0, 0, 0), sphere_radius=1.0, color_res=(640, 480), depth_res=(640, 480), fps=30):
        self.safety_distance = safety_distance
        self.sphere_center = np.array(sphere_center)
        self.sphere_radius = sphere_radius

        # Initialize RealSense and MediaPipe
        self.pipeline = rs.pipeline()
        self.config = rs.config()
        self.config.enable_stream(rs.stream.color, color_res[0], color_res[1], rs.format.bgr8, fps)
        self.config.enable_stream(rs.stream.depth, depth_res[0], depth_res[1], rs.format.z16, fps)
        self.align_to = rs.stream.color
        self.align = rs.align(self.align_to)
        self.pipeline.start(self.config)

        # Initialize pose detection
        self.pose = mp.solutions.pose.Pose()
        self.mp_drawing = mp.solutions.drawing_utils

        # Load transformation matrix (robot base to camera frame)
        self.T_robot2cam = self.load_transformation()

        # Initialize filter
        self.filter = ABFilter(alpha=0.1, beta=0.05, dt=1/30)

    def load_transformation(self):
        # Load or calculate T_robot2cam here
        # Placeholder identity matrix for this example
        return np.eye(4)

    def set_robot_tcp(self, tcp_pose):
        """Convert TCP pose from robot to camera coordinates."""
        tcp_pose_camera_frame = np.dot(self.T_robot2cam, np.append(tcp_pose[:3], 1))
        self.tcp_coords = tcp_pose_camera_frame[:3]

    def stop_monitoring(self):
        """Stop RealSense pipeline."""
        self.pipeline.stop()

    def calculate_distance_to_sphere(self, point):
        """Calculate distance from a point to the surface of the sphere."""
        distance_to_center = np.linalg.norm(point - self.sphere_center)
        distance_to_surface = abs(distance_to_center - self.sphere_radius)
        return distance_to_surface

    @staticmethod
    def draw_tcp_on_image(tcp_coords, depth_intrin, color_image):
        """Draw TCP on the image at the correct pixel coordinates."""
        tcp_pixel_coords = rs.rs2_project_point_to_pixel(depth_intrin, tcp_coords)
        tcp_x, tcp_y = int(tcp_pixel_coords[0]), int(tcp_pixel_coords[1])
        height, width, _ = color_image.shape

        if 0 <= tcp_x < width and 0 <= tcp_y < height:
            cv2.circle(color_image, (tcp_x, tcp_y), 10, (0, 0, 255), -1)
            cv2.putText(color_image, "TCP", (tcp_x + 15, tcp_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    def monitor_safety(self, patch_coords_list):
        """Main loop for monitoring safety with respect to the sphere surface."""
        frames = self.pipeline.wait_for_frames()
        aligned_frames = self.align.process(frames)
        depth_frame = aligned_frames.get_depth_frame()
        color_frame = aligned_frames.get_color_frame()

        if not depth_frame or not color_frame:
            return 0, None, None, None, False

        # Convert RealSense frames to numpy arrays
        color_image = np.asanyarray(color_frame.get_data())
        depth_image = np.asanyarray(depth_frame.get_data())

        # Convert color image to RGB for MediaPipe processing
        rgb_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb_image)

        # Project TCP onto the color image
        depth_intrin = depth_frame.profile.as_video_stream_profile().intrinsics
        self.draw_tcp_on_image(self.tcp_coords, depth_intrin, color_image)

        # Calculate the distance from TCP to the sphere surface
        distance_to_sphere = self.calculate_distance_to_sphere(self.tcp_coords)
        too_close = distance_to_sphere < self.safety_distance

        if too_close:
            print("Warning: Robot TCP too close to sphere surface!")

        # Draw rectangles for patches (for fixture checks)
        for x, y, w, h in patch_coords_list:
            cv2.rectangle(color_image, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Update drawing every 500 ms
        time.sleep(0.5)
        if results.pose_landmarks:
            # Draw the landmarks on the image
            self.mp_drawing.draw_landmarks(
                color_image,
                results.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS,
                self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=4, circle_radius=5),
                self.mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=4, circle_radius=5),
            )

        # Display distance on the image
        cv2.putText(color_image, f"Distance to Sphere: {distance_to_sphere:.2f}m",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

        # Display and exit handling
        if cv2.waitKey(1) & 0xFF == ord('q'):
            terminate = True
        else:
            terminate = False

        return too_close, distance_to_sphere, color_image, depth_image, terminate

if __name__ == "__main__":
    monitor = RobotSafetyMonitor(safety_distance=0.5, sphere_center=(0, 0, 0), sphere_radius=1.0)

    patch_coords_list = [
        (166, 203, 18, 12),  # Component 1
        (152, 223, 18, 12), 
        (133, 243, 18, 12), 
        (113, 265, 18, 12)   # Component 4
    ]

    # Set initial robot TCP
    monitor.set_robot_tcp([-0.45057, -0.34136, 0.66577, -0.46792, 1.23244, 2.73046])

    # Monitoring loop
    while True:
        too_close, distance, color_image, depth_image, terminate = monitor.monitor_safety(patch_coords_list)
        if terminate:
            break

    monitor.stop_monitoring()
