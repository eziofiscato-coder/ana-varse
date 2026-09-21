import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="ANA Varese", layout="centered")

def hdr():
    col_logo, col_tit = st.columns([1,5])
    with col_logo:
        try:
            st.image("logo.png", width=120)
        except:
            st.write("ANA")
    with col_tit:
        st.markdown("<div style='background:#0e7a3d; padding:10px; border-radius:8px; color:white; text-align:center; font-weight:bold;'>NUCLEO DI VOLONTARI DI PROTEZIONE CIVILE<br>ANA SEZIONE DI VARESE</div>", unsafe_allow_html=True)

# --- GESTIONE PAGINE ---
if "page" not in st.session_state:
    st.session_state.page = "entra"
if "logged" not in st.session_state:
    st.session_state.logged = False
if "dati" not in st.session_state:
    st.session_state.dati = []

# --- 1° FOGLIO: ENTRA ---
if st.session_state.page == "entra":
    hdr()
    c1,c2,c3 = st.columns([1,2,1])
    with c2:
        try:
            st.image("copertina.png", width=400)
        except:
            try:
                st.image("logo.png", width=250)
            except:
                st.write("")
    st.markdown("<h2 style='text-align:center; color:#0e7a3d;'>VOLONTARIATO<br>Sezione di Varese</h2>", unsafe_allow_html=True)
    st.divider()
    st.markdown("<br><br>", unsafe_allow_html=True)
    c1,c2,c3 = st.columns([1,1,1])
    with c2:
        if st.button("🚪 ENTRA", use_container_width=True, type="primary"):
            st.session_state.page = "login"
            st.rerun()
    st.markdown("<p style='text-align:center; color:gray;'><br>Benvenuto nel sistema ANA Varese</p>", unsafe_allow_html=True)

# --- 2° FOGLIO: LOGIN ---
elif st.session_state.page == "login":
    hdr()
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
                # CAMBIA QUI UTENTE E PASSWORD SE VUOI
                if user == "admin" and pwd == "ana2024":
                    st.session_state.logged = True
                    st.session_state.page = "dashboard"
                    st.rerun()
                else:
                    st.error("Utente o password errati - prova admin / ana2024")

# --- 3° FOGLIO: DASHBOARD DOPO LOGIN ---
elif st.session_state.page == "dashboard" and st.session_state.logged:
    hdr()
    c1,c2 = st.columns([8,1])
    with c2:
        if st.button("Logout"):
            st.session_state.logged = False
            st.session_state.page = "entra"
            st.rerun()
    
    st.markdown("<h2 style='text-align:center; color:#0e7a3d;'>VOLONTARIATO - Dashboard</h2>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "👥 Volontari", "🗺️ Mappa"])

    with tab1:
        st.markdown("### Dashboard ANA Varese")
        st.info(f"Totale volontari registrati: {len(st.session_state.dati)}")
        if st.session_state.dati:
            df_dash = pd.DataFrame(st.session_state.dati)
            st.dataframe(df_dash, use_container_width=True, hide_index=True)
            if "Ruolo" in df_dash.columns:
                st.bar_chart(df_dash["Ruolo"].value_counts())
            output = BytesIO()
            df_dash.to_excel(output, index=False, engine="openpyxl")
            st.download_button("📥 Scarica Excel completo", output.getvalue(), file_name="ana_varese_completo.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        else:
            st.warning("Nessun volontario ancora registrato. Vai in tab Volontari.")

    with tab2:
        st.markdown("### Registra Volontario")
        with st.form("form"):
            nome = st.text_input("Nome e Cognome *")
            assoc = st.text_input("Associazione *")
            cell = st.text_input("Cellulare *")
            ruolo = st.selectbox("Ruolo *", ["Volontario", "Caposquadra", "Coordinatore", "Autista", "Radio", "Telecomunicazioni", "Logistica", "Segreteria", "Sanitario", "Altro"])
            st.divider()
            st.markdown("**Posizione - SENZA DEFAULT VARESE**")
            comune = st.text_input("Comune *")
            via = st.text_input("Via / Localita")
            cc1, cc2 = st.columns(2)
            with cc1:
                lat_txt = st.text_input("Lat", placeholder="es. 45.123456")
            with cc2:
                lon_txt = st.text_input("Log", placeholder="es. 8.123456")
            submitted = st.form_submit_button("✅ Salva con posizione", use_container_width=True)
            if submitted:
                if nome and assoc and cell and comune:
                    try:
                        lat_v = float(lat_txt.replace(",", ".")) if lat_txt else 0.0
                        lon_v = float(lon_txt.replace(",", ".")) if lon_txt else 0.0
                    except:
                        lat_v = 0.0
                        lon_v = 0.0
                    st.session_state.dati.append({"Nome": nome, "Associazione": assoc, "Cellulare": cell, "Ruolo": ruolo, "Comune": comune, "Via": via, "Lat": lat_v, "Log": lon_v})
                    st.success(f"Aggiunto {nome} - {comune}")
                else:
                    st.error("Compila * e Comune")

    with tab3:
        st.markdown("### Mappa - Tutti i marker")
        if st.session_state.dati:
            df = pd.DataFrame(st.session_state.dati)
            st.dataframe(df, use_container_width=True, hide_index=True)
            if "Lat" in df.columns:
                df_map = df.rename(columns={"Lat": "lat", "Log": "lon"})
                df_map = df_map[(df_map["lat"] != 0) & (df_map["lon"] != 0)]
                if not df_map.empty:
                    st.map(df_map, latitude="lat", longitude="lon", zoom=10, use_container_width=True)
                    st.info(f"{len(df_map)} marker sulla mappa - nessun default Varese")
                else:
                    st.info("Inserisci Lat e Log nel form - nessun default Varese")
        else:
            st.info("Nessuna posizione da mostrare")