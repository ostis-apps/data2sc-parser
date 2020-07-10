from factory.LoaderFactory import LoaderFactory
from translators.JsonToScsTranslator import json_to_scs

import argparse
import os


def parse(entities, save_dir='sc_out', lang='en', loader='wiki', with_context=False, debug=False):
    print('Starting...')
    loader = LoaderFactory().create_loader(loader, with_context)

    print('Loading data from external source...')
    try:
        loader.getEntities(entities, lang=lang)
    except Exception:
        print("Can't load data. Try another loader")
    else:
        print('Data loaded')

        if debug:
            try:
                os.mkdir(save_dir)
            except FileExistsError:
                pass
            os.chdir(save_dir)
            print('Saving intermediate JSON file...')
            f = open("debug.json", "wt")
            f.write(loader.getJson())
            f.close()
            print('Saved')
            os.chdir('..')

        print('Translating data to scs...')
        json_to_scs(loader.getJson(), save_dir)
        print('Data translated')
        print('Finished')


def args_parser_init():
    parser = argparse.ArgumentParser(
        description='Loader from external sources')
    parser.add_argument('entities', metavar='ENT', type=str,
                        nargs='+', help="Searched entities")
    parser.add_argument(
        "--lang", choices=["en", "de", "ru"], default='en', type=str, help="Language of titles")
    parser.add_argument('--dir', default='sc_out', type=str,
                        help='Enter directory to save scs files')
    parser.add_argument("--source", choices=["wiki", "google"],
                        default="wiki", type=str, help="Select external source")
    parser.add_argument("--context", choices=["yes", "no"], default='no',
                        type=str, help="Get entity with context (works only with Wiki)")
    parser.add_argument(
        "--debug", choices=['yes', 'no'], default='no', type=str, help='If True, also saves json file')
    return parser


def word2bool(word):
    if word == 'yes':
        return True
    else:
        return False


if __name__ == "__main__":
    parser = args_parser_init()

    args = parser.parse_args()

    parse(args.entities, args.dir, args.lang, args.source,
          word2bool(args.context), word2bool(args.debug))
