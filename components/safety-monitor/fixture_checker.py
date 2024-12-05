import cv2
import numpy as np

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
    

    def calibrate_depth(self, current_depth_image):
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


    def visualize_all_patches(self, image):
        # Convert the grayscale image to BGR to display colored rectangles
        image_with_patches = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

        # Colors for each patch (you can customize the colors for each rectangle)
        colors = [(0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 255, 0)]  # Green, Blue, Red, Yellow

        # Draw rectangles for each patch
        for i, patch_coords in enumerate(self.patch_coords_list):
            x, y, w, h = patch_coords
            cv2.rectangle(image_with_patches, (x, y), (x + w, y + h), colors[i], 2)

        # Display the image with all patches
        cv2.imshow("Image with Patches", image_with_patches)

        # Wait for a key press and close windows
        cv2.waitKey(0)
        cv2.destroyAllWindows()


if __name__ == "__main__":
    # Assuming the images are loaded externally and passed as numpy arrays
    # You can capture these from a camera or any other image acquisition system
    reference_image = cv2.imread('images/reference.png', cv2.IMREAD_GRAYSCALE)  # Load reference image from camera or input

    
    # Define the patch coordinates (x, y, width, height) ------- x is horizontal and x,y are the top left pixel of the image patch
    # patch_coords_1 = (175, 205, 20, 15) # Component 1
    # patch_coords_2 = (155, 225, 20, 15) # Component 2
    # patch_coords_3 = (140, 245, 20, 15) # Component 3
    # patch_coords_4 = (120, 265, 20, 15) # Component 4
    patch_coords_1 = (485, 345, 20, 15) # Component 1
    patch_coords_2 = (465, 365, 20, 15) # Component 2
    patch_coords_3 = (440, 395, 20, 15) # Component 3
    patch_coords_4 = (415, 420, 20, 15) # Component 4


    # List of all patch coordinates
    patch_coords_list = [patch_coords_1, patch_coords_2, patch_coords_3, patch_coords_4]

    ref_img_path = 'images/reference.png'
    check_fixtures = CheckFixtures(patch_coords_list, ref_img_path)


    # CheckFixtures.visualize(current_image, patch_coords_3)
    # check_fixtures.visualize_all_patches(current_image)
    check_fixtures.visualize_all_patches(reference_image)

    # Check if objects are detected in all patches
    try:
        current_image = cv2.imread('images/all_components.png', cv2.IMREAD_GRAYSCALE)  # Load current image from camera or input

        results = check_fixtures.check_all_patches(current_image)
        
        for patch, detected in results.items():
            if detected:
                print(f"Object detected in {patch}.")
            else:
                print(f"No object detected in {patch}.")
    except Exception:
        print("No image to compare to")