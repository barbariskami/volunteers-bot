import dataBase


class Message:
    def __init__(self, user_id, message_id=0, media=None, text='', image=None, date=None, marks=tuple(), keyboard=None,
                 **kwargs):
        self.id = message_id
        self.user_id = user_id
        self.media = media
        self.text = text
        self.image = image
        self.date = date
        self.marks = marks
        self.keyboard = keyboard
