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
if "utenti" not in st.session_state:
    st.session_state.utenti=[]
if "menu" not in st.session_state:
    st.session_state.menu="Dashboard"
if "auth" not in st.session_state:
    st.session_state.auth=False

st.session_state.dati=load_json(FD,[])
st.session_state.utenti=load_json(FU,[])
st.session_state.post=load_json(FP,[])
st.session_state.eventi=load_json(FE,[])
st.session_state.radio=load_json(FR,[])
st.session_state.check=load_json(FC,[])
st.session_state.brog=load_json(FB,[])
st.session_state.consegna=load_json(FO,[])
st.session_state.emerg=load_json(FM,[])

if not st.session_state.utenti:
    st.session_state.utenti=[
        {"username":"admin","password":hash_pwd("ana2024")},
        {"username":"utente","password":hash_pwd("utente2024")}
    ]
    save_json(FU,st.session_state.utenti)

def header():
    b=get_b64("logo.png")
    if b:
        h="<div style='text-align:center;background:#a5d6a7;padding:15px;border-radius:15px;border:3px solid #2e7d32;'><img src='data:image/png;base64,"+b+"' style='width:80px;border-radius:50%;'><h2 style='color:#0e7a3d;'>VOLONTARIATO<br>Sezione di Varese</h2></div>"
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
    st.markdown("## DASHBOARD - MENU RAPIDO")
    st.success("Benvenuto")
    c1,c2,c3,c4=st.columns(4)
    with c1:
        if st.button("VOLONTARI",use_container_width=True,key="d1"):
            st.session_state.menu="Volontari"
            st.rerun()
    with c2:
        if st.button("MAPPA POSTAZIONI",use_container_width=True,key="d2"):
            st.session_state.menu="Mappa Postazioni"
            st.rerun()
    with c3:
        if st.button("EVENTI",use_container_width=True,key="d3"):
            st.session_state.menu="Eventi"
            st.rerun()
    with c4:
        if st.button("DB RADIO",use_container_width=True,key="d4"):
            st.session_state.menu="DB Radio"
            st.rerun()
    c1,c2,c3,c4=st.columns(4)
    with c1:
        if st.button("CHECK-IN",use_container_width=True,key="d5"):
            st.session_state.menu="Check-In"
            st.rerun()
    with c2:
        if st.button("BROGLIACCIO",use_container_width=True,key="d6"):
            st.session_state.menu="Brogliaccio"
            st.rerun()
    with c3:
        if st.button("CONSEGNA RADIO",use_container_width=True,key="d7"):
            st.session_state.menu="Consegna Radio"
            st.rerun()
    with c4:
        if st.button("EMERGENZE",use_container_width=True,key="d8"):
            st.session_state.menu="Emergenze"
            st.rerun()
    if st.button("BACKUP",use_container_width=True,key="d9"):
        st.session_state.menu="Backup"
        st.rerun()
    footer()

elif scelta=="Volontari":
    torna()
    st.markdown("## VOLONTARI - 5 SOTTOMASCHERE")
    t1,t2,t3,t4,t5=st.tabs(["1 ANAGRAFICA","2 RESIDENZA","3 TESSERA","4 ABILITAZIONI","5 NOTE"])
    with t1:
        st.markdown('<div class="sub">',unsafe_allow_html=True)
        with st.form("f1"):
            a1=st.text_input("Nome *",key="a1")
            a2=st.text_input("Cognome *",key="a2")
            a3=st.text_input("Codice Fiscale",key="a3")
            a4=st.date_input("Data Nascita",value=date(1980,1,1),key="a4")
            a5=st.text_input("Luogo Nascita",key="a5")
            if st.form_submit_button("SALVA ANAGRAFICA"):
                st.session_state.s1_nome=a1
                st.session_state.s1_cogn=a2
                st.session_state.s1_cf=a3
                st.session_state.s1_dn=str(a4)
                st.session_state.s1_ln=a5
                st.success("Salvato Anagrafica")
        st.markdown('</div>',unsafe_allow_html=True)
    with t2:
        st.markdown('<div class="sub">',unsafe_allow_html=True)
        with st.form("f2"):
            b1=st.text_input("Via e Numero *",key="b1")
            b2=st.text_input("Comune Residenza *",value="Varese",key="b2")
            b3=st.text_input("CAP",value="21100",key="b3")
            b4=st.text_input("Cellulare *",key="b4")
            b5=st.text_input("Email",key="b5")
            if st.form_submit_button("SALVA RESIDENZA"):
                st.session_state.s2_via=b1
                st.session_state.s2_com=b2
                st.session_state.s2_cap=b3
                st.session_state.s2_cell=b4
                st.session_state.s2_email=b5
                st.success("Salvato Residenza")
        st.markdown('</div>',unsafe_allow_html=True)
    with t3:
        st.markdown('<div class="sub">',unsafe_allow_html=True)
        with st.form("f3"):
            c1x=st.text_input("Tessera ANA",key="c1")
            c2x=st.text_input("Sezione",value="Varese",key="c2")
            c3x=st.text_input("Gruppo",key="c3")
            c4x=st.text_input("Ruolo PC",value="Volontario",key="c4")
            c5x=st.text_input("Associazione",value="ANA Varese",key="c5")
            if st.form_submit_button("SALVA TESSERA"):
                st.session_state.s3_tess=c1x
                st.session_state.s3_sez=c2x
                st.session_state.s3_gruppo=c3x
                st.session_state.s3_ruolo=c4x
                st.session_state.s3_ass=c5x
                st.success("Salvato Tessera")
        st.markdown('</div>',unsafe_allow_html=True)
    with t4:
        st.markdown('<div class="sub">',unsafe_allow_html=True)
        with st.form("f4"):
            d1=st.text_input("Patenti",value="B",key="d1")
            d2=st.text_input("Corso Base PC",value="Si",key="d2")
            d3=st.text_input("Corso Radio",value="Base",key="d3")
            d4=st.text_input("Altre Abilitazioni",key="d4")
            if st.form_submit_button("SALVA ABILITAZIONI"):
                st.session_state.s4_pat=d1
                st.session_state.s4_base=d2
                st.session_state.s4_radio=d3
                st.session_state.s4_altro=d4
                st.success("Salvato Abilitazioni")
        st.markdown('</div>',unsafe_allow_html=True)
    with t5:
        st.markdown('<div class="sub">',unsafe_allow_html=True)
        with st.form("f5"):
            e1=st.text_input("Disponibilita",value="Sab-Dom",key="e1")
            e2=st.text_input("Fascia Oraria",value="H24",key="e2")
            e3=st.text_area("Note Aggiuntive",key="e3")
            btn=st.form_submit_button("SALVA VOLONTARIO COMPLETO",use_container_width=True)
            if btn:
                nome=""
                cogn=""
                cell=""
                com=""
                ruolo=""
                ass=""
                if "s1_nome" in st.session_state:
                    nome=st.session_state.s1_nome
                if "s1_cogn" in st.session_state:
                    cogn=st.session_state.s1_cogn
                if "s2_cell" in st.session_state:
                    cell=st.session_state.s2_cell
                if "s2_com" in st.session_state:
                    com=st.session_state.s2_com
                if "s3_ruolo" in st.session_state:
                    ruolo=st.session_state.s3_ruolo
                if "s3_ass" in st.session_state:
                    ass=st.session_state.s3_ass
                if nome and cell:
                    nuovo={}
                    nuovo["Nome"]=nome+" "+cogn
                    nuovo["Cellulare"]=cell
                    nuovo["Comune"]=com
                    nuovo["Ruolo"]=ruolo
                    nuovo["Associazione"]=ass
                    nuovo["Note"]=e3
                    st.session_state.dati.append(nuovo)
                    save_json(FD,st.session_state.dati)
                    st.success("Volontario salvato completo")
                    st.rerun()
                else:
                    st.error("Compila Nome e Cellulare")
        st.markdown('</div>',unsafe_allow_html=True)
    if st.session_state.dati:
        st.divider()
        st.dataframe(pd.DataFrame(st.session_state.dati),use_container_width=True)
        out=BytesIO()
        pd.DataFrame(st.session_state.dati).to_excel(out,index=False,engine="openpyxl")
        st.download_button("SCARICA EXCEL VOLONTARI",out.getvalue(),file_name="VOLONTARI.xlsx",mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",use_container_width=True)

elif scelta=="Mappa Postazioni":
    torna()
    st.markdown("## MAPPA POSTAZIONI - FORM COMPLETO COME PRIMA")
    st.info("Form che avevamo fatto alle 12:00 - ripristinato")
    with st.form("form_mappa"):
        st.markdown("### DATI POSTAZIONE")
        col1,col2=st.columns(2)
        with col1:
            m1=st.text_input("Nome Postazione *",key="m1")
            m2=st.text_input("Comune *",value="Varese",key="m2")
            m3=st.text_input("Via / Localita *",key="m3")
            m4=st.text_input("CAP",value="21100",key="m4")
        with col2:
            m5=st.text_input("Latitudine",value="45.8205",key="m5")
            m6=st.text_input("Longitudine",value="8.8250",key="m6")
            m7=st.text_input("Tipo Postazione",value="Presidio",key="m7")
            m8=st.text_input("Responsabile",key="m8")
        m9=st.text_area("Note Postazione",key="m9")
        m10=st.text_input("Attrezzature Presenti",key="m10")
        ok=st.form_submit_button("SALVA POSTAZIONE",use_container_width=True)
        if ok and m1:
            nuovo={}
            nuovo["Postazione"]=m1
            nuovo["Comune"]=m2
            nuovo["Via"]=m3
            nuovo["Lat"]=m5
            nuovo["Lon"]=m6
            nuovo["Tipo"]=m7
            nuovo["Resp"]=m8
            nuovo["Note"]=m9
            st.session_state.post.append(nuovo)
            save_json(FP,st.session_state.post)
            st.success("Postazione salvata")
            st.rerun()
    if st.session_state.post:
        st.divider()
        st.markdown("### ELENCO POSTAZIONI")
        st.dataframe(pd.DataFrame(st.session_state.post),use_container_width=True)
        out=BytesIO()
        pd.DataFrame(st.session_state.post).to_excel(out,index=False,engine="openpyxl")
        st.download_button("SCARICA EXCEL MAPPA",out.getvalue(),file_name="MAPPA_POSTAZIONI.xlsx",mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",use_container_width=True)