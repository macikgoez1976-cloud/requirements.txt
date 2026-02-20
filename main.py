import yfinance as yf
import pandas as pd
from datetime import datetime
import requests
import streamlit as st
import time

# --- KONFIGURATION & SYMBOLE ---
TICKER_LISTS = {
    "DAX": ["ADS.DE", "AIR.DE", "ALV.DE", "BAS.DE", "BAYN.DE", "BMW.DE", "CBK.DE", "DBK.DE", "DHL.DE", "DTE.DE", "EON.DE", "IFX.DE", "MBG.DE", "MUV2.DE", "RWE.DE", "SAP.DE", "SIE.DE", "VOW3.DE"],
    "MDAX": ["HNR1.DE", "LHA.DE", "LEG.DE", "KGX.DE", "TALK.DE", "EVK.DE", "FRA.DE", "BOSS.DE", "PUM.DE"],
    "SDAX": ["SDF.DE", "BC8.DE", "PNE3.DE", "WAF.DE", "HDD.DE", "G1A.DE", "WCH.DE"],
    "Dow Jones": ["AAPL", "MSFT", "GS", "JPM", "V", "AXP", "BA", "CAT", "DIS", "KO", "IBM", "INTC", "MMM", "WMT"],
    "S&P 500 (Top)": ["NVDA", "TSLA", "AMZN", "GOOGL", "META", "AMD", "NFLX", "MSFT", "AAPL"]
}

def run_asperg_scan(index_name, interval):
    selected_tickers = TICKER_LISTS.get(index_name, TICKER_LISTS["DAX"])
    hits = []
    
    # Mapping für die Berechnung des Durchschnitts
    # Bei 15m schauen wir die letzten 20 Kerzen an (ca. 5 Stunden)
    # Bei 1h schauen wir die letzten 10 Kerzen an (ca. 1,5 Handelstage)
    period = "2d" if interval == "15m" else "5d"
    
    progress_bar = st.progress(0)
    for i, ticker in enumerate(selected_tickers):
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period, interval=interval)
            
            if not hist.empty and len(hist) >= 5:
                current_vol = hist['Volume'].iloc[-1]
                avg_vol = hist['Volume'].tail(15).mean()
                
                if avg_vol > 0:
                    vol_factor = round(current_vol / avg_vol, 2)
                    
                    # Für Daytrader: Alles ab 0.3x anzeigen, um Trends früh zu sehen
                    if vol_factor >= 0.3:
                        zeit = datetime.now().strftime("%H:%M")
                        chart_url = f"https://de.finance.yahoo.com/quote/{ticker}"
                        
                        # Status-Ampel
                        if vol_factor >= 2.0: status = "🔥"
                        elif vol_factor >= 1.0: status = "🟢"
                        else: status = "⚪"
                        
                        hits.append({
                            "Uhrzeit": zeit,
                            "Status": status,
                            "Aktie": f"[{ticker.replace('.DE', '')}]({chart_url})",
                            "Vol-Faktor": vol_factor,
                            "Preis": f"{round(hist['Close'].iloc[-1], 2)} {'€' if '.DE' in ticker else '$'}"
                        })
            
            time.sleep(0.05)
            progress_bar.progress((i + 1) / len(selected_tickers))
        except:
            continue
            
    if hits:
        hits = sorted(hits, key=lambda x: x['Vol-Faktor'], reverse=True)
        for h in hits:
            h['Vol-Faktor'] = f"{h['Vol-Faktor']}x"
                
    return hits

# --- STREAMLIT UI ---
st.set_page_config(page_title="Projekt Asperg", page_icon="🚀")
st.title("🚀 Projekt Asperg: Markt-Scanner")

# Sidebar für Einstellungen
with st.sidebar:
    st.header("⚙️ Einstellungen")
    
    # 1. Markt Auswahl (Jetzt mit US Märkten)
    index_choice = st.selectbox("Welchen Markt prüfen?", list(TICKER_LISTS.keys()))
    
    # 2. Intervall Auswahl (Neu!)
    interval_choice = st.select_slider(
        "Zeit-Intervall (Sensibilität)",
        options=["15m", "30m", "1h"],
        value="1h",
        help="15m ist für schnelles Daytrading, 1h für Trends."
    )
    
    start_scan = st.button(f"Scan für {index_choice} starten")

if start_scan:
    results = run_asperg_scan(index_choice, interval_choice)
    
    if results:
        st.success(f"Gefundene Volumen-Ausreißer im {index_choice} ({interval_choice}):")
        st.table(pd.DataFrame(results))
    else:
        st.info(f"Keine auffälligen Bewegungen im {index_choice} bei {interval_choice} gefunden.")
