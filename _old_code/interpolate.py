import numpy as np

def interpolate_joint_positions(q_start, q_end, num_points=10):
    """
    Interpolate between two sets of joint positions.
    
    Parameters:
    q_start (list): The starting joint positions.
    q_end (list): The ending joint positions.
    num_points (int): The number of interpolation points (default is 10).
    
    Returns:
    list: A list of interpolated joint positions.
    """
    # Ensure inputs are numpy arrays for element-wise operations
    q_start = np.array(q_start)
    q_end = np.array(q_end)
    
    # Create an array of interpolation factors from 0 to 1
    t_values = np.linspace(0, 1, num_points)
    
    # Interpolate between the start and end joint positions
    interpolated_positions = [(1 - t) * q_start + t * q_end for t in t_values]
    
    # Convert back to a list of lists for easier interpretation
    return [list(pos) for pos in interpolated_positions]

# Example usage
q_start = [-1.54, -1.83, -2.28, -0.59, 1.60, 0.023]
q_end = [-1.0, -1.5, -2.0, -0.3, 1.2, 0.5]
interpolated_positions = interpolate_joint_positions(q_start, q_end, num_points=3)
print(interpolated_positions)
