#!/usr/bin/python

import os
import sys
import time
import creds ## dev file
import serial
import gw_bot ## dev file
import gw_utils ## dev file
import time
import datetime
import gw_config ## dev file
import traceback
import threading
import uploadGSheets ## dev file
from functools import wraps
from paqueteLoRa import PaqueteLoRa ## dev file
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Initialize serial port
ser = serial.Serial('/dev/serial0', 9600)
time.sleep(2)
ser.write("config-mod+2+")
time.sleep(1)

# Check if all files and directories are created
gw_utils.initFileStructure(gw_config.nodes_ids, gw_config.data_header)

# Schedule data upload every X minutes
def uploadData ():
	print "stackoverflow ", str(datetime.datetime.now().time())[:8]

	try:
		uploadGSheets.upload()
	except Exception as e:
		print 'Error uploading data to gsheets'
		print 'Error: ', e

	os.system("rm /home/pi/data/temp_**")
	gw_utils.initFileStructure(gw_config.nodes_ids, gw_config.data_header)

	threading.Timer(60, uploadData).start () # -> seconds
uploadData ()

# ##### ##### #     ##### ###   #####   #   ## ##
#   #   ###   #     ###   #  ## #####  ###  #####
#   #   ##### ##### ##### ##### # #   #   # #   #
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
FIRMWARE_DOWNLOAD_URL = "not_configured"
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

@restricted
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

@restricted
def reboot(bot, update):
    update.message.reply_text('Restarting GW');
    #update.message.reply_text(str(datetime.datetime.now()))
    os.system('sudo reboot')

@restricted
def verbose(bot, update):
	global TELEGRAM_VERBOSE
	if TELEGRAM_VERBOSE:
		TELEGRAM_VERBOSE = False
		update.message.reply_text('Cashate... Silence everything about LoRa communication')
	else:
		TELEGRAM_VERBOSE = True
		update.message.reply_text('Aaaaaaa... Printing everything about LoRa communication')

@restricted
def deletetempdata(bot, update):
    os.system("sudo rm /home/pi/data/temp_data**")
    update.message.reply_text("Ready, temporal data deleted")

@restricted
def updateFirmware(bot, update):
	os.system("wget {}".format(FIRMWARE_DOWNLOAD_URL))
	if not os.path.isfile("/home/pi/{}".format(FIRMWARE_FILE_NAME)):
		update.message.reply_text("Error in download")
		return
	#os.system("sudo rm /home/pi/{}.py /home/pi/{}.py /home/pi/{}.py /home/pi/{}.py /home/pi/{}.py /home/pi/{}.py /home/pi/{}.py /home/pi/{}.json".format("gw2", "gw_bot", "gw_utils", "gw_config", "paqueteLoRa", "uploadGSheets", "creds", "PruebaPaginaHumedales-7d3cc40aae82"))
	os.system("sudo rm *.py *.json *.pyc")
	os.system("unzip {}".format(FIRMWARE_FILE_NAME))
	os.system("sudo rm {}".format(FIRMWARE_FILE_NAME))
	os.system("sudo rm -rf __MACOSX")
	update.message.reply_text("Ready, 'gw.py' updated")
	update.message.reply_text('/reboot for changes to take effect')

@restricted
def firmwareDownloadURL(bot, update):
	global FIRMWARE_DOWNLOAD_URL
	url = update.message.text[21:] # takes off instruction chars and retrieve url
	FIRMWARE_DOWNLOAD_URL = url
	update.message.reply_text("URL configured ;)")

@restricted
def firmwareFileName(bot, update):
	global FIRMWARE_FILE_NAME
	name = update.message.text[18:]
	FIRMWARE_FILE_NAME = name
	update.message.reply_text("name configured ;)")

@restricted
def getFirmwareURL(bot, update):
	global FIRMWARE_DOWNLOAD_URL
	update.message.reply_text("URL: " + FIRMWARE_DOWNLOAD_URL)

@restricted
def getFirmwareName(bot, update):
	global FIRMWARE_FILE_NAME
	update.message.reply_text("Name: " + FIRMWARE_FILE_NAME)

@restricted
def addAdmin(bot, update):
	global LIST_OF_ADMINS
	try:
		idd = update.message.text[10:]
		LIST_OF_ADMINS.append(int(idd))
		update.message.reply_text("User added as admin :)")
	except Exception as e:
		update.message.reply_text("Error. Could be invalid user id :(")

def echo(bot, update):
    update.message.reply_text("echo: " + update.message.text)
    print "\tbot - " + update.message.from_user.first_name + " (" + str(update.message.chat_id) + "): " + update.message.text

def error(bot, update, error):
	# If anything fails in the GW Telegram Bot it's shown here!
	print 'Update "%s" caused error "%s", ' + update + ", " + error
	sys.exit()


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
dp.add_handler(CommandHandler("deletetempdata", deletetempdata))
dp.add_handler(CommandHandler("updatefirmware", updateFirmware))
dp.add_handler(CommandHandler("firmwaredownloadurl", firmwareDownloadURL))
dp.add_handler(CommandHandler("firmwarefilename", firmwareFileName))
dp.add_handler(CommandHandler("getfirmwareurl", getFirmwareURL))
dp.add_handler(CommandHandler("getfirmwarename", getFirmwareName))
dp.add_handler(CommandHandler("addadmin", addAdmin))
dp.add_handler(MessageHandler(Filters.all, echo))
dp.add_error_handler(error)

updater.start_polling()

hello_msg = """
################################################
# Gateway Llanquihue Telegram Bot
# {} {}
################################################""".format(str(datetime.datetime.now().date()), str(datetime.datetime.now().time())[:8])

bot.send_message(chat_id=idMati, text=hello_msg)

# ##### ##### #     ##### ###   #####   #   ## ##
#   #   ###   #     ###   #  ## #####  ###  #####
#   #   ##### ##### ##### ##### #  #  #   # #   #

# ###     #   ##### ##### #   #   #   #   #
# #  ##  ###    #   ###   # # #  ###   ###
# ##### #   #   #   #####  # #  #   #   #

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
				tmsg = lora_msg.telegramMessage()
				send_message_admins(tmsg)

except Exception as e:
	print 'Error: ' + e.message
	print 'Traceback' + traceback.format_exc()


ser.close()
# script ends

# ###     #   ##### ##### #   #   #   #   #
# #  ##  ###    #   ###   # # #  ###   ###
# ##### #   #   #   #####  # #  #   #   #

#####################

def newTest(bot, update):
    os.system('sudo rm /home/pi/data_gw.txt')
    #os.system("echo 'Date\tTime\tuC Clock [ms]\tPacket Number\tPayload\tRSSI [dBm]\tLight [rel]\tHumidity [%]\tTemperature [C]' > /home/pi/data_gw.txt")
    os.system("echo 'Datos almacenados localmente:' > /home/pi/data_gw.txt")
    update.message.reply_text("Rea-dy, 'data_gw.txt' file is clean")

def getDataFile(bot, update):
    bot.sendDocument(chat_id=idMati, document=open('/home/pi/data_gw.txt', 'rb'))
