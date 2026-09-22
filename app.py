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
                data.append([str(row.get(c,''))[:60] for c in cols])
            t = Table(data, repeatRows=1)
            t.setStyle(TableStyle([
                ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#1A5D1A')),
                ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
                ('ALIGN',(0,0),(-1,-1),'LEFT'),
                ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
                ('FONTSIZE',(0,0),(-1,-1),7),
                ('GRID',(0,0),(-1,-1),0.5,colors.grey),
                ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.whitesmoke, colors.lightgrey])
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

# INIT COMPLETO CON MAPPA
for k in ['page','logged','menu','volontari','radio_db','eventi','emergenze','checkin','icone','postazioni','last_clicked','temp_markers','brogliaccio','mezzi','attrezzature','map_fullscreen','map_fullscreen2','vol_form_data','custom_defs','custom_data','alias_radio','brog_evento_blindato','brog_emergenza_blindata','brog_blindato','check_evento_blindato','check_emergenza_blindata','check_blindato','interventi','interventi_emergenza_blindata','interventi_blindato']:
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
        elif k in ['map_fullscreen','map_fullscreen2','brog_blindato','check_blindato','interventi_blindato']:
            st.session_state[k] = False
        elif k == 'vol_form_data':
            st.session_state[k] = {}
        elif k == 'custom_defs':
            st.session_state[k] = {}
        elif k == 'custom_data':
            st.session_state[k] = {}
        elif k in ['brog_evento_blindato','brog_emergenza_blindata','check_evento_blindato','check_emergenza_blindata','interventi_emergenza_blindata']:
            st.session_state[k] = None
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
    menu_base = ['Dashboard','Volontari (con foto)','DB Radio','Alias Radio','Brogliaccio','Eventi','Emergenze','Check-in','Interventi Emergenza','Mezzi','Attrezzature','Mappa Avanzata','Libreria Icone','Backup','Esporta','Crea Nuovo Form']
    menu_custom = list(st.session_state.custom_defs.keys())
    menu_tot = menu_base + menu_custom
    with st.sidebar:
        try:
            st.image('logo.png', width=120)
        except:
            pass
        st.markdown('### MENU')
        try:
            idx = menu_tot.index(st.session_state.menu)
        except:
            idx = 0
        menu = st.radio('Scegli:', menu_tot, index=idx)
        st.session_state.menu = menu
        if st.button('Logout', use_container_width=True):
            st.session_state.page = 'entra'
            st.rerun()

    m = st.session_state.menu

    if m == 'Dashboard':
        hdr_form('Dashboard - TASTI RAPIDI OK')
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
            if st.button('MAPPA', key='btn_mappa', use_container_width=True, type='primary'):
                st.session_state.menu = 'Mappa Avanzata'
                st.rerun()

    elif m == 'Volontari (con foto)':
        hdr_form('VOLONTARI - MASCHERA COMPLETA')
        t1,t2,t3,t4,t5 = st.tabs(['1.Anagrafica','2.Contatti','3.Ruolo','4.Foto','5.Elenco'])
        with t1:
            with st.form('vol_anag'):
                c1,c2 = st.columns(2)
                with c1:
                    nome = st.text_input('Nome *')
                    cognome = st.text_input('Cognome *')
                    cf = st.text_input('Codice Fiscale')
                with c2:
                    comune = st.text_input('Comune Residenza *')
                    data_n = st.date_input('Data Nascita', value=date(1980,1,1))
                    luogo_n = st.text_input('Luogo Nascita')
                if st.form_submit_button('Salva Anagrafica', type='primary', use_container_width=True):
                    if nome and cognome and comune:
                        st.session_state.vol_form_data['Nome'] = nome
                        st.session_state.vol_form_data['Cognome'] = cognome
                        st.session_state.vol_form_data['CF'] = cf
                        st.session_state.vol_form_data['Comune'] = comune
                        st.session_state.vol_form_data['DataNascita'] = str(data_n)
                        st.session_state.vol_form_data['LuogoNascita'] = luogo_n
                        st.success('Anagrafica salvata')
        with t2:
            with st.form('vol_cont'):
                c1,c2 = st.columns(2)
                with c1:
                    cell = st.text_input('Cellulare *')
                    tel = st.text_input('Telefono')
                    email = st.text_input('Email')
                with c2:
                    contatto_em = st.text_input('Contatto Emergenza')
                    tel_em = st.text_input('Tel Emergenza')
                if st.form_submit_button('Salva Contatti', type='primary', use_container_width=True):
                    if cell:
                        st.session_state.vol_form_data['Cellulare'] = cell
                        st.session_state.vol_form_data['Telefono'] = tel
                        st.session_state.vol_form_data['Email'] = email
                        st.session_state.vol_form_data['ContattoEm'] = contatto_em
                        st.session_state.vol_form_data['TelEm'] = tel_em
                        st.success('Contatti salvati')
        with t3:
            with st.form('vol_ruolo'):
                c1,c2 = st.columns(2)
                with c1:
                    ruolo = st.selectbox('Ruolo *', ['Volontario','Caposquadra','Coordinatore','Autista','Radio','Logistica','Sanitario','Altro'])
                    squadra = st.selectbox('Squadra', ['Alpini Caronno','Squadra A','Squadra B','Squadra C'])
                with c2:
                    spec = st.multiselect('Specializzazioni', ['AIB','Idrogeologico','Neve','Cinofilo','Motosega','Radio','Sanitario'])
                    pat = st.multiselect('Patenti', ['B','C','CE','D'])
                if st.form_submit_button('Salva Ruolo', type='primary', use_container_width=True):
                    st.session_state.vol_form_data['Ruolo'] = ruolo
                    st.session_state.vol_form_data['Squadra'] = squadra
                    st.session_state.vol_form_data['Special'] = ','.join(spec)
                    st.session_state.vol_form_data['Patenti'] = ','.join(pat)
                    st.success('Ruolo salvato')
        with t4:
            foto = st.file_uploader('Carica Foto *', type=['png','jpg','jpeg'])
            if foto:
                st.image(foto, width=200, caption='Preview OK')
            with st.form('vol_foto'):
                scadenza_doc = st.date_input('Scadenza Documento', value=date.today())
                if st.form_submit_button('SALVA VOLONTARIO COMPLETO', type='primary', use_container_width=True):
                    if not st.session_state.vol_form_data.get('Nome'):
                        st.error('Compila prima Anagrafica')
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
                        v['ScadenzaDoc'] = str(scadenza_doc)
                        v['Data'] = str(date.today())
                        st.session_state.volontari.append(v)
                        st.session_state.vol_form_data = {}
                        st.success('Volontario salvato!')
                        st.balloons()
                        st.rerun()
        with t5:
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
                st.dataframe(pd.DataFrame(lista), use_container_width=True, hide_index=True)

    elif m == 'Alias Radio':
        hdr_form('ALIAS RADIO - EVENTO COMBO DA FORM EVENTO OK')
        with st.form('alias_form'):
            nome_alias = st.text_input('NOME ALIAS *')
            if st.session_state.volontari:
                lista_vol = [f"{v.get('Nome','')} {v.get('Cognome','')}" for v in st.session_state.volontari]
                volontario_sel = st.selectbox('VOLONTARIO * (combo da Volontari)', lista_vol)
            else:
                volontario_sel = st.text_input('VOLONTARIO *')
            if st.session_state.postazioni:
                lista_post = ['Base','Avanzata'] + [p.get('Nome','') for p in st.session_state.postazioni]
                postazione_sel = st.selectbox('POSTAZIONE', lista_post)
            else:
                postazione_sel = st.selectbox('POSTAZIONE', ['Base','Avanzata'])
            if st.session_state.eventi:
                lista_eventi = [e.get('NomeEvento','') for e in st.session_state.eventi]
                lista_eventi = ['Nessuno'] + [x for x in lista_eventi if x]
                evento_sel = st.selectbox('EVENTO * (combo da Form Evento)', lista_eventi)
            else:
                evento_sel = st.text_input('EVENTO (crea prima Evento)')
            if st.session_state.emergenze:
                lista_emerg = [e.get('Tipo','') + ' - ' + e.get('Luogo','') for e in st.session_state.emergenze]
                lista_emerg = ['Nessuna'] + lista_emerg
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
        if st.session_state.alias_radio:
            st.dataframe(pd.DataFrame(st.session_state.alias_radio), use_container_width=True)

    elif m == 'Brogliaccio':
        hdr_form('BROGLIACCIO - BLINDATO SU EVENTO/EMERGENZA')
        st.markdown('### 1. Seleziona Evento o Emergenza e BLINDA')
        if not st.session_state.brog_blindato:
            c1,c2 = st.columns(2)
            with c1:
                st.markdown('**Scegli Evento da blindare**')
                if st.session_state.eventi:
                    lista_ev = [e.get('NomeEvento','') for e in st.session_state.eventi]
                    evento_blind = st.selectbox('EVENTO da associare e blindare', ['Nessuno'] + lista_ev, key='ev_blind')
                else:
                    st.warning('Nessun Evento - crea in Eventi')
                    evento_blind = 'Nessuno'
                if st.button('BLINDA BROGLIACCIO SU EVENTO', type='primary', use_container_width=True):
                    if evento_blind!= 'Nessuno':
                        st.session_state.brog_evento_blindato = evento_blind
                        st.session_state.brog_emergenza_blindata = None
                        st.session_state.brog_blindato = True
                        st.rerun()
            with c2:
                st.markdown('**Oppure scegli Emergenza da blindare**')
                if st.session_state.emergenze:
                    lista_em = [e.get('Tipo','') + ' - ' + e.get('Luogo','') for e in st.session_state.emergenze]
                    emerg_blind = st.selectbox('EMERGENZA da associare e blindare', ['Nessuna'] + lista_em, key='em_blind')
                else:
                    st.warning('Nessuna Emergenza - crea in Emergenze')
                    emerg_blind = 'Nessuna'
                if st.button('BLINDA BROGLIACCIO SU EMERGENZA', type='primary', use_container_width=True):
                    if emerg_blind!= 'Nessuna':
                        st.session_state.brog_emergenza_blindata = emerg_blind
                        st.session_state.brog_evento_blindato = None
                        st.session_state.brog_blindato = True
                        st.rerun()
        else:
            if st.session_state.brog_evento_blindato:
                st.success(f"BLINDATO SU EVENTO: {st.session_state.brog_evento_blindato} - Resta blindato finche non sblocchi tu")
            if st.session_state.brog_emergenza_blindata:
                st.success(f"BLINDATO SU EMERGENZA: {st.session_state.brog_emergenza_blindata} - Resta blindato finche non sblocchi tu")
            if st.button('SBLOCCA BROGLIACCIO', type='primary', use_container_width=True):
                st.session_state.brog_blindato = False
                st.session_state.brog_evento_blindato = None
                st.session_state.brog_emergenza_blindata = None
                st.rerun()
        st.divider()
        st.markdown('### 2. Maschera Brogliaccio - Mittente/Destinatario da Alias Radio')
        if not st.session_state.brog_blindato:
            st.warning('Prima BLINDA Brogliaccio su Evento o Emergenza')
        else:
            with st.form('brog_form'):
                if st.session_state.brog_evento_blindato:
                    st.text_input('EVENTO BLINDATO', value=st.session_state.brog_evento_blindato, disabled=True)
                if st.session_state.brog_emergenza_blindata:
                    st.text_input('EMERGENZA BLINDATA', value=st.session_state.brog_emergenza_blindata, disabled=True)
                if st.session_state.alias_radio:
                    lista_alias = [a.get('NomeAlias','') for a in st.session_state.alias_radio]
                    lista_alias = [x for x in lista_alias if x]
                    mitt = st.selectbox('Mittente * (da Alias Radio - NOME ALIAS)', lista_alias)
                    dest = st.selectbox('Destinatario * (da Alias Radio - NOME ALIAS)', lista_alias)
                else:
                    mitt = st.text_input('Mittente * (crea prima Alias)')
                    dest = st.text_input('Destinatario * (crea prima Alias)')
                canale_b = st.text_input('Canale Radio')
                priorita = st.selectbox('Priorita', ['Bassa','Normale','Alta','Urgenza'])
                ora_b = st.text_input('Ora', value=datetime.now().strftime('%H:%M'))
                data_b = st.date_input('Data', value=date.today())
                msg = st.text_area('Messaggio *')
                if st.form_submit_button('Salva Brogliaccio Blindato', type='primary', use_container_width=True):
                    if mitt and dest and msg:
                        b = {}
                        b['Data'] = str(data_b)
                        b['Ora'] = ora_b
                        b['EventoBlindato'] = st.session_state.brog_evento_blindato if st.session_state.brog_evento_blindato else ''
                        b['EmergenzaBlindata'] = st.session_state.brog_emergenza_blindata if st.session_state.brog_emergenza_blindata else ''
                        b['Mittente'] = mitt
                        b['Destinatario'] = dest
                        b['Canale'] = canale_b
                        b['Priorita'] = priorita
                        b['Messaggio'] = msg
                        st.session_state.brogliaccio.append(b)
                        st.success(f'Brogliaccio {mitt} -> {dest} salvato')

    elif m == 'Eventi':
        hdr_form('EVENTI')
        with st.form('eventi_form'):
            nome_e = st.text_input('NOME EVENTO *')
            luogo_e = st.text_input('Luogo *')
            tipo_e = st.selectbox('Tipo', ['Esercitazione','Emergenza','Prevenzione','Manifestazione','Formazione','Altro'])
            if st.form_submit_button('Crea Evento', type='primary', use_container_width=True):
                if nome_e and luogo_e:
                    e = {}
                    e['NomeEvento'] = nome_e
                    e['Luogo'] = luogo_e
                    e['Tipo'] = tipo_e
                    e['Data'] = str(date.today())
                    st.session_state.eventi.append(e)
                    st.success(f'Evento {nome_e} creato - disponibile in Alias Radio, Brogliaccio, Check-in')
        if st.session_state.eventi:
            st.dataframe(pd.DataFrame(st.session_state.eventi), use_container_width=True)

    elif m == 'Emergenze':
        hdr_form('EMERGENZE')
        with st.form('em_form'):
            tipo_em = st.selectbox('Tipo *', ['Alluvione','Frana','Incendio','Terremoto','Neve','Ricerca','Altro'])
            luogo_em = st.text_input('Luogo *')
            descr_em = st.text_area('Descrizione *')
            if st.form_submit_button('Attiva Emergenza', type='primary', use_container_width=True):
                if luogo_em and descr_em:
                    em = {}
                    em['Tipo'] = tipo_em
                    em['Luogo'] = luogo_em
                    em['Descrizione'] = descr_em
                    em['Data'] = str(date.today())
                    st.session_state.emergenze.append(em)
                    st.success('Emergenza attivata - disponibile per blindare')
        if st.session_state.emergenze:
            st.dataframe(pd.DataFrame(st.session_state.emergenze), use_container_width=True)

    elif m == 'Check-in':
        hdr_form('CHECK-IN - BLINDATO SU EVENTO/EMERGENZA')
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
                        st.session_state.check_emergenza_blindata = None
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
                        st.session_state.check_evento_blindato = None
                        st.session_state.check_blindato = True
                        st.rerun()
        else:
            if st.session_state.check_evento_blindato:
                st.success(f"CHECK-IN BLINDATO SU EVENTO: {st.session_state.check_evento_blindato} - Resta blindato finche non sblocchi tu")
            if st.session_state.check_emergenza_blindata:
                st.success(f"CHECK-IN BLINDATO SU EMERGENZA: {st.session_state.check_emergenza_blindata} - Resta blindato finche non sblocchi tu")
            if st.button('SBLOCCA CHECK-IN', type='primary', use_container_width=True, key='sbc'):
                st.session_state.check_blindato = False
                st.session_state.check_evento_blindato = None
                st.session_state.check_emergenza_blindata = None
                st.rerun()
        st.divider()
        if st.session_state.check_blindato:
            if not st.session_state.volontari:
                st.warning('Inserisci prima Volontario')
            else:
                with st.form('check_form'):
                    if st.session_state.check_evento_blindato:
                        st.text_input('EVENTO BLINDATO', value=st.session_state.check_evento_blindato, disabled=True)
                    if st.session_state.check_emergenza_blindata:
                        st.text_input('EMERGENZA BLINDATA', value=st.session_state.check_emergenza_blindata, disabled=True)
                    vol_sel = st.selectbox('Volontario *', [f"{v.get('Nome','')} {v.get('Cognome','')}" for v in st.session_state.volontari])
                    if st.session_state.postazioni:
                        lista_post = ['Base','Avanzata'] + [p.get('Nome','') for p in st.session_state.postazioni]
                        post_sel = st.selectbox('Postazione *', lista_post)
                    else:
                        post_sel = st.selectbox('Postazione *', ['Base','Avanzata'])
                    ora_check = st.text_input('Ora', value=datetime.now().strftime('%H:%M'))
                    note_check = st.text_input('Note')
                    if st.form_submit_button('Registra Check-in Blindato', type='primary', use_container_width=True):
                        c = {}
                        c['Data'] = str(date.today())
                        c['Ora'] = ora_check
                        c['EventoBlindato'] = st.session_state.check_evento_blindato if st.session_state.check_evento_blindato else ''
                        c['EmergenzaBlindata'] = st.session_state.check_emergenza_blindata if st.session_state.check_emergenza_blindata else ''
                        c['Volontario'] = vol_sel
                        c['Postazione'] = post_sel
                        c['Note'] = note_check
                        st.session_state.checkin.append(c)
                        st.success(f'Check-in {vol_sel} registrato blindato')

    elif m == 'Interventi Emergenza':
        hdr_form('INTERVENTI EMERGENZA - COLLEGATO A EMERGENZA BLINDATA + STATO')
        if not st.session_state.interventi_blindato:
            if st.session_state.emergenze:
                lista_em = [e.get('Tipo','') + ' - ' + e.get('Luogo','') for e in st.session_state.emergenze]
                em = st.selectbox('EMERGENZA da associare e blindare per Interventi', ['Nessuna'] + lista_em, key='em_blind_int')
            else:
                st.warning('Nessuna Emergenza - crea prima in Emergenze')
                em = 'Nessuna'
            if st.button('BLINDA INTERVENTI SU EMERGENZA', type='primary', use_container_width=True):
                if em!= 'Nessuna':
                    st.session_state.interventi_emergenza_blindata = em
                    st.session_state.interventi_blindato = True
                    st.rerun()
        else:
            st.success(f"INTERVENTI BLINDATO SU EMERGENZA: {st.session_state.interventi_emergenza_blindata} - Resta blindato finche non sblocchi tu")
            if st.button('SBLOCCA INTERVENTI', type='primary', use_container_width=True):
                st.session_state.interventi_blindato = False
                st.session_state.interventi_emergenza_blindata = None
                st.rerun()
        st.divider()
        if st.session_state.interventi_blindato:
            with st.form('form_int'):
                st.text_input('EMERGENZA BLINDATA (collegata e bloccata)', value=st.session_state.interventi_emergenza_blindata, disabled=True)
                c1,c2,c3 = st.columns(3)
                with c1:
                    data_int = st.date_input('Data *', value=date.today())
                    ora_int = st.time_input('Ora *', value=datetime.now().time())
                with c2:
                    comune_int = st.text_input('Comune *')
                    via_int = st.text_input('Via *')
                with c3:
                    civico_int = st.text_input('Civico')
                    odv_int = st.selectbox('ODV Operativa *', ['ANA Varese','ANA Sezione Varese','Protezione Civile Lombardia','Croce Rossa','Altro'])
                c4,c5 = st.columns(2)
                with c4:
                    stato_int = st.selectbox('STATO INTERVENTO *', ['Operativo','In Stand By','Chiuso','In Corso','Completato','Annullato','Sospeso','In Attesa'])
                with c5:
                    priorita_int = st.selectbox('Priorita', ['Bassa','Media','Alta','Urgente'])
                azione_int = st.text_area('Azione Intervento *', height=120)
                note_int = st.text_input('Note')
                if st.form_submit_button('SALVA INTERVENTO COLLEGATO A EMERGENZA BLINDATA', use_container_width=True, type='primary'):
                    if comune_int and via_int and azione_int:
                        iv = {}
                        iv['Data'] = str(data_int)
                        iv['Ora'] = str(ora_int)
                        iv['EmergenzaBlindata'] = st.session_state.interventi_emergenza_blindata
                        iv['Comune'] = comune_int
                        iv['Via'] = via_int
                        iv['Civico'] = civico_int
                        iv['ODV'] = odv_int
                        iv['Stato'] = stato_int
                        iv['Priorita'] = priorita_int
                        iv['Azione'] = azione_int
                        iv['Note'] = note_int
                        st.session_state.interventi.append(iv)
                        st.success(f'Intervento {stato_int} salvato collegato a Emergenza')
                        st.balloons()

    elif m == 'Mappa Avanzata':
        hdr_form('MAPPA AVANZATA - BUON LAVORO - RIPRISTINATA OK')
        st.info('OSM default, fullscreen + - ESC, click coord, icona marker - TUTTO IL LAVORO RIPRISTINATO')
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
        if st.session_state.postazioni:
            df_post = pd.DataFrame(st.session_state.postazioni)
            st.dataframe(df_post, use_container_width=True)
            c1,c2 = st.columns(2)
            pdf = to_pdf(df_post, 'Postazioni ANA Varese')
            if pdf:
                c1.download_button('PDF Postazioni', pdf, file_name='postazioni.pdf', mime='application/pdf', use_container_width=True)
            c2.download_button('Excel Postazioni', to_excel(df_post), file_name='postazioni.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', use_container_width=True)

    elif m == 'Libreria Icone':
        hdr_form('LIBRERIA ICONE - MASCHERA RIPRISTINATA')
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
        hdr_form('BACKUP - TUTTI I DATI + PDF')
        datasets = {}
        datasets['Volontari'] = st.session_state.volontari
        datasets['Radio'] = st.session_state.radio_db
        datasets['AliasRadio'] = st.session_state.alias_radio
        datasets['Brogliaccio'] = st.session_state.brogliaccio
        datasets['Eventi'] = st.session_state.eventi
        datasets['Emergenze'] = st.session_state.emergenze
        datasets['Checkin'] = st.session_state.checkin
        datasets['Interventi'] = st.session_state.interventi
        datasets['Mezzi'] = st.session_state.mezzi
        datasets['Attrezzature'] = st.session_state.attrezzature
        datasets['Postazioni'] = st.session_state.postazioni
        c1,c2 = st.columns(2)
        with c1:
            if any(datasets.values()):
                st.download_button('EXPORT TOTALE EXCEL', to_excel_multi(datasets), file_name=f'backup_TUTTI_{date.today()}.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', use_container_width=True, type='primary')
