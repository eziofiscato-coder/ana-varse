import streamlit as st
import pandas as pd
from datetime import date, datetime
from io import BytesIO
import os, json, base64, requests, tempfile

st.set_page_config(page_title="ANA Varese", page_icon="🟢", layout="wide")

st.markdown("""
<style>
.stApp{background:#e8f5e9!important;}
.main.block-container{background:white!important;border-radius:18px;padding:20px!important;max-width:98%!important;}
[data-testid="stSidebar"]{background:#a5d6a7!important;border-right:4px solid #2e7d32!important;}
.stForm{background:#c8e6c9!important;border:3px solid #2e7d32!important;border-radius:15px!important;}
.stButton>button{background:#2e7d32!important;color:white!important;font-weight:bold!important;min-height:50px!important;}
div[data-testid="stFormSubmitButton"]>button{background:#d32f2f!important;}
.vol-selected{background:#fff3e0!important;border:4px solid #ef6c00!important;border-radius:12px!important;padding:20px!important;}
.submask{background:#f1f8e9!important;border:3px solid #2e7d32!important;border-radius:12px!important;padding:15px!important;margin:8px 0!important;}
.icon-lib{border:3px solid #2e7d32;border-radius:12px;padding:10px;background:white;margin:5px;text-align:center;}
.icon-selected{border:4px solid #ef6c00!important;background:#fff3e0!important;}
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
def get_b64(p):
    try:
        if os.path.exists(p):
            with open(p,"rb") as f: return base64.b64encode(f.read()).decode()
    except: pass
    return ""
def img_to_b64(file):
    try: return base64.b64encode(file.getvalue()).decode()
    except: return ""
def trova_b64_logo(nome, libreria):
    for ic in libreria:
        if ic.get("nome")==nome and ic.get("b64"): return ic.get("b64")
    return None
def salva_icona_temp(b64, nome):
    try:
        data=base64.b64decode(b64)
        tmp_path=os.path.join(tempfile.gettempdir(), f"icon_{nome.replace(' ','_').replace('/','_')}.png")
        with open(tmp_path,"wb") as f: f.write(data)
        return tmp_path
    except: return None

FILE_DATI="dati_volontari.json"
FILE_POST="postazioni.json"
FILE_INTERVENTI="interventi_emergenza.json"
FILE_ICONE_COND="libreria_icone_condivisa.json"
FILE_RADIO="db_radio.json"
FILE_CONSEGNA="consegna_radio.json"
FILE_EVENTI="eventi.json"
FILE_BROGLIACCIO="brogliaccio.json"
COMUNI=["Varese","Busto Arsizio","Gallarate","Saronno","Venegono Superiore","Venegono Inferiore","Castiglione Olona","Lozza","Tradate","Malnate","Luino"]
ICONS=["📍","🚨","🏕️","🚧","👥","🔥","🌊","⛰️","🚑","🚒","🦺","📻","🏠"]

for k,v in [("dati",[]),("postazioni",[]),("icone_lib",[]),("interventi_lista",[]),("db_radio",[]),("consegna_radio",[]),("eventi",[]),("brogliaccio",[]),("menu_scelta","Dashboard"),("volontario_selezionato",None),("volontario_idx",None),("form_nome",""),("form_cognome",""),("form_cell",""),("form_assoc","ANA Varese"),("map_lat",45.8205),("map_lon",8.8250),("map_comune","Varese"),("map_via",""),("map_logo_selezionato","📍 Default"),("em_comune",""),("em_via",""),("em_lat",""),("em_lon",""),("em_post_selezionata",None),("em_logo_selezionato","🚨 Default"),("postazione_selezionata_per_mappa",None),("authenticated",False)]:
    if k not in st.session_state: st.session_state[k]=v

if not st.session_state.dati: st.session_state.dati=load_json(FILE_DATI,[])
if not st.session_state.postazioni: st.session_state.postazioni=load_json(FILE_POST,[])
if not st.session_state.interventi_lista: st.session_state.interventi_lista=load_json(FILE_INTERVENTI,[])
if not st.session_state.icone_lib: st.session_state.icone_lib=load_json(FILE_ICONE_COND,[])
if not st.session_state.db_radio: st.session_state.db_radio=load_json(FILE_RADIO,[])
if not st.session_state.consegna_radio: st.session_state.consegna_radio=load_json(FILE_CONSEGNA,[])
if not st.session_state.eventi: st.session_state.eventi=load_json(FILE_EVENTI,[])
if not st.session_state.brogliaccio: st.session_state.brogliaccio=load_json(FILE_BROGLIACCIO,[])

def header_loghi():
    b64=get_b64("logo.png")
    if b64:
        st.markdown(f"<div style='display:flex;justify-content:center;align-items:center;gap:25px;background:#a5d6a7;padding:15px;border-radius:15px;border:3px solid #2e7d32;margin-bottom:15px;'><img src='data:image/png;base64,{b64}' style='width:90px;height:90px;border-radius:50%;border:3px solid #1b5e20;background:white;'><h2 style='color:#0e7a3d;margin:0;text-align:center;'>VOLONTARIATO<br>Sezione di Varese</h2><img src='data:image/png;base64,{b64}' style='width:90px;height:90px;border-radius:50%;border:3px solid #1b5e20;background:white;'></div>", unsafe_allow_html=True)
    else:
        st.markdown("<h2 style='text-align:center;color:#0e7a3d;'>VOLONTARIATO<br>Sezione di Varese</h2>", unsafe_allow_html=True)

def torna_dashboard():
    c1,c2=st.columns([1,1])
    with c1:
        if st.button("🏠 TORNA ALLA DASHBOARD",use_container_width=True,key=f"torna_{st.session_state.menu_scelta}"):
            st.session_state.menu_scelta="Dashboard"; st.rerun()
    with c2:
        if st.button("🚪 LOGOUT",use_container_width=True,key=f"logout_{st.session_state.menu_scelta}"):
            st.session_state.authenticated=False; st.rerun()

if not st.session_state.authenticated:
    header_loghi()
    c1,c2,c3=st.columns([1,2,1])
    with c2:
        with st.form("login"):
            u=st.text_input("Username",value="admin")
            p=st.text_input("Password",type="password",value="ana2024")
            if st.form_submit_button("🔴 ACCEDI",use_container_width=True,type="primary"):
                if (u=="admin" and p=="ana2024") or p=="ANA2025":
                    st.session_state.authenticated=True; st.rerun()
                else: st.error("Password errata")
    st.stop()

header_loghi()
st.divider()

with st.sidebar:
    if os.path.exists("logo.png"): st.image("logo.png",width=80)
    st.markdown("### MENU")
    opzioni=["Dashboard","Volontari","Mappa Postazioni","Tabella Emergenze","DB Radio","Consegna Radio","Evento","Brogliaccio","Backup"]
    sel=st.radio("Vai a",opzioni,index=opzioni.index(st.session_state.menu_scelta) if st.session_state.menu_scelta in opzioni else 0)
    if sel!=st.session_state.menu_scelta:
        st.session_state.menu_scelta=sel; st.rerun()
    st.divider()
    st.metric("Volontari",len(st.session_state.dati))
    st.metric("Postazioni",len(st.session_state.postazioni))
    st.metric("Loghi",len(st.session_state.icone_lib))
    st.divider()
    if st.button("🚪 LOGOUT",use_container_width=True,key="logout_sidebar"):
        st.session_state.authenticated=False; st.rerun()

scelta=st.session_state.menu_scelta
MIME="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

if scelta=="Dashboard":
    c1,c2=st.columns([4,1])
    with c1: st.markdown("## 🏠 DASHBOARD - TUTTI I FORM")
    with c2:
        if st.button("🚪 LOGOUT",use_container_width=True,key="logout_dashboard"):
            st.session_state.authenticated=False; st.rerun()
    c1,c2,c3,c4=st.columns(4)
    with c1:
        if st.button("👥 VOLONTARI\n6 Sottomaschere",key="q_vol",use_container_width=True):
            st.session_state.menu_scelta="Volontari"; st.rerun()
    with c2:
        if st.button("📍 MAPPA\nLoghi",key="q_map",use_container_width=True):
            st.session_state.menu_scelta="Mappa Postazioni"; st.rerun()
    with c3:
        if st.button("🚨 EMERGENZE",key="q_em",use_container_width=True):
            st.session_state.menu_scelta="Tabella Emergenze"; st.rerun()
    with c4:
        if st.button("📻 DB RADIO",key="q_radio",use_container_width=True):
            st.session_state.menu_scelta="DB Radio"; st.rerun()
    c5,c6,c7,c8=st.columns(4)
    with c5:
        if st.button("📦 CONSEGNA RADIO",key="q_cons",use_container_width=True):
            st.session_state.menu_scelta="Consegna Radio"; st.rerun()
    with c6:
        if st.button("📅 EVENTO",key="q_ev",use_container_width=True):
            st.session_state.menu_scelta="Evento"; st.rerun()
    with c7:
        if st.button("📝 BROGLIACCIO",key="q_brog",use_container_width=True):
            st.session_state.menu_scelta="Brogliaccio"; st.rerun()
    with c8:
        if st.button("💾 BACKUP",key="q_back",use_container_width=True):
            st.session_state.menu_scelta="Backup"; st.rerun()

elif scelta=="Volontari":
    torna_dashboard()
    st.markdown("## 👥 VOLONTARI - 6 SOTTOMASCHERE")
    if st.session_state.volontario_selezionato is not None:
        vol=st.session_state.volontario_selezionato
        idx=st.session_state.volontario_idx
        st.markdown('<div class="vol-selected">',unsafe_allow_html=True)
        st.markdown(f"### 👤 {vol.get('Nome','')} - 6 SOTTOMASCHERE")
        st.write(f"{vol.get('Cellulare','')} | {vol.get('Comune','')} | {vol.get('Ruolo','')}")
        if st.button("❌ Chiudi",key="chiudi_det"):
            st.session_state.volontario_selezionato=None; st.session_state.volontario_idx=None; st.rerun()
        st.markdown('</div>',unsafe_allow_html=True)
        t1,t2,t3,t4,t5,t6=st.tabs(["📋 Anagrafica","📻 Radio","📅 Eventi","✅ Presenze","🚨 Emergenze","📄 Note"])
        with t1:
            st.markdown('<div class="submask">',unsafe_allow_html=True)
            st.markdown("#### Anagrafica")
            with st.form("form_anag"):
                parti=vol.get('Nome','').split(" ",1)
                nome=st.text_input("Nome",value=parti[0] if len(parti)>0 else "")
                cognome=st.text_input("Cognome",value=parti[1] if len(parti)>1 else "")
                cell=st.text_input("Cellulare",value=vol.get('Cellulare',''))
                comune=st.selectbox("Comune",COMUNI,index=0)
                ruolo=st.selectbox("Ruolo",["Volontario","Caposquadra","Coordinatore"],index=0)
                if st.form_submit_button("💾 SALVA",use_container_width=True,type="primary"):