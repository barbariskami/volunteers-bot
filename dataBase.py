from airtable import Airtable
from exceptions import UserNotFound
import enumerates
import logging
import datetime

logging.basicConfig(level=logging.INFO,
                    format=u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s')

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
    logging.info('get_user_by_id_in_media')
    return user


def get_user_by_base_id(base_id):
    users_table = Airtable(BASE_ID, USERS_TABLE_NAME, api_key=API_KEY)
    user = users_table.get(base_id)
    if not user:
        raise UserNotFound
    logging.info('get_user_by_base_id')
    return user


def get_user_by_password(password):
    users_table = Airtable(BASE_ID, USERS_TABLE_NAME, api_key=API_KEY)
    user = users_table.match('password', password)
    if not user:
        raise UserNotFound
    logging.info('get_user_by_password')
    return user


def get_user_by_passwords_hash(passwords_hash):
    users_table = Airtable(BASE_ID, USERS_TABLE_NAME, api_key=API_KEY)
    user = users_table.match(field_name='passwords_hash', field_value=passwords_hash)
    if not user:
        raise UserNotFound
    logging.info('get_user_by_passwords_hash')
    return user


def update_user_on_server(record):
    table = Airtable(BASE_ID, USERS_TABLE_NAME, api_key=API_KEY)
    user_elem = table.update(record['id'], record['fields'])
    logging.info('update_user_on_server')
    return user_elem


def update_request(record):
    table = Airtable(BASE_ID, REQUESTS_TABLE_NAME, api_key=API_KEY)
    request_elem = table.update(record['id'], record['fields'])
    logging.info('update_request')
    return request_elem


def get_request_by_id(request_id):
    table = Airtable(BASE_ID, REQUESTS_TABLE_NAME, api_key=API_KEY)
    request_elem = table.match('id', request_id)
    logging.info('get_request_by_id')
    return request_elem


def get_request_by_base_id(request_base_id):
    table = Airtable(BASE_ID, REQUESTS_TABLE_NAME, api_key=API_KEY)
    request_elem = table.get(request_base_id)
    logging.info('get_request_by_base_id')
    return request_elem


def new_request(name, creator_record_id):
    now = datetime.datetime.today().strftime('%Y-%m-%dT%H:%M:%S.000Z')
    table = Airtable(BASE_ID, REQUESTS_TABLE_NAME, api_key=API_KEY)
    record = {'creator': [creator_record_id], 'name': name, 'creation_time': now}
    res_record = table.insert(record)
    logging.info('new_request')
    return res_record


def delete_request(request_id):
    table = Airtable(BASE_ID, REQUESTS_TABLE_NAME, api_key=API_KEY)
    logging.info('delete_request')
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

    logging.info('get_id_of_all_moderators')
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
    logging.info('get_id_of_users_without_ignore_hashtags')
    return res_list


def get_all_users():
    table = Airtable(BASE_ID, USERS_TABLE_NAME, api_key=API_KEY)
    users_from_table = table.get_all()
    logging.info('get_all_users')
    return users_from_table


def get_requests_taken_by_user(user):
    table = Airtable(BASE_ID, REQUESTS_TABLE_NAME, api_key=API_KEY)
    formula = 'FIND({user_id}, {{taken_by}}, TRUE())'.format(user_id=user.id)
    res = table.get_all(formula=formula)
    logging.info('get_requests_taken_by_user')
    return res


def get_requests_created_by_user(user):
    table = Airtable(BASE_ID, REQUESTS_TABLE_NAME, api_key=API_KEY)
    formula = 'FIND({user_id}, {{creator}}, TRUE())'.format(user_id=user.id)
    res = table.get_all(formula=formula)
    logging.info('get_requests_created_by_user')
    return res


def get_overdue_requests(date):  # date - datetime.date format
    table = Airtable(BASE_ID, REQUESTS_TABLE_NAME, api_key=API_KEY)
    date_string = date.strftime('%d-%m-%Y')
    date_formula_string = 'DATETIME_PARSE("{today}", "DD-MM-YYYY")'.format(today=date_string)
    formula = 'AND(OR(AND(date2, date2<{date_formula}), AND(NOT(date2), date1<{date_formula})), date1)'.format(
        date_formula=date_formula_string)
    res = table.get_all(formula=formula)
    return res


def get_users_who_received_these_requests_main_bot(requests_id_list, media):
    # Метод не дописан, но, вероятно, уже не будет использоваться (написала аналог под mysql)
    # Поэтому пока доделывать не буду
    table = Airtable(BASE_ID, USERS_TABLE_NAME, api_key=API_KEY)
    field_name = media.name.lower() + '_main_messages_for_requests'
    find_string = 'FIND("{request_id}", {field_name})'
    find_strings = [find_string.format(request_id=i, field_name=field_name) for i in requests_id_list]
    formula = 'OR({finds})'.format(finds=', '.join(find_strings))

    users = table.get_all(formula=formula)
    for i in users:
        print(i)
