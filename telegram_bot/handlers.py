import traceback
from bot import Bot
from message import Message
from enumerates import Media, MessageMarks, Bots
from telegram_bot.useful_additions import send_message, delete_message
import telegram


def start(update, context):
    try:
        if context.args:
            password = context.args[0]
            new_messages = Bot.register(Media.TELEGRAM,
                                        user_id=update.effective_user.id,
                                        password=password,
                                        user_contact_link='@' + (
                                            update.effective_user.username if update.effective_user.username else ''))
        else:
            new_messages = Bot.start_conversation(Media.TELEGRAM,
                                                  update.effective_user.id,
                                                  user_contact_link='@' + (
                                                      update.effective_user.username if update.effective_user.username else ''))
        context.user_data['registered'] = True
        for message in new_messages['send']:
            if MessageMarks.UNREGISTERED in message.marks:
                context.user_data['registered'] = False
            if message.keyboard:
                context.user_data['keyboard'] = message.keyboard
            context, message_id = send_message(update, context, message)
    except:
        traceback.print_exc()


def text_message_handler(update, context):
    try:
        if not context.user_data.get('registered', None):
            new_messages = Bot.register(Media.TELEGRAM,
                                        update.effective_user.id,
                                        update.message.text,
                                        user_contact_link='@' + (
                                            update.effective_user.username if update.effective_user.username else ''))
        elif context.user_data.get('keyboard', None) and \
                update.message.text in context.user_data['keyboard'].get_buttons():
            new_messages = Bot.button_pressed(media=Media.TELEGRAM,
                                              user_id=update.effective_user.id,
                                              button=context.user_data['keyboard'].get_button(update.message.text))
        else:
            new_messages = Bot.handle_message(media=Media.TELEGRAM,
                                              message=Message(user_id=update.effective_user.id,
                                                              text=update.message.text,
                                                              message_id=update.message.message_id,
                                                              media=Media.TELEGRAM))
        for message in new_messages['send']:
            if MessageMarks.UNREGISTERED in message.marks:
                context.user_data['registered'] = False
            elif MessageMarks.SUCCESSFUL_REGISTRATION in message.marks:
                context.user_data['registered'] = True
            if message.keyboard:
                context.user_data['keyboard'] = message.keyboard
            context, message_id = send_message(update, context, message)
            if message.__dict__.get('request_id'):
                if not message.bot:
                    message_bot = Bots.MAIN
                else:
                    message_bot = message.bot
                Bot.connect_message_to_request(media=Media.TELEGRAM,
                                               media_user_id=message.user_id,
                                               bot=message_bot,
                                               message_id=message_id,
                                               request_base_id=message.request_id)
        for message in new_messages.get('delete', tuple()):
            delete_message(update, context, message)
    except Exception:
        traceback.print_exc()


def switch_language(update, context):
    try:
        if not context.user_data.get('registered', None):
            new_messages = Bot.unregistered(Media.TELEGRAM, update.effective_user.id)
        else:
            new_messages = Bot.switch_language_command(update.effective_user.id, Media.TELEGRAM)

        for message in new_messages['send']:
            if MessageMarks.UNREGISTERED in message.marks:
                context.user_data['registered'] = False
            if message.keyboard:
                context.user_data['keyboard'] = message.keyboard
            context, message_id = send_message(update, context, message)
            if message.__dict__.get('request_id'):
                if not message.bot:
                    message_bot = Bots.MAIN
                else:
                    message_bot = message.bot
                Bot.connect_message_to_request(media=Media.TELEGRAM,
                                               media_user_id=update.effective_user.id,
                                               bot=message_bot,
                                               message_id=message_id,
                                               request_base_id=message.request_id)
    except Exception:
        traceback.print_exc()


def help_command(update, context):
    try:
        if not context.user_data.get('registered', None):
            new_messages = Bot.unregistered(Media.TELEGRAM, update.effective_user.id)
        else:
            new_messages = Bot.help_command(update.effective_user.id, Media.TELEGRAM)

        for message in new_messages['send']:
            if MessageMarks.UNREGISTERED in message.marks:
                context.user_data['registered'] = False
            if message.keyboard:
                context.user_data['keyboard'] = message.keyboard
            context, message_id = send_message(update, context, message)
            if message.__dict__.get('request_id'):
                if not message.bot:
                    message_bot = Bots.MAIN
                else:
                    message_bot = message.bot
                Bot.connect_message_to_request(media=Media.TELEGRAM,
                                               media_user_id=update.effective_user.id,
                                               bot=message_bot,
                                               message_id=message_id,
                                               request_base_id=message.request_id)
    except Exception:
        traceback.print_exc()


def callback_query_handler(update, context):
    try:
        if not context.user_data.get('registered', None):
            new_messages = Bot.unregistered(Media.TELEGRAM, update.effective_user.id)
        else:
            new_messages = Bot.callback_query_handler(media=Media.TELEGRAM,
                                                      user_id=update.effective_user.id,
                                                      callback_data=update.callback_query.data,
                                                      bot=Bots.MAIN)
        for message in new_messages['send']:
            try:
                if MessageMarks.UNREGISTERED in message.marks:
                    context.user_data['registered'] = False
                elif MessageMarks.SUCCESSFUL_REGISTRATION in message.marks:
                    context.user_data['registered'] = True
                if MessageMarks.NO_ACCESS in message.marks:
                    context.user_data['access'] = False
                if message.keyboard:
                    context.user_data['keyboard'] = message.keyboard
                context, message_id = send_message(update, context, message)
                if message.__dict__.get('request_id'):
                    if not message.bot:
                        message_bot = Bots.MAIN
                    else:
                        message_bot = message.bot
                    Bot.connect_message_to_request(media=Media.TELEGRAM,
                                                   media_user_id=message.user_id,
                                                   bot=message_bot,
                                                   message_id=message_id,
                                                   request_base_id=message.request_id)
            except telegram.error.BadRequest:
                traceback.print_exc()
        for message in new_messages.get('delete', tuple()):
            delete_message(update, context, message)
    except Exception:
        traceback.print_exc()
