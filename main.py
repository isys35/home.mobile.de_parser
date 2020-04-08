import requests
from bs4 import BeautifulSoup as BS
import time
import xlwt
import xlrd
import os
import proxy as pr
import traceback
from analys import brenchmark



class MobileParser:
    URL_REGION = 'https://home.mobile.de/regional/'
    HEADERS = {
        'Host': 'home.mobile.de',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0',
        'TE': 'Trailers'
    }

    JSON_HEADERS = {
        'Host': 'home.mobile.de',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br',
        'X-Requested-With': 'XMLHttpRequest',
        'Connection': 'keep-alive',
        'TE': 'Trailers'
    }

    def __init__(self):
        self.qualle = 'Mobile'
        self.land = 'Deutschland'
        self.firma = None
        self.street = None
        self.plz = None
        self.ort = None
        self.bundesland = None
        self.phone = None
        self.fax = None
        self.email = None
        self.site = None
        self.host = None
        self.count_offer = None
        self.automarks = None
        self.dealer_status = None
        self.qualifications = None
        self.href = None
        self.file_name = 'data.xls'
        self.proxy = pr.get_proxy()
        if self.file_name not in os.listdir('.'):
            self.create_xls_file()
        self.parsed_hrefs = self.load_hrefs()
        self.parsed_regions = self.load_regions()
        self.parsed_pages = self.load_pages()

    def load_hrefs(self):
        try:
            with open('save_file', 'r') as save_file:
                hrefs = save_file.read()
        except FileNotFoundError:
            hrefs = '[]'
        print(hrefs)
        return eval(hrefs)

    def load_pages(self):
        try:
            with open('save_file_page', 'r') as save_file:
                hrefs = save_file.read()
        except FileNotFoundError:
            hrefs = '[]'
        print(hrefs)
        return eval(hrefs)


    def create_xls_file(self):
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
        while True:
            try:
                wb.save(self.file_name)
                break
            except PermissionError:
                print('[ОШИБКА] Закройте Excel файл')
                time.sleep(1)

    @brenchmark
    def save_file(self):
        rb = xlrd.open_workbook(self.file_name)
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
        ws.write(rows, 0, self.qualle)
        ws.write(rows, 1, self.firma)
        ws.write(rows, 2, self.street)
        ws.write(rows, 3, self.plz)
        ws.write(rows, 4, self.ort)
        ws.write(rows, 5, self.bundesland)
        ws.write(rows, 6, self.land)
        for i in range(len(self.phone)):
            ws.write(rows, 7+i, self.phone[i])
        ws.write(rows, 10, self.fax)
        ws.write(rows, 11, self.email)
        ws.write(rows, 12, self.site)
        ws.write(rows, 13, self.host)
        ws.write(rows, 14, self.automarks)
        ws.write(rows, 15, self.count_offer)
        ws.write(rows, 16, self.dealer_status)
        for i in range(len(self.qualifications)):
            ws.write(rows, 17+i, self.qualifications[i])
        while True:
            try:
                wb.save(self.file_name)
                break
            except PermissionError:
                print('[ОШИБКА] Закройте Excel файл')
                time.sleep(1)

    def request(self, url, headers):
        while True:
            try:
                r = requests.get(url, headers=headers, proxies=self.proxy)
                if 'Ups, bist Du ein Mensch? / Are you a human?' in r.text:
                    # print(r.status_code)
                    # print('пройдите рекапчу и введите cookie')
                    # cookie = input('==>')
                    # headers['Cookie'] = cookie
                    print('Ups, bist Du ein Mensch? / Are you a human?')
                    self.proxy = pr.get_proxy()
                else:
                    break
            except Exception as ex:
                print(ex)
                self.proxy = pr.get_proxy()
        return r

    def get_regions(self):
        r = self.request(self.URL_REGION, self.HEADERS)
        soup = BS(r.text, 'lxml')
        regions = soup.select('area')
        regions_data = []
        for region in regions:
            regions_data.append({'href':region['href'], 'title': region['title'].split(' ')[-1]})
        return regions_data

    @staticmethod
    def get_pages(soup):
        pg = soup.select_one('.row.pg')
        pages_li = pg.select('li')
        return int(pages_li[-1].text)

    def get_dealers_info(self, soup):
        dealers = soup.select('.dealerItem')
        dealers_data = []
        for dealer in dealers:
            info = dealer.select('.dealer')
            self.href = info[0].select_one('a')['href']
            print(self.href)
            if self.href in self.parsed_hrefs:
                continue
            if 'http://home.mobile.de/' not in self.href:
                continue
            self.ort = None
            self.ort = info[2].text.split(' ', maxsplit=1)[1]
            self.qualifications = []
            if len(info) > 3:
                self.qualifications = info[3].text.replace('\n', '').split(',')
            self.get_dealer_contact(self.href)


    def get_dealer_contact(self, url):
        if 'http://home.mobile.de/' not in url:
            return
        r = self.request(url, self.HEADERS)
        soup = BS(r.text, 'lxml')
        if not soup.select_one('.de'):
            return
        id = soup.select_one('.de').select('var')[0].text
        self.JSON_HEADERS['Referer'] = url
        while True:
            try:
                timer = int(time.time() * 1000)
                contact_url = f'https://home.mobile.de/home/contact.html?customerId={id}&adId=0&json=true&_={timer}'
                r = requests.get(contact_url, headers=self.JSON_HEADERS, proxies=self.proxy)
                if 'Ups, bist Du ein Mensch? / Are you a human?' in r.text:
                    print('Ups, bist Du ein Mensch? / Are you a human?')
                    self.proxy = pr.get_proxy()
                else:
                    break
            except Exception as ex:
                print(ex)
                self.proxy = pr.get_proxy()
        resp = r.json()
        self.firma = resp['contactPage']['contactData']['companyName']['value']
        print(self.firma)
        self.street = resp['contactPage']['contactData']['streetAndHouseNumber']['value']
        self.plz = resp['contactPage']['contactData']['zipcodeAndCity']['value'].split(' ')[0]
        self.ort = resp['contactPage']['contactData']['zipcodeAndCity']['value'].split(' ', maxsplit=1)[1]
        self.land = resp['contactPage']['contactData']['country']['value']
        self.phone = [el['value'] for el in resp['contactPage']['contactData']['phoneNumbers']]
        if 'value' in resp['contactPage']['contactData']['faxNumber']:
            self.fax = resp['contactPage']['contactData']['faxNumber']['value']
        else:
            self.fax = None
        if 'value' in resp['contactPage']['userDefinedLink']:
            self.site = resp['contactPage']['userDefinedLink']['value']
            self.host = self.site.replace('http://www.','')
        else:
            self.site = None
            self.host = None
        if 'value' in resp['contactPage']['dealerStatus']:
            self.dealer_status = resp['contactPage']['dealerStatus']['value']
        else:
            self.dealer_status = None
        #print(self.firma, self.street, self.phone)
        headers = self.JSON_HEADERS
        while True:
            try:
                timer = int(time.time() * 1000)
                imprint_url = f'https://home.mobile.de/home/imprint.html?noHeader=true&customerId={id}&json=false&_={timer}'
                r = requests.get(imprint_url, headers=self.JSON_HEADERS, proxies=self.proxy)
                if 'Ups, bist Du ein Mensch? / Are you a human?' in r.text:
                    print('Ups, bist Du ein Mensch? / Are you a human?')
                    self.proxy = pr.get_proxy()
                else:
                    break
            except Exception as ex:
                print(ex)
                self.proxy = pr.get_proxy()
        soup = BS(r.text, 'lxml')
        splited_data = soup.text.split('\n')
        #print(splited_data)
        self.email = None
        for el in splited_data:
            if '@' in el:
                splited_el = el.split(' ')
                if len(splited_el) > 1:
                    self.email = splited_el[1]
                else:
                    self.email = el
                break
        while True:
            try:
                timer = int(time.time() * 1000)
                ses_url = f'https://home.mobile.de/home/ses.html?customerId={id}&json=true&_={timer}'
                r = requests.get(ses_url, headers=self.JSON_HEADERS, proxies=self.proxy)
                if 'Ups, bist Du ein Mensch? / Are you a human?' in r.text:
                    print('Ups, bist Du ein Mensch? / Are you a human?')
                    self.proxy = pr.get_proxy()
                else:
                    break
            except Exception as ex:
                print(ex)
                self.proxy = pr.get_proxy()
        resp = r.json()
        self.count_offer = resp['searchMetadata']['totalResults']
        self.automarks = [el['value'] for el in resp['searchReferenceData']['makes'] if el['key']]
        self.save_file()
        self.save_href()
        # timer = int(time.time() * 1000)
        # url_about = f'https://home.mobile.de/home/about.html?noHeader=true&customerId={id}&json=false&_={timer}'
        # r = requests.get(url_about, headers=headers)
        # soup = BS(r.text, 'lxml')
        # print(soup.select_one('.row-fluid.about').text)


        # for el in splited_data:
        #     if 'www' in el:
        #         splited_el = el.split(' ')
        #         if len(splited_el) > 1:
        #             for _el in splited_el:
        #                 if 'www' in _el:
        #                     self.site = _el
        #         else:
        #             self.site = el
        #         self.host = self.site.replace('www.','')
        # print(self.site)

    def save_href(self):
        try:
            with open('save_file', 'r') as save_file:
                hrefs = save_file.read()
        except FileNotFoundError:
            hrefs = '[]'
        hrefs = eval(hrefs)
        hrefs.append(self.href)
        with open('save_file', 'w') as save_file:
            save_file.write(str(hrefs))

    def get_dialers(self, url):
        r = self.request(url, self.HEADERS)
        soup = BS(r.text, 'lxml')
        pages = self.get_pages(soup)
        self.get_dealers_info(soup)
        for p in range(1, pages):
            page_url = url.replace('0', str(p))
            if page_url in self.parsed_pages:
                continue
            r = self.request(page_url, self.HEADERS)
            soup = BS(r.text, 'lxml')
            self.get_dealers_info(soup)
            self.save_page_catalog(page_url)

    def save_page_catalog(self, page):
        try:
            with open('save_file_page', 'r') as save_file:
                pages_str = save_file.read()
        except FileNotFoundError:
            pages_str = '[]'
        pages = eval(pages_str)
        pages.append(page)
        with open('save_file_page', 'w') as save_file:
            save_file.write(str(pages))


    def save_region(self, save_region):
        try:
            with open('save_file_region', 'r') as save_file:
                regions_hrefs = save_file.read()
        except FileNotFoundError:
            regions_hrefs = '[]'
        hrefs = eval(regions_hrefs)
        hrefs.append(save_region)
        with open('save_file_region', 'w') as save_file:
            save_file.write(str(hrefs))

    def parsing(self):
        regions = self.get_regions()
        for region in regions:
            if region['href'] in self.parsed_regions:
                 continue
            self.bundesland = region['title']
            self.get_dialers(region['href'])
            self.save_region(region['href'])

    def load_regions(self):
        try:
            with open('save_file_region', 'r') as save_file:
                regions_hrefs = save_file.read()
        except FileNotFoundError:
            regions_hrefs = '[]'
        print(regions_hrefs)
        return eval(regions_hrefs)


if __name__ == '__main__':
    parser = MobileParser()
    try:
        while True:
            parser.parsing()
            break
    except Exception as ex:
        print(ex)
        print(traceback.format_exc())
    print('Завершено')
