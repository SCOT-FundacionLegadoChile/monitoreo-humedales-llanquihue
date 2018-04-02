// 
//
//////////////////////////////////////////
// String node_id = "las_ranas_maullin";
// String node_id = "las_ranas_mirador";
// String node_id = "las_ranas_1";
// String node_id = "los_helechos_1";
// String node_id = "el_loto_plaza";
String node_id = "el_loto_werner";
// String node_id = "el_loto_isla";
// String node_id = "baquedano_pasarela";
// String node_id = "sarao_1";
//////////////////////////////////////////

String inputstring = "";
String sensorstring = "";
boolean input_string_complete = false;
boolean sensor_string_complete = false;
float temperature;
float hum;
float temp;

//#include <SoftwareSerial.h>
//#define rx 3
//#define tx 4
//SoftwareSerial myserial(rx, tx);

#include "DHT.h"
#define DHT_PIN 5
#define DHT_TYPE DHT22
DHT dht(DHT_PIN, DHT_TYPE);

/* sx1276*/
#include <SPI.h>
#include <RH_RF95.h>

#define RFM95_INT 2
#define RFM95_CS 10
#define RFM95_RST 9
#define RF95_FREQ 915.0

RH_RF95 rf95(RFM95_CS, RFM95_INT);

String aux;
unsigned long n = 0;

unsigned long time1;
unsigned long time2;
String tab = String("\t");

#include "LowPower.h"

#include <Vcc.h>
Vcc vcc(1.0);
float v;

void setup() {
	Serial.begin(9600);

  //myserial.begin(9600);
  inputstring.reserve(10);
  sensorstring.reserve(30);

  pinMode(DHT_PIN, INPUT);
  dht.begin();

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
  if (error == "ok" && !rf95.setModemConfig(RH_RF95::mod2)) error = "LoRa mod configuration error";
  rf95.setTxPower(13,true);

  if (error != "ok") {
  //  Serial.println("Error: " + error);
    while(1);
  }
}

void serialEvent() {
  sensorstring = Serial.readStringUntil(13);
  sensor_string_complete = true;
}

void loop() {
  //if (input_string_complete) {
  //  myserial.print(inputstring);
  //  myserial.print('\r');
  //  inputstring = "";
  //  input_string_complete = false;
  //}

  //if (Serial.available() > 0) {
  //  char inchar = (char) Serial.read();
  //  if (inchar == '\r') {
  //    sensor_string_complete = true;
  //  } else {
  //    sensorstring += inchar;
  //  }
  //}

  if (sensor_string_complete == true) {

    hum = dht.readHumidity();
    temp = dht.readTemperature();

    v = vcc.Read_Volts();

    aux = String(n) + tab + 
          String(hum) + tab + 
          String(temp) + tab + 
          String(sensorstring) + tab + 
          String(v) + tab + 
          node_id;

    uint8_t len = aux.length() + 1;
    char payload[len];
    aux.toCharArray(payload, len);
    n++;

    //Serial.print(String(millis()) + "\tTx, payload: <\t" + String(payload));
    //time1 = micros();

    rf95.send((uint8_t *)payload, len);
    delay(10);
    rf95.waitPacketSent();

    //time2 = micros();
    //Serial.println("\t>, tx time:\t" + String(time2 - time1) + "\tus");

    Serial.print("Sleep\r");
    rf95.sleep();

    delay(5000);
    // delay(1200000);

    Serial.print("R\r");
    sensorstring = "";
    sensor_string_complete = false;
  }
}



//
//  consumo 8.7 mA - 22mA sensor sleep
//          7.0 mA - 20mA sensor inAir9 sleep
//
//

