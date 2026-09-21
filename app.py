import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import date, datetime

st.set_page_config(page_title='ANA Varese', layout='wide')

def hdr():
    st.markdown(
        '<div style="background:#0e7a3d;padding:8px;'
        'border-radius:8px;color:white;text-align:center;'
        'font-weight:bold;">NUCLEO PROT CIVILE ANA VARESE '
        'Squadra Alpini Caronno Pertusella Bariola</div>',
        unsafe_allow_html=True
    )

def to_excel(df):
    out = BytesIO()
    df.to_excel(out, index=False, engine='openpyxl')
    return out.getvalue()

for k in [
    'page','logged','menu','volontari','radio_db',
    'eventi','checkin','icone','postazioni',
    'last_clicked','temp_markers','brogliaccio',
    'mezzi','attrezzature'
]:
    if k not in st.session_state:
        if k == 'page':
            st.session_state[k] = 'entra'
        elif k == 'logged':
            st.session_state[k] = False
        elif k == 'menu':
            st.session_state[k] = 'Dashboard'
        elif k == 'last_clicked':
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
            st.image('copertina.png', width=300)
        except:
            try:
                st.image('logo.png', width=150)
            except:
                pass
    st.markdown(
        '<h2 style="text-align:center;color:#0e7a3d;">'
        'GESTIONALE<br>Prot Civile</h2>',
        unsafe_allow_html=True
    )
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
        st.markdown('### MENU COMPLETO')
        menu = st.radio(
            'Scegli:',
            [
                'Dashboard',
                'Volontari',
                'DB Radio',
                'Brogliaccio',
                'Eventi',
                'Check-in',
                'Mezzi',
                'Attrezzature',
                'Mappa Avanzata',
                'Libreria Icone',
                'Backup',
                'Esporta'
            ],
            index=0
        )
        st.session_state.menu = menu
        st.divider()
        if st.button('Logout', use_container_width=True):
            st.session_state.logged = False
            st.session_state.page = 'entra'
            st.rerun()

    m = st.session_state.menu

    if m == 'Dashboard':
        st.markdown('## Dashboard')
        c1,c2,c3,c4 = st.columns(4)
        with c1:
            st.metric('Volontari', len(st.session_state.volontari))
        with c2:
            st.metric('Eventi', len(st.session_state.eventi))
        with c3:
            st.metric('Check-in', len(st.session_state.checkin))
        with c4:
            st.metric('Postazioni', len(st.session_state.postazioni))

    elif m == 'Volontari':
        st.markdown('## Volontari - Sottomaschere')
        t1,t2,t3,t4 = st.tabs([
            'Anagrafica Foto',
            'Contatti Ruolo',
            'Qualifiche',
            'Doc Taglie Note'
        ])

        with t1:
            with st.form('vol1'):
                nome = st.text_input('Nome *')
                cf = st.text_input('CF')
                comune = st.text_input('Comune *')
                via = st.text_input('Via')
                lat_txt = st.text_input('Lat')
                lon_txt = st.text_input('Log')
                foto = st.file_uploader('Foto', type=['png','jpg','jpeg'])
                if foto:
                    st.image(foto, width=100)
                if st.form_submit_button('Salva', use_container_width=True, type='primary'):
                    if nome and comune:
                        try:
                            lat_v = float(lat_txt.replace(',','.')) if lat_txt else 0.0
                            lon_v = float(lon_txt.replace(',','.')) if lon_txt else 0.0
                        except:
                            lat_v = 0.0
                            lon_v = 0.0
                        fb = foto.getvalue() if foto else None
                        st.session_state.volontari.append({
                            'Nome': nome,
                            'CF': cf,
                            'Comune': comune,
                            'Via': via,
                            'Lat': lat_v,
                            'Log': lon_v,
                            'Foto': fb,
                            'Cell': '',
                            'Email': '',
                            'Ruolo': 'Volontario',
                            'Qual': '',
                            'Doc': '',
                            'Taglia': '',
                            'Note': ''
                        })
                        st.success('Salvato')

        with t2:
            if st.session_state.volontari:
                sel = st.selectbox('Seleziona', [v['Nome'] for v in st.session_state.volontari], key='c1')
                idx = [v['Nome'] for v in st.session_state.volontari].index(sel)
                vol = st.session_state.volontari[idx]
                if vol.get('Foto'):
                    st.image(vol['Foto'], width=100)
                with st.form('vol2'):
                    cell = st.text_input('Cell', value=vol.get('Cell',''))
                    email = st.text_input('Email', value=vol.get('Email',''))
                    ruolo = st.selectbox('Ruolo', ['Volontario','Caposquadra','Coordinatore','Autista','Radio','Logistica'])
                    if st.form_submit_button('Aggiorna', use_container_width=True):
                        st.session_state.volontari[idx]['Cell'] = cell
                        st.session_state.volontari[idx]['Email'] = email
                        st.session_state.volontari[idx]['Ruolo'] = ruolo
                        st.success('Aggiornato')

        with t3:
            if st.session_state.volontari:
                sel = st.selectbox('Volontario', [v['Nome'] for v in st.session_state.volontari], key='c2')
                idx = [v['Nome'] for v in st.session_state.volontari].index(sel)
                qual = st.multiselect('Qualifiche', ['AIB','BLSD','Radio','Motosega','Idro'])
                if st.button('Salva Qual', use_container_width=True):
                    st.session_state.volontari[idx]['Qual'] = ','.join(qual)
                    st.success('Salvato')

        with t4:
            if st.session_state.volontari:
                sel = st.selectbox('Vol', [v['Nome'] for v in st.session_state.volontari], key='c3')
                idx = [v['Nome'] for v in st.session_state.volontari].index(sel)
                doc = st.text_input('Doc')
                taglia = st.selectbox('Taglia', ['S','M','L','XL','XXL'])
                note = st.text_area('Note')
                if st.button('Salva Doc', use_container_width=True):
                    st.session_state.volontari[idx]['Doc'] = doc
                    st.session_state.volontari[idx]['Taglia'] = taglia
                    st.session_state.volontari[idx]['Note'] = note
                    st.success('Salvato')
            if st.session_state.volontari:
                df = pd.DataFrame([{'Nome': v['Nome'], 'Comune': v['Comune'], 'Ruolo': v.get('Ruolo','')} for v in st.session_state.volontari])
                st.dataframe(df, use_container_width=True)

    elif m == 'DB Radio':
        st.markdown('## DB Radio Combo')
        with st.form('radio'):
            modello = st.text_input('Modello *')
            matricola = st.text_input('Matricola *')
            tipo = st.selectbox('Tipo *', ['DMR','PMR446','TETRA','NAUTICHE','VHF','UHF','VHF/UHF','HF','CB','Altro'])
            freq = st.text_input('Freq')
            if st.form_submit_button('Salva', use_container_width=True, type='primary'):
                if modello and matricola:
                    st.session_state.radio_db.append({'Modello': modello, 'Matricola': matricola, 'Tipo': tipo, 'Freq': freq})
                    st.success('Salvata')
        if st.session_state.radio_db:
            st.dataframe(pd.DataFrame(st.session_state.radio_db), use_container_width=True)

    elif m == 'Eventi':
        st.markdown('## Eventi')
        with st.form('eventi'):
            nome_e = st.text_input('NOME EVENTO *')
            luogo = st.text_input('Luogo *')
            if st.form_submit_button('Crea', use_container_width=True, type='primary'):
                if nome_e and luogo:
                    st.session_state.eventi.append({'NomeEvento': nome_e, 'Luogo': luogo})
                    st.success('Creato')
        if st.session_state.eventi:
            st.dataframe(pd.DataFrame(st.session_state.eventi), use_container_width=True)

    elif m == 'Check-in':
        st.markdown('## Check-in - Collegato Evento')
        if st.session_state.eventi and st.session_state.volontari:
            ev_nomi = [e['NomeEvento'] for e in st.session_state.eventi]
            ev_sel = st.selectbox('NOME EVENTO *', ev_nomi)
            ev_det = next((e for e in st.session_state.eventi if e['NomeEvento'] == ev_sel), None)
            if ev_det:
                st.info(f"Evento: {ev_det.get('NomeEvento','')} - Luogo: {ev_det.get('Luogo','')}")
            with st.form('checkin'):
                vol = st.selectbox('Volontario *', [v['Nome'] for v in st.session_state.volontari])
                post = st.selectbox('Postazione', ['Base','Avanzata'] + [p['Nome'] for p in st.session_state.postazioni] if st.session_state.postazioni else ['Base','Avanzata'])
                if st.form_submit_button('Registra', use_container_width=True, type='primary'):
                    st.session_state.checkin.append({'NomeEvento': ev_sel, 'Volontario': vol, 'Postazione': post})
                    st.success('Registrato')
        if st.session_state.checkin:
            st.dataframe(pd.DataFrame(st.session_state.checkin), use_container_width=True)

    elif m == 'Mappa Avanzata':
        st.markdown('## Mappa Avanzata')
        icona_sel = st.selectbox('Icona Libreria', ['Nessuna'] + [i['Nome'] for i in st.session_state.icone] if st.session_state.icone else ['Nessuna'])
        try:
            import folium
            from streamlit_folium import st_folium
            import requests
            def rev_geo(lat, lon):
                try:
                    url = f'https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=18&addressdetails=1'
                    headers = {'User-Agent': 'ANA-Varese'}
                    r = requests.get(url, headers=headers, timeout=5)
                    if r.status_code == 200:
                        d = r.json()
                        a = d.get('address', {})
                        c = a.get('city') or a.get('town') or a.get('village') or ''
                        v = a.get('road') or ''
                        return c, v
                except:
                    pass
                return '', ''
            if st.session_state.postazioni:
                lat_c = sum([p['Lat'] for p in st.session_state.postazioni]) / len(st.session_state.postazioni)
                lon_c = sum([p['Log'] for p in st.session_state.postazioni]) / len(st.session_state.postazioni)
            else:
                lat_c = 45.65
                lon_c = 8.79
            mapa = folium.Map(location=[lat_c, lon_c], zoom_start=11)
            for p in st.session_state.postazioni:
                folium.Marker([p['Lat'], p['Log']], popup=f"{p['Nome']} - {p.get('Comune','')}", icon=folium.Icon(color='blue')).add_to(mapa)
            for tm in st.session_state.temp_markers:
                folium.Marker([tm['lat'], tm['lon']], popup=f"TEMP {tm.get('icona','')}", icon=folium.Icon(color='orange')).add_to(mapa)
            out = st_folium(mapa, height=450, width=700, returned_objects=['last_clicked'])
            if out and out.get('last_clicked'):
                lat_c = out['last_clicked']['lat']
                lon_c = out['last_clicked']['lng']
                com, via = rev_geo(lat_c, lon_c)
                st.session_state.temp_markers.append({'lat': lat_c, 'lon': lon_c, 'icona': icona_sel, 'comune': com, 'via': via})
                st.session_state.last_clicked = {'lat': lat_c, 'lon': lon_c, 'icona': icona_sel, 'comune': com, 'via': via}
                st.success(f'Marker: {lat_c:.5f} {lon_c:.5f} {com} {via}')
        except Exception as e:
            st.error(f'Errore: {e}')
        last = st.session_state.last_clicked
        if last:
            st.info(f"Click: {last['lat']:.6f} {last['lon']:.6f} {last.get('comune','')} {last.get('via','')}")
        with st.form('form_post'):
            nome_p = st.text_input('Nome Postazione *')
            comune_p = st.text_input('Comune *', value=last.get('comune','') if last else '')
            via_p = st.text_input('Via *', value=last.get('via','') if last else '')
            c1,c2 = st.columns(2)
            with c1:
                lat_def = str(last['lat']) if last else ''
                lat_p = st.text_input('Lat *', value=lat_def)
            with c2:
                lon_def = str(last['lon']) if last else ''
                lon_p = st.text_input('Log *', value=lon_def)
            lista_icone = ['Nessuna'] + [i['Nome'] for i in st.session_state.icone] if st.session_state.icone else ['Nessuna']
            icona_def = last.get('icona','Nessuna') if last else 'Nessuna'
            if icona_def in lista_icone:
                idx_ico = lista_icone.index(icona_def)
            else:
                idx_ico = 0
            icona_p = st.selectbox('Icona', lista_icone, index=idx_ico)
            if st.form_submit_button('Salva', use_container_width=True, type='primary'):
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
        if st.session_state.postazioni:
            st.dataframe(pd.DataFrame(st.session_state.postazioni), use_container_width=True)

    elif m == 'Libreria Icone':
        st.markdown('## Libreria Icone')
        with st.form('icone'):
            nome_i = st.text_input('Nome icona *')
            file_i = st.file_uploader('Carica', type=['png','jpg','jpeg'])
            if file_i:
                st.image(file_i, width=100)
            if st.form_submit_button('Salva', use_container_width=True, type='primary'):
                if nome_i and file_i:
                    st.session_state.icone.append({'Nome': nome_i, 'FileName': file_i.name, 'FileBytes': file_i.getvalue()})
                    st.success('Caricata')
        if st.session_state.icone:
            cols