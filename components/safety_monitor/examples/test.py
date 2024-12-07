from safety_minitor import SafetyMonitor
import time

monitor = SafetyMonitor()
monitor.start()

while True:
    result = monitor.get_frames()
    print(result.color_image.shape)
    time.sleep(1)