import streamlit as st
import pandas as pd
from datetime import date
from io import BytesIO
import os
import json
import base64
import hashlib

st.set_page_config(
    page_title="ANA Varese",
    page_icon="🟢",
    layout="wide"
)

st.markdown("""
<style>
.stApp{background:#e8f5e9!important;}
.main.block-container{
    background:white!important;
    border-radius:18px;
    padding:20px!important;
    padding-bottom:95px!important;
}
[data-testid="stSidebar"]{
    background:#a5d6a7!important;
    border-right:4px solid #2e7d32!important;
}
.stForm{
    background:#c8e6c9!important;
    border:3px solid #2e7d32!important;
    border-radius:15px!important;
}
.stButton>button{
    background:#2e7d32!important;
    color:white!important;
    font-weight:bold!important;
    min-height:50px!important;
    border-radius:10px!important;
}
.submask{
    border:2px solid #2e7d32;
    border-radius:12px;
    padding:15px;
    background:#f1f8e9;
    margin:10px 0px;
}
.footer-ezio{
    position: fixed;
    bottom: 5px;
    left: 10px;
    background: white;
    border: 2px solid #2e7d32;
    border-radius: 12px;
    padding: 5px 12px;
    display: flex;
    align-items: center;
    gap: 8px;
    z-index: 9999;
}
.footer-ezio img{
    width:45px;
    height:45px;
    border-radius:50%;
    border:2px solid #2e7d32;
}
.footer-ezio span{
    font-size:13px;
    font-weight:bold;
    color:#2e7d32;
}
</style>
""", unsafe_allow_html=True)

def load_json(f, default):
    try:
        if os.path.exists(f):
            with open(f,"r",encoding="utf-8") as fh:
                return json.load(fh)
    except:
        pass
    return default

def save_json(f,d):
    try:
        with open(f,"w",encoding="utf-8") as fh:
            json.dump(d,fh,ensure_ascii=False,indent=2)
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

def hash_pwd(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()

def footer_ezio():
    b64 = get_b64("ezio_whatsapp_round_transparent.png")
    if not b64:
        b64 = get_b64("ezio.png")
    if not b64:
        b64 = get_b64("ezio.jpg")
    if b64:
        img = "<img src='data:image/png;base64,"+b64+"'>"
    else:
        b64_logo = get_b64("logo.png")
        if b64_logo:
            img = "<img src='data:image/png;base64,"+b64_logo+"'>"
        else:
            img = "<div style='width:45px;height:45px;border-radius:50%;background:#2e7d32;color:white;display:flex;align-items:center;justify-content:center;font-weight:bold;'>EF</div>"
    st.markdown(
        "<div class='footer-ezio'>"+img+"<span>by Ezio F. vers. 1.0 2026</span></div>",
        unsafe_allow_html=True
    )

FILE_DATI="dati_volontari.json"
FILE_UTENTI="utenti.json"
COMUNI=["Varese","Busto Arsizio","Gallarate","Saronno","Venegono Superiore","Venegono Inferiore","Castiglione Olona","Lozza","Tradate","Malnate","Luino","Altro"]

if "dati" not in st.session_state:
    st.session_state.dati=[]
if "utenti" not in st.session_state:
    st.session_state.utenti=[]
if "menu_scelta" not in st.session_state:
    st.session_state.menu_scelta="Dashboard"
if "authenticated" not in st.session_state:
    st.session_state.authenticated=False
if "ruolo" not in st.session_state:
    st.session_state.ruolo=""
if "username" not in st.session_state:
    st.session_state.username=""

st.session_state.dati=load_json(FILE_DATI,[])
st.session_state.utenti=load_json(FILE_UTENTI,[])

if not st.session_state.utenti:
    st.session_state.utenti=[
        {
            "username":"admin",
            "password":hash_pwd("ana2024"),
            "ruolo":"Amministratore",
            "nome":"Admin"
        },
        {
            "username":"utente",
            "password":hash_pwd("utente2024"),
            "ruolo":"Utente",
            "nome":"Utente"
        }
    ]
    save_json(FILE_UTENTI,st.session_state.utenti)

def header_loghi():
    b64=get_b64("