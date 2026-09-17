import streamlit as st
import pandas as pd
from datetime import datetime, date
from io import BytesIO
import base64, os, uuid, json, requests

st.set_page_config(page_title="ANA Varese", page_icon="🟢", layout="wide")

st.markdown("""
<style>
.stApp{background-color:#e8f5e9!important;}
.main.block-container{background-color:white!important; border-radius:18px; padding:25px!important;}
[data-testid="stSidebar"]{background-color:#a5d6a7!important; border-right:4px solid #2e7d32!important;}
.stForm{background-color:#c8e6c9!important; border:3px solid #2e7d32!important; border-radius:15px!important; padding:20px!important;}
.stTextInput input,.stSelectbox div[data-baseweb="select"],.stDateInput input,.stNumberInput input,.stTextArea textarea {
    background-color:white!important; color:#1b5e20!important; border:2px solid #2e7d32!important;
}
.stButton>button{background-color:#2e7d32!important; color:white!important; border:2px solid #1b5e20!important; font-weight:bold!important; border-radius:12px!important; min-height:60px!important;}
div[data-testid="stFormSubmitButton"]>button{background-color:#d32f2f!important; color:white!important;}
h1,h2,h3{color:#1b5e20!important;}
</style>
""", unsafe_allow_html=True)

# ELENCO COMUNI ITALIANI - COMBO AGGANCIATA
COMUNI_VARESE = ["Varese","Busto Arsizio","Gallarate","Saronno","Cassano Magnago","Tradate","Somma Lombardo","Malnate","Luino","Samarate","Laveno-Mombello","Cittiglio","Besozzo","Gavirate","Vergiate","Sesto Calende","Besnate","Cardano al Campo","Cavaria con Premezzo","Castellanza","Lonate Pozzolo","Fagnano Olona","Caronno Pertusella","Gerenzano","Origgio","Uboldo","Cislago","Mozzate","Gornate Olona","Castelseprio","Gazzada Schianno","Bodio Lomnago","Buguggiate","Azzate","Brunello","Morazzone","Caravate","Cocquio-Trevisago","Cuvio","Cuveglio","Rancio Valcuvia","Brinzio","Bedero Valcuvia","Masciago Primo","Ferrera di Varese","Maccagno con Pino e Veddasca","Tronzano Lago Maggiore","Pino sulla Sponda","Curiglia con Monteviasco","Dumenza","Agra","Brezzo di Bedero","Germignaga","Brezzo di Bedero","Montegrino Valtravaglia","Grantola","Mesenzana","Brissago-Valtravaglia","Cassano Valcuvia","Duno","Porto Valtravaglia","Castelveccana","Laveno-Mombello","Leggiuno","Monvalle","Besozzo","Brebbia","Malnate","Bregnano","Castronno","Albizzate","Sumirago","Jerago con Orago","Oggiona con Santo Stefano","Solbiate Arno","Carnago","Caravate","Gemonio","Azzio","Orino","Cocquio","Barasso","Luvinate","Casciago","Varese"]

COMUNI_LOMBARDIA = COMUNI_VARESE + ["Milano","Como","Lecco","Bergamo","Brescia","Pavia","Lodi","Cremona","Mantova","Monza","Sondrio","Varese","Busto Arsizio","Gallarate"]

# FUNZIONE PER PRENDERE VIE DA OVERPASS API - COMBO AGGANCIATA
@st.cache_data(ttl=3600)
def get_vie_comune(comune):
    try:
        # Overpass query per vie del comune
        query = f"""
        [out:json][timeout:10];
        area[name="{comune}"][admin_level=8]->.searchArea;
        (
          way(area.searchArea)["highway"]["name"];
        );
        out 100;
        """
        url = "https://overpass-api.de/api/interpreter"
        r = requests.post(url, data={"data": query}, timeout=8)
        if r.status_code == 200:
            data = r.json()
            vie = sorted(list(set([el["tags"]["name"] for el in data.get("elements", []) if "tags" in el and "name" in el["tags"]])))
            if vie:
                return ["-- Seleziona Via --"] + vie[:200] # prime 200
        return ["-- Seleziona Via --", "Via Roma", "Via Garibaldi", "Via Milano", "Via Verdi", "Via Dante", "Via Volta", "Via Sacco", "Corso Matteotti", "Piazza Libertà", "Via XX Settembre"]
    except:
        return ["-- Seleziona Via --", "Via Roma", "Via Garibaldi", "Via Milano", "Via Verdi", "Via Dante", "Via Sacco", "Corso Matteotti"]

ICONS = {
 "volontario": {"nome":"Volontario","icon":"👤"}, "sede": {"nome":"Sede","icon":"🏠"},
 "radio": {"nome":"Radio","icon":"📻"}, "emergenza": {"nome":"Emergenza","icon":"🚨"},
 "protezione_civile": {"nome":"Prot Civile","icon":"🛡️"}, "ospedale": {"nome":"Ospedale","icon":"🏥"},
 "postazione": {"nome":"Postazione","icon":"📍"}, "auto": {"nome":"Auto","icon":"🚗"},
 "elicottero": {"nome":"Elicottero","icon":"🚁"}, "incendio": {"nome":"Incendio","icon":"🔥"},
 "alluvione": {"nome":"Alluvione","icon":"🌊"}, "campo_base": {"nome":"Campo Base","icon":"⛺"},
}

for k,v in [("authenticated",False),("emergenze_lista",[]),("interventi_lista",[]),("dati",[]),("mem_nomi",["Mario Rossi","Luigi Bianchi","Giuseppe Verdi"]),("postazioni",[]),("radio_db",[]),("dist_radio",[]),("menu_scelta","🏠 Dashboard"),("selected_postazione",None),("comune_sel","Varese")]:
    if k not in st.session_state:
        st.session_state[k]=v

def torna_dashboard(suffix=""):
    if st.button("🏠 Torna Dashboard", use_container_width=True, key=f"back_{suffix}_{uuid.uuid4().hex[:8]}"):
        st.session_state.menu_scelta="🏠 Dashboard"; st.rerun()

def header_3_loghi():
    c1,c2,c3=st.columns([1,1,1])
    try:
        if os.path.exists("logo.png"): c1.image("logo.png", width=80)
        else: c1.markdown("**ANA Varese**")
    except: c1.markdown("**Logo 1**")
    try:
        if os.path.exists("logo2.png"): c2.image("logo2.png", width=80)
        else: c2.markdown("**Logo 2**")
    except: c2.markdown("**Logo 2**")
    try:
        if os.path.exists("logo_pc_lombardia.png"): c3.image("logo_pc_lombardia.png", width=80)
        else: c3.markdown("**Prot Civile Lombardia**")
    except: c3.markdown("**Prot Civile**")

if not st.session_state.authenticated:
    st.markdown("""<style>[data-testid="stSidebar"]{display:none;}</style>""", unsafe_allow_html=True)
    header_3_loghi()
    st.divider()
    st.markdown("<h2 style='text-align:center; color:#2e7d32;'>Accesso Riservato - admin / ana2024</h2>", unsafe_allow_html=True)
    c1,c2,c3=st.columns([1,2,1])
    with c2:
        with st.form("login_form"):
            u=st.text_input("Username", value="admin"); p=st.text_input("Password", type="password", value="ana2024")
            if st.form_submit_button("Accedi", use_container_width=True, type="primary"):
                if u=="admin" and p=="ana2024":
                    st.session_state.authenticated=True; st.rerun()
                else: st.error("admin / ana2024")
    st.stop()

header_3_loghi()
st.divider()

with st.sidebar:
    st.image("logo.png", width=100) if os.path.exists("logo.png") else st.markdown("### ANA Varese")
    opzioni=["🏠 Dashboard","🚨 Emergenze con Loghi","🗺️ Mappa Postazioni","🚨 Interventi Emergenza","👥 Volontari","📻 DB Radio","📦 Distribuzione Radio","💾 Backup"]
    idx = opzioni.index(st.session_state.menu_scelta) if st.session_state.menu_scelta in opzioni else 0
    sel=st.radio("MENU", opzioni, index=idx)
    if sel!=st.session_state.menu_scelta:
        st.session_state.menu_scelta=sel; st.rerun()
    if st.button("Logout", use_container_width=True, type="primary", key="logout_btn"):
        st.session_state.authenticated=False; st.rerun()

scelta=st.session_state.menu_scelta
st.markdown(f"## {scelta}")
st.divider()

if scelta=="🏠 Dashboard":
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Interventi", len(st.session_state.interventi_lista))
    c2.metric("Emergenze", len(st.session_state.emergenze_lista))
    c3.metric("Volontari", len(st.session_state.mem_nomi))
    c4.metric("Postazioni", len(st.session_state.postazioni))
    r1c1,r1c2,r1c3,r1c4=st.columns(4)
    with r1c1:
        if st.button("Emergenze con Loghi", key="q1", use_container_width=True):
            st.session_state.menu_scelta="🚨 Emergenze con Loghi"; st.rerun()
    with r1c2:
        if st.button("Mappa Postazioni", key="q2", use_container_width=True):
            st.session_state.menu_scelta="🗺️ Mappa Postazioni"; st.rerun()
    with r1c3:
        if st.button("Interventi", key="q3", use_container_width=True):
            st.session_state.menu_scelta="🚨 Interventi Emergenza"; st.rerun()
    with r1c4:
        if st.button("Volontari", key="q4", use_container_width=True):
            st.session_state.menu_scelta="👥 Volontari"; st.rerun()

elif scelta=="🚨 Emergenze con Loghi":
    torna_dashboard("top_em")
    st.markdown("#### Libreria Loghi")
    cols=st.columns(6)
    for i,(k,v) in enumerate(ICONS.items()):
        with cols[i%6]:
            st.markdown(f"<div style='background:white; border:2px solid #2e7d32; border-radius:10px; padding:8px; text-align:center;'><div style='font-size:28px;'>{v['icon']}</div><div style='font-size:10px;'>{v['nome']}</div></div>", unsafe_allow_html=True)
    st.divider()
    # COMUNE COMBO AGGANCIATA + VIA COMBO AGGANCIATA
    st.markdown("### Form con Comune e Via combo agganciate")
    c_com1,c_com2=st.columns(2)
    with c_com1:
        comune_sel = st.selectbox("Comune * (combo con ricerca)", COMUNI_VARESE, index=COMUNI_VARESE.index("Varese") if "Varese" in COMUNI_VARESE else 0, key="comune_combo")
        st.session_state.comune_sel = comune_sel
    with c_com2:
        with st.spinner(f"Carico vie di {comune_sel}..."):
            vie_list = get_vie_comune(comune_sel)
        via_sel = st.selectbox(f"Via * (combo agganciata a {comune_sel} - {len(vie_list)-1} vie)", vie_list, key="via_combo")
        if via_sel == "-- Seleziona Via --":
            via_manual = st.text_input("Oppure scrivi Via manualmente", placeholder="Via Sacco 5")
            via_final = via_manual if via_manual else via_sel
        else:
            via_final = via_sel
    with st.form("form_em", clear_on_submit=True):
        c1,c2,c3=st.columns(3)
        with c1: data_em=st.date_input("Data *", value=date.today()); st.text_input("Comune *", value=comune_sel, disabled=True)
        with c2: st.text_input("Via *", value=via_final, disabled=True); tipo_key=st.selectbox("Tipo + Logo *", list(ICONS.keys()), format_func=lambda x: f"{ICONS[x]['icon']} {ICONS[x]['nome']}")
        with c3: odv=st.selectbox("ODV", ["ANA Varese","Prot Civile","Altro"]); st.markdown(f"<div style='background:#c8e6c9; border:3px solid #2e7d32; border-radius:12px; padding:10px; text-align:center;'><div style='font-size:40px;'>{ICONS[tipo_key]['icon']}</div><b>{ICONS[tipo_key]['nome']}</b></div>", unsafe_allow_html=True)
        desc=st.text_area("Descrizione *", height=80, value=f"{comune_sel} - {via_final}")
        if st.form_submit_button("SALVA CON LOGO", use_container_width=True, type="primary"):
            if via_final!= "-- Seleziona Via --" and desc:
                st.session_state.emergenze_lista.append({"Data":str(data_em),"Logo":ICONS[tipo_key]['icon'],"Tipo":ICONS[tipo_key]['nome'],"Comune":comune_sel,"Via":via_final,"ODV":odv,"Descrizione":desc})
                st.success(f"Salvata {ICONS[tipo_key]['icon']} {comune_sel} {via_final}!"); st.balloons(); st.rerun()
    if st.session_state.emergenze_lista:
        df=pd.DataFrame(st.session_state.emergenze_lista)
        st.dataframe(df, use_container_width=True)
    torna_dashboard("bottom_em")

elif scelta=="🗺️ Mappa Postazioni":
    torna_dashboard("top_map")
    with st.container(border=True):
        st.markdown("#### Mappa FULLSCREEN - Google Map e OpenStreetMap + Comune e Via combo")
        st.info("Se non vedi la mappa, aggiungi al file requirements.txt su GitHub: folium e streamlit-folium")
        # COMBO COMUNE E VIA AGGANCIATE ANCHE QUI
        c_com1,c_com2=st.columns(2)
        with c_com1:
            comune_map = st.selectbox("Comune * (combo)", COMUNI_VARESE, index=0, key="comune_map")
        with c_com2:
            vie_map = get_vie_comune(comune_map)
            via_map = st.selectbox(f"Via * (combo {comune_map})", vie_map, key="via_map")
        with st.form("form_post", clear_on_submit=True):
            c1,c2,c3=st.columns(3)
            with c1: nome_post=st.text_input("Nome Postazione *"); st.text_input("Comune *", value=comune_map, disabled=True)
            with c2: st.text_input("Via *", value=via_map if via_map!="-- Seleziona Via --" else "", disabled=True); lat=st.text_input("Latitudine *", placeholder="45.8205"); lon=st.text_input("Longitudine *", placeholder="8.8255")
            with c3: resp_post=st.text_input("Responsabile"); radio_post=st.text_input("Radio"); tipo_post=st.selectbox("Tipo", ["Controllo accessi","Viabilita","Sicurezza","Logistica","COC","Altro"])
            if st.form_submit_button("Aggiungi alla Mappa", use_container_width=True, type="primary"):
                if nome_post and lat and lon:
                    st.session_state.postazioni.append({"Data":str(date.today()),"Postazione":nome_post,"Comune":comune_map,"Via":via_map,"Latitudine":lat,"Longitudine":lon,"Responsabile":resp_post,"Radio":radio_post,"Tipo":tipo_post})
                    st.success(f"{nome_post} aggiunta!"); st.rerun()
        if st.session_state.postazioni:
            df_post=pd.DataFrame(st.session_state.postazioni)
            # MAPPA FOLIUM CON GOOGLE E OSM
            map_type=st.selectbox("Tipo Mappa:", ["OpenStreetMap","Google Stradale","Google Satellite","Google Ibrida","Google Rilievo"], key="map_type_sel")
            try:
                import folium
                from streamlit_folium import st_folium
                center_lat, center_lon=45.8205, 8.8255; zoom=12
                if map_type=="OpenStreetMap": m=folium.Map(location=[center_lat, center_lon], zoom_start=zoom, tiles="OpenStreet