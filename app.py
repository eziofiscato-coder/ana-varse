import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime, date
import pydeck as pdk

st.set_page_config(page_title="ANA Varese - Protezione Civile", layout="wide")

def hdr_small():
    st.markdown("<div style='background:#0e7a3d; padding:8px; border-radius:8px; color:white; text-align:center; font-weight:bold;'>NUCLEO VOLONTARI PROTEZIONE CIVILE - ANA SEZIONE VARESE</div>", unsafe_allow_html=True)

for k in ["page","logged","menu","volontari","radio_db","brogliaccio","eventi","checkin","icone","mezzi","attrezzature","map_markers","postazioni"]:
    if k not in st.session_state:
        if k=="page": st.session_state[k]="entra"
        elif k=="logged": st.session_state[k]=False
        elif k=="menu": st.session_state[k]="Dashboard"
        else: st.session_state[k]=[]

# 1 - ENTRA
if st.session_state.page=="entra":
    hdr_small()
    c1,c2,c3 = st.columns([1,2,1])
    with c2:
        try: st.image("copertina.png", width=400)
        except:
            try: st.image("logo.png", width=250)
            except: pass
    st.markdown("<h2 style='text-align:center; color:#0e7a3d;'>VOLONTARIATO<br>Sezione di Varese</h2>", unsafe_allow_html=True)
    st.divider()
    c1,c2,c3 = st.columns([1,1,1])
    with c2:
        if st.button("🚪 ENTRA", use_container_width=True, type="primary"):
            st.session_state.page="login"
            st.rerun()

# 2 - LOGIN
elif st.session_state.page=="login":
    hdr_small()
    st.markdown("<h3 style='text-align:center;'>Login</h3>", unsafe_allow_html=True)
    c1,c2,c3 = st.columns([1,2,1])
    with c2:
        user = st.text_input("Utente")
        pwd = st.text_input("Password", type="password")
        a,b = st.columns(2)
        with a:
            if st.button("⬅️ Indietro", use_container_width=True):
                st.session_state.page="entra"
                st.rerun()
        with b:
            if st.button("🔐 Accedi", use_container_width=True, type="primary"):
                if user=="admin" and pwd=="ana2024":
                    st.session_state.logged=True
                    st.session_state.page="dashboard"
                    st.rerun()
                else:
                    st.error("admin / ana2024")

# 3 - DASHBOARD SENZA IMMAGINE
elif st.session_state.page=="dashboard":
    hdr_small()
    with st.sidebar:
        st.markdown("### MENU")
        menu = st.radio("Scegli:", ["📊 Dashboard","👥 Volontari","📻 DB Radio","📓 Brogliaccio","📅 Eventi","✅ Check-in","🚚 Mezzi","🧰 Attrezzature","🗺️ Mappa Avanzata","🎨 Libreria Icone","💾 Backup","📥 Esporta"], index=0)
        st.session_state.menu=menu
        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged=False
            st.session_state.page="entra"
            st.rerun()

    if st.session_state.menu=="📊 Dashboard":
        st.markdown("## 📊 Dashboard")
        c1,c2,c3,c4 = st.columns(4)
        with c1: st.metric("Volontari", len(st.session_state.volontari))
        with c2: st.metric("Eventi", len(st.session_state.eventi))
        with c3: st.metric("Check-in", len(st.session_state.checkin))
        with c4: st.metric("Postazioni Mappa", len(st.session_state.postazioni))

    elif st.session_state.menu=="👥 Volontari":
        st.markdown("## 👥 Volontari")
        with st.form("vol"):
            nome = st.text_input("Nome e Cognome *")
            comune = st.text_input("Comune *")
            lat_txt = st.text_input("Lat - VUOTO = no default")
            lon_txt = st.text_input("Log - VUOTO = no default")
            if st.form_submit_button("✅ Salva", use_container_width=True, type="primary"):
                if nome and comune:
                    try:
                        lat_v = float(lat_txt.replace(",", ".")) if lat_txt else 0.0
                        lon_v = float(lon_txt.replace(",", ".")) if lon_txt else 0.0
                    except:
                        lat_v = 0.0
                        lon_v = 0.0
                    st.session_state.volontari.append({"Nome":nome,"Comune":comune,"Lat":lat_v,"Log":lon_v})
                    st.success("Salvato")
        if st.session_state.volontari: st.dataframe(pd.DataFrame(st.session_state.volontari), use_container_width=True)

    elif st.session_state.menu=="📅 Eventi":
        st.markdown("## 📅 Eventi - NOME EVENTO per Check-in associato")
        with st.form("eventi"):
            nome_evento = st.text_input("NOME EVENTO * per check-in associato")
            luogo_e = st.text_input("Luogo Evento *")
            c1,c2 = st.columns(2)
            with c1: lat_e = st.text_input("Lat Evento - VUOTO = no default")
            with c2: lon_e = st.text_input("Log Evento - VUOTO = no default")
            if st.form_submit_button("✅ Crea Evento", use_container_width=True, type="primary"):
                if nome_evento and luogo_e:
                    try:
                        lat_ev = float(lat_e.replace(",", ".")) if lat_e else 0.0
                        lon_ev = float(lon_e.replace(",", ".")) if lon_e else 0.0
                    except:
                        lat_ev = 0.0
                        lon_ev = 0.0
                    st.session_state.eventi.append({"NomeEvento":nome_evento,"Luogo":luogo_e,"Lat":lat_ev,"Log":lon_ev,"Stato":"Aperto"})
                    st.success(f"Evento '{nome_evento}' creato")
                else:
                    st.error("Compila NOME EVENTO * e Luogo *")
        if st.session_state.eventi: st.dataframe(pd.DataFrame(st.session_state.eventi), use_container_width=True)

    # FORM CHECK-IN CON MASCHERA COMPLETA - FIX
    elif st.session_state.menu=="✅ Check-in":
        st.markdown("## ✅ Check-in - Maschera completa associata a NOME EVENTO")
        if not st.session_state.eventi:
            st.warning("Crea prima un Evento con NOME EVENTO")
        elif not st.session_state.volontari:
            st.warning("Registra prima Volontari")
        else:
            # MASCHERA PER FARE CHECK-IN
            with st.form("form_checkin_completo"):
                st.markdown("### Maschera Check-in")
                ev_sel = st.selectbox("NOME EVENTO *", [e["NomeEvento"] for e in st.session_state.eventi])
                ev_info = next((e for e in st.session_state.eventi if e["NomeEvento"]==ev_sel), None)
                if ev_info:
                    st.info(f"Evento: {ev_info['NomeEvento']} | Luogo: {ev_info['Luogo']}")
                vol_sel = st.selectbox("Volontario *", [v["Nome"] for v in st.session_state.volontari])
                c1,c2,c3 = st.columns(3)
                with c1:
                    data_c = st.date_input("Data Check-in *", value=date.today())
                    ora_c = st.time_input("Ora Check-in *", value=datetime.now().time())
                with c2:
                    mezzo_c = st.selectbox("Mezzo", ["Nessuno","Piedi","Fuoristrada","Furgone"] + [m["Targa"] for m in st.session_state.mezzi] if st.session_state.mezzi else ["Nessuno","Piedi"])
                    ruolo_ev = st.selectbox("Ruolo in Evento", ["Volontario","Caposquadra","Autista","Radio","Logistica","Sanitario","Coordinatore"])
                with c3:
                    postazione_c = st.selectbox("Postazione", ["Base","Avanzata","Magazzino","Sede"] + [p["Nome"] for p in st.session_state.postazioni] if st.session_state.postazioni else ["Base","Avanzata"])
                    stato_c = st.selectbox("Stato", ["Presente","In arrivo","Partito","Non disponibile"])
                note_c = st.text_area("Note Check-in")
                if st.form_submit_button("✅ REGISTRA CHECK-IN SU EVENTO", use_container_width=True, type="primary"):
                    st.session_state.checkin.append({"NomeEvento":ev_sel,"Volontario":vol_sel,"Data":str(data_c),"Ora":str(ora_c),"Mezzo":mezzo_c,"RuoloEvento":ruolo_ev,"Postazione":postazione_c,"Stato":stato_c,"Note":note_c,"LuogoEvento":ev_info["Luogo"] if ev_info else ""})
                    st.success(f"✅ Check-in: {vol_sel} -> {ev_sel} | Postazione: {postazione_c}")

        if st.session_state.checkin:
            st.markdown("### Elenco Check-in per NOME EVENTO")
            df_c = pd.DataFrame(st.session_state.checkin)
            st.dataframe(df_c, use_container_width=True)
            filtro_ev = st.selectbox("Filtra per NOME EVENTO", ["Tutti"] + [e["NomeEvento"] for e in st.session_state.eventi])
            if filtro_ev!="Tutti":
                st.dataframe(df_c[df_c["NomeEvento"]==filtro_ev], use_container_width=True)

    # FORM ICONE CON UPLOAD E DOWNLOAD - FIX
    elif st.session_state.menu=="🎨 Libreria Icone":
        st.markdown("## 🎨 Libreria Icone - Carica icone con Download")
        with st.form("icone_upload"):
            nome_i = st.text_input("Nome icona *")
            c1,c2 = st.columns(2)
            with c1: cat_i = st.selectbox("Categoria", ["Volontari","Radio","Mezzi","Eventi","Mappa","Postazioni","Emergenza","Altro"])
            with c2: colore = st.color_picker("Colore icona", "#0e7a3d")
            uso = st.text_input("Uso / Descrizione")
            file_i = st.file_uploader("Carica icona PNG / SVG / JPG *", type=["png","svg","jpg","jpeg"])
            if st.form_submit_button("✅ Salva Icona con file", use_container_width=True, type="primary"):
                if nome_i and file_i:
                    file_bytes = file_i.getvalue()
                    st.session_state.icone.append({"Nome":nome_i,"Categoria":cat_i,"Colore":colore,"Uso":uso,"FileName":file_i.name,"FileBytes":file_bytes,"Tipo":file_i.type})
                    st.success(f"Icona {nome_i} caricata: {file_i.name}")
                elif nome_i:
                    st.session_state.icone.append({"Nome":nome_i,"Categoria":cat_i,"Colore":colore,"Uso":uso,"FileName":"","FileBytes":None,"Tipo":""})
                    st.success(f"Icona {nome_i} salvata senza file")
                else:
                    st.error("Nome icona * e file richiesti")

        if st.session_state.icone:
            st.markdown("### Icone caricate con Download")
            for idx, ico in enumerate(st.session_state.icone):
                c1,c2,c3,c4 = st.columns([2,2,3,2])
                with c1:
                    st.markdown(f"<div style='background:{ico['Colore']}; padding:8px; border-radius:6px; color:white; text-align:center;'>{ico['Nome']}<br>{ico['Categoria']}</div>", unsafe_allow_html=True)
                with c2:
                    st.write(f"File: {ico.get('FileName','')}")
                    st.write(f"Uso: {ico.get('Uso','')}")
                with c3:
                    if ico.get("FileBytes"):
                        st.download_button(f"📥 Download {ico['Nome']}", ico["FileBytes"], file_name=ico["FileName"], mime=ico.get("Tipo","image/png"), key=f"dl_{idx}", use_container_width=True)
                    else:
                        st.write("Nessun file")
                with c4:
                    if st.button(f"🗑️ Elimina", key=f"del_{idx}", use_container_width=True):
                        st.session_state.icone.pop(idx)
                        st.rerun()
                st.divider()

    # FORM MAPPE GRAN LAVORO - VISIONE MAPPE + MARKER POSTAZIONI + SALVA POSTAZIONI SU ALTRA MAPPA SOTTO + CAMBIA TIPO MAPPA
    elif st.session_state.menu=="🗺️ Mappa Avanzata":
        st.markdown("## 🗺️ Mappa Avanzata - Gran lavoro di stamattina")

        # CAMBIA MAPPA TIPO
        tipo_mappa = st.selectbox("🗺️ Cambia tipo mappa:", ["Google Maps (Roadmap)","Google Earth (Satellite)","Waze (Dark)","HERE / OpenStreetMap (Light)","Topografica"], index=0)
        if tipo_mappa=="Google Maps (Roadmap)": map_style="road"
        elif tipo_mappa=="Google Earth (Satellite)": map_style="satellite"
        elif tipo_mappa=="Waze (Dark)": map_style="dark"
        elif tipo_mappa=="HERE / OpenStreetMap (Light)": map_style="light"
        else: map_style="light"
        st.info(f"Mappa selezionata: {tipo_mappa} | Stile: {map_style} | VUOTO = no default Varese")

        tab1, tab2, tab3 = st.tabs(["Visione Mappe + Marker","Form Aggiungi Postazioni","Postazioni Salvate su altra Mappa sotto"])

        with tab1:
            st.markdown("### Visione Mappe - Tutte le postazioni")
            all_markers = []
            for v in st.session_state.volontari:
                if v.get("Lat",0)!=0 and v.get("Log",0)!=0:
                    all_markers.append({"lat":v["Lat"],"lon":v["Log"],"tipo":"Volontario","nome":v["Nome"],"info":v.get("Comune",""),"color":[14,122,61]})
            for e in st.session_state.eventi:
                if e.get("Lat",0)!=0 and e.get("Log",0)!=0:
                    all_markers.append({"lat":e["Lat"],"lon":e["Log"],"tipo":"Evento","nome":e.get("NomeEvento",""),"info":e.get("Luogo",""),"color":[255,0,0]})
            for p in st.session_state.postazioni:
                all_markers.append({"lat":p["Lat"],"lon":p["Log"],"tipo":p.get("Tipo","Postazione"),"nome":p["Nome"],"info":f"{p.get('Comune','')} - {p.get('Note','')}","color":[0,100,255]})
            for m in st.session_state.map_markers:
                all_markers.append({"lat":m["Lat"],"lon":m["Log"],"tipo":m.get("Tipo","Manuale"),"nome":m.get("Nome",""),"info":m.get("Comune",""),"color":[255,165,0]})

            if all_markers:
                df_map = pd.DataFrame(all_markers)
                layer = pdk.Layer("ScatterplotLayer", data=df_map, get_position='[lon, lat]', get_color='color', get_radius=200, pickable=True)
                view = pdk.ViewState(latitude=df_map["lat"].mean(), longitude=df_map["lon"].mean(), zoom=11, pitch=0)
                tooltip = {"html": "<b>{nome}</b><br>{tipo}<br>{info}<br>Lat: {lat}<br>Lon: {lon}", "style": {"backgroundColor": "steelblue", "color": "white"}}
                # cambia mappa tipo
                if map_style=="satellite":
                    deck = pdk.Deck(layers=[layer], initial_view_state=view, tooltip=tooltip, map_style="mapbox://styles/mapbox/s