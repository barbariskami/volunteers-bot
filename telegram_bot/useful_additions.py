def send_message(update, context, message):
    context.bot.send_message(chat_id=update.effective_user.id,
                             text='Заглушка, напишите нормальный код!')
