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
  background:{VERDE}!important;
  color:white!important;
  font-weight:bold!important;
  border:2px solid {VERDE}!important;
}}
[data-testid="stSidebar"] {{ background:{VERDE_BG}!important; }}
</style>
""", unsafe_allow_html=True)

def hdr():
    st.markdown(f'<div style="background:{VERDE};padding:10px;border-radius:8px;color:white;text-align:center;font-weight:bold;">NUCLEO PROT CIVILE ANA VARESE - Squadra Alpini Caronno</div>', unsafe_allow_html=True)

def to_excel(df):
    out = BytesIO()
    cols = [c for c in df.columns if c not in ['Foto','FotoBytes','DocBytes','FileBytes']]
    df[cols].to_excel(out, index=False, engine='openpyxl')
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
        story.append(Paragraph(f"<b>{titolo}</b> {datetime.now():%d/%m/%Y}", styles['Title']))
        story.append(Spacer(1,12))
        cols = [c for c in df.columns if c not in ['Foto','FotoBytes','DocBytes','FileBytes']]
        df2 = df[cols].astype(str)
        data = [list(df2.columns)] + df2.values.tolist()
        if len(data[0]) > 8:
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

for k in ['page','logged','menu','volontari','radio_db','eventi','emergenze','checkin','icone','postazioni','last_clicked','temp_markers','brogliaccio','mezzi','attrezzature','map_fullscreen','map_fullscreen2','vol_form_data']:
    if k not in st.session_state:
        if k == 'page': st.session_state[k] = 'entra'
        elif k == 'logged': st.session_state[k] = False
        elif k == 'menu': st.session_state[k] = 'Dashboard'
        elif k == 'last_clicked': st.session_state[k] = None
        elif k == 'temp_markers': st.session_state[k] = []
        elif k in ['map_fullscreen','map_fullscreen2']: st.session_state[k] = False
        elif k == 'vol_form_data': st.session_state[k] = {}
        else: st.session_state[k] = []

if st.session_state.page == 'entra':
    hdr()
    c1,c2,c3 = st.columns([1,2,1])
    with c2:
        try: st.image('copertina.png', width=350)
        except:
            try: st.image('logo.png', width=200)
            except: pass
    st.markdown(f'<h2 style="text-align:center;color:{VERDE};">GESTIONALE PROT CIVILE</h2>', unsafe_allow_html=True)
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
        user = st.text_input('Utente')
        pwd = st.text_input('Password', type='password')
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
        st.markdown(f'### MENU - TUTTI I FORM CON MASCHERE')
        menu = st.radio('Scegli:', ['Dashboard','Volontari (con foto)','DB Radio','Brogliaccio','Eventi','Emergenze','Check-in','Mezzi','Attrezzature','Mappa Avanzata','Libreria Icone','Backup','Esporta'], index=0)
        st.session_state.menu = menu
        st.divider()
        if st.button('Logout', use_container_width=True):
            st.session_state.page = 'entra'
            st.rerun()

    m = st.session_state.menu

    if m == 'Dashboard':
        st.markdown('## Dashboard - TUTTI I FORM CON MASCHERE INSERIMENTO')
        c1,c2,c3,c4 = st.columns(4)
        c1.metric('Volontari', len(st.session_state.volontari))
        c2.metric('Radio', len(st.session_state.radio_db))
        c3.metric('Eventi', len(st.session_state.eventi))
        c4.metric('Emergenze', len(st.session_state.emergenze))
        c1,c2,c3,c4 = st.columns(4)
        c1.metric('Check-in', len(st.session_state.checkin))
        c2.metric('Mezzi', len(st.session_state.mezzi))
        c3.metric('Attrezzature', len(st.session_state.attrezzature))
        c4.metric('Postazioni', len(st.session_state.postazioni))
        st.divider()
        st.markdown('### TUTTI I FORM HANNO ORA MASCHERA INSERIMENTO')
        st.success('Ogni form sotto ha la sua maschera con campi * e tasto Salva')

    elif m == 'Volontari (con foto)':
        st.markdown('## VOLONTARI - MASCHERA CON 5 SOTTOMASCHERE + FOTO')
        tab1, tab2, tab3, tab4, tab5 = st.tabs(['1. Anagrafica','2. Contatti','3. Ruolo','4. Foto','5. Elenco'])
        with tab1:
            with st.form('vol_anag'):
                c1,c2 = st.columns(2)
                with c1:
                    nome = st.text_input('Nome *')
                    cognome = st.text_input('Cognome *')
                    cf = st.text_input('Codice Fiscale')
                with c2:
                    comune = st.text_input('Comune Residenza *')
                    data_nasc = st.date_input('Data Nascita', value=date(1980,1,1))
                if st.form_submit_button('Salva Anagrafica', type='primary', use_container_width=True):
                    if nome and cognome and comune:
                        st.session_state.vol_form_data.update({'Nome': nome, 'Cognome': cognome, 'CF': cf, 'Comune': comune, 'DataNascita': str(data_nasc)})
                        st.success('Anagrafica salvata')
        with tab2:
            with st.form('vol_cont'):
                cellulare = st.text_input('Cellulare *')
                email = st.text_input('Email')
                contatto_em = st.text_input('Contatto Emergenza')
                if st.form_submit_button('Salva Contatti', type='primary', use_container_width=True):
                    if cellulare:
                        st.session_state.vol_form_data.update({'Cellulare': cellulare, 'Email': email, 'ContattoEm': contatto_em})
                        st.success('Contatti salvati')
        with tab3:
            with st.form('vol_ruolo'):
                ruolo = st.selectbox('Ruolo *', ['Volontario','Caposquadra','Coordinatore','Autista','Radio','Logistica','Sanitario','Altro'])
                squadra = st.selectbox('Squadra', ['Alpini Caronno','Squadra A','B','C'])
                spec = st.multiselect('Specializzazioni', ['AIB','Idro','Neve','Cinofilo','Motosega','Radio'])
                if st.form_submit_button('Salva Ruolo', type='primary', use_container_width=True):
                    st.session_state.vol_form_data.update({'Ruolo': ruolo, 'Squadra': squadra, 'Specializzazioni': ','.join(spec)})
                    st.success('Ruolo salvato')
        with tab4:
            c1,c2 = st.columns([1,2])
            with c1:
                foto_file = st.file_uploader('Carica Foto *', type=['png','jpg','jpeg'])
                if foto_file:
                    st.image(foto_file, width=200, caption='Preview OK')
            with c2:
                with st.form('vol_foto'):
                    scadenza_doc = st.date_input('Scadenza Documento', value=date.today())
                    if st.form_submit_button('SALVA VOLONTARIO COMPLETO', type='primary', use_container_width=True):
                        if not st.session_state.vol_form_data.get('Nome'):
                            st.error('Compila Anagrafica, Contatti, Ruolo')
                        else:
                            fb = foto_file.getvalue() if foto_file else None
                            vol = {
                                'Nome': st.session_state.vol_form_data.get('Nome',''),
                                'Cognome': st.session_state.vol_form_data.get('Cognome',''),
                                'Comune': st.session_state.vol_form_data.get('Comune',''),
                                'Cellulare': st.session_state.vol_form_data.get('Cellulare',''),
                                'Ruolo': st.session_state.vol_form_data.get('Ruolo',''),
                                'Squadra': st.session_state.vol_form_data.get('Squadra',''),
                                'Specializzazioni': st.session_state.vol_form_data.get('Specializzazioni',''),
                                'FotoBytes': fb,
                                'ScadenzaDoc': str(scadenza_doc)
                            }
                            st.session_state.volontari.append(vol)
                            st.session_state.vol_form_data = {}
                            st.success(f"Volontario {vol['Nome']} salvato!")
                            st.balloons()
            if foto_file:
                st.session_state.vol_form_data['FotoBytes'] = foto_file.getvalue()
        with tab5:
            if st.session_state.volontari:
                df = pd.DataFrame([{'Nome': v['Nome'], 'Cognome': v['Cognome'], 'Comune': v['Comune'], 'Ruolo': v['Ruolo'], 'Foto': 'SI' if v.get('FotoBytes') else 'NO'} for v in st.session_state.volontari])
                st.dataframe(df, use_container_width=True)
                cols = st.columns(4)
                for idx, v in enumerate(st.session_state.volontari):
                    col = cols[idx % 4]
                    with col:
                        st.write(f"**{v['Nome']} {v['Cognome']}**")
                        if v.get('FotoBytes'):
                            st.image(v['FotoBytes'], width=100)
                st.download_button('Excel', to_excel(pd.DataFrame(st.session_state.volontari)), file_name='volontari.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    elif m == 'DB Radio':
        st.markdown('## DB Radio - MASCHERA INSERIMENTO')
        with st.form('radio_form'):
            st.markdown('### Inserisci Radio')
            c1,c2 = st.columns(2)
            with c1:
                modello = st.text_input('Modello *')
                matricola = st.text_input('Matricola *')
                tipo = st.selectbox('Tipo *', ['DMR','PMR446','TETRA','VHF','UHF','CB','Altro'])
            with c2:
                frequenza = st.text_input('Frequenza')
                canale = st.text_input('Canale')
                stato_r = st.selectbox('Stato', ['Disponibile','In Uso','Manutenzione','Guasta'])
            note_r = st.text_area('Note')
            if st.form_submit_button('Salva Radio', type='primary', use_container_width=True):
                if modello and matricola:
                    st.session_state.radio_db.append({'Modello': modello, 'Matricola': matricola, 'Tipo': tipo, 'Frequenza': frequenza, 'Canale': canale, 'Stato': stato_r, 'Note': note_r})
                    st.success('Radio salvata')
        if st.session_state.radio_db:
            st.dataframe(pd.DataFrame(st.session_state.radio_db), use_container_width=True)
            st.download_button('Excel Radio', to_excel(pd.DataFrame(st.session_state.radio_db)), file_name='radio.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    elif m == 'Brogliaccio':
        st.markdown('## Brogliaccio - MASCHERA INSERIMENTO')
        with st.form('brog_form'):
            st.markdown('### Inserisci Messaggio Radio')
            c1,c2 = st.columns(2)
            with c1:
                mitt = st.text_input('Mittente *')
                dest = st.text_input('Destinatario *')
                canale_b = st.text_input('Canale')
            with c2:
                priorita = st.selectbox('Priorita', ['Bassa','Normale','Alta','Urgenza'])
                ora_b = st.text_input('Ora', value=datetime.now().strftime('%H:%M'))
            msg = st.text_area('Messaggio *')
            if st.form_submit_button('Salva Messaggio', type='primary', use_container_width=True):
                if mitt and dest and msg:
                    st.session_state.brogliaccio.append({'Data': str(date.today()), 'Ora': ora_b, 'Mittente': mitt, 'Destinatario': dest, 'Canale': canale_b, 'Priorita': priorita, 'Messaggio': msg})
                    st.success('Messaggio salvato')
        if st.session_state.brogliaccio:
            st.dataframe(pd.DataFrame(st.session_state.brogliaccio), use_container_width=True)
            st.download_button('Excel Brogliaccio', to_excel(pd.DataFrame(st.session_state.brogliaccio)), file_name='brogliaccio.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    elif m == 'Eventi':
        st.markdown('## Eventi - MASCHERA INSERIMENTO')
        with st.form('eventi_form'):
            st.markdown('### Inserisci Evento')
            c1,c2 = st.columns(2)
            with c1:
                nome_e = st.text_input('NOME EVENTO *')
                luogo_e = st.text_input('Luogo *')
                tipo_e = st.selectbox('Tipo', ['Esercitazione','Emergenza','Prevenzione','Manifestazione','Formazione','Altro'])
            with c2:
                data_e = st.date_input('Data Evento', value=date.today())
                ora_e = st.text_input('Ora Inizio', value='08:00')
                resp_e = st.text_input('Responsabile')
            descr_e = st.text_area('Descrizione')
            if st.form_submit_button('Crea Evento', type='primary', use_container_width=True):
                if nome_e and luogo_e:
                    st.session_state.eventi.append({'NomeEvento': nome_e, 'Luogo': luogo_e, 'Tipo': tipo_e, 'Data': str(data_e), 'Ora': ora_e, 'Responsabile': resp_e, 'Descrizione': descr_e})
                    st.success('Evento creato')
        if st.session_state.eventi:
            st.dataframe(pd.DataFrame(st.session_state.eventi), use_container_width=True)

    elif m == 'Emergenze':
        st.markdown('## Emergenze - MASCHERA INSERIMENTO')
        with st.form('emergenze_form'):
            st.markdown('### Inserisci Emergenza')
            c1,c2 = st.columns(2)
            with c1:
                tipo_em = st.selectbox('Tipo Emergenza *', ['Alluvione','Frana','Incendio','Terremoto','Neve','Ricerca','Altro'])
                luogo_em = st.text_input('Luogo Emergenza *')
                data_em = st.date_input('Data Attivazione', value=date.today())
            with c2:
                gravita = st.selectbox('Gravita', ['Bassa','Media','Alta','Critica'])
                squadre_em = st.text_input('Squadre Coinvolte')
                resp_em = st.text_input('Responsabile')
            descr_em = st.text_area('Descrizione Emergenza *')
            mezzi_em = st.multiselect('Mezzi Impiegati', ['Fuoristrada','Furgone','Ambulanza','Motosega','Idrovora','Gruppo Elettrogeno'])
            if st.form_submit_button('Attiva Emergenza', type='primary', use_container_width=True):
                if luogo_em and descr_em:
                    st.session_state.emergenze.append({'Tipo': tipo_em, 'Luogo': luogo_em, 'Data': str(data_em), 'Gravita': gravita, 'Squadre': squadre_em, 'Responsabile': resp_em, 'Descrizione': descr_em, 'Mezzi': ','.join(mezzi_em)})
                    st.success('Emergenza attivata')
        if st.session_state.emergenze:
            st.dataframe(pd.DataFrame(st.session_state.emergenze), use_container_width=True)

    elif m == 'Check-in':
        st.markdown('## Check-in - MASCHERA INSERIMENTO COLLEGATA EVENTO')
        if not st.session_state.eventi:
            st.warning('Crea prima un Evento in menu Eventi - Maschera mancante perche nessun evento')
        elif not st.session_state.volontari:
            st.warning('Inserisci prima un Volontario - Maschera mancante perche nessun volontario')
        else:
            with st.form('checkin_form'):
                st.markdown('### Registra Presenza')
                c1,c2 = st.columns(2)
                with c1:
                    ev_sel = st.selectbox('NOME EVENTO *', [e['NomeEvento'] for e in st.session_state.eventi])
                    vol_sel = st.selectbox('Volontario *', [f"{v['Nome']} {v['Cognome']}" for v in st.session_state.volontari])
                with c2:
                    post_sel = st.selectbox('Postazione *', ['Base','Avanzata'] + [p['Nome'] for p in st.session_state.postazioni] if st.session_state.postazioni else ['Base','Avanzata'])
                    ora_check = st.text_input('Ora Check-in', value=datetime.now().strftime('%H:%M'))
                if st.form_submit_button('Registra Check-in', type='primary', use_container_width=True):
                    st.session_state.checkin.append({'NomeEvento': ev_sel, 'Volontario': vol_sel, 'Postazione': post_sel, 'Ora': ora_check, 'Data': str(date.today())})
                    st.success('Check-in registrato')
        if st.session_state.checkin:
            st.dataframe(pd.DataFrame(st.session_state.checkin), use_container_width=True)

    elif m == 'Mezzi':
        st.markdown('## Mezzi - MASCHERA INSERIMENTO')
        with st.form('mezzi_form'):
            st.markdown('### Inserisci Mezzo')
            c1,c2 = st.columns(2)
            with c1:
                targa = st.text_input('Targa *')
                tipo_m = st.selectbox('Tipo Mezzo *', ['Fuoristrada','Furgone','Autocarro','Ambulanza','Pulmino','Altro'])
                modello_m = st.text_input('Modello')
            with c2:
                stato_m = st.selectbox('Stato', ['Disponibile','In Missione','In Manutenzione','Fuori Uso'])
                km_m = st.number_input('KM', min_value=0, value=0)
                scadenza_rev = st.date_input('Scadenza Revisione', value=date.today())
            note_m = st.text_area('Note')
            if st.form_submit_button('Salva Mezzo', type='primary', use_container_width=True):
                if targa and tipo_m:
                    st.session_state.mezzi.append({'Targa': targa, 'Tipo': tipo_m, 'Modello': modello_m, 'Stato': stato_m, 'KM': km_m, 'ScadenzaRevisione': str(scadenza_rev), 'Note': note_m})
                    st.success('Mezzo salvato')
        if st.session_state.mezzi:
            st.dataframe(pd.DataFrame(st.session_state.mezzi), use_container_width=True)

    elif m == 'Attrezzature':
        st.markdown('## Attrezzature - MASCHERA INSERIMENTO')
        with st.form('attr_form'):
            st.markdown('### Inserisci Attrezzatura')
            c1,c2 = st.columns(2)
            with c1:
                nome_a = st.text_input('Attrezzatura *')
                categoria_a = st.selectbox('Categoria', ['AIB','Idraulica','Elettrica','Radio','Sanitaria','Logistica','Altro'])
                quantita_a = st.number_input('Quantita *', min_value=1, value=1)
            with c2:
                locazione_a = st.text_input('Locazione')
                stato_a = st.selectbox('Stato', ['Disponibile','In Uso','Manutenzione','Da Sostituire'])
            note_a = st.text_area('Note')
            if st.form_submit_button('Salva Attrezzatura', type='primary', use_container_width=True):
                if nome_a and quantita_a:
                    st.session_state.attrezzature.append({'Attrezzatura': nome_a, 'Categoria': categoria_a, 'Quantita': quantita_a, 'Locazione': locazione_a, 'Stato': stato_a, 'Note': note_a})
                    st.success('Attrezzatura salvata')
        if st.session_state.attrezzature:
            st.dataframe(pd.DataFrame(st.session_state.attrezzature), use_container_width=True)

    elif m == 'Mappa Avanzata':
        st.markdown('## Mappa Avanzata - MASCHERA INSERIMENTO POSTAZIONI')
        st.info('Clicca su mappa per coordinate - Fullscreen sotto + e - con ESC')

        col1,col2,col3 = st.columns([2,2,1])
        with col1:
            map_type = st.selectbox('Tipo Mappa', ['OpenStreetMap','Google Map','Google Satellite','Google Hybrid'], index=0)
        with col2:
            icona_sel = st.selectbox('Icona Marker', ['Nessuna'] + [i['Nome'] for i in st.session_state.icone] if st.session_state.icone else ['Nessuna'])
        with col3:
            lab1 = 'Riduci Mappa 1' if st.session_state.map_fullscreen else 'Espandi Mappa 1'
            if st.button(lab1, key='exp1', use_container_width=True):
                st.session_state.map_fullscreen = not st.session_state.map_fullscreen
                st.rerun()

        h1 = 800 if st.session_state.map_fullscreen else 450

        try:
            import folium
            from streamlit_folium import st_folium
            from folium.plugins import Fullscreen
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
            lat_c, lon_c = 45.65, 8.79
            if st.session_state.postazioni:
                lat_c = sum([p['Lat'] for p in st.session_state.postazioni]) / len(st.session_state.postazioni)
                lon_c = sum([p['Log'] for p in st.session_state.postazioni]) / len(st.session_state.postazioni)
            mm = folium.Map(location=[lat_c, lon_c], zoom_start=12, tiles=None)
            if map_type == 'OpenStreetMap':
                folium.TileLayer('openstreetmap', name='OpenStreetMap').add_to(mm)
            elif map_type == 'Google Map':
                folium.TileLayer(tiles='https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}', attr='Google', name='Google Map').add_to(mm)
            elif map_type == 'Google Satellite':
                folium.TileLayer(tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', attr='Google', name='Google Satellite').add_to(mm)
            else:
                folium.TileLayer(tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr='Google', name='Google Hybrid').add_to(mm)
            Fullscreen(position='topleft', title='Espandi 100%', title_cancel='Esci ESC', force_separate_button=True).add_to(mm)
            for p in st.session_state.postazioni:
                lat_f = p['Lat']
                lon_f = p['Log']
                popup_html = f"<b>{p['Nome']}</b><br>{p.get('Comune','')}<br><a href='https://www.google.com/maps/search/?api=1&query={lat_f},{lon_f}' target='_blank'>Google</a>"
                p_icon = p.get('Icona','Nessuna')
                use_path = None
                if p_icon!= 'Nessuna':
                    ico = next((i for i in st.session_state.icone if i['Nome'] == p_icon), None)
                    if ico and ico.get('FileBytes'):
                        use_path = salva_icona_temp(ico['FileBytes'], p_icon)
                if use_path:
                    folium.Marker([lat_f, lon_f], popup=popup_html, icon=folium.CustomIcon(use_path, icon_size=(40,40))).add_to(mm)
                else:
                    folium.Marker([lat_f, lon_f], popup=popup_html, icon=folium.Icon(color='green')).add_to(mm)
            icon_path_sel = None
            if icona_sel!= 'Nessuna':
                ico_sel = next((i for i in st.session_state.icone if i['Nome'] == icona_sel), None)
                if ico_sel and ico_sel.get('FileBytes'):
                    icon_path_sel = salva_icona_temp(ico_sel['FileBytes'], icona_sel)
            for tm in st.session_state.temp_markers:
                if icon_path_sel:
                    folium.Marker([tm['lat'], tm['lon']], icon=folium.CustomIcon(icon_path_sel, icon_size=(40,40))).add_to(mm)
                else:
                    folium.Marker([tm['lat'], tm['lon']], icon=folium.Icon(color='orange')).add_to(mm)
            folium.LayerControl().add_to(mm)
            out = st_folium(mm, width=1400, height=h1, use_container_width=True, returned_objects=['last_clicked'], key='map1')
            if out and out.get('last_clicked'):
                lat_c = out['last_clicked']['lat']
                lon_c = out['last_clicked']['lng']
                com, via = rev_geo(lat_c, lon_c)
                st.session_state.temp_markers.append({'lat': lat_c, 'lon': lon_c, 'icona': icona_sel, 'comune': com, 'via': via})
                st.session_state.last_clicked = {'lat': lat_c, 'lon': lon_c, 'icona': icona_sel, 'comune': com, 'via': via}
                st.success(f"Click {lat_c:.5f} {lon_c:.5f} {com} - Compila maschera sotto")
                st.rerun()
        except Exception as e:
            st.error(f"Errore mappa: {e}")

        last = st.session_state.last_clicked
        if last:
            st.info(f"Ultimo click: {last['lat']:.6f} {last['lon']:.6f} {last.get('comune','')} Icona {last.get('icona','')}")

        st.divider()
        st.markdown('### MASCHERA INSERIMENTO POSTAZIONE')
        with st.form('form_post'):
            c1,c2 = st.columns(2)
            with c1:
                nome_p = st.text_input('Nome Postazione *')
                comune_p = st.text_input('Comune *', value=last.get('comune','') if last else '')
                via_p = st.text_input('Via *', value=last.get('via','') if last else '')
                tipo_p = st.selectbox('Tipo Postazione', ['Base','Avanzata','Check Point','Cantiere','Magazzino','Altro'])
            with c2:
                lat_p = st.text_input('Latitudine *', value=str(last['lat']) if last else '')
                lon_p = st.text_input('Longitudine *', value=str(last['lon']) if last else '')
                lista_icone = ['Nessuna'] + [i['Nome'] for i in st.session_state.icone] if st.session_state.icone else ['Nessuna']
                icona_def = last.get('icona','Nessuna') if last else 'Nessuna'
                idx_ico = lista_icone.index(icona_def) if icona_def in lista_icone else 0
                icona_p = st.selectbox('Icona Libreria', lista_icone, index=idx_ico)
            note_p = st.text_area('Note Postazione')
            if st.form_submit_button('Salva Postazione con Icona Marker', type='primary', use_container_width=True):
                if nome_p and comune_p and lat_p and lon_p:
                    try:
                        lat_v = float(lat_p.replace(',','.'))
                        lon_v = float(lon_p.replace(',','.'))
                        st.session_state.postazioni.append({'Nome': nome_p, 'Comune': comune_p, 'Via': via_p, 'Tipo': tipo_p, 'Icona': icona_p, 'Lat': lat_v, 'Log': lon_v, 'Note': note_p})
                        st.session_state.temp_markers = []
                        st.session_state.last_clicked = None
                        st.success('Postazione salvata')
                        st.rerun()
                    except:
                        st.error('Lat/Log non validi')
                else:
                    st.error('Compila Nome, Comune, Lat, Log *')

        st.divider()
        st.markdown('## Mappa Tutte Postazioni - Default OpenStreetMap')
        lab2 = 'Riduci Mappa 2' if st.session_state.map_fullscreen2 else 'Espandi Mappa 2'
        if st.button(lab2, key='exp2', use_container_width=True):
            st.session_state.map_fullscreen2 = not st.session_state.map_fullscreen2
            st.rerun()
        h2 = 800 if st.session_state.map_fullscreen2 else 500
        if st.session_state.postazioni:
            df_post = pd.DataFrame(st.session_state.postazioni)
            st.dataframe(df_post, use_container_width=True)
            st.download_button('Excel Postazioni', to_excel(df_post), file_name='postazioni.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            try:
                import folium
                from streamlit_folium import st_folium
                from folium.plugins import Fullscreen
                lat_m = df_post.Lat.mean()
                lon_m = df_post.Log.mean()
                m2 = folium.Map(location=[lat_m, lon_m], zoom_start=11, tiles='openstreetmap')
                Fullscreen(position='topleft', title='Espandi', title_cancel='Esci ESC', force_separate_button=True).add_to(m2)
                for p in st.session_state.postazioni:
                    folium.Marker([p['Lat'], p['Log']], popup=p['Nome'], icon=folium.Icon(color='green')).add_to(m2)
                folium.LayerControl().add_to(m2)
                st_folium(m2, width=1400, height=h2, use_container_width=True, key='map2')
            except Exception as e:
                st.error(f"Errore mappa 2: {e}")
        else:
            st.info('Nessuna postazione')

    elif m == 'Libreria Icone':
        st.markdown('## Libreria Icone - MASCHERA INSERIMENTO MARKER')
        with st.form('icone_form'):
            st.markdown('### Carica Icona per Marker Mappa')
            c1,c2 = st.columns([1,2])
            with c1:
                nome_i = st.text_input('Nome icona *')
                file_i = st.file_uploader('Carica PNG/JPG *', type=['png','jpg','jpeg'])
                if file_i:
                    st.image(file_i, width=120, caption='Preview marker')
            with c2:
                descr_i = st.text_area('Descrizione Icona')
                categoria_i = st.selectbox('Categoria', ['Emergenza','Postazione','Mezzo','Attrezzatura','Pericolo','Altro'])
            if st.form_submit_button('Salva Icona Marker', type='primary', use_container_width=True):
                if nome_i and file_i:
                    st.session_state.icone.append({'Nome': nome_i, 'FileName': file_i.name, 'FileBytes': file_i.getvalue(), 'Descrizione': descr_i, 'Categoria': categoria_i})
                    st.success(f"Icona {nome_i} caricata - disponibile in Mappa")
                else:
                    st.error('Nome e File *')
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

    elif m == 'Backup':
        st.markdown('## Backup - Excel e PDF per Tutti i Form')
        for key, titolo in [('volontari','Volontari'),('radio_db','DB Radio'),('brogliaccio','Brogliaccio'),('eventi','Eventi'),('emergenze','Emergenze'),('checkin','Check-in'),('mezzi','Mezzi'),('attrezzature','Attrezzature'),('postazioni','Postazioni')]:
            if st.session_state[key]:
                df = pd.DataFrame(st.session_state[key])
                st.write(f"**{titolo}: {len(df)}**")
                c1,c2 = st.columns(2)
                c1.download_button(f"Excel {titolo}", to_excel(df), file_name=f"{key}.xlsx", mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', key=f"ex_{key}", use_container_width=True)
                pdf = genera_pdf(df, titolo)
                if pdf:
                    c2.download_button(f"PDF {titolo}", pdf, file_name=f"{key}.pdf", mime='application/pdf', key=f"pdf_{key}", use_container_width=True)

    elif m == 'Esporta':
        st.markdown('## Esporta Tutto')
        for key, titolo in [('volontari','Volontari'),('radio_db','Radio'),('eventi','Eventi'),('emergenze','Emergenze'),('checkin','Check-in'),('postazioni','Postazioni')]:
            if st.session_state[key]:
                df = pd.DataFrame(st.session_state[key])
                st.download_button(f"Scarica {titolo}", to_excel(df), file_name=f"{key}.xlsx", mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', key=f"ex2_{key}")