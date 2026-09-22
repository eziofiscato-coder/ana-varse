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
    # LOGO PC ANA A LATO INTESTAZIONE - IN TUTTI I FORM
    col_logo, col_title = st.columns([1,5])
    with col_logo:
        try:
            st.image('logo.png', width=110)
        except:
            try:
                st.image('copertina.png', width=110)
            except:
                st.markdown('**ANA**')
    with col_title:
        st.markdown(f'<div style="background:{VERDE};padding:12px;border-radius:8px;color:white;font-weight:bold;font-size:18px;">NUCLEO PROT CIVILE ANA VARESE<br>Squadra Alpini Caronno - Varese</div>', unsafe_allow_html=True)

def hdr_form(titolo):
    # LOGO + TITOLO FORM
    c1,c2 = st.columns([1,8])
    with c1:
        try:
            st.image('logo.png', width=80)
        except:
            try:
                st.image('copertina.png', width=80)
            except:
                pass
    with c2:
        st.markdown(f'## {titolo}')

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

for k in ['page','logged','menu','volontari','radio_db','eventi','emergenze','checkin','icone','postazioni','last_clicked','temp_markers','brogliaccio','mezzi','attrezzature','map_fullscreen','map_fullscreen2','vol_form_data','custom_defs','custom_data','alias_radio']:
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
                st.image('logo.png', width=250)
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
    menu_base = ['Dashboard','Volontari (con foto)','DB Radio','Alias Radio','Brogliaccio','Eventi','Emergenze','Check-in','Mezzi','Attrezzature','Mappa Avanzata','Libreria Icone','Backup','Esporta','Crea Nuovo Form']
    menu_custom = list(st.session_state.custom_defs.keys())
    menu_tot = menu_base + menu_custom
    with st.sidebar:
        # LOGO ANCHE IN SIDEBAR
        try:
            st.image('logo.png', width=120)
        except:
            pass
        st.markdown('### MENU')
        menu = st.radio('Scegli:', menu_tot, index=0)
        st.session_state.menu = menu
        if st.button('Logout', use_container_width=True):
            st.session_state.page = 'entra'
            st.rerun()

    m = st.session_state.menu

    if m == 'Dashboard':
        hdr_form('Dashboard - TASTI RAPIDI')
        c1,c2,c3,c4 = st.columns(4)
        c1.metric('Volontari', len(st.session_state.volontari))
        c2.metric('Radio', len(st.session_state.radio_db))
        c3.metric('Alias Radio', len(st.session_state.alias_radio))
        c4.metric('Eventi', len(st.session_state.eventi))
        c1b,c2b,c3b,c4b = st.columns(4)
        c1b.metric('Check-in', len(st.session_state.checkin))
        c2b.metric('Mezzi', len(st.session_state.mezzi))
        c3b.metric('Attrezzature', len(st.session_state.attrezzature))
        c4b.metric('Postazioni', len(st.session_state.postazioni))
        st.divider()
        st.markdown('### MENU RAPIDO - CLICCA E APRE FORM')
        r1 = st.columns(4)
        with r1[0]:
            if st.button('VOLONTARI', key='btn_vol', use_container_width=True, type='primary'):
                st.session_state.menu = 'Volontari (con foto)'
                st.rerun()
        with r1[1]:
            if st.button('DB RADIO', key='btn_radio', use_container_width=True, type='primary'):
                st.session_state.menu = 'DB Radio'
                st.rerun()
        with r1[2]:
            if st.button('ALIAS RADIO', key='btn_alias', use_container_width=True, type='primary'):
                st.session_state.menu = 'Alias Radio'
                st.rerun()
        with r1[3]:
            if st.button('BROGLIACCIO', key='btn_brog', use_container_width=True, type='primary'):
                st.session_state.menu = 'Brogliaccio'
                st.rerun()
        r2 = st.columns(4)
        with r2[0]:
            if st.button('EVENTI', key='btn_eventi', use_container_width=True, type='primary'):
                st.session_state.menu = 'Eventi'
                st.rerun()
        with r2[1]:
            if st.button('EMERGENZE', key='btn_emerg', use_container_width=True, type='primary'):
                st.session_state.menu = 'Emergenze'
                st.rerun()
        with r2[2]:
            if st.button('CHECK-IN', key='btn_check', use_container_width=True, type='primary'):
                st.session_state.menu = 'Check-in'
                st.rerun()
        with r2[3]:
            if st.button('MEZZI', key='btn_mezzi', use_container_width=True, type='primary'):
                st.session_state.menu = 'Mezzi'
                st.rerun()
        r3 = st.columns(4)
        with r3[0]:
            if st.button('ATTREZZATURE', key='btn_attr', use_container_width=True, type='primary'):
                st.session_state.menu = 'Attrezzature'
                st.rerun()
        with r3[1]:
            if st.button('MAPPA', key='btn_mappa', use_container_width=True, type='primary'):
                st.session_state.menu = 'Mappa Avanzata'
                st.rerun()
        with r3[2]:
            if st.button('ICONE', key='btn_icone', use_container_width=True, type='primary'):
                st.session_state.menu = 'Libreria Icone'
                st.rerun()
        with r3[3]:
            if st.button('BACKUP', key='btn_backup', use_container_width=True, type='primary'):
                st.session_state.menu = 'Backup'
                st.rerun()
        r4 = st.columns(4)
        with r4[0]:
            if st.button('CREA NUOVO FORM', key='btn_nuovo', use_container_width=True, type='primary'):
                st.session_state.menu = 'Crea Nuovo Form'
                st.rerun()
        with r4[1]:
            if st.button('ESPORTA', key='btn_export', use_container_width=True, type='primary'):
                st.session_state.menu = 'Esporta'
                st.rerun()

    elif m == 'Volontari (con foto)':
        hdr_form('VOLONTARI - CON FOTO')
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
                st.image(foto, width=200, caption='Preview OK')
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
                        v['Data'] = str(date.today())
                        st.session_state.volontari.append(v)
                        st.session_state.vol_form_data = {}
                        st.success('Volontario salvato!')
                        st.balloons()
                        st.rerun()
        with t5:
            st.markdown('### Elenco Volontari Salvati')
            if st.session_state.volontari:
                lista = []
                for vol in st.session_state.volontari:
                    r = {}
                    r['Nome'] = vol.get('Nome','')
                    r['Cognome'] = vol.get('Cognome','')
                    r['Comune'] = vol.get('Comune','')
                    r['Cellulare'] = vol.get('Cellulare','')
                    r['Ruolo'] = vol.get('Ruolo','')
                    r['Squadra'] = vol.get('Squadra','')
                    r['Foto'] = 'SI' if vol.get('FotoBytes') else 'NO'
                    lista.append(r)
                df = pd.DataFrame(lista)
                st.dataframe(df, use_container_width=True, hide_index=True)
                st.success(f"Trovati {len(lista)} volontari")
                st.download_button('Excel', to_excel(pd.DataFrame(st.session_state.volontari)), file_name='volontari.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', use_container_width=True)
            else:
                st.warning('Nessun volontario salvato')

    elif m == 'DB Radio':
        hdr_form('DB RADIO')
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

    elif m == 'Alias Radio':
        hdr_form('ALIAS RADIO - NOME ALIAS, VOLONTARIO, POSTAZIONE, EVENTO, EMERGENZA')
        with st.form('alias_form'):
            nome_alias = st.text_input('NOME ALIAS *')
            if st.session_state.volontari:
                lista_vol = [f"{v.get('Nome','')} {v.get('Cognome','')}" for v in st.session_state.volontari]
                volontario_sel = st.selectbox('VOLONTARIO *', lista_vol)
            else:
                volontario_sel = st.text_input('VOLONTARIO *')
            if st.session_state.postazioni:
                lista_post = ['Base','Avanzata'] + [p.get('Nome','') for p in st.session_state.postazioni]
                postazione_sel = st.selectbox('POSTAZIONE', lista_post)
            else:
                postazione_sel = st.selectbox('POSTAZIONE', ['Base','Avanzata'])
            if st.session_state.eventi:
                lista_eventi = ['Nessuno'] + [e.get('NomeEvento','') for e in st.session_state.eventi]
                evento_sel = st.selectbox('EVENTO', lista_eventi)
            else:
                evento_sel = st.text_input('EVENTO')
            if st.session_state.emergenze:
                lista_emerg = ['Nessuna'] + [e.get('Tipo','') + ' - ' + e.get('Luogo','') for e in st.session_state.emergenze]
                emergenza_sel = st.selectbox('EMERGENZA', lista_emerg)
            else:
                emergenza_sel = st.text_input('EMERGENZA')
            note_alias = st.text_area('Note')
            if st.form_submit_button('Salva Alias Radio', type='primary', use_container_width=True):
                if nome_alias and volontario_sel:
                    a = {}
                    a['NomeAlias'] = nome_alias
                    a['Volontario'] = volontario_sel
                    a['Postazione'] = postazione_sel
                    a['Evento'] = evento_sel
                    a['Emergenza'] = emergenza_sel
                    a['Note'] = note_alias
                    a['Data'] = str(date.today())
                    st.session_state.alias_radio.append(a)
                    st.success(f'Alias {nome_alias} salvato!')
                    st.balloons()
                else:
                    st.error('NOME ALIAS e VOLONTARIO obbligatori')
        if st.session_state.alias_radio:
            st.divider()
            df_alias = pd.DataFrame(st.session_state.alias_radio)
            st.dataframe(df_alias, use_container_width=True, hide_index=True)
            st.download_button('Excel Alias', to_excel(df_alias), file_name='alias_radio.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', use_container_width=True)

    elif m == 'Brogliaccio':
        hdr_form('BROGLIACCIO')
        with st.form('brog_form'):
            mitt = st.text_input('Mittente *')
            dest = st.text_input('Destinatario *')
            msg = st.text_area('Messaggio *')
            if st.form_submit_button('Salva', type='primary', use