import yfinance as yf
from pytickersymbols import PyTickerSymbols
import pandas as pd
from datetime import datetime
import requests
import streamlit as st

def send_telegram_message(message):
    try:
        token = st.secrets["TELEGRAM_BOT_TOKEN"]
        chat_id = st.secrets["TELEGRAM_CHAT_ID"]
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        params = {"chat_id": chat_id, "text": message}
        requests.get(url, params=params, timeout=5)
    except:
        pass

def run_asperg_scan(index_name):
    stock_data = PyTickerSymbols()
    # Wir holen die Aktien für den gewählten Index
    stocks = stock_data.get_stocks_by_index(index_name)
    hits = []

    for s in stocks:
        try:
            # Wir nehmen das erste verfügbare Yahoo-Symbol
            ticker_symbol = s['symbols'][0]['yahoo']
            name = s['name']
            
            # WICHTIG: Wir holen nur die allernötigsten Daten für heute & gestern
            stock = yf.Ticker(ticker_symbol)
            hist = stock.history(period="2d", interval="1h")
            
            # Wenn keine Daten kommen (siehe dein Error-Log), überspringen wir sofort
            if hist.empty or len(hist) < 2:
                continue
            
            # Volumen der letzten Stunde vs. Durchschnitt der letzten 2 Tage
            current_vol = hist['Volume'].iloc[-1]
            avg_vol = hist['Volume'].mean()
            
            if avg_vol == 0: continue
            vol_factor = round(current_vol / avg_vol, 2)
            
            # Wir setzen die Schwelle zum Testen jetzt mal auf 1.1x 
            # damit du DEFINITIV siehst, ob er überhaupt arbeitet.
            if vol_factor >= 1.1:
                zeit = datetime.now().strftime("%H:%M")
                
                # News & Link
                news = stock.news
                top_news = news[0]['title'] if news else "Keine aktuellen News"
                chart_url = f"https://de.finance.yahoo.com/quote/{ticker_symbol}"
                
                # Formatierung
                status = "🔥" if vol_factor >= 2.0 else "🟢"
                display_name = f"[{name}]({chart_url})"
                
                hits.append({
                    "Uhrzeit": zeit,
                    "Status": status,
                    "Aktie": display_name,
                    "Vol-Faktor": vol_factor,
                    "Top-News": top_news
                })
        except Exception as e:
            # Wenn eine einzelne Aktie (wie RTL) hakt, einfach weitermachen
            continue
                
    if hits:
        # Sortieren nach Stärke des Volumens
        hits = sorted(hits, key=lambda x: x['Vol-Faktor'], reverse=True)
        # Für die Anzeige das 'x' anhängen
        for h in hits:
            h['Vol-Faktor'] = f"{h['Vol-Faktor']}x"
            
    return hits
