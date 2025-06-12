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

# Obtenir parelles de l'API i filtrar per Solana
def get_solana_pairs():
    url = "https://api.dexscreener.com/latest/dex/pairs"
    try:
        res = requests.get(url, timeout=10)
        if res.status_code != 200:
            return []
        all_pairs = res.json().get("pairs", [])
        solana_pairs = [p for p in all_pairs if p.get("chainId") == "solana"]
        return solana_pairs
    except Exception as e:
        print("Error obtenint parelles:", e)
        return []

# Format de Market Cap
def format_market_cap(mcap):
    if mcap > 1_000_000:
        return f"${round(mcap / 1_000_000, 2)}M"
    elif mcap > 1_000:
        return f"${round(mcap / 1_000, 2)}k"
    else:
        return f"${int(mcap)}"

# Filtrar parelles amb criteris amplis
def filter_pairs(pairs):
    tokens_bons = []
    for p in pairs:
        try:
            liquidity = float(p.get("liquidityUsd", 0))
            volume = float(p.get("volumeUsd", 0))
            change = float(p.get("priceChange", {}).get("h1", 0))
            mcap = liquidity * 2  # estimació bàsica
            name = p.get("baseToken", {}).get("name", "Sense nom")
            url = p.get("url")

            if 15_000 <= mcap <= 30_000_000 and volume > 5_000 and change > -20:
                tokens_bons.append({
                    "nom": name,
                    "mcap": format_market_cap(mcap),
                    "url": url
                })
        except:
            continue
    return tokens_bons

# Comandes de Telegram
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Hola! Envia /tokens per veure noves gemmes a Solana 🚀")

def tokens(update: Update, context: CallbackContext):
    update.message.reply_text("🔍 Cercant tokens recents a Solana...")
    results = filter_pairs(get_solana_pairs())
    if results:
        for p in results[:10]:  # mostra com a màxim 10 tokens
            msg = (
                f"🚀 {p['nom']}\n"
                f"📈 Market Cap estimat: {p['mcap']}\n"
                f"🔗 {p['url']}"
            )
            update.message.reply_text(msg)
    else:
        update.message.reply_text("No s'han trobat tokens que compleixin els filtres.")

# Dispatcher i handlers
dispatcher = Dispatcher(bot, update_queue=None, use_context=True)
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("tokens", tokens))

# Webhook segur
@app.route(f"/{WEBHOOK_SECRET}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK"

@app.route("/", methods=["GET"])
def home():
    return "Bot actiu 🚀"

# Inici de l'app Flask
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
