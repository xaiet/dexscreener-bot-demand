import os
import requests
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext

BOT_TOKEN = os.getenv("BOT_TOKEN")

def get_pairs():
    res = requests.get("https://api.dexscreener.com/latest/dex/pairs/solana")
    return res.json().get("pairs", []) if res.status_code == 200 else []

def filter_pairs(pairs):
    resultats = []
    for p in pairs:
        try:
            mcap = float(p.get("liquidityUsd", 0)) * 2
            volume = float(p.get("volumeUsd", 0))
            change = float(p.get("priceChange", {}).get("h1", 0))
            if 300_000 <= mcap <= 5_000_000 and volume > 100_000 and change > 5:
                resultats.append(p)
        except:
            continue
    return resultats

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Hola! Envia /tokens per veure gemmes amb potencial 🚀")

def tokens(update: Update, context: CallbackContext):
    update.message.reply_text("🔍 Cercant tokens...")
    results = filter_pairs(get_pairs())
    if results:
        for p in results[:5]:
            nom = p['baseToken']['name']
            canvi = p['priceChange']['h1']
            volum = int(float(p['volumeUsd']))
            url = p['url']
            update.message.reply_text(f"🚀 {nom} | +{canvi}% amb {volum}$ de volum\n👉 {url}")
    else:
        update.message.reply_text("No s'han trobat tokens amb els filtres actuals.")

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("tokens", tokens))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
    