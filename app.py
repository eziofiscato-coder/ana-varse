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

hdr()

c1,c2,c3 = st.columns([1,2,1])
with c2:
    try:
        st.image("copertina.png", width=400)
    except:
        st.write("")

st.markdown("<h2 style='text-align:center; color:#0e7a3d;'>VOLONTARIATO<br>Sezione di Varese</h2>", unsafe_allow_html=True)

if "dati" not in st.session_state:
    st.session_state.dati = []

with st.form("form"):
    nome = st.text_input("Nome e Cognome *")
    assoc = st.text_input("Associazione *")
    cell = st.text_input("Cellulare *")
    ruolo = st.selectbox("Ruolo *", ["Volontario", "Caposquadra", "Coordinatore", "Autista", "Radio", "Telecomunicazioni", "Logistica", "Segreteria", "Sanitario", "Altro"])
    st.divider()
    comune = st.text_input("Comune *")
    via = st.text_input("Via / Localita")
    cc1, cc2 = st.columns(2)
    with cc1:
        lat_txt = st.text_input("Lat", placeholder="es. 45.123456")
    with cc2:
        lon_txt = st.text_input("Log", placeholder="es. 8.123456")
    submitted = st.form_submit_button("✅ Salva", use_container_width=True)
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

if st.session_state.dati:
    df = pd.DataFrame(st.session_state.dati)
    st.divider()
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.divider()
    st.markdown("### Mappa - Tutti i marker")
    if "Lat" in df.columns:
        df_map = df.rename(columns={"Lat": "lat", "Log": "lon"})
        df_map = df_map[(df_map["lat"] != 0) & (df_map["lon"] != 0)]
        if not df_map.empty:
            st.map(df_map, latitude="lat", longitude="lon", zoom=10)
        else:
            st.info("Inserisci Lat e Log - nessun default Varese")
    output = BytesIO()
    df.to_excel(output, index=False, engine="openpyxl")
    st.download_button("📥 Scarica Excel", output.getvalue(), file_name="associazioni.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)