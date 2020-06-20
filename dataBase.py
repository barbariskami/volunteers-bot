from airtable import Airtable

tasks_table = Airtable('apphvG4aTncmmmVPv', 'Tasks', api_key='keym557M67PXieeCa')


def get_user_by_password(password):
    users_table = Airtable('apphvG4aTncmmmVPv', 'Users', api_key='keym557M67PXieeCa')
    print(users_table.get_all())
    res = users_table.match('password', password)
    print(res)
    return res


def register(password, vk_user_id):
    users_table = Airtable('apphvG4aTncmmmVPv', 'Users', api_key='keym557M67PXieeCa')
    user = users_table.match('password', password)
    if not user:
        print('PasswordDoesNotExist')
    if 'vk_user_id' in user['fields'].keys() and user['fields']['vk_user_id']:
        print('UserIsAlreadyRegistered')
    users_table.update_by_field('password', password, {'vk_user_id': vk_user_id, 'page': 'start'})


def get_page(vk_user_id):
    users_table = Airtable('apphvG4aTncmmmVPv', 'Users', api_key='keym557M67PXieeCa')
    user = users_table.match('vk_user_id', vk_user_id)
    if not user:
        return 'no_register'
    else:
        return user['fields']['page']


def add_task(creator_id, text, period, duration, if_one_time=True, people_number=1):
    pass
