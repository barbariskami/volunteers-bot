import traceback
from bot import Bot
from message import Message
from enumerates import Media, MessageMarks
from telegram_bot.useful_additions import send_message


def start(update, context):
    try:
        new_messages = Bot.start_conversation(Media.TELEGRAM, update.effective_user.id)
        context.user_data['registered'] = True
        for message in new_messages:
            if MessageMarks.UNREGISTERED in message.marks:
                context.user_data['registered'] = False
            if message.keyboard:
                context.user_data['keyboard'] = message.keyboard
            context = send_message(update, context, message)
    except:
        traceback.print_exc()


def text_message_handler(update, context):
    try:
        if not context.user_data.get('registered', None):
            new_messages = Bot.register(Media.TELEGRAM, update.effective_user.id, update.message.text)
        elif context.user_data.get('keyboard', None) and \
                update.message.text in context.user_data['keyboard'].get_buttons():
            new_messages = Bot.button_pressed(media=Media.TELEGRAM,
                                              user_id=update.effective_user.id,
                                              button=context.user_data['keyboard'].get_button(update.message.text))
        else:
            new_messages = Bot.handle_message(media=Media.TELEGRAM,
                                              message=Message(user_id=update.effective_user.id,
                                                              text=update.message.text,
                                                              message_id=update.message.message_id,
                                                              media=Media.TELEGRAM))
        for message in new_messages:
            if MessageMarks.UNREGISTERED in message.marks:
                context.user_data['registered'] = False
            elif MessageMarks.SUCCESSFUL_REGISTRATION in message.marks:
                context.user_data['registered'] = True
            if message.keyboard:
                context.user_data['keyboard'] = message.keyboard
            context = send_message(update, context, message)
    except Exception:
        traceback.print_exc()


def image_message_handler(update, context):
    pass
