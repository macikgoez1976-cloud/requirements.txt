import yfinance as yf
import pandas as pd
import streamlit as st
import plotly.express as px

# 1. AUTH-CHECK
if "auth_ok" not in st.session_state:
    st.session_state.auth_ok = False

st.set_page_config(page_title="Projekt Asperg", layout="wide")

if not st.session_state.auth_ok:
    st.sidebar.title("🔐 Login")
    pwd_input = st.sidebar.text_input("Passwort", type="password", key="login_field")
    if st.sidebar.button("Anmelden", key="login_btn"):
        if pwd_input == st.secrets["APP_PASSWORD"]:
            st.session_state.auth_ok = True
            st.rerun()
        else:
            st.sidebar.error("Passwort falsch")
    st.info("Bitte loggen Sie sich über die Sidebar ein.")
    st.stop()

# --- AB HIER NUR EINGELOGGT ---
TICKERS = {
    "DAX": ["ADS.DE", "AIR.DE", "ALV.DE", "BAS.DE", "BAYN.DE", "BMW.DE", "CBK.DE", "DBK.DE", "DHL.DE", "DTE.DE", "EON.DE", "IFX.DE", "MBG.DE", "MUV2.DE", "RWE.DE", "SAP.DE", "SIE.DE", "VOW3.DE"],
    "MDAX": ["HNR1.DE", "LHA.DE", "LEG.DE", "KGX.DE", "TALK.DE", "EVK.DE", "FRA.DE", "BOSS.DE", "PUM.DE", "WAF.DE"],
    "Dow Jones": ["AAPL", "MSFT", "GS", "JPM", "V", "AXP", "BA", "CAT", "DIS", "KO"],
    "S&P 500": ["NVDA", "TSLA", "AMZN", "GOOGL", "META", "AMD", "NFLX"]
}

with st.sidebar:
    st.title("⚙️ Scanner Setup")
    target_idx = st.selectbox("Index wählen", list(TICKERS.keys()))
    target_iv = st.select_slider("Intervall", options=["15m", "30m", "1h"], value="1h")
    if st.button("Logout"):
        st.session_state.auth_ok = False
        st.rerun()

st.title(f"🚀 Markt-Analyse: {target_idx}")

if st.button(f"Scan starten"):
    hits = []
    progress_bar = st.progress(0)
    selected_list = TICKERS[target_idx]
    
    for i, t in enumerate(selected_list):
        try:
            stock = yf.Ticker(t)
            hist = stock.history(period="5d", interval=target_iv)
            if not hist.empty and len(hist) >= 2:
                vol_ratio = round(hist['Volume'].iloc[-1] / hist['Volume'].tail(15).mean(), 2)
                perf = round(((hist['Close'].iloc[-1] - hist['Open'].iloc[-1]) / hist['Open'].iloc[-1]) * 100, 2)
                hits.append({"Aktie": t.replace(".DE", ""), "Vol-Faktor": vol_ratio, "Perf %": perf, "Preis": round(hist['Close'].iloc[-1], 2)})
            progress_bar.progress((i + 1) / len(selected_list))
        except: continue

    if hits:
        df = pd.DataFrame(hits)
        st.subheader("Volumen-Ausreißer")
        fig = px.bar(df, x='Aktie', y='Vol-Faktor', color='Perf %',
                     color_continuous_scale='RdYlGn', range_color=[-1.5, 1.5],
                     text='Perf %', title="Relativer Volumen-Faktor")
        st.plotly_chart(fig, use_container_width=True)
        st.table(df.sort_values("Vol-Faktor", ascending=False))
    else:
        st.warning("Keine Daten gefunden.")
