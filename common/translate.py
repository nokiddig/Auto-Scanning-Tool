# %% [markdown]
# ### Document: 
# ```
# @param sl => source_language. Ex: vi  = Việt Nam (để auto để tự động detect ngôn ngữ đầu vào)  
# @param tl =>  target_language. Ex: en = Tiếng Anh  
# @param text => (query) the text to be translated.
# ```
# Init driver   
# Create an instance of Translate class with the source and target languages.  
# ```
# EX: translator = Translate(driver, source_language='vi', target_language='en')  
# translate(text) => return translated text.
# ```

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

logger = get_logger(name='Translate')

# %%
LANGUAGE_CODES = {
    'Afrikaans': 'af',
    'Albanian': 'sq',
    'Amharic': 'am',
    'Arabic': 'ar',
    'Armenian': 'hy',
    'Azerbaijani': 'az',
    'Basque': 'eu',
    'Belarusian': 'be',
    'Bengali': 'bn',
    'Bosnian': 'bs',
    'Bulgarian': 'bg',
    'Catalan': 'ca',
    'Cebuano': 'ceb',
    'Chichewa': 'ny',
    'Chinese (Simplified)': 'zh-CN',
    'Chinese (Traditional)': 'zh-TW',
    'Corsican': 'co',
    'Croatian': 'hr',
    'Czech': 'cs',
    'Danish': 'da',
    'Dutch': 'nl',
    'English': 'en',
    'Esperanto': 'eo',
    'Estonian': 'et',
    'Filipino': 'tl',
    'Finnish': 'fi',
    'French': 'fr',
    'Frisian': 'fy',
    'Galician': 'gl',
    'Georgian': 'ka',
    'German': 'de',
    'Greek': 'el',
    'Gujarati': 'gu',
    'Haitian Creole': 'ht',
    'Hausa': 'ha',
    'Hawaiian': 'haw',
    'Hebrew': 'he',
    'Hindi': 'hi',
    'Hmong': 'hmn',
    'Hungarian': 'hu',
    'Icelandic': 'is',
    'Igbo': 'ig',
    'Indonesian': 'id',
    'Irish': 'ga',
    'Italian': 'it',
    'Japanese': 'ja',
    'Javanese': 'jw',
    'Kannada': 'kn',
    'Kazakh': 'kk',
    'Khmer': 'km',
    'Kinyarwanda': 'rw',
    'Korean': 'ko',
    'Kurdish (Kurmanji)': 'ku',
    'Kyrgyz': 'ky',
    'Lao': 'lo',
    'Latin': 'la',
    'Latvian': 'lv',
    'Lithuanian': 'lt',
    'Luxembourgish': 'lb',
    'Macedonian': 'mk',
    'Malagasy': 'mg',
    'Malay': 'ms',
    'Malayalam': 'ml',
    'Maltese': 'mt',
    'Maori': 'mi',
    'Marathi': 'mr',
    'Mongolian': 'mn',
    'Myanmar (Burmese)': 'my',
    'Nepali': 'ne',
    'Norwegian': 'no',
    'Odia (Oriya)': 'or',
    'Pashto': 'ps',
    'Persian': 'fa',
    'Polish': 'pl',
    'Portuguese': 'pt',
    'Punjabi': 'pa',
    'Romanian': 'ro',
    'Russian': 'ru',
    'Samoan': 'sm',
    'Scots Gaelic': 'gd',
    'Serbian': 'sr',
    'Sesotho': 'st',
    'Shona': 'sn',
    'Sindhi': 'sd',
    'Sinhala': 'si',
    'Slovak': 'sk',
    'Slovenian': 'sl',
    'Somali': 'so',
    'Spanish': 'es',
    'Sundanese': 'su',
    'Swahili': 'sw',
    'Swedish': 'sv',
    'Tajik': 'tg',
    'Tamil': 'ta',
    'Tatar': 'tt',
    'Telugu': 'te',
    'Thai': 'th',
    'Turkish': 'tr',
    'Turkmen': 'tk',
    'Ukrainian': 'uk',
    'Urdu': 'ur',
    'Uyghur': 'ug',
    'Uzbek': 'uz',
    'Vietnamese': 'vi',
    'Welsh': 'cy',
    'Xhosa': 'xh',
    'Yiddish': 'yi',
    'Yoruba': 'yo',
    'Zulu': 'zu',
    'IsiZulu': 'zu',
    'IsiXhosa': 'xh'
}

# %%
class Translate:
    def __init__(self, driver, source_language='auto', target_language='en'):
        self.driver = driver
        self.source_language = source_language
        self.target_language = target_language
        logger.info(f"Translate from {source_language} to {target_language}")
        
    def set_source_language(self, language):
        self.source_language = language
        
    def set_target_language(self, language):
        self.target_language = language

    def translate(self, text, re_try = 0):
        try:
            self.driver.get(f"https://translate.google.com.my/?sl={self.source_language}&tl={self.target_language}&text={text}&op=translate")
            time.sleep(1)
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//span[@jsname="W297wb"]'))).text

            output = self.driver.find_element(By.XPATH, '//span[@jsname="W297wb"]').text
            if (output == 'None' or output == '' or output == None) and re_try<5:
                # open new tab by JS
                self.driver.execute_script("window.open('');")
                self.driver.switch_to.window(self.driver.window_handles[-1])
                return self.translate(text= text, re_try= re_try+1)
            return output
        except Exception as e:
            logger.error(f"Translation error: {e}")

# %% [markdown]
# Somalia': ['Somali']
# "samsung AND (unlock OR hacking OR bypass OR crack OR furid OR jabsasho OR ka gudubid OR jebin) AND (Knox guard OR knoxguard OR KG OR MDM OR Maareynta Aaladaha Gacanta)"
# 
# South Africa': ['Afrikaans']
# "samsung AND (unlock OR hacking OR bypass OR crack OR ontsluit OR inbraak OR omseil OR kraak) AND (Knox guard OR knoxguard OR KG OR MDM OR Mobiele Toestelbestuur)"
# 
# South Africa': ['Zulu']
# "samsung AND (unlock OR hacking OR bypass OR crack OR ukuphula OR ukugenca OR ukudlula OR ukuqhekeza) AND (Knox guard OR knoxguard OR KG OR MDM OR Ukuphathwa Kwamadivayisi Eselula)"