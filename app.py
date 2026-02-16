import streamlit as st
import main

# Konfiguration der Seite
st.set_page_config(page_title="Projekt Asperg", layout="wide")

# --- LOGIN LOGIK ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

st.sidebar.title("🔐 Login Bereich")

if not st.session_state["authenticated"]:
    pw_input = st.sidebar.text_input("Passwort eingeben", type="password")
    if st.sidebar.button("Einloggen"):
        if pw_input == st.secrets["APP_PASSWORD"]:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.sidebar.error("Falsches Passwort!")
    st.stop()

# --- DASHBOARD NACH LOGIN ---
st.title("🚀 Projekt Asperg: Markt-Scanner")

st.sidebar.write("---")
st.sidebar.header("Einstellungen")
wahl = st.sidebar.selectbox("Welchen Index prüfen?", ["DAX", "MDAX", "SDAX", "TecDAX"])

if st.button(f"Scan für {wahl} jetzt starten"):
    with st.spinner(f"Analysiere {wahl} Aktien..."):
        ergebnisse = main.run_asperg_scan(wahl)
        
        if ergebnisse:
            st.success(f"Gefundene Volumen-Ausreißer im {wahl}:")
            # Wir machen daraus eine schöne Tabelle
            df = pd.DataFrame(ergebnisse)
            st.table(df)
        else:
            st.info(f"Im {wahl} gibt es aktuell keine auffälligen Bewegungen (>1.5x Volumen).")

if st.sidebar.button("Logout"):
    st.session_state["authenticated"] = False
    st.rerun()
