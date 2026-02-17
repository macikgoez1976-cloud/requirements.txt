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
    # Die stabilen .DE (XETRA) Ticker
    dax_list = ["ADS.DE", "AIR.DE", "ALV.DE", "BAS.DE", "BAYN.DE", "BMW.DE", "BNR.DE", "CBK.DE", "CON.DE", "DB1.DE", "DBK.DE", "DHL.DE", "DTE.DE", "DTG.DE", "EON.DE", "FRE.DE", "HEI.DE", "HEN3.DE", "IFX.DE", "MBG.DE", "MRK.DE", "MUV2.DE", "P911.DE", "RWE.DE", "SAP.DE", "SIE.DE", "SY1.DE", "VOW3.DE", "ZAL.DE"]
    mdax_list = ["HNR1.DE", "LHA.DE", "LEG.DE", "KGX.DE", "TALK.DE", "EVK.DE", "FRA.DE", "BOSS.DE", "PUM.DE", "G1A.DE", "WAF.DE", "SDF.DE", "EVT.DE", "NDX1.DE", "JUN3.DE"]
    
    selected_tickers = dax_list if index_name == "DAX" else mdax_list
    hits = []

    for ticker in selected_tickers:
        try:
            stock = yf.Ticker(ticker)
            # Wir bleiben bei '2d', da dies vorhin den Erfolg brachte
            hist = stock.history(period="2d")
            
            if hist.empty or len(hist) < 2:
                continue
            
            # Die Logik vom erfolgreichen Test: Heute vs. Gestern
            current_vol = hist['Volume'].iloc[-1]
            prev_vol = hist['Volume'].iloc[-2]
            
            if prev_vol == 0: continue
            vol_factor = round(current_vol / prev_vol, 2)
            
            # Signale ab 1.2x (Du kannst das später auf 2.0x erhöhen)
            if vol_factor >= 1.2:
                zeit = datetime.now().strftime("%H:%M")
                
                # Status-Icon
                status = "🔥" if vol_factor >= 2.0 else "🟢"
                chart_url = f"https://de.finance.yahoo.com/quote/{ticker}"
                
                # News (optional, falls Yahoo mitspielt)
                try:
                    news_title = stock.news[0]['title']
                except:
                    news_title = "Keine News aktuell"
                
                hits.append({
                    "Uhrzeit": zeit,
                    "Status": status,
                    "Aktie": f"[{ticker.replace('.DE', '')}]({chart_url})",
                    "Vol-Faktor": vol_factor,
                    "Top-News": news_title
                })
        except:
            continue
            
    if hits:
        hits = sorted(hits, key=lambda x: x['Vol-Faktor'], reverse=True)
        # Kurze Telegram-Info bei Top-Hits
        if hits[0]['Vol-Faktor'] >= 2.0:
            send_telegram_message(f"🚀 Top-Volumen: {hits[0]['Aktie']} mit {hits[0]['Vol-Faktor']}x")

        for h in hits:
            h['Vol-Faktor'] = f"{h['Vol-Faktor']}x"
                
    return hits
