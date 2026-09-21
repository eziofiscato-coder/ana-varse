import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="ANA Varese", layout="centered")

# INTESTAZIONE VERDE COME PRIMA - RIGA 7-8
st.markdown("<div style='background:#0e7a3d; padding:12px; border-radius:8px; color:white; text-align:center; font-weight:bold; font-size:16px;'>NUCLEO DI VOLONTARI DI PROTEZIONE CIVILE<br>ANA SEZIONE DI VARESE</div>", unsafe_allow_html=True)

st.write("")

# COPERTINA AL CENTRO 700px - RIGA 12-17
c1,c2,c3 = st.columns([1,2,1])
with c2:
    try:
        st.image("copertina.png", width=700)
    except:
        try:
            st.image("logo.png", width=250)
        except:
            st.write("Carica copertina.png")

# TITOLO VOLONTARIATO - RIGA 20
st.markdown("<h2 style='text-align:center; color:#0e7a3d; font-family:\"Times New Roman\", Times, serif; font-weight:bold; font-size:32px;'>VOLONTARIATO<br>Sezione di Varese</h2>", unsafe_allow_html=True)

if "dati" not in st.session_state:
    st.session_state.dati = []

with st.form("form"):
    nome = st.text_input("Nome e Cognome *")
    assoc = st.text_input("Associazione *")
    cell = st.text_input("Cellulare *")
    ruolo = st.selectbox("Ruolo *", ["Volontario", "Caposquadra", "Coordinatore", "Autista", "Radio", "Telecomunicazioni", "Logistica", "Segreteria", "Sanitario", "Altro"])
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
    output = BytesIO()
    df.to_excel(output, index=False, engine="openpyxl")
    st.download_button("📥 Scarica Excel", output.getvalue(), file_name="associazioni.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)