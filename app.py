import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime, date
import pydeck as pdk

st.set_page_config(page_title="ANA Varese", layout="wide")

def hdr_small():
    st.markdown(
        "<div style='background:#0e7a3d; padding:8px; "
        "border-radius:8px; color:white; text-align:center; "
        "font-weight:bold;'>NUCLEO VOLONTARI PROT CIVILE - ANA VARESE</div>",
        unsafe_allow_html=True
    )

def to_excel(df):
    out = BytesIO()
    df.to_excel(out, index=False, engine="openpyxl")
    return out.getvalue()

def to_pdf(df, title):
    try:
        from reportlab.lib.pagesizes import landscape, A4
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Paragraph
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib import colors
        buf = BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=landscape(A4))
        styles = getSampleStyleSheet()
        story = []
        story.append(Paragraph(title, styles['Title']))
        story.append(Spacer(1, 12))
        data = [df.columns.tolist()] + df.astype(str).values.tolist()
        data = data[:35]
        t = Table(data)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0e7a3d")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('FONTSIZE', (0,0), (-1,-1), 6),
        ]))
        story.append(t)
        doc.build(story)
        return buf.getvalue()
    except:
        buf = BytesIO()
        buf.write(title.encode())
        return buf.getvalue()

def export_buttons(df, name):
    c1,c2 = st.columns(2)
    with c1:
        st.download_button(
            f"Excel {name}",
            to_excel(df),
            file_name=f"{name}_{date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key=f"ex_{name}_{len(df)}"
        )
    with c2:
        st.download_button(
            f"PDF {name}",
            to_pdf(df, name),
            file_name=f"{name}_{date.today()}.pdf",
            mime="application/pdf",
            use_container_width=True,
            key=f"pdf_{name}_{len(df)}"
        )

# INIT
for k in ["page","logged","menu","volontari","radio_db","brogliaccio","eventi","checkin","icone","mezzi","attrezzature","postazioni","map_markers"]:
    if k not in st.session_state:
        if k == "page": st.session_state[k] = "entra"
        elif k == "logged": st.session_state[k] = False
        elif k == "menu": st.session_state[k] = "Dashboard"
        else: st.session_state[k] = []

# ENTRA
if st.session_state.page == "entra":
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
        if st.button("ENTRA", use_container_width=True, type="primary"):
            st.session_state.page = "login"
            st.rerun()

# LOGIN
elif st.session_state.page == "login":
    hdr_small()
    c1,c2,c3 = st.columns([1,2,1])
    with c2:
        user = st.text_input("Utente")
        pwd = st.text_input("Password", type="password")
        a,b = st.columns(2)
        with a:
            if st.button("Indietro", use_container_width=True):
                st.session_state.page = "entra"
                st.rerun()
        with b:
            if st.button("Accedi", use_container_width=True, type="primary"):
                if user == "admin" and pwd == "ana2024":
                    st.session_state.logged = True
                    st.session_state.page = "dashboard"
                    st.rerun()
                else:
                    st.error("admin / ana2024")

# DASHBOARD - MENU COMPLETO - NO IMMAGINE
elif st.session_state.page == "dashboard":
    hdr_small()
    with st.sidebar:
        st.markdown("### MENU COMPLETO")
        menu = st.radio(
            "Scegli form:",
            [
                "Dashboard",
                "Volontari",
                "DB Radio",
                "Brogliaccio",
                "Eventi",
                "Check-in",
                "Mezzi",
                "Attrezzature",
                "Mappa Avanzata",
                "Libreria Icone",
                "Backup",
                "Esporta"
            ],
            index=0
        )
        st.session_state.menu = menu
        st.divider()
        if st.button("Logout", use_container_width=True):
            st.session_state.logged = False
            st.session_state.page = "entra"
            st.rerun()

    # DASHBOARD
    if st.session_state.menu == "Dashboard":
        st.markdown("## Dashboard - Menu completo")
        c1,c2,c3,c4 = st.columns(4)
        with c1: st.metric("Volontari", len(st.session_state.volontari))
        with c2: st.metric("Eventi", len(st.session_state.eventi))
        with c3: st.metric("Check-in", len(st.session_state.checkin))
        with c4: st.metric("Postazioni", len(st.session_state.postazioni))
        st.markdown("### Tasti rapidi - Tutti i form")
        r1 = st.columns(4)
        with r1[0]:
            if st.button("VOLONTARI", use_container_width=True, type="primary"):
                st.session_state.menu = "Volontari"
                st.rerun()
        with r1[1]:
            if st.button("EVENTI", use_container_width=True):
                st.session_state.menu = "Eventi"
                st.rerun()
        with r1[2]:
            if st.button("CHECK-IN", use_container_width=True):
                st.session_state.menu = "Check-in"
                st.rerun()
        with r1[3]:
            if st.button("MAPPA", use_container_width=True):
                st.session_state.menu = "Mappa Avanzata"
                st.rerun()

    # VOLONTARI CON SOTTOMASCHERE
    elif st.session_state.menu == "Volontari":
        st.markdown("## Volontari con sottomaschere")
        t1,t2,t3 = st.tabs(["Anagrafica e Posizione","Contatti e Ruolo","Qualifiche e Note"])
        with t1:
            with st.form("vol_anag"):
                nome = st.text_input("Nome e Cognome *")
                cf = st.text_input("Codice Fiscale")
                comune = st.text_input("Comune residenza *")
                via = st.text_input("Via")
                c1,c2 = st.columns(2)
                with c1: lat_txt = st.text_input("Lat - VUOTO=no default")
                with c2: lon_txt = st.text_input("Log - VUOTO=no default")
                if st.form_submit_button("Salva Anagrafica", use_container_width=True, type="primary"):
                    if nome and comune:
                        try:
                            lat_v = float(lat_txt.replace(",",".")) if lat_txt else 0.0
                            lon_v = float(lon_txt.replace(",",".")) if lon_txt else 0.0
                        except:
                            lat_v = 0.0
                            lon_v = 0.0
                        st.session_state.volontari.append({
                            "Nome": nome,
                            "CF": cf,
                            "Comune": comune,
                            "Via": via,
                            "Lat": lat_v,
                            "Log": lon_v,
                            "Cellulare": "",
                            "Ruolo": "",
                            "Qualifiche": "",
                            "Note": ""
                        })
                        st.success(f"Salvato {nome}")
        with t2:
            if st.session_state.volontari:
                sel = st.selectbox("Seleziona volontario", [v["Nome"] for v in st.session_state.volontari])
                idx = [v["Nome"] for v in st.session_state.volontari].index(sel)
                with st.form("vol_cont"):
                    cell = st.text_input("Cellulare", value=st.session_state.volontari[idx].get("Cellulare",""))
                    ruolo = st.selectbox("Ruolo", ["Volontario","Caposquadra","Coordinatore","Autista","Radio"])
                    if st.form_submit_button("Aggiorna Contatti", use_container_width=True):
                        st.session_state.volontari[idx]["Cellulare"] = cell
                        st.session_state.volontari[idx]["Ruolo"] = ruolo
                        st.success("Aggiornato")
            else:
                st.info("Inserisci prima anagrafica in tab 1")
        with t3:
            if st.session_state.volontari:
                sel = st.selectbox("Volontario", [v["Nome"] for v in st.session_state.volontari], key="q")
                idx = [v["Nome"] for v in st.session_state.volontari].index(sel)
                qual = st.multiselect("Qualifiche", ["AIB","BLSD","Radio","Guida fuoristrada"])
                note = st.text_area("Note", value=st.session_state.volontari[idx].get("Note",""))
                if st.button("Salva Qualifiche e Note", use_container_width=True):
                    st.session_state.volontari[idx]["Qualifiche"] = ",".join(qual)
                    st.session_state.volontari[idx]["Note"] = note
                    st.success("Salvato")
                df = pd.DataFrame(st.session_state.volontari)
                st.dataframe(df, use_container_width=True)
                export_buttons(df, "Volontari")

    # EVENTI CON NOME EVENTO
    elif st.session_state.menu == "Eventi":
        st.markdown("## Eventi - NOME EVENTO per Check-in")
        with st.form("eventi"):
            nome_evento = st.text_input("NOME EVENTO * per check-in")
            luogo_e = st.text_input("Luogo Evento *")
            tipo_e = st.selectbox("Tipo", ["Emergenza","Esercitazione","Prevenzione"])
            lat_e = st.text_input("Lat Evento - VUOTO=no default")
            lon_e = st.text_input("Log Evento - VUOTO=no default")
            descr = st.text_area("Descrizione")
            if st.form_submit_button("Crea Evento", use_container_width=True, type="primary"):
                if nome_evento and luogo_e:
                    try:
                        lat_ev = float(lat_e.replace(",",".")) if lat_e else 0.0
                        lon_ev = float(lon_e.replace(",",".")) if lon_e else 0.0
                    except:
                        lat_ev = 0.0
                        lon_ev = 0.0
                    st.session_state.eventi.append({
                        "NomeEvento": nome_evento,
                        "Luogo": luogo_e,
                        "Tipo": tipo_e,
                        "Lat": lat_ev,
                        "Log": lon_ev,
                        "Descrizione": descr,
                        "Stato": "Aperto"
                    })
                    st.success(f"Evento {nome_evento} creato")
        if st.session_state.eventi:
            df = pd.DataFrame(st.session_state.eventi)
            st.dataframe(df, use_container_width=True)
            export_buttons(df, "Eventi")

    # CHECK-IN MASCHERA COMPLETA
    elif st.session_state.menu == "Check-in":
        st.markdown("## Check-in - Maschera completa associata a NOME EVENTO")
        if not st.session_state.eventi:
            st.warning("Crea prima Evento con NOME EVENTO")
        elif not st.session_state.volontari:
            st.warning("Registra prima Volontari")
        else:
            with st.form("form_checkin"):
                ev_sel = st.selectbox("NOME EVENTO *", [e["NomeEvento"] for e in st.session_state.eventi])
                vol_sel = st.selectbox("Volontario *", [v["Nome"] for v in st.session_state.volontari])
                c1,c2 = st.columns(2)
                with c1:
                    data_c = st.date_input("Data", value=date.today())
                    ora_c = st.time_input("Ora", value=datetime.now().time())
                with c2:
                    mezzo_c = st.selectbox("Mezzo", ["Nessuno","Piedi","Fuoristrada","Furgone"])
                    postazione_c = st.selectbox("Postazione", ["Base","Avanzata"] + [p["Nome"] for p in st.session_state.postazioni] if st.session_state.postazioni else ["Base","Avanzata"])
                note_c = st.text_input("Note")
                if st.form_submit_button("REGISTRA CHECK-IN", use_container_width=True, type="primary"):
                    ev_info = next((e for e in st.session_state.eventi if e["NomeEvento"]==ev_sel), None)
                    luogo_ev = ev_info["Luogo"] if ev_info else ""
                    st.session_state.checkin.append({
                        "NomeEvento": ev_sel,
                        "Volontario": vol_sel,
                        "Data": str(data_c),
                        "Ora": str(ora_c),
                        "Mezzo": mezzo_c,
                        "Postazione": postazione_c,
                        "Note": note_c,
                        "LuogoEvento": luogo_ev
                    })
                    st.success(f"Check-in {vol_sel} -> {ev_sel}")
        if st.session_state.checkin:
            df = pd.DataFrame(st.session_state.checkin)
            st.dataframe(df, use_container_width=True)
            export_buttons(df, "Checkin")

    # MAPPA AVANZATA CON TUTTO
    elif st.session_state.menu == "Mappa Avanzata":
        st.markdown("## Mappa Avanzata - Gran lavoro stamattina")
        tipo_mappa = st.selectbox("Cambia tipo mappa:", ["Google Maps Roadmap","Google Earth Satellite","Waze Dark","HERE Light"])
        st.info(f"Mappa: {tipo_mappa} | VUOTO=no default | Icona da libreria come marker")

        tab1, tab2, tab3 = st.tabs(["Visione Mappe","Form Aggiungi Postazioni con Icona","Postazioni salvate su altra mappa sotto"])

        with tab1:
            all_markers = []
            for v in st.session_state.volontari:
                lat_v = v.get("Lat",0)
                lon_v = v.get("Log",0)
                if lat_v!= 0 and lon_v!= 0:
                    all_markers.append({"lat": lat_v, "lon": lon_v, "tipo": "Volontario", "nome": v["Nome"], "info": v.get("Comune",""), "color": [14,122,61], "icona": ""})
            for e in st.session_state.eventi:
                lat_e = e.get("Lat",0)
                lon_e = e.get("Log",0)
                if lat_e!= 0 and lon_e!= 0:
                    all_markers.append({"lat": lat_e, "lon": lon_e, "tipo": "Evento", "nome": e.get("NomeEvento",""), "info": e.get("Luogo",""), "color": [255,0,0], "icona": ""})
            for p in st.session_state.postazioni:
                all_markers.append({"lat": p["Lat"], "lon": p["Log"], "tipo": p.get("Tipo","Postazione"), "nome": p["Nome"], "info": p.get("Comune",""), "color": [0,100,255], "icona": p.get("Icona","")})

            if all_markers:
                df_map = pd.DataFrame(all_markers)
                lat_mean = df_map.lat.mean()
                lon_mean = df_map.lon.mean()
                layer = pdk.Layer("ScatterplotLayer", data=df_map, get_position='[lon, lat]', get_color='color', get_radius=200, pickable=True)
                view = pdk.ViewState(latitude=lat_mean, longitude=lon_mean, zoom=11)
                tooltip = {"html": "<b>{nome}</b><br>{tipo}<br>{info}<br>Icona: {icona}", "style": {"backgroundColor": "steelblue", "color": "white"}}
                deck = pdk.Deck(layers=[layer], initial_view_state=view, tooltip=tooltip)
                st.pydeck_chart(deck)
                st.dataframe(df_map, use_container_width=True)
                export_buttons(df_map, "Mappa_Totale")

                sel = st.selectbox("Apri in Google Maps / Waze / Earth", [f"{m['nome']} - {m['lat']},{m['lon']}" for m in all_markers])
                if sel:
                    for m in all_markers:
                        tag = f"{m['nome']} - {m['lat']},{m['lon']}"
                        if tag == sel:
                            m_sel = m
                            break
                    c1,c2,c3 = st.columns(3)
                    with c1:
                        url_g = f"https://www.google.com/maps?q={m_sel['lat']},{m_sel['lon']}"
                        st.link_button("Google Maps", url_g, use_container_width=True)
                    with c2:
                        url_w = f"https://waze.com/ul?ll={m_sel['lat']},{m_sel['lon']}&navigate=yes"
                        st.link_button("Waze", url_w, use_container_width=True)
                    with c3:
                        url_e = f"https://earth.google.com/web/search/{m_sel['lat']},{m_sel['lon']}"
                        st.link_button("Google Earth", url_e, use_container_width=True)
            else:
                st.warning("Nessun marker - inserisci Lat/Log - VUOTO=no default")

        with tab2:
            st.markdown("### Aggiungi Postazione con Icona da Libreria come Marker")
            if not st.session_state.icone:
                st.warning("Carica prima icone in Libreria Icone per usarle come marker")
            with st.form("form_postazioni"):
                nome_p = st.text_input("Nome Postazione *")
                tipo_p = st.selectbox("Tipo Postazione *", ["Postazione","Punto ritrovo","Magazzino","Sede","Idrante","Base Operativa","Altro"])
                comune_p = st.text_input("Comune Postazione *")
                via_p = st.text_input("Via")
                # CARICAMENTO ICONA DA LIBRERIA PER MARKER
                icona_p = st.selectbox("Icona da Libreria come Marker *", ["Nessuna"] + [i["Nome"] for i in st.session_state.icone] if st.session_state.icone else ["Nessuna"])
                stato_p = st.selectbox("Stato", ["Operativa","Non operativa","In allestimento"])
                c1,c2 = st.columns(2)
                with c1: lat_p = st.text_input("Lat * - VUOTO=no default", placeholder="45.123456")
                with c2: lon_p = st.text_input("Log * - VUOTO=no default", placeholder="8.123456")
                note_p = st.text_area("Note")
                if st.form_submit_button("Aggiungi Postazione con Icona Marker", use_container_width=True, type="