import streamlit as st
import pandas as pd
import os
from io import BytesIO
from datetime import datetime, date
import json
import base64
import tempfile

st.set_page_config(page_title="ANA Varese - Gestionale", page_icon="🎖️", layout="wide")

# === VERDE ALPINI ===
VERDE = "#2e7d32"
VERDE_SC = "#1b5e20"
VERDE_CH = "#e8f5e9"

st.markdown(f"""
<style>
h1,h2,h3 {{ color: {VERDE}!important; }}
.stButton>button {{
    background-color: {VERDE}!important;
    color: white!important;
    border: 2px solid {VERDE_SC}!important;
    font-weight: bold!important;
}}
[data-testid="stSidebar"] {{ background-color: {VERDE_CH}!important; }}
[data-testid="stMetricValue"] {{ color: {VERDE}!important; }}
</style>
""", unsafe_allow_html=True)

# === FUNZIONE PDF ===
def genera_pdf(df, titolo):
    try:
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib import colors
        buf = BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=landscape(A4), rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20)
        styles = getSampleStyleSheet()
        story = []
        story.append(Paragraph(f"<b>{titolo}</b> - {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Title']))
        story.append(Spacer(1, 12))
        if df.empty:
            story.append(Paragraph("Nessun dato", styles['Normal']))
        else:
            # prendi solo colonne senza bytes
            df_print = df[[c for c in df.columns if c not in ['Foto','FotoBytes','FileBytes']]].copy()
            df_print = df_print.astype(str)
            data = [list(df_print.columns)] + df_print.values.tolist()
            # limita a 8 colonne per pagina
            if len(data[0]) > 8:
                data = [row[:8] for row in data]
            t = Table(data)
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor(VERDE)),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,-1), 7),
                ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ]))
            story.append(t)
        doc.build(story)
        return buf.getvalue()
    except Exception as e:
        # fallback fpdf
        try:
            from fpdf import FPDF
            pdf = FPDF(orientation='L', unit='mm', format='A4')
            pdf.add_page()
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, f"{titolo} - {datetime.now()}", ln=True)
            pdf.set_font("Arial", '', 7)
            cols = [c for c in df.columns if c not in ['Foto','FotoBytes','FileBytes']][:8]
            for c in cols:
                pdf.cell(35, 6, str(c)[:20], border=1)
            pdf.ln()
            for _, r in df.head(100).iterrows():
                for c in cols:
                    pdf.cell(35, 5, str(r.get(c,''))[:20], border=1)
                pdf.ln()
            return pdf.output(dest='S').encode('latin-1')
        except Exception as e2:
            return None

def to_excel(df):
    out = BytesIO()
    # rimuovi colonne bytes per excel
    df2 = df[[c for c in df.columns if c not in ['Foto','FotoBytes','FileBytes']]].copy()
    df2.to_excel(out, index=False, engine='openpyxl')
    return out.getvalue()

def salva_icona_temp(file_bytes, nome):
    try:
        tmp_dir = tempfile.gettempdir()
        path = os.path.join(tmp_dir, f"icon_{nome}.png")
        with open(path, "wb") as f:
            f.write(file_bytes)
        return path
    except:
        return None

# === STATO ===
for k in ['volontari','radio_db','eventi','checkin','icone','postazioni','brogliaccio','mezzi','attrezzature','last_clicked','temp_markers','authenticated','map_fullscreen','selected_postazione']:
    if k not in st.session_state:
        if k in ['last_clicked','selected_postazione']:
            st.session_state[k] = None
        elif k in ['temp_markers']:
            st.session_state[k] = []
        elif k in ['map_fullscreen','authenticated']:
            st.session_state[k] = False
        else:
            st.session_state[k] = []

APP_PASSWORD = "ANA2025"
if not st.session_state.authenticated:
    c1,c2,c3 = st.columns([1,2,1])
    with c2:
        st.markdown(f"<h2 style='text-align:center;color:{VERDE}'>🔐 Accesso Riservato ANA Varese</h2>", unsafe_allow_html=True)
        pwd = st.text_input("Password", type="password")
        if st.button("Accedi", use_container_width=True, type="primary"):
            if pwd == APP_PASSWORD or pwd == "ana2024":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Password errata")
    st.stop()

# HEADER
try:
    c1,c2,c3 = st.columns([1,1,1])
    if os.path.exists("logo.png"): c1.image("logo.png", width=100)
    if os.path.exists("logo2.png"): c2.image("logo2.png", width=100)
    if os.path.exists("logo_pc_lombardia.png"): c3.image("logo_pc_lombardia.png", width=100)
except:
    pass

with st.sidebar:
    st.markdown(f"### <span style='color:{VERDE}'>MENU</span>", unsafe_allow_html=True)
    scelta = st.radio("Scegli", ["Dashboard","Volontari","DB Radio","Brogliaccio","Eventi","Check-in","Mezzi","Attrezzature","Mappa Avanzata","Libreria Icone","Backup"], index=0)

# === DASHBOARD ===
if scelta == "Dashboard":
    st.markdown(f"## <span style='color:{VERDE}'>Dashboard</span>", unsafe_allow_html=True)
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Volontari", len(st.session_state.volontari))
    c2.metric("Eventi", len(st.session_state.eventi))
    c3.metric("Check-in", len(st.session_state.checkin))
    c4.metric("Postazioni", len(st.session_state.postazioni))
    if st.session_state.postazioni:
        st.dataframe(pd.DataFrame(st.session_state.postazioni), use_container_width=True)
        col1,col2 = st.columns(2)
        with col1:
            st.download_button("📥 Excel Postazioni", to_excel(pd.DataFrame(st.session_state.postazioni)), file_name="postazioni.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        with col2:
            pdf = genera_pdf(pd.DataFrame(st.session_state.postazioni), "Postazioni")
            if pdf: st.download_button("📄 PDF Postazioni", pdf, file_name="postazioni.pdf", mime="application/pdf", use_container_width=True)

# === VOLONTARI ===
elif scelta == "Volontari":
    st.markdown(f"## <span style='color:{VERDE}'>Volontari</span>", unsafe_allow_html=True)
    t1,t2 = st.tabs(["Anagrafica","Elenco"])
    with t1:
        with st.form("vol"):
            nome = st.text_input("Nome *")
            comune = st.text_input("Comune *")
            foto = st.file_uploader("Foto", type=['png','jpg','jpeg'])
            if foto: st.image(foto, width=100)
            if st.form_submit_button("Salva", use_container_width=True, type="primary"):
                if nome and comune:
                    fb = foto.getvalue() if foto else None
                    st.session_state.volontari.append({"Nome": nome, "Comune": comune, "Foto": fb})
                    st.success("Salvato")
    with t2:
        if st.session_state.volontari:
            df = pd.DataFrame([{"Nome": v["Nome"], "Comune": v["Comune"]} for v in st.session_state.volontari])
            st.dataframe(df, use_container_width=True)
            c1,c2 = st.columns(2)
            c1.download_button("Excel", to_excel(df), file_name="volontari.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
            pdf = genera_pdf(df, "Volontari")
            if pdf: c2.download_button("PDF", pdf, file_name="volontari.pdf", mime="application/pdf", use_container_width=True)

# === DB RADIO ===
elif scelta == "DB Radio":
    st.markdown(f"## <span style='color:{VERDE}'>DB Radio</span>", unsafe_allow_html=True)
    with st.form("radio"):
        modello = st.text_input("Modello *")
        matricola = st.text_input("Matricola *")
        tipo = st.selectbox("Tipo *", ["DMR","PMR446","TETRA","NAUTICHE","VHF","UHF","VHF/UHF","HF","CB","Altro"])
        if st.form_submit_button("Salva", use_container_width=True, type="primary"):
            if modello and matricola:
                st.session_state.radio_db.append({"Modello": modello, "Matricola": matricola, "Tipo": tipo})
                st.success("Salvata")
    if st.session_state.radio_db:
        df = pd.DataFrame(st.session_state.radio_db)
        st.dataframe(df, use_container_width=True)
        c1,c2 = st.columns(2)
        c1.download_button("Excel Radio", to_excel(df), file_name="radio.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        pdf = genera_pdf(df, "Radio DB")
        if pdf: c2.download_button("PDF Radio", pdf, file_name="radio.pdf", mime="application/pdf", use_container_width=True)

# === BROGLIACCIO ===
elif scelta == "Brogliaccio":
    st.markdown(f"## <span style='color:{VERDE}'>Brogliaccio</span>", unsafe_allow_html=True)
    with st.form("brog"):
        mitt = st.text_input("Mittente")
        dest = st.text_input("Destinatario")
        msg = st.text_area("Messaggio *")
        if st.form_submit_button("Salva", use_container_width=True, type="primary"):
            if msg:
                st.session_state.brogliaccio.append({"Data": str(date.today()), "Mittente": mitt, "Destinatario": dest, "Messaggio": msg})
                st.success("Salvato")
    if st.session_state.brogliaccio:
        df = pd.DataFrame(st.session_state.brogliaccio)
        st.dataframe(df, use_container_width=True)
        c1,c2 = st.columns(2)
        c1.download_button("Excel", to_excel(df), file_name="brogliaccio.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        pdf = genera_pdf(df, "Brogliaccio")
        if pdf: c2.download_button("PDF", pdf, file_name="brogliaccio.pdf", mime="application/pdf", use_container_width=True)

# === EVENTI ===
elif scelta == "Eventi":
    st.markdown(f"## <span style='color:{VERDE}'>Eventi</span>", unsafe_allow_html=True)
    with st.form("eventi"):
        nome_e = st.text_input("NOME EVENTO *")
        luogo = st.text_input("Luogo *")
        if st.form_submit_button("Crea", use_container_width=True, type="primary"):
            if nome_e and luogo:
                st.session_state.eventi.append({"NomeEvento": nome_e, "Luogo": luogo, "Data": str(date.today())})
                st.success("Creato")
    if st.session_state.eventi:
        df = pd.DataFrame(st.session_state.eventi)
        st.dataframe(df, use_container_width=True)
        c1,c2 = st.columns(2)
        c1.download_button("Excel Eventi", to_excel(df), file_name="eventi.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        pdf = genera_pdf(df, "Eventi")
        if pdf: c2.download_button("PDF Eventi", pdf, file_name="eventi.pdf", mime="application/pdf", use_container_width=True)

# === CHECK-IN ===
elif scelta == "Check-in":
    st.markdown(f"## <span style='color:{VERDE}'>Check-in - Maschera Collegata Evento</span>", unsafe_allow_html=True)
    if not st.session_state.eventi or not st.session_state.volontari:
        st.warning("Crea Eventi e Volontari prima")
    else:
        ev_sel = st.selectbox("NOME EVENTO *", [e["NomeEvento"] for e in st.session_state.eventi])
        ev_det = next((e for e in st.session_state.eventi if e["NomeEvento"] == ev_sel), None)
        if ev_det: st.info(f"Evento: {ev_det.get('NomeEvento')} - Luogo: {ev_det.get('Luogo')}")
        with st.form("checkin"):
            vol = st.selectbox("Volontario *", [v["Nome"] for v in st.session_state.volontari])
            post = st.selectbox("Postazione", ["Base","Avanzata"] + [p["Nome"] for p in st.session_state.postazioni] if st.session_state.postazioni else ["Base","Avanzata"])
            note = st.text_area("Note")
            if st.form_submit_button("Registra", use_container_width=True, type="primary"):
                st.session_state.checkin.append({"NomeEvento": ev_sel, "Volontario": vol, "Postazione": post, "Note": note, "Data": str(date.today())})
                st.success("Registrato")
    if st.session_state.checkin:
        df = pd.DataFrame(st.session_state.checkin)
        st.dataframe(df, use_container_width=True)
        c1,c2 = st.columns(2)
        c1.download_button("Excel Check-in", to_excel(df), file_name="checkin.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        pdf = genera_pdf(df, "Check-in")
        if pdf: c2.download_button("PDF Check-in", pdf, file_name="checkin.pdf", mime="application/pdf", use_container_width=True)

# === MEZZI / ATTREZZATURE ===
elif scelta in ["Mezzi","Attrezzature"]:
    st.markdown(f"## <span style='color:{VERDE}'>{scelta}</span>", unsafe_allow_html=True)
    key = 'mezzi' if scelta == 'Mezzi' else 'attrezzature'
    with st.form(f"form_{key}"):
        nome = st.text_input(f"{scelta} *")
        if st.form_submit_button("Salva", use_container_width=True, type="primary"):
            if nome: st.session_state[key].append({scelta: nome})
    if st.session_state[key]:
        df = pd.DataFrame(st.session_state[key])
        st.dataframe(df, use_container_width=True)
        c1,c2 = st.columns(2)
        c1.download_button(f"Excel {scelta}", to_excel(df), file_name=f"{key}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        pdf = genera_pdf(df, scelta)
        if pdf: c2.download_button(f"PDF {scelta}", pdf, file_name=f"{key}.pdf", mime="application/pdf", use_container_width=True)

# === MAPPA AVANZATA ===
elif scelta == "Mappa Avanzata":
    st.markdown(f"## <span style='color:{VERDE}'>Mappa Avanzata - Marker con Icona Caricata</span>", unsafe_allow_html=True)

    # SCELTA TIPO MAPPA
    col_map1, col_map2, col_map3 = st.columns([2,2,2])
    with col_map1:
        map_type = st.selectbox("Tipo Mappa", ["OpenStreetMap","Google Map","Google Satellite","Google Hybrid","CartoDB Positron","CartoDB Dark","OpenTopoMap"])
    with col_map2:
        icona_sel = st.selectbox("Icona per Marker", ["Nessuna"] + [i["Nome"] for i in st.session_state.icone] if st.session_state.icone else ["Nessuna"])
    with col_map3:
        if st.button("⛶ Espandi / Riduci Mappa", use_container_width=True):
            st.session_state.map_fullscreen = not st.session_state.map_fullscreen

    map_height = 800 if st.session_state.map_fullscreen else 500

    try:
        import folium
        from streamlit_folium import st_folium
        import requests

        def rev_geo(lat, lon):
            try:
                url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=18&addressdetails=1"
                r = requests.get(url, headers={"User-Agent": "ANA-Varese"}, timeout=5)
                if r.status_code == 200:
                    d = r.json()
                    a = d.get('address',{})
                    c = a.get('city') or a.get('town') or a.get('village') or ''
                    v = a.get('road') or ''
                    return c, v
            except:
                pass
            return '', ''

        # centro
        if st.session_state.postazioni:
            lat_c = sum([p['Lat'] for p in st.session_state.postazioni]) / len(st.session_state.postazioni)
            lon_c = sum([p['Log'] for p in st.session_state.postazioni]) / len(st.session_state.postazioni)
        else:
            lat_c, lon_c = 45.65, 8.79

        m = folium.Map(location=[lat_c, lon_c], zoom_start=12, tiles=None)

        # Aggiungi tile in base a scelta
        if map_type == "OpenStreetMap":
            folium.TileLayer('openstreetmap', name='OpenStreetMap').add_to(m)
        elif map_type == "Google Map":
            folium.TileLayer(tiles='https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}', attr='Google', name='Google Map').add_to(m)
        elif map_type == "Google Satellite":
            folium.TileLayer(tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', attr='Google', name='Google Satellite').add_to(m)
        elif map_type == "Google Hybrid":
            folium.TileLayer(tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr='Google', name='Google Hybrid').add_to(m)
        elif map_type == "CartoDB Positron":
            folium.TileLayer('cartodbpositron', name='CartoDB Positron').add_to(m)
        elif map_type == "CartoDB Dark":
            folium.TileLayer('cartodbdark_matter', name='CartoDB Dark').add_to(m)
        elif map_type == "OpenTopoMap":
            folium.TileLayer('opentopomap', name='OpenTopoMap').add_to(m)

        # Prepara icona custom se selezionata
        icon_path = None
        icon_bytes = None
        if icona_sel!= "Nessuna":
            ico = next((i for i in st.session_state.icone if i["Nome"] == icona_sel), None)
            if ico and ico.get("FileBytes"):
                icon_bytes = ico["FileBytes"]
                icon_path = salva_icona_temp(icon_bytes, icona_sel)

        # Marker postazioni con icona caricata
        for p in st.session_state.postazioni:
            # se postazione ha icona salvata, usa quella
            p_icon_name = p.get('Icona','Nessuna')
            use_path = None
            if p_icon_name!= "Nessuna":
                ico_p = next((i for i in st.session_state.icone if i["Nome"] == p_icon_name), None)
                if ico_p and ico_p.get("FileBytes"):
                    use_path = salva_icona_temp(ico_p["FileBytes"], p_icon_name)

            # Link per navigazione
            lat_f, lon_f = p['Lat'], p['Log']
            popup_html = f"""
            <b>{p['Nome']}</b><br>
            {p.get('Comune','')} - {p.get('Via','')}<br>
            Icona: {p.get('Icona','')}<br>
            Lat:{lat_f:.5f} Lon:{lon_f:.5f}<br>
            <a href='https://www.google.com/maps/search/?api=1&query={lat_f},{lon_f}' target='_blank'>Google Map</a> |
            <a href='https://www.google.com/maps/dir/?api=1&destination={lat_f},{lon_f}' target='_blank'>Naviga</a> |
            <a href='https://waze.com/ul?ll={lat_f},{lon_f}&navigate=yes' target='_blank'>Waze</a> |
            <a href='https://earth.google.com/web/search/{lat_f},{lon_f}' target='_blank'>Google Earth</a>
            """
            if use_path:
                try:
                    icon = folium.CustomIcon(use_path, icon_size=(40,40))
                    folium.Marker([lat_f, lon_f], popup=folium.Popup(popup_html, max_width=300), tooltip=p['Nome'], icon=icon).add_to(m)
                except:
                    folium.Marker([lat_f, lon_f], popup=popup_html, icon=folium.Icon(color='green')).add_to(m)
            else:
                folium.Marker([lat_f, lon_f], popup=folium.Popup(popup_html, max_width=300), tooltip=p['Nome'], icon=folium.Icon(color='green', icon='info-sign')).add_to(m)

        # Marker temporanei con icona caricata
        for tm in st.session_state.temp_markers:
            tm_icon_name = tm.get('icona','Nessuna')
            tm_path = None
            if tm_icon_name!= "Nessuna":
                ico_tm = next((i for i in st.session_state.icone if i["Nome"] == tm_icon_name), None)
                if ico_tm and ico_tm.get("FileBytes"):
                    tm_path = salva_icona_temp(ico_tm["FileBytes"], tm_icon_name)
            if tm_path and icon_path: # se hai selezionato icona per marker
                try:
                    icon = folium.CustomIcon(tm_path if tm_path else icon_path, icon_size=(40,40))
                    folium.Marker([tm['lat'], tm['lon']], popup=f"TEMP {tm_icon_name}", icon=icon).add_to(m)
                except:
                    folium.Marker([tm['lat'], tm['lon']], popup=f"TEMP", icon=folium.Icon(color='orange')).add_to(m)
            else:
                if icon_path:
                    try:
                        icon = folium.CustomIcon(icon_path, icon_size=(40,40))
                        folium.Marker([tm['lat'], tm['lon']], popup=f"TEMP {tm.get('icona','')}", icon=icon).add_to(m)
                    except:
                        folium.Marker([tm['lat'], tm['lon']], icon=folium.Icon(color='orange')).add_to(m)
                else:
                    folium.Marker([tm['lat'], tm['lon']], icon=folium.Icon(color='orange')).add_to(m)

        folium.LayerControl().add_to(m)
        out = st_folium(m, width=1400, height=map_height, use_container_width=True, returned_objects=['last_clicked'])

        if out and out.get('last_clicked'):
            lat_c = out['last_clicked']['lat']
            lon_c = out['last_clicked']['lng']
            com, via = rev_geo(lat_c, lon_c)
            st.session_state.temp_markers.append({'lat': lat_c, 'lon': lon_c, 'icona': icona_sel, 'comune': com, 'via': via})
            st.session_state.last_clicked = {'lat': lat_c, 'lon': lon_c, 'icona': icona_sel, 'comune': com, 'via': via}
            st.success(f"Marker con icona {icona_sel}: {lat_c:.5f} {lon_c:.5f} - {com} {via}")
    except Exception as e:
        st.error(f"Errore mappa: {e}")

    last = st.session_state.last_clicked
    if last:
        st.info(f"Ultimo Click: Lat {last['lat']:.6f} Log {last['lon']:.6f} | Comune: {last.get('comune','')} Via: {last.get('via','')} | Icona: {last.get('icona','')}")

    # MASCHERA SOTTO MAPPA
    st.markdown("### 📍 Aggiungi Postazione da Click")
    with st.form("form_post"):
        nome_p = st.text_input("Nome Postazione *")
        comune_p = st.text_input("Comune *", value=last.get('comune','') if last else '')
        via_p = st.text_input("Via *", value=last.get('via','') if last else '')
        c1,c2 = st.columns(2)
        with c1:
            lat_p = st.text_input("Lat * - Auto da click", value=str(last['lat']) if last else '')
        with c2:
            lon_p = st.text_input("Log * - Auto da click", value=str(last['lon']) if last else '')
        lista_icone = ["Nessuna"] + [i["Nome"] for i in st.session_state.icone] if st.session_state.icone else ["Nessuna"]
        icona_def = last.get('icona','Nessuna') if last else 'Nessuna'
        idx_ico = lista_icone.index(icona_def) if icona_def in lista_icone else 0
        icona_p = st.selectbox("Icona Libreria per Marker", lista_icone, index=idx_ico)
        if icona_p!= "Nessuna":
            ico_prev = next((i for i in st.session_state.icone if i["Nome"] == icona_p), None)
            if ico_prev and ico_prev.get("FileBytes"):
                st.image(ico_prev["FileBytes"], width=60, caption=f"Icona {icona_p} per marker")
        note_p = st.text_area("Note")
        if st.form_submit_button("Salva Postazione con Icona", use_container_width=True, type="primary"):
            if nome_p and comune_p and lat_p and lon_p:
                try:
                    lat_v = float(lat_p.replace(',','.'))
                    lon_v = float(lon_p.replace(',','.'))
                    st.session_state.postazioni.append({"Nome": nome_p, "Comune": comune_p, "Via": via_p, "Icona": icona_p, "Lat": lat_v, "Log": lon_v, "Note": note_p})
                    st.session_state.temp_markers = []
                    st.session_state.last_clicked = None
                    st.success(f"Postazione {nome_p} con icona {icona_p} salvata")
                    st.rerun()
                except:
                    st.error("Lat/Log non validi")

    # MAPPA SOTTO MASCHERA CON TUTTE LE POSTAZIONI
    st.divider()
    st.markdown(f"## <span style='color:{VERDE}'>Mappa con Tutte le Postazioni Sotto Maschera</span>", unsafe_allow_html=True)
    if st.session_state.postazioni:
        df_post = pd.DataFrame(st.session_state.postazioni)
        st.dataframe(df_post, use_container_width=True)
        c1,c2,c3 = st.columns(3)
        with c1:
            st.download_button("📥 Excel Postazioni", to_excel(df_post), file_name="postazioni.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        with c2:
            pdf = genera_pdf(df_post, "Postazioni")
            if pdf: st.download_button("📄 PDF Postazioni", pdf, file_name="postazioni.pdf", mime="application/pdf", use_container_width=True)
        with c3:
            # Link Waze / Google Earth per tutte
            if st.session_state.postazioni:
                lat_m = df_post.Lat.mean() if 'Lat' in df_post.columns else 45.65
                lon_m = df_post.Log.mean() if 'Log' in df_post.columns else 8.79
                st.link_button("🌍 Apri Centro in Google Earth", f"https://earth.google.com/web/@{lat_m},{lon_m},500a", use_container_width=True)

        try:
            import folium
            from streamlit_folium import st_folium
            lat_m = df_post.Lat.mean()
            lon_m = df_post.Log.mean()
            m2 = folium.Map(location=[lat_m, lon_m], zoom_start=11, tiles=None)
            folium.TileLayer('openstreetmap', name='OpenStreetMap').add_to(m2)
            folium.TileLayer(tiles='https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}', attr='Google', name='Google Map').add_to(m2)
            folium.TileLayer(tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', attr='Google', name='Google Satellite').add_to(m2)
            for p in st.session_state.postazioni:
                p_icon_name = p.get('Icona','Nessuna')
                use_path = None
                if p_icon_name!= "Nessuna":
                    ico_p = next((i for i in st.session_state.icone if i["Nome"] == p_icon_name), None)
                    if ico_p and ico_p.get("FileBytes"):
                        use_path = salva_icona_temp(ico_p["FileBytes"], p_icon_name)
                popup_html = f"<b>{p['Nome']}</b><br>{p.get('Comune','')} {p.get('Via','')}<br><a href='https://www.google.com/maps/search/?api=1&query={p['Lat']},{p['Log']}' target='_blank'>Google</a> | <a href='https://waze.com/ul?ll={p['Lat']},{p['Log']}&navigate=yes' target='_blank'>Waze</a>"
                if use_path:
                    try:
                        icon = folium.CustomIcon(use_path, icon_size=(40,40))
                        folium.Marker([p['Lat'], p['Log']], popup=popup_html, tooltip=p['Nome'], icon=icon).add_to(m2)
                    except:
                        folium.Marker([p['Lat'], p['Log']], popup=popup_html, icon=folium.Icon(color='green')).add_to(m2)
                else:
                    folium.Marker([p['Lat'], p['Log']], popup=popup_html, icon=folium.Icon(color='green')).add_to(m2)
            folium.LayerControl().add_to(m2)
            st_folium(m2, width=1400, height=600, use_container_width=True)
        except Exception as e:
            st.error(f"Errore mappa sotto: {e}")
    else:
        st.info("Nessuna postazione - Aggiungi la prima dalla mappa sopra")

# === LIBRERIA ICONE ===
elif scelta == "Libreria Icone":
    st.markdown(f"## <span style='color:{VERDE}'>Libreria Icone - Visualizza Icona Caricata</span>", unsafe_allow_html=True)
    with st.form("icone"):
        nome_i = st.text_input("Nome icona *")
        file_i = st.file_uploader("Carica icona PNG/JPG - Sara usata come marker", type=['png','jpg','jpeg'])
        if file_i:
            st.image(file_i, width=120, caption="Preview icona caricata - Sara usata come marker mappa")
        if st.form_submit_button("Salva Icona per Marker", use_container_width=True, type="primary"):
            if nome_i and file_i:
                st.session_state.icone.append({"Nome": nome_i, "FileName": file_i.name, "FileBytes": file_i.getvalue()})
                st.success(f"Icona {nome_i} caricata - Ora disponibile in Mappa come marker")
    if st.session_state.icone:
        st.markdown("### Icone caricate - Marker Mappa")
        cols = st.columns(4)
        for idx, ico in enumerate(st.session_state.icone):
            col = cols[idx % 4]
            with col:
                st.write(f"**{ico['Nome']}**")
                if ico.get("FileBytes"):
                    st.image(ico["FileBytes"], width=80)
                    st.caption("Sara marker mappa")
                    if st.button(f"Usa in Mappa", key=f"use_{idx}"):
                        st.session_state.map_icon_selected = ico["Nome"]
                        st.success(f"Icona {ico['Nome']} selezionata per mappa")
                if st.button("Elimina", key=f"del_{idx}"):
                    st.session_state.icone.pop(idx)
                    st.rerun()

# === BACKUP ===
elif scelta == "Backup":
    st.markdown(f"## <span style='color:{VERDE}'>Backup Completo con PDF</span>", unsafe_allow_html=True)
    for key, titolo in [("volontari","Volontari"),("radio_db","Radio"),("eventi","Eventi"),("checkin","Check-in"),("postazioni","Postazioni"),("brogliaccio","Brogliaccio")]:
        if st.session_state[key]:
            df = pd.DataFrame(st.session_state[key])
            st.write(f"**{titolo}: {len(df)} record**")
            c1,c2 = st.columns(2)
            c1.download_button(f"Excel {titolo}", to_excel(df), file_name=f"{key}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key=f"excel_{key}", use_container_width=True)
            pdf = genera_pdf(df, titolo)
            if pdf:
                c2.download_button(f"PDF {titolo}", pdf, file_name=f"{key}.pdf", mime="application/pdf", key=f"pdf_{key}", use_container_width=True)