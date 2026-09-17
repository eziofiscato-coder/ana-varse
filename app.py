import streamlit as st
import pandas as pd
from datetime import datetime, date
from io import BytesIO
import base64, os

st.set_page_config(page_title="ANA Varese", page_icon="🟢", layout="wide")

st.markdown("""
<style>
.stApp{background-color:#e8f5e9!important;}
.main.block-container{background-color:rgba(255,255,255,0.93)!important; border-radius:18px; padding:25px!important;}
[data-testid="stSidebar"]{background-color:#a5d6a7!important; border-right:4px solid #2e7d32!important;}
.stForm{background-color:#c8e6c9!important; border:3px solid #2e7d32!important; border-radius:15px!important; padding:20px!important;}
.stButton>button{background-color:#2e7d32!important; color:white!important; border:2px solid #1b5e20!important; font-weight:bold!important; border-radius:12px!important; min-height:65px!important;}
div[data-testid="stFormSubmitButton"]>button{background-color:#d32f2f!important; border:3px solid #b71c1c!important; color:white!important;}
h1,h2,h3{color:#1b5e20!important;}
div[data-testid="stMetric"]{background:#c8e6c9!important; border:2px solid #2e7d32!important; border-radius:12px!important;}
</style>
""", unsafe_allow_html=True)

ICONS = {
 "volontario": {"nome":"Volontario","icon":"👤"},
 "sede": {"nome":"Sede","icon":"🏠"},
 "radio": {"nome":"Radio","icon":"📻"},
 "emergenza": {"nome":"Emergenza","icon":"🚨"},
 "protezione_civile": {"nome":"Prot Civile","icon":"🛡️"},
 "ospedale": {"nome":"Ospedale","icon":"🏥"},
 "postazione": {"nome":"Postazione","icon":"📍"},
 "auto": {"nome":"Auto","icon":"🚗"},
 "elicottero": {"nome":"Elicottero","icon":"🚁"},
 "incendio": {"nome":"Incendio","icon":"🔥"},
 "alluvione": {"nome":"Alluvione","icon":"🌊"},
 "campo_base": {"nome":"Campo Base","icon":"⛺"},
}

for k,v in [("authenticated",False),("emergenze_lista",[]),("interventi_lista",[]),("dati",[]),("mem_nomi",["Mario Rossi","Luigi Bianchi","Giuseppe Verdi"]),("postazioni",[]),("menu_scelta","🏠 Dashboard")]:
    if k not in st.session_state:
        st.session_state[k]=v

def get_b64(p):
    try:
        if os.path.exists(p):
            with open(p,"rb") as f: return base64.b64encode(f.read()).decode()
    except: pass
    return ""

def torna_dashboard():
    if st.button("Torna Dashboard", use_container_width=True, key=f"back_{datetime.now().microsecond}"):
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
    LOGHI="<div style='background:#a5d6a7; padding:12px; border-radius:12px; border:3px solid #2e7d32; text-align:center;'><h3 style='color:#1b5e20; margin:0;'>ANA Varese</h3></div>"

if not st.session_state.authenticated:
    st.markdown(LOGHI, unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center; color:#1b5e20; background:#a5d6a7; padding:15px; border-radius:12px; border:3px solid #2e7d32;'>Accesso Riservato<br>admin / ana2024</h2>", unsafe_allow_html=True)
    c1,c2,c3=st.columns([1,2,1])
    with c2:
        with st.form("login"):
            u=st.text_input("Username", value="admin")
            p=st.text_input("Password", type="password", value="ana2024")
            if st.form_submit_button("ENTRA", use_container_width=True, type="primary"):
                if u=="admin" and p=="ana2024":
                    st.session_state.authenticated=True
                    st.rerun()
                else:
                    st.error("Usa admin / ana2024")
    st.stop()

with st.sidebar:
    st.markdown(LOGHI, unsafe_allow_html=True)
    opzioni=["🏠 Dashboard","🚨 Emergenze con Loghi","🗺️ Mappa Postazioni","🚨 Interventi Emergenza","👥 Volontari","💾 Backup"]
    idx = opzioni.index(st.session_state.menu_scelta) if st.session_state.menu_scelta in opzioni else 0
    sel=st.radio("MENU", opzioni, index=idx)
    if sel!=st.session_state.menu_scelta:
        st.session_state.menu_scelta=sel
        st.rerun()
    if st.button("Logout", use_container_width=True, type="primary"):
        st.session_state.authenticated=False; st.rerun()

scelta=st.session_state.menu_scelta

if scelta=="🏠 Dashboard":
    st.markdown(LOGHI, unsafe_allow_html=True)
    st.markdown("<h2 style='color:#1b5e20; background:#a5d6a7; padding:15px; border-radius:12px; border:3px solid #2e7d32; text-align:center;'>Dashboard ANA Varese</h2>", unsafe_allow_html=True)
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Interventi", len(st.session_state.interventi_lista))
    c2.metric("Emergenze", len(st.session_state.emergenze_lista))
    c3.metric("Volontari", len(st.session_state.mem_nomi))
    c4.metric("Postazioni", len(st.session_state.postazioni))
    st.markdown("### MENU SCELTA RAPIDA - TASTI CHE FUNZIONANO")
    r1c1,r1c2,r1c3,r1c4=st.columns(4)
    with r1c1:
        if st.button("Emergenze\ncon Loghi", key="q_em", use_container_width=True):
            st.session_state.menu_scelta="🚨 Emergenze con Loghi"; st.rerun()
    with r1c2:
        if st.button("Interventi", key="q_int", use_container_width=True):
            st.session_state.menu_scelta="🚨 Interventi Emergenza"; st.rerun()
    with r1c3:
        if st.button("Mappa", key="q_mappa", use_container_width=True):
            st.session_state.menu_scelta="🗺️ Mappa Postazioni"; st.rerun()
    with r1c4:
        if st.button("Volontari", key="q_vol", use_container_width=True):
            st.session_state.menu_scelta="👥 Volontari"; st.rerun()

elif scelta=="🚨 Emergenze con Loghi":
    st.markdown(LOGHI, unsafe_allow_html=True)
    torna_dashboard()
    st.markdown("#### Libreria Loghi")
    cols=st.columns(6)
    for i,(k,v) in enumerate(ICONS.items()):
        with cols[i%6]:
            st.markdown(f"<div style='background:white; border:2px solid #2e7d32; border-radius:10px; padding:8px; text-align:center;'><div style='font-size:28px;'>{v['icon']}</div><div style='font-size:10px;'>{v['nome']}</div></div>", unsafe_allow_html=True)
    st.divider()
    with st.form("form_em", clear_on_submit=True):
        c1,c2,c3=st.columns(3)
        with c1:
            data_em=st.date_input("Data *", value=date.today())
            comune=st.text_input("Comune *", value="Varese")
        with c2:
            via=st.text_input("Via *")
            tipo_key=st.selectbox("Tipo + Logo *", list(ICONS.keys()), format_func=lambda x: f"{ICONS[x]['icon']} {ICONS[x]['nome']}")
        with c3:
            odv=st.selectbox("ODV *", ["ANA Varese","Prot Civile","Altro"])
            st.markdown(f"<div style='background:#c8e6c9; border:3px solid #2e7d32; border-radius:12px; padding:10px; text-align:center;'><div style='font-size:40px;'>{ICONS[tipo_key]['icon']}</div><b>{ICONS[tipo_key]['nome']}</b></div>", unsafe_allow_html=True)
        desc=st.text_area("Descrizione *", height=80)
        if st.form_submit_button("SALVA CON LOGO", use_container_width=True, type="primary"):
            if comune and via and desc:
                st.session_state.emergenze_lista.append({"Data":str(data_em),"Logo":ICONS[tipo_key]['icon'],"Tipo":ICONS[tipo_key]['nome'],"Comune":comune,"Via":via,"ODV":odv,"Descrizione":desc})
                st.success(f"Salvata {ICONS[tipo_key]['icon']}!"); st.rerun()
    if st.session_state.emergenze_lista:
        df=pd.DataFrame(st.session_state.emergenze_lista)
        st.markdown(f"### Tabella {len(df)} Emergenze con Logo")
        for idx,row in df.iterrows():
            with st.container(border=True):
                cL,cI=st.columns([1,4])
                with cL: st.markdown(f"<div style='font-size:45px; text-align:center; background:#e8f5e9; border:2px solid #2e7d32; border-radius:12px; padding:10px;'>{row['Logo']}</div>", unsafe_allow_html=True)
                with cI: st.markdown(f"**{row['Logo']} {row['Tipo']}** | {row['Comune']} {row['Via']} | {row['Data']}"); st.write(row['Descrizione'])
        st.dataframe(df, use_container_width=True)
        st.download_button("CSV", df.to_csv(index=False).encode('utf-8'), "emergenze.csv", use_container_width=True)
    torna_dashboard()

elif scelta=="👥 Volontari":
    st.markdown(LOGHI, unsafe_allow_html=True)
    torna_dashboard()
    with st.form("form_vol", clear_on_submit=True):
        c1,c2=st.columns(2)
        with c1:
            nome=st.text_input("Nome e Cognome *")
            assoc=st.text_input("Associazione *", value="ANA Varese")
            cell=st.text_input("Cellulare *")
        with c2:
            email=st.text_input("Email")
            ruolo=st.selectbox("Ruolo *", ["Volontario","Caposquadra","Coordinatore","Autista","Radio","Logistica","Segreteria","Sanitario","Altro"])
        if st.form_submit_button("SALVA VOLONTARIO", use_container_width=True, type="primary"):
            if nome and assoc and cell:
                st.session_state.dati.append({"Nome":nome,"Associazione":assoc,"Cellulare":cell,"Email":email,"Ruolo":ruolo})
                st.success(f"Aggiunto {nome}"); st.rerun()
    if st.session_state.dati:
        df=pd.DataFrame(st.session_state.dati)
        st.dataframe(df, use_container_width=True)
        output=BytesIO()
        df.to_excel(output, index=False, engine="openpyxl")
        st.download_button("Excel", output.getvalue(), "volontari.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
    torna_dashboard()
else:
    st.markdown(LOGHI, unsafe_allow_html=True)
    torna_dashboard()
    st.info(f"Sezione {scelta}")
    torna_dashboard()