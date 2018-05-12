
import os

def internet_on():
    try:
        urllib2.urlopen('http://216.58.192.142', timeout=1)
        return True
    except urllib2.URLError as err:
        return False

def checkInternetConnectionRestart():
	if NON_STOP_INTERNET_CONN_TRY:
	    for i in range(3):
	        if internet_on():
	            break
	        else:
	            if (i == 2):
	                os.system('sudo reboot')
	            time.sleep(20)

def initFileStructure(nodes_ids, data_header):
	# Check if all files and directories are created
	# tempdata & data for all nodes_ids
	# .
	# |-data
	# |---data_sarao_1.txt
	# |---data_los_helechos_1.txt
	# |---data_el_loto_werner.txt
	# |---data_el_loto_isla.txt
	# |---data_baquedano_pasarela.txt
	# |---data_prueba.txt
	# |---temp_data_sarao_1.txt
	# |---temp_data_los_helechos_1.txt
	# |---temp_data_el_loto_werner.txt
	# |---temp_data_el_loto_isla.txt
	# |---temp_data_baquedano_pasarela.txt
	# |---temp_data_prueba.txt
	# |-gw2.py
	# |-gw_bot.py
	# |-gw_utils.py
	# |-gw_config.py
	# |-paqueteLoRa.py
	# |-uploadGSheets.py
	# |-creds.py
	# \-PruebaPaginaHumedales-7d3cc40aae82.json

	if not os.path.isdir("/home/pi/data"):
		os.system("mkdir /home/pi/data")
	for node in nodes_ids:
		if not os.path.exists("/home/pi/data/data_{}.txt".format(node)):
			os.system("echo {} > /home/pi/data/data_{}.txt".format(data_header, node))
		if not os.path.exists("/home/pi/data/temp_data_{}.txt".format(node)):
			os.system("echo {} > /home/pi/data/temp_data_{}.txt".format(data_header, node))
