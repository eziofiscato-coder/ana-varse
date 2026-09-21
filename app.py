import streamlit as st
import pandas as pd
import os
from io import BytesIO
from datetime import date, datetime
import tempfile

st.set_page_config(page_title='ANA Varese', layout='wide')

VERDE = "#1A5D1A"

st.markdown(f"""
<style>
h1,h2,h3 {{ color: {VERDE}!important; }}
.stButton>button {{
  background:{VERDE}!important;
  color:white!important;
}}
</style>
""", unsafe_allow_html=True)

def hdr():
    st.markdown(
        f'<div style="background:{VERDE};'
        f'padding:8px;border-radius:8px;'
        f'color:white;text-align:center;">'
        f'NUCLEO PROT CIVILE ANA VARESE</div>',
        unsafe_allow_html=True
    )

def to_excel(df):
    out = BytesIO()
    cols = [c for c in df.columns if c not in ['Foto','FileBytes']]
    df[cols].to_excel(out, index=False, engine='openpyxl')
    return out.getvalue()

def salva_icona_temp(fb, nome):
    try:
        p = os.path.join(tempfile.gettempdir(), f"icon_{nome}.png")
        with open(p,"wb") as f:
            f.write(fb)
        return p
    except:
        return None

for k in ['page','logged','menu','volontari','radio_db','eventi','emergenze','checkin','icone','postazioni','last_clicked','temp_markers','brogliaccio','map_fullscreen','map_fullscreen2']:
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
    with st.sidebar:
        menu = st.radio('Menu', ['Dashboard','Volontari','DB Radio','Eventi','Emergenze','Check-in','Mappa Avanzata','Libreria Icone','Backup'], index=0)
        st.session_state.menu = menu
        if st.button('Logout'):
            st.session_state.page = 'entra'
            st.rerun()

    m = st.session_state.menu

    if m == 'Dashboard':
        st.write('## Dashboard - Menu Completo')
        c1,c2,c3,c4 = st.columns(4)
        c1.metric('Volontari', len(st.session_state.volontari))
        c2.metric('Eventi', len(st.session_state.eventi))
        c3.metric('Emergenze', len(st.session_state.emergenze))
        c4.metric('Postazioni', len(st.session_state.postazioni))
        st.divider()
        r1 = st.columns(4)
        with r1[0]:
            if st.button('VOLONTARI', use_container_width=True):
                st.session_state.menu = 'Volontari'
                st.rerun()
        with r1[1]:
            if st.button('EMERGENZE', use_container_width=True):
                st.session_state.menu = 'Emergenze'
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
        st.write('## Volontari')
        with st.form('vol1'):
            nome = st.text_input('Nome *')
            comune = st.text_input('Comune *')
            if st.form_submit_button('Salva', type='primary'):
                if nome and comune:
                    st.session_state.volontari.append({'Nome': nome, 'Comune': comune})
                    st.success('Salvato')

    elif m == 'Eventi':
        st.write('## Eventi')
        with st.form('eventi'):
            nome_e = st.text_input('NOME EVENTO *')
            luogo = st.text_input('Luogo *')
            if st.form_submit_button('Crea', type='primary'):
                if nome_e and luogo:
                    st.session_state.eventi.append({'NomeEvento': nome_e, 'Luogo': luogo})
                    st.success('Creato')

    elif m == 'Emergenze':
        st.write('## Emergenze - Form')
        with st.form('emergenze'):
            tipo_em = st.selectbox('Tipo *', ['Alluvione','Frana','Incendio','Terremoto','Neve','Ricerca','Altro'])
            luogo_em = st.text_input('Luogo *')
            descr = st.text_area('Descrizione *')
            if st.form_submit_button('Attiva', type='primary'):
                if luogo_em and descr:
                    st.session_state.emergenze.append({'Tipo': tipo_em, 'Luogo': luogo_em, 'Descrizione': descr, 'Data': str(date.today())})
                    st.success('Attivata')
        if st.session_state.emergenze:
            st.dataframe(pd.DataFrame(st.session_state.emergenze))

    elif m == 'Mappa Avanzata':
        st.write('## Mappa Avanzata - Fullscreen sotto + e - con ESC')
        st.info('Tasto sotto + e - espande al 100% - ESC torna indietro')

        col1,col2,col3 = st.columns([2,2,1])
        with col1:
            map_type = st.selectbox('Tipo Mappa', ['OpenStreetMap','Google Map','Google Satellite'])
        with col2:
            icona_sel = st.selectbox('Icona Marker', ['Nessuna'] + [i['Nome'] for i in st.session_state.icone] if st.session_state.icone else ['Nessuna'])
        with col3:
            if st.session_state.map_fullscreen:
                lab1 = 'Riduci Mappa 1'
            else:
                lab1 = 'Espandi Mappa 1'
            if st.button(lab1, key='exp1'):
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