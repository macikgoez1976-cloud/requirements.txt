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
        url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message}"
        requests.get(url)
    except:
        pass

def run_asperg_scan(index_name):
    stock_data = PyTickerSymbols()
    indices = [index_name]
    hits = []

    for index in indices:
        stocks = stock_data.get_stocks_by_index(index)
        
        for s in stocks:
            try:
                ticker_symbol = s['symbols'][0]['yahoo']
                name = s['name']
                
                stock = yf.Ticker(ticker_symbol)
                # Wir nutzen '1d' für die Historie und '1h' für den aktuellen Check
                hist = stock.history(period="3d", interval="1h")
                
                if len(hist) < 3: continue
                
                current_vol = hist['Volume'].iloc[-1]
                avg_vol = hist['Volume'].mean()
                
                vol_factor = round(current_vol / avg_vol, 2) if avg_vol > 0 else 0
                
                # SENSIBLERER FILTER: Ab 1.3x statt 2.0x für den Vormittag
                if vol_factor >= 1.3:
                    zeit = datetime.now().strftime("%H:%M")
                    
                    # NEWS & CHART-LINK
                    news = stock.news
                    top_news = news[0]['title'] if news else "Keine aktuellen News"
                    chart_url = f"https://de.finance.yahoo.com/quote/{ticker_symbol}/chart"
                    
                    # LINK-FORMATIERUNG (Markdown für die Tabelle)
                    display_name = f"[{name}]({chart_url})"
                    
                    # FARB-LOGIK (Ampel-Logik verfeinert)
                    ampel = "🟢" if vol_factor < 2.0 else "🔥"
                    
                    hits.append({
                        "Uhrzeit": zeit,
                        "Status": ampel,
                        "Aktie": display_name,
                        "Vol-Faktor": vol_factor,
                        "Top-News": top_news
                    })
            except:
                continue
                
    if hits:
        # Sortierung nach höchstem Volumen
        hits = sorted(hits, key=lambda x: x['Vol-Faktor'], reverse=True)
        # Formatierung für die Anzeige
        for h in hits:
            h['Vol-Faktor'] = f"{h['Vol-Faktor']}x"
        
    return hits
