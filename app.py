import streamlit as st
import pandas as pd
from datetime import date, datetime
from io import BytesIO
import os, uuid, requests, json

st.set_page_config(page_title="ANA Varese", page_icon="🟢", layout="wide")

st.markdown("""
<style>
.stApp{background-color:#e8f5e9!important;}
.main.block-container{background-color:white!important;border-radius:18px;padding:25px!important;}
[data-testid="stSidebar"]{background-color:#a5d6a7!important;border-right:4px solid #2e7d32!important;}
.stForm{background-color:#c8e6c9!important;border:3px solid #2e7d32!important;border-radius:15px!important;}
.stButton>button{background-color:#2e7d32!important;color:white!important;font-weight:bold!important;min-height:50px!important;}
div[data-testid="stFormSubmitButton"]>button{background-color:#d32f2f!important;}
.torna-btn>button{background-color:#1565c0!important;}
.quick-btn>button{background-color:#ff9800!important;border:2px solid #e65100!important;min-height:80px!important;}
.quick-btn-green>button{background-color:#2e7d32!important;min-height:80px!important;}
.quick-btn-red>button{background-color:#c62828!important;min-height:80px!important;}
.quick-btn-blue>button{background-color:#1565c0!important;min-height:80px!important;}
.vol-selected{background-color:#fff3e0;border:3px solid #ef6c00;border-radius:12px;padding:20px;margin:15px 0;}
.submask{background-color:#f1f8e9;border:2px solid #2e7d32;border-radius:12px;padding:15px;margin:10px 0;}
</style>
""", unsafe_allow_html=True)

def load_json(f, default):
    try:
        if os.path.exists(f):
            with open(f,"r",encoding="utf-8") as fh:
                d=json.load(fh)
                if isinstance(d,list) or isinstance(d,dict): return d
    except: pass
    return default

def save_json(f,d):
    try:
        with open(f,"w",encoding="utf-8") as fh: json.dump(d,fh,ensure_ascii=False,indent=2)
    except: pass

FILE_DATI="dati_volontari.json"
FILE_POST="postazioni.json"
FILE_EMER="emergenze.json"
FILE_RADIO="radio_db.json"
FILE_DIST="dist_radio.json"
FILE_EVENTI="eventi.json"
FILE_CHECK="checkin.json"
FILE_NOMI="mem_nomi.json"
FILE_DETTAGLI="volontari_dettagli.json"

COMUNI_VARESE=["Varese","Busto Arsizio","Gallarate","Saronno","Cassano Magnago","Tradate","Malnate","Luino","Venegono Superiore","Venegono Inferiore","Castiglione Olona","Lozza"]
EMERGENCY_LOGOS = {
 "incendio_boschivo": {"nome": "Incendio Boschivo","emoji": "🔥"},
 "frana": {"nome": "Frana","emoji": "⛰️"},
 "caduta_albero": {"nome": "Caduta Albero","emoji": "🌳"},
 "esondazione": {"nome": "Esondazione","emoji": "🌊"},
 "vvff": {"nome": "VVFF","emoji": "🚒"},
 "protezione_civile": {"nome": "Prot. Civile","emoji": "🦺"},
 "ambulanza": {"nome": "Ambulanza 118","emoji": "🚑"},
}

@st.cache_data(ttl=86400)
def load_comuni_italia():
    try:
        url="https://raw.githubusercontent.com/matteocontrini/comuni-json/master/comuni.json"
        r=requests.get(url,timeout=10)
        if r.status_code==200:
            data=r.json()
            comuni=sorted([c["nome"] for c in data])
            top=[c for c in COMUNI_VARESE if c in comuni]
            altri=[c for c in comuni if c not in top]
            return top+altri
    except: pass
    return sorted(list(set(COMUNI_VARESE)))

if "authenticated" not in st.session_state: st.session_state.authenticated=False
if "dati" not in st.session_state: st.session_state.dati=load_json(FILE_DATI,[])
if "postazioni" not in st.session_state: st.session_state.postazioni=load_json(FILE_POST,[])
if "emergenze_lista" not in st.session_state: st.session_state.emergenze_lista=load_json(FILE_EMER,[])
if "radio_db" not in st.session_state: st.session_state.radio_db=load_json(FILE_RADIO,[])
if "dist_radio" not in st.session_state: st.session_state.dist_radio=load_json(FILE_DIST,[])
if "eventi_lista" not in st.session_state: st.session_state.eventi_lista=load_json(FILE_EVENTI,[])
if "checkin_lista" not in st.session_state: st.session_state.checkin_lista=load_json(FILE_CHECK,[])
if "mem_nomi" not in st.session_state: st.session_state.mem_nomi=load_json(FILE_NOMI,[])
if "vol_dettagli" not in st.session_state: st.session_state.vol_dettagli=load_json(FILE_DETTAGLI,{})
if "menu_scelta" not in st.session_state: st.session_state.menu_scelta="Dashboard"
if "volontario_selezionato" not in st.session_state: st.session_state.volontario_selezionato=None
if "volontario_idx" not in st.session_state: st.session_state.volontario_idx=None

def header_loghi():
    c1,c2,c3=st.columns([1,2,1])
    if os.path.exists("logo.png"): c1.image("logo.png",width=90)
    c2.markdown("<h2 style='text-align:center; color:#0e7a3d;'>VOLONTARIATO<br>Sezione di Varese</h2>", unsafe_allow_html=True)
    if os.path.exists("logo_pc_lombardia.png"): c3.image("logo_pc_lombardia.png",width=90)

if not st.session_state.authenticated:
    header_loghi()
    st.markdown("<h2 style='text-align:center; color:#2e7d32;'>Accesso - admin / ana2024</h2>", unsafe_allow_html=True)
    c1,c2,c3=st.columns([1,2,1])
    with c2:
        with st.form("login"):
            u=st.text_input("Username",value="admin")
            p=st.text_input("Password",type="password",value="ana2024")
            if st.form_submit_button("Accedi",use_container_width=True):
                if u=="admin" and p=="ana2024":
                    st.session_state.authenticated=True
                    st.rerun()
    st.stop()

header_loghi()
st.divider()
with st.sidebar:
    if os.path.exists("logo.png"): st.image("logo.png",width=80)
    st.markdown("### MENU ANA VARESE")
    opzioni=["Dashboard","Volontari","Emergenze con Loghi","Mappa Postazioni","DB Radio","Distribuzione Radio","Eventi","Check-in","Tabella Interventi Emergenza","Backup"]
    sel=st.radio("Seleziona",opzioni,index=opzioni.index(st.session_state.menu_scelta) if st.session_state.menu_scelta in opzioni else 0)
    if sel!=st.session_state.menu_scelta:
        st.session_state.menu_scelta=sel
        st.rerun()
    if st.button("🚪 LOGOUT",use_container_width=True):
        st.session_state.authenticated=False
        st.rerun()

scelta=st.session_state.menu_scelta
st.markdown(f"## {scelta}")
st.divider()
COMUNI_TUTTI=load_comuni_italia()
MIME="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

# DASHBOARD
if scelta=="Dashboard":
    st.markdown("### ⚡ TASTI SCELTA RAPIDA - COME PRIMA")
    c1,c2,c3,c4=st.columns(4)
    with c1:
        if st.button("🚨\nNUOVA EMERGENZA", key="q_em", use_container_width=True):
            st.session_state.menu_scelta="Emergenze con Loghi"; st.rerun()
    with c2:
        if st.button("📍\nPOSTAZIONE", key="q_post", use_container_width=True):
            st.session_state.menu_scelta="Mappa Postazioni"; st.rerun()
    with c3:
        if st.button("👤\nVOLONTARIO", key="q_vol", use_container_width=True):
            st.session_state.menu_scelta="Volontari"; st.session_state.volontario_selezionato=None; st.rerun()
    with c4:
        if st.button("💾\nBACKUP UNICO", key="q_back", use_container_width=True):
            st.session_state.menu_scelta="Backup"; st.rerun()

    st.divider()
    c1,c2,c3,c4=st.columns(4)
    c1.metric("🚨 Emergenze",len(st.session_state.emergenze_lista))
    c2.metric("📍 Postazioni",len(st.session_state.postazioni))
    c3.metric("👤 Volontari",len(st.session_state.dati))
    c4.metric("📻 Radio",len(st.session_state.radio_db))
    c5,c6,c7,c8=st.columns(4)
    c5.metric("📅 Eventi",len(st.session_state.eventi_lista))
    c6.metric("✅ Check-in",len(st.session_state.checkin_lista))
    c7.metric("📡 Distr Radio",len(st.session_state.dist_radio))
    c8.metric("📝 Nomi",len(st.session_state.mem_nomi))

    st.divider()
    st.markdown("### 👥 TABELLA VOLONTARI - CLICCA NOME PER SOTTOMASCHERE")
    st.info("Clicca sul nome per aprire le sottomaschere del volontario!")
    if st.session_state.dati:
        h1,h2,h3,h4=st.columns([3,2,2,2])
        h1.markdown("**Nome - CLICCA**"); h2.markdown("**Cell**"); h3.markdown("**Comune**"); h4.markdown("**Ruolo**")
        st.divider()
        for idx, vol in enumerate(st.session_state.dati):
            c1,c2,c3,c4=st.columns([3,2,2,2])
            with c1:
                if st.button(f"👤 {vol.get('Nome','')}", key=f"dash_vol_{idx}", use_container_width=True):
                    st.session_state.volontario_selezionato=vol
                    st.session_state.volontario_idx=idx
                    st.session_state.menu_scelta="Volontari"
                    st.rerun()
            with c2: st.write(vol.get('Cellulare',''))
            with c3: st.write(vol.get('Comune',''))
            with c4: st.write(vol.get('Ruolo',''))

# VOLONTARI CON SOTTOMASCHERE - COME PRIMA + SOTTOMASCHERE
elif scelta=="Volontari":
    if st.button("🏠 Torna alla Dashboard", use_container_width=True):
        st.session_state.menu_scelta="Dashboard"; st.rerun()

    # DETTAGLIO CON SOTTOMASCHERE SE SELEZIONATO
    if st.session_state.volontario_selezionato is not None:
        vol=st.session_state.volontario_selezionato
        idx=st.session_state.volontario_idx
        vol_id=f"{vol.get('Nome','')}_{idx}"
        st.markdown('<div class="vol-selected">', unsafe_allow_html=True)
        st.markdown(f"### 👤 VOLONTARIO SELEZIONATO: {vol.get('Nome','')} - SOTTOMASCHERE")
        c1,c2=st.columns([3,1])
        with c1: st.markdown(f"**{vol.get('Cellulare','')} | {vol.get('Comune','')} | {vol.get('Ruolo','')}**")
        with c2:
            if st.button("❌ Chiudi", key="chiudi_det"):
                st.session_state.volontario_selezionato=None; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📋 Anagrafica","📻 Radio","📅 Eventi","✅ Presenze","🚨 Emergenze","📄 Note/Doc"])

        with tab1:
            st.markdown('<div class="submask">', unsafe_allow_html=True)
            st.markdown("#### 📋 Sottomaschera 1 - Anagrafica Completa (come vecchi app.py)")
            with st.form("form_anag"):
                nome_completo=vol.get('Nome','')
                parti=nome_completo.split(" ",1)
                nome_init=parti[0] if len(parti)>0 else ""
                cognome_init=parti[1] if len(parti)>1 else ""
                c1,c2=st.columns(2)
                with c1:
                    nome=st.text_input("Nome *", value=nome_init)
                    cognome=st.text_input("Cognome *", value=cognome_init)