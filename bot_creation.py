from bot import Bot, ButtonHandler, MessageHandler
from user import User
from message import Message
from exceptions import UserNotFound, AlreadyRegistered
from extensions import load_text, transform_tags_into_text
from keyboard import Keyboard
from enumerates import TextLabels, States, MessageMarks, Languages, ButtonActions
import copy


class CreationBot(Bot):
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
            new_message = Message(user_id, text=load_text(TextLabels.CREATION_UNREGISTERED, media=media),
                                  marks=[MessageMarks.UNREGISTERED])
        else:
            new_message = Message(user_id,
                                  text=load_text(TextLabels.CREATION_MAIN_MENU_GREETING,
                                                 media=media,
                                                 language=user.language[media]),
                                  keyboard=Keyboard(state=States.CREATION_MAIN_MENU,
                                                    language=user.language.get(media, Languages.RU)))
            user.set_state(media, States.CREATION_MAIN_MENU, creation=True)
        return list([new_message])

    @staticmethod
    def unregistered(media, user_id):
        new_message = Message(user_id,
                              text=load_text(TextLabels.CREATION_UNREGISTERED, media=media),
                              marks=list([MessageMarks.UNREGISTERED]))
        return list([new_message])
