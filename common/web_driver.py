# %%
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from fake_useragent import UserAgent
import undetected_chromedriver as uc
from webdriver_manager.chrome import ChromeDriverManager
# %%
import importlib.util
import os
def get_module(module_name, file_name):
    name = file_name.split('.')[0]

    module_path = os.path.join(os.getcwd(), '..', module_name, file_name)
    spec = importlib.util.spec_from_file_location(name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# %%
variable_module = get_module('internal', 'variable.py')
CHROMEDRIVER_PATH = variable_module.CHROMEDRIVER_PATH

# %%
def get_driver():
    # Set path for chrome Selenium
    # CHROMEDRIVER_PATH = '/usr/local/bin/chromedriver'
    s = Service(CHROMEDRIVER_PATH)
    
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  #headless -> hide running browser
    # chrome_options.add_argument("user-data-dir=../internal/user-data") # cookie / cert, ...
    chrome_options.add_argument("--ignore-certificate-errors")  # Thêm tùy chọn này
    chrome_options.add_argument("--allow-insecure-localhost")  # Cho phép localhost không an toàn (nếu cần)
    chrome_options.add_argument("--lang=vi-VN") #thiết lập tiếng việt

    # chrome_options.add_experimental_option("detach", True) # keep browser open after script ends -> dangerous
    # chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    
    chrome_options.add_argument("--disable-geolocation")  # Vô hiệu hóa vị trí thật
    chrome_options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.geolocation": 1,
        "profile.default_content_setting_values.notifications": 1,
    })
    # chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"]) # ignore logs from chrome
    # chrome_options.add_argument("--disable-gpu")  # Vô hiệu hóa GPU (giúp chạy ổn định hơn trên Windows)
    chrome_options.add_argument("--no-sandbox")  # Tùy chọn an toàn, đặc biệt khi chạy trong container


    op = webdriver.ChromeOptions()
    op.add_argument(f"user-agent={UserAgent.random}")
    driver = uc.Chrome(options=op)
    # Khởi tạo trình duyệt Chrome với các tùy chọn
    # driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()
    return driver


