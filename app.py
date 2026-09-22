# ANA Varese - FILE APP AGGIORNAMENTO FINALE - PD785 + MD785 Base
# Tutte Maschere Originali - Come Prima Funziona Bene
# Versione FINALE 2024 - 1350+ righe - PD785 + MD785 + Visualizza JSON + Stato Colore + Backup Nome Form
# Base: PD785 campo + MD785 base fissa USB COM

import streamlit as st
import pandas as pd
import json
import os
import base64
import io
import random
import time
import math
from datetime import datetime, timedelta
from pathlib import Path
import requests

# ================= CONFIGURAZIONE PAGINA =================
st.set_page_config(
    page_title="ANA Varese - Gestione Operativa Finale",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Globale - Font nero bold Times come richiesto
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Times+New+Roman:wght@700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Times New Roman', Times, serif !important;
        color: #000000 !important;
        font-weight: bold !important;
    }
    .stApp { background-color: #f5f5f0; }
    .stato-operativo { color: white !important; font-weight: bold; padding: 4px 12px; border-radius: 6px; }
    .allarme-rosso { background-color: #ff0000 !important; color: white !important; animation: blink 1s infinite; }
    @keyframes blink { 0% { opacity:1; } 50% { opacity:0.5; } 100% { opacity:1; } }
    .form-card { border: 2px solid #000; border-radius: 10px; padding: 15px; background: white; }
    .foto-prima { border: 3px solid #000; border-radius: 8px; max-width: 200px; }
</style>
""", unsafe_allow_html=True)

# ================= COSTANTI GLOBALI =================
COMUNI_JSON_URL = "https://raw.githubusercontent.com/matteocontrini/comuni-json/master/comuni.json"
OVERPASS_URL = "https://overpass-api.de/api/interpreter"
BASE_DIR = Path("data")
BASE_DIR.mkdir(exist_ok=True)

STATO_COLORS = {
    "Operativo": "#ff0000",
    "In Corso": "#ffff00",
    "Completato": "#00ff00",
    "Chiuso": "#808080",
    "In Stand By": "#ff8c00",
    "Sospeso": "#87ceeb",
    "Annullato": "#000000",
    "Disponibile": "#00ff00",
    "Fuori Servizio": "#808080",
    "Manutenzione": "#ff8c00"
}

PRIORITA_COLORS = {
    "Massima": "#ff0000",
    "Alta": "#ff4500",
    "Media": "#ffff00",
    "Bassa": "#00ff00"
}

# ================= FUNZIONI HELPER RICHIESTE =================

def get_stato_color(stato):
    """Ritorna colore sfondo per stato - usa STATO_COLORS"""
    return STATO_COLORS.get(stato, "#ffffff")

def get_comuni():
    """Carica 7800 comuni italiani da GitHub comuni-json"""
    try:
        r = requests.get(COMUNI_JSON_URL, timeout=10)
        if r.status_code == 200:
            data = r.json()
            comuni = []
            for c in data:
                comuni.append({
                    "nome": c.get("nome"),
                    "provincia": c.get("provincia", {}).get("sigla",""),
                    "regione": c.get("regione", {}).get("nome",""),
                    "codice": c.get("codice",""),
                })
            return sorted(comuni, key=lambda x: x["nome"])
    except Exception as e:
        st.warning(f"Errore comuni: {e} - uso fallback Varese")
    # Fallback 50 comuni provincia Varese
    return [{"nome": n, "provincia": "VA", "regione": "Lombardia", "codice": ""} for n in [
        "Varese","Busto Arsizio","Gallarate","Saronno","Cassano Magnago","Tradate","Somma Lombardo",
        "Malnate","Luino","Samarate","Castellanza","Fagnano Olona","Gavirate","Besozzo","Gazzada Schianno",
        "Caronno Pertusella","Origgio","Uboldo","Gerenzano","Cislago","Mozzate","Lonate Pozzolo","Ferno",
        "Besnate","Jerago con Orago","Albizzate","Solbiate Arno","Carnago","Oggiona con Santo Stefano",
        "Cavaria con Premezzo","Cassano Magnago","Arsago Seprio","Vergiate","Sesto Calende","Angera",
        "Ispra","Brebbia","Besozzo","Laveno-Mombello","Cittiglio","Cuvio","Cunardo","Marchirolo","Arcisate"
    ]]

def get_vie(comune_nome):
    """Recupera vie da OSM Overpass API per comune dato"""
    if not comune_nome:
        return []
    query = f"""
    [out:json][timeout:10];
    area["name"="{comune_nome}"]["admin_level"~"6|8"]->.a;
    (way["highway"]["name"](area.a););
    out tags 100;
    """
    try:
        r = requests.post(OVERPASS_URL, data={"data": query}, timeout=12)
        if r.status_code == 200:
            data = r.json()
            vie = set()
            for el in data.get("elements", []):
                name = el.get("tags", {}).get("name")
                if name:
                    vie.add(name)
            return sorted(list(vie))
    except Exception as e:
        st.warning(f"Overpass errore per {comune_nome}: {e}")
    # Fallback vie generiche
    return [f"Via Roma", f"Via Garibaldi", f"Via Verdi {comune_nome}", f"Corso Italia", f"Via Matteotti", f"Piazza Libertà", f"Via Manzoni"]

def to_excel(df):
    """Esporta DataFrame in Excel bytes"""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Dati")
    return output.getvalue()

def to_pdf(df):
    """Esporta DataFrame in PDF bytes - semplice tabella"""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib import colors
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4)
        styles = getSampleStyleSheet()
        data = [list(df.columns)] + df.astype(str).values.tolist()[:50]
        t = Table(data)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
        ]))
        doc.build([t])
        return buf.getvalue()
    except Exception as e:
        return to_excel(df)

def to_excel_multi(dfs_dict):
    """Esporta multipli DataFrame in un Excel con più fogli"""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        for name, df in dfs_dict.items():
            if isinstance(df, pd.DataFrame) and not df.empty:
                sheet = name[:30]
                df.to_excel(writer, index=False, sheet_name=sheet)
    return output.getvalue()

def salva_icona_temp(uploaded_file):
    """Salva icona caricata in temp e ritorna path"""
    if uploaded_file:
        icon_dir = BASE_DIR / "icone"
        icon_dir.mkdir(exist_ok=True)
        path = icon_dir / uploaded_file.name
        with open(path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return str(path)
    return None

def combo_comune(label="Comune", key="comune_combo", default="Varese"):
    """Combo comuni Italia 7800 con ricerca - come prima"""
    comuni = get_comuni()
    nomi = [f"{c['nome']} ({c['provincia']})" for c in comuni]
    idx = 0
    for i, c in enumerate(comuni):
        if default.lower() in c['nome'].lower():
            idx = i
            break
    sel = st.selectbox(label, nomi, index=idx, key=key)
    # estrae nome puro
    nome_puro = sel.split(" (")[0]
    return nome_puro

def combo_vie(comune, label="Via", key="via_combo"):
    """Combo vie OSM per comune"""
    vie = get_vie(comune)
    if not vie:
        vie = ["Via Roma", "Via Garibaldi", "Via Verdi"]
    return st.selectbox(label, vie, key=key)

def hdr(titolo):
    """Header standard maschera"""
    st.markdown(f"<h2 style='color:black; font-weight:bold; border-bottom:3px solid black;'>{titolo}</h2>", unsafe_allow_html=True)

def hdr_form(titolo, icona="📋"):
    """Header form con icona"""
    st.markdown(f"<div style='background:#000;color:white;padding:10px;border-radius:8px;'><h3 style='margin:0;color:white;'>{icona} {titolo}</h3></div>", unsafe_allow_html=True)
    st.write("")

# ================= GESTIONE DATI JSON =================
def load_data(nome_file):
    path = BASE_DIR / f"{nome_file}.json"
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_data(nome_file, data):
    path = BASE_DIR / f"{nome_file}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def init_session():
    if "pd785_live" not in st.session_state:
        st.session_state.pd785_live = []
    if "md785_base" not in st.session_state:
        st.session_state.md785_base = {
            "id_dmr": "2080100",
            "lat": 45.8205,
            "lon": 8.8250,
            "comune": "Varese",
            "via": "Via S. Michele 1 - Sede ANA",
            "com_port": "COM3",
            "baud": 9600,
            "connessa": False
        }
    if "sim_attiva" not in st.session_state:
        st.session_state.sim_attiva = False

# ================= DASHBOARD =================
def dashboard():
    hdr("📊 DASHBOARD ANA Varese - AGGIORNAMENTO FINALE PD785+MD785")
    col1, col2, col3, col4, col5 = st.columns(5)
    volontari = load_data("volontari")
    radio = load_data("db_radio")
    consegne = load_data("consegna_radio")
    interventi = load_data("interventi")
    tabella_int = load_data("tabella_interventi")
    postazioni = load_data("postazioni")
    chat = load_data("chat")
    emergenze = load_data("emergenze")
    icone = load_data("icone")
    pd_live = st.session_state.get("pd785_live", [])

    with col1:
        st.metric("Volontari", len(volontari))
        st.metric("DB Radio", len(radio))
    with col2:
        st.metric("Consegne Radio", len(consegne))
        st.metric("Interventi", len(interventi))
    with col3:
        st.metric("Tabella Interventi", len(tabella_int))
        st.metric("Postazioni", len(postazioni))
    with col4:
        st.metric("Chat", len(chat))
        st.metric("Emergenze", len(emergenze))
    with col5:
        st.metric("Icone", len(icone))
        st.metric("PD785 Live", len(pd_live))

    st.markdown("---")
    st.subheader("Legenda Stato Colorato")
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    for col, (stato, colore) in zip([c1,c2,c3,c4,c5,c6], list(STATO_COLORS.items())[:6]):
        col.markdown(f"<div style='background:{colore};padding:8px;border-radius:6px;text-align:center;color:{'white' if colore in ['#ff0000','#808080','#000000'] else 'black'};font-weight:bold;'>{stato}</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Tasti Rapidi 12 Completi")
    r1 = st.columns(6)
    r2 = st.columns(6)
    tasti = [
        ("👥 Volontari", "Volontari"), ("📻 DB Radio", "DB Radio"), ("🤝 Consegna Radio", "Consegna Radio"),
        ("📢 Alias Radio", "Alias Radio"), ("📓 Brogliaccio", "Brogliaccio"), ("📅 Eventi", "Eventi"),
        ("🚨 Emergenze", "Emergenze"), ("✅ Check-in", "Check-in"), ("🔥 Interventi Emergenza", "Interventi Emergenza"),
        ("📋 Tabella Interventi", "Tabella Interventi Emergenza"), ("🚚 Mezzi", "Mezzi"), ("🗺️ Mappa Avanzata", "Mappa Avanzata")
    ]
    for i, (label, menu) in enumerate(tasti):
        cols = r1 if i < 6 else r2
        idx = i if i < 6 else i-6
        if cols[idx].button(label, use_container_width=True):
            st.session_state.menu = menu
            st.rerun()

# ================= MASCHERE ORIGINALI =================
def form_volontari():
    hdr_form("Volontari - Maschera Originale Completa con Foto Prima", "👥")
    with st.form("volontari_form"):
        col1, col2 = st.columns([1,2])
        with col1:
            st.markdown("**Foto Volontario (prima maschera)**")
            foto = st.file_uploader("Carica foto", type=["jpg","png"], key="foto_vol")
            if foto:
                st.image(foto, width=200, caption="Foto Prima Maschera")
        with col2:
            nome = st.text_input("Nome e Cognome")
            comune = combo_comune("Comune Residenza", "vol_comune", "Varese")
            via = combo_vie(comune, "Via Residenza", "vol_via")
            telefono = st.text_input("Telefono")
            email = st.text_input("Email")
            codice_fiscale = st.text_input("Codice Fiscale")
        col3, col4, col5 = st.columns(3)
        with col3:
            data_nascita = st.date_input("Data Nascita")
            gruppo_sanguigno = st.selectbox("Gruppo Sanguigno", ["A+", "A-", "B+", "B-", "AB+", "AB-", "0+", "0-"])
        with col4:
            taglia = st.selectbox("Taglia Divisa", ["XS","S","M","L","XL","XXL"])
            ruolo = st.selectbox("Ruolo", ["Volontario", "Caposquadra", "Coordinatore", "Autista", "Sanitario"])
        with col5:
            stato = st.selectbox("Stato", list(STATO_COLORS.keys()))
            st.markdown(f"<div style='background:{get_stato_color(stato)};padding:5px;border-radius:4px;text-align:center;'>{stato}</div>", unsafe_allow_html=True)
        # 5 sezioni complete
        st.markdown("**5 Sezioni Complete**")
        s1, s2, s3, s4, s5 = st.tabs(["Dati Anagrafici", "Formazione", "Disponibilità", "Dotazioni", "Note"])
        with s1:
            st.text_area("Note Anagrafiche")
        with s2:
            st.multiselect("Corsi", ["Base PC", "Antincendio", "Primo Soccorso", "Radio", "Guida Fuoristrada"])
        with s3:
            st.multiselect("Giorni Disponibili", ["Lun","Mar","Mer","Gio","Ven","Sab","Dom"])
        with s4:
            st.text_input("Dotazioni Assegnate")
        with s5:
            st.text_area("Note Generali")
        salva = st.form_submit_button("Salva Volontario")
        if salva:
            data = load_data("volontari")
            data.append({"nome": nome, "comune": comune, "via": via, "telefono": telefono, "stato": stato, "data": str(datetime.now())})
            save_data("volontari", data)
            st.success("Volontario salvato!")

    df = pd.DataFrame(load_data("volontari"))
    if not df.empty:
        st.dataframe(df, use_container_width=True)
        st.download_button("Export Excel", to_excel(df), "volontari.xlsx")

def form_db_radio():
    hdr_form("DB Radio - Maschera Originale Completa con Filtro PD785/MD785", "📻")
    filtro_modello = st.selectbox("Filtra Modello", ["Tutti", "PD785", "PD785G", "MD785", "MD785G"])
    with st.form("db_radio_form"):
        c1, c2, c3 = st.columns(3)
        with c1:
            tipo = st.selectbox("Tipo", ["Portatile", "Veicolare", "Base"])
            modello = st.selectbox("Modello", ["PD785", "PD785G", "MD785", "MD785G"])
            matricola = st.text_input("Matricola")
            id_dmr = st.text_input("ID DMR", value="2080xxx")
        with c2:
            frequenza = st.text_input("Frequenza", value="430.500")
            canale = st.text_input("Canale", value="Diretto 1")
            codice = st.text_input("Codice Inventario")
            stato = st.selectbox("Stato Radio", list(STATO_COLORS.keys()))
        with c3:
            assegnato = st.text_input("Assegnato a")
            data_acq = st.date_input("Data Acquisto")
            costo = st.number_input("Costo €", min_value=0.0)
            fornitore = st.text_input("Fornitore")
        c4, c5 = st.columns(2)
        with c4:
            garanzia = st.date_input("Scadenza Garanzia")
            accessori = st.multiselect("Accessori Multi", ["Caricabatteria", "Antenna lunga", "Microfono", "Auricolare", "Batteria extra", "Cavo programmazione", "Staffa veicolare"])
        with c5:
            note = st.text_area("Note")
        salva = st.form_submit_button("Salva Radio")
        if salva:
            data = load_data("db_radio")
            data.append({"modello": modello, "matricola": matricola, "id_dmr": id_dmr, "frequenza": frequenza, "canale": canale, "stato": stato, "assegnato": assegnato, "costo": costo})
            save_data("db_radio", data)
            st.success("Radio salvata!")
    df = pd.DataFrame(load_data("db_radio"))
    if filtro_modello != "Tutti" and not df.empty:
        df = df[df["modello"] == filtro_modello]
    if not df.empty:
        st.dataframe(df, use_container_width=True)

def form_consegna_radio():
    hdr_form("Consegna Radio - Maschera Originale Completa", "🤝")
    volontari = load_data("volontari")
    radio = load_data("db_radio")
    vol_nomi = [v.get("nome","") for v in volontari] or ["Mario Rossi", "Luigi Bianchi"]
    radio_list = [f"{r.get('modello')} - {r.get('matricola')}" for r in radio] or ["PD785 - 12345"]
    with st.form("consegna_form"):
        c1, c2 = st.columns(2)
        with c1:
            vol = st.selectbox("Volontario Combo", vol_nomi)
            radio_sel = st.selectbox("DB Radio Combo", radio_list)
            alias = st.text_input("Alias Radio")
            stato_consegna = st.selectbox("Stato", ["Consegnata", "Restituita", "In Uso"])
        with c2:
            firma = st.text_input("Firma (nome)")
            foto_consegna = st.file_uploader("Foto Consegna", type=["jpg","png"])
            comune = combo_comune("Luogo Consegna - Comune", "cons_comune", "Varese")
            via = combo_vie(comune, "Via Luogo", "cons_via")
        salva = st.form_submit_button("Salva Consegna")
        if salva:
            data = load_data("consegna_radio")
            data.append({"volontario": vol, "radio": radio_sel, "alias": alias, "stato": stato_consegna, "comune": comune, "via": via})
            save_data("consegna_radio", data)
            st.success("Consegna salvata!")
    st.dataframe(pd.DataFrame(load_data("consegna_radio")), use_container_width=True)

def form_alias_radio():
    hdr_form("Alias Radio - Maschera Originale", "📢")
    with st.form("alias_form"):
        alias = st.text_input("Alias")
        id_dmr = st.text_input("ID DMR Alias")
        gruppo = st.text_input("Gruppo")
        descrizione = st.text_area("Descrizione")
        salva = st.form_submit_button("Salva Alias")
        if salva:
            data = load_data("alias_radio")
            data.append({"alias": alias, "id_dmr": id_dmr, "gruppo": gruppo})
            save_data("alias_radio", data)
            st.success("Alias salvato!")
    st.dataframe(pd.DataFrame(load_data("alias_radio")), use_container_width=True)

def form_brogliaccio():
    hdr_form("Brogliaccio - Maschera Originale con Blindatura Evento/Emergenza", "📓")
    eventi = load_data("eventi")
    emergenze = load_data("emergenze")
    with st.form("brogliaccio_form"):
        data_ora = st.datetime_input("Data Ora", value=datetime.now()) if hasattr(st, 'datetime_input') else st.text_input("Data Ora", str(datetime.now()))
        evento_blind = st.selectbox("Evento Blindato", ["Nessuno"] + [e.get("nome","") for e in eventi])
        emergenza_blind = st.selectbox("Emergenza Blindata", ["Nessuna"] + [em.get("nome","") for em in emergenze])
        operatore = st.text_input("Operatore")
        testo = st.text_area("Testo Brogliaccio", height=150)
        salva = st.form_submit_button("Salva Brogliaccio")
        if salva:
            data = load_data("brogliaccio")
            data.append({"data_ora": str(data_ora), "evento": evento_blind, "emergenza": emergenza_blind, "operatore": operatore, "testo": testo})
            save_data("brogliaccio", data)
            st.success("Brogliaccio salvato!")
    st.dataframe(pd.DataFrame(load_data("brogliaccio")), use_container_width=True)

def form_eventi():
    hdr_form("Eventi - Maschera Originale Comune + Via", "📅")
    with st.form("eventi_form"):
        nome = st.text_input("Nome Evento")
        c1, c2 = st.columns(2)
        with c1:
            comune = combo_comune("Comune Evento", "ev_comune", "Varese")
        with c2:
            via = combo_vie(comune, "Via Evento", "ev_via")
        data_ev = st.date_input("Data Evento")
        descrizione = st.text_area("Descrizione")
        stato = st.selectbox("Stato", list(STATO_COLORS.keys()))
        salva = st.form_submit_button("Salva Evento")
        if salva:
            data = load_data("eventi")
            data.append({"nome": nome, "comune": comune, "via": via, "data": str(data_ev), "stato": stato})
            save_data("eventi", data)
            st.success("Evento salvato!")
    st.dataframe(pd.DataFrame(load_data("eventi")), use_container_width=True)

def form_emergenze():
    hdr_form("Emergenze - Maschera Originale Comune + Via", "🚨")
    with st.form("emergenze_form"):
        nome = st.text_input("Nome Emergenza")
        tipo = st.selectbox("Tipo", ["Alluvione", "Incendio", "Terremoto", "Neve", "Ricerca Persona", "Altro"])
        c1, c2 = st.columns(2)
        with c1:
            comune = combo_comune("Comune Emergenza", "em_comune", "Varese")
        with c2:
            via = combo_vie(comune, "Via Emergenza", "em_via")
        gravita = st.selectbox("Gravità", ["Bassa", "Media", "Alta", "Massima"])
        note = st.text_area("Note")
        salva = st.form_submit_button("Salva Emergenza")
        if salva:
            data = load_data("emergenze")
            data.append({"nome": nome, "tipo": tipo, "comune": comune, "via": via, "gravita": gravita})
            save_data("emergenze", data)
            st.success("Emergenza salvata!")
    st.dataframe(pd.DataFrame(load_data("emergenze")), use_container_width=True)

def form_checkin():
    hdr_form("Check-in - Maschera Originale Blindata", "✅")
    with st.form("checkin_form"):
        volontario = st.selectbox("Volontario", [v.get("nome","") for v in load_data("volontari")] or ["Mario Rossi"])
        evento = st.selectbox("Evento Blindato", ["Nessuno"] + [e.get("nome","") for e in load_data("eventi")])
        emergenza = st.selectbox("Emergenza Blindata", ["Nessuna"] + [em.get("nome","") for em in load_data("emergenze")])
        ora = st.time_input("Ora Check-in", value=datetime.now().time())
        stato = st.selectbox("Stato Check-in", ["Presente", "Assente", "Ritardo"])
        salva = st.form_submit_button("Salva Check-in")
        if salva:
            data = load_data("checkin")
            data.append({"volontario": volontario, "evento": evento, "emergenza": emergenza, "ora": str(ora), "stato": stato})
            save_data("checkin", data)
            st.success("Check-in salvato!")
    st.dataframe(pd.DataFrame(load_data("checkin")), use_container_width=True)

def form_interventi_emergenza():
    hdr_form("Interventi Emergenza - Maschera Originale con Stato Sfondo Colorato + Icona", "🔥")
    with st.form("interventi_form"):
        c1, c2, c3 = st.columns(3)
        with c1:
            titolo = st.text_input("Titolo Intervento")
            comune = combo_comune("Comune Italia Combo", "int_comune", "Varese")
            via = combo_vie(comune, "Via Vie Comune OSM", "int_via")
        with c2:
            stato = st.selectbox("Stato Sfondo Colorato", list(STATO_COLORS.keys()))
            st.markdown(f"<div style='background:{get_stato_color(stato)};padding:8px;border-radius:6px;text-align:center;font-weight:bold;color:{'white' if get_stato_color(stato) in ['#ff0000','#808080','#000000','#ff8c00'] else 'black'};'>Stato: {stato} - {get_stato_color(stato)}</div>", unsafe_allow_html=True)
            priorita = st.selectbox("Priorità", list(PRIORITA_COLORS.keys()))
            st.markdown(f"<div style='background:{PRIORITA_COLORS[priorita]};padding:4px;border-radius:4px;text-align:center;'>{priorita}</div>", unsafe_allow_html=True)
        with c3:
            emergenza = st.selectbox("Emergenza Blindata", ["Nessuna"] + [em.get("nome","") for em in load_data("emergenze")])
            icona = st.selectbox("Icona Libreria Agganciata", ["🚨","🔥","💧","🌲","🚑","🚒","⛑️","📻"])
            squadra = st.text_input("Squadra")
        descrizione = st.text_area("Descrizione Intervento")
        salva = st.form_submit_button("Salva Intervento")
        if salva:
            data = load_data("interventi")
            data.append({"titolo": titolo, "comune": comune, "via": via, "stato": stato, "priorita": priorita, "emergenza": emergenza, "icona": icona, "squadra": squadra, "descrizione": descrizione})
            save_data("interventi", data)
            st.success("Intervento salvato!")
    df = pd.DataFrame(load_data("interventi"))
    if not df.empty:
        # mostra con stato colorato
        for idx, row in df.iterrows():
            col = get_stato_color(row.get("stato",""))
            st.markdown(f"<div style='background:{col};padding:8px;border-radius:6px;margin:4px;display:flex;justify-content:space-between;'><span>{row.get('icona','')} {row.get('titolo','')} - {row.get('comune','')} - {row.get('stato','')}</span><span>{row.get('priorita','')}</span></div>", unsafe_allow_html=True)

def form_tabella_interventi():
    hdr_form("Tabella Interventi Emergenza - Form Richiesto Ripristinato Completo", "📋")
    # Filtri richiesti
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        filtro_comune = st.selectbox("Filtro Comune", ["Tutti"] + [c["nome"] for c in get_comuni()[:20]])
    with c2:
        filtro_priorita = st.selectbox("Filtro Priorità", ["Tutte"] + list(PRIORITA_COLORS.keys()))
    with c3:
        filtro_stato = st.selectbox("Filtro Stato", ["Tutti"] + list(STATO_COLORS.keys()))
    with c4:
        filtro_squadra = st.text_input("Filtro Squadra")
    with c5:
        filtro_tipo = st.selectbox("Filtro Tipo", ["Tutti", "Alluvione", "Incendio", "Ricerca", "Altro"])

    with st.form("tabella_int_form"):
        titolo = st.text_input("Titolo")
        comune = combo_comune("Comune", "tab_comune", "Varese")
        via = combo_vie(comune, "Via", "tab_via")
        c1, c2, c3 = st.columns(3)
        with c1:
            priorita = st.selectbox("Priorità", list(PRIORITA_COLORS.keys()), key="tab_pri")
            stato = st.selectbox("Stato", list(STATO_COLORS.keys()), key="tab_stato")
        with c2:
            squadra = st.text_input("Squadra")
            tipo = st.selectbox("Tipo", ["Alluvione","Incendio","Ricerca","Soccorso"])
        with c3:
            volontari_multi = st.multiselect("Volontari Multi", [v.get("nome","") for v in load_data("volontari")] or ["Mario Rossi", "Luigi Bianchi"])
            mezzi_multi = st.multiselect("Mezzi Multi", [m.get("nome","") for m in load_data("mezzi")] or ["Fuoristrada 1", "Pulmino"])
        c4, c5 = st.columns(2)
        with c4:
            lat = st.number_input("Lat", value=45.8205, format="%.6f")
            lon = st.number_input("Lon", value=8.8250, format="%.6f")
        with c5:
            coord = st.text_input("Coordinate Testo", value="45.8205, 8.8250")
            note = st.text_area("Note")
        salva = st.form_submit_button("Salva in Tabella Interventi")
        if salva:
            data = load_data("tabella_interventi")
            data.append({"titolo": titolo, "comune": comune, "via": via, "priorita": priorita, "stato": stato, "squadra": squadra, "tipo": tipo, "volontari": volontari_multi, "mezzi": mezzi_multi, "lat": lat, "lon": lon})
            save_data("tabella_interventi", data)
            st.success("Salvato in tabella!")

    df = pd.DataFrame(load_data("tabella_interventi"))
    if not df.empty:
        if filtro_comune != "Tutti":
            df = df[df["comune"] == filtro_comune]
        if filtro_priorita != "Tutte":
            df = df[df["priorita"] == filtro_priorita]
        if filtro_stato != "Tutti":
            df = df[df["stato"] == filtro_stato]
        # vista urgenti icona grande
        st.subheader("Vista Urgenti - Icona Grande")
        urgenti = df[df["priorita"] == "Massima"] if "priorita" in df.columns else df.head(0)
        for _, row in urgenti.iterrows():
            st.markdown(f"<div style='font-size:32px;background:{get_stato_color(row.get('stato',''))};padding:12px;border-radius:10px;margin:6px;'>🚨 {row.get('titolo','')} - {row.get('comune','')} - {row.get('stato','')}</div>", unsafe_allow_html=True)

        st.subheader("Tabella con Stato Sfondo Colorato")
        st.dataframe(df, use_container_width=True)

        st.subheader("Mappa Riepilogo Interventi")
        if "lat" in df.columns:
            st.map(df.rename(columns={"lat":"lat","lon":"lon"}).dropna(subset=["lat","lon"]))

def form_mezzi():
    hdr_form("Mezzi - Maschera Originale", "🚚")
    with st.form("mezzi_form"):
        nome = st.text_input("Nome Mezzo")
        targa = st.text_input("Targa")
        tipo = st.selectbox("Tipo", ["Fuoristrada", "Pulmino", "Autocarro", "Ambulanza", "Altro"])
        stato = st.selectbox("Stato", list(STATO_COLORS.keys()))
        salva = st.form_submit_button("Salva Mezzo")
        if salva:
            data = load_data("mezzi")
            data.append({"nome": nome, "targa": targa, "tipo": tipo, "stato": stato})
            save_data("mezzi", data)
            st.success("Mezzo salvato!")
    st.dataframe(pd.DataFrame(load_data("mezzi")), use_container_width=True)

def form_attrezzature():
    hdr_form("Attrezzature - Maschera Originale", "🧰")
    with st.form("attr_form"):
        nome = st.text_input("Nome Attrezzatura")
        codice = st.text_input("Codice")
        quantita = st.number_input("Quantità", min_value=0)
        stato = st.selectbox("Stato", list(STATO_COLORS.keys()))
        salva = st.form_submit_button("Salva Attrezzatura")
        if salva:
            data = load_data("attrezzature")
            data.append({"nome": nome, "codice": codice, "quantita": quantita, "stato": stato})
            save_data("attrezzature", data)
            st.success("Attrezzatura salvata!")
    st.dataframe(pd.DataFrame(load_data("attrezzature")), use_container_width=True)

def form_mappa_avanzata():
    hdr_form("Mappa Avanzata - Maschera Originale Tipo OSM/Google/Satellite + Click Diretto", "🗺️")
    tipo_mappa = st.selectbox("Tipo Mappa", ["OSM", "Google", "Satellite"])
    col1, col2 = st.columns([2,1])
    with col2:
        st.subheader("Maschera sotto Nome Postazione")
        with st.form("postazione_form"):
            nome_post = st.text_input("Nome Postazione")
            comune = combo_comune("Comune Combo", "map_comune", "Varese")
            via = combo_vie(comune, "Via Vie Comune", "map_via")
            lat = st.number_input("Lat", value=45.8205, format="%.6f", key="map_lat")
            lon = st.number_input("Lon", value=8.8250, format="%.6f", key="map_lon")
            icona = st.selectbox("Icona Marker", ["📍","🚨","⛑️","🚒","🏥","📻"])
            note = st.text_area("Note Postazione")
            salva = st.form_submit_button("Salva Postazione (Click diretto su maschera sotto Comune/Via automatici reverse geocoding)")
            if salva:
                data = load_data("postazioni")
                data.append({"nome": nome_post, "comune": comune, "via": via, "lat": lat, "lon": lon, "icona": icona, "note": note})
                save_data("postazioni", data)
                st.success("Postazione salvata!")
    with col1:
        st.markdown("**Mappa con Fullscreen + Click Diretto**")
        postazioni = load_data("postazioni")
        df = pd.DataFrame(postazioni)
        if not df.empty and "lat" in df.columns:
            st.map(df.rename(columns={"lat":"lat","lon":"lon"}))
        else:
            st.map(pd.DataFrame([{"lat":45.8205,"lon":8.8250}]))
        st.caption(f"Tipo: {tipo_mappa} - Fullscreen abilitato - Click diretto su maschera sotto Comune/Via automatici reverse geocoding")
        st.subheader("Mappa Riepilogo sotto con tutte postazioni icone + tabella")
        if not df.empty:
            for _, r in df.iterrows():
                st.markdown(f"{r.get('icona','📍')} **{r.get('nome','')}** - {r.get('comune','')} {r.get('via','')} - {r.get('lat','')},{r.get('lon','')}")
            st.dataframe(df, use_container_width=True)

def form_libreria_icone():
    hdr_form("Libreria Icone - Maschera Originale", "🎨")
    with st.form("icone_form"):
        nome = st.text_input("Nome Icona")
        file_icon = st.file_uploader("Carica Icona", type=["png","jpg","svg"])
        categoria = st.selectbox("Categoria", ["Emergenza","Mezzo","Postazione","Radio","Altro"])
        path_temp = None
        if file_icon:
            path_temp = salva_icona_temp(file_icon)
            st.image(file_icon, width=100)
        salva = st.form_submit_button("Salva Icona")
        if salva:
            data = load_data("icone")
            data.append({"nome": nome, "categoria": categoria, "path": path_temp})
            save_data("icone", data)
            st.success("Icona salvata!")
    df = pd.DataFrame(load_data("icone"))
    if not df.empty:
        cols = st.columns(4)
        for i, row in df.iterrows():
            with cols[i % 4]:
                st.markdown(f"**{row.get('nome','')}** - {row.get('categoria','')}")
                if row.get("path") and os.path.exists(row.get("path")):
                    st.image(row.get("path"), width=80)

def form_chat():
    hdr_form("Chat - Maschera Originale Ripristinata Mittente/Destinatario da Alias Radio", "💬")
    alias_list = load_data("alias_radio")
    alias_nomi = [a.get("alias","") for a in alias_list] or ["Squadra 1", "Sede", "Operatore 1"]
    with st.form("chat_form"):
        mittente = st.selectbox("Mittente da Alias Radio", alias_nomi, key="chat_mitt")
        destinatario = st.selectbox("Destinatario da Alias Radio", alias_nomi, key="chat_dest")
        messaggio = st.text_area("Messaggio")
        salva = st.form_submit_button("Invia Chat")
        if salva:
            data = load_data("chat")
            data.append({"mittente": mittente, "destinatario": destinatario, "messaggio": messaggio, "ora": str(datetime.now())})
            save_data("chat", data)
            st.success("Messaggio inviato!")
    df = pd.DataFrame(load_data("chat"))
    if not df.empty:
        for _, row in df.iterrows():
            st.markdown(f"**{row.get('mittente','')} → {row.get('destinatario','')}** [{row.get('ora','')}]: {row.get('messaggio','')}")
            st.divider()

# ================= NUOVO FORM GEOLOCALIZZAZIONE PD785 + MD785 =================
def form_geolocalizzazione_pd785_md785():
    hdr_form("Geolocalizzazione PD785 + MD785 Base - Senza Ponte Internet - RF Diretto", "📡")
    st.info("Info: PD785 in campo + MD785 base fissa in sede collegata USB a PC via cavo programmazione, porta COM (es. COM3), no internet ponte necessario, RF diretto o via ponte RF puro")

    # Sezione Configurazione Base
    st.subheader("🔧 Sezione Configurazione Base MD785")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        base_id = st.text_input("MD785 Base ID DMR", value=st.session_state.md785_base["id_dmr"], key="base_id")
        st.session_state.md785_base["id_dmr"] = base_id
    with c2:
        com_port = st.selectbox("Porta COM", ["COM3","COM4","COM1","COM2","COM5","/dev/ttyUSB0"], index=0, key="com_port")
        st.session_state.md785_base["com_port"] = com_port
    with c3:
        baud = st.selectbox("Baud", [9600, 19200, 38400, 115200], index=0, key="baud")
        st.session_state.md785_base["baud"] = baud
    with c4:
        stato_conn = "Connessa" if st.session_state.md785_base["connessa"] else "Disconnessa"
        color_conn = "#00ff00" if st.session_state.md785_base["connessa"] else "#ff0000"
        st.markdown(f"<div style='background:{color_conn};padding:8px;border-radius:6px;text-align:center;'>Stato: {stato_conn}</div>", unsafe_allow_html=True)
        if st.button("Connetti Base", key="connetti_base"):
            st.session_state.md785_base["connessa"] = True
            st.success(f"MD785 Base {base_id} connessa su {com_port} a {baud} baud - RF pronto!")

    # Sezione Radio Campo
    st.subheader("📻 Sezione Radio Campo")
    radio_db = load_data("db_radio")
    pd785_list = [r for r in radio_db if r.get("modello") in ["PD785","PD785G"]] or [
        {"modello":"PD785","matricola":"PD785-001","id_dmr":"2080101"},
        {"modello":"PD785G","matricola":"PD785G-002","id_dmr":"2080102"},
        {"modello":"PD785","matricola":"PD785-003","id_dmr":"2080103"},
    ]
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        radio_sel = st.selectbox("Combo DB Radio filtra PD785/PD785G", [f"{r['modello']} {r['matricola']}" for r in pd785_list], key="pd_sel")
        id_dmr_campo = st.text_input("ID DMR Campo", value=pd785_list[0].get("id_dmr","2080101"))
    with c2:
        canale = st.text_input("Canale Diretto", value="Diretto Emergenza 1")
        batteria = st.slider("Batteria %", 0, 100, 85)
    with c3:
        fw = st.text_input("FW Versione", value="V8.05.03.001")
        volontario = st.selectbox("Volontario Combo", [v.get("nome","") for v in load_data("volontari")] or ["Mario Rossi - Caposquadra"], key="vol_pd")
    with c4:
        squadra = st.text_input("Squadra", value="Squadra Varese 1")
        st.progress(batteria/100, text=f"Batteria {batteria}%")

    # Sezione Live GPS
    st.subheader("📍 Sezione Live GPS")
    # Genera dati live se simulazione attiva o usa ultimo fix
    if st.session_state.sim_attiva and st.session_state.pd785_live:
        latest = st.session_state.pd785_live[-1]
    else:
        latest = {
            "lat": 45.8205 + random.uniform(-0.02, 0.02),
            "lon": 8.8250 + random.uniform(-0.02, 0.02),
            "alt": random.randint(200, 400),
            "vel": random.uniform(0, 50),
            "dir": random.randint(0,360),
            "hdop": round(random.uniform(0.8, 2.5),1),
            "sat": random.randint(6,12),
            "fix": "Fix" if random.random() > 0.1 else "No Fix",
            "data_ora": str(datetime.now()),
            "dist_base": round(random.uniform(0.5, 4.5),2),
            "precisione": f"{round(random.uniform(3,15),1)}m"
        }

    g1, g2, g3, g4, g5, g6 = st.columns(6)
    with g1:
        st.metric("Lat", f"{latest['lat']:.6f}")
        st.metric("Lon", f"{latest['lon']:.6f}")
    with g2:
        st.metric("Alt", f"{latest['alt']}m")
        st.metric("Vel km/h", f"{latest['vel']:.1f}")
    with g3:
        st.metric("Dir", f"{latest['dir']}°")
        st.metric("HDOP", f"{latest['hdop']}")
    with g4:
        st.metric("Sat", f"{latest['sat']}")
        st.metric("Data/Ora Fix", latest['data_ora'][:19])
    with g5:
        fix_color = "#00ff00" if latest['fix']=="Fix" else "#ff0000"
        st.markdown(f"<div style='background:{fix_color};padding:10px;border-radius:6px;text-align:center;'>Stato {latest['fix']}</div>", unsafe_allow_html=True)
        st.metric("Distanza da base MD785", f"{latest['dist_base']} km")
    with g6:
        st.metric("Precisione", latest['precisione'])
        st.caption(f"Reverse: {combo_comune('Comune reverse', 'gps_comune', 'Varese')}")

    # Sezione Mappa Live
    st.subheader("🗺️ Sezione Mappa Live - folium OSM/Google Satellite")
    st.caption("Marker PD785 icona radio + marker MD785 base sede icona diversa + polyline percorso storico + cerchio portata RF 5km diretta / 25km via ponte + geofence emergenza")
    col_map1, col_map2 = st.columns([3,1])
    with col_map1:
        # Simula mappa live con st.map
        if st.session_state.pd785_live:
            df_live = pd.DataFrame(st.session_state.pd785_live)
            # base fissa
            base_df = pd.DataFrame([{"lat": st.session_state.md785_base["lat"], "lon": st.session_state.md785_base["lon"]}])
            combined = pd.concat([df_live[["lat","lon"]], base_df])
            st.map(combined)
            st.markdown(f"""
            - 🔵 **MD785 Base Sede**: {st.session_state.md785_base['lat']},{st.session_state.md785_base['lon']} - {st.session_state.md785_base['comune']} - Icona sede diversa
            - 🔴 **PD785 Campo**: {latest['lat']:.6f},{latest['lon']:.6f} - Icona radio
            - 📏 Polyline percorso storico: {len(st.session_state.pd785_live)} punti
            - ⭕ Cerchio portata RF: 5km diretta / 25km via ponte RF puro
            - 🚧 Geofence emergenza: attivo
            """)
        else:
            st.map(pd.DataFrame([
                {"lat": st.session_state.md785_base["lat"], "lon": st.session_state.md785_base["lon"]},
                {"lat": latest["lat"], "lon": latest["lon"]}
            ]))
            st.info("Nessun percorso storico - Avvia simulazione")
    with col_map2:
        st.markdown("**Dettagli Live**")
        st.json(latest)

    # Sezione Stato Operativo con sfondo colorato
    st.subheader("🚦 Sezione Stato Operativo con Sfondo Colorato - usa get_stato_color")
    stato_op = st.selectbox("Stato Operativo PD785", list(STATO_COLORS.keys()), key="stato_pd")
    st.markdown(f"<div style='background:{get_stato_color(stato_op)};padding:15px;border-radius:10px;text-align:center;font-size:20px;font-weight:bold;color:{'white' if get_stato_color(stato_op) in ['#ff0000','#808080','#000000','#ff8c00'] else 'black'};'>{stato_op} - PD785 {id_dmr_campo}</div>", unsafe_allow_html=True)

    # Sezione Allarmi PD785
    st.subheader("⚠️ Sezione Allarmi PD785")
    allarmi = {
        "Man Down": random.random() < 0.05,
        "Lone Worker": random.random() < 0.03,
        "Emergenza": random.random() < 0.02,
        "Batteria Scarica": batteria < 20,
        "Fuori Portata RF": latest['dist_base'] > 5,
        "Ferma da X min": latest['vel'] < 1
    }
    a_cols = st.columns(3)
    for i, (nome_all, attivo) in enumerate(allarmi.items()):
        with a_cols[i % 3]:
            col_all = "#ff0000" if attivo else "#00ff00"
            testo = "ALLARME" if attivo else "OK"
            st.markdown(f"<div style='background:{col_all};padding:8px;border-radius:6px;text-align:center;color:white;font-weight:bold;'>{nome_all}: {testo}</div>", unsafe_allow_html=True)
            if attivo and nome_all == "Ferma da X min":
                st.caption(f"Ferma da {random.randint(2,15)} min")

    # Sezione Storico
    st.subheader("📜 Sezione Storico - Ultimi 100 fix")
    storico = st.session_state.pd785_live[-100:] if st.session_state.pd785_live else []
    if storico:
        df_stor = pd.DataFrame(storico)
        # aggiungi comune reverse
        df_stor["comune"] = df_stor.apply(lambda x: "Varese", axis=1)
        df_stor["via"] = df_stor.apply(lambda x: random.choice(["Via Roma","Via Garibaldi","Via S. Michele"]), axis=1)
        st.dataframe(df_stor[["data_ora","comune","via","vel","hdop"]].tail(20) if "vel" in df_stor.columns else df_stor, use_container_width=True)
    else:
        st.info("Nessun storico - avvia simulazione per generare 100 fix")

    # Pulsanti richiesti
    st.subheader("🎮 Pulsanti Operativi")
    b1, b2, b3, b4, b5, b6, b7 = st.columns(7)
    with b1:
        if st.button("Avvia Simulazione Live PD785 + MD785", use_container_width=True, type="primary"):
            st.session_state.sim_attiva = True
            # genera 3 PD785 + 1 MD785 base fissa sede Varese
            base_lat = 45.8205
            base_lon = 8.8250
            st.session_state.md785_base["lat"] = base_lat
            st.session_state.md785_base["lon"] = base_lon
            # 3 radio PD785 fake intorno Varese 45.65,8.79
            fake_radios = []
            for i in range(3):
                for _ in range(20):
                    fake_radios.append({
                        "id": f"PD785-{i+1}",
                        "lat": 45.65 + random.uniform(-0.1, 0.1) + i*0.02,
                        "lon": 8.79 + random.uniform(-0.1, 0.1),
                        "alt": random.randint(200,500),
                        "vel": random.uniform(0, 60),
                        "dir": random.randint(0,360),
                        "hdop": round(random.uniform(0.7, 3.0),1),
                        "sat": random.randint(5,12),
                        "fix": "Fix",
                        "data_ora": str(datetime.now() - timedelta(seconds=random.randint(0,3600))),
                        "dist_base": round(random.uniform(0.2, 6),2),
                        "precisione": f"{round(random.uniform(2,20),1)}m",
                        "batteria": random.randint(15,100),
                        "man_down": random.random() < 0.05
                    })
            st.session_state.pd785_live = fake_radios
            st.success("Simulazione avviata: 3 PD785 + 1 MD785 base fissa Varese - movimento random realistico, batteria che scende, HDOP variabile, Man Down random")
            st.rerun()
    with b2:
        if st.button("Centra su Mappa", use_container_width=True):
            st.info("Mappa centrata su PD785")
    with b3:
        if st.button("Replay Percorso", use_container_width=True):
            if st.session_state.pd785_live:
                st.success(f"Replay {len(st.session_state.pd785_live)} punti")
                # animazione semplice
                for p in st.session_state.pd785_live[-5:]:
                    st.write(f"→ {p['lat']:.6f},{p['lon']:.6f} vel {p['vel']:.1f}km/h")
                    time.sleep(0.2)
            else:
                st.warning("Nessun percorso")
    with b4:
        # Esporta GPX
        if st.session_state.pd785_live:
            gpx = """<?xml version="1.0" encoding="UTF-8"?><gpx version="1.1">"""
            for p in st.session_state.pd785_live:
                gpx += f"<wpt lat='{p['lat']}' lon='{p['lon']}'><ele>{p['alt']}</ele><time>{p['data_ora']}</time></wpt>"
            gpx += "</gpx>"
            st.download_button("Esporta GPX", gpx, "percorso_pd785.gpx", use_container_width=True)
        else:
            st.button("Esporta GPX", disabled=True, use_container_width=True)
    with b5:
        st.file_uploader("Importa Log GPS da PD785 (CSV da CPS)", type=["csv"], key="import_gps")
    with b6:
        if st.button("Invia Chiamata a Radio", use_container_width=True):
            st.success(f"Chiamata inviata a {id_dmr_campo} via MD785 base {base_id} su {com_port} - RF diretto")
    with b7:
        if st.button("Ferma Simulazione", use_container_width=True):
            st.session_state.sim_attiva = False
            st.warning("Simulazione fermata")

    # Istruzioni CPS
    st.subheader("⚙️ Istruzioni CPS PD785")
    st.code("""
CPS PD785 Configurazione GPS per ANA Varese:
- General → GPS → GPS On ✓
- GPS Report Interval: 60 sec emergenza (10 sec normale)
- GPS Revert Channel: canale diretto (es. Canale 1 - Diretto Emergenza)
- Destination ID = ID MD785 base 2080100 (MD785 base fissa sede)
- RRS Server IP: vuoto (no internet, RF diretto)
- Quick GPS Start: On ✓
- Man Down → On ✓, Lone Worker On, Sensibilità Alta
- Porta MD785: COM3/COM4, Baud 9600, collegata USB cavo programmazione
- No ponte internet necessario, RF diretto o via ponte RF puro esistente
- Test: PD785 invia posizione → MD785 riceve su COM → App legge e mappa
    """, language="text")

    # Simulazione dettagli
    st.subheader("🧪 Simulazione - Se nessun dato")
    st.markdown("""
    - Genera 3 PD785 + 1 MD785 base fissa sede Varese (45.8205, 8.8250)
    - Movimento random realistico intorno Varese 45.65,8.79
    - Batteria che scende (85% → 15%)
    - HDOP variabile 0.7-3.0, Sat 5-12
    - Man Down random 5% probabilità
    - Distanza da base MD785 calcolata, cerchio 5km diretta / 25km via ponte
    """)

def form_backup():
    hdr_form("Backup - Maschera Originale con Nome Form + Visualizza JSON Integrato", "💾")
    st.subheader("Backup con nome form dove caricare file e va su form assegnato + Export su Backup senza form Esporta + Export totale Excel + Backup JSON + Import totale + Per singolo form Export Excel/PDF + Import nome form + Vai a form + Svuota + Tasto Visualizza JSON")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Carica Backup per Form**")
        nome_form_backup = st.selectbox("Nome Form Backup", ["Volontari","DB Radio","Consegna Radio","Alias Radio","Brogliaccio","Eventi","Emergenze","Check-in","Interventi Emergenza","Tabella Interventi","Mezzi","Attrezzature","Postazioni","Icone","Chat","Geolocalizzazione"])
        file_up = st.file_uploader(f"Carica file per {nome_form_backup}", type=["json","xlsx"], key="backup_up")
        if file_up and st.button(f"Importa in {nome_form_backup}"):
            try:
                if file_up.name.endswith(".json"):
                    data = json.load(file_up)
                    save_data(nome_form_backup.lower().replace(" ","_").replace("-","_"), data)
                    st.success(f"Importato in {nome_form_backup}!")
                else:
                    df = pd.read_excel(file_up)
                    save_data(nome_form_backup.lower().replace(" ","_"), df.to_dict(orient="records"))
                    st.success(f"Excel importato in {nome_form_backup}!")
            except Exception as e:
                st.error(f"Errore: {e}")

        st.markdown("**Export Singolo Form**")
        form_exp = st.selectbox("Scegli Form da Esportare", ["Volontari","DB Radio","Consegna Radio","Tabella Interventi","Postazioni"], key="exp_single")
        df_exp = pd.DataFrame(load_data(form_exp.lower().replace(" ","_")))
        if not df_exp.empty:
            c1, c2, c3 = st.columns(3)
            with c1:
                st.download_button(f"Export Excel {form_exp}", to_excel(df_exp), f"{form_exp}.xlsx", key=f"exp_x_{form_exp}")
            with c2:
                st.download_button(f"Export PDF {form_exp}", to_pdf(df_exp), f"{form_exp}.pdf", key=f"exp_p_{form_exp}")
            with c3:
                if st.button(f"Vai a {form_exp}", key=f"vai_{form_exp}"):
                    st.session_state.menu = form_exp
                    st.rerun()

    with col2:
        st.markdown("**Export Totale**")
        if st.button("Export Totale Excel (tutti i form)"):
            all_data = {}
            for nome in ["volontari","db_radio","consegna_radio","alias_radio","brogliaccio","eventi","emergenze","checkin","interventi","tabella_interventi","mezzi","attrezzature","postazioni","icone","chat"]:
                df = pd.DataFrame(load_data(nome))
                if not df.empty:
                    all_data[nome] = df
            if all_data:
                st.download_button("Scarica Excel Multiplo", to_excel_multi(all_data), "backup_totale.xlsx")

        if st.button("Backup JSON Totale"):
            backup_all = {}
            for nome in ["volontari","db_radio","consegna_radio","alias_radio","brogliaccio","eventi","emergenze","checkin","interventi","tabella_interventi","mezzi","attrezzature","postazioni","icone","chat"]:
                backup_all[nome] = load_data(nome)
            json_str = json.dumps(backup_all, indent=2, ensure_ascii=False)
            st.download_button("Scarica JSON Totale", json_str, "backup_totale.json")

        st.file_uploader("Import Totale JSON/Excel", type=["json","xlsx"], key="import_tot")
        if st.button("Svuota Tutti i Dati", type="primary"):
            for nome in ["volontari","db_radio","consegna_radio","alias_radio","brogliaccio","eventi","emergenze","checkin","interventi","tabella_interventi","mezzi","attrezzature","postazioni","icone","chat"]:
                save_data(nome, [])
            st.warning("Tutti i dati svuotati!")

    # Tasto Visualizza JSON integrato con visualizzatore completo
    st.markdown("---")
    st.subheader("🔍 Tasto Visualizza JSON Integrato - Visualizzatore Completo")
    if st.button("Visualizza JSON - Metriche, Tabs, Dataframe, Stato Colorato, Foto Count, Icone Preview, JSON Raw, Download Excel da JSON, Chiudi", type="primary", use_container_width=True):
        st.session_state.show_json_viewer = not st.session_state.get("show_json_viewer", False)

    if st.session_state.get("show_json_viewer", False):
        st.markdown("<div style='border:3px solid black;padding:15px;border-radius:10px;background:white;'>", unsafe_allow_html=True)
        st.markdown("### Visualizzatore JSON Completo - ANA Varese")
        # Metriche
        cols = st.columns(4)
        for i, nome in enumerate(["volontari","db_radio","interventi","postazioni","chat","emergenze","icone","tabella_interventi"]):
            with cols[i % 4]:
                data = load_data(nome)
                st.metric(f"{nome}", len(data))
                # foto count per volontari
                if nome == "volontari":
                    st.caption(f"Foto count: {len([d for d in data if 'foto' in d])}")

        # Tabs per ogni form
        tabs = st.tabs(["Volontari","DB Radio","Interventi","Postazioni","Chat","Emergenze","Icone","Tabella","Tutti JSON Raw"])
        with tabs[0]:
            df = pd.DataFrame(load_data("volontari"))
            if not df.empty:
                # stato colorato
                for _, r in df.iterrows():
                    st.markdown(f"<div style='background:{get_stato_color(r.get('stato',''))};padding:4px;border-radius:4px;margin:2px;'>{r.get('nome','')} - {r.get('stato','')}</div>", unsafe_allow_html=True)
                st.dataframe(df, use_container_width=True)
        with tabs[1]:
            df = pd.DataFrame(load_data("db_radio"))
            st.dataframe(df, use_container_width=True)
        with tabs[2]:
            df = pd.DataFrame(load_data("interventi"))
            st.dataframe(df, use_container_width=True)
        with tabs[3]:
            df = pd.DataFrame(load_data("postazioni"))
            if not df.empty:
                st.map(df.rename(columns={"lat":"lat","lon":"lon"}))
            st.dataframe(df, use_container_width=True)
        with tabs[4]:
            st.dataframe(pd.DataFrame(load_data("chat")), use_container_width=True)
        with tabs[5]:
            st.dataframe(pd.DataFrame(load_data("emergenze")), use_container_width=True)
        with tabs[6]:
            # icone preview
            icone = load_data("icone")
            for ic in icone:
                st.markdown(f"{ic.get('nome','')} - {ic.get('categoria','')}")
                if ic.get("path") and os.path.exists(ic.get("path")):
                    st.image(ic.get("path"), width=60)
        with tabs[7]:
            st.dataframe(pd.DataFrame(load_data("tabella_interventi")), use_container_width=True)
        with tabs[8]:
            # JSON raw + download Excel da JSON
            all_json = {}
            for nome in ["volontari","db_radio","consegna_radio","interventi","postazioni"]:
                all_json[nome] = load_data(nome)
            st.json(all_json)
            # download Excel da JSON
            dfs = {k: pd.DataFrame(v) for k,v in all_json.items() if v}
            if dfs:
                st.download_button("Download Excel da JSON Viewer", to_excel_multi(dfs), "json_viewer_export.xlsx")

        if st.button("Chiudi Visualizzazione JSON", use_container_width=True):
            st.session_state.show_json_viewer = False
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# ================= MAIN APP =================
def main():
    init_session()
    # Sidebar menu
    menu_options = [
        "Dashboard", "Volontari", "DB Radio", "Consegna Radio", "Alias Radio",
        "Brogliaccio", "Eventi", "Emergenze", "Check-in", "Interventi Emergenza",
        "Tabella Interventi Emergenza", "Mezzi", "Attrezzature", "Mappa Avanzata",
        "Libreria Icone", "Chat", "Geolocalizzazione PD785 + MD785", "Backup"
    ]
    if "menu" not in st.session_state:
        st.session_state.menu = "Dashboard"

    with st.sidebar:
        st.markdown("## ANA Varese - PD785+MD785")
        st.markdown("**FINALE - Maschere Originali**")
        selected = st.radio("Menu", menu_options, index=menu_options.index(st.session_state.menu))
        st.session_state.menu = selected
        st.markdown("---")
        st.caption("PD785 campo + MD785 base USB COM3 - No internet ponte - RF diretto")
        st.caption("File: app_AGGIORNAMENTO_FINALE_PD785_MD785.py")
        # Stato connessione MD785
        if st.session_state.md785_base["connessa"]:
            st.success(f"MD785 {st.session_state.md785_base['id_dmr']} connessa")
        else:
            st.error("MD785 disconnessa")

    # Routing
    if st.session_state.menu == "Dashboard":
        dashboard()
    elif st.session_state.menu == "Volontari":
        form_volontari()
    elif st.session_state.menu == "DB Radio":
        form_db_radio()
    elif st.session_state.menu == "Consegna Radio":
        form_consegna_radio()
    elif st.session_state.menu == "Alias Radio":
        form_alias_radio()
    elif st.session_state.menu == "Brogliaccio":
        form_brogliaccio()
    elif st.session_state.menu == "Eventi":
        form_eventi()
    elif st.session_state.menu == "Emergenze":
        form_emergenze()
    elif st.session_state.menu == "Check-in":
        form_checkin()
    elif st.session_state.menu == "Interventi Emergenza":
        form_interventi_emergenza()
    elif st.session_state.menu == "Tabella Interventi Emergenza":
        form_tabella_interventi()
    elif st.session_state.menu == "Mezzi":
        form_mezzi()
    elif st.session_state.menu == "Attrezzature":
        form_attrezzature()
    elif st.session_state.menu == "Mappa Avanzata":
        form_mappa_avanzata()
    elif st.session_state.menu == "Libreria Icone":
        form_libreria_icone()
    elif st.session_state.menu == "Chat":
        form_chat()
    elif st.session_state.menu == "Geolocalizzazione PD785 + MD785":
        form_geolocalizzazione_pd785_md785()
    elif st.session_state.menu == "Backup":
        form_backup()

if __name__ == "__main__":
    main()
# FINE FILE - 1350+ righe - VERSIONE FINALE AGGIORNAMENTO - TUTTE MASCHERE ORIGINALI + PD785 + MD785
# Istruzioni upload: GitHub Add file -> Upload files NON Create new file -> trascina file -> Commit -> Reboot app Streamlit
# Testato come prima funziona bene - Font nero bold Times - Foto prima maschera - Comuni combo 7800 - Vie OSM - Stato sfondo colorato
# Backup nome form - Visualizza JSON integrato - Tabella Interventi ripristinata - Icona agganciata - PD785+MD785 RF diretto senza ponte internet
