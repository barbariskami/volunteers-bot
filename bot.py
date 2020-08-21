from user import User
from message import Message
from exceptions import UserNotFound, AlreadyRegistered
from extensions import load_text, transform_tags_into_text
from keyboard import Keyboard
from enumerates import TextLabels, States, MessageMarks, Languages, ButtonActions
import copy


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
            new_message = Message(user_id, text=load_text(TextLabels.WRONG_PASSWORD, media=media),
                                  marks=list([MessageMarks.UNREGISTERED]))
        except AlreadyRegistered:
            new_message = Message(user_id, text=load_text(TextLabels.ALREADY_REGISTERED, media=media),
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
        # new_message = Message(user_id=user.media_id[media],
        #                       text=load_text(TextLabels.TAG_DELETED_FROM_IGNORE,
        #                                      media,
        #                                      user.language.get(media, Languages.RU)))
        # new_messages.append(new_message)
        return new_messages

    @staticmethod
    def __button_add_tag_into_ignore__(user, media, button):
        tag = button.info['tag']
        user.add_tag_into_ignore(tag)
        new_messages = list()
        new_message = Message(user_id=user.media_id[media],
                              text=load_text(TextLabels.TAG_ADDED_INTO_IGNORE,
                                             media,
                                             user.language.get(media, Languages.RU)))
        new_messages.append(new_message)
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


class FormingProducer:
    def __init__(self, user, media, button):
        self.user = user
        self.media = media
        self.button = button

        self.functions_for_formation = {TextLabels.IGNORE_SETTINGS: self.ignore_lists_messages,
                                        TextLabels.CHOSE_TAG_DELETION: self.chose_tag_to_edit,
                                        TextLabels.CHOSE_TAG_ADDING: self.chose_tag_to_edit,
                                        TextLabels.TAG_ADDED_INTO_IGNORE: self.chose_tag_to_edit,
                                        TextLabels.TAG_DELETED_FROM_IGNORE: self.chose_tag_to_edit}

    def form_message(self, text_label):
        data = self.functions_for_formation[text_label](self.user, self.media, self.button)
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
