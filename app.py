import streamlit as st
import pandas as pd
from io import BytesIO
import os
from datetime import datetime

st.set_page_config(page_title="ANA Varese", layout="centered")

# --- FOTO DI IERI copertina.png - GRANDE ---
try:
    if os.path.exists("copertina.png"):
        st.image("copertina.png", width=450)
    elif os.path.exists("logo.png"):
        st.image("logo.png", width=350)
    else:
        st.write("ANA")
except:
    st.warning("Carica copertina.png su GitHub!")

# --- INTESTAZIONE Times New Roman + BOLD + GRANDE ---
st.markdown("<h2 style='text-align:center; color:#0e7a3d; font-family:\"Times New Roman\", Times, serif; font-weight:bold; font-size:50px;'>VOLONTARIATO<br>Sezione di Varese</h2>", unsafe_allow_html=True)

if "dati" not in st.session_state:
    st.session_state.dati = []

with st.form("form"):
    nome = st.text_input("Nome e Cognome *")
    assoc = st.text_input("Associazione *")
    cell = st.text_input("Cellulare *")
    ruolo = st.selectbox("Ruolo *", ["Volontario", "Caposquadra", "Coordinatore", "Autista", "Radio", "Telecomunicazioni", "Logistica", "Segreteria", "Sanitario", "Altro"])
    # DATA in GG/MM/ANNO
    data = st.date_input("Data *", value=datetime.now().date(), format="DD/MM/YYYY")
    submitted = st.form_submit_button("✅ Salva", use_container_width=True)
    if submitted:
        if nome and assoc and cell:
            data_str = data.strftime("%d/%m/%Y")
            st.session_state.dati.append({"Nome": nome, "Associazione": assoc, "Cellulare": cell, "Ruolo": ruolo, "Data": data_str})
            st.success(f"Aggiunto {nome} - {data_str}")
        else:
            st.error("Compila i campi *")

if st.session_state.dati:
    df = pd.DataFrame(st.session_state.dati)
    st.divider()
    st.dataframe(df, use_container_width=True, hide_index=True)
    output = BytesIO()
    df.to_excel(output, index=False, engine="openpyxl")
    st.download_button("📥 Scarica Excel", output.getvalue(), file_name="associazioni.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)