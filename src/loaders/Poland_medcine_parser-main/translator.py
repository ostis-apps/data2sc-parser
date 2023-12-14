import openpyxl
from googletrans import Translator


def translator(text, lang):
    ts= Translator()
    T = ts.translate(text, dest = lang)
    return T.text

def fix_name(name):
    name = name.replace(" ","_")
    return name

def fix_dose(dose):
    if dose == '-':
        result = ["",""]
        return result
    dose = dose.replace(",",".")
    dose = dose.replace(" ","")
    dose = dose.replace("(","")
    dose = dose.replace('niemniejniż','')
    if 'mg' in dose or 'mcg' in dose:
        dose = dose[0:dose.find('g')+1]
    elif 'j.m.' in dose:
        dose = dose[0:dose.find('j.m.')+1]
    dose = dose.replace(".","")
    dose1 = "_" + dose
    dose2 = "(" + dose + ")"
    result = [dose1,dose2]
    return result

def fix_P_name(P_name, name):
    if '+' in P_name:
        result = ""
        sp = P_name.split(sep = '+')
        for n in sp:
            result = result + "["
            result = result + n + "]; "
    else: result = '['+ P_name +'];'
    if P_name == '-':
        result = name + ';'
    return result
            
        
def fix_atc(atc):
    if atc == '':
        return ''
    else:
        return '=> nrel_atc_code: ' + atc + ';'
    
def fix_country(country):
    sp = country.split()
    st = set(sp)
    result = ""
    for n in st:
        result = result + n + "; "
    return result

def fix_active(active):
    if '+' in active:
        result = ""
        sp = active.split(sep = '+')
        for n in sp:
            n = n.replace(" ","_")
        for n in sp:
            result = result + "["
            result = result + n + "]; "
    else:
        result = '[' + active + "];"
    return result

def fix_dosage_form(dosage_form):
    dosage_form = dosage_form.replace("/","")
    dosage_form = dosage_form.replace(" ","_")
    dosage_form = dosage_form.replace(",","")
    return dosage_form
    
def fix_route(dosage_form):
    result = ""
    dosage_form_low = dosage_form.lower()
    if 'injection' in dosage_form_low or 'infusion' in dosage_form_low:
        result = 'concept_parenteral_route;;'
    if 'cream' in dosage_form_low or 'gel'in dosage_form_low or 'transdermal' in dosage_form_low:
        result = 'concept_transdermal_route;;'
    if 'drops' in dosage_form_low or 'eyes'in dosage_form_low:
        result = 'concept_intra_ocular_route;;'
    if 'capsules' in dosage_form_low or 'pills' in dosage_form_low or 'tablets' in dosage_form_low:
        result = 'concept_oral_route;;'
    if result != "":
        result = '=> nrel_route_of_administration:' + result
    return result

def create_file(templates, c_files, c_scs):
    count = 0
    for i in range(c_files):
        file = open(f"{i}.scs","a+",encoding="utf-8")
        for j in range(c_scs):
            count+=1
            file.write(templates[count])
        file.close()   

def parse_and_input(excel_file, number_of_files, number_of_scs):
    workbook = openpyxl.open(excel_file, read_only = True)
    sheet = workbook.active
    templates = []
    for row in range(2,number_of_scs * number_of_files + 1):
        name_pl = sheet[row][1].value
        name_en = translator(name_pl, 'en')
        dose0 = sheet[row][4].value
        ATC = sheet[row][6].value
        ATC = fix_atc(ATC)
        P_name0 = sheet[row][2].value
        company = translator(sheet[row][7].value, 'en')
        dosage_form0 = translator(sheet[row][5].value, 'en')
        
        country_test = sheet[row][10].value
        if country_test == "":
            country_test = "Polska"
        country0 = translator(country_test, 'en')
            
        name = fix_name(name_en).lower().replace('%','')
        dose = fix_dose(dose0)
        dose1 = dose[0]
        dose2 = dose[1]
        P_name =  fix_P_name(P_name0, name_en)
        
        active_test = sheet[row][8].value 
        if active_test == "":
            active_test = P_name
        active0 = translator(active_test, 'en')
        
        active = fix_active(active0)
        country = fix_country(country0)
        dosage_form = fix_dosage_form(dosage_form0)
        route = fix_route(dosage_form0)
        end =''
        if route == "":
            end = ';'
        
        template = f"""
medication_{name}{dose1}
<-sc_node_not_relation;
=> nrel_main_idtf:
                [{name_en} {dose2}] (* <- lang_en;;*);
                [{name_pl} {dose2}] (* <- lang_pl;;*);
{ATC}
=> nrel_international_non_proprietary_name: {P_name}
=> nrel_company: [{company}];
=> nrel_countries_of_sale: {country}
=> nrel_active_substances: {active}
=> nrel_dosage_form:{dosage_form};{end}
{route}
         """
        templates.append(template)
    create_file(templates, number_of_files, number_of_scs)

             
excel_file = 'C:\work\Course\Med.xlsx'
values = parse_and_input(excel_file, 5, 10)


    



