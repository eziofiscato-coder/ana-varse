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
    st.markdown(f'<div style="background:{VERDE};padding:10px;border-radius:8px;color:white;text-align:center;font-weight:bold;">NUCLEO PROT CIVILE ANA VARESE - Squadra Alpini Caronno</div>', unsafe_allow_html=True)

def to_excel(df):
    out = BytesIO()
    cols = [c for c in df.columns if c not in ['Foto','FotoBytes']]
    df[cols].to_excel(out, index=False, engine='openpyxl')
    return out.getvalue()

def to_excel_multi(datasets):
    out = BytesIO()
    with pd.ExcelWriter(out, engine='openpyxl') as writer:
        for nome, df_list in datasets.items():
            if df_list:
                df = pd.DataFrame(df_list)
                cols = [c for c in df.columns if c not in ['Foto','FotoBytes']]
                df[cols].to_excel(writer, sheet_name=nome[:31], index=False)
    return out.getvalue()

def salva_icona_temp(fb, nome):
    try:
        p = os.path.join(tempfile.gettempdir(), f"icon_{nome}.png")
        with open(p,"wb") as f:
            f.write(fb)
        return p
    except:
        return None

# INIT
for k in ['page','logged','menu','volontari','radio_db','eventi','emergenze','checkin','icone','postazioni','last_clicked','temp_markers','brogliaccio','mezzi','attrezzature','map_fullscreen','map_fullscreen2','vol_form_data']:
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
        elif k in ['map_fullscreen','map_fullscreen2']:
            st.session_state[k] = False
        elif k == 'vol_form_data':
            st.session_state[k] = {}
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
                st.image('logo.png', width=200)
            except:
                pass
    st.markdown(f'<h2 style="text-align:center;color:{VERDE};">GESTIONALE PROT CIVILE</h2>', unsafe_allow_html=True)
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
        st.markdown('### MENU - TUTTE LE MASCHERE')
        menu = st.radio('Scegli:', ['Dashboard','Volontari (con foto)','DB Radio','Brogliaccio','Eventi','Emergenze','Check-in','Mezzi','Attrezzature','Mappa Avanzata','Libreria Icone','Backup','Esporta'], index=0)
        st.session_state.menu = menu
        if st.button('Logout', use_container_width=True):
            st.session_state.page = 'entra'
            st.rerun()

    m = st.session_state.menu

    if m == 'Dashboard':
        st.markdown('## Dashboard')
        c1,c2,c3,c4 = st.columns(4)
        c1.metric('Volontari', len(st.session_state.volontari))
        c2.metric('Radio', len(st.session_state.radio_db))
        c3.metric('Eventi', len(st.session_state.eventi))
        c4.metric('Emergenze', len(st.session_state.emergenze))
        c1b,c2b,c3b,c4b = st.columns(4)
        c1b.metric('Check-in', len(st.session_state.checkin))
        c2b.metric('Mezzi', len(st.session_state.mezzi))
        c3b.metric('Attrezzature', len(st.session_state.attrezzature))
        c4b.metric('Postazioni', len(st.session_state.postazioni))

    elif m == 'Volontari (con foto)':
        st.markdown('## VOLONTARI - 5 SOTTOMASCHERE')
        t1,t2,t3,t4,t5 = st.tabs(['1.Anagrafica','2.Contatti','3.Ruolo','4.Foto','5.Elenco'])
        with t1:
            with st.form('vol_anag'):
                nome = st.text_input('Nome *')
                cognome = st.text_input('Cognome *')
                comune = st.text_input('Comune *')
                data_n = st.date_input('Data Nascita', value=date(1980,1,1))
                if st.form_submit_button('Salva Anagrafica', type='primary', use_container_width=True):
                    if nome and cognome and comune:
                        st.session_state.vol_form_data['Nome'] = nome
                        st.session_state.vol_form_data['Cognome'] = cognome
                        st.session_state.vol_form_data['Comune'] = comune
                        st.session_state.vol_form_data['DataNascita'] = str(data_n)
                        st.success('Salvata')
        with t2:
            with st.form('vol_cont'):
                cell = st.text_input('Cellulare *')
                email = st.text_input('Email')
                if st.form_submit_button('Salva Contatti', type='primary', use_container_width=True):
                    if cell:
                        st.session_state.vol_form_data['Cellulare'] = cell
                        st.session_state.vol_form_data['Email'] = email
                        st.success('Salvati')
        with t3:
            with st.form('vol_ruolo'):
                ruolo = st.selectbox('Ruolo *', ['Volontario','Caposquadra','Coordinatore','Autista','Radio','Logistica','Sanitario','Altro'])
                squadra = st.selectbox('Squadra', ['Alpini Caronno','Squadra A','Squadra B','Squadra C'])
                spec = st.multiselect('Specializzazioni', ['AIB','Idro','Neve','Cinofilo','Motosega','Radio'])
                pat = st.multiselect('Patenti', ['B','C','CE','D'])
                if st.form_submit_button('Salva Ruolo', type='primary', use_container_width=True):
                    st.session_state.vol_form_data['Ruolo'] = ruolo
                    st.session_state.vol_form_data['Squadra'] = squadra
                    st.session_state.vol_form_data['Special'] = ','.join(spec)
                    st.session_state.vol_form_data['Patenti'] = ','.join(pat)
                    st.success('Salvato')
        with t4:
            foto = st.file_uploader('Foto *', type=['png','jpg','jpeg'])
            if foto:
                st.image(foto, width=200)
            with st.form('vol_foto'):
                if st.form_submit_button('SALVA VOLONTARIO', type='primary', use_container_width=True):
                    if not st.session_state.vol_form_data.get('Nome'):
                        st.error('Compila Anagrafica')
                    else:
                        v = {}
                        v['Nome'] = st.session_state.vol_form_data.get('Nome','')
                        v['Cognome'] = st.session_state.vol_form_data.get('Cognome','')
                        v['Comune'] = st.session_state.vol_form_data.get('Comune','')
                        v['Cellulare'] = st.session_state.vol_form_data.get('Cellulare','')
                        v['Ruolo'] = st.session_state.vol_form_data.get('Ruolo','')
                        v['Squadra'] = st.session_state.vol_form_data.get('Squadra','')
                        v['Special'] = st.session_state.vol_form_data.get('Special','')
                        v['FotoBytes'] = foto.getvalue() if foto else None
                        st.session_state.volontari.append(v)
                        st.session_state.vol_form_data = {}
                        st.success('Volontario salvato!')
                        st.balloons()
        with t5:
            if st.session_state.volontari:
                df = pd.DataFrame(st.session_state.volontari)
                st.dataframe(df, use_container_width=True)
                st.download_button('Excel', to_excel(df), file_name='volontari.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    elif m == 'DB Radio':
        st.markdown('## DB Radio - MASCHERA')
        with st.form('radio_form'):
            modello = st.text_input('Modello *')
            matricola = st.text_input('Matricola *')
            tipo = st.selectbox('Tipo *', ['DMR','PMR446','TETRA','VHF','UHF','CB','Altro'])
            freq = st.text_input('Frequenza')
            canale = st.text_input('Canale')
            stato_r = st.selectbox('Stato', ['Disponibile','In Uso','Manutenzione'])
            note_r = st.text_area('Note')
            if st.form_submit_button('Salva Radio', type='primary', use_container_width=True):
                if modello and matricola:
                    r = {}
                    r['Modello'] = modello
                    r['Matricola'] = matricola
                    r['Tipo'] = tipo
                    r['Frequenza'] = freq
                    r['Canale'] = canale
                    r['Stato'] = stato_r
                    r['Note'] = note_r
                    st.session_state.radio_db.append(r)
                    st.success('Radio salvata')
        if st.session_state.radio_db:
            st.dataframe(pd.DataFrame(st.session_state.radio_db), use_container_width=True)

    elif m == 'Brogliaccio':
        st.markdown('## Brogliaccio - MASCHERA')
        with st.form('brog_form'):
            mitt = st.text_input('Mittente *')
            dest = st.text_input('Destinatario *')
            msg = st.text_area('Messaggio *')
            if st.form_submit_button('Salva', type='primary', use_container_width=True):
                if mitt and dest and msg:
                    b = {}
                    b['Data'] = str(date.today())
                    b['Mittente'] = mitt
                    b['Destinatario'] = dest
                    b['Messaggio'] = msg
                    st.session_state.brogliaccio.append(b)
                    st.success('Salvato')
        if st.session_state.brogliaccio:
            st.dataframe(pd.DataFrame(st.session_state.brogliaccio), use_container_width=True)

    elif m == 'Eventi':
        st.markdown('## Eventi - MASCHERA')
        with st.form('eventi_form'):
            nome_e = st.text_input('NOME EVENTO *')
            luogo_e = st.text_input('Luogo *')
            if st.form_submit_button('Crea Evento', type='primary', use_container_width=True):
                if nome_e and luogo_e:
                    e = {}
                    e['NomeEvento'] = nome_e
                    e['Luogo'] = luogo_e
                    e['Data'] = str(date.today())
                    st.session_state.eventi.append(e)
                    st.success('Evento creato')
        if st.session_state.eventi:
            st.dataframe(pd.DataFrame(st.session_state.eventi), use_container_width=True)

    elif m == 'Emergenze':
        st.markdown('## Emergenze - MASCHERA')
        with st.form('em_form'):
            tipo_em = st.selectbox('Tipo *', ['Alluvione','Frana','Incendio','Terremoto','Neve','Ricerca','Altro'])
            luogo_em = st.text_input('Luogo *')
            descr_em = st.text_area('Descrizione *')
            if st.form_submit_button('Attiva', type='primary', use_container_width=True):
                if luogo_em and descr_em:
                    em = {}
                    em['Tipo'] = tipo_em
                    em['Luogo'] = luogo_em
                    em['Descrizione'] = descr_em
                    em['Data'] = str(date.today())
                    st.session_state.emergenze.append(em)
                    st.success('Attivata')
        if st.session_state.emergenze:
            st.dataframe(pd.DataFrame(st.session_state.emergenze), use_container_width=True)

    elif m == 'Check-in':
        st.markdown('## Check-in - MASCHERA')
        if st.session_state.eventi and st.session_state.volontari:
            with st.form('check_form'):
                ev_sel = st.selectbox('EVENTO *', [e['NomeEvento'] for e in st.session_state.eventi])
                vol_sel = st.selectbox('Volontario *', [f"{v['Nome']} {v['Cognome']}" for v in st.session_state.volontari])
                post_sel = st.selectbox('Postazione *', ['Base','Avanzata'] + [p['Nome'] for p in st.session_state.postazioni] if st.session_state.postazioni else ['Base','Avanzata'])
                if st.form_submit_button('Registra', type='primary', use_container_width=True):
                    c = {}
                    c['NomeEvento'] = ev_sel
                    c['Volontario'] = vol_sel
                    c['Postazione'] = post_sel
                    c['Data'] = str(date.today())
                    st.session_state.checkin.append(c)
                    st.success('Registrato')
        if st.session_state.checkin:
            st.dataframe(pd.DataFrame(st.session_state.checkin), use_container_width=True)

    elif m == 'Mezzi':
        st.markdown('## Mezzi - MASCHERA')
        with st.form('mezzi_form'):
            targa = st.text_input('Targa *')
            tipo_m = st.selectbox('Tipo *', ['Fuoristrada','Furgone','Autocarro','Ambulanza','Pulmino','Altro'])
            if st.form_submit_button('Salva', type='primary', use_container_width=True):
                if targa and tipo_m:
                    mz = {}
                    mz['Targa'] = targa
                    mz['Tipo'] = tipo_m
                    st.session_state.mezzi.append(mz)
                    st.success('Salvato')
        if st.session_state.mezzi:
            st.dataframe(pd.DataFrame(st.session_state.mezzi), use_container_width=True)

    elif m == 'Attrezzature':
        st.markdown('## Attrezzature - MASCHERA')
        with st.form('attr_form'):
            nome_a = st.text_input('Attrezzatura *')
            quant = st.number_input('Quantita *', min_value=1, value=1)
            if st.form_submit_button('Salva', type='primary', use_container_width=True):
                if nome_a:
                    at = {}
                    at['Attrezzatura'] = nome_a
                    at['Quantita'] = quant
                    st.session_state.attrezzature.append(at)
                    st.success('Salvata')
        if st.session_state.attrezzature:
            st.dataframe(pd.DataFrame(st.session_state.attrezzature), use_container_width=True)

    elif m == 'Mappa Avanzata':
        st.markdown('## Mappa Avanzata - BUON LAVORO RIPRISTINATO')
        st.info('OSM default, fullscreen + - ESC, click coordinate, icona marker')
        c1,c2,c3 = st.columns([2,2,1])
        with c1:
            map_type = st.selectbox('Tipo Mappa', ['OpenStreetMap','Google Map','Google Satellite'], index=0)
        with c2:
            icona_sel = st.selectbox('Icona', ['Nessuna'] + [i['Nome'] for i in st.session_state.icone] if st.session_state.icone else ['Nessuna'])
        with c3:
            lab = 'Riduci' if st.session_state.map_fullscreen else 'Espandi'
            if st.button(lab, key='exp1', use_container_width=True):
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
                    url = f'https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=18'
                    r = requests.get(url, headers={'User-Agent':'ANA'}, timeout=5)
                    if r.status_code == 200:
                        d = r.json()
                        a = d.get('address',{})
                        c = a.get('city') or a.get('town') or ''
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
                folium.TileLayer('openstreetmap').add_to(mm)
            elif map_type == 'Google Map':
                folium.TileLayer(tiles='https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}', attr='Google').add_to(mm)
            else:
                folium.TileLayer(tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', attr='Google').add_to(mm)
            Fullscreen(position='topleft', title='Espandi', title_cancel='Esci ESC', force_separate_button=True).add_to(mm)
            for p in st.session_state.postazioni:
                lat_f = p['Lat']
                lon_f = p['Log']
                popup = f"<b>{p['Nome']}</b><br>{p.get('Comune','')}"
                p_icon = p.get('Icona','Nessuna')
                use_path = None
                if p_icon!= 'Nessuna':
                    ico = next((i for i in st.session_state.icone if i['Nome'] == p_icon), None)
                    if ico and ico.get('FileBytes'):
                        use_path = salva_icona_temp(ico['FileBytes'], p_icon)
                if use_path:
                    folium.Marker([lat_f, lon_f], popup=popup, icon=folium.CustomIcon(use_path, icon_size=(40,40))).add_to(mm)
                else:
                    folium.Marker([lat_f, lon_f], popup=popup, icon=folium.Icon(color='green')).add_to(mm)
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
                st.success(f"Click {lat_c:.5f} {lon_c:.5f}")
                st.rerun()
        except Exception as e:
            st.error(f"Errore mappa: {e}")
        last = st.session_state.last_clicked
        if last:
            st.info(f"Click: {last['lat']:.6f} {last['lon']:.6f} {last.get('comune','')}")
        with st.form('form_post'):
            nome_p = st.text_input('Nome Postazione *')
            comune_p = st.text_input('Comune *', value=last.get('comune','') if last else '')
            lat_p = st.text_input('Lat *', value=str(last['lat']) if last else '')
            lon_p = st.text_input('Log *', value=str(last['lon']) if last else '')
            lista_icone = ['Nessuna'] + [i['Nome'] for i in st.session_state.icone] if st.session_state.icone else ['Nessuna']
            icona_p = st.selectbox('Icona', lista_icone)
            if st.form_submit_button('Salva Postazione', type='primary', use_container_width=True):
                if nome_p and comune_p and lat_p and lon_p:
                    try:
                        lat_v = float(lat_p.replace(',','.'))
                        lon_v = float(lon_p.replace(',','.'))
                        np = {}
                        np['Nome'] = nome_p
                        np['Comune'] = comune_p
                        np['Icona'] = icona_p
                        np['Lat'] = lat_v
                        np['Log'] = lon_v
                        st.session_state.postazioni.append(np)
                        st.session_state.temp_markers = []
                        st.session_state.last_clicked = None
                        st.success('Postazione salvata')
                        st.rerun()
                    except:
                        st.error('Lat/Log non validi')
        st.divider()
        lab2 = 'Riduci Mappa 2' if st.session_state.map_fullscreen2 else 'Espandi Mappa 2'
        if st.button(lab2, key='exp2', use_container_width=True):
            st.session_state.map_fullscreen2 = not st.session_state.map_fullscreen2
            st.rerun()
        h2 = 800 if st.session_state.map_fullscreen2 else 400
        if st.session_state.postazioni:
            df_post = pd.DataFrame(st.session_state.postazioni)
            st.dataframe(df_post, use_container_width=True)
            st.download_button('Excel Postazioni', to_excel(df_post), file_name='postazioni.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', use_container_width=True)
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
                st.error(f"Errore mappa2 {e}")

    elif m == 'Libreria Icone':
        st.markdown('## Libreria Icone - MASCHERA')
        with st.form('icone_form'):
            nome_i = st.text_input('Nome icona *')
            file_i = st.file_uploader('Carica PNG/JPG *', type=['png','jpg','jpeg'])
            if file_i:
                st.image(file_i, width=120, caption='Preview')
            if st.form_submit_button('Salva Icona', type='primary', use_container_width=True):
                if nome_i and file_i:
                    ni = {}
                    ni['Nome'] = nome_i
                    ni['FileName'] = file_i.name
                    ni['FileBytes'] = file_i.getvalue()
                    st.session_state.icone.append(ni)
                    st.success('Icona caricata')
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
        st.markdown('## BACKUP - IMPORT EXPORT TUTTI I DATI')
        st.success('Backup con EXPORT e IMPORT di TUTTI i dati di TUTTI i form')
        datasets = {}
        datasets['Volontari'] = st.session_state.volontari
        datasets['Radio'] = st.session_state.radio_db
        datasets['Brogliaccio'] = st.session_state.brogliaccio
        datasets['Eventi'] = st.session_state.eventi
        datasets['Emergenze'] = st.session_state.emergenze
        datasets['Checkin'] = st.session_state.checkin
        datasets['Mezzi'] = st.session_state.mezzi
        datasets['Attrezzature'] = st.session_state.attrezzature
        datasets['Postazioni'] = st.session_state.postazioni
        st.markdown('### 1. EXPORT DI TUTTI I DATI')
        c1,c2 = st.columns(2)
        with c1:
            if any(datasets.values()):
                st.download_button('📥 EXPORT TOTALE EXCEL', to_excel_multi(datasets), file_name=f'backup_TUTTI_{date.today()}.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', use_container_width=True, type='primary')
                jd = {}
                for k in ['volontari','radio_db','brogliaccio','eventi','emergenze','checkin','mezzi','attrezzature','postazioni']:
                    jd[k] = [{kk: vv for kk, vv in item.items() if kk not in ['FotoBytes']} for item in st.session_state[k]]
                st.download_button('📥 EXPORT TOTALE JSON', json.dumps(jd, indent=2, ensure_ascii=False), file_name=f'backup_TUTTI_{date.today()}.json', mime='application/json', use_container_width=True)
        with c2:
            st.markdown('**IMPORT DI TUTTI I DATI**')
            f_excel = st.file_uploader('Carica Excel TUTTI', type=['xlsx'], key='import_tot_excel')
            if f_excel:
                try:
                    xls = pd.ExcelFile(f_excel)
                    if st.button('CONFERMA IMPORT EXCEL', type='primary', use_container_width=True, key='conf_tot_excel'):
                        for sheet in xls.sheet_names:
                            df = pd.read_excel(xls, sheet_name=sheet)
                            s_low = sheet.lower()
                            if 'volontar' in s_low:
                                st.session_state.volontari = df.to_dict('records')
                            elif 'radio' in s_low:
                                st.session_state.radio_db = df.to_dict('records')
                            elif 'brogliaccio' in s_low:
                                st.session_state.brogliaccio = df.to_dict('records')
                            elif 'event' in s_low:
                                st.session_state.eventi = df.to_dict('records')
                            elif 'emergenz' in s_low:
                                st.session_state.emergenze = df.to_dict('records')
                            elif 'checkin' in s_low:
                                st.session_state.checkin = df.to_dict('records')
                            elif 'mezz' in s_low:
                                st.session_state.mezzi = df.to_dict('records')
                            elif 'attrezz' in s_low:
                                st.session_state.attrezzature = df.to_dict('records')
                            elif 'postaz' in s_low:
                                st.session_state.postazioni = df.to_dict('records')
                        st.success('Import completato!')
                        st.rerun()
                except Exception as e:
                    st.error(f'Errore: {e}')
            f_json = st.file_uploader('Carica JSON TUTTI', type=['json'], key='import_tot_json')
            if f_json:
                try:
                    data = json.loads(f_json.getvalue().decode('utf-8'))
                    if st.button('CONFERMA IMPORT JSON', type='primary', use_container_width=True, key='conf_tot_json'):
                        for k in ['volontari','radio_db','brogliaccio','eventi','emergenze','checkin','mezzi','attrezzature','postazioni']:
                            if k in data:
                                st.session_state[k] = data[k]
                        st.success('Import JSON completato!')
                        st.rerun()
                except Exception as e:
                    st.error(f'Errore JSON: {e}')
        st.divider()
        st.markdown('### 2. PER SINGOLO FORM')
        forms_b = [('volontari','Volontari'),('radio_db','DB Radio'),('brogliaccio','Brogliaccio'),('eventi','Eventi'),('emergenze','Emergenze'),('checkin','Check-in'),('mezzi','Mezzi'),('attrezzature','Attrezzature'),('postazioni','Postazioni')]
        for key, titolo in forms_b:
            with st.expander(f"{titolo} - {len(st.session_state[key])} record"):
                c1,c2,c3 = st.columns([1,1,1])
                with c1:
                    if st.session_state[key]:
                        df = pd.DataFrame(st.session_state[key])
                        st.download_button(f'Excel {titolo}', to_excel(df), file_name=f'{key}.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', key=f'ex_{key}', use_container_width=True)
                with c2:
                    fu = st.file_uploader(f'Carica Excel {titolo}', type=['xlsx','xls'], key=f'imp_excel_{key}')
                    if fu:
                        try:
                            df_imp = pd.read_excel(fu)
                            if st.button(f'Conferma Import {titolo}', key=f'conf_excel_{key}', use_container_width=True, type='primary'):
                                st.session_state[key] = df_imp.to_dict('records')
                                st.success(f'Import {titolo} OK')
                                st.rerun()
                        except Exception as e:
                            st.error(f'Errore: {e}')
                with c3:
                    if st.button(f"Cancella {titolo}", key=f'del_{key}', use_container_width=True):
                        st.session_state[key] = []
                        st.rerun()

    elif m == 'Esporta':
        st.markdown('## Esporta Rapido')
        for key, titolo in [('volontari','Volontari'),('radio_db','Radio'),('eventi','Eventi'),('emergenze','Emergenze'),('checkin','Check-in'),('postazioni','Postazioni')]:
            if st.session_state[key]:
                df = pd.DataFrame(st.session_state[key])
                c1,c2 = st.columns(2)
                c1.download_button(f"Excel {titolo}", to_excel(df), file_name=f"{key}.xlsx", mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', key=f"ex2_{key}", use_container_width=True)