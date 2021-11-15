import requests
from pprint import pprint
from bs4 import BeautifulSoup

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
        vacancys_list = []
        for vacancy in vacancys:
                vacancy_data = {}
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
                        salary = salary.getText().split()
                        if salary[0] == 'до':
                                salary_min = None
                                salary_max = int(salary[1]+salary[2])
                                currency = str(salary[3])
                        elif salary[0] == 'от':
                                salary_min = int(salary[1]+salary[2])
                                salary_max = None
                                currency = str(salary[3])
                        else:
                                salary_min = int(salary[0]+salary[1])
                                salary_max = int(salary[3]+salary[4])
                                currency = str(salary[5])

                vacancy_data['name'] = name
                vacancy_data['link'] = link
                vacancy_data['source'] = source
                vacancy_data['salary_min'] = salary_min
                vacancy_data['salary_max'] = salary_max
                vacancy_data['salary_currency'] = currency

                vacancys_list.append(vacancy_data)

        i += 1
        pprint(vacancys_list)
        #pprint(len(vacancys_list)) для проверки
