import pyrealsense2 as rs
import cv2
import mediapipe as mp
import numpy as np
import math
from utils.abfilter import ABFilter

class RobotSafetyMonitor:
    def __init__(self, safety_distance=0.5, color_res=(1280, 720), depth_res=(1280, 720), fps=15):
        self.safety_distance = safety_distance
        self.robotSphereCenter = [1,1,1]
        self.robotSphereRadius = 1
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


    @staticmethod
    def line_sphere_intersection(p1, p2, center, radius):
        # Convert points to numpy arrays
        p1 = np.array(p1)
        p2 = np.array(p2)
        center = np.array(center)

        # Calculate the direction vector of the line
        d = p2 - p1

        # Calculate coefficients for the quadratic equation at^2 + bt + c = 0
        a = np.dot(d, d)
        b = 2 * np.dot(d, p1 - center)
        c = np.dot(p1 - center, p1 - center) - radius**2

        # Calculate the discriminant
        discriminant = b**2 - 4 * a * c

        # Check if there are intersections
        if discriminant < 0:
            return None  # No intersection
        elif discriminant == 0:
            # One intersection (line is tangent to sphere)
            t = -b / (2 * a)
            intersection = p1 + t * d
            return [intersection]
        else:
            # Two intersections
            t1 = (-b + np.sqrt(discriminant)) / (2 * a)
            t2 = (-b - np.sqrt(discriminant)) / (2 * a)
            intersection1 = p1 + t1 * d
            intersection2 = p1 + t2 * d
            return [intersection1, intersection2]


    def checkDistToSphere(self,points):
        minDist = float('inf')  
        center = self.robotSphereCenter 
        radius = self.robotSphereRadius

        for point in points:
            p1 = np.array(point)

            intersections = self.line_sphere_intersection(p1, center, center, radius)

            if intersections is None:
                continue  

            distances = [self.calculate_distance(inter, p1) for inter in intersections]            
            closest_distance = min(distances)

            if closest_distance < minDist:
                minDist = closest_distance

        return minDist


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
        height, width, _ = color_image.shape

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

            # Check distance for each human landmark
            for id, landmark in enumerate(results.pose_landmarks.landmark):
                if(id >=24):#ignore legs
                    break

                cx,cy = self.filter.filter((landmark.x, landmark.y))
                cx = int(cx * width)
                cy = int(cy * height)

                # Ensure the coordinates are within the bounds of the image
                if 0 <= cx < width and 0 <= cy < height:
                    depth_value = depth_frame.get_distance(cx, cy)
                    human_coords = rs.rs2_deproject_pixel_to_point(depth_intrin, [cx, cy], depth_value)

                    # Display the distance for each landmark
                    cv2.putText(color_image, f"D:{distance:.2f}m", (cx, cy),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 1, cv2.LINE_AA)

            landmark_points = [(landmark.x, landmark.y, landmark.z) for landmark in results.pose_landmarks.landmark]
            distance=self.checkDistToSphere(landmark_points)
            if distance<self.safety_distance:
                print("Robot too close to human! Slowing down...")

        # Colors for each patch (you can customize the colors for each rectangle)
        colors = [(0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 255, 0)]  # Green, Blue, Red, Yellow

        # Draw rectangles for each patch
        for i, patch_coords in enumerate(patch_coords_list):
            x, y, w, h = patch_coords
            cv2.rectangle(color_image, (x, y), (x + w, y + h), colors[i], 2)


        # Draw the vertical line in the middle of the image, showing only the bottom 20 pixels
        center_x = width // 2
        line_start_y = height - 50  # Start 20 pixels from the bottom
        line_end_y = height          # End at the bottom of the image
        cv2.line(color_image, (center_x, line_start_y), (center_x, line_end_y), (255, 0, 0), 2)  # Blue line


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

    patch_coords_list = [
        (166, 203, 18, 12), # Component 1
        (152, 223, 18, 12), 
        (133, 243, 18, 12), 
        (113, 265, 18, 12) # Component 4
    ]

    while True:
        monitor.monitor_safety(patch_coords_list)
