import yfinance as yf
import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime
import time

# --- KONFIGURATION ---
TICKER_LISTS = {
    "DAX": ["ADS.DE", "AIR.DE", "ALV.DE", "BAS.DE", "BAYN.DE", "BMW.DE", "CBK.DE", "DBK.DE", "DHL.DE", "DTE.DE", "EON.DE", "IFX.DE", "MBG.DE", "MUV2.DE", "RWE.DE", "SAP.DE", "SIE.DE", "VOW3.DE"],
    "MDAX": ["HNR1.DE", "LHA.DE", "LEG.DE", "KGX.DE", "TALK.DE", "EVK.DE", "FRA.DE", "BOSS.DE", "PUM.DE", "WAF.DE"],
    "Dow Jones": ["AAPL", "MSFT", "GS", "JPM", "V", "AXP", "BA", "CAT", "DIS", "KO"],
    "S&P 500": ["NVDA", "TSLA", "AMZN", "GOOGL", "META", "AMD", "NFLX"]
}

def run_asperg_scan(index_name, interval):
    selected = TICKER_LISTS.get(index_name)
    hits = []
    progress_bar = st.progress(0)
    
    for i, ticker in enumerate(selected):
        try:
            stock = yf.Ticker(ticker)
            # Wir holen 5 Tage Daten, um einen sauberen Durchschnitt zu haben
            hist = stock.history(period="5d", interval=interval)
            
            if len(hist) >= 3:
                current_vol = hist['Volume'].iloc[-1]
                avg_vol = hist['Volume'].tail(10).mean()
                vol_factor = round(current_vol / avg_vol, 2)
                
                # Kurs-Performance der aktuellen Kerze
                perf = round(((hist['Close'].iloc[-1] - hist['Open'].iloc[-1]) / hist['Open'].iloc[-1]) * 100, 2)
                
                # Wir nehmen alles ab 0.3x auf, damit die Tabelle nicht leer bleibt
                if vol_factor >= 0.3:
                    hits.append({
                        "Ticker": ticker.replace(".DE", ""),
                        "Vol-Faktor": vol_factor,
                        "Perf %": perf,
                        "Preis": round(hist['Close'].iloc[-1], 2)
                    })
            time.sleep(0.05)
            progress_bar.progress((i + 1) / len(selected))
        except:
            continue
    return pd.DataFrame(hits) if hits else None

# --- UI ---
st.set_page_config(page_title="Projekt Asperg", layout="wide")

if "auth" not in st.session_state:
    st.session_state.auth = False

with st.sidebar:
    st.title("🚀 Asperg Scanner")
    if not st.session_state.auth:
        pwd = st.text_input("Passwort", type="password")
        if st.button("Einloggen"):
            if pwd == st.secrets["APP_PASSWORD"]:
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("Falsch!")
    else:
        st.success("Bereit")
        idx_choice = st.selectbox("Markt", list(TICKER_LISTS.keys()))
        int_choice = st.select_slider("Intervall", options=["15m", "30m", "1h"], value="1h")
        if st.button("Logout"):
            st.session_state.auth = False
            st.rerun()

# Hauptfenster
if st.session_state.auth:
    st.write(f"### Aktueller Fokus: {idx_choice} ({int_choice})")
    # Der Button zum Scannen muss im Hauptfenster oder Sidebar sein, 
    # aber die Variablen müssen existieren
    if st.button("Markt jetzt scannen"):
        df = run_asperg_scan(idx_choice, int_choice)
        if df is not None:
            # Das neue Balkendiagramm
            fig = px.bar(df, x='Ticker', y='Vol-Faktor', color='Perf %', 
                         color_continuous_scale='RdYlGn', title="Volumen-Ausreißer")
            st.plotly_chart(fig, use_container_width=True)
            
            # Die Tabelle
            st.table(df.sort_values("Vol-Faktor", ascending=False))
        else:
            st.info("Keine Bewegungen gefunden.")
else:
    st.info("Bitte einloggen.")
