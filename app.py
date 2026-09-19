import streamlit as st
import pandas as pd
from datetime import date, datetime
from io import BytesIO
import os, json, base64, hashlib

st.set_page_config(page_title="ANA Varese", page_icon="🟢", layout="wide")

st.markdown("""
<style>
.stApp{background:#e8f5e9!important;}
.main.block-container{background:white!important;border-radius:18px;padding:20px!important;padding-bottom:95px!important;}
[data-testid="stSidebar"]{background:#a5d6a7!important;border-right:4px solid #2e7d32!important;}
.stForm{background:#c8e6c9!important;border:3px solid #2e7d32!important;border-radius:15px!important;}
.stButton>button{background:#2e7d32!important;color:white!important;font-weight:bold!important;min-height:50px!important;border-radius:10px!important;font-size:16px!important;}
.submask{border:2px solid #2e7d32;border-radius:12px;padding:15px;background:#f1f8e9;margin:10px 0px;}
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
    box-shadow: 2px 2px 8px rgba(0,0,0,0.2);
}
.footer-ezio img{width:45px;height:45px;border-radius:50%;border:2px solid #2e7d32;}
.footer-ezio span{font-size:13px;font-weight:bold;color:#2e7d32;}
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
        img_html = "<img src='data:image/png;base64,"+b64+"'>"
    else:
        b64_logo = get_b64("logo.png")
        if b64_logo:
            img_html = "<img src='data:image/png;base64,"+b64_logo+"'>"
        else:
            img_html = "<div style='width:45px;height:45px;border-radius:50%;background:#2e7d32;color:white;display:flex;align-items:center;justify-content:center;font-weight:bold;'>EF</div>"
    st.markdown("<div class='footer-ezio'>"+img_html+"<span>by Ezio F. vers. 1.0 2026</span></div>", unsafe_allow_html=True)

FILE_DATI="dati_volontari.json"
FILE_UTENTI="utenti.json"
COMUNI=["Varese","Busto Arsizio","Gallarate","Saronno","Venegono Superiore","Venegono Inferiore","Castiglione Olona","Lozza","Tradate","Malnate","Luino","Altro"]

for k,v in [("dati",[]),("utenti",[]),("menu_scelta","Dashboard"),("authenticated",False),("ruolo",""),("username","")]:
    if k not in st.session_state:
        st.session_state[k]=v

if not st.session_state.dati: st.session_state.dati=load_json(FILE_DATI,[])
if not st.session_state.utenti: st.session_state.utenti=load_json(FILE_UTENTI,[])

if not st.session_state.utenti:
    st.session_state.utenti=[
        {"username":"admin","password":hash_pwd("ana2024"),"ruolo":"Amministratore","nome":"Admin"},
        {"username":"utente","password":hash_pwd("utente2024"),"ruolo":"Utente","nome":"Utente"}
    ]
    save_json(FILE_UTENTI,st.session_state.utenti)

def header_loghi():
    b64=get_b64("logo.png")
    if b64:
        st.markdown("<div style='display:flex;justify-content:center;align-items:center;gap:25px;background:#a5d6a7;padding:15px;border-radius:15px;border:3px solid #2e7d32;'><img src='data:image/png;base64,"+b64+"' style='width:80px;height:80px;border-radius:50%;'><h2 style='color:#0e7a3d;margin:0;text-align:center;'>VOLONTARIATO<br>Sezione di Varese</h2><img src='data:image/png;base64,"+b64+"' style='width:80px;height:80px;border-radius:50%;'></div>", unsafe_allow_html=True)
    else:
        st.markdown("<h2 style='text-align:center;color:#0e7a3d;'>VOLONTARIATO Sezione di Varese</h2>", unsafe_allow_html=True)

def torna_dashboard():
    if st.button("TORNA A DASHBOARD",use_container_width=True):
        st.session_state.menu_scelta="Dashboard"
        st.rerun()

# PAGINA LOGIN - CON FOTO IN BASSO A SX
if not st.session_state.authenticated:
    header_loghi()
    st.markdown("## LOGIN")
    st.info("Admin: admin / ana2024 | Utente: utente / utente2024")
    c1,c2,c3=st.columns([1,2,1])
    with c2:
        with st.form("login"):
            u=st.text_input("Username",value="admin")
            p=st.text_input("Password",type="password",value="ana2024")
            if st.form_submit_button("ACCEDI",use_container_width=True,type="primary"):
                pwd_hash=hash_pwd(p)
                trovato=None
                for ut in st.session_state.utenti:
                    if ut["username"]==u and ut["password"]==pwd_hash:
                        trovato=ut
                        break
                if trovato:
                    st.session_state.authenticated=True
                    st.session_state.ruolo=trovato["ruolo"]
                    st.session_state.username=trovato["username"]
                    st.rerun()
                else:
                    st.error("Username o password errati")
    footer_ezio()
    st.stop()

header_loghi()
st.divider()

with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png",width=80)
    st.markdown("Ciao "+st.session_state.username+" | "+st.session_state.ruolo)
    opzioni=["Dashboard","Volontari","Mappa Postazioni","Eventi","DB Radio","Check-In","Brogliaccio","Consegna Radio","Emergenze","Backup"]
    sel=st.radio("Vai a",opzioni,index=0)
    if sel!=st.session_state.menu_scelta:
        st.session_state.menu_scelta=sel
        st.rerun()
    if st.button("LOGOUT",use_container_width=True):
        st.session_state.authenticated=False
        st.rerun()

scelta=st.session_state.menu_scelta
MIME="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

if scelta=="Dashboard":
    st.markdown("## DASHBOARD")
    c1,c2=st.columns([3,1])
    with c1:
        st.success("Benvenuto "+st.session_state.username+" | Ruolo: "+st.session_state.ruolo)
    with c2:
        if st.button("LOGOUT",use_container_width=True,type="primary",key="logout_dash"):
            st.session_state.authenticated=False
            st.rerun()
    st.divider()
    st.markdown("### MENU RAPIDO - TASTI")
    r1c1, r1c2, r1c3, r1c4 = st.columns(4)
    with r1c1:
        if st.button("VOLONTARI", use_container_width=True, key="rap_vol"):
            st.session_state.menu_scelta="Volontari"
            st.rerun()
    with r1c2:
        if st.button("MAPPA POSTAZIONI", use_container_width=True, key="rap_mappa"):
            st.session_state.menu_scelta="Mappa Postazioni"
            st.rerun()
    with r1c3:
        if st.button("EVENTI", use_container_width=True, key="rap_eventi"):
            st.session_state.menu_scelta="Eventi"
            st.rerun()
    with r1c4:
        if st.button("DB RADIO", use_container_width=True, key="rap_radio"):
            st.session_state.menu_scelta="DB Radio"
            st.rerun()
    r2c1, r2c2, r2c3, r2c4 = st.columns(4)
    with r2c1:
        if st.button("CHECK-IN", use_container_width=True, key="rap_check"):
            st.session_state.menu_scelta="Check-In"
            st.rerun()
    with r2c2:
        if st.button("BROGLIACCIO", use_container_width=True, key="rap_brog"):
            st.session_state.menu_scelta="Brogliaccio"
            st.rerun()
    with r2c3:
        if st.button("CONSEGNA RADIO", use_container_width=True, key="rap_consegna"):
            st.session_state.menu_scelta="Consegna Radio"
            st.rerun()
    with r2c4:
        if st.button("EMERGENZE", use_container_width=True, key="rap_emerg"):
            st.session_state.menu_scelta="Emergenze"
            st.rerun()
    r3c1, r3c2, r3c3, r3c4 = st.columns(4)
    with r3c1:
        if st.button("BACKUP", use_container_width=True, key="rap_backup"):
            st.session_state.menu_scelta="Backup"
            st.rerun()
    footer_ezio()

elif scelta=="Volontari":
    torna_dashboard()
    st.markdown("## FORM VOLONTARI - 5 SOTTOMASCHERE")
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["1: ANAGRAFICA","2: RESIDENZA E CONTATTI","3: TESSERAMENTO ANA","4: ABILITAZIONI E CORSI","5: DISPONIBILITA E NOTE"])

    with tab1:
        st.markdown('<div class="submask">', unsafe_allow_html=True)
        st.markdown("### SOTTOMASCHERA 1 - DATI ANAGRAFICI")
        with st.form("form_anagrafica"):
            c1,c2=st.columns(2)
            with c1:
                nome=st.text_input("Nome *",key="vol_nome")
                cognome=st.text_input("Cognome *",key="vol_cognome")
                cf=st.text_input("Codice Fiscale",key="vol_cf")
                data_nascita=st.date_input("Data di Nascita",value=date(1980,1,1),key="vol_datanasc")
            with c2:
                luogo_nascita=st.text_input("Luogo di Nascita",key="vol_luogonasc")
                sesso=st.selectbox("Sesso",["M","F"],key="vol_sesso")
                stato_civile=st.selectbox("Stato Civile",["Celibe/Nubile","Coniugato/a","Vedovo/a","Separato/a"],key="vol_statociv")
                gruppo_sanguigno=st.selectbox("Gruppo Sanguigno",["Non noto","A+","A-","B+","B-","AB+","AB-","0+","0-"],key="vol_grupposang")
            st.session_state["tmp_anagrafica"]={"nome":nome,"cognome":cognome,"cf":cf,"data_nascita":str(data_nascita),"luogo_nascita":luogo_nascita,"sesso":sesso,"stato_civile":stato_civile,"gruppo_sanguigno":gruppo_sanguigno}
            st.form_submit_button("SALVA ANAGRAFICA TEMP")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="submask">', unsafe_allow_html=True)
        st.markdown("### SOTTOMASCHERA 2 - RESIDENZA E CONTATTI")
        with st.form("form_residenza"):
            c1,c2=st.columns(2)
            with c1:
                via_res=st.text_input("Via e Numero Civico *",key="vol_via")
                comune_res=st.selectbox("Comune Residenza *",COMUNI,index=0,key="vol_comune_res")
                cap=st.text_input("CAP",value="21100",key="vol_cap")
                provincia=st.text_input("Provincia",value="VA",key="vol_prov")
            with c2:
                cell=st.text_input("Cellulare *",key="vol_cell")
                tel_fisso=st.text_input("Telefono Fisso",key="vol_telfisso")
                email=st.text_input("Email",key="vol_email")
                contatto_emerg=st.text_input("Contatto Emergenza - Nome e Tel",key="vol_cont_emerg")
            st.session_state["tmp_residenza"]={"via":via_res,"comune":comune_res,"cap":cap,"provincia":provincia,"cell":cell,"tel_fisso":tel_fisso,"email":email,"contatto_emerg":contatto_emerg}
            st.form_submit_button("SALVA RESIDENZA TEMP")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab3:
        st.markdown('<div class="submask">', unsafe_allow_html=True)
        st.markdown("### SOTTOMASCHERA 3 - TESSERAMENTO ANA")
        with st.form("form_tesseramento"):
            c1,c2=st.columns(2)
            with c1:
                tessera_ana=st.text_input("Numero Tessera ANA",key="vol_tessera")
                sezione=st.text_input("Sezione ANA",value="Varese",key="vol_sezione")
                gruppo=st.text_input("Gruppo",key="vol_gruppo")
                anno_iscrizione=st.number_input("Anno Iscrizione ANA",min_value=1950,max_value=2030,value=2020,key="vol_annoisc")
            with c