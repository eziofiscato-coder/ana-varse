import streamlit as st
import pandas as pd
from datetime import date, datetime
from io import BytesIO
import os
import uuid
import json
import requests

st.set_page_config(page_title="ANA Varese", page_icon="🟢", layout="wide")

st.markdown("""
<style>
.stApp{background-color:#e8f5e9!important;}
.main.block-container{background-color:white!important;border-radius:18px;padding:25px!important;}
[data-testid="stSidebar"]{background-color:#a5d6a7!important;border-right:4px solid #2e7d32!important;}
.stForm{background-color:#c8e6c9!important;border:3px solid #2e7d32!important;border-radius:15px!important;}
.stButton>button{background-color:#2e7d32!important;color:white!important;font-weight:bold!important;min-height:45px!important;}
.vol-selected{background-color:#fff3e0;border:3px solid #ef6c00;border-radius:12px;padding:20px;margin:15px 0;}
.submask{background-color:#f1f8e9;border:2px solid #2e7d32;border-radius:12px;padding:15px;margin:10px 0;}
</style>
""", unsafe_allow_html=True)

def load_json(f, default):
    try:
        if os.path.exists(f):
            with open(f, "r", encoding="utf-8") as fh:
                d = json.load(fh)
                if isinstance(d, list) or isinstance(d, dict):
                    return d
    except:
        pass
    return default

def save_json(f, d):
    try:
        with open(f, "w", encoding="utf-8") as fh:
            json.dump(d, fh, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"Errore {f}: {e}")

FILE_DATI = "dati_volontari.json"
FILE_POST = "postazioni.json"
FILE_EMER = "emergenze.json"
FILE_RADIO = "radio_db.json"
FILE_DIST = "dist_radio.json"
FILE_EVENTI = "eventi.json"
FILE_CHECK = "checkin.json"
FILE_NOMI = "mem_nomi.json"
FILE_DETTAGLI = "volontari_dettagli.json"

COMUNI_VARESE = ["Varese","Busto Arsizio","Gallarate","Saronno","Venegono Superiore","Venegono Inferiore","Castiglione Olona","Lozza","Gornate Olona","Vedano Olona","Tradate","Malnate"]
EMERGENCY_LOGOS = {
    "incendio_boschivo": {"nome": "Incendio Boschivo", "emoji": "🔥"},
    "frana": {"nome": "Frana", "emoji": "⛰️"},
    "caduta_albero": {"nome": "Caduta Albero", "emoji": "🌳"},
    "esondazione": {"nome": "Esondazione", "emoji": "🌊"},
    "vvff": {"nome": "VVFF", "emoji": "🚒"},
    "protezione_civile": {"nome": "Prot. Civile", "emoji": "🦺"},
    "ambulanza": {"nome": "Ambulanza", "emoji": "🚑"},
}

@st.cache_data(ttl=86400)
def load_comuni_italia():
    try:
        url = "https://raw.githubusercontent.com/matteocontrini/comuni-json/master/comuni.json"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return sorted([c["nome"] for c in r.json()])
    except:
        pass
    return COMUNI_VARESE

# INIT SESSION
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "dati" not in st.session_state:
    st.session_state.dati = load_json(FILE_DATI, [])
if "postazioni" not in st.session_state:
    st.session_state.postazioni = load_json(FILE_POST, [])
if "emergenze_lista" not in st.session_state:
    st.session_state.emergenze_lista = load_json(FILE_EMER, [])
if "radio_db" not in st.session_state:
    st.session_state.radio_db = load_json(FILE_RADIO, [])
if "dist_radio" not in st.session_state:
    st.session_state.dist_radio = load_json(FILE_DIST, [])
if "eventi_lista" not in st.session_state:
    st.session_state.eventi_lista = load_json(FILE_EVENTI, [])
if "checkin_lista" not in st.session_state:
    st.session_state.checkin_lista = load_json(FILE_CHECK, [])
if "mem_nomi" not in st.session_state:
    st.session_state.mem_nomi = load_json(FILE_NOMI, [])
if "vol_dettagli" not in st.session_state:
    st.session_state.vol_dettagli = load_json(FILE_DETTAGLI, {})
if "menu_scelta" not in st.session_state:
    st.session_state.menu_scelta = "Dashboard"
if "volontario_selezionato" not in st.session_state:
    st.session_state.volontario_selezionato = None
if "volontario_idx" not in st.session_state:
    st.session_state.volontario_idx = None
if "form_nome" not in st.session_state:
    st.session_state.form_nome = ""
if "form_cognome" not in st.session_state:
    st.session_state.form_cognome = ""
if "form_cell" not in st.session_state:
    st.session_state.form_cell = ""
if "form_comune" not in st.session_state:
    st.session_state.form_comune = "Varese"
if "form_ruolo" not in st.session_state:
    st.session_state.form_ruolo = "Volontario"
if "form_assoc" not in st.session_state:
    st.session_state.form_assoc = "ANA Varese"

def header_loghi():
    c1, c2, c3 = st.columns([1, 2, 1])
    if os.path.exists("logo.png"):
        c1.image("logo.png", width=90)
    c2.markdown("<h2 style='text-align:center; color:#0e7a3d;'>VOLONTARIATO<br>Sezione di Varese</h2>", unsafe_allow_html=True)
    if os.path.exists("logo_pc_lombardia.png"):
        c3.image("logo_pc_lombardia.png", width=90)

if not st.session_state.authenticated:
    header_loghi()
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        with st.form("login"):
            u = st.text_input("Username", value="admin")
            p = st.text_input("Password", type="password", value="ana2024")
            if st.form_submit_button("Accedi", use_container_width=True):
                if u == "admin" and p == "ana2024":
                    st.session_state.authenticated = True
                    st.rerun()
    st.stop()

header_loghi()
st.divider()

with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=80)
    opzioni = ["Dashboard","Volontari","Emergenze con Loghi","Mappa Postazioni","DB Radio","Distribuzione Radio","Eventi","Check-in","Tabella Interventi Emergenza","Backup"]
    sel = st.radio("MENU", opzioni, index=opzioni.index(st.session_state.menu_scelta) if st.session_state.menu_scelta in opzioni else 0)
    if sel!= st.session_state.menu_scelta:
        st.session_state.menu_scelta = sel
        st.rerun()
    if st.button("🚪 LOGOUT", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

scelta = st.session_state.menu_scelta
st.markdown(f"## {scelta}")
st.divider()
COMUNI_TUTTI = load_comuni_italia()
MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

# DASHBOARD
if scelta == "Dashboard":
    st.markdown("### ⚡ TASTI SCELTA RAPIDA")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("🚨\nNUOVA EMERGENZA", key="q_em", use_container_width=True):
            st.session_state.menu_scelta = "Emergenze con Loghi"
            st.rerun()
    with c2:
        if st.button("📍\nPOSTAZIONE", key="q_post", use_container_width=True):
            st.session_state.menu_scelta = "Mappa Postazioni"
            st.rerun()
    with c3:
        if st.button("👤\nVOLONTARIO", key="q_vol", use_container_width=True):
            st.session_state.menu_scelta = "Volontari"
            st.session_state.volontario_selezionato = None
            st.rerun()
    with c4:
        if st.button("💾\nBACKUP UNICO", key="q_back", use_container_width=True):
            st.session_state.menu_scelta = "Backup"
            st.rerun()
    st.divider()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🚨 Emergenze", len(st.session_state.emergenze_lista))
    c2.metric("📍 Postazioni", len(st.session_state.postazioni))
    c3.metric("👤 Volontari", len(st.session_state.dati))
    c4.metric("📻 Radio", len(st.session_state.radio_db))
    st.divider()
    st.markdown("### 👥 TABELLA VOLONTARI - CLICCA NOME PER CARICARE FORM")
    if st.session_state.dati:
        for idx, vol in enumerate(st.session_state.dati):
            c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
            with c1:
                if st.button(f"👤 {vol.get('Nome','')}", key=f"dash_vol_{idx}", use_container_width=True):
                    nome_completo = vol.get('Nome','')
                    parti = nome_completo.split(" ", 1)
                    st.session_state.form_nome = parti[0] if len(parti) > 0 else ""
                    st.session_state.form_cognome = parti[1] if len(parti) > 1 else ""
                    st.session_state.form_cell = vol.get('Cellulare','')
                    st.session_state.form_comune = vol.get('Comune','Varese')
                    st.session_state.form_ruolo = vol.get('Ruolo','Volontario')
                    st.session_state.form_assoc = vol.get('Associazione','ANA Varese')
                    st.session_state.volontario_selezionato = vol
                    st.session_state.volontario_idx = idx
                    st.session_state.menu_scelta = "Volontari"
                    st.rerun()
            with c2:
                st.write(vol.get('Cellulare',''))
            with c3:
                st.write(vol.get('Comune',''))
            with c4:
                st.write(vol.get('Ruolo',''))

# VOLONTARI
elif scelta == "Volontari":
    if st.button("🏠 Torna alla Dashboard", use_container_width=True):
        st.session_state.menu_scelta = "Dashboard"
        st.rerun()

    if st.session_state.volontario_selezionato is not None:
        vol = st.session_state.volontario_selezionato
        idx = st.session_state.volontario_idx
        vol_id = f"{vol.get('Nome','')}_{idx}"
        st.markdown('<div class="vol-selected">', unsafe_allow_html=True)
        st.markdown(f"### 👤 VOLONTARIO SELEZIONATO: {vol.get('Nome','')} - SOTTOMASCHERE")
        st.markdown("**Cliccato dalla tabella - Dati caricati nel form sotto!**")
        if st.button("❌ Chiudi dettaglio", key="chiudi_det"):
            st.session_state.volontario_selezionato = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📋 Anagrafica","📻 Radio","📅 Eventi","✅ Presenze","🚨 Emergenze","📄 Note"])

        with tab1:
            st.markdown('<div class="submask">', unsafe_allow_html=True)
            st.markdown("#### 📋 Sottomaschera 1 - Anagrafica Completa")
            with st.form("form_anagrafica"):
                nome_completo = vol.get('Nome','')
                parti = nome_completo.split(" ", 1)
                nome_init = parti[0] if len(parti) > 0 else ""
                cognome_init = parti[1] if len(parti) > 1 else ""
                c1, c2 = st.columns(2)
                with c1:
                    nome = st.text_input("Nome *", value=nome_init)
                    cognome = st.text_input("Cognome *", value=cognome_init)
                    cf = st.text_input("CF", value=st.session_state.vol_dettagli.get(vol_id, {}).get('CF',''))
                    email = st.text_input("Email", value=st.session_state.vol_dettagli.get(vol_id, {}).get('Email',''))
                with c2:
                    cell = st.text_input("Cellulare *", value=vol.get('Cellulare',''))
                    comune = st.selectbox("Comune", COMUNI_TUTTI, index=0)
                    ruolo = st.selectbox("Ruolo", ["Volontario","Caposquadra","Coordinatore","Autista","Radio","Logistica","Segreteria","Sanitario","Altro"], index=0)
                    assoc = st.text_input("Associazione", value=vol.get('Associazione','ANA Varese'))
                c3, c4, c5 = st.columns(3)
                with c3:
                    patente = st.selectbox("Patente", ["","B","C","D","BE","CE"])
                    scadenza = st.date_input("Scadenza Patente", value=date.today())
                with c4:
                    motosega = st.checkbox("Motosega")
                    idrovora = st.checkbox("Idrovora")
                with c5:
                    primo = st.checkbox("Primo Soccorso")
                    antinc = st.checkbox("Antincendio")
                if st.form_submit_button("💾 SALVA ANAGRAFICA", use_container_width=True, type="primary"):
                    nome_new = f"{nome} {cognome}"
                    st.session_state.dati[idx] = {"Nome": nome_new, "Cellulare": cell, "Comune": comune, "Ruolo": ruolo, "Associazione": assoc}
                    if vol_id not in st.session_state.vol_dettagli:
                        st.session_state.vol_dettagli[vol_id] = {}
                    st.session_state.vol_dettagli[vol_id].update({'CF': cf, 'Email': email, 'Patente': patente, 'Motosega': motosega})
                    save_json(FILE_DATI, st.session_state.dati)
                    save_json(FILE_DETTAGLI, st.session_state.vol_dettagli)
                    st.session_state.form_nome = nome
                    st.session_state.form_cognome = cognome
                    st.session_state.form_cell = cell
                    st.session_state.form_comune = comune
                    st.session_state.form_ruolo = ruolo
                    st.session_state.form_assoc = assoc
                    st.session_state.volontario_selezionato = st.session_state.dati[idx]
                    st.success("✅ Salvato!")
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        with tab2:
            st.markdown('<div class="submask">', unsafe_allow_html=True)
            st.markdown("#### 📻 Sottomaschera 2 - Radio Assegnate")
            radio_vol = [r for r in st.session_state.dist_radio if r.get('Volontario','') == vol.get('Nome','')]
            if radio_vol:
                st.dataframe(pd.DataFrame(radio_vol), use_container_width=True)
            else:
                st.info("Nessuna radio")
            with st.form("form_radio"):
                if st.session_state.radio_db:
                    radio_disp = [f"{r.get('Marca','')} {r.get('Modello','')}" for r in st.session_state.radio_db]
                    sel = st.selectbox("Radio", radio_disp)
                    if st.form_submit_button("📻 ASSEGNA", use_container_width=True):
                        new = {"ID": str(uuid.uuid4())[:8], "Volontario": vol.get('Nome',''), "Radio": sel, "Data": str(date.today())}
                        st.session_state.dist_radio.append(new)
                        save_json(FILE_DIST, st.session_state.dist_radio)
                        st.success("Assegnata!")
                        st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        with tab3:
            st.markdown('<div class="submask">', unsafe_allow_html=True)
            st.markdown("#### 📅 Eventi")
            if st.session_state.eventi_lista:
                st.dataframe(pd.DataFrame(st.session_state.eventi_lista), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with tab4:
            st.markdown('<div class="submask">', unsafe_allow_html=True)
            st.markdown("#### ✅ Presenze")
            check_vol = [c for c in st.session_state.checkin_lista if c.get('Volontario','') == vol.get('Nome','')]
            if check_vol:
                st.dataframe(pd.DataFrame(check_vol), use_container_width=True)
            with st.form("form_check"):
                luogo = st.selectbox("Luogo", COMUNI_TUTTI)
                ore = st.number_input("Ore", min_value=0.5, max_value=24.0, value=4.0, step=0.5)
                if st.form_submit_button("✅ REGISTRA", use_container_width=True, type="primary"):
                    new = {"ID": str(uuid.uuid4())[:8], "Volontario": vol.get('Nome',''), "Luogo": luogo, "Ore": ore, "Data": str(date.today())}
                    st.session_state.checkin_lista.append(new)
                    save_json(FILE_CHECK, st.session_state.checkin_lista)
                    st.success("Registrato!")
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        with tab5:
            st.markdown('<div class="submask">', unsafe_allow_html=True)
            st.markdown("#### 🚨 Emergenze")
            if st.session_state.emergenze_lista:
                st.dataframe(pd.DataFrame(st.session_state.emergenze_lista), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with tab6:
            st.markdown('<div class="submask">', unsafe_allow_html=True)
            st.markdown("#### 📄 Note")
            note = st.text_area("Note", value=st.session_state.vol_dettagli.get(vol_id, {}).get('Note',''))
            if st.button("💾 Salva Note", use_container_width=True):
                if vol_id not in st.session_state.vol_dettagli:
                    st.session_state.vol_dettagli[vol_id] = {}
                st.session_state.vol_dettagli[vol_id]['Note'] = note
                save_json(FILE_DETTAGLI, st.session_state.vol_dettagli)
                st.success("Salvate!")
            if st.button(f"🗑️ ELIMINA {vol.get('Nome','')}", use_container_width=True):
                st.session_state.dati.pop(idx)
                save_json(FILE_DATI, st.session_state.dati)
                st.session_state.volontario_selezionato =