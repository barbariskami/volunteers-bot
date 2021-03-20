from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
from telegram_bot.handlers_creation import start, text_message_handler, image_message_handler
import os


def main():
    port = int(os.environ.get('PORT', 5000))
    token = open('telegram_bot/token_creation.txt').read()
    updater = Updater(token, use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(MessageHandler(Filters.text, text_message_handler))
    dp.add_handler(MessageHandler(Filters.photo, image_message_handler))

    updater.start_webhook(listen="0.0.0.0",
                          port=int(port),
                          url_path=token)
    updater.bot.setWebhook('https://volunteers-bot.herokuapp.com/' + token)

    updater.idle()


if __name__ == '__main__':
    main()
