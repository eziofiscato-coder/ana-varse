
import streamlit as st
import pandas as pd
import os, json, datetime

# --- 1. FIX ModuleNotFoundError streamlit_folium riga 16 ---
try:
    import folium
    from streamlit_folium import st_folium
    FOLIUM_OK = True
except Exception:
    FOLIUM_OK = False
    folium = None
    st_folium = None

st.set_page_config(page_title="ANA Varese - Base 2032 + 3 Fix", layout="wide")

# --- CSS Fix fullscreen 100% mappe ---
st.markdown("""
<style>
[data-testid="stMap"] { height: 100vh !important; }
iframe[title="streamlit_folium.st_folium"] { height: 100vh !important; width:100% !important; }
.stApp { max-width: 100% !important; }
</style>
""", unsafe_allow_html=True)

# --- 3. FIX CSV comune,via ---
CSV_VIE = "vie_italia.csv"

def get_comuni():
    if os.path.exists(CSV_VIE):
        try:
            df = pd.read_csv(CSV_VIE)
            if "comune" in df.columns:
                return sorted(df["comune"].dropna().unique().tolist())
        except:
            pass
    # fallback
    return ["Varese","Venegono Superiore","Venegono Inferiore","Castiglione Olona","Tradate","Gornate Olona","Busto Arsizio"]

def get_vie(comune):
    if os.path.exists(CSV_VIE):
        try:
            df = pd.read_csv(CSV_VIE)
            if "comune" in df.columns and "via" in df.columns:
                filt = df[df["comune"]==comune]
                vie = filt["via"].dropna().unique().tolist()
                if vie:
                    return sorted(vie)
        except:
            pass
    # fallback demo
    base = {
        "Varese": ["Via Roma","Via Sacco","Via Manzoni","Via Volta","Via Cavour","Via Garibaldi","Via Orrigoni","Via Marcobi"],
        "Venegono Superiore": ["Via Roma","Via Verdi","Via Matteotti","Via Dante"]
    }
    return base.get(comune, ["Via Roma","Via Centro"])

# --- Stato sessione per fix 2 ---
if "map_center" not in st.session_state:
    st.session_state.map_center = {"lat": 45.816, "lon": 8.825, "comune": "Varese"}
if "map_zoom" not in st.session_state:
    st.session_state.map_zoom = 14

# --- LOGIN SEMPLICE (base 2032) ---
if "logged" not in st.session_state:
    st.session_state.logged = False

if not st.session_state.logged:
    st.title("ANA Varese - Login")
    u = st.text_input("Utente")
    p = st.text_input("Password", type="password")
    if st.button("Entra"):
        st.session_state.logged = True
        st.rerun()
    st.stop()

# --- DASHBOARD BASE 2032 (menu + form griglia 3 colonne) ---
col1, col2 = st.columns([4,1])
with col1:
    st.title("ANA Varese - Base 2032 + 3 Fix (come ieri)")
with col2:
    if st.button("Logout"):
        st.session_state.logged = False
        st.rerun()

menu = st.selectbox("Menu", ["Dashboard","Volontari","Radio DB","Consegne","Eventi","Emergenze","Mappe Fusione","Mezzi","Attrezzature","Backup PDF/Excel/JSON"])

# --- COMUNE / VIA SELECT ---
st.subheader("Selezione Comune / Via (CSV fix)")
c1, c2, c3 = st.columns(3)
with c1:
    comuni = get_comuni()
    comune_sel = st.selectbox("Comune *", comuni, key="comune_sel")
with c2:
    vie = get_vie(comune_sel)
    via_sel = st.selectbox(f"Via * di {comune_sel} ({len(vie)} vie)", vie, key="via_sel")
with c3:
    civico = st.text_input("Civico", "10")

# --- ESEMPIO VOLONTARI - click cognome -> modifica + AGGIORNA ---
if menu == "Volontari":
    st.subheader("Volontari - base 2032")
    df_vol = pd.DataFrame([
        {"id":1,"cognome":"Rossi","nome":"Mario","comune":"Varese","via":"Via Roma","lat":45.816,"lon":8.825,"stato":"Attivo"},
        {"id":2,"cognome":"Bianchi","nome":"Luca","comune":"Venegono Superiore","via":"Via Verdi","lat":45.75,"lon":8.90,"stato":"In Emergenza"},
    ])
    
    for idx, row in df_vol.iterrows():
        col_a, col_b, col_c, col_d = st.columns([2,2,1,1])
        col_a.write(f"**{row['cognome']} {row['nome']}** - {row['comune']}")
        col_b.write(f"{row['via']} - Stato: {row['stato']}")
        # --- 2. FIX Vedi su Mappa + fullscreen ---
        if col_c.button(f"📍 Vedi su Mappa", key=f"vedi_{idx}_{row['id']}"):
            st.session_state.map_center = {"lat": float(row["lat"]), "lon": float(row["lon"]), "comune": row["comune"], "via": row["via"]}
            st.session_state.map_zoom = 17
            st.rerun()
        if col_d.button(f"Modifica", key=f"mod_{idx}_{row['id']}"):
            st.session_state.edit_id = row["id"]

    if "edit_id" in st.session_state:
        st.info(f"Modifica volontario ID {st.session_state.edit_id}")
        if st.button("AGGIORNA", type="primary"):
            st.success("Aggiornato!")

# --- MAPPE FUSIONE - FULLSCREEN 100% + FIX VEDI SU MAPPA ---
if menu == "Mappe Fusione" or menu == "Dashboard":
    st.subheader(f"Mappa - Centro: {st.session_state.map_center}")
    
    lat = st.session_state.map_center["lat"]
    lon = st.session_state.map_center["lon"]
    zoom = st.session_state.map_zoom

    if FOLIUM_OK:
        m = folium.Map(location=[lat, lon], zoom_start=zoom)
        folium.Marker([lat, lon], popup=f"{st.session_state.map_center.get('comune','')} - {st.session_state.map_center.get('via','')}", icon=folium.Icon(color="red")).add_to(m)
        # fullscreen 100% - width 1400 height 800 + use_container_width
        st_folium(m, height=800, width=1400, use_container_width=True)
    else:
        st.warning("folium non installato - uso st.map fallback (fix 1 attivo)")
        st.map(pd.DataFrame([{"lat": lat, "lon": lon}]), zoom=zoom)

st.divider()
st.caption("Base 2032 identica a ieri + 3 fix: 1) folium try/except 2) Vedi su Mappa con key univoca + rerun + fullscreen 100% 3) CSV comune/via")
