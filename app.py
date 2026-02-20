import yfinance as yf
import pandas as pd
import streamlit as st
import plotly.express as px

# FUNKTION FÜR VERSIONSSICHERHEIT
def safe_rerun():
    if hasattr(st, "rerun"):
        st.rerun()
    else:
        st.experimental_rerun()

# 1. AUTH-CHECK
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

# --- AB HIER NUR EINGELOGGT ---

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
            # 20 Kerzen laden für sauberen RSI
            hist = stock.history(period="10d", interval=target_iv)
            if not hist.empty and len(hist) >= 15:
                # 1. VOLUMEN
                vol_ratio = round(hist['Volume'].iloc[-1] / hist['Volume'].tail(15).mean(), 2)
                
                # 2. PERFORMANCE
                perf = round(((hist['Close'].iloc[-1] - hist['Open'].iloc[-1]) / hist['Open'].iloc[-1]) * 100, 2)
                
                # 3. RSI BERECHNUNG (vereinfacht)
                delta = hist['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                rsi = round(100 - (100 / (1 + rs.iloc[-1])), 1)
                
                hits.append({
                    "Aktie": t.replace(".DE", ""), 
                    "Vol-Faktor": vol_ratio, 
                    "Perf %": perf, 
                    "RSI (14)": rsi,
                    "Preis": round(hist['Close'].iloc[-1], 2)
                })
            progress_bar.progress((i + 1) / len(selected_list))
        except: continue

    if hits:
        df = pd.DataFrame(hits)
        
        # --- ALARM SEKTION ---
        top_hits = df[df['Vol-Faktor'] >= vol_threshold].sort_values("Vol-Faktor", ascending=False)
        if not top_hits.empty:
            st.error(f"🚨 ALARM: {len(top_hits)} Aktien mit extremem Volumen gefunden!")
            cols = st.columns(len(top_hits[:3])) # Zeige Top 3 als Metrik
            for idx, row in enumerate(top_hits.iloc[:3].iterrows()):
                with cols[idx]:
                    st.metric(label=row[1]['Aktie'], value=f"Vol: {row[1]['Vol-Faktor']}", delta=f"{row[1]['Perf %']}%")

        # --- VISUALISIERUNG ---
        st.subheader("Volumen vs. Relative Stärke (RSI)")
        # Bubble Chart: X=RSI, Y=Volumen, Größe=Performance
        fig = px.scatter(df, x="RSI (14)", y="Vol-Faktor", size=df['Perf %'].abs().add(1),
                         color="Perf %", hover_name="Aktie",
                         color_continuous_scale='RdYlGn', range_color=[-2, 2],
                         title="RSI < 30 = Überverkauft | RSI > 70 = Überkauft")
        # Referenzlinien für RSI
        fig.add_vline(x=70, line_dash="dash", line_color="red", annotation_text="Überkauft")
        fig.add_vline(x=30, line_dash="dash", line_color="green", annotation_text="Überverkauft")
        st.plotly_chart(fig, use_container_width=True)
        
        # --- TABELLE ---
        st.subheader("Detail-Daten")
        # Styling für die Tabelle
        def color_rsi(val):
            if val > 70: return 'background-color: #ffcccc' # Rot für teuer
            if val < 30: return 'background-color: #ccffcc' # Grün für günstig
            return ''
            
        st.dataframe(df.sort_values("Vol-Faktor", ascending=False).style.applymap(color_rsi, subset=['RSI (14)']), use_container_width=True)
    else:
        st.warning("Keine Daten gefunden.")
