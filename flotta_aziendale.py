import streamlit as st
import pandas as pd
from datetime import datetime

# Configurazione file
FILE_PRINCIPALE = "flotta.xlsx"
FILE_STORICO = "storico_assegnazioni.xlsx"

# --- 1. FUNZIONE DI LOGICA (Il tuo motore) ---
def aggiorna_database_e_storico(targa_target, nuovo_op):
    try:
        df_p = pd.read_excel(FILE_PRINCIPALE)
        df_p.columns = df_p.columns.str.strip() # Pulisce i nomi delle colonne

        if targa_target in df_p['Targa'].values:
            idx = df_p.index[df_p['Targa'] == targa_target][0]
            
            vecchio_op = df_p.at[idx, 'Operatore']
            data_inizio_val = df_p.at[idx, 'Data_Assegnazione']
            
            # Calcolo giorni di possesso
            try:
                data_inizio = pd.to_datetime(data_inizio_val)
                giorni = (datetime.now() - data_inizio).days
            except:
                giorni = "N/D"

            # Aggiornamento Storico
            nuova_riga_st = {
                "Targa": [targa_target],
                "Operatore": [vecchio_op],
                "Inizio_Assegnazione": [data_inizio_val],
                "Fine_Assegnazione": [datetime.now().strftime("%Y-%m-%d")],
                "Giorni_Utilizzo": [giorni],
                "Tipo_Vettura": ["N/D"]
            }
            df_new_st = pd.DataFrame(nuova_riga_st)

            try:
                df_st_esistente = pd.read_excel(FILE_STORICO)
                df_finale_st = pd.concat([df_st_esistente, df_new_st], ignore_index=True)
            except:
                df_finale_st = df_new_st
            
            df_finale_st.to_excel(FILE_STORICO, index=False)

            # Aggiornamento Database Principale
            df_p.at[idx, 'Operatore'] = nuovo_op.upper()
            df_p.at[idx, 'Data_Assegnazione'] = datetime.now().strftime("%Y-%m-%d")
            df_p.to_excel(FILE_PRINCIPALE, index=False)
            
            return True, f"✅ {targa_target} riassegnata a {nuovo_op}"
        return False, "❌ Targa non trovata."
    except Exception as e:
        return False, f"⚠️ Errore: {e}"

# --- 2. INTERFACCIA GRAFICA (La tua dashboard) ---
st.set_page_config(layout="wide")
st.title("🚗 Gestione Flotta Aziendale")

# Layout a due colonne come nel tuo screenshot
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📝 Registra Cambio")
    targa_in = st.text_input("Targa Veicolo").upper().strip()
    nuovo_op_in = st.text_input("Nuovo Operatore").upper().strip()
    
    if st.button("Applica Modifica"):
        if targa_in and nuovo_op_in:
            successo, messaggio = aggiorna_database_e_storico(targa_in, nuovo_op_in)
            if successo:
                st.success(messaggio)
                # Forza il refresh della pagina per aggiornare la tabella
                st.rerun()
            else:
                st.error(messaggio)
        else:
            st.warning("Inserisci sia targa che operatore!")

with col2:
    st.subheader("📊 Anteprima Flotta")
    try:
        df_visualizza = pd.read_excel(FILE_PRINCIPALE)
        st.dataframe(df_visualizza, use_container_width=True, hide_index=True)
    except:
        st.error("Carica il file flotta.xlsx per vedere la tabella.")

# Sezione Salva il lavoro
st.divider()
st.subheader("💾 Salva il lavoro")
with open(FILE_PRINCIPALE, "rb") as f:
    st.download_button("📥 SCARICA EXCEL AGGIORNATO", f, file_name="flotta_aggiornata.xlsx")
