import requests
from bs4 import BeautifulSoup

class ChampionatParser:
    def __init__(self):
        self.url = 'https://championat.com/'

    def get_news(self):
        # Logic for parsing Championat.com
        response = requests.get(self.url)
        soup = BeautifulSoup(response.text, 'html.parser')
        news_items = []
        # Example parsing logic
        for item in soup.find_all('div', class_='news-item'):
            title = item.find('h2').text
            link = item.find('a')['href']
            news_items.append({'title': title, 'link': link})
        return news_items

class SportsRuParser:
    def __init__(self):
        self.url = 'https://sports.ru/'

    def get_news(self):
        # Logic for parsing Sports.ru
        response = requests.get(self.url)
        soup = BeautifulSoup(response.text, 'html.parser')
        news_items = []
        # Example parsing logic
        for item in soup.find_all('div', class_='news-item'):
            title = item.find('h2').text
            link = item.find('a')['href']
            news_items.append({'title': title, 'link': link})
        return news_items

class SportboxRuParser:
    def __init__(self):
        self.url = 'https://sportbox.ru/'

    def get_news(self):
        # Logic for parsing Sportbox.ru
        response = requests.get(self.url)
        soup = BeautifulSoup(response.text, 'html.parser')
        news_items = []
        # Example parsing logic
        for item in soup.find_all('div', class_='news-item'):
            title = item.find('h2').text
            link = item.find('a')['href']
            news_items.append({'title': title, 'link': link})
        return news_items
