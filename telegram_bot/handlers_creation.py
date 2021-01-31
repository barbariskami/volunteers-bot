import traceback
from enumerates import Media, MessageMarks, Bots
from telegram_bot.useful_additions import send_message, delete_message
from bot_creation import CreationBot
from message import Message


def start(update, context):
    try:
        new_messages = CreationBot.start_conversation(Media.TELEGRAM, update.effective_user.id)
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
            new_messages = CreationBot.unregistered(Media.TELEGRAM, update.effective_user.id)
        elif context.user_data.get('keyboard', None) and \
                update.message.text in context.user_data['keyboard'].get_buttons():
            new_messages = CreationBot.button_pressed(media=Media.TELEGRAM,
                                                      user_id=update.effective_user.id,
                                                      button=context.user_data['keyboard'].get_button(
                                                          update.message.text),
                                                      creation=True)
        else:
            new_messages = CreationBot.handle_message(media=Media.TELEGRAM,
                                                      message=Message(user_id=update.effective_user.id,
                                                                      text=update.message.text,
                                                                      message_id=update.message.message_id,
                                                                      media=Media.TELEGRAM),
                                                      creation=True)
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
                    message_bot = Bots.CREATION
                else:
                    message_bot = message.bot
                CreationBot.connect_message_to_request(media=Media.TELEGRAM,
                                                       media_user_id=message.user_id,
                                                       bot=message_bot,
                                                       message_id=message_id,
                                                       request_base_id=message.request_id)
        for message in new_messages.get('delete', tuple()):
            delete_message(update, context, message)
    except Exception:
        traceback.print_exc()


def image_message_handler(update, context):
    pass
