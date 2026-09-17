import streamlit as st
import pandas as pd
from datetime import datetime, date
import base64, os

st.set_page_config(page_title="ANA Varese - Verde ANA", page_icon="🟢", layout="wide")

st.markdown("""
<style>
.stApp{background-color:#e8f5e9!important;}
[data-testid="stSidebar"]{background-color:#a5d6a7!important; border-right:4px solid #2e7d32!important;}
.stForm{background-color:#c8e6c9!important; border:3px solid #2e7d32!important; border-radius:15px!important; padding:20px!important;}
.stButton>button{background-color:#2e7d32!important; color:white!important; border:2px solid #1b5e20!important; font-weight:bold!important; border-radius:12px!important; min-height:55px!important;}
div[data-testid="stFormSubmitButton"]>button{background-color:#d32f2f!important; border:3px solid #b71c1c!important;}
h1,h2,h3{color:#1b5e20!important;}
div[data-testid="stMetric"]{background:#c8e6c9!important; border:2px solid #2e7d32!important; border-radius:12px!important; padding:12px!important;}
</style>
""", unsafe_allow_html=True)

LIBRERIA_LOGHI = {
    "🔥 Incendio Boschivo": "🔥", "🏠 Incendio Urbano": "🏠🔥", "🌊 Alluvione": "🌊",
    "⛰️ Frana": "⛰️", "❄️ Neve": "❄️", "🚗 Incidente": "🚗💥",
    "🚑 Sanitario": "🚑", "🚒 VVF": "🚒", "🌳 Albero": "🌳",
    "📦 Logistico": "📦", "👥 Popolazione": "👥", "📍 Postazione": "📍", "⚠️ Altro": "⚠️"
}

for k,v in [("authenticated",False),("emergenze",[]),("interventi",[]),("postazioni",[]),("volontari",["Mario Rossi","Luigi Bianchi","Giuseppe Verdi"]),("menu","🏠 Dashboard")]:
    if k not in st.session_state:
        st.session_state[k]=v

def get_b64(p):
    try:
        if os.path.exists(p):
            with open(p,"rb") as f: return base64.b64encode(f.read()).decode()
    except: pass
    return ""

b64_vol=get_b64("logo_volontariato_varese.jpg")
b64_ana=get_b64("logo_ana_varese.jpg")
b64_pc=get_b64("logo_protezione_civile_lombardia.jpg")
if b64_vol and b64_ana and b64_pc:
    LOGHI=f"""<div style='display:flex; justify-content:center; gap:25px; background:#a5d6a7; padding:15px; border-radius:15px; border:3px solid #2e7d32; margin-bottom:15px;'>
      <img src='data:image/jpeg;base64,{b64_vol}' style='width:80px; height:80px; border-radius:50%; border:3px solid #1b5e20; background:white; object-fit:cover;'>
      <img src='data:image/jpeg;base64,{b64_ana}' style='width:90px; height:90px; border-radius:50%; border:4px solid #1b5e20; background:white; object-fit:cover;'>
      <img src='data:image/jpeg;base64,{b64_pc}' style='width:80px; height:80px; border-radius:50%; border:3px solid #2e7d32; background:white; object-fit:cover;'>
    </div>"""
else:
    LOGHI="<div style='background:#a5d6a7; padding:12px; border-radius:12px; border:3px solid #2e7d32; text-align:center;'><h3 style='color:#1b5e20; margin:0;'>🟢 ANA Varese</h3></div>"

def btn_back():
    if st.button("🏠 Torna alla Dashboard", use_container_width=True, key=f"back_{datetime.now().microsecond}"):
        st.session_state.menu="🏠 Dashboard"; st.rerun()

if not st.session_state.authenticated:
    st.markdown(LOGHI, unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center; color:#1b5e20; background:#a5d6a7; padding:15px; border-radius:12px; border:3px solid #2e7d32;'>🔐 Accesso Riservato - admin / ana2024</h2>", unsafe_allow_html=True)
    c1,c2,c3=st.columns([1,2,1])
    with c2:
        with st.form("login"):
            u=st.text_input("Username"); p=st.text_input("Password", type="password")
            if st.form_submit_button("🔓 ENTRA", use_container_width=True, type="primary"):
                if u=="admin" and p=="ana2024":
                    st.session_state.authenticated=True; st.rerun()
                else: st.error("Usa admin / ana2024")
    st.stop()

with st.sidebar:
    st.markdown(LOGHI, unsafe_allow_html=True)
    opzioni=["🏠 Dashboard","🚨 Emergenze con Loghi","🗺️ Mappa Postazioni","🚨 Interventi","👥 Volontari","💾 Backup"]
    idx=opzioni.index(st.session_state.menu) if st.session_state.menu in opzioni else 0
    sel=st.radio("MENU", opzioni, index=idx)
    if sel!=st.session_state.menu:
        st.session_state.menu=sel; st.rerun()
    st.divider()
    if st.button("🏠 Vai Dashboard", use_container_width=True):
        st.session_state.menu="🏠 Dashboard"; st.rerun()
    if st.button("🔒 Logout", use_container_width=True, type="primary"):
        st.session_state.authenticated=False; st.rerun()

if st.session_state.menu=="🏠 Dashboard":
    st.markdown(LOGHI, unsafe_allow_html=True)
    st.markdown("<h2 style='color:#1b5e20; background:#a5d6a7; padding:15px; border-radius:12px; border:3px solid #2e7d32; text-align:center;'>🏠 Dashboard - ANA Varese</h2>", unsafe_allow_html=True)
    c1,c2,c3,c4=st.columns(4)
    c1.metric("🚨 Emergenze", len(st.session_state.emergenze))
    c2.metric("📍 Postazioni", len(st.session_state.postazioni))
    c3.metric("👥 Volontari", len(st.session_state.volontari))
    c4.metric("🚨 Interventi", len(st.session_state.interventi))
    st.markdown("### ⚡ MENU SCELTA RAPIDA")
    r1c1,r1c2,r1c3,r1c4=st.columns(4)
    with r1c1:
        if st.button("🚨\nEmergenze\ncon Loghi", key="q1", use_container_width=True):
            st.session_state.menu="🚨 Emergenze con Loghi"; st.rerun()
    with r1c2:
        if st.button("🗺️\nMappa", key="q2", use_container_width=True):
            st.session_state.menu="🗺️ Mappa Postazioni"; st.rerun()
    with r1c3:
        if st.button("🚨\nInterventi", key="q3", use_container_width=True):
            st.session_state.menu="🚨 Interventi"; st.rerun()
    with r1c4:
        if st.button("🔒\nLogout", key="q4", use_container_width=True, type="primary"):
            st.session_state.authenticated=False; st.rerun()

elif st.session_state.menu=="🚨 Emergenze con Loghi":
    st.markdown(LOGHI, unsafe_allow_html=True)
    st.markdown("<h2 style='color:#1b5e20; background:#a5d6a7; padding:12px; border-radius:12px; border:3px solid #2e7d32;'>🚨 Form + Tabella Emergenze con Loghi</h2>", unsafe_allow_html=True)
    btn_back()
    st.markdown("#### 📚 Libreria Loghi")
    cols=st.columns(6)
    for i,(nome,icona) in enumerate(LIBRERIA_LOGHI.items()):
        with cols[i%6]:
            st.markdown(f"<div style='background:white; border:2px solid #2e7d32; border-radius:10px; padding:6px; text-align:center; margin-bottom:6px;'><div style='font-size:24px;'>{icona}</div><div style='font-size:8px;'>{nome[:14]}</div></div>", unsafe_allow_html=True)
    st.divider()
    with st.form("form_em", clear_on_submit=True):
        c1,c2,c3=st.columns(3)
        with c1:
            data_e=st.date_input("Data *", value=date.today()); comune=st.text_input("Comune *", value="Varese")
        with c2:
            via=st.text_input("Via *"); tipo=st.selectbox("Tipo + Logo *", list(LIBRERIA_LOGHI.keys()))
        with c3:
            odv=st.selectbox("ODV", ["ANA Varese","Prot.Civile","Altro"])
            st.markdown(f"<div style='background:#c8e6c9; border:3px solid #2e7d32; border-radius:12px; padding:10px; text-align:center;'><div style='font-size:40px;'>{LIBRERIA_LOGHI[tipo]}</div><b>{tipo}</b></div>", unsafe_allow_html=True)
        desc=st.text_area("Descrizione *", height=80)
        if st.form_submit_button("🔴 SALVA CON LOGO", use_container_width=True, type="primary"):
            if comune and via and desc:
                st.session_state.emergenze.append({"Data":str(data_e),"Logo":LIBRERIA_LOGHI[tipo],"Tipo":tipo,"Comune":comune,"Via":via,"ODV":odv,"Descrizione":desc})
                st.success(f"Salvata {LIBRERIA_LOGHI[tipo]} {tipo}!"); st.rerun()
    btn_back()
    if st.session_state.emergenze:
        df=pd.DataFrame(st.session_state.emergenze)
        st.markdown(f"### 📋 Tabella {len(df)} Emergenze")
        for idx,row in df.iterrows():
            with st.container(border=True):
                cL,cI=st.columns([1,4])
                with cL: st.markdown(f"<div style='font-size:45px; text-align:center; background:#e8f5e9; border:2px solid #2e7d32; border-radius:12px; padding:10px;'>{row['Logo']}</div>", unsafe_allow_html=True)
                with cI:
                    st.markdown(f"**{row['Logo']} {row['Tipo']}** | 📍 {row['Comune']} {row['Via']} | 📅 {row['Data']}")
                    st.write(row['Descrizione'])
        st.dataframe(df, use_container_width=True)
        st.download_button("📥 Scarica CSV", df.to_csv(index=False).encode('utf-8'), "emergenze.csv", use_container_width=True)
    btn_back()

elif st.session_state.menu=="🗺️ Mappa Postazioni":
    st.markdown(LOGHI, unsafe_allow_html=True)
    st.markdown("<h2 style='color:#1b5e20; background:#a5d6a7; padding:12px; border-radius:12px; border:3px solid #2e7d32;'>🗺️ Mappa</h2>", unsafe_allow_html=True)
    btn_back()
    with st.form("post", clear_on_submit=True):
        c1,c2=st.columns(2)
        with c1: nome=st.text_input("Nome *");
        with c2: lat=st.text_input("Lat *", placeholder="45.8205"); lon=st.text_input("Lon *", placeholder="8.8255")
        if st.form_submit_button("🔴 SALVA", use_container_width=True, type="primary"):
            if nome and lat and lon:
                st.session_state.postazioni.append({"Postazione":nome,"Latitudine":lat,"Longitudine":lon}); st.success("Salvata!"); st.rerun()
    if st.session_state.postazioni:
        dfp=pd.DataFrame(st.session_state.postazioni)
        try:
            dfm=dfp.copy(); dfm["lat"]=pd.to_numeric(dfm["Latitudine"], errors='coerce'); dfm["lon"]=pd.to_numeric(dfm["Longitudine"], errors='coerce')
            dfm=dfm.dropna(subset=["lat","lon"])
            if not dfm.empty: st.map(dfm[["lat","lon"]], zoom=11)
        except: pass
    btn_back()
else:
    st.markdown(LOGHI, unsafe_allow_html=True)
    btn_back()
    st.info(f"Sezione {st.session_state.menu}")
    btn_back()
