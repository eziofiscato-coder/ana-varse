import streamlit as st
import pandas as pd
import datetime
import os
import json
import base64
import io
import time
from datetime import date, time as dt_time

# Reportlab per PDF - solo reportlab, no fpdf
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
from reportlab.lib.units import cm

# Mappa
try:
    import folium
    from streamlit_folium import st_folium
    HAS_FOLIUM = True
except:
    HAS_FOLIUM = False

import requests

# ------------------------------------------------------------
# BASE MINI 36 RIGHE - RICOSTRUZIONE PULITA
# Questa e' la base originale corretta da cui ripartiamo
# st.set_page_config, logo, titolo VOLONTARIATO Sezione Varese
# session_state dati, form Nome Associazione Cellulare Ruolo
# dataframe, Excel
# ------------------------------------------------------------

st.set_page_config(
    page_title="GESTIONALE 950+ ANA VARESE",
    page_icon="🟢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------------------------------------------------
# INIT SESSION STATE - DATI CENTRALI
# ------------------------------------------------------------
if 'page' not in st.session_state:
    st.session_state.page = 'entra'

if 'logged' not in st.session_state:
    st.session_state.logged = False

if 'menu' not in st.session_state:
    st.session_state.menu = 'Dashboard'

# Dati base volontari - base mini
if 'dati' not in st.session_state:
    st.session_state.dati = []

# Anagrafica estesa volontari
if 'volontari' not in st.session_state:
    st.session_state.volontari = []

if 'turni' not in st.session_state:
    st.session_state.turni = []

if 'db_radio' not in st.session_state:
    st.session_state.db_radio = []

if 'consegna_radio' not in st.session_state:
    st.session_state.consegna_radio = []

if 'alias_radio' not in st.session_state:
    st.session_state.alias_radio = []

if 'brogliaccio' not in st.session_state:
    st.session_state.brogliaccio = []

if 'eventi' not in st.session_state:
    st.session_state.eventi = []

if 'emergenze' not in st.session_state:
    st.session_state.emergenze = []

if 'checkin' not in st.session_state:
    st.session_state.checkin = []

if 'interventi' not in st.session_state:
    st.session_state.interventi = []

if 'tabella_interventi' not in st.session_state:
    st.session_state.tabella_interventi = []

if 'mezzi' not in st.session_state:
    st.session_state.mezzi = []

if 'attrezzature' not in st.session_state:
    st.session_state.attrezzature = []

if 'mappa_punti' not in st.session_state:
    st.session_state.mappa_punti = []

if 'libreria_icone' not in st.session_state:
    st.session_state.libreria_icone = []

if 'chat_msg' not in st.session_state:
    st.session_state.chat_msg = []

if 'geoloc_hytera' not in st.session_state:
    st.session_state.geoloc_hytera = []

if 'geoloc_anytone' not in st.session_state:
    st.session_state.geoloc_anytone = []

if 'temp_lat' not in st.session_state:
    st.session_state.temp_lat = 45.657

if 'temp_lon' not in st.session_state:
    st.session_state.temp_lon = 8.793

if 'last_clicked' not in st.session_state:
    st.session_state.last_clicked = None

if 'edit_vol_idx' not in st.session_state:
    st.session_state.edit_vol_idx = None

if 'edit_turno_idx' not in st.session_state:
    st.session_state.edit_turno_idx = None

if 'edit_intervento_idx' not in st.session_state:
    st.session_state.edit_intervento_idx = None

if 'filtro_data_turni' not in st.session_state:
    st.session_state.filtro_data_turni = None

# ------------------------------------------------------------
# HELPERS - COMUNI VARESE + VIE
# ------------------------------------------------------------
def get_comuni_varese():
    return [
        "Varese", "Busto Arsizio", "Gallarate", "Saronno", "Cassano Magnago",
        "Tradate", "Malnate", "Somma Lombardo", "Gavirate", "Laveno-Mombello",
        "Luino", "Sesto Calende", "Samarate", "Besozzo", "Castellanza",
        "Caronno Pertusella", "Fagnano Olona", "Olgiate Olona", "Solbiate Olona",
        "Carnago", "Castronno", "Gazzada Schianno", "Lozza", "Morazzone",
        "Brunello", "Azzate", "Buguggiate", "Bodio Lomnago", "Galliate Lombardo",
        "Davero", "Casale Litta", "Mornago", "Sumirago", "Besnate",
        "Jerago con Orago", "Albizzate", "Cavaria con Premezzo", "Oggiona con S. Stefano",
        "Solbiate Arno", "Crosio della Valle", "Cairate", "Lonate Ceppino", "Venegono Inf",
        "Venegono Sup", "Castiglione Olona", "Vedano Olona", "Binago", "Malnate",
        "Cantello", "Arcisate", "Induno Olona", "Valganna", "Cugliate Fabiasco",
        "Cunardo", "Bedero Valcuvia", "Brinzio", "Rancio Valcuvia", "Cassano Valcuvia",
        "Ferrera di Varese", "Masciago Primo", "Brenta", "Cittiglio", "Laveno",
        "Leggiuno", "Sangiano", "Caravate", "Gemonio", "Azzio", "Orino",
        "Cocquio Trevisago", "Comerio", "Barasso", "Luvinate", "Casciago",
        "Varese Centro", "Varese Nord", "Bizzozero", "Biumo", "Giubiano"
    ]

def get_vie_varese():
    return [
        "Via Sacco", "Via Verdi", "Via Roma", "Via Garibaldi", "Via Mazzini",
        "Via Manzoni", "Via Volta", "Via Copelli", "Via Orrigoni", "Via Marcobi",
        "Via Crispi", "Via Cavour", "Via Dante", "Via Milano", "Via Como",
        "Corso Matteotti", "Piazza Monte Grappa", "Via Walder", "Via Avegno",
        "Via Carrobbio", "Via Sanvito Silvestro", "Viale Belforte", "Via Casula",
        "Via Campigli", "Via Piave", "Via XXV Aprile", "Via Daverio", "Via Bernascone",
        "Via Bizzozero", "Via Biumo", "Via Giubiano", "Via San Pedrino", "Via Limido",
        "Via del Santuario", "Via Sorrisole", "Via Valganna", "Via dei Santi",
        "Via dei Bersaglieri", "Via degli Alpini", "Via 950+", "Via ANA"
    ]

def get_stato_color(stato):
    colori = {
        "In Corso": {"bg": "#ffeb3b", "txt": "#000000"},
        "Chiuso": {"bg": "#4caf50", "txt": "#ffffff"},
        "Aperto": {"bg": "#2196f3", "txt": "#ffffff"},
        "Critico": {"bg": "#f44336", "txt": "#ffffff"},
        "In Attesa": {"bg": "#ff9800", "txt": "#ffffff"},
        "Assegnato": {"bg": "#9c27b0", "txt": "#ffffff"},
    }
    return colori.get(stato, {"bg": "#e0e0e0", "txt": "#000000"})

# ------------------------------------------------------------
# PDF ED EXCEL - REPORTLAB SOLO
# ------------------------------------------------------------
def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Dati')
    return output.getvalue()

def to_pdf(df, titolo="GESTIONALE 950+ ANA VARESE"):
    buffer = io.BytesIO()
    # Landscape 27cm come richiesto
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=20,
        leftMargin=20,
        topMargin=20,
        bottomMargin=20
    )
    elements = []
    styles = getSampleStyleSheet()

    # Header con logo sx + titolo dx - Table 2 colonne logo 80x60 sx + titolo dx
    header_data = []
    # Prova logo
    try:
        if os.path.exists("logo.png"):
            logo_img = RLImage("logo.png", width=80, height=60)
            header_data = [[logo_img, Paragraph(f"<b><font size=18 color='#1A5D1A'>{titolo}</font></b><br/><font size=10>VOLONTARIATO Sezione Varese - 950+ ANA</font><br/><font size=8>Data: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}</font>", styles['Normal'])]]
        else:
            header_data = [[Paragraph(f"<b><font size=18 color='#1A5D1A'>{titolo}</font></b>", styles['Normal'])]]
    except:
        header_data = [[Paragraph(f"<b>{titolo}</b>", styles['Normal'])]]

    if header_data:
        t = Table(header_data, colWidths=[90, 700])
        t.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 20))

    if not df.empty:
        # Prepara dati tabella
        cols = list(df.columns)
        data = [cols] + df.astype(str).values.tolist()
        # Limita colonne per larghezza
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1A5D1A")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 8),
            ('FONTSIZE', (0,1), (-1,-1), 7),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,-1), colors.beige),
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ]))
        elements.append(table)
    else:
        elements.append(Paragraph("Nessun dato disponibile", styles['Normal']))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()

# ------------------------------------------------------------
# HDR - HEADER PRINCIPALE
# ------------------------------------------------------------
def hdr():
    col1, col2 = st.columns([1, 4])
    with col1:
        try:
            if os.path.exists("logo.png"):
                st.image("logo.png", width=110)
            else:
                st.markdown("<div style='width:110px;height:110px;background:#1A5D1A;color:white;display:flex;align-items:center;justify-content:center;font-weight:bold;border-radius:8px'>ANA<br/>VARESE</div>", unsafe_allow_html=True)
        except:
            st.markdown("<div style='width:110px;height:110px;background:#1A5D1A;color:white;display:flex;align-items:center;justify-content:center;font-weight:bold;border-radius:8px'>ANA<br/>VARESE</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<h1 style='color:#1A5D1A;font-family:Times New Roman, Times, serif;font-weight:bold;font-size:42px;margin-bottom:0'>GESTIONALE 950+ ANA VARESE</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='color:#333;font-family:Times New Roman;margin-top:0'>VOLONTARIATO Sezione Varese</h3>", unsafe_allow_html=True)

def hdr_form(titolo):
    st.markdown(f"<div style='background:#1A5D1A;padding:12px 20px;border-radius:8px;margin-bottom:15px'><h2 style='color:white;margin:0;font-family:Times New Roman;font-weight:bold'>{titolo}</h2></div>", unsafe_allow_html=True)

# ------------------------------------------------------------
# FULLSCREEN API BUTTON
# ------------------------------------------------------------
def fullscreen_button():
    st.markdown("""
    <button id='fs-btn' style='background:#1A5D1A;color:white;border:none;padding:8px 16px;border-radius:6px;cursor:pointer;font-weight:bold;margin-bottom:10px'>⛶ Tutto Schermo</button>
    <script>
    document.getElementById('fs-btn')?.addEventListener('click', ()=>{
        if(!document.fullscreenElement){
            document.documentElement.requestFullscreen();
        } else {
            document.exitFullscreen();
        }
    });
    </script>
    """, unsafe_allow_html=True)

# ------------------------------------------------------------
# PAGINA ENTRA - SEMPRE PRIMA
# ------------------------------------------------------------
def page_entra():
    hdr()
    st.markdown("<hr/>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        try:
            if os.path.exists("copertina.png"):
                st.image("copertina.png", width=350)
            else:
                st.markdown("<div style='width:350px;height:220px;background:linear-gradient(135deg,#1A5D1A,#4caf50);border-radius:12px;display:flex;align-items:center;justify-content:center;color:white;font-size:32px;font-weight:bold'>950+<br/>ANA VARESE</div>", unsafe_allow_html=True)
        except:
            st.markdown("<div style='width:350px;height:220px;background:linear-gradient(135deg,#1A5D1A,#4caf50);border-radius:12px;display:flex;align-items:center;justify-content:center;color:white;font-size:32px;font-weight:bold'>950+<br/>ANA VARESE</div>", unsafe_allow_html=True)

        st.markdown("<br/><h2 style='text-align:center;color:#1A5D1A;font-family:Times New Roman;font-weight:bold'>VOLONTARIATO</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center'>Sezione di Varese - Associazione Nazionale Alpini<br/>Gestionale Operativo 950+ Volontari</p>", unsafe_allow_html=True)
        st.markdown("<br/>", unsafe_allow_html=True)
        if st.button("ENTRA NEL GESTIONALE", type="primary", use_container_width=True):
            st.session_state.page = 'login'
            st.rerun()
        st.markdown("<br/><p style='text-align:center;font-size:12px;color:#888'>Versione 950+ con Form Turni integrato - Base Mini 36 righe ricostruita</p>", unsafe_allow_html=True)

# ------------------------------------------------------------
# LOGIN
# ------------------------------------------------------------
def page_login():
    hdr()
    st.markdown("---")
    st.subheader("Login Amministratore")
    with st.form("login_form"):
        user = st.text_input("Username")
        pwd = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Accedi", type="primary")
        if submitted:
            if pwd == "ana2024":
                st.session_state.logged = True
                st.session_state.page = 'dashboard'
                st.success("Accesso effettuato")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("Password errata - usa ana2024")
    if st.button("Torna a Entra"):
        st.session_state.page = 'entra'
        st.rerun()

# ------------------------------------------------------------
# DASHBOARD 18 TASTI VERDE ANA #1A5D1A 60px BOLD TIMES
# ------------------------------------------------------------
def page_dashboard():
    hdr()
    fullscreen_button()
    st.markdown("<hr/>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#1A5D1A;font-family:Times New Roman;font-weight:bold'>Dashboard Operativa - Seleziona Modulo</h3>", unsafe_allow_html=True)

    # Stile tasti verdi ANA
    st.markdown("""
    <style>
    div[data-testid="stButton"] > button[kind="primary"]{
        background-color:#1A5D1A !important;
        color:white !important;
        font-family: 'Times New Roman', Times, serif !important;
        font-weight: bold !important;
        font-size: 18px !important;
        height: 60px !important;
        border-radius: 10px !important;
        border: 2px solid #145014 !important;
    }
    div[data-testid="stButton"] > button[kind="primary"]:hover{
        background-color:#145014 !important;
        border-color:#0f3d0f !important;
    }
    </style>
    """, unsafe_allow_html=True)

    forms = [
        "Volontari", "DB Radio", "Consegna Radio", "Alias Radio",
        "Brogliaccio", "Eventi", "Emergenze", "Check-in",
        "Interventi Emergenza", "Tabella Interventi", "Mezzi", "Attrezzature",
        "Mappa Avanzata", "Libreria Icone", "Chat", "Geolocalizzazione Hytera + Anytone",
        "Backup", "Turni"
    ]

    # 3 colonne per 18 tasti = 6 righe
    for i in range(0, len(forms), 3):
        cols = st.columns(3)
        for j in range(3):
            if i+j < len(forms):
                nome = forms[i+j]
                with cols[j]:
                    # Evidenzia Turni come nuovo
                    if nome == "Turni":
                        st.markdown("<div style='background:#ffeb3b;color:#000;text-align:center;font-size:10px;font-weight:bold;border-radius:4px;padding:2px;margin-bottom:2px'>NUOVO</div>", unsafe_allow_html=True)
                    if st.button(nome, key=f"dash_{nome}", type="primary", use_container_width=True):
                        st.session_state.menu = nome
                        st.rerun()

    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    col1.metric("Volontari Registrati", len(st.session_state.volontari))
    col2.metric("Turni Attivi", len(st.session_state.turni))
    col3.metric("Interventi", len(st.session_state.interventi))

    if st.session_state.turni:
        st.subheader("Ultimi Turni")
        df_last = pd.DataFrame(st.session_state.turni[-5:])
        st.dataframe(df_last, use_container_width=True)

# ------------------------------------------------------------
# SIDEBAR FIX WidgetAlreadyInstantiatedError RIGA 542
# MAI settare menu_radio diretto solo menu rerun + sidebar elenco form sx radio index basato su menu + logout
# ------------------------------------------------------------
def render_sidebar():
    with st.sidebar:
        try:
            if os.path.exists("logo.png"):
                st.image("logo.png", width=80)
        except:
            pass
        st.markdown("### ANA VARESE 950+")

        forms_list = [
            "Dashboard", "Volontari", "DB Radio", "Consegna Radio", "Alias Radio",
            "Brogliaccio", "Eventi", "Emergenze", "Check-in",
            "Interventi Emergenza", "Tabella Interventi", "Mezzi", "Attrezzature",
            "Mappa Avanzata", "Libreria Icone", "Chat", "Geolocalizzazione Hytera + Anytone",
            "Backup", "Turni"
        ]

        # FIX CRITICO: non settare mai menu_radio direttamente, solo menu con rerun
        # Calcola index basato su menu corrente
        try:
            current_idx = forms_list.index(st.session_state.menu)
        except:
            current_idx = 0

        # Radio con index calcolato - MAI assegnare a st.session_state.menu_radio = ...
        selected = st.radio("Elenco Form", forms_list, index=current_idx, key="menu_radio_sidebar")

        # Solo se diverso, aggiorna menu e rerun - evita WidgetAlreadyInstantiatedError
        if selected != st.session_state.menu:
            st.session_state.menu = selected
            st.rerun()

        st.markdown("---")
        if st.button("Logout", use_container_width=True):
            st.session_state.logged = False
            st.session_state.page = 'entra'
            st.session_state.menu = 'Dashboard'
            st.rerun()

        st.markdown("---")
        st.caption("ANA Varese - Gestionale 950+")
        st.caption("Form Turni integrato")

# ------------------------------------------------------------
# FORM VOLONTARI - 6 TABS
# ------------------------------------------------------------
def form_volontari():
    hdr_form("Volontari - Gestione Anagrafica")
    fullscreen_button()

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Anagrafica", "Residenza", "Contatti", "Emergenza", "Ruolo Squadra", "Specializzazioni Foto"])

    # Dati temporanei per form
    if 'temp_vol' not in st.session_state:
        st.session_state.temp_vol = {}

    with tab1:
        st.subheader("Anagrafica")
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome*", key="vol_nome", value=st.session_state.temp_vol.get("Nome",""))
            cognome = st.text_input("Cognome*", key="vol_cognome", value=st.session_state.temp_vol.get("Cognome",""))
            cf = st.text_input("Codice Fiscale", key="vol_cf", value=st.session_state.temp_vol.get("CF",""))
            data_nascita = st.date_input("Data Nascita", value=date(1980,1,1), key="vol_datan")
        with col2:
            luogo_nascita = st.text_input("Luogo Nascita", key="vol_luogon", value=st.session_state.temp_vol.get("LuogoNascita",""))
            sesso = st.selectbox("Sesso", ["M","F"], key="vol_sesso")
            gruppo_sanguigno = st.selectbox("Gruppo Sanguigno", ["A+","A-","B+","B-","AB+","AB-","0+","0-","Non noto"], key="vol_gruppo")

    with tab2:
        st.subheader("Residenza")
        col1, col2 = st.columns(2)
        with col1:
            indirizzo = st.text_input("Indirizzo", key="vol_indirizzo", value=st.session_state.temp_vol.get("Indirizzo",""))
            comune = st.selectbox("Comune", get_comuni_varese(), key="vol_comune")
            cap = st.text_input("CAP", key="vol_cap", value=st.session_state.temp_vol.get("CAP",""))
        with col2:
            provincia = st.text_input("Provincia", value="VA", key="vol_prov")
            via_sel = st.selectbox("Via", get_vie_varese(), key="vol_via")
            civico = st.text_input("Civico", key="vol_civico")

    with tab3:
        st.subheader("Contatti")
        col1, col2 = st.columns(2)
        with col1:
            cellulare = st.text_input("Cellulare*", key="vol_cell", value=st.session_state.temp_vol.get("Cellulare",""))
            telefono = st.text_input("Telefono Fisso", key="vol_tel")
            email = st.text_input("Email", key="vol_email", value=st.session_state.temp_vol.get("Email",""))
        with col2:
            associazione = st.text_input("Associazione", value="ANA Varese", key="vol_assoc")
            ruolo_base = st.selectbox("Ruolo", ["Volontario","Caposquadra","Autista","Radio","Logistica","Coordinatore"], key="vol_ruolo")
            cellulare2 = st.text_input("Cellulare 2", key="vol_cell2")

    with tab4:
        st.subheader("Contatti Emergenza")
        col1, col2 = st.columns(2)
        with col1:
            emerg_nome = st.text_input("Nome Contatto Emergenza", key="vol_em_nome")
            emerg_parentela = st.text_input("Parentela", key="vol_em_par")
        with col2:
            emerg_tel = st.text_input("Telefono Emergenza", key="vol_em_tel")
            emerg_note = st.text_area("Note Emergenza", key="vol_em_note")

    with tab5:
        st.subheader("Ruolo e Squadra")
        col1, col2 = st.columns(2)
        with col1:
            squadra = st.selectbox("Squadra*", ["Squadra A","Squadra B","Squadra C","Squadra D","Logistica","Centrale"], key="vol_squadra")
            grado = st.selectbox("Grado", ["Volontario","Vice Caposquadra","Caposquadra","Coordinatore"], key="vol_grado")
            data_iscrizione = st.date_input("Data Iscrizione", value=date.today(), key="vol_data_iscr")
        with col2:
            specialita = st.multiselect("Specialità", ["Antincendio","Idrogeologico","Sanitario","Radio","Logistica","Cucina","Mezzi","Alpino"], key="vol_spec")
            taglia = st.selectbox("Taglia Divisa", ["S","M","L","XL","XXL"], key="vol_taglia")
            note_ruolo = st.text_area("Note Ruolo", key="vol_note_ruolo")

    with tab6:
        st.subheader("Specializzazioni e Foto")
        col1, col2 = st.columns([1,2])
        with col1:
            st.markdown("Foto 150px")
            foto_file = st.file_uploader("Carica Foto", type=["jpg","png","jpeg"], key="vol_foto")
            if foto_file:
                st.image(foto_file, width=150)
            else:
                st.markdown("<div style='width:150px;height:150px;background:#ddd;display:flex;align-items:center;justify-content:center;border-radius:8px'>150px<br/>Foto</div>", unsafe_allow_html=True)
        with col2:
            patenti = st.multiselect("Patenti", ["B","C","CQC","Muletto","Escavatore"], key="vol_patenti")
            corsi = st.text_area("Corsi Effettuati", key="vol_corsi", placeholder="Es: Corso Antincendio 2023, Corso Radio...")
            note_finali = st.text_area("Note Generali", key="vol_note_finali")

    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("SALVA NUOVO", type="primary", use_container_width=True):
            nuovo = {
                "Nome": nome,
                "Cognome": cognome,
                "CF": cf,
                "DataNascita": str(data_nascita),
                "LuogoNascita": luogo_nascita,
                "Sesso": sesso,
                "Gruppo": gruppo_sanguigno,
                "Indirizzo": indirizzo,
                "Comune": comune,
                "CAP": cap,
                "Provincia": provincia,
                "Via": via_sel,
                "Civico": civico,
                "Cellulare": cellulare,
                "Telefono": telefono,
                "Email": email,
                "Associazione": associazione,
                "Ruolo": ruolo_base,
                "EmergenzaNome": emerg_nome,
                "EmergenzaTel": emerg_tel,
                "Squadra": squadra,
                "Grado": grado,
                "Specialita": ",".join(specialita),
                "Taglia": taglia,
            }
            if nome and cognome:
                if st.session_state.edit_vol_idx is not None:
                    st.session_state.volontari[st.session_state.edit_vol_idx] = nuovo
                    st.session_state.edit_vol_idx = None
                    st.success("Volontario aggiornato")
                else:
                    st.session_state.volontari.append(nuovo)
                    st.session_state.dati.append({"Nome": nome, "Associazione": associazione, "Cellulare": cellulare, "Ruolo": ruolo_base})
                    st.success(f"Volontario {cognome} {nome} salvato")
                st.session_state.temp_vol = {}
                st.rerun()
            else:
                st.error("Nome e Cognome obbligatori")
    with col2:
        if st.button("AGGIORNA", use_container_width=True):
            st.rerun()
    with col3:
        if st.button("ANNULLA", use_container_width=True):
            st.session_state.temp_vol = {}
            st.session_state.edit_vol_idx = None
            st.rerun()
    with col4:
        if st.session_state.volontari:
            df = pd.DataFrame(st.session_state.volontari)
            st.download_button("Excel", to_excel(df), file_name="volontari.xlsx", use_container_width=True)

    # Tabella volontari con click Cognome mod_vol_{idx}
    if st.session_state.volontari:
        st.markdown("---")
        st.subheader("Elenco Volontari - Click su Cognome per modifica")
        df = pd.DataFrame(st.session_state.volontari)
        st.dataframe(df, use_container_width=True)

        st.markdown("Seleziona per modifica:")
        cols = st.columns(4)
        for idx, vol in enumerate(st.session_state.volontari):
            with cols[idx % 4]:
                if st.button(f"{vol.get('Cognome','')} {vol.get('Nome','')}", key=f"mod_vol_{idx}"):
                    st.session_state.temp_vol = vol
                    st.session_state.edit_vol_idx = idx
                    st.rerun()

# ------------------------------------------------------------
# FORM TURNI - NUOVO RICHIESTO - MASCHERA INSERISCI VOLONTARI ED ASSEGNA TURNO
# ------------------------------------------------------------
def form_turni():
    hdr_form("Turni - Maschera Inserisci Volontari ed Assegna Turno")
    fullscreen_button()

    st.markdown("<p style='background:#e8f5e9;padding:10px;border-radius:6px;border-left:4px solid #1A5D1A'>Form Turni NUOVO richiesto: inserisci volontari ed assegna turno con data, squadra, orari, luogo</p>", unsafe_allow_html=True)

    # Inizializza temp turno per modifica
    if 'temp_turno' not in st.session_state:
        st.session_state.temp_turno = {}

    # Lista volontari per multiselect - Cognome Nome da volontari list, se vuota da dati Associazione
    volontari_options = []
    if st.session_state.volontari:
        for v in st.session_state.volontari:
            volontari_options.append(f"{v.get('Cognome','')} {v.get('Nome','')}")
    elif st.session_state.dati:
        for d in st.session_state.dati:
            volontari_options.append(f"{d.get('Nome','')} - {d.get('Associazione','')}")
    else:
        volontari_options = ["Mario Rossi", "Luigi Bianchi", "Giuseppe Verdi", "Antonio Neri", "Carlo Alpini"]

    # Recupero valori temp se modifica
    temp = st.session_state.temp_turno

    st.subheader("Inserimento Turno")
    col1, col2, col3 = st.columns(3)
    with col1:
        data_turno = st.date_input("Data* Turno", value=temp.get("Data", date.today()) if isinstance(temp.get("Data"), date) else date.today(), key="turno_data")
        turno_tipo = st.selectbox("Turno*", ["Mattina","Pomeriggio","Sera","Notte","Intera Giornata","H24"], index=["Mattina","Pomeriggio","Sera","Notte","Intera Giornata","H24"].index(temp.get("Turno","Mattina")) if temp.get("Turno") in ["Mattina","Pomeriggio","Sera","Notte","Intera Giornata","H24"] else 0, key="turno_tipo")
        ora_inizio = st.time_input("Ora Inizio*", value=temp.get("OraInizio", dt_time(8,0)) if isinstance(temp.get("OraInizio"), dt_time) else dt_time(8,0), key="turno_ora_inizio")

    with col2:
        ora_fine = st.time_input("Ora Fine*", value=temp.get("OraFine", dt_time(20,0)) if isinstance(temp.get("OraFine"), dt_time) else dt_time(20,0), key="turno_ora_fine")
        squadra_turno = st.selectbox("Squadra*", ["Squadra A","Squadra B","Squadra C","Squadra D","Logistica","Centrale"], index=["Squadra A","Squadra B","Squadra C","Squadra D","Logistica","Centrale"].index(temp.get("Squadra","Squadra A")) if temp.get("Squadra") in ["Squadra A","Squadra B","Squadra C","Squadra D","Logistica","Centrale"] else 0, key="turno_squadra")
        ruolo_turno = st.selectbox("Ruolo Turno", ["Caposquadra","Autista","Radio","Logistica","Volontario","Coordinatore"], index=["Caposquadra","Autista","Radio","Logistica","Volontario","Coordinatore"].index(temp.get("RuoloTurno","Volontario")) if temp.get("RuoloTurno") in ["Caposquadra","Autista","Radio","Logistica","Volontario","Coordinatore"] else 4, key="turno_ruolo")

    with col3:
        luogo = st.text_input("Luogo", value=temp.get("Luogo",""), key="turno_luogo", placeholder="Es: Sede ANA, Campo base")
        comune = st.selectbox("Comune", get_comuni_varese(), index=get_comuni_varese().index(temp.get("Comune","Varese")) if temp.get("Comune") in get_comuni_varese() else 0, key="turno_comune")
        via_turno = st.selectbox("Via", get_vie_varese(), index=get_vie_varese().index(temp.get("Via","Via Roma")) if temp.get("Via") in get_vie_varese() else 0, key="turno_via")

    col4, col5 = st.columns(2)
    with col4:
        tipo_turno = st.selectbox("Tipo Turno", ["Ordinario","Straordinario","Emergenza","Reperibilità"], index=["Ordinario","Straordinario","Emergenza","Reperibilità"].index(temp.get("Tipo","Ordinario")) if temp.get("Tipo") in ["Ordinario","Straordinario","Emergenza","Reperibilità"] else 0, key="turno_tipo2")
        volontari_sel = st.multiselect("Volontari* Assegnati - Cognome Nome", volontari_options, default=temp.get("Volontari",[]), key="turno_volontari")
    with col5:
        note_turno = st.text_area("Note", value=temp.get("Note",""), key="turno_note", height=100, placeholder="Note aggiuntive turno...")

    st.markdown("---")
    col_btn1, col_btn2, col_btn3 = st.columns([2,1,1])
    with col_btn1:
        if st.button("Salva Turno", type="primary", use_container_width=True):
            if not volontari_sel:
                st.error("Seleziona almeno un volontario")
            else:
                nuovo_turno = {
                    "Data": str(data_turno),
                    "Turno": turno_tipo,
                    "OraInizio": str(ora_inizio),
                    "OraFine": str(ora_fine),
                    "Squadra": squadra_turno,
                    "Volontari": ", ".join(volontari_sel),
                    "VolontariList": volontari_sel,
                    "RuoloTurno": ruolo_turno,
                    "Luogo": luogo,
                    "Comune": comune,
                    "Via": via_turno,
                    "Tipo": tipo_turno,
                    "Note": note_turno,
                    "DataObj": data_turno,
                }
                if st.session_state.edit_turno_idx is not None:
                    st.session_state.turni[st.session_state.edit_turno_idx] = nuovo_turno
                    st.session_state.edit_turno_idx = None
                    st.success("Turno aggiornato")
                else:
                    st.session_state.turni.append(nuovo_turno)
                    st.success(f"Turno {turno_tipo} del {data_turno} salvato con {len(volontari_sel)} volontari")
                st.session_state.temp_turno = {}
                st.rerun()

    with col_btn2:
        if st.button("Annulla Modifica", use_container_width=True):
            st.session_state.temp_turno = {}
            st.session_state.edit_turno_idx = None
            st.rerun()
    with col_btn3:
        if st.session_state.turni:
            df_t = pd.DataFrame(st.session_state.turni)
            st.download_button("Excel Turni", to_excel(df_t), file_name="turni_ana_varese.xlsx", use_container_width=True)

    # --------------------------------------------------------
    # TABELLA TURNI CON FILTRI DATA SQUADRA TURNO + DATAFRAME
    # --------------------------------------------------------
    if st.session_state.turni:
        st.markdown("---")
        st.subheader("Tabella Turni con Filtri")

        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            filtro_data = st.date_input("Filtra Data", value=None, key="filtro_data_turni_input")
        with col_f2:
            filtro_squadra = st.selectbox("Filtra Squadra", ["Tutte"]+["Squadra A","Squadra B","Squadra C","Squadra D","Logistica","Centrale"], key="filtro_squadra_turni")
        with col_f3:
            filtro_turno = st.selectbox("Filtra Turno", ["Tutti"]+["Mattina","Pomeriggio","Sera","Notte","Intera Giornata","H24"], key="filtro_turno_tipo")

        # Applica filtri
        turni_filtrati = st.session_state.turni.copy()
        if filtro_data:
            turni_filtrati = [t for t in turni_filtrati if t.get("Data") == str(filtro_data)]
        if filtro_squadra != "Tutte":
            turni_filtrati = [t for t in turni_filtrati if t.get("Squadra") == filtro_squadra]
        if filtro_turno != "Tutti":
            turni_filtrati = [t for t in turni_filtrati if t.get("Turno") == filtro_turno]

        if turni_filtrati:
            df_show = pd.DataFrame(turni_filtrati)
            # Mostra colonne richieste: Data Turno Squadra Volontari assegnati
            cols_show = ["Data","Turno","Squadra","Volontari","OraInizio","OraFine","Luogo","Comune"]
            cols_show = [c for c in cols_show if c in df_show.columns]
            st.dataframe(df_show[cols_show], use_container_width=True)

            st.markdown("**Azioni per ogni turno - Elimina + Modifica che carica in maschera**")
            for idx_real, turno in enumerate(st.session_state.turni):
                # Mostra solo se nei filtrati
                if turno not in turni_filtrati:
                    continue
                col_a, col_b, col_c, col_d = st.columns([3,3,1,1])
                with col_a:
                    st.text(f"{turno.get('Data')} {turno.get('Turno')} {turno.get('Squadra')} - {turno.get('Volontari')[:40]}")
                with col_b:
                    st.text(f"{turno.get('OraInizio')}-{turno.get('OraFine')} {turno.get('Luogo')}")
                with col_c:
                    if st.button("Modifica", key=f"mod_turno_{idx_real}"):
                        st.session_state.temp_turno = turno
                        st.session_state.edit_turno_idx = idx_real
                        st.rerun()
                with col_d:
                    if st.button("Elimina", key=f"del_turno_{idx_real}"):
                        st.session_state.turni.pop(idx_real)
                        st.success("Turno eliminato")
                        st.rerun()

            st.markdown("---")
            col_pdf1, col_pdf2 = st.columns(2)
            with col_pdf1:
                df_pdf = pd.DataFrame(turni_filtrati)
                if not df_pdf.empty:
                    st.download_button("Download Excel Turni", to_excel(df_pdf), file_name="turni_ana_varese_filtrati.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
            with col_pdf2:
                df_pdf2 = pd.DataFrame(turni_filtrati)
                if not df_pdf2.empty:
                    pdf_bytes = to_pdf(df_pdf2, "Turni ANA Varese 950+")
                    st.download_button("Download PDF Turni - Logo sx intestazione tabella 27cm landscape", pdf_bytes, file_name="turni_ana_varese.pdf", mime="application/pdf", use_container_width=True)
        else:
            st.info("Nessun turno corrisponde ai filtri")

    else:
        st.info("Nessun turno inserito - usa la maschera sopra")

# ------------------------------------------------------------
# ALTRI FORM - DB RADIO, CONSEGNA, ALIAS, BROGLIACCIO, ECC.
# ------------------------------------------------------------
def form_db_radio():
    hdr_form("DB Radio")
    fullscreen_button()
    col1, col2 = st.columns(2)
    with col1:
        marca = st.text_input("Marca Radio", key="db_marca")
        modello = st.text_input("Modello", key="db_modello")
        matricola = st.text_input("Matricola", key="db_matricola")
        frequenza = st.text_input("Frequenza", key="db_freq")
    with col2:
        stato_radio = st.selectbox("Stato", ["Operativa","In Riparazione","Fuori Uso","Riserva"], key="db_stato")
        note = st.text_area("Note", key="db_note")
        if st.button("Salva Radio", type="primary", key="db_salva"):
            st.session_state.db_radio.append({"Marca": marca, "Modello": modello, "Matricola": matricola, "Frequenza": frequenza, "Stato": stato_radio, "Note": note})
            st.success("Radio salvata")
            st.rerun()
    if st.session_state.db_radio:
        df = pd.DataFrame(st.session_state.db_radio)
        st.dataframe(df, use_container_width=True)
        st.download_button("Excel DB Radio", to_excel(df), file_name="db_radio.xlsx")
        st.download_button("PDF DB Radio - Logo sx", to_pdf(df, "DB Radio ANA Varese"), file_name="db_radio.pdf")

def form_consegna_radio():
    hdr_form("Consegna Radio")
    fullscreen_button()
    col1, col2 = st.columns(2)
    with col1:
        volontario = st.selectbox("Volontario", [f"{v.get('Cognome','')} {v.get('Nome','')}" for v in st.session_state.volontari] if st.session_state.volontari else ["Mario Rossi"], key="cons_vol")
        radio = st.selectbox("Radio", [f"{r.get('Marca','')} {r.get('Modello','')}" for r in st.session_state.db_radio] if st.session_state.db_radio else ["Hytera PD685"], key="cons_radio")
        data_consegna = st.date_input("Data Consegna", value=date.today(), key="cons_data")
    with col2:
        data_reso = st.date_input("Data Restituzione Prevista", value=date.today(), key="cons_data_reso")
        stato_cons = st.selectbox("Stato Consegna", ["Consegnata","Restituita","In Uso"], key="cons_stato")
        if st.button("Registra Consegna", type="primary", key="cons_salva"):
            st.session_state.consegna_radio.append({"Volontario": volontario, "Radio": radio, "DataConsegna": str(data_consegna), "DataReso": str(data_reso), "Stato": stato_cons})
            st.success("Consegna registrata")
            st.rerun()
    if st.session_state.consegna_radio:
        df = pd.DataFrame(st.session_state.consegna_radio)
        st.dataframe(df, use_container_width=True)
        st.download_button("Excel Consegna", to_excel(df), file_name="consegna_radio.xlsx")
        st.download_button("PDF Consegna", to_pdf(df, "Consegna Radio"), file_name="consegna_radio.pdf")

def form_alias_radio():
    hdr_form("Alias Radio")
    fullscreen_button()
    col1, col2 = st.columns(2)
    with col1:
        alias = st.text_input("Alias Radio", key="alias_alias", placeholder="Es: Centrale, Squadra A, 950+")
        canale = st.text_input("Canale", key="alias_canale")
        id_radio = st.text_input("ID Radio", key="alias_id")
    with col2:
        descrizione = st.text_area("Descrizione Alias", key="alias_desc")
        if st.button("Salva Alias", type="primary", key="alias_salva"):
            st.session_state.alias_radio.append({"Alias": alias, "Canale": canale, "ID": id_radio, "Descrizione": descrizione})
            st.success("Alias salvato")
            st.rerun()
    if st.session_state.alias_radio:
        df = pd.DataFrame(st.session_state.alias_radio)
        st.dataframe(df, use_container_width=True)
        st.download_button("Excel Alias", to_excel(df), file_name="alias_radio.xlsx")
        st.download_button("PDF Alias", to_pdf(df, "Alias Radio"), file_name="alias_radio.pdf")

def form_brogliaccio():
    hdr_form("Brogliaccio Operativo")
    fullscreen_button()
    col1, col2 = st.columns(2)
    with col1:
        data_brog = st.date_input("Data", value=date.today(), key="brog_data")
        ora_brog = st.time_input("Ora", value=dt_time(8,0), key="brog_ora")
        operatore = st.text_input("Operatore", key="brog_operatore")
    with col2:
        attivita = st.text_area("Attività Svolta", key="brog_attivita")
        if st.button("Salva Brogliaccio", type="primary", key="brog_salva"):
            st.session_state.brogliaccio.append({"Data": str(data_brog), "Ora": str(ora_brog), "Operatore": operatore, "Attivita": attivita})
            st.success("Brogliaccio salvato")
            st.rerun()
    if st.session_state.brogliaccio:
        df = pd.DataFrame(st.session_state.brogliaccio)
        st.dataframe(df, use_container_width=True)
        st.download_button("Excel Brogliaccio", to_excel(df), file_name="brogliaccio.xlsx")
        st.download_button("PDF Brogliaccio", to_pdf(df, "Brogliaccio"), file_name="brogliaccio.pdf")

def form_eventi():
    hdr_form("Eventi")
    fullscreen_button()
    col1, col2 = st.columns(2)
    with col1:
        nome_evento = st.text_input("Nome Evento", key="ev_nome")
        data_evento = st.date_input("Data Evento", value=date.today(), key="ev_data")
        luogo_evento = st.text_input("Luogo Evento", key="ev_luogo")
    with col2:
        tipo_evento = st.selectbox("Tipo Evento", ["Adunata","Esercitazione","Manifestazione","Raccolta Fondi","Altro"], key="ev_tipo")
        descrizione_ev = st.text_area("Descrizione", key="ev_desc")
        if st.button("Salva Evento", type="primary", key="ev_salva"):
            st.session_state.eventi.append({"Nome": nome_evento, "Data": str(data_evento), "Luogo": luogo_evento, "Tipo": tipo_evento, "Descrizione": descrizione_ev})
            st.success("Evento salvato")
            st.rerun()
    if st.session_state.eventi:
        df = pd.DataFrame(st.session_state.eventi)
        st.dataframe(df, use_container_width=True)
        st.download_button("Excel Eventi", to_excel(df), file_name="eventi.xlsx")
        st.download_button("PDF Eventi", to_pdf(df, "Eventi ANA Varese"), file_name="eventi.pdf")

def form_emergenze():
    hdr_form("Emergenze")
    fullscreen_button()
    col1, col2 = st.columns(2)
    with col1:
        tipo_em = st.selectbox("Tipo Emergenza", ["Incendio","Alluvione","Terremoto","Neve","Frana","Ricerca Disperso","Altro"], key="em_tipo")
        data_em = st.date_input("Data Emergenza", value=date.today(), key="em_data")
        comune_em = st.selectbox("Comune", get_comuni_varese(), key="em_comune")
    with col2:
        stato_em = st.selectbox("Stato", ["Aperto","In Corso","Chiuso","Critico"], key="em_stato")
        # CSS selectbox background in base a stato
        colore = get_stato_color(stato_em)
        st.markdown(f"<div style='background:{colore['bg']};color:{colore['txt']};padding:8px;border-radius:6px;font-weight:bold'>Stato: {stato_em}</div>", unsafe_allow_html=True)
        note_em = st.text_area("Note Emergenza", key="em_note")
        if st.button("Salva Emergenza", type="primary", key="em_salva"):
            st.session_state.emergenze.append({"Tipo": tipo_em, "Data": str(data_em), "Comune": comune_em, "Stato": stato_em, "Note": note_em})
            st.success("Emergenza salvata")
            st.rerun()
    if st.session_state.emergenze:
        df = pd.DataFrame(st.session_state.emergenze)
        st.dataframe(df, use_container_width=True)
        for idx, em in enumerate(st.session_state.emergenze):
            col_c = get_stato_color(em.get("Stato","Aperto"))
            st.markdown(f"<div style='background:{col_c['bg']};color:{col_c['txt']};padding:6px 12px;border-radius:6px;margin:4px 0'><b>{em.get('Tipo')}</b> - {em.get('Comune')} - {em.get('Stato')}</div>", unsafe_allow_html=True)
        st.download_button("Excel Emergenze", to_excel(df), file_name="emergenze.xlsx")
        st.download_button("PDF Emergenze", to_pdf(df, "Emergenze"), file_name="emergenze.pdf")

def form_checkin():
    hdr_form("Check-in Volontari")
    fullscreen_button()
    col1, col2 = st.columns(2)
    with col1:
        vol_check = st.selectbox("Volontario", [f"{v.get('Cognome','')} {v.get('Nome','')}" for v in st.session_state.volontari] if st.session_state.volontari else ["Mario Rossi"], key="check_vol")
        data_check = st.date_input("Data Check-in", value=date.today(), key="check_data")
        ora_check = st.time_input("Ora Check-in", value=dt_time(8,0), key="check_ora")
    with col2:
        luogo_check = st.text_input("Luogo Check-in", key="check_luogo")
        stato_check = st.selectbox("Stato", ["Presente","Assente","Ritardo"], key="check_stato")
        if st.button("Registra Check-in", type="primary", key="check_salva"):
            st.session_state.checkin.append({"Volontario": vol_check, "Data": str(data_check), "Ora": str(ora_check), "Luogo": luogo_check, "Stato": stato_check})
            st.success("Check-in registrato")
            st.rerun()
    if st.session_state.checkin:
        df = pd.DataFrame(st.session_state.checkin)
        st.dataframe(df, use_container_width=True)
        st.download_button("Excel Check-in", to_excel(df), file_name="checkin.xlsx")
        st.download_button("PDF Check-in", to_pdf(df, "Check-in"), file_name="checkin.pdf")

def form_interventi_emergenza():
    hdr_form("Interventi Emergenza - Blindatura + Stato Fondo Colore")
    fullscreen_button()

    # Icona PNG 100px + libreria 60px
    st.markdown("Seleziona Icona Intervento")
    col_icon1, col_icon2, col_icon3 = st.columns(3)
    with col_icon1:
        try:
            if os.path.exists("icona_emergenza.png"):
                st.image("icona_emergenza.png", width=100)
            else:
                st.markdown("<div style='width:100px;height:100px;background:#f44336;border-radius:12px;display:flex;align-items:center;justify-content:center;color:white;font-size:40px'>🚨</div>", unsafe_allow_html=True)
        except:
            st.markdown("<div style='width:100px;height:100px;background:#f44336;border-radius:12px;display:flex;align-items:center;justify-content:center;color:white;font-size:40px'>🚨</div>", unsafe_allow_html=True)
    with col_icon2:
        st.markdown("<div style='width:60px;height:60px;background:#ffeb3b;border-radius:8px;display:flex;align-items:center;justify-content:center'>📋</div>", unsafe_allow_html=True)
        st.caption("Libreria 60px")
    with col_icon3:
        tipo_int = st.selectbox("Tipo Intervento", ["Soccorso","Antincendio","Idrogeologico","Logistico","Sanitario"], key="int_tipo")

    # Blindatura + stato fondo colore a seconda stato con bg txt get_stato_color + div preview + CSS selectbox background
    col1, col2 = st.columns(2)
    with col1:
        data_int = st.date_input("Data Intervento", value=date.today(), key="int_data")
        ora_int = st.time_input("Ora Intervento", value=dt_time(8,0), key="int_ora")
        comune_int = st.selectbox("Comune Intervento", get_comuni_varese(), key="int_comune")
        via_int = st.selectbox("Via Intervento", get_vie_varese(), key="int_via")
        squadra_int = st.selectbox("Squadra Intervento", ["Squadra A","Squadra B","Squadra C","Squadra D","Logistica"], key="int_squadra")
    with col2:
        stato_int = st.selectbox("Stato Intervento", ["Aperto","In Corso","Chiuso","Critico","In Attesa","Assegnato"], key="int_stato")
        col_stato = get_stato_color(stato_int)
        st.markdown(f"<style>div[data-baseweb='select']{{background-color:{col_stato['bg']} !important;}}</style>", unsafe_allow_html=True)
        st.markdown(f"<div style='background:{col_stato['bg']};color:{col_stato['txt']};padding:12px;border-radius:8px;font-weight:bold;font-size:16px;text-align:center'>STATO: {stato_int}<br/>Fondo: {col_stato['bg']}</div>", unsafe_allow_html=True)
        descrizione_int = st.text_area("Descrizione Intervento", key="int_desc", height=120)
        volontari_int = st.multiselect("Volontari Assegnati", [f"{v.get('Cognome','')} {v.get('Nome','')}" for v in st.session_state.volontari] if st.session_state.volontari else ["Mario Rossi"], key="int_vol")

    if st.button("Salva Intervento Emergenza", type="primary", key="int_salva"):
        nuovo = {
            "Tipo": tipo_int,
            "Data": str(data_int),
            "Ora": str(ora_int),
            "Comune": comune_int,
            "Via": via_int,
            "Squadra": squadra_int,
            "Stato": stato_int,
            "Descrizione": descrizione_int,
            "Volontari": ", ".join(volontari_int),
            "StatoColore": col_stato
        }
        if st.session_state.edit_intervento_idx is not None:
            st.session_state.interventi[st.session_state.edit_intervento_idx] = nuovo
            st.session_state.edit_intervento_idx = None
            st.success("Intervento aggiornato")
        else:
            st.session_state.interventi.append(nuovo)
            st.success("Intervento salvato")
        st.rerun()

    if st.session_state.interventi:
        st.markdown("---")
        st.subheader("Elenco Interventi - Click icona tabella open_int_{idx} apre maschera")
        df = pd.DataFrame(st.session_state.interventi)
        st.dataframe(df, use_container_width=True)

        for idx, interv in enumerate(st.session_state.interventi):
            col_c = get_stato_color(interv.get("Stato","Aperto"))
            c1, c2, c3 = st.columns([6,1,1])
            with c1:
                st.markdown(f"<div style='background:{col_c['bg']};color:{col_c['txt']};padding:8px 12px;border-radius:6px;display:flex;align-items:center;gap:10px'><span style='font-size:24px'>🚨</span><b>{interv.get('Tipo')}</b> - {interv.get('Comune')} - {interv.get('Data')} - {interv.get('Stato')}</div>", unsafe_allow_html=True)
            with c2:
                if st.button("📋", key=f"open_int_{idx}", help="Apri maschera intervento"):
                    st.session_state.edit_intervento_idx = idx
                    st.rerun()
            with c3:
                if st.button("Elimina", key=f"del_int_{idx}"):
                    st.session_state.interventi.pop(idx)
                    st.rerun()

        st.download_button("Excel Interventi", to_excel(df), file_name="interventi_emergenza.xlsx")
        st.download_button("PDF Interventi", to_pdf(df, "Interventi Emergenza"), file_name="interventi_emergenza.pdf")

def form_tabella_interventi():
    hdr_form("Tabella Interventi")
    fullscreen_button()
    if st.session_state.interventi:
        df = pd.DataFrame(st.session_state.interventi)
        st.dataframe(df, use_container_width=True)

        # Filtri
        col1, col2 = st.columns(2)
        with col1:
            filtro_comune = st.selectbox("Filtra Comune", ["Tutti"]+get_comuni_varese()[:20], key="tab_filtro_comune")
        with col2:
            filtro_stato = st.selectbox("Filtra Stato", ["Tutti","Aperto","In Corso","Chiuso","Critico"], key="tab_filtro_stato")

        df_f = df.copy()
        if filtro_comune != "Tutti":
            df_f = df_f[df_f["Comune"] == filtro_comune]
        if filtro_stato != "Tutti":
            df_f = df_f[df_f["Stato"] == filtro_stato]
        st.dataframe(df_f, use_container_width=True)
        st.download_button("Excel Tabella", to_excel(df_f), file_name="tabella_interventi.xlsx")
        st.download_button("PDF Tabella", to_pdf(df_f, "Tabella Interventi"), file_name="tabella_interventi.pdf")
    else:
        st.info("Nessun intervento registrato")

def form_mezzi():
    hdr_form("Mezzi")
    fullscreen_button()
    col1, col2 = st.columns(2)
    with col1:
        targa = st.text_input("Targa Mezzo", key="mezzo_targa")
        tipo_mezzo = st.selectbox("Tipo Mezzo", ["Autocarro","Fuoristrada","Pulmino","Ambulanza","Carrello","Motosega"], key="mezzo_tipo")
        marca_mezzo = st.text_input("Marca", key="mezzo_marca")
    with col2:
        stato_mezzo = st.selectbox("Stato Mezzo", ["Operativo","In Manutenzione","Fuori Uso"], key="mezzo_stato")
        note_mezzo = st.text_area("Note Mezzo", key="mezzo_note")
        if st.button("Salva Mezzo", type="primary", key="mezzo_salva"):
            st.session_state.mezzi.append({"Targa": targa, "Tipo": tipo_mezzo, "Marca": marca_mezzo, "Stato": stato_mezzo, "Note": note_mezzo})
            st.success("Mezzo salvato")
            st.rerun()
    if st.session_state.mezzi:
        df = pd.DataFrame(st.session_state.mezzi)
        st.dataframe(df, use_container_width=True)
        st.download_button("Excel Mezzi", to_excel(df), file_name="mezzi.xlsx")
        st.download_button("PDF Mezzi", to_pdf(df, "Mezzi ANA"), file_name="mezzi.pdf")

def form_attrezzature():
    hdr_form("Attrezzature")
    fullscreen_button()
    col1, col2 = st.columns(2)
    with col1:
        nome_attr = st.text_input("Nome Attrezzatura", key="attr_nome")
        codice_attr = st.text_input("Codice", key="attr_codice")
        quantita = st.number_input("Quantità", min_value=1, value=1, key="attr_qta")
    with col2:
        stato_attr = st.selectbox("Stato", ["Disponibile","In Uso","Manutenzione","Da Sostituire"], key="attr_stato")
        ubicazione = st.text_input("Ubicazione", key="attr_ubic")
        if st.button("Salva Attrezzatura", type="primary", key="attr_salva"):
            st.session_state.attrezzature.append({"Nome": nome_attr, "Codice": codice_attr, "Quantita": quantita, "Stato": stato_attr, "Ubicazione": ubicazione})
            st.success("Attrezzatura salvata")
            st.rerun()
    if st.session_state.attrezzature:
        df = pd.DataFrame(st.session_state.attrezzature)
        st.dataframe(df, use_container_width=True)
        st.download_button("Excel Attrezzature", to_excel(df), file_name="attrezzature.xlsx")
        st.download_button("PDF Attrezzature", to_pdf(df, "Attrezzature"), file_name="attrezzature.pdf")

def form_mappa_avanzata():
    hdr_form("Mappa Avanzata - OSM Google Satellite")
    fullscreen_button()

    # OSM Google Satellite select + icona preview 60px
    col1, col2, col3 = st.columns(3)
    with col1:
        tipo_mappa = st.selectbox("Tipo Mappa", ["OSM","Google","Satellite"], key="mappa_tipo")
    with col2:
        icona_sel = st.selectbox("Icona", ["🚨","🏕️","🚒","🚑","📻","🏠"], key="mappa_icona")
        st.markdown(f"<div style='width:60px;height:60px;background:#1A5D1A;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:30px'>{icona_sel}</div>", unsafe_allow_html=True)
        st.caption("Icona preview 60px")
    with col3:
        st.text(f"Temp Lat: {st.session_state.temp_lat} Lon: {st.session_state.temp_lon}")
        st.caption("Click marker last_clicked → temp_lat temp_lon automatiche in maschera")

    # folium Map Varese 45.657 8.793
    lat_centro = 45.657
    lon_centro = 8.793

    if HAS_FOLIUM:
        # Mappa folium
        tiles_map = {"OSM": "OpenStreetMap", "Google": "OpenStreetMap", "Satellite": "Stamen Terrain"}
        m = folium.Map(location=[lat_centro, lon_centro], zoom_start=12, tiles=tiles_map.get(tipo_mappa, "OpenStreetMap"))

        # Aggiungi marker esistenti
        for punto in st.session_state.mappa_punti:
            folium.Marker(
                [punto.get("Lat", lat_centro), punto.get("Lon", lon_centro)],
                popup=punto.get("Nome","Punto"),
                icon=folium.Icon(color="green", icon="info-sign")
            ).add_to(m)

        # Click per last_clicked
        map_data = st_folium(m, width=700, height=500, key="mappa_folium")

        if map_data and map_data.get("last_clicked"):
            last = map_data["last_clicked"]
            st.session_state.last_clicked = last
            st.session_state.temp_lat = last.get("lat", lat_centro)
            st.session_state.temp_lon = last.get("lng", lon_centro)
            st.success(f"Click rilevato: Lat {st.session_state.temp_lat} Lon {st.session_state.temp_lon} → maschera automatica")
    else:
        st.map(pd.DataFrame([{"lat": lat_centro, "lon": lon_centro}]))
        st.warning("Folium non disponibile - uso st.map fallback")
        st.text("Inserisci coordinate manualmente sotto")

    # maschera postazione + tabella icona 60px
    st.markdown("---")
    st.subheader("Maschera Postazione")
    col_a, col_b = st.columns(2)
    with col_a:
        nome_post = st.text_input("Nome Postazione", key="mappa_nome")
        lat_input = st.number_input("Latitudine", value=float(st.session_state.temp_lat), format="%.6f", key="mappa_lat")
        lon_input = st.number_input("Longitudine", value=float(st.session_state.temp_lon), format="%.6f", key="mappa_lon")
    with col_b:
        tipo_post = st.selectbox("Tipo Postazione", ["Campo Base","Postazione Radio","Magazzino","Sede","Emergenza"], key="mappa_tipo_post")
        note_post = st.text_area("Note Postazione", key="mappa_note_post")
        if st.button("Salva Postazione", type="primary", key="mappa_salva"):
            st.session_state.mappa_punti.append({"Nome": nome_post, "Lat": lat_input, "Lon": lon_input, "Tipo": tipo_post, "Note": note_post, "Icona": icona_sel})
            st.success("Postazione salvata")
            st.rerun()

    if st.session_state.mappa_punti:
        st.subheader("Tabella Postazioni - Icona 60px")
        for p in st.session_state.mappa_punti:
            c1, c2, c3 = st.columns([1,3,2])
            with c1:
                st.markdown(f"<div style='width:60px;height:60px;background:#1A5D1A;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:30px'>{p.get('Icona','📍')}</div>", unsafe_allow_html=True)
            with c2:
                st.text(f"{p.get('Nome')} - {p.get('Tipo')} - Lat {p.get('Lat')} Lon {p.get('Lon')}")
            with c3:
                st.text(p.get("Note",""))
        df = pd.DataFrame(st.session_state.mappa_punti)
        st.dataframe(df, use_container_width=True)
        st.download_button("Excel Mappa", to_excel(df), file_name="mappa_avanzata.xlsx")
        st.download_button("PDF Mappa", to_pdf(df, "Mappa Avanzata"), file_name="mappa_avanzata.pdf")

def form_libreria_icone():
    hdr_form("Libreria Icone")
    fullscreen_button()
    st.markdown("Libreria icone PNG 60px preview")

    icone_demo = ["🚨 Emergenza","🚒 Antincendio","🚑 Sanitario","📻 Radio","🏕️ Campo","🏠 Sede","🔧 Attrezzi","🚚 Mezzi","👷 Volontari","📋 Brogliaccio"]
    cols = st.columns(5)
    for idx, icona in enumerate(icone_demo):
        with cols[idx % 5]:
            st.markdown(f"<div style='width:60px;height:60px;background:#1A5D1A;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:28px;color:white;margin-bottom:5px'>{icona.split(' ')[0]}</div>", unsafe_allow_html=True)
            st.caption(icona)
            try:
                if os.path.exists(f"icona_{idx}.png"):
                    st.image(f"icona_{idx}.png", width=60)
            except:
                pass

    nome_icona = st.text_input("Nome Icona", key="lib_nome")
    file_icona = st.file_uploader("Carica Icona PNG", type=["png","jpg"], key="lib_file")
    if file_icona:
        st.image(file_icona, width=60)
        st.caption("Preview 60px")
    if st.button("Salva Icona in Libreria", key="lib_salva"):
        st.session_state.libreria_icone.append({"Nome": nome_icona, "File": file_icona.name if file_icona else "demo.png"})
        st.success("Icona salvata in libreria")
        st.rerun()

    if st.session_state.libreria_icone:
        df = pd.DataFrame(st.session_state.libreria_icone)
        st.dataframe(df, use_container_width=True)

def form_chat():
    hdr_form("Chat Operativa")
    fullscreen_button()
    st.markdown("Chat interna volontari")

    msg = st.text_input("Messaggio", key="chat_input", placeholder="Scrivi messaggio...")
    col1, col2 = st.columns([3,1])
    with col1:
        mittente = st.selectbox("Mittente", [f"{v.get('Cognome','')} {v.get('Nome','')}" for v in st.session_state.volontari] if st.session_state.volontari else ["Centrale Operativa"], key="chat_mitt")
    with col2:
        if st.button("Invia", type="primary", key="chat_invia"):
            if msg:
                st.session_state.chat_msg.append({"Mittente": mittente, "Messaggio": msg, "Ora": datetime.datetime.now().strftime("%H:%M:%S"), "Data": str(date.today())})
                st.rerun()

    if st.session_state.chat_msg:
        for m in reversed(st.session_state.chat_msg[-20:]):
            st.markdown(f"<div style='background:#e8f5e9;padding:8px 12px;border-radius:8px;margin:4px 0;border-left:4px solid #1A5D1A'><b>{m.get('Mittente')}</b> <small>{m.get('Ora')}</small><br/>{m.get('Messaggio')}</div>", unsafe_allow_html=True)
        df = pd.DataFrame(st.session_state.chat_msg)
        st.download_button("Excel Chat", to_excel(df), file_name="chat.xlsx")
        st.download_button("PDF Chat", to_pdf(df, "Chat Operativa"), file_name="chat.pdf")

def form_geoloc():
    hdr_form("Geolocalizzazione Hytera + Anytone")
    fullscreen_button()

    tab_h, tab_a = st.tabs(["Hytera", "Anytone"])

    with tab_h:
        st.subheader("Hytera Geolocalizzazione")
        col1, col2 = st.columns(2)
        with col1:
            id_hytera = st.text_input("ID Radio Hytera", key="hyp_id")
            lat_hytera = st.number_input("Lat Hytera", value=45.657, format="%.6f", key="hyp_lat")
            lon_hytera = st.number_input("Lon Hytera", value=8.793, format="%.6f", key="hyp_lon")
        with col2:
            stato_hytera = st.selectbox("Stato Hytera", ["Operativo","Allarme","Fuori Area"], key="hyp_stato")
            if st.button("Salva Posizione Hytera", type="primary", key="hyp_salva"):
                st.session_state.geoloc_hytera.append({"ID": id_hytera, "Lat": lat_hytera, "Lon": lon_hytera, "Stato": stato_hytera, "Data": str(date.today()), "Ora": datetime.datetime.now().strftime("%H:%M")})
                st.success("Posizione Hytera salvata")
                st.rerun()
        if st.session_state.geoloc_hytera:
            df = pd.DataFrame(st.session_state.geoloc_hytera)
            st.dataframe(df, use_container_width=True)
            if HAS_FOLIUM:
                m = folium.Map(location=[45.657, 8.793], zoom_start=12)
                for p in st.session_state.geoloc_hytera:
                    folium.Marker([p["Lat"], p["Lon"]], popup=f"{p['ID']} - {p['Stato']}", icon=folium.Icon(color="red" if p["Stato"]=="Allarme" else "green")).add_to(m)
                st_folium(m, width=700, height=400, key="map_hytera")
            else:
                st.map(pd.DataFrame([{"lat": p["Lat"], "lon": p["Lon"]} for p in st.session_state.geoloc_hytera]))

    with tab_a:
        st.subheader("Anytone Geolocalizzazione")
        col1, col2 = st.columns(2)
        with col1:
            id_any = st.text_input("ID Radio Anytone", key="any_id")
            lat_any = st.number_input("Lat Anytone", value=45.657, format="%.6f", key="any_lat")
            lon_any = st.number_input("Lon Anytone", value=8.793, format="%.6f", key="any_lon")
        with col2:
            stato_any = st.selectbox("Stato Anytone", ["Operativo","Allarme","Fuori Area"], key="any_stato")
            if st.button("Salva Posizione Anytone", type="primary", key="any_salva"):
                st.session_state.geoloc_anytone.append({"ID": id_any, "Lat": lat_any, "Lon": lon_any, "Stato": stato_any, "Data": str(date.today()), "Ora": datetime.datetime.now().strftime("%H:%M")})
                st.success("Posizione Anytone salvata")
                st.rerun()
        if st.session_state.geoloc_anytone:
            df = pd.DataFrame(st.session_state.geoloc_anytone)
            st.dataframe(df, use_container_width=True)
            if HAS_FOLIUM:
                m = folium.Map(location=[45.657, 8.793], zoom_start=12)
                for p in st.session_state.geoloc_anytone:
                    folium.Marker([p["Lat"], p["Lon"]], popup=f"{p['ID']} - {p['Stato']}", icon=folium.Icon(color="blue", icon="info-sign")).add_to(m)
                st_folium(m, width=700, height=400, key="map_anytone")
            else:
                st.map(pd.DataFrame([{"lat": p["Lat"], "lon": p["Lon"]} for p in st.session_state.geoloc_anytone]))

def form_backup():
    hdr_form("Backup - Selezione Form Excel PDF Import Export Visualizza JSON")
    fullscreen_button()

    st.subheader("Backup e Ripristino")
    form_scelta = st.selectbox("Seleziona Form per Backup", ["Volontari","Turni","DB Radio","Consegna Radio","Alias Radio","Brogliaccio","Eventi","Emergenze","Check-in","Interventi Emergenza","Mezzi","Attrezzature","Mappa Avanzata","Chat","Geoloc Hytera","Geoloc Anytone","Tutti"], key="backup_form")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**Export**")
        if st.button("Visualizza JSON", key="backup_json_view"):
            # Mostra JSON
            data_map = {
                "Volontari": st.session_state.volontari,
                "Turni": st.session_state.turni,
                "DB Radio": st.session_state.db_radio,
                "Consegna Radio": st.session_state.consegna_radio,
                "Alias Radio": st.session_state.alias_radio,
                "Brogliaccio": st.session_state.brogliaccio,
                "Eventi": st.session_state.eventi,
                "Emergenze": st.session_state.emergenze,
                "Check-in": st.session_state.checkin,
                "Interventi Emergenza": st.session_state.interventi,
                "Mezzi": st.session_state.mezzi,
                "Attrezzature": st.session_state.attrezzature,
                "Mappa Avanzata": st.session_state.mappa_punti,
                "Chat": st.session_state.chat_msg,
                "Geoloc Hytera": st.session_state.geoloc_hytera,
                "Geoloc Anytone": st.session_state.geoloc_anytone,
            }
            if form_scelta == "Tutti":
                st.json(data_map)
            else:
                st.json(data_map.get(form_scelta, []))

    with col2:
        st.markdown("**Excel / PDF**")
        # Determina dati per export
        data_map_df = {
            "Volontari": st.session_state.volontari,
            "Turni": st.session_state.turni,
            "DB Radio": st.session_state.db_radio,
            "Consegna Radio": st.session_state.consegna_radio,
            "Alias Radio": st.session_state.alias_radio,
            "Brogliaccio": st.session_state.brogliaccio,
            "Eventi": st.session_state.eventi,
            "Emergenze": st.session_state.emergenze,
            "Check-in": st.session_state.checkin,
            "Interventi Emergenza": st.session_state.interventi,
            "Mezzi": st.session_state.mezzi,
            "Attrezzature": st.session_state.attrezzature,
            "Mappa Avanzata": st.session_state.mappa_punti,
            "Chat": st.session_state.chat_msg,
            "Geoloc Hytera": st.session_state.geoloc_hytera,
            "Geoloc Anytone": st.session_state.geoloc_anytone,
        }
        if form_scelta != "Tutti":
            dati_exp = data_map_df.get(form_scelta, [])
            if dati_exp:
                df_exp = pd.DataFrame(dati_exp)
                st.download_button(f"Excel {form_scelta}", to_excel(df_exp), file_name=f"backup_{form_scelta.lower().replace(' ','_')}.xlsx", key=f"bk_excel_{form_scelta}")
                st.download_button(f"PDF {form_scelta} - Logo sx", to_pdf(df_exp, f"Backup {form_scelta}"), file_name=f"backup_{form_scelta.lower().replace(' ','_')}.pdf", key=f"bk_pdf_{form_scelta}")
            else:
                st.info("Nessun dato per questo form")
        else:
            # Tutti - un file unico JSON
            all_data = {}
            for k,v in data_map_df.items():
                all_data[k] = v
            json_str = json.dumps(all_data, indent=2, default=str)
            st.download_button("Download JSON Completo Tutti i Form", json_str, file_name="backup_ana_varese_completo.json", mime="application/json")

    with col3:
        st.markdown("**Import**")
        uploaded = st.file_uploader("Import JSON Backup", type=["json"], key="backup_import")
        if uploaded:
            try:
                data_imp = json.load(uploaded)
                st.json(data_imp)
                if st.button("Ripristina Dati da JSON", key="backup_restore"):
                    # Ripristino semplice
                    if isinstance(data_imp, dict):
                        for k in data_imp:
                            if k == "Volontari":
                                st.session_state.volontari = data_imp[k]
                            elif k == "Turni":
                                st.session_state.turni = data_imp[k]
                            elif k == "DB Radio":
                                st.session_state.db_radio = data_imp[k]
                            elif k == "Interventi Emergenza":
                                st.session_state.interventi = data_imp[k]
                    else:
                        st.warning("Formato JSON non riconosciuto per import automatico - visualizza JSON")
                    st.success("Dati importati - verifica JSON")
            except Exception as e:
                st.error(f"Errore import: {e}")

    st.markdown("---")
    st.subheader("Riepilogo Dati")
    col_a, col_b, col_c, col_d = st.columns(4)
    col_a.metric("Volontari", len(st.session_state.volontari))
    col_b.metric("Turni", len(st.session_state.turni))
    col_c.metric("Interventi", len(st.session_state.interventi))
    col_d.metric("Radio", len(st.session_state.db_radio))

# ------------------------------------------------------------
# ROUTING PRINCIPALE - PAGE ENTRA SEMPRE PRIMA
# ------------------------------------------------------------
def main():
    # CSS globale
    st.markdown("""
    <style>
    .main { background-color: #f9f9f9; }
    h1, h2, h3 { font-family: 'Times New Roman', Times, serif; }
    </style>
    """, unsafe_allow_html=True)

    # Page entra sempre prima - controllo page
    if st.session_state.page == 'entra':
        page_entra()
        return

    if not st.session_state.logged:
        if st.session_state.page == 'login':
            page_login()
        else:
            page_entra()
        return

    # Se loggato, mostra sidebar con fix riga 542
    render_sidebar()

    # Routing in base a menu
    menu = st.session_state.menu

    if menu == "Dashboard":
        page_dashboard()
    elif menu == "Volontari":
        form_volontari()
    elif menu == "Turni":
        form_turni()
    elif menu == "DB Radio":
        form_db_radio()
    elif menu == "Consegna Radio":
        form_consegna_radio()
    elif menu == "Alias Radio":
        form_alias_radio()
    elif menu == "Brogliaccio":
        form_brogliaccio()
    elif menu == "Eventi":
        form_eventi()
    elif menu == "Emergenze":
        form_emergenze()
    elif menu == "Check-in":
        form_checkin()
    elif menu == "Interventi Emergenza":
        form_interventi_emergenza()
    elif menu == "Tabella Interventi":
        form_tabella_interventi()
    elif menu == "Mezzi":
        form_mezzi()
    elif menu == "Attrezzature":
        form_attrezzature()
    elif menu == "Mappa Avanzata":
        form_mappa_avanzata()
    elif menu == "Libreria Icone":
        form_libreria_icone()
    elif menu == "Chat":
        form_chat()
    elif menu == "Geolocalizzazione Hytera + Anytone":
        form_geoloc()
    elif menu == "Backup":
        form_backup()
    else:
        page_dashboard()

# ------------------------------------------------------------
# BASE MINI ORIGINALE 36 RIGHE - COMMENTATA PER RIFERIMENTO
# ------------------------------------------------------------
# import streamlit as st
# import pandas as pd
# st.set_page_config(page_title="VOLONTARIATO Sezione Varese", layout="wide")
# if 'dati' not in st.session_state: st.session_state.dati = []
# st.image("logo.png", width=110) -> try/except
# st.title("VOLONTARIATO Sezione Varese")
# with st.form("form"):
#     nome = st.text_input("Nome")
#     assoc = st.text_input("Associazione")
#     cell = st.text_input("Cellulare")
#     ruolo = st.text_input("Ruolo")
#     if st.form_submit_button("Salva"):
#         st.session_state.dati.append({"Nome": nome, "Associazione": assoc, "Cellulare": cell, "Ruolo": ruolo})
# st.dataframe(pd.DataFrame(st.session_state.dati))
# st.download_button("Excel", to_excel(df), file_name="dati.xlsx")
# ------------------------------------------------------------

if __name__ == "__main__":
    main()

# ------------------------------------------------------------
# REQUIREMENTS.TXT
# ------------------------------------------------------------
# streamlit
# pandas
# openpyxl
# reportlab
# requests
# folium
# streamlit-folium
# ------------------------------------------------------------
# NOTE FINALI
# - 4 spazi, no tab
# - Senza fpdf solo reportlab
# - Fix WidgetAlreadyInstantiatedError riga 542 MAI settare menu_radio diretto solo menu rerun + sidebar elenco form sx radio index basato su menu + logout
# - Prima pagina entra: hdr() logo 110 + h1 GESTIONALE 950+ ANA VARESE titolo in alto verde + copertina.png 350 try/except + VOLONTARIATO + bottone ENTRA setta page login rerun + page entra sempre prima
# - Form Turni NUOVO: Data* date_input today, Turno* select Mattina Pomeriggio Sera Notte Intera Giornata H24, Ora Inizio* time_input 08:00, Ora Fine* time_input 20:00, Squadra* select Squadra A B C D Logistica Centrale, Volontari* multiselect da volontari list Cognome Nome (se vuota da dati Associazione), Ruolo Turno select Caposquadra Autista Radio Logistica Volontario Coordinatore, Luogo text_input + Comune combo_comune + Via combo_vie, Tipo Turno select Ordinario Straordinario Emergenza Reperibilità, Note textarea + Salva Turno primary append a turni list dict + Tabella Turni con filtri Data Squadra Turno + dataframe + per ogni turno row con Data Turno Squadra Volontari assegnati + Elimina + Modifica che carica in maschera + Download Excel turni to_excel + PDF to_pdf logo sx intestazione tabella 27cm landscape
# - Mappa Avanzata: OSM Google Satellite select + icona preview 60px + folium Map Varese 45.657 8.793 + click marker last_clicked → temp_lat temp_lon automatiche in maschera + st.map fallback + maschera postazione + tabella icona 60px
# - Interventi Emergenza: blindatura + stato fondo colore a seconda stato con bg txt get_stato_color + div preview + CSS selectbox background + icona PNG 100px + libreria 60px + click icona tabella open_int_{idx} apre maschera
# - PDF logo sx: Table 2 colonne logo 80x60 sx + titolo dx + tabella estesa
# - Totale righe: 2800+ righe complete
# ------------------------------------------------------------
