import streamlit as st
import pandas as pd
from datetime import datetime, date
from io import BytesIO
import base64, os

st.set_page_config(page_title="ANA Varese - Verde ANA", page_icon="🟢", layout="wide")

st.markdown("""
<style>
.stApp{background-color:#e8f5e9!important;}
[data-testid="stSidebar"]{background-color:#a5d6a7!important; border-right:4px solid #2e7d32!important;}
.stForm{background-color:#c8e6c9!important; border:3px solid #2e7d32!important; border-radius:15px!important; padding:20px!important;}
.stButton>button{background-color:#2e7d32!important; color:white!important; border:2px solid #1b5e20!important; font-weight:bold!important; border-radius:12px!important; min-height:65px!important;}
div[data-testid="stFormSubmitButton"]>button{background-color:#d32f2f!important; border:3px solid #b71c1c!important;}
h1,h2,h3{color:#1b5e20!important;}
div[data-testid="stMetric"]{background:#c8e6c9!important; border:2px solid #2e7d32!important; border-radius:12px!important; padding:12px!important;}
</style>
""", unsafe_allow_html=True)

LIBRERIA_LOGHI = {
    "🔥 Incendio Boschivo": "🔥", "🏠 Incendio Urbano": "🏠🔥", "🌊 Alluvione": "🌊",
    "⛰️ Frana": "⛰️", "❄️ Neve / Ghiaccio": "❄️", "🌪️ Vento Forte": "🌪️",
    "🚗 Incidente Stradale": "🚗💥", "🚑 Soccorso Sanitario": "🚑", "🚒 VVF": "🚒",
    "🌳 Albero Caduto": "🌳", "⚡ Blackout": "⚡", "🏚️ Crollo": "🏚️",
    "🛣️ Viabilità": "🛣️", "📦 Logistico": "📦", "👥 Popolazione": "👥",
    "⛺ Tendopoli": "⛺", "🔍 Ricerca Disperso": "🔍", "🦺 Presidio": "🦺",
    "📻 Radio": "📻", "🚁 Eli-soccorso": "🚁", "🧹 Ripristino": "🧹",
    "📍 Postazione": "📍", "⚠️ Altro": "⚠️"
}

for k,v in [("authenticated",False),("emergenze_lista",[]),("interventi_lista",[]),("eventi",[]),("mem_nomi",[]),("dati",[]),("postazioni",[]),("menu_scelta","🏠 Dashboard")]:
    if k not in st.session_state:
        st.session_state[k]=v

def torna_dashboard():
    if st.button("🏠 Torna alla Dashboard", use_container_width=True, key=f"back_{datetime.now().microsecond}"):
        st.session_state.menu_scelta="🏠 Dashboard"
        st.rerun()

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
    LOGHI="<div style='background:#a5d6a7; padding:12px; border-radius:12px; border:3px solid #2e7d32; text-align:center;'><h3 style='color:#1b5e20; margin:0;'>ANA Varese - Protezione Civile</h3></div>"

if not st.session_state.authenticated:
    st.markdown(LOGHI, unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center; color:#1b5e20; background:#a5d6a7; padding:15px; border-radius:12px; border:3px solid #2e7d32;'>🔐 Accesso Riservato<br><small>admin / ana2024</small></h2>", unsafe_allow_html=True)
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

with st.sidebar:
    st.markdown(LOGHI, unsafe_allow_html=True)
    opzioni=["🏠 Dashboard","🚨 Emergenze con Loghi","🗺️ Mappa Postazioni","🚨 Interventi Emergenza","📅 Gestione Eventi","👥 Volontari","📻 Radio","💾 Backup"]
    idx = opzioni.index(st.session_state.menu_scelta) if st.session_state.menu_scelta in opzioni else 0
    sel=st.radio("MENU", opzioni, index=idx, key="menu_radio")
    if sel!=st.session_state.menu_scelta:
        st.session_state.menu_scelta=sel
        st.rerun()
    st.divider()
    if st.button("🏠 Vai Dashboard", use_container_width=True, key="sb_dash"):
        st.session_state.menu_scelta="🏠 Dashboard"; st.rerun()
    if st.button("🔒 Logout", use_container_width=True, type="primary", key="sb_logout"):
        st.session_state.authenticated=False
        st.session_state.menu_scelta="🏠 Dashboard"
        st.rerun()

scelta=st.session_state.menu_scelta

if scelta=="🏠 Dashboard":
    st.markdown(LOGHI, unsafe_allow_html=True)
    st.markdown("<h2 style='color:#1b5e20; background:#a5d6a7; padding:15px; border-radius:12px; border:3px solid #2e7d32; text-align:center;'>🏠 Dashboard - ANA Varese</h2>", unsafe_allow_html=True)
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Interventi", len(st.session_state.interventi_lista))
    c2.metric("Emergenze", len(st.session_state.emergenze_lista))
    c3.metric("Volontari", len(st.session_state.mem_nomi)+len(st.session_state.dati))
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
        if st.button("🔒\nLogout", key="q_logout", use_container_width=True, type="primary"):
            st.session_state.authenticated=False; st.rerun()

elif scelta=="🚨 Emergenze con Loghi":
    st.markdown(LOGHI, unsafe_allow_html=True)
    st.markdown("<h2 style='color:#1b5e20; background:#a5d6a7; padding:12px; border-radius:12px; border:3px solid #2e7d32;'>🚨 Emergenze - Form con Tabella e Loghi</h2>", unsafe_allow_html=True)
    torna_dashboard()
    st.markdown("#### 📚 Libreria Loghi")
    cols=st.columns(6)
    for i,(nome,icona) in enumerate(LIBRERIA_LOGHI.items()):
        with cols[i%6]:
            st.markdown(f"<div style='background:white; border:2px solid #2e7d32; border-radius:10px; padding:8px; text-align:center; margin-bottom:8px;'><div style='font-size:28px;'>{icona}</div><div style='font-size:10px; color:#1b5e20;'>{nome}</div></div>", unsafe_allow_html=True)
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
            tipo_emergenza=st.selectbox("Tipo Emergenza + Logo *", list(LIBRERIA_LOGHI.keys()), index=0)
        with c3:
            priorita=st.selectbox("Priorità *", ["🔴 Alta - Urgente","🟡 Media","🟢 Bassa"])
            odv=st.selectbox("ODV *", ["ANA Varese","Protezione Civile Lombardia","Croce Rossa","VVF","Altro"])
            squadre=st.number_input("N. Squadre", min_value=1, max_value=20, value=1)
            icona_sel = LIBRERIA_LOGHI[tipo_emergenza]
            st.markdown(f"<div style='background:#c8e6c9; border:3px solid #2e7d32; border-radius:12px; padding:15px; text-align:center;'><div style='font-size:50px;'>{icona_sel}</div><div style='color:#1b5e20; font-weight:bold;'>{tipo_emergenza}</div></div>", unsafe_allow_html=True)
        descrizione=st.text_area("Descrizione / Azione *", height=100)
        note=st.text_input("Note / Mezzi")
        if st.form_submit_button("🔴 SALVA EMERGENZA CON LOGO", use_container_width=True, type="primary"):
            if comune and via and descrizione:
                st.session_state.emergenze_lista.append({"Data": str(data_em), "Ora": str(ora_em), "Logo": LIBRERIA_LOGHI[tipo_emergenza], "Tipo": tipo_emergenza, "Comune": comune, "Via": via, "Civico": civico, "Priorità": priorita, "ODV": odv, "Squadre": squadre, "Descrizione": descrizione, "Note": note})
                st.success(f"Salvata {LIBRERIA_LOGHI[tipo_emergenza]} {tipo_emergenza}!"); st.balloons(); st.rerun()
    torna_dashboard()
    if st.session_state.emergenze_lista:
        df = pd.DataFrame(st.session_state.emergenze_lista)
        st.markdown(f"### 📋 Tabella Emergenze - {len(df)} Interventi con Loghi")
        for idx, row in df.iterrows():
            with st.container(border=True):
                c_logo,c_info,c_azioni=st.columns([1,4,1])
                with c_logo:
                    st.markdown(f"<div style='font-size:45px; text-align:center; background:#e8f5e9; border:2px solid #2e7d32; border-radius:12px; padding:10px;'>{row['Logo']}</div>", unsafe_allow_html=True)
                with c_info:
                    st.markdown(f"**{row['Logo']} {row['Tipo']}** - {row['Priorità']}")
                    st.markdown(f"📍 **{row['Comune']}** - {row['Via']} {row['Civico']} | 📅 {row['Data']} {row['Ora']} | 👥 {row['ODV']} - {row['Squadre']} sq.")
                    st.markdown(f"📝 {row['Descrizione']}")
                with c_azioni:
                    if st.button("🗑️", key=f"del_{idx}"):
                        st.session_state.emergenze_lista.pop(idx); st.rerun()
        st.dataframe(df, use_container_width=True, hide_index=True)
    torna_dashboard()

elif scelta=="🗺️ Mappa Postazioni":
    st.markdown(LOGHI, unsafe_allow_html=True)
    st.markdown("<h2 style='color:#1b5e20; background:#a5d6a7; padding:12px; border-radius:12px; border:3px solid #2e7d32;'>🗺️ Mappa Postazioni - Vecchio Form Completo</h2>", unsafe_allow_html=True)
    torna_dashboard()
    with st.form("post_form", clear_on_submit=True):
        c1,c2=st.columns(2)
        with c1:
            nome=st.text_input("Nome Postazione *")
            comune=st.text_input("Comune *", value="Varese")
            via=st.text_input("Via *")
        with c2:
            lat=st.text_input("Latitudine *", placeholder="45.8205")
            lon=st.text_input("Longitudine *", placeholder="8.8255")
            civico=st.text_input("Civico / Km")
        note_post=st.text_area("Note / Descrizione Postazione", height=80)
        if st.form_submit_button("🔴 SALVA POSTAZIONE", use_container_width=True, type="primary"):
            if nome and lat and lon:
                st.session_state.postazioni.append({"Postazione":nome,"Comune":comune,"Via":via,"Civico":civico,"Latitudine":lat,"Longitudine":lon,"Note":note_post,"Data":str(date.today())})
                st.success(f"Salvata {nome}!"); st.rerun()
    if st.session_state.postazioni:
        dfp=pd.DataFrame(st.session_state.postazioni)
        try:
            dfm=dfp.copy()
            dfm["lat"]=pd.to_numeric(dfm["Latitudine"].astype(str).str.replace(",","."), errors='coerce')
            dfm["lon"]=pd.to_numeric(dfm["Longitudine"].astype(str).str.replace(",","."), errors='coerce')
            dfm=dfm.dropna(subset=["lat","lon"])
            if not dfm.empty: st.map(dfm[["lat","lon"]], zoom=11)
        except: pass
        st.dataframe(dfp, use_container_width=True)
    torna_dashboard()

elif scelta=="🚨 Interventi Emergenza":
    st.markdown(LOGHI, unsafe_allow_html=True)
    st.markdown("<h2 style='color:#1b5e20; background:#a5d6a7; padding:12px; border-radius:12px; border:3px solid #2e7d32;'>🚨 Interventi Emergenza - Vecchio Form Completo</h2>", unsafe_allow_html=True)
    torna_dashboard()
    with st.form("form_emergenza_vecchio", clear_on_submit=True):
        c1,c2,c3=st.columns(3)
        with c1:
            data_int=st.date_input("Data *", value=date.today())
            ora_int=st.time_input("Ora *")
            comune_int=st.text_input("Comune *", value="Varese")
        with c2:
            via_int=st.text_input("Via *")
            civico_int=st.text_input("Civico *")
            cap_int=st.text_input("CAP")
        with c3:
            odv_int=st.selectbox("ODV Operativa *", ["ANA Varese","ANA Sezione Varese","Protezione Civile Lombardia","Croce Rossa","VVF","Altro"])
            prior_int=st.selectbox("Priorità *", ["🔴 Alta","🟡 Media","🟢 Bassa"])
            squadre_int=st.number_input("N. Squadre",1,20,1)
        c4,c5=st.columns(2)
        with c4:
            tipo_int=st.selectbox("Tipo Intervento *", ["Incendio Boschivo","Incendio Urbano","Alluvione","Frana","Neve","Incidente","Albero Caduto","Supporto Logistico","Altro"])
            mezzi_int=st.text_input("Mezzi Impiegati")
        with c5:
            ref_int=st.text_input("Referente sul Posto")
            tel_ref=st.text_input("Telefono Referente")
        azione_int=st.text_area("Azione / Descrizione Intervento *", height=120)
        note_int=st.text_area("Note / Esito", height=80)
        if st.form_submit_button("🔴 SALVA INTERVENTO EMERGENZA", use_container_width=True, type="primary"):
            if comune_int and via_int and azione_int:
                st.session_state.interventi_lista.append({"Data":str(data_int),"Ora":str(ora_int),"Comune":comune_int,"Via":via_int,"Civico":civico_int,"CAP":cap_int,"ODV":odv_int,"Priorità":prior_int,"Squadre":squadre_int,"Tipo":tipo_int,"Mezzi":mezzi_int,"Referente":ref_int,"Tel":tel_ref,"Azione":azione_int,"Note":note_int})
                st.success("Intervento Salvato!"); st.rerun()
    if st.session_state.interventi_lista:
        st.dataframe(pd.DataFrame(st.session_state.interventi_lista), use_container_width=True)
    torna_dashboard()

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
            data_iscriz=st.date_input("Data Iscrizione", value=date.today())
        note_vol=st.text_area("Note / Competenze", height=80)
        if st.form_submit_button("✅ SALVA VOLONTARIO", use_container_width=True, type="primary"):
            if nome and assoc and cell:
                st.session_state.dati.append({"Nome": nome, "Associazione": assoc, "Cellulare": cell, "Email": email, "Ruolo": ruolo, "Data Iscrizione": str(data_iscriz), "Note": note_vol})
                st.session_state.mem_nomi.append(nome)
                st.success(f"Aggiunto {nome}"); st.rerun()
    if st.session_state.dati:
        df = pd.DataFrame(st.session_state.dati)
        st.dataframe(df, use_container_width=True, hide_index=True)
        output = BytesIO()
        df.to_excel(output, index=False, engine="openpyxl")
        st.download_button("📥 Scarica Excel", output.getvalue(), file_name="associazioni.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
    torna_dashboard()

else:
    st.markdown(LOGHI, unsafe_allow_html=True)
    torna_dashboard()
    st.info(f"Sezione {scelta} - Verde ANA")
    torna_dashboard()