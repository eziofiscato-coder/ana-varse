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
ICONS={"volontario":{"nome":"Volontario","icon":"👤"},"sede":{"nome":"Sede","icon":"🏠"},"radio":{"nome":"Radio","icon":"📻"},"emergenza":{"nome":"Emergenza","icon":"🚨"},"postazione":{"nome":"Postazione","icon":"📍"},"incendio":{"nome":"Incendio","icon":"🔥"}}
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
        st.session_state.authenticated=False
        st.success("Logout effettuato!")
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.divider(); st.caption("💾 Dati memorizzati automaticamente!")
scelta=st.session_state.menu_scelta; st.markdown(f"## {scelta}"); st.divider()
COMUNI_TUTTI=load_comuni_italia(); MIME_SHORT="application/octet-stream"
if scelta=="Dashboard":
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Emergenze",len(st.session_state.emergenze_lista)); c2.metric("Postazioni",len(st.session_state.postazioni))
    c3.metric("Volontari",len(st.session_state.dati)); c4.metric("Radio",len(st.session_state.radio_db))
    c5,c6=st.columns(2); c5.metric("Eventi",len(st.session_state.eventi_lista)); c6.metric("Check-in",len(st.session_state.checkin_lista))
    st.info("✅ Tutti i dati memorizzati su disco! Non perdi più nulla al reboot.")
    if st.session_state.emergenze_lista:
        st.markdown("### Ultimi 5 Interventi Emergenza")
        df_last=pd.DataFrame(st.session_state.emergenze_lista[-5:])
        st.dataframe(df_last,use_container_width=True)
        if st.button("📋 Vedi Tabella Completa Emergenze",use_container_width=True):
            st.session_state.menu_scelta="Tabella Interventi Emergenza"; st.rerun()
elif scelta=="Emergenze con Loghi":
    torna("top_em")
    c1,c2=st.columns(2)
    with c1: comune=st.selectbox("Comune *",COMUNI_TUTTI,key="comune_em")
    with c2:
        with st.spinner(f"Carico TUTTE le vie di {comune}..."): vie=get_vie_comune(comune)
        if len(vie)>10: st.success(f"Trovate {len(vie)-1} vie per {comune} - TUTTE!")
        else: st.warning(f"Solo {len(vie)-1} vie default - scrivi manuale")
        via=st.selectbox(f"Via * ({comune}) - {len(vie)-1} vie totali",vie,key="via_em")
        if via=="-- Seleziona Via --":
            via_man=st.text_input("Via manuale se non in lista",key="via_man_em"); via_f=via_man if via_man else via
        else: via_f=via
    with st.form("form_em"):
        data_em=st.date_input("Data",value=date.today())
        tipo=st.selectbox("Tipo",list(ICONS.keys()),format_func=lambda x: ICONS[x]["icon"]+" "+ICONS[x]["nome"])
        desc=st.text_area("Descrizione",value=f"{comune} - {via_f}")
        if st.form_submit_button("Salva con Logo"):
            if via_f!="-- Seleziona Via --" and via_f!="":
                st.session_state.emergenze_lista.append({"Data":str(data_em),"Logo":ICONS[tipo]["icon"],"Comune":comune,"Via":via_f,"Tipo":ICONS[tipo]["nome"],"Descrizione":desc})
                save_json(FILE_EMER,st.session_state.emergenze_lista); st.success("Salvata e memorizzata!"); st.rerun()
    if st.session_state.emergenze_lista: st.dataframe(pd.DataFrame(st.session_state.emergenze_lista),use_container_width=True)
    torna("bottom_em")
elif scelta=="Mappa Postazioni":
    torna("top_map")
    c1,c2=st.columns(2)
    with c1: comune=st.selectbox("Comune *",COMUNI_TUTTI,key="comune_map")
    with c2:
        with st.spinner(f"Carico TUTTE le vie di {comune}..."): vie=get_vie_comune(comune)
        if len(vie)>10: st.success(f"Trovate {len(vie)-1} vie - TUTTE!")
        else: st.warning(f"Solo {len(vie)-1} vie default")
        via=st.selectbox(f"Via * ({comune}) - {len(vie)-1} vie",vie,key="via_map")
        if via=="-- Seleziona Via --":
            via_man=st.text_input("Via manuale",key="via_man_map"); via_f=via_man if via_man else via
        else: via_f=via
    with st.form("form_post"):
        nome=st.text_input("Nome Postazione *")
        col1,col2=st.columns(2)
        with col1: lat=st.text_input("Lat *",placeholder="45.8205")
        with col2: lon=st.text_input("Lon *",placeholder="8.8255")
        resp=st.text_input("Responsabile")
        if st.form_submit_button("Aggiungi alla Mappa"):
            if nome and lat and lon:
                st.session_state.postazioni.append({"Postazione":nome,"Comune":comune,"Via":via_f,"Latitudine":lat,"Longitudine":lon,"Responsabile":resp})
                save_json(FILE_POST,st.session_state.postazioni); st.success("Aggiunta e memorizzata!"); st.rerun()
    if st.session_state.postazioni:
        df=pd.DataFrame(st.session_state.postazioni)
        tipo=st.selectbox("Tipo Mappa",["OpenStreetMap","Google Stradale","Google Satellite"],key="tipo_mappa")
        try:
            import folium; from streamlit_folium import st_folium
            lat_c=45.8205; lon_c=8.8255
            if tipo=="OpenStreetMap": m=folium.Map(location=[lat_c,lon_c],zoom_start=12,tiles="OpenStreetMap")
            else:
                m=folium.Map(location=[lat_c,lon_c],zoom_start=12,tiles=None)
                if tipo=="Google Stradale": url="https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}"; nome_t="Google Stradale"
                else: url="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}"; nome_t="Google Satellite"
                folium.TileLayer(url,attr="Google",name=nome_t,max_zoom=20).add_to(m)
            for _,r in df.iterrows():
                try:
                    la=float(str(r["Latitudine"]).replace(",",".")); lo=float(str(r["Longitudine"]).replace(",","."))
                    folium.Marker([la,lo],popup=r["Postazione"]).add_to(m)
                except: pass
            st_folium(m,width=700,height=500)
        except ImportError: st.map(df.rename(columns={"Latitudine":"lat","Longitudine":"lon"}))
        st.dataframe(df,use_container_width=True)
    torna("bottom_map")
elif scelta=="Volontari":
    torna("top_vol")
    st.markdown("### Volontari - Sottomaschere + TUTTE LE VIE + MEMORIZZAZIONE")
    tab1,tab2,tab3=st.tabs(["Anagrafica","Contatti + Vie","Ruolo"])
    with tab1:
        with st.container(border=True):
            c1,c2=st.columns(2)
            with c1: nome=st.text_input("Nome *",key="nome_anag"); cognome=st.text_input("Cognome *",key="cogn_anag"); cf=st.text_input("CF",key="cf_anag")
            with c2: data_nasc=st.date_input("Data Nascita",value=date(1980,1,1),key="data_anag"); luogo_nasc=st.text_input("Luogo Nascita",key="luogo_anag"); sesso=st.selectbox("Sesso",["M","F"],key="sesso_anag")
    with tab2:
        with st.container(border=True):
            c1,c2=st.columns(2)
            with c1: cell=st.text_input("Cellulare *",key="cell_cont"); email=st.text_input("Email",key="email_cont")
            with c2:
                comune_cont=st.selectbox("Comune Residenza *",COMUNI_TUTTI,key="comune_cont")
                with st.spinner(f"Carico TUTTE le vie di {comune_cont}..."): vie_cont=get_vie_comune(comune_cont)
                if len(vie_cont)>10: st.success(f"{len(vie_cont)-1} vie trovate - TUTTE!")
                else: st.warning(f"Solo {len(vie_cont)-1} vie default")
                via_cont=st.selectbox(f"Via - {comune_cont} - {len(vie_cont)-1} vie totali",vie_cont,key="via_cont")
                if via_cont=="-- Seleziona Via --":
                    via_man_cont=st.text_input("Via manuale",key="via_man_cont"); via_f_cont=via_man_cont if via_man_cont else via_cont
                else: via_f_cont=via_cont
                civico=st.text_input("Civico",key="civ_cont")
    with tab3:
        with st.container(border=True):
            c1,c2=st.columns(2)
            with c1: ruolo=st.selectbox("Ruolo *",["Volontario","Caposquadra","Coordinatore","Autista","Radio"],key="ruolo_4"); spec=st.selectbox("Specializzazione",["AIB","Cinofilo","Prot Civile","Sanitario","Nessuna"],key="spec_4")
            with c2: assoc=st.text_input("Associazione",value="ANA Varese",key="assoc_3"); gruppo=st.selectbox("Gruppo",["Varese","Busto","Gallarate","Luino","Saronno","Altro"],key="gruppo_3")
    st.divider()
    with st.form("form_vol"):
        if st.form_submit_button("SALVA VOLONTARIO",use_container_width=True,type="primary"):
            if nome and cognome and cell:
                nome_completo=f"{nome} {cognome}"
                st.session_state.dati.append({"Nome":nome_completo,"CF":cf,"DataNascita":str(data_nasc),"Cellulare":cell,"Email":email,"Comune":comune_cont,"Via":via_f_cont,"Civico":civico,"Ruolo":ruolo,"Specializzazione":spec,"Associazione":assoc,"Gruppo":gruppo})
                save_json(FILE_DATI,st.session_state.dati)
                if nome_completo not in st.session_state.mem_nomi: st.session_state.mem_nomi.append(nome_completo); save_json(FILE_NOMI,st.session_state.mem_nomi)
                st.success(f"Aggiunto {nome_completo} e memorizzato!"); st.rerun()
    if st.session_state.dati: st.dataframe(pd.DataFrame(st.session_state.dati),use_container_width=True)
    torna("bottom_vol")
elif scelta=="DB Radio":
    torna("top_radio")
    st.markdown("### DB Radio - MEMORIZZAZIONE PERMANENTE")
    with st.form("form_radio"):
        c1,c2=st.columns(2)
        with c1: rid=st.text_input("Radio ID *",placeholder="R-01"); mod=st.text_input("Modello *",placeholder="Baofeng UV-5R")
        with c2: stato=st.selectbox("Stato",["Disponibile","In uso","Guasta"]); note=st.text_input("Note")
        if st.form_submit_button("Salva Radio"):
            if rid and mod:
                st.session_state.radio_db.append({"Radio ID":rid,"Modello":mod,"Stato":stato,"Note":note})
                save_json(FILE_RADIO,st.session_state.radio_db); st.success("Aggiunta e memorizzata!"); st.rerun()
    if st.session_state.radio_db:
        st.dataframe(pd.DataFrame(st.session_state.radio_db),use_container_width=True)
        st.success(f"✅ {len(st.session_state.radio_db)} radio memorizzate!")
    torna("bottom_radio")
elif scelta=="Distribuzione Radio":
    torna("top_dist")
    st.markdown("### Distribuzione - Modello agganciato a ID + MEMORIZZAZIONE")
    radio_map={}
    if st.session_state.radio_db:
        for r in st.session_state.radio_db: radio_map[r.get("Radio ID","")]=r.get("Modello","")
    with st.form("form_dist"):
        c1,c2=st.columns(2)
        with c1:
            if st.session_state.radio_db:
                lista_id=[r["Radio ID"] for r in st.session_state.radio_db]
                rid=st.selectbox("Radio ID *",lista_id,key="rid_dist"); modello_agg=radio_map.get(rid,"")
                st.text_input("Modello agganciato",value=modello_agg,disabled=True,key="mod_agg")
            else: rid=st.text_input("Radio ID *",key="rid_man"); modello_agg=st.text_input("Modello *",key="mod_man")
            ass=st.selectbox("Assegnato A *",["--"]+st.session_state.mem_nomi,key="ass_dist")
        with c2: posto=st.text_input("Postazione *",key="posto_dist"); canale=st.selectbox("Canale",["CH1 Emergenza","CH2 Logistica","CH3 Coord"],key="can_dist"); note_dist=st.text_input("Note",key="note_dist")
        if st.form_submit_button("Assegna Radio"):
            if rid and ass!="--" and posto:
                st.session_state.dist_radio.append({"RadioID":rid,"Modello":modello_agg,"Assegnatario":ass,"Postazione":posto,"Canale":canale,"Note":note_dist,"Data":str(date.today())})
                save_json(FILE_DIST,st.session_state.dist_radio); st.success(f"Radio {rid} - {modello_agg} assegnata!"); st.rerun()
    if st.session_state.dist_radio: st.dataframe(pd.DataFrame(st.session_state.dist_radio),use_container_width=True)
    torna("bottom_dist")
elif scelta=="Eventi":
    torna("top_eventi")
    c1,c2=st.columns(2)
    with c1: comune_ev=st.selectbox("Comune Evento *",COMUNI_TUTTI,key="comune_ev")
    with c2:
        with st.spinner(f"Carico TUTTE le vie di {comune_ev}..."): vie_ev=get_vie_comune(comune_ev)
        if len(vie_ev)>10: st.success(f"{len(vie_ev)-1} vie per {comune_ev} - TUTTE!")
        else: st.warning(f"Solo {len(vie_ev)-1} vie default")
        via_ev=st.selectbox(f"Via - {comune_ev} - {len(vie_ev)-1} vie",vie_ev,key="via_ev")
        if via_ev=="-- Seleziona Via --":
            via_man_ev=st.text_input("Via manuale evento",key="via_man_ev"); via_f_ev=via_man_ev if via_man_ev else via_ev
        else: via_f_ev=via_ev
    with st.form("form_eventi"):
        nome_ev=st.text_input("Nome Evento *"); data_ev=st.date_input("Data *",value=date.today()); resp_ev=st.text_input("Responsabile *")
        tipo_ev=st.selectbox("Tipo Evento",["Esercitazione","Intervento Reale","Formazione","Riunione","Altro"]); desc_ev=st.text_area("Descrizione")
        if st.form_submit_button("Salva Evento",type="primary"):
            if nome_ev and resp_ev:
                st.session_state.eventi_lista.append({"NomeEvento":nome_ev,"Data":str(data_ev),"Comune":comune_ev,"Via":via_f_ev,"Responsabile":resp_ev,"Tipo":tipo_ev,"Descrizione":desc_ev})
                save_json(FILE_EVENTI,st.session_state.eventi_lista); st.success("Evento salvato!"); st.rerun()
    if st.session_state.eventi_lista: st.dataframe(pd.DataFrame(st.session_state.eventi_lista),use_container_width=True)
    torna("bottom_eventi")
elif scelta=="Check-in":
    torna("top_checkin")
    if st.session_state.dati: vol_check=st.selectbox("Volontario *",[d["Nome"] for d in st.session_state.dati],key="vol_check")
    else: vol_check=st.text_input("Volontario *",key="vol_check_man")
    if st.session_state.eventi_lista: evento_check=st.selectbox("Evento *",[e["NomeEvento"] for e in st.session_state.eventi_lista],key="evento_check")
    else: evento_check=st.text_input("Evento *",key="evento_check_man")
    with st.form("form_checkin"):
        data_check=st.date_input("Data *",value=date.today()); ora_in=st.time_input("Ora Ingresso",value=datetime.now().time()); stato_check=st.selectbox("Stato",["Presente","Arrivato","Partito","Assente"])
        if st.form_submit_button("Registra Check-in",type="primary"):
            if vol_check and evento_check:
                st.session_state.checkin_lista.append({"Volontario":vol_check,"Evento":evento_check,"Data":str(data_check),"OraIngresso":str(ora_in),"Stato":stato_check})
                save_json(FILE_CHECK,st.session_state.checkin_lista); st.success("Check-in registrato!"); st.rerun()
    if st.session_state.checkin_lista: st.dataframe(pd.DataFrame(st.session_state.checkin_lista),use_container_width=True)
    torna("bottom_checkin")
elif scelta=="Tabella Interventi Emergenza":
    torna("top_tab")
    st.markdown("### 📋 TABELLA COMPLETA INTERVENTI EMERGENZA")
    st.info("Qui vedi TUTTI gli interventi emergenza inseriti, con filtri e ricerca")
    if not st.session_state.emergenze_lista:
        st.warning("Nessun intervento emergenza ancora inserito! Vai in Emergenze con Loghi per inserirne uno.")
    else:
        df=pd.DataFrame(st.session_state.emergenze_lista)
        c1,c2,c3=st.columns(3)
        with c1: filtro_comune=st.selectbox("Filtra per Comune",["Tutti"]+sorted(df["Comune"].unique().tolist()))
        with c2: filtro_tipo=st.selectbox("Filtra per Tipo",["Tutti"]+sorted(df["Tipo"].unique().tolist()))
        with c3: ricerca=st.text_input("🔍 Cerca in Descrizione/Via")
        df_filtrato=df.copy()
        if filtro_comune!="Tutti": df_filtrato=df_filtrato[df_filtrato["Comune"]==filtro_comune]
        if filtro_tipo!="Tutti": df_filtrato=df_filtrato[df_filtrato["Tipo"]==filtro_tipo]
        if ricerca: df_filtrato=df_filtrato[df_filtrato.apply(lambda row: ricerca.lower() in str(row["Descrizione"]).lower() or ricerca.lower() in str(row["Via"]).lower() or ricerca.lower() in str(row["Comune"]).lower(), axis=1)]
        st.markdown(f"**Totale interventi: {len(df)} | Filtrati: {len(df_filtrato)}**")
        st.dataframe(df_filtrato,use_container_width=True,hide_index=True)
        c1,c2,c3=st.columns(3)
        with c1:
            out=BytesIO(); df_filtrato.to_excel(out,index=False,engine="openpyxl")
            st.download_button("📥 Scarica Excel Filtrato",out.getvalue(),file_name=f"interventi_emergenza_{date.today()}.xlsx",mime=MIME_SHORT,use_container_width=True)
        with c2:
            if st.button("🗑️ Cancella Filtri",use_container_width=True): st.rerun()
        with c3:
            if st.button("📊 Statistiche",use_container_width=True):
                st.markdown("#### Statistiche Interventi")
                st.write(f"Per Comune: {df['Comune'].value_counts().to_dict()}")
                st.write(f"Per Tipo: {df['Tipo'].value_counts().to_dict()}")
    torna("bottom_tab")
elif scelta=="Backup":
    torna("top_back")
    st.markdown("### Backup Completo + Singoli + Memorizzazione Permanente")
    st.info("✅ Tutti i dati salvati automaticamente in JSON!")
    if st.button("Crea Backup Completo",use_container_width=True,type="primary"):
        output=BytesIO()
        with pd.ExcelWriter(output,engine="openpyxl") as writer:
            if st.session_state.dati: pd.DataFrame(st.session_state.dati).to_excel(writer,sheet_name="Volontari",index=False)
            if st.session_state.postazioni: pd.DataFrame(st.session_state.postazioni).to_excel(writer,sheet_name="Postazioni",index=False)
            if st.session_state.emergenze_lista: pd.DataFrame(st.session_state.emergenze_lista).to_excel(writer,sheet_name="Emergenze",index=False)
            if st.session_state.radio_db: pd.DataFrame(st.session_state.radio_db).to_excel(writer,sheet_name="DB_Radio",index=False)
            if st.session_state.dist_radio: pd.DataFrame(st.session_state.dist_radio).to_excel(writer,sheet_name="Distribuzione",index=False)
            if st.session_state.eventi_lista: pd.DataFrame(st.session_state.eventi_lista).to_excel(writer,sheet_name="Eventi",index=False)
            if st.session_state.checkin_lista: pd.DataFrame(st.session_state.checkin_lista).to_excel(writer,sheet_name="Checkin",index=False)
        st.session_state.backup_bytes=output.getvalue(); st.success("Backup creato!")
    if "backup_bytes" in st.session_state:
        fname=f"backup_{date.today()}.xlsx"
        st.download_button("Scarica Backup Completo",st.session_state.backup_bytes,file_name=fname,mime=MIME_SHORT,use_container_width=True)
    torna("bottom_back")
