import streamlit as st
import pandas as pd
from datetime import date, datetime
from io import BytesIO
import os, json, base64, tempfile, requests, hashlib

st.set_page_config(page_title="ANA Varese", page_icon="🟢", layout="wide")

st.markdown("""
<style>
.stApp{background:#e8f5e9!important;}
.main.block-container{background:white!important;border-radius:18px;padding:20px!important;}
[data-testid="stSidebar"]{background:#a5d6a7!important;border-right:4px solid #2e7d32!important;}
.stForm{background:#c8e6c9!important;border:3px solid #2e7d32!important;border-radius:15px!important;}
.stButton>button{background:#2e7d32!important;color:white!important;font-weight:bold!important;min-height:45px!important;border-radius:10px!important;}
.dashboard-card{border:3px solid #2e7d32;border-radius:15px;padding:15px;background:#e8f5e9;text-align:center;margin:10px;min-height:180px;}
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
def img_to_b64(file):
    try:
        return base64.b64encode(file.getvalue()).decode()
    except:
        return ""
def trova_b64_logo(nome, libreria):
    for ic in libreria:
        if ic.get("nome")==nome and ic.get("b64"):
            return ic.get("b64")
    return None
def salva_icona_temp(b64, nome):
    try:
        data=base64.b64decode(b64)
        tmp=os.path.join(tempfile.gettempdir(), f"icon_{nome}.png")
        with open(tmp,"wb") as f:
            f.write(data)
        return tmp
    except:
        return None
def reverse_geocode(lat, lon):
    try:
        url=f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=18&addressdetails=1"
        r=requests.get(url, headers={"User-Agent":"ANA-Varese-App"}, timeout=5)
        if r.status_code==200:
            data=r.json()
            addr=data.get("address",{})
            road=addr.get("road","") or addr.get("pedestrian","") or ""
            house=addr.get("house_number","")
            via=f"{road} {house}".strip()
            if not via:
                via=data.get("display_name","").split(",")[0]
            comune=addr.get("city","") or addr.get("town","") or addr.get("village","") or ""
            return via, comune
    except:
        pass
    return "", ""
def hash_pwd(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()

FILE_DATI="dati_volontari.json"
FILE_POST="postazioni.json"
FILE_ICONE="libreria_icone_condivisa.json"
FILE_UTENTI="utenti.json"
FILE_EVENTI="eventi.json"
FILE_RADIO="db_radio.json"
FILE_CHECKIN="checkin.json"
FILE_BROGLIACCIO="brogliaccio.json"
FILE_CONSEGNA="consegna_radio.json"
FILE_EMERGENZE="emergenze.json"

COMUNI=["Varese","Busto Arsizio","Gallarate","Saronno","Venegono Superiore","Venegono Inferiore","Castiglione Olona","Lozza","Tradate","Malnate","Luino","Altro"]

for k,v in [("dati",[]),("postazioni",[]),("icone_lib",[]),("utenti",[]),("eventi",[]),("radio",[]),("checkin",[]),("brogliaccio",[]),("consegna",[]),("emergenze",[]),("menu_scelta","Dashboard"),("map_lat",45.8205),("map_lon",8.8250),("map_via",""),("map_comune","Varese"),("map_logo","Default"),("authenticated",False),("ruolo",""),("username","")]:
    if k not in st.session_state:
        st.session_state[k]=v

if not st.session_state.dati: st.session_state.dati=load_json(FILE_DATI,[])
if not st.session_state.postazioni: st.session_state.postazioni=load_json(FILE_POST,[])
if not st.session_state.icone_lib: st.session_state.icone_lib=load_json(FILE_ICONE,[])
if not st.session_state.utenti: st.session_state.utenti=load_json(FILE_UTENTI,[])
if not st.session_state.eventi: st.session_state.eventi=load_json(FILE_EVENTI,[])
if not st.session_state.radio: st.session_state.radio=load_json(FILE_RADIO,[])
if not st.session_state.checkin: st.session_state.checkin=load_json(FILE_CHECKIN,[])
if not st.session_state.brogliaccio: st.session_state.brogliaccio=load_json(FILE_BROGLIACCIO,[])
if not st.session_state.consegna: st.session_state.consegna=load_json(FILE_CONSEGNA,[])
if not st.session_state.emergenze: st.session_state.emergenze=load_json(FILE_EMERGENZE,[])

if not st.session_state.utenti:
    st.session_state.utenti=[
        {"username":"admin","password":hash_pwd("ana2024"),"ruolo":"Amministratore","nome":"Admin"},
        {"username":"utente","password":hash_pwd("utente2024"),"ruolo":"Utente","nome":"Utente"}
    ]
    save_json(FILE_UTENTI,st.session_state.utenti)

def header_loghi():
    b64=get_b64("logo.png")
    if b64:
        st.markdown(f"<div style='display:flex;justify-content:center;align-items:center;gap:25px;background:#a5d6a7;padding:15px;border-radius:15px;border:3px solid #2e7d32;'><img src='data:image/png;base64,{b64}' style='width:80px;height:80px;border-radius:50%;'><h2 style='color:#0e7a3d;margin:0;text-align:center;'>VOLONTARIATO<br>Sezione di Varese</h2><img src='data:image/png;base64,{b64}' style='width:80px;height:80px;border-radius:50%;'></div>", unsafe_allow_html=True)
    else:
        st.markdown("<h2 style='text-align:center;color:#0e7a3d;'>VOLONTARIATO Sezione di Varese</h2>", unsafe_allow_html=True)

def torna_dashboard():
    if st.button("TORNA A DASHBOARD MENU COMPLETO",use_container_width=True):
        st.session_state.menu_scelta="Dashboard"
        st.rerun()

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
    st.stop()

header_loghi()
st.divider()

with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png",width=80)
    st.markdown(f"Ciao {st.session_state.username} | {st.session_state.ruolo}")
    st.markdown("### MENU COMPLETO FORM")
    if st.session_state.ruolo=="Amministratore":
        opzioni=["Dashboard","Volontari","Mappa Postazioni","Eventi","DB Radio","Check-In","Brogliaccio","Consegna Radio","Emergenze","Gestione Loghi","Gestione Utenti","Backup"]
    else:
        opzioni=["Dashboard","Volontari","Mappa Postazioni","Eventi","DB Radio","Check-In","Brogliaccio","Consegna Radio","Emergenze","Backup"]
    sel=st.radio("Vai a",opzioni,index=0)
    if sel!=st.session_state.menu_scelta:
        st.session_state.menu_scelta=sel
        st.rerun()
    st.divider()
    st.metric("Volontari",len(st.session_state.dati))
    st.metric("Postazioni",len(st.session_state.postazioni))
    st.metric("Emergenze",len(st.session_state.emergenze))
    if st.button("LOGOUT",use_container_width=True):
        st.session_state.authenticated=False
        st.rerun()

scelta=st.session_state.menu_scelta
MIME="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

if scelta=="Dashboard":
    st.markdown("## DASHBOARD - ELENCO MENU COMPLETO")
    c1,c2=st.columns([3,1])
    with c1:
        st.success(f"Benvenuto {st.session_state.username} | Ruolo: {st.session_state.ruolo}")
    with c2:
        if st.button("LOGOUT DALLA DASHBOARD",use_container_width=True,type="primary"):
            st.session_state.authenticated=False
            st.rerun()
    st.divider()
    st.markdown("### MENU RAPIDO")
    mr1,mr2,mr3,mr4,mr5,mr6=st.columns(6)
    with mr1:
        if st.button("Volontari",use_container_width=True):
            st.session_state.menu_scelta="Volontari"; st.rerun()
    with mr2:
        if st.button("Mappa",use_container_width=True):
            st.session_state.menu_scelta="Mappa Postazioni"; st.rerun()
    with mr3:
        if st.button("Eventi",use_container_width=True):
            st.session_state.menu_scelta="Eventi"; st.rerun()
    with mr4:
        if st.button("DB Radio",use_container_width=True):
            st.session_state.menu_scelta="DB Radio"; st.rerun()
    with mr5:
        if st.button("Emergenze",use_container_width=True):
            st.session_state.menu_scelta="Emergenze"; st.rerun()
    with mr6:
        if st.button("Check-In",use_container_width=True):
            st.session_state.menu_scelta="Check-In"; st.rerun()
    st.divider()
    c1,c2,c3=st.columns(3)
    with c1:
        st.markdown('<div class="dashboard-card">',unsafe_allow_html=True)
        st.markdown("### FORM 1: VOLONTARI"); st.metric("Totale",len(st.session_state.dati))
        if st.button("APRI VOLONTARI",key="dash_vol",use_container_width=True,type="primary"):
            st.session_state.menu_scelta="Volontari"; st.rerun()
        st.markdown('</div>',unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="dashboard-card">',unsafe_allow_html=True)
        st.markdown("### FORM 2: MAPPA POSTAZIONI"); st.write("Tabella + Anteprima TUTTE 15x15 + Via")
        st.metric("Totale",len(st.session_state.postazioni))
        if st.button("APRI MAPPA",key="dash_mappa",use_container_width=True,type="primary"):
            st.session_state.menu_scelta="Mappa Postazioni"; st.rerun()
        st.markdown('</div>',unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="dashboard-card">',unsafe_allow_html=True)
        st.markdown("### FORM 3: EVENTI"); st.metric("Totale",len(st.session_state.eventi))
        if st.button("APRI EVENTI",key="dash_eventi",use_container_width=True,type="primary"):
            st.session_state.menu_scelta="Eventi"; st.rerun()
        st.markdown('</div>',unsafe_allow_html=True)
    c4,c5,c6=st.columns(3)
    with c4:
        st.markdown('<div class="dashboard-card">',unsafe_allow_html=True)
        st.markdown("### FORM 4: DB RADIO"); st.metric("Totale",len(st.session_state.radio))
        if st.button("APRI DB RADIO",key="dash_radio",use_container_width=True,type="primary"):
            st.session_state.menu_scelta="DB Radio"; st.rerun()
        st.markdown('</div>',unsafe_allow_html=True)
    with c5:
        st.markdown('<div class="dashboard-card">',unsafe_allow_html=True)
        st.markdown("### FORM 5: EMERGENZE"); st.metric("Totale",len(st.session_state.emergenze))
        if st.button("APRI EMERGENZE",key="dash_emerg",use_container_width=True,type="primary"):
            st.session_state.menu_scelta="Emergenze"; st.rerun()
        st.markdown('</div>',unsafe_allow_html=True)
    with c6:
        st.markdown('<div class="dashboard-card">',unsafe_allow_html=True)
        st.markdown("### FORM 6: CHECK-IN"); st.metric("Totale",len(st.session_state.checkin))
        if st.button("APRI CHECK-IN",key="dash_check",use_container_width=True,type="primary"):
            st.session_state.menu_scelta="Check-In"; st.rerun()
        st.markdown('</div>',unsafe_allow_html=True)
    c7,c8,c9=st.columns(3)
    with c7:
        st.markdown('<div class="dashboard-card">',unsafe_allow_html=True)
        st.markdown("### FORM 7: BROGLIACCIO"); st.metric("Totale",len(st.session_state.brogliaccio))
        if st.button("APRI BROGLIACCIO",key="dash_brog",use_container_width=True,type="primary"):
            st.session_state.menu_scelta="Brogliaccio"; st.rerun()
        st.markdown('</div>',unsafe_allow_html=True)
    with c8:
        st.markdown('<div class="dashboard-card">',unsafe_allow_html=True)
        st.markdown("### FORM 8: CONSEGNA RADIO"); st.metric("Totale",len(st.session_state.consegna))
        if st.button("APRI CONSEGNA",key="dash_consegna",use_container_width=True,type="primary"):
            st.session_state.menu_scelta="Consegna Radio"; st.rerun()
        st.markdown('</div>',unsafe_allow_html=True)
    with c9:
        st.markdown('<div class="dashboard-card">',unsafe_allow_html=True)
        st.markdown("### FORM 9: BACKUP")
        if st.button("APRI BACKUP",key="dash_backup",use_container_width=True,type="primary"):
            st.session_state.menu_scelta="Backup"; st.rerun()
        st.markdown('</div>',unsafe_allow_html=True)

elif scelta=="Volontari":
    torna_dashboard()
    st.markdown("## FORM VOLONTARI")
    with st.form("form_vol"):
        c1,c2=st.columns(2)
        with c1:
            nome=st.text_input("Nome *"); cognome=st.text_input("Cognome *"); cell=st.text_input("Cellulare *")
        with c2:
            assoc=st.text_input("Associazione *",value="ANA Varese"); comune=st.selectbox("Comune",COMUNI,index=0); ruolo=st.selectbox("Ruolo *",["Volontario","Caposquadra","Coordinatore"])
        if st.form_submit_button("SALVA VOLONTARIO",use_container_width=True,type="primary"):
            if nome and cognome and cell and assoc:
                st.session_state.dati.append({"Nome":f"{nome} {cognome}","Associazione":assoc,"Cellulare":cell,"Comune":comune,"Ruolo":ruolo})
                save_json(FILE_DATI,st.session_state.dati); st.success(f"Salvato {nome} {cognome}"); st.rerun()
    if st.session_state.dati:
        st.dataframe(pd.DataFrame(st.session_state.dati),use_container_width=True)

elif scelta=="Mappa Postazioni":
    torna_dashboard()
    st.markdown