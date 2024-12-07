from .state_machine import StateMachine
from socket_robot_controller.client import RobotSocketClient

robot_controller = RobotSocketClient("http://localhost:5000")

state_machine = StateMachine(robot_controller)

while True:
    state_machine.process_state_machine()