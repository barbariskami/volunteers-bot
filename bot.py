from user import User
from message import Message
from exceptions import UserNotFound, AlreadyRegistered
from extentions import load_text, form_keyboard
from enumerates import TextLabels, States, MessageMarks


class Bot:

    @staticmethod
    def start_conversation(media, user_id):
        try:
            user = User(media, user_id)
        except UserNotFound:
            new_message = Message(user_id, text=load_text(TextLabels.REGISTRATION), marks=[MessageMarks.UNREGISTERED])
        else:
            new_message = Message(user_id,
                                  text=load_text(TextLabels.MAIN_MENU_GREETING),
                                  keyboard=form_keyboard(user, States.MAIN_MENU))
            user.set_state(media, States.MAIN_MENU)
        return new_message

    @staticmethod
    def register(media, user_id, password):
        try:
            User.register(media, user_id, password)
        except UserNotFound:
            new_message = Message(user_id, text=load_text(TextLabels.WRONG_PASSWORD), marks=(MessageMarks.UNREGISTERED))
        except AlreadyRegistered:
            new_message = Message(user_id, text=load_text(TextLabels.ALREADY_REGISTERED),
                                  marks=(MessageMarks.UNREGISTERED))
        else:
            user = User(media, user_id)
            new_message = Message(user_id,
                                  text=load_text(TextLabels.MAIN_MENU_GREETING_NEW),
                                  keyboard=form_keyboard(user, States.MAIN_MENU))
        return new_message

    @staticmethod
    def handle_message(media, message):
        try:
            user = User(media, message.user_id)
        except UserNotFound:
            new_message = Message(message.user_id,
                                  text=load_text(TextLabels.REGISTRATION),
                                  marks=(MessageMarks.UNREGISTERED))
        else:
            new_message = None
        return new_message

    @staticmethod
    def key_pressed(media, user_id, key):
        try:
            user = User(media, user_id)
        except UserNotFound:
            pass

    @staticmethod
    def __main_menu_state_handler__(user, message):
        new_message = None
        return new_message

    state_handlers = {States.MAIN_MENU: __main_menu_state_handler__}
