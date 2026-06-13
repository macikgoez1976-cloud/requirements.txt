import requests
import yfinance as yf
import pandas as pd

# Deine ntfy-Topic-URL
NTFY_URL = "https://ntfy.sh/DEIN_TOPIC_NAME" # Wähle hier einen einzigartigen Namen

# Liste der Indizes, die wir überwachen wollen
assets = {
    "DAX": "^GDAXI",
    "S&P 500": "^GSPC",
    "Nasdaq": "^IXIC"
}

def send_push(message):
    requests.post(NTFY_URL, data=message.encode('utf-8'))

def check_market():
    for name, ticker in assets.items():
        # Lade Daten (letzte 200 Tage + aktuelle)
        df = yf.download(ticker, period="1y", interval="1d")
        
        current_price = df['Close'].iloc[-1]
        gd200 = df['Close'].rolling(window=200).mean().iloc[-1]
        
        print(f"{name}: Kurs {current_price:.2f} | GD200: {gd200:.2f}")
        
        if current_price > gd200:
            send_push(f"ALARM: {name} hat den GD200 überschritten! Kurs: {current_price:.2f}")

if __name__ == "__main__":
    check_market()
