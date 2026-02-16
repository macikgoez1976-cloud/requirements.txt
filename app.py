import streamlit as st
import main

# --- PASSWORT-SCHUTZ ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

def check_password():
    if st.sidebar.text_input("Passwort", type="password") == st.secrets["APP_PASSWORD"]:
        st.session_state["authenticated"] = True
    else:
        st.sidebar.warning("Bitte Passwort eingeben")

if not st.session_state["authenticated"]:
    check_password()
    st.stop()

# --- HAUPTSEITE ---
st.title("🚀 Projekt Asperg: Multi-Scanner")

# Auswahlmenü
gewaehlter_index = st.sidebar.selectbox(
    "Welchen Index scannen?", 
    ["DAX", "MDAX", "SDAX", "TecDAX"]
)

if st.button(f"Scanne jetzt {gewaehlter_index}"):
    # Hier rufen wir die Funktion in der main.py auf
    ergebnisse = main.run_asperg_scan(gewaehlter_index)
    
    if ergebnisse:
        for treffer in ergebnisse:
            st.write(treffer)
    else:
        st.info("Keine Treffer nach den Kriterien gefunden.")
