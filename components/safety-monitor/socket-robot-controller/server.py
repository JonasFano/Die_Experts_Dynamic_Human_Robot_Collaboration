import socketio
import rtde_control
import rtde_receive
import rtde_io
from events import Events  # Import the shared enum

ROBOT_SPEED = 0.5

# Initialize Socket.IO server
sio = socketio.Server(async_mode='eventlet')
app = socketio.WSGIApp(sio)

# Robot control variables
ROBOT_HOST = "192.168.1.100"  # Replace with your robot's IP
rtde_control = rtde_control.RTDEControlInterface(ROBOT_HOST)
rtde_receive = rtde_receive.RTDEReceiveInterface(ROBOT_HOST)
i_rtde_io = rtde_io.RTDEIOInterface(ROBOT_HOST)
i_rtde_io.setSpeedSlider(ROBOT_SPEED)

@sio.event
def connect(sid, environ):
    print(f"Client {sid} connected.")
    sio.emit(Events.SERVER_MESSAGE.value, {'status': 'Connected to Robot Arm Server'}, to=sid)

@sio.event
def disconnect(sid):
    print(f"Client {sid} disconnected.")



@sio.on(Events.MOVE_TO_POSITION.value)
def move_to_position(sid, data):
    try:
        position = data.get("position", [])
        speed = data.get("speed", 0.5)
        acceleration = data.get("acceleration", 0.3)

        if len(position) != 6:
            raise ValueError("Invalid position format. Must be a list of 6 values.")

        print(f"Moving to position: {position}")
        rtde_control.moveJ(position, speed, acceleration, asynchronous=True)
        sio.emit(Events.SERVER_MESSAGE.value, {'status': 'Movement complete'}, to=sid)
    except Exception as e:
        sio.emit(Events.SERVER_MESSAGE.value, {'status': f"Error: {str(e)}"}, to=sid)

#@sio.on(Events.MOVE_TO_POSITION.value)
def move_to_position_blend(sid, data):
    try:
        position = data.get("position", [])
        speed = data.get("speed", 0.5)
        acceleration = data.get("acceleration", 0.3)
        blend = data.get("blend", 0.1)

        if len(position) != 6:
            raise ValueError("Invalid position format. Must be a list of 6 values.")

        print(f"Moving to position: {position}")
        blended_position = []
        blended_position.extend(position)
        blended_position.extend([speed, acceleration, blend])
        print(blended_position)
        rtde_control.moveJ(blended_position, asynchronous=True)
        print("Done moving")
        sio.emit(Events.SERVER_MESSAGE.value, {'status': 'Movement complete'}, to=sid)
        print("Done with emitting")
    except Exception as e:
        sio.emit(Events.SERVER_MESSAGE.value, {'status': f"Error: {str(e)}"}, to=sid)

@sio.on(Events.GET_JOINT_POSITIONS.value)
def get_joint_positions(sid):
    try:
        joint_positions = rtde_receive.getActualQ()
        sio.emit(Events.JOINT_POSITIONS.value, {'positions': joint_positions}, to=sid)
    except Exception as e:
        sio.emit(Events.SERVER_MESSAGE.value, {'status': f"Error: {str(e)}"}, to=sid)


@sio.on(Events.STOP_ROBOT.value)
def stop_robot(sid):
    try:
        rtde_control.stopL()
        sio.emit(Events.SERVER_MESSAGE.value, {'status': 'Robot stopped'}, to=sid)
    except Exception as e:
        sio.emit(Events.SERVER_MESSAGE.value, {'status': f"Error: {str(e)}"}, to=sid)


@sio.on(Events.SPEED_VALUE.value)
def set_speed(sid, data):
    try:
        speed = data.get("speed", 0.5)
        print(f"Speed being set is {speed}")
        ROBOT_SPEED = speed
        i_rtde_io.setSpeedSlider(ROBOT_SPEED)
    except Exception as e:
        sio.emit(Events.SERVER_MESSAGE.value, {'status': f"Error: {str(e)}"}, to=sid)

@sio.on(Events.IS_RUNNING.value)
def get_status(sid):
    operation = rtde_control.getAsyncOperationProgress()
    running = True 
    if operation < 0:
        running = False

    sio.emit(Events.IS_RUNNING.value, {"running": running, "value": operation}, to=sid)

@sio.on(Events.GET_TCP_VALUE.value)
def get_tcp_value(sid):
    sio.emit(Events.SERVER_MESSAGE.value, {"tcp_pose": rtde_receive.getActualTCPPose()})


@sio.on(Events.SPEED_VALUE.value)
def get_speed_value(sid):
    sio.emit(Events.SPEED_VALUE.value, {"speed": ROBOT_SPEED}, to=sid)

@sio.on(Events.SET_GRIPPER.value)
def set_gripper_value(sid, data):
    return i_rtde_io.setStandardDigitalOut(0, data["open"])

def stop_server():
    global server_thread
    if server_thread is not None:
        print("Stopping server...")
        server_thread.kill()  # Stop the server greenthread
        server_thread = None
        print("Server stopped.")


if __name__ == "__main__":
    import eventlet
    import eventlet.wsgi

    try:
        print("Starting Socket.IO server...")
        eventlet.wsgi.server(eventlet.listen(("0.0.0.0", 5000)), app)
    except KeyboardInterrupt:
        stop_server()
        