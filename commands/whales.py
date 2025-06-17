from telegram import Update
from telegram.ext import CommandHandler, CallbackContext


def whales_handler(update: Update, context: CallbackContext):
    update.message.reply_text(
        "📡 Funcionalitat de seguiment de grans moviments encara en desenvolupament."
    )


cmd_whales = CommandHandler("whales", whales_handler)