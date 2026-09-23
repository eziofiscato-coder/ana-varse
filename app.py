import streamlit as st
import pandas as pd
import os
import io
import json
import base64
from io import BytesIO
from datetime import datetime, date, time
import requests

try:
    from reportlab.lib.pagesizes import landscape, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    REPORTLAB_OK = True
except:
    REPORTLAB_OK = False

try:
    import openpyxl
    OPENPYXL_OK = True
except:
    OPENPYXL_OK = False

st.set_page_config(
    page_title="ANA Varese 950+ Modifiche Richieste",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Auto-inietta UI PATCH nella sidebar se disponibile
try:
    ui_patch_loader_sidebar()
except:
    pass



COMUNI_ITALIA = [
    "Varese", "Busto Arsizio", "Gallarate", "Saronno", "Cassano Magnago",
    "Tradate", "Malnate", "Somma Lombardo", "Gavirate", "Laveno-Mombello",
    "Luino", "Sesto Calende", "Samarate", "Lonate Pozzolo", "Fagnano Olona",
    "Castellanza", "Caronno Pertusella", "Gerenzano", "Origgio", "Uboldo",
    "Cislago", "Gorla Minore", "Gorla Maggiore", "Marnate", "Olgiate Olona",
    "Solbiate Olona", "Solbiate Arno", "Albizzate", "Cairate", "Carnago",
    "Caravate", "Besozzo", "Besnate", "Brebbia", "Bregano", "Brenta",
    "Bardello", "Biandronno", "Bodio Lomnago", "Buguggiate", "Casale Litta",
    "Casciago", "Castelseprio", "Castiglione Olona", "Cavaria con Premezzo",
    "Cazzago Brabbia", "Cislago", "Cittiglio", "Comabbio", "Comerio",
    "Cremenaga", "Cuasso al Monte", "Cugliate-Fabiasco", "Cunardo", "Curiglia",
    "Daverio", "Dumenza", "Duno", "Ferrera di Varese", "Gazzada Schianno",
    "Gemonio", "Gornate Olona", "Inarzo", "Induno Olona", "Ispra",
    "Jerago con Orago", "Lavena Ponte Tresa", "Lozza", "Maccagno",
    "Malgesso", "Marchirolo", "Marzio", "Masciago Primo", "Mercallo",
    "Montegrino Valtravaglia", "Morazzone", "Mornago", "Oggiona con Santo Stefano",
    "Porto Ceresio", "Porto Valtravaglia", "Rancio Valcuvia", "Saltrio",
    "Sangiano", "Travedona Monate", "Vedano Olona", "Venegono Inferiore",
    "Venegono Superiore", "Vergiate", "Viggiu"
]

VIE_STANDARD = [
    "Via Roma", "Via Garibaldi", "Via Matteotti", "Via Verdi",
    "Via Manzoni", "Via Milano", "Via Varese", "Via Dante",
    "Via Mazzini", "Via Cavour", "Corso Italia", "Piazza Libertà",
    "Via San Martino", "Via XXV Aprile", "Via IV Novembre",
    "Via Risorgimento", "Via Volta", "Via Marconi", "Via De Gasperi",
    "Viale Europa"
]


# ===== BASE 2032 + PATCH CSV COMUNE VIA - INIZIO =====
BASE_2032_PATHS = [
    "/mnt/data/base_2032.csv",
    "/mnt/data/base2032.csv",
    "base_2032.csv",
    "base2032.csv"
]
PATCH_PATHS = [
    "/mnt/data/patch_comune_via.csv",
    "/mnt/data/patch_comuni_vie.csv",
    "patch_comune_via.csv"
]

def load_base_2032_df():
    for p in BASE_2032_PATHS:
        if os.path.exists(p):
            try:
                df = pd.read_csv(p, dtype=str, keep_default_na=False)
                df.columns = [c.strip().lower() for c in df.columns]
                if 'comune' in df.columns:
                    return df
            except Exception as e:
                print(f"Errore lettura base {p}: {e}")
    return None

def load_patch_df():
    if "patch_df" in st.session_state and st.session_state.patch_df is not None:
        return st.session_state.patch_df
    for p in PATCH_PATHS:
        if os.path.exists(p):
            try:
                df = pd.read_csv(p, dtype=str, keep_default_na=False)
                df.columns = [c.strip().lower() for c in df.columns]
                if 'comune' in df.columns:
                    return df
            except:
                pass
    return None

def ui_patch_loader_sidebar():
    with st.sidebar.expander("🛠️ BASE 2032 + PATCH CSV", expanded=False):
        st.caption("CSV con colonne `comune,via` - sovrascrive base")
        up_base = st.file_uploader("BASE 2032 (opzionale)", type=["csv"], key="up_base_2032")
        if up_base:
            try:
                df = pd.read_csv(up_base, dtype=str, keep_default_na=False)
                df.to_csv("/mnt/data/base_2032.csv", index=False, encoding='utf-8-sig')
                st.success(f"Base 2032 caricata: {len(df)} righe")
                st.cache_data.clear()
            except Exception as e:
                st.error(f"Errore base: {e}")
        up_patch = st.file_uploader("PATCH comune via", type=["csv"], key="up_patch_comune_via")
        if up_patch:
            try:
                df = pd.read_csv(up_patch, dtype=str, keep_default_na=False)
                df.to_csv("/mnt/data/patch_comune_via.csv", index=False, encoding='utf-8-sig')
                df.columns = [c.strip().lower() for c in df.columns]
                st.session_state.patch_df = df
                st.success(f"Patch: {len(df)} righe - {df['comune'].nunique() if 'comune' in df.columns else '?'} comuni")
                st.cache_data.clear()
            except Exception as e:
                st.error(f"Errore patch: {e}")
        patch_df = load_patch_df()
        base_df = load_base_2032_df()
        c1,c2 = st.columns(2)
        with c1:
            st.metric("Base", f"{len(base_df) if base_df is not None else 0} righe")
        with c2:
            st.metric("Patch", f"{len(patch_df) if patch_df is not None else 0} righe")
        if patch_df is not None:
            st.dataframe(patch_df.head(20), use_container_width=True)
            if st.button("❌ Rimuovi patch", key="btn_remove_patch"):
                if os.path.exists("/mnt/data/patch_comune_via.csv"):
                    os.remove("/mnt/data/patch_comune_via.csv")
                st.session_state.patch_df = None
                st.cache_data.clear()
                st.rerun()
# ===== BASE 2032 + PATCH - FINE =====




def get_stato_color(stato):
    """
    Modifica 4: Colora fondo campo stato intervento emergenze
    Return bg, txt, label
    """
    bg_color = "#ffffff"
    txt_color = "#000000"
    label = stato

    if stato == "Operativo":
        bg_color = "#ff0000"
        txt_color = "white"
        label = "Operativo"
    elif stato == "In Corso":
        bg_color = "#ffff00"
        txt_color = "black"
        label = "In Corso"
    elif stato == "Completato":
        bg_color = "#00ff00"
        txt_color = "black"
        label = "Completato"
    elif stato == "Chiuso":
        bg_color = "#808080"
        txt_color = "white"
        label = "Chiuso"
    elif stato == "In Stand By":
        bg_color = "#ff8c00"
        txt_color = "white"
        label = "In Stand By"
    elif stato == "Sospeso":
        bg_color = "#87ceeb"
        txt_color = "black"
        label = "Sospeso"
    elif stato == "Annullato":
        bg_color = "#000000"
        txt_color = "white"
        label = "Annullato"
    elif stato == "In Attesa":
        bg_color = "#ffd700"
        txt_color = "black"
        label = "In Attesa"
    else:
        bg_color = "#ffffff"
        txt_color = "#000000"
        label = stato

    return bg_color, txt_color, label


def get_comuni():
    """
    BASE 2032 + PATCH CSV comune via
    Priorità: PATCH > BASE_2032.csv > GitHub > COMUNI_ITALIA
    """
    comuni_set = set()
    # 1. BASE 2032
    base_df = load_base_2032_df()
    if base_df is not None and 'comune' in base_df.columns:
        for c in base_df['comune'].dropna().unique():
            c = str(c).strip()
            if c:
                comuni_set.add(c)
    else:
        # GitHub come base 2032 online
        try:
            url = "https://raw.githubusercontent.com/matteocontrini/comuni-json/master/comuni.json"
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                for cc in data:
                    nome = cc.get("nome", "")
                    if nome:
                        comuni_set.add(nome)
        except:
            pass
        if not comuni_set:
            comuni_set.update(COMUNI_ITALIA)

    # 2. PATCH aggiunge comuni
    patch_df = load_patch_df()
    if patch_df is not None and 'comune' in patch_df.columns:
        for c in patch_df['comune'].dropna().unique():
            c = str(c).strip()
            if c:
                # normalizza titolo
                comuni_set.add(c)

    return sorted(list(comuni_set))


def get_vie(comune):
    """
    BASE 2032 + PATCH CSV comune via
    Priorità: PATCH per comune > BASE_2032 > Overpass > VIE_STANDARD
    """
    vie = []
    if not comune:
        return VIE_STANDARD
    comune_norm = comune.strip().lower()

    # 1. PATCH
    patch_df = load_patch_df()
    if patch_df is not None and 'comune' in patch_df.columns and 'via' in patch_df.columns:
        mask = patch_df['comune'].astype(str).str.strip().str.lower() == comune_norm
        vie_patch = patch_df[mask]['via'].dropna().astype(str).str.strip().unique().tolist()
        vie_patch = [v for v in vie_patch if v]
        if vie_patch:
            vie.extend(vie_patch)

    # 2. BASE 2032
    base_df = load_base_2032_df()
    if base_df is not None and 'comune' in base_df.columns and 'via' in base_df.columns:
        mask = base_df['comune'].astype(str).str.strip().str.lower() == comune_norm
        vie_base = base_df[mask]['via'].dropna().astype(str).str.strip().unique().tolist()
        for v in vie_base:
            if v not in vie:
                vie.append(v)
        if vie:
            return sorted(list(set(vie)))[:150]

    if vie:
        return sorted(list(set(vie)))[:150]

    # 3. Overpass API
    try:
        query = """
        [out:json][timeout:10];
        area["name"="%s"]->.a;
        way(area.a)["highway"]["name"];
        out tags;
        """ % comune
        overpass_url = "https://overpass-api.de/api/interpreter"
        resp = requests.get(
            overpass_url,
            params={"data": query},
            timeout=8
        )
        if resp.status_code == 200:
            data = resp.json()
            for el in data.get("elements", []):
                tags = el.get("tags", {})
                nome_via = tags.get("name", "")
                if nome_via and nome_via not in vie:
                    vie.append(nome_via)
            if len(vie) > 3:
                return sorted(vie[:80])
    except:
        pass

    pref = "Via " + comune
    custom = [pref + " Centro", pref + " Nord", pref + " Sud"]
    return VIE_STANDARD + custom


def combo_comune(label, key, default=""):
    """
    Selectbox COMUNI ITALIA con default
    """
    comuni_list = get_comuni()
    comuni_list = sorted(list(set(comuni_list)))

    if default and default not in comuni_list:
        comuni_list = [default] + comuni_list

    idx_default = 0
    if default:
        try:
            idx_default = comuni_list.index(default)
        except:
            idx_default = 0

    selected = st.selectbox(
        label,
        comuni_list,
        index=idx_default,
        key=key
    )
    return selected


def combo_vie(label, comune, key, default=""):
    """
    Se comune, get_vie e selectbox VIE DI COMUNE + checkbox via manuale
    """
    vie_list = []
    if comune:
        vie_list = get_vie(comune)
    else:
        vie_list = VIE_STANDARD

    vie_list = sorted(list(set(vie_list)))

    if default and default not in vie_list:
        vie_list = [default] + vie_list

    idx_default = 0
    if default:
        try:
            idx_default = vie_list.index(default)
        except:
            idx_default = 0

    col1, col2 = st.columns([3, 1])
    with col1:
        selected_via = st.selectbox(
            label,
            vie_list,
            index=idx_default,
            key=key
        )
    with col2:
        manuale = st.checkbox(
            "Via manuale",
            key=key + "_manuale_chk"
        )

    if manuale:
        via_manuale = st.text_input(
            "Inserisci via manuale",
            value=default if default else "",
            key=key + "_manuale_txt"
        )
        if via_manuale:
            return via_manuale
        else:
            return selected_via
    else:
        return selected_via


def to_excel(df):
    """
    Esporta DataFrame in Excel, esclude colonne binarie foto
    """
    buf = BytesIO()
    df_copy = df.copy()

    cols_to_exclude = [
        "FotoBytes",
        "FileBytes",
        "FotoConsegnaBytes",
        "Foto",
        "FotoBytesObj"
    ]

    for col in cols_to_exclude:
        if col in df_copy.columns:
            df_copy = df_copy.drop(columns=[col])

    try:
        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            df_copy.to_excel(writer, index=False, sheet_name="Dati")
        buf.seek(0)
        return buf.getvalue()
    except:
        buf2 = BytesIO()
        df_copy.to_csv(buf2, index=False)
        buf2.seek(0)
        return buf2.getvalue()


def to_excel_multi(datasets):
    """
    datasets = dict nome_sheet -> df
    """
    buf = BytesIO()
    try:
        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            for sheet_name, df in datasets.items():
                df_copy = df.copy()
                for col in ["FotoBytes", "FileBytes", "FotoConsegnaBytes", "Foto"]:
                    if col in df_copy.columns:
                        df_copy = df_copy.drop(columns=[col])
                safe_name = sheet_name[:30]
                df_copy.to_excel(writer, index=False, sheet_name=safe_name)
        buf.seek(0)
        return buf.getvalue()
    except:
        return to_excel(list(datasets.values())[0] if datasets else pd.DataFrame())


def to_pdf(df, tit):
    """
    Modifica 3: PDF con logo pc ana in intestazione e tabella estesa tutto foglio
    landscape A4 ~ 27cm utilizzabili
    """
    if not REPORTLAB_OK:
        buf_err = BytesIO()
        buf_err.write(f"Reportlab non installato - {tit}".encode("utf-8"))
        return buf_err.getvalue()

    buf = BytesIO()
    try:
        doc = SimpleDocTemplate(
            buf,
            pagesize=landscape(A4),
            leftMargin=1 * cm,
            rightMargin=1 * cm,
            topMargin=1.5 * cm,
            bottomMargin=1 * cm
        )
        styles = getSampleStyleSheet()
        story = []

        try:
            if os.path.exists("logo.png"):
                logo_img = Image("logo.png", width=80, height=80)
                story.append(logo_img)
                story.append(Spacer(1, 12))
        except:
            pass

        title_para = Paragraph(
            f"<b>{tit} - ANA Varese Protezione Civile</b>",
            styles["Title"]
        )
        story.append(title_para)
        story.append(Spacer(1, 12))

        date_para = Paragraph(
            f"Generato il {datetime.now().strftime('%d/%m/%Y %H:%M')} - Gestionale 950+ Modifiche Richieste",
            styles["Normal"]
        )
        story.append(date_para)
        story.append(Spacer(1, 12))

        if not df.empty:
            cols = list(df.columns)[:12]
            if len(cols) == 0:
                cols = ["Dato"]

            header = cols
            rows = []
            for _, r in df.iterrows():
                row_vals = []
                for c in cols:
                    try:
                        val = r.get(c, "")
                        sval = str(val)[:80]
                        sval = sval.replace("<", "").replace(">", "")
                        row_vals.append(sval)
                    except:
                        row_vals.append("")
                rows.append(row_vals)

            data = [header] + rows

            available_width = landscape(A4)[0] - 2 * cm
            col_width = available_width / len(cols) if cols else available_width
            col_widths = [col_width] * len(cols)

            t = Table(data, colWidths=col_widths, repeatRows=1)
            t.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1A5D1A")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, -1), 7),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#e8f5e9")]),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 3),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                        ("TOPPADDING", (0, 0), (-1, -1), 3),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                    ]
                )
            )
            story.append(t)
        else:
            story.append(
                Paragraph("Nessun dato disponibile", styles["Normal"])
            )

        doc.build(story)
        buf.seek(0)
        return buf.getvalue()
    except Exception as e:
        try:
            buf2 = BytesIO()
            doc2 = SimpleDocTemplate(buf2, pagesize=landscape(A4))
            styles2 = getSampleStyleSheet()
            story2 = []
            story2.append(Paragraph(f"{tit} - Errore PDF: {str(e)[:200]}", styles2["Title"]))
            doc2.build(story2)
            buf2.seek(0)
            return buf2.getvalue()
        except:
            return b"PDF ERROR"


def hdr():
    """
    columns 1,5 con logo.png 110 e div verde titolo GESTIONALE 950+ MODIFICHE RICHIESTE
    """
    c1, c2 = st.columns([1, 5])
    with c1:
        try:
            if os.path.exists("logo.png"):
                st.image("logo.png", width=110)
            else:
                st.markdown(
                    """
                    <div style="width:110px;height:110px;background:#1A5D1A;
                    border-radius:12px;display:flex;align-items:center;
                    justify-content:center;color:white;font-weight:bold;
                    font-size:40px;text-align:center;line-height:110px;">
                    ANA
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        except:
            st.markdown("**ANA**")

    with c2:
        st.markdown(
            """
            <div style="background:linear-gradient(135deg,#1A5D1A 0%,#2e7d32 100%);
            padding:18px 24px;border-radius:12px;color:white;
            border-left:6px solid #FFD700;">
                <h1 style="margin:0;font-family:Times New Roman;
                font-weight:bold;font-size:28px;color:white;">
                GESTIONALE 950+ MODIFICHE RICHIESTE - ANA Varese Protezione Civile
                </h1>
                <p style="margin:4px 0 0 0;font-size:14px;opacity:0.9;">
                Dashboard solo menu + tasti form | PDF logo + tabella estesa | Stato colorato | Click cognome per modifica | Login/Logout ripristinati | Fusione Mappe SI
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )


def hdr_form(t):
    """
    h2 Times New Roman bold black
    """
    st.markdown(
        f"""
        <h2 style="font-family:Times New Roman;
        font-weight:bold;color:black;
        border-bottom:3px solid #1A5D1A;
        padding-bottom:8px;margin-top:16px;">
        {t}
        </h2>
        """,
        unsafe_allow_html=True
    )


def init_session():
    defaults = {
        "page": "entra",
        "logged": False,
        "menu": "Dashboard",
        "volontari": [],
        "radio_db": [],
        "consegna_radio": [],
        "eventi": [],
        "emergenze": [],
        "checkin": [],
        "icone": [],
        "postazioni": [],
        "temp_markers": [],
        "brogliaccio": [],
        "mezzi": [],
        "attrezzature": [],
        "map_fullscreen": False,
        "vol_form_data": {},
        "alias_radio": [],
        "brog_evento_blindato": None,
        "brog_emergenza_blindata": None,
        "brog_blindato": False,
        "check_evento_blindato": None,
        "check_emergenza_blindata": None,
        "check_blindato": False,
        "interventi": [],
        "interventi_emergenza_blindata": None,
        "interventi_blindato": False,
        "chat": [],
        "tabella_interventi": [],
        "json_visualizzato": None,
        "posizioni_pd785": [],
        "posizioni_anytone": [],
        "vol_edit_index": None,
        "mappe": []
    }

    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


init_session()

# PAGINA ENTRA
if st.session_state.page == "entra":
    hdr()
    st.write("")
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        try:
            if os.path.exists("copertina.png"):
                st.image("copertina.png", width=350)
            else:
                st.markdown(
                    """
                    <div style="text-align:center;padding:40px;
                    background:linear-gradient(135deg,#e8f5e9,#c8e6c9);
                    border-radius:16px;border:2px dashed #1A5D1A;">
                    <div style="font-size:80px;">🛡️</div>
                    <p style="font-weight:bold;">Copertina ANA Varese</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        except:
            st.markdown("### ANA Varese")

        st.markdown(
            """
            <h2 style="text-align:center;font-family:Times New Roman;
            font-weight:bold;color:black;margin-top:20px;">
            GESTIONALE 950+ MODIFICHE 6 RICHIESTE
            </h2>
            <p style="text-align:center;">
            Versione finale con tutte le modifiche Ezio implementate
            </p>
            """,
            unsafe_allow_html=True
        )

        if st.button(
            "ENTRA NEL GESTIONALE",
            type="primary",
            use_container_width=True
        ):
            st.session_state.page = "login"
            st.rerun()

    st.stop()

# PAGINA LOGIN RIPRISTINATA - MODIFICA 6
if st.session_state.page == "login":
    hdr()
    st.write("")
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown(
            """
            <div style="background:white;padding:24px;
            border-radius:12px;box-shadow:0 4px 12px rgba(0,0,0,0.1);
            border-top:4px solid #1A5D1A;">
            <h3 style="font-family:Times New Roman;font-weight:bold;text-align:center;">
            LOGIN RIPRISTINATO - Modifica 6
            </h3>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.write("")
        utente = st.text_input("Utente", key="login_utente")
        pwd = st.text_input("Password", type="password", key="login_pwd")

        st.info("Demo: admin / ana2024")

        if st.button("Accedi", type="primary", use_container_width=True):
            if utente == "admin" and pwd == "ana2024":
                st.session_state.logged = True
                st.session_state.page = "dashboard"
                st.session_state.menu = "Dashboard"
                st.success("Accesso effettuato")
                st.rerun()
            else:
                st.error("Credenziali errate - Usa admin / ana2024")

        if st.button("Torna a Entra", use_container_width=True):
            st.session_state.page = "entra"
            st.rerun()

    st.stop()

# CONTROLLO LOGIN
if not st.session_state.logged:
    st.session_state.page = "login"
    st.rerun()

# SIDEBAR - MENU
with st.sidebar:
    try:
        if os.path.exists("logo.png"):
            st.image("logo.png", width=120)
        else:
            st.markdown(
                """
                <div style="width:120px;height:120px;background:#1A5D1A;
                border-radius:12px;display:flex;align-items:center;
                justify-content:center;color:white;font-weight:bold;font-size:28px;">
                ANA
                </div>
                """,
                unsafe_allow_html=True
            )
    except:
        st.write("ANA")

    st.markdown(
        """
        <p style="font-weight:bold;font-family:Times New Roman;
        margin-top:12px;color:#1A5D1A;">
        MENU 950+ MODIFICHE
        </p>
        """,
        unsafe_allow_html=True
    )

    menu_base = [
        "Dashboard",
        "Volontari (con foto)",
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

    cur = st.radio(
        "Seleziona form",
        menu_base,
        index=menu_base.index(st.session_state.menu) if st.session_state.menu in menu_base else 0,
        key="menu_radio"
    )
    st.session_state.menu = cur

    st.divider()

    # MODIFICA 6 - LOGOUT RIPRISTINATO
    if st.button("Logout", type="primary", use_container_width=True, key="logout_btn"):
        st.session_state.page = "entra"
        st.session_state.logged = False
        st.session_state.menu = "Dashboard"
        st.rerun()

    st.divider()
    st.markdown(
        """
        <div style="background:#e8f5e9;padding:12px;border-radius:8px;">
        <p style="font-size:12px;font-weight:bold;margin:0;">INFO RADIO HYTERA</p>
        <p style="font-size:11px;margin:4px 0 0 0;">
        PD785 - Anytone 878<br>
        Varese 950+ attivo<br>
        6 Modifiche implementate<br>
        Fusione Mappe: SI ottima idea
        </p>
        </div>
        """,
        unsafe_allow_html=True
    )

# DASHBOARD MODIFICATA RICHIESTA 1 e 2 - FULLSCREEN ROSSO + BOTTONI ON_CLICK
if cur == "Dashboard":
    hdr()
    hdr_form("Dashboard - Menu + Tasti Form")

    st.markdown(
        """
        <p style="font-family:Times New Roman;font-weight:bold;color:black;
        background:#fffde7;padding:12px;border-radius:8px;
        border-left:4px solid #FFD700;">
        Clicca su un tasto per aprire il form - Fullscreen rosso - Date gg/mm/aaaa
        </p>
        """,
        unsafe_allow_html=True
    )

    form_buttons = [
        ("Volontari (con foto)", "👤 Volontari"),
        ("DB Radio", "📻 DB Radio"),
        ("Consegna Radio", "🤝 Consegna Radio"),
        ("Alias Radio", "🔖 Alias Radio"),
        ("Brogliaccio", "📓 Brogliaccio"),
        ("Eventi", "📅 Eventi"),
        ("Emergenze", "🚨 Emergenze"),
        ("Check-in", "✅ Check-in"),
        ("Interventi Emergenza", "🚒 Interventi Emergenza"),
        ("Tabella Interventi Emergenza", "📋 Tabella Interventi"),
        ("Mezzi", "🚐 Mezzi"),
        ("Attrezzature", "🧰 Attrezzature"),
        ("Mappa Avanzata", "🌍 Mappa Avanzata"),
        ("Libreria Icone", "🎨 Libreria Icone"),
        ("Chat", "💬 Chat"),
        ("Geolocalizzazione Hytera + Anytone", "📡 Geoloc"),
        ("Backup", "💾 Backup")
    ]

    # TASTO ROSSO FULLSCREEN
    c_fs1, c_fs2 = st.columns([1,3])
    with c_fs1:
        if st.button("⛶ SCHERMO INTERO", key="btn_fullscreen_dash", use_container_width=True, type="primary"):
            st.session_state["fs_active"] = True
    with c_fs2:
        st.markdown('<span style="background:red;color:white;padding:6px 12px;border-radius:6px;font-weight:bold;">🔴 FULLSCREEN - ESC per uscire</span>', unsafe_allow_html=True)

    if st.session_state.get("fs_active"):
        st.components.v1.html(
            """
            <script>
            (function(){
                try {
                    const docEl = window.parent.document.documentElement;
                    if (docEl.requestFullscreen) docEl.requestFullscreen();
                } catch(e){}
                try {
                    if (document.documentElement.requestFullscreen) document.documentElement.requestFullscreen();
                } catch(e){}
            })();
            </script>
            <div style="background:#ff0000;color:white;padding:8px;border-radius:6px;text-align:center;font-weight:bold;">
            🔴 FULLSCREEN ATTIVO - premi ESC per uscire
            </div>
            """,
            height=70
        )
        if st.button("❌ Esci Fullscreen", key="btn_exit_fs", use_container_width=True):
            st.components.v1.html("<script>try{document.exitFullscreen(); parent.document.exitFullscreen();}catch(e){}</script>", height=0)
            st.session_state["fs_active"] = False
            st.rerun()

    st.write("")

    def vai_a_form_callback(form_name):
        st.session_state.menu = form_name
        st.session_state["menu_radio"] = form_name

    # CSS bottoni verde ANA
    st.markdown(
        """
        <style>
        /* Bottoni dashboard verde ANA */
        div[data-testid="column"] .stButton > button {
            background-color: #1A5D1A !important;
            color: white !important;
            border: 2px solid #1A5D1A !important;
            font-weight: bold !important;
            font-family: 'Times New Roman', serif !important;
        }
        div[data-testid="column"] .stButton > button:hover {
            background-color: #2e7d32 !important;
            border-color: #2e7d32 !important;
            color: white !important;
        }
        /* Tasto fullscreen rosso */
        button[kind="primary"] {
            background-color: #ff0000 !important;
            border-color: #ff0000 !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    cols = st.columns(3)
    for i, (menu_name, btn_label) in enumerate(form_buttons):
        col = cols[i % 3]
        with col:
            st.button(
                btn_label, 
                key=f"dash_btn_{i}_{menu_name}_FINAL", 
                use_container_width=True, 
                help=f"Vai a {menu_name}",
                on_click=vai_a_form_callback,
                args=(menu_name,)
            )

    st.divider()

    st.markdown(
        """
        <div style="background:linear-gradient(135deg,#e8f5e9,#c8e6c9);
        padding:16px;border-radius:12px;border:2px solid #1A5D1A;">
        <h4 style="margin:0;color:#1A5D1A;font-family:Times New Roman;">
        Fusione Emergenze+Eventi in Mappe: SI ottima idea - Ezio
        </h4>
        <p style="margin:8px 0 0 0;font-family:Times New Roman;font-weight:bold;color:black;">
        Già creato form Mappa Avanzata OLD RIMOSSO con Tipo Emergenza/Evento + mappa unica.
        Unico form georeferenziato, filtri per Tipo, priorità e stato colorato.
        Soluzione ottimale per gestione unificata.
        </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Statistiche semplici
    st.write("")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Volontari", len(st.session_state.volontari))
    with c2:
        st.metric("Radio DB", len(st.session_state.radio_db))
    with c3:
        st.metric("Emergenze", len(st.session_state.emergenze))
    with c4:
        st.metric("Mappa Avanzata", len(st.session_state.mappe))

# VOLONTARI FORM CON SOTTOMASCHERE A LINGUETTE + CAMPO ODV - NUOVA VERSIONE FINALE
elif cur == "Volontari (con foto)":
    hdr()
    hdr_form("VOLONTARI - Sottomaschere a Linguette + ODV")

    edit_mode = False
    edit_data = {}
    if st.session_state.vol_edit_index is not None:
        try:
            edit_data = st.session_state.volontari[st.session_state.vol_edit_index]
            edit_mode = True
        except:
            edit_data = {}
            edit_mode = False

    if edit_mode:
        st.warning(f"✏️ Modifica: {edit_data.get('Nome','')} {edit_data.get('Cognome','')} - Capo ODV: {edit_data.get('CapoODV','')}")

    # SOTTOMASCHERE A LINGUETTE - 6 TAB
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📋 Anagrafica", "📞 Contatti", "🛡️ Ruolo", "📻 Dotazione", "📄 Documenti", "📸 Foto"])

    # Valori default da edit
    nome_def = edit_data.get("Nome", "")
    cognome_def = edit_data.get("Cognome", "")
    comune_def = edit_data.get("Comune", "Varese")
    via_def = edit_data.get("Via", "")
    capo_odv_def = edit_data.get("CapoODV", "")
    odv_app_def = edit_data.get("ODVAppartenenza", "ANA Varese")
    cell_def = edit_data.get("Cellulare", "")
    email_def = edit_data.get("Email", "")
    tel_em_def = edit_data.get("TelEmergenza", "")
    ruolo_def = edit_data.get("Ruolo", "Volontario")
    squadra_def = edit_data.get("Squadra", "Squadra A")
    radio_id_def = edit_data.get("RadioID", "")
    doc_def = edit_data.get("Documento", "")
    scad_def = edit_data.get("ScadDoc", "")

    with tab1:
        st.markdown("#### 📋 Anagrafica + Capo ODV")
        c1, c2 = st.columns(2)
        with c1:
            nome = st.text_input("Nome *", value=nome_def, key="vol_nome_tab")
            cognome = st.text_input("Cognome *", value=cognome_def, key="vol_cognome_tab")
            comune_res = combo_comune("Comune Residenza", "vol_comune_tab", comune_def)
            via = combo_vie("Via", comune_res, "vol_via_tab", via_def)
        with c2:
            capo_odv = st.text_input("Capo ODV *", value=capo_odv_def, key="vol_capo_odv", help="Nome del Capo ODV di riferimento")
            odv_app = st.selectbox("ODV Associazione di Appartenenza *", ["ANA Varese", "ANA Milano", "ANA Como", "Protezione Civile Varese", "Altro"], index=0, key="vol_odv_app")
            if odv_app == "Altro":
                odv_app_custom = st.text_input("Specifica ODV", value=odv_app_def if odv_app_def not in ["ANA Varese", "ANA Milano", "ANA Como", "Protezione Civile Varese"] else "", key="vol_odv_custom")
                if odv_app_custom:
                    odv_app = odv_app_custom
            data_nascita = st.date_input("Data Nascita", value=date(1990,1,1), format="DD/MM/YYYY", key="vol_data_nasc")
            codice_fisc = st.text_input("Codice Fiscale", value=edit_data.get("CodFisc",""), key="vol_cf")

    with tab2:
        st.markdown("#### 📞 Contatti")
        c1, c2 = st.columns(2)
        with c1:
            cellulare = st.text_input("Cellulare *", value=cell_def, key="vol_cell_tab")
            email = st.text_input("Email", value=email_def, key="vol_email_tab")
        with c2:
            tel_emerg = st.text_input("Telefono Emergenza", value=tel_em_def, key="vol_tel_em")
            note_cont = st.text_area("Note Contatti", value=edit_data.get("NoteContatti",""), key="vol_note_cont")

    with tab3:
        st.markdown("#### 🛡️ Ruolo e Squadra")
        c1, c2 = st.columns(2)
        with c1:
            ruolo = st.selectbox("Ruolo *", ["Volontario", "Capo Squadra", "Coordinatore", "Autista", "Radio Operatore", "Capo ODV", "Vice Capo ODV"], index=["Volontario", "Capo Squadra", "Coordinatore", "Autista", "Radio Operatore", "Capo ODV", "Vice Capo ODV"].index(ruolo_def) if ruolo_def in ["Volontario", "Capo Squadra", "Coordinatore", "Autista", "Radio Operatore", "Capo ODV", "Vice Capo ODV"] else 0, key="vol_ruolo_tab")
            squadra = st.selectbox("Squadra *", ["Squadra A", "Squadra B", "Squadra C", "Logistica", "Segreteria", "ODV Centrale"], index=["Squadra A", "Squadra B", "Squadra C", "Logistica", "Segreteria", "ODV Centrale"].index(squadra_def) if squadra_def in ["Squadra A", "Squadra B", "Squadra C", "Logistica", "Segreteria", "ODV Centrale"] else 0, key="vol_squadra_tab")
        with c2:
            data_iscriz = st.date_input("Data Iscrizione ODV", value=date.today(), format="DD/MM/YYYY", key="vol_data_iscr")
            stato_vol = st.selectbox("Stato", ["Attivo", "Inattivo", "In Formazione", "Sospeso"], key="vol_stato")

    with tab4:
        st.markdown("#### 📻 Dotazione Radio")
        radio_id = st.text_input("ID Radio / Matricola", value=radio_id_def, key="vol_radio_id")
        modello_radio = st.selectbox("Modello Radio", ["Hytera PD785", "Anytone 878", "Motorola", "Altro"], key="vol_radio_mod")
        note_dot = st.text_area("Note Dotazione", value=edit_data.get("NoteDotazione",""), key="vol_note_dot")

    with tab5:
        st.markdown("#### 📄 Documenti")
        doc_tipo = st.text_input("Tipo Documento", value=doc_def, key="vol_doc_tipo")
        doc_num = st.text_input("Numero Documento", value=edit_data.get("DocNum",""), key="vol_doc_num")
        doc_scad = st.date_input("Scadenza Documento", value=date.today(), format="DD/MM/YYYY", key="vol_doc_scad")
        st.caption("Formato data gg/mm/aaaa - es: 23/09/2026")

    with tab6:
        st.markdown("#### 📸 Foto Volontario")
        foto_file = st.file_uploader("Carica foto", type=["jpg", "jpeg", "png"], key="vol_foto_tab")
        foto_preview = None
        if foto_file:
            foto_bytes = foto_file.getvalue()
            st.image(foto_bytes, width=150, caption="Preview")
            foto_preview = foto_bytes
        elif edit_mode and edit_data.get("FotoBytes"):
            try:
                st.image(edit_data.get("FotoBytes"), width=150, caption="Foto esistente")
                foto_preview = edit_data.get("FotoBytes")
            except:
                pass

    st.divider()

    col_btn1, col_btn2, col_btn3 = st.columns([1,1,2])
    if edit_mode:
        with col_btn1:
            if st.button("🔄 AGGIORNA VOLONTARIO", type="primary", use_container_width=True):
                if nome and cognome and cellulare and capo_odv:
                    updated = {
                        "Nome": nome,
                        "Cognome": cognome,
                        "Comune": comune_res,
                        "Via": via,
                        "CapoODV": capo_odv,
                        "ODVAppartenenza": odv_app,
                        "DataNascita": str(data_nascita),
                        "CodFisc": codice_fisc,
                        "Cellulare": cellulare,
                        "Email": email,
                        "TelEmergenza": tel_emerg,
                        "Ruolo": ruolo,
                        "Squadra": squadra,
                        "RadioID": radio_id,
                        "ModelloRadio": modello_radio,
                        "Documento": doc_tipo,
                        "DocNum": doc_num,
                        "ScadDoc": str(doc_scad),
                        "FotoBytes": foto_preview,
                        "DataAgg": datetime.now().strftime("%d/%m/%Y %H:%M")
                    }
                    st.session_state.volontari[st.session_state.vol_edit_index] = updated
                    st.session_state.vol_edit_index = None
                    st.success("Volontario aggiornato con ODV OK")
                    st.rerun()
                else:
                    st.error("Compila Nome, Cognome, Cellulare e Capo ODV *")
        with col_btn2:
            if st.button("❌ ANNULLA", use_container_width=True):
                st.session_state.vol_edit_index = None
                st.rerun()
    else:
        with col_btn1:
            if st.button("💾 SALVA VOLONTARIO", type="primary", use_container_width=True):
                if nome and cognome and cellulare and capo_odv:
                    nuovo = {
                        "Nome": nome,
                        "Cognome": cognome,
                        "Comune": comune_res,
                        "Via": via,
                        "CapoODV": capo_odv,
                        "ODVAppartenenza": odv_app,
                        "DataNascita": str(data_nascita),
                        "CodFisc": codice_fisc,
                        "Cellulare": cellulare,
                        "Email": email,
                        "TelEmergenza": tel_emerg,
                        "Ruolo": ruolo,
                        "Squadra": squadra,
                        "RadioID": radio_id,
                        "ModelloRadio": modello_radio,
                        "Documento": doc_tipo,
                        "DocNum": doc_num,
                        "ScadDoc": str(doc_scad),
                        "FotoBytes": foto_preview,
                        "DataIns": datetime.now().strftime("%d/%m/%Y %H:%M")
                    }
                    st.session_state.volontari.append(nuovo)
                    st.success(f"Volontario {cognome} {nome} - Capo ODV {capo_odv} salvato!")
                    st.rerun()
                else:
                    st.error("Compila campi obbligatori * (Nome, Cognome, Cellulare, Capo ODV)")

    # Tabella volontari con click cognome per modifica
    st.divider()
    if st.session_state.volontari:
        st.markdown(f"#### Elenco Volontari ({len(st.session_state.volontari)}) - Clicca cognome per modifica")
        df_vol = pd.DataFrame([{k:v for k,v in vol.items() if "Bytes" not in k} for vol in st.session_state.volontari])
        # Mostra con colonne importanti
        cols_show = ["Cognome", "Nome", "CapoODV", "ODVAppartenenza", "Comune", "Cellulare", "Ruolo", "Squadra"]
        cols_show = [c for c in cols_show if c in df_vol.columns]
        st.dataframe(df_vol[cols_show] if cols_show else df_vol, use_container_width=True)

        # Click cognome per modifica - selectbox
        cognomi = [f"{i}: {v.get('Cognome','')} {v.get('Nome','')} - ODV {v.get('ODVAppartenenza','')} - Capo {v.get('CapoODV','')}" for i, v in enumerate(st.session_state.volontari)]
        sel = st.selectbox("Seleziona volontario per modifica", ["--"] + cognomi, key="sel_vol_mod")
        if sel != "--":
            try:
                idx = int(sel.split(":")[0])
                st.session_state.vol_edit_index = idx
                st.rerun()
            except:
                pass
    else:
        st.info("Nessun volontario inserito")

    st.divider()

# DB RADIO
elif cur == "DB Radio":
    hdr()
    hdr_form("DB RADIO - Gestione Apparati")

    c1, c2, c3 = st.columns(3)
    with c1:
        modello = st.selectbox("Modello Radio", ["Hytera PD785", "Anytone 878", "Motorola", "Altro"], key="radio_modello")
        matricola = st.text_input("Matricola / ID", key="radio_mat")
        freq = st.text_input("Frequenza", value="430.000", key="radio_freq")

    with c2:
        alias_r = st.text_input("Alias Radio", key="radio_alias")
        stato_r = st.selectbox("Stato Radio", ["Operativa", "In Manutenzione", "Fuori Servizio", "Assegnata"], key="radio_stato")
        note_r = st.text_area("Note", key="radio_note")

    with c3:
        st.write("Foto Radio")
        foto_r = st.file_uploader("Foto", type=["jpg", "png"], key="radio_foto")
        if foto_r:
            st.image(foto_r.getvalue(), width=100)

    if st.button("Salva Radio in DB", type="primary", use_container_width=True):
        if matricola:
            st.session_state.radio_db.append({
                "Modello": modello,
                "Matricola": matricola,
                "Frequenza": freq,
                "Alias": alias_r,
                "Stato": stato_r,
                "Note": note_r,
                "Data": datetime.now().strftime("%d/%m/%Y")
            })
            st.success("Radio salvata")
            st.rerun()

    if st.session_state.radio_db:
        df_r = pd.DataFrame(st.session_state.radio_db)
        st.dataframe(df_r, use_container_width=True)
        st.download_button("Excel Radio", to_excel(df_r), "radio_db.xlsx", use_container_width=True)
        if REPORTLAB_OK:
            st.download_button("PDF Logo Estesa", to_pdf(df_r, "DB RADIO"), "radio_db.pdf", use_container_width=True)

# CONSEGNA RADIO
elif cur == "Consegna Radio":
    hdr()
    hdr_form("CONSEGNA RADIO - Tracciamento")

    c1, c2 = st.columns(2)
    with c1:
        vol_list = [f"{v.get('Cognome','')} {v.get('Nome','')}" for v in st.session_state.volontari]
        if vol_list:
            sel_vol = st.selectbox("Volontario", vol_list, key="cons_vol")
        else:
            sel_vol = st.text_input("Volontario (manuale)", key="cons_vol_man")

        radio_list = [f"{r.get('Matricola','')} - {r.get('Modello','')}" for r in st.session_state.radio_db]
        if radio_list:
            sel_radio = st.selectbox("Radio", radio_list, key="cons_radio")
        else:
            sel_radio = st.text_input("Radio manuale", key="cons_radio_man")

    with c2:
        data_cons = st.date_input("Data Consegna", value=date.today(), format="DD/MM/YYYY", key="cons_data")
        ora_cons = st.time_input("Ora", value=datetime.now().time(), key="cons_ora")
        motivo = st.text_input("Motivo / Evento", key="cons_motivo")

    if st.button("Registra Consegna", type="primary", use_container_width=True):
        st.session_state.consegna_radio.append({
            "Volontario": sel_vol,
            "Radio": sel_radio,
            "Data": str(data_cons),
            "Ora": str(ora_cons),
            "Motivo": motivo,
            "Stato": "Consegnata"
        })
        st.success("Consegna registrata")
        st.rerun()

    if st.session_state.consegna_radio:
        df_cr = pd.DataFrame(st.session_state.consegna_radio)
        st.dataframe(df_cr, use_container_width=True)
        st.download_button("Excel Consegne", to_excel(df_cr), "consegne.xlsx", use_container_width=True)
        if REPORTLAB_OK:
            st.download_button("PDF Logo Estesa", to_pdf(df_cr, "CONSEGNA RADIO"), "consegne.pdf", use_container_width=True)

# ALIAS RADIO
elif cur == "Alias Radio":
    hdr()
    hdr_form("ALIAS RADIO - Gestione Alias")

    c1, c2 = st.columns(2)
    with c1:
        alias_n = st.text_input("Alias", key="alias_n")
        id_r = st.text_input("ID Radio", key="alias_id")

    with c2:
        gruppo = st.selectbox("Gruppo", ["Squadra A", "Squadra B", "Squadra C", "Coordinamento", "Logistica"], key="alias_gruppo")
        desc = st.text_input("Descrizione", key="alias_desc")

    if st.button("Salva Alias", type="primary", use_container_width=True):
        if alias_n and id_r:
            st.session_state.alias_radio.append({
                "Alias": alias_n,
                "ID Radio": id_r,
                "Gruppo": gruppo,
                "Descrizione": desc
            })
            st.success("Alias salvato")
            st.rerun()

    if st.session_state.alias_radio:
        df_al = pd.DataFrame(st.session_state.alias_radio)
        st.dataframe(df_al, use_container_width=True)
        st.download_button("Excel Alias", to_excel(df_al), "alias.xlsx", use_container_width=True)

# BROGLIACCIO
elif cur == "Brogliaccio":
    hdr()
    hdr_form("BROGLIACCIO - Registro Operativo")

    c1, c2 = st.columns(2)
    with c1:
        data_b = st.date_input("Data", value=date.today(), format="DD/MM/YYYY", key="brog_data")
        ora_b = st.time_input("Ora", value=datetime.now().time(), key="brog_ora")
        operatore = st.text_input("Operatore", key="brog_op")

    with c2:
        evento_b = st.text_input("Evento Riferimento", key="brog_evento")
        emerg_b = st.text_input("Emergenza Riferimento", key="brog_emerg")
        blindato = st.checkbox("Blinda Evento/Emergenza", key="brog_blind")

    testo_b = st.text_area("Testo Brogliaccio *", height=150, key="brog_testo")

    if st.button("Salva Brogliaccio", type="primary", use_container_width=True):
        if testo_b:
            st.session_state.brogliaccio.append({
                "Data": str(data_b),
                "Ora": str(ora_b),
                "Operatore": operatore,
                "Evento": evento_b,
                "Emergenza": emerg_b,
                "Testo": testo_b,
                "Blindato": blindato
            })
            st.success("Brogliaccio salvato")
            st.rerun()

    if st.session_state.brogliaccio:
        df_br = pd.DataFrame(st.session_state.brogliaccio)
        st.dataframe(df_br, use_container_width=True)
        st.download_button("Excel Brogliaccio", to_excel(df_br), "brogliaccio.xlsx", use_container_width=True)
        if REPORTLAB_OK:
            st.download_button("PDF Logo Estesa", to_pdf(df_br, "BROGLIACCIO"), "brogliaccio.pdf", use_container_width=True)

# EVENTI
elif cur == "Eventi":
    hdr()
    hdr_form("EVENTI - Gestione Eventi Programmati")

    c1, c2, c3 = st.columns(3)
    with c1:
        nome_ev = st.text_input("Nome Evento *", key="ev_nome")
        tipo_ev = st.selectbox("Tipo Evento", ["Esercitazione", "Manifestazione", "Formazione", "Riunione", "Altro"], key="ev_tipo")
        data_ev = st.date_input("Data Evento", value=date.today(), format="DD/MM/YYYY", key="ev_data")

    with c2:
        comune_ev = combo_comune("Comune Evento", "ev_comune", "Varese")
        via_ev = combo_vie("Via Evento", comune_ev, "ev_via", "")
        ora_ev = st.time_input("Ora Inizio", value=time(9, 0), key="ev_ora")

    with c3:
        resp_ev = st.text_input("Responsabile", key="ev_resp")
        stato_ev = st.selectbox("Stato", ["Programmato", "In Corso", "Completato", "Annullato"], key="ev_stato")
        note_ev = st.text_area("Note Evento", key="ev_note")

    if st.button("Salva Evento", type="primary", use_container_width=True):
        if nome_ev:
            st.session_state.eventi.append({
                "Nome": nome_ev,
                "Tipo": tipo_ev,
                "Data": str(data_ev),
                "Comune": comune_ev,
                "Via": via_ev,
                "Ora": str(ora_ev),
                "Responsabile": resp_ev,
                "Stato": stato_ev,
                "Note": note_ev
            })
            st.success("Evento salvato")
            st.rerun()

    if st.session_state.eventi:
        df_ev = pd.DataFrame(st.session_state.eventi)
        st.dataframe(df_ev, use_container_width=True)
        st.download_button("Excel Eventi", to_excel(df_ev), "eventi.xlsx", use_container_width=True)
        if REPORTLAB_OK:
            st.download_button("PDF Logo Estesa", to_pdf(df_ev, "EVENTI"), "eventi.pdf", use_container_width=True)

# EMERGENZE
elif cur == "Emergenze":
    hdr()
    hdr_form("EMERGENZE - Gestione Emergenze Attive")

    c1, c2, c3 = st.columns(3)
    with c1:
        nome_em = st.text_input("Nome Emergenza *", key="em_nome")
        tipo_em = st.selectbox("Tipo Emergenza", ["Alluvione", "Incendio", "Frana", "Neve", "Ricerca Persona", "Altro"], key="em_tipo")
        data_em = st.date_input("Data Emergenza", value=date.today(), format="DD/MM/YYYY", key="em_data")

    with c2:
        comune_em = combo_comune("Comune Emergenza", "em_comune", "Varese")
        via_em = combo_vie("Via Emergenza", comune_em, "em_via", "")
        prior_em = st.selectbox("Priorità", ["Bassa", "Media", "Alta", "Critica"], key="em_prior")

    with c3:
        stato_em = st.selectbox("Stato", ["Operativo", "In Corso", "Completato", "Chiuso"], key="em_stato")
        bg_c, txt_c, lab_c = get_stato_color(stato_em)
        st.markdown(
            f"""
            <div style="background:{bg_c};color:{txt_c};padding:10px;
            border-radius:8px;text-align:center;font-weight:bold;
            border:2px solid black;margin-top:8px;">
            STATO: {lab_c}
            </div>
            """,
            unsafe_allow_html=True
        )
        coord_em = st.text_input("Coordinate", placeholder="45.81, 8.82", key="em_coord")

    note_em = st.text_area("Descrizione Emergenza", key="em_note")

    if st.button("Salva Emergenza", type="primary", use_container_width=True):
        if nome_em:
            st.session_state.emergenze.append({
                "Nome": nome_em,
                "Tipo": tipo_em,
                "Data": str(data_em),
                "Comune": comune_em,
                "Via": via_em,
                "Priorita": prior_em,
                "Stato": stato_em,
                "StatoColoreBg": bg_c,
                "StatoColoreTxt": txt_c,
                "Coordinate": coord_em,
                "Note": note_em
            })
            st.success("Emergenza salvata")
            st.rerun()

    if st.session_state.emergenze:
        df_em = pd.DataFrame(st.session_state.emergenze)
        st.dataframe(df_em, use_container_width=True)
        st.download_button("Excel Emergenze", to_excel(df_em), "emergenze.xlsx", use_container_width=True)
        if REPORTLAB_OK:
            st.download_button("PDF Logo Estesa", to_pdf(df_em, "EMERGENZE"), "emergenze.pdf", use_container_width=True)

# MAPPE (Emergenze+Eventi) FUSIONE - SI OTTIMA IDEA
elif cur == "# RIMOSSO":
    hdr()
    hdr_form("MAPPE - Fusione Emergenze + Eventi - Proposta Ezio - SI OTTIMA IDEA")

    st.markdown(
        """
        <div style="background:linear-gradient(135deg,#e3f2fd,#bbdefb);
        padding:16px;border-radius:12px;border:2px solid #1976d2;
        margin-bottom:16px;">
        <h4 style="margin:0;color:#0d47a1;">Fusione Emergenze+Eventi in Mappe: SI ottima idea</h4>
        <p style="margin:8px 0 0 0;color:black;">
        Unico form georeferenziato con Tipo Emergenza/Evento, filtri, priorità e stato colorato.
        Soluzione ottimale approvata - gestione unificata su mappa unica.
        </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        tipo_mappa = st.selectbox("Tipo Mappa *", ["Emergenza", "Evento"], key="mappa_tipo")
        nome_mappa = st.text_input("Nome / Titolo *", key="mappa_nome")
        data_mappa = st.date_input("Data", value=date.today(), format="DD/MM/YYYY", key="mappa_data")

    with c2:
        comune_mappa = combo_comune("Comune", "mappa_comune", "Varese")
        via_mappa = combo_vie("Via", comune_mappa, "mappa_via", "")
        prior_mappa = st.selectbox("Priorità", ["Bassa", "Media", "Alta", "Critica"], key="mappa_prior")

    with c3:
        stato_mappa = st.selectbox(
            "STATO *",
            ["Operativo", "In Corso", "Completato", "Chiuso", "In Stand By", "Sospeso", "Annullato", "In Attesa"],
            key="stato_mappa_fusione"
        )
        bg_m, txt_m, lab_m = get_stato_color(stato_mappa)
        st.markdown(
            f"""
            <div style="background:{bg_m};color:{txt_m};padding:12px;
            border-radius:8px;text-align:center;font-weight:bold;
            border:3px solid black;margin-top:8px;">
            STATO SELEZIONATO: {lab_m} - Fondo campo colorato come richiesto Modifica 4
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown(
            f"""
            <style>
            div[data-testid='stSelectbox']:has(#stato_mappa_fusione) div[data-baseweb='select'] {{
                background-color:{bg_m} !important;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )

    c4, c5 = st.columns(2)
    with c4:
        lat_mappa = st.text_input("Latitudine", value="45.8167", key="mappa_lat")
        lon_mappa = st.text_input("Longitudine", value="8.8333", key="mappa_lon")
        icona_mappa = st.selectbox("Icona", ["🚨", "📅", "🚒", "⛑️", "📍", "⚠️"], key="mappa_icona")

    with c5:
        desc_mappa = st.text_area("Descrizione", key="mappa_desc")
        note_mappa = st.text_area("Note Coordinate", key="mappa_note")

    if st.button("Salva in Mappa Avanzata", type="primary", use_container_width=True):
        if nome_mappa:
            st.session_state.mappe.append({
                "Tipo": tipo_mappa,
                "Nome": nome_mappa,
                "Data": str(data_mappa),
                "Comune": comune_mappa,
                "Via": via_mappa,
                "Priorita": prior_mappa,
                "Stato": stato_mappa,
                "StatoBg": bg_m,
                "StatoTxt": txt_m,
                "Lat": lat_mappa,
                "Lon": lon_mappa,
                "Icona": icona_mappa,
                "Descrizione": desc_mappa,
                "Note": note_mappa
            })
            st.success("Mappa salvata - Fusione OK")
            st.rerun()

    if st.session_state.mappe:
        st.divider()
        st.markdown("**Riepilogo Mappa Avanzata con Filtri Tipo**")
        filtro_tipo = st.selectbox("Filtra per Tipo", ["Tutti", "Emergenza", "Evento"], key="filtro_mappa_tipo")
        df_map = pd.DataFrame(st.session_state.mappe)
        if filtro_tipo != "Tutti":
            df_map = df_map[df_map["Tipo"] == filtro_tipo]

        st.dataframe(df_map, use_container_width=True)

        # Mappa semplice con st.map se coordinate valide
        try:
            map_df = pd.DataFrame([
                {"lat": float(m.get("Lat", 0)), "lon": float(m.get("Lon", 0))}
                for m in st.session_state.mappe
                if m.get("Lat") and m.get("Lon")
            ])
            if not map_df.empty:
                st.map(map_df)
        except:
            st.info("Mappa coordinate non disponibili per visualizzazione")

        st.download_button("Excel Mappa Avanzata", to_excel(df_map), "mappe_fusione.xlsx", use_container_width=True)
        if REPORTLAB_OK:
            st.download_button("PDF Logo Estesa Tutto Foglio", to_pdf(df_map, "MAPPE FUSIONE EMERGENZE+EVENTI"), "mappe_fusione.pdf", use_container_width=True)

# CHECK-IN
elif cur == "Mappe":
    hdr()
    hdr_form("MAPPE - Form Completo")
    c1, c2 = st.columns(2)
    with c1:
        tipo_mappa = st.selectbox("Tipo Mappa *", ["Emergenza", "Evento"], key="mappa_tipo_old2")
        nome_mappa = st.text_input("Nome / Titolo *", key="mappa_nome_old2")
    with c2:
        comune_mappa = combo_comune("Comune", "mappa_comune_old2", "Varese")
        via_mappa = combo_vie("Via", comune_mappa, "mappa_via_old2", "")
        lat_mappa = st.text_input("Latitudine", value="45.8167", key="mappa_lat_old2")
        lon_mappa = st.text_input("Longitudine", value="8.8333", key="mappa_lon_old2")
    if st.button("Salva in Mappe", type="primary", use_container_width=True):
        if nome_mappa:
            st.session_state.mappe.append({"Tipo": tipo_mappa, "Nome": nome_mappa, "Comune": comune_mappa, "Via": via_mappa, "Lat": lat_mappa, "Lon": lon_mappa})
            st.success("Salvata")
            st.rerun()
    if st.session_state.mappe:
        st.dataframe(pd.DataFrame(st.session_state.mappe), use_container_width=True)

elif cur == "Check-in":
    hdr()
    hdr_form("CHECK-IN - Presenze Operative")

    c1, c2 = st.columns(2)
    with c1:
        vol_check_list = [f"{v.get('Cognome','')} {v.get('Nome','')}" for v in st.session_state.volontari]
        if vol_check_list:
            sel_check_vol = st.selectbox("Volontario", vol_check_list, key="check_vol")
        else:
            sel_check_vol = st.text_input("Volontario", key="check_vol_man")

        ev_check_list = [e.get("Nome", "") for e in st.session_state.eventi]
        em_check_list = [em.get("Nome", "") for em in st.session_state.emergenze]
        all_ref = ev_check_list + em_check_list
        if all_ref:
            sel_check_ref = st.selectbox("Evento/Emergenza", all_ref, key="check_ref")
        else:
            sel_check_ref = st.text_input("Evento/Emergenza", key="check_ref_man")

    with c2:
        data_check = st.date_input("Data Check-in", value=date.today(), format="DD/MM/YYYY", key="check_data")
        ora_check = st.time_input("Ora Check-in", value=datetime.now().time(), key="check_ora")
        stato_check = st.selectbox("Stato", ["Presente", "Assente", "Ritardo"], key="check_stato")

    if st.button("Registra Check-in", type="primary", use_container_width=True):
        st.session_state.checkin.append({
            "Volontario": sel_check_vol,
            "Riferimento": sel_check_ref,
            "Data": str(data_check),
            "Ora": str(ora_check),
            "Stato": stato_check
        })
        st.success("Check-in registrato")
        st.rerun()

    if st.session_state.checkin:
        df_ch = pd.DataFrame(st.session_state.checkin)
        st.dataframe(df_ch, use_container_width=True)
        st.download_button("Excel Check-in", to_excel(df_ch), "checkin.xlsx", use_container_width=True)

# INTERVENTI EMERGENZA - MODIFICA 4 STATO COLORE FONDO CAMPO
elif cur == "Interventi Emergenza":
    hdr()
    hdr_form("INTERVENTI EMERGENZA - Modifica 4 Stato Colore Fondo Campo")

    st.markdown(
        """
        <p style="font-family:Times New Roman;font-weight:bold;color:black;
        background:#e8f5e9;padding:8px;border-radius:6px;">
        Modifica 4: Campo Stato con fondo colorato come richiesto
        </p>
        """,
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        tipo_int = st.selectbox("Tipo Intervento", ["Soccorso", "Logistica", "Monitoraggio", "Bonifica", "Altro"], key="int_tipo")
        squadra_int = st.selectbox("Squadra", ["Squadra A", "Squadra B", "Squadra C", "Logistica"], key="int_squadra")
        data_int = st.date_input("Data Intervento", value=date.today(), format="DD/MM/YYYY", key="int_data")

    with c2:
        comune_int = combo_comune("Comune Intervento", "int_comune", "Varese")
        via_int = combo_vie("Via Intervento", comune_int, "int_via", "")
        ora_int = st.time_input("Ora Intervento", value=datetime.now().time(), key="int_ora")

    with c3:
        # MODIFICA 4 - STATO CON COLORE FONDO CAMPO
        stato_int = st.selectbox(
            "STATO *",
            ["Operativo", "In Corso", "Completato", "Chiuso", "In Stand By", "Sospeso", "Annullato", "In Attesa"],
            key="stato_int"
        )
        bg_color, txt_color, label = get_stato_color(stato_int)

        st.markdown(
            f"""
            <div style="background-color:{bg_color};color:{txt_color};
            padding:15px;border:3px solid black;border-radius:8px;
            text-align:center;font-weight:bold;font-size:16px;
            margin-top:10px;box-shadow:0 2px 8px rgba(0,0,0,0.3);">
            STATO SELEZIONATO: {label}<br>
            Fondo campo colorato come richiesto - Modifica 4
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <style>
            div[data-testid='stSelectbox'] div[data-baseweb='select'] {{
                transition: all 0.3s ease;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )

    desc_int = st.text_area("Descrizione Intervento *", key="int_desc")
    mezzi_int = st.text_input("Mezzi Utilizzati", key="int_mezzi")
    volontari_int = st.text_input("Volontari Coinvolti", key="int_vol")

    if st.button("Salva Intervento Emergenza", type="primary", use_container_width=True):
        if desc_int:
            st.session_state.interventi.append({
                "Tipo": tipo_int,
                "Squadra": squadra_int,
                "Data": str(data_int),
                "Comune": comune_int,
                "Via": via_int,
                "Ora": str(ora_int),
                "Stato": stato_int,
                "StatoColoreBg": bg_color,
                "StatoColoreTxt": txt_color,
                "Descrizione": desc_int,
                "Mezzi": mezzi_int,
                "Volontari": volontari_int
            })
            st.success(f"Intervento salvato con stato {label} colorato {bg_color}")
            st.rerun()

    if st.session_state.interventi:
        st.divider()
        st.markdown("**Interventi Salvati con Stato Colorato**")
        for idx, interv in enumerate(st.session_state.interventi):
            bg = interv.get("StatoColoreBg", "#ffffff")
            txt = interv.get("StatoColoreTxt", "black")
            st.markdown(
                f"""
                <div style="border:1px solid #ccc;padding:10px;border-radius:8px;
                margin-bottom:8px;background:white;">
                <span style="background:{bg};color:{txt};padding:4px 12px;
                border-radius:12px;font-weight:bold;border:2px solid black;">
                {interv.get('Stato','')}
                </span>
                <strong> {interv.get('Tipo','')} - {interv.get('Comune','')} {interv.get('Via','')}</strong><br>
                {interv.get('Descrizione','')[:100]}
                </div>
                """,
                unsafe_allow_html=True
            )

        df_int = pd.DataFrame(st.session_state.interventi)
        st.dataframe(df_int, use_container_width=True)
        st.download_button("Excel Interventi", to_excel(df_int), "interventi.xlsx", use_container_width=True)
        if REPORTLAB_OK:
            st.download_button("PDF Logo Estesa", to_pdf(df_int, "INTERVENTI EMERGENZA"), "interventi.pdf", use_container_width=True)

# TABELLA INTERVENTI EMERGENZA
elif cur == "Tabella Interventi Emergenza":
    hdr()
    hdr_form("TABELLA INTERVENTI EMERGENZA - Filtri Corretti")

    if not st.session_state.interventi:
        st.info("Nessun intervento salvato - Vai in Interventi Emergenza")
    else:
        df_tab = pd.DataFrame(st.session_state.interventi)

        # Filtri con variabili intermedie corrette parentesi chiuse
        squadre_list = sorted(list(set([str(x) for x in df_tab["Squadra"].tolist() if x])))
        comuni_list = sorted(list(set([str(x) for x in df_tab["Comune"].tolist() if x])))
        stati_list = sorted(list(set([str(x) for x in df_tab["Stato"].tolist() if x])))
        tipi_list = sorted(list(set([str(x) for x in df_tab["Tipo"].tolist() if x])))

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            filtro_squadra = st.selectbox(
                "Filtra Squadra",
                ["Tutte"] + squadre_list,
                key="tab_f_sq"
            )
        with c2:
            filtro_comune = st.selectbox(
                "Filtra Comune",
                ["Tutti"] + comuni_list,
                key="tab_f_com"
            )
        with c3:
            filtro_stato = st.selectbox(
                "Filtra Stato",
                ["Tutti"] + stati_list,
                key="tab_f_stato"
            )
        with c4:
            filtro_tipo = st.selectbox(
                "Filtra Tipo",
                ["Tutti"] + tipi_list,
                key="tab_f_tipo"
            )

        df_filtrato = df_tab.copy()

        if filtro_squadra != "Tutte":
            df_filtrato = df_filtrato[df_filtrato["Squadra"] == filtro_squadra]

        if filtro_comune != "Tutti":
            df_filtrato = df_filtrato[df_filtrato["Comune"] == filtro_comune]

        if filtro_stato != "Tutti":
            df_filtrato = df_filtrato[df_filtrato["Stato"] == filtro_stato]

        if filtro_tipo != "Tutti":
            df_filtrato = df_filtrato[df_filtrato["Tipo"] == filtro_tipo]

        st.write(f"Risultati filtrati: {len(df_filtrato)} su {len(df_tab)}")
        st.dataframe(df_filtrato, use_container_width=True)

        st.download_button(
            "Excel Filtrato",
            to_excel(df_filtrato),
            "tabella_interventi_filtrata.xlsx",
            use_container_width=True
        )
        if REPORTLAB_OK:
            st.download_button(
                "PDF Logo Tabella Estesa Tutto Foglio - Modifica 3",
                to_pdf(df_filtrato, "TABELLA INTERVENTI FILTRATA"),
                "tabella_interventi.pdf",
                use_container_width=True
            )

# MEZZI
elif cur == "Mezzi":
    hdr()
    hdr_form("MEZZI - Parco Automezzi")

    c1, c2, c3 = st.columns(3)
    with c1:
        targa = st.text_input("Targa", key="mez_targa")
        modello_m = st.text_input("Modello Mezzo", key="mez_modello")
        tipo_m = st.selectbox("Tipo", ["Fuoristrada", "Furgone", "Autocarro", "Auto", "Moto"], key="mez_tipo")

    with c2:
        stato_m = st.selectbox("Stato Mezzo", ["Operativo", "In Manutenzione", "Fuori Servizio"], key="mez_stato")
        km = st.text_input("Km", key="mez_km")
        scadenza = st.date_input("Scadenza Revisione", value=date.today(), format="DD/MM/YYYY", key="mez_scad")

    with c3:
        note_mez = st.text_area("Note Mezzo", key="mez_note")
        foto_mez = st.file_uploader("Foto Mezzo", type=["jpg", "png"], key="mez_foto")

    if st.button("Salva Mezzo", type="primary", use_container_width=True):
        if targa:
            st.session_state.mezzi.append({
                "Targa": targa,
                "Modello": modello_m,
                "Tipo": tipo_m,
                "Stato": stato_m,
                "Km": km,
                "Scadenza": str(scadenza),
                "Note": note_mez
            })
            st.success("Mezzo salvato")
            st.rerun()

    if st.session_state.mezzi:
        df_mez = pd.DataFrame(st.session_state.mezzi)
        st.dataframe(df_mez, use_container_width=True)
        st.download_button("Excel Mezzi", to_excel(df_mez), "mezzi.xlsx", use_container_width=True)
        if REPORTLAB_OK:
            st.download_button("PDF Logo Estesa", to_pdf(df_mez, "MEZZI"), "mezzi.pdf", use_container_width=True)

# ATTREZZATURE
elif cur == "Attrezzature":
    hdr()
    hdr_form("ATTREZZATURE - Magazzino")

    c1, c2 = st.columns(2)
    with c1:
        nome_att = st.text_input("Nome Attrezzatura", key="att_nome")
        cat_att = st.selectbox("Categoria", ["DPI", "Utensili", "Elettrico", "Idraulico", "Altro"], key="att_cat")
        qta_att = st.number_input("Quantità", min_value=1, value=1, key="att_qta")

    with c2:
        stato_att = st.selectbox("Stato", ["Disponibile", "In Uso", "Guasto", "Esaurito"], key="att_stato")
        ubic_att = st.text_input("Ubicazione Magazzino", key="att_ubic")
        note_att = st.text_area("Note", key="att_note")

    if st.button("Salva Attrezzatura", type="primary", use_container_width=True):
        if nome_att:
            st.session_state.attrezzature.append({
                "Nome": nome_att,
                "Categoria": cat_att,
                "Quantita": qta_att,
                "Stato": stato_att,
                "Ubicazione": ubic_att,
                "Note": note_att
            })
            st.success("Attrezzatura salvata")
            st.rerun()

    if st.session_state.attrezzature:
        df_att = pd.DataFrame(st.session_state.attrezzature)
        st.dataframe(df_att, use_container_width=True)
        st.download_button("Excel Attrezzature", to_excel(df_att), "attrezzature.xlsx", use_container_width=True)
        if REPORTLAB_OK:
            st.download_button("PDF Logo Estesa", to_pdf(df_att, "ATTREZZATURE"), "attrezzature.pdf", use_container_width=True)

# MAPPA AVANZATA - FINALE con Fullscreen + Marker rimane + Coordinate Comune Via Lat Lon in maschera
elif cur == "Mappa Avanzata":
    hdr()
    hdr_form("MAPPA AVANZATA - Marker da Libreria Icone + Fullscreen")

    st.markdown(
        """
        <div style="background:#e3f2fd;padding:12px;border-radius:8px;border-left:4px solid #1976d2;">
        <b>Mappa cliccabile con fullscreen - Marker rimane - Coordinate Comune Via Lat Lon in maschera automatica - Icone da libreria - Google Maps / Waze / Google Earth</b>
        </div>
        """,
        unsafe_allow_html=True
    )

    if "mappa_avanzata_markers" not in st.session_state:
        st.session_state.mappa_avanzata_markers = []
    if "last_clicked_lat" not in st.session_state:
        st.session_state.last_clicked_lat = "45.8167"
    if "last_clicked_lon" not in st.session_state:
        st.session_state.last_clicked_lon = "8.8333"

    # Fullscreen mappa
    c_fs1, c_fs2 = st.columns([1,3])
    with c_fs1:
        if st.button("⛶ Fullscreen Mappa", key="btn_fs_mappa", use_container_width=True, type="primary"):
            st.session_state["fs_mappa_active"] = True
    with c_fs2:
        st.markdown('<span style="background:#1A5D1A;color:white;padding:6px 12px;border-radius:6px;font-weight:bold;">🗺️ Mappa con marker che rimane</span>', unsafe_allow_html=True)

    if st.session_state.get("fs_mappa_active"):
        st.components.v1.html(
            """
            <script>
            (function(){
                try {
                    const el = window.parent.document.documentElement;
                    if (el.requestFullscreen) el.requestFullscreen();
                } catch(e){}
            })();
            </script>
            <div style="background:#1A5D1A;color:white;padding:8px;border-radius:6px;text-align:center;font-weight:bold;">FULLSCREEN MAPPA ATTIVO - ESC per uscire</div>
            """,
            height=60
        )
        if st.button("❌ Esci Fullscreen Mappa", key="btn_exit_fs_mappa"):
            st.components.v1.html("<script>try{document.exitFullscreen(); parent.document.exitFullscreen();}catch(e){}</script>", height=0)
            st.session_state["fs_mappa_active"] = False
            st.rerun()

    c_tipo1, c_tipo2 = st.columns([1,2])
    with c_tipo1:
        tipo_mappa_ext = st.selectbox("Tipo Mappa Esterna", ["Google Maps", "Waze", "Google Earth"], index=0, key="tipo_mappa_ext")
    with c_tipo2:
        st.caption("Marker da libreria icone - rimane sulla mappa - coordinate in maschera")

    st.markdown("#### 📍 Aggiungi Marker - Coordinate da mappa in maschera automatica")

    icone_disponibili = st.session_state.get("icone", [])
    if not icone_disponibili:
        icone_nomi = ["🚨 Emergenza", "📅 Evento", "🚐 Mezzo", "👤 Volontario", "📻 Radio", "🏥 Ospedale", "🔥 Incendio", "💧 Alluvione"]
    else:
        icone_nomi = [f"{ico.get('Nome','')} ({ico.get('Tipo','')})" for ico in icone_disponibili]

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        marker_nome = st.text_input("Nome Marker *", key="adv_marker_nome", placeholder="Es: Incidente Via Roma")
        marker_lat = st.text_input("Latitudine *", value=st.session_state.last_clicked_lat, key="adv_marker_lat")
    with c2:
        marker_lon = st.text_input("Longitudine *", value=st.session_state.last_clicked_lon, key="adv_marker_lon")
        marker_comune = st.text_input("Comune (da mappa)", value="Varese", key="adv_marker_comune")
    with c3:
        marker_via = st.text_input("Via (da mappa)", value="", key="adv_marker_via")
        marker_icona = st.selectbox("Icona dalla Libreria", icone_nomi, key="adv_marker_icona")
    with c4:
        marker_tipo = st.selectbox("Tipo Marker", ["Emergenza", "Evento", "Mezzo", "Volontario", "Punto Interesse"], key="adv_marker_tipo")
        marker_data = st.date_input("Data Evento", value=date.today(), format="DD/MM/YYYY", key="adv_marker_data")
        marker_desc = st.text_input("Descrizione", key="adv_marker_desc")

    if st.button("➕ Aggiungi Marker - Rimane su mappa", type="primary", use_container_width=True):
        if marker_nome and marker_lat and marker_lon:
            try:
                lat_f = float(str(marker_lat).replace(",", "."))
                lon_f = float(str(marker_lon).replace(",", "."))
                nuovo_marker = {
                    "Nome": marker_nome,
                    "Lat": lat_f,
                    "Lon": lon_f,
                    "Comune": marker_comune,
                    "Via": marker_via,
                    "Icona": marker_icona,
                    "Descrizione": marker_desc,
                    "Tipo": marker_tipo,
                    "Data": str(marker_data),
                    "DataIns": datetime.now().strftime("%d/%m/%Y %H:%M")
                }
                st.session_state.mappa_avanzata_markers.append(nuovo_marker)
                st.success(f"Marker {marker_nome} aggiunto - Rimane su mappa - Comune {marker_comune} Via {marker_via}")
                st.rerun()
            except Exception as e:
                st.error(f"Coordinate non valide: {e}")
        else:
            st.error("Compila Nome, Lat, Lon")

    st.divider()

    all_markers = st.session_state.get("mappa_avanzata_markers", [])

    import json as json_lib
    markers_for_js = json_lib.dumps([{"lat": m["Lat"], "lon": m["Lon"], "nome": m["Nome"], "icona": m["Icona"], "tipo": m["Tipo"], "comune": m.get("Comune",""), "via": m.get("Via","")} for m in all_markers])

    html_code = """
    <div id="map-container" style="position:relative; background:white; border-radius:12px;">
        <div id="map" style="height:650px; width:100%; border-radius:12px; border:3px solid #1A5D1A;"></div>
        <button id="fs-btn" style="position:absolute; top:15px; right:15px; z-index:1000; background:#ff0000; color:white; border:2px solid white; padding:10px 16px; border-radius:8px; font-weight:bold; cursor:pointer; box-shadow:0 2px 6px rgba(0,0,0,0.3);">⛶ FULLSCREEN MAPPA</button>
        <button id="fs-btn-exit" style="position:absolute; top:15px; left:15px; z-index:1000; background:#1A5D1A; color:white; border:2px solid white; padding:8px 12px; border-radius:6px; font-weight:bold; cursor:pointer; display:none;">❌ Esci Fullscreen</button>
    </div>
    <div id="coords" style="background:#fffde7;padding:12px;border-radius:6px;margin-top:8px;font-weight:bold;border-left:4px solid #FFD700; font-family:Times New Roman; min-height:50px;">📍 Clicca sulla mappa - Il marker rimarrà - Coordinate in maschera automatica</div>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script>
    var markersData = MARKERS_JSON_PLACEHOLDER;
    var map = L.map('map').setView([45.8167, 8.8333], 14);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {attribution: 'ANA Varese - OpenStreetMap'}).addTo(map);

    // Fullscreen gestione
    var fsBtn = document.getElementById('fs-btn');
    var fsExitBtn = document.getElementById('fs-btn-exit');
    var mapContainer = document.getElementById('map-container');
    
    fsBtn.addEventListener('click', function() {
        if (mapContainer.requestFullscreen) mapContainer.requestFullscreen();
        else if (mapContainer.webkitRequestFullscreen) mapContainer.webkitRequestFullscreen();
        else if (mapContainer.msRequestFullscreen) mapContainer.msRequestFullscreen();
    });
    
    document.addEventListener('fullscreenchange', function() {
        if (document.fullscreenElement) {
            fsBtn.style.display = 'none';
            fsExitBtn.style.display = 'block';
            setTimeout(function(){ map.invalidateSize(); }, 500);
        } else {
            fsBtn.style.display = 'block';
            fsExitBtn.style.display = 'none';
            setTimeout(function(){ map.invalidateSize(); }, 500);
        }
    });

    fsExitBtn.addEventListener('click', function() {
        if (document.exitFullscreen) document.exitFullscreen();
    });

    // Marker esistenti - RIMANGONO
    var allMarkers = [];
    markersData.forEach(function(m) {
        var iconEmoji = "📍";
        if (m.icona && m.icona.includes("Emergenza")) iconEmoji = "🚨";
        else if (m.icona && m.icona.includes("Evento")) iconEmoji = "📅";
        else if (m.tipo == "Emergenza") iconEmoji = "🚨";
        else if (m.tipo == "Evento") iconEmoji = "📅";
        
        var marker = L.marker([m.lat, m.lon]).addTo(map)
            .bindPopup("<b>" + m.nome + "</b><br>" + m.icona + "<br>" + m.tipo + "<br>" + m.comune + " - " + m.via + "<br>Lat: " + m.lat + "<br>Lon: " + m.lon);
        allMarkers.push(marker);
    });

    // Fit bounds se ci sono marker
    if (allMarkers.length > 0) {
        var group = new L.featureGroup(allMarkers);
        map.fitBounds(group.getBounds().pad(0.2));
    }

    // Marker cliccati - RIMANGONO tutti
    var clickedMarkers = [];
    map.on('click', function(e) {
        var lat = e.latlng.lat.toFixed(6);
        var lon = e.latlng.lng.toFixed(6);
        
        // Crea marker che RIMANE - non rimuove precedenti
        var newMarker = L.marker([lat, lon], {
            draggable:true,
            icon: L.icon({
                iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
                shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
                iconSize: [25, 41],
                iconAnchor: [12, 41],
                popupAnchor: [1, -34]
            })
        }).addTo(map)
            .bindPopup("<b>Nuovo marker</b><br>Lat: " + lat + "<br>Lon: " + lon + "<br>Trascina per spostare<br><b>RIMANE sulla mappa</b>").openPopup();
        
        clickedMarkers.push(newMarker);
        document.getElementById('coords').innerHTML = "📍 Marker aggiunto - RIMANE sulla mappa - Totale marker temporanei: " + clickedMarkers.length + "<br>Lat: " + lat + " - Lon: " + lon + "<br><b>Copia in maschera sopra e clicca Aggiungi Marker per salvare definitivamente</b><br>Reverse geocoding in corso...";

        // Auto-compila maschera
        try {
            var parentDoc = window.parent.document;
            var allInputs = parentDoc.querySelectorAll('input[type="text"]');
            allInputs.forEach(function(inp) {
                var label = inp.getAttribute('aria-label') || '';
                if (label.includes('Latitudine') && label.includes('*')) {
                    inp.focus();
                    document.execCommand('selectAll', false, null);
                    inp.value = lat;
                    inp.dispatchEvent(new Event('input', {bubbles:true}));
                    inp.dispatchEvent(new Event('change', {bubbles:true}));
                    parentDoc.defaultView.localStorage.setItem('last_lat', lat);
                }
                if (label.includes('Longitudine') && label.includes('*')) {
                    inp.value = lon;
                    inp.dispatchEvent(new Event('input', {bubbles:true}));
                    inp.dispatchEvent(new Event('change', {bubbles:true}));
                    parentDoc.defaultView.localStorage.setItem('last_lon', lon);
                }
            });
            fetch('https://nominatim.openstreetmap.org/reverse?format=json&lat=' + lat + '&lon=' + lon + '&zoom=18&addressdetails=1')
                .then(response => response.json())
                .then(data => {
                    var comune = data.address.city || data.address.town || data.address.village || data.address.municipality || "";
                    var via = data.address.road || data.address.street || "";
                    document.getElementById('coords').innerHTML += "<br>📍 Comune: <b>" + comune + "</b> - Via: <b>" + via + "</b>";
                    allInputs.forEach(function(inp) {
                        var label = inp.getAttribute('aria-label') || '';
                        if (label.includes('Comune (da mappa)')) {
                            inp.value = comune;
                            inp.dispatchEvent(new Event('input', {bubbles:true}));
                            inp.dispatchEvent(new Event('change', {bubbles:true}));
                        }
                        if (label.includes('Via (da mappa)')) {
                            inp.value = via;
                            inp.dispatchEvent(new Event('input', {bubbles:true}));
                            inp.dispatchEvent(new Event('change', {bubbles:true}));
                        }
                    });
                });
        } catch(err) {
            console.log(err);
        }

        newMarker.on('dragend', function(event) {
            var pos = event.target.getLatLng();
            document.getElementById('coords').innerHTML = "📍 Marker trascinato - RIMANE<br>Lat: " + pos.lat.toFixed(6) + " Lon: " + pos.lng.toFixed(6);
        });
    });
    </script>
    """
    html_code = html_code.replace("MARKERS_JSON_PLACEHOLDER", markers_for_js)
    st.components.v1.html(html_code, height=700)

    if all_markers:
        st.markdown(f"#### Elenco {len(all_markers)} Marker - Rimangono su mappa")
        for idx, m in enumerate(all_markers):
            c1, c2, c3, c4 = st.columns([2,2,3,1])
            with c1:
                st.write(f"**{m['Nome']}**")
                st.caption(f"{m['Icona']} - {m['Tipo']}")
            with c2:
                st.text(f"Lat: {m['Lat']} Lon: {m['Lon']}")
                st.caption(f"{m.get('Comune','')} - {m.get('Via','')}")
            with c3:
                lat = m['Lat']
                lon = m['Lon']
                gmaps = f"https://www.google.com/maps?q={lat},{lon}"
                waze = f"https://waze.com/ul?ll={lat},{lon}&navigate=yes"
                gearth = f"https://earth.google.com/web/@{lat},{lon},500a,1000d"
                st.markdown(f"[Google Maps]({gmaps}) | [Waze]({waze}) | [Earth]({gearth})")
                if tipo_mappa_ext == "Google Maps":
                    st.link_button(f"Apri {tipo_mappa_ext}", gmaps, use_container_width=True)
                elif tipo_mappa_ext == "Waze":
                    st.link_button(f"Apri {tipo_mappa_ext}", waze, use_container_width=True)
                else:
                    st.link_button(f"Apri {tipo_mappa_ext}", gearth, use_container_width=True)
            with c4:
                if st.button("🗑️", key=f"del_marker_{idx}"):
                    st.session_state.mappa_avanzata_markers.pop(idx)
                    st.rerun()
            st.divider()
        if st.button("⬇️ Export Marker Excel", use_container_width=True):
            df_exp = pd.DataFrame(all_markers)
            st.download_button("Download Excel", data=to_excel(df_exp), file_name="mappa_avanzata.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.info("Nessun marker - Clicca sulla mappa - Marker rimane - Coordinate Comune Via Lat Lon in maschera")

# LIBRERIA ICONE



elif cur == "Libreria Icone":
    hdr()
    hdr_form("LIBRERIA ICONE - Icone Personalizzate")

    c1, c2 = st.columns(2)
    with c1:
        nome_icona = st.text_input("Nome Icona", key="ico_nome")
        tipo_icona = st.selectbox("Tipo", ["Emergenza", "Evento", "Mezzo", "Volontario", "Altro"], key="ico_tipo")

    with c2:
        file_icona = st.file_uploader("File Icona", type=["png", "jpg", "svg"], key="ico_file")
        desc_icona = st.text_input("Descrizione Icona", key="ico_desc")

    if st.button("Salva Icona", type="primary", use_container_width=True):
        if nome_icona:
            st.session_state.icone.append({
                "Nome": nome_icona,
                "Tipo": tipo_icona,
                "Descrizione": desc_icona,
                "Data": datetime.now().strftime("%d/%m/%Y")
            })
            st.success("Icona salvata")
            st.rerun()

    if st.session_state.icone:
        df_ico = pd.DataFrame(st.session_state.icone)
        st.dataframe(df_ico, use_container_width=True)

# CHAT
elif cur == "Chat":
    hdr()
    hdr_form("CHAT - Comunicazioni Squadra")

    st.markdown("Chat operativa volontari")

    msg = st.text_input("Messaggio", key="chat_msg")

    c1, c2 = st.columns([1, 3])
    with c1:
        if st.button("Invia Messaggio", type="primary", use_container_width=True):
            if msg:
                st.session_state.chat.append({
                    "Ora": datetime.now().strftime("%H:%M:%S"),
                    "Utente": "Admin",
                    "Messaggio": msg
                })
                st.rerun()

    st.divider()

    if st.session_state.chat:
        for chat_msg in reversed(st.session_state.chat[-20:]):
            st.markdown(
                f"""
                <div style="background:white;padding:10px;border-radius:8px;
                margin-bottom:6px;border-left:4px solid #1A5D1A;">
                <strong>{chat_msg.get('Ora','')} - {chat_msg.get('Utente','')}</strong><br>
                {chat_msg.get('Messaggio','')}
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.info("Nessun messaggio - Inizia conversazione")

# GEOLOCALIZZAZIONE HYTERA + ANYTONE
elif cur == "Geolocalizzazione Hytera + Anytone":
    hdr()
    hdr_form("GEOLOCALIZZAZIONE HYTERA + ANYTONE - PD785 + 878")

    st.markdown(
        """
        <div style="background:#e8f5e9;padding:12px;border-radius:8px;
        border:1px solid #1A5D1A;margin-bottom:12px;">
        <strong>Hytera PD785 e Anytone 878 - Tracciamento GPS volontari in campo</strong>
        </div>
        """,
        unsafe_allow_html=True
    )

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Posizioni Hytera PD785**")
        id_pd = st.text_input("ID Radio PD785", key="pd_id")
        lat_pd = st.text_input("Latitudine PD785", value="45.8167", key="pd_lat")
        lon_pd = st.text_input("Longitudine PD785", value="8.8333", key="pd_lon")

        if st.button("Aggiorna Posizione PD785", use_container_width=True):
            if id_pd:
                st.session_state.posizioni_pd785.append({
                    "ID": id_pd,
                    "Lat": lat_pd,
                    "Lon": lon_pd,
                    "Ora": datetime.now().strftime("%H:%M:%S"),
                    "Modello": "PD785"
                })
                st.success("Posizione PD785 aggiornata")

    with c2:
        st.markdown("**Posizioni Anytone 878**")
        id_any = st.text_input("ID Radio Anytone", key="any_id")
        lat_any = st.text_input("Latitudine Anytone", value="45.82", key="any_lat")
        lon_any = st.text_input("Longitudine Anytone", value="8.84", key="any_lon")

        if st.button("Aggiorna Posizione Anytone", use_container_width=True):
            if id_any:
                st.session_state.posizioni_anytone.append({
                    "ID": id_any,
                    "Lat": lat_any,
                    "Lon": lon_any,
                    "Ora": datetime.now().strftime("%H:%M:%S"),
                    "Modello": "Anytone 878"
                })
                st.success("Posizione Anytone aggiornata")

    st.divider()

    all_pos = st.session_state.posizioni_pd785 + st.session_state.posizioni_anytone
    if all_pos:
        df_pos = pd.DataFrame(all_pos)
        st.dataframe(df_pos, use_container_width=True)

        try:
            map_pos = pd.DataFrame([
                {"lat": float(p.get("Lat", 0)), "lon": float(p.get("Lon", 0))}
                for p in all_pos
                if p.get("Lat") and p.get("Lon")
            ])
            if not map_pos.empty:
                st.map(map_pos)
        except:
            pass

        st.download_button("Excel Posizioni", to_excel(df_pos), "posizioni_hytera_anytone.xlsx", use_container_width=True)
    else:
        st.info("Nessuna posizione registrata")

        demo_pos = pd.DataFrame([
            {"lat": 45.8167, "lon": 8.8333},
            {"lat": 45.82, "lon": 8.84}
        ])
        st.map(demo_pos)

# BACKUP - Import/Export singolo + totale - gg/mm/aaaa
elif cur == "Backup":
    hdr()
    hdr_form("BACKUP - Import / Export Completo")

    FORM_KEYS = {
        "Volontari (con foto)": "volontari",
        "DB Radio": "radio_db",
        "Consegna Radio": "consegna_radio",
        "Alias Radio": "alias_radio",
        "Brogliaccio": "brogliaccio",
        "Eventi": "eventi",
        "Emergenze": "emergenze",
        "# RIMOSSO": "mappe",
        "Check-in": "checkin",
        "Interventi Emergenza": "interventi",
        "Mezzi": "mezzi",
        "Attrezzature": "attrezzature",
        "Libreria Icone": "icone",
        "Chat": "chat",
        "Posizioni PD785": "posizioni_pd785",
        "Posizioni Anytone": "posizioni_anytone"
    }

    def clean_for_json(obj):
        if isinstance(obj, list):
            cleaned = []
            for item in obj:
                if isinstance(item, dict):
                    new_item = {}
                    for k, v in item.items():
                        if "Bytes" not in k and "Foto" not in k and "File" not in k:
                            try:
                                json.dumps(v)
                                new_item[k] = v
                            except:
                                new_item[k] = str(v)
                        else:
                            new_item[k] = "BINARIO_OMESSO"
                    cleaned.append(new_item)
                else:
                    cleaned.append(item)
            return cleaned
        return obj

    tab_tot, tab_singolo, tab_import = st.tabs(["💾 Backup Totale", "📄 Singolo Form", "📥 Importa Backup"])

    with tab_tot:
        st.markdown("#### Backup Totale")
        backup_data = {k: st.session_state.get(k, []) for k in FORM_KEYS.values()}
        backup_data["data_backup"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        backup_data["versione"] = "ANA Varese v2 - gg/mm/aaaa - ODV + linguette"
        json_clean = {k: clean_for_json(v) if isinstance(v, list) else v for k,v in backup_data.items()}
        json_str = json.dumps(json_clean, indent=2, ensure_ascii=False)
        c1, c2, c3 = st.columns(3)
        with c1:
            st.download_button("⬇️ JSON Totale", data=json_str.encode("utf-8"), file_name=f"backup_totale_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", mime="application/json", use_container_width=True, type="primary")
        with c2:
            try:
                datasets = {}
                for label, key in FORM_KEYS.items():
                    data = st.session_state.get(key, [])
                    if data:
                        clean = [{kk: vv for kk, vv in r.items() if "Bytes" not in kk and "Foto" not in kk} for r in data if isinstance(r, dict)]
                        if clean:
                            datasets[label[:31]] = pd.DataFrame(clean)
                if datasets:
                    st.download_button("⬇️ Excel Multi", data=to_excel_multi(datasets), file_name=f"backup_totale_{datetime.now().strftime('%Y%m%d')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
            except Exception as e:
                st.error(f"Excel: {e}")
        with c3:
            if REPORTLAB_OK:
                try:
                    df_summary = pd.DataFrame([{"Form": label, "Record": len(st.session_state.get(key, []))} for label, key in FORM_KEYS.items()])
                    st.download_button("⬇️ PDF", data=to_pdf(df_summary, "BACKUP TOTALE"), file_name="backup_riepilogo.pdf", mime="application/pdf", use_container_width=True)
                except:
                    pass
        st.code(json_str[:4000] + ("..." if len(json_str)>4000 else ""), language="json")

    with tab_singolo:
        st.markdown("#### Export / Import Singolo Form")
        sel_label = st.selectbox("Seleziona Form", list(FORM_KEYS.keys()), key="backup_sel_form")
        sel_key = FORM_KEYS[sel_label]
        sel_data = st.session_state.get(sel_key, [])
        st.metric(f"Record in {sel_label}", len(sel_data))
        if sel_data:
            df_sel = pd.DataFrame([{k:v for k,v in r.items() if "Bytes" not in k} for r in sel_data if isinstance(r, dict)])
            st.dataframe(df_sel.head(20), use_container_width=True)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"**⬇️ EXPORT {sel_label}**")
            if sel_data:
                df_clean = pd.DataFrame([{k:v for k,v in r.items() if "Bytes" not in k and "Foto" not in k} for r in sel_data])
                st.download_button(f"⬇️ Excel {sel_label}", data=to_excel(df_clean), file_name=f"{sel_key}_{datetime.now().strftime('%Y%m%d')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True, key=f"exp_excel_{sel_key}")
                st.download_button(f"⬇️ CSV {sel_label}", data=df_clean.to_csv(index=False).encode("utf-8"), file_name=f"{sel_key}.csv", mime="text/csv", use_container_width=True, key=f"exp_csv_{sel_key}")
                st.download_button(f"⬇️ JSON {sel_label}", data=json.dumps(clean_for_json(sel_data), indent=2, ensure_ascii=False).encode("utf-8"), file_name=f"{sel_key}.json", mime="application/json", use_container_width=True, key=f"exp_json_{sel_key}")
            else:
                st.warning("Vuoto")
        with c2:
            st.markdown(f"**📥 IMPORT in {sel_label}**")
            up_mode = st.radio("Modalità", ["Aggiungi", "Sostituisci"], key="up_mode_single", horizontal=True)
            up_file = st.file_uploader(f"Carica per {sel_label}", type=["json", "xlsx", "csv"], key="up_single_form")
            if up_file:
                try:
                    imported = []
                    if up_file.name.endswith(".json"):
                        raw = json.loads(up_file.read().decode("utf-8"))
                        if isinstance(raw, dict):
                            if sel_key in raw:
                                imported = raw[sel_key]
                            else:
                                for v in raw.values():
                                    if isinstance(v, list) and v and isinstance(v[0], dict):
                                        imported = v
                                        break
                        elif isinstance(raw, list):
                            imported = raw
                    elif up_file.name.endswith(".xlsx"):
                        imported = pd.read_excel(up_file).to_dict(orient="records")
                    else:
                        imported = pd.read_csv(up_file).to_dict(orient="records")
                    st.success(f"{len(imported)} record")
                    st.dataframe(pd.DataFrame(imported).head(10), use_container_width=True)
                    if st.button(f"✅ Importa in {sel_label}", type="primary"):
                        if up_mode == "Sostituisci":
                            st.session_state[sel_key] = imported
                        else:
                            st.session_state[sel_key] = st.session_state.get(sel_key, []) + imported
                        st.rerun()
                except Exception as e:
                    st.error(f"Errore: {e}")

    with tab_import:
        st.markdown("#### Importa Backup Totale")
        up_total = st.file_uploader("JSON Totale", type=["json"], key="up_total_backup")
        if up_total:
            try:
                data_total = json.loads(up_total.read().decode("utf-8"))
                st.write(f"Backup del: {data_total.get('data_backup','?')}")
                cols = st.columns(4)
                for i, (label, key) in enumerate(FORM_KEYS.items()):
                    if key in data_total:
                        cols[i % 4].metric(label, f"{len(data_total.get(key, []))}")
                mode_total = st.radio("Modalità", ["Aggiungi", "Sostituisci"], key="mode_total")
                if st.button("✅ CONFERMA IMPORT TOTALE", type="primary", use_container_width=True):
                    for label, key in FORM_KEYS.items():
                        if key in data_total and isinstance(data_total[key], list):
                            if mode_total.startswith("Sostituisci"):
                                st.session_state[key] = data_total[key]
                            else:
                                st.session_state[key] = st.session_state.get(key, []) + data_total[key]
                    st.success("Importato!")
                    st.rerun()
            except Exception as e:
                st.error(f"Errore: {e}")
        with st.expander("⚠️ Azzera"):
            sel_zero = st.selectbox("Form da azzerare", ["--"] + list(FORM_KEYS.keys()), key="zero_sel")
            if sel_zero != "--":
                if st.button(f"🗑️ Azzera {sel_zero}"):
                    st.session_state[FORM_KEYS[sel_zero]] = []
                    st.rerun()
            if st.button("🗑️ AZZERA TUTTO"):
                for k in FORM_KEYS.values():
                    st.session_state[k] = []
                st.rerun()

# Footer
st.divider()
st.markdown(
    """
    <div style="text-align:center;padding:12px;background:linear-gradient(135deg,#1A5D1A,#2e7d32);border-radius:8px;color:white;font-size:12px;">
    ANA Varese - Dashboard rosso + bottoni OK | Volontari linguette + ODV | Date gg/mm/aaaa | Backup Import/Export<br>
    Sviluppato per Ezio
    </div>
    """,
    unsafe_allow_html=True
)
