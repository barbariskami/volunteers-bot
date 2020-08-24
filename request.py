from dataBase import get_request_by_id, get_request_by_base_id, new_request, delete_request
import dataBase
from copy import deepcopy


class Request:
    def __init__(self, request_id=None, request_base_id=None, record=None):
        if request_id:
            record = get_request_by_id(request_id)
        elif request_base_id:
            record = get_request_by_base_id(request_base_id)

        self.__dict__ = deepcopy(record['fields'])

        self.request_elem = record
        self.base_id = record['id']

    def into_record(self):
        record = {'id': self.base_id}
        fields = deepcopy(self.__dict__)
        keys = list(fields.keys())

        for key in keys:
            if key == 'user_elem' or key == 'base_id' or fields[key] is None:
                del fields[key]

        record['fields'] = fields
        return record

    def delete(self):
        delete_request(self.base_id)

    def change_text(self, text):
        self.text = text

    @classmethod
    def new(cls, name, creator_base_id):
        print(name, creator_base_id)
        record = dataBase.new_request(name=name, creator_record_id=creator_base_id)
        new_request_obj = cls(record=record)
        return new_request_obj

