import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="ANA Varese", layout="centered")

if "popup" not in st.session_state:
    st.session_state.popup = False
if "dati" not in st.session_state:
    st.session_state.dati = []

# FUNZIONE LOGO PICCOLO PC ANA - RIGA 13-24
def hdr():
    a,b = st.columns([1,5])
    with a:
        try:
            st.image("logo.png", width=120)  # LOGO PICCOLO PC ANA
        except:
            st.write("ANA")
    with b:
        st.markdown("<div style='background:#0e7a3d; padding:10px; border-radius:8px; color:white; text-align:center; font-weight:bold;'>NUCLEO DI VOLONTARI DI PROTEZIONE CIVILE<br>ANA SEZIONE DI VARESE</div>", unsafe_allow_html=True)

# PRIMA PAGINA - RIGA 27-50
if not st.session_state.popup:
    hdr()  # LOGO PICCOLO + INTESTAZIONE
    st.write("")
    # COPERTINA AL CENTRO
    c1,c2,c3 = st.columns([1,2,1])
    with c2:
        try:
            st.image("copertina.png", width=700)
        except:
            st.warning("Carica copertina.png")
    
    st.markdown("<h2 style='text-align:center; color:#0e7a3d; font-family:'Times New Roman', Times, serif; font-weight:bold;'>VOLONTARIATO<br>Sezione di Varese</h2>", unsafe_allow_html=True)
    
    c1,c2,c3 = st.columns([1,1,1])
    with c2:
        if st.button("ENTRA", use_container_width=True):
            st.session_state.popup = True
            st.rerun()
    st.stop()

# SECONDA PAGINA DOPO ENTRA - CON LOGO PICCOLO
hdr()

if st.button("⬅️ TORNA INDIETRO"):
    st.session_state.popup = False
    st.rerun()

st.markdown("<h2 style='text-align:center; color:#0e7a3d;'>VOLONTARIATO<br>Sezione di Varese</h2>", unsafe_allow_html=True)

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