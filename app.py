import streamlit as st
import pandas as pd
import os
from datetime import datetime
from PIL import Image

FILE_EXCEL = "associazioni.xlsx"
st.set_page_config(page_title="Registro Associazioni", page_icon="📋", layout="centered")

# --- LOGO ---
# Metti il tuo file logo.png nella stessa cartella, oppure caricalo da qui
logo_path = "logo.png"
if os.path.exists(logo_path):
    st.image(logo_path, width=200)
else:
    uploaded_logo = st.sidebar.file_uploader("Carica Logo (opzionale)", type=["png","jpg","jpeg"])
    if uploaded_logo:
        st.image(uploaded_logo, width=200)
        # salva per dopo
        with open("logo.png","wb") as f:
            f.write(uploaded_logo.getbuffer())

st.title("Registro Associazioni")

# Inizializza Excel se non esiste
if not os.path.exists(FILE_EXCEL):
    df_init = pd.DataFrame(columns=["Data","Nome e Cognome","Associazione","Cellulare"])
    df_init.to_excel(FILE_EXCEL, index=False)

with st.form("form"):
    nome = st.text_input("Nome e Cognome *")
    associazione = st.text_input("Associazione *")
    cellulare = st.text_input("Cellulare *")
    submitted = st.form_submit_button("SALVA SU EXCEL", use_container_width=True)

    if submitted:
        if not nome or not associazione or not cellulare:
            st.error("Compila tutti i campi!")
        else:
            # Aggiungi riga
            df = pd.read_excel(FILE_EXCEL) if os.path.getsize(FILE_EXCEL) > 0 else pd.DataFrame(columns=["Data","Nome e Cognome","Associazione","Cellulare"])
            nuova_riga = {
                "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "Nome e Cognome": nome,
                "Associazione": associazione,
                "Cellulare": cellulare
            }
            df = pd.concat([df, pd.DataFrame([nuova_riga])], ignore_index=True)
            df.to_excel(FILE_EXCEL, index=False)
            st.success(f"Salvato {nome}!")
            st.balloons()

# Mostra tabella e download
if os.path.exists(FILE_EXCEL):
    df = pd.read_excel(FILE_EXCEL)
    st.subheader(f"Iscritti: {len(df)}")
    st.dataframe(df, use_container_width=True)
    with open(FILE_EXCEL, "rb") as f:
        st.download_button("📥 Scarica Excel", f, file_name="associazioni.xlsx", use_container_width=True)
