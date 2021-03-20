from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, CallbackQueryHandler
import telegram_bot.handlers as h_main
import telegram_bot.handlers_creation as h_creation
import os
import logging

logging.basicConfig(level=logging.INFO,
                    format=u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s')


def main():
    port_main = int(os.environ.get('PORT', 5000))
    token_main = open('telegram_bot/token_main.txt').read()
    updater_main = Updater(token_main, use_context=True)

    dp_main = updater_main.dispatcher

    dp_main.add_handler(CommandHandler('start', h_main.start))
    dp_main.add_handler(CommandHandler('switch_language', h_main.switch_language))
    dp_main.add_handler(CommandHandler('help', h_main.help_command))
    dp_main.add_handler(MessageHandler(Filters.text, h_main.text_message_handler))
    dp_main.add_handler(CallbackQueryHandler(h_main.callback_query_handler, pass_user_data=True))

    updater_main.start_webhook(listen="0.0.0.0",
                               port=int(port_main),
                               url_path=token_main)
    updater_main.bot.setWebhook('https://volunteers-bot.herokuapp.com/' + token_main)

    port_creation = int(os.environ.get('PORT', 5000))
    token_creation = open('telegram_bot/token_creation.txt').read()
    updater_creation = Updater(token_creation, use_context=True)

    dp_creation = updater_creation.dispatcher

    dp_creation.add_handler(CommandHandler('start', h_creation.start))
    dp_creation.add_handler(MessageHandler(Filters.text, h_creation.text_message_handler))
    dp_creation.add_handler(MessageHandler(Filters.photo, h_creation.image_message_handler))

    updater_creation.start_webhook(listen="0.0.0.0",
                                   port=int(port_creation),
                                   url_path=token_creation)
    updater_creation.bot.setWebhook('https://volunteers-bot.herokuapp.com/' + token_creation)

    logging.info('here now')

    updater_main.idle()

    logging.info('and finally here')


if __name__ == '__main__':
    main()
