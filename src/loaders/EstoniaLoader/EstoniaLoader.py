import requests
import pandas as pd
from io import BytesIO
from googletrans import Translator

class EstoniaLoader():
    def load_everything(self, file_path):
        table_url = 'https://ravimiregister.ee/Data/XML/hum_medProducts.csv'
        response = requests.get(table_url)
        drugs_table = pd.read_csv(BytesIO(response.content), delimiter = ';',encoding="unicode_escape")
        

        for i in range(len(drugs_table)):
            original_name = drugs_table['ï»¿Name'][i].lower()
            name = self.remove_dozage(original_name).strip(' ').replace(' ', '_')
            if isinstance(drugs_table['Strength of active substance'][i], str): 
                strengths = drugs_table['Strength of active substance'][i].replace('/', ' ').replace('+', ' ').split()
                strengths = self.delete_nonexisting_dosages(strengths)
            else:
                strengths = []
            company = drugs_table['Marketing autorization holder or manufacturer'][i]
            company = self.delete_wierd_characters(company).strip().replace(' ', '_').replace('&', 'and')
            routes = drugs_table['Route of administration'][i].split(',')
            form = drugs_table['Dosage form'][i].replace('-', '_')
            actives = drugs_table['Name of active substance'][i].split('+')
            for strength in strengths:
                file = open(file_path, 'a+', encoding = 'utf-8')
                number, measurement = self.seperate_dosage(strength)
                file.write(f"{name}_{number}_{measurement}=[*\n")
                file.write(f"concept_{name}_{number}_{measurement}\n<-sc_node_not_relation;\n<-consept_medication(*<-sc_node_not_relation;;*);")
                file.close()
                self.write_atc(drugs_table['ATC code'][i], file_path)
                file = open(file_path, 'a+', encoding = 'utf-8')
                file.write(f"\n=>nrel_main_idtf:[{name} ({strength})](*<-lang_en;;*);\n")
                file.write(f"=>nrel_company:{company};\n")
                file.write(f"=>nrel_countries_of_sale:...(*->country_estonia;;*);\n")
                for route in routes:
                    route = route.strip(' ').replace(' ', '_')
                    route = route.replace('use', 'route')
                    file.write(f"=>nrel_route_of_administration:concept_{route}(*<-sc_node_not_relation;;*);\n")
                file.write(f"=>nrel_dosage_form:concept_{form.replace(' ', '_')}(*<-sc_node_not_relation;;*);\n")
                file.write(f"=>nrel_dosage:...(*\n\t<-sc_node_not_relation;;\n\t<-concept_dosage(*<-sc_node_not_relation;;*);;")
                file.write(f"\n\t=>nrel_measurement_in_{measurement}:{number}(*<-concept_number(*<-sc_node_not_relation;;*);;*);;*);")
                for active in actives:
                    active = active.split(',')[-1]
                    active = active.lower().replace(' ', '_')
                    file.write(f"\n=>nrel_active_substances:...(*->{active}(*\n\t<-sc_node_not_relation;;")
                    file.write(f"\n\t<-concept_pharmacologic_substance(*<-sc_node_not_relation;;*);;*);;*);")
                file.write(';\n*];;\n\n')
                file.close()

    def write_atc(self, atc_code, file_path):
        atc_url = 'https://ravimiregister.ee/en/Data/XML/atc.csv'
        response = requests.get(atc_url)
        atc_tree = pd.read_csv(BytesIO(response.content), delimiter = ';',encoding="unicode_escape")

        with open(file_path, 'a+') as file:
            layers = [atc_code[0], atc_code[:3], atc_code[:4], atc_code[:5], atc_code]
            for layer in layers:
                description = ''
                left = 0
                right = len(atc_tree)-1
                while left<=right:
                    mid = (left+right)//2
                    if atc_tree['ATC kood'][mid] == layer:
                        description = atc_tree['Nimi'][mid].lower()
                        description = self.translate(atc_tree['Nimi'][mid], 'et', 'en').lower()
                        description = self.delete_excess(description)
                        break
                    elif atc_tree['ATC kood'][mid] > layer:
                        right = mid-1
                    else:
                        left = mid+1
                if description != '':
                    file.write(f"\n<-concept_{layer.lower()}_{description}(*<-sc_node_not_relation;;*);\n=>nrel_atc_code:[{layer}];")

    def translate(self, text, origin_lan, dest_lan):
        translator = Translator()
        result = translator.translate(text, src = origin_lan, dest = dest_lan).text
        return result
    
    def delete_wierd_characters(self, string):
        i = 0
        while i < len(string):
            if ord(string[i]) < 128:
                i+=1
            else:
                string = string[:i] + string[i+1:]
        return string
    
    def delete_excess(self, string):
        forbidden_characters = [' ', '-', '+']
        left_bracket, right_bracket = string.find('('), string.find(')')
        if left_bracket != -1 and right_bracket != -1:
            string = string[:left_bracket].strip() +' '+ string[right_bracket+1:].strip()
        string = string.split(',')[0]
        for character in forbidden_characters:
            string = string.replace(character, '_')
        string = string.replace('&', 'and')
        return string
 
    def remove_dozage(self, drug):
        i = 0
        while i<len(drug):
            if drug[i].isdigit():
                return drug[:i]
            i+=1
        return drug
    
    def seperate_dosage(self, dose):
        i = 0
        while i< len(dose) and dose[i].isdigit():
            i+=1
        return dose[:i].strip(' '), dose[i:].strip(' ')

    def delete_nonexisting_dosages(self, strengths):
        measurements = ['mg', 'mcg', 'ml', 'g']
        i = 0
        while i < len(strengths):
            num, measurement = self.seperate_dosage(strengths[i])
            if measurement in measurements:
                i+=1
            else:
                strengths.pop(i)
        return strengths



