# Auto-Scanning-Tool
Automatically Craw tool for KG in the internet.

# Project structure
Project/
│
├── common/
│       └── genai.py
│       └── logger.py
│       └── web_driver.py
├── google/
│       ├── google_selenium.ipynb
│       └── parser.py
├── gsmhosting/
│       ├── gsm_selenium.ipynb
│       └── gsmhosting.py
├── youtube/
│       ├── youtube_api_auto_tool_selenium.ipynb
│       └── youtube_api_auto_tool.ipynb
│       └── youtube.py
├── mail/
│       └── mail.py
├── internal/
│       └── user_data/
├── output/
│       ├── screenshot/
│       └── output_{date}.xlsx
├── log/
│       └── log_{date}.txt
└── README.md

# Module: common

The `common` module contains shared files and classes used across the AutoCrawlDataTool project. It handles tasks related to Selenium and artificial intelligence (AI).

## Files:

### 1. genai.py
- This file contains code that uses Selenium to send a text-based prompt to an AI system and receives a summarized result of the text. It automates the process of summarizing documents through browser interactions.

### 2. web_driver.py
- This file configures the web driver using the Selenium library, which is used to control browsers and scrape data from web pages. It manages the initialization and operation of the WebDriver for browser-related tasks.
- Method: 
    + get_driver: This method initializes and returns a configured WebDriver instance.
        chrome_options.add_argument("--headless")  #headless -> hide running browser
        chrome_options.add_argument(f"user-agent={UserAgent().random}") # fake user agent
        chrome_options.add_argument("user-data-dir=../internal") # save cookie to internal folder
        chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"]) # ignore logs from chrome

# Module: google

The `google` module contains the functionality for crawling data from Google Search using Selenium.

## Files:

### 1. google.py
- This file uses Selenium to query Google’s advanced search. It extracts information such as "link", "title", and "short description" from the search results and saves them into the "google_{date}" sheet of the output file.

# Module: gsmhosting

The `gsmhosting` module is designed for crawling data from the GSMHosting website using Selenium.

## Files:

### 1. gsmhosting.py
- This file utilizes Selenium to query the search functionality on the GSMHosting site. It retrieves the five most recent responses from each post, summarizes the key points using the AI system from `genai.py`, and saves the results into the "gsm_{date}" sheet of the output file.

# Module: youtube
The `youtube` module is designed for crawling data from youtube website using Selenium.
## Files:

### 1. youtube.py
- This file use google api to query search: https://www.googleapis.com/youtube/v3/videos
- It requires:
    headers = {
        'Content-Type': 'application/json',
        'accept': 'application/json',
    }

    params = {
        'part': 'snippet,contentDetails,statistics',
        'id': video_id,
        'key': API_KEY
    }
- Ignore words are defined to ignore unrelated cases.
- After getting information from api, `description` will be summarized by `genai` to `short description`.

# Note:
## screen shot
    driver.save_screenshot('screenshot.png')
## Certificate
    \\107.98.48.222\SRV common\01. IS Setup\Fix certificate errors
