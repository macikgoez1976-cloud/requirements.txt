import requests
import yfinance as yf

# --- KONFIGURATION ---
# Ersetze 'DEIN_TOPIC_NAME' mit dem Namen, den du in der ntfy-App abonniert hast.
# WICHTIG: Er muss in der App und hier exakt gleich sein!
NTFY_TOPIC = "DEIN_TOPIC_NAME" 
NTFY_URL = f"https://ntfy.sh/{NTFY_TOPIC}"

# Hier kannst du beliebig weitere Indizes hinzufügen
# Format: "Name": "Ticker-Symbol"
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
    """Prüft die Indizes und vergleicht den Kurs mit dem GD200."""
    print("Starte Markt-Check...")
    
    for name, ticker in assets.items():
        try:
            # Lade Daten für 1 Jahr (benötigt für den GD200)
            df = yf.download(ticker, period="1y", interval="1d", progress=False)
            
            if df.empty:
                print(f"Keine Daten für {name} erhalten.")
                continue
                
            current_price = float(df['Close'].iloc[-1])
            gd200 = float(df['Close'].rolling(window=200).mean().iloc[-1])
            
            print(f"{name}: Kurs {current_price:.2f} | GD200: {gd200:.2f}")
            
            # Logik: Wenn Kurs über GD200 (kannst du hier ändern auf <, falls gewünscht)
            if current_price > gd200:
                message = f"ALARM: {name} über GD200! Kurs: {current_price:.2f} (GD200: {gd200:.2f})"
                send_push(message)
                
        except Exception as e:
            print(f"Fehler bei der Berechnung für {name}: {e}")

if __name__ == "__main__":
    check_market()
