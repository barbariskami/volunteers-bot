from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from enumerates import KeyboardTypes


def send_message(update, context, message):
    message = context.bot.send_message(chat_id=update.effective_user.id,
                                           text=message.text,
                                           reply_markup=convert_keyboard(
                                               message.keyboard) if message.keyboard else None)
    context.user_data['last_message_id'] = message.message_id
    return context


def convert_keyboard(keyboard):
    tg_keyboard = None
    if keyboard.type == KeyboardTypes.REPLY:
        tg_keyboard = ReplyKeyboardMarkup([[button.text for button in line] for line in keyboard.buttons])
    elif keyboard.type == KeyboardTypes.INLINE:
        tg_keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text=button.text) for button in line] for line in keyboard.buttons])
    return tg_keyboard
