import streamlit as st
import pandas as pd
from datetime import date
from io import BytesIO
import os, json, base64, tempfile, requests, hashlib

st.set_page_config(page_title="ANA Varese", page_icon="🟢", layout="wide")

st.markdown("""
<style>
.stApp{background:#e8f5e9!important;}
.main.block-container{background:white!important;border-radius:18px;padding:20px!important;}
[data-testid="stSidebar"]{background:#a5d6a7!important;border-right:4px solid #2e7d32!important;}
.stForm{background:#c8e6c9!important;border:3px solid #2e7d32!important;border-radius:15px!important;padding:15px!important;}
.stButton>button{background:#2e7d32!important;color:white!important;font-weight:bold!important;min-height:45px!important;border-radius:10px!important;}
div[data-testid="stFormSubmitButton"]>button{background:#d32f2f!important;}
.icon-lib{border:3px solid #2e7d32;border-radius:12px;padding:10px;background:white;text-align:center;margin:5px;}
.dashboard-card{border:3px solid #2e7d32;border-radius:15px;padding:15px;background:#e8f5e9;text-align:center;margin:10px;}
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
        tmp=os.path.join(tempfile.gettempdir(), f"icon_{nome}.png")
        with open(tmp,"wb") as f: f.write(data)
        return tmp
    except: return None

def reverse_geocode(lat, lon):
    try:
        url=f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=18&addressdetails=1"
        r=requests.get(url, headers={"User-Agent":"ANA-Varese-App"}, timeout=5)
        if r.status_code==200:
            data=r.json()
            addr=data.get("address",{})
            road=addr.get("road","") or addr.get("pedestrian","") or ""
            house=addr.get("house_number","")
            via=f"{road} {house}".strip() or data.get("display_name","").split(",")[0]
            comune=addr.get("city","") or addr.get("town","") or addr.get("village","") or ""
            return via, comune
    except: pass
    return "", ""

def hash_pwd(pwd): return hashlib.sha256(pwd.encode()).hexdigest()

FILE_DATI="dati_volontari.json"
FILE_POST="postazioni.json"
FILE_ICONE="libreria_icone_condivisa.json"
FILE_UTENTI="utenti.json"
COMUNI=["Varese","Busto Arsizio","Gallarate","Saronno","Venegono Superiore","Venegono Inferiore","Castiglione Olona","Lozza","Tradate","Malnate","Luino","Altro"]
RUOLI=["Amministratore","Utente"]

for k,v in [("dati",[]),("postazioni",[]),("icone_lib",[]),("utenti",[]),("menu_scelta","Dashboard"),("map_lat",45.8205),("map_lon",8.8250),("map_via",""),("map_comune","Varese"),("map_logo","Default"),("post_sel",None),("map_zoom",13),("authenticated",False),("ruolo",""),("username","")]:
    if k not in st.session_state: st.session_state[k]=v

if not st.session_state.dati: st.session_state.dati=load_json(FILE_DATI,[])
if not st.session_state.postazioni: st.session_state.postazioni=load_json(FILE_POST,[])
if not st.session_state.icone_lib: st.session_state.icone_lib=load_json(FILE_ICONE,[])
if not st.session_state.utenti: st.session_state.utenti=load_json(FILE_UTENTI,[])

if not st.session_state.utenti:
    st.session_state.utenti=[
        {"username":"admin","password":hash_pwd("ana2024"),"ruolo":"Amministratore","nome":"Amministratore ANA"},
        {"username":"utente","password":hash_pwd("utente2024"),"ruolo":"Utente","nome":"Utente Volontario"}
    ]
    save_json(FILE_UTENTI,st.session_state.utenti)

def header_loghi():
    b64=get_b64("logo.png")
    if b64:
        st.markdown(f"<div style='display:flex;justify-content:center;align-items:center;gap:25px;background:#a5d6a7;padding:15px;border-radius:15px;border:3px solid #2e7d32;'><img src='data:image/png;base64,{b64}' style='width:80px;height:80px;border-radius:50%;'><h2 style='color:#0e7a3d;margin:0;text-align:center;'>VOLONTARIATO<br>Sezione di Varese</h2><img src='data:image/png;base64,{b64}' style='width:80px;height:80px;border-radius:50%;'></div>", unsafe_allow_html=True)
    else:
        st.markdown("<h2 style='text-align:center;color:#0e7a3d;'>VOLONTARIATO Sezione di Varese</h2>", unsafe_allow_html=True)

def torna_dashboard():
    if st.button("🏠 TORNA A DASHBOARD",use_container_width=True,key="torna_home"):
        st.session_state.menu_scelta="Dashboard"
        st.rerun()

if not st.session_state.authenticated:
    header_loghi()
    st.markdown("## 🔐 LOGIN - Locale e Cloud")
    st.info("Admin: admin / ana2024 (tutto) | Utente: utente / utente2024 (inserisce e visualizza)")
    c1,c2,c3=st.columns([1,2,1])
    with c2:
        with st.form("login"):
            u=st.text_input("Username",value="admin")
            p=st.text_input("Password",type="password",value="ana2024")
            if st.form_submit_button("🔴 ACCEDI",use_container_width=True,type="primary"):
                pwd_hash=hash_pwd(p)
                trovato=None
                for ut in st.session_state.utenti:
                    if ut["username"]==u and ut["password"]==pwd_hash:
                        trovato=ut
                        break
                if trovato:
                    st.session_state.authenticated=True
                    st.session_state.ruolo=trovato["ruolo"]
                    st.session_state.username=trovato["username"]
                    st.rerun()
                else:
                    st.error("Username o password errati")
    st.stop()

header_loghi()
st.markdown(f"**Utente:** {st.session_state.username} | **Ruolo:** {st.session_state.ruolo}")
if st.button("🚪 Logout"):
    st.session_state.authenticated=False
    st.session_state.ruolo=""
    st.session_state.username=""
    st.rerun()
st.divider()

with st.sidebar:
    if os.path.exists("logo.png"): st.image("logo.png",width=80)
    st.markdown(f"### Ciao {st.session_state.username}")
    st.markdown(f"Ruolo: **{st.session_state.ruolo}**")
    st.markdown("### 📋 MENU COMPLETO FORM")
    if st.session_state.ruolo=="Amministratore":
        opzioni=["Dashboard","Volontari","Mappa Postazioni","Gestione Loghi","Gestione Utenti","Backup"]
    else:
        opzioni=["Dashboard","Volontari","Mappa Postazioni","Backup"]
    sel=st.radio("Vai a",opzioni,index=0,key="radio_menu")
    if sel!=st.session_state.menu_scelta:
        st.session_state.menu_scelta=sel
        st.rerun()
    st.divider()
    st.metric("👥 Volontari",len(st.session_state.dati))
    st.metric("📍 Postazioni",len(st.session_state.postazioni))
    st.metric("🎨 Loghi",len(st.session_state.icone_lib))

scelta=st.session_state.menu_scelta
MIME="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

# --- DASHBOARD CON MENU VISIBILE ---
if scelta=="Dashboard":
    st.markdown("## 🏠 DASHBOARD - MENU COMPLETO DI TUTTI I FORM")
    st.success(f"Benvenuto {st.session_state.username} - Ruolo: {st.session_state.ruolo} - Uso locale e Cloud OK")

    c1,c2,c3=st.columns(3)
    with c1:
        st.markdown('<div class="dashboard-card">',unsafe_allow_html=True)
        st.markdown("### 👥 VOLONTARI")
        st.write(f"{len(st.session_state.dati)} volontari")
        st.write("Form: Anagrafica, Associazione, Ruolo, Comune, Contatti")
        if st.button("👥 APRI VOLONTARI",key="dash_vol",use_container_width=True,type="primary"):
            st.session_state.menu_scelta="Volontari"
            st.rerun()
        st.markdown('</div>',unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="dashboard-card">',unsafe_allow_html=True)
        st.markdown("### 📍 MAPPA POSTAZIONI")
        st.write(f"{len(st.session_state.postazioni)} postazioni")
        st.write("Anteprima TUTTE + Via associata + 15x15 + Tabella")
        if st.button("📍 APRI MAPPA",key="dash_mappa",use_container_width=True,type="primary"):
            st.session_state.menu_scelta="Mappa Postazioni"
            st.rerun()
        st.markdown('</div>',unsafe_allow_html=True)

    with c3:
        st.markdown('<div class="dashboard-card">',unsafe_allow_html=True)
        st.markdown("### 💾 BACKUP")
        st.write("Backup Excel completo")
        if st.button("💾 APRI BACKUP",key="dash_backup",use_container_width=True):
            st.session_state.menu_scelta="Backup"
            st.rerun()
        st.markdown('</div>',unsafe_allow_html=True)

    if st.session_state.ruolo=="Amministratore":
        c4,c5=st.columns(2)
        with c4:
            st.markdown('<div class="dashboard-card">',unsafe_allow_html=True)
            st.markdown("### 🎨 GESTIONE LOGHI")
            st.write(f"{len(st.session_state.icone_lib)} loghi 15x15")
            if st.button("🎨 APRI LOGHI",key="dash_loghi",use_container_width=True):
                st.session_state.menu_scelta="Gestione Loghi"
                st.rerun()
            st.markdown('</div>',unsafe_allow_html=True)
        with c5:
            st.markdown('<div class="dashboard-card">',unsafe_allow_html=True)
            st.markdown("### 👤 GESTIONE UTENTI")
            st.write(f"{len(st.session_state.utenti)} utenti")
            st.write("Solo Amministratore")
            if st.button("👤 GESTISCI UTENTI",key="dash_utenti",use_container_width=True):
                st.session_state.menu_scelta="Gestione Utenti"
                st.rerun()
            st.markdown('</div>',unsafe_allow_html=True)

    st.divider()
    st.markdown("### 📊 RIEPILOGO PROGETTO")
    st.info("Progetto usabile sia in locale (PC) che su Streamlit Cloud - Con utenti Admin e Utente che inserisce e visualizza")

elif scelta=="Volontari":
    torna_dashboard()
    st.markdown("## 👥 VOLONTARI")
    if st.session_state.ruolo=="Utente": st.info("Ruolo Utente: puoi inserire e visualizzare")
    with st.form("form_vol"):
        c1,c2=st.columns(2)
        with c1:
            nome=st.text_input("Nome *")
            cognome=st.text_input("Cognome *")
            cell=st.text_input("Cellulare *")
        with c2:
            assoc=st.text_input("Associazione *",value="ANA Varese")
            comune=st.selectbox("Comune",COMUNI,index=0)
            ruolo=st.selectbox("Ruolo *",["Volontario","Caposquadra","Coordinatore"])
        if st.form_submit_button("✅ SALVA",use_container_width=True,type="primary"):
            if nome and cognome and cell and assoc:
                st.session_state.dati.append({"Nome":f"{nome} {cognome}","Associazione":assoc,"Cellulare":cell,"Comune":comune,"Ruolo":ruolo})
                save_json(FILE_DATI,st.session_state.dati)
                st.success(f"Salvato {nome} {cognome}")
                st.rerun()
    if st.session_state.dati:
        st.dataframe(pd.DataFrame(st.session_state.dati),use_container_width=True)
        out=BytesIO()
        pd.DataFrame(st.session_state.dati).to_excel(out,index=False,engine="openpyxl")
        st.download_button("📥 Excel",out.getvalue(),file_name=f"volontari_{date.today()}.xlsx",mime=MIME,use_container_width=True)

elif scelta=="Mappa Postazioni":
    torna_dashboard()
    st.markdown("## 📍 MAPPA POSTAZIONI - CON TABELLA POSTAZIONI NEL FORM MAPPA")

    st.markdown("### 🎨 Libreria loghi 15x15")
    uploaded=st.file_uploader("📤 CARICA LOGO PNG", type=["png","jpg","jpeg"], key="up_logo")
    if uploaded:
        b64=img_to_b64(uploaded)
        nome_icona=st.text_input("Nome logo", value=uploaded.name.split(".")[0])
        if st.button("💾 SALVA LOGO 15x15",use_container_width=True,type="primary"):
            st.session_state.icone_lib.append({"nome":nome_icona,"b64":b64})
            save_json(FILE_ICONE,st.session_state.icone_lib)
            st.success(f"Logo {nome_icona} salvato!")
            st.rerun()
    if st.session_state.icone_lib:
        cols=st.columns(6)
        for i, ic in enumerate(st.session_state.icone_lib):
            with cols[i%6]:
                st.markdown(f'<div class="icon-lib">',unsafe_allow_html=True)
                if ic.get("b64"):
                    st.image(f"data:image/png;base64,{ic['b64']}",width=40)
                    st.write(f"**{ic['nome']}**")
                    st.caption("15x15")
                    if st.button(f"✅ SEL",key=f"sel_{i}_{ic['nome']}",use_container_width=True,type="primary"):
                        st.session_state.map_logo=ic['nome']
                        st.rerun()
                st.markdown('</div>',unsafe_allow_html=True)
    st.divider()

    c1,c2=st.columns([2,1])
    with c1:
        st.markdown("### 🗺️ MAPPA SELEZIONE - Clicca per associare Via in maschera")
        try:
            import folium
            from streamlit_folium import st_folium
            m=folium.Map(location=[st.session_state.map_lat, st.session_state.map_lon], zoom_start=15)
            for idx_p, p in enumerate(st.session_state.postazioni):
                try:
                    lat_f=float(p.get('Latitudine')); lon_f=float(p.get('Longitudine'))
                    logo_nome=p.get('Icona',''); b64=trova_b64_logo(logo_nome, st.session_state.icone_lib)
                    popup_text=f"{p.get('Postazione','')} - {p.get('Via','')}"
                    if b64:
                        tmp_path=salva_icona_temp(b64, f"sel_{logo_nome}_{idx_p}")
                        if tmp_path:
                            icon=folium.CustomIcon(tmp_path, icon_size=(15,15))
                            folium.Marker([lat_f, lon_f], popup=popup_text, icon=icon).add_to(m)
                        else:
                            folium.Marker([lat_f, lon_f], popup=popup_text, icon=folium.Icon(color="green")).add_to(m)
                    else:
                        folium.Marker([lat_f, lon_f], popup=popup_text, icon=folium.Icon(color="green")).add_to(m)
                except: pass
            map_data=st_folium(m,width=700,height=400,key="mappa_sel")
            if map_data and map_data.get("last_clicked"):
                lat_c=map_data["last_clicked"]["lat"]; lon_c=map_data["last_clicked"]["lng"]
                st.session_state.map_lat=lat_c; st.session_state.map_lon=lon_c
                via_auto, comune_auto=reverse_geocode(lat_c, lon_c)
                st.session_state.map_via=via_auto or f"{lat_c:.6f},{lon_c:.6f}"
                if comune_auto: st.session_state.map_comune=comune_auto
                st.session_state.post_sel=None
                st.toast(f"Via: {st.session_state.map_via} associata in maschera")
                st.rerun()
        except Exception as e: st.error(f"Errore: {e}")

        st.markdown("### 🔍 ANTEPRIMA - TUTTE LE POSTAZIONI CON ICONE 15x15")
        tipo_mappa=st.selectbox("Tipo mappa", ["StreetMap","OpenTopoMap (OTM)","Google Maps Stradale","Google Satellite","Waze Style"], index=0)
        try:
            import folium
            from streamlit_folium import st_folium
            lat_center=45.8205; lon_center=8.8250; zoom_anteprima=13
            if st.session_state.postazioni:
                lats=[float(p.get('Latitudine')) for p in st.session_state.postazioni if p.get('Latitudine')]
                lons=[float(p.get('Longitudine')) for p in st.session_state.postazioni if p.get('Longitudine')]
                if lats and lons:
                    lat_center=sum(lats)/len(lats); lon_center=sum(lons)/len(lons)
            if st.session_state.post_sel:
                try:
                    lat_center=float(st.session_state.post_sel.get('Latitudine',lat_center))