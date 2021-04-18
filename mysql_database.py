import traceback
from sqlalchemy import create_engine, or_
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm.session import sessionmaker
from enumerates import Media
from exceptions import UserNotFound


class DBAlchemyConnector:
    ITEMS_NOT_TO_CHANGE = (
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

        Session_class = sessionmaker(bind=self.engine)
        self.session = Session_class()

    def get_user_by_id_in_media(self, media, user_id):
        field_name = media.name.lower() + '_id'
        user_data = self.session.query(self.users).filter_by(**{field_name: user_id}).first()
        if not user_data:
            raise UserNotFound
        final_res = self.get_user_by_base_id(base_id=user_data.id, data_from_users_table=user_data)
        return final_res

    def get_user_by_base_id(self,
                            base_id,
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
            if k in self.ITEMS_NOT_TO_CHANGE:
                final_res['fields'][k] = data_from_users_table.__dict__[k]
            elif k == 'is_moderator':
                final_res['fields'][k] = bool(data_from_users_table.__dict__[k])
            elif k == 'telegram_main_messages_for_requests' or k == 'telegram_moderation_messages_for_requests' or k == 'telegram_creation_messages_for_requests':
                final_res['fields'][k] = str(data_from_users_table.__dict__[k])
            elif k == 'ignored_tags':
                final_res['fields'][k] = list(data_from_users_table.__dict__[k])

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

        if not data_from_taken_requests_table:
            data_from_taken_requests_table = self.session.query(self.taken_requests).filter_by(user_id=base_id).all()
        final_res['fields']['taken_requests'] = [i.id for i in data_from_taken_requests_table]

        if not data_from_refused_requests_table:
            data_from_refused_requests_table = self.session.query(self.refused_requests).filter_by(user_id=base_id).all()
        final_res['fields']['refused_requests'] = [i.id for i in data_from_refused_requests_table]
        return final_res

#     def add_user(self, properties):
#         new_user = self.users(**properties)
#         self.session.add(new_user)
#         self.session.commit()
#
#     def select_users_as_lists(self):
#         users = self.session.query(self.users).all()
#         users = [u.__dict__ for u in users]
#         return users
#
#
# connector = DBAlchemyConnector(host='localhost',
#                                user='letovo_helper_admin',
#                                password='PomozhemVsemDa',
#                                database='letovo_helper')
#
# connector.get_user_by_id_in_media(Media.TELEGRAM, user_id=282381990)
# print(connector.get_user_by_base_id(1083))
