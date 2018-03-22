#include <Arduino.h>

#include <Wire.h>
#define PH_ADDRESS 99
#define EC_ADDRESS 100
#define DO_ADDRESS 97

uint8_t trial = 0;
char response_code = 0;
char sensor_data[20];
char in_char = 0;
uint8_t i = 0;
uint16_t acquisition_time = 900;

float ph_float;
float do_float;
float ec_float;

float read_value(uint8_t sensor);

void setup() {
	Serial.begin(9600);
	Wire.begin();
}

void loop() {
	ph_float = read_value(PH_ADDRESS);
	do_float = read_value(DO_ADDRESS);
	ec_float = read_value(EC_ADDRESS);

	Serial.print(String(ph_float) + '\t');
	Serial.print(String(do_float) + '\t');
	// Serial.print(String(ec_float));
	Serial.println('');

	delay(1000);
}

float read_value(uint8_t sensor) {
	for (int i=0; i<20; i++) {
		sensor_data[i] = 0;
	}

	do {
		Wire.beginTransmission(sensor);
		Wire.write("R");
		Wire.endTransmission();

		delay(acquisition_time);

		Wire.requestFrom(sensor, 20, 1);
		response_code = Wire.read();

		while (Wire.available()) {
			in_char = Wire.read();
			sensor_data[i] = in_char;
			i++;
			if (in_char == 0) {
				i = 0;
				Wire.endTransmission();
				break;
			}
		}

		trial++;				// If it fails to read a value
		if (trial == 5) {		// 	it tries five more times
			trial = 0;
			break;
	 	}

	} while (response_code != 1);

	return atof(sensor_data);
}
