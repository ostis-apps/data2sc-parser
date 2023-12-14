import sys
import requests
import xml.etree.ElementTree as ET
import json
import re
from io import BytesIO
import pandas as pd
from googletrans import Translator

xml_url = "https://www.hpra.ie/img/uploaded/swedocuments/latestHMlist.xml"

def read_file():
    response = requests.get(xml_url)
    response.raise_for_status()

    root = ET.fromstring(response.text)

    for product_elem in root.findall(".//{http://www.hpra.ie/xml/productsHM}Product"):
        product_name = product_elem.findtext(".//{http://www.hpra.ie/xml/productsHM}ProductName")
        formatted_product_name = "medicine_" + re.sub(r'[^a-zA-Z0-9]+', '_', product_name.lower())
        formatted_product_name = re.sub(r'_+', '_', formatted_product_name)
        formatted_product_name = re.sub(r'[.,-/_\s]+$', '', formatted_product_name)
        pa_holder = product_elem.findtext(".//{http://www.hpra.ie/xml/productsHM}PAHolder")
        formatted_pa_holder = "company_" + re.sub(r'[^a-zA-Z0-9]+', '_', pa_holder.lower().replace("&", "_and_").replace("+", "_and_"))
        formatted_pa_holder = re.sub(r'\([^)]*\)', '', formatted_pa_holder)
        formatted_pa_holder = re.sub(r'_+', '_', formatted_pa_holder.replace("\xa0", "_"))
        formatted_pa_holder = re.sub(r'[.,-/_\s]+$', '', formatted_pa_holder)
        dosage_form = product_elem.findtext(".//{http://www.hpra.ie/xml/productsHM}DosageForm")
        formatted_dosage_form = "concept_" + dosage_form.lower().replace(",", "").replace(" ", "_").replace("-", "_").replace("/", "_or_").replace("+", "_and_") + "_form"
        formatted_dosage_form = re.sub(r'_+', '_', formatted_dosage_form)
        formatted_active_substances = ["pharmacological_substance_" + re.sub(r'[^a-zA-Z0-9]+', '_', substance.text.lower()) for substance in product_elem.findall(".//{http://www.hpra.ie/xml/productsHM}ActiveSubstance")]
        formatted_active_substances = [re.sub(r'\([^)]*\)', '', i) for i in formatted_active_substances]
        formatted_active_substances = [re.sub(r'_+', '_', i) for i in formatted_active_substances]
        formatted_active_substances = [re.sub(r'[.,-/_\s]+$', '', i) for i in formatted_active_substances]
        product_dict = {
            "ProductName Full": product_name,
            "ProductName": formatted_product_name,
            "PAHolder": formatted_pa_holder,
            "DosageForm": formatted_dosage_form,
            "ATCs": [atc.text for atc in product_elem.findall(".//{http://www.hpra.ie/xml/productsHM}ATC")],
            "RoutesOfAdministration": ["concept_" + re.sub(r'[^a-zA-Z0-9]+', '_', route.text.lower()).replace("use", "route") for route in product_elem.findall(".//{http://www.hpra.ie/xml/productsHM}RoutesOfAdministration") if route.text and not route.text.isspace()],
            "ActiveSubstances": formatted_active_substances
        }

        
            
        products_list.append(product_dict)


    with open("products.json", "w", encoding="utf-8") as json_file:
        json.dump(products_list, json_file, ensure_ascii=False, indent=2)

def create_scs():
    
    for dictionary in products_list:

        product_string = ["{}=[*\n".format(dictionary["ProductName"]),
        "    sc_node_norole_relation->nrel_dosage_form;;", "    sc_node_norole_relation->nrel_company;;",
        "    sc_node_norole_relation->nrel_atc_code;;", "    sc_node_not_relation->concept_route_of_administration;;",
        "    sc_node_norole_relation->nrel_atc_level_code;;", "    sc_node_norole_relation->nrel_countries_of_sale;;",
        "    sc_node_not_relation->concept_pharmacological_substance;;", "    sc_node_norole_relation->nrel_route_of_administration;;",
        "    sc_node_norole_relation->nrel_active_substances;;\n", "    medication_{}".format(dictionary["ProductName"]),
        "    <-concept_medication;", "    =>nrel_countries_of_sale:...(*->country_ireland;;*);", "    =>nrel_main_idtf:[{}] (* <-lang_eng;;*);".format(re.sub(r'[^a-zA-Z0-9/+\&]+', ' ', dictionary["ProductName Full"])),
        "    =>nrel_company:{};".format(dictionary["PAHolder"])]

        if dictionary["ActiveSubstances"] == [] and dictionary["RoutesOfAdministration"] == [] and dictionary["ATCs"] == []:
            product_string.append("    =>nrel_dosage_form:{}(*<-sc_node_not_relation;;*);;".format(dictionary["DosageForm"]))
        else:
            product_string.append("    =>nrel_dosage_form:{}(*<-sc_node_not_relation;;*);".format(dictionary["DosageForm"]))
        
        

        for index, atc_code in enumerate(dictionary["ATCs"]):
            is_last_atc_code = index == len(dictionary["ATCs"]) - 1
            atc_code_concept = write_atc(atc_code)
            atc_code_concept = re.sub(r'[^a-zA-Z0-9]+', '_', str(atc_code_concept))
            atc_code_concept = re.sub(r'_+', '_', str(atc_code_concept))
            
            if dictionary["ActiveSubstances"] == [] and dictionary["RoutesOfAdministration"] == [] and is_last_atc_code:
                if(atc_code_concept == "None"):
                    product_string.append("    =>nrel_atc_code:[{}];".format(atc_code))
                else:
                    product_string.append("    =>nrel_atc_code:[{}] (*<=nrel_atc_level_code:concept_{}_{};;*);;".format(atc_code, str(atc_code).lower(), atc_code_concept))
            else:
                if(atc_code_concept == "None"):
                    product_string.append("    =>nrel_atc_code:[{}];".format(atc_code))
                else:
                    product_string.append("    =>nrel_atc_code:[{}] (*<=nrel_atc_level_code:concept_{}_{};;*);".format(atc_code, str(atc_code).lower(), atc_code_concept))

        if(dictionary["ActiveSubstances"] != []):
            product_string.append("\n    =>nrel_active_substances:...")
            product_string.append("        (*")
            for active_substance in dictionary["ActiveSubstances"]:
                product_string.append("        ->{}(*".format(active_substance))
                product_string.append("        <-sc_node_not_relation;;")
                product_string.append("        <-concept_pharmacological_substance;;*);;")
            
            product_string.append("        *);;")

    
        if(dictionary["RoutesOfAdministration"] != []):
            if(dictionary["ActiveSubstances"] != []):
                product_string.append("\n    medication_{}".format(dictionary["ProductName"]))
            product_string.append("    =>nrel_route_of_administration:...")
            product_string.append("        (*")
            for route_of_administration in dictionary["RoutesOfAdministration"]:
                product_string.append("        ->{}(*".format(route_of_administration))
                product_string.append("        <-sc_node_not_relation;;")
                product_string.append("        <-concept_route_of_administration;;*);;")
            
            product_string.append("        *);;")

        product_string.append("\n*];;\n\n")

        with open("medicine_products.scs", "a", encoding="utf-8") as scs_file:
            for string in product_string:
                scs_file.write("{}\n".format(string))


def translate_from_et_to_en(text):
    translator = Translator()
    translation = translator.translate(text, src='et', dest='en')

    if translation and hasattr(translation, 'text'):
        return translation.text
    else:
        print(f"Translation failed. Response text: {translator.response.text}")
        return None

def write_atc(atc_code):
    atc_url = 'https://ravimiregister.ee/en/Data/XML/atc.csv'
    response = requests.get(atc_url)
    atc_tree = pd.read_csv(BytesIO(response.content), delimiter=';', encoding="unicode_escape")

    description = ''
    left = 0
    right = len(atc_tree) - 1
    while left <= right:
        mid = (left + right) // 2
        if atc_tree['ATC kood'][mid] == atc_code:
            description = atc_tree['Nimi'][mid]
            translated_description = translate_from_et_to_en(description).lower().replace(' ', '_')
            break
        elif atc_tree['ATC kood'][mid] > atc_code:
            right = mid - 1
        else:
            left = mid + 1
    if description != '':
        return translated_description


try:

    products_list = []
    read_file()
    create_scs()

except requests.exceptions.RequestException as e:
    print(f"Error fetching the XML content: {e}")
except ET.ParseError as e:
    print(f"Error parsing the XML content: {e}")

