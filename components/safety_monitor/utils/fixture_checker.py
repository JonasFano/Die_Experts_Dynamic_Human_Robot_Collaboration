import cv2
import numpy as np
import pathlib
import os

class CheckFixtures:
    def __init__(self, patch_coords_list, image_path, intensity_threshold=40, percentage_threshold=35, min_dist=1.2, max_dist=1.8):
        self.patch_coords_list = patch_coords_list
        self.reference_image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        self.intensity_threshold = intensity_threshold # Pixel intensity difference threshold to detect significant changes.
        self.percentage_threshold = percentage_threshold # The minimum percentage of difference required to consider an object detected.
        self.min_dist = min_dist  # Minimum valid distance for object detection
        self.max_dist = max_dist  # Maximum valid distance for object detection

    @staticmethod
    def compare_image_patch(reference_image, current_image, patch_coords, threshold=100):
        """
        Compares a predefined patch of the reference and current images.
        
        Parameters:
        - reference_image: Image of the empty fixture (numpy array).
        - current_image: Image with/without the object (numpy array).
        - patch_coords: A tuple of the form (x, y, width, height) defining the patch area to compare where x,y is the top left point of the image patch.
        - threshold: Pixel intensity difference threshold to detect significant changes (default=40).
        
        Returns:
        - diff_percentage: The percentage of pixels that differ between the reference and current patch.
        - threshold_diff: The binary difference image highlighting significant changes.
        """
        
        # Step 1: Extract the patch from the images based on the coordinates
        x, y, w, h = patch_coords
        reference_patch = reference_image[y:y+h, x:x+w]
        current_patch = current_image[y:y+h, x:x+w]

        if reference_patch.shape != current_patch.shape:
            raise ValueError("The patches must have the same dimensions for comparison.")
        
        # Step 2: Compute the absolute difference between the reference and current patch
        difference = cv2.absdiff(reference_patch, current_patch)

        # Step 3: Threshold the difference to only count significant changes
        _, threshold_diff = cv2.threshold(difference, threshold, 255, cv2.THRESH_BINARY)

        # Step 4: Calculate the percentage of pixels that are different
        num_diff_pixels = np.sum(threshold_diff > 0)
        total_pixels = reference_patch.shape[0] * reference_patch.shape[1]
        diff_percentage = (num_diff_pixels / total_pixels) * 100

        return diff_percentage, threshold_diff


    @staticmethod
    def object_detected(diff_percentage, percentage_threshold=50.0):
        """
        Determines if an object has been detected based on the percentage of different pixels.
        
        Parameters:
        - diff_percentage: Percentage of pixels that differ between reference and current patch.
        - percentage_threshold: The minimum percentage of difference required to consider an object detected.
        
        Returns:
        - True if object detected, False otherwise.
        """
        # print(diff_percentage)
        return diff_percentage > percentage_threshold


    def check_for_object_intensity(self, current_image, patch_coords):
        """
        Checks whether an object has been placed in the fixture by comparing a specific patch of the images.
        
        Parameters:
        - current_image: Image with/without the object (numpy array).
        - patch_coords: A tuple of the form (x, y, width, height) defining the patch area to compare.

        
        Returns:
        - True if an object is detected, False otherwise.
        """
        # Perform patch comparison
        diff_percentage, _ = self.compare_image_patch(self.reference_image, current_image, patch_coords, self.intensity_threshold)
        
        # Determine if the object is detected based on the difference percentage
        if CheckFixtures.object_detected(diff_percentage, self.percentage_threshold):
            return True
        return False


    def check_all_patches_only_intensity(self, current_image):
        """
        Checks if an object has been detected in any of the given patches.

        Parameters:
        - current_image: Image with/without the object (numpy array).

        Returns:
        - A numpy array where each element is 0 (empty) or 1 (full) for the corresponding patch.
        """
        # Create an empty list to store the results
        results = []

        # Iterate over each patch in the list of patch coordinates
        for patch_coords in self.patch_coords_list:
            # Call the function to check if the object is in the patch
            result = self.check_for_object_intensity(self.reference_image, current_image, patch_coords, self.intensity_threshold, self.percentage_threshold)
            
            # Convert the result to 1 (full) or 0 (empty)
            patch_status = 1 if result else 0
            
            # Append the result to the list
            results.append(patch_status)
        
        # Convert the results list to a numpy array and return
        return np.array(results)
    

    def check_depth(self, current_depth_image, patch_coords):
        """
        Computes the average depth in the patch of the current depth image
        
        Parameters:
        - current_depth_image: Depth image corresponding to the current_image (numpy array).
        - patch_coords: A tuple of the form (x, y, width, height) defining the patch area to compare.
        """
        # Check the depth in the patch
        x, y, w, h = patch_coords
        depth_patch = current_depth_image[y:y+h, x:x+w]

        # Calculate the average depth in the patch
        avg_depth = np.mean(depth_patch) / 1000
        return avg_depth


    def check_for_object_intensity_and_depth(self, current_image, current_depth_image, patch_coords):
        """
        Checks whether an object has been placed in the fixture by comparing a specific patch of the images,
        and verifying that the distance in the depth image is within the valid range.
        
        Parameters:
        - current_image: Image with/without the object (numpy array).
        - current_depth_image: Depth image corresponding to the current_image (numpy array).
        - patch_coords: A tuple of the form (x, y, width, height) defining the patch area to compare.
        
        Returns:
        - True if an object is detected and within the depth range, False otherwise.
        """
        # Perform patch comparison
        diff_percentage, _ = self.compare_image_patch(self.reference_image, current_image, patch_coords, self.intensity_threshold)

        # Check if the object is detected based on the difference percentage
        if self.object_detected(diff_percentage, self.percentage_threshold):
            # Check the depth in the patch
            avg_depth = self.check_depth(current_depth_image, patch_coords)

            # Check if the depth is within the specified range
            if self.min_dist < avg_depth < self.max_dist:
                return True  # Object detected and within valid depth range
        
        return False  # Either object not detected or depth not in range
    

    def _calibrate_depth(self, current_depth_image):
        """
        Helps calibrating the depth values to successfully detect a component in any of the given patches.

        Parameters:
        - current_depth_image: Depth image with/without the object (numpy array).
        """
        # Create an empty list to store the results

        #results = []

        # Iterate over each patch in the list of patch coordinates with index
        for patch_idx, patch_coords in enumerate(self.patch_coords_list):
            # Call the function to check depth
            avg_depth = self.check_depth(current_depth_image, patch_coords)

            #print(f"Patch {patch_idx + 1}: {avg_depth}")
    

    def check_all_patches(self, current_image, current_depth_image):
        """
        Checks if an object has been detected in any of the given patches.
        Additionally uses the depth image to differentiate between detecting the components or the robot.

        Parameters:
        - current_image: Image with/without the object (numpy array).
        - current_depth_image: Depth image with/without the object (numpy array).

        Returns:
        - A numpy array where each element is 0 (empty) or 1 (full) for the corresponding patch.
        """
        # Create an empty list to store the results
        results = []

        current_image = cv2.cvtColor(current_image, cv2.COLOR_RGB2GRAY)

        # Iterate over each patch in the list of patch coordinates
        for patch_coords in self.patch_coords_list:
            # Call the function to check if the object is in the patch
            result = self.check_for_object_intensity_and_depth(current_image, current_depth_image, patch_coords)
            
            # Convert the result to 1 (full) or 0 (empty)
            patch_status = 1 if result else 0
            
            # Append the result to the list
            results.append(patch_status)
        
        # Convert the results list to a numpy array and return
        return results

    def debug_patches(self, image, reference_image, patch_coords):
        for i, patch in enumerate(patch_coords):
            diff_percentage, _ = self.compare_image_patch(
                reference_image, image, patch, 40)
            detected = self.object_detected(diff_percentage, 50)
            display_string = f"{i+1} : {diff_percentage:0.2f} | detected: {detected}"
            text_color = (255,255,255)
            if detected:
                text_color = (255,0,0)
            cv2.putText(image, display_string, (100, (i+1)* 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, text_color, 2, cv2.LINE_AA)

            cv2.putText(image, str(i+1), (patch[0], patch[1]-10),
                cv2.FONT_HERSHEY_SIMPLEX, 1, text_color, 2, cv2.LINE_AA)

        
        self.draw_patches(image)


    @staticmethod
    def visualize(image, patch_coords):
        # Extract x, y, width, and height from patch coordinates
        x, y, w, h = patch_coords

        # Draw rectangles on the images
        # Color is BGR, and thickness is the border thickness (set to 2 here)
        image_with_patch = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)  # Convert to BGR to display color rectangle

        cv2.rectangle(image_with_patch, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Green rectangle on reference image

        cv2.imshow("Image with Patch", image_with_patch)

        # Wait for a key press and close windows
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def draw_patches(self, image):
        # Colors for each patch (you can customize the colors for each rectangle)
        colors = [(0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 255, 255)]  # Green, Blue, Red, Yellow
        # Draw rectangles for each patch
        for i, patch_coords in enumerate(self.patch_coords_list):
            x, y, w, h = patch_coords
            cv2.rectangle(image, (x, y), (x + w, y + h), colors[i], 2)

    def visualize_all_patches(self, image):
        # Convert the grayscale image to BGR to display colored rectangles
        #image_with_patches = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

        self.draw_patches(image)

        # Display the image with all patches
        cv2.imshow("Image with Patches", image)

        # Wait for a key press and close windows
        cv2.waitKey(0)
        cv2.destroyAllWindows()

# Old test code for testing the fixtures
def _test_main():
    # Assuming the images are loaded externally and passed as numpy arrays
    # You can capture these from a camera or any other image acquisition system

    current_file_path = pathlib.Path(__file__).parent.resolve()
    reference_image_path = os.path.join(current_file_path, "../images/reference.png")
    all_components_path = os.path.join(current_file_path, "../images/all_components.png")

    reference_image = cv2.imread(reference_image_path, cv2.IMREAD_COLOR)  # Load reference image from camera or input

    
    patch_coords_1 = (485, 345, 20, 15) # Component 1
    patch_coords_2 = (465, 365, 20, 15) # Component 2
    patch_coords_3 = (440, 395, 20, 15) # Component 3
    patch_coords_4 = (415, 420, 20, 15) # Component 4

    # List of all patch coordinates
    patch_coords_list = [patch_coords_1, patch_coords_2, patch_coords_3, patch_coords_4]

    check_fixtures = CheckFixtures(patch_coords_list, reference_image_path)


    # CheckFixtures.visualize(current_image, patch_coords_3)
    # check_fixtures.visualize_all_patches(current_image)
    check_fixtures.visualize_all_patches(reference_image)

    # Check if objects are detected in all patches
    depth_image = cv2.imread(all_components_path, cv2.IMREAD_COLOR)  # Load current image from camera or input

    results = check_fixtures.check_all_patches(reference_image, depth_image)
    
    for patch, detected in enumerate(results):
        if detected:
            print(f"Object detected in {patch+1}.")
        else:
            print(f"No object detected in {patch+1}.")
    

def _main_realsense():
    import time
    window_name = "Fixture checker"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 1280, 720)

    #Realsense2
    from shared.create_realsense_pipeline import create_pipeline

    (pipeline, align) = create_pipeline()

    # Fixture checker
    
    # TODO: Are these the correct coordinates?
    patch_coords_list = [
        (339, 365, 20, 15), # Component 1
        (299, 393, 20, 15), # Component 2
        (270, 415, 20, 15), # Component 3
        (231, 458, 20, 15), # Component 4
    ]


    current_file_path = pathlib.Path(__file__).parent.resolve()
    reference_image_path = os.path.join(current_file_path, "images/reference2.png")
    check_fixtures = CheckFixtures(patch_coords_list, reference_image_path, intensity_threshold=60)


    while True:
        frames = pipeline.wait_for_frames()
        aligned_frames = align.process(frames)

        color_frame = aligned_frames.get_color_frame()
        depth_frame = aligned_frames.get_depth_frame()

        
        # Convert RealSense frames to numpy arrays
        color_image = np.asanyarray(color_frame.get_data())
        depth_image = np.asanyarray(depth_frame.get_data())
        gray_image = cv2.cvtColor(color_image, cv2.COLOR_RGB2GRAY)
        
        reference_image = cv2.imread(reference_image_path, cv2.IMREAD_GRAYSCALE)  # Load reference image from camera or input
        cv2.imshow("Referemce Image", reference_image)

        check_fixtures.debug_patches(gray_image, reference_image, patch_coords_list)

        fixture_status = check_fixtures.check_all_patches(color_image, depth_image)
        cv2.putText(gray_image, str(fixture_status), (100, 300),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2, cv2.LINE_AA)

        #print(check_fixture½s.check_all_patches(color_image, depth_image))
        cv2.imshow(window_name, gray_image)
        # Being able to read values
        cv2.waitKey(1)

        
if __name__ == "__main__":
    _main_realsense()