import requests
from bs4 import BeautifulSoup
import csv
import os

HEADERS = {'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36 OPR/85.0.4341.72', 'accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'}
HOST = 'https://auto.ria.com'
FILE = 'cars.csv'

def get_html(url, params=None):
    r = requests.get(url, headers=HEADERS, params=params)
    return r

def get_pages_count(html):
    soup = BeautifulSoup(html, 'html.parser')
    pagination = soup.find('span', class_='dhide')
    if pagination:
        return int(pagination.get_text()[pagination.get_text().index("/") + 1:].strip())
    else:
        return 1

def get_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('section', class_='proposition')
    
    cars = []
    for item in items:
        uah_price = item.find('span', class_='size16')
        if uah_price:
            uah_price = uah_price.get_text(strip=True)
        else:
            uah_price = 'Уточняйте цену'
        cars.append({
            'title' : item.find('div', class_='proposition_title').get_text(strip=True),
            'link' : HOST + item.find('a', class_='proposition_link').get('href'),
            'usd_price' : item.find('span', class_='green').get_text(strip=True),
            'uah_price' : uah_price,
            'city' : item.find('span', class_='region').get_text(strip=True)
        })
    return cars

def save_file(items, path):
    with open(path, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['Марка', 'Ссылка', 'Цена в USD', 'Цена в UAH', 'Город'])
        for item in items:
            writer.writerow([item['title'], item['link'], item['usd_price'], item['uah_price'], item['city']])

def parse():
    URL = input('Введите ссылку: ')
    URL = URL.strip()
    html = get_html(URL)
    if html.status_code == 200:
        cars = []        
        pages_count = get_pages_count(html.text)
        for page in range(1, pages_count + 1):
            print(f'Парсинг страницы {page} / {pages_count}')
            html = get_html(URL, params = {'page' : page})
            cars.extend(get_content(html.text))
        save_file(cars, FILE)
        print("Получено автомобилей:", len(cars))
        os.startfile(FILE)
    else:
        print('Error')

parse()