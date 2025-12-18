import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Configurazione file
FILE_PRINCIPALE = "flotta.xlsx"
FILE_STORICO = "storico_assegnazioni.xlsx"

def registra_riassegnazione(targa_input, nuovo_operatore):
    try:
        if not os.path.exists(FILE_PRINCIPALE):
            return False, f"❌ Errore: Il file '{FILE_PRINCIPALE}' non esiste."
        
        df_p = pd.read_excel(FILE_PRINCIPALE)
        
        # Normalizzazione colonne per evitare KeyError
        df_p.columns = [c.strip().lower() for c in df_p.columns]
        
        col_targa = 'targa'
        col_operatore = 'operatore'
        col_data = 'data_assegnazione'

        # Pulizia dati targa
        df_p[col_targa] = df_p[col_targa].astype(str).str.strip().str.upper()
        targa_input = targa_input.strip().upper()

        if targa_input in df_p[col_targa].values:
            idx = df_p.index[df_p[col_targa] == targa_input][0]
            
            vecchio_op = df_p.at[idx, col_operatore]
            data_inizio = df_p.at[idx, col_data]
            data_fine = datetime.now().strftime("%Y-%m-%d")

            # --- AGGIORNAMENTO STORICO ---
            nuova_riga_storico = {
                "Targa": [targa_input],
                "Operatore_Precedente": [vecchio_op],
                "Nuovo_Operatore": [nuovo_operatore],
                "Data_Cambio": [data_fine]
            }
            df_new_st = pd.DataFrame(nuova_riga_storico)

            if os.path.exists(FILE_STORICO):
                df_st_esistente = pd.read_excel(FILE_STORICO)
                df_finale_st = pd.concat([df_st_esistente, df_new_st], ignore_index=True)
            else:
                df_finale_st = df_new_st
            
            df_finale_st.to_excel(FILE_STORICO, index=False)

            # --- AGGIORNAMENTO PRINCIPALE ---
            df_p.at[idx, col_operatore] = nuovo_operatore
            df_p.at[idx, col_data] = data_fine
            df_p.to_excel(FILE_PRINCIPALE, index=False)

            return True, f"✅ Riassegnazione completata per **{targa_input}**."
        else:
            return False, f"❌ Targa **{targa_input}** non trovata."
            
    except Exception as e:
        return False, f"⚠️ Errore: {e}"

# --- INTERFACCIA STREAMLIT ---
st.set_page_config(page_title="Gestione Flotta", layout="wide")
st.title("🚗 Gestione Riassegnazione Flotta")

# Input dati
col1, col2 = st.columns(2)
with col1:
    targa = st.text_input("Inserisci Targa", placeholder="es. GX834SK").strip().upper()
with col2:
    nuovo = st.text_input("Nuovo Operatore", placeholder="es. FINE RENT").strip().upper()

if st.button("Conferma Riassegnazione", use_container_width=True):
    if targa and nuovo:
        successo, messaggio = registra_riassegnazione(targa, nuovo)
        if successo:
            st.success(messaggio)
            st.balloons()
        else:
            st.error(messaggio)
    else:
        st.warning("⚠️ Compila entrambi i campi.")

st.divider()

# --- SEZIONE DOWNLOAD E STATO ATTUALE ---
col_titolo, col_download = st.columns([3, 1])

with col_titolo:
    st.subheader("📊 Stato Attuale Flotta")

if os.path.exists(FILE_PRINCIPALE):
    df_attuale = pd.read_excel(FILE_PRINCIPALE)
    
    # Tasto per scaricare l'Excel aggiornato
    with col_download:
        with open(FILE_PRINCIPALE, "rb") as f:
            st.download_button(
                label="📥 Scarica Excel Aggiornato",
                data=f,
                file_name="flotta_aggiornata.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    
    st.dataframe(df_attuale, use_container_width=True)

# --- SEZIONE STORICO MOVIMENTI ---
st.divider()
st.subheader("📜 Storico Movimenti (Log)")

if os.path.exists(FILE_STORICO):
    df_st = pd.read_excel(FILE_STORICO)
    # Mostriamo gli ultimi movimenti in alto
    st.dataframe(df_st.sort_index(ascending=False), use_container_width=True)
else:
    st.info("Nessun movimento registrato nello storico.")
