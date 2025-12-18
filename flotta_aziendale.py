import pandas as pd
from datetime import datetime
import streamlit as st
import os

# Configurazione Pagina
st.set_page_config(page_title="Gestione Flotta", layout="wide")
st.title("🚗 Gestione Flotta Aziendale")

FILE_PRINCIPALE = "flotta.xlsx"
FILE_STORICO = "storico_assegnazioni.xlsx"

# --- FUNZIONE LOGICA ---
def registra_riassegnazione(targa_input, nuovo_operatore):
    if not os.path.exists(FILE_PRINCIPALE):
        st.error(f"File {FILE_PRINCIPALE} non trovato!")
        return

    df_p = pd.read_excel(FILE_PRINCIPALE)
    
    # FORZIAMO TUTTE LE COLONNE IN MINUSCOLO per evitare errori
    df_p.columns = [str(c).strip().lower() for c in df_p.columns]

    # Ora cerchiamo usando il nome minuscolo 'targa'
    if 'targa' in df_p.columns:
        # Puliamo anche i dati nella colonna targa da eventuali spazi
        df_p['targa'] = df_p['targa'].astype(str).str.strip().str.upper()
        targa_input = targa_input.strip().upper()

        if targa_input in df_p['targa'].values:
            idx = df_p.index[df_p['targa'] == targa_input][0]

            # Recuperiamo i dati (usando i nomi minuscoli delle colonne)
            vecchio_op = df_p.at[idx, 'operatore'] if 'operatore' in df_p.columns else "N/D"
            
            # Se la colonna data_assegnazione non esiste, la creiamo
            col_data = 'data_assegnazione'
            data_fine = datetime.now().strftime("%Y-%m-%d")

            # Aggiornamento
            if 'operatore' in df_p.columns:
                df_p.at[idx, 'operatore'] = nuovo_operatore
            
            if col_data in df_p.columns:
                df_p.at[idx, col_data] = data_fine
            else:
                df_p[col_data] = "" # Crea colonna se manca
                df_p.at[idx, col_data] = data_fine

            # Salvataggio
            df_p.to_excel(FILE_PRINCIPALE, index=False)
            st.success(f"✅ Riassegnazione completata per {targa_input}!")
            st.balloons()
            st.rerun() # Ricarica l'app per mostrare la tabella aggiornata
        else:
            st.error(f"❌ Errore: Targa {targa_input} non trovata nei dati.")
    else:
        st.error("❌ Errore critico: Colonna 'targa' non trovata nel file Excel.")
# --- INTERFACCIA STREAMLIT ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("Registra Cambio Operatore")
    targa_form = st.text_input("Inserisci Targa:").strip().upper()
    nuovo_form = st.text_input("Inserisci Nuovo Operatore:").strip().upper()
    
    if st.button("Aggiorna Database"):
        if targa_form and nuovo_form:
            registra_riassegnazione(targa_form, nuovo_form)
        else:
            st.warning("Compila entrambi i campi")

with col2:
    st.subheader("Visualizza Dati Attuali")
    if os.path.exists(FILE_PRINCIPALE):
        df_view = pd.read_excel(FILE_PRINCIPALE)
        st.dataframe(df_view)
    else:
        st.info("Carica il file flotta.xlsx per vedere la tabella")
