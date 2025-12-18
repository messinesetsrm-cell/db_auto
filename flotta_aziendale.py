import streamlit as st
import pandas as pd
from datetime import datetime
import io

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Gestione Flotta Locale", layout="wide", page_icon="🚗")

st.title("🚗 Gestione Flotta Aziendale")
st.markdown("Modifica i dati e scarica il file aggiornato sul tuo PC.")

# --- CARICAMENTO DATI DA GITHUB ---
@st.cache_data
def load_local_data():
    try:
        # Legge i file che hai caricato nel tuo repository
        df_f = pd.read_excel("flotta.xlsx")
        df_s = pd.read_excel("storico_assegnazioni.xlsx")
        # Pulizia colonne
        df_f.columns = [str(c).strip().lower() for c in df_f.columns]
        df_s.columns = [str(c).strip().lower() for c in df_s.columns]
        return df_f, df_s
    except Exception as e:
        st.error(f"Errore caricamento file Excel da GitHub: {e}")
        return pd.DataFrame(), pd.DataFrame()

# Inizializzazione stato della sessione per mantenere le modifiche
if 'df_flotta' not in st.session_state:
    st.session_state.df_flotta, st.session_state.df_storico = load_local_data()

# --- INTERFACCIA DI AGGIORNAMENTO ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📝 Registra Cambio")
    with st.form("form_cambio"):
        targa_input = st.text_input("Targa Veicolo").upper().strip()
        nuovo_op = st.text_input("Nuovo Operatore").upper().strip()
        submit = st.form_submit_button("Applica Modifica")

        if submit:
            df_p = st.session_state.df_flotta
            if targa_input in df_p['targa'].astype(str).values:
                idx = df_p.index[df_p['targa'].astype(str) == targa_input][0]
                
                # Dati per lo storico
                vecchio_op = df_p.at[idx, 'operatore']
                data_cambio = datetime.now().strftime("%d/%m/%Y")

                # Aggiorno flotta in sessione
                st.session_state.df_flotta.at[idx, 'operatore'] = nuovo_op
                st.session_state.df_flotta.at[idx, 'data_assegnazione'] = data_cambio

                # Aggiorno storico in sessione
                nuovo_log = pd.DataFrame([{
                    "targa": targa_input,
                    "vecchio_operatore": vecchio_op,
                    "nuovo_operatore": nuovo_op,
                    "data_cambio": data_cambio
                }])
                st.session_state.df_storico = pd.concat([st.session_state.df_storico, nuovo_log], ignore_index=True)
                
                st.success(f"Modifica applicata in memoria per {targa_input}!")
            else:
                st.error("Targa non trovata nel file.")

with col2:
    st.subheader("📊 Anteprima Flotta (Modificata)")
    st.dataframe(st.session_state.df_flotta, use_container_width=True, hide_index=True)

st.divider()

# --- SEZIONE DOWNLOAD (L'AGGIORNAMENTO LOCALE) ---
st.subheader("💾 Salva le modifiche sul tuo PC")
st.info("Clicca il tasto qui sotto per scaricare il file Excel aggiornato con le nuove assegnazioni.")

# Generazione file Excel in memoria per il download
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
    st.session_state.df_flotta.to_excel(writer, index=False, sheet_name='Flotta_Aggiornata')
    st.session_state.df_storico.to_excel(writer, index=False, sheet_name='Storico_Completo')

st.download_button(
    label="📥 SCARICA EXCEL AGGIORNATO",
    data=buffer.getvalue(),
    file_name=f"database_flotta_aggiornato_{datetime.now().strftime('%H%M')}.xlsx",
    mime="application/vnd.ms-excel"
)
