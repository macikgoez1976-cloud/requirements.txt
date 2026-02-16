import streamlit as st
import main

# --- 1. PASSWORT-SCHUTZ MIT LOGIN-BUTTON ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

st.sidebar.title("🔐 Projekt Asperg")

if not st.session_state["authenticated"]:
    # Passwort-Eingabe ohne automatischen Submit
    input_password = st.sidebar.text_input("Passwort", type="password")
    
    # Der dedizierte Login-Button
    if st.sidebar.button("Einloggen"):
        if input_password == st.secrets["APP_PASSWORD"]:
            st.session_state["authenticated"] = True
            st.rerun() # Seite neu laden, um Login zu bestätigen
        else:
            st.sidebar.error("Falsches Passwort!")
    st.stop() # App stoppt hier, wenn nicht eingeloggt

# --- 2. HAUPTSEITE (Nur sichtbar nach Login) ---
st.title("🚀 Projekt Asperg: Multi-Scanner")

# Index-Auswahl in der Seitenleiste
st.sidebar.header("Scanner-Einstellungen")
gewaehlter_index = st.sidebar.selectbox(
    "Index wählen:", 
    ["DAX", "MDAX", "SDAX", "TecDAX"]
)

st.write(f"Bereit für den Scan von: **{gewaehlter_index}**")

# Der dedizierte "Enter"-Button für den Scan
if st.button(f"Starte {gewaehlter_index} Analyse"):
    with st.spinner(f"Suche im {gewaehlter_index} nach Volumen-Sprüngen..."):
        # Aufruf der Logik in main.py
        ergebnisse = main.run_asperg_scan(gewaehlter_index)
        
        if ergebnisse:
            st.success(f"Scan für {gewaehlter_index} abgeschlossen!")
            # Erstellt eine schöne Übersicht für jeden Treffer
            for treffer in ergebnisse:
                with st.expander(f"📈 {treffer['Aktie']} ({treffer['Symbol']})"):
                    st.write(f"**Volumen-Faktor:** {treffer['Vol-Faktor']}")
                    st.write(f"**Status:** {treffer['Ampel']}")
        else:
            st.info(f"Aktuell keine auffälligen Aktien im {gewaehlter_index} gefunden.")

# Logout-Option (falls du dich mal abmelden willst)
if st.sidebar.button("Logout"):
    st.session_state["authenticated"] = False
    st.rerun()
