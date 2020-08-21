import traceback
from enumerates import Media, MessageMarks
from telegram_bot.useful_additions import send_message
from bot_creation import CreationBot


def start(update, context):
    try:
        new_messages = CreationBot.start_conversation(Media.TELEGRAM, update.effective_user.id)
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
            new_messages = CreationBot.unregistered(Media.TELEGRAM, update.effective_user.id)
        else:
            pass
    except Exception:
        traceback.print_exc()


def image_message_handler(update, context):
    pass
