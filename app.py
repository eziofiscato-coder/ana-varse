import streamlit as st
import pandas as pd
from datetime import date, datetime
from io import BytesIO
import os, uuid, requests, json
st.set_page_config(page_title="ANA Varese", page_icon="🟢", layout="wide")
st.markdown("""<style>
.stApp{background-color:#e8f5e9!important;}
.main.block-container{background-color:white!important;border-radius:18px;padding:25px!important;}
[data-testid="stSidebar"]{background-color:#a5d6a7!important;border-right:4px solid #2e7d32!important;}
.stForm{background-color:#c8e6c9!important;border:3px solid #2e7d32!important;border-radius:15px!important;}
.stButton>button{background-color:#2e7d32!important;color:white!important;font-weight:bold!important;min-height:55px!important;}
div[data-testid="stFormSubmitButton"]>button{background-color:#d32f2f!important;color:white!important;}
.logout-btn>button{background-color:#b71c1c!important;color:white!important;}
.torna-btn>button{background-color:#1565c0!important;color:white!important;}
</style>""", unsafe_allow_html=True)
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
FILE_DATI="dati_volontari.json"; FILE_POST="postazioni.json"; FILE_EMER="emergenze.json"; FILE_RADIO="radio_db.json"; FILE_DIST="dist_radio.json"; FILE_EVENTI="eventi.json"; FILE_CHECK="checkin.json"; FILE_NOMI="mem_nomi.json"
COMUNI_VARESE=["Varese","Busto Arsizio","Gallarate","Saronno","Cassano Magnago","Tradate","Somma Lombardo","Malnate","Luino","Samarate","Laveno-Mombello","Cittiglio","Besozzo","Gavirate","Vergiate","Sesto Calende","Besnate","Cardano al Campo","Cavaria con Premezzo","Castellanza","Lonate Pozzolo","Fagnano Olona"]
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
    headers={"User-Agent":"ANA-Varese-App-TutteVie-2.0"}
    try:
        nom_url="https://nominatim.openstreetmap.org/search"
        params={"q":f"{comune}, Italy","format":"json","limit":3,"addressdetails":1}
        r=requests.get(nom_url,params=params,headers=headers,timeout=10)
        if r.status_code==200 and r.json():
            for res in r.json():
                osm_type=res.get("osm_type"); osm_id=res.get("osm_id"); lat=res.get("lat"); lon=res.get("lon")
                if osm_type=="relation" and osm_id:
                    area_id=3600000000+int(osm_id)
                    try:
                        q=f'[out:json][timeout:30];area({area_id})->.a;(way(area.a)["highway"]["name"];);out 3000;'
                        url="https://overpass-api.de/api/interpreter"
                        r2=requests.post(url,data={"data":q},timeout=30)
                        if r2.status_code==200:
                            data=r2.json(); vie=[]
                            for el in data.get("elements",[]):
                                if "tags" in el and "name" in el["tags"]:
                                    nome=el["tags"]["name"]
                                    if 2<len(nome)<80: vie.append(nome.strip())
                            vie=sorted(list(set(vie)))
                            if len(vie)>=5: return ["-- Seleziona Via --"]+vie
                    except: pass
                if lat and lon:
                    try:
                        q2=f'[out:json][timeout:30];way(around:8000,{lat},{lon})["highway"]["name"];out 3000;'
                        url="https://overpass-api.de/api/interpreter"
                        r2=requests.post(url,data={"data":q2},timeout=30)
                        if r2.status_code==200:
                            data=r2.json(); vie=[]
                            for el in data.get("elements",[]):
                                if "tags" in el and "name" in el["tags"]:
                                    nome=el["tags"]["name"]
                                    if 2<len(nome)<80: vie.append(nome.strip())
                            vie=sorted(list(set(vie)))
                            if len(vie)>=10: return ["-- Seleziona Via --"]+vie
                    except: pass
    except: pass
    try:
        q=f'[out:json][timeout:25];area["name"="{comune}"]["admin_level"~"^[6-8]$"]->.a;(way(area.a)["highway"]["name"];);out 2000;'
        url="https://overpass-api.de/api/interpreter"
        r=requests.post(url,data={"data":q},timeout=25)
        if r.status_code==200:
            data=r.json(); vie=[]
            for el in data.get("elements",[]):
                if "tags" in el and "name" in el["tags"]:
                    nome=el["tags"]["name"]
                    if 2<len(nome)<80: vie.append(nome.strip())
            vie=sorted(list(set(vie)))
            if len(vie)>=5: return ["-- Seleziona Via --"]+vie
    except: pass
    return ["-- Seleziona Via --","Via Roma","Via Garibaldi","Via Milano","Via Sacco","Via Verdi","Via Dante","Via Marconi","Via Mazzini"]
ICONS={"volontario":{"nome":"Volontario","icon":"👤"},"sede":{"nome":"Sede","icon":"🏠"},"radio":{"nome":"Radio","icon":"📻"},"emergenza":{"nome":"Emergenza","icon":"🚨"},"postazione":{"nome":"Postazione","icon":"📍"},"incendio":{"nome":"Incendio","icon":"🔥"},"alluvione":{"nome":"Alluvione","icon":"🌊"},"frana":{"nome":"Frana","icon":"⛰️"},"neve":{"nome":"Neve/Ghiaccio","icon":"❄️"}}
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
def torna(suffix=""):
    with st.container():
        st.markdown('<div class="torna-btn">', unsafe_allow_html=True)
        k=f"back_{suffix}_{uuid.uuid4().hex[:6]}"
        if st.button("🏠 Torna alla Dashboard",key=k,use_container_width=True):
            st.session_state.menu_scelta="Dashboard"; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
def header_loghi():
    c1,c2,c3=st.columns(3)
    if os.path.exists("logo.png"): c1.image("logo.png",width=80)
    if os.path.exists("logo2.png"): c2.image("logo2.png",width=80)
    if os.path.exists("logo_pc_lombardia.png"): c3.image("logo_pc_lombardia.png",width=80)
if not st.session_state.authenticated:
    st.markdown("<style>[data-testid='stSidebar']{display:none;}</style>",unsafe_allow_html=True)
    header_loghi()
    st.markdown("<h2 style='text-align:center; color:#2e7d32;'>Accesso - admin / ana2024</h2>",unsafe_allow_html=True)
    c1,c2,c3=st.columns([1,2,1])
    with c2:
        with st.form("login"):
            u=st.text_input("Username",value="admin"); p=st.text_input("Password",type="password",value="ana2024")
            if st.form_submit_button("Accedi",use_container_width=True):
                if u=="admin" and p=="ana2024": st.session_state.authenticated=True; st.rerun()
    st.stop()
header_loghi(); st.divider()
with st.sidebar:
    if os.path.exists("logo.png"): st.image("logo.png",width=80)
    st.markdown("### MENU ANA VARESE")
    opzioni=["Dashboard","Emergenze con Loghi","Mappa Postazioni","Volontari","DB Radio","Distribuzione Radio","Eventi","Check-in","Tabella Interventi Emergenza","Backup"]
    sel=st.radio("Seleziona",opzioni,index=opzioni.index(st.session_state.menu_scelta) if st.session_state.menu_scelta in opzioni else 0)
    if sel!=st.session_state.menu_scelta: st.session_state.menu_scelta=sel; st.rerun()
    st.divider()
    st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
    if st.button("🚪 LOGOUT - Esci",use_container_width=True,key="logout_btn"):
        st.session_state.authenticated=False; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.divider(); st.caption("💾 Dati memorizzati automaticamente!")
scelta=st.session_state.menu_scelta; st.markdown(f"## {scelta}"); st.divider()
COMUNI_TUTTI=load_comuni_italia(); MIME_SHORT="application/octet-stream"
if scelta=="Dashboard":
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Emergenze",len(st.session_state.emergenze_lista)); c2.metric("Postazioni",len(st.session_state.postazioni))
    c3.metric("Volontari",len(st.session_state.dati)); c4.metric("Radio",len(st.session_state.radio_db))
    c5,c6=st.columns(2); c5.metric("Eventi",len(st.session_state.eventi_lista)); c6.metric("Check-in",len(st.session_state.checkin_lista))
    st.info("✅ Tutti i dati memorizzati su disco!")
    if st.session_state.emergenze_lista:
        st.markdown("### Ultimi 5 Interventi Emergenza")
        st.dataframe(pd.DataFrame(st.session_state.emergenze_lista[-5:]),use_container_width=True)
        if st.button("📋 Vedi Tabella Completa Emergenze",use_container_width=True):
            st.session_state.menu_scelta="Tabella Interventi Emergenza"; st.rerun()
elif scelta=="Emergenze con Loghi":
    torna("top_em")
    st.markdown("### 🚨 EMERGENZA CON LOGHI - VECCHIO FORM COMPLETO CON TUTTI I CAMPI")
    c1,c2=st.columns(2)
    with c1: comune=st.selectbox("Comune *",COMUNI_TUTTI,key="comune_em")
    with c2:
        with st.spinner(f"Carico TUTTE le vie di {comune}..."): vie=get_vie_comune(comune)
        if len(vie)>10: st.success(f"Trovate {len(vie)-1} vie per {comune} - TUTTE!")
        else: st.warning(f"Solo {len(vie)-1} vie default")
        via=st.selectbox(f"Via * ({comune}) - {len(vie)-1} vie totali",vie,key="via_em")
        if via=="-- Seleziona Via --":
            via_man=st.text_input("Via manuale se non in lista",key="via_man_em"); via_f=via_man if via_man else via
        else: via_f=via
    with st.form("form_em_completo"):
        st.markdown("#### Dati Emergenza - Tutti i campi")
        col1,col2,col3=st.columns(3)
        with col1:
            data_em=st.date_input("Data *",value=date.today())
            ora_em=st.time_input("Ora *",value=datetime.now().time())
            tipo=st.selectbox("Tipo Emergenza *",list(ICONS.keys()),format_func=lambda x: ICONS[x]["icon"]+" "+ICONS[x]["nome"])
        with col2:
            gravita=st.selectbox("Gravità *",["Bassa","Media","Alta","Critica"],index=1)
            stato=st.selectbox("Stato *",["Aperta","In Corso","Chiusa","Archiviata"],index=0)
            civico=st.text_input("Civico")
        with col3:
            coord=st.text_input("Coordinatore *",value="ANA Varese")
            volontari_sel=st.multiselect("Volontari Coinvolti",st.session_state.mem_nomi)
            mezzi=st.text_input("Mezzi Utilizzati",placeholder="Es. Fuoristrada 1, Motosega")
        desc=st.text_area("Descrizione Dettagliata *",value=f"Intervento a {comune} - {via_f}",height=100)
        note=st.text_area("Note Aggiuntive",height=80)
        st.divider()
        if st.form_submit_button("💾 SALVA EMERGENZA COMPLETA",use_container_width=True,type="primary"):
            if via_f!="-- Seleziona Via --" and via_f!="" and desc!="":
                st.session_state.emergenze_lista.append({
                    "Data":str(data_em),"Ora":str(ora_em),"Logo":ICONS[tipo]["icon"],
                    "Comune":comune,"Via":via_f,"Civico":civico,
                    "Tipo":ICONS[tipo]["nome"],"TipoCod":tipo,"Gravità":gravita,"Stato":stato,
                    "Descrizione":desc,"Volontari":", ".join(volontari_sel),"Mezzi":mezzi,
                    "Coordinatore":coord,"Note":note
                })
                save_json(FILE_EMER,st.session_state.emergenze_lista)
                st.success(f"✅ Emergenza salvata con tutti i campi! {comune} - {via_f}"); st.rerun()
            else: st.error("Compila Via e Descrizione!")
    if st.session_state.emergenze_lista:
        st.markdown("#### Ultime Emergenze Inserite")
        st.dataframe(pd.DataFrame(st.session_state.emergenze_lista),use_container_width=True)
    torna("bottom_em")
elif scelta=="Mappa Postazioni":
    torna("top_map")
    c1,c2=st.columns(2)
    with c1: comune=st.selectbox("Comune *",COMUNI_TUTTI,key="comune_map")
    with c2:
        with st.spinner(f"Carico TUTTE le vie di {comune}..."): vie=get_vie_comune(comune)
        if len(vie)>10: st.success(f"Trovate {len(vie)-1} vie - TUTTE!")
