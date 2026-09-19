import streamlit as st
import pandas as pd
from datetime import date
from io import BytesIO
import os, json, base64, tempfile

st.set_page_config(page_title="ANA Varese", page_icon="🟢", layout="wide")

st.markdown("""
<style>
.stApp{background:#e8f5e9!important;}
.main.block-container{background:white!important;border-radius:18px;padding:20px!important;}
[data-testid="stSidebar"]{background:#a5d6a7!important;border-right:4px solid #2e7d32!important;}
.stForm{background:#c8e6c9!important;border:3px solid #2e7d32!important;border-radius:15px!important;padding:15px!important;}
.stButton>button{background:#2e7d32!important;color:white!important;font-weight:bold!important;min-height:45px!important;border-radius:10px!important;}
div[data-testid="stFormSubmitButton"]>button{background:#d32f2f!important;}
.vol-selected{background:#fff3e0!important;border:4px solid #ef6c00!important;border-radius:12px!important;padding:15px!important;}
.submask{background:#f1f8e9!important;border:3px solid #2e7d32!important;border-radius:12px!important;padding:15px!important;}
.icon-lib{border:3px solid #2e7d32;border-radius:12px;padding:10px;background:white;text-align:center;margin:5px;}
.icon-selected{border:4px solid #ef6c00!important;background:#fff3e0!important;}
</style>
""", unsafe_allow_html=True)

def load_json(f, default):
    try:
        if os.path.exists(f):
            with open(f,"r",encoding="utf-8") as fh:
                d=json.load(fh)
                if isinstance(d,list) or isinstance(d,dict):
                    return d
    except:
        pass
    return default

def save_json(f,d):
    try:
        with open(f,"w",encoding="utf-8") as fh:
            json.dump(d,fh,ensure_ascii=False,indent=2)
    except:
        pass

def get_b64(p):
    try:
        if os.path.exists(p):
            with open(p,"rb") as f:
                return base64.b64encode(f.read()).decode()
    except:
        pass
    return ""

def img_to_b64(file):
    try:
        return base64.b64encode(file.getvalue()).decode()
    except:
        return ""

def trova_b64_logo(nome, libreria):
    for ic in libreria:
        if ic.get("nome")==nome and ic.get("b64"):
            return ic.get("b64")
    return None

def salva_icona_temp(b64, nome):
    try:
        data=base64.b64decode(b64)
        tmp_path=os.path.join(tempfile.gettempdir(), f"icon_{nome.replace(' ','_')}.png")
        with open(tmp_path,"wb") as f:
            f.write(data)
        return tmp_path
    except:
        return None

FILE_DATI="dati_volontari.json"
FILE_POST="postazioni.json"
FILE_INTERVENTI="interventi_emergenza.json"
FILE_ICONE_COND="libreria_icone_condivisa.json"
COMUNI=["Varese","Busto Arsizio","Gallarate","Saronno","Venegono Superiore","Venegono Inferiore","Castiglione Olona","Lozza","Tradate","Malnate","Luino"]

for k,v in [("dati",[]),("postazioni",[]),("icone_lib",[]),("interventi_lista",[]),("menu_scelta","Dashboard"),("volontario_selezionato",None),("volontario_idx",None),("map_lat",45.8205),("map_lon",8.8250),("map_tipo","OpenStreetMap"),("map_logo_selezionato","📍 Default"),("postazione_selezionata_per_mappa",None),("authenticated",False)]:
    if k not in st.session_state:
        st.session_state[k]=v

if not st.session_state.dati:
    st.session_state.dati=load_json(FILE_DATI,[])
if not st.session_state.postazioni:
    st.session_state.postazioni=load_json(FILE_POST,[])
if not st.session_state.interventi_lista:
    st.session_state.interventi_lista=load_json(FILE_INTERVENTI,[])
if not st.session_state.icone_lib:
    st.session_state.icone_lib=load_json(FILE_ICONE_COND,[])

def header_loghi():
    b64=get_b64("logo.png")
    if b64:
        st.markdown(f"<div style='display:flex;justify-content:center;align-items:center;gap:25px;background:#a5d6a7;padding:15px;border-radius:15px;border:3px solid #2e7d32;margin-bottom:15px;'><img src='data:image/png;base64,{b64}' style='width:90px;height:90px;border-radius:50%;border:3px solid #1b5e20;background:white;'><h2 style='color:#0e7a3d;margin:0;text-align:center;'>VOLONTARIATO<br>Sezione di Varese</h2><img src='data:image/png;base64,{b64}' style='width:90px;height:90px;border-radius:50%;border:3px solid #1b5e20;background:white;'></div>", unsafe_allow_html=True)
    else:
        st.markdown("<h2 style='text-align:center;color:#0e7a3d;'>VOLONTARIATO<br>Sezione di Varese</h2>", unsafe_allow_html=True)

def torna_dashboard():
    if st.button("🏠 TORNA ALLA DASHBOARD",use_container_width=True,key=f"torna_{st.session_state.menu_scelta}"):
        st.session_state.menu_scelta="Dashboard"
        st.rerun()

if not st.session_state.authenticated:
    header_loghi()
    c1,c2,c3=st.columns([1,2,1])
    with c2:
        with st.form("login"):
            u=st.text_input("Username",value="admin")
            p=st.text_input("Password",type="password",value="ana2024")
            if st.form_submit_button("🔴 ACCEDI",use_container_width=True,type="primary"):
                if (u=="admin" and p=="ana2024") or p=="ANA2025":
                    st.session_state.authenticated=True
                    st.rerun()
                else:
                    st.error("Password errata")
    st.stop()

header_loghi()
st.divider()

with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png",width=80)
    st.markdown("### MENU")
    opzioni=["Dashboard","Volontari","Mappa Postazioni","Tabella Emergenze","Backup"]
    sel=st.radio("Vai a",opzioni,index=opzioni.index(st.session_state.menu_scelta) if st.session_state.menu_scelta in opzioni else 0)
    if sel!=st.session_state.menu_scelta:
        st.session_state.menu_scelta=sel
        st.rerun()
    st.divider()
    st.metric("Volontari",len(st.session_state.dati))
    st.metric("Postazioni",len(st.session_state.postazioni))

scelta=st.session_state.menu_scelta
MIME="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

if scelta=="Dashboard":
    st.markdown("## 🏠 DASHBOARD")
    c1,c2,c3=st.columns(3)
    with c1:
        if st.button("👥 VOLONTARI",key="q_vol",use_container_width=True):
            st.session_state.menu_scelta="Volontari"; st.rerun()
    with c2:
        if st.button("📍 MAPPA POSTAZIONI",key="q_map",use_container_width=True):
            st.session_state.menu_scelta="Mappa Postazioni"; st.rerun()
    with c3:
        if st.button("🚨 EMERGENZE",key="q_em",use_container_width=True):
            st.session_state.menu_scelta="Tabella Emergenze"; st.rerun()

elif scelta=="Volontari":
    torna_dashboard()
    st.markdown("## 👥 VOLONTARI - 6 SOTTOMASCHERE - SOLO SALVA")
    if st.session_state.volontario_selezionato is not None:
        vol=st.session_state.volontario_selezionato
        idx=st.session_state.volontario_idx
        st.markdown('<div class="vol-selected">',unsafe_allow_html=True)
        st.markdown(f"### 👤 {vol.get('Nome','')}")
        if st.button("❌ Chiudi",key="chiudi_det"):
            st.session_state.volontario_selezionato=None
            st.session_state.volontario_idx=None
            st.rerun()
        st.markdown('</div>',unsafe_allow_html=True)
        t1,t2,t3,t4,t5,t6=st.tabs(["Anagrafica","Radio","Eventi","Presenze","Emergenze","Note"])
        with t1:
            st.markdown('<div class="submask">',unsafe_allow_html=True)
            with st.form("form_anag"):
                parti=vol.get('Nome','').split(" ",1)
                nome_val=parti[0] if len(parti)>0 else ""
                cognome_val=parti[1] if len(parti)>1 else ""
                nome=st.text_input("Nome",value=nome_val)
                cognome=st.text_input("Cognome",value=cognome_val)
                cell=st.text_input("Cellulare",value=vol.get('Cellulare',''))
                comune=st.selectbox("Comune",COMUNI,index=0)
                ruolo=st.selectbox("Ruolo",["Volontario","Caposquadra","Coordinatore"],index=0)
                salva_anag=st.form_submit_button("💾 SALVA",use_container_width=True,type="primary")
                if salva_anag:
                    st.session_state.dati[idx]={"Nome":f"{nome} {cognome}","Cellulare":cell,"Comune":comune,"Ruolo":ruolo,"Associazione":vol.get('Associazione','ANA Varese')}
                    save_json(FILE_DATI,st.session_state.dati)
                    st.session_state.volontario_selezionato=st.session_state.dati[idx]
                    st.success("Salvato!")
                    st.rerun()
            st.markdown('</div>',unsafe_allow_html=True)
        with t2:
            st.markdown('<div class="submask">Radio</div>',unsafe_allow_html=True)
        with t3:
            st.markdown('<div class="submask">Eventi</div>',unsafe_allow_html=True)
        with t4:
            st.markdown('<div class="submask">',unsafe_allow_html=True)
            with st.form("form_pres"):
                ore=st.number_input("Ore",value=4.0,step=0.5)
                luogo=st.text_input("Luogo")
                salva_pres=st.form_submit_button("💾 SALVA PRESENZA",use_container_width=True,type="primary")
                if salva_pres:
                    st.success(f"{ore}h a {luogo}")
            st.markdown('</div>',unsafe_allow_html=True)
        with t5:
            st.markdown('<div class="submask">Emergenze</div>',unsafe_allow_html=True)
        with t6:
            st.markdown('<div class="submask">',unsafe_allow_html=True)
            if st.button(f"ELIMINA {vol.get('Nome','')}",use_container_width=True):
                st.session_state.dati.pop(idx)
                save_json(FILE_DATI,st.session_state.dati)
                st.session_state.volontario_selezionato=None
                st.rerun()
            st.markdown('</div>',unsafe_allow_html=True)
        st.divider()
    with st.form("form"):
        c1,c2=st.columns(2)
        with c1:
            nome=st.text_input("Nome *")
            cognome=st.text_input("Cognome *")
            cell=st.text_input("Cellulare *")
        with c2:
            assoc=st.text_input("Associazione *",value="ANA Varese")
            comune=st.selectbox("Comune",COMUNI,index=0)
            ruolo=st.selectbox("Ruolo *",["Volontario","Caposquadra","Coordinatore"])
        salva_vol=st.form_submit_button("✅ SALVA",use_container_width=True,type="primary")
        if salva_vol:
            if nome and cognome and cell and assoc:
                st.session_state.dati.append({"Nome":f"{nome} {cognome}","Associazione":assoc,"Cellulare":cell,"Comune":comune,"Ruolo":ruolo})
                save_json(FILE_DATI,st.session_state.dati)
                st.rerun()
    for idx, vol in enumerate(st.session_state.dati):
        c1,c2,c3=st.columns([3,2,2])
        with c1:
            if st.button(f"👤 {vol.get('Nome','')}",key=f"vol_{idx}",use_container_width=True):
                st.session_state.volontario_selezionato=vol
                st.session_state.volontario_idx=idx
                st.rerun()
        with c2:
            st.write(vol.get('Cellulare',''))
        with c3:
            st.write(vol.get('Ruolo',''))

elif scelta=="Mappa Postazioni":
    torna_dashboard()
    st.markdown("## 📍 MAPPA POSTAZIONI - OTM / GOOGLE / WAZE - CON LOGHI")
    st.caption("Tabella come ieri | Postazioni con loghi | Mappa visionabile con OTM/Google/Waze | Senza tasti verdi senza dicitura")

    st.markdown("### 🎨 Libreria loghi condivisa")
    uploaded=st.file_uploader("📤 CARICA LOGO PNG", type=["png","jpg","jpeg"], key="up_icon_post")
    if uploaded:
        b64=img_to_b64(uploaded)
        nome_icona=st.text_input("Nome logo", value=uploaded.name.split(".")[0], key="nome_icona_post")
        if st.button("💾 SALVA LOGO",key="save_icon_post",use_container_width=True,type="primary"):
            st.session_state.icone_lib.append({"nome":nome_icona,"b64":b64})
            save_json(FILE_ICONE_COND,st.session_state.icone_lib)
            st.success(f"Logo {nome_icona} salvato!")
            st.rerun()

    if st.session_state.icone_lib:
        cols=st.columns(4)
        for i, ic in enumerate(st.session_state.icone_lib):
            with cols[i%4]:
                is_sel = st.session_state.map_logo_selezionato == ic['nome']
                css = "icon-lib icon-selected" if is_sel else "icon-lib"
                st.markdown(f'<div class="{css}">',unsafe_allow_html=True)
                if ic.get("b64"):
                    st.image(f"data:image/png;base64,{ic['b64']}",width=80)
                    st.write(f"**{ic['nome']}**")
                    if st.button(f"Seleziona {ic['nome']}",key=f"sel_post_{i}",use_container_width=True):
                        st.session_state.map_logo_selezionato=ic['nome']
                        st.rerun()
                    if st.button(f"Elimina {ic['nome']}",key=f"del_post_{i}",use_container_width=True):
                        st.session_state.icone_lib.pop(i)
                        save_json(FILE_ICONE_COND,st.session_state.icone_lib)
                        st.rerun()
                else:
                    st.markdown(f"<div style='font-size:35px;'>{ic.get('nome','📍')}</div>",unsafe_allow_html=True)
                    st.write(f"**{ic['nome']}**")
                    if st.button(f"Seleziona {ic['nome']}",key=f"sel_emoji_{i}",use_container_width=True):
                        st.session_state.map_logo_selezionato=ic['nome']
                        st.rerun()
                st.markdown('</div>',unsafe_allow_html=True)
    st.divider()

    c1,c2=st.columns([2,1])
    with c1:
        st.markdown("### 🗺️ MAPPA CON TUTTE LE POSTAZIONI E LOGHI - OTM / GOOGLE / WAZE")
        tipo_mappa=st.selectbox("Tipo mappa", ["OpenStreetMap","OpenTopoMap (OTM)","Google Maps"], index=0, key="tipo_mappa_sel")
        if tipo_mappa!=st.session_state.map_tipo:
            st.session_state.map_tipo=tipo_mappa
            st.rerun()

        if st.session_state.postazione_selezionata_per_mappa:
            p_sel=st.session_state.postazione_selezionata_per_mappa
            st.markdown(f"<div style='background:#fff3e0;border:3px solid #ef6c00;padding:10px;border-radius:10px;'><b>📍 {p_sel.get('Postazione','')} - {p_sel.get('Icona','')}</b></div>", unsafe_allow_html=True)
            lat_focus=float(p_sel.get('Latitudine',st.session_state.map_lat))
            lon_focus=float(p_sel.get('Longitudine',st.session_state.map_lon))
        else:
            lat_focus=st.session_state.map_lat
            lon_focus=st.session_state.map_lon

        try:
            import folium
            from streamlit_folium import st_folium
            if tipo_mappa=="OpenTopoMap (OTM)":
                m=folium.Map(location=[lat_focus, lon_focus], zoom_start=13, tiles="OpenTopoMap")
            elif tipo_mappa=="Google Maps":
                m=folium.Map(location=[lat_focus, lon_focus], zoom_start=13, tiles="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}", attr="Google")
            else:
                m=folium.Map(location=[lat_focus, lon_focus], zoom_start=13, tiles="OpenStreetMap")
            for idx_p, p in enumerate(st.session_state.postazioni):
                try:
                    lat_f=float(p['Latitudine'])
                    lon_f=float(p['Longitudine'])
                    logo_nome=p.get('Icona','📍')
                    b64=trova_b64_logo(logo_nome, st.session_state.icone_lib)
                    if b64:
                        tmp_path=salva_icona_temp(b64, f"{logo_nome}_{idx_p}")
                        if tmp_path and os.path.exists(tmp_path):
                            icon=folium.CustomIcon(tmp_path, icon_size=(50,50))
                            folium.Marker([lat_f, lon_f], popup=f"{logo_nome} {p.get('Postazione','')}", tooltip=f"{logo_nome}