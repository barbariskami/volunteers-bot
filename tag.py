import json
from mysql_database import DBAlchemyConnector
from enumerates import Languages
from exceptions import TagNotFound, TagCodeValueError, TagNotAllLanguages
import string


class Tag:
    f = open('db_info.json')
    db_connector = DBAlchemyConnector(**json.load(f))

    def __init__(self, code=None, data=None):
        if not data and code:
            data = self.db_connector.get_tag(code)
        if not data:
            raise TagNotFound
        self.code = data['code']
        self.text = dict()
        for l in Languages:
            self.text[l] = data.get(l.name, '')
        self.name = self.code
        self.is_shown = data['is_shown']

    @classmethod
    def get_all_tags(cls, only_shown=False):
        tags_data_pieces = cls.db_connector.get_all_tags(only_shown=only_shown)
        tags = [cls(data=i) for i in tags_data_pieces]
        return tags

    def get_text(self, language):
        return self.text.get(language, '')

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.code == other.code
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def switch_state(self):
        self.is_shown = not self.is_shown
        self.db_connector.change_tags_state(self.code)
        return self.is_shown

    @classmethod
    def new(cls, code, languages):
        for i in code:
            if i not in string.ascii_letters and i.isalpha():
                raise TagCodeValueError
        code = code.upper()
        for l in languages:
            if l not in languages.keys():
                raise TagNotAllLanguages
        new_tag = cls.db_connector.add_tag(code, languages)
        return cls(data=new_tag)

    def delete(self):
        self.db_connector.delete_tag(self.code)

