import streamlit as st
import pandas as pd
from datetime import date, datetime
from io import BytesIO
import os, uuid, requests, json

st.set_page_config(page_title="ANA Varese", page_icon="🟢", layout="wide")

st.markdown("""
<style>
.stApp{background-color:#e8f5e9!important;}
.main.block-container{background-color:white!important;border-radius:18px;padding:25px!important;}
[data-testid="stSidebar"]{background-color:#a5d6a7!important;border-right:4px solid #2e7d32!important;}
.stForm{background-color:#c8e6c9!important;border:3px solid #2e7d32!important;border-radius:15px!important;}
.stButton>button{background-color:#2e7d32!important;color:white!important;font-weight:bold!important;min-height:50px!important;}
div[data-testid="stFormSubmitButton"]>button{background-color:#d32f2f!important;}
.logout-btn>button{background-color:#b71c1c!important;}
.torna-btn>button{background-color:#1565c0!important;}
.quick-btn>button{background-color:#ff9800!important;border:2px solid #e65100!important;font-size:16px!important;min-height:80px!important;}
.quick-btn-green>button{background-color:#2e7d32!important;border:2px solid #1b5e20!important;min-height:80px!important;}
.quick-btn-red>button{background-color:#c62828!important;border:2px solid #b71c1c!important;min-height:80px!important;}
.quick-btn-blue>button{background-color:#1565c0!important;border:2px solid #0d47a1!important;min-height:80px!important;}
.vol-btn>button{background-color:#e8f5e9!important;color:#2e7d32!important;border:2px solid #2e7d32!important;text-align:left!important;min-height:40px!important;}
.vol-selected{background-color:#fff3e0;border:3px solid #ef6c00;border-radius:12px;padding:20px;margin:15px 0;}
.checkbox-box{background-color:#f1f8e9;border:3px solid #2e7d32;border-radius:12px;padding:20px;margin:15px 0;}
.logo-box{border:2px solid #2e7d32;border-radius:10px;padding:10px;text-align:center;background:#f1f8e9;}
</style>
""", unsafe_allow_html=True)

def load_json(f, default):
    try:
        if os.path.exists(f):
            with open(f,"r",encoding="utf-8") as fh:
                d=json.load(fh)
                if isinstance(d,list): return d
    except: pass
    return default

def save_json(f,d):
    try:
        with open(f,"w",encoding="utf-8") as fh: json.dump(d,fh,ensure_ascii=False,indent=2)
    except Exception as e: st.error(f"Errore {f}: {e}")

FILE_DATI="dati_volontari.json"
FILE_POST="postazioni.json"
FILE_EMER="emergenze.json"
FILE_RADIO="radio_db.json"
FILE_DIST="dist_radio.json"
FILE_EVENTI="eventi.json"
FILE_CHECK="checkin.json"
FILE_NOMI="mem_nomi.json"

COMUNI_VARESE=["Varese","Busto Arsizio","Gallarate","Saronno","Cassano Magnago","Tradate","Malnate","Luino"]
EMERGENCY_LOGOS = {
 "incendio_boschivo": {"nome": "Incendio Boschivo","emoji": "🔥","png": "https://cdn-icons-png.flaticon.com/512/206/206887.png"},
 "frana": {"nome": "Frana","emoji": "⛰️","png": "https://cdn-icons-png.flaticon.com/512/2942/2942041.png"},
 "caduta_albero": {"nome": "Caduta Albero","emoji": "🌳","png": "https://cdn-icons-png.flaticon.com/512/740/740934.png"},
 "esondazione": {"nome": "Esondazione","emoji": "🌊","png": "https://cdn-icons-png.flaticon.com/512/210/210543.png"},
 "vvff": {"nome": "VVFF","emoji": "🚒","png": "https://cdn-icons-png.flaticon.com/512/599/599502.png"},
 "protezione_civile": {"nome": "Prot. Civile","emoji": "🦺","png": "https://cdn-icons-png.flaticon.com/512/599/599505.png"},
 "ambulanza": {"nome": "Ambulanza 118","emoji": "🚑","png": "https://cdn-icons-png.flaticon.com/512/2751/2751790.png"},
}

@st.cache_data(ttl=86400)
def load_comuni_italia():
    try:
        url="https://raw.githubusercontent.com/matteocontrini/comuni-json/master/comuni.json"
        r=requests.get(url,timeout=10)
        if r.status_code==200:
            data=r.json()
            comuni=sorted([c["nome"] for c in data])
            top=[c for c in COMUNI_VARESE if c in comuni]
            altri=[c for c in comuni if c not in top]
            return top+altri
    except: pass
    return sorted(list(set(COMUNI_VARESE)))

@st.cache_data(ttl=3600, show_spinner=False)
def get_vie_comune(comune):
    try:
        nom_url="https://nominatim.openstreetmap.org/search"
        params={"q":f"{comune}, Italy","format":"json","limit":3}
        headers={"User-Agent":"ANA-Varese-App"}
        r=requests.get(nom_url,params=params,headers=headers,timeout=10)
        if r.status_code==200 and r.json():
            for res in r.json():
                if res.get("osm_type")=="relation" and res.get("osm_id"):
                    area_id=3600000000+int(res.get("osm_id"))
                    try:
                        q=f'[out:json][timeout:30];area({area_id})->.a;(way(area.a)["highway"]["name"];);out 3000;'
                        url="https://overpass-api.de/api/interpreter"
                        r2=requests.post(url,data={"data":q},timeout=30)
                        if r2.status_code==200:
                            data=r2.json()
                            vie=[]
                            for el in data.get("elements",[]):
                                if "tags" in el and "name" in el["tags"]:
                                    nome=el["tags"]["name"]
                                    if 2<len(nome)<80: vie.append(nome.strip())
                            vie=sorted(list(set(vie)))
                            if len(vie)>=5: return ["-- Seleziona Via --"]+vie
                    except: pass
    except: pass
    return ["-- Seleziona Via --","Via Roma","Via Garibaldi","Via Milano","Via Sacco","Via Verdi","Via Dante"]

# SESSION STATE
if "authenticated" not in st.session_state: st.session_state.authenticated=False
if "dati" not in st.session_state: st.session_state.dati=load_json(FILE_DATI,[])
if "postazioni" not in st.session_state: st.session_state.postazioni=load_json(FILE_POST,[])
if "emergenze_lista" not in st.session_state: st.session_state.emergenze_lista=load_json(FILE_EMER,[])
if "radio_db" not in st.session_state: st.session_state.radio_db=load_json(FILE_RADIO,[])
if "dist_radio" not in st.session_state: st.session_state.dist_radio=load_json(FILE_DIST,[])
if "eventi_lista" not in st.session_state: st.session_state.eventi_lista=load_json(FILE_EVENTI,[])
if "checkin_lista" not in st.session_state: st.session_state.checkin_lista=load_json(FILE_CHECK,[])
if "mem_nomi" not in st.session_state: st.session_state.mem_nomi=load_json(FILE_NOMI,["Mario Rossi","Luigi Bianchi"])
if "menu_scelta" not in st.session_state: st.session_state.menu_scelta="Dashboard"
if "volontario_selezionato" not in st.session_state: st.session_state.volontario_selezionato=None
if "volontario_idx" not in st.session_state: st.session_state.volontario_idx=None
if "clicked_lat" not in st.session_state: st.session_state.clicked_lat=""
if "clicked_lon" not in st.session_state: st.session_state.clicked_lon=""
if "form_lat" not in st.session_state: st.session_state.form_lat=""
if "form_lon" not in st.session_state: st.session_state.form_lon=""
if "form_via" not in st.session_state: st.session_state.form_via=""
if "form_desc" not in st.session_state: st.session_state.form_desc=""

def torna(suffix=""):
    st.markdown('<div class="torna-btn">', unsafe_allow_html=True)
    k=f"back_{suffix}_{uuid.uuid4().hex[:6]}"
    if st.button("🏠 Torna alla Dashboard",key=k,use_container_width=True):
        st.session_state.menu_scelta="Dashboard"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

def header_loghi():
    c1,c2,c3=st.columns(3)
    if os.path.exists("logo.png"): c1.image("logo.png",width=80)
    if os.path.exists("logo2.png"): c2.image("logo2.png",width=80)
    if os.path.exists("logo_pc_lombardia.png"): c3.image("logo_pc_lombardia.png",width=80)

if not st.session_state.authenticated:
    st.markdown("<style>[data-testid='stSidebar']{display:none;}</style>", unsafe_allow_html=True)
    header_loghi()
    st.markdown("<h2 style='text-align:center; color:#2e7d32;'>Accesso - admin / ana2024</h2>", unsafe_allow_html=True)
    c1,c2,c3=st.columns([1,2,1])
    with c2:
        with st.form("login"):
            u=st.text_input("Username",value="admin")
            p=st.text_input("Password",type="password",value="ana2024")
            if st.form_submit_button("Accedi",use_container_width=True):
                if u=="admin" and p=="ana2024":
                    st.session_state.authenticated=True
                    st.rerun()
    st.stop()

header_loghi()
st.divider()

with st.sidebar:
    if os.path.exists("logo.png"): st.image("logo.png",width=80)
    st.markdown("### MENU ANA VARESE")
    opzioni=["Dashboard","Emergenze con Loghi","Mappa Postazioni","Volontari","DB Radio","Distribuzione Radio","Eventi","Check-in","Tabella Interventi Emergenza","Backup"]
    sel=st.radio("Seleziona",opzioni,index=opzioni.index(st.session_state.menu_scelta) if st.session_state.menu_scelta in opzioni else 0)
    if sel!=st.session_state.menu_scelta:
        st.session_state.menu_scelta=sel
        st.rerun()
    st.divider()
    if st.button("🚪 LOGOUT - Esci",use_container_width=True,key="logout_btn"):
        st.session_state.authenticated=False
        st.rerun()

scelta=st.session_state.menu_scelta
st.markdown(f"## {scelta}")
st.divider()
COMUNI_TUTTI=load_comuni_italia()
MIME_SHORT="application/octet-stream"

# ======================================================
# DASHBOARD CON TASTI SCELTA RAPIDA
# ======================================================
if scelta=="Dashboard":
    st.markdown("### ⚡ TASTI SCELTA RAPIDA")
    st.info("Clicca un tasto per andare veloce al form!")

    # RIGA 1 - Emergenze e Postazioni
    c1,c2,c3,c4=st.columns(4)
    with c1:
        st.markdown('<div class="quick-btn-red">', unsafe_allow_html=True)
        if st.button("🚨\nNUOVA EMERGENZA", key="quick_emergenza", use_container_width=True):
            st.session_state.menu_scelta="Emergenze con Loghi"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="quick-btn-blue">', unsafe_allow_html=True)
        if st.button("📍\nNUOVA POSTAZIONE", key="quick_postazione", use_container_width=True):
            st.session_state.menu_scelta="Mappa Postazioni"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="quick-btn-green">', unsafe_allow_html=True)
        if st.button("👤\nNUOVO VOLONTARIO", key="quick_volontario", use_container_width=True):
            st.session_state.menu_scelta="Volontari"
            st.session_state.volontario_selezionato=None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with c4:
        st.markdown('<div class="quick-btn">', unsafe_allow_html=True)
        if st.button("📻\nASSEGNA RADIO", key="quick_radio", use_container_width=True):
            st.session_state.menu_scelta="Distribuzione Radio"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # RIGA 2 - Altri tasti rapidi
    c5,c6,c7,c8=st.columns(4)
    with c5:
        st.markdown('<div class="quick-btn">', unsafe_allow_html=True)
        if st.button("📅\nNUOVO EVENTO", key="quick_evento", use_container_width=True):
            st.session_state.menu_scelta="Eventi"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with c6:
        st.markdown('<div class="quick-btn-green">', unsafe_allow_html=True)
        if st.button("✅\nCHECK-IN", key="quick_checkin", use_container_width=True):
            st.session_state.menu_scelta="Check-in"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with c7:
        st.markdown('<div class="quick-btn-blue">', unsafe_allow_html=True)
        if st.button("📋\nTABELLA INTERVENTI", key="quick_tabella", use_container_width=True):
            st.session_state.menu_scelta="Tabella Interventi Emergenza"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with c8:
        st.markdown('<div class="quick-btn-red">', unsafe_allow_html=True)
        if st.button("💾\nBACKUP UNICO", key="quick_backup", use_container_width=True):
            st.session_state.menu_scelta="Backup"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

    # METRICHE
    c1,c2,c3,c4=st.columns(4)
    c1.metric("🚨 Emergenze",len(st.session_state.emergenze_lista))
    c2.metric("📍 Postazioni",len(st.session_state.postazioni))
    c3.metric("👤 Volontari",len(st.session_state.dati))
    c4.metric("📻 Radio",len(st.session_state.radio_db))
    c5,c6,c7,c8=st.columns(4)
    c5.metric("📅 Eventi",len(st.session_state.eventi_lista))
    c6.metric("✅ Check-in",len(st.session_state.checkin_lista))
    c7.metric("📡 Distr Radio",len(st.session_state.dist_radio))
    c8.metric("📝 Nomi",len(st.session_state.mem_nomi))

    st.divider()

    # ======================================================
    # TABELLA VOLONTARI CLICCABILE SULLA DASHBOARD
    # ======================================================
    st.markdown("### 👥 TABELLA VOLONTARI - CLICCA SUL NOME PER VEDERE I DATI")
    st.info("👉 Clicca sul nome del volontario per aprire il suo form con tutti i dati!")

    if st.session_state.dati:
        # Header tabella
        h1,h2,h3,h4=st.columns([3,2,2,2])
        h1.markdown("**👤 Nome - CLICCA**")
        h2.markdown("**📱 Cellulare**")
        h3.markdown("**🏠 Comune**")
        h4.markdown("**🎖️ Ruolo**")
        st.divider()

        for idx, vol in enumerate(st.session_state.dati):
            c1,c2,c3,c4=st.columns([3,2,2,2])
            with c1:
                st.markdown('<div class="vol-btn">', unsafe_allow_html=True)
                if st.button(f"👤 {vol.get('Nome','N/D')}", key=f"vol_dash_{idx}", use_container_width=True):
                    st.session_state.volontario_selezionato = vol
                    st.session_state.volontario_idx = idx
                    st.session_state.menu_scelta = "Volontari"
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            with c2:
                st.write(vol.get('Cellulare',''))
            with c3:
                st.write(vol.get('Comune',''))
            with c4:
                st.write(vol.get('Ruolo',''))
    else:
        st.warning("Nessun volontario ancora inserito. Usa il tasto rapido 👤 NUOVO VOLONTARIO!")

    st.divider()
    st.markdown("### 📦 BACKUP UNICO RAPIDO")
    col_b1,col_b2,col_b3=st.columns(3)
    with col_b1:
        if st.button("📦 CREA EXCEL UNICO TUTTI I FORM", use_container_width=True, type="primary", key="dash_excel_unico"):
            output=BytesIO()
            with pd.ExcelWriter(output,engine="openpyxl") as writer:
                if st.session_state.dati: pd.DataFrame(st.session_state.dati).to_excel(writer,sheet_name="Volontari",index=False)
                if st.session_state.postazioni: pd.DataFrame(st.session_state.postazioni).to_excel(writer,sheet_name="Postazioni",index=False)
                if st.session_state.emergenze_lista: pd.DataFrame(st.session_state.emergenze_lista).to_excel(writer,sheet_name="Emergenze",index=False)
                if st.session_state.radio_db: pd.DataFrame(st.session_state.radio_db).to_excel(writer,sheet_name="DB_Radio",index=False)
                if st.session_state.dist_radio: pd.DataFrame(st.session_state.dist_radio).to_excel(writer,sheet_name="Dist_Radio",index=False)
                if st.session_state.eventi_lista: pd.DataFrame(st.session_state.eventi_lista).to_excel(writer,sheet_name="Eventi",index=False)
                if st.session_state.checkin_lista: pd.DataFrame(st.session_state.checkin_lista).to_excel(writer,sheet_name="Checkin",index=False)
                if st.session_state.mem_nomi: pd.DataFrame(st.session_state.mem_nomi, columns=["Nomi"]).to_excel(writer,sheet_name="Mem_Nomi",index=False)
            st.session_state["backup_unico_excel"] = output.getvalue()
            st.success("✅ Excel UNICO creato!")
    with col_b2:
        if "backup_unico_excel" in st.session_state:
            st.download_button("📥 SCARICA EXCEL UNICO", st.session_state["backup_unico_excel"], file_name=f"BACKUP_UNICO_{date.today()}.xlsx", mime=MIME_SHORT, use_container_width=True, key="dash_dl_excel")
    with col_b3:
        totale = len(st.session_state.dati)+len(st.session_state.postazioni)+len(st.session_state.emergenze_lista)
        st.metric("Totale record", totale)

elif scelta=="Volontari":
    torna("top_vol")

    # SE HAI CLICCATO SU UN VOLONTARIO DALLA DASHBOARD, MOSTRA I SUOI DATI
    if st.session_state.volontario_selezionato is not None:
        vol = st.session_state.volontario_selezionato
        idx = st.session_state.volontario_idx
        st.markdown('<div class="vol-selected">', unsafe_allow_html=True)
        st.markdown(f"### 👤 VOLONTARIO SELEZIONATO: {vol.get('Nome','')}")
        st.markdown(f"**Hai cliccato sul nome nella tabella! Ecco i dati completi:**")
        c1,c2=st.columns(2)
        with c1:
            st.markdown(f"**Nome:** {vol.get('Nome','')}")
            st.markdown(f"**Cellulare:** {vol.get('Cellulare','')}")
            st.markdown(f"**Comune:** {vol.get('Comune','')}")
            st.markdown(f"**Ruolo:** {vol.get('Ruolo','')}")
            st.markdown(f"**Associazione:** {vol.get('Associazione','')}")
        with c2:
            if st.button("❌ Chiudi dettaglio", key="chiudi_vol", use_container_width=True):
                st.session_state.volontario_selezionato=None
                st.session_state.volontario_idx=None
                st.rerun()
            if st.button("🗑️ Elimina volontario", key="elimina_vol", use_container_width=True):
                st.session_state.dati.pop(idx)
                save_json(FILE_DATI,st.session_state.dati)
                st.session_state.volontario_selezionato=None
                st.session_state.volontario_idx=None
                st.success("Volontario eliminato!")
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        st.divider()

        # FORM MODIFICA CON DATI PRE-COMPILATI
        st.markdown("### ✏️ MODIFICA DATI VOLONTARIO")
        with st.form("form_modifica_vol"):
            nome_completo = vol.get('Nome','')
            parti = nome_completo.split(" ",1)
            nome_init = parti[0] if len(parti)>0 else ""
            cognome_init = parti[1] if len(parti)>1 else ""
            nome = st.text_input("Nome *", value=nome_init)
            cognome = st.text_input("Cognome *", value=cognome_init)
            cell = st.text_input("Cellulare *", value=vol.get('Cellulare',''))
            comune_cont = st.selectbox("Comune *", COMUNI_TUTTI, index=COMUNI_TUTTI.index(vol.get('Comune',COMUNI_TUTTI[0])) if vol.get('Comune','') in COMUNI_TUTTI else 0)
            ruolo = st.selectbox("Ruolo *", ["Volontario","Caposquadra","Coordinatore","Autista","Radio"], index=["Volontario","Caposquadra","Coordinatore","Autista","Radio"].index(vol.get('Ruolo','Volontario')) if vol.get('Ruolo','') in ["Volontario","Caposquadra","Coordinatore","Autista","Radio"] else 0)
            assoc = st.text_input("Associazione", value=vol.get('Associazione','ANA Varese'))
            if st.form_submit_button("💾 SALVA MODIFICHE", use_container_width=True, type="primary"):
                nome_completo_new=f"{nome} {cognome}"
                st.session_state.dati[idx]={"Nome":nome_completo_new,"Cellulare":cell,"Comune":comune_cont,"Ruolo":ruolo,"Associazione":assoc}
                save_json(FILE_DATI,st.session_state.dati)
                st.session_state.volontario_selezionato=None
                st.success(f"✅ Modificato {nome_completo_new}!")
                st.rerun()
        st.divider()

    # FORM NUOVO VOLONTARIO
    st.markdown("### ➕ NUOVO VOLONTARIO")
    with st.form("form_vol"):
        c1,c2=st.columns(2)
        with c1:
            nome=st.text_input("Nome *", key="nome_new")
            cognome=st.text_input("Cognome *", key="cognome_new")
            cell=st.text_input("Cellulare *", key="cell_new")
        with c2:
            comune_cont=st.selectbox("Comune *",COMUNI_TUTTI,key="comune_cont")
            ruolo=st.selectbox("Ruolo *",["Volontario","Caposquadra","Coordinatore","Autista","Radio"],key="ruolo_4")
            assoc=st.text_input("Associazione", value="ANA Varese", key="assoc_new")
        if st.form_submit_button("SALVA VOLONTARIO",use_container_width=True,type="primary"):
            if nome and cognome and cell:
                nome_completo=f"{nome} {cognome}"
                st.session_state.dati.append({"Nome":nome_completo,"Cellulare":cell,"Comune":comune_cont,"Ruolo":ruolo,"Associazione":assoc})
                save_json(FILE_DATI,st.session_state.dati)
                if nome_completo not in st.session_state.mem_nomi:
                    st.session_state.mem_nomi.append(nome_completo)
                    save_json(FILE_NOMI,st.session_state.mem_nomi)
                st.success(f"Aggiunto {nome_completo}!")
                st.rerun()

    # TABELLA VOLONTARI CLICCABILE ANCHE QUI
    st.divider()
    st.markdown("### 👥 TABELLA VOLONTARI - CLICCA SUL NOME")
    if st.session_state.dati:
        h1,h2,h3,h4,h5=st.columns([3,2,2,2,1])
        h1.markdown("**Nome - CLICCA**")
        h2.markdown("**Cell**")
        h3.markdown("**Comune**")
        h4.markdown("**Ruolo**")
        h5.markdown("**Azione**")
        st.divider()
        for idx, vol in enumerate(st.session_state.dati):
            c1,c2,c3,c4,c5=st.columns([3,2,2,2,1])
            with c1:
                if st.button(f"👤 {vol.get('Nome','')}", key=f"vol_tab_{idx}", use_container_width=True):
                    st.session_state.volontario_selezionato = vol
                    st.session_state.volontario_idx = idx
                    st.rerun()
            with c2: st.write(vol.get('Cellulare','')[:15])
            with c3: st.write(vol.get('Comune','')[:12])
            with c4: st.write(vol.get('Ruolo',''))
            with c5:
                if st.button("👁️", key=f"view_{idx}"):
                    st.session_state.volontario_selezionato = vol
                    st.session_state.volontario_idx = idx
                    st.rerun()
        st.divider()
        df=pd.DataFrame(st.session_state.dati)
        st.dataframe(df,use_container_width=True)
        output=BytesIO()
        df.to_excel(output,index=False,engine="openpyxl")
        st.download_button("📥 Scarica Excel Volontari", output.getvalue(), file_name=f"volontari_{date.today()}.xlsx", mime=MIME_SHORT, use_container_width=True)
    else:
        st.warning("Nessun volontario")

    torna("bottom_vol")

elif scelta=="Emergenze con Loghi":
    torna("top_em")
    st.markdown("### 🚨 EMERGENZA CON LOGHI")
    c1,c2=st.columns(2)
    with c1: comune=st.selectbox("Comune *",COMUNI_TUTTI,key="comune_em")
    with c2:
        with st.spinner(f"Carico vie di {comune}..."): vie=get_vie_comune(comune)
        via=st.selectbox(f"Via * ({len(vie)-1} vie)",vie,key="via_em")
        via_f=via if via!="-- Seleziona Via --" else st.text_input("Via manuale",key="via_man_em")
    logo_keys=list(EMERGENCY_LOGOS.keys())
    logo_names=[f"{EMERGENCY_LOGOS[k]['emoji']} {EMERGENCY_LOGOS[k]['nome']}" for k in logo_keys]
    sel_logo_idx=st.selectbox("Tipo Emergenza *",range(len(logo_keys)),format_func=lambda i: logo_names[i],key="logo_sel")
    sel_logo_info=EMERGENCY_LOGOS[logo_keys[sel_logo_idx]]
    with st.form("form_em_completo"):
        data_em=st.date_input("Data *",value=date.today())
        gravita=st.selectbox("Gravità *",["Bassa","Media","Alta","Critica"],index=1)
        desc=st.text_area("Descrizione *",value=f"{sel_logo_info['nome']} a {comune} - {via_f}",height=100)
        if st.form_submit_button("💾 SALVA EMERGENZA",use_container_width=True,type="primary"):
            if via_f!="-- Seleziona Via --" and desc!="":
                new_em={"ID":str(uuid.uuid4())[:8],"Data":str(data_em),"Logo":sel_logo_info['emoji'],"LogoNome":sel_logo_info['nome'],"Comune":comune,"Via":via_f,"Tipo":sel_logo_info['nome'],"Gravità":gravita,"Descrizione":desc}
                st.session_state.emergenze_lista.append(new_em)
                save_json(FILE_EMER,st.session_state.emergenze_lista)
                st.success(f"✅ Emergenza salvata!")
                st.rerun()
    if st.session_state.emergenze_lista:
        st.dataframe(pd.DataFrame(st.session_state.emergenze_lista),use_container_width=True)
    torna("bottom_em")

elif scelta=="Mappa Postazioni":
    torna("top_map")
    st.markdown("### 🗺️ MAPPA POSTAZIONI")
    c1,c2=st.columns(2)
    with c1: comune=st.selectbox("Comune *",COMUNI_TUTTI,key="comune_map_final")
    with c2: via=st.text_input("Via *",value=st.session_state.form_via,key="via_map_final")
    with st.form("form_post_finale"):
        nome=st.text_input("Nome Postazione *")
        lat_final=st.text_input("Latitudine *",value=st.session_state.form_lat,key="lat_final")
        lon_final=st.text_input("Longitudine *",value=st.session_state.form_lon,key="lon_final")
        if st.form_submit_button("➕ SALVA POSTAZIONE",use_container_width=True,type="primary"):
            if nome and lat_final and lon_final:
                new_post={"Postazione":nome,"Comune":comune,"Via":via,"Latitudine":lat_final,"Longitudine":lon_final}
                st.session_state.postazioni.append(new_post)
                save_json(FILE_POST,st.session_state.postazioni)
                st.success(f"✅ {nome} salvata!")
                st.rerun()
    if st.session_state.postazioni:
        st.dataframe(pd.DataFrame(st.session_state.postazioni),use_container_width=True)
    torna("bottom_map")

elif scelta=="Backup":
    torna("top_back")
    st.markdown("### 💾 BACKUP UNICO DI TUTTI I FORM")
    totale = len(st.session_state.dati)+len(st.session_state.postazioni)+len(st.session_state.emergenze_lista)+len(st.session_state.radio_db)+len(st.session_state.dist_radio)+len(st.session_state.eventi_lista)+len(st.session_state.checkin_lista)+len(st.session_state.mem_nomi)
    st.metric("Totale record tutti i form", totale)
    c1,c2,c3=st.columns(3)
    with c1:
        if st.button("📦 CREA EXCEL UNICO", use_container_width=True, type="primary", key="backup_excel_unico"):
            output=BytesIO()
            with pd.ExcelWriter(output,engine="openpyxl") as writer:
                if st.session_state.dati: pd.DataFrame(st.session_state.dati).to_excel(writer,sheet_name="Volontari",index=False)
                if st.session_state.postazioni: pd.DataFrame(st.session_state.postazioni).to_excel(writer,sheet_name="Postazioni",index=False)
                if st.session_state.emergenze_lista: pd.DataFrame(st.session_state.emergenze_lista).to_excel(writer,sheet_name="Emergenze",index=False)
                if st.session_state.radio_db: pd.DataFrame(st.session_state.radio_db).to_excel(writer,sheet_name="DB_Radio",index=False)
                if st.session_state.dist_radio: pd.DataFrame(st.session_state.dist_radio).to_excel(writer,sheet_name="Dist_Radio",index=False)
                if st.session_state.eventi_lista: pd.DataFrame(st.session_state.eventi_lista).to_excel(writer,sheet_name="Eventi",index=False)
                if st.session_state.checkin_lista: pd.DataFrame(st.session_state.checkin_lista).to_excel(writer,sheet_name="Checkin",index=False)
                if st.session_state.mem_nomi: pd.DataFrame(st.session_state.mem_nomi, columns=["Nomi"]).to_excel(writer,sheet_name="Mem_Nomi",index=False)
            st.session_state["backup_unico_excel"] = output.getvalue()
            st.success("✅ Excel UNICO creato!")
    with c2:
        if "backup_unico_excel" in st.session_state:
            st.download_button("📥 SCARICA EXCEL UNICO", st.session_state["backup_unico_excel"], file_name=f"BACKUP_UNICO_{date.today()}.xlsx", mime=MIME_SHORT, use_container_width=True, key="dl_unico")
    with c3:
        if st.button("📦 CREA JSON UNICO", use_container_width=True, key="backup_json_unico"):
            all_data={"volontari":st.session_state.dati,"postazioni":st.session_state.postazioni,"emergenze":st.session_state.emergenze_lista,"radio_db":st.session_state.radio_db,"dist_radio":st.session_state.dist_radio,"eventi":st.session_state.eventi_lista,"checkin":st.session_state.checkin_lista,"mem_nomi":st.session_state.mem_nomi}
            st.session_state["backup_unico_json"] = json.dumps(all_data,ensure_ascii=False,indent=2).encode('utf-8')
            st.success("✅ JSON UNICO creato!")
    if "backup_unico_json" in st.session_state:
        st.download_button("📥 SCARICA JSON UNICO TUTTI I FORM", st.session_state["backup_unico_json"], file_name=f"BACKUP_UNICO_{date.today()}.json", mime="application/json", use_container_width=True, key="dl_json_unico")

    st.divider()
    st.markdown("#### 📋 Backup con caselle")
    col1,col2=st.columns(2)
    with col1:
        chk_vol = st.checkbox(f"👤 Volontari ({len(st.session_state.dati)})", value=True, key="chk_vol_b")
        chk_post = st.checkbox(f"📍 Postazioni ({len(st.session_state.postazioni)})", value=True, key="chk_post_b")
        chk_emer = st.checkbox(f"🚨 Emergenze ({len(st.session_state.emergenze_lista)})", value=True, key="chk_emer_b")
        chk_radio = st.checkbox(f"📻 DB Radio ({len(st.session_state.radio_db)})", value=True, key="chk_radio_b")
    with col2:
        chk_dist = st.checkbox(f"📡 Distribuzione ({len(st.session_state.dist_radio)})", value=True, key="chk_dist_b")
        chk_eventi = st.checkbox(f"📅 Eventi ({len(st.session_state.eventi_lista)})", value=True, key="chk_eventi_b")
        chk_check = st.checkbox(f"✅ Check-in ({len(st.session_state.checkin_lista)})", value=True, key="chk_check_b")
        chk_nomi = st.checkbox(f"📝 Mem Nomi ({len(st.session_state.mem_nomi)})", value=True, key="chk_nomi_b")
    selected_count = sum([chk_vol, chk_post, chk_emer, chk_radio, chk_dist, chk_eventi, chk_check, chk_nomi])
    if st.button(f"📦 Crea Excel con {selected_count} Form",use_container_width=True,key="btn_excel_sel"):
        output=BytesIO()
        with pd.ExcelWriter(output,engine="openpyxl") as writer:
            if chk_vol and st.session_state.dati: pd.DataFrame(st.session_state.dati).to_excel(writer,sheet_name="Volontari",index=False)
            if chk_post and st.session_state.postazioni: pd.DataFrame(st.session_state.postazioni).to_excel(writer,sheet_name="Postazioni",index=False)
            if chk_emer and st.session_state.emergenze_lista: pd.DataFrame(st.session_state.emergenze_lista).to_excel(writer,sheet_name="Emergenze",index=False)
            if chk_radio and st.session_state.radio_db: pd.DataFrame(st.session_state.radio_db).to_excel(writer,sheet_name="DB_Radio",index=False)
        st.session_state["backup_sel_excel"] = output.getvalue()
        st.session_state["backup_sel_count"] = selected_count
    if "backup_sel_excel" in st.session_state:
        st.download_button(f"📥 Scarica Excel {st.session_state['backup_sel_count']} Form", st.session_state["backup_sel_excel"], file_name=f"backup_{st.session_state['backup_sel_count']}form_{date.today()}.xlsx", mime=MIME_SHORT, use_container_width=True, key="dl_sel")

    torna("bottom_back")

else:
    torna("generic")
    st.info(f"Sezione {scelta} - implementazione completa nel file diviso backup_modulo.py se usi 2 file")
    torna("bottom_generic")