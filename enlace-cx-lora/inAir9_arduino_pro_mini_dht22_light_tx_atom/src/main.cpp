// Código de prueba inAir9 (SX1276)
// Tx
//
// Conexiones ------------
//                        |
//                        v
//             Arduino          inAir4 inAir9
//                 GND----------0V   (ground in)
//                 3V3----------3.3V (3.3V in)
// interrupt 0 pin D2-----------D0   (interrupt request out)
//          SS pin D10----------CS   (CS chip select in)
//         SCK pin D13----------CK   (SPI clock in)
//        MOSI pin D11----------SI   (SPI Data in)
//        MISO pin D12----------SO   (SPI Data out)
//       reset pin D9-----------RST  (RST)
//
//                              DHT22
//                 GND----------NEG (ground in)
//                 3V3----------POS (3.3V in)
//             pin D5-----------OUT (data out)
//
//                              photo-resistor
//                 GND----------resistor (ground in)
//                 3V3----------photo-resistor (3.3V in)
//             pin A2-----------resistor + photo-resistor (data out)
//
// For PlatformIO
#include <Arduino.h>

bool transmit = false;
const bool VERBOSE = false;

void verbosePrint(String msgOut) {
    if (VERBOSE)
        Serial.print(msgOut);
}

void verbosePrintln(String msgOut) {
    if (VERBOSE)
    Serial.println(msgOut);
}

/*
 * sx1276
 */
#include <SPI.h>
#include <RH_RF95.h>

#define RFM95_INT 2
#define RFM95_CS 10
#define RFM95_RST 9
#define RF95_FREQ 915.0

RH_RF95 rf95(RFM95_CS, RFM95_INT);

//char payload[23] = "Decir adios es crecer ";
//String msg = "Lo que puede llegar a ocurrir en la crisis energetica galactica";
uint8_t node_id = 2;
String msg = "que ocurre con las garzas";
String aux;
unsigned long n = 0;


/*
 * sensors
 */
#define BUTTON_PIN 3
#define LED_PIN 7
unsigned long lastDebounceTime = 0;
unsigned long debounceDelay = 100;

bool virtual_channel_jamming_off = true;

// DHT22 & Light
#include "DHT.h"
#define DHT_PIN 5     // what digital pin we're connected to
#define DHT_TYPE DHT22   // DHT 22  (AM2302), AM2321
DHT dht(DHT_PIN, DHT_TYPE);

#define LIGHT_PIN A2

float hum, temp, light;

// Temperatura
#include "Wire.h"
#define TMP102 72

#include "Adafruit_BMP280.h"
Adafruit_BMP280 bmp; // I2C

// Time
unsigned long time1;
unsigned long time2;
unsigned long total_time;
String tab = String("\t");

// Various vars
bool newCmd = false;
String cmd;

void onClick();

void setup() {
	Serial.begin(115200);
	Wire.begin();

    pinMode(LED_PIN, OUTPUT);
    digitalWrite(LED_PIN, virtual_channel_jamming_off);
    pinMode(BUTTON_PIN, INPUT_PULLUP);
    attachInterrupt(1, onClick, FALLING);

    pinMode(LIGHT_PIN, INPUT);
    pinMode(DHT_PIN, INPUT);
    dht.begin();

    pinMode(RFM95_RST, OUTPUT);
    digitalWrite(RFM95_RST, HIGH);

    // inAir9 manual reset
    digitalWrite(RFM95_RST, LOW);  delay(10);
    digitalWrite(RFM95_RST, HIGH); delay(10);

    String error = "ok";

    // Configuring 915 MHz band
    //   defaults config <434.0MHz, modulation GFSK_Rb250Fd250, +13dbM>
    // Configuring Tx power
    //   rf95.setTxPower(10)       -> use PA_BOOST transmitter pin. +5 to +23 (for modules that use PA_BOOST)            <- INAIR9B.
    //   rf95.setTxPower(10, true) -> use PA_RFO   transmitter pin. -1 to +14 (for modules that use RFO transmitter pin) <- INAIR9.

    if (error == "ok" && !rf95.init())                        error = "LoRa radio initialization failed";
    if (error == "ok" && !rf95.setFrequency(RF95_FREQ))       error = "Frequency configuration failed";
	// mod10 + CRC disable
	//uint8_t register_1D = 0b10010010; // Bw (7-4), CR (3-1), ImplicitHeaderModeOn (0)
    //uint8_t register_1E = 0b01110000; // SF (7-4), TxContinuousMode (3), RxPayloadCrcOn (2), SymbTimeout(1-0)
    //rf95.configureLoraRegs(register_1D, register_1E);
    if (error == "ok" && !rf95.setModemConfig(RH_RF95::mod10)) error = "LoRa mod configuration error";

    rf95.setTxPower(5,true);

    if (error != "ok") {
        verbosePrintln("Error: " + error);
        while(1);
    }

    verbosePrintln("LoRa is ready!");
    verbosePrintln("Freq: " + String(RF95_FREQ) + "MHz");
    verbosePrintln("Tx Pow:" + String(10) + "dBm");


	//if (!bmp.begin()) {
	//    Serial.println(F("Could not find a valid BMP280 sensor, check wiring!"));
	//    while (1);
	//}


    verbosePrintln("Begining Tx...\n");
}

void serialEvent() {
      cmd = Serial.readStringUntil('+');
      newCmd = true;
}

void onClick() {
    if ((millis() - lastDebounceTime) > debounceDelay) {
        virtual_channel_jamming_off = !virtual_channel_jamming_off;
        digitalWrite(LED_PIN, virtual_channel_jamming_off);
    }

    lastDebounceTime = millis();
}

void executeCommand(String command) {
    int n_command = 0;
    if      (command == "start") {n_command = 1;}
    else if (command == "stop")  {n_command = 2;}

    switch(n_command) {
		case 1: // start
		{
		    String boost = Serial.readStringUntil('+');
		    String power = Serial.readStringUntil('+');
		    String mod = Serial.readStringUntil('+');

		    if (boost.toInt() == 1) rf95.setTxPower(power.toInt());
		    else                    rf95.setTxPower(power.toInt(),true); // 2nd arg 'useRFO'

		    switch(mod.toInt()){
		        case 0: { rf95.setModemConfig(RH_RF95::mod0); break;}
		        case 1: { rf95.setModemConfig(RH_RF95::mod1); break;}
		        case 2: { rf95.setModemConfig(RH_RF95::mod2); break;}
		        case 3: { rf95.setModemConfig(RH_RF95::mod3); break;}
		        case 4: { rf95.setModemConfig(RH_RF95::mod4); break;}
		        case 5: { rf95.setModemConfig(RH_RF95::mod5); break;}
		        case 6: { rf95.setModemConfig(RH_RF95::mod6); break;}
		        case 7: { rf95.setModemConfig(RH_RF95::mod7); break;}
		        case 8: { rf95.setModemConfig(RH_RF95::mod8); break;}
		        case 9: { rf95.setModemConfig(RH_RF95::mod9); break;}
		        case 10:{ rf95.setModemConfig(RH_RF95::mod10);break;}
		    }

		    String bost;
		    if (boost.toInt() == 1) bost = "boost";
		    else                    bost = "rf0";

		    verbosePrintln("OK, lora -> " + bost + ", " + power + "dBm, mod" + mod);

		    transmit = true;
		    verbosePrintln("Transmiting...");

			break;
		}
		case 2: // stop
		{
			transmit=false;
			verbosePrintln("stopped transmiting.");
			break;
		}
		default:
		{
			verbosePrintln("ERROR, invalid cmd");
			break;
		}
	}

	// flush serial buffer
	while(Serial.available())
		Serial.read();

	newCmd = false;
	cmd = "";
}

float getTemp102(){
  byte firstbyte, secondbyte; //these are the bytes we read from the TMP102 temperature registers
  int val;
  float convertedtemp;

  Wire.beginTransmission(TMP102); //Say hi to the sensor.
  Wire.write(0x00);
  Wire.endTransmission();
  Wire.requestFrom(TMP102, 2);
  Wire.endTransmission();


  firstbyte      = (Wire.read());
  secondbyte     = (Wire.read());

  val = ((firstbyte) << 4);
  val |= (secondbyte >> 4);
  convertedtemp = val*0.0625;

  return convertedtemp;
}

void loop() {
	if (newCmd) {
		executeCommand(cmd);
	}

	if (transmit) {
		//light = analogRead(LIGHT_PIN);
		//hum = dht.readHumidity();
		//temp = dht.readTemperature();

		temp = getTemp102();

		hum = random(100);//bmp.readTemperature(); //*C
    	light = 22;//random(100);//bmp.readPressure(); // Pa
		//bmp.readAltitude(1013.25);

		//msg.concat(String(n));
		aux = String(n) + tab +
          String(light) + tab +
          String(hum) + tab +
          String(temp) + tab +
          msg;
	  	//aux = aux + tab + aux;

		uint8_t len = aux.length() + 1;
		char payload[len];
		aux.toCharArray(payload, len);
		n++;

		send_packet:

		verbosePrint(String(millis()) + "\tTx, payload: <\t");// + String(payload));
		time1 = millis();

		if (virtual_channel_jamming_off) {
			rf95.send((uint8_t *)payload, len);
			delay(10);
			rf95.waitPacketSent();

			Serial.print(payload);
		}

		//time2 = millis();
		total_time = millis() - time1;
		verbosePrint("\t>, tx time:\t" + String(total_time) + "\tms");
		Serial.write(10);
		delay(5000);

		// wait for response
		/*delay(10);

		tic = micros();
		boolean acked = false;
		do {
			if (rf95.available() {
				// Should be a reply message for us now
				if (rf95.recv(buf, &len)) {
					// Serial.print("Got reply: ");
					// Serial.println((char*)buf);
					// Serial.print("RSSI: ");
					// Serial.println(rf95.lastRssi(), DEC);

					uint8_t l = sizeof(buf);
					uint8_t lls = 0;
					for(uint32_t i=0; i<l; i++) {
						if (buf[i] == node_id)
							lls++;
					}

					if (lls > (l/2)) {
						acked = true;
					}
				}
			}
			delay(10);
		} while(micros()-tic < total_time + 2000);
		*/
	}
}
