#!/usr/bin/python

import os
import sys
import time
import creds
import serial
import gw_bot
import gw_utils
import gw_config
import traceback
import threading
import uploadGSheets
from functools import wraps
from paqueteLoRa import PaqueteLoRa
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Initialize serial port
ser = serial.Serial('/dev/serial0', 9600)
time.sleep(2)
ser.write("config-mod+2+")
time.sleep(1)

# Check if all files and directories are created
gw_utils.initFileStructure(gw_config.nodes_ids, gw_config.data_header)

# Schedule data upload every 20 minutes
def uploadData ():
	print "stackoverflow"

	uploadGSheets.upload()
	os.system("rm /home/pi/data/temp_**")
	gw_utils.initFileStructure(gw_config.nodes_ids, gw_config.data_header)

	threading.Timer(600, uploadData).start ()
uploadData ()

# Initialize telegram methods
# TELEGRAM funcs
global TELEGRAM_VERBOSE
global LIST_OF_ADMINS
global FIRMWARE_DOWNLOAD_URL
global FIRMWARE_FILE_NAME
TELEGRAM_VERBOSE = False
idMati = creds.TELEGRAM_ADMIN_ID
botKey = creds.TELEGRAM_BOT_GW_PRUEBA_KEY
updater = Updater(botKey)
LIST_OF_ADMINS = [int(idMati)]
FIRMWARE_DOWNLOAD_URL = "https://www.dropbox.com/s/gg13mo2a517yxmc/prueba_telegram_bot.py"
FIRMWARE_FILE_NAME = "Archivo.zip"

def restricted(func):
    @wraps(func)
    def wrapped(bot, update, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in LIST_OF_ADMINS:
            print("Unauthorized access denied for {}.".format(user_id))
            return
        return func(bot, update, *args, **kwargs)
    return wrapped


def start(bot, update):
    update.message.reply_text('Hi!')


def help(bot, update):
    update.message.reply_text(help_message())

@restricted
def stop(bot, update):
    update.message.reply_text('Stopping bot!')
    updater.stop()
    print 'Telegram Bot stopped!! (by user ' + update.message.from_user.first_name + ')'
    sys.exit()

def mod(bot, update):
    try:
        lora_mod = max(0, min(int(update.message.text[5:]), 10))
        command =  "config-mod+{}+".format(lora_mod)
        if RASPI:
            ser.write(command)
        update.message.reply_text(command)
    except:
        print 'Error: Invalid /mod command'
        update.message.reply_text('Error: Invalid /mod command')

def reboot(bot, update):
    update.message.reply_text('Restarting GW');
    #update.message.reply_text(str(datetime.datetime.now()))
    os.system('sudo reboot')

def verbose(bot, update):
	global TELEGRAM_VERBOSE
	if TELEGRAM_VERBOSE:
		TELEGRAM_VERBOSE = False
		update.message.reply_text('Cashate... Silence everything about LoRa communication')
	else:
		TELEGRAM_VERBOSE = True
		update.message.reply_text('Aaaaaaa... Printing everything about LoRa communication')

def updateFirmware(bot, update):
	os.system("wget {}".format(FIRMWARE_DOWNLOAD_URL))
	if not os.path.isdir("/home/pi/{}".format(FIRMWARE_FILE_NAME)):
		update.message.reply_text("Error in download")
		return
	os.system("sudo rm /home/pi/{}.py /home/pi/{}.py /home/pi/{}.py /home/pi/{}.py /home/pi/{}.py /home/pi/{}.py /home/pi/{}.py /home/pi/{}.json".format("gw2", "gw_bot", "gw_utils", "gw_config", "paqueteLoRa", "uploadGSheets", "creds", "PruebaPaginaHumedales-7d3cc40aae82"))
	os.system("unzip {}".format(FIRMWARE_FILE_NAME))
	update.message.reply_text("Ready, 'gw.py' updated")
	update.message.reply_text('/reboot for changes to take effect')

def firmwareDownloadURL(bot, update):
	global FIRMWARE_DOWNLOAD_URL
	url = update.message.text[21:]
	FIRMWARE_DOWNLOAD_URL = url
	update.message.reply_text("URL configured ;)")

def firmawareFileName(bot, update):
	global FIRMWARE_FILE_NAME
	name = update.message.text[18:]
	FIRMWARE_FILE_NAME = name
	update.message.reply_text("name configured ;)")

def getFirmwareURL(bot, update):
	global FIRMWARE_DOWNLOAD_URL
	update.message.reply_text("URL: " + FIRMWARE_DOWNLOAD_URL)

def getFirmwareName(bot, update):
	global FIRMWARE_FILE_NAME
	update.message.reply_text("Name: " + FIRMWARE_FILE_NAME)

def addAdmin(bot, update):
	global LIST_OF_ADMINS
	try:
		idd = update.message.text[10:]
		LIST_OF_ADMINS.append(int(idd))
		update.message.reply_text("User added as admin :)")
	except Exception as e:
		update.message.reply_text("Invalid user id :(")

def echo(bot, update):
    update.message.reply_text("echo: " + update.message.text)
    print "\tbot - " + update.message.from_user.first_name + " (" + str(update.message.chat_id) + "): " + update.message.text

def error(bot, update, error):
    print 'Update "%s" caused error "%s", ' + update + ", " + error

def send_message_admins(ttmsg):
	global LIST_OF_ADMINS
	for iid in LIST_OF_ADMINS:
		bot.send_message(chat_id=str(iid), text=ttmsg)


# Initialize telegram bot
bot = updater.bot
dp = updater.dispatcher

dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("help", help))
dp.add_handler(CommandHandler("stop", stop))
dp.add_handler(CommandHandler("mod", mod))
dp.add_handler(CommandHandler("reboot", reboot))
dp.add_handler(CommandHandler("verbose", verbose))
#dp.add_handler(CommandHandler("newTest", newTest))
#dp.add_handler(CommandHandler("getData", getDataFile))
#dp.add_handler(CommandHandler("uploadGSheets", uploadGSheets))
dp.add_handler(CommandHandler("updateFirmware", updateFirmware))
dp.add_handler(CommandHandler("firmwareDownloadURL", firmwareDownloadURL))
dp.add_handler(CommandHandler("firmawareFileName", firmawareFileName))
dp.add_handler(CommandHandler("getFirmwareURL", getFirmwareURL))
dp.add_handler(CommandHandler("getFirmwareName", getFirmwareName))
dp.add_handler(CommandHandler("addAdmin", addAdmin))
dp.add_handler(MessageHandler(Filters.all, echo))
dp.add_error_handler(error)

updater.start_polling()

bot.send_message(chat_id=idMati, text="!Hola aloh")

# Initialize Gateway routine
try:
	while 1:
		arduino_msg = ser.readline()

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
			if TELEGRAM_VERBOSE:
				tmsg = "[" + lora_msg.node_id + " - #" + lora_msg.pack_num + " rssi=" + lora_msg.rssi + " value=" + lora_msg.sensor_value + "]"
				send_message_admins(tmsg)

except Exception as e:
	print 'Error: ' + e.message
	print 'Traceback' + traceback.format_exc()

ser.close()

#####################

def newTest(bot, update):
    os.system('sudo rm /home/pi/data_gw.txt')
    #os.system("echo 'Date\tTime\tuC Clock [ms]\tPacket Number\tPayload\tRSSI [dBm]\tLight [rel]\tHumidity [%]\tTemperature [C]' > /home/pi/data_gw.txt")
    os.system("echo 'Datos almacenados localmente:' > /home/pi/data_gw.txt")
    update.message.reply_text("Rea-dy, 'data_gw.txt' file is clean")

def getDataFile(bot, update):
    bot.sendDocument(chat_id=idMati, document=open('/home/pi/data_gw.txt', 'rb'))

def uploadGSheets(bot, update):
    global UPLOAD_GSHEETS
    if UPLOAD_GSHEETS:
        UPLOAD_GSHEETS = False
        update.message.reply_text('Packets just stored locally')
    else:
        UPLOAD_GSHEETS = True
        update.message.reply_text('Packets will be stored in GSheets too')
