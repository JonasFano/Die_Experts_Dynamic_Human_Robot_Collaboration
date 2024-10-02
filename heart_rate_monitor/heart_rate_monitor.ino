#include <SPI.h>

const int csPin = 10;  // Chip Select/Slave Select (DV10)
const int sensorValuePin = 11;  // Data from sensor (SDO)

void setup() {
  pinMode(csPin, OUTPUT);  // Chip select pin as output
  digitalWrite(csPin, HIGH);  // Deselect the sensor initially

  pinMode(LED_BUILTIN, OUTPUT);

  SPI.begin();  // Initialize SPI communication
  Serial.begin(9600);  // Start serial communication for output
}

void loop() {
  digitalWrite(csPin, LOW);  // Select the sensor
  byte sensorData = SPI.transfer(0x00);  // Read sensor data by sending dummy byte

  digitalWrite(csPin, HIGH);  // Deselect the sensor

  Serial.println(sensorData);  // Output sensor data to serial monitor

  delay(1000); 
}
