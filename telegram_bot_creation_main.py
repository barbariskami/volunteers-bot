from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
from telegram_bot.handlers_creation import start, text_message_handler, image_message_handler


def main():
    token = open('telegram_bot/token_creation.txt').read()
    updater = Updater(token, use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(MessageHandler(Filters.text, text_message_handler))
    dp.add_handler(MessageHandler(Filters.photo, image_message_handler))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
