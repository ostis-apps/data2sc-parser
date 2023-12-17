import sys

from selenium.webdriver.common.by import By
import pandas as pd
from string import punctuation

from src.generics import StandartXLSXHandler


class AustrianHandler(StandartXLSXHandler):

    INITIAL_WAIT_SECONDS = 8
    TEXT_LINK_SEQUENCE = [
        (By.XPATH, "//button[contains(text(),'Suchen')]", 1),
        (By.XPATH, "//img[@title='Trefferliste als .xls herunterladen']", 45)
    ]
    URL = 'https://aspregister.basg.gv.at/aspregister/faces/aspregister.jspx'
    COUNTRY_CODE = 'au'
    FILENAME_RAW = f'data_{COUNTRY_CODE}.xlsx'
    OUTPUT_DIR = f'output/{COUNTRY_CODE}/'
    RAW_DATA_DIR = f"{sys.path[0]}\\data\\"
    XLSX_MAPPING = {
            'Name': 'name',
            'ATC Code': 'code',
            'Wirkstoff': 'active_substance',
            'Inhaber/-in	': 'manufacturer'
        }

    def generate(self) -> dict:
        """
        A simple generator that yields .json entries for .scs templates.
        """
        raw_df = pd.read_excel(f"{self.RAW_DATA_DIR}\\{self.FILENAME_RAW}")
        raw_df = raw_df[self.XLSX_MAPPING.keys()]
        raw_df = raw_df.dropna()
        raw_df = raw_df.rename(columns=self.XLSX_MAPPING)
        raw_df = raw_df.astype('str')

        for idx, row in raw_df.iterrows():
            out = row.to_dict()
            for c in punctuation.replace('_', '').replace('%', '') + '„“–':
                out['name'] = out['name'].replace(c, '')
            out['name'] = "_".join(out['name'].split(' '))

            option_list = [out['name'].partition(x) for x in
                           ['_mg_', '_mg/' '_g_', '_g/', '_E_', '_E/', '_I_', '_I/', '_mmol_', '_mmol/', '_%']]
            name, dose_unit, _ = min(option_list, key=lambda x: len(x[0]))
            name = name.strip()
            if len(dose_unit) == 0:
                continue

            name, dose_value = "_".join(name.split('_')[:-1]), name.split('_')[-1]

            out['name'] = name.strip('_')
            out['dose_value'] = [dose_value.strip('_')]
            out['dose_unit'] = [dose_unit.strip('_')]
            out['active_substance'] = out['active_substance'].split()

            yield out
