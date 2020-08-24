from airtable import Airtable
from exceptions import UserNotFound
import os

BASE_ID = 'apphvG4aTncmmmVPv'
API_KEY = 'keym557M67PXieeCa'
REQUESTS_TABLE_NAME = 'Requests'
USERS_TABLE_NAME = 'Users'


def get_user_by_id_in_media(media, user_id):
    users_table = Airtable(BASE_ID, USERS_TABLE_NAME, api_key=API_KEY)
    user = users_table.match(media.name.lower() + '_id', user_id)
    if not user:
        raise UserNotFound
    return user


def get_user_by_password(password):
    users_table = Airtable(BASE_ID, USERS_TABLE_NAME, api_key=API_KEY)
    user = users_table.match('password', password)
    if not user:
        raise UserNotFound
    return user


def update_user(record):
    table = Airtable(BASE_ID, USERS_TABLE_NAME, api_key=API_KEY)
    user_elem = table.update(record['id'], record['fields'])
    return user_elem


def get_request_by_id(request_id):
    table = Airtable(BASE_ID, REQUESTS_TABLE_NAME, api_key=API_KEY)
    request_elem = table.match('id', request_id)
    return request_elem


def get_request_by_base_id(request_base_id):
    table = Airtable(BASE_ID, REQUESTS_TABLE_NAME, api_key=API_KEY)
    request_elem = table.get(request_base_id)
    return request_elem


def new_request(name, creator_record_id):
    cur_dir = os.getcwd()
    table = Airtable(BASE_ID, REQUESTS_TABLE_NAME, api_key=API_KEY)
    print(creator_record_id, type(creator_record_id))
    creator = list()
    creator.append(creator_record_id)
    record = {'creator': creator, 'name': name, 'published_by': creator}
    res_record = table.insert(record)
    del res_record['fields']['id']
    table.update(record_id=res_record['id'], fields={'creator': creator})
    return res_record


def delete_request(request_id):
    table = Airtable(BASE_ID, REQUESTS_TABLE_NAME, api_key=API_KEY)
    table.delete(request_id)
