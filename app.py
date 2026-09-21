import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="ANA Varese", layout="wide")

def hdr_small():
    st.markdown("<div style='background:#0e7a3d; padding:8px; border-radius:8px; color:white; text-align:center; font-weight:bold;'>NUCLEO VOLONTARI PROTEZIONE CIVILE - ANA VARESE</div>", unsafe_allow_html=True)

if "page" not in st.session_state:
    st.session_state.page = "entra"
if "logged" not in st.session_state:
    st.session_state.logged = False
if "menu" not in st.session_state:
    st.session_state.menu = "Dashboard"
if "volontari" not in st.session_state:
    st.session_state.volontari = []
if "mezzi" not in st.session_state:
    st.session_state.mezzi = []
if "attrezzature" not in st.session_state:
    st.session_state.attrezzature = []
if "interventi" not in st.session_state:
    st.session_state.interventi = []

# 1 - ENTRA (con copertina solo qui)
if st.session_state.page == "entra":
    hdr_small()
    c1,c2,c3 = st.columns([1,2,1])
    with c2:
        try:
            st.image("copertina.png", width=400)
        except:
            try:
                st.image("logo.png", width=200)
            except:
                pass
    st.markdown("<h2 style='text-align:center; color:#0e7a3d;'>VOLONTARIATO<br>Sezione di Varese</h2>", unsafe_allow_html=True)
    st.divider()
    c1,c2,c3 = st.columns([1,1,1])
    with c2:
        if st.button("🚪 ENTRA", use_container_width=True, type="primary"):
            st.session_state.page = "login"
            st.rerun()

# 2 - LOGIN
elif st.session_state.page == "login":
    hdr_small()
    st.markdown("<h3 style='text-align:center;'>Login</h3>", unsafe_allow_html=True)
    c1,c2,c3 = st.columns([1,2,1])
    with c2:
        user = st.text_input("Utente")
        pwd = st.text_input("Password", type="password")
        col1,col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Indietro", use_container_width=True):
                st.session_state.page = "entra"
                st.rerun()
        with col2:
            if st.button("🔐 Accedi", use_container_width=True, type="primary"):
                if user == "admin" and pwd == "ana2024":
                    st.session_state.logged = True
                    st.session_state.page = "dashboard"
                    st.rerun()
                else:
                    st.error("admin / ana2024")

# 3 - DASHBOARD SENZA IMMAGINI - CON MENU LATERALE E BOTTONI
elif st.session_state.page == "dashboard":
    hdr_small()
    
    with st.sidebar:
        st.markdown("### MENU FORM")
        menu = st.radio("Scegli form:", ["📊 Dashboard", "👥 Form Volontario", "🏢 Form Associazione", "🚚 Form Mezzi", "🧰 Form Attrezzature", "📍 Form Intervento", "🗺️ Mappa", "📥 Esporta"], index=0, key="menu_radio")
        st.session_state.menu = menu
        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged = False
            st.session_state.page = "entra"
            st.rerun()

    # DASHBOARD - BOTTONI RAPIDI - NO IMMAGINI
    if st.session_state.menu == "📊 Dashboard":
        st.markdown("## 📊 Dashboard - Scelta rapida")
        st.info(f"Volontari: {len(st.session_state.volontari)} | Mezzi: {len(st.session_state.mezzi)} | Attrezzature: {len(st.session_state.attrezzature)} | Interventi: {len(st.session_state.interventi)}")
        
        st.markdown("### TASTI RAPIDI FORM")
        c1,c2,c3,c4 = st.columns(4)
        with c1:
            if st.button("👥 VOLONTARIO", use_container_width=True, type="primary"):
                st.session_state.menu = "👥 Form Volontario"
                st.rerun()
        with c2:
            if st.button("🏢 ASSOCIAZIONE", use_container_width=True):
                st.session_state.menu = "🏢 Form Associazione"
                st.rerun()
        with c3:
            if st.button("🚚 MEZZI", use_container_width=True):
                st.session_state.menu = "🚚 Form Mezzi"
                st.rerun()
        with c4:
            if st.button("🧰 ATTREZZATURE", use_container_width=True):
                st.session_state.menu = "🧰 Form Attrezzature"
                st.rerun()
        c1,c2,c3,c4 = st.columns(4)
        with c1:
            if st.button("📍 INTERVENTO", use_container_width=True):
                st.session_state.menu = "📍 Form Intervento"
                st.rerun()
        with c2:
            if st.button("🗺️ MAPPA", use_container_width=True):
                st.session_state.menu = "🗺️ Mappa"
                st.rerun()
        with c3:
            if st.button("📥 ESPORTA", use_container_width=True):
                st.session_state.menu = "📥 Esporta"
                st.rerun()
        with c4:
            if st.button("📋 ELENCO", use_container_width=True):
                st.session_state.menu = "📊 Dashboard"
                st.rerun()
        
        st.divider()
        if st.session_state.volontari:
            st.markdown("### Ultimi volontari")
            st.dataframe(pd.DataFrame(st.session_state.volontari), use_container_width=True)

    # TUTTI I FORM - ORA SI VEDONO QUANDO CLICCHI
    elif st.session_state.menu == "👥 Form Volontario":
        st.markdown("## 👥 Form Volontario")
        with st.form("form_vol"):
            nome = st.text_input("Nome e Cognome *")
            assoc = st.text_input("Associazione *")
            cell = st.text_input("Cellulare *")
            ruolo = st.selectbox("Ruolo *", ["Volontario", "Caposquadra", "Coordinatore", "Autista", "Radio", "Telecomunicazioni", "Logistica", "Segreteria", "Sanitario", "Altro"])
            st.divider()
            comune = st.text_input("Comune *")
            via = st.text_input("Via / Localita")
            cc1, cc2 = st.columns(2)
            with cc1:
                lat_txt = st.text_input("Lat", placeholder="VUOTO = no default Varese")
            with cc2:
                lon_txt = st.text_input("Log", placeholder="VUOTO = no default Varese")
            if st.form_submit_button("✅ SALVA VOLONTARIO", use_container_width=True, type="primary"):
                if nome and assoc and cell and comune:
                    try:
                        lat_v = float(lat_txt.replace(",", ".")) if lat_txt else 0.0
                        lon_v = float(lon_txt.replace(",", ".")) if lon_txt else 0.0
                    except:
                        lat_v = 0.0
                        lon_v = 0.0
                    st.session_state.volontari.append({"Nome": nome, "Associazione": assoc, "Cellulare": cell, "Ruolo": ruolo, "Comune": comune, "Via": via, "Lat": lat_v, "Log": lon_v})
                    st.success(f"✅ Salvato {nome}")
                else:
                    st.error("Compila *")

    elif st.session_state.menu == "🏢 Form Associazione":
        st.markdown("## 🏢 Form Associazione")
        with st.form("form_assoc"):
            nome_a = st.text_input("Nome Associazione *")
            resp = st.text_input("Responsabile *")
            tel = st.text_input("Telefono")
            comune = st.text_input("Comune *")
            if st.form_submit_button("✅ SALVA ASSOCIAZIONE", use_container_width=True, type="primary"):
                if nome_a and resp and comune:
                    st.success(f"✅ Associazione {nome_a} salvata")
                else:
                    st.error("Compila *")

    elif st.session_state.menu == "🚚 Form Mezzi":
        st.markdown("## 🚚 Form Mezzi")
        with st.form("form_mezzi"):
            targa = st.text_input("Targa *")
            tipo = st.selectbox("Tipo", ["Fuoristrada", "Furgone", "Ambulanza", "Autocarro", "Moto", "Altro"])
            stato = st.selectbox("Stato", ["Operativo", "In manutenzione", "Non operativo"])
            if st.form_submit_button("✅ SALVA MEZZO", use_container_width=True, type="primary"):
                if targa:
                    st.session_state.mezzi.append({"Targa": targa, "Tipo": tipo, "Stato": stato})
                    st.success(f"✅ Mezzo {targa} salvato")
        if st.session_state.mezzi:
            st.dataframe(pd.DataFrame(st.session_state.mezzi), use_container_width=True)

    elif st.session_state.menu == "🧰 Form Attrezzature":
        st.markdown("## 🧰 Form Attrezzature")
        with st.form("form_attr"):
            nome_attr = st.text_input("Attrezzatura *")
            qta = st.number_input("Quantita", min_value=1, value=1)
            mag = st.text_input("Magazzino")
            if st.form_submit_button("✅ SALVA ATTREZZATURA", use_container_width=True, type="primary"):
                if nome_attr:
                    st.session_state.attrezzature.append({"Attrezzatura": nome_attr, "Qta": qta, "Magazzino": mag})
                    st.success(f"✅ {nome_attr} salvata")
        if st.session_state.attrezzature:
            st.dataframe(pd.DataFrame(st.session_state.attrezzature), use_container_width=True)

    elif st.session_state.menu == "📍 Form Intervento":
        st.markdown("## 📍 Form Intervento")
        with st.form("form_int"):
            data = st.date_input("Data")
            luogo = st.text_input("Luogo *")
            tipo = st.selectbox("Tipo", ["Emergenza", "Esercitazione", "Prevenzione", "Logistica", "Altro"])
            descr = st.text_area("Descrizione")
            if st.form_submit_button("✅ SALVA INTERVENTO", use_container_width=True, type="primary"):
                if luogo:
                    st.session_state.interventi.append({"Data": str(data), "Luogo": luogo, "Tipo": tipo, "Descrizione": descr})
                    st.success("✅ Intervento salvato")
        if st.session_state.interventi:
            st.dataframe(pd.DataFrame(st.session_state.interventi), use_container_width=True)

    elif st.session_state.menu == "🗺️ Mappa":
        st.markdown("## 🗺️ Mappa")
        if st.session_state.volontari:
            df = pd.DataFrame(st.session_state.volontari)
            df_map = df.rename(columns={"Lat": "lat", "Log": "lon"})
            df_map = df_map[(df_map["lat"] != 0) & (df_map["lon"] != 0)]
            if not df_map.empty:
                st.map(df_map, zoom=10, use_container_width=True)
                st.success(f"{len(df_map)} marker")
            else:
                st.info("Nessun Lat/Log - VUOTO = no default Varese")
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Nessun volontario")

    elif st.session_state.menu == "📥 Esporta":
        st.markdown("## 📥 Esporta Excel")
        if st.session_state.volontari:
            df = pd.DataFrame(st.session_state.volontari)
            output = BytesIO()
            df.to_excel(output, index=False, engine="openpyxl")
            st.download_button("📥 Scarica Volontari", output.getvalue(), file_name="volontari.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)