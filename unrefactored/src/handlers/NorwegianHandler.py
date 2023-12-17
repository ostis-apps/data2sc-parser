import sys

from selenium.webdriver.common.by import By
from src.generics import StandartXLSXHandler


class NorwegianHandler(StandartXLSXHandler):

    TEXT_LINK_SEQUENCE = [
        (By.PARTIAL_LINK_TEXT, 'Pakninger', 6),
        (By.PARTIAL_LINK_TEXT, 'Eksporter resultater', 6)
    ]
    URL = 'https://www.legemiddelsok.no/'
    COUNTRY_CODE = 'no'
    FILENAME_RAW = f'data_{COUNTRY_CODE}.xlsx'
    OUTPUT_DIR = f'output/{COUNTRY_CODE}/'
    RAW_DATA_DIR = f"{sys.path[0]}\\data\\"
    XLSX_MAPPING = {
            'Handelsnavn': 'name',
            'Form': 'form',
            'Styrke tallverdi': 'dose_value',
            'Styrke enhet': 'dose_unit',
            'ATC-kode': 'code',
            'Virkestoff': 'active_substance',
            'MT-innehaver': 'manufacturer'
        }

