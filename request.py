from dataBase import get_request_by_id, get_request_by_base_id, new_request, delete_request
import dataBase
from copy import deepcopy
from enumerates import DateType, HashTags
import exceptions
from datetime import datetime, date
from traceback import print_exc


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
        if 'tags' not in self.__dict__.keys():
            self.tags = list()
        else:
            self.tags = [HashTags[i] for i in self.tags]

    def into_record(self):
        record = {'id': self.base_id}
        fields = deepcopy(self.__dict__)
        keys = list(fields.keys())

        for key in keys:
            if key == 'request_elem' or key == 'base_id' or fields[key] is None:
                del fields[key]
            elif key == 'date_type':
                fields[key] = self.date_type.name
            elif key == 'id':
                del fields[key]
            elif key == 'date1' or key == 'date2':
                fields[key] = fields[key].strftime('%Y-%m-%d')
            elif key == 'tags':
                fields[key] = [i.name for i in fields[key]]

        record['fields'] = fields
        return record

    def update(self):
        record = self.into_record()
        self.request_elem = dataBase.update_request(record)

    def delete(self):
        delete_request(self.base_id)

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

    @classmethod
    def new(cls, name, creator_base_id):
        record = dataBase.new_request(name=name, creator_record_id=creator_base_id)
        new_request_obj = cls(record=record)
        return new_request_obj
