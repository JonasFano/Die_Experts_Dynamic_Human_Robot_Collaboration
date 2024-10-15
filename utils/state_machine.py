import numpy as np
from utils.interpolate import interpolate_joint_positions

class StateMachine:
    def __init__(self, robot_controller, safety_monitor, fixture_checker):
        self.robot_controller = robot_controller
        self.safety_monitor = safety_monitor
        self.fixture_checker = fixture_checker
        self.small_state = 0
        self.state = 100
        self.terminate = False

    def change_robot_velocity(self, safety_warning, fixture_results, distance):
        """Adjust robot velocity based on safety warnings and fixture detection."""
        if safety_warning:
            return 0.3 * distance
        elif np.any(fixture_results == 1):
            return 1.0
        return 0.5

    def process_state_machine(self):
        """Process the state machine to control robot behavior."""
        while not self.terminate:
            # Monitor safety
            tcp_pose = self.robot_controller.get_tcp_pose()
            self.safety_monitor.set_robot_tcp(tcp_pose)
            safety_warning, distance, current_frame, current_depth_frame, self.terminate = self.safety_monitor.monitor_safety(self.fixture_checker.patch_coords_list)

            # Check fixtures
            fixture_results = self.fixture_checker.check_all_patches(current_frame, current_depth_frame)

            # Determine velocity
            robot_velocity = self.change_robot_velocity(safety_warning, fixture_results, distance)

            # Handle state transitions
            match self.state:
                case 0:  # State for fixture 1
                    print("State 1")
                    self._handle_fixture_1(robot_velocity)

                case 1:  # State for fixture 2
                    print("State 2")
                    self._handle_fixture_2(robot_velocity)

                case 2:  # State for fixture 3
                    print("State 3")
                    self._handle_fixture_3(robot_velocity)
                
                case 3:  # State for fixture 4
                    print("State 4")
                    self._handle_fixture_4(robot_velocity)

                case 4:  # State for fixture 5
                    print("State 5")
                    self._handle_fixture_5(robot_velocity)

                case 5:  # State for fixture 6
                    print("State 6")
                    self._handle_fixture_6(robot_velocity)

                case 6:  # State for moving from fixtures to place position
                    print("State 7")
                    self._handle_movement_to_place(robot_velocity)

                case 1000: # Camera calibration state for checking fixture detection
                    self._check_fixtures(fixture_results)
                    self.fixture_checker.calibrate_depth(current_depth_frame)

                case _:  # Initial state
                    # print("State default")
                    self._decide_next_state(fixture_results)
                


    def _handle_fixtures(self, robot_velocity, joint_pos_1, joint_pos_2, joint_pos_3):
        """Handle logic for moving above the pick up position, moving to the pick up position, opening the gripper and moving back up."""
        match self.small_state:
            case 0: # Above pick up component
                self.robot_controller.open_gripper()

                if self.robot_controller.move_to_position(joint_pos_1, robot_velocity):
                    self.small_state += 1
            case 1: # Pick up component
                self.robot_controller.open_gripper()

                if self.robot_controller.move_to_position(joint_pos_2, robot_velocity):
                    self.small_state += 1
            case 2: # Close gripper
                if self.robot_controller.close_gripper():
                    self.small_state += 1
            case 3: # Above pick up component when grasped
                if self.robot_controller.move_to_position(joint_pos_3, robot_velocity):
                    self.small_state = 0
                    self.state = 6 # Move to place position


    def _handle_fixture_1(self, robot_velocity):
        """Handle logic for fixture 1."""
        joint_pos_1 = np.array([68.05, -66.47, 87.16, 250.25, 270.29, 271.17]) # Above pick up 1. component
        joint_pos_2 = np.array([68.53, -64.05, 90.21, 244.84, 270.31, 271.68]) # Pick up 1. component
        joint_pos_3 = np.array([68.05, -70.09, 66.97, 274.06, 270.22, 271.07]) # Above pick up 1. component when grasped
        self._handle_fixtures(robot_velocity, joint_pos_1, joint_pos_2, joint_pos_3)                

    def _handle_fixture_2(self, robot_velocity):
        """Handle logic for fixture 2."""
        joint_pos_1 = np.array([69.07, -74.42, 98.29, 247.50, 270.32, 272.54])  # Above pick up 2. component
        joint_pos_2 = np.array([69.03, -71.71, 102.11, 240.99, 270.32, 272.53]) # Pick up 2. component
        joint_pos_3 = np.array([69.07, -79.10, 78.95, 271.52, 270.26, 272.43]) # Above pick up 2. component when grasped
        self._handle_fixtures(robot_velocity, joint_pos_1, joint_pos_2, joint_pos_3) 

    def _handle_fixture_3(self, robot_velocity):
        """Handle logic for fixture 3."""
        joint_pos_1 = np.array([69.50, -83.71, 111.47, 242.33, 270.32, 272.55])  # Above pick up 3. component
        joint_pos_2 = np.array([69.50, -80.99, 114.47, 236.61, 270.32, 272.57]) # Pick up 3. component
        joint_pos_3 = np.array([69.50, -89.82, 91.32, 268.59, 270.26, 272.43]) # Above pick up 3. component when grasped
        self._handle_fixtures(robot_velocity, joint_pos_1, joint_pos_2, joint_pos_3) 

    def _handle_fixture_4(self, robot_velocity):
        """Handle logic for fixture 4."""
        joint_pos_1 = np.array([69.61, -92.89, 119.87, 243.11, 270.32, 272.71])  # Above pick up 4. component
        joint_pos_2 = np.array([69.78, -88.92, 123.92, 235.09, 270.32, 272.93]) # Pick up 4. component
        joint_pos_3 = np.array([69.62, -98.70, 99.53, 269.27, 270.26, 272.59]) # Above pick up 4. component when grasped
        self._handle_fixtures(robot_velocity, joint_pos_1, joint_pos_2, joint_pos_3) 

    def _handle_fixture_5(self, robot_velocity):
        """Handle logic for fixture 5."""
        joint_pos_1 = np.array([])  # Above pick up 5. component
        joint_pos_2 = np.array([]) # Pick up 5. component
        joint_pos_3 = np.array([]) # Above pick up 5. component when grasped
        self._handle_fixtures(robot_velocity, joint_pos_1, joint_pos_2, joint_pos_3) 

    def _handle_fixture_6(self, robot_velocity):
        """Handle logic for fixture 6."""
        joint_pos_1 = np.array([])  # Above pick up 6. component
        joint_pos_2 = np.array([]) # Pick up 6. component
        joint_pos_3 = np.array([]) # Above pick up 6. component when grasped
        self._handle_fixtures(robot_velocity, joint_pos_1, joint_pos_2, joint_pos_3) 

    def _handle_movement_to_place(self, robot_velocity):
        """Handle logic for moving the grasped component to the place position above the box."""
        match self.small_state:
            case 0:
                # Interpolate
                self.joint_pos_intermediate = np.array([2.43, -130.48, 95.77, 304.95, 269.33, 261.24])
                self.joint_pos_place = np.array([-35.01, -73.70, 84.80, 256.20, 269.29, 261.24])

                self.from_actual_to_intermediate = interpolate_joint_positions(self.robot_controller.get_actual_joint_positions(), self.joint_pos_intermediate, num_points=10)
                self.from_intermediate_to_place = interpolate_joint_positions(self.joint_pos_intermediate, self.joint_pos_place, num_points=10)
                self.from_place_to_intermediate = interpolate_joint_positions(self.joint_pos_place, self.joint_pos_intermediate, num_points=10)

                self.intermediate_index = 0  # Initialize the index for interpolating joint positions
                self.small_state += 1
            case 1:
                # From actual to intermediate point
                # if self.intermediate_index < len(self.from_actual_to_intermediate):
                #     joint_pos = self.from_actual_to_intermediate[self.intermediate_index]
                    
                #     if self.robot_controller.move_to_position(joint_pos, robot_velocity):
                #         self.intermediate_index += 1  # Move to the next joint position
                # else:
                #     self.small_state += 1  # Move to the next state once all intermediate points are reached
                #     self.intermediate_index = 0

                if self.robot_controller.move_to_position(self.joint_pos_intermediate, robot_velocity):
                    self.small_state += 1
            case 2:
                # From intermediate to place point
                # if self.intermediate_index < len(self.from_intermediate_to_place):
                #     joint_pos = self.from_intermediate_to_place[self.intermediate_index]
                    
                #     if self.robot_controller.move_to_position(joint_pos, robot_velocity):
                #         self.intermediate_index += 1  # Move to the next joint position
                # else:
                #     self.small_state += 1  # Move to the next state once all intermediate points are reached
                #     self.intermediate_index = 0

                if self.robot_controller.move_to_position(self.joint_pos_place, robot_velocity):
                    self.small_state += 1
            case 3:
                # Open gripper
                if self.robot_controller.open_gripper(): 
                    self.small_state += 1
            case 4:
                # From place to intermediate point
                # if self.intermediate_index < len(self.from_place_to_intermediate):
                #     joint_pos = self.from_place_to_intermediate[self.intermediate_index]
                    
                #     if self.robot_controller.move_to_position(joint_pos, robot_velocity):
                #         self.intermediate_index += 1  # Move to the next joint position
                # else:
                #     self.small_state = 0 # Move to the next state once all intermediate points are reached
                #     self.intermediate_index = 0
                #     self.state = 100

                if self.robot_controller.move_to_position(self.joint_pos_intermediate, robot_velocity):
                    self.small_state = 0
                    self.state = 100

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