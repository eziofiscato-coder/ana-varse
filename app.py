import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import date

st.set_page_config(page_title='ANA Varese', layout='wide')

def hdr():
    st.markdown(
        '<div style="background:#0e7a3d;padding:8px;'
        'border-radius:8px;color:white;text-align:center;'
        'font-weight:bold;">NUCLEO VOLONTARI DI PROTEZIONE CIVILE- ANA VARESE Squadra di Caronno Pertusella</div>',
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
            st.image('copertina.png', width=400)
        except:
            try:
                st.image('logo.png', width=250)
            except:
                pass
    st.markdown(
        '<h2 style="text-align:center;color:#0e7a3d;">'
        'VOLONTARIATO<br>Sezione di Varese</h2>',
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
        st.markdown('### MENU COMPLETO FORM')
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
        st.markdown('## Dashboard - Tutti i Form')
        st.info('Menu completo - tutti i form visibili')
        c1,c2,c3,c4 = st.columns(4)
        with c1:
            st.metric('Volontari', len(st.session_state.volontari))
        with c2:
            st.metric('Eventi', len(st.session_state.eventi))
        with c3:
            st.metric('Check-in', len(st.session_state.checkin))
        with c4:
            st.metric('Postazioni', len(st.session_state.postazioni))
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
        st.markdown('## Volontari - Con Foto e Sottomaschere')
        t1,t2 = st.tabs(['Anagrafica e Foto', 'Elenco'])
        with t1:
            with st.form('vol'):
                nome = st.text_input('Nome *')
                comune = st.text_input('Comune *')
                foto = st.file_uploader('Foto', type=['png','jpg','jpeg'])
                if foto:
                    st.image(foto, width=100, caption='Preview foto')
                if st.form_submit_button('Salva', use_container_width=True, type='primary'):
                    if nome and comune:
                        fb = foto.getvalue() if foto else None
                        st.session_state.volontari.append({'Nome': nome, 'Comune': comune, 'Foto': fb})
                        st.success('Salvato')
        with t2:
            if st.session_state.volontari:
                for v in st.session_state.volontari:
                    c1,c2 = st.columns([1,3])
                    with c1:
                        if v.get('Foto'):
                            st.image(v['Foto'], width=80)
                    with c2:
                        st.write(f"{v['Nome']} - {v['Comune']}")

    elif m == 'DB Radio':
        st.markdown('## DB Radio - Combo')
        with st.form('radio'):
            modello = st.text_input('Modello *')
            matricola = st.text_input('Matricola *')
            tipo = st.selectbox('Tipo *', ['DMR','PMR446','TETRA','NAUTICHE','VHF','UHF','VHF/UHF','HF','CB','Altro'])
            freq = st.text_input('Frequenza')
            if st.form_submit_button('Salva', use_container_width=True, type='primary'):
                if modello and matricola:
                    st.session_state.radio_db.append({'Modello': modello, 'Matricola': matricola, 'Tipo': tipo, 'Frequenza': freq})
                    st.success('Salvata')
        if st.session_state.radio_db:
            st.dataframe(pd.DataFrame(st.session_state.radio_db), use_container_width=True)

    elif m == 'Brogliaccio':
        st.markdown('## Brogliaccio')
        with st.form('brog'):
            msg = st.text_area('Messaggio *')
            if st.form_submit_button('Salva', use_container_width=True, type='primary'):
                if msg:
                    st.session_state.brogliaccio.append({'Data': str(date.today()), 'Messaggio': msg})
                    st.success('Salvato')
        if st.session_state.brogliaccio:
            st.dataframe(pd.DataFrame(st.session_state.brogliaccio), use_container_width=True)

    elif m == 'Eventi':
        st.markdown('## Eventi - NOME EVENTO')
        with st.form('eventi'):
            nome_evento = st.text_input('NOME EVENTO *')
            luogo = st.text_input('Luogo *')
            if st.form_submit_button('Crea', use_container_width=True, type='primary'):
                if nome_evento and luogo:
                    st.session_state.eventi.append({'NomeEvento': nome_evento, 'Luogo': luogo})
                    st.success('Creato')
        if st.session_state.eventi:
            st.dataframe(pd.DataFrame(st.session_state.eventi), use_container_width=True)

    elif m == 'Check-in':
        st.markdown('## Check-in')
        if st.session_state.eventi and st.session_state.volontari:
            with st.form('checkin'):
                ev = st.selectbox('NOME EVENTO *', [e['NomeEvento'] for e in st.session_state.eventi])
                vol = st.selectbox('Volontario *', [v['Nome'] for v in st.session_state.volontari])
                post = st.selectbox('Postazione', ['Base','Avanzata'] + [p['Nome'] for p in st.session_state.postazioni] if st.session_state.postazioni else ['Base','Avanzata'])
                if st.form_submit_button('Registra', use_container_width=True, type='primary'):
                    st.session_state.checkin.append({'NomeEvento': ev, 'Volontario': vol, 'Postazione': post})
                    st.success('Registrato')
        if st.session_state.checkin:
            st.dataframe(pd.DataFrame(st.session_state.checkin), use_container_width=True)

    elif m == 'Mezzi':
        st.markdown('## Mezzi')
        with st.form('mezzi'):
            targa = st.text_input('Targa *')
            if st.form_submit_button('Salva', use_container_width=True, type='primary'):
                if targa:
                    st.session_state.mezzi.append({'Targa': targa})
                    st.success('Salvato')
        if st.session_state.mezzi:
            st.dataframe(pd.DataFrame(st.session_state.mezzi), use_container_width=True)

    elif m == 'Attrezzature':
        st.markdown('## Attrezzature')
        with st.form('attr'):
            nome_a = st.text_input('Attrezzatura *')
            if st.form_submit_button('Salva', use_container_width=True, type='primary'):
                if nome_a:
                    st.session_state.attrezzature.append({'Attrezzatura': nome_a})
                    st.success('Salvata')
        if st.session_state.attrezzature:
            st.dataframe(pd.DataFrame(st.session_state.attrezzature), use_container_width=True)

    elif m == 'Mappa Avanzata':
        st.markdown('## Mappa Avanzata - Come Stamattina')
        st.markdown('### Clicca su mappa per marker con icona')

        icona_sel = st.selectbox(
            'Icona da Libreria per marker',
            ['Nessuna'] + [i['Nome'] for i in st.session_state.icone]
            if st.session_state.icone else ['Nessuna']
        )

        try:
            import folium
            from streamlit_folium import st_folium
            import requests

            def reverse_geocode(lat, lon):
                try:
                    url = f'https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=18&addressdetails=1'
                    headers = {'User-Agent': 'ANA-Varese-App'}
                    r = requests.get(url, headers=headers, timeout=5)
                    if r.status_code == 200:
                        data = r.json()
                        addr = data.get('address', {})
                        comune = addr.get('city') or addr.get('town') or addr.get('village') or addr.get('municipality') or ''
                        via = addr.get('road') or addr.get('footway') or ''
                        return comune, via
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
                folium.Marker(
                    [p['Lat'], p['Log']],
                    popup=f"{p['Nome']} - {p.get('Comune','')} - {p.get('Via','')} - {p.get('Icona','')}",
                    icon=folium.Icon(color='blue')
                ).add_to(mapa)

            for tm in st.session_state.temp_markers:
                folium.Marker(
                    [tm['lat'], tm['lon']],
                    popup=f"TEMP {tm.get('icona','')}",
                    icon=folium.Icon(color='orange')
                ).add_to(mapa)

            out = st_folium(mapa, height=450, width=700, returned_objects=['last_clicked'])

            if out and out.get('last_clicked'):
                lat_click = out['last_clicked']['lat']
                lon_click = out['last_clicked']['lng']
                comune_auto, via_auto = reverse_geocode(lat_click, lon_click)
                st.session_state.temp_markers.append({
                    'lat': lat_click,
                    'lon': lon_click,
                    'icona': icona_sel,
                    'comune': comune_auto,
                    'via': via_auto
                })
                st.session_state.last_clicked = {
                    'lat': lat_click,
                    'lon': lon_click,
                    'icona': icona_sel,
                    'comune': comune_auto,
                    'via': via_auto
                }
                st.success(f'Marker: {lat_click:.5f} {lon_click:.5f} {icona_sel} - {comune_auto} {via_auto}')

        except Exception as e:
            st.error(f'Errore mappa: {e}')

        last = st.session_state.last_clicked
        if last:
            st.info(f"Click: Lat {last['lat']:.6f} Log {last['lon']:.6f} Comune {last.get('comune','')} Via {last.get('via','')} Icona {last.get('icona','')}")

        with st.form('form_post'):
            nome_p = st.text_input('Nome Postazione *')
            comune_p = st.text_input('Comune *', value=last.get('comune','') if last else '')
            via_p = st.text_input('Via *', value=last.get('via','') if last else '')
            c1,c2 = st.columns(2)
            with c1:
                lat_def = str(last['lat']) if last else ''
                lat_p = st.text_input('Lat * - Auto da click', value=lat_def)
            with c2:
                lon_def = str(last['lon']) if last else ''
                lon_p = st.text_input('Log * - Auto da click', value=lon_def)
            lista_icone = ['Nessuna'] + [i['Nome'] for i in st.session_state.icone] if st.session_state.icone else ['Nessuna']
            icona_def = last.get('icona','Nessuna') if last else 'Nessuna'
            if icona_def in lista_icone:
                idx_ico = lista_icone.index(icona_def)
            else:
                idx_ico = 0
            icona_p = st.selectbox('Icona Libreria', lista_icone, index=idx_ico)
            note_p = st.text_area('Note')
            if st.form_submit_button('Salva Postazione', use_container_width=True, type='primary'):
                if nome_p and comune_p and lat_p and lon_p:
                    try:
                        lat_v = float(lat_p.replace(',','.'))
                        lon_v = float(lon_p.replace(',','.'))
                        st.session_state.postazioni.append({
                            'Nome': nome_p,
                            'Comune': comune_p,
                            'Via': via_p,
                            'Icona': icona_p,
                            'Lat': lat_v,
                            'Log': lon_v,
                            'Note': note_p
                        })
                        st.session_state.temp_markers = []
                        st.session_state.last_clicked = None
                        st.success('Postazione salvata')
                        st.rerun()
                    except:
                        st.error('Lat/Log non validi')
                else:
                    st.error('Compila campi *')

        st.markdown('### Postazioni salvate su altra mappa sotto')
        if st.session_state.postazioni:
            df_post = pd.DataFrame(st.session_state.postazioni)
            st.dataframe(df_post, use_container_width=True)
            out = BytesIO()
            df_post.to_excel(out, index=False, engine='openpyxl')
            st.download_button('Scarica', out.getvalue(), file_name=f"postazioni_{date.today()}.xlsx", mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', use_container_width=True)
            try:
                import folium
                from streamlit_folium import st_folium
                lat_m = df_post.Lat.mean()
                lon_m = df_post.Log.mean()
                m2 = folium.Map(location=[lat_m, lon_m], zoom_start=12)
                for p in st.session_state.postazioni:
                    folium.Marker([p['Lat'], p['Log']], popup=f"{p['Nome']} - {p['Comune']} - {p['Via']}").add_to(m2)
                st_folium(m2, height=350, width=700)
            except:
                pass
        else:
            st.warning('Nessuna postazione')

    elif m == 'Libreria Icone':
        st.markdown('## Libreria Icone - Visualizza Icona')
        with st.form('icone'):
            nome_i = st.text_input('Nome icona *')
            file_i = st.file_uploader('Carica icona', type=['png','svg','jpg','jpeg'])
            if file_i:
                st.image(file_i, width=120, caption='Preview icona caricata')
            if st.form_submit_button('Salva', use_container_width=True, type='primary'):
                if nome_i and file_i:
                    st.session_state.icone.append({'Nome': nome_i, 'FileName': file_i.name, 'FileBytes': file_i.getvalue()})
                    st.success('Icona caricata')
        if st.session_state.icone:
            st.markdown('### Icone caricate - Visualizzazione')
            cols = st.columns(3)
            for idx, ico in enumerate(st.session_state.icone):
                col = cols[idx % 3]
                with col:
                    st.write(f"**{ico['Nome']}**")
                    if ico.get('FileBytes'):
                        try:
                            st.image(ico['FileBytes'], width=100)
                        except:
                            st.write('Non visualizzabile')
                        st.download_button(f"Download {ico['Nome']}", ico['FileBytes'], file_name=ico['FileName'], key=f"dl_{idx}", use_container_width=True)
                    if st.button('Elimina', key=f"del_{idx}"):
                        st.session_state.icone.pop(idx)
                        st.rerun()

    elif m == 'Backup':
        st.markdown('## Backup')
        if st.session_state.volontari:
            df = pd.DataFrame(st.session_state.volontari)
            out = BytesIO()
            df.to_excel(out, index=False, engine='openpyxl')
            st.download_button('Scarica Volontari', out.getvalue(), file_name='volontari.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', use_container_width=True)

    elif m == 'Esporta':
        st.markdown('## Esporta')
        if st.session_state.postazioni:
            df = pd.DataFrame(st.session_state.postazioni)
            out = BytesIO()
            df.to_excel(out, index=False, engine='openpyxl')
            st.download_button('Scarica Postazioni', out.getvalue(), file_name='postazioni.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', use_container_width=True)
