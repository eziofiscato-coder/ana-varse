import streamlit as st
import pandas as pd
from datetime import date
from io import BytesIO
import os, json, base64, tempfile, requests, hashlib

st.set_page_config(page_title="ANA Varese", page_icon="🟢", layout="wide")

st.markdown("""
<style>
.stApp{background:#e8f5e9!important;}
.main.block-container{background:white!important;border-radius:18px;padding:20px!important;box-shadow:0 4px 15px rgba(0,0,0,0.1);}
[data-testid="stSidebar"]{background:#a5d6a7!important;border-right:4px solid #2e7d32!important;}
.stForm{background:#c8e6c9!important;border:3px solid #2e7d32!important;border-radius:15px!important;padding:15px!important;}
.stButton>button{background:#2e7d32!important;color:white!important;font-weight:bold!important;min-height:48px!important;border-radius:12px!important;}
div[data-testid="stFormSubmitButton"]>button{background:#d32f2f!important;}
.icon-lib{border:3px solid #2e7d32;border-radius:12px;padding:10px;background:white;text-align:center;margin:5px;}
.dashboard-card{border:3px solid #2e7d32;border-radius:15px;padding:15px;background:#e8f5e9;text-align:center;margin:10px;min-height:220px;}
.menu-rapido{border:2px solid #2e7d32;border-radius:10px;padding:10px;background:white;margin:5px;text-align:center;}
</style>
""", unsafe_allow_html=True)

def load_json(f, default):
    try:
        if os.path.exists(f):
            with open(f,"r",encoding="utf-8") as fh:
                d=json.load(fh)
                if isinstance(d,list) or isinstance(d,dict):
                    return d
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
            via=f"{road} {house}".strip() or data.get("display_name","").split(",")[0]
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
COMUNI=["Varese","Busto Arsizio","Gallarate","Saronno","Venegono Superiore","Venegono Inferiore","Castiglione Olona","Lozza","Tradate","Malnate","Luino","Altro"]
RUOLI=["Amministratore","Utente"]

for k,v in [("dati",[]),("postazioni",[]),("icone_lib",[]),("utenti",[]),("menu_scelta","Dashboard"),("map_lat",45.8205),("map_lon",8.8250),("map_via",""),("map_comune","Varese"),("map_logo","Default"),("post_sel",None),("map_zoom",13),("authenticated",False),("ruolo",""),("username","")]:
    if k not in st.session_state:
        st.session_state[k]=v

if not st.session_state.dati:
    st.session_state.dati=load_json(FILE_DATI,[])
if not st.session_state.postazioni:
    st.session_state.postazioni=load_json(FILE_POST,[])
if not st.session_state.icone_lib:
    st.session_state.icone_lib=load_json(FILE_ICONE,[])
if not st.session_state.utenti:
    st.session_state.utenti=load_json(FILE_UTENTI,[])

if not st.session_state.utenti:
    st.session_state.utenti=[
        {"username":"admin","password":hash_pwd("ana2024"),"ruolo":"Amministratore","nome":"Amministratore ANA"},
        {"username":"utente","password":hash_pwd("utente2024"),"ruolo":"Utente","nome":"Utente Volontario"}
    ]
    save_json(FILE_UTENTI,st.session_state.utenti)

def header_loghi():
    b64=get_b64("logo.png")
    if b64:
        st.markdown(f"<div style='display:flex;justify-content:center;align-items:center;gap:25px;background:#a5d6a7;padding:15px;border-radius:15px;border:3px solid #2e7d32;'><img src='data:image/png;base64,{b64}' style='width:80px;height:80px;border-radius:50%;'><h2 style='color:#0e7a3d;margin:0;text-align:center;'>VOLONTARIATO<br>Sezione di Varese</h2><img src='data:image/png;base64,{b64}' style='width:80px;height:80px;border-radius:50%;'></div>", unsafe_allow_html=True)
    else:
        st.markdown("<h2 style='text-align:center;color:#0e7a3d;'>VOLONTARIATO Sezione di Varese</h2>", unsafe_allow_html=True)

def torna_dashboard():
    if st.button("🏠 TORNA A DASHBOARD MENU COMPLETO",use_container_width=True,key="torna_home"):
        st.session_state.menu_scelta="Dashboard"
        st.rerun()

if not st.session_state.authenticated:
    header_loghi()
    st.markdown("## 🔐 LOGIN - Locale e Cloud")
    st.info("Admin: admin / ana2024 (gestisce tutto) | Utente: utente / utente2024 (inserisce e visualizza)")
    c1,c2,c3=st.columns([1,2,1])
    with c2:
        with st.form("login"):
            u=st.text_input("Username",value="admin")
            p=st.text_input("Password",type="password",value="ana2024")
            if st.form_submit_button("🔴 ACCEDI",use_container_width=True,type="primary"):
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
    st.markdown(f"### Ciao {st.session_state.username}")
    st.markdown(f"Ruolo: **{st.session_state.ruolo}**")
    st.markdown("### 📋 MENU COMPLETO FORM")
    if st.session_state.ruolo=="Amministratore":
        opzioni=["Dashboard","Volontari","Mappa Postazioni","Gestione Loghi","Gestione Utenti","Backup"]
    else:
        opzioni=["Dashboard","Volontari","Mappa Postazioni","Backup"]
    sel=st.radio("Vai a",opzioni,index=0,key="radio_menu")
    if sel!=st.session_state.menu_scelta:
        st.session_state.menu_scelta=sel
        st.rerun()
    st.divider()
    st.metric("Volontari",len(st.session_state.dati))
    st.metric("Postazioni",len(st.session_state.postazioni))
    st.metric("Loghi",len(st.session_state.icone_lib))
    st.divider()
    if st.button("🚪 LOGOUT",use_container_width=True,key="logout_sidebar"):
        st.session_state.authenticated=False
        st.session_state.ruolo=""
        st.session_state.username=""
        st.rerun()

scelta=st.session_state.menu_scelta
MIME="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

# ============ DASHBOARD CON ELENCO MENU COMPLETO + TASTI RAPIDI + LOGOUT ============
if scelta=="Dashboard":
    st.markdown("## 🏠 DASHBOARD - ELENCO MENU COMPLETO DI TUTTI I FORM CREATI")

    c_logout1,c_logout2=st.columns([3,1])
    with c_logout1:
        st.success(f"Benvenuto **{st.session_state.username}** | Ruolo: **{st.session_state.ruolo}** | Uso locale e Cloud attivo")
    with c_logout2:
        if st.button("🚪 LOGOUT DALLA DASHBOARD",use_container_width=True,type="primary",key="logout_dashboard"):
            st.session_state.authenticated=False
            st.session_state.ruolo=""
            st.session_state.username=""
            st.rerun()

    st.divider()
    st.markdown("### 📋 ELENCO MENU COMPLETO DI TUTTI I FORM CREATI")
    st.markdown("Tutti i form creati nel progetto - Con tasti menu rapido per accesso veloce")

    # --- MENU RAPIDO IN ALTO ---
    st.markdown("#### ⚡ MENU RAPIDO - Tasti rapidi per tutti i form")
    mr1,mr2,mr3,mr4,mr5,mr6=st.columns(6)
    with mr1:
        if st.button("👥\nVolontari",key="rapido_vol",use_container_width=True):
            st.session_state.menu_scelta="Volontari"
            st.rerun()
    with mr2:
        if st.button("📍\nMappa",key="rapido_mappa",use_container_width=True):
            st.session_state.menu_scelta="Mappa Postazioni"
            st.rerun()
    with mr3:
        if st.button("💾\nBackup",key="rapido_backup",use_container_width=True):
            st.session_state.menu_scelta="Backup"
            st.rerun()
    with mr4:
        if st.button("🎨\nLoghi",key="rapido_loghi",use_container_width=True):
            if st.session_state.ruolo=="Amministratore":
                st.session_state.menu_scelta="Gestione Loghi"
                st.rerun()
            else:
                st.warning("Solo Admin")
    with mr5:
        if st.button("👤\nUtenti",key="rapido_utenti",use_container_width=True):
            if st.session_state.ruolo=="Amministratore":
                st.session_state.menu_scelta="Gestione Utenti"
                st.rerun()
            else:
                st.warning("Solo Admin")
    with mr6:
        if st.button("🏠\nHome",key="rapido_home",use_container_width=True):
            st.session_state.menu_scelta="Dashboard"
            st.rerun()

    st.divider()

    # --- ELENCO COMPLETO FORM ---
    c1,c2,c3=st.columns(3)
    with c1:
        st.markdown('<div class="dashboard-card">',unsafe_allow_html=True)
        st.markdown("### 👥 FORM 1: VOLONTARI")
        st.markdown("**Sottomaschere:**")
        st.write("1. Anagrafica (Nome, Cognome)")
        st.write("2. Contatti (Cell, Email)")
        st.write("3. Associazione")
        st.write("4. Ruolo (Volontario, Caposquadra...)")
        st.write("5. Comune")
        st.write("6. Elenco + Excel")
        st.metric("Totale",len(st.session_state.dati))
        if st.button("👥 APRI FORM VOLONTARI",key="dash_vol",use_container_width=True,type="primary"):
            st.session_state.menu_scelta="Volontari"
            st.rerun()
        st.markdown('</div>',unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="dashboard-card">',unsafe_allow_html=True)
        st.markdown("### 📍 FORM 2: MAPPA POSTAZIONI")
        st.markdown("**Sottomaschere:**")
        st.write("1. Libreria loghi 15x15")
        st.write("2. Mappa selezione (clic + via)")
        st.write("3. Anteprima TUTTE con icone")
        st.write("4. Maschera con Via associata")
        st.write("5. Tabella postazioni nel form")
        st.write("6. Elenco con zoom + Excel")
        st.metric("Totale",len(st.session_state.postazioni))
        if st.button("📍 APRI MAPPA POSTAZIONI",key="dash_mappa",use_container_width=True,type="primary"):
            st.session_state.menu_scelta="Mappa Postazioni"
            st.rerun()
        st.markdown('</div>',unsafe_allow_html=True)

    with c3:
        st.markdown('<div class="dashboard-card">',unsafe_allow_html=True)
        st.markdown("### 💾 FORM 3: BACKUP")
        st.markdown("**Sottomaschere:**")
        st.write("1. Backup Volontari")
        st.write("2. Backup Postazioni")
        st.write("3. Backup Utenti")
        st.write("4. Excel completo")
        st.write("5. Download")
        if st.button("💾 APRI FORM BACKUP",key="dash_backup",use_container_width=True,type="primary"):
            st.session_state.menu_scelta="Backup"
            st.rerun()
        st.markdown('</div>',unsafe_allow_html=True)

    if st.session_state.ruolo=="Amministratore":
        c4,c5,c6=st.columns(3)
        with c4:
            st.markdown('<div class="dashboard-card">',unsafe_allow_html=True)
            st.markdown("### 🎨 FORM 4: GESTIONE LOGHI")
            st.markdown("**Sottomaschere:**")
            st.write("1. Carica logo PNG")
            st.write("2. Libreria loghi")
            st.write("3. Selezione 15x15")
            st.write("4. Loghi come puntatori")
            st.metric("Totale",len(st.session_state.icone_lib))
            if st.button("🎨 APRI GESTIONE LOGHI",key="dash_loghi",use_container_width=True,type="primary"):
                st.session_state.menu_scelta="Gestione Loghi"
                st.rerun()
            st.markdown('</div>',unsafe_allow_html=True)

        with c5:
            st.markdown('<div class="dashboard-card">',unsafe_allow_html=True)
            st.markdown("### 👤 FORM 5: GESTIONE UTENTI")
            st.markdown("**Sottomaschere:**")
            st.write("1. Elenco utenti")
            st.write("2. Crea utente")
            st.write("3. Ruoli: Admin/Utente")
            st.write("4. Elimina utente")
            st.write("5. Solo Admin")
            st.metric("Totale",len(st.session_state.utenti))
            if st.button("👤 APRI GESTIONE UTENTI",key="dash_utenti",use_container_width=True,type="primary"):
                st.session_state.menu_scelta="Gestione Utenti"
                st.rerun()
            st.markdown('</div>',unsafe_allow_html=True)

        with c6:
            st.markdown('<div class="dashboard-card">',unsafe_allow_html=True)
            st.markdown("### ⚙️ FORM 6: IMPOSTAZIONI PROGETTO")
            st.markdown("**Info:**")
            st.write(f"Comuni: {len(COMUNI)}")
            st.write("Mappe: 5 tipi")
            st.write("Icone: 15x15")
            st.write("Uso: Locale + Cloud")
            st.write("Ruoli: Admin, Utente")
            st.info("Progetto locale OK")
            st.markdown('</div>',unsafe_allow_html=True)

    st.divider()
    st.markdown("### 📊 RIEPILOGO PROGETTO LOCALE")
    rc1,rc2,rc3,rc4=st.columns(4)
    with rc1:
        st.metric("Volontari",len(st.session_state.dati))
    with rc2:
        st.metric("Postazioni",len(st.session_state.postazioni))
    with rc3:
        st.metric("Loghi",len(st.session_state.icone_lib))
    with rc4:
        st.metric("Utenti",len(st.session_state.utenti))

elif scelta=="Volontari":
    torna_dashboard()
    st.markdown("## 👥 FORM VOLONTARI")
    if st.session_state.ruolo=="Utente":
        st.info("Ruolo Utente: puoi inserire e visualizzare")
    with st.form("form_vol"):
        c1,c2=st.columns(2)
        with c1:
            nome=st.text_input("Nome *")
            cognome=st.text_input("Cognome *")
            cell=st.text_input("Cellulare *")
        with c2:
            assoc=st.text_input("Associazione *",value="ANA Varese")
            comune=st.selectbox("Comune",COMUNI,index=0)
            ruolo=st.selectbox("Ruolo *",["Volontario","Caposquadra","Coordinatore"])
        if st.form_submit_button("✅ SALVA