import yfinance as yf
import pandas as pd
import streamlit as st
import plotly.express as px

# 1. SERVER-CACHE LEEREN (Verhindert Geister-Elemente)
st.cache_data.clear()

# --- KONFIGURATION ---
INDIZES = {
    "DAX": ["ADS.DE", "AIR.DE", "ALV.DE", "BAS.DE", "BAYN.DE", "BMW.DE", "CBK.DE", "DBK.DE", "DTE.DE", "EON.DE", "IFX.DE", "MBG.DE", "MUV2.DE", "RWE.DE", "SAP.DE", "SIE.DE", "VOW3.DE"],
    "MDAX": ["HNR1.DE", "LHA.DE", "LEG.DE", "KGX.DE", "TALK.DE", "EVK.DE", "FRA.DE", "BOSS.DE", "PUM.DE", "WAF.DE"]
}

# --- AUTH LOGIK ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def check_login():
    if st.session_state.authenticated:
        return True
    
    # Diese Spalte erscheint NUR, wenn man nicht eingeloggt ist
    st.sidebar.title("🔐 Projekt Asperg Login")
    pwd = st.sidebar.text_input("Passwort", type="password", key="unique_pwd_key")
    if st.sidebar.button("Anmelden", key="unique_login_button"):
        if pwd == st.secrets["APP_PASSWORD"]:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.sidebar.error("Falsches Passwort")
    return False

# --- APP START ---
st.set_page_config(page_title="Asperg Scanner", layout="wide")

if check_login():
    # ALLES HIER DRIN erscheint erst nach dem Login
    with st.sidebar:
        st.title("⚙️ Einstellungen")
        wahl = st.selectbox("Index", list(INDIZES.keys()))
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.rerun()

    st.header(f"Markt-Analyse: {wahl}")
    
    if st.button("🚀 Scan jetzt starten"):
        with st.spinner("Lade Daten..."):
            # Scanner Logik
            found = []
            for t in INDIZES[wahl]:
                try:
                    s = yf.Ticker(t)
                    h = s.history(period="1d", interval="1h")
                    if not h.empty:
                        vol_factor = round(h['Volume'].iloc[-1] / h['Volume'].mean(), 2)
                        found.append({"Aktie": t, "Vol-Faktor": vol_factor, "Preis": h['Close'].iloc[-1]})
                except: continue
            
            if found:
                df = pd.DataFrame(found)
                fig = px.bar(df, x="Aktie", y="Vol-Faktor", title="Volumen-Check")
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(df)
else:
    # Das hier sieht man, wenn man NICHT eingeloggt ist
    st.warning("Bitte logge dich in der Sidebar ein.")
    st.stop() # STOPPT den Rest des Codes sofort!
