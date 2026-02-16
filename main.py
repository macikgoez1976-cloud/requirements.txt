import yfinance as yf
from pytickersymbols import PyTickerSymbols
import pandas as pd

def run_asperg_scan(index_name):
    stock_data = PyTickerSymbols()
    
    # Der Index kommt direkt aus der Auswahl der app.py
    indices = [index_name]
    hits = []

    for index in indices:
        stocks = stock_data.get_stocks_by_index(index)
        
        for s in stocks:
            try:
                # Wir nehmen das Yahoo-Symbol (meistens das erste in der Liste)
                ticker_symbol = s['symbols'][0]['yahoo']
                name = s['name']
                
                stock = yf.Ticker(ticker_symbol)
                hist = stock.history(period="10d")
                
                if len(hist) < 2:
                    continue
                
                current_vol = hist['Volume'].iloc[-1]
                avg_vol = hist['Volume'].iloc[:-1].mean()
                vol_factor = round(current_vol / avg_vol, 2) if avg_vol > 0 else 0
                
                # Filter: Volumen muss mindestens 1.5x höher als der Schnitt sein
                if vol_factor >= 1.5:
                    hits.append({
                        "Ampel": "🟢",
                        "Aktie": name,
                        "Symbol": ticker_symbol,
                        "Vol-Faktor": f"{vol_factor}x"
                    })
            except:
                continue
                
    return hits
