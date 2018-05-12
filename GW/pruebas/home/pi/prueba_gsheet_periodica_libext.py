#!/usr/bin/python

import time
import random
import traceback
import uploadGSheets



def main():
    try:
        i = 0
        while 1:
            localtime = time.asctime( time.localtime(time.time()) )
            t = random.randint(1150, 1250)
            
            uploadGSheets.test_upload_virtual_data(localtime, i)
            #uploadGSheets.test_upload(localtime, t, i)
            uploadGSheets.upload()
            
            i += 1
            time.sleep(1200)

    except Exception as e:
        print 'Error: ' + e.message
        print 'Traceback' + traceback.format_exc()

if __name__ == '__main__':
    main()
