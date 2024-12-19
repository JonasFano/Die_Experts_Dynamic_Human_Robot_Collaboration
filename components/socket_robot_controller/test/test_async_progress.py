import threading
from socket_robot_controller.client import RobotSocketClient
from shared.interpolate import interpolate_joint_positions
import time

client = RobotSocketClient()

def print_progress(c: RobotSocketClient):
    while True:
        print(f"Progress {c.get_async_progress()}")
        time.sleep(0.1)



threading.Thread(target=print_progress, args=(client,)).start()
left = [-0.7936861961531458, 0.1345208677156332, 0.20121193043062877, 1.1699186936945596, -2.8533212546104387, 0.03498279477610326] 
right = [-0.0478652061102549, -0.5543761199523133, 0.18625675585468152, -2.675987463798992, 1.130718964904632, -0.06266753642526122] 
inter_1 = [-0.5233737985443254, -0.1327023600841468, 0.12760996243660583, 1.6409461753248429, -2.6576221330257113, 0.08272675494556461]
inter_2 = [-0.4268266227721198, -0.3307839848188225, 0.12783709763407114, 2.156008410285979, -2.274461019909372, 0.086462066397168]
inter_3 = [-0.22035444113270958, -0.4763358964950922, 0.14467730168837914, 2.6172269067364504, -1.7022307298591368, 0.08076196211917594]

left_arr = [left,inter_2, right]
[item.extend([1, 1]) for item in left_arr]

right_arr = list(reversed(left_arr))


left_interpolated = interpolate_joint_positions(right, left)
right_interpolated = interpolate_joint_positions(right, left)
[item.extend([0.5, 0.05, 0.3]) for item in left_interpolated]
[item.extend([0.5, 0.05, 0.3]) for item in right_interpolated]

print("Going to left side.")
while True:
    client.moveL_path(left_arr)
    input("Press enter to go the right side")
    client.moveL_path(right_arr)
    input("Press enter to go the left side")