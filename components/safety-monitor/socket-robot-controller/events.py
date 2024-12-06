from enum import Enum
from typing import Dict


class Events(Enum):
    IS_CONNECTED = "connect"
    IS_RUNNING = "is_running"
    STOP_ROBOT = "stop_robot"
    SERVER_MESSAGE = "server_message"
    JOINT_POSITIONS = "joint_positions"
    GET_SPEED_VALUE = "get_speed_value"
    SET_SPEED_VALUE = "set_speed_value"
    GET_TCP_VALUE = "get_tcp_value"
    SET_GRIPPER = "set_gripper_value"
    GET_JOINT_POSITIONS = "get_joint_positions"
    MOVE_TO_POSITION = "move_to_position"
    MOVE_TO_POSITION_L = "move_to_position_l"
    MOVE_TO_POSITION_J = "move_to_position_l"
    MOVE_L_SPEED_ACCEL = "move_l_SPEED_ACCEL"


menu_options: Dict[int, str] = {
    0: "Disconnect",
    1: "Move to position 1",
    2: "Move to position 2",
    3: "Move to position 3",
    4: "Move to position 4",
    5: "Set speed of robots",
    6: "Robot status",
    7: "Stop moving",
    8: "Open gripper",
    9: "Close gripper",
}
