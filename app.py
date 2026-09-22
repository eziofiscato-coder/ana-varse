import streamlit as st
import pandas as pd
import os
from io import BytesIO
from datetime import date, datetime
import tempfile

st.set_page_config(page_title='ANA Varese', layout='wide')
VERDE = "#1A5D1A"
st.markdown(f"<style>h1,h2,h3{{color:{VERDE}!important;}}.stButton>button{{background:{VERDE}!important;color:white!important;font-weight:bold!important;}}</style>", unsafe_allow_html=True)

def hdr():
    c1,c2 = st.columns([1,5])
    with c1:
        try:
            st.image('logo.png', width=110)
        except:
            st.markdown('**ANA**')
    with c2:
        st.markdown(f'<div style="background:{VERDE};padding:12px;border-radius:8px;color:white;font-weight:bold;">NUCLEO PROT CIVILE ANA VARESE</div>', unsafe_allow_html=True)

def hdr_form(t):
    c1,c2 = st.columns([1,8])
    with c2:
        st.markdown(f'## {t}')

def to_excel(df):
    out = BytesIO()
    cols = [c for c in df.columns if c not in ['Foto','FotoBytes']]
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
            cols = [c for c in df.columns if c not in ['Foto','FotoBytes']]
            data = [cols]
            for _, row in df.iterrows():
                r = []
                for c in cols:
                    r.append(str(row.get(c,''))[:60])
                data.append(r)
            t = Table(data, repeatRows=1)
            t.setStyle(TableStyle([
                ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#1A5D1A')),
                ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
                ('ALIGN',(0,0),(-1,-1),'LEFT'),
                ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
                ('FONTSIZE',(0,0),(-1,-1),7),
                ('GRID',(0,0),(-1,-1),0.5,colors.grey)
            ]))
            story.append(t)
        doc.build(story)
        return buf.getvalue()
    except:
        return None

# INIT COMPLETO
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
        hdr_form('Dashboard - TASTI RAPIDI OK')
        c1,c2,c3,c4 = st.columns(4)
        c1.metric('Volontari', len(st.session_state.volontari))
        c2.metric('Radio', len(st.session_state.radio_db))
        c3.metric('Alias', len(st.session_state.alias_radio))
        c4.metric('Eventi', len(st.session_state.eventi))
        c1b,c2b,c3b,c4b = st.columns(4)
        c1b.metric('Check-in', len(st.session_state.checkin))
        c2b.metric('Brogliaccio', len(st.session_state.brogliaccio))
        c3b.metric('Interventi', len(st.session_state.interventi))
        c4b.metric('Emergenze', len(st.session_state.emergenze))
        st.divider()
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

    elif cur == 'Volontari (con foto)':
        hdr_form('VOLONTARI')
        t1,t2,t3,t4,t5 = st.tabs(['1.Anagrafica','2.Contatti','3.Ruolo','4.Foto','5.Elenco'])
        with t1:
            with st.form('vol_anag'):
                nome = st.text_input('Nome *')
                cognome = st.text_input('Cognome *')
                comune = st.text_input('Comune Residenza *')
                if st.form_submit_button('Salva Anagrafica', type='primary', use_container_width=True):
                    if nome and cognome and comune:
                        st.session_state.vol_form_data['Nome'] = nome
                        st.session_state.vol_form_data['Cognome'] = cognome
                        st.session_state.vol_form_data['Comune'] = comune
                        st.success('Anagrafica salvata')
        with t4:
            foto = st.file_uploader('Carica Foto', type=['png','jpg','jpeg'])
            with st.form('vol_foto'):
                if st.form_submit_button('SALVA VOLONTARIO COMPLETO', type='primary', use_container_width=True):
                    if not st.session_state.vol_form_data.get('Nome'):
                        st.error('Compila Anagrafica')
                    else:
                        v = {}
                        v['Nome'] = st.session_state.vol_form_data.get('Nome','')
                        v['Cognome'] = st.session_state.vol_form_data.get('Cognome','')
                        v['Comune'] = st.session_state.vol_form_data.get('Comune','')
                        v['Ruolo'] = st.session_state.vol_form_data.get('Ruolo','Volontario')
                        v['FotoBytes'] = foto.getvalue() if foto else None
                        v['Data'] = str(date.today())
                        st.session_state.volontari.append(v)
                        st.session_state.vol_form_data = {}
                        st.success('Volontario salvato!')
                        st.rerun()
        with t5:
            if st.session_state.volontari:
                st.dataframe(pd.DataFrame(st.session_state.volontari), use_container_width=True)

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
                lista_eventi = ['Nessuno'] + [x for x in lista_eventi if x]
                evento_sel = st.selectbox('EVENTO * (combo da Form Evento)', lista_eventi)
            else:
                evento_sel = st.text_input('EVENTO (crea prima Evento)')
            btn_alias = st.form_submit_button('Salva Alias Radio', type='primary', use_container_width=True)
            if btn_alias:
                if nome_alias and volontario_sel:
                    a = {}
                    a['NomeAlias'] = nome_alias
                    a['Volontario'] = volontario_sel
                    a['Evento'] = evento_sel
                    a['Data'] = str(date.today())
                    st.session_state.alias_radio.append(a)
                    st.success(f'Alias {nome_alias} salvato!')
        if st.session_state.alias_radio:
            st.dataframe(pd.DataFrame(st.session_state.alias_radio), use_container_width=True)

    elif cur == 'Brogliaccio':
        hdr_form('BROGLIACCIO BLINDATO SU EVENTO/EMERGENZA')
        if not st.session_state.brog_blindato:
            c1,c2 = st.columns(2)
            with c1:
                if st.session_state.eventi:
                    lista_ev = [e.get('NomeEvento','') for e in st.session_state.eventi]
                    ev = st.selectbox('EVENTO da blindare', ['Nessuno'] + lista_ev, key='ev_blind')
                else:
                    ev = 'Nessuno'
                if st.button('BLINDA BROGLIACCIO SU EVENTO', type='primary', use_container_width=True):
                    if ev!= 'Nessuno':
                        st.session_state.brog_evento_blindato = ev
                        st.session_state.brog_blindato = True
                        st.rerun()
            with c2:
                if st.session_state.emergenze:
                    lista_em = [e.get('Tipo','') + ' - ' + e.get('Luogo','') for e in st.session_state.emergenze]
                    em = st.selectbox('EMERGENZA da blindare', ['Nessuna'] + lista_em, key='em_blind')
                else:
                    em = 'Nessuna'
                if st.button('BLINDA BROGLIACCIO SU EMERGENZA', type='primary', use_container_width=True):
                    if em!= 'Nessuna':
                        st.session_state.brog_emergenza_blindata = em
                        st.session_state.brog_blindato = True
                        st.rerun()
        else:
            st.success(f"BLINDATO: {st.session_state.brog_evento_blindato or st.session_state.brog_emergenza_blindata}")
            if st.button('SBLOCCA BROGLIACCIO', type='primary', use_container_width=True):
                st.session_state.brog_blindato = False
                st.session_state.brog_evento_blindato = None
                st.session_state.brog_emergenza_blindata = None
                st.rerun()
        st.divider()
        if st.session_state.brog_blindato:
            with st.form('brog_form'):
                if st.session_state.brog_evento_blindato:
                    st.text_input('EVENTO BLINDATO', value=st.session_state.brog_evento_blindato, disabled=True)
                if st.session_state.brog_emergenza_blindata:
                    st.text_input('EMERGENZA BLINDATA', value=st.session_state.brog_emergenza_blindata, disabled=True)
                if st.session_state.alias_radio:
                    lista_alias = [a.get('NomeAlias','') for a in st.session_state.alias_radio]
                    mitt = st.selectbox('Mittente * (da Alias Radio NOME ALIAS)', lista_alias)
                    dest = st.selectbox('Destinatario * (da Alias Radio NOME ALIAS)', lista_alias)
                else:
                    mitt = st.text_input('Mittente *')
                    dest = st.text_input('Destinatario *')
                ora_b = st.text_input('Ora', value=datetime.now().strftime('%H:%M'))
                msg = st.text_area('Messaggio *')
                if st.form_submit_button('Salva Brogliaccio Blindato', type='primary', use_container_width=True):
                    if mitt and dest and msg:
                        b = {}
                        b['Ora'] = ora_b
                        b['Mittente'] = mitt
                        b['Destinatario'] = dest
                        b['Messaggio'] = msg
                        b['EventoBlindato'] = st.session_state.brog_evento_blindato if st.session_state.brog_evento_blindato else ''
                        b['EmergenzaBlindata'] = st.session_state.brog_emergenza_blindata if st.session_state.brog_emergenza_blindata else ''
                        b['Data'] = str(date.today())
                        st.session_state.brogliaccio.append(b)
                        st.success('Salvato')
        if st.session_state.brogliaccio:
            st.dataframe(pd.DataFrame(st.session_state.brogliaccio), use_container_width=True)

    elif cur == 'Eventi':
        hdr_form('EVENTI')
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
                    st.success(f'Evento {nome_e} creato - disponibile in Alias Radio')
        if st.session_state.eventi:
            st.dataframe(pd.DataFrame(st.session_state.eventi), use_container_width=True)

    elif cur == 'Emergenze':
        hdr_form('EMERGENZE')
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
                    st.success('Emergenza attivata')
        if st.session_state.emergenze:
            st.dataframe(pd.DataFrame(st.session_state.emergenze), use_container_width=True)

    elif cur == 'Check-in':
        hdr_form('CHECK-IN BLINDATO COME BROGLIACCIO')
        if not st.session_state.check_blindato:
            c1,c2 = st.columns(2)
            with c1:
                if st.session_state.eventi:
                    lista_ev = [e.get('NomeEvento','') for e in st.session_state.eventi]
                    ev = st.selectbox('EVENTO da blindare', ['Nessuno'] + lista_ev, key='ev_blind_check')
                else:
                    ev = 'Nessuno'
                if st.button('BLINDA CHECK-IN SU EVENTO', type='primary', use_container_width=True, key='bce'):
                    if ev!= 'Nessuno':
                        st.session_state.check_evento_blindato = ev
                        st.session_state.check_blindato = True
                        st.rerun()
            with c2:
                if st.session_state.emergenze:
                    lista_em = [e.get('Tipo','') + ' - ' + e.get('Luogo','') for e in st.session_state.emergenze]
                    em = st.selectbox('EMERGENZA da blindare', ['Nessuna'] + lista_em, key='em_blind_check')
                else:
                    em = 'Nessuna'
                if st.button('BLINDA CHECK-IN SU EMERGENZA', type='primary', use_container_width=True, key='bcm'):
                    if em!= 'Nessuna':
                        st.session_state.check_emergenza_blindata = em
