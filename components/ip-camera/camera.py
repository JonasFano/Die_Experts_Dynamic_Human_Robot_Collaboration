import cv2
from flask import Flask, Response

# Initialize Flask app
app = Flask(__name__)

# Video capture source: 0 for webcam, or replace with video file path
camera = cv2.VideoCapture(0)


def generate_frames():
    """Generator function to yield video frames."""
    while True:
        success, frame = camera.read()  # Read the camera frame
        if not success:
            break
        else:
            # Encode frame as JPEG
            _, buffer = cv2.imencode(".jpg", frame)
            frame = buffer.tobytes()

            # Yield the frame as part of a multipart response
            yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")


@app.route("/video_feed")
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(
        generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@app.route("/")
def index():
    """Home page with embedded video stream."""
    return """
    <html>
        <head>
            <title>IP Camera</title>
        </head>
        <body>
            <h1>Live Video Feed</h1>
            <img src="/video_feed" width="640" height="480">
        </body>
    </html>
    """


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
