import socketio
from events import Events, menu_options  # Import the shared enum
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

    def __init__(self,socket_url="http://localhost:5000"):
        while True: # Keep trying to connect until it works
            try:
                self.sioc = create_client()
                self.sioc.connect(socket_url)
                break
            except Exception as e:
                print(f"Failed to connect to robot socket server with {e}..")
                print("Trying again in 5 sec..")
                time.sleep(5)

    def get_client(self):
        return self.sioc

    def get_tcp_pose(self, retries: int=3) -> List[float]:
        tries_left = retries
        while True:
            try:
                self.sioc.emit(Events.GET_TCP_VALUE.value)
                response = self.sioc.receive(timeout=5)
                return response["tcp_pose"]
            except Exception as e:
                tries_left -= 1
                print(f"Failed to get tcp pose with error {e}")
                print(f"Trying {tries_left} more times.")
    
    def open_gripper(self):
        self.sioc.emit(Events.SET_GRIPPER.value, {"open": True})

    def close_gripper(self):
        self.sioc.emit(Events.SET_GRIPPER.value, {"open": False})

    def get_tcp_velocity(self):
        self.sioc.emit(Events.GET_SPEED.value)
        response = self.sioc.receive(timeout=5)
        return response["speed"]
    
    def get_actual_joint_positions(self):
        self.sioc.emit(Events.JOINT_POSITIONS.value)
        response = self.sioc.receive(timeout=5)
        return response["positions"]
        
    
    def set_robot_velocity(self, speed_fraction=1):
        self.sioc.emit(Events.SPEED_VALUE.value, {"speed": speed_fraction})
    
    def moveJ_path(self, path):
        data = {"position": path}
        self.sioc.emit(Events.MOVE_TO_POSITION.value, data)
    
    def moveL_path(self, path):
        data = {"position": path}
        self.sioc.emit(Events.MOVE_TO_POSITION_L.value, data)

    def moveL(self, target_pose, velocity=0.2, acceleration=0.3):
        data = {
            "position": target_pose,
            "speed": velocity,
            "acceleration": acceleration
        }
        self.sioc.emit(Events.MOVE_TO_POSITION_L, data)




positions = [
        [1.172, -1.2148, 1.7949, -0.6192, -0.1986, 0.0382],
        [0.432, -1.2148, 1.7949, -0.6191, -0.1987, 0.0383],
        [-0.4789, -1.0999, 1.5347, -0.6192, -0.1987, 0.0383],
        [-0.3862, -0.2917, 0.1344, -0.0297, -0.1996, 0.0383]
]

def menu():
    server_url = "http://localhost:5000"  # Replace with your server URL
    client = RobotSocketClient(server_url)
    sio = client.get_client()

    while True:
        menu_str = [f"{item[0]}: {item[1]}" for item in menu_options.items()]
        for option in menu_str:
            print(option)

        command = input("Command: ")

        try:
            command_int = int(command)
        except Exception as _:
            print("Please select a number from the menu...")
            continue

        if command_int < 0 and command_int > 6:
            print("Too high or too low")
            continue

        elif command_int == 0:
            sio.emit(Events.STOP_ROBOT.value)
            sio.disconnect()
            break

        elif command_int == 1:
            target_position = positions[0]
            sio.emit(Events.MOVE_TO_POSITION.value, {
                "position": target_position,
                "speed": 0.3,
                "acceleration": 0.3
            })
            
        elif command_int == 2:
            target_position = positions[1]
            sio.emit(Events.MOVE_TO_POSITION.value, {
                "position": target_position,
                "speed": 0.3,
                "acceleration": 0.3
            })

        elif command_int == 3:
            target_position = positions[2]
            sio.emit(Events.MOVE_TO_POSITION.value, {
                "position": target_position,
                "speed": 0.3,
                "acceleration": 0.3
            })

        elif command_int == 4:
            target_position = positions[3]
            sio.emit(Events.MOVE_TO_POSITION.value, {
                "position": target_position,
                "speed": 0.3,
                "acceleration": 0.3
            })

        elif command_int == 5:
            speed = input("Select speed (0.01-1.0)")
            try:
                speed_int = float(speed)
            except Exception as _:
                print("Command failed. Selected a number between 0.01 to 1.0..")
                continue
            
            sio.emit(Events.SPEED_VALUE.value, {"speed": speed_int})
            response = sio.receive()
            print(f"Running {response['running']} value: {response['operation']}")
        
        elif command_int == 6:
            def callback(response):
                print(response)
            response = sio.emit(Events.IS_RUNNING.value, {}, callback=callback)
            print(response)
        elif command_int == 7:
            sio.emit(Events.STOP_ROBOT.value)            
        elif command_int == 8:
            client.open_gripper()
        elif command_int == 9:
            client.close_gripper()
        else:
            continue 


if __name__ == "__main__":
    #main()
    menu()
