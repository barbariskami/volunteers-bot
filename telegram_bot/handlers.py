import traceback
import random
from telegram import ParseMode
from bot import Bot
from enumerates import Media, MessageMarks
from telegram_bot.useful_additions import send_message


def start(update, context):
    try:
        new_messages = Bot.start_conversation(Media.TELEGRAM, update.effective_user.id)
        context.user_data['registered'] = True
        for message in new_messages:
            if MessageMarks.UNREGISTERED in message.marks:
                context.user_data['registered'] = False
            send_message(update, context, message)
    except:
        traceback.print_exc()


def text_message_handler(update, context):
    try:
        if not context.user_data['registered']:
            new_messages = Bot.register(Media.TELEGRAM, update.effective_user.id, update.message.text)
        else:
            new_messages = Bot.handle_message(media=Media.TELEGRAM, message=update.message.text)
        for message in new_messages:
            if MessageMarks.UNREGISTERED in message.marks:
                context.user_data['registered'] = False
            elif MessageMarks.SUCCESSFUL_REGISTRATION in message.marks:
                context.user_data['registered'] = True
            send_message(update, context, message)
    except Exception:
        traceback.print_exc()


def image_message_handler(update, context):
    pass
