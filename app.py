import streamlit as st
import pandas as pd
from datetime import date, datetime
from io import BytesIO
import os, json, base64, requests

st.set_page_config(page_title="ANA Varese", page_icon="🟢", layout="wide")

st.markdown("""
<style>
.stApp{background:#e8f5e9!important;}
.main.block-container{background:white!important;border-radius:18px;padding:20px!important;max-width:98%!important;}
[data-testid="stSidebar"]{background:#a5d6a7!important;border-right:4px solid #2e7d32!important;}
.stForm{background:#c8e6c9!important;border:3px solid #2e7d32!important;border-radius:15px!important;padding:15px!important;}
.stButton>button{background:#2e7d32!important;color:white!important;font-weight:bold!important;min-height:50px!important;border-radius:10px!important;}
div[data-testid="stFormSubmitButton"]>button{background:#d32f2f!important;}
.quick-btn-green>button{background:linear-gradient(135deg,#2e7d32,#1b5e20)!important;min-height:90px!important;font-size:15px!important;}
.quick-btn-blue>button{background:linear-gradient(135deg,#1565c0,#0d47a1)!important;min-height:90px!important;}
.quick-btn-red>button{background:linear-gradient(135deg,#c62828,#b71c1c)!important;min-height:90px!important;}
.quick-btn>button{background:linear-gradient(135deg,#ff9800,#ef6c00)!important;min-height:90px!important;}
.vol-selected{background:#fff3e0!important;border:4px solid #ef6c00!important;border-radius:12px!important;padding:20px!important;margin:10px 0!important;}
.submask{background:#f1f8e9!important;border:3px solid #2e7d32!important;border-radius:12px!important;padding:15px!important;margin:8px 0!important;}
.icon-lib{border:2px solid #2e7d32;border-radius:10px;padding:10px;background:white;margin:5px;}
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

FILE_DATI="dati_volontari.json"
FILE_POST="postazioni.json"
FILE_INTERVENTI="interventi_emergenza.json"
FILE_ICONE="libreria_icone.json"
FILE_ICONE_EM="libreria_icone_emergenze.json"
FILE_RADIO="db_radio.json"
FILE_CONSEGNA="consegna_radio.json"
FILE_EVENTI="eventi.json"
FILE_BROGLIACCIO="brogliaccio.json"
FILE_REGISTRO="registro_radio.json"

COMUNI=["Varese","Busto Arsizio","Gallarate","Saronno","Venegono Superiore","Venegono Inferiore","Castiglione Olona","Lozza","Tradate","Malnate","Luino"]
ICONS=["📍","🚨","🏕️","🚧","👥","🔥","🌊","⛰️","🚑","🚒","🦺","📻","🏠"]

for k,v in [("dati",[]),("postazioni",[]),("icone_lib",[]),("icone_em_lib",[]),("interventi_lista",[]),("db_radio",[]),("consegna_radio",[]),("eventi",[]),("brogliaccio",[]),("registro_radio",[]),("menu_scelta","Dashboard"),("volontario_selezionato",None),("volontario_idx",None),("form_nome",""),("form_cognome",""),("form_cell",""),("form_assoc","ANA Varese"),("map_lat",45.8205),("map_lon",8.8250),("map_comune","Varese"),("map_via",""),("em_comune",""),("em_via",""),("em_lat",""),("em_lon",""),("em_post_selezionata",None),("authenticated",False)]:
    if k not in st.session_state: st.session_state[k]=v

# Carica tutti i dati salvati - così li ritrovi quando esci
if not st.session_state.dati: st.session_state.dati=load_json(FILE_DATI,[])
if not st.session_state.postazioni: st.session_state.postazioni=load_json(FILE_POST,[])
if not st.session_state.interventi_lista: st.session_state.interventi_lista=load_json(FILE_INTERVENTI,[])
if not st.session_state.icone_lib: st.session_state.icone_lib=load_json(FILE_ICONE,[])
if not st.session_state.icone_em_lib: st.session_state.icone_em_lib=load_json(FILE_ICONE_EM,[])
if not st.session_state.db_radio: st.session_state.db_radio=load_json(FILE_RADIO,[])
if not st.session_state.consegna_radio: st.session_state.consegna_radio=load_json(FILE_CONSEGNA,[])
if not st.session_state.eventi: st.session_state.eventi=load_json(FILE_EVENTI,[])
if not st.session_state.brogliaccio: st.session_state.brogliaccio=load_json(FILE_BROGLIACCIO,[])
if not st.session_state.registro_radio: st.session_state.registro_radio=load_json(FILE_REGISTRO,[])

def header_loghi():
    b64=get_b64("logo.png")
    if b64:
        st.markdown(f"<div style='display:flex;justify-content:center;align-items:center;gap:25px;background:#a5d6a7;padding:15px;border-radius:15px;border:3px solid #2e7d32;margin-bottom:15px;'><img src='data:image/png;base64,{b64}' style='width:90px;height:90px;border-radius:50%;border:3px solid #1b5e20;background:white;'><h2 style='color:#0e7a3d;margin:0;text-align:center;'>VOLONTARIATO<br>Sezione di Varese</h2><img src='data:image/png;base64,{b64}' style='width:90px;height:90px;border-radius:50%;border:3px solid #1b5e20;background:white;'></div>", unsafe_allow_html=True)
    else:
        st.markdown("<h2 style='text-align:center;color:#0e7a3d;'>VOLONTARIATO<br>Sezione di Varese</h2>", unsafe_allow_html=True)

if not st.session_state.authenticated:
    header_loghi()
    st.markdown("<h2 style='text-align:center;color:#2e7a3d;'>🔒 Accesso Riservato</h2>", unsafe_allow_html=True)
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
    st.markdown("### MENU COMPLETO")
    opzioni=["Dashboard","Volontari","Mappa Postazioni","Tabella Emergenze","DB Radio","Consegna Radio","Evento","Brogliaccio","Registro Radio","Backup"]
    sel=st.radio("Vai a",opzioni,index=opzioni.index(st.session_state.menu_scelta) if st.session_state.menu_scelta in opzioni else 0)
    if sel!=st.session_state.menu_scelta:
        st.session_state.menu_scelta=sel; st.rerun()
    st.divider()
    st.metric("Volontari",len(st.session_state.dati))
    st.metric("Postazioni",len(st.session_state.postazioni))
    st.metric("Emergenze",len(st.session_state.interventi_lista))
    st.metric("Radio",len(st.session_state.db_radio))
    st.divider()
    if st.button("🚪 LOGOUT",use_container_width=True):
        st.session_state.authenticated=False; st.rerun()

scelta=st.session_state.menu_scelta
MIME="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

def tabella_sotto(nome, lista, file_json):
    st.divider()
    st.markdown(f"### 📋 TABELLA {nome} - Sotto maschera - Dati salvati")
    if lista:
        df=pd.DataFrame(lista)
        st.dataframe(df,use_container_width=True)
        out=BytesIO(); df.to_excel(out,index=False,engine="openpyxl")
        c1,c2=st.columns(2)
        with c1:
            st.download_button(f"📥 Excel {nome}",out.getvalue(),file_name=f"{nome.lower()}_{date.today()}.xlsx",mime=MIME,use_container_width=True,key=f"dl_{nome}")
        with c2:
            if st.button(f"🗑️ Cancella tutti {nome}",use_container_width=True,key=f"del_{nome}"):
                lista.clear()
                save_json(file_json,[])
                st.rerun()
    else:
        st.info(f"Nessun dato in {nome} - Inserisci sopra e si salva automaticamente!")

if scelta=="Dashboard":
    st.markdown("## 🏠 DASHBOARD - MENU COMPLETO ALLINEATO")
    st.markdown("### ⚡ Tasti tutti allineati a posto")
    c1,c2,c3,c4=st.columns(4)
    with c1:
        st.markdown('<div class="quick-btn-green">',unsafe_allow_html=True)
        if st.button("👥\nVOLONTARI\nSottomaschere",key="q_vol",use_container_width=True):
            st.session_state.menu_scelta="Volontari"; st.rerun()
        st.markdown('</div>',unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="quick-btn-blue">',unsafe_allow_html=True)
        if st.button("📍\nMAPPA\nPostazioni",key="q_map",use_container_width=True):
            st.session_state.menu_scelta="Mappa Postazioni"; st.rerun()
        st.markdown('</div>',unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="quick-btn-red">',unsafe_allow_html=True)
        if st.button("🚨\nTABELLA\nEmergenze",key="q_em",use_container_width=True):
            st.session_state.menu_scelta="Tabella Emergenze"; st.rerun()
        st.markdown('</div>',unsafe_allow_html=True)
    with c4:
        st.markdown('<div class="quick-btn">',unsafe_allow_html=True)
        if st.button("📻\nDB RADIO\nInventario",key="q_radio",use_container_width=True):
            st.session_state.menu_scelta="DB Radio"; st.rerun()
        st.markdown('</div>',unsafe_allow_html=True)
    c5,c6,c7,c8=st.columns(4)
    with c5:
        if st.button("📦\nCONSEGNA\nRadio",key="q_cons",use_container_width=True):
            st.session_state.menu_scelta="Consegna Radio"; st.rerun()
    with c6:
        if st.button("📅\nEVENTO\nGestione",key="q_ev",use_container_width=True):
            st.session_state.menu_scelta="Evento"; st.rerun()
    with c7:
        if st.button("📝\nBROGLIACCIO\nODV",key="q_brog",use_container_width=True):
            st.session_state.menu_scelta="Brogliaccio"; st.rerun()
    with c8:
        if st.button("💾\nBACKUP\nExcel Unico",key="q_back",use_container_width=True):
            st.session_state.menu_scelta="Backup"; st.rerun()
    st.divider()
    c1,c2,c3,c4=st.columns(4)
    c1.metric("👥 Volontari",len(st.session_state.dati))
    c2.metric("📍 Postazioni",len(st.session_state.postazioni))
    c3.metric("🚨 Emergenze",len(st.session_state.interventi_lista))
    c4.metric("📻 Radio",len(st.session_state.db_radio))

elif scelta=="Volontari":
    if st.button("🏠 Dashboard",use_container_width=True):
        st.session_state.menu_scelta="Dashboard"; st.rerun()
    st.markdown("## 👥 VOLONTARI - 6 SOTTOMASCHERE")
    if st