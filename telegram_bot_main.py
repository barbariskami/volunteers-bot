from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, CallbackQueryHandler
import telegram_bot.handlers as h_main
import telegram_bot.handlers_creation as h_creation
import telegram_bot.handlers_moderation as h_moderation
import os
import logging
import argparse

logging.basicConfig(level=logging.INFO,
                    format=u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s')

parser = argparse.ArgumentParser()
parser.add_argument('--bot',
                    default='main',
                    type=str,
                    help='Which bot is to be started',
                    dest="bot",
                    choices=['main', 'creation', 'moderation'])
args = parser.parse_args()
logging.info(args.bot)


def main(bot_type='main'):
    port = int(os.environ.get('PORT', 5000))
    token = open('telegram_bot/token_{bot}.txt'.format(bot=bot_type)).read()
    logging.info('token is ' + str(token))
    updater = Updater(token, use_context=True)

    dp = updater.dispatcher

    url = ''
    if bot_type == 'main':
        dp.add_handler(CommandHandler('start', h_main.start))
        dp.add_handler(CommandHandler('switch_language', h_main.switch_language))
        dp.add_handler(CommandHandler('help', h_main.help_command))
        dp.add_handler(MessageHandler(Filters.text, h_main.text_message_handler))
        dp.add_handler(CallbackQueryHandler(h_main.callback_query_handler, pass_user_data=True))
        url = 'https://letovo-helper.herokuapp.com/'
    elif bot_type == 'creation':
        logging.info(args.bot + 'recognized')
        dp.add_handler(CommandHandler('start', h_creation.start))
        dp.add_handler(MessageHandler(Filters.text, h_creation.text_message_handler))
        dp.add_handler(MessageHandler(Filters.photo, h_creation.image_message_handler))
        url = 'https://letovo-helper-ask.herokuapp.com/'
    elif bot_type == 'moderation':
        dp.add_handler(CommandHandler('start', h_moderation.start))
        dp.add_handler(CommandHandler('all_tags', h_moderation.get_all_tags))
        dp.add_handler(CommandHandler('tag_info', h_moderation.get_tag_info, pass_args=True))
        dp.add_handler(CommandHandler('new_tag', h_moderation.new_tag, pass_args=True))
        dp.add_handler(CommandHandler('delete_tag', h_moderation.delete_tag, pass_args=True))
        dp.add_handler(CommandHandler('assign_moderator', h_moderation.assign_moderator, pass_args=True))
        dp.add_handler(CommandHandler('assign_admin', h_moderation.assign_admin, pass_args=True))
        dp.add_handler(CommandHandler('change_tag_condition', h_moderation.change_tag_condition, pass_args=True))
        dp.add_handler(CommandHandler('withdraw_moderator', h_moderation.withdraw_moderator, pass_args=True))
        dp.add_handler(CommandHandler('withdraw_admin', h_moderation.withdraw_admin, pass_args=True))
        dp.add_handler(CommandHandler('get_all_users_csv', h_moderation.get_all_users_csv))
        dp.add_handler(CommandHandler('get_all_requests_csv', h_moderation.get_all_requests_csv))
        dp.add_handler(MessageHandler(Filters.text, h_moderation.text_message_handler))
        dp.add_handler(CallbackQueryHandler(h_moderation.callback_query_handler, pass_user_data=True))
        url = 'https://letovo-helper-moderation.herokuapp.com/'

    updater.start_webhook(listen="0.0.0.0",
                          port=int(port),
                          url_path=token)
    updater.bot.setWebhook(url + token)

    updater.idle()


if __name__ == '__main__':
    main(bot_type=args.bot)
