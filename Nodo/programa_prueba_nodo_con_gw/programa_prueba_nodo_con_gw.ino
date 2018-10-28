//////////////////////////////////////////
//
//  Conexiones
//
//                 Arduino      inAir4 inAir9
//                 GND----------0V   (ground in)
//                 3V3----------3.3V (3.3V in)
// interrupt 0 pin D2-----------D0   (interrupt request out)
//          SS pin D10----------CS   (CS chip select in)
//         SCK pin D13----------CK   (SPI clock in)
//        MOSI pin D11----------SI   (SPI Data in)
//        MISO pin D12----------SO   (SPI Data out)
//       reset pin D9-----------RST  (RST)
//
//                              DHT
//                 D5-----------out
//
//                              EZO Circuit
//  SSerial Rx pin D7-----------Tx
//  SSerial Tx pin D6-----------Rx
//
//////////////////////////////////////////

/* LoRa */
#include <SPI.h>
#include <RH_RF95.h>

#define RFM95_INT 2
#define RFM95_CS 10
#define RFM95_RST 9
#define RF95_FREQ 915.0

RH_RF95 rf95(RFM95_CS, RFM95_INT);

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
uint8_t i;

uint8_t node_count = 0;
String node_ids[6] = {"prueba",
                      "sarao_1",
                      "baquedano_pasarela",
                      "el_loto_isla",
                      "el_loto_werner",
                      "los_helechos_1"};

void setup() {
  Serial.begin(9600);

  randomSeed(analogRead(0));

  // inAir9 manual reset
  digitalWrite(RFM95_RST, LOW);  delay(10);
  digitalWrite(RFM95_RST, HIGH); delay(10);

  //   rf95.setTxPower(10)       -> use PA_BOOST transmitter pin. +5 to +23 (for modules that use PA_BOOST)            <- INAIR9B.
  //   rf95.setTxPower(10, true) -> use PA_RFO   transmitter pin. -1 to +14 (for modules that use RFO transmitter pin) <- INAIR9.
  String error = "ok";
  if (error == "ok" && !rf95.init())                        error = "LoRa radio initialization failed";
  if (error == "ok" && !rf95.setFrequency(RF95_FREQ))       error = "Frequency configuration failed";
  if (error == "ok" && !rf95.setModemConfig(RH_RF95::mod2)) error = "LoRa mod configuration error";
  rf95.setTxPower(23);

  if (error != "ok") {
    while(1);
    Serial.print("fail");
  }
  
  Serial.print("wuju");

  delay(5000);
}

void loop() {
  sensorvalue = "no_value";
  message = "no_msg";
  
  aux = String(n)     + tab + 
        "prueba"      + tab + //node_ids[node_count]    + tab + 
        String(random(10,28))   + tab + //String(temp)  + tab + 
        String(random(1,5))     + tab + //sensorvalue   + tab + 
        String(random(50,100))  + tab + //String(hum)   + tab + 
        message;

  n++;
  node_count++;
  if (node_count == 6) {
    node_count = 0;
  }

  uint8_t len = aux.length() + 1;
  char payload[len];
  aux.toCharArray(payload, len);

  rf95.send((uint8_t *)payload, len);
  delay(10);
  rf95.waitPacketSent();
  rf95.sleep();

  Serial.println(aux);
  
  delay(50000);
  //while(Serial.available())
}

