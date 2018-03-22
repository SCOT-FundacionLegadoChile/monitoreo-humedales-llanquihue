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
float hum;
float temp;

long j = 0;

float read_value(uint8_t sensor);

#include "DHT.h"
#define DHT_PIN 5     // what digital pin we're connected to
#define DHT_TYPE DHT22   // DHT 22  (AM2302), AM2321
DHT dht(DHT_PIN, DHT_TYPE);

void setup() {
	Serial.begin(9600);
	Wire.begin();

  pinMode(DHT_PIN, INPUT);
  dht.begin();
}

void loop() {
  hum = dht.readHumidity();
  temp = dht.readTemperature();
  
  do_float = read_value(DO_ADDRESS);
  ec_float = read_value(EC_ADDRESS);
	ph_float = read_value(PH_ADDRESS);

  Serial.print(String(j) + '\t');
	Serial.print(String(ph_float) + '\t');
	Serial.print(String(do_float) + '\t');
  Serial.print(String(ec_float) + '\t');
  Serial.print(String(temp) + '\t');
  Serial.print(String(hum) + '\t');
	Serial.print('\n');

	delay(3000);
  j++;
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

    if (sensor == EC_ADDRESS) {
		  Wire.requestFrom(sensor, 48, 1);
    } else {
      Wire.requestFrom(sensor, 20, 1);
    }
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
