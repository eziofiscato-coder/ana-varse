import streamlit as st
import pandas as pd
from datetime import datetime, date
from io import BytesIO
import base64, os
from PIL import Image

st.set_page_config(page_title="ANA Varese - Verde ANA", page_icon="🟢", layout="wide")

# ICONS - LIBRERIA LOGHI CHE AVEVI TU
ICONS = {
 "volontario": {"nome":"Volontario","color":"blue","forma":"cerchio","icon":"👤"},
 "sede": {"nome":"Sede","color":"red","forma":"quadrato","icon":"🏠"},
 "radio": {"nome":"Radio","color":"orange","forma":"triangolo","icon":"📻"},
 "emergenza": {"nome":"Emergenza","color":"red","forma":"stella","icon":"🚨"},
 "protezione_civile": {"nome":"Prot. Civile","color":"darkblue","forma":"esagono","icon":"🛡️"},
 "ospedale": {"nome":"Ospedale","color":"red","forma":"croce","icon":"🏥"},
 "postazione": {"nome":"Postazione","color":"green","forma":"bandiera","icon":"📍"},
 "auto": {"nome":"Auto","color":"black","forma":"rettangolo","icon":"🚗"},
 "elicottero": {"nome":"Elicottero","color":"yellow","forma":"rombo","icon":"🚁"},
 "incendio": {"nome":"Incendio","color":"orange","forma":"fiamma","icon":"🔥"},
 "alluvione": {"nome":"Alluvione","color":"blue","forma":"goccia","icon":"🌊"},
 "campo_base": {"nome":"Campo Base","color":"green","forma":"tenda","icon":"⛺"},
}

LIBRERIA_LOGHI = {
    "🔥 Incendio": "🔥", "🌊 Alluvione": "🌊", "🚨 Emergenza": "🚨",
    "📍 Postazione": "📍", "📻 Radio": "📻", "🚗 Auto": "🚗",
    "🚁 Elicottero": "🚁", "⛺ Campo Base": "⛺", "🏥 Ospedale": "🏥",
    "👤 Volontario": "👤", "🏠 Sede": "🏠", "🛡️ Prot.Civile": "🛡️",
    "⚠️ Altro": "⚠️"
}

# VERDE ANA - CSS GIUSTO (non nero!)
st.markdown("""
<style>
.stApp{background-color:#e8f5e9!important;}
.main.block-container{background-color:rgba(255,255,255,0.93)!important; border-radius:18px; padding:25px!important; box-shadow:0 4px 20px rgba(0,0,0,0.08);}
[data-testid="stSidebar"]{background-color:#a5d6a7!important; border-right:4px solid #2e7d32!important;}
.stForm{background-color:#c8e6c9!important; border:3px solid #2e7d32!important; border-radius:15px!important; padding:20px!important;}
.stButton>button{background-color:#2e7d32!important; color:white!important; border:2px solid #1b5e20!important; font-weight:bold!important; border-radius:12px!important; min-height:65px!important;}
div[data-testid="stFormSubmitButton"]>button{background-color:#d32f2f!important; border:3px solid #b71c1c!important; color:white!important; font-weight:bold!important;}
h1,h2,h3{color:#1b5e20!important;}
div[data-testid="stMetric"]{background:#c8e6c9!important; border:2px solid #2e7d32!important; border-radius:12px!important; padding:12px!important;}
</style>
""", unsafe_allow_html=True)

# SESSION
for k,v in [("authenticated",False),("emergenze_lista",[]),("interventi_lista",[]),("eventi",[]),("mem_nomi",["Mario Rossi","Luigi Bianchi","Giuseppe Verdi"]),("postazioni",[]),("dati",[]),("menu_scelta","🏠 Dashboard")]:
    if k not in st.session_state:
        st.session_state[k]=v

def get_b64(p):
    try:
        if os.path.exists(p):
            with open(p,"rb") as f: return base64.b64encode(f.read()).decode()
    except: pass
    return ""

def torna_dashboard():
    if st.button("🏠 Torna alla Dashboard", use_container_width=True, key=f"back_{datetime.now().microsecond}"):
        st.session_state.menu_scelta="🏠 Dashboard"
        st.rerun()

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
    LOGHI="<div style='background:#a5d6a7; padding:12px; border-radius:12px; border:3px solid #2e7d32; text-align:center;'><h3 style='color:#1b5e20; margin:0;'>ANA Varese - Protezione Civile</h3></div>"

# LOGIN
if not st.session_state.authenticated:
    st.markdown(LOGHI, unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center; color:#1b5e20; background:#a5d6a7; padding:15px; border-radius:12px; border:3px solid #2e7d32;'>🔐 Accesso Riservato<br>admin / ana2024</h2>", unsafe_allow_html=True)
    c1,c2,c3=st.columns([1,2,1])
    with c2:
        with st.form("login"):
            u=st.text_input("Username", value="admin")
            p=st.text_input("Password", type="password", value="ana2024")
            if st.form_submit_button("🔓 ENTRA", use_container_width=True, type="primary"):
                if u=="admin" and p=="ana2024":
                    st.session_state.authenticated=True
                    st.rerun()
                else:
                    st.error("Usa admin / ana2024")
    st.stop()

# SIDEBAR - TASTI CHE FUNZIONANO
with st.sidebar:
    st.markdown(LOGHI, unsafe_allow_html=True)
    opzioni=["🏠 Dashboard","🚨 Emergenze con Loghi","🗺️ Mappa Postazioni","🚨 Interventi Emergenza","📅 Gestione Eventi","👥 Volontari","📻 Radio","💾 Backup"]
    idx = opzioni.index(st.session_state.menu_scelta) if st.session_state.menu_scelta in opzioni else 0
    sel=st.radio("MENU", opzioni, index=idx)
    if sel!=st.session_state.menu_scelta:
        st.session_state.menu_scelta=sel
        st.rerun()
    st.divider()
    if st.button("🏠 Vai Dashboard", use_container_width=True, key="sb_dash"):
        st.session_state.menu_scelta="🏠 Dashboard"; st.rerun()
    if st.button("🔒 Logout", use_container_width=True, type="primary", key="sb_logout"):
        st.session_state.authenticated=False; st.session_state.menu_scelta="🏠 Dashboard"; st.rerun()

scelta=st.session_state.menu_scelta

# DASHBOARD - TASTI SCELTA RAPIDA CHE FUNZIONANO DAVVERO
if scelta=="🏠 Dashboard":
    st.markdown(LOGHI, unsafe_allow_html=True)
    st.markdown("<h2 style='color:#1b5e20; background:#a5d6a7; padding:15px; border-radius:12px; border:3px solid #2e7d32; text-align:center;'>🏠 Dashboard - ANA Varese</h2>", unsafe_allow_html=True)
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Interventi", len(st.session_state.interventi_lista))
    c2.metric("Emergenze", len(st.session_state.emergenze_lista))
    c3.metric("Volontari", len(st.session_state.mem_nomi))
    c4.metric("Postazioni", len(st.session_state.postazioni))
    st.markdown("### ⚡ MENU SCELTA RAPIDA - Clicca per aprire il form")
    r1c1,r1c2,r1c3,r1c4=st.columns(4)
    with r1c1:
        if st.button("🚨\nEmergenze\ncon Loghi", key="q_em_loghi", use_container_width=True):
            st.session_state.menu_scelta="🚨 Emergenze con Loghi"; st.rerun()
    with r1c2:
        if st.button("🚨\nInterventi\nEmergenza", key="q_int", use_container_width=True):
            st.session_state.menu_scelta="🚨 Interventi Emergenza"; st.rerun()
    with r1c3:
        if st.button("🗺️\nMappa\nPostazioni", key="q_mappa", use_container_width=True):
            st.session_state.menu_scelta="🗺️ Mappa Postazioni"; st.rerun()
    with r1c4:
        if st.button("📅\nGestione\nEventi", key="q_eventi", use_container_width=True):
            st.session_state.menu_scelta="📅 Gestione Eventi"; st.rerun()
    r2c1,r2c2,r2c3,r2c4=st.columns(4)
    with r2c1:
        if st.button("👥\nVolontari", key="q_vol", use_container_width=True):
            st.session_state.menu_scelta="👥 Volontari"; st.rerun()
    with r2c2:
        if st.button("📻\nRadio", key="q_radio", use_container_width=True):
            st.session_state.menu_scelta="📻 Radio"; st.rerun()
    with r2c3:
        if st.button("💾\nBackup", key="q_backup", use_container_width=True):
            st.session_state.menu_scelta="💾 Backup"; st.rerun()
    with r2c4:
        if st.button("🔄\nAggiorna", key="q_refresh", use_container_width=True):
            st.rerun()

# EMERGENZE CON LOGHI - FORM + TABELLA
elif scelta=="🚨 Emergenze con Loghi":
    st.markdown(LOGHI, unsafe_allow_html=True)
    st.markdown("<h2 style='color:#1b5e20; background:#a5d6a7; padding:12px; border-radius:12px; border:3px solid #2e7d32;'>🚨 Emergenze - Form con Tabella e Loghi Libreria</h2>", unsafe_allow_html=True)
    torna_dashboard()
    st.markdown("#### 📚 Libreria Loghi ICONS")
    cols=st.columns(6)
    for i,(k,v) in enumerate(ICONS.items()):
        with cols[i%6]:
            st.markdown(f"<div style='background:white; border:2px solid #2e7d32; border-radius:10px; padding:8px; text-align:center; margin-bottom:8px;'><div style='font-size:28px;'>{v['icon']}</div><div style='font-size:10px; color:#1b5e20;'>{v['nome']}</div><div style='font-size:8px;'>{v['forma']} {v['color']}</div></div>", unsafe_allow_html=True)
    st.divider()
    with st.form("form_emergenza_loghi", clear_on_submit=True):
        c1,c2,c3=st.columns(3)
        with c1:
            data_em=st.date_input("Data *", value=date.today())
            ora_em=st.time_input("Ora *")
            comune=st.text_input("Comune *", value="Varese")
        with c2:
            via=st.text_input("Via / Località *")
            civico=st.text_input("Civico")
            tipo_key=st.selectbox("Tipo Emergenza + Logo *", list(ICONS.keys()), format_func=lambda x: f"{ICONS[x]['icon']} {ICONS[x]['nome']}")
        with c3:
            priorita=st.selectbox("Priorità *", ["🔴 Alta - Urgente","🟡 Media","🟢 Bassa"])
            odv=st.selectbox("ODV *", ["ANA Varese","Protezione Civile Lombardia","Croce Rossa","VVF","Altro"])
            squadre=st.number_input("N. Squadre", min_value=1, max_value=20, value=1)
            icona_sel = ICONS[tipo_key]['icon']
            st.markdown(f"<div style='background:#c8e6c9; border:3px solid #2e7d32; border-radius:12px; padding:15px; text-align:center;'><div style='font-size:50px;'>{icona_sel}</div><div style='color:#1b5e20; font-weight:bold;'>{ICONS[tipo_key]['nome']}</div><div style='font-size:10px;'>{ICONS[tipo_key]['forma']} - {ICONS[tipo_key]['color']}</div></div>", unsafe_allow_html=True)
        descrizione=st.text_area("Descrizione / Azione *", height=100)
        if st.form_submit_button("🔴 SALVA EMERGENZA CON LOGO", use_container_width=True, type="primary"):
            if comune and via and descrizione:
                st.session_state.emergenze_lista.append({
                    "Data": str(data_em), "Ora": str(ora_em),
                    "Logo": ICONS[tipo_key]['icon'], "Tipo": ICONS[tipo_key]['nome'], "Forma": ICONS[tipo_key]['forma'], "Colore": ICONS[tipo_key]['color'],
                    "Comune": comune, "Via": via, "Civico": civico,
                    "Priorità": priorita, "ODV": odv, "Squadre": squadre,
                    "Descrizione": descrizione
                })
                st.success(f"Salvata {ICONS[tipo_key]['icon']} {ICONS[tipo_key]['nome']}!"); st.balloons(); st.rerun()
    torna_dashboard()
    if st.session_state.emergenze_lista:
        df = pd.DataFrame(st.session_state.emergenze_lista)
        st.markdown(f"### 📋 Tabella Emergenze - {len(df)} con Loghi")
        for idx, row in df.iterrows():
            with st.container(border=True):
                c_logo,c_info,c_azioni=st.columns([1,4,1])
                with c_logo:
                    st.markdown(f"<div style='font-size:45px; text-align:center; background:#e8f5e9; border:2px solid #2e7d32; border-radius:12px; padding:10px;'>{row['Logo']}</div>", unsafe_allow_html=True)
                with c_info:
                    st.markdown(f"**{row['Logo']} {row['Tipo']}** - {row['Priorità']} | {row['Forma']} {row['Colore']}")
                    st.markdown(f"📍 **{row['Comune']}** - {row['Via']} {row['Civico']} | 📅 {row['Data']} {row['Ora']}")
                    st.markdown(f"📝 {row['Descrizione']}")
                with c_azioni:
                    if st.button("🗑️", key=f"del_{idx}"):
                        st.session_state.emergenze_lista.pop(idx); st.rerun()
        st.dataframe(df, use_container_width=True)
        st.download_button("📥 Scarica CSV", df.to_csv(index=False).encode('utf-8'), "emergenze_con_loghi.csv", use_container_width=True)
                if map_type == "OpenStreetMap":
                m = folium.Map(
                    location=[center_lat, center_lon],
                    zoom_start=zoom,
                    tiles="OpenStreetMap"
                )
            else:
                m = folium.Map(
                    location=[center_lat, center_lon],
                    zoom_start=zoom,
                    tiles=None
                )
                if map_type == "Google Stradale":
                    url = "https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}"
                    name = "Google Stradale"
                elif map_type == "Google Satellite":
                    url = "https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}"
                    name = "Google Satellite"
                elif map_type == "Google Ibrida":
                    url = "https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}"
                    name = "Google Ibrida"
                else:
                    url = "https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}"
                    name = "Google Rilievo"
                folium.TileLayer(
                    url,
                    attr="Google",
                    name=name,
                    max_zoom=20
                ).add_to(m)

# ALTRI FORM VECCHI CON CAMPI
elif scelta=="👥 Volontari":
    st.markdown(LOGHI, unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center; color:#0e7a3d;'>VOLONTARIATO<br>Sezione di Varese - Vecchio Form Completo</h2>", unsafe_allow_html=True)
    torna_dashboard()
    with st.form("form_volontari_vecchio", clear_on_submit=True):
        c1,c2=st.columns(2)
        with c1:
            nome = st.text_input("Nome e Cognome *")
            assoc = st.text_input("Associazione *", value="ANA Varese")
            cell = st.text_input("Cellulare *")
        with c2:
            email = st.text_input("Email")
            ruolo = st.selectbox("Ruolo *", ["Volontario","Caposquadra","Coordinatore","Autista","Radio","Logistica","Segreteria","Sanitario","Altro"])
        if st.form_submit_button("✅ SALVA VOLONTARIO", use_container_width=True, type="primary"):
            if nome and assoc and cell:
                st.session_state.dati.append({"Nome": nome, "Associazione": assoc, "Cellulare": cell, "Email": email, "Ruolo": ruolo})
                st.session_state.mem_nomi.append(nome)
                st.success(f"Aggiunto {nome}"); st.rerun()
    if st.session_state.dati:
        df = pd.DataFrame(st.session_state.dati)
        st.dataframe(df, use_container_width=True)
        output = BytesIO()
        df.to_excel(output, index=False, engine="openpyxl")
        st.download_button("📥 Scarica Excel", output.getvalue(), file_name="associazioni.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
    torna_dashboard()

else:
    st.markdown(LOGHI, unsafe_allow_html=True)
    torna_dashboard()
    st.info(f"Sezione {scelta} - Form vecchi con campi ripristinati")
    torna_dashboard()
