# 📁 Estructura de fitxers:
# .
# ├── main.py                 # Punt d'entrada del servidor i webhook
# ├── commands/
# │   ├── tendencia.py       # Comanda /tendencia
# │   ├── status.py          # Comanda /status
# │   ├── id.py              # Comanda /id
# │   └── whales.py          # Comanda /whales
# └── notifier.py            # Notificacions automàtiques

# ✅ Ara et genero tot aquest codi dividit en fitxers, començant per `main.py`

# ----------- main.py -----------
import os
import time
import threading
from flask import Flask, request, jsonify
from telegram import Bot, Update
from telegram.ext import Dispatcher

from commands.tendencia import cmd_tendencia
from commands.status import show_status
from commands.id import show_id
from commands.whales import cmd_whales
from notifier import iniciar_notificacions
from commands.grans import grans
from commands.dormits import cmd_dormits
from commands.volum import cmd_volum
from commands.descompte import cmd_descompte
from commands.estrena import cmd_estrena

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "ruta-secreta")
PORT = int(os.getenv("PORT", 5000))

bot = Bot(token=BOT_TOKEN)
app = Flask(__name__)

dispatcher = Dispatcher(bot, update_queue=None, use_context=True)
dispatcher.add_handler(cmd_tendencia)
dispatcher.add_handler(show_status)
dispatcher.add_handler(show_id)
dispatcher.add_handler(cmd_whales)
dispatcher.add_handler(grans)

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

if __name__ == "__main__":
    iniciar_notificacions(bot)
    print("[LOG] Iniciant servidor Flask...")
    app.run(host="0.0.0.0", port=PORT)
    print("[LOG] Servidor iniciat a port", PORT)