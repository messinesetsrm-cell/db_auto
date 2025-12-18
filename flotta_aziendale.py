import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Configurazione nomi file come da tuoi screenshot
FILE_PRINCIPALE = "flotta.xlsx"
FILE_STORICO = "storico_assegnazioni.xlsx"

# --- LOGICA DI AGGIORNAMENTO (Il Motore) ---
def registra_cambio_operatore(targa_input, nuovo_op_nome):
    try:
        # Carica il database principale
        df_p = pd.read_excel(FILE_PRINCIPALE)
        
        # NORMALIZZAZIONE: Trasformiamo i nomi colonne in minuscolo per la logica interna
        # Questo evita gli errori 'KeyError: Targa'
        df_p.columns = df_p.columns.str.strip().str.lower()
        
        targa_cercata = targa_input.strip().lower()

        # Controlliamo se la targa esiste
        if targa_cercata in df_p['targa'].astype(str).str.lower().values:
            # Troviamo la riga specifica
            idx = df_p.index[df_p['targa'].astype(str).str.lower() == targa_cercata][0]
            
            # Recupero dati per lo storico
            vecchio_op = df_p.at[idx, 'operatore']
            data_inizio_originale = df_p.at[idx, 'data_assegnazione']
            data_oggi = datetime.now().strftime("%Y-%m-%d")

            # Calcolo giorni di utilizzo
            try:
                inizio_dt = pd.to_datetime(data_inizio_originale)
                giorni = (datetime.now() - inizio_dt).days
            except:
                giorni = "N/D"

            # 1. Creazione e salvataggio dello Storico
            nuova_riga_st = {
                "Targa": [targa_input.upper()],
                "Operatore": [vecchio_op],
                "Inizio_Assegnazione": [data_inizio_originale],
                "Fine_Assegnazione": [data_oggi],
                "Giorni_Utilizzo": [giorni],
                "Tipo_Vettura": ["N/D"] # Colonna non presente nel file principale
            }
            df_nuovo_st = pd.DataFrame(nuova_riga_st)

            if os.path.exists(FILE_STORICO):
                df_st_vecchio = pd.read_excel(FILE_STORICO)
                df_st_finale = pd.concat([df_st_vecchio, df_nuovo_st], ignore_index=True)
            else:
                df_st_finale = df_nuovo_st
            
            df_st_finale.to_excel(FILE_STORICO, index=False)

            # 2. Aggiornamento file principale
            df_p.at[idx, 'operatore'] = nuovo_op_nome.upper()
            df_p.at[idx, 'data_assegnazione'] = data_oggi

            # Ripristiniamo i nomi colonne originali per il salvataggio
            df_p.columns = ['Operatore', 'Targa', 'Data_Assegnazione']
            df_p.to_excel(FILE_PRINCIPALE, index=False)
            
            return True
