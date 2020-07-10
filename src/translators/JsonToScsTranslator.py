import json
import requests
import re
import os


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

    for ent in info['entities'].values():
        try:
            translate_entity(ent)
        except Exception:
            continue

    for rlt in info['relations'].values():
        try:
            translate_relation(rlt)
        except Exception:
            continue

    for triplet in info['triplets']:
        scs = open('triplets.scs', 'at', encoding='utf-8')
        scs.write('{} => {}: {};;\n'.format(
            triplet[0], triplet[1], triplet[2]))
        scs.close()


def translate_entity(ent):
    scs = open('{}.scs'.format(ent['identifier']), 'wt', encoding='utf-8')
    scs.write(ent['identifier']+'\n')
    scs.write('=> nrel_main_idtf:\n')
    for lang, label in ent['label'].items():
        scs.write('\t[{}] (* <- lang_{};; *);\n'.format(label, lang))
    scs.write(
        '<- rrel_key_sc_element: ...\n(*\n\t<- sc_definition;;\n\t<= nrel_sc_text_translation:')
    for lang, description in ent['description'].items():
        scs.write(
            '\n\t\t... (* -> rrel_example: [{}] (* <-lang_{};; *);; *);'.format(description, lang))
    scs.write(';\n*);\n')

    try:
        image_url = ent['image_url']
        image_format = re.findall(r'\.\w*$', image_url)[0]
        image_format = image_format[1:]
        image = requests.get(image_url)
        os.chdir('images')
        image_file = open('{}_image.{}'.format(
            ent['identifier'], image_format), 'wb')
        image_file.write(image.content)
        image_file.close()
        os.chdir('..')
        scs.write(
            '<- rrel_key_sc_element: ...\n(*\n\t<-sc_illustration;;\n\t<=nrel_sc_text_translation: ...\n')
        scs.write('\t(*\n\t\t-> rrel_example: "file://images/{}_image.{}"'.format(
            ent['identifier'], image_format))
        scs.write(
            ' (* => nrel_format: format_{};; *);;\n\t*);;\n*);\n'.format(image_format))
    except KeyError:
        pass

    scs.write('<-sc_node_not_relation;;')
    scs.close()


def translate_relation(rlt):
    scs = open('{}.scs'.format(rlt['identifier']), 'wt', encoding='utf-8')
    scs.write(rlt['identifier']+'\n')
    scs.write('=> nrel_main_idtf:\n')
    for lang, label in rlt['label'].items():
        scs.write('\t[{}] (* <- lang_{};; *);\n'.format(label, lang))
    scs.write(
        '<- rrel_key_sc_element: ...\n(*\n\t<- sc_definition;;\n\t<= nrel_sc_text_translation:')
    for lang, description in rlt['description'].items():
        scs.write(
            '\n\t\t... (* -> rrel_example: [{}] (* <-lang_{};; *);; *);'.format(description, lang))
    scs.write(';\n*);\n')
    scs.write('<-sc_node_norole_relation;;')
    scs.close()
