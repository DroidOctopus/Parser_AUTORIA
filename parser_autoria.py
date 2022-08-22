import requests
import csv
import os


from requests_html import HTMLSession
from urllib.parse import *


FILE = 'cars.csv'
HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0', 'accept': '*/*'}
HOST = 'https://auto.ria.com/uk'


def parse_url(url):
    """ parsing URL """
    url = urlsplit(url)
    u = url.query.split('&')
    if (u[-1])[0:4] == 'size':
        print('size')
        u[-1] = 'size=100'
    else:
        u.append('size=100')
    global x
    if url.path == '/uk/newauto/search/':
        x = 'newauto'
        print('New auto')
        if (u[0])[0:4] == 'page':
            print('page')
            u.remove(u[0])
    else:
        x = 'oldauto'
        print('Old auto')
        if (u[-2])[0:4] == 'page':
            print('page')
            u.remove(u[-2])
    u = '&'.join(u)
    url = url._replace(query=u)
    url = urlunsplit(url)
    return url



def get_html(url, params=None):
    """ starting a session """
    try:
        session = HTMLSession()
        session.headers['user-agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0'
        response = session.get(url, params=params)
        print(response.url)
        return response 
         
    except requests.exceptions.RequestException as e:
        print(e) 
         

def get_pages_count(response):
    """ pagination analysis """
    pagination = response.html.find('.page-link')
    for i in range(2, (len(pagination))):
        try:
            return int(pagination[-i].text)
        except ValueError as e:
            print(e)


def get_content(response):
    """ OLD AUTO """
    items = response.html.find('.content-bar')
    cars = []
    for item in items:
        if item.find('.footer_ticket'):
            link = item.find('.m-link-ticket', first=True)
            usd_price = item.find('.size15', first=True)
            uah_price = item.find('.i-block', first=True)
            if uah_price:
                uah_price = uah_price.text
            else:
                uah_price = 'Цену уточняйте'
            cars.append({
                'title': item.find('.ticket-title', first=True).text,
                'link': link.attrs['href'],
                'usd_price': item.find('.size22', first=True).text,
                'uah_price': uah_price,
                'city': item.find('.js-location', first=True).text,
            })
    """ NEW AUTO """
    items = response.html.find('.proposition')
    for item in items:
        if item.find('.proposition_price'):
            link = item.find('.proposition_link', first=True)
            usd_price = item.find('.red', first=True)
            if usd_price:
                usd_price = usd_price.text
            else:
                usd_price = item.find('.size22', first=True).text
            uah_price = item.find('.proposition_price', first=True)
            uah_price = uah_price.find('.size16')
            if uah_price:
                uah_price = uah_price[-1].text
            else:
                uah_price = 'Цену уточняйте'
            cars.append({
                'title': item.find('.link', first=True).text,
                'link': HOST + link.attrs['href'],
                'usd_price': item.find('.size22', first=True).text,
                'uah_price': uah_price,
                'city': item.find('.region', first=True).text,
            })
    return cars


def save_file(items, path):
    """ save the result """
    with open(path, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['Марка', 'Посилання', 'Ціна в $', 'Ціна в UAH', 'Місто'])
        for item in items:
            writer.writerow([item['title'], item['link'], item['usd_price'], item['uah_price'], item['city']])


def main():
    URL = input('Введите URL: ')
    URL = URL.strip()
    URL = parse_url(URL)
    response = get_html(URL)
    response.html.render(timeout=20)
    if response.status_code == 200:
        cars = []
        pages_count = get_pages_count(response)
        if x == 'newauto':
            i = range(1, pages_count + 1)
        else:
            i = range(0, pages_count)
        for page in i:
            print(f'Парсинг сторінки {page} із {pages_count}...')
            response = get_html(URL, params={'page': page})
            cars.extend(get_content(response))
        save_file(cars, FILE)
        print(f'Отримано {len(cars)} автівок')
        os.startfile(FILE)
    else:
        print('Error')


if __name__ == '__main__':
    main()
