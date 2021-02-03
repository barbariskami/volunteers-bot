from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, CallbackQueryHandler
from telegram_bot.handlers_moderation import start, text_message_handler, callback_query_handler


def main():
    token = open('telegram_bot/token_moderation.txt').read()
    updater = Updater(token, use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(MessageHandler(Filters.text, text_message_handler))
    dp.add_handler(CallbackQueryHandler(callback_query_handler, pass_user_data=True))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()