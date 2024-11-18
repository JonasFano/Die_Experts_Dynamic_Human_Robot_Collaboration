import numpy as np
from utils.interpolate import interpolate_tcp_poses
from logging import Logger

class StateMachine:
    def __init__(self, robot_controller, fixture_checker):
        self.robot_controller = robot_controller
        self.fixture_checker = fixture_checker
        self.logger = Logger(log_dir="logs")
        self.small_state = 0
        self.state = 100 # Type 1000 for calibration
        self.terminate = False
        self.num_points_interp = 20
        self.robot_pose_state = 0 # 0 -> home, 1 -> fixtures, 2 -> place
        self.save_fixture_nr = []

        # self.velocity = {"low": 0.2, "medium": 0.6, "high": 1.4}
        self.velocity = {"low": 0.1, "medium": 0.3, "high": 0.3}
        self.acceleration = 0.1
        self.blend = {"non": 0.0, "large": 0.02}

        self.pose_intermediate = np.array([-0.14073875492311985, -0.1347932873639663, 0.50, -1.7173584058437448, 2.614817123624442, 0.015662793265223476])
        self.pose_place = np.array([-0.5765337725404966, 0.24690845869221661, 0.28, -1.7173584058437448, 2.614817123624442, 0.015662793265223476])
        self.pose_fixture_1 = np.array([-0.11416495380452188, -0.6366095280680834, 0.25, -1.7173584058437448, 2.614817123624442, 0.015662793265223476]) # Above pick up 1. component
        self.pose_fixture_2 = np.array([-0.07957651394105475, -0.5775855654308832, 0.25, -1.7060825343589325, 2.614852489706341, 0.022595902601295428])  # Above pick up 2. component
        self.pose_fixture_3 = np.array([-0.04925448702503588, -0.5082985306025327, 0.25, -1.7261076468170813, 2.623645026630323, 0.0023482443015084543])  # Above pick up 3. component
        self.pose_fixture_4 = np.array([-0.025557349301992764, -0.44688229341926045, 0.25, -1.7245031583352266, 2.6246444976427994, 0.002526657100955647])  # Above pick up 4. component
        self.pose_fixture_5 = np.array([])
        self.pose_fixture_6 = np.array([])

        self.upper_offset = np.array([0.0, 0.0, 0.15, 0.0, 0.0, 0.0]) # Offset that is added to self.pose_fixture_n to have a point that is further up than self.pose_fixture_n for lifting
<<<<<<< HEAD
        self.lower_offset = np.array([0.0, 0.0, -0.04, 0.0, 0.0, 0.0]) # Offset that is added to self.pose_fixture_n to have a point that is lower than self.pose_fixture_n for grasping
=======
        self.lower_offset = np.array([0.0, 0.0, -0.1, 0.0, 0.0, 0.0]) # Offset that is added to self.pose_fixture_n to have a point that is lower than self.pose_fixture_n for grasping
>>>>>>> threading

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


    def process_state_machine(self, fixture_results, current_depth_frame):
        """Process the state machine to control robot behavior."""
<<<<<<< HEAD
        while not self.terminate:
            # Monitor safety
            tcp_pose = self.robot_controller.get_tcp_pose()
            self.safety_monitor.set_robot_tcp(tcp_pose)
            safety_warning, distance, current_frame, current_depth_frame, self.terminate = self.safety_monitor.monitor_safety(self.fixture_checker.patch_coords_list)
            self.logger.log("Distance",distance)
            # Check fixtures
            fixture_results = self.fixture_checker.check_all_patches(current_frame, current_depth_frame)
            self.logger.log("Fixture_result",fixture_results)
            # Determine velocity
            self.change_robot_velocity(safety_warning, fixture_results, distance)
=======
        # Handle state transitions
        match self.state:
            case 0:  # State for fixture 1
                print("State 1")
                self._handle_fixture_1()
                self.save_fixture_nr.append(1)

            case 1:  # State for fixture 2
                print("State 2")
                self._handle_fixture_2()
                self.save_fixture_nr.append(2)

            case 2:  # State for fixture 3
                print("State 3")
                self._handle_fixture_3()
                self.save_fixture_nr.append(3)
            
            case 3:  # State for fixture 4
                print("State 4")
                self._handle_fixture_4()
                self.save_fixture_nr.append(4)
>>>>>>> threading

            case 4:  # State for fixture 5
                print("State 5")
                self._handle_fixture_5()
                self.save_fixture_nr.append(5)

            case 5:  # State for fixture 6
                print("State 6")
                self._handle_fixture_6()
                self.save_fixture_nr.append(6)

            case 6:  # State for moving from fixtures to place position
                print("State 7")
                self._handle_movement_to_place()
                self.save_fixture_nr.append(7)

            case 1000: # Camera calibration state for checking fixture detection
                self._check_fixtures(fixture_results)
                self.fixture_checker.calibrate_depth(current_depth_frame)

            case _:  # Initial state
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
        match self.small_state:
            case 0: # Above pick up component
                self.robot_controller.open_gripper()

                print("Handling fixtures")

                if self.robot_controller.moveL_path(path_intermediate_to_fixture):
                    self.small_state += 1
            case 1: # Pick up component
                self.robot_controller.open_gripper()

                print("Handling fixtures 2")

                if self.robot_controller.moveL(pose_fixture + self.lower_offset, velocity=self.velocity["low"]):
                    self.small_state += 1
            case 2: # Close gripper
                if self.robot_controller.close_gripper():
                    self.small_state += 1
            case 3: # Above pick up component when grasped
                if self.robot_controller.moveL(pose_fixture, velocity=self.velocity["low"]):
                    self.small_state += 1
            case 4: # Further above pick up when grasped
                if self.robot_controller.moveL_path(path_lift_component):
                    self.small_state = 0
                    self.state = 6 # Move to place position


    def _handle_fixture_1(self):
        """Handle logic for fixture 1."""
        # pose_1 = np.array([-0.11416495380452188, -0.6366095280680834, 0.20364282861631133, -1.7173584058437448, 2.614817123624442, 0.015662793265223476]) # Above pick up 1. component
        # pose_2 = np.array([-0.10927225089149672, -0.638808684706488, 0.16189487119823975, -1.7171870780646261, 2.614478233276138, 0.015947482150488666]) # Pick up 1. component
        # pose_3 = np.array([-0.11426353877896417, -0.6367850021118604, 0.37342196534573907, -1.7172805001473428, 2.614861661856344, 0.01562220979246864]) # Above pick up 1. component when grasped
        self._handle_fixtures(self.pose_fixture_1, self.intermediate_to_fixture_1, self.path_lift_component_1)                


    def _handle_fixture_2(self):
        """Handle logic for fixture 2."""
        # pose_1 = np.array([-0.07957651394105475, -0.5775855654308832, 0.2023741615008534, -1.7060825343589325, 2.614852489706341, 0.022595902601295428])  # Above pick up 2. component
        # pose_2 = np.array([-0.0794715050646689, -0.5763134771536808, 0.15689830700328303, -1.7062760747070256, 2.614848580062184, 0.02276340968191546]) # Pick up 2. component
        # pose_3 = np.array([-0.07961487102277967, -0.5776175305046732, 0.36997942349606483, -1.7059307001537876, 2.614718091511983, 0.022713872557162004]) # Above pick up 2. component when grasped
        self._handle_fixtures(self.pose_fixture_2, self.intermediate_to_fixture_2, self.path_lift_component_2) 


    def _handle_fixture_3(self):
        """Handle logic for fixture 3."""
        # pose_1 = np.array([-0.04925448702503588, -0.5082985306025327, 0.1936708406298164, -1.7261076468170813, 2.623645026630323, 0.0023482443015084543])  # Above pick up 3. component
        # pose_2 = np.array([-0.04922361412155398, -0.5082741917115655, 0.1574407674565033, -1.7265598120065448, 2.623701513754936, 0.0022291121420809964]) # Pick up 3. component
        # pose_3 = np.array([-0.04933753474346547, -0.5083689053674434, 0.36860275233554163, -1.7258038337871062, 2.623673826634714, 0.0024556181851659044]) # Above pick up 3. component when grasped
        self._handle_fixtures(self.pose_fixture_3, self.intermediate_to_fixture_3, self.path_lift_component_3) 


    def _handle_fixture_4(self):
        """Handle logic for fixture 4."""
        # pose_1 = np.array([-0.025557349301992764, -0.44688229341926045, 0.2003871289944606, -1.7245031583352266, 2.6246444976427994, 0.002526657100955647])  # Above pick up 4. component
        # pose_2 = np.array([-0.024614733648472432, -0.44811676404310946, 0.15400051180951044, -1.7248856208975198, 2.6250816985232532, 0.0021132655857843247]) # Pick up 4. component
        # pose_3 = np.array([-0.025528569271143754, -0.44697782277537473, 0.368303731431036, -1.7246152624556719, 2.6244098807794094, 0.0025722110232124845]) # Above pick up 4. component when grasped
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
        match self.small_state:
            case 0:
                # Create blended paths
                self.path_to_intermediate = self.create_blended_path(self.robot_controller.get_tcp_pose(), self.pose_intermediate, num_points=self.num_points_interp, fixed_end=True)
                self.small_state += 1
            case 1:
                # From actual to intermediate point
                if self.robot_controller.moveL_path(self.path_to_intermediate):
                    self.small_state += 1  # Transition to next state
            case 2:
                # From intermediate to place point
                if self.robot_controller.moveL_path(self.path_to_place):
                    self.small_state += 1  # Transition to next state
            case 3:
                # Open gripper
                if self.robot_controller.open_gripper(): 
                    self.small_state += 1
            case 4:
                # From place to intermediate point
                if self.robot_controller.moveL_path(self.path_back_to_intermediate):
                    # Reset to initial state
                    self.small_state = 0
                    self.path_index = 0
                    self.state = 100