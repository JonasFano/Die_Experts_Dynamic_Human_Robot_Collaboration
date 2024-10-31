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
    pose_start (tuple): The starting TCP pose (position, orientation).
                        Position is a list of [x, y, z] and orientation is a list of [roll, pitch, yaw].
    pose_end (tuple): The ending TCP pose (position, orientation).
    num_points (int): The number of interpolation points (default is 10).
    
    Returns:
    list: A list of interpolated TCP poses.
    """
    position_start, orientation_start = pose_start
    position_end, orientation_end = pose_end

    # Interpolate positions
    position_start = np.array(position_start)
    position_end = np.array(position_end)
    t_values = np.linspace(0, 1, num_points)[:, np.newaxis]  # Reshape for broadcasting
    interpolated_positions = position_start + t_values * (position_end - position_start)

    # Interpolate orientations
    orientation_start = np.array(orientation_start)
    orientation_end = np.array(orientation_end)
    interpolated_orientations = orientation_start + t_values * (orientation_end - orientation_start)

    # Combine interpolated positions and orientations into a single pose
    interpolated_poses = [(pos.tolist(), orient.tolist()) for pos, orient in zip(interpolated_positions, interpolated_orientations)]

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