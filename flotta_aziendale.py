import streamlit as st
import pandas as pd
from datetime import datetime

# Configurazione nomi file
FILE_PRINCIPALE = "flotta.xlsx"
FILE_STORICO = "storico_assegnazioni.xlsx"

# --- 1. MOTORE DEL PROGRAMMA (Logica di Aggiornamento) ---
def aggiorna_database_e_storico(targa_input, nuovo_op_nome):
    try:
        # Carichiamo il file principale
        df_p = pd.read_excel(FILE_PRINCIPALE)
        
        # NORMALIZZAZIONE: Trasforma tutto in minuscolo per evitare errori di battitura
        df_p.columns = df_p.columns.str.strip().str.lower()
        targa_cercata = targa_input.strip().lower()

        # Verifichiamo se la targa esiste
        if targa_cercata in df_p['targa'].values:
            # Troviamo la riga esatta
            idx = df_p.index[df_p['targa'] == targa_cercata][0]
            
            # Recuperiamo i dati attuali per lo storico
            vecchio_op = df_p.at[idx, 'operatore']
            data_inizio_val = df_p.at[idx, 'data_assegnazione']
            data_fine = datetime.now().strftime("%Y-%m-%d")

            # Calcolo automatico dei giorni di possesso
            try:
                data_inizio_dt = pd.to_datetime(data_inizio_val)
                giorni_possesso = (datetime.now() - data_inizio_dt).days
            except:
                giorni_possesso = "N/D"

            # --- AGGIORNAMENTO STORICO ---
            nuova_riga_st = {
                "Targa": [targa_input.upper()],
                "Operatore": [vecchio_op],
                "Inizio_Assegnazione": [data_inizio_val],
                "Fine_Assegnazione": [data_fine],
                "Giorni_Utilizzo": [giorni_possesso],
                "Tipo_Vettura": ["N/D"] # Colonna non presente nel file principale
            }
            df_new_st = pd.DataFrame(nuova_riga_st)

            try:
                df_st_esistente = pd.read_excel(FILE_STORICO)
                df_finale_st = pd.concat([df_st_esistente, df_new_st], ignore_index=True)
            except:
                df_finale_st = df_new_st
            
            # Salvataggio fisico dello storico
            df_finale_st.to_excel(FILE_STORICO, index=False)

            # --- AGGIORNAMENTO DATABASE ATTUALE ---
            df_p.at[idx, 'operatore'] = nuovo_op_nome.upper()
            df_p.at[idx, 'data_assegnazione'] = data_fine

            # Ripristiniamo i nomi originali delle colonne (Maiuscole) prima di salvare
            df_p.columns = ['Operatore', 'Targa', 'Data_Assegnazione']
            df_p.to_excel(FILE_PRINCIPALE, index=False)
            
            return True, f"✅ Mezzo {targa_input.upper()} assegnato a {nuovo_op_nome.upper()}."
        else:
            return False, f"❌ La targa {targa_input.upper()} non è presente nel database."
            
    except Exception as e:
        return False, f"⚠️ Errore durante l'operazione: {str(e)}"

# --- 2. INTERFACCIA STREAMLIT (Il tuo Layout) ---
st.set_page_config(layout="wide", page_title="Gestionale Flotta")
st.title("🚗 Gestione Flotta Aziendale")

# Suddivisione in due colonne
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📝 Registra Cambio")
    # Campi di inserimento
    targa_veicolo = st.text_input("Targa Veicolo", placeholder="Es. GL111TJ")
    nuovo_operatore = st.text_input("Nuovo Operatore", placeholder="Es. MARIO ROSSI")
    
    if st.button("Applica Modifica"):
        if targa_veicolo and nuovo_operatore:
            successo, messaggio = aggiorna_database_e_storico(targa_veicolo, nuovo_operatore)
            if successo:
                st.success(messaggio)
                st.rerun() # Ricarica per aggiornare la tabella a destra
            else:
                st.error(messaggio)
        else:
            st.warning("⚠️ Compila entrambi i campi!")

with col2:
    st.subheader("📊 Anteprima Flotta")
    try:
        # Visualizzazione tabella aggiornata
        df_view = pd.read_excel(FILE_PRINCIPALE)
        st.dataframe(df_view, use_container_width=True, hide_index=True)
    except:
        st.info("Carica i file Excel nella cartella per iniziare.")

# Sezione salvataggio finale
st.divider()
st.subheader("💾 Salva il lavoro")
try:
    with open(FILE_PRINCIPALE, "rb") as f:
        st.download_button(
            label="📥 SCARICA EXCEL AGGIORNATO",
            data=f,
            file_name="flotta_aggiornata.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
except:
    st.write("Nessun file disponibile per il download.")
