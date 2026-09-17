import streamlit as st
import pandas as pd
from datetime import date, datetime
from io import BytesIO
import os, uuid, requests, json, base64

st.set_page_config(
    page_title="ANA Varese",
    page_icon="🟢",
    layout="wide"
)

st.markdown("""
<style>
.stApp{background-color:#e8f5e9!important;}
.main.block-container{
 background-color:white!important;
 border-radius:18px;
 padding:25px!important;
}
[data-testid="stSidebar"]{
 background-color:#a5d6a7!important;
 border-right:4px solid #2e7d32!important;
}
.stForm{
 background-color:#c8e6c9!important;
 border:3px solid #2e7d32!important;
 border-radius:15px!important;
}
.stButton>button{
 background-color:#2e7d32!important;
 color:white!important;
 font-weight:bold!important;
 min-height:55px!important;
}
div[data-testid="stFormSubmitButton"]>button{
 background-color:#d32f2f!important;
 color:white!important;
}
.logout-btn>button{
 background-color:#b71c1c!important;
 color:white!important;
}
.torna-btn>button{
 background-color:#1565c0!important;
 color:white!important;
}
.logo-box{
 border:2px solid #2e7d32;
 border-radius:10px;
 padding:10px;
 text-align:center;
 background:#f1f8e9;
}
</style>
""", unsafe_allow_html=True)

def load_json(f, default):
    try:
        if os.path.exists(f):
            with open(f,"r",encoding="utf-8") as fh:
                d=json.load(fh)
                if isinstance(d,list):
                    return d
    except:
        pass
    return default

def save_json(f,d):
    try:
        with open(f,"w",encoding="utf-8") as fh:
            json.dump(d,fh,ensure_ascii=False,indent=2)
    except Exception as e:
        st.error(f"Errore {f}: {e}")

FILE_DATI="dati_volontari.json"
FILE_POST="postazioni.json"
FILE_EMER="emergenze.json"
FILE_RADIO="radio_db.json"
FILE_DIST="dist_radio.json"
FILE_EVENTI="eventi.json"
FILE_CHECK="checkin.json"
FILE_NOMI="mem_nomi.json"

COMUNI_VARESE=[
 "Varese","Busto Arsizio","Gallarate",
 "Saronno","Cassano Magnago","Tradate",
 "Somma Lombardo","Malnate","Luino"
]

# LIBRERIA LOGHI PNG VERI EMERGENZA
EMERGENCY_LOGOS = {
 "incendio_boschivo": {
  "nome": "Incendio Boschivo",
  "emoji": "🔥",
  "png": "https://cdn-icons-png.flaticon.com/512/206/206887.png",
  "colore": "red"
 },
 "frana": {
  "nome": "Frana / Smottamento",
  "emoji": "⛰️",
  "png": "https://cdn-icons-png.flaticon.com/512/2942/2942041.png",
  "colore": "brown"
 },
 "caduta_albero": {
  "nome": "Caduta Albero",
  "emoji": "🌳",
  "png": "https://cdn-icons-png.flaticon.com/512/740/740934.png",
  "colore": "green"
 },
 "esondazione": {
  "nome": "Esondazione / Alluvione",
  "emoji": "🌊",
  "png": "https://cdn-icons-png.flaticon.com/512/210/210543.png",
  "colore": "blue"
 },
 "allagamento": {
  "nome": "Allagamento",
  "emoji": "💧",
  "png": "https://cdn-icons-png.flaticon.com/512/245/245246.png",
  "colore": "blue"
 },
 "neve_ghiaccio": {
  "nome": "Neve / Ghiaccio",
  "emoji": "❄️",
  "png": "https://cdn-icons-png.flaticon.com/512/642/642102.png",
  "colore": "lightblue"
 },
 "auto_polizia": {
  "nome": "Auto Polizia",
  "emoji": "🚓",
  "png": "https://cdn-icons-png.flaticon.com/512/3774/3774091.png",
  "colore": "blue"
 },
 "polizia_locale": {
  "nome": "Polizia Locale",
  "emoji": "👮",
  "png": "https://cdn-icons-png.flaticon.com/512/3106/3106091.png",
  "colore": "darkblue"
 },
 "vvff": {
  "nome": "VVFF - Vigili del Fuoco",
  "emoji": "🚒",
  "png": "https://cdn-icons-png.flaticon.com/512/599/599502.png",
  "colore": "red"
 },
 "protezione_civile": {
  "nome": "Mezzi Protezione Civile",
  "emoji": "🦺",
  "png": "https://cdn-icons-png.flaticon.com/512/599/599505.png",
  "colore": "orange"
 },
 "ambulanza": {
  "nome": "Ambulanza / 118",
  "emoji": "🚑",
  "png": "https://cdn-icons-png.flaticon.com/512/2751/2751790.png",
  "colore": "white"
 },
 "prima_accoglienza": {
  "nome": "Area Prima Accoglienza",
  "emoji": "⛺",
  "png": "https://cdn-icons-png.flaticon.com/512/109/109345.png",
  "colore": "green"
 },
 "elisoccorso": {
  "nome": "Elisoccorso",
  "emoji": "🚁",
  "png": "https://cdn-icons-png.flaticon.com/512/3079/3079004.png",
  "colore": "yellow"
 },
 "incidente_stradale": {
  "nome": "Incidente Stradale",
  "emoji": "🚗",
  "png": "https://cdn-icons-png.flaticon.com/512/3774/3774086.png",
  "colore": "red"
 },
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
    except:
        pass
    return sorted(list(set(COMUNI_VARESE)))

@st.cache_data(ttl=3600, show_spinner=False)
def get_vie_comune(comune):
    headers={"User-Agent":"ANA-Varese-App"}
    try:
        nom_url="https://nominatim.openstreetmap.org/search"
        params={
         "q":f"{comune}, Italy",
         "format":"json",
         "limit":3
        }
        r=requests.get(
         nom_url,
         params=params,
         headers=headers,
         timeout=10
        )
        if r.status_code==200 and r.json():
            for res in r.json():
                osm_type=res.get("osm_type")
                osm_id=res.get("osm_id")
                lat=res.get("lat")
                lon=res.get("lon")
                if osm_type=="relation" and osm_id:
                    area_id=3600000000+int(osm_id)
                    try:
                        q=f'[out:json][timeout:30];area({area_id})->.a;(way(area.a)["highway"]["name"];);out 3000;'
                        url="https://overpass-api.de/api/interpreter"
                        r2=requests.post(
                         url,
                         data={"data":q},
                         timeout=30
                        )
                        if r2.status_code==200:
                            data=r2.json()
                            vie=[]
                            for el in data.get("elements",[]):
                                if "tags" in el and "name" in el["tags"]:
                                    nome=el["tags"]["name"]
                                    if 2<len(nome)<80:
                                        vie.append(nome.strip())
                            vie=sorted(list(set(vie)))
                            if len(vie)>=5:
                                return ["-- Seleziona Via --"]+vie
                    except:
                        pass
    except:
        pass
    return [
     "-- Seleziona Via --",
     "Via Roma","Via Garibaldi","Via Milano",
     "Via Sacco","Via Verdi","Via Dante"
    ]

if "authenticated" not in st.session_state:
    st.session_state.authenticated=False
if "dati" not in st.session_state:
    st.session_state.dati=load_json(FILE_DATI,[])
if "postazioni" not in st.session_state:
    st.session_state.postazioni=load_json(FILE_POST,[])
if "emergenze_lista" not in st.session_state:
    st.session_state.emergenze_lista=load_json(FILE_EMER,[])
if "radio_db" not in st.session_state:
    st.session_state.radio_db=load_json(FILE_RADIO,[])
if "dist_radio" not in st.session_state:
    st.session_state.dist_radio=load_json(FILE_DIST,[])
if "eventi_lista" not in st.session_state:
    st.session_state.eventi_lista=load_json(FILE_EVENTI,[])
if "checkin_lista" not in st.session_state:
    st.session_state.checkin_lista=load_json(FILE_CHECK,[])
if "mem_nomi" not in st.session_state:
    st.session_state.mem_nomi=load_json(
     FILE_NOMI,
     ["Mario Rossi","Luigi Bianchi"]
    )
if "menu_scelta" not in st.session_state:
    st.session_state.menu_scelta="Dashboard"
if "last_postazione" not in st.session_state:
    st.session_state.last_postazione=None

def torna(suffix=""):
    with st.container():
        st.markdown(
         '<div class="torna-btn">',
         unsafe_allow_html=True
        )
        k=f"back_{suffix}_{uuid.uuid4().hex[:6]}"
        if st.button(
         "🏠 Torna alla Dashboard",
         key=k,
         use_container_width=True
        ):
            st.session_state.menu_scelta="Dashboard"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

def header_loghi():
    c1,c2,c3=st.columns(3)
    if os.path.exists("logo.png"):
        c1.image("logo.png",width=80)
    if os.path.exists("logo2.png"):
        c2.image("logo2.png",width=80)
    if os.path.exists("logo_pc_lombardia.png"):
        c3.image("logo_pc_lombardia.png",width=80)

if not st.session_state.authenticated:
    st.markdown(
     "<style>[data-testid='stSidebar']{display:none;}</style>",
     unsafe_allow_html=True
    )
    header_loghi()
    st.markdown(
     "<h2 style='text-align:center; color:#2e7d32;'>Accesso - admin / ana2024</h2>",
     unsafe_allow_html=True
    )
    c1,c2,c3=st.columns([1,2,1])
    with c2:
        with st.form("login"):
            u=st.text_input("Username",value="admin")
            p=st.text_input(
             "Password",
             type="password",
             value="ana2024"
            )
            if st.form_submit_button(
             "Accedi",
             use_container_width=True
            ):
                if u=="admin" and p=="ana2024":
                    st.session_state.authenticated=True
                    st.rerun()
    st.stop()

header_loghi()
st.divider()

with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png",width=80)
    st.markdown("### MENU ANA VARESE")
    opzioni=[
     "Dashboard",
     "Emergenze con Loghi",
     "Mappa Postazioni",
     "Volontari",
     "DB Radio",
     "Distribuzione Radio",
     "Eventi",
     "Check-in",
     "Tabella Interventi Emergenza",
     "Backup"
    ]
    sel=st.radio(
     "Seleziona",
     opzioni,
     index=opzioni.index(
      st.session_state.menu_scelta
     ) if st.session_state.menu_scelta in opzioni else 0
    )
    if sel!=st.session_state.menu_scelta:
        st.session_state.menu_scelta=sel
        st.rerun()
    st.divider()
    st.markdown(
     '<div class="logout-btn">',
     unsafe_allow_html=True
    )
    if st.button(
     "🚪 LOGOUT - Esci",
     use_container_width=True,
     key="logout_btn"
    ):
        st.session_state.authenticated=False
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.divider()
    st.caption("💾 Dati memorizzati!")

scelta=st.session_state.menu_scelta
st.markdown(f"## {scelta}")
st.divider()
COMUNI_TUTTI=load_comuni_italia()
MIME_SHORT="application/octet-stream"

if scelta=="Dashboard":
    c1,c2,c3,c4=st.columns(4)
    c1.metric(
     "Emergenze",
     len(st.session_state.emergenze_lista)
    )
    c2.metric(
     "Postazioni",
     len(st.session_state.postazioni)
    )
    c3.metric(
     "Volontari",
     len(st.session_state.dati)
    )
    c4.metric(
     "Radio",
     len(st.session_state.radio_db)
    )
    st.info("✅ Dati memorizzati su disco!")

elif scelta=="Emergenze con Loghi":
    torna("top_em")
    st.markdown("### 🚨 EMERGENZA CON LOGHI VERI PNG")
    st.info("Loghi veri PNG: Incendio, Frana, VVFF, Polizia, Ambulanza, ecc.")
    c1,c2=st.columns(2)
    with c1:
        comune=st.selectbox(
         "Comune *",
         COMUNI_TUTTI,
         key="comune_em"
        )
    with c2:
        with st.spinner(f"Carico vie di {comune}..."):
            vie=get_vie_comune(comune)
        via=st.selectbox(
         f"Via * ({len(vie)-1} vie)",
         vie,
         key="via_em"
        )
        if via=="-- Seleziona Via --":
            via_man=st.text_input(
             "Via manuale",
             key="via_man_em"
            )
            via_f=via_man if via_man else via
        else:
            via_f=via

    st.markdown("#### 🎨 SCEGLI LOGO VERO PNG")
    col_logo1,col_logo2,col_logo3=st.columns([2,1,1])
    with col_logo1:
        logo_keys=list(EMERGENCY_LOGOS.keys())
        logo_names=[
         f"{EMERGENCY_LOGOS[k]['emoji']} {EMERGENCY_LOGOS[k]['nome']}"
         for k in logo_keys
        ]
        sel_logo_idx=st.selectbox(
         "Tipo Emergenza con Logo PNG *",
         range(len(logo_keys)),
         format_func=lambda i: logo_names[i],
         key="logo_sel"
        )
        sel_logo_key=logo_keys[sel_logo_idx]
        sel_logo_info=EMERGENCY_LOGOS[sel_logo_key]
    with col_logo2:
        st.markdown('<div class="logo-box">', unsafe_allow_html=True)
        st.markdown(f"**{sel_logo_info['nome']}**")
        try:
            st.image(sel_logo_info['png'],width=80)
        except:
            st.markdown(f"# {sel_logo_info['emoji']}")
        st.markdown('</div>', unsafe_allow_html=True)
    with col_logo3:
        st.markdown("**Carica PNG Personalizzato**")
        custom_logo_upload=st.file_uploader(
         "Carica logo PNG",
         type=["png","jpg","jpeg"],
         key="custom_logo"
        )
        custom_b64=""
        if custom_logo_upload:
            st.image(custom_logo_upload,width=80)
            custom_b64=base64.b64encode(
             custom_logo_upload.getvalue()
            ).decode()
            st.success("✅ PNG caricato!")

    with st.form("form_em_completo"):
        st.markdown("#### Dati Emergenza")
        col1
