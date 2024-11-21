import cv2

# URL of the IP camera feed (replace with your Flask server's URL)
ip_camera_url = "http://localhost:5000/video_feed"

# Open the video stream
cap = cv2.VideoCapture(ip_camera_url)

if not cap.isOpened():
    print("Error: Unable to access the video stream.")
    exit()

while True:
    # Read a frame from the stream
    ret, frame = cap.read()
    
    if not ret:
        print("Error: Unable to read frame from the stream.")
        break

    # Display the frame
    cv2.imshow('IP Camera Stream', frame)

    # Break the loop on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()