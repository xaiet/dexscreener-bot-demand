import time
import threading
import os

NOTIF_CHAT_ID = os.getenv("NOTIF_CHAT_ID")

def iniciar_notificacions(bot):
    def loop():
        while True:
            try:
                print("[LOG] Enviant notificació automàtica de prova...")
                if NOTIF_CHAT_ID:
                    bot.send_message(
                        chat_id=NOTIF_CHAT_ID,
                        text="🚨 Notificació automàtica de prova enviada correctament.",
                        parse_mode="Markdown",
                        disable_web_page_preview=True
                    )
                else:
                    print("[DEBUG] NOTIF_CHAT_ID no està definit.")
            except Exception as e:
                print("[LOG] Error al bucle de notificació:", e)
            time.sleep(60)

    threading.Thread(target=loop, daemon=True).start()