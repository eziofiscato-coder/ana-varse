import streamlit as st
import pandas as pd
from datetime import date
from io import BytesIO
import os
import uuid
import requests

st.set_page_config(
    page_title="ANA Varese - Verde ANA",
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
    "Castelseprio","Gazzada Schianno","Bodio Lomnago",
    "Buguggiate","Azzate","Brunello","Morazzone",
    "Caravate","Cocquio-Trevisago","Cuvio","Cuveglio",
    "Rancio Valcuvia","Brinzio","Bedero Valcuvia",
    "Maccagno con Pino e Veddasca",
    "Tronzano Lago Maggiore","Dumenza","Agra",
    "Brezzo di Bedero","Germignaga",
    "Montegrino Valtravaglia","Grantola","Mesenzana",
    "Porto Valtravaglia","Castelveccana","Leggiuno",
    "Monvalle","Brebbia","Bregnano","Castronno",
    "Albizzate","Sumirago","Jerago con Orago",
    "Oggiona con Santo Stefano","Solbiate Arno",
    "Carnago","Gemonio","Barasso","Luvinate","Casciago"
]

@st.cache_data(ttl=86400)
def load_comuni_italia():
    try:
        url = "https://raw.githubusercontent.com/matteocontrini/comuni-json/master/comuni.json"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            comuni = sorted([c["nome"] for c in data])
            top = [c for c in COMUNI_VARESE if c in comuni]
            altri = [c for c in comuni if c not in top]
            return top + altri
    except:
        pass
    capoluoghi = [
        "Roma","Milano","Napoli","Torino","Palermo","Genova",
        "Bologna","Firenze","Bari","Catania","Venezia","Verona",
        "Messina","Padova","Trieste","Brescia","Parma","Prato"
    ]
    tutti = COMUNI_VARESE + capoluoghi
    return sorted(list(set(tutti)))

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
                return ["-- Seleziona Via --"] + vie[:250]
    except:
        pass
    return [
        "-- Seleziona Via --",
        "Via Roma","Via Garibaldi","Via Milano","Via Sacco"
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
    if st.button("🏠 Torna Dashboard", key=k, use_container_width=True):
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

if scelta == "Dashboard":
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Emergenze", len(st.session_state.emergenze_lista))
    c2.metric("Postazioni", len(st.session_state.postazioni))
    c3.metric("Volontari", len(st.session_state.dati))
    c4.metric("Radio", len(st.session_state.radio_db))
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
        if st.button("Backup", key="b4", use_container_width=True):
            st.session_state.menu_scelta = "Backup"
            st.rerun()

elif scelta == "Emergenze con Loghi":
    torna("top_em")
    c1, c2 = st.columns(2)
    with c1:
        comune = st.selectbox("Comune * - tutti Italia", COMUNI_TUTTI, key="comune_em")
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
        st.dataframe(pd.DataFrame(st.session_state.emergenze_lista), use_container_width=True)
    torna("bottom_em")

elif scelta == "Mappa Postazioni":
    torna("top_map")
    c1, c2 = st.columns(2)
    with c1:
        comune = st.selectbox("Comune * - tutti Italia", COMUNI_TUTTI, key="comune_map")
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
        tipo = st.selectbox("Tipo Mappa", ["OpenStreetMap","Google Stradale","Google Satellite","Google Ibrida","Google Rilievo"], key="tipo_mappa")
        try:
            import folium
            from streamlit_folium import st_folium
            lat_c = 45.8205
            lon_c = 8.8255
            zoom = 12
            if tipo == "OpenStreetMap":
                m = folium.Map(location=[lat_c, lon_c], zoom_start=zoom, tiles="OpenStreetMap")
            else:
                m = folium.Map(location=[lat_c, lon_c], zoom_start=zoom, tiles=None)
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
                folium.TileLayer(url, attr="Google", name=nome_t, max_zoom=20).add_to(m)
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
        for _, r in df.iterrows():
            with st.container(border=True):
                c1, c2, c3, c4 = st.columns([2,1,1,1])
                with c1:
                    st.write(f"**{r['Postazione']}** {r['Comune']} {r['Via']}")
                with c2:
                    url_g = "https://www.google.com/maps/search/?api=1&query=" + r["Latitudine"] + "," + r["Longitudine"]
                    st.link_button("Google Map", url_g, key=f"g_{uuid.uuid4().hex[:4]}")
                with c3:
                    url_osm = "https://www.openstreetmap.org/?mlat=" + r["Latitudine"] + "&mlon=" + r["Longitudine"]
                    st.link_button("OSM", url_osm, key=f"o_{uuid.uuid4().hex[:4]}")
                with c4:
                    url_w = "https://waze.com/ul?ll=" + r["Latitudine"] + "," + r["Longitudine"]
                    st.link_button("Waze", url_w, key=f"w_{uuid.uuid4().hex[:4]}")
    torna("bottom_map")

elif scelta == "Volontari":
    torna("top_vol")
    st.markdown("### Volontari - Sottomaschere come vecchio form")
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Anagrafica", "Contatti", "Associazione", "Ruolo/Competenze", "Disponibilita"
    ])
    with tab1:
        with st.container(border=True):
            st.markdown("#### Anagrafica")
            c1, c2 = st.columns(2)
            with c1:
                nome = st.text_input("Nome *", key="nome_anag")
                cognome = st.text_input("Cognome *", key="cogn_anag")
                cf = st.text_input("Codice Fiscale", key="cf_anag")
            with c2:
                data_nasc = st.date_input("Data Nascita", value=date(1980,1,1), key="data_anag")
                luogo_nasc = st.text_input("Luogo Nascita", key="luogo_anag")
                sesso = st.selectbox("Sesso", ["M","F"], key="sesso_anag")
    with tab2:
        with st.container(border=True):
            st.markdown("#### Contatti")
            c1, c2 = st.columns(2)
            with c1:
                cell = st.text_input("Cellulare *", key="cell_cont")
                email = st.text_input("Email", key="email_cont")
            with c2:
                comune_cont = st.selectbox("Comune Residenza - tutti Italia", COMUNI_TUTTI, key="comune_cont")
                vie_cont = get_vie_comune(comune_cont)
                via_cont = st.selectbox(f"Via - {comune_cont}", vie_cont, key="via_cont")
                civico = st.text_input("Civico", key="civ_cont")
    with tab3:
        with st.container(border=True):
            st.markdown("#### Associazione")
            c1, c2 = st.columns(2)
            with c1:
                assoc = st.text_input("Associazione *", value="ANA Varese", key="assoc_3")
                sezione = st.text_input("Sezione", value="Varese", key="sez_3")
            with c2:
                tessera = st.text_input("Numero Tessera", key="tess_3")
                scad = st.date_input("Scadenza Tessera", value=date.today(), key="scad_3")
                gruppo = st.selectbox("Gruppo", ["Varese","Busto","Gallarate","Luino","Saronno","Altro"], key="gruppo_3")
    with tab4:
        with st.container(border=True):
            st.markdown("#### Ruolo e Competenze")
            c1, c2 = st.columns(2)
            with c1:
                ruolo = st.selectbox("Ruolo *", ["Volontario","Caposquadra","Coordinatore","Autista","Radio","Logistica","Sanitario","Segreteria","Altro"], key="ruolo_4")
                spec = st.selectbox("Specializzazione", ["AIB","Cinofilo","Sub","Nautico","Alpino","Protezione Civile","Sanitario","Logistica","Nessuna"], key="spec_4")
                patente = st.selectbox("Patente", ["B","C","D","BE","CE","Nessuna"], key="pat_4")
            with c2:
                formazione = st.text_area("Formazione / Corsi", key="form_4")
                note = st.text_area("Note", key="note_4")
    with tab5:
        with st.container(border=True):
            st.markdown("#### Disponibilita")
            c1, c2 = st.columns(2)
            with c1:
                giorni = st.multiselect("Giorni Disponibili", ["Lun","Mar","Mer","Gio","Ven","Sab","Dom"], key="giorni_5")
                orari = st.selectbox("Orari", ["Mattina","Pomeriggio","Sera","H24"], key="orari_5")
            with c2:
                disp_em = st.selectbox("Disponibilita Emergenza", ["Si - Immediata","Si - 2h","Si - 12h","No"], key="disp_5")
                note_disp = st.text_input("Note disponibilita", key="note_disp_5")
    st.divider()
    with st.form("form_vol_completo"):
        st.markdown("#### Salva Volontario - Riepilogo")
        c1, c2 = st.columns(2)
        with c1:
            st.write(f"**{nome} {cognome}** - {cell}")
            st.write(f"{comune_cont} - {via_cont} {civico}")
        with c2:
            st.write(f"{assoc} - {sezione} - Tessera {tessera}")
            st.write(f"{ruolo} - {spec} - {gruppo}")
        if st.form_submit_button("✅ SALVA VOLONTARIO COMPLETO", use_container_width=True, type="primary"):
            if nome and cognome and cell:
                nome_completo = f"{nome} {cognome}"
                st.session_state.dati.append({
                    "Nome": nome_completo,
                    "Cognome": cognome,
                    "NomeSingolo": nome,
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
                    "ScadenzaTessera": str(scad),
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
                st.success(f"Volontario {nome_completo} aggiunto!")
                st.balloons()
                st.rerun()
            else:
                st.error("Compila Nome, Cognome e Cellulare *")
    if st.session_state.dati:
        st.divider()
        st.markdown("### Elenco Volontari")
        df = pd.DataFrame(st.session_state.dati)
        st.dataframe(df, use_container_width=True)
        out = BytesIO()
        df.to_excel(out, index=False, engine="openpyxl")
        st.download_button("📥 Scarica Excel Volontari", out.getvalue(), file_name="volontari_completo.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
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
        st.dataframe(pd.DataFrame(st.session_state.radio_db))
    torna("bottom_radio")

elif scelta == "Distribuzione Radio":
    torna("top_dist")
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
                st.session_state.dist_radio.append({"RadioID": rid, "Assegnatario": ass, "Postazione": posto, "Canale": canale})
                st.success("Assegnata!")
                st.rerun()
    if st.session_state.dist_radio:
        st.dataframe(pd.DataFrame(st.session_state.dist_radio))
    torna("bottom_dist")

elif scelta == "Backup":
    torna("top_back")
    st.markdown("### Backup Completo - Sistemato")
    st.info("Scarica tutti i dati in un unico Excel con fogli separati")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📦 Crea Backup Completo Excel", use_container_width=True, type="primary"):
            output = BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                if st.session_state.dati:
                    pd.DataFrame(st.session_state.dati).to_excel(writer, sheet_name="Volontari", index=False)
                else:
                    pd.DataFrame([{"Info":"Nessun volontario"}]).to_excel(writer, sheet_name="Volontari", index=False)
                if st.session_state.postazioni:
                    pd.DataFrame(st.session_state.postazioni).to_excel(writer, sheet_name="Postazioni", index=False)
                else:
                    pd.DataFrame([{"Info":"Nessuna postazione"}]).to_excel(writer, sheet_name="Postazioni", index=False)
                if st.session_state.emergenze_lista:
                    pd.DataFrame(st.session_state.emergenze_lista).to_excel(writer, sheet_name="Emergenze", index=False)
                else:
                    pd.DataFrame([{"Info":"Nessuna emergenza"}]).to_excel(writer, sheet_name="Emergenze", index=False)
                if st.session_state.radio_db:
                    pd.DataFrame(st.session_state.radio_db).to_excel(writer, sheet_name="DB_Radio", index=False)
                else:
                    pd.DataFrame([{"Info":"Nessun radio"}]).to_excel(writer, sheet_name="DB_Radio", index=False)
                if st.session_state.dist_radio:
                    pd.DataFrame(st.session_state.dist_radio).to_excel(writer, sheet_name="Distribuzione_Radio", index=False)
                else:
                    pd.DataFrame([{"Info":"Nessuna distribuzione"}]).to_excel(writer, sheet_name="Distribuzione_Radio", index=False)
            st.session_state.backup_bytes = output.getvalue()
            st.success("Backup creato!")
    with c2:
        if "backup_bytes" in st.session_state:
            st.download_button(
                "📥 Scarica Backup Completo",
                st.session_state.backup_bytes,
                file_name=f"backup_ana_varese_{date.today()}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
    st.divider()
    st.markdown("### Backup singoli")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.session_state.dati:
            out = BytesIO()
            pd.DataFrame(st.session_state.dati).to_excel(out, index=False, engine="openpyxl")
            st.download_button("Volontari Excel", out.getvalue(), "volontari.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        if st.session_state.postazioni:
            st.download_button("Postazioni CSV", pd.DataFrame(st.session_state.postazioni).to_csv(index=False).encode("utf-8"), "postazioni.csv", use_container_width=True)
    with col2:
        if st.session_state.emergenze_lista:
            out = BytesIO()
            pd.DataFrame(st.session_state.emergenze_lista).to_excel(out, index=False, engine="openpyxl")
            st.download_button("Emergenze Excel", out.getvalue(), "emergenze.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        if st.session_state.radio_db:
            out = BytesIO()
            pd.DataFrame(st.session_state.radio_db).to_excel(out, index=False, engine="openpyxl")
            st.download_button("DB Radio Excel", out.getvalue(), "radio_db.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
    with col3:
        if st.session_state.dist_radio:
            out = BytesIO()
            pd.DataFrame(st.session_state.dist_radio).to_excel(out, index=False, engine="openpyxl")
            st.download_button("Distribuzione Excel", out.getvalue(), "distribuzione.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
    st.divider()
    st.markdown("### Ripristino")
    uploaded = st.file_uploader("Carica backup Excel per ripristinare", type=["xlsx"])
    if uploaded:
        try:
            xls = pd.ExcelFile(uploaded)
            for sheet in xls.sheet_names:
                df = pd.read_excel(xls, sheet_name=sheet)
                if sheet == "Volontari" and not df.empty and "Info" not in df.columns:
                    st.session_state.dati = df.to_dict(orient="records")
                    st.session_state.mem_nomi = [d.get("Nome","") for d in st.session_state.dati if d.get("Nome")]
                elif sheet == "Postazioni" and not df.empty and "Info" not in df.columns:
                    st.session_state.postazioni = df.to_dict(orient="records")
                elif sheet == "Emergenze" and not df.empty and "Info" not in df.columns:
                    st.session_state.emergenze_lista = df.to_dict(orient="records")
                elif sheet == "DB_Radio" and not df.empty and "Info" not in df.columns:
                    st.session_state.radio_db = df.to_dict(orient="records")
                elif sheet == "Distribuzione_Radio" and not df.empty and "Info" not in df.columns:
                    st.session_state.dist_radio = df.to_dict(orient="records")
            st.success("Dati ripristinati!")
            st.rerun()
        except Exception as e:
            st.error(f"Errore ripristino: {e}")
    st.divider()
    st.markdown("### Pulizia")
    if st.button("🗑️ Cancella Tutti i Dati (attenzione!)", use_container_width=True):
        st.session_state.dati = []
        st.session_state.postazioni = []
        st.session_state.emergenze_lista = []
        st.session_state.radio_db = []
        st.session_state.dist_radio = []
        st.session_state.mem_nomi = []
        st.success("Dati cancellati!")
        st.rerun()
    torna("bottom_back")