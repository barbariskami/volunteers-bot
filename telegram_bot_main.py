from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, CallbackQueryHandler
from telegram_bot.handlers import start, text_message_handler, switch_language, callback_query_handler, help_command
import os
import logging

logging.basicConfig(level=logging.INFO,
                    format = u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s')


def main():
    port = int(os.environ.get('PORT', 5000))
    token = open('telegram_bot/token_main.txt').read()
    updater = Updater(token, use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('switch_language', switch_language))
    dp.add_handler(CommandHandler('help', help_command))
    dp.add_handler(MessageHandler(Filters.text, text_message_handler))
    dp.add_handler(CallbackQueryHandler(callback_query_handler, pass_user_data=True))

    updater.start_webhook(listen="0.0.0.0",
                          port=int(port),
                          url_path=token)
    updater.bot.setWebhook('https://volunteers-bot.herokuapp.com/' + token)

    logging.info('here now')

    updater.idle()

    logging.info('and finally here')


if __name__ == '__main__':
    main()
