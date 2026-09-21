import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime, date
import pydeck as pdk

st.set_page_config(page_title="ANA Varese - Protezione Civile", layout="wide")

def hdr_small():
    st.markdown("<div style='background:#0e7a3d; padding:8px; border-radius:8px; color:white; text-align:center; font-weight:bold;'>NUCLEO VOLONTARI PROTEZIONE CIVILE - ANA SEZIONE VARESE</div>", unsafe_allow_html=True)

# INIT
for k in ["page","logged","menu","volontari","radio_db","brogliaccio","eventi","checkin","icone","mezzi","attrezzature","map_markers"]:
    if k not in st.session_state:
        if k=="page": st.session_state[k]="entra"
        elif k=="logged": st.session_state[k]=False
        elif k=="menu": st.session_state[k]="Dashboard"
        else: st.session_state[k]=[]

# 1 - ENTRA (con copertina 400px solo qui)
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
            st.session_state.page="login"; st.rerun()

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
                st.session_state.page="entra"; st.rerun()
        with b:
            if st.button("🔐 Accedi", use_container_width=True, type="primary"):
                if user=="admin" and pwd=="ana2024":
                    st.session_state.logged=True; st.session_state.page="dashboard"; st.rerun()
                else: st.error("admin / ana2024")

# 3 - DASHBOARD SENZA IMMAGINE - TUTTO ORDINATO
elif st.session_state.page=="dashboard":
    hdr_small()
    with st.sidebar:
        st.markdown("### MENU")
        menu = st.radio("Scegli:", ["📊 Dashboard","👥 Volontari","📻 DB Radio","📓 Brogliaccio","📅 Eventi","✅ Check-in","🚚 Mezzi","🧰 Attrezzature","🗺️ Mappa Avanzata","🎨 Libreria Icone","📥 Esporta"], index=0)
        st.session_state.menu=menu
        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged=False; st.session_state.page="entra"; st.rerun()

    # DASHBOARD BOTTONI RAPIDI - NO COPERTINA.PNG
    if st.session_state.menu=="📊 Dashboard":
        st.markdown("## 📊 Dashboard - Scelta rapida form")
        c1,c2,c3,c4,c5 = st.columns(5)
        with c1: st.metric("Volontari", len(st.session_state.volontari))
        with c2: st.metric("Radio", len(st.session_state.radio_db))
        with c3: st.metric("Brogliaccio", len(st.session_state.brogliaccio))
        with c4: st.metric("Eventi", len(st.session_state.eventi))
        with c5: st.metric("Check-in", len(st.session_state.checkin))
        st.markdown("### TASTI RAPIDI FORM")
        r1 = st.columns(4)
        with r1[0]:
            if st.button("👥 VOLONTARI", use_container_width=True, type="primary"):
                st.session_state.menu="👥 Volontari"; st.rerun()
        with r1[1]:
            if st.button("📻 DB RADIO", use_container_width=True):
                st.session_state.menu="📻 DB Radio"; st.rerun()
        with r1[2]:
            if st.button("📓 BROGLIACCIO", use_container_width=True):
                st.session_state.menu="📓 Brogliaccio"; st.rerun()
        with r1[3]:
            if st.button("📅 EVENTI", use_container_width=True):
                st.session_state.menu="📅 Eventi"; st.rerun()
        r2 = st.columns(4)
        with r2[0]:
            if st.button("✅ CHECK-IN", use_container_width=True):
                st.session_state.menu="✅ Check-in"; st.rerun()
        with r2[1]:
            if st.button("🗺️ MAPPA AVANZATA", use_container_width=True):
                st.session_state.menu="🗺️ Mappa Avanzata"; st.rerun()
        with r2[2]:
            if st.button("🚚 MEZZI", use_container_width=True):
                st.session_state.menu="🚚 Mezzi"; st.rerun()
        with r2[3]:
            if st.button("🎨 ICONE", use_container_width=True):
                st.session_state.menu="🎨 Libreria Icone"; st.rerun()

    # VOLONTARI CON SOTTOMASCHERE
    elif st.session_state.menu=="👥 Volontari":
        st.markdown("## 👥 Volontari con sottomaschere")
        t1,t2,t3 = st.tabs(["Anagrafica + Posizione","Contatti Ruolo Qualifiche","Documenti Taglie Note"])
        with t1:
            with st.form("vol_anag"):
                nome = st.text_input("Nome e Cognome *")
                cf = st.text_input("CF")
                comune = st.text_input("Comune residenza *")
                via = st.text_input("Via / Localita")
                c1,c2 = st.columns(2)
                with c1: lat_txt = st.text_input("Lat - VUOTO = no default Varese", placeholder="es. 45.123456")
                with c2: lon_txt = st.text_input("Log - VUOTO = no default Varese", placeholder="es. 8.123456")
                if st.form_submit_button("✅ Salva Anagrafica", use_container_width=True, type="primary"):
                    if nome and comune:
                        try:
                            lat_v = float(lat_txt.replace(",", ".")) if lat_txt else 0.0
                            lon_v = float(lon_txt.replace(",", ".")) if lon_txt else 0.0
                        except: lat_v=lon_v=0.0
                        st.session_state.volontari.append({"Nome":nome,"CF":cf,"Comune":comune,"Via":via,"Lat":lat_v,"Log":lon_v,"Cellulare":"","Ruolo":"","Qualifiche":"","Taglia":"","Note":""})
                        st.success(f"Salvato {nome}")
        with t2:
            if st.session_state.volontari:
                sel = st.selectbox("Volontario", [v["Nome"] for v in st.session_state.volontari])
                idx = [v["Nome"] for v in st.session_state.volontari].index(sel)
                with st.form("vol_det"):
                    cell = st.text_input("Cellulare *", value=st.session_state.volontari[idx].get("Cellulare",""))
                    ruolo = st.selectbox("Ruolo *", ["Volontario","Caposquadra","Coordinatore","Autista","Radio","Telecomunicazioni","Logistica","Segreteria","Sanitario","Altro"])
                    qual = st.multiselect("Qualifiche", ["AIB","Cinofilo","BLSD","Radio operatore","Guida fuoristrada"])
                    if st.form_submit_button("💾 Aggiorna", use_container_width=True):
                        st.session_state.volontari[idx]["Cellulare"]=cell; st.session_state.volontari[idx]["Ruolo"]=ruolo; st.session_state.volontari[idx]["Qualifiche"]=",".join(qual); st.success("Aggiornato")
        with t3:
            if st.session_state.volontari:
                sel = st.selectbox("Volontario", [v["Nome"] for v in st.session_state.volontari], key="t3")
                idx = [v["Nome"] for v in st.session_state.volontari].index(sel)
                taglia = st.selectbox("Taglia", ["XS","S","M","L","XL","XXL"])
                note = st.text_area("Note", value=st.session_state.volontari[idx].get("Note",""))
                if st.button("💾 Salva Taglia/Note", use_container_width=True):
                    st.session_state.volontari[idx]["Taglia"]=taglia; st.session_state.volontari[idx]["Note"]=note; st.success("Salvato")

    # DB RADIO
    elif st.session_state.menu=="📻 DB Radio":
        st.markdown("## 📻 DB Radio")
        with st.form("radio"):
            c1,c2 = st.columns(2)
            with c1:
                modello = st.text_input("Modello *"); matricola = st.text_input("Matricola *"); freq = st.text_input("Frequenza")
            with c2:
                assegnato = st.selectbox("Assegnato", ["Magazzino"] + [v["Nome"] for v in st.session_state.volontari] if st.session_state.volontari else ["Magazzino"])
                stato = st.selectbox("Stato", ["Operativa","In carica","Guasta"]); canale = st.text_input("Canale")
            if st.form_submit_button("✅ Salva Radio", use_container_width=True, type="primary"):
                if modello and matricola:
                    st.session_state.radio_db.append({"Modello":modello,"Matricola":matricola,"Frequenza":freq,"Canale":canale,"Assegnato":assegnato,"Stato":stato,"Data":datetime.now().strftime("%d/%m/%Y %H:%M")})
                    st.success("Salvata")
        if st.session_state.radio_db: st.dataframe(pd.DataFrame(st.session_state.radio_db), use_container_width=True)

    # BROGLIACCIO
    elif st.session_state.menu=="📓 Brogliaccio":
        st.markdown("## 📓 Brogliaccio")
        with st.form("brog"):
            c1,c2,c3 = st.columns(3)
            with c1: data_b = st.date_input("Data", value=date.today()); ora_b = st.time_input("Ora", value=datetime.now().time())
            with c2: operatore = st.selectbox("Operatore", [v["Nome"] for v in st.session_state.volontari] if st.session_state.volontari else ["Operatore"]); canale = st.text_input("Canale")
            with c3: mitt = st.text_input("Da"); dest = st.text_input("A")
            msg = st.text_area("Messaggio *")
            if st.form_submit_button("✅ Registra", use_container_width=True, type="primary"):
                if msg: st.session_state.brogliaccio.append({"Data":str(data_b),"Ora":str(ora_b),"Operatore":operatore,"Canale":canale,"Da":mitt,"A":dest,"Messaggio":msg}); st.success("Registrato")
        if st.session_state.brogliaccio: st.dataframe(pd.DataFrame(st.session_state.brogliaccio), use_container_width=True)

    # EVENTI
    elif st.session_state.menu=="📅 Eventi":
        st.markdown("## 📅 Eventi")
        with st.form("eventi"):
            nome_e = st.text_input("Nome Evento *")
            c1,c2 = st.columns(2)
            with c1: data_i = st.date_input("Inizio"); luogo_e = st.text_input("Luogo *")
            with c2: data_f = st.date_input("Fine"); tipo_e = st.selectbox("Tipo", ["Emergenza","Esercitazione","Prevenzione","Manifestazione"])
            coord = st.selectbox("Coordinatore", [v["Nome"] for v in st.session_state.volontari] if st.session_state.volontari else ["Da assegnare"])
            lat_e = st.text_input("Lat evento - VUOTO = no default"); lon_e = st.text_input("Log evento - VUOTO = no default")
            if st.form_submit_button("✅ Crea Evento", use_container_width=True, type="primary"):
                if nome_e and luogo_e:
                    try: lat_ev = float(lat_e.replace(",", ".")) if lat_e else 0.0; lon_ev = float(lon_e.replace(",", ".")) if lon_e else 0.0
                    except: lat_ev=lon_ev=0.0
                    st.session_state.eventi.append({"Evento":nome_e,"Luogo":luogo_e,"Tipo":tipo_e,"Inizio":str(data_i),"Fine":str(data_f),"Coordinatore":coord,"Lat":lat_ev,"Log":lon_ev,"Stato":"Aperto"})
                    st.success("Evento creato")
        if st.session_state.eventi: st.dataframe(pd.DataFrame(st.session_state.eventi), use_container_width=True)

    # CHECK-IN
    elif st.session_state.menu=="✅ Check-in":
        st.markdown("## ✅ Check-in")
        if not st.session_state.eventi: st.warning("Crea prima evento")
        elif not st.session_state.volontari: st.warning("Registra volontari")
        else:
            with st.form("checkin"):
                ev_sel = st.selectbox("Evento *", [e["Evento"] for e in st.session_state.eventi])
                vol_sel = st.selectbox("Volontario *", [v["Nome"] for v in st.session_state.volontari])
                data_c = st.date_input("Data", value=date.today()); ora_c = st.time_input("Ora", value=datetime.now().time())
                mezzo_c = st.selectbox("Mezzo", ["Nessuno"] + [m["Targa"] for m in st.session_state.mezzi] if st.session_state.mezzi else ["Nessuno"])
                if st.form_submit_button("✅ Registra Check-in", use_container_width=True, type="primary"):
                    st.session_state.checkin.append({"Evento":ev_sel,"Volontario":vol_sel,"Data":str(data_c),"Ora":str(ora_c),"Mezzo":mezzo_c}); st.success("Check-in registrato")
        if st.session_state.checkin: st.dataframe(pd.DataFrame(st.session_state.checkin), use_container_width=True)

    # MEZZI
    elif st.session_state.menu=="🚚 Mezzi":
        st.markdown("## 🚚 Mezzi")
        with st.form("mezzi"):
            targa = st.text_input("Targa *"); tipo = st.selectbox("Tipo", ["Fuoristrada","Furgone","Ambulanza","Autocarro"]); stato = st.selectbox("Stato", ["Operativo","In manutenzione","Non operativo"])
            if st.form_submit_button("✅ Salva Mezzo", use_container_width=True, type="primary"):
                if targa: st.session_state.mezzi.append({"Targa":targa,"Tipo":tipo,"Stato":stato}); st.success("Salvato")
        if st.session_state.mezzi: st.dataframe(pd.DataFrame(st.session_state.mezzi), use_container_width=True)

    # ATTREZZATURE
    elif st.session_state.menu=="🧰 Attrezzature":
        st.markdown("## 🧰 Attrezzature")
        with st.form("attr"):
            nome_a = st.text_input("Attrezzatura *"); qta = st.number_input("Qta", min_value=1, value=1); mag = st.text_input("Magazzino")
            if st.form_submit_button("✅ Salva", use_container_width=True, type="primary"):
                if nome_a: st.session_state.attrezzature.append({"Attrezzatura":nome_a,"Qta":qta,"Magazzino":mag}); st.success("Salvata")
        if st.session_state.attrezzature: st.dataframe(pd.DataFrame(st.session_state.attrezzature), use_container_width=True)

    # MAPPA AVANZATA - TUTTE LE MODIFICHE DI STAMATTINA
    elif st.session_state.menu=="🗺️ Mappa Avanzata":
        st.markdown("## 🗺️ Mappa Avanzata - Modifiche di stamattina")
        st.info("✅ No default Varese | ✅ Tutti i marker | ✅ Filtri | ✅ Colori per tipo | ✅ Popup info | ✅ Form mappa dedicato")

        tab_map1, tab_map2, tab_map3 = st.tabs(["Mappa Generale","Form Mappa / Aggiungi Marker","Mappa Eventi + Check-in"])

        with tab_map1:
            st.markdown("### Mappa Generale con Filtri")
            f1,f2,f3 = st.columns(3)
            with f1: filtro_tipo = st.multiselect("Tipo marker:", ["Volontari","Eventi","Marker Manuali"], default=["Volontari","Eventi","Marker Manuali"])
            with f2: filtro_comune = st.text_input("Filtra per Comune/Luogo")
            with f3: filtro_ruolo = st.text_input("Filtra per Ruolo/Tipo")

            all_markers = []
            if "Volontari" in filtro_tipo:
                for v in st.session_state.volontari:
                    if v.get("Lat",0)!=0 and v.get("Log",0)!=0:
                        if filtro_comune and filtro_comune.lower() not in v.get("Comune","").lower(): continue
                        if filtro_ruolo and filtro_ruolo.lower() not in v.get("Ruolo","").lower(): continue
                        all_markers.append({"lat":v["Lat"],"lon":v["Log"],"tipo":"Volontario","nome":v["Nome"],"info":f"{v.get('Ruolo','')} - {v.get('Comune','')}","color":[14,122,61]})
            if "Eventi" in filtro_tipo:
                for e in st.session_state.eventi:
                    if e.get("Lat",0)!=0 and e.get("Log",0)!=0:
                        if filtro_comune and filtro_comune.lower() not in e.get("Luogo","").lower(): continue
                        all_markers.append({"lat":e["Lat"],"lon":e["Log"],"tipo":"Evento","nome":e["Evento"],"info":f"{e.get('Tipo','')} - {e.get('Luogo','')}","color":[255,0,0]})
            if "Marker Manuali" in filtro_tipo:
                for m in st.session_state.map_markers:
                    if filtro_comune and filtro_comune.lower() not in m.get("Comune","").lower(): continue
                    all_markers.append({"lat":m["Lat"],"lon":m["Log"],"tipo":m.get("Tipo","Manuale"),"nome":m.get("Nome",""),"info":m.get("Note",""),"color":[0,100,255]})

            if all_markers:
                df_map = pd.DataFrame(all_markers)
                # Mappa con pydeck con colori
                layer = pdk.Layer("ScatterplotLayer", data=df_map, get_position='[lon, lat]', get_color='color', get_radius=150, pickable=True)
                view = pdk.ViewState(latitude=df_map["lat"].mean(), longitude=df_map["lon"].mean(), zoom=10, pitch=0)
                tooltip = {"html": "<b>{nome}</b><br>{tipo}<br>{info}", "style": {"backgroundColor": "steelblue", "color": "white"}}
                r = pdk.Deck(layers=[layer], initial_view_state=view, tooltip=tooltip)
                st.pydeck_chart(r)
                st.success(f"{len(df_map)} marker totali - come stamattina")
                st.dataframe(df_map, use_container_width=True)
            else: