from .client import RobotSocketClient
from .events import Events


class RobotMenu:
    positions = [
        [-0.14073875492311985, -0.1347932873639663, 0.50, -1.7173584058437448, 2.614817123624442, 0.015662793265223476],
        [-0.5765337725404966, 0.24690845869221661, 0.28, -1.7173584058437448, 2.614817123624442, 0.015662793265223476],
        [-0.11416495380452188, -0.6366095280680834, 0.25, -1.7173584058437448, 2.614817123624442, 0.015662793265223476],
        [-0.07957651394105475, -0.5775855654308832, 0.25, -1.7060825343589325, 2.614852489706341, 0.022595902601295428],
        [-0.04925448702503588, -0.5082985306025327, 0.25, -1.7261076468170813, 2.623645026630323, 0.0023482443015084543], 
    ]

    menu_options = {
        0: "Stop and Disconnect",
        1: "Move to position",
        2: "Set speed",
        3: "Check if running",
        4: "Stop robot",
        5: "Open gripper",
        6: "Close gripper",
        7: "Get TCP pose"
    }

    def __init__(self, server_url: str, client_class):
        self.client = client_class(server_url)
        self.sio = self.client.get_client()

    def run(self):
        max_command = max(self.menu_options.keys())
        while True:
            self.print_menu()
            command_int = self.get_command()


            if command_int is None:
                print("Please select a number from the menu...")
                continue

            if command_int < 0 or command_int > max_command:
                print("Too high or too low")
                continue

            if command_int == 0:
                self.stop_robot_and_disconnect()
                break

            elif command_int  == 1:
                while True:
                    try:
                        print("Select position:")
                        print("0) Exit")
                        for i in range(1, len(self.positions)+1):
                            print(f"{i}) Position") 
                        
                        position_index = int(input("Select: "))
                        if position_index == 0:
                            break
                        print(position_index)
                        print(self.move_to_position(position_index - 1))
                        break
                    except Exception:
                        print("Write a valid number")
                
            elif command_int == 2:
                self.set_speed()

            elif command_int == 3:
                self.check_if_running()

            elif command_int == 4:
                self.sio.emit(Events.STOP_ROBOT.value)

            elif command_int == 5:
                print(self.client.open_gripper())
                
            elif command_int == 6:
                print(self.client.close_gripper())

            elif command_int == 7:
                print(self.client.get_tcp_pose())

            else:
                print(f"Command {command_int} has not been registered yet")

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
