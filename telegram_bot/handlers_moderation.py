import traceback
from enumerates import Media, MessageMarks
from telegram_bot.useful_additions import send_message
from bot_moderation import ModerationBot
from message import Message


def start(update, context):
    try:
        new_messages = ModerationBot.start_conversation(Media.TELEGRAM, update.effective_user.id)
        context.user_data['registered'] = True
        for message in new_messages:
            if MessageMarks.UNREGISTERED in message.marks:
                context.user_data['registered'] = False
            if MessageMarks.NO_ACCESS in message.marks:
                context.user_data['access'] = False
            if message.keyboard:
                context.user_data['keyboard'] = message.keyboard
            context = send_message(update, context, message)
    except:
        traceback.print_exc()


def text_message_handler(update, context):
    try:
        if not context.user_data.get('registered', None):
            new_messages = ModerationBot.unregistered(Media.TELEGRAM, update.effective_user.id)
        elif context.user_data.get('keyboard', None) and \
                update.message.text in context.user_data['keyboard'].get_buttons():
            new_messages = ModerationBot.button_pressed(media=Media.TELEGRAM,
                                                        user_id=update.effective_user.id,
                                                        button=context.user_data['keyboard'].get_button(
                                                            update.message.text),
                                                        creation=True)
        else:
            new_messages = ModerationBot.handle_message(media=Media.TELEGRAM,
                                                        message=Message(user_id=update.effective_user.id,
                                                                        text=update.message.text,
                                                                        message_id=update.message.message_id,
                                                                        media=Media.TELEGRAM),
                                                        creation=True)
        for message in new_messages:
            if MessageMarks.UNREGISTERED in message.marks:
                context.user_data['registered'] = False
            elif MessageMarks.SUCCESSFUL_REGISTRATION in message.marks:
                context.user_data['registered'] = True
            if MessageMarks.NO_ACCESS in message.marks:
                context.user_data['access'] = False
            if message.keyboard:
                context.user_data['keyboard'] = message.keyboard
                context.user_data['previous_buttons'].update(message.keyboard.get_buttons())
            context = send_message(update, context, message)
    except Exception:
        traceback.print_exc()


def image_message_handler(update, context):
    pass
