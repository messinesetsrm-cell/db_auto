import pandas as pd
from datetime import datetime

FILE_PRINCIPALE = "flotta.xlsx"
FILE_STORICO = "storico_assegnazioni.xlsx"

def aggiorna_database_e_storico(targa_target, nuovo_op):
    # 1. Caricamento file con gestione errore
    try:
        df_p = pd.read_excel(FILE_PRINCIPALE)
    except FileNotFoundError:
        print("Errore: File flotta.xlsx non trovato!")
        return

    # Pulizia nomi colonne
    df_p.columns = df_p.columns.str.strip()

    if targa_target in df_p['Targa'].values:
        # Identifichiamo la riga
        idx = df_p.index[df_p['Targa'] == targa_target][0]
        
        # 2. Recupero dati per lo Storico
        vecchio_op = df_p.at[idx, 'Operatore']
        data_inizio_str = str(df_p.at[idx, 'Data_Assegnazione'])
        
        # Gestione date per il calcolo dei giorni
        try:
            data_inizio = pd.to_datetime(data_inizio_str)
            oggi = datetime.now()
            giorni_possesso = (oggi - data_inizio).days
        except:
            giorni_possesso = "N/D"
            data_inizio = data_inizio_str

        # 3. Aggiornamento dello Storico
        nuova_riga_st = {
            "Targa": [targa_target],
            "Operatore": [vecchio_op],
            "Inizio_Assegnazione": [data_inizio],
            "Fine_Assegnazione": [datetime.now().strftime("%Y-%m-%d")],
            "Giorni_Utilizzo": [giorni_possesso],
            "Tipo_Vettura": ["N/D"] # Colonna non presente nel file principale
        }
        df_new_st = pd.DataFrame(nuova_riga_st)

        try:
            df_st_esistente = pd.read_excel(FILE_STORICO)
            df_finale_st = pd.concat([df_st_esistente, df_new_st], ignore_index=True)
        except:
            df_finale_st = df_new_st

        # SALVATAGGIO FISICO STORICO
        df_finale_st.to_excel(FILE_STORICO, index=False)

        # 4. Aggiornamento del Database Principale
        df_p.at[idx, 'Operatore'] = nuovo_op.upper()
        df_p.at[idx, 'Data_Assegnazione'] = datetime.now().strftime("%Y-%m-%d")

        # SALVATAGGIO FISICO PRINCIPALE (Questo rende la modifica permanente)
        df_p.to_excel(FILE_PRINCIPALE, index=False)
        
        return f"✅ {targa_target} riassegnata. Vecchio operatore: {vecchio_op} ({giorni_possesso} giorni)"
    else:
        return "❌ Targa non trovata."

# Esempio di chiamata (collegalo al tuo pulsante "Applica Modifica")
# risultato = aggiorna_database_e_storico(targa_inserita, nome_inserito)
