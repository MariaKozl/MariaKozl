#Задание 1. Написать приложение, которое собирает основные новости с сайта на выбор news.mail.ru,
# lenta.ru, yandex-новости. Для парсинга использовать XPath. Структура данных должна содержать:
# название источника; наименование новости; ссылку на новость; дата публикации.
from lxml import html
import pymongo
from pymongo import MongoClient
import requests
from pprint import pprint

client = MongoClient('127.0.0.1', 27017)
db = client['mail']
news = db.news

header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'}
url = 'https://news.mail.ru/'
response = requests.get(url, headers=header)

dom = html.fromstring(response.text)

#собираем ссылки на новости вверху страницы (5 штук с фото и 6 штук ниже в виде списка = 11 штук)

#names_news = dom.xpath("//div[contains(@class, 'daynews__item')] | //a[@class='list__text']") #можно наименование новости взять на этом этапе
links_news = dom.xpath("//a[contains(@class, 'js-topnews__item')]/@href | //a[@class='list__text']/@href")

#print(len(names_news))
#pprint(len(links_news))


#создаем цикл с get-запросом по ссылкам
num = 0
for new in links_news:
    news_info = {}
    response_news = requests.get(links_news[num], headers=header)
    dom_news = html.fromstring(response_news.text)

    id_news = links_news[num].split('/')[-2] #задаем id для сохранения в БД
    source_news = dom_news.xpath("//span[@class='note']//span[@class='link__text']/text()") #название источника
    names_news = dom_news.xpath("//h1/text()") #наименование новости
    date_news = dom_news.xpath("//span[@class='note']//@datetime")[0]

    news_info['id'] = id_news
    news_info['source_news'] = source_news
    news_info['names_news'] = names_news
    news_info['date_news'] = date_news

    pprint(news_info)

#Задание 2. Сложить собранные новости в БД.
    try:
        news.insert_one(news_info)
    except DuplicateKeyError:
        print(f"Документ с id={news_info['id']} уже существует")

    num += 1

print(news.count_documents({}))
