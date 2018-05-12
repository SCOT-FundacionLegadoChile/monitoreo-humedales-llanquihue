#!/usr/bin/python

import gspread
from oauth2client.service_account import ServiceAccountCredentials

## Credentials
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

credentials = ServiceAccountCredentials.from_json_keyfile_name('PruebaPaginaHumedales-7d3cc40aae82.json', scope)

## GSheets
gc = gspread.authorize(credentials)

# Open a worksheet from spreadsheet with one shot
#wks = gc.open_by_key('1cgTCOSI_ZbpCvykMs_hXGQxQw2LLut9q01PfXEHLPVQ').sheet1
wks = gc.open("prueba_si").sheet1

wks.update_acell('B2', "it's down there somewhere, let me take another look.")

# Fetch a cell range
cell_list = wks.range('A1:B7')
