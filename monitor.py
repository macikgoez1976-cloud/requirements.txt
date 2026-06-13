import requests
import yfinance as yf

# --- KONFIGURATION ---
# Dein festgelegter Topic-Name für die Push-Benachrichtigungen
NTFY_TOPIC = "mein_trading_alarm_123" 
NTFY_URL = f"https://ntfy.sh/{NTFY_TOPIC}"

# Liste der Indizes, die überwacht werden sollen
assets = {
    "DAX": "^GDAXI",
    "S&P 500": "^GSPC",
    "Nasdaq": "^IXIC"
}

def send_push(message):
    """Sendet eine Nachricht an deinen ntfy-Topic."""
    try:
        requests.post(NTFY_URL, data=message.encode('utf-8'))
        print(f"Push gesendet: {message}")
    except Exception as e:
        print(f"Fehler beim Senden der Push-Nachricht: {e}")

def check_market():
    """Prüft die Indizes und vergleicht den aktuellen Kurs mit dem GD200."""
    print("Starte Markt-Check...")
    
    for name, ticker in assets.items():
        try:
            # Lade Daten für 1 Jahr (benötigt für die Berechnung des GD200)
            df = yf.download(ticker, period="1y", interval="1d", progress=False)
            
            if df.empty:
                print(f"Keine Daten für {name} erhalten.")
                continue
                
            # Extrahiere den aktuellsten Schlusskurs und berechne den GD200
            current_price = float(df['Close'].iloc[-1])
            gd200 = float(df['Close'].rolling(window=200).mean().iloc[-1])
            
            print(f"{name}: Kurs {current_price:.2f} | GD200: {gd200:.2f}")
            
            # Logik: Prüfen, ob der Kurs über dem GD200 liegt
            if current_price > gd200:
                message = f"ALARM: {name} über GD200! Kurs: {current_price:.2f} (GD200: {gd200:.2f})"
                send_push(message)
                
        except Exception as e:
            print(f"Fehler bei der Berechnung für {name}: {e}")

if __name__ == "__main__":
    check_market()
