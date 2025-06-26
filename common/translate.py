""" Document: Translate.ipynb
    @param sl => source_language. Ex: vi  = Viet Nam (auto -> auto detect)
    @param tl => target_language. Ex: en = English
    @param text => (query) the text to be translated.

    Init driver
    Create an instance of Translate class with the source and target languages.

    EX: translator = Translate(driver, source_language='vi', target_language='en')
    translator.translate(text) => return translated text from vi to en.
"""

import os
import time
import importlib
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


# ==========================================================
# ====================== Import local ======================
# ==========================================================
# logger: defined in logger.py, use this logger to log all the process of translate with prefix 'translate'.
with open('../common/logger.py') as f:
    exec(f.read())
logger = get_logger(name='Translate')


"""
    get_module(folder_name, file_name)
    Imports a module from another directory.
    Ex: get_module('common', 'web_driver.py')
    => import web_driver.py from common folder and return it as a module object.
"""
def get_module(folder_name, file_name):
    module_name = file_name.split('.')[0]
    module_path = os.path.join(os.getcwd(), '..', folder_name, file_name)
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


driver_module = get_module('common', 'web_driver.py')
get_driver = driver_module.get_driver


LANGUAGE_CODES = {
    'Afrikaans': 'af', 'Albanian': 'sq',
    'Amharic': 'am', 'Arabic': 'ar',
    'Armenian': 'hy', 'Azerbaijani': 'az',
    'Basque': 'eu', 'Belarusian': 'be',
    'Bengali': 'bn', 'Bosnian': 'bs',
    'Bulgarian': 'bg', 'Catalan': 'ca',
    'Cebuano': 'ceb', 'Chichewa': 'ny',
    'Chinese (Simplified)': 'zh-CN', 'Chinese (Traditional)': 'zh-TW',
    'Corsican': 'co', 'Croatian': 'hr',
    'Czech': 'cs', 'Danish': 'da',
    'Dutch': 'nl', 'English': 'en',
    'Esperanto': 'eo', 'Estonian': 'et',
    'Filipino': 'tl', 'Finnish': 'fi',
    'French': 'fr', 'Frisian': 'fy',
    'Galician': 'gl', 'Georgian': 'ka',
    'German': 'de', 'Greek': 'el',
    'Gujarati': 'gu', 'Haitian Creole': 'ht',
    'Hausa': 'ha', 'Hawaiian': 'haw',
    'Hebrew': 'he', 'Hindi': 'hi',
    'Hmong': 'hmn', 'Hungarian': 'hu',
    'Icelandic': 'is', 'Igbo': 'ig',
    'Indonesian': 'id', 'Irish': 'ga',
    'Italian': 'it', 'Japanese': 'ja',
    'Javanese': 'jw', 'Kannada': 'kn',
    'Kazakh': 'kk', 'Khmer': 'km',
    'Kinyarwanda': 'rw', 'Korean': 'ko',
    'Kurdish (Kurmanji)': 'ku', 'Kyrgyz': 'ky',
    'Lao': 'lo', 'Latin': 'la',
    'Latvian': 'lv', 'Lithuanian': 'lt',
    'Luxembourgish': 'lb', 'Macedonian': 'mk',
    'Malagasy': 'mg', 'Malay': 'ms',
    'Malayalam': 'ml', 'Maltese': 'mt',
    'Maori': 'mi', 'Marathi': 'mr',
    'Mongolian': 'mn', 'Myanmar (Burmese)': 'my',
    'Nepali': 'ne', 'Norwegian': 'no',
    'Odia (Oriya)': 'or', 'Pashto': 'ps',
    'Persian': 'fa', 'Polish': 'pl',
    'Portuguese': 'pt', 'Punjabi': 'pa',
    'Romanian': 'ro', 'Russian': 'ru',
    'Samoan': 'sm', 'Scots Gaelic': 'gd',
    'Serbian': 'sr', 'Sesotho': 'st',
    'Shona': 'sn', 'Sindhi': 'sd',
    'Sinhala': 'si', 'Slovak': 'sk',
    'Slovenian': 'sl', 'Somali': 'so',
    'Spanish': 'es', 'Sundanese': 'su',
    'Swahili': 'sw', 'Swedish': 'sv',
    'Tajik': 'tg', 'Tamil': 'ta',
    'Tatar': 'tt', 'Telugu': 'te',
    'Thai': 'th', 'Turkish': 'tr',
    'Turkmen': 'tk', 'Ukrainian': 'uk',
    'Urdu': 'ur', 'Uyghur': 'ug',
    'Uzbek': 'uz', 'Vietnamese': 'vi',
    'Welsh': 'cy', 'Xhosa': 'xh',
    'Yiddish': 'yi', 'Yoruba': 'yo',
    'Zulu': 'zu'
}


# =============================================================
# ====================== Class translate ======================
# =============================================================
class Translate:
    def __init__(self, source_language='auto', target_language='en'):
        self.driver = get_driver()
        self.source_language = source_language
        self.target_language = target_language
        logger.info(f"Translate from {source_language} to {target_language}")

    def set_source_language(self, language):
        self.source_language = language
        logger.info(f"Set source language to {language}")

    def set_target_language(self, language):
        self.target_language = language
        logger.info(f"Set target language to {language}")

    # Translate text from source language to target language. Return translated text.
    def translate(self, text):
        try:
            url = f"https://translate.google.com.my/?sl={self.source_language}&tl={self.target_language}&text={text}&op=translate"
            self.driver.get(url)
            time.sleep(0.5)

            # Wait for the translation result to appear.
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//span[@jsname="W297wb"]'))).text

            output = self.driver.find_element(By.XPATH, '//span[@jsname="W297wb"]').text
            return output
        except Exception as e:
            logger.error(f"Translation error: {e}")
