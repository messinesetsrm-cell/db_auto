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
        st.error(f"File {FILE_PRINCIPALE} non trovato nel repository!")
        return

    df_p = pd.read_excel(FILE_PRINCIPALE)
    df_p.columns = df_p.columns.str.strip()

    if targa_input in df_p['Targa'].values:
        idx = df_p.index[df_p['Targa'] == targa_input][0]
        vecchio_op = df_p.at[idx, 'Operatore']
        data_inizio = df_p.at[idx, 'Data_Assegnazione']
        data_fine = datetime.now().strftime("%Y-%m-%d")

        # Storico
        nuova_riga_storico = {
            "Targa": [targa_input],
            "Operatore": [vecchio_op],
            "Inizio_Assegnazione": [data_inizio],
            "Fine_Assegnazione": [data_fine],
            "Tipo_Vettura": ["N/D"]
        }
        df_new_st = pd.DataFrame(nuova_riga_storico)

        try:
            df_st_esistente = pd.read_excel(FILE_STORICO)
            df_finale_st = pd.concat([df_st_esistente, df_new_st], ignore_index=True)
        except:
            df_finale_st = df_new_st

        df_finale_st.to_excel(FILE_STORICO, index=False)

        # Aggiornamento principale
        df_p.at[idx, 'Operatore'] = nuovo_operatore
        df_p.at[idx, 'Data_Assegnazione'] = data_fine
        df_p.to_excel(FILE_PRINCIPALE, index=False)
        
        st.success(f"✅ Riassegnazione completata per {targa_input}")
        st.balloons()
    else:
        st.error(f"❌ Errore: Targa {targa_input} non trovata.")

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
