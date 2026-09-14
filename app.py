import streamlit as st
import pandas as pd
from io import BytesIO
import os

st.set_page_config(page_title="ANA Varese", layout="centered")

try:
    st.image("logo.png", width=250)
except:
    pass

st.markdown("<h2 style='text-align:center; color:#0e7a3d;'>VOLONTARIATO<br>Sezione di Varese</h2>", unsafe_allow_html=True)

FILE_DATI = "dati_iscritti.csv"

# CARICA DATI SALVATI SE ESISTONO
if "dati" not in st.session_state:
    if os.path.exists(FILE_DATI):
        try:
            df_load = pd.read_csv(FILE_DATI)
            st.session_state.dati = df_load.to_dict(orient="records")
        except:
            st.session_state.dati = []
    else:
        st.session_state.dati = []

def salva_su_disco():
    if st.session_state.dati:
        df = pd.DataFrame(st.session_state.dati)
        df.to_csv(FILE_DATI, index=False)

with st.form("form"):
    nome = st.text_input("Nome e Cognome *")
    assoc = st.text_input("Associazione *")
    cell = st.text_input("Cellulare *")
    ruolo = st.selectbox("Ruolo *", ["Volontario", "Caposquadra", "Coordinatore", "Autista", "Radio", "Telecomunicazioni", "Logistica", "Segreteria", "Sanitario", "Altro"])
    submitted = st.form_submit_button("✅ Salva", use_container_width=True)
    if submitted:
        if nome and assoc and cell:
            st.session_state.dati.append({"Nome": nome, "Associazione": assoc, "Cellulare": cell, "Ruolo": ruolo})
            salva_su_disco()
            st.success(f"Aggiunto {nome} - dati salvati!")
        else:
            st.error("Compila i campi *")

if st.session_state.dati:
    df = pd.DataFrame(st.session_state.dati)
    st.divider()
    st.write(f"**Totale iscritti: {len(df)}** - Dati tenuti in memoria")
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    col1, col2 = st.columns(2)
    with col1:
        output = BytesIO()
        df.to_excel(output, index=False, engine="openpyxl")
        st.download_button("📥 Scarica Excel", output.getvalue(), file_name="associazioni.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
    with col2:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Scarica CSV", csv, file_name="associazioni.csv", mime="text/csv", use_container_width=True)
    
    if st.button("🗑️ Svuota TUTTO (cancella memoria)", use_container_width=True):
        st.session_state.dati = []
        if os.path.exists(FILE_DATI):
            os.remove(FILE_DATI)
        st.rerun()
else:
    st.info("Nessun iscritto ancora. I dati verranno tenuti in memoria automaticamente.")
