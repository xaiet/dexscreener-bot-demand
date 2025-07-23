import schedule
import time
from datetime import datetime
from utils.analyzer import analyze_token
from utils.news import get_crypto_news
from utils.filters import get_top_gainers 

class TokenInsightReporter:
    def __init__(self, bot, chat_id):
        self.bot = bot
        self.chat_id = chat_id

    def run(self):
        schedule.every().day.at("08:00").do(self.report)
        schedule.every().day.at("20:00").do(self.report)
        print("📅 Programador actiu: informes a les 08:00 i 20:00")

        while True:
            schedule.run_pending()
            time.sleep(30)

    def report(self):
        print(f"📊 Generant informe a {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        top_tokens = get_top_gainers(limit=7)

        if not top_tokens:
            self.bot.send_message(chat_id=self.chat_id, text="❌ No s'han trobat tokens destacats.")
            return

        message = "📈 *Tokens amb més pujada:*"
        for token in top_tokens:
            reason = analyze_token(token)
            message += f"\n🔹 *{token['symbol']}* (+{token['priceChangePct']}%)\n"
            message += f"Motiu possible: {reason}\n"
            message += f"[Dexscreener]({token['url']})\n"

        news = get_crypto_news(limit=3)
        if news:
            message += "\n📰 *Notícies destacades del món cripto:*"
            for n in news:
                message += f"• [{n['title']}]({n['url']})\n"

        self.bot.send_message(chat_id=self.chat_id, text=message, parse_mode="Markdown")