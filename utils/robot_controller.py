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
    
    def get_actual_joint_positions(self):
        """Get the actual joint positions of the robot."""
        return np.degrees(self.rtde_r.getActualQ())
    
    def moveJ_path(self, path, velocity=None, asynchronous=False):
        """
        Executes a moveJ command with a path containing one joint position, 
        with speed, acceleration, and blend radius.

        Args:
            path (dict): It is a dict with:
                - 'q': joint positions in degrees,
                - 'acceleration': joint acceleration of leading axis [rad/s^2],
                - 'blend': blend radius for smooth transitions [m].
            velocity (float): If provided, overrides the speed defined in the path entry.
            asynchronous (bool): If true, command executes asynchronously.
        
        Returns:
            bool: True if the command was successfully sent, False otherwise.
        """
        # Convert joint positions to radians
        radians_positions = [math.radians(deg) for deg in path['q']]

        # Prepare formatted path as a list containing one entry
        formatted_path = [radians_positions, velocity, path['acceleration'], path['blend']]

        # Execute the moveJ command with formatted path
        return self.rtde_c.moveJ([formatted_path], asynchronous)


    def move_to_cartesian_pose(self, target_pose, velocity=0.5, acceleration=0.3, blend=0.0):
        """
        Move the robot's end-effector to the target pose in Cartesian space.
        
        target_pose: A list or array with [x, y, z, roll, pitch, yaw].
        velocity: Desired velocity for the movement.
        acceleration: Desired acceleration for the movement.
        blend: Desired blend for the movement.
        """
        return self.rtde_c.servoC(target_pose, velocity=velocity, acceleration=acceleration, blend=blend)