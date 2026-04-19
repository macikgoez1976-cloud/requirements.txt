import yfinance as yf
import pandas as pd
import streamlit as st
import plotly.express as px

def safe_rerun():
    if hasattr(st, "rerun"):
        st.rerun()
    else:
        st.experimental_rerun()

if "auth_ok" not in st.session_state:
    st.session_state.auth_ok = False

st.set_page_config(page_title="Projekt Asperg", layout="wide")

if not st.session_state.auth_ok:
    st.sidebar.title("🔐 Login")
    pwd_input = st.sidebar.text_input("Passwort", type="password", key="login_field")
    if st.sidebar.button("Anmelden", key="login_btn"):
        if "APP_PASSWORD" in st.secrets and pwd_input == st.secrets["APP_PASSWORD"]:
            st.session_state.auth_ok = True
            safe_rerun()
        else:
            st.sidebar.error("Passwort falsch")
    st.stop()

# --- DATEN-DEFINITION ---
TICKERS = {
    "DAX": ["ADS.DE", "AIR.DE", "ALV.DE", "BAS.DE", "BAYN.DE", "BMW.DE", "CBK.DE", "DBK.DE", "DHL.DE", "DTE.DE", "EON.DE", "IFX.DE", "MBG.DE", "MUV2.DE", "RWE.DE", "SAP.DE", "SIE.DE", "VOW3.DE", "SY1.DE", "BEI.DE"],
    "MDAX": ["HNR1.DE", "LHA.DE", "LEG.DE", "KGX.DE", "TALK.DE", "EVK.DE", "FRA.DE", "BOSS.DE", "PUM.DE", "WAF.DE"],
    "Dow Jones": ["AAPL", "MSFT", "GS", "JPM", "V", "AXP", "BA", "CAT", "DIS", "KO"],
    "S&P 500": ["NVDA", "TSLA", "AMZN", "GOOGL", "META", "AMD", "NFLX"]
}

with st.sidebar:
    st.title("⚙️ Scanner Setup")
    target_idx = st.selectbox("Index wählen", list(TICKERS.keys()))
    target_iv = st.select_slider("Intervall", options=["15m", "30m", "1h"], value="1h")
    vol_threshold = st.number_input("Alarm-Schwellenwert (Volumen)", value=2.0, step=0.1)
    if st.button("Logout"):
        st.session_state.auth_ok = False
        safe_rerun()

st.title(f"🚀 Markt-Analyse: {target_idx}")

if st.button(f"Scan starten"):
    hits = []
    progress_bar = st.progress(0)
    selected_list = TICKERS[target_idx]
    
    for i, t in enumerate(selected_list):
        try:
            stock = yf.Ticker(t)
            hist_daily = stock.history(period="1y") 
            hist_iv = stock.history(period="10d", interval=target_iv)
            
            if not hist_iv.empty and len(hist_daily) >= 200:
                # 1. VOLUMEN & RSI
                vol_ratio = round(hist_iv['Volume'].iloc[-1] / hist_iv['Volume'].tail(15).mean(), 2)
                perf = round(((hist_iv['Close'].iloc[-1] - hist_iv['Open'].iloc[-1]) / hist_iv['Open'].iloc[-1]) * 100, 2)
                
                delta = hist_iv['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rsi = round(100 - (100 / (1 + (gain / loss).iloc[-1])), 1)

                # 2. SMA 200
                sma200 = hist_daily['Close'].rolling(window=200).mean()
                current_price = hist_daily['Close'].iloc[-1]
                prev_price = hist_daily['Close'].iloc[-2]
                current_sma = sma200.iloc[-1]
                prev_sma = sma200.iloc[-2]
                
                sma_status = "Neutral"
                if prev_price < prev_sma and current_price > current_sma:
                    sma_status = "🚀 Breakout (OBEN)"
                elif prev_price > prev_sma and current_price < current_sma:
                    sma_status = "⚠️ Breakdown (UNTEN)"
                elif current_price > current_sma:
                    sma_status = "Trend: Bullisch"
                else:
                    sma_status = "Trend: Bärisch"

                # 3. LINK GENERIERUNG (Finanzen.net)
                clean_name = t.replace(".DE", "")
                link = f"https://www.finanzen.net/suchergebnis.asp?_search={clean_name}"

                hits.append({
                    "Aktie": clean_name,
                    "Link": link,
                    "Vol-Faktor": vol_ratio,
                    "Perf %": perf,
                    "RSI (14)": rsi,
                    "200-Tage-Check": sma_status,
                    "Preis": round(current_price, 2)
                })
            progress_bar.progress((i + 1) / len(selected_list))
        except: continue

    if hits:
        df = pd.DataFrame(hits)
        
        # --- SMA ALARM ---
        breakouts = df[df['200-Tage-Check'].str.contains("Break")]
        if not breakouts.empty:
            st.success(f"📈 Signal an der 200er Linie: {len(breakouts)} Treffer!")
            st.table(breakouts[['Aktie', '200-Tage-Check', 'Preis']])

        # --- VISUALISIERUNG ---
        st.subheader("Analyse-Matrix")
        fig = px.scatter(df, x="RSI (14)", y="Vol-Faktor", color="200-Tage-Check",
                         size=df['Perf %'].abs().add(1), hover_name="Aktie",
                         title="Fokus: Volumen vs. Trend-Status")
        st.plotly_chart(fig, use_container_width=True)
        
        # --- TABELLE MIT KLICKBAREN LINKS ---
        st.subheader("Detail-Daten (Klick auf den Namen öffnet Finanzen.net)")
        
        # Spalten-Konfiguration für klickbare Links
        st.data_editor(
            df.sort_values("Vol-Faktor", ascending=False),
            column_config={
                "Link": st.column_config.LinkColumn("Finanzen.net 🔗", display_text="Ansehen"),
                "Aktie": st.column_config.TextColumn("Ticker"),
            },
            hide_index=True,
            use_container_width=True,
            disabled=True # Deaktiviert das Editieren, behält aber das Styling
        )
    else:
        st.warning("Keine Daten gefunden.")
