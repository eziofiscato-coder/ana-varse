import streamlit as st
import pandas as pd
from io import BytesIO
import hashlib

st.set_page_config(page_title="ANA Varese", layout="wide")

if "popup" not in st.session_state:
    st.session_state.popup = False
if "auth" not in st.session_state:
    st.session_state.auth = False
if "dati" not in st.session_state:
    st.session_state.dati = []
if "menu" not in st.session_state:
    st.session_state.menu = "Dashboard"

def hpwd(p):
    return hashlib.sha256(p.encode()).hexdigest()

def hdr():
    a,b = st.columns([1,5])
    with a:
        try:
            st.image("logo.png", width=120)
        except:
            st.write("ANA")
    with b:
        st.markdown("<div style='background:#0e7a3d; padding:10px; border-radius:8px; color:white; text-align:center; font-weight:bold;'>NUCLEO DI VOLONTARI DI PROTEZIONE CIVILE<br>ANA SEZIONE DI VARESE</div>", unsafe_allow_html=True)

# PRIMA PAGINA - COPERTINA CENTRATA
if not st.session_state.popup:
    hdr()
    st.write("")
    c1,c2,c3 = st.columns([1,2,1])
    with c2:
        try:
            st.image("copertina.png", width=400)
        except:
            try:
                st.image("logo.png", width=250)
            except:
                st.write("Carica copertina.png")
    st.markdown("<h2 style='text-align:center; color:#0e7a3d;'>VOLONTARIATO Sezione di Varese</h2>", unsafe_allow_html=True)
    c1,c2,c3 = st.columns([1,1,1])
    with c2:
        if st.button("ENTRA", use_container_width=True):
            st.session_state.popup = True
            st.rerun()
    st.stop()

# SECONDA PAGINA - LOGIN
if not st.session_state.auth:
    hdr()
    st.write("")
    c1,c2,c3 = st.columns([1,2,1])
    with c2:
        st.markdown("<div style='background:#e8f5e9; padding:15px; border-radius:10px; border:2px solid #0e7a3d;'><h3 style='color:#0e7a3d; text-align:center;'>LOGIN</h3></div>", unsafe_allow_html=True)
        with st.form("login"):
            u = st.text_input("User", value="admin")
            p = st.text_input("Password", type="password", value="ana2024")
            ok = st.form_submit_button("ACCEDI", use_container_width=True)
            if ok:
                if u == "admin" and hpwd(p) == hpwd("ana2024"):
                    st.session_state.auth = True
                    st.session_state.menu = "Dashboard"
                    st.rerun()
                else:
                    st.error("User o password errati")
        if st.button("⬅️ TORNA A COPERTINA"):
            st.session_state.popup = False
            st.rerun()
    st.stop()

# TERZA PAGINA - DASHBOARD DOPO LOGIN
hdr()

with st.sidebar:
    st.markdown("<div style='background:#0e7a3d; padding:8px; border-radius:8px; color:white; text-align:center;'><b>MENU</b></div>", unsafe_allow_html=True)
    opts = ['Dashboard','Volontari','Mappe Posizioni','Eventi','Backup','Logout']
    sel = st.radio('Menu', opts, index=0)
    if sel == 'Logout':
        st.session_state.auth = False
        st.session_state.popup = False
        st.rerun()
    st.session_state.menu = sel

sc = st.session_state.menu

if sc == 'Dashboard':
    st.markdown("<div style='background:#e8f5e9; padding:15px; border-radius:10px; border:2px solid #0e7a3d;'><h2 style='color:#0e7a3d;'>Dashboard ANA</h2></div>", unsafe_allow_html=True)
    c1,c2,c3,c4 = st.columns(4)
    with c1:
        if st.button('VOLONTARI', use_container_width=True):
            st.session_state.menu = 'Volontari'
            st.rerun()
    with c2:
        if st.button('BACKUP', use_container_width=True):
            st.session_state.menu = 'Backup'
            st.rerun()
    with c3:
        st.metric('Volontari', len(st.session_state.dati))
    with c4:
        if st.button("LOGOUT", use_container_width=True):
            st.session_state.auth = False
            st.session_state.popup = False
            st.rerun()

elif sc == 'Volontari':
    if st.button('⬅️ TORNA DASHBOARD'):
        st.session_state.menu = 'Dashboard'
        st.rerun()
    st.markdown("<h2 style='text-align:center; color:#0e7a3d;'>VOLONTARIATO</h2>", unsafe_allow_html=True)
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
        st.dataframe(df, use_container_width=True, hide_index=True)

elif sc == 'Backup':
    if st.button('⬅️ TORNA DASHBOARD'):
        st.session_state.menu = 'Dashboard'
        st.rerun()
    st.markdown("<h3>Backup</h3>", unsafe_allow_html=True)
    if st.session_state.dati:
        df = pd.DataFrame(st.session_state.dati)
        st.dataframe(df, use_container_width=True, hide_index=True)
        output = BytesIO()
        df.to_excel(output, index=False, engine="openpyxl")
        st.download_button("📥 Scarica Excel", output.getvalue(), file_name="associazioni.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
    else:
        st.info("Nessun volontario")
