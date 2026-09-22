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
    c1,c2 = st.columns([1,5])
    with c1:
        try:
            st.image('logo.png', width=110)
        except:
            try:
                st.image('copertina.png', width=110)
            except:
                st.markdown('**ANA**')
    with c2:
        st.markdown(f'<div style="background:{VERDE};padding:12px;border-radius:8px;color:white;font-weight:bold;font-size:18px;">NUCLEO PROT CIVILE ANA VARESE - Squadra Alpini Caronno</div>', unsafe_allow_html=True)

def hdr_form(titolo):
    c1,c2 = st.columns([1,8])
    with c1:
        try:
            st.image('logo.png', width=80)
        except:
            pass
    with c2:
        st.markdown(f'## {titolo}')

def to_excel(df):
    out = BytesIO()
    cols = [c for c in df.columns if c not in ['Foto','FotoBytes','FileBytes']]
    cols = [c for c in cols if c in df.columns]
    df[cols].to_excel(out, index=False, engine='openpyxl')
    return out.getvalue()

def to_pdf(df, titolo):
    try:
        from reportlab.lib.pagesizes import landscape, A4
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib import colors
        buf = BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=landscape(A4), leftMargin=20, rightMargin=20, topMargin=20, bottomMargin=20)
        styles = getSampleStyleSheet()
        story = []
        story.append(Paragraph(f"<b>{titolo} - {date.today()}</b>", styles['Title']))
        story.append(Spacer(1,12))
        if not df.empty:
            cols = [c for c in df.columns if c not in ['Foto','FotoBytes','FileBytes']][:8]
            data = [cols]
            for _, row in df.iterrows():
                data.append([str(row.get(c,''))[:50] for c in cols])
            t = Table(data, repeatRows=1)
            t.setStyle(TableStyle([
                ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#1A5D1A')),
                ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
                ('ALIGN',(0,0),(-1,-1),'LEFT'),
                ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
                ('FONTSIZE',(0,0),(-1,-1),7),
                ('GRID',(0,0),(-1,-1),0.5,colors.grey),
            ]))
            story.append(t)
        doc.build(story)
        return buf.getvalue()
    except:
        return None

def to_excel_multi(datasets):
    out = BytesIO()
    with pd.ExcelWriter(out, engine='openpyxl') as writer:
        for nome, df_list in datasets.items():
            if df_list:
                try:
                    df = pd.DataFrame(df_list)
                    cols = [c for c in df.columns if c not in ['Foto','FotoBytes','FileBytes']]
                    df[cols].to_excel(writer, sheet_name=nome[:31], index=False)
                except:
                    pass
    return out.getvalue()

def salva_icona_temp(fb, nome):
    try:
        p = os.path.join(tempfile.gettempdir(), f"icon_{nome}.png")
        with open(p,"wb") as f:
            f.write(fb)
        return p
    except:
        return None

for k in ['page','logged','menu','volontari','radio_db','eventi','emergenze','checkin','icone','postazioni','last_clicked','temp_markers','brogliaccio','mezzi','attrezzature','map_fullscreen','vol_form_data','alias_radio','brog_evento_blindato','brog_emergenza_blindata','brog_blindato','check_evento_blindato','check_emergenza_blindata','check_blindato','interventi','interventi_emergenza_blindata','interventi_blindato']:
    if k not in st.session_state:
        if k == 'page':
            st.session_state[k] = 'entra'
        elif k == 'logged':
            st.session_state[k] = False
        elif k == 'menu':
            st.session_state[k] = 'Dashboard'
        elif k in ['map_fullscreen','brog_blindato','check_blindato','interventi_blindato']:
            st.session_state[k] = False
        elif k == 'vol_form_data':
            st.session_state[k] = {}
        elif k in ['brog_evento_blindato','brog_emergenza_blindata','check_evento_blindato','check_emergenza_blindata','interventi_emergenza_blindata','last_clicked']:
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
            st.image('copertina.png', width=350)
        except:
            try:
                st.image('logo.png', width=250)
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
        u = st.text_input('Utente')
        p = st.text_input('Password', type='password')
        if st.button('Accedi', use_container_width=True, type='primary'):
            if u == 'admin' and p == 'ana2024':
                st.session_state.logged = True
                st.session_state.page = 'dashboard'
                st.rerun()
            else:
                st.error('admin / ana2024')

elif st.session_state.page == 'dashboard':
    hdr()
    menu_base = ['Dashboard','Volontari (con foto)','DB Radio','Alias Radio','Brogliaccio','Eventi','Emergenze','Check-in','Interventi Emergenza','Mezzi','Attrezzature','Mappa Avanzata','Libreria Icone','Backup','Esporta']
    with st.sidebar:
        try:
            st.image('logo.png', width=120)
        except:
            pass
        st.markdown('### MENU')
        try:
            idx = menu_base.index(st.session_state.menu)
        except:
            idx = 0
        m = st.radio('Scegli:', menu_base, index=idx)
        st.session_state.menu = m
        if st.button('Logout', use_container_width=True):
            st.session_state.page = 'entra'
            st.rerun()
    cur = st.session_state.menu

    if cur == 'Dashboard':
        hdr_form('Dashboard - TASTI RAPIDI OK - MENU VELOCE')
        c1,c2,c3,c4 = st.columns(4)
        c1.metric('Volontari', len(st.session_state.volontari))
        c2.metric('Radio', len(st.session_state.radio_db))
        c3.metric('Alias Radio', len(st.session_state.alias_radio))
        c4.metric('Eventi', len(st.session_state.eventi))
        c1b,c2b,c3b,c4b = st.columns(4)
        c1b.metric('Check-in', len(st.session_state.checkin))
        c2b.metric('Brogliaccio', len(st.session_state.brogliaccio))
        c3b.metric('Interventi', len(st.session_state.interventi))
        c4b.metric('Emergenze', len(st.session_state.emergenze))
        st.divider()
        st.markdown('### MENU RAPIDO - TASTI RAPIDI - CLICCA E APRE FORM')
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
            if st.button('INTERVENTI', key='btn_interv', use_container_width=True, type='primary'):
                st.session_state.menu = 'Interventi Emergenza'
                st.rerun()
        r3 = st.columns(4)
        with r3[0]:
            if st.button('MEZZI', key='btn_mezzi', use_container_width=True, type='primary'):
                st.session_state.menu = 'Mezzi'
                st.rerun()
        with r3[1]:
            if st.button('MAPPA', key='btn_mappa', use_container_width=True, type='primary'):
                st.session_state.menu = 'Mappa Avanzata'
                st.rerun()
        with r3[2]:
            if st.button('LIBRERIA ICONE', key='btn_icone', use_container_width=True, type='primary'):
                st.session_state.menu = 'Libreria Icone'
                st.rerun()
        with r3[3]:
            if st.button('BACKUP', key='btn_backup', use_container_width=True, type='primary'):
                st.session_state.menu = 'Backup'
                st.rerun()

    elif cur == 'DB Radio':
        hdr_form('DB RADIO - MASCHERA COMPLETA RIPRISTINATA')
        with st.form('radio_form'):
            st.markdown('#### Dati Radio')
            c1,c2 = st.columns(2)
            with c1:
                modello = st.text_input('Modello *')
                matricola = st.text_input('Matricola *')
                tipo = st.selectbox('Tipo *', ['DMR','PMR446','TETRA','VHF','UHF','CB','Altro'])
            with c2:
                freq = st.text_input('Frequenza')
                canale = st.text_input('Canale')
                stato_r = st.selectbox('Stato', ['Disponibile','In Uso','Manutenzione','Guasta'])
            note_r = st.text_area('Note')
            if st.form_submit_button('Salva Radio', type='primary', use_container_width=True):
                if modello and matricola:
                    r = {'Modello':modello,'Matricola':matricola,'Tipo':tipo,'Frequenza':freq,'Canale':canale,'Stato':stato_r,'Note':note_r,'Data':str(date.today())}
                    st.session_state.radio_db.append(r)
                    st.success(f'Radio {modello} {matricola} salvata!')
                    st.balloons()
        if st.session_state.radio_db:
            st.divider()
            st.dataframe(pd.DataFrame(st.session_state.radio_db), use_container_width=True)
            c1,c2 = st.columns(2)
            c1.download_button('Excel Radio', to_excel(pd.DataFrame(st.session_state.radio_db)), file_name='radio.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', use_container_width=True)
            pdf = to_pdf(pd.DataFrame(st.session_state.radio_db), 'DB Radio')
            if pdf:
                c2.download_button('PDF Radio', pdf, file_name='radio.pdf', mime='application/pdf', use_container_width=True)

    elif cur == 'Alias Radio':
        hdr_form('ALIAS RADIO - EVENTO COMBO DA FORM EVENTO OK')
        with st.form('alias_form'):
            nome_alias = st.text_input('NOME ALIAS *')
            if st.session_state.volontari:
                lista_vol = [f"{v.get('Nome','')} {v.get('Cognome','')}" for v in st.session_state.volontari]
                volontario_sel = st.selectbox('VOLONTARIO * (combo da Volontari)', lista_vol)
            else:
                volontario_sel = st.text_input('VOLONTARIO *')
            if st.session_state.eventi:
                lista_eventi = [e.get('NomeEvento','') for e in st.session_state.eventi]
                evento_sel = st.selectbox('EVENTO * (combo da Form Evento)', ['Nessuno'] + lista_eventi)
            else:
                evento_sel = st.text_input('EVENTO')
            if st.form_submit_button('Salva Alias Radio', type='primary', use_container_width=True):
                if nome_alias and volontario_sel:
                    st.session_state.alias_radio.append({'NomeAlias':nome_alias,'Volontario':volontario_sel,'Evento':evento_sel,'Data':str(date.today())})
                    st.success(f'Alias {nome_alias} salvato!')
        if st.session_state.alias_radio:
            st.dataframe(pd.DataFrame(st.session_state.alias_radio), use_container_width=True)

    elif cur == 'Interventi Emergenza':
        hdr_form('INTERVENTI EMERGENZA - COLLEGATO A EMERGENZA BLINDATA + STATO')
        if not st.session_state.interventi_blindato:
            if st.session_state.emergenze:
                lista_em = [e.get('Tipo','') + ' - ' + e.get('Luogo','') for e in st.session_state
