import json
from googletrans import Translator
from selenium import webdriver
from selenium.webdriver.common.by import By
import re
import pandas as pd

def translate_to_english(text):
    translator = Translator()
    translation = translator.translate(text, dest='en')
    return translation.text

def fix_name(data):
    if isinstance(data, str):
        return re.sub("[\s/.,-]+", "_", data.lower().replace('\\', ''))
    if isinstance(data, list):
        for i in range(len(data)):
            data[i] = data[i].replace(' ', '_').lower()
        return data
def get_composition_for_medicine(url):
    driver = webdriver.Chrome()
    try:
        driver.get(url)
        try:
            composition_element = driver.find_element(By.XPATH, "//td[text()='Excipients:']/following-sibling::td")
            composition_text = composition_element.text
            components = [fix_name(component.strip()) for component in composition_text.split('\n')]
        except:
            components = None
        try:
            active_element = driver.find_element(By.XPATH, "//td[text()='Active substance:']/following-sibling::td")
            active_text = active_element.text
            active = [fix_name(component.strip()) for component in active_text.split('\n')]
        except:
            active = None
        try:
            holder_element = driver.find_element(By.XPATH, '//li[contains(text(), "Marketing authorisation holder:")]')
            holder_text = holder_element.find_element(By.CLASS_NAME, 'pull-right').get_attribute("textContent")
        except:
            holder_text = None
        return components, fix_name(active), holder_text
    finally:
        driver.quit()

def parse_medicines_from_csv(csv_url):
    df = pd.read_csv(csv_url, sep='|')

    result_data = []

    for index, row in df.iterrows():
        name = re.split('[,./]', row['PRODUCTNAAM'], 1)
        product_name = fix_name(name[0])
        translated_name = translate_to_english(product_name)
        potency = row['POTENTIE']
        atc_raw = row['ATC'].split(' - ')
        atc_code = atc_raw[0]
        alt_name = atc_raw[1]
        farm_form = row['FARMACEUTISCHEVORM']
        using_way = row['TOEDIENINGSWEG']

        registration_number_digits = int(re.findall(r'(\d+)[/=]', row['REGISTRATIENUMMER'])[0])

        medicine_url = (f"https://www.geneesmiddeleninformatiebank.nl/ords/f?p=111:3::SEARCH:::P0_DOMAIN,P0_LANG,P3_RVG1:H,EN,"
                        f"{registration_number_digits}")

        composition,active, licensiator = get_composition_for_medicine(medicine_url)

        result_data.append({
            'Название препарата (национальный язык)': product_name,
            'Название препарата (английский)': translated_name,
            'ATC-код': atc_code,
            'Дозировка': f"{potency}",
            'Действующие вещества': active,
            'Варианты альтернативного названия препарата': fix_name(alt_name),
            'Производитель/держатель лицензии': licensiator,
            'Состав': composition,
            'Фармацевтическая форма': fix_name(translate_to_english(farm_form)),
            'Способы применения': fix_name(translate_to_english(using_way))
        })
        with open('result.json', 'w', encoding='utf-8') as json_file:
            json.dump(result_data, json_file, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    csv_url = "https://www.geneesmiddeleninformatiebank.nl/metadata.csv"
    parse_medicines_from_csv(csv_url)
