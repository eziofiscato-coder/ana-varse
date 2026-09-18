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
.stForm{background:#c8e6c9!important;border:3px solid #2e7d32!important;border-radius:15px!important;}
.stButton>button{background:#2e7d32!important;color:white!important;font-weight:bold!important;min-height:50px!important;border-radius:10px!important;}
div[data-testid="stFormSubmitButton"]>button{background:#d32f2f!important;}
.quick-btn-green>button{background:linear-gradient(135deg,#2e7d32,#1b5e20)!important;min-height:90px!important;}
.quick-btn-blue>button{background:linear-gradient(135deg,#1565c0,#0d47a1)!important;min-height:90px!important;}
.quick-btn-red>button{background:linear-gradient(135deg,#c62828,#b71c1c)!important;min-height:90px!important;}
.quick-btn>button{background:linear-gradient(135deg,#ff9800,#ef6c00)!important;min-height:90px!important;}
.vol-selected{background:#fff3e0!important;border:4px solid #ef6c00!important;border-radius:12px!important;padding:20px!important;margin:10px 0!important;}
.submask{background:#f1f8e9!important;border:3px solid #2e7d32!important;border-radius:12px!important;padding:15px!important;margin:8px 0!important;}
.icon-lib{border:2px solid #2e7d32;border-radius:10px;padding:10px;background:white;margin:5px;}
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

COMUNI=["Varese","Busto Arsizio","Gallarate","Saronno","Venegono Superiore","Venegono Inferiore","Castiglione Olona","Lozza","Tradate","Malnate","Luino"]
ICONS=["📍","🚨","🏕️","🚧","👥","🔥","🌊","⛰️","🚑","🚒","🦺","📻","🏠"]

for k,v in [("dati",[]),("postazioni",[]),("icone_lib",[]),("icone_em_lib",[]),("interventi_lista",[]),("menu_scelta","Dashboard"),("volontario_selezionato",None),("volontario_idx",None),("form_nome",""),("form_cognome",""),("form_cell",""),("form_assoc","ANA Varese"),("map_lat",45.8205),("map_lon",8.8250),("map_comune","Varese"),("map_via",""),("em_comune",""),("em_via",""),("em_civico",""),("em_lat",""),("em_lon",""),("em_post_selezionata",None),("authenticated",False)]:
    if k not in st.session_state: st.session_state[k]=v

if not st.session_state.dati: st.session_state.dati=load_json(FILE_DATI,[])
if not st.session_state.postazioni: st.session_state.postazioni=load_json(FILE_POST,[])
if not st.session_state.interventi_lista: st.session_state.interventi_lista=load_json(FILE_INTERVENTI,[])
if not st.session_state.icone_lib: st.session_state.icone_lib=load_json(FILE_ICONE,[])
if not st.session_state.icone_em_lib: st.session_state.icone_em_lib=load_json(FILE_ICONE_EM,[])

def header_loghi():
    b64=get_b64("logo.png")
    if b64:
        st.markdown(f"<div style='display:flex;justify-content:center;align-items:center;gap:25px;background:#a5d6a7;padding:15px;border-radius:15px;border:3px solid #2e7d32;margin-bottom:15px;'><img src='data:image/png;base64,{b64}' style='width:90px;height:90px;border-radius:50%;border:3px solid #1b5e20;background:white;'><h2 style='color:#0e7a3d;margin:0;text-align:center;'>VOLONTARIATO<br>Sezione di Varese</h2><img src='data:image/png;base64,{b64}' style='width:90px;height:90px;border-radius:50%;border:3px solid #1b5e20;background:white;'></div>", unsafe_allow_html=True)
    else:
        st.markdown("<h2 style='text-align:center;color:#0e7a3d;'>VOLONTARIATO<br>Sezione di Varese</h2>", unsafe_allow_html=True)

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
    opzioni=["Dashboard","Volontari","Mappa Postazioni","Tabella Emergenze","Backup"]
    sel=st.radio("Vai a",opzioni,index=opzioni.index(st.session_state.menu_scelta) if st.session_state.menu_scelta in opzioni else 0)
    if sel!=st.session_state.menu_scelta:
        st.session_state.menu_scelta=sel; st.rerun()
    st.divider()
    st.metric("Volontari",len(st.session_state.dati))
    st.metric("Postazioni",len(st.session_state.postazioni))
    st.metric("Emergenze",len(st.session_state.interventi_lista))
    if st.button("🚪 LOGOUT",use_container_width=True):
        st.session_state.authenticated=False; st.rerun()

scelta=st.session_state.menu_scelta
MIME="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

if scelta=="Dashboard":
    st.markdown("## 🏠 DASHBOARD - MENU ALLINEATO")
    c1,c2,c3,c4=st.columns(4)
    with c1:
        st.markdown('<div class="quick-btn-green">',unsafe_allow_html=True)
        if st.button("👥\nVOLONTARI\nSottomaschere",key="q_vol",use_container_width=True):
            st.session_state.menu_scelta="Volontari"; st.rerun()
        st.markdown('</div>',unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="quick-btn-blue">',unsafe_allow_html=True)
        if st.button("📍\nMAPPA\nPostazioni",key="q_map",use_container_width=True):
            st.session_state.menu_scelta="Mappa Postazioni"; st.rerun()
        st.markdown('</div>',unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="quick-btn-red">',unsafe_allow_html=True)
        if st.button("🚨\nTABELLA\nEmergenze",key="q_em",use_container_width=True):
            st.session_state.menu_scelta="Tabella Emergenze"; st.rerun()
        st.markdown('</div>',unsafe_allow_html=True)
    with c4:
        if st.button("💾\nBACKUP\nExcel",key="q_back",use_container_width=True):
            st.session_state.menu_scelta="Backup"; st.rerun()
    st.divider()
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Volontari",len(st.session_state.dati))
    c2.metric("Postazioni",len(st.session_state.postazioni))
    c3.metric("Emergenze",len(st.session_state.interventi_lista))
    c4.metric("Oggi",date.today().strftime("%d/%m/%Y"))

elif scelta=="Volontari":
    if st.button("🏠 Dashboard",use_container_width=True):
        st.session_state.menu_scelta="Dashboard"; st.rerun()
    st.markdown("## 👥 VOLONTARI - 6 SOTTOMASCHERE")
    if st.session_state.volontario_selezionato is not None:
        vol=st.session_state.volontario_selezionato
        idx=st.session_state.volontario_idx
        vol_id=f"{vol.get('Nome','')}_{idx}"
        st.markdown('<div class="vol-selected">',unsafe_allow_html=True)
        st.markdown(f"### 👤 {vol.get('Nome','')} - 6 SOTTOMASCHERE")
        if st.button("❌ Chiudi",key="chiudi"):
            st.session_state.volontario_selezionato=None; st.session_state.volontario_idx=None; st.rerun()
        st.markdown('</div>',unsafe_allow_html=True)
        t1,t2,t3,t4,t5,t6=st.tabs(["Anagrafica","Radio","Eventi","Presenze","Emergenze","Note"])
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
                    save_json(FILE_DATI,st.session_state.dati)
                    st.success("Salvato!"); st.rerun()
            st.markdown('</div>',unsafe_allow_html=True)
        with t2: st.markdown('<div class="submask"><h4>📻 Sottomaschera 2 - Radio</h4></div>',unsafe_allow_html=True)
        with t3: st.markdown('<div class="submask"><h4>📅 Sottomaschera 3 - Eventi</h4></div>',unsafe_allow_html=True)
        with t4:
            st.markdown('<div class="submask">',unsafe_allow_html=True)
            st.markdown("#### ✅ Sottomaschera 4 - Presenze")
            with st.form("form_pres"):
                ore=st.number_input("Ore",value=4.0,step=0.5)
                luogo=st.text_input("Luogo")
                if st.form_submit_button("Registra"):
                    st.success(f"{ore}h a {luogo}")
            st.markdown('</div>',unsafe_allow_html=True)
        with t5: st.markdown('<div class="submask"><h4>🚨 Sottomaschera 5 - Emergenze</h4></div>',unsafe_allow_html=True)
        with t6:
            st.markdown('<div class="submask">',unsafe_allow_html=True)
            st.markdown("#### 📄 Sottomaschera 6 - Note")
            if st.button(f"ELIMINA {vol.get('Nome','')}"):
                st.session_state.dati.pop(idx); save_json(FILE_DATI,st.session_state.dati); st.session_state.volontario_selezionato=None; st.rerun()
            st.markdown('</div>',unsafe_allow_html=True)
        st.divider()
    st.markdown("### ➕ FORM VOLONTARI")
    with st.form("form"):
        c1,c2=st.columns(2)
        with c1:
            nome=st.text_input("Nome *",value=st.session_state.form_nome)
            cognome=st.text_input("Cognome *",value=st.session_state.form_cognome)
            cell=st.text_input("Cellulare *",value=st.session_state.form_cell)
        with c2:
            assoc=st.text_input("Associazione *",value=st.session_state.form_assoc)
            ruolo=st.selectbox("Ruolo *",["Volontario","Caposquadra","Coordinatore","Autista","Radio","Logistica"])
        col1,col2=st.columns(2)
        with col1: sub=st.form_submit_button("✅ SALVA",use_container_width=True,type="primary")
        with col2: pul=st.form_submit_button("🆕 PULISCI",use_container_width=True)
        if sub:
            if nome and cognome and cell and assoc:
                nome_compl=f"{nome} {cognome}"
                if st.session_state.volontario_selezionato is not None:
                    idx=st.session_state.volontario_idx
                    st.session_state.dati[idx]={"Nome":nome_compl,"Associazione":assoc,"Cellulare":cell,"Ruolo":ruolo}
                else:
                    st.session_state.dati.append({"Nome":nome_compl,"Associazione":assoc,"Cellulare":cell,"Ruolo":ruolo})
                save_json(FILE_DATI,st.session_state.dati)
                st.rerun()
        if pul:
            st.session_state.form_nome=""; st.session_state.form_cognome=""; st.session_state.form_cell=""
            st.session_state.volontario_selezionato=None; st.rerun()
    st.divider()
    st.markdown("### 👥 TABELLA VOLONTARI - Sotto maschera")
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
        st.dataframe(pd.DataFrame(st.session_state.dati),use_container_width=True,hide_index=True)
        out=BytesIO(); pd.DataFrame(st.session_state.dati).to_excel(out,index=False,engine="openpyxl")
        st.download_button("📥 Excel Volontari",out.getvalue(),file_name=f"volontari_{date.today()}.xlsx",mime=MIME,use_container_width=True)

elif scelta=="Mappa Postazioni":
    if st.button("🏠 Dashboard",use_container_width=True):
        st.session_state.menu_scelta="Dashboard"; st.rerun()
    st.markdown("## 📍 MAPPA POSTAZIONI - Libreria Icone PNG + Inserimento in Emergenze")

    st.markdown("### 🎨 LIBRERIA ICONE POSTAZIONI")
    c_up1,c_up2=st.columns([2,1])
    with c_up1:
        uploaded=st.file_uploader("Carica PNG per postazione", type=["png","jpg","jpeg"], key="up_icon_post")
        if uploaded:
            b64=img_to_b64(uploaded)
            nome_icona=st.text_input("Nome icona", value=uploaded.name.split(".")[0], key="nome_icona_post")
            if st.button("💾 Salva in libreria postazioni",key="save_icon_post"):
                st.session_state.icone_lib.append({"nome":nome_icona,"b64":b64})
                save_json(FILE_ICONE,st.session_state.icone_lib)
                st.success(f"Icona {nome_icona} salvata!"); st.rerun()
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
                    st.image(f"data:image/png;base64,{ic['b64']}",width=60)
                    st.download_button(f"📥 {ic['nome']}", base64.b64decode(ic['b64']), file_name=f"{ic['nome']}.png", mime="image/png", key=f"dl_post_{i}")
                else:
                    st.markdown(f"<div style='font-size:40px;text-align:center;'>{ic.get('emoji',ic.get('nome','📍'))}</div>",unsafe_allow_html=True)
                    st.write(ic.get('nome',''))
                if st.button(f"🗑️",key=f"del_post_{i}"):
                    st.session_state.icone_lib.pop(i); save_json(FILE_ICONE,st.session_state.icone_lib); st.rerun()
                st.markdown('</div>',unsafe_allow_html=True)

    st.divider()
    try:
        import folium
        from streamlit_folium import st_folium
        HAS_FOLIUM=True
    except:
        HAS_FOLIUM=False

    c1,c2=st.columns([2,1])
    with c1:
        st.markdown("### 🗺️ Clicca sulla mappa per mettere icona")
        if HAS_FOLIUM:
            m=folium.Map(location=[st.session_state.map_lat, st.session_state.map_lon], zoom_start=13)
            for p in st.session_state.postazioni:
                try: folium.Marker([float(p['Latitudine']), float(p['Longitudine'])], popup=f"{p.get('Icona','📍')} {p['Postazione']}", tooltip=p['Postazione']).add_to(m)
                except: pass
            folium.Marker([st.session_state.map_lat, st.session_state.map_lon], popup="Nuova", icon=folium.Icon(color="red")).add_to(m)
            map_data=st_folium(m,width=700,height=500,key="mappa_click")
            if map_data and map_data.get("last_clicked"):
                lat=map_data["last_clicked"]["lat"]; lon=map_data["last_clicked"]["lng"]
                st.session_state.map_lat=lat; st.session_state.map_lon=lon
                try:
                    url=f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=18&addressdetails=1"
                    r=requests.get(url,headers={"User-Agent":"ANA-Varese"},timeout=5)
                    if r.status_code==200:
                        addr=r.json().get('address',{})
                        st.session_state.map_comune=addr.get('city',addr.get('town','Varese'))
                        st.session_state.map_via=f"{addr.get('road','')} {addr.get('house_number','')}".strip()
                except: pass
                st.rerun()
        else:
            st.map(pd.DataFrame([{"lat":st.session_state.map_lat,"lon":st.session_state.map_lon}]),zoom=12)
        lat=st.session_state.map_lat; lon=st.session_state.map_lon
        c_osm,c_gm,c_waze=st.columns(3)
        with c_osm: st.link_button("🗺️ OpenStreetMap", f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=16/{lat}/{lon}", use_container_width=True)
        with c_gm: st.link_button("🔍 Google Maps", f"https://www.google.com/maps/search/?api=1&query={lat},{lon}", use_container_width=True)
        with c_waze: st.link_button("🚗 Waze", f"https://waze.com/ul?ll={lat},{lon}&navigate=yes", use_container_width=True)

    with c2:
        st.markdown("### 📋 Maschera Postazione")
        st.info(f"📍 {st.session_state.map_lat:.6f}, {st.session_state.map_lon:.6f}")
        opzioni_logo=["📍 Default"] + [f"{ic['nome']}" for ic in st.session_state.icone_lib]
        sel_logo=st.selectbox("Scegli logo da libreria", opzioni_logo, key="sel_logo_post")
        with st.form("form_post"):
            nome_post=st.text_input("Nome Postazione *")
            comune_post=st.selectbox("Comune *",COMUNI,index=COMUNI.index(st.session_state.map_comune) if st.session_state.map_comune in COMUNI else 0)
            via_post=st.text_input("Via *",value=st.session_state.map_via)
            lat_post=st.text_input("Latitudine *",value=str(st.session_state.map_lat))
            lon_post=st.text_input("Longitudine *",value=str(st.session_state.map_lon))
            tipo_post=st.selectbox("Tipo",["Presidio","Campo Base","Magazzino","Sede","Altro"])
            desc=st.text_area("Descrizione")
            if st.form_submit_button("📍 SALVA CON LOGO",use_container_width=True,type="primary"):
                if nome_post and lat_post and lon_post:
                    new={"Postazione":nome_post,"Comune":comune_post,"Via":via_post,"Latitudine":lat_post,"Longitudine":lon_post,"Icona":sel_logo,"Tipo":tipo_post,"Descrizione":desc}
                    st.session_state.postazioni.append(new); save_json(FILE_POST,st.session_state.postazioni); st.success(f"{sel_logo} {nome_post} salvata!"); st.rerun()

    st.divider()
    st.markdown("### 📋 TABELLA POSTAZIONI - Sotto maschera + Tasto inserimento in emergenze")
    if st.session_state.postazioni:
        for idx, p in enumerate(st.session_state.postazioni):
            c1,c2,c3,c4=st.columns([2,2,2,2])
            with c1: st.write(f"{p.get('Icona','📍')} {p.get('Postazione','')}")
            with c2: st.write(f"{p.get('Via','')} {p.get('Comune','')}")
            with c3: st.write(f"{p.get('Latitudine','')}, {p.get('Longitudine','')}")
            with c4:
                if st.button(f"📍 Usa in Emergenza",key=f"use_em_{idx}",use_container_width=True):
                    st.session_state.em_comune=p.get('Comune','')
                    st.session_state.em_via=p.get('Via','')
                    st.session_state.em_lat=p.get('Latitudine','')
                    st.session_state.em_lon=p.get('Longitudine','')
                    st.session_state.em_post_selezionata=p
                    st.success(f"Dati di {p.get('Postazione','')} caricati in Emergenze!")
                    st.session_state.menu_scelta="Tabella Emergenze"
                    st.rerun()
        st.dataframe(pd.DataFrame(st.session_state.postazioni),use_container_width=True)
        out=BytesIO(); pd.DataFrame(st.session_state.postazioni).to_excel(out,index=False,engine="openpyxl")
        st.download_button("📥 Excel Postazioni",out.getvalue(),file_name=f"postazioni_{date.today()}.xlsx",mime=MIME,use_container_width=True)
    else:
        st.info("Nessuna postazione")

# TABELLA EMERGENZE CON TASTO RICHIESTA POSTAZIONE
elif scelta=="Tabella Emergenze":
    if st.button("🏠 Dashboard",use_container_width=True):
        st.session_state.menu_scelta="Dashboard"; st.rerun()
    st.markdown("## 🚨 TABELLA EMERGENZE - Con inserimento dati da postazione")

    # SE ARRIVA DA POSTAZIONE, MOSTRA AVVISO
    if st.session_state.em_post_selezionata:
        p=st.session_state.em_post_selezionata
        st.markdown(f"""<div style='background:#fff3e0;border:4px solid #ef6c00;border-radius:12px;padding:15px;margin:10px 0;'>
        <h3>📍 Dati da Postazione caricati: {p.get('Postazione','')} - {p.get('Icona','📍')}</h3>
        <p><b>Comune:</b> {p.get('Comune','')} | <b>Via:</b> {p.get('Via','')} | <b>Lat:</b> {p.get('Latitudine','')} | <b>Lon:</b> {p.get('Longitudine','')}</p>
        <p>Vuoi inserire questi dati nell'emergenza? I campi sotto sono già riempiti!</p>
        </div>""", unsafe_allow_html=True)
        if st.button("❌ Non usare dati postazione",key="no_post"):
            st.session_state.em_comune=""; st.session_state.em_via=""; st.session_state.em_lat=""; st.session_state.em_lon=""; st.session_state.em_post_selezionata=None; st.rerun()

    st.markdown("### 🎨 LIBRERIA ICONE EMERGENZE")
    c_up1,c_up2=st.columns([2,1])
    with c_up1:
        up_em=st.file_uploader("Carica PNG emergenza", type=["png","jpg","jpeg"], key="up_icon_em")
        if up_em:
            b64=img_to_b64(up_em)
            nome_em=st.text_input("Nome icona emergenza", value=up_em.name.split(".")[0], key="nome_icona_em")
            if st.button("💾 Salva in libreria emergenze",key="save_icon_em"):
                st.session_state.icone_em_lib.append({"nome":nome_em,"b64":b64})
                save_json(FILE_ICONE_EM,st.session_state.icone_em_lib)
                st.success(f"Icona {nome_em} salvata!"); st.rerun()
    with c_up2:
        for ic in ["🔥","🌊","⛰️","🚑","🚒"]:
            if st.button(f"{ic}",key=f"base_{ic}_em"):
                st.session_state.icone_em_lib.append({"nome":ic,"b64":"","emoji":ic})
                save_json(FILE_ICONE_EM,st.session_state.icone_em_lib); st.rerun()

    if st.session_state.icone_em_lib:
        cols=st.columns(6)
        for i, ic in enumerate(st.session_state.icone_em_lib):
            with cols[i%6]:
                st.markdown('<div class="icon-lib">',unsafe_allow_html=True)
                if ic.get("b64"):
                    st.image(f"data:image/png;base64,{ic['b64']}",width=60)
                    st.download_button(f"📥 {ic['nome']}", base64.b64decode(ic['b64']), file_name=f"{ic['nome']}.png", mime="image/png", key=f"dl_em_{i}")
                else:
                    st.markdown(f"<div style='font-size:40px;text-align:center;'>{ic.get('emoji',ic.get('nome','🚨'))}</div>",unsafe_allow_html=True)
                if st.button(f"🗑️",key=f"del_em_{i}"):
                    st.session_state.icone_em_lib.pop(i); save_json(FILE_ICONE_EM,st.session_state.icone_em_lib); st.rerun()
                st.markdown('</div>',unsafe_allow_html=True)

    st.divider()
    st.markdown("### 🚨 FORM EMERGENZA - Con dati da postazione se richiesti")

    # Selezione postazione da lista
    if st.session_state.postazioni:
        st.markdown("#### 📍 Vuoi inserire i dati di una postazione esistente?")
        lista_post=["Nessuna"] + [f"{idx} - {p.get('Postazione','')} - {p.get('Comune','')} {p.get('Via','')} ({p.get('Icona','📍')})" for idx, p in enumerate(st.session_state.postazioni)]
        sel_post=st.selectbox("Seleziona postazione da usare", lista_post, key="sel_post_em")
        if sel_post!="Nessuna":
            if st.button("📍 SI, VOGLIO INSERIRE I DATI DI QUESTA POSTAZIONE NELL'EMERGENZA",key="btn_insert_post",use_container_width=True,type="primary"):
                idx=int(sel_post.split(" - ")[0])
                p=st.session_state.postazioni[idx]
                st.session_state.em_comune=p.get('Comune','')
                st.session_state.em_via=p.get('Via','')
                st.session_state.em_lat=p.get('Latitudine','')
                st.session_state.em_lon=p.get('Longitudine','')
                st.session_state.em_post_selezionata=p
                st.success(f"Dati di {p.get('Postazione','')} inseriti!"); st.rerun()

    opzioni_logo_em=["🚨 Default"] + [f"{ic['nome']}" for ic in st.session_state.icone_em_lib]
    sel_logo_em=st.selectbox("Scegli logo emergenza da libreria", opzioni_logo_em, key="sel_logo_em")

    with st.form("form_em",clear_on_submit=False):
        c1,c2,c3=st.columns(3)
        with c1:
            data_int=st.date_input("Data *",value=date.today())
            ora_int=st.time_input("Ora *",value=datetime.now().time())
        with c2:
            comune_int=st.text_input("Comune *",value=st.session_state.em_comune if st.session_state.em_comune else "",placeholder="Varese")
            via_int=st.text_input("Via *",value=st.session_state.em_via if st.session_state.em_via else "",placeholder="Via Roma")
            st.text_input("Latitudine da postazione",value=st.session_state.em_lat if st.session_state.em_lat else "",key="em_lat_display",disabled=True)
        with c3:
            civico_int=st.text_input("Civico",placeholder="10")
            odv_int=st.selectbox("ODV *",["ANA Varese","Protezione Civile Lombardia","Croce Rossa","Altro"])
            st.text_input("Longitudine da postazione",value=st.session_state.em_lon if st.session_state.em_lon else "",key="em_lon_display",disabled=True)
        azione_int=st.text_area("Azione *",height=100,placeholder="Descrizione intervento...")
        st.markdown(f"**Logo:** {sel_logo_em}")
        if st.session_state.em_post_selezionata:
            st.markdown(f"**Dati postazione:** {st.session_state.em_post_selezionata.get('Postazione','')} - {st.session_state.em_post_selezionata.get('Icona','')}")
        if st.form_submit_button("🔴 SALVA CON DATI POSTAZIONE + LOGO",use_container_width=True,type="primary"):
            if comune_int and via_int and azione_int:
                st.session_state.interventi_lista.append({"Data":str(data_int),"Ora":str(ora_int),"Comune":comune_int,"Via":via_int,"Civico":civico_int,"ODV Operativa":odv_int,"Azione":azione_int,"Logo":sel_logo_em,"Lat":st.session_state.em_lat,"Lon":st.session_state.em_lon,"PostazioneOrigine":st.session_state.em_post_selezionata.get('Postazione','') if st.session_state.em_post_selezionata else ""})
                save_json(FILE_INTERVENTI,st.session_state.interventi_lista)
                # Pulisci dati postazione dopo salvataggio
                st.session_state.em_comune=""; st.session_state.em_via=""; st.session_state.em_lat=""; st.session_state.em_lon=""; st.session_state.em_post_selezionata=None
                st.success(f"Salvato con logo {sel_logo_em} e dati postazione!"); st.rerun()
            else:
                st.error("Compila Comune, Via e Azione *")

    st.divider()
    st.markdown("### 📋 TABELLA EMERGENZE - Sotto maschera")
    if st.session_state.interventi_lista:
        df=pd.DataFrame(st.session_state.interventi_lista)
        st.dataframe(df,use_container_width=True)
        out=BytesIO(); df.to_excel(out,index=False,engine="openpyxl")
        st.download_button("📥 Excel Emergenze",out.getvalue(),file_name=f"emergenze_{date.today()}.xlsx",mime=MIME,use_container_width=True)
        if st.button("🗑️ Cancella tutti",use_container_width=True):
            st.session_state.interventi_lista=[]; save_json(FILE_INTERVENTI,[]); st.rerun()
    else:
        st.info("Nessun intervento")

elif scelta=="Backup":
    if st.button("🏠 Dashboard",use_container_width=True):
        st.session_state.menu_scelta="Dashboard"; st.rerun()
    st.markdown("## 💾 BACKUP UNICO")
    tot=len(st.session_state.dati)+len(st.session_state.postazioni)+len(st.session_state.interventi_lista)
    st.metric("Totale",tot)
    if st.button("📦 CREA EXCEL UNICO",use_container_width=True,type="primary"):
        out=BytesIO()
        with pd.ExcelWriter(out,engine="openpyxl") as writer:
            if st.session_state.dati: pd.DataFrame(st.session_state.dati).to_excel(writer,sheet_name="Volontari",index=False)
            if st.session_state.postazioni: pd.DataFrame(st.session_state.postazioni).to_excel(writer,sheet_name="Postazioni",index=False)
            if st.session_state.interventi_lista: pd.DataFrame(st.session_state.interventi_lista).to_excel(writer,sheet_name="Emergenze",index=False)
        st.session_state["backup_unico"]=out.getvalue()
        st.success("Creato!")
    if "backup_unico" in st.session_state:
        st.download_button("📥 SCARICA EXCEL UNICO",st.session_state["backup_unico"],file_name=f"BACKUP_UNICO_{date.today()}.xlsx",mime=MIME,use_container_width=True)