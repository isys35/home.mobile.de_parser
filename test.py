import csv
import xlrd
import xlwt
import time

with open('data.csv', "r", newline="", encoding='utf8') as file:
    reader = csv.reader(file, delimiter=';')
    rb = xlrd.open_workbook('data.xls')
    wb = xlwt.Workbook()
    ws = wb.add_sheet('sheet')
    for i in range(0, 21):
        ws.col(i).width = 6000
    sheet = rb.sheet_by_index(0)
    rows = sheet.nrows
    for rownum in range(rows):
        row = sheet.row_values(rownum)
        for colnum in range(len(row)):
            ws.write(rownum, colnum, row[colnum])
    reader = list(reader)
    for r in range(len(reader)):
        for c in range(len(reader[r])):
            ws.write(rows + r, c, reader[r][c])
    while True:
        try:
            wb.save('data.xls')
            break
        except PermissionError:
            print('[ОШИБКА] Закройте Excel файл')
            time.sleep(1)
