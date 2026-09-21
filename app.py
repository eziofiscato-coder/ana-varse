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
  font-weight:bold!important;
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

for k in ['page','logged','menu','volontari','radio_db','eventi','emergenze','checkin','icone','postazioni','last_clicked','temp_markers','map_fullscreen','map_fullscreen2']:
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
        st.write('## Emergenze - Form Completo')
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
        st.info('Tasto quadrato sotto + e - espande al 100% - ESC torna indietro')

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
            folium.TileLayer('openstreetmap', name='OSM').add_to(mm)
        elif map_type == 'Google Map':
            folium.TileLayer(tiles='https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}', attr='Google', name='Google').add_to(mm)
        else:
            folium.TileLayer(tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', attr='Google', name='Satellite').add_to(mm)

        Fullscreen(position='topleft', title='Espandi a tutto schermo', title_cancel='Esci ESC', force_separate_button=True).add_to(mm)

        for p in st.session_state.postazioni:
            lat_f = p['Lat']
            lon_f = p['Log']
            nome = p['Nome']
            com = p.get('Comune','')
            popup_html = f"<b>{nome}</b><br>{com}"
            p_icon = p.get('Icona','Nessuna')
            use_path = None
            if p_icon!= 'Nessuna':
                ico = next((i for i in st.session_state.icone if i['Nome'] == p_icon), None)
                if ico:
                    fb = ico.get('FileBytes')
                    if fb:
                        use_path = salva_icona_temp(fb, p_icon)
            if use_path:
                icon_obj = folium.CustomIcon(use_path, icon_size=(40,40))
                folium.Marker([lat_f, lon_f], popup=popup_html, icon=icon_obj).add_to(mm)
            else:
                folium.Marker([lat_f, lon_f], popup=popup_html, icon=folium.Icon(color='green')).add_to(mm)

        icon_path_sel = None
        if icona_sel!= 'Nessuna':
            ico_sel = next((i for i in st.session_state.icone if i['Nome'] == icona_sel), None)
            if ico_sel:
                fb_sel = ico_sel.get('FileBytes')
                if fb_sel:
                    icon_path_sel = salva_icona_temp(fb_sel, icona_sel)

        for tm in st.session_state.temp_markers:
            if icon_path_sel:
                icon_obj2 = folium.CustomIcon(icon_path_sel, icon_size=(40,40))
                folium.Marker([tm['lat'], tm['lon']], icon=icon_obj2).add_to(mm)
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
            st.success(f"Marker {icona_sel}: {lat_c:.5f}")
            st.rerun()

        last = st.session_state.last_clicked
        if last:
            st.info(f"Click {last['lat']:.6f} {last['lon']:.6f} {last.get('comune','')}")

        with st.form('form_post'):
            nome_p = st.text_input('Nome Postazione *')
            comune_p = st.text_input('Comune *', value=last.get('comune','') if last else '')
            via_p = st.text_input('Via *', value=last.get('via','') if last else '')
            c1,c2 = st.columns(2)
            with c1:
                lat_p = st.text_input('Lat *', value=str(last['lat']) if last else '')
            with c2:
                lon_p = st.text_input('Log *', value=str(last['lon']) if last else '')
            lista_icone = ['Nessuna'] + [i['Nome'] for i in st.session_state.icone] if st.session_state.icone else ['Nessuna']
            icona_def = last.get('icona','Nessuna') if last else 'Nessuna'
            idx_ico = lista_icone.index(icona_def) if icona_def in lista_icone else 0
            icona_p = st.selectbox('Icona Libreria', lista_icone, index=idx_ico)
            if st.form_submit_button('Salva Postazione', use_container_width=True, type='primary'):
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
                        st.error('Lat Log non validi')

        st.divider()
        st.write('## Mappa Tutte Postazioni - OSM Default')

        if st.session_state.map_fullscreen2:
            lab2 = 'Riduci Mappa 2'
        else:
            lab2 = 'Espandi Mappa 2'

        if st.button(lab2, key='exp2'):
            st.session_state.map_fullscreen2 = not st.session_state.map_fullscreen2
            st.rerun()

        h2 = 800 if st.session_state.map_fullscreen2 else 500

        if st.session_state.postazioni:
            df_post = pd.DataFrame(st.session_state.postazioni)
            st.dataframe(df_post, use_container_width=True)
            import folium
            from streamlit_folium import st_folium
            from folium.plugins import Fullscreen
            lat_m = df_post.Lat.mean()
            lon_m = df_post.Log.mean()
            m2 = folium.Map(location=[lat_m, lon_m], zoom_start=11, tiles='openstreetmap')
            folium.TileLayer(tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', attr='Google', name='Satellite').add_to(m2)
            Fullscreen(position='topleft', title='Espandi', title_cancel='Esci ESC', force_separate_button=True).add_to(m2)
            for p in st.session_state.postazioni:
                folium.Marker([p['Lat'], p['Log']], popup=p['Nome'], icon=folium.Icon(color='green')).add_to(m2)
            folium.LayerControl().add_to(m2)
            st_folium(m2, width=1400, height=h2, use_container_width=True, key='map2')
        else:
            st.info('Nessuna postazione')

    elif m == 'Libreria Icone':
        st.write('## Libreria Icone - Marker Mappa')
        with st.form('icone'):
            nome_i = st.text_input('Nome icona *')
            file_i = st.file_uploader('Carica PNG - Sara marker', type=['png','jpg','jpeg'])
            if file_i:
                st.image(file_i, width=120)
            if st.form_submit_button('Salva Icona Marker', type='primary'):
                if nome_i and file_i:
                    st.session_state.icone.append({'Nome': nome_i, 'FileName': file_i.name, 'FileBytes': file_i.getvalue()})
                    st.success(f"Icona {nome_i} caricata")
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