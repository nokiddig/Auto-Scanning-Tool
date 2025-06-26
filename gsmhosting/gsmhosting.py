""" Script
    Step 1: Import the necessary libraries
    - Import external libraries
    - Import local modules
    Step 2: Crawl data using Selenium
    - Go to "Product Support Sections" category on GSM-forum by url
    - Get all links of products(tools) under "Product Support Sections" category
    - For each product, get all post and filter them based on the deadline and key words.
    - Get max 5 newest comments from each post
    Step 3: Summarize comments using GenAI
    - Generate summary for each thread-product's comments using GenAI
    Step 4: Save data to excel file
"""


# ==========================================================
# ========================= Import =========================
# ==========================================================

import os
import importlib
import pandas as pd
from time import sleep
from time import strptime
from datetime import datetime
from datetime import timedelta
from selenium.webdriver.common.by import By


# Run file logger.py and create logger object with prefix 'gsm'
with open('../common/logger.py') as f:
    exec(f.read())
logger = get_logger(name='gsm')
logger.info('Start crawl gsm-forum')


# Import a module from another directory
def get_module(folder_name, file_name):
    module_name = file_name.split('.')[0]
    module_path = os.path.join(os.getcwd(), '..', folder_name, file_name)
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# Import web driver module from common directory and create driver object.
try:
    driver_module = get_module('common', 'web_driver.py')
    get_driver = driver_module.get_driver
    driver = get_driver()
except Exception as e:
    logger.error(f'Import web driver fail: {e}')


input_module = get_module('internal', 'gsm_input.py')
MIN_POST_DATE = input_module.MIN_POST_DATE
KEY_WORDS = input_module.KEY_WORDS
IGNORE_WORDS = input_module.IGNORE_WORDS


# ==========================================================
# ===================== Craw selenium ======================
# ==========================================================

# Go to "Product Support Sections" category on GSM-forum
driver.get("https://forum.gsmhosting.com/vbb/f209/")


# Get all links of tools/products under "Product Support Sections" category
tools = []
try:
    product_links = driver.find_elements(By.CLASS_NAME, "alt1Active")
    for product in product_links:
        a_tag = product.find_element(By.TAG_NAME, "a")
        title = product.text
        href = a_tag.get_attribute("href")

        tools.append({'title': title, 'link':href})  
except Exception as e:
    logger.error(f'Crawl selenium: {e}')


# Check if the post's title contains any words from the IGNORE_WORDS list.
def check_contain_ignore(title):
    title = title.lower()
    for word in IGNORE_WORDS:
        if word.lower() in title:
            return True
    return False


# YESTERDAY_TIME, TODAY_TIME: display time format on gsm-forum.
YESTERDAY_TIME = "Yesterday"
TODAY_TIME = "Today"


# Get all thread-product from a specific topic link and filter them based on the deadline and key words.
# topic: dictionary containing the title and link of the topic.
def get_posts_from_product(product):
    thread_posts = []
    driver.get(product['link'])
    print(product['title'])

    # Get all thread-products in this topic.
    rows = driver.find_elements(By.XPATH, "//*[contains(@id, 'thread_title')]")
    times = driver.find_elements(By.CSS_SELECTOR, "div.smallfont[style*='text-align:right; white-space:nowrap']")

    # Iterate through the rows and times to extract the title, link, and creation date of each thread-product.
    for (row, time) in (zip(rows, times)):
        title = row.text
        link = row.get_attribute('href')
        creatAt = time.text[:10]

        if creatAt.startswith(YESTERDAY_TIME):
            yesterday = datetime.today().date() - timedelta(days=1)
            creatAt = yesterday.strftime('%m-%d-%Y')
        if creatAt.startswith(TODAY_TIME):
            today = datetime.today().date()
            creatAt = today.strftime('%m-%d-%Y')
        
        if check_contain_ignore(title=title) is False: 
            thread_posts.append({'title': title, 'link':link, 'creatAt': creatAt})

    # Filter the threads based on the deadline and key words.
    post_links_by_deadline = [item for item in thread_posts if strptime(item['creatAt'], '%m-%d-%Y') >= strptime(MIN_POST_DATE, '%m-%d-%Y')]
    post_links_by_keywords = [item for item in post_links_by_deadline if any(keyword in item['title'].lower() for keyword in KEY_WORDS)]
    logger.info(f"Get {len(post_links_by_keywords)} posts from '{product['title']}' ({product['link']})")
    return post_links_by_keywords


# Get all post from all products(tools).
total_posts = []
for product in (tools):
    try: 
        total_posts += get_posts_from_product(product)
    except Exception as e:
        logger.error(f'Get all posts in products: {e}')


# Retrieves the first 5 earliest comments from a topic.
# including navigating to the last page of comments if necessary.
# driver: Selenium WebDriver instance.
# url: URL of the topic.
# Returns list_answers: List of the first 5 earliest comments.
def get_comments_by_link(url=''):
    driver.get(url)

    # Navigate to the last page of comments (earliest comments)
    try:
        last_page_a = driver.find_element(By.XPATH, "//a[@class='smallfont' and contains(text(), 'Last ')]")
        last_page_a.click()
        sleep(3)
    except Exception:
        print("Only 1 page of comments found")

    # Retrieve the last 5 div elements with an id starting with 'post...'
    comment_divs = driver.find_elements(By.CSS_SELECTOR, "table[id^='post']:nth-last-of-type(-n+5)")
    
    # Get the content of the 5 comments
    comments = []
    for cmt_container in reversed(comment_divs):
        container_id = cmt_container.get_attribute("id")    # ex: post14872555
        comment_id = container_id[4:]                       # ex: 14872555
        content = cmt_container.find_element(By.ID, f"post_message_{comment_id}").text
        comments.append(content)

    return comments


# Check if there is any new post since MIN_POST_DATE(input in gsm_input.py).
# post: Dictionary containing the title, link, and creation date of a post.
def check_new_post(post):
    try: 
        driver.get(post['link'])
        # Get the first comment table element and its publish date.
        first_comment_table = driver.find_element(By.XPATH, "//table[starts-with(@id, 'post')]")
        publish_at = first_comment_table.find_element(By.TAG_NAME, "td").text
        publish_date = publish_at[:10]
        print(publish_at, publish_date)
        # Compare the publish date with MIN_POST_DATE and YESTERDAY_TIME. Return True if it is newer.
        if publish_date.startswith(YESTERDAY_TIME) or publish_date.startswith(TODAY_TIME):
            return True
        return publish_at.startswith(YESTERDAY_TIME) or strptime(publish_date, '%m-%d-%Y') >= strptime(MIN_POST_DATE, '%m-%d-%Y')
    except Exception as e:
        logger.error(f'Date not match with %m-%d-%Y: {publish_date} \n {e}')
    

# ==========================================================
# ===================== Filter data ========================
# ==========================================================

COL_TYPE = 'Type'
COL_LINK = 'Link'
COL_PUBLISHED = 'Published at'
COL_TITLE = 'Title'
COL_CONTENT = 'Content'
COL_SUMMARY = 'Summary'
    
# Get post data from total_products and comments
# filter out posts with less than MIN_WORDS words in their comments, and add them to data_output.
# data_output (list): List of dictionaries containing post data and filtered comments.
data_output = []
for i, post in enumerate(total_posts):
    if check_new_post(post):
        comment = ''.join(get_comments_by_link(post['link']))
        row = {
            COL_TYPE:'gsm',
            COL_LINK: post["link"],
            COL_PUBLISHED: post["creatAt"], 
            COL_TITLE: post["title"], 
            COL_CONTENT: comment
        }
        data_output.append(row)


driver.quit()


# ==========================================================
# ===================== GenAI Summary ======================
# ==========================================================

# Import GenAI module from common directory and create GenAI object.
genai_module = get_module('common', 'genai.py')
Genai = genai_module.Genai
genai = Genai()


# Generate summary for each comment using GenAI
# summaries: List of generated summaries for each post's comments.
summaries = []
try:    
    for i, row in enumerate(data_output):
        text = row[COL_CONTENT]
        summary = genai.search(text)        
        summaries.append(summary)
        sleep(1)
        
except Exception as e:
    logger.error(f'Genai summary: {e}')


# Add comment's summary to data output
for i, row in enumerate(data_output):
    if i<len(summaries):
        row[COL_SUMMARY] = ''.join(summaries[i])
    else:
        row[COL_SUMMARY] = ''


# ==========================================================
# ======================= Save data ======================
# ==========================================================

# Save data to Excel file with date as filename and sheetname. 
# If the file already exists, append new data to existing file. 
# If the sheetname already exists, remove the old sheet before adding new data.
try:
    columns = [COL_TYPE, COL_LINK, COL_PUBLISHED, COL_TITLE, COL_CONTENT, COL_SUMMARY]
    df = pd.DataFrame(data_output, columns=columns)

    today = datetime.today().date()
    file_path = f'..//output//output_{today}.xlsx'
    sheet_name = f'gsm_{today}'

    # Check if the file already exists
    if os.path.exists(file_path):
        with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='new') as writer:
            if sheet_name in writer.book.sheetnames:
            # Remove old sheet with same name
                writer.book.remove(writer.book[sheet_name])
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    else:
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    logger.info(f'Export {len(data_output)} data successful')
except Exception as e:
    logger.error(f'Save data fail: {e}')
