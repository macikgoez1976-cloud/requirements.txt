import yfinance as yf
import pandas as pd
from datetime import datetime
import streamlit as st
import time
import plotly.express as px

# --- KONFIGURATION ---
TICKER_LISTS = {
    "DAX": ["ADS.DE", "AIR.DE", "ALV.DE", "BAS.DE", "BAYN.DE", "BMW.DE", "CBK.DE", "DB1.DE", "DBK.DE", "DHL.DE", "DTE.DE", "DTG.DE", "EON.DE", "FRE.DE", "HEI.DE", "HEN3.DE", "IFX.DE", "MBG.DE", "MRK.DE", "MUV2.DE", "P911.DE", "RWE.DE", "SAP.DE", "SIE.DE", "SY1.DE", "VOW3.DE", "ZAL.DE"],
    "MDAX": ["HNR1.DE", "LHA.DE", "LEG.DE", "KGX.DE", "TALK.DE", "EVK.DE", "FRA.DE", "BOSS.DE", "PUM.DE", "WAF.DE"],
    "SDAX": ["SDF.DE", "BC8.DE", "PNE3.DE", "HDD.DE", "G1A.DE", "WCH.DE"],
    "Dow Jones": ["AAPL", "MSFT", "GS", "JPM", "V", "AXP", "BA", "CAT", "DIS", "KO"],
    "S&P 500 (Top)": ["NVDA", "TSLA", "AMZN", "GOOGL", "META", "AMD", "NFLX"]
}

def run_asperg_scan(index_name, interval):
    selected_tickers = TICKER_LISTS.get(index_name, TICKER_LISTS["DAX"])
    hits = []
    
    # Sicherstellen, dass genug Daten für den Durchschnitt da sind
    period = "5d" if interval == "1h" else "2d"
    
    progress_bar = st.progress(0)
    for i, ticker in enumerate(selected_tickers):
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period, interval=interval)
            
            if not hist.empty and len(hist) >= 3:
                # Volumen & Performance Logik
                current_vol = hist['Volume'].iloc[-1]
                avg_vol = hist['Volume'].tail(10).mean()
                
                close_p = hist['Close'].iloc[-1]
                open_p = hist['Open'].iloc[-1]
                perf = round(((close_p - open_p) / open_p) * 100, 2)
                
                if avg_vol > 0:
                    vol_factor = round(current_vol / avg_vol, 2)
                    
                    if vol_factor >= 0.3:
                        # Branchen-Info abrufen
                        sector = stock.info.get('sector', 'Unbekannt')
                        
                        hits.append({
                            "Ticker": ticker.replace(".DE", ""),
                            "Uhrzeit": datetime.now().strftime("%H:%M"),
                            "Status": "🚀" if vol_factor > 1.5 and perf > 0 else "🟢" if perf > 0 else "🔴",
                            "Sektor": sector,
                            "Vol-Faktor": vol_factor,
                            "Perf %": perf,
                            "Preis": round(close_p, 2)
                        })
            
            time.sleep(0.05)
            progress_bar.progress((i + 1) / len(selected_tickers))
        except:
            continue
            
    return pd.DataFrame(hits) if hits else None

# --- STREAMLIT UI SETUP ---
st.set_page_config(page_title="Projekt Asperg", layout="wide")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# SIDEBAR LOGIN & SETUP
with st.sidebar:
    st.title("🔐 Projekt Asperg")
    
    if not st.session_state.logged_in:
        pwd = st.text_input("Passwort", type="password")
        if st.button("Einloggen"):
            if pwd == st.secrets["APP_PASSWORD"]:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Falsches Passwort")
    else:
        st.success("Eingeloggt")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()
        
        st.divider()
        st.header("⚙️ Scanner-Setup")
        idx = st.selectbox("Markt", list(TICKER_LISTS.keys()))
        iv = st.select_slider("Intervall", options=["15m", "30m", "1h"], value="1h")
        do_scan = st.button("Scan starten")

# HAUPTBEREICH
if st.session_state.logged_in:
    st.title(f"📊 Analyse: {idx} ({iv})")
    
    if 'do_scan' in locals() and do_scan:
        df = run_asperg_scan(idx, iv)
        
        if df is not None:
            # 1. Metriken anzeigen
            c1, c2, c3 = st.columns(3)
            top_stock = df.iloc[0]
            c1.metric("Top Vol-Ausreißer", top_stock['Ticker'], f"{top_stock['Vol-Faktor']}x")
            c2.metric("Beste Performance", f"{df.sort_values('Perf %').iloc[-1]['Ticker']}", f"{df.sort_values('Perf %').iloc[-1]['Perf %']}%")
            c3.metric("Gescannte Aktien", len(df))

            # 2. Balkendiagramm (Visualisierung)
            st.subheader("Volumen-Faktoren im Vergleich")
            fig = px.bar(df, x='Ticker', y='Vol-Faktor', color='Perf %', 
                         title="Volumen-Spikes nach Aktie",
                         color_continuous_scale='RdYlGn')
            st.plotly_chart(fig, use_container_width=True)
            
            # 3. Tabelle
            st.subheader("Detail-Daten")
            st.dataframe(df.sort_values('Vol-Faktor', ascending=False), use_container_width=True)
        else:
            st.warning("Keine Treffer mit aktuellem Filter.")
else:
    st.info("Bitte loggen Sie sich über die Sidebar ein.")
