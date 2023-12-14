import json
import re
from googletrans import Translator


def translate_to_russian(text):
    translator = Translator()
    translation = translator.translate(text, dest='ru')
    return translation.text


def substances_check(substances):
    with open('extra/active.scs', 'r') as actives_file:
        actives = actives_file.read()
    for substance in substances:
        if substance not in actives:
            substance_identifier = substance.replace('_', ' ')
            substance_identifier_ru = translate_to_russian(substance_identifier)
            active_template = f"""{substance}
    =>nrel_main_idtf:[{substance_identifier_ru}] (* <-lang_ru;;*);
    =>nrel_main_idtf:[{substance_identifier}] (* <-lang_en;;*);;   
                    """
            file_name = f"extra/active.scs"
            with open(file_name, 'a') as file:
                file.write(active_template + '\n')


if '__name__' == '__main__':
    with open('result.json', 'r') as file:
        data = json.load(file)

    for item in data:
        name = item["Название препарата (английский)"]
        identifier = name.replace('_', ' ')
        identifier_ru = translate_to_russian(identifier)
        dose = item["Дозировка"]
        ATC = item["ATC-код"]
        P_name = item["Варианты альтернативного названия препарата"]
        license_holder = item["Производитель/держатель лицензии"]
        dos_form = item["Фармацевтическая форма"]
        usage_method = item["Способы применения"]
        active = item["Действующие вещества"]
        substances_check(active)

        drug_template = f"""medication_{name}_{dose}
            <-sc_node_not_relation;
            => nrel_main_idtf:
                            [{identifier} ({dose})] (* <- lang_en;;*);
                            [{identifier} ({dose})] (* <- lang_nl;;*);
            => nrel_atc_code: {ATC};
            => nrel_international_non_proprietary_name: [{P_name}];
            => nrel_company: [{license_holder}];
            => nrel_countries_of_sale: Netherlands;
            => nrel_active_substances: {active};
            => nrel_dosage_form: {dos_form};
            => nrel_usage_method: {usage_method};
            => nrel_route_of_administration:concept_parenteral_route;;"""

        file_name = f"scs_out/{name}.scs"
        with open(file_name, 'w') as file:
            file.write(drug_template)
