import streamlit as st
import pandas as pd
from datetime import date, datetime
from io import BytesIO
import os, json, base64, hashlib

st.set_page_config(page_title="ANA Varese", layout="wide")

st.markdown("""
<style>
.stApp{background:#e8f5e9!important;}
.block-container{background:white!important;border-radius:18px;padding:20px!important;padding-bottom:95px!important;}
[data-testid="stSidebar"]{background:#a5d6a7!important;border-right:4px solid #2e7d32!important;}
.stForm{background:#c8e6c9!important;border:3px solid #2e7d32!important;border-radius:15px!important;}
.stButton>button{background:#2e7d32!important;color:white!important;font-weight:bold!important;min-height:50px!important;border-radius:10px!important;}
.sub{border:2px solid #2e7d32;border-radius:12px;padding:15px;background:#f1f8e9;margin:10px 0px;}
.foot{position:fixed;bottom:5px;left:10px;background:white;border:2px solid #2e7d32;border-radius:12px;padding:5px 12px;display:flex;align-items:center;gap:8px;z-index:9999;}
.foot img{width:45px;height:45px;border-radius:50%;border:2px solid #2e7d32;}
.foot span{font-size:13px;font-weight:bold;color:#2e7d32;}
</style>
""", unsafe_allow_html=True)

def load_json(f,d):
    try:
        if os.path.exists(f):
            with open(f,"r",encoding="utf-8") as fh:
                return json.load(fh)
    except:
        pass
    return d

def save_json(f,d):
    try:
        with open(f,"w",encoding="utf-8") as fh:
            json.dump(d,fh,indent=2)
    except:
        pass

def get_b64(p):
    try:
        if os.path.exists(p):
            with open(p,"rb") as f:
                return base64.b64encode(f.read()).decode()
    except:
        pass
    return ""

def hash_pwd(p):
    return hashlib.sha256(p.encode()).hexdigest()

def footer():
    b=get_b64("ezio.png")
    if not b:
        b=get_b64("logo.png")
    if b:
        img="<img src='data:image/png;base64,"+b+"'>"
    else:
        img="<div style='width:45px;height:45px;background:#2e7d32;border-radius:50%;'></div>"
    st.markdown("<div class='foot'>"+img+"<span>by Ezio F. vers. 1.0 2026</span></div>",unsafe_allow_html=True)

FD="dati.json"
FU="utenti.json"
FP="post.json"
FE="eventi.json"
FR="radio.json"
FC="check.json"
FB="brog.json"
FO="consegna.json"
FM="emerg.json"
COM=["Varese","Busto","Gallarate","Saronno","Altro"]

if "dati" not in st.session_state:
    st.session_state.dati=[]
if "utenti" not in st.session_state:
    st.session_state.utenti=[]
if "menu" not in st.session_state:
    st.session_state.menu="Dashboard"
if "auth" not in st.session_state:
    st.session_state.auth=False

st.session_state.dati=load_json(FD,[])
st.session_state.utenti=load_json(FU,[])

if not st.session_state.utenti:
    st.session_state.utenti=[
        {"username":"admin","password":hash_pwd("ana2024")},
        {"username":"utente","password":hash_pwd("utente2024")}
    ]
    save_json(FU,st.session_state.utenti)

def header():
    b=get_b64("logo.png")
    if b:
        h="<div style='text-align:center;background:#a5d6a7;padding:15px;border-radius:15px;border:3px solid #2e7d32;'><img src='data:image/png;base64,"+b+"' style='width:80px;border-radius:50%;'><h2 style='color:#0e7a3d;'>VOLONTARIATO Varese</h2></div>"
        st.markdown(h,unsafe_allow_html=True)
    else:
        st.markdown("<h2 style='text-align:center;color:#0e7a3d;'>VOLONTARIATO Varese</h2>",unsafe_allow_html=True)

def torna():
    if st.button("TORNA A DASHBOARD",use_container_width=True):
        st.session_state.menu="Dashboard"
        st.rerun()

if not st.session_state.auth:
    header()
    st.markdown("## LOGIN")
    c1,c2,c3=st.columns([1,2,1])
    with c2:
        with st.form("login"):
            u=st.text_input("Username",value="admin")
            p=st.text_input("Password",type="password",value="ana2024")
            ok=st.form_submit_button("ACCEDI",use_container_width=True)
            if ok:
                ph=hash_pwd(p)
                trov=None
                for ut in st.session_state.utenti:
                    if ut["username"]==u and ut["password"]==ph:
                        trov=ut
                if trov:
                    st.session_state.auth=True
                    st.rerun()
                else:
                    st.error("Errati")
    footer()
    st.stop()

header()
st.divider()

with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png",width=80)
    opts=["Dashboard","Volontari","Mappa","Eventi","Radio","Check-In","Brogliaccio","Consegna","Emergenze","Backup"]
    sel=st.radio("Vai a",opts,index=0)
    if sel!=st.session_state.menu:
        st.session_state.menu=sel
        st.rerun()
    if st.button("LOGOUT",use_container_width=True):
        st.session_state.auth=False
        st.rerun()

scelta=st.session_state.menu

if scelta=="Dashboard":
    st.markdown("## DASHBOARD")
    st.success("Benvenuto")
    if st.button("VOLONTARI",use_container_width=True,key="d1"):
        st.session_state.menu="Volontari"
        st.rerun()
    if st.button("MAPPA",use_container_width=True,key="d2"):
        st.session_state.menu="Mappa"
        st.rerun()
    if st.button("EVENTI",use_container_width=True,key="d3"):
        st.session_state.menu="Eventi"
        st.rerun()
    if st.button("RADIO",use_container_width=True,key="d4"):
        st.session_state.menu="Radio"
        st.rerun()
    if st.button("BACKUP",use_container_width=True,key="d9"):
        st.session_state.menu="Backup"
        st.rerun()
    footer()

elif scelta=="Volontari":
    torna()
    st.markdown("## VOLONTARI - 5 SOTTOMASCHERE")
    t1,t2,t3,t4,t5=st.tabs(["1 ANAGRAFICA","2 RESIDENZA","3 TESSERA","4 ABILIT","5 NOTE"])
    with t1:
        st.markdown('<div class="sub">',unsafe_allow_html=True)
        with st.form("f1"):
            a1=st.text_input("Nome *",key="a1")
            a2=st.text_input("Cognome *",key="a2")
            a3=st.text_input("CF",key="a3")
            a4=st.date_input("Data Nascita",value=date(1980,1,1),key="a4")
            if st.form_submit_button("SALVA 1"):
                st.session_state.s1_nome=a1
                st.session_state.s1_cogn=a2
                st.session_state.s1_cf=a3
                st.session_state.s1_dn=str(a4)
                st.success("Salvato 1")
        st.markdown('</div>',unsafe_allow_html=True)
    with t2:
        st.markdown('<div class="sub">',unsafe_allow_html=True)
        with st.form("f2"):
            b1=st.text_input("Via *",key="b1")
            b2=st.selectbox("Comune",COM,key="b2")
            b3=st.text_input("Cell *",key="b3")
            b4=st.text_input("Email",key="b4")
            if st.form_submit_button("SALVA 2"):
                st.session_state.s2_via=b1
                st.session_state.s2_com=b2
                st.session_state.s2_cell=b3
                st.session_state.s2_email=b4
                st.success("Salvato 2")
        st.markdown('</div>',unsafe_allow_html=True)
    with t3:
        st.markdown('<div class="sub">',unsafe_allow_html=True)
        with st.form("f3"):
            c1x=st.text_input("Tessera ANA",key="c1")
            c2x=st.text_input("Sezione",value="Varese",key="c2")
            c3x=st.selectbox("Ruolo",["Volontario","Caposquad