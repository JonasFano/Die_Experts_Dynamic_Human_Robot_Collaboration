import cv2
import numpy as np

def compare_image_patch(reference_image, current_image, patch_coords, threshold=50):
    """
    Compares a predefined patch of the reference and current images.
    
    Parameters:
    - reference_image: Image of the empty fixture (numpy array).
    - current_image: Image with/without the object (numpy array).
    - patch_coords: A tuple of the form (x, y, width, height) defining the patch area to compare.
    - threshold: Pixel intensity difference threshold to detect significant changes (default=50).
    
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


def object_detected(diff_percentage, detection_threshold=5.0):
    """
    Determines if an object has been detected based on the percentage of different pixels.
    
    Parameters:
    - diff_percentage: Percentage of pixels that differ between reference and current patch.
    - detection_threshold: The minimum percentage of difference required to consider an object detected.
    
    Returns:
    - True if object detected, False otherwise.
    """
    return diff_percentage > detection_threshold


def check_for_object_in_patch(reference_image, current_image, patch_coords):
    """
    Checks whether an object has been placed in the fixture by comparing a specific patch of the images.
    
    Parameters:
    - reference_image: Image of the empty fixture (numpy array).
    - current_image: Image with/without the object (numpy array).
    - patch_coords: A tuple of the form (x, y, width, height) defining the patch area to compare.
    
    Returns:
    - True if an object is detected, False otherwise.
    """
    # Perform patch comparison
    diff_percentage, _ = compare_image_patch(reference_image, current_image, patch_coords)
    
    # Determine if the object is detected based on the difference percentage
    if object_detected(diff_percentage):
        return True
    return False


if __name__ == "__main__":
    # Assuming the images are loaded externally and passed as numpy arrays
    # You can capture these from a camera or any other image acquisition system
    reference_image = cv2.imread('empty_fixture.jpg', cv2.IMREAD_GRAYSCALE)  # Load reference image from camera or input
    current_image = cv2.imread('current_fixture.jpg', cv2.IMREAD_GRAYSCALE)  # Load current image from camera or input
    
    # Define the patch coordinates (x, y, width, height)
    patch_coords = (50, 50, 200, 200)  # Example patch coordinates
    
    # Check if an object is detected in the patch
    result = check_for_object_in_patch(reference_image, current_image, patch_coords)
    
    if result:
        print("Object detected in the patch.")
    else:
        print("No object detected in the patch.")
