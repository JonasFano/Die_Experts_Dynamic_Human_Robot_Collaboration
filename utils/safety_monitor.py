import pyrealsense2 as rs
import cv2
import mediapipe as mp
import numpy as np
import math

from utils.abfilter import ABFilter

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

        # Set up OpenCV window
        cv2.namedWindow('Pose Detection', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Pose Detection', 1920, 1080)

        self.filter = ABFilter(alpha=0.1,beta=0.05,dt=1/30)


    def set_robot_tcp(self, tcp_pose):
        """Sets the input robot TCP coordinates (simulated)."""
        vector_camera_to_robot = np.array([0.44857067, 0.27121427, 0.38783426]) # np.array([0.44857067, 0.27121427, 0.38783426]) 
        self.tcp_coords = vector_camera_to_robot + tcp_pose[:3]


    def stop_monitoring(self):
        """Stop the pipeline."""
        self.pipeline.stop()


    @staticmethod
    def draw_tcp_on_image(tcp_coords, depth_intrin, color_image):
        """Draws the TCP on the image at the correct pixel coordinates."""
        tcp_pixel_coords = rs.rs2_project_point_to_pixel(depth_intrin, tcp_coords)
        tcp_x, tcp_y = int(tcp_pixel_coords[0]), int(tcp_pixel_coords[1])
        height, width, _ = color_image.shape

        if 0 <= tcp_x < width and 0 <= tcp_y < height:
            cv2.circle(color_image, (tcp_x, tcp_y), 10, (0, 0, 255), -1)  # Red circle
            cv2.putText(color_image, "TCP", (tcp_x + 15, tcp_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)


    @staticmethod
    def calculate_distance(point1, point2):
        """Calculates the Euclidean distance between two 3D points."""
        return math.sqrt(
            (point1[0] - point2[0]) ** 2 +
            (point1[1] - point2[1]) ** 2 +
            (point1[2] - point2[2]) ** 2
        )


    def monitor_safety(self, patch_coords_list):
        """Runs the main loop for safety monitoring."""
        # Get frames from the RealSense camera
        frames = self.pipeline.wait_for_frames()
        aligned_frames = self.align.process(frames)

        depth_frame = aligned_frames.get_depth_frame()
        color_frame = aligned_frames.get_color_frame()

        if not depth_frame or not color_frame:
            return 0

        # Convert RealSense frames to numpy arrays
        color_image = np.asanyarray(color_frame.get_data())
        depth_image = np.asanyarray(depth_frame.get_data())

        # Convert color image to RGB for MediaPipe processing
        rgb_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb_image)

        too_close = False
        distance = 0

        if results.pose_landmarks:
            # Draw the landmarks on the image
            self.mp_drawing.draw_landmarks(
                color_image,
                results.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS,
                self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=4, circle_radius=5),
                self.mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=4, circle_radius=5),
            )

            # Get robot TCP coordinates
            depth_intrin = depth_frame.profile.as_video_stream_profile().intrinsics
            self.draw_tcp_on_image(self.tcp_coords, depth_intrin, color_image)

            height, width, _ = color_image.shape

            # Check distance for each human landmark
            for id, landmark in enumerate(results.pose_landmarks.landmark):
                if(id >=24):#ignore legs
                    break
                # cx = int(landmark.x * width)
                # cy = int(landmark.y * height)

                # cx,cy = self.filter.filter((cx,cy))

                cx,cy = self.filter.filter((landmark.x, landmark.y))
                cx = int(cx * width)
                cy = int(cy * height)

                # Ensure the coordinates are within the bounds of the image
                if 0 <= cx < width and 0 <= cy < height:
                    depth_value = depth_frame.get_distance(cx, cy)
                    human_coords = rs.rs2_deproject_pixel_to_point(depth_intrin, [cx, cy], depth_value)

                    distance = self.calculate_distance(self.tcp_coords, human_coords)

                    # Display the distance for each landmark
                    cv2.putText(color_image, f"D:{distance:.2f}m", (cx, cy),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 1, cv2.LINE_AA)

                    # cv2.putText(color_image, f"D:{human_coords[0]:.2f}, {human_coords[1]:.2f}, {human_coords[2]:.2f}", (cx, cy),
                    #             cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 1, cv2.LINE_AA)

                    # Check if robot is too close to human
                    if distance < self.safety_distance:
                        too_close = True

            if too_close:
                print("Robot too close to human! Slowing down...")

        # Colors for each patch (you can customize the colors for each rectangle)
        colors = [(0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 255, 0)]  # Green, Blue, Red, Yellow

        # Draw rectangles for each patch
        for i, patch_coords in enumerate(patch_coords_list):
            x, y, w, h = patch_coords
            cv2.rectangle(color_image, (x, y), (x + w, y + h), colors[i], 2)


        # Display the image
        cv2.imshow('Pose Detection', color_image)

        # Exit if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            terminate = True
        else:
            terminate = False
        
        return too_close, distance, cv2.cvtColor(color_image, cv2.COLOR_RGB2GRAY), depth_image, terminate


if __name__ == "__main__":
    monitor = RobotSafetyMonitor(safety_distance=0.5)
    monitor.monitor_safety()
