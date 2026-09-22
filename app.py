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
        st.markdown(f'<div style="background:{VERDE};padding:12px;border-radius:8px;color:white;font-weight:bold;font-size:18px;">NUCLEO PROT CIVILE ANA VARESE - Squadra Alpini Caronno</div>', unsafe_allow_html=True)

def hdr_form(titolo):
    c1,c2 = st.columns([1,8])
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
        story.append(Paragraph(f"<b>{titolo} - ANA Varese - {date.today()}</b>", styles['Title']))
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
                ('GRID',(0,0),(-1,-1),0.5,colors.grey)
            ]))
            story.append(t)
        doc.build(story)
        return buf.getvalue()
    except:
        return None

# INIT TUTTI I FORM
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
        st.markdown(f'<h2 style="text-align:center;color:{VERDE};">GESTIONALE ANA VARESE</h2>', unsafe_allow_html=True)
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
        c3.metric('Alias Radio', len(st.session_state.alias_radio))
        c4.metric('Eventi', len(st.session_state.eventi))
        c1b,c2b,c3b,c4b = st.columns(4)
        c1b.metric('Check-in', len(st.session_state.checkin))
        c2b.metric('Brogliaccio', len(st.session_state.brogliaccio))
        c3b.metric('Interventi', len(st.session_state.interventi))
        c4b.metric('Emergenze', len(st.session_state.emergenze))

    elif cur == 'Volontari (con foto)':
        hdr_form('VOLONTARI (con foto) - MASCHERA COMPLETA')
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
                    squadra = st.selectbox('Squadra', ['Alpini Caronno','Squadra A','Squadra B'])
                with c2:
                    spec = st.multiselect('Specializzazioni', ['AIB','Idrogeologico','Neve','Cinofilo','Motosega','Radio'])
                    pat = st.multiselect('Patenti', ['B','C','CE','D'])
                if st.form_submit_button('Salva Ruolo', type='primary', use_container_width=True):
                    st.session_state.vol_form_data['Ruolo'] = ruolo
                    st.session_state.vol_form_data['Squadra'] = squadra
                    st.session_state.vol_form_data['Special'] = ','.join(spec)
                    st.session_state.vol_form_data['Patenti'] = ','.join(pat)
                    st.success('Ruolo salvato')
        with t4:
            foto = st.file_uploader('Carica Foto', type=['png','jpg','jpeg'])
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
            else:
                st.warning('Nessun volontario')

    elif cur == 'DB Radio':
        hdr_form('DB RADIO - MASCHERA')
        with st.form('radio_form'):
            modello = st.text_input('Modello *')
            matricola = st.text_input('Matricola *')
            tipo = st.selectbox('Tipo *', ['DMR','PMR446','TETRA','VHF','UHF','CB','Altro'])
            freq = st.text_input('Frequenza')
            canale = st.text_input('Canale')
            stato_r = st.selectbox('Stato', ['Disponibile','In Uso','Manutenzione'])
            note_r = st.text_area('Note')
            if st.form_submit_button('Salva Radio', type='primary', use_container_width=True):
                if modello and matricola:
                    r = {'Modello':modello,'Matricola':matricola,'Tipo':tipo,'Frequenza':freq,'Canale':canale,'Stato':stato_r,'Note':note_r}
                    st.session_state.radio_db.append(r)
                    st.success('Radio salvata')
        if st.session_state.radio_db:
            st.dataframe(pd.DataFrame(st.session_state.radio_db), use_container_width=True)

    elif cur == 'Alias Radio':
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
                    a = {'NomeAlias':nome_alias,'Volontario':volontario_sel,'Postazione':postazione_sel,'Evento':evento_sel,'Emergenza':emergenza_sel,'Note':note_alias,'Data':str(date.today())}
                    st.session_state.alias_radio.append(a)
                    st.success(f'Alias {nome_alias} salvato!')
        if st.session_state.alias_radio:
            st.dataframe(pd.DataFrame(st.session_state.alias_radio), use_container_width=True)

    elif cur == 'Brogliaccio':
        hdr_form('BROGLIACCIO - BLINDATO SU EVENTO/EMERGENZA')
        if not st.session_state.brog_blindato:
            c1,c2 = st.columns(2)
            with c1:
                if st.session_state.eventi:
                    lista_ev = [e.get('NomeEvento','') for e in st.session_state.eventi]
                    ev = st.selectbox('EVENTO da blindare', ['Nessuno'] + lista_ev, key='ev_blind')
                else:
                    st.warning('Nessun Evento - crea in Eventi')
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
                    st.warning('Nessuna Emergenza - crea in Emergenze')
                    em = 'Nessuna'
                if st.button('BLINDA BROGLIACCIO SU EMERGENZA', type='primary', use_container_width=True):
                    if em!= 'Nessuna':
                        st.session_state.brog_emergenza_blindata = em
                        st.session_state.brog_blindato = True
                        st.rerun()
        else:
            st.success(f"BLINDATO SU: {st.session_state.brog_evento_blindato or st.session_state.brog_emergenza_blindata} - Resta blindato finche non sblocchi tu")
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
                        b = {'Data':str(data_b),'Ora':ora_b,'EventoBlindato':st.session_state.brog_evento_blindato if st.session_state.brog_evento_blindato else '','EmergenzaBlindata':st.session_state.brog_emergenza_blindata if st.session_state.brog_emergenza_blindata else '','Mittente':mitt,'Destinatario':dest,'Canale':canale_b,'Priorita':priorita,'Messaggio':msg}
                        st.session_state.brogliaccio.append(b)
                        st.success(f'Brogliaccio {mitt} -> {dest} salvato')
        if st.session_state.brogliaccio:
            st.dataframe(pd.DataFrame(st.session_state.brogliaccio), use_container_width=True)

    elif cur == 'Eventi':
        hdr_form('EVENTI - MASCHERA')
        with st.form('eventi_form'):
            nome_e = st.text_input('NOME EVENTO *')
            luogo_e = st.text_input('Luogo *')
            tipo_e = st.selectbox('Tipo', ['Esercitazione','Emergenza','Prevenzione','Manifestazione','Formazione','Altro'])
            if st.form_submit_button('Crea Evento', type='primary', use_container_width=True):
                if nome_e and luogo_e:
                    e = {'NomeEvento':nome_e,'Luogo':luogo_e,'Tipo':tipo_e,'Data':str(date.today())}
                    st.session_state.eventi.append(e)
                    st.success(f'Evento {nome_e} creato - disponibile in Alias Radio, Brogliaccio, Check-in')
        if st.session_state.eventi:
            st.dataframe(pd.DataFrame(st.session_state.eventi), use_container_width=True)

    elif cur == 'Emergenze':
        hdr_form('EMERGENZE - MASCHERA')
        with st.form('em_form'):
            tipo_em = st.selectbox('Tipo *', ['Alluvione','Frana','Incendio','Terremoto','Neve','Ricerca','Altro'])
            luogo_em = st.text_input('Luogo *')
            descr_em = st.text_area('Descrizione *')
            if st.form_submit_button('Attiva Emergenza', type='primary', use_container_width=True):
                if luogo_em and descr_em:
                    em = {'Tipo':tipo_em,'Luogo':luogo_em,'Descrizione':descr_em,'Data':str(date.today())}
                    st.session_state.emergenze.append(em)
                    st.success('Emergenza attivata - disponibile per blindare Brogliaccio, Check-in, Interventi')
        if st.session_state.emergenze:
            st.dataframe(pd.DataFrame(st.session_state.emergenze), use_container_width=True)

    elif cur == 'Check-in':
        hdr_form('CHECK-IN - BLINDATO COME BROGLIACCIO OK')
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
                        st.session_state.check_blindato = True
                        st.rerun()
        else:
            st.success(f"CHECK-IN BLINDATO: {st.session_state.check_evento_blindato or st.session_state.check_emergenza_blindata} - Resta blindato finche non sblocchi tu")
            if st.button('SBLOCCA CHECK-IN', type='primary', use_container_width=True, key='sbc'):
                st.session_state.check_blindato = False
                st.session_state.check_evento_blindato = None
                st.session_state.check_emergenza_blindata = None
                st.rerun()
        st.divider()
        st.markdown('### 2. Maschera Check-in Blindato')
        if not st.session_state.check_blindato:
            st.warning('Prima BLINDA Check-in su Evento o Emergenza')
        else:
            if not st.session_state.volontari:
                st.warning('Inserisci prima Volontario in Volontari')
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
                        c = {'Data':str(date.today()),'Ora':ora_check,'EventoBlindato':st.session_state.check_evento_blindato if st.session_state.check_evento_blindato else '','EmergenzaBlindata':st.session_state.check_emergenza_blindata if st.session_state.check_emergenza_blindata else '','Volontario':vol_sel,'Postazione':post_sel,'Note':note_check}
                        st.session_state.checkin.append(c)
                        st.success(f'Check-in {vol_sel} registrato blindato')
        if st.session_state.checkin:
            st.dataframe(pd.DataFrame(st.session_state.checkin), use_container_width=True)

    elif cur == 'Interventi Emergenza':
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
        st.markdown('### 2. Maschera Interventi - Collegata a Emergenza Blindata')
        if not st.session_state.interventi_blindato:
            st.warning('Prima BLINDA Interventi su Emergenza')
        else:
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
                        iv = {'Data':str(data_int),'Ora':str(ora_int),'EmergenzaBlindata':st.session_state.interventi_emergenza_blindata,'Comune':comune_int,'Via':via_int,'Civico':civico_int,'ODV':odv_int,'Stato':stato_int,'Priorita':priorita_int,'Azione':azione_int,'Note':note_int}
                        st.session_state.interventi.append(iv)
                        st.success(f'Intervento {stato_int} salvato collegato a Emergenza')
                        st.balloons()
        if st.session_state.interventi:
            st.dataframe(pd.DataFrame(st.session_state.interventi), use_container_width=True)

    elif cur == 'Mezzi':
        hdr_form('MEZZI - MASCHERA')
        with st.form('mezzi_form'):
            targa = st.text_input('Targa *')
            tipo_m = st.selectbox('Tipo *', ['Fuoristrada','Furgone','Autocarro','Ambulanza','Pulmino','Altro'])
            if st.form_submit_button('Salva Mezzo', type='primary', use_container_width=True):
                if targa and tipo_m:
                    mz = {'Targa':targa,'Tipo':tipo_m}
                    st.session_state.mezzi.append(mz)
                    st.success('Mezzo salvato')
        if st.session_state.mezzi:
            st.dataframe(pd.DataFrame(st.session_state.mezzi), use_container_width=True)

    elif cur == 'Attrezzature':
        hdr_form('ATTREZZATURE - MASCHERA')
        with st.form('attr_form'):
            nome_a = st.text_input('Attrezzatura *')
            quant = st.number_input('Quantita *', min_value=1, value=1)
            if st.form_submit_button('Salva Attrezzatura', type='primary', use_container_width=True):
                if nome_a:
                    at = {'Attrezzatura':nome_a,'Quantita':quant}
                    st.session_state.attrezzature.append(at)
                    st.success('Attrezzatura salvata')
        if st.session_state.attrezzature:
            st.dataframe(pd.DataFrame(st.session_state.attrezzature), use_container_width=True)

    elif cur == 'Backup':
        hdr_form('BACKUP')
        st.download_button('EXPORT TOTALE EXCEL', to_excel_multi({'Volontari':st.session_state.volontari,'Radio':st.session_state.radio_db,'Alias':st.session_state.alias_radio,'Brogliaccio':st.session_state.brogliaccio,'Eventi':st.session_state.eventi,'Emergenze':st.session_state.emergenze,'Checkin':st.session_state.checkin,'Interventi':st.session_state.interventi}), file_name=f'backup_{date.today()}.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', use_container_width=True, type='primary')
