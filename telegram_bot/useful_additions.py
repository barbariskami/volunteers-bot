from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, ParseMode, Bot, \
    ReplyKeyboardRemove
from enumerates import KeyboardTypes
import logging
import traceback

logging.basicConfig(level=logging.INFO,
                    format=u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s')


def send_message(update, context, message):
    if message.bot:
        token = open('telegram_bot/token_{}.txt'.format(message.bot.name.lower())).read()
        telegram_bot = Bot(token=token)
    else:
        telegram_bot = context.bot

    if message.file:
        new_message = telegram_bot.send_document(message.user_id, message.file)
    else:
        new_message = telegram_bot.send_message(chat_id=message.user_id,
                                                text=message.text,
                                                reply_markup=convert_keyboard(
                                                    message.keyboard) if message.keyboard else None,
                                                parse_mode=ParseMode.MARKDOWN)
    context.dispatcher.user_data[message.user_id]['last_message_id'] = new_message.message_id
    return context, new_message.message_id


def convert_keyboard(keyboard):
    tg_keyboard = None
    if keyboard.DELETE:
        tg_keyboard = ReplyKeyboardRemove()
        return tg_keyboard
    if keyboard.type == KeyboardTypes.REPLY:
        tg_keyboard = ReplyKeyboardMarkup([[button.text for button in line] for line in keyboard.buttons])
    elif keyboard.type == KeyboardTypes.INLINE:
        tg_keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text=button.text, callback_data=button.info['callback_data']) for button in line]
             for
             line in keyboard.buttons])
    return tg_keyboard


def delete_message(update=None, context=None, message=None):
    if message.bot:
        token = open('telegram_bot/token_{}.txt'.format(message.bot.name.lower())).read()
        telegram_bot = Bot(token=token)
    else:
        telegram_bot = context.bot
    try:
        success = telegram_bot.delete_message(chat_id=message.user_id, message_id=message.media_id)
        if success:
            logging.info('Message {m_id} has been deleted from user {u_id}, bot {bot_name}, media {media_name}'.format(
                m_id=str(message.media_id),
                u_id=str(message.user_id),
                bot_name=telegram_bot.name,
                media_name='Telegram'))
        if not success:
            edit_success = telegram_bot.edit_message_reply_markup(chat_id=message.user_id, message_id=message.media_id)
            edit_success += telegram_bot.edit_message_text(chat_id=message.user_id,
                                                           message_id=message.media_id,
                                                           text='.')
            if edit_success:
                logging.info('Message {m_id} has been edited by user {u_id}, bot {bot_name}, media {media_name}'.format(
                    m_id=str(message.media_id),
                    u_id=str(message.user_id),
                    bot_name=telegram_bot.name,
                    media_name='Telegram'))
            else:
                logging.info(
                    'Message {m_id} has NOT been edited by user {u_id}, bot {bot_name}, media {media_name}'.format(
                        m_id=str(message.media_id),
                        u_id=str(message.user_id),
                        bot_name=telegram_bot.name,
                        media_name='Telegram'))

    except Exception as ex:
        logging.error(ex)
        traceback.print_exc()
