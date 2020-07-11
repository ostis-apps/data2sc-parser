from loaders.GoogleSearchLoader import GoogleSearchLoader
from loaders.WikiDataLoader import WikiDataLoader
from loaders.WikiDataWithContextLoader import WikiDataWithContextLoader


class LoaderFactory():
    def create_loader(self, name, with_context):
        if name == 'google':
            return GoogleSearchLoader()
        elif name == 'wiki':
            if with_context:
                return WikiDataWithContextLoader()
            else:
                return WikiDataLoader()
        else:
            raise Exception('No such type of loader: "{}"'.format(name))
