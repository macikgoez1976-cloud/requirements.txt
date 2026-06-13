import requests
import yfinance as yf

# --- KONFIGURATION ---
NTFY_TOPIC = "mein_trading_alarm_123" 
NTFY_URL = f"https://ntfy.sh/{NTFY_TOPIC}"

# Liste der Indizes (und Krypto)
assets = {
    "DAX": "^GDAXI",
    "MDAX": "MDAX.DE",
    "TecDAX": "TECDAX.DE",
    "Dow Jones": "^DJI",
    "S&P 500": "^GSPC",
    "Bitcoin": "BTC-USD"
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
            # 250 Tage für GD-Berechnung
            df = yf.download(ticker, period="1y", interval="1d", progress=False)
            if df.empty: continue
                
            current = float(df['Close'].iloc[-1])
            prev = float(df['Close'].iloc[-2])
            
            gd100_curr = float(df['Close'].rolling(window=100).mean().iloc[-1])
            gd200_curr = float(df['Close'].rolling(window=200).mean().iloc[-1])
            gd100_prev = float(df['Close'].rolling(window=100).mean().iloc[-2])
            gd200_prev = float(df['Close'].rolling(window=200).mean().iloc[-2])
            
            # --- LONG LOGIK (Kurs über GD) ---
            if prev <= gd100_prev and current > gd100_curr:
                send_push(f"LONG-ALARM: {name} über GD100! Kurs: {current:.2f}")
            if prev <= gd200_prev and current > gd200_curr:
                send_push(f"LONG-ALARM: {name} über GD200! Kurs: {current:.2f}")
            
            # --- SHORT LOGIK (Kurs unter GD) ---
            if prev >= gd100_prev and current < gd100_curr:
                send_push(f"SHORT-ALARM: {name} unter GD100! Kurs: {current:.2f}")
            if prev >= gd200_prev and current < gd200_curr:
                send_push(f"SHORT-ALARM: {name} unter GD200! Kurs: {current:.2f}")
                
        except Exception as e:
            print(f"Fehler bei {name}: {e}")

if __name__ == "__main__":
    check_market()
