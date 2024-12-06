from enum import Enum
from typing import Dict

class Events(Enum):
    IS_CONNECTED = "connect"
    MOVE_TO_POSITION = "move_to_position"
    MOVE_TO_POSITION_BLEND = "move_to_postion_blend"
    GET_JOINT_POSITIONS = "get_joint_positions"
    STOP_ROBOT = "stop_robot"
    SERVER_MESSAGE = "server_message"
    JOINT_POSITIONS = "joint_positions"
    IS_RUNNING = "is_running"
    SPEED_VALUE = "speed_value"
    GET_TCP_VALUE = "get_tcp_value"

menu_options: Dict[int, str] = {
    0: "Disconnect",
    1: "Move to position 1",
    2: "Move to position 2",
    3: "Move to position 3",
    4: "Move to position 4",
    5: "Set speed of robots",
    6: "Robot status",
    7: "Stop moving",
}