
import streamlit as st, os, json, pandas as pd
from datetime import datetime, date
import base64

st.set_page_config(page_title="ANA Varese - Dashboard Unica", page_icon="🛡️", layout="wide", initial_sidebar_state="expanded")

for k,v in {
    "page":"entra","logged":False,"menu":"Dashboard","hub_page":"hub",
    "volontari":[],"ospiti":[],"eventi":[],"emergenze":[],"checkin":[],"interventi":[],
    "mezzi":[],"attrezzature":[],"radio_db":[],"consegna_radio":[],"alias_radio":[],
    "brogliaccio":[],"turni":[],"chat":[],"spese_odv":[],"note_spese":[],"archivio_documenti":[],
    "verbali":[],"diplomi":[]
}.items():
    if k not in st.session_state:
        st.session_state[k]=v

MENU_ADMIN = ["Dashboard","Volontari (con foto)","Ospiti","Verbali","Archivio Documenti","Diplomi Attestati","Spese ODV per Evento","Note Spese","Report Filtro","Statistiche","Gestione Utenti","Backup"]
MENU_OPER = ["Dashboard","Volontari (con foto)","DB Radio","Consegna Radio","Alias Radio","Brogliaccio","Eventi","Emergenze","Tabella Emergenze","Check-in","Interventi Emergenza","Tabella Interventi Emergenza","Mezzi","Attrezzature","Mappe Postazioni","Libreria Icone","Turni","Chat"]

def hdr_form(tit):
    st.markdown(f"<div style='background:linear-gradient(135deg,#1A5D1A,#2e7d32);color:white;padding:10px;border-radius:8px;border:2px solid #FFD700;text-align:center'><b>{tit}</b></div>", unsafe_allow_html=True)
    st.write("")

# CSS
st.markdown("""
<style>
#MainMenu{visibility:hidden;} footer{visibility:hidden;}
.stApp{background:#e8f5e9 !important;}
.stButton>button{border-radius:8px;font-weight:600;}
</style>
""", unsafe_allow_html=True)

# PAGINA ENTRA - come primo file
if st.session_state.page == "entra":
    hdr_form("GESTIONALE DI PROTEZIONE CIVILE - Versione BETA")
    c1,c2,c3 = st.columns([1,2,1])
    with c2:
        try:
            if os.path.exists("copertina.png"):
                st.image("copertina.png", width=350)
            elif os.path.exists("logo.png"):
                st.image("logo.png", width=250)
            else:
                st.markdown('<div style="text-align:center;padding:40px;background:#c8e6c9;border-radius:16px;border:2px dashed #1A5D1A;"><div style="font-size:100px;">🛡️</div><p><b>Squadra Volontari di protezione civile</b><br>Gruppo Alpini di Caronno Pertusella Bariola</p></div>', unsafe_allow_html=True)
        except:
            pass
        st.markdown('<h2 style="text-align:center;">GESTIONALE DI PROTEZIONE CIVILE</h2><p style="text-align:center;">Squadra Volontari di protezione civile<br>Gruppo Alpini di Caronno Pertusella Bariola</p><p style="text-align:center;">Versione BETA - Sviluppato per Ezio</p>', unsafe_allow_html=True)
        if st.button("ENTRA NEL GESTIONALE", type="primary", use_container_width=True):
            st.session_state.page = "login"
            st.rerun()
    st.divider()
    st.markdown('<div style="text-align:center;padding:6px;background:#1A5D1A;color:white;border-radius:6px">Developed by Ezio F. 2026 Vers 1.0 - Senza Geoloc - Senza Splash dopo login</div>', unsafe_allow_html=True)
    st.stop()

# LOGIN
if not st.session_state.logged:
    if st.session_state.page == "login":
        st.markdown("### Login")
        u = st.text_input("Username", value="admin")
        p = st.text_input("Password", type="password", value="ana2024")
        if st.button("Accedi", type="primary", use_container_width=True):
            if u=="admin" and p=="ana2024":
                st.session_state.logged=True
                st.session_state.page="dashboard"
                st.session_state.hub_page="hub"
                st.rerun()
            else:
                st.error("Credenziali errate")
        if st.button("Torna a Entra"):
            st.session_state.page="entra"
            st.rerun()
    st.stop()

# HUB - INTESTAZIONE COME PRIMA PAGINA - SENZA SPLASH DOPO LOGIN
if st.session_state.hub_page == "hub":
    hdr_form("GESTIONALE DI PROTEZIONE CIVILE - Seleziona Progetto")
    c1,c2,c3 = st.columns([1,2,1])
    with c2:
        try:
            if os.path.exists("copertina.png"):
                st.image("copertina.png", width=350)
            elif os.path.exists("logo.png"):
                st.image("logo.png", width=250)
            else:
                st.markdown('<div style="text-align:center;padding:40px;background:#c8e6c9;border-radius:16px;border:2px dashed #1A5D1A;"><div style="font-size:100px;">🛡️</div><p><b>Squadra Volontari</b></p></div>', unsafe_allow_html=True)
        except:
            pass
        st.markdown('<h2 style="text-align:center;">SQUADRA VOLONTARI DI PROTEZIONE CIVILE</h2><p style="text-align:center;">Gruppo Alpini di Caronno Pertusella Bariola</p><p style="text-align:center;font-weight:bold;">Seleziona il progetto - Senza Geolocalizzazione - Senza Splash dopo login</p>', unsafe_allow_html=True)
        st.divider()
        colA,colB = st.columns(2, gap="large")
        with colA:
            st.markdown('<div style="text-align:center;background:#1565C0;color:white;padding:14px;border-radius:12px;font-weight:bold">📋 AMMINISTRATIVO<br><small>13 form - Gestione ODV</small></div>', unsafe_allow_html=True)
            st.write("")
            if st.button("📋 ENTRA AMMINISTRATIVO\nGestione ODV", key="hub_admin_final", use_container_width=True, type="primary"):
                st.session_state.hub_page="admin"
                st.session_state.menu="Dashboard"
                st.rerun()
        with colB:
            st.markdown('<div style="text-align:center;background:#1A5D1A;color:white;padding:14px;border-radius:12px;font-weight:bold">🚒 OPERATIVO<br><small>Emergenze e Radio</small></div>', unsafe_allow_html=True)
            st.write("")
            if st.button("🚒 ENTRA OPERATIVO\nEmergenze e Radio", key="hub_oper_final", use_container_width=True, type="primary"):
                st.session_state.hub_page="operativo"
                st.session_state.menu="Dashboard"
                st.rerun()
        st.divider()
        st.markdown('<div style="text-align:center;padding:6px;background:#1A5D1A;color:white;border-radius:6px">Developed by Ezio F. 2026 Vers 1.0</div>', unsafe_allow_html=True)
    st.stop()

# SIDEBAR - solo elenco del progetto aperto
with st.sidebar:
    try:
        if os.path.exists("logo.png"):
            st.image("logo.png", width=110)
        else:
            st.markdown('<div style="width:110px;height:110px;background:#1A5D1A;border-radius:10px;display:flex;align-items:center;justify-content:center;color:white;font-weight:bold">ANA</div>', unsafe_allow_html=True)
    except:
        st.write("ANA")
    st.markdown(f"<p style='font-weight:bold;color:#1A5D1A'>HUB: {st.session_state.hub_page.upper()}</p>", unsafe_allow_html=True)
    if st.button("🏠 TORNA AL HUB", use_container_width=True, type="primary"):
        st.session_state.hub_page="hub"
        st.session_state.menu="Dashboard"
        st.rerun()
    st.divider()
    if st.session_state.hub_page=="admin":
        menu_base = MENU_ADMIN
        st.markdown("**📋 AMMINISTRATIVO - Solo elenco admin**")
    else:
        menu_base = MENU_OPER
        st.markdown("**🚒 OPERATIVO - Solo elenco operativo**")
    cur = st.radio("Seleziona form", menu_base, index=menu_base.index(st.session_state.menu) if st.session_state.menu in menu_base else 0)
    st.session_state.menu = cur
    st.divider()
    if st.button("Logout", use_container_width=True):
        st.session_state.logged=False
        st.session_state.page="entra"
        st.session_state.hub_page="hub"
        st.rerun()

# DASHBOARD - SENZA SPLASH, CON VOLONTARI, BOTTONI ATTIVI
if cur == "Dashboard":
    hdr_form(f"DASHBOARD {st.session_state.hub_page.upper()} - Solo form del progetto aperto")
    if st.session_state.hub_page=="admin":
        buttons = [("Volontari (con foto)","👤 Volontari"),("Ospiti","🧑‍🤝‍🧑 Ospiti"),("Verbali","📝 Verbali"),("Archivio Documenti","📁 Archivio"),("Diplomi Attestati","🏅 Diplomi"),("Spese ODV per Evento","💰 Spese ODV"),("Note Spese","🧾 Note Spese"),("Report Filtro","📊 Report"),("Statistiche","📈 Statistiche"),("Backup","💾 Backup")]
        st.success(f"📋 AMMINISTRATIVO - {len(buttons)} form - Senza Splash - Con Volontari")
    else:
        buttons = [("Volontari (con foto)","👤 Volontari"),("Eventi","📅 Eventi"),("DB Radio","📻 DB Radio"),("Consegna Radio","🤝 Consegna"),("Alias Radio","🔖 Alias"),("Brogliaccio","📓 Brogliaccio"),("Emergenze","🚨 Emergenze"),("Tabella Emergenze","📋 Tab Emergenze"),("Check-in","✅ Check-in"),("Interventi Emergenza","🚒 Interventi"),("Tabella Interventi Emergenza","📋 Tab Interventi"),("Mezzi","🚐 Mezzi"),("Attrezzature","🧰 Attrezzature"),("Mappe Postazioni","🌍 Mappe"),("Libreria Icone","🎨 Icone"),("Turni","🕐 Turni"),("Chat","💬 Chat")]
        st.success(f"🚒 OPERATIVO - {len(buttons)} form - Senza Splash - Con Volontari - Geoloc rimossa - Bottoni ATTIVI")
    cols = st.columns(3)
    for idx,(fkey,flabel) in enumerate(buttons):
        with cols[idx%3]:
            if st.button(flabel, key=f"dash_{st.session_state.hub_page}_{fkey}_{idx}_ATTIVO", use_container_width=True, type="primary"):
                st.session_state.menu=fkey
                st.rerun()
    st.caption(f"Dashboard {st.session_state.hub_page.upper()} - {len(buttons)} bottoni ATTIVI - Senza Splash - Con Volontari - A sinistra solo elenco {st.session_state.hub_page}")

elif cur == "Eventi":
    hdr_form("📅 EVENTI")
    with st.form("eventi_form"):
        c1,c2 = st.columns(2)
        with c1:
            nome = st.text_input("Nome Evento")
            data = st.date_input("Data Evento")
            luogo = st.text_input("Luogo")
        with c2:
            tipo = st.selectbox("Tipo", ["Esercitazione","Emergenza","Manifestazione","Formazione","Altro"])
            note = st.text_area("Note")
        if st.form_submit_button("💾 Salva Evento", type="primary", use_container_width=True):
            st.session_state.eventi.append({"nome":nome,"data":str(data),"luogo":luogo,"tipo":tipo,"note":note,"ts":str(datetime.now())})
            st.success("Salvato!")
            st.rerun()
    if st.session_state.eventi:
        st.dataframe(pd.DataFrame(st.session_state.eventi), use_container_width=True)

elif cur == "Note Spese":
    hdr_form("🧾 NOTE SPESE")
    with st.form("note_spese"):
        c1,c2,c3 = st.columns(3)
        with c1:
            d = st.date_input("Data")
            vol = st.text_input("Volontario")
            ev = st.text_input("Evento")
        with c2:
            tipo = st.selectbox("Tipo", ["Carburante","Pedaggio","Vitto","Materiale","Parcheggio","Altro"])
            imp = st.number_input("Importo €", min_value=0.0, step=0.1)
        with c3:
            pag = st.selectbox("Pagato da", ["Volontario","ODV","Anticipo"])
            note = st.text_area("Note")
        if st.form_submit_button("💾 Salva", type="primary", use_container_width=True):
            st.session_state.note_spese.append({"data":str(d),"volontario":vol,"evento":ev,"tipo":tipo,"importo":imp,"pagato_da":pag,"note":note})
            st.success("Salvata!")
            st.rerun()
    if st.session_state.note_spese:
        df = pd.DataFrame(st.session_state.note_spese)
        st.dataframe(df, use_container_width=True)

elif cur == "Statistiche":
    hdr_form("📊 STATISTICHE")
    spese = st.session_state.get("spese_odv",[])
    note = st.session_state.get("note_spese",[])
    tot_s = sum([float(x.get("importo",0)) for x in spese]) if spese else 0
    tot_n = sum([float(x.get("importo",0)) for x in note]) if note else 0
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Spese ODV", f"€ {tot_s:.2f}")
    c2.metric("Note Spese", f"€ {tot_n:.2f}")
    c3.metric("Totale", f"€ {tot_s+tot_n:.2f}")
    c4.metric("Eventi", len(st.session_state.eventi))

else:
    hdr_form(f"{cur}")
    st.info(f"Form '{cur}' - struttura base - Senza Geoloc - Senza Splash in dashboard ma con Volontari")

st.divider()
st.markdown('<div style="text-align:center;padding:6px;background:#1A5D1A;color:white;border-radius:6px">ANA Varese - UNICO - Senza Splash in dashboard ma con Volontari - No Splash dopo login - HUB come prima pagina - Fix 7513</div>', unsafe_allow_html=True)
