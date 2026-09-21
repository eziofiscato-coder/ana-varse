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

for k in [
    "page","logged","menu","volontari","radio_db",
    "brogliaccio","eventi","checkin","icone","mezzi",
    "attrezzature","postazioni","map_markers","last_clicked"
]:
    if k not in st.session_state:
        if k == "page": st.session_state[k] = "entra"
        elif k == "logged": st.session_state[k] = False
        elif k == "menu": st.session_state[k] = "Dashboard"
        elif k == "last_clicked": st.session_state[k] = None
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

# DASHBOARD
elif st.session_state.page == "dashboard":
    hdr_small()
    with st.sidebar:
        st.markdown("### MENU COMPLETO")
        menu = st.radio(
            "Scegli:",
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

    if st.session_state.menu == "Dashboard":
        st.markdown("## Dashboard - Menu completo")
        c1,c2,c3,c4 = st.columns(4)
        with c1: st.metric("Volontari", len(st.session_state.volontari))
        with c2: st.metric("Eventi", len(st.session_state.eventi))
        with c3: st.metric("Check-in", len(st.session_state.checkin))
        with c4: st.metric("Postazioni", len(st.session_state.postazioni))

    # VOLONTARI CON SOTTOMASCHERE + FOTO
    elif st.session_state.menu == "Volontari":
        st.markdown("## Volontari con sottomaschere + Foto")
        t1,t2,t3 = st.tabs(["Anagrafica e Foto","Contatti e Ruolo","Qualifiche"])
        with t1:
            with st.form("vol_anag"):
                nome = st.text_input("Nome e Cognome *")
                comune = st.text_input("Comune *")
                lat_txt = st.text_input("Lat - VUOTO=no default")
                lon_txt = st.text_input("Log - VUOTO=no default")
                foto_file = st.file_uploader("Foto Volontario", type=["png","jpg","jpeg"])
                if st.form_submit_button("Salva con Foto", use_container_width=True, type="primary"):
                    if nome and comune:
                        try:
                            lat_v = float(lat_txt.replace(",",".")) if lat_txt else 0.0
                            lon_v = float(lon_txt.replace(",",".")) if lon_txt else 0.0
                        except:
                            lat_v = 0.0
                            lon_v = 0.0
                        foto_bytes = foto_file.getvalue() if foto_file else None
                        foto_name = foto_file.name if foto_file else ""
                        st.session_state.volontari.append({
                            "Nome": nome,
                            "Comune": comune,
                            "Lat": lat_v,
                            "Log": lon_v,
                            "FotoBytes": foto_bytes,
                            "FotoName": foto_name,
                            "Cellulare": "",
                            "Ruolo": ""
                        })
                        st.success(f"Salvato {nome}")
        with t2:
            if st.session_state.volontari:
                sel = st.selectbox("Seleziona", [v["Nome"] for v in st.session_state.volontari])
                idx = [v["Nome"] for v in st.session_state.volontari].index(sel)
                vol = st.session_state.volontari[idx]
                if vol.get("FotoBytes"):
                    st.image(vol["FotoBytes"], width=150)
                with st.form("vol_cont"):
                    cell = st.text_input("Cellulare", value=vol.get("Cellulare",""))
                    ruolo = st.selectbox("Ruolo", ["Volontario","Caposquadra","Coordinatore"])
                    if st.form_submit_button("Aggiorna", use_container_width=True):
                        st.session_state.volontari[idx]["Cellulare"] = cell
                        st.session_state.volontari[idx]["Ruolo"] = ruolo
                        st.success("Aggiornato")
        with t3:
            if st.session_state.volontari:
                df = pd.DataFrame([{"Nome": v["Nome"], "Comune": v["Comune"]} for v in st.session_state.volontari])
                st.dataframe(df, use_container_width=True)
                export_buttons(df, "Volontari")

    # DB RADIO CON CAMPO COMBO
    elif st.session_state.menu == "DB Radio":
        st.markdown("## DB Radio - Con Campo Combo")
        with st.form("radio"):
            c1,c2 = st.columns(2)
            with c1:
                modello = st.text_input("Modello *")
                matricola = st.text_input("Matricola *")
                # CAMPO COMBO RICHIESTO
                tipo_combo = st.selectbox(
                    "Tipo Radio * - COMBO",
                    [
                        "DMR",
                        "PMR446",
                        "TETRA",
                        "NAUTICHE",
                        "VHF",
                        "UHF",
                        "VHF/UHF",
                        "HF",
                        "CB",
                        "LPD",
                        "Altro"
                    ]
                )
            with c2:
                freq = st.text_input("Frequenza")
                canale = st.text_input("Canale")
                potenza = st.selectbox("Potenza", ["0.5W","2W","5W","25W","50W"])
            assegnato = st.selectbox("Assegnato", ["Magazzino"] + [v["Nome"] for v in st.session_state.volontari] if st.session_state.volontari else ["Magazzino"])
            stato = st.selectbox("Stato", ["Operativa","In carica","Guasta"])
            if st.form_submit_button("Salva Radio con Combo", use_container_width=True, type="primary"):
                if modello and matricola:
                    st.session_state.radio_db.append({
                        "Modello": modello,
                        "Matricola": matricola,
                        "TipoCombo": tipo_combo,
                        "Frequenza": freq,
                        "Canale": canale,
                        "Potenza": potenza,
                        "Assegnato": assegnato,
                        "Stato": stato,
                        "Data": datetime.now().strftime("%d/%m/%Y")
                    })
                    st.success(f"Radio {tipo_combo} salvata")
                else:
                    st.error("Modello e Matricola *")
        if st.session_state.radio_db:
            df = pd.DataFrame(st.session_state.radio_db)
            st.dataframe(df, use_container_width=True)
            export_buttons(df, "Radio")

    # MAPPA AVANZATA COME STAMATTINA
    elif st.session_state.menu == "Mappa Avanzata":
        st.markdown("## Mappa Avanzata - Come Stamattina")
        tipo_mappa = st.selectbox(
            "Cambia tipo mappa:",
            ["Google Maps Roadmap","Google Earth Satellite","Waze Dark","HERE Light"]
        )
        st.info(f"Mappa: {tipo_mappa} - Clicca sulla mappa per marker")

        tab1, tab2, tab3 = st.tabs([
            "Mappa Cliccabile - Visione",
            "Form Postazioni con Icona",
            "Postazioni salvate su altra mappa sotto"
        ])

        with tab1:
            st.markdown("### Mappa visibile - Clicca per aggiungere marker")
            try:
                import folium
                from streamlit_folium import st_folium

                if st.session_state.postazioni:
                    lat_c = sum([p["Lat"] for p in st.session_state.postazioni]) / len(st.session_state.postazioni)
                    lon_c = sum([p["Log"] for p in st.session_state.postazioni]) / len(st.session_state.postazioni)
                else:
                    lat_c = 45.65
                    lon_c = 8.79

                m = folium.Map(location=[lat_c, lon_c], zoom_start=11)

                for v in st.session_state.volontari:
                    lat_v = v.get("Lat",0)
                    lon_v = v.get("Log",0)
                    if lat_v!= 0 and lon_v!= 0:
                        folium.Marker(
                            [lat_v, lon_v],
                            popup=f"Volontario: {v['Nome']}",
                            icon=folium.Icon(color="green")
                        ).add_to(m)

                for e in st.session_state.eventi:
                    lat_e = e.get("Lat",0)
                    lon_e = e.get("Log",0)
                    if lat_e!= 0 and lon_e!= 0:
                        folium.Marker(
                            [lat_e, lon_e],
                            popup=f"Evento: {e.get('NomeEvento','')}",
                            icon=folium.Icon(color="red")
                        ).add_to(m)

                for p in st.session_state.postazioni:
                    folium.Marker(
                        [p["Lat"], p["Log"]],
                        popup=f"{p['Nome']} - {p.get('Tipo','')} - Icona: {p.get('Icona','')}",
                        icon=folium.Icon(color="blue")
                    ).add_to(m)

                out = st_folium(m, height=500, width=700, returned_objects=["last_clicked"])

                if out and out.get("last_clicked"):
                    lat_click = out["last_clicked"]["lat"]
                    lon_click = out["last_clicked"]["lng"]
                    st.session_state.last_clicked = {"lat": lat_click, "lon": lon_click}
                    st.success(f"Cliccato: {lat_click:.6f}, {lon_click:.6f}")

                    c1,c2,c3 = st.columns(3)
                    with c1:
                        url_g = f"https://www.google.com/maps?q={lat_click},{lon_click}"
                        st.link_button("Google Maps", url_g, use_container_width=True)
                    with c2:
                        url_w = f"https://waze.com/ul?ll={lat_click},{lon_click}&navigate=yes"
                        st.link_button("Waze", url_w, use_container_width=True)
                    with c3:
                        url_e = f"https://earth.google.com/web/search/{lat_click},{lon_click}"
                        st.link_button("Google Earth", url_e, use_container_width=True)

            except Exception as e:
                st.error(f"Folium errore: {e}")
                # fallback pydeck
                all_markers = []
                for v in st.session_state.volontari:
                    lat_v = v.get("Lat",0)
                    lon_v = v.get("Log",0)
                    if lat_v!= 0 and lon_v!= 0:
                        all_markers.append({"lat": lat_v, "lon": lon_v, "tipo": "Volontario", "nome": v["Nome"], "color": [14,122,61]})
                for p in st.session_state.postazioni:
                    all_markers.append({"lat": p["Lat"], "lon": p["Log"], "tipo": p.get("Tipo",""), "nome": p["Nome"], "color": [0,100,255]})
                if all_markers:
                    df_map = pd.DataFrame(all_markers)
                    lat_mean = df_map.lat.mean()
                    lon_mean = df_map.lon.mean()
                    layer = pdk.Layer("ScatterplotLayer", data=df_map, get_position='[lon, lat]', get_color='color', get_radius=200, pickable=True)
                    view = pdk.ViewState(latitude=lat_mean, longitude=lon_mean, zoom=11)
                    deck = pdk.Deck(layers=[layer], initial_view_state=view)
                    st.pydeck_chart(deck)
                else:
                    st.warning("Nessun marker - mappa vuota")

        with tab2:
            st.markdown("### Form Postazioni con Icona da Libreria")
            last = st.session_state.last_clicked
            if last:
                st.info(f"Da click mappa: Lat {last['lat']:.6f} Log {last['lon']:.6f}")
            with st.form("form_postazioni"):
                nome_p = st.text_input("Nome Postazione *")
                tipo_p = st.selectbox("Tipo *", ["Postazione","Punto ritrovo","Magazzino","Sede","Idrante","Altro"])
                comune_p = st.text_input("Comune *")
                icona_p = st.selectbox("Icona da Libreria come Marker", ["Nessuna"] + [i["Nome"] for i in st.session_state.icone] if st.session_state.icone else ["Nessuna"])
                c1,c2 = st.columns(2)
                with c1:
                    lat_default = str(last["lat"]) if last else ""
                    lat_p = st.text_input("Lat *", value=lat_default)
                with c2:
                    lon_default = str(last["lon"]) if last else ""
                    lon_p = st.text_input("Log *", value=lon_default)
                note_p = st.text_area("Note")
                if st.form_submit_button("Aggiungi con Icona", use_container_width=True, type="primary"):
                    if nome_p and comune_p and lat_p and lon_p:
                        try:
                            lat_v = float(lat_p.replace(",","."))
                            lon_v = float(lon_p.replace(",","."))
                            st.session_state.postazioni.append({
                                "Nome": nome_p,
                                "Tipo": tipo_p,
                                "Comune": comune_p,
                                "Icona": icona_p,
                                "Lat": lat_v,
                                "Log": lon_v,
                                "Note": note_p,
                                "Data": datetime.now().strftime("%d/%m/%Y %H:%M")
                            })
                            st.success(f"Postazione {nome_p} con icona {icona_p} salvata sotto")
                        except:
                            st.error("Lat/Log non validi")
                    else:
                        st.error("Compila campi *")

        with tab3:
            st.markdown("### Postazioni salvate su altra mappa sotto")
            if st.session_state.postazioni:
                df_post = pd.DataFrame(st.session_state.postazioni)
                st.dataframe(df_post, use_container_width=True)
                export_buttons(df_post, "Postazioni")
                try:
                    import folium
                    from streamlit_folium import st_folium
                    lat_p_mean = df_post.Lat.mean()
                    lon_p_mean = df_post.Log.mean()
                    m2 = folium.Map(location=[lat_p_mean, lon_p_mean], zoom_start=12)
                    for p in st.session_state.postazioni:
                        folium.Marker(
                            [p["Lat"], p["Log"]],
                            popup=f"{p['Nome']} - Icona {p.get('Icona','')}",
                            icon=folium.Icon(color="blue")
                        ).add_to(m2)
                    st_folium(m2, height=400, width=700)
                except:
                    lat_p_mean = df_post.Lat.mean()
                    lon_p_mean = df_post.Log.mean()
                    layer_p = pdk.Layer("ScatterplotLayer", data=df_post, get_position='[Log, Lat]', get_color='[0, 100, 255]', get_radius=200, pickable=True)
                    view_p = pdk.ViewState(latitude=lat_p_mean, longitude=lon_p_mean, zoom=11)
                    deck_p = pdk.Deck(layers=[layer_p], initial_view_state=view_p)
                    st.pydeck_chart(deck_p)
            else:
                st.warning("Nessuna postazione")

    elif st.session_state.menu == "Eventi":
        st.markdown("## Eventi")
        with st.form("eventi"):
            nome_evento = st.text_input("NOME EVENTO *")
            luogo_e = st.text_input("Luogo *")
            if st.form_submit_button("Crea Evento", use_container_width=True, type="primary"):
                if nome_evento and luogo_e:
                    st.session_state.eventi.append({"NomeEvento": nome_evento, "Luogo": luogo_e, "Lat": 0.0, "Log": 0.0})
                    st.success("Evento creato")
        if st.session_state.eventi:
            df = pd.DataFrame(st.session_state.eventi)
            st.dataframe(df, use_container_width=True)
            export_buttons(df, "Eventi")

    elif st.session_state.menu == "Check-in":
        st.markdown("## Check-in")
        if st.session_state.eventi and st.session_state.volontari:
            with st.form("form_checkin"):
                ev_sel = st.selectbox("NOME EVENTO *", [e["NomeEvento"] for e in st.session_state.eventi])
                vol_sel = st.selectbox("Volontario *", [v["Nome"] for v in st.session_state.volontari])
                postazione_c = st.selectbox("Postazione", ["Base","Avanzata"] + [p["Nome"] for p in st.session_state.postazioni] if st.session_state.postazioni else ["Base","Avanzata"])
                if st.form_submit_button("REGISTRA", use_container_width=True, type="primary"):
                    st.session_state.checkin.append({"NomeEvento": ev_sel, "Volontario": vol_sel, "Postazione": postazione_c})
                    st.success("Check-in registrato")
        if st.session_state.checkin:
            df = pd.DataFrame(st.session_state.checkin)
            st.dataframe(df, use_container_width=True)
            export_buttons(df, "Checkin")

    elif st.session_state.menu == "Libreria Icone":
        st.markdown("## Libreria Icone")
        with st.form("icone_upload"):
            nome_i = st.text_input("Nome icona *")
            file_i = st.file_uploader("Carica icona", type=["png","svg","jpg","jpeg"])
            if st.form_submit_button("Salva Icona", use_container_width=True, type="primary"):
                if nome_i and file_i:
                    st.session_state.icone.append({"Nome": nome_i, "FileName": file_i.name, "FileBytes": file_i.getvalue(), "Tipo": file_i.type})
                    st.success(f"Icona {nome_i} caricata - disponibile in Mappa")
        if st.session_state.icone:
            for idx, ico in enumerate(st.session_state.icone):
                c1,c2 = st.columns([2,2])
                with c1:
                    st.write(ico["Nome"])
                    if ico.get("FileBytes"):
                        st.download_button(f"Download {ico['Nome']}", ico["FileBytes"], file_name=ico["FileName"], key=f"dl_{idx}", use_container_width=True)
                with c2:
                    if st.button("Elimina", key=f"del_{idx}"):
                        st.session_state.icone.pop(idx)
                        st.rerun()

    else:
        st.markdown(f"## {st.session_state.menu}")
        st.info("Form presente - dati con PDF ed Excel")