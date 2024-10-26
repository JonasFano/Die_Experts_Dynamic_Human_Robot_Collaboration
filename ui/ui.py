import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from graph import live_update_graph
import cv2
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'utils')))
from safety_monitor import RobotSafetyMonitor  
import threading 
from matplotlib.animation import FuncAnimation
import time

# Initialize the RobotSafetyMonitor class to access the camera
monitor = RobotSafetyMonitor()

def update_camera_feed(ax, fig):
    # Initialize image display on the first frame to avoid clearing in each loop
    too_close, distance, color_image, depth_image, terminate = monitor.monitor_safety([])
    im = ax.imshow(color_image)
    ax.axis('off')

    # Continuous update loop for new frames
    while plt.fignum_exists(fig.number):  
        too_close, distance, color_image, depth_image, terminate = monitor.monitor_safety([])

        # Update only the image data without clearing the axis
        im.set_data(color_image)

        # Redraw the canvas without delay
        fig.canvas.draw_idle()

        if terminate:
            break


def display_layout():
    # Set up the figure and layout
    fig = plt.figure(figsize=(12, 6), facecolor='#1E1E1E')
    gs = gridspec.GridSpec(1, 2, width_ratios=[1, 2])
    gs.update(wspace=0.05)

    # Left panel: Camera feed axis
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.set_facecolor('#1E1E1E')

    # Right panel: Live graph axis
    ax3 = fig.add_subplot(gs[0, 1])
    ax3.set_title("Live Graph", fontsize=12, color='white')
    ax3.set_facecolor('#1E1E1E')

    # Start the camera feed update in a separate thread
    video_thread = threading.Thread(target=update_camera_feed, args=(ax1, fig))
    video_thread.start()

    # Run the live graph in the main thread
    live_update_graph(ax3)

    # Close the video thread once the plot window is closed
    video_thread.join()

if __name__ == "__main__":
    display_layout()