from enum import Enum

class Events(Enum):
    IS_CONNECTED = "connect"
    MOVE_TO_POSITION = "move_to_position"
    GET_JOINT_POSITIONS = "get_joint_positions"
    STOP_ROBOT = "stop_robot"
    SERVER_MESSAGE = "server_message"
    JOINT_POSITIONS = "joint_positions"
    SPEED_VALUE = "speed_value"