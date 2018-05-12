//////////////////////////////////////////
//
//  Nombre del nodo:
//
// String node_id = "las_ranas_maullin";
// String node_id = "las_ranas_mirador";
// String node_id = "las_ranas_1";
// String node_id = "los_helechos_1";
// String node_id = "el_loto_plaza";
// String node_id = "el_loto_werner";
// String node_id = "el_loto_isla";
// String node_id = "baquedano_pasarela";
// String node_id = "sarao_1";
String node_id = "prueba";
//
//////////////////////////////////////////
//
//  Sensores y variables:
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
#define rx 7 //4
#define tx 6 //3
SoftwareSerial SSerial(rx, tx);

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

void setup() {
  Serial.begin(9600);
  SSerial.begin(9600);

  sensorstring.reserve(30);

  //Disminuimos consumo setiando pines a un estado
  pinMode(3, OUTPUT); pinMode(4, OUTPUT); pinMode(8, OUTPUT);
  pinMode(14, OUTPUT); pinMode(15, OUTPUT); pinMode(16, OUTPUT);
  pinMode(17, OUTPUT); pinMode(18, OUTPUT); pinMode(19, OUTPUT);

  //SETUP WATCHDOG TIMER
  WDTCSR = (24);//change enable and WDE - also resets
  WDTCSR = (33);//prescalers only - get rid of the WDE and WDCE bit
  WDTCSR |= (1<<6);//enable interrupt mode

  //Disable ADC - don't forget to flip back after waking up if using ADC in your application ADCSRA |= (1 << 7);
  ADCSRA &= ~(1 << 7);

  //ENABLE SLEEP - this enables the sleep mode
  SMCR |= (1 << 2); //power down mode
  SMCR |= 1;//enable sleep
  
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
  rf95.setTxPower(23);

  if (error != "ok") {
    while(1);
    Serial.print("fail");
  }
  
    Serial.print("wuju");

  delay(5000);
  SSerial.print("Status\r");
  delay(3000);
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
        String(temp)  + tab + 
        sensorvalue   + tab + 
        String(hum)   + tab + 
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

  delay(2000);

  for (i=0; i<1; i++) { //148 ~= 20 min
    __asm__ __volatile__("sleep");
  }
  
  SSerial.print(".\r"); delay(50); // *WA
  SSerial.print("Status\r");
}

ISR(WDT_vect){
}// watchdog interrupt

