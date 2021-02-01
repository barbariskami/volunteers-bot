from bot import Bot
from user import User
from message import Message
from exceptions import UserNotFound
from extensions import load_text
from enumerates import TextLabels, States, MessageMarks


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
