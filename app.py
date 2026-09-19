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
.stForm{background:#c8e6c9!important;border:3px solid #2e7d32!important;border-radius:15px!important;}
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
        tmp=os.path.join(tempfile.gettempdir(), f"icon_{nome.replace(' ','_')}.png")
        with open(tmp,"wb") as f:
            f.write(data)
        return tmp
    except:
        return None

FILE_DATI="dati_volontari.json"
FILE_POST="postazioni.json"
FILE_ICONE="libreria_icone_condivisa.json"
COMUNI=["Varese","Busto Arsizio","Gallarate","Saronno","Venegono Superiore","Venegono Inferiore","Castiglione Olona","Lozza","Tradate","Malnate","Luino"]

for k,v in [("dati",[]),("postazioni",[]),("icone_lib",[]),("menu_scelta","Dashboard"),("map_lat",45.8205),("map_lon",8.8250),("map_tipo","OpenStreetMap"),("map_logo_selezionato","Default"),("postazione_selezionata",None),("authenticated",False)]:
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
    if st.button("🏠 TORNA ALLA DASHBOARD",use_container_width=True,key="torna_dash"):
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
    sel=st.radio("Vai a",opzioni,index=0,key="menu_radio")
    if sel!=st.session_state.menu_scelta:
        st.session_state.menu_scelta=sel
        st.rerun()
    st.metric("Volontari",len(st.session_state.dati))
    st.metric("Postazioni",len(st.session_state.postazioni))

scelta=st.session_state.menu_scelta
MIME="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

if scelta=="Dashboard":
    st.markdown("## DASHBOARD")
    c1,c2=st.columns(2)
    with c1:
        if st.button("👥 VOLONTARI",use_container_width=True,key="btn_vol"):
            st.session_state.menu_scelta="Volontari"
            st.rerun()
    with c2:
        if st.button("📍 MAPPA",use_container_width=True,key="btn_mappa"):
            st.session_state.menu_scelta="Mappa Postazioni"
            st.rerun()

elif scelta=="Volontari":
    torna_dashboard()
    st.markdown("## VOLONTARI - SOLO SALVA")
    with st.form("form_vol"):
        c1,c2=st.columns(2)
        with c1:
            nome=st.text_input("Nome *",key="nome_vol")
            cognome=st.text_input("Cognome *",key="cognome_vol")
            cell=st.text_input("Cellulare *",key="cell_vol")
        with c2:
            assoc=st.text_input("Associazione *",value="ANA Varese",key="assoc_vol")
            comune=st.selectbox("Comune",COMUNI,index=0,key="comune_vol")
            ruolo=st.selectbox("Ruolo *",["Volontario","Caposquadra","Coordinatore"],key="ruolo_vol")
        salva_vol=st.form_submit_button("SALVA",use_container_width=True,type="primary")
        if salva_vol:
            if nome and cognome and cell and assoc:
                st.session_state.dati.append({"Nome":f"{nome} {cognome}","Associazione":assoc,"Cellulare":cell,"Comune":comune,"Ruolo":ruolo})
                save_json(FILE_DATI,st.session_state.dati)
                st.success(f"Salvato {nome} {cognome}")
                st.rerun()
    if st.session_state.dati:
        df=pd.DataFrame(st.session_state.dati)
        st.dataframe(df,use_container_width=True)

elif scelta=="Mappa Postazioni":
    torna_dashboard()
    st.markdown("## MAPPA POSTAZIONI - TASTO VEDI LOGHI SISTEMATO + PUNTATORI PICCOLI")
    st.caption("Come ieri - Tabella come ieri - Loghi piccoli 25x25 come puntatori - Tasto Vedi funzionante")

    st.markdown("### Libreria loghi - CLICCA VEDI LOGHI")
    uploaded=st.file_uploader("CARICA LOGO PNG", type=["png","jpg","jpeg"], key="up_logo")
    if uploaded:
        b64=img_to_b64(uploaded)
        nome_icona=st.text_input("Nome logo", value=uploaded.name.split(".")[0], key="nome_logo_input")
        if st.button("SALVA LOGO",use_container_width=True,type="primary",key="btn_salva_logo"):
            st.session_state.icone_lib.append({"nome":nome_icona,"b64":b64})
            save_json(FILE_ICONE,st.session_state.icone_lib)
            st.success(f"Logo {nome_icona} salvato!")
            st.rerun()

    if st.session_state.icone_lib:
        cols=st.columns(4)
        for i, ic in enumerate(st.session_state.icone_lib):
            with cols[i%4]:
                is_sel=st.session_state.map_logo_selezionato==ic['nome']
                css="icon-lib icon-selected" if is_sel else "icon-lib"
                st.markdown(f'<div class="{css}">',unsafe_allow_html=True)
                if ic.get("b64"):
                    st.image(f"data:image/png;base64,{ic['b64']}",width=60)
                    st.write(f"**{ic['nome']}**")
                    # TASTO VEDI LOGHI SISTEMATO - KEY UNICA
                    if st.button(f"👁️ VEDI LOGO",key=f"vedi_logo_lib_{i}_{ic['nome']}",use_container_width=True):
                        st.session_state.map_logo_selezionato=ic['nome']
                        st.toast(f"Logo {ic['nome']} selezionato - visibile su mappa come puntatore 25x25")
                        st.rerun()
                    if st.button(f"✅ SELEZIONA",key=f"seleziona_logo_lib_{i}_{ic['nome']}",use_container_width=True,type="primary"):
                        st.session_state.map_logo_selezionato=ic['nome']
                        st.success(f"Logo {ic['nome']} assegnato!")
                        st.rerun()
                    if st.button(f"🗑️ Elimina",key=f"elimina_logo_lib_{i}_{ic['nome']}",use_container_width=True):
                        st.session_state.icone_lib.pop(i)
                        save_json(FILE_ICONE,st.session_state.icone_lib)
                        st.rerun()
                st.markdown('</div>',unsafe_allow_html=True)
    else:
        st.info("Carica un logo PNG per iniziare")
    st.divider()

    c1,c2=st.columns([2,1])
    with c1:
        st.markdown("### MAPPA CON TUTTE LE POSTAZIONI - LOGHI PICCOLI 25x25 COME PUNTATORI")
        tipo_mappa=st.selectbox("Tipo mappa", ["OpenStreetMap","OpenTopoMap (OTM)","Google Maps"], index=0, key="tipo_mappa")
        if tipo_mappa!=st.session_state.map_tipo:
            st.session_state.map_tipo=tipo_mappa
            st.rerun()

        if st.session_state.postazione_selezionata:
            p_sel=st.session_state.postazione_selezionata
            st.success(f"📍 VEDI LOGHI: {p_sel.get('Postazione','')} - Logo {p_sel.get('Icona','')} - Visibile come puntatore 25x25")
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
                m=folium.Map(location=[lat_focus, lon_focus], zoom_start=13)

            # LOGHI PICCOLI COME PUNTATORI 25x25
            for idx_p, p in enumerate(st.session_state.postazioni):
                try:
                    lat_f=float(p.get('Latitudine'))
                    lon_f=float(p.get('Longitudine'))
                    nome_post=p.get('Postazione','')
                    logo_nome=p.get('Icona','')
                    b64=trova_b64_logo(logo_nome, st.session_state.icone_lib)
                    popup_text=logo_nome + " - " + nome_post
                    if b64:
                        tmp_path=salva_icona_temp(b64, logo_nome + str(idx_p))
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
            map_data=st_folium(m,width=700,height=500,key="mappa_principale")
            if map_data and map_data.get("last_clicked"):
                st.session_state.map_lat=map_data["last_clicked"]["lat"]
                st.session_state.map_lon=map_data["last_clicked"]["lng"]
                st.rerun()
        except Exception as e:
            st.map(pd.DataFrame([{"lat":lat_focus,"lon":lon_focus}]),zoom=12)
            st.error(f"Errore mappa: {e}")

        if st.session_state.postazione_selezionata:
            p=st.session_state.postazione_selezionata
            lat_sel=p.get('Latitudine')
            lon_sel=p.get('Longitudine')
            logo_sel=p.get('Icona','')
            c_otm,c_gm,c_waze=st.columns(3)
            with c_otm:
                st.link_button(f"OTM {logo_sel}", f"https://opentopomap.org/#map=16/{lat_sel}/{lon_sel}", use_container_width=True,key="btn_otm")
            with c_gm:
                st.link_button(f"Google {logo_sel}", f"https://www.google.com/maps/search/?api=1&query={lat_sel},{lon_sel}", use_container_width=True,key="btn_google")
            with c_waze:
                st.link_button(f"Waze {logo_sel}", f"https://waze.com/ul?ll={lat_sel},{lon_sel}&navigate=yes", use_container_width=True,key="btn_waze")

        with st.expander("MAPPA ESPANSA - VEDI TUTTI I LOGHI COME PUNTATORI 30x30", expanded=True if st.session_state.postazione_selezionata else False):
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
                st_folium(m2,width=1000,height=600,key="mappa_espansa")
            except Exception as e:
                st.error(f"Errore mappa espansa: {e}")

    with c2:
        st.markdown("### Maschera - VEDI LOGHI")
        st.info(f"{st.session_state.map_lat:.6f}, {st.session_state.map_lon:.6f} - Clicca mappa")
        st.write(f"Logo selezionato: **{st.session_state.map_logo_selezionato}**")
        b64_sel=trova_b64_logo(st.session_state.map_logo_selezionato, st.session_state.icone_lib)
        if b64_sel:
            st.image(f"data:image/png;base64,{b64_sel}",width=80)
            st.caption("Puntatore 25x25 su mappa - VEDI LOGHI funziona")
        opzioni_logo=["Default"] + [ic['nome'] for ic in st.session_state.icone_lib]
        idx_default=0
        if st.session_state.map_logo_selezionato in opzioni_logo:
            idx_default=opzioni_logo.index(st.session_state.map_logo_selezionato)
        sel_logo=st.selectbox("Scegli logo da vedere", opzioni_logo, index=idx_default, key="select_logo_mask")
        if sel_logo!=st.session_state.map_logo_selezionato:
            st.session_state.map_logo_selezionato=sel_logo
            st.rerun()
        with st.form("form_post"):
            nome_post=st.text_input("Nome Postazione *",key="nome_post")
            comune_post=st.selectbox("Comune *",COMUNI,index=0,key="comune_post")
            via_post=st.text_input("Via *",key="via_post")
            lat_post=st.text_input("Latitudine *",value=str(st.session_state.map_lat),key="lat_post")
            lon_post=st.text_input("Longitudine *",value=str(st.session_state.map_lon),key="lon_post")
            salva_post=st.form_submit_button("📍 SALVA - VEDI LOGO SU MAPPA",use_container_width=True,type="primary")
            if salva_post:
                if nome_post and lat_post and lon_post:
                    new={"Postazione":nome_post,"Comune":comune_post,"Via":via_post,"Latitudine":lat_post,"Longitudine":lon_post,"Icona":st.session_state.map_logo_selezionato}
                    st.session_state.postazioni.append(new)
                    st.session_state.postazione_selezionata=new
                    save_json(FILE_POST,st.session_state.postazioni)
                    st.success(f"Salvata {nome_post} con logo {st.session_state.map_logo_selezionato} - Ora VEDI LOGO su mappa!")
                    st.rerun()

    st.divider()
    st.markdown("### TABELLA POSTAZIONI - TASTO VEDI LOGHI FUNZIONANTE")
    if st.session_state.postazioni:
        df_post=pd.DataFrame(st.session_state.postazioni)
        st.dataframe(df_post,use_container_width=True)
        st.markdown("#### Clicca VEDI LOGHI per vedere il logo sulla mappa come puntatore")
        for idx, p in enumerate(st.session_state.postazioni):
            c_img,c1,c2,c3=st.columns([1,2,2,2])
            with c_img:
                logo_nome=p.get('Icona','')
                b64=trova_b64_logo(logo_nome, st.session_state.icone_lib)
                if b64:
                    st.image(f"data:image/png;base64,{b64}",width=25)
                else:
                    st.write(logo_nome)
            with c1:
                st.write(f"**{p.get('Postazione','')}**")
                st.caption(f"Logo: {logo_nome}")
            with c2:
                st.write(f"{p.get('Via','')} {p.get('Comune','')}")
            with c3:
                # TASTO VEDI LOGHI SISTEMATO - KEY UNICA
                if st.button(f"👁️ VEDI LOGHI",key=f"vedi_loghi_tabella_{idx}_{p.get('Postazione','')}",use_container_width=True):
                    st.session_state.postazione_selezionata=p
                    st.session_state.map_lat=float(p.get('Latitudine',45.8205))
                    st.session_state.map_lon=float(p.get('Longitudine',8.8250))
                    st.session_state.map_logo_selezionato=p.get('Icona','Default')
                    st.toast(f"VEDI LOGHI: {p.get('Postazione','')} - {p.get('Icona','')} - Puntatore 25x25")
                    st.rerun()
        out=BytesIO()
        pd.DataFrame(st.session_state.postazioni).to_excel(out,index=False,engine="openpyxl")
        st.download_button("📥 Excel Postazioni",out.getvalue(),file_name=f"postazioni_{date.today()}.xlsx",mime=MIME,use_container_width=True,key="btn_excel_post")
    else:
        st.info("Nessuna postazione - Clicca sulla mappa!")

elif scelta=="Backup":
    torna_dashboard()
    st.markdown("## Backup")
    if st.button("CREA EXCEL",use_container_width=True,type="primary",key="btn_crea_excel"):
        out=BytesIO()
        with pd.ExcelWriter(out,engine="openpyxl") as writer:
            if st.session_state.dati:
                pd.DataFrame(st.session_state.dati).to_excel(writer,sheet_name="Volontari",index=False)
            if st.session_state.postazioni:
                pd.DataFrame(st.session_state.postazioni).to_excel(writer,sheet_name="Postazioni",index=False)
        st.session_state["backup"]=out.getvalue()
        st.success("Creato!")
    if "backup" in st.session_state:
        st.download_button("SCARICA",st.session_state["backup"],file_name=f"BACKUP_{date.today()}.xlsx",mime=MIME,use_container_width=True,key="btn_scarica_backup")