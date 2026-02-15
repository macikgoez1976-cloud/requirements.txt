import yfinance as yf
import pandas as pd
import requests
import os
from pytickersymbols import PyTickerSymbols

# --- KONFIGURATION AUS GITHUB SECRETS ---
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def send_telegram_msg(message):
    if not TOKEN or not CHAT_ID:
        print("Fehler: Telegram Secrets nicht gefunden!")
        return
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    requests.post(url, data=payload)

def get_sentiment_ampel(ticker):
    search_term = ticker.split('.')[0].lower()
    url = f"https://www.finanznachrichten.de/aktien-nachrichten/{search_term}.htm"
    try:
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(res.text, 'html.parser')
        headline = soup.find('a', class_='link-beratung')
        if headline:
            text = headline.get_text().lower()
            pos = ["plus", "gewinn", "hoch", "steigt", "rekord", "kauf", "prognose"]
            neg = ["minus", "verlust", "senkt", "fällt", "warnung", "enttäuschung"]
            score = sum(1 for w in pos if w in text) - sum(1 for w in neg if w in text)
            ampel = "🟢" if score > 0 else "🔴" if score < 0 else "🟡"
            return f"{ampel} {headline.get_text()}"
    except: pass
    return "⚪ Keine News gefunden"

def run_asperg_scan():
    stock_data = PyTickerSymbols()
    # Wir scannen DAX und MDAX für maximale Trefferquote
    indices = ["DAX", "MDAX"]
    hits = []

    for index in indices:
        stocks = stock_data.get_stocks_by_index(index)
        tickers = [s['symbols'][0]['yahoo'] for s in stocks if s['symbols']]
        
        for t in tickers:
            try:
                df = yf.Ticker(t).history(period="1y")
                if len(df) < 50: continue
                
                curr_p = df['Close'].iloc[-1]
                high_52w = df['High'].iloc[:-1].max()
                vol_avg = df['Volume'].tail(20).mean()
                vol_curr = df['Volume'].iloc[-1]
                
                # Filter: Innerhalb 2% vom Hoch & 1.5x Volumen
                if curr_p >= (high_52w * 0.98) and (vol_curr > vol_avg * 1.5):
                    news_info = get_sentiment_ampel(t)
                    hits.append(f"🚀 *{t}*\nPreis: {curr_p:.2f}€\nVolumen: {vol_curr/vol_avg:.1f}x\nNews: {news_info}")
            except: continue

    if hits:
        message = "🔔 *PROJEKT ASPERG ALERT*\n\n" + "\n\n".join(hits)
        send_telegram_msg(message)
    else:
        print("Scan beendet: Keine Treffer.")

if __name__ == "__main__":
    run_asperg_scan()
