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
    except Exception as e:
        print(f"Telegram Fehler: {e}")

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
                # Stunden-Intervall für maximale Aktualität
                hist = stock.history(period="5d", interval="1h")
                
                if len(hist) < 5: continue
                
                current_vol = hist['Volume'].iloc[-1]
                avg_vol = hist['Volume'].iloc[:-1].mean()
                vol_factor = round(current_vol / avg_vol, 2) if avg_vol > 0 else 0
                
                # Filter: Ab 2.0x Volumen schlagen wir Alarm
                if vol_factor >= 2.0:
                    zeit = datetime.now().strftime("%H:%M")
                    news = stock.news
                    top_news = news[0]['title'] if news else "Keine aktuellen News"
                    
                    # Nachricht für Telegram vorbereiten
                    msg = f"🚀 Projekt Asperg Alarm!\n\nAktie: {name}\nIndex: {index_name}\nVolumen: {vol_factor}x\nNews: {top_news}"
                    send_telegram_message(msg)
                    
                    hits.append({
                        "Uhrzeit": zeit,
                        "Aktie": name,
                        "Symbol": ticker_symbol,
                        "Vol-Faktor": f"{vol_factor}x",
                        "Top-News": top_news
                    })
            except:
                continue
                
    if hits:
        hits = sorted(hits, key=lambda x: float(x['Vol-Faktor'].replace('x', '')), reverse=True)
        
    return hits
