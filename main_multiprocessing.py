import cv2
import numpy as np
import os
import multiprocessing
from utils.robot_controller import RobotController
from utils.fixture_checker import CheckFixtures
from utils.state_machine import StateMachine
from utils.safety_monitor_prev import RobotSafetyMonitor
import time


class RobotProcessManager:
    def __init__(self, robot_ip, safety_distance, home, patch_coords_list, image_path):
        # Initialize robot components
        self.robot_controller = RobotController(robot_ip)
        self.safety_monitor = RobotSafetyMonitor(safety_distance)
        self.fixture_checker = CheckFixtures(patch_coords_list, image_path)
        self.state_machine = StateMachine(self.robot_controller, self.fixture_checker)

        # Manager for shared state
        manager = multiprocessing.Manager()
        self.shared_data = manager.dict()
        self.shared_data["terminate"] = False
        self.shared_data["safety_warning"] = None
        self.shared_data["distance"] = None
        self.shared_data["fixture_results"] = None
        self.shared_data["current_frame"] = None
        self.shared_data["current_depth_frame"] = None

        # Initial home position
        self.home = home

    def start_process(self):
        # Start process_state_machine as a separate process
        process = multiprocessing.Process(target=self.process_state_machine)
        process.start()
        return process

    def monitor_and_adjust(self):
        """This function runs within the main process and monitors safety conditions."""
        print("Monitor Safety and Adjust Velocity is Running")

        # Run safety monitoring
        self.shared_data["safety_warning"], self.shared_data["distance"], \
        self.shared_data["current_frame"], self.shared_data["current_depth_frame"], \
        self.shared_data["terminate"] = self.safety_monitor.monitor_safety(self.fixture_checker.patch_coords_list)

        # Check fixtures
        self.shared_data["fixture_results"] = self.fixture_checker.check_all_patches(
            self.shared_data["current_frame"],
            self.shared_data["current_depth_frame"]
        )

        # Adjust robot velocity based on fixture check results and safety warning
        self.state_machine.change_robot_velocity(
            self.shared_data["safety_warning"],
            self.shared_data["fixture_results"],
            self.shared_data["distance"]
        )

    def process_state_machine(self):
        """This function runs in a separate process."""
        while not self.shared_data["terminate"]:
            print(self.shared_data["fixture_results"])
        
            # Process state machine logic if fixture results are available
            if np.any(self.shared_data["fixture_results"]):
                self.state_machine.process_state_machine(
                    self.shared_data["fixture_results"],
                    self.shared_data["current_depth_frame"]
                )
            # time.sleep(0.01)

    def run(self):
        # Move to home position
        self.robot_controller.moveL(self.home)

        # Start the process for state machine management
        state_machine_process = self.start_process()

        try:
            while not self.shared_data["terminate"]:
                # Perform safety monitoring and adjustment within the main process
                self.monitor_and_adjust()
                time.sleep(0.1)
        finally:
            self.shared_data["terminate"] = True
            state_machine_process.join()  # Ensure the process is terminated
            self.safety_monitor.stop_monitoring()
            cv2.destroyAllWindows()


def main():
    # Initialize parameters
    robot_ip = "192.168.1.100"
    safety_distance = 0.4
    home_pose = np.array([-0.14066618616650417, -0.1347854199496408, 0.50, -1.7173584058437448, 2.614817123624442, 0.015662793265223476])

    current_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(current_dir, 'images', 'reference.png')

    # Define the patch coordinates (x, y, width, height)
    patch_coords_list = [
        (480, 325, 20, 15), 
        (460, 350, 20, 15), 
        (435, 375, 20, 15), 
        (410, 400, 20, 15)
    ]

    # Initialize and run the manager
    manager = RobotProcessManager(robot_ip, safety_distance, home_pose, patch_coords_list, image_path)
    manager.run()


if __name__ == "__main__":
    main()
