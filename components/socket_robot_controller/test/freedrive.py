import rtde_control
import rtde_io as rio
import rtde_receive


IP = "192.168.1.100"
rtde_c = rtde_control.RTDEControlInterface(IP)
rtde_r = rtde_receive.RTDEReceiveInterface(IP)
rtde_io = rio.RTDEIOInterface(IP)

rtde_c.freedriveMode()

while True:
    a = input("Press enter to print position")
    if a == "q":
        break
    print(rtde_r.getActualTCPPose())

rtde_c.endFreedriveMode()