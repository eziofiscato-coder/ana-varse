import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="ANA Varese", layout="centered")

try:
    st.image("logo.png", width=250)
except:
    st.info("Carica logo.png su GitHub - l'app funziona anche senza!")

st.markdown("<h2 style='text-align:center; color:#0e7a3d;'>VOLONTARIATO<br>Sezione di Varese</h2>", unsafe_allow_html=True)

if "dati" not in st.session_state:
    st.session_state.dati = []

with st.form("form"):
    nome = st.text_input("Nome e Cognome *")
    assoc = st.text_input("Associazione *")
    cell = st.text_input("Cellulare *")
    ruolo = st.selectbox("Ruolo *", ["Volontario", "Caposquadra", "Coordinatore", "Autista", "Radio", "Logistica", "Segreteria", "Sanitario", "Altro"])
    submitted = st.form_submit_button("✅ Salva", use_container_width=True)
    if submitted:
        if nome and assoc and cell:
            st.session_state.dati.append({"Nome": nome, "Associazione": assoc, "Cellulare": cell, "Ruolo": ruolo})
            st.success(f"Aggiunto {nome}")
        else:
            st.error("Compila i campi *")

if st.session_state.dati:
    df = pd.DataFrame(st.session_state.dati)
    st.divider()
    st.dataframe(df, use_container_width=True, hide_index=True)
    try:
        output = BytesIO()
        df.to_excel(output, index=False, engine="openpyxl")
        st.download_button("📥 Scarica Excel", output.getvalue(), file_name="associazioni.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
    except:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Scarica CSV", csv, file_name="associazioni.csv", mime="text/csv", use_container_width=True)
