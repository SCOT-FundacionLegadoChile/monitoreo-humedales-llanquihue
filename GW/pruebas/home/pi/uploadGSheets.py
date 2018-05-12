#!/usr/bin/python

#    # Google Spreadsheets
#    sudo pip uninstall oauth2client
#    sudo pip install oauth2client==1.5.2
#        Previous...
#            pip install --upgrade google-api-python-client
#    pip install PyOpenSSL
#        Previous...
#            sudo apt-get install build-essential libssl-dev libffi-dev python-dev
#            pip install cryptography
#    pip install gspread
#    pip install json

# import uploadGSheets
# import time
# localtime = time.asctime( time.localtime(time.time()) )
# uploadGSheets.test_upload_virtual_data(localtime, 3)

import time
import random
import gspread
import datetime
import gw_config
import numpy as np
from oauth2client.service_account import ServiceAccountCredentials

nodes_ids = gw_config.nodes_ids
node_id2wks_name = gw_config.node_id2wks_name

def upload():
	scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
	credentials = ServiceAccountCredentials.from_json_keyfile_name('PruebaPaginaHumedales-7d3cc40aae82.json', scope)
	gc = gspread.authorize(credentials)
	sps = gc.open("prueba_datos_definitiva")

	for node in nodes_ids:
		wks = sps.worksheet(node_id2wks_name[node])

		with open('/home/pi/data/temp_data_' + node + '.txt') as f:
			nn = 0
			for line in f:
				nn += 1
				if nn == 1:
					continue

				line = line.split('\n')[0]

				mlist = line.split("\t")
				mlist = list(filter(None, mlist))
				mlist.pop(0)
				wks.append_row(mlist)

def test_upload(localtime, t, i):
	## Credentials
	scope = ['https://spreadsheets.google.com/feeds',
				'https://www.googleapis.com/auth/drive']

	credentials = ServiceAccountCredentials.from_json_keyfile_name('PruebaPaginaHumedales-7d3cc40aae82.json', scope)

	## GSheets
	gc = gspread.authorize(credentials)

	# Open a worksheet from spreadsheet with one shot
	wks = gc.open("prueba_si").sheet1

	wks.append_row([localtime, t, i, 'que ocurre baby', 'no', 'baby no', random.randint(10,70), random.random()])
	wks.append_row([localtime, t, i+1, 'que ocurre baby', 'no', 'baby no', random.randint(10,70), random.random()])
	wks.append_row([localtime, t, i+2, 'que ocurre baby', 'no', 'baby no', random.randint(10,70), random.random()])
	wks.append_row([localtime, t, i+3, 'que ocurre baby', 'no', 'baby no', random.randint(10,70), random.random()])
	wks.append_row([localtime, t, i+4, 'que ocurre baby', 'no', 'baby no', random.randint(10,70), random.random()])
	wks.append_row([localtime, t, i+5, 'que ocurre baby', 'no', 'baby no', random.randint(10,70), random.random()])
	wks.append_row([localtime, t, i+6, 'que ocurre baby', 'no', 'baby no', random.randint(10,70), random.random()])
	wks.append_row([localtime, t, i+7, 'que ocurre baby', 'no', 'baby no', random.randint(10,70), random.random()])
	wks.append_row([localtime, t, i+8, 'que ocurre baby', 'no', 'baby no', random.randint(10,70), random.random()])
	wks.append_row([localtime, t, i+9, 'que ocurre baby', 'no', 'baby no', random.randint(10,70), random.random()])

def test_upload_virtual_data(localtime, i):
	## Credentials
	scope = ['https://spreadsheets.google.com/feeds',
				'https://www.googleapis.com/auth/drive']

	credentials = ServiceAccountCredentials.from_json_keyfile_name('PruebaPaginaHumedales-7d3cc40aae82.json', scope)

	gc = gspread.authorize(credentials)
	sps = gc.open("prueba_datos_definitiva")

	mdate = datetime.datetime.now().date()
	mtime = datetime.datetime.now().time()
	mtimestamp = time.time()

	for node in nodes_ids:
		#wks = sps.worksheet(node_id2wks_name[node])
		wks = sps.sheet1
		wks.append_row([mdate,
						mtime,
						mtimestamp,
						i,
						int(np.random.normal(-87, 5)),      #rssi
						round(np.random.normal(7, 2),1),    #sensor_value
						int(np.random.normal(14, 2)),       #temp
						int(np.random.normal(64, 10)),      #hum
						"no_msg",                           #sensor_msg
						"-0.0"])                            #sensor_battery
