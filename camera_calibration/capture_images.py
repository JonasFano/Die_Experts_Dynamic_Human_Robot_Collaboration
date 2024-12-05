import cv2
import os



def main():
    
    os.makedirs("./images", exist_ok=True)

    # Open the default camera (index 0)
    cap = cv2.VideoCapture(6)
    
    # Check if the camera is opened successfully
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    # Initialize the image counter
    img_counter = 0
    
    print("Press 's' to save the image, 'q' to quit.")

    while True:
        # Capture a frame from the camera
        ret, frame = cap.read()
        
        if not ret:
            print("Failed to capture frame. Exiting...")
            break

        # Display the frame in a window
        cv2.imshow("Camera Feed", frame)
        
        # Wait for a key press
        key = cv2.waitKey(1) & 0xFF
        
        # If 'q' is pressed, quit the loop
        if key == ord('q'):
            print("Exiting...")
            break
        
        # If 's' is pressed, save the image
        elif key == ord('s'):
            # Save the frame as an image
            img_name = f"images/image_{img_counter}.png"
            cv2.imwrite(img_name, frame)
            print(f"Image saved: {img_name}")
            img_counter += 1

    # Release the camera and close the window
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
