# 📁 Estructura de fitxers:
# .
# ├── main.py                 # Punt d'entrada del servidor i webhook
# ├── commands/
# │   ├── tendencia.py       # Comanda /tendencia
# │   ├── status.py          # Comanda /status
# │   ├── id.py              # Comanda /id
# │   └── whales.py          # Comanda /whales
# └── notifier.py            # Notificacions automàtiques

import os
from flask import Flask, request, jsonify
from telegram import Bot, Update
from telegram.ext import Dispatcher

from commands.tendencia import cmd_tendencia
from commands.status import show_status
from commands.id import show_id
from commands.whales import cmd_whales
from commands.grans import grans
from notifier import iniciar_notificacions

# Carrega variables d'entorn
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "ruta-secreta")
PORT = int(os.getenv("PORT", 5000))

# Inicialitza bot i Flask
bot = Bot(token=BOT_TOKEN)
app = Flask(__name__)
dispatcher = Dispatcher(bot, update_queue=None, use_context=True)


dispatcher.add_handler(cmd_tendencia)
dispatcher.add_handler(show_status)
dispatcher.add_handler(show_id)
dispatcher.add_handler(cmd_whales)
dispatcher.add_handler(grans)
iniciar_notificacions(bot)

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
    print("[LOG] Iniciant servidor Flask...")
    app.run(host="0.0.0.0", port=PORT)
    print(f"[LOG] Servidor iniciat a port {PORT}")

# --- Inici del reporter automàtic ---
from reporter import TokenInsightReporter

if __name__ == "__main__":
    from telegram import Bot
    import threading

    TOKEN = "EL_TEU_TOKEN_TELEGRAM"  # <-- substitueix pel teu token real
    CHAT_ID = "EL_TEU_CHAT_ID"       # <-- substitueix pel teu chat_id real

    bot = Bot(token=TOKEN)
    reporter = TokenInsightReporter(bot, CHAT_ID)

    # S'executa en un fil independent perquè no bloquegi altres funcionalitats
    reporter_thread = threading.Thread(target=reporter.run, daemon=True)
    reporter_thread.start()

    # Aquí pots deixar el bot escoltant com fins ara o qualsevol altre loop
    print("✅ Bot actiu amb reporter automatitzat.")