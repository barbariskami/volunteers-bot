from sqlalchemy import create_engine, or_, func, not_, and_
import sqlalchemy.exc as sqlExc
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm.session import sessionmaker
import json
import enumerates
from datetime import datetime
from exceptions import UserNotFound, TagDuplicateValue
import traceback


class DBAlchemyConnector:
    USER_ITEMS_NOT_TO_CHANGE = (
        'id',
        'analytics_id',
        'name',
        'password',
        'passwords_hash',
        'email',
        'telegram_link',
        'telegram_id',
        'telegram_state',
        'telegram_language',
        'telegram_creation_state',
        'telegram_moderation_state',
        'telegram_keyboard'
    )
    REQUEST_ITEMS_NOT_TO_CHANGE = (
        'id',
        'name',
        'text',
        'date_type',
        'people_number'
    )

    def __init__(self, host, user, password, database):
        self.Base = automap_base()
        base_address = 'mysql://{user}:{password}@{host}/{database}'.format(user=user,
                                                                            host=host,
                                                                            password=password,
                                                                            database=database)
        self.engine = create_engine(base_address, echo=True)
        self.Base.prepare(self.engine, reflect=True)

        self.users = self.Base.classes.users
        self.requests = self.Base.classes.requests
        self.taken_requests = self.Base.classes.taken_requests
        self.refused_requests = self.Base.classes.refused_requests
        self.message_for_request = self.Base.classes.message_for_request
        self.tags = self.Base.classes.tags
        self.ignored_tags = self.Base.classes.ignored_tags
        self.request_tags = self.Base.classes.request_tags

        Session_class = sessionmaker(bind=self.engine)
        self.session = Session_class()

    def get_user_by_id_in_media(self, media, user_id):
        field_name = media.name.lower() + '_id'
        user_data = self.session.query(self.users).filter_by(**{field_name: user_id}).first()
        if not user_data:
            raise UserNotFound
        final_res = self.get_user_by_base_id(base_id=user_data.id, data_from_users_table=user_data)
        return final_res

    def get_user_by_base_id(self, base_id,
                            data_from_users_table=None,
                            data_from_requests_table=None,
                            data_from_taken_requests_table=None,
                            data_from_refused_requests_table=None):
        final_res = dict()
        final_res['id'] = base_id
        final_res['fields'] = dict()
        if not data_from_users_table:
            data_from_users_table = self.session.query(self.users).filter_by(id=base_id).first()
        if not data_from_users_table:
            raise UserNotFound
        for k in data_from_users_table.__dict__.keys():
            if k in self.USER_ITEMS_NOT_TO_CHANGE:
                final_res['fields'][k] = data_from_users_table.__dict__[k]
            elif k == 'is_moderator' or k == 'is_admin':
                final_res['fields'][k] = bool(data_from_users_table.__dict__[k])
            # elif k == 'ignored_tags':
            #     final_res['fields'][k] = list(data_from_users_table.__dict__[k])
            elif k == 'telegram_creation_edited_draft':
                final_res['fields'][k] = list()
                final_res['fields'][k].append(data_from_users_table.__dict__[k])

        ignored_tags = self.session.query(self.ignored_tags).filter(self.ignored_tags.user_id == base_id).all()
        tags = [tag.tag for tag in ignored_tags]
        final_res['fields']['ignored_tags'] = tags

        filter_expression = or_(self.requests.creator == base_id, self.requests.published_by == base_id)
        if not data_from_requests_table:
            data_from_requests_table = self.session.query(self.requests).filter(filter_expression).all()
        final_res['fields']['created_requests'] = list()
        final_res['fields']['moderated_requests'] = list()
        for i in data_from_requests_table:
            if i.creator == base_id:
                final_res['fields']['created_requests'].append(i.id)
            if i.published_by == base_id:
                final_res['fields']['moderated_requests'].append(i.id)

        messages_for_requests = self.session.query(self.message_for_request).filter_by(user_id=base_id)
        for media in enumerates.Media:
            for bot in enumerates.Bots:
                filter_expression = and_(self.message_for_request.media == media.name,
                                         self.message_for_request.bot == bot.name)
                messages = messages_for_requests.filter(filter_expression).all()
                field_name = media.name.lower() + '_' + bot.name.lower() + '_messages_for_requests'
                final_res['fields'][field_name] = dict()
                for m in messages:
                    final_res['fields'][field_name][m.request_id] = m.message_id
                final_res['fields'][field_name] = json.dumps(final_res['fields'][field_name])

        if not data_from_taken_requests_table:
            data_from_taken_requests_table = self.session.query(self.taken_requests).filter_by(user_id=base_id).all()
        final_res['fields']['taken_requests'] = [i.id for i in data_from_taken_requests_table]

        if not data_from_refused_requests_table:
            data_from_refused_requests_table = self.session.query(self.refused_requests).filter_by(
                user_id=base_id).all()
        final_res['fields']['refused_requests'] = [i.id for i in data_from_refused_requests_table]
        return final_res

    def get_user_by_password(self, password):
        user_data = self.session.query(self.users).filter_by(password=password).first()
        if not user_data:
            raise UserNotFound
        final_res = self.get_user_by_base_id(base_id=user_data.id, data_from_users_table=user_data)
        return final_res

    def get_user_by_passwords_hash(self, passwords_hash):
        user_data = self.session.query(self.users).filter_by(passwords_hash=passwords_hash).first()
        if not user_data:
            raise UserNotFound
        final_res = self.get_user_by_base_id(base_id=user_data.id, data_from_users_table=user_data)
        return final_res

    def update_user_on_server(self, record):
        user_data = self.session.query(self.users).filter_by(id=record['id']).first()
        if not user_data:
            raise UserNotFound
        for k in record['fields'].keys():
            if k in self.USER_ITEMS_NOT_TO_CHANGE and record['fields'][k]:
                setattr(user_data, k, record['fields'][k])
            elif (k == 'is_moderator' or k == 'is_admin') and record['fields'][k]:
                setattr(user_data, k, int(record['fields'][k]))
            elif (
                    k == 'telegram_main_messages_for_requests' or k == 'telegram_moderation_messages_for_requests' or k == 'telegram_creation_messages_for_requests') and \
                    record['fields'][k]:
                data = json.loads(record['fields'][k])
                media_name, bot_name, *other = k.split('_')
                media_name = media_name.upper()
                bot_name = bot_name.upper()
                filter_expression = and_(self.message_for_request.bot == bot_name,
                                         self.message_for_request.media == media_name,
                                         self.message_for_request.user_id == record['id'])
                messages_for_requests_from_base = self.session.query(self.message_for_request).filter(
                    filter_expression).all()
                messages_for_requests_from_base_pairs = [(i.request_id, i.message_id) for i in
                                                         messages_for_requests_from_base]
                new_data_pairs = [(i, data[i]) for i in data.keys()]
                difference = list(set(new_data_pairs) - set(messages_for_requests_from_base_pairs))
                for i in difference:
                    new_connection = self.message_for_request(id=None, bot=bot_name, media=media_name,
                                                              user_id=record['id'], message_id=i[1], request_id=i[0])
                    self.session.add(new_connection)

            elif k == 'ignored_tags' and record['fields'][k]:
                current_tags = self.session.query(self.ignored_tags).filter_by(user_id=record['id'])
                current_tags_as_strings = set([i.tag for i in current_tags.all()])
                tags_to_add = set(record['fields'][k]) - current_tags_as_strings
                tags_to_delete = current_tags_as_strings - set(record['fields'][k])
                for tag in tags_to_add:
                    new_connection = self.ignored_tags(id=None, tag=tag, user_id=record['id'])
                    self.session.add(new_connection)
                for tag in tags_to_delete:
                    current_tags.filter_by(tag=tag).delete(synchronize_session=False)
                # setattr(user_data, k, set(record['fields'][k]))
            elif k == 'telegram_creation_edited_draft' and record['fields'][k]:
                setattr(user_data, k, record['fields'][k][0])
            elif k == 'taken_requests' or k == 'refused_requests':
                base = None
                if k == 'taken_requests':
                    base = self.taken_requests
                elif k == 'refused_requests':
                    base = self.refused_requests
                requests_from_base = self.session.query(base).filter_by(user_id=record['id']).all()
                requests_from_base_ids = [i.id for i in requests_from_base]
                new_requests = list(set(record['fields'][k]) - set(requests_from_base_ids))
                for r_id in new_requests:
                    new_connection = base(id=None, request_id=r_id, user_id=record['id'])
                    self.session.add(new_connection)
        self.session.commit()

    def update_request(self, record):
        request_data = self.session.query(self.requests).filter_by(id=record['id']).first()
        if not request_data:
            raise UserNotFound
        for k in record['fields'].keys():
            if k in self.REQUEST_ITEMS_NOT_TO_CHANGE and record['fields'][k]:
                setattr(request_data, k, record['fields'][k])
            elif (k == 'creation_time' or k == 'submission_time') and record['fields'][k]:
                setattr(request_data, k, datetime.strptime(record['fields'][k], '%Y-%m-%dT%H:%M:%S.000Z'))
            elif (k == 'was_published' or k == 'was_submited' or k == 'was_executed') and record['fields'][k]:
                setattr(request_data, k, int(record['fields'][k]))
            elif (k == 'creator' or k == 'published_by') and record['fields'][k]:
                setattr(request_data, k, record['fields'][k][0])
            elif (k == 'date1' or k == 'date2') and record['fields'][k]:
                setattr(request_data, k, datetime.strptime(record['fields'][k], '%Y-%m-%d').date())
            elif k == 'tags' and record['fields'][k]:
                current_tags = self.session.query(self.request_tags).filter_by(request_id=record['id'])
                current_tags_list = [i.tag for i in current_tags.all()]
                tags_to_add = set(record['fields'][k]) - set(current_tags_list)
                tags_to_delete = set(current_tags_list) - set(record['fields'][k])

                for t in tags_to_add:
                    new_connection = self.request_tags(id=None, request_id=record['id'], tag=t)
                    self.session.add(new_connection)
                for t in tags_to_delete:
                    current_tags.filter_by(tag=t).delete(synchronize_session=False)
                # setattr(request_data, k, set(record['fields'][k]))
        self.session.commit()

    def get_request_by_id(self, request_id):
        res = self.get_request_by_base_id(request_base_id=request_id)
        return res

    def get_request_by_base_id(self, request_base_id,
                               data_from_requests_table=None,
                               data_from_taken_requests_table=None,
                               data_from_refused_requests_table=None):
        final_res = dict()
        final_res['id'] = request_base_id
        final_res['fields'] = dict()

        if not data_from_requests_table:
            data_from_requests_table = self.session.query(self.requests).filter_by(id=request_base_id).first()
        if not data_from_requests_table:
            raise UserNotFound
        for k in data_from_requests_table.__dict__.keys():
            if data_from_requests_table.__dict__[k]:
                if k in self.REQUEST_ITEMS_NOT_TO_CHANGE:
                    final_res['fields'][k] = data_from_requests_table.__dict__[k]
                elif k == 'creation_time' or k == 'submission_time':
                    final_res['fields'][k] = data_from_requests_table.__dict__[k].strftime('%Y-%m-%dT%H:%M:%S.000Z')
                elif k == 'date1' or k == 'date2':
                    final_res['fields'][k] = data_from_requests_table.__dict__[k].strftime('%Y-%m-%d')
                elif k == 'was_published' or k == 'was_submited' or k == 'was_executed':
                    final_res['fields'][k] = bool(data_from_requests_table.__dict__[k])
                elif k == 'creator' or k == 'published_by':
                    final_res['fields'][k] = list()
                    final_res['fields'][k].append(data_from_requests_table.__dict__[k])
                # elif k == 'tags':
                #     final_res['fields'][k] = list(data_from_requests_table.__dict__[k])

        tags = self.session.query(self.request_tags).filter_by(request_id=request_base_id).all()
        final_res['fields']['tags'] = [i.tag for i in tags]

        if not data_from_taken_requests_table:
            data_from_taken_requests_table = self.session.query(self.taken_requests).filter(
                self.taken_requests.request_id == request_base_id).all()
        final_res['fields']['taken_by'] = [i.id for i in data_from_taken_requests_table]

        if not data_from_refused_requests_table:
            data_from_refused_requests_table = self.session.query(self.refused_requests).filter(
                self.refused_requests.request_id == request_base_id).all()
        final_res['fields']['refused_by'] = [i.id for i in data_from_refused_requests_table]

        return final_res

    def new_request(self, name, creator_record_id):
        now = datetime.today()
        new_request = self.requests(id=None, creator=creator_record_id, name=name, creation_time=now)
        self.session.add(new_request)
        self.session.commit()
        recording = self.get_request_by_id(new_request.id)
        return recording

    def delete_request(self, request_id):
        self.session.query(self.requests).filter_by(id=request_id).delete(synchronize_session=False)
        self.session.commit()

    def get_id_of_all_moderators(self, media):
        moderators = self.session.query(self.users).filter(self.users.is_moderator == 1).all()
        res = list()
        for i in moderators:
            res.append(i.__dict__.get(media.name.lower() + '_id'))
        return res

    def get_id_of_users_without_ignore_hashtags(self, media=enumerates.Media.TELEGRAM, tags=None):
        if tags is None:
            tags = list()
        tags_strings = [i.name for i in tags]
        filter_expression = not_(or_(*[func.find_in_set(s, self.users.ignored_tags) for s in tags_strings]))
        users = self.session.query(self.users).filter(filter_expression).all()
        res = list()
        for i in users:
            res.append(i.__dict__.get(media.name.lower() + '_id'))
        return res

    def get_all_users(self):
        users = self.session.query(self.users).all()
        res = [self.get_user_by_base_id(base_id=i.id, data_from_users_table=i) for i in users]
        return res

    def get_requests_taken_by_user(self, user):
        requests = self.session.query(self.taken_requests).filter_by(user_id=user.id).all()
        ids = list(set([r.request_id for r in requests]))
        res = [self.get_request_by_base_id(i) for i in ids]
        return res

    def get_requests_created_by_user(self, user):
        requests = self.session.query(self.requests).filter_by(creator=user.id).all()
        res = [self.get_request_by_base_id(r.id, data_from_requests_table=r) for r in requests]
        return res

    def get_overdue_requests(self, date):
        expression1 = and_(self.requests.date2, self.requests.date2 < date)
        expression2 = and_(not_(self.requests.date2), self.requests.date1 < date)
        filter_expression = and_(or_(expression1, expression2), self.requests.date1)
        requests = self.session.query(self.requests).filter(filter_expression).all()
        res = [self.get_request_by_base_id(r.id, data_from_requests_table=r) for r in requests]
        return res

    def get_users_who_received_these_requests_main_bot(self, requests_id_list, media):
        bot_name = 'MAIN'
        media_name = media.name.upper()
        filter_expression = and_(self.message_for_request.bot == bot_name,
                                 self.message_for_request.media == media_name,
                                 self.message_for_request.request_id.in_(requests_id_list))
        connections = self.session.query(self.message_for_request).filter(filter_expression).all()
        users_id = set([i.user_id for i in connections])
        users = [self.get_user_by_base_id(i) for i in users_id]
        return users

    def get_tag(self, code):
        tag = self.session.query(self.tags).filter_by(code=code).first()
        if not tag:
            return None
        data_set = {'code': tag.code,
                    'RU': tag.ru,
                    'EN': tag.en,
                    'is_shown': tag.is_shown}
        return data_set

    def get_all_tags(self, only_shown=False):
        tags = self.session.query(self.tags)
        if only_shown:
            tags = tags.filter_by(is_shown=True)
        tags = tags.all()
        res = [{'code': tag.code,
                'RU': tag.ru,
                'EN': tag.en,
                'is_shown': tag.is_shown} for tag in tags]
        return res

    def change_tags_state(self, code):
        tag = self.session.query(self.tags).filter_by(code=code).first()
        tag.is_shown = not tag.is_shown
        self.session.commit()

    def add_tag(self, code, languages):
        try:
            tag = self.tags(code=code, **{l.name.lower(): languages[l] for l in languages.keys()}, is_shown=True)
            self.session.add(tag)
            self.session.commit()
        except sqlExc.IntegrityError:
            raise TagDuplicateValue
        data_set = {'code': tag.code,
                    'RU': tag.ru,
                    'EN': tag.en,
                    'is_shown': tag.is_shown}
        return data_set

    def delete_tag(self, code):
        self.session.query(self.tags).filter_by(code=code).delete(synchronize_session=False)
        self.session.commit()

    def get_all_requests(self):
        requests = self.session.query(self.requests).all()
        res = [self.get_request_by_base_id(request_base_id=i.id, data_from_requests_table=i) for i in requests]
        return res