import cv2
import dlib
import numpy as np
from imutils import face_utils
from shared.ilogging import CustomLogger

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

# Blink counter variables
blink_count = 0
blink_threshold = 0.25  # EAR threshold to detect blink
frames_to_consider_blink = 2  # Minimum consecutive frames for a blink
consecutive_frames = 0
logger = CustomLogger()

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
                logger.log("Blink", blink_count)
            consecutive_frames = 0

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