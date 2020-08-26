from user import User
from message import Message
from exceptions import UserNotFound, AlreadyRegistered
from extensions import load_text, transform_tags_into_text
from keyboard import Keyboard
from enumerates import TextLabels, States, MessageMarks, Languages, ButtonActions, DateType
from request import Request
import copy
import json


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
            new_message = Message(user_id, text=load_text(TextLabels.REGISTRATION, media=media),
                                  marks=[MessageMarks.UNREGISTERED])
        else:
            new_message = Message(user_id,
                                  text=load_text(TextLabels.MAIN_MENU_GREETING,
                                                 media=media,
                                                 language=user.language[media]),
                                  keyboard=Keyboard(state=States.MAIN_MENU,
                                                    language=user.language.get(media, Languages.RU)))
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
            new_message = Message(user_id,
                                  text=load_text(TextLabels.WRONG_PASSWORD, media=media),
                                  marks=list([MessageMarks.UNREGISTERED]))
        except AlreadyRegistered:
            new_message = Message(user_id,
                                  text=load_text(TextLabels.ALREADY_REGISTERED, media=media),
                                  marks=list([MessageMarks.UNREGISTERED]))
        else:
            user = User(media=media, user_id=user_id)
            new_message = Message(user_id,
                                  text=load_text(TextLabels.MAIN_MENU_GREETING_NEW,
                                                 media=media,
                                                 language=user.language[media]),
                                  keyboard=Keyboard(state=States.MAIN_MENU,
                                                    language=user.language.get(media, Languages.RU)),
                                  marks=list([MessageMarks.SUCCESSFUL_REGISTRATION]))
        return list([new_message])

    @staticmethod
    def unregistered(media, user_id):
        new_message = Message(user_id,
                              text=load_text(TextLabels.UNREGISTERED, media=media),
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
    def handle_message(cls, media, message, creation=False):
        """
         Метод предполагает быть запущенным при получении некоторого сообщения от пользователя. При получении сообщения
         бот определяет его отправителя, его состояние на этой платформе (его позицию в дереве диалога, например главное
         меню или меню выбора шаблона задачи) и запускает обработчик сообщения, соответствующий состоянию пользователя
        :param media:
        :param message:
        :param creation:
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
                state = user.get_state(media, creation=creation)
            except AttributeError:
                user.set_state(media, States.MAIN_MENU)
                state = user.get_state(media, creation=creation)

            message_handler = MessageHandler(user, media)
            new_messages = message_handler.handle(state, message)
        return new_messages

    @staticmethod
    def button_pressed(media, user_id, button, creation=False):
        new_messages = list()
        try:
            user = User(media=media, user_id=user_id)
        except UserNotFound:
            new_messages.append(Message(user_id=user_id,
                                        text=load_text(TextLabels.REGISTRATION, media=media),
                                        marks=list([MessageMarks.UNREGISTERED]))
                                )
        else:
            button_handler = ButtonHandler(user, media, button)
            for action in button.actions:
                new_messages_from_button = button_handler.handle(action)
                new_messages.extend(new_messages_from_button)
            user.set_state(media, button.following_state, creation=creation)
        return new_messages


class ButtonHandler:
    def __init__(self, user, media, button):
        self.user = user
        self.media = media
        self.button = button

        self.button_action_methods = {ButtonActions.LOAD_STATE: self.standard,
                                      ButtonActions.SWITCH_LANGUAGE: self.switch_language,
                                      ButtonActions.FORM_MESSAGE: self.form_message,
                                      ButtonActions.ADD_TAG: self.add_tag_into_ignore,
                                      ButtonActions.DELETE_TAG: self.delete_tag_from_ignore,
                                      ButtonActions.DELETE_CURRENT_EDITED_DRAFT: self.delete_current_draft,
                                      ButtonActions.SET_DATE_TYPE: self.set_date_type}

    def handle(self, action):
        res = self.button_action_methods[action]()
        return res

    def standard(self):
        # Обработчик для тех кнопок, которые не выполняют особых действий, а просто переводят в состояние, в
        # котором юзеру отправляется только одно соощение
        new_messages = list()
        new_message = Message(user_id=self.user.media_id[self.media],
                              text=load_text(TextLabels[self.button.following_state.name], self.media,
                                             self.user.language.get(self.media, Languages.RU)),
                              keyboard=Keyboard(state=self.button.following_state,
                                                language=self.user.language.get(self.media, Languages.RU)))

        new_messages.append(new_message)
        return new_messages

    def switch_language(self):
        language = Languages[self.button.info['language']]
        self.user.set_language(self.media, language)
        new_messages = list()
        new_message = Message(user_id=self.user.media_id[self.media],
                              text=load_text(TextLabels.LANGUAGE_SWITCHED_SUCCESSFULLY,
                                             self.media,
                                             self.user.language.get(self.media, Languages.RU)))
        new_messages.append(new_message)
        return new_messages

    def form_message(self):
        producer = FormingProducer(self.user, self.media, self.button)
        message_type = TextLabels[self.button.info['message_type']]
        message_data = producer.form_message(message_type)

        new_messages = list()
        new_message = Message(user_id=self.user.media_id[self.media],
                              text=message_data['text'] if not self.button.info.get('no_text', False) else '',
                              keyboard=message_data['keyboard'] if message_data['keyboard']
                              else Keyboard(state=self.button.following_state,
                                            language=self.user.language.get(self.media, Languages.RU)))
        new_messages.append(new_message)
        return new_messages

    def delete_tag_from_ignore(self):
        tag = self.button.info['tag']
        self.user.delete_tag_from_ignore(tag)
        new_messages = list()
        return new_messages

    def add_tag_into_ignore(self):
        tag = self.button.info['tag']
        self.user.add_tag_into_ignore(tag)
        new_messages = list()
        return new_messages

    def delete_current_draft(self):
        draft = self.user.get_edited_draft(self.media)
        draft.delete()

        message = Message(user_id=self.user.media_id[self.media],
                          text=load_text(TextLabels.CREATION_DRAFT_DELETED_SUCCESSFULLY,
                                         self.media,
                                         self.user.language.get(self.media, Languages.RU))
                          )
        new_messages = list()
        new_messages.append(message)
        return new_messages

    def set_date_type(self):
        date_type = self.button.info['date_type']
        request = self.user.get_edited_draft(self.media)
        request.change_date_type(date_type)

        return list()


class FormingProducer:
    def __init__(self, user, media, button):
        self.user = user
        self.media = media
        self.button = button

        self.FEATURES_PATH = 'features_for_formation.json'
        self.FUNCTIONS_FOR_FORMATION = {TextLabels.IGNORE_SETTINGS: self.ignore_lists_messages,
                                        TextLabels.CHOSE_TAG_DELETION: self.chose_tag_to_edit,
                                        TextLabels.CHOSE_TAG_ADDING: self.chose_tag_to_edit,
                                        TextLabels.TAG_ADDED_INTO_IGNORE: self.chose_tag_to_edit,
                                        TextLabels.TAG_DELETED_FROM_IGNORE: self.chose_tag_to_edit,
                                        TextLabels.CREATION_SET_DATE: self.creation_set_date}

    def load_features_for_formation(self, type_of_features):
        file = open(self.FEATURES_PATH)
        data = json.load(file)
        return data[type_of_features]

    def form_message(self, text_label):
        data = self.FUNCTIONS_FOR_FORMATION[text_label]()
        message_text = load_text(text_label,
                                 self.media,
                                 self.user.language.get(self.media, Languages.RU))
        res_message_text = message_text.format(**data['text'])
        return {'text': res_message_text, 'keyboard': data['keyboard']}

    def ignore_lists_messages(self):
        ignored = self.user.get_ignored_hashtags_text(self.media)
        subscription = self.user.get_subscription_hashtags_text(self.media)

        keyboard_data = Keyboard.load_keyboard(self.button.following_state.name)

        if ignored:
            ignored = '\n'.join(map(lambda x: '- ' + x, ignored))
        else:
            ignored = load_text(TextLabels.EMPTY_LIST, self.media, language=self.user.language[self.media]).strip()
            del keyboard_data['buttons'][1]
        if subscription:
            subscription = '\n'.join(map(lambda x: '- ' + x, subscription))
        else:
            subscription = load_text(TextLabels.EMPTY_LIST, self.media, language=self.user.language[self.media]).strip()
            del keyboard_data['buttons'][0]

        keyboard = Keyboard(language=self.user.language.get(self.media, Languages.RU), json_set=keyboard_data)

        res = {'text': {'ignored': ignored, 'subscription': subscription}, 'keyboard': keyboard}
        return res

    def chose_tag_to_edit(self):
        new_button_state = ''
        tags = list()
        if self.button.following_state == States.CHOSE_TAG_ADDING:
            new_button_state = 'CHOSE_TAG_ADDING'
            tags = self.user.subscription_hashtags()
        elif self.button.following_state == States.CHOSE_TAG_DELETION:
            new_button_state = 'CHOSE_TAG_DELETION'
            tags = self.user.ignored_tags

        keyboard = Keyboard.load_keyboard(self.button.following_state.name)
        if len(tags) > 10:
            right_border = (self.button.info['page'] + 1) * 7
            if right_border > len(tags):
                right_border = len(tags)
            left_border = (self.button.info['page'] * 7)
            tags = tags[left_border:right_border]
            keyboard['buttons'][1][0]['info']['page'] = self.button.info['page'] - 1
            keyboard['buttons'][1][1]['info']['page'] = self.button.info['page'] + 1
            if self.button.info['page'] == 0:
                del keyboard['buttons'][1][0]
                keyboard['buttons'][1][0]['info']['page'] = 1
            elif self.button.info['page'] * 7 >= len(tags):
                del keyboard['buttons'][1][1]
        else:
            del keyboard['buttons'][1]
        button_template = keyboard['buttons'][0][0]
        del keyboard['buttons'][0][0]
        for tag in tags:
            new_button = copy.deepcopy(button_template)
            for l in list(Languages):
                new_button[l.name] = '–' + transform_tags_into_text([tag], l)[0] + '–'
            new_button['state'] = new_button_state
            new_button['info']['tag'] = tag
            keyboard['buttons'].insert(0, [new_button])

        res = {'text': {},
               'keyboard': Keyboard(language=self.user.language.get(self.media, Languages.RU),
                                    json_set=keyboard)}
        return res

    def creation_set_date(self):
        request = self.user.get_edited_draft(self.media)
        features = self.load_features_for_formation('CREATION_SET_DATE')
        res = {'text': dict()}
        res['text']['date_word'] = features['date_word'][request.date_type.name][self.user.language[self.media].name]

        res['keyboard'] = Keyboard(state=self.button.following_state, language=self.user.language[self.media])

        return res


class MessageHandler:
    def __init__(self, user, media):
        self.user = user
        self.media = media

        self.message_handlers = {States.MAIN_MENU: self.ignore_handler,
                                 States.CREATION_NEW_REQUEST: self.create_new_request,
                                 States.CREATION_TYPE_TEXT: self.edit_text}

    def handle(self, state, message):
        handler = self.message_handlers.get(state, None)
        if not handler:
            handler = self.ignore_handler
        res = handler(message)
        return res

    def ignore_handler(self, message):
        new_messages = list()
        return new_messages

    def create_new_request(self, message):
        name = message.text
        request = Request.new(name, self.user.base_id)
        self.user.connect_request(request)

        new_messages = list()

        next_state = States.CREATION_TYPE_TEXT
        new_message = Message(self.user.media_id[self.media],
                              text=load_text(TextLabels[next_state.name],
                                             media=self.media,
                                             language=self.user.language[self.media]),
                              keyboard=Keyboard(state=next_state,
                                                language=self.user.language.get(self.media, Languages.RU)))

        new_messages.append(new_message)
        self.user.set_state(self.media, next_state, creation=True)
        self.user.set_edited_draft(self.media, request.id)
        return new_messages

    def edit_text(self, message):
        text = message.text
        request = self.user.get_edited_draft(self.media)
        request.change_text(text)

        new_messages = list()

        next_state = States.CREATION_CHOSE_DATE_TYPE
        new_message = Message(self.user.media_id[self.media],
                              text=load_text(TextLabels[next_state.name],
                                             media=self.media,
                                             language=self.user.language[self.media]),
                              keyboard=Keyboard(state=next_state,
                                                language=self.user.language.get(self.media, Languages.RU)))
        new_messages.append(new_message)
        self.user.set_state(self.media, next_state, creation=True)
        return new_messages
