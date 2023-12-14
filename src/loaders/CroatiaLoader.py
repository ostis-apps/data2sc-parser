import requests
import pandas as pd
from io import BytesIO
from googletrans import Translator
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup as bs
import PyPDF2
from PyPDF2 import PdfReader
import xml.etree.ElementTree as ET


class CroatiaLoader():
    def load_everything(self, file_path):
        table_url = 'https://www.halmed.hr/hr/Download/xls/lijekovi/Halmed_Lijekovi_165647b33eeb4d.xlsx"'
        response = requests.get(table_url)
        drugs_table = pd.read_exel(BytesIO(response.content), delimiter=';', encoding="unicode_escape")

        for i in range(7000):
            original_name = drugs_table['Naziv'][i].lower()
            name, strengths = self.remove_dozage(original_name).replace(' ', '_')
            #strengths = drugs_table['Strength of active substance'][i].split('+')
            company = drugs_table['Proizvođač'][i].replace(' ', '_')
            #routes = drugs_table['Route of administration'][i].split(',')
            form = drugs_table['Farmaceutski oblik'][i].replace('-', '_')
            actives = drugs_table['Djelatna tvar'][i].split('+')
            for strength in strengths:
                file = open(file_path, 'a+', encoding = 'utf-8')
                if strength.isdigit():
                    number, measurement = self.seperate_dosage(strength)
                    file.write(f"{name}_{number}_{measurement}=[*")
                    file.write(f"concept_{name}_{number}_{measurement}(*<-sc_node_not_relation;;*)\n\t<-consept_medication(*<-sc_node_not_relation;;*);;")
                    file.write(f"\n\t\t=>nrel_measurement_in_{measurement}:{number}(*<-concept_number(*<-sc_node_not_relation;;*);;*);;*);;")
                    file.close()
                else:
                    file.write(
                        f"concept_{name}_{strength}(*<-sc_node_not_relation;;*)\n\t<-consept_medication(*<-sc_node_not_relation;;*);;")
                    file.close()
                self.write_atc(drugs_table['ATK'][i], file_path)
                file = open(file_path, 'a+', encoding = 'utf-8')
                file.write(f"\n\t=>nrel_main_idtf:[{name} ({strength})](*<-lang_en;;*);;\n")
                file.write(f"\t=>nrel_company:{company};;\n")
                file.write(f"\t=>nrel_countries_of_sale:...(*->country_croatia;;*);;\n")
                # for route in routes:
                #     route = route.strip(' ').replace(' ', '_')
                #     route = route.replace('use', 'route')
                #     file.write(f"\t=>nrel_route_of_administration:concept_{route}(*<-sc_node_not_relation;;*);;\n")
                file.write(f"\t=>nrel_dosage_form:concept_{form.replace(' ', '_')}(*<-sc_node_not_relation;;*);;\n")
                file.write(f"\t=>nrel_dosage:...(*\n\t\t<-sc_node_not_relation;;\n\t\t<-concept_dosage(*<-sc_node_not_relation;;*);;")
                for active in actives:
                    active = active.split(',')[-1]
                    active = active.lower().replace(' ', '_')
                    file.write(f"\n\t=>nrel_active_substances:...(*->{active}(*\n\t\t<-sc_node_not_relation;;")
                    file.write(f"\n\t\t<-concept_pharmacologic_substance(*<-sc_node_not_relation;;*);;*);;*);;*];;\n\n")
                file.close()
    
    def pdf_reader(self, drug_name):
        url = 'https://ravimiregister.ee/en/publichomepage.aspx?pv=PublicSearchResult'

        driver = webdriver.Chrome()
        driver.get(url)

        open_the_search_button = driver.find_element(By.CLASS_NAME, 'openSearchMobileLiteral')
        open_the_search_button.click()

        search_input = driver.find_element(By.NAME, 'publicSearch$nimetusTextField')
        search_input.send_keys('cipralex')

        search_button = driver.find_element(By.ID, 'publicSearch_doDrugSearchButton')
        search_button.click()

        soup = bs(driver.page_source, 'html.parser')
        download_links = soup.find_all('div', class_ = 'public-search-result-item-middle-right-field')
        for download_link in download_links:
            if download_link.a != None:
                download_link = download_link.a['href']

        response = requests.get('https://ravimiregister.ee' + download_link)
        #pdf_file = codecs.open(response.content, mode='rb', encoding='latin1')
        pdf_file = open('file.pdf', 'wb')
        pdf_file.write(response.content)
        pdf_file.close()
        reader = PyPDF2.PdfReader('file.pdf')
        page = reader.pages[0]
        print(page.extract_text())
        pdf_file.close()

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
                    print(f"right = {right}, left = {left}, mid = {mid}")
                    if atc_tree['ATC kood'][mid] == layer:
                        description = atc_tree['Nimi'][mid].lower()
                        description = self.translate(atc_tree['Nimi'][mid], 'et', 'en').lower().replace(' ', '_')
                        break
                    elif atc_tree['ATC kood'][mid] > layer:
                        right = mid-1
                    else:
                        left = mid+1
                if description != '':
                    file.write(f"\n\t<-concept_{layer}_{description}(*<-sc_node_not_relation;;*);;\n\t=>nrel_atc_code:[{layer}];;")

    def translate(self, text, origin_lan, dest_lan):
        translator = Translator()
        result = translator.translate(text, src = origin_lan, dest = dest_lan).text
        return result
 
    def remove_dozage(self, drug):
        i = 0
        endd = ['ml', 'mg']
        if drug.startswith('injekciju') == True:
            return drug[:drug.find('injekciju')], 'injekciju'
        else:
            while i<len(drug):
                if drug[i].isdigit():
                    name = drug[:i]
                    streng = drug[i:]
                    for word in endd:
                        if word in streng:
                            strenght = streng[:streng.find(word)+1]
                            return name, strenght
                    if '%' in streng:
                        strenght = streng[:streng.find('%')]
                        return name, strenght
                i+=1



        return drug
    
    def seperate_dosage(self, dose):
        i = 0
        while dose[i].isdigit():
            i+=1
        return dose[:i], dose[i:]


#'''
loader = CroatiaLoader()
loader.load_everything("test.scs")
#'''

#loader = EstoniaLoader()
#loader.pdf_reader('cipralex')
'''
loader = EstoniaLoader()
file = loader.load_everything()
file = open('test.txt')
lines = file.readlines()
for line in lines:
    print(line, end='')
'''