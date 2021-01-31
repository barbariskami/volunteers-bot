class Message:
    def __init__(self, user_id, media_id=0, media=None, text='', image=None, date=None, marks=tuple(), keyboard=None,
                 bot=None, record=None, request_id=None, moderation=False, main_bot=False, **kwargs):
        self.media_id = media_id
        self.user_id = user_id
        self.media = media
        self.text = text
        self.image = image
        self.date = date
        self.marks = marks
        self.keyboard = keyboard
        self.bot = bot
        self.record = record

        # Блок переменных, необходимых для записи соответствия {запрос – сообщение в мессенджере} в базу данных
        self.request_id = request_id
        self.moderation = moderation
        self.main_bot = main_bot
