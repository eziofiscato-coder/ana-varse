import streamlit as st
import pandas as pd
from datetime import datetime, date
from io import BytesIO
import base64, os

st.set_page_config(page_title="ANA Varese - Emergenze con Loghi", page_icon="🟢", layout="wide")

# VERDE ANA
st.markdown("""
<style>
.stApp{background-color:#e8f5e9!important;}
[data-testid="stSidebar"]{background-color:#a5d6a7!important; border-right:4px solid #2e7d32!important;}
.stForm{background-color:#c8e6c9!important; border:3px solid #2e7d32!important; border-radius:15px!important; padding:20px!important;}
.stButton>button{background-color:#2e7d32!important; color:white!important; border:2px solid #1b5e20!important; font-weight:bold!important; border-radius:12px!important; min-height:55px!important;}
div[data-testid="stFormSubmitButton"]>button{background-color:#d32f2f!important; border:3px solid #b71c1c!important;}
h1,h2,h3{color:#1b5e20!important;}
</style>
""", unsafe_allow_html=True)

for k,v in [("authenticated",False),("emergenze_lista",[]),("menu_scelta","🚨 Emergenze con Loghi")]:
    if k not in st.session_state:
        st.session_state[k]=v

# LIBRERIA 30 LOGHI
LIBRERIA_LOGHI = {
    "🔥 Incendio Boschivo": "🔥",
    "🏠 Incendio Urbano": "🏠🔥",
    "🌊 Alluvione": "🌊",
    "⛰️ Frana": "⛰️",
    "❄️ Neve / Ghiaccio": "❄️",
    "🌪️ Vento Forte": "🌪️",
    "🌧️ Pioggia Intensa": "🌧️",
    "🚗 Incidente Stradale": "🚗💥",
    "🚑 Soccorso Sanitario": "🚑",
    "🚒 VVF": "🚒",
    "🌳 Albero Caduto": "🌳",
    "⚡ Blackout": "⚡",
    "🏚️ Crollo": "🏚️",
    "🛣️ Viabilità": "🛣️",
    "📦 Logistico": "📦",
    "👥 Popolazione": "👥",
    "⛺ Tendopoli": "⛺",
    "🔍 Ricerca Disperso": "🔍",
    "🦺 Presidio": "🦺",
    "📻 Radio": "📻",
    "🚁 Eli-soccorso": "🚁",
    "🧹 Ripristino": "🧹",
    "📍 Postazione": "📍",
    "⚠️ Altro": "⚠️"
}

def btn_back():
    if st.button("🏠 Torna Dashboard", use_container_width=True, key=f"back_{datetime.now().microsecond}"):
        st.session_state.menu_scelta="🏠 Dashboard"; st.rerun()

# LOGIN
if not st.session_state.authenticated:
    st.markdown("<h2 style='text-align:center; color:#1b5e20; background:#a5d6a7; padding:15px; border-radius:12px; border:3px solid #2e7d32;'>🔐 ANA Varese</h2>", unsafe_allow_html=True)
    with st.form("login"):
        u=st.text_input("Username"); p=st.text_input("Password", type="password")
        if st.form_submit_button("ENTRA", use_container_width=True, type="primary"):
            if u=="admin" and p=="ana2024":
                st.session_state.authenticated=True; st.rerun()
            else: st.error("admin / ana2024")
    st.stop()

with st.sidebar:
    sel=st.radio("MENU", ["🏠 Dashboard","🚨 Emergenze con Loghi"], index=1)
    if sel!=st.session_state.menu_scelta:
        st.session_state.menu_scelta=sel; st.rerun()
    if st.button("🔒 Logout", use_container_width=True, type="primary"):
        st.session_state.authenticated=False; st.rerun()

if st.session_state.menu_scelta=="🏠 Dashboard":
    st.markdown("<h2 style='background:#a5d6a7; padding:12px; border-radius:12px; border:3px solid #2e7d32; color:#1b5e20; text-align:center;'>🏠 Dashboard</h2>", unsafe_allow_html=True)
    st.metric("Emergenze", len(st.session_state.emergenze_lista))
    if st.button("🚨 Vai Emergenze con Loghi", use_container_width=True, type="primary"):
        st.session_state.menu_scelta="🚨 Emergenze con Loghi"; st.rerun()

else:
    st.markdown("<h2 style='background:#a5d6a7; padding:12px; border-radius:12px; border:3px solid #2e7d32; color:#1b5e20;'>🚨 Emergenze - Tabella con Loghi Libreria</h2>", unsafe_allow_html=True)
    btn_back()

    st.markdown("### 📚 Libreria Loghi")
    cols=st.columns(6)
    for i,(nome,icona) in enumerate(LIBRERIA_LOGHI.items()):
        with cols[i%6]:
            st.markdown(f"<div style='background:white; border:2px solid #2e7d32; border-radius:10px; padding:8px; text-align:center; margin-bottom:8px;'><div style='font-size:28px;'>{icona}</div><div style='font-size:9px; color:#1b5e20;'>{nome}</div></div>", unsafe_allow_html=True)

    st.divider()
    with st.form("form_em", clear_on_submit=True):
        c1,c2,c3=st.columns(3)
        with c1:
            data_em=st.date_input("Data *", value=date.today()); ora_em=st.time_input("Ora *"); comune=st.text_input("Comune *", value="Varese")
        with c2:
            via=st.text_input("Via *"); tipo=st.selectbox("Tipo + Logo *", list(LIBRERIA_LOGHI.keys())); priorita=st.selectbox("Priorità", ["🔴 Alta","🟡 Media","🟢 Bassa"])
        with c3:
            odv=st.selectbox("ODV", ["ANA Varese","Prot. Civile","CRI","Altro"]); squadre=st.number_input("Squadre",1,20,1)
            icona_sel=LIBRERIA_LOGHI[tipo]
            st.markdown(f"<div style='background:#c8e6c9; border:3px solid #2e7d32; border-radius:12px; padding:10px; text-align:center;'><div style='font-size:40px;'>{icona_sel}</div><b>{tipo}</b></div>", unsafe_allow_html=True)
        desc=st.text_area("Descrizione *", height=80)
        if st.form_submit_button("🔴 SALVA CON LOGO", use_container_width=True, type="primary"):
            if comune and via and desc:
                st.session_state.emergenze_lista.append({"Data":str(data_em),"Ora":str(ora_em),"Logo":LIBRERIA_LOGHI[tipo],"Tipo":tipo,"Comune":comune,"Via":via,"Priorità":priorita,"ODV":odv,"Squadre":squadre,"Descrizione":desc})
                st.success(f"Salvata {LIBRERIA_LOGHI[tipo]} {tipo}!"); st.rerun()

    st.divider()
    if st.session_state.emergenze_lista:
        df=pd.DataFrame(st.session_state.emergenze_lista)
        st.markdown(f"### 📋 Tabella {len(df)} Emergenze con Loghi")
        for idx,row in df.iterrows():
            with st.container(border=True):
                c1,c2,c3=st.columns([1,4,1])
                with c1:
                    st.markdown(f"<div style='font-size:40px; text-align:center; background:#e8f5e9; border:2px solid #2e7d32; border-radius:12px; padding:8px;'>{row['Logo']}</div>", unsafe_allow_html=True)
                with c2:
                    st.markdown(f"**{row['Logo']} {row['Tipo']}** - {row['Priorità']} | 📍 {row['Comune']} - {row['Via']} | 📅 {row['Data']} {row['Ora']}")
                    st.write(row['Descrizione'])
                with c3:
                    if st.button("🗑️", key=f"del_{idx}"):
                        st.session_state.emergenze_lista.pop(idx); st.rerun()
        st.dataframe(df, use_container_width=True)
        st.download_button("📥 Scarica CSV", df.to_csv(index=False).encode('utf-8'), "emergenze.csv", use_container_width=True)
    else:
        st.info("Nessuna emergenza")
    btn_back()
