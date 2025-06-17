import time
import threading
import os
from utils.filters import get_filtered_tokens

NOTIF_CHAT_ID = os.getenv("NOTIF_CHAT_ID")


def iniciar_notificacions(bot):
    def loop():
        while True:
            try:
                print("[LOG] Iniciant notificació automàtica...")
                if NOTIF_CHAT_ID:
                    tokens = get_filtered_tokens()
                    if not tokens:
                        print("[LOG] Cap token per notificar.")
                    else:
                        for msg in tokens:
                            bot.send_message(chat_id=NOTIF_CHAT_ID, text=msg, parse_mode="Markdown", disable_web_page_preview=True)
                            time.sleep(2)  # petit delay entre missatges
            except Exception as e:
                print("[LOG] Error al bucle de notificació:", e)
            time.sleep(4 * 3600)  # Esperar 4 hores

    threading.Thread(target=loop, daemon=True).start()