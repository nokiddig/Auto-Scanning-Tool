# ==========================================================
# ========================= Import =========================
# ==========================================================

import os
import importlib.util
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Imports a module from another directory.
def get_module(folder_name, file_name):
    module_name = file_name.split('.')[0]
    module_path = os.path.join(os.getcwd(), '..', folder_name, file_name)
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ================================================================
# ====================== Get new web driver ======================
# ================================================================
# Get new web driver with chrome_options. Return the driver object.
def get_driver():
    """
        --headless: hide ui while running browser.
        --ignore-certificate-errors: ignore certificate errors
        --allow-insecure-localhost: allow insecure localhost
        --lang=vi-VN: set language to vietnamese
        --no-sandbox: no sandbox (for linux)
    """
    options = Options()
    #chrome_options.add_argument("--headless")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--allow-insecure-localhost")
    options.add_argument("--lang=en")
    options.add_argument("--no-sandbox")

    user_profile = r"C:/Users/SyLV/AppData/Local/Google/Chrome/User Data/"
    options.add_argument(f"user-data-dir={user_profile}")
    options.add_argument("profile-directory=Profile 1")


    # disable location services -> search many case
    options.add_argument("--disable-geolocation")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # Disable automation detection by website -> search many case
    options.add_argument("--disable-blink-features=AutomationControlled") 
    # driver = webdriver.Chrome(options=chrome_options)
    # driver = webdriver.Edge(options=options)
    driver = webdriver.Chrome(options=options)

    #driver.maximize_window()
    return driver
