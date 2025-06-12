import os
import requests
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, CallbackContext

# Variables d'entorn
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "ruta-secreta")
BIRDEYE_API_KEY = os.getenv("BIRDEYE_API_KEY")
bot = Bot(token=BOT_TOKEN)

app = Flask(__name__)

# Obtenir tokens nous de Solana via Birdeye
def get_new_solana_tokens(limit=10):
    url = "https://public-api.birdeye.so/defi/tokenlist?sort_by=liquidity&order=desc"
    headers = {"x-api-key": BIRDEYE_API_KEY}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code != 200:
            print("Error API Birdeye:", res.text)
            return []
        data = res.json().get("data", [])
        return data[:limit]
    except Exception as e:
        print("Excepció Birdeye:", e)
        return []

# Format Market Cap
def format_market_cap(mcap):
    if not mcap: return "?"
    if mcap > 1_000_000:
        return f"${round(mcap / 1_000_000, 2)}M"
    elif mcap > 1_000:
        return f"${round(mcap / 1_000, 2)}k"
    else:
        return f"${int(mcap)}"

# Comandes Telegram
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Hola! Envia /tokens per veure els tokens més nous a Solana 🚀")

def tokens(update: Update, context: CallbackContext):
    if not BIRDEYE_API_KEY:
        update.message.reply_text("❌ Falten credencials de Birdeye (BIRDEYE_API_KEY)")
        return

    update.message.reply_text("🔍 Buscant els últims tokens creats a Solana...")

    tokens = get_new_solana_tokens(limit=20)
    mostrats = 0

    for t in tokens:
        try:
            name = t.get("name", "Sense nom")
            symbol = t.get("symbol", "")
            address = t.get("address", "N/A")
            mcap = t.get("market_cap", 0)
            liquidity = t.get("liquidity", 0)
            price = t.get("price_usd", "?")

            # Filtres opcionals
            if liquidity < 10000 or mcap < 50000:
                continue

            msg = (
                f"🚀 {name} ({symbol})\n"
                f"📍 {address}\n"
                f"💧 Liquidity: ${round(liquidity):,}\n"
                f"📈 Market Cap: {format_market_cap(mcap)}\n"
                f"💵 Price: ${price}\n"
                f"🔗 https://birdeye.so/token/{address}?chain=solana"
            )
            update.message.reply_text(msg)
            mostrats += 1
        except:
            continue

    if mostrats == 0:
        update.message.reply_text("No s'han trobat tokens que compleixin els filtres.")

# Dispatcher
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
    return "Bot actiu amb Birdeye 🚀"

# Inici de l'app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
