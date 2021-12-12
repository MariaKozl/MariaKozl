from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from pymongo import MongoClient
import requests
from pprint import pprint

client = MongoClient('127.0.0.1', 27017)
db = client['mail']
post_mail = db.post_mail

driver = webdriver.Chrome()
driver.maximize_window()
driver.implicitly_wait(10)
driver.get('https://account.mail.ru/')

#вводим имя пользователя
elem = driver.find_element(By.NAME, 'username')
elem.send_keys('study.ai_172@mail.ru')
elem.send_keys(Keys.ENTER)

#вводим пароль
elem = driver.find_element(By.NAME, 'password')
elem.send_keys('NextPassword172#')
elem.send_keys(Keys.ENTER)

#найдем количество писем в почте
elem = driver.find_element(By.XPATH, "//a[contains(@class, 'nav__item_active')]").get_attribute('title')
counts_mail = int(elem.split()[1])
print(counts_mail)

#соберем все ссылки на письма
links = []
i = 0
for i in range(counts_mail):
    link = driver.find_element(By.XPATH, "//a[contains(@href, '/inbox/0:')]").get_attribute('href')
    links.append(link)
    i += 1
print(links)

#зайдем внутрь первого письма
mail = driver.find_element(By.XPATH, "//a[contains(@href, '/inbox/0:')]")
mail.send_keys(Keys.ENTER)

#соберем всю информацию
num = 0
while True:
    mails_info = {}
    id_mail = links[num].split('/')[-1] #задаем id для сохранения в БД
    link_mail = links[num]
    sender_mail = driver.find_element(By.XPATH, "//div[@class='letter__author']/span[@class='letter-contact']").get_attribute('title')
    date_mail = driver.find_element(By.XPATH, "//div[contains(@class, 'letter__date')]").text
    body_mail = driver.find_element(By.XPATH, "//div[contains(@class, 'letter-body__body-content')]").text

    mails_info['id'] = id_mail
    mails_info['link_mail'] = link_mail
    mails_info['sender_mail'] = sender_mail
    mails_info['date_mail'] = date_mail
    mails_info['body_mail'] = body_mail

#сложим информацию о письме в БД
    try:
        post_mail.insert_one(mails_info)
    except DuplicateKeyError:
        print(f"Документ с id={mails_info['id']} уже существует")

#для перемещения к следующему письму воспользуемся кнопкой "следующее"
    element = driver.find_element(By.XPATH, "//div[contains(@class, 'portal-menu-element_next')]")
    element.click()
    #button.send_keys(Keys.CONTROL)
    #button.send_keys(Keys.ARROW_DOWN)

    num += 1

print(mails_info)

driver.quit()
