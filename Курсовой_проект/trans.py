import json
import requests
import re
import os
from jinja2 import Environment, FileSystemLoader


def json_to_scs(raw_info, save_dir,templ):
    try:
        os.mkdir(save_dir)
    except FileExistsError:
        pass
    os.chdir(save_dir)
    #info=[]
    with open(raw_info,'r',encoding='utf-8') as f:
         info=json.load(f)

    jinja_env = Environment(loader=FileSystemLoader(os.path.realpath(templ)))
        #'{}/../templates'.format(os.path.dirname(os.path.realpath(__file__))))))

    try:
        os.mkdir('entities')
    except FileExistsError:
        pass
    os.chdir('entities')
    #try:
    #    os.mkdir('images')
    #except FileExistsError:
    #    pass
    template = jinja_env.get_template('entity_new.scs')
    for ent in info['entities'].values():
        translate_entity(ent, template)
    os.chdir('..')

    #try:
    #    os.mkdir('relations')
    #except FileExistsError:
    #    pass
    #os.chdir('relations')
    #template = jinja_env.get_template('relation.scs')
    #for rlt in info['relations'].values():
    #    translate_relation(rlt, template)
    #os.chdir('..')

    #template = jinja_env.get_template('triplets.scs')
    #if len(info['triplets']) != 0:
    #    scs = open('triplets.scs', 'at', encoding='utf-8')
    #    scs.write(template.render(triplets=info['triplets']))
    #    scs.close()
    #os.chdir('..')


def translate_entity(entity, template):
    rendered_tmpl = template.render(identifier=entity['identifier'], labels=entity['label'].items(),
                                     dsks=entity['dsk'].items(),dens=entity['den'].items(),html_ref=entity['html_ref'])
    scs = open('{}.scs'.format(entity['identifier']), 'wt', encoding='utf-8')
    scs.write(rendered_tmpl)
    
    scs.close()


def translate_relation(relation, template):
    scs = open('{}.scs'.format(relation['identifier']), 'wt', encoding='utf-8')
    #scs.write(template.render(identifier=relation['identifier'], labels=relation['label'].items(), descriptions=relation['descroption'].items()))
    xtempl = template.render(identifier=relation['identifier'], labels=relation['label'].items(), dsks=relation['dsk'].items(), dens=relation['den'].items())
    scs.write(xtempl)
    scs.close()
