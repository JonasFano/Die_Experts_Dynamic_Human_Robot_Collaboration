import numpy as np
import rtde_control
import rtde_receive

rtde_c = rtde_control.RTDEControlInterface("192.168.1.100")
rtde_r = rtde_receive.RTDEReceiveInterface("192.168.1.100")

def rotation_matrix_from_euler_angles(roll, pitch, yaw, degrees=False):
    """
    Creates a rotation matrix from roll, pitch, and yaw (Euler angles).

    Parameters:
    roll (float): Rotation around the X-axis.
    pitch (float): Rotation around the Y-axis.
    yaw (float): Rotation around the Z-axis.
    degrees (bool): If True, the angles are in degrees. Otherwise, in radians.

    Returns:
    numpy.ndarray: A 3x3 rotation matrix.
    """
    if degrees:
        roll = np.radians(roll)
        pitch = np.radians(pitch)
        yaw = np.radians(yaw)
    
    # Rotation matrix around X-axis (roll)
    Rx = np.array([
        [1, 0, 0],
        [0, np.cos(roll), -np.sin(roll)],
        [0, np.sin(roll), np.cos(roll)]
    ])
    
    # Rotation matrix around Y-axis (pitch)
    Ry = np.array([
        [np.cos(pitch), 0, np.sin(pitch)],
        [0, 1, 0],
        [-np.sin(pitch), 0, np.cos(pitch)]
    ])
    
    # Rotation matrix around Z-axis (yaw)
    Rz = np.array([
        [np.cos(yaw), -np.sin(yaw), 0],
        [np.sin(yaw), np.cos(yaw), 0],
        [0, 0, 1]
    ])
    
    # Combined rotation matrix: R = Rz * Ry * Rx
    R = Rz @ Ry @ Rx
    return R


def transform_R(rotation, degrees=False):
    """
    Creates a 6x6 transformation matrix for rotational motion.

    Parameters:
    rotation (tuple): A tuple (roll, pitch, yaw) for the rotation in radians (or degrees if specified).
    degrees (bool): Set to True if the rotation angles are given in degrees.

    Returns:
    numpy.ndarray: A 6x6 transformation matrix.
    """
    # Convert Euler angles to a 3x3 rotation matrix
    R = rotation_matrix_from_euler_angles(*rotation, degrees=degrees)

    # Create the 6x6 transformation matrix
    R_mat = np.zeros((6, 6))  # Initialize a 6x6 matrix of zeros
    R_mat[:3, :3] = R         # Top-left 3x3 block is R
    R_mat[3:, 3:] = R         # Bottom-right 3x3 block is R

    return R_mat


# Example usage:
w_t_b = np.array([-0.276, 0.024, -0.035, 0, 0, 0]) # Translation (x, y, z)
#w_t_b = np.array([-0.10, -0.276, -0.035, 0, 0, 0]) # Translation (x, y, z)

w_R_b = transform_R([0, 180, 67.5], degrees=True)  # Rotation (roll, pitch, yaw) in degrees
#w_R_b = transform_R([0, 180, -112.5], degrees=True)  # Rotation (roll, pitch, yaw) in degrees


b_p_tcp = rtde_r.getActualTCPPose() #np.array([-0.08, -0.278, -0.151, 1.718, -2.631, -0.023]) 
# placeholder rtde_c.getActualTCPPose()

w_p_tcp = w_R_b @ b_p_tcp + w_t_b

c_T_w = np.array([[ 0.51970216,  0.854174,    0.01645907, -0.53570101],
                  [-0.59055939,  0.34525865,  0.72936413,  0.40769184],
                  [ 0.61733134, -0.38878397,  0.68387034,  1.36497584],
                  [ 0,           0,           0,           1,        ]])

c_R_w = np.zeros((6, 6))
c_R_w[:3, :3] = c_T_w[:3,:3]
c_R_w[3:, 3:] = c_T_w[:3,:3]

c_t_w = np.zeros(6)
c_t_w[:3] = c_T_w[:3, 3]

c_p_tcp = c_R_w @ w_p_tcp + c_t_w

# math.dist(c_p_tcp[:3], human_pos[:3])

print([round(w_p_tcp[i],3) for i in range(len(w_p_tcp))])
print("------------------------------------------------------")
print([round(c_p_tcp[i],3) for i in range(len(c_p_tcp))])