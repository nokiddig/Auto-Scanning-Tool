# %% [markdown]
# ### import

# %%
import os
import datetime
import importlib.util
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

# %%
with open('../common/logger.py') as f:
    exec(f.read())

logger = get_logger(name='genai')

# %%
def get_module(module_name, file_name):
    name = file_name.split('.')[0]

    module_path = os.path.join(os.getcwd(), '..', module_name, file_name)
    spec = importlib.util.spec_from_file_location(name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# %% [markdown]
# ### Init variable

# %%
driver_module = get_module('common', 'web_driver.py')
get_driver = driver_module.get_driver

variable_module = get_module('internal', 'variable.py')
USERNAME = variable_module.GENAI_USERNAME
PASSWORD = variable_module.GENAI_PASSWORD
CHROMEDRIVER_PATH = variable_module.CHROMEDRIVER_PATH

# %% [markdown]
# ### Handle text

# %%
import unicodedata
import re

# normalize remove non ASCII chars
def normalize_text(text):
    normalized_text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    return normalized_text


# replace non-word characters with space
def clean_text(text):
    cleaned_text = re.sub(r'[^\w\s]', '', text)  # Giữ lại chữ cái, số và khoảng trắng
    return cleaned_text

def remove_paths_and_urls(text):
    # Regex url
    pattern = r'(?:[A-Za-z]:\\[^\\\n]*|\/[^\/\n]*)+|http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    
    # replace url with space
    cleaned_text = re.sub(pattern, '', text)
    return cleaned_text

def handle_text(text):
    text = remove_paths_and_urls(text)
    text = normalize_text(text)
    text = clean_text(text)
    line_text = '.  '.join(text.splitlines())
    return line_text

# %% [markdown]
# ### Genai class

# %%

class Genai:
    # set driver
    def __init__(self): 
        self.driver = get_driver()
        self.driver.get('https://genai.sec.samsung.net/summarize')

        user_ip = self.driver.find_element(By.ID, 'userNameInput')
        password_ip = self.driver.find_element(By.ID, 'passwordInput')
        login_btn = self.driver.find_element(By.ID, 'submitButton')

        user_ip.send_keys(USERNAME)
        password_ip.send_keys(PASSWORD)
        login_btn.click()

        # self.driver.execute_script("document.body.style.zoom='90%'")
        # self.driver.execute_script("document.body.style.transform='scale(0.8)';")
        # self.driver.execute_script("document.body.style.transformOrigin='0 0';")
        self.driver.maximize_window()
        self.driver.implicitly_wait(15)

        self.click_close_btn()
        self.open_conversation_tab()
        logger.info(f'Init genai success.')
        self.cap_screen()
    
    def click_close_btn(self):
        # Close notice
        elems = self.driver.find_elements(By.CLASS_NAME, 'v-btn__content')
        for elem in elems:
            try:
                if (elem.text == 'Close'):
                    elem.click()
            except Exception as e:
                logger.info("Clicked on close button using Selenium failed, trying to click using js")
        # Close introduce
        try:            
            elements = self.driver.find_elements(By.XPATH, "//*[text()='Close']")
            for elem in elements:
                self.driver.execute_script("arguments[0].click();", elem)              
        except Exception as e:
            logger.info("Clicked on close button using js.")
    
    def close_popup(self):
        self.click_close_btn()
        try:
            # close overlay screem
            circle_btn = self.driver.find_elements(By.CLASS_NAME, "mdi-circle")
            if (len(circle_btn)  == 0):
                return
            circle_btn[4].click()

            close_btn = self.driver.find_elements(By.CLASS_NAME, "mdi-close")
            close_btn[1].click()
        except Exception as e:
            logger.error(f'Close popup fail: {type(e).__name__}')
            self.cap_screen(type(e).__name__)

    def open_conversation_tab(self):
        try: 
            img_close_Prompt_template = self.driver.find_element(By.CLASS_NAME, 'drawerClose')
            img_close_Prompt_template.click()
        except:
            pass
        
        try:
            new_conver = self.driver.find_elements(By.CLASS_NAME, "fold-chatlist")
            if (len(new_conver) == 0):
                return
            new_conver[0].click()
            sleep(2)
        except Exception as e:
            logger.info(f'Open list conversation')

    def search(self, text, delay = 20):
        text = handle_text(text)
        max_delay = 50
        try:
            # close hover mouse: move mouse to another position
            action = ActionChains(self.driver)
            action.move_by_offset(100, 100).perform()

            # search
            search_promt = "summarize below text in english focus on samsung keyword(required English):"

            # new chat
            new_chat_btn = self.driver.find_element(By.XPATH, '//*[@class="chat-type-context"]')
            new_chat_btn.click()

            input_txt = self.driver.find_element(By.ID, "input-39")
            search_input = search_promt + text 
            input_txt.send_keys(search_input)

            send_btn = self.driver.find_element(By.CLASS_NAME, "inquiry")
            send_btn.click()

            sleep(delay)

            elements = self.driver.find_elements(By.TAG_NAME, "P")
            if len(elements) == 0:
                logger.error('Summary fail: No result found. Please check your input text.')
                self.cap_screen()
                return ''
            else:
                result  = elements[-1].text
                return result
        except Exception as e:
            if delay < max_delay:
                return self.search(text, delay = max_delay)
            else:
                logger.error(f"Search fail: {e}")
                self.cap_screen(type(e).__name__)
                return 'Fail'
    
    def cap_screen(self, name = "ScreenShot"):
        current_time = datetime.today().strftime('%Y-%m-%d_%H-%M-%S')
        screenshot_path = f'../output/screenshot/{current_time}_{name}.png'
        self.driver.save_screenshot(screenshot_path)
        print(f'Screen capture saved at{screenshot_path}.')

    def __del__(self):
        self.driver.quit()


