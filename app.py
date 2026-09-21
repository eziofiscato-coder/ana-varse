import streamlit as st
import pandas as pd
import os
from io import BytesIO
from datetime import date, datetime
import tempfile

st.set_page_config(page_title='ANA Varese', layout='wide')

VERDE = "#1A5D1A"
VERDE_LIGHT = "#2E8B57"
VERDE_BG = "#E8F5E9"

st.markdown(f"""
<style>
h1,h2,h3 {{ color: {VERDE}!important; }}
.stButton>button {{
    background-color: {VERDE}!important;
    color: white!important;
    border: 2px solid {VERDE}!important;
    font-weight: bold!important;
}}
.stButton>button:hover {{ background-color: {VERDE_LIGHT}!important; }}
[data-testid="stSidebar"] {{ background-color: {VERDE_BG}!important; }}
[data-testid="stMetricValue"] {{ color: {VERDE}!important; }}
</style>
""", unsafe_allow_html=True)

def hdr():
    st.markdown(
        f'<div style="background:{VERDE};padding:8px;'
        f'border-radius:8px;color:white;text-align:center;'
        f'font-weight:bold;">NUCLEO PROT CIVILE ANA VARESE '
        f'Squadra Alpini Caronno Pertusella Bariola</div>',
        unsafe_allow_html=True
    )

def to_excel(df):
    out = BytesIO()
    df2 = df[[c for c in df.columns if c not in ['Foto','FotoBytes','FileBytes']]]
    df2.to_excel(out, index=False, engine='openpyxl')
    return out.getvalue()

def genera_pdf(df, titolo):
    try:
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib import colors
        buf = BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=landscape(A4))
        styles = getSampleStyleSheet()
        story = []
        story.append(Paragraph(f"<b>{titolo}</b> - {datetime.now():%d/%m/%Y}", styles['Title']))
        story.append(Spacer(1,12))
        df2 = df[[c for c in df.columns if c not in ['Foto','FotoBytes','FileBytes']]].astype(str)
        data = [list(df2.columns)][:1] + df2.values.tolist()
        if len(data[0])>8:
            data = [r[:8] for r in data]
        t = Table(data)
        t.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0), colors.HexColor(VERDE)),
            ('TEXTCOLOR',(0,0),(-1,0), colors.white),
            ('GRID',(0,0),(-1,-1),0.5, colors.grey),
            ('FONTSIZE',(0,0),(-1,-1),7),
        ]))
        story.append(t)
        doc.build(story)
        return buf.getvalue()
    except:
        return None

def salva_icona_temp(fb, nome):
    try:
        p = os.path.join(tempfile.gettempdir(), f"icon_{nome}.png")
        with open(p,"wb") as f:
            f.write(fb)
        return p
    except:
        return None

for k in [
    'page','logged','menu','volontari','radio_db',
    'eventi','checkin','icone','postazioni',
    'last_clicked','temp_markers','brogliaccio',
    'mezzi','attrezzature','map_fullscreen','map_fullscreen2','mappa_tutto_schermo'
]:
    if k not in st.session_state:
        if k == 'page':
            st.session_state[k] = 'entra'
        elif k == 'logged':
            st.session_state[k] = False
        elif k == 'menu':
            st.session_state[k] = 'Dashboard'
        elif k in ['last_clicked']:
            st.session_state[k] = None
        elif k in ['temp_markers']:
            st.session_state[k] = []
        elif k in ['map_fullscreen','map_fullscreen2','mappa_tutto_schermo']:
            st.session_state[k] = False
        else:
            st.session_state[k] = []

# PRIMA PAGINA
if st.session_state.page == 'entra':
    hdr()
    c1,c2,c3 = st.columns([1,2,1])
    with c2:
        try:
            st.image('copertina.png', width=350)
        except:
            try:
                st.image('logo.png', width=200)
            except:
                pass
    st.markdown(f'<h2 style="text-align:center;color:{VERDE};">GESTIONALE<br>Prot Civile</h2>', unsafe_allow_html=True)
    st.divider()
    c1,c2,c3 = st.columns([1,1,1])
    with c2:
        if st.button('ENTRA', use_container_width=True, type='primary'):
            st.session_state.page = 'login'
            st.rerun()

elif st.session_state.page == 'login':
    hdr()
    c1,c2,c3 = st.columns([1,2,1])
    with c2:
        st.markdown(f'### <span style="color:{VERDE}">Login</span>', unsafe_allow_html=True)
        user = st.text_input('Utente')
        pwd = st.text_input('Password', type='password')
        a,b = st.columns(2)
        with a:
            if st.button('Indietro', use_container_width=True):
                st.session_state.page = 'entra'
                st.rerun()
        with b:
            if st.button('Accedi', use_container_width=True, type='primary'):
                if user == 'admin' and pwd == 'ana2024':
                    st.session_state.logged = True
                    st.session_state.page = 'dashboard'
                    st.rerun()
                else:
                    st.error('admin / ana2024')

elif st.session_state.page == 'dashboard':
    hdr()
    with st.sidebar:
        st.markdown(f'### <span style="color:{VERDE}">MENU</span>', unsafe_allow_html=True)
        menu = st.radio('Scegli:', ['Dashboard','Volontari','DB Radio','Brogliaccio','Eventi','Check-in','Mezzi','Attrezzature','Mappa Avanzata','Libreria Icone','Backup'], index=0)
        st.session_state.menu = menu
        st.divider()
        if st.button('Logout', use_container_width=True):
            st.session_state.logged = False
            st.session_state.page = 'entra'
            st.rerun()

    m = st.session_state.menu

    if m == 'Dashboard':
        st.markdown(f'## <span style="color:{VERDE}">Dashboard</span>', unsafe_allow_html=True)
        c1,c2,c3,c4 = st.columns(4)
        with c1: st.metric('Volontari', len(st.session_state.volontari))
        with c2: st.metric('Eventi', len(st.session_state.eventi))
        with c3: st.metric('Check-in', len(st.session_state.checkin))
        with c4: st.metric('Postazioni', len(st.session_state.postazioni))
        st.divider()
        st.markdown('### Menu Rapido Form')
        r1 = st.columns(4)
        with r1[0]:
            if st.button('VOLONTARI', use_container_width=True):
                st.session_state.menu = 'Volontari'
                st.rerun()
        with r1[1]:
            if st.button('RADIO', use_container_width=True):
                st.session_state.menu = 'DB Radio'
                st.rerun()
        with r1[2]:
            if st.button('MAPPA', use_container_width=True):
                st.session_state.menu = 'Mappa Avanzata'
                st.rerun()
        with r1[3]:
            if st.button('ICONE', use_container_width=True):
                st.session_state.menu = 'Libreria Icone'
                st.rerun()

    elif m == 'Volontari':
        st.markdown(f'## <span style="color:{VERDE}">Volontari</span>', unsafe_allow_html=True)
        t1,t2 = st.tabs(['Anagrafica Foto','Elenco'])
        with t1:
            with st.form('vol1'):
                nome = st.text_input('Nome *')
                comune = st.text_input('Comune *')
                foto = st.file_uploader('Foto', type=['png','jpg','jpeg'])
                if foto: st.image(foto, width=100)
                if st.form_submit_button('Salva', use_container_width=True, type='primary'):
                    if nome and comune:
                        fb = foto.getvalue() if foto else None
                        st.session_state.volontari.append({'Nome': nome, 'Comune': comune, 'Foto': fb})
                        st.success('Salvato')
        with t2:
            if st.session_state.volontari:
                df = pd.DataFrame([{'Nome': v['Nome'], 'Comune': v['Comune']} for v in st.session_state.volontari])
                st.dataframe(df, use_container_width=True)
                c1,c2 = st.columns(2)
                c1.download_button('Excel', to_excel(df), file_name='volontari.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', use_container_width=True)
                pdf = genera_pdf(df, 'Volontari')
                if pdf: c2.download_button('PDF', pdf, file_name='volontari.pdf', mime='application/pdf', use_container_width=True)

    elif m == 'DB Radio':
        st.markdown(f'## <span style="color:{VERDE}">DB Radio</span>', unsafe_allow_html=True)
        with st.form('radio'):
            modello = st.text_input('Modello *')
            matricola = st.text_input('Matricola *')
            tipo = st.selectbox('Tipo *', ['DMR','PMR446','TETRA','NAUTICHE','VHF','UHF','VHF/UHF','HF','CB','Altro'])
            if st.form_submit_button('Salva', use_container_width=True, type='primary'):
                if modello and matricola:
                    st.session_state.radio_db.append({'Modello': modello, 'Matricola': matricola, 'Tipo': tipo})
                    st.success('Salvata')
        if st.session_state.radio_db:
            df = pd.DataFrame(st.session_state.radio_db)
            st.dataframe(df, use_container_width=True)
            c1,c2 = st.columns(2)
            c1.download_button('Excel', to_excel(df), file_name='radio.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', use_container_width=True)
            pdf = genera_pdf(df, 'Radio')
            if pdf: c2.download_button('PDF', pdf, file_name='radio.pdf', mime='application/pdf', use_container_width=True)

    elif m == 'Eventi':
        st.markdown(f'## <span style="color:{VERDE}">Eventi</span>', unsafe_allow_html=True)
        with st.form('eventi'):
            nome_e = st.text_input('NOME EVENTO *')
            luogo = st.text_input('Luogo *')
            if st.form_submit_button('Crea', use_container_width=True, type='primary'):
                if nome_e and luogo:
                    st.session_state.eventi.append({'NomeEvento': nome_e, 'Luogo': luogo})
                    st.success('Creato')
        if st.session_state.eventi:
            df = pd.DataFrame(st.session_state.eventi)
            st.dataframe(df, use_container_width=True)
            c1,c2 = st.columns(2)
            c1.download_button('Excel', to_excel(df), file_name='eventi.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', use_container_width=True)
            pdf = genera_pdf(df, 'Eventi')
            if pdf: c2.download_button('PDF', pdf, file_name='eventi.pdf', mime='application/pdf', use_container_width=True)

    elif m == 'Check-in':
        st.markdown(f'## <span style="color:{VERDE}">Check-in Collegato Evento</span>', unsafe_allow_html=True)
        if st.session_state.eventi and st.session_state.volontari:
            ev_sel = st.selectbox('NOME EVENTO *', [e['NomeEvento'] for e in st.session_state.eventi])
            ev_det = next((e for e in st.session_state.eventi if e['NomeEvento'] == ev_sel), None)
            if ev_det: st.info(f"Evento: {ev_det.get('NomeEvento')} - Luogo: {ev_det.get('Luogo')}")
            with st.form('checkin'):
                vol = st.selectbox('Volontario *', [v['Nome'] for v in st.session_state.volontari])
                post = st.selectbox('Postazione', ['Base','Avanzata'] + [p['Nome'] for p in st.session_state.postazioni] if st.session_state.postazioni else ['Base','Avanzata'])
                if st.form_submit_button('Registra', use_container_width=True, type='primary'):
                    st.session_state.checkin.append({'NomeEvento': ev_sel, 'Volontario': vol, 'Postazione': post})
                    st.success('Registrato')
        if st.session_state.checkin:
            df = pd.DataFrame(st.session_state.checkin)
            st.dataframe(df, use_container_width=True)
            c1,c2 = st.columns(2)
            c1.download_button('Excel', to_excel(df), file_name='checkin.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', use_container_width=True)
            pdf = genera_pdf(df, 'Check-in')
            if pdf: c2.download_button('PDF', pdf, file_name='checkin.pdf', mime='application/pdf', use_container_width=True)

    elif m == 'Mappa Avanzata':
        # === ESPANSIONE A TUTTO SCHERMO DELLA MASCHERA MAPPA ===
        if st.session_state.mappa_tutto_schermo:
            st.markdown(f"""
            <style>
           .main {{ max-width: 100%!important; padding:0!important; }}
            [data-testid="stSidebar"] {{ display:none; }}
            header {{ display:none; }}
            </style>
            """, unsafe_allow_html=True)
            if st.button('❌ Chiudi Tutto Schermo', use_container_width=True):
                st.session_state.mappa_tutto_schermo = False
                st.rerun()

        st.markdown(f'## <span style="color:{VERDE}">Mappa Avanzata - Marker Icona Caricata</span>', unsafe_allow_html=True)

        col1,col2,col3,col4 = st.columns([2,2,2,2])
        with col1:
            map_type = st.selectbox('Tipo Mappa', ['OpenStreetMap','Google Map','Google Satellite','Google Hybrid','CartoDB Positron'], index=0)
        with col2:
            icona_sel = st.selectbox('Icona per Marker', ['Nessuna'] + [i['Nome'] for i in st.session_state.icone] if st.session_state.icone else ['Nessuna'])
        with col3:
            if st.button('⛶ Espandi Mappa 1', use_container_width=True):
                st.session_state.map_fullscreen = not st.session_state.map_fullscreen
                st.rerun()
        with col4:
            if st.button('🖥️ TUTTO SCHERMO MASCHERA', use_container_width=True, type='primary'):
                st.session_state.mappa_tutto_schermo = True
                st.rerun()

        h1 = 900 if st.session_state.mappa_tutto_schermo else (800 if st.session_state.map_fullscreen else 450)

        try:
            import folium
            from streamlit_folium import st_folium
            import requests
            def rev_geo(lat, lon):
                try:
                    url = f'https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=18&addressdetails=1'
                    r = requests.get(url, headers={'User-Agent':'ANA'}, timeout=5)
                    if r.status_code == 200:
                        d = r.json()
                        a = d.get('address',{})
                        c = a.get('city') or a.get('town') or a.get('village') or ''
                        v = a.get('road') or ''
                        return c, v
                except:
                    pass
                return '',''
            if st.session_state.postazioni:
                lat_c = sum([p['Lat'] for p in st.session_state.postazioni]) / len(st.session_state.postazioni)
                lon_c = sum([p['Log'] for p in st.session_state.postazioni]) / len(st.session_state.postazioni)
            else:
                lat_c, lon_c = 45.65, 8.79
            m = folium.Map(location=[lat_c, lon_c], zoom_start=12, tiles=None)
            if map_type == 'OpenStreetMap':
                folium.TileLayer('openstreetmap', name='OpenStreetMap').add_to(m)
            elif map_type == 'Google Map':
                folium.TileLayer(tiles='https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}', attr='Google').add_to(m)
            elif map_type == 'Google Satellite':
                folium.TileLayer(tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', attr='Google').add_to(m)
            elif map_type == 'Google Hybrid':
                folium.TileLayer(tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr='Google').add_to(m)
            else:
                folium.TileLayer('cartodbpositron').add_to(m)

            icon_path_sel = None
            if icona_sel!= 'Nessuna':
                ico_sel = next((i for i in st.session_state.icone if i['Nome']==icona_sel), None)
                if ico_sel and ico_sel.get('FileBytes'):
                    icon_path_sel = salva_icona_temp(ico_sel['FileBytes'], icona_sel)

            for p in st.session_state.postazioni:
                lat_f, lon_f = p['Lat'], p['Log']
                popup_html = f"<b>{p['Nome']}</b><br>{p.get('Comune','')} {p.get('Via','')}<br>Icona:{p.get('Icona','')}<br><a href='https://www.google.com/maps/search/?api=1&query={lat_f},{lon_f}' target='_blank'>Google</a> | <a href='https://waze.com/ul?ll={lat_f},{lon_f}&navigate=yes' target='_blank'>Waze</a> | <a href='https://earth.google.com/web/search/{lat_f},{lon_f}' target='_blank'>Earth</a>"
                p_icon = p.get('Icona','Nessuna')
                use_path = None
                if p_icon!= 'Nessuna':
                    ico = next((i for i in st.session_state.icone if i['Nome']==p_icon), None)
                    if ico and ico.get('FileBytes'):
                        use_path = salva_icona_temp(ico['FileBytes'], p_icon)
                if use_path:
                    try:
                        icon = folium.CustomIcon(use_path, icon_size=(40,40))
                        folium.Marker([lat_f, lon_f], popup=folium.Popup(popup_html, max_width=250), tooltip=p['Nome'], icon=icon).add_to(m)
                    except:
                        folium.Marker([lat_f, lon_f], popup=popup_html, icon=folium.Icon(color='green')).add_to(m)
                else:
                    folium.Marker([lat_f, lon_f], popup=folium.Popup(popup_html, max_width=250), icon=folium.Icon(color='green')).add_to(m)

            for tm in st.session_state.temp_markers:
                if icon_path_sel:
                    try:
                        icon = folium.CustomIcon(icon_path_sel, icon_size=(40,40))
                        folium.Marker([tm['lat'], tm['lon']], popup=f"TEMP {tm.get('icona','')}", icon=icon).add_to(m)
                    except:
                        folium.Marker([tm['lat'], tm['lon']], icon=folium.Icon(color='orange')).add_to(m)
                else:
                    folium.Marker([tm['lat'], tm['lon']], icon=folium.Icon(color='orange')).add_to(m)

            folium.LayerControl().add_to(m)
            out = st_folium(m, width=1400, height=h1, use_container_width=True, returned_objects=['last_clicked'])
            if out and out.get('last_clicked'):
                lat_c = out['last_clicked']['lat']
                lon_c = out['last_clicked']['lng']
                com, via = rev_geo(lat_c, lon_c)
                st.session_state.temp_markers.append({'lat': lat_c, 'lon': lon_c, 'icona': icona_sel, 'comune': com, 'via': via})
                st.session_state.last_clicked = {'lat': lat_c, 'lon': lon_c, 'icona': icona_sel, 'comune': com, 'via': via}
                st.success(f"Marker {icona_sel}: {lat_c:.5f} {lon_c:.5f} {com} {via}")
                st.rerun()
        except Exception as e:
            st.error(f"Errore mappa: {e}")

        last = st.session_state.last_clicked
        if last:
            st.info(f"Click: {last['lat']:.6f} {last['lon']:.6f} {last.get('comune','')} {last.get('via','')} Icona: {last.get('icona','')}")

        with st.form('form_post'):
            nome_p = st.text_input('Nome Postazione *')
            comune_p = st.text_input('Comune *', value=last.get('comune','') if last else '')
            via_p = st.text_input('Via *', value=last.get('via','') if last else '')
            c1,c2 = st.columns(2)
            with c1:
                lat_p = st.text_input('Lat *', value=str(last['lat']) if last else '')
            with c2:
                lon_p = st.text_input('Log *', value=str(last['lon']) if last else '')
            lista_icone = ['Nessuna'] + [i['Nome'] for i in st.session_state.icone] if st.session_state.icone else ['Nessuna']
            icona_def = last.get('icona','Nessuna') if last else 'Nessuna'
            idx_ico = lista_icone.index(icona_def) if icona_def in lista_icone else 0
            icona_p = st.selectbox('Icona Libreria', lista_icone, index=idx_ico)
            if icona_p!= 'Nessuna':
                ico_prev = next((i for i in st.session_state.icone if i['Nome']==icona_p), None)
                if ico_prev and ico_prev.get('FileBytes'):
                    st.image(ico_prev['FileBytes'], width=60, caption=f"Marker {icona_p}")
            if st.form_submit_button('Salva Postazione con Icona', use_container_width=True, type='primary'):
                if nome_p and comune_p and lat_p and lon_p:
                    try:
                        lat_v = float(lat_p.replace(',','.'))
                        lon_v = float(lon_p.replace(',','.'))
                        st.session_state.postazioni.append({'Nome': nome_p, 'Comune': comune_p, 'Via': via_p, 'Icona': icona_p, 'Lat': lat_v, 'Log': lon_v})
                        st.session_state.temp_markers = []
                        st.session_state.last_clicked = None
                        st.success('Salvata')
                        st.rerun()
                    except:
                        st.error('Lat/Log non validi')

        # MAPPA SOTTO MASCHERA CON TUTTE LE POSTAZIONI - DEFAULT OPENSTREETMAP
        st.divider()
        st.markdown(f"## <span style='color:{VERDE}'>Mappa Tutte le Postazioni - Default OpenStreetMap</span>", unsafe_allow_html=True)
        if st.button('⛶ Espandi / Riduci Mappa 2 - Tutte Postazioni', use_container_width=True):
            st.session_state.map_fullscreen2 = not st.session_state.map_fullscreen2
            st.rerun()
        h2 = 800 if st.session_state.map_fullscreen2 else 500

        if st.session_state.postazioni:
            df_post = pd.DataFrame(st.session_state.postazioni)
            st.dataframe(df_post, use_container_width=True)
            c1,c2 = st.columns(2)
            c1.download_button('Excel Postazioni', to_excel(df_post), file_name='postazioni.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', use_container_width=True)
            pdf = genera_pdf(df_post, 'Postazioni')
            if pdf: c2.download_button('PDF Postazioni', pdf, file_name='postazioni.pdf', mime='application/pdf', use_container_width=True)
            try:
                import folium
                from streamlit_folium import st_folium
                lat_m = df_post.Lat.mean()
                lon_m = df_post.Log.mean()
                # DEFAULT OPENSTREETMAP come richiesto
                m2 = folium.Map(location=[lat_m, lon_m], zoom_start=11, tiles='openstreetmap')
                # Aggiungi anche altri layer ma default e OSM
                folium.TileLayer(tiles='https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}', attr='Google', name='Google Map').add_to(m2)
                folium.TileLayer(tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', attr='Google', name='Google Satellite').add_to(m2)
                for p in st.session_state.postazioni:
                    lat_f, lon_f = p['Lat'], p['Log']
                    p_icon = p.get('Icona','Nessuna')
                    use_path = None
                    if p_icon!= 'Nessuna':
                        ico = next((i for i in st.session_state.icone if i['Nome']==p_icon), None)
                        if ico and ico.get('FileBytes'):
                            use_path = salva_icona_temp(ico['FileBytes'], p_icon)
                    popup_html = f"<b>{p['Nome']}</b><br>{p.get('Comune','')}<br><a href='https://www.google.com/maps/search/?api=1&query={lat_f},{lon_f}' target='_blank'>Google</a> | <a href='https://waze.com/ul?ll={lat_f},{lon_f}&navigate=yes' target='_blank'>Waze</a> | <a href='https://earth.google.com/web/search/{lat_f},{lon_f}' target='_blank'>Earth</a>"
                    if use_path:
                        try:
                            icon = folium.CustomIcon(use_path, icon_size=(40,40))
                            folium.Marker([lat_f, lon_f], popup=popup_html, icon=icon).add_to(m2)
                        except:
                            folium.Marker([lat_f, lon_f], icon=folium.Icon(color='green')).add_to