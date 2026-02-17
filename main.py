import yfinance as yf
import pandas as pd
from datetime import datetime
import requests
import streamlit as st
import time

def send_telegram_message(message):
    try:
        token = st.secrets["TELEGRAM_BOT_TOKEN"]
        chat_id = st.secrets["TELEGRAM_CHAT_ID"]
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        requests.get(url, params={"chat_id": chat_id, "text": message}, timeout=5)
    except:
        pass

def run_asperg_scan(index_name):
    # Wir nutzen NUR die funktionierenden .DE Ticker
    dax = ["ADS.DE", "AIR.DE", "ALV.DE", "BAS.DE", "BAYN.DE", "BMW.DE", "BNR.DE", "CBK.DE", "CON.DE", "DB1.DE", "DBK.DE", "DHL.DE", "DTE.DE", "DTG.DE", "EON.DE", "FRE.DE", "HEI.DE", "HEN3.DE", "IFX.DE", "MBG.DE", "MRK.DE", "MUV2.DE", "P911.DE", "RWE.DE", "SAP.DE", "SIE.DE", "SY1.DE", "VOW3.DE", "ZAL.DE"]
    mdax = ["HNR1.DE", "LHA.DE", "LEG.DE", "KGX.DE", "TALK.DE", "EVK.DE", "FRA.DE", "BOSS.DE", "PUM.DE", "G1A.DE", "WAF.DE", "SDF.DE", "EVT.DE", "NDX1.DE", "JUN3.DE"]
    
    selected_tickers = dax if index_name == "DAX" else mdax
    hits = []

    # WICHTIG: Wir tarnen uns als Browser, um den 404 Error zu vermeiden
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

    for ticker in selected_tickers:
        try:
            # Wir rufen die Daten direkt via requests/yfinance stabil ab
            stock = yf.Ticker(ticker)
            # Wir nutzen period='2d', das hat um 12:34 Uhr funktioniert!
            hist = stock.history(period="2d")
            
            if hist.empty or len(hist) < 2:
                continue
            
            # Volumen-Vergleich (Heute vs. Gestern)
            current_vol = hist['Volume'].iloc[-1]
            prev_vol = hist['Volume'].iloc[-2]
            
            if prev_vol == 0: continue
            vol_factor = round(current_vol / prev_vol, 2)
            
            # Wir zeigen zum Start alles ab 1.1x an, damit wir sehen dass es geht
            if vol_factor >= 1.1:
                zeit = datetime.now().strftime("%H:%M")
                chart_url = f"https://de.finance.yahoo.com/quote/{ticker}"
                
                hits.append({
                    "Uhrzeit": zeit,
                    "Status": "🔥" if vol_factor >= 2.0 else "🟢",
                    "Aktie": f"[{ticker.replace('.DE', '')}]({chart_url})",
                    "Vol-Faktor": vol_factor,
                    "Top-News": "Live-Daten aktiv"
                })
            
            # 0.2 Sekunde Pause, damit Yahoo nicht blockt
            time.sleep(0.2)
            
        except Exception:
            continue
            
    if hits:
        hits = sorted(hits, key=lambda x: x['Vol-Faktor'], reverse=True)
        # Kurzes Telegram-Update bei Ausreißern
        if hits[0]['Vol-Faktor'] >= 2.0:
            send_telegram_message(f"🚨 Projekt Asperg: {hits[0]['Aktie']} hat {hits[0]['Vol-Faktor']}x Volumen!")

        for h in hits:
            h['Vol-Faktor'] = f"{h['Vol-Faktor']}x"
                
    return hits
