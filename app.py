import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import date, datetime
import os
import json
import uuid

st.set_page_config(page_title="ANA Varese", page_icon="🟢", layout="wide")

st.markdown("""
<style>
.stApp{background-color:#e8f5e9!important;}
.main.block-container{background-color:white!important;border-radius:18px;padding:20px!important;max-width:95%!important;}
[data-testid="stSidebar"]{background-color:#a5d6a7!important;border-right:4px solid #2e7d32!important;}
.stForm{background-color:#c8e6c9!important;border:3px solid #2e7d32!important;border-radius:15px!important;padding:15px!important;}
.stButton>button{background-color:#2e7d32!important;color:white!important;font-weight:bold!important;min-height:50px!important;border-radius:10px!important;}
div[data-testid="stFormSubmitButton"]>button{background-color:#d32f2f!important;color:white!important;}
.quick-btn>button{background:linear-gradient(135deg,#ff9800,#ef6c00)!important;border:2px solid #e65100!important;min-height:90px!important;font-size:18px!important;}
.quick-btn-green>button{background:linear-gradient(135deg,#2e7d32,#1b5e20)!important;min-height:90px!important;font-size:18px!important;}
.quick-btn-red>button{background:linear-gradient(135deg,#c62828,#b71c1c)!important;min-height:90px!important;font-size:18px!important;}
.quick-btn-blue>button{background:linear-gradient(135deg,#1565c0,#0d47a1)!important;min-height:90px!important;font-size:18px!important;}
.quick-btn-purple>button{background:linear-gradient(135deg,#6a1b9a,#4a148c)!important;min-height:90px!important;font-size:18px!important;}
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
    except:
        pass

FILE_DATI = "dati_volontari.json"

if "dati" not in st.session_state:
    st.session_state.dati = load_json(FILE_DATI, [])
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
if "form_assoc" not in st.session_state:
    st.session_state.form_assoc = "ANA Varese"
if "form_ruolo" not in st.session_state:
    st.session_state.form_ruolo = "Volontario"

try:
    c1, c2, c3 = st.columns([1,2,1])
    if os.path.exists("logo.png"):
        c1.image("logo.png", width=90)
    c2.markdown("<h2 style='text-align:center; color:#0e7a3d;'>VOLONTARIATO<br>Sezione di Varese</h2>", unsafe_allow_html=True)
    if os.path.exists("logo_pc_lombardia.png"):
        c3.image("logo_pc_lombardia.png", width=90)
except:
    st.markdown("<h2 style='text-align:center; color:#0e7a3d;'>VOLONTARIATO<br>Sezione di Varese</h2>", unsafe_allow_html=True)

st.divider()

with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=80)
    st.markdown("### MENU ANA VARESE")
    opzioni = ["Dashboard", "Volontari", "Emergenze", "Mappa Postazioni", "DB Radio", "Eventi", "Check-in", "Backup"]
    sel = st.radio("Seleziona pagina", opzioni, index=opzioni.index(st.session_state.menu_scelta) if st.session_state.menu_scelta in opzioni else 0)
    if sel!= st.session_state.menu_scelta:
        st.session_state.menu_scelta = sel
        st.rerun()
    st.divider()
    st.metric("👥 Volontari totali", len(st.session_state.dati))

scelta = st.session_state.menu_scelta

if scelta == "Dashboard":
    st.markdown("## 🏠 DASHBOARD - ANA Varese")
    st.markdown("### ⚡ TASTI MENU VELOCE - Clicca per andare subito alla pagina!")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown('<div class="quick-btn-green">', unsafe_allow_html=True)
        if st.button("👥\nVOLONTARI\nGestisci anagrafica", key="q_vol", use_container_width=True):
            st.session_state.menu_scelta = "Volontari"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="quick-btn-red">', unsafe_allow_html=True)
        if st.button("🚨\nEMERGENZE\nNuovo intervento", key="q_em", use_container_width=True):
            st.session_state.menu_scelta = "Emergenze"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="quick-btn-blue">', unsafe_allow_html=True)
        if st.button("📍\nMAPPA\nPostazioni", key="q_map", use_container_width=True):
            st.session_state.menu_scelta = "Mappa Postazioni"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with c4:
        st.markdown('<div class="quick-btn">', unsafe_allow_html=True)
        if st.button("📻\nRADIO\nDB Radio", key="q_radio", use_container_width=True):
            st.session_state.menu_scelta = "DB Radio"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    c5, c6, c7, c8 = st.columns(4)
    with c5:
        st.markdown('<div class="quick-btn-purple">', unsafe_allow_html=True)
        if st.button("📅\nEVENTI\nCalendario", key="q_eventi", use_container_width=True):
            st.session_state.menu_scelta = "Eventi"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with c6:
        if st.button("✅\nCHECK-IN\nPresenze", key="q_check", use_container_width=True):
            st.session_state.menu_scelta = "Check-in"
            st.rerun()
    with c7:
        if st.button("💾\nBACKUP\nEsporta dati", key="q_backup", use_container_width=True):
            st.session_state.menu_scelta = "Backup"
            st.rerun()
    with c8:
        if st.button("➕\nNUOVO\nVolontario rapido", key="q_new", use_container_width=True):
            st.session_state.menu_scelta = "Volontari"
            st.session_state.volontario_selezionato = None
            st.session_state.form_nome = ""
            st.session_state.form_cognome = ""
            st.session_state.form_cell = ""
            st.rerun()

    st.divider()
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("👥 Volontari Registrati", len(st.session_state.dati))
    with c2:
        st.metric("📅 Data Oggi", date.today().strftime("%d/%m/%Y"))
    with c3:
        st.metric("⏰ Ora", datetime.now().strftime("%H:%M"))
    st.divider()
    st.markdown("### 👥 VOLONTARI - Clicca sul nome per modificare")
    if st.session_state.dati:
        for idx, vol in enumerate(st.session_state.dati):
            c1, c2, c3, c4 = st.columns([3,2,2,2])
            with c1:
                if st.button(f"👤 {vol.get('Nome','')}", key=f"dash_vol_{idx}", use_container_width=True):
                    nome_completo = vol.get('Nome','')
                    parti = nome_completo.split(" ", 1)
                    st.session_state.form_nome = parti[0] if len(parti) > 0 else ""
                    st.session_state.form_cognome = parti[1] if len(parti) > 1 else ""
                    st.session_state.form_cell = vol.get('Cellulare','')
                    st.session_state.form_assoc = vol.get('Associazione','ANA Varese')
                    st.session_state.form_ruolo = vol.get('Ruolo','Volontario')
                    st.session_state.volontario_selezionato = vol
                    st.session_state.volontario_idx = idx
                    st.session_state.menu_scelta = "Volontari"
                    st.rerun()
            with c2:
                st.write(vol.get('Cellulare',''))
            with c3:
                st.write(vol.get('Associazione',''))
            with c4:
                st.write(vol.get('Ruolo',''))
    else:
        st.info("Nessun volontario ancora - Clicca su VOLONTARI per aggiungerne uno!")

elif scelta == "Volontari":
    if st.button("🏠 Torna alla Dashboard", use_container_width=True):
        st.session_state.menu_scelta = "Dashboard"
        st.rerun()
    st.markdown("## 👥 VOLONTARI - Form originale + Sottomaschere")
    if st.session_state.volontario_selezionato is not None:
        vol = st.session_state.volontario_selezionato
        idx = st.session_state.volontario_idx
        st.markdown(f"""
        <div style="background-color:#fff3e0;border:4px solid #ef6c00;border-radius:12px;padding:20px;margin:15px 0;">
        <h3>👤 VOLONTARIO SELEZIONATO: {vol.get('Nome','')}</h3>
        <p><b>{vol.get('Cellulare','')} | {vol.get('Associazione','')} | {vol.get('Ruolo','')}</b><br>
        Cliccato dalla tabella - Dati caricati nel form sotto!</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("❌ Chiudi dettaglio", key="chiudi_det"):
            st.session_state.volontario_selezionato = None
            st.session_state.volontario_idx = None
            st.rerun()
        tab1, tab2, tab3 = st.tabs(["📋 Anagrafica", "📻 Radio", "📄 Note"])
        with tab1:
            st.write(f"**Nome:** {vol.get('Nome','')}")
            st.write(f"**Cellulare:** {vol.get('Cellulare','')}")
            st.write(f"**Associazione:** {vol.get('Associazione','')}")
            st.write(f"**Ruolo:** {vol.get('Ruolo','')}")
            if st.button(f"🗑️ ELIMINA {vol.get('Nome','')}", key="del_vol", use_container_width=True):
                st.session_state.dati.pop(idx)
                save_json(FILE_DATI, st.session_state.dati)
                st.session_state.volontario_selezionato = None
                st.session_state.volontario_idx = None
                st.session_state.form_nome = ""
                st.session_state.form_cognome = ""
                st.session_state.form_cell = ""
                st.rerun()
        with tab2:
            st.info("Radio assegnate - Da implementare")
        with tab3:
            st.info("Note e documenti - Da implementare")
        st.divider()

    st.markdown("### ➕ FORM VOLONTARI - Originale con caricamento da tabella")
    st.info("👉 I campi si riempiono quando clicchi un nome nella tabella sotto!")
    with st.form("form"):
        c1, c2 = st.columns(2)
        with c1:
            nome_input = st.text_input("Nome *", value=st.session_state.form_nome, key="nome_field")
            cognome_input = st.text_input("Cognome *", value=st.session_state.form_cognome, key="cognome_field")
            cell = st.text_input("Cellulare *", value=st.session_state.form_cell, key="cell_field")
        with c2:
            assoc = st.text_input("Associazione *", value=st.session_state.form_assoc, key="assoc_field")
            ruolo = st.selectbox("Ruolo *", ["Volontario", "Caposquadra", "Coordinatore", "Autista", "Radio", "Logistica", "Segreteria", "Sanitario", "Altro"], index=0)
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("✅ Salva", use_container_width=True)
        with col2:
            clear = st.form_submit_button("🆕 Pulisci", use_container_width=True)
        if submitted:
            if nome_input and cognome_input and cell and assoc:
                nome_completo = f"{nome_input} {cognome_input}".strip()
                if st.session_state.volontario_selezionato is not None:
                    idx = st.session_state.volontario_idx
                    st.session_state.dati[idx] = {"Nome": nome_completo, "Associazione": assoc, "Cellulare": cell, "Ruolo": ruolo}
                    save_json(FILE_DATI, st.session_state.dati)
                    st.success(f"✅ Modificato {nome_completo}")
                else:
                    st.session_state.dati.append({"Nome": nome_completo, "Associazione": assoc, "Cellulare": cell, "Ruolo": ruolo})
                    save_json(FILE_DATI, st.session_state.dati)
                    st.success(f"✅ Aggiunto {nome_completo}")
                st.rerun()
            else:
                st.error("Compila i campi *")
        if clear:
            st.session_state.form_nome = ""
            st.session_state.form_cognome = ""
            st.session_state.form_cell = ""
            st.session_state.form_assoc = "ANA Varese"
            st.session_state.form_ruolo = "Volontario"
            st.session_state.volontario_selezionato = None
            st.session_state.volontario_idx = None
            st.rerun()

    st.divider()
    st.markdown("### 👥 TABELLA VOLONTARI - Clicca sul nome per caricare il form + sottomaschere")
    if st.session_state.dati:
        df = pd.DataFrame(st.session_state.dati)
        for idx, vol in enumerate(st.session_state.dati):
            c1, c2, c3, c4 = st.columns([3,2,2,2])
            with c1:
                if st.button(f"👤 {vol.get('Nome','')}", key=f"vol_{idx}", use_container_width=True):
                    nome_completo = vol.get('Nome','')
                    parti = nome_completo.split(" ", 1)
                    st.session_state.form_nome = parti[0] if len(parti) > 0 else ""
                    st.session_state.form_cognome = parti[1] if len(parti) > 1 else ""
                    st.session_state.form_cell = vol.get('Cellulare','')
                    st.session_state.form_assoc = vol.get('Associazione','ANA Varese')
                    st.session_state.form_ruolo = vol.get('Ruolo','Volontario')
                    st.session_state.volontario_selezionato = vol
                    st.session_state.volontario_idx = idx
                    st.rerun()
            with c2:
                st.write(vol.get('Cellulare',''))
            with c3:
                st.write(vol.get('Associazione',''))
            with c4:
                st.write(vol.get('Ruolo',''))
        st.divider()
        st.dataframe(df, use_container_width=True, hide_index=True)
        output = BytesIO()
        df.to_excel(output, index=False, engine="openpyxl")
        st.download_button("📥 Scarica Excel", output.getvalue(), file_name="associazioni.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)

elif scelta == "Emergenze":
    if st.button("🏠 Torna alla Dashboard", use_container_width=True):
        st.session_state.menu_scelta = "Dashboard"
        st.rerun()
    st.markdown("## 🚨 EMERGENZE")
    st.info("Form emergenze - Da implementare")

elif scelta == "Mappa Postazioni":
    if st.button("🏠 Torna alla Dashboard", use_container_width=True):
        st.session_state.menu_scelta = "Dashboard"
        st.rerun()
    st.markdown("## 📍 MAPPA POSTAZIONI")
    st.info("Form mappa postazioni - Come ieri con lat/lon")

elif scelta == "DB Radio":
    if st.button("🏠 Torna alla Dashboard", use_container_width=True):
        st.session_state.menu_scelta = "Dashboard"
        st.rerun()
    st.markdown("## 📻 DB RADIO")

elif scelta == "Eventi":
    if st.button("🏠 Torna alla Dashboard", use_container_width=True):
        st.session_state.menu_scelta = "Dashboard"
        st.rerun()
    st.markdown("## 📅 EVENTI")

elif scelta == "Check-in":
    if st.button("🏠 Torna alla Dashboard", use_container_width=True):
        st.session_state.menu_scelta = "Dashboard"
        st.rerun()
    st.markdown("## ✅ CHECK-IN")

elif scelta == "Backup":
    if st.button("🏠 Torna alla Dashboard", use_container_width=True):
        st.session_state.menu_scelta = "Dashboard"
        st.rerun()
    st.markdown("## 💾 BACKUP UNICO")
    if st.session_state.dati:
        df = pd.DataFrame(st.session_state.dati)
        output = BytesIO()
        df.to_excel(output, index=False, engine="openpyxl")
        st.download_button("📥 Scarica Excel Unico Volontari", output.getvalue(), file_name=f"backup_volontari_{date.today()}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)