import rtde_control
import rtde_receive
import rtde_io
import math
import numpy as np

class RobotController:
    def __init__(self, ip_address):
        self.rtde_c = rtde_control.RTDEControlInterface(ip_address)
        self.rtde_r = rtde_receive.RTDEReceiveInterface(ip_address)
        self.rtde_io = rtde_io.RTDEIOInterface(ip_address)
    
    def move_to_position(self, joint_positions, velocity=0.5, acceleration=0.3):
        """Move the robot to the specified joint positions."""
        radians_positions = [math.radians(deg) for deg in joint_positions]
        return self.rtde_c.moveJ(radians_positions, velocity, acceleration)
    
    def open_gripper(self):
        """Open the gripper."""
        return self.rtde_io.setStandardDigitalOut(0, True)

    def close_gripper(self):
        """Close the gripper."""
        return self.rtde_io.setStandardDigitalOut(0, False)

    def get_tcp_pose(self):
        """Get the current TCP (Tool Center Point) pose."""
        return self.rtde_r.getActualTCPPose()
    
    def get_tcp_velocity(self):
        """Get the current TCP (Tool Center Point) speed in cartesian coordinates."""
        # self.rtde_r.getSpeedScaling()
        return self.rtde_r.getActualTCPSpeed()
    
    def get_actual_joint_positions(self):
        """Get the actual joint positions of the robot."""
        return np.degrees(self.rtde_r.getActualQ())
    
    def set_robot_velocity(self, speed_fraction=1):
        """Set the speed slider on the controller. It's a fraction value between 0 and 1 based on the selected velocity when using moveL"""
        return self.rtde_io.setSpeedSlider(speed_fraction)
    
    def moveJ_path(self, path):
        """
        Executes a moveJ command with a path containing joint positions, 
        with speed, acceleration, and blend radius.

        Args:
            path (List): It contains:
                - A list of joint positions in radians,
                - For each list it contains a list of joint velocity, acceleration, and a blend radius for smooth transitions [m].
        
        Returns:
            bool: True if the command was successfully sent, False otherwise.
        """
        return self.rtde_c.moveJ(path)
    
    def moveL_path(self, path):
        """
        Executes a moveL command with a path containing TCP poses, 
        with speed, acceleration, and blend radius.

        Args:
            path (List): It contains:
                - A list of TCP poses in base frame,
                - For each list it contains a list of joint velocity, acceleration, and a blend radius for smooth transitions [m].
        
        Returns:
            bool: True if the command was successfully sent, False otherwise.
        """
        return self.rtde_c.moveL(path)


    def moveL(self, target_pose, velocity=0.2, acceleration=0.3):
        """
        Move the robot's end-effector to the target pose in Cartesian space.
        
        target_pose: A list or array with [x, y, z, roll, pitch, yaw].
        velocity: Desired velocity for the movement.
        acceleration: Desired acceleration for the movement.
        """
        return self.rtde_c.moveL(target_pose, speed=velocity, acceleration=acceleration)
    
    def set_free_move(self, enable):
        if enable:
            self.rtde_r.freedriveMode()
        else:
            self.rtde_r.endFreedriveMode()