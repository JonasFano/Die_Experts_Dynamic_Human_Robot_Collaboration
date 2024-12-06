from client import RobotSocketClient
from events import Events


class RobotMenu:
    positions = [
        [1.172, -1.2148, 1.7949, -0.6192, -0.1986, 0.0382],
        [0.432, -1.2148, 1.7949, -0.6191, -0.1987, 0.0383],
        [-0.4789, -1.0999, 1.5347, -0.6192, -0.1987, 0.0383],
        [-0.3862, -0.2917, 0.1344, -0.0297, -0.1996, 0.0383],
    ]

    menu_options = {
        0: "Stop and Disconnect",
        1: "Move to position 1",
        2: "Move to position 2",
        3: "Move to position 3",
        4: "Move to position 4",
        5: "Set speed",
        6: "Check if running",
        7: "Stop robot",
        8: "Open gripper",
        9: "Close gripper",
    }

    def __init__(self, server_url: str, client_class):
        self.client = client_class(server_url)
        self.sio = self.client.get_client()

    def run(self):
        while True:
            self.print_menu()
            command_int = self.get_command()

            if command_int is None:
                print("Please select a number from the menu...")
                continue

            if command_int < 0 or command_int > 9:
                print("Too high or too low")
                continue

            if command_int == 0:
                self.stop_robot_and_disconnect()
                break

            elif command_int in [1, 2, 3, 4]:
                print(self.move_to_position(command_int - 1))

            elif command_int == 5:
                self.set_speed()

            elif command_int == 6:
                self.check_if_running()

            elif command_int == 7:
                self.sio.emit(Events.STOP_ROBOT.value)

            elif command_int == 8:
                print(self.client.open_gripper())

            elif command_int == 9:
                print(self.client.close_gripper())

    def print_menu(self):
        menu_str = [f"{item[0]}: {item[1]}" for item in self.menu_options.items()]
        for option in menu_str:
            print(option)

    def get_command(self) -> int:
        command = input("Command: ")
        try:
            return int(command)
        except ValueError:
            return None

    def stop_robot_and_disconnect(self):
        self.client.stop
        self.sio.disconnect()

    def move_to_position(self, index: int):
        target_position = self.positions[index]
        return self.client.moveL(target_position, 0.3, 0.3)

    def set_speed(self):
        speed = input("Select speed (0.01-1.0): ")
        try:
            speed_float = float(speed)
        except ValueError:
            print("Command failed. Select a number between 0.01 to 1.0.")
            return

        response = (Events.SET_SPEED_VALUE.value, {"speed": speed_float})
        print(f"Response: {response}")

    def check_if_running(self):
        print(self.client.is_running())


if __name__ == "__main__":
    server_url = "http://localhost:5000"  # Adjust as needed
    menu = RobotMenu(server_url=server_url, client_class=RobotSocketClient)
    menu.run()
