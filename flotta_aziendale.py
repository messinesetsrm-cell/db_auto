import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Configurazione nomi file
FILE_PRINCIPALE = "flotta.xlsx"
FILE_STORICO = "storico_assegnazioni.xlsx"

# --- 1. LOGICA DI AGGIORNAMENTO ---
def registra_cambio_operatore(targa_input, nuovo_op_nome):
    try:
        # Carica il database attuale
        df_p = pd.read_excel(FILE_PRINCIPALE)
        
        # PULIZIA: Rimuoviamo spazi dai nomi delle colonne per evitare KeyError
        df_p.columns = df_p.columns.str.strip()
        
        targa_cercata = targa_input.strip().upper()
        
        # Cerchiamo la targa ignorando maiuscole/minuscole
        if targa_cercata in df_p['Targa'].astype(str).str.upper().values:
            idx = df_p.index[df_p['Targa'].astype(str).str.upper() == targa_cercata][0]
            
            # Recupero dati per lo storico
            vecchio_op = df_p.at[idx, 'Operatore']
            data_inizio_originale = df_p.at[idx, 'Data_Assegnazione']
            data_oggi = datetime.now().strftime("%Y-%m-%d")

            # Calcolo giorni di utilizzo
            try:
                inizio_dt = pd.to_datetime(data_inizio_originale)
                giorni = (datetime.now() - inizio_dt).days
            except:
                giorni = "N/D"

            # --- SALVATAGGIO STORICO ---
            # Impostiamo 'Tipo_Vettura' a "N/D" perché non esiste nel file flotta.xlsx
            nuova_riga_st = {
                "Targa": [targa_input.upper()],
                "Operatore": [vecchio_op],
                "Inizio_Assegnazione": [data_inizio_originale],
                "Fine_Assegnazione": [data_oggi],
                "Giorni_Utilizzo": [giorni],
                "Tipo_Vettura": ["N/D"] 
            }
            df_nuovo_st = pd.DataFrame(nuova_riga_st)

            if os.path.exists(FILE_STORICO):
                df_st_vecchio = pd.read_excel(FILE_STORICO)
                df_st_finale = pd.concat([df_st_vecchio, df_nuovo_st], ignore_index=True)
            else:
                df_st_finale = df_nuovo_st
            
            df_st_finale.to_excel(FILE_STORICO, index=False)

            # --- AGGIORNAMENTO FILE PRINCIPALE ---
            df_p.at[idx, 'Operatore'] = nuovo_op_nome.upper()
            df_p.at[idx, 'Data_Assegnazione'] = data_oggi
            df_p.to_excel(FILE_PRINCIPALE, index=False)
            
            return True, f"✅ Aggiornamento riuscito per {targa_input.upper()}"
        else:
            return False, f"❌ La targa {targa_input.upper()} non è presente nel database."

    except Exception as e:
        return False, f"⚠️ Errore tecnico: {str(e)}"

# --- 2. LAYOUT DASHBOARD ---
st.set_page_config(layout="wide", page_title="Gestionale Flotta")
st.title("🚗 Gestione Flotta Aziendale")

col_form, col_tabella = st.columns([1, 2])

with col_form:
    st.subheader("📝 Registra Cambio")
    targa_veicolo = st.text_input("Targa Veicolo", placeholder="Es. GX666SK").upper()
    nuovo_operatore = st.text_input("Nuovo Operatore", placeholder="Es. FINE RENT").upper()
    
    if st.button("Applica Modifica", use_container_width=True):
        if targa_veicolo and nuovo_operatore:
            successo, msg = registra_cambio_operatore(targa_veicolo, nuovo_operatore)
            if successo:
                st.success(msg)
                st.rerun() # Forza il ricaricamento per aggiornare la tabella
            else:
                st.error(msg)
        else:
            st.warning("Completa tutti i campi.")

with col_tabella:
    st.subheader("📊 Anteprima Flotta")
    if os.path.exists(FILE_PRINCIPALE):
        df_mostra = pd.read_excel(FILE_PRINCIPALE)
        st.dataframe(df_mostra, use_container_width=True, hide_index=True)
    else:
        st.info("File flotta.xlsx non trovato.")

st.divider()
st.subheader("💾 Salva il lavoro")
if os.path.exists(FILE_PRINCIPALE):
    with open(FILE_PRINCIPALE, "rb") as f:
        st.download_button(
            label="📥 SCARICA EXCEL AGGIORNATO",
            data=f,
            file_name="flotta_aggiornata.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
