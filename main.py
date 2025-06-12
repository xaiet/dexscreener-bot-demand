import os
import requests
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, CallbackContext

# Variables d'entorn
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)

# Inici Flask
app = Flask(__name__)

# Obtenir parelles des de Dexscreener
def get_pairs():
    res = requests.get("https://api.dexscreener.com/latest/dex/pairs/solana")
    return res.json().get("pairs", []) if res.status_code == 200 else []

# Format market cap en M/k
def format_market_cap(mcap):
    if mcap > 1_000_000:
        return f"${round(mcap / 1_000_000, 2)}M"
    elif mcap > 1_000:
        return f"${round(mcap / 1_000, 2)}k"
    else:
        return f"${int(mcap)}"

# Filtrar parelles prometedores
def filter_pairs(pairs):
    resultats = []
    for p in pairs:
        try:
            liquidity = float(p.get("liquidityUsd", 0))
            mcap = liquidity * 2  # estimació senzilla
            volume = float(p.get("volumeUsd", 0))
            change = float(p.get("priceChange", {}).get("h1", 0))
            address = p.get("pairAddress")
            nom = p.get("baseToken", {}).get("name", "Sense nom")
            url = p.get("url")

            if 150_000 <= mcap <= 10_000_000 and volume > 50_000 and change >= 0:
                resultat = {
                    "nom": nom,
                    "mcap": format_market_cap(mcap),
                    "url": url,
                    "address": address
                }
                resultats.append(resultat)
        except:
            continue
    return resultats

# Comandes de Telegram
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Hola! Envia /tokens per veure gemmes en fase inicial 🚀")

def tokens(update: Update, context: CallbackContext):
    update.message.reply_text("🔍 Buscant tokens amb bon potencial...")
    results = filter_pairs(get_pairs())
    if results:
        for p in results[:7]:
            msg = (
                f"🚀 {p['nom']}\n"
                f"📈 Market Cap: {p['mcap']}\n"
                f"🔗 {p['url']}"
            )
            update.message.reply_text(msg)
    else:
        update.message.reply_text("No s'han trobat tokens amb els filtres actuals.")

# Configuració del dispatcher
dispatcher = Dispatcher(bot, update_queue=None, use_context=True)
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("tokens", tokens))

# Webhook endpoint
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK"

# Endpoint simple per provar que està actiu
@app.route("/", methods=["GET"])
def home():
    return "Bot actiu 🚀"

# Executar app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
