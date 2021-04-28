from copy import deepcopy
from enumerates import DateType, Media, TextLabels
import exceptions
from extensions import load_text
from datetime import datetime, date
from traceback import print_exc
import user
import logging
from mysql_database import DBAlchemyConnector
import json
from tag import Tag
import io


class Request:
    INDEXES_FOR_CSV = [
        'id',
        'creation_time',
        'was_published',
        'was_submited',
        'submission_time',
        'was_executed',
        'creator',
        'published_by',
        'name',
        'text',
        'date1',
        'date2',
        'date_type',
        'people_number',
        'taken_by',
        'refused_by',
        'tags'
    ]
    f = open('db_info.json')
    db_connector = DBAlchemyConnector(**json.load(f))

    def __init__(self, request_id=None, request_base_id=None, record=None):
        if request_id:
            record = self.db_connector.get_request_by_id(request_id)
        elif request_base_id:
            record = self.db_connector.get_request_by_base_id(request_base_id)

        self.__dict__ = deepcopy(record['fields'])

        self.request_elem = record
        self.base_id = record['id']
        if 'date_type' in self.__dict__.keys():
            self.date_type = DateType[self.date_type]
        if 'date1' in self.__dict__.keys():
            self.date1 = datetime.strptime(self.date1, '%Y-%m-%d').date()
        else:
            self.date1 = None
        if 'date2' in self.__dict__.keys():
            self.date2 = datetime.strptime(self.date2, '%Y-%m-%d').date()
        else:
            self.date2 = None
        if 'tags' not in self.__dict__.keys() or not self.tags:
            self.tags = list()
        else:
            self.tags = [Tag(code=i) for i in self.tags]
        if 'creation_time' in self.__dict__.keys():
            self.creation_time = datetime.strptime(self.creation_time, '%Y-%m-%dT%H:%M:%S.000Z')
        if 'submission_time' in self.__dict__.keys():
            self.submission_time = datetime.strptime(self.submission_time, '%Y-%m-%dT%H:%M:%S.000Z')

        self.FEATURES_FOR_READABLE_FORMAT = {'creator': {
            'RU': 'Создатель: {creator}',
            'EN': 'Creator: {creator}'
        },
            'people_number': {
                'RU': 'Сколько человек необходимо: {people_number}',
                'EN': 'How many volunteers is needed: {people_number}'
            },
            'tags': {
                'RU': 'Хэш-тэги: {tags}',
                'EN': 'Hashtags: {tags}'
            },
            'date_type': {'DATE': {
                'RU': 'Дата выполнения: {date1}',
                'EN': 'Date: {date1}'
            },
                'DEADLINE': {
                    'RU': 'Крайний срок выполнения: {date1}',
                    'EN': 'Deadline: {date1}'
                },
                'PERIOD': {
                    'RU': 'Период выполнения с {date1} по {date2}',
                    'EN': 'The execution period is from {date1} to {date2}'
                }}
        }
        self.FEATURES_FOR_DRAFT_FORMAT = {
            "not_stated": {
                "RU": "не указано",
                "EN": "not stated"
            },
            "date_type_name": {
                "DATE": {
                    "RU": "Конкретная дата",
                    "EN": "Date"
                },
                "DEADLINE": {
                    "RU": "Дэдлайн",
                    "EN": "Deadline"
                },
                "PERIOD": {
                    "RU": "Период",
                    "EN": "Period"
                }
            }
        }

    def load_from_server(self):
        self.__init__(request_base_id=self.base_id)

    def into_record(self):
        record = {'id': self.base_id}
        fields = deepcopy(self.__dict__)
        keys = list(fields.keys())

        for key in keys:
            if key == 'request_elem' or key == 'base_id' or fields[key] is None:
                del fields[key]
            elif key == 'date_type':
                fields[key] = self.date_type.name
            elif key == 'id' or key == 'FEATURES_FOR_READABLE_FORMAT' or key == 'FEATURES_FOR_DRAFT_FORMAT':
                del fields[key]
            elif (key == 'date1' or key == 'date2') and fields[key]:
                fields[key] = fields[key].strftime('%Y-%m-%d')
            elif key == 'tags':
                fields[key] = [i.name for i in fields[key]]
            elif key == 'creation_time' or key == 'submission_time':
                fields[key] = fields[key].strftime('%Y-%m-%dT%H:%M:%S.000Z')

        record['fields'] = fields
        logging.info(record)
        return record

    def into_human_readable(self, language, show_creator=True, media=Media.TELEGRAM):
        lines = list()
        if show_creator:
            lines.append(self.FEATURES_FOR_READABLE_FORMAT['creator'][language.name].format(
                creator=self.get_creators_name()) + '\n')
        if media == Media.TELEGRAM:
            lines.append('*' + self.name + '*')
        else:
            lines.append(self.name)
        lines.append(self.text + '\n')
        date_types_names = self.FEATURES_FOR_READABLE_FORMAT['date_type']
        lines.append(date_types_names[self.date_type.name][language.name].format(
            date1=self.date1.strftime('%d.%m.%Y'), date2=self.date2.strftime('%d.%m.%Y') if self.date2 else None))

        lines.append(self.FEATURES_FOR_READABLE_FORMAT['people_number'][language.name].format(
            people_number=str(self.people_number)))
        hashtags_list = [t.get_text(language) for t in self.tags]
        if hashtags_list:
            lines.append(self.FEATURES_FOR_READABLE_FORMAT['tags'][language.name].format(tags=', '.join(hashtags_list)))
        res_text = '\n'.join(lines)
        return res_text

    def into_draft_text(self, language, media=Media.TELEGRAM):
        not_stated = self.FEATURES_FOR_DRAFT_FORMAT['not_stated'][language.name]
        text = load_text(TextLabels.CREATION_REQUEST_DRAFT, media=media, language=language)
        if self.__dict__.get('date_type', None):
            date_type = self.FEATURES_FOR_DRAFT_FORMAT['date_type_name'][self.date_type.name][language.name]
        else:
            date_type = not_stated
        if self.__dict__.get('date1', None):
            if self.date_type == DateType.PERIOD:
                if self.__dict__.get('date2', None):
                    date = self.date1.strftime('%d.%m.%Y') + ' – ' + self.date1.strftime('%d.%m.%Y')
                else:
                    date = self.date1.strftime('%d.%m.%Y') + ' – ' + not_stated
            else:
                date = self.date1.strftime('%d.%m.%Y')
        else:
            date = not_stated
        if self.__dict__.get('tags', None):
            tags = ', '.join([t.get_text(language) for t in self.tags])
        else:
            tags = not_stated
        data = {'name': self.name if self.__dict__.get('name', None) else not_stated,
                'text': self.text if self.__dict__.get('text', None) else not_stated,
                'date_type': date_type,
                'date': date,
                'people_number': self.people_number if self.__dict__.get('people_number', None) else not_stated,
                'tags': tags}

        res_text = text.format(**data).strip()
        return res_text

    def get_creators_name(self):
        creator_user = user.User(base_id=self.creator[0])
        return creator_user.name

    def get_creator(self):
        creator = user.User(base_id=self.creator[0])
        return creator

    def update(self):
        record = self.into_record()
        self.request_elem = self.db_connector.update_request(record)

    def delete(self):
        self.db_connector.delete_request(self.base_id)

    def change_name(self, name):
        self.name = name
        self.update()

    def change_text(self, text):
        self.text = text
        self.update()

    def change_date_type(self, date_type):
        self.date_type = date_type
        self.update()

    def set_date(self, date_string):
        def transform_date_str_into_date(date_str):
            try:
                res_date = datetime.strptime(date_str, '%d.%m.%y').date()
            except ValueError:
                print_exc()
                raise exceptions.DateFormatError
            return res_date

        if self.date_type == DateType.DATE or self.date_type == DateType.DEADLINE:
            new_date = transform_date_str_into_date(date_string)
            today = date.today()
            if new_date < today:
                raise exceptions.EarlyDate
            self.date1 = new_date
            self.update()

        elif self.date_type == DateType.PERIOD:
            try:
                date1, date2 = date_string.split()
            except ValueError:
                raise exceptions.OneDateMissing
            date1 = transform_date_str_into_date(date1)
            date2 = transform_date_str_into_date(date2)
            today = date.today()
            if date1 > date2:
                raise exceptions.WrongDateOrder
            elif date1 < today:
                raise exceptions.EarlyDate
            self.date1 = date1
            self.date2 = date2
            self.update()

    def set_people_number(self, number):
        if number < 1:
            raise ValueError
        self.people_number = number
        self.update()

    def add_tag(self, tag):
        self.tags.append(tag)
        self.update()

    def delete_tag(self, tag):
        try:
            self.tags.remove(tag)
        except ValueError:
            pass
        self.update()

    def set_submission_status(self, status):
        self.was_submited = status
        self.submission_time = datetime.now()
        self.update()

    def set_publishing_status(self, status):
        self.was_published = status
        self.update()

    def set_publisher(self, publisher_user):
        self.published_by = list()
        self.published_by.append(publisher_user.base_id)
        self.update()

    @classmethod
    def new(cls, name, creator_base_id):
        record = cls.db_connector.new_request(name=name, creator_record_id=creator_base_id)
        new_request_obj = cls(record=record)
        return new_request_obj

    def has_enough_executors(self):
        if 'taken_by' in self.__dict__.keys():
            executors_number = len(self.taken_by)
        else:
            executors_number = 0
        return executors_number == self.__dict__.get('people_number', 0)

    def get_executors(self):
        executors = [user.User(base_id=u) for u in self.__dict__.get('taken_by', list())]
        return executors

    def user_is_executor(self, user_to_check):
        executors = self.__dict__.get('taken_by', list())
        return user_to_check.base_id in executors

    def get_people_number(self):
        return self.__dict__.get('people_number', 0)

    def is_expired(self):
        today = datetime.today().date()
        if self.date2:
            return self.date2 < today
        elif self.date1:
            return self.date1 < today
        else:
            return False

    def is_ready_for_submission(self):
        if self.__dict__.get('name', None) and self.__dict__.get('text', None):
            if self.__dict__.get('date_type', None) and self.__dict__.get('people_number', None):
                if self.__dict__.get('date1', None):
                    if self.__dict__.get('date_type', None) == DateType.PERIOD and self.__dict__.get('date2', None):
                        return True
                    elif self.__dict__.get('date_type', None) and self.__dict__.get('date_type',
                                                                                    None) != DateType.PERIOD:
                        return True
        return False

    @classmethod
    def get_overdue_requests(cls, date_to_check):
        requests_recs = cls.db_connector.get_overdue_requests(date_to_check)
        requests = [cls(record=i) for i in requests_recs]
        return requests

    @classmethod
    def create_csv_file(cls):
        requests = cls.db_connector.get_all_requests()
        file = ','.join(cls.INDEXES_FOR_CSV) + '\n'
        requests_sets = list()
        for r in requests:
            fields = r['fields']
            keys = tuple(fields.keys())
            for i in keys:
                if i not in cls.INDEXES_FOR_CSV:
                    del fields[i]
                elif not fields[i]:
                    fields[i] = ''
                elif type(fields[i]) == list:
                    fields[i] = ';'.join([str(i) for i in fields[i]])
                else:
                    fields[i] = str(fields[i])
            requests_sets.append(fields)
        for i in range(len(requests_sets)):
            requests_sets[i] = [requests_sets[i].get(k, '') for k in cls.INDEXES_FOR_CSV]
        file = file + '\n'.join([','.join(i) for i in requests_sets])
        name = 'requests-' + datetime.now().strftime('%d-%m-%yT%H.%M') + '.csv'
        res = bytes(file, 'utf-8')
        file_obj = io.BytesIO(res)
        file_obj.name = name
        return file_obj
