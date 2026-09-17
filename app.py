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
}
.logout-btn>button{background-color:#b71c1c!important;}
.torna-btn>button{background-color:#1565c0!important;}
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
 "Saronno","Cassano Magnago","Tradate"
]

EMERGENCY_LOGOS = {
 "incendio_boschivo": {
  "nome": "Incendio Boschivo",
  "emoji": "🔥",
  "png": "https://cdn-icons-png.flaticon.com/512/206/206887.png"
 },
 "frana": {
  "nome": "Frana",
  "emoji": "⛰️",
  "png": "https://cdn-icons-png.flaticon.com/512/2942/2942041.png"
 },
 "caduta_albero": {
  "nome": "Caduta Albero",
  "emoji": "🌳",
  "png": "https://cdn-icons-png.flaticon.com/512/740/740934.png"
 },
 "esondazione": {
  "nome": "Esondazione",
  "emoji": "🌊",
  "png": "https://cdn-icons-png.flaticon.com/512/210/210543.png"
 },
 "auto_polizia": {
  "nome": "Auto Polizia",
  "emoji": "🚓",
  "png": "https://cdn-icons-png.flaticon.com/512/3774/3774091.png"
 },
 "polizia_locale": {
  "nome": "Polizia Locale",
  "emoji": "👮",
  "png": "https://cdn-icons-png.flaticon.com/512/3106/3106091.png"
 },
 "vvff": {
  "nome": "VVFF Vigili del Fuoco",
  "emoji": "🚒",
  "png": "https://cdn-icons-png.flaticon.com/512/599/599502.png"
 },
 "protezione_civile": {
  "nome": "Mezzi Protezione Civile",
  "emoji": "🦺",
  "png": "https://cdn-icons-png.flaticon.com/512/599/599505.png"
 },
 "ambulanza": {
  "nome": "Ambulanza 118",
  "emoji": "🚑",
  "png": "https://cdn-icons-png.flaticon.com/512/2751/2751790.png"
 },
 "prima_accoglienza": {
  "nome": "Area Prima Accoglienza",
  "emoji": "⛺",
  "png": "https://cdn-icons-png.flaticon.com/512/109/109345.png"
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
        params={"q":f"{comune}, Italy","format":"json","limit":3}
        r=requests.get(nom_url,params=params,headers=headers,timeout=10)
        if r.status_code==200 and r.json():
            for res in r.json():
                osm_type=res.get("osm_type")
                osm_id=res.get("osm_id")
                if osm_type=="relation" and osm_id:
                    area_id=3600000000+int(osm_id)
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
                                    if 2<len(nome)<80:
                                        vie.append(nome.strip())
                            vie=sorted(list(set(vie)))
                            if len(vie)>=5:
                                return ["-- Seleziona Via --"]+vie
                    except:
                        pass
    except:
        pass
    return ["-- Seleziona Via --","Via Roma","Via Garibaldi","Via Milano","Via Sacco","Via Verdi","Via Dante"]

def reverse_geocode(lat, lon):
    try:
        url=f"https://nominatim.openstreetmap.org/reverse"
        params={"format":"json","lat":lat,"lon":lon,"zoom":18,"addressdetails":1}
        headers={"User-Agent":"ANA-Varese-App"}
        r=requests.get(url,params=params,headers=headers,timeout=10)
        if r.status_code==200:
            data=r.json()
            addr=data.get("address",{})
            comune=addr.get("city") or addr.get("town") or addr.get("village") or ""
            via=addr.get("road") or addr.get("pedestrian") or ""
            return comune, via
    except:
        pass
    return "", ""

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
    st.session_state.mem_nomi=load_json(FILE_NOMI,["Mario Rossi","Luigi Bianchi"])
if "menu_scelta" not in st.session_state:
    st.session_state.menu_scelta="Dashboard"
if "last_postazione" not in st.session_state:
    st.session_state.last_postazione=None
if "clicked_lat" not in st.session_state:
    st.session_state.clicked_lat=""
if "clicked_lon" not in st.session_state:
    st.session_state.clicked_lon=""
if "clicked_comune" not in st.session_state:
    st.session_state.clicked_comune=""
if "clicked_via" not in st.session_state:
    st.session_state.clicked_via=""
if "selected_pointer" not in st.session_state:
    st.session_state.selected_pointer="📍 Default Rosso"
if "selected_custom_b64" not in st.session_state:
    st.session_state.selected_custom_b64=""

def torna(suffix=""):
    st.markdown('<div class="torna-btn">', unsafe_allow_html=True)
    k=f"back_{suffix}_{uuid.uuid4().hex[:6]}"
    if st.button("🏠 Torna alla Dashboard",key=k,use_container_width=True):
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
    if os.path.exists("logo.png"):
        st.image("logo.png",width=80)
    st.markdown("### MENU ANA VARESE")
    opzioni=[
     "Dashboard","Emergenze con Loghi","Mappa Postazioni",
     "Volontari","DB Radio","Distribuzione Radio",
     "Eventi","Check-in","Tabella Interventi Emergenza","Backup"
    ]
    sel=st.radio("Seleziona",opzioni,index=opzioni.index(st.session_state.menu_scelta) if st.session_state.menu_scelta in opzioni else 0)
    if sel!=st.session_state.menu_scelta:
        st.session_state.menu_scelta=sel
        st.rerun()
    st.divider()
    st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
    if st.button("🚪 LOGOUT - Esci",use_container_width=True,key="logout_btn"):
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
    c1.metric("Emergenze",len(st.session_state.emergenze_lista))
    c2.metric("Postazioni",len(st.session_state.postazioni))
    c3.metric("Volontari",len(st.session_state.dati))
    c4.metric("Radio",len(st.session_state.radio_db))
    st.info("✅ Dati memorizzati su disco!")
    if st.session_state.emergenze_lista:
        st.markdown("### Ultimi Interventi con Loghi PNG")
        st.dataframe(pd.DataFrame(st.session_state.emergenze_lista[-5:]),use_container_width=True)

elif scelta=="Emergenze con Loghi":
    torna("top_em")
    st.markdown("### 🚨 EMERGENZA CON LOGHI VERI PNG")
    st.info("14 loghi PNG veri: incendio, frana, VVFF, polizia, ambulanza, area accoglienza ecc.")
    c1,c2=st.columns(2)
    with c1:
        comune=st.selectbox("Comune *",COMUNI_TUTTI,key="comune_em")
    with c2:
        with st.spinner(f"Carico vie di {comune}..."):
            vie=get_vie_comune(comune)
        via=st.selectbox(f"Via * ({len(vie)-1} vie)",vie,key="via_em")
        if via=="-- Seleziona Via --":
            via_man=st.text_input("Via manuale",key="via_man_em")
            via_f=via_man if via_man else via
        else:
            via_f=via
    st.markdown("#### 🎨 SCEGLI LOGO VERO PNG")
    col_logo1,col_logo2,col_logo3=st.columns([2,1,1])
    with col_logo1:
        logo_keys=list(EMERGENCY_LOGOS.keys())
        logo_names=[f"{EMERGENCY_LOGOS[k]['emoji']} {EMERGENCY_LOGOS[k]['nome']}" for k in logo_keys]
        sel_logo_idx=st.selectbox("Tipo Emergenza *",range(len(logo_keys)),format_func=lambda i: logo_names[i],key="logo_sel")
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
        custom_logo_upload=st.file_uploader("Carica PNG",type=["png","jpg","jpeg"],key="custom_logo")
        custom_b64=""
        if custom_logo_upload:
            st.image(custom_logo_upload,width=80)
            custom_b64=base64.b64encode(custom_logo_upload.getvalue()).decode()
            st.success("✅ PNG caricato!")
    with st.form("form_em_completo"):
        st.markdown("#### Dati Emergenza - Tutti i campi")
        cc1,cc2,cc3=st.columns(3)
        with cc1:
            data_em=st.date_input("Data *",value=date.today())
            ora_em=st.time_input("Ora *",value=datetime.now().time())
            gravita=st.selectbox("Gravità *",["Bassa","Media","Alta","Critica"],index=1)
        with cc2:
            stato=st.selectbox("Stato *",["Aperta","In Corso","Chiusa","Archiviata"],index=0)
            civico=st.text_input("Civico")
            coord=st.text_input("Coordinatore *",value="ANA Varese")
        with cc3:
            volontari_sel=st.multiselect("Volontari",st.session_state.mem_nomi)
            mezzi=st.text_input("Mezzi Utilizzati",placeholder="Es. Fuoristrada 1")
        desc=st.text_area("Descrizione *",value=f"{sel_logo_info['nome']} a {comune} - {via_f}",height=100)
        note=st.text_area("Note",height=80)
        st.divider()
        if st.form_submit_button("💾 SALVA CON LOGO PNG VERO",use_container_width=True,type="primary"):
            if via_f!="-- Seleziona Via --" and via_f!="" and desc!="":
                if custom_b64:
                    logo_png_to_save=f"data:image/png;base64,{custom_b64}"
                else:
                    logo_png_to_save=sel_logo_info['png']
                st.session_state.emergenze_lista.append({
                 "Data":str(data_em),"Ora":str(ora_em),
                 "Logo":sel_logo_info['emoji'],"LogoNome":sel_logo_info['nome'],"LogoPNG":logo_png_to_save,
                 "Comune":comune,"Via":via_f,"Civico":civico,
                 "Tipo":sel_logo_info['nome'],"Gravità":gravita,"Stato":stato,
                 "Descrizione":desc,"Volontari":", ".join(volontari_sel),"Mezzi":mezzi,
                 "Coordinatore":coord,"Note":note
                })
                save_json(FILE_EMER,st.session_state.emergenze_lista)
                st.success("✅ Emergenza salvata con logo PNG!")
                st.rerun()
            else:
                st.error("Compila Via e Descrizione!")
    if st.session_state.emergenze_lista:
        st.dataframe(pd.DataFrame(st.session_state.emergenze_lista),use_container_width=True)
    torna("bottom_em")

elif scelta=="Mappa Postazioni":
    torna("top_map")
    st.markdown("### 🗺️ MAPPA - CLICK + PUNTATORE PNG SCELTO")
    st.info("💡 Scegli prima il puntatore PNG (libreria o tuo PNG), poi clicca sulla mappa: ti appare subito il puntatore scelto!")

    # SELEZIONE PUNTATORE PRIMA DEL CLICK
    st.markdown("#### 1️⃣ Scegli il puntatore PNG che vuoi usare al click")
    cc1,cc2,cc3=st.columns([2,1,1])
    with cc1:
        tipo_puntatore=st.selectbox("Tipo Puntatore *",["📍 Default Rosso","🚨 Emergenza","🏠 Sede ANA","👤 Volontario","🔥 Incendio","🌊 Alluvione","🚑 Sanitario","📻 Radio","⭐ Personalizzato PNG"],key="pointer_select")
        st.session_state.selected_pointer=tipo_puntatore
    with cc2:
        st.markdown('<div class="logo-box">', unsafe_allow_html=True)
        st.markdown(f"**{tipo_puntatore}**")
        if tipo_puntatore=="⭐ Personalizzato PNG" and st.session_state.selected_custom_b64:
            try:
                st.image(f"data:image/png;base64,{st.session_state.selected_custom_b64}",width=60)
            except:
                st.markdown("PNG caricato")
        else:
            st.markdown(f"# {tipo_puntatore[:2]}")
        st.markdown('</div>', unsafe_allow_html=True)
    with cc3:
        png_upload=st.file_uploader("Carica PNG tuo",type=["png","jpg","jpeg"],key="png_up")
        if png_upload:
            st.image(png_upload,width=60)
            b64=base64.b64encode(png_upload.getvalue()).decode()
            st.session_state.selected_custom_b64=b64
            st.session_state["custom_png_b64"]=b64
            st.success("✅ PNG salvato!")

    st.divider()
    st.markdown("#### 2️⃣ Clicca sulla mappa - Appare subito il puntatore scelto")

    try:
        import folium
        from streamlit_folium import st_folium
        from folium.plugins import Fullscreen

        if st.session_state.last_postazione:
            try:
                lat_c=float(str(st.session_state.last_postazione["Latitudine"]).replace(",","."))
                lon_c=float(str(st.session_state.last_postazione["Longitudine"]).replace(",","."))
                zoom=14
            except:
                lat_c=45.8205; lon_c=8.8255; zoom=12
        else:
            lat_c=45.8205; lon_c=8.8255; zoom=12

        m_click=folium.Map(location=[lat_c,lon_c],zoom_start=zoom,tiles="OpenStreetMap")
        Fullscreen(position="topleft", title="Espandi", title_cancel="Esci").add_to(m_click)

        # Postazioni esistenti
        if st.session_state.postazioni:
            df_temp=pd.DataFrame(st.session_state.postazioni)
            for idx, r in df_temp.iterrows():
                try:
                    la=float(str(r["Latitudine"]).replace(",","."))
                    lo=float(str(r["Longitudine"]).replace(",","."))
                    punt=r.get("Puntatore","📍 Default Rosso")
                    cb64=r.get("CustomPNG","")
                    if punt=="⭐ Personalizzato PNG" and cb64:
                        icon_url=f"data:image/png;base64,{cb64}"
                        icon=folium.CustomIcon(icon_url,icon_size=(40,40),icon_anchor=(20,40))
                        folium.Marker([la,lo],popup=f"{r['Postazione']}",icon=icon).add_to(m_click)
                    else:
                        color_map={"📍 Default Rosso":"red","🚨 Emergenza":"red","🏠 Sede ANA":"green","👤 Volontario":"blue","🔥 Incendio":"orange","🌊 Alluvione":"blue","🚑 Sanitario":"white","📻 Radio":"cadetblue"}
                        color=color_map.get(punt,"red")
                        folium.Marker([la,lo],popup=f"{r['Postazione']}",icon=folium.Icon(color=color,icon="info-sign")).add_to(m_click)
                except:
                    pass

        # MOSTRA SUBITO PUNTATORE SCELTO AL CLICK PRECEDENTE
        if st.session_state.clicked_lat and st.session_state.clicked_lon:
            try:
                clat=float(st.session_state.clicked_lat)
                clon=float(st.session_state.clicked_lon)
                sel_ptr=st.session_state.selected_pointer
                sel_b64=st.session_state.selected_custom_b64
                if sel_ptr=="⭐ Personalizzato PNG" and sel_b64:
                    icon_url=f"data:image/png;base64,{sel_b64}"
                    icon=folium.CustomIcon(icon_url,icon_size=(50,50),icon_anchor=(25,50))
                    folium.Marker([clat,clon],popup=f"🎯 NUOVA - {sel_ptr}",icon=icon).add_to(m_click)
                else:
                    color_map={"📍 Default Rosso":"red","🚨 Emergenza":"red","🏠 Sede ANA":"green","👤 Volontario":"blue","🔥 Incendio":"orange","🌊 Alluvione":"blue","🚑 Sanitario":"white","📻 Radio":"cadetblue"}
                    color=color_map.get(sel_ptr,"red")
                    folium.Marker([clat,clon],popup=f"🎯 NUOVA - {sel_ptr}",icon=folium.Icon(color=color,icon="star",prefix="fa")).add_to(m_click)
                folium.CircleMarker([clat,clon],radius=25,color="yellow",fill=False,weight=4).add_to(m_click)
            except:
                pass

        st.markdown("**Clicca dove vuoi - Appare subito il PNG scelto! Pulsante ⛶ in alto a sinistra per fullscreen**")
        map_data=st_folium(m_click,width=800,height=600,returned_objects=["last_clicked"])

        if map_data and map_data.get("last_clicked"):
            clicked_lat=map_data["last_clicked"]["lat"]
            clicked_lon=map_data["last_clicked"]["lng"]
            st.session_state.clicked_lat=str(clicked_lat)
            st.session_state.clicked_lon=str(clicked_lon)
            with st.spinner("Recupero Comune e Via..."):
                rev_comune, rev_via=reverse_geocode(clicked_lat, clicked_lon)
                if rev_comune:
                    st.session_state.clicked_comune=rev_comune
                if rev_via:
                    st.session_state.clicked_via=rev_via
            st.success(f"✅ Cliccato con puntatore {st.session_state.selected_pointer}: Lat {clicked_lat:.6f}, Lon {clicked_lon:.6f} - {rev_comune} {rev_via}")
            st.rerun()
    except ImportError:
        st.warning("Installa folium per il click manuale")

    if st.session_state.clicked_lat and st.session_state.clicked_lon:
        st.markdown("#### 📍 Posizione selezionata con puntatore scelto")
        cc1,cc2,cc3,cc4=st.columns(4)
        cc1.metric("Latitudine",st.session_state.clicked_lat)
        cc2.metric("Longitudine",st.session_state.clicked_lon)
        cc3.metric("Comune",st.session_state.clicked_comune or "Non rilevato")
        cc4.metric("Via",st.session_state.clicked_via or "Non rilevata")
        st.markdown(f"**Puntatore scelto:** {st.session_state.selected_pointer}")
        if st.session_state.selected_custom_b64:
            st.image(f"data:image/png;base64,{st.session_state.selected_custom_b64}",width=50)

    st.divider()
    st.markdown("#### 3️⃣ Dati Postazione - Auto-compilati dal click + PNG scelto")

    c1,c2=st.columns(2)
    with c1:
        if st.session_state.clicked_comune:
            comune_default=st.session_state.clicked_comune
            if comune_default in COMUNI_TUTTI:
                idx_com=COMUNI_TUTTI.index(comune_default)
            else:
                idx_com=0
            comune=st.selectbox("Comune *",COMUNI_TUTTI,index=idx_com,key="comune_map")
        else:
            comune=st.selectbox("Comune *",COMUNI_TUTTI,key="comune_map")
    with c2:
        with st.spinner(f"Carico vie di {comune}..."):
            vie=get_vie_comune(comune)
        if st.session_state.clicked_via and st.session_state.clicked_via in vie:
            idx_via=vie.index(st.session_state.clicked_via)
            via=st.selectbox(f"Via * ({len(vie)-1} vie)",vie,index=idx_via,key="via_map")
        else:
            via=st.selectbox(f"Via * ({len(vie)-1} vie)",vie,key="via_map")
        if via=="-- Seleziona Via --":
            via_man=st.text_input("Via manuale",value=st.session_state.clicked_via,key="via_man_map")
            via_f=via_man if via_man else via
        else:
            via_f=via

    with st.form("form_post"):
        st.markdown("#### Conferma e salva con PNG scelto al click")
        nome=st.text_input("Nome Postazione *")
        cc1,cc2=st.columns(2)
        with cc1:
            lat_val=st.session_state.clicked_lat if st.session_state.clicked_lat else ""
            lon_val=st.session_state.clicked_lon if st.session_state.clicked_lon else ""
            lat=st.text_input("Lat *",value=lat_val,placeholder="Clicca mappa",key="lat_new")
            lon=st.text_input("Lon *",value=lon_val,placeholder="Clicca mappa",key="lon_new")
        with cc2:
            resp=st.text_input("Responsabile")
            st.markdown(f"**Puntatore che apparirà:** {st.session_state.selected_pointer}")
        if st.form_submit_button("➕ Aggiungi e Visualizza Subito con PNG"):
            if nome and lat and lon:
                custom_b64=st.session_state.selected_custom_b64 if st.session_state.selected_pointer=="⭐ Personalizzato PNG" else ""
                new_post={
                 "Postazione":nome,"Comune":comune,"Via":via_f,
                 "Latitudine":lat,"Longitudine":lon,
                 "Responsabile":resp,"Puntatore":st.session_state.selected_pointer,"CustomPNG":custom_b64
                }
                st.session_state.postazioni.append(new_post)
                save_json(FILE_POST,st.session_state.postazioni)
                st.session_state.last_postazione=new_post
                st.session_state.clicked_lat=""
                st.session_state.clicked_lon=""
                st.session_state.clicked_comune=""
                st.session_state.clicked_via=""
                st.success(f"✅ {nome} aggiunta con {st.session_state.selected_pointer}!")
                st.rerun()
            else:
                st.error("Compila Nome, Lat, Lon! Clicca sulla mappa!")

    if st.session_state.postazioni:
        df=pd.DataFrame(st.session_state.postazioni)
        st.markdown(f"### 📍 Mappa Finale - {len(df)} Postazioni - Fullscreen ⛶")
        tipo_mappa=st.selectbox("Tipo Mappa",["OpenStreetMap","Google Stradale","Google Satellite"],key="tipo_mappa")
        try:
            import folium
            from streamlit_folium import st_folium
            from folium.plugins import Fullscreen
            if st.session_state.last_postazione:
                try:
                    lat_c=float(str(st.session_state.last_postazione["Latitudine"]).replace(",","."))
                    lon_c=float(str(st.session_state.last_postazione["Longitudine"]).replace(",","."))
                    zoom=15
                except:
                    lat_c=45.8205; lon_c=8.8255; zoom=12
            else:
                lat_c=45.8205; lon_c=8.8255; zoom=12
            if tipo_mappa=="OpenStreetMap":
                m=folium.Map(location=[lat_c,lon_c],zoom_start=zoom,tiles="OpenStreetMap")
            else:
                m=folium.Map(location=[lat_c,lon_c],zoom_start=zoom,tiles=None)
                if tipo_mappa=="Google Stradale":
                    url="https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}"
                    nome_t="Google Stradale"
                else:
                    url="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}"
                    nome_t="Google Satellite"
                folium.TileLayer(url,attr="Google",name=nome_t,max_zoom=20).add_to(m)
            Fullscreen(position="topleft").add_to(m)
            for idx, r in df.iterrows():
                try:
                    la=float(str(r["Latitudine"]).replace(",","."))
                    lo=float(str(r["Longitudine"]).replace(",","."))
                    popup_text=f"<b>{r['Postazione']}</b><br>{r['Comune']} - {r['Via']}"
                    puntatore=r.get("Puntatore","📍 Default Rosso")
                    custom_b64=r.get("CustomPNG","")
                    is_last=False
                    if st.session_state.last_postazione:
                        if r["Postazione"]==st.session_state.last_postazione["Postazione"]:
                            is_last=True
                    if puntatore=="⭐ Personalizzato PNG" and custom_b64:
                        try:
                            icon_url=f"data:image/png;base64,{custom_b64}"
                            icon=folium.CustomIcon(icon_url,icon_size=(40,40),icon_anchor=(20,40))
                            folium.Marker([la,lo],popup=folium.Popup(popup_text,max_width=300),icon=icon).add_to(m)
                        except:
                            folium.Marker([la,lo],popup=popup_text,icon=folium.Icon(color="red",icon="info-sign")).add_to(m)
                    else:
                        color_map={"📍 Default Rosso":"red","🚨 Emergenza":"red","🏠 Sede ANA":"green","👤 Volontario":"blue","🔥 Incendio":"orange","🌊 Alluvione":"blue","🚑 Sanitario":"white","📻 Radio":"cadetblue"}
                        color=color_map.get(puntatore,"red")
                        if is_last:
                            folium.Marker([la,lo],popup=folium.Popup(f"🎯 ULTIMA<br>{popup_text}",max_width=300),icon=folium.Icon(color=color,icon="star",prefix="fa")).add_to(m)
                            folium.CircleMarker([la,lo],radius=20,color="yellow",fill=False,weight=3).add_to(m)
                        else:
                            folium.Marker([la,lo],popup=popup_text,icon=folium.Icon(color=color,icon="info-sign")).add_to(m)
                except:
                    pass
            st_folium(m,width=800,height=600,returned_objects=[])
        except ImportError:
            st.map(df.rename(columns={"Latitudine":"lat","Longitudine":"lon"}))
        st.dataframe(df.drop(columns=["CustomPNG"],errors="ignore"),use_container_width=True)
    torna("bottom_map")

elif scelta=="Volontari":
    torna("top_vol")
    tab1,tab2,tab3=st.tabs(["Anagrafica","Contatti + Vie","Ruolo"])
    with tab1:
        with st.container(border=True):
            cc1,cc2=st.columns(2)
            with cc1:
                nome=st.text_input("Nome *",key="nome_anag")
                cognome=st.text_input("Cognome *",key="cogn_anag")
                cf=st.text_input("CF",key="cf_anag")
            with cc2:
                data_nasc=st.date_input("Data Nascita",value=date(1980,1,1),key="data_anag")
                luogo_nasc=st.text_input("Luogo Nascita",key="luogo_anag")
                sesso=st.selectbox("Sesso",["M","F"],key="sesso_anag")
    with tab2:
        with st.container(border=True):
            cc1,cc2=st.columns(2)
            with cc1:
                cell=st.text_input("Cellulare *",key="cell_cont")
                email=st.text_input("Email",key="email_cont")
            with cc2:
                comune_cont=st.selectbox("Comune Residenza *",COMUNI_TUTTI,key="comune_cont")
                with st.spinner(f"Carico vie {comune_cont}..."):
                    vie_cont=get_vie_comune(comune_cont)
                via_cont=st.selectbox(f"Via - {comune_cont}",vie_cont,key="via_cont")
                if via_cont=="-- Seleziona Via --":
                    via_man_cont=st.text_input("Via manuale",key="via_man_cont")
                    via_f_cont=via_man_cont if via_man_cont else via_cont
                else:
                    via_f_cont=via_cont
                civico=st.text_input("Civico",key="civ_cont")
    with tab3:
        with st.container(border=True):
            cc1,cc2=st.columns(2)
            with cc1:
                ruolo=st.selectbox("Ruolo *",["Volontario","Caposquadra","Coordinatore","Autista","Radio"],key="ruolo_4")
                spec=st.selectbox("Specializzazione",["AIB","Cinofilo","Prot Civile","Sanitario","Nessuna"],key="spec_4")
            with cc2:
                assoc=st.text_input("Associazione",value="ANA Varese",key="assoc_3")
                gruppo=st.selectbox("Gruppo",["Varese","Busto","Gallarate","Luino","Saronno","Altro"],key="gruppo_3")
    st.divider()
    with st.form("form_vol"):
        if st.form_submit_button("SALVA VOLONTARIO",use_container_width=True,type="primary"):
            if nome and cognome and cell:
                nome_completo=f"{nome} {cognome}"
                st.session_state.dati.append({
                 "Nome":nome_completo,"CF":cf,"DataNascita":str(data_nasc),
                 "Cellulare":cell,"Email":email,"Comune":comune_cont,
                 "Via":via_f_cont,"Civico":civico,"Ruolo":ruolo,
                 "Specializzazione":spec,"Associazione":assoc,"Gruppo":gruppo
                })
                save_json(FILE_DATI,st.session_state.dati)
                if nome_completo not in st.session_state.mem_nomi:
                    st.session_state.mem_nomi.append(nome_completo)
                    save_json(FILE_NOMI,st.session_state.mem_nomi)
                st.success(f"Aggiunto {nome_completo}!")
                st.rerun()
    if st.session_state.dati:
        st.dataframe(pd.DataFrame(st.session_state.dati),use_container_width=True)
    torna("bottom_vol")

elif scelta=="Tabella Interventi Emergenza":
    torna("top_tab")
    st.markdown("### 📋 TABELLA INTERVENTI CON LOGHI PNG")
    if not st.session_state.emergenze_lista:
        st.warning("Nessun intervento ancora inserito!")
    else:
        df=pd.DataFrame(st.session_state.emergenze_lista)
        cc1,cc2,cc3=st.columns(3)
        with cc1:
            filtro_comune=st.selectbox("Filtra Comune",["Tutti"]+sorted(df["Comune"].unique().tolist()))
        with cc2:
            filtro_tipo=st.selectbox("Filtra Tipo",["Tutti"]+sorted(df["Tipo"].unique().tolist()))
        with cc3:
            ricerca=st.text_input("🔍 Cerca")
        df_f=df.copy()
        if filtro_comune!="Tutti":
            df_f=df_f[df_f["Comune"]==filtro_comune]
        if filtro_tipo!="Tutti":
            df_f=df_f[df_f["Tipo"]==filtro_tipo]
        if ricerca:
            df_f=df_f[df_f.apply(lambda row: ricerca.lower() in str(row["Descrizione"]).lower(),axis=1)]
        st.markdown(f"**Totale: {len(df)} | Filtrati: {len(df_f)}**")
        for idx, row in df_f.iterrows():
            c1,c2,c3=st.columns([1,3,2])
            with c1:
                try:
                    st.image(row.get("LogoPNG",""),width=50)
                except:
                    st.markdown(f"## {row.get('Logo','🚨')}")
            with c2:
                st.markdown(f"**{row.get('Tipo','')} - {row.get('Comune','')}**")
                st.caption(f"{row.get('Data','')} {row.get('Via','')}")
            with c3:
                st.caption(row.get('Descrizione','')[:100])
        st.divider()
        st.dataframe(df_f,use_container_width=True,hide_index=True)
        out=BytesIO()
        df_f.to_excel(out,index=False,engine="openpyxl")
        st.download_button("📥 Scarica Excel",out.getvalue(),file_name=f"emergenze_{date.today()}.xlsx",mime=MIME_SHORT,use_container_width=True)
    torna("bottom_tab")

elif scelta=="Backup":
    torna("top_back")
    st.markdown("### Backup Completo")
    if st.button("Crea Backup Completo",use_container_width=True,type="primary"):
        output=BytesIO()
        with pd.ExcelWriter(output,engine="openpyxl") as writer:
            if st.session_state.dati:
                pd.DataFrame(st.session_state.dati).to_excel(writer,sheet_name="Volontari",index=False)
            if st.session_state.postazioni:
                pd.DataFrame(st.session_state.postazioni).to_excel(writer,sheet_name="Postazioni",index=False)
            if st.session_state.emergenze_lista:
                pd.DataFrame(st.session_state.emergenze_lista).to_excel(writer,sheet_name="Emergenze",index=False)
            if st.session_state.radio_db:
                pd.DataFrame(st.session_state.radio_db).to_excel(writer,sheet_name="DB_Radio",index=False)
        st.session_state.backup_bytes=output.getvalue()
        st.success("Backup creato!")
    if "backup_bytes" in st.session_state:
        fname=f"backup_{date.today()}.xlsx"
        st.download_button("Scarica Backup",st.session_state.backup_bytes,file_name=fname,mime=MIME_SHORT,use_container_width=True)
    torna("bottom_back")
