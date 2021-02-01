from airtable import Airtable
from exceptions import UserNotFound
import enumerates

BASE_ID = 'apphvG4aTncmmmVPv'
API_KEY_PATH = 'api_key.txt'
API_KEY = open(API_KEY_PATH).read()
REQUESTS_TABLE_NAME = 'Requests'
USERS_TABLE_NAME = 'Users'


def get_user_by_id_in_media(media, user_id):
    users_table = Airtable(BASE_ID, USERS_TABLE_NAME, api_key=API_KEY)
    user = users_table.match(media.name.lower() + '_id', user_id)
    if not user:
        raise UserNotFound
    return user


def get_user_by_base_id(base_id):
    users_table = Airtable(BASE_ID, USERS_TABLE_NAME, api_key=API_KEY)
    user = users_table.get(base_id)
    if not user:
        raise UserNotFound
    return user


def get_user_by_password(password):
    users_table = Airtable(BASE_ID, USERS_TABLE_NAME, api_key=API_KEY)
    user = users_table.match('password', password)
    if not user:
        raise UserNotFound
    return user


def update_user_on_server(record):
    table = Airtable(BASE_ID, USERS_TABLE_NAME, api_key=API_KEY)
    user_elem = table.update(record['id'], record['fields'])
    return user_elem


def update_request(record):
    table = Airtable(BASE_ID, REQUESTS_TABLE_NAME, api_key=API_KEY)
    request_elem = table.update(record['id'], record['fields'])
    return request_elem


def get_request_by_id(request_id):
    table = Airtable(BASE_ID, REQUESTS_TABLE_NAME, api_key=API_KEY)
    request_elem = table.match('id', request_id)
    return request_elem


def get_request_by_base_id(request_base_id):
    table = Airtable(BASE_ID, REQUESTS_TABLE_NAME, api_key=API_KEY)
    request_elem = table.get(request_base_id)
    return request_elem


def new_request(name, creator_record_id):
    table = Airtable(BASE_ID, REQUESTS_TABLE_NAME, api_key=API_KEY)
    record = {'creator': [creator_record_id], 'name': name}
    res_record = table.insert(record)
    return res_record


def delete_request(request_id):
    table = Airtable(BASE_ID, REQUESTS_TABLE_NAME, api_key=API_KEY)
    table.delete(request_id)


def get_id_of_all_moderators(media):
    table = Airtable(BASE_ID, USERS_TABLE_NAME, api_key=API_KEY)
    users_from_table = table.search('is_moderator', '1')
    res_users = list()
    for i in users_from_table:
        try:
            user_id = i['fields'][media.name.lower() + '_id']
            res_users.append(user_id)
        except KeyError:
            pass

    return res_users


def get_id_of_users_without_ignore_hashtags(media=enumerates.Media.TELEGRAM,
                                            tags=None):  # tags = список тэгов в виде объектов enum.HashTags
    if tags is None:
        tags = list()
    tags_strings = [i.name for i in tags]

    if tags:
        find_formula = 'FIND("{tag_name}", {{ignored_tags}}, 0)'
        find_formulas = [find_formula.format(tag_name=i) for i in tags_strings]
        formula = 'IF(OR({find_formulas}), FALSE(), TRUE())'
        final_formula = formula.format(find_formulas=', '.join(find_formulas))
    else:
        final_formula = None

    table = Airtable(BASE_ID, USERS_TABLE_NAME, api_key=API_KEY)
    res_list = list()
    for u in table.get_all(formula=final_formula, fields=media.name.lower() + '_id'):
        if u['fields'].get('telegram_id', None):
            res_list.append(u['fields']['telegram_id'])
    return res_list


def get_all_users():
    table = Airtable(BASE_ID, USERS_TABLE_NAME, api_key=API_KEY)
    users_from_table = table.get_all()
    return users_from_table