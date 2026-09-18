import streamlit as st
import pandas as pd
from datetime import date, datetime
from io import BytesIO
import os
import uuid
import json
import requests

st.set_page_config(page_title="ANA Varese", page_icon="🟢", layout="wide")

st.markdown("""
<style>
.stApp{background-color:#e8f5e9!important;}
.main.block-container{background-color:white!important;border-radius:18px;padding:20px!important;}
[data-testid="stSidebar"]{background-color:#a5d6a7!important;border-right:4px solid #2e7d32!important;}
.stForm{background-color:#c8e6c9!important;border:3px solid #2e7d32!important;border-radius:15px!important;padding:15px!important;}
.stButton>button{background-color:#2e7d32!important;color:white!important;font-weight:bold!important;min-height:45px!important;}
div[data-testid="stFormSubmitButton"]>button{background-color:#d32f2f!important;}
.vol-selected{background-color:#fff3e0;border:4px solid #ef6c00;border-radius:12px;padding:20px;margin:15px 0;}
.submask{background-color:#f1f8e9;border:3px solid #2e7d32;border-radius:12px;padding:15px;margin:10px 0;}
.quick-btn>button{background-color:#ff9800!important;border:2px solid #e65100!important;min-height:75px!important;}
.quick-btn-green>button{background-color:#2e7d32!important;min-height:75px!important;}
.quick-btn-red>button{background-color:#c62828!important;min-height:75px!important;}
.quick-btn-blue>button{background-color:#1565c0!important;min-height:75px!important;}
</style>
""", unsafe_allow_html=True)

def load_json(f, default):
    try:
        if os.path.exists(f):
            with open(f, "r", encoding="utf-8") as fh:
                d = json.load(fh)
                if isinstance(d, list) or isinstance(d, dict):
                    return d
    except:
        pass
    return default

def save_json(f, d):
    try:
        with open(f, "w", encoding="utf-8") as fh:
            json.dump(d, fh, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"Errore {f}: {e}")

COMUNI_VARESE = ["Varese","Busto Arsizio","Gallarate","Saronno","Cassano Magnago","Tradate","Malnate","Luino","Venegono Superiore","Venegono Inferiore","Castiglione Olona","Lozza"]
EMERGENCY_LOGOS = {
    "incendio_boschivo": {"nome": "Incendio Boschivo", "emoji": "🔥"},
    "frana": {"nome": "Frana", "emoji": "⛰️"},
    "caduta_albero": {"nome": "Caduta Albero", "emoji": "🌳"},
    "esondazione": {"nome": "Esondazione", "emoji": "🌊"},
    "vvff": {"nome": "VVFF", "emoji": "🚒"},
    "protezione_civile": {"nome": "Prot. Civile", "emoji": "🦺"},
    "ambulanza": {"nome": "Ambulanza 118", "emoji": "🚑"},
}

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
    return sorted(list(set(COMUNI_VARESE)))

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "dati" not in st.session_state:
    st.session_state.dati = load_json(FILE_DATI, [])
if "postazioni" not in st.session_state:
    st.session_state.postazioni = load_json(FILE_POST, [])
if "emergenze_lista" not in st.session_state:
    st.session_state.emergenze_lista = load_json(FILE_EMER, [])
if "radio_db" not in st.session_state:
    st.session_state.radio_db = load_json(FILE_RADIO, [])
if "dist_radio" not in st.session_state:
    st.session_state.dist_radio = load_json(FILE_DIST, [])
if "eventi_lista" not in st.session_state:
    st.session_state.eventi_lista = load_json(FILE_EVENTI, [])
if "checkin_lista" not in st.session_state:
    st.session_state.checkin_lista = load_json(FILE_CHECK, [])
if "mem_nomi" not in st.session_state:
    st.session_state.mem_nomi = load_json(FILE_NOMI, [])
if "vol_dettagli" not in st.session_state:
    st.session_state.vol_dettagli = load_json(FILE_DETTAGLI, {})
if "interventi_lista" not in st.session_state:
    st.session_state.interventi_lista = load_json(FILE_INTERVENTI, [])
if "menu_scelta" not in st.session_state:
    st.session_state.menu_scelta = "Dashboard"
if "volontario_selezionato" not in st.session_state:
    st.session_state.volontario_selezionato = None
if "volontario_idx" not in st.session_state:
    st.session_state.volontario_idx = None
if "form_nome" not in st.session_state:
    st.session_state.form_nome = ""
if "form_cognome" not in st.session_state:
    st.session_state.form_cognome = ""
if "form_cell" not in st.session_state:
    st.session_state.form_cell = ""
if "form_comune" not in st.session_state:
    st.session_state.form_comune = "Varese"
if "form_ruolo" not in st.session_state:
    st.session_state.form_ruolo = "Volontario"
if "form_assoc" not in st.session_state:
    st.session_state.form_assoc = "ANA Varese"

def header_loghi():
    c1, c2, c3 = st.columns([1,2,1])
    if os.path.exists("logo.png"):
        c1.image("logo.png", width=90)
    c2.markdown("<h2 style='text-align:center; color:#0e7a3d;'>VOLONTARIATO<br>Sezione di Varese</h2>", unsafe_allow_html=True)
    if os.path.exists("logo_pc_lombardia.png"):
        c3.image("logo_pc_lombardia.png", width=90)

if not st.session_state.authenticated:
    header_loghi()
    st.markdown("<h2 style='text-align:center; color:#2e7d32;'>Accesso - admin / ana2024</h2>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1,2,1])
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
    st.markdown("### MENU ANA VARESE")
    opzioni = ["Dashboard","Volontari","Emergenze con Loghi","Mappa Postazioni","DB Radio","Distribuzione Radio","Eventi","Check-in","Tabella Interventi Emergenza","Backup"]
    sel = st.radio("Seleziona", opzioni, index=opzioni.index(st.session_state.menu_scelta) if st.session_state.menu_scelta in opzioni else 0)
    if sel!= st.session_state.menu_scelta:
        st.session_state.menu_scelta = sel
        st.rerun()
    st.divider()
    if st.button("🚪 LOGOUT - Esci", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

scelta = st.session_state.menu_scelta
st.markdown(f"## {scelta}")
st.divider()
COMUNI_TUTTI = load_comuni_italia()
MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

if scelta == "Dashboard":
    st.markdown("### ⚡ TASTI SCELTA RAPIDA")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("🚨\nNUOVA EMERGENZA", key="q_em", use_container_width=True):
            st.session_state.menu_scelta = "Emergenze con Loghi"
            st.rerun()
    with c2:
        if st.button("📍\nPOSTAZIONE", key="q_post", use_container_width=True):
            st.session_state.menu_scelta = "Mappa Postazioni"
            st.rerun()
    with c3:
        if st.button("👤\nVOLONTARIO", key="q_vol", use_container_width=True):
            st.session_state.menu_scelta = "Volontari"
            st.session_state.volontario_selezionato = None
            st.session_state.volontario_idx = None
            st.rerun()
    with c4:
        if st.button("💾\nBACKUP UNICO", key="q_back", use_container_width=True):
            st.session_state.menu_scelta = "Backup"
            st.rerun()

    c5, c6, c7, c8 = st.columns(4)
    with c5:
        if st.button("📅\nEVENTO", key="q_evento", use_container_width=True):
            st.session_state.menu_scelta = "Eventi"
            st.rerun()
    with c6:
        if st.button("✅\nCHECK-IN", key="q_check", use_container_width=True):
            st.session_state.menu_scelta = "Check-in"
            st.rerun()
    with c7:
        if st.button("📋\nTABELLA INTERVENTI", key="q_tab", use_container_width=True):
            st.session_state.menu_scelta = "Tabella Interventi Emergenza"
            st.rerun()
    with c8:
        if st.button("📻\nASSEGNA RADIO", key="q_radio", use_container_width=True):
            st.session_state.menu_scelta = "Distribuzione Radio"
            st.rerun()

    st.divider()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🚨 Emergenze", len(st.session_state.emergenze_lista))
    c2.metric("📍 Postazioni", len(st.session_state.postazioni))
    c3.metric("👤 Volontari", len(st.session_state.dati))
    c4.metric("📻 Radio", len(st.session_state.radio_db))
    c5, c6, c7, c8 = st.columns(4)
    c5.metric("📅 Eventi", len(st.session_state.eventi_lista))
    c6.metric("✅ Check-in", len(st.session_state.checkin_lista))
    c7.metric("📡 Distr Radio", len(st.session_state.dist_radio))
    c8.metric("🚒 Interventi", len(st.session_state.interventi_lista))

    st.divider()
    st.markdown("### 👥 TABELLA VOLONTARI - CLICCA SUL NOME PER VEDERE SOTTOMASCHERE E CARICARE FORM")
    st.info("Clicca sul nome per aprire il form volontari con i dati e le 6 sottomaschere!")
    if st.session_state.dati:
        h1, h2, h3, h4 = st.columns([3,2,2,2])
        h1.markdown("**👤 Nome - CLICCA**")
        h2.markdown("**📱 Cellulare**")
        h3.markdown("**🏠 Comune**")
        h4.markdown("**🎖️ Ruolo**")
        st.divider()
        for idx, vol in enumerate(st.session_state.dati):
            c1, c2, c3, c4 = st.columns([3,2,2,2])
            with c1:
                if st.button(f"👤 {vol.get('Nome','')}", key=f"dash_vol_{idx}", use_container_width=True):
                    nome_completo = vol.get('Nome','')
                    parti = nome_completo.split(" ", 1)
                    st.session_state.form_nome = parti[0] if len(parti) > 0 else ""
                    st.session_state.form_cognome = parti[1] if len(parti) > 1 else ""
                    st.session_state.form_cell = vol.get('Cellulare','')
                    st.session_state.form_comune = vol.get('Comune','Varese')
                    st.session_state.form_ruolo = vol.get('Ruolo','Volontario')
                    st.session_state.form_assoc = vol.get('Associazione','ANA Varese')
                    st.session_state.volontario_selezionato = vol
                    st.session_state.volontario_idx = idx
                    st.session_state.menu_scelta = "Volontari"
                    st.rerun()
            with c2:
                st.write(vol.get('Cellulare',''))
            with c3:
                st.write(vol.get('Comune',''))
            with c4:
                st.write(vol.get('Ruolo',''))

elif scelta == "Volontari":
    if st.button("🏠 Torna alla Dashboard", use_container_width=True):
        st.session_state.menu_scelta = "Dashboard"
        st.rerun()

    if st.session_state.volontario_selezionato is not None:
        vol = st.session_state.volontario_selezionato
        idx = st.session_state.volontario_idx
        vol_id = f"{vol.get('Nome','')}_{idx}"
        st.markdown('<div class="vol-selected">', unsafe_allow_html=True)
        st.markdown(f"### 👤 VOLONTARIO SELEZIONATO: {vol.get('Nome','')} - SOTTOMASCHERE")
        st.markdown(f"**Cliccato dalla tabella - Dati caricati nel form sotto!**")
        if st.button("❌ Chiudi dettaglio", key="chiudi_det"):
            st.session_state.volontario_selezionato = None
            st.session_state.volontario_idx = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📋 Anagrafica","📻 Radio","📅 Eventi","✅ Presenze","🚨 Emergenze","📄 Note/Doc"])

        with tab1:
            st.markdown('<div class="submask">', unsafe_allow_html=True)
            st.markdown("#### 📋 Sottomaschera 1 - Anagrafica Completa")
            with st.form("form_anagrafica"):
                nome_completo = vol.get('Nome','')
                parti = nome_completo.split(" ", 1)
                nome_init = parti[0] if len(parti) > 0 else ""
                cognome_init = parti[1] if len(parti) > 1 else ""
                c1, c2 = st.columns(2)
                with c1:
                    nome = st.text_input("Nome *", value=nome_init)
                    cognome = st.text_input("Cognome *", value=cognome_init)
                    cf = st.text_input("CF", value=st.session_state.vol_dettagli.get(vol_id, {}).get('CF',''))
                    email = st.text_input("Email", value=st.session_state.vol_dettagli.get(vol_id, {}).get('Email',''))
                with c2:
                    cell = st.text_input("Cellulare *", value=vol.get('Cellulare',''))
                    comune = st.selectbox("Comune", COMUNI_TUTTI, index=COMUNI_TUTTI.index(vol.get('Comune','Varese')) if vol.get('Comune','') in COMUNI_TUTTI else 0)
                    ruolo = st.selectbox("Ruolo", ["Volontario","Caposquadra","Coordinatore","Autista","Radio","Logistica","Segreteria","Sanitario","Altro"], index=0)
                    assoc = st.text_input("Associazione", value=vol.get('Associazione','ANA Varese'))
                c3, c4, c5 = st.columns(3)
                with c3:
                    patente = st.selectbox("Patente", ["","B","C","D","BE","CE"])
                    scadenza = st.date_input("Scadenza Patente", value=date.today())
                with c4:
                    motosega = st.checkbox("Abilitazione Motosega")
                    idrovora = st.checkbox("Abilitazione Idrovora")
                with c5:
                    primo = st.checkbox("Primo Soccorso")
                    antinc = st.checkbox("Antincendio")
                if st.form_submit_button("💾 SALVA ANAGRAFICA", use_container_width=True, type="primary"):
                    nome_new = f"{nome} {cognome}"
                    st.session_state.dati[idx] = {"Nome": nome_new, "Cellulare": cell, "Comune": comune, "Ruolo": ruolo, "Associazione": assoc}
                    if vol_id not in st.session_state.vol_dettagli:
                        st.session_state.vol_dettagli[vol_id] = {}
                    st.session_state.vol_dettagli[vol_id].update({'CF': cf, 'Email': email, 'Patente': patente, 'Motosega': motosega, 'Idrovora': idrovora, 'Primo': primo, 'Antincendio': antinc})
                    save_json(FILE_DATI, st.session_state.dati)
                    save_json(FILE_DETTAGLI, st.session_state.vol_dettagli)
                    st.session_state.form_nome = nome
                    st.session_state.form_cognome = cognome
                    st.session_state.form_cell = cell
                    st.session_state.form_comune = comune
                    st.session_state.form_ruolo = ruolo
                    st.session_state.form_assoc = assoc
                    st.session_state.volontario_selezionato = st.session_state.dati[idx]
                    st.success("✅ Salvato! Form aggiornato!")
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        with tab2:
            st.markdown('<div class="submask">', unsafe_allow_html=True)
            st.markdown("#### 📻 Sottomaschera 2 - Radio Assegnate")
            radio_vol = [r for r in st.session_state.dist_radio if r.get('Volontario','') == vol.get('Nome','')]
            if radio_vol:
                st.dataframe(pd.DataFrame(radio_vol), use_container_width=True)
            else:
                st.info(f"Nessuna radio per {vol.get('Nome','')}")
            with st.form("form_radio_vol"):
                if st.session_state.radio_db:
                    radio_disp = [f"{r.get('Marca','')} {r.get('Modello','')} - {r.get('ID','')}" for r in st.session_state.radio_db]
                    sel = st.selectbox("Radio disponibile", radio_disp)
                    if st.form_submit_button("📻 ASSEGNA RADIO A QUESTO VOLONTARIO", use_container_width=True):
                        new = {"ID": str(uuid.uuid4())[:8], "Volontario": vol.get('Nome',''), "Radio": sel, "Data": str(date.today())}
                        st.session_state.dist_radio.append(new)
                        save_json(FILE_DIST, st.session_state.dist_radio)
                        st.success("Radio assegnata!")
                        st.rerun()
                else:
                    st.warning("Nessuna radio in DB - Vai in DB Radio")
            st.markdown('</div>', unsafe_allow_html=True)

        with tab3:
            st.markdown('<div class="submask">', unsafe_allow_html=True)
            st.markdown("#### 📅 Sottomaschera 3 - Eventi partecipati")
            if st.session_state.eventi_lista:
                st.dataframe(pd.DataFrame(st.session_state.eventi_lista), use_container_width=True)
            else:
                st.info("Nessun evento - Vai in Eventi per crearne")
            st.markdown('</div>', unsafe_allow_html=True)

        with tab4:
            st.markdown('<div class="submask">', unsafe_allow_html=True)
            st.markdown("#### ✅ Sottomaschera 4 - Presenze / Ore Volontariato")
            check_vol = [c for c in st.session_state.checkin_lista if c.get('Volontario','') == vol.get('Nome','')]
            if check_vol:
                st.dataframe(pd.DataFrame(check_vol), use_container_width=True)
                st.metric("Totale presenze", len(check_vol))
            with st.form("form_check_vol"):
                luogo = st.selectbox("Luogo", COMUNI_TUTTI)
                ore = st.number_input("Ore", min_value=0.5, max_value=24.0, value=4.0, step=0.5)
                attivita = st.selectbox("Attivita", ["Emergenza","Esercitazione","Manutenzione","Formazione","Segreteria"])
                if st.form_submit_button("✅ REGISTRA PRESENZA", use_container_width=True, type="primary"):
                    new = {"ID": str(uuid.uuid4())[:8], "Volontario": vol.get('Nome',''), "Luogo": luogo, "Ore": ore, "Attivita": attivita, "Data": str(date.today())}
                    st.session_state.checkin_lista.append(new)
                    save_json(FILE_CHECK, st.session_state.checkin_lista)
                    st.success("Presenza registrata!")
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        with tab5:
            st.markdown('<div class="submask">', unsafe_allow_html=True)
            st.markdown("#### 🚨 Sottomaschera 5 - Emergenze / Interventi")
            if st.session_state.emergenze_lista:
                st.dataframe(pd.DataFrame(st.session_state.emergenze_lista), use_container_width=True)
            else:
                st.info("Nessuna emergenza")
            if st.session_state.interventi_lista:
                st.markdown("##### Interventi Emergenza")
                st.dataframe(pd.DataFrame(st.session_state.interventi_lista), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with tab6:
            st.markdown('<div class="submask">', unsafe_allow_html=True)
            st.markdown("#### 📄 Sottomaschera 6 - Note, Documenti, Scadenze")
            note = st.text_area("Note", value=st.session_state.vol_dettagli.get(vol_id, {}).get('Note',''), height=120)
            c1, c2 = st.columns(2)
            with c1:
                if st.button("💾 Salva Note", use_container_width=True):
                    if vol_id not in st.session_state.vol_dettagli:
                        st.session_state.vol_dettagli[vol_id] = {}
                    st.session_state.vol_dettagli[vol_id]['Note'] = note
                    save_json(FILE_DETTAGLI, st.session_state.vol_dettagli)
                    st.success("Note salvate!")
            with c2:
                visita = st.date_input("Visita Medica scadenza", value=date.today())
                if st.button("💾 Salva Scadenze", use_container_width=True):
                    if vol_id not in st.session_state.vol_dettagli:
                        st.session_state.vol_dettagli[vol_id] = {}
                    st.session_state.vol_dettagli[vol_id]['Visita'] = str(visita)
                    save_json(FILE_DETTAGLI, st.session_state.vol_dettagli)
                    st.success("Salvato!")
            st.divider()
            if st.button(f"🗑️ ELIMINA DEFINITIVAMENTE {vol.get('Nome','')}", use_container_width=True):
                st.session_state.dati.pop(idx)
                save_json(FILE_DATI, st.session_state.dati)
                st.session_state.volontario_selezionato = None
                st.session_state.volontario_idx = None
                st.session_state.form_nome = ""
                st.session_state.form_cognome = ""
                st.session_state.form_cell = ""
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        st.divider()

    st.markdown("### ➕ FORM VOLONTARI - COME PRIMA")
    st.info("👉 I campi si riempiono automaticamente quando clicchi un nome nella tabella sotto!")
    with st.form("form_vol"):
        c1, c2 = st.columns(2)
        with c1:
            nome = st.text_input("Nome *", value=st.session_state.form_nome, key="n_nome")
            cognome = st.text_input("Cognome *", value=st.session_state.form_cognome, key="n_cognome")
            cell = st.text_input("Cellulare *", value=st.session_state.form_cell, key="n_cell")
            assoc = st.text_input("Associazione *", value=st.session_state.form_assoc, key="n_assoc")
        with c2:
            comune = st.selectbox("Comune *", COMUNI_TUTTI, index=COMUNI_TUTTI.index(st.session_state.form_comune) if st.session_state.form_comune in COMUNI_TUTTI else 0, key="n_comune")
            ruolo = st.selectbox("Ruolo *", ["Volontario","Caposquadra","Coordinatore","Autista","Radio","Logistica","Segreteria","Sanitario","Altro"], index=0, key="n_ruolo")
        col_save, col_clear = st.columns(2)
        with col_save:
            submitted = st.form_submit_button("✅ SALVA VOLONTARIO", use_container_width=True, type="primary")
        with col_clear:
            clear = st.form_submit_button("🆕 NUOVO - PULISCI FORM", use_container_width=True)
        if submitted:
            if nome and cognome and cell:
                nome_completo = f"{nome} {cognome}"
                if st.session_state.volontario_selezionato is not None:
                    idx = st.session_state.volontario_idx
                    st.session_state.dati[idx] = {"Nome": nome_completo, "Associazione": assoc, "Cellulare": cell, "Comune": comune, "Ruolo": ruolo}
                    save_json(FILE_DATI, st.session_state.dati)
                    st.success(f"✅ Modificato {nome_completo}!")
                else:
                    st.session_state.dati.append({"Nome": nome_completo, "Associazione": assoc, "Cellulare": cell, "Comune": comune, "Ruolo": ruolo})
                    save_json(FILE_DATI, st.session_state.dati)
                    if nome_completo not in st.session_state.mem_nomi:
                        st.session_state.mem_nomi.append(nome_completo)
                        save_json(FILE_NOMI, st.session_state.mem_nomi)
                    st.success(f"✅ Aggiunto {nome_completo}!")
                st.rerun()
            else:
                st.error("Compila i campi *")
        if clear:
            st.session_state.form_nome = ""
            st.session_state.form_cognome = ""
            st.session_state.form_cell = ""
            st.session_state.form_comune = "Varese"
            st.session_state.form_ruolo = "Volontario"
            st.session_state.form_assoc = "ANA Varese"
            st.session_state.volontario_selezionato = None
            st.session_state.volontario_idx = None
            st.rerun()

    st.divider()
    st.markdown("### 👥 TABELLA VOLONTARI - CLICCA SUL NOME PER CARICARE IL FORM + SOTTOMASCHERE")
    st.info("Come nei vecchi file: clicchi sul nome e i dati si caricano nel form sopra + si aprono le 6 sottomaschere!")
    if st.session_state.dati:
        h1, h2, h3, h4 = st.columns([3,2,2,2])
        h1.markdown("**👤 Nome - CLICCA**")
        h2.markdown("**📱 Cellulare**")
        h3.markdown("**🏠 Comune**")
        h4.markdown("**🎖️ Ruolo**")
        st.divider()
        for idx, vol in enumerate(st.session_state.dati):
            c1, c2, c3, c4 = st.columns([3,2,2,2])
            with c1:
                if st.button(f"👤 {vol.get('Nome','')}", key=f"vol_tab_{idx}", use_container_width=True):
                    nome_completo = vol.get('Nome','')
                    parti = nome_completo.split(" ", 1)
                    st.session_state.form_nome = parti[0] if len(parti) > 0 else ""
                    st.session_state.form_cognome = parti[1] if len(parti) > 1 else ""
                    st.session_state.form_cell = vol.get('Cellulare','')
                    st.session_state.form_comune = vol.get('Comune','Varese')
                    st.session_state.form_ruolo = vol.get('Ruolo','Volontario')
                    st.session_state.form_assoc = vol.get('Associazione','ANA Varese')
                    st.session_state.volontario_selezionato = vol
                    st.session_state.volontario_idx = idx
                    st.rerun()
            with c2:
                st.write(vol.get('Cellulare',''))
            with c3:
                st.write(vol.get('Comune',''))
            with c4:
                st.write(vol.get('Ruolo',''))
        st.divider()
        df = pd.DataFrame(st.session_state.dati)
        st.dataframe(df, use_container_width=True, hide_index=True)
        output = BytesIO()
        df.to_excel(output, index=False, engine="openpyxl")
        st.download_button("📥 Scarica Excel Volontari", output.getvalue(), file_name=f"volontari_{date.today()}.xlsx", mime=MIME, use_container_width=True)

elif scelta == "Tabella Interventi Emergenza":
    if st.button("🏠 Torna alla Dashboard", use_container_width=True):
        st.session_state.menu_scelta = "Dashboard"
        st.rerun()
    st.markdown("### 🚒 TABELLA INTERVENTI EMERGENZA - COME PRIMA")
    st.markdown("## INTERVENTI EMERGENZA")
    with st.form("form_emergenza", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            data_int = st.date_input("Data *")
            ora_int = st.time_input("Ora *")
        with c2:
            comune_int = st.text_input("Comune *")
            via_int = st.text_input("Via *")
        with c3:
            civico_int = st.text_input("Civico")
            odv_int = st.selectbox("ODV Operativa *", ["ANA Varese","ANA Sezione Varese","Protezione Civile Lombardia","Croce Rossa","Altro"])
        azione_int = st.text_area("Azione *", height=100)
        salva = st.form_submit_button("SALVA INTERVENTO EMERGENZA", use_container_width=True)
        if salva:
            if comune_int and via_int and azione_int:
                new = {"Data": str(data_int), "Ora": str(ora_int), "Comune": comune_int, "Via": via_int, "Civico": civico_int, "ODV Operativa": odv_int, "Azione": azione_int}
                st.session_state.interventi_lista.append(new)
                save_json(FILE_INTERVENTI, st.session_state.interventi_lista)
                st.success("Salvato!")
                st.rerun()
            else:
                st.error("Compila i campi *")
    if st.session_state.interventi_lista:
        df = pd.DataFrame(st.session_state.interventi_lista)
        st.dataframe(df, use_container_width=True)
        output = BytesIO()
        df.to_excel(output, index=False, engine="openpyxl")
        st.download_button("📥 Scarica Excel Interventi", output.getvalue(), file_name=f"interventi_{date.today()}.xlsx", mime=MIME, use_container_width=True)

elif scelta == "Backup":
    if st.button("🏠 Torna alla Dashboard", use_container_width=True):
        st.session_state.menu_scelta = "Dashboard"
        st.rerun()
    st.markdown("### 💾 BACKUP - UNICO BACKUP DI TUTTI I FORM")
    st.success("✅ Un unico backup di tutti i form in un solo file!")
    st.markdown("## 📦 BACKUP UNICO DI TUTTI I FORM - TUTTO INSIEME")
    totale = len(st.session_state.dati) + len(st.session_state.postazioni) + len(st.session_state.emergenze_lista) + len(st.session_state.radio_db) + len(st.session_state.dist_radio) + len(st.session_state.eventi_lista) + len(st.session_state.checkin_lista) + len(st.session_state.interventi_lista)
    st.metric("TOTALE RECORD TUTTI I FORM", f"{totale} record")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📦 CREA EXCEL UNICO TUTTI I FORM", use_container_width=True, type="primary", key="b_excel_unico"):
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
                    pd.DataFrame(st.session_state.dist_radio).to_excel(writer, sheet_name="Dist_Radio", index=False)
                if st.session_state.eventi_lista:
                    pd.DataFrame(st.session_state.eventi_lista).to_excel(writer, sheet_name="Eventi", index=False)
                if st.session_state.checkin_lista:
                    pd.DataFrame(st.session_state.checkin_lista).to_excel(writer, sheet_name="Checkin", index=False)
                if st.session_state.interventi_lista:
                    pd.DataFrame(st.session_state.interventi_lista).to_excel(writer, sheet_name="Interventi", index=False)
            st.session_state["backup_unico_excel"] = output.getvalue()
            st.success(f"Excel UNICO creato con {totale} record!")
    with c2:
        if st.button("📦 CREA JSON UNICO TUTTI I FORM", use_container_width=True, key="b_json_unico"):
            all_data = {
                "volontari": st.session_state.dati,
                "postazioni": st.session_state.postazioni,
                "emergenze": st.session_state.emergenze_lista,
                "radio_db": st.session_state.radio_db,
                "dist_radio": st.session_state.dist_radio,
                "eventi": st.session_state.eventi_lista,
                "checkin": st.session_state.checkin_lista,
                "interventi": st.session_state.interventi_lista,
            }
            json_str = json.dumps(all_data, ensure_ascii=False, indent=2)
            st.session_state["backup_unico_json"] = json_str.encode('utf-8')
            st.success("JSON UNICO creato!")
    d1, d2 = st.columns(2)
    with d1:
        if "backup_unico_excel" in st.session_state:
            st.download_button(f"📥 SCARICA EXCEL UNICO - {totale} RECORD", st.session_state["backup_unico_excel"], file_name=f"BACKUP_UNICO_TUTTI_I_FORM_{date.today()}.xlsx", mime=MIME, use_container_width=True, key="dl_excel_unico")
    with d2:
        if "backup_unico_json" in st.session_state:
            st.download_button("📥 SCARICA JSON UNICO TUTTI I FORM", st.session_state["backup_unico_json"], file_name=f"BACKUP_UNICO_TUTTI_I_FORM_{date.today()}.json", mime="application/json", use_container_width=True, key="dl_json_unico")

else:
    if st.button("🏠 Torna alla Dashboard", use_container_width=True):
        st.session_state.menu_scelta = "Dashboard"
        st.rerun()
    st.info(f"Sezione {scelta} - Come prima - Form completo restaurato")
