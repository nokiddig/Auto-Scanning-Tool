import os
import importlib
import pandas as pd
from datetime import datetime
with open('../common/logger.py') as f:
    exec(f.read())

# logger: defined in logger.py, use this logger to log all the process.
logger = get_logger(name='Input')


try: 
    # Imports a module from another directory. 
    def get_module(folder_name, file_name):
        module_name = file_name.split('.')[0]
        module_path = os.path.join(os.getcwd(), '..', folder_name, file_name)
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module


    multi_lang_inp_module = get_module('internal', 'multi_language_input.py')
    INPUTS_SEARCH = multi_lang_inp_module.INPUTS['English'].replace('\"', '')

    gsm_inp_module = get_module('internal', 'gsm_input.py')
    GSM_KEY_WORDS = gsm_inp_module.KEY_WORDS
    GSM_IGNORE_WORDS = gsm_inp_module.IGNORE_WORDS

    youtube_inp_module = get_module('internal', 'youtube_input.py')
    YOUTUBE_IGNORE_WORDS = youtube_inp_module.IGNORE_WORDS


    COL_TYPE = "Type"
    COL_VARIABLE = "Variable"
    COL_VALUE = "Value"
    data = [
        {COL_TYPE:"Google", COL_VARIABLE:"INPUT_SEARCH", COL_VALUE: INPUTS_SEARCH},
        {COL_TYPE:"GSM", COL_VARIABLE:"KEY_WORDS", COL_VALUE: GSM_KEY_WORDS},
    ]
except Exception as e:
    logger.error(f"Failed to load input data: {e}")


try:
    df = pd.DataFrame(data)

    today = datetime.today().date()
    file_path = f"..//output//output_{today}.xlsx"
    sheet_name = f"input"

    # Check if the file already exists
    if os.path.exists(file_path):
        with pd.ExcelWriter(file_path, engine="openpyxl", mode='a', if_sheet_exists="new") as writer:
            if sheet_name in writer.book.sheetnames:
            # Remove old sheet with same name
                writer.book.remove(writer.book[sheet_name])
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    else:
        with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)

    logger.info(f"Export input data successful")
except Exception as e:
    logger.error(f"Failed to export input: {e}")