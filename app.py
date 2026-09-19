import streamlit as st
import pandas as pd
from datetime import date
from io import BytesIO
import os, json, base64, tempfile, requests

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
        tmp=os.path.join(tempfile.gettempdir(), f"icon_{nome}.png")
        with open(tmp,"wb") as f:
            f.write(data)
        return tmp
    except:
        return None

def reverse_geocode(lat, lon):
    try:
        url=f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=18&addressdetails=1"
        headers={"User-Agent":"ANA-Varese-App"}
        r=requests.get(url, headers=headers, timeout=5)
        if r.status_code==200:
            data=r.json()
            addr=data.get("address",{})
            road=addr.get("road","") or addr.get("pedestrian","") or addr.get("footway","") or addr.get("path","") or ""
            house=addr.get("house_number","")
            via=f"{road} {house}".strip()
            if not via:
                via=addr.get("road","") or data.get("display_name","").split(",")[0]
            comune=addr.get("city","") or addr.get("town","") or addr.get("village","") or addr.get("municipality","") or ""
            return via, comune
    except:
        pass
    return "", ""

FILE_DATI="dati_volontari.json"
FILE_POST="postazioni.json"
FILE_ICONE="libreria_icone_condivisa.json"
COMUNI=["Varese","Busto Arsizio","Gallarate","Saronno","Venegono Superiore","Venegono Inferiore","Castiglione Olona","Lozza","Tradate","Malnate","Luino","Altro"]

for k,v in [("dati",[]),("postazioni",[]),("icone_lib",[]),("menu_scelta","Dashboard"),("map_lat",45.8205),("map_lon",8.8250),("map_via",""),("map_comune","Varese"),("map_logo","Default"),("post_sel",None),("map_zoom",14),("authenticated",False)]:
    if k not in st.session_state:
        st.session_state[k]=v

if not st.session_state.dati:
    st.session_state.dati=load_json(FILE_DATI,[])
if not st.session_state.postazioni:
    st.session_state.postazioni=load_json(FILE_POST,[])
if not st.session_state.icone_lib:
    st.session_state.icone_lib=load_json(FILE_ICONE,[])

def header_loghi():
    b64=get_b64("logo.png")
    if b64:
        st.markdown(f"<div style='display:flex;justify-content:center;gap:25px;background:#a5d6a7;padding:15px;border-radius:15px;border:3px solid #2e7d32;'><img src='data:image/png;base64,{b64}' style='width:80px;height:80px;border-radius:50%;'><h2 style='color:#0e7a3d;margin:0;text-align:center;'>VOLONTARIATO<br>Sezione di Varese</h2><img src='data:image/png;base64,{b64}' style='width:80px;height:80px;border-radius:50%;'></div>", unsafe_allow_html=True)
    else:
        st.markdown("<h2 style='text-align:center;color:#0e7a3d;'>VOLONTARIATO Sezione di Varese</h2>", unsafe_allow_html=True)

def torna_dashboard():
    if st.button("🏠 TORNA ALLA DASHBOARD",use_container_width=True,key="torna_home"):
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
    opzioni=["Dashboard","Volontari","Mappa Postazioni","Backup"]
    sel=st.radio("Vai a",opzioni,index=0,key="radio_menu")
    if sel!=st.session_state.menu_scelta:
        st.session_state.menu_scelta=sel
        st.rerun()
    st.metric("Volontari",len(st.session_state.dati))
    st.metric("Postazioni",len(st.session_state.postazioni))
    st.metric("Loghi",len(st.session_state.icone_lib))

scelta=st.session_state.menu_scelta
MIME="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

if scelta=="Dashboard":
    st.markdown("## 🏠 DASHBOARD")
    c1,c2,c3=st.columns(3)
    with c1:
        if st.button("👥 VOLONTARI",key="dash_vol",use_container_width=True):
            st.session_state.menu_scelta="Volontari"
            st.rerun()
    with c2:
        if st.button("📍 MAPPA POSTAZIONI",key="dash_mappa",use_container_width=True):
            st.session_state.menu_scelta="Mappa Postazioni"
            st.rerun()
    with c3:
        if st.button("💾 BACKUP",key="dash_backup",use_container_width=True):
            st.session_state.menu_scelta="Backup"
            st.rerun()

elif scelta=="Volontari":
    torna_dashboard()
    st.markdown("## 👥 VOLONTARI")
    with st.form("form_vol"):
        c1,c2=st.columns(2)
        with c1:
            nome=st.text_input("Nome *",key="new_nome")
            cognome=st.text_input("Cognome *",key="new_cognome")
            cell=st.text_input("Cellulare *",key="new_cell")
        with c2:
            assoc=st.text_input("Associazione *",value="ANA Varese",key="new_assoc")
            comune=st.selectbox("Comune",COMUNI,index=0,key="new_comune")
            ruolo=st.selectbox("Ruolo *",["Volontario","Caposquadra","Coordinatore"],key="new_ruolo")
        salva_vol=st.form_submit_button("✅ SALVA",use_container_width=True,type="primary")
        if salva_vol:
            if nome and cognome and cell and assoc:
                st.session_state.dati.append({"Nome":f"{nome} {cognome}","Associazione":assoc,"Cellulare":cell,"Comune":comune,"Ruolo":ruolo})
                save_json(FILE_DATI,st.session_state.dati)
                st.rerun()
    if st.session_state.dati:
        st.dataframe(pd.DataFrame(st.session_state.dati),use_container_width=True)

elif scelta=="Mappa Postazioni":
    torna_dashboard()
    st.markdown("## 📍 MAPPA POSTAZIONI - FIX VIA ASSOCIATA + ANTEPRIMA TUTTE + NO PUNTATORE DEFAULT")

    st.markdown("### 🎨 Libreria loghi 15x15")
    uploaded=st.file_uploader("📤 CARICA LOGO PNG", type=["png","jpg","jpeg"], key="up_logo")
    if uploaded:
        b64=img_to_b64(uploaded)
        nome_icona=st.text_input("Nome logo", value=uploaded.name.split(".")[0], key="nome_logo_up")
        if st.button("💾 SALVA LOGO",use_container_width=True,type="primary",key="btn_salva_lib"):
            st.session_state.icone_lib.append({"nome":nome_icona,"b64":b64})
            save_json(FILE_ICONE,st.session_state.icone_lib)
            st.success(f"Logo {nome_icona} salvato!")
            st.rerun()

    if st.session_state.icone_lib:
        cols=st.columns(6)
        for i, ic in enumerate(st.session_state.icone_lib):
            with cols[i%6]:
                is_sel=st.session_state.map_logo==ic['nome']
                css="icon-lib icon-selected" if is_sel else "icon-lib"
                st.markdown(f'<div class="{css}">',unsafe_allow_html=True)
                if ic.get("b64"):
                    st.image(f"data:image/png;base64,{ic['b64']}",width=40)
                    st.write(f"**{ic['nome']}**")
                    if st.button(f"✅ SEL",key=f"sel_lib_{i}_{ic['nome']}",use_container_width=True,type="primary"):
                        st.session_state.map_logo=ic['nome']
                        st.rerun()
                st.markdown('</div>',unsafe_allow_html=True)
    st.divider()

    c1,c2=st.columns([2,1])
    with c1:
        st.markdown("### 🗺️ MAPPA SELEZIONE - Clicca e Via si associa in maschera")
        try:
            import folium
            from streamlit_folium import st_folium
            m=folium.Map(location=[st.session_state.map_lat, st.session_state.map_lon], zoom_start=15)
            for idx_p, p in enumerate(st.session_state.postazioni):
                try:
                    lat_f=float(p.get('Latitudine'))
                    lon_f=float(p.get('Longitudine'))
                    logo_nome=p.get('Icona','')
                    b64=trova_b64_logo(logo_nome, st.session_state.icone_lib)
                    popup_text=logo_nome + " - " + p.get('Postazione','') + " - " + p.get('Via','')
                    if b64:
                        tmp_path=salva_icona_temp(b64, f"{logo_nome}_{idx_p}")
                        if tmp_path:
                            icon=folium.CustomIcon(tmp_path, icon_size=(15,15))
                            folium.Marker([lat_f, lon_f], popup=popup_text, icon=icon).add_to(m)
                        else:
                            folium.Marker([lat_f, lon_f], popup=popup_text).add_to(m)
                    else:
                        folium.Marker([lat_f, lon_f], popup=popup_text).add_to(m)
                except:
                    pass
            # PUNTATORE DEFAULT TOLTO - Non c'e' piu' Marker rosso +
            map_data=st_folium(m,width=700,height=400,key="mappa_sel")
            if map_data and map_data.get("last_clicked"):
                lat_c=map_data["last_clicked"]["lat"]
                lon_c=map_data["last_clicked"]["lng"]
                st.session_state.map_lat=lat_c
                st.session_state.map_lon=lon_c
                via_auto, comune_auto=reverse_geocode(lat_c, lon_c)
                if via_auto:
                    st.session_state.map_via=via_auto
                else:
                    st.session_state.map_via=f"{lat_c:.6f}, {lon_c:.6f}"
                if comune_auto:
                    st.session_state.map_comune=comune_auto
                st.session_state.post_sel=None
                st.session_state.map_zoom=14
                st.toast(f"Via associata: {via_auto}")
                st.rerun()
        except Exception as e:
            st.error(f"Errore: {e}")

        st.markdown("### 🔍 ANTEPRIMA - VEDI TUTTE LE POSTAZIONI SALVATE - NO PUNTATORE DEFAULT")
        tipo_mappa=st.selectbox("Tipo mappa anteprima", ["StreetMap","OpenTopoMap (OTM)","Google Maps Stradale","Google Satellite","Waze Style"], index=0, key="sel_tipo_anteprima")

        try:
            import folium
            from streamlit_folium import st_folium
            lat_center=st.session_state.map_lat
            lon_center=st.session_state.map_lon
            zoom_anteprima=st.session_state.map_zoom
            if st.session_state.post_sel:
                lat_center=float(st.session_state.post_sel.get('Latitudine',lat_center))
                lon_center=float(st.session_state.post_sel.get('Longitudine',lon_center))
                zoom_anteprima=17

            if tipo_mappa=="OpenTopoMap (OTM)":
                m2=folium.Map(location=[lat_center, lon_center], zoom_start=zoom_anteprima, tiles="OpenTopoMap")
            elif tipo_mappa=="Google Maps Stradale":
                m2=folium.Map(location=[lat_center, lon_center], zoom_start=zoom_anteprima, tiles="https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}", attr="Google")
            elif tipo_mappa=="Google Satellite":
                m2=folium.Map(location=[lat_center, lon_center], zoom_start=zoom_anteprima, tiles="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}", attr="Google")
            elif tipo_mappa=="Waze Style":
                m2=folium.Map(location=[lat_center, lon_center], zoom_start=zoom_anteprima, tiles="CartoDB positron")
            else:
                m2=folium.Map(location=[lat_center, lon_center], zoom_start=zoom_anteprima)

            # ANTEPRIMA DEVE VEDERE TUTTE LE POSTAZIONI SALVATE - SEMPRE
            for idx_p, p in enumerate(st.session_state.postazioni):
                try:
                    lat_f=float(p.get('Latitudine'))
                    lon_f=float(p.get('Longitudine'))
                    nome_post=p.get('Postazione','')
                    logo_nome=p.get('Icona','')
                    via_p=p.get('Via','')
                    b64=trova_b64_logo(logo_nome, st.session_state.icone_lib)
                    popup_text=f"{logo_nome} - {nome_post} - {via_p}"
                    if b64:
                        tmp_path=salva_icona_temp(b64, f"ante_{logo_nome}_{idx_p}")
                        if tmp_path:
                            icon=folium.CustomIcon(tmp_path, icon_size=(15,15))
                            folium.Marker([lat_f, lon_f], popup=popup_text, icon=icon).add_to(m2)
                        else:
                            folium.Marker([lat_f, lon_f], popup=popup_text).add_to(m2)
                    else:
                        folium.Marker([lat_f, lon_f], popup=popup_text).add_to(m2)
                except:
                    pass

            # PUNTATORE DEFAULT TOLTO ANCHE QUI - Solo postazioni salvate
            if st.session_state.post_sel:
                try:
                    lat_s=float(st.session_state.post_sel.get('Latitudine'))
                    lon_s=float(st.session_state.post_sel.get('Longitudine'))
                    folium.CircleMarker([lat_s, lon_s], radius=30, color="red", fill=False, weight=3).add_to(m2)
                except:
                    pass

            st_folium(m2,width=1000,height=650,key="mappa_anteprima_tutte")
            st.success(f"ANTEPRIMA {tipo_mappa} - Tutte {len(st.session_state.postazioni)} postazioni salvate 15x15 - NO puntatore default")
        except Exception as e:
            st.error(f"Errore anteprima: {e}")

    with c2:
        st.markdown("### 📋 Maschera - Via associata come sopra")
        st.info(f"Lat {st.session_state.map_lat:.6f} Lon {st.session_state.map_lon:.6f}")
        # QUI SOPRA ALLA MASCHERA VEDEVI LA VIA - ORA LA ASSOCIA NEL CAMPO VIA
        if st.session_state.map_via:
            st.success(f"✅ Via rilevata sopra: {st.session_state.map_via} - Ora associata nel campo Via sotto!")
        else:
            st.warning("Clicca su mappa per rilevare via")
        if st.session_state.post_sel:
            p_sel=st.session_state.post_sel
            st.success(f"Selezionata: {p_sel.get('Postazione','')}\nVia: {p_sel.get('Via','')}\nComune: {p_sel.get('Comune','')}")

        st.write(f"Logo: {st.session_state.map_logo} 15x15")
        b64_sel=trova_b64_logo(st.session_state.map_logo, st.session_state.icone_lib)
        if b64_sel:
            st.image(f"data:image/png;base64,{b64_sel}",width=30)

        opzioni_logo=["Default"] + [ic['nome'] for ic in st.session_state.icone_lib]
        idx_default=0
        if st.session_state.map_logo in opzioni_logo:
            idx_default=opzioni_logo.index(st.session_state.map_logo)
        sel_logo=st.selectbox("Scegli logo 15x15", opzioni_logo, index=idx_default, key="sel_logo_mask")
        if sel_logo!=st.session_state.map_logo:
            st.session_state.map_logo=sel_logo
            st.rerun()

        with st.form("form_post_finale"):
            val_nome=""
            if st.session_state.post_sel:
                val_nome=st.session_state.post_sel.get('Postazione','')
            nome_post=st.text_input("Nome Postazione *",value=val_nome,key="inp_nome")

            val_comune=st.session_state.map_comune
            if st.session_state.post_sel:
                val_comune=st.session_state.post_sel.get('Comune','Varese')
            idx_comune=0
            if val_comune in COMUNI:
                idx_comune=COMUNI.index(val_comune)
            comune_post=st.selectbox("Comune *",COMUNI,index=idx_comune,key="inp_comune")

            # CAMPO VIA - ORA ASSOCIA IL NOME DELLA VIA COME VEDI SOPRA ALLA MASCHERA - FIX
            val_via=st.session_state.map_via
            if st.session_state.post_sel:
                val_via=st.session_state.post_sel.get('Via','')
            via_post=st.text_input("Via * - Associa nome via come sopra",value=val_via,key="inp_via",help="Quando selezioni postazione nella mappa, il nome della via che vedi sopra ora viene associato qui nel campo Via")

            lat_post=st.text_input("Latitudine *",value=str(st.session_state.map_lat),key="inp_lat")
            lon_post=st.text_input("Longitudine *",value=str(st.session_state.map_lon),key="inp_lon")

            salva_post=st.form_submit_button("📍 SALVA CON VIA ASSOCIATA E LOGO 15x15",use_container_width=True,type="primary")
            if salva_post:
                if nome_post and lat_post and lon_post:
                    new={"Postazione":nome_post,"Comune":comune_post,"Via":via_post,"Latitudine":lat_post,"Longitudine":lon_post,"Icona":st.session_state.map_logo}
                    st.session_state.postazioni.append(new)
                    st.session_state.post_sel=new
                    st.session_state.map_zoom=17
                    save_json(FILE_POST,st.session_state.postazioni)
                    st.success(f"Salvata {nome_post} - Via {via_post} associata!")
                    st.rerun()

    st.divider()
    st.markdown("### 📋 TABELLA POSTAZIONI - Clicca e Via va in maschera")
    if st.session_state.postazioni:
        st.dataframe(pd.DataFrame(st.session_state.postazioni),use_container_width=True)
        for idx, p in enumerate(st.session_state.postazioni):
            c_img,c1,c2,c3=st.columns([1,2,2,2])
            with c_img:
                logo_nome=p.get('Icona','')
                b64=trova_b64_logo(logo_nome, st.session_state.icone_lib)
                if b64:
                    st.image(f"data:image/png;base64,{b64}",width=15)
            with c1:
                st.write(f"**{p.get('Postazione','')}**")
            with c2:
                st.write(f"{p.get('Via','')} - {p.get('Comune','')}")
            with c3:
                if st.button(f"📍 POSTAZIONE",key=f"vedi_post_{idx}_{p.get('Postazione','')}",use_container_width=True):
                    st.session_state.post_sel=p
                    st.session_state.map_lat=float(p.get('Latitudine',45.8205))
                    st.session_state.map_lon=float(p.get('Longitudine',8.8250))
                    st.session_state.map_via=p.get('Via','')
                    st.session_state.map_comune=p.get('Comune','Varese')
                    st.session_state.map_logo=p.get('Icona','Default')
                    st.session_state.map_zoom=17
                    st.toast(f"Via {p.get('Via','')} associata in maschera")
                    st.rerun()
        out=BytesIO()
        pd.DataFrame(st.session_state.postazioni).to_excel(out,index=False,engine="openpyxl")
        st.download_button("📥 Excel",out.getvalue(),file_name=f"postazioni_{date.today()}.xlsx",mime=MIME,use_container_width=True)

elif scelta=="Backup":
    torna_dashboard()
    st.markdown("## 💾 BACKUP")
    if st.button("📦 CREA EXCEL",use_container_width=True,type="primary"):
        out=BytesIO()
        with pd.ExcelWriter(out,engine="openpyxl") as writer:
            if st.session_state.dati:
                pd.DataFrame(st.session_state.dati).to_excel(writer,sheet_name="Volontari",index=False)
            if st.session_state.postazioni:
                pd.DataFrame(st.session_state.postazioni).to_excel(writer,sheet_name="Postazioni",index=False)
        st.session_state["backup"]=out.getvalue()
        st.success("Creato!")
    if "backup" in st.session_state:
        st.download_button("📥 SCARICA",st.session_state["backup"],file_name=f"BACKUP_{date.today()}.xlsx",mime=MIME,use_container_width=True)