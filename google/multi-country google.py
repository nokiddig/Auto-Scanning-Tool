from langdetect import detect
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import importlib.util
import os
import pandas as pd
from datetime import datetime

COUNTRIES = ['Ghana', 'Kenya', 'Liberia', 
             'Malawi', 'Mauritania', 'Morocco',
             'Mozambique', 'Nigeria', 'Sierra Leone', 
             'Somalia', 'South Africa', 'Tanzania', 
             'Zambia', 'Thailand']

LANGUAGES = {
    'Ghana': ['English'],
    'Kenya': ['English', 'Swahili'],
    'Liberia': ['English'],
    'Malawi': ['Chichewa', 'English'],
    'Mauritania': ['Arabic'],
    'Morocco': ['Arabic'],
    'Mozambique': ['Portuguese'],
    'Nigeria': ['English'],
    'Sierra Leone': ['English'],
    'Somalia': ['Somali'],
    'South Africa': ['Afrikaans', 'English', 'Zulu'],
    'Tanzania': ['Swahili', 'English'],
    'Zambia': ['English'],
    'Thailand': ['Thai']
}

LANGUAGES_CODES = {
    'English': 'en',
    'Swahili': 'sw',
    'Arabic': 'ar',
    'Portuguese': 'pt',
    'Somali': 'so',
    'Afrikaans': 'af',
    'Chichewa': 'ny',
    'Northern Sotho': 'ns',
    'Ndebele': 'nr',
    'Siswati': 'ss',
    'Tswana': 'tn',
    'Tsonga': 'ts',
    'Venda': 've',
    'Xhosa': 'xh',
    'Zulu': 'zu',
    'Thai': 'th'
}

COUNTRY_CODES = {
    'Ghana': 'GH',
    'Kenya': 'KE',
    'Liberia': 'LR',
    'Malawi': 'MW',
    'Mauritania': 'MR',
    'Morocco': 'MA',
    'Mozambique': 'MZ',
    'Nigeria': 'NG',
    'Sierra Leone': 'SL',
    'Somalia': 'SO',
    'South Africa': 'ZA',
    'Tanzania': 'TZ',
    'Zambia': 'ZM',
    'Thailand': 'TH'
}

TAT_CA_CAC_TU = 'bypass knox samsung'
CUM_TU_CHINH_XAC = ''
BAT_KY_TU_NAO = ''
KHONG_TU_NAO = ''

COL_TYPE = 'Type'
COL_LINK = 'Link'
COL_TITLE = 'Title'
COL_DES = 'Short description'
COL_CONTENT = 'Web content'
COL_SUMMARY = 'Summary'

def getAPIURL(text, from_lang, to_lang):
    return f"https://api.mymemory.translated.net/get?q={text}&langpair={from_lang}%7C{to_lang}"

def translateUsingApi(text):
    from_lang = detect(text)
    url = getAPIURL(text, from_lang, 'en')
    response = requests.get(url, verify=False)
    data = response.json()
    response.raise_for_status() # Raise an exception for HTTP errors
    data['responseData']['translatedText']
    return data['responseData']['translatedText']

with open('../common/logger.py') as f:
    exec(f.read())

logger = get_logger(name='google')
logger.info('Start crawl multi-country google')
logger

def get_module(module_name, file_name):
    name = file_name.split('.')[0]

    module_path = os.path.join(os.getcwd(), '..', module_name, file_name)
    spec = importlib.util.spec_from_file_location(name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

driver_module = get_module('common', 'web_driver.py')
get_driver = driver_module.get_driver
driver = get_driver()

try:
    driver.get("https://www.google.com/advanced_search")
    elems = driver.find_elements(By.TAG_NAME, "input")
    elems[0].send_keys(TAT_CA_CAC_TU)
    elems[1].send_keys(CUM_TU_CHINH_XAC)
    elems[2].send_keys(BAT_KY_TU_NAO)
    elems[3].send_keys(KHONG_TU_NAO)
    elems[14].send_keys(Keys.ENTER)
except Exception as e:
    logger.error(f'Selenium google search advanced: {e}')

url = driver.current_url
urlByCountry = []
for country in COUNTRIES:
    new_url = url + "&cr=country" + COUNTRY_CODES[country]
    urlByCountry.append(new_url)

google_links = []

def preprocess():
    try:
        cur_url = driver.current_url
        driver.get(cur_url+"&udm=14&tbs=qdr:w")
    except Exception as e:
        logger.error(f'Selenium google filter search result: {e}')

def process():    
    list_ignore = ['youtube.com', 'samsung.com']
    try:
        while(1):
            elem = driver.find_elements(By.CSS_SELECTOR, 'div.g')
            for e in elem:
                title       = e.find_element(By.TAG_NAME, 'h3').text
                link        = e.find_element(By.TAG_NAME, 'a').get_attribute("href")
                elem        = e.find_elements(By.TAG_NAME, 'span')
                website     = elem[2].text 
                elem        = e.find_element(By.TAG_NAME, 'div')
                elem        = elem.find_elements(By.TAG_NAME, 'div')
                description = elem[-2].text
                if all(ignore not in link for ignore in list_ignore):
                    google_links.append({'title': title, 'link': link, 'description': description, 'website': website})

            # next page    
            elem = driver.find_element(By.ID, "pnnext")
            elem.click()

    except NoSuchElementException:
        logger.info('Searched all pages!')
    except Exception as e:
        logger.info(f'Selenium search filter many pages: {e}')

for url in urlByCountry:
    driver.get(url)
    preprocess()
    process()

for link in google_links:
    try:
        if(detect(link["description"])!= 'en'):
            original = link["description"]
            translate = translateUsingApi(original)
            link["description"] = "Translate by API: " + translate + "\nOriginal: " + original
    except:
        pass
    try:
        if(detect(link["title"])!= 'en'):
            original = link["title"]
            translate = translateUsingApi(original)
            link["title"] = "Translate by API: " + translate + "\nOriginal: " + original
    except:
        pass

data = []

for i, link in enumerate(google_links):
    row = {
        COL_TYPE:'google',
        COL_LINK: link["link"],
        COL_TITLE: link["title"],
        COL_DES: link["description"]
    }
    data.append(row)

try:
    today = datetime.today().date()
    file_path = f'..//output//output_{today}.xlsx'
    sheet_name = f'google_{today}'

    columns = [COL_TYPE, COL_LINK, COL_TITLE, COL_DES]
    df = pd.DataFrame(data, columns=columns)

    # Check file exist, delete old sheet before add new sheet
    if os.path.exists(file_path):
        with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='new') as writer:
            if sheet_name in writer.book.sheetnames:
                writer.book.remove(writer.book[sheet_name])
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    else:
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)

    logger.info(f'Exported {len(data)} data successful')
except Exception as e:
    logger.error(f'Save data fail: {e}')