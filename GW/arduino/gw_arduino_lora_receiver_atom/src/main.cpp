// https://learn.sparkfun.com/tutorials/using-the-arduino-pro-mini-33v
// Powering arduino 5V with 3V3: https://arduino.stackexchange.com/questions/4950/powering-a-5v-arduino-pro-mini-with-3-3v

/***************************************************************
*
*  Matías Macaya L.
*  keny92@gmail.com
*
*  Arduino sketch for the lora receiver of the GW for llanquihue's
* smart-wetland monitoring platform.
*
*  The gateway its composed of (1) a Rasperry Pi 3 saving local data
*  and uploading it to the cloud, plus other services. And (2) an
*  arduino serving as lora receiver and passing comunication data to
*  the raspi.
*
*  Conexiones ------------------
*                               |
*                               v
*            (Arduino) Teensy      inAir4 inAir9
*                      GND----------0V   (ground in)
*                      3V3----------3.3V (3.3V in)
*      interrupt 0 pin D2-----------D0   (interrupt request out)
*               SS pin D10----------CS   (CS chip select in)
*              SCK pin D13----------CK   (SPI clock in)
*             MOSI pin D11----------SI   (SPI Data in)
*             MISO pin D12----------SO   (SPI Data out)
*            reset pin D9-----------RST  (RST)
*
*  Comandos "at" disponibles:
*    Command             Function                 Params            Syntax (always end's with '+')
*    at                  check if ok              -                 at+
*    begin               start listening          -                 begin+
*    stop                stop receiving           -                 stop+
*    send                send lora packet         Message           send+decir adios es crecer+
*    config-mod          configure lora mod       Mod               config-mod+5+
*    config-params       configure lora params    BW, CR, SF        config-params+125+4/5+7+
*    sleep               enter sleep mode         -                 sleep+
*    config-tx-power     configure tx power       Tx Power          config-tx-power+13+
*
*****************************************************************/
// For PlatformIO
#include <Arduino.h>

// SX1276 libraries
#include <SPI.h>
#include <RH_RF95.h>

#define RFM95_CS 10
#define RFM95_RST 9
#define RFM95_INT 2

#define RF95_FREQ 915.0

RH_RF95 rf95(RFM95_CS, RFM95_INT);

// Second serial library
#include <DHT.h>

// Various vars
bool newCmd = false;
String cmd;

bool listening = true;

int packetNumber;
int lastRSSI = 0;
int lastPacketNumber = 0;
int lastPacketSentDuration = 0;

const String LORA_TAG = "lora\t";
const String INFO_TAG = "info\t";

void setup() {
	Serial.begin(9600); delay(100);

	pinMode(RFM95_RST, OUTPUT);
	digitalWrite(RFM95_RST, HIGH); delay(100);

	digitalWrite(RFM95_RST, LOW); delay(10);
	digitalWrite(RFM95_RST, HIGH); delay(10);

	String error = "ok";

	if (error == "ok" && !rf95.init())                        error = "LoRa radio initialization failed";
	if (error == "ok" && !rf95.setFrequency(RF95_FREQ))       error = "Frequency configuration failed";
	if (error == "ok" && !rf95.setModemConfig(RH_RF95::mod10)) error = "LoRa mod configuration error";

	if (error != "ok") {
		Serial.print(INFO_TAG);
		Serial.println("Error: " + error);
		while(1);
	}

	Serial.print(INFO_TAG);
	Serial.println("LoRa is ready!");
	Serial.print(INFO_TAG);
	Serial.println("Freq: " + String(RF95_FREQ) + "MHz");
}

void serialEvent() {
	cmd = Serial.readStringUntil('+');
	newCmd = true;
}

void configureLoraMod(int modmod) {
	switch(modmod) {                                        // <BW,     CR,  SF>
		case 0: { rf95.setModemConfig(RH_RF95::mod0); break;} //
		case 1: { rf95.setModemConfig(RH_RF95::mod1); break;} //  125kHz, 4/5, 12
		case 2: { rf95.setModemConfig(RH_RF95::mod2); break;} //  250kHz, 4/5, 12
		case 3: { rf95.setModemConfig(RH_RF95::mod3); break;} //  125kHz, 4/5, 10
		case 4: { rf95.setModemConfig(RH_RF95::mod4); break;} //  500kHz, 4/5, 12
		case 5: { rf95.setModemConfig(RH_RF95::mod5); break;} //  250kHz, 4/5, 10
		case 6: { rf95.setModemConfig(RH_RF95::mod6); break;} //  500kHz, 4/5, 11
		case 7: { rf95.setModemConfig(RH_RF95::mod7); break;} //  250kHz, 4/5, 9
		case 8: { rf95.setModemConfig(RH_RF95::mod8); break;} //  500kHz, 4/5, 9
		case 9: { rf95.setModemConfig(RH_RF95::mod9); break;} //  500kHz, 4/5, 8
		case 10: { rf95.setModemConfig(RH_RF95::mod10); break;} //500kHz, 4/5, 7
	}
}

void configureLoraParams(String bandWidth, String codingRate, String spreadingFactor) {
	uint8_t bw, cr, sf;
	bool invalid = false;

	float n_bw = bandWidth.toFloat();
	switch((int) n_bw*100) {                // BW
		case 780:   {bw = 0b00000000; break;} // 7.8 kHz
		case 1040:  {bw = 0b00010000; break;} // 10.4 kHz
		case 1560:  {bw = 0b00100000; break;} // 15.6 kHz
		case 2080:  {bw = 0b00110000; break;} // 20.8 kHz
		case 3125:  {bw = 0b01000000; break;} // 31.25 kHz
		case 4170:  {bw = 0b01010000; break;} // 41.7 kHz
		case 6250:  {bw = 0b01100000; break;} // 62.5 kHz
		case 12500: {bw = 0b01110000; break;} // 125 kHz
		case 25000: {bw = 0b10000000; break;} // 250 kHz
		case 50000: {bw = 0b10010000; break;} // 500 kHz
		default: {invalid = true; break;}
	}

	char n_cr = codingRate.charAt(2);
	switch(n_cr) {                        // CR
		case '5': {cr = 0b00000010; break;} // 4/5
		case '6': {cr = 0b00000100; break;} // 4/6
		case '7': {cr = 0b00000110; break;} // 4/7
		case '8': {cr = 0b00001000; break;} // 4/8
		default: {invalid = true; break;}
	}

	int n_sf = spreadingFactor.toInt();
	switch(n_sf) {                       // SF
		case 6:  {sf = 0b01100100; break;} // 6
		case 7:  {sf = 0b01110100; break;} // 7
		case 8:  {sf = 0b10000100; break;} // 8
		case 9:  {sf = 0b10010100; break;} // 9
		case 10: {sf = 0b10100100; break;} // 10
		case 11: {sf = 0b10110100; break;} // 11
		case 12: {sf = 0b11000100; break;} // 12
		default: {invalid = true; break;}
	}

	if (!invalid) {
		uint8_t register_1D = bw | cr;
		uint8_t register_1E = sf;

		rf95.configureLoraRegs(register_1D, register_1E);
	} else {
		Serial.print(INFO_TAG);
		Serial.println("Error: Invalid lora params");
		return;
	}
}

void sendLoraPacket(String msg) {
	uint8_t len = msg.length() + 1;
	char payload[len];
	msg.toCharArray(payload, len);

	unsigned long time1 = micros();

	rf95.send((uint8_t *)payload, len);
	delay(10);
	rf95.waitPacketSent();

	unsigned long time2 = micros();
	lastPacketSentDuration = time2 - time1;
}

void executeCommand(String command) {
	int n_command = 0;
	if      (command == "at")            {n_command = 1;}
	else if (command == "begin")         {n_command = 2;}
	else if (command == "stop")          {n_command = 3;}
	else if (command == "send")          {n_command = 4;}
	else if (command == "config-mod")    {n_command = 5;}
	else if (command == "config-params") {n_command = 6;}
	else if (command == "sleep")         {n_command = 7;}
	else if (command == "config-tx-pow") {n_command = 8;}

	switch(n_command) {
		case 1: // at
		{
			Serial.print(INFO_TAG);
			Serial.println("OK");
			break;
		}
		case 2: // begin
		{
			rf95.setModeRx();
			listening = true;
			Serial.print(INFO_TAG);
			Serial.println("OK, Rx mode");
			break;
		}
		case 3: // stop
		{
			rf95.setModeIdle(); // stdby mode, msgs should not be received
			listening = false;
			Serial.print(INFO_TAG);
			Serial.println("OK, Stdby mode");
			break;
		}
		case 4: // send
		{
			String message = Serial.readStringUntil('+');
			sendLoraPacket(message);
			Serial.print(INFO_TAG);
			Serial.println("OK, '" + message + "' sent");
			break;
		}
		case 5: // config-mod
		{
			int mod = Serial.readStringUntil('+').toInt();
			configureLoraMod(mod);
			Serial.print(INFO_TAG);
			Serial.println("OK, mod " + String(mod));
			break;
		}
		case 6: // config-params
		{
			String bw = Serial.readStringUntil('+');
			String cr = Serial.readStringUntil('+');
			String sf = Serial.readStringUntil('+');
			configureLoraParams(bw, cr, sf);
			Serial.print(INFO_TAG);
			Serial.println("OK, <" + bw + ", " + cr + ", " + sf + ">");
			break;
		}
		case 7: // sleep
		{
			// TODO: Averiguar más sobre el modo 'sleep' del sx1276, ya que parece existe
			// un tiempo máximo luego del cual se despieerta automáticamente para escuchar.
			rf95.sleep();
			Serial.print(INFO_TAG);
			Serial.println("OK, sleep mode");
			break;
		}
		case 8: // config-tx-pow
		{
			// Se asume que ocupamos boost mode
			String power = Serial.readStringUntil('+');
			rf95.setTxPower(power.toInt(), false);
			Serial.print(INFO_TAG);
			Serial.println("OK, tx power " + power + "dBm");
			break;
		}
		default:
		{
			Serial.print(INFO_TAG);
			Serial.println("ERROR, invalid cmd");
			break;
		}
	}

	// flush serial buffer
	while(Serial.available()) {
		Serial.read();
	}

	newCmd = false;
	cmd = "";
}

void printPreviousPacketsNotReceived(uint32_t n) {
	// Print previous packets not received
	if (lastPacketNumber != 0) {
		for (uint32_t i=lastPacketNumber+1; i<n; i++) {
			Serial.print(LORA_TAG);
			Serial.print(""); Serial.print("\tRx\t"); Serial.println(i);
		}
	}
}

void loop() {
	if (newCmd) {
		executeCommand(cmd);
	}

	if (rf95.available() && listening) {
		uint8_t buf[RH_RF95_MAX_MESSAGE_LEN];
		uint8_t len = sizeof(buf);

		if (rf95.recv(buf, &len)) {
			// Check & Print packets not received
			uint8_t c;
			for(uint32_t i=0; i<sizeof(buf); i++) {
				if ((c = buf[i]) == '\t')
					break;
				packetNumber = packetNumber * 10 + (c - 48);
			}

			if (packetNumber != lastPacketNumber + 1) {
				printPreviousPacketsNotReceived(packetNumber);
			}
			lastPacketNumber = packetNumber;
			packetNumber = 0;

			lastRSSI = rf95.lastRssi();
			Serial.print(LORA_TAG);
			Serial.print(
			String(millis()) + "\t" +
			"Rx" + "\t" +
			String(lastPacketNumber) + "\t" +
			"payload" + "\t" +
			"<" + "\t" +
			String((char*) buf) + "\t" +
			">" + "\t" +
			"rssi" + "\t" +
			String(lastRSSI) + "\n"
			);

			// Send a reply
			uint8_t data[] = "And hello back to you";
			//rf95.send(data, sizeof(data));
			//rf95.waitPacketSent();
			//Serial.println("Sent a reply");
			//digitalWrite(LED, LOW);

		} else {
			Serial.println("\tfailed");
		}
	}
}
