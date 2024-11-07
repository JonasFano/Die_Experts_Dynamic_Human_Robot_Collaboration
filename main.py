#{import cv2
#import numpy as np
#import os
#from utils.robot_controller import RobotController
#from utils.fixture_checker import CheckFixtures
#from utils.state_machine import StateMachine
#from utils.safety_monitor_prev import RobotSafetyMonitor
#
#def main():
#    # Initialize parameters
#    robot_ip = "192.168.1.100"
#    safety_distance = 0.5
#    home_q_deg = np.array([2.43, -130.48, 95.77, 304.95, 269.33, 261.24])
#    home_pose = np.array([-0.14066618616650417, -0.1347854199496408, 0.5007380032923527, -0.29084513888394903, 3.12302361256465, 0.021555350542996385])
#
#    current_dir = os.path.dirname(os.path.abspath(__file__))
#    image_path = os.path.join(current_dir, 'images', 'reference.png')
#
#    # Define the patch coordinates (x, y, width, height) ------- x is horizontal and x,y are the top left pixel of the image patch
#    patch_coords_list = [
#        (485, 345, 20, 15) # Component 1
#        (465, 365, 20, 15) # Component 2
#        (440, 395, 20, 15) # Component 3
#        (415, 420, 20, 15) # Component 4
#    ]
#
#    # Initialize components
#    robot_controller = RobotController(robot_ip)
#    safety_monitor = RobotSafetyMonitor(safety_distance)
#    fixture_checker = CheckFixtures(patch_coords_list, image_path)
#    state_machine = StateMachine(robot_controller, safety_monitor, fixture_checker)
#
#    # Move to home position
#    robot_controller.move_to_position(home_q_deg)
#    # robot_controller.move_to_cartesian_pose(home_pose)
#
#    try:
#        # Start the state machine process
#        # state_machine.process_state_machine_pose()
#        state_machine.process_state_machine()
#    finally:
#        # Stop monitoring and clean up
#        safety_monitor.stop_monitoring()
#        cv2.destroyAllWindows()
#
#
#if __name__ == "__main__":
#    main()}

# In main.py


import cv2
import numpy as np
import os
import threading
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

        # Shared state
        self.terminate = False
        self.safety_warning, self.distance, self.fixture_results = None, None, None
        self.current_frame, self.current_depth_frame = None, None

        # Initial home position
        self.home = home

    # def start_threads(self):
    #     threads = [
    #         threading.Thread(target=self.monitor_safety),
    #         threading.Thread(target=self.check_fixtures),
    #         threading.Thread(target=self.adjust_velocity)
    #     ]
    #     for thread in threads:
    #         thread.start()
    #     return threads

    def start_threads(self):
        threads = [
            # threading.Thread(target=self.monitor_safety),
            # threading.Thread(target=self.check_fixtures),
            # threading.Thread(target=self.adjust_velocity),
            # threading.Thread(target=self.process_state_machine)  # Add process_state_machine here
        ]
        for thread in threads:
            thread.start()
        return threads


    def monitor_safety(self):
        while not self.terminate:
            print("Monitor Safety is Running")
            
            self.safety_warning, self.distance, self.current_frame, self.current_depth_frame, self.terminate = \
                self.safety_monitor.monitor_safety(self.fixture_checker.patch_coords_list)
            
            self.fixture_results = self.fixture_checker.check_all_patches(self.current_frame, self.current_depth_frame)
            self.state_machine.change_robot_velocity(self.safety_warning, self.fixture_results, self.distance)
            self.safety_monitor.robot_pose_state = self.state_machine.process_state_machine(self.fixture_results, self.current_depth_frame)
            # time.sleep(0.01)  # Short sleep to allow other threads to run


    # def check_fixtures(self):
    #     while not self.terminate and self.current_frame is not None:
    #         self.fixture_results = self.fixture_checker.check_all_patches(self.current_frame, self.current_depth_frame)
    #         self.state_machine.change_robot_velocity(self.safety_warning, self.fixture_results, self.distance)
    #         self.state_machine.process_state_machine(self.fixture_results, self.current_depth_frame)
            # time.sleep(0.01)  # Short sleep to allow other threads to run


    # def adjust_velocity(self):
    #     while not self.terminate:
    #         if self.safety_warning and self.fixture_results:
    #             self.state_machine.change_robot_velocity(self.safety_warning, self.fixture_results, self.distance)
            # time.sleep(0.01)  # Short sleep to allow other threads to run


    # def process_state_machine(self):
    #     while not self.terminate:
    #         if self.fixture_results:
    #             self.state_machine.process_state_machine(self.fixture_results, self.current_depth_frame)
            # time.sleep(0.01)  # Short sleep to allow other threads to run


    # def run(self):
    #     # Move to home position
    #     # self.robot_controller.move_to_position(self.home)
    #     self.robot_controller.moveL(self.home)

    #     # Start threads and main state machine loop
    #     threads = self.start_threads()
    #     try:
    #         self.process_state_machine()
    #     finally:
    #         self.terminate = True
    #         for thread in threads:
    #             thread.join()
    #         self.safety_monitor.stop_monitoring()
    #         cv2.destroyAllWindows()


    def run(self):
        # Move to home position
        self.robot_controller.moveL(self.home)

        # Start all threads, including process_state_machine
        threads = self.start_threads()
        try:
            while not self.terminate:
                self.safety_warning, self.distance, self.current_frame, self.current_depth_frame, self.terminate = \
                    self.safety_monitor.monitor_safety(self.fixture_checker.patch_coords_list)
                
                self.fixture_results = self.fixture_checker.check_all_patches(self.current_frame, self.current_depth_frame)
                self.state_machine.change_robot_velocity(self.safety_warning, self.fixture_results, self.distance)
                self.state_machine.process_state_machine(self.fixture_results, self.current_depth_frame)
            # Main thread can now just wait for user or other events,
            # or simply idle while other threads run independently.
            # for thread in threads:
            #     thread.join()  # Wait for all threads to complete
        finally:
            self.terminate = True
            for thread in threads:
                thread.join()  # Ensure all threads are terminated
            self.safety_monitor.stop_monitoring()
            cv2.destroyAllWindows()



def main():
    # Initialize parameters
    robot_ip = "192.168.1.100"
    safety_distance = 0.5
    # home_q_deg = np.array([2.43, -130.48, 95.77, 304.95, 269.33, 261.24])
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
