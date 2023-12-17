import pandas as pd
import re
from dataclasses import dataclass


@dataclass
class PharmaceuticalProduct:
    name: str
    active_ingredient: str
    pharmaceutical_form: str
    strength: str
    atc_code: str
    mah: str

def translate_line(text, target_language='en'):
    translator = Translator()
    translation = translator.translate(text, dest=target_language)
    return translation.text

def build_product_record(product):
    res=build_medication_obj(product)+'\n'+'<-sc_node_not_relation;\n'
    res+=build_main_idtfs(product)
    res+=build_nrel(product)
    res+='\n'
    return res

def units_converter(isl_measure):
    replace_dict = {
        "ein.": "units",
        "ml": "ml",
        "alþjóðlegar einingar": 'international units',
        "míkróg": 'mg',
        'milljón':"million",
        "Speywood einingar": 'Speywood units',
        "frumur": 'cells',
        "einingar": 'units',
        'míkrógram': 'mg'
    }
    for isl_unit, eng_unit in replace_dict.items():
        isl_measure = isl_measure.replace(isl_unit, eng_unit)
    return isl_measure

def replace_icelandic_chars(text):
    text = text.lower()
    icelandic_to_english = {
        'á': 'a',
        'ä':'a',
        'å': 'a',
        'ð': 'd',
        'ø': 'o',
        'é': 'e',
        'í': 'i',
        'í':'i',
        'ó': 'o',
        'ú': 'u',
        'ý': 'y',
        'æ': 'ae',
        'ö': 'o',
        'þ': 'th',
    }
    for char, replacement in icelandic_to_english.items():
        text = text.replace(char, replacement)
    return text

def replace_characters(text):
    text=text.lower()
    characters = {
        '/':'_per_',
        '-':'_to_',
        '×':'_mult_',
        '^':'_deg_',
        '+':'_plus_',
        ',':'_dot_',
        ' ':'_',
        '(':'_',
        ')':'_',
        '&':'_',
        '%':'_percent_',
        '[':'_',
        ']':'_',
        'mgram': '_mg_'
    }
    for char, replacement in characters.items():
        text = text.replace(char, replacement)
    text = re.sub('_+', '_', text)
    if text.endswith('_'):
        text = text[:-1]
    text = re.sub(r'[^\x20-\x7E]', '', text)
    return text
    

def build_medication_obj(product):
    line = replace_characters(replace_icelandic_chars(units_converter(f"medication {product.name} {product.strength}")))
    return line

def build_main_idtfs(product):
    res = '=>nrel_main_idtf:\n'
    lang_en = f'    [{product.name} ({units_converter(product.strength)})] (* <- lang_en;;*);'
    lang_is = f'    [{product.name} ({product.strength})] (* <- lang_is;;*);'
    res = res + lang_en + '\n' + lang_is + '\n'
    return res

def build_nrel(product):
    return f"""=>nrel_atc_code: {product.atc_code};\n=>nrel_company: [{product.mah.
    replace("*",'')}];\n=>nrel_countries_of_sale: Iceland;\n=>nrel_active_substances: {
        replace_characters(replace_icelandic_chars(units_converter(product.active_ingredient)))};;\n"""

def create_pharmaceutical_product(row):
    return PharmaceuticalProduct(
        name=row.get('Name of Product'),
        active_ingredient=row.get('Active Ingredient'),
        pharmaceutical_form=row.get('Pharmaceutical Form'),
        strength=row.get('Strength'),
        atc_code=row.get('ATC Code'),
        mah=row.get('MAH')
    )

df = pd.read_excel('D:/university/labs_5_sem/Course/sources/iceland_drugs.xlsx')

df.drop(['Marketing authorisation number', 'Other Information', 'Legal Status', 'Marketed', 'MA Issued'], inplace=True, axis=1)
df.dropna(axis=0,inplace=True)
df.drop_duplicates(subset=['Name of Product','Strength'],inplace=True)
prepared_df = df.to_dict(orient='records')
products = [create_pharmaceutical_product(product_note) for product_note in prepared_df]
arr = [build_product_record(_) for _ in products]
with open('iceland_drugs.scs', 'a', encoding='utf-8') as file:
    file.write(''.join(arr))
