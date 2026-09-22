import streamlit as st
import pandas as pd
import os
from io import BytesIO
from datetime import date, datetime
import tempfile
import json

st.set_page_config(page_title='ANA Varese', layout='wide')

VERDE = "#1A5D1A"
VERDE_BG = "#E8F5E9"

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
        st.markdown(f'### MENU - TUTTI I FORM')
        menu = st.radio('Scegli:', ['Dashboard','Volontari (con foto)','DB Radio','Brogliaccio','Eventi','Emergenze','Check-in','Mezzi','Attrezzature','Mappa Avanzata','Libreria Icone','Backup','Esporta'], index=0)
        st.session_state.menu = menu
        if st.button('Logout', use_container_width=True):
            st.session_state.page = 'entra'
            st.rerun()

    m = st.session_state.menu

    if m == 'Dashboard':
        st.markdown('## Dashboard - TUTTI I FORM VISIBILI')
        # FIX RIGA 137 - PARENTESI CHIUSE CORRETTAMENTE
        c1,c2,c3,c4 = st.columns(4)
        c1.metric('Volontari', len(st.session_state.volontari))
        c2.metric('Radio', len(st.session_state.radio_db))
        c3.metric('Eventi', len(st.session_state.eventi))
        c4.metric('Emergenze', len(st.session_state.emergenze))
        c1,c2,c3,c4 = st.columns(4)
        c1.metric('Check-in', len(st.session_state.checkin))
        c2.metric('Mezzi', len(st.session_state.mezzi))
        c3.metric('Attrezzature', len(st.session_state.attrezzature))
        c4.metric('Postazioni', len(st.session_state.postazioni))

    elif m == 'Volontari (con foto)':
        st.markdown('## VOLONTARI - 5 Sottomaschere + Foto OK')
        tab1, tab2, tab3, tab4, tab5 = st.tabs(['1. Anagrafica','2. Contatti','3. Ruolo','4. Foto','5. Elenco'])
        with tab1:
            with st.form('vol_anag'):
                c1,c2 = st.columns(2)
                with c1:
                    nome = st.text_input('Nome *')
                    cognome = st.text_input('Cognome *')
                with c2:
                    comune = st.text_input('Comune *')
                    data_nasc = st.date_input('Data Nascita', value=date(1980,1,1))
                if st.form_submit_button('Salva Anagrafica', type='primary', use_container_width=True):
                    if nome and cognome and comune:
                        st.session_state.vol_form_data.update({'Nome': nome, 'Cognome': cognome, 'Comune': comune, 'DataNascita': str(data_nasc)})
                        st.success('Anagrafica salvata')
        with tab2:
            with st.form('vol_cont'):
                cellulare = st.text_input('Cellulare *')
                email = st.text_input('Email')
                if st.form_submit_button('Salva Contatti', type='primary', use_container_width=True):
                    if cellulare:
                        st.session_state.vol_form_data.update({'Cellulare': cellulare, 'Email': email})
                        st.success('Contatti salvati')
        with tab3:
            with st.form('vol_ruolo'):
                ruolo = st.selectbox('Ruolo *', ['Volontario','Caposquadra','Coordinatore','Autista','Radio','Logistica','Sanitario','Altro'])
                squadra = st.selectbox('Squadra', ['Alpini Caronno','Squadra A','B','C'])
                if st.form_submit_button('Salva Ruolo', type='primary', use_container_width=True):
                    st.session_state.vol_form_data.update({'Ruolo': ruolo, 'Squadra': squadra})
                    st.success('Ruolo salvato')
        with tab4:
            c1,c2 = st.columns([1,2])
            with c1:
                foto_file = st.file_uploader('Carica Foto *', type=['png','jpg','jpeg'])
                if foto_file:
                    st.image(foto_file, width=200, caption='Preview OK')
            with c2:
                with st.form('vol_foto'):
                    if st.form_submit_button('SALVA VOLONTARIO COMPLETO', type='primary', use_container_width=True):
                        if not st.session_state.vol_form_data.get('Nome'):
                            st.error('Compila Anagrafica, Contatti, Ruolo')
                        else:
                            fb = foto_file.getvalue() if foto_file else None
                            vol = {
                                'Nome': st.session_state.vol_form_data.get('Nome',''),
                                'Cognome': st.session_state.vol_form_data.get('Cognome',''),
                                'Comune': st.session_state.vol_form_data.get('Comune',''),
                                'Cellulare': st.session_state.vol_form_data.get('Cellulare',''),
                                'Ruolo': st.session_state.vol_form_data.get('Ruolo',''),
                                'Squadra': st.session_state.vol_form_data.get('Squadra',''),
                                'FotoBytes': fb
                            }
                            st.session_state.volontari.append(vol)
                            st.session_state.vol_form_data = {}
                            st.success('Volontario salvato!')
            if foto_file:
                st.session_state.vol_form_data['FotoBytes'] = foto_file.getvalue()
        with tab5:
            if st.session_state.volontari:
                df = pd.DataFrame([{'Nome': v['Nome'], 'Cognome': v['Cognome'], 'Comune': v['Comune'], 'Ruolo': v['Ruolo']} for v in st.session_state.volontari])
                st.dataframe(df, use_container_width=True)

    elif m == 'DB Radio':
        st.markdown('## DB Radio - MASCHERA')
        with st.form('radio_form'):
            modello = st.text_input('Modello *')
            matricola = st.text_input('Matricola *')
            tipo = st.selectbox('Tipo *', ['DMR','PMR446','TETRA','VHF','UHF','CB','Altro'])
            if st.form_submit_button('Salva Radio', type='primary', use_container_width=True):
                if modello and matricola:
                    st.session_state.radio_db.append({'Modello': modello, 'Matricola': matricola, 'Tipo': tipo})
                    st.success