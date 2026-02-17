import yfinance as yf
import pandas as pd
from datetime import datetime
import streamlit as st

def run_asperg_scan(index_name):
    # Wir testen mit den 5 liquidesten Werten, die IMMER Daten liefern
    test_tickers = ["SAP.DE", "SIE.DE", "ALV.DE", "DTE.DE", "BMW.DE", "AIR.DE", "CBK.DE", "DBK.DE"]
    hits = []

    for ticker in test_tickers:
        try:
            stock = yf.Ticker(ticker)
            # Wir nutzen '1d' Daten (Tagesbasis), um Fehler bei Stunden-Intervallen auszuschließen
            hist = stock.history(period="2d")
            
            if hist.empty or len(hist) < 2:
                continue
            
            # Vergleich Heute vs. Gestern
            current_vol = hist['Volume'].iloc[-1]
            prev_vol = hist['Volume'].iloc[-2]
            
            if prev_vol == 0: continue
            vol_factor = round(current_vol / prev_vol, 2)
            
            # EXTREM NIEDRIGE SCHWELLE zum Testen
            if vol_factor >= 0.1:
                zeit = datetime.now().strftime("%H:%M")
                chart_url = f"https://de.finance.yahoo.com/quote/{ticker}"
                
                hits.append({
                    "Uhrzeit": zeit,
                    "Status": "✅" if vol_factor > 1.0 else "⚪",
                    "Aktie": f"[{ticker}]({chart_url})",
                    "Vol-Faktor": f"{vol_factor}x",
                    "Top-News": "Test-Modus aktiv"
                })
        except Exception as e:
            continue
                
    return hits
