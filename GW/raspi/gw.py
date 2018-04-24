#!/usr/bin/python

## Installation
#
#    Needed:
#    	- Python 2.7x
#    	- pip
#
#    # Google Spreadsheets
#    sudo pip uninstall oauth2client
#    sudo pip install oauth2client==1.5.2
#    pip install PyOpenSSL
#    pip install gspread
#    pip install json
#
#    # Telegram Bot
#    pip install python-telegram-bot --upgrade
#
#    # Serial
#    pip install pyserial --upgrade
#
#    # Log
#    pip install logging
#
## References
#
#    GSheets python article: http://www.makeuseof.com/tag/read-write-google-sheets-python/
#    Google Sheets Python Library: https://github.com/burnash/gspread
#
#    Problemas:
#      https://stackoverflow.com/questions/14063124/importerror-cannot-import-name-signedjwtassertioncredentials#35447759
#      https://raspberrypi.stackexchange.com/questions/59741/access-serial-port-with-python-on-raspberry-pi3#59766
#
#    Raspi power limitations: https://raspberrypi.stackexchange.com/questions/51615/raspberry-pi-power-limitations
#    Exploring de 3.3V power rail: https://raspberrypise.tumblr.com/post/144555785379/exploring-the-33v-power-rail
#
#    Why use if __name__ == "__main__": https://stackoverflow.com/questions/419163/what-does-if-name-main-do#419185
#
#    Python Telegram Bot Library: https://github.com/python-telegram-bot
#
#    Remove final new line of string: https://stackoverflow.com/questions/275018/how-can-i-remove-chomp-a-newline-in-python#275025
#
#    Configure raspis date & time: https://stackoverflow.com/questions/25374570/how-to-update-date-and-time-of-raspberry-pi-with-out-internet
#    Get time & date python: https://www.cyberciti.biz/faq/howto-get-current-date-time-in-python/
#
#    Launch python script on startup: http://www.instructables.com/id/Raspberry-Pi-Launch-Python-script-on-startup/
#
#    Hello.gif : https://media.giphy.com/media/dzaUX7CAG0Ihi/giphy.gif
#
#    Serial: https://oscarliang.com/raspberry-pi-and-arduino-connected-serial-gpio/
#
#    Run script as service: http://www.diegoacuna.me/how-to-run-a-script-as-a-service-in-raspberry-pi-raspbian-jessie/
#    Service problem import: https://stackoverflow.com/questions/35641414/python-import-of-local-module-failing-when-run-as-systemd-systemctl-service#39987693
#
#
## TODO's
#   - Hay que ver a futuro como se podra actualizar este codigo desde Santiago remotamete a Llanquihue
#       opcion 1: hacer un vpn a la raspberry y ssh'ear de ahi
#       opcion 2: actualizar codigo en reopsitorio online y a traves de un comando de telegram actualizar repo local
#   - Aumentar baud rate serial
#   - Add & Redirect gw-launcher.sh to repo direction
#   - Add gw.txt and logs directories from loscal raspbery to repo
#   - Implementar actualizacion de codigo desde telegram a traves del github (opcion 2 de arriba)
#   - Agregar id. nodo a paquetes
#   - Esconder todas las id's y api keays delicadas del codigo para subir al repositorio de manera segura
#
# SCP Command ->  scp gw.py pi@192.168.1.8:/home/pi/Desktop/gw.py

# Global vars
RASPI = True
global TELEGRAM_VERBOSE
TELEGRAM_VERBOSE = False
UPLOAD_GSHEETS = False
NON_STOP_INTERNET_CONN_TRY = False

# Credentials
import creds
idMati = creds.TELEGRAM_ADMIN_ID
botKey = creds.TELEGRAM_BOT_KEY


# OS
import os
import sys

# Data & Time, & time
import datetime
import time

## Check wifi connection
#  and reboot after 1 min without Wifi
import urllib2

def internet_on():
    try:
        urllib2.urlopen('http://216.58.192.142', timeout=1)
        return True
    except urllib2.URLError as err:
        return False

if NON_STOP_INTERNET_CONN_TRY:
    for i in range(3):
        if internet_on():
            break
        else:
            if (i == 2):
                os.system('sudo reboot')
            time.sleep(20)

## 0. Import libraries
# Google Sheets
import json
import gspread
from oauth2client.client import SignedJwtAssertionCredentials

# Telegram Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

updater = Updater(botKey)

from functools import wraps

LIST_OF_ADMINS = [int(idMati)]

# Serial
import serial
if RASPI:
    ser = serial.Serial('/dev/serial0', 9600)

# Logging
import traceback
import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

print 'Libraries imported'

## 1. Code
# Telegram
#Restricts acces to handlers to authorized list of admins
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
    logger.info('telegram: /start')


def help(bot, update):
    logger.info('telegram: /help')
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
        logger.info('telegram: /mod {}'.format(lora_mod))
    except:
        print 'Error: Invalid /mod command'
        logger.info('Error: Invalid /mod command')
        update.message.reply_text('Error: Invalid /mod command')

def reboot(bot, update):
    update.message.reply_text('Restarting GW');
    update.message.reply_text(str(datetime.datetime.now()))
    logger.info('telegram: /reboot')
    logger.info('Restarting GW')
    os.system('sudo reboot')

def verbose(bot, update):
    logger.info('telegram: /verbose')
    global TELEGRAM_VERBOSE
    if TELEGRAM_VERBOSE:
        TELEGRAM_VERBOSE = False
        update.message.reply_text('Shh! Silence everything about LoRa communication')
    else:
        TELEGRAM_VERBOSE = True
        update.message.reply_text('Aaa! Printing everything about LoRa communication')

def newTest(bot, update):
    logger.info('telegram: /newTest')
    #/home/pi/monitoreo-humedales-llanquihue/GW/raspi/gw.py
    os.system('sudo rm /home/pi/data_gw.txt')
    #os.system("echo 'Date\tTime\tuC Clock [ms]\tPacket Number\tPayload\tRSSI [dBm]\tLight [rel]\tHumidity [%]\tTemperature [C]' > /home/pi/data_gw.txt")
    os.system("echo 'Datos almacenados localmente:' > /home/pi/data_gw.txt")
    update.message.reply_text("Rea-dy, 'data_gw.txt' file is clean")
    logger.info("Ready, 'data_gw.txt' file is clean")

def getDataFile(bot, update):
    logger.info('telegram: /getDataFile')
    bot.sendDocument(chat_id=idMati, document=open('/home/pi/data_gw.txt', 'rb'))
    logger.info('OK, data_gw.txt fetched')

def uploadGSheets(bot, update):
    logger.info('telegram: /uploadGSheets')
    global UPLOAD_GSHEETS
    if UPLOAD_GSHEETS:
        UPLOAD_GSHEETS = False
        update.message.reply_text('Packets just stored locally')
    else:
        UPLOAD_GSHEETS = True
        update.message.reply_text('Packets will be stored in GSheets too')

def updateFirmware(bot, update):
    # wget https://raw.githubusercontent.com/SCOT-FundacionLegadoChile/monitoreo-humedales-llanquihue/master/GW/raspi/gw.py
    logger.info('telegram: /updateFirmware')
    #os.system('sudo rm gw.py')
    #os.system('wget https://raw.githubusercontent.com/SCOT-FundacionLegadoChile/monitoreo-humedales-llanquihue/master/GW/raspi/gw.py')
    os.system('cd /home/pi/monitoreo-humedales-llanquihue/')
    os.system('git pull')
    update.message.reply_text("Ready, 'gw.py' updated")
    update.message.reply_text('/reboot for changes to take effect')
    logger.info("Ready, 'gw.py' updated")


def echo(bot, update):
    update.message.reply_text(update.message.text)
    # print update.message
    # print update.message.from_user.first_name
    # print update.message.chat_id
    print update.message.from_user.first_name + " (" + str(update.message.chat_id) + "): " + update.message.text
    logger.info(update.message.from_user.first_name + " (" + str(update.message.chat_id) + "): " + update.message.text)

def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)

# Utils
def get_json(list):
    if (list[2] == ''):
        valid = 'false'
        list[0] = list[1] = list[2] = list[3] = ''
        list.append('')
        list.append('')
        list.append('')
        list.append('')
        list.append('')
        list.append('')
        list.append('')
        list.append('')
        list.append('')
        list.append('')
    else:
        valid = 'true'

    yeison = {
        'valid': valid,
        'date': list[0],
        'time': list[1],
        'module_time': list[2],
        'packet_number': list[4],
        'payload': list[7] + " " + list[8] + " " + list[9] + " " + list[10] + " " + list[11],
        'rssi': list[14],
        'sensors': {
            'light': list[8],
            'humidity': list[9],
            'temperature': list[10]
        }
    }

    return yeison

def get_list(yeison):
    list = [yeison['date'],
            yeison['time'],
            yeison['module_time'],
            yeison['packet_number'],
            yeison['payload'],
            yeison['rssi'],
            yeison['sensors']['light'],
            yeison['sensors']['humidity'],
            yeison['sensors']['temperature']]

    return list

def clean_response_list(reslist):
    if (reslist[2] != ''):
        return reslist[0] + '\t' + \
               reslist[1] + '\t' + \
               reslist[2] + '\t' + \
               reslist[4] + '\t' + \
               reslist[7] + " " + reslist[8] + " " + reslist[9] + " " + reslist[10] + " " + reslist[11] + '\t' + \
               reslist[14] + '\t' + \
               reslist[8] + '\t' + \
               reslist[9] + '\t' + \
               reslist[10] + '\n'
    else:
        return ''         + '\t' + \
               ''         + '\t' + \
               ''         + '\t' + \
               reslist[4] + '\t' + \
               ''         + " " + '' + " " + '' + " " + '' + " " + '' + '\t' + \
               ''         + '\t' + \
               ''         + '\t' + \
               ''         + '\t' + \
               ''         + '\n'

def telegram_respose(reslist):
    if (reslist[2] != ''):
        return '[#' + reslist[4] + ' , RSSI: ' + reslist[14] + ' , [light: ' + reslist[8] + ' , hum: ' + reslist[9] + ' , temp:' + reslist[10] + ']]'
    else:
        return '[#' + reslist[4] + '...]'

def help_message():
    return 'Available commands\n\t' +\
           '- /help\n\n\t' +\
           '- /start\n\t' +\
           '- /stop\n\n\t' +\
           '- /reboot\n\n\t' +\
           '- /mod\n\t' +\
           '- /verbose\n\n\t' +\
           '- /newTest\n\t' +\
           '- /getData\n\t' +\
           '- /uploadGSheets\n\t' +\
           '- /updateFirmware'

# Main
def main():
    ### 1. Setup & initialize
    ## Google Sheet
    # if UPLOAD_GSHEETS:
    #     print 'Initializing Google Sheets...',
    #     logger.info('Initializing Google Sheets...')
    #
    #     json_key = json.load(open('creds.py.json'))
    #     scope = ['https://spreadsheets.google.com/feeds']
    #
    #     credentials = SignedJwtAssertionCredentials(json_key['client_email'], json_key['private_key'].encode(), scope)
    #
    #     file = gspread.authorize(credentials)
    #     client = file.open("Datos Monitoreo Humedales Llanquihue")
    #     sheet = client.worksheet("prueba")
    #
    #     print ' Ready!'
    #     logger.info(' Ready!')

    #time.sleep(10)

    ## Telegram Bot
    logger.info('Initializing Telegram Bot...')

    bot = updater.bot
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("stop", stop))
    dp.add_handler(CommandHandler("mod", mod))
    dp.add_handler(CommandHandler("reboot", reboot))
    dp.add_handler(CommandHandler("verbose", verbose))
    dp.add_handler(CommandHandler("newTest", newTest))
    dp.add_handler(CommandHandler("getData", getDataFile))
    dp.add_handler(CommandHandler("uploadGSheets", uploadGSheets))
    dp.add_handler(CommandHandler("updateFirmware", updateFirmware))
    dp.add_handler(MessageHandler(Filters.all, echo))
    dp.add_error_handler(error)

    updater.start_polling()
    # updater.idle()

    bot.send_photo(chat_id=idMati, photo=open('/home/pi/hello.png', 'rb'))
    bot.send_message(chat_id=idMati, text=str(datetime.datetime.now()))
    bot.send_message(chat_id=idMati, text=help_message())

    print ' Ready!'
    logger.info('Ready!')

    ### 2. Handle LoRa Serial Comm
    ## Reading serial packets from sx1276 LoRa
    print 'Listening serial...'
    logger.info('Listening serial...')

    try:
        while 1:
            if RASPI:
                ## 1. Read packet
                arduino_msg = ser.readline() #.rstrip()

                # Messages from arduino are formatted as '[tag][msg]'.
                # tag indicates if it's an arduino info message or a lora packet
                tag = arduino_msg[:4]
                msg = arduino_msg[5:]

                if tag == "info":
                    info = msg
                    bot.send_message(chat_id=idMati, text=info)
                    logger.info('arduino: ' + info)

                elif tag == "lora":
                    lora_msg = msg
                    lora_msg = lora_msg.split('\n')[0]

                    dt = datetime.datetime.now()
                    lora_msg = str(dt.date()) + '\t' + str(dt.time()) + '\t' + lora_msg

                    lora_msg_list = lora_msg.split("\t")

                    ## 2. Save in local file
                    clean_response = clean_response_list(lora_msg_list)
                    with open('/home/pi/data_gw.txt', 'a') as file:
                        #file.write(clean_response)
                        file.write(lora_msg)
                        logger.info('writing packet in data file')

                    ## 3. Upload data to spreadsheet
                    data = get_json(lora_msg_list)
                    # if UPLOAD_GSHEETS:
                    #     r = sheet.row_count
                    #
                    #     logger.info('updating row ' + str(r) + ' <- ' + str(data))
                    #
                    #     try:
                    #         sheet.insert_row(get_list(data), index=r)
                    #     except:
                    #         for shot in range(3):
                    #             try:
                    #                 bot.send_message(chat_id=idMati, text='Error, reattempting to upload data to spreadsheet in 20 seconds')
                    #                 time.sleep(20)
                    #
                    #                 bot.send_message(chat_id=idMati, text='Attempt #' + str(shot+1))
                    #                 sheet.insert_row(get_list(data), index=r)
                    #                 break
                    #             except:
                    #                 pass

                    ## 4. telegram
                    if TELEGRAM_VERBOSE:
                        #bot.send_message(chat_id=idMati, text=telegram_respose(lora_msg_list))
                        bot.send_message(chat_id=idMati, text=lora_msg)
            else:
                pass
    except Exception as e:
        logging.error('traceback' + traceback.format_exc())
        bot.send_message(chat_id=idMati, text='traceback' + str(traceback.format_exc()))
        logging.error('error: ' + e.message)
        bot.send_message(chat_id=idMati, text='error: ' + e.message)

    logger.info('ERROR! Not listening for lora packets')
    bot.send_message(chat_id=idMati, text='ERROR! Not listening for lora packets')
    if RASPI:
       ser.close()

if __name__ == '__main__':
    main()

#