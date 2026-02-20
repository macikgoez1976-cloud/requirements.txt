import yfinance as yf
import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime
import time

# --- SETUP ---
TICKER_LISTS = {
    "DAX": ["ADS.DE", "AIR.DE", "ALV.DE", "BAS.DE", "BAYN.DE", "BMW.DE", "CBK.DE", "DBK.DE", "DTE.DE", "EON.DE", "IFX.DE", "MBG.DE", "MUV2.DE", "RWE.DE", "SAP.DE", "SIE.DE", "VOW3.DE"],
    "MDAX": ["HNR1.DE", "LHA.DE", "LEG.DE", "KGX.DE", "TALK.DE", "EVK.DE", "FRA.DE", "BOSS.DE", "PUM.DE", "WAF.DE"],
    "Dow Jones": ["AAPL", "MSFT", "GS", "JPM", "V", "AXP", "BA", "CAT", "DIS", "KO"]
}

def run_asperg_scan(index_name, interval):
    selected = TICKER_LISTS.get(index_name)
    hits = []
    progress_bar = st.progress(0)
    
    for i, ticker in enumerate(selected):
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="5d", interval=interval)
            if not hist.empty and len(hist) >= 2:
                current_vol = hist['Volume'].iloc[-1]
                avg_vol = hist['Volume'].tail(10).mean()
                vol_factor = round(current_vol / avg_vol, 2)
                
                # Performance der Kerze
                perf = round(((hist['Close'].iloc[-1] - hist['Open'].iloc[-1]) / hist['Open'].iloc[-1]) * 100, 2)
                
                hits.append({
                    "Ticker": ticker.replace(".DE", ""),
                    "Vol-Faktor": vol_factor,
                    "Perf %": perf,
                    "Preis": round(hist['Close'].iloc[-1], 2)
                })
            progress_bar.progress((i + 1) / len(selected))
        except: continue
    return pd.DataFrame(hits) if hits else None

# --- UI ---
st.set_page_config(page_title="Projekt Asperg", layout="wide")

if "auth_ok" not in st.session_state:
    st.session_state.auth_ok = False

with st.sidebar:
    st.title("🛡️ Projekt Asperg")
    
    # LOGIN-LOGIK (Nacheinander)
    if not st.session_state.auth_ok:
        user_pwd = st.text_input("Passwort", type="password", key="login_pwd")
        if st.button("Einloggen", key="btn_login"):
            if user_pwd == st.secrets["APP_PASSWORD"]:
                st.session_state.auth_ok = True
                st.rerun()
            else:
                st.error("Passwort falsch")
    else:
        st.success("Eingeloggt ✅")
        # Menü erst NACH Login anzeigen
        target_idx = st.selectbox("Index wählen", list(TICKER_LISTS.keys()), key="sel_idx")
        target_iv = st.select_slider("Intervall", options=["15m", "30m", "1h"], value="1h", key="sl_iv")
        if st.button("Logout", key="btn_logout"):
            st.session_state.auth_ok = False
            st.rerun()

# Hauptfenster
if st.session_state.auth_ok:
    st.header(f"Markt-Scanner: {target_idx}")
    if st.button(f"Scan für {target_idx} starten", key="btn_scan"):
        df = run_asperg_scan(target_idx, target_iv)
        if df is not None:
            # Balkendiagramm zur Visualisierung der Volumen-Ausreißer
            fig = px.bar(df, x='Ticker', y='Vol-Faktor', color='Perf %',
                         color_continuous_scale='RdYlGn', 
                         title=f"Volumen-Faktoren {target_idx} ({target_iv})")
            st.plotly_chart(fig, use_container_width=True)
            
            st.table(df.sort_values("Vol-Faktor", ascending=False))
        else:
            st.warning("Keine Daten gefunden.")
else:
    st.info("Bitte logge dich in der Sidebar ein.")
