import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import io

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Gestione Flotta Cloud", layout="wide", page_icon="🚗")

st.title("🚗 Gestione Flotta Aziendale (Google Sheets)")
st.markdown("Aggiorna le assegnazioni in tempo reale sul database cloud.")

# --- CONNESSIONE A GOOGLE SHEETS ---
# Assicurati che nelle Secrets l'URL sia pulito (senza gid finali)
conn = st.connection("gsheets", type=GSheetsConnection)
st.write("Verifica URL:", st.secrets["connections"]["gsheets"]["spreadsheet"])
# --- FUNZIONE PER LEGGERE I DATI ---
def get_data(sheet_name):
    # Legge il foglio e normalizza i nomi delle colonne in minuscolo
    df = conn.read(worksheet=sheet_name, ttl=0) # ttl=0 forza l'aggiornamento senza cache
    df.columns = [str(c).strip().lower() for c in df.columns]
    return df

# --- FUNZIONE PER REGISTRARE IL CAMBIO ---
def registra_riassegnazione(targa_input, nuovo_operatore):
    # 1. Carica i dati attuali
    df_p = get_data("flotta")
    targa_input = targa_input.strip().upper()
    nuovo_operatore = nuovo_operatore.strip().upper()

    if 'targa' in df_p.columns:
        # Pulizia colonna targa per il confronto
        df_p['targa'] = df_p['targa'].astype(str).str.strip().str.upper()

        if targa_input in df_p['targa'].values:
            idx = df_p.index[df_p['targa'] == targa_input][0]
            
            # Recupero dati per lo storico prima dell'aggiornamento
            vecchio_op = df_p.at[idx, 'operatore'] if 'operatore' in df_p.columns else "N/D"
            data_inizio = df_p.at[idx, 'data_assegnazione'] if 'data_assegnazione' in df_p.columns else "N/D"
            data_cambio = datetime.now().strftime("%Y-%m-%d")

            # 2. Aggiorna Tabella Principale ('flotta')
            df_p.at[idx, 'operatore'] = nuovo_operatore
            df_p.at[idx, 'data_assegnazione'] = data_cambio
            conn.update(worksheet="flotta", data=df_p)

            # 3. Aggiorna Tabella Storico ('storico')
            df_st = get_data("storico")
            nuovo_log = pd.DataFrame([{
                "targa": targa_input,
                "vecchio_operatore": vecchio_op,
                "nuovo_operatore": nuovo_operatore,
                "inizio_assegnazione": data_inizio,
                "fine_assegnazione": data_cambio
            }])
            df_finale_st = pd.concat([df_st, nuovo_log], ignore_index=True)
            conn.update(worksheet="storico", data=df_finale_st)

            st.success(f"✅ Database aggiornato! {targa_input} assegnata a {nuovo_operatore}")
            st.balloons()
            st.rerun()
        else:
            st.error(f"❌ Targa {targa_input} non trovata.")
    else:
        st.error("❌ Errore: Colonna 'targa' non trovata nel foglio Google.")

# --- INTERFACCIA UTENTE ---
try:
    df_flotta = get_data("flotta")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("📝 Registra Cambio")
        with st.form("form_aggiornamento"):
            targa_f = st.text_input("Targa Veicolo").upper()
            nuovo_f = st.text_input("Nuovo Operatore").upper()
            submit = st.form_submit_button("Salva su Cloud")
            
            if submit:
                if targa_f and nuovo_f:
                    registra_riassegnazione(targa_f, nuovo_f)
                else:
                    st.warning("Inserisci sia la targa che il nuovo operatore.")

    with col2:
        st.subheader("📊 Stato Attuale Flotta")
        st.dataframe(df_flotta, use_container_width=True, hide_index=True)

    st.divider()

    # --- SEZIONE STORICO E DOWNLOAD ---
    st.subheader("📜 Storico Permanente e Download")
    df_storico = get_data("storico")

    if not df_storico.empty:
        st.dataframe(df_storico.sort_index(ascending=False), use_container_width=True, hide_index=True)
        
        # LOGICA DI DOWNLOAD EXCEL
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df_flotta.to_excel(writer, index=False, sheet_name='Stato_Attuale')
            df_storico.to_excel(writer, index=False, sheet_name='Storico_Cambi')
        
        st.download_button(
            label="📥 Scarica Database Excel",
            data=buffer.getvalue(),
            file_name=f"report_flotta_{datetime.now().strftime('%d_%m_%Y')}.xlsx",
            mime="application/vnd.ms-excel"
        )
    else:
        st.info("Lo storico è attualmente vuoto.")

except Exception as e:
    st.error("⚠️ Errore di connessione al database.")
    st.info("Controlla che l'URL nelle Secrets sia corretto e che il foglio sia condiviso come Editor.")
