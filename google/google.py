# %% [markdown]
# ### Logger

# %%
with open('../common/logger.py') as f:
    exec(f.read())

logger = get_logger(name='google')
logger.info('Start crawl google')

# %% [markdown]
# ### Import

# %%
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import importlib.util
import os

# %%
def get_module(module_name, file_name):
    name = file_name.split('.')[0]

    module_path = os.path.join(os.getcwd(), '..', module_name, file_name)
    spec = importlib.util.spec_from_file_location(name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# %%
driver_module = get_module('common', 'web_driver.py')
get_driver = driver_module.get_driver

# %% [markdown]
# ### Init driver

# %%
driver = get_driver()

# %% [markdown]
# ### Find element

# %%
TAT_CA_CAC_TU = 'samsung'
CUM_TU_CHINH_XAC = '"bypass KNOX" OR "bypass samsung"' # chua 1 trong cac cum tu
BAT_KY_TU_NAO = 'KNOX KG hack bypass attack' # chưa 1 trong cac tu nay
KHONG_TU_NAO = ''

# %%
try:
    driver.get("https://www.google.com/advanced_search")

    #setup rule
    elem = driver.find_element(By.ID, "xX4UFf")
    elem.clear()
    elem.send_keys(TAT_CA_CAC_TU)

    elem = driver.find_element(By.ID, "CwYCWc")
    elem.clear()
    elem.send_keys(CUM_TU_CHINH_XAC)

    elem = driver.find_element(By.ID, "mSoczb")
    elem.clear()
    elem.send_keys(BAT_KY_TU_NAO)

    elem = driver.find_element(By.ID, "t2dX1c")
    elem.clear()
    elem.send_keys(KHONG_TU_NAO)
    
    elem = driver.find_element(By.ID, "xX4UFf")
    elem.send_keys(Keys.ENTER)
except Exception as e:
    logger.error(f'Selenium google search advanced: {e}')

# %%
try:
    # Chon Website only
    try:
        elem = driver.find_element(By.XPATH, "//div[@class='YmvwI1' or contains(text(), 'Web')]")
        # Tim thay
        elem.click()
        logger.info('Click option website')
    except NoSuchElementException:
        # Them -> Chon website only
        logger.info("Chua tim thay website only -> chon: them option")
        elem = driver.find_element(By.XPATH, "//div[@class='Lu57id']")
        elem.click()
        elem = driver.find_element(By.XPATH, "//div[@class='YmvwI' and contains(text(), 'Web')]")
        elem.click()

    # open filter
    elem = driver.find_element(By.XPATH, "//div[@class='BaegVc YmvwI' and contains(text(), 'Công cụ')]")
    elem.click()

    # filter date time
    elem = driver.find_element(By.XPATH, "//div[@class='KTBKoe' and (contains(text(), 'Mọi lúc') or contains(text(), 'Any time')) ]")
    elem.click()

    elem = driver.find_element(By.XPATH, "//a[(contains(text(), 'Tuần qua') or contains(text(), 'Past week'))]")
    elem.click()
except Exception as e:
    logger.error(f'Selenium google advanced search result: {e}')

# %%
google_links = []
list_ignore = ['youtube.com']
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
    logger.info(f'Selenium search result many pages: {e}')

# %%
google_links

# %% [markdown]
# ### Save data

# %%
COL_TYPE = 'Type'
COL_LINK = 'Link'
COL_TITLE = 'Title'
COL_DES = 'Short description'
COL_CONTENT = 'Web content'
COL_SUMMARY = 'Summary'

# %%
data = []

for i, link in enumerate(google_links):
    row = {
        COL_TYPE:'google',
        COL_LINK: link["link"],
        COL_TITLE: link["title"],
        COL_DES: link["description"]
    }
    data.append(row)

# %%
len(google_links)

# %%
import os
import pandas as pd
from datetime import datetime
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

# %%
import sys
driver.quit()
sys.exit()

# %% [markdown]
# ### GENAI

# %%
# import genai
genai_module = get_module('common', 'genai.py')
Genai = genai_module.Genai

# %%
import requests
from bs4 import BeautifulSoup

def get_webpage_content(url):
    try:
        # Lấy dữ liệu từ URL
        response = requests.get(url)
        # Sử dụng BeautifulSoup để phân tích cú pháp HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Lấy toàn bộ văn bản trong trang web
        paragraphs = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'b', 'i', 'u', 'span'])
        text = '\n'.join([para.get_text() for para in paragraphs])
        
        return text
    except Exception as e:
        logger.error('Genai get web content')
        return ""

# %%
genai = Genai()

# %%
# # summary
# for row in data:
#     content  = get_webpage_content(row[COL_LINK])
#     summary  = genai.search(content)
#     row[COL_CONTENT] = content
#     row[COL_GENAI] = summary
#     print(f'{row[COL_LINK]}')
#     print(summary)
#     print("-----------------------------")

# %% [markdown]
# ### Save data

# %%
import pandas as pd
import os
from datetime import datetime

try:
    today = datetime.today().date()
    file_path = f'..//output//output_{today}.xlsx'
    sheet_name = f'gooogle_{today}'

    columns = [COL_TYPE, COL_LINK, COL_TITLE, COL_DES, COL_CONTENT, COL_SUMMARY ]
    df = pd.DataFrame(data, columns=columns)

    # Check exist file 
    if os.path.exists(file_path):
        with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='new') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    else:
        with pd.ExcelWriter(file_path, engine='openpyxl', mode='w') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)

    logger.info(f'Exported {len(data)} data successful')
except Exception as e:
    logger.error(f'Save data fail: {e}')


