#Задание 1. Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB
# и реализовать функцию, которая будет добавлять только новые вакансии/продукты в вашу базу.
import pymongo
from pymongo import MongoClient
import requests
from pprint import pprint
from bs4 import BeautifulSoup

client = MongoClient('127.0.0.1', 27017)
db = client['hh']
job = db.job

profession = input('Какую профессию будем искать? ') #прим. Big data analyst
page = int(input('Сколько страниц сайта вы хотели бы просмотреть? '))
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'}
params = {'clusters': 'true',
        'ored_clusters': 'true',
        'enable_snippets': 'true',
        'text': profession,
        'from': 'suggest_post',
        'search_field': 'description',
        'search_field': 'company_name',
        'search_field': 'name'}

url = 'https://hh.ru'

response = requests.get(url + '/search/vacancy', params=params, headers=headers)

dom = BeautifulSoup(response.text, 'html.parser')

vacancys = dom.find_all('div', {'class':'vacancy-serp-item'})
i = 1
while i <= page:

        for vacancy in vacancys:
                vacancy_data = {}
                id = job.create_index([('link', pymongo.TEXT)]) #Задаем id документа
                info = vacancy.find('span', {'class': 'resume-search-item__name'})
                name = info.getText() #Наименование вакансии
                link = info.find('a')['href'] #Ссылка на вакансию
                source = url #Ссылка на сайт
                salary = vacancy.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'}) #Условия, для нахождения з/п
                if salary is None:
                        salary_min = None
                        salary_max = None
                        currency = None
                else:
                        salary = salary.getText().replace(u'\u202f', u'')
                        salary = salary.split()
                        if salary[0] == 'до':
                                salary_min = None
                                salary_max = int(salary[1])
                                currency = str(salary[2])
                        elif salary[0] == 'от':
                                salary_min = int(salary[1])
                                salary_max = None
                                currency = str(salary[2])
                        else:
                                salary_min = int(salary[0])
                                salary_max = int(salary[2])
                                currency = str(salary[3])

                vacancy_data['name'] = name
                vacancy_data['link'] = link
                vacancy_data['source'] = source
                vacancy_data['salary_min'] = salary_min
                vacancy_data['salary_max'] = salary_max
                vacancy_data['salary_currency'] = currency

                try:
                    job.insert_one(vacancy_data)
                    #pprint(vacancy_data)
                except DuplicateKeyError:
                    print(f"Документ с id={vacancy_data['id']} уже существует")

        i += 1

        print(job.count_documents({}))

#Задание 2. Написать функцию, которая производит поиск и выводит на экран вакансии
# с заработной платой больше введённой суммы (необходимо анализировать оба поля зарплаты).

search_salary = int(input('Какую минимальную зарплату вы бы хотели получать? '))

for i in job.find({'$or':
    [{'salary_min': {'$gt': search_salary}},
     {'salary_max': {'$gt': search_salary}}]
                   }):
    pprint(i)
