from main import MobileParser
import requests
import time
from bs4 import BeautifulSoup as BS
import traceback
from json.decoder import JSONDecodeError
from analys import brenchmark
import csv
import asyncio
import aiohttp
import json


async def fetch_content(url, session, headers):
    async with session.get(url, headers=headers) as response:
        data = await response.text()
        return data


async def req(urls, headers):
    tasks = []
    async with aiohttp.ClientSession() as session:
        for i in range(0,len(urls)):
            task = asyncio.create_task(fetch_content(urls[i], session, headers[i]))
            tasks.append(task)
        data = await asyncio.gather(*tasks)
        return data



class Parser(MobileParser):
    def __init__(self):
        super().__init__()

    def request(self, url, headers):
        while True:
            try:
                r = requests.get(url, headers=headers)
                if 'Ups, bist Du ein Mensch? / Are you a human?' in r.text:
                    # print(r.status_code)
                    # print('пройдите рекапчу и введите cookie')
                    # cookie = input('==>')
                    # headers['Cookie'] = cookie
                    print('Ups, bist Du ein Mensch? / Are you a human?')
                    print('Пройдите рекапчу')
                    cookie = input('COOKIE: ')
                    headers['Cookie'] = cookie
                else:
                    break
            except Exception as ex:
                print(ex)
        return r

    def dealer_id(self,url):
        if 'http://home.mobile.de/' not in url:
            return
        r = self.request(url, self.HEADERS)
        soup = BS(r.text, 'lxml')
        if not soup.select_one('.de'):
            return
        id = soup.select_one('.de').select('var')[0].text
        return id

    def get_dealer_contact(self, url):
        id = self.dealer_id(url)
        if not id:
            return
        self.JSON_HEADERS['Referer'] = url
        while True:
            try:
                timer = int(time.time() * 1000)
                contact_url = f'https://home.mobile.de/home/contact.html?customerId={id}&adId=0&json=true&_={timer}'
                r = requests.get(contact_url, headers=self.JSON_HEADERS)
                if 'Ups, bist Du ein Mensch? / Are you a human?' in r.text:
                    print('Ups, bist Du ein Mensch? / Are you a human?')
                    cookie = input('COOKIE: ')
                    self.JSON_HEADERS['Cookie'] = cookie
                else:
                    break
            except Exception as ex:
                print(ex)
        resp = r.json()
        self.firma = resp['contactPage']['contactData']['companyName']['value']
        if 'value' not in resp['contactPage']['contactData']['streetAndHouseNumber']:
            return
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
                r = requests.get(imprint_url, headers=self.JSON_HEADERS)
                if 'Ups, bist Du ein Mensch? / Are you a human?' in r.text:
                    print('Ups, bist Du ein Mensch? / Are you a human?')
                    print('Пройдите рекапчу')
                    cookie = input('COOKIE: ')
                    self.JSON_HEADERS['Cookie'] = cookie
                else:
                    break
            except Exception as ex:
                print(ex)
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
                r = requests.get(ses_url, headers=self.JSON_HEADERS)
                if 'Ups, bist Du ein Mensch? / Are you a human?' in r.text:
                    print('Ups, bist Du ein Mensch? / Are you a human?')
                    print('Пройдите рекапчу')
                    cookie = input('COOKIE: ')
                    self.JSON_HEADERS['Cookie'] = cookie
                else:
                    break
            except Exception as ex:
                print(ex)
        try:
            resp = r.json()
        except JSONDecodeError:
            return
        self.count_offer = resp['searchMetadata']['totalResults']
        self.automarks = [el['value'] for el in resp['searchReferenceData']['makes'] if el['key']]
        self.save_file()
        self.save_href()


class ParserCsv(Parser):
    def __init__(self):
        super().__init__()

    @brenchmark
    def save_file(self):
        with open('data.csv', "a", newline="", encoding='utf8') as file:
            data = [self.qualle,
                    self.firma,
                    self.street,
                    self.plz,
                    self.ort,
                    self.bundesland,
                    self.land,
                    None,
                    None,
                    None,
                    self.fax,
                    self.email,
                    self.site,
                    self.host,
                    str(self.automarks),
                    self.count_offer,
                    self.dealer_status,
                    None,
                    None,
                    None,
                    None]
            for i in range(len(self.phone)):
                data[7 + i] = self.phone[i]
            for i in range(len(self.qualifications[:4])):
                data[17 + i] = self.qualifications[i]
            writer = csv.writer(file, delimiter=';')
            writer.writerow(data)


class ParserAsync(ParserCsv):
    def __init__(self):
        super().__init__()

    def get_dealer_contact(self, url):
        id = self.dealer_id(url)
        if not id:
            return
        self.JSON_HEADERS['Referer'] = url
        while True:
            try:
                timer = int(time.time() * 1000)
                contact_url = f'https://home.mobile.de/home/contact.html?customerId={id}&adId=0&json=true&_={timer}'
                imprint_url = f'https://home.mobile.de/home/imprint.html?noHeader=true&customerId={id}&json=false&_={timer}'
                ses_url = f'https://home.mobile.de/home/ses.html?customerId={id}&json=true&_={timer}'
                data = asyncio.run(req([contact_url, imprint_url, ses_url], [self.JSON_HEADERS for _ in range(3)]))
                for el in data:
                    if 'Ups, bist Du ein Mensch? / Are you a human?' in el:
                        print('Ups, bist Du ein Mensch? / Are you a human?')
                        cookie = input('COOKIE: ')
                break
            except Exception as ex:
                print(ex)
        contact_json = json.loads(data[0])
        self.firma = contact_json['contactPage']['contactData']['companyName']['value']
        print(self.firma)
        if 'value' not in contact_json['contactPage']['contactData']['streetAndHouseNumber']:
            return
        self.street = contact_json['contactPage']['contactData']['streetAndHouseNumber']['value']
        self.plz = contact_json['contactPage']['contactData']['zipcodeAndCity']['value'].split(' ')[0]
        self.ort = contact_json['contactPage']['contactData']['zipcodeAndCity']['value'].split(' ', maxsplit=1)[1]
        self.land = contact_json['contactPage']['contactData']['country']['value']
        self.phone = [el['value'] for el in contact_json['contactPage']['contactData']['phoneNumbers']]
        if 'value' in contact_json['contactPage']['contactData']['faxNumber']:
            self.fax = contact_json['contactPage']['contactData']['faxNumber']['value']
        else:
            self.fax = None
        if 'value' in contact_json['contactPage']['userDefinedLink']:
            self.site = contact_json['contactPage']['userDefinedLink']['value']
            self.host = self.site.replace('http://www.', '')
        else:
            self.site = None
            self.host = None
        if 'value' in contact_json['contactPage']['dealerStatus']:
            self.dealer_status = contact_json['contactPage']['dealerStatus']['value']
        else:
            self.dealer_status = None
        imprint_soup = BS(data[1], 'lxml')
        splited_data = imprint_soup.text.split('\n')
        for el in splited_data:
            if '@' in el:
                splited_el = el.split(' ')
                if len(splited_el) > 1:
                    self.email = splited_el[1]
                else:
                    self.email = el
                break
        try:
            ses_json = json.loads(data[2])
        except JSONDecodeError:
            return
        self.count_offer = ses_json['searchMetadata']['totalResults']
        self.automarks = [el['value'] for el in ses_json['searchReferenceData']['makes'] if el['key']]
        self.save_file()
        self.save_href()


if __name__ == '__main__':
    parser = ParserAsync()
    while True:
        try:
            parser.parsing()
            break
        except Exception as ex:
            print(ex)
            print(traceback.format_exc())
    print('Завершено')
