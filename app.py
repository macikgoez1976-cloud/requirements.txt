import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
from pytickersymbols import PyTickerSymbols

# --- KONFIGURATION ---
st.set_page_config(page_title="Projekt Asperg", layout="wide")
stock_data = PyTickerSymbols()

def get_news_and_sentiment(ticker):
    search_term = ticker.split('.')[0].lower()
    url = f"https://www.finanznachrichten.de/aktien-nachrichten/{search_term}.htm"
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=3)
        soup = BeautifulSoup(response.text, 'html.parser')
        headline_tag = soup.find('a', class_='link-beratung')
        if headline_tag:
            headline = headline_tag.get_text()
            # Sentiment Logik
            pos = ["plus", "gewinn", "erhöht", "kauf", "rekord", "top", "prognose"]
            neg = ["minus", "verlust", "senkt", "verkauf", "warnung", "schwach"]
            score = sum(1 for w in pos if w in headline.lower()) - sum(1 for w in neg if w in headline.lower())
            
            ampel = "🟢" if score > 0 else "🔴" if score < 0 else "🟡"
            return headline, ampel
        return "Keine News", "⚪"
    except:
        return "Portal-Fehler", "⚪"

# --- UI ---
st.title("🚀 Projekt Asperg: Der Sentiment-Scanner")
index_choice = st.sidebar.selectbox("Index wählen", ["DAX", "MDAX", "SDAX"])
vol_min = st.sidebar.slider("Mindest-Volumen (Faktor)", 1.0, 3.0, 1.3)

if st.button(f"Scanne {index_choice} & News"):
    stocks = stock_data.get_stocks_by_index(index_choice)
    tickers = [s['symbols'][0]['yahoo'] for s in stocks if s['symbols']]
    
    final_list = []
    progress = st.progress(0)
    
    for i, t in enumerate(tickers):
        try:
            data = yf.Ticker(t).history(period="1y")
            if len(data) < 50: continue
            
            # Analyse
            curr_p = data['Close'].iloc[-1]
            h52 = data['High'].iloc[:-1].max()
            vol_avg = data['Volume'].tail(20).mean()
            vol_curr = data['Volume'].iloc[-1]
            
            # Bedingung: Innerhalb 2% vom Hoch + Volumen-Kick
            if curr_p >= (h52 * 0.98) and (vol_curr / vol_avg) >= vol_min:
                news, ampel = get_news_and_sentiment(t)
                final_list.append({
                    "Ampel": ampel,
                    "Aktie": t,
                    "Preis": f"{curr_p:.2f} €",
                    "Vol-Faktor": f"{vol_curr/vol_avg:.1f}x",
                    "Letzte Schlagzeile": news
                })
        except: pass
        progress.progress((i + 1) / len(tickers))

    if final_list:
        st.table(pd.DataFrame(final_list))
    else:
        st.info("Keine Aktie erfüllt aktuell die Kriterien.")
