from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from enumerates import KeyboardTypes


def send_message(update, context, message):
    print(message.keyboard.buttons)
    context.bot.send_message(chat_id=update.effective_user.id,
                             text=message.text + '\nКод сообщений не дописан! Дописать! '
                                                 '(Если вы видите эту приписку, обратитей к программисту)',
                             reply_markup=convert_keyboard(message.keyboard))


def convert_keyboard(keyboard):
    tg_keyboard = None
    if keyboard.type == KeyboardTypes.REPLY:
        tg_keyboard = ReplyKeyboardMarkup([[button.text for button in line] for line in keyboard.buttons])
    elif keyboard.type == KeyboardTypes.INLINE:
        tg_keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text=button.text) for button in line] for line in keyboard.buttons])
    return tg_keyboard
