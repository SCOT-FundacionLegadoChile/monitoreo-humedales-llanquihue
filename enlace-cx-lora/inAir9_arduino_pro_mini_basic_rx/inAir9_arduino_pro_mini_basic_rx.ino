// Código de prueba inAir9 (SX1276)
// Rx
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

#define RFM95_INT 2
#define RFM95_CS 10
#define RFM95_RST 9
#define RF95_FREQ 915.0
RH_RF95 rf95(RFM95_CS, RFM95_INT);

#define LED 13

void setup() {
  Serial.begin(9600);
  pinMode(LED, OUTPUT);
  pinMode(RFM95_RST, OUTPUT);
  digitalWrite(RFM95_RST, HIGH);

  // inAir9 manual reset
  digitalWrite(RFM95_RST, LOW);  delay(10);
  digitalWrite(RFM95_RST, HIGH); delay(10);

  // inAir9 initializing
  while (!rf95.init()) {
    Serial.println("Error: inAir9 initialization failed.");
    while (1);
  }
  Serial.println("\ninAir9 ready!");

  // Configuring 915 MHz band
  //   defaults config <434.0MHz, modulation GFSK_Rb250Fd250, +13dbM>
  if (!rf95.setFrequency(RF95_FREQ)) {
    Serial.println("Error: inAir9 frequency configuration failed");
    while (1);
  }
  Serial.print("inAir9 freq: "); Serial.println(RF95_FREQ);

  // Configuring LoRa <B,SF,CR>
  if (!rf95.setModemConfig(RH_RF95::mod10)) {
    Serial.println("Error: inAir9 LoRa params configuration error");
    while(1);
  }
  Serial.println("inAir9 LoRa mod10");

  Serial.println("inAir9 listening ...\n");
}

void loop() {
  if (rf95.available()) {
    Serial.print(millis()); Serial.print(" Rx");
    
    uint8_t buf[RH_RF95_MAX_MESSAGE_LEN];
    uint8_t len = sizeof(buf);

    if (rf95.recv(buf, &len)) {
      //RH_RF95::printBuffer("Received: ", buf, len);
      
      Serial.print(", payload: "); Serial.print((char*)buf);
      Serial.print(", rssi: "); Serial.println(rf95.lastRssi(), DEC);
      
      // Send a reply
      //  uint8_t data[] = "And hello back to you";
      //  rf95.send(data, sizeof(data));
      //  rf95.waitPacketSent();
      //  Serial.println("Sent a reply");
      //  digitalWrite(LED, LOW);
    } else {
      Serial.println(" failed.");
    }    
  }
}

