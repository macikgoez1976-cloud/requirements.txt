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
    # Manuelle, saubere Listen für maximale Stabilität
    stock_lists = {
        "DAX": ["ADS.DE", "AIR.DE", "ALV.DE", "BAS.DE", "BAYN.DE", "BMW.DE", "CBK.DE", "CON.DE", "DB1.DE", "DBK.DE", "DPW.DE", "DTE.DE", "DTG.DE", "EON.DE", "FRE.DE", "IFX.DE", "MBG.DE", "MUV2.DE", "RWE.DE", "SAP.DE", "SIE.DE", "VOW3.DE"],
        "MDAX": ["HNR1.DE", "LHA.DE", "LEG.DE", "KGX.DE", "TALK.DE", "EVK.DE", "FRA.DE", "BOSS.DE", "PUM.DE", "SY1.DE"],
        "SDAX": ["SDF.DE", "BC8.DE", "PNE3.DE", "WAF.DE", "HDD.DE", "G1A.DE"]
    }
    
    # Falls der Index nicht in unserer Liste ist, nehmen wir den DAX als Fallback
    ticker_list = stock_lists.get(index_name, stock_lists["DAX"])
    hits = []

    for ticker_symbol in ticker_list:
        try:
            stock = yf.Ticker(ticker_symbol)
            # Wir holen 5 Tage Stunden-Daten
            hist = stock.history(period="5d", interval="1h")
            
            if hist.empty or len(hist) < 5:
                continue
            
            # Aktuelles Volumen (letzte Stunde)
            current_vol = hist['Volume'].iloc[-1]
            # Durchschnittliches Volumen der letzten 20 Handelsstunden
            avg_vol = hist['Volume'].tail(20).mean()
            
            if avg_vol == 0: continue
            vol_factor = round(current_vol / avg_vol, 2)
            
            # SEHR SENSIBEL: Ab 1.2x (damit du jetzt sofort Ergebnisse siehst!)
            if vol_factor >= 1.2:
                zeit = datetime.now().strftime("%H:%M")
                news = stock.news
                top_news = news[0]['title'] if news else "Keine aktuellen News"
                
                # Chart Link & Status
                chart_url = f"https://de.finance.yahoo.com/quote/{ticker_symbol}"
                status = "🔥" if vol_factor >= 2.0 else "🟢"
                
                hits.append({
                    "Uhrzeit": zeit,
                    "Status": status,
                    "Aktie": f"[{ticker_symbol.replace('.DE', '')}]({chart_url})",
                    "Vol-Faktor": vol_factor,
                    "Top-News": top_news
                })
        except:
            continue
                
    if hits:
        hits = sorted(hits, key=lambda x: x['Vol-Faktor'], reverse=True)
        for h in hits:
            h['Vol-Faktor'] = f"{h['Vol-Faktor']}x"
            
    return hits
