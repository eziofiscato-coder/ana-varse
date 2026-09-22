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
    if not cols:
        cols = list(df.columns)
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
            cols = [c for c in df.columns if c not in ['Foto','FotoBytes','FileBytes']]
            cols = cols[:8]
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
            ]))
            story.append(t)
        doc.build(story)
        return buf.getvalue()
    except Exception as e:
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

# INIT - TUTTI I FORM CON PIU RIGHE
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
        st.markdown(f'<h2 style="text-align:center;color:{VERDE};">GESTIONALE ANA VARESE - 1000+ RIGHE</h2>', unsafe_allow_html=True)
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
        st.markdown('### MENU - 15 FORM')
        try:
            idx = menu_base.index(st.session_state.menu)
        except:
            idx = 0
        m = st.radio('Scegli form:', menu_base, index=idx)
        st.session_state.menu = m
        if st.button('Logout', use_container_width=True):
            st.session_state.page = 'entra'
            st.rerun()
    cur = st.session_state.menu

    if cur == 'Dashboard':
        hdr_form('Dashboard - TASTI RAPIDI - MENU VELOCE - 1000+ RIGHE')
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
        c1c,c2c,c3c,c4c = st.columns(4)
        c1c.metric('Mezzi', len(st.session_state.mezzi))
        c2c.metric('Attrezzature', len(st.session_state.attrezzature))
        c3c.metric('Postazioni', len(st.session_state.postazioni))
        c4c.metric('Icone', len(st.session_state.icone))
        st.divider()
        st.markdown('### TASTI RAPIDI - MENU VELOCE - CLICCA E APRE FORM')
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

    elif cur == 'Volontari (con foto)':
        hdr_form('VOLONTARI (con foto) - 5 TAB - MASCHERA COMPLETA')
        t1,t2,t3,t4,t5 = st.tabs(['1.Anagrafica','2.Contatti','3.Ruolo','4.Foto','5.Elenco + Import'])
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
                c1,c2 = st.columns(2)
                c1.download_button('Excel Volontari', to_excel(pd.DataFrame(lista)), file_name='volontari.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', use_container_width=True)
                pdf = to_pdf(pd.DataFrame(lista), 'Volontari')
                if pdf:
                    c2.download_button('PDF Volontari', pdf, file_name='volontari.pdf', mime='application/pdf', use_container_width=True)
            st.divider()
            st.markdown('### IMPORT Volontari da Excel')
            up_vol = st.file_uploader('Carica Excel Volontari', type=['xlsx'], key='up_vol')
            if up_vol:
                try:
                    df_imp = pd.read_excel(up_vol)
                    st.write(df_imp.head())
                    if st.button(f'Importa {len(df_imp)} Volontari', key='imp_vol'):
                        for _, row in df_imp.iterrows():
                            st.session_state.volontari.append(row.to_dict())
                        st.success(f'Importati {len(df_imp)}')
                        st.rerun()
                except Exception as e:
                    st.error(f'Errore: {e}')

    elif cur == 'DB Radio':
        hdr_form('DB RADIO - MASCHERA COMPLETA - PIU RIGHE RIPRISTINATA')
        with st.form('radio_form'):
            st.markdown('#### Dati Radio - Maschera Completa')
            c1,c2,c3 = st.columns(3)
            with c1:
                modello = st.text_input('Modello *')
                matricola = st.text_input('Matricola *')
                tipo = st.selectbox('Tipo *', ['DMR','PMR446','TETRA','VHF','UHF','CB','Altro'])
            with c2:
                freq = st.text_input('Frequenza')
                canale = st.text_input('Canale')
                codice = st.text_input('Codice Radio')
            with c3:
                stato_r = st.selectbox('Stato', ['Disponibile','In Uso','Manutenzione','Guasta','Assegnata'])
                assegnato = st.text_input('Assegnato a')
                data_acq = st.date_input('Data Acquisto', value=date.today())
            c4,c5 = st.columns(2)
            with c4:
                accessori = st.multiselect('Accessori', ['Batteria','Caricabatteria','Auricolare','Microfono','Antenna','Custodia'])
            with c5:
                note_r = st.text_area('Note', height=80)
            if st.form_submit_button('Salva Radio', type='primary', use_container_width=True):
                if modello and matricola:
                    r = {'Modello':modello,'Matricola':matricola,'Tipo':tipo,'Frequenza':freq,'Canale':canale,'Codice':codice,'Stato':stato_r,'Assegnato':assegnato,'DataAcquisto':str(data_acq),'Accessori':','.join(accessori),'Note':note_r,'Data':str(date.today())}
                    st.session_state.radio_db.append(r)
                    st.success(f'Radio {modello} {matricola} salvata!')
                    st.balloons()
        if st.session_state.radio_db:
            st.divider()
            st.dataframe(pd.DataFrame(st.session_state.radio_db), use_container_width=True)
            c1,c2,c3 = st.columns(3)
            c1.download_button('Excel Radio', to_excel(pd.DataFrame(st.session_state.radio_db)), file_name='radio.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', use_container_width=True)
            pdf = to_pdf(pd.DataFrame(st.session_state.radio_db), 'DB Radio ANA Varese')
            if pdf:
                c2.download_button('PDF Radio', pdf, file_name='radio.pdf', mime='application/pdf', use_container_width=True)
            up_r = c3.file_uploader('Import Radio Excel', type=['xlsx'], key='up_radio')
            if up_r:
                try:
                    df_imp = pd.read_excel(up_r)
                    if st.button(f'Importa {len(df_imp)} Radio'):
                        for _, row in df_imp.iterrows():
                            st.session_state.radio_db.append(row.to_dict())
                        st.success('Importate')
                        st.rerun()
                except Exception as e:
                    st.error(f'{e}')

    elif cur == 'Alias Radio':
        hdr_form('ALIAS RADIO - EVENTO COMBO DA FORM EVENTO OK - PIU RIGHE')
        with st.form('alias_form'):
            nome_alias = st.text_input('NOME ALIAS *')
            if st.session_state.volontari:
                lista_vol = [f"{v.get('Nome','')} {v.get('Cognome','')}" for v in st.session_state.volontari]
                volontario_sel = st.selectbox('VOLONTARIO * (combo da Volontari)', lista_vol)
            else:
                volontario_sel = st.text_input('VOLONTARIO *')
            if st.session_state.postazioni:
                lista_post = ['Base','Avanzata','Posto 1','Posto 2'] + [p.get('Nome','') for p in st.session_state.postazioni]
                postazione_sel = st.selectbox('POSTAZIONE', lista_post)
            else:
                postazione_sel = st.selectbox('POSTAZIONE', ['Base','Avanzata','Posto 1','Posto 2'])
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
            if st.session_state.radio_db:
                lista_radio = [f"{r.get('Modello','')} {r.get('Matricola','')}" for r in st.session_state.radio_db]
                radio_sel = st.selectbox('RADIO ASSEGNATA', ['Nessuna'] + lista_radio)
            else:
                radio_sel = st.text_input('RADIO')
            note_alias = st.text_area('Note')
            if st.form_submit_button('Salva Alias Radio', type='primary', use_container_width=True):
                if nome_alias and volontario_sel:
                    a = {'NomeAlias':nome_alias,'Volontario':volontario_sel,'Postazione':postazione_sel,'Evento':evento_sel,'Emergenza':emergenza_sel,'Radio':radio_sel,'Note':note_alias,'Data':str(date.today())}
                    st.session_state.alias_radio.append(a)
                    st.success(f'Alias {nome_alias} salvato!')
                    st.balloons()
        if st.session_state.alias_radio:
            st.dataframe(pd.DataFrame(st.session_state.alias_radio), use_container_width=True)

    elif cur == 'Brogliaccio':
        hdr_form('BROGLIACCIO - BLINDATO SU EVENTO/EMERGENZA - PIU RIGHE')
        if not st.session_state.brog_blindato:
            c1,c2 = st.columns(2)
            with c1:
                if st.session_state.eventi:
                    lista_ev = [e.get('NomeEvento','') for e in st.session_state.eventi]
                    ev = st.selectbox('EVENTO da associare e blindare', ['Nessuno'] + lista_ev, key='ev_blind')
                else:
                    st.warning('Nessun Evento - crea in Eventi')
                    ev = 'Nessuno'
                if st.button('BLINDA BROGLIACCIO SU EVENTO', type='primary', use_container_width=True):
                    if ev!= 'Nessuno':
                        st.session_state.brog_evento_blindato = ev
                        st.session_state.brog_emergenza_blindata = None
                        st.session_state.brog_blindato = True
                        st.rerun()
            with c2:
                if st.session_state.emergenze:
                    lista_em = [e.get('Tipo','') + ' - ' + e.get('Luogo','') for e in st.session_state.emergenze]
                    em = st.selectbox('EMERGENZA da associare e blindare', ['Nessuna'] + lista_em, key='em_blind')
                else:
                    st.warning('Nessuna Emergenza - crea in Emergenze')
                    em = 'Nessuna'
                if st.button('BLINDA BROGLIACCIO SU EMERGENZA', type='primary', use_container_width=True):
                    if em!= 'Nessuna':
                        st.session_state.brog_emergenza_blindata = em
                        st.session_state.brog_evento_blindato = None
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
        if not st.session_state.brog_blindato:
            st.warning('Prima BLINDA Brogliaccio su Evento o Emergenza')
        else:
            with st.form('brog_form'):
                if st.session_state.brog_evento_blindato:
                    st.text_input('EVENTO BLINDATO (associato e bloccato)', value=st.session_state.brog_evento_blindato, disabled=True)
                if st.session_state.brog_emergenza_blindata:
                    st.text_input('EMERGENZA BLINDATA (associata e bloccata)', value=st.session_state.brog_emergenza_blindata, disabled=True)
                if st.session_state.alias_radio:
                    lista_alias = [a.get('NomeAlias','') for a in st.session_state.alias_radio]
                    lista_alias = [x for x in lista_alias if x]
                    mitt = st.selectbox('Mittente * (da Alias Radio - NOME ALIAS)', lista_alias)
                    dest = st.selectbox('Destinatario * (da Alias Radio - NOME ALIAS)', lista_alias)
                else:
                    mitt = st.text_input('Mittente * (crea prima Alias)')
                    dest = st.text_input('Destinatario * (crea prima Alias)')
                c1,c2,c3 = st.columns(3)
                with c1:
                    canale_b = st.text_input('Canale Radio')
                with c2:
                    priorita = st.selectbox('Priorita', ['Bassa','Normale','Alta','Urgenza'])
                with c3:
                    ora_b = st.text_input('Ora', value=datetime.now().strftime('%H:%M'))
                data_b = st.date_input('Data', value=date.today())
                msg = st.text_area('Messaggio *', height=120)
                if st.form_submit_button('Salva Brogliaccio Blindato', type='primary', use_container_width=True):
                    if mitt and dest and msg:
                        b = {'Data':str(data_b),'Ora':ora_b,'EventoBlindato':st.session_state.brog_evento_blindato if st.session_state.brog_evento_blindato else '','EmergenzaBlindata':st.session_state.brog_emergenza_blindata if st.session_state.brog_emergenza_blindata else '','Mittente':mitt,'Destinatario':dest,'Canale':canale_b,'Priorita':priorita,'Messaggio':msg}
                        st.session_state.brogliaccio.append(b)
                        st.success(f'Brogliaccio {mitt} -> {dest} salvato')
                        st.balloons()
        if st.session_state.brogliaccio:
            st.dataframe(pd.DataFrame(st.session_state.brogliaccio), use_container_width=True)
            c1,c2 = st.columns(2)
            c1.download_button('Excel Brogliaccio', to_excel(pd.DataFrame(st.session_state.brogliaccio)), file_name='brogliaccio.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', use_container_width=True)
            pdf = to_pdf(pd.DataFrame(st.session_state.brogliaccio), 'Brogliaccio')
            if pdf:
                c2.download_button('PDF Brogliaccio', pdf, file_name='brogliaccio.pdf', mime='application/pdf', use_container_width=True)

    elif cur == 'Eventi':
        hdr_form('EVENTI - PIU RIGHE')
        with st.form('eventi_form'):
            c1,c2 = st.columns(2)
            with c1:
                nome_e = st.text_input('NOME EVENTO *')
                luogo_e = st.text_input('Luogo *')
            with c2:
                tipo_e = st.selectbox('Tipo', ['Esercitazione','Emergenza','Prevenzione','Manifestazione','Formazione','Altro'])
                data_e = st.date_input('Data Evento', value=date.today())
            descr_e = st.text_area('Descrizione')
            if st.form_submit_button('Crea Evento', type='primary', use_container_width=True):
                if nome_e and luogo_e:
                    e = {'NomeEvento':nome_e,'Luogo':luogo_e,'Tipo':tipo_e,'DataEvento':str(data_e),'Descrizione':descr_e,'Data':str(date.today())}
                    st.session_state.eventi.append(e)
                    st.success(f'Evento {nome_e} creato - disponibile in Alias Radio, Brogliaccio, Check-in')
                    st.balloons()
        if st.session_state.eventi:
            st.dataframe(pd.DataFrame(st.session_state.eventi), use_container_width=True)

    elif cur == 'Emergenze':
        hdr_form('EMERGENZE - PIU RIGHE')
        with st.form('em_form'):
            c1,c2 = st.columns(2)
            with c1:
                tipo_em = st.selectbox('Tipo *', ['Alluvione','Frana','Incendio','Terremoto','Neve','Ricerca','Altro'])
                luogo_em = st.text_input('Luogo *')
            with c2:
                data_em = st.date_input('Data Emergenza', value=date.today())
                ora_em = st.time_input('Ora Allarme', value=datetime.now().time())
            descr_em = st.text_area('Descrizione *')
            note_em = st.text_area('Note')
            if st.form_submit_button('Attiva Emergenza', type='primary', use_container_width=True):
                if luogo_em and descr_em:
                    em = {'Tipo':tipo_em,'Luogo':luogo_em,'Descrizione':descr_em,'Note':note_em,'DataEmergenza':str(data_em),'Ora':str(ora_em),'Data':str(date.today())}
                    st.session_state.emergenze.append(em)
                    st.success('Emergenza attivata - disponibile per blindare Brogliaccio, Check-in, Interventi')
                    st.balloons()
        if st.session_state.emergenze:
            st.dataframe(pd.DataFrame(st.session_state.emergenze), use_container_width=True)

    elif cur == 'Check-in':
        hdr_form('CHECK-IN - BLINDATO SU EVENTO/EMERGENZA - PIU RIGHE')
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
            st.success(f"CHECK-IN BLINDATO SU: {st.session_state.check_evento_blindato or st.session_state.check_emergenza_blindata} - Resta blindato finche non sblocchi tu")
            if st.button('SBLOCCA CHECK-IN', type='primary', use_container_width=True, key='sbc'):
                st.session_state.check_blindato = False
                st.session_state.check_evento_blindato = None
                st.session_state.check_emergenza_blindata = None
                st.rerun()
        st.divider()
        if st.session_state.check_blindato:
            if not st.session_state.volontari:
                st.warning('Inserisci prima Volontario in Volontari')
            else:
                with st.form('check_form'):
                    if st.session_state.check_evento_blindato:
                        st.text_input('EVENTO BLINDATO', value=st.session_state.check_evento_blindato, disabled=True)
                    if st.session_state.check_emergenza_blindata:
                        st.text_input('EMERGENZA BLINDATA', value=st.session_state.check_emergenza_blindata, disabled=True)
                    c1,c2 = st.columns(2)
                    with c1:
                        vol_sel = st.selectbox('Volontario *', [f"{v.get('Nome','')} {v.get('Cognome','')}" for v in st.session_state.volontari])
                        ora_check = st.text_input('Ora', value=datetime.now().strftime('%H:%M'))
                    with c2:
                        if st.session_state.postazioni:
                            lista_post = ['Base','Avanzata'] + [p.get('Nome','') for p in st.session_state.postazioni]
                            post_sel = st.selectbox('Postazione *', lista_post)
                        else:
                            post_sel = st.selectbox('Postazione *', ['Base','Avanzata'])
                        note_check = st.text_input('Note')
                    if st.form_submit_button('Registra Check-in Blindato', type='primary', use_container_width=True):
                        c = {'Data':str(date.today()),'Ora':ora_check,'EventoBlindato':st.session_state.check_evento_blindato if st.session_state.check_evento_blindato else '','EmergenzaBlindata':st.session_state.check_emergenza_blindata if st.session_state.check_emergenza_blindata else '','Volontario':vol_sel,'Postazione':post_sel,'Note':note_check}
                        st.session_state.checkin.append(c)
                        st.success(f'Check-in {vol_sel} registrato blindato')
                        st.balloons()
        if st.session_state.checkin:
            st.dataframe(pd.DataFrame(st.session_state.checkin), use_container_width=True)

    elif cur == 'Interventi Emergenza':
        hdr_form('INTERVENTI EMERGENZA - COLLEGATO A EMERGENZA BLINDATA + STATO - PIU RIGHE')
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
                        iv = {'Data':str(data_int),'Ora':str(ora_int),'EmergenzaBlindata':st.session_state.interventi_emergenza_blindata,'Comune':comune_int,'Via':via_int,'Civico':civico_int,'ODV':odv_int,'Stato':stato_int,'Priorita':priorita_int,'Azione':azione_int,'Note':note_int}
                        st.session_state.interventi.append(iv)
                        st.success(f'Intervento {stato_int} salvato collegato a Emergenza')
                        st.balloons()
        if st.session_state.interventi:
            st.divider()
            st.dataframe(pd.DataFrame(st.session_state.interventi), use_container_width=True)
            c1,c2 = st.columns(2)
            c1.download_button('Excel Interventi', to_excel(pd.DataFrame(st.session_state.interventi)), file_name='interventi.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', use_container_width=True)
            pdf = to_pdf(pd.DataFrame(st.session_state.interventi), 'Interventi')
            if pdf:
                c2.download_button('PDF Interventi', pdf, file_name='interventi.pdf', mime='application/pdf', use_container_width=True)

    elif cur == 'Mezzi':
        hdr_form('MEZZI - PIU RIGHE')
        with st.form('mezzi_form'):
            c1,c2,c3 = st.columns(3)
            with c1:
                targa = st.text_input('Targa *')
                tipo_m = st.selectbox('Tipo *', ['Fuoristrada','Furgone','Autocarro','Ambulanza','Pulmino','Altro'])
            with c2:
                modello_m = st.text_input('Modello')
                anno_m = st.text_input('Anno')
            with c3:
                stato_m = st.selectbox('Stato', ['Disponibile','In Uso','Manutenzione','Fuori Uso'])
                note_m = st.text_input('Note')
            if st.form_submit_button('Salva Mezzo', type='primary', use_container_width=True):
                if targa and tipo_m:
                    st.session_state.mezzi.append({'Targa':targa,'Tipo':tipo_m,'Modello':modello_m,'Anno':anno_m,'Stato':stato_m,'Note':note_m})
                    st.success('Mezzo salvato')
        if st.session_state.mezzi:
            st.dataframe(pd.DataFrame(st.session_state.mezzi), use_container_width=True)

    elif cur == 'Attrezzature':
        hdr_form('ATTREZZATURE - PIU RIGHE')
        with st.form('attr_form'):
            c1,c2,c3 = st.columns(3)
            with c1:
                nome_a = st.text_input('Attrezzatura *')
                cat_a = st.selectbox('Categoria', ['AIB','Idrogeologico','Logistica','Sanitario','Radio','Altro'])
            with c2:
                quant = st.number_input('Quantita *', min_value=1, value=1)
                stato_a = st.selectbox('Stato', ['Disponibile','In Uso','Manutenzione'])
            with c3:
                ubicazione = st.text_input('Ubicazione')
                note_a = st.text_input('Note')
            if st.form_submit_button('Salva Attrezzatura', type='primary', use_container_width=True):
                if nome_a:
                    st.session_state.attrezzature.append({'Attrezzatura':nome_a,'Categoria':cat_a,'Quantita':quant,'Stato':stato_a,'Ubicazione':ubicazione,'Note':note_a})
                    st.success('Attrezzatura salvata')
        if st.session_state.attrezzature:
            st.dataframe(pd.DataFrame(st.session_state.attrezzature), use_container_width=True)

    elif cur == 'Mappa Avanzata':
        hdr_form('MAPPA AVANZATA - BUON LAVORO - TUTTO IL LAVORO RIPRISTINATO - PIU RIGHE')
        st.info('OSM default, fullscreen + - ESC, click coord, icona marker, reverse geocoding')
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
                popup = f"<b>{p['Nome']}</b><br>{p.get('Comune','')}"
                p_icon = p.get('Icona','Nessuna')
                use_path = None
                if p_icon!= 'Nessuna':
                    ico = next((i for i in st.session_state.icone if i['Nome'] == p_icon), None)
                    if ico and ico.get('FileBytes'):
                        use_path = salva_icona_temp(ico['FileBytes'], p_icon)
                if use_path:
                    folium.Marker([p['Lat'], p['Log']], popup=popup, icon=folium.CustomIcon(use_path, icon_size=(40,40))).add_to(mm)
                else:
                    folium.Marker([p['Lat'], p['Log']], popup=popup, icon=folium.Icon(color='green')).add_to(mm)
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
            st.error(f"Errore mappa: {e} - pip install folium streamlit-folium requests")
        last = st.session_state.last_clicked
        if last:
            st.info(f"Click: {last['lat']:.6f} {last['lon']:.6f} Comune: {last.get('comune','')} Via: {last.get('via','')}")
        with st.form('form_post'):
            c1,c2 = st.columns(2)
            with c1:
                nome_p = st.text_input('Nome Postazione *')
                comune_p = st.text_input('Comune *', value=last.get('comune','') if last else '')
            with c2:
                lat_p = st.text_input('Lat *', value=str(last['lat']) if last else '')
                lon_p = st.text_input('Log *', value=str(last['lon']) if last else '')
            lista_icone = ['Nessuna'] + [i['Nome'] for i in st.session_state.icone] if st.session_state.icone else ['Nessuna']
            icona_p = st.selectbox('Icona', lista_icone)
            note_p = st.text_input('Note')
            if st.form_submit_button('Salva Postazione', type='primary', use_container_width=True):
                if nome_p and comune_p and lat_p and lon_p:
                    try:
                        lat_v = float(lat_p.replace(',','.'))
                        lon_v = float(lon_p.replace(',','.'))
                        st.session_state.postazioni.append({'Nome':nome_p,'Comune':comune_p,'Icona':icona_p,'Lat':lat_v,'Log':lon_v,'Note':note_p})
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

    elif cur == 'Libreria Icone':
        hdr_form('LIBRERIA ICONE - FORM PER CARICARE LE ICONE - PIU RIGHE')
        with st.form('icone_form'):
            nome_i = st.text_input('Nome icona *')
            desc_i = st.text_input('Descrizione')
            file_i = st.file_uploader('Carica PNG/JPG *', type=['png','jpg','jpeg'])
            if file_i:
                st.image(file_i, width=120, caption='Preview OK')
            if st.form_submit_button('Salva Icona', type='primary', use_container_width=True):
                if nome_i and file_i:
                    st.session_state.icone.append({'Nome':nome_i,'Descrizione':desc_i,'FileName':file_i.name,'FileBytes':file_i.getvalue(),'Data':str(date.today())})
                    st.success('Icona caricata!')
                    st.balloons()
        if st.session_state.icone:
            st.divider()
            st.markdown(f'### {len(st.session_state.icone)} icone caricate')
            cols = st.columns(4)
            for idx, ico in enumerate(st.session_state.icone):
                col = cols[idx % 4]
                with col:
                    st.write(f"**{ico['Nome']}**")
                    st.caption(ico.get('Descrizione',''))
                    if ico.get('FileBytes'):
                        st.image(ico['FileBytes'], width=80)
                    if st.button('Elimina', key=f"del_{idx}"):
                        st.session_state.icone.pop(idx)
                        st.rerun()

    elif cur == 'Backup':
        hdr_form('BACKUP - EXPORT + IMPORT PER TUTTI I DATI + BACKUP DI TUTTO - PIU RIGHE')
        datasets = {
            'Volontari': st.session_state.volontari,
            'Radio': st.session_state.radio_db,
            'AliasRadio': st.session_state.alias_radio,
            'Brogliaccio': st.session_state.brogliaccio,
            'Eventi': st.session_state.eventi,
            'Emergenze': st.session_state.emergenze,
            'Checkin': st.session_state.checkin,
            'Interventi': st.session_state.interventi,
            'Mezzi': st.session_state.mezzi,
            'Attrezzature': st.session_state.attrezzature,
            'Postazioni': st.session_state.postazioni
        }
        totale = sum([len(v) for v in datasets.values() if v])
        st.info(f'Totale record da esportare: {totale} - Form con dati: {len([k for k,v in datasets.items() if v])} su {len(datasets)}')
        c1,c2,c3 = st.columns(3)
        with c1:
            if any(datasets.values()):
                st.download_button('📥 EXPORT TOTALE EXCEL - TUTTI I FORM', to_excel_multi(datasets), file_name=f'backup_TUTTO_ANA_Varese_{date.today()}.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', use_container_width=True, type='primary')
        with c2:
            backup_json = json.dumps({k: v for k,v in datasets.items()}, default=str, indent=2)
            st.download_button('📥 BACKUP JSON COMPLETO - TUTTO', backup_json, file_name=f'backup_JSON_TUTTO_{date.today()}.json', mime='application/json', use_container_width=True)
        with c3:
            # Backup icone nomi
            if st.session_state.icone:
                df_icone = pd.DataFrame([{'Nome': i['Nome'], 'Descrizione': i.get('Descrizione','')} for i in st.session_state.icone])
                st.download_button('📥 BACKUP ICONE', to_excel(df_icone), file_name=f'icone_{date.today()}.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', use_container_width=True)
        st.divider()
        st.markdown('### 2. IMPORT TOTALE - RIPRISTINA TUTTI I DATI DEI FORM')
        st.warning('IMPORT sovrascrive - fai prima EXPORT!')
        up_tot = st.file_uploader('Carica file Backup Excel TOTALE (con tutti i fogli)', type=['xlsx'], key='up_backup_totale')
        if up_tot:
            try:
                xls = pd.ExcelFile(up_tot)
                st.write(f'Fogli trovati: {xls.sheet_names}')
                if st.button('🔄 IMPORTA TUTTO - SOVRASCRIVI DATI', type='primary', use_container_width=True):
                    for sheet in xls.sheet_names:
                        df = pd.read_excel(xls, sheet_name=sheet)
                        records = df.to_dict('records')
                        if sheet == 'Volontari':
                            st.session_state.volontari = records
                        elif sheet == 'Radio':
                            st.session_state.radio_db = records
                        elif sheet == 'AliasRadio':
                            st.session_state.alias_radio = records
                        elif sheet == 'Brogliaccio':
                            st.session_state.brogliaccio = records
                        elif sheet == 'Eventi':
                            st.session_state.eventi = records
                        elif sheet == 'Emergenze':
                            st.session_state.emergenze = records
                        elif sheet == 'Checkin':
                            st.session_state.checkin = records
                        elif sheet == 'Interventi':
                            st.session_state.interventi = records
                        elif sheet == 'Mezzi':
                            st.session_state.mezzi = records
                        elif sheet == 'Attrezzature':
                            st.session_state.attrezzature = records
                        elif sheet == 'Postazioni':
                            st.session_state.postazioni = records
                    st.success(f'Import totale completato!')
                    st.balloons()
                    st.rerun()
            except Exception as e:
                st.error(f'Errore import: {e}')

    elif cur == 'Esporta':
        hdr_form('ESPORTA / IMPORTA PER OGNI FORM - TUTTI I DATI DEI FORM')
        for key, titolo in [('volontari','Volontari'),('radio_db','Radio'),('alias_radio','Alias Radio'),('brogliaccio','Brogliaccio'),('eventi','Eventi'),('emergenze','Emergenze'),('checkin','Check-in'),('interventi','Interventi Emergenza'),('mezzi','Mezzi'),('attrezzature','Attrezzature'),('postazioni','Postazioni Mappa'),('icone','Libreria Icone')]:
            st.markdown(f'#### {titolo} - {len(st.session_state[key])} record')
            c1,c2,c3,c4 = st.columns(4)
            df = pd.DataFrame(st.session_state[key]) if st.session_state[key] else pd.DataFrame()
            with c1:
                if st.session_state[key]:
                    st.download_button(f"📥 Excel {titolo}", to_excel(pd.DataFrame(st.session_state[key])), file_name=f"{key}_{date.today()}.xlsx", mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', key=f"ex_{key}", use_container_width=True)
            with c2:
                if st.session_state[key]:
                    pdf = to_pdf(pd.DataFrame(st.session_state[key]), titolo)
                    if pdf:
                        st.download_button(f"📄 PDF {titolo}", pdf, file_name=f"{key}_{date.today()}.pdf", mime='application/pdf', key=f"pdf_{key}", use_container_width=True)
            with c3:
                up = st.file_uploader(f'📤 Import {titolo}', type=['xlsx'], key=f'up_{key}')
                if up:
                    try:
                        df_imp = pd.read_excel(up)
                        if st.button(f'Importa {len(df_imp)} in {titolo}', key=f'imp_{key}'):
                            for _, row in df_imp.iterrows():
                                st.session_state[key].append(row.to_dict())
                            st.success(f'Importati {len(df_imp)} in {titolo}')
                            st.rerun()
                    except Exception as e:
                        st.error(f'Errore: {e}')
            with c4:
                if st.session_state[key]:
                    if st.button(f'🗑️ Svuota {titolo}', key=f'clear_{key}'):
                        st.session_state[key] = []
                        st.rerun()
            st.divider()
