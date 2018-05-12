#!/usr/bin/python

import os
import sys
import creds
from functools import wraps
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

idMati = creds.TELEGRAM_ADMIN_ID
botKey = creds.TELEGRAM_BOT_GW_PRUEBA_KEY

updater = Updater(botKey)
LIST_OF_ADMINS = [int(idMati)]


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
    update.message.reply_text(str(datetime.datetime.now()))
    os.system('sudo reboot')

def verbose(bot, update):
    global TELEGRAM_VERBOSE
    if TELEGRAM_VERBOSE:
        TELEGRAM_VERBOSE = False
        update.message.reply_text('Cashate nene! Silence everything about LoRa communication')
    else:
        TELEGRAM_VERBOSE = True
        update.message.reply_text('Aaaaaaaaaa??? Printing everything about LoRa communication')

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

def updateFirmware(bot, update):
    os.system('sudo rm /home/pi/prueba_telegram_bot.py')
    os.system('wget https://www.dropbox.com/s/gg13mo2a517yxmc/prueba_telegram_bot.py')
    update.message.reply_text("Ready, 'gw.py' updated")
    update.message.reply_text('/reboot for changes to take effect')


def echo(bot, update):
    update.message.reply_text("echo: " + update.message.text)
    print update.message.from_user.first_name + " (" + str(update.message.chat_id) + "): " + update.message.text

def error(bot, update, error):
    print 'Update "%s" caused error "%s", ' + update + ", " + error

def main():
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


    bot.send_message(chat_id=idMati, text="!Hola aloh")

if __name__ == '__main__':
    main()
