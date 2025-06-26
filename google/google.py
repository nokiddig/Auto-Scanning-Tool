# Auto Scanning Tool for Google version 1.0.1
# This current version is designed to optimaze search in countries that Samsung supports in Africa and Thailand.

#####################################################
##################### LIBRARIES #####################
#####################################################

from datetime import datetime
from datetime import timedelta
import pandas as pd
import os
import time
import random
import importlib.util
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
import requests
from langdetect import detect

############################################################
##################### GLOBAL VARIABLES #####################
############################################################

# List to store the links found during the search.
google_links = []

# Global variables to store the web driver module and instance.
driver_module = None
driver = None

# List to store the data to be stored in the Excel file.
excel_data = []

#####################################################
##################### FUNCTIONS #####################
#####################################################

# Import common logger module to log the progress of the script.
with open('../common/logger.py') as f:
    exec(f.read())
logger = get_logger(name='google')
logger.info('Start crawl multi-country google')

# Description: Import web driver module to control the browser and perform the search on Google.
# Input parameters:
# module_name: Name of the module to be imported.
# file_name: Path to the module file.
def get_module(module_name, file_name):
    name = file_name.split('.')[0]

    module_path = os.path.join(os.getcwd(), '..', module_name, file_name)
    spec = importlib.util.spec_from_file_location(name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# Get translate function from translate module.
translate_module = get_module('common', 'translate_api.py')
translate_using_api = translate_module.translate_using_api

# Import multi-lang input module to get the list of countries, languages, inputs, country codes.
multilang_input_module = get_module('internal', 'multi_language_input.py')
COUNTRIES = multilang_input_module.COUNTRIES
LANGUAGES = multilang_input_module.LANGUAGES
INPUTS = multilang_input_module.INPUTS
COUNTRY_CODES = multilang_input_module.COUNTRY_CODES
LANGUAGES_CODES = multilang_input_module.LANGUAGES_CODES

# Get the web driver module and create a driver instance to control the browser.
driver_module = get_module('common', 'web_driver.py')
get_driver = driver_module.get_driver
driver = get_driver()

# Function to get the publish date of a webpage using its description.
# description: Description of the webpage.
# Returns the publish date in the format YYYY-MM-DD or today's date if the publish date cannot be determined.
def get_publish_from_des(description):
    description_words = description.split(' ')
    if description_words[0].isdigit():
        time_del = int(description_words[0])
        # time_unit = description_words[1]  
        # en: hour, minute, day, week, month, year
        time_unit = description_words[1]
        if time_unit.startswith('day'):
            publish_date = datetime.today().date() - timedelta(days=time_del)
            return publish_date.strftime("%Y-%m-%d")
    return datetime.today().date().strftime("%Y-%m-%d")


# Description: Function to preprocess the search results on Google by filtering out irrelevant results.
# Note:
# "&udm=14": Filtering out results that are not sitelinks.
# "&tbs=qdr:w": Filtering out results that are older than a week.
def preprocess():
    try:
        cur_url = driver.current_url
        driver.get(cur_url+"&udm=14&tbs=qdr:w")
    except Exception as e:
        logger.error(f'Selenium google filter search result: {e}')

# Description: Function to search for relevant links on Google and store them in the google_links list. 
# The function iterates through multiple pages of search results and extracts the title, link, description, and website for each result. 
# It also filters out irrelevant results that their link contains keyword listed in the list_ignore.
# The function uses Selenium to interact with the browser and perform the search. 
# If there are no more pages of search results, the function stops and logs a message. 
# If there is an error during the search, the function logs the error message. 
# Finally, the function returns the list of links found during the search.
def process():
    list_ignore = ['youtube.com', 'samsung.com']
    try:
        while (1):
            elem = driver.find_elements(By.CSS_SELECTOR, 'div.g')
            for e in elem:
                title = e.find_element(By.TAG_NAME, 'h3').text
                link = e.find_element(By.TAG_NAME, 'a').get_attribute("href")
                elem = e.find_elements(By.TAG_NAME, 'span')
                website = elem[2].text
                elem = e.find_element(By.TAG_NAME, 'div')
                elem = elem.find_elements(By.TAG_NAME, 'div')
                description = elem[-2].text
                if all(ignore not in link for ignore in list_ignore):
                    publish_date = get_publish_from_des(description)
                    split_date_index = description.find("—")
                    if split_date_index in range (0, 20):
                        description = description[split_date_index+1:].strip()
                    google_links.append(
                        {'title': title, 'link': link, 'description': description, 'website': website, 'publish': publish_date})

            # next page
            for _ in range(4):
                delta = random.uniform(200, 330)
                driver.execute_script(f"window.scrollBy(0, {delta});")
                time.sleep(random.uniform(0,2))
            elem = driver.find_element(By.ID, "pnnext")
            elem.click()

    except NoSuchElementException:
        logger.info('Searched all pages!')
    except Exception as e:
        logger.info(f'Selenium search filter many pages: {e}')

# Description: Function to initiate the search on Google using the given input string. 
# Results are stored in the google_links list.
# Input parameters:
# input: Search query string.
def scan(input):
    url = "https://www.google.com/search?hl=en&q=" + input
    driver.get(url)
    preprocess()
    process()

# Description: Function to remove duplicate links from the google_links list.
# Returns a list of unique links.
def remove_duplicate_links():
    seen_links = set()
    result = []

    for link in google_links:
        if link['link'] not in seen_links:
            result.append(link)
            seen_links.add(link['link'])

    return result

#############################################################
##################### SEARCHING PROCESS #####################
#############################################################

# STEP 1: Genaral search.
# Location: All the world. 
# Language: English. 
# scan("allintext:samsung (app OR tool OR android) (attack OR bypass OR crack OR 'Privilege Escalation' OR Root OR 'Zero-day') after:2025-01-01")
# scan("allintext:samsung (app OR tool OR android) (attack OR bypass OR crack OR 'Privilege Escalation' OR Root OR 'Zero-day') (Trojan OR Spyware OR Ransomware OR Adware) after:2025-01-01")
scan("allintext:samsung app (attack OR exploit OR malware) after:2025-01-01")
# scan(INPUTS['English'])

# STEP 2: Localized search.
# Location: Each country listed in COUNTRIES one by one.
# Language: Official language of each country. Defined in LANGUAGES dictionary. 
# Note: "&cr=country" + COUNTRY_CODES of each country using for getting localized search results.
for country in COUNTRIES:
    input = INPUTS[LANGUAGES[country][0]]
    input += "&cr=country" + COUNTRY_CODES[country]
    scan(input)

# STEP 3: Remove duplicate links.
google_links = remove_duplicate_links()

# STEP 4: Translate non-English descriptions and titles using the MyMemory API (open source translation service).
for link in google_links:
    try:
        if (detect(link["description"]) != 'en'):
            original = link["description"]
            translate = translate_using_api(original)
            # translate = "Translate is not support now."
            link["description"] = "Translate by API: " + \
                translate + "\nOriginal: " + original
    except:
        pass
    try:
        if (detect(link["title"]) != 'en'):
            original = link["title"]
            translate = translate_using_api(original)
            # translate = "Translate is not support now."
            link["title"] = "Translate by API: " + \
                translate + "\nOriginal: " + original
    except:
        pass

#########################################################
##################### STORE RESULTS #####################
#########################################################

# Store the results in an Excel file with the following columns: Type, Link, Title, Short description, Web content, Summary.
COL_TYPE = 'Type'
COL_LINK = 'Link'
COL_TITLE = 'Title'
COL_DES = 'Short description'
COL_PUBLISHED = 'Published at'
COL_CONTENT = 'Web content'
COL_SUMMARY = 'Summary'

# Create a list of dictionaries containing the data to be stored in the Excel file. 
# Each dictionary represents a row in the Excel file.
excel_data = []

# Iterate over the google_links list and create a dictionary for each link containing the required data.
for i, link in enumerate(google_links):
    row = {
        COL_TYPE: 'google',
        COL_LINK: link["link"],
        COL_PUBLISHED: link["publish"],
        COL_TITLE: link["title"],
        COL_DES: link["description"],
    }
    excel_data.append(row)

# Store the data in an Excel file with the date as part of the file name.
try:
    today = datetime.today().date()

    path = '..//output'
    # Check if the directory exists
    if not os.path.exists(path):
        # Create the directory if it doesn't exist
        os.makedirs(path)
        logger.info(f'The directory "{path}" has been created.')
        
    file_path = f'{path}//output_{today}.xlsx'
    
    sheet_name = f'google_{today}'
    columns = [COL_TYPE, COL_LINK, COL_PUBLISHED, COL_TITLE, COL_DES]
    df = pd.DataFrame(excel_data, columns=columns)

    # Check file exist, delete old sheet before add new sheet
    if os.path.exists(file_path):
        with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='new') as writer:
            if sheet_name in writer.book.sheetnames:
                writer.book.remove(writer.book[sheet_name])
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    else:
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)

    logger.info(f'Exported {len(excel_data)} data successful to {file_path} with sheet name {sheet_name}!')
except Exception as e:
    logger.error(f'Save data fail: {e}')