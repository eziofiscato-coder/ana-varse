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
    st.markdown("<div class='foot'>"+img+"<span>by Ezio F. 2026</span></div>",unsafe_allow_html=True)

FD="dati.json"
FU="utenti.json"
FP="post.json"
FE="eventi.json"
FR="radio.json"
FC="check.json"
FB="brog.json"
FO="consegna.json"
FM="emerg.json"
FI="icone.json"

if "dati" not in st.session_state:
    st.session_state.dati=[]
if "post" not in st.session_state:
    st.session_state.post=[]
if "eventi" not in st.session_state:
    st.session_state.eventi=[]
if "radio" not in st.session_state:
    st.session_state.radio=[]
if "check" not in st.session_state:
    st.session_state.check=[]
if "brog" not in st.session_state:
    st.session_state.brog=[]
if "consegna" not in st.session_state:
    st.session_state.consegna=[]
if "emerg" not in st.session_state:
    st.session_state.emerg=[]
if "icone" not in st.session_state:
    st.session_state.icone={}
if "utenti" not in st.session_state:
    st.session_state.utenti=[]
if "menu" not in st.session_state:
    st.session_state.menu="Dashboard"
if "auth" not in st.session_state:
    st.session_state.auth=False
if "lat_tmp" not in st.session_state:
    st.session_state.lat_tmp=45.8205
if "lon_tmp" not in st.session_state:
    st.session_state.lon_tmp=8.8250

st.session_state.dati=load_json(FD,[])
st.session_state.utenti=load_json(FU,[])
st.session_state.post=load_json(FP,[])
st.session_state.eventi=load_json(FE,[])
st.session_state.radio=load_json(FR,[])
st.session_state.check=load_json(FC,[])
st.session_state.brog=load_json(FB,[])
st.session_state.consegna=load_json(FO,[])
st.session_state.emerg=load_json(FM,[])
st.session_state.icone=load_json(FI,{})

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
        st.markdown("<h2 style='text-align:center;color:green;'>VOLONTARIATO Varese</h2>",unsafe_allow_html=True)

def torna():
    if st.button("TORNA",use_container_width=True):
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
    opts=["Dashboard","Volontari","Mappa Postazioni","Eventi","DB Radio","Check-In","Brogliaccio","Consegna Radio","Emergenze","Backup"]
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
    st.success("Mappe ripristinate")
    c1,c2=st.columns(2)
    with c1:
        if st.button("VOLONTARI",use_container_width=True,key="d1"):
            st.session_state.menu="Volontari"
            st.rerun()
        if st.button("MAPPA",use_container_width=True,key="d2"):
            st.session_state.menu="Mappa Postazioni"
            st.rerun()
    with c2:
        if st.button("CHECK-IN",use_container_width=True,key="d5"):
            st.session_state.menu="Check-In"
            st.rerun()
        if st.button("BACKUP",use_container_width=True,key="d9"):
            st.session_state.menu="Backup"
            st.rerun()
    footer()

elif scelta=="Volontari":
    torna()
    st.markdown("## VOLONTARI - 5 MASCHERE")
    t1,t2,t3,t4,t5=st.tabs(["ANAGRAFICA","RESIDENZA","TESSERA","ABILIT","NOTE"])
    with t1:
        with st.form("f1"):
            a1=st.text_input("Nome *",key="a1")
            a2=st.text_input("Cognome *",key="a2")
            a3=st.text_input("CF",key="a3")
            a4=st.date_input("Nascita",value=date(1980,1,1),key="a4")
            if st.form_submit_button("SALVA"):
                st.session_state.s1_nome=a1
                st.session_state.s1_cogn=a2
                st.session_state.s1_dn=str(a4)
                st.success("OK 1")
    with t2:
        with st.form("f2"):
            b1=st.text_input("Via *",key="b1")
            b2=st.text_input("Comune *",value="Varese",key="b2")
            b3=st.text_input("Cell *",key="b3")
            if st.form_submit_button("SALVA"):
                st.session_state.s2_via=b1
                st.session_state.s2_com=b2
                st.session_state.s2_cell=b3
                st.success("OK 2")
    with t3:
        with st.form("f3"):
            c1x=st.text_input("Tessera",key="c1")
            c2x=st.text_input("Ruolo",value="Volontario",key="c3")
            if st.form_submit_button("SALVA"):
                st.session_state.s3_tess=c1x
                st.session_state.s3_ruolo=c2x
                st.success("OK 3")
    with t4:
        with st.form("f4"):
            d1=st.text_input("Patenti",value="B",key="d1")
            d2=st.text_input("Base",value="Si",key="d2")
            if st.form_submit_button("SALVA"):
                st.session_state.s4_pat=d1
                st.success("OK 4")
    with t5:
        with st.form("f5"):
            e2=st.text_area("Note",key="e2")
            btn=st.form_submit_button("SALVA COMPLETO",use_container_width=True)
            if btn:
                nome=st.session_state.get("s1_nome","")
                cogn=st.session_state.get("s1_cogn","")
                cell=st.session_state.get("s2_cell","")
                com=st.session_state.get("s2_com","")
                ruolo=st.session_state.get("s3_ruolo","")
                if nome and cell:
                    nuovo={}
                    nuovo["Nome