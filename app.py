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
        # PDF semplificato
        buf = BytesIO()
        buf.write(f"{name}".encode())
        st.download_button(
            f"PDF {name}",
            buf.getvalue(),
            file_name=f"{name}_{date.today()}.pdf",
            mime="application/pdf",
            use_container_width=True,
            key=f"pdf_{name}_{len(df)}"
        )

for k in [
    "page","logged","menu","volontari","radio_db",
    "brogliaccio","eventi","checkin","icone","mezzi",
    "attrezzature","postazioni","map_markers",
    "last_clicked","temp_markers"
]:
    if k not in st.session_state:
        if k == "page": st.session_state[k] = "entra"
        elif k == "logged": st.session_state[k] = False
        elif k == "menu": st.session_state[k] = "Dashboard"
        elif k == "last_clicked": st.session_state[k] = None
        elif k == "temp_markers": st.session_state[k] = []
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
            ["Dashboard","Volontari","DB Radio","Brogliaccio","Eventi","Check-in","Mezzi","Attrezzature","Mappa Avanzata","Libreria Icone","Backup","Esporta"],
            index=0
        )
        st.session_state.menu = menu
        st.divider()
        if st.button("Logout", use_container_width=True):
            st.session_state.logged = False
            st.session_state.page = "entra"
            st.rerun()

    if st.session_state.menu == "Dashboard":
        st.markdown("## Dashboard")
        c1,c2,c3,c4 = st.columns(4)
        with c1: st.metric("Volontari", len(st.session_state.volontari))
        with c2: st.metric("Eventi", len(st.session_state.eventi))
        with c3: st.metric("Check-in", len(st.session_state.checkin))
        with c4: st.metric("Postazioni", len(st.session_state.postazioni))

    elif st.session_state.menu == "Volontari":
        st.markdown("## Volontari con sottomaschere + Foto")
        t1,t2 = st.tabs(["Anagrafica e Foto","Elenco"])
        with t1:
            with st.form("vol_anag"):
                nome = st.text_input("Nome e Cognome *")
                comune = st.text_input("Comune *")
                lat_txt = st.text_input("Lat - VUOTO=no default")
                lon_txt = st.text_input("Log - VUOTO=no default")
                foto_file = st.file_uploader("Foto Volontario", type=["png","jpg","jpeg"])
                if st.form_submit_button("Salva", use_container_width=True, type="primary"):
                    if nome and comune:
                        try:
                            lat_v = float(lat_txt.replace(",",".")) if lat_txt else 0.0
                            lon_v = float(lon_txt.replace(",",".")) if lon_txt else 0.0
                        except:
                            lat_v = 0.0
                            lon_v = 0.0
                        fb = foto_file.getvalue() if foto_file else None
                        fn = foto_file.name if foto_file else ""
                        st.session_state.volontari.append({
                            "Nome": nome,
                            "Comune": comune,
                            "Lat": lat_v,
                            "Log": lon_v,
                            "FotoBytes": fb,
                            "FotoName": fn
                        })
                        st.success("Salvato")
        with t2:
            if st.session_state.volontari:
                st.dataframe(pd.DataFrame([{"Nome": v["Nome"], "Comune": v["Comune"]} for v in st.session_state.volontari]), use_container_width=True)

    elif st.session_state.menu == "DB Radio":
        st.markdown("## DB Radio con Combo")
        with st.form("radio"):
            modello = st.text_input("Modello *")
            matricola = st.text_input("Matricola *")
            tipo_combo = st.selectbox(
                "Tipo * - COMBO",
                ["DMR","PMR446","TETRA","NAUTICHE","VHF","UHF","VHF/UHF","HF","CB","Altro"]
            )
            freq = st.text_input("Frequenza")
            assegnato = st.selectbox("Assegnato", ["Magazzino"] + [v["Nome"] for v in st.session_state.volontari] if st.session_state.volontari else ["Magazzino"])
            if st.form_submit_button("Salva Radio", use_container_width=True, type="primary"):
                if modello and matricola:
                    st.session_state.radio_db.append({
                        "Modello": modello,
                        "Matricola": matricola,
                        "TipoCombo": tipo_combo,
                        "Frequenza": freq,
                        "Assegnato": assegnato
                    })
                    st.success(f"Radio {tipo_combo} salvata")
        if st.session_state.radio_db:
            st.dataframe(pd.DataFrame(st.session_state.radio_db), use_container_width=True)

    # MAPPA AVANZATA COME STAMATTINA CON MARKER + ICONA LIBRERIA + MASCHERA AUTO
    elif st.session_state.menu == "Mappa Avanzata":
        st.markdown("## Mappa Avanzata - Come Stamattina")
        st.markdown("### Clicca sulla mappa per lasciare marker postazione con icona libreria")

        # Selettore icona da libreria PRIMA del click
        icona_selezionata = st.selectbox(
            "Scegli icona da Libreria per marker che lascerai cliccando",
            ["Nessuna"] + [i["Nome"] for i in st.session_state.icone] if st.session_state.icone else ["Nessuna"]
        )

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

            # marker esistenti postazioni
            for p in st.session_state.postazioni:
                # colore in base a icona
                folium.Marker(
                    [p["Lat"], p["Log"]],
                    popup=f"{p['Nome']} - {p.get('Comune','')} - Via {p.get('Via','')} - Icona {p.get('Icona','')}",
                    icon=folium.Icon(color="blue", icon="map-marker")
                ).add_to(m)

            # marker temporanei da click precedenti non ancora salvati
            for tm in st.session_state.temp_markers:
                folium.Marker(
                    [tm["lat"], tm["lon"]],
                    popup=f"TEMP - {tm.get('icona','')} - {tm['lat']:.5f},{tm['lon']:.5f}",
                    icon=folium.Icon(color="orange", icon="plus")
                ).add_to(m)

            # marker volontari
            for v in st.session_state.volontari:
                lat_v = v.get("Lat",0)
                lon_v = v.get("Log",0)
                if lat_v!= 0 and lon_v!= 0:
                    folium.Marker(
                        [lat_v, lon_v],
                        popup=f"Volontario {v['Nome']}",
                        icon=folium.Icon(color="green", icon="user")
                    ).add_to(m)

            out = st_folium(m, height=500, width=700, returned_objects=["last_clicked"])

            if out and out.get("last_clicked"):
                lat_click = out["last_clicked"]["lat"]
                lon_click = out["last_clicked"]["lng"]
                # lascia marker con icona libreria
                st.session_state.temp_markers.append({
                    "lat": lat_click,
                    "lon": lon_click,
                    "icona": icona_selezionata,
                    "comune": "",
                    "via": ""
                })
                st.session_state.last_clicked = {
                    "lat": lat_click,
                    "lon": lon_click,
                    "icona": icona_selezionata
                }
                st.success(f"Marker lasciato! Lat {lat_click:.6f} Log {lon_click:.6f} con icona {icona_selezionata} - Ora compila maschera sotto")

        except Exception as e:
            st.error(f"Folium errore {e} - uso pydeck")
            all_markers = []
            for p in st.session_state.postazioni:
                all_markers.append({"lat": p["Lat"], "lon": p["Log"], "nome": p["Nome"], "color": [0,100,255]})
            if all_markers:
                df_map = pd.DataFrame(all_markers)
                lat_mean = df_map.lat.mean()
                lon_mean = df_map.lon.mean()
                layer = pdk.Layer("ScatterplotLayer", data=df_map, get_position='[lon, lat]', get_color='color', get_radius=200, pickable=True)
                view = pdk.ViewState(latitude=lat_mean, longitude=lon_mean, zoom=11)
                deck = pdk.Deck(layers=[layer], initial_view_state=view)
                st.pydeck_chart(deck)

        # MASCHERA CON COORDINATE, COMUNE, VIA, LAT LOG DEL MARKER AUTO-INSERITE
        st.markdown("### Maschera Postazione - Dati da marker cliccato auto-inseriti")
        last = st.session_state.last_clicked
        if last:
            st.info(f"Dati da ultimo click: Lat {last['lat']:.6f} Log {last['lon']:.6f} Icona {last.get('icona','')} - Inseriti in maschera")

        with st.form("form_postazioni_auto"):
            nome_p = st.text_input("Nome Postazione *")
            tipo_p = st.selectbox("Tipo *", ["Postazione","Punto ritrovo","Magazzino","Sede","Idrante","Altro"])
            # Comune e Via auto-compilabili ma editabili
            comune_p = st.text_input("Comune * - Da marker", value="")
            via_p = st.text_input("Via * - Da marker", value="")
            c1,c2 = st.columns(2)
            with c1:
                lat_default = str(last["lat"]) if last else ""
                lat_p = st.text_input("Lat * - Auto da marker cliccato", value=lat_default, placeholder="45.123456")
            with c2:
                lon_default = str(last["lon"]) if last else ""
                lon_p = st.text_input("Log * - Auto da marker cliccato", value=lon_default, placeholder="8.123456")
            # icona da libreria pre-selezionata da click
            icona_default = last.get("icona","Nessuna") if last else "Nessuna"
            lista_icone = ["Nessuna"] + [i["Nome"] for i in st.session_state.icone] if st.session_state.icone else ["Nessuna"]
            if icona_default in lista_icone:
                idx_icona = lista_icone.index(icona_default)
            else:
                idx_icona = 0
            icona_p = st.selectbox("Icona da Libreria come Marker", lista_icone, index=idx_icona)
            note_p = st.text_area("Note")

            if st.form_submit_button("Salva Postazione con Marker e Icona", use_container_width=True, type="primary"):
                if nome_p and comune_p and lat_p and lon_p:
                    try:
                        lat_v = float(lat_p.replace(",","."))
                        lon_v = float(lon_p.replace(",","."))
                        st.session_state.postazioni.append({
                            "Nome": nome_p,
                            "Tipo": tipo_p,
                            "Comune": comune_p,
                            "Via": via_p,
                            "Icona": icona_p,
                            "Lat": lat_v,
                            "Log": lon_v,
                            "Note": note_p,
                            "Data": datetime.now().strftime("%d/%m/%Y %H:%M")
                        })
                        # rimuovi temp marker usato
                        if st.session_state.temp_markers:
                            st.session_state.temp_markers.pop()
                        st.session_state.last_clicked = None
                        st.success(f"Postazione {nome_p} - Comune {comune_p} Via {via_p} Lat {lat_v} Log {lon_v} Icona {icona_p} salvata")
                        st.rerun()
                    except:
                        st.error("Lat/Log non validi")
                else:
                    st.error("Compila Nome *, Comune *, Via *, Lat *, Log *")

        # Altra mappa sotto con postazioni salvate
        st.markdown("### Postazioni salvate su altra mappa sotto la maschera")
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
                        popup=f"{p['Nome']} - {p['Comune']} {p['Via']} - Icona {p.get('Icona','')}",
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
            st.warning("Nessuna postazione salvata")

    elif st.session_state.menu == "Libreria Icone":
        st.markdown("## Libreria Icone - Per marker mappa")
        with st.form("icone_upload"):
            nome_i = st.text_input("Nome icona *")
            cat_i = st.selectbox("Categoria", ["Postazioni","Mappa","Emergenza","Volontari"])
            file_i = st.file_uploader("Carica icona", type=["png","svg","jpg","jpeg"])
            if st.form_submit_button("Salva Icona", use_container_width=True, type="primary"):
                if nome_i and file_i:
                    st.session_state.icone.append({"Nome": nome_i, "Categoria": cat_i, "FileName": file_i.name, "FileBytes": file_i.getvalue(), "Tipo": file_i.type})
                    st.success(f"Icona {nome_i} caricata - disponibile come marker in mappa")
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

    elif st.session_state.menu == "