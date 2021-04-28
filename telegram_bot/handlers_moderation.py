import traceback
from enumerates import Media, MessageMarks, Bots, Languages
from telegram_bot.useful_additions import send_message, delete_message
import telegram
from bot_moderation import ModerationBot
from message import Message


def start(update, context):
    try:
        new_messages = ModerationBot.start_conversation(Media.TELEGRAM, update.effective_user.id)
        context.user_data['registered'] = True
        for message in new_messages['send']:
            if MessageMarks.UNREGISTERED in message.marks:
                context.user_data['registered'] = False
            if MessageMarks.NO_ACCESS in message.marks:
                context.user_data['access'] = False
            if message.keyboard:
                context.user_data['keyboard'] = message.keyboard
            context, message_id = send_message(update, context, message)
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
                    context.user_data['previous_buttons'].update(message.keyboard.get_buttons())
                context, message_id = send_message(update, context, message)
                if message.__dict__.get('request_id'):
                    if not message.bot:
                        message_bot = Bots.MODERATION
                    else:
                        message_bot = message.bot
                    ModerationBot.connect_message_to_request(media=Media.TELEGRAM,
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


def callback_query_handler(update, context):
    try:
        if not context.user_data.get('registered', None):
            new_messages = ModerationBot.unregistered(Media.TELEGRAM, update.effective_user.id)
        else:
            new_messages = ModerationBot.callback_query_handler(media=Media.TELEGRAM,
                                                                user_id=update.effective_user.id,
                                                                callback_data=update.callback_query.data,
                                                                bot=Bots.MODERATION)
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
                        message_bot = Bots.MODERATION
                    else:
                        message_bot = message.bot
                    ModerationBot.connect_message_to_request(media=Media.TELEGRAM,
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


def get_all_tags(update, context):
    try:
        if not context.user_data.get('registered', None):
            new_messages = ModerationBot.unregistered(Media.TELEGRAM, update.effective_user.id)
        else:
            new_messages = ModerationBot.get_all_tags(media=Media.TELEGRAM,
                                                      user_id=update.effective_user.id)
        for message in new_messages['send']:
            try:
                if MessageMarks.UNREGISTERED in message.marks:
                    context.user_data['registered'] = False
                elif MessageMarks.SUCCESSFUL_REGISTRATION in message.marks:
                    context.user_data['registered'] = True
                if MessageMarks.NO_ACCESS in message.marks:
                    context.user_data['access'] = False
                context, message_id = send_message(update, context, message)
            except telegram.error.BadRequest:
                traceback.print_exc()
    except Exception:
        traceback.print_exc()


def get_tag_info(update, context):
    try:
        if not context.user_data.get('registered', None):
            new_messages = ModerationBot.unregistered(Media.TELEGRAM, update.effective_user.id)
        else:
            if len(context.args):
                code = context.args[0]
            else:
                code = None
            new_messages = ModerationBot.get_tag_info(media=Media.TELEGRAM,
                                                      user_id=update.effective_user.id,
                                                      code=code)
        for message in new_messages['send']:
            try:
                if MessageMarks.UNREGISTERED in message.marks:
                    context.user_data['registered'] = False
                elif MessageMarks.SUCCESSFUL_REGISTRATION in message.marks:
                    context.user_data['registered'] = True
                if MessageMarks.NO_ACCESS in message.marks:
                    context.user_data['access'] = False
                context, message_id = send_message(update, context, message)
            except telegram.error.BadRequest:
                traceback.print_exc()
    except Exception:
        traceback.print_exc()


def change_tag_condition(update, context):
    try:
        if not context.user_data.get('registered', None):
            new_messages = ModerationBot.unregistered(Media.TELEGRAM, update.effective_user.id)
        else:
            if len(context.args):
                code = context.args[0]
            else:
                code = None
            new_messages = ModerationBot.change_tag_condition(media=Media.TELEGRAM,
                                                              user_id=update.effective_user.id,
                                                              code=code)
        for message in new_messages['send']:
            try:
                if MessageMarks.UNREGISTERED in message.marks:
                    context.user_data['registered'] = False
                elif MessageMarks.SUCCESSFUL_REGISTRATION in message.marks:
                    context.user_data['registered'] = True
                if MessageMarks.NO_ACCESS in message.marks:
                    context.user_data['access'] = False
                context, message_id = send_message(update, context, message)
            except telegram.error.BadRequest:
                traceback.print_exc()
    except Exception:
        traceback.print_exc()


def new_tag(update, context):
    try:
        if not context.user_data.get('registered', None):
            new_messages = ModerationBot.unregistered(Media.TELEGRAM, update.effective_user.id)
        else:
            try:
                code, *languages_list = context.args
                languages = {Languages.RU: languages_list[0],
                             Languages.EN: languages_list[1]}
            except (ValueError, IndexError) as ex:
                code = languages = None
            new_messages = ModerationBot.add_tag(media=Media.TELEGRAM,
                                                 user_id=update.effective_user.id,
                                                 code=code,
                                                 languages=languages)
        for message in new_messages['send']:
            try:
                if MessageMarks.UNREGISTERED in message.marks:
                    context.user_data['registered'] = False
                elif MessageMarks.SUCCESSFUL_REGISTRATION in message.marks:
                    context.user_data['registered'] = True
                if MessageMarks.NO_ACCESS in message.marks:
                    context.user_data['access'] = False
                context, message_id = send_message(update, context, message)
            except telegram.error.BadRequest:
                traceback.print_exc()
    except Exception:
        traceback.print_exc()


def delete_tag(update, context):
    try:
        if not context.user_data.get('registered', None):
            new_messages = ModerationBot.unregistered(Media.TELEGRAM, update.effective_user.id)
        else:
            if len(context.args):
                code = context.args[0]
            else:
                code = None
            new_messages = ModerationBot.delete_tag(media=Media.TELEGRAM,
                                                    user_id=update.effective_user.id,
                                                    code=code)
        for message in new_messages['send']:
            try:
                if MessageMarks.UNREGISTERED in message.marks:
                    context.user_data['registered'] = False
                elif MessageMarks.SUCCESSFUL_REGISTRATION in message.marks:
                    context.user_data['registered'] = True
                if MessageMarks.NO_ACCESS in message.marks:
                    context.user_data['access'] = False
                context, message_id = send_message(update, context, message)
            except telegram.error.BadRequest:
                traceback.print_exc()
    except Exception:
        traceback.print_exc()


def assign_moderator(update, context):
    try:
        if not context.user_data.get('registered', None):
            new_messages = ModerationBot.unregistered(Media.TELEGRAM, update.effective_user.id)
        else:
            if len(context.args):
                new_moderator_id = context.args[0]
            else:
                new_moderator_id = None
            new_messages = ModerationBot.assign_status(media=Media.TELEGRAM,
                                                       user_id=update.effective_user.id,
                                                       new_moderator_id=new_moderator_id,
                                                       moderator=True)
        for message in new_messages['send']:
            try:
                if MessageMarks.UNREGISTERED in message.marks:
                    context.user_data['registered'] = False
                elif MessageMarks.SUCCESSFUL_REGISTRATION in message.marks:
                    context.user_data['registered'] = True
                if MessageMarks.NO_ACCESS in message.marks:
                    context.user_data['access'] = False
                context, message_id = send_message(update, context, message)
            except telegram.error.BadRequest:
                traceback.print_exc()
    except Exception:
        traceback.print_exc()


def assign_admin(update, context):
    try:
        if not context.user_data.get('registered', None):
            new_messages = ModerationBot.unregistered(Media.TELEGRAM, update.effective_user.id)
        else:
            if len(context.args):
                new_admin_id = context.args[0]
            else:
                new_admin_id = None
            new_messages = ModerationBot.assign_status(media=Media.TELEGRAM,
                                                       user_id=update.effective_user.id,
                                                       new_moderator_id=new_admin_id,
                                                       admin=True)
        for message in new_messages['send']:
            try:
                if MessageMarks.UNREGISTERED in message.marks:
                    context.user_data['registered'] = False
                elif MessageMarks.SUCCESSFUL_REGISTRATION in message.marks:
                    context.user_data['registered'] = True
                if MessageMarks.NO_ACCESS in message.marks:
                    context.user_data['access'] = False
                context, message_id = send_message(update, context, message)
            except telegram.error.BadRequest:
                traceback.print_exc()
    except Exception:
        traceback.print_exc()


def withdraw_moderator(update, context):
    try:
        if not context.user_data.get('registered', None):
            new_messages = ModerationBot.unregistered(Media.TELEGRAM, update.effective_user.id)
        else:
            if len(context.args):
                user_to_withdraw = context.args[0]
            else:
                user_to_withdraw = None
            new_messages = ModerationBot.withdraw_status(media=Media.TELEGRAM,
                                                         user_id=update.effective_user.id,
                                                         user_to_withdraw=user_to_withdraw,
                                                         moderator=True)
        for message in new_messages['send']:
            try:
                if MessageMarks.UNREGISTERED in message.marks:
                    context.user_data['registered'] = False
                elif MessageMarks.SUCCESSFUL_REGISTRATION in message.marks:
                    context.user_data['registered'] = True
                if MessageMarks.NO_ACCESS in message.marks:
                    context.user_data['access'] = False
                context, message_id = send_message(update, context, message)
            except telegram.error.BadRequest:
                traceback.print_exc()
    except Exception:
        traceback.print_exc()


def withdraw_admin(update, context):
    try:
        if not context.user_data.get('registered', None):
            new_messages = ModerationBot.unregistered(Media.TELEGRAM, update.effective_user.id)
        else:
            if len(context.args):
                user_to_withdraw = context.args[0]
            else:
                user_to_withdraw = None
            new_messages = ModerationBot.withdraw_status(media=Media.TELEGRAM,
                                                         user_id=update.effective_user.id,
                                                         user_to_withdraw=user_to_withdraw,
                                                         admin=True)
        for message in new_messages['send']:
            try:
                if MessageMarks.UNREGISTERED in message.marks:
                    context.user_data['registered'] = False
                elif MessageMarks.SUCCESSFUL_REGISTRATION in message.marks:
                    context.user_data['registered'] = True
                if MessageMarks.NO_ACCESS in message.marks:
                    context.user_data['access'] = False
                context, message_id = send_message(update, context, message)
            except telegram.error.BadRequest:
                traceback.print_exc()
    except Exception:
        traceback.print_exc()


def get_all_users_csv(update, context):
    try:
        if not context.user_data.get('registered', None):
            new_messages = ModerationBot.unregistered(Media.TELEGRAM, update.effective_user.id)
        else:
            new_messages = ModerationBot.get_all_users_csv(media=Media.TELEGRAM,
                                                           user_id=update.effective_user.id)
        for message in new_messages['send']:
            try:
                if MessageMarks.UNREGISTERED in message.marks:
                    context.user_data['registered'] = False
                elif MessageMarks.SUCCESSFUL_REGISTRATION in message.marks:
                    context.user_data['registered'] = True
                if MessageMarks.NO_ACCESS in message.marks:
                    context.user_data['access'] = False
                context, message_id = send_message(update, context, message)
            except telegram.error.BadRequest:
                traceback.print_exc()
    except Exception:
        traceback.print_exc()


def get_all_requests_csv(update, context):
    try:
        if not context.user_data.get('registered', None):
            new_messages = ModerationBot.unregistered(Media.TELEGRAM, update.effective_user.id)
        else:
            new_messages = ModerationBot.get_all_requests_csv(media=Media.TELEGRAM,
                                                              user_id=update.effective_user.id)
        for message in new_messages['send']:
            try:
                if MessageMarks.UNREGISTERED in message.marks:
                    context.user_data['registered'] = False
                elif MessageMarks.SUCCESSFUL_REGISTRATION in message.marks:
                    context.user_data['registered'] = True
                if MessageMarks.NO_ACCESS in message.marks:
                    context.user_data['access'] = False
                context, message_id = send_message(update, context, message)
            except telegram.error.BadRequest:
                traceback.print_exc()
    except Exception:
        traceback.print_exc()
