import requests
from langdetect import detect


# Description: Function to get the URL for the MyMemory API (open source translation service) for translating a given text from one language to another.
# Input parameters:
# text: Text to be translated.
# from_lang: Source language code.
# to_lang: Target language code.
def get_api_url(text, from_lang, to_lang):
    return f"https://api.mymemory.translated.net/get?q={text}&langpair={from_lang}%7C{to_lang}"

# Description: Function to translate a given text using the MyMemory API (open source translation service). The function first detects the language of the input text and then translates it to English using the API.
# Input parameters:
# text: Text to be translated.
def translate_using_api(text):
    try: 
        from_lang = detect(text)
        url = get_api_url(text, from_lang, 'en')
        response = requests.get(url, verify=False)
        data = response.json()
        response.raise_for_status()  # Raise an exception for HTTP errors
        data['responseData']['translatedText']
        return data['responseData']['translatedText']
    except Exception as e:
        return ""