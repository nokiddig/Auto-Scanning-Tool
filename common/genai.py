# ==========================================================
# ====================== Import ============================
# ==========================================================

import os
import re
import datetime
import unicodedata
import importlib.util
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import ElementClickInterceptedException, MoveTargetOutOfBoundsException

# logger: defined in logger.py, use this logger to log all the process of genai with prefix 'genai'.
with open('../common/logger.py') as f:
    exec(f.read())
logger = get_logger(name='genai')

# Imports a module from another directory. 
def get_module(folder_name, file_name):
    module_name = file_name.split('.')[0]
    module_path = os.path.join(os.getcwd(), '..', folder_name, file_name)
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# get_module('common', 'web_driver.py') import web_driver.py from common folder and return it as a module object. 
driver_module = get_module('common', 'web_driver.py')
get_driver = driver_module.get_driver

# USERNAME and PASSWORD(GenAI account) are defined in variable.py.
input_module = get_module('internal', 'genai_input.py')
USERNAME = input_module.GENAI_USERNAME
PASSWORD = input_module.GENAI_PASSWORD

# =========================================================
# ====================== Handle text ======================
# =========================================================

# normalize remove non ASCII chars
def normalize_text(text):
    normalized_text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    return normalized_text

# replace non-word characters with space
def remove_non_word(text):
    cleaned_text = re.sub(r'[^\w\s]', ' ', text)
    return cleaned_text

# remove paths and urls from text 
def remove_paths_and_urls(text):
    pattern = r'(?:[A-Za-z]:\\[^\\\n]*|\/[^\/\n]*)+|http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    # replace url with space
    cleaned_text = re.sub(pattern, '', text)
    return cleaned_text

# handle text: remove paths and urls, remove special character, clean text, join lines with '.'and return.
def handle_text(text):
    text = remove_paths_and_urls(text)
    text = normalize_text(text)
    text = remove_non_word(text)
    line_text = '.  '.join(text.splitlines())
    return line_text


# =========================================================
# ====================== Genai class ======================
# =========================================================

# Genai class: handle genai summarization. 
# Use Selenium to interact with GenAI web page.
class Genai:
    # init genai: login with username and password. 
    def __init__(self): 
        self.a = 1
        # self.driver = get_driver()
        # self.driver.get('https://genai.sec.samsung.net/summarize')

        # self.login() 
        # self.driver.implicitly_wait(50)
        # sleep(50)

        # # Close tutorial popup and notice popup.
        # self.IS_CLOSE_POPUP = False
        # self.close_tutorial_popup()
        # self.close_template()
        # logger.info('Init genai success.')
    
    # login with username and password(define in input/variable.py).
    def login(self):
        try:
            user_ip = self.driver.find_element(By.ID, 'userNameInput')
            password_ip = self.driver.find_element(By.ID, 'passwordInput')
            login_btn = self.driver.find_element(By.ID, 'submitButton')

            user_ip.send_keys(USERNAME)
            password_ip.send_keys(PASSWORD)
            login_btn.click()
        except Exception as e:
            logger.error(f'Login fail: {type(e).__name__}')
            self.cap_screen(type(e).__name__)
    
    # Try to click close button in tutorial popup and notice popup.
    def click_close_btn(self):
        close_btns = self.driver.find_elements(By.XPATH, "//*[text()='Close']")
        if len(close_btns) > 0:
            logger.info('Close tutorial popup.')
            for btn in close_btns:
                try:            
                    self.driver.execute_script("arguments[0].click();", btn)              
                except Exception:
                    logger.info("Clicked on close button using js.")

        btn_by_class = self.driver.find_elements(By.CLASS_NAME, 'v-btn__content')
        if len(btn_by_class) > 0:
            logger.info('Close notice popup.')
            for btn in btn_by_class:
                try:
                    if (btn.text == 'Close'):
                        btn.click()
                except Exception:
                    pass
    
    # Close tutorial popup after login.
    def close_tutorial_popup(self):
        self.click_close_btn()
        try:
            # move to last tutorial -> click close tutorial
            last_tutorial_btn = self.driver.find_elements(By.CLASS_NAME, "mdi-circle")
            if (len(last_tutorial_btn)  == 0):
                return
            last_tutorial_btn[4].click()

            close_btn = self.driver.find_elements(By.CLASS_NAME, "mdi-close")
            close_btn[1].click()
        except Exception as e:
            logger.error(f'Close popup fail: {type(e).__name__}')
            self.cap_screen(type(e).__name__)

    # Close prompt template before search summary(not importance).
    def close_template(self):
        # close hover mouse: move mouse to another position
        action = ActionChains(self.driver)
        action.move_by_offset(0, 0).perform()

        try: 
            logger.info('Close prompt template.')
            img_close_Prompt_template = self.driver.find_element(By.XPATH, '//img[@alt="drawerClose"]')
            img_close_Prompt_template.click()
        except:
            pass

    # Create new chat and send prompt
    # Use handle_text function to clean text before search summary.
    # Search text and return summary text. If no result found, return 'Fail'.
    # wait: time to wait for summary result. default is 20s. max is 50s.
    # research: retry search with max wait time 50s. Default is false.
    def search(self, text, wait=20, research=False):
        return ""
        # if self.IS_CLOSE_POPUP is False:
        #     self.close_tutorial_popup()

        # max_wait = 50
        # text = handle_text(text)
        # if len(text) < 20:
        #     return text
        
        # try:
        #     new_chat_btn = self.driver.find_element(By.CLASS_NAME, "new-chat-floating")
        #     new_chat_btn.click()

        #     search_promt = "summarize below text in english focus on samsung keyword(required English):"
        #     search_input = search_promt + text 
        #     input_txt = self.driver.find_element(By.ID, "input-40")
        #     input_txt.send_keys(search_input)
        #     send_btn = self.driver.find_element(By.CLASS_NAME, "inquiry")
        #     send_btn.click()
        #     sleep(wait)

        #     elements = self.driver.find_elements(By.TAG_NAME, "P")
        #     if len(elements) == 0:
        #         logger.error('Summary fail: No result found. Please check your input text.')
        #         self.cap_screen()
        #     else:
        #         self.IS_CLOSE_POPUP = True
        #         result = elements[-1].text
        #         return result
        # # Login expried -> relogin genai
        # except (ElementClickInterceptedException, MoveTargetOutOfBoundsException) as e:
        #     if research is False:
        #         self.__init__()
        #         return self.search(text=text, wait=20, research=True)
        #     else:
        #         self.cap_screen(type(e).__name__)
        # # Other exception -> retry search
        # except Exception as e:
        #     if research is False:
        #         return self.search(text, wait=max_wait, research=True)
        #     else:
        #         logger.error(f"Search fail: {e}")
        #         self.cap_screen(type(e).__name__)

        return "Fail"

    # Capture screen when error occur.
    def cap_screen(self, name="ScreenShot"):
        current_time = datetime.today().strftime('%Y-%m-%d_%H-%M-%S')
        screenshot_path = f'../output/screenshot/{current_time}_{name}.png'
        self.driver.save_screenshot(screenshot_path)
        logger.info(f'Screen capture saved at{screenshot_path}.')

    # Quit genai, close driver. Called by garbage collector.
    def __del__(self):
        self.driver.quit()
        logger.info('Quit genai.')
