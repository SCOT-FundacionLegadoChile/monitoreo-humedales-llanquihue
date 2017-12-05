import os
import xlrd
import xlsxwriter

workbook = xlsxwriter.Workbook('0_total.xlsx')
worksheet = workbook.add_worksheet()
worksheet.write_row(0, 0, ['rol','# paquete', 'paquete', 'lora_pa', 'lora_pow', 'lora_mod',
                           'time', 'date', 'lat', 'lon', 'altura', 'lugar'])
worksheet_row = 1

n_paq_anterior = 0

files = [f for f in os.listdir('.') if os.path.isfile(f)]
files.sort()
for f in files:
    if (str(f) != 'join_datas_in_one.py' and str(f) != '0_total.xlsx'):
        print str(f)
        wb = xlrd.open_workbook(f)
        sheet = wb.sheet_by_index(0)
        n_data_rows = len(sheet.col_values(3)) -1

        for i in range(1,n_data_rows):
            row = sheet.row_values(i)

            n_paq = row[2].partition('\t')[0]
            if int(n_paq) != n_paq_anterior + 1 and n_paq_anterior != 0:
                for j in range(n_paq_anterior+1,int(n_paq)):
                    data = ['', str(j), '', '', '', '', '', '', '', '', '', '']
                    worksheet.write_row(worksheet_row, 0, data)
                    worksheet_row += 1

            data = [row[0], n_paq, row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11]]
            n_paq_anterior = int(n_paq)

            worksheet.write_row(worksheet_row, 0, data)
            worksheet_row += 1

workbook.close()

