import os
import time
from string import punctuation
from abc import ABCMeta, abstractmethod

import pandas as pd
from selenium import webdriver
from jinja2 import Environment, FileSystemLoader
from utils.repair_xlsx import repair_xlsx
from utils.translate_text import translate


class AbstractHandler(metaclass=ABCMeta):

    URL = None
    OUTPUT_DIR = None

    @abstractmethod
    def generate(self) -> dict:
        """
        A generator type object that yields processed .json objects ready to be inserted into template.
        """
        pass

    @abstractmethod
    def render_scs(self) -> (str, str):
        """
        Uses 'generate' method to retrieve data.
        """
        pass

    @abstractmethod
    def run(self):
        """
        Runs the whole download-parse-render-save pipeline.
        """
        pass


class AbstractStreamHandler(AbstractHandler):

    @abstractmethod
    def generate_raw(self) -> dict:
        """
        A generator type object responsible for parsing and streaming data from target site.
        """
        pass


class AbstractXLSXHandler(AbstractHandler):

    RAW_DATA_DIR = None

    @abstractmethod
    def download_xlsx(self) -> None:
        """
        Downloads xlsx file from target site and saves it in filesystem.
        """
        pass

    def run(self):
        self.download_xlsx()
        os.makedirs(self.OUTPUT_DIR, exist_ok=True)
        for name, payload in self.render_scs():
            if name is not None:
                with open(f'{self.OUTPUT_DIR}{name}.scs', 'w', encoding="utf-8") as file:
                    file.write(payload)


class StandartXLSXHandler(AbstractXLSXHandler):

    INITIAL_WAIT_SECONDS = 0
    TEXT_LINK_SEQUENCE = None
    COUNTRY_CODE = None
    FILENAME_RAW = None
    XLSX_MAPPING = None

    def __init__(self):
        super().__init__()

        null_fields = []
        for field in ['TEXT_LINK_SEQUENCE', 'URL', 'COUNTRY_CODE', 'FILENAME_RAW', 'OUTPUT_DIR', 'RAW_DATA_DIR']:
            if getattr(self, field) is None:
                null_fields.append(field)

        if len(null_fields) > 0:
            raise Exception(f"Following fields can't be None: {', '.join(null_fields)}")

    def download_xlsx(self) -> None:
        """
        Downloads xlsx file from a target site and saves it in filesystem.
        """
        options = webdriver.ChromeOptions()
        os.makedirs(self.RAW_DATA_DIR, exist_ok=True)
        prefs = {"download.default_directory": self.RAW_DATA_DIR}
        options.add_experimental_option("prefs", prefs)

        driver = webdriver.Chrome(options=options)
        driver.maximize_window()

        try:
            # 1. Load page.
            driver.get(self.URL)
            time.sleep(self.INITIAL_WAIT_SECONDS)

            # 2. Navigates to download button using sequence of text links.
            for by, text, sleep in self.TEXT_LINK_SEQUENCE:
                element = driver.find_element(
                    by,
                    text
                )
                element.click()
                time.sleep(sleep)

            # 3. Check if xlsx file is downloaded.
            path = max([self.RAW_DATA_DIR + "\\" + f for f in os.listdir(self.RAW_DATA_DIR)], key=os.path.getctime)
            filename = path.split('\\')[-1]

            # 4. Rename file.
            os.rename(src=f"{self.RAW_DATA_DIR}\\{filename}", dst=f"{self.RAW_DATA_DIR}\\{self.FILENAME_RAW}")

            # 5. Repair xlsx file.
            repair_xlsx(f"{self.RAW_DATA_DIR}\\{self.FILENAME_RAW}", f"{self.RAW_DATA_DIR}\\{self.FILENAME_RAW}")

        except Exception as err:
            print(err)

    def generate(self) -> dict:
        """
        A simple generator that yields .json entries for .scs templates.
        """
        raw_df = pd.read_excel(f"{self.RAW_DATA_DIR}\\{self.FILENAME_RAW}")
        raw_df = raw_df[self.XLSX_MAPPING.keys()]
        raw_df = raw_df.dropna()
        raw_df = raw_df.rename(columns=self.XLSX_MAPPING)
        raw_df = raw_df.astype('str')
        if 'dose_unit' in raw_df.columns:
            raw_df = raw_df[raw_df['dose_unit'].str.contains('%') == 0]

        # # Run script with "export PYTHONIOENCODING=UTF-8" or uncomment this:
        # # ------------------------------------------------------------------
        # for name in raw_df.columns:
        #     raw_df[name] = raw_df[name].apply(lambda x: x.encode('unicode_escape').decode())

        if 'dose_value' in raw_df.columns:
            raw_df['dose_value'] = raw_df['dose_value'].apply(lambda x: x.replace(';', '/'))
            if 'dose_unit' in raw_df.columns:
                raw_df['dose_unit'] = raw_df['dose_unit'].apply(lambda x: x.replace(';', '/'))

        for idx, row in raw_df.iterrows():
            out = row.to_dict()
            for c in punctuation.replace('_', '').replace('%', '') + '„“–':
                out['name'] = out['name'].replace(c, '')
            out['name'] = "_".join(out['name'].split(' '))
            if 'form' in raw_df.columns:
                out['form'] = list(map(str.strip, out['form'].split(',')))
            if 'dose_value' in raw_df.columns:
                out['dose_value'] = out['dose_value'].replace(',', '_').replace('.', '_')
            if 'dose_value' in raw_df.columns:
                out['dose_value'] = list(map(str.strip, out['dose_value'].split('/')))
            if 'dose_unit' in raw_df.columns:
                out['dose_unit'] = list(map(str.strip, out['dose_unit'].split('/')))
            if 'active_substance' in raw_df.columns:
                out['active_substance'] = list(map(str.strip, out['active_substance'].split(';')))

            if all([x in out.keys() for x in ['dose_value', 'dose_unit', 'form']]):

                difference = len(out['dose_value']) - len(out['dose_unit'])

                if difference == 1:
                    out['dose_unit'] = out['dose_unit'] + out['dose_unit']
                elif difference == -1:
                    out['dose_value'] = out['dose_value'] + out['dose_value']

                if len(out['dose_value']) > 2 or len(out['dose_unit']) > 2 or abs(difference) > 1:
                    continue

                if not len(out['dose_value']) == len(out['dose_unit']) == len(out['form']):
                    continue

            yield out

    def render_scs(self) -> (str, str):
        """
        Generator responsible for yielding tuples consisting of filenames and rendered jinja2 templates.
        """

        jinja_env = Environment(loader=FileSystemLoader('./templates'))
        template = jinja_env.get_template('template.scs')

        for data in self.generate():

            for key in data.keys():
                if type(data[key]) == 'str':
                    data[key] = data[key].strip()

            data['labels'] = [
                (self.COUNTRY_CODE, data['name']),
                ('en', translate(data['name'])),
            ]

            data['name'] = data['name'].lower()

            if 'dose_value' in data.keys() and 'dose_unit' in data.keys():
                for dvalue, dunit in zip(data['dose_value'], data['dose_unit']):
                    identifier = f'medication_{data["name"]}_{dvalue}{dunit}'
                    data['identifier'] = identifier
                    yield identifier, template.render(**data)
            else:
                identifier = f'medication_{data["name"]}'
                data['identifier'] = identifier
                yield identifier, template.render(**data)
