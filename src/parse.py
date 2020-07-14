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
            f = open("debug.json", "wt", encoding="utf-8")
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
        description='Module for parsing external sources into SC-code')
    parser.add_argument('entities', metavar='ENT', type=str,
                        nargs='+', help="Searched entities")
    parser.add_argument(
        "--lang", choices=["en", "de", "ru"], default='en', type=str, help="Language of titles")
    parser.add_argument('--dir', default='sc_out', type=str,
                        help='Enter directory to save scs files')
    parser.add_argument("--source", choices=["wiki", "google"],
                        default="wiki", type=str, help="Select external source")
    parser.add_argument("--context", action='store_true',
                        help="Get entity with context (works only with Wiki)")
    parser.add_argument("--debug", action='store_true',
                        help='If True, also saves JSON file')
    return parser


if __name__ == "__main__":
    parser = args_parser_init()

    args = parser.parse_args()

    parse(args.entities, args.dir, args.lang,
          args.source, args.context, args.debug)
