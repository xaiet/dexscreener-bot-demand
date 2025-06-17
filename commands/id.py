from telegram import Update
from telegram.ext import CommandHandler, CallbackContext


def id_handler(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    update.message.reply_text(f"El teu ID és: `{chat_id}`", parse_mode="Markdown")


show_id = CommandHandler("id", id_handler)