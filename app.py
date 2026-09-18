import streamlit as st
import pandas as pd
from datetime import date, datetime
from io import BytesIO
import os, json, uuid, base64, requests

st.set_page_config(page_title="ANA Varese", page_icon="🟢", layout="wide")

st.markdown("""
<style>
.stApp{background:#e8f5e9!important;}
.main.block-container{background:white!important;border-radius:18px;padding:20px!important;max-width:98%!important;}
[data-testid="stSidebar"]{background:#a5d6a7!important;border-right:4px solid #2e7d32!important;}
.stForm{background:#c8e6c9!important;border:3px solid #2e7d32!important;border-radius:15px!important;padding:15px!important;}
.stButton>button{background:#2e7d32!important;color:white!important;font-weight:bold!important;min-height:45px!important;border-radius:10px!important;}
div[data-testid="stFormSubmitButton"]>button{background:#d32f2f!important;}
.quick-btn>button{background:linear-gradient(135deg,#ff9800,#ef6c00)!important;min-height:85px!important;font-size:16px!important;}
.quick-btn-green>button{background:linear-gradient(135deg,#2e7d32,#1b5e20)!important;min-height:85px!important;}
.quick-btn-red>button{background:linear-gradient(135deg,#c62828,#b71c1c)!important;min-height:85px!important;}
.quick-btn-blue>button{background:linear-gradient(135deg,#1565c0,#0d47a1)!important;min-height:85px!important;}
.vol-selected{background:#fff3e0!important;border:4px solid #ef6c00!important;border-radius:12px!important;padding:20px!important;margin:15px 0!important;}
.submask{background:#f1f8e9!important;border:3px solid #2e7d32!important;border-radius:12px!important;padding:15px!important;margin:10px 0!important;}
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

FILE_DATI="dati_volontari.json"
FILE_POST="postazioni.json"
FILE_DETTAGLI="volontari_dettagli.json"
FILE_INTERVENTI="interventi_emergenza.json"

COMUNI=["Varese","Busto Arsizio","Gallarate","Saronno","Venegono Superiore","Venegono Inferiore","Castiglione Olona","Lozza","Tradate","Malnate","Luino","Cassano Magnago"]
ICONS=["📍","🚨","🏕️","🚧","👥","🔥","🌊","⛰️","🚑","🚒","🦺","📻","🏠"]

for k,v in [("dati",[]),("postazioni",[]),("vol_dettagli",{}),("interventi_lista",[]),("menu_scelta","Dashboard"),("volontario_selezionato",None),("volontario_idx",None),("form_nome",""),("form_cognome",""),("form_cell",""),("form_assoc","ANA Varese"),("form_ruolo","Volontario"),("map_lat",45.8205),("map_lon",8.8250),("map_comune","Varese"),("map_via","")]:
    if k not in st.session_state: st.session_state[k]=v

# Carica dati esistenti
if not st.session_state.dati: st.session_state.dati=load_json(FILE_DATI,[])
if not st.session_state.postazioni: st.session_state.postazioni=load_json(FILE_POST,[])
if not st.session_state.interventi_lista: st.session_state.interventi_lista=load_json(FILE_INTERVENTI,[])

# Header loghi
b64=get_b64("logo.png")
if b64:
    st.markdown(f"""<div style='display:flex;justify-content:center;align-items:center;gap:25px;background:#a5d6a7;padding:15px;border-radius:15px;border:3px solid #2e7d32;margin-bottom:15px;'>
    <img src='data:image/png;base64,{b64}' style='width:90px;height:90px;border-radius:50%;border:3px solid #1b5e20;background:white;object-fit:cover;'>
    <h2 style='color:#0e7a3d;text-align:center;margin:0;'>VOLONTARIATO<br>Sezione di Varese</h2>
    <img src='data:image/png;base64,{b64}' style='width:90px;height:90px;border-radius:50%;border:3px solid #1b5e20;background:white;object-fit:cover;'>
    </div>""", unsafe_allow_html=True)
else:
    st.markdown("<h2 style='text-align:center;color:#0e7a3d;'>VOLONTARIATO<br>Sezione di Varese</h2>", unsafe_allow_html=True)

# Sidebar con menu completo
with st.sidebar:
    if os.path.exists("logo.png"): st.image("logo.png",width=80)
    st.markdown("### MENU COMPLETO")
    opzioni=["Dashboard","Volontari","Mappa Postazioni","Tabella Emergenze","Backup"]
    sel=st.radio("Vai a", opzioni, index=opzioni.index(st.session_state.menu_scelta) if st.session_state.menu_scelta in opzioni else 0)
    if sel!=st.session_state.menu_scelta:
        st.session_state.menu_scelta=sel
        st.rerun()
    st.divider()
    st.metric("👥 Volontari",len(st.session_state.dati))
    st.metric("📍 Postazioni",len(st.session_state.postazioni))
    st.metric("🚨 Emergenze",len(st.session_state.interventi_lista))

scelta=st.session_state.menu_scelta
MIME="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

# DASHBOARD CON MENU VELOCE COMPLETO
if scelta=="Dashboard":
    st.markdown("## 🏠 DASHBOARD - MENU VELOCE COMPLETO")
    c1,c2,c3,c4=st.columns(4)
    with c1:
        st.markdown('<div class="quick-btn-green">',unsafe_allow_html=True)
        if st.button("👥\nVOLONTARI\nSottomaschere",key="q_vol",use_container_width=True):
            st.session_state.menu_scelta="Volontari"; st.rerun()
        st.markdown('</div>',unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="quick-btn-blue">',unsafe_allow_html=True)
        if st.button("📍\nMAPPA\nClicca per Icona",key="q_map",use_container_width=True):
            st.session_state.menu_scelta="Mappa Postazioni"; st.rerun()
        st.markdown('</div>',unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="quick-btn-red">',unsafe_allow_html=True)
        if st.button("🚨\nTABELLA\nEmergenze",key="q_em",use_container_width=True):
            st.session_state.menu_scelta="Tabella Emergenze"; st.rerun()
        st.markdown('</div>',unsafe_allow_html=True)
    with c4:
        if st.button("💾\nBACKUP\nExcel Unico",key="q_back",use_container_width=True):
            st.session_state.menu_scelta="Backup"; st.rerun()
    st.divider()
    # tabella rapida
    if st.session_state.dati:
        st.markdown("### 👥 Ultimi volontari - Clicca per sottomaschere")
        for idx, vol in enumerate(st.session_state.dati[-5:][::-1]):
            real_idx=len(st.session_state.dati)-1-idx
            c1,c2=st.columns([3,2])
            with c1:
                if st.button(f"👤 {vol.get('Nome','')}",key=f"dash_{real_idx}",use_container_width=True):
                    parti=vol.get('Nome','').split(" ",1)
                    st.session_state.form_nome=parti[0] if len(parti)>0 else ""
                    st.session_state.form_cognome=parti[1] if len(parti)>1 else ""
                    st.session_state.form_cell=vol.get('Cellulare','')
                    st.session_state.volontario_selezionato=vol
                    st.session_state.volontario_idx=real_idx
                    st.session_state.menu_scelta="Volontari"; st.rerun()
            with c2: st.write(vol.get('Ruolo',''))

# VOLONTARI CON 6 SOTTOMASCHERE
elif scelta=="Volontari":
    if st.button("🏠 Dashboard",use_container_width=True):
        st.session_state.menu_scelta="Dashboard"; st.rerun()
    st.markdown("## 👥 VOLONTARI - CON SOTTOMASCHERE")

    if st.session_state.volontario_selezionato is not None:
        vol=st.session_state.volontario_selezionato
        idx=st.session_state.volontario_idx
        vol_id=f"{vol.get('Nome','')}_{idx}"
        st.markdown('<div class="vol-selected">',unsafe_allow_html=True)
        st.markdown(f"### 👤 {vol.get('Nome','')} - 6 SOTTOMASCHERE")
        if st.button("❌ Chiudi",key="chiudi"):
            st.session_state.volontario_selezionato=None; st.session_state.volontario_idx=None; st.rerun()
        st.markdown('</div>',unsafe_allow_html=True)

        t1,t2,t3,t4,t5,t6=st.tabs(["📋 Anagrafica","📻 Radio","📅 Eventi","✅ Presenze","🚨 Emergenze","📄 Note"])
        with t1:
            st.markdown('<div class="submask">',unsafe_allow_html=True)
            st.markdown("#### Sottomaschera 1 - Anagrafica")
            with st.form("form_anag"):
                parti=vol.get('Nome','').split(" ",1)
                nome=st.text_input("Nome",value=parti[0] if len(parti)>0 else "")
                cognome=st.text_input("Cognome",value=parti[1] if len(parti)>1 else "")
                cell=st.text_input("Cellulare",value=vol.get('Cellulare',''))
                comune=st.selectbox("Comune",COMUNI,index=0)
                ruolo=st.selectbox("Ruolo",["Volontario","Caposquadra","Coordinatore","Autista","Radio","Logistica"],index=0)
                if st.form_submit_button("💾 SALVA",use_container_width=True,type="primary"):
                    st.session_state.dati[idx]={"Nome":f"{nome} {cognome}","Cellulare":cell,"Comune":comune,"Ruolo":ruolo,"Associazione":vol.get('Associazione','ANA Varese')}
                    save_json(FILE_DATI,st.session_state.dati)
                    st.session_state.volontario_selezionato=st.session_state.dati[idx]
                    st.success("Salvato!"); st.rerun()
            st.markdown('</div>',unsafe_allow_html=True)
        with t2:
            st.markdown('<div class="submask">',unsafe_allow_html=True)
            st.markdown("#### Sottomaschera 2 - Radio")
            st.info("Radio assegnate")
            st.markdown('</div>',unsafe_allow_html=True)
        with t3:
            st.markdown('<div class="submask">',unsafe_allow_html=True)
            st.markdown("#### Sottomaschera 3 - Eventi")
            st.info("Eventi partecipati")
            st.markdown('</div>',unsafe_allow_html=True)
        with t4:
            st.markdown('<div class="submask">',unsafe_allow_html=True)
            st.markdown("#### Sottomaschera 4 - Presenze")
            with st.form("form_pres"):
                ore=st.number_input("Ore",value=4.0,step=0.5)
                luogo=st.text_input("Luogo")
                if st.form_submit_button("✅ Registra"):
                    st.success(f"{ore}h a {luogo} per {vol.get('Nome','')}")
            st.markdown('</div>',unsafe_allow_html=True)
        with t5:
            st.markdown('<div class="submask">',unsafe_allow_html=True)
            st.markdown("#### Sottomaschera 5 - Emergenze")
            if st.session_state.interventi_lista:
                st.dataframe(pd.DataFrame(st.session_state.interventi_lista),use_container_width=True)
            st.markdown('</div>',unsafe_allow_html=True)
        with t6:
            st.markdown('<div class="submask">',unsafe_allow_html=True)
            st.markdown("#### Sottomaschera 6 - Note")
            note=st.text_area("Note",value=st.session_state.vol_dettagli.get(vol_id,{}).get('Note',''))
            if st.button("💾 Salva Note"):
                if vol_id not in st.session_state.vol_dettagli: st.session_state.vol_dettagli[vol_id]={}
                st.session_state.vol_dettagli[vol_id]['Note']=note
                save_json(FILE_DETTAGLI,st.session_state.vol_dettagli)
                st.success("Salvata!")
            if st.button(f"🗑️ ELIMINA {vol.get('Nome','')}"):
                st.session_state.dati.pop(idx)
                save_json(FILE_DATI,st.session_state.dati)
                st.session_state.volontario_selezionato=None
                st.session_state.volontario_idx=None
                st.rerun()
            st.markdown('</div>',unsafe_allow_html=True)
        st.divider()

    # Form base volontari
    st.markdown("### ➕ FORM VOLONTARI")
    st.info("Clicca nome in tabella sotto per aprire le 6 sottomaschere!")
    with st.form("form"):
        c1,c2=st.columns(2)
        with c1:
            nome=st.text_input("Nome *",value=st.session_state.form_nome)
            cognome=st.text_input("Cognome *",value=st.session_state.form_cognome)
            cell=st.text_input("Cellulare *",value=st.session_state.form_cell)
        with c2:
            assoc=st.text_input("Associazione *",value=st.session_state.form_assoc)
            ruolo=st.selectbox("Ruolo *",["Volontario","Caposquadra","Coordinatore","Autista","Radio","Logistica","Segreteria","Sanitario","Altro"])
        col1,col2=st.columns(2)
        with col1: sub=st.form_submit_button("✅ Salva",use_container_width=True)
        with col2: pul=st.form_submit_button("🆕 Pulisci",use_container_width=True)
        if sub:
            if nome and cognome and cell and assoc:
                nome_compl=f"{nome} {cognome}"
                if st.session_state.volont