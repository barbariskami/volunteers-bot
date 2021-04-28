from bot import Bot
from request import Request
from user import User
from message import Message
from exceptions import UserNotFound, TagNotFound, TagCodeValueError, TagNotAllLanguages, TagDuplicateValue
from extensions import load_text
from enumerates import TextLabels, States, MessageMarks, Media, Languages
from tag import Tag


class ModerationBot(Bot):

    @staticmethod
    def start_conversation(media, user_id, user_contact_link=''):
        try:
            user = User(media=media, user_id=user_id)
        except UserNotFound:
            new_message = Message(user_id, text=load_text(TextLabels.MODERATION_UNREGISTERED, media=media),
                                  marks=[MessageMarks.UNREGISTERED])
        else:
            if user.is_moderator:
                new_message = Message(user_id,
                                      text=load_text(TextLabels.MODERATION_GREETING,
                                                     media=media,
                                                     language=user.language[media]))
                user.set_state(media, States.MODERATION_MAIN_MENU, moderation=True)
            else:
                new_message = Message(user_id,
                                      text=load_text(TextLabels.MODERATION_ACCESS_DENIED,
                                                     media=media,
                                                     language=user.language[media]),
                                      marks=[MessageMarks.NO_ACCESS])
        response = {'send': list([new_message])}
        return response

    @staticmethod
    def unregistered(media, user_id):
        new_message = Message(user_id,
                              text=load_text(TextLabels.MODERATION_UNREGISTERED, media=media),
                              marks=list([MessageMarks.UNREGISTERED]))
        response = {'send': list([new_message])}
        return response

    @staticmethod
    def no_access(media, user_id):
        new_message = Message(user_id,
                              text=load_text(TextLabels.MODERATION_ACCESS_DENIED, media=media),
                              marks=list([MessageMarks.NO_ACCESS]))
        response = {'send': list([new_message])}
        return response

    @staticmethod
    def get_all_tags(media, user_id):
        try:
            user = User(media=media, user_id=user_id)
        except UserNotFound:
            new_message = Message(user_id, text=load_text(TextLabels.MODERATION_UNREGISTERED, media=media),
                                  marks=[MessageMarks.UNREGISTERED])
            response = {'send': list([new_message])}
            return response
        if not user.is_admin:
            new_message = Message(user_id,
                                  text=load_text(TextLabels.MODERATION_ACCESS_DENIED,
                                                 media=media,
                                                 language=user.language[media]),
                                  marks=[MessageMarks.NO_ACCESS])
            response = {'send': list([new_message])}
            return response
        tags = sorted(Tag.get_all_tags(), key=lambda x: not x.is_shown)
        marks = {True: '+', False: '-'}
        tags_strings = [marks[t.is_shown] + ' ' + t.code for t in tags]
        message_text = load_text(TextLabels.MODERATION_GET_ALL_TAGS, media=media).format(tags='\n'.join(tags_strings))
        if media == Media.TELEGRAM:
            message_text = message_text.replace('_', '\_')
        new_message = Message(user_id,
                              text=message_text)
        response = {'send': list([new_message])}
        return response

    @staticmethod
    def get_tag_info(media, user_id, code):
        try:
            user = User(media=media, user_id=user_id)
        except UserNotFound:
            new_message = Message(user_id, text=load_text(TextLabels.MODERATION_UNREGISTERED, media=media),
                                  marks=[MessageMarks.UNREGISTERED])
            response = {'send': list([new_message])}
            return response
        if not user.is_admin:
            new_message = Message(user_id,
                                  text=load_text(TextLabels.MODERATION_ACCESS_DENIED,
                                                 media=media,
                                                 language=user.language[media]),
                                  marks=[MessageMarks.NO_ACCESS])
            response = {'send': list([new_message])}
            return response
        if not code:
            new_message = Message(user_id,
                                  text=load_text(TextLabels.WRONG_COMMAND_SIGNATURE,
                                                 media=media))
            response = {'send': list([new_message])}
            return response
        try:
            tag = Tag(code=code)
        except TagNotFound:
            new_message = Message(user_id,
                                  text=load_text(TextLabels.MODERATION_WRONG_TAG_CODE,
                                                 media=media))
            response = {'send': list([new_message])}
            return response
        marks = {True: 'да', False: 'нет'}
        message_text = load_text(TextLabels.MODERATION_GET_TAG_INFO, media=media)
        lang_args = {l.name.lower(): tag.text[l] for l in Languages}
        print(lang_args)
        message_text = message_text.format(code=tag.code, is_shown=marks[tag.is_shown], **lang_args)
        if media == Media.TELEGRAM:
            message_text = message_text.replace('_', '\_')
        new_message = Message(user_id,
                              text=message_text)
        response = {'send': list([new_message])}
        return response

    @staticmethod
    def change_tag_condition(media, user_id, code):
        try:
            user = User(media=media, user_id=user_id)
        except UserNotFound:
            new_message = Message(user_id, text=load_text(TextLabels.MODERATION_UNREGISTERED, media=media),
                                  marks=[MessageMarks.UNREGISTERED])
            response = {'send': list([new_message])}
            return response
        if not user.is_admin:
            new_message = Message(user_id,
                                  text=load_text(TextLabels.MODERATION_ACCESS_DENIED,
                                                 media=media,
                                                 language=user.language[media]),
                                  marks=[MessageMarks.NO_ACCESS])
            response = {'send': list([new_message])}
            return response
        if not code:
            new_message = Message(user_id,
                                  text=load_text(TextLabels.WRONG_COMMAND_SIGNATURE,
                                                 media=media))
            response = {'send': list([new_message])}
            return response
        try:
            tag = Tag(code=code)
        except TagNotFound:
            new_message = Message(user_id,
                                  text=load_text(TextLabels.MODERATION_WRONG_TAG_CODE,
                                                 media=media))
            response = {'send': list([new_message])}
            return response
        new_state = tag.switch_state()
        marks = {True: 'показывается', False: 'не показывается'}
        message_text = load_text(TextLabels.MODERATION_TAG_STATE_SWITCHED, media=media)
        message_text = message_text.format(code=tag.code, state=marks[new_state])
        if media == Media.TELEGRAM:
            message_text = message_text.replace('_', '\_')
        new_message = Message(user_id,
                              text=message_text)
        response = {'send': list([new_message])}
        return response

    @staticmethod
    def add_tag(media, user_id, code, languages):
        try:
            user = User(media=media, user_id=user_id)
        except UserNotFound:
            new_message = Message(user_id, text=load_text(TextLabels.MODERATION_UNREGISTERED, media=media),
                                  marks=[MessageMarks.UNREGISTERED])
            response = {'send': list([new_message])}
            return response
        if not user.is_admin:
            new_message = Message(user_id,
                                  text=load_text(TextLabels.MODERATION_ACCESS_DENIED,
                                                 media=media,
                                                 language=user.language[media]),
                                  marks=[MessageMarks.NO_ACCESS])
            response = {'send': list([new_message])}
            return response
        if not code or not languages or None in languages.values():
            new_message = Message(user_id,
                                  text=load_text(TextLabels.WRONG_COMMAND_SIGNATURE,
                                                 media=media))
            response = {'send': list([new_message])}
            return response
        try:
            tag = Tag.new(code, languages)
        except TagCodeValueError:
            message_text = load_text(TextLabels.MODERATION_TAG_CODE_VALUE_ERROR,
                                     media=media)
        except TagNotAllLanguages:
            message_text = load_text(TextLabels.MODERATION_TAG_NOT_ALL_LANGUAGES,
                                     media=media)
        except TagDuplicateValue:
            message_text = load_text(TextLabels.MODERATION_TAG_DUPLICATE_VALUE,
                                     media=media)
        else:
            message_text = load_text(TextLabels.MODERATION_TAG_ADDED, media=media).format(tag=tag.code)
        if media == Media.TELEGRAM:
            message_text = message_text.replace('_', '\_')
        new_message = Message(user_id,
                              text=message_text)
        response = {'send': list([new_message])}
        return response

    @staticmethod
    def delete_tag(media, user_id, code):
        try:
            user = User(media=media, user_id=user_id)
        except UserNotFound:
            new_message = Message(user_id, text=load_text(TextLabels.MODERATION_UNREGISTERED, media=media),
                                  marks=[MessageMarks.UNREGISTERED])
            response = {'send': list([new_message])}
            return response
        if not user.is_admin:
            new_message = Message(user_id,
                                  text=load_text(TextLabels.MODERATION_ACCESS_DENIED,
                                                 media=media,
                                                 language=user.language[media]),
                                  marks=[MessageMarks.NO_ACCESS])
            response = {'send': list([new_message])}
            return response
        if not code:
            new_message = Message(user_id,
                                  text=load_text(TextLabels.WRONG_COMMAND_SIGNATURE,
                                                 media=media))
            response = {'send': list([new_message])}
            return response
        try:
            tag = Tag(code)
        except TagNotFound:
            message_text = load_text(TextLabels.MODERATION_WRONG_TAG_CODE,
                                     media=media)
        else:
            tag.delete()
            message_text = load_text(TextLabels.MODERATION_TAG_DELETED, media=media).format(tag=tag.code)
        if media == Media.TELEGRAM:
            message_text = message_text.replace('_', '\_')
        new_message = Message(user_id,
                              text=message_text)
        response = {'send': list([new_message])}
        return response

    @staticmethod
    def assign_status(media, user_id, new_moderator_id, moderator=False, admin=False):
        try:
            user = User(media=media, user_id=user_id)
        except UserNotFound:
            new_message = Message(user_id, text=load_text(TextLabels.MODERATION_UNREGISTERED, media=media),
                                  marks=[MessageMarks.UNREGISTERED])
            response = {'send': list([new_message])}
            return response
        if not user.is_admin:
            new_message = Message(user_id,
                                  text=load_text(TextLabels.MODERATION_ACCESS_DENIED,
                                                 media=media,
                                                 language=user.language[media]),
                                  marks=[MessageMarks.NO_ACCESS])
            response = {'send': list([new_message])}
            return response
        if not new_moderator_id:
            new_message = Message(user_id,
                                  text=load_text(TextLabels.WRONG_COMMAND_SIGNATURE,
                                                 media=media))
            response = {'send': list([new_message])}
            return response
        try:
            new_moderator = User(base_id=new_moderator_id)
            if moderator:
                new_moderator.assign_moderator()
            elif admin:
                new_moderator.assign_admin()
        except UserNotFound:
            message_text = load_text(TextLabels.MODERATION_INVALID_USER_ID,
                                     media=media)
        else:
            if moderator:
                message_text = load_text(TextLabels.MODERATION_M_STATUS_ASSIGNED,
                                         media=media).format(user=user.name)
            elif admin:
                message_text = load_text(TextLabels.MODERATION_A_STATUS_ASSIGNED,
                                         media=media).format(user=user.name)
            else:
                return
        new_message = Message(user_id,
                              text=message_text)
        response = {'send': list([new_message])}
        return response

    @staticmethod
    def withdraw_status(media, user_id, user_to_withdraw, moderator=False, admin=False):
        try:
            user = User(media=media, user_id=user_id)
        except UserNotFound:
            new_message = Message(user_id, text=load_text(TextLabels.MODERATION_UNREGISTERED, media=media),
                                  marks=[MessageMarks.UNREGISTERED])
            response = {'send': list([new_message])}
            return response
        if not user.is_admin:
            new_message = Message(user_id,
                                  text=load_text(TextLabels.MODERATION_ACCESS_DENIED,
                                                 media=media,
                                                 language=user.language[media]),
                                  marks=[MessageMarks.NO_ACCESS])
            response = {'send': list([new_message])}
            return response
        if not user_to_withdraw:
            new_message = Message(user_id,
                                  text=load_text(TextLabels.WRONG_COMMAND_SIGNATURE,
                                                 media=media))
            response = {'send': list([new_message])}
            return response
        try:
            new_moderator = User(base_id=user_to_withdraw)
            if moderator:
                new_moderator.withdraw_moderator()
            elif admin:
                new_moderator.withdraw_admin()
        except UserNotFound:
            message_text = load_text(TextLabels.MODERATION_INVALID_USER_ID,
                                     media=media)
        else:
            if moderator:
                message_text = load_text(TextLabels.MODERATION_M_STATUS_ASSIGNED,
                                         media=media).format(user=user.name)
            elif admin:
                message_text = load_text(TextLabels.MODERATION_A_STATUS_ASSIGNED,
                                         media=media).format(user=user.name)
            else:
                return
        new_message = Message(user_id,
                              text=message_text)
        response = {'send': list([new_message])}
        return response

    @staticmethod
    def get_all_users_csv(media, user_id):
        try:
            user = User(media=media, user_id=user_id)
        except UserNotFound:
            new_message = Message(user_id, text=load_text(TextLabels.MODERATION_UNREGISTERED, media=media),
                                  marks=[MessageMarks.UNREGISTERED])
            response = {'send': list([new_message])}
            return response
        if not user.is_admin:
            new_message = Message(user_id,
                                  text=load_text(TextLabels.MODERATION_ACCESS_DENIED,
                                                 media=media,
                                                 language=user.language[media]),
                                  marks=[MessageMarks.NO_ACCESS])
            response = {'send': list([new_message])}
            return response
        file = User.create_csv_file()
        first_message = Message(user_id,
                                text=load_text(TextLabels.MODERATION_GET_ALL_USERS_DATA,
                                               media=media))
        second_message = Message(user_id,
                                 text=None,
                                 file=file)
        response = {'send': list([first_message, second_message])}
        return response

    @staticmethod
    def get_all_requests_csv(media, user_id):
        try:
            user = User(media=media, user_id=user_id)
        except UserNotFound:
            new_message = Message(user_id, text=load_text(TextLabels.MODERATION_UNREGISTERED, media=media),
                                  marks=[MessageMarks.UNREGISTERED])
            response = {'send': list([new_message])}
            return response
        if not user.is_admin:
            new_message = Message(user_id,
                                  text=load_text(TextLabels.MODERATION_ACCESS_DENIED,
                                                 media=media,
                                                 language=user.language[media]),
                                  marks=[MessageMarks.NO_ACCESS])
            response = {'send': list([new_message])}
            return response
        file = Request.create_csv_file()
        first_message = Message(user_id,
                                text=load_text(TextLabels.MODERATION_GET_ALL_REQUESTS_DATA,
                                               media=media))
        second_message = Message(user_id,
                                 text=None,
                                 file=file)
        response = {'send': list([first_message, second_message])}
        return response