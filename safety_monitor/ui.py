import sys
import cv2
import numpy as np
import requests
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton
from PyQt5.QtCore import QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap, QFont
import pyqtgraph as pg
import asyncio
import aiohttp
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'utils')))
from safety_monitor_prev import RobotSafetyMonitor

class DataFetchThread(QThread):
    new_data_signal = pyqtSignal(int)

    async def fetch_data_from_api(self):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get("https://jiranek-chochola.cz/die-experts/index.php?limit=1") as response:
                    response.raise_for_status()
                    data = await response.json()
                    if data:
                        heart_rate = int(data[0]["heartRate"])
                        self.new_data_signal.emit(heart_rate)
            except Exception as e:
                print(f"Error fetching data from API: {e}")

    async def run_fetch_loop(self):
        while True:
            await self.fetch_data_from_api()
            await asyncio.sleep(1)

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.run_fetch_loop())
        loop.close()

class CameraGraphApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Initialize the safety monitor and the PyQtGraph plot widget
        #self.monitor = RobotSafetyMonitor()
        #self.monitor.set_robot_tcp([-0.45057, -0.34136,  0.66577, -0.46792,  1.23244,  2.73046])

        # Toggle variables
        self.draw_circles = True
        self.draw_text = True
        self.draw_rectangles = True

        # Set up PyQtGraph with a modern style
        pg.setConfigOptions(antialias=True)
        self.graph_widget = pg.PlotWidget(title="Live Heart Rate Graph")
        self.graph_widget.setBackground('#2E2E2E')
        self.graph_data = [0] * 100
        self.graph_plot = self.graph_widget.plot(self.graph_data, pen=pg.mkPen('cyan', width=3))

        # Set up the camera feed display
        self.camera_label = QLabel(self)
        self.camera_label.setFixedSize(640, 480)
        self.camera_label.setStyleSheet("border: 2px solid #4c4c4c;")

        # Buttons to toggle drawing options
        self.toggle_circles_btn = QPushButton("Toggle Circles", self)
        self.toggle_circles_btn.clicked.connect(self.toggle_circles)
        
        self.toggle_text_btn = QPushButton("Toggle Text", self)
        self.toggle_text_btn.clicked.connect(self.toggle_text)

        self.toggle_rectangles_btn = QPushButton("Toggle Rectangles", self)
        self.toggle_rectangles_btn.clicked.connect(self.toggle_rectangles)

        # Style the buttons for a modern look
        button_style = """
            QPushButton {
                background-color: #3A3A3A;
                color: white;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #5A5A5A;
            }
        """
        self.toggle_circles_btn.setStyleSheet(button_style)
        self.toggle_text_btn.setStyleSheet(button_style)
        self.toggle_rectangles_btn.setStyleSheet(button_style)

        # Layout for buttons in a column next to the camera feed
        button_layout = QVBoxLayout()
        button_layout.addWidget(self.toggle_circles_btn)
        button_layout.addWidget(self.toggle_text_btn)
        button_layout.addWidget(self.toggle_rectangles_btn)
        button_layout.addStretch(1)

        # Layout for the camera feed and buttons side by side
        camera_layout = QHBoxLayout()
        camera_layout.addWidget(self.camera_label)
        camera_layout.addLayout(button_layout)

        # Main layout with graph at the bottom
        main_layout = QVBoxLayout()
        main_layout.addLayout(camera_layout)
        main_layout.addWidget(self.graph_widget)

        # Set up main widget
        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        main_widget.setStyleSheet("background-color: #2E2E2E;")
        self.setCentralWidget(main_widget)

        # Timer for updating the camera feed
        self.camera_timer = QTimer()
        self.camera_timer.timeout.connect(self.update_camera_feed)
        self.camera_timer.start(30)

        # Asynchronous data fetch thread
        self.data_thread = DataFetchThread()
        self.data_thread.new_data_signal.connect(self.update_graph_data)
        self.data_thread.start()

        # Customize window title and font
        self.setWindowTitle("Camera and Heart Rate Display")
        self.setStyleSheet("font-size: 11pt; color: #FFFFFF;")
        self.setFont(QFont('Arial', 10))

    def update_camera_feed(self):

        patch_coords_list = [
                (166, 203, 18, 12), # Component 1
                (152, 223, 18, 12), 
                (133, 243, 18, 12), 
                (113, 265, 18, 12) # Component 4
            ]

        #_, _, color_image, _, _ = self.monitor.monitor_safety(
        #    patch_coords_list, draw_circles=self.draw_circles, draw_text=self.draw_text, draw_rectangles=self.draw_rectangles
        #)
        #color_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)
        #h, w, ch = color_image.shape
        #bytes_per_line = ch * w
        #qimg = QImage(color_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        #self.camera_label.setPixmap(QPixmap.fromImage(qimg))

    def update_graph_data(self, heart_rate):
        self.graph_data = self.graph_data[1:] + [heart_rate]
        self.graph_plot.setData(self.graph_data)

    # Toggle functions
    def toggle_circles(self):
        self.draw_circles = not self.draw_circles

    def toggle_text(self):
        self.draw_text = not self.draw_text

    def toggle_rectangles(self):
        self.draw_rectangles = not self.draw_rectangles

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CameraGraphApp()
    window.resize(900, 750)
    window.show()
    sys.exit(app.exec_())
