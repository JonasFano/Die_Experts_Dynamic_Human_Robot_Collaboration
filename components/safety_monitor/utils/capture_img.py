import cv2
import os
from itertools import combinations

def main():
    components = ["1", "3", "5", "6"]
    # Do all possible combinations
    images_needed = [list(combinations(components, i)) for i in range(1, len(components)+1)]
    # Flatten list
    images_needed = sum(images_needed, [])
    # Sort by length to make it more enjoyable to take pictures
    images_needed = list(sorted(images_needed, key=lambda x: len(x), reverse=True))

    os.makedirs("./images", exist_ok=True)

    # Open the default camera (index 0)
    cap = cv2.VideoCapture(6)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    cv2.namedWindow("Camera Feed", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Camera Feed", 1280, 720) 

    # Check if the camera is opened successfully
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    # Initialize the image counter
    img_counter = 0
    
    print("Press 's' to save the image, 'q' to quit.")
    
    images_index = 0
    while True:
        # Capture a frame from the camera
        ret, frame = cap.read()
        
        if not ret:
            print("Failed to capture frame. Exiting...")
            break

        cv2.putText(frame, f"Config: {images_needed[images_index]}", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,0), 2, cv2.LINE_AA)

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
            print(os.path.abspath("./images"))
            combination_joined = "_".join(list(images_needed[images_index]))
            img_name = f"images/image_{combination_joined}.png"
            cv2.imwrite(img_name, frame)
            print(f"Image saved: {img_name}")
            img_counter += 1
            images_index += 1

    # Release the camera and close the window
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
