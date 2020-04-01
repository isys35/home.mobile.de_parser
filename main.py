import requests
from bs4 import BeautifulSoup as BS
import time


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

    def get_regions(self):
        r = requests.get(self.URL_REGION, headers=self.HEADERS)
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
            href = info[0].select_one('a')['href']
            if 'http://home.mobile.de/' not in href:
                continue
            self.ort = info[2].text.split(' ', maxsplit=1)[1]
            if len(info) > 3:
                self.qualifications = info[3].text.replace('\n', '').split(',')
            print(self.qualifications)
            self.get_dealer_contact(href)

    def get_dealer_contact(self, url):
        if 'http://home.mobile.de/' not in url:
            return
        r = requests.get(url, headers=self.HEADERS, timeout=100)
        soup = BS(r.text, 'lxml')
        id = soup.select_one('.de').select('var')[0].text
        self.JSON_HEADERS['Referer'] = url
        timer = int(time.time()*1000)
        contact_url = f'https://home.mobile.de/home/contact.html?customerId={id}&adId=0&json=true&_={timer}'
        r = requests.get(contact_url, headers=self.JSON_HEADERS)
        resp = r.json()
        self.firma = resp['contactPage']['contactData']['companyName']['value']
        self.street = resp['contactPage']['contactData']['streetAndHouseNumber']['value']
        self.plz = resp['contactPage']['contactData']['zipcodeAndCity']['value'].split(' ')[0]
        self.ort = resp['contactPage']['contactData']['zipcodeAndCity']['value'].split(' ', maxsplit=1)[1]
        self.land = resp['contactPage']['contactData']['country']['value']
        self.phone = resp['contactPage']['contactData']['phonumber']['number']
        if 'value' in resp['contactPage']['contactData']['faxNumber']:
            self.fax = resp['contactPage']['contactData']['faxNumber']['value']
        if 'value' in resp['contactPage']['userDefinedLink']:
            self.site = resp['contactPage']['userDefinedLink']['value']
            self.host = self.site.replace('http://www.','')
        if 'value' in resp['contactPage']['dealerStatus']:
            self.dealer_status = resp['contactPage']['dealerStatus']['value']
        #print(self.firma, self.street, self.phone)
        headers = self.JSON_HEADERS
        timer = int(time.time() * 1000)
        imprint_url = f'https://home.mobile.de/home/imprint.html?noHeader=true&customerId={id}&json=false&_={timer}'
        r = requests.get(imprint_url, headers=headers)
        soup = BS(r.text, 'lxml')
        splited_data = soup.text.split('\n')
        #print(splited_data)
        for el in splited_data:
            if '@' in el:
                splited_el = el.split(' ')
                if len(splited_el) > 1:
                    self.email = splited_el[1]
                else:
                    self.email = el
                break
        timer = int(time.time() * 1000)
        ses_url = f'https://home.mobile.de/home/ses.html?customerId={id}&json=true&_={timer}'
        r = requests.get(ses_url, headers=headers)
        resp = r.json()
        self.count_offer = resp['searchMetadata']['totalResults']
        self.automarks = [el['value'] for el in resp['searchReferenceData']['makes'] if el['key']]
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

    def get_dialers(self, url):
        r = requests.get(url, headers=self.HEADERS)
        soup = BS(r.text, 'lxml')
        pages = self.get_pages(soup)
        self.get_dealers_info(soup)
        for p in range(1,pages):
            r = requests.get(url.replace('0', str(p)), headers=self.HEADERS)
            soup = BS(r.text, 'lxml')
            self.get_dealers_info(soup)

    def parsing(self):
        regions = self.get_regions()
        for region in regions:
            self.bundesland = region['title']
            self.get_dialers(region['href'])


if __name__ == '__main__':
    parser = MobileParser()
    parser.parsing()
