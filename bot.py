from request import Request
from user import User
from message import Message
from exceptions import UserNotFound, AlreadyRegistered, DateFormatError, EarlyDate, WrongDateOrder
from extensions import load_text, tag_into_text, load_features_for_formation, get_action_text_for_creation
from keyboard import Keyboard
from enumerates import TextLabels, States, MessageMarks, Languages, ButtonActions, HashTags, Bots
import copy
from traceback import print_exc


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
    def start_conversation(media, user_id, user_contact_link=''):
        """
        Метод должен использоваться программой-ботом для начала диалога с пользователем, который раньше не использовал
        бота на этой конкретной платформе или перезапустил бота. Этот метод совершает попытку опознать пользователя на
        случай, если он уже использовал бота в этой платформы и просто воспользовался перезагруской, и в случае успеха
        выводит его в главное меню. Иначе он предлагает пользователю связать его аккаунт на платформе с уже существующим
        (и созданным силами админов) аккаунтом в системе.
        :param user_contact_link:
        :param media:
        :param user_id:
        :return:
        """
        try:
            user = User(media=media, user_id=user_id)
            user.set_link(media=media,
                          link=user_contact_link)
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
            user.clear_edited_draft_field(media)

        messages_list = list([new_message])
        response = {'send': messages_list}
        return response

    @staticmethod
    def register(media, user_id, password, user_contact_link=''):
        """
        Метод получает на вход объект media, который является экземпляром класса enumerates.Media, id пользователя на
        этой платформе, и пароль, который он должен получить через инфе каналы связи от департамента внеакадема или
        других лиц, отвечающих за регистрацию учеников в системе ресурса. Метод пытается зарегистрировать пользователя
        (связать аккаунт в медиа с аккаунтом в системе) При несовпадении пароля предлагается попробовать ввести его
        снова. Если аккаунт этого человека в системе уже связан с неким аккаунтом в этом медиа, пользователю предлага-
        ется обратиться в аккаунт внеакадема.
        :param user_contact_link:
        :param media:
        :param user_id: is id of the user inside the media, for example in Telegram it is id given to user by telegram
        :param password: is the password sent by a user to register
        :return:
        """

        try:
            User.register(media, user_id, password, user_contact_link)
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
        messages_list = list([new_message])
        response = {'send': messages_list}
        return response

    @staticmethod
    def unregistered(media, user_id):
        new_message = Message(user_id,
                              text=load_text(TextLabels.UNREGISTERED, media=media),
                              marks=list([MessageMarks.UNREGISTERED]))
        messages_list = list([new_message])
        response = {'send': messages_list}
        return response

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

        response = {'send': new_messages}
        return response

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
        new_messages = {'send': list()}
        try:
            user = User(media, message.user_id)
        except UserNotFound:
            new_messages['send'].append(Message(message.user_id,
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
            messages_from_handler = message_handler.handle(state, message)
            for key in messages_from_handler.keys():
                if key in new_messages.keys():
                    new_messages[key].extend(messages_from_handler[key])
                else:
                    new_messages[key] = messages_from_handler[key]
        return new_messages

    @staticmethod
    def button_pressed(media, user_id, button, creation=False):
        new_messages = {'send': list()}
        try:
            user = User(media=media, user_id=user_id)
        except UserNotFound:
            new_messages['send'].append(Message(user_id=user_id,
                                                text=load_text(TextLabels.REGISTRATION, media=media),
                                                marks=list([MessageMarks.UNREGISTERED]))
                                        )
        else:
            button_handler = ButtonHandler(user, media)
            messages_from_handler = button_handler.handle_button(button)
            for key in messages_from_handler.keys():
                if key in new_messages.keys():
                    new_messages[key].extend(messages_from_handler[key])
                else:
                    new_messages[key] = messages_from_handler[key]

            user.set_state(media, button.following_state, creation=creation)

        return new_messages

    @staticmethod
    def callback_query_handler(media, user_id, callback_data, bot=Bots.MAIN):
        new_messages = dict()
        try:
            user = User(media=media, user_id=user_id)
        except UserNotFound:
            new_messages['send'].append(Message(user_id=user_id,
                                                text=load_text(TextLabels.REGISTRATION, media=media),
                                                marks=list([MessageMarks.UNREGISTERED]))
                                        )
        else:
            if bot == Bots.MODERATION or bot == Bots.MAIN:
                action, request_id = callback_data.split('|')
                action = ButtonActions[action]
                request_id = int(request_id)

                button_handler = ButtonHandler(user=user, media=media)
                messages_from_handler = button_handler.handle_action(action, request_id=request_id)
                for key in messages_from_handler.keys():
                    if key in new_messages.keys():
                        new_messages[key].extend(messages_from_handler[key])
                    else:
                        new_messages[key] = messages_from_handler[key]
        return new_messages

    @staticmethod
    def connect_message_to_request(media, media_user_id, bot, request_base_id, message_id):
        user = User(media=media, user_id=media_user_id)
        user.add_message_id(media=media, bot=bot, message_id=message_id, request_id=request_base_id)


class ButtonHandler:
    def __init__(self, user, media):
        self.user = user
        self.media = media

        self.button_action_methods = {ButtonActions.LOAD_STATE: self.standard,
                                      ButtonActions.SWITCH_LANGUAGE: self.switch_language,
                                      ButtonActions.FORM_MESSAGE: self.form_message,
                                      ButtonActions.ADD_TAG: self.add_tag_into_ignore,
                                      ButtonActions.DELETE_TAG: self.delete_tag_from_ignore,
                                      ButtonActions.DELETE_CURRENT_EDITED_DRAFT: self.delete_current_draft,
                                      ButtonActions.SET_DATE_TYPE: self.set_date_type,
                                      ButtonActions.ADD_TAG_TO_DRAFT: self.add_tag_to_draft,
                                      ButtonActions.DELETE_TAG_FROM_DRAFT: self.delete_tag_from_draft,
                                      ButtonActions.CREATION_SEND_SAVING_CONFIRMATION: self.send_saving_confirmation,
                                      ButtonActions.CREATION_SHOW_REQUEST_DRAFT: self.creation_show_request_draft,
                                      ButtonActions.CREATION_SUBMIT_REQUEST: self.creation_submit_request,
                                      ButtonActions.MODERATION_APPROVE_REQUEST: self.moderation_approve_request,
                                      ButtonActions.MODERATION_DISMISS_REQUEST: self.moderation_dismiss_request,
                                      ButtonActions.TAKE_REQUEST: self.take_request,
                                      ButtonActions.DECLINE_REQUEST: self.decline_request}

    def handle_button(self, button):
        new_messages = dict()
        for action in button.actions:
            action_messages = self.handle_action(action, button=button)
            for key in action_messages.keys():
                if key in new_messages.keys():
                    new_messages[key].extend(action_messages[key])
                else:
                    new_messages[key] = action_messages[key]
        return new_messages

    def handle_action(self, action, **kwargs):
        new_messages = self.button_action_methods[action](**kwargs)
        return new_messages

    def standard(self, button=None, **kwargs):
        # Обработчик для тех кнопок, которые не выполняют особых действий, а просто переводят в состояние, в
        # котором юзеру отправляется только одно соощение
        new_messages = {'send': list()}
        new_message = Message(user_id=self.user.media_id[self.media],
                              text=load_text(TextLabels[button.following_state.name], self.media,
                                             self.user.language.get(self.media, Languages.RU)),
                              keyboard=Keyboard(state=button.following_state,
                                                language=self.user.language.get(self.media, Languages.RU)))

        new_messages['send'].append(new_message)
        return new_messages

    def switch_language(self, button=None, **kwargs):
        language = Languages[button.info['language']]
        self.user.set_language(self.media, language)
        new_messages = {'send': list()}
        new_message = Message(user_id=self.user.media_id[self.media],
                              text=load_text(TextLabels.LANGUAGE_SWITCHED_SUCCESSFULLY,
                                             self.media,
                                             self.user.language.get(self.media, Languages.RU)))
        new_messages['send'].append(new_message)
        return new_messages

    def form_message(self, button=None, **kwargs):
        producer = MessageBuildingProducer(self.user, self.media)
        message_data = producer.build_message(button=button)

        new_messages = {'send': list()}
        new_message = Message(user_id=self.user.media_id[self.media],
                              text=message_data['text'],
                              keyboard=message_data['keyboard'] if message_data['keyboard']
                              else Keyboard(state=button.following_state,
                                            language=self.user.language.get(self.media, Languages.RU)))
        new_messages['send'].append(new_message)
        return new_messages

    def delete_tag_from_ignore(self, button=None, **kwargs):
        tag = button.info['tag']
        self.user.delete_tag_from_ignore(tag)
        new_messages = dict()
        return new_messages

    def add_tag_into_ignore(self, button=None, **kwargs):
        tag = button.info['tag']
        self.user.add_tag_into_ignore(tag)
        new_messages = dict()
        return new_messages

    def delete_current_draft(self, button=None, **kwargs):
        draft = self.user.get_edited_draft(self.media)
        draft.delete()

        message = Message(user_id=self.user.media_id[self.media],
                          text=load_text(TextLabels.CREATION_DRAFT_DELETED_SUCCESSFULLY,
                                         self.media,
                                         self.user.language.get(self.media, Languages.RU))
                          )
        new_messages = {'send': list()}
        new_messages['send'].append(message)
        return new_messages

    def set_date_type(self, button=None, **kwargs):
        date_type = button.info['date_type']
        request = self.user.get_edited_draft(self.media)
        request.change_date_type(date_type)
        return dict()

    def add_tag_to_draft(self, button=None, **kwargs):
        tag = button.info['tag']
        request = self.user.get_edited_draft(self.media)
        request.add_tag(tag)
        return dict()

    def delete_tag_from_draft(self, button=None, **kwargs):
        tag = button.info['tag']
        request = self.user.get_edited_draft(self.media)
        request.delete_tag(tag)
        return dict()

    def send_saving_confirmation(self, button=None, **kwargs):
        new_messages = {'send': list()}
        new_message = Message(user_id=self.user.media_id[self.media],
                              text=load_text(TextLabels.CREATION_SAVING_CONFIRMATION, self.media,
                                             self.user.language.get(self.media, Languages.RU)))
        new_messages['send'].append(new_message)
        return new_messages

    def creation_show_request_draft(self, button=None, draft_type=None, **kwargs):
        new_messages = {'send': list()}
        message_builder = MessageBuildingProducer(self.user, self.media)

        if not draft_type:
            draft_type = button.info.get('draft_to_show', 'CURRENT_EDITED')
        draft = None
        if draft_type == 'CURRENT_EDITED':
            draft = self.user.get_edited_draft(self.media)
        message_text = message_builder.build_message(text_label=TextLabels.CREATION_SHOW_REQUEST_DRAFT,
                                                     request=draft,
                                                     text_without_button=True)['text']
        new_message = Message(user_id=self.user.media_id[self.media],
                              text=message_text)
        new_messages['send'].append(new_message)
        return new_messages

    def creation_submit_request(self, **kwargs):
        new_messages = {'send': list()}
        message_builder = MessageBuildingProducer(self.user, self.media)
        request = self.user.get_edited_draft(self.media)

        moderators = User.get_id_of_all_moderators(self.media)

        for moderator_id in moderators:
            message_data = message_builder.build_message(text_label=TextLabels.MODERATION_SEND_DRAFT,
                                                         language=Languages.RU,
                                                         request=request)
            new_message = Message(user_id=moderator_id,
                                  text=message_data['text'],
                                  keyboard=message_data['keyboard'],
                                  bot=Bots.MODERATION,
                                  request_id=request.base_id,
                                  moderation=True)
            new_messages['send'].append(new_message)

        message_for_creator = Message(user_id=self.user.media_id[self.media],
                                      text=load_text(TextLabels.CREATION_SUBMIT_REQUEST, self.media,
                                                     self.user.language.get(self.media, Languages.RU))
                                      )
        new_messages['send'].append(message_for_creator)
        request.set_submission_status(True)
        self.user.clear_edited_draft_field(self.media)

        return new_messages

    def moderation_approve_request(self, request_id=None, **kwargs):
        request = Request(request_id=request_id)
        request.set_publishing_status(True)
        request.set_publisher(self.user)

        message_builder = MessageBuildingProducer(self.user, self.media)
        new_messages = {'send': list()}
        users = User.get_id_of_users_without_ignore_hashtags(media=self.media,
                                                             tags=request.tags)
        for i in users:
            keyboard = \
                message_builder.build_message(following_state=States.MAIN_REQUEST, no_text=True, request=request)[
                    'keyboard']
            message = Message(user_id=i,
                              text=request.into_human_readable(self.user.language[self.media]),
                              keyboard=keyboard,
                              bot=Bots.MAIN,
                              request_id=request.base_id,
                              main_bot=True)
            new_messages['send'].append(message)

        creator = request.get_creator()
        message_data = message_builder.build_message(text_label=TextLabels.CREATION_PUBLICATION_NOTIFICATION,
                                                     request=request)
        message = Message(user_id=creator.media_id[self.media],
                          text=message_data['text'],
                          bot=Bots.CREATION)
        new_messages['send'].append(message)

        new_messages['delete'] = list()
        moderators = User.get_id_of_all_moderators(media=self.media)
        for moderator_id in moderators:
            moder = User(user_id=moderator_id, media=self.media)
            message_id = moder.get_message_id_by_request_id(media=self.media,
                                                            bot=Bots.MODERATION,
                                                            request_base_id=request.base_id)
            message_to_delete = Message(media_id=message_id,
                                        user_id=moder.media_id[self.media],
                                        bot=Bots.MODERATION)
            new_messages['delete'].append(message_to_delete)
        return new_messages

    def moderation_dismiss_request(self, request_id=None, **kwargs):
        request = Request(request_id=request_id)
        request.set_submission_status(False)

        message_builder = MessageBuildingProducer(self.user, self.media)
        new_messages = {'send': list()}

        creator = request.get_creator()
        message_data = message_builder.build_message(text_label=TextLabels.CREATION_REQUEST_DISMISSED_NOTIFICATION,
                                                     request=request)
        message = Message(user_id=creator.media_id[self.media],
                          text=message_data['text'],
                          bot=Bots.CREATION)
        new_messages['send'].append(message)

        new_messages['delete'] = list()
        moderators = User.get_id_of_all_moderators(media=self.media)
        for moderator_id in moderators:
            moder = User(user_id=moderator_id, media=self.media)
            message_id = moder.get_message_id_by_request_id(media=self.media,
                                                            bot=Bots.MODERATION,
                                                            request_base_id=request.base_id)
            message_to_delete = Message(media_id=message_id,
                                        user_id=moder.media_id[self.media],
                                        bot=Bots.MODERATION)
            new_messages['delete'].append(message_to_delete)
        return new_messages

    def take_request(self, request_id=None, **kwargs):
        request = Request(request_id=request_id)
        self.user.take_request(request)
        request.load_from_server()

        creator = request.get_creator()

        message_builder = MessageBuildingProducer(self.user, self.media)
        new_messages = {'send': list(), 'delete': list()}

        notification_data = message_builder.build_message(text_label=TextLabels.NEW_EXECUTOR_NOTIFICATION,
                                                          request=request)
        notification_message = Message(user_id=creator.media_id[self.media],
                                       text=notification_data['text'],
                                       bot=Bots.CREATION)
        new_messages['send'].append(notification_message)

        id_of_message_to_delete = self.user.get_message_id_by_request_id(request_base_id=request.base_id,
                                                                         media=self.media,
                                                                         bot=Bots.MAIN)
        message_to_delete = Message(user_id=self.user.media_id[self.media],
                                    media_id=id_of_message_to_delete,
                                    bot=Bots.MAIN)
        new_messages['delete'].append(message_to_delete)

        notification_for_executor_data = message_builder.build_message(
            text_label=TextLabels.TAKING_CONFIRMATION_FOR_EXECUTOR,
            request=request)
        notification_for_executor = Message(user_id=self.user.media_id[self.media],
                                            text=notification_for_executor_data['text'],
                                            bot=Bots.MAIN)
        new_messages['send'].append(notification_for_executor)

        if request.has_enough_executors():
            if request.get_people_number() > 1:
                notification_for_creator_data = message_builder.build_message(
                    text_label=TextLabels.ENOUGH_EXECUTORS_NOTIFICATION,
                    request=request,
                    executors=request.get_executors())
                notification_for_creator = Message(user_id=creator.media_id[self.media],
                                                   text=notification_for_creator_data['text'],
                                                   bot=Bots.CREATION)
                new_messages['send'].append(notification_for_creator)

            ids_of_messages_to_delete = User.get_ids_of_messages_to_delete_for_enough_executors(request=request,
                                                                                                media=self.media,
                                                                                                bot=Bots.MAIN)
            for user_id in ids_of_messages_to_delete.keys():
                message_to_delete = Message(user_id=user_id,
                                            media_id=ids_of_messages_to_delete[user_id],
                                            bot=Bots.MAIN)
                new_messages['delete'].append(message_to_delete)

        return new_messages

    def decline_request(self, request_id=None, **kwargs):
        request = Request(request_id=request_id)
        self.user.decline_request(request)

        new_messages = {'send': list(), 'delete': list()}
        message_id = self.user.get_message_id_by_request_id(media=self.media,
                                                            bot=Bots.MAIN,
                                                            request_base_id=request.base_id)
        message = Message(user_id=self.user.media_id[self.media], media_id=message_id)
        new_messages['delete'].append(message)

        return new_messages


class MessageBuildingProducer:
    def __init__(self, user, media):
        self.user = user
        self.media = media

        self.FUNCTIONS_FOR_FORMATION = {TextLabels.IGNORE_SETTINGS: self.ignore_lists_messages,
                                        TextLabels.CHOSE_TAG_DELETION: self.chose_tag_to_edit,
                                        TextLabels.CHOSE_TAG_ADDING: self.chose_tag_to_edit,
                                        TextLabels.TAG_ADDED_INTO_IGNORE: self.chose_tag_to_edit,
                                        TextLabels.TAG_DELETED_FROM_IGNORE: self.chose_tag_to_edit,
                                        TextLabels.REQUESTS_I_TOOK_PENDING: self.requests_i_took_list,
                                        TextLabels.REQUESTS_I_TOOK_FULFILLED: self.requests_i_took_list,
                                        TextLabels.CREATION_SET_DATE: self.creation_set_date,
                                        TextLabels.CREATION_SET_TAGS: self.creation_set_tags,
                                        TextLabels.CREATION_TAG_ADDED_TO_DRAFT: self.creation_tag_added_or_deleted,
                                        TextLabels.CREATION_TAG_DELETED_FROM_DRAFT: self.creation_tag_added_or_deleted,
                                        TextLabels.CREATION_SHOW_REQUEST_DRAFT: self.creation_show_request_draft,
                                        TextLabels.MODERATION_SEND_DRAFT: self.moderation_send_draft,
                                        TextLabels.MAIN_REQUEST: self.request_inline_keyboard,
                                        TextLabels.CREATION_PUBLICATION_NOTIFICATION: self.creation_publication_notification,
                                        TextLabels.CREATION_REQUEST_DISMISSED_NOTIFICATION: self.creation_request_dismissed,
                                        TextLabels.NEW_EXECUTOR_NOTIFICATION: self.new_executor_notification,
                                        TextLabels.TAKING_CONFIRMATION_FOR_EXECUTOR: self.taking_confirmation_for_executor,
                                        TextLabels.ENOUGH_EXECUTORS_NOTIFICATION: self.enough_executors_notification,
                                        TextLabels.CREATION_DRAFTS_LIST: self.creation_requests_lists,
                                        TextLabels.CREATION_REQUESTS_ON_MODERATION_LIST: self.creation_requests_lists,
                                        TextLabels.CREATION_REQUESTS_WAITING_TO_BE_DONE_LIST: self.creation_requests_lists,
                                        TextLabels.CREATION_FINISHED_REQUESTS_LIST: self.creation_requests_lists
                                        }

    @staticmethod
    def get_features_for_formation(type_of_features):
        data = load_features_for_formation()
        return data[type_of_features]

    def build_message(self, button=None, following_state=None, text_label=None, no_text=False, **kwargs):
        if button:
            text_label = TextLabels[button.info['message_type']]
        elif following_state:
            text_label = TextLabels[following_state.name]
        data = self.FUNCTIONS_FOR_FORMATION[text_label](button=button, following_state=following_state, **kwargs)
        if data.get('change_label', None):
            text_label = data['change_label']
        if button and not button.info.get('no_text', False) or not no_text:
            message_text = load_text(text_label,
                                     self.media,
                                     kwargs.get('language', self.user.language.get(self.media, Languages.RU)))
            res_message_text = message_text.format(**data['text'])
        else:
            res_message_text = ''
        return {'text': res_message_text, 'keyboard': data.get('keyboard', None)}

    def ignore_lists_messages(self, button=None, **kwargs):
        ignored = self.user.get_ignored_hashtags_text(self.media)
        subscription = self.user.get_subscription_hashtags_text(self.media)

        keyboard_data = Keyboard.load_keyboard(button.following_state.name)

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

    def chose_tag_to_edit(self, button=None, **kwargs):
        new_button_state = ''
        tags = list()
        if button.following_state == States.CHOSE_TAG_ADDING:
            new_button_state = 'CHOSE_TAG_ADDING'
            tags = self.user.subscription_hashtags()
        elif button.following_state == States.CHOSE_TAG_DELETION:
            new_button_state = 'CHOSE_TAG_DELETION'
            tags = self.user.ignored_tags
        keyboard = Keyboard.load_keyboard(button.following_state.name)
        if len(tags) > 10:
            right_border = (button.info['page'] + 1) * 7
            if right_border > len(tags):
                right_border = len(tags)
            left_border = (button.info['page'] * 7)
            tags = tags[left_border:right_border]
            keyboard['buttons'][1][0]['info']['page'] = button.info['page'] - 1
            keyboard['buttons'][1][1]['info']['page'] = button.info['page'] + 1
            if button.info['page'] == 0:
                del keyboard['buttons'][1][0]
                keyboard['buttons'][1][0]['info']['page'] = 1
            elif button.info['page'] * 7 >= len(tags):
                del keyboard['buttons'][1][1]
        else:
            del keyboard['buttons'][1]
        button_template = keyboard['buttons'][0][0]
        del keyboard['buttons'][0]
        for tag in tags:
            new_button = copy.deepcopy(button_template)

            for l in list(Languages):
                new_button[l.name] = '–' + tag_into_text([tag], l)[0] + '–'
            new_button['state'] = new_button_state
            new_button['info']['tag'] = tag
            keyboard['buttons'].insert(0, [new_button])

        res = {'text': {},
               'keyboard': Keyboard(language=self.user.language.get(self.media, Languages.RU),
                                    json_set=keyboard)}
        return res

    def creation_set_date(self, button=None, **kwargs):
        request = self.user.get_edited_draft(self.media)
        features = self.__class__.get_features_for_formation('CREATION_SET_DATE')
        res = {'text': dict()}
        res['text']['date_word'] = features['date_word'][request.date_type.name][self.user.language[self.media].name]

        res['keyboard'] = Keyboard(state=button.following_state, language=self.user.language[self.media])

        return res

    def creation_set_tags(self, button=None, following_state=None, **kwargs):
        request = self.user.get_edited_draft(self.media)
        tags = list(HashTags)
        tags.sort(key=lambda x: (x in request.tags))

        if button:
            keyboard = Keyboard.load_keyboard(button.following_state.name)
        elif following_state:
            keyboard = Keyboard.load_keyboard(following_state.name)
        else:
            keyboard = None  # This should never happen, but just in case
        if len(tags) > 10:
            if button:
                page = button.info['page']
            else:
                page = 0
            right_border = (page + 1) * 7
            if right_border > len(tags):
                right_border = len(tags)
            left_border = (page * 7)
            tags = tags[left_border:right_border]
            keyboard['buttons'][2][0]['info']['page'] = page - 1
            keyboard['buttons'][2][1]['info']['page'] = page + 1

            if page == 0:
                del keyboard['buttons'][2][0]
            elif page * 7 >= len(tags):
                del keyboard['buttons'][2][1]
        else:
            del keyboard['buttons'][2]
        button_addition_template = keyboard['buttons'][0][0]
        button_deletion_template = keyboard['buttons'][1][0]
        del keyboard['buttons'][0:2]
        action_texts = get_action_text_for_creation()
        for tag in tags:
            if tag in request.tags:
                new_button = copy.deepcopy(button_deletion_template)
            else:
                new_button = copy.deepcopy(button_addition_template)
            for l in list(Languages):
                action_text = action_texts[new_button['info']['actions'][0]][l.name]
                new_button[l.name] = '–- ' + action_text + '"' + tag_into_text([tag], l)[0] + '"' + ' -–'
            new_button['info']['tag'] = tag
            keyboard['buttons'].insert(0, [new_button])

        res = {'text': {},
               'keyboard': Keyboard(language=self.user.language.get(self.media, Languages.RU),
                                    json_set=keyboard)}
        return res

    def creation_tag_added_or_deleted(self, button=None, **kwargs):
        tag = button.info['tag']
        tag_text = tag_into_text([tag], self.user.language[self.media])[0]
        text = {'tag': tag_text}
        keyboard = self.creation_set_tags(button=button)['keyboard']
        return {'text': text, 'keyboard': keyboard}

    def creation_show_request_draft(self, request=None, **kwargs):
        res_text = request.into_human_readable(language=self.user.language.get(self.media, Languages.RU))
        return {'text': {'request': res_text}, 'keyboard': None}

    def moderation_send_draft(self, request=None, **kwargs):
        result = self.creation_show_request_draft(request=request)
        keyboard = Keyboard.load_keyboard("MODERATION_SEND_DRAFT")
        for i in range(len(keyboard['buttons'][0])):
            keyboard['buttons'][0][i]['info']['request'] = request.id
            keyboard['buttons'][0][i]['info']['callback_data'] = ' '.join(
                keyboard['buttons'][0][i]['info']['actions']) + '|' + str(request.id)
        result['keyboard'] = Keyboard(language=self.user.language.get(self.media, Languages.RU), json_set=keyboard)
        return result

    def request_inline_keyboard(self, request=None, **kwargs):
        result = {'text': None}
        keyboard = Keyboard.load_keyboard("MAIN_REQUEST")
        for i in range(len(keyboard['buttons'][0])):
            keyboard['buttons'][0][i]['info']['request'] = request.id
            keyboard['buttons'][0][i]['info']['callback_data'] = ' '.join(
                keyboard['buttons'][0][i]['info']['actions']) + '|' + str(request.id)
        result['keyboard'] = Keyboard(language=self.user.language.get(self.media, Languages.RU), json_set=keyboard)
        return result

    def creation_publication_notification(self, request=None, **kwargs):
        return {'text': {'request_name': request.name}}

    def creation_request_dismissed(self, request=None, **kwargs):
        return {'text': {'request_name': request.name}}

    def new_executor_notification(self, request=None, **kwargs):
        request_name = request.name
        contact_info = self.user.get_contact_card(self.media)
        return {'text': {'request_name': request_name, 'contacts': contact_info}, 'keyboard': None}

    def taking_confirmation_for_executor(self, request=None, **kwargs):
        request_name = request.name
        return {'text': {'request_name': request_name}, 'keyboard': None}

    def enough_executors_notification(self, request, executors, **kwargs):
        users_cards = [e.get_contact_card(self.media) for e in executors]
        contact_info = '\n––––––––––––––––––––––––'.join(users_cards).strip()
        request_name = request.name
        return {'text': {'request_name': request_name, 'contacts': contact_info}, 'keyboard': None}

    def requests_i_took_list(self, button=None, **kwargs):
        res = {'text': dict()}
        keyboard = Keyboard.load_keyboard(button.following_state.name)

        requests = self.user.get_taken_requests()
        if button.following_state == States.REQUESTS_I_TOOK_PENDING:
            requests = list(filter(lambda r: (not r.is_expired()), requests))
        elif button.following_state == States.REQUESTS_I_TOOK_FULFILLED:
            requests = list(filter(lambda r: r.is_expired(), requests))

        if len(requests) > 5:
            right_border = (button.info['page'] + 1) * 5
            if right_border > len(requests):
                right_border = len(requests)
            left_border = (button.info['page'] * 5)
            requests = requests[left_border:right_border]
            keyboard['buttons'][1][0]['info']['page'] = button.info['page'] - 1
            keyboard['buttons'][1][1]['info']['page'] = button.info['page'] + 1
            if button.info['page'] == 0:
                del keyboard['buttons'][1][0]
                keyboard['buttons'][1][0]['info']['page'] = 1
            elif button.info['page'] * 5 >= len(requests):
                del keyboard['buttons'][1][1]
        else:
            del keyboard['buttons'][1]
        button_template = keyboard['buttons'][0][0]
        del keyboard['buttons'][0]
        for req in requests:
            new_button = copy.deepcopy(button_template)
            for l in list(Languages):
                new_button[l.name] = req.name
            new_button['state'] = button.following_state.name
            new_button['info']['request_base_is'] = req.base_id
            keyboard['buttons'].insert(0, [new_button])
        res['keyboard'] = Keyboard(language=self.user.language.get(self.media, Languages.RU),
                                   json_set=keyboard)
        return res

    def creation_requests_lists(self, button=None, **kwargs):
        all_requests = self.user.get_created_requests()
        requests = list()
        if button.following_state == States.CREATION_DRAFTS_LIST:
            sort_function = lambda r: not r.__dict__.get('was_submited', False)
            requests = list(filter(sort_function, all_requests))
        elif button.following_state == States.CREATION_REQUESTS_ON_MODERATION_LIST:
            sort_function = lambda r: r.__dict__.get('was_submited', False) and \
                                      not r.__dict__.get('was_published', False)
            requests = list(filter(sort_function, all_requests))
        elif button.following_state == States.CREATION_REQUESTS_WAITING_TO_BE_DONE_LIST:
            sort_function = lambda r: r.__dict__.get('was_published', False) and \
                                      not r.__dict__.get('was_executed', False) and not r.is_expired()
            requests = list(filter(sort_function, all_requests))
        elif button.following_state == States.CREATION_FINISHED_REQUESTS_LIST:
            sort_function = lambda r: r.__dict__.get('was_executed', False) or r.is_expired()
            requests = list(filter(sort_function, all_requests))

        if button.following_state == States.CREATION_DRAFTS_LIST:
            keyboard = Keyboard.load_keyboard(button.following_state.name)
        else:
            keyboard = Keyboard.load_keyboard('CREATION_REQUESTS_LIST')

        if len(requests) == 0:
            print('here')
            keyboard['buttons'] = keyboard['buttons'][-1:]
            feqtures_for_formaion = self.get_features_for_formation('CREATION_LISTS_OF_REQUESTS_NAMES')[
                button.following_state.name]
            res = {'text': {'list_name': feqtures_for_formaion[self.user.language.get(self.media, Languages.RU).name]},
                   'keyboard': Keyboard(language=self.user.language.get(self.media, Languages.RU),
                                        json_set=keyboard),
                   'change_label': TextLabels.CREATION_REQUESTS_LIST_IS_EMPTY}
            return res
        elif len(requests) > 5:
            right_border = (button.info['page'] + 1) * 5
            if right_border > len(requests):
                right_border = len(requests)
            left_border = (button.info['page'] * 5)
            requests = requests[left_border:right_border]
            keyboard['buttons'][1][0]['info']['page'] = button.info['page'] - 1
            keyboard['buttons'][1][1]['info']['page'] = button.info['page'] + 1
            if button.info['page'] == 0:
                del keyboard['buttons'][1][0]
                keyboard['buttons'][1][0]['info']['page'] = 1
            elif button.info['page'] * 5 >= len(requests):
                del keyboard['buttons'][1][1]
        else:
            del keyboard['buttons'][1]

        button_template = keyboard['buttons'][0][0]
        del keyboard['buttons'][0]
        for req in requests:
            new_button = copy.deepcopy(button_template)
            for l in list(Languages):
                new_button[l.name] = req.name
            if button.following_state != States.CREATION_DRAFTS_LIST:
                new_button['state'] = button.following_state.name
            new_button['info']['request_base_is'] = req.base_id
            keyboard['buttons'].insert(0, [new_button])
        res = {'text': dict()}
        res['keyboard'] = Keyboard(language=self.user.language.get(self.media, Languages.RU),
                                   json_set=keyboard)
        return res


class MessageHandler:
    def __init__(self, user, media):
        self.user = user
        self.media = media

        self.message_handlers = {States.MAIN_MENU: self.ignore_handler,
                                 States.CREATION_NEW_REQUEST: self.create_new_request,
                                 States.CREATION_TYPE_TEXT: self.edit_text,
                                 States.CREATION_SET_DATE: self.set_date,
                                 States.CREATION_SET_PEOPLE_NUMBER: self.set_people_number}

    def handle(self, state, message):
        handler = self.message_handlers.get(state, None)
        if not handler:
            handler = self.ignore_handler
        res = handler(message)
        return res

    def ignore_handler(self, message):
        response = dict()
        return response

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

        response = {'send': new_messages}
        return response

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

        response = {'send': new_messages}
        return response

    def set_date(self, message):
        text = message.text
        request = self.user.get_edited_draft(self.media)
        new_messages = list()
        try:
            request.set_date(text)
        except DateFormatError:
            new_message = Message(self.user.media_id[self.media],
                                  text=load_text(TextLabels.CREATION_SET_DATE_FORMAT_ERROR,
                                                 media=self.media,
                                                 language=self.user.language[self.media]),
                                  keyboard=Keyboard(state=self.user.state[self.media],
                                                    language=self.user.language.get(self.media, Languages.RU)))
        except EarlyDate:
            new_message = Message(self.user.media_id[self.media],
                                  text=load_text(TextLabels.CREATION_SET_DATE_EARLY_DATE,
                                                 media=self.media,
                                                 language=self.user.language[self.media]),
                                  keyboard=Keyboard(state=self.user.state[self.media],
                                                    language=self.user.language.get(self.media, Languages.RU)))
        except WrongDateOrder:
            new_message = Message(self.user.media_id[self.media],
                                  text=load_text(TextLabels.CREATION_SET_DATE_WRONG_DATE_ORDER,
                                                 media=self.media,
                                                 language=self.user.language[self.media]),
                                  keyboard=Keyboard(state=self.user.state[self.media],
                                                    language=self.user.language.get(self.media, Languages.RU)))
        else:
            next_state = States.CREATION_SET_PEOPLE_NUMBER
            new_message = Message(self.user.media_id[self.media],
                                  text=load_text(TextLabels[next_state.name],
                                                 media=self.media,
                                                 language=self.user.language[self.media]),
                                  keyboard=Keyboard(state=next_state,
                                                    language=self.user.language.get(self.media, Languages.RU)))
            self.user.set_state(self.media, next_state, creation=True)
        new_messages.append(new_message)

        response = {'send': new_messages}
        return response

    def set_people_number(self, message):
        text = message.text
        request = self.user.get_edited_draft(self.media)
        new_messages = list()
        try:
            request.set_people_number(int(text))
        except ValueError:
            print_exc()
            new_message = Message(self.user.media_id[self.media],
                                  text=load_text(States.CREATION_SET_PEOPLE_NUMBER,
                                                 media=self.media,
                                                 language=self.user.language[self.media]),
                                  keyboard=Keyboard(state=States.CREATION_SET_PEOPLE_NUMBER,
                                                    language=self.user.language.get(self.media, Languages.RU)))
        else:
            next_state = States.CREATION_SET_TAGS
            building_producer = MessageBuildingProducer(self.user, self.media)
            message_data = building_producer.build_message(following_state=next_state)
            new_message = Message(self.user.media_id[self.media],
                                  text=load_text(TextLabels[next_state.name],
                                                 media=self.media,
                                                 language=self.user.language[self.media]),
                                  keyboard=message_data['keyboard'])
            self.user.set_state(self.media, next_state, creation=True)
        new_messages.append(new_message)

        response = {'send': new_messages}
        return response
