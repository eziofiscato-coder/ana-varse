import streamlit as st
import pandas as pd
from datetime import datetime, date
from io import BytesIO
import base64, os
import json

st.set_page_config(page_title="ANA Varese - Verde ANA", page_icon="🟢", layout="wide")

st.markdown("""
<style>
.stApp{background-color:#e8f5e9!important;}
.main.block-container{background-color:white!important; border-radius:18px; padding:25px!important;}
[data-testid="stSidebar"]{background-color:#a5d6a7!important; border-right:4px solid #2e7d32!important;}
.stForm{background-color:#c8e6c9!important; border:3px solid #2e7d32!important; border-radius:15px!important; padding:20px!important;}
.stTextInput input,.stSelectbox div[data-baseweb="select"],.stDateInput input,.stNumberInput input,.stTextArea textarea {
    background-color:white!important; color:#1b5e20!important; border:2px solid #2e7d32!important;
}
.stButton>button{background-color:#2e7d32!important; color:white!important; border:2px solid #1b5e20!important; font-weight:bold!important; border-radius:12px!important; min-height:60px!important;}
div[data-testid="stFormSubmitButton"]>button{background-color:#d32f2f!important; color:white!important;}
h1,h2,h3{color:#1b5e20!important;}
</style>
""", unsafe_allow_html=True)

ICONS = {
 "volontario": {"nome":"Volontario","icon":"👤"}, "sede": {"nome":"Sede","icon":"🏠"},
 "radio": {"nome":"Radio","icon":"📻"}, "emergenza": {"nome":"Emergenza","icon":"🚨"},
 "protezione_civile": {"nome":"Prot Civile","icon":"🛡️"}, "ospedale": {"nome":"Ospedale","icon":"🏥"},
 "postazione": {"nome":"Postazione","icon":"📍"}, "auto": {"nome":"Auto","icon":"🚗"},
 "elicottero": {"nome":"Elicottero","icon":"🚁"}, "incendio": {"nome":"Incendio","icon":"🔥"},
 "alluvione": {"nome":"Alluvione","icon":"🌊"}, "campo_base": {"nome":"Campo Base","icon":"⛺"},
}

for k,v in [("authenticated",False),("emergenze_lista",[]),("interventi_lista",[]),("dati",[]),("mem_nomi",["Mario Rossi","Luigi Bianchi","Giuseppe Verdi"]),("postazioni",[]),("radio_db",[]),("dist_radio",[]),("menu_scelta","🏠 Dashboard"),("selected_postazione",None)]:
    if k not in st.session_state:
        st.session_state[k]=v

def get_b64(p):
    try:
        if os.path.exists(p):
            with open(p,"rb") as f: return base64.b64encode(f.read()).decode()
    except: pass
    return ""

def torna_dashboard():
    if st.button("Torna Dashboard", use_container_width=True):
        st.session_state.menu_scelta="🏠 Dashboard"; st.rerun()

def header_3_loghi():
    c1,c2,c3=st.columns([1,1,1])
    try:
        if os.path.exists("logo.png"): c1.image("logo.png", width=80)
        else: c1.markdown("**ANA Varese**")
    except: c1.markdown("**Logo 1**")
    try:
        if os.path.exists("logo2.png"): c2.image("logo2.png", width=80)
        else: c2.markdown("**Logo 2**")
    except: c2.markdown("**Logo 2**")
    try:
        if os.path.exists("logo_pc_lombardia.png"): c3.image("logo_pc_lombardia.png", width=80)
        else:
            for nf in ["logo_pc.png","protezione-civile-regione-lombardia-logo-png_seeklogo-113086.png"]:
                if os.path.exists(nf):
                    c3.image(nf, width=80); break
            else: c3.markdown("**Prot Civile Lombardia**")
    except: c3.markdown("**Prot Civile**")

if not st.session_state.authenticated:
    st.markdown("""<style>[data-testid="stSidebar"]{display:none;}</style>""", unsafe_allow_html=True)
    header_3_loghi()
    st.divider()
    st.markdown("<h2 style='text-align:center; color:#2e7d32;'>Accesso Riservato<br>ANA Varese</h2>", unsafe_allow_html=True)
    c1,c2,c3=st.columns([1,2,1])
    with c2:
        with st.form("login_form"):
            u=st.text_input("Username", value="admin"); p=st.text_input("Password", type="password", value="ana2024")
            st.caption("admin / ana2024")
            if st.form_submit_button("Accedi", use_container_width=True, type="primary"):
                if u=="admin" and p=="ana2024":
                    st.session_state.authenticated=True; st.rerun()
                else: st.error("Password errata!")
    st.stop()

header_3_loghi()
st.divider()

with st.sidebar:
    st.image("logo.png", width=100) if os.path.exists("logo.png") else st.markdown("### ANA Varese")
    opzioni=["🏠 Dashboard","🚨 Emergenze con Loghi","🗺️ Mappa Postazioni","🚨 Interventi Emergenza","👥 Volontari","📻 DB Radio Inventario","📦 Distribuzione Radio","💾 Backup"]
    idx = opzioni.index(st.session_state.menu_scelta) if st.session_state.menu_scelta in opzioni else 0
    sel=st.radio("MENU", opzioni, index=idx)
    if sel!=st.session_state.menu_scelta:
        st.session_state.menu_scelta=sel; st.rerun()
    if st.button("Logout", use_container_width=True, type="primary"):
        st.session_state.authenticated=False; st.rerun()

scelta=st.session_state.menu_scelta
st.markdown(f"## {scelta}")
st.divider()

if scelta=="🏠 Dashboard":
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Interventi", len(st.session_state.interventi_lista))
    c2.metric("Emergenze", len(st.session_state.emergenze_lista))
    c3.metric("Volontari", len(st.session_state.mem_nomi))
    c4.metric("Postazioni", len(st.session_state.postazioni))
    c5,c6=st.columns(2)
    c5.metric("Radio in DB", len(st.session_state.radio_db))
    c6.metric("Distribuzioni", len(st.session_state.dist_radio))
    st.markdown("### MENU SCELTA RAPIDA - TUTTI ATTIVI")
    r1c1,r1c2,r1c3,r1c4=st.columns(4)
    with r1c1:
        if st.button("Emergenze con Loghi", key="q1", use_container_width=True):
            st.session_state.menu_scelta="🚨 Emergenze con Loghi"; st.rerun()
    with r1c2:
        if st.button("Mappa Postazioni", key="q2", use_container_width=True):
            st.session_state.menu_scelta="🗺️ Mappa Postazioni"; st.rerun()
    with r1c3:
        if st.button("Interventi", key="q3", use_container_width=True):
            st.session_state.menu_scelta="🚨 Interventi Emergenza"; st.rerun()
    with r1c4:
        if st.button("Volontari", key="q4", use_container_width=True):
            st.session_state.menu_scelta="👥 Volontari"; st.rerun()
    r2c1,r2c2,r2c3=st.columns(3)
    with r2c1:
        if st.button("DB Radio", key="q5", use_container_width=True):
            st.session_state.menu_scelta="📻 DB Radio Inventario"; st.rerun()
    with r2c2:
        if st.button("Distribuzione Radio", key="q6", use_container_width=True):
            st.session_state.menu_scelta="📦 Distribuzione Radio"; st.rerun()
    with r2c3:
        if st.button("Aggiorna", key="q7", use_container_width=True):
            st.rerun()

elif scelta=="🚨 Emergenze con Loghi":
    torna_dashboard()
    st.markdown("#### Libreria Loghi")
    cols=st.columns(6)
    for i,(k,v) in enumerate(ICONS.items()):
        with cols[i%6]:
            st.markdown(f"<div style='background:white; border:2px solid #2e7d32; border-radius:10px; padding:8px; text-align:center;'><div style='font-size:28px;'>{v['icon']}</div><div style='font-size:10px;'>{v['nome']}</div></div>", unsafe_allow_html=True)
    st.divider()
    with st.form("form_em", clear_on_submit=True):
        c1,c2,c3=st.columns(3)
        with c1: data_em=st.date_input("Data *", value=date.today()); comune=st.text_input("Comune *", value="Varese")
        with c2: via=st.text_input("Via *"); tipo_key=st.selectbox("Tipo + Logo *", list(ICONS.keys()), format_func=lambda x: f"{ICONS[x]['icon']} {ICONS[x]['nome']}")
        with c3: odv=st.selectbox("ODV", ["ANA Varese","Prot Civile","Altro"]); st.markdown(f"<div style='background:#c8e6c9; border:3px solid #2e7d32; border-radius:12px; padding:10px; text-align:center;'><div style='font-size:40px;'>{ICONS[tipo_key]['icon']}</div><b>{ICONS[tipo_key]['nome']}</b></div>", unsafe_allow_html=True)
        desc=st.text_area("Descrizione *", height=80)
        if st.form_submit_button("SALVA CON LOGO", use_container_width=True, type="primary"):
            if comune and via and desc:
                st.session_state.emergenze_lista.append({"Data":str(data_em),"Logo":ICONS[tipo_key]['icon'],"Tipo":ICONS[tipo_key]['nome'],"Comune":comune,"Via":via,"ODV":odv,"Descrizione":desc})
                st.success(f"Salvata {ICONS[tipo_key]['icon']}!"); st.balloons(); st.rerun()
    if st.session_state.emergenze_lista:
        df=pd.DataFrame(st.session_state.emergenze_lista)
        st.markdown(f"### Tabella {len(df)} Emergenze con Logo")
        for idx,row in df.iterrows():
            with st.container(border=True):
                cL,cI=st.columns([1,4])
                with cL: st.markdown(f"<div style='font-size:45px; text-align:center; background:#e8f5e9; border:2px solid #2e7d32; border-radius:12px; padding:10px;'>{row['Logo']}</div>", unsafe_allow_html=True)
                with cI: st.markdown(f"**{row['Logo']} {row['Tipo']}** | {row['Comune']} {row['Via']} | {row['Data']}"); st.write(row['Descrizione'])
        st.dataframe(df, use_container_width=True)
    torna_dashboard()

elif scelta=="🗺️ Mappa Postazioni":
    torna_dashboard()
    with st.container(border=True):
        st.markdown("#### Mappa FULLSCREEN - Google Map e OpenStreetMap")
        if st.session_state.get("selected_postazione"):
            st.success(f"Evidenziata: {st.session_state.selected_postazione}")
        with st.expander("Aggiungi Postazione", expanded=True):
            with st.form("form_post", clear_on_submit=True):
                c1,c2,c3=st.columns(3)
                with c1: nome_post=st.text_input("Nome Postazione *"); comune_post=st.text_input("Comune *", value="Varese"); via_post=st.text_input("Via *")
                with c2: lat=st.text_input("Latitudine *", placeholder="45.8205"); lon=st.text_input("Longitudine *", placeholder="8.8255"); civico_post=st.text_input("Civico")
                with c3: resp_post=st.text_input("Responsabile"); radio_post=st.text_input("Radio"); tipo_post=st.selectbox("Tipo", ["Controllo accessi","Viabilita","Sicurezza","Logistica","COC","Altro"])
                note_post=st.text_input("Note")
                if st.form_submit_button("Aggiungi alla Mappa", use_container_width=True, type="primary"):
                    if nome_post and lat and lon:
                        st.session_state.postazioni.append({"Data":str(date.today()),"Postazione":nome_post,"Comune":comune_post,"Via":via_post,"Civico":civico_post,"Latitudine":lat,"Longitudine":lon,"Responsabile":resp_post,"Radio":radio_post,"Tipo":tipo_post,"Note":note_post})
                        st.success(f"{nome_post} aggiunta!"); st.rerun()
        if st.session_state.postazioni:
            df_post=pd.DataFrame(st.session_state.postazioni)
            if "map_type" not in st.session_state: st.session_state.map_type="OpenStreetMap"
            map_type=st.selectbox("Tipo Mappa:", ["OpenStreetMap","Google Stradale","Google Satellite","Google Ibrida","Google Rilievo"], index=["OpenStreetMap","Google Stradale","Google Satellite","Google Ibrida","Google Rilievo"].index(st.session_state.map_type))
            st.session_state.map_type=map_type
            if st.session_state.get("selected_postazione"):
                for _, r in df_post.iterrows():
                    if r.get("Postazione")==st.session_state.selected_postazione:
                        lat_s=r.get("Latitudine"); lon_s=r.get("Longitudine")
                        st.markdown(f"**Naviga verso: {st.session_state.selected_postazione}**")
                        c1,c2,c3,c4=st.columns(4)
                        with c1: st.link_button("Google Maps", f"https://www.google.com/maps/search/?api=1&query={lat_s},{lon_s}", use_container_width=True, type="primary")
                        with c2: st.link_button("Google Naviga", f"https://www.google.com/maps/dir/?api=1&destination={lat_s},{lon_s}", use_container_width=True)
                        with c3: st.link_button("Waze", f"https://waze.com/ul?ll={lat_s},{lon_s}&navigate=yes&zoom=17", use_container_width=True)
                        with c4: st.link_button("OpenStreetMap", f"https://www.openstreetmap.org/?mlat={lat_s}&mlon={lon_s}#map=18/{lat_s}/{lon_s}", use_container_width=True)
            st.markdown("**Clicca postazione per centrare:**")
            cols_map=st.columns(3)
            for idx, p in enumerate(st.session_state.postazioni):
                with cols_map[idx%3]:
                    nome=p.get("Postazione","")
                    is_sel=st.session_state.get("selected_postazione")==nome
                    if st.button(f"{'⭐' if is_sel else '📍'} {nome}", key=f"map_sel_{idx}", use_container_width=True, type="primary" if is_sel else "secondary"):
                        st.session_state.selected_postazione=nome; st.rerun()
            try:
                import folium
                from streamlit_folium import st_folium
                selected=st.session_state.get("selected_postazione")
                center_lat, center_lon=45.8205, 8.8255; zoom=14
                if selected:
                    for _, r in df_post.iterrows():
                        if r.get("Postazione")==selected:
                            try: center_lat=float(str(r.get("Latitudine")).replace(",",".")); center_lon=float(str(r.get("Longitudine")).replace(",",".")); zoom=17
                            except: pass
                if map_type=="OpenStreetMap": m=folium.Map(location=[center_lat, center_lon], zoom_start=zoom, tiles="OpenStreetMap")
                elif map_type=="Google Stradale": m=folium.Map(location=[center_lat, center_lon], zoom_start=zoom, tiles=None); folium.TileLayer('https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}', attr='Google', name='Google Stradale', max_zoom=20).add_to(m)
                elif map_type=="Google Satellite": m=folium.Map(location=[center_lat, center_lon], zoom_start=zoom, tiles=None); folium.TileLayer('https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', attr='Google', name='Google Satellite', max_zoom=20).add_to(m)
                elif map_type=="Google Ibrida": m=folium.Map(location=[center_lat, center_lon], zoom_start=zoom, tiles=None); folium.TileLayer('https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr='Google', name='Google Ibrida', max_zoom=20).add_to(m)
                elif map_type=="Google Rilievo": m=folium.Map(location=[center_lat, center_lon], zoom_start=zoom, tiles=None); folium.TileLayer('https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}', attr='Google', name='Google Rilievo', max_zoom=20).add_to(m)
                try:
                    from folium.plugins import Fullscreen, LocateControl
                    Fullscreen(position="topleft").add_to(m); LocateControl().add_to(m)
                except: pass
                for _, r in df_post.iterrows():
                    try:
                        lat_f=float(str(r.get("Latitudine")).replace(",",".")); lon_f=float(str(r.get("Longitudine")).replace(",","."))
                        nome_p=r.get('Postazione',''); is_sel=nome_p==selected
                        popup=f"<b>{nome_p}</b><br>{r.get('Via','')} {r.get('Civico','')}, {r.get('Comune','')}<br><a href='https://www.google.com/maps/search/?api=1&query={lat_f},{lon_f}' target='_blank'>Google Maps</a> | <a href='https://waze.com/ul?ll={lat_f},{lon_f}&navigate=yes' target='_blank'>Waze</a>"
                        folium.Marker([lat_f, lon_f], popup=folium.Popup(popup, max_width=250), tooltip=nome_p, icon=folium.Icon(color="red" if is_sel else "green", icon="star" if is_sel else "info-sign")).add_to(m)
                    except: pass
                st_folium(m, width=1400, height=600, use_container_width=True)
            except ImportError:
                st.warning("Aggiungi folium e streamlit-folium ai requirements.txt")
                try:
                    dfm=df_post.copy(); dfm["lat"]=pd.to_numeric(dfm["Latitudine"].astype(str).str.replace(",","."), errors='coerce'); dfm["lon"]=pd.to_numeric(dfm["Longitudine"].astype(str).str.replace(",","."), errors='coerce')
                    dfm=dfm.dropna(subset=["lat","lon"])
                    if not dfm.empty: st.map(dfm[["lat","lon"]], zoom=11)
                except: pass
            st.dataframe(df_post, use_container_width=True, hide_index=True)
            for _, r in df_post.iterrows():
                with st.container(border=True):
                    c1,c2,c3,c4=st.columns([2,1,1,1])
                    with c1: st.markdown(f"**{r['Postazione']}** - {r['Comune']} {r['Via']}")
                    with c2: st.link_button("Google Map", f"https://www.google.com/maps/search/?api=1&query={r['Latitudine']},{r['Longitudine']}", use_container_width=True)
                    with c3: st.link_button("OpenStreetMap", f"https://www.openstreetmap.org/?mlat={r['Latitudine']}&mlon={r['Longitudine']}#map=17/{r['Latitudine']}/{r['Longitudine']}", use_container_width=True)
                    with c4: st.link_button("Waze", f"https://waze.com/ul?ll={r['Latitudine']},{r['Longitudine']}&navigate=yes", use_container_width=True)
        else:
            st.info("Nessuna postazione")
    torna_dashboard()

elif scelta=="📻 DB Radio Inventario":
    torna_dashboard()
    with st.container(border=True):
        st.markdown("#### Database Radio - Form del 15 Settembre")
        with st.form("form_radio_db"):
            c1,c2,c3,c4=st.columns(4)
            with c1: radio_id_db=st.text_input("Radio ID *", placeholder="R-01"); modello_db=st.selectbox("Modello *", ["Baofeng UV-5R","Motorola T82","Midland G9","Altro"])
            with c2: seriale=st.text_input("Seriale"); frequenza=st.text_input("Frequenza", placeholder="145.500 MHz")
            with c3: batteria=st.selectbox("Batteria", ["Carica","Da caricare","Guasta","Nuova"]); accessori=st.text_input("Accessori")
            with c4: stato_radio_db=st.selectbox("Stato", ["Disponibile","In uso","Guasta","In riparazione"]); note_radio_db=st.text_input("Note")
            if st.form_submit_button("Salva Radio nel DB", use_container_width=True, type="primary"):
                if radio_id_db and modello_db:
                    if any(r.get("Radio ID")==radio_id_db for r in st.session_state.radio_db): st.error(f"Radio {radio_id_db} gia esistente!")
                    else:
                        st.session_state.radio_db.append({"Radio ID":radio_id_db,"Modello":modello_db,"Seriale":seriale,"Frequenza":frequenza,"Batteria":batteria,"Accessori":accessori,"Stato":stato_radio_db,"Note":note_radio_db,"Data Inserimento":str(date.today())})
                        st.success(f"Radio {radio_id_db} aggiunta!"); st.rerun()
                else: st.error("Radio ID e Modello obbligatori")
        if st.session_state.radio_db:
            df_db=pd.DataFrame(st.session_state.radio_db).iloc[::-1]
            st.dataframe(df_db, use_container_width=True, hide_index=True)
            col1,col2=st.columns(2)
            with col1:
                out=BytesIO(); df_db.to_excel(out, index=False, engine="openpyxl")
                st.download_button("Scarica Excel DB Radio", out.getvalue(), file_name="db_radio.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
            with col2:
                if st.button("Cancella DB", use_container_width=True):
                    st.session_state.radio_db=[]; st.rerun()
    torna_dashboard()

elif scelta=="📦 Distribuzione Radio":
    torna_dashboard()
    with st.container(border=True):
        st.markdown("#### Distribuzione Radio - Form del 15 Settembre")
        st.caption(f"Volontari disponibili: {len(st.session_state.mem_nomi)}")
        with st.form("form_dist"):
            c1,c2,c3,c4=st.columns(4)
            with c1:
                data_d=st.date_input("Data", value=datetime.now())
                if st.session_state.radio_db:
                    radio_list=[f"{r.get('Radio ID')} | {r.get('Modello')} | {r.get('Stato')}" for r in st.session_state.radio_db]
                    scelta_display=st.selectbox("Radio ID dal DB *", ["-- Seleziona --"]+radio_list)
                    if scelta_display!="-- Seleziona --": radio_id=scelta_display.split(" | ")[0]; modello=scelta_display.split(" | ")[1] if len(scelta_display.split(" | "))>1 else ""
                    else: radio_id=""; modello=""
                    st.session_state["_tmp_radio_id"]=radio_id; st.session_state["_tmp_modello"]=modello
                else:
                    st.error("DB Radio vuoto! Vai in DB Radio")
                    radio_id=st.text_input("Radio ID *", placeholder="R-01"); modello=st.text_input("Modello *"); st.session_state["_tmp_radio_id"]=radio_id; st.session_state["_tmp_modello"]=modello
            with c2:
                assegnatario=st.selectbox("Assegnato A *", ["--"]+st.session_state.mem_nomi); consegnato_da=st.selectbox("Consegnata DA *", ["--"]+st.session_state.mem_nomi)
            with c3:
                opzioni_post=["-- Nuova --"]+[p.get("Postazione","") for p in st.session_state.postazioni]
                scelta_post=st.selectbox("Postazione *", opzioni_post)
                if scelta_post=="-- Nuova --": postazione=st.text_input("Nuova Postazione *", placeholder="Posto 1")
                else: postazione=scelta_post
                canale=st.selectbox("Canale", ["CH 1 - Emergenza","CH 2 - Logistica","CH 3 - Coordinamento","VHF 145.500"])
            with c4:
                ora_cons=st.text_input("Ora consegna", value=datetime.now().strftime("%H:%M")); ora_ric=st.text_input("Ora riconsegna", placeholder="Al rientro"); stato_r=st.selectbox("Stato", ["Consegnata","Riconsegnata","Guasta"])
            note_d=st.text_input("Note", placeholder="Con batteria carica")
            if st.form_submit_button("Assegna Radio", use_container_width=True, type="primary"):
                radio_id_final=st.session_state.get("_tmp_radio_id",""); modello_final=st.session_state.get("_tmp_modello","")
                if radio_id_final and assegnatario!="--" and postazione and consegnato_da!="--" and modello_final:
                    st.session_state.dist_radio.append({"Data":str(data_d),"RadioID":radio_id_final,"Modello":modello_final,"Assegnatario":assegnatario,"Consegnata DA":consegnato_da,"Postazione":postazione,"Canale":canale,"OraConsegna":ora_cons,"OraRiconsegna":ora_ric,"Stato":stato_r,"Note":note_d})
                    st.success(f"Radio {radio_id_final} consegnata a {assegnatario}"); st.rerun()
                else: st.error("Compila Radio, Assegnato A, Consegnata DA, Postazione")
        if st.session_state.dist_radio:
            df_dist=pd.DataFrame(st.session_state.dist_radio).iloc[::-1]
            st.dataframe(df_dist, use_container_width=True, hide_index=True)
            out=BytesIO(); df_dist.to_excel(out, index=False, engine="openpyxl")
            st.download_button("Scarica Excel Distribuzione", out.getvalue(), file_name="distribuzione.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
    torna_dashboard()

else:
    torna_dashboard()
    st.info(f"Sezione {scelta}")
    torna_dashboard()