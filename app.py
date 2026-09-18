import streamlit as st
import pandas as pd
from datetime import date, datetime
from io import BytesIO
import os, json, base64, requests, tempfile

st.set_page_config(page_title="ANA Varese", page_icon="🟢", layout="wide")

st.markdown("""
<style>
.stApp{background:#e8f5e9!important;}
.main.block-container{background:white!important;border-radius:18px;padding:20px!important;}
[data-testid="stSidebar"]{background:#a5d6a7!important;border-right:4px solid #2e7d32!important;}
.stForm{background:#c8e6c9!important;border:3px solid #2e7d32!important;border-radius:15px!important;}
.stButton>button{background:#2e7d32!important;color:white!important;font-weight:bold!important;min-height:50px!important;}
.vol-selected{background:#fff3e0!important;border:4px solid #ef6c00!important;border-radius:12px!important;padding:20px!important;}
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
def trova_b64_logo(nome, libreria):
    for ic in libreria:
        if ic.get("nome")==nome and ic.get("b64"): return ic.get("b64")
    return None
def salva_icona_temp(b64, nome):
    try:
        data=base64.b64decode(b64)
        tmp_path=os.path.join(tempfile.gettempdir(), f"icon_{nome.replace(' ','_')}.png")
        with open(tmp_path,"wb") as f: f.write(data)
        return tmp_path
    except: return None

FILE_DATI="dati_volontari.json"
FILE_POST="postazioni.json"
FILE_INTERVENTI="interventi_emergenza.json"
FILE_ICONE_COND="libreria_icone_condivisa.json"
FILE_RADIO="db_radio.json"
FILE_CONSEGNA="consegna_radio.json"
FILE_EVENTI="eventi.json"
FILE_BROGLIACCIO="brogliaccio.json"
COMUNI=["Varese","Busto Arsizio","Gallarate","Saronno","Venegono Superiore","Venegono Inferiore","Castiglione Olona","Lozza","Tradate","Malnate","Luino"]
ICONS=["📍","🚨","🏕️","🚧","👥","🔥","🌊","⛰️","🚑","🚒","🦺","📻","🏠"]

for k,v in [("dati",[]),("postazioni",[]),("icone_lib",[]),("interventi_lista",[]),("db_radio",[]),("consegna_radio",[]),("eventi",[]),("brogliaccio",[]),("menu_scelta","Dashboard"),("volontario_selezionato",None),("volontario_idx",None),("form_nome",""),("form_cognome",""),("form_cell",""),("form_assoc","ANA Varese"),("map_lat",45.8205),("map_lon",8.8250),("map_comune","Varese"),("map_via",""),("em_comune",""),("em_via",""),("em_lat",""),("em_lon",""),("em_post_selezionata",None),("authenticated",False)]:
    if k not in st.session_state: st.session_state[k]=v
if not st.session_state.dati: st.session_state.dati=load_json(FILE_DATI,[])
if not st.session_state.postazioni: st.session_state.postazioni=load_json(FILE_POST,[])
if not st.session_state.interventi_lista: st.session_state.interventi_lista=load_json(FILE_INTERVENTI,[])
if not st.session_state.icone_lib: st.session_state.icone_lib=load_json(FILE_ICONE_COND,[])
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
    st.markdown("### MENU COMPLETO")
    opzioni=["Dashboard","Volontari","Mappa Postazioni","Tabella Emergenze","DB Radio","Consegna Radio","Evento","Brogliaccio","Backup"]
    sel=st.radio("Vai a",opzioni,index=opzioni.index(st.session_state.menu_scelta) if st.session_state.menu_scelta in opzioni else 0)
    if sel!=st.session_state.menu_scelta:
        st.session_state.menu_scelta=sel; st.rerun()
    st.divider()
    st.metric("Volontari",len(st.session_state.dati))
    st.metric("Postazioni",len(st.session_state.postazioni))
    st.metric("Loghi condivisi",len(st.session_state.icone_lib))
    st.divider()
    if st.button("🚪 LOGOUT",use_container_width=True,key="logout_sidebar"):
        st.session_state.authenticated=False; st.rerun()

scelta=st.session_state.menu_scelta
MIME="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

if scelta=="Dashboard":
    c1,c2=st.columns([4,1])
    with c1: st.markdown("## 🏠 DASHBOARD - TUTTI I FORM")
    with c2:
        if st.button("🚪 LOGOUT",use_container_width=True,key="logout_dashboard"):
            st.session_state.authenticated=False; st.rerun()
    c1,c2,c3,c4=st.columns(4)
    with c1:
        if st.button("👥 VOLONTARI\n6 Sottomaschere",key="q_vol",use_container_width=True):
            st.session_state.menu_scelta="Volontari"; st.rerun()
    with c2:
        if st.button("📍 MAPPA\nLoghi condivisi",key="q_map",use_container_width=True):
            st.session_state.menu_scelta="Mappa Postazioni"; st.rerun()
    with c3:
        if st.button("🚨 EMERGENZE\nLoghi condivisi",key="q_em",use_container_width=True):
            st.session_state.menu_scelta="Tabella Emergenze"; st.rerun()
    with c4:
        if st.button("📻 DB RADIO",key="q_radio",use_container_width=True):
            st.session_state.menu_scelta="DB Radio"; st.rerun()
    c5,c6,c7,c8=st.columns(4)
    with c5:
        if st.button("📦 CONSEGNA RADIO",key="q_cons",use_container_width=True):
            st.session_state.menu_scelta="Consegna Radio"; st.rerun()
    with c6:
        if st.button("📅 EVENTO",key="q_ev",use_container_width=True):
            st.session_state.menu_scelta="Evento"; st.rerun()
    with c7:
        if st.button("📝 BROGLIACCIO",key="q_brog",use_container_width=True):
            st.session_state.menu_scelta="Brogliaccio"; st.rerun()
    with c8:
        if st.button("💾 BACKUP",key="q_back",use_container_width=True):
            st.session_state.menu_scelta="Backup"; st.rerun()

elif scelta=="Volontari":
    torna_dashboard()
    st.markdown("## 👥 VOLONTARI - 6 SOTTOMASCHERE COME IERI")
    if st.session_state.volontario_selezionato is not None:
        vol=st.session_state.volontario_selezionato
        idx=st.session_state.volontario_idx
        st.markdown('<div class="vol-selected">',unsafe_allow_html=True)
        st.markdown(f"### 👤 {vol.get('Nome','')} - 6 SOTTOMASCHERE")
        st.write(f"{vol.get('Cellulare','')} | {vol.get('Comune','')} | {vol.get('Ruolo','')}")
        if st.button("❌ Chiudi",key="chiudi_det"):
            st.session_state.volontario_selezionato=None; st.session_state.volontario_idx=None; st.rerun()
        st.markdown('</div>',unsafe_allow_html=True)
        t1,t2,t3,t4,t5,t6=st.tabs(["📋 Anagrafica","📻 Radio","📅 Eventi","✅ Presenze","🚨 Emergenze","📄 Note"])
        with t1:
            st.markdown('<div class="submask">',unsafe_allow_html=True)
            st.markdown("#### Sottomaschera 1 - Anagrafica")
            with st.form("form_anag"):
                parti=vol.get('Nome','').split(" ",1)
                nome=st.text_input("Nome *",value=parti[0] if len(parti)>0 else "")
                cognome=st.text_input("Cognome *",value=parti[1] if len(parti)>1 else "")
                cell=st.text_input("Cellulare *",value=vol.get('Cellulare',''))
                comune=st.selectbox("Comune",COMUNI,index=0)
                ruolo=st.selectbox("Ruolo",["Volontario","Caposquadra","Coordinatore"],index=0)
                if st.form_submit_button("💾 SALVA",use_container_width=True,type="primary"):
                    st.session_state.dati[idx]={"Nome":f"{nome} {cognome}","Cellulare":cell,"Comune":comune,"Ruolo":ruolo,"Associazione":vol.get('Associazione','ANA Varese')}
                    save_json(FILE_DATI,st.session_state.dati); st.success("Salvato!"); st.rerun()
            st.markdown('</div>',unsafe_allow_html=True)
        with t2: st.markdown('<div class="submask"><h4>📻 Sottomaschera 2 - Radio</h4></div>',unsafe_allow_html=True)
        with t3: st.markdown('<div class="submask"><h4>📅 Sottomaschera 3 - Eventi</h4></div>',unsafe_allow_html=True)
        with t4:
            st.markdown('<div class="submask">',unsafe_allow_html=True)
            st.markdown("#### ✅ Sottomaschera 4 - Presenze")
            with st.form("form_pres"):
                ore=st.number_input("Ore",value=4.0,step=0.5)
                luogo=st.text_input("Luogo")
                if st.form_submit_button("Registra"): st.success(f"{ore}h a {luogo}")
            st.markdown('</div>',unsafe_allow_html=True)
        with t5: st.markdown('<div class="submask"><h4>🚨 Sottomaschera 5 - Emergenze</h4></div>',unsafe_allow_html=True)
        with t6:
            st.markdown('<div class="submask">',unsafe_allow_html=True)
            st.markdown("#### 📄 Sottomaschera 6 - Note")
            if st.button(f"ELIMINA {vol.get('Nome','')}"):
                st.session_state.dati.pop(idx); save_json(FILE_DATI,st.session_state.dati); st.session_state.volontario_selezionato=None; st.rerun()
            st.markdown('</div>',unsafe_allow_html=True)
        st.divider()
    st.markdown("### FORM VOLONTARI")
    with st.form("form"):
        c1,c2=st.columns(2)
        with c1:
            nome=st.text_input("Nome *",value=st.session_state.form_nome)
            cognome=st.text_input("Cognome *",value=st.session_state.form_cognome)
            cell=st.text_input("Cellulare *",value=st.session_state.form_cell)
        with c2:
            assoc=st.text_input("Associazione *",value=st.session_state.form_assoc)
            comune=st.selectbox("Comune",COMUNI,index=0)
            ruolo=st.selectbox("Ruolo *",["Volontario","Caposquadra","Coordinatore"])
        if st.form_submit_button("✅ SALVA VOLONTARIO",use_container_width=True,type="primary"):
            if nome and cognome and cell and assoc:
                st.session_state.dati.append({"Nome":f"{nome} {cognome}","Associazione":assoc,"Cellulare":cell,"Comune":comune,"Ruolo":ruolo})
                save_json(FILE_DATI,st.session_state.dati); st.rerun()
    st.divider()
    st.markdown("### TABELLA VOLONTARI - CLICCA SU NOME PER SOTTOMASCHERE")
    if st.session_state.dati:
        for idx, vol in enumerate(st.session_state.dati):
            c1,c2,c3=st.columns([3,2,2])
            with c1:
                if st.button(f"👤 {vol.get('Nome','')}",key=f"vol_{idx}",use_container_width=True):
                    parti=vol.get('Nome','').split(" ",1)
                    st.session_state.form_nome=parti[0] if len(parti)>0 else ""
                    st.session_state.form_cognome=parti[1] if len(parti)>1 else ""
                    st.session_state.form_cell=vol.get('Cellulare','')
                    st.session_state.volontario_selezionato=vol; st.session_state.volontario_idx=idx; st.rerun()
            with c2: st.write(vol.get('Cellulare',''))
            with c3: st.write(vol.get('Ruolo',''))

elif scelta=="Mappa Postazioni":
    torna_dashboard()
    st.markdown("## 📍 MAPPA POSTAZIONI - LIBRERIA CONDIVISA + LOGHI SU MAPPA")
    st.markdown("### 🎨 CARICA LOGHI PNG - Libreria CONDIVISA con Emergenze")
    st.info("Questa libreria è la stessa per Mappe ed Emergenze!")
    c_up1,c_up2=st.columns([2,1])
    with c_up1:
        uploaded=st.file_uploader("📤 CARICA LOGO PNG", type=["png","jpg","jpeg"], key="up_icon_post")
        if uploaded:
            b64=img_to_b64(uploaded)
            nome_icona=st.text_input("Nome logo", value=uploaded.name.split(".")[0], key="nome_icona_post")
            if st.button("💾 SALVA LOGO IN LIBRERIA CONDIVISA",key="save_icon_post",use_container_width=True,type="primary"):
                st.session_state.icone_lib.append({"nome":nome_icona,"b64":b64})
                save_json(FILE_ICONE_COND,st.session_state.icone_lib)
                st.success(f"Logo {nome_icona} salvato! Ora lo vedi sia in Mappe che Emergenze!"); st.rerun()
    with c_up2:
        for ic in ICONS:
            if st.button(f"{ic}",key=f"base_{ic}_post",use_container_width=True):
                st.session_state.icone_lib.append({"nome":ic,"b64":"","emoji":ic})
                save_json(FILE_ICONE_COND,st.session_state.icone_lib); st.rerun()
    if st.session_state.icone_lib:
        cols=st.columns(4)
        for i, ic in enumerate(st.session_state.icone_lib):
            with cols[i%4]:
                st.markdown('<div class="icon-lib">',unsafe_allow_html=True)
                if ic.get("b64"):
                    st.image(f"data:image/png;base64,{ic['b64']}",width=80)
                    st.write(f"{ic['nome']}")
                    st.download_button(f"📥 PNG", base64.b64decode(ic['b64']), file_name=f"{ic['nome']}.png", mime="image/png", key=f"dl_post_{i}",use_container_width=True)
                else:
                    st.markdown(f"<div style='font-size:40px;'>{ic.get('emoji',ic.get('nome','📍'))}</div>",unsafe_allow_html=True)
                if st.button(f"🗑️ Elimina",key=f"del_post_{i}",use_container_width=True):
                    st.session_state.icone_lib.pop(i); save_json(FILE_ICONE_COND,st.session_state.icone_lib); st.rerun()
                st.markdown('</div>',unsafe_allow_html=True)
    st.divider()
    try:
        import folium
        from streamlit_folium import st_folium
        HAS_FOLIUM=True
    except: HAS_FOLIUM=False
    c1,c2=st.columns([2,1])
    with c1:
        st.markdown("### 🗺️ Mappa con LOGHI sulle postazioni - Google/OSM/Waze")
        if HAS_FOLIUM:
            m=folium.Map(location=[st.session_state.map_lat, st.session_state.map_lon], zoom_start=13)
            for idx_p, p in enumerate(st.session_state.postazioni):
                try:
                    lat_f=float(p['Latitudine']); lon_f=float(p['Longitudine'])
                    logo_nome=p.get('Icona','📍')
                    b64=trova_b64_logo(logo_nome, st.session_state.icone_lib)
                    if b64:
                        tmp_path=salva_icona_temp(b64, f"{logo_nome}_{idx_p}")
                        if tmp_path and os.path.exists(tmp_path):
                            icon=folium.CustomIcon(tmp_path, icon_size=(40,40))
                            folium.Marker([lat_f, lon_f], popup=f"{logo_nome} {p.get('Postazione','')}", tooltip=p['Postazione'], icon=icon).add_to(m)
                        else:
                            folium.Marker([lat_f, lon_f], popup=p.get('Postazione',''), tooltip=p['Postazione']).add_to(m)
                    else:
                        folium.Marker([lat_f, lon_f], popup=p.get('Postazione',''), tooltip=p['Postazione']).add_to(m)
                except: pass
            folium.Marker([st.session_state.map_lat, st.session_state.map_lon], popup="Nuova", icon=folium.Icon(color="red")).add_to(m)
            map_data=st_folium(m,width=700,height=500,key="mappa_click")
            if map_data and map_data.get("last_clicked"):
                st.session_state.map_lat=map_data["last_clicked"]["lat"]
                st.session_state.map_lon=map_data["last_clicked"]["lng"]
                try:
                    url=f"https://nominatim.openstreetmap.org/reverse?format=json&lat={st.session_state.map_lat}&lon={st.session_state.map_lon}&zoom=18&addressdetails=1"
                    r=requests.get(url,headers={"User-Agent":"ANA-Varese"},timeout=5)
                    if r.status_code==200:
                        addr=r.json().get('address',{})
                        st.session_state.map_comune=addr.get('city',addr.get('town','Varese'))
                        st.session_state.map_via=f"{addr.get('road','')} {addr.get('house_number','')}".strip()
                except: pass
                st.rerun()
        lat=st.session_state.map_lat; lon=st.session_state.map_lon
        c_osm,c_gm,c_waze=st.columns(3)
        with c_osm: st.link_button("🗺️ OSM", f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=16/{lat}/{lon}", use_container_width=True)
        with c_gm: st.link_button("🔍 Google Maps", f"https://www.google.com/maps/search/?api=1&query={lat},{lon}", use_container_width=True)
        with c_waze: st.link_button("🚗 Waze", f"https://waze.com/ul?ll={lat},{lon}&navigate=yes", use_container_width=True)
    with c2:
        st.info(f"📍 {st.session_state.map_lat:.6f}, {st.session_state.map_lon:.6f}")
        opzioni_logo=["📍 Default"] + [f"{ic['nome']}" for ic in st.session_state.icone_lib]
        sel_logo=st.selectbox("🎨 Scegli logo da libreria CONDIVISA", opzioni_logo, key="sel_logo_post_combo")
        for ic in st.session_state.icone_lib:
            if ic['nome']==sel_logo and ic.get("b64"):
                st.image(f"data:image/png;base64,{ic['b64']}",width=120,caption=f"Logo: {sel_logo}")
        with st.form("form_post"):
            nome_post=st.text_input("Nome Postazione *")
            comune_post=st.selectbox("Comune *",COMUNI,index=COMUNI.index(st.session_state.map_comune) if st.session_state.map_comune in COMUNI else 0)
            via_post=st.text_input("Via *",value=st.session_state.map_via)
            lat_post=st.text_input("Latitudine *",value=str(st.session_state.map_lat))
            lon_post=st.text_input("Longitudine *",value=str(st.session_state.map_lon))
            tipo_post=st.selectbox("Tipo",["Presidio","Campo Base","Magazzino","Sede","Altro"])
            if st.form_submit_button("📍 SALVA CON LOGO",use_container_width=True,type="primary"):
                if nome_post and lat_post and lon_post:
                    new={"Postazione":nome_post,"Comune":comune_post,"Via":via_post,"Latitudine":lat_post,"Longitudine":lon_post,"Icona":sel_logo,"Tipo":tipo_post}
                    st.session_state.postazioni.append(new); save_json(FILE_POST,st.session_state.postazioni); st.success(f"{sel_logo} {nome_post} salvata!"); st.rerun()
    st.divider()
    st.markdown("### 📋 TABELLA POSTAZIONI - Loghi come IMMAGINE")
    if st.session_state.postazioni:
        for idx, p in enumerate(st.session_state.postazioni):
            c_img,c1,c2,c3=st.columns([1,2,2,2])
            with c_img:
                b64=trova_b64_logo(p.get('Icona','📍'), st.session_state.icone_lib)
                if b64: st.image(f"data:image/png;base64,{b64}",width=50)
                else: st.write(p.get('Icona','📍'))
            with c1: st.write(p.get('Postazione',''))
            with c2: st.write(f"{p.get('Comune','')}")
            with c3:
                if st.button(f"📍 Usa in Emergenza",key=f"use_em_{idx}",use_container_width=True):
                    st.session_state.em_comune=p.get('Comune',''); st.session_state.em_via=p.get('Via',''); st.session_state.em_lat=p.get('Latitudine',''); st.session_state.em_lon=p.get('Longitudine',''); st.session_state.em_post_selezionata=p; st.session_state.menu_scelta="Tabella Emergenze"; st.rerun()

elif scelta=="Tabella Emergenze":
    torna_dashboard()
    st.markdown("## 🚨 TABELLA EMERGENZE - LIBRERIA CONDIVISA")
    st.info("Stessa libreria di Mappe!")
    c_up1,c_up2=st.columns([2,1])
    with c_up1:
        up_em=st.file_uploader("📤 CARICA LOGO PNG EMERGENZA", type=["png","jpg","jpeg"], key="up_icon_em")
        if up_em:
            b64=img_to_b64(up_em)
            nome_em=st.text_input("Nome logo emergenza", value=up_em.name.split(".")[0], key="nome_icona_em")
            if st.button("💾 SALVA LOGO CONDIVISO",key="save_icon_em",use_container_width=True,type="primary"):
                st.session_state.icone_lib.append({"nome":nome_em,"b64":b64})
                save_json(FILE_ICONE_COND,st.session_state.icone_lib)
                st.success(f"Logo {nome_em} salvato!"); st.rerun()
    with c_up2:
        for ic in ["🔥","🌊","⛰️","🚑","🚒"]:
            if st.button(f"{ic}",key=f"base_{ic}_em",use_container_width=True):
                st.session_state.icone_lib.append({"nome":ic,"b64":"","emoji":ic})
                save_json(FILE_ICONE_COND,st.session_state.icone_lib); st.rerun()
    if st.session_state.icone_lib:
        cols=st.columns(4)
        for i, ic in enumerate(st.session_state.icone_lib):
            with cols[i%4]:
                st.markdown('<div class="icon-lib">',unsafe_allow_html=True)
                if ic.get("b64"):
                    st.image(f"data:image/png;base64,{ic['b64']}",width=80)
                    st.write(f"{ic['nome']}")
                    st.download_button(f"📥 PNG", base64.b64decode(ic['b64']), file_name=f"{ic['nome']}.png", mime="image/png", key=f"dl_em_{i}",use_container_width=True)
                else:
                    st.markdown(f"<div style='font-size:40px;'>{ic.get('emoji',ic.get('nome','🚨'))}</div>",unsafe_allow_html=True)
                if st.button(f"🗑️",key=f"del_em_{i}",use_container_width=True):
                    st.session_state.icone_lib.pop(i); save_json(FILE_ICONE_COND,st.session_state.icone_lib); st.rerun()
                st.markdown('</div>',unsafe_allow_html=True)
    st.divider()
    if st.session_state.postazioni:
        lista_post=["Nessuna"] + [f"{idx} - {p.get('Postazione','')} - {p.get('Comune','')}" for idx, p in enumerate(st.session_state.postazioni)]
        sel_post=st.selectbox("Seleziona postazione",lista_post,key="sel_post_em")
        if sel_post!="Nessuna":
            if st.button("📍 SI, INSERISCI DATI POSTAZIONE",key="btn_insert_post",use_container_width=True,type="primary"):
                idx=int(sel_post.split(" - ")[0]); p=st.session_state.postazioni[idx]
                st.session_state.em_comune=p.get('Comune',''); st.session_state.em_via=p.get('Via',''); st.session_state.em_lat=p.get('Latitudine',''); st.session_state.em_lon=p.get('Longitudine',''); st.session_state.em_post_selezionata=p; st.rerun()
    opzioni_logo_em=["🚨 Default"] + [f"{ic['nome']}" for ic in st.session_state.icone_lib]
    sel_logo_em=st.selectbox("🎨 Scegli logo da libreria CONDIVISA", opzioni_logo_em, key="sel_logo_em_combo")
    for ic in st.session_state.icone_lib:
        if ic['nome']==sel_logo_em and ic.get("b64"):
            st.image(f"data:image/png;base64,{ic['b64']}",width=120,caption=f"Logo: {sel_logo_em}")
    with st.form("form_em",clear_on_submit=False):
        c1,c2,c3=st.columns(3)
        with c1:
            data_int=st.date_input("Data *",value=date.today())
            ora_int=st.time_input("Ora *",value=datetime.now().time())
        with c2:
            comune_int=st.text_input("Comune *",value=st.session_state.em_comune if st.session_state.em_comune else "")
            via_int=st.text_input("Via *",value=st.session_state.em_via if st.session_state.em_via else "")
        with c3:
            civico_int=st.text_input("Civico",placeholder="10")
            odv_int=st.selectbox("ODV *",["ANA Varese","Protezione Civile Lombardia","Croce Rossa","Altro"])
        azione_int=st.text_area("Azione *",height=100)
        if st.form_submit_button("🔴 SALVA CON LOGO",use_container_width=True,type="primary"):
            if comune_int and via_int and azione_int:
                st.session_state.interventi_lista.append({"Data":str(data_int),"Ora":str(ora_int),"Comune":comune_int,"Via":via_int,"Civico":civico_int,"ODV Operativa":odv_int,"Azione":azione_int,"Logo":sel_logo_em,"Lat":st.session_state.em_lat,"Lon":st.session_state.em_lon})
                save_json(FILE_INTERVENTI,st.session_state.interventi_lista)
                st.session_state.em_comune=""; st.session_state.em_via=""; st.session_state.em_lat=""; st.session_state.em_lon=""; st.session_state.em_post_selezionata=None; st.success("Salvato!"); st.rerun()
    st.divider()
    st.markdown("### 📋 TABELLA EMERGENZE - Loghi come IMMAGINE")
    if st.session_state.interventi_lista:
        for e in st.session_state.interventi_lista:
            c_img,c1,c2=st.columns([1,2,3])
            with c_img:
                b64=trova_b64_logo(e.get('Logo','🚨'), st.session_state.icone_lib)
                if b64: st.image(f"data:image/png;base64,{b64}",width=50)
                else: st.write(e.get('Logo','🚨'))
            with c1: st.write(f"{e.get('Data','')} {e.get('Comune','')}")
            with c2: st.write(e.get('Azione',''))

else:
    torna_dashboard()
    st.markdown(f"## {scelta}")
    st.info("Form in costruzione - Torna alla Dashboard")
