from shared.create_realsense_pipeline import create_pipeline
from safety_monitor.utils.fixture_checker import CheckFixtures
import pathlib
import numpy as np
import cv2
import time
import os

def calculate_answer(image_name):
    components_used = image_name.split(".")[0]
    components_used= components_used.split("_")[1:]

    result = []
    for n in [1,3,5,6]:
        if str(n) in components_used:
            result.append(1)
        else:
            result.append(0)

    return result

def test():
    # TODO: Are these the correct coordinates?
    patch_coords_list = [
        (339, 365, 20, 15), # Component 1
        (299, 393, 20, 15), # Component 2
        (270, 415, 20, 15), # Component 3
        (230, 470, 20, 15), # Component 4
    ]


    current_file_path = pathlib.Path(__file__).parent.resolve()
    image_dir = os.path.join(current_file_path, "../../images/")

    reference_image_path = os.path.join(image_dir, "reference.png")
    testing_images = []
    for x in os.listdir(image_dir):
        if x.startswith("image_"):
            testing_images.append(x)
    check_fixtures = CheckFixtures(patch_coords_list, reference_image_path)

    print("image name - answer = patch ")

    for image_name in testing_images:

        # Convert RealSense frames to numpy arrays
        image_path = os.path.join(image_dir, image_name)
        color_image = cv2.imread(image_path)  # Load reference image from camera or input

        answer = calculate_answer(image_name)
        patch_check = check_fixtures.check_all_patches(color_image, color_image)
        print(f"{image_name}: ")
        print(f"{answer} = {(patch_check)} : {answer == patch_check}")

if __name__ == "__main__":
    test()