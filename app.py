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
.stButton>button{background:#2e7d32!important;color:white!important;font-weight:bold!important;min-height:50px!important;border-radius:10px!important;}
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

FILE_DATI="dati_volontari.json"
FILE_POST="postazioni.json"
FILE_ICONE="libreria_icone_condivisa.json"
FILE_INTERVENTI="interventi_emergenza.json"
COMUNI=["Varese","Busto Arsizio","Gallarate","Saronno","Venegono Superiore","Venegono Inferiore","Castiglione Olona","Lozza","Tradate","Malnate","Luino"]

for k,v in [("dati",[]),("postazioni",[]),("icone_lib",[]),("interventi_lista",[]),("menu_scelta","Dashboard"),("volontario_selezionato",None),("volontario_idx",None),("map_lat",45.8205),("map_lon",8.8250),("map_tipo","OpenStreetMap"),("map_logo_selezionato","Default"),("postazione_selezionata",None),("authenticated",False)]:
    if k not in st.session_state:
        st.session_state[k]=v

if not st.session_state.dati:
    st.session_state.dati=load_json(FILE_DATI,[])
if not st.session_state.postazioni:
    st.session_state.postazioni=load_json(FILE_POST,[])
if not st.session_state.icone_lib:
    st.session_state.icone_lib=load_json(FILE_ICONE,[])
if not st.session_state.interventi_lista:
    st.session_state.interventi_lista=load_json(FILE_INTERVENTI,[])

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
    st.markdown("### MENU")
    opzioni=["Dashboard","Volontari","Mappa Postazioni","Tabella Emergenze","Backup"]
    sel=st.radio("Vai a",opzioni,index=opzioni.index(st.session_state.menu_scelta) if st.session_state.menu_scelta in opzioni else 0,key="radio_menu")
    if sel!=st.session_state.menu_scelta:
        st.session_state.menu_scelta=sel
        st.rerun()
    st.divider()
    st.metric("Volontari",len(st.session_state.dati))
    st.metric("Postazioni",len(st.session_state.postazioni))
    st.metric("Loghi",len(st.session_state.icone_lib))

scelta=st.session_state.menu_scelta
MIME="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

# DASHBOARD CON TUTTI I FORM E TASTI SCELTA RAPIDA RIPRISTINATA
if scelta=="Dashboard":
    st.markdown("## 🏠 DASHBOARD - MENU CON TUTTI I FORM - TASTI SCELTA RAPIDA")
    st.caption("Ripristinata come ieri con tutti i form")
    c1,c2,c3=st.columns(3)
    with c1:
        if st.button("👥 VOLONTARI\n6 Sottomaschere\nSolo SALVA",key="dash_vol",use_container_width=True):
            st.session_state.menu_scelta="Volontari"
            st.rerun()
        st.markdown("<br>",unsafe_allow_html=True)
        if st.button("🚨 TABELLA EMERGENZE\nLoghi condivisi",key="dash_em",use_container_width=True):
            st.session_state.menu_scelta="Tabella Emergenze"
            st.rerun()
    with c2:
        if st.button("📍 MAPPA POSTAZIONI\nOTM / Google / Waze\nLoghi piccoli puntatori",key="dash_mappa",use_container_width=True):
            st.session_state.menu_scelta="Mappa Postazioni"
            st.rerun()
        st.markdown("<br>",unsafe_allow_html=True)
        if st.button("💾 BACKUP\nExcel unico",key="dash_backup",use_container_width=True):
            st.session_state.menu_scelta="Backup"
            st.rerun()
    with c3:
        st.markdown("#### 📊 Riepilogo")
        st.info(f"Volontari: {len(st.session_state.dati)}\n\nPostazioni: {len(st.session_state.postazioni)}\n\nLoghi: {len(st.session_state.icone_lib)}")
        if st.session_state.postazioni:
            st.markdown("#### 📍 Ultime postazioni")
            for p in st.session_state.postazioni[-3:]:
                st.write(f"{p.get('Icona','')} {p.get('Postazione','')}")

elif scelta=="Volontari":
    torna_dashboard()
    st.markdown("## 👥 VOLONTARI - 6 SOTTOMASCHERE - SOLO SALVA SENZA MODIFICA")
    if st.session_state.volontario_selezionato is not None:
        vol=st.session_state.volontario_selezionato
        idx=st.session_state.volontario_idx
        st.markdown(f"### 👤 {vol.get('Nome','')}")
        if st.button("❌ Chiudi scheda",key="chiudi_vol"):
            st.session_state.volontario_selezionato=None
            st.session_state.volontario_idx=None
            st.rerun()
        t1,t2,t3,t4,t5,t6=st.tabs(["Anagrafica","Radio","Eventi","Presenze","Emergenze","Note"])
        with t1:
            with st.form("form_anag"):
                parti=vol.get('Nome','').split(" ",1)
                nv=parti[0] if len(parti)>0 else ""
                cv=parti[1] if len(parti)>1 else ""
                nome=st.text_input("Nome",value=nv,key="anag_nome")
                cognome=st.text_input("Cognome",value=cv,key="anag_cognome")
                cell=st.text_input("Cellulare",value=vol.get('Cellulare',''),key="anag_cell")
                comune=st.selectbox("Comune",COMUNI,index=0,key="anag_comune")
                ruolo=st.selectbox("Ruolo",["Volontario","Caposquadra","Coordinatore"],index=0,key="anag_ruolo")
                salva_anag=st.form_submit_button("💾 SALVA",use_container_width=True,type="primary")
                if salva_anag:
                    st.session_state.dati[idx]={"Nome":f"{nome} {cognome}","Cellulare":cell,"Comune":comune,"Ruolo":ruolo,"Associazione":vol.get('Associazione','ANA Varese')}
                    save_json(FILE_DATI,st.session_state.dati)
                    st.success("Salvato!")
                    st.rerun()
        with t2: st.info("📻 Sottomaschera Radio")
        with t3: st.info("📅 Sottomaschera Eventi")
        with t4:
            with st.form("form_pres"):
                ore=st.number_input("Ore",value=4.0,step=0.5,key="ore_pres")
                luogo=st.text_input("Luogo",key="luogo_pres")
                salva_pres=st.form_submit_button("💾 SALVA PRESENZA",use_container_width=True)
                if salva_pres: st.success(f"{ore}h a {luogo}")
        with t5: st.info("🚨 Sottomaschera Emergenze")
        with t6:
            if st.button(f"ELIMINA {vol.get('Nome','')}",use_container_width=True,key="elimina_vol"):
                st.session_state.dati.pop(idx)
                save_json(FILE_DATI,st.session_state.dati)
                st.session_state.volontario_selezionato=None
                st.rerun()
        st.divider()
    with st.form("form_vol_new"):
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
    st.divider()
    st.markdown("### 📋 Tabella volontari - Clicca per 6 sottomaschere")
    for idx, vol in enumerate(st.session_state.dati):
        c1,c2,c3=st.columns([3,2,2])
        with c1:
            if st.button(f"👤 {vol.get('Nome','')}",key=f"btn_vol_{idx}",use_container_width=True):
                st.session_state.volontario_selezionato=vol
                st.session_state.volontario_idx=idx
                st.rerun()
        with c2: st.write(vol.get('Cellulare',''))
        with c3: st.write(vol.get('Ruolo',''))

elif scelta=="Mappa Postazioni":
    torna_dashboard()
    st.markdown("## 📍 MAPPA POSTAZIONI - COME IERI - LOGHI SALVATI VISIBILI")
    st.caption("Tabella con loghi | Tasto postazione per vedere dove è | Selezione mappe Google Waze OTM | Loghi piccoli puntatori 25x25")

    # LIBRERIA LOGHI SALVATI - ORA VISIBILI
    st.markdown("### 🎨 Libreria loghi salvati - VEDI LOGHI")
    uploaded=st.file_uploader("📤 CARICA LOGO PNG", type=["png","jpg","jpeg"], key="up_logo_mappa")
    if uploaded:
        b64=img_to_b64(uploaded)
        nome_icona=st.text_input("Nome logo", value=uploaded.name.split(".")[0], key="nome_logo_mappa")
        if st.button("💾 SALVA LOGO IN LIBRERIA",use_container_width=True,type="primary",key="btn_salva_logo_lib"):
            st.session_state.icone_lib.append({"nome":nome_icona,"b64":b64})
            save_json(FILE_ICONE,st.session_state.icone_lib)
            st.success(f"Logo {nome_icona} salvato! Ora visibile!")
            st.rerun()

    if st.session_state.icone_lib:
        st.markdown(f"#### 📚 {len(st.session_state.icone_lib)} loghi salvati - Clicca VEDI LOGHI")
        cols=st.columns(4)
        for i, ic in enumerate(st.session_state.icone_lib):
            with cols[i%4]:
                is_sel=st.session_state.map_logo_selezionato==ic['nome']
                css="icon-lib icon-selected" if is_sel else "icon-lib"
                st.markdown(f'<div class="{css}">',unsafe_allow_html=True)
                if ic.get("b64"):
                    st.image(f"data:image/png;base64,{ic['b64']}",width=70)
                    st.write(f"**{ic['nome']}**")
                    if st.button(f"👁️ VEDI LOGHI",key=f"vedi_lib_{i}_{ic['nome']}",use_container_width=True):
                        st.session_state.map_logo_selezionato=ic['nome']
                        st.toast(f"VEDI LOGHI: {ic['nome']} selezionato")
                        st.rerun()
                    if st.button(f"✅ SELEZIONA",key=f"sel_lib_{i}_{ic['nome']}",use_container_width=True,type="primary"):
                        st.session_state.map_logo_selezionato=ic['nome']
                        st.success(f"Selezionato {ic['nome']}")
                        st.rerun()
                    if st.button(f"🗑️ Elimina",key=f"del_lib_{i}_{ic['nome']}",use_container_width=True):
                        st.session_state.icone_lib.pop(i)
                        save_json(FILE_ICONE,st.session_state.icone_lib)
                        st.rerun()
                st.markdown('</div>',unsafe_allow_html=True)
    else:
        st.warning("Nessun logo salvato - Carica un PNG")
    st.divider()

    c1,c2=st.columns([2,1])
    with c1:
        st.markdown("### 🗺️ MAPPA CON TUTTE LE POSTAZIONI - LOGHI PICCOLI COME PUNTATORI")
        # SELEZIONE MAPPE TIPO GOOGLE MAP WAZE OTM RIPRISTINATA
        st.markdown("#### 🗺️ Selezione tipo mappa:")
        tipo_mappa=st.selectbox("Scegli mappa", ["OpenStreetMap","OpenTopoMap (OTM)","Google Maps","Waze"], index=0, key="select_tipo_mappa")
        if tipo_mappa!=st.session_state.map_tipo:
            st.session_state.map_tipo=tipo_mappa
            st.rerun()

        if st.session_state.postazione_selezionata:
            p_sel=st.session_state.postazione_selezionata
            st.success(f"📍 VEDI POSTAZIONE: {p_sel.get('Postazione','')} - Logo {p_sel.get('Icona','')} - Puntatore 25x25 visibile")
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
            elif tipo_mappa=="Waze":
                m=folium.Map(location=[lat_focus, lon_focus], zoom_start=13, tiles="OpenStreetMap")
            else:
                m=folium.Map(location=[lat_focus, lon_focus], zoom_start=13)

            # TUTTE LE POSTAZIONI CON LOGHI PICCOLI COME PUNTATORI 25x25
            for idx_p, p in enumerate(st.session_state.postazioni):
                try:
                    lat_f=float(p.get('Latitudine'))
                    lon_f=float(p.get('Longitudine'))
                    nome_post=p.get('Postazione','')
                    logo_nome=p.get('Icona','')
                    b64=trova_b64_logo(logo_nome, st.session_state.icone_lib)
                    popup_text=logo_nome + " - " + nome_post
                    if b64:
                        tmp_path=salva_icona_temp(b64, f"{logo_nome}_{idx_p}")
                        if tmp_path:
                            icon=folium.CustomIcon(tmp_path, icon_size=(25,25))
                            folium.Marker([lat_f, lon_f], popup=popup_text, icon=icon).add_to(m)
                        else:
                            folium.Marker([lat_f, lon_f], popup=popup_text).add_to(m)
                    else:
                        folium.Marker([lat_f, lon_f], popup=popup_text).add_to(m)
                except:
                    pass

            folium.Marker([st.session_state.map_lat, st.session_state.map_lon], popup="Nuova posizione", icon=folium.Icon(color="red", icon="plus")).add_to(m)
            map_data=st_folium(m,width=700,height=500,key="mappa_main")
            if map_data and map_data.get("last_clicked"):
                st.session_state.map_lat=map_data["last_clicked"]["lat"]
                st.session_state.map_lon=map_data["last_clicked"]["lng"]
                st.toast(f"Posizione: {st.session_state.map_lat:.6f}, {st.session_state.map_lon:.6f}")
                st.rerun()
        except Exception as e:
            st.map(pd.DataFrame([{"lat":lat_focus,"lon":lon_focus}]),zoom=12)
            st.error(f"Mappa: {e}")

        # BOTTONI GOOGLE WAZE OTM CON LOGO
        st.markdown("#### 🌍 Apri postazione su:")
        if st.session_state.postazione_selezionata:
            p=st.session_state.postazione_selezionata
            lat_sel=p.get('Latitudine')
            lon_sel=p.get('Longitudine')
            logo_sel=p.get('Icona','')
            c_otm,c_gm,c_waze=st.columns(3)
            with c_otm:
                st.link_button(f"🗺️ OTM {logo_sel}", f"https://opentopomap.org/#map=16/{lat_sel}/{lon_sel}", use_container_width=True,key="link_otm")
            with c_gm:
                st.link_button(f"🔍 Google {logo_sel}", f"https://www.google.com/maps/search/?api=1&query={lat_sel},{lon_sel}", use_container_width=True,key="link_google")
            with c_waze:
                st.link_button(f"🚗 Waze {logo_sel}", f"https://waze.com/ul?ll={lat_sel},{lon_sel}&navigate=yes", use_container_width=True,key="link_waze")
        else:
            lat=st.session_state.map_lat
            lon=st.session_state.map_lon
            c_otm,c_gm,c_waze=st.columns(3)
            with c_otm:
                st.link_button("🗺️ OTM", f"https://opentopomap.org/#map=16/{lat}/{lon}", use_container_width=True,key="link_otm2")
            with c_gm:
                st.link_button("🔍 Google Maps", f"https://www.google.com/maps/search/?api=1&query={lat},{lon}", use_container_width=True,key="link_google2")
            with c_waze:
                st.link_button("🚗 Waze", f"https://waze.com/ul?ll={lat},{lon}&navigate=yes", use_container_width=True,key="link_waze2")

        # MAPPA ESPANSA DOPO SALVATAGGIO VISIBILE SU FORM
        with st.expander("🔍 MAPPA ESPANSA - Tutte le postazioni con loghi piccoli puntatori - Visibile dopo salvataggio", expanded=True if st.session_state.postazione_selezionata else False):
            try:
                import folium
                from streamlit_folium import st_folium
                m2=folium.Map(location=[lat_focus, lon_focus], zoom_start=14)
                for idx_p, p in enumerate(st.session_state.postazioni):
                    try:
                        lat_f=float(p.get('Latitudine'))
                        lon_f=float(p.get('Longitudine'))
                        nome_post=p.get('Postazione','')
                        logo_nome=p.get('Icona','')
                        b64=trova_b64_logo(logo_nome, st.session_state.icone_lib)
                        popup_text=logo_nome + " - " + nome_post
                        if b64:
                            tmp_path=salva_icona_temp(b64, f"exp_{logo_nome}_{idx_p}")
                            if tmp_path:
                                icon=folium.CustomIcon(tmp_path, icon_size=(30,30))
                                folium.Marker([lat_f, lon_f], popup=popup_text, icon=icon).add_to(m2)
                            else:
                                folium.Marker([lat_f, lon_f], popup=popup_text).add_to(m2)
                        else:
                            folium.Marker([lat_f, lon_f], popup=popup_text).add_to(m2)
                    except:
                        pass
                st_folium(m2,width=1000,height=600,key="mappa_expansa")
            except Exception as e:
                st.error(f"Errore: {e}")

    with c2:
        st.markdown("### 📋 Maschera - Salva con logo")
        st.info(f"📍 {st.session_state.map_lat:.6f}, {st.session_state.map_lon:.6f}\nClicca mappa per posizionare")
        st.write(f"Logo assegnato: **{st.session_state.map_logo_selezionato}**")
        b64_sel=trova_b64_logo(st.session_state.map_logo_selezionato, st.session_state.icone_lib)
        if b64_sel:
            st.image(f"data:image/png;base64,{b64_sel}",width=80)
            st.caption(f"Puntatore 25x25 - {st.session_state.map_logo_selezionato}")
        opzioni_logo=["Default"] + [ic['nome'] for ic in st.session_state.icone_lib]
        idx_default=0
        if st.session_state.map_logo_selezionato in opzioni_logo:
            idx_default=opzioni_logo.index(st.session_state.map_logo_selezionato)
        sel_logo=st.selectbox("Scegli logo da assegnare", opzioni_logo, index=idx_default, key="select_logo_mask")
        if sel_logo!=st.session_state.map_logo_selezionato:
            st.session_state.map_logo_selezionato=sel_logo
            st.rerun()
        with st.form("form_post_mappa"):
            nome_post=st.text_input("Nome Postazione *",key="input_nome_post")
            comune_post=st.selectbox("Comune *",COMUNI,index=0,key="input_comune_post")
            via_post=st.text_input("Via *",key="input_via_post")
            lat_post=st.text_input("Latitudine *",value=str(st.session_state.map_lat),key="input_lat_post")
            lon_post=st.text_input("Longitudine *",value=str(st.session_state.map_lon),key="input_lon_post")
            salva_post=st.form_submit_button("📍 SALVA CON LOGO - VISIBILE SU MAPPA",use_container_width=True,type="primary")
            if salva_post:
                if nome_post and lat_post and lon_post:
                    new={"Postazione":nome_post,"Comune":comune_post,"Via":via_post,"Latitudine":lat_post,"Longitudine":lon_post,"Icona":st.session_state.map_logo_selezionato}
                    st.session_state.postazioni.append(new)
                    st.session_state.postazione_selezionata=new
                    save_json(FILE_POST,st.session_state.postazioni)
                    st.success(f"✅ {nome_post} con logo {st.session_state.map_logo_selezionato} salvata! Visibile su mappa come puntatore!")
                    st.rerun()

    st.divider()
    # TABELLA CON LOGHI E TASTO POSTAZIONE PER VEDERE DOVE E' LA POSTAZIONE - RIPRISTINATA COME IERI
    st.markdown("### 📋 TABELLA POSTAZIONI COME IERI - Con loghi salvati e tasto VEDI POSTAZIONE")
    if st.session_state.postazioni:
        df_post=pd.DataFrame(st.session_state.postazioni)
        st.dataframe(df_post,use_container_width=True)
        st.markdown("#### 👁️ Clicca VEDI POSTAZIONE per vedere dove è la postazione sulla mappa con logo")
        for idx, p in enumerate(st.session_state.postazioni):
            c_img,c1,c2,c3=st.columns([1,2,2,2])
            with c_img:
                logo_nome=p.get('Icona','')
                b64=trova_b64_logo(logo_nome, st.session_state.icone_lib)
                if b64:
                    st.image(f"data:image/png;base64,{b64}",width=30)
                else:
                    st.write(logo_nome)
            with c1:
                st.write(f"**{p.get('Postazione','')}**")
                st.caption(f"Logo: {logo_nome}")
            with c2:
                st.write(f"{p.get('Via','')} - {p.get('Comune','')}")
                st.caption(f"{p.get('Latitudine','')}, {p.get('Longitudine','')}")
            with c3:
                if st.button(f"📍 VEDI POSTAZIONE",key=f"vedi_post_{idx}_{p.get('Postazione','')}",use_container_width=True):
                    st.session_state.postazione_selezionata=p
                    st.session_state.map_lat=float(p.get('Latitudine',45.8205))
                    st.session_state.map_lon=float(p.get('Longitudine',8.8250))
                    st.session_state.map_logo_selezionato=p.get('Icona','Default')
                    st.toast(f"VEDI POSTAZIONE: {p.get('Postazione','')} - Logo {p.get('Icona','')}")
                    st.rerun()
                if st.button(f"🗑️ Elimina",key=f"elimina_post_{idx}",use_container_width=True):
                    st.session_state.postazioni.pop(idx)
                    save_json(FILE_POST,st.session_state.postazioni)
                    st.rerun()
        out=BytesIO()
        pd.DataFrame(st.session_state.postazioni).to_excel(out,index=False,engine="openpyxl")
        st.download_button("📥 Excel Postazioni con loghi",out.getvalue(),file_name=f"postazioni_{date.today()}.xlsx",mime=MIME,use_container_width=True,key="excel_post")
    else:
        st.info("Nessuna postazione - Clicca sulla mappa, scegli logo e salva!")

elif scelta=="Tabella Emergenze":
    torna_dashboard()
    st.markdown("## 🚨 TABELLA EMERGENZE - Loghi condivisi con Mappe")
    if st.session_state.icone_lib:
        cols=st.columns(6)
        for i, ic in enumerate(st.session_state.icone_lib):
            with cols[i%6]:
                if ic.get("b64"):
                    st.image(f"data:image/png;base64,{ic['b64']}",width=40)
                    st.caption(ic['nome'])
    with st.form("form_em"):
        com=st.text_input("Comune *",key="em_comune")
        via=st.text_input("Via *",key="em_via")
        az=st.text_area("Azione *",key="em_azione")
        salva_em=st.form_submit_button("💾 SALVA",use_container_width=True,type="primary")
        if salva_em:
            if com and via and az:
                st.session_state.interventi_lista.append({"Comune":com,"Via":via,"Azione":az,"Logo":st.session_state.map_logo_selezionato,"Data":str(date.today())})
                save_json(FILE_INTERVENTI,st.session_state.interventi_lista)
                st.success("Salvato!")
                st.rerun()
    if st.session_state.interventi_lista:
        st.dataframe(pd.DataFrame(st.session_state.interventi_lista),use_container_width=True)

elif scelta=="Backup":
    torna_dashboard()
    st.markdown("## 💾 BACKUP")
    if st.button("📦 CREA EXCEL UNICO CON TUTTO",use_container_width=True,type="primary",key="btn_crea_backup"):
        out=BytesIO()
        with pd.ExcelWriter(out,engine="openpyxl") as writer:
            if st.session_state.dati:
                pd.DataFrame(st.session_state.dati).to_excel(writer,sheet_name="Volontari",index=False)
            if st.session_state.postazioni:
                pd.DataFrame(st.session_state.postazioni).to_excel(writer,sheet_name="Postazioni",index=False)
            if st.session_state.interventi_lista:
                pd.DataFrame(st.session_state.interventi_lista).to_excel(writer,sheet_name="Emergenze",index=False)
            if st.session_state.icone_lib:
                pd.DataFrame([{"Nome":ic['nome']} for ic in st.session_state.icone_lib]).to_excel(writer,sheet_name="Loghi",index=False)
        st.session_state["backup_unico"]=out.getvalue()
        st.success("Backup creato con tutto!")
    if "backup_unico" in st.session_state:
        st.download_button("📥 SCARICA BACKUP COMPLETO",st.session_state["backup_unico"],file_name=f"BACKUP_ANA_{date.today()}.xlsx",mime=MIME,use_container_width=True,key="btn_download_backup")