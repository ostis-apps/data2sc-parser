from .BaseLoader import BaseLoader
import urllib
import requests
from bs4 import BeautifulSoup


class GoogleSearchLoader(BaseLoader):
    # desktop user-agent
    _USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0"
    # mobile user-agent
    _MOBILE_USER_AGENT = "Mozilla/5.0 (Linux; Android 7.0; SM-G930V Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.125 Mobile Safari/537.36"
    # google search URL
    _URL = 'https://google.com/search?q={}'

    def getEntity(self, entity, lang='en'):
        query = self.check_lang(lang, entity)

        query = query.replace(' ', '+')

        headers = {"user-agent": self._USER_AGENT}
        resp = requests.get(self._URL.format(query), headers=headers)

        if resp.status_code == 200:
            soup = BeautifulSoup(resp.content, "html.parser")
            results = self.scrape_page(soup)
            self.make_json(entity, lang, results)

    def check_lang(self, lang, entity):
        if lang == 'en':
            query = 'definition of a word "{}"'.format(entity)
        elif lang == 'de':
            query = 'Definition eines Wortes "{}"'.format(entity)
        elif lang == 'ru':
            query = 'определение слова "{}"'.format(entity)
        return query

    def make_json(self, entity, lang, results):
        try:
            self._info['entities'][entity.lower().replace(' ', '_')] = {
                'identifier': entity.lower().replace(' ', '_'),
                'label': {lang: entity},
                'description': {lang: results[0]['definition']}
            }
        except IndexError:
            raise Exception('No definition')

    def scrape_page(self, soup):
        results = []
        for vmod in soup.find_all('div', class_='vmod', jsname='r5Nvmf'):
            part_of_speech = vmod.find(
                'div', class_='lW8rQd').find('span').text
            definition = vmod.find(
                'div', class_='QIclbb XpoqFe').find('span').text
            results.append({
                'part_of_speech': part_of_speech,
                'definition': definition
            })
        return results
