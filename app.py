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
.quick-btn>button{background:linear-gradient(135deg,#ff9800,#ef6c00)!important;min-height:90px!important;font-size:15px!important;}
.quick-btn-green>button{background:linear-gradient(135deg,#2e7d32,#1b5e20)!important;min-height:90px!important;font-size:15px!important;}
.quick-btn-red>button{background:linear-gradient(135deg,#c62828,#b71c1c)!important;min-height:90px!important;}
.quick-btn-blue>button{background:linear-gradient(135deg,#1565c0,#0d47a1)!important;min-height:90px!important;}
.vol-selected{background:#fff3e0!important;border:4px solid #ef6c00!important;border-radius:12px!important;padding:20px!important;margin:10px 0!important;}
.submask{background:#f1f8e9!important;border:3px solid #2e7d32!important;border-radius:12px!important;padding:15px!important;margin:8px 0!important;}
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
COMUNI=["Varese","Busto Arsizio","Gallarate","Saronno","Venegono Superiore","Venegono Inferiore","Castiglione Olona","Lozza","Tradate","Malnate","Luino"]
ICONS=["📍","🚨","🏕️","🚧","👥","🔥","🌊","⛰️","🚑","🚒","🦺","📻","🏠"]

for k,v in [("dati",[]),("postazioni",[]),("vol_dettagli",{}),("interventi_lista",[]),("menu_scelta","Dashboard"),("volontario_selezionato",None),("volontario_idx",None),("form_nome",""),("form_cognome",""),("form_cell",""),("form_assoc","ANA Varese"),("map_lat",45.8205),("map_lon",8.8250),("map_comune","Varese"),("map_via",""),("authenticated",False)]:
    if k not in st.session_state: st.session_state[k]=v

if not st.session_state.dati: st.session_state.dati=load_json(FILE_DATI,[])
if not st.session_state.postazioni: st.session_state.postazioni=load_json(FILE_POST,[])
if not st.session_state.interventi_lista: st.session_state.interventi_lista=load_json(FILE_INTERVENTI,[])

def header_loghi():
    b64=get_b64("logo.png")
    if b64:
        st.markdown(f"<div style='display:flex;justify-content:center;align-items:center;gap:25px;background:#a5d6a7;padding:15px;border-radius:15px;border:3px solid #2e7d32;margin-bottom:15px;'><img src='data:image/png;base64,{b64}' style='width:90px;height:90px;border-radius:50%;border:3px solid #1b5e20;background:white;'><h2 style='color:#0e7a3d;margin:0;text-align:center;'>VOLONTARIATO<br>Sezione di Varese</h2><img src='data:image/png;base64,{b64}' style='width:90px;height:90px;border-radius:50%;border:3px solid #1b5e20;background:white;'></div>", unsafe_allow_html=True)
    else:
        st.markdown("<h2 style='text-align:center;color:#0e7a3d;'>VOLONTARIATO<br>Sezione di Varese</h2>", unsafe_allow_html=True)

# LOGIN PAGE COME IERI
if not st.session_state.authenticated:
    header_loghi()
    st.markdown("<h2 style='text-align:center;color:#2e7a3d;'>🔒 Accesso Riservato</h2>", unsafe_allow_html=True)
    c1,c2,c3=st.columns([1,2,1])
    with c2:
        with st.form("login"):
            u=st.text_input("Username",value="admin")
            p=st.text_input("Password",type="password",value="ana2024")
            if st.form_submit_button("🔴 ACCEDI",use_container_width=True,type="primary"):
                if (u=="admin" and p=="ana2024") or p=="ANA2025" or p=="admin":
                    st.session_state.authenticated=True
                    st.rerun()
                else:
                    st.error("Password errata")
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
    st.markdown("### ⚡ Tasti tutti allineati a posto")
    # RIGA 1 - 4 tasti allineati uguali
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
        st.markdown('<div class="quick-btn">',unsafe_allow_html=True)
        if st.button("💾\nBACKUP\nExcel",key="q_back",use_container_width=True):
            st.session_state.menu_scelta="Backup"; st.rerun()
        st.markdown('</div>',unsafe_allow_html=True)
    # RIGA 2 - altri 4 allineati
    c5,c6,c7,c8=st.columns(4)
    with c5:
        if st.button("➕\nNUOVO\nVolontario",key="q_new_vol",use_container_width=True):
            st.session_state.volontario_selezionato=None; st.session_state.form_nome=""; st.session_state.form_cognome=""; st.session_state.form_cell=""; st.session_state.menu_scelta="Volontari"; st.rerun()
    with c6:
        if st.button("📍\nNUOVA\nPostazione",key="q_new_post",use_container_width=True):
            st.session_state.menu_scelta="Mappa Postazioni"; st.rerun()
    with c7:
        if st.button("🚨\nNUOVA\nEmergenza",key="q_new_em",use_container_width=True):
            st.session_state.menu_scelta="Tabella Emergenze"; st.rerun()
    with c8:
        if st.button("🔄\nAGGIORNA",key="q_refresh",use_container_width=True):
            st.rerun()
    st.divider()
    c1,c2,c3,c4=st.columns(4)
    c1.metric("👥 Volontari",len(st.session_state.dati))
    c2.metric("📍 Postazioni",len(st.session_state.postazioni))
    c3.metric("🚨 Emergenze",len(st.session_state.interventi_lista))
    c4.metric("📅 Oggi",date.today().strftime("%d/%m/%Y"))

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
        t1,t2,t3,t4,t5,t6=st.tabs(["📋 Anagrafica","📻 Radio","📅 Eventi","✅ Presenze","🚨 Emergenze","📄 Note"])
        with t1:
            st.markdown('<div class="submask">',unsafe_allow_html=True)
            st.markdown("#### Sottomaschera 1 - Anagrafica Completa")
            with st.form("form_anag"):
                parti=vol.get('Nome','').split(" ",1)
                nome=st.text_input("Nome *",value=parti[0] if len(parti)>0 else "")
                cognome=st.text_input("Cognome *",value=parti[1] if len(parti)>1 else "")
                cell=st.text_input("Cellulare *",value=vol.get('Cellulare',''))
                comune=st.selectbox("Comune",COMUNI,index=0)
                ruolo=st.selectbox("Ruolo",["Volontario","Caposquadra","Coordinatore","Autista","Radio","Logistica"],index=0)
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
            note=st.text_area("Note",value=st.session_state.vol_dettagli.get(vol_id,{}).get('Note',''))
            if st.button("Salva Note"):
                if vol_id not in st.session_state.vol_dettagli: st.session_state.vol_dettagli[vol_id]={}
                st.session_state.vol_dettagli[vol_id]['Note']=note
                save_json(FILE_DETTAGLI,st.session_state.vol_dettagli)
                st.success("Salvata!")
            if st.button(f"ELIMINA {vol.get('Nome','')}"):
                st.session_state.dati.pop(idx); save_json(FILE_DATI,st.session_state.dati); st.session_state.volontario_selezionato=None; st.session_state.volontario_idx=None; st.rerun()
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
            ruolo=st.selectbox("Ruolo *",["Volontario","Caposquadra","Coordinatore","Autista","Radio","Logistica","Segreteria","Sanitario","Altro"])
        col1,col2=st.columns(2)
        with col1: sub=st.form_submit_button("✅ SALVA",use_container_width=True)
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
            st.session_state.volontario_selezionato=None; st.session_state.volontario_idx=None; st.rerun()
    st.divider()
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
    if st.button("🏠 Dashboard",use_container_width=True):
        st.session_state.menu_scelta="Dashboard"; st.rerun()
    st.markdown("## 📍 MAPPA POSTAZIONI - Con Google / OSM / Waze")
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
        # LINK GOOGLE MAPS / OSM / WAZE COME IERI
        st.markdown("### 🌐 Apri in:")
        lat=st.session_state.map_lat; lon=st.session_state.map_lon
        c_osm,c_gm,c_waze=st.columns(3)
        with c_osm: st.link_button("🗺️ OpenStreetMap", f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=16/{lat}/{lon}", use_container_width=True)
        with c_gm: st.link_button("🔍 Google Maps", f"https://www.google.com/maps/search/?api=1&query={lat},{lon}", use_container_width=True)
        with c_waze: st.link_button("🚗 Waze", f"https://waze.com/ul?ll={lat},{lon}&navigate=yes", use_container_width=True)
    with c2:
        st.info(f"📍 {st.session_state.map_lat:.6f}, {st.session_state.map_lon:.6f}")
        with st.form("form_post"):
            nome_post=st.text_input("Nome Postazione *")
            comune_post=st.selectbox("Comune *",COMUNI,index=COMUNI.index(st.session_state.map_comune) if st.session_state.map_comune in COMUNI else 0)
            via_post=st.text_input("Via *",value=st.session_state.map_via)
            lat_post=st.text_input("Latitudine *",value=str(st.session_state.map_lat))
            lon_post=st.text_input("Longitudine *",value=str(st.session_state.map_lon))
            icona_post=st.selectbox("Icona",ICONS,index=0)
            if st.form_submit_button("📍 SALVA CON ICONA",use_container_width=True,type="primary"):
                if nome_post and lat_post and lon_post:
                    new={"Postazione":nome_post,"Comune":comune_post,"Via":via_post,"Latitudine":lat_post,"Longitudine":lon_post,"Icona":icona_post}
                    st.session_state.postazioni.append(new); save_json(FILE_POST,st.session_state.postazioni); st.success(f"{icona_post} {nome_post} salvata!"); st.rerun()
    st.divider()
    if st.session_state.postazioni:
        st.markdown("### Postazioni con link Google / OSM / Waze")
        for p in st.session_state.postazioni:
            c1,c2,c3=st.columns([2,2,3])
            with c1: st.write(f"{p.get('Icona','📍')} {p.get('Postazione','')}")
            with c2: st.write(f"{p.get('Via','')} {p.get('Comune','')}")
            with c3:
                lat=p.get('Latitudine',''); lon=p.get('Longitudine','')
                ca,cb,cc=st.columns(3)
                with ca: st.link_button("OSM",f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=16/{lat}/{lon}")
                with cb: st.link_button("Google",f"https://www.google.com/maps/search/?api=1&query={lat},{lon}")
                with cc: st.link_button("Waze",f"https://waze.com/ul?ll={lat},{lon}&navigate=yes")

elif scelta=="Tabella Emergenze":
    if st.button("🏠 Dashboard",use_container_width=True):
        st.session_state.menu_scelta="Dashboard"; st.rerun()
    st.markdown("## 🚨 TABELLA EMERGENZE")
    with st.form("form_em",clear_on_submit=True):
        c1,c2,c3=st.columns(3)
        with c1:
            data_int=st.date_input("Data *",value=date.today())
            ora_int=st.time_input("Ora *",value=datetime.now().time())
        with c2:
            comune_int=st.text_input("Comune *",placeholder="Varese")
            via_int=st.text_input("Via *",placeholder="Via Roma")
        with c3:
            civico_int=st.text_input("Civico",placeholder="10")
            odv_int=st.selectbox("ODV *",["ANA Varese","Protezione Civile Lombardia","Croce Rossa","Altro"])
        azione_int=st.text_area("Azione *",height=100)
        if st.form_submit_button("🔴 SALVA",use_container_width=True):
            if comune_int and via_int and azione_int:
                st.session_state.interventi_lista.append({"Data":str(data_int),"Ora":str(ora_int),"Comune":comune_int,"Via":via_int,"Civico":civico_int,"ODV Operativa":odv_int,"Azione":azione_int})
                save_json(FILE_INTERVENTI,st.session_state.interventi_lista)
                st.success("Salvato!"); st.rerun()
    if st.session_state.interventi_lista:
        st.dataframe(pd.DataFrame(st.session_state.interventi_lista),use_container_width=True)

elif scelta=="Backup":
    if st.button("🏠 Dashboard",use_container_width=True):
        st.session_state.menu_scelta="Dashboard"; st.rerun()
    st.markdown("## 💾 BACKUP")
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