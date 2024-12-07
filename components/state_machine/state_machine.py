import numpy as np
from websocket import create_connection
import requests
from typing import List

from socket_robot_controller.client import RobotSocketClient
from shared.interpolate import interpolate_tcp_poses
from shared.ilogging import CustomLogger

class StateMachine:
    def __init__(self, robot_controller):
        self.robot_controller = robot_controller
        self.logger = CustomLogger(log_dir="logs")
        self.small_state = 0
        self.state = 100 # Type 1000 for calibration
        self.terminate = False
        self.num_points_interp = 20
        self.robot_pose_state = 0 # 0 -> home, 1 -> fixtures, 2 -> place
        self.save_fixture_nr = []
        self.robot_speed = 50

        # self.velocity = {"low": 0.2, "medium": 0.6, "high": 1.4}
        self.velocity = {"low": 0.1, "medium": 0.3, "high": 0.3}
        self.acceleration = 0.1
        self.blend = {"non": 0.0, "large": 0.02}
        while True:
            try:
                self.fixture_socket = create_connection("ws://127.0.0.1:8000/fixtures")
                break
            except Exception as e:
                print(f"Failed to connect to fixture socket: {e}")
                input("Waiting for key..")

        self.pose_intermediate = np.array([-0.14073875492311985, -0.1347932873639663, 0.50, 0.669, 3.068, 0.00])
        self.pose_place = np.array([-0.5765337725404966, 0.24690845869221661, 0.28, 0.669, 3.068, 0.00])
        self.pose_fixture_1 = np.array([-0.11416495380452188, -0.6366095280680834, 0.25, 0.669, 3.068, 0.00]) # Above pick up 1. component
        self.pose_fixture_2 = np.array([-0.07957651394105475, -0.5775855654308832, 0.25, 0.669, 3.068, 0.00])  # Above pick up 2. component
        self.pose_fixture_3 = np.array([-0.04925448702503588, -0.5082985306025327, 0.25, 0.669, 3.068, 0.00])  # Above pick up 3. component
        self.pose_fixture_4 = np.array([-0.025557349301992764, -0.44688229341926045, 0.25, 0.669, 3.068, 0.00])  # Above pick up 4. component
        self.pose_fixture_5 = np.array([])
        self.pose_fixture_6 = np.array([])

        self.upper_offset = np.array([0.0, 0.0, 0.15, 0.0, 0.0, 0.0]) # Offset that is added to self.pose_fixture_n to have a point that is further up than self.pose_fixture_n for lifting
        self.lower_offset = np.array([0.0, 0.0, -0.1, 0.0, 0.0, 0.0]) # Offset that is added to self.pose_fixture_n to have a point that is lower than self.pose_fixture_n for grasping

        self.path_to_place = self.create_blended_path(self.pose_intermediate, self.pose_place, num_points=self.num_points_interp+10, fixed_end=True)
        self.path_back_to_intermediate = self.create_blended_path(self.pose_place, self.pose_intermediate, num_points=self.num_points_interp, fixed_end=True)

        self.path_lift_component_1 = self.create_blended_path(self.pose_fixture_1, self.pose_fixture_1 + self.upper_offset, num_points=self.num_points_interp, fixed_end=True) # Path from fixture base pose to upper pose to lift component
        self.path_lift_component_2 = self.create_blended_path(self.pose_fixture_2, self.pose_fixture_2 + self.upper_offset, num_points=self.num_points_interp, fixed_end=True)
        self.path_lift_component_3 = self.create_blended_path(self.pose_fixture_3, self.pose_fixture_3 + self.upper_offset, num_points=self.num_points_interp, fixed_end=True)
        self.path_lift_component_4 = self.create_blended_path(self.pose_fixture_4, self.pose_fixture_4 + self.upper_offset, num_points=self.num_points_interp, fixed_end=True)
        self.path_lift_component_5 = self.create_blended_path(self.pose_fixture_4, self.pose_fixture_4 + self.upper_offset, num_points=self.num_points_interp, fixed_end=True) # Needs to be adjusted for new components
        self.path_lift_component_6 = self.create_blended_path(self.pose_fixture_4, self.pose_fixture_4 + self.upper_offset, num_points=self.num_points_interp, fixed_end=True)

        self.intermediate_to_fixture_1 = self.create_blended_path(self.pose_intermediate, self.pose_fixture_1, num_points=self.num_points_interp, fixed_end=True)
        self.intermediate_to_fixture_2 = self.create_blended_path(self.pose_intermediate, self.pose_fixture_2, num_points=self.num_points_interp, fixed_end=True)
        self.intermediate_to_fixture_3 = self.create_blended_path(self.pose_intermediate, self.pose_fixture_3, num_points=self.num_points_interp, fixed_end=True)
        self.intermediate_to_fixture_4 = self.create_blended_path(self.pose_intermediate, self.pose_fixture_4, num_points=self.num_points_interp, fixed_end=True)
        self.intermediate_to_fixture_5 = self.create_blended_path(self.pose_intermediate, self.pose_fixture_4, num_points=self.num_points_interp, fixed_end=True) # Needs to be adjusted for new components
        self.intermediate_to_fixture_6 = self.create_blended_path(self.pose_intermediate, self.pose_fixture_4, num_points=self.num_points_interp, fixed_end=True)
        print("Done with init")

    def change_robot_velocity(self, safety_warning, fixture_results, distance):
        """Adjust robot velocity based on safety warnings and fixture detection."""
        if safety_warning:
            speed_fraction = 0.3 # * distance
        elif np.any(fixture_results == 1):
            speed_fraction = 1.0
        else:
            speed_fraction = 0.5
        self.robot_controller.set_robot_velocity(speed_fraction)
        self.logger.log("Speed",speed_fraction)


    def request_fixture_status(self) -> List[bool]:
        try:
            self.fixture_socket.send_text("")
            fixture_status = self.fixture_socket.recv()
            fixture_status = list(map(lambda x: int(x), fixture_status.split(",")))
            return fixture_status
        except Exception as e:
            print(f"Fixture socket failed with {e}")
            return [0,0,0,0]

    def get_stress_level(self):
        try:
            result = None
            response = requests.get("http://localhost:8000/stress_level")
            result = response.json()
            return result["stress_level"]
        except Exception as e:
            print(f"Failed to get stress level : {e}")
            return None

    def process_state_machine(self):
        """Process the state machine to control robot behavior."""
        # Handle state transitions
        fixture_results = self.request_fixture_status()
        #fixture_results = [0,0,0,0]
        
        result = self.get_stress_level()

        if result is not None:
            if result == "Low":
                self.robot_speed += 0.05
            elif result == "Medium":
                self.robot_speed -= 0.05
            elif result == "High":
                self.robot_speed -= 0.10

            if self.robot_speed < 0:
                self.robot_speed = 0
            if self.robot_speed > 1:
                self.robot_speed = 1

            self.robot_controller.set_robot_velocity(self.robot_speed) 

        print(f"Stress level: {result}")
        if self.state == 0:  # State for fixture 1
            print("State 1")
            self._handle_fixture_1()
            self.save_fixture_nr.append(1)

        elif self.state == 1:  # State for fixture 2
            print("State 2")
            self._handle_fixture_2()
            self.save_fixture_nr.append(2)

        elif self.state == 2:  # State for fixture 3
            print("State 3")
            self._handle_fixture_3()
            self.save_fixture_nr.append(3)

        elif self.state == 3:  # State for fixture 4
            print("State 4")
            self._handle_fixture_4()
            self.save_fixture_nr.append(4)

        elif self.state == 4:  # State for fixture 5
            print("State 5")
            self._handle_fixture_5()
            self.save_fixture_nr.append(5)

        elif self.state == 5:  # State for fixture 6
            print("State 6")
            self._handle_fixture_6()
            self.save_fixture_nr.append(6)

        elif self.state == 6:  # State for moving from fixtures to place position
            print("State 7")
            self._handle_movement_to_place()
            self.save_fixture_nr.append(7)

        else:  # Initial state or unknown state
            self._decide_next_state(fixture_results)
            self.save_fixture_nr.append(8)


        if self.state == 6:
            if self.small_state == 0:
                self.robot_pose_state = 1 # fixtures
            elif self.small_state == 1 or self.small_state == 4:
                self.robot_pose_state = 0 # home
            elif self.small_state >= 2 and self.small_state <= 3:
                self.robot_pose_state = 2 # place
        elif self.state < 6:
            self.robot_pose_state = 1 # fixtures
        else:
            self.robot_pose_state = 0 # home
        
        return self.robot_pose_state


    def _handle_fixtures(self, pose_fixture, path_intermediate_to_fixture, path_lift_component):
        """Handle logic for moving above the pick up position, moving to the pick up position, opening the gripper and moving back up."""
        
        print("curr: ", self.robot_controller.get_tcp_pose())
        print("planned: ", path_intermediate_to_fixture[-1])
        print("small state: ", self.small_state)

        if self.small_state == 0:  # Above pick up component
            self.robot_controller.open_gripper()
            print("Handling fixtures")
        
            self.robot_controller.moveL_path(path_intermediate_to_fixture)
            if(np.isclose(self.robot_controller.get_tcp_pose(), path_intermediate_to_fixture[-1][:6], atol=0.001).all()):
                self.small_state += 1

        elif self.small_state == 1:  # Pick up component
            self.robot_controller.open_gripper()

            self.robot_controller.moveL(pose_fixture + self.lower_offset, velocity=self.velocity["low"])
            if(np.isclose(self.robot_controller.get_tcp_pose(), pose_fixture + self.lower_offset, atol=0.001).all()):
                self.small_state += 1

        elif self.small_state == 2:  # Close gripper
            self.robot_controller.close_gripper()
            self.small_state += 1

        elif self.small_state == 3:  # Above pick up component when grasped
            self.robot_controller.moveL(pose_fixture, velocity=self.velocity["low"])
            if(np.isclose(self.robot_controller.get_tcp_pose(), pose_fixture, atol=0.001).all()):
                self.small_state += 1

        elif self.small_state == 4:  # Further above pick up when grasped
            self.robot_controller.moveL_path(path_lift_component)
            if(np.isclose(self.robot_controller.get_tcp_pose(), path_lift_component[-1][:6], atol=0.003).all()):
                self.small_state = 0
                self.state = 6  # Move to place position


    def _handle_fixture_1(self):
        """Handle logic for fixture 1."""
        # pose_1 = np.array([-0.11416495380452188, -0.6366095280680834, 0.20364282861631133, 0.669, 3.068, 0.00]) # Above pick up 1. component
        # pose_2 = np.array([-0.10927225089149672, -0.638808684706488, 0.16189487119823975, 0.669, 3.068, 0.00]) # Pick up 1. component
        # pose_3 = np.array([-0.11426353877896417, -0.6367850021118604, 0.37342196534573907, 0.669, 3.068, 0.00]) # Above pick up 1. component when grasped
        self._handle_fixtures(self.pose_fixture_1, self.intermediate_to_fixture_1, self.path_lift_component_1)                


    def _handle_fixture_2(self):
        """Handle logic for fixture 2."""
        # pose_1 = np.array([-0.07957651394105475, -0.5775855654308832, 0.2023741615008534, 0.669, 3.068, 0.00])  # Above pick up 2. component
        # pose_2 = np.array([-0.0794715050646689, -0.5763134771536808, 0.15689830700328303, ]) # Pick up 2. component
        # pose_3 = np.array([-0.07961487102277967, -0.5776175305046732, 0.36997942349606483, 0.669, 3.068, 0.00]) # Above pick up 2. component when grasped
        self._handle_fixtures(self.pose_fixture_2, self.intermediate_to_fixture_2, self.path_lift_component_2) 


    def _handle_fixture_3(self):
        """Handle logic for fixture 3."""
        # pose_1 = np.array([-0.04925448702503588, -0.5082985306025327, 0.1936708406298164, 0.669, 3.068, 0.00])  # Above pick up 3. component
        # pose_2 = np.array([-0.04922361412155398, -0.5082741917115655, 0.1574407674565033, 0.669, 3.068, 0.00]) # Pick up 3. component
        # pose_3 = np.array([-0.04933753474346547, -0.5083689053674434, 0.36860275233554163, 0.669, 3.068, 0.00]) # Above pick up 3. component when grasped
        self._handle_fixtures(self.pose_fixture_3, self.intermediate_to_fixture_3, self.path_lift_component_3) 


    def _handle_fixture_4(self):
        """Handle logic for fixture 4."""
        # pose_1 = np.array([-0.025557349301992764, -0.44688229341926045, 0.2003871289944606, 0.669, 3.068, 0.00])  # Above pick up 4. component
        # pose_2 = np.array([-0.024614733648472432, -0.44811676404310946, 0.15400051180951044, 0.669, 3.068, 0.00]) # Pick up 4. component
        # pose_3 = np.array([-0.025528569271143754, -0.44697782277537473, 0.368303731431036, 0.669, 3.068, 0.00]) # Above pick up 4. component when grasped
        self._handle_fixtures(self.pose_fixture_4, self.intermediate_to_fixture_4, self.path_lift_component_4) 


    def _handle_fixture_5(self):
        """Handle logic for fixture 5."""
        # pose_1 = np.array([])  # Above pick up 5. component
        # pose_2 = np.array([]) # Pick up 5. component
        # pose_3 = np.array([]) # Above pick up 5. component when grasped
        self._handle_fixtures(self.pose_fixture_5, self.intermediate_to_fixture_5, self.path_lift_component_5) 


    def _handle_fixture_6(self):
        """Handle logic for fixture 6."""
        # pose_1 = np.array([])  # Above pick up 6. component
        # pose_2 = np.array([]) # Pick up 6. component
        # pose_3 = np.array([]) # Above pick up 6. component when grasped
        self._handle_fixtures(self.pose_fixture_6, self.intermediate_to_fixture_6, self.path_lift_component_6) 


    def _decide_next_state(self, fixture_results):
        """Decide the next state based on fixture detection results."""
        if fixture_results[0]: 
            print("Moving to fixture 1")
            self.state = 0
        elif fixture_results[1]:
            print("Moving to fixture 2") 
            self.state = 1
        elif fixture_results[2]: 
            print("Moving to fixture 3")
            self.state = 2
        elif fixture_results[3]: 
            print("Moving to fixture 4")
            self.state = 3
        # elif fixture_results[4]: 
            # print("Moving to fixture 5")
            # self.state = 4
        # elif fixture_results[5]: 
            # print("Moving to fixture 6")
            # self.state = 5


    def _check_fixtures(self, fixture_results):
        """Check fixture detection results."""
        if fixture_results[0]: 
            print("Moving to fixture 1")
        elif fixture_results[1]:
            print("Moving to fixture 2") 
        elif fixture_results[2]: 
            print("Moving to fixture 3")
        elif fixture_results[3]: 
            print("Moving to fixture 4")
        # elif fixture_results[4]: 
            # print("Moving to fixture 5")
        # elif fixture_results[5]: 
            # print("Moving to fixture 6")


    def create_blended_path(self, start_pose, end_pose, num_points=20, fixed_end=False):
        """Creates a blended path with interpolation between start and end joint positions.

        Parameters:
            start_pose (tuple): Starting TCP pose (position, orientation).
            end_pose (tuple): Ending TCP pose (position, orientation).
            num_points (int): Number of points in the path (default is 20).
            fixed_end (bool): If True, apply a fixed blend for the last pose (default is False).

        Returns:
            list: A blended path with interpolated poses.
        """
        velocity = self.velocity["high"]
        acceleration = self.acceleration
        blend = self.blend["large"]

        # Interpolate TCP poses from start to end
        interpolated_points = interpolate_tcp_poses(start_pose, end_pose, num_points)

        # Create a blended path that includes TCP positions in radians along with velocity, acceleration, and blend radius
        blended_path = []
        
        for pose in interpolated_points:
            blended_path.append(pose + [velocity, acceleration, blend])  # Append velocity, acceleration, and blend

        # blended_path.append(end_pose.tolist() + [velocity, acceleration, blend])

        # Check if we need to adjust the last element
        if fixed_end:
            blended_path[-1][-1] = self.blend["non"]  # Update the blend value of the last point
            blended_path[-1][-3] = self.velocity["low"]  # Update the velocity value of the last point

        return blended_path
    
    
    def _handle_movement_to_place(self):
        """Handle logic for moving the grasped component to the place position above the box."""
        if self.small_state ==  0:
            # Create blended paths
            self.path_to_intermediate = self.create_blended_path(self.robot_controller.get_tcp_pose(), self.pose_intermediate, num_points=self.num_points_interp, fixed_end=True)
            self.small_state += 1
        elif self.small_state ==  1:
            # From actual to intermediate point
            self.robot_controller.moveL_path(self.path_to_intermediate)
            if(np.isclose(self.robot_controller.get_tcp_pose(), self.path_to_intermediate[-1][:6], atol=0.001).all()):
                self.small_state += 1  # Transition to next state
        elif self.small_state ==  2:
            # From intermediate to place point
            self.robot_controller.moveL_path(self.path_to_place)
            if(np.isclose(self.robot_controller.get_tcp_pose(), self.path_to_place[-1][:6], atol=0.001).all()):
                self.small_state += 1  # Transition to next state
        elif self.small_state ==  3:
            # Open gripper
            if self.robot_controller.open_gripper(): 
                self.small_state += 1
        elif self.small_state ==  4:
            self.robot_controller.moveL_path(self.path_back_to_intermediate)
            if(np.isclose(self.robot_controller.get_tcp_pose(), self.path_back_to_intermediate[-1][:6], atol=0.001).all()):
                # From place to intermediate point
                # Reset to initial state
                self.small_state = 0
                self.path_index = 0
                self.state = 100

if __name__ == "__main__":

    robot_controller = None
    try:
        robot_ip = "192.168.1.100"
        print("Starting robot controller")
        robot_controller = RobotSocketClient(robot_ip)
        print("Starting state machine")
        state_machine = StateMachine(robot_controller)

        while True:
            print("Processing")
            state_machine.process_state_machine()

    except Exception as e:
        print(f"{e}")
        if robot_controller is not None:
            robot_controller.rtde_c.disconnect()
            robot_controller.rtde_r.disconnect()
            robot_controller.rtde_io.disconnect()