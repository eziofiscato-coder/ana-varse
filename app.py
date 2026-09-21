import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime, date

st.set_page_config(page_title='ANA Varese', layout='wide')

def hdr():
    st.markdown(
        '<div style="background:#0e7a3d; padding:8px; '
        'border-radius:8px; color:white; text-align:center; '
        'font-weight:bold;">NUCLEO VOLONTARI - ANA VARESE</div>',
        unsafe_allow_html=True
    )

def to_excel(df):
    out = BytesIO()
    df.to_excel(out, index=False, engine='openpyxl')
    return out.getvalue()

for k in [
    'page','logged','menu','volontari','radio_db',
    'eventi','checkin','icone','postazioni',
    'last_clicked','temp_markers'
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
        '<h2 style="text-align:center; color:#0e7a3d;">'
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
        st.markdown('### MENU')
        menu = st.radio(
            'Scegli:',
            [
                'Dashboard',
                'Volontari',
                'DB Radio',
                'Eventi',
                'Check-in',
                'Mappa Avanzata',
                'Libreria Icone'
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
        st.markdown('## Volontari - Foto')
        with st.form('vol'):
            nome = st.text_input('Nome *')
            comune = st.text_input('Comune *')
            lat_txt = st.text_input('Lat')
            lon_txt = st.text_input('Log')
            foto = st.file_uploader('Foto', type=['png','jpg','jpeg'])
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
                        'Comune': comune,
                        'Lat': lat_v,
                        'Log': lon_v,
                        'Foto': fb
                    })
                    st.success('Salvato')
        if st.session_state.volontari:
            st.dataframe(pd.DataFrame([{'Nome': v['Nome'], 'Comune': v['Comune']} for v in st.session_state.volontari]), use_container_width=True)

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

    elif m == 'Eventi':
        st.markdown('## Eventi')
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

    elif m == 'Mappa Avanzata':
        st.markdown('## Mappa Avanzata')
        st.markdown('### Clicca per marker con icona libreria')

        icona_sel = st.selectbox('Icona da Libreria', ['Nessuna'] + [i['Nome'] for i in st.session_state.icone] if st.session_state.icone else ['Nessuna'])

        try:
            import folium
            from streamlit_folium import st_folium

            if st.session_state.postazioni:
                lat_c = sum([p['Lat'] for p in st.session_state.postazioni]) / len(st.session_state.postazioni)
                lon_c = sum([p['Log'] for p in st.session_state.postazioni]) / len(st.session_state.postazioni)
            else:
                lat_c = 45.65
                lon_c = 8.79

            mapa = folium.Map(location=[lat_c, lon_c], zoom_start=11)

            for p in st.session_state.postazioni:
                folium.Marker([p['Lat'], p['Log']], popup=f"{p['Nome']} - {p.get('Comune','')} - {p.get('Via','')} - {p.get('Icona','')}", icon=folium.Icon(color='blue')).add_to(mapa)

            for tm in st.session_state.temp_markers:
                folium.Marker([tm['lat'], tm['lon']], popup=f"TEMP {tm.get('icona','')}", icon=folium.Icon(color='orange')).add_to(mapa)

            out = st_folium(mapa, height=450, width=700, returned_objects=['last_clicked'])

            if out and out.get('last_clicked'):
                lat_click = out['last_clicked']['lat']
                lon_click = out['last_clicked']['lng']
                st.session_state.temp_markers.append({'lat': lat_click, 'lon': lon_click, 'icona': icona_sel})
                st.session_state.last_clicked = {'lat': lat_click, 'lon': lon_click, 'icona': icona_sel}
                st.success(f'Marker: {lat_click:.5f} {lon_click:.5f} {icona_sel}')

        except Exception as e:
            st.error(f'Errore mappa: {e}')

        last = st.session_state.last_clicked
        if last:
            st.info(f"Click: Lat {last['lat']:.6f} Log {last['lon']:.6f} Icona {last.get('icona','')}")

        with st.form('form_post'):
            nome_p = st.text_input('Nome Postazione *')
            comune_p = st.text_input('Comune *')
            via_p = st.text_input('Via *')
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
                        st.session_state.postazioni.append({'Nome': nome_p, 'Comune': comune_p, 'Via': via_p, 'Icona': icona_p, 'Lat': lat_v, 'Log': lon_v, 'Note': note_p})
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
                    folium.Marker([p['Lat'], p['Log']], popup=f"{p['Nome']} - {p['Comune']}").add_to(m2)
                st_folium(m2, height=350, width=700)
            except:
                pass
        else:
            st.warning('Nessuna postazione')

    elif m == 'Libreria Icone':
        st.markdown('## Libreria Icone')
        with st.form('icone'):
            nome_i = st.text_input('Nome icona *')
            file_i = st.file_uploader('Carica icona', type=['png','svg','jpg','jpeg'])
            if st.form_submit_button('Salva', use_container_width=True, type='primary'):
                if nome_i and file_i:
                    st.session_state.icone.append({'Nome': nome_i, 'FileName': file_i.name, 'FileBytes': file_i.getvalue()})
                    st.success('Icona caricata')
        if st.session_state.icone:
            for idx, ico in enumerate(st.session_state.icone):
                c1,c2 = st.columns([2,2])
                with c1:
                    st.write(ico['Nome'])
                    if ico.get('FileBytes'):
                        st.download_button(f"Download {ico['Nome']}", ico['FileBytes'], file_name=ico['FileName'], key=f"dl_{idx}", use_container_width=True)
                with c2:
                    if st.button('Elimina', key=f"del_{idx}"):
                        st.session_state.icone.pop(idx)
                        st.rerun()