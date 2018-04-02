//////////////////////////////////////////
// String node_id = "las_ranas_maullin";
// String node_id = "las_ranas_mirador";
// String node_id = "las_ranas_1";
// String node_id = "los_helechos_1";
// String node_id = "el_loto_plaza";
// String node_id = "el_loto_werner";
String node_id = "el_loto_isla";
// String node_id = "baquedano_pasarela";
// String node_id = "sarao_1";
//////////////////////////////////////////
//
//// Tº H 
//// EC, OD, T, pH
//
// EC + 
// Total dissolved solids
// Salinity
// Specific gravity (sea water only)
//
//////////////////////////////////////////

/* Temp & Hum */
#include "DHT.h"
#define DHT_PIN 5
#define DHT_TYPE DHT22
DHT dht(DHT_PIN, DHT_TYPE);

/* LoRa */
#include <SPI.h>
#include <RH_RF95.h>

#define RFM95_INT 2
#define RFM95_CS 10
#define RFM95_RST 9
#define RF95_FREQ 915.0

RH_RF95 rf95(RFM95_CS, RFM95_INT);

/* SoftwareSerial */
#include <SoftwareSerial.h>
#define rx 4
#define tx 3
SoftwareSerial SSerial(rx, tx);

#include <Vcc.h>
Vcc vcc(1.0);

/* Variables */
float hum;
float temp;
float vin;
String sensorstring = "";
boolean sensor_string_complete = false;
String sensorvalue = "";

String aux;
unsigned long n = 0;
String message;
String tab = String("\t");

void setup() {
  //Serial.begin(9600);
  SSerial.begin(9600);

  sensorstring.reserve(30);

  pinMode(DHT_PIN, INPUT);
  dht.begin();

  // inAir9 manual reset
  digitalWrite(RFM95_RST, LOW);  delay(10);
  digitalWrite(RFM95_RST, HIGH); delay(10);

  //   rf95.setTxPower(10)       -> use PA_BOOST transmitter pin. +5 to +23 (for modules that use PA_BOOST)            <- INAIR9B.
  //   rf95.setTxPower(10, true) -> use PA_RFO   transmitter pin. -1 to +14 (for modules that use RFO transmitter pin) <- INAIR9.
  String error = "ok";
  if (error == "ok" && !rf95.init())                        error = "LoRa radio initialization failed";
  if (error == "ok" && !rf95.setFrequency(RF95_FREQ))       error = "Frequency configuration failed";
  if (error == "ok" && !rf95.setModemConfig(RH_RF95::mod2)) error = "LoRa mod configuration error";
  rf95.setTxPower(14);

  if (error != "ok") {
    while(1);
  }

  delay(5000);
  SSerial.print("Status\r");
  delay(2000);
}

boolean isNumeric(String str) {
    unsigned int stringLength = str.length();
 
    if (stringLength == 0) {
        return false;
    }
 
    boolean seenDecimal = false;
 
    for(unsigned int i = 0; i < stringLength; ++i) {
        if (isDigit(str.charAt(i))) {
            continue;
        }
 
        if (str.charAt(i) == '.') {
            if (seenDecimal) {
                return false;
            }
            seenDecimal = true;
            continue;
        }
        return false;
    }
    return true;
}

void loop() {
  sensorvalue = "no_value";
  message = "no_msg";
  SSerial.print("R\r");            // *value *OK
  
  hum = dht.readHumidity();
  temp = dht.readTemperature();
  vin = vcc.Read_Volts();

  delay(1000); // 800 + 200 ms

  while(SSerial.available()) {
    sensorstring = SSerial.readStringUntil(13);
    
    if (isNumeric(sensorstring)) {
      sensorvalue = sensorstring;
    } else {
      message = sensorstring;
    }
  }
  
  aux = String(n)     + tab + 
        node_id       + tab + 
        String(hum)   + tab + 
        String(temp)  + tab + 
        sensorvalue   + tab + 
        String(vin)   + tab + 
        message;

  uint8_t len = aux.length() + 1;
  char payload[len];
  aux.toCharArray(payload, len);
  n++;

  rf95.send((uint8_t *)payload, len);
  delay(10);
  rf95.waitPacketSent();

  SSerial.print("Sleep\r");  // *SL
  rf95.sleep();

  delay(1200000);
  
  SSerial.print(".\r"); delay(50); // *WA
  SSerial.print("Status\r");
}

