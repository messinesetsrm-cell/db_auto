import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Configurazione file
FILE_PRINCIPALE = "flotta.xlsx"
FILE_STORICO = "storico_assegnazioni.xlsx"

# --- FUNZIONE LOGICA ---
def registra_riassegnazione(targa_input, nuovo_operatore):
    try:
        # Carichiamo il database attuale
        if not os.path.exists(FILE_PRINCIPALE):
            return False, f"❌ Errore: Il file '{FILE_PRINCIPALE}' non esiste nella cartella."
        
        df_p = pd.read_excel(FILE_PRINCIPALE)
        df_p.columns = df_p.columns.str.strip() # Pulizia nomi colonne
        
        # Cerchiamo la targa
        if targa_input in df_p['Targa'].values:
            idx = df_p.index[df_p['Targa'] == targa_input][0]
            
            # Recuperiamo i dati prima della modifica
            vecchio_op = df_p.at[idx, 'Operatore']
            data_inizio = df_p.at[idx, 'Data_Assegnazione']
            data_fine = datetime.now().strftime("%Y-%m-%d")

            # Preparazione dati per lo storico
            nuova_riga_storico = {
                "Targa": [targa_input],
                "Operatore_Precedente": [vecchio_op],
                "Inizio_Assegnazione": [data_inizio],
                "Fine_Assegnazione": [data_fine],
                "Tipo_Vettura": ["N/D"] 
            }
            df_new_st = pd.DataFrame(nuova_riga_storico)

            # Salvataggio Storico
            if os.path.exists(FILE_STORICO):
                df_st_esistente = pd.read_excel(FILE_STORICO)
                df_finale_st = pd.concat([df_st_esistente, df_new_st], ignore_index=True)
            else:
                df_finale_st = df_new_st
            df_finale_st.to_excel(FILE_STORICO, index=False)

            # Aggiornamento Database Principale
            df_p.at[idx, 'Operatore'] = nuovo_operatore
            df_p.at[idx, 'Data_Assegnazione'] = data_fine
            df_p.to_excel(FILE_PRINCIPALE, index=False)

            return True, f"✅ Riassegnazione completata per la targa **{targa_input}**."
        else:
            return False, f"❌ La targa **{targa_input}** non è stata trovata nel database."
            
    except Exception as e:
        return False, f"⚠️ Si è verificato un errore: {e}"

# --- INTERFACCIA UTENTE (STREAMLIT) ---
st.set_page_config(page_title="Gestione Flotta", layout="wide")

st.title("🚗 Gestione Riassegnazione Flotta")
st.markdown("Usa questo strumento per aggiornare l'operatore di una vettura e salvare lo storico.")

# Layout a colonne per l'inserimento dati
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        targa = st.text_input("Inserisci Targa", placeholder="es. AA123BB").strip().upper()
    with col2:
        nuovo = st.text_input("Nuovo Operatore", placeholder="Nome Cognome").strip().upper()

    if st.button("Conferma Riassegnazione", use_container_width=True):
        if targa and nuovo:
            successo, messaggio = registra_riassegnazione(targa, nuovo)
            if successo:
                st.success(messaggio)
                st.balloons() # Animazione di successo
            else:
                st.error(messaggio)
        else:
            st.warning("⚠️ Inserisci sia la targa che il nuovo operatore.")

# --- SEZIONE VISUALIZZAZIONE DATI ---
st.divider()
st.subheader("📊 Stato Attuale Flotta")

if os.path.exists(FILE_PRINCIPALE):
    df_mostra = pd.read_excel(FILE_PRINCIPALE)
    st.dataframe(df_mostra, use_container_width=True)
else:
    st.info("Carica il file 'flotta.xlsx' nella cartella del progetto per vedere i dati.")
