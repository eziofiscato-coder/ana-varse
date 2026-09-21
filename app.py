import streamlit as st
import pandas as pd
import os
from io import BytesIO
from datetime import date, datetime
import tempfile

st.set_page_config(
    page_title='ANA Varese',
    layout='wide'
)

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
}}
</style>
""", unsafe_allow_html=True)

def hdr():
    st.markdown(
        f'<div style="background:{VERDE};padding:8px;'
        f'border-radius:8px;color:white;'
        f'text-align:center;font-weight:bold;">'
        f'NUCLEO PROT CIVILE ANA VARESE '
        f'Squadra Alpini Caronno</div>',
        unsafe_allow_html=True
    )

def to_excel(df):
    out = BytesIO()
    df2 = df[[c for c in df.columns
               if c not in ['Foto','FileBytes']]]
    df2.to_excel(out, index=False, engine='openpyxl')
    return out.getvalue()

def genera_pdf(df, titolo):
    try:
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.platypus import (
            SimpleDocTemplate,
            Table,
            TableStyle,
            Paragraph,
            Spacer
        )
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib import colors
        buf = BytesIO()
        doc = SimpleDocTemplate(
            buf,
            pagesize=landscape(A4)
        )
        styles = getSampleStyleSheet()
        story = []
        story.append(Paragraph(
            f"<b>{titolo}</b> - {datetime.now():%d/%m/%Y}",
            styles['Title']
        ))
        story.append(Spacer(1,12))
        df2 = df[[c for c in df.columns
                  if c not in ['Foto','FileBytes']]].astype(str)
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
        p = os.path.join(
            tempfile.gettempdir(),
            f"icon_{nome}.png"
        )
        with open(p,"wb") as f:
            f.write(fb)
        return p
    except:
        return None

for k in [
    'page','logged','menu','volontari','radio_db',
    'eventi','emergenze','checkin','icone',
    'postazioni','last_clicked','temp_markers',
    'brogliaccio','mezzi','attrezzature',
    'map_fullscreen','map_fullscreen2'
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
    st.markdown(
        f'<h2 style="text-align:center;'
        f'color:{VERDE};">GESTIONALE<br>Prot Civile</h2>',
        unsafe_allow_html=True
    )
    st.divider()
    c1,c2,c3 = st.columns([1,1,1])
    with c2:
        if st.button('ENTRA', use_container_width=True,
                      type='primary'):
            st.session_state.page = 'login'
            st.rerun()

elif st.session_state.page == 'login':
    hdr()
    c1,c2,c3 = st.columns([1,2,1])
    with c2:
        st.markdown(
            f'### <span style="color:{VERDE}">Login</span>',
            unsafe_allow_html=True
        )
        user = st.text_input('Utente')
        pwd = st.text_input('Password', type='password')
        a,b = st.columns(2)
        with a:
            if st.button('Indietro', use_container_width=True):
                st.session_state.page = 'entra'
                st.rerun()
        with b:
            if st.button('Accedi', use_container_width=True,
                          type='primary'):
                if user == 'admin' and pwd == 'ana2024':
                    st.session_state.logged = True
                    st.session_state.page = 'dashboard'
                    st.rerun()
                else:
                    st.error('admin / ana2024')

elif st.session_state.page == 'dashboard':
    hdr()
    with st.sidebar:
        st.markdown(
            f'### <span style="color:{VERDE}">MENU</span>',
            unsafe_allow_html=True
        )
        menu = st.radio(
            'Scegli:',
            [
                'Dashboard',
                'Volontari',
                'DB Radio',
                'Brogliaccio',
                'Eventi',
                'Emergenze',
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
        st.markdown(f'## Dashboard', unsafe_allow_html=True)
        c1,c2,c3,c4 = st.columns(4)
        with c1:
            st.metric('Volontari',
                      len(st.session_state.volontari))
        with c2:
            st.metric('Eventi',
                      len(st.session_state.eventi))
        with c3:
            st.metric('Emergenze',
                      len(st.session_state.emergenze))
        with c4:
            st.metric('Postazioni',
                      len(st.session_state.postazioni))
        st.divider()
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
            if st.button('EMERGENZE', use_container_width=True):
                st.session_state.menu = 'Emergenze'
                st.rerun()
        with r1[3]:
            if st.button('MAPPA', use_container_width=True):
                st.session_state.menu = 'Mappa Avanzata'
                st.rerun()

    elif m == 'Volontari':
        st.markdown(f'## Volontari', unsafe_allow_html=True)
        t1,t2 = st.tabs(['Anagrafica','Elenco'])
        with t1:
            with st.form('vol1'):
                nome = st.text_input('Nome *')
                comune = st.text_input('Comune *')
                foto = st.file_uploader(
                    'Foto',
                    type=['png','jpg','jpeg']
                )
                if foto:
                    st.image(foto, width=100)
                if st.form_submit_button(
                    'Salva', use_container_width=True,
                    type='primary'
                ):
                    if nome and comune:
                        fb = foto.getvalue() if foto else None
                        st.session_state.volontari.append(
                            {'Nome': nome,
                             'Comune': comune,
                             'Foto': fb}
                        )
                        st.success('Salvato')
        with t2:
            if st.session_state.volontari:
                df = pd.DataFrame([
                    {'Nome': v['Nome'],
                     'Comune': v['Comune']}
                    for v in st.session_state.volontari
                ])
                st.dataframe(df, use_container_width=True)
                c1,c2 = st.columns(2)
                c1.download_button(
                    'Excel',
                    to_excel(df),
                    file_name='volontari.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    use_container_width=True
                )
                pdf = genera_pdf(df, 'Volontari')
                if pdf:
                    c2.download_button(
                        'PDF',
                        pdf,
                        file_name='volontari.pdf',
                        mime='application/pdf',
                        use_container_width=True
                    )

    elif m == 'DB Radio':
        st.markdown(f'## DB Radio', unsafe_allow_html=True)
        with st.form('radio'):
            modello = st.text_input('Modello *')
            matricola = st.text_input('Matricola *')
            tipo = st.selectbox(
                'Tipo *',
                ['DMR','PMR446','TETRA','NAUTICHE',
                 'VHF','UHF','VHF/UHF','HF','CB','Altro']
            )
            if st.form_submit_button(
                'Salva', use_container_width=True,
                type='primary'
            ):
                if modello and matricola:
                    st.session_state.radio_db.append(
                        {'Modello': modello,
                         'Matricola': matricola,
                         'Tipo': tipo}
                    )
                    st.success('Salvata')
        if st.session_state.radio_db:
            df = pd.DataFrame(st.session_state.radio_db)
            st.dataframe(df, use_container_width=True)

    elif m == 'Emergenze':
        st.markdown(f'## Emergenze', unsafe_allow_html=True)
        with st.form('emergenze'):
            tipo_em = st.selectbox(
                'Tipo *',
                ['Alluvione','Frana','Incendio',
                 'Terremoto','Neve','Ricerca','Altro']
            )
            luogo_em = st.text_input('Luogo *')
            descr = st.text_area('Descrizione *')
            if st.form_submit_button(
                'Attiva', use_container_width=True,
                type='primary'
            ):
                if luogo_em and descr:
                    st.session_state.emergenze.append(
                        {'Tipo': tipo_em,
                         'Luogo': luogo_em,
                         'Descrizione': descr,
                         'Data': str(date.today())}
                    )
                    st.success('Attivata')
        if st.session_state.emergenze:
            df = pd.DataFrame(st.session_state.emergenze)
            st.dataframe(df, use_container_width=True)
            c1,c2 = st.columns(2)
            c1.download_button(
                'Excel',
                to_excel(df),
                file_name='emergenze.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                use_container_width=True
            )
            pdf = genera_pdf(df, 'Emergenze')
            if pdf:
                c2.download_button(
                    'PDF',
                    pdf,
                    file_name='emergenze.pdf',
                    mime='application/pdf',
                    use_container_width=True
                )

    elif m == 'Eventi':
        st.markdown(f'## Eventi', unsafe_allow_html=True)
        with st.form('eventi'):
            nome_e = st.text_input('NOME EVENTO *')
            luogo = st.text_input('Luogo *')
            if st.form_submit_button(
                'Crea', use_container_width=True,
                type='primary'
            ):
                if nome_e and luogo:
                    st.session_state.eventi.append(
                        {'NomeEvento': nome_e,
                         'Luogo': luogo}
                    )
                    st.success('Creato')
        if st.session_state.eventi:
            df = pd.DataFrame(st.session_state.eventi)
            st.dataframe(df, use_container_width=True)

    elif m == 'Mappa Avanzata':
        st.markdown(f'## Mappa Avanzata', unsafe_allow_html=True)
        st.info(
            'Fullscreen sotto + e - con ESC per tornare'
        )
        col1,col2,col3 = st.columns([2,2,1])
        with col1:
            map_type = st.selectbox(
                'Tipo Mappa',
                ['OpenStreetMap','Google Map',
                 'Google Satellite','Google Hybrid']
            )
        with col2:
            icona_sel = st.selectbox(
                'Icona Marker',
                ['Nessuna'] + [i['Nome']
                               for i in st.session_state.icone]
                if st.session_state.icone else ['Nessuna']
            )
        with col3:
            if st.session_state.map_fullscreen:
                lab1 = 'Riduci Mappa 1'
            else:
                lab1 = 'Espandi Mappa 1'
            if st.button(lab1, use_container_width=True,
                          key='exp1'):
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
                    url = (
                        f'https://nominatim.openstreetmap.org/'
                        f'reverse?format=json&lat={lat}'
                        f'&lon={lon}&zoom=18&addressdetails=1'
                    )
                    r = requests.get(
                        url,
                        headers={'User-Agent':'ANA'},
                        timeout=5
                    )
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

            m = folium.Map(
                location=[lat_c, lon_c],
                zoom_start=12,
                tiles=None
            )
            if map_type == 'OpenStreetMap':
                folium.TileLayer('openstreetmap').add_to(m)
            elif map_type == 'Google Map':
                folium.TileLayer(
                    tiles='https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',
                    attr='Google'
                ).add_to(m)
            elif map_type == 'Google Satellite':
                folium.TileLayer(
                    tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
                    attr='Google'
                ).add_to(m)
            else:
                folium.TileLayer(
                    tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
                    attr='Google'
                ).add_to(m)

            Fullscreen(
                position='topleft',
                title='Espandi a tutto schermo',
                title_cancel='Esci - ESC',
                force_separate_button=True
            ).add_to(m)

            for p in st.session_state.postazioni:
                lat_f = p['Lat']
                lon_f = p['Log']
                popup_html = (
                    f"<b>{p['Nome']}</b><br>"
                    f"{p.get('Comune','')}<br>"
                    f"<a href='https://www.google.com/maps/"
                    f"search/?api=1&query={lat_f},{lon_f}' "
                    f"target='_blank'>Google</a> | "
                    f"<a href='https://waze.com/ul?ll={lat_f},"
                    f"{lon_f}&navigate=yes' target='_blank'>Waze</a>"
                )
                p_icon = p.get('Icona','Nessuna')
                use_path = None
                if p_icon!= 'Nessuna':