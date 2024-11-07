import numpy as np

def interpolate_joint_positions(q_start, q_end, num_points=10):
    """
    Interpolate between two sets of joint positions (in degrees), independently for each joint.
    
    Parameters:
    q_start (list): The starting joint positions (in degrees).
    q_end (list): The ending joint positions (in degrees).
    num_points (int): The number of interpolation points (default is 10).
    
    Returns:
    list: A list of interpolated joint positions.
    """
    q_start = np.array(q_start)
    q_end = np.array(q_end)
    
    # Generate num_points linearly spaced values between 0 and 1
    t_values = np.linspace(0, 1, num_points)[:, np.newaxis]  # Reshape for broadcasting
    
    # Perform linear interpolation for each joint separately
    interpolated_positions = q_start + t_values * (q_end - q_start)
    
    # Convert to list of lists (each inner list represents joint positions at an interpolation step)
    return interpolated_positions.tolist()


def interpolate_tcp_poses(pose_start, pose_end, num_points=10):
    """
    Interpolate between two TCP poses: (position, orientation).
    
    Parameters:
    pose_start (list): The starting TCP pose [x, y, z, roll, pitch, yaw].
    pose_end (list): The ending TCP pose [x, y, z, roll, pitch, yaw].
    num_points (int): The number of interpolation points (default is 10).
    
    Returns:
    list: A list of interpolated TCP poses.
    """
    # Split into positions and orientations
    position_start = np.array(pose_start[:3])
    orientation_start = np.array(pose_start[3:])
    position_end = np.array(pose_end[:3])
    orientation_end = np.array(pose_end[3:])

    # Interpolate positions
    t_values = np.linspace(0, 1, num_points)[:, np.newaxis]  # Reshape for broadcasting
    interpolated_positions = position_start + t_values * (position_end - position_start)

    # Interpolate orientations
    interpolated_orientations = orientation_start + t_values * (orientation_end - orientation_start)

    # Combine interpolated positions and orientations into a single pose
    interpolated_poses = [np.concatenate((pos, orient)).tolist() for pos, orient in zip(interpolated_positions, interpolated_orientations)]

    return interpolated_poses



if __name__ == "__main__":
    # Example usage: Joint positions in degrees
    q_start = [69.07, -79.10, 78.95, 271.52, 270.26, 272.43]  # Example: start joint positions (in degrees)
    q_end = [2.43, -130.48, 95.77, 304.95, 269.33, 261.24]          # Example: end joint positions (in degrees)
    
    # Interpolate with 3 points (start, midpoint, end)
    interpolated_positions = interpolate_joint_positions(q_start, q_end, num_points=10)
    for interpolated_position in interpolated_positions:
        formatted_position = [f"{joint:.3f}" for joint in interpolated_position]
        print(formatted_position)