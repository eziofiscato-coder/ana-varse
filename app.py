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
    cols = [c for c in df.columns if c not in ['Foto','FotoBytes','DocBytes','FileBytes']]
    df[cols].to_excel(out, index=False, engine='openpyxl')
    return out.getvalue()

def to_excel_multi(datasets):
    out = BytesIO()
    with pd.ExcelWriter(out, engine='openpyxl') as writer:
        for nome, df_list in datasets.items():
            if df_list:
                df = pd.DataFrame(df_list)
                cols = [c for c in df.columns if c not in ['Foto','FotoBytes','DocBytes','FileBytes']]
                df[cols].to_excel(writer, sheet_name=nome[:31], index=False)
    return out.getvalue()

def genera_pdf(df, titolo):
    try:
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib import colors
        buf = BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=landscape(A4))
        styles = getSampleStyleSheet()
        story = []
        story.append(Paragraph(f"<b>{titolo}</b> {datetime.now():%d/%m/%Y}", styles['Title']))
        story.append(Spacer(1,12))
        cols = [c for c in df.columns if c not in ['Foto','FotoBytes','DocBytes','FileBytes']]
        df2 = df[cols].astype(str)
        data = [list(df2.columns)] + df2.values.tolist()
        if len(data[0]) > 8:
            data = [r[:8] for r in data]
        t = Table(data)
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0), colors.HexColor(VERDE)),('TEXTCOLOR',(0,0),(-1,0), colors.white),('GRID',(0,0),(-1,-1),0.5, colors.grey),('FONTSIZE',(0,0),(-1,-1),7),]))
        story.append(t)
        doc.build(story)
        return buf.getvalue()
    except:
        return None

def salva_icona_temp(fb, nome):
    try:
        p = os.path.join(tempfile.gettempdir(), f"icon_{nome}.png")
        with open(p,"wb") as f:
            f.write(fb)
        return p
    except:
        return None

for k in ['page','logged','menu','volontari','radio_db','eventi','emergenze','checkin','icone','postazioni','last_clicked','temp_markers','brogliaccio','mezzi','attrezzature','map_fullscreen','map_fullscreen2','vol_form_data']:
    if k not in st.session_state:
        if k == 'page': st.session_state[k] = 'entra'
        elif k == 'logged': st.session_state[k] = False
        elif k == 'menu': st.session_state[k] = 'Dashboard'
        elif k == 'last_clicked': st.session_state[k] = None
        elif k == 'temp_markers': st.session_state[k] = []
        elif k in ['map_fullscreen','map_fullscreen2']: st.session_state[k] = False
        elif k == 'vol_form_data': st.session_state[k] = {}
        else: st.session_state[k] = []

if st.session_state.page == 'entra':
    hdr()
    c1,c2,c3 = st.columns([1,2,1])
    with c2:
        try: st.image('copertina.png', width=350)
        except:
            try: st.image('logo.png', width=200)
            except: pass
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
        st.markdown('## Dashboard - TUTTE LE MASCHERE PRESENTI')
        col1, col2, col3, col4 = st.columns(4)
        col1.metric('Volontari', len(st.session_state.volontari))
        col2.metric('Radio', len(st.session_state.radio_db))
        col3.metric('Eventi', len(st.session_state.eventi))
        col4.metric('Emergenze', len(st.session_state.emergenze))
        col1b, col2b, col3b, col4b = st.columns(4)
        col1b.metric('Check-in', len(st.session_state.checkin))
        col2b.metric('Mezzi', len(st.session_state.mezzi))
        col3b.metric('Attrezzature', len(st.session_state.attrezzature))
        col4b.metric('Postazioni', len(st.session_state.postazioni))
    elif m == 'Volontari (con foto)':
        st.markdown('## VOLONTARI - 5 SOTTOMASCHERE + FOTO')
        tab1, tab2, tab3, tab4, tab5 = st.tabs(['1. Anagrafica','2. Contatti','3. Ruolo','4. Foto','5. Elenco'])
        with tab1:
            with st.form('vol_anag'):
                c1,c2 = st.columns(2)
                with c1:
                    nome = st.text_input('Nome *')
                    cognome = st.text_input('Cognome *')
                    cf = st.text_input('Codice Fiscale')
                with c2:
                    comune = st.text_input('Comune Residenza *')
                    data_nasc = st.date_input('Data Nascita', value=date(1980,1,1))
                    luogo_nasc = st.text_input('Luogo Nascita')
                if st.form_submit_button('Salva Anagrafica', type='primary', use_container_width=True):
                    if nome and cognome and comune:
                        st.session_state.vol_form_data.update({'Nome': nome, 'Cognome': cognome, 'CF': cf, 'Comune': comune, 'DataNascita': str(data_nasc), 'LuogoNascita': luogo_nasc})