from .WikiDataLoader import WikiDataLoader
import wptools


class WikiDataWithContextLoader(WikiDataLoader):
    def getEntity(self, entity, lang='en'):
        super().getEntity(entity, lang=lang)
        self._page = wptools.page(wikibase=self._page.data['wikibase'], lang='en', skip=[
                                  'labels', 'imageinfo'], silent=True)
        self._page.get_wikidata()
        context = self._page.data['claims']
        for rlt, ents in context.items():
            rlt_page = wptools.page(
                wikibase=rlt, skip=['labels', 'imageinfo'], silent=True)
            rlt_page.get_wikidata()
            rlt_de_page = wptools.page(wikibase=rlt, lang='de', skip=[
                                       'labels', 'imageinfo'], silent=True)
            rlt_de_page.get_wikidata()
            rlt_ru_page = wptools.page(wikibase=rlt, lang='ru', skip=[
                                       'labels', 'imageinfo'], silent=True)
            rlt_ru_page.get_wikidata()
            rlt_id = rlt_page.data['title']

            self._info['relations'][rlt_id] = {
                'identifier': rlt_id,
                'label': {'en': rlt_page.data['label'], 'de': rlt_de_page.data['label'], 'ru': rlt_ru_page.data['label']},
                'description': {'en': rlt_page.data['description'], 'de': rlt_de_page.data['description'], 'ru': rlt_ru_page.data['description']}
            }

            for ent in ents:
                if type(ent) is str:
                    if ent.startswith('Q'):
                        ent_page = wptools.page(
                            wikibase=ent, skip=['labels'], silent=True)
                        ent_page.get_wikidata()
                        ent_de_page = wptools.page(wikibase=ent, lang='de', skip=[
                                                   'labels', 'imageinfo'], silent=True)
                        ent_de_page.get_wikidata()
                        ent_ru_page = wptools.page(wikibase=ent, lang='ru', skip=[
                                                   'labels', 'imageinfo'], silent=True)
                        ent_ru_page.get_wikidata()
                        try:
                            ent_id = ent_page.data['title']
                        except KeyError:
                            continue

                        self._info['entities'][ent_id] = {
                            'identifier': ent_id,
                            'label': {'en': ent_page.data['label'], 'de': ent_de_page.data['label'], 'ru': ent_ru_page.data['label']},
                            'description': {'en': ent_page.data['description'], 'de': ent_de_page.data['description'], 'ru': ent_ru_page.data['description']}
                        }

                        self.add_image_url(ent_page, 'entities', ent_id)

                        self._info['triplets'].append(
                            [self._page.data['title'], rlt_id, ent_id])
