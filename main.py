import yfinance as yf
import pandas as pd
import streamlit as st
import plotly.express as px
import time

# --- MÄRKTE ---
INDIZES = {
    "DAX": ["ADS.DE", "AIR.DE", "ALV.DE", "BAS.DE", "BAYN.DE", "BMW.DE", "CBK.DE", "DBK.DE", "DTE.DE", "EON.DE", "IFX.DE", "MBG.DE", "MUV2.DE", "RWE.DE", "SAP.DE", "SIE.DE", "VOW3.DE"],
    "MDAX": ["HNR1.DE", "LHA.DE", "LEG.DE", "KGX.DE", "TALK.DE", "EVK.DE", "FRA.DE", "BOSS.DE", "PUM.DE", "WAF.DE"],
    "Dow Jones": ["AAPL", "MSFT", "GS", "JPM", "V", "AXP", "BA", "CAT", "DIS", "KO"]
}

def scan_logic(idx, interval):
    tickers = INDIZES.get(idx)
    data_list = []
    progress = st.progress(0)
    
    for i, t in enumerate(tickers):
        try:
            stock = yf.Ticker(t)
            hist = stock.history(period="5d", interval=interval)
            if not hist.empty and len(hist) >= 2:
                v_now = hist['Volume'].iloc[-1]
                v_avg = hist['Volume'].tail(10).mean()
                ratio = round(v_now / v_avg, 2) if v_avg > 0 else 0
                perf = round(((hist['Close'].iloc[-1] - hist['Open'].iloc[-1]) / hist['Open'].iloc[-1]) * 100, 2)
                
                data_list.append({
                    "Aktie": t.replace(".DE", ""),
                    "Vol-Faktor": ratio,
                    "Performance %": perf,
                    "Preis": round(hist['Close'].iloc[-1], 2)
                })
            progress.progress((i + 1) / len(tickers))
        except: continue
    return pd.DataFrame(data_list) if data_list else None

# --- UI START ---
st.set_page_config(page_title="Projekt Asperg", layout="wide")

# Session State Check
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# SIDEBAR: Hier wird strikt unterschieden
with st.sidebar:
    st.title("🛡️ Projekt Asperg")
    
    if not st.session_state.logged_in:
        # NUR wenn nicht eingeloggt
        pwd = st.text_input("Master-Passwort", type="password", key="pwd_field")
        if st.button("Anmelden", key="login_final"):
            if pwd == st.secrets["APP_PASSWORD"]:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Falsch!")
    else:
        # NUR wenn eingeloggt
        st.success("Login aktiv")
        markt_wahl = st.selectbox("Index wählen", list(INDIZES.keys()), key="m_select")
        zeit_wahl = st.select_slider("Intervall", options=["15m", "30m", "1h"], value="1h", key="z_select")
        if st.button("Abmelden", key="logout_final"):
            st.session_state.logged_in = False
            st.rerun()

# HAUPTSEITE
if st.session_state.logged_in:
    st.header(f"Analyse: {markt_wahl}")
    if st.button(f"Scan starten", key="run_main"):
        ergebnisse = scan_logic(markt_wahl, zeit_wahl)
        if ergebnisse is not None:
            # Diagramm
            fig = px.bar(ergebnisse, x='Aktie', y='Vol-Faktor', color='Performance %',
                         color_continuous_scale='RdYlGn', range_color=[-1, 1],
                         title="Volumen vs. Performance")
            st.plotly_chart(fig, use_container_width=True)
            # Tabelle
            st.dataframe(ergebnisse.sort_values("Vol-Faktor", ascending=False), use_container_width=True)
else:
    st.info("Bitte nutzen Sie das Login-Feld in der Seitenleiste.")
