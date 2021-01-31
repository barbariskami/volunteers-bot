from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, ParseMode, Bot
from enumerates import KeyboardTypes, Media
from user import User
import traceback


def send_message(update, context, message):
    if message.bot:
        token = open('telegram_bot/token_{}.txt'.format(message.bot.name.lower())).read()
        telegram_bot = Bot(token=token)
    else:
        telegram_bot = context.bot

    new_message = telegram_bot.send_message(chat_id=message.user_id,
                                            text=message.text,
                                            reply_markup=convert_keyboard(
                                                message.keyboard) if message.keyboard else None,
                                            parse_mode=ParseMode.MARKDOWN)
    context.dispatcher.user_data[message.user_id]['last_message_id'] = new_message.message_id
    return context, new_message.message_id


def convert_keyboard(keyboard):
    tg_keyboard = None
    if keyboard.type == KeyboardTypes.REPLY:
        tg_keyboard = ReplyKeyboardMarkup([[button.text for button in line] for line in keyboard.buttons])
    elif keyboard.type == KeyboardTypes.INLINE:
        tg_keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text=button.text, callback_data=button.info['callback_data']) for button in line]
             for
             line in keyboard.buttons])
    return tg_keyboard


def delete_message(update, context, message):
    if message.bot:
        token = open('telegram_bot/token_{}.txt'.format(message.bot.name.lower())).read()
        telegram_bot = Bot(token=token)
    else:
        telegram_bot = context.bot
    try:
        success = telegram_bot.delete_message(chat_id=message.user_id, message_id=message.media_id)
        if not success:
            telegram_bot.edit_message_reply_markup(chat_id=message.user_id, message_id=message.media_id)
            telegram_bot.edit_message_text(chat_id=message.user_id, message_id=message.media_id, text='.')
    except:
        traceback.print_exc()
