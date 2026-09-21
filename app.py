import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime, date
import pydeck as pdk

st.set_page_config(page_title="ANA Varese", layout="wide")

def hdr_small():
    st.markdown("<div style='background:#0e7a3d; padding:8px; border-radius:8px; color:white; text-align:center; font-weight:bold;'>NUCLEO VOLONTARI PROTEZIONE CIVILE</div>", unsafe_allow_html=True)

for k in ["page","logged","menu","volontari","radio_db","brogliaccio","eventi","checkin","icone","mezzi","attrezzature","map_markers","postazioni"]:
    if k not in st.session_state:
        if k == "page": st.session_state[k] = "entra"
        elif k == "logged": st.session_state[k] = False
        elif k == "menu": st.session_state[k] = "Dashboard"
        else: st.session_state[k] = []

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

elif st.session_state.page == "dashboard":
    hdr_small()
    with st.sidebar:
        menu = st.radio("Scegli:", ["Dashboard","Volontari","Eventi","Check-in","Mappa Avanzata","Libreria Icone","Backup"], index=0)
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
        st.markdown("## Volontari")
        with st.form("vol"):
            nome = st.text_input("Nome e Cognome *")
            comune = st.text_input("Comune *")
            lat_txt = st.text_input("Lat - VUOTO=no default")
            lon_txt = st.text_input("Log - VUOTO=no default")
            if st.form_submit_button("Salva", use_container_width=True, type="primary"):
                if nome and comune:
                    try:
                        lat_v = float(lat_txt.replace(",",".")) if lat_txt else 0.0
                        lon_v = float(lon_txt.replace(",",".")) if lon_txt else 0.0
                    except:
                        lat_v = 0.0
                        lon_v = 0.0
                    st.session_state.volontari.append({"Nome": nome, "Comune": comune, "Lat": lat_v, "Log": lon_v})
                    st.success("Salvato")
        if st.session_state.volontari:
            st.dataframe(pd.DataFrame(st.session_state.volontari), use_container_width=True)

    elif st.session_state.menu == "Eventi":
        st.markdown("## Eventi - NOME EVENTO per Check-in")
        with st.form("eventi"):
            nome_evento = st.text_input("NOME EVENTO *")
            luogo_e = st.text_input("Luogo Evento *")
            lat_e = st.text_input("Lat Evento")
            lon_e = st.text_input("Log Evento")
            if st.form_submit_button("Crea Evento", use_container_width=True, type="primary"):
                if nome_evento and luogo_e:
                    try:
                        lat_ev = float(lat_e.replace(",",".")) if lat_e else 0.0
                        lon_ev = float(lon_e.replace(",",".")) if lon_e else 0.0
                    except:
                        lat_ev = 0.0
                        lon_ev = 0.0
                    st.session_state.eventi.append({"NomeEvento": nome_evento, "Luogo": luogo_e, "Lat": lat_ev, "Log": lon_ev})
                    st.success("Evento creato")
        if st.session_state.eventi:
            st.dataframe(pd.DataFrame(st.session_state.eventi), use_container_width=True)

    elif st.session_state.menu == "Check-in":
        st.markdown("## Check-in - Maschera completa")
        if not st.session_state.eventi:
            st.warning("Crea prima Evento")
        elif not st.session_state.volontari:
            st.warning("Registra prima Volontari")
        else:
            with st.form("form_checkin"):
                ev_sel = st.selectbox("NOME EVENTO *", [e["NomeEvento"] for e in st.session_state.eventi])
                vol_sel = st.selectbox("Volontario *", [v["Nome"] for v in st.session_state.volontari])
                data_c = st.date_input("Data", value=date.today())
                ora_c = st.time_input("Ora", value=datetime.now().time())
                postazione_c = st.selectbox("Postazione", ["Base","Avanzata"] + [p["Nome"] for p in st.session_state.postazioni] if st.session_state.postazioni else ["Base","Avanzata"])
                note_c = st.text_input("Note")
                if st.form_submit_button("REGISTRA CHECK-IN", use_container_width=True, type="primary"):
                    ev_info = next((e for e in st.session_state.eventi if e["NomeEvento"]==ev_sel), None)
                    luogo_ev = ev_info["Luogo"] if ev_info else ""
                    st.session_state.checkin.append({"NomeEvento": ev_sel, "Volontario": vol_sel, "Data": str(data_c), "Ora": str(ora_c), "Postazione": postazione_c, "Note": note_c, "LuogoEvento": luogo_ev})
                    st.success("Check-in registrato")
        if st.session_state.checkin:
            st.dataframe(pd.DataFrame(st.session_state.checkin), use_container_width=True)

    elif st.session_state.menu == "Libreria Icone":
        st.markdown("## Libreria Icone - Upload e Download")
        with st.form("icone_upload"):
            nome_i = st.text_input("Nome icona *")
            file_i = st.file_uploader("Carica icona", type=["png","svg","jpg","jpeg"])
            if st.form_submit_button("Salva Icona", use_container_width=True, type="primary"):
                if nome_i and file_i:
                    st.session_state.icone.append({"Nome": nome_i, "FileName": file_i.name, "FileBytes": file_i.getvalue(), "Tipo": file_i.type})
                    st.success("Icona caricata")
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

    elif st.session_state.menu == "Mappa Avanzata":
        st.markdown("## Mappa Avanzata - Fix riga 307")
        tipo_mappa = st.selectbox("Cambia tipo mappa:", ["Google Maps","Google Earth Satellite","Waze Dark","HERE Light"])
        st.info(f"Mappa: {tipo_mappa} | VUOTO=no default")

        tab1, tab2, tab3 = st.tabs(["Visione Mappe","Form Postazioni","Postazioni salvate sotto"])

        with tab1:
            all_markers = []
            for v in st.session_state.volontari:
                lat_v = v.get("Lat",0)
                lon_v = v.get("Log",0)
                if lat_v!= 0 and lon_v!= 0:
                    all_markers.append({"lat": lat_v, "lon": lon_v, "tipo": "Volontario", "nome": v["Nome"], "info": v.get("Comune",""), "color": [14,122,61]})
            for e in st.session_state.eventi:
                lat_e = e.get("Lat",0)
                lon_e = e.get("Log",0)
                if lat_e!= 0 and lon_e!= 0:
                    all_markers.append({"lat": lat_e, "lon": lon_e, "tipo": "Evento", "nome": e.get("NomeEvento",""), "info": e.get("Luogo",""), "color": [255,0,0]})
            for p in st.session_state.postazioni:
                all_markers.append({"lat": p["Lat"], "lon": p["Log"], "tipo": p.get("Tipo","Postazione"), "nome": p["Nome"], "info": p.get("Comune",""), "color": [0,100,255]})

            if all_markers:
                df_map = pd.DataFrame(all_markers)
                # FIX RIGA 307 - senza virgolette ["lat"]
                lat_mean = df_map.lat.mean()
                lon_mean = df_map.lon.mean()
                layer = pdk.Layer("ScatterplotLayer", data=df_map, get_position='[lon, lat]', get_color='color', get_radius=200, pickable=True)
                view = pdk.ViewState(latitude=lat_mean, longitude=lon_mean, zoom=11)
                tooltip = {"html": "<b>{nome}</b><br>{tipo}<br>{info}", "style": {"backgroundColor": "steelblue", "color": "white"}}
                deck = pdk.Deck(layers=[layer], initial_view_state=view, tooltip=tooltip)
                st.pydeck_chart(deck)
                st.dataframe(df_map, use_container_width=True)

                sel = st.selectbox("Apri in app esterne", [f"{m['nome']} - {m['lat']},{m['lon']}" for m in all_markers])
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
                st.warning("Nessun marker - inserisci Lat/Log")

        with tab2:
            with st.form("form_postazioni"):
                nome_p = st.text_input("Nome Postazione *")
                tipo_p = st.selectbox("Tipo *", ["Postazione","Punto ritrovo","Magazzino","Sede","Idrante","Altro"])
                comune_p = st.text_input("Comune *")
                lat_p = st.text_input("Lat *", placeholder="45.123456")
                lon_p = st.text_input("Log *", placeholder="8.123456")
                note_p = st.text_area("Note")
                if st.form_submit_button("Aggiungi Postazione", use_container_width=True, type="primary"):
                    if nome_p and comune_p and lat_p and lon_p:
                        try:
                            lat_v = float(lat_p.replace(",","."))
                            lon_v = float(lon_p.replace(",","."))
                            st.session_state.postazioni.append({"Nome": nome_p, "Tipo": tipo_p, "Comune": comune_p, "Lat": lat_v, "Log": lon_v, "Note": note_p, "Data": datetime.now().strftime("%d/%m/%Y %H:%M")})
                            st.success(f"Postazione {nome_p} salvata sotto")
                        except:
                            st.error("Lat/Log non validi")
                    else:
                        st.error("Compila campi *")

        with tab3:
            st.markdown("### Postazioni Salvate su altra Mappa sotto")
            if st.session_state.postazioni:
                df_post = pd.DataFrame(st.session_state.postazioni)
                st.dataframe(df_post, use_container_width=True)
                # FIX anche qui senza ["Lat"]
                lat_p_mean = df_post.Lat.mean()
                lon_p_mean = df_post.Log.mean()
                layer_p = pdk.Layer("ScatterplotLayer", data=df_post, get_position='[Log, Lat]', get_color='[0, 100, 255]', get_radius=200, pickable=True)
                view_p = pdk.ViewState(latitude=lat_p_mean, longitude=lon_p_mean, zoom=11)
                tooltip_p = {"html": "<b>{Nome}</b><br>{Tipo}<br>{Comune}", "style": {"backgroundColor": "blue", "color": "white"}}
                deck_p = pdk.Deck(layers=[layer_p], initial_view_state=view_p, tooltip=tooltip_p)
                st.pydeck_chart(deck_p)
                out = BytesIO()
                df_post.to_excel(out, index=False, engine="openpyxl")
                st.download_button("Scarica Postazioni", out.getvalue(), file_name=f"postazioni_{date.today()}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
            else:
                st.warning("Nessuna postazione")

    elif st.session_state.menu == "Backup":
        st.markdown("## Backup")
        if st.session_state.volontari:
            out = BytesIO()
            pd.DataFrame(st.session_state.volontari).to_excel(out, index=False, engine="openpyxl")
            st.download_button("Scarica Volontari", out.getvalue(), file_name="volontari.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)