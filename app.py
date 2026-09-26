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

import sys
# FIX DEFINITIVO OPENPYXL per Streamlit Cloud - Ezio
# Su Cloud NON si può fare pip install a runtime, deve stare in requirements.txt
try:
    import openpyxl
    OPENPYXL_OK = True
except Exception:
    OPENPYXL_OK = False

try:
    import xlsxwriter
    XLSXWRITER_OK = True
except Exception:
    XLSXWRITER_OK = False

try:
    import xlrd
    XLRD_OK = True
except Exception:
    XLRD_OK = False


st.set_page_config(
    page_title="ANA Varese 950+ Modifiche Richieste",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Globale - Times New Roman grassetto per tutti + Verde ANA - FIX upload/download storpiati
st.markdown(
    """
    <style>
    /* Solo form e testi normali in Times New Roman bold - NON su upload/download */
    html, body {
        font-family: 'Times New Roman', Times, serif !important;
    }
    p, div, span, label {
        font-family: 'Times New Roman', Times, serif !important;
        font-weight: bold !important;
    }
    .stTextInput label, .stSelectbox label, .stDateInput label, .stTimeInput label, .stTextArea label {
        font-family: 'Times New Roman', Times, serif !important;
        font-weight: bold !important;
        font-size: 14px !important;
        color: black !important;
    }
    /* FIX UPLOAD/DOWNLOAD - Ripristina font normale per non storpiare scritte - Ezio */
    [data-testid="stFileUploader"], [data-testid="stFileUploader"] * {
        font-family: 'Source Sans Pro', sans-serif !important;
        font-weight: normal !important;
    }
    [data-testid="stFileUploader"] button {
        font-family: 'Source Sans Pro', sans-serif !important;
        font-weight: 500 !important;
        font-size: 14px !important;
        background-color: white !important;
        color: black !important;
        border: 1px solid #d0d0d0 !important;
    }
    [data-testid="stFileUploader"] small {
        font-family: 'Source Sans Pro', sans-serif !important;
        font-weight: normal !important;
        font-size: 12px !important;
    }
    /* Fix download button - non storpiare */
    [data-testid="stDownloadButton"] button {
        font-family: 'Times New Roman', Times, serif !important;
        font-weight: bold !important;
        font-size: 13px !important;
        white-space: normal !important;
        line-height: 1.3 !important;
    }
    /* Bottoni dashboard verde ANA */
    div[data-testid="column"] .stButton > button {
        background-color: #1A5D1A !important;
        color: white !important;
        border: 2px solid #1A5D1A !important;
        font-weight: bold !important;
        font-family: 'Times New Roman', serif !important;
        font-size: 13px !important;
        white-space: normal !important;
        line-height: 1.2 !important;
        padding: 6px 8px !important;
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

    /* Fullscreen rosso + 100% */
    button#fs-btn, button[key="btn_fullscreen_dash"], button[key="btn_fs_mappa"] {
        background-color: #ff0000 !important;
        border-color: #ff0000 !important;
    }
    /* Fullscreen 100% tutto schermo */
    :fullscreen {
        width: 100vw !important;
        height: 100vh !important;
    }
    ::backdrop {
        background: white !important;
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
    Esporta DataFrame in Excel - FIX Office 2016 100% compatibile - Ezio
    Usa openpyxl, compatibile Office 2016/2019/365 - MAI CSV travestito
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

    # Assicura che df non sia None
    if df_copy is None or not isinstance(df_copy, pd.DataFrame):
        df_copy = pd.DataFrame()

    # Prova openpyxl prima (100% Office 2016 compatibile)
    last_error = ""
    for engine_try in ["openpyxl", "xlsxwriter"]:
        try:
            buf = BytesIO()
            # Verifica engine disponibile
            if engine_try == "openpyxl" and not OPENPYXL_OK:
                continue
            if engine_try == "xlsxwriter" and not XLSXWRITER_OK:
                continue
            with pd.ExcelWriter(buf, engine=engine_try) as writer:
                df_copy.to_excel(writer, index=False, sheet_name="Dati")
            buf.seek(0)
            data = buf.getvalue()
            # Verifica che sia un vero xlsx (PK zip header)
            if data[:2] == b'PK':
                return data
            else:
                last_error = f"Engine {engine_try} non ha prodotto xlsx valido"
        except Exception as e:
            last_error = str(e)
            continue

    # Ultimo tentativo: forza openpyxl anche se flag dice False (per Cloud)
    try:
        buf = BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            df_copy.to_excel(writer, index=False, sheet_name="Dati")
        buf.seek(0)
        return buf.getvalue()
    except Exception as e:
        last_error = str(e)

    # Se proprio fallisce, crea file Excel minimo con openpyxl diretto
    try:
        import openpyxl
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Dati"
        for c_idx, col_name in enumerate(df_copy.columns, 1):
            ws.cell(row=1, column=c_idx, value=col_name)
        for r_idx, row in enumerate(df_copy.itertuples(index=False), 2):
            for c_idx, val in enumerate(row, 1):
                try:
                    ws.cell(row=r_idx, column=c_idx, value=val)
                except:
                    ws.cell(row=r_idx, column=c_idx, value=str(val))
        buf = BytesIO()
        wb.save(buf)
        buf.seek(0)
        return buf.getvalue()
    except Exception as e:
        # FIX CRASH CLOUD: NON fare raise, ritorna CSV come ultima spiaggia ma con avviso
        # Così app non crasha su Cloud anche se openpyxl manca
        try:
            buf_csv = BytesIO()
            df_copy.to_csv(buf_csv, index=False, encoding='utf-8-sig')
            buf_csv.seek(0)
            # Salva errore in session per mostrare avviso
            return buf_csv.getvalue()
        except:
            # Ritorna bytes vuoti ma non crasha
            return b


def to_excel_multi(datasets):
    """
    datasets = dict nome_sheet -> df - FIX Win7 - NON CRASHA CLOUD
    """
    buf = BytesIO()
    try:
        engine = "openpyxl" if OPENPYXL_OK else ("xlsxwriter" if XLSXWRITER_OK else "openpyxl")
        with pd.ExcelWriter(buf, engine=engine) as writer:
            for sheet_name, df in datasets.items():
                df_copy = df.copy()
                for col in ["FotoBytes", "FileBytes", "FotoConsegnaBytes", "Foto"]:
                    if col in df_copy.columns:
                        df_copy = df_copy.drop(columns=[col])
                safe_name = sheet_name[:30]
                df_copy.to_excel(writer, index=False, sheet_name=safe_name)
        buf.seek(0)
        data = buf.getvalue()
        if data and len(data) > 100:
            return data
        else:
            return to_excel(list(datasets.values())[0] if datasets else pd.DataFrame())
    except Exception as e:
        try:
            return to_excel(list(datasets.values())[0] if datasets else pd.DataFrame())
        except:
            return b''


def excel_import_inline(form_key, form_label):
    """
    Import/Export inline per ogni form - Ezio richiesta - ORA CON PDF
    Ogni form ha Excel + PDF + Template ODV + Import - Office 2016 compatibile
    Lascia tutti campi aggiunti OK
    """
    st.divider()
    st.markdown(f"#### 📥📤 Import/Export - {form_label} - Excel + PDF + Template ODV (Office 2016)")

    c1, c2, c3, c4 = st.columns(4)

    # Export Excel corrente - FIX CRASH CLOUD
    with c1:
        data = st.session_state.get(form_key, [])
        if data:
            clean = [{kk: vv for kk, vv in r.items() if "Bytes" not in kk and "Foto" not in kk and "File" not in kk} for r in data if isinstance(r, dict)]
            if clean:
                df_exp = pd.DataFrame(clean)
                try:
                    excel_data = to_excel(df_exp)
                    if excel_data and len(excel_data) > 100:
                        st.download_button(
                            f"⬇️ Excel {form_label}",
                            data=excel_data,
                            file_name=f"{form_key}_export_{datetime.now().strftime('%Y%m%d')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True,
                            key=f"exp_inline_{form_key}"
                        )
                        st.caption(f"Excel: {len(data)} record")
                    else:
                        st.warning("Excel non disponibile - verifica requirements.txt: openpyxl")
                        st.caption(f"{len(data)} record - Excel disabilitato")
                except Exception as e:
                    st.error(f"Excel errore: {str(e)[:100]}")
                    st.info("Su Streamlit Cloud: verifica requirements.txt contenga openpyxl poi Reboot")
            else:
                st.info("Nessun dato")
        else:
            st.info(f"{form_label} vuoto")

    # Export PDF corrente - NUOVO RICHIESTA EZIO
    with c2:
        data_pdf = st.session_state.get(form_key, [])
        if data_pdf:
            clean_pdf = [{kk: vv for kk, vv in r.items() if "Bytes" not in kk and "Foto" not in kk and "File" not in kk} for r in data_pdf if isinstance(r, dict)]
            if clean_pdf:
                df_pdf = pd.DataFrame(clean_pdf)
                if REPORTLAB_OK:
                    try:
                        pdf_data = to_pdf(df_pdf, form_label.upper())
                        st.download_button(
                            f"📄 PDF {form_label}",
                            data=pdf_data,
                            file_name=f"{form_key}_{datetime.now().strftime('%Y%m%d')}.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                            key=f"pdf_inline_{form_key}",
                            type="primary"
                        )
                        st.caption(f"PDF: {len(data_pdf)} record")
                    except Exception as e:
                        st.error(f"PDF errore: {e}")
                else:
                    st.warning("Reportlab non installato - aggiungi in requirements.txt: reportlab")
            else:
                st.info("Nessun dato PDF")
        else:
            st.info("Nessun dato per PDF")

    # Template vuoto per ODV
    with c3:
        data_existing = st.session_state.get(form_key, [])
        if data_existing and len(data_existing) > 0:
            first = data_existing[0]
            cols = [k for k in first.keys() if "Bytes" not in k and "Foto" not in k and "File" not in k]
            if not cols:
                cols = ["Nome","Cognome","Note"]
        else:
            if form_key == "volontari":
                cols = ["Nome","Cognome","Comune","Via","CapoODV","ODVAppartenenza","DataNascita","CodFisc","Cellulare","Email","TelEmergenza","Ruolo","Squadra","RadioID","Documento","ScadDoc","Note"]
            elif form_key == "radio_db":
                cols = ["ID","Modello","Frequenza","Canale","Note"]
            elif form_key == "consegna_radio":
                cols = ["Data","Volontario","RadioID","Note"]
            elif form_key == "mezzi":
                cols = ["Targa","Modello","Tipo","ODV","Stato","Note"]
            elif form_key == "attrezzature":
                cols = ["Nome","Tipo","Quantita","ODV","Stato","Note"]
            elif form_key == "brogliaccio":
                cols = ["Data","Evento","Descrizione","Operatore","Note"]
            elif form_key == "eventi":
                cols = ["Data","Titolo","Luogo","Descrizione","Note"]
            elif form_key == "emergenze":
                cols = ["Data","Tipo","Luogo","Descrizione","Note"]
            else:
                cols = ["Campo1","Campo2","Campo3","Note"]

        df_template = pd.DataFrame(columns=cols)
        try:
            tpl_data = to_excel(df_template)
            if tpl_data and len(tpl_data) > 100:
                st.download_button(
                    f"📋 Template {form_label} ODV",
                    data=tpl_data,
                    file_name=f"TEMPLATE_{form_key}_ODV_Office2016.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    key=f"tpl_inline_{form_key}",
                    help="File .xlsx puro compatibile Office 2016 - solo intestazioni"
                )
            else:
                st.warning("Template Excel non disponibile - openpyxl mancante su Cloud")
                st.info("Su GitHub verifica requirements.txt contenga openpyxl, poi Manage app -> Reboot")
        except Exception as e:
            st.error(f"Template errore: {str(e)[:100]}")
            st.info("Fix: requirements.txt deve contenere openpyxl")
        st.caption("Template vuoto per ODV")

    # Import
    with c4:
        up_mode = st.radio("Modalità import", ["Aggiungi","Sostituisci"], key=f"mode_inline_{form_key}", horizontal=True)
        up_file = st.file_uploader(f"Carica Excel per {form_label}", type=["xlsx","xls"], key=f"up_inline_{form_key}")

        if up_file:
            try:
                df_imp = None
                last_err = ""
                # Prova tutti gli engine per compatibilità Office 2016
                for eng in [None, "openpyxl", "xlrd"]:
                    try:
                        up_file.seek(0)
                        if eng is None:
                            df_imp = pd.read_excel(up_file)
                        else:
                            df_imp = pd.read_excel(up_file, engine=eng)
                        if df_imp is not None and len(df_imp.columns) > 0:
                            break
                    except Exception as e:
                        last_err = str(e)
                        continue

                # FIX: accetta anche file con solo header + dati, e mostra anche se vuoto
                if df_imp is not None:
                    # Pulisci
                    try:
                        df_imp = df_imp.dropna(how='all')
                        # Pulisci colonne Unnamed
                        if not df_imp.columns.empty:
                            df_imp = df_imp.loc[:, ~df_imp.columns.astype(str).str.contains('^Unnamed', na=False)]
                    except:
                        pass

                    if df_imp.empty:
                        # File ha solo intestazioni o vuoto - mostra colonne
                        if len(df_imp.columns) > 0:
                            st.warning(f"File letto: {len(df_imp.columns)} colonne trovate ma 0 righe dati")
                            st.write(f"Colonne: {list(df_imp.columns)}")
                            st.info("💡 Aggiungi righe dati sotto intestazione in Excel e ricarica")
                            st.dataframe(pd.DataFrame(columns=df_imp.columns).head(), use_container_width=True)
                        else:
                            st.warning("Excel vuoto - solo intestazioni? Aggiungi righe e ricarica")
                    else:
                        st.success(f"✅ {len(df_imp)} righe lette da Excel - {len(df_imp.columns)} colonne")
                        st.write(f"Colonne: {list(df_imp.columns)}")
                        st.dataframe(df_imp.head(20), use_container_width=True)

                        if st.button(f"✅ Importa {len(df_imp)} righe in {form_label}", type="primary", use_container_width=True, key=f"btn_imp_inline_{form_key}"):
                            imported = df_imp.to_dict(orient="records")
                        # Pulisci NaN
                        cleaned = []
                        for r in imported:
                            nr = {}
                            for k,v in r.items():
                                if pd.isna(v):
                                    continue
                                if isinstance(v, (pd.Timestamp, datetime, date)):
                                    nr[k] = v.strftime("%d/%m/%Y")
                                else:
                                    nr[k] = str(v).strip() if isinstance(v, str) else v
                            # Salta righe vuote
                            if any(nr.values()):
                                cleaned.append(nr)

                        if up_mode.startswith("Sostituisci"):
                            st.session_state[form_key] = cleaned
                        else:
                            st.session_state[form_key] = st.session_state.get(form_key, []) + cleaned

                        st.success(f"Importati {len(cleaned)} in {form_label}!")
                        st.balloons()
                        st.rerun()
                elif df_imp is not None:
                    st.warning("Excel vuoto - solo intestazioni? Aggiungi righe e ricarica")
                else:
                    st.error(f"Errore: {last_err}")
                    if "openpyxl" in last_err.lower():
                        st.error("Office 2016 FIX: Salva file come .xlsx (non .xls) in Office 2016 -> File -> Salva con nome -> Cartella di lavoro Excel (*.xlsx)")
            except Exception as e:
                st.error(f"Errore import: {e}")



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
        
        st.write("")
        st.write("")
        # ETICHETTA CON LOGO - Developed by Ezio F. 2026 Vers. 1.0 - SOLO PRIMA PAGINA - Richiesta Ezio
        try:
            # Prova a mostrare logo_dev_ezio.png
            col_logo, col_text = st.columns([1, 3])
            with col_logo:
                if os.path.exists("logo_dev_ezio.png"):
                    st.image("logo_dev_ezio.png", width=80)
                elif os.path.exists("/mnt/data/logo_dev_ezio.png"):
                    st.image("/mnt/data/logo_dev_ezio.png", width=80)
                else:
                    st.markdown('<div style="font-size:40px;text-align:center;">👨‍💻</div>', unsafe_allow_html=True)
            with col_text:
                st.markdown("""
                <div style="background:linear-gradient(135deg,#1A5D1A 0%,#2e7d32 100%);padding:10px 14px;border-radius:10px;
                border-left:4px solid #FFD700;margin-top:8px;">
                <p style="margin:0;color:white;font-family:Times New Roman;font-weight:bold;font-size:14px;">
                Developed by Ezio F. 2026 Vers. 1.0
                </p>
                <p style="margin:2px 0 0 0;color:#FFD700;font-family:Times New Roman;font-size:11px;">
                ANA Varese Protezione Civile - Gestionale 950+ Modifiche
                </p>
                </div>
                """, unsafe_allow_html=True)
        except:
            st.markdown("""
            <div style="text-align:center;background:#1A5D1A;color:white;padding:10px;border-radius:8px;margin-top:20px;">
            <b>Developed by Ezio F. 2026 Vers. 1.0</b><br>
            <small>ANA Varese Protezione Civile</small>
            </div>
            """, unsafe_allow_html=True)
        
        # Footer HTML con logo base64 fallback per Cloud
        try:
            import base64
            logo_path = "logo_dev_ezio.png" if os.path.exists("logo_dev_ezio.png") else "/mnt/data/logo_dev_ezio.png" if os.path.exists("/mnt/data/logo_dev_ezio.png") else None
            if logo_path:
                with open(logo_path, "rb") as f:
                    b64_logo = base64.b64encode(f.read()).decode()
                st.markdown(f"""
                <div style="text-align:center;margin-top:12px;padding:10px;background:white;border-radius:10px;border:2px solid #1A5D1A;">
                <img src="data:image/png;base64,{b64_logo}" style="width:60px;height:60px;border-radius:50%;border:2px solid #1A5D1A;object-fit:cover;"><br>
                <span style="font-family:Times New Roman;font-weight:bold;font-size:13px;color:#1A5D1A;">Developed by Ezio F. 2026 Vers. 1.0</span>
                </div>
                """, unsafe_allow_html=True)
        except:
            pass

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

    # Menu base - Gestione Utenti solo per amministratore
    ruolo_corrente = st.session_state.get("ruolo_utente", "amministratore")
    if ruolo_corrente == "amministratore":
        menu_base = [
            "Dashboard",
            "Volontari (con foto)",
            "DB Radio",
            "Consegna Radio",
            "Alias Radio",
            "Brogliaccio",
            "Eventi",
            "Emergenze",
            "Tabella Emergenze",
            "Check-in",
            "Interventi Emergenza",
            "Tabella Interventi Emergenza",
            "Mezzi",
            "Attrezzature",
            "Mappe Postazioni",
            "Libreria Icone",
            "Chat",
            "Geolocalizzazione Hytera + Anytone",
            "Gestione Utenti",
            "Backup"
        ]
    else:
        menu_base = [
            "Dashboard",
            "Volontari (con foto)",
            "DB Radio",
            "Consegna Radio",
            "Alias Radio",
            "Brogliaccio",
            "Eventi",
            "Emergenze",
            "Tabella Emergenze",
            "Check-in",
            "Interventi Emergenza",
            "Tabella Interventi Emergenza",
            "Mezzi",
            "Attrezzature",
            "Mappe Postazioni",
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
    
    # Utente loggato + ruolo
    username = st.session_state.get("username", "admin")
    nome_utente = st.session_state.get("nome_utente", "Amministratore")
    ruolo_utente = st.session_state.get("ruolo_utente", "amministratore")
    
    # Colore ruolo
    colore_ruolo = {"amministratore": "#d32f2f", "operatore": "#1A5D1A", "lettore": "#1976d2"}.get(ruolo_utente, "#1A5D1A")
    
    st.markdown(f"""
    <div style="background:{colore_ruolo};color:white;padding:8px;border-radius:8px;text-align:center;">
    <b>{nome_utente}</b><br>
    <small>{username} - {ruolo_utente.upper()}</small>
    </div>
    """, unsafe_allow_html=True)
    
    # Aggiorna presenza ogni volta che naviga
    try:
        aggiorna_presenza(username, nome_utente, ruolo_utente)
    except:
        pass

    # MODIFICA 6 - LOGOUT RIPRISTINATO con rimozione presenza
    if st.button("Logout", type="primary", use_container_width=True, key="logout_btn"):
        try:
            rimuovi_presenza(st.session_state.get("username", ""))
        except:
            pass
        st.session_state.page = "entra"
        st.session_state.logged = False
        st.session_state.menu = "Dashboard"
        st.session_state.username = ""
        st.session_state.nome_utente = ""
        st.session_state.ruolo_utente = ""
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
    # IMPORT/EXPORT INLINE - Ezio - TUTTI I FORM - Excel + PDF + Template ODV
    excel_import_inline("volontari", "Volontari (con foto)")


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


    # IMPORT/EXPORT INLINE - Ezio - TUTTI I FORM - Excel + PDF + Template ODV
    excel_import_inline("radio_db", "DB Radio")


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


    # IMPORT/EXPORT INLINE - Ezio - TUTTI I FORM - Excel + PDF + Template ODV
    excel_import_inline("consegna_radio", "Consegna Radio")


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


    # IMPORT/EXPORT INLINE - Ezio - TUTTI I FORM - Excel + PDF + Template ODV
    excel_import_inline("alias_radio", "Alias Radio")


elif cur == "Brogliaccio":
    hdr()
    hdr_form("BROGLIACCIO - Registro Operativo - Alias + Volontari agganciati")

    st.markdown("""
    <div style="background:#e8f5e9;padding:8px;border-radius:8px;border-left:4px solid #1A5D1A;margin-bottom:10px;">
    <b>NUOVO:</b> Chiamate e Ricevente da Alias Radio | Operatore da Volontari Nome Cognome
    </div>
    """, unsafe_allow_html=True)

    # Prepara liste combo da Alias Radio e Volontari
    # Alias Radio -> lista Alias
    alias_list = []
    try:
        alias_data = st.session_state.get("alias_radio", [])
        for a in alias_data:
            al = a.get("Alias", "").strip() if isinstance(a, dict) else ""
            if al and al not in alias_list:
                alias_list.append(al)
    except:
        pass
    if not alias_list:
        alias_list = ["Centrale Operativa", "Squadra A", "Squadra B", "Squadra C", "Coordinamento"]

    # Volontari -> lista Nome Cognome
    volontari_list = []
    try:
        vol_data = st.session_state.get("volontari", [])
        for v in vol_data:
            if isinstance(v, dict):
                nome = v.get("Nome", "").strip()
                cognome = v.get("Cognome", "").strip()
                full = f"{nome} {cognome}".strip()
                if full and full not in volontari_list:
                    volontari_list.append(full)
    except:
        pass
    if not volontari_list:
        volontari_list = ["Ezio Fiscato", "Operatore 1", "Operatore 2"]

    c1, c2 = st.columns(2)
    with c1:
        data_b = st.date_input("Data", value=date.today(), format="DD/MM/YYYY", key="brog_data")
        ora_b = st.time_input("Ora", value=datetime.now().time(), key="brog_ora")
        # OPERATORE COMBO DA VOLONTARI NOME COGNOME - Richiesta Ezio
        operatore = st.selectbox("Operatore (da Volontari Nome Cognome)", volontari_list, key="brog_op_combo", help="Lista agganciata a form Volontari - Nome Cognome")
        # Permetti anche inserimento manuale se non in lista
        operatore_custom = st.text_input("Oppure inserisci Operatore manuale", key="brog_op_custom", placeholder="Se non in lista volontari")
        if operatore_custom.strip():
            operatore = operatore_custom.strip()

        # CHIAMATE COMBO DA ALIAS RADIO - Richiesta Ezio
        chiamate = st.selectbox("Chiamate (da Alias Radio - Alias)", alias_list, key="brog_chiamate", help="Lista agganciata a form Alias Radio - campo Alias")
        chiamate_custom = st.text_input("Oppure Chiamate manuale", key="brog_chiamate_custom", placeholder="Alias non in lista")
        if chiamate_custom.strip():
            chiamate = chiamate_custom.strip()

    with c2:
        evento_b = st.text_input("Evento Riferimento", key="brog_evento")
        emerg_b = st.text_input("Emergenza Riferimento", key="brog_emerg")
        # RICEVENTE COMBO DA ALIAS RADIO - Richiesta Ezio
        ricevente = st.selectbox("Ricevente (da Alias Radio - Alias)", alias_list, key="brog_ricevente", help="Lista agganciata a form Alias Radio - campo Alias")
        ricevente_custom = st.text_input("Oppure Ricevente manuale", key="brog_ricevente_custom", placeholder="Alias non in lista")
        if ricevente_custom.strip():
            ricevente = ricevente_custom.strip()
        blindato = st.checkbox("Blinda Evento/Emergenza", key="brog_blind")

    testo_b = st.text_area("Testo Brogliaccio *", height=150, key="brog_testo")

    if st.button("Salva Brogliaccio", type="primary", use_container_width=True):
        if testo_b:
            st.session_state.brogliaccio.append({
                "Data": str(data_b),
                "Ora": str(ora_b),
                "Operatore": operatore,
                "Chiamate": chiamate,
                "Ricevente": ricevente,
                "Evento": evento_b,
                "Emergenza": emerg_b,
                "Testo": testo_b,
                "Blindato": blindato
            })
            st.success(f"Brogliaccio salvato - Op: {operatore} - Chiamate: {chiamate} -> Ricevente: {ricevente}")
            st.rerun()
        else:
            st.error("Compila Testo Brogliaccio *")

    if st.session_state.brogliaccio:
        df_br = pd.DataFrame(st.session_state.brogliaccio)
        st.markdown(f"#### Elenco Brogliaccio ({len(st.session_state.brogliaccio)})")
        st.dataframe(df_br, use_container_width=True)
        # Tabella con colonne importanti
        cols_show = ["Data","Ora","Operatore","Chiamate","Ricevente","Testo","Evento"]
        cols_show = [c for c in cols_show if c in df_br.columns]
        if cols_show:
            st.dataframe(df_br[cols_show], use_container_width=True)

# EVENTI


    # IMPORT/EXPORT INLINE - Ezio - TUTTI I FORM - Excel + PDF + Template ODV
    excel_import_inline("brogliaccio", "Brogliaccio")


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


    # IMPORT/EXPORT INLINE - Ezio - TUTTI I FORM - Excel + PDF + Template ODV
    excel_import_inline("eventi", "Eventi")


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


    # IMPORT/EXPORT INLINE - Ezio - TUTTI I FORM - Excel + PDF + Template ODV
    excel_import_inline("emergenze", "Emergenze")


# TABELLA EMERGENZE - FORM TABELLA - Richiesta Ezio - Formato tabella per vedere emergenze
elif cur == "Tabella Emergenze":
    hdr()
    hdr_form("TABELLA EMERGENZE - Vista Tabella - Filtri + Stato Colorato")
    
    st.markdown("""
    <div style="background:#fff3e0;padding:10px;border-radius:8px;border-left:4px solid #ff9800;margin-bottom:12px;">
    <b>📋 Tabella Emergenze - Formato Tabella</b><br>
    Vedi tutte le emergenze in tabella con filtri per Tipo, Comune, Stato, Priorità - Stato colorato
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.emergenze:
        st.info("Nessuna emergenza salvata - Vai in Emergenze per crearne una")
        st.markdown("""
        <div style="background:#e8f5e9;padding:12px;border-radius:8px;text-align:center;">
        <b>Come creare emergenza:</b><br>
        1. Vai in <b>Emergenze</b><br>
        2. Compila Nome, Tipo, Comune, Via, Priorità, Stato<br>
        3. Salva - Apparirà qui in tabella
        </div>
        """, unsafe_allow_html=True)
    else:
        df_em = pd.DataFrame(st.session_state.emergenze)
        
        # Filtri
        tipi_list = sorted(list(set([str(x) for x in df_em.get("Tipo", []).tolist() if x]))) if "Tipo" in df_em.columns else []
        comuni_list = sorted(list(set([str(x) for x in df_em.get("Comune", []).tolist() if x]))) if "Comune" in df_em.columns else []
        stati_list = sorted(list(set([str(x) for x in df_em.get("Stato", []).tolist() if x]))) if "Stato" in df_em.columns else []
        prior_list = sorted(list(set([str(x) for x in df_em.get("Priorita", []).tolist() if x]))) if "Priorita" in df_em.columns else []
        
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            filtro_tipo = st.selectbox("Filtra Tipo", ["Tutti"] + tipi_list, key="tab_em_tipo")
        with c2:
            filtro_comune = st.selectbox("Filtra Comune", ["Tutti"] + comuni_list, key="tab_em_comune")
        with c3:
            filtro_stato = st.selectbox("Filtra Stato", ["Tutti"] + stati_list, key="tab_em_stato")
        with c4:
            filtro_prior = st.selectbox("Filtra Priorità", ["Tutte"] + prior_list, key="tab_em_prior")
        
        df_filtrato = df_em.copy()
        if filtro_tipo != "Tutti" and "Tipo" in df_filtrato.columns:
            df_filtrato = df_filtrato[df_filtrato["Tipo"] == filtro_tipo]
        if filtro_comune != "Tutti" and "Comune" in df_filtrato.columns:
            df_filtrato = df_filtrato[df_filtrato["Comune"] == filtro_comune]
        if filtro_stato != "Tutti" and "Stato" in df_filtrato.columns:
            df_filtrato = df_filtrato[df_filtrato["Stato"] == filtro_stato]
        if filtro_prior != "Tutte" and "Priorita" in df_filtrato.columns:
            df_filtrato = df_filtrato[df_filtrato["Priorita"] == filtro_prior]
        
        st.write(f"**Risultati: {len(df_filtrato)} su {len(df_em)} emergenze**")
        
        # Tabella formattata con stato colorato
        if not df_filtrato.empty:
            for idx, row in df_filtrato.iterrows():
                bg_c = row.get("StatoColoreBg", "#e8f5e9")
                txt_c = row.get("StatoColoreTxt", "black")
                stato = row.get("Stato","")
                prior = row.get("Priorita","")
                col_prior = {"Bassa":"#4caf50","Media":"#ff9800","Alta":"#ff5722","Critica":"#d32f2f"}.get(prior, "#9e9e9e")
                
                c1, c2, c3 = st.columns([3,1,1])
                with c1:
                    st.markdown(f"""
                    <div style="background:white;padding:8px;border-radius:8px;border-left:4px solid {bg_c};margin-bottom:4px;">
                    <b>{row.get('Nome','')}</b> - Tipo: {row.get('Tipo','')} - Comune: {row.get('Comune','')} {row.get('Via','')}<br>
                    <small>Data: {row.get('Data','')} - Coord: {row.get('Coordinate','')} - Note: {row.get('Note','')[:80]}</small>
                    </div>
                    """, unsafe_allow_html=True)
                with c2:
                    st.markdown(f"""
                    <div style="background:{bg_c};color:{txt_c};padding:8px;border-radius:8px;text-align:center;font-weight:bold;border:2px solid black;">
                    {stato}
                    </div>
                    """, unsafe_allow_html=True)
                with c3:
                    st.markdown(f"""
                    <div style="background:{col_prior};color:white;padding:4px;border-radius:4px;text-align:center;font-weight:bold;">
                    {prior}
                    </div>
                    """, unsafe_allow_html=True)
                st.divider()
            
            st.markdown("#### 📊 Tabella Completa Emergenze")
            cols_show = ["Nome","Tipo","Data","Comune","Via","Priorita","Stato","Coordinate","Note"]
            cols_show = [c for c in cols_show if c in df_filtrato.columns]
            st.dataframe(df_filtrato[cols_show], use_container_width=True)
        else:
            st.warning("Nessuna emergenza con questi filtri")
        
        # Export
        st.divider()
        c_exp1, c_exp2 = st.columns(2)
        with c_exp1:
            st.download_button("⬇️ Excel Emergenze Filtrate", data=to_excel(df_filtrato), file_name="tabella_emergenze_filtrata.xlsx", use_container_width=True, key="exp_tab_em")
        with c_exp2:
            if REPORTLAB_OK:
                st.download_button("📄 PDF Emergenze Filtrate", data=to_pdf(df_filtrato, "TABELLA EMERGENZE"), file_name="tabella_emergenze.pdf", use_container_width=True, key="pdf_tab_em")

    # IMPORT/EXPORT INLINE
    excel_import_inline("emergenze", "Tabella Emergenze")


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
    # IMPORT/EXPORT INLINE - Ezio - TUTTI I FORM - Excel + PDF + Template ODV
    excel_import_inline("checkin", "Check-in")


elif cur == "Interventi Emergenza":
    hdr()
    hdr_form("INTERVENTI EMERGENZA - Stato Colore + Icona da Libreria")

    st.markdown(
        """
        <div style="background:#e8f5e9;padding:10px;border-radius:8px;border-left:4px solid #1A5D1A;margin-bottom:10px;">
        <b>NUOVO:</b> Ora puoi caricare un'icona dalla Libreria Icone per ogni intervento!
        </div>
        """,
        unsafe_allow_html=True
    )

    # Prepara lista icone da Libreria Icone - Richiesta Ezio
    icone_lib = st.session_state.get("icone", [])
    if not icone_lib:
        icone_lib = [
            {"Nome": "Emergenza", "Emoji": "🚨", "Tipo": "Emergenza", "Colore": "red"},
            {"Nome": "Soccorso", "Emoji": "⛑️", "Tipo": "Emergenza", "Colore": "red"},
            {"Nome": "Mezzo", "Emoji": "🚐", "Tipo": "Mezzo", "Colore": "green"},
            {"Nome": "Logistica", "Emoji": "📦", "Tipo": "Logistica", "Colore": "blue"},
        ]
    
    # Crea opzioni per selectbox: Emoji + Nome
    icone_options = ["-- Nessuna Icona --"]
    icone_map = {"-- Nessuna Icona --": None}
    for ico in icone_lib:
        label = f"{ico.get('Emoji','📍')} {ico.get('Nome','')} - {ico.get('Tipo','')} ({ico.get('Colore','')})"
        icone_options.append(label)
        icone_map[label] = ico

    c1, c2, c3 = st.columns(3)
    with c1:
        tipo_int = st.selectbox("Tipo Intervento", ["Soccorso", "Logistica", "Monitoraggio", "Bonifica", "Altro"], key="int_tipo")
        squadra_int = st.selectbox("Squadra", ["Squadra A", "Squadra B", "Squadra C", "Logistica"], key="int_squadra")
        data_int = st.date_input("Data Intervento", value=date.today(), format="DD/MM/YYYY", key="int_data")
        # ICONA DA LIBRERIA - Richiesta Ezio
        icona_sel_label = st.selectbox("Icona da Libreria Icone", icone_options, index=0, key="int_icona", help="Scegli icona creata in Libreria Icone")
        sel_ico_obj = icone_map.get(icona_sel_label)

    with c2:
        comune_int = combo_comune("Comune Intervento", "int_comune", "Varese")
        via_int = combo_vie("Via Intervento", comune_int, "int_via", "")
        ora_int = st.time_input("Ora Intervento", value=datetime.now().time(), key="int_ora")
        # Anteprima icona selezionata
        if sel_ico_obj:
            st.markdown(f"""
            <div style="background:white;padding:10px;border-radius:8px;border:2px solid #1A5D1A;text-align:center;margin-top:8px;">
            <div style="font-size:32px;">{sel_ico_obj.get('Emoji','📍')}</div>
            <b>{sel_ico_obj.get('Nome','')}</b><br>
            <small>{sel_ico_obj.get('Tipo','')} - {sel_ico_obj.get('Colore','')}</small>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Nessuna icona selezionata - Vai in Libreria Icone per crearne")

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
            Fondo campo colorato - Modifica 4
            </div>
            """,
            unsafe_allow_html=True
        )

    desc_int = st.text_area("Descrizione Intervento *", key="int_desc")
    mezzi_int = st.text_input("Mezzi Utilizzati", key="int_mezzi")
    volontari_int = st.text_input("Volontari Coinvolti", key="int_vol")

    if st.button("Salva Intervento Emergenza con Icona", type="primary", use_container_width=True):
        if desc_int:
            new_intervento = {
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
                "Volontari": volontari_int,
                "IconaLabel": icona_sel_label,
                "IconaNome": sel_ico_obj.get("Nome","") if sel_ico_obj else "",
                "IconaEmoji": sel_ico_obj.get("Emoji","") if sel_ico_obj else "",
                "IconaColore": sel_ico_obj.get("Colore","") if sel_ico_obj else "",
                "IconaTipo": sel_ico_obj.get("Tipo","") if sel_ico_obj else ""
            }
            st.session_state.interventi.append(new_intervento)
            icona_msg = f" con icona {sel_ico_obj.get('Emoji','')} {sel_ico_obj.get('Nome','')}" if sel_ico_obj else ""
            st.success(f"Intervento salvato con stato {label} colorato {bg_color}{icona_msg}")
            st.balloons()
            st.rerun()
        else:
            st.error("Compila Descrizione Intervento *")

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
    # IMPORT/EXPORT INLINE - Ezio - TUTTI I FORM - Excel + PDF + Template ODV
    excel_import_inline("interventi", "Interventi Emergenza")


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
    # IMPORT/EXPORT INLINE - Ezio - TUTTI I FORM - Excel + PDF + Template ODV
    excel_import_inline("tabella_interventi", "Tabella Interventi Emergenza")


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


    # IMPORT/EXPORT INLINE - Ezio - TUTTI I FORM - Excel + PDF + Template ODV
    excel_import_inline("mezzi", "Mezzi")


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


    # IMPORT/EXPORT INLINE - Ezio - TUTTI I FORM - Excel + PDF + Template ODV
    excel_import_inline("attrezzature", "Attrezzature")


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
    try:
        inject_fullscreen_all_maps()
    except:
        pass

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
    // TASTO FULLSCREEN 100% TUTTO LO SCHERMO - Ezio - SOTTO + - 100% vero fullscreen
    var FullscreenControl = L.Control.extend({
        onAdd: function(map) {
            var container = L.DomUtil.create('div', 'leaflet-bar leaflet-control');
            container.style.backgroundColor = 'white';
            container.style.width = '34px';
            container.style.height = '34px';
            container.style.lineHeight = '34px';
            container.style.textAlign = 'center';
            container.style.cursor = 'pointer';
            container.style.fontSize = '22px';
            container.style.fontWeight = 'bold';
            container.style.border = '2px solid rgba(0,0,0,0.2)';
            container.style.borderRadius = '4px';
            container.innerHTML = '⛶';
            container.title = 'Schermo intero 100% - Tutto lo schermo';
            container.onclick = function(){
                var mapContainer = document.getElementById('map');
                var parentContainer = document.getElementById('map-container');
                var rootContainer = document.documentElement;
                // Prova fullscreen su tutto lo schermo 100%
                try {
                    if (!document.fullscreenElement) {
                        // Prova prima il container mappa grande a 100%
                        if (parentContainer.requestFullscreen) {
                            parentContainer.requestFullscreen();
                        } else if (rootContainer.requestFullscreen) {
                            rootContainer.requestFullscreen();
                        } else if (mapContainer.requestFullscreen) {
                            mapContainer.requestFullscreen();
                        } else {
                            // Fallback: prova parent window (Streamlit iframe parent)
                            try {
                                var parentDoc = window.parent.document;
                                var iframe = parentDoc.querySelector('iframe[title*="st.components"]');
                                if (iframe && iframe.requestFullscreen) iframe.requestFullscreen();
                                else if (parentDoc.documentElement.requestFullscreen) parentDoc.documentElement.requestFullscreen();
                            } catch(e) {
                                console.log('Fullscreen parent failed', e);
                            }
                        }
                        // Imposta mappa a 100vh in fullscreen
                        setTimeout(function(){
                            parentContainer.style.width = '100vw';
                            parentContainer.style.height = '100vh';
                            mapContainer.style.height = '100vh';
                            map.invalidateSize();
                        }, 100);
                    } else {
                        if (document.exitFullscreen) document.exitFullscreen();
                        else if (document.webkitExitFullscreen) document.webkitExitFullscreen();
                        try {
                            var parentDoc = window.parent.document;
                            if (parentDoc.exitFullscreen) parentDoc.exitFullscreen();
                            else if (parentDoc.webkitExitFullscreen) parentDoc.webkitExitFullscreen();
                        } catch(e) {}
                        // Ripristina dimensioni normali
                        setTimeout(function(){
                            parentContainer.style.width = '100%';
                            parentContainer.style.height = '';
                            mapContainer.style.height = '650px';
                            map.invalidateSize();
                        }, 100);
                    }
                } catch(err) {
                    console.log('Fullscreen error', err);
                }
                setTimeout(function(){ map.invalidateSize(); }, 600);
            };
            return container;
        }
    });
    new FullscreenControl({position: 'topleft'}).addTo(map);
    // Listener per gestire fullscreen 100% - mappa diventa 100vh
    document.addEventListener('fullscreenchange', function(){
        var mapContainer = document.getElementById('map');
        var parentContainer = document.getElementById('map-container');
        if (document.fullscreenElement) {
            // In fullscreen: mappa 100% schermo
            parentContainer.style.width = '100vw';
            parentContainer.style.height = '100vh';
            parentContainer.style.background = 'white';
            mapContainer.style.height = '100vh';
            mapContainer.style.borderRadius = '0';
        } else {
            // Fuori fullscreen: ripristina
            parentContainer.style.width = '100%';
            parentContainer.style.height = '';
            parentContainer.style.background = '';
            mapContainer.style.height = '650px';
            mapContainer.style.borderRadius = '12px';
        }
        setTimeout(function(){ map.invalidateSize(); }, 600);
    });
    // CSS per fullscreen 100% vero
    var style = document.createElement('style');
    style.innerHTML = `
        #map-container:fullscreen {
            width: 100vw !important;
            height: 100vh !important;
            background: white !important;
            padding: 0 !important;
            margin: 0 !important;
        }
        #map-container:fullscreen #map {
            height: 100vh !important;
            width: 100vw !important;
            border-radius: 0 !important;
            border: none !important;
        }
        #map:fullscreen {
            width: 100vw !important;
            height: 100vh !important;
        }
        :-webkit-full-screen {
            width: 100vw !important;
            height: 100vh !important;
        }
    `;
    document.head.appendChild(style);
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
            var mapB = L.map('preview_bottom', {zoomControl: false}).setView([45.8167, 8.8333], 12);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(mapB);
            L.control.zoom({position: 'topleft'}).addTo(mapB);
            var FsBottom = L.Control.extend({onAdd: function(m){var cEl=L.DomUtil.create('div','leaflet-bar leaflet-control');cEl.style.background='white';cEl.style.width='34px';cEl.style.height='34px';cEl.style.lineHeight='34px';cEl.style.textAlign='center';cEl.style.cursor='pointer';cEl.style.fontSize='20px';cEl.innerHTML='⛶';cEl.title='Fullscreen 100%';cEl.onclick=function(){var contEl=document.getElementById('preview_bottom').parentElement;if(!document.fullscreenElement){if(contEl.requestFullscreen)contEl.requestFullscreen();}else{if(document.exitFullscreen)document.exitFullscreen();} setTimeout(function(){m.invalidateSize();},500);};return cEl;}}); new FsBottom({position:'topleft'}).addTo(mapB);
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
    # IMPORT/EXPORT INLINE - Ezio - TUTTI I FORM - Excel + PDF + Template ODV
    excel_import_inline("mappe", "Mappe Postazioni")


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


    # IMPORT/EXPORT INLINE - Ezio - TUTTI I FORM - Excel + PDF + Template ODV
    excel_import_inline("turni", "Turni")


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
    # IMPORT/EXPORT INLINE - Ezio - TUTTI I FORM - Excel + PDF + Template ODV
    excel_import_inline("icone", "Libreria Icone")


elif cur == "Chat":
    hdr()
    hdr_form("CHAT - Comunicazioni Squadra - Chi è collegato")

    # Mostra chi è collegato ora - Richiesta Ezio
    st.markdown("#### 🟢 Chi è collegato ora")
    try:
        presenza = load_presenza()
        if presenza:
            # Aggiorna mia presenza
            aggiorna_presenza(st.session_state.get("username",""), st.session_state.get("nome_utente",""), st.session_state.get("ruolo_utente",""))
            presenza = load_presenza()
            cols = st.columns(min(len(presenza), 4))
            for idx, p in enumerate(presenza[-12:]):  # ultimi 12
                with cols[idx % len(cols)]:
                    ruolo = p.get("ruolo","operatore")
                    colore = {"amministratore":"#d32f2f","operatore":"#1A5D1A","lettore":"#1976d2"}.get(ruolo, "#1A5D1A")
                    st.markdown(f"""
                    <div style="background:{colore};color:white;padding:8px;border-radius:8px;text-align:center;margin-bottom:6px;">
                    <b>🟢 {p.get("nome","")}</b><br>
                    <small>{p.get("username","")} - {ruolo}</small><br>
                    <small>{p.get("ora","")}</small>
                    </div>
                    """, unsafe_allow_html=True)
            st.caption(f"{len(presenza)} utenti collegati negli ultimi 30 minuti - Aggiornamento automatico")
        else:
            st.info("Nessun utente collegato oltre te - File presenza.json vuoto")
    except Exception as e:
        st.warning(f"Presenza non disponibile: {e}")

    st.divider()
    
    # Info multi-utente
    st.markdown("""
    <div style="background:#e3f2fd;padding:10px;border-radius:8px;border-left:4px solid #1976d2;margin-bottom:10px;">
    <b>ℹ️ Multi-utente contemporaneo:</b> Sì, più utenti possono aprire il gestionale insieme!<br>
    - Ogni utente ha il suo login (admin, operatore1, lettore1)<br>
    - Su Streamlit Cloud session_state è separato per utente, ma presenza.json è condiviso<br>
    - Per dati condivisi in tempo reale serve database esterno (Firebase/Supabase) - per ora chat e presenza usano file condiviso<br>
    - Chat salvata in sessione locale (per condivisione reale serve DB)
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### 💬 Chat operativa volontari")
    
    # Mostra utente corrente
    curr_user = st.session_state.get("nome_utente", "Admin")
    curr_username = st.session_state.get("username", "admin")
    st.caption(f"Stai chattando come: {curr_user} ({curr_username})")

    msg = st.text_input("Messaggio", key="chat_msg", placeholder="Scrivi messaggio e premi Invio o Invia")

    c1, c2, c3 = st.columns([1, 1, 3])
    with c1:
        if st.button("📤 Invia Messaggio", type="primary", use_container_width=True):
            if msg:
                st.session_state.chat.append({
                    "Data": datetime.now().strftime("%d/%m/%Y"),
                    "Ora": datetime.now().strftime("%H:%M:%S"),
                    "Utente": curr_user,
                    "Username": curr_username,
                    "Messaggio": msg,
                    "Ruolo": st.session_state.get("ruolo_utente","operatore")
                })
                # Salva anche su file per condivisione parziale
                try:
                    with open("chat.json","a", encoding="utf-8") as f:
                        f.write(json.dumps({"Data": datetime.now().strftime("%d/%m/%Y"), "Ora": datetime.now().strftime("%H:%M:%S"), "Utente": curr_user, "Messaggio": msg}) + "\n")
                except:
                    pass
                st.rerun()
    with c2:
        if st.button("🔄 Aggiorna", use_container_width=True):
            try:
                aggiorna_presenza(curr_username, curr_user, st.session_state.get("ruolo_utente",""))
            except:
                pass
            st.rerun()

    st.divider()

    if st.session_state.chat:
        st.markdown(f"#### Ultimi {len(st.session_state.chat[-30:])} messaggi")
        for chat_msg in reversed(st.session_state.chat[-30:]):
            ruolo = chat_msg.get('Ruolo','operatore')
            colore = {"amministratore":"#d32f2f","operatore":"#1A5D1A","lettore":"#1976d2"}.get(ruolo, "#1A5D1A")
            st.markdown(
                f"""
                <div style="background:white;padding:10px;border-radius:8px;
                margin-bottom:6px;border-left:4px solid {colore};">
                <strong>{chat_msg.get('Data','')} {chat_msg.get('Ora','')} - {chat_msg.get('Utente','')} ({chat_msg.get('Ruolo','')})</strong><br>
                {chat_msg.get('Messaggio','')}
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.info("Nessun messaggio - Inizia conversazione - I messaggi sono visibili solo nella tua sessione (per chat condivisa serve DB)")

    # Mostra anche chat da file se esiste
    try:
        if os.path.exists("chat.json"):
            st.divider()
            st.markdown("#### 📁 Chat condivisa da file (ultimi 10)")
            with open("chat.json","r", encoding="utf-8") as f:
                lines = f.readlines()[-10:]
                for line in reversed(lines):
                    try:
                        cj = json.loads(line)
                        st.caption(f"{cj.get('Data','')} {cj.get('Ora','')} - {cj.get('Utente','')}: {cj.get('Messaggio','')}")
                    except:
                        pass
    except:
        pass

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

# GESTIONE UTENTI - Amministratore e utenti view/insert - Ezio richiesta
elif cur == "Gestione Utenti":
    hdr()
    hdr_form("GESTIONE UTENTI - Solo Amministratore - Crea Utenti con Livelli Accesso")
    
    # Solo amministratore può accedere - RICHIESTA EZIO
    if st.session_state.get("ruolo_utente") != "amministratore":
        st.error("⛔ Accesso negato - Solo amministratore può gestire utenti")
        st.info(f"Il tuo ruolo: {st.session_state.get('ruolo_utente')} - Contatta amministratore (admin / ana2024)")
        st.markdown("""
        <div style="background:#fff3e0;padding:12px;border-radius:8px;text-align:center;">
        <b>Questo form è solo per Amministratore</b><br>
        Livelli accesso: Amministratore = tutto, Coordinatore = gestione squadre, Operatore = vede+inserisce, Lettore = solo vede
        </div>
        """, unsafe_allow_html=True)
        st.stop()
    
    st.markdown("""
    <div style="background:#ffebee;padding:12px;border-radius:8px;border-left:4px solid #d32f2f;margin-bottom:12px;">
    <b>🔐 Gestione Utenti - Solo Amministratore - Livelli Accesso</b><br>
    - <b>Amministratore:</b> 🔴 può tutto - creare utenti, cancellare dati, backup, gestione utenti, tutti i form<br>
    - <b>Coordinatore:</b> 🟠 può gestire squadre, volontari, mezzi, eventi, emergenze, brogliaccio, mappe, interventi<br>
    - <b>Operatore:</b> 🟢 può vedere e inserire (volontari, mezzi, brogliaccio, chat, check-in) ma non cancellare utenti né gestire ruoli<br>
    - <b>Volontario:</b> 🔵 può vedere e inserire solo proprio check-in, chat, volontari (solo lettura)<br>
    - <b>Lettore:</b> ⚪ può solo vedere tutto (no inserimento, no modifica)<br>
    - <b>Multi-utente:</b> Sì! Più utenti contemporaneamente - ogni login separato
    </div>
    """, unsafe_allow_html=True)
    
    utenti = load_utenti()
    
    tab1, tab2, tab3, tab4 = st.tabs(["👥 Elenco Utenti", "➕ Crea Utente con Livello", "✏️ Modifica Utente", "📊 Presenza Online"])
    
    with tab1:
        st.markdown(f"#### Utenti configurati ({len(utenti)}) - Solo Amministratore vede questo")
        if utenti:
            # Mostra senza password ma con permessi
            df_show = []
            for u in utenti:
                df_show.append({
                    "Username": u.get("username"),
                    "Nome": u.get("nome"),
                    "Ruolo": u.get("ruolo"),
                    "Attivo": "✅" if u.get("attivo",True) else "❌",
                    "Permessi": ", ".join(u.get("permessi", [])[:5]) if u.get("permessi") else "Tutti" if u.get("ruolo")=="amministratore" else "Base"
                })
            df_ut = pd.DataFrame(df_show)
            st.dataframe(df_ut, use_container_width=True)
            
            # Info livelli
            st.info("Livelli accesso: amministratore=tutto, coordinatore=gestione operativa, operatore=vede+inserisce, volontario=check-in+chat, lettore=solo vista")
    
    with tab2:
        st.markdown("#### ➕ Crea Nuovo Utente con Livello Accesso - Solo Amministratore")
        st.markdown("""
        <div style="background:#e8f5e9;padding:8px;border-radius:8px;margin-bottom:10px;">
        <b>Come Amministratore crei utenti:</b> Scegli username, password, nome, ruolo/livello accesso - L'utente potrà fare login con quel livello
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("crea_utente_form_avanzato"):
            c1, c2 = st.columns(2)
            with c1:
                new_username = st.text_input("Username * (senza spazi, minuscolo)", placeholder="es: mario.rossi", key="new_username_adv")
                new_nome = st.text_input("Nome Completo *", placeholder="es: Mario Rossi - ODV Varese - Squadra A", key="new_nome_user_adv")
                new_ruolo = st.selectbox("Livello Accesso / Ruolo *", 
                    ["operatore","coordinatore","volontario","lettore","amministratore"], 
                    index=0, 
                    key="new_ruolo_user_adv",
                    help="amministratore=tutto, coordinatore=gestione squadre, operatore=vede+inserisce, volontario=base, lettore=solo vista")
                
                # Descrizione ruolo
                desc_ruoli = {
                    "amministratore": "🔴 Può tutto: creare utenti, cancellare, backup, tutti i form",
                    "coordinatore": "🟠 Gestisce squadre, volontari, mezzi, eventi, emergenze, brogliaccio",
                    "operatore": "🟢 Vede e inserisce volontari, mezzi, brogliaccio, chat, check-in",
                    "volontario": "🔵 Solo check-in, chat, vista volontari e mezzi",
                    "lettore": "⚪ Solo visualizzazione, nessun inserimento"
                }
                st.caption(desc_ruoli.get(new_ruolo, ""))
            
            with c2:
                new_pwd = st.text_input("Password * (min 4 caratteri)", type="password", key="new_pwd_user_adv")
                new_pwd2 = st.text_input("Conferma Password *", type="password", key="new_pwd2_user_adv")
                attivo_new = st.checkbox("Utente Attivo", value=True, key="new_attivo_adv")
                st.caption("Se disattivo, non può fare login")
                
                # Permessi extra per livello
                st.markdown("**Permessi extra (opzionale):**")
                perm_brogliaccio = st.checkbox("Può gestire Brogliaccio", value=True if new_ruolo in ["amministratore","coordinatore","operatore"] else False, key="perm_brog")
                perm_mezzi = st.checkbox("Può gestire Mezzi/Attrezzature", value=True if new_ruolo in ["amministratore","coordinatore","operatore"] else False, key="perm_mezzi")
                perm_mappe = st.checkbox("Può gestire Mappe", value=True if new_ruolo in ["amministratore","coordinatore"] else False, key="perm_mappe")
                perm_radio = st.checkbox("Può gestire Radio", value=True if new_ruolo in ["amministratore","coordinatore","operatore"] else False, key="perm_radio")
            
            submitted = st.form_submit_button("✅ Crea Utente con Livello Accesso", type="primary", use_container_width=True)
            if submitted:
                if not new_username or not new_nome or not new_pwd:
                    st.error("Compila campi obbligatori * (Username, Nome, Password)")
                elif new_pwd != new_pwd2:
                    st.error("Password non coincidono - riscrivi")
                elif len(new_pwd) < 4:
                    st.error("Password minimo 4 caratteri")
                elif any(u.get("username") == new_username.strip().lower() for u in utenti):
                    st.error(f"Username {new_username} già esistente - scegli altro")
                elif " " in new_username.strip():
                    st.error("Username senza spazi - usa punto es: mario.rossi")
                else:
                    permessi_list = []
                    if perm_brogliaccio: permessi_list.append("brogliaccio")
                    if perm_mezzi: permessi_list.append("mezzi")
                    if perm_mappe: permessi_list.append("mappe")
                    if perm_radio: permessi_list.append("radio")
                    
                    nuovo_utente = {
                        "username": new_username.strip().lower(),
                        "password": hash_pwd(new_pwd.strip()),
                        "nome": new_nome.strip(),
                        "ruolo": new_ruolo,
                        "attivo": attivo_new,
                        "permessi": permessi_list,
                        "creato_da": st.session_state.get("username","admin"),
                        "data_creazione": datetime.now().strftime("%d/%m/%Y %H:%M")
                    }
                    utenti.append(nuovo_utente)
                    if save_utenti(utenti):
                        st.success(f"✅ Utente {new_username} creato con livello {new_ruolo.upper()} - Permessi: {', '.join(permessi_list) if permessi_list else 'base'}")
                        st.balloons()
                        st.info(f"L'utente può fare login con: {new_username.strip().lower()} / {new_pwd.strip()} - Ruolo: {new_ruolo}")
                        st.rerun()
                    else:
                        st.error("Errore salvataggio utenti.json - verifica permessi file")
    
    with tab3:
        st.markdown("#### ✏️ Modifica / Elimina Utente - Solo Amministratore")
        st.warning("Solo amministratore può modificare livelli accesso e eliminare utenti")
        usernames = [u.get("username") for u in utenti]
        sel_user = st.selectbox("Seleziona utente da modificare", ["-- Seleziona --"] + usernames, key="sel_user_edit_adv")
        if sel_user != "-- Seleziona --":
            user_obj = next((u for u in utenti if u.get("username") == sel_user), None)
            if user_obj:
                st.markdown(f"#### Modifica: {user_obj.get('nome')} ({user_obj.get('username')})")
                c1, c2 = st.columns(2)
                with c1:
                    nuovo_nome = st.text_input("Nome Completo", value=user_obj.get("nome",""), key="edit_nome_adv")
                    nuovo_ruolo = st.selectbox("Livello Accesso / Ruolo", 
                        ["amministratore","coordinatore","operatore","volontario","lettore"], 
                        index=["amministratore","coordinatore","operatore","volontario","lettore"].index(user_obj.get("ruolo","operatore")) if user_obj.get("ruolo") in ["amministratore","coordinatore","operatore","volontario","lettore"] else 2,
                        key="edit_ruolo_adv")
                    attivo = st.checkbox("Utente Attivo", value=user_obj.get("attivo",True), key="edit_attivo_adv")
                    st.caption(f"Creato da: {user_obj.get('creato_da','sistema')} il {user_obj.get('data_creazione','--')}")
                with c2:
                    nuova_pwd = st.text_input("Nuova Password (lascia vuoto per non cambiare)", type="password", key="edit_pwd_adv")
                    st.caption(f"Username: {user_obj.get('username')} - Non modificabile - Serve per login")
                    st.caption(f"Ruolo attuale: {user_obj.get('ruolo')} - Nuovo: {nuovo_ruolo}")
                    # Permessi
                    perm_attuali = user_obj.get("permessi", [])
                    st.write("Permessi attuali:", ", ".join(perm_attuali) if perm_attuali else "Base")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("💾 Salva Modifiche Livello Accesso", type="primary", use_container_width=True, key="btn_save_user_adv"):
                        for u in utenti:
                            if u.get("username") == sel_user:
                                u["nome"] = nuovo_nome
                                u["ruolo"] = nuovo_ruolo
                                u["attivo"] = attivo
                                if nuova_pwd.strip():
                                    u["password"] = hash_pwd(nuova_pwd.strip())
                                    st.info("Password aggiornata")
                        if save_utenti(utenti):
                            st.success(f"✅ Utente {sel_user} aggiornato a livello {nuovo_ruolo.upper()}")
                            st.rerun()
                        else:
                            st.error("Errore salvataggio")
                with col2:
                    if st.button("🔄 Reset Password a 'password'", use_container_width=True, key="btn_reset_pwd"):
                        for u in utenti:
                            if u.get("username") == sel_user:
                                u["password"] = hash_pwd("password")
                        save_utenti(utenti)
                        st.success(f"Password di {sel_user} resettata a 'password'")
                        st.rerun()
                with col3:
                    if st.button("🗑️ Elimina Utente", use_container_width=True, key="btn_del_user_adv"):
                        if sel_user == "admin":
                            st.error("⛔ Non puoi eliminare admin principale - è amministratore di sistema")
                        else:
                            # Conferma
                            if st.session_state.get("conferma_elimina") == sel_user:
                                utenti = [u for u in utenti if u.get("username") != sel_user]
                                save_utenti(utenti)
                                st.success(f"Utente {sel_user} eliminato definitivamente")
                                st.session_state["conferma_elimina"] = None
                                st.rerun()
                            else:
                                st.session_state["conferma_elimina"] = sel_user
                                st.warning(f"Clicca di nuovo Elimina per confermare eliminazione di {sel_user}")
    
    with tab3:
        st.markdown("#### 🟢 Utenti Online - Presenza")
        try:
            presenza = load_presenza()
            if presenza:
                df_pres = pd.DataFrame(presenza)
                st.dataframe(df_pres, use_container_width=True)
                st.success(f"{len(presenza)} utenti collegati ultimi 30 min")
                if st.button("🧹 Pulisci Presenza", use_container_width=True):
                    save_presenza([])
                    st.success("Presenza pulita")
                    st.rerun()
            else:
                st.info("Nessun utente online oltre te")
        except Exception as e:
            st.error(f"Errore presenza: {e}")
        
        st.divider()
        st.markdown("""
        #### ℹ️ Come funziona multi-utente contemporaneo?
        - **Sì, più utenti possono aprire il progetto insieme!**
        - Ogni utente apre link Streamlit su browser diverso (PC, telefono)
        - Login con username/password diversi
        - Su Streamlit Cloud session_state è separato per utente (dati in memoria non condivisi)
        - Ma utenti.json e presenza.json sono file condivisi sul server (visibili a tutti)
        - Per dati condivisi in tempo reale (volontari, brogliaccio) serve database esterno:
          - Opzione 1: Google Sheets come DB
          - Opzione 2: Supabase / Firebase (gratis)
          - Opzione 3: File JSON su GitHub + sync
        - Per ora: chat presenza funziona, dati form restano locali per utente (su Cloud si resettano a reboot)
        - Su PC locale (localhost): tutti i dati condivisi se usi file JSON
        """)

# BACKUP - Import/Export singolo + totale - gg/mm/aaaa
# BACKUP - Import/Export singolo + totale - gg/mm/aaaa - FIX TEMPLATE ODV
elif cur == "Backup":
    hdr()
    hdr_form("BACKUP - Template ODV + Import Multiplo - Solo Excel")

    FORM_KEYS = {
        "Volontari (con foto)": "volontari",
        "DB Radio": "radio_db",
        "Consegna Radio": "consegna_radio",
        "Alias Radio": "alias_radio",
        "Brogliaccio": "brogliaccio",
        "Eventi": "eventi",
        "Emergenze": "emergenze",
        "Check-in": "checkin",
        "Interventi Emergenza": "interventi",
        "Tabella Interventi Emergenza": "tabella_interventi",
        "Mezzi": "mezzi",
        "Attrezzature": "attrezzature",
        "Mappe Postazioni": "mappa_avanzata_markers",
        "Libreria Icone": "icone",
        "Turni": "turni",
        "Chat": "chat",
        "Posizioni PD785": "posizioni_pd785",
        "Posizioni Anytone": "posizioni_anytone"
    }

    st.markdown("""
    <div style="background:#e8f5e9;padding:10px;border-radius:8px;border-left:4px solid #1A5D1A;margin-bottom:12px;">
    <b>NUOVO: Template Excel per ODV - Invia file vuoto, ODV compila, tu importi in Volontari senza inserire uno per uno!</b><br>
    <small>Backup Totale | Template ODV | Import Multi-Foglio | Solo Excel</small>
    </div>
    """, unsafe_allow_html=True)

    # Riepilogo
    cols = st.columns(4)
    tot_records = 0
    for i, (label, key) in enumerate(FORM_KEYS.items()):
        cnt = len(st.session_state.get(key, []))
        tot_records += cnt
        cols[i % 4].metric(label[:18], cnt)
    st.metric("Totale Record", tot_records)

    st.divider()

    # === SEZIONE 1: TEMPLATE EXCEL PER ODV - VOLONTARI ===
    st.markdown("### 📋 TEMPLATE EXCEL PER ODV - Volontari")
    st.info("Scarica template vuoto, invialo alle ODV, loro compilano Nome/Cognome/CF etc, ti rimandano file, tu lo importi sotto in un click!")

    def get_volontari_template_df():
        # Template OFFICE 2016 COMPATIBILE - solo header, no righe esempio che danno errore formato
        columns = [
            "Nome", "Cognome", "Comune", "Via", "CapoODV", "ODVAppartenenza",
            "DataNascita", "CodFisc", "Cellulare", "Email", "TelEmergenza",
            "Ruolo", "Squadra", "RadioID", "Documento", "ScadDoc", "Note"
        ]
        # Office 2016 FIX: DataFrame vuoto solo con colonne, niente righe esempio
        # Office 2016 da errore "formato non valido" se ci sono righe con tipi misti esempio
        return pd.DataFrame(columns=columns)

    c_t1, c_t2 = st.columns(2)
    with c_t1:
        df_template_vol = get_volontari_template_df()
        st.dataframe(df_template_vol, use_container_width=True)
        st.download_button(
            "📥 Scarica TEMPLATE Volontari per ODV (Excel vuoto + esempio)",
            data=to_excel(df_template_vol),
            file_name="TEMPLATE_Volontari_ODV_da_compilare.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            type="primary",
            key="download_template_vol_odv"
        )
    with c_t2:
        st.markdown("""
        **Istruzioni per ODV:**
        1. Scarica template a sinistra
        2. Compila righe: Nome, Cognome, Comune, CapoODV, Cellulare...
        3. Data formato: gg/mm/aaaa (es: 15/06/1985)
        4. Lascia prima riga esempio o cancellala
        5. Salva e rimanda file a te
        6. Tu carichi file sotto in "Import Template ODV"
        
        **Campi obbligatori:** Nome, Cognome, CapoODV
        """)
        # Template anche per altri form
        sel_template_other = st.selectbox("Scarica Template altro Form", ["--"] + list(FORM_KEYS.keys()), key="sel_template_other")
        if sel_template_other != "--":
            key_other = FORM_KEYS[sel_template_other]
            data_other = st.session_state.get(key_other, [])
            if data_other:
                df_other = pd.DataFrame([{k:v for k,v in r.items() if "Bytes" not in k and "Foto" not in k and "File" not in k} for r in data_other[:1]])
                if df_other.empty:
                    df_other = pd.DataFrame(columns=["Col1","Col2"])
            else:
                # Template vuoto con colonne generiche
                df_other = pd.DataFrame(columns=["Campo1","Campo2","Note"])
            st.download_button(
                f"📥 Template {sel_template_other}",
                data=to_excel(df_other),
                file_name=f"TEMPLATE_{key_other}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                key=f"tpl_{key_other}"
            )

    st.divider()

    # Backup Totale Excel
    st.markdown("### 💾 Backup Totale Excel")
    c1, c2, c3 = st.columns(3)
    with c1:
        try:
            datasets = {}
            for label, key in FORM_KEYS.items():
                data = st.session_state.get(key, [])
                if data:
                    clean = [{kk: vv for kk, vv in r.items() if "Bytes" not in kk and "Foto" not in kk and "File" not in kk} for r in data if isinstance(r, dict)]
                    if clean:
                        datasets[label[:31]] = pd.DataFrame(clean)
            if datasets:
                st.download_button("⬇️ Backup Totale Excel", data=to_excel_multi(datasets), file_name=f"backup_totale_{datetime.now().strftime('%Y%m%d')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True, type="primary", key="backup_tot_excel")
            else:
                st.info("Nessun dato")
        except Exception as e:
            st.error(f"Excel: {e}")
    with c2:
        if REPORTLAB_OK:
            try:
                df_summary = pd.DataFrame([{"Form": label, "Record": len(st.session_state.get(key, []))} for label, key in FORM_KEYS.items()])
                st.download_button("⬇️ PDF Riepilogo", data=to_pdf(df_summary, "BACKUP TOTALE"), file_name="backup_riepilogo.pdf", mime="application/pdf", use_container_width=True, key="backup_pdf")
            except:
                pass
    with c3:
        if st.button("🗑️ Azzera Tutto", use_container_width=True, key="azzera_backup_unico"):
            for k in FORM_KEYS.values():
                st.session_state[k] = []
            st.success("Azzerati")
            st.rerun()

    st.divider()

    # Export Singolo Excel
    st.markdown("### 📄 Export Singolo Form - Solo Excel")
    sel_label = st.selectbox("Seleziona Form per Export Excel", list(FORM_KEYS.keys()), key="backup_sel_form_unico")
    sel_key = FORM_KEYS[sel_label]
    sel_data = st.session_state.get(sel_key, [])
    st.metric(f"Record in {sel_label}", len(sel_data))
    if sel_data:
        df_sel = pd.DataFrame([{k:v for k,v in r.items() if "Bytes" not in k and "Foto" not in k and "File" not in k} for r in sel_data if isinstance(r, dict)])
        st.dataframe(df_sel.head(20), use_container_width=True)
        c1, c2 = st.columns(2)
        with c1:
            st.download_button(f"⬇️ Excel {sel_label}", data=to_excel(df_sel), file_name=f"{sel_key}_{datetime.now().strftime('%Y%m%d')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True, key=f"exp_excel_{sel_key}_unico")
        with c2:
            if REPORTLAB_OK:
                st.download_button(f"📄 PDF {sel_label}", data=to_pdf(df_sel, sel_label.upper()), file_name=f"{sel_key}.pdf", mime="application/pdf", use_container_width=True, key=f"exp_pdf_{sel_key}_unico")
    else:
        st.warning(f"{sel_label} vuoto")

    st.divider()

    # === IMPORT TEMPLATE ODV - NUOVO - PER VOLONTARI ===
    st.markdown("### 📥 IMPORT TEMPLATE ODV - Volontari da Excel")
    st.success("Carica qui il file Excel compilato dalle ODV - Importa tutti i volontari in un click senza inserire uno per uno!")

    sel_label_imp_odv = st.selectbox("Form destinazione", ["Volontari (con foto)"] + list(FORM_KEYS.keys()), index=0, key="import_odv_dest")
    sel_key_imp_odv = FORM_KEYS.get(sel_label_imp_odv, "volontari")
    up_mode_odv = st.radio("Modalità", ["Aggiungi a esistenti", "Sostituisci tutto"], key="up_mode_odv", horizontal=True)
    up_file_odv = st.file_uploader(f"Carica Excel ODV compilato per {sel_label_imp_odv}", type=["xlsx", "xls"], key="up_odv_excel")

    if up_file_odv:
        try:
            df_odv = None
            last_err = ""
            # Prova lettura con engine automatico
            for eng in [None, "openpyxl", "xlrd"]:
                try:
                    up_file_odv.seek(0)
                    if eng is None:
                        df_odv = pd.read_excel(up_file_odv)
                    else:
                        df_odv = pd.read_excel(up_file_odv, engine=eng)
                    if df_odv is not None and not df_odv.empty:
                        break
                except Exception as e:
                    last_err = str(e)
                    continue

            if df_odv is not None and not df_odv.empty:
                # Pulisci colonne vuote e righe vuote
                df_odv = df_odv.dropna(how='all')
                # Rimuovi righe dove Nome e Cognome vuoti
                if "Nome" in df_odv.columns and "Cognome" in df_odv.columns:
                    df_odv = df_odv[~(df_odv["Nome"].astype(str).str.strip().isin(["", "nan", "None"]) & df_odv["Cognome"].astype(str).str.strip().isin(["", "nan", "None"]))]
                # Rimuovi riga esempio se c'è
                df_odv = df_odv[~((df_odv.astype(str).apply(lambda x: x.str.contains("Esempio", na=False)).any(axis=1)) | (df_odv.astype(str).apply(lambda x: x.str.contains("gg/mm/aaaa", na=False)).any(axis=1)))]

                st.success(f"✅ {len(df_odv)} volontari trovati nel file Excel ODV")
                st.dataframe(df_odv.head(30), use_container_width=True)

                # Mappatura colonne -> campi volontari
                # Converte DataNascita in formato gg/mm/aaaa se necessario
                if st.button(f"✅ IMPORTA {len(df_odv)} VOLONTARI IN {sel_label_imp_odv}", type="primary", use_container_width=True, key="btn_import_odv_vol"):
                    imported_list = []
                    for _, row in df_odv.iterrows():
                        rec = {}
                        for col in df_odv.columns:
                            val = row[col]
                            # Salta NaN
                            if pd.isna(val):
                                continue
                            # Converte date
                            if "Data" in col or "Scad" in col:
                                try:
                                    if isinstance(val, (pd.Timestamp, datetime, date)):
                                        rec[col] = val.strftime("%d/%m/%Y")
                                    else:
                                        rec[col] = str(val).strip()
                                except:
                                    rec[col] = str(val)
                            else:
                                rec[col] = str(val).strip() if isinstance(val, str) else val
                        # Normalizza chiavi comuni
                        # Mappa CodFisc varianti
                        if "CodFisc" not in rec:
                            for k in ["CodiceFiscale","CF","Codice Fiscale"]:
                                if k in rec:
                                    rec["CodFisc"] = rec.pop(k)
                        # Aggiungi campi default se mancano
                        if "ODVAppartenenza" not in rec:
                            rec["ODVAppartenenza"] = "ANA Varese"
                        if "Ruolo" not in rec:
                            rec["Ruolo"] = "Volontario"
                        if "Squadra" not in rec:
                            rec["Squadra"] = "Squadra A"
                        if "Comune" not in rec:
                            rec["Comune"] = "Varese"
                        # Solo se ha Nome o Cognome
                        if rec.get("Nome") or rec.get("Cognome"):
                            imported_list.append(rec)

                    if up_mode_odv.startswith("Sostituisci"):
                        st.session_state[sel_key_imp_odv] = imported_list
                    else:
                        st.session_state[sel_key_imp_odv] = st.session_state.get(sel_key_imp_odv, []) + imported_list

                    st.success(f"🎉 Importati {len(imported_list)} volontari in {sel_label_imp_odv}!")
                    st.balloons()
                    st.rerun()
            elif df_odv is not None:
                st.warning("File Excel vuoto o solo intestazioni")
            else:
                st.error(f"Errore lettura Excel: {last_err}")
                st.error("Verifica che file sia .xlsx valido e che requirements.txt contenga openpyxl, xlrd")
        except Exception as e:
            st.error(f"Errore import ODV: {e}")
            import traceback
            st.code(traceback.format_exc())

    st.divider()

    # Import Singolo - Solo Excel - FIX DEFINITIVO - Mantenuto per compatibilità
    st.markdown("### 📥 Import Singolo Form - Solo Excel xlsx/xls (Generico)")
    sel_label_imp = st.selectbox("Seleziona Form per Import Excel", list(FORM_KEYS.keys()), key="import_sel_form_excel")
    sel_key_imp = FORM_KEYS[sel_label_imp]
    up_mode_single = st.radio("Modalità Import Singolo Excel", ["Aggiungi", "Sostituisci"], key="up_mode_single_excel", horizontal=True)
    up_file_single = st.file_uploader(f"Carica Excel per {sel_label_imp} - Solo xlsx/xls", type=["xlsx", "xls"], key="up_single_excel")
    if up_file_single:
        try:
            df_imp = None
            last_err = ""
            for eng in [None, "openpyxl", "xlrd"]:
                try:
                    up_file_single.seek(0)
                    if eng is None:
                        df_imp = pd.read_excel(up_file_single)
                    else:
                        df_imp = pd.read_excel(up_file_single, engine=eng)
                    if df_imp is not None and len(df_imp.columns) > 0:
                        break
                except Exception as e:
                    last_err = str(e)
                    continue

            if df_imp is not None and not df_imp.empty:
                imported = df_imp.to_dict(orient="records")
                st.success(f"{len(imported)} record letti da Excel - OK")
                st.dataframe(pd.DataFrame(imported).head(10), use_container_width=True)
                if st.button(f"✅ Importa Excel in {sel_label_imp}", type="primary", use_container_width=True, key=f"btn_import_excel_{sel_key_imp}"):
                    if up_mode_single == "Sostituisci":
                        st.session_state[sel_key_imp] = imported
                    else:
                        st.session_state[sel_key_imp] = st.session_state.get(sel_key_imp, []) + imported
                    st.success(f"Importato {len(imported)} record in {sel_label_imp}")
                    st.rerun()
            elif df_imp is not None:
                st.warning("File Excel vuoto")
            else:
                st.error(f"Errore lettura Excel: {last_err}")
                if "openpyxl" in last_err.lower():
                    st.error("⚠️ openpyxl non installato - Controlla requirements.txt e Reboot Cloud")
        except Exception as e:
            st.error(f"Errore import Excel: {e}")

    st.divider()

    # Import Totale - Solo Excel Multi-foglio - Un file con tanti fogli
    st.markdown("### 📥 Import Backup Totale - Solo Excel xlsx/xls Multi-fogli")
    st.info("Carica un file Excel con più fogli: ogni foglio = un form (Volontari, Radio, etc). Importa tutto in un click!")
    up_total_excel = st.file_uploader("Carica Backup Totale Excel - Solo xlsx/xls", type=["xlsx", "xls"], key="up_total_excel")
    if up_total_excel:
        try:
            xls = None
            last_err = ""
            for eng in [None, "openpyxl", "xlrd"]:
                try:
                    up_total_excel.seek(0)
                    if eng is None:
                        xls = pd.ExcelFile(up_total_excel)
                    else:
                        xls = pd.ExcelFile(up_total_excel, engine=eng)
                    if xls is not None:
                        break
                except Exception as e:
                    last_err = str(e)
                    continue

            if xls is not None:
                st.write(f"Fogli trovati: {xls.sheet_names}")
                for sh in xls.sheet_names:
                    try:
                        df_preview = pd.read_excel(xls, sheet_name=sh)
                        st.write(f"**{sh}**: {len(df_preview)} righe")
                    except:
                        pass
                mode_total = st.radio("Modalità Import Totale Excel", ["Aggiungi", "Sostituisci"], key="mode_total_excel", horizontal=True)
                if st.button("✅ CONFERMA IMPORT TOTALE EXCEL MULTI-FOGLIO", type="primary", use_container_width=True, key="btn_import_tot_excel"):
                    for sheet in xls.sheet_names:
                        for label, key in FORM_KEYS.items():
                            if label[:31].lower() in sheet.lower() or key.lower() in sheet.lower() or label.lower() in sheet.lower():
                                try:
                                    df_sheet = pd.read_excel(xls, sheet_name=sheet)
                                    df_sheet = df_sheet.dropna(how='all')
                                    imported_sheet = df_sheet.to_dict(orient="records")
                                    if imported_sheet:
                                        if mode_total.startswith("Sostituisci"):
                                            st.session_state[key] = imported_sheet
                                        else:
                                            st.session_state[key] = st.session_state.get(key, []) + imported_sheet
                                        st.success(f"Importato {len(imported_sheet)} in {label}")
                                except Exception as e:
                                    st.error(f"Errore foglio {sheet}: {e}")
                                break
                    st.success("Import totale Excel completato!")
                    st.balloons()
                    st.rerun()
            else:
                st.error(f"Errore apertura Excel: {last_err}")
        except Exception as e:
            st.error(f"Errore import totale Excel: {e}")

    st.divider()

    with st.expander("⚠️ Azzera Singolo Form"):
        sel_zero = st.selectbox("Form da azzerare", ["--"] + list(FORM_KEYS.keys()), key="zero_sel_unico")
        if sel_zero != "--":
            if st.button(f"🗑️ Azzera {sel_zero}", key=f"btn_zero_{sel_zero}"):
                st.session_state[FORM_KEYS[sel_zero]] = []
                st.success(f"{sel_zero} azzerato")
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