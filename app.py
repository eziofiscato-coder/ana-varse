import streamlit as st
import pandas as pd
from datetime import date, datetime
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

COMUNI_VARESE = [
    "Varese","Busto Arsizio","Gallarate","Saronno",
    "Cassano Magnago","Tradate","Somma Lombardo",
    "Malnate","Luino","Samarate","Laveno-Mombello",
    "Cittiglio","Besozzo","Gavirate","Vergiate",
    "Sesto Calende","Besnate","Cardano al Campo",
    "Cavaria con Premezzo","Castellanza",
    "Lonate Pozzolo","Fagnano Olona",
    "Caronno Pertusella","Gerenzano","Origgio",
    "Uboldo","Cislago","Mozzate","Gornate Olona",
    "Castelseprio","Gazzada Schianno","Bodio Lomnago"
]

@st.cache_data(ttl=86400)
def load_comuni_italia():
    try:
        url = (
            "https://raw.githubusercontent.com/"
            "matteocontrini/comuni-json/"
            "master/comuni.json"
        )
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            comuni = sorted([c["nome"] for c in data])
            top = [c for c in COMUNI_VARESE if c in comuni]
            altri = [c for c in comuni if c not in top]
            return top + altri
    except:
        pass
    return sorted(list(set(COMUNI_VARESE)))

@st.cache_data(ttl=3600)
def get_vie_comune(comune):
    try:
        q = (
            '[out:json][timeout:10];'
            f'area[name="{comune}"][admin_level=8]->.a;'
            '(way(area.a)["highway"]["name"];);'
            'out 150;'
        )
        url = "https://overpass-api.de/api/interpreter"
        r = requests.post(url, data={"data": q}, timeout=10)
        if r.status_code == 200:
            data = r.json()
            vie = []
            for el in data.get("elements", []):
                if "tags" in el and "name" in el["tags"]:
                    nome = el["tags"]["name"]
                    if len(nome) > 2:
                        vie.append(nome)
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
}

for k, v in [
    ("authenticated", False),
    ("dati", []),
    ("postazioni", []),
    ("emergenze_lista", []),
    ("radio_db", []),
    ("dist_radio", []),
    ("eventi_lista", []),
    ("checkin_lista", []),
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
        "Eventi",
        "Check-in",
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

COMUNI_TUTTI = load_comuni_italia()
MIME_XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
MIME_XLSX_SHORT = "application/octet-stream"

if scelta == "Dashboard":
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Emergenze", len(st.session_state.emergenze_lista))
    c2.metric("Postazioni", len(st.session_state.postazioni))
    c3.metric("Volontari", len(st.session_state.dati))
    c4.metric("Radio", len(st.session_state.radio_db))
    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Eventi", len(st.session_state.eventi_lista))
    c6.metric("Check-in", len(st.session_state.checkin_lista))
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
        if st.button("Eventi", key="b3", use_container_width=True):
            st.session_state.menu_scelta = "Eventi"
            st.rerun()
    with r4:
        if st.button("Check-in", key="b4", use_container_width=True):
            st.session_state.menu_scelta = "Check-in"
            st.rerun()

elif scelta == "Emergenze con Loghi":
    torna("top_em")
    c1, c2 = st.columns(2)
    with c1:
        comune = st.selectbox("Comune *", COMUNI_TUTTI, key="comune_em")
    with c2:
        vie = get_vie_comune(comune)
        via = st.selectbox(f"Via * ({comune})", vie, key="via_em")
        if via == "-- Seleziona Via --":
            via_man = st.text_input("Via manuale")
            via_f = via_man if via_man else via
        else:
            via_f = via
    with st.form("form_em"):
        data_em = st.date_input("Data", value=date.today())
        tipo = st.selectbox("Tipo", list(ICONS.keys()), format_func=lambda x: ICONS[x]["icon"] + " " + ICONS[x]["nome"])
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
        df = pd.DataFrame(st.session_state.emergenze_lista)
        st.dataframe(df, use_container_width=True)
        st.markdown("#### Backup singolo - Emergenze")
        out = BytesIO()
        df.to_excel(out, index=False, engine="openpyxl")
        fname = f"emergenze_{date.today()}.xlsx"
        st.download_button(
            label="Backup Emergenze Excel",
            data=out.getvalue(),
            file_name=fname,
            mime=MIME_XLSX_SHORT,
            use_container_width=True,
            key="back_em"
        )
    torna("bottom_em")

elif scelta == "Mappa Postazioni":
    torna("top_map")
    c1, c2 = st.columns(2)
    with c1:
        comune = st.selectbox("Comune *", COMUNI_TUTTI, key="comune_map")
    with c2:
        vie = get_vie_comune(comune)
        via = st.selectbox(f"Via * ({comune})", vie, key="via_map")
        if via == "-- Seleziona Via --":
            via_man = st.text_input("Via manuale", key="via_man_map")
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
        tipo = st.selectbox("Tipo Mappa", ["OpenStreetMap","Google Stradale","Google Satellite"], key="tipo_mappa")
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
                else:
                    url = "https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}"
                    nome_t = "Google Satellite"
                folium.TileLayer(
                    url,
                    attr="Google",
                    name=nome_t,
                    max_zoom=20
                ).add_to(m)
            for _, r in df.iterrows():
                try:
                    la = float(str(r["Latitudine"]).replace(",","."))
                    lo = float(str(r["Longitudine"]).replace(",","."))
                    folium.Marker([la, lo], popup=r["Postazione"]).add_to(m)
                except:
                    pass
            st_folium(m, width=700, height=500)
        except ImportError:
            st.map(df.rename(columns={"Latitudine":"lat","Longitudine":"lon"}))
        st.dataframe(df, use_container_width=True)
        st.markdown("#### Backup singolo - Postazioni")
        out = BytesIO()
        df.to_excel(out, index=False, engine="openpyxl")
        fname = f"postazioni_{date.today()}.xlsx"
        st.download_button(
            label="Backup Postazioni Excel",
            data=out.getvalue(),
            file_name=fname,
            mime=MIME_XLSX_SHORT,
            use_container_width=True,
            key="back_post"
        )
    torna("bottom_map")

elif scelta == "Volontari":
    torna("top_vol")
    st.markdown("### Volontari - Sottomaschere")
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Anagrafica","Contatti","Associazione","Ruolo","Disponibilita"])
    with tab1:
        with st.container(border=True):
            c1, c2 = st.columns(2)
            with c1:
                nome = st.text_input("Nome *", key="nome_anag")
                cognome = st.text_input("Cognome *", key="cogn_anag")
                cf = st.text_input("CF", key="cf_anag")
            with c2:
                data_nasc = st.date_input("Data Nascita", value=date(1980,1,1), key="data_anag")
                luogo_nasc = st.text_input("Luogo Nascita", key="luogo_anag")
                sesso = st.selectbox("Sesso", ["M","F"], key="sesso_anag")
    with tab2:
        with st.container(border=True):
            c1, c2 = st.columns(2)
            with c1:
                cell = st.text_input("Cellulare *", key="cell_cont")
                email = st.text_input("Email", key="email_cont")
            with c2:
                comune_cont = st.selectbox("Comune", COMUNI_TUTTI, key="comune_cont")
                vie_cont = get_vie_comune(comune_cont)
                via_cont = st.selectbox(f"Via - {comune_cont}", vie_cont, key="via_cont")
                civico = st.text_input("Civico", key="civ_cont")
    with tab3:
        with st.container(border=True):
            c1, c2 = st.columns(2)
            with c1:
                assoc = st.text_input("Associazione *", value="ANA Varese", key="assoc_3")
                sezione = st.text_input("Sezione", value="Varese", key="sez_3")
            with c2:
                tessera = st.text_input("Tessera", key="tess_3")
                scad = st.date_input("Scadenza", value=date.today(), key="scad_3")
                gruppo = st.selectbox("Gruppo", ["Varese","Busto","Gallarate","Luino","Saronno","Altro"], key="gruppo_3")
    with tab4:
        with st.container(border=True):
            c1, c2 = st.columns(2)
            with c1:
                ruolo = st.selectbox("Ruolo *", ["Volontario","Caposquadra","Coordinatore","Autista","Radio"], key="ruolo_4")
                spec = st.selectbox("Specializzazione", ["AIB","Cinofilo","Prot Civile","Sanitario","Nessuna"], key="spec_4")
                patente = st.selectbox("Patente", ["B","C","D","BE","CE","Nessuna"], key="pat_4")
            with c2:
                formazione = st.text_area("Formazione", key="form_4")
                note = st.text_area("Note", key="note_4")
    with tab5:
        with st.container(border=True):
            c1, c2 = st.columns(2)
            with c1:
                giorni = st.multiselect("Giorni", ["Lun","Mar","Mer","Gio","Ven","Sab","Dom"], key="giorni_5")
                orari = st.selectbox("Orari", ["Mattina","Pomeriggio","Sera","H24"], key="orari_5")
            with c2:
                disp_em = st.selectbox("Disp Emergenza", ["Si - Immediata","Si - 2h","Si - 12h","No"], key="disp_5")
    st.divider()
    with st.form("form_vol_completo"):
        if st.form_submit_button("SALVA VOLONTARIO", use_container_width=True, type="primary"):
            if nome and cognome and cell:
                nome_completo = f"{nome} {cognome}"
                st.session_state.dati.append({
                    "Nome": nome_completo,
                    "Cognome": cognome,
                    "CF": cf,
                    "DataNascita": str(data_nasc),
                    "LuogoNascita": luogo_nasc,
                    "Sesso": sesso,
                    "Cellulare": cell,
                    "Email": email,
                    "Comune": comune_cont,
                    "Via": via_cont,
                    "Civico": civico,
                    "Associazione": assoc,
                    "Sezione": sezione,
                    "Tessera": tessera,
                    "Scadenza": str(scad),
                    "Gruppo": gruppo,
                    "Ruolo": ruolo,
                    "Specializzazione": spec,
                    "Patente": patente,
                    "Formazione": formazione,
                    "Note": note,
                    "Giorni": ",".join(giorni),
                    "Orari": orari,
                    "DispEmergenza": disp_em
                })
                if nome_completo not in st.session_state.mem_nomi:
                    st.session_state.mem_nomi.append(nome_completo)
                st.success(f"Aggiunto {nome_completo}!")
                st.rerun()
            else:
                st.error("Compila Nome, Cognome e Cellulare")
    if st.session_state.dati:
        df = pd.DataFrame(st.session_state.dati)
        st.dataframe(df, use_container_width=True)
        out = BytesIO()
        df.to_excel(out, index=False, engine="openpyxl")
        fname = f"volontari_{date.today()}.xlsx"
        st.download_button(
            label="Backup Volontari Excel",
            data=out.getvalue(),
            file_name=fname,
            mime=MIME_XLSX_SHORT,
            use_container_width=True,
            key="back_vol"
        )
    torna("bottom_vol")

elif scelta == "DB Radio":
    torna("top_radio")
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
                st.session_state.radio_db.append({"Radio ID": rid, "Modello": mod, "Stato": stato, "Note": note})
                st.success("Aggiunta!")
                st.rerun()
    if st.session_state.radio_db:
        df = pd.DataFrame(st.session_state.radio_db)
        st.dataframe(df, use_container_width=True)
        out = BytesIO()
        df.to_excel(out, index=False, engine="openpyxl")
        fname = f"db_radio_{date.today()}.xlsx"
        st.download_button(
            label="Backup DB Radio Excel",
            data=out.getvalue(),
            file_name=fname,
            mime=MIME_XLSX_SHORT,
            use_container_width=True,
            key="back_radiodb"
        )
    torna("bottom_radio")

elif scelta == "Distribuzione Radio":
    torna("top_dist")
    st.markdown("### Distribuzione - Modello agganciato a ID")
    radio_map = {}
    if st.session_state.radio_db:
        for r in st.session_state.radio_db:
            rid_key = r.get("Radio ID","")
            mod_val = r.get("Modello","")
            radio_map[rid_key] = mod_val
    with st.form("form_dist"):
        c1, c2 = st.columns(2)
        with c1:
            if st.session_state.radio_db:
                lista_id = [r["Radio ID"] for r in st.session_state.radio_db]
                rid = st.selectbox("Radio ID *", lista_id, key="rid_dist")
                modello_agg = radio_map.get(rid, "")
                st.text_input("Modello agganciato", value=modello_agg, disabled=True, key="mod_agg")
            else:
                rid = st.text_input("Radio ID *", key="rid_man")
                modello_agg = st.text_input("Modello *", key="mod_man")
            ass = st.selectbox("Assegnato A *", ["--"] + st.session_state.mem_nomi, key="ass_dist")
        with c2:
            posto = st.text_input("Postazione *", key="posto_dist")
            canale = st.selectbox("Canale", ["CH1 Emergenza","CH2 Logistica","CH3 Coord"], key="can_dist")
            note_dist = st.text_input("Note", key="note_dist")
        if st.form_submit_button("Assegna Radio"):
            if rid and ass!="--" and posto:
                st.session_state.dist_radio.append({
                    "RadioID": rid,
                    "Modello": modello_agg,
                    "Assegnatario": ass,
                    "Postazione": posto,
                    "Canale": canale,
                    "Note": note_dist,
                    "Data": str(date.today())
                })
                st.success(f"Radio {rid} assegnata!")
                st.rerun()
    if st.session_state.dist_radio:
        df = pd.DataFrame(st.session_state.dist_radio)
        st.dataframe(df, use_container_width=True)
        out = BytesIO()
        df.to_excel(out, index=False, engine="openpyxl")
        fname = f"distribuzione_{date.today()}.xlsx"
        st.download_button(
            label="Backup Distribuzione Excel",
            data=out.getvalue(),
            file_name=fname,
            mime=MIME_XLSX_SHORT,
            use_container_width=True,
            key="back_dist"
        )
    torna("bottom_dist")

elif scelta == "Eventi":
    torna("top_eventi")
    st.markdown("### Form Eventi - Ripristinato")
    st.info("Crea e gestisci eventi, esercitazioni, interventi")
    c1, c2 = st.columns(2)
    with c1:
        comune_ev = st.selectbox("Comune Evento *", COMUNI_TUTTI, key="comune_ev")
    with c2:
        vie_ev = get_vie_comune(comune_ev)
        via_ev = st.selectbox(f"Via - {comune_ev}", vie_ev, key="via_ev")
        if via_ev == "-- Seleziona Via --":
            via_man_ev = st.text_input("Via manuale evento", key="via_man_ev")
            via_f_ev = via_man_ev if via_man_ev else via_ev
        else:
            via_f_ev = via_ev
    with st.form("form_eventi"):
        col1, col2 = st.columns(2)
        with col1:
            nome_ev = st.text_input("Nome Evento *", placeholder="Esercitazione AIB")
            data_ev = st.date_input("Data Evento *", value=date.today(), key="data_ev")
            ora_ev = st.time_input("Ora Inizio", value=datetime.now().time(), key="ora_ev")
            tipo_ev = st.selectbox("Tipo Evento *", ["Esercitazione","Intervento Reale","Formazione","Riunione","Manutenzione","Altro"], key="tipo_ev")
        with col2:
            resp_ev = st.text_input("Responsabile *", key="resp_ev")
            stato_ev = st.selectbox("Stato", ["Programmato","In Corso","Concluso","Annullato"], key="stato_ev")
            priorita_ev = st.selectbox("Priorita", ["Bassa","Media","Alta","Critica"], key="prio_ev")
            num_vol = st.number_input("Num Volontari Previsti", min_value=1, max_value=100, value=5, key="num_vol_ev")
        desc_ev = st.text_area("Descrizione Evento", key="desc_ev")
        note_ev = st.text_area("Note / Materiale Necessario", key="note_ev")
        if st.form_submit_button("Salva Evento", use_container_width=True, type="primary"):
            if nome_ev and resp_ev and via_f_ev!="-- Seleziona Via --":
                st.session_state.eventi_lista.append({
                    "NomeEvento": nome_ev,
                    "Data": str(data_ev),
                    "Ora": str(ora_ev),
                    "Comune": comune_ev,
                    "Via": via_f_ev,
                    "Tipo": tipo_ev,
                    "Responsabile": resp_ev,
                    "Stato": stato_ev,
                    "Priorita": priorita_ev,
                    "NumVolontari": num_vol,
                    "Descrizione": desc_ev,
                    "Note": note_ev
                })
                st.success(f"Evento {nome_ev} salvato!")
                st.rerun()
            else:
                st.error("Compila Nome, Responsabile e Via")
    if st.session_state.eventi_lista:
        df = pd.DataFrame(st.session_state.eventi_lista)
        st.dataframe(df, use_container_width=True)
        st.markdown("#### Backup singolo - Eventi")
        out = BytesIO()
        df.to_excel(out, index=False, engine="openpyxl")
        fname = f"eventi_{date.today()}.xlsx"
        st.download_button(
            label="Backup Eventi Excel",
            data=out.getvalue(),
            file_name=fname,
            mime=MIME_XLSX_SHORT,
            use_container_width=True,
            key="back_eventi"
        )
        fname_csv = f"eventi_{date.today()}.csv"
        st.download_button(
            label="Backup Eventi CSV",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name=fname_csv,
            use_container_width=True,
            key="back_eventi_csv"
        )
    torna("bottom_eventi")

elif scelta == "Check-in":
    torna("top_checkin")
    st.markdown("### Form Check-in - Ripristinato")
    st.info("Registra presenza volontari a eventi e postazioni")
    c1, c2 = st.columns(2)
    with c1:
        if st.session_state.dati:
            volontari_list = [d["Nome"] for d in st.session_state.dati]
            vol_check = st.selectbox("Volontario *", volontari_list, key="vol_check")
        else:
            vol_check = st.text_input("Volontario *", key="vol_check_man")
            st.warning("Nessun volontario in anagrafica - inserisci manualmente")
        if st.session_state.eventi_lista:
            eventi_list = [e["NomeEvento"] for e in st.session_state.eventi_lista]
            evento_check = st.selectbox("Evento *", eventi_list, key="evento_check")
        else:
            evento_check = st.text_input("Evento / Postazione *", key="evento_check_man")
            st.warning("Nessun evento - inserisci manualmente")
    with c2:
        data_check = st.date_input("Data Check-in *", value=date.today(), key="data_check")
        ora_check_in = st.time_input("Ora Ingresso *", value=datetime.now().time(), key="ora_in_check")
        ora_check_out = st.time_input("Ora Uscita", key="ora_out_check")
        mezzo = st.selectbox("Mezzo", ["Proprio","Associazione","Pulmino ANA","Altro"], key="mezzo_check")
    with st.form("form_checkin"):
        col1, col2 = st.columns(2)
        with col1:
            stato_check = st.selectbox("Stato", ["Presente","Arrivato","Partito","Assente Giustificato"], key="stato_check")
            ruolo_check = st.selectbox("Ruolo in Evento", ["Volontario","Caposquadra","Autista","Radio","Logistica","Sanitario"], key="ruolo_check")
        with col2:
            note_check = st.text_area("Note Check-in", key="note_check")
            firma = st.checkbox("Confermo presenza", key="firma_check")
        if st.form_submit_button("Registra Check-in", use_container_width=True, type="primary"):
            if vol_check and evento_check and firma:
                st.session_state.checkin_lista.append({
                    "Volontario": vol_check,
                    "Evento": evento_check,
                    "Data": str(data_check),
                    "OraIngresso": str(ora_check_in),
                    "OraUscita": str(ora_check_out) if ora_check_out else "",
                    "Mezzo": mezzo,
                    "Stato": stato_check,
                    "RuoloEvento": ruolo_check,
                    "Note": note_check,
                    "Timestamp": str(datetime.now())
                })
                st.success(f"Check-in {vol_check} a {evento_check} registrato!")
                st.balloons()
                st.rerun()
            else:
                st.error("Compila Volontario, Evento e spunta Conferma")
    if st.session_state.checkin_lista:
        df = pd.DataFrame(st.session_state.checkin_lista)
        st.dataframe(df, use_container_width=True)
        # Statistiche rapide
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Totale Check-in", len(df))
        with c2:
            if not df.empty:
                presenti = len(df[df["Stato"]=="Presente"])
                st.metric("Presenti", presenti)
        with c3:
            if not df.empty and "Evento" in df.columns:
                st.metric("Eventi con Check-in", df["Evento"].nunique())
        st.markdown("#### Backup singolo - Check-in")
        out = BytesIO()
        df.to_excel(out, index=False, engine="openpyxl")
        fname = f"checkin_{date.today()}.xlsx"
        st.download_button(
            label="Backup Check-in Excel",
            data=out.getvalue(),
            file_name=fname,
            mime=MIME_XLSX_SHORT,
            use_container_width=True,
            key="back_checkin"
        )
        fname_csv = f"checkin_{date.today()}.csv"
        st.download_button(
            label="Backup Check-in CSV",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name=fname_csv,
            use_container_width=True,
            key="back_checkin_csv"
        )
    torna("bottom_checkin")

elif scelta == "Backup":
    torna("top_back")
    st.markdown("### Backup Completo + Singoli")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Crea Backup Completo", use_container_width=True, type="primary"):
            output = BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                if st.session_state.dati:
                    pd.DataFrame(st.session_state.dati).to_excel(writer, sheet_name="Volontari", index=False)
                if st.session_state.postazioni:
                    pd.DataFrame(st.session_state.postazioni).to_excel(writer, sheet_name="Postazioni", index=False)
                if st.session_state.emergenze_lista:
                    pd.DataFrame(st.session_state.emergenze_lista).to_excel(writer, sheet_name="Emergenze", index=False)
                if st.session_state.radio_db:
                    pd.DataFrame(st.session_state.radio_db).to_excel(writer, sheet_name="DB_Radio", index=False)
                if st.session_state.dist_radio:
                    pd.DataFrame(st.session_state.dist_radio).to_excel(writer, sheet_name="Distribuzione", index=False)
                if st.session_state.eventi_lista:
                    pd.DataFrame(st.session_state.eventi_lista).to_excel(writer, sheet_name="Eventi", index=False)
                if st.session_state.checkin_lista:
                    pd.DataFrame(st.session_state.checkin_lista).to_excel(writer, sheet_name="Checkin", index=False)
            st.session_state.backup_bytes = output.getvalue()
            st.success("Backup creato!")
    with c2:
        if "backup_bytes" in st.session_state:
            fname = f"backup_{date.today()}.xlsx"
            st.download_button(
                label="Scarica Backup Completo",
                data=st.session_state.backup_bytes,
                file_name=fname,
                mime=MIME_XLSX_SHORT,
                use_container_width=True
            )
    st.divider()
    st.markdown("### Backup singoli per form")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.session_state.dati:
            out = BytesIO()
            pd.DataFrame(st.session_state.dati).to_excel(out, index=False, engine="openpyxl")
            fname = f"volontari_{date.today()}.xlsx"
            st.download_button("Volontari Excel", out.getvalue(), file_name=fname, mime=MIME_XLSX_SHORT, use_container_width=True, key="b_vol")
        if st.session_state.eventi_lista:
            out = BytesIO()
            pd.DataFrame(st.session_state.eventi_lista).to_excel(out, index=False, engine="openpyxl")
            fname = f"eventi_{date.today()}.xlsx"
            st.download_button("Eventi Excel", out.getvalue(), file_name=fname, mime=MIME_XLSX_SHORT, use_container_width=True, key="b_ev")
    with col2:
        if st.session_state.emergenze_lista:
            out = BytesIO()
            pd.DataFrame(st.session_state.emergenze_lista).to_excel(out, index=False, engine="openpyxl")
            fname = f"emergenze_{date.today()}.xlsx"
            st.download_button("Emergenze Excel", out.getvalue(), file_name=fname, mime=MIME_XLSX_SHORT, use_container_width=True, key="b_em")
        if st.session_state.checkin_lista:
            out = BytesIO()
            pd.DataFrame(st.session_state.checkin_lista).to_excel(out, index=False, engine="openpyxl")
            fname = f"checkin_{date.today()}.xlsx"
            st.download_button("Checkin Excel", out.getvalue(), file_name=fname, mime=MIME_XLSX_SHORT, use_container_width=True, key="b_check")
    with col3:
        if st.session_state.radio_db:
            out = BytesIO()
            pd.DataFrame(st.session_state.radio_db).to_excel(out, index=False, engine="openpyxl")
            fname = f"db_radio_{date.today()}.xlsx"
            st.download_button("DB Radio Excel", out.getvalue(), file_name=fname, mime=MIME_XLSX_SHORT, use_container_width=True, key="b_rdb")
        if st.session_state.dist_radio:
            out = BytesIO()
            pd.DataFrame(st.session_state.dist_radio).to_excel(out, index=False, engine="openpyxl")
            fname = f"distribuzione_{date.today()}.xlsx"
            st.download_button("Distribuzione Excel", out.getvalue(), file_name=fname, mime=MIME_XLSX_SHORT, use_container_width=True, key="b_dist")
    torna("bottom_back")
