from airtable import Airtable
from exceptions import UserNotFound

BASE_ID = 'apphvG4aTncmmmVPv'
API_KEY = 'keym557M67PXieeCa'
TASK_TABLE_NAME = 'Tasks'
USERS_TABLE_NAME = 'Users'

tasks_table = Airtable(BASE_ID, TASK_TABLE_NAME, api_key=API_KEY)


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
