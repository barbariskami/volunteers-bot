from airtable import Airtable
from exceptions import UserNotFound
import os

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
