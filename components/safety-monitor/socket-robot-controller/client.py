import socketio
from events import Events  # Import the shared enum
import time
from typing import List


# Initialize Socket.IO client
def create_client():
    sio = socketio.Client()

    @sio.event
    def connect():
        print("Connected to server.")

    @sio.event
    def disconnect():
        print("Disconnected from server.")

    @sio.on(Events.SERVER_MESSAGE.value)
    def on_server_message(data):
        print(f"Server message: {data['status']}")

    @sio.on(Events.JOINT_POSITIONS.value)
    def on_joint_positions(data):
        print(f"Joint positions: {data['positions']}")

    return sio


class RobotSocketClient:
    sioc = None
    socket_url = "http://localhost:5000"

    def __init__(self, socket_url=None):
        if socket_url is not None:
            self.socket_url = socket_url

        self.connect_to_server()

    def connect_to_server(self):
        while True:  # Keep trying to connect until it works
            try:
                self.sioc = create_client()
                self.sioc.connect(self.socket_url)
                break
            except Exception as e:
                print(f"Failed to connect to robot socket server with {e}..")
                print("Trying again in 5 sec..")
                time.sleep(5)

    def get_client(self):
        return self.sioc

    def is_running(self):
        self.sioc.call(Events.IS_RUNNING.value)

    def get_tcp_pose(self, retries: int = 3) -> List[float]:
        response = self.sioc.call(Events.GET_TCP_VALUE.value, timeout=5)
        return response["poistions"]

    def open_gripper(self):
        response = self.sioc.call(Events.SET_GRIPPER.value, {"open": True}, timeout=5)
        return response["open"]

    def close_gripper(self):
        response = self.sioc.call(Events.SET_GRIPPER.value, {"open": False}, timeout=5)
        return response["open"]

    def get_tcp_velocity(self):
        self.sioc.call(Events.GET_SPEED.value)
        response = self.sioc.receive(timeout=5)
        return response["speed"]

    def set_robot_velocity(self, speed_fraction=1):
        response = self.sioc.call(Events.SPEED_VALUE.value, {"speed": speed_fraction})
        return response["speed"]

    def get_actual_joint_positions(self):
        response = self.sioc.call(Events.JOINT_POSITIONS.value)
        return response["positions"]

    def moveJ_path(self, path):
        data = {"position": path}
        response = self.sioc.call(Events.MOVE_TO_POSITION.value, data)
        return response["postions"]

    def moveL_path(self, path):
        data = {"position": path}
        response = self.sioc.call(Events.MOVE_TO_POSITION_L.value, data)
        return response["positions"]

    def moveL(
        self, target_pose: List[float], velocity: float = 0.2, acceleration: float = 0.3
    ):
        data = {
            "position": target_pose,
            "speed": velocity,
            "acceleration": acceleration,
        }
        response = self.sioc.call(Events.MOVE_L_SPEED_ACCEL.value, data)
        return response["positions"]

    def stop_robot(self):
        self.sioc.call(Events.STOP_ROBOT.value)
