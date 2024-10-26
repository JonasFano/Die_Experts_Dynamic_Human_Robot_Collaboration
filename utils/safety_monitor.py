import pyrealsense2 as rs
import cv2
import mediapipe as mp
from scipy.spatial.transform import Rotation as R
import numpy as np
import math
import os
from abfilter import ABFilter

class RobotSafetyMonitor:
    def __init__(self, safety_distance=0.5, color_res=(640, 480), depth_res=(640, 480), fps=30):
        self.safety_distance = safety_distance
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

        self.filter = ABFilter(alpha=0.1, beta=0.05, dt=1/30)

        # Load ArUco and robot poses (adjust paths as needed)
        aruco_poses = self.load_poses('pose_data/aruco_poses.txt')
        robot_poses = self.load_poses('pose_data/robot_poses.txt')

        # Extract translation and rotation vectors
        aruco_translations = aruco_poses[:, :3]  # ArUco translation in camera frame
        aruco_rotations = aruco_poses[:, 3:]     # ArUco rotations (Euler angles) in camera frame
        robot_translations = robot_poses[:, :3]  # TCP translation in robot base frame
        robot_rotations = robot_poses[:, 3:]     # TCP rotations (Euler angles) in robot base frame

        # Convert Euler angles to rotation matrices
        aruco_rot_matrices = np.array([R.from_euler('xyz', rot).as_matrix() for rot in aruco_rotations])
        robot_rot_matrices = np.array([R.from_euler('xyz', rot).as_matrix() for rot in robot_rotations])


        # Perform hand-eye calibration the other way around to find transformation from robot base to camera
        R_robot2cam, t_robot2cam = cv2.calibrateHandEye(
            R_gripper2base=aruco_rot_matrices, t_gripper2base=aruco_translations,
            R_target2cam=robot_rot_matrices, t_target2cam=robot_translations
        )

        # Transformation matrix setup
        self.T_robot2cam = np.eye(4)
        self.T_robot2cam[:3, :3] = R_robot2cam
        self.T_robot2cam[:3, 3] = t_robot2cam.flatten()

    @staticmethod
    def load_poses(relative_path):
        file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), relative_path)
        poses = []
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip().strip('[]')
                if line:
                    pose = list(map(float, line.split()))
                    poses.append(pose)
        return np.array(poses)

    def set_robot_tcp(self, tcp_pose):
        tcp_pose_camera_frame = np.dot(self.T_robot2cam, np.append(tcp_pose[:3], 1))
        self.tcp_coords = tcp_pose_camera_frame[:3]

    def stop_monitoring(self):
        """Stop the pipeline."""
        self.pipeline.stop()

    @staticmethod
    def draw_tcp_on_image(tcp_coords, depth_intrin, color_image):
        tcp_pixel_coords = rs.rs2_project_point_to_pixel(depth_intrin, tcp_coords)
        tcp_x, tcp_y = int(tcp_pixel_coords[0]), int(tcp_pixel_coords[1])
        height, width, _ = color_image.shape

        if 0 <= tcp_x < width and 0 <= tcp_y < height:
            cv2.circle(color_image, (tcp_x, tcp_y), 10, (0, 0, 255), -1)
            cv2.putText(color_image, "TCP", (tcp_x + 15, tcp_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    @staticmethod
    def calculate_distance(point1, point2):
        return math.sqrt(
            (point1[0] - point2[0]) ** 2 +
            (point1[1] - point2[1]) ** 2 +
            (point1[2] - point2[2]) ** 2
        )

    def monitor_safety(self, patch_coords_list):
        frames = self.pipeline.wait_for_frames()
        aligned_frames = self.align.process(frames)

        depth_frame = aligned_frames.get_depth_frame()
        color_frame = aligned_frames.get_color_frame()

        if not depth_frame or not color_frame:
            return 0

        color_image = np.asanyarray(color_frame.get_data())
        depth_image = np.asanyarray(depth_frame.get_data())

        rgb_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb_image)

        too_close = False
        distance = 0

        if results.pose_landmarks:
            self.mp_drawing.draw_landmarks(
                color_image,
                results.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS,
                self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=4, circle_radius=5),
                self.mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=4, circle_radius=5),
            )

            depth_intrin = depth_frame.profile.as_video_stream_profile().intrinsics
            self.draw_tcp_on_image(self.tcp_coords, depth_intrin, color_image)

            height, width, _ = color_image.shape

            for id, landmark in enumerate(results.pose_landmarks.landmark):
                if id >= 24:
                    break

                cx, cy = self.filter.filter((landmark.x, landmark.y))
                cx = int(cx * width)
                cy = int(cy * height)

                if 0 <= cx < width and 0 <= cy < height:
                    depth_value = depth_frame.get_distance(cx, cy)
                    human_coords = rs.rs2_deproject_pixel_to_point(depth_intrin, [cx, cy], depth_value)
                    distance = self.calculate_distance(self.tcp_coords, human_coords)

                    if distance < self.safety_distance:
                        too_close = True

            if too_close:
                print("Robot too close to human! Slowing down...")

        return too_close, distance, color_image, depth_image, False

if __name__ == "__main__":
    monitor = RobotSafetyMonitor(safety_distance=0.5)
    patch_coords_list = [(166, 203, 18, 12), (152, 223, 18, 12), (133, 243, 18, 12), (113, 265, 18, 12)]
    monitor.set_robot_tcp([-0.45057, -0.34136, 0.66577, -0.46792, 1.23244, 2.73046])

    # Main monitoring loop with OpenCV display removed.
    while True:
        monitor.monitor_safety(patch_coords_list)
