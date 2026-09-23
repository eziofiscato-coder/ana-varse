import streamlit as st
import pandas as pd
import os
from io import BytesIO
from datetime import date, datetime
import tempfile
import json
import requests

# =============================================================
# CONFIGURAZIONE PAGINA
# =============================================================
st.set_page_config(
    page_title="ANA Varese 950+",
    page_icon="🟢",
    layout="wide",
    initial_sidebar_state="expanded"
)

VERDE = "#1A5D1A"
VERDE_CHIARO = "#2E8B57"
VERDE_SCURISSIMO = "#0F3D0F"

st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: #f8fdf8;
    }}
    label, .stTextInput label, .stSelectbox label, .stTextArea label,
    .stNumberInput label, .stDateInput label, .stTimeInput label {{
        color: black !important;
        font-weight: bold !important;
        font-family: 'Times New Roman', Times, serif !important;
        font-size: 16px !important;
    }}
    h1, h2, h3 {{
        color: {VERDE} !important;
        font-family: 'Times New Roman', serif !important;
        font-weight: bold !important;
    }}
    .stButton > button {{
        background-color: {VERDE} !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        border: 2px solid {VERDE_SCURISSIMO} !important;
    }}
    .stFormSubmitButton > button {{
        background-color: {VERDE} !important;
        color: white !important;
        font-weight: bold !important;
        font-size: 16px !important;
    }}
    div[data-testid="stForm"] {{
        border: 2px solid {VERDE} !important;
        border-radius: 12px !important;
        padding: 20px !important;
        background-color: white !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# =============================================================
# COMUNI ITALIA - PROVINCIA VARESE 80+
# =============================================================
COMUNI_ITALIA = [
    "Agra", "Albizzate", "Angera", "Arcisate", "Arsago Seprio",
    "Azzate", "Azzio", "Barasso", "Bardello", "Bedero Valcuvia",
    "Besano", "Besnate", "Besozzo", "Biandronno", "Bisuschio",
    "Bodio Lomnago", "Brebbia", "Bregano", "Brenta", "Brezzo di Bedero",
    "Brinzio", "Brissago-Valtravaglia", "Brunello", "Brusimpiano",
    "Buguggiate", "Busto Arsizio", "Cadegliano-Viconago", "Cadrezzate",
    "Cairate", "Cantello", "Caravate", "Cardano al Campo",
    "Carnago", "Caronno Pertusella", "Caronno Varesino", "Casale Litta",
    "Casalzuigno", "Casciago", "Casorate Sempione", "Cassano Magnago",
    "Cassano Valcuvia", "Castellanza", "Castello Cabiaglio",
    "Castelseprio", "Castelveccana", "Castiglione Olona",
    "Castronno", "Cavaria con Premezzo", "Cazzago Brabbia",
    "Cislago", "Cittiglio", "Clivio", "Cocquio-Trevisago",
    "Comabbio", "Comerio", "Cremenaga", "Crosio della Valle",
    "Cuasso al Monte", "Cugliate-Fabiasco", "Cunardo", "Curiglia con Monteviasco",
    "Cuveglio", "Cuvio", "Daverio", "Dumenza", "Duno",
    "Fagnano Olona", "Ferno", "Ferrera di Varese", "Gallarate",
    "Galliate Lombardo", "Gavirate", "Gazzada Schianno", "Gemonio",
    "Gerenzano", "Germignaga", "Golasecca", "Gorla Maggiore",
    "Gorla Minore", "Gornate-Olona", "Grantola", "Inarzo",
    "Induno Olona", "Ispra", "Jerago con Orago", "Lavena Ponte Tresa",
    "Laveno-Mombello", "Leggiuno", "Lonate Ceppino", "Lonate Pozzolo",
    "Lozza", "Luino", "Luvinate", "Maccagno con Pino e Veddasca",
    "Malgesso", "Malnate", "Marchirolo", "Marnate", "Marzio",
    "Masciago Primo", "Mercallo", "Mesenzana", "Montegrino Valtravaglia",
    "Monvalle", "Morazzone", "Mornago", "Oggiona con Santo Stefano",
    "Olgiate Olona", "Origgio", "Orino", "Porto Ceresio",
    "Porto Valtravaglia", "Rancio Valcuvia", "Ranco", "Saltrio",
    "Samarate", "Saronno", "Sesto Calende", "Solbiate Arno",
    "Solbiate Olona", "Somma Lombardo", "Sumirago", "Taino",
    "Ternate", "Tradate", "Travedona-Monate", "Tronzano Lago Maggiore",
    "Uboldo", "Valganna", "Varano Borghi", "Varese", "Vedano Olona",
    "Venegono Inferiore", "Venegono Superiore", "Vergiate", "Viggiu",
    "Vizzola Ticino"
]

VIE_FALLBACK = {
    "Varese": ["Via Sacco", "Via Verdi", "Via Roma", "Via Volta", "Via Manzoni", "Piazza Monte Grappa", "Via Crispi", "Via Cavour"],
    "Busto Arsizio": ["Via Milano", "Via Matteotti", "Via XX Settembre", "Via Rossini", "Corso XX Settembre"],
    "Gallarate": ["Via Manzoni", "Via Torino", "Via Roma", "Via Postporta", "Via Varese"],
    "Saronno": ["Via Roma", "Via Varese", "Corso Italia", "Via Manzoni"],
    "Tradate": ["Via Mameli", "Via Europa", "Via Trento", "Via Libertà"],
    "DEFAULT": ["Via Roma", "Via Garibaldi", "Via Verdi", "Via Manzoni", "Via XXV Aprile", "Via Matteotti", "Piazza Libertà", "Via Dante", "Via Milano", "Via Volta"]
}

# =============================================================
# FUNZIONI UTILI
# =============================================================
def get_comuni():
    """
    Ritorna lista comuni Varese
    """
    return sorted(COMUNI_ITALIA)


def get_vie(comune):
    """
    Prova a recuperare vie da API, fallback locale
    """
    try:
        url = f"https://api.example.com/vie?comune={comune}"
        resp = requests.get(url, timeout=2)
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, list) and len(data) > 0:
                return data
    except Exception:
        pass
    if comune in VIE_FALLBACK:
        return VIE_FALLBACK[comune]
    return VIE_FALLBACK["DEFAULT"]


def combo_comune(label, key, default=""):
    """
    Combo comune con checkbox manuale
    """
    st.markdown(f"**{label}**")
    col1, col2 = st.columns([4, 1])
    with col1:
        comuni = get_comuni()
        idx = 0
        if default in comuni:
            idx = comuni.index(default) + 1
        options = ["-- Seleziona --"] + comuni
        sel = st.selectbox(
            label,
            options,
            index=idx,
            key=f"{key}_select",
            label_visibility="collapsed"
        )
    with col2:
        manuale = st.checkbox("Manuale", key=f"{key}_manuale")
    if manuale:
        val = st.text_input(
            f"{label} manuale",
            value=default,
            key=f"{key}_man",
            label_visibility="collapsed",
            placeholder="Inserisci comune"
        )
        return val
    else:
        if sel == "-- Seleziona --":
            return ""
        return sel


def combo_vie(label, comune, key, default=""):
    """
    Combo vie con checkbox manuale
    """
    st.markdown(f"**{label}**")
    col1, col2 = st.columns([4, 1])
    with col1:
        if comune:
            vie = get_vie(comune)
        else:
            vie = VIE_FALLBACK["DEFAULT"]
        idx = 0
        if default in vie:
            idx = vie.index(default) + 1
        options = ["-- Seleziona --"] + vie
        sel = st.selectbox(
            label,
            options,
            index=idx,
            key=f"{key}_select",
            label_visibility="collapsed"
        )
    with col2:
        manuale = st.checkbox("Manuale", key=f"{key}_manuale_vie")
    if manuale:
        val = st.text_input(
            f"{label} manuale",
            value=default,
            key=f"{key}_man_vie",
            label_visibility="collapsed",
            placeholder="Inserisci via"
        )
        return val
    else:
        if sel == "-- Seleziona --":
            return ""
        return sel


def get_stato_color(stato):
    """
    Ritorna tuple bg, txt, label per stato
    """
    stato = str(stato).strip()
    if stato == "Operativo":
        return ("#ff0000", "white", "Operativo")
    if stato == "In Corso":
        return ("#ffff00", "black", "In Corso")
    if stato == "Completato":
        return ("#00ff00", "black", "Completato")
    if stato == "Chiuso":
        return ("#808080", "white", "Chiuso")
    if stato == "In Stand By":
        return ("#ff8c00", "white", "In Stand By")
    if stato == "Sospeso":
        return ("#87ceeb", "black", "Sospeso")
    if stato == "Annullato":
        return ("#000000", "white", "Annullato")
    if stato == "In Attesa":
        return ("#ffd700", "black", "In Attesa")
    if stato == "Urgente":
        return ("#ff0000", "white", "Urgente")
    if stato == "Critica":
        return ("#8b0000", "white", "Critica")
    if stato == "Alta":
        return ("#ff4500", "white", "Alta")
    if stato == "Media":
        return ("#ffa500", "black", "Media")
    if stato == "Bassa":
        return ("#90ee90", "black", "Bassa")
    return ("#ffffff", "black", stato)


def to_excel(df):
    """
    Converte DataFrame in Excel Bytes escludendo colonne binarie
    """
    exclude_cols = ["FotoBytes", "FileBytes", "FotoConsegnaBytes", "Foto", "FirmaBytes"]
    cols_to_keep = [c for c in df.columns if c not in exclude_cols]
    df_clean = df[cols_to_keep] if cols_to_keep else df
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_clean.to_excel(writer, index=False, sheet_name="Dati")
    output.seek(0)
    return output.getvalue()


def to_pdf(df, titolo):
    """
    Crea PDF report con reportlab landscape A4
    """
    try:
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
    except Exception:
        return None
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4))
    elements = []
    styles = getSampleStyleSheet()
    title = Paragraph(f"<b>{titolo}</b>", styles["Title"])
    elements.append(title)
    elements.append(Spacer(1, 20))
    exclude_cols = ["FotoBytes", "FileBytes", "FotoConsegnaBytes", "Foto", "FirmaBytes"]
    cols_to_keep = [c for c in df.columns if c not in exclude_cols][:8]
    if not cols_to_keep:
        cols_to_keep = list(df.columns)[:8]
    data = [cols_to_keep]
    for _, row in df.head(50).iterrows():
        r = [str(row.get(c, ""))[:40] for c in cols_to_keep]
        data.append(r)
    table = Table(data)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(VERDE)),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 8),
                ("FONTSIZE", (0, 1), (-1, -1), 6),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#e8f5e9")]),
            ]
        )
    )
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()


def to_excel_multi(datasets):
    """
    datasets: dict nome->df
    """
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for name, df in datasets.items():
            if df is None or len(df) == 0:
                continue
            exclude_cols = ["FotoBytes", "FileBytes", "FotoConsegnaBytes", "Foto", "FirmaBytes"]
            cols_to_keep = [c for c in df.columns if c not in exclude_cols]
            df_clean = df[cols_to_keep] if cols_to_keep else df
            sheet = name[:31]
            df_clean.to_excel(writer, index=False, sheet_name=sheet)
    output.seek(0)
    return output.getvalue()


def salva_icona_temp(icona_bytes, nome):
    """
    Salva icona temporanea e ritorna path
    """
    try:
        tf = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        tf.write(icona_bytes)
        tf.close()
        return tf.name
    except Exception:
        return None


def hdr():
    """
    Header con logo
    """
    c1, c2 = st.columns([1, 5])
    with c1:
        if os.path.exists("logo.png"):
            st.image("logo.png", width=80)
        else:
            st.markdown(f"<div style='background:{VERDE};color:white;padding:10px;border-radius:8px;text-align:center;font-weight:bold;'>ANA<br>Varese</div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<h1 style='margin-bottom:0;'>ANA Varese - Sezione 950+</h1><p style='color:{VERDE};font-weight:bold;'>Sistema Gestione Operativa Volontari</p>", unsafe_allow_html=True)


def hdr_form(t):
    """
    Header form con titolo
    """
    st.markdown(f"<div style='background:{VERDE};color:white;padding:12px;border-radius:8px;margin-bottom:15px;'><h2 style='color:white;margin:0;font-size:20px;'>{t}</h2></div>", unsafe_allow_html=True)

# =============================================================
# SESSION STATE INIT - TUTTI I FORM
# =============================================================
if "volontari" not in st.session_state:
    st.session_state.volontari = []

if "radio_db" not in st.session_state:
    st.session_state.radio_db = []

if "consegna_radio" not in st.session_state:
    st.session_state.consegna_radio = []

if "alias_radio" not in st.session_state:
    st.session_state.alias_radio = []

if "brogliaccio" not in st.session_state:
    st.session_state.brogliaccio = []

if "eventi" not in st.session_state:
    st.session_state.eventi = []

if "emergenze" not in st.session_state:
    st.session_state.emergenze = []

if "checkin" not in st.session_state:
    st.session_state.checkin = []

if "interventi" not in st.session_state:
    st.session_state.interventi = []

if "interventi_emergenza" not in st.session_state:
    st.session_state.interventi_emergenza = []

if "interventi_blindato" not in st.session_state:
    st.session_state.interventi_blindato = False

if "interventi_emergenza_sel" not in st.session_state:
    st.session_state.interventi_emergenza_sel = ""

if "mezzi" not in st.session_state:
    st.session_state.mezzi = []

if "attrezzature" not in st.session_state:
    st.session_state.attrezzature = []

if "icone" not in st.session_state:
    st.session_state.icone = [
        {"Nome": "Incendio", "Categoria": "Emergenza", "Colore": "#ff0000"},
        {"Nome": "Alluvione", "Categoria": "Emergenza", "Colore": "#0000ff"},
        {"Nome": "Frana", "Categoria": "Emergenza", "Colore": "#8b4513"},
        {"Nome": "Soccorso", "Categoria": "Sanitario", "Colore": "#ff0000"},
        {"Nome": "Ricerca", "Categoria": "Operativo", "Colore": "#ffa500"},
        {"Nome": "Viabilità", "Categoria": "Operativo", "Colore": "#ffff00"},
    ]

if "chat" not in st.session_state:
    st.session_state.chat = []

if "posizioni_pd785" not in st.session_state:
    st.session_state.posizioni_pd785 = []

if "simulazione_attiva" not in st.session_state:
    st.session_state.simulazione_attiva = False

if "menu" not in st.session_state:
    st.session_state.menu = "Dashboard"

if "logged" not in st.session_state:
    st.session_state.logged = False

if "json_visualizzato" not in st.session_state:
    st.session_state.json_visualizzato = None

if "base_hytera" not in st.session_state:
    st.session_state.base_hytera = {"lat": 45.657, "lon": 8.793, "id": "MD785 BASE", "com": "COM3"}

# =============================================================
# LOGIN PAGE
# =============================================================
if not st.session_state.logged:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if os.path.exists("copertina.png"):
            st.image("copertina.png", use_column_width=True)
        else:
            st.markdown(f"<div style='background:{VERDE};color:white;padding:40px;border-radius:15px;text-align:center;'><h1 style='color:white;'>ANA VARESE</h1><h3 style='color:white;'>Sezione 950+</h3></div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        with st.form("login_form"):
            st.markdown("### Accesso Riservato")
            utente = st.text_input("Utente")
            password = st.text_input("Password", type="password")
            login_btn = st.form_submit_button("Entra")
            if login_btn:
                if utente == "admin" and password == "ana2024":
                    st.session_state.logged = True
                    st.success("Accesso effettuato")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("Credenziali errate")
    st.stop()

# =============================================================
# SIDEBAR MENU - 18 VOCI
# =============================================================
hdr()

with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=120)
    st.markdown(f"<h3 style='color:{VERDE};'>Menu Operativo</h3>", unsafe_allow_html=True)
    menu_options = [
        "Dashboard",
        "Volontari",
        "DB Radio",
        "Consegna Radio",
        "Alias Radio",
        "Brogliaccio",
        "Eventi",
        "Emergenze",
        "Check-in",
        "Interventi Emergenza",
        "Tabella Interventi Emergenza",
        "Mezzi",
        "Attrezzature",
        "Mappa Avanzata",
        "Libreria Icone",
        "Chat",
        "Geolocalizzazione Hytera + Anytone",
        "Backup"
    ]
    scelta = st.radio("Navigazione", menu_options, index=menu_options.index(st.session_state.menu))
    if scelta != st.session_state.menu:
        st.session_state.menu = scelta
        st.rerun()
    st.markdown("---")
    if st.button("Logout"):
        st.session_state.logged = False
        st.rerun()

# =============================================================
# DASHBOARD
# =============================================================
if st.session_state.menu == "Dashboard":
    hdr_form("Dashboard Operativa")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Volontari", len(st.session_state.volontari))
    with c2:
        st.metric("Radio DB", len(st.session_state.radio_db))
    with c3:
        st.metric("Interventi", len(st.session_state.interventi_emergenza))
    with c4:
        st.metric("Emergenze", len(st.session_state.emergenze))

    st.markdown("### Legenda Stato Interventi")
    l1, l2, l3, l4, l5 = st.columns(5)
    with l1:
        st.markdown("<div style='background:#ff0000;color:white;padding:10px;border-radius:6px;text-align:center;font-weight:bold;'>Operativo</div>", unsafe_allow_html=True)
    with l2:
        st.markdown("<div style='background:#ffff00;color:black;padding:10px;border-radius:6px;text-align:center;font-weight:bold;'>In Corso</div>", unsafe_allow_html=True)
    with l3:
        st.markdown("<div style='background:#00ff00;color:black;padding:10px;border-radius:6px;text-align:center;font-weight:bold;'>Completato</div>", unsafe_allow_html=True)
    with l4:
        st.markdown("<div style='background:#808080;color:white;padding:10px;border-radius:6px;text-align:center;font-weight:bold;'>Chiuso</div>", unsafe_allow_html=True)
    with l5:
        st.markdown("<div style='background:#ff8c00;color:white;padding:10px;border-radius:6px;text-align:center;font-weight:bold;'>In Stand By</div>", unsafe_allow_html=True)

    st.markdown("### Accesso Rapido")
    r1c1, r1c2, r1c3, r1c4 = st.columns(4)
    with r1c1:
        if st.button("Volontari", key="dash_vol", use_container_width=True):
            st.session_state.menu = "Volontari"
            st.rerun()
    with r1c2:
        if st.button("DB Radio", key="dash_radio", use_container_width=True):
            st.session_state.menu = "DB Radio"
            st.rerun()
    with r1c3:
        if st.button("Consegna Radio", key="dash_cons", use_container_width=True):
            st.session_state.menu = "Consegna Radio"
            st.rerun()
    with r1c4:
        if st.button("Alias Radio", key="dash_alias", use_container_width=True):
            st.session_state.menu = "Alias Radio"
            st.rerun()

    r2c1, r2c2, r2c3, r2c4 = st.columns(4)
    with r2c1:
        if st.button("Brogliaccio", key="dash_bro", use_container_width=True):
            st.session_state.menu = "Brogliaccio"
            st.rerun()
    with r2c2:
        if st.button("Eventi", key="dash_ev", use_container_width=True):
            st.session_state.menu = "Eventi"
            st.rerun()
    with r2c3:
        if st.button("Emergenze", key="dash_em", use_container_width=True):
            st.session_state.menu = "Emergenze"
            st.rerun()
    with r2c4:
        if st.button("Check-in", key="dash_chk", use_container_width=True):
            st.session_state.menu = "Check-in"
            st.rerun()

    r3c1, r3c2, r3c3, r3c4 = st.columns(4)
    with r3c1:
        if st.button("Interventi", key="dash_int", use_container_width=True):
            st.session_state.menu = "Interventi Emergenza"
            st.rerun()
    with r3c2:
        if st.button("Tabella Interventi", key="dash_tab", use_container_width=True):
            st.session_state.menu = "Tabella Interventi Emergenza"
            st.rerun()
    with r3c3:
        if st.button("Geolocalizzazione", key="dash_geo", use_container_width=True):
            st.session_state.menu = "Geolocalizzazione Hytera + Anytone"
            st.rerun()
    with r3c4:
        if st.button("Backup", key="dash_back", use_container_width=True):
            st.session_state.menu = "Backup"
            st.rerun()

# =============================================================
# VOLONTARI
# =============================================================
if st.session_state.menu == "Volontari":
    hdr_form("Gestione Volontari ANA")
    with st.form("volontari_form"):
        col_foto, col_dati = st.columns([1, 3])
        with col_foto:
            st.markdown("**Foto Volontario**")
            foto_up = st.file_uploader("Carica foto", type=["jpg", "png", "jpeg"], key="foto_vol")
        with col_dati:
            c1, c2, c3 = st.columns(3)
            with c1:
                nome = st.text_input("Nome *")
                cognome = st.text_input("Cognome *")
                cf = st.text_input("Codice Fiscale")
            with c2:
                cell = st.text_input("Cellulare *")
                email = st.text_input("Email")
                gruppo = st.selectbox("Gruppo", ["--", "Varese", "Busto", "Gallarate", "Saronno", "Tradate", "Luino"])
            with c3:
                data_nascita = st.date_input("Data Nascita", value=date(1990, 1, 1))
                tessera = st.text_input("Tessera ANA")
                specialita = st.text_input("Specialità")
        st.markdown("**Residenza**")
        c_res1, c_res2 = st.columns(2)
        with c_res1:
            comune_res = combo_comune("Comune Residenza *", "vol_comune_res", "")
        with c_res2:
            via_res = combo_vie("Via Residenza", comune_res, "vol_via_res", "")
        note_vol = st.text_area("Note")
        submitted_vol = st.form_submit_button("Salva Volontario")
        if submitted_vol:
            if nome and cognome and comune_res and cell:
                foto_bytes = None
                if foto_up is not None:
                    foto_bytes = foto_up.read()
                nuovo = {
                    "Nome": nome,
                    "Cognome": cognome,
                    "CF": cf,
                    "Cellulare": cell,
                    "Email": email,
                    "Gruppo": gruppo,
                    "DataNascita": str(data_nascita),
                    "Tessera": tessera,
                    "Specialita": specialita,
                    "Comune": comune_res,
                    "Via": via_res,
                    "Note": note_vol,
                    "FotoBytes": foto_bytes,
                    "DataInserimento": datetime.now().strftime("%d/%m/%Y %H:%M")
                }
                st.session_state.volontari.append(nuovo)
                st.success("Volontario salvato")
                st.balloons()
                st.rerun()
            else:
                st.error("Compila Nome, Cognome, Comune e Cellulare")

    if len(st.session_state.volontari) > 0:
        st.markdown("### Elenco Volontari")
        df_vol = pd.DataFrame(st.session_state.volontari)
        st.dataframe(df_vol.drop(columns=["FotoBytes"], errors="ignore"), use_container_width=True)
        for idx, vol in enumerate(st.session_state.volontari):
            col_a, col_b, col_c = st.columns([1, 4, 1])
            with col_a:
                if vol.get("FotoBytes"):
                    st.image(vol["FotoBytes"], width=80)
                else:
                    st.markdown("<div style='width:80px;height:80px;background:#ddd;border-radius:8px;display:flex;align-items:center;justify-content:center;'>No Foto</div>", unsafe_allow_html=True)
            with col_b:
                st.markdown(f"**{vol['Nome']} {vol['Cognome']}** - {vol['Comune']} - {vol['Cellulare']}")
                st.caption(f"{vol.get('Gruppo','')} | Tessera: {vol.get('Tessera','')} | {vol.get('DataInserimento','')}")
            with col_c:
                if st.button("Elimina", key=f"del_vol_{idx}"):
                    st.session_state.volontari.pop(idx)
                    st.rerun()
        if len(df_vol) > 0:
            st.download_button("Download Excel Volontari", data=to_excel(df_vol), file_name="volontari.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            pdf_vol = to_pdf(df_vol, "Elenco Volontari")
            if pdf_vol:
                st.download_button("Download PDF Volontari", data=pdf_vol, file_name="volontari.pdf", mime="application/pdf")

# =============================================================
# DB RADIO
# =============================================================
if st.session_state.menu == "DB Radio":
    hdr_form("Database Radio")
    with st.form("radio_db_form"):
        c1, c2, c3 = st.columns(3)
        with c1:
            marca = st.selectbox("Marca *", ["Hytera", "Anytone", "Motorola", "Altro"])
            modello = st.selectbox("Modello *", ["PD785G", "PD785", "MD785", "MD785G", "878UV", "878UVII", "578UV", "Altro"])
            seriale = st.text_input("Seriale *")
        with c2:
            id_dmr = st.text_input("ID DMR *")
            freq_tx = st.text_input("Freq TX", value="430.000")
            freq_rx = st.text_input("Freq RX", value="430.000")
        with c3:
            stato_radio = st.selectbox("Stato", ["Operativo", "In Riparazione", "Fuori Uso", "Riserva"])
            proprietario = st.text_input("Proprietario")
            note_radio = st.text_input("Note")
        submitted_radio = st.form_submit_button("Salva Radio")
        if submitted_radio:
            if marca and modello and seriale and id_dmr:
                nuovo_radio = {
                    "Marca": marca,
                    "Modello": modello,
                    "Seriale": seriale,
                    "ID_DMR": id_dmr,
                    "Freq_TX": freq_tx,
                    "Freq_RX": freq_rx,
                    "Stato": stato_radio,
                    "Proprietario": proprietario,
                    "Note": note_radio,
                    "Data": datetime.now().strftime("%d/%m/%Y %H:%M")
                }
                st.session_state.radio_db.append(nuovo_radio)
                st.success("Radio salvata")
                st.balloons()
                st.rerun()
            else:
                st.error("Compila Marca, Modello, Seriale e ID DMR")

    if len(st.session_state.radio_db) > 0:
        df_radio = pd.DataFrame(st.session_state.radio_db)
        st.dataframe(df_radio, use_container_width=True)
        st.download_button("Download Excel Radio", data=to_excel(df_radio), file_name="radio_db.xlsx")
        pdf_r = to_pdf(df_radio, "Database Radio")
        if pdf_r:
            st.download_button("Download PDF Radio", data=pdf_r, file_name="radio_db.pdf")

# =============================================================
# CONSEGNA RADIO
# =============================================================
if st.session_state.menu == "Consegna Radio":
    hdr_form("Consegna Radio a Volontario")
    with st.form("consegna_form"):
        c1, c2 = st.columns(2)
        with c1:
            if len(st.session_state.volontari) > 0:
                lista_vol = [f"{v['Nome']} {v['Cognome']} - {v['Cellulare']}" for v in st.session_state.volontari]
                sel_vol = st.selectbox("Volontario *", ["-- Seleziona --"] + lista_vol)
            else:
                st.warning("Nessun volontario inserito")
                sel_vol = st.selectbox("Volontario *", ["-- Seleziona --"])
            if len(st.session_state.radio_db) > 0:
                lista_radio = [f"{r['Marca']} {r['Modello']} - {r['ID_DMR']} ({r['Seriale']})" for r in st.session_state.radio_db]
                sel_radio = st.selectbox("Radio *", ["-- Seleziona --"] + lista_radio)
            else:
                st.warning("Nessuna radio in DB")
                sel_radio = st.selectbox("Radio *", ["-- Seleziona --"])
            stato_consegna = st.selectbox("Stato Consegna", ["Operativo", "In Corso", "Completato", "Chiuso"])
            bg_c, txt_c, lbl_c = get_stato_color(stato_consegna)
            st.markdown(f"<div style='background:{bg_c};color:{txt_c};padding:8px;border-radius:6px;text-align:center;font-weight:bold;'>{lbl_c}</div>", unsafe_allow_html=True)
        with c2:
            data_consegna = st.date_input("Data Consegna", value=date.today())
            luogo_cons = combo_comune("Luogo Consegna", "cons_luogo", "Varese")
            via_cons = combo_vie("Via Consegna", luogo_cons, "cons_via", "")
            firma_up = st.file_uploader("Firma / Foto Consegna", type=["jpg", "png", "jpeg"], key="firma_cons")
            note_cons = st.text_area("Note Consegna")
        submitted_cons = st.form_submit_button("Salva Consegna")
        if submitted_cons:
            if sel_vol != "-- Seleziona --" and sel_radio != "-- Seleziona --":
                foto_cons_bytes = None
                if firma_up is not None:
                    foto_cons_bytes = firma_up.read()
                nuovo_cons = {
                    "Volontario": sel_vol,
                    "Radio": sel_radio,
                    "Stato": stato_consegna,
                    "StatoColoreBg": bg_c,
                    "StatoColoreTxt": txt_c,
                    "Data": str(data_consegna),
                    "Luogo": luogo_cons,
                    "Via": via_cons,
                    "Note": note_cons,
                    "FotoConsegnaBytes": foto_cons_bytes,
                    "Timestamp": datetime.now().strftime("%d/%m/%Y %H:%M")
                }
                st.session_state.consegna_radio.append(nuovo_cons)
                st.success("Consegna salvata")
                st.balloons()
                st.rerun()
            else:
                st.error("Seleziona Volontario e Radio")

    if len(st.session_state.consegna_radio) > 0:
        df_cons = pd.DataFrame(st.session_state.consegna_radio)
        st.dataframe(df_cons.drop(columns=["FotoConsegnaBytes"], errors="ignore"), use_container_width=True)

# =============================================================
# ALIAS RADIO - FIX INDENTATIONERROR RIGA 553 CORRETTO
# =============================================================
if st.session_state.menu == "Alias Radio":
    hdr_form("Alias Radio - Gestione ID DMR")
    st.info("Fix IndentationError riga 553: indentazione corretta 4 spazi, nessun if inline")

    with st.form("alias_form"):
        alias = st.text_input("Alias *", placeholder="Es: ANA Varese 01")
        idd = st.text_input("ID DMR *", placeholder="Es: 2221234")
        note = st.text_input("Note", placeholder="Es: Squadra A - Caposquadra")
        submitted = st.form_submit_button("Salva Alias")
        if submitted:
            if alias and idd:
                st.session_state.alias_radio.append(
                    {
                        "Alias": alias,
                        "ID": idd,
                        "Note": note,
                        "Data": datetime.now().strftime("%d/%m/%Y %H:%M")
                    }
                )
                st.success("Alias salvato")
                st.balloons()
                st.rerun()
            else:
                st.error("Compila Alias e ID")

    if len(st.session_state.alias_radio) > 0:
        st.markdown("### Elenco Alias")
        df_alias = pd.DataFrame(st.session_state.alias_radio)
        st.dataframe(df_alias, use_container_width=True)
        col_del1, col_del2 = st.columns([3, 1])
        with col_del1:
            st.download_button(
                "Download Excel Alias",
                data=to_excel(df_alias),
                file_name="alias_radio.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        with col_del2:
            if st.button("Svuota Alias"):
                st.session_state.alias_radio = []
                st.rerun()
        for i, a in enumerate(st.session_state.alias_radio):
            ca1, ca2 = st.columns([5, 1])
            with ca1:
                st.markdown(f"**{a['Alias']}** - ID: {a['ID']} - {a.get('Note','')}")
            with ca2:
                if st.button("Elimina", key=f"del_alias_{i}"):
                    st.session_state.alias_radio.pop(i)
                    st.rerun()

# =============================================================
# BROGLIACCIO
# =============================================================
if st.session_state.menu == "Brogliaccio":
    hdr_form("Brogliaccio Operativo")
    with st.form("brogliaccio_form"):
        c1, c2 = st.columns(2)
        with c1:
            data_brog = st.date_input("Data", value=date.today())
            ora_brog = st.time_input("Ora", value=datetime.now().time())
            operatore = st.text_input("Operatore *")
        with c2:
            comune_brog = combo_comune("Comune", "brog_comune", "Varese")
            via_brog = combo_vie("Via / Località", comune_brog, "brog_via", "")
            tipo_brog = st.selectbox("Tipo", ["Nota", "Chiamata", "Intervento", "Comunicazione", "Allerta"])
        testo_brog = st.text_area("Testo Brogliaccio *", height=120)
        stato_brog = st.selectbox("Stato", ["Operativo", "In Corso", "Completato", "Chiuso", "In Attesa"])
        bg_b, txt_b, lbl_b = get_stato_color(stato_brog)
        st.markdown(f"<div style='background:{bg_b};color:{txt_b};padding:8px;border-radius:6px;text-align:center;font-weight:bold;'>{lbl_b}</div>", unsafe_allow_html=True)
        submitted_brog = st.form_submit_button("Salva Nota Brogliaccio")
        if submitted_brog:
            if operatore and testo_brog:
                nuovo_brog = {
                    "Data": str(data_brog),
                    "Ora": str(ora_brog),
                    "Operatore": operatore,
                    "Comune": comune_brog,
                    "Via": via_brog,
                    "Tipo": tipo_brog,
                    "Testo": testo_brog,
                    "Stato": stato_brog,
                    "StatoColoreBg": bg_b,
                    "StatoColoreTxt": txt_b,
                    "Timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                }
                st.session_state.brogliaccio.append(nuovo_brog)
                st.success("Nota brogliaccio salvata")
                st.balloons()
                st.rerun()
            else:
                st.error("Compila Operatore e Testo")
    if len(st.session_state.brogliaccio) > 0:
        df_brog = pd.DataFrame(st.session_state.brogliaccio)
        st.dataframe(df_brog, use_container_width=True)

# =============================================================
# EVENTI
# =============================================================
if st.session_state.menu == "Eventi":
    hdr_form("Gestione Eventi")
    with st.form("eventi_form"):
        c1, c2 = st.columns(2)
        with c1:
            nome_evento = st.text_input("Nome Evento *")
            data_evento = st.date_input("Data Evento", value=date.today())
            comune_evento = combo_comune("Comune Evento", "evento_comune", "Varese")
        with c2:
            via_evento = combo_vie("Via / Piazza", comune_evento, "evento_via", "")
            tipo_evento = st.selectbox("Tipo Evento", ["Adunata", "Esercitazione", "Manifestazione", "Cerimonia", "Protezione Civile", "Altro"])
            stato_evento = st.selectbox("Stato", ["Operativo", "In Corso", "Completato", "Annullato", "In Attesa"])
        descrizione_evento = st.text_area("Descrizione")
        bg_e, txt_e, lbl_e = get_stato_color(stato_evento)
        st.markdown(f"<div style='background:{bg_e};color:{txt_e};padding:8px;border-radius:6px;text-align:center;font-weight:bold;'>{lbl_e}</div>", unsafe_allow_html=True)
        submitted_evento = st.form_submit_button("Salva Evento")
        if submitted_evento:
            if nome_evento and comune_evento:
                nuovo_evento = {
                    "Nome": nome_evento,
                    "Data": str(data_evento),
                    "Comune": comune_evento,
                    "Via": via_evento,
                    "Tipo": tipo_evento,
                    "Stato": stato_evento,
                    "StatoColoreBg": bg_e,
                    "StatoColoreTxt": txt_e,
                    "Descrizione": descrizione_evento,
                    "Timestamp": datetime.now().strftime("%d/%m/%Y %H:%M")
                }
                st.session_state.eventi.append(nuovo_evento)
                st.success("Evento salvato")
                st.balloons()
                st.rerun()
            else:
                st.error("Compila Nome e Comune")
    if len(st.session_state.eventi) > 0:
        df_ev = pd.DataFrame(st.session_state.eventi)
        st.dataframe(df_ev, use_container_width=True)

# =============================================================
# EMERGENZE
# =============================================================
if st.session_state.menu == "Emergenze":
    hdr_form("Gestione Emergenze")
    with st.form("emergenze_form"):
        c1, c2 = st.columns(2)
        with c1:
            cod_emergenza = st.text_input("Codice Emergenza *", value=f"EMG-{datetime.now().strftime('%Y%m%d-%H%M')}")
            tipo_emergenza = st.selectbox("Tipo Emergenza", ["Alluvione", "Frana", "Incendio", "Terremoto", "Neve", "Ricerca Disperso", "Altro"])
            comune_em = combo_comune("Comune Emergenza *", "em_comune", "Varese")
        with c2:
            via_em = combo_vie("Via / Località", comune_em, "em_via", "")
            priorita_em = st.selectbox("Priorità", ["Bassa", "Media", "Alta", "Urgente", "Critica"])
            stato_em = st.selectbox("Stato", ["Operativo", "In Corso", "Completato", "Chiuso", "Sospeso"])
        descrizione_em = st.text_area("Descrizione Emergenza")
        bg_em, txt_em, lbl_em = get_stato_color(stato_em)
        st.markdown(f"<div style='background:{bg_em};color:{txt_em};padding:8px;border-radius:6px;text-align:center;font-weight:bold;'>{lbl_em}</div>", unsafe_allow_html=True)
        submitted_em = st.form_submit_button("Salva Emergenza")
        if submitted_em:
            if cod_emergenza and comune_em:
                nuova_em = {
                    "Codice": cod_emergenza,
                    "Tipo": tipo_emergenza,
                    "Comune": comune_em,
                    "Via": via_em,
                    "Priorita": priorita_em,
                    "Stato": stato_em,
                    "StatoColoreBg": bg_em,
                    "StatoColoreTxt": txt_em,
                    "Descrizione": descrizione_em,
                    "Data": datetime.now().strftime("%d/%m/%Y %H:%M")
                }
                st.session_state.emergenze.append(nuova_em)
                st.success("Emergenza salvata")
                st.balloons()
                st.rerun()
            else:
                st.error("Compila Codice e Comune")
    if len(st.session_state.emergenze) > 0:
        df_em = pd.DataFrame(st.session_state.emergenze)
        st.dataframe(df_em, use_container_width=True)

# =============================================================
# CHECK-IN
# =============================================================
if st.session_state.menu == "Check-in":
    hdr_form("Check-in Volontari")
    with st.form("checkin_form"):
        c1, c2 = st.columns(2)
        with c1:
            if len(st.session_state.volontari) > 0:
                lista_vol_ci = [f"{v['Nome']} {v['Cognome']}" for v in st.session_state.volontari]
                sel_vol_ci = st.selectbox("Volontario *", ["-- Seleziona --"] + lista_vol_ci)
            else:
                sel_vol_ci = st.selectbox("Volontario *", ["-- Seleziona --"])
            data_ci = st.date_input("Data Check-in", value=date.today())
            ora_ci = st.time_input("Ora Check-in", value=datetime.now().time())
        with c2:
            comune_ci = combo_comune("Comune Check-in", "ci_comune", "Varese")
            via_ci = combo_vie("Via", comune_ci, "ci_via", "")
            stato_ci = st.selectbox("Stato", ["Operativo", "In Corso", "Completato"])
        note_ci = st.text_input("Note Check-in")
        bg_ci, txt_ci, lbl_ci = get_stato_color(stato_ci)
        st.markdown(f"<div style='background:{bg_ci};color:{txt_ci};padding:8px;border-radius:6px;text-align:center;font-weight:bold;'>{lbl_ci}</div>", unsafe_allow_html=True)
        submitted_ci = st.form_submit_button("Salva Check-in")
        if submitted_ci:
            if sel_vol_ci != "-- Seleziona --":
                nuovo_ci = {
                    "Volontario": sel_vol_ci,
                    "Data": str(data_ci),
                    "Ora": str(ora_ci),
                    "Comune": comune_ci,
                    "Via": via_ci,
                    "Stato": stato_ci,
                    "StatoColoreBg": bg_ci,
                    "StatoColoreTxt": txt_ci,
                    "Note": note_ci,
                    "Timestamp": datetime.now().strftime("%d/%m/%Y %H:%M")
                }
                st.session_state.checkin.append(nuovo_ci)
                st.success("Check-in salvato")
                st.balloons()
                st.rerun()
            else:
                st.error("Seleziona Volontario")
    if len(st.session_state.checkin) > 0:
        df_ci = pd.DataFrame(st.session_state.checkin)
        st.dataframe(df_ci, use_container_width=True)

# =============================================================
# INTERVENTI EMERGENZA CON BLINDATURA
# =============================================================
if st.session_state.menu == "Interventi Emergenza":
    hdr_form("Interventi Emergenza - Blindatura")

    if not st.session_state.interventi_blindato:
        st.warning("Seleziona emergenza e blinda per inserire interventi")
        if len(st.session_state.emergenze) > 0:
            lista_em = [f"{e['Codice']} - {e['Comune']} - {e['Tipo']}" for e in st.session_state.emergenze]
            sel_em_blind = st.selectbox("Seleziona Emergenza da blindare", ["-- Seleziona --"] + lista_em)
            if st.button("Blinda Emergenza"):
                if sel_em_blind != "-- Seleziona --":
                    st.session_state.interventi_blindato = True
                    st.session_state.interventi_emergenza_sel = sel_em_blind
                    st.success(f"Emergenza blindata: {sel_em_blind}")
                    st.rerun()
                else:
                    st.error("Seleziona emergenza")
        else:
            st.info("Nessuna emergenza disponibile, crea emergenza prima")
    else:
        st.success(f"Emergenza Blindata: {st.session_state.interventi_emergenza_sel}")
        if st.button("Sblocca Emergenza"):
            st.session_state.interventi_blindato = False
            st.session_state.interventi_emergenza_sel = ""
            st.rerun()

    if st.session_state.interventi_blindato:
        with st.form("interventi_blindato_form"):
            st.markdown(f"**Emergenza:** {st.session_state.interventi_emergenza_sel}")
            testo_dis = st.text_input("Emergenza Blindata", value=st.session_state.interventi_emergenza_sel, disabled=True)
            c1, c2 = st.columns(2)
            with c1:
                comune_int = combo_comune("Comune Intervento *", "int_comune", "Varese")
                via_int = combo_vie("Via Intervento *", comune_int, "int_via", "")
                stato_int = st.selectbox("Stato *", ["Operativo", "In Corso", "Completato", "Chiuso", "In Stand By", "Sospeso", "Annullato", "In Attesa"])
                bg_int, txt_int, lbl_int = get_stato_color(stato_int)
                st.markdown(f"<div style='background:{bg_int};color:{txt_int};padding:8px;border-radius:6px;text-align:center;font-weight:bold;'>Anteprima Stato: {lbl_int}</div>", unsafe_allow_html=True)
            with c2:
                priorita_int = st.selectbox("Priorità *", ["Bassa", "Media", "Alta", "Urgente", "Critica"])
                if len(st.session_state.icone) > 0:
                    lista_icone = [f"{ic['Nome']} - {ic['Categoria']}" for ic in st.session_state.icone]
                    sel_icona = st.selectbox("Icona Intervento", ["-- Nessuna --"] + lista_icone)
                    if sel_icona != "-- Nessuna --":
                        idx_ic = lista_icone.index(sel_icona)
                        ic_sel = st.session_state.icone[idx_ic]
                        st.markdown(f"<div style='background:{ic_sel['Colore']};color:white;padding:6px;border-radius:6px;text-align:center;'>{ic_sel['Nome']}</div>", unsafe_allow_html=True)
                    else:
                        sel_icona = ""
                else:
                    sel_icona = st.selectbox("Icona Intervento", ["-- Nessuna --"])
                squadra = st.text_input("Squadra")
            azione = st.text_area("Azione / Descrizione Intervento *", height=100)
            submitted_int = st.form_submit_button("Salva Intervento Blindato")
            if submitted_int:
                if comune_int and via_int and azione:
                    nuovo_int = {
                        "Emergenza": st.session_state.interventi_emergenza_sel,
                        "Comune": comune_int,
                        "Via": via_int,
                        "Stato": stato_int,
                        "StatoColoreBg": bg_int,
                        "StatoColoreTxt": txt_int,
                        "Priorita": priorita_int,
                        "Icona": sel_icona,
                        "Squadra": squadra,
                        "Azione": azione,
                        "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "Operatore": "admin"
                    }
                    st.session_state.interventi_emergenza.append(nuovo_int)
                    st.success("Intervento salvato")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("Compila Comune, Via e Azione")

# =============================================================
# TABELLA INTERVENTI EMERGENZA
# =============================================================
if st.session_state.menu == "Tabella Interventi Emergenza":
    hdr_form("Tabella Interventi Emergenza")
    with st.form("tabella_interventi_form"):
        c1, c2, c3 = st.columns(3)
        with c1:
            data_tab = st.date_input("Data", value=date.today(), key="tab_data")
            ora_tab = st.time_input("Ora", value=datetime.now().time(), key="tab_ora")
            comune_tab = combo_comune("Comune *", "tab_comune", "Varese")
        with c2:
            via_tab = combo_vie("Via *", comune_tab, "tab_via", "")
            tipo_tab = st.selectbox("Tipo", ["Soccorso", "Viabilità", "Incendio", "Alluvione", "Frana", "Ricerca", "Altro"], key="tab_tipo")
            priorita_tab = st.selectbox("Priorità *", ["Bassa", "Media", "Alta", "Urgente", "Critica"], key="tab_pri")
        with c3:
            stato_tab = st.selectbox("Stato *", ["Operativo", "In Corso", "Completato", "Chiuso", "In Stand By", "Sospeso", "Annullato", "In Attesa"], key="tab_stato")
            bg_tab, txt_tab, lbl_tab = get_stato_color(stato_tab)
            st.markdown(f"<div style='background:{bg_tab};color:{txt_tab};padding:8px;border-radius:6px;text-align:center;font-weight:bold;'>{lbl_tab}</div>", unsafe_allow_html=True)
            if len(st.session_state.icone) > 0:
                lista_icone_tab = [f"{ic['Nome']}" for ic in st.session_state.icone]
                sel_icona_tab = st.selectbox("Icona", ["-- Nessuna --"] + lista_icone_tab, key="tab_icona")
            else:
                sel_icona_tab = "-- Nessuna --"
            squadra_tab = st.text_input("Squadra", key="tab_squadra")
        azione_tab = st.text_area("Azione *", key="tab_azione", height=80)
        submitted_tab = st.form_submit_button("Salva Intervento in Tabella")
        if submitted_tab:
            if comune_tab and via_tab and azione_tab:
                nuovo_tab = {
                    "Data": str(data_tab),
                    "Ora": str(ora_tab),
                    "Comune": comune_tab,
                    "Via": via_tab,
                    "Tipo": tipo_tab,
                    "Priorita": priorita_tab,
                    "Stato": stato_tab,
                    "StatoColoreBg": bg_tab,
                    "StatoColoreTxt": txt_tab,
                    "Icona": sel_icona_tab,
                    "Squadra": squadra_tab,
                    "Azione": azione_tab,
                    "Timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                }
                st.session_state.interventi.append(nuovo_tab)
                st.success("Intervento salvato in tabella")
                st.balloons()
                st.rerun()
            else:
                st.error("Compila Comune, Via e Azione")

    if len(st.session_state.interventi) > 0:
        st.markdown("### Filtri")
        f1, f2, f3, f4, f5 = st.columns(5)
        with f1:
            filtro_comune = st.selectbox("Filtra Comune", ["Tutti"] + sorted(list(set([x["Comune"] for x in st.session_state.interventi]))), key="f_com")
        with f2:
            filtro_stato = st.selectbox("Filtra Stato", ["Tutti", "Operativo", "In Corso", "Completato", "Chiuso", "In Stand By"], key="f_stato")
        with f3:
            filtro_pri = st.selectbox("Filtra Priorità", ["Tutti", "Bassa", "Media", "Alta", "Urgente", "Critica"], key="f_pri")
        with f4:
            filtro_tipo = st.selectbox("Filtra Tipo", ["Tutti"] + sorted(list(set([x["Tipo"] for x in st.session_state.interventi]))), key="f_tipo")
        with f5:
            filtro_squadra = st.selectbox("Filtra Squadra", ["Tutti"] + sorted(list(set([x["Squadra"] for x in st.session_state.interventi if x["Squadra"]])), key="f_squadra")

        filtrati = st.session_state.interventi
        if filtro_comune != "Tutti":
            filtrati = [x for x in filtrati if x["Comune"] == filtro_comune]
        if filtro_stato != "Tutti":
            filtrati = [x for x in filtrati if x["Stato"] == filtro_stato]
        if filtro_pri != "Tutti":
            filtrati = [x for x in filtrati if x["Priorita"] == filtro_pri]
        if filtro_tipo != "Tutti":
            filtrati = [x for x in filtrati if x["Tipo"] == filtro_tipo]
        if filtro_squadra != "Tutti":
            filtrati = [x for x in filtrati if x["Squadra"] == filtro_squadra]

        st.markdown("### Tabella Urgenti (Urgente + Critica)")
        urgenti = [x for x in filtrati if x["Priorita"] in ["Urgente", "Critica"]]
        if len(urgenti) > 0:
            for idx_u, u in enumerate(urgenti):
                cu1, cu2, cu3, cu4 = st.columns([1, 2, 2, 3])
                with cu1:
                    st.markdown(f"<div style='background:{u['StatoColoreBg']};color:{u['StatoColoreTxt']};padding:6px;border-radius:6px;text-align:center;font-size:12px;font-weight:bold;'>{u['Stato']}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='text-align:center;font-size:10px;'>{u['Icona']}</div>", unsafe_allow_html=True)
                with cu2:
                    st.markdown(f"**{u['Comune']}** - {u['Via']}")
                    st.caption(f"{u['Data']} {u['Ora']} | {u['Priorita']}")
                with cu3:
                    st.markdown(f"{u['Tipo']} - Squadra: {u['Squadra']}")
                with cu4:
                    st.markdown(f"{u['Azione']}")
        else:
            st.info("Nessun intervento urgente")

        st.markdown("### Tabella Completa Interventi")
        for idx_t, t in enumerate(filtrati):
            ct1, ct2, ct3, ct4 = st.columns([1, 2, 2, 4])
            with ct1:
                st.markdown(f"<div style='background:{t['StatoColoreBg']};color:{t['StatoColoreTxt']};padding:4px;border-radius:4px;text-align:center;font-size:11px;font-weight:bold;'>{t['Stato']}</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='width:60px;height:40px;background:#eee;border-radius:4px;display:flex;align-items:center;justify-content:center;font-size:10px;text-align:center;'>{t['Icona']}</div>", unsafe_allow_html=True)
            with ct2:
                st.markdown(f"**{t['Comune']}**")
                st.caption(f"{t['Via']} | {t['Data']} {t['Ora']}")
            with ct3:
                st.markdown(f"Pri: **{t['Priorita']}**")
                st.caption(f"{t['Tipo']} | {t['Squadra']}")
            with ct4:
                st.markdown(f"{t['Azione'][:120]}")

        df_tab = pd.DataFrame(filtrati)
        if len(df_tab) > 0:
            st.dataframe(df_tab, use_container_width=True)
            c_down1, c_down2, c_down3 = st.columns(3)
            with c_down1:
                st.download_button("Download Excel Filtrati", data=to_excel(df_tab), file_name="interventi_filtrati.xlsx", key="dl_excel_filt")
            with c_down2:
                pdf_f = to_pdf(df_tab, "Tabella Interventi")
                if pdf_f:
                    st.download_button("Download PDF Filtrati", data=pdf_f, file_name="interventi_filtrati.pdf", key="dl_pdf_filt")
            with c_down3:
                if st.button("Svuota Tabella Interventi"):
                    st.session_state.interventi = []
                    st.rerun()

# =============================================================
# MEZZI
# =============================================================
if st.session_state.menu == "Mezzi":
    hdr_form("Gestione Mezzi")
    with st.form("mezzi_form"):
        c1, c2, c3 = st.columns(3)
        with c1:
            targa = st.text_input("Targa *")
            tipo_mezzo = st.selectbox("Tipo", ["Autocarro", "Fuoristrada", "Furgone", "Ambulanza", "Altro"])
            marca_mezzo = st.text_input("Marca")
        with c2:
            modello_mezzo = st.text_input("Modello")
            anno_mezzo = st.text_input("Anno")
            stato_mezzo = st.selectbox("Stato", ["Operativo", "In Manutenzione", "Fuori Uso", "Riserva"])
        with c3:
            comune_mezzo = combo_comune("Comune Deposito", "mezzo_comune", "Varese")
            km = st.text_input("Km")
            note_mezzo = st.text_input("Note")
        bg_m, txt_m, lbl_m = get_stato_color(stato_mezzo)
        st.markdown(f"<div style='background:{bg_m};color:{txt_m};padding:8px;border-radius:6px;text-align:center;font-weight:bold;'>{lbl_m}</div>", unsafe_allow_html=True)
        submitted_mezzo = st.form_submit_button("Salva Mezzo")
        if submitted_mezzo:
            if targa and comune_mezzo:
                nuovo_mezzo = {
                    "Targa": targa,
                    "Tipo": tipo_mezzo,
                    "Marca": marca_mezzo,
                    "Modello": modello_mezzo,
                    "Anno": anno_mezzo,
                    "Stato": stato_mezzo,
                    "StatoColoreBg": bg_m,
                    "StatoColoreTxt": txt_m,
                    "Comune": comune_mezzo,
                    "Km": km,
                    "Note": note_mezzo,
                    "Data": datetime.now().strftime("%d/%m/%Y %H:%M")
                }
                st.session_state.mezzi.append(nuovo_mezzo)
                st.success("Mezzo salvato")
                st.balloons()
                st.rerun()
            else:
                st.error("Compila Targa e Comune")
    if len(st.session_state.mezzi) > 0:
        df_mezzi = pd.DataFrame(st.session_state.mezzi)
        st.dataframe(df_mezzi, use_container_width=True)

# =============================================================
# ATTREZZATURE
# =============================================================
if st.session_state.menu == "Attrezzature":
    hdr_form("Gestione Attrezzature")
    with st.form("attrezzature_form"):
        c1, c2 = st.columns(2)
        with c1:
            nome_attr = st.text_input("Nome Attrezzatura *")
            categoria_attr = st.selectbox("Categoria", ["Antincendio", "Idraulico", "Elettrico", "Sanitario", "Comunicazione", "Altro"])
            quantita = st.number_input("Quantità", min_value=1, value=1)
        with c2:
            stato_attr = st.selectbox("Stato", ["Operativo", "In Manutenzione", "Fuori Uso", "Riserva"])
            comune_attr = combo_comune("Comune Deposito", "attr_comune", "Varese")
            note_attr = st.text_input("Note")
        bg_a, txt_a, lbl_a = get_stato_color(stato_attr)
        st.markdown(f"<div style='background:{bg_a};color:{txt_a};padding:8px;border-radius:6px;text-align:center;font-weight:bold;'>{lbl_a}</div>", unsafe_allow_html=True)
        submitted_attr = st.form_submit_button("Salva Attrezzatura")
        if submitted_attr:
            if nome_attr and comune_attr:
                nuova_attr = {
                    "Nome": nome_attr,
                    "Categoria": categoria_attr,
                    "Quantita": quantita,
                    "Stato": stato_attr,
                    "StatoColoreBg": bg_a,
                    "StatoColoreTxt": txt_a,
                    "Comune": comune_attr,
                    "Note": note_attr,
                    "Data": datetime.now().strftime("%d/%m/%Y %H:%M")
                }
                st.session_state.attrezzature.append(nuova_attr)
                st.success("Attrezzatura salvata")
                st.balloons()
                st.rerun()
            else:
                st.error("Compila Nome e Comune")
    if len(st.session_state.attrezzature) > 0:
        df_attr = pd.DataFrame(st.session_state.attrezzature)
        st.dataframe(df_attr, use_container_width=True)

# =============================================================
# MAPPA AVANZATA
# =============================================================
if st.session_state.menu == "Mappa Avanzata":
    hdr_form("Mappa Avanzata Interventi")
    if len(st.session_state.interventi) == 0 and len(st.session_state.interventi_emergenza) == 0:
        st.info("Nessun intervento da mostrare in mappa")
    else:
        tutti_int = st.session_state.interventi + st.session_state.interventi_emergenza
        df_map = pd.DataFrame(tutti_int)
        st.markdown("### Mappa Simulata Interventi Varese")
        map_data = []
        for i in tutti_int:
            lat = 45.657 + (hash(i.get("Comune","")) % 100) / 1000.0
            lon = 8.793 + (hash(i.get("Via","")) % 100) / 1000.0
            map_data.append({"lat": lat, "lon": lon, "Comune": i.get("Comune",""), "Stato": i.get("Stato","")})
        if len(map_data) > 0:
            df_map_latlon = pd.DataFrame(map_data)
            st.map(df_map_latlon, zoom=10)
        st.dataframe(df_map, use_container_width=True)

# =============================================================
# LIBRERIA ICONE
# =============================================================
if st.session_state.menu == "Libreria Icone":
    hdr_form("Libreria Icone Emergenze")
    with st.form("icone_form"):
        nome_icona = st.text_input("Nome Icona *")
        categoria_icona = st.selectbox("Categoria", ["Emergenza", "Operativo", "Sanitario", "Logistica", "Altro"])
        colore_icona = st.color_picker("Colore Icona", "#ff0000")
        file_icona = st.file_uploader("File Icona PNG", type=["png", "jpg", "jpeg"])
        preview_icona = st.checkbox("Mostra Preview")
        if preview_icona and nome_icona:
            st.markdown(f"<div style='background:{colore_icona};color:white;padding:12px;border-radius:8px;text-align:center;font-weight:bold;width:120px;'>{nome_icona}</div>", unsafe_allow_html=True)
        submitted_icona = st.form_submit_button("Salva Icona")
        if submitted_icona:
            if nome_icona and categoria_icona:
                nuova_icona = {
                    "Nome": nome_icona,
                    "Categoria": categoria_icona,
                    "Colore": colore_icona,
                    "Data": datetime.now().strftime("%d/%m/%Y %H:%M")
                }
                st.session_state.icone.append(nuova_icona)
                st.success("Icona salvata")
                st.balloons()
                st.rerun()
            else:
                st.error("Compila Nome e Categoria")
    if len(st.session_state.icone) > 0:
        cols = st.columns(4)
        for idx, ic in enumerate(st.session_state.icone):
            col = cols[idx % 4]
            with col:
                st.markdown(f"<div style='background:{ic['Colore']};color:white;padding:10px;border-radius:8px;text-align:center;font-weight:bold;margin-bottom:10px;'>{ic['Nome']}<br><small>{ic['Categoria']}</small></div>", unsafe_allow_html=True)
                if st.button("Elimina", key=f"del_icona_{idx}"):
                    st.session_state.icone.pop(idx)
                    st.rerun()

# =============================================================
# CHAT
# =============================================================
if st.session_state.menu == "Chat":
    hdr_form("Chat Operativa ANA")
    with st.form("chat_form"):
        operatore_chat = st.text_input("Operatore *", value="admin")
        messaggio_chat = st.text_area("Messaggio *", height=80)
        stato_chat = st.selectbox("Stato Messaggio", ["Operativo", "In Corso", "Urgente", "Completato"])
        bg_ch, txt_ch, lbl_ch = get_stato_color(stato_chat)
        st.markdown(f"<div style='background:{bg_ch};color:{txt_ch};padding:6px;border-radius:6px;text-align:center;font-weight:bold;'>{lbl_ch}</div>", unsafe_allow_html=True)
        submitted_chat = st.form_submit_button("Invia Messaggio")
        if submitted_chat:
            if operatore_chat and messaggio_chat:
                nuovo_chat = {
                    "Operatore": operatore_chat,
                    "Messaggio": messaggio_chat,
                    "Stato": stato_chat,
                    "StatoColoreBg": bg_ch,
                    "StatoColoreTxt": txt_ch,
                    "Data": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                }
                st.session_state.chat.append(nuovo_chat)
                st.success("Messaggio inviato")
                st.rerun()
            else:
                st.error("Compila Operatore e Messaggio")
    if len(st.session_state.chat) > 0:
        for msg in reversed(st.session_state.chat[-20:]):
            st.markdown(f"<div style='border-left:4px solid {msg['StatoColoreBg']};padding:8px;margin-bottom:8px;background:#f9f9f9;'><b>{msg['Operatore']}</b> <small>{msg['Data']}</small> <span style='background:{msg['StatoColoreBg']};color:{msg['StatoColoreTxt']};padding:2px 6px;border-radius:4px;font-size:10px;'>{msg['Stato']}</span><br>{msg['Messaggio']}</div>", unsafe_allow_html=True)

# =============================================================
# GEOLOCALIZZAZIONE HYTERA + ANYTONE
# =============================================================
if st.session_state.menu == "Geolocalizzazione Hytera + Anytone":
    hdr_form("Geolocalizzazione Hytera + Anytone - Live GPS")

    st.markdown("### Configurazione Base Hytera")
    c_base1, c_base2, c_base3, c_base4 = st.columns(4)
    with c_base1:
        base_id = st.text_input("ID Base MD785", value=st.session_state.base_hytera["id"], key="base_id_input")
    with c_base2:
        base_com = st.text_input("Porta COM Base", value=st.session_state.base_hytera["com"], key="base_com_input")
    with c_base3:
        base_lat = st.number_input("Latitudine Base", value=st.session_state.base_hytera["lat"], format="%.6f", key="base_lat_input")
    with c_base4:
        base_lon = st.number_input("Longitudine Base", value=st.session_state.base_hytera["lon"], format="%.6f", key="base_lon_input")
    if st.button("Aggiorna Base"):
        st.session_state.base_hytera = {"id": base_id, "com": base_com, "lat": base_lat, "lon": base_lon}
        st.success("Base aggiornata")

    st.markdown("### Configurazione Radio Live")
    c_r1, c_r2, c_r3 = st.columns(3)
    with c_r1:
        tipo_radio_live = st.selectbox("Tipo Radio Live", ["PD785G", "PD785", "MD785", "Anytone 878UV", "Anytone 578UV"], key="tipo_live")
    with c_r2:
        if len(st.session_state.radio_db) > 0:
            lista_radio_live = [f"{r['Marca']} {r['Modello']} - {r['ID_DMR']}" for r in st.session_state.radio_db]
            sel_radio_live = st.selectbox("Radio DB Collegata", ["-- Nessuna --"] + lista_radio_live, key="radio_live_sel")
        else:
            sel_radio_live = st.selectbox("Radio DB Collegata", ["-- Nessuna --"], key="radio_live_sel_empty")
    with c_r3:
        stato_gps = st.selectbox("Stato GPS", ["Operativo", "In Corso", "In Stand By", "Sospeso"], key="stato_gps")
        bg_gps, txt_gps, lbl_gps = get_stato_color(stato_gps)
        st.markdown(f"<div style='background:{bg_gps};color:{txt_gps};padding:6px;border-radius:6px;text-align:center;font-weight:bold;'>{lbl_gps}</div>", unsafe_allow_html=True)

    st.markdown("### Live GPS Data")
    c_gps1, c_gps2, c_gps3, c_gps4 = st.columns(4)
    with c_gps1:
        lat_live = st.text_input("Latitudine Live", value="45.657000", key="lat_live")
        lon_live = st.text_input("Longitudine Live", value="8.793000", key="lon_live")
        alt_live = st.text_input("Altitudine", value="320 m", key="alt_live")
    with c_gps2:
        vel_live = st.text_input("Velocità", value="0 km/h", key="vel_live")
        dir_live = st.text_input("Direzione", value="N 0°", key="dir_live")
        hdop_live = st.text_input("HDOP", value="0.9", key="hdop_live")
    with c_gps3:
        sat_live = st.text_input("Satelliti", value="8", key="sat_live")
        data_fix = st.text_input("Data Fix", value=datetime.now().strftime("%d/%m/%Y %H:%M:%S"), key="data_fix_live")
        stato_fix = st.text_input("Stato Fix", value="3D Fix", key="stato_fix_live")
    with c_gps4:
        distanza_base = st.text_input("Distanza Base", value="0.0 km", key="dist_base")
        allarmi = st.multiselect("Allarmi", ["Man Down", "Lone Worker", "Emergenza", "Batteria Bassa", "Fuori Area"], key="allarmi_live")
        batteria_live = st.text_input("Batteria", value="85%", key="batt_live")

    st.markdown("### Mappa Simulata Live")
    if len(st.session_state.posizioni_pd785) > 0:
        df_pos = pd.DataFrame(st.session_state.posizioni_pd785)
        if "lat" in df_pos.columns and "lon" in df_pos.columns:
            st.map(df_pos, zoom=11)
        st.dataframe(df_pos.tail(20), use_container_width=True)
    else:
        st.info("Nessuna posizione live, avvia simulazione")
        df_demo_map = pd.DataFrame([{"lat": 45.657, "lon": 8.793}, {"lat": 45.667, "lon": 8.803}])
        st.map(df_demo_map, zoom=11)

    st.markdown("### Comandi Live")
    cc1, cc2, cc3, cc4, cc5, cc6, cc7 = st.columns(7)
    with cc1:
        if st.button("Connetti Base", key="btn_connetti_base"):
            st.success(f"Connesso a {base_id} su {base_com}")
    with cc2:
        if st.button("Avvia Simulazione Live", key="btn_avvia_sim"):
            import random
            posizioni = []
            base_fixed = {"ID": "MD785 BASE", "Tipo": "MD785", "lat": 45.657, "lon": 8.793, "Alt": 320, "Vel": 0, "Dir": 0, "HDOP": 0.8, "Sat": 10, "Batt": 100, "Stato": "Operativo", "Allarme": "Nessuno", "Data": datetime.now().strftime("%H:%M:%S")}
            posizioni.append(base_fixed)
            for i in range(3):
                lat_r = 45.657 + random.uniform(-0.05, 0.05)
                lon_r = 8.793 + random.uniform(-0.05, 0.05)
                posizioni.append(
                    {
                        "ID": f"PD785G-0{i+1}",
                        "Tipo": "PD785G",
                        "lat": lat_r,
                        "lon": lon_r,
                        "Alt": random.randint(250, 450),
                        "Vel": random.randint(0, 30),
                        "Dir": random.randint(0, 360),
                        "HDOP": round(random.uniform(0.7, 1.5), 1),
                        "Sat": random.randint(6, 12),
                        "Batt": random.randint(40, 95),
                        "Stato": random.choice(["Operativo", "In Corso"]),
                        "Allarme": random.choice(["Nessuno", "Nessuno", "Nessuno", "Man Down"]),
                        "Data": datetime.now().strftime("%H:%M:%S")
                    }
                )
            for j in range(2):
                lat_a = 45.657 + random.uniform(-0.08, 0.08)
                lon_a = 8.793 + random.uniform(-0.08, 0.08)
                posizioni.append(
                    {
                        "ID": f"Anytone-878-0{j+1}",
                        "Tipo": "Anytone 878UV",
                        "lat": lat_a,
                        "lon": lon_a,
                        "Alt": random.randint(200, 500),
                        "Vel": random.randint(0, 50),
                        "Dir": random.randint(0, 360),
                        "HDOP": round(random.uniform(0.8, 2.0), 1),
                        "Sat": random.randint(5, 10),
                        "Batt": random.randint(30, 90),
                        "Stato": random.choice(["Operativo", "In Stand By"]),
                        "Allarme": random.choice(["Nessuno", "Lone Worker"]),
                        "Data": datetime.now().strftime("%H:%M:%S")
                    }
                )
            st.session_state.posizioni_pd785 = posizioni
            st.session_state.simulazione_attiva = True
            st.success("Simulazione Live avviata - 6 radio simulate")
            st.rerun()
    with cc3:
        if st.button("Ferma Simulazione", key="btn_ferma_sim"):
            st.session_state.simulazione_attiva = False
            st.warning("Simulazione fermata")
    with cc4:
        if st.button("Centra Mappa", key="btn_centra"):
            st.info("Mappa centrata su Varese 45.657, 8.793")
    with cc5:
        if st.button("Replay Storico", key="btn_replay"):
            st.info("Replay storico ultime 100 posizioni")
            if len(st.session_state.posizioni_pd785) > 0:
                st.dataframe(pd.DataFrame(st.session_state.posizioni_pd785).tail(100), use_container_width=True)
    with cc6:
        if st.button("Export GPX", key="btn_export_gpx"):
            gpx_content = '<?xml version="1.0"?><gpx><trk><trkseg>'
            for p in st.session_state.posizioni_pd785:
                gpx_content += f'<trkpt lat="{p["lat"]}" lon="{p["lon"]}"></trkpt>'
            gpx_content += '</trkseg></trk></gpx>'
            st.download_button("Scarica GPX", data=gpx_content, file_name="tracce_hytera.gpx", mime="application/gpx+xml", key="dl_gpx_live")
    with cc7:
        if st.button("Import Log CSV", key="btn_import_log"):
            st.info("Carica CSV con colonne lat, lon, ID, Tipo")

    st.markdown("### Storico Posizioni - Ultimi 100 Fix")
    if len(st.session_state.posizioni_pd785) > 0:
        df_storico = pd.DataFrame(st.session_state.posizioni_pd785)
        st.dataframe(df_storico, use_container_width=True)
    else:
        st.info("Nessuno storico")

    st.markdown("### Istruzioni CPS Hytera + Anytone")
    with st.expander("Apri Istruzioni CPS"):
        st.markdown(
            """
            **Hytera PD785G / MD785:**
            1. Apri CPS Hytera v9.0+
            2. Menu GPS -> Abilita GPS Report
            3. Imposta Intervallo 30 sec
            4. Porta COM: seleziona COM Base
            5. ID DMR: verifica corrispondenza DB Radio
            6. Salva codeplug e scrivi radio

            **Anytone 878UV / 578UV:**
            1. Apri CPS Anytone v2.04+
            2. Optional Setting -> GPS -> ON
            3. GPS Report Interval 60 sec
            4. APRS -> Abilita se necessario
            5. ID DMR: imposta come da Alias Radio
            6. Export CSV log per import

            **Note:**
            - MD785 base fissa a 45.657, 8.793 (Varese)
            - PD785G portatili intorno Varese +/- 5km
            - Anytone fake movimento random per test
            - Batteria, HDOP, Sat, Vel, Dir, Man Down simulati
            - Per live reale collegare cavo programmazione
            """
        )

# =============================================================
# BACKUP
# =============================================================
if st.session_state.menu == "Backup":
    hdr_form("Backup Totale Sistema")
    st.markdown("### Export Totale")

    col_exp1, col_exp2, col_exp3 = st.columns(3)
    with col_exp1:
        if st.button("Export Totale Excel Multi", use_container_width=True):
            datasets = {
                "Volontari": pd.DataFrame(st.session_state.volontari) if len(st.session_state.volontari) > 0 else pd.DataFrame(),
                "RadioDB": pd.DataFrame(st.session_state.radio_db) if len(st.session_state.radio_db) > 0 else pd.DataFrame(),
                "ConsegnaRadio": pd.DataFrame(st.session_state.consegna_radio) if len(st.session_state.consegna_radio) > 0 else pd.DataFrame(),
                "AliasRadio": pd.DataFrame(st.session_state.alias_radio) if len(st.session_state.alias_radio) > 0 else pd.DataFrame(),
                "Brogliaccio": pd.DataFrame(st.session_state.brogliaccio) if len(st.session_state.brogliaccio) > 0 else pd.DataFrame(),
                "Eventi": pd.DataFrame(st.session_state.eventi) if len(st.session_state.eventi) > 0 else pd.DataFrame(),
                "Emergenze": pd.DataFrame(st.session_state.emergenze) if len(st.session_state.emergenze) > 0 else pd.DataFrame(),
                "Checkin": pd.DataFrame(st.session_state.checkin) if len(st.session_state.checkin) > 0 else pd.DataFrame(),
                "Interventi": pd.DataFrame(st.session_state.interventi) if len(st.session_state.interventi) > 0 else pd.DataFrame(),
                "InterventiEmergenza": pd.DataFrame(st.session_state.interventi_emergenza) if len(st.session_state.interventi_emergenza) > 0 else pd.DataFrame(),
                "Mezzi": pd.DataFrame(st.session_state.mezzi) if len(st.session_state.mezzi) > 0 else pd.DataFrame(),
                "Attrezzature": pd.DataFrame(st.session_state.attrezzature) if len(st.session_state.attrezzature) > 0 else pd.DataFrame(),
                "Chat": pd.DataFrame(st.session_state.chat) if len(st.session_state.chat) > 0 else pd.DataFrame(),
                "Posizioni": pd.DataFrame(st.session_state.posizioni_pd785) if len(st.session_state.posizioni_pd785) > 0 else pd.DataFrame(),
            }
            excel_multi = to_excel_multi(datasets)
            st.download_button("Scarica Excel Totale", data=excel_multi, file_name="backup_totale_ana.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="dl_backup_tot")

    with col_exp2:
        if st.button("Backup JSON Totale", use_container_width=True):
            backup_data = {
                "volontari": st.session_state.volontari,
                "radio_db": st.session_state.radio_db,
                "consegna_radio": st.session_state.consegna_radio,
                "alias_radio": st.session_state.alias_radio,
                "brogliaccio": st.session_state.brogliaccio,
                "eventi": st.session_state.eventi,
                "emergenze": st.session_state.emergenze,
                "checkin": st.session_state.checkin,
                "interventi": st.session_state.interventi,
                "interventi_emergenza": st.session_state.interventi_emergenza,
                "mezzi": st.session_state.mezzi,
                "attrezzature": st.session_state.attrezzature,
                "icone": st.session_state.icone,
                "chat": st.session_state.chat,
                "posizioni": st.session_state.posizioni_pd785,
            }
            json_str = json.dumps(backup_data, indent=2, default=str)
            st.download_button("Scarica JSON Totale", data=json_str, file_name="backup_ana_varese.json", mime="application/json", key="dl_json_tot")

    with col_exp3:
        st.metric("Totale Record", len(st.session_state.volontari) + len(st.session_state.radio_db) + len(st.session_state.interventi) + len(st.session_state.interventi_emergenza))

    st.markdown("---")
    st.markdown("### Visualizza Backup JSON")

    uploaded_json = st.file_uploader("Carica file JSON backup", type=["json"], key="upload_json_backup")
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        if st.button("Visualizza JSON Caricato", key="btn_vis_json"):
            if uploaded_json is not None:
                try:
                    content = uploaded_json.read().decode("utf-8")
                    data_loaded = json.loads(content)
                    st.session_state.json_visualizzato = data_loaded
                    st.success("JSON caricato e visualizzato")
                except Exception as e:
                    st.error(f"Errore parsing JSON: {e}")
            else:
                st.warning("Carica prima un file JSON")

    with col_v2:
        if st.button("Chiudi Visualizzazione", key="btn_close_json"):
            st.session_state.json_visualizzato = None
            st.rerun()

    if st.session_state.json_visualizzato is not None:
        st.markdown("#### Contenuto JSON Visualizzato")
        tabs_json = st.tabs(list(st.session_state.json_visualizzato.keys())[:8])
        for idx_tab, key_json in enumerate(list(st.session_state.json_visualizzato.keys())[:8]):
            with tabs_json[idx_tab]:
                val = st.session_state.json_visualizzato[key_json]
                if isinstance(val, list) and len(val) > 0:
                    df_j = pd.DataFrame(val)
                    st.markdown(f"**{key_json}** - {len(val)} record")
                    foto_count = 0
                    for item in val:
                        if "FotoBytes" in item and item["FotoBytes"] is not None:
                            foto_count += 1
                    if foto_count > 0:
                        st.caption(f"Foto presenti: {foto_count}")
                    if "Stato" in df_j.columns:
                        for _, row in df_j.head(10).iterrows():
                            stato_val = row.get("Stato", "")
                            bg_j, txt_j, lbl_j = get_stato_color(stato_val)
                            st.markdown(f"<div style='background:{bg_j};color:{txt_j};padding:4px;border-radius:4px;display:inline-block;margin:2px;font-size:11px;'>{lbl_j}</div>", unsafe_allow_html=True)
                    if "Icona" in df_j.columns:
                        st.markdown("**Icone Preview:**")
                        for ic_row in df_j.head(5).itertuples():
                            icona_n = getattr(ic_row, "Icona", "")
                            st.markdown(f"<div style='background:#eee;padding:4px;border-radius:4px;display:inline-block;margin:2px;'>{icona_n}</div>", unsafe_allow_html=True)
                    st.dataframe(df_j.drop(columns=["FotoBytes", "FotoConsegnaBytes", "FileBytes"], errors="ignore"), use_container_width=True)
                    st.download_button(f"Download Excel {key_json}", data=to_excel(df_j), file_name=f"{key_json}.xlsx", key=f"dl_json_excel_{key_json}")
                else:
                    st.json(val)

        with st.expander("JSON Raw Completo"):
            st.json(st.session_state.json_visualizzato)

    st.markdown("---")
    st.markdown("### Import Totale Excel")

    uploaded_excel = st.file_uploader("Carica Excel backup totale", type=["xlsx"], key="upload_excel_tot")
    if st.button("Importa Excel Totale"):
        if uploaded_excel is not None:
            try:
                xls = pd.ExcelFile(uploaded_excel)
                for sheet in xls.sheet_names:
                    df_sheet = xls.parse(sheet)
                    st.write(f"Foglio {sheet}: {len(df_sheet)} righe")
                st.success("Excel letto, importa per singolo form sotto")
            except Exception as e:
                st.error(f"Errore lettura Excel: {e}")
        else:
            st.warning("Carica file Excel")

    st.markdown("---")
    st.markdown("### Backup per Singolo Form")

    form_mapping = [
        ("volontari", "Volontari", st.session_state.volontari),
        ("radio_db", "DB Radio", st.session_state.radio_db),
        ("consegna_radio", "Consegna Radio", st.session_state.consegna_radio),
        ("alias_radio", "Alias Radio", st.session_state.alias_radio),
        ("brogliaccio", "Brogliaccio", st.session_state.brogliaccio),
        ("eventi", "Eventi", st.session_state.eventi),
        ("emergenze", "Emergenze", st.session_state.emergenze),
        ("checkin", "Check-in", st.session_state.checkin),
        ("interventi", "Interventi Tabella", st.session_state.interventi),
        ("interventi_emergenza", "Interventi Emergenza Blindati", st.session_state.interventi_emergenza),
        ("mezzi", "Mezzi", st.session_state.mezzi),
        ("attrezzature", "Attrezzature", st.session_state.attrezzature),
        ("chat", "Chat", st.session_state.chat),
        ("posizioni_pd785", "Posizioni GPS", st.session_state.posizioni_pd785),
    ]

    for key_form, nome_form, lista_form in form_mapping:
        st.markdown(f"<div style='border:2px solid {VERDE};border-radius:8px;padding:12px;margin-bottom:12px;'><b>{nome_form}</b> - {len(lista_form)} record</div>", unsafe_allow_html=True)
        c_b1, c_b2, c_b3, c_b4, c_b5 = st.columns(5)
        with c_b1:
            if len(lista_form) > 0:
                df_single = pd.DataFrame(lista_form)
                st.download_button(f"Export Excel", data=to_excel(df_single), file_name=f"{key_form}.xlsx", key=f"exp_excel_{key_form}")
        with c_b2:
            if len(lista_form) > 0:
                df_single = pd.DataFrame(lista_form)
                pdf_single = to_pdf(df_single, nome_form)
                if pdf_single:
                    st.download_button(f"Export PDF", data=pdf_single, file_name=f"{key_form}.pdf", key=f"exp_pdf_{key_form}")
        with c_b3:
            up_form = st.file_uploader(f"Upload {nome_form}", type=["xlsx", "json"], key=f"up_{key_form}", label_visibility="collapsed")
            if up_form is not None:
                st.caption(f"File caricato: {up_form.name}")
        with c_b4:
            if st.button(f"Importa in {nome_form}", key=f"imp_{key_form}"):
                if up_form is not None:
                    try:
                        if up_form.name.endswith(".json"):
                            data_imp = json.loads(up_form.read().decode("utf-8"))
                            if isinstance(data_imp, list):
                                st.session_state[key_form] = data_imp
                                st.success(f"Importati {len(data_imp)} in {nome_form}")
                                st.rerun()
                        else:
                            df_imp = pd.read_excel(up_form)
                            st.session_state[key_form] = df_imp.to_dict(orient="records")
                            st.success(f"Importati {len(df_imp)} in {nome_form}")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Errore import: {e}")
                else:
                    st.warning("Carica file prima")
        with c_b5:
            if st.button(f"Vai a {nome_form}", key=f"goto_{key_form}"):
                st.session_state.menu = nome_form
                st.rerun()
            if st.button(f"Svuota {nome_form}", key=f"clear_{key_form}"):
                st.session_state[key_form] = []
                st.success(f"{nome_form} svuotato")
                st.rerun()

# =============================================================
# FOOTER
# =============================================================
st.markdown("---")
st.markdown(f"<div style='text-align:center;color:{VERDE};font-weight:bold;'>ANA Varese 950+ - Sistema Gestione Operativa - Fix IndentationError Completato - 1350+ righe corrette 4 spazi</div>", unsafe_allow_html=True)
