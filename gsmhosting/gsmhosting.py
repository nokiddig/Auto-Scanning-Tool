with open('../common/logger.py') as f:
    exec(f.read())

logger = get_logger(name='gsm')
logger.info('Start crawl gsm-forum')
# ### Import
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

import os
import sys
import importlib
def get_module(module_name, file_name):
    name = file_name.split('.')[0]

    module_path = os.path.join(os.getcwd(), '..', module_name, file_name)
    spec = importlib.util.spec_from_file_location(name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

try:
    driver_module = get_module('common', 'web_driver.py')
    get_driver = driver_module.get_driver
except ImportError as e:
    logger.error(f'Import web driver fail: {e}')
except Exception as e:
    logger.error(e)

# ### Crawl selenium

try:
    driver = get_driver()
    driver.get("https://forum.gsmhosting.com/vbb/f209/")
except Exception as e:
    logger.error(f'Init driver fail: {e}')
    sys.exit()

links = []
try:
    raw_links = driver.find_elements(By.CLASS_NAME, "alt1Active")
    for link in raw_links:
        a_tag = link.find_element(By.TAG_NAME, "a")
        title = link.text
        href = a_tag.get_attribute("href")

        links.append({'title': title, 'link':href})
        
except Exception as e:
    logger.error(f'Crawl selenium: {e}')
    

DAY = 1
MONTH = 7
YEAR = 2024

KEY_WORDS = ["unlock", "hack", "samsung", "s2", "flip", "fold", "knox"]

import re
import datetime
from time import strptime

# convert string to datetime
date_str = '2022-01-15'
date_obj = strptime(date_str, '%Y-%m-%d')

def get_threads_from_link(wdriver, link):
    thread_links = []
    wdriver.get(link['link'])
    print(link['title'])

    rows = wdriver.find_elements(By.XPATH, "//*[contains(@id, 'thread_title')]")
    times = wdriver.find_elements(By.CSS_SELECTOR, "div.smallfont[style*='text-align:right; white-space:nowrap']")

    for i, (row, time) in enumerate(zip(rows, times)):
        title = row.text
        link = row.get_attribute('href')
        creatAt = time.text 

        pattern = r'(\d{2}-\d{2}-\d{4})'
        match = re.search(pattern, time.text)
        if match:
            creatAt = match.group(1)
        else:
            creatAt = None

        if(creatAt != None): 
            thread_links.append({'title': row.text, 'link':link, 'creatAt': creatAt})
        # print(f"Row {i+1}: {title} \n{link} \n{creatAt}\n")

    month_str = str(MONTH).zfill(2)
    day_str = str(DAY).zfill(2)
    year_str = str(YEAR)
    deadline = month_str + '-' + day_str + '-' + year_str

    thread_links_by_deadline = [item for item in thread_links if strptime(item['creatAt'], '%m-%d-%Y') >= strptime(deadline, '%m-%d-%Y')]
    thread_links_by_keywords = [item for item in thread_links_by_deadline if any(keyword in item['title'].lower() for keyword in KEY_WORDS)]

    for i, thread_link in enumerate(thread_links_by_keywords):
        print(f"Link {i+1}: {thread_link['title']} \n{thread_link['link']} \n{thread_link['creatAt']}\n")

    return thread_links_by_keywords


driver.implicitly_wait(20)


total_thread_links = []
try: 
    for link in (links):
        total_thread_links += get_threads_from_link(driver, link)

    for i, thread_link in enumerate(total_thread_links):
        print(i) 
        print(thread_link['title'])
        print(thread_link['link'])
        print(thread_link['creatAt'])
        print()
except Exception as e:
    logger.error(f'total_thread_links: {e}')


# ### Get comment
from time import sleep
def getDataByLink(driver,url = ''):
    driver.get(url)
    # link to the last page of commens(earliest)
    try:
        elem = driver.find_element(By.XPATH, "//a[@class='smallfont' and contains(text(), 'Last ')]")
        elem.click()
        sleep(3)
    except Exception as e:
        print(f"1 page found")

    # lay 5 the div cuoi cung co id la post...
    edit_divs = driver.find_elements(By.CSS_SELECTOR, "table[id^='post']:nth-last-of-type(-n+5)")
    
    # get 5 comments
    list_answers = []
    for div in reversed(edit_divs):
        div_id = div.get_attribute("id")    #ex: edit14872555
        id = div_id[4:]                     #ex: 14872555

        content = div.find_element(By.ID, f"post_message_{id}").text
        list_answers.append(content)
    return list_answers


list_answers = []
try:
    for i, thread_link in enumerate(total_thread_links):
        print(f"Thread {i}: {thread_link['link']}")
        list_answers.append(getDataByLink(driver, thread_link['link']))
        
except Exception as e:
    logger.error(f'Get data by link: {e}')


COL_TYPE = 'Type'
COL_LINK = 'Link'
COL_PUBLISHED = 'Published at'
COL_TITLE = 'Title'
COL_CONTENT = 'Content'
COL_SUMMARY = 'Summary'


# collect data
MIN_WORDS = 30
data = []

for i, thread_link in enumerate(total_thread_links):
    comment = ''.join(list_answers[i][0:5])
    row = {
        COL_TYPE:'gsm',
        COL_LINK: thread_link["link"],
        COL_PUBLISHED: thread_link["creatAt"], 
        COL_TITLE: thread_link["title"], 
        COL_CONTENT: comment
    }
    if len(comment) >= MIN_WORDS:
        data.append(row)

# ### Genai
from time import sleep


genai_module = get_module('common', 'genai.py')
Genai = genai_module.Genai
genai = Genai()

# ### Insert data

#summary
list_summary = []

sleep(5)
try:    
    for i, row in enumerate(data):
        text = row[COL_CONTENT]
        summary = genai.search(text)
        print(f' {i} ==============================================================')
        # print(f'Origin: {text}')
        print(f'Summary: {summary}')
        
        list_summary.append(summary)
        sleep(1)
        
except Exception as e:
    logger.error(f'Genai summary: {e}')

for i, row in enumerate(data):
    if i<len(list_summary):
        row[COL_SUMMARY] = ''.join(list_summary[i])
    else:
        row[COL_SUMMARY] = ''

# %% [markdown]
# #### Save data

# %%
data

# %%
import os
import pandas as pd
from datetime import datetime
try:
    today = datetime.today().date()

    columns = [COL_TYPE, COL_LINK, COL_PUBLISHED, COL_TITLE, COL_CONTENT, COL_SUMMARY]
    df = pd.DataFrame(data, columns=columns)

    file_path = f'..//output//output_{today}.xlsx'
    sheet_name = f'gsm_{today}'

    if os.path.exists(file_path):
        with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='new') as writer:
            if sheet_name in writer.book.sheetnames:
            # Xóa sheet cũ
                writer.book.remove(writer.book[sheet_name])
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    else:
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    logger.info(f'Export {len(data)} data successful')
except Exception as e:
    logger.error(f'Save data fail: {e}')

# %% [markdown]
# 


