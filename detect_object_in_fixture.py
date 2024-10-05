import cv2
import numpy as np

def compare_image_patch(reference_image, current_image, patch_coords, threshold=50):
    """
    Compares a predefined patch of the reference and current images.
    
    Parameters:
    - reference_image: Image of the empty fixture (numpy array).
    - current_image: Image with/without the object (numpy array).
    - patch_coords: A tuple of the form (x, y, width, height) defining the patch area to compare where x,y is the top left point of the image patch.
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


def object_detected(diff_percentage, detection_threshold=65.0):
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


def check_all_patches(reference_image, current_image, patch_coords_list):
    """
    Checks if an object has been detected in any of the given patches.
    
    Parameters:
    - reference_image: Image of the empty fixture (numpy array).
    - current_image: Image with/without the object (numpy array).
    - patch_coords_list: List of tuples, each defining a patch (x, y, width, height).
    
    Returns:
    - A dictionary with results for each patch (True if object detected, False otherwise).
    """
    results = {}
    for i, patch_coords in enumerate(patch_coords_list):
        result = check_for_object_in_patch(reference_image, current_image, patch_coords)
        results[f"Patch_{i+1}"] = result
    return results


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


def visualize_all_patches(image, patch_coords_list):
    # Convert the grayscale image to BGR to display colored rectangles
    image_with_patches = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    # Colors for each patch (you can customize the colors for each rectangle)
    colors = [(0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 255, 0)]  # Green, Blue, Red, Yellow

    # Draw rectangles for each patch
    for i, patch_coords in enumerate(patch_coords_list):
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
    current_image = cv2.imread('images/all_components.png', cv2.IMREAD_GRAYSCALE)  # Load current image from camera or input
    image_without_comp_1 = cv2.imread('images/image_without_comp_1.png', cv2.IMREAD_GRAYSCALE)
    image_without_comp_2 = cv2.imread('images/image_without_comp_2.png', cv2.IMREAD_GRAYSCALE)
    image_without_comp_3 = cv2.imread('images/image_without_comp_3.png', cv2.IMREAD_GRAYSCALE)
    image_without_comp_4 = cv2.imread('images/image_without_comp_4.png', cv2.IMREAD_GRAYSCALE)

    
    # Define the patch coordinates (x, y, width, height) ------- x is horizontal and x,y are the top left pixel of the image patch
    patch_coords_1 = (175, 205, 20, 15) # Component 1
    patch_coords_2 = (155, 225, 20, 15) # Component 2
    patch_coords_3 = (140, 245, 20, 15) # Component 3
    patch_coords_4 = (120, 265, 20, 15) # Component 4

    # visualize(current_image, patch_coords_3)
    # visualize_all_patches(current_image, patch_coords_list)
    # visualize_all_patches(reference_image, patch_coords_list)

    # List of all patch coordinates
    patch_coords_list = [patch_coords_1, patch_coords_2, patch_coords_3, patch_coords_4]

    # Check if objects are detected in all patches
    results = check_all_patches(reference_image, current_image, patch_coords_list)
    
    for patch, detected in results.items():
        if detected:
            print(f"Object detected in {patch}.")
        else:
            print(f"No object detected in {patch}.")
    




    # Check if objects are detected in all patches
    results = check_all_patches(reference_image, image_without_comp_1, patch_coords_list)
    print("New image")
    for patch, detected in results.items():
        if detected:
            print(f"Object detected in {patch}.")
        else:
            print(f"No object detected in {patch}.")


    # Check if objects are detected in all patches
    results = check_all_patches(reference_image, image_without_comp_2, patch_coords_list)
    print("New image")
    for patch, detected in results.items():
        if detected:
            print(f"Object detected in {patch}.")
        else:
            print(f"No object detected in {patch}.")

    
    # Check if objects are detected in all patches
    results = check_all_patches(reference_image, image_without_comp_3, patch_coords_list)
    print("New image")
    for patch, detected in results.items():
        if detected:
            print(f"Object detected in {patch}.")
        else:
            print(f"No object detected in {patch}.")


    # Check if objects are detected in all patches
    results = check_all_patches(reference_image, image_without_comp_4, patch_coords_list)
    print("New image")
    for patch, detected in results.items():
        if detected:
            print(f"Object detected in {patch}.")
        else:
            print(f"No object detected in {patch}.")