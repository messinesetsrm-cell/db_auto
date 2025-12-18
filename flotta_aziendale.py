import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import io

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Gestione Flotta", layout="wide", page_icon="🚗")
st.title("🚗 Gestione Flotta Aziendale")

# Connessione
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data(sheet_name):
    # Forza la lettura ignorando la cache locale
    df = conn.read(worksheet=sheet_name, ttl=0)
    df.columns = [str(c).strip().lower() for c in df.columns]
    return df

# --- INTERFACCIA ---
try:
    df_flotta = get_data("flotta")
    
    # Debug URL (opzionale, puoi rimuoverlo dopo che funziona)
    st.write(f"Connesso con successo al foglio: **flotta**")

    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("📝 Registra Cambio")
        with st.form("form_update"):
            targa = st.text_input("Targa").upper()
            nuovo = st.text_input("Nuovo Operatore").upper()
            if st.form_submit_button("Salva su Cloud"):
                # Qui la logica di update fornita nei messaggi precedenti
                pass

    with col2:
        st.subheader("📊 Stato Attuale")
        st.dataframe(df_flotta, hide_index=True)

    # Storico e Download
    st.divider()
    df_storico = get_data("storico")
    st.subheader("📜 Storico")
    st.dataframe(df_storico, hide_index=True)

except Exception as e:
    st.error("⚠️ Errore di connessione al database.")
    st.info("Segui la procedura qui sotto per correggere l'URL nelle Secrets.")
