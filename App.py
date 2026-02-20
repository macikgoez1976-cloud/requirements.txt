import yfinance as yf
import pandas as pd
import streamlit as st
import plotly.express as px
import time

# 1. AUTH-CHECK (Muss ganz oben stehen)
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# 2. SEITEN-KONFIGURATION
st.set_page_config(page_title="Projekt Asperg", layout="wide")

# --- LOGIN BEREICH ---
if not st.session_state.authenticated:
    st.sidebar.title("🔐 Login")
    pwd = st.sidebar.text_input("Passwort", type="password")
    if st.sidebar.button("Anmelden"):
        if pwd == st.secrets["APP_PASSWORD"]:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.sidebar.error("Passwort falsch")
    
    st.title("Willkommen bei Projekt Asperg")
    st.info("Bitte loggen Sie sich in der Sidebar ein, um den Markt-Scanner zu starten.")
    st.stop() # STOPPT den Code hier, solange man nicht eingeloggt ist

# --- AB HIER: NUR FÜR EINGELOGGTE NUTZER ---

# 3. MÄRKTE & LOGIK
INDIZES = {
    "DAX": ["ADS.DE", "AIR.DE", "ALV.DE", "BAS.DE", "BAYN.DE", "BMW.DE", "CBK.DE", "DBK.DE", "DTE.DE", "EON.DE", "IFX.DE", "MBG.DE", "MUV2.DE", "RWE.DE", "SAP.DE", "SIE.DE", "VOW3.DE"],
    "MDAX": ["HNR1.DE", "LHA.DE", "LEG.DE", "KGX.DE", "TALK.DE", "EVK.DE", "FRA.DE", "BOSS.DE", "PUM.DE", "WAF.DE"],
    "Dow Jones": ["AAPL", "MSFT", "GS", "JPM", "V", "AXP", "BA", "CAT", "DIS", "KO"]
}

with st.sidebar:
    st.title("🛡️ Einstellungen")
    target_idx = st.selectbox("Index wählen", list(INDIZES.keys()))
    target_iv = st.select_slider("Intervall", options=["15m", "30m", "1h"], value="1h")
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()

st.title(f"🚀 Markt-Analyse: {target_idx}")

if st.button(f"Scan für {target_idx} starten"):
    hits = []
    progress_bar = st.progress(0)
    
    tickers = INDIZES[target_idx]
    for i, t in enumerate(tickers):
        try:
            stock = yf.Ticker(t)
            # 5 Tage Historie für stabilen Durchschnitt
            hist = stock.history(period="5d", interval=target_iv)
            
            if not hist.empty and len(hist) >= 2:
                v_now = hist['Volume'].iloc[-1]
                v_avg = hist['Volume'].tail(15).mean()
                ratio = round(v_now / v_avg, 2)
                
                # Performance (Open zu Close der aktuellen Kerze)
                perf = round(((hist['Close'].iloc[-1] - hist['Open'].iloc[-1]) / hist['Open'].iloc[-1]) * 100, 2)
                
                hits.append({
                    "Aktie": t.replace(".DE", ""),
                    "Vol-Faktor": ratio,
                    "Perf %": perf,
                    "Preis": round(hist['Close'].iloc[-1], 2)
                })
            progress_bar.progress((i + 1) / len(tickers))
        except: continue

    if hits:
        df = pd.DataFrame(hits)
        
        # VISUALISIERUNG
        st.subheader("Volumen-Ausreißer & Kursrichtung")
        fig = px.bar(df, x='Aktie', y='Vol-Faktor', color='Perf %',
                     color_continuous_scale='RdYlGn', 
                     range_color=[-1.5, 1.5], # Rot bei -1.5%, Grün bei +1.5%
                     text='Perf %',
                     title="Relative Volumen-Stärke")
        
        fig.update_traces(texttemplate='%{text}%', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
        
        # DATEN-TABELLE
        st.subheader("Detail-Liste")
        st.dataframe(df.sort_values("Vol-Faktor", ascending=False), use_container_width=True)
    else:
        st.warning("Keine Daten gefunden.")
