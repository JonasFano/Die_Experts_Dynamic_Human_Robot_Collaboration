import pyrealsense2 as rs
import cv2
import mediapipe as mp
import numpy as np
import math
from utils.abfilter import ABFilter
from dataclasses import dataclass
from typing import NamedTuple, List

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
        self, safety_distance=0.5, color_res=(1280, 720), depth_res=(1280, 720), fps=15
    ):
        self.safety_distance = safety_distance
        self.sphere_center_fixtures = [-0.65887, -0.32279, 1.93131]  # in camera frame
        self.sphere_center_home = [-0.53615, -0.11935, 1.23248]
        self.sphere_center_place = [-0.15476, 0.1909, 0.91111]
        self.robot_pose_state = 0  # 0 -> home, 1 -> fixtures, 2 -> place
        self.min_distance_array = []

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

        # Start the camera stream
        self.pipeline.start(self.config)

        """
        # Unsure if needed
        # Set up OpenCV window
        cv2.namedWindow("Pose Detection", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Pose Detection", 1920, 1080)
        """

        self.filter = ABFilter(alpha=0.1, beta=0.05, dt=1 / 30)

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

    @staticmethod
    def apply_landmark_overlay(self, color_img: np.ndarray, poses: NamedTuple) -> None:
        """If landmarks present, draw landmark pose markers onto an image"""
        if poses.pose_landmarks:
            self.mp_drawing.draw_landmarks(
                color_img,
                poses.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS,
                self.mp_drawing.DrawingSpec(
                    color=(0, 255, 0), thickness=4, circle_radius=5
                ),
                self.mp_drawing.DrawingSpec(
                    color=(255, 0, 0), thickness=4, circle_radius=5
                ),
            )

    @staticmethod
    def calculate_human_robot_distance(
        self, poses: NamedTuple, color_frame: rs.color_frame, color_image: np.ndarray
    ) -> float:
        """Calculate the minimum distance between the human and the robot"""
        min_distance = float("inf")
        if poses.pose_landmarks:
            height, width, _ = color_image.shape

            depth_intrin = color_frame.profile.as_video_stream_profile().intrinsics

            # Check distance for each human landmark
            for id, landmark in enumerate(poses.pose_landmarks.landmark):
                if id >= 24:  # Ignore leg landmarks
                    break

                cx, cy = self.filter.filter((landmark.x, landmark.y))
                cx = int(cx * width)
                cy = int(cy * height)

                # Ensure the coordinates are within the bounds of the image
                if 0 <= cx < width and 0 <= cy < height:
                    depth_value = color_frame.get_distance(cx, cy)
                    human_coords = rs.rs2_deproject_pixel_to_point(
                        depth_intrin, [cx, cy], depth_value
                    )

                    distance = self.calculate_distance_to_sphere(human_coords)
                    min_distance = min(
                        min_distance, distance
                    )  # Track the minimum distance

        return min_distance

    @staticmethod
    def calculate_poses(self, color_image: np.ndarray) -> NamedTuple:
        rgb_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)
        return self.pose.process(
            rgb_image
        )  # Used for creating pose overlay, calculating distance between human and robot

    # TODO: What is this used for?
    @staticmethod
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
        cv2.line(
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
        frames = self.pipeline.wait_for_frames()
        aligned_frames = self.align.process(frames)

        depth_frame = aligned_frames.get_depth_frame()
        color_frame = aligned_frames.get_color_frame()
        color_image = np.asanyarray(color_frame.get_data())
        depth_image = np.asanyarray(depth_frame.get_data())

        return SafetyFrameResults(color_frame, color_image, depth_frame, depth_image)
