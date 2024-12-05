import cv2
import dlib
import numpy as np
from imutils import face_utils

# Load the dlib face detector and facial landmark predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")  # need to download this model online


# Function to calculate Eye Aspect Ratio (EAR)
def calculate_ear(eye_points):
    A = np.linalg.norm(eye_points[1] - eye_points[5])  # vertical distance
    B = np.linalg.norm(eye_points[2] - eye_points[4])  # vertical distance
    C = np.linalg.norm(eye_points[0] - eye_points[3])  # horizontal distance
    ear = (A + B) / (2.0 * C)
    return ear

# Function to detect if the user is looking at the task area
def is_looking_at_task(eye_points, frame):
    # Calculate the center of the eye
    left_point = (eye_points[0, 0], eye_points[0, 1])
    right_point = (eye_points[3, 0], eye_points[3, 1])
    center_top = midpoint(eye_points[1], eye_points[2])
    center_bottom = midpoint(eye_points[5], eye_points[4])

    # Draw a circle at the center
    hor_line = cv2.line(frame, left_point, right_point, (0, 255, 0), 2)
    ver_line = cv2.line(frame, center_top, center_bottom, (0, 255, 0), 2)

    # Calculate the midpoint of the horizontal and vertical lines (approximation of the pupil center)
    pupil_x = (left_point[0] + right_point[0]) // 2
    pupil_y = (center_top[1] + center_bottom[1]) // 2

    # Draw the pupil center
    cv2.circle(frame, (pupil_x, pupil_y), 2, (255, 255, 0), -1)


    # Estimate if the pupil is within a specific region (simple approach)
    # You can define a "task area" on the screen and compare the gaze direction with that area.
    screen_center_x = frame.shape[1] // 2
    screen_center_y = frame.shape[0] // 2

    
    # Draw the center of the screen
    cv2.circle(frame, (screen_center_x, screen_center_y), 5, (255, 255, 255), -1)

    # Draw a rectangle for the task area
    cv2.rectangle(frame, 
              (screen_center_x - 50, screen_center_y - 50), 
              (screen_center_x + 50, screen_center_y + 50), 
              (255, 0, 0), 2)



    # Check if the user is looking at the center of the screen (task area)
    if screen_center_x - 50 < pupil_x < screen_center_x + 50 and screen_center_y - 50 < pupil_y < screen_center_y + 50:
        return True
    return False

# Function to calculate midpoint between two points
def midpoint(p1, p2):
    return int((p1[0] + p2[0]) / 2), int((p1[1] + p2[1]) / 2)


# Blink counter variables
blink_count = 0
blink_threshold = 0.25  # EAR threshold to detect blink
frames_to_consider_blink = 2  # Minimum consecutive frames for a blink
consecutive_frames = 0

# Start video capture
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Convert frame to grayscale for better processing
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces
    faces = detector(gray)
    for face in faces:
        # Get the landmarks/parts for the face
        shape = predictor(gray, face)
        shape = face_utils.shape_to_np(shape)

        # Extract the left and right eye coordinates
        left_eye = shape[36:42]
        right_eye = shape[42:48]

        # Calculate EAR for both eyes
        left_ear = calculate_ear(left_eye)
        right_ear = calculate_ear(right_eye)
        avg_ear = (left_ear + right_ear) / 2.0

        # Check for blink
        if avg_ear < blink_threshold:
            consecutive_frames += 1
        else:
            if consecutive_frames >= frames_to_consider_blink:
                blink_count += 1
            consecutive_frames = 0

        # Check if the user is looking at the task area
        if is_looking_at_task(left_eye, frame) or is_looking_at_task(right_eye, frame):
            cv2.putText(frame, "Looking at Task", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        else:
            cv2.putText(frame, "Not Looking at Task", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # Draw the eye region on the frame
        for (x, y) in left_eye:
            cv2.circle(frame, (x, y), 2, (255, 0, 0), -1)
        for (x, y) in right_eye:
            cv2.circle(frame, (x, y), 2, (255, 0, 0), -1)


    # Display the blink count
    cv2.putText(frame, f"Blinks: {blink_count}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

    # Show the frame
    cv2.imshow("Eye Tracking", frame)

    # Break the loop on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release video capture and close windows
cap.release()
cv2.destroyAllWindows()
