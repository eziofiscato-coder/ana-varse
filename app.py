import streamlit as st
import pandas as pd
from datetime import date, datetime
from io import BytesIO
import os, json, base64, requests

st.set_page_config(page_title="ANA Varese", page_icon="🟢", layout="wide")

st.markdown("""
<style>
.stApp{background:#e8f5e9!important;}
.main.block-container{background:white!important;border-radius:18px;padding:20px!important;max-width:98%!important;}
[data-testid="stSidebar"]{background:#a5d6a7!important;border-right:4px solid #2e7d32!important;}
.stForm{background:#c8e6c9!important;border:3px solid #2e7d32!important;border-radius:15px!important;padding:15px!important;}
.stButton>button{background:#2e7d32!important;color:white!important;font-weight:bold!important;min-height:50px!important;border-radius:10px!important;}
div[data-testid="stFormSubmitButton"]>button{background:#d32f2f!important;}
.vol-selected{background:#fff3e0!important;border:4px solid #ef6c00!important;border-radius:12px!important;padding:20px!important;margin:10px 0!important;}
.submask{background:#f1f8e9!important;border:3px solid #2e7d32!important;border-radius:12px!important;padding:15px!important;margin:8px 0!important;}
.icon-lib{border:2px solid #2e7d32;border-radius:10px;padding:10px;background:white;margin:5px;text-align:center;}
</style>
""", unsafe_allow_html=True)

def load_json(f, default):
    try:
        if os.path.exists(f):
            with open(f,"r",encoding="utf-8") as fh:
                d=json.load(fh)
                if isinstance(d,list) or isinstance(d,dict): return d
    except: pass
    return default

def save_json(f,d):
    try:
        with open(f,"w",encoding="utf-8") as fh: json.dump(d,fh,ensure_ascii=False,indent=2)
    except: pass

def get_b64(p):
    try:
        if os.path.exists(p):
            with open(p,"rb") as f: return base64.b64encode(f.read()).decode()
    except: pass
    return ""

def img_to_b64(file):
    try: return base64.b64encode(file.getvalue()).decode()
    except: return ""

FILE_DATI="dati_volontari.json"
FILE_POST="postazioni.json"
FILE_INTERVENTI="interventi_emergenza.json"
FILE_ICONE="libreria_icone.json"
FILE_ICONE_EM="libreria_icone_emergenze.json"
FILE_RADIO="db_radio.json"
FILE_CONSEGNA="consegna_radio.json"
FILE_EVENTI="eventi.json"
FILE_BROGLIACCIO="brogliaccio.json"

COMUNI=["Varese","Busto Arsizio","Gallarate","Saronno","Venegono Superiore","Venegono Inferiore","Castiglione Olona","Lozza","Tradate","Malnate","Luino"]
ICONS=["📍","🚨","🏕️","🚧","👥","🔥","🌊","⛰️","🚑","🚒","🦺","📻","🏠"]

for k,v in [("dati",[]),("postazioni",[]),("icone_lib",[]),("icone_em_lib",[]),("interventi_lista",[]),("db_radio",[]),("consegna_radio",[]),("eventi",[]),("brogliaccio",[]),("menu_scelta","Dashboard"),("volontario_selezionato",None),("volontario_idx",None),("form_nome",""),("form_cognome",""),("form_cell",""),("form_assoc","ANA Varese"),("map_lat",45.8205),("map_lon",8.8250),("map_comune","Varese"),("map_via",""),("em_comune",""),("em_via",""),("em_lat",""),("em_lon",""),("em_post_selezionata",None),("authenticated",False)]:
    if k not in st.session_state: st.session_state[k]=v

if not st.session_state.dati: st.session_state.dati=load_json(FILE_DATI,[])
if not st.session_state.postazioni: st.session_state.postazioni=load_json(FILE_POST,[])
if not st.session_state.interventi_lista: st.session_state.interventi_lista=load_json(FILE_INTERVENTI,[])
if not st.session_state.icone_lib: st.session_state.icone_lib=load_json(FILE_ICONE,[])
if not st.session_state.icone_em_lib: st.session_state.icone_em_lib=load_json(FILE_ICONE_EM,[])
if not st.session_state.db_radio: st.session_state.db_radio=load_json(FILE_RADIO,[])
if not st.session_state.consegna_radio: st.session_state.consegna_radio=load_json(FILE_CONSEGNA,[])
if not st.session_state.eventi: st.session_state.eventi=load_json(FILE_EVENTI,[])
if not st.session_state.brogliaccio: st.session_state.brogliaccio=load_json(FILE_BROGLIACCIO,[])

def header_loghi():
    b64=get_b64("logo.png")
    if b64:
        st.markdown(f"<div style='display:flex;justify-content:center;align-items:center;gap:25px;background:#a5d6a7;padding:15px;border-radius:15px;border:3px solid #2e7d32;margin-bottom:15px;'><img src='data:image/png;base64,{b64}' style='width:90px;height:90px;border-radius:50%;border:3px solid #1b5e20;background:white;'><h2 style='color:#0e7a3d;margin:0;text-align:center;'>VOLONTARIATO<br>Sezione di Varese</h2><img src='data:image/png;base64,{b64}' style='width:90px;height:90px;border-radius:50%;border:3px solid #1b5e20;background:white;'></div>", unsafe_allow_html=True)
    else:
        st.markdown("<h2 style='text-align:center;color:#0e7a3d;'>VOLONTARIATO<br>Sezione di Varese</h2>", unsafe_allow_html=True)

def torna_dashboard():
    c1,c2=st.columns([1,1])
    with c1:
        if st.button("🏠 TORNA ALLA DASHBOARD",use_container_width=True,key=f"torna_{st.session_state.menu_scelta}"):
            st.session_state.menu_scelta="Dashboard"; st.rerun()
    with c2:
        if st.button("🚪 LOGOUT",use_container_width=True,key=f"logout_{st.session_state.menu_scelta}"):
            st.session_state.authenticated=False; st.rerun()

if not st.session_state.authenticated:
    header_loghi()
    st.markdown("<h2 style='text-align:center;color:#2e7a3d;'>🔒 Accesso Riservato</h2>", unsafe_allow_html=True)
    c1,c2,c3=st.columns([1,2,1])
    with c2:
        with st.form("login"):
            u=st.text_input("Username",value="admin")
            p=st.text_input("Password",type="password",value="ana2024")
            if st.form_submit_button("🔴 ACCEDI",use_container_width=True,type="primary"):
                if (u=="admin" and p=="ana2024") or p=="ANA2025":
                    st.session_state.authenticated=True; st.rerun()
                else: st.error("Password errata")
    st.stop()

header_loghi()
st.divider()

with st.sidebar:
    if os.path.exists("logo.png"): st.image("logo.png",width=80)
    st.markdown("### MENU")
    opzioni=["Dashboard","Volontari","Mappa Postazioni","Tabella Emergenze","DB Radio","Consegna Radio","Evento","Brogliaccio","Backup"]
    sel=st.radio("Vai a",opzioni,index=opzioni.index(st.session_state.menu_scelta) if st.session_state.menu_scelta in opzioni else 0)
    if sel!=st.session_state.menu_scelta:
        st.session_state.menu_scelta=sel; st.rerun()
    st.divider()
    st.metric("Volontari",len(st.session_state.dati))
    st.metric("Postazioni",len(st.session_state.postazioni))
    st.metric("Emergenze",len(st.session_state.interventi_lista))
    st.divider()
    if st.button("🚪 LOGOUT",use_container_width=True,key="logout_sidebar"):
        st.session_state.authenticated=False; st.rerun()

scelta=st.session_state.menu_scelta
MIME="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

def tabella_sotto(nome, lista, file_json):
    st.divider()
    st.markdown(f"### 📋 TABELLA {nome} - Sotto maschera")
    if lista:
        df=pd.DataFrame(lista)
        st.dataframe(df,use_container_width=True)
        out=BytesIO(); df.to_excel(out,index=False,engine="openpyxl")
        c1,c2=st.columns(2)
        with c1:
            st.download_button(f"📥 Excel {nome}",out.getvalue(),file_name=f"{nome.lower()}_{date.today()}.xlsx",mime=MIME,use_container_width=True,key=f"dl_{nome}")
        with c2:
            if st.button(f"🗑️ Cancella {nome}",use_container_width=True,key=f"del_{nome}"):
                lista.clear(); save_json(file_json,[]); st.rerun()
    else:
        st.info(f"Nessun dato in {nome}")

if scelta=="Dashboard":
    c_log1,c_log2=st.columns([4,1])
    with c_log1: st.markdown("## 🏠 DASHBOARD - MENU ALLINEATO")
    with c_log2:
        if st.button("🚪 LOGOUT",use_container_width=True,key="logout_dashboard"):
            st.session_state.authenticated=False; st.rerun()
    c1,c2,c3,c4=st.columns(4)
    with c1:
        if st.button("👥\nVOLONTARI",key="q_vol",use_container_width=True):
            st.session_state.menu_scelta="Volontari"; st.rerun()
    with c2:
        if st.button("📍\nMAPPA",key="q_map",use_container_width=True):
            st.session_state.menu_scelta="Mappa Postazioni"; st.rerun()
    with c3:
        if st.button("🚨\nEMERGENZE",key="q_em",use_container_width=True):
            st.session_state.menu_scelta="Tabella Emergenze"; st.rerun()
    with c4:
        if st.button("💾\nBACKUP",key="q_back",use_container_width=True):
            st.session_state.menu_scelta="Backup"; st.rerun()

elif scelta=="Volontari":
    torna_dashboard()
    st.markdown("## 👥 VOLONTARI - CON 6 SOTTOMASCHERE (come prima)")

    # SOTTOMASCHERE - COME PRIMA
    if st.session_state.volontario_selezionato is not None:
        vol=st.session_state.volontario_selezionato
        idx=st.session_state.volontario_idx
        st.markdown('<div class="vol-selected">',unsafe_allow_html=True)
        st.markdown(f"### 👤 VOLONTARIO SELEZIONATO: {vol.get('Nome','')} - 6 SOTTOMASCHERE")
        st.write(f"**Cellulare:** {vol.get('Cellulare','')} | **Comune:** {vol.get('Comune','Varese')} | **Ruolo:** {vol.get('Ruolo','')} | **Associazione:** {vol.get('Associazione','')}")
        if st.button("❌ Chiudi dettaglio",key="chiudi_det"):
            st.session_state.volontario_selezionato=None; st.session_state.volontario_idx=None; st.rerun()
        st.markdown('</div>',unsafe_allow_html=True)

        t1,t2,t3,t4,t5,t6=st.tabs(["📋 Anagrafica","📻 Radio","📅 Eventi","✅ Presenze","🚨 Emergenze","📄 Note"])

        with t1:
            st.markdown('<div class="submask">',unsafe_allow_html=True)
            st.markdown("#### 📋 Sottomaschera 1 - Anagrafica Completa")
            with st.form("form_anag"):
                parti=vol.get('Nome','').split(" ",1)
                nome=st.text_input("Nome *",value=parti[0] if len(parti)>0 else "")
                cognome=st.text_input("Cognome *",value=parti[1] if len(parti)>1 else "")
                cell=st.text_input("Cellulare *",value=vol.get('Cellulare',''))
                comune=st.selectbox("Comune",COMUNI,index=COMUNI.index(vol.get('Comune','Varese')) if vol.get('Comune','') in COMUNI else 0)
                ruolo=st.selectbox("Ruolo",["Volontario","Caposquadra","Coordinatore","Autista","Radio","Logistica","Segreteria","Sanitario","Altro"],index=0)
                assoc=st.text_input("Associazione",value=vol.get('Associazione','ANA Varese'))
                if st.form_submit_button("💾 SALVA ANAGRAFICA",use_container_width=True,type="primary"):
                    st.session_state.dati[idx]={"Nome":f"{nome} {cognome}","Cellulare":cell,"Comune":comune,"Ruolo":ruolo,"Associazione":assoc}
                    save_json(FILE_DATI,st.session_state.dati)
                    st.session_state.volontario_selezionato=st.session_state.dati[idx]
                    st.success("Anagrafica salvata!"); st.rerun()
            st.markdown('</div>',unsafe_allow_html=True)

        with t2:
            st.markdown('<div class="submask">',unsafe_allow_html=True)
            st.markdown("#### 📻 Sottomaschera 2 - Radio Assegnate")
            st.write(f"Radio assegnate a {vol.get('Nome','')}")
            if st.session_state.db_radio:
                for r in st.session_state.db_radio:
                    st.write(f"- {r.get('ID','')} {r.get('Modello','')} - {r.get('Stato','')}")
            else:
                st.info("Nessuna radio in DB - Vai in DB Radio")
            st.markdown('</div>',unsafe_allow_html=True)

        with t3:
            st.markdown('<div class="submask">',unsafe_allow_html=True)
            st.markdown("#### 📅 Sottomaschera 3 - Eventi Partecipati")
            if st.session_state.eventi:
                st.dataframe(pd.DataFrame(st.session_state.eventi),use_container_width=True)
            else:
                st.info("Nessun evento")
            st.markdown('</div>',unsafe_allow_html=True)

        with t4:
            st.markdown('<div class="submask">',unsafe_allow_html=True)
            st.markdown("#### ✅ Sottomaschera 4 - Presenze / Ore")
            with st.form("form_pres"):
                ore=st.number_input("Ore",min_value=0.5,value=4.0,step=0.5)
                luogo=st.text_input("Luogo")
                attivita=st.selectbox("Attività",["Emergenza","Esercitazione","Manutenzione","Formazione"])
                if st.form_submit_button("✅ REGISTRA PRESENZA",use_container_width=True):
                    st.success(f"{ore}h registrate per {vol.get('Nome','')} a {luogo} - {attivita}")
            st.markdown('</div>',unsafe_allow_html=True)

        with t5:
            st.markdown('<div class="submask">',unsafe_allow_html=True)
            st.markdown("#### 🚨 Sottomaschera 5 - Emergenze del volontario")
            if st.session_state.interventi_lista:
                st.dataframe(pd.DataFrame(st.session_state.interventi_lista),use_container_width=True)
            else:
                st.info("Nessuna emergenza")
            st.markdown('</div>',unsafe_allow_html=True)

        with t6:
            st.markdown('<div class="submask">',unsafe_allow_html=True)
            st.markdown("#### 📄 Sottomaschera 6 - Note / Documenti")
            vol_id=f"{vol.get('Nome','')}_{idx}"
            note=st.text_area("Note",height=120)
            if st.button("💾 Salva Note",use_container_width=True):
                st.success("Note salvate!")
            if st.button(f"🗑️ ELIMINA {vol.get('Nome','')}",use_container_width=True):
                st.session_state.dati.pop(idx); save_json(FILE_DATI,st.session_state.dati); st.session_state.volontario_selezionato=None; st.session_state.volontario_idx=None; st.rerun()
            st.markdown('</div>',unsafe_allow_html=True)

        st.divider()

    st.markdown("### ➕ FORM VOLONTARI")
    with st.form("form"):
        c1,c2=st.columns(2)
        with c1:
            nome=st.text_input("Nome *",value=st.session_state.form_nome,placeholder="Mario")
            cognome=st.text_input("Cognome *",value=st.session_state.form_cognome,placeholder="Rossi")
            cell=st.text_input("Cellulare *",value=st.session_state.form_cell,placeholder="3331234567")
        with c2:
            assoc=st.text_input("Associazione *",value=st.session_state.form_assoc)
            comune=st.selectbox("Comune",COMUNI,index=0)
            ruolo=st.selectbox("Ruolo *",["Volontario","Caposquadra","Coordinatore","Autista","Radio","Logistica","Segreteria","Sanitario","Altro"])
        col1,col2=st.columns(2)
        with col1: sub=st.form_submit_button("✅ SALVA VOLONTARIO",use_container_width=True,type="primary")
        with col2: pul=st.form_submit_button("🆕 PULISCI",use_container_width=True)
        if sub:
            if nome and cognome and cell and assoc:
                nome_compl=f"{nome} {cognome}"
                if st.session_state.volontario_selezionato is not None:
                    idx=st.session_state.volontario_idx
                    st.session_state.dati[idx]={"Nome":nome_compl,"Associazione":assoc,"Cellulare":cell,"Comune":comune,"Ruolo":ruolo}
                else:
                    st.session_state.dati.append({"Nome":nome_compl,"Associazione":assoc,"Cellulare":cell,"Comune":comune,"Ruolo":ruolo})
                save_json(FILE_DATI,st.session_state.dati)
                st.success(f"Salvato {nome_compl}!")
                st.rerun()
            else:
                st.error("Compila campi *")
        if pul:
            st.session_state.form_nome=""; st.session_state.form_cognome=""; st.session_state.form_cell=""
            st.session_state.volontario_selezionato=None; st.session_state.volontario_idx=None; st.rerun()

    # TABELLA SOTTO MASCHERA CON CLICK SU COGNOME PER VISUALIZZARE IN MASCHERA
    st.divider()
    st.markdown("### 👥 TABELLA VOLONTARI SOTTO MASCHERA - CLICCA SU COGNOME PER VEDERE DATI IN MASCHERA")
    if st.session_state.dati:
        st.markdown("**Clicca sul nome per aprire le 6 sottomaschere e vedere i dati nella maschera sopra**")
        for idx, vol in enumerate(st.session_state.dati):
            nome_completo=vol.get('Nome','')
            parti=nome_completo.split(" ",1)
            cognome=parti[1] if len(parti)>1 else nome_completo
            nome=parti[0] if len(parti)>0 else ""
            c1,c2,c3,c4=st.columns([3,2,2,2])
            with c1:
                # CLICK SU COGNOME/NOME PER VISUALIZZARE NELLA MASCHERA
                if st.button(f"👤 {nome_completo}",key=f"vol_{idx}",use_container_width=True,help="Clicca per vedere dati nella maschera + sottomaschere"):
                    st.session_state.form_nome=nome
                    st.session_state.form_cognome=cognome
                    st.session_state.form_cell=vol.get('Cellulare','')
                    st.session_state.volontario_selezionato=vol
                    st.session_state.volontario_idx=idx
                    st.rerun()
            with c2: st.write(vol.get('Cellulare',''))
            with c3: st.write(vol.get('Comune','Varese'))
            with c4: st.write(vol.get('Ruolo',''))
        st.divider()
        df=pd.DataFrame(st.session_state.dati)
        st.dataframe(df,use_container_width=True,hide_index=True)
        out=BytesIO(); df.to_excel(out,index=False,engine="openpyxl")
        st.download_button("📥 Scarica Excel Volontari",out.getvalue(),file_name=f"volontari_{date.today()}.xlsx",mime=MIME,use_container_width=True)
    else:
        st.info("Nessun volontario - Inserisci sopra!")

elif scelta=="Mappa Postazioni":
    torna_dashboard()
    st.markdown("## 📍 MAPPA POSTAZIONI - Libreria Loghi PNG nel Combo")
    st.markdown("### 🎨 CARICA LOGHI PNG - Crea libreria")
    c_up1,c_up2=st.columns([2,1])
    with c_up1:
        uploaded=st.file_uploader("Carica logo PNG per postazione", type=["png","jpg","jpeg"], key="up_icon_post")
        if uploaded:
            b64=img_to_b64(uploaded)
            nome_icona=st.text_input("Nome logo", value=uploaded.name.split(".")[0], key="nome_icona_post")
            if st.button("💾 Salva logo in libreria",key="save_icon_post"):
                st.session_state.icone_lib.append({"nome":nome_icona,"b64":b64})
                save_json(FILE_ICONE,st.session_state.icone_lib)
                st.success(f"Logo {nome_icona} salvato! Ora nel combo!"); st.rerun()
    with c_up2:
        for ic in ICONS:
            if st.button(f"{ic}",key=f"base_{ic}_post"):
                st.session_state.icone_lib.append({"nome":ic,"b64":"","emoji":ic})
                save_json(FILE_ICONE,st.session_state.icone_lib); st.rerun()
    if st.session_state.icone_lib:
        cols=st.columns(6)
        for i, ic in enumerate(st.session_state.icone_lib):
            with cols[i%6]:
                st.markdown('<div class="icon-lib">',unsafe_allow_html=True)
                if ic.get("b64"):
                    st.image(f"data:image/png;base64,{ic['b64']}",width=70)
                    st.write(f"{ic['nome']}")
                    st.download_button(f"📥 PNG", base64.b64decode(ic['b64']), file_name=f"{ic['nome']}.png", mime="image/png", key=f"dl_post_{i}")
                else:
                    st.markdown(f"<div style='font-size:40px;'>{ic.get('emoji',ic.get('nome','📍'))}</div>",unsafe_allow_html=True)
                if st.button(f"🗑️",key=f"del_post_{i}"):
                    st.session_state.icone_lib.pop(i); save_json(FILE_ICONE,st.session