import yfinance as yf
import pandas as pd
from datetime import datetime
import requests
import streamlit as st
import time

def run_asperg_scan(index_name):
    # Erweiterte Listen inkl. US-Märkte
    tickers = {
        "DAX": ["ADS.DE", "AIR.DE", "ALV.DE", "BAS.DE", "BAYN.DE", "BMW.DE", "CBK.DE", "DBK.DE", "DHL.DE", "DTE.DE", "EON.DE", "IFX.DE", "MBG.DE", "MUV2.DE", "RWE.DE", "SAP.DE", "SIE.DE", "VOW3.DE"],
        "MDAX": ["HNR1.DE", "LHA.DE", "LEG.DE", "KGX.DE", "TALK.DE", "EVK.DE", "FRA.DE", "BOSS.DE", "PUM.DE"],
        "SDAX": ["SDF.DE", "BC8.DE", "PNE3.DE", "WAF.DE", "HDD.DE", "G1A.DE", "WCH.DE", "AM3D.DE"],
        "Dow Jones": ["AAPL", "MSFT", "GS", "JPM", "V", "AXP", "BA", "CAT", "DIS", "KO"],
        "S&P 500 (Top)": ["NVDA", "TSLA", "AMZN", "GOOGL", "META", "AMD", "NFLX"]
    }
    
    selected_tickers = tickers.get(index_name, tickers["DAX"])
    hits = []
    
    progress_bar = st.progress(0)
    for i, ticker in enumerate(selected_tickers):
        try:
            stock = yf.Ticker(ticker)
            # Wir holen jetzt 1h Daten für mehr Feingefühl
            hist = stock.history(period="3d", interval="1h")
            
            if not hist.empty and len(hist) >= 5:
                current_vol = hist['Volume'].iloc[-1]
                # Durchschnitt der letzten 10 Handelsstunden
                avg_vol = hist['Volume'].tail(10).mean()
                
                if avg_vol > 0:
                    vol_factor = round(current_vol / avg_vol, 2)
                    
                    # SENSIBLERER FILTER: Zeige alles ab 0.3x für aktives Monitoring
                    if vol_factor >= 0.3:
                        zeit = datetime.now().strftime("%H:%M")
                        # Korrekte Chart-Links für DE und US
                        suffix = "" if ".DE" in ticker else ""
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
                            "Letzter Preis": f"{round(hist['Close'].iloc[-1], 2)} €" if ".DE" in ticker else f"{round(hist['Close'].iloc[-1], 2)} $"
                        })
            
            time.sleep(0.05) # Schnellere Verarbeitung
            progress_bar.progress((i + 1) / len(selected_tickers))
        except:
            continue
            
    if hits:
        hits = sorted(hits, key=lambda x: x['Vol-Faktor'], reverse=True)
        for h in hits:
            h['Vol-Faktor'] = f"{h['Vol-Faktor']}x"
                
    return hits
