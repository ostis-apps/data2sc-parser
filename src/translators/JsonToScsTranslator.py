import json
import requests
import re
import os
from jinja2 import Environment, FileSystemLoader


def json_to_scs(raw_info, save_dir):
    try:
        os.mkdir(save_dir)
    except FileExistsError:
        pass
    os.chdir(save_dir)
    try:
        os.mkdir('images')
    except FileExistsError:
        pass

    info = json.loads(raw_info)
    jinja_env = Environment(loader=FileSystemLoader(os.path.realpath(
        '{}/../templates'.format(os.path.dirname(os.path.realpath(__file__))))))

    template = jinja_env.get_template('entity.scs')
    for ent in info['entities'].values():
        translate_entity(ent, template)

    template = jinja_env.get_template('relation.scs')
    for rlt in info['relations'].values():
        translate_relation(rlt, template)

    template = jinja_env.get_template('triplets.scs')
    if len(info['triplets']) != 0:
        scs = open('triplets.scs', 'at', encoding='utf-8')
        scs.write(template.render(triplets=info['triplets']))
        scs.close()


def translate_entity(entity, template):
    if 'image_url' in entity:
        image_url = entity['image_url']
        image_format = re.findall(r'\.\w*$', image_url)[0][1:]
        image_name = '{}_image.{}'.format(entity['identifier'], image_format)
        image = requests.get(image_url)
        os.chdir('images')
        image_file = open('{}_image.{}'.format(
            entity['identifier'], image_format), 'wb')
        image_file.write(image.content)
        image_file.close()
        os.chdir('..')

        rendered_tmpl = template.render(identifier=entity['identifier'], labels=entity['label'].items(
        ), descriptions=entity['description'].items(), img_name=image_name, img_format=image_format)
    else:
        rendered_tmpl = template.render(identifier=entity['identifier'], labels=entity['label'].items(
        ), descriptions=entity['description'].items())

    scs = open('{}.scs'.format(entity['identifier']), 'wt', encoding='utf-8')
    scs.write(rendered_tmpl)
    scs.close()


def translate_relation(relation, template):
    scs = open('{}.scs'.format(relation['identifier']), 'wt', encoding='utf-8')
    scs.write(template.render(identifier=relation['identifier'], labels=relation['label'].items(
    ), descriptions=relation['description'].items()))
    scs.close()
