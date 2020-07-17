from user import User
from message import Message
from exceptions import UserNotFound, AlreadyRegistered
from extensions import load_text
from keyboard import Keyboard
from enumerates import TextLabels, States, MessageMarks, Media


class Bot:
    """
    Класс Bot представляет собой основной класс проекта, который содержит в себе все базовые функции.
    Класс используется для отделения механики бота от платформы, на которой он будет использоваться.
    Используя статические методы класса, программа для работы с конкретным медиа может использовать все функции,
    необходимые для коректной работы.
    Позволяет начать диалог с пользователем, связать его медиа-акк с аккаунтом в системе, обработать получение нового
    сообщения и нажатие на кнопку клавиатуры.
    """

    @staticmethod
    def start_conversation(media, user_id):
        """
        Метод должен использоваться программой-ботом для начала диалога с пользователем, который раньше не использовал
        бота на этой конкретной платформе или перезапустил бота. Этот метод совершает попытку опознать пользователя на
        случай, если он уже использовал бота в этой платформы и просто воспользовался перезагруской, и в случае успеха
        выводит его в главное меню. Иначе он предлагает пользователю связать его аккаунт на платформе с уже существующим
        (и созданным силами админов) аккаунтом в системе.
        :param media:
        :param user_id:
        :return:
        """
        try:
            user = User(media=media, user_id=user_id)
        except UserNotFound:
            new_message = Message(user_id, text=load_text(TextLabels.REGISTRATION, media=Media.TELEGRAM),
                                  marks=[MessageMarks.UNREGISTERED])
        else:
            new_message = Message(user_id,
                                  text=load_text(TextLabels.MAIN_MENU_GREETING,
                                                 media=Media.TELEGRAM),
                                  keyboard=Keyboard(state=States.MAIN_MENU),
                                  marks=[MessageMarks.KEYBOARD])
            user.set_state(media, States.MAIN_MENU)
        return list([new_message])

    @staticmethod
    def register(media, user_id, password):
        """
        Метод получает на вход объект media, который является экземпляром класса enumerates.Media, id пользователя на
        этой платформе, и пароль, который он должен получить через инфе каналы связи от департамента внеакадема или
        других лиц, отвечающих за регистрацию учеников в системе ресурса. Метод пытается зарегистрировать пользователя
        (связать аккаунт в медиа с аккаунтом в системе) При несовпадении пароля предлагается попробовать ввести его
        снова. Если аккаунт этого человека в системе уже связан с неким аккаунтом в этом медиа, пользователю предлага-
        ется обратиться в аккаунт внеакадема.
        :param media:
        :param user_id: is id of the user inside the media, for example in Telegram it is id given to user by telegram
        :param password: is the password sent by a user to register
        :return:
        """

        try:
            User.register(media, user_id, password)
        except UserNotFound:
            new_message = Message(user_id, text=load_text(TextLabels.WRONG_PASSWORD, media=Media.TELEGRAM),
                                  marks=list([MessageMarks.UNREGISTERED]))
        except AlreadyRegistered:
            new_message = Message(user_id, text=load_text(TextLabels.ALREADY_REGISTERED, media=Media.TELEGRAM),
                                  marks=list([MessageMarks.UNREGISTERED]))
        else:
            user = User(media=media, user_id=user_id)
            new_message = Message(user_id,
                                  text=load_text(TextLabels.MAIN_MENU_GREETING_NEW, media=Media.TELEGRAM),
                                  keyboard=Keyboard(state=States.MAIN_MENU),
                                  marks=list([MessageMarks.SUCCESSFUL_REGISTRATION]))
        return list([new_message])

    @classmethod
    def handle_message(cls, media, message):
        """
         Метод предполагает быть запущенным при получении некоторого сообщения от пользователя. При получении сообщения
         бот определяет его отправителя, его состояние на этой платформе (его позицию в дереве диалога, например главное
         меню или меню выбора шаблона задачи) и запускает обработчик сообщения, соответствующий состоянию пользователя
        :param media:
        :param message:
        :return:
        """
        new_messages = list()
        try:
            user = User(media, message.user_id)
        except UserNotFound:
            new_messages.append(Message(message.user_id,
                                        text=load_text(TextLabels.REGISTRATION, media=Media.TELEGRAM),
                                        marks=list([MessageMarks.UNREGISTERED]))
                                )
        else:
            try:
                state = user.state
            except AttributeError:
                user.state = States.MAIN_MENU
                state = user.state
            new_message = cls.state_handlers[state](user, message)
            new_messages.append(new_message)
        return new_messages

    @staticmethod
    def button_pressed(media, user_id, button):
        new_messages = list()
        try:
            user = User(media=media, user_id=user_id)
        except UserNotFound:
            pass
        return new_messages

    @staticmethod
    def __main_menu_state_handler__(user, message):
        new_messages = list()
        new_message = None
        return new_messages

    # Словарь определяет обработчик сообщения для каждого состояния
    state_handlers = {States.MAIN_MENU: __main_menu_state_handler__}
