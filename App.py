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

# CSS Globale - Times New Roman grassetto per tutti + Verde ANA
st.markdown(
    """
    <style>
    * {
        font-family: 'Times New Roman', Times, serif !important;
    }
    html, body, [class*="css"] {
        font-family: 'Times New Roman', Times, serif !important;
    }
    p, div, span, label, input, select, textarea, button {
        font-family: 'Times New Roman', Times, serif !important;
        font-weight: bold !important;
    }
    .stTextInput label, .stSelectbox label, .stDateInput label, .stTimeInput label, .stTextArea label {
        font-family: 'Times New Roman', Times, serif !important;
        font-weight: bold !important;
        font-size: 14px !important;
        color: black !important;
    }
    /* Bottoni dashboard verde ANA */
    div[data-testid="column"] .stButton > button {
        background-color: #1A5D1A !important;
        color: white !important;
        border: 2px solid #1A5D1A !important;
        font-weight: bold !important;
        font-family: 'Times New Roman', serif !important;
        font-size: 13px !important;
    }
    div[data-testid="column"] .stButton > button:hover {
        background-color: #2e7d32 !important;
        border-color: #2e7d32 !important;
        color: white !important;
    }
    /* Bottoni primary verde ANA (tranne fullscreen) */
    button[kind="primary"] {
        background-color: #1A5D1A !important;
        border-color: #1A5D1A !important;
        font-family: 'Times New Roman', serif !important;
        font-weight: bold !important;
    }
    button[kind="primary"]:hover {
        background-color: #2e7d32 !important;
    }

    /* FIX FULLSCREEN 100% SU TUTTE LE MAPPE - SOTTO + - */
    .leaflet-control-zoom { margin-bottom: 5px !important; }
    .fullscreen-btn-all {
        background: white !important;
        width: 34px !important;
        height: 34px !important;
        line-height: 34px !important;
        text-align: center !important;
        font-size: 22px !important;
        cursor: pointer !important;
        border: 2px solid rgba(0,0,0,0.2) !important;
        border-radius: 4px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        color: black !important;
        font-weight: bold !important;
        text-decoration: none !important;
    }
    .fullscreen-btn-all:hover { background: #f4f4f4 !important; }

    /* Fullscreen rosso */
    button#fs-btn, button[key="btn_fullscreen_dash"], button[key="btn_fs_mappa"] {
        background-color: #ff0000 !important;
        border-color: #ff0000 !important;
    }
    /* Tab linguette Times New Roman bold */
    .stTabs [data-baseweb="tab-list"] button {
        font-family: 'Times New Roman', serif !important;
        font-weight: bold !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# Auto-inietta UI PATCH nella sidebar se disponibile
try:
    ui_patch_loader_sidebar()
except:
    pass




# FIX FULLSCREEN SU TUTTE LE MAPPE + MARKER = ICONA LIBRERIA
def inject_fullscreen_all_maps():
    st.components.v1.html('''
    <script>
    function addFullscreenToAllLeafletMaps() {
        document.querySelectorAll('.leaflet-container').forEach(function(container) {
            if (container.querySelector('.fullscreen-btn-all')) return;
            var zoomCtrl = container.querySelector('.leaflet-control-zoom');
            if (!zoomCtrl) return;
            var fsDiv = document.createElement('div');
            fsDiv.className = 'leaflet-bar leaflet-control';
            fsDiv.style.marginTop = '5px';
            var btn = document.createElement('a');
            btn.className = 'fullscreen-btn-all';
            btn.innerHTML = '⛶';
            btn.href = '#';
            btn.title = 'Schermo intero 100%';
            btn.onclick = function(e) {
                e.preventDefault();
                e.stopPropagation();
                var mapEl = this.closest('.leaflet-container');
                if (!document.fullscreenElement) {
                    if (mapEl.requestFullscreen) mapEl.requestFullscreen();
                    else if (mapEl.webkitRequestFullscreen) mapEl.webkitRequestFullscreen();
                    else if (mapEl.msRequestFullscreen) mapEl.msRequestFullscreen();
                    setTimeout(function(){ 
                        try { mapEl._leaflet_map && mapEl._leaflet_map.invalidateSize(); } catch(e){}
                    }, 600);
                } else {
                    if (document.exitFullscreen) document.exitFullscreen();
                }
            };
            fsDiv.appendChild(btn);
            zoomCtrl.parentNode.insertBefore(fsDiv, zoomCtrl.nextSibling);
        });
    }
    setTimeout(addFullscreenToAllLeafletMaps, 800);
    setInterval(addFullscreenToAllLeafletMaps, 1500);
    </script>
    ''', height=0)


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
                font-weight:bold;font-size:18px;color:white;">
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
                justify-content:center;color:white;font-weight:bold;font-size:18px;">
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
        "Mappe Postazioni",
        "Libreria Icone",
        "Turni",
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
        <div style="background:#e8f5e9;padding:8px;border-radius:8px;">
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
        background:#fffde7;padding:8px;border-radius:8px;
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
        ("Mappe Postazioni", "🌍 Mappe Postazioni"),
        ("Libreria Icone", "🎨 Libreria Icone"),
        ("Turni", "🕐 Turni"),
        ("Chat", "💬 Chat"),
        ("Geolocalizzazione Hytera + Anytone", "📡 Geoloc"),
        ("Backup", "💾 Backup")
    ]
    # FIX TURNI BUTTON - forza visibilità
    if "Turni" not in [x[0] for x in form_buttons]:
        form_buttons.append(("Turni", "🕐 Turni"))

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
        st.session_state["cur"] = form_name
        # Forza rerun immediato
        try:
            st.rerun()
        except:
            pass

    # CSS bottoni verde ANA - SFONDO PIENO VERDE - FIX DEFINITIVO
    st.markdown(
        """
        <style>
        /* Reset e forza verde ANA su TUTTI i bottoni dashboard */
        [data-testid="column"] .stButton > button,
        [data-testid="stColumn"] .stButton > button,
        div[data-testid="stVerticalBlock"] .stButton > button {
            background-color: #1A5D1A !important;
            background-image: none !important;
            background: #1A5D1A !important;
            color: white !important;
            border: 2px solid #1A5D1A !important;
            font-weight: bold !important;
            font-family: 'Times New Roman', serif !important;
            border-radius: 8px !important;
        }
        [data-testid="column"] .stButton > button:hover {
            background-color: #2e7d32 !important;
            background: #2e7d32 !important;
            border-color: #2e7d32 !important;
            color: white !important;
        }
        [data-testid="column"] .stButton > button:active,
        [data-testid="column"] .stButton > button:focus,
        [data-testid="column"] .stButton > button:focus-visible {
            background-color: #1A5D1A !important;
            background: #1A5D1A !important;
            color: white !important;
            box-shadow: 0 0 0 2px rgba(26,93,26,0.3) !important;
            outline: none !important;
        }
        /* Forza anche su kind secondary */
        button[kind="secondary"] {
            background-color: #1A5D1A !important;
            background: #1A5D1A !important;
            color: white !important;
            border-color: #1A5D1A !important;
        }
        /* Solo i bottoni primary generici lasciali verdi, tranne fullscreen */
        button[kind="primary"]:not([data-testid*="fullscreen"]) {
            background-color: #1A5D1A !important;
            background: #1A5D1A !important;
            border-color: #1A5D1A !important;
        }
        /* Fullscreen dashboard rosso - specifico */
        button[key="btn_fullscreen_dash"], button[key="btn_exit_fs"] {
            background-color: #ff0000 !important;
            background: #ff0000 !important;
            border-color: #ff0000 !important;
        }
        /* Testo dentro bottone bianco */
        .stButton > button div, .stButton > button p, .stButton > button span {
            color: white !important;
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
        Già creato form Mappe Postazioni OLD RIMOSSO con Tipo Emergenza/Evento + mappa unica.
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
        st.metric("Mappe Postazioni", len(st.session_state.mappe))

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
            # CASELLA COMBO PER SCEGLIERE LE ODV - lista completa
            odv_lista = [
                "ANA Varese", "ANA Milano", "ANA Como", "ANA Bergamo", "ANA Brescia", "ANA Torino", "ANA Sezione Varese",
                "Protezione Civile Varese", "Protezione Civile Lombardia", "Protezione Civile Nazionale",
                "Croce Rossa Italiana - Varese", "Croce Rossa Italiana - Milano", "Misericordia", "ANPAS",
                "Associazione Nazionale Alpini", "Gruppo Comunale Volontari", "AIB - Antincendio Boschivo",
                "Altro"
            ]
            # Se valore esistente non in lista, aggiungilo
            if odv_app_def and odv_app_def not in odv_lista:
                odv_lista = [odv_app_def] + odv_lista
            
            odv_app = st.selectbox("ODV Associazione di Appartenenza *", odv_lista, index=odv_lista.index(odv_app_def) if odv_app_def in odv_lista else 0, key="vol_odv_app")
            if odv_app == "Altro":
                odv_app_custom = st.text_input("Specifica ODV - Inserisci nome", value="" if odv_app_def in odv_lista else odv_app_def, key="vol_odv_custom", placeholder="Es: Protezione Civile Busto Arsizio")
                if odv_app_custom:
                    odv_app = odv_app_custom
            data_nascita = st.date_input("Data Nascita", value=date(1990,1,1), format="DD/MM/YYYY", key="vol_data_nasc")
            codice_fisc = st.text_input("Codice Fiscale", value=edit_data.get("CodFisc",""), key="vol_cf")
            
            # FOTO NELLA PRIMA MASCHERA + DOWNLOAD
            st.markdown("**📸 Foto Volontario - Prima Maschera**")
            foto_file_prima = st.file_uploader("Carica foto (prima maschera)", type=["jpg", "jpeg", "png"], key="vol_foto_prima")
            if foto_file_prima:
                foto_bytes_prima = foto_file_prima.getvalue()
                st.image(foto_bytes_prima, width=120, caption="Preview prima maschera")
                # Salva in session per uso globale
                st.session_state["foto_temp_prima"] = foto_bytes_prima
                st.download_button("⬇️ Download Foto", data=foto_bytes_prima, file_name=f"foto_{nome}_{cognome}.jpg", mime="image/jpeg", use_container_width=True, key="download_foto_prima")
            elif edit_mode and edit_data.get("FotoBytes"):
                try:
                    st.image(edit_data.get("FotoBytes"), width=120, caption="Foto esistente")
                    st.download_button("⬇️ Download Foto Esistente", data=edit_data.get("FotoBytes"), file_name=f"foto_{edit_data.get('Cognome','')}_{edit_data.get('Nome','')}.jpg", mime="image/jpeg", use_container_width=True, key="download_foto_esistente_prima")
                except:
                    pass

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
        foto_preview = st.session_state.get("foto_temp_prima", None)
        if foto_file:
            foto_bytes = foto_file.getvalue()
            st.image(foto_bytes, width=150, caption="Preview")
            foto_preview = foto_bytes
            st.download_button("⬇️ Download Foto Volontario", data=foto_bytes, file_name=f"foto_{nome}_{cognome}.jpg", mime="image/jpeg", use_container_width=True, key="download_foto_tab")
        elif edit_mode and edit_data.get("FotoBytes"):
            try:
                st.image(edit_data.get("FotoBytes"), width=150, caption="Foto esistente")
                foto_preview = edit_data.get("FotoBytes")
                st.download_button("⬇️ Download Foto", data=edit_data.get("FotoBytes"), file_name=f"foto_{edit_data.get('Cognome','')}.jpg", mime="image/jpeg", use_container_width=True, key="download_foto_tab_edit")
            except:
                pass
        elif foto_preview:
            st.image(foto_preview, width=150, caption="Foto da prima maschera")
            st.download_button("⬇️ Download Foto da Prima Maschera", data=foto_preview, file_name=f"foto_{nome}_{cognome}.jpg", mime="image/jpeg", use_container_width=True, key="download_foto_da_prima")

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
            <div style="background:{bg_m};color:{txt_m};padding:8px;
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

    if st.button("Salva in Mappe Postazioni", type="primary", use_container_width=True):
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
        st.markdown("**Riepilogo Mappe Postazioni con Filtri Tipo**")
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

        st.download_button("Excel Mappe Postazioni", to_excel(df_map), "mappe_fusione.xlsx", use_container_width=True)
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

# MAPPE POSTAZIONI - STABILE - MARKER RIMANGONO - TABELLA SOTTO - ANTEPRIMA SOTTO TABELLA - NOME EMERGENZA/EVENTO COMBO
elif cur == "Mappe Postazioni":
    hdr()
    hdr_form("MAPPE POSTAZIONI - Postazioni + Marker - Stabile")

    # Init stabile
    if "mappa_avanzata_markers" not in st.session_state:
        st.session_state.mappa_avanzata_markers = []
    if "last_clicked_lat" not in st.session_state:
        st.session_state.last_clicked_lat = ""
    if "last_clicked_lon" not in st.session_state:
        st.session_state.last_clicked_lon = ""
    if "map_focus" not in st.session_state:
        st.session_state.map_focus = None
    if "selected_icon_label" not in st.session_state:
        st.session_state.selected_icon_label = ""

    # Recupera liste emergenze ed eventi per combo
    emergenze_list = st.session_state.get("emergenze", [])
    eventi_list = st.session_state.get("eventi", [])
    nomi_emergenze = ["-- Nessuna --"] + [f"{e.get('Nome','')} - {e.get('Data','')}" for e in emergenze_list[-20:]] if emergenze_list else ["-- Nessuna --"]
    nomi_eventi = ["-- Nessuno --"] + [f"{ev.get('Nome','')} - {ev.get('Data','')}" for ev in eventi_list[-20:]] if eventi_list else ["-- Nessuno --"]

    # TOP BAR
    c1, c2, c3, c4 = st.columns([1,1,1,2])
    with c1:
        if st.button("⛶ Fullscreen", key="btn_fs_mappa", use_container_width=True, type="primary"):
            st.session_state["fs_mappa_active"] = True
    with c2:
        if st.button("🧹 Pulisci TUTTI", key="btn_clear_all_markers", use_container_width=True):
            st.session_state.mappa_avanzata_markers = []
            st.session_state.map_focus = None
            st.success("Tutti i marker rimossi")
            st.rerun()
    with c3:
        if st.button("🎯 Mostra tutte", key="btn_fit_all", use_container_width=True):
            st.session_state.map_focus = None
            st.rerun()
    with c4:
        st.markdown(f'<span style="background:#1A5D1A;color:white;padding:6px 12px;border-radius:6px;font-weight:bold;">🗺️ {len(st.session_state.mappa_avanzata_markers)} postazioni - Tutti rimangono</span>', unsafe_allow_html=True)
    # fullscreen fix globale rimosso - ora dentro mappa

    if st.session_state.get("fs_mappa_active"):
        st.components.v1.html("<div style='background:#1A5D1A;color:white;padding:8px;border-radius:6px;text-align:center;'>FULLSCREEN - ESC per uscire</div>", height=40)
        if st.button("❌ Esci Fullscreen", key="btn_exit_fs"):
            st.session_state["fs_mappa_active"] = False
            st.rerun()

    c_tipo1, c_tipo2 = st.columns([1,2])
    with c_tipo1:
        tipo_mappa_ext = st.selectbox("Apri con", ["Google Maps", "Waze", "Google Earth"], index=0, key="tipo_mappa_ext")
    with c_tipo2:
        st.caption("NESSUN default - Click lascia marker - Tutti rimangono - Non si cancellano da soli")

    # LIBRERIA ICONE scelta rapida
    icone_disponibili = st.session_state.get("icone", [])
    if not icone_disponibili:
        icone_disponibili = [
            {"Nome": "Postazione", "Emoji": "⛑️", "Tipo": "Postazione", "Colore": "green"},
            {"Nome": "Emergenza", "Emoji": "🚨", "Tipo": "Emergenza", "Colore": "red"},
            {"Nome": "Evento", "Emoji": "📅", "Tipo": "Evento", "Colore": "blue"},
            {"Nome": "Mezzo", "Emoji": "🚐", "Tipo": "Mezzo", "Colore": "green"},
        ]
    icone_options = []
    icone_map = {}
    for ico in icone_disponibili:
        label = f"{ico.get('Emoji','📍')} {ico.get('Nome','')} - {ico.get('Tipo','')} ({ico.get('Colore','')})"
        icone_options.append(label)
        icone_map[label] = ico
    if not st.session_state.selected_icon_label and icone_options:
        st.session_state.selected_icon_label = icone_options[0]

    st.markdown("**Scegli icona dalla Libreria:**")
    cols_ico = st.columns(6)
    for idx, ico in enumerate(icone_disponibili[:12]):
        with cols_ico[idx % 6]:
            is_sel = st.session_state.selected_icon_label and ico.get('Nome','') in st.session_state.selected_icon_label
            if st.button(f"{ico.get('Emoji','📍')} {ico.get('Nome','')}", key=f"sel_ico_{idx}", use_container_width=True, type="primary" if is_sel else "secondary"):
                for opt in icone_options:
                    if ico.get('Nome','') in opt and ico.get('Emoji','') in opt:
                        st.session_state.selected_icon_label = opt
                        break
                st.rerun()

    try:
        default_idx = icone_options.index(st.session_state.selected_icon_label) if st.session_state.selected_icon_label in icone_options else 0
    except:
        default_idx = 0

    # PROCEDURA VISIBILE PER EZIO
    st.markdown("""
    <div style="background:#fffde7;padding:12px;border-radius:8px;border-left:4px solid #FFD700;margin-bottom:12px;">
    <b>📋 PROCEDURA PER SALVARE POSIZIONE:</b><br>
    1. <b>Scegli icona</b> dalla libreria sopra (es: ⛑️ Postazione)<br>
    2. <b>Clicca sulla mappa grande</b> dove vuoi la postazione - vedi marker temporaneo + coordinate in giallo<br>
    3. <b>Controlla maschera</b>: Lat/Lon si compilano da soli, Comune/Via da Nominatim<br>
    4. <b>Scrivi Nome Postazione</b> * obbligatorio (es: Postazione 1 Varese)<br>
    5. <b>Verifica Comune * e Via *</b> - se vuoti scrivili tu<br>
    6. <b>Scegli Emergenza e Evento</b> dalle combo se servono<br>
    7. <b>Clicca 💾 SALVA POSTAZIONE</b> - vedi messaggio verde ✅ SALVATA<br>
    8. <b>Scorri sotto</b>: tabella sotto mappa con tutte le postazioni + anteprima sotto tabella<br>
    9. Tutti i marker rimangono sulla mappa - piccoli - non si cancellano
    </div>
    """, unsafe_allow_html=True)

    # MASCHERA con NOME EMERGENZA e NOME EVENTO COMBO
    st.markdown("#### 📍 Maschera Postazione")

    c1, c2, c3 = st.columns(3)
    with c1:
        marker_nome = st.text_input("Nome Postazione *", key="adv_marker_nome", placeholder="Es: Postazione 1")
        marker_lat = st.text_input("Latitudine *", value=st.session_state.last_clicked_lat, key="adv_marker_lat", placeholder="Clicca mappa")
        marker_lon = st.text_input("Longitudine *", value=st.session_state.last_clicked_lon, key="adv_marker_lon", placeholder="Clicca mappa")
    with c2:
        marker_comune = st.text_input("Comune *", value="Varese", key="adv_marker_comune")
        marker_via = st.text_input("Via *", value="", key="adv_marker_via", placeholder="Via + civico")
        # CAMPI COMBO RICHIESTI
        nome_emergenza = st.selectbox("Nome Emergenza (combo)", nomi_emergenze, index=0, key="nome_emergenza_combo")
        nome_evento = st.selectbox("Nome Evento (combo)", nomi_eventi, index=0, key="nome_evento_combo")
    with c3:
        marker_icona_label = st.selectbox("Icona Libreria", icone_options, index=default_idx, key="adv_marker_icona_select")
        st.session_state.selected_icon_label = marker_icona_label
        selected_ico_obj = icone_map.get(marker_icona_label, {"Emoji":"⛑️","Nome":"Postazione","Colore":"green","Tipo":"Postazione"})
        st.markdown(f"<div style='font-size:24px;text-align:center;background:#e8f5e9;padding:8px;border-radius:8px;border:2px solid #1A5D1A;'>{selected_ico_obj.get('Emoji','⛑️')} {selected_ico_obj.get('Nome','')}</div>", unsafe_allow_html=True)
        marker_tipo = st.selectbox("Tipo", ["Postazione", "Emergenza", "Evento", "Mezzo", "Volontario"], key="adv_marker_tipo")
        marker_desc = st.text_input("Descrizione", key="adv_marker_desc")

    # SALVA
    col_save1, col_save2 = st.columns([3,1])
    with col_save1:
        save_clicked = st.button("💾 SALVA POSTAZIONE - RIMANE su mappa", type="primary", use_container_width=True, key="btn_salva_postazione")
    with col_save2:
        if st.button("🔄 Pulisci campi", use_container_width=True, key="btn_pulisci_campi"):
            st.session_state.last_clicked_lat = ""
            st.session_state.last_clicked_lon = ""
            st.session_state.map_focus = None
            st.rerun()

    # Recupera coordinate da query params se presenti (fix per salvataggio)
    try:
        q_params = st.query_params
        qp_lat = q_params.get("lat", "")
        qp_lon = q_params.get("lon", "")
        if qp_lat and qp_lon:
            st.session_state.last_clicked_lat = str(qp_lat)
            st.session_state.last_clicked_lon = str(qp_lon)
            # Pulisci query params dopo lettura
            # st.query_params.clear()  # lascia per debug
    except:
        pass

    if save_clicked:
        # Procedura robusta: prova tutte le fonti possibili per lat/lon
        eff_lat = marker_lat or st.session_state.get("last_clicked_lat") or st.session_state.get("adv_marker_lat") or ""
        eff_lon = marker_lon or st.session_state.get("last_clicked_lon") or st.session_state.get("adv_marker_lon") or ""
        # Prova anche da query params
        try:
            if not eff_lat:
                eff_lat = st.query_params.get("lat", "")
            if not eff_lon:
                eff_lon = st.query_params.get("lon", "")
        except:
            pass

        if not marker_nome:
            st.error("❌ Inserisci Nome Postazione")
            st.info("Procedura: 1) Clicca mappa 2) Scrivi Nome Postazione 3) Verifica Comune/Via 4) Clicca SALVA")
        elif not eff_lat or not eff_lon:
            st.error("❌ Manca Latitudine o Longitudine")
            st.warning("Procedura corretta: Clicca sulla mappa grande → vedi coordinate in giallo → compila Nome → SALVA")
            st.info(f"Debug - Lat: '{eff_lat}' Lon: '{eff_lon}' - last_clicked_lat: '{st.session_state.get('last_clicked_lat')}'")
        else:
            try:
                lat_f = float(str(eff_lat).replace(",", "."))
                lon_f = float(str(eff_lon).replace(",", "."))
                sel_obj = icone_map.get(st.session_state.selected_icon_label, selected_ico_obj)
                nuovo = {
                    "Nome": marker_nome,
                    "Lat": lat_f,
                    "Lon": lon_f,
                    "Comune": marker_comune,
                    "Via": marker_via,
                    "NomeEmergenza": nome_emergenza,
                    "NomeEvento": nome_evento,
                    "Emoji": sel_obj.get("Emoji","⛑️"),
                    "Colore": sel_obj.get("Colore","green"),
                    "IconaNome": sel_obj.get("Nome","Postazione"),
                    "Icona": st.session_state.selected_icon_label,
                    "Tipo": marker_tipo,
                    "Descrizione": marker_desc,
                    "DataIns": datetime.now().strftime("%d/%m/%Y %H:%M")
                }
                st.session_state.mappa_avanzata_markers.append(nuovo)
                st.session_state.map_focus = nuovo
                st.session_state.last_clicked_lat = str(lat_f)
                st.session_state.last_clicked_lon = str(lon_f)
                st.success(f"✅ SALVATA {sel_obj.get('Emoji','⛑️')} {marker_nome} - {marker_comune} {marker_via} - Emergenza: {nome_emergenza} Evento: {nome_evento} - Totale {len(st.session_state.mappa_avanzata_markers)} - Ora vedi tabella sotto mappa")
                # Pulisci query params
                try:
                    st.query_params.clear()
                except:
                    pass
                st.rerun()
            except Exception as e:
                st.error(f"❌ Errore coordinate: {e}")
                st.info(f"Hai inserito Lat: '{eff_lat}' Lon: '{eff_lon}' - Usa formato 45.8167 8.8333 con punto")

    # ANTEPRIMA SOPRA MAPPA GRANDE
    st.divider()
    st.markdown("#### 🗺️ Anteprima - Mappa piccola sopra mappa grande")
    preview_lat = marker_lat or st.session_state.last_clicked_lat
    preview_lon = marker_lon or st.session_state.last_clicked_lon
    if preview_lat and preview_lon:
        try:
            p_lat = float(str(preview_lat).replace(",", "."))
            p_lon = float(str(preview_lon).replace(",", "."))
            sel_e = selected_ico_obj.get('Emoji','⛑️')
            sel_c = selected_ico_obj.get('Colore','green')
            preview_html = f"""
            <div style="border:2px solid #1A5D1A;border-radius:8px;overflow:hidden;">
            <div style="background:#1A5D1A;color:white;padding:6px;text-align:center;">Anteprima: {sel_e} {marker_nome or 'Nuova'} - {marker_comune} {marker_via} - Emergenza: {nome_emergenza} - Evento: {nome_evento}</div>
            <div id="preview_map_top" style="height:250px;width:100%;"></div>
            </div>
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
            <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
            <script>
            var pMap = L.map('preview_map_top').setView([{p_lat}, {p_lon}], 15);
            L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png').addTo(pMap);
            var colMap = {{'red':'#d32f2f','blue':'#1976d2','green':'#388e3c','orange':'#f57c00','purple':'#7b1fa2'}};
            var cCode = colMap['{sel_c}'] || '#388e3c';
            var pIcon = L.divIcon({{html: "<div style='background:white;border:2px solid " + cCode + ";width:26px;height:26px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:13px;'>"+ "{sel_e}" + "</div>", iconSize: [26,26], iconAnchor: [13,13]}});
            L.marker([{p_lat}, {p_lon}], {{icon: pIcon}}).addTo(pMap).bindPopup("{sel_e} Anteprima").openPopup();
            </script>
            """
            st.components.v1.html(preview_html, height=300)
        except:
            st.info("Anteprima non disponibile - clicca mappa grande")
    else:
        st.info("Clicca mappa grande per anteprima qui")

    # MAPPA GRANDE - NESSUN DEFAULT - MARKER RIMANGONO
    st.divider()
    all_markers = st.session_state.get("mappa_avanzata_markers", [])
    focus_marker = st.session_state.get("map_focus")

    import json as json_lib
    markers_for_js = json_lib.dumps([{"lat": m["Lat"], "lon": m["Lon"], "nome": m["Nome"], "emoji": m.get("Emoji","⛑️"), "colore": m.get("Colore","green"), "iconaNome": m.get("IconaNome",""), "comune": m.get("Comune",""), "via": m.get("Via",""), "emergenza": m.get("NomeEmergenza",""), "evento": m.get("NomeEvento","")} for m in all_markers])
    focus_for_js = json_lib.dumps(focus_marker) if focus_marker else "null"

    st.markdown("#### 🌍 Mappa Grande - Tutti i marker rimangono - Non si cancellano")
    html_code = """
    <div id="map-container" style="position:relative; background:white; border-radius:12px;">
        <div id="map" style="height:650px; width:100%; border-radius:12px; border:3px solid #1A5D1A;"></div>
    </div>
    <div id="coords" style="background:#fffde7;padding:8px;border-radius:6px;margin-top:8px;font-weight:bold;border-left:4px solid #FFD700;">📍 Clicca per aggiungere - Tutti rimangono</div>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script>
    var markersData = MARKERS_JSON_PLACEHOLDER;
    var focusMarker = FOCUS_JSON_PLACEHOLDER;
    var selectedIconEmoji = SELECTED_EMOJI_PLACEHOLDER;
    var selectedIconColor = SELECTED_COLOR_PLACEHOLDER;
    var map = L.map('map', {zoomControl: false}).setView([45.8167, 8.8333], 13);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {attribution: 'ANA Varese'}).addTo(map);
    L.control.zoom({position: 'topleft'}).addTo(map);
    function getColorCode(c){ var m={'red':'#d32f2f','blue':'#1976d2','green':'#388e3c','orange':'#f57c00','purple':'#7b1fa2'}; return m[c]||'#388e3c'; }
    var allMarkers = [];
    // MARKER SALVATI - RIMANGONO - PICCOLI
    markersData.forEach(function(md){
        var icon = L.divIcon({html: "<div style='background:white;border:2px solid " + getColorCode(md.colore) + ";width:26px;height:26px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:12px;box-shadow:0 2px 4px rgba(0,0,0,0.3);'>" + md.emoji + "</div>", iconSize: [26,26], iconAnchor: [13,13]});
        var mk = L.marker([md.lat, md.lon], {icon: icon}).addTo(map).bindPopup("<b>" + md.emoji + " " + md.nome + "</b><br>Comune: " + md.comune + "<br>Via: " + md.via + "<br>Emergenza: " + md.emergenza + "<br>Evento: " + md.evento);
        allMarkers.push(mk);
    });
    if (focusMarker && focusMarker.Lat){
        map.setView([focusMarker.Lat, focusMarker.Lon], 16);
        // Apri popup del focus
        for(var i=0;i<markersData.length;i++){
            if(markersData[i].lat==focusMarker.Lat && markersData[i].lon==focusMarker.Lon){
                allMarkers[i].openPopup();
                break;
            }
        }
        document.getElementById('coords').innerHTML = "📍 Focus: " + focusMarker.Emoji + " " + focusMarker.Nome + " - " + focusMarker.Comune + " " + focusMarker.Via;
    } else {
        if(allMarkers.length>0){
            var g = new L.featureGroup(allMarkers);
            map.fitBounds(g.getBounds().pad(0.3));
            document.getElementById('coords').innerHTML = "📍 " + markersData.length + " postazioni - Tutti rimangono - Clicca tabella per focus";
        } else {
            document.getElementById('coords').innerHTML = "📍 Nessun marker - Mappa vuota - Clicca per aggiungere - Tutti rimangono quando salvati";
        }
    }
    map.on('click', function(e){
        var lat = e.latlng.lat.toFixed(6);
        var lon = e.latlng.lng.toFixed(6);
        // Sincronizza con Python via query params - per salvataggio robusto
        try {
            var url = new URL(window.parent.location.href);
            url.searchParams.set('lat', lat);
            url.searchParams.set('lon', lon);
            window.parent.history.replaceState(null, '', url.toString());
        } catch(err) { console.log(err); }

        var tmpIcon = L.divIcon({html: "<div style='background:#e8f5e9;border:2px dashed " + getColorCode(selectedIconColor) + ";width:30px;height:30px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:14px;'>" + selectedIconEmoji + "</div>", iconSize: [30,30], iconAnchor: [15,15]});
        var nm = L.marker([lat, lon], {draggable:true, icon: tmpIcon}).addTo(map).bindPopup("Nuova - " + selectedIconEmoji + "<br>" + lat + "," + lon).openPopup();
        document.getElementById('coords').innerHTML = "📍 Nuovo " + selectedIconEmoji + " " + lat + "," + lon + " - Compila e salva - Rimane dopo salvataggio";
        try{
            var pd = window.parent.document;
            var inputs = pd.querySelectorAll('input[type="text"]');
            inputs.forEach(function(inp){
                var lb = inp.getAttribute('aria-label')||'';
                if(lb.includes('Latitudine')){ inp.value=lat; inp.dispatchEvent(new Event('input',{bubbles:true})); }
                if(lb.includes('Longitudine')){ inp.value=lon; inp.dispatchEvent(new Event('input',{bubbles:true})); }
            });
            fetch('https://nominatim.openstreetmap.org/reverse?format=json&lat='+lat+'&lon='+lon)
                .then(r=>r.json()).then(d=>{
                    var com = d.address.city||d.address.town||d.address.village||"";
                    var via = d.address.road||"";
                    document.getElementById('coords').innerHTML += "<br>Comune: "+com+" Via: "+via;
                    inputs.forEach(function(inp){
                        var lb = inp.getAttribute('aria-label')||'';
                        if(lb.includes('Comune *')){ inp.value=com; inp.dispatchEvent(new Event('input',{bubbles:true})); }
                        if(lb.includes('Via *')){ inp.value=via; inp.dispatchEvent(new Event('input',{bubbles:true})); }
                    });
                });
        }catch(err){ console.log(err); }
    });
    </script>
    """
    import json as json_lib2
    sel_e = selected_ico_obj.get('Emoji','⛑️')
    sel_c = selected_ico_obj.get('Colore','green')
    html_code = html_code.replace("MARKERS_JSON_PLACEHOLDER", markers_for_js)
    html_code = html_code.replace("FOCUS_JSON_PLACEHOLDER", focus_for_js)
    html_code = html_code.replace("SELECTED_EMOJI_PLACEHOLDER", json_lib2.dumps(sel_e))
    html_code = html_code.replace("SELECTED_COLOR_PLACEHOLDER", json_lib2.dumps(sel_c))

    # FIX DEFINITIVO FULLSCREEN SOTTO + - DENTRO MAPPA - INIETTA JS DENTRO HTML_CODE
    try:
        # Inserisci bottone fullscreen dentro html_code prima di </script>
        fs_js = """ 
    // FIX FULLSCREEN 100% SOTTO + -
    try {
        var fsControl = L.control({position: 'topleft'});
        fsControl.onAdd = function(map) {
            var container = L.DomUtil.create('div', 'leaflet-bar leaflet-control');
            container.style.marginTop = '5px';
            var btn = L.DomUtil.create('a', '', container);
            btn.innerHTML = '⛶';
            btn.href = '#';
            btn.title = 'Schermo intero 100%';
            btn.style.width = '34px';
            btn.style.height = '34px';
            btn.style.lineHeight = '34px';
            btn.style.textAlign = 'center';
            btn.style.fontSize = '22px';
            btn.style.background = 'white';
            btn.style.display = 'block';
            btn.style.textDecoration = 'none';
            btn.style.color = 'black';
            btn.style.fontWeight = 'bold';
            btn.style.border = '2px solid rgba(0,0,0,0.2)';
            btn.style.borderRadius = '4px';
            L.DomEvent.on(btn, 'click', function(e){
                L.DomEvent.stop(e);
                var mapContainer = document.getElementById('map');
                if (!document.fullscreenElement) {
                    if (mapContainer.requestFullscreen) mapContainer.requestFullscreen();
                    else if (mapContainer.webkitRequestFullscreen) mapContainer.webkitRequestFullscreen();
                    else if (mapContainer.msRequestFullscreen) mapContainer.msRequestFullscreen();
                    setTimeout(function(){ map.invalidateSize(); }, 600);
                } else {
                    if (document.exitFullscreen) document.exitFullscreen();
                    setTimeout(function(){ map.invalidateSize(); }, 600);
                }
            });
            return container;
        };
        fsControl.addTo(map);
    } catch(e){}
    """
        html_code = html_code.replace("</script>", fs_js + "\n</script>")
    except Exception as _e:
        pass


    # FIX DEFINITIVO FULLSCREEN 100% SOTTO + - DENTRO MAPPA GRANDE
    try:
        fs_js_big = """
    // FIX FULLSCREEN 100% SOTTO + - PER MAPPA GRANDE
    try {
        var fsControl = L.control({position: 'topleft'});
        fsControl.onAdd = function(map) {
            var container = L.DomUtil.create('div', 'leaflet-bar leaflet-control');
            container.style.marginTop = '5px';
            var btn = L.DomUtil.create('a', '', container);
            btn.innerHTML = '⛶';
            btn.href = '#';
            btn.title = 'Espandi mappa tutto schermo';
            btn.style.width = '34px';
            btn.style.height = '34px';
            btn.style.lineHeight = '34px';
            btn.style.textAlign = 'center';
            btn.style.fontSize = '22px';
            btn.style.background = 'white';
            btn.style.display = 'block';
            btn.style.textDecoration = 'none';
            btn.style.color = 'black';
            btn.style.fontWeight = 'bold';
            btn.style.border = '2px solid rgba(0,0,0,0.2)';
            btn.style.borderRadius = '4px';
            btn.style.cursor = 'pointer';
            L.DomEvent.on(btn, 'click', function(e){
                L.DomEvent.stop(e);
                var mapContainer = document.getElementById('map');
                if (mapContainer) {
                    if (!document.fullscreenElement) {
                        if (mapContainer.requestFullscreen) mapContainer.requestFullscreen();
                        else if (mapContainer.webkitRequestFullscreen) mapContainer.webkitRequestFullscreen();
                        else if (mapContainer.msRequestFullscreen) mapContainer.msRequestFullscreen();
                        setTimeout(function(){ map.invalidateSize(); }, 600);
                    } else {
                        if (document.exitFullscreen) document.exitFullscreen();
                        setTimeout(function(){ map.invalidateSize(); }, 600);
                    }
                }
            });
            return container;
        };
        fsControl.addTo(map);
    } catch(e){ console.log('fs big error', e); }
"""
        html_code = html_code.replace("</script>", fs_js_big + "\n</script>")
    except Exception as _e:
        pass

    st.components.v1.html(html_code, height=700)

    # TABELLA SOTTO MAPPA COME PRIMA - CON COMUNE + VIA + EMERGENZA + EVENTO
    st.divider()
    st.markdown(f"### 📋 Tabella Postazioni - {len(all_markers)} salvate - Sotto mappa come prima")
    if all_markers:
        st.success(f"✅ {len(all_markers)} postazioni - Marker rimangono sulla mappa - Piccoli")
        for idx, m in enumerate(all_markers):
            is_focus = focus_marker and str(focus_marker.get('Lat')) == str(m['Lat']) and focus_marker.get('Nome')==m['Nome']
            bg = "#fffde7" if is_focus else "white"
            border = "#FFD700" if is_focus else "#1A5D1A"
            c1, c2, c3, c4 = st.columns([1,2,2,2])
            with c1:
                st.markdown(f"<div style='background:{bg};padding:6px;border-radius:8px;border:2px solid {border};text-align:center;'><div style='font-size:22px;'>{m.get('Emoji','⛑️')}</div><div style='font-size:10px;'>{m.get('IconaNome','')}</div></div>", unsafe_allow_html=True)
                if is_focus:
                    st.caption("👆 IN VISTA")
            with c2:
                st.write(f"**{m['Nome']}**")
                st.caption(f"Tipo: {m.get('Tipo','')}")
                st.caption(f"Emergenza: {m.get('NomeEmergenza','--')}")
                st.caption(f"Evento: {m.get('NomeEvento','--')}")
            with c3:
                st.markdown(f"**Comune:** {m.get('Comune','')}")
                st.markdown(f"**Via:** {m.get('Via','')}")
                st.caption(f"Lat: {m['Lat']} Lon: {m['Lon']}")
            with c4:
                if st.button("📍 Vedi su mappa", key=f"focus_{idx}", use_container_width=True, type="primary" if is_focus else "secondary"):
                    st.session_state.map_focus = m
                    st.rerun()
                col_del, col_dup = st.columns(2)
                with col_del:
                    if st.button("🗑️", key=f"del_{idx}", use_container_width=True):
                        st.session_state.mappa_avanzata_markers.pop(idx)
                        if is_focus:
                            st.session_state.map_focus = None
                        st.rerun()
                with col_dup:
                    if st.button("📋", key=f"dup_{idx}", use_container_width=True):
                        nm = m.copy()
                        nm["Nome"] = m["Nome"] + " copia"
                        st.session_state.mappa_avanzata_markers.append(nm)
                        st.rerun()
            st.divider()

        # Export e pulizia
        c_exp1, c_exp2 = st.columns(2)
        with c_exp1:
            df_exp = pd.DataFrame(all_markers)
            st.download_button("⬇️ Excel Postazioni", data=to_excel(df_exp), file_name="postazioni.xlsx", use_container_width=True)
        with c_exp2:
            if st.button("🧹 Pulisci TUTTI", key="clear_bottom", use_container_width=True):
                st.session_state.mappa_avanzata_markers = []
                st.session_state.map_focus = None
                st.rerun()

        # MAPPA ANTEPRIMA SOTTO TABELLA - RICHIESTA EZIO
        st.divider()
        st.markdown("#### 🗺️ Anteprima sotto tabella - Mappa con tutte le postazioni")
        try:
            # Crea mappa anteprima con tutte le postazioni
            preview_all_html = """
            <div style="border:2px solid #1A5D1A;border-radius:8px;overflow:hidden;">
            <div style="background:#1A5D1A;color:white;padding:6px;text-align:center;">Anteprima sotto tabella - Tutte le postazioni - """ + str(len(all_markers)) + """ marker - Piccoli</div>
            <div id="preview_bottom" style="height:400px;width:100%;"></div>
            </div>
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
            <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
            <script>
            var markersDataBottom = """ + markers_for_js + """;
            var mapB = L.map('preview_bottom').setView([45.8167, 8.8333], 12);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(mapB);
            function getColorCodeB(c){ var m={'red':'#d32f2f','blue':'#1976d2','green':'#388e3c','orange':'#f57c00','purple':'#7b1fa2'}; return m[c]||'#388e3c'; }
            var allB = [];
            markersDataBottom.forEach(function(md){
                var ic = L.divIcon({html: "<div style='background:white;border:2px solid " + getColorCodeB(md.colore) + ";width:22px;height:22px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:10px;'>" + md.emoji + "</div>", iconSize: [22,22], iconAnchor: [11,11]});
                var mk = L.marker([md.lat, md.lon], {icon: ic}).addTo(mapB).bindPopup(md.emoji + " " + md.nome + "<br>" + md.comune + " " + md.via);
                allB.push(mk);
            });
            if(allB.length>0){
                var gB = new L.featureGroup(allB);
                mapB.fitBounds(gB.getBounds().pad(0.3));
            }
            </script>
            """
            st.components.v1.html(preview_all_html, height=450)
        except Exception as e:
            st.error(f"Errore anteprima: {e}")

    else:
        st.info("📍 Nessuna postazione salvata - Tabella apparirà qui dopo salvataggio - Clicca mappa grande sopra per aggiungere - Marker rimarranno")
        st.markdown("""
        <div style="background:#fffde7;padding:12px;border-radius:8px;text-align:center;">
        <b>Mappa anteprima sotto tabella apparirà quando salvi la prima postazione</b><br>
        1. Clicca mappa grande<br>2. Compila maschera (Comune, Via, Emergenza, Evento)<br>3. Salva - Tabella sotto mappa + anteprima sotto tabella
        </div>
        """, unsafe_allow_html=True)

# LIBRERIA ICONE



# TURNI - RIPRISTINATO DEFINITIVO
elif cur == "Turni":
    hdr()
    hdr_form("TURNI - Gestione Turni Volontari")
    if "turni" not in st.session_state:
        st.session_state.turni = []
    tab1, tab2 = st.tabs(["➕ Nuovo Turno", "📋 Elenco Turni"])
    with tab1:
        c1, c2, c3 = st.columns(3)
        with c1:
            data_turno = st.date_input("Data Turno *", value=date.today(), format="DD/MM/YYYY", key="turno_data")
            ora_inizio = st.time_input("Ora Inizio *", value=time(8,0), key="turno_ora_in")
            ora_fine = st.time_input("Ora Fine *", value=time(12,0), key="turno_ora_fine")
        with c2:
            volontari_list = st.session_state.get("volontari", [])
            nomi_vol = [f"{v.get('Cognome','')} {v.get('Nome','')} - {v.get('Telefono','')}" for v in volontari_list] if volontari_list else ["-- Nessun volontario --"]
            volontario_sel = st.selectbox("Volontario *", nomi_vol, key="turno_volontario")
            tipo_turno = st.selectbox("Tipo Turno *", ["Mattina", "Pomeriggio", "Sera", "Notte", "Reperibilità", "Emergenza", "Evento", "Formazione", "Altro"], key="turno_tipo")
            luogo_turno = combo_comune("Luogo / Comune", "turno_comune", "Varese")
        with c3:
            via_turno = combo_vie("Via", luogo_turno, "turno_via", "")
            stato_turno = st.selectbox("Stato", ["Programmato", "Confermato", "In Corso", "Completato", "Annullato"], key="turno_stato")
            note_turno = st.text_area("Note Turno", key="turno_note")
            bg_t, txt_t, lab_t = get_stato_color(stato_turno)
            st.markdown(f'<div style="background:{bg_t};color:{txt_t};padding:6px;border-radius:6px;text-align:center;">{lab_t}: {stato_turno}</div>', unsafe_allow_html=True)
        if st.button("💾 Salva Turno", type="primary", use_container_width=True, key="btn_salva_turno"):
            if volontario_sel and volontario_sel != "-- Nessun volontario --":
                nuovo_turno = {
                    "Data": str(data_turno),
                    "OraInizio": str(ora_inizio),
                    "OraFine": str(ora_fine),
                    "Volontario": volontario_sel,
                    "Tipo": tipo_turno,
                    "Comune": luogo_turno,
                    "Via": via_turno,
                    "Stato": stato_turno,
                    "Note": note_turno,
                    "DataIns": datetime.now().strftime("%d/%m/%Y %H:%M")
                }
                st.session_state.turni.append(nuovo_turno)
                st.success(f"✅ Turno salvato: {volontario_sel} - {data_turno}")
                st.rerun()
            else:
                st.error("Seleziona volontario")
    with tab2:
        if st.session_state.turni:
            df_turni = pd.DataFrame(st.session_state.turni)
            st.dataframe(df_turni, use_container_width=True)
            for idx, row in enumerate(st.session_state.turni):
                c1, c2, c3 = st.columns([4,1,1])
                bg, txt, lab = get_stato_color(row.get("Stato","Programmato"))
                c1.markdown(f"**{row.get('Data','')} {row.get('OraInizio','')}-{row.get('OraFine','')}** - {row.get('Volontario','')} - {row.get('Tipo','')} - {row.get('Comune','')} {row.get('Via','')}")
                c2.markdown(f"<span style='background:{bg};color:{txt};padding:4px 8px;border-radius:4px;'>{row.get('Stato','')}</span>", unsafe_allow_html=True)
                if c3.button("🗑️", key=f"del_turno_{idx}"):
                    st.session_state.turni.pop(idx)
                    st.rerun()
            if REPORTLAB_OK:
                st.download_button("📄 PDF Turni", data=to_pdf(df_turni, "TURNI"), file_name="turni.pdf", mime="application/pdf", use_container_width=True, key="pdf_turni_final")
            st.download_button("📊 Excel Turni", data=to_excel(df_turni), file_name="turni.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True, key="excel_turni_final")
        else:
            st.info("Nessun turno salvato")


elif cur == "Libreria Icone":
    hdr()
    hdr_form("LIBRERIA ICONE - Scegli tu il marker da usare su Mappe Postazioni")

    st.markdown("""
    <div style="background:#e8f5e9;padding:8px;border-radius:8px;border-left:4px solid #1A5D1A;margin-bottom:12px;">
    <b>Qui crei le icone che poi usi su Mappe Postazioni - Decidi tu che marker usare - Ogni icona ha Emoji + Colore + Nome</b>
    </div>
    """, unsafe_allow_html=True)

    # Icone predefinite se vuoto
    if not st.session_state.icone:
        st.session_state.icone = [
            {"Nome": "Emergenza", "Emoji": "🚨", "Tipo": "Emergenza", "Colore": "red", "Descrizione": "Emergenza", "Data": datetime.now().strftime("%d/%m/%Y")},
            {"Nome": "Evento", "Emoji": "📅", "Tipo": "Evento", "Colore": "blue", "Descrizione": "Evento", "Data": datetime.now().strftime("%d/%m/%Y")},
            {"Nome": "Mezzo", "Emoji": "🚐", "Tipo": "Mezzo", "Colore": "green", "Descrizione": "Mezzo", "Data": datetime.now().strftime("%d/%m/%Y")},
            {"Nome": "Volontario", "Emoji": "👤", "Tipo": "Volontario", "Colore": "orange", "Descrizione": "Volontario", "Data": datetime.now().strftime("%d/%m/%Y")},
            {"Nome": "Ospedale", "Emoji": "🏥", "Tipo": "Emergenza", "Colore": "red", "Descrizione": "Ospedale", "Data": datetime.now().strftime("%d/%m/%Y")},
            {"Nome": "Incendio", "Emoji": "🔥", "Tipo": "Emergenza", "Colore": "red", "Descrizione": "Incendio", "Data": datetime.now().strftime("%d/%m/%Y")},
            {"Nome": "Alluvione", "Emoji": "💧", "Tipo": "Emergenza", "Colore": "blue", "Descrizione": "Alluvione", "Data": datetime.now().strftime("%d/%m/%Y")},
            {"Nome": "Radio", "Emoji": "📻", "Tipo": "Mezzo", "Colore": "purple", "Descrizione": "Radio", "Data": datetime.now().strftime("%d/%m/%Y")},
        ]

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        nome_icona = st.text_input("Nome Icona *", key="ico_nome", placeholder="Es: Postazione 1")
        emoji_icona = st.text_input("Emoji Icona *", value="📍", key="ico_emoji", help="Inserisci emoji: 🚨 📅 🚐 👤 🏥 🔥 💧 📻 ⛑️ 🚒 🚑")
    with c2:
        tipo_icona = st.selectbox("Tipo", ["Emergenza", "Evento", "Mezzo", "Volontario", "Postazione", "Punto Interesse", "Altro"], key="ico_tipo")
        colore_icona = st.selectbox("Colore Marker", ["red", "blue", "green", "orange", "purple", "darkred", "darkblue", "cadetblue"], key="ico_colore")
    with c3:
        desc_icona = st.text_input("Descrizione Icona", key="ico_desc", placeholder="Descrizione")
        file_icona = st.file_uploader("File Icona (opzionale)", type=["png", "jpg", "svg"], key="ico_file")
    with c4:
        st.markdown("**Anteprima**")
        preview_emoji = st.session_state.get("ico_emoji", "📍") if "ico_emoji" in st.session_state else emoji_icona
        st.markdown(f"<div style='font-size:40px;text-align:center;background:white;padding:10px;border-radius:8px;border:2px solid #1A5D1A;'>{preview_emoji}</div>", unsafe_allow_html=True)

    if st.button("💾 Salva Icona in Libreria", type="primary", use_container_width=True):
        if nome_icona and emoji_icona:
            # Controlla se esiste già
            exists = False
            for ico in st.session_state.icone:
                if ico.get("Nome") == nome_icona:
                    exists = True
                    break
            if not exists:
                st.session_state.icone.append({
                    "Nome": nome_icona,
                    "Emoji": emoji_icona,
                    "Tipo": tipo_icona,
                    "Colore": colore_icona,
                    "Descrizione": desc_icona,
                    "Data": datetime.now().strftime("%d/%m/%Y %H:%M")
                })
                st.success(f"Icona {emoji_icona} {nome_icona} salvata - Ora la puoi usare su Mappe Postazioni")
                st.rerun()
            else:
                st.warning("Nome già esistente - cambia nome")
        else:
            st.error("Nome e Emoji obbligatori")

    st.divider()
    st.markdown(f"### Libreria Icone - {len(st.session_state.icone)} icone disponibili - Le usi su Mappe Postazioni")

    if st.session_state.icone:
        cols = st.columns(4)
        for idx, ico in enumerate(st.session_state.icone):
            col = cols[idx % 4]
            with col:
                st.markdown(f"""
                <div style="background:white;padding:8px;border-radius:8px;border:2px solid #1A5D1A;text-align:center;margin-bottom:8px;">
                <div style="font-size:32px;">{ico.get('Emoji','📍')}</div>
                <b>{ico.get('Nome','')}</b><br>
                <small>{ico.get('Tipo','')} - {ico.get('Colore','')}</small><br>
                <small>{ico.get('Descrizione','')}</small>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"🗑️ Elimina", key=f"del_ico_{idx}"):
                    st.session_state.icone.pop(idx)
                    st.rerun()
        st.divider()
        df_ico = pd.DataFrame(st.session_state.icone)
        st.dataframe(df_ico, use_container_width=True)
        st.download_button("Excel Libreria Icone", to_excel(df_ico), "libreria_icone.xlsx", use_container_width=True)
    else:
        st.info("Nessuna icona - Crea la prima icona sopra")

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
        <div style="background:#e8f5e9;padding:8px;border-radius:8px;
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
        "Turni": "turni",
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
    <div style="text-align:center;padding:8px;background:linear-gradient(135deg,#1A5D1A,#2e7d32);border-radius:8px;color:white;font-size:12px;">
    ANA Varese - Dashboard rosso + bottoni OK | Volontari linguette + ODV | Date gg/mm/aaaa | Backup Import/Export<br>
    Sviluppato per Ezio
    </div>
    """,
    unsafe_allow_html=True
)
