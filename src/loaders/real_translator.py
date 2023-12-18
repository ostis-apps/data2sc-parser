import json
from googletrans import Translator
import pubchempy as pcp

def get_substance_name(substance):
    try:
        compound = pcp.get_compounds(substance, 'name', record_type='3d')[0]
        return compound.iupac_name
    except Exception as e:
        print(f"Error retrieving name for {substance}: {e}")
        return f"[{substance}]"
        # return f"[Unknown_Active_Substance_{substance}]"

def translate(text):
    translator = Translator()
    trans = translator.translate(text)
    return trans.text

def fix_name(name):
    name = name.replace(" ", "_")
    return name.lower()

# Добавлена обработка ошибок для функции fix_dose
def fix_dose(dose):
    try:
        if dose == '-':
            result = ["", ""]
            return result
        dose = dose.replace(" ", "")
        dose = dose.replace("(", "")
        dose = dose[0:dose.find('g')+1]
        dose1 = "_" + dose
        dose2 = "(" + dose + ")"
        result = [dose1, dose2]
        return result
    except Exception as e:
        print(f"Error in fix_dose: {e}")
        return ["", ""]

# Добавлена обработка ошибок для функции fix_P_name
def fix_P_name(P_name0, name_en):
    try:
        if '+' in P_name0:
            result = ""
            sp = P_name0.split(sep='+')
            for n in sp:
                result = result + "["
                result = result + n + "]; "
        else:
            result = P_name0
        if P_name0 == '-' or any(char.isdigit() for char in P_name0):
            result = name_en
        return result
    except Exception as e:
        print(f"Error in fix_P_name: {e}")
        return ""

# Добавлена обработка ошибок для функции fix_country
def fix_country(country):
    try:
        sp = country.split()
        st = set(sp)
        result = ""
        for n in st:
            result = result + n + "; "
        return result
    except Exception as e:
        print(f"Error in fix_country: {e}")
        return ""

def get_substance_name(substance):
    try:
        compound = pcp.get_compounds(substance, 'name', record_type='3d')[0]
        return compound.iupac_name
    except Exception as e:
        print(f"Error retrieving name for {substance}: {e}")
        return f"[{substance}]"

def fix_active(active0, name_en, composicion_pa):
    if any(char.isdigit() for char in active0):  # Если есть цифры
        # Используем IUPAC-имя из PubChem
        substance_name = get_substance_name(active0)
        result = f"{substance_name};" if substance_name else ""
    else:
        if '+' in active0:
            result = ""
            sp = active0.split(sep='+')
            for n in sp:
                n = n.replace(" ", "_")
                result += "[" + n + "]; "
        else:
            result = '[' + active0 + "];"

    # Если IUPAC-имя пусто, используем название препарата
    if result == "[Unknown_Active_Substance_" + active0 + "]":
        result = f"[{name_en}]"

    return result

def fix_dosage_form(dosage_form):
    dosage_form = dosage_form.replace(" ", "_")
    return dosage_form

def fix_route(dosage_form):
    result = ""
    dosage_form_low = dosage_form.lower()
    if 'injection' in dosage_form_low or 'infusion' in dosage_form_low:
        result = 'concept_parenteral_route;'
    if 'cream' in dosage_form_low or 'gel' in dosage_form_low or 'transdermal' in dosage_form_low:
        result = 'concept_transdermal_route;'
    if 'drops' in dosage_form_low or 'eyes' in dosage_form_low:
        result = 'concept_intra_ocular_route;'
    if 'capsules' in dosage_form_low or 'pills' in dosage_form_low or 'tablets' in dosage_form_low:
        result = 'concept_oral_route;'
    if result != "":
        result = '=> nrel_route_of_administration:' + result
    return result


def create_file(templates, num_files, num_scs):
    count = 0
    medications_count = len(templates)

    for i in range(num_files):
        if count < medications_count:
            with open(f"{i}.scs", "w", encoding="utf-8") as file:
                for j in range(num_scs):
                    if count < medications_count:
                        file.write("\n\n" + templates[count])
                        count += 1
                    else:
                        break


def get_user_input():
    try:
        num_medications = int(input("Введите количество лекарств для обработки (оставьте пустым для всех): "))
        return num_medications
    except ValueError:
        print("Некорректный ввод. Будут обработаны все лекарства.")
        return None


def parse_and_input(json_file_path, num_files=5, num_scs=2):
    with open(json_file_path, 'r') as json_file:
        json_data = json.load(json_file)

    templates = []
    num_medications = get_user_input()

    medications_processed = 0

    for prescription in json_data.get("aemps_prescripcion", {}).get("prescription", []):
        name_en = prescription.get("des_nomco", "")
        dose0 = prescription.get("des_dosific", "")
        ATC = prescription.get("atc", {}).get("cod_atc", "")
        composicion_pa_list = prescription.get("formasfarmaceuticas", {}).get("composicion_pa", [])

        if not composicion_pa_list or not isinstance(composicion_pa_list, list):
            continue

        composicion_pa = composicion_pa_list[0]
        P_name0 = composicion_pa.get("dosis_prescripcion", "")

        name_en = name_en.split('/')[0].strip()

        company = prescription.get("laboratorio_titular", "")
        country0 = "Spain"
        active0 = prescription.get("des_nomco", "")
        dosage_form0 = "Injection"
        name = fix_name(name_en).lower()
        dose = fix_dose(dose0)
        dose1 = dose[0]
        dose2 = dose[1]
        P_name = fix_P_name(P_name0, name_en)
        print(f"P_name: {P_name}")
        active = fix_active(active0, name_en, composicion_pa)
        country = fix_country(country0)
        dosage_form = fix_dosage_form(dosage_form0)
        route = fix_route(dosage_form0)

        template = f"""
        medication_{name}{dose1}
        <-sc_node_not_relation;
        => nrel_main_idtf:
                        [{name_en} {dose2}] (* <- lang_en;;*);
        => nrel_atc_code: {ATC};
        => nrel_international_non_proprietary_name: {P_name}
        => nrel_company: [{company}];
        => nrel_countries_of_sale: {country}
        => nrel_active_substances: {active}
        => nrel_dosage_form:{dosage_form};
        {route};
         """
        templates.append(template)

        medications_processed += 1
        if num_medications is not None and medications_processed >= num_medications:
            break

    num_files_to_create = (medications_processed + num_scs - 1) // num_scs  # Деление с округлением вверх
    create_file(templates, num_medications if num_medications is not None else num_files_to_create, num_scs)


# Пример использования:
json_file_path = 'db.json'
parse_and_input(json_file_path)
