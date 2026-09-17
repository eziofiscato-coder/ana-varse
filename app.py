import streamlit as st
import pandas as pd
from datetime import date
from io import BytesIO
import os
import uuid
import requests

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
    min-height:60px!important;
}
div[data-testid="stFormSubmitButton"]>button{
    background-color:#d32f2f!important;
    color:white!important;
}
</style>
""", unsafe_allow_html=True)

COMUNI = [
    "Varese","Busto Arsizio","Gallarate","Saronno",
    "Cassano Magnago","Tradate","Somma Lombardo",
    "Malnate","Luino","Samarate","Laveno-Mombello",
    "Cittiglio","Besozzo","Gavirate","Vergiate",
    "Sesto Calende","Besnate","Cardano al Campo",
    "Castellanza","Lonate Pozzolo","Fagnano Olona",
    "Caronno Pertusella","Gerenzano","Origgio",
    "Uboldo","Cislago","Mozzate","Gornate Olona",
    "Castelseprio","Gazzada Schianno","Bodio Lomnago"
]

@st.cache_data(ttl=3600)
def get_vie(comune):
    try:
        q = (
            '[out:json][timeout:10];'
            f'area[name="{comune}"][admin_level=8]->.a;'
            '(way(area.a)["highway"]["name"];);'
            'out 100;'
        )
        url = "https://overpass-api.de/api/interpreter"
        r = requests.post(url, data={"data": q}, timeout=8)
        if r.status_code == 200:
            data = r.json()
            vie = []
            for el in data.get("elements", []):
                if "tags" in el and "name" in el["tags"]:
                    vie.append(el["tags"]["name"])
            vie = sorted(list(set(vie)))
            if vie:
                base = ["-- Seleziona Via --"]
                return base + vie[:200]
    except:
        pass
    return [
        "-- Seleziona Via --",
        "Via Roma","Via Garibaldi",
        "Via Milano","Via Sacco"
    ]

ICONS = {
    "volontario": {"nome":"Volontario","icon":"👤"},
    "sede": {"nome":"Sede","icon":"🏠"},
    "radio": {"nome":"Radio","icon":"📻"},
    "emergenza": {"nome":"Emergenza","icon":"🚨"},
    "postazione": {"nome":"Postazione","icon":"📍"},
    "incendio": {"nome":"Incendio","icon":"🔥"},
    "alluvione": {"nome":"Alluvione","icon":"🌊"},
}

for k, v in [
    ("authenticated", False),
    ("dati", []),
    ("postazioni", []),
    ("emergenze_lista", []),
    ("radio_db", []),
    ("dist_radio", []),
    ("mem_nomi", ["Mario Rossi","Luigi Bianchi"]),
    ("menu_scelta", "Dashboard"),
]:
    if k not in st.session_state:
        st.session_state[k] = v

def torna(suffix=""):
    k = f"back_{suffix}_{uuid.uuid4().hex[:6]}"
    if st.button("Torna Dashboard", key=k, use_container_width=True):
        st.session_state.menu_scelta = "Dashboard"
        st.rerun()

def header_loghi():
    c1, c2, c3 = st.columns(3)
    if os.path.exists("logo.png"):
        c1.image("logo.png", width=80)
    if os.path.exists("logo2.png"):
        c2.image("logo2.png", width=80)
    if os.path.exists("logo_pc_lombardia.png"):
        c3.image("logo_pc_lombardia.png", width=80)
    else:
        if os.path.exists("logo_pc.png"):
            c3.image("logo_pc.png", width=80)

if not st.session_state.authenticated:
    st.markdown(
        "<style>[data-testid='stSidebar']{display:none;}</style>",
        unsafe_allow_html=True
    )
    header_loghi()
    st.markdown(
        "<h2 style='text-align:center; color:#2e7d32;'>"
        "Accesso - admin / ana2024</h2>",
        unsafe_allow_html=True
    )
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        with st.form("login"):
            u = st.text_input("Username", value="admin")
            p = st.text_input("Password", type="password", value="ana2024")
            if st.form_submit_button("Accedi", use_container_width=True):
                if u == "admin" and p == "ana2024":
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("admin / ana2024")
    st.stop()

header_loghi()
st.divider()

with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=80)
    opzioni = [
        "Dashboard",
        "Emergenze con Loghi",
        "Mappa Postazioni",
        "Volontari",
        "DB Radio",
        "Distribuzione Radio",
        "Backup"
    ]
    sel = st.radio(
        "MENU",
        opzioni,
        index=opzioni.index(st.session_state.menu_scelta)
        if st.session_state.menu_scelta in opzioni else 0
    )
    if sel!= st.session_state.menu_scelta:
        st.session_state.menu_scelta = sel
        st.rerun()
    if st.button("Logout", key="logout"):
        st.session_state.authenticated = False
        st.rerun()

scelta = st.session_state.menu_scelta
st.markdown(f"## {scelta}")
st.divider()

if scelta == "Dashboard":
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Emergenze", len(st.session_state.emergenze_lista))
    c2.metric("Postazioni", len(st.session_state.postazioni))
    c3.metric("Volontari", len(st.session_state.dati))
    c4.metric("Radio", len(st.session_state.radio_db))
    st.markdown("### Scelta rapida")
    r1, r2, r3, r4 = st.columns(4)
    with r1:
        if st.button("Emergenze", key="b1", use_container_width=True):
            st.session_state.menu_scelta = "Emergenze con Loghi"
            st.rerun()
    with r2:
        if st.button("Mappa", key="b2", use_container_width=True):
            st.session_state.menu_scelta = "Mappa Postazioni"
            st.rerun()
    with r3:
        if st.button("Volontari", key="b3", use_container_width=True):
            st.session_state.menu_scelta = "Volontari"
            st.rerun()
    with r4:
        if st.button("DB Radio", key="b4", use_container_width=True):
            st.session_state.menu_scelta = "DB Radio"
            st.rerun()

elif scelta == "Emergenze con Loghi":
    torna("top_em")
    st.markdown("### Libreria Loghi")
    cols = st.columns(6)
    for i, (k, v) in enumerate(ICONS.items()):
        with cols[i % 6]:
            st.markdown(
                f"<div style='background:white; "
                f"border:2px solid #2e7d32; border-radius:10px; "
                f"padding:8px; text-align:center;'>"
                f"<div style='font-size:28px;'>{v['icon']}</div>"
                f"<div style='font-size:10px;'>{v['nome']}</div></div>",
                unsafe_allow_html=True
            )
    st.divider()
    st.markdown("### Comune e Via combo agganciate")
    c1, c2 = st.columns(2)
    with c1:
        comune = st.selectbox("Comune *", COMUNI, key="comune_em")
    with c2:
        vie = get_vie(comune)
        via = st.selectbox(f"Via * ({comune})", vie, key="via_em")
        if via == "-- Seleziona Via --":
            via_man = st.text_input("Via manuale")
            via_f = via_man if via_man else via
        else:
            via_f = via
    with st.form("form_em"):
        data_em = st.date_input("Data", value=date.today())
        tipo = st.selectbox(
            "Tipo",
            list(ICONS.keys()),
            format_func=lambda x: ICONS[x]["icon"] + " " + ICONS[x]["nome"]
        )
        desc = st.text_area("Descrizione", value=f"{comune} - {via_f}")
        if st.form_submit_button("Salva con Logo"):
            if via_f!= "-- Seleziona Via --":
                st.session_state.emergenze_lista.append({
                    "Data": str(data_em),
                    "Logo": ICONS[tipo]["icon"],
                    "Comune": comune,
                    "Via": via_f,
                    "Tipo": ICONS[tipo]["nome"],
                    "Descrizione": desc
                })
                st.success("Salvata!")
                st.rerun()
    if st.session_state.emergenze_lista:
        st.dataframe(pd.DataFrame(st.session_state.emergenze_lista))
    torna("bottom_em")

elif scelta == "Mappa Postazioni":
    torna("top_map")
    st.markdown("### Mappa - Google e OpenStreetMap")
    st.info("Serve in requirements.txt: folium, streamlit-folium, requests")
    c1, c2 = st.columns(2)
    with c1:
        comune = st.selectbox("Comune *", COMUNI, key="comune_map")
    with c2:
        vie = get_vie(comune)
        via = st.selectbox(f"Via * ({comune})", vie, key="via_map")
        if via == "-- Seleziona Via --":
            via_man = st.text_input("Via manuale map")
            via_f = via_man if via_man else via
        else:
            via_f = via
    with st.form("form_post"):
        nome = st.text_input("Nome Postazione *")
        col1, col2 = st.columns(2)
        with col1:
            lat = st.text_input("Lat *", placeholder="45.8205")
        with col2:
            lon = st.text_input("Lon *", placeholder="8.8255")
        resp = st.text_input("Responsabile")
        if st.form_submit_button("Aggiungi alla Mappa"):
            if nome and lat and lon:
                st.session_state.postazioni.append({
                    "Postazione": nome,
                    "Comune": comune,
                    "Via": via_f,
                    "Latitudine": lat,
                    "Longitudine": lon,
                    "Responsabile": resp
                })
                st.success("Aggiunta!")
                st.rerun()
    if st.session_state.postazioni:
        df = pd.DataFrame(st.session_state.postazioni)
        tipo = st.selectbox(
            "Tipo Mappa",
            ["OpenStreetMap", "Google Stradale", "Google Satellite", "Google Ibrida", "Google Rilievo"],
            key="tipo_mappa"
        )
        try:
            import folium
            from streamlit_folium import st_folium
            lat_c = 45.8205
            lon_c = 8.8255
            zoom = 12
            if tipo == "OpenStreetMap":
                m = folium.Map(
                    location=[lat_c, lon_c],
                    zoom_start=zoom,
                    tiles="OpenStreetMap"
                )
            else:
                m = folium.Map(
                    location=[lat_c, lon_c],
                    zoom_start=zoom,
                    tiles=None
                )
                if tipo == "Google Stradale":
                    url = "https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}"
                    nome_t = "Google Stradale"
                elif tipo == "Google Satellite":
                    url = "https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}"
                    nome_t = "Google Satellite"
                elif tipo == "Google Ibrida":
                    url = "https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}"
                    nome_t = "Google Ibrida"
                else:
                    url = "https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}"
                    nome_t = "Google Rilievo"
                folium.TileLayer(
                    url,
                    attr="Google",
                    name=nome_t,
                    max_zoom=20
                ).add_to(m)
            try:
                from folium.plugins import Fullscreen
                Fullscreen().add_to(m)
            except:
                pass
            for _, r in df.iterrows():
                try:
                    la = float(str(r["Latitudine"]).replace(",", "."))
                    lo = float(str(r["Longitudine"]).replace(",", "."))
                    folium.Marker(
                        [la, lo],
                        popup=r["Postazione"]
                    ).add_to(m)
                except:
                    pass
            st_folium(m, width=700, height=500)
        except Exception as e:
            st.error(f"Mappa: {e}")
            st.map(df.rename(columns={"Latitudine": "lat", "Longitudine": "lon"}))
        st.dataframe(df, use_container_width=True)
        for _, r in df.iterrows():
            with st.container(border=True):
                c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
                with c1:
                    st.write(f"**{r['Postazione']}** {r['Comune']} {r['Via']}")
                with c2:
                    url_g = (
                        "https://www.google.com/maps/search/?api=1&query="
                        + r["Latitudine"] + "," + r["Longitudine"]
                    )
                    st.link_button("Google Map", url_g, key=f"g_{uuid.uuid4().hex[:4]}")
                with c3:
                    url_osm = (
                        "https://www.openstreetmap.org/?mlat="
                        + r["Latitudine"] + "&mlon=" + r["Longitudine"]
                    )
                    st.link_button("OSM", url_osm, key=f"o_{uuid.uuid4().hex[:4]}")
                with c4:
                    url_w = (
                        "https://waze.com/ul?ll="
                        + r["Latitudine"] + "," + r["Longitudine"]
                    )
                    st.link_button("Waze", url_w, key=f"w_{uuid.uuid4().hex[:4]}")
    else:
        st.info("Nessuna postazione - usa combo Comune/Via")
    torna("bottom_map")

elif scelta == "Volontari":
    torna("top_vol")
    with st.form("form_vol"):
        nome = st.text_input("Nome e Cognome *")
        assoc = st.text_input("Associazione *", value="ANA Varese")
        cell = st.text_input("Cellulare *")
        ruolo = st.selectbox("Ruolo", ["Volontario","Caposquadra","Coordinatore","Autista","Radio"])
        if st.form_submit_button("Salva"):
            if nome and cell:
                st.session_state.dati.append({
                    "Nome": nome,
                    "Associazione": assoc,
                    "Cellulare": cell,
                    "Ruolo": ruolo
                })
                if nome not in st.session_state.mem_nomi:
                    st.session_state.mem_nomi.append(nome)
                st.success("Aggiunto!")
                st.rerun()
    if st.session_state.dati:
        df = pd.DataFrame(st.session_state.dati)
        st.dataframe(df, use_container_width=True)
        out = BytesIO()
        df.to_excel(out, index=False, engine="openpyxl")
        st.download_button(
            "Scarica Excel",
            out.getvalue(),
            file_name="volontari.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    torna("bottom_vol")

elif scelta == "DB Radio":
    torna("top_radio")
    st.markdown("### DB Radio Inventario - Form 15 settembre")
    with st.form("form_radio"):
        c1, c2 = st.columns(2)
        with c1:
            rid = st.text_input("Radio ID *", placeholder="R-01")
            mod = st.text_input("Modello *", placeholder="Baofeng UV-5R")
        with c2:
            stato = st.selectbox("Stato", ["Disponibile","In uso","Guasta"])
            note = st.text_input("Note")
        if st.form_submit_button("Salva Radio"):
            if rid and mod:
                st.session_state.radio_db.append({
                    "Radio ID": rid,
                    "Modello": mod,
                    "Stato": stato,
                    "Note": note
                })
                st.success("Aggiunta!")
                st.rerun()
    if st.session_state.radio_db:
        st.dataframe(pd.DataFrame(st.session_state.radio_db))
    torna("bottom_radio")

elif scelta == "Distribuzione Radio":
    torna("top_dist")
    st.markdown("### Distribuzione Radio - Form 15 settembre")
    with st.form("form_dist"):
        c1, c2 = st.columns(2)
        with c1:
            if st.session_state.radio_db:
                lista = [r["Radio ID"] for r in st.session_state.radio_db]
                rid = st.selectbox("Radio ID *", lista)
            else:
                rid = st.text_input("Radio ID *")
            ass = st.selectbox("Assegnato A *", ["--"] + st.session_state.mem_nomi)
        with c2:
            posto = st.text_input("Postazione *")
            canale = st.selectbox("Canale", ["CH1 Emergenza","CH2 Logistica","CH3 Coord"])
        if st.form_submit_button("Assegna Radio"):
            if rid and ass!="--" and posto:
                st.session_state.dist_radio.append({
                    "RadioID": rid,
                    "Assegnatario": ass,
                    "Postazione": posto,
                    "Canale": canale
                })
                st.success("Assegnata!")
                st.rerun()
    if st.session_state.dist_radio:
        st.dataframe(pd.DataFrame(st.session_state.dist_radio))
        out = BytesIO()
        pd.DataFrame(st.session_state.dist_radio).to_excel(out, index=False, engine="openpyxl")
        st.download_button(
            "Scarica Excel Distribuzione",
            out.getvalue(),
            file_name="distribuzione.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    torna("bottom_dist")

elif scelta == "Backup":
    torna("top_back")
    st.markdown("### Backup")
    if st.session_state.postazioni:
        df = pd.DataFrame(st.session_state.postazioni)
        st.download_button(
            "Postazioni CSV",
            df.to_csv(index=False).encode("utf-8"),
            "postazioni.csv"
        )
    if st.session_state.dati:
        df = pd.DataFrame(st.session_state.dati)
        out = BytesIO()
        df.to_excel(out, index=False, engine="openpyxl")
        st.download_button(
            "Volontari Excel",
            out.getvalue(),
            "volontari.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    torna("bottom_back")