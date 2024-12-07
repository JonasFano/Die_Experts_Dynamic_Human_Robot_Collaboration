import numpy as np

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

def make_transformation_matrix_xyzrpy(translation, rotation, degrees=False):
    """
    Constructs a 4x4 transformation matrix from XYZ translation and XYZ rotation (roll, pitch, yaw).

    Parameters:
    translation (list or tuple): Translation [x, y, z].
    rotation (list or tuple): Rotation [roll, pitch, yaw].
    degrees (bool): If True, the rotation angles are in degrees. Otherwise, in radians.

    Returns:
    numpy.ndarray: A 4x4 transformation matrix.
    """
    if len(translation) != 3 or len(rotation) != 3:
        raise ValueError("Translation and rotation must be 3-element lists or tuples.")

    # Create the rotation matrix
    rotation_matrix = rotation_matrix_from_euler_angles(*rotation, degrees=degrees)

    # Create the transformation matrix
    transformation_matrix = np.eye(4)
    transformation_matrix[:3, :3] = rotation_matrix
    transformation_matrix[:3, 3] = translation

    return transformation_matrix

# Example usage:
translation = [74, 46.5, 119]  # Translation (x, y, z)
rotation = [45, 0, 0]  # Rotation (roll, pitch, yaw) in degrees

# Generate the transformation matrix
transformation_matrix = make_transformation_matrix_xyzrpy(translation, rotation, degrees=True)

print("Transformation Matrix:")
print(transformation_matrix)