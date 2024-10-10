import rtde_control
import rtde_receive
import rtde_io
from Robot_Safety_Monitor import RobotSafetyMonitor
import cv2
import numpy as np
import math
import os

from detect_object_in_fixture import CheckFixtures
from interpolate import interpolate_joint_positions



rtde_c = rtde_control.RTDEControlInterface("192.168.1.100")
rtde_r = rtde_receive.RTDEReceiveInterface("192.168.1.100")
rtde_input_output = rtde_io.RTDEIOInterface("192.168.1.100")

# Get the current script's directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the full path to the image
image_path = os.path.join(current_dir, 'images', 'reference2.png')

# Read the image in grayscale
reference_image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

# Define the patch coordinates (x, y, width, height) ------- x is horizontal and x,y are the top left pixel of the image patch
patch_coords_1 = (166, 204, 20, 15) # Component 1
patch_coords_2 = (148, 222, 20, 15) # Component 2
patch_coords_3 = (132, 242, 20, 15) # Component 3
patch_coords_4 = (112, 262, 20, 15) # Component 4

# List of all patch coordinates
patch_coords_list = [patch_coords_1, patch_coords_2, patch_coords_3, patch_coords_4]

check_fixtures = CheckFixtures(patch_coords_list)

monitor = RobotSafetyMonitor(safety_distance=0.5)

small_state = 0
state = 100


def move_to_home_pos(rtde_c):
    home = np.array([2.43, -130.48, 95.77, 304.95, 269.33, 261.24])
    rtde_c.moveJ([math.radians(deg) for deg in home], 0.5, 0.3)

move_to_home_pos(rtde_c)

def change_robot_velocity(safety_warning, fixture_results, distance):
    """Function to change the robot velocity based on robot-to-worker distance and objects in fixture detection."""
    if safety_warning:
        robot_velocity = 0.3 * distance
    elif np.any(fixture_results == 1) and not safety_warning:
        robot_velocity = 1.0
    else:
        robot_velocity = 0.5
    return robot_velocity


try:
    while True:
        monitor.set_robot_tcp(rtde_r.getActualTCPPose())
        safety_warning, distance, current_frame, terminate = monitor.monitor_safety(patch_coords_list)

        # Check if objects are detected in all patches
        fixture_results = check_fixtures.check_all_patches(reference_image, current_frame)

        # Change robot_velocity based on distance from the human worker to the robot
        robot_velocity = change_robot_velocity(safety_warning, fixture_results, distance)

        # State machine
        match state:
            case 0: # Take component from 1. fixture
                match small_state:
                    case 0:
                        # Above pick up 1. component
                        joint_pos_1_ab_deg = np.array([68.05, -66.47, 87.16, 250.25, 270.29, 271.17])
                        # TCP XYZ [-114.71, -638.17, -103.83] RX RY RZ [1.732, -2.637, -0.015]

                        # Open gripper
                        rtde_input_output.setStandardDigitalOut(0, True)

                        # Move
                        reached = rtde_c.moveJ([math.radians(deg) for deg in joint_pos_1_ab_deg], robot_velocity, 0.3)

                        if reached: 
                            small_state += 1
                            reached = False
                    case 1:
                        # Pick up 1. component
                        joint_pos_1_deg = np.array([68.53, -64.05, 90.21, 244.84, 270.31, 271.68])
                        # TCP XYZ [-109.74, -640.26, -145.87] RX RY RZ [1.732, -2.637, -0.017]
                        reached = rtde_c.moveJ([math.radians(deg) for deg in joint_pos_1_deg], robot_velocity, 0.3)

                        if reached: 
                            small_state += 1
                            reached = False
                    case 2:
                        # Close gripper
                        reached = rtde_input_output.setStandardDigitalOut(0, False)

                        if reached: 
                            small_state += 1
                            reached = False
                    case 3:
                        # Above pick up 1. component
                        joint_pos_1_ab_deg = np.array([68.05, -70.09, 66.97, 274.06, 270.22, 271.07])
                        # TCP XYZ [-114.71, -638.17, -103.83] RX RY RZ [1.732, -2.637, -0.015]
                        reached = rtde_c.moveJ([math.radians(deg) for deg in joint_pos_1_ab_deg], robot_velocity, 0.3)

                        if reached: 
                            small_state = 0
                            reached = False
                            state = 6

            case 1: # Take component from 2. fixture
                match small_state:         
                    case 0:
                        # Above pick up 2. component
                        joint_pos_2_ab_deg = np.array([69.07, -74.42, 98.29, 247.50, 270.32, 272.54])
                        # TCP XYZ [-80.28, -579.63, -105.11] RX RY RZ [1.727, -2.647, -0.023]

                        # Open gripper
                        rtde_input_output.setStandardDigitalOut(0, True)

                        # Move
                        reached = rtde_c.moveJ([math.radians(deg) for deg in joint_pos_2_ab_deg], robot_velocity, 0.3)

                        if reached: 
                            small_state += 1
                            reached = False
                    case 1:
                        # Pick up 2. component
                        joint_pos_2_deg = np.array([69.03, -71.71, 102.11, 240.99, 270.32, 272.53])
                        # TCP XYZ [-80.27, -578.46, -150.71] RX RY RZ [1.727, -2.647, -0.023]
                        reached = rtde_c.moveJ([math.radians(deg) for deg in joint_pos_2_deg], robot_velocity, 0.3)

                        if reached: 
                            small_state += 1
                            reached = False
                    case 2:
                        # Close gripper
                        reached = rtde_input_output.setStandardDigitalOut(0, False)

                        if reached: 
                            small_state += 1
                            reached = False
                    case 3:
                        # Above pick up 2. component
                        joint_pos_2_ab_deg = np.array([69.07, -79.10, 78.95, 271.52, 270.26, 272.43])
                        # TCP XYZ [-80.28, -579.63, -105.11] RX RY RZ [1.727, -2.647, -0.023]
                        reached = rtde_c.moveJ([math.radians(deg) for deg in joint_pos_2_ab_deg], robot_velocity, 0.3)

                        if reached: 
                            small_state = 0
                            reached = False
                            state = 6
                
            case 2: # Take component from 3. fixture
                match small_state:         
                    case 0:
                        # Above pick up 3. component
                        joint_pos_3_ab_deg = np.array([69.50, -83.71, 111.47, 242.33, 270.32, 272.55])
                        # TCP XYZ [-49.23, -508.43, -113.75] RX RY RZ [1.727, -2.625, -0.002]

                        # Open gripper
                        rtde_input_output.setStandardDigitalOut(0, True)

                        # Move
                        reached = rtde_c.moveJ([math.radians(deg) for deg in joint_pos_3_ab_deg], robot_velocity, 0.3)

                        if reached: 
                            small_state += 1
                            reached = False
                    case 1:
                        # Pick up 3. component
                        joint_pos_3_deg = np.array([69.50, -80.99, 114.47, 236.61, 270.32, 272.57])
                        # TCP XYZ [-49.24, -508.42, -150.15] RX RY RZ [1.727, -2.625, -0.002]
                        reached = rtde_c.moveJ([math.radians(deg) for deg in joint_pos_3_deg], robot_velocity, 0.3)

                        if reached: 
                            small_state += 1
                            reached = False
                    case 2:
                        # Close gripper
                        reached = rtde_input_output.setStandardDigitalOut(0, False)

                        if reached: 
                            small_state += 1
                            reached = False
                    case 3:
                        # Above pick up 3. component
                        joint_pos_3_ab_deg = np.array([69.50, -89.82, 91.32, 268.59, 270.26, 272.43])
                        # TCP XYZ [-49.23, -508.43, -113.75] RX RY RZ [1.727, -2.625, -0.002]
                        reached = rtde_c.moveJ([math.radians(deg) for deg in joint_pos_3_ab_deg], robot_velocity, 0.3)

                        if reached: 
                            small_state = 0
                            reached = False
                            state = 6

            case 3: # Take component from 4. fixture
                match small_state:         
                    case 0:
                        # Above pick up 4. component
                        joint_pos_4_ab_deg = np.array([69.61, -92.89, 119.87, 243.11, 270.32, 272.71])
                        # TCP XYZ [-25.55, -447.09, -107.00] RX RY RZ [1.726, -2.626, -0.002]

                        # Open gripper
                        rtde_input_output.setStandardDigitalOut(0, True)

                        # Move
                        reached = rtde_c.moveJ([math.radians(deg) for deg in joint_pos_4_ab_deg], robot_velocity, 0.3)

                        if reached: 
                            small_state += 1
                            reached = False
                    case 1:
                        # Pick up 4. component    
                        joint_pos_4_deg = np.array([69.78, -88.92, 123.92, 235.09, 270.32, 272.93])
                        # TCP XYZ [-24.51, -448.18, -153.59] RX RY RZ [1.726, -2.626, -0.002]
                        reached = rtde_c.moveJ([math.radians(deg) for deg in joint_pos_4_deg], robot_velocity, 0.3)

                        if reached: 
                            small_state += 1
                            reached = False
                    case 2:
                        # Close gripper
                        reached = rtde_input_output.setStandardDigitalOut(0, False)

                        if reached: 
                            small_state += 1
                            reached = False
                    case 3:
                        # Above pick up 4. component
                        joint_pos_4_ab_deg = np.array([69.62, -98.70, 99.53, 269.27, 270.26, 272.59])
                        # TCP XYZ [-25.55, -447.09, -107.00] RX RY RZ [1.726, -2.626, -0.002]
                        reached = rtde_c.moveJ([math.radians(deg) for deg in joint_pos_4_ab_deg], robot_velocity, 0.3)

                        if reached: 
                            small_state = 0
                            reached = False
                            state = 6
                
            case 4: # Take component from 5. fixture
                match small_state:         
                    case 0:
                        # Above pick up 4. component
                        joint_pos_4_ab_deg = np.array([69.61, -92.89, 119.87, 243.11, 270.32, 272.71])
                        # TCP XYZ [-25.55, -447.09, -107.00] RX RY RZ [1.726, -2.626, -0.002]

                        # Open gripper
                        rtde_input_output.setStandardDigitalOut(0, True)

                        # Move
                        reached = rtde_c.moveJ([math.radians(deg) for deg in joint_pos_4_ab_deg], robot_velocity, 0.3)

                        if reached: 
                            small_state += 1
                            reached = False
                    case 1:
                        # Pick up 4. component    
                        joint_pos_4_deg = np.array([69.78, -88.92, 123.92, 235.09, 270.32, 272.93])
                        # TCP XYZ [-24.51, -448.18, -153.59] RX RY RZ [1.726, -2.626, -0.002]
                        reached = rtde_c.moveJ([math.radians(deg) for deg in joint_pos_4_deg], robot_velocity, 0.3)

                        if reached: 
                            small_state += 1
                            reached = False
                    case 2:
                        # Close gripper
                        reached = rtde_input_output.setStandardDigitalOut(0, False)

                        if reached: 
                            small_state += 1
                            reached = False
                    case 3:
                        # Above pick up 4. component
                        joint_pos_4_ab_deg = np.array([69.61, -92.89, 119.87, 243.11, 270.32, 272.71])
                        # TCP XYZ [-25.55, -447.09, -107.00] RX RY RZ [1.726, -2.626, -0.002]
                        reached = rtde_c.moveJ([math.radians(deg) for deg in joint_pos_4_ab_deg], robot_velocity, 0.3)

                        if reached: 
                            small_state = 0
                            reached = False
                            state = 6


            case 5: # Take component from 6. fixture
                match small_state:         
                    case 0:
                        # Above pick up 4. component
                        joint_pos_4_ab_deg = np.array([69.61, -92.89, 119.87, 243.11, 270.32, 272.71])
                        # TCP XYZ [-25.55, -447.09, -107.00] RX RY RZ [1.726, -2.626, -0.002]

                        # Open gripper
                        rtde_input_output.setStandardDigitalOut(0, True)

                        # Move
                        reached = rtde_c.moveJ([math.radians(deg) for deg in joint_pos_4_ab_deg], robot_velocity, 0.3)

                        if reached: 
                            small_state += 1
                            reached = False
                    case 1:
                        # Pick up 4. component    
                        joint_pos_4_deg = np.array([69.78, -88.92, 123.92, 235.09, 270.32, 272.93])
                        # TCP XYZ [-24.51, -448.18, -153.59] RX RY RZ [1.726, -2.626, -0.002]
                        reached = rtde_c.moveJ([math.radians(deg) for deg in joint_pos_4_deg], robot_velocity, 0.3)

                        if reached: 
                            small_state += 1
                            reached = False
                    case 2:
                        # Close gripper
                        reached = rtde_input_output.setStandardDigitalOut(0, False)

                        if reached: 
                            small_state += 1
                            reached = False
                    case 3:
                        # Above pick up 4. component
                        joint_pos_4_ab_deg = np.array([69.61, -92.89, 119.87, 243.11, 270.32, 272.71])
                        # TCP XYZ [-25.55, -447.09, -107.00] RX RY RZ [1.726, -2.626, -0.002]
                        reached = rtde_c.moveJ([math.radians(deg) for deg in joint_pos_4_ab_deg], robot_velocity, 0.3)

                        if reached: 
                            small_state = 0
                            reached = False
                            state = 6

            case 6:
                match small_state:
                    case 0:
                        # Interpolate
                        joint_pos_intermediate = np.array([2.43, -130.48, 95.77, 304.95, 269.33, 261.24])
                        joint_pos_place = np.array([-35.01, -73.70, 84.80, 256.20, 269.29, 261.24])

                        from_actual_to_intermediate = interpolate_joint_positions(rtde_r.getActualQ(), joint_pos_intermediate, num_points=10)
                        from_intermediate_to_place = interpolate_joint_positions(joint_pos_intermediate, joint_pos_place, num_points=10)
                        from_place_to_intermediate = interpolate_joint_positions(joint_pos_place, joint_pos_intermediate, num_points=10)

                        intermediate_index = 0  # Initialize the index for interpolating joint positions
                        small_state += 1
                    case 1:
                        # # From actual to intermediate point
                        # if intermediate_index < len(from_actual_to_intermediate):
                        #     joint_pos = from_actual_to_intermediate[intermediate_index]
                        #     reached = rtde_c.moveJ([math.radians(deg) for deg in joint_pos], robot_velocity, 0.3)
                        #     if reached:
                        #         intermediate_index += 1  # Move to the next joint position
                        # else:
                        #     small_state += 1  # Move to the next state once all intermediate points are reached
                        #     reached = False
                        #     intermediate_index = 0

                        reached = rtde_c.moveJ([math.radians(deg) for deg in joint_pos_intermediate], robot_velocity, 0.3)

                        if reached:
                            small_state += 1
                            reached = False
                    case 2:
                        # # From intermediate to place point
                        # if intermediate_index < len(from_intermediate_to_place):
                        #     joint_pos = from_intermediate_to_place[intermediate_index]
                        #     reached = rtde_c.moveJ([math.radians(deg) for deg in joint_pos], robot_velocity, 0.3)
                        #     if reached:
                        #         intermediate_index += 1  # Move to the next joint position
                        # else:
                        #     small_state += 1  # Move to the next state once all intermediate points are reached
                        #     reached = False
                        #     intermediate_index = 0

                        reached = rtde_c.moveJ([math.radians(deg) for deg in joint_pos_place], robot_velocity, 0.3)

                        if reached:
                            small_state += 1
                            reached = False
                    case 3:
                        # Open gripper
                        reached = rtde_input_output.setStandardDigitalOut(0, True)

                        if reached: 
                            small_state += 1
                            reached = False
                    case 4:
                        # # From place to intermediate point
                        # if intermediate_index < len(from_intermediate_to_place):
                        #     joint_pos = from_intermediate_to_place[intermediate_index]
                        #     reached = rtde_c.moveJ([math.radians(deg) for deg in joint_pos], robot_velocity, 0.3)
                        #     if reached:
                        #         intermediate_index += 1  # Move to the next joint position
                        # else:
                        #     small_state = 0 # Move to the next state once all intermediate points are reached
                        #     reached = False
                        #     intermediate_index = 0
                        #     state = 100

                        reached = rtde_c.moveJ([math.radians(deg) for deg in joint_pos_intermediate], robot_velocity, 0.3)

                        if reached:
                            small_state = 0
                            reached = False
                            state = 100
                            
            
            case _:
                if fixture_results[0]: 
                    print("Moving to fixture 1")
                    state = 0
                elif fixture_results[1]:
                    print("Moving to fixture 2") 
                    state = 1
                elif fixture_results[2]: 
                    print("Moving to fixture 3")
                    state = 2
                elif fixture_results[3]: 
                    print("Moving to fixture 4")
                    state = 3
                # elif fixture_results[4]: 
                    # print("Moving to fixture 5")
                    # state = 4
                # elif fixture_results[5]: 
                    # print("Moving to fixture 6")
                    # state = 5



finally:
    # Stop the camera stream and close windows
    monitor.pipeline.stop()
    cv2.destroyAllWindows()


# # Set TCP frame
# rtde_c.setTcp([0, 0, 0, 0, 0, 0])

# # Home position
# rtde_c.moveJ([0.0, -1.5708, 0.0, -1.5708, 0.0, 0.0], 1.0, 0.3) # Still needs to be specified

# # Above pick up 1. component
# joint_pos_1_ab_deg = np.array([68.05, -66.47, 87.16, 250.25, 270.29, 271.17])
# # TCP XYZ [-114.71, -638.17, -103.83] RX RY RZ [1.732, -2.637, -0.015]
# rtde_c.moveJ([math.radians(deg) for deg in joint_pos_1_ab_deg], 1.0, 0.3) 

# # Pick up 1. component
# joint_pos_1_deg = np.array([68.53, -64.05, 90.21, 244.84, 270.31, 271.68])
# # TCP XYZ [-109.74, -640.26, -145.87] RX RY RZ [1.732, -2.637, -0.017]
# rtde_c.moveJ([math.radians(deg) for deg in joint_pos_1_deg], 1.0, 0.3)

# # Above pick up 2. component
# joint_pos_2_ab_deg = np.array([69.07, -74.42, 98.29, 247.50, 270.32, 272.54])
# # TCP XYZ [-80.28, -579.63, -105.11] RX RY RZ [1.727, -2.647, -0.023]
# rtde_c.moveJ([math.radians(deg) for deg in joint_pos_2_ab_deg], 1.0, 0.3)

# # Pick up 2. component
# joint_pos_2_deg = np.array([69.03, -71.71, 102.11, 240.99, 270.32, 272.53])
# # TCP XYZ [-80.27, -578.46, -150.71] RX RY RZ [1.727, -2.647, -0.023]
# rtde_c.moveJ([math.radians(deg) for deg in joint_pos_2_deg], 1.0, 0.3)

# # Above pick up 3. component
# joint_pos_3_ab_deg = np.array([69.50, -83.71, 111.47, 242.33, 270.32, 272.55])
# # TCP XYZ [-49.23, -508.43, -113.75] RX RY RZ [1.727, -2.625, -0.002]
# rtde_c.moveJ([math.radians(deg) for deg in joint_pos_3_ab_deg], 1.0, 0.3)

# # Pick up 3. component
# joint_pos_3_deg = np.array([69.50, -80.99, 114.47, 236.61, 270.32, 272.57])
# # TCP XYZ [-49.24, -508.42, -150.15] RX RY RZ [1.727, -2.625, -0.002]
# rtde_c.moveJ([math.radians(deg) for deg in joint_pos_3_deg], 1.0, 0.3)

# # Above pick up 4. component
# joint_pos_4_ab_deg = np.array([69.61, -92.89, 119.87, 243.11, 270.32, 272.71])
# # TCP XYZ [-25.55, -447.09, -107.00] RX RY RZ [1.726, -2.626, -0.002]
# rtde_c.moveJ([math.radians(deg) for deg in joint_pos_4_ab_deg], 1.0, 0.3)

# # Pick up 4. component
# joint_pos_4_deg = np.array([69.78, -88.92, 123.92, 235.09, 270.32, 272.93])
# # TCP XYZ [-24.51, -448.18, -153.59] RX RY RZ [1.726, -2.626, -0.002]
# rtde_c.moveJ([math.radians(deg) for deg in joint_pos_4_deg], 1.0, 0.3)