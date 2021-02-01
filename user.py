import dataBase
from enumerates import Media, States, Languages, HashTags, Bots
from exceptions import AlreadyRegistered
from extensions import tag_into_text
from copy import deepcopy
import request
import json


class User:
    """
    Класс представляет собой объект пользователя. В экземпляре класса хранятся все данные о пользователе, которые
    содержатся в базе данных или данные, которые еше не занесены в базу, но будут помещены туда (формат данных должен
    совпадать с форматом airtable)
    """

    def __init__(self, media=None, user_id=None, record=None, base_id=None):
        if record:
            # If there is a record given, we use it
            user_elem = record
        elif base_id:
            user_elem = dataBase.get_user_by_base_id(base_id)
        else:
            # Otherwise load the data from the base
            user_elem = dataBase.get_user_by_id_in_media(media, user_id)

        # all the fields from airtable-base turn into class object's fields
        self.__dict__ = self.__class__.transform_from_record_into_variable_dict(user_elem)

        # Adding some other important fields, which were not mentioned in database or changing format
        self.user_elem = user_elem
        self.base_id = user_elem['id']

        self.REQUEST_COLUMNS_CONNECTION = {'published_by': 'moderated_requests',
                                           'no_reply': 'not_seen_requests',
                                           'refused_by': 'refused_requests',
                                           'taken_by': 'taken_requests',
                                           'creator': 'created_requests'}

        self.FEATURES_FOR_CONTACTS = {
            'not_stated': {
                'RU': 'не указано',
                'EN': 'not stated'
            },
            'phone_number': {
                'RU': 'Номер телефона: ',
                'EN': 'Phone number: '
            },
            'link':
                {'TELEGRAM':
                    {
                        'RU': '[Telegram-сылка](tg://user?id={user_id})',
                        'EN': '[Telegram-link](tg://user?id={user_id}})'
                    }
                },
            'email': {
                'RU': 'Почта: ',
                'EN': 'Email: '
            }
        }

    @staticmethod
    def transform_from_record_into_variable_dict(record):
        res_dict = deepcopy(record['fields'])
        res_dict['media_id'] = dict()
        res_dict['state'] = dict()
        res_dict['creation_state'] = dict()
        res_dict['moderation_state'] = dict()
        res_dict['language'] = dict()
        res_dict['edited_drafts'] = dict()
        res_dict['messages_for_requests'] = dict()
        res_dict['link'] = dict()
        for bot in Bots:
            res_dict['messages_for_requests'][bot] = dict()

        for media in Media:
            res_dict['media_id'][media] = record['fields'].get(media.name.lower() + '_id', None)
            res_dict['state'][media] = States[record['fields'].get(media.name.lower() + '_state', 'MAIN_MENU')]
            res_dict['creation_state'][media] = States[
                record['fields'].get(media.name.lower() + '_creation_state', 'CREATION_MAIN_MENU')]
            res_dict['moderation_state'][media] = States[
                record['fields'].get(media.name.lower() + '_moderation_state', 'MODERATION_MAIN_MENU')]
            res_dict['language'][media] = Languages[record['fields'].get(media.name.lower() + '_language', 'RU')]
            res_dict['edited_drafts'][media] = record['fields'].get(media.name.lower() + '_creation_edited_draft', None)
            res_dict['link'][media] = record['fields'].get(media.name.lower() + '_link', None)
            for bot in Bots:
                if media.name.lower() + '_' + bot.name.lower() + '_messages_for_requests' in record['fields'].keys():
                    res_dict['messages_for_requests'][bot][media] = json.loads(
                        record['fields'][media.name.lower() + '_' + bot.name.lower() + '_messages_for_requests'])
                else:
                    res_dict['messages_for_requests'][bot][media] = dict()
        if 'is_moderator' not in res_dict.keys():
            res_dict['is_moderator'] = False
        res_dict['ignored_tags'] = list()
        for tag in record['fields'].get('ignored_tags', tuple()):
            res_dict['ignored_tags'].append(HashTags[tag])

        # Deletion of needless (or inconvenient) fields
        del res_dict['id']
        for media in Media:
            if media.name.lower() + '_id' in res_dict.keys():
                del res_dict[media.name.lower() + '_id']
            if media.name.lower() + '_state' in res_dict.keys():
                del res_dict[media.name.lower() + '_state']
            if media.name.lower() + '_language' in res_dict.keys():
                del res_dict[media.name.lower() + '_language']
            if media.name.lower() + '_creation_state' in res_dict.keys():
                del res_dict[media.name.lower() + '_creation_state']
            if media.name.lower() + '_moderation_state' in res_dict.keys():
                del res_dict[media.name.lower() + '_moderation_state']
            if media.name.lower() + '_creation_edited_draft' in res_dict.keys():
                del res_dict[media.name.lower() + '_creation_edited_draft']
            if media.name.lower() + '_link' in res_dict.keys():
                del res_dict[media.name.lower() + '_link']

        return res_dict

    def transform_into_record(self):
        # Creates an airtable record from an object and returns it
        record = {'id': self.base_id}
        fields = deepcopy(self.__dict__)
        keys = list(fields.keys())
        for key in keys:
            if key == 'user_elem' or key == 'base_id' or fields[key] is None:
                del fields[key]
            elif key == 'media_id':
                del fields[key]
                for media in self.media_id.keys():
                    if not self.media_id[media] is None:
                        fields[media.name.lower() + '_id'] = self.media_id[media]
            elif key == 'state':
                del fields[key]
                for media in self.state.keys():
                    if self.state[media]:
                        fields[media.name.lower() + '_state'] = self.state[media].name
            elif key == 'creation_state':
                del fields[key]
                for media in self.creation_state.keys():
                    if self.creation_state[media]:
                        fields[media.name.lower() + '_creation_state'] = self.creation_state[media].name
            elif key == 'moderation_state':
                del fields[key]
                for media in self.moderation_state.keys():
                    if self.moderation_state[media]:
                        fields[media.name.lower() + '_moderation_state'] = self.moderation_state[media].name
            elif key == 'language':
                del fields[key]
                for media in self.state.keys():
                    if not self.state[media] is None:
                        fields[media.name.lower() + '_language'] = self.language[media].name
            elif key == 'edited_drafts':
                del fields[key]
                for media in self.edited_drafts.keys():
                    if self.edited_drafts[media]:
                        fields[media.name.lower() + '_creation_edited_draft'] = self.edited_drafts[media]
            elif key == 'ignored_tags':
                fields['ignored_tags'] = list(map(lambda x: x.name, fields['ignored_tags']))
            elif key == 'REQUEST_COLUMNS_CONNECTION':
                del fields[key]
            elif key == 'messages_for_requests':
                del fields[key]
                for bot in self.messages_for_requests:
                    for media in self.messages_for_requests[bot]:
                        fields[media.name.lower() + '_' + bot.name.lower() + '_messages_for_requests'] = json.dumps(
                            self.messages_for_requests[bot][media])
            elif key == 'link':
                del fields[key]
                for media in self.link.keys():
                    if self.link[media]:
                        fields[media.name.lower() + '_link'] = self.link[media]
            elif key == 'FEATURES_FOR_CONTACTS':
                del fields[key]
        record['fields'] = fields
        return record

    def update_from_server(self):
        # download the data from server
        record = dataBase.get_user_by_base_id(self.base_id)
        new_var_dict = self.__class__.transform_from_record_into_variable_dict(record)
        for key in new_var_dict.keys():
            self.__dict__[key] = new_var_dict[key]

    def update_on_server(self):
        # uploads the data on server
        record = self.transform_into_record()
        self.user_elem = dataBase.update_user_on_server(record)

    def get_state(self, media, creation=False):
        self.update_from_server()
        if creation:
            state = self.creation_state[media]
        else:
            state = self.state[media]
        return state

    def set_state(self, media, state, creation=False, moderation=False):
        # changes the state parameter and loads the changes on a server
        self.update_from_server()
        if creation:
            self.creation_state[media] = state
        elif moderation:
            self.moderation_state[media] = state
        else:
            self.state[media] = state
        self.update_on_server()

    def set_link(self, media, link):
        self.update_from_server()
        self.link[media] = link
        self.update_on_server()

    def set_language(self, media, language):
        self.update_from_server()
        self.language[media] = language
        self.update_on_server()

    def get_ignored_hashtags_text(self, media):
        self.update_from_server()
        ignored = self.ignored_tags
        return tag_into_text(ignored, self.language[media])

    def get_subscription_hashtags_text(self, media):
        self.update_from_server()
        all_tags = list(HashTags)
        ignored = self.ignored_tags
        for tag in ignored:
            index = all_tags.index(tag)
            if index >= 0:
                del all_tags[index]
        return tag_into_text(all_tags, self.language[media])

    def subscription_hashtags(self):
        self.update_from_server()
        all_tags = list(HashTags)
        ignored = self.ignored_tags
        for tag in ignored:
            index = all_tags.index(tag)
            if index >= 0:
                del all_tags[index]
        return all_tags

    def delete_tag_from_ignore(self, tag):
        self.update_from_server()
        index = self.ignored_tags.index(tag)
        if index >= 0:
            del self.ignored_tags[index]
        self.update_on_server()

    def add_tag_into_ignore(self, tag):
        self.update_from_server()
        if tag not in self.ignored_tags:
            self.ignored_tags.append(tag)
        self.update_on_server()

    def set_edited_draft(self, media, draft_id):
        self.update_from_server()
        self.edited_drafts[media] = draft_id
        self.update_on_server()

    def get_edited_draft(self, media):
        self.update_from_server()
        draft = request.Request(request_id=self.edited_drafts[media])
        return draft

    def connect_request(self, request):
        self.update_from_server()

    def clear_edited_draft_field(self, media):
        self.edited_drafts[media] = None
        self.update_on_server()

    def delete_created_request(self, request_id):
        self.update_from_server()

    def add_message_id(self, media, bot, message_id, request_id):
        self.update_from_server()
        self.messages_for_requests[bot][media][request_id] = message_id
        self.update_on_server()

    @staticmethod
    def get_id_of_all_moderators(media):
        res_list = dataBase.get_id_of_all_moderators(media)
        return res_list

    @staticmethod
    def get_id_of_users_without_ignore_hashtags(media, tags):
        res_list = dataBase.get_id_of_users_without_ignore_hashtags(media, tags)
        return res_list

    def get_message_id_by_request_id(self, media, bot, request_base_id):
        self.update_from_server()
        message_id = self.messages_for_requests[bot][media].get(request_base_id, 0)
        return message_id

    def decline_request(self, request_to_decline):
        self.update_from_server()
        self.refused_requests = self.__dict__.get('refused_requests', list())
        self.refused_requests.append(request_to_decline.base_id)
        self.update_on_server()

    def take_request(self, request_to_take):
        self.update_from_server()
        self.taken_requests = self.__dict__.get('taken_requests', list())
        self.taken_requests.append(request_to_take.base_id)
        self.update_on_server()

    def get_contact_card(self, media):
        lines = list()
        lines.append(self.name_surname)
        link_line = self.FEATURES_FOR_CONTACTS['link'][media.name][self.language[media].name].format(
            user_id=str(self.media_id[media]))
        lines.append(link_line)
        email_line = self.FEATURES_FOR_CONTACTS['email'][self.language[media].name]
        email_line += self.__dict__.get('email', self.FEATURES_FOR_CONTACTS['not_stated'][self.language[media].name])
        lines.append(email_line)
        phone_line = self.FEATURES_FOR_CONTACTS['phone_number'][self.language[media].name]
        phone_line += self.__dict__.get('phone_number',
                                        self.FEATURES_FOR_CONTACTS['not_stated'][self.language[media].name])
        lines.append(phone_line)

        text = '\n'.join(lines)

        if media == Media.TELEGRAM:
            self.replace = text.replace('_', '\_')
            text = self.replace
        return text

    @staticmethod
    def get_ids_of_messages_to_delete_for_enough_executors(request, bot, media):
        res = dict()
        all_users_records = dataBase.get_all_users()
        for user_record in all_users_records:
            user = User(record=user_record)
            try:
                message_id = user.messages_for_requests[bot][media].get(request.base_id, 0)
                if (not request.user_is_executor(user)) and user.media_id[media] and message_id:
                    res[user.media_id[media]] = message_id
            except AttributeError or KeyError:
                pass
        return res

    @staticmethod
    def register(media, user_id, password, user_contact_link):
        """
        This static method is used to register a new user using a unique password given to them by student development
        department (or any other people that regulate the usage of this service). It loads all the information about the
        user from the password and add his media-id to an airtable base.
        :param user_contact_link:
        :param media:
        :param user_id:
        :param password:
        :return:
        """
        user = User(record=dataBase.get_user_by_password(password))
        if user.media_id.get(media, None):
            raise AlreadyRegistered
        user.media_id[media] = user_id
        user.update_on_server()
        user.set_link(media, user_contact_link)
