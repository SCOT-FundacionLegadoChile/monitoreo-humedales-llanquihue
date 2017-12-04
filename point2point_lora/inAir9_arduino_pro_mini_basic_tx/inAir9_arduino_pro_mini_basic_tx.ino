// Código de prueba inAir9 (SX1276)
// Tx
//
// Conexiones ------------
//                        |
//                        v
//       (Arduino) Teensy      inAir4 inAir9
//                 GND----------0V   (ground in)
//                 3V3----------3.3V (3.3V in)
// interrupt 0 pin D2-----------D0   (interrupt request out)
//          SS pin D10----------CS   (CS chip select in)
//         SCK pin D13----------CK   (SPI clock in)
//        MOSI pin D11----------SI   (SPI Data in)
//        MISO pin D12----------SO   (SPI Data out)
//       reset pin D9-----------RST  (RST)

#include <SPI.h>
#include <RH_RF95.h>

//#define ARDUINO
#define ESP

#ifdef ARDUINO
#define RFM95_INT 2
#define RFM95_CS 10
#define RFM95_RST 9
#define RF95_FREQ 915.0
#endif
#ifdef ESP
#define RFM95_INT 2  //D4
#define RFM95_CS  15 //D8
#define RFM95_RST 14 //D5
#define RF95_FREQ 915.0
#endif

RH_RF95 rf95(RFM95_CS, RFM95_INT);

//char payload[23]="Decir adios es crecer ";
String msg = "Decir adios es crecer ";
String aux;
unsigned long n = 0;

unsigned long time1;
unsigned long time2;

void setup() {
  Serial.begin(9600);
  pinMode(RFM95_RST, OUTPUT);
  digitalWrite(RFM95_RST, HIGH);

  // inAir9 manual reset
  digitalWrite(RFM95_RST, LOW);  delay(10);
  digitalWrite(RFM95_RST, HIGH); delay(10);

  // inAir9 initializing
  //Serial.println("initializing inAir9 ...");
  while (!rf95.init()) {
    Serial.println("error: inAir9 initialization failed.");
    while (1);
  }
  Serial.println("\ninAir9 ready!");

  // Configuring 915 MHz band
  //   defaults config <434.0MHz, modulation GFSK_Rb250Fd250, +13dbM>
  if (!rf95.setFrequency(RF95_FREQ)) {
    Serial.println("error: inAir9 frequency configuration failed");
    while (1);
  }
  Serial.print("inAir9 freq: "); Serial.println(RF95_FREQ);
  
  // Configuring Tx power
  //   rf95.setTxPower(10)       -> use PA_BOOST transmitter pin. +5 to +23 (for modules that use PA_BOOST)            <- INAIR9B.
  //   rf95.setTxPower(10, true) -> use PA_RFO   transmitter pin. -1 to +14 (for modules that use RFO transmitter pin) <- INAIR9.
  rf95.setTxPower(10,true);
  Serial.println("inAir Tx power: ");

  // Configuring LoRa <B,SF,CR>
  if (!rf95.setModemConfig(RH_RF95::mod10)) {
    Serial.println("error: inAir9 LoRa params configuration error");
    while(1);
  }
  Serial.println("inAir9 LoRa mod");

  Serial.println("Begining Tx...\n");
}

void loop() {
  //msg.concat(String(n));
  aux = msg + n;
  uint8_t len = aux.length() + 1;
  char payload[len];
  aux.toCharArray(payload, len);
  n++;
  
  Serial.print(millis()); Serial.print(" Tx, payload: "); Serial.print(payload);
  time1 = micros();
  
  rf95.send((uint8_t *)payload, len);
  delay(10);
  rf95.waitPacketSent();
  
  time2 = micros();
  Serial.print(", tx time: "); Serial.print(time2 - time1); Serial.println(" us");
  delay(4000);
}
