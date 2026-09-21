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
        "font-weight:bold;'>NUCLEO VOLONTARI PROTEZIONE CIVILE "
        "- ANA VARESE</div>",
        unsafe_allow_html=True
    )

def df_to_excel_bytes(df):
    out = BytesIO()
    df.to_excel(out, index=False, engine="openpyxl")
    return out.getvalue()

def df_to_pdf_bytes(df, title="Report"):
    try:
        from reportlab.lib.pagesizes import landscape, A4
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Paragraph
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib import colors
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(A4))
        styles = getSampleStyleSheet()
        story = []
        story.append(Paragraph(title, styles['Title']))
        story.append(Spacer(1, 12))
        data = [df.columns.tolist()] + df.astype(str).values.tolist()
        data = data[:40]
        t = Table(data)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0e7a3d")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTSIZE', (0,0), (-1,0), 8),
            ('FONTSIZE', (0,1), (-1,-1), 6),
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ]))
        story.append(t)
        doc.build(story)
        return buffer.getvalue()
    except:
        buffer = BytesIO()
        buffer.write(f"{title}\n".encode())
        buffer.write(df.to_string().encode())
        return buffer.getvalue()

def export_buttons(df, name):
    c1,c2 = st.columns(2)
    with c1:
        st.download_button(
            f"Scarica {name} Excel",
            df_to_excel_bytes(df),
            file_name=f"{name.lower()}_{date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key=f"excel_{name}_{len(df)}"
        )
    with c2:
        st.download_button(
            f"Scarica {name} PDF",
            df_to_pdf_bytes(df, name),
            file_name=f"{name.lower()}_{date.today()}.pdf",
            mime="application/pdf",
            use_container_width=True,
            key=f"pdf_{name}_{len(df)}"
        )

for k in [
    "page","logged","menu","volontari",
    "radio_db","brogliaccio","eventi",
    "checkin","icone","mezzi",
    "attrezzature","map_markers","postazioni"
]:
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
    st.markdown(
        "<h2 style='text-align:center; color:#0e7a3d;'>"
        "VOLONTARIATO<br>Sezione di Varese</h2>",
        unsafe_allow_html=True
    )
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
        st.markdown("### MENU FORM")
        menu = st.radio(
            "Scegli:",
            [
                "Dashboard","Volontari","DB Radio","Brogliaccio",
                "Eventi","Check-in","Mezzi","Attrezzature",
                "Mappa Avanzata","Libreria Icone","Backup","Esporta"
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
        st.markdown("## Dashboard - Scelta rapida")
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
            cell = st.text_input("Cellulare *")
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
                    st.session_state.volontari.append({
                        "Nome": nome,
                        "Comune": comune,
                        "Cellulare": cell,
                        "Lat": lat_v,
                        "Log": lon_v
                    })
                    st.success(f"Salvato {nome}")
        if st.session_state.volontari:
            df = pd.DataFrame(st.session_state.volontari)
            st.dataframe(df, use_container_width=True)
            export_buttons(df, "Volontari")

    elif st.session_state.menu == "Eventi":
        st.markdown("## Eventi - NOME EVENTO per Check-in")
        with st.form("eventi"):
            nome_evento = st.text_input("NOME EVENTO *")
            luogo_e = st.text_input("Luogo Evento *")
            lat_e = st.text_input("Lat Evento - VUOTO=no default")
            lon_e = st.text_input("Log Evento - VUOTO=no default")
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
                        "Lat": lat_ev,
                        "Log": lon_ev
                    })
                    st.success(f"Evento {nome_evento} creato")
        if st.session_state.eventi:
            df = pd.DataFrame(st.session_state.eventi)
            st.dataframe(df, use_container_width=True)
            export_buttons(df, "Eventi")

    elif st.session_state.menu == "Check-in":
        st.markdown("## Check-in - Maschera completa")
        if not st.session_state.eventi:
            st.warning("Crea prima Evento")
        elif not st.session_state.volontari:
            st.warning("Registra Volontari")
        else:
            with st.form("form_checkin"):
                ev_sel = st.selectbox(
                    "NOME EVENTO *",
                    [e["NomeEvento"] for e in st.session_state.eventi]
                )
                vol_sel = st.selectbox(
                    "Volontario *",
                    [v["Nome"] for v in st.session_state.volontari]
                )
                data_c = st.date_input("Data", value=date.today())
                ora_c = st.time_input("Ora", value=datetime.now().time())
                mezzo_c = st.selectbox("Mezzo", ["Nessuno","Piedi","Fuoristrada"])
                postazione_c = st.selectbox(
                    "Postazione",
                    ["Base","Avanzata"] + [p["Nome"] for p in st.session_state.postazioni]
                    if st.session_state.postazioni else ["Base","Avanzata"]
                )
                note_c = st.text_input("Note")
                if st.form_submit_button("REGISTRA CHECK-IN", use_container_width=True, type="primary"):
                    st.session_state.checkin.append({
                        "NomeEvento": ev_sel,
                        "Volontario": vol_sel,
                        "Data": str(data_c),
                        "Ora": str(ora_c),
                        "Mezzo": mezzo_c,
                        "Postazione": postazione_c,
                        "Note": note_c
                    })
                    st.success(f"Check-in {vol_sel} -> {ev_sel}")
        if st.session_state.checkin:
            df = pd.DataFrame(st.session_state.checkin)
            st.dataframe(df, use_container_width=True)
            export_buttons(df, "Checkin")

    elif st.session_state.menu == "Mappa Avanzata":
        st.markdown("## Mappa Avanzata")
        tipo_mappa = st.selectbox(
            "Cambia tipo mappa:",
            ["Google Maps Roadmap","Google Earth Satellite","Waze Dark","HERE Light"]
        )
        st.info(f"Mappa: {tipo_mappa} | VUOTO=no default")
        tab1, tab2, tab3 = st.tabs([
            "Visione Mappe",
            "Form Aggiungi Postazioni",
            "Postazioni salvate su altra mappa sotto"
        ])
        with tab1:
            all_markers = []
            for v in st.session_state.volontari:
                if v.get("Lat",0)!= 0 and v.get("Log",0)!= 0:
                    all_markers.append({
                        "lat": v["Lat"],
                        "lon": v["Log"],
                        "tipo": "Volontario",
                        "nome": v["Nome"],
                        "info": v.get("Comune",""),
                        "color": [14,122,61]
                    })
            for e in st.session_state.eventi:
                if e.get("Lat",0)!= 0 and e.get("Log",0)!= 0:
                    all_markers.append({
                        "lat": e["Lat"],
                        "lon": e["Log"],
                        "tipo": "Evento",
                        "nome": e.get("NomeEvento",""),
                        "info": e.get("Luogo",""),
                        "color": [255,0,0]
                    })
            for p in st.session_state.postazioni:
                all_markers.append({
                    "lat": p["Lat"],
                    "lon": p["Log"],
                    "tipo": p.get("Tipo","Postazione"),
                    "nome": p["Nome"],
                    "info": p.get("Comune",""),
                    "color": [0,100,255]
                })
            if all_markers:
                df_map = pd.DataFrame(all_markers)
                layer = pdk.Layer(
                    "ScatterplotLayer",
                    data=df_map,
                    get_position='[lon, lat]',
                    get_color='color',
                    get_radius=200,
                    pickable=True
                )
                view = pdk.ViewState(
                    latitude=df_map["lat