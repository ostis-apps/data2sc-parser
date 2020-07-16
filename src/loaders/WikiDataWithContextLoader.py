from .WikiDataLoader import WikiDataLoader
import wptools
import re
import threading
from queue import Queue


class WikiDataWithContextLoader(WikiDataLoader):
    def __init__(self):
        super().__init__()
        self._lock = threading.Lock()
        self._THREADS_NUM = 16

    def load_object(self, obj, obj_type):
        page = wptools.page(wikibase=obj, skip=['labels'], silent=True)
        de_page = wptools.page(wikibase=obj, lang='de', skip=[
                               'labels', 'imageinfo'], silent=True)
        ru_page = wptools.page(wikibase=obj, lang='ru', skip=[
                               'labels', 'imageinfo'], silent=True)

        page.get_wikidata()
        de_page.get_wikidata()
        ru_page.get_wikidata()

        try:
            obj_id = re.sub(r"\+|-|–|\/|:|\s", '_',
                            re.sub(r"'s?|\(|\)|,", '', page.data['title']))
        except KeyError:
            obj_id = obj

        with self._lock:
            self._info[obj_type][obj] = {
                'identifier': obj_id,
                'label': {'en': page.data['label'], 'de': de_page.data['label'], 'ru': ru_page.data['label']},
                'description': {'en': page.data['description'], 'de': de_page.data['description'], 'ru': ru_page.data['description']}
            }
            self.add_image_url(page, obj_type, obj)

    def thread_fun(self, queue):
        while True:
            obj, obj_type = queue.get()
            self.load_object(obj, obj_type)
            queue.task_done()

    def resolve_ids(self):
        for triplet in self._info['triplets']:
            _, rlt, ent = triplet
            triplet[1] = self._info['relations'][rlt]['identifier']
            triplet[2] = self._info['entities'][ent]['identifier']

        temp_ent = self._info['entities']
        self._info['entities'] = {}
        for ent in temp_ent:
            self._info['entities'][temp_ent[ent]['identifier']] = temp_ent[ent]

        temp_rlt = self._info['relations']
        self._info['relations'] = {}
        for rlt in temp_rlt:
            self._info['relations'][temp_rlt[rlt]
                                    ['identifier']] = temp_rlt[rlt]

    def getEntity(self, entity, lang='en'):
        super().getEntity(entity, lang=lang)
        self._page = wptools.page(wikibase=self._page.data['wikibase'], lang='en', skip=[
                                  'labels', 'imageinfo'], silent=True)
        self._page.get_wikidata()
        page_title = re.sub(r"\+|-|–|\/|:|\s", '_',
                            re.sub(r"'s?|\(|\)|,", '', self._page.data['title']))
        loading_queue = Queue()

        for _ in range(self._THREADS_NUM):
            threading.Thread(target=self.thread_fun, args=[
                             loading_queue, ], daemon=True).start()

        context = self._page.data['claims']
        for rlt, ents in context.items():
            loading_queue.put([rlt, 'relations'])
            for ent in ents:
                if type(ent) is str:
                    if ent.startswith('Q'):
                        loading_queue.put([ent, 'entities'])
                        self._info['triplets'].append([page_title, rlt, ent])

        loading_queue.join()
        self.resolve_ids()
