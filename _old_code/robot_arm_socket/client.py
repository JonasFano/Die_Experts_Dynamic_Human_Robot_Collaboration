import socketio
from events import Events, menu_options  # Import the shared enum

# Initialize Socket.IO client
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


positions = [
        [1.172, -1.2148, 1.7949, -0.6192, -0.1986, 0.0382],
        [0.432, -1.2148, 1.7949, -0.6191, -0.1987, 0.0383],
        [-0.4789, -1.0999, 1.5347, -0.6192, -0.1987, 0.0383],
        [-0.3862, -0.2917, 0.1344, -0.0297, -0.1996, 0.0383]
]

def main():
    server_url = "http://localhost:5000"  # Replace with your server URL
    sio.connect(server_url)

    try:
        # Move to a position
        target_position = positions[-2]
        sio.emit(Events.MOVE_TO_POSITION.value, {
            "position": target_position,
            "speed": 0.3,
            "acceleration": 0.3
        })


        # Wait for the movement to complete
        sio.sleep(5)

        # Request joint positions
        sio.emit(Events.GET_JOINT_POSITIONS.value)

        # Wait for the response
        sio.sleep(2)

        target_position = positions[-1]
        sio.emit(Events.MOVE_TO_POSITION.value, {
            "position": target_position,
            "speed": 0.3,
            "acceleration": 0.3
        })

        # Wait for the movement to complete
        sio.sleep(5)

        # Request joint positions
        sio.emit(Events.GET_JOINT_POSITIONS.value)

        # Wait for the response
        sio.sleep(2)

        # Stop the robot
        sio.emit(Events.STOP_ROBOT.value)

    finally:
        sio.disconnect()

def menu():
    server_url = "http://localhost:5000"  # Replace with your server URL
    sio.connect(server_url)

    while True:
        menu_str = [f"{item[0]}: {item[1]}" for item in menu_options.items()]
        print(menu_str)

        command = input("Command: ")

        try:
            command_int = int(command)
        except Exception as _:
            print("Please select a number from the menu...")
            continue

        if command_int < 0 and command_int > 6:
            print("Too high or too low")
            continue

        if command_int == 0:
            sio.emit(Events.STOP_ROBOT.value)
            sio.disconnect()
            break

        if command_int == 1:
            target_position = positions[0]
            sio.emit(Events.MOVE_TO_POSITION.value, {
                "position": target_position,
                "speed": 0.3,
                "acceleration": 0.3
            })
            
        if command_int == 2:
            target_position = positions[1]
            sio.emit(Events.MOVE_TO_POSITION.value, {
                "position": target_position,
                "speed": 0.3,
                "acceleration": 0.3
            })

        if command_int == 3:
            target_position = positions[2]
            sio.emit(Events.MOVE_TO_POSITION.value, {
                "position": target_position,
                "speed": 0.3,
                "acceleration": 0.3
            })

        if command_int == 4:
            target_position = positions[3]
            sio.emit(Events.MOVE_TO_POSITION.value, {
                "position": target_position,
                "speed": 0.3,
                "acceleration": 0.3
            })

        if command_int == 5:
            speed = input("Select speed (0.01-1.0)")
            try:
                speed_int = float(speed)
            except Exception as _:
                print("Command failed. Selected a number between 0.01 to 1.0..")
                continue
            
            sio.emit(Events.SPEED_VALUE.value, {"speed": speed_int})
        
        if command_int == 6:
            sio.emit(Events.IS_RUNNING.value)

        if command_int == 7:
            sio.emit(Events.STOP_ROBOT.value)

if __name__ == "__main__":
    #main()
    menu()
