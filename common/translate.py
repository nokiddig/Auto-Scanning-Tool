# %% [markdown]
# Tham số: 
# 
# Tham số sl => nguồn ngôn ngữ. Ex: vi  = Việt Nam (các bạn có thể để auto để api tự động detect ngôn ngữ đầu vào)
# 
# Tham số tl =>  ngôn ngữ đích cần dịch. Ex: en = Tiếng Anh
# 
# Tham số q => (query) truyền vào đoạn văn bản cần dịch

# %%
import os
import time
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# %%
with open('../common/logger.py') as f:
    exec(f.read())

logger = get_logger(name='genai')

# %%
class Translate:
    def __init__(self, driver, source_language='auto', target_language='en'):
        self.driver = driver
        self.source_language = source_language
        self.target_language = target_language
        
    def set_source_language(self, language):
        self.source_language = language
        
    def set_target_language(self, language):
        self.target_language = language

    def translate(self, text):
        try:
            self.driver.get(f"https://translate.google.com.my/?sl={self.source_language}&tl={self.target_language}&text={text}&op=translate")

            # time.sleep(0.5)
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//span[@jsname="W297wb"]'))).text

            output = self.driver.find_element(By.XPATH, '//span[@jsname="W297wb"]').text
            return output
        except Exception as e:
            logger.error(f"Translation error: {e}")


