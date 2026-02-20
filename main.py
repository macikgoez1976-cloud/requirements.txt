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
                vol_factor = round(current_vol / avg_vol, 2) if avg_vol > 0 else 0
                
                # Performance der Kerze
                perf = round(((hist['Close'].iloc[-1] - hist['Open'].iloc[-1]) / hist['Open'].iloc[-1]) * 100, 2)
                
                if vol_factor >= 0.1: # Sehr niedrige Schwelle für den Test
                    hits.append({
                        "Ticker": ticker.replace(".DE", ""),
                        "Vol-Faktor": vol_factor,
                        "Perf %": perf,
                        "Preis": round(hist['Close'].iloc[-1], 2)
                    })
            progress_bar.progress((i + 1) / len(selected))
        except: continue
    return pd.DataFrame(hits) if hits else None

# --- UI STRUKTUR ---
st.set_page_config(page_title="Projekt Asperg", layout="wide")

if "auth_ok" not in st.session_state:
    st.session_state.auth_ok = False

# Sidebar
with st.sidebar:
    st.title("🛡️ Projekt Asperg")
    if not st.session_state.auth_ok:
        # Eindeutige Keys verhindern DuplicateElementID
        user_pwd = st.text_input("Passwort", type="password", key="login_pwd_input")
        if st.button("Einloggen", key="login_btn"):
            if user_pwd == st.secrets["APP_PASSWORD"]:
                st.session_state.auth_ok = True
                st.rerun()
            else:
                st.error("Passwort falsch")
    else:
        st.success("Eingeloggt ✅")
        target_idx = st.selectbox("Index wählen", list(TICKER_LISTS.keys()), key="idx_sel")
        target_iv = st.select_slider("Intervall", options=["15m", "30m", "1h"], value="1h", key="iv_slider")
        if st.button("Logout", key="logout_btn"):
            st.session_state.auth_ok = False
            st.rerun()

# Hauptfenster
if st.session_state.auth_ok:
    st.header(f"Markt-Scanner: {target_idx}")
    # Eindeutiger Key für den Scan-Button
    if st.button(f"Scan für {target_idx} jetzt starten", key="run_scan_btn"):
        with st.spinner("Analysiere Marktdaten..."):
            df = run_asperg_scan(target_idx, target_iv)
            
            if df is not None:
                # Das gewünschte Balkendiagramm
                fig = px.bar(df, x='Ticker', y='Vol-Faktor', color='Perf %',
                             title=f"Volumen-Ausreißer im {target_idx}",
                             color_continuous_scale='RdYlGn',
                             text_auto='.2f')
                st.plotly_chart(fig, use_container_width=True)
                
                # Die Detail-Tabelle
                st.subheader("Detail-Daten")
                st.dataframe(df.sort_values("Vol-Faktor", ascending=False), use_container_width=True)
            else:
                st.warning("Keine Werte mit erhöhtem Volumen gefunden.")
else:
    st.info("Bitte logge dich in der Sidebar ein, um den Scanner zu starten.")
