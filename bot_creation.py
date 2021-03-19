from bot import Bot
from user import User
from message import Message
from exceptions import UserNotFound
from extensions import load_text
from keyboard import Keyboard
from enumerates import TextLabels, States, MessageMarks, Languages


class CreationBot(Bot):

    @staticmethod
    def start_conversation(media, user_id, user_contact_link=''):
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
            user.clear_edited_draft_field(media=media)
        response = {'send': list([new_message])}
        return response

    @staticmethod
    def unregistered(media, user_id):
        new_message = Message(user_id,
                              text=load_text(TextLabels.CREATION_UNREGISTERED, media=media),
                              marks=list([MessageMarks.UNREGISTERED]))
        response = {'send': list([new_message])}
        return response
