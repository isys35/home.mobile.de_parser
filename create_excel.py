import csv
import xlwt
import time


def remake_format(csv_file, excel_file):
    with open(csv_file, "r", newline="", encoding='utf8') as file:
        wb = xlwt.Workbook()
        ws = wb.add_sheet('sheet')
        for i in range(0, 21):
            ws.col(i).width = 6000
        ws.col(0).width = 3000
        ws.col(3).width = 3000
        ws.write(0, 0, 'Source')
        ws.write(0, 1, 'Company')
        ws.write(0, 2, 'Street')
        ws.write(0, 3, 'Postcode')
        ws.write(0, 4, 'Place')
        ws.write(0, 5, 'State')
        ws.write(0, 6, 'Country')
        ws.write(0, 7, 'Telephone_1')
        ws.write(0, 8, 'Telephone_2')
        ws.write(0, 9, 'Telephone_3')
        ws.write(0, 10, 'Fax')
        ws.write(0, 11, 'EMail')
        ws.write(0, 12, 'Website')
        ws.write(0, 13, 'Host')
        ws.write(0, 14, 'Car brands')
        ws.write(0, 15, 'Number of offers')
        ws.write(0, 16, 'Description')
        ws.write(0, 17, 'Qualification_1')
        ws.write(0, 18, 'Qualification_2')
        ws.write(0, 19, 'Qualification_3')
        ws.write(0, 20, 'Qualification_4')
        reader = csv.reader(file, delimiter=';')
        rows = 1
        reader = list(reader)
        for r in range(len(reader)):
            for c in range(len(reader[r])):
                ws.write(rows + r, c, reader[r][c])
        while True:
            try:
                wb.save(excel_file)
                break
            except PermissionError:
                print('[ОШИБКА] Закройте Excel файл')
                time.sleep(1)


if __name__ == '__main__':
    remake_format('data.csv', 'data.xls')
    print('[INFO] Завершено')
