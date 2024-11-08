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


    def start_processes(self):
        processes = [
            multiprocessing.Process(target=self.monitor_and_adjust),
            multiprocessing.Process(target=self.process_state_machine)
        ]
        for process in processes:
            process.start()
        return processes


    def monitor_and_adjust(self):
        while not self.shared_data["terminate"]:
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
            time.sleep(0.01)


    def process_state_machine(self):
        while not self.shared_data["terminate"]:
            # Process state machine logic if fixture results are available
            if self.shared_data["fixture_results"]:
                self.state_machine.process_state_machine(
                    self.shared_data["fixture_results"],
                    self.shared_data["current_depth_frame"]
                )
            time.sleep(0.01)


    def run(self):
        # Move to home position
        self.robot_controller.moveL(self.home)

        # Start all processes
        processes = self.start_processes()
        try:
            while not self.shared_data["terminate"]:
                time.sleep(0.1)  # Main process idle, waiting for terminate signal
        finally:
            self.shared_data["terminate"] = True
            for process in processes:
                process.join()  # Ensure all processes are terminated
            self.safety_monitor.stop_monitoring()
            cv2.destroyAllWindows()


def main():
    # Initialize parameters
    robot_ip = "192.168.1.100"
    safety_distance = 0.5
    home_pose = np.array([-0.14066618616650417, -0.1347854199496408, 0.50, -1.7173584058437448, 2.614817123624442, 0.015662793265223476])

    current_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(current_dir, 'images', 'reference.png')

    # Define the patch coordinates (x, y, width, height) ------- x is horizontal and x,y are the top left pixel of the image patch
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
