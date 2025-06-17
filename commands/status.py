from telegram import Update
from telegram.ext import CommandHandler, CallbackContext


def status_handler(update: Update, context: CallbackContext):
    update.message.reply_text("✅ El bot està actiu i escoltant.")


show_status = CommandHandler("status", status_handler)