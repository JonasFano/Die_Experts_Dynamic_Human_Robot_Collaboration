import cv2
import numpy as np
import os
from utils.robot_controller import RobotController
from utils.fixture_checker import CheckFixtures
from utils.state_machine import StateMachine
from utils.safety_monitor import RobotSafetyMonitor

def main():
    # Initialize parameters
    robot_ip = "192.168.1.100"
    safety_distance = 0.5
    home_q_deg = np.array([2.43, -130.48, 95.77, 304.95, 269.33, 261.24])

    current_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(current_dir, 'images', 'reference2.png')

    # Define the patch coordinates (x, y, width, height) ------- x is horizontal and x,y are the top left pixel of the image patch
    patch_coords_list = [
        (166, 204, 20, 15), 
        (148, 222, 20, 15), 
        (132, 242, 20, 15), 
        (112, 262, 20, 15)
    ]

    # Initialize components
    robot_controller = RobotController(robot_ip)
    safety_monitor = RobotSafetyMonitor(safety_distance)
    fixture_checker = CheckFixtures(patch_coords_list, image_path)
    state_machine = StateMachine(robot_controller, safety_monitor, fixture_checker)

    # Move to home position
    robot_controller.move_to_position(home_q_deg)

    try:
        # Start the state machine process
        state_machine.process_state_machine()
    finally:
        # Stop monitoring and clean up
        safety_monitor.stop_monitoring()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()