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