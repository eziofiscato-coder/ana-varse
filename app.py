
import streamlit as st
import pandas as pd
import os
from io import BytesIO
from datetime import datetime
import json
import requests

st.set_page_config(page_title="ANA Varese - Gestionale", page_icon="🎖️", layout="wide")

# --- Presentazione ---
if "entered" not in st.session_state:
    st.session_state.entered = False
if "current_page" not in st.session_state:
    st.session_state.current_page = "🏠 Dashboard"

if not st.session_state.entered:
    st.markdown("""
    <style>
    [data-testid="stSidebar"] {display: none;}
    .main .block-container {max-width: 900px; padding-top: 2rem;}
    </style>
    """, unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        try:
            st.image("logo.png", width=220)
        except:
            st.markdown("## 🎖️ ANA Varese")
    st.markdown("""
    <div style="text-align:center; padding:20px;">
        <h1 style="color:#0e7a3d; font-size:42px; margin-bottom:0;">🎖️ ANA - ASSOCIAZIONE NAZIONALE ALPINI</h1>
        <h2 style="color:#333; font-size:28px; margin-top:5px;">Sezione di Varese</h2>
        <h3 style="color:#666; font-size:20px; margin-top:20px;">Sistema Gestione Volontari, Radio e Postazioni</h3>
        <div style="background:#e8f5e9; padding:20px; border-radius:15px; margin:30px 0; border-left:6px solid #0e7a3d; text-align:left;">
            <p style="font-size:16px; color:#333; margin:0;">
            ✅ <b>Dashboard</b> - Riepilogo generale<br>
            👥 <b>Volontari</b> - Anagrafica completa<br>
            📻 <b>DB Radio</b> - Inventario radio<br>
            📦 <b>Distribuzione</b> - Consegna radio con firma<br>
            🗺️ <b>Mappa</b> - Postazioni FULLSCREEN OSM/Google + Navigazione<br>
            📋 <b>Registro</b> - Registro uso radio<br>
            🔗 <b>Link</b> - Condivisione aggiornamenti con QR Code
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    col_a, col_b, col_c = st.columns([1,1,1])
    with col_b:
        if st.button("🚀 ENTRA NEL SISTEMA", use_container_width=True, type="primary"):
            st.session_state.entered = True
            st.rerun()
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align:center; background:#f8f9fa; padding:15px; border-radius:10px; margin-top:30px;">
        <p style="font-size:14px; color:#888; margin:0;">Realizzato con ❤️ per la Sezione ANA Varese</p>
        <p style="font-size:20px; color:#0e7a3d; font-weight:bold; margin:5px 0;">👨‍💻 Realizzato da Ezio Fiscato</p>
        <p style="font-size:12px; color:#aaa; margin:0;">Versione 2025 - Gestionale Volontariato</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# --- Funzioni comuni ---
def combo_memoria(label, opzioni, key_suffix, placeholder=""):
    if not opzioni:
        opzioni = ["Volontario"]
    sel = st.selectbox(label, opzioni + ["-- Nuovo --"], key=f"combo_{key_suffix}")
    if sel == "-- Nuovo --":
        nuovo = st.text_input(f"Nuovo {label}", placeholder=placeholder, key=f"nuovo_{key_suffix}")
        return nuovo if nuovo else ""
    return sel

# Files
FILE_NOMI = "mem_nomi.csv"
FILE_RADIO_DB = "radio_db.csv"
FILE_DIST_RADIO = "distribuzione_radio.csv"
FILE_POSTAZIONI = "postazioni_mappa.csv"
FILE_REGISTRO = "registro_radio.csv"

for f_name, key in [(FILE_NOMI, "mem_nomi"), (FILE_RADIO_DB, "radio_db"), (FILE_DIST_RADIO, "dist_radio"), (FILE_POSTAZIONI, "postazioni"), (FILE_REGISTRO, "registro_radio")]:
    if key not in st.session_state:
        if os.path.exists(f_name):
            try:
                df_tmp = pd.read_csv(f_name)
                st.session_state[key] = df_tmp.to_dict(orient="records") if not df_tmp.empty else []
            except:
                st.session_state[key] = []
        else:
            st.session_state[key] = []

if "selected_postazione" not in st.session_state:
    st.session_state.selected_postazione = None
if "mem_nomi" not in st.session_state or not st.session_state.mem_nomi:
    st.session_state.mem_nomi = ["Mario Rossi", "Luigi Bianchi", "Giuseppe Verdi"]

def salva_csv(data, filename):
    if data:
        pd.DataFrame(data).to_csv(filename, index=False)


import requests

def geocode_comune_via(comune, via):
    """Cerca lat/lon da comune e via usando OSM Nominatim"""
    try:
        query = f"{via}, {comune}, Italy" if via and comune else f"{comune}, Italy" if comune else via
        if not query or query.strip() == ", Italy" or query.strip() == "":
            return None, None, "Inserisci comune e via"
        url = "https://nominatim.openstreetmap.org/search"
        params = {"q": query, "format": "json", "limit": 1, "countrycodes": "it", "addressdetails": 1}
        headers = {"User-Agent": "ANA-Varese-App/1.0 (eziofiscato@example.com)"}
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data:
            lat = data[0].get("lat")
            lon = data[0].get("lon")
            display = data[0].get("display_name", "")
            return lat, lon, display
        else:
            return None, None, "Nessun risultato trovato"
    except Exception as e:
        return None, None, f"Errore rete: {str(e)}"


def calc_h(text, max_w=35):
    if not text:
        return 8
    t = str(text)
    lines = 1
    for part in t.split("\n"):
        lines += len(part) // max_w
    return min(max(lines * 5, 8), 30)

# --- MENU MULTIPAGINA ---
st.sidebar.image("logo.png", width=120) if os.path.exists("logo.png") else st.sidebar.markdown("### 🎖️ ANA Varese")
st.sidebar.markdown("## 📚 MENU PRINCIPALE")

pagine = {
    "🏠 Dashboard": "Dashboard",
    "👥 Volontari": "Volontari",
    "📻 DB Radio Inventario": "DB Radio",
    "📦 Distribuzione Radio": "Distribuzione",
    "🗺️ Mappa Postazioni": "Mappa",
    "📋 Registro Radio": "Registro",
    "🔗 Link & Aggiornamenti": "Link"
}

scelta = st.sidebar.radio("Vai a:", list(pagine.keys()), index=list(pagine.keys()).index(st.session_state.current_page) if st.session_state.current_page in pagine else 0, key="menu_radio")

st.session_state.current_page = scelta

if st.sidebar.button("🏠 Torna a Presentazione", use_container_width=True):
    st.session_state.entered = False
    st.rerun()

st.sidebar.divider()
st.sidebar.caption(f"👤 Realizzato da Ezio Fiscato")
st.sidebar.caption(f"📅 {datetime.now().strftime('%d/%m/%Y')}")

# Titolo pagina
st.markdown(f"## {scelta}")
st.divider()


# === DASHBOARD ===
if scelta == "🏠 Dashboard":
    col1,col2,col3,col4 = st.columns(4)
    with col1:
        st.metric("👥 Volontari", len(st.session_state.mem_nomi))
    with col2:
        st.metric("📻 Radio in DB", len(st.session_state.radio_db))
    with col3:
        st.metric("📦 Distribuzioni", len(st.session_state.dist_radio))
    with col4:
        st.metric("🗺️ Postazioni", len(st.session_state.postazioni))
    
    st.markdown("### 🚀 Accesso Rapido")
    c1,c2,c3 = st.columns(3)
    with c1:
        if st.button("👥 Gestisci Volontari", use_container_width=True):
            st.session_state.current_page = "👥 Volontari"
            st.rerun()
        if st.button("📻 DB Radio", use_container_width=True):
            st.session_state.current_page = "📻 DB Radio Inventario"
            st.rerun()
    with c2:
        if st.button("📦 Distribuisci Radio", use_container_width=True):
            st.session_state.current_page = "📦 Distribuzione Radio"
            st.rerun()
        if st.button("🗺️ Vai alla Mappa", use_container_width=True):
            st.session_state.current_page = "🗺️ Mappa Postazioni"
            st.rerun()
    with c3:
        if st.button("📋 Registro Radio", use_container_width=True):
            st.session_state.current_page = "📋 Registro Radio"
            st.rerun()
        if st.button("🔗 Link Aggiornamenti", use_container_width=True):
            st.session_state.current_page = "🔗 Link & Aggiornamenti"
            st.rerun()
    
    if st.session_state.dist_radio:
        st.markdown("### 📦 Ultime Distribuzioni")
        st.dataframe(pd.DataFrame(st.session_state.dist_radio).tail(5).iloc[::-1], use_container_width=True, hide_index=True)

# === VOLONTARI ===
elif scelta == "👥 Volontari":
    with st.container(border=True):
        st.markdown("#### 👥 Anagrafica Volontari - DB collegato a Distribuzione Radio")
        st.caption("I volontari inseriti qui saranno disponibili automaticamente nella scheda Distribuzione Radio (Assegnato A e Consegnata DA)")
        with st.form("form_volontari"):
            c1,c2,c3,c4 = st.columns(4)
            with c1:
                nome = st.text_input("Nome e Cognome *", placeholder="Mario Rossi")
                telefono = st.text_input("Telefono", placeholder="333 1234567")
            with c2:
                ruolo = st.selectbox("Ruolo", ["Volontario", "Capo Squadra", "Coordinatore", "Responsabile Magazzino", "Autista", "Presidente", "Segretario"])
                sezione = st.text_input("Sezione / Gruppo", value="Varese")
            with c3:
                email = st.text_input("Email", placeholder="mario@ana.it")
                tessera = st.text_input("N° Tessera ANA", placeholder="12345")
            with c4:
                note_v = st.text_input("Note", placeholder="Patente, specializzazioni...")
            if st.form_submit_button("💾 Salva Volontario", type="primary", use_container_width=True):
                if nome:
                    # Aggiungi a mem_nomi se non esiste
                    if nome not in st.session_state.mem_nomi:
                        st.session_state.mem_nomi.append(nome)
                        # Salva lista nomi
                        salva_csv([{"Nome": n} for n in st.session_state.mem_nomi], FILE_NOMI)
                    # Salva anche anagrafica completa se esiste file volontari
                    FILE_VOLONTARI = "anagrafica_volontari.csv"
                    # Carica esistente
                    volontari_full = []
                    if os.path.exists(FILE_VOLONTARI):
                        try:
                            volontari_full = pd.read_csv(FILE_VOLONTARI).to_dict(orient="records")
                        except:
                            pass
                    # Aggiorna o aggiungi
                    found = False
                    for v in volontari_full:
                        if v.get("Nome e Cognome") == nome or v.get("Nome") == nome:
                            v.update({"Nome e Cognome": nome, "Telefono": telefono, "Ruolo": ruolo, "Sezione": sezione, "Email": email, "Tessera": tessera, "Note": note_v})
                            found = True
                    if not found:
                        volontari_full.append({"Nome e Cognome": nome, "Telefono": telefono, "Ruolo": ruolo, "Sezione": sezione, "Email": email, "Tessera": tessera, "Note": note_v, "Data Iscrizione": str(datetime.now().date())})
                    pd.DataFrame(volontari_full).to_csv(FILE_VOLONTARI, index=False)
                    st.success(f"✅ Volontario {nome} salvato! Ora disponibile in Distribuzione Radio")
                    st.rerun()
                else:
                    st.error("Nome e Cognome obbligatorio")
        
        # Mostra volontari con DB completo
        FILE_VOLONTARI = "anagrafica_volontari.csv"
        if os.path.exists(FILE_VOLONTARI):
            try:
                df_vol_full = pd.read_csv(FILE_VOLONTARI)
                st.markdown(f"**Totale volontari: {len(df_vol_full)} - Questi nomi appaiono automaticamente in Distribuzione Radio**")
                st.dataframe(df_vol_full.iloc[::-1], use_container_width=True, hide_index=True)
                c1,c2,c3 = st.columns(3)
                with c1:
                    out = BytesIO()
                    df_vol_full.to_excel(out, index=False, engine="openpyxl")
                    st.download_button("📥 Excel Volontari", out.getvalue(), file_name="anagrafica_volontari.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
                with c2:
                    if st.button("🔄 Sincronizza nomi per Distribuzione", use_container_width=True):
                        # Sincronizza mem_nomi da anagrafica
                        nomi_from_full = df_vol_full["Nome e Cognome"].dropna().tolist() if "Nome e Cognome" in df_vol_full.columns else df_vol_full["Nome"].dropna().tolist() if "Nome" in df_vol_full.columns else []
                        st.session_state.mem_nomi = list(dict.fromkeys(nomi_from_full + st.session_state.mem_nomi))
                        salva_csv([{"Nome": n} for n in st.session_state.mem_nomi], FILE_NOMI)
                        st.success(f"Sincronizzati {len(st.session_state.mem_nomi)} nomi!")
                        st.rerun()
                with c3:
                    if st.button("🗑️ Cancella Anagrafica", use_container_width=True):
                        if os.path.exists(FILE_VOLONTARI):
                            os.remove(FILE_VOLONTARI)
                        st.session_state.mem_nomi = []
                        salva_csv([], FILE_NOMI)
                        st.rerun()
            except Exception as e:
                st.error(f"Errore lettura: {e}")
                st.dataframe(pd.DataFrame({"Volontari (lista rapida)": st.session_state.mem_nomi}), use_container_width=True, hide_index=True)
        else:
            if st.session_state.mem_nomi:
                st.markdown(f"**Volontari (lista rapida): {len(st.session_state.mem_nomi)}**")
                st.dataframe(pd.DataFrame({"Volontari": st.session_state.mem_nomi}), use_container_width=True, hide_index=True)
                st.info("💡 I nomi qui sopra sono già disponibili in Distribuzione Radio → Assegnato A e Consegnata DA")

# === DB RADIO ===
elif scelta == "📻 DB Radio Inventario":
    with st.container(border=True):
        st.markdown("#### 📻 Database Radio - Inventario")
        with st.form("form_radio_db"):
            c1,c2,c3,c4 = st.columns(4)
            with c1:
                radio_id_db = st.text_input("Radio ID *", placeholder="R-01")
                modello_db = st.selectbox("Modello *", ["Baofeng UV-5R", "Motorola T82", "Midland G9", "Altro"])
            with c2:
                seriale = st.text_input("Seriale")
                frequenza = st.text_input("Frequenza", placeholder="145.500 MHz")
            with c3:
                batteria = st.selectbox("Batteria", ["Carica", "Da caricare", "Guasta", "Nuova"])
                accessori = st.text_input("Accessori")
            with c4:
                stato_radio_db = st.selectbox("Stato", ["Disponibile", "In uso", "Guasta", "In riparazione"])
                note_radio_db = st.text_input("Note")
            if st.form_submit_button("💾 Salva Radio nel DB", use_container_width=True, type="primary"):
                if radio_id_db and modello_db:
                    if any(r.get("Radio ID")==radio_id_db for r in st.session_state.radio_db):
                        st.error(f"Radio {radio_id_db} già esistente!")
                    else:
                        st.session_state.radio_db.append({
                            "Radio ID": radio_id_db, "Modello": modello_db, "Seriale": seriale,
                            "Frequenza": frequenza, "Batteria": batteria, "Accessori": accessori,
                            "Stato": stato_radio_db, "Note": note_radio_db, "Data Inserimento": str(datetime.now().date())
                        })
                        salva_csv(st.session_state.radio_db, FILE_RADIO_DB)
                        st.success(f"Radio {radio_id_db} aggiunta!")
                        st.rerun()
                else:
                    st.error("Radio ID e Modello obbligatori")
        if st.session_state.radio_db:
            df_db = pd.DataFrame(st.session_state.radio_db).iloc[::-1]
            st.dataframe(df_db, use_container_width=True, hide_index=True)
            col1,col2 = st.columns(2)
            with col1:
                out = BytesIO()
                df_db.to_excel(out, index=False, engine="openpyxl")
                st.download_button("📥 Excel DB Radio", out.getvalue(), file_name="db_radio.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
            with col2:
                if st.button("🗑️ Cancella DB", use_container_width=True):
                    st.session_state.radio_db = []
                    salva_csv([], FILE_RADIO_DB)
                    st.rerun()

# === DISTRIBUZIONE ===
elif scelta == "📦 Distribuzione Radio":
    with st.container(border=True):
        st.markdown("#### 📦 Distribuzione Radio - Collegata ad Anagrafica Volontari")
        st.caption(f"📋 Volontari disponibili: {len(st.session_state.mem_nomi)} - Agganciati automaticamente dalla scheda Volontari | Se non vedi un nome, vai in 👥 Volontari e aggiungilo")
        if not st.session_state.mem_nomi:
            st.warning("⚠️ Nessun volontario in anagrafica! Vai in 👥 Volontari per aggiungerli prima di distribuire le radio")
        with st.form("form_dist"):
            c1,c2,c3,c4 = st.columns(4)
            with c1:
                data_d = st.date_input("Data", value=datetime.now())
                if st.session_state.radio_db:
                    st.markdown("**📻 Agganciato a DB Radio Inventario**")
                    # Crea lista con info complete
                    radio_list = []
                    for r in st.session_state.radio_db:
                        rid = str(r.get("Radio ID","")).strip()
                        if rid:
                            mod = str(r.get("Modello","")).strip()
                            stato = str(r.get("Stato","")).strip()
                            batt = str(r.get("Batteria","")).strip()
                            radio_list.append({"id": rid, "modello": mod, "stato": stato, "batteria": batt, "full": r})
                    
                    # Opzioni con stato
                    opzioni_display = ["-- Seleziona Radio dal DB --"]
                    for rl in radio_list:
                        icon = "🟢" if rl["stato"]=="Disponibile" else "🔴" if rl["stato"] in ["Guasta","In riparazione"] else "🟡"
                        opzioni_display.append(f"{icon} {rl['id']} - {rl['modello']} [{rl['stato']}] - Batt: {rl['batteria']}")
                    
                    scelta_display = st.selectbox("Radio ID dal DB Inventario *", opzioni_display, key="radio_db_linked")
                    
                    if scelta_display == "-- Seleziona Radio dal DB --":
                        st.warning("⚠️ Seleziona una radio dall'inventario")
                        radio_id = ""
                        modello = ""
                        radio_selezionata_full = None
                    else:
                        # Estrai ID
                        try:
                            # Formato "🟢 R-01 - Baofeng... [Disponibile] - Batt: Carica"
                            radio_id = scelta_display.split(" ")[1]  # R-01
                        except:
                            radio_id = scelta_display
                        radio_selezionata_full = next((rl["full"] for rl in radio_list if rl["id"]==radio_id), None)
                        if radio_selezionata_full:
                            modello = str(radio_selezionata_full.get("Modello",""))
                            st.success(f"✅ **{radio_id}** | Modello: **{modello}** | Stato: {radio_selezionata_full.get('Stato','')} | Batt: {radio_selezionata_full.get('Batteria','')}")
                            if radio_selezionata_full.get("Stato") != "Disponibile":
                                st.warning(f"⚠️ Attenzione: Radio in stato {radio_selezionata_full.get('Stato','')}")
                        else:
                            modello = ""
                    
                    # Campo modello bloccato agganciato
                    st.text_input("Modello (da DB Inventario) *", value=modello, disabled=True, key="modello_locked")
                    
                    if not st.session_state.radio_db:
                        st.info("💡 Vai in 📻 DB Radio per inserire radio")
                else:
                    st.error("⚠️ DB Radio vuoto! Vai in 📻 DB Radio Inventario e inserisci le radio")
                    radio_id = st.text_input("Radio ID * (manuale - DB vuoto)", placeholder="R-01")
                    modello = st.text_input("Modello *", placeholder="Baofeng UV-5R")
            with c2:
                assegnatario = combo_memoria("Assegnato A *", st.session_state.mem_nomi, "asseg", "Chi riceve")
                consegnato_da = combo_memoria("Consegnata DA *", st.session_state.mem_nomi, "cons_da", "Chi consegna")
            with c3:
                opzioni_post = ["-- Nuova --"] + [p.get("Postazione","") for p in st.session_state.postazioni]
                scelta_post = st.selectbox("Postazione *", opzioni_post)
                if scelta_post == "-- Nuova --":
                    postazione = st.text_input("Nuova Postazione *", placeholder="Posto 1")
                else:
                    postazione = scelta_post
                canale = st.selectbox("Canale", ["CH 1 - Emergenza", "CH 2 - Logistica", "CH 3 - Coordinamento", "VHF 145.500"])
            with c4:
                ora_cons = st.text_input("Ora consegna", value=datetime.now().strftime("%H:%M"))
                ora_ric = st.text_input("Ora riconsegna", placeholder="Al rientro")
                stato_r = st.selectbox("Stato", ["Consegnata", "Riconsegnata", "Guasta"])
            note_d = st.text_input("Note", placeholder="Con batteria carica")
            if st.form_submit_button("📦 Assegna Radio", use_container_width=True, type="primary"):
                if radio_id and radio_id != "" and assegnatario and postazione and consegnato_da and modello:
                    st.session_state.dist_radio.append({
                        "Data": str(data_d), "RadioID": radio_id, "Modello": modello,
                        "Assegnatario": assegnatario, "Consegnata DA": consegnato_da,
                        "Postazione": postazione, "Canale": canale,
                        "OraConsegna": ora_cons, "OraRiconsegna": ora_ric, "Stato": stato_r, "Note": note_d
                    })
                    salva_csv(st.session_state.dist_radio, FILE_DIST_RADIO)
                    st.success(f"Radio {radio_id} consegnata da {consegnato_da} a {assegnatario} in {postazione}")
                    st.rerun()
                else:
                    st.error("Compila Radio ID, Assegnato A, Consegnata DA e Postazione")
        if st.session_state.dist_radio:
            df_dist = pd.DataFrame(st.session_state.dist_radio).iloc[::-1]
            st.markdown("**👆 Clicca per vedere su mappa:**")
            cols_btn = st.columns(3)
            for i, row in df_dist.head(9).iterrows():
                with cols_btn[i % 3]:
                    if st.button(f"🗺️ {row.get('Postazione','')} | {row.get('RadioID','')} -> {str(row.get('Assegnatario',''))[:12]}", key=f"goto_{i}", use_container_width=True):
                        st.session_state.selected_postazione = row.get("Postazione","")
                        st.session_state.current_page = "🗺️ Mappa Postazioni"
                        st.rerun()
            st.dataframe(df_dist, use_container_width=True, hide_index=True)
            out = BytesIO()
            df_dist.to_excel(out, index=False, engine="openpyxl")
            st.download_button("📥 Excel Distribuzione", out.getvalue(), file_name="distribuzione.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)

# === MAPPA ===
elif scelta == "🗺️ Mappa Postazioni":
    with st.container(border=True):
        st.markdown("#### 🗺️ Mappa Postazioni FULLSCREEN")
        if st.session_state.get("selected_postazione"):
            st.success(f"📍 Evidenziata: **{st.session_state.selected_postazione}**")
        with st.expander("➕ Aggiungi Postazione con Comune e Via (agganciato a rete)", expanded=True):
            st.markdown("##### 🌍 Geocoding automatico da Comune e Via")
            c_com1, c_com2, c_com3 = st.columns([2,3,1])
            with c_com1:
                comune_input = st.text_input("Comune *", placeholder="Es: Varese", key="comune_input")
            with c_com2:
                via_input = st.text_input("Via / Indirizzo *", placeholder="Es: Via Sacco 5, Piazza Monte Grappa", key="via_input")
            with c_com3:
                st.markdown("<br>", unsafe_allow_html=True)
                cerca_coord = st.button("🔍 Cerca coordinate da rete", use_container_width=True, type="primary", key="cerca_coord_btn")
            
            # Risultato geocoding in session
            if "geo_lat" not in st.session_state:
                st.session_state.geo_lat = ""
                st.session_state.geo_lon = ""
                st.session_state.geo_display = ""
            
            if cerca_coord:
                if comune_input or via_input:
                    with st.spinner(f"🌐 Cerco {via_input}, {comune_input} sulla rete OSM..."):
                        lat_found, lon_found, display = geocode_comune_via(comune_input, via_input)
                        if lat_found and lon_found:
                            st.session_state.geo_lat = lat_found
                            st.session_state.geo_lon = lon_found
                            st.session_state.geo_display = display
                            st.success(f"✅ Trovato: {display}")
                            st.success(f"📍 Lat: {lat_found} | Lon: {lon_found}")
                        else:
                            st.error(f"❌ {display}")
                else:
                    st.error("Inserisci Comune e/o Via")
            
            if st.session_state.geo_display:
                st.info(f"📍 Risultato rete: **{st.session_state.geo_display}** | Lat: {st.session_state.geo_lat} | Lon: {st.session_state.geo_lon}")
            
            st.divider()
            with st.form("form_post"):
                c1,c2,c3 = st.columns(3)
                with c1:
                    nome_post = st.text_input("Nome Postazione *", placeholder="Posto 1 - Ingresso")
                    # Lat/Lon con valori da geocoding se presenti
                    lat_default = st.session_state.geo_lat if st.session_state.geo_lat else ""
                    lon_default = st.session_state.geo_lon if st.session_state.geo_lon else ""
                    lat = st.text_input("Latitudine *", value=lat_default, placeholder="45.8205")
                    lon = st.text_input("Longitudine *", value=lon_default, placeholder="8.8255")
                    # Campi comune e via salvati
                    comune_save = st.text_input("Comune (salvato)", value=comune_input, placeholder="Varese")
                    via_save = st.text_input("Via (salvata)", value=via_input, placeholder="Via Sacco 5")
                with c2:
                    resp_post = combo_memoria("Responsabile", st.session_state.mem_nomi, "resp_post", "Nome")
                    radio_post = st.text_input("Radio assegnata", placeholder="R-01")
                with c3:
                    tipo_post = st.selectbox("Tipo", ["Controllo accessi", "Viabilita", "Sicurezza", "Logistica", "COC", "Altro"])
                    note_post = st.text_input("Note")
                if st.form_submit_button("📍 Aggiungi alla Mappa", use_container_width=True, type="primary"):
                    if nome_post and lat and lon:
                        try:
                            float(lat); float(lon)
                            st.session_state.postazioni.append({
                                "Data": str(datetime.now().date()), "Postazione": nome_post,
                                "Comune": comune_save, "Via": via_save,
                                "Latitudine": lat, "Longitudine": lon,
                                "Responsabile": resp_post, "Radio": radio_post,
                                "Tipo": tipo_post, "Note": note_post,
                                "Indirizzo Completo": st.session_state.geo_display
                            })
                            # Reset geo dopo salvataggio
                            st.session_state.geo_lat = ""
                            st.session_state.geo_lon = ""
                            st.session_state.geo_display = ""
                            salva_csv(st.session_state.postazioni, FILE_POSTAZIONI)
                            st.success(f"{nome_post} aggiunta!")
                            st.rerun()
                        except:
                            st.error("Lat/Lon numeri")
        if st.session_state.postazioni:
            df_post = pd.DataFrame(st.session_state.postazioni)
            if "map_type" not in st.session_state:
                st.session_state.map_type = "OpenStreetMap"
            map_type = st.selectbox("🗺️ Tipo Mappa:", ["OpenStreetMap", "Google Stradale", "Google Satellite", "Google Ibrida", "Google Rilievo"], index=["OpenStreetMap", "Google Stradale", "Google Satellite", "Google Ibrida", "Google Rilievo"].index(st.session_state.map_type))
            st.session_state.map_type = map_type
            
            # Pulsanti navigazione se selezionata
            if st.session_state.get("selected_postazione"):
                for _, r in df_post.iterrows():
                    if r.get("Postazione") == st.session_state.selected_postazione:
                        try:
                            lat_s = r.get("Latitudine"); lon_s = r.get("Longitudine")
                            st.markdown(f"**🧭 Naviga verso: {st.session_state.selected_postazione}** - {lat_s},{lon_s}")
                            c1,c2,c3,c4 = st.columns(4)
                            with c1:
                                st.link_button("📱 Google Maps", f"https://www.google.com/maps/dir/?api=1&destination={lat_s},{lon_s}", use_container_width=True, type="primary")
                            with c2:
                                st.link_button("🚗 Waze", f"https://waze.com/ul?ll={lat_s},{lon_s}&navigate=yes", use_container_width=True)
                            with c3:
                                st.link_button("🗺️ OSM", f"https://www.openstreetmap.org/?mlat={lat_s}&mlon={lon_s}#map=18/{lat_s}/{lon_s}", use_container_width=True)
                            with c4:
                                st.link_button("🌍 Earth", f"https://earth.google.com/web/search/{lat_s},{lon_s}", use_container_width=True)
                        except:
                            pass
            
            st.markdown("**🔗 Clicca postazione per centrare:**")
            cols_map = st.columns(3)
            for idx, p in enumerate(st.session_state.postazioni):
                with cols_map[idx % 3]:
                    nome = p.get("Postazione","")
                    is_sel = st.session_state.get("selected_postazione") == nome
                    if st.button(f"{'✅ ' if is_sel else '📍 '}{nome}", key=f"map_sel_{idx}", use_container_width=True, type="primary" if is_sel else "secondary"):
                        st.session_state.selected_postazione = nome
                        st.rerun()
            
            try:
                import folium
                from streamlit_folium import st_folium
                selected = st.session_state.get("selected_postazione")
                center_lat, center_lon = 45.8205, 8.8255
                zoom = 14
                if selected:
                    for _, r in df_post.iterrows():
                        if r.get("Postazione") == selected:
                            try:
                                center_lat = float(r.get("Latitudine")); center_lon = float(r.get("Longitudine")); zoom = 17
                            except:
                                pass
                if map_type == "OpenStreetMap":
                    m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom, tiles="OpenStreetMap")
                elif map_type == "Google Stradale":
                    m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom, tiles=None)
                    folium.TileLayer('https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}', attr='Google', name='Google Stradale', max_zoom=20).add_to(m)
                elif map_type == "Google Satellite":
                    m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom, tiles=None)
                    folium.TileLayer('https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', attr='Google', name='Google Satellite', max_zoom=20).add_to(m)
                elif map_type == "Google Ibrida":
                    m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom, tiles=None)
                    folium.TileLayer('https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr='Google', name='Google Ibrida', max_zoom=20).add_to(m)
                elif map_type == "Google Rilievo":
                    m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom, tiles=None)
                    folium.TileLayer('https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}', attr='Google', name='Google Rilievo', max_zoom=20).add_to(m)
                
                for _, r in df_post.iterrows():
                    try:
                        lat_f = float(r.get("Latitudine")); lon_f = float(r.get("Longitudine"))
                        nome_p = r.get('Postazione','')
                        is_sel = nome_p == selected
                        comune_p = r.get('Comune','')
                        via_p = r.get('Via','')
                        popup = f"<b>{nome_p}</b><br>{comune_p} - {via_p}<br>Resp: {r.get('Responsabile','')}<br>Radio: {r.get('Radio','')}<br><a href='https://www.google.com/maps/dir/?api=1&destination={lat_f},{lon_f}' target='_blank'>Naviga Google</a> | <a href='https://waze.com/ul?ll={lat_f},{lon_f}&navigate=yes' target='_blank'>Waze</a>"
                        folium.Marker([lat_f, lon_f], popup=folium.Popup(popup, max_width=250), tooltip=nome_p, icon=folium.Icon(color="red" if is_sel else "green", icon="star" if is_sel else "info-sign")).add_to(m)
                        if is_sel:
                            folium.Circle([lat_f, lon_f], radius=60, color="red", fill=True, fill_opacity=0.3).add_to(m)
                    except:
                        pass
                st_folium(m, width=1400, height=600, use_container_width=True, key=f"folium_{map_type}_{center_lat}")
            except ImportError:
                st.warning("Installa folium")
            except Exception as e:
                st.error(f"Errore mappa: {e}")
            
            st.dataframe(df_post, use_container_width=True, hide_index=True)
        else:
            st.info("Nessuna postazione - Aggiungi la prima!")

# === REGISTRO ===
elif scelta == "📋 Registro Radio":
    st.info("📋 Registro uso radio - qui puoi aggiungere il registro giornaliero")
    with st.container(border=True):
        with st.form("form_registro"):
            c1,c2,c3 = st.columns(3)
            with c1:
                data_reg = st.date_input("Data", value=datetime.now())
                radio_reg = st.text_input("Radio ID")
            with c2:
                volontario_reg = combo_memoria("Volontario", st.session_state.mem_nomi, "vol_reg", "Nome")
                ore_uso = st.text_input("Ore uso", placeholder="08:00-12:00")
            with c3:
                stato_reg = st.selectbox("Stato finale", ["OK", "Batteria scarica", "Guasta", "Persa"])
                note_reg = st.text_input("Note")
            if st.form_submit_button("💾 Salva Registro", type="primary", use_container_width=True):
                st.session_state.registro_radio.append({
                    "Data": str(data_reg), "RadioID": radio_reg, "Volontario": volontario_reg,
                    "OreUso": ore_uso, "Stato": stato_reg, "Note": note_reg
                })
                salva_csv(st.session_state.registro_radio, FILE_REGISTRO)
                st.success("Registro salvato!")
                st.rerun()
        if st.session_state.registro_radio:
            st.dataframe(pd.DataFrame(st.session_state.registro_radio).iloc[::-1], use_container_width=True, hide_index=True)

# === LINK ===
elif scelta == "🔗 Link & Aggiornamenti":
    with st.container(border=True):
        st.markdown("#### 🔗 Link per Inserire Aggiornamenti")
        app_url = st.text_input("🌐 URL della tua app Streamlit", placeholder="https://ana-varse.streamlit.app")
        if app_url:
            st.success(f"Link: {app_url}")
            c1,c2 = st.columns(2)
            with c1:
                msg = f"Aggiorna ANA Varese: {app_url}"
                st.link_button("📱 WhatsApp", f"https://wa.me/?text={msg.replace(' ', '%20')}", use_container_width=True)
            with c2:
                st.link_button("✈️ Telegram", f"https://t.me/share/url?url={app_url}", use_container_width=True)
            try:
                import qrcode
                qr = qrcode.QRCode(version=1, box_size=10, border=4)
                qr.add_data(app_url)
                qr.make(fit=True)
                img = qr.make_image(fill='black', back_color='white')
                buf = BytesIO()
                img.save(buf, format='PNG')
                st.image(buf.getvalue(), caption="QR Code", width=200)
                st.download_button("📥 Scarica QR", buf.getvalue(), file_name="qr_ana.png", mime="image/png", use_container_width=True)
            except:
                st.info("Aggiungi qrcode[pil] ai requirements per QR")
        st.divider()
        st.markdown("#### 📤 Backup & Ripristino")
        c1,c2 = st.columns(2)
        with c1:
            if st.session_state.postazioni or st.session_state.dist_radio:
                all_data = {
                    "postazioni": st.session_state.postazioni,
                    "distribuzione_radio": st.session_state.dist_radio,
                    "radio_db": st.session_state.radio_db,
                    "volontari": st.session_state.mem_nomi,
                    "data_export": str(datetime.now())
                }
                st.download_button("📥 Backup JSON Completo", json.dumps(all_data, indent=2, ensure_ascii=False).encode('utf-8'), file_name=f"backup_{datetime.now().strftime('%Y%m%d')}.json", mime="application/json", use_container_width=True)
        with c2:
            uploaded = st.file_uploader("Carica backup JSON", type=["json"])
            if uploaded:
                try:
                    data = json.loads(uploaded.read().decode('utf-8'))
                    if st.button("🔄 Importa", type="primary", use_container_width=True):
                        if "postazioni" in data:
                            st.session_state.postazioni = data["postazioni"]
                            salva_csv(data["postazioni"], FILE_POSTAZIONI)
                        if "distribuzione_radio" in data:
                            st.session_state.dist_radio = data["distribuzione_radio"]
                            salva_csv(data["distribuzione_radio"], FILE_DIST_RADIO)
                        if "radio_db" in data:
                            st.session_state.radio_db = data["radio_db"]
                            salva_csv(data["radio_db"], FILE_RADIO_DB)
                        st.success("Importato!")
                        st.rerun()
                except Exception as e:
                    st.error(f"Errore: {e}")
