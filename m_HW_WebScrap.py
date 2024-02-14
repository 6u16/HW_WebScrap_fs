# Домашнее задание к лекции 6.«Web-scrapping»

import requests
import bs4  # библиотека beautifulsoup4 - будемиспользовать для парсинга днных вместо регулярных выражений
import lxml  # библиотека движок для beautifulsoup4, без неё неработает beautifulsoup4
import fake_headers  # библиотека для формирования загловков, чтобы сайт не думал что мы робот
import json
import os

from pprint import pprint


# Определяем списки ключевых слов:
l_kw_city = ['Москва', 'Санкт-Петербург']
l_kw_pl = ['Django', 'Flask']
s_kw_salary = 'USD'

# Функция для генерации заголовков(с пмощью fake_headers)
def gen_headers():
    headers_gen = fake_headers.Headers(os='win', browser='chrome')  # Передаём в перемнные нашу операционку и браузер которым пользуемся
    return headers_gen.generate()  # генерация слваря

# Функция парснга headhunter по ключевым словам
def pars_hh():
    URL = 'https://spb.hh.ru/search/vacancy?text=python&area=1&area=2'

    response = requests.get(URL, headers=gen_headers())  # Тут добавим в параметр headers= библиотеку fake-headers - для того чтобы сайт нас не заблокировал как робота

    # Структурируем наши запросы чтобы небыло путаницы
    main_html = response.text  # main_html - наша страница со всеми статьями
    main_page = bs4.BeautifulSoup(main_html, features='lxml')
    article_list_tag = main_page.find(name='div', id='a11y-main-content')  # <div class="a11y-main-content"> - путь поиска статей
    article_tags = article_list_tag.find_all(name='div', class_='serp-item serp-item_link')  # сюда добавляем наши статьи и по ним можно будет итерироваться

    article_data = []  # список наших извлечённых данных

    for article_tag in article_tags:
        # Извлеаем элементы, а позже извлечём из них конкретику
        main_info_tag = article_tag.find(name='div', class_='vacancy-serp-item-body__main-info')

        # Ссылка на вакансию
        a_tag = article_tag.find(name='a', class_='bloko-link')  # здесь будет ссылка этой статьи
        link = a_tag['href']  # обращемся к тегу a_tag за ссылкой через пиисок
        
        # Извлекаем зарплатную вилку
        salary = main_info_tag.find(name='span', class_='bloko-header-section-2')
        if salary != None: salary = salary.text.strip().replace('\u202f', '.')  # Условие, чтобы преобразовывать текст, когда class != None
        
        # Извлекаем только зназвание копании, его же уберём из ткста города, по другому доступа нет
        co_name_tag = main_info_tag.find(name='a', class_='bloko-link bloko-link_kind-tertiary')
        if co_name_tag != None:
            co_name_tmp = co_name_tag.text.strip()  # Неформатирванную строку будем использовать для исключеия и даннх о городе
            co_name = co_name_tmp.replace('\xa0', ' ')
        
        # Извлекаем город, доступен только с компнией, убираем компанию
        city_tag = main_info_tag.find(name='div', class_='vacancy-serp-item__info')
        if city_tag != None:
            city = city_tag.text.strip().replace(co_name_tmp, '')
        
        
        ## Текст статьи это уже отдельный запрос по ссылке, которую найдём в элементе main_page
        # Извлекаем полный текст статьи
        response = requests.get(link, headers=gen_headers()) 
        article_html = response.text
        article_page = bs4.BeautifulSoup(article_html, features='lxml')
        article_body_tag = article_page.find(name='div', class_='g-user-content')
        artcle_text = article_body_tag.text.strip()
        
        for elem in l_kw_pl:
            if artcle_text.count(elem):
                article_data.append({
                            'link': link,
                            'salary':salary,
                            'co_name': co_name,
                            'city': city,
                            'l_kw_pl': elem
                            })
        
        # Сделан отдельный вывод по условию USD так как сейчас это редкость для первой страницы
        for elem in l_kw_pl:
            if artcle_text.count(elem):
                if salary != None: 
                    if salary.count(s_kw_salary):
                        article_data.append({
                                    'link': link,
                                    'salary':salary,
                                    'co_name': co_name,
                                    'city': city,
                                    'l_kw_pl': elem
                                    })
        
    pprint(article_data, width=240, sort_dicts=False)  # выводим данные без сортировки(нам нужно: ссылка, вилка зп, название компании, город)
    return article_data

pars_hh()

# ЗАПИСЬ в json
def wrt_dump(l_data):
    file_path = os.path.join(os.getcwd(), 'HW_ALL\MPI\HW_WebScrap\data')  # строительство путик нашему файлу
    with open(f'{file_path}/vacancy.json', 'w', encoding='utf-8') as f:
        json.dump(l_data, f, ensure_ascii=False, indent=3) # добавляем две настройки 1:ensure_ascii=False - чтобы видеть русский, 2:indent=2 - отступ(читаемость)

wrt_dump(pars_hh())


















## Ваш код