import socketio
import rtde_control
import rtde_receive
import rtde_io
from events import Events  # Import the shared enum

# Initialize Socket.IO server
sio = socketio.Server(async_mode='eventlet')
app = socketio.WSGIApp(sio)

# Robot control variables
ROBOT_HOST = "192.168.1.100"  # Replace with your robot's IP
rtde_control = rtde_control.RTDEControlInterface(ROBOT_HOST)
rtde_receive = rtde_receive.RTDEReceiveInterface(ROBOT_HOST)
i_rtde_io = rtde_io.RTDEIOInterface(ROBOT_HOST)

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

@sio.on(Events.MOVE_TO_POSITION.value)
def move_to_position_blend(sid, data):
    try:
        position = data.get("position", [])
        speed = data.get("speed", 0.5)
        acceleration = data.get("acceleration", 0.3)
        blend = data.get("blend", 0.1)

        if len(position) != 6:
            raise ValueError("Invalid position format. Must be a list of 6 values.")

        print(f"Moving to position: {position}")
        blended_position = [].extend(position, [speed, acceleration, blend])
        rtde_control.moveJ(blended_position, asynchronous=True)
        sio.emit(Events.SERVER_MESSAGE.value, {'status': 'Movement complete'}, to=sid)
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
        i_rtde_io.setSpeedSlider(speed)
    except Exception as e:
        sio.emit(Events.SERVER_MESSAGE.value, {'status': f"Error: {str(e)}"}, to=sid)

@sio.on(Events.IS_RUNNING.value)
def get_status(sid):
    operation = rtde_control.getAsyncOperationProgress()
    running = True 
    if operation < 0:
        running = False

    sio.emit(Events.SERVER_MESSAGE.value, {"running": running, "value": operation}, to=sid)

@sio.on(Events.GET_TCP_VALUE.value)
def get_tcp_value(sid):
    sio.emit(Events.SERVER_MESSAGE.value, {"tcp_pose": rtde_receive.getActualTCPPose()})


if __name__ == "__main__":
    import eventlet
    import eventlet.wsgi

    print("Starting Socket.IO server...")
    eventlet.wsgi.server(eventlet.listen(("0.0.0.0", 5000)), app)