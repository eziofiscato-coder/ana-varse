import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime, date
import pydeck as pdk

st.set_page_config(page_title="ANA Varese - Protezione Civile", layout="wide")

def hdr_small():
    st.markdown("<div style='background:#0e7a3d; padding:8px; border-radius:8px; color:white; text-align:center; font-weight:bold;'>NUCLEO VOLONTARI PROTEZIONE CIVILE - ANA SEZIONE VARESE</div>", unsafe_allow_html=True)

for k in ["page","logged","menu","volontari","radio_db","brogliaccio","eventi","checkin","icone","mezzi","attrezzature","map_markers"]:
    if k not in st.session_state:
        if k=="page": st.session_state[k]="entra"
        elif k=="logged": st.session_state[k]=False
        elif k=="menu": st.session_state[k]="Dashboard"
        else: st.session_state[k]=[]

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

elif st.session_state.page=="dashboard":
    hdr_small()
    with st.sidebar:
        st.markdown("### MENU")
        menu = st.radio("Scegli:", ["📊 Dashboard","👥 Volontari","📻 DB Radio","📓 Brogliaccio","📅 Eventi","✅ Check-in","🚚 Mezzi","🧰 Attrezzature","🗺️ Mappa Avanzata","🎨 Libreria Icone","📥 Esporta"], index=0)
        st.session_state.menu=menu
        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged=False
            st.session_state.page="entra"
            st.rerun()

    if st.session_state.menu=="📊 Dashboard":
        st.markdown("## 📊 Dashboard")
        c1,c2,c3,c4,c5 = st.columns(5)
        with c1: st.metric("Volontari", len(st.session_state.volontari))
        with c2: st.metric("Radio", len(st.session_state.radio_db))
        with c3: st.metric("Brogliaccio", len(st.session_state.brogliaccio))
        with c4: st.metric("Eventi", len(st.session_state.eventi))
        with c5: st.metric("Check-in", len(st.session_state.checkin))
        st.markdown("### TASTI RAPIDI")
        r1 = st.columns(4)
        with r1[0]:
            if st.button("👥 VOLONTARI", use_container_width=True, type="primary"):
                st.session_state.menu="👥 Volontari"
                st.rerun()
        with r1[1]:
            if st.button("📻 DB RADIO", use_container_width=True):
                st.session_state.menu="📻 DB Radio"
                st.rerun()
        with r1[2]:
            if st.button("📓 BROGLIACCIO", use_container_width=True):
                st.session_state.menu="📓 Brogliaccio"
                st.rerun()
        with r1[3]:
            if st.button("📅 EVENTI", use_container_width=True):
                st.session_state.menu="📅 Eventi"
                st.rerun()
        r2 = st.columns(4)
        with r2[0]:
            if st.button("✅ CHECK-IN", use_container_width=True):
                st.session_state.menu="✅ Check-in"
                st.rerun()
        with r2[1]:
            if st.button("🗺️ MAPPA AVANZATA", use_container_width=True):
                st.session_state.menu="🗺️ Mappa Avanzata"
                st.rerun()
        with r2[2]:
            if st.button("🚚 MEZZI", use_container_width=True):
                st.session_state.menu="🚚 Mezzi"
                st.rerun()
        with r2[3]:
            if st.button("🎨 ICONE", use_container_width=True):
                st.session_state.menu="🎨 Libreria Icone"
                st.rerun()

    elif st.session_state.menu=="👥 Volontari":
        st.markdown("## 👥 Volontari con sottomaschere")
        t1,t2,t3 = st.tabs(["Anagrafica + Posizione","Contatti Ruolo","Qualifiche Note"])
        with t1:
            with st.form("vol_anag"):
                nome = st.text_input("Nome e Cognome *")
                comune = st.text_input("Comune residenza *")
                via = st.text_input("Via / Localita")
                c1,c2 = st.columns(2)
                with c1: lat_txt = st.text_input("Lat - VUOTO = no default", placeholder="45.123456")
                with c2: lon_txt = st.text_input("Log - VUOTO = no default", placeholder="8.123456")
                if st.form_submit_button("✅ Salva", use_container_width=True, type="primary"):
                    if nome and comune:
                        try:
                            lat_v = float(lat_txt.replace(",", ".")) if lat_txt else 0.0
                            lon_v = float(lon_txt.replace(",", ".")) if lon_txt else 0.0
                        except:
                            lat_v = 0.0
                            lon_v = 0.0
                        st.session_state.volontari.append({"Nome":nome,"Comune":comune,"Via":via,"Lat":lat_v,"Log":lon_v,"Cellulare":"","Ruolo":""})
                        st.success(f"Salvato {nome}")

    elif st.session_state.menu=="📻 DB Radio":
        st.markdown("## 📻 DB Radio")
        with st.form("radio"):
            modello = st.text_input("Modello *")
            matricola = st.text_input("Matricola *")
            freq = st.text_input("Frequenza")
            assegnato = st.selectbox("Assegnato", ["Magazzino"] + [v["Nome"] for v in st.session_state.volontari] if st.session_state.volontari else ["Magazzino"])
            if st.form_submit_button("✅ Salva Radio", use_container_width=True, type="primary"):
                if modello and matricola:
                    st.session_state.radio_db.append({"Modello":modello,"Matricola":matricola,"Frequenza":freq,"Assegnato":assegnato,"Data":datetime.now().strftime("%d/%m/%Y %H:%M")})
                    st.success("Salvata")
        if st.session_state.radio_db: st.dataframe(pd.DataFrame(st.session_state.radio_db), use_container_width=True)

    elif st.session_state.menu=="📓 Brogliaccio":
        st.markdown("## 📓 Brogliaccio")
        with st.form("brog"):
            operatore = st.selectbox("Operatore", [v["Nome"] for v in st.session_state.volontari] if st.session_state.volontari else ["Operatore"])
            msg = st.text_area("Messaggio *")
            if st.form_submit_button("✅ Registra", use_container_width=True, type="primary"):
                if msg:
                    st.session_state.brogliaccio.append({"Data":str(date.today()),"Operatore":operatore,"Messaggio":msg})
                    st.success("Registrato")
        if st.session_state.brogliaccio: st.dataframe(pd.DataFrame(st.session_state.brogliaccio), use_container_width=True)

    elif st.session_state.menu=="📅 Eventi":
        st.markdown("## 📅 Eventi")
        with st.form("eventi"):
            nome_e = st.text_input("Nome Evento *")
            luogo_e = st.text_input("Luogo *")
            lat_e = st.text_input("Lat - VUOTO = no default")
            lon_e = st.text_input("Log - VUOTO = no default")
            if st.form_submit_button("✅ Crea Evento", use_container_width=True, type="primary"):
                if nome_e and luogo_e:
                    try:
                        lat_ev = float(lat_e.replace(",", ".")) if lat_e else 0.0
                        lon_ev = float(lon_e.replace(",", ".")) if lon_e else 0.0
                    except:
                        lat_ev = 0.0
                        lon_ev = 0.0
                    st.session_state.eventi.append({"Evento":nome_e,"Luogo":luogo_e,"Lat":lat_ev,"Log":lon_ev})
                    st.success("Evento creato")
        if st.session_state.eventi: st.dataframe(pd.DataFrame(st.session_state.eventi), use_container_width=True)

    elif st.session_state.menu=="✅ Check-in":
        st.markdown("## ✅ Check-in")
        if st.session_state.eventi and st.session_state.volontari:
            with st.form("checkin"):
                ev_sel = st.selectbox("Evento *", [e["Evento"] for e in st.session_state.eventi])
                vol_sel = st.selectbox("Volontario *", [v["Nome"] for v in st.session_state.volontari])
                if st.form_submit_button("✅ Registra", use_container_width=True, type="primary"):
                    st.session_state.checkin.append({"Evento":ev_sel,"Volontario":vol_sel,"Data":str(date.today())})
                    st.success("Check-in registrato")
        if st.session_state.checkin: st.dataframe(pd.DataFrame(st.session_state.checkin), use_container_width=True)

    elif st.session_state.menu=="🚚 Mezzi":
        st.markdown("## 🚚 Mezzi")
        with st.form("mezzi"):
            targa = st.text_input("Targa *")
            if st.form_submit_button("✅ Salva Mezzo", use_container_width=True, type="primary"):
                if targa:
                    st.session_state.mezzi.append({"Targa":targa})
                    st.success("Salvato")
        if st.session_state.mezzi: st.dataframe(pd.DataFrame(st.session_state.mezzi), use_container_width=True)

    elif st.session_state.menu=="🧰 Attrezzature":
        st.markdown("## 🧰 Attrezzature")
        with st.form("attr"):
            nome_a = st.text_input("Attrezzatura *")
            if st.form_submit_button("✅ Salva", use_container_width=True, type="primary"):
                if nome_a:
                    st.session_state.attrezzature.append({"Attrezzatura":nome_a})
                    st.success("Salvata")
        if st.session_state.attrezzature: st.dataframe(pd.DataFrame(st.session_state.attrezzature), use_container_width=True)

    elif st.session_state.menu=="🗺️ Mappa Avanzata":
        st.markdown("## 🗺️ Mappa Avanzata - Fix stamattina")
        tab1, tab2 = st.tabs(["Mappa Generale","Form Mappa"])
        with tab1:
            all_markers = []
            for v in st.session_state.volontari:
                if v.get("Lat",0)!=0 and v.get("Log",0)!=0:
                    all_markers.append({"lat":v["Lat"],"lon":v["Log"],"tipo":"Volontario","nome":v["Nome"],"info":v.get("Comune",""),"color":[14,122,61]})
            for e in st.session_state.eventi:
                if e.get("Lat",0)!=0 and e.get("Log",0)!=0:
                    all_markers.append({"lat":e["Lat"],"lon":e["Log"],"tipo":"Evento","nome":e["Evento"],"info":e.get("Luogo",""),"color":[255,0,0]})
            for m in st.session_state.map_markers:
                all_markers.append({"lat":m["Lat"],"lon":m["Log"],"tipo":m.get("Tipo","Manuale"),"nome":m.get("Nome",""),"info":m.get("Note",""),"color":[0,100,255]})
            if all_markers:
                df_map = pd.DataFrame(all_markers)
                layer = pdk.Layer("ScatterplotLayer", data=df_map, get_position='[lon, lat]', get_color='color', get_radius=150, pickable=True)
                view = pdk.ViewState(latitude=df_map["lat"].mean(), longitude=df_map["lon"].mean(), zoom=10)
                tooltip = {"html": "<b>{nome}</b><br>{tipo}<br>{info}", "style": {"backgroundColor": "steelblue", "color": "white"}}
                r = pdk.Deck(layers=[layer], initial_view_state=view, tooltip=tooltip)
                st.pydeck_chart(r)
                st.dataframe(df_map, use_container_width=True)
            else:
                st.warning("Nessun marker - inserisci Lat/Log - VUOTO = no default Varese")

        with tab2:
            st.markdown("### Form Mappa - Aggiungi Marker")
            with st.form("form_mappa_manuale"):
                nome_m = st.text_input("Nome marker *")
                tipo_m = st.selectbox("Tipo", ["Punto ritrovo","Magazzino","Sede","Idrante","Altro"])
                comune_m = st.text_input("Comune *")
                lat_m = st.text_input("Lat * - VUOTO = no default", placeholder="45.123456")
                lon_m = st.text_input("Log * - VUOTO = no default", placeholder="8.123456")
                note_m = st.text_area("Note")
                if st.form_submit_button("✅ Aggiungi Marker", use_container_width=True, type="primary"):
                    if nome_m and comune_m and lat_m and lon_m:
                        try:
                            lat_v = float(lat_m.replace(",", "."))
                            lon_v = float(lon_m.replace(",", "."))
                            st.session_state.map_markers.append({"Nome":nome_m,"Tipo":tipo_m,"Comune":comune_m,"Lat":lat_v,"Log":lon_v,"Note":note_m})
                            st.success(f"Marker {nome_m} aggiunto")
                        except:
                            st.error("Lat/Log non validi")
                    else:
                        st.error("Compila *")

    elif st.session_state.menu=="🎨 Libreria Icone":
        st.markdown("## 🎨 Libreria Icone")
        with st.form("icone"):
            nome_i = st.text_input("Nome icona *")
            if st.form_submit_button("✅ Salva Icona", use_container_width=True, type="primary"):
                if nome_i:
                    st.session_state.icone.append({"Nome":nome_i})
                    st.success("Icona salvata")
        if st.session_state.icone: st.dataframe(pd.DataFrame(st.session_state.icone), use_container_width=True)

    elif st.session_state.menu=="📥 Esporta":
        st.markdown("## 📥 Esporta")
        def dl(df,name):
            out = BytesIO()
            df.to_excel(out, index=False, engine="openpyxl")
            st.download_button(f"📥 Scarica {name}", out.getvalue(), file_name=f"{name.lower()}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        if st.session_state.volontari: dl(pd.DataFrame(st.session_state.volontari),"Volontari")
        if st.session_state.radio_db: dl(pd.DataFrame(st.session_state.radio_db),"Radio_DB")
        if st.session_state.brogliaccio: dl(pd.DataFrame(st.session_state.brogliaccio),"Brogliaccio")
        if st.session_state.eventi: dl(pd.DataFrame(st.session_state.eventi),"Eventi")