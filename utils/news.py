import feedparser

def get_crypto_news(limit=3):
    rss_url = "https://cryptopanic.com/feed/rss/"
    feed = feedparser.parse(rss_url)

    news_items = []
    for entry in feed.entries[:limit]:
        news_items.append({
            "title": entry.title,
            "url": entry.link
        })

    return news_items