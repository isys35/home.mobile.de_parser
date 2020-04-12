# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import time
from json.decoder import JSONDecodeError
import asyncio
import aiohttp
import json
import csv


def create_save_file(file_name):
    with open(file_name, 'w') as file:
        file.write('')


def save_file(file_name, url):
    with open(file_name, 'a') as file:
        file.write(url + '\n')


def load_file(file_name):
    with open(file_name, 'r') as file:
        data = file.read()
    return data.split('\n')


def create_csv_file(file_name):
    with open(file_name, "w", newline="") as file:
        csv.writer(file)


def request(url, headers):
    while True:
        try:
            r = requests.get(url, headers=headers)
            if 'Ups, bist Du ein Mensch? / Are you a human?' in r.text:
                print('Ups, bist Du ein Mensch? / Are you a human?')
                print('Пройдите рекапчу')
                cookie = input('COOKIE: ')
                headers['Cookie'] = cookie
            else:
                break
        except Exception as ex:
            print(ex)
    return r


def get_pages(soup):
    pg = soup.select_one('.row.pg')
    pages_li = pg.select('li')
    return int(pages_li[-1].text)


async def fetch_content(url, session, headers):
    async with session.get(url, headers=headers) as response:
        data = await response.text()
        return data


async def req(urls, headers):
    tasks = []
    async with aiohttp.ClientSession() as session:
        for i in range(0, len(urls)):
            task = asyncio.create_task(fetch_content(urls[i], session, headers[i]))
            tasks.append(task)
        data = await asyncio.gather(*tasks)
        return data


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

    def get_regions(self):
        r = request(self.URL_REGION, self.HEADERS)
        soup = BeautifulSoup(r.text, 'lxml')
        regions = soup.select('area')
        regions_data = []
        for region in regions:
            regions_data.append({'href': region['href'], 'title': region['title'].split(' ')[-1]})
        return regions_data

    def parsing(self, begin=True):
        if begin:
            create_save_file('saved_dealers')
            create_save_file('saved_pages')
            create_save_file('saved_region')
            create_csv_file('data.csv')
        regions = self.get_regions()
        if not begin:
            regions = [region for region in regions if region['href'] not in load_file('saved_region')]
        for region in regions:
            self.bundesland = region['title']
            self.get_dialers(region['href'])
            save_file('saved_region', region['href'])

    def get_dialers(self, url):
        r = request(url, self.HEADERS)
        soup = BeautifulSoup(r.text, 'lxml')
        pages = get_pages(soup)
        self.get_dealers_main_info(soup)
        for p in range(1, pages):
            page_url = url.replace('0', str(p))
            if page_url in load_file('saved_pages'):
                continue
            r = request(page_url, self.HEADERS)
            soup = BeautifulSoup(r.text, 'lxml')
            self.get_dealers_main_info(soup)
            save_file('saved_pages', page_url)

    def get_dealers_main_info(self, soup):
        dealers = soup.select('.dealerItem')
        for dealer in dealers:
            info = dealer.select('.dealer')
            self.href = info[0].select_one('a')['href']
            print(self.href)
            if self.href in load_file('saved_dealers'):
                continue
            if 'http://home.mobile.de/' not in self.href:
                continue
            self.ort = None
            self.ort = info[2].text.split(' ', maxsplit=1)[1]
            self.qualifications = []
            if len(info) > 3:
                self.qualifications = info[3].text.replace('\n', '').split(',')
            self.get_dealer_app_info()

    def dealer_id(self):
        if 'http://home.mobile.de/' not in self.href:
            return
        r = request(self.href, self.HEADERS)
        soup = BeautifulSoup(r.text, 'lxml')
        if not soup.select_one('.de'):
            return
        index = soup.select_one('.de').select('var')[0].text
        return index

    def get_dealer_app_info(self):
        index = self.dealer_id()
        if not index:
            return
        self.JSON_HEADERS['Referer'] = self.href
        while True:
            try:
                timer = int(time.time() * 1000)
                contact_url = f'https://home.mobile.de/home/contact.html?customerId={index}&adId=0&json=true&_={timer}'
                imprint_url = f'https://home.mobile.de/home/imprint.html?noHeader=true&customerId={index}&json=false&_={timer} '
                ses_url = f'https://home.mobile.de/home/ses.html?customerId={index}&json=true&_={timer}'
                data = asyncio.run(req([contact_url, imprint_url, ses_url], [self.JSON_HEADERS for _ in range(3)]))
                check_robot = False
                for el in data:
                    print(el)
                    if 'Ups, bist Du ein Mensch?' in str(el):
                        print('Ups, bist Du ein Mensch? / Are you a human?')
                        cookie = input('COOKIE: ')
                        self.JSON_HEADERS['Cookie'] = cookie
                        check_robot = True
                        break
                if not check_robot:
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
        imprint_soup = BeautifulSoup(data[1], 'lxml')
        splited_data = imprint_soup.text.split('\n')
        self.email = None
        for el in splited_data:
            if '@' in el:
                splited_el = el.split(' ')
                if len(splited_el) > 1:
                    for el2 in splited_el:
                        if '@' in el2:
                            self.email = el2.replace('eMail:', '').replace('Email.', '')
                else:
                    self.email = el.replace('eMail:', '').replace('Email.', '')
                break
        try:
            ses_json = json.loads(data[2])
        except JSONDecodeError:
            return
        self.count_offer = ses_json['searchMetadata']['totalResults']
        self.automarks = [el['value'] for el in ses_json['searchReferenceData']['makes'] if el['key']]
        self.add_data_in_csv()
        save_file('saved_dealers', self.href)

    def add_data_in_csv(self):
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
                    self.automarks,
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


if __name__ == '__main__':
    parser = MobileParser()
    parser.parsing(begin=True)
