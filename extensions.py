from enumerates import Languages
from exceptions import MessageTextNotFoundInFile
import os
import json


def load_text(label, media, language=Languages.RU):
    cwd = os.getcwd().split('/')
    if cwd[-1] == 'telegram_bot':
        os.chdir('/'.join(cwd[:-1]))
    DIRECTIRY_NAME = 'text_labels/'
    file_name = label.name + '.txt'
    text_heading = media.name + '_' + language.name
    full_path = DIRECTIRY_NAME + file_name
    file = open(full_path, mode='r')
    file_text = file.read()
    file.close()
    text = cut_out_message_text(file_text, media, language)
    return text


def cut_out_message_text(file, media, language):
    apologies_text = ''
    try:
        heading = media.name + '_' + language.name
        starting_point = file.find(heading)
        if starting_point < 0:
            raise MessageTextNotFoundInFile
    except MessageTextNotFoundInFile:
        heading = media.name + '_' + Languages.RU.name
        starting_point = file.find(heading)

        apologies_text = load_language_apologies(language)
    split_line_between_texts = '++++++++++++++++\n'
    text = file[starting_point:].split(split_line_between_texts)[0]
    text = apologies_text + '\n' + '\n'.join(text.split('\n')[1:])
    return text


def load_language_apologies(language):
    FILE_PATH = 'text_labels/LANGUAGE_APOLOGIES.TXT'
    file = open(FILE_PATH)
    text = file.read()
    file.close()
    position = text.find(language.name)
    if position < 0:
        raise FileNotFoundError
    text = text[position:].split('\n\n')[0]
    text = '\n'.join(text.split('\n')[1:])
    return text


def load_hashtags_json():
    FILE_PATH = "hashtags.json"
    cwd = os.getcwd().split('/')
    if cwd[-1] == 'telegram_bot':
        os.chdir('/'.join(cwd[:-1]))
    file = open(FILE_PATH)
    data = json.load(file)
    return data


def transform_tags_into_text(tags_list, language):
    tags_json = load_hashtags_json()
    res_list = list()
    for tag in tags_list:
        tag_id = tag.value
        list_copy = list(tags_json['hashtags']).copy()
        list_copy = list(filter(lambda x: x['id'] == tag_id, list_copy))
        tag_translation = list_copy[0][language.name]
        res_list.append(tag_translation)
    return res_list
