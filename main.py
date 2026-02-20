import yfinance as yf
import pandas as pd
from datetime import datetime
import streamlit as st
import time

# --- KONFIGURATION & SYMBOLE ---
TICKER_LISTS = {
    "DAX": ["ADS.DE", "AIR.DE", "ALV.DE", "BAS.DE", "BAYN.DE", "BMW.DE", "CBK.DE", "DBK.DE", "DHL.DE", "DTE.DE", "EON.DE", "IFX.DE", "MBG.DE", "MUV2.DE", "RWE.DE", "SAP.DE", "SIE.DE", "VOW3.DE"],
    "MDAX": ["HNR1.DE", "LHA.DE", "LEG.DE", "KGX.DE", "TALK.DE", "EVK.DE", "FRA.DE", "BOSS.DE", "PUM.DE"],
    "SDAX": ["SDF.DE", "BC8.DE", "PNE3.DE", "WAF.DE", "HDD.DE", "G1A.DE", "WCH.DE"],
    "Dow Jones": ["AAPL", "MSFT", "GS", "JPM", "V", "AXP", "BA", "CAT", "DIS", "KO"],
    "S&P 500 (Top)": ["NVDA", "TSLA", "AMZN", "GOOGL", "META", "AMD", "NFLX"]
}

def run_asperg_scan(index_name, interval):
    selected_tickers = TICKER_LISTS.get(index_name, TICKER_LISTS["DAX"])
    hits = []
    
    # Dynamische Periode wählen
    period = "2d" if interval in ["15m", "30m"] else "5d"
    
    progress_bar = st.progress(0)
    for i, ticker in enumerate(selected_tickers):
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period, interval=interval)
            
            if not hist.empty and len(hist) >= 2:
                # Volumen-Analyse
                current_vol = hist['Volume'].iloc[-1]
                avg_vol = hist['Volume'].tail(15).mean()
                
                # Performance-Analyse (Profi-Feature)
                open_price = hist['Open'].iloc[-1]
                close_price = hist['Close'].iloc[-1]
                perf = round(((close_price - open_price) / open_price) * 100, 2)
                
                if avg_vol > 0:
                    vol_factor = round(current_vol / avg_vol, 2)
                    
                    if vol_factor >= 0.3:
                        zeit = datetime.now().strftime("%H:%M")
                        chart_url = f"https://de.finance.yahoo.com/quote/{ticker}"
                        
                        # Sektor & Name (Profi-Feature)
                        info = stock.info
                        sector = info.get('sector', 'N/A')
                        
                        # Status-Ampel (Kombiniert Volumen & Performance)
                        if vol_factor >= 2.0 and perf > 0: status = "🚀"
                        elif vol_factor >= 1.0: status = "🟢"
                        elif perf < -2: status = "⚠️"
                        else: status = "⚪"
                        
                        hits.append({
                            "Uhrzeit": zeit,
                            "Status": status,
                            "Aktie": f"[{ticker.replace('.DE', '')}]({chart_url})",
                            "Sektor": sector,
                            "Vol-Faktor": vol_factor,
                            "Perf %": f"{perf}%",
                            "Preis": f"{round(close_price, 2)} {'€' if '.DE' in ticker else '$'}"
                        })
            
            time.sleep(0.05)
            progress_bar.progress((i + 1) / len(selected_tickers))
        except:
            continue
            
    if hits:
        df = pd.DataFrame(hits).sort_values(by="Vol-Faktor", ascending=False)
        df['Vol-Faktor'] = df['Vol-Faktor'].apply(lambda x: f"{x}x")
        return df
    return None

# --- STREAMLIT UI ---
st.set_page_config(page_title="Projekt Asperg", page_icon="🚀", layout="wide")
st.title("🚀 Projekt Asperg: Markt-Scanner")

# Login-Logik
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

with st.sidebar:
    st.header("🔐 Bereich")
    if not st.session_state.logged_in:
        password = st.text_input("Passwort eingeben", type="password")
        if st.button("Einloggen"):
            if password == st.secrets["APP_PASSWORD"]: # Passwort in Secrets hinterlegen!
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Falsches Passwort")
    else:
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()
        
        st.divider()
        st.header("⚙️ Scanner-Setup")
        index_choice = st.selectbox("Markt wählen", list(TICKER_LISTS.keys()))
        interval_choice = st.select_slider("Intervall (Sensibilität)", options=["15m", "30m", "1h"], value="1h")
        start_scan = st.button("Scan jetzt starten")

# Hauptbereich
if st.session_state.logged_in:
    if 'start_scan' in locals() and start_scan:
        ergebnisse = run_asperg_scan(index_choice, interval_choice)
        if ergebnisse is not None:
            st.success(f"Signale für {index_choice} gefunden!")
            st.table(ergebnisse)
        else:
            st.info("Keine Ausreißer gefunden.")
else:
    st.warning("Bitte logge dich ein, um den Scanner zu nutzen.")
