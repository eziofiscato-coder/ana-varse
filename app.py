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
    st.markdown(f'<div style="background:{VERDE};padding:10px;border-radius:8px;color:white;text-align:center;font-weight:bold;">NUCLEO PROT CIVILE ANA VARESE</div>', unsafe_allow_html=True)

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

for k in ['page','logged','menu','volontari','radio_db','eventi','emergenze','checkin','icone','postazioni','last_clicked','temp_markers','brogliaccio','mezzi','attrezzature','map_fullscreen','map_fullscreen2','vol_form_data','custom_defs','custom_data']:
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
        elif k == 'custom_defs':
            st.session_state[k] = {}
        elif k == 'custom_data':
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
    st.markdown(f'<h2 style="text-align:center;color:{VERDE};">GESTIONALE</h2>', unsafe_allow_html=True)
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
    menu_base = ['Dashboard','Volontari (con foto)','DB Radio','Brogliaccio','Eventi','Emergenze','Check-in','Mezzi','Attrezzature','Mappa Avanzata','Libreria Icone','Backup','Esporta','Crea Nuovo Form']
    menu_custom = list(st.session_state.custom_defs.keys())
    menu_tot = menu_base + menu_custom
    with st.sidebar:
        st.markdown('### MENU')
        menu = st.radio('Scegli:', menu_tot, index=0)
        st.session_state.menu = menu
        if st.button('Logout', use_container_width=True):
            st.session_state.page = 'entra'
            st.rerun()

    m = st.session_state.menu

    if m == 'Dashboard':
        st.markdown('## Dashboard - TASTI RAPIDI OK')
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
        st.divider()
        st.markdown('### MENU RAPIDO - CLICCA E APRE FORM')
        r1 = st.columns(4)
        with r1[0]:
            if st.button('VOLONTARI', use_container_width=True, type='primary'):
                st.session_state.menu = 'Volontari (con foto)'
                st.rerun()
        with r1[1]:
            if st.button('DB RADIO', use_container_width=True, type='primary'):
                st.session_state.menu = 'DB Radio'
                st.rerun()
        with r1[2]:
            if st.button('BROGLIACCIO', use_container_width=True, type='primary'):
                st.session_state.menu = 'Brogliaccio'
                st.rerun()
        with r1[3]:
            if st.button('EVENTI', use_container_width=True, type='primary'):
                st.session_state.menu = 'Eventi'
                st.rerun()
        r2 = st.columns(4)
        with r2[0]:
            if st.button('EMERGENZE', use_container_width=True, type='primary'):
                st.session_state.menu = 'Emergenze'
                st.rerun()
        with r2[1]:
            if st.button('CHECK-IN', use_container_width=True, type='primary'):
                st.session_state.menu = 'Check-in'
                st.rerun()
        with r2[2]:
            if st.button('MEZZI', use_container_width=True, type='primary'):
                st.session_state.menu = 'Mezzi'
                st.rerun()
        with r2[3]:
            if st.button('ATTREZZATURE', use_container_width=True, type='primary'):
                st.session_state.menu = 'Attrezzature'
                st.rerun()
        r3 = st.columns(4)
        with r3[0]:
            if st.button('MAPPA AVANZATA', use_container_width=True, type='primary'):
                st.session_state.menu = 'Mappa Avanzata'
                st.rerun()
        with r3[1]:
            if st.button('LIBRERIA ICONE', use_container_width=True, type='primary'):
                st.session_state.menu = 'Libreria Icone'
                st.rerun()
        with r3[2]:
            if st.button('BACKUP', use_container_width=True, type='primary'):
                st.session_state.menu = 'Backup'
                st.rerun()
        with r3[3]:
            if st.button('ESPORTA', use_container_width=True, type='primary'):
                st.session_state.menu = 'Esporta'
                st.rerun()
        r4 = st.columns(4)
        with r4[0]:
            if st.button('CREA NUOVO FORM', use_container_width=True, type='primary'):
                st.session_state.menu = 'Crea Nuovo Form'
                st.rerun()
        with r4[1]:
            for cf in menu_custom:
                if st.button(f'Apri {cf}', key=f'rapido_{cf}', use_container_width=True):
                    st.session_state.menu = cf
                    st.rerun()

    elif m == 'Volontari (con foto)':
        st.markdown('## VOLONTARI')
        t1,t2,t3,t4,t5 = st.tabs(['1.Anagrafica','2.Contatti','3.Ruolo','4.Foto','5.Elenco'])
        with t1:
            with st.form('vol_anag'):
                nome = st.text_input('Nome *')
                cognome = st.text_input('Cognome *')
                comune = st.text_input('Comune *')
                if st.form_submit_button('Salva', type='primary', use_container_width=True):
                    if nome and cognome and comune:
                        st.session_state.vol_form_data['Nome'] = nome
                        st.session_state.vol_form_data['Cognome'] = cognome
                        st.session_state.vol_form_data['Comune'] = comune
                        st.success('Salvata')
        with t2:
            with st.form('vol_cont'):
                cell = st.text_input('Cellulare *')
                if st.form_submit_button('Salva', type='primary', use_container_width=True):
                    if cell:
                        st.session_state.vol_form_data['Cellulare'] = cell
                        st.success('Salvati')
        with t3:
            with st.form('vol_ruolo'):
                ruolo = st.selectbox('Ruolo *', ['Volontario','Caposquadra','Coordinatore','Autista','Radio','Logistica','Sanitario','Altro'])
                squadra = st.selectbox('Squadra', ['Alpini Caronno','Squadra A','Squadra B'])
                spec = st.multiselect('Specializzazioni', ['AIB','Idro','Neve','Cinofilo','Motosega','Radio'])
                if st.form_submit_button('Salva', type='primary', use_container_width=True):
                    st.session_state.vol_form_data['Ruolo'] = ruolo
                    st.session_state.vol_form_data['Squadra'] = squadra
                    st.session_state.vol_form_data['Special'] = ','.join(spec)
                    st.success('Salvato')
        with t4:
            foto = st.file_uploader('Foto', type=['png','jpg','jpeg'])
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
                        st.success('Salvato!')
                        st.balloons()
        with t5:
            if st.session_state.volontari:
                st.dataframe(pd.DataFrame(st.session_state.volontari), use_container_width=True)
                st.download_button('Excel', to_excel(pd.DataFrame(st.session_state.volontari)), file_name='volontari.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    elif m == 'DB Radio':
        st.markdown('## DB Radio')
        with st.form('radio_form'):
            modello = st.text_input('Modello *')
            matricola = st.text_input('Matricola *')
            tipo = st.selectbox('Tipo *', ['DMR','PMR446','TETRA','VHF','UHF','CB','Altro'])
            freq = st.text_input('Frequenza')
            canale = st.text_input('Canale')
            stato_r = st.selectbox('Stato', ['Disponibile','In Uso','Manutenzione'])
            note_r = st.text_area('Note')
            if st.form_submit_button('Salva', type='primary', use_container_width=True):
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
                    st.success('Salvata')
        if st.session_state.radio_db:
            st.dataframe(pd.DataFrame(st.session_state.radio_db), use_container_width=True)

    elif m == 'Brogliaccio':
        st.markdown('## Brogliaccio')
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
        st.markdown('## Eventi')
        with st.form('eventi_form'):
            nome_e = st.text_input('NOME EVENTO *')
            luogo_e = st.text_input('Luogo *')
            if st.form_submit_button('Crea', type='primary', use_container_width=True):
                if nome_e and luogo_e:
                    e = {}
                    e['NomeEvento'] = nome_e
                    e['Luogo'] = luogo_e
                    e['Data'] = str(date.today())
                    st.session_state.eventi.append(e)
                    st.success('Creato')
        if st.session_state.eventi:
            st.dataframe(pd.DataFrame(st.session_state.eventi), use_container_width=True)

    elif m == 'Emergenze':
        st.markdown('## Emergenze')
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
        st.markdown('## Check-in')
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
        st.markdown('## Mezzi')
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
        st.markdown('## Attrezzature')
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
        st.markdown('## Mappa Avanzata')
        st.info('OSM default, fullscreen + - ESC, click coord, icona marker')
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

    elif m == 'Libreria Icone':
        st.markdown('## Libreria Icone')
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
        for cf_name, cf_data in st.session_state.custom_data.items():
            datasets[cf_name] = cf_data
        st.markdown('### EXPORT DI TUTTI I DATI')
        c1,c2 = st.columns(2)
        with c1:
            if any(datasets.values()):
                st.download_button('📥 EXPORT TOTALE EXCEL', to_excel_multi(datasets), file_name=f'backup_TUTTI_{date.today()}.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', use_container_width=True, type='primary')
                jd = {}
                for k in ['volontari','radio_db','brogliaccio','eventi','emergenze','checkin','mezzi','attrezzature','postazioni']:
                    jd[k] = [{kk: vv for kk, vv in item.items() if kk not in ['FotoBytes']} for item in st.session_state[k]]
                jd['custom_defs'] = st.session_state.custom_defs
                jd['custom_data'] = {k: [{kk: vv for kk, vv in item.items() if kk not in ['FotoBytes']} for item in v] for k,v in st.session_state.custom_data.items()}
                st.download_button('📥 EXPORT TOTALE JSON', json.dumps(jd, indent=2, ensure_ascii=False), file_name=f'backup_TUTTI_{date.today()}.json', mime='application/json', use_container_width=True)
        with c2:
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
                            else:
                                st.session_state.custom_data[sheet] = df.to_dict('records')
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
                        if 'custom_defs' in data:
                            st.session_state.custom_defs = data['custom_defs']
                        if 'custom_data' in data:
                            st.session_state.custom_data = data['custom_data']
                        st.success('Import JSON completato!')
                        st.rerun()
                except Exception as e:
                    st.error(f'Errore JSON: {e}')

    elif m == 'Crea Nuovo Form':
        st.markdown('## CREA NUOVO FORM')
        st.success('Qui crei nuovi form senza perdere quelli vecchi!')
        with st.form('new_form_def'):
            nome_nuovo = st.text_input('Nome nuovo form *')
            descr_nuovo = st.text_area('Descrizione')
            if st.form_submit_button('Crea Form Vuoto', type='primary', use_container_width=True):
                if nome_nuovo:
                    if nome_nuovo not in st.session_state.custom_defs:
                        st.session_state.custom_defs[nome_nuovo] = {}
                        st.session_state.custom_defs[nome_nuovo]['descrizione'] = descr_nuovo
                        st.session_state.custom_defs[nome_nuovo]['campi'] = []
                        st.session_state.custom_data[nome_nuovo] = []
                        st.success(f'Form {nome_nuovo} creato!')
                        st.rerun()
                    else:
                        st.error('Form gia esistente')
        if st.session_state.custom_defs:
            form_sel = st.selectbox('Seleziona form', list(st.session_state.custom_defs.keys()))
            if form_sel:
                campi = st.session_state.custom_defs[form_sel]['campi']
                if campi:
                    st.dataframe(pd.DataFrame(campi), use_container_width=True)
                c1,c2,c3 = st.columns(3)
                with c1:
                    nome_campo = st.text_input('Nome campo *', key='nc_nome')
                    tipo_campo = st.selectbox('Tipo *', ['Testo','Numero','Data','Ora','Select','Multiselect','Telefono','Email','Note'], key='nc_tipo')
                with c2:
                    obb = st.checkbox('Obbligatorio *', key='nc_obb')
                    opzioni = st.text_input('Opzioni separate da virgola', key='nc_opt')
                with c3:
                    if st.button('Aggiungi Campo', type='primary', use_container_width=True, key='btn_add_campo'):
                        if nome_campo:
                            nc = {}
                            nc['nome'] = nome_campo
                            nc['tipo'] = tipo_campo
                            nc['obbligatorio'] = obb
                            nc['opzioni'] = [o.strip() for o in opzioni.split(',')] if opzioni else []
                            st.session_state.custom_defs[form_sel]['campi'].append(nc)
                            st.success(f'Campo {nome_campo} aggiunto')
                            st.rerun()
                if st.button(f'Elimina ultimo campo di {form_sel}', use_container_width=True):
                    if campi:
                        st.session_state.custom_defs[form_sel]['campi'].pop()
                        st.rerun()
                if st.button(f'Elimina form {form_sel} completo', use_container_width=True):
                    del st.session_state.custom_defs[form_sel]
                    if form_sel in st.session_state.custom_data:
                        del st.session_state.custom_data[form_sel]
                    st.success('Eliminato')
                    st.rerun()
        st.divider()
        c1,c2,c3 = st.columns(3)
        with c1:
            if st.button('Esempio: TESSERAMENTO', use_container_width=True):
                d = {}
                d['descrizione'] = 'Tesseramento soci'
                d['campi'] = []
                d['campi'].append({'nome': 'Nome Cognome', 'tipo': 'Testo', 'obbligatorio': True, 'opzioni': []})
                d['campi'].append({'nome': 'Numero Tessera', 'tipo': 'Testo', 'obbligatorio': True, 'opzioni': []})
                d['campi'].append({'nome': 'Data Iscrizione', 'tipo': 'Data', 'obbligatorio': True, 'opzioni': []})
                d['campi'].append({'nome': 'Quota', 'tipo': 'Select', 'obbligatorio': True, 'opzioni': ['20 Euro','30 Euro','50 Euro']})
                d['campi'].append({'nome': 'Telefono', 'tipo': 'Telefono', 'obbligatorio': False, 'opzioni': []})
                st.session_state.custom_defs['Tesseramento'] = d
                st.session_state.custom_data['Tesseramento'] = []
                st.success('Creato!')
                st.rerun()
        with c2:
            if st.button('Esempio: CORSI', use_container_width=True):
                d = {}
                d['descrizione'] = 'Corsi'
                d['campi'] = []
                d['campi'].append({'nome': 'Corso', 'tipo': 'Testo', 'obbligatorio': True, 'opzioni': []})
                d['campi'].append({'nome': 'Partecipante', 'tipo': 'Testo', 'obbligatorio': True, 'opzioni': []})
                d['campi'].append({'nome': 'Data Corso', 'tipo': 'Data', 'obbligatorio': True, 'opzioni': []})
                d['campi'].append({'nome': 'Esito', 'tipo': 'Select', 'obbligatorio': True, 'opzioni': ['Superato','Non Superato','In corso']})
                st.session_state.custom_defs['Corsi Formazione'] = d
                st.session_state.custom_data['Corsi Formazione'] = []
                st.success('Creato!')
                st.rerun()
        with c3:
            if st.button('Esempio: MAGAZZINO', use_container_width=True):
                d = {}
                d['descrizione'] = 'Carico scarico'
                d['campi'] = []
                d['campi'].append({'nome': 'Articolo', 'tipo': 'Testo', 'obbligatorio': True, 'opzioni': []})
                d['campi'].append({'nome': 'Quantita', 'tipo': 'Numero', 'obbligatorio': True, 'opzioni': []})
                d['campi'].append({'nome': 'Movimento', 'tipo': 'Select', 'obbligatorio': True, 'opzioni': ['Carico','Scarico']})
                d['campi'].append({'nome': 'Data', 'tipo': 'Data', 'obbligatorio': True, 'opzioni': []})
                st.session_state.custom_defs['Magazzino'] = d
                st.session_state.custom_data['Magazzino'] = []
                st.success('Creato!')
                st.rerun()

    elif m in st.session_state.custom_defs:
        def_form = st.session_state.custom_defs[m]
        st.markdown(f'## {m} - FORM PERSONALIZZATO')
        with st.form(f'form_{m}'):
            st.markdown(f'### Maschera {m}')
            valori = {}
            for campo in def_form.get('campi',[]):
                nome_c = campo['nome']
                tipo_c = campo['tipo']
                obb = campo['obbligatorio']
                label = f"{nome_c} {'*' if obb else ''}"
                if tipo_c == 'Testo':
                    valori[nome_c] = st.text_input(label)
                elif tipo_c == 'Numero':
                    valori[nome_c] = st.number_input(label, step=1)
                elif tipo_c == 'Data':
                    valori[nome_c] = str(st.date_input(label, value=date.today()))
                elif tipo_c == 'Ora':
                    valori[nome_c] = st.text_input(label, value=datetime.now().strftime('%H:%M'))
                elif tipo_c == 'Telefono':
                    valori[nome_c] = st.text_input(label)
                elif tipo_c == 'Email':
                    valori[nome_c] = st.text_input(label)
                elif tipo_c == 'Note':
                    valori[nome_c] = st.text_area(label)
                elif tipo_c == 'Select':
                    opts = campo.get('opzioni',[])
                    if opts:
                        valori[nome_c] = st.selectbox(label, opts)
                    else:
                        valori[nome_c] = st.text_input(label)
                elif tipo_c == 'Multiselect':
                    opts = campo.get('opzioni',[])
                    if opts:
                        sel = st.multiselect(label, opts)
                        valori[nome_c] = ','.join(sel)
                    else:
                        valori[nome_c] = st.text_input(label)
            if st.form_submit_button(f'Salva in {m}', type='primary', use_container_width=True):
                ok = True
                for campo in def_form.get('campi',[]):
                    if campo['obbligatorio']:
                        if not valori.get(campo['nome']):
                            ok = False
                if ok:
                    valori['DataIns'] = str(date.today())
                    if m not in st.session_state.custom_data:
                        st.session_state.custom_data[m] = []
                    st.session_state.custom_data[m].append(valori)
                    st.success(f'Salvato in {m}!')
                else:
                    st.error('Compila campi *')
        if st.session_state.custom_data.get(m):
            df = pd.DataFrame(st.session_state.custom_data[m])
            st.dataframe(df, use_container_width=True)
            st.download_button(f'Excel {m}', to_excel(df), file_name=f'{m}.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', use_container_width=True)

    elif m == 'Esporta':
        st.markdown('## Esporta Rapido')
        for key, titolo in [('volontari','Volontari'),('radio_db','Radio'),('eventi','Eventi'),('emergenze','Emergenze'),('checkin','Check-in'),('postazioni','Postazioni')]:
            if st.session_state[key]:
                df = pd.DataFrame(st.session_state[key])
                st.download_button(f"Excel {titolo}", to_excel(df), file_name=f"{key}.xlsx", mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', key=f"ex2_{key}", use_container_width=True)