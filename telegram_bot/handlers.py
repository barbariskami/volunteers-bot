import traceback
import random
from telegram import ParseMode
from bot import Bot
from enumerates import Media
from telegram_bot.useful_additions import send_message


def start(update, context):
    try:
        next_message = Bot.start_conversation(Media.TELEGRAM, update.effective_user.id)
        send_message(update, context, next_message)
    except:
        traceback.print_exc()


def text_message_handler(update, context):
    pass


def image_message_handler(update, context):
    pass
