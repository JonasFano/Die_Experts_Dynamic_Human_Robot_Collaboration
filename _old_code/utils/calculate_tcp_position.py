import rtde_control
import rtde_io as rtdeio
import rtde_receive
import math
import numpy as np
from scipy.spatial.transform import Rotation as R


IP = "192.168.1.100"
"""
r_controller = rtde_control.RTDEControlInterface(IP)
rtde_receive = rtde_receive.RTDEReceiveInterface(IP)
rt_io = rtdeio.RTDEIOInterface(IP)
tcp_pose = rtde_receive.getActualTCPPose()

"""


tcp_pose =[-0.0522081420651402, -0.1860365086580939, 0.4971387378730318, -2.337205497882533, 2.0629104442118296, 0.028725767781790888]

transformed_rotation = list(map(lambda x: x*(180.0/math.pi),[45, 15, 0]))
CAMERA_TRANSLATION = np.array([0.64, 0.47, 1.27])  # Replace with the actual camera position in world coordinates
CAMERA_ROTATION = R.from_euler('xyz', transformed_rotation).as_matrix()  # Replace with actual camera orientation in world coordinates

# Transformation from camera to world frame
T_CAMERA_TO_WORLD = np.eye(4)
T_CAMERA_TO_WORLD[:3, :3] = CAMERA_ROTATION
T_CAMERA_TO_WORLD[:3, 3] = CAMERA_TRANSLATION
p = tcp_pose[:3]
p.append(1)

np_pose = np.array(p).T

tcp_in_camera_frame = np_pose@T_CAMERA_TO_WORLD
print(tcp_in_camera_frame)