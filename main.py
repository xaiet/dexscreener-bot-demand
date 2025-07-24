import os
import threading
import requests
from flask import Flask, request, jsonify
from telegram import Bot, Update
from telegram.ext import Dispatcher

from commands.tendencia import cmd_tendencia
from commands.status import show_status
from commands.id import show_id
from commands.whales import cmd_whales
from commands.grans import grans
from notifier import iniciar_notificacions
from reporter import TokenInsightReporter

# Variables d'entorn
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "ruta-secreta")
PORT = int(os.getenv("PORT", 5000))
NOTIF_CHAT_ID = os.getenv("NOTIF_CHAT_ID")

# Inicia bot i Flask
bot = Bot(token=BOT_TOKEN)
app = Flask(__name__)
dispatcher = Dispatcher(bot, update_queue=None, use_context=True)

# Registra handlers
dispatcher.add_handler(cmd_tendencia)
dispatcher.add_handler(show_status)
dispatcher.add_handler(show_id)
dispatcher.add_handler(cmd_whales)
dispatcher.add_handler(grans)

# Webhook endpoint
@app.route(f"/{WEBHOOK_SECRET}", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True)
        update = Update.de_json(data, bot)
        dispatcher.process_update(update)
        return "OK"
    except Exception as e:
        print("[LOG] Error processant webhook:", e)
        return jsonify({"error": "Error processant la petició"}), 500

@app.route("/")
def home():
    return "Bot actiu amb Birdeye ✅"

# 🔁 Pinger per evitar que Render mati el servei
def autopinger():
    while True:
        try:
            print("[LOG] Pingant el propi servei per mantenir-lo viu...")
            requests.get("https://dexscreener-bot-demand.onrender.com/") # URL del servei
        except Exception as e:
            print(f"[LOG] Error al fer autoping: {e}")
        time.sleep(1800)  # cada 30 minuts

if __name__ == "__main__":
    print("[LOG] Iniciant bot i serveis...")

    # Inicia notificacions automàtiques cada hora
    iniciar_notificacions(bot)

    # Inicia el reporter de TokenInsight
    if NOTIF_CHAT_ID:
        reporter = TokenInsightReporter(bot, NOTIF_CHAT_ID)
        reporter_thread = threading.Thread(target=reporter.run, daemon=True)
        reporter_thread.start()
        print("[LOG] Reporter TokenInsight actiu.")
    else:
        print("[LOG] Variable NOTIF_CHAT_ID no definida. No s'inicia reporter.")

    # Inicia autopinger per evitar que Render mati el procés
    threading.Thread(target=autopinger, daemon=True).start()

    # Inicia Flask
    app.run(host="0.0.0.0", port=PORT)
