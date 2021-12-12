# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient

class JobparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.vacancies

    def process_item(self, item, spider):
        if spider.name == 'hhru':
            final_salary = self.process_salary(item['salary'])
            item['min_salary'] = final_salary[0]
            item['max_salary'] = final_salary[1]
            item['currency'] = final_salary[2]
            del item['salary']
        else:
            final_salary = self.process_salary_sj(item['salary'])
            item['min_salary'] = final_salary[0]
            item['max_salary'] = final_salary[1]
            item['currency'] = final_salary[2]
            del item['salary']

        collection = self.mongo_base[spider.name]
        collection.insert_one(item)

        return item

    def process_salary(self, salary):
        salary_new = [x.replace(' ', '') for x in salary]
        salary_new = [x.replace(u'\xa0', u'') for x in salary_new]
        if salary is None:
            min_salary = None
            max_salary = None
            currency = None
        elif 'з/п не указана' in salary:
            min_salary = None
            max_salary = None
            currency = None
        else:
            if salary_new[0] == 'от' and salary_new[2] == 'до':
                min_salary = salary_new[1]
                max_salary = salary_new[3]
                currency = salary_new[5]
            elif salary_new[0] == 'до':
                min_salary = None
                max_salary = salary_new[1]
                currency = salary_new[3]
            elif salary_new[0] == 'от':
                min_salary = salary_new[1]
                max_salary = None
                currency = salary_new[3]
            else:
                min_salary = salary_new[0]
                max_salary = salary_new[2]
                currency = salary_new[4]

        return min_salary, max_salary, currency

    def process_salary_sj(self, salary):
        salary_new = [x.replace(u'\xa0', u' ') for x in salary]
        salary_new = [x for x in salary_new if len(x.strip())]
        if salary is None:
            min_salary = None
            max_salary = None
            currency = None
        elif 'По договорённости' in salary:
            min_salary = None
            max_salary = None
            currency = None
        else:
            if salary_new[0] == 'до':
                pos = salary_new[1].find('руб.')
                min_salary = None
                max_salary = salary_new[1][:pos]
                currency = salary_new[1].split().pop()
            elif salary_new[0] == 'от':
                pos = salary_new[1].find('руб.')
                min_salary = salary_new[1][:pos]
                max_salary = None
                currency = salary_new[1].split().pop()
            else:
                min_salary = salary_new[0]
                max_salary = salary_new[2]
                currency = salary_new[3]

        return min_salary, max_salary, currency


