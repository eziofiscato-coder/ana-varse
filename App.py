import streamlit as st
import pandas as pd
from datetime import datetime, date
from io import BytesIO
import base64, os

st.set_page_config(page_title="ANA Varese - Verde ANA", page_icon="🟢", layout="wide")

# VERDE ANA OVUNQUE - SU TUTTI I FORM E PAGINE
st.markdown("""
<style>
.stApp{background-color:#e8f5e9!important;}
.main.block-container{max-width:100%!important; padding:1% 2%!important;}
[data-testid="stSidebar"]{background-color:#a5d6a7!important; border-right:4px solid #2e7d32!important;}
.stForm{background-color:#c8e6c9!important; border:3px solid #2e7d32!important; border-radius:15px!important; padding:20px!important;}
[data-testid="stDataFrame"]{background-color:white!important; border:2px solid #2e7d32!important; border-radius:10px!important;}
.stButton>button{background-color:#2e7d32!important; color:white!important; border:2px solid #1b5e20!important; font-weight:bold!important; border-radius:12px!important; min-height:55px!important;}
.stButton>button:hover{background-color:#1b5e20!important;}
div[data-testid="stFormSubmitButton"]>button{background-color:#d32f2f!important; color:white!important; border:3px solid #b71c1c!important;}
.stDownloadButton>button{background-color:#2e7d32!important; color:white!important;}
h1,h2,h3{color:#1b5e20!important;}
div[data-testid="stMetric"]{background:#c8e6c9!important; border:2px solid #2e7d32!important; border-radius:12px!important; padding:12px!important;}
</style>
""", unsafe_allow_html=True)

# SESSION
for k,v in [("authenticated",False),("interventi_lista",[]),("eventi",[]),("mem_nomi",["Mario Rossi","Luigi Bianchi","Giuseppe Verdi"]),("postazioni",[]),("menu_scelta","🏠 Dashboard"),("volontari_full",[])]:
    if k not in st.session_state:
        st.session_state[k]=v

def get_b64(p):
    try:
        if os.path.exists(p):
            with open(p,"rb") as f:
                return base64.b64encode(f.read()).decode()
    except: pass
    return ""

b64_vol=get_b64("logo_volontariato_varese.jpg")
b64_ana=get_b64("logo_ana_varese.jpg")
b64_pc=get_b64("logo_protezione_civile_lombardia.jpg")

if b64_vol and b64_ana and b64_pc:
    LOGHI=f"""<div style='display:flex; justify-content:center; align-items:center; gap:25px; background:#a5d6a7; padding:15px; border-radius:15px; border:3px solid #2e7d32; margin-bottom:15px;'>
      <img src='data:image/jpeg;base64,{b64_vol}' style='width:80px; height:80px; border-radius:50%; border:3px solid #1b5e20; background:white; object-fit:cover;'>
      <img src='data:image/jpeg;base64,{b64_ana}' style='width:90px; height:90px; border-radius:50%; border:4px solid #1b5e20; background:white; object-fit:cover;'>
      <img src='data:image/jpeg;base64,{b64_pc}' style='width:80px; height:80px; border-radius:50%; border:3px solid #2e7d32; background:white; object-fit:cover;'>
    </div>"""
else:
    LOGHI="<div style='background:#a5d6a7; padding:12px; border-radius:12px; border:3px solid #2e7d32; text-align:center;'><h3 style='color:#1b5e20; margin:0;'>🟢 ANA Varese - Protezione Civile</h3></div>"

def btn_torna_dashboard():
    if st.button("🏠 Torna alla Dashboard", use_container_width=True, key=f"back_{datetime.now().microsecond}"):
        st.session_state.menu_scelta="🏠 Dashboard"
        st.rerun()

# LOGIN CON PSW
if not st.session_state.authenticated:
    st.markdown(LOGHI, unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center; color:#1b5e20; background:#a5d6a7; padding:15px; border-radius:12px; border:3px solid #2e7d32;'>🔐 Accesso Riservato - ANA Varese</h2>", unsafe_allow_html=True)
    c1,c2,c3=st.columns([1,2,1])
    with c2:
        with st.form("login_form"):
            user=st.text_input("Username")
            psw=st.text_input("Password", type="password")
            if st.form_submit_button("🔓 ENTRA", use_container_width=True, type="primary"):
                if user=="admin" and psw=="ana2024":
                    st.session_state.authenticated=True
                    st.rerun()
                else:
                    st.error("Errati! Usa admin / ana2024")
    st.stop()

# SIDEBAR
with st.sidebar:
    st.markdown(LOGHI, unsafe_allow_html=True)
    opzioni=["🏠 Dashboard","🗺️ Mappa Postazioni","🚨 Interventi Emergenza","📅 Gestione Eventi","👥 Volontari","📻 Radio","💾 Backup"]
    idx = opzioni.index(st.session_state.menu_scelta) if st.session_state.menu_scelta in opzioni else 0
    scelta_radio=st.radio("MENU PRINCIPALE", opzioni, index=idx, key="menu_radio_main")
    if scelta_radio!=st.session_state.menu_scelta:
        st.session_state.menu_scelta=scelta_radio
        st.rerun()
    st.divider()
    if st.button("🏠 Vai Dashboard", use_container_width=True, key="sb_dash"):
        st.session_state.menu_scelta="🏠 Dashboard"; st.rerun()
    if st.button("🔒 Logout", use_container_width=True, type="primary", key="sb_logout"):
        st.session_state.authenticated=False; st.rerun()

scelta=st.session_state.menu_scelta

# DASHBOARD
if scelta=="🏠 Dashboard":
    st.markdown(LOGHI, unsafe_allow_html=True)
    st.markdown("<h2 style='color:#1b5e20; background:#a5d6a7; padding:15px; border-radius:12px; border:3px solid #2e7d32; text-align:center;'>🏠 Dashboard - ANA Varese</h2>", unsafe_allow_html=True)
    c1,c2,c3,c4=st.columns(4)
    c1.metric("🚨 Interventi", len(st.session_state.interventi_lista))
    c2.metric("📅 Eventi", len(st.session_state.eventi))
    c3.metric("👥 Volontari", len(st.session_state.mem_nomi))
    c4.metric("📍 Postazioni", len(st.session_state.postazioni))
    st.markdown("### ⚡ MENU SCELTA RAPIDA - Clicca per aprire")
    r1c1,r1c2,r1c3,r1c4=st.columns(4)
    with r1c1:
        if st.button("🚨\nInterventi\nEmergenza", key="q_int", use_container_width=True):
            st.session_state.menu_scelta="🚨 Interventi Emergenza"; st.rerun()
    with r1c2:
        if st.button("🗺️\nMappa\nPostazioni", key="q_mappa", use_container_width=True):
            st.session_state.menu_scelta="🗺️ Mappa Postazioni"; st.rerun()
    with r1c3:
        if st.button("📅\nGestione\nEventi", key="q_eventi", use_container_width=True):
            st.session_state.menu_scelta="📅 Gestione Eventi"; st.rerun()
    with r1c4:
        if st.button("👥\nVolontari", key="q_vol", use_container_width=True):
            st.session_state.menu_scelta="👥 Volontari"; st.rerun()
    r2c1,r2c2,r2c3,r2c4=st.columns(4)
    with r2c1:
        if st.button("📻\nRadio", key="q_radio", use_container_width=True):
            st.session_state.menu_scelta="📻 Radio"; st.rerun()
    with r2c2:
        if st.button("💾\nBackup", key="q_backup", use_container_width=True):
            st.session_state.menu_scelta="💾 Backup"; st.rerun()
    with r2c3:
        if st.button("🔄\nAggiorna", key="q_refresh", use_container_width=True):
            st.rerun()
    with r2c4:
        if st.button("🔒\nLogout", key="q_logout", use_container_width=True, type="primary"):
            st.session_state.authenticated=False; st.rerun()

# MAPPA
elif scelta=="🗺️ Mappa Postazioni":
    st.markdown(LOGHI, unsafe_allow_html=True)
    st.markdown("<h2 style='color:#1b5e20; background:#a5d6a7; padding:12px; border-radius:12px; border:3px solid #2e7d32;'>🗺️ Mappa Postazioni</h2>", unsafe_allow_html=True)
    btn_torna_dashboard()
    with st.expander("🔗 COLLEGA MAPPOINT", expanded=False):
        up_mp = st.file_uploader("Carica MapPoint", type=["csv","xlsx","xls"], key="mappoint")
        if up_mp:
            try:
                df_mp = pd.read_csv(up_mp) if up_mp.name.endswith(".csv") else pd.read_excel(up_mp)
                st.dataframe(df_mp.head(), use_container_width=True)
                cols = df_mp.columns.tolist()
                c1,c2,c3=st.columns(3)
                with c1: lat_col = st.selectbox("Lat", cols, key="mp_lat")
                with c2: lon_col = st.selectbox("Lon", cols, key="mp_lon")
                with c3: nome_col = st.selectbox("Nome", cols, key="mp_nome")
                if st.button("📥 IMPORTA DA MAPPOINT", use_container_width=True, type="primary"):
                    cnt=0
                    for _, row in df_mp.iterrows():
                        try:
                            lat=float(str(row[lat_col]).replace(",",".")); lon=float(str(row[lon_col]).replace(",","."))
                            st.session_state.postazioni.append({"Postazione":str(row[nome_col]),"Latitudine":str(lat),"Longitudine":str(lon),"Data":str(date.today()),"Fonte":"MapPoint"})
                            cnt+=1
                        except: pass
                    st.success(f"Importate {cnt}!"); st.rerun()
            except Exception as e:
                st.error(f"Errore: {e}")
    with st.form("post_form", clear_on_submit=True):
        c1,c2=st.columns(2)
        with c1:
            nome=st.text_input("Nome Postazione *")
            comune=st.text_input("Comune *", value="Varese")
        with c2:
            lat=st.text_input("Latitudine *", placeholder="45.8205")
            lon=st.text_input("Longitudine *", placeholder="8.8255")
        if st.form_submit_button("🔴 SALVA POSTAZIONE", use_container_width=True, type="primary"):
            if nome and lat and lon:
                try:
                    float(lat); float(lon)
                    st.session_state.postazioni.append({"Postazione":nome,"Comune":comune,"Latitudine":lat,"Longitudine":lon,"Data":str(date.today())})
                    st.success(f"Salvata {nome}!"); st.rerun()
                except: st.error("Lat/Lon numeri")
    btn_torna_dashboard()
    if st.session_state.postazioni:
        df_post=pd.DataFrame(st.session_state.postazioni)
        try:
            df_map=df_post.copy()
            df_map["lat"]=pd.to_numeric(df_map["Latitudine"], errors='coerce')
            df_map["lon"]=pd.to_numeric(df_map["Longitudine"], errors='coerce')
            df_map=df_map.dropna(subset=["lat","lon"])
            if not df_map.empty: st.map(df_map[["lat","lon"]], zoom=11, use_container_width=True)
        except: pass
        for _, row in df_post.iterrows():
            lat=row.get("Latitudine",""); lon=row.get("Longitudine",""); nome=row.get("Postazione","")
            st.markdown(f"**📍 {nome}** - {lat},{lon}")
            c1,c2,c3=st.columns(3)
            with c1: st.link_button("Google Maps", f"https://www.google.com/maps/search/?api=1&query={lat},{lon}", use_container_width=True)
            with c2: st.link_button("OSM", f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=16/{lat}/{lon}", use_container_width=True)
            with c3: st.link_button("Waze", f"https://waze.com/ul?ll={lat},{lon}&navigate=yes", use_container_width=True)
    btn_torna_dashboard()

# INTERVENTI
elif scelta=="🚨 Interventi Emergenza":
    st.markdown(LOGHI, unsafe_allow_html=True)
    st.markdown("<h2 style='color:#1b5e20; background:#a5d6a7; padding:12px; border-radius:12px; border:3px solid #2e7d32;'>🚨 Interventi Emergenza</h2>", unsafe_allow_html=True)
    btn_torna_dashboard()
    with st.form("form_emergenza", clear_on_submit=True):
        c1,c2,c3=st.columns(3)
        with c1:
            data_int=st.date_input("Data *")
            ora_int=st.time_input("Ora *")
        with c2:
            comune_int=st.text_input("Comune *")
            via_int=st.text_input("Via *")
        with c3:
            civico_int=st.text_input("Civico")
            odv_int=st.selectbox("ODV *", ["ANA Varese","Protezione Civile Lombardia","Croce Rossa","Altro"])
        azione_int=st.text_area("Azione *", height=100)
        if st.form_submit_button("🔴 SALVA INTERVENTO", use_container_width=True, type="primary"):
            if comune_int and via_int and azione_int:
                st.session_state.interventi_lista.append({"Data":str(data_int),"Ora":str(ora_int),"Comune":comune_int,"Via":via_int,"Civico":civico_int,"ODV":odv_int,"Azione":azione_int})
                st.success("Salvato!"); st.rerun()
    btn_torna_dashboard()

# ALTRI FORM...
elif scelta=="📅 Gestione Eventi":
    st.markdown(LOGHI, unsafe_allow_html=True)
    btn_torna_dashboard()
    with st.form("ev_form", clear_on_submit=True):
        titolo=st.text_input("Titolo *")
        if st.form_submit_button("🔴 SALVA", use_container_width=True, type="primary"):
            if titolo:
                st.session_state.eventi.append({"Titolo":titolo,"Data":str(date.today())}); st.success("Salvato!"); st.rerun()
    btn_torna_dashboard()

elif scelta=="👥 Volontari":
    st.markdown(LOGHI, unsafe_allow_html=True)
    btn_torna_dashboard()
    with st.form("vol_form", clear_on_submit=True):
        nome=st.text_input("Nome *")
        if st.form_submit_button("🔴 SALVA", use_container_width=True, type="primary"):
            if nome:
                st.session_state.mem_nomi.append(nome); st.success(f"Aggiunto {nome}"); st.rerun()
    btn_torna_dashboard()

else:
    st.markdown(LOGHI, unsafe_allow_html=True)
    btn_torna_dashboard()
    st.info(f"Sezione {scelta} - Verde ANA")
    btn_torna_dashboard()

 
  
 
  

 
   
   
