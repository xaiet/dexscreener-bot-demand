import os
import requests
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, CallbackContext

# Inici
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
app = Flask(__name__)

# Funcions de filtrat
def get_pairs():
    res = requests.get("https://api.dexscreener.com/latest/dex/pairs/solana")
    return res.json().get("pairs", []) if res.status_code == 200 else []

def filter_pairs(pairs):
    filtered = []
    for p in pairs:
        try:
            mcap = float(p.get("liquidityUsd", 0)) * 2
            volume = float(p.get("volumeUsd", 0))
            change = float(p.get("priceChange", {}).get("h1", 0))
            if 300_000 <= mcap <= 5_000_000 and volume > 100_000 and change > 5:
                filtered.append(p)
        except:
            continue
    return filtered

# Handlers
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Hola! Envia /tokens per veure gemmes 🚀")

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
        update.message.reply_text("No s'han trobat tokens.")

# Dispatcher i Webhook
dispatcher = Dispatcher(bot, update_queue=None, use_context=True)
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("tokens", tokens))

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK"

@app.route("/", methods=["GET"])
def home():
    return "Bot actiu 🚀"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
