import yfinance as yf
import pandas as pd
from datetime import datetime
import requests
import streamlit as st

def send_telegram_message(message):
    try:
        token = st.secrets["TELEGRAM_BOT_TOKEN"]
        chat_id = st.secrets["TELEGRAM_CHAT_ID"]
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        requests.get(url, params={"chat_id": chat_id, "text": message}, timeout=5)
    except:
        pass

def run_asperg_scan(index_name):
    # Saubere XETRA-Listen für maximale Stabilität
    dax_tickers = ["ADS.DE", "AIR.DE", "ALV.DE", "BAS.DE", "BAYN.DE", "BMW.DE", "BNR.DE", "CBK.DE", "CON.DE", "DB1.DE", "DBK.DE", "DHL.DE", "DTE.DE", "DTG.DE", "EON.DE", "FRE.DE", "HEI.DE", "HEN3.DE", "IFX.DE", "MBG.DE", "MRK.DE", "MUV2.DE", "P911.DE", "RWE.DE", "SAP.DE", "SIE.DE", "SY1.DE", "VOW3.DE", "ZAL.DE"]
    mdax_tickers = ["HNR1.DE", "LHA.DE", "LEG.DE", "KGX.DE", "TALK.DE", "EVK.DE", "FRA.DE", "BOSS.DE", "PUM.DE", "G1A.DE", "WAF.DE", "SDF.DE"]
    
    selected_tickers = dax_tickers if index_name == "DAX" else mdax_tickers
    hits = []

    for ticker in selected_tickers:
        try:
            stock = yf.Ticker(ticker)
            # Wir schauen uns die letzten 3 Tage auf Stundenbasis an
            hist = stock.history(period="3d", interval="1h")
            
            if len(hist) < 5: continue
            
            current_vol = hist['Volume'].iloc[-1]
            # Durchschnitt der letzten 15 Handelsstunden
            avg_vol = hist['Volume'].tail(15).mean()
            
            if avg_vol == 0: continue
            vol_factor = round(current_vol / avg_vol, 2)
            
            # WIRKLICHE SIGNALE: Ab 1.5x wird es interessant
            if vol_factor >= 1.2:
                zeit = datetime.now().strftime("%H:%M")
                
                # Status-Symbol
                if vol_factor >= 3.0: status = "🟥" # Extrem
                elif vol_factor >= 2.0: status = "🔥" # Hoch
                else: status = "🟢" # Auffällig
                
                chart_url = f"https://de.finance.yahoo.com/quote/{ticker}"
                
                # News abrufen
                news = stock.news
                title = news[0]['title'] if news else "Keine News"
                
                hits.append({
                    "Uhrzeit": zeit,
                    "Status": status,
                    "Aktie": f"[{ticker.replace('.DE', '')}]({chart_url})",
                    "Vol-Faktor": vol_factor,
                    "Top-News": title
                })
        except:
            continue
            
    if hits:
        hits = sorted(hits, key=lambda x: x['Vol-Faktor'], reverse=True)
        # Telegram bei echten Ausreißern (> 2.0x)
        top_hit = hits[0]
        if top_hit['Vol-Faktor'] >= 2.0:
            send_telegram_message(f"🚨 Projekt Asperg Alarm! {top_hit['Aktie']} Vol: {top_hit['Vol-Faktor']}x")

        for h in hits:
            h['Vol-Faktor'] = f"{h['Vol-Faktor']}x"
                
    return hits
