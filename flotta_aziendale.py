import streamlit as st
import pandas as pd
from datetime import datetime
import io

st.set_page_config(page_title="Gestione Flotta", layout="wide", page_icon="🚗")
st.title("🚗 Gestione Flotta Aziendale")

# --- CARICAMENTO E PULIZIA DATI ---
@st.cache_data
def load_local_data():
    try:
        df_f = pd.read_excel("flotta.xlsx")
        df_s = pd.read_excel("storico_assegnazioni.xlsx")
        
        # Pulizia: nomi colonne in minuscolo e senza spazi
        df_f.columns = [str(c).strip().lower() for c in df_f.columns]
        df_s.columns = [str(c).strip().lower() for c in df_s.columns]
        
        # PULIZIA FONDAMENTALE: Toglie spazi bianchi da TUTTE le celle di testo
        df_f = df_f.applymap(lambda x: x.strip() if isinstance(x, str) else x)
        
        return df_f, df_s
    except Exception as e:
        st.error(f"Errore caricamento file: {e}")
        return pd.DataFrame(), pd.DataFrame()

if 'df_flotta' not in st.session_state:
    st.session_state.df_flotta, st.session_state.df_storico = load_local_data()

# --- INTERFACCIA ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📝 Registra Cambio")
    with st.form("form_cambio"):
        # Puliamo l'input dell'utente eliminando spazi prima e dopo
        targa_input = st.text_input("Targa Veicolo").strip().upper()
        nuovo_op = st.text_input("Nuovo Operatore").strip().upper()
        submit = st.form_submit_button("Applica Modifica")

        if submit:
            df_p = st.session_state.df_flotta
            
            # Confronto reso ultra-sicuro convertendo tutto in stringa e togliendo spazi
            if targa_input in df_p['targa'].astype(str).values:
                idx = df_p.index[df_p['targa'].astype(str) == targa_input][0]
                
                vecchio_op = df_p.at[idx, 'operatore']
                data_cambio = datetime.now().strftime("%d/%m/%Y")

                st.session_state.df_flotta.at[idx, 'operatore'] = nuovo_op
                st.session_state.df_flotta.at[idx, 'data_assegnazione'] = data_cambio

                nuovo_log = pd.DataFrame([{
                    "targa": targa_input,
                    "vecchio_operatore": vecchio_op,
                    "nuovo_operatore": nuovo_op,
                    "data_cambio": data_cambio
                }])
                st.session_state.df_storico = pd.concat([st.session_state.df_storico, nuovo_log], ignore_index=True)
                
                st.success(f"✅ Modifica applicata per {targa_input}!")
                st.balloons()
            else:
                st.error(f"❌ La targa '{targa_input}' non è stata trovata. Verifica che sia scritta correttamente nel file Excel.")

with col2:
    st.subheader("📊 Anteprima Flotta")
    st.dataframe(st.session_state.df_flotta, use_container_width=True, hide_index=True)

st.divider()

# --- DOWNLOAD ---
st.subheader("💾 Salva il lavoro")
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
    st.session_state.df_flotta.to_excel(writer, index=False, sheet_name='Flotta')
    st.session_state.df_storico.to_excel(writer, index=False, sheet_name='Storico')

st.download_button(
    label="📥 SCARICA EXCEL AGGIORNATO",
    data=buffer.getvalue(),
    file_name=f"flotta_aggiornata_{datetime.now().strftime('%H%M')}.xlsx",
    mime="application/vnd.ms-excel"
)
