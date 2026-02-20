import yfinance as yf
import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime
import time

# --- SETUP MÄRKTE ---
TICKER_LISTS = {
    "DAX": ["ADS.DE", "AIR.DE", "ALV.DE", "BAS.DE", "BAYN.DE", "BMW.DE", "CBK.DE", "DBK.DE", "DTE.DE", "EON.DE", "IFX.DE", "MBG.DE", "MUV2.DE", "RWE.DE", "SAP.DE", "SIE.DE", "VOW3.DE"],
    "MDAX": ["HNR1.DE", "LHA.DE", "LEG.DE", "KGX.DE", "TALK.DE", "EVK.DE", "FRA.DE", "BOSS.DE", "PUM.DE", "WAF.DE"],
    "Dow Jones": ["AAPL", "MSFT", "GS", "JPM", "V", "AXP", "BA", "CAT", "DIS", "KO", "NKE", "TRV", "UNH", "VZ"],
    "S&P 500": ["NVDA", "TSLA", "AMZN", "GOOGL", "META", "AMD", "NFLX", "AAPL", "MSFT"]
}

def run_asperg_scan(index_name, interval):
    selected = TICKER_LISTS.get(index_name)
    hits = []
    progress_bar = st.progress(0)
    
    for i, ticker in enumerate(selected):
        try:
            stock = yf.Ticker(ticker)
            # Wir nehmen 5 Tage für einen stabilen Durchschnitt
            hist = stock.history(period="5d", interval=interval)
            
            if not hist.empty and len(hist) >= 3:
                current_vol = hist['Volume'].iloc[-1]
                avg_vol = hist['Volume'].tail(15).mean() # Vergleich mit den letzten 15 Intervallen
                vol_factor = round(current_vol / avg_vol, 2)
                
                # Kurs-Performance der aktuellen Kerze (Open zu Close)
                perf = round(((hist['Close'].iloc[-1] - hist['Open'].iloc[-1]) / hist['Open'].iloc[-1]) * 100, 2)
                
                # Wir erfassen alles ab 0.2x, um die Dynamik zu sehen
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

# --- UI STRUKTUR ---
st.set_page_config(page_title="Projekt Asperg", layout="wide")

# Initialisiere Auth-Status
if "auth_ok" not in st.session_state:
    st.session_state.auth_ok = False

# SIDEBAR
with st.sidebar:
    st.title("🛡️ Projekt Asperg")
    
    if not st.session_state.auth_ok:
        # NUR PASSWORT ANZEIGEN
        user_pwd = st.text_input("Passwort eingeben", type="password", key="main_pwd")
        if st.button("Einloggen", key="login_trigger"):
            if user_pwd == st.secrets["APP_PASSWORD"]:
                st.session_state.auth_ok = True
                st.rerun()
            else:
                st.error("Passwort inkorrekt")
    else:
        # NUR SCANNER-MENÜ ANZEIGEN
        st.success("Verbindung gesichert ✅")
        target_idx = st.selectbox("Markt wählen", list(TICKER_LISTS.keys()), key="sel_market")
        target_iv = st.select_slider("Intervall", options=["15m", "30m", "1h"], value="1h", key="iv_slider")
        
        st.divider()
        if st.button("Logout", key="logout_trigger"):
            st.session_state.auth_ok = False
            st.rerun()

# HAUPTFENSTER
if st.session_state.auth_ok:
    st.header(f"📊 Live-Analyse: {target_idx} ({target_iv})")
    
    if st.button(f"🔍 {target_idx} jetzt scannen", key="scan_trigger"):
        with st.spinner("Hole Echtzeitdaten..."):
            df = run_asperg_scan(target_idx, target_iv)
            
            if df is not None and not df.empty:
                # 1. Visualisierung: Volumen-Balkendiagramm
                # Farbskala von Rot (negativ) über Gelb (neutral) zu Grün (positiv)
                fig = px.bar(df, x='Ticker', y='Vol-Faktor', color='Perf %',
                             title=f"Relative Volumen-Stärke - {target_idx}",
                             color_continuous_scale='RdYlGn',
                             range_color=[-2, 2], # Zentriert die Farben um 0%
                             text='Perf %')
                
                fig.update_traces(texttemplate='%{text}%', textposition='outside')
                st.plotly_chart(fig, use_container_width=True)
                
                # 2. Detail-Tabelle
                st.subheader("Markt-Details")
                # Styling für die Tabelle: Höchster Vol-Faktor zuerst
                st.dataframe(df.sort_values("Vol-Faktor", ascending=False), use_container_width=True)
            else:
                st.warning("Keine Daten verfügbar. Prüfe die Marktöffnungszeiten.")
else:
    st.info("Willkommen bei Projekt Asperg. Bitte loggen Sie sich in der Sidebar ein, um fortzufahren.")
