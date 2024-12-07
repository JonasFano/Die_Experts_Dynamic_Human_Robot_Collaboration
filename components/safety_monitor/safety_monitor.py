import pyrealsense2 as rs
import cv2
import mediapipe as mp
import numpy as np
import math
from dataclasses import dataclass
from typing import NamedTuple, List
import time
from .utils.tcp_calculations import calculate_camera_tcp_coords
from socket_robot_controller.client import RobotSocketClient
from shared.abfilter import ABFilter

PATCH_COORDS_LIST = [
    (166, 203, 18, 12),  # Component 1
    (152, 223, 18, 12),
    (133, 243, 18, 12),
    (113, 265, 18, 12),  # Component 4
]


@dataclass
class SafetyFrameResults:
    # frame: rs.composite_frame
    color_frame: rs.video_frame
    color_image: np.ndarray
    depth_frame: rs.depth_frame
    depth_image: np.ndarray


class SafetyMonitor:
    def __init__(
        self, safety_distance=0.5, color_res=(1280, 720), depth_res=(1280, 720), fps=15, socket_url="http://localhost:5000"
    ):
        print("Starting the monitor")
        self.safety_distance = safety_distance
        self.sphere_center_fixtures = [-0.65887, -0.32279, 1.93131]  # in camera frame
        self.sphere_center_home = [-0.53615, -0.11935, 1.23248]
        self.sphere_center_place = [-0.15476, 0.1909, 0.91111]
        self.robot_pose_state = 0  # 0 -> home, 1 -> fixtures, 2 -> place
        self.min_distance_array = []
        print(socket_url)
        self.robot_controller = RobotSocketClient(socket_url)
        self.sphere_radius = 0.2
        self.pipeline = rs.pipeline()
        self.config = rs.config()


        # Configure the RealSense camera streams
        self.config.enable_stream(
            rs.stream.color, color_res[0], color_res[1], rs.format.bgr8, fps
        )
        self.config.enable_stream(
            rs.stream.depth, depth_res[0], depth_res[1], rs.format.z16, fps
        )

        self.align_to = rs.stream.color
        self.align = rs.align(self.align_to)

        # Initialize MediaPipe Pose
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose()
        self.mp_drawing = mp.solutions.drawing_utils

        """
        # Unsure if needed
        # Set up OpenCV window
        cv2.namedWindow("Pose Detection", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Pose Detection", 1920, 1080)
        """

        self.filter = ABFilter(alpha=0.1, beta=0.05, dt=1 / 30)
        print("Done starting the monitor")

    def start(self):
        # Start the camera stream
        while True:
            try:
                print("Starting safety monitor...")
                self.pipeline.start(self.config)
                break
            except KeyboardInterrupt:
                print("Stopped by user.")
                break
            except Exception as e:
                print(f"Failed to start realsense with error {e}")

    def stop_monitoring(self):
        """Stop the pipeline."""
        self.pipeline.stop()

    @staticmethod
    def calculate_distance(point1, point2):
        """Calculates the Euclidean distance between two 3D points."""
        return math.sqrt(
            (point1[0] - point2[0]) ** 2
            + (point1[1] - point2[1]) ** 2
            + (point1[2] - point2[2]) ** 2
        )

    def calculate_distance_to_sphere(self, point):
        """Calculate distance from a point to the surface of the sphere."""
        distance_to_center = np.linalg.norm(np.array(point) - self.sphere_center)
        distance_to_surface = abs(distance_to_center - self.sphere_radius)
        return distance_to_surface

    def apply_landmark_overlay(
        self, color_image: np.ndarray, results: NamedTuple
    ) -> None:
        """If landmarks present, draw landmark pose markers onto an image"""
        if results.pose_landmarks:
            # Draw the landmarks on the image
            self.mp_drawing.draw_landmarks(
                color_image,
                results.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS,
                self.mp_drawing.DrawingSpec(
                    color=(0, 255, 0), thickness=4, circle_radius=5
                ),
                self.mp_drawing.DrawingSpec(
                    color=(255, 0, 0), thickness=4, circle_radius=5
                ),
            )
        return color_image


    def rotation_matrix_from_euler_XYZ(self, roll, pitch, yaw, degrees=False):
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
        Rx = np.array(
            [[1, 0, 0], [0, np.cos(roll), -np.sin(roll)], [0, np.sin(roll), np.cos(roll)]]
        )

        # Rotation matrix around Y-axis (pitch)
        Ry = np.array(
            [
                [np.cos(pitch), 0, np.sin(pitch)],
                [0, 1, 0],
                [-np.sin(pitch), 0, np.cos(pitch)],
            ]
        )

        # Rotation matrix around Z-axis (yaw)
        Rz = np.array(
            [[np.cos(yaw), -np.sin(yaw), 0], [np.sin(yaw), np.cos(yaw), 0], [0, 0, 1]]
        )

        return Rz @ Ry @ Rx  # Combined rotation matrix: R = Rz * Ry * Rx

    def get_tcp_coords(self):
        while True:
            tcp_coords = self.robot_controller.get_tcp_pose()
            if tcp_coords is None:
                print("Tcp coords is none")
                continue
            break
        return tcp_coords

    def calculate_human_robot_distance(
        self, poses: NamedTuple, depth_frame: rs.depth_frame, color_image: np.ndarray
    ) -> float:
        """Calculate the minimum distance between the human and the robot"""
        min_distance = float("inf")

        saved_landmark = None
        actual_tcp_coords = self.get_tcp_coords()
        tcp_coords = calculate_camera_tcp_coords(actual_tcp_coords)

        if poses.pose_landmarks:
            height, width, _ = color_image.shape

            depth_intrin = depth_frame.profile.as_video_stream_profile().intrinsics
            
            # Check distance for each human landmark
            for id, landmark in enumerate(poses.pose_landmarks.landmark):
                if id >= 24:  # Ignore leg landmarks
                    break

                cx = int(landmark.x * width)
                cy = int(landmark.y * height)

                # Ensure the coordinates are within the bounds of the image
                if 0 <= cx < width and 0 <= cy < height:
                    depth_value = depth_frame.get_distance(cx, cy)
                    human_coords = rs.rs2_deproject_pixel_to_point(
                        depth_intrin, [cx, cy], depth_value
                    )

                    
                    distance = math.dist(human_coords, tcp_coords[:3])

                    cv2.putText(color_image, f"{id}: {distance:0.02f}", (cx, cy),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,0), 2, cv2.LINE_AA)
                    if (min_distance > distance):
                        saved_landmark = (cx,cy)
                    min_distance = min(
                        min_distance, distance
                    )  # Track the minimum distance

        print(f"Distance: {min_distance}")
        if saved_landmark is not None:
            tcp_pixel_coords = rs.rs2_project_point_to_pixel(depth_intrin, tcp_coords[:3])
            tcp_x, tcp_y = int(tcp_pixel_coords[0]), int(tcp_pixel_coords[1])
            cv2.line(color_image, saved_landmark, (tcp_x, tcp_y), (100,0,0), 2)

        return min_distance

    @staticmethod
    def draw_tcp_on_image(tcp_coords, depth_intrin, color_image):
        """Draws the TCP on the image at the correct pixel coordinates."""
        tcp_pixel_coords = rs.rs2_project_point_to_pixel(depth_intrin, tcp_coords)
        tcp_x, tcp_y = int(tcp_pixel_coords[0]), int(tcp_pixel_coords[1])
        height, width, _ = color_image.shape

        if 0 <= tcp_x < width and 0 <= tcp_y < height:
            cv2.circle(color_image, (tcp_x, tcp_y), 10, (0, 0, 255), -1)  # Red circle
            cv2.putText(color_image, "TCP", (tcp_x + 15, tcp_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)



    def calculate_poses(self, color_image: np.ndarray) -> NamedTuple:
        rgb_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)
        return self.pose.process(
            rgb_image
        )  # Used for creating pose overlay, calculating distance between human and robot

    # TODO: What is this used for?
    def apply_some_graphic(
        self, color_image: np.ndarray, patch_coords_list: List[List[float]]
    ) -> None:
        height, width, _ = color_image.shape

        # Colors for each patch (you can customize the colors for each rectangle)
        colors = [
            (0, 255, 0),
            (255, 0, 0),
            (0, 0, 255),
            (255, 255, 0),
        ]  # Green, Blue, Red, Yellow

        # Draw rectangles for each patch
        for i, patch_coords in enumerate(patch_coords_list):
            x, y, w, h = patch_coords
            cv2.rectangle(color_image, (x, y), (x + w, y + h), colors[i], 2)

        # Draw the vertical line in the middle of the image, showing only the bottom 20 pixels
        center_x = width // 2
        line_start_y = height - 50  # Start 20 pixels from the bottom
        line_end_y = height  # End at the bottom of the image
        return cv2.line(
            color_image,
            (center_x, line_start_y),
            (center_x, line_end_y),
            (255, 0, 0),
            2,
        )  # Blue line

    def get_frames(self) -> SafetyFrameResults:
        """Get the latest frames from the safety monitor"""
        if self.robot_pose_state == 1:
            self.sphere_center = self.sphere_center_fixtures
        elif self.robot_pose_state == 2:
            self.sphere_center = self.sphere_center_place
        else:
            self.sphere_center = self.sphere_center_home

        # Get frames from the RealSense camera

        frames = None

        while frames is None:
            try:
                frames = self.pipeline.wait_for_frames()
            except Exception:
                time.sleep(0.05)
        aligned_frames = self.align.process(frames)

        depth_frame = aligned_frames.get_depth_frame()
        color_frame = aligned_frames.get_color_frame()


        color_image = np.asanyarray(color_frame.get_data())
        depth_image = np.asanyarray(depth_frame.get_data())
        
        human_poses = self.calculate_poses(color_image)
        
        distance = self.calculate_human_robot_distance(human_poses, depth_frame, color_image)
        color_image = self.apply_landmark_overlay(color_image, human_poses)



        cv2.putText(color_image, f"Distance: {distance:0.02f}", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,0), 2, cv2.LINE_AA)

        tcp_coords = self.get_tcp_coords()
        tcp_coords = calculate_camera_tcp_coords(tcp_coords)
        depth_intrin = depth_frame.profile.as_video_stream_profile().intrinsics
        self.draw_tcp_on_image(tcp_coords[:3], depth_intrin, color_image)


        return SafetyFrameResults(color_frame, color_image, depth_frame, depth_image)


def main():
    s = SafetyMonitor(socket_url="http://localhost:5000")
    s.start()

    try:
        while True:
            frames = s.get_frames()
            rgb_color = frames.color_image
            cv2.imshow("Pose Detection", np.asanyarray(rgb_color))
            cv2.waitKey(1)
            time.sleep(1/60)

    except KeyboardInterrupt:
        s.robot_controller.rtde_c.disconnect()
        s.robot_controller.rtde_r.disconnect()
        s.robot_controller.rtde_io.disconnect()

if __name__ == "__main__":
    main()