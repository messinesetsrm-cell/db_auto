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
        
        # --- NORMALIZZAZIONE COLONNE ---
        # Trasformiamo tutti i nomi delle colonne in minuscolo per evitare errori
        df_p.columns = [c.strip().lower() for c in df_p.columns]
        
        col_targa = 'targa'
        col_operatore = 'operatore'
        col_data = 'data_assegnazione'

        # Verifichiamo che le colonne necessarie esistano davvero
        if col_targa not in df_p.columns:
            return False, f"❌ Colonna '{col_targa}' non trovata nel file Excel!"

        # Cerchiamo la targa (confronto case-insensitive)
        df_p[col_targa] = df_p[col_targa].astype(str).str.strip().str.upper()
        targa_input = targa_input.strip().upper()

        if targa_input in df_p[col_targa].values:
            idx = df_p.index[df_p[col_targa] == targa_input][0]
            
            vecchio_op = df_p.at[idx, col_operatore]
            data_inizio = df_p.at[idx, col_data]
            data_fine = datetime.now().strftime("%Y-%m-%d")

            # Preparazione storico
            nuova_riga_storico = {
                "Targa": [targa_input],
                "Operatore_Precedente": [vecchio_op],
                "Inizio_Assegnazione": [data_inizio],
                "Fine_Assegnazione": [data_fine]
            }
            df_new_st = pd.DataFrame(nuova_riga_storico)

            if os.path.exists(FILE_STORICO):
                df_st_esistente = pd.read_excel(FILE_STORICO)
                df_finale_st = pd.concat([df_st_esistente, df_new_st], ignore_index=True)
            else:
                df_finale_st = df_new_st
            
            df_finale_st.to_excel(FILE_STORICO, index=False)

            # Aggiornamento Database Principale
            df_p.at[idx, col_operatore] = nuovo_operatore
            df_p.at[idx, col_data] = data_fine
            df_p.to_excel(FILE_PRINCIPALE, index=False)

            return True, f"✅ Riassegnazione completata per **{targa_input}**."
        else:
            return False, f"❌ Targa **{targa_input}** non trovata."
            
    except Exception as e:
        return False, f"⚠️ Errore tecnico: {e}"

# --- INTERFACCIA STREAMLIT ---
st.set_page_config(page_title="Gestione Flotta", layout="wide")
st.title("🚗 Gestione Riassegnazione Flotta")

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
st.subheader("📊 Stato Attuale Flotta")
if os.path.exists(FILE_PRINCIPALE):
    st.dataframe(pd.read_excel(FILE_PRINCIPALE), use_container_width=True)
