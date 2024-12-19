import numpy as np
from websocket import create_connection
import requests
from typing import List

from socket_robot_controller.client import RobotSocketClient
from shared.interpolate import interpolate_tcp_poses
from shared.ilogging import CustomLogger
import time
import math

class StateMachine:
    def __init__(self, robot_controller):
        self.robot_controller = robot_controller
        self.logger = CustomLogger(log_dir="logs")
        self.small_state = 0
        self.state = 100 # Type 1000 for calibration
        self.terminate = False
        self.num_points_interp = 50
        self.robot_pose_state = 0 # 0 -> home, 1 -> fixtures, 2 -> place
        self.save_fixture_nr = []
        self.speed_scaler = 1
        self.base_speed = 1
        self.hertz = 20
        self.sleep_adjust_count_max = 10*self.hertz
        self.sleep_adjust_count = 0

        self.velocity = {"low": 0.1, "medium": 0.3, "high": 0.3}
        self.velocity = {"low": 0.4, "medium": 0.8, "high": 1.4}
        self.acceleration = 2
        self.blend = {"non": 0.0, "low": 0.007, "large": 0.025}
        self.multiplier = 1.1
        self.tolerance = 0.004
        while True:
            try:
                self.fixture_socket = create_connection("ws://127.0.0.1:8000/fixtures")
                break
            except Exception as e:
                print(f"Failed to connect to fixture socket: {e}")
                input("Waiting for key..")
    
        self.pose_intermediate = np.array([-0.14073875492311985, -0.1347932873639663, 0.50, 3.06, -0.6, -0.0175]) # Homej
        self.pose_place = np.array([-0.5765337725404966, 0.24690845869221661, 0.28, 3.06, -0.6, -0.0175]) 
        self.pose_fixture_1 = np.array([-0.11416495380452188, -0.6366095280680834, 0.25, 3.06, -0.6, -0.0175]) # Above pick up 1. component
        self.pose_fixture_2 = np.array([-0.07957651394105475, -0.5775855654308832, 0.25, 3.06, -0.6, -0.0175])  # Above pick up 2. component
        self.pose_fixture_3 = np.array([-0.04925448702503588, -0.5082985306025327, 0.25, 3.06, -0.6, -0.0175])  # Above pick up 3. component
        self.pose_fixture_4 = np.array([-0.025557349301992764, -0.44688229341926045, 0.25, 3.06, -0.6, -0.0175])  # Above pick up 4. component
        self.pose_fixture_5 = np.array([0.044883889943587316, -0.3961740540470739, 0.18, 3.06, -0.6, -0.0175])
        self.pose_fixture_6 = np.array([0.07650894191968563, -0.3309545133625595, 0.18, 3.06, -0.6, -0.0175])

        self.upper_offset = np.array([0.0, 0.0, 0.205, 0.0, 0.0, 0.0]) # Offset that is added to self.pose_fixture_n to have a point that is further up than self.pose_fixture_n for lifting
        self.lower_offset = np.array([0.0, 0.0, -0.1, 0.0, 0.0, 0.0]) # Offset that is added to self.pose_fixture_n to have a point that is lower than self.pose_fixture_n for grasping

        self.path_to_place = self.create_blended_path(self.pose_intermediate, self.pose_place, num_points=self.num_points_interp+10, fixed_end=True)
        self.path_back_to_intermediate = self.create_blended_path(self.pose_place, self.pose_intermediate, num_points=self.num_points_interp, fixed_end=True)
        
        self.num_points_interp_lifiting = 20

        self.path_lift_component_1 = self.create_blended_path(self.pose_fixture_1, self.pose_fixture_1 + self.upper_offset, num_points=self.num_points_interp_lifiting, fixed_end=True) # Path from fixture base pose to upper pose to lift component
        self.path_lift_component_2 = self.create_blended_path(self.pose_fixture_2, self.pose_fixture_2 + self.upper_offset, num_points=self.num_points_interp_lifiting, fixed_end=True)
        self.path_lift_component_3 = self.create_blended_path(self.pose_fixture_3, self.pose_fixture_3 + self.upper_offset, num_points=self.num_points_interp_lifiting, fixed_end=True)
        self.path_lift_component_4 = self.create_blended_path(self.pose_fixture_4, self.pose_fixture_4 + self.upper_offset, num_points=self.num_points_interp_lifiting, fixed_end=True)
        self.path_lift_component_5 = self.create_blended_path(self.pose_fixture_5, self.pose_fixture_5 + self.upper_offset, num_points=self.num_points_interp_lifiting, fixed_end=True) # Needs to be adjusted for new components
        self.path_lift_component_6 = self.create_blended_path(self.pose_fixture_6, self.pose_fixture_6 + self.upper_offset, num_points=self.num_points_interp_lifiting, fixed_end=True)

        self.intermediate_to_fixture_1 = self.create_blended_path(self.pose_intermediate, self.pose_fixture_1, num_points=self.num_points_interp, fixed_end=True)
        self.intermediate_to_fixture_2 = self.create_blended_path(self.pose_intermediate, self.pose_fixture_2, num_points=self.num_points_interp, fixed_end=True)
        self.intermediate_to_fixture_3 = self.create_blended_path(self.pose_intermediate, self.pose_fixture_3, num_points=self.num_points_interp, fixed_end=True)
        self.intermediate_to_fixture_4 = self.create_blended_path(self.pose_intermediate, self.pose_fixture_4, num_points=self.num_points_interp, fixed_end=True)
        self.intermediate_to_fixture_5 = self.create_blended_path(self.pose_intermediate, self.pose_fixture_5, num_points=self.num_points_interp, fixed_end=True) # Needs to be adjusted for new components
        self.intermediate_to_fixture_6 = self.create_blended_path(self.pose_intermediate, self.pose_fixture_6, num_points=self.num_points_interp, fixed_end=True)
        print("Done with init")


    def request_fixture_status(self) -> List[bool]:
        retries = 3
        while retries != 0:
            try:
                self.fixture_socket.send_text("")
                fixture_status = self.fixture_socket.recv()
                fixture_status = list(map(lambda x: int(x), fixture_status.split(",")))
                return fixture_status
            except BrokenPipeError as e:
                retries -= 1
                print(f"Fixtures failed with {e}. Trying {retries} more times.")
            except Exception as e:
                self.fixture_socket = create_connection("http://localhost:8000/fixture")
                raise Exception("Fixture socket failed with {e}")

    def get_stress_level(self):
        try:
            result = None
            response = requests.get("http://localhost:8000/data")
            result = response.json()
            return (result["distance"], result["stress_status"])
        except Exception as e:
            res_text = response.text
            print(f"Failed to get stress level : {e}")
            print(f"Res text for {res_text}")
            return (None, None)


    def _apply_calculate_speed_from_stress(self, stress: str):
        """Apply speed from stress to the robot speed value"""
        if stress == "Low":
            self.speed_scaler += 0.05
        elif stress == "Medium":
            self.speed_scaler -= 0.05
        elif stress == "High":
            self.speed_scaler -= 0.10

        if self.speed_scaler < 0.20:
            self.speed_scaler = 0.20
        if self.speed_scaler > 1:
            self.speed_scaler = 1

    def _apply_base_speed_based_on_distance(self, distance_to_human):
        # Based on paper from the lego guy
        if distance_to_human < 0.2:
            self.base_speed = 0
        elif distance_to_human < 0.5:
            # Scale speed scale distance 0.2-0.5 to a 0-100 scale
            self.base_speed = (distance_to_human - 0.2) / (0.5-0.2)
        else:
            self.base_speed = 1

    def calculate_robot_speed(self, distance_to_human: float, stress_level: str):
       
        self._apply_base_speed_based_on_distance(distance_to_human)
        #self._apply_calculate_speed_from_stress(stress_level)

        return round(self.speed_scaler*self.base_speed, 2)


    def process_state_machine(self):
        """Process the state machine to control robot behavior."""
        # Handle state transitions

        print(f"Current state: {self.state}")
        try:
            self.fixture_socket.ping() # Keep connection alive
        except BrokenPipeError:
            print("Ping failed")

        speed = round(self.base_speed*self.speed_scaler, 2)

        (distance, stress_level) = self.get_stress_level()
        if stress_level is not None and distance is not None:        
            speed = self.calculate_robot_speed(distance, stress_level)
        self.robot_controller.set_robot_velocity(speed) 
        #print(f"Speed scaling is {speed:0.02f}")
        if self.robot_controller.is_running():
            return

        # async_running = self.robot_controller.is_running()
        # print(async_running)
        # # If the robot is currently executing an async action
        # if async_running:
        #     print(f"Progress {self.robot_controller.get_async_progress()}")
        #     return # Return early since we are not done with performing an action


        #print(f"Stress level: {result}")
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
            try:
                fixture_results = self.request_fixture_status()
                self._decide_next_state(fixture_results)
                self.save_fixture_nr.append(8)
            except Exception as e:
                print("Failed to get fixtures with retires. Error : {e}")


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
        
        if self.robot_controller.is_running():
            
            return

        print("curr: ", self.robot_controller.get_tcp_pose())
        print("small state: ", self.small_state)

        if self.small_state == 0:  # Above pick up component
            self.robot_controller.open_gripper()
        
            self.robot_controller.moveL_path(path_intermediate_to_fixture)
            
            # if (np.isclose(self.robot_controller.get_tcp_pose(), path_intermediate_to_fixture[-1][:6], atol=self.tolerance).all()):
            # # if not self.robot_controller.is_running():
            self.small_state += 1

        elif self.small_state == 1:  # Pick up component
            self.robot_controller.open_gripper()

            self.robot_controller.moveL(pose_fixture + self.lower_offset, velocity=self.velocity["low"])
            # if(np.isclose(self.robot_controller.get_tcp_pose(), pose_fixture + self.lower_offset, atol=self.tolerance).all()):
            # # if not self.robot_controller.is_running():
            self.small_state += 1

        elif self.small_state == 2:  # Close gripper
            self.robot_controller.close_gripper()
            self.small_state += 1

        elif self.small_state == 3:  # Above pick up component when grasped
            self.robot_controller.moveL(pose_fixture, velocity=self.velocity["low"])
            # if(np.isclose(self.robot_controller.get_tcp_pose(), pose_fixture, atol=self.tolerance).all()):
            # # if not self.robot_controller.is_running():
            self.small_state += 1

        elif self.small_state == 4:  # Further above pick up when grasped
            self.robot_controller.moveL_path(path_lift_component)
            print("planned: ", path_lift_component[-1][:6])
            # if(np.isclose(self.robot_controller.get_tcp_pose(), path_lift_component[-1][:6], atol=self.tolerance).all()):
            # # if not self.robot_controller.is_running():
            self.small_state = 0
            self.state = 6  # Move to place position


    def _handle_fixture_1(self):
        """Handle logic for fixture 1."""
        # pose_1 = np.array([-0.11416495380452188, -0.6366095280680834, 0.20364282861631133, 3.06, -0.6, -0.0175]) # Above pick up 1. component
        # pose_2 = np.array([-0.10927225089149672, -0.638808684706488, 0.16189487119823975, 3.06, -0.6, -0.0175]) # Pick up 1. component
        # pose_3 = np.array([-0.11426353877896417, -0.6367850021118604, 0.37342196534573907, 3.06, -0.6, -0.0175]) # Above pick up 1. component when grasped
        self._handle_fixtures(self.pose_fixture_1, self.intermediate_to_fixture_1, self.path_lift_component_1)                


    def _handle_fixture_2(self):
        """Handle logic for fixture 2."""
        # pose_1 = np.array([-0.07957651394105475, -0.5775855654308832, 0.2023741615008534, 3.06, -0.6, -0.0175])  # Above pick up 2. component
        # pose_2 = np.array([-0.0794715050646689, -0.5763134771536808, 0.15689830700328303, ]) # Pick up 2. component
        # pose_3 = np.array([-0.07961487102277967, -0.5776175305046732, 0.36997942349606483, 3.06, -0.6, -0.0175]) # Above pick up 2. component when grasped
        self._handle_fixtures(self.pose_fixture_2, self.intermediate_to_fixture_2, self.path_lift_component_2) 


    def _handle_fixture_3(self):
        """Handle logic for fixture 3."""
        # pose_1 = np.array([-0.04925448702503588, -0.5082985306025327, 0.1936708406298164, 3.06, -0.6, -0.0175])  # Above pick up 3. component
        # pose_2 = np.array([-0.04922361412155398, -0.5082741917115655, 0.1574407674565033, 3.06, -0.6, -0.0175]) # Pick up 3. component
        # pose_3 = np.array([-0.04933753474346547, -0.5083689053674434, 0.36860275233554163, 3.06, -0.6, -0.0175]) # Above pick up 3. component when grasped
        self._handle_fixtures(self.pose_fixture_3, self.intermediate_to_fixture_3, self.path_lift_component_3) 


    def _handle_fixture_4(self):
        """Handle logic for fixture 4."""
        # pose_1 = np.array([-0.025557349301992764, -0.44688229341926045, 0.2003871289944606, 3.06, -0.6, -0.0175])  # Above pick up 4. component
        # pose_2 = np.array([-0.024614733648472432, -0.44811676404310946, 0.15400051180951044, 3.06, -0.6, -0.0175]) # Pick up 4. component
        # pose_3 = np.array([-0.025528569271143754, -0.44697782277537473, 0.368303731431036, 3.06, -0.6, -0.0175]) # Above pick up 4. component when grasped
        self._handle_fixtures(self.pose_fixture_4, self.intermediate_to_fixture_4, self.path_lift_component_4) 


    def _handle_fixture_5(self):
        """Handle logic for fixture 5."""
        self._handle_fixtures(self.pose_fixture_5, self.intermediate_to_fixture_5, self.path_lift_component_5) 


    def _handle_fixture_6(self):
        """Handle logic for fixture 6."""
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
        elif fixture_results[4]: 
            print("Moving to fixture 5")
            self.state = 4
        elif fixture_results[5]: 
            print("Moving to fixture 6")
            self.state = 5


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
        elif fixture_results[4]: 
            print("Moving to fixture 5")
        elif fixture_results[5]: 
            print("Moving to fixture 6")


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
        num_points = self.calculate_n_points(start_pose, end_pose, self.multiplier)
        interpolated_points = interpolate_tcp_poses(start_pose, end_pose, num_points)

        # Create a blended path that includes TCP positions in radians along with velocity, acceleration, and blend radius
        blended_path = []
        
        for pose in interpolated_points:
            blended_path.append(pose + [velocity, acceleration, blend])  # Append velocity, acceleration, and blend

        # blended_path.append(end_pose.tolist() + [velocity, acceleration, blend])


        # Check if we need to adjust the last element
        # if fixed_end:
        #     blended_path[-1][-1] = self.blend["non"]  # Update the blend value of the last point
        #     blended_path[-1][-3] = self.velocity["low"]  # Update the velocity value of the last point
        #     blended_path[-2][-3] = self.velocity["medium"]  # Update the velocity value of the last point
        #     blended_path[-3][-3] = self.velocity["medium"]  # Update the velocity value of the last point
        gradient_n_points = min(num_points, 4)

        speed_values = self.speed_gradient(self.velocity["low"], self.velocity["medium"], gradient_n_points)
        for index,val in enumerate(speed_values):
            blended_path[((index+1)*-1)][-3] = val
        
        blended_path[-1][-1] = self.blend["non"]  # Update the blend value of the last point

        return blended_path
    
    def speed_gradient(self, low_val, high_val, n):
        """calculate a gradient n speed values between low_val and high_val"""
        d_speed = (high_val-low_val)/n
        return [low_val+((i+1)*d_speed) for i in range(n)]

    def calculate_n_points(self, point_a, point_b, multiplier=4):
        distance = math.dist(point_a[:3], point_b[:3])

        if distance > 0.25:
            blend_dist = self.blend["large"] * multiplier
        else:
            blend_dist = self.blend["low"] * multiplier
        return int(distance / blend_dist)
    
    def _handle_movement_to_place(self):
        """Handle logic for moving the grasped component to the place position above the box."""
        if self.small_state == 0:
            # Create blended paths
            self.path_to_intermediate = self.create_blended_path(self.robot_controller.get_tcp_pose(), self.pose_intermediate, num_points=self.num_points_interp, fixed_end=True)
            self.small_state += 1

        elif self.small_state == 1:
            # From actual to intermediate point
            self.robot_controller.moveL_path(self.path_to_intermediate)
            # if(np.isclose(self.robot_controller.get_tcp_pose(), self.path_to_intermediate[-1][:6], atol=self.tolerance).all()):
            # if not self.robot_controller.is_running():
            self.small_state += 1  # Transition to next state

        elif self.small_state == 2:
            # From intermediate to place point
            self.robot_controller.moveL_path(self.path_to_place)
            # if(np.isclose(self.robot_controller.get_tcp_pose(), self.path_to_place[-1][:6], atol=self.tolerance).all()):
            # if not self.robot_controller.is_running():
            self.small_state += 1  # Transition to next state

        elif self.small_state == 3:
            # Open gripper
            self.robot_controller.open_gripper()
            self.small_state += 1

        elif self.small_state == 4:
            # From place to intermediate point
            self.robot_controller.moveL_path(self.path_back_to_intermediate)
            # if(np.isclose(self.robot_controller.get_tcp_pose(), self.path_back_to_intermediate[-1][:6], atol=self.tolerance).all()):
            # if not self.robot_controller.is_running():
                # Reset to initial state
            self.small_state = 0
            self.path_index = 0
            self.state = 100

if __name__ == "__main__":

    try:
        print("Starting robot controller")
        robot_controller = RobotSocketClient()
        print("Starting state machine")
        state_machine = StateMachine(robot_controller)

        while True:
            state_machine.process_state_machine()
    except KeyboardInterrupt:
        robot_controller.stop()