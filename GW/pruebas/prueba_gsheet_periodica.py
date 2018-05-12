#!/usr/bin/python

import time
import random
import traceback
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def main():
    #time.sleep(10)
    
    ## Credentials
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']

    credentials = ServiceAccountCredentials.from_json_keyfile_name('PruebaPaginaHumedales-7d3cc40aae82.json', scope)

    ## GSheets
    gc = gspread.authorize(credentials)

    # Open a worksheet from spreadsheet with one shot
    wks = gc.open("prueba_si").sheet1

    try:
        i = 0
        while 1:
            localtime = time.asctime( time.localtime(time.time()) )
            #t = random.randint(1100, 1300)
            t = 3540
            
            wks.append_row([localtime, t, i, 'que ocurre baby', 'no', 'baby no', random.randint(10,70), random.random()])
            i += 1
            if wks.acell('A1').value == 'stop':
                break
                
            time.sleep(t)

    except Exception as e:
        print 'Error: ' + e.message
        print 'Traceback' + traceback.format_exc()

if __name__ == '__main__':
    main()
