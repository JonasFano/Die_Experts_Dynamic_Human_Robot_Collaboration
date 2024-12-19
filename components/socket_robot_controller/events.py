from enum import Enum

class Events(Enum):
    IS_CONNECTED = "connect"
    IS_RUNNING = "is_running"
    STOP_ROBOT = "stop_robot"
    SERVER_MESSAGE = "server_message"
    JOINT_POSITIONS = "joint_positions"
    GET_SPEED_VALUE = "get_speed_value"
    SET_SPEED_VALUE = "set_speed_value"
    GET_TCP_VALUE = "get_tcp_pose"
    SET_GRIPPER = "set_gripper_value"
    GET_JOINT_POSITIONS = "get_joint_positions"
    MOVE_TO_POSITION = "move_to_position"
    MOVE_TO_POSITION_L = "move_to_position_l"
    MOVE_TO_POSITION_J = "move_to_position_l"
    MOVE_L_SPEED_ACCEL = "move_l_SPEED_ACCEL"
    ASYNC_PROGRESS = "async_progress"