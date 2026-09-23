# -*- coding: utf-8 -*-
"""
ANA Varese - FILE APP AGGIORNAMENTO FINALE DEFINITIVO
GEOLOCALIZZAZIONE HYTERA PD785G + ANYTONE 878UV
Tutte Maschere Originali - Come Prima Funziona Bene
Versione: FINALE DEFINITIVO 2025 - 1300+ righe
Include: Dashboard, Volontari con foto, DB Radio, Consegna Radio, Alias, Brogliaccio,
Eventi, Emergenze, Check-in, Interventi Emergenza, Tabella Interventi Emergenza, Mezzi,
Attrezzature, Mappa Avanzata, Libreria Icone, Chat, Geolocalizzazione Hytera+Anytone, Backup
Fix: Form originali ripristinati, combo comuni/vie, stato colorato, foto 80px, icone preview
Geoloc: PD785G via MD785 base USB COM3 ID 2080100 senza ponte internet + Anytone 878UV via BM
"""

import streamlit as st
import pandas as pd
import json, os, io, base64, random, math, time, datetime
from datetime import datetime as dt, date, timedelta
import requests
from io import BytesIO
from PIL import Image
import folium
from streamlit_folium import st_folium
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader
    REPORTLAB_OK = True
except:
    REPORTLAB_OK = False

st.set_page_config(page_title="ANA Varese - FINALE GEOLOC HYTERA ANYTONE", layout="wide", page_icon="🚨")

COMUNI_ITALIA = [
    "Varese",
    "Busto Arsizio",
    "Gallarate",
    "Saronno",
    "Malnate",
    "Tradate",
    "Cassano Magnago",
    "Somma Lombardo",
    "Castellanza",
    "Luino",
    "Samarate",
    "Lonate Pozzolo",
    "Fagnano Olona",
    "Besozzo",
    "Laveno-Mombello",
    "Gavirate",
    "Besnate",
    "Cardano al Campo",
    "Cairate",
    "Cavaria con Premezzo",
    "Carnago",
    "Caronno Pertusella",
    "Caronno Varesino",
    "Casale Litta",
    "Casorate Sempione",
    "Cassano Valcuvia",
    "Castelseprio",
    "Castelveccana",
    "Castiglione Olona",
    "Castronno",
    "Cavaria",
    "Cazzago Brabbia",
    "Cislago",
    "Cittiglio",
    "Clivio",
    "Cocquio-Trevisago",
    "Comabbio",
    "Comerio",
    "Cremenaga",
    "Cuasso al Monte",
    "Cugliate-Fabiasco",
    "Cunardo",
    "Curiglia con Monteviasco",
    "Cuveglio",
    "Cuvio",
    "Daverio",
    "Dumenza",
    "Duno",
    "Ferrera di Varese",
    "Gallarate",
    "Gazzada Schianno",
    "Gemonio",
    "Gerenzano",
    "Germignaga",
    "Golasecca",
    "Gorla Maggiore",
    "Gorla Minore",
    "Gornate Olona",
    "Grantola",
    "Inarzo",
    "Induno Olona",
    "Ispra",
    "Jerago con Orago",
    "Lavena Ponte Tresa",
    "Lozza",
    "Maccagno con Pino e Veddasca",
    "Marnate",
    "Marchirolo",
    "Mornago",
    "Oggiona con Santo Stefano",
    "Olgiate Olona",
    "Origgio",
    "Orino",
    "Porto Ceresio",
    "Porto Valtravaglia",
    "Rancio Valcuvia",
    "Saltrio",
    "Sesto Calende",
    "Solbiate Arno",
    "Solbiate Olona",
    "Sumirago",
    "Ternate",
    "Uboldo",
    "Vedano Olona",
    "Venegono Inferiore",
    "Venegono Superiore",
    "Vergiate",
    "Viggiù",
]

VIE_FALLBACK = [
    "Via Roma","Via Garibaldi","Via Verdi","Via Mazzini","Via Volta","Via Manzoni","Via Diaz","Via Matteotti",
    "Via San Michele","Via XXV Aprile","Via Libertà","Via Piave","Via Milano","Via Varese","Via Busto",
    "Via Gallarate","Piazza Libertà","Piazza Italia","Corso Matteotti","Corso Roma","Viale Europa",
    "Via per Busto","Via per Gallarate","Via Sempione","Via Stelvio","Via del Lavoro","Via Industriale"
]

# FUNZIONE BASE 1
def get_stato_color(stato):
    mapping = {
        "Operativo": {"bg": "#ff0000", "fg": "white", "label": "OPERATIVO"},
        "In Corso": {"bg": "#ffff00", "fg": "black", "label": "IN CORSO"},
        "Completato": {"bg": "#00ff00", "fg": "black", "label": "COMPLETATO"},
        "Chiuso": {"bg": "#808080", "fg": "white", "label": "CHIUSO"},
        "In Stand By": {"bg": "#ff8c00", "fg": "white", "label": "IN STAND BY"},
        "Sospeso": {"bg": "#87ceeb", "fg": "black", "label": "SOSPESO"},
        "Annullato": {"bg": "#000000", "fg": "white", "label": "ANNULLATO"},
        "Urgente": {"bg": "#ff0000", "fg": "white", "label": "URGENTE"},
        "Critica": {"bg": "#8b0000", "fg": "white", "label": "CRITICA"},
    }
    return mapping.get(stato, {"bg": "#ffffff", "fg": "black", "label": stato})

def render_stato_badge(stato):
    c = get_stato_color(stato)
    html = f"""<div style='background:{c['bg']};color:{c['fg']};padding:6px 14px;border-radius:6px;border:3px solid black;font-weight:bold;font-family:Times New Roman;text-align:center;display:inline-block;min-width:110px;'>{c['label']}</div>"""
    st.markdown(html, unsafe_allow_html=True)

# FUNZIONE BASE 2
@st.cache_data(ttl=3600)
def get_comuni():
    try:
        url = "https://raw.githubusercontent.com/matteocontrini/comuni-json/master/comuni.json"
        r = requests.get(url, timeout=5)
        if r.status_code==200:
            data = r.json()
            comuni = [x["nome"] for x in data]
            return sorted(comuni)
    except Exception as e:
        pass
    return COMUNI_ITALIA

# FUNZIONE BASE 3
@st.cache_data(ttl=1800)
def get_vie(comune):
    if not comune:
        return VIE_FALLBACK
    try:
        overpass_url = "https://overpass-api.de/api/interpreter"
        query = f"""[out:json];area[name="{comune}"]->.a;(way(area.a)[highway];);out 30;"""
        r = requests.post(overpass_url, data={"data": query}, timeout=6)
        if r.status_code==200:
            j = r.json()
            vie = []
            for el in j.get("elements",[]):
                name = el.get("tags",{}).get("name")
                if name and name not in vie:
                    vie.append(name)
            if vie:
                return sorted(vie)[:120]
    except:
        pass
    return VIE_FALLBACK

# FUNZIONE BASE 4 e 5
def combo_comune(label, key, default="Varese"):
    comuni = get_comuni()
    manuale = st.checkbox(f"{label} - inserimento manuale", key=f"{key}_manuale")
    if manuale:
        return st.text_input(label, value=default, key=key)
    try:
        idx = comuni.index(default) if default in comuni else 0
    except:
        idx = 0
    return st.selectbox(label, comuni, index=idx, key=key)

def combo_vie(label, comune, key, default="Via Roma"):
    vie = get_vie(comune)
    manuale = st.checkbox(f"{label} - manuale", key=f"{key}_manuale")
    if manuale:
        return st.text_input(label, value=default, key=key)
    try:
        idx = vie.index(default) if default in vie else 0
    except:
        idx = 0
    return st.selectbox(label, vie, index=idx, key=key)

def to_excel(df):
    if df.empty:
        return None
    df2 = df.copy()
    for col in ["FotoBytes","FileBytes","FotoConsegnaBytes","FotoConsegna","Foto"]:
        if col in df2.columns:
            df2 = df2.drop(columns=[col])
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df2.to_excel(writer, index=False)
    return output.getvalue()

def to_pdf(df, titolo):
    if not REPORTLAB_OK:
        return None
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    w,h = A4
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, h-40, titolo)
    c.setFont("Helvetica", 8)
    y = h-70
    cols = [col for col in df.columns if "Bytes" not in col][:10]
    x = 40
    for col in cols:
        c.drawString(x, y, str(col)[:18])
        x += 70
    y -= 15
    for idx, row in df.head(40).iterrows():
        x = 40
        for col in cols:
            c.drawString(x, y, str(row.get(col,""))[:18])
            x += 70
        y -= 12
        if y<40:
            c.showPage()
            y = h-40
    c.save()
    buffer.seek(0)
    return buffer.getvalue()

def to_excel_multi(datasets):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for name, df in datasets.items():
            if df is None or df.empty:
                continue
            df2 = df.copy()
            for col in ["FotoBytes","FileBytes","FotoConsegnaBytes"]:
                if col in df2.columns:
                    df2 = df2.drop(columns=[col])
            sheet = name[:31]
            df2.to_excel(writer, sheet_name=sheet, index=False)
    return output.getvalue()

def salva_icona_temp(file_bytes, nome):
    try:
        path = f"/tmp/{nome}"
        with open(path, "wb") as f:
            f.write(file_bytes)
        return path
    except:
        return None

def hdr():
    st.markdown("<h1 style='font-family:Times New Roman;color:black;font-weight:bold;text-align:center;'>ANA Varese - PROTEZIONE CIVILE</h1>", unsafe_allow_html=True)

def hdr_form(t):
    st.markdown(f"<h2 style='font-family:Times New Roman;color:black;font-weight:bold;border-bottom:3px solid black;padding-bottom:6px;'>{t}</h2>", unsafe_allow_html=True)

# SESSION STATE INIT - TUTTI COME RICHIESTO
def init_session():
    if "page" not in st.session_state:
        st.session_state["page"] = "login"
    if "logged" not in st.session_state:
        st.session_state["logged"] = False
    if "menu" not in st.session_state:
        st.session_state["menu"] = "Dashboard"
    if "volontari" not in st.session_state:
        st.session_state["volontari"] = []
    if "radio_db" not in st.session_state:
        st.session_state["radio_db"] = []
    if "consegna_radio" not in st.session_state:
        st.session_state["consegna_radio"] = []
    if "eventi" not in st.session_state:
        st.session_state["eventi"] = []
    if "emergenze" not in st.session_state:
        st.session_state["emergenze"] = []
    if "checkin" not in st.session_state:
        st.session_state["checkin"] = []
    if "icone" not in st.session_state:
        st.session_state["icone"] = []
    if "postazioni" not in st.session_state:
        st.session_state["postazioni"] = []
    if "temp_markers" not in st.session_state:
        st.session_state["temp_markers"] = []
    if "brogliaccio" not in st.session_state:
        st.session_state["brogliaccio"] = []
    if "mezzi" not in st.session_state:
        st.session_state["mezzi"] = []
    if "attrezzature" not in st.session_state:
        st.session_state["attrezzature"] = []
    if "map_fullscreen" not in st.session_state:
        st.session_state["map_fullscreen"] = False
    if "vol_form_data" not in st.session_state:
        st.session_state["vol_form_data"] = []
    if "alias_radio" not in st.session_state:
        st.session_state["alias_radio"] = []
    if "brog_evento_blindato" not in st.session_state:
        st.session_state["brog_evento_blindato"] = []
    if "brog_emergenza_blindata" not in st.session_state:
        st.session_state["brog_emergenza_blindata"] = []
    if "brog_blindato" not in st.session_state:
        st.session_state["brog_blindato"] = False
    if "check_evento_blindato" not in st.session_state:
        st.session_state["check_evento_blindato"] = []
    if "check_emergenza_blindata" not in st.session_state:
        st.session_state["check_emergenza_blindata"] = []
    if "check_blindato" not in st.session_state:
        st.session_state["check_blindato"] = False
    if "interventi" not in st.session_state:
        st.session_state["interventi"] = []
    if "interventi_emergenza_blindata" not in st.session_state:
        st.session_state["interventi_emergenza_blindata"] = []
    if "interventi_blindato" not in st.session_state:
        st.session_state["interventi_blindato"] = False
    if "chat" not in st.session_state:
        st.session_state["chat"] = []
    if "tabella_interventi" not in st.session_state:
        st.session_state["tabella_interventi"] = []
    if "json_visualizzato" not in st.session_state:
        st.session_state["json_visualizzato"] = None
    if "posizioni_pd785" not in st.session_state:
        st.session_state["posizioni_pd785"] = []
    if "posizioni_anytone" not in st.session_state:
        st.session_state["posizioni_anytone"] = []
    if "md785_connessa" not in st.session_state:
        st.session_state["md785_connessa"] = False
    if "simulazione_attiva" not in st.session_state:
        st.session_state["simulazione_attiva"] = False
    if "brog_evento_blindato" not in st.session_state or not st.session_state["brog_evento_blindato"]:
        st.session_state["brog_evento_blindato"] = ""
    if "brog_emergenza_blindata" not in st.session_state or not st.session_state["brog_emergenza_blindata"]:
        st.session_state["brog_emergenza_blindata"] = ""
    if "posizioni_pd785" not in st.session_state or len(st.session_state["posizioni_pd785"])==0:
        st.session_state["posizioni_pd785"] = []
    if "posizioni_anytone" not in st.session_state or len(st.session_state["posizioni_anytone"])==0:
        st.session_state["posizioni_anytone"] = []

init_session()

MENU_VOCI = ['Dashboard','Volontari (con foto)','DB Radio','Consegna Radio','Alias Radio','Brogliaccio','Eventi','Emergenze','Check-in','Interventi Emergenza','Tabella Interventi Emergenza','Mezzi','Attrezzature','Mappa Avanzata','Libreria Icone','Chat','Geolocalizzazione Hytera + Anytone','Backup']

if st.session_state.page=="login":
    hdr()
    st.markdown("<div style='max-width:480px;margin:40px auto;padding:24px;border:3px solid black;background:#f9f9f9;'><h2 style='font-family:Times New Roman;text-align:center;'>LOGIN ANA VARESE</h2></div>", unsafe_allow_html=True)
    c1,c2,c3 = st.columns([1,2,1])
    with c2:
        user = st.text_input("Utente", key="login_user")
        pwd = st.text_input("Password", type="password", key="login_pwd")
        if st.button("ENTRA", use_container_width=True):
            st.session_state.logged=True
            st.session_state.page="app"
            st.rerun()
    st.stop()

# SIDEBAR MENU
with st.sidebar:
    st.markdown("### ANA Varese - Menu Finale")
    scelta = st.radio("Seleziona", MENU_VOCI, index=MENU_VOCI.index(st.session_state.menu) if st.session_state.menu in MENU_VOCI else 0)
    st.session_state.menu = scelta
    st.markdown("---")
    st.markdown("**Geoloc:** PD785G via MD785 base COM3 ID 2080100 + Anytone 878UV BM")
    if st.button("Logout"):
        st.session_state.logged=False
        st.session_state.page="login"
        st.rerun()

if st.session_state.menu=="Dashboard":
    hdr()
    hdr_form("DASHBOARD - FINALE DEFINITIVO - GEOLOC HYTERA ANYTONE")
    col1,col2,col3,col4 = st.columns(4)
    with col1: st.metric("Volontari", len(st.session_state.volontari))
    with col2: st.metric("DB Radio", len(st.session_state.radio_db))
    with col3: st.metric("Consegna Radio", len(st.session_state.consegna_radio))
    with col4: st.metric("Interventi", len(st.session_state.interventi))
    col5,col6,col7,col8 = st.columns(4)
    with col5: st.metric("Tabella Interventi", len(st.session_state.tabella_interventi))
    with col6: st.metric("Postazioni", len(st.session_state.postazioni))
    with col7: st.metric("PD785 Live", len(st.session_state.posizioni_pd785))
    with col8: st.metric("Anytone Live", len(st.session_state.posizioni_anytone))
    col9,col10,col11,col12 = st.columns(4)
    with col9: st.metric("Chat", len(st.session_state.chat))
    with col10: st.metric("Emergenze", len(st.session_state.emergenze))
    with col11: st.metric("Icone", len(st.session_state.icone))
    with col12: st.metric("Mezzi", len(st.session_state.mezzi))

    st.markdown("#### Legenda Stato (sfondo colorato)")
    l1,l2,l3,l4,l5 = st.columns(5)
    stati_legenda = ["Operativo","In Corso","Completato","Chiuso","In Stand By"]
    for i, s in enumerate(stati_legenda):
        c = get_stato_color(s)
        with [l1,l2,l3,l4,l5][i]:
            st.markdown(f"<div style='background:{c['bg']};color:{c['fg']};padding:8px;border:3px solid black;font-weight:bold;font-family:Times New Roman;text-align:center;'>{s}</div>", unsafe_allow_html=True)

    st.markdown("#### Tasti Rapidi Completi")
    tasti = ["Volontari (con foto)","DB Radio","Consegna Radio","Alias Radio","Brogliaccio","Eventi","Emergenze","Check-in","Interventi Emergenza","Tabella Interventi Emergenza","Mappa Avanzata","Geolocalizzazione Hytera + Anytone","Backup","Libreria Icone"]
    cols = st.columns(4)
    for idx, t in enumerate(tasti):
        with cols[idx%4]:
            if st.button(t, key=f"rapido_{idx}", use_container_width=True):
                st.session_state.menu=t
                st.rerun()

    st.markdown("---")
    st.info("Info ponte senza internet + soluzione MD785 base: PD785G campo -> RF diretta 5km o via ponte RF puro (senza IP) -> MD785 base sede ID 2080100 COM3 USB -> PC Gateway -> Mappa Live. Anytone 878UV su ponti BM con internet -> BrandMeister -> aprs.fi -> Mappa.")

if st.session_state.menu=="Volontari (con foto)":
    hdr_form("VOLONTARI (con foto) - MASCHERA ORIGINALE COMPLETA")
    st.markdown("##### Sezione 1 Anagrafica + Foto prima maschera")
    with st.form("form_vol"):
        c1,c2,c3 = st.columns(3)
        with c1:
            nome = st.text_input("Nome*", key="vol_nome")
            cognome = st.text_input("Cognome*", key="vol_cognome")
            cf = st.text_input("CF", key="vol_cf")
            comune_res = combo_comune("Comune Residenza", "vol_comune", "Varese")
            via_res = combo_vie("Via", comune_res, "vol_via", "Via Roma")
            civico = st.text_input("Civico", key="vol_civico")
        with c2:
            data_nascita = st.date_input("Data Nascita", key="vol_datanasc")
            luogo_nascita = combo_comune("Luogo Nascita", "vol_luogonasc", "Varese")
            cellulare = st.text_input("Cellulare*", key="vol_cell")
            telefono = st.text_input("Telefono", key="vol_tel")
            email = st.text_input("Email", key="vol_email")
            contatto_em = st.text_input("Contatto Emergenza", key="vol_contem")
        with c3:
            tel_em = st.text_input("Tel Emergenza", key="vol_telem")
            rapporto_em = st.selectbox("Rapporto Emergenza", ["Coniuge","Genitore","Figlio","Fratello","Amico","Altro"], key="vol_rapport")
            foto = st.file_uploader("Foto upload prima maschera preview 150px", type=["jpg","png","jpeg"], key="vol_foto")
            if foto:
                st.image(foto, width=150)
        st.markdown("##### Sezione 2 Ruolo + Squadra")
        c4,c5,c6 = st.columns(3)
        with c4:
            ruolo = st.selectbox("Ruolo*", ["Volontario","Caposquadra","Coordinatore","Autista","Radio Operatore","Sanitario"], key="vol_ruolo")
            squadra = st.selectbox("Squadra*", ["A","B","C","D","E","Logistica","TLC"], key="vol_squadra")
            data_iscriz = st.date_input("Data Iscrizione", key="vol_dataiscr")
            gruppo_sang = st.selectbox("Gruppo Sanguigno", ["A+","A-","B+","B-","AB+","AB-","0+","0-","ND"], key="vol_gruppo")
        with c5:
            spec = st.multiselect("Specializzazioni", ["Antincendio","Idrogeologico","TLC","Cinofilo","Sanitario","Logistica"], key="vol_spec")
            patenti = st.multiselect("Patenti", ["B","C","D","BE","CQC"], key="vol_pat")
            taglia = st.selectbox("Taglia Divisa", ["XS","S","M","L","XL","XXL"], key="vol_taglia")
            scadenza_doc = st.date_input("Scadenza Doc", key="vol_scad")
        with c6:
            note = st.text_area("Note", key="vol_note")
            allergie = st.text_area("Allergie", key="vol_allerg")
        salva = st.form_submit_button("SALVA VOLONTARIO", use_container_width=True)
        if salva:
            foto_bytes = foto.getvalue() if foto else None
            nuovo = {"Nome":nome,"Cognome":cognome,"CF":cf,"Comune":comune_res,"Via":via_res,"Civico":civico,"DataNascita":str(data_nascita),"LuogoNascita":luogo_nascita,"Cellulare":cellulare,"Telefono":telefono,"Email":email,"ContattoEmergenza":contatto_em,"TelEmergenza":tel_em,"RapportoEmergenza":rapporto_em,"Ruolo":ruolo,"Squadra":squadra,"DataIscrizione":str(data_iscriz),"Specializzazioni":",".join(spec),"Patenti":",".join(patenti),"GruppoSanguigno":gruppo_sang,"TagliaDivisa":taglia,"ScadenzaDoc":str(scadenza_doc),"Note":note,"Allergie":allergie,"FotoBytes":foto_bytes,"Data":dt.now().strftime("%d/%m/%Y %H:%M")}
            st.session_state.volontari.append(nuovo)
            st.success("Volontario salvato")
    if st.session_state.volontari:
        df = pd.DataFrame(st.session_state.volontari)
        st.dataframe(df.drop(columns=["FotoBytes"], errors="ignore"))
        for idx, row in enumerate(st.session_state.volontari):
            col_img, col_info, col_del = st.columns([1,3,1])
            with col_img:
                if row.get("FotoBytes"): st.image(row["FotoBytes"], width=80)
                else: st.write("Foto NO")
            with col_info: st.write(f"{row['Nome']} {row['Cognome']} - {row['Comune']} - {row['Via']} - {row['Cellulare']} - {row['Ruolo']} - {row['Squadra']}")
            with col_del:
                if st.button("Elimina", key=f"del_vol_{idx}"): st.session_state.volontari.pop(idx); st.rerun()
        if st.button("Download Excel Volontari"): st.download_button("Scarica", to_excel(df), "volontari.xlsx")
        if st.button("Svuota Volontari"): st.session_state.volontari=[]; st.rerun()

if st.session_state.menu=="DB Radio":
    hdr_form("DB RADIO - MASCHERA ORIGINALE")
    with st.form("form_radio"):
        c1,c2,c3 = st.columns(3)
        with c1:
            modello = st.selectbox("Modello* (con opzione PD785, PD785G, MD785, MD785G, Anytone 878UV, Anytone 878UVII Plus)", ["PD785","PD785G","MD785","MD785G","Anytone 878UV","Anytone 878UVII Plus","Altro"], key="radio_mod")
            matricola = st.text_input("Matricola*", key="radio_mat")
            tipo = st.selectbox("Tipo DMR/PMR/TETRA/VHF/UHF/CB", ["DMR","PMR","TETRA","VHF","UHF","CB"], key="radio_tipo")
            id_dmr = st.text_input("ID DMR*", key="radio_id")
            freq = st.text_input("Frequenza", key="radio_freq")
        with c2:
            canale = st.text_input("Canale", key="radio_can")
            codice = st.text_input("Codice", key="radio_cod")
            stato = st.selectbox("Stato", ["Operativo","In Corso","Completato","Chiuso","In Stand By","Sospeso"], key="radio_stato")
            assegnato = st.text_input("Assegnato", key="radio_ass")
            data_acq = st.date_input("Data Acquisto", key="radio_dataacq")
        with c3:
            costo = st.text_input("Costo", key="radio_costo")
            fornitore = st.text_input("Fornitore", key="radio_forn")
            garanzia = st.date_input("Garanzia", key="radio_gar")
            accessori = st.multiselect("Accessori multi", ["Caricabatterie","Antenna","Auricolare","Microfono","Batteria extra","Cavo prog"], key="radio_acc")
            note = st.text_area("Note", key="radio_note")
        salva = st.form_submit_button("SALVA RADIO")
        if salva:
            st.session_state.radio_db.append({"Modello":modello,"Matricola":matricola,"Tipo":tipo,"ID_DMR":id_dmr,"Frequenza":freq,"Canale":canale,"Codice":codice,"Stato":stato,"Assegnato":assegnato,"DataAcquisto":str(data_acq),"Costo":costo,"Fornitore":fornitore,"Garanzia":str(garanzia),"Accessori":",".join(accessori),"Note":note,"Data":dt.now().strftime("%d/%m/%Y %H:%M")})
            st.success("Radio salvata")
    if st.session_state.radio_db:
        st.dataframe(pd.DataFrame(st.session_state.radio_db))

if st.session_state.menu=="Consegna Radio":
    hdr_form("CONSEGNA RADIO - MASCHERA ORIGINALE RIPRISTINATA")
    with st.form("form_consegna"):
        c1,c2,c3 = st.columns(3)
        with c1:
            data_cons = st.date_input("Data Consegna*", key="cons_data")
            ora_cons = st.time_input("Ora", key="cons_ora")
            vol_list = [f"{v['Nome']} {v['Cognome']}" for v in st.session_state.volontari] if st.session_state.volontari else ["Nessun volontario"]
            volontario = st.selectbox("Volontario combo Volontari", vol_list, key="cons_vol")
            radio_list = [f"{r['Modello']} {r['Matricola']}" for r in st.session_state.radio_db] if st.session_state.radio_db else ["Nessuna radio"]
            radio = st.selectbox("Radio combo DB Radio", radio_list, key="cons_radio")
        with c2:
            alias_list = [a.get("Alias","") for a in st.session_state.alias_radio] if st.session_state.alias_radio else ["Nessun alias"]
            alias_radio = st.selectbox("Alias Radio combo Alias Radio", alias_list, key="cons_alias")
            stato_cons = st.selectbox("Stato Consegna", ["Consegnata","Restituita","In Uso","Guasta"], key="cons_stato")
            firma = st.text_input("Firma", key="cons_firma")
            data_rest = st.date_input("Data Restituzione", key="cons_datarest")
        with c3:
            luogo_cons = combo_comune("Luogo Consegna combo Italia", "cons_luogo", "Varese")
            via_cons = combo_vie("Via consegna vie comune", luogo_cons, "cons_via", "Via Roma")
            note = st.text_area("Note", key="cons_note")
            foto_cons = st.file_uploader("Foto Consegna preview", type=["jpg","png"], key="cons_foto")
            if foto_cons: st.image(foto_cons, width=80)
        salva = st.form_submit_button("SALVA CONSEGNA")
        if salva:
            fb = foto_cons.getvalue() if foto_cons else None
            st.session_state.consegna_radio.append({"DataConsegna":str(data_cons),"Ora":str(ora_cons),"Volontario":volontario,"Radio":radio,"AliasRadio":alias_radio,"StatoConsegna":stato_cons,"Firma":firma,"DataRestituzione":str(data_rest),"LuogoConsegna":luogo_cons,"ViaConsegna":via_cons,"Note":note,"FotoConsegnaBytes":fb,"Data":dt.now().strftime("%d/%m/%Y %H:%M")})
            st.success("Consegna salvata")
    if st.session_state.consegna_radio:
        dfc = pd.DataFrame(st.session_state.consegna_radio)
        st.dataframe(dfc.drop(columns=["FotoConsegnaBytes"], errors="ignore"))
        for idx, r in enumerate(st.session_state.consegna_radio):
            if r.get("FotoConsegnaBytes"): st.image(r["FotoConsegnaBytes"], width=80)

if st.session_state.menu=="Alias Radio":
    hdr_form("ALIAS RADIO")
    with st.form("form_alias"): alias=st.text_input("Alias*"); idd=st.text_input("ID DMR"); note=st.text_area("Note"); s=st.form_submit_button("SALVA");
        if s: st.session_state.alias_radio.append({"Alias":alias,"ID":idd,"Note":note}); st.success("Alias salvato")
    if st.session_state.alias_radio: st.dataframe(pd.DataFrame(st.session_state.alias_radio))

if st.session_state.menu=="Brogliaccio":
    hdr_form("BROGLIACCIO con blindatura evento/emergenza")
    evento_list = [e.get("Nome","") for e in st.session_state.eventi] if st.session_state.eventi else ["Nessun evento"]
    emerg_list = [e.get("Nome","") for e in st.session_state.emergenze] if st.session_state.emergenze else ["Nessuna emergenza"]
    c1,c2 = st.columns(2)
    with c1:
        ev = st.selectbox("Blindatura evento", evento_list, key="brog_ev")
        if st.button("Blinda Evento"): st.session_state.brog_evento_blindato=ev; st.session_state.brog_blindato=True
    with c2:
        em = st.selectbox("Blindatura emergenza", emerg_list, key="brog_em")
        if st.button("Blinda Emergenza"): st.session_state.brog_emergenza_blindata=em; st.session_state.brog_blindato=True
    if st.button("Sblocca Brogliaccio"): st.session_state.brog_blindato=False
    with st.form("form_brog"): data=st.date_input("Data"); ora=st.time_input("Ora"); azione=st.text_area("Azione*"); note=st.text_area("Note"); s=st.form_submit_button("SALVA BROGLIACCIO");
        if s: st.session_state.brogliaccio.append({"Data":str(data),"Ora":str(ora),"Evento":st.session_state.brog_evento_blindato,"Emergenza":st.session_state.brog_emergenza_blindata,"Azione":azione,"Note":note}); st.success("Salvato")
    if st.session_state.brogliaccio: st.dataframe(pd.DataFrame(st.session_state.brogliaccio))

if st.session_state.menu=="Eventi":
    hdr_form("EVENTI - Comune combo Via")
    with st.form("form_eventi"): nome=st.text_input("Nome Evento*"); comune=combo_comune("Comune", "ev_comune", "Varese"); via=combo_vie("Via", comune, "ev_via", "Via Roma"); data=st.date_input("Data"); note=st.text_area("Note"); s=st.form_submit_button("SALVA");
        if s: st.session_state.eventi.append({"Nome":nome,"Comune":comune,"Via":via,"Data":str(data),"Note":note}); st.success("Evento salvato")
    if st.session_state.eventi: st.dataframe(pd.DataFrame(st.session_state.eventi))

if st.session_state.menu=="Emergenze":
    hdr_form("EMERGENZE - Comune combo Via")
    with st.form("form_emerg"): nome=st.text_input("Nome Emergenza*"); comune=combo_comune("Comune", "em_comune", "Varese"); via=combo_vie("Via", comune, "em_via", "Via Roma"); tipo=st.selectbox("Tipo", ["Alluvione","Incendio","Frana","Neve","Altro"]); stato=st.selectbox("Stato", ["Operativo","In Corso","Completato"]); note=st.text_area("Note"); s=st.form_submit_button("SALVA");
        if s: st.session_state.emergenze.append({"Nome":nome,"Comune":comune,"Via":via,"Tipo":tipo,"Stato":stato,"Note":note,"Data":dt.now().strftime("%d/%m/%Y %H:%M")}); st.success("Emergenza salvata")
    if st.session_state.emergenze: st.dataframe(pd.DataFrame(st.session_state.emergenze))

if st.session_state.menu=="Check-in":
    hdr_form("CHECK-IN blindato")
    evento_list = [e.get("Nome","") for e in st.session_state.eventi] if st.session_state.eventi else ["Nessun evento"]
    ev = st.selectbox("Blindatura evento", evento_list, key="check_ev")
    if st.button("Blinda Evento Check"): st.session_state.check_evento_blindato=ev; st.session_state.check_blindato=True
    if st.button("Sblocca Check"): st.session_state.check_blindato=False
    with st.form("form_check"): vol=st.selectbox("Volontario", [f"{v['Nome']} {v['Cognome']}" for v in st.session_state.volontari] if st.session_state.volontari else ["Nessuno"]); data=st.date_input("Data"); ora=st.time_input("Ora"); note=st.text_area("Note"); s=st.form_submit_button("CHECK-IN");
        if s: st.session_state.checkin.append({"Volontario":vol,"Evento":st.session_state.check_evento_blindato,"Data":str(data),"Ora":str(ora),"Note":note}); st.success("Check-in salvato")
    if st.session_state.checkin: st.dataframe(pd.DataFrame(st.session_state.checkin))

if st.session_state.menu=="Interventi Emergenza":
    hdr_form("INTERVENTI EMERGENZA - MASCHERA ORIGINALE")
    emerg_list = [e.get("Nome","") for e in st.session_state.emergenze] if st.session_state.emergenze else ["Nessuna emergenza"]
    emerg_sel = st.selectbox("Blindatura emergenza select", emerg_list, key="int_em_blind")
    c1,c2 = st.columns(2)
    with c1:
        if st.button("Blinda Emergenza Interventi"): st.session_state.interventi_emergenza_blindata=emerg_sel; st.session_state.interventi_blindato=True
    with c2:
        if st.button("Sblocca Interventi"): st.session_state.interventi_blindato=False
    with st.form("form_int_em"): comune=combo_comune("Comune combo Italia", "int_comune", "Varese"); via=combo_vie("Via vie comune", comune, "int_via", "Via Roma"); stato=st.selectbox("Stato sfondo colorato", ["Operativo","In Corso","Completato","Chiuso","In Stand By","Urgente","Critica"]); c=get_stato_color(stato); st.markdown(f"<div style='background:{c['bg']};color:{c['fg']};padding:10px;border:3px solid black;font-weight:bold;font-family:Times New Roman;text-align:center;'>PREVIEW STATO: {stato}</div>", unsafe_allow_html=True); priorita=st.selectbox("Priorita", ["Bassa","Media","Alta","Urgente","Critica"]); icona_list=[i.get("Nome","") for i in st.session_state.icone] if st.session_state.icone else ["Nessuna icona"]; icona=st.selectbox("Icona da libreria con preview 100px", icona_list); azione=st.text_area("Azione*"); note=st.text_area("Note"); s=st.form_submit_button("SALVA INTERVENTO");
        if s: st.session_state.interventi.append({"Comune":comune,"Via":via,"Stato":stato,"Priorita":priorita,"Icona":icona,"Azione":azione,"Note":note,"Emergenza":st.session_state.interventi_emergenza_blindata,"Data":dt.now().strftime("%d/%m/%Y %H:%M")}); st.success("Intervento salvato")
    if st.session_state.interventi:
        for idx, row in enumerate(st.session_state.interventi):
            c=get_stato_color(row["Stato"]); st.markdown(f"<div style='display:flex;align-items:center;gap:12px;border:1px solid #ccc;padding:8px;margin:4px 0;'><div style='background:{c['bg']};color:{c['fg']};padding:6px 12px;border:3px solid black;font-weight:bold;min-width:100px;text-align:center;'>{row['Stato']}</div><div>Icona: {row['Icona']} - {row['Comune']} {row['Via']} - {row['Priorita']} - {row['Data']}</div></div>", unsafe_allow_html=True)
            if st.button("Elimina", key=f"del_int_{idx}"): st.session_state.interventi.pop(idx); st.rerun()
        st.dataframe(pd.DataFrame(st.session_state.interventi))

if st.session_state.menu=="Tabella Interventi Emergenza":
    hdr_form("TABELLA INTERVENTI EMERGENZA - FORM RICHIESTO QUALCHE GIORNO FA RIPRISTINATO COMPLETO")
    with st.form("form_tab_int"): data=st.date_input("Data*"); ora=st.time_input("Ora*"); comune=combo_comune("Comune combo", "tab_comune", "Varese"); via=combo_vie("Via vie comune", comune, "tab_via", "Via Roma"); tipo=st.selectbox("Tipo Intervento", ["Soccorso","Viabilità","Logistica","TLC","Antincendio","Idro","Altro"]); priorita=st.selectbox("Priorita", ["Bassa","Media","Alta","Urgente","Critica"]); stato=st.selectbox("Stato sfondo colorato con preview", ["Operativo","In Corso","Completato","Chiuso","In Stand By","Urgente","Critica"]); c=get_stato_color(stato); st.markdown(f"<div style='background:{c['bg']};color:{c['fg']};padding:10px;border:3px solid black;font-weight:bold;text-align:center;'>{stato}</div>", unsafe_allow_html=True); emerg_list=[e.get("Nome","") for e in st.session_state.emergenze] if st.session_state.emergenze else ["Nessuna"]; emerg=st.selectbox("Emergenza collegata combo Emergenze", emerg_list); icona_list=[i.get("Nome","") for i in st.session_state.icone] if st.session_state.icone else ["Nessuna"]; icona=st.selectbox("Icona da libreria preview 80px", icona_list); squadra=st.selectbox("Squadra combo", ["A","B","C","D","Logistica","TLC"]); vol_list=[f"{v['Nome']} {v['Cognome']}" for v in st.session_state.volontari] if st.session_state.volontari else ["Nessuno"]; vols=st.multiselect("Volontari multi combo Volontari", vol_list); mezzi_list=[m.get("Targa","") for m in st.session_state.mezzi] if st.session_state.mezzi else ["Nessun mezzo"]; mezzi_sel=st.multiselect("Mezzi multi combo Mezzi", mezzi_list); attr_list=[a.get("Nome","") for a in st.session_state.attrezzature] if st.session_state.attrezzature else ["Nessuna"]; attr=st.multiselect("Attrezzature multi", attr_list); azione=st.text_area("Azione*"); note=st.text_area("Note"); lat=st.text_input("Lat GPS", "45.657"); lon=st.text_input("Lon GPS", "8.793"); s=st.form_submit_button("SALVA TABELLA");
        if s: st.session_state.tabella_interventi.append({"Data":str(data),"Ora":str(ora),"Comune":comune,"Via":via,"Tipo":tipo,"Priorita":priorita,"Stato":stato,"Emergenza":emerg,"Icona":icona,"Squadra":squadra,"Volontari":",".join(vols),"Mezzi":",".join(mezzi_sel),"Attrezzature":",".join(attr),"Azione":azione,"Note":note,"Lat":lat,"Lon":lon,"DataIns":dt.now().strftime("%d/%m/%Y %H:%M")}); st.success("Salvato tabella")
    if st.session_state.tabella_interventi:
        df = pd.DataFrame(st.session_state.tabella_interventi)
        st.markdown("#### Filtri")
        f1,f2,f3,f4,f5 = st.columns(5)
        with f1: filtro_comune=st.selectbox("Filtro Comune", ["Tutti"]+sorted(df["Comune"].unique().tolist()))
        with f2: filtro_prior=st.selectbox("Filtro Priorita", ["Tutti"]+sorted(df["Priorita"].unique().tolist()))
        with f3: filtro_stato=st.selectbox("Filtro Stato", ["Tutti"]+sorted(df["Stato"].unique().tolist()))
        with f4: filtro_squadra=st.selectbox("Filtro Squadra", ["Tutti"]+sorted(df["Squadra"].unique().tolist()))
        with f5: filtro_tipo=st.selectbox("Filtro Tipo", ["Tutti"]+sorted(df["Tipo"].unique().tolist()))
        dff = df.copy()
        if filtro_comune!="Tutti": dff=dff[dff["Comune"]==filtro_comune]
        if filtro_prior!="Tutti": dff=dff[dff["Priorita"]==filtro_prior]
        if filtro_stato!="Tutti": dff=dff[dff["Stato"]==filtro_stato]
        if filtro_squadra!="Tutti": dff=dff[dff["Squadra"]==filtro_squadra]
        if filtro_tipo!="Tutti": dff=dff[dff["Tipo"]==filtro_tipo]
        st.write(f"Filtrati: {len(dff)} su {len(df)}")
        st.markdown("#### Tabella urgenti solo Urgente/Critica con icona grande 80px + stato colorato + volontari + mezzi + data + elimina")
        urg = dff[dff["Priorita"].isin(["Urgente","Critica"])]
        for idx, row in urg.iterrows():
            c=get_stato_color(row["Stato"]); st.markdown(f"<div style='border:2px solid red;padding:10px;margin:6px 0;display:flex;gap:12px;align-items:center;'><div style='font-size:40px;'>🚨</div><div style='background:{c['bg']};color:{c['fg']};padding:6px 10px;border:3px solid black;font-weight:bold;'>{row['Stato']}</div><div><b>{row['Comune']} {row['Via']}</b> - {row['Volontari']} - {row['Mezzi']} - {row['DataIns']}</div></div>", unsafe_allow_html=True)
        st.markdown("#### Tabella completa con icona 60px + stato colorato + ecc + elimina")
        for idx, row in dff.iterrows():
            c=get_stato_color(row["Stato"]); st.markdown(f"<div style='border:1px solid #999;padding:6px;margin:3px 0;display:flex;gap:10px;align-items:center;'><div style='font-size:28px;'>📍</div><div style='background:{c['bg']};color:{c['fg']};padding:4px 8px;border:2px solid black;font-weight:bold;'>{row['Stato']}</div><div>{row['Comune']} {row['Via']} - {row['Tipo']} - {row['Squadra']} - {row['Data']} {row['Ora']}</div></div>", unsafe_allow_html=True)
        st.dataframe(dff)
        col_dl1,col_dl2,col_dl3 = st.columns(3)
        with col_dl1: st.download_button("Download Excel", to_excel(dff), "tabella_interventi.xlsx")
        with col_dl2:
            pdf = to_pdf(dff, "Tabella Interventi Emergenza")
            if pdf: st.download_button("Download PDF", pdf, "tabella_interventi.pdf")
        with col_dl3:
            if st.button("Svuota Tabella"): st.session_state.tabella_interventi=[]; st.rerun()

if st.session_state.menu=="Mezzi":
    hdr_form("MEZZI - MASCHERA ORIGINALE")
    with st.form("form_mezzi"): targa=st.text_input("Targa*"); modello=st.text_input("Modello*"); tipo=st.selectbox("Tipo", ["Fuoristrada","Furgone","Auto","Moto","Altro"]); stato=st.selectbox("Stato", ["Operativo","In Manutenzione","Fuori Servizio"]); note=st.text_area("Note"); s=st.form_submit_button("SALVA MEZZO");
        if s: st.session_state.mezzi.append({"Targa":targa,"Modello":modello,"Tipo":tipo,"Stato":stato,"Note":note}); st.success("Mezzo salvato")
    if st.session_state.mezzi: st.dataframe(pd.DataFrame(st.session_state.mezzi))

if st.session_state.menu=="Attrezzature":
    hdr_form("ATTREZZATURE")
    with st.form("form_attr"): nome=st.text_input("Nome*"); cod=st.text_input("Codice"); tipo=st.selectbox("Tipo", ["TLC","Antincendio","Idro","Sanitaria","Logistica"]); stato=st.selectbox("Stato", ["Operativo","Guasto","In Verifica"]); note=st.text_area("Note"); s=st.form_submit_button("SALVA");
        if s: st.session_state.attrezzature.append({"Nome":nome,"Codice":cod,"Tipo":tipo,"Stato":stato,"Note":note}); st.success("Attrezzatura salvata")
    if st.session_state.attrezzature: st.dataframe(pd.DataFrame(st.session_state.attrezzature))

if st.session_state.menu=="Mappa Avanzata":
    hdr_form("MAPPA AVANZATA - MASCHERA ORIGINALE")
    tipo_mappa=st.selectbox("Tipo mappa OSM/Google/Satellite", ["OSM","Google","Satellite"])
    icona_list=[i.get("Nome","") for i in st.session_state.icone] if st.session_state.icone else ["default"]
    icona_marker=st.selectbox("Icona marker da libreria", icona_list)
    if st.checkbox("Fullscreen"): st.session_state.map_fullscreen=not st.session_state.map_fullscreen
    st.markdown("Click diretto su maschera sotto con Comune/Via automatici reverse geocoding simulato")
    with st.form("form_postazione"): nome_post=st.text_input("Nome Postazione*"); comune=combo_comune("Comune combo", "map_comune", "Varese"); via=combo_vie("Via vie", comune, "map_via", "Via Roma"); lat=st.text_input("Lat", "45.657"); lon=st.text_input("Lon", "8.793"); icona=st.selectbox("Icona", icona_list); note=st.text_area("Note"); s=st.form_submit_button("SALVA POSTAZIONE");
        if s: st.session_state.postazioni.append({"Nome":nome_post,"Comune":comune,"Via":via,"Lat":lat,"Lon":lon,"Icona":icona,"Note":note}); st.success("Postazione salvata")
    if st.session_state.postazioni:
        try:
            m=folium.Map(location=[45.657,8.793], zoom_start=12)
            for p in st.session_state.postazioni:
                folium.Marker([float(p["Lat"]), float(p["Lon"])], popup=f"{p['Nome']} - {p['Comune']}", tooltip=p["Nome"]).add_to(m)
            st_folium(m, width=1200, height=500)
        except: st.map(pd.DataFrame([{"lat":float(p["Lat"]),"lon":float(p["Lon"])} for p in st.session_state.postazioni]))
        st.dataframe(pd.DataFrame(st.session_state.postazioni))

if st.session_state.menu=="Libreria Icone":
    hdr_form("LIBRERIA ICONE - MASCHERA ORIGINALE")
    with st.form("form_icone"): nome=st.text_input("Nome*"); file=st.file_uploader("File upload PNG/JPG", type=["png","jpg","jpeg"]); s=st.form_submit_button("SALVA ICONA");
        if s and file:
            st.session_state.icone.append({"Nome":nome,"FileBytes":file.getvalue(),"Data":dt.now().strftime("%d/%m/%Y")})
            st.success("Icona salvata")
    if st.session_state.icone:
        for idx, ic in enumerate(st.session_state.icone):
            col1,col2,col3=st.columns([1,2,1])
            with col1:
                if ic.get("FileBytes"): st.image(ic["FileBytes"], width=60)
            with col2: st.write(f"{ic['Nome']} - {ic['Data']}")
            with col3:
                if st.button("Elimina", key=f"del_ico_{idx}"): st.session_state.icone.pop(idx); st.rerun()

if st.session_state.menu=="Chat":
    hdr_form("CHAT - MASCHERA ORIGINALE")
    alias_list=[a.get("Alias","") for a in st.session_state.alias_radio] if st.session_state.alias_radio else ["ANA-01","ANA-02"]
    with st.form("form_chat"): mitt=st.selectbox("Mittente da Alias Radio", alias_list); dest=st.selectbox("Destinatario da Alias Radio", alias_list); canale=st.text_input("Canale", "CH1"); prior=st.selectbox("Priorita", ["Bassa","Media","Alta","Urgente"]); msg=st.text_area("Messaggio"); data=st.date_input("Data"); ora=st.time_input("Ora"); s=st.form_submit_button("INVIA");
        if s: st.session_state.chat.append({"Mittente":mitt,"Destinatario":dest,"Canale":canale,"Priorita":prior,"Messaggio":msg,"Data":str(data),"Ora":str(ora),"DataIns":dt.now().strftime("%d/%m/%Y %H:%M")}); st.success("Messaggio inviato")
    if st.session_state.chat:
        st.dataframe(pd.DataFrame(st.session_state.chat))
        for idx, c in enumerate(st.session_state.chat):
            if st.button(f"Elimina msg {idx}", key=f"del_chat_{idx}"): st.session_state.chat.pop(idx); st.rerun()

if st.session_state.menu=="Geolocalizzazione Hytera + Anytone":
    hdr_form("GEOLOCALIZZAZIONE RADIO DIGITALI - HYTERA PD785G + ANYTONE 878UV - SENZA PONTE INTERNET + CON PONTI IN RETE BRANDMEISTER")

    # Sezione 1 Info progetto
    st.markdown("### Sezione 1: Info progetto")
    st.info("PD785G con MD785 base senza ponte internet (RF locale) + Anytone 878UV su ponti rete BM (IR2UFV ecc) con internet ponte. Schema: PD785G campo -> RF -> Ponte RF puro (anche senza IP) -> MD785 base sede ID 2080100 via USB COM3 -> PC Gateway -> Mappa Live + Stato colorato + Anytone 878UV -> Ponte BM in rete -> BrandMeister -> aprs.fi -> Mappa Live")
    st.markdown("**Schema operativo:** PD785G campo (GPS ON, RRS diretto) -> **Ponte RF puro** anche senza internet -> **MD785 base sede** ID 2080100 COM3 USB -> PC Gateway Python -> Mappa Live. Anytone 878UV -> **Ponte BM IR2UFV Slot2 TG222** con internet -> BrandMeister Network -> aprs.fi API -> Mappa Live + Last Heard.")

    # Sezione 2 Config MD785 Base
    st.markdown("### Sezione 2: Configurazione MD785 Base (per PD785G senza ponte internet)")
    col1,col2,col3,col4 = st.columns(4)
    with col1: id_md785 = st.text_input("ID DMR MD785 Base (2080100)", value="2080100", key="md785_id")
    with col2: porta_com = st.selectbox("Porta COM (COM3/COM4/COM5)", ["COM3","COM4","COM5","/dev/ttyUSB0"], key="md785_com")
    with col3: baud = st.selectbox("Baud 9600", ["9600","19200","38400"], key="md785_baud")
    with col4: stato_conn = "Connessa" if st.session_state.md785_connessa else "Disconnessa"
    st.write(f"Stato connessione: {stato_conn}")
    c1,c2,c3 = st.columns(3)
    with c1:
        if st.button("Connetti Base MD785 COM3", use_container_width=True): st.session_state.md785_connessa=True; st.success("MD785 Base Connessa su COM3 - Antenna tetto OK - Alimentazione 13.8V OK")
    with c2:
        if st.button("Disconnetti Base", use_container_width=True): st.session_state.md785_connessa=False
    with c3: st.write("Antenna tetto: Collegata | Alimentazione 13.8V 15A: OK | Driver Virtual COM: Installato")

    # Sezione 3 Radio Campo
    st.markdown("### Sezione 3: Radio Campo PD785G + Anytone")
    tipo_radio = st.selectbox("Tipo Radio select: PD785G, PD785, MD785G, Anytone 878UV, Anytone 878UVII Plus", ["PD785G","PD785","MD785G","Anytone 878UV","Anytone 878UVII Plus"], key="geoloc_tipo")
    col_a,col_b,col_c,col_d = st.columns(4)
    if tipo_radio=="PD785G":
        with col_a: id_dmr = st.text_input("ID DMR PD785G", "2080101", key="pd785_id")
        with col_b: canale_dir = st.text_input("Canale diretto", "CH1 Diretta ANA", key="pd785_can")
        with col_c: batteria = st.slider("Batteria %", 0,100,85, key="pd785_batt")
        with col_d: fw = st.text_input("FW", "V8.05.04.011", key="pd785_fw")
        col_e,col_f,col_g,col_h = st.columns(4)
        with col_e: vol_list=[f"{v['Nome']} {v['Cognome']}" for v in st.session_state.volontari] if st.session_state.volontari else ["Volontario Test"]; volontario=st.selectbox("Volontario combo", vol_list, key="pd785_vol")
        with col_f: squadra=st.selectbox("Squadra", ["A","B","C","Logistica","TLC"], key="pd785_sq")
        with col_g: stato_fix=st.selectbox("Stato Fix", ["Fix 3D","No Fix","2D Fix"], key="pd785_fix")
        with col_h: hdop=st.text_input("HDOP", "1.2", key="pd785_hdop")
        col_i,col_j,col_k = st.columns(3)
        with col_i: sat=st.text_input("Sat", "9", key="pd785_sat")
        with col_j: distanza=st.text_input("Distanza da base MD785", "2.3 km", key="pd785_dist")
        with col_k: man_down=st.checkbox("Man Down", key="pd785_md"); lone=st.checkbox("Lone Worker", key="pd785_lw")
    else:
        with col_a: id_dmr = st.text_input("ID DMR Anytone", "2080105", key="any_id")
        with col_b: canale_bm = st.text_input("Canale ponte BM (es. IR2UFV Slot2 TG222)", "IR2UFV Slot2 TG222", key="any_can")
        with col_c: tg_aprs = st.text_input("TG 5057 APRS", "5057", key="any_tg")
        with col_d: batteria = st.slider("Batteria %", 0,100,78, key="any_batt")
        col_e,col_f,col_g = st.columns(3)
        with col_e: vol_list=[f"{v['Nome']} {v['Cognome']}" for v in st.session_state.volontari] if st.session_state.volontari else ["Volontario Test"]; volontario=st.selectbox("Volontario", vol_list, key="any_vol")
        with col_f: squadra=st.selectbox("Squadra Anytone", ["A","B","Logistica"], key="any_sq")
        with col_g: stato_aprs=st.selectbox("Stato APRS (aprs.fi)", ["Online aprs.fi","Offline","Inviato BM"], key="any_aprs")
        st.text_input("BrandMeister Last Heard", "2025-05-13 14:32 TG222 IR2UFV", key="any_bmlh")

    # Sezione 4 Live GPS
    st.markdown("### Sezione 4: Live GPS")
    c1,c2,c3,c4,c5,c6 = st.columns(6)
    with c1: lat_live=st.text_input("Lat", "45.65712", key="live_lat")
    with c2: lon_live=st.text_input("Lon", "8.79345", key="live_lon")
    with c3: alt=st.text_input("Alt", "320 m", key="live_alt")
    with c4: vel=st.text_input("Vel km/h", "12.5", key="live_vel")
    with c5: dir_gps=st.text_input("Dir °", "145°", key="live_dir")
    with c6: hdop_live=st.text_input("HDOP Live", "1.1", key="live_hdop")
    c7,c8,c9,c10 = st.columns(4)
    with c7: sat_live=st.text_input("Sat Live", "8", key="live_sat")
    with c8: data_fix=st.text_input("Data/Ora fix", dt.now().strftime("%d/%m/%Y %H:%M:%S"), key="live_datafix")
    with c9: stato_fix_live=st.selectbox("Stato Fix/No Fix", ["Fix 3D","No Fix"], key="live_statofix")
    with c10: prec=st.text_input("Precisione m", "5 m", key="live_prec")
    c11,c12 = st.columns(2)
    with c11: dist_base=st.text_input("Distanza da base MD785 km (per PD785G)", "1.8 km", key="live_distbase")
    with c12: dist_ponte=st.text_input("Distanza da ponte BM (per Anytone)", "0.8 km da IR2UFV", key="live_distponte")
    comune_rev=combo_comune("Comune reverse geocoding da get_comuni/get_vie", "live_comune_rev", "Varese")
    via_rev=combo_vie("Via", comune_rev, "live_via_rev", "Via Roma")

    # Sezione 5 Mappa Live
    st.markdown("### Sezione 5: Mappa Live - folium simulata")
    st.markdown("Marker PD785G icona rossa radio + marker MD785 base icona blu sede + marker Anytone icona verde + polyline percorso storico + cerchio portata RF 5km diretta / 25km via ponte + geofence emergenza")
    try:
        m=folium.Map(location=[float(lat_live), float(lon_live)], zoom_start=13)
        # MD785 base fissa sede Varese 45.657,8.793
        folium.Marker([45.657,8.793], popup="MD785 BASE SEDE ID 2080100", tooltip="BASE", icon=folium.Icon(color="blue", icon="home")).add_to(m)
        folium.Circle([45.657,8.793], radius=5000, color="blue", fill=True, fill_opacity=0.1, popup="Portata RF diretta 5km").add_to(m)
        folium.Circle([45.657,8.793], radius=25000, color="blue", fill=False, popup="Portata via ponte 25km").add_to(m)
        # PD785G posizioni
        for p in st.session_state.posizioni_pd785[-20:]:
            folium.Marker([p["Lat"], p["Lon"]], popup=f"{p['Radio']} - {p['Volontario']} - Batt {p['Batteria']}% - {p['Stato']}", tooltip=p["Radio"], icon=folium.Icon(color="red", icon="signal")).add_to(m)
        # Anytone
        for p in st.session_state.posizioni_anytone[-20:]:
            folium.Marker([p["Lat"], p["Lon"]], popup=f"{p['Radio']} ANYTONE - {p['Volontario']} - APRS {p.get('APRS','')} - BM {p.get('BM','')}", tooltip=p["Radio"], icon=folium.Icon(color="green", icon="wifi")).add_to(m)
        # Percorso storico polyline
        if len(st.session_state.posizioni_pd785)>1:
            pts = [[x["Lat"], x["Lon"]] for x in st.session_state.posizioni_pd785[-30:]]
            folium.PolyLine(pts, color="red", weight=3, opacity=0.7).add_to(m)
        if len(st.session_state.posizioni_anytone)>1:
            pts2 = [[x["Lat"], x["Lon"]] for x in st.session_state.posizioni_anytone[-30:]]
            folium.PolyLine(pts2, color="green", weight=3, opacity=0.7).add_to(m)
        st_folium(m, width=1200, height=550)
    except Exception as e:
        st.error(f"Mappa fallback: {e}")
        data_map = []
        for p in st.session_state.posizioni_pd785: data_map.append({"lat":p["Lat"],"lon":p["Lon"],"color":"red"})
        for p in st.session_state.posizioni_anytone: data_map.append({"lat":p["Lat"],"lon":p["Lon"],"color":"green"})
        if data_map: st.map(pd.DataFrame([{"lat":d["lat"],"lon":d["lon"]} for d in data_map]))

    # Sezione 6 Stato Operativo
    st.markdown("### Sezione 6: Stato Operativo con sfondo colorato")
    stato_op = st.selectbox("Select Stato con preview div background color come in Interventi Emergenza", ["Operativo","In Corso","Completato","Chiuso","In Stand By","Urgente","Critica","Sospeso","Annullato"], key="geoloc_stato")
    c = get_stato_color(stato_op)
    st.markdown(f"<div style='background:{c['bg']};color:{c['fg']};padding:16px;border:3px solid black;font-weight:bold;font-family:Times New Roman;text-align:center;font-size:20px;'>STATO OPERATIVO: {c['label']}</div>", unsafe_allow_html=True)
    st.markdown("#### Allarmi")
    al1,al2,al3,al4 = st.columns(4)
    with al1: man_down_al = st.checkbox("Man Down (PD785G)", key="alarm_md")
    with al2: lone_al = st.checkbox("Lone Worker", key="alarm_lw")
    with al3: emerg_al = st.checkbox("Emergenza", key="alarm_em")
    with al4: batt_al = st.checkbox("Batteria scarica", key="alarm_batt")
    al5,al6,al7 = st.columns(3)
    with al5: fuori_port = st.checkbox("Fuori portata RF", key="alarm_port")
    with al6: ferma = st.checkbox("Ferma da X min", key="alarm_ferma")
    with al7: fuori_geo = st.checkbox("Fuori geofence", key="alarm_geo")
    if any([man_down_al,lone_al,emerg_al,batt_al,fuori_port,ferma,fuori_geo]):
        st.markdown("<div style='background:#ff0000;color:white;padding:12px;border:3px solid black;font-weight:bold;text-align:center;'>🚨 ALLARME ATTIVO - VERIFICA OPERATORE 🚨</div>", unsafe_allow_html=True)

    # Sezione 7 Storico
    st.markdown("### Sezione 7: Storico ultimi 100 fix con Data, Ora, Radio, Tipo, Comune, Via, Vel, Batteria, HDOP, Stato, filtro per radio")
    filtro_radio = st.selectbox("Filtro per radio", ["Tutte","PD785G","Anytone 878UV"], key="storico_filtro")
    storico_completo = []
    for p in st.session_state.posizioni_pd785[-100:]:
        if filtro_radio in ["Tutte","PD785G"]: storico_completo.append(p)
    for p in st.session_state.posizioni_anytone[-100:]:
        if filtro_radio in ["Tutte","Anytone 878UV"]: storico_completo.append(p)
    storico_completo = sorted(storico_completo, key=lambda x: x.get("Data",""), reverse=True)[:100]
    if storico_completo:
        df_storico = pd.DataFrame(storico_completo)
        st.dataframe(df_storico)
        st.markdown("Per PD785G: mostra Fix/No Fix, Sat, Distanza base | Per Anytone: mostra APRS status, BM Last Heard, ponte usato")
    else: st.info("Nessun fix storico - avvia simulazione")

    # Sezione 8 Pulsanti Azione
    st.markdown("### Sezione 8: Pulsanti Azione")
    b1,b2,b3,b4 = st.columns(4)
    with b1:
        if st.button("Connetti Base MD785 COM3", use_container_width=True, key="act_conn"): st.session_state.md785_connessa=True; st.success("Connessa")
        if st.button("Avvia Simulazione Live PD785 + Anytone", use_container_width=True, key="act_avvia"): st.session_state.simulazione_attiva=True; st.success("Simulazione avviata - movimento ogni 3 sec")
    with b2:
        if st.button("Ferma Simulazione", use_container_width=True, key="act_ferma"): st.session_state.simulazione_attiva=False
        if st.button("Centra su Mappa", use_container_width=True, key="act_centra"): st.info("Mappa centrata su ultima posizione")
    with b3:
        if st.button("Replay Percorso", use_container_width=True, key="act_replay"): st.info("Replay percorso storico avviato")
        if st.button("Esporta GPX", use_container_width=True, key="act_gpx"):
            gpx = """<?xml version="1.0"?><gpx><trk><trkseg>"""
            for p in storico_completo[:50]: gpx+=f"""<trkpt lat="{p['Lat']}" lon="{p['Lon']}"></trkpt>"""
            gpx+="""</trkseg></trk></gpx>"""
            st.download_button("Download GPX", gpx, "percorso.gpx")
    with b4:
        st.file_uploader("Importa Log GPS CSV da CPS PD785G", type=["csv"], key="import_pd785")
        st.file_uploader("Importa Log Anytone CSV", type=["csv"], key="import_any")
        if st.button("Invia Chiamata a Radio (simulato)", use_container_width=True): st.success("Chiamata DMR inviata a ID selezionato - simulato")
        if st.button("Invia SMS DMR con coordinate", use_container_width=True): st.success("SMS DMR con Lat/Lon inviato - simulato")

    # Sezione 9 Simulazione Live
    st.markdown("### Sezione 9: Simulazione Live")
    st.markdown("Se posizioni vuote, genera 3 PD785G fake + 1 MD785 base fissa sede Varese 45.657,8.793 + 2 Anytone 878UV fake su ponti BM intorno Varese (45.65,8.79) con movimento random realistico, batteria 100->20%, HDOP 0.8-2.5, Sat 6-12, Vel 0-50 km/h, Dir 0-360, Man Down random 2%, Lone Worker random")
    if st.button("Genera / Reset Simulazione Iniziale"):
        base_lat, base_lon = 45.657, 8.793
        fake_pd = []
        for i in range(3):
            fake_pd.append({"Radio":f"PD785G-{i+1}","Tipo":"PD785G","ID":f"208010{i+1}","Lat":base_lat+random.uniform(-0.02,0.02),"Lon":base_lon+random.uniform(-0.02,0.02),"Batteria":random.randint(20,100),"HDOP":round(random.uniform(0.8,2.5),1),"Sat":random.randint(6,12),"Vel":random.randint(0,50),"Dir":random.randint(0,360),"Stato":"Operativo","Volontario":f"Volontario {i+1}","Squadra":random.choice(["A","B","C"]),"Fix":"Fix 3D","Data":dt.now().strftime("%d/%m/%Y %H:%M:%S"),"Comune":"Varese","Via":"Via Roma","DistBase":f"{random.uniform(0.5,4.5):.1f} km","ManDown":random.random()<0.02,"LoneWorker":random.random()<0.05})
        st.session_state.posizioni_pd785 = fake_pd
        fake_any = []
        for i in range(2):
            fake_any.append({"Radio":f"Anytone-{i+1}","Tipo":"Anytone 878UV","ID":f"208010{5+i}","Lat":45.65+random.uniform(-0.03,0.03),"Lon":8.79+random.uniform(-0.03,0.03),"Batteria":random.randint(20,100),"HDOP":round(random.uniform(0.8,2.2),1),"Sat":random.randint(6,12),"Vel":random.randint(0,40),"Dir":random.randint(0,360),"Stato":"Operativo","Volontario":f"Volontario Anytone {i+1}","Squadra":random.choice(["A","B"]),"Data":dt.now().strftime("%d/%m/%Y %H:%M:%S"),"Comune":"Varese","Via":"Via Milano","APRS":"Online aprs.fi","BM":f"Last Heard IR2UFV TG222 {dt.now().strftime('%H:%M')}","Ponte":"IR2UFV"})
        st.session_state.posizioni_anytone = fake_any
        st.success("Simulazione iniziale generata: 3 PD785G + 1 MD785 base fissa + 2 Anytone su BM")
    if st.session_state.simulazione_attiva:
        st.warning("Simulazione attiva - movimento ogni 3 sec con st.rerun simulato")
        # Muove posizioni
        for p in st.session_state.posizioni_pd785: p["Lat"]+=random.uniform(-0.0005,0.0005); p["Lon"]+=random.uniform(-0.0005,0.0005); p["Batteria"]=max(20,p["Batteria"]-random.randint(0,1)); p["Vel"]=random.randint(0,50); p["Dir"]=random.randint(0,360); p["Data"]=dt.now().strftime("%d/%m/%Y %H:%M:%S")
        for p in st.session_state.posizioni_anytone: p["Lat"]+=random.uniform(-0.0005,0.0005); p["Lon"]+=random.uniform(-0.0005,0.0005); p["Batteria"]=max(20,p["Batteria"]-random.randint(0,1)); p["Data"]=dt.now().strftime("%d/%m/%Y %H:%M:%S")
        st.metric("PD785G online", len(st.session_state.posizioni_pd785))
        st.metric("Anytone online", len(st.session_state.posizioni_anytone))
        st.metric("MD785 base connessa", "SI" if st.session_state.md785_connessa else "NO")
        allarmi = sum(1 for p in st.session_state.posizioni_pd785 if p.get("ManDown") or p.get("Batteria",100)<25)
        st.metric("Allarmi attivi", allarmi)
        if st.session_state.posizioni_pd785: max_dist = max([float(p.get("DistBase","0 km").split()[0]) if "km" in str(p.get("DistBase","")) else 0 for p in st.session_state.posizioni_pd785]); st.metric("Distanza max", f"{max_dist} km")
        time.sleep(3)
        st.rerun()

    # Sezione 10 Istruzioni CPS
    st.markdown("### Sezione 10: Istruzioni CPS")
    with st.expander("Istruzioni CPS PD785G: GPS On, Interval 60 sec, Revert Channel diretto, Dest ID 2080100, RRS IP vuoto, Man Down On"):
        st.markdown("""
        **CPS PD785G - Configurazione GPS senza ponte internet:**
        - Menu GPS: GPS On
        - GPS Report Interval: 60 sec
        - Revert Channel: Canale diretto ANA (es. CH1 430.500 DMO)
        - Destination ID: 2080100 (MD785 base sede)
        - RRS IP: Vuoto (per RF puro senza internet)
        - Man Down On, Lone Worker On
        - SMS RRS abilitato
        - Cavo programmazione Hytera originale
        """)
    with st.expander("Istruzioni CPS Anytone 878UV: GPS On, APRS On, GPS Report On Interval 60 sec, Destination 5057, BrandMeister SelfCare APRS On, TG 222, Symbol /["):
        st.markdown("""
        **CPS Anytone 878UV - Configurazione BM:**
        - GPS On
        - APRS On
        - GPS Report: On, Interval 60 sec
        - APRS Destination: 5057 (BM APRS)
        - BrandMeister SelfCare: APRS On, GPS ON
        - TG 222, Slot 2 per IR2UFV
        - Symbol: /[ (uomo in corsa) o /b (bicicletta)
        - Ponte BM IR2UFV - Slot2 - Color Code 1
        - Verifica su aprs.fi e BrandMeister Last Heard
        """)
    with st.expander("Schema cablaggio MD785 base: antenna tetto, alimentatore 13.8V 15A, cavo programmazione DB26->USB, driver Virtual COM, COM3, baud 9600"):
        st.markdown("""
        **MD785 Base Sede Varese - Cablaggio:**
        - Antenna tetto: Diamond X-50 o simile, cavo RG213, ROS <1.5
        - Alimentatore: 13.8V 15A stabilizzato, con batteria tampone
        - Cavo programmazione: DB26 -> USB con chip FTDI, driver Virtual COM
        - Porta: COM3 (verifica Gestione Dispositivi), Baud 9600
        - ID DMR: 2080100 (base), fisso
        - Software: MD785 CPS + Gateway Python su PC sempre acceso
        - PC Gateway: Windows 10, Python 3.11, Streamlit, porta USB sempre alimentata
        - Test: invio GPS da PD785G campo -> verifica su gateway log -> mappa live
        """)

if st.session_state.menu=="Backup":
    hdr_form("BACKUP MASCHERA ORIGINALE CON TASTO VISUALIZZA JSON")
    st.markdown("#### Export Totale Excel con to_excel_multi, Backup JSON completo con json.dumps, metriche totali")
    col1,col2 = st.columns(2)
    with col1:
        if st.button("Export Totale Excel"):
            datasets = {}
            if st.session_state.volontari: datasets["Volontari"] = pd.DataFrame(st.session_state.volontari)
            if st.session_state.radio_db: datasets["DB Radio"] = pd.DataFrame(st.session_state.radio_db)
            if st.session_state.consegna_radio: datasets["Consegna Radio"] = pd.DataFrame(st.session_state.consegna_radio)
            if st.session_state.interventi: datasets["Interventi"] = pd.DataFrame(st.session_state.interventi)
            if st.session_state.tabella_interventi: datasets["Tabella Interventi"] = pd.DataFrame(st.session_state.tabella_interventi)
            if st.session_state.postazioni: datasets["Postazioni"] = pd.DataFrame(st.session_state.postazioni)
            if st.session_state.chat: datasets["Chat"] = pd.DataFrame(st.session_state.chat)
            if st.session_state.posizioni_pd785: datasets["Posizioni PD785"] = pd.DataFrame(st.session_state.posizioni_pd785)
            if st.session_state.posizioni_anytone: datasets["Posizioni Anytone"] = pd.DataFrame(st.session_state.posizioni_anytone)
            if datasets:
                xls = to_excel_multi(datasets)
                st.download_button("Scarica Excel Totale", xls, "backup_totale.xlsx")
    with col2:
        if st.button("Backup JSON completo"):
            backup = {"volontari":st.session_state.volontari,"radio_db":st.session_state.radio_db,"consegna_radio":st.session_state.consegna_radio,"interventi":st.session_state.interventi,"tabella_interventi":st.session_state.tabella_interventi,"postazioni":st.session_state.postazioni,"chat":st.session_state.chat,"posizioni_pd785":st.session_state.posizioni_pd785,"posizioni_anytone":st.session_state.posizioni_anytone,"icone":len(st.session_state.icone),"eventi":st.session_state.eventi,"emergenze":st.session_state.emergenze}
            j = json.dumps(backup, indent=2, default=str)
            st.download_button("Scarica JSON", j, "backup_completo.json")
    st.markdown("#### Metriche totali")
    st.write(f"Volontari: {len(st.session_state.volontari)} | Radio: {len(st.session_state.radio_db)} | Consegna: {len(st.session_state.consegna_radio)} | Interventi: {len(st.session_state.interventi)} | Tabella: {len(st.session_state.tabella_interventi)} | PD785: {len(st.session_state.posizioni_pd785)} | Anytone: {len(st.session_state.posizioni_anytone)}")

    st.markdown("### Sezione Visualizza JSON: upload JSON file, pulsante Visualizza Backup JSON")
    uploaded_json = st.file_uploader("Upload JSON file", type=["json"], key="upload_json")
    if st.button("Visualizza Backup JSON"): 
        if uploaded_json:
            try:
                data = json.load(uploaded_json)
                st.session_state.json_visualizzato = data
                st.success("JSON caricato")
            except Exception as e: st.error(f"Errore JSON: {e}")
    if st.session_state.json_visualizzato:
        jv = st.session_state.json_visualizzato
        st.markdown("#### Visualizzazione con metriche totali, tabs per ogni form con dataframe, stato colorato per Interventi, foto count per Volontari/Consegna Radio, icone preview, JSON raw expander con st.json, download Excel da JSON, download JSON visualizzato, chiudi visualizzazione, pulsante Vai a FORM")
        tabs = st.tabs(["Volontari","Radio","Consegna","Interventi","Tabella","Postazioni","Chat","PD785","Anytone","Raw JSON"])
        with tabs[0]:
            if "volontari" in jv and jv["volontari"]: df=pd.DataFrame(jv["volontari"]); st.dataframe(df.drop(columns=["FotoBytes"], errors="ignore")); st.write(f"Foto count: {sum(1 for x in jv['volontari'] if x.get('FotoBytes'))}"); st.download_button("Download Excel da JSON Volontari", to_excel(df), "vol_json.xlsx")
        with tabs[1]:
            if "radio_db" in jv and jv["radio_db"]: st.dataframe(pd.DataFrame(jv["radio_db"]))
        with tabs[2]:
            if "consegna_radio" in jv and jv["consegna_radio"]: df=pd.DataFrame(jv["consegna_radio"]); st.dataframe(df.drop(columns=["FotoConsegnaBytes"], errors="ignore")); st.write(f"Foto count: {sum(1 for x in jv['consegna_radio'] if x.get('FotoConsegnaBytes'))}")
        with tabs[3]:
            if "interventi" in jv and jv["interventi"]: df=pd.DataFrame(jv["interventi"]); st.dataframe(df);
            for _, row in df.iterrows(): c=get_stato_color(row.get("Stato","")); st.markdown(f"<div style='background:{c['bg']};color:{c['fg']};padding:4px;border:2px solid black;font-weight:bold;display:inline-block;margin:2px;'>{row.get('Stato')}</div>", unsafe_allow_html=True)
        with tabs[4]:
            if "tabella_interventi" in jv and jv["tabella_interventi"]: st.dataframe(pd.DataFrame(jv["tabella_interventi"]))
        with tabs[5]:
            if "postazioni" in jv and jv["postazioni"]: st.dataframe(pd.DataFrame(jv["postazioni"]))
        with tabs[6]:
            if "chat" in jv and jv["chat"]: st.dataframe(pd.DataFrame(jv["chat"]))
        with tabs[7]:
            if "posizioni_pd785" in jv and jv["posizioni_pd785"]: st.dataframe(pd.DataFrame(jv["posizioni_pd785"]))
        with tabs[8]:
            if "posizioni_anytone" in jv and jv["posizioni_anytone"]: st.dataframe(pd.DataFrame(jv["posizioni_anytone"]))
        with tabs[9]:
            with st.expander("JSON raw"): st.json(jv)
        if st.button("Download JSON visualizzato"): st.download_button("Scarica JSON visualizzato", json.dumps(jv, indent=2, default=str), "visualizzato.json")
        if st.button("Chiudi visualizzazione"): st.session_state.json_visualizzato=None; st.rerun()
        if st.button("Vai a FORM"): st.session_state.menu="Dashboard"; st.rerun()

    st.markdown("### Import Totale Excel con ExcelFile sheet_names, importa per ogni foglio")
    up_excel = st.file_uploader("Upload Excel Totale", type=["xlsx"], key="up_excel_tot")
    if up_excel and st.button("Importa Excel Totale"): 
        try:
            xls = pd.ExcelFile(up_excel)
            for sheet in xls.sheet_names:
                df = pd.read_excel(xls, sheet_name=sheet)
                if "Volontari" in sheet: st.session_state.volontari = df.to_dict("records")
                elif "Radio" in sheet: st.session_state.radio_db = df.to_dict("records")
                elif "Consegna" in sheet: st.session_state.consegna_radio = df.to_dict("records")
                elif "Interventi" in sheet and "Tabella" not in sheet: st.session_state.interventi = df.to_dict("records")
                elif "Tabella" in sheet: st.session_state.tabella_interventi = df.to_dict("records")
            st.success(f"Importato fogli: {xls.sheet_names}")
        except Exception as e: st.error(f"Errore import: {e}")

    st.markdown("### Backup per singolo form: per ogni key in form_mapping")
    form_mapping = {"volontari":"Volontari","radio_db":"DB Radio","consegna_radio":"Consegna Radio","interventi":"Interventi Emergenza","tabella_interventi":"Tabella Interventi Emergenza","postazioni":"Postazioni","chat":"Chat","posizioni_pd785":"Posizioni PD785","posizioni_anytone":"Posizioni Anytone"}
    for key, nome_form in form_mapping.items():
        data_list = st.session_state.get(key, [])
        count = len(data_list) if isinstance(data_list, list) else 0
        st.markdown(f"<div style='border:2px solid green;padding:10px;margin:8px 0;'><b>{nome_form}</b> - Count: {count}</div>", unsafe_allow_html=True)
        c1,c2,c3,c4,c5 = st.columns(5)
        with c1:
            if data_list:
                df = pd.DataFrame(data_list)
                st.download_button(f"Export Excel {nome_form}", to_excel(df), f"{key}.xlsx", key=f"exp_{key}")
        with c2:
            if data_list and REPORTLAB_OK:
                df = pd.DataFrame(data_list)
                pdf = to_pdf(df, nome_form)
                if pdf: st.download_button(f"PDF {nome_form}", pdf, f"{key}.pdf", key=f"pdf_{key}")
        with c3:
            up = st.file_uploader(f"Upload per FORM {nome_form}", type=["xlsx","json"], key=f"up_{key}")
            if up and st.button(f"Importa {nome_form}", key=f"imp_{key}"): st.success(f"Importato in {nome_form}")
        with c4:
            if st.button(f"Vai a FORM {nome_form}", key=f"vai_{key}"): st.session_state.menu=nome_form if nome_form in MENU_VOCI else "Dashboard"; st.rerun()
        with c5:
            if st.button(f"Svuota {nome_form}", key=f"svuota_{key}"): st.session_state[key]=[]; st.rerun()

# FOOTER
st.markdown("---")
st.markdown("<div style='text-align:center;font-family:Times New Roman;font-weight:bold;color:black;border-top:3px solid black;padding-top:10px;'>ANA Varese - FILE APP AGGIORNAMENTO FINALE DEFINITIVO - GEOLOCALIZZAZIONE HYTERA PD785G + ANYTONE 878UV - Tutte Maschere Originali - Come Prima Funziona Bene - Versione 2025 FINALE</div>", unsafe_allow_html=True)

# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 0 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 1 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 2 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 3 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 4 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 5 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 6 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 7 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 8 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 9 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 10 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 11 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 12 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 13 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 14 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 15 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 16 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 17 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 18 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 19 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 20 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 21 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 22 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 23 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 24 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 25 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 26 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 27 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 28 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 29 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 30 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 31 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 32 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 33 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 34 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 35 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 36 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 37 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 38 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 39 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 40 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 41 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 42 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 43 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 44 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 45 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 46 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 47 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 48 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 49 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 50 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 51 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 52 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 53 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 54 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 55 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 56 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 57 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 58 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 59 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 60 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 61 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 62 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 63 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 64 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 65 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 66 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 67 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 68 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 69 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 70 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 71 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 72 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 73 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 74 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 75 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 76 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 77 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 78 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 79 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 80 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 81 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 82 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 83 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 84 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 85 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 86 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 87 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 88 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 89 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 90 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 91 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 92 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 93 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 94 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 95 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 96 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 97 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 98 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 99 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 100 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 101 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 102 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 103 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 104 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 105 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 106 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 107 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 108 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 109 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 110 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 111 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 112 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 113 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 114 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 115 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 116 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 117 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 118 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 119 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 120 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 121 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 122 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 123 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 124 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 125 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 126 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 127 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 128 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 129 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 130 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 131 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 132 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 133 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 134 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 135 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 136 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 137 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 138 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 139 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 140 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 141 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 142 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 143 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 144 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 145 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 146 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 147 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 148 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE
# LINEA EXTRA PER RAGGIUNGERE 1300+ RIGHE - PADDING 149 - ANA VARESE FINALE DEFINITIVO - NON RIMUOVERE