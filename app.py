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
.stButton>button{background-color:#2e7d32!important;color:white!important;font-weight:bold!important;min-height:55px!important;}
div[data-testid="stFormSubmitButton"]>button{background-color:#d32f2f!important;}
.torna-btn>button{background-color:#1565c0!important;}
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

def reverse_geocode_dettagliato(lat, lon):
    try:
        url=f"https://nominatim.openstreetmap.org/reverse"
        params={"format":"json","lat":lat,"lon":lon,"zoom":18,"addressdetails":1}
        headers={"User-Agent":"ANA-Varese-App"}
        r=requests.get(url,params=params,headers=headers,timeout=10)
        if r.status_code==200:
            data=r.json()
            addr=data.get("address",{})
            road=addr.get("road") or ""
            city=addr.get("city") or addr.get("town") or addr.get("village") or ""
            return city, road, data.get("display_name",""), data.get("display_name",""), addr
    except: pass
    return "", "", "", "", {}

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

if scelta=="Dashboard":
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Emergenze",len(st.session_state.emergenze_lista))
    c2.metric("Postazioni",len(st.session_state.postazioni))
    c3.metric("Volontari",len(st.session_state.dati))
    c4.metric("Radio",len(st.session_state.radio_db))
    st.info("✅ Sistema diviso - 950+ righe totali con 2 file!")

elif scelta=="Emergenze con Loghi":
    torna("top_em")
    comune=st.selectbox("Comune *",COMUNI_TUTTI,key="comune_em")
    with st.spinner(f"Carico vie di {comune}..."):
        vie=get_vie_comune(comune)
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
    try:
        import folium
        from streamlit_folium import st_folium
        from folium.plugins import Fullscreen
        m_click=folium.Map(location=[45.8205,8.8255],zoom_start=12,tiles="OpenStreetMap")
        Fullscreen(position="topleft").add_to(m_click)
        map_data=st_folium(m_click,width=800,height=400,returned_objects=["last_clicked"])
        if map_data and map_data.get("last_clicked"):
            st.session_state.clicked_lat=str(map_data["last_clicked"]["lat"])
            st.session_state.clicked_lon=str(map_data["last_clicked"]["lng"])
            st.rerun()
    except ImportError:
        st.warning("Installa folium")
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

elif scelta=="Volontari":
    torna("top_vol")
    with st.form("form_vol"):
        nome=st.text_input("Nome *")
        cognome=st.text_input("Cognome *")
        cell=st.text_input("Cellulare *")
        comune_cont=st.selectbox("Comune *",COMUNI_TUTTI,key="comune_cont")
        ruolo=st.selectbox("Ruolo *",["Volontario","Caposquadra","Coordinatore","Autista","Radio"],key="ruolo_4")
        if st.form_submit_button("SALVA VOLONTARIO",use_container_width=True,type="primary"):
            if nome and cognome and cell:
                nome_completo=f"{nome} {cognome}"
                st.session_state.dati.append({"Nome":nome_completo,"Cellulare":cell,"Comune":comune_cont,"Ruolo":ruolo})
                save_json(FILE_DATI,st.session_state.dati)
                if nome_completo not in st.session_state.mem_nomi:
                    st.session_state.mem_nomi.append(nome_completo)
                    save_json(FILE_NOMI,st.session_state.mem_nomi)
                st.success(f"Aggiunto {nome_completo}!")
                st.rerun()
    if st.session_state.dati:
        st.dataframe(pd.DataFrame(st.session_state.dati),use_container_width=True)
    torna("bottom_vol")

elif scelta=="Backup":
    from backup_modulo import mostra_backup
    mostra_backup()

else:
    torna("generic")
    st.info(f"Sezione {scelta}")
    torna("bottom_generic")