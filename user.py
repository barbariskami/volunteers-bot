import dataBase
from enumerates import Media
from exceptions import AlreadyRegistered


class User:
    def __init__(self, media=None, user_id=None, recording=None):
        if recording:
            user_elem = recording
        else:
            user_elem = dataBase.get_user_by_id_in_media(media, user_id)
        self.__dict__ = user_elem['fields']

        # Deletion of needless (or inconvenient) fields
        del self.__dict__['id']
        for i in Media:
            if i.name.lower() + '_id' in self.__dict__.keys():
                del self.__dict__[i.name.lower() + '_id']
            if i.name.lower() + '_state' in self.__dict__.keys():
                del self.__dict__[i.name.lower() + '_state']

        # Adding some other important fields
        self.user_elem = user_elem
        self.base_id = user_elem['id']
        self.media_id = {}
        self.state = {}
        for i in Media:
            self.media_id[i] = user_elem['fields'].get(i.name.lower() + '_id', None)
            self.state[i] = user_elem['fields'].get(i.name.lower() + '_state', None)
        if 'if_moderator' not in self.__dict__.keys():
            self.__dict__['if_moderator'] = False

        print(self.__dict__)

    def transform_into_record(self):
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
                        fields[media.name.lower() + '_state'] = self.state[media]
        record['fields'] = fields
        return record

    def update(self):
        record = self.transform_into_record()
        self.user_elem = dataBase.update_user(record)

    def set_state(self, media, state):
        self.state[media] = state.name
        self.update()

    @staticmethod
    def register(media, user_id, password):
        user = User(dataBase.get_user_by_password(password))
        if user.media_id.get(media, None):
            raise AlreadyRegistered
        user.media_id[media] = user_id
        user.update()




