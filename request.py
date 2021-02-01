from dataBase import get_request_by_id, get_request_by_base_id
import dataBase
from copy import deepcopy
from enumerates import DateType, HashTags
import exceptions
from extensions import tag_into_text
from datetime import datetime, date
from traceback import print_exc
import user


class Request:
    def __init__(self, request_id=None, request_base_id=None, record=None):
        if request_id:
            record = get_request_by_id(request_id)
        elif request_base_id:
            record = get_request_by_base_id(request_base_id)

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
            self.date2 = datetime.strptime(self.date1, '%Y-%m-%d').date()
        else:
            self.date2 = None
        if 'tags' not in self.__dict__.keys():
            self.tags = list()
        else:
            self.tags = [HashTags[i] for i in self.tags]

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
            elif key == 'id' or key == 'FEATURES_FOR_READABLE_FORMAT':
                del fields[key]
            elif (key == 'date1' or key == 'date2') and fields[key]:
                fields[key] = fields[key].strftime('%Y-%m-%d')
            elif key == 'tags':
                fields[key] = [i.name for i in fields[key]]

        record['fields'] = fields
        return record

    def into_human_readable(self, language):
        lines = list()
        lines.append(self.FEATURES_FOR_READABLE_FORMAT['creator'][language.name].format(
            creator=self.get_creators_name()))
        lines.append(self.name)
        lines.append(self.text)
        date_types_names = self.FEATURES_FOR_READABLE_FORMAT['date_type']
        lines.append(date_types_names[self.date_type.name][language.name].format(
            date1=str(self.date1), date2=str(self.date2)))

        lines.append(self.FEATURES_FOR_READABLE_FORMAT['people_number'][language.name].format(
            people_number=str(self.people_number)))
        hashtags_list = tag_into_text(self.tags, language)
        if hashtags_list:
            lines.append(self.FEATURES_FOR_READABLE_FORMAT['tags'][language.name].format(tags=', '.join(hashtags_list)))
        res_text = '\n'.join(lines)
        return res_text

    def get_creators_name(self):
        creator_user = user.User(base_id=self.creator[0])
        return creator_user.name_surname

    def get_creator(self):
        creator = user.User(base_id=self.creator[0])
        return creator

    def update(self):
        record = self.into_record()
        self.request_elem = dataBase.update_request(record)

    def delete(self):
        dataBase.delete_request(self.base_id)

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
            if new_date <= today:
                raise exceptions.EarlyDate
            self.date1 = new_date
            self.update()

        elif self.date_type == DateType.PERIOD:
            date1, date2 = date_string.split()
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
        record = dataBase.new_request(name=name, creator_record_id=creator_base_id)
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

