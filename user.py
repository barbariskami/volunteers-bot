import dataBase
from enumerates import Media, States, Languages
from exceptions import AlreadyRegistered


class User:
    """
    Класс представляет собой объект пользователя. В экземпляре класса хранятся все данные о пользователе, которые
    содержатся в базе данных или данные, которые еше не занесены в базу, но будут помещены туда (формат данных должен
    совпадать с форматом airtable)
    """

    def __init__(self, media=None, user_id=None, record=None):
        if record:
            # If there is a record given, we use it
            user_elem = record
        else:
            # Otherwise load the data from the base
            user_elem = dataBase.get_user_by_id_in_media(media, user_id)

        # all the fields from airtable-base turn into class object's fields
        self.__dict__ = user_elem['fields']

        # Adding some other important fields, which were not mentioned in database
        self.user_elem = user_elem
        self.base_id = user_elem['id']
        self.media_id = {}
        self.state = {}
        self.creative_state = {}
        self.language = {}
        for i in Media:
            self.media_id[i] = user_elem['fields'].get(i.name.lower() + '_id', None)
            self.state[i] = States[user_elem['fields'].get(i.name.lower() + '_state', 'MAIN_MENU')]
            self.language[i] = Languages[user_elem['fields'].get(i.name.lower() + '_language', 'RU')]
            self.creative_state[i] = States[user_elem['fields'].get(i.name.lower() + '_creative_state', 'MAIN_MENU')]
        if 'if_moderator' not in self.__dict__.keys():
            self.__dict__['if_moderator'] = False

        # Deletion of needless (or inconvenient) fields
        del self.__dict__['id']
        for i in Media:
            if i.name.lower() + '_id' in self.__dict__.keys():
                del self.__dict__[i.name.lower() + '_id']
            if i.name.lower() + '_state' in self.__dict__.keys():
                del self.__dict__[i.name.lower() + '_state']
            if i.name.lower() + '_language' in self.__dict__.keys():
                del self.__dict__[i.name.lower() + '_language']
            if i.name.lower() + '_creative_state' in self.__dict__.keys():
                del self.__dict__[i.name.lower() + '_creative_state']

    def transform_into_record(self):
        # Creates an airtable record from an object and returns it
        record = {'id': self.base_id}
        fields = self.__dict__.copy()
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
                    if not self.state[media] is None:
                        fields[media.name.lower() + '_state'] = self.state[media].name
            elif key == 'creative_state':
                del fields[key]
                for media in self.state.keys():
                    if not self.state[media] is None:
                        fields[media.name.lower() + '_creative_state'] = self.creative_state[media].name
            elif key == 'language':
                del fields[key]
                for media in self.state.keys():
                    if not self.state[media] is None:
                        fields[media.name.lower() + '_language'] = self.language[media].name
        record['fields'] = fields
        return record

    def update(self):
        # updates the state of a user on a server
        record = self.transform_into_record()
        self.user_elem = dataBase.update_user(record)

    def set_state(self, media, state):
        # changes the state parameter and loads the changes on a server
        self.state[media] = state
        self.update()

    @staticmethod
    def register(media, user_id, password):
        """
        This static method is used to register a new user using a unique password given to them by student development
        department (or any other people that regulate the usage of this service). It loads all the information about the
        user from the password and add his media-id to an airtable base.
        :param media:
        :param user_id:
        :param password:
        :return:
        """
        user = User(record=dataBase.get_user_by_password(password))
        if user.media_id.get(media, None):
            raise AlreadyRegistered
        user.media_id[media] = user_id
        user.update()
