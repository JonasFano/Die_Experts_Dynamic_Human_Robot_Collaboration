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

class RobotProcessManager:
    def __init__(self, robot_ip, safety_distance, home_q_deg, patch_coords_list, image_path):
        # Initialize robot components
        self.robot_controller = RobotController(robot_ip)
        self.safety_monitor = RobotSafetyMonitor(safety_distance)
        self.fixture_checker = CheckFixtures(patch_coords_list, image_path)
        self.state_machine = StateMachine(self.robot_controller, self.safety_monitor, self.fixture_checker)

        # Shared state
        self.terminate = False
        self.safety_warning, self.distance, self.fixture_results = None, None, None
        self.current_frame, self.current_depth_frame = None, None

        # Initial home position
        self.home_q_deg = home_q_deg

    def start_threads(self):
        threads = [
            threading.Thread(target=self.monitor_safety),
            threading.Thread(target=self.check_fixtures),
            threading.Thread(target=self.adjust_velocity)
        ]
        for thread in threads:
            thread.start()
        return threads

    def monitor_safety(self):
        while not self.terminate:
            tcp_pose = self.robot_controller.get_tcp_pose()
            self.safety_monitor.set_robot_tcp(tcp_pose)
            self.safety_warning, self.distance, self.current_frame, self.current_depth_frame, self.terminate = \
                self.safety_monitor.monitor_safety(self.fixture_checker.patch_coords_list)

    def check_fixtures(self):
        while not self.terminate and self.current_frame is not None:
            self.fixture_results = self.fixture_checker.check_all_patches(self.current_frame, self.current_depth_frame)

    def adjust_velocity(self):
        while not self.terminate:
            if self.safety_warning and self.fixture_results:
                self.state_machine.change_robot_velocity(self.safety_warning, self.fixture_results, self.distance)

    def process_state_machine(self):
        while not self.terminate:
            if self.fixture_results:
                self.state_machine.process_state_machine(self.fixture_results, self.current_depth_frame)

    def run(self):
        # Move to home position
        self.robot_controller.move_to_position(self.home_q_deg)

        # Start threads and main state machine loop
        threads = self.start_threads()
        try:
            self.process_state_machine()
        finally:
            self.terminate = True
            for thread in threads:
                thread.join()
            self.safety_monitor.stop_monitoring()
            cv2.destroyAllWindows()

def main():
    # Initialize parameters
    robot_ip = "192.168.1.100"
    safety_distance = 0.5
    home_q_deg = np.array([2.43, -130.48, 95.77, 304.95, 269.33, 261.24])
    current_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(current_dir, 'images', 'reference.png')
    patch_coords_list = [
        (485, 345, 20, 15), (465, 365, 20, 15), (440, 395, 20, 15), (415, 420, 20, 15)
    ]

    # Initialize and run the manager
    manager = RobotProcessManager(robot_ip, safety_distance, home_q_deg, patch_coords_list, image_path)
    manager.run()

if __name__ == "__main__":
    main()
