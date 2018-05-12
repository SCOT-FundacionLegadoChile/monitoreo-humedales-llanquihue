#!/usr/bin/python

import os
import time
import serial
import gw_utils
import gw_config
import traceback
from paqueteLoRa import PaqueteLoRa

ser = serial.Serial('/dev/serial0', 9600)

time.sleep(2)

ser.write("config-mod+2+")

time.sleep(1)

tab = "\t"
data_header = "node_id" + tab + "date" + tab + "time" + tab + "timestamp" + tab + "pack_num" + tab + "rssi" + tab + "sensor_value" + tab + "temperature" + tab + "humidity" + tab + "sensor_msg" + tab + "sensor_battery"

if not os.path.isdir("/home/pi/data"):
	os.system("mkdir /home/pi/data")
gw_utils.initFileStructure(gw_config.nodes_ids, gw_config.data_header)


try:
	while 1:
		arduino_msg = ser.readline()
		print "rx", " ",

		#se quita '\n' final
		arduino_msg = arduino_msg.split('\n')[0]

		tag = arduino_msg[:4]
		msg = arduino_msg[5:]

		if tag == "info":
			info = msg
			print "info: " + info

		elif tag == "lora":
			lora_msg = PaqueteLoRa(msg)
			lora_msg.printPacket()
			lora_msg.storePacket()


except Exception as e:
	print 'Error: ' + e.message
	print 'Traceback' + traceback.format_exc()

ser.close()
