# %% [markdown]
# ### Get link

# %% [markdown]
# Doc: https://developers.google.com/youtube/v3/docs/search/list?hl=vi

# %%
import certifi
certifi.where()
cert_path = certifi.where()

# %% [markdown]
# ### Logger

# %%
with open('../common/logger.py') as f:
    exec(f.read())

logger = get_logger(name='youtube')
logger.info('Start crawl youtube')

# %%
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

import os
import sys
import importlib

# %%
def get_module(module_name, file_name):
    name = file_name.split('.')[0]

    module_path = os.path.join(os.getcwd(), '..', module_name, file_name)
    spec = importlib.util.spec_from_file_location(name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# %%
variable_module = get_module('internal', 'variable.py')
API_KEY = variable_module.API_KEY
CHROMEDRIVER_PATH = variable_module.CHROMEDRIVER_PATH

# %%
driver_module = get_module('common', 'web_driver.py')
get_driver = driver_module.get_driver

# %%
driver = get_driver()

# %%
# limit time query
from datetime import datetime
from dateutil.relativedelta import relativedelta

def get_previous_date(month, day):
    today = datetime.now()

    # Lấy ngày của tháng trước
    previous_month_date = today - relativedelta(months=month, days=day)

    # Chuyển đổi sang định dạng yêu cầu "YYYY-MM-DDTHH:MM:SSZ"
    formatted_date = previous_month_date.strftime("%Y-%m-%dT%H:%M:%SZ")

    return formatted_date


# %%
import urllib.parse
import json
from time import sleep


# URL của API YouTube
API_URL = 'https://www.googleapis.com/youtube/v3/search'

def search_youtube(query, before, after):
    headers = {
        'Content-Type': 'application/json',
        'accept': 'application/json',
    }
    params = {
        'q': query,
        'part': 'snippet',
        'type': 'video',
        'order': 'date',
        'publishedBefore': before,
        'publishedAfter': after,
        'maxResults': 50,
        'key': API_KEY
    }
    
    # response = requests.get(API_URL, params=params, headers=headers, verify=False)
    # response.raise_for_status()  # Raise an exception for HTTP errors
    # items = response.json()['items']

    param_string = urllib.parse.urlencode(params)
    driver.get(f"{API_URL}?{param_string}")
    sleep(2)
    
    json_res = driver.find_element(By.TAG_NAME, 'pre').text
    response = json.loads(json_res)  # Convert the JSON string to a Python dictionary
    items = response['items']
    return items

# %%
query = "samsung+kg+mdm+unlock"
before_date = get_previous_date(month=0, day=0) # end
after_date = get_previous_date(month=1, day=0) # start

search_result = search_youtube(query= query, before=before_date, after=after_date)

# %%
search_result

# %%
video_ids = [item['id']['videoId'] for item in search_result]

# %% [markdown]
# ### Get data API

# %%
# get video id
from urllib.parse import urlparse, parse_qs

def get_video_id(url):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    return query_params.get('v', [None])[0]

# %%
#print json
import json

def prinJson(data):
    formatted_json = json.dumps(data, indent=4, ensure_ascii=False)
    print(formatted_json)

# %%
COL_TYPE = 'Type'
COL_LINK = 'Link'
COL_TITLE = 'Title'
COL_PUBLISHED = 'Published at'
COL_DES = 'Short description'
COL_CONTENT = 'Web content'
COL_SUMMARY = 'Summary'

# %%
import requests
from time import sleep
# requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'ALL:@SECLEVEL=1'

# URL của API YouTube
API_URL_VIDEO_INFO = 'https://www.googleapis.com/youtube/v3/videos'

def get_video_info(video_id):
    headers = {
        'Content-Type': 'application/json',
        'accept': 'application/json',
    }

    params = {
        'part': 'snippet,contentDetails,statistics',
        'id': video_id,
        'key': API_KEY
    }
    # response = requests.get(API_URL_VIDEO_INFO, params=params, headers=headers, verify=False)
    # response.raise_for_status()  # Raise an exception for HTTP errors
    
    # video_info = response.json()['items'][0]

    param_string = urllib.parse.urlencode(params)
    driver.get(f"{API_URL_VIDEO_INFO}?{param_string}")
    # print(f"{API_URL_VIDEO_INFO}?{param_string}")
    sleep(2)
    
    json_res = driver.find_element(By.TAG_NAME, 'pre').text
    response = json.loads(json_res)  # Convert the JSON string to a Python dictionary
    video_info = response['items'][0]

    return video_info

def get_data(link, video_info):
    title = video_info['snippet']['title']
    description = video_info['snippet']['description']
    published_at = video_info['snippet']['publishedAt']
    res = {
        COL_TYPE: 'youtube',
        COL_LINK: link,
        COL_PUBLISHED: published_at,
        COL_TITLE: title,
        COL_DES: description
    }
    return res

# %%
#ignore title
ignore_word = ["T Mobile", "US Cellular", "Sprint USA", "Unlock Service", "Xfinity USA", "Cricket USA", "FRP", "Boost USA", "Verizon USA", "Spectrum", "Lost mode", "Huawei",
                   "Xiaomi", "screen lock", "TFN", "iphone", "icloud"]
def checkContain(title):
    title = title.lower()
    for word in ignore_word:
        if word.lower() in title:
            return True
    else:
        return False

# %%
data = []
try:
    for i, video_id in enumerate(video_ids):
        video_info = get_video_info(video_id)
        link = f"https://www.youtube.com/watch?v={video_id}"
        data_row = get_data(link, video_info)
        title = data_row[COL_TITLE]
        if checkContain(title = title):
            data.append(data_row)
            print (f'{i} {data_row[COL_TITLE]}')
    logger.info(f'Get video info success')
except Exception as e:
    logger.error(f'Get video info err: {e}')

# %% [markdown]
# # GENAI

# %%
genai_module = get_module('common', 'genai.py')
Genai = genai_module.Genai

# %%
genai = Genai()

# %%
for i, row in enumerate(data):
    try:
        summary  = genai.search(row[COL_DES])
        print(summary)
        print(f"{i}. -----------------------------")
        row[COL_SUMMARY] = summary

    except Exception as e:
        logger.error(f'Query genai fail: {e}')
        row[COL_SUMMARY] = ''

# %% [markdown]
# ### Save data

# %%
data

# %%
import pandas as pd
import os
from datetime import datetime
from openpyxl import load_workbook
try:
    today = datetime.today().date()
    df = pd.DataFrame(data)

    file_path = f'..//output//output_{today}.xlsx'
    sheet_name = f'youtube_{today}'

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
    logger.error(f"Save data fail: {e}")

# %%
print('Success')

# %% [markdown]
# query"
# ("Samsung Knox Guard" OR "Samsung MDM" OR "Samsung KG") AND ("unlock" OR "unfasten" OR "unbolt" OR "open" OR "release" OR "unlatch" OR "disengage" OR "free" OR "unseal" OR "uncover" OR "access") AND ("bypass" OR "circumvent" OR "avoid" OR "sidestep" OR "evade" OR "skip" OR "dodge" OR "work around" OR "ignore" OR "overcome" OR "elude") AND ("removal" OR "elimination" OR "deletion" OR "eradication" OR "extraction" OR "withdrawal" OR "dismissal" OR "expulsion" OR "displacement" OR "ouster" OR "exclusion") AND ("tool" OR "software" OR "method" OR "technique" OR "unlocker" OR "key generator" OR "exploit" OR "vulnerability" OR "APK") AND ("ADB" OR "flash firmware") AND ("guide" OR "tutorial" OR "step-by-step" OR "how-to") AND ("legal" OR "issues" OR "compatibility" OR "support") AND ("community forums" OR "troubleshooting") AND ("2024" OR "updated methods") AND ("Galaxy S-series" OR "Note-series" OR "latest security patch") AND (date:2024-08)
# 
# 32 words only for google search:
# ("Samsung Knox Guard" OR "Samsung MDM" OR "Samsung KG") AND ("unlock" OR "bypass" OR "removal") AND ("tool" OR "method" OR "software" OR "guide") AND ("August 2024" OR "latest update")
# 


