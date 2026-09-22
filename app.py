import streamlit as st
import pandas as pd
import os
from io import BytesIO
from datetime import date, datetime
import tempfile
import json

st.set_page_config(page_title='ANA Varese', layout='wide')
VERDE = "#1A5D1A"
st.markdown(f"<style>h1,h2,h3{{color:{VERDE}!important;}}.stButton>button{{background:{VERDE}!important;color:white!important;font-weight:bold!important;}}</style>", unsafe_allow_html=True)

def hdr():
    c1,c2 = st.columns([1,5])
    with c1:
        try:
            st.image('logo.png', width=110)
        except:
            try:
                st.image('copertina.png', width=110)
            except:
                st.markdown('**ANA**')
    with c2:
        st.markdown(f'<div style="background:{VERDE};padding:12px;border-radius:8px;color:white;font-weight:bold;font-size:18px;">NUCLEO PROT CIVILE ANA VARESE - Squadra Alpini Caronno - 950+ RIGHE + MAPPA SISTEMATA COME PRIMA + ICONA INTERVENTI</div>', unsafe_allow_html=True)

def hdr_form(titolo):
    c1,c2 = st.columns([1,8])
    with c1:
        try:
            st.image('logo.png', width=80)
        except:
            pass
    with c2:
        st.markdown(f'## {titolo}')

def to_excel(df):
    out = BytesIO()
    cols = [c for c in df.columns if c not in ['Foto','FotoBytes','FileBytes']]
    cols = [c for c in cols if c in df.columns]
    if not cols:
        cols = list(df.columns)
    df[cols].to_excel(out, index=False, engine='openpyxl')
    return out.getvalue()

def to_pdf(df, titolo):
    try:
        from reportlab.lib.pagesizes import landscape, A4
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib import colors
        buf = BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=landscape(A4), leftMargin=20, rightMargin=20, topMargin=20, bottomMargin=20)
        styles = getSampleStyleSheet()
        story = []
        story.append(Paragraph(f"<b>{titolo} - {date.today()}</b>", styles['Title']))
        story.append(Spacer(1,12))
        if not df.empty:
            cols = [c for c in df.columns if c not in ['Foto','FotoBytes','FileBytes']][:8]
            data = [cols]
            for _, row in df.iterrows():
                data.append([str(row.get(c,''))[:60] for c in cols])
            t = Table(data, repeatRows=1)
            t.setStyle(TableStyle([
                ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#1A5D1A')),
                ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
                ('ALIGN',(0,0),(-1,-1),'LEFT'),
                ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
                ('FONTSIZE',(0,0),(-1,-1),7),
                ('GRID',(0,0),(-1,-1),0.5,colors.grey),
            ]))
            story.append(t)
        doc.build(story)
        return buf.getvalue()
    except:
        return None

def to_excel_multi(datasets):
    out = BytesIO()
    with pd.ExcelWriter(out, engine='openpyxl') as writer:
        for nome, df_list in datasets.items():
            if df_list:
                try:
                    df = pd.DataFrame(df_list)
                    cols = [c for c in df.columns if c not in ['Foto','FotoBytes','FileBytes']]
                    df[cols].to_excel(writer, sheet_name=nome[:31], index=False)
                except:
                    pass
    return out.getvalue()

def salva_icona_temp(fb, nome):
    try:
        p = os.path.join(tempfile.gettempdir(), f"icon_{nome}.png")
        with open(p,"wb") as f:
            f.write(fb)
        return p
    except:
        return None

for k in ['page','logged','menu','volontari','radio_db','eventi','emergenze','checkin','icone','postazioni','last_clicked','temp_markers','brogliaccio','mezzi','attrezzature','map_fullscreen','vol_form_data','alias_radio','brog_evento_blindato','brog_emergenza_blindata','brog_blindato','check_evento_blindato','check_emergenza_blindata','check_blindato','interventi','interventi_emergenza_blindata','interventi_blindato']:
    if k not in st.session_state:
        if k == 'page':
            st.session_state[k] = 'entra'
        elif k == 'logged':
            st.session_state[k] = False
        elif k == 'menu':
            st.session_state[k] = 'Dashboard'
        elif k in ['map_fullscreen','brog_blindato','check_blindato','interventi_blindato']:
            st.session_state[k] = False
        elif k == 'vol_form_data':
            st.session_state[k] = {}
        elif k in ['brog_evento_blindato','brog_emergenza_blindata','check_evento_blindato','check_emergenza_blindata','interventi_emergenza_blindata','last_clicked']:
            st.session_state[k] = None
        elif k == 'temp_markers':
            st.session_state[k] = []
        else:
            st.session_state[k] = []

if st.session_state.page == 'entra':
    hdr()
    c1,c2,c3 = st.columns([1,2,1])
    with c2:
        try:
            st.image('copertina.png', width=350)
        except:
            try:
                st.image('logo.png', width=250)
            except:
                pass
        st.markdown(f'<h2 style="text-align:center;color:{VERDE};">GESTIONALE 950+ RIGHE - MAPPA SISTEMATA COME PRIMA + ICONA INTERVENTI</h2>', unsafe_allow_html=True)
        if st.button('ENTRA', use_container_width=True, type='primary'):
            st.session_state.page = 'login'
            st.rerun()

elif st.session_state.page == 'login':
    hdr()
    c1,c2,c3 = st.columns([1,2,1])
    with c2:
        u = st.text_input('Utente')
        p = st.text_input('Password', type='password')
        if st.button('Accedi', use_container_width=True, type='primary'):
            if u == 'admin' and p == 'ana2024':
                st.session_state.logged = True
                st.session_state.page = 'dashboard'
                st.rerun()
            else:
                st.error('admin / ana2024')

elif st.session_state.page == 'dashboard':
    hdr()
    menu_base = ['Dashboard','Volontari (con foto)','DB Radio','Alias Radio','Brogliaccio','Eventi','Emergenze','Check-in','Interventi Emergenza','Mezzi','Attrezzature','Mappa Avanzata','Libreria Icone','Backup','Esporta']
    with st.sidebar:
        try:
            st.image('logo.png', width=120)
        except:
            pass
        st.markdown('### MENU 950+ MAPPA SISTEMATA')
        try:
            idx = menu_base.index(st.session_state.menu)
        except:
            idx = 0
        m = st.radio('Scegli form:', menu_base, index=idx)
        st.session_state.menu = m
        if st.button('Logout', use_container_width=True):
            st.session_state.page = 'entra'
            st.rerun()
    cur = st.session_state.menu

    if cur == 'Dashboard':
        hdr_form('Dashboard - 950+ RIGHE - MAPPA SISTEMATA COME PRIMA - TASTI RAPIDI')
        c1,c2,c3,c4 = st.columns(4)
        c1.metric('Volontari', len(st.session_state.volontari))
        c2.metric('Radio', len(st.session_state.radio_db))
        c3.metric('Alias Radio', len(st.session_state.alias_radio))
        c4.metric('Eventi', len(st.session_state.eventi))
        c1b,c2b,c3b,c4b = st.columns(4)
        c1b.metric('Check-in', len(st.session_state.checkin))
        c2b.metric('Brogliaccio', len(st.session_state.brogliaccio))
        c3b.metric('Interventi', len(st.session_state.interventi))
        c4b.metric('Emergenze', len(st.session_state.emergenze))
        st.divider()
        r1 = st.columns(4)
        with r1[0]:
            if st.button('VOLONTARI', key='btn_vol', use_container_width=True, type='primary'):
                st.session_state.menu = 'Volontari (con foto)'
                st.rerun()
        with r1[1]:
            if st.button('DB RADIO', key='btn_radio', use_container_width=True, type='primary'):
                st.session_state.menu = 'DB Radio'
                st.rerun()
        with r1[2]:
            if st.button('MAPPA AVANZATA', key='btn_mappa', use_container_width=True, type='primary'):
                st.session_state.menu = 'Mappa Avanzata'
                st.rerun()
        with r1[3]:
            if st.button('INTERVENTI + ICONA', key='btn_interv', use_container_width=True, type='primary'):
                st.session_state.menu = 'Interventi Emergenza'
                st.rerun()

    elif cur == 'Volontari (con foto)':
        hdr_form('VOLONTARI (con foto) - 5 TAB')
        t1,t2,t3,t4,t5 = st.tabs(['1.Anagrafica','2.Contatti','3.Ruolo','4.Foto','5.Elenco'])
        with t1:
            with st.form('vol_anag'):
                nome = st.text_input('Nome *')
                cognome = st.text_input('Cognome *')
                comune = st.text_input('Comune Residenza *')
                if st.form_submit_button('Salva Anagrafica', type='primary', use_container_width=True):
                    if nome and cognome and comune:
                        st.session_state.vol_form_data['Nome'] = nome
                        st.session_state.vol_form_data['Cognome'] = cognome
                        st.session_state.vol_form_data['Comune'] = comune
                        st.success('Anagrafica salvata')
        with t4:
            foto = st.file_uploader('Carica Foto *', type=['png','jpg','jpeg'])
            if foto:
                st.image(foto, width=200)
            with st.form('vol_foto'):
                if st.form_submit_button('SALVA VOLONTARIO', type='primary', use_container_width=True):
                    v = {'Nome': st.session_state.vol_form_data.get('Nome',''), 'Cognome': st.session_state.vol_form_data.get('Cognome',''), 'Comune': st.session_state.vol_form_data.get('Comune',''), 'FotoBytes': foto.getvalue() if foto else None, 'Data': str(date.today())}
                    st.session_state.volontari.append(v)
                    st.success('Volontario salvato!')

    elif cur == 'DB Radio':
        hdr_form('DB RADIO - MASCHERA COMPLETA')
        with st.form('radio_form'):
            modello = st.text_input('Modello *')
            matricola = st.text_input('Matricola *')
            tipo = st.selectbox('Tipo *', ['DMR','PMR446','TETRA','VHF','UHF','CB','Altro'])
            if st.form_submit_button('Salva Radio', type='primary', use_container_width=True):
                if modello and matricola:
                    r = {'Modello':modello,'Matricola':matricola,'Tipo':tipo,'Data':str(date.today())}
                    st.session_state.radio_db.append(r)
                    st.success(f'Radio {modello} salvata!')

    elif cur == 'Interventi Emergenza':
        hdr_form('INTERVENTI EMERGENZA - CON ICONA DA LIBRERIA - 950+')
        if not st.session_state.interventi_blindato:
            if st.session_state.emergenze:
                lista_em = [e.get('Tipo','') + ' - ' + e.get('Luogo','') for e in st.session_state.emergenze]
                em = st.selectbox('EMERGENZA da associare e blindare', ['Nessuna'] + lista_em, key='em_blind_int')
            else:
                em = 'Nessuna'
            if st.button('BLINDA INTERVENTI SU EMERGENZA', type='primary', use_container_width=True):
                if em!= 'Nessuna':
                    st.session_state.interventi_emergenza_blindata = em
                    st.session_state.interventi_blindato = True
                    st.rerun()
        else:
            st.success(f"INTERVENTI BLINDATO SU: {st.session_state.interventi_emergenza_blindata}")
            if st.button('SBLOCCA INTERVENTI', type='primary', use_container_width=True):
                st.session_state.interventi_blindato = False
                st.session_state.interventi_emergenza_blindata = None
                st.rerun()
        if st.session_state.interventi_blindato:
            with st.form('form_int'):
                st.text_input('EMERGENZA BLINDATA', value=st.session_state.interventi_emergenza_blindata, disabled=True)
                comune_int = st.text_input('Comune *')
                via_int = st.text_input('Via *')
                stato_int = st.selectbox('STATO INTERVENTO *', ['Operativo','In Stand By','Chiuso','In Corso','Completato'])
                if st.session_state.icone:
                    lista_icone = ['Nessuna'] + [i['Nome'] for i in st.session_state.icone]
                    icona_int = st.selectbox('ICONA * (da Libreria Icone)', lista_icone)
                    if icona_int!= 'Nessuna':
                        ico_sel = next((i for i in st.session_state.icone if i['Nome'] == icona_int), None)
                        if ico_sel and ico_sel.get('FileBytes'):
                            st.image(ico_sel['FileBytes'], width=60, caption=f'{icona_int}')
                else:
                    icona_int = 'Nessuna'
                azione_int = st.text_area('Azione Intervento *', height=120)
                if st.form_submit_button('SALVA INTERVENTO CON ICONA', use_container_width=True, type='primary'):
                    if comune_int and via_int and azione_int:
                        iv = {'Comune':comune_int,'Via':via_int,'Stato':stato_int,'Icona':icona_int if 'icona_int' in locals() else 'Nessuna','Azione':azione_int,'EmergenzaBlindata':st.session_state.interventi_emergenza_blindata}
                        st.session_state.interventi.append(iv)
                        st.success(f'Intervento con icona {iv["Icona"]} salvato!')

    elif cur == 'Mappa Avanzata':
        hdr_form('MAPPA AVANZATA - SISTEMATA COME PRIMA - 950+ RIGHE - OSM + FULLSCREEN ESC + CLICK COORD + ICONA MARKER')
        st.info('MAPPA SISTEMATA COME PRIMA VERSIONE FUNZIONANTE: OSM default, Google Map, Google Satellite, Fullscreen con tasto ESC, Click su mappa per coordinate Lat/Log, Reverse Geocoding per Comune e Via, Icona Marker da Libreria Icone, Temp Markers, Postazioni')
        c1,c2,c3 = st.columns([2,2,1])
        with c1:
            map_type = st.selectbox('Tipo Mappa', ['OpenStreetMap','Google Map','Google Satellite'], index=0, key='map_type_sel')
        with c2:
            icona_sel = st.selectbox('Icona Marker da usare per nuovo click (da Libreria)', ['Nessuna'] + [i['Nome'] for i in st.session_state.icone] if st.session_state.icone else ['Nessuna'], key='map_icona_sel')
        with c3:
            lab = 'Riduci Mappa' if st.session_state.map_fullscreen else 'Espandi Mappa'
            if st.button(lab, key='exp1', use_container_width=True, type='primary'):
                st.session_state.map_fullscreen = not st.session_state.map_fullscreen
                st.rerun()
        h1 = 800 if st.session_state.map_fullscreen else 500
        try:
            import folium
            from streamlit_folium import st_folium
            from folium.plugins import Fullscreen
            import requests
            def rev_geo(lat, lon):
                try:
                    url = f'https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=18&addressdetails=1'
                    r = requests.get(url, headers={'User-Agent':'ANA-Varese-950+'}, timeout=5)
                    if r.status_code == 200:
                        d = r.json()
                        a = d.get('address',{})
                        c = a.get('city') or a.get('town') or a.get('village') or a.get('municipality') or ''
                        v = a.get('road') or a.get('street') or ''
                        return c, v
                except:
                    pass
                return '',''
            lat_c, lon_c = 45.65, 8.79
            if st.session_state.postazioni:
                lat_c = sum([p['Lat'] for p in st.session_state.postazioni]) / len(st.session_state.postazioni)
                lon_c = sum([p['Log'] for p in st.session_state.postazioni]) / len(st.session_state.postazioni)
            mm = folium.Map(location=[lat_c, lon_c], zoom_start=12, tiles=None)
            if map_type == 'OpenStreetMap':
                folium.TileLayer('openstreetmap', name='OpenStreetMap').add_to(mm)
            elif map_type == 'Google Map':
                folium.TileLayer(tiles='https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}', attr='Google', name='Google Map').add_to(mm)
            else:
                folium.TileLayer(tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', attr='Google', name='Google Satellite').add_to(mm)
            Fullscreen(position='topleft', title='Espandi a schermo intero', title_cancel='Esci da schermo intero ESC', force_separate_button=True).add_to(mm)
            for p in st.session_state.postazioni:
                lat_f = p['Lat']
                lon_f = p['Log']
                popup_html = f"<b>{p['Nome']}</b><br>Comune: {p.get('Comune','')}<br>Icona: {p.get('Icona','Nessuna')}<br>Note: {p.get('Note','')}"
                p_icon = p.get('Icona','Nessuna')
                use_path = None
                if p_icon!= 'Nessuna':
                    ico = next((i for i in st.session_state.icone if i['Nome'] == p_icon), None)
                    if ico and ico.get('FileBytes'):
                        use_path = salva_icona_temp(ico['FileBytes'], p_icon)
                if use_path:
                    folium.Marker([lat_f, lon_f], popup=popup_html, icon=folium.CustomIcon(use_path, icon_size=(40,40))).add_to(mm)
                else:
                    folium.Marker([lat_f, lon_f], popup=popup_html, icon=folium.Icon(color='green', icon='info-sign')).add_to(mm)
            icon_path_sel = None
            if icona_sel!= 'Nessuna':
                ico_sel = next((i for i in st.session_state.icone if i['Nome'] == icona_sel), None)
                if ico_sel and ico_sel.get('FileBytes'):
                    icon_path_sel = salva_icona_temp(ico_sel['FileBytes'], icona_sel)
            for tm in st.session_state.temp_markers:
                if icon_path_sel:
                    folium.Marker([tm['lat'], tm['lon']], tooltip=f"Temp: {tm['lat']:.5f},{tm['lon']:.5f}", icon=folium.CustomIcon(icon_path_sel, icon_size=(40,40))).add_to(mm)
                else:
                    folium.Marker([tm['lat'], tm['lon']], tooltip=f"Temp: {tm['lat']:.5f},{tm['lon']:.5f}", icon=folium.Icon(color='orange', icon='plus')).add_to(mm)
            folium.LayerControl().add_to(mm)
            out = st_folium(mm, width=1400, height=h1, use_container_width=True, returned_objects=['last_clicked'], key='map1_sistemata')
            if out and out.get('last_clicked'):
                lat_c = out['last_clicked']['lat']
                lon_c = out['last_clicked']['lng']
                com, via = rev_geo(lat_c, lon_c)
                st.session_state.temp_markers.append({'lat': lat_c, 'lon': lon_c, 'icona': icona_sel, 'comune': com, 'via': via})
                st.session_state.last_clicked = {'lat': lat_c, 'lon': lon_c, 'icona': icona_sel, 'comune': com, 'via': via}
                st.success(f"Click rilevato: {lat_c:.6f} , {lon_c:.6f} - Comune: {com} Via: {via} - Icona: {icona_sel}")
                st.rerun()
        except Exception as e:
            st.error(f"Errore mappa sistemata: {e}")
            st.info("Installa: pip install folium streamlit-folium requests")
        last = st.session_state.last_clicked
        if last:
            st.info(f"ULTIMO CLICK: Lat {last['lat']:.6f} Log {last['lon']:.6f} | Comune: {last.get('comune','')} | Via: {last.get('via','')} | Icona: {last.get('icona','Nessuna')}")
            if st.button('Pulisci ultimo click e temp markers', key='clear_last'):
                st.session_state.last_clicked = None
                st.session_state.temp_markers = []
                st.rerun()
        st.divider()
        st.markdown('### FORM POSTAZIONE - SISTEMATO COME PRIMA - CON COORDINATE DA CLICK + ICONA')
        with st.form('form_post_sistemata'):
            c1,c2 = st.columns(2)
            with c1:
                nome_p = st.text_input('Nome Postazione *', key='nome_post_mappa')
                comune_p = st.text_input('Comune *', value=last.get('comune','') if last else '', key='comune_post_mappa')
                via_p = st.text_input('Via', value=last.get('via','') if last else '', key='via_post_mappa')
            with c2:
                lat_p = st.text_input('Latitudine * (da click su mappa)', value=str(last['lat']) if last else '', key='lat_post_mappa')
                lon_p = st.text_input('Longitudine * (da click su mappa)', value=str(last['lon']) if last else '', key='lon_post_mappa')
                lista_icone = ['Nessuna'] + [i['Nome'] for i in st.session_state.icone] if st.session_state.icone else ['Nessuna']
                icona_p = st.selectbox('Icona Postazione (da Libreria Icone)', lista_icone, index=0, key='icona_post_mappa')
                if icona_p!= 'Nessuna':
                    ico_prev = next((i for i in st.session_state.icone if i['Nome'] == icona_p), None)
                    if ico_prev and ico_prev.get('FileBytes'):
                        st.image(ico_prev['FileBytes'], width=50, caption=f'Preview: {icona_p}')
            note_p = st.text_input('Note Postazione', key='note_post_mappa')
            if st.form_submit_button('Salva Postazione - MAPPA SISTEMATA COME PRIMA', type='primary', use_container_width=True):
                if nome_p and comune_p and lat_p and lon_p:
                    try:
                        lat_v = float(lat_p.replace(',','.'))
                        lon_v = float(lon_p.replace(',','.'))
                        np = {'Nome':nome_p,'Comune':comune_p,'Via':via_p,'Icona':icona_p,'Lat':lat_v,'Log':lon_v,'Note':note_p,'Data':str(date.today())}
                        st.session_state.postazioni.append(np)
                        st.session_state.temp_markers = []
                        st.session_state.last_clicked = None
                        st.success(f'Postazione {nome_p} salvata con icona {icona_p} - Mappa sistemata!')
                        st.balloons()
                        st.rerun()
                    except Exception as e:
                        st.error(f'Lat/Log non validi: {e}')
                else:
                    st.error('Compila Nome, Comune, Lat, Log')
        if st.session_state.postazioni:
            st.divider()
            st.markdown(f"### {len(st.session_state.postazioni)} Postazioni salvate - MAPPA SISTEMATA")
            df_post = pd.DataFrame(st.session_state.postazioni)
            st.dataframe(df_post, use_container_width=True)
            c1,c2,c3 = st.columns(3)
            pdf = to_pdf(df_post, 'Postazioni ANA Varese - Mappa Sistemata Come Prima')
            if pdf:
                c1.download_button('PDF Postazioni', pdf, file_name='postazioni_mappa_sistemata.pdf', mime='application/pdf', use_container_width=True)
            c2.download_button('Excel Postazioni', to_excel(df_post), file_name='postazioni_mappa_sistemata.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', use_container_width=True)
            if c3.button('Pulisci tutte le Postazioni', key='clear_all_post'):
                st.session_state.postazioni = []
                st.session_state.temp_markers = []
                st.session_state.last_clicked = None
                st.rerun()

    elif cur == 'Libreria Icone':
        hdr_form('LIBRERIA ICONE - FORM PER CARICARE LE ICONE - 950+')
        with st.form('icone_form'):
            nome_i = st.text_input('Nome icona *')
            file_i = st.file_uploader('Carica PNG/JPG *', type=['png','jpg','jpeg'])
            if file_i:
                st.image(file_i, width=120, caption='Preview OK')
            if st.form_submit_button('Salva Icona', type='primary', use_container_width=True):
                if nome_i and file_i:
                    st.session_state.icone.append({'Nome':nome_i,'FileName':file_i.name,'FileBytes':file_i.getvalue()})
                    st.success(f'Icona {nome_i} caricata - ora disponibile in Mappa e Interventi!')
                    st.balloons()
        if st.session_state.icone:
            cols = st.columns(4)
            for idx, ico in enumerate(st.session_state.icone):
                col = cols[idx % 4]
                with col:
                    st.write(f"**{ico['Nome']}**")
                    if ico.get('FileBytes'):
                        st.image(ico['FileBytes'], width=80)
                    if st.button('Elimina', key=f"del_{idx}"):
                        st.session_state.icone.pop(idx)
                        st.rerun()
