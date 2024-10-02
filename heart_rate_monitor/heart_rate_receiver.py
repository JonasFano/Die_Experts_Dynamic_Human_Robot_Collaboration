import serial
import time

# Establish a serial connection with Arduino
arduino = serial.Serial('COM3', 9600, timeout=1)
time.sleep(2)

# Example function to control UR5 robot
def control_ur5(sensor_data):
    print(f"Controlling UR5 with sensor data: {sensor_data}")


try:
    while True:
        if arduino.in_waiting > 0:
            sensor_data = arduino.readline().decode('utf-8').strip() 
            if sensor_data.isdigit():
                control_ur5(int(sensor_data))
        time.sleep(1)

except KeyboardInterrupt:
    print("Program stopped")

finally:
    arduino.close()
