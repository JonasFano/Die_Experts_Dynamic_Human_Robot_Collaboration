import os
import signal
import socketio
import rtde_control
import rtde_receive
import rtde_io as r_io
from .events import Events  # Import the shared enum
from typing import List
import numpy as np
from flask import Flask

robot_enabled = True
ROBOT_SPEED = 0.5

app = Flask(__name__)
sio = socketio.Server(cors_allowed_origins="*")
app.wsgi_app = socketio.WSGIApp(sio, app.wsgi_app)

# Robot control variables
if robot_enabled:
    ROBOT_HOST = "192.168.1.100"  # Replace with your robot's IP
    rtde_c = rtde_control.RTDEControlInterface(ROBOT_HOST)
    rtde_r = rtde_receive.RTDEReceiveInterface(ROBOT_HOST)
    rtde_io = r_io.RTDEIOInterface(ROBOT_HOST)
    rtde_io.setSpeedSlider(ROBOT_SPEED)



@sio.event
def connect(sid, environ):
    print(f"Client {sid} connected.")
    sio.emit(
        Events.SERVER_MESSAGE.value, {"status": "Connected to Robot Arm Server"}, to=sid
    )


@sio.event
def disconnect(sid):
    print(f"Client {sid} disconnected.")


@sio.on(Events.IS_RUNNING.value)
def is_running(sid) -> bool:
    if robot_enabled:
        operation_prog = rtde_c.getAsyncOperationProgress()
        if operation_prog < 0:
            return False
        else:
            return  True


@sio.on(Events.GET_TCP_VALUE.value)
def get_tcp_pose(sid) -> List[float]:
    print(f"Running: {Events.GET_TCP_VALUE.value}")
    if robot_enabled:
        print("Running with robot")
        positions = rtde_r.getActualTCPPose()
        return positions
    positions = [-0.08, -0.278, -0.151, 1.718, -2.631, -0.023]
    return positions



@sio.on(Events.SET_GRIPPER.value)
def open_gripper(sid, data):
    print(f"Running: {Events.SET_GRIPPER.value}")
    if robot_enabled:
        rtde_io.setStandardDigitalOut(0, data["open"])
    return {"open": data["open"]}


@sio.on(Events.GET_SPEED_VALUE.value)
def get_tcp_velocity(sid):
    print(f"Running: {Events.GET_SPEED_VALUE.value}")
    return {"speed": ROBOT_SPEED}


@sio.on(Events.SET_SPEED_VALUE.value)
def set_robot_velocity(self, data):
    print(f"Running: {Events.SET_SPEED_VALUE.value}")
    speed = data.get("speed", 0.5)
    ROBOT_SPEED = speed
    if robot_enabled:
        rtde_io.setSpeedSlider(ROBOT_SPEED)
    return {"speed": ROBOT_SPEED}


@sio.on(Events.JOINT_POSITIONS.value)
def get_actual_joint_positions(sid):
    print(f"Running: {Events.JOINT_POSITIONS.value}")
    if robot_enabled:
        return {"positions": np.degrees(rtde_r.getActualQ())}
    return [1.0, 2.0, 3.0]


@sio.on(Events.MOVE_TO_POSITION_J.value)
def moveJ_path(sid, data):
    print(f"Running: {Events.MOVE_TO_POSITION_J.value}")
    path = data["positions"]
    if robot_enabled:
        rtde_c.moveJ(path, asynchronous=True)
    return {"positions": path}


@sio.on(Events.MOVE_TO_POSITION_L.value)
def moveL_path(sid, data):
    print(f"Running: {Events.MOVE_TO_POSITION_L.value}")
    path = data["positions"]
    if robot_enabled:
        rtde_c.moveL(path, asynchronous=True)
    return {"positions": path}


@sio.on(Events.MOVE_L_SPEED_ACCEL.value)
def moveL(sid, data):
    print(f"Running: {Events.MOVE_L_SPEED_ACCEL.value}")
    target_pose = data["position"]
    velocity = data["speed"]
    acceleration = data["acceleration"]

    if robot_enabled:
        if is_running(""):
            print("Stopping robot")
            rtde_c.stopL()
        rtde_c.moveL(target_pose, speed=velocity, acceleration=acceleration, asynchronous=True)
    return {"positions": target_pose}


@sio.on(Events.STOP_ROBOT.value)
def stop_robot(sid):
    print(f"Running: {Events.STOP_ROBOT.value}")
    if robot_enabled:
        rtde_c.stopL()


def stopServer():
    os.kill(os.getpid(), signal.SIGINT)

def main():
    import eventlet
    import eventlet.wsgi

    try:
        print("Starting Socket.IO server...")
        eventlet.wsgi.server(eventlet.listen(("0.0.0.0", 5000)), app)
        app.run(port=5000)
    except KeyboardInterrupt:
        app.shutdown()

if __name__ == "__main__":
    main()