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
    # Komplette, saubere Listen mit .DE Endung
    dax = ["ADS.DE", "AIR.DE", "ALV.DE", "BAS.DE", "BAYN.DE", "BMW.DE", "BNR.DE", "CBK.DE", "CON.DE", "DB1.DE", "DBK.DE", "DHL.DE", "DTE.DE", "DTG.DE", "EON.DE", "FRE.DE", "HEI.DE", "HEN3.DE", "IFX.DE", "MBG.DE", "MRK.DE", "MUV2.DE", "P911.DE", "RWE.DE", "SAP.DE", "SIE.DE", "SY1.DE", "VOW3.DE", "ZAL.DE"]
    mdax = ["HNR1.DE", "LHA.DE", "LEG.DE", "KGX.DE", "TALK.DE", "EVK.DE", "FRA.DE", "BOSS.DE", "PUM.DE", "G1A.DE", "WAF.DE", "SDF.DE", "EVT.DE", "NDX1.DE", "JUN3.DE", "KBX.DE", "TAG.DE", "CBK.DE"]
    
    selected_tickers = dax if index_name == "DAX" else mdax
    hits = []

    # Fortschrittsbalken für Streamlit
    progress_bar = st.progress(0)
    for i, ticker in enumerate(selected_tickers):
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="2d")
            
            if not hist.empty and len(hist) >= 2:
                current_vol = hist['Volume'].iloc[-1]
                prev_vol = hist['Volume'].iloc[-2]
                
                if prev_vol > 0:
                    vol_factor = round(current_vol / prev_vol, 2)
                    
                    # Ab 0.5x zeigen wir es an, damit die Tabelle nicht leer bleibt
                    if vol_factor >= 0.5:
                        zeit = datetime.now().strftime("%H:%M")
                        chart_url = f"https://de.finance.yahoo.com/quote/{ticker}"
                        
                        # Farbe/Status je nach Stärke
                        if vol_factor >= 1.5: status = "🔥"
                        elif vol_factor >= 1.0: status = "🟢"
                        else: status = "⚪"
                        
                        hits.append({
                            "Uhrzeit": zeit,
                            "Status": status,
                            "Aktie": f"[{ticker.replace('.DE', '')}]({chart_url})",
                            "Vol-Faktor": vol_factor,
                            "Top-News": "Live-Daten"
                        })
            
            # Kurze Pause für Yahoo Stabilität
            time.sleep(0.1)
            progress_bar.progress((i + 1) / len(selected_tickers))
            
        except:
            continue
            
    if hits:
        hits = sorted(hits, key=lambda x: x['Vol-Faktor'], reverse=True)
        # Telegram nur bei echtem Ausbruch über 1.5x
        if hits[0]['Vol-Faktor'] >= 1.5:
            send_telegram_message(f"🚨 Asperg Alarm: {hits[0]['Aktie']} bei {hits[0]['Vol-Faktor']}x!")

        for h in hits:
            h['Vol-Faktor'] = f"{h['Vol-Faktor']}x"
                
    return hits
