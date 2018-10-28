#!/usr/bin/python

import datetime
import time

tab = "\t"

class PaqueteLoRa:
	'Base class for a LoRa packet in MonitoreoHumedalesLlanquihueProject'
	#initialize vars

	#constructor
	def __init__(self, msg):
		msg_list = msg.split("\t")
		# -> 12839950	Rx	63	payload	<	63	prueba	16	1	92	no_msg	>	rssi	-52
		# i: 0          1   2   3       4   5   6       7   8   9   10      11  12      13

		self.date           = str(datetime.datetime.now().date())
		self.time           = str(datetime.datetime.now().time())
		self.timestamp      = str(time.time())
		self.node_id        = msg_list[6]
		self.pack_num       = msg_list[5]
		self.temperature    = msg_list[7]
		self.humidity       = msg_list[9]
		self.sensor_value   = msg_list[8]
		self.sensor_msg     = msg_list[10]
		self.sensor_battery = "-0.0"
		self.rssi           = msg_list[13]

		# node_id, date, time, timestamp, pack_num, rssi, sensor_value, temperature, humidity, sensor_msg, sensor_battery
		self.data           = self.node_id + tab + self.date + tab + self.time + tab + self.timestamp + tab + self.pack_num + tab + self.rssi + tab + self.sensor_value + tab + self.temperature + tab + self.humidity + tab + self.sensor_msg + tab + self.sensor_battery

		#methods
	def printPacket(self):
		print self.node_id + ", " + self.timestamp + ", " + self.pack_num + ", " + self.sensor_value + ", " + self.rssi

	def storePacket(self):
		self.printPreviousLostPackets()
		with open('/home/pi/data/data_' + self.node_id + '.txt', 'a') as file:
			file.write(self.data + "\n")
		with open('/home/pi/data/temp_data_' + self.node_id + '.txt', 'a') as file:
			file.write(self.data + "\n")

	def printPreviousLostPackets(self):
		actual_num = int(self.pack_num)
		nums = []
		nn = 0
		with open('/home/pi/data/temp_data_' + self.node_id + '.txt') as f:
			for line in f:
				nn += 1
				pass
			last = line

		if nn > 2:
			# AQUI, cuando lee la primera linea de header y es la unica,
			# no la interpreta como separada por \t sino por espacios y queda una gran fila
			mlist = last.split("\t")
			mlist = list(filter(None, mlist))
			last_num = mlist[4]

			#prueba	02/11/18	23:12:23	376254673254876523	3	-45	34	23	12	web	0.0

			if actual_num != (int(last_num) + 1):
				with open('/home/pi/data/temp_data_' + self.node_id + '.txt', 'a') as file:
					for i in range(int(last_num)+1, actual_num):
						file.write(voidPacket(self.node_id, i) + "\n")
				with open('/home/pi/data/data_' + self.node_id + '.txt', 'a') as file:
					for i in range(int(last_num)+1, actual_num):
						file.write(voidPacket(self.node_id, i) + "\n")

	def telegramMessage(self):
		return "[" + self.node_id + " - #" + self.pack_num + " rssi=" + self.rssi + " value=" + self.sensor_value + "]"

def voidPacket(pid, n):
	return pid + tab + " " + tab + " " + tab + " " + tab + str(n) + tab + " " + tab + " " + tab + " " + tab + " " + tab + " "
