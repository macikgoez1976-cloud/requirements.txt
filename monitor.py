import requests
import yfinance as yf

# --- KONFIGURATION ---
NTFY_TOPIC = "mein_trading_alarm_123" 
NTFY_URL = f"https://ntfy.sh/{NTFY_TOPIC}"

# Liste deiner Indizes
assets = {
    "DAX": "^GDAXI",
    "MDAX": "MDAX.DE",
    "TecDAX": "TECDAX.DE",
    "Dow Jones": "^DJI",
    "S&P 500": "^GSPC"
}

def send_push(message):
    try:
        requests.post(NTFY_URL, data=message.encode('utf-8'))
        print(f"Push gesendet: {message}")
    except Exception as e:
        print(f"Fehler: {e}")

def check_market():
    print("Starte Markt-Check...")
    
    for name, ticker in assets.items():
        try:
            # Wir laden 250 Tage, um genug Daten für den GD100 und GD200 zu haben
            df = yf.download(ticker, period="1y", interval="1d", progress=False)
            
            if df.empty: continue
                
            # Aktueller Kurs
            current = float(df['Close'].iloc[-1])
            prev = float(df['Close'].iloc[-2]) # Kurs von gestern
            
            # Berechnungen
            gd100_curr = float(df['Close'].rolling(window=100).mean().iloc[-1])
            gd200_curr = float(df['Close'].rolling(window=200).mean().iloc[-1])
            
            gd100_prev = float(df['Close'].rolling(window=100).mean().iloc[-2])
            gd200_prev = float(df['Close'].rolling(window=200).mean().iloc[-2])
            
            # Prüfen auf Kreuzung (Kurs kreuzt von unten nach oben)
            # GD100 Kreuzung
            if prev <= gd100_prev and current > gd100_curr:
                send_push(f"ALARM: {name} hat GD100 nach oben gekreuzt! Kurs: {current:.2f}")
            
            # GD200 Kreuzung
            if prev <= gd200_prev and current > gd200_curr:
                send_push(f"ALARM: {name} hat GD200 nach oben gekreuzt! Kurs: {current:.2f}")
                
        except Exception as e:
            print(f"Fehler bei {name}: {e}")

if __name__ == "__main__":
    check_market()
