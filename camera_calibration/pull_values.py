import cv2
import os

camera_calibration_parameters_filename = 'calibration_chessboard.yaml'

print(os.listdir())
# Load the camera parameters from the saved file
cv_file = cv2.FileStorage(
camera_calibration_parameters_filename, cv2.FILE_STORAGE_READ) 
mtx = cv_file.getNode('K').mat()
dst = cv_file.getNode('D').mat()
cv_file.release()


print(mtx)