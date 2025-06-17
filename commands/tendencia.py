from telegram import Update
from telegram.ext import CommandHandler, CallbackContext
from utils.filters import get_filtered_tokens
from utils.helpers import format_token_message


def tendencia_handler(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    update.message.reply_text("🔍 Cercant tokens en tendència...")

    tokens = get_filtered_tokens()
    if not tokens:
        update.message.reply_text("❌ No s'ha trobat cap token que compleixi els filtres ara mateix.")
        return

    for msg in tokens:
        context.bot.send_message(chat_id=chat_id, text=msg, parse_mode="Markdown", disable_web_page_preview=True)


cmd_tendencia = CommandHandler("tendencia", tendencia_handler)