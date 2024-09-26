import rtde_control
import rtde_receive
from camera import RobotSafetyMonitor
import cv2
import numpy as np


rtde_c = rtde_control.RTDEControlInterface("192.168.1.100")
rtde_r = rtde_receive.RTDEReceiveInterface("192.168.1.100")

monitor = RobotSafetyMonitor(safety_distance=0.5)


try:
    while True:
        print(rtde_r.getActualTCPPose()) 
        
        # TCP seen from the camera [-0.10, -0.25, 1.05]
        # TCP in robot base frame [-0.5485706744986745, -0.521214273227599, 0.6621657372351374]

        tcp_from_camera = np.array([-0.10, -0.25, 1.05])
        tcp_in_base_frame = np.array([-0.5485706744986745, -0.521214273227599, 0.6621657372351374])

        vector_camera_robot = tcp_from_camera - tcp_in_base_frame 
        
        # result: [-0.44857067 -0.27121427 -0.38783426]
        # result 2: [-0.64857067 -0.77121427  1.71216574]
        # result 3: [0.44857067 0.27121427 0.38783426]
        # print(vector_camera_robot)


        monitor.set_robot_tcp(rtde_r.getActualTCPPose())
        monitor.monitor_safety()
finally:
    # Stop the camera stream and close windows
    monitor.pipeline.stop()
    cv2.destroyAllWindows()

# #Set TCP frame
# rtde_c.setTcp([0, 0, 0, 0, 0, 0])

# #Home position
# rtde_c.moveJ([0.0, -1.5708, 0.0, -1.5708, 0.0, 0.0], 1.0, 0.3)

# #Move to first pose
# rtde_c.moveJ([0.0, -1.5708, -1.5708, -1.5708, 1.5708, 0.0], 1.0, 0.3)
# first_pose_q = rtde_r.getActualQ()
# first_pose = rtde_r.getActualTCPPose()
# first_pose_string = ' '.join(str(e) for e in first_pose)
# first_pose_q_string = ' '.join(str(e) for e in first_pose_q)
# print("First Pose: " + first_pose_string)
# print("First Pose Q: " + first_pose_q_string)

# #Move LIN to second pose
# second_pose = first_pose
# second_pose[2] = second_pose[2] + 0.1
# second_pose_string = ' '.join(str(e) for e in second_pose)
# print("Second Pose: " + second_pose_string)
# rtde_c.moveL(second_pose, 0.25, 1.2, False)

# #Back to first pose
# rtde_c.moveJ(first_pose_q, 1.0, 0.3)

# #Example2: move relative to TCP pose
# print("Get initial pose")
# initial_pose = rtde_r.getActualTCPPose()

# desired_displacement = [0.20, 0, 0, 0, 0, 0]

# target_pose_base = rtde_c.poseTrans(initial_pose, desired_displacement)
# print("Target pose w.r.t. base")
# rtde_c.moveL(target_pose_base, 1.0, 0.5, False) #Perform the desired displacement according to the base frame

# print("Back to initial pose")
# rtde_c.moveL(initial_pose, 0.25, 1.2, False)
