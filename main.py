import os
import requests
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, CallbackContext

# Variables d'entorn
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "ruta-secreta")
bot = Bot(token=BOT_TOKEN)

# Inici Flask
app = Flask(__name__)

# Obtenir parelles de Dexscreener
def get_pairs():
    res = requests.get("https://api.dexscreener.com/latest/dex/pairs/solana")
    return res.json().get("pairs", []) if res.status_code == 200 else []

# Format market cap
def format_market_cap(mcap):
    if mcap > 1_000_000:
        return f"${round(mcap / 1_000_000, 2)}M"
    elif mcap > 1_000:
        return f"${round(mcap / 1_000, 2)}k"
    else:
        return f"${int(mcap)}"

# Filtrar parelles (amb filtres molt amplis)
def filter_pairs(pairs):
    resultats = []
    for p in pairs:
        try:
            liquidity = float(p.get("liquidityUsd", 0))
            mcap = liquidity * 2
            volume = float(p.get("volumeUsd", 0))
            change = float(p.get("priceChange", {}).get("h1", 0))
            nom = p.get("baseToken", {}).get("name", "Sense nom")
            url = p.get("url")

            if 50_000 <= mcap <= 20_000_000 and volume >= 10_000 and change > -10:
                resultats.append({
                    "nom": nom,
                    "mcap": format_market_cap(mcap),
                    "url": url
                })
        except:
            continue
    return resultats

# Comandes Telegram
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Hola! Envia /tokens per veure criptos prometedores 🚀")

def tokens(update: Update, context: CallbackContext):
    update.message.reply_text("🔍 Cercant tokens amb potencial...")
    results = filter_pairs(get_pairs())
    if results:
        for p in results:
            msg = (
                f"🚀 {p['nom']}\n"
                f"📈 Market Cap: {p['mcap']}\n"
                f"🔗 {p['url']}"
            )
            update.message.reply_text(msg)
    else:
        update.message.reply_text("No s'han trobat tokens.")

# Dispatcher
dispatcher = Dispatcher(bot, update_queue=None, use_context=True)
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("tokens", tokens))

# Webhook amb ruta secreta
@app.route(f"/{WEBHOOK_SECRET}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK"

@app.route("/", methods=["GET"])
def home():
    return "Bot actiu 🚀"

# Executar Flask
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
