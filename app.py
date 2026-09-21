import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import date

st.set_page_config(page_title='ANA Varese', layout='wide')

def hdr():
    st.markdown(
        '<div style="background:#0e7a3d;padding:8px;'
        'border-radius:8px;color:white;text-align:center;'
        'font-weight:bold;">NUCLEO DI PROTEZIONE CIVILE ANA '
        'SEZ. DI VARESE Squadra Gruppo Alpini Caronno '
        'Pertusella Bariola</div>',
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
        'GESTIONALE<br>di Protezione Civile</h2>',
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
        st.markdown('## Volontari - Con Sottomaschere')
        t1,t2,t3,t4 = st.tabs([
            'Anagrafica e Foto',
            'Contatti e Ruolo',
            'Qualifiche',
            'Documenti Taglie Note'
        ])

        with t1:
            with st.form('vol_anag'):
                nome = st.text_input('Nome e Cognome *')
                cf = st.text_input('Codice Fiscale')
                comune = st.text_input('Comune residenza *')
                via = st.text_input('Via')
                c1,c2 = st.columns(2)
                with c1:
                    lat_txt = st.text_input('Lat - VUOTO=no default')
                with c2:
                    lon_txt = st.text_input('Log - VUOTO=no default')
                foto = st.file_uploader('Foto Volontario', type=['png','jpg','jpeg'])
                if foto:
                    st.image(foto, width=120, caption='Preview foto')
                if st.form_submit_button('Salva Anagrafica', use_container_width=True, type='primary'):
                    if nome and comune:
                        try:
                            lat_v = float(lat_txt.replace(',','.')) if lat_txt else 0.0
                            lon_v = float(lon_txt.replace(',','.')) if lon_txt else 0.0
                        except:
                            lat_v = 0.0
                            lon_v = 0.0
                        fb = foto.getvalue() if foto else None
                        fn = foto.name if foto else ''
                        st.session_state.volontari.append({
                            'Nome': nome,
                            'CF': cf,
                            'Comune': comune,
                            'Via': via,
                            'Lat': lat_v,
                            'Log': lon_v,
                            'FotoBytes': fb,
                            'FotoName': fn,
                            'Cellulare': '',
                            'Email': '',
                            'Ruolo': 'Volontario',
                            'Qualifiche': '',
                            'Documento