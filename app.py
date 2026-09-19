import streamlit as st
import pandas as pd
from datetime import date
from io import BytesIO
import os, json, base64, hashlib

st.set_page_config(
    page_title="ANA Varese",
    layout="wide"
)

st.markdown("""
<style>
.stApp{background:#e8f5e9!important;}
.main{background:white!important;}
.footer{
 position:fixed;bottom:5px;left:10px;
 background:white;border:2px solid green;
 border-radius:12px;padding:5px 12px;
 display:flex;align-items:center;gap:8px;
 z-index:9999;
}
.footer img{width:45px;height:45px;border-radius:50%;}
.footer span{font-size:13px;font-weight:bold;color:green;}
.sub{border:2px solid green;border-radius:12px;padding:15px;background:#f1f8e9;margin:10px 0px;}
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
    b64=get_b64("ezio.png")
    if not b64:
        b64=get_b64("logo.png")
    if b64:
        img="<img src='data:image/png;base64,"+b64+"'>"
    else:
        img="<div style='width:45px;height:45px;background:green;border-radius:50%;color:white;display:flex;align-items:center;justify-content:center;'>EF</div>"
    st.markdown(
        "<div class='footer'>"+img+"<span>by Ezio F. vers. 1.0 2026</span></div>",
        unsafe_allow_html=True
    )

FILE_D="dati.json"
FILE_U="utenti.json"
COMUNI=["Varese","Busto","Gallarate","Saronno","Altro"]

if "dati" not in st.session_state:
    st.session_state.dati=[]
if "utenti" not in st.session_state:
    st.session_state.utenti=[]
if "menu" not in st.session_state:
    st.session_state.menu="Dashboard"
if "auth" not in st.session_state:
    st.session_state.auth=False
if "ruolo" not in st.session_state:
    st.session_state.ruolo=""

st.session_state.dati=load_json(FILE_D,[])
st.session_state.utenti=load_json(FILE_U,[])

if not st.session_state.utenti:
    st.session_state.utenti=[
        {"username":"admin","password":hash_pwd("ana2024"),"ruolo":"Admin"},
        {"username":"utente","password":hash_pwd("utente2024"),"ruolo":"Utente"}
    ]
    save_json(FILE_U,st.session_state.utenti)

def header():
    b64=get_b64("logo.png")
    if b64:
        h="<div style='text-align:center;background:#a5d6a7;padding:15px;border-radius:15px;border:3px solid green;'><img src='data:image/png;base64,"+b64+"' style='width:80px;border-radius:50%;'><h2 style='color:green;'>VOLONTARIATO Varese</h2></div>"
        st.markdown(h,unsafe_allow_html=True)
    else:
        st.markdown("<h2 style='text-align:center;color:green;'>VOLONTARIATO Varese</h2>",unsafe_allow_html=True)

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
                    st.session_state.ruolo=trov["ruolo"]
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
    sel=st.radio("Vai a",["Dashboard","Volontari","Backup"],index=0)
    if sel!=st.session_state.menu:
        st.session_state.menu=sel
        st.rerun()
    if st.button("LOGOUT",use_container_width=True):
        st.session_state.auth=False
        st.rerun()

scelta=st.session_state.menu

if scelta=="Dashboard":
    st.markdown("## DASHBOARD")
    if st.button("VOLONTARI",use_container_width=True,key="b1"):
        st.session_state.menu="Volontari"
        st.rerun()
    if st.button("BACKUP",use_container_width=True,key="b2"):
        st.session_state.menu="Backup"
        st.rerun()
    if st.button("LOGOUT",use_container_width=True,key="b3"):
        st.session_state.auth=False
        st.rerun()
    footer()

elif scelta=="Volontari":
    torna()
    st.markdown("## VOLONTARI - 5 SOTTOMASCHERE")
    t1,t2,t3,t4,t5=st.tabs(["1 ANAGRAFICA","2 RESIDENZA","3 TESSERA","4 ABILIT","5 NOTE"])

    with t1:
        st.markdown('<div class="sub">',unsafe_allow_html=True)
        st.markdown("### 1 - ANAGRAFICA")
        with st.form("f1"):
            c1,c2=st.columns(2)
            with c1:
                nome=st.text_input("Nome *",key="n1")
                cogn=st.text_input("Cognome *",key="n2")
                cf=st.text_input("CF",key="n3")
            with c2:
                dn=st.date_input("Data Nascita",value=date(1980,1,1),key="n4")
                ln=st.text_input("Luogo",key="n5")
                sx=st.selectbox("Sesso",["M","F"],key="n6")
            st.session_state["a1"]={"nome":nome,"cogn":cogn,"cf":cf,"dn":str(dn)}
            st.form_submit_button("SALVA TEMP 1")
        st.markdown('</div>',unsafe_allow_html=True)

    with t2:
        st.markdown('<div class="sub">',unsafe_allow_html=True)
        st.markdown("### 2 - RESIDENZA")
        with st.form("f2"):
            c1,c2=st.columns(2)
            with c1:
                via=st.text_input("Via *",key="r1")
                com=st.selectbox("Comune *",COMUNI,key="r2")
            with c2:
                cell=st.text_input("Cell *",key="r3")
                email=st.text_input("Email",key="r4")
            st.session_state["a2"]={"via":via,"com":com,"cell":cell,"email":email}
            st.form_submit_button("SALVA TEMP 2")
        st.markdown('</div>',unsafe_allow_html=True)

    with t3:
        st.markdown('<div class="sub">',unsafe_allow_html=True)
        st.markdown("### 3 - TESSERA")
        with st.form("f3"):
            c1,c2=st.columns(2)
            with c1:
                tess=st.text_input("Tessera",key="t1")
                sez=st.text_input("Sezione",value="Varese",key="t2")
            with c2:
                ruolo=st.selectbox("Ruolo",["Volontario","Caposquadra"],key="t3")
                ass=st.text_input("Associazione",value="ANA Varese",key="t4")
            st.session_state["a3"]={"tess":tess,"ruolo":ruolo,"ass":ass}
            st.form_submit_button("SALVA TEMP 3")
        st.markdown('</div>',unsafe_allow_html=True)

    with t4:
        st.markdown('<div class="sub">',unsafe_allow_html=True)
        st.markdown("### 4 - ABILITAZIONI")
        with st.form("f4"):
            pat=st.multiselect("Patenti",["A","B","C"],key="ab1")
            base=st.selectbox("Base PC",["Si","No"],key="ab2")
            st.session_state["a4"]={"pat":",".join(pat),"base":base}
            st.form_submit_button("SALVA TEMP 4")
        st.markdown('</div>',unsafe_allow_html=True)

    with t5:
        st.markdown('<div class="sub">',unsafe_allow_html=True)
        st.markdown("### 5 - NOTE")
        with st.form("f5"):
            note=st.text_area("Note",key="ab3")
            btn=st.form_submit_button("SALVA COMPLETO",use_container_width=True)
            if btn:
                a1=st.session_state.get("a1",{})
                a2=st.session_state.get("a2",{})
                a3=st.session_state.get("a3",{})
                if a1.get("nome") and a1.get("cogn") and a2.get("cell"):
                    nuovo={
                        "Nome":a1.get("nome")+" "+a1.get("cogn"),
                        "Cell":a2.get("cell"),
                        "Comune":a2.get("com"),
                        "Ruolo":a3.get("ruolo"),
                        "Ass":a3.get("ass"),
                        "Note":note
                    }
                    st.session_state.dati.append(nuovo)
                    save_json(FILE_D,st.session_state.dati)
                    st.success("Salvato")
                    st.rerun()
        st.markdown('</div>',unsafe_allow_html=True)

    if st.session_state.dati:
        st.dataframe(pd.DataFrame(st.session_state.dati),use_container_width=True)

else:
    torna()
    st.markdown("## "+scelta)