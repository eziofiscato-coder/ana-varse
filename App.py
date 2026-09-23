
import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="ANA Varese - TEST CLOUD", layout="wide", page_icon="🛡️")

# Init minimale
if "logged" not in st.session_state:
    st.session_state.logged = False
if "page" not in st.session_state:
    st.session_state.page = "entra"
if "menu" not in st.session_state:
    st.session_state.menu = "Dashboard"
if "volontari" not in st.session_state:
    st.session_state.volontari = []
if "vol_edit_index" not in st.session_state:
    st.session_state.vol_edit_index = None
if "patch_df" not in st.session_state:
    st.session_state.patch_df = None

COMUNI = ["Varese", "Venegono Superiore", "Venegono Inferiore", "Tradate", "Malnate"]

def hdr_form(t):
    st.markdown(f"<h3 style='color:#1A5D1A'>{t}</h3>", unsafe_allow_html=True)

if st.session_state.page == "entra":
    st.title("ANA Varese - TEST CLOUD")
    st.success("App minimale per test Cloud - se vedi questo, Cloud funziona")
    if st.button("ENTRA"):
        st.session_state.page = "login"
        st.rerun()
    st.stop()

if st.session_state.page == "login":
    st.title("Login")
    u = st.text_input("Utente")
    p = st.text_input("Password", type="password")
    if st.button("Accedi"):
        if u=="admin" and p=="ana2024":
            st.session_state.logged=True
            st.session_state.page="dashboard"
            st.rerun()
        else:
            st.error("admin / ana2024")
    st.stop()

if not st.session_state.logged:
    st.session_state.page="login"
    st.rerun()

with st.sidebar:
    st.markdown("### MENU TEST")
    cur = st.radio("Vai a", ["Dashboard", "Volontari (con foto)"], index=0, key="menu_radio_test")
    st.session_state.menu = cur
    if st.button("Logout"):
        st.session_state.logged=False
        st.session_state.page="entra"
        st.rerun()
    
    with st.expander("PATCH TEST", expanded=False):
        st.info("Patch solo in memoria")
        up = st.file_uploader("CSV comune,via", type=["csv"], key="up_patch_test")
        if up:
            try:
                df = pd.read_csv(up, dtype=str)
                st.session_state.patch_df = df
                st.success(f"Caricato {len(df)} righe")
            except Exception as e:
                st.error(str(e))

if cur == "Dashboard":
    hdr_form("Dashboard - TEST")
    st.success("Se vedi questa dashboard, il fix cloud ha funzionato!")
    st.write(f"Volontari: {len(st.session_state.volontari)}")
    if st.button("👤 Vai a Volontari"):
        st.session_state.menu = "Volontari (con foto)"
        st.rerun()
    if st.button("⛶ Test Fullscreen"):
        st.toast("Premi ESC per uscire - fullscreen JS")

elif cur == "Volontari (con foto)":
    hdr_form("VOLONTARI - 6 linguette TEST")
    edit_mode = st.session_state.vol_edit_index is not None
    edit_data = st.session_state.volontari[st.session_state.vol_edit_index] if edit_mode else {}

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📋 Anagrafica","📞 Contatti","🛡️ Ruolo","📻 Dotazione","📄 Doc","📸 Foto"])
    
    with tab1:
        nome = st.text_input("Nome *", value=edit_data.get("Nome",""), key="v_nome")
        cognome = st.text_input("Cognome *", value=edit_data.get("Cognome",""), key="v_cogn")
        comune = st.selectbox("Comune", COMUNI, key="v_com")
    with tab2:
        cell = st.text_input("Cellulare *", value=edit_data.get("Cellulare",""), key="v_cell")
        email = st.text_input("Email", value=edit_data.get("Email",""), key="v_mail")
    with tab3:
        ruolo = st.selectbox("Ruolo", ["Volontario","Capo Squadra","Coordinatore"], key="v_ruolo")
        squadra = st.selectbox("Squadra", ["Squadra A","Squadra B"], key="v_squad")
    with tab4:
        radio_id = st.text_input("ID Radio", key="v_radio")
    with tab5:
        note = st.text_area("Note", key="v_note")
    with tab6:
        foto = st.file_uploader("Foto", type=["jpg","png"], key="v_foto")

    if st.button("💾 SALVA VOLONTARIO TEST"):
        if nome and cognome and cell:
            nuovo = {"Nome":nome,"Cognome":cognome,"Comune":comune,"Cellulare":cell,"Email":email,"Ruolo":ruolo,"Squadra":squadra,"Data":datetime.now().strftime("%d/%m/%Y")}
            st.session_state.volontari.append(nuovo)
            st.success("Salvato!")
            st.rerun()
        else:
            st.error("Compila Nome, Cognome, Cellulare")

    if st.session_state.volontari:
        st.divider()
        for i,v in enumerate(st.session_state.volontari):
            st.write(f"{i+1}. {v['Cognome']} {v['Nome']} - {v['Comune']} - {v['Cellulare']}")

st.divider()
st.caption("TEST CLOUD OK - Ezio")
