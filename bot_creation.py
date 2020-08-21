from bot import Bot
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

    @staticmethod
    def switch_language_command(user_id, media):
        new_messages = list()
        try:
            user = User(media, user_id)
        except UserNotFound:
            new_messages.append(Message(user_id,
                                        text=load_text(TextLabels.REGISTRATION, media=media),
                                        marks=list([MessageMarks.UNREGISTERED])))
        else:
            new_message = Message(user_id=user.media_id[media],
                                  text=load_text(TextLabels.CHOSE_LANGUAGE, media,
                                                 user.language.get(media, Languages.RU)),
                                  keyboard=Keyboard(state=States.CHOSE_LANGUAGE,
                                                    language=user.language.get(media, Languages.RU)))
            new_messages.append(new_message)

            user.set_state(media, States.CHOSE_LANGUAGE)

        return new_messages

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
                                        text=load_text(TextLabels.REGISTRATION, media=media),
                                        marks=list([MessageMarks.UNREGISTERED]))
                                )
        else:
            try:
                state = user.state[media]
            except AttributeError:
                user.state = States.MAIN_MENU
                state = user.state
            new_messages_from_handler = cls.state_handlers[state](user, media, message)
            for message in new_messages_from_handler:
                new_messages.append(message)
        return new_messages

    @classmethod
    def button_pressed(cls, media, user_id, button):
        new_messages = list()
        try:
            user = User(media=media, user_id=user_id)
        except UserNotFound:
            new_messages.append(Message(user_id=user_id,
                                        text=load_text(TextLabels.REGISTRATION, media=media),
                                        marks=list([MessageMarks.UNREGISTERED]))
                                )
        else:
            for action in button.actions:
                new_messages_from_button = cls.buttons_methods[action](user, media, button)
                new_messages.extend(new_messages_from_button)
            user.set_state(media, button.following_state)
        return new_messages

    @staticmethod
    def __ignore_handler__(user, media, message):
        new_messages = list()
        return new_messages

    @staticmethod
    def __button_standard__(user, media, button):
        # Обработчик для тех кнопок, которые не выполняют особых действий, а просто переводят в состояние, в
        # котором юзеру отправляется только одно соощение
        new_messages = list()
        new_message = Message(user_id=user.media_id[media],
                              text=load_text(TextLabels[button.following_state.name], media,
                                             user.language.get(media, Languages.RU)),
                              keyboard=Keyboard(state=button.following_state,
                                                language=user.language.get(media, Languages.RU)))

        new_messages.append(new_message)
        return new_messages

    @staticmethod
    def __button_switch_language__(user, media, button):
        language = Languages[button.info['language']]
        user.set_language(media, language)
        new_messages = list()
        new_message = Message(user_id=user.media_id[media],
                              text=load_text(TextLabels.LANGUAGE_SWITCHED_SUCCESSFULLY,
                                             media,
                                             user.language.get(media, Languages.RU)))
        new_messages.append(new_message)
        return new_messages

    @staticmethod
    def __button_form_message__(user, media, button):
        producer = FormingProducer(user, media, button)
        message_type = TextLabels[button.info['message_type']]
        message_data = producer.form_message(message_type)

        new_messages = list()
        new_message = Message(user_id=user.media_id[media],
                              text=message_data['text'] if not button.info.get('no_text', False) else '',
                              keyboard=message_data['keyboard'] if message_data['keyboard']
                              else Keyboard(state=button.following_state,
                                            language=user.language.get(media, Languages.RU)))
        new_messages.append(new_message)
        return new_messages

    @staticmethod
    def __button_delete_tag_from_ignore__(user, media, button):
        tag = button.info['tag']
        user.delete_tag_from_ignore(tag)
        new_messages = list()
        return new_messages

    @staticmethod
    def __button_add_tag_into_ignore__(user, media, button):
        tag = button.info['tag']
        user.add_tag_into_ignore(tag)
        new_messages = list()
        return new_messages

    # Словарь определяет обработчик сообщения для каждого состояния
    state_handlers = {States.MAIN_MENU: __ignore_handler__.__get__(object),
                      States.SETTINGS: __ignore_handler__.__get__(object),
                      States.HELP: __ignore_handler__.__get__(object)}

    # Словарь определяет обработчик для каждого дейстаия, предусмотренного какой-то кнопкой
    buttons_methods = {ButtonActions.LOAD_STATE: __button_standard__.__get__(object),
                       ButtonActions.SWITCH_LANGUAGE: __button_switch_language__.__get__(object),
                       ButtonActions.FORM_MESSAGE: __button_form_message__.__get__(object),
                       ButtonActions.ADD_TAG: __button_add_tag_into_ignore__.__get__(object),
                       ButtonActions.DELETE_TAG: __button_delete_tag_from_ignore__.__get__(object)}
