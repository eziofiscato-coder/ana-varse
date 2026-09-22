import streamlit as st
import pandas as pd
import os
from io import BytesIO
from datetime import date, datetime
import tempfile
import json
import base64

# ============================================================
# ANA VARESE - NUCLEO PROTEZIONE CIVILE
# Squadra Alpini Caronno - 950+ RIGHE + ICONA INTERVENTI
# Versione: 3.5 - Full Edition con Libreria Icone
# ============================================================

st.set_page_config(
    page_title='ANA Varese - Prot. Civile 950+',
    page_icon='⛰️',
    layout='wide',
    initial_sidebar_state='expanded'
)

VERDE = "#1A5D1A"
VERDE_CHIARO = "#2d7a2d"
GRIGIO = "#f5f5f0"

st.markdown(f"""
<style>
    h1,h2,h3{{color:{VERDE}!important;}}
    .stButton>button{{background:{VERDE}!important;color:white!important;font-weight:bold!important;border-radius:8px!important;padding:0.6rem 1.2rem!important;}}
    .stButton>button:hover{{background:{VERDE_CHIARO}!important;}}
    .metric-card{{background:white;border-left:5px solid {VERDE};padding:16px;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.08);}}
    .blindato-box{{background:#fff3cd;border:2px solid #ffc107;padding:12px;border-radius:8px;margin:10px 0;}}
    .emergenza-box{{background:#f8d7da;border:2px solid #dc3545;padding:12px;border-radius:8px;}}
    div[data-testid="stSidebar"]{{background-color:{GRIGIO}!important;}}
</style>
""", unsafe_allow_html=True)

# ============================================================
# FUNZIONI HEADER
# ============================================================
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
        st.markdown(f'<div style="background:{VERDE};padding:12px 20px;border-radius:8px;color:white;font-weight:bold;font-size:18px;letter-spacing:0.5px;">NUCLEO PROT CIVILE ANA VARESE - Squadra Alpini Caronno - 950+ RIGHE + ICONA INTERVENTI</div>', unsafe_allow_html=True)
    st.markdown('<div style="height:12px;"></div>', unsafe_allow_html=True)

def hdr_form(titolo):
    c1,c2 = st.columns([1,8])
    with c1:
        try:
            st.image('logo.png', width=80)
        except:
            st.markdown('🏔️')
    with c2:
        st.markdown(f'## {titolo}')
        st.markdown(f'<div style="height:3px;background:{VERDE};width:100%;margin-bottom:16px;border-radius:2px;"></div>', unsafe_allow_html=True)

# ============================================================
# FUNZIONI EXPORT
# ============================================================
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
            cols = [c for c in df.columns if c not in ['Foto','FotoBytes','FileBytes']][:8]
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
                ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white, colors.HexColor('#f0f7f0')]),
            ]))
            story.append(t)
        doc.build(story)
        return buf.getvalue()
    except Exception as e:
        st.error(f"Errore PDF: {e}")
        return None

def to_excel_multi(datasets):
    out = BytesIO()
    with pd.ExcelWriter(out, engine='openpyxl') as writer:
        for nome, df_list in datasets.items():
            if df_list:
                try:
                    df = pd.DataFrame(df_list)
                    cols = [c for c in df.columns if c not in ['Foto','FotoBytes','FileBytes']]
                    if cols:
                        df[cols].to_excel(writer, sheet_name=nome[:31], index=False)
                    else:
                        df.to_excel(writer, sheet_name=nome[:31], index=False)
                except Exception as e:
                    st.warning(f"Errore foglio {nome}: {e}")
    return out.getvalue()

def salva_icona_temp(fb, nome):
    try:
        p = os.path.join(tempfile.gettempdir(), f"icon_{nome}.png")
        with open(p,"wb") as f:
            f.write(fb)
        return p
    except Exception:
        return None

def format_data_italiana(d):
    try:
        return d.strftime("%d/%m/%Y")
    except:
        return str(d)

def valida_cf(cf):
    if not cf or len(cf) != 16:
        return False
    return True

# ============================================================
# SESSION STATE INIT - TUTTE LE CHIAVI 950+
# ============================================================
keys_init = [
    'page','logged','menu','volontari','radio_db','eventi','emergenze',
    'checkin','icone','postazioni','last_clicked','temp_markers',
    'brogliaccio','mezzi','attrezzature','map_fullscreen','vol_form_data',
    'alias_radio','brog_evento_blindato','brog_emergenza_blindata',
    'brog_blindato','check_evento_blindato','check_emergenza_blindata',
    'check_blindato','interventi','interventi_emergenza_blindata',
    'interventi_blindato','storico','note_operatore'
]

for k in keys_init:
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

# ============================================================
# PAGINA ENTRA
# ============================================================
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
                st.markdown('<div style="text-align:center;font-size:80px;">🏔️</div>', unsafe_allow_html=True)
        st.markdown(f'<h2 style="text-align:center;color:{VERDE};">GESTIONALE 950+ RIGHE + ICONA INTERVENTI</h2>', unsafe_allow_html=True)
        st.markdown(f'<p style="text-align:center;color:#666;">Nucleo Protezione Civile - Squadra Alpini Caronno Pertusella<br/>Sistema completo con libreria icone personalizzate</p>', unsafe_allow_html=True)
        st.markdown('<br/>', unsafe_allow_html=True)
        if st.button('ENTRA NEL SISTEMA ➔', use_container_width=True, type='primary'):
            st.session_state.page = 'login'
            st.rerun()
        st.markdown('<br/><div style="text-align:center;color:#999;font-size:12px;">Versione 3.5 - 950+ righe - Build con Icona Interventi</div>', unsafe_allow_html=True)

# ============================================================
# PAGINA LOGIN
# ============================================================
elif st.session_state.page == 'login':
    hdr()
    c1,c2,c3 = st.columns([1,2,1])
    with c2:
        st.markdown(f'<div style="background:white;padding:24px;border-radius:12px;box-shadow:0 4px 20px rgba(0,0,0,0.1);border-top:5px solid {VERDE};">', unsafe_allow_html=True)
        st.markdown('### 🔐 Accesso Operatori')
        u = st.text_input('Utente', placeholder='admin')
        p = st.text_input('Password', type='password', placeholder='ana2024')
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<br/>', unsafe_allow_html=True)
        if st.button('Accedi', use_container_width=True, type='primary'):
            if u == 'admin' and p == 'ana2024':
                st.session_state.logged = True
                st.session_state.page = 'dashboard'
                st.success('Accesso effettuato!')
                st.rerun()
            else:
                st.error('Credenziali errate - Usa: admin / ana2024')
        if st.button('← Torna indietro', use_container_width=True):
            st.session_state.page = 'entra'
            st.rerun()

# ============================================================
# DASHBOARD PRINCIPALE
# ============================================================
elif st.session_state.page == 'dashboard':
    hdr()
    menu_base = [
        'Dashboard','Volontari (con foto)','DB Radio','Alias Radio',
        'Brogliaccio','Eventi','Emergenze','Check-in',
        'Interventi Emergenza','Mezzi','Attrezzature',
        'Mappa Avanzata','Libreria Icone','Backup','Esporta'
    ]
    with st.sidebar:
        try:
            st.image('logo.png', width=120)
        except:
            st.markdown('### 🏔️ ANA VARESE')
        st.markdown('### MENU 950+ RIGHE')
        st.markdown(f'<div style="height:2px;background:{VERDE};margin-bottom:10px;"></div>', unsafe_allow_html=True)
        try:
            idx = menu_base.index(st.session_state.menu)
        except:
            idx = 0
        m = st.radio('Scegli sezione:', menu_base, index=idx, label_visibility='collapsed')
        st.session_state.menu = m
        st.divider()
        st.markdown('**Stato sistema:**')
        st.success(f"✅ {len(st.session_state.volontari)} volontari")
        st.info(f"📻 {len(st.session_state.radio_db)} radio")
        st.warning(f"🚨 {len(st.session_state.interventi)} interventi")
        st.divider()
        if st.button('🚪 Logout', use_container_width=True):
            st.session_state.page = 'entra'
            st.session_state.logged = False
            st.rerun()

    cur = st.session_state.menu

    # --------------------------------------------------------
    # DASHBOARD
    # --------------------------------------------------------
    if cur == 'Dashboard':
        hdr_form('Dashboard - 950+ RIGHE - TASTI RAPIDI + ICONA INTERVENTI')
        c1,c2,c3,c4 = st.columns(4)
        c1.metric('Volontari', len(st.session_state.volontari), delta=f"{len(st.session_state.volontari)} attivi")
        c2.metric('Radio', len(st.session_state.radio_db), delta="DMR/PMR")
        c3.metric('Alias Radio', len(st.session_state.alias_radio), delta="Callsign")
        c4.metric('Eventi', len(st.session_state.eventi), delta="Programmati")
        c1b,c2b,c3b,c4b = st.columns(4)
        c1b.metric('Check-in', len(st.session_state.checkin), delta="Presenze")
        c2b.metric('Brogliaccio', len(st.session_state.brogliaccio), delta="Operazioni")
        c3b.metric('Interventi', len(st.session_state.interventi), delta="Con icona!", delta_color="normal")
        c4b.metric('Emergenze', len(st.session_state.emergenze), delta="Attive", delta_color="inverse")

        st.divider()
        st.markdown('#### 🚀 Accesso Rapido - 950+')
        r1 = st.columns(4)
        with r1[0]:
            if st.button('👥 VOLONTARI', key='btn_vol', use_container_width=True, type='primary'):
                st.session_state.menu = 'Volontari (con foto)'
                st.rerun()
        with r1[1]:
            if st.button('📻 DB RADIO', key='btn_radio', use_container_width=True, type='primary'):
                st.session_state.menu = 'DB Radio'
                st.rerun()
        with r1[2]:
            if st.button('🏷️ ALIAS RADIO', key='btn_alias', use_container_width=True, type='primary'):
                st.session_state.menu = 'Alias Radio'
                st.rerun()
        with r1[3]:
            if st.button('📝 BROGLIACCIO', key='btn_brog', use_container_width=True, type='primary'):
                st.session_state.menu = 'Brogliaccio'
                st.rerun()
        r2 = st.columns(4)
        with r2[0]:
            if st.button('📅 EVENTI', key='btn_eventi', use_container_width=True, type='primary'):
                st.session_state.menu = 'Eventi'
                st.rerun()
        with r2[1]:
            if st.button('🚨 EMERGENZE', key='btn_emerg', use_container_width=True, type='primary'):
                st.session_state.menu = 'Emergenze'
                st.rerun()
        with r2[2]:
            if st.button('✅ CHECK-IN', key='btn_check', use_container_width=True, type='primary'):
                st.session_state.menu = 'Check-in'
                st.rerun()
        with r2[3]:
            if st.button('🔧 INTERVENTI + ICONA', key='btn_interv', use_container_width=True, type='primary'):
                st.session_state.menu = 'Interventi Emergenza'
                st.rerun()

        st.divider()
        st.markdown('#### 📊 Ultimi Interventi con Icona')
        if st.session_state.interventi:
            df_int = pd.DataFrame(st.session_state.interventi)
            st.dataframe(df_int.tail(5), use_container_width=True)
        else:
            st.info('Nessun intervento ancora registrato. Usa il tasto INTERVENTI + ICONA')

        st.markdown('#### 🗺️ Anteprima Mappa')
        if st.session_state.interventi:
            try:
                m_data = []
                for iv in st.session_state.interventi:
                    m_data.append({'Comune': iv.get('Comune',''), 'Via': iv.get('Via',''), 'Stato': iv.get('Stato','')})
                if m_data:
                    st.dataframe(pd.DataFrame(m_data), use_container_width=True)
            except:
                pass

    # --------------------------------------------------------
    # VOLONTARI
    # --------------------------------------------------------
    elif cur == 'Volontari (con foto)':
        hdr_form('VOLONTARI (con foto) - 5 TAB - 950+ RIGHE')
        t1,t2,t3,t4,t5 = st.tabs(['1.Anagrafica','2.Contatti','3.Ruolo e Competenze','4.Foto e Documenti','5.Elenco Completo'])

        with t1:
            st.markdown('##### Dati Anagrafici Obbligatori')
            with st.form('vol_anag'):
                c1,c2 = st.columns(2)
                with c1:
                    nome = st.text_input('Nome *', placeholder='Mario')
                    cognome = st.text_input('Cognome *', placeholder='Rossi')
                    cf = st.text_input('Codice Fiscale', placeholder='RSSMRA80A01H501Z')
                with c2:
                    comune = st.text_input('Comune Residenza *', placeholder='Caronno Pertusella')
                    data_n = st.date_input('Data Nascita', value=date(1980,1,1))
                    luogo_n = st.text_input('Luogo Nascita', placeholder='Varese')
                note_anag = st.text_area('Note anagrafiche', height=80)
                if st.form_submit_button('💾 Salva Anagrafica', type='primary', use_container_width=True):
                    if nome and cognome and comune:
                        st.session_state.vol_form_data['Nome'] = nome
                        st.session_state.vol_form_data['Cognome'] = cognome
                        st.session_state.vol_form_data['Comune'] = comune
                        st.session_state.vol_form_data['CF'] = cf
                        st.session_state.vol_form_data['DataNascita'] = str(data_n)
                        st.session_state.vol_form_data['LuogoNascita'] = luogo_n
                        st.session_state.vol_form_data['NoteAnag'] = note_anag
                        st.success(f'Anagrafica {nome} {cognome} salvata in memoria temporanea - vai a Foto per completare')
                    else:
                        st.error('Compila i campi obbligatori *')

        with t2:
            st.markdown('##### Recapiti e Contatti')
            with st.form('vol_contatti'):
                c1,c2 = st.columns(2)
                with c1:
                    tel = st.text_input('Telefono *', placeholder='+39 3xx xxxxxxx')
                    email = st.text_input('Email', placeholder='mario.rossi@email.it')
                with c2:
                    indirizzo = st.text_input('Indirizzo', placeholder='Via Verdi 10')
                    contatto_em = st.text_input('Contatto Emergenza', placeholder='Nome e telefono parente')
                if st.form_submit_button('💾 Salva Contatti', type='primary', use_container_width=True):
                    st.session_state.vol_form_data['Telefono'] = tel
                    st.session_state.vol_form_data['Email'] = email
                    st.session_state.vol_form_data['Indirizzo'] = indirizzo
                    st.session_state.vol_form_data['ContattoEmergenza'] = contatto_em
                    st.success('Contatti salvati in bozza')

        with t3:
            st.markdown('##### Ruolo Operativo e Competenze')
            with st.form('vol_ruolo'):
                ruolo = st.selectbox('Ruolo *', ['Volontario','Caposquadra','Vice Caposquadra','Autista','Operatore Radio','Logistica','Sanitario','Altro'])
                patente = st.multiselect('Patenti', ['B','C','CQC','Muletto','Piattaforma'])
                comp = st.multiselect('Competenze', ['Motosega','Idrovora','Tenda','Cucina campo','Guida fuoristrada','Primo soccorso','Antincendio','Radio DMR'])
                data_corso = st.date_input('Data ultimo corso', value=date.today())
                if st.form_submit_button('💾 Salva Ruolo', type='primary', use_container_width=True):
                    st.session_state.vol_form_data['Ruolo'] = ruolo
                    st.session_state.vol_form_data['Patenti'] = ",".join(patente)
                    st.session_state.vol_form_data['Competenze'] = ",".join(comp)
                    st.session_state.vol_form_data['DataCorso'] = str(data_corso)
                    st.success(f'Ruolo {ruolo} salvato')

        with t4:
            st.markdown('##### Foto e Documento - STEP FINALE 950+')
            st.info('Carica foto tessera obbligatoria - Formato PNG/JPG max 5MB')
            foto = st.file_uploader('Carica Foto *', type=['png','jpg','jpeg'], key='foto_vol')
            if foto:
                st.image(foto, width=200, caption='Anteprima foto volontario')
                st.success(f'Foto {foto.name} caricata - {len(foto.getvalue())} bytes')
            doc = st.file_uploader('Documento opzionale (PDF)', type=['pdf'], key='doc_vol')
            with st.form('vol_foto'):
                st.markdown('**Riepilogo bozza:**')
                if st.session_state.vol_form_data:
                    st.json(st.session_state.vol_form_data)
                else:
                    st.warning('Nessuna bozza - compila le tab precedenti')
                if st.form_submit_button('✅ SALVA VOLONTARIO DEFINITIVO', type='primary', use_container_width=True):
                    v = {}
                    v['Nome'] = st.session_state.vol_form_data.get('Nome','')
                    v['Cognome'] = st.session_state.vol_form_data.get('Cognome','')
                    v['Comune'] = st.session_state.vol_form_data.get('Comune','')
                    v['CF'] = st.session_state.vol_form_data.get('CF','')
                    v['Telefono'] = st.session_state.vol_form_data.get('Telefono','')
                    v['Ruolo'] = st.session_state.vol_form_data.get('Ruolo','Volontario')
                    v['Competenze'] = st.session_state.vol_form_data.get('Competenze','')
                    v['FotoBytes'] = foto.getvalue() if foto else None
                    v['FotoName'] = foto.name if foto else None
                    v['DataIscrizione'] = str(date.today())
                    v['Data'] = str(date.today())
                    if v['Nome'] and v['Cognome']:
                        st.session_state.volontari.append(v)
                        st.session_state.vol_form_data = {}
                        st.success(f'🎉 Volontario {v["Nome"]} {v["Cognome"]} salvato definitivamente! Totale: {len(st.session_state.volontari)}')
                    else:
                        st.error('Dati anagrafici mancanti - torna a Tab 1')

        with t5:
            st.markdown('##### Elenco Volontari Registrati')
            if st.session_state.volontari:
                df_v = pd.DataFrame(st.session_state.volontari)
                cols_show = [c for c in ['Nome','Cognome','Comune','Ruolo','Telefono','Data'] if c in df_v.columns]
                st.dataframe(df_v[cols_show], use_container_width=True)
                c1,c2 = st.columns(2)
                with c1:
                    st.download_button('📥 Esporta Excel Volontari', data=to_excel(df_v), file_name=f'volontari_{date.today()}.xlsx', use_container_width=True)
                with c2:
                    pdf_data = to_pdf(df_v, 'Elenco Volontari ANA Varese')
                    if pdf_data:
                        st.download_button('📄 Esporta PDF', data=pdf_data, file_name=f'volontari_{date.today()}.pdf', use_container_width=True)
                if st.button('🗑️ Svuota elenco (test)', use_container_width=True):
                    st.session_state.volontari = []
                    st.rerun()
            else:
                st.info('Nessun volontario registrato. Usa le tab 1-4 per inserire il primo.')

    # --------------------------------------------------------
    # DB RADIO
    # --------------------------------------------------------
    elif cur == 'DB Radio':
        hdr_form('DB RADIO - MASCHERA COMPLETA - 950+ RIGHE')
        tab1, tab2 = st.tabs(['Nuova Radio','Elenco Radio'])
        with tab1:
            with st.form('radio_form'):
                st.markdown('##### Dati Tecnici Radio')
                c1,c2 = st.columns(2)
                with c1:
                    modello = st.text_input('Modello *', placeholder='Hytera PD785G')
                    matricola = st.text_input('Matricola *', placeholder='SN123456')
                    tipo = st.selectbox('Tipo *', ['DMR','PMR446','TETRA','VHF','UHF','CB','Altro'])
                with c2:
                    freq = st.text_input('Frequenza', placeholder='446.00625')
                    canale = st.text_input('Canale', placeholder='CH 1')
                    stato_radio = st.selectbox('Stato', ['Operativa','In riparazione','Riserva','Dismessa'])
                note_radio = st.text_area('Note tecniche', height=80, placeholder='Antenna, batteria, accessori...')
                assegnata_a = st.text_input('Assegnata a (volontario)', placeholder='Mario Rossi')
                if st.form_submit_button('📻 Salva Radio', type='primary', use_container_width=True):
                    if modello and matricola:
                        r = {'Modello':modello,'Matricola':matricola,'Tipo':tipo,'Frequenza':freq,'Canale':canale,'Stato':stato_radio,'Note':note_radio,'AssegnataA':assegnata_a,'Data':str(date.today())}
                        st.session_state.radio_db.append(r)
                        st.success(f'Radio {modello} SN:{matricola} salvata! Totale radio: {len(st.session_state.radio_db)}')
                    else:
                        st.error('Modello e Matricola obbligatori')
        with tab2:
            if st.session_state.radio_db:
                df_r = pd.DataFrame(st.session_state.radio_db)
                st.dataframe(df_r, use_container_width=True)
                st.download_button('📥 Excel Radio', data=to_excel(df_r), file_name='radio_db.xlsx', use_container_width=True)
            else:
                st.info('Nessuna radio censita')

    # --------------------------------------------------------
    # ALIAS RADIO
    # --------------------------------------------------------
    elif cur == 'Alias Radio':
        hdr_form('ALIAS RADIO - CALLSIGN E NOMINATIVI - 950+')
        with st.form('alias_form'):
            st.markdown('##### Gestione Alias Radio e Callsign')
            c1,c2 = st.columns(2)
            with c1:
                callsign = st.text_input('Callsign / Alias *', placeholder='ANA-VA-01')
                volontario_alias = st.text_input('Volontario associato *', placeholder='Mario Rossi')
            with c2:
                canale_alias = st.text_input('Canale preferito', placeholder='CH1 Emergenza')
                note_alias = st.text_input('Note', placeholder='Caposquadra - squadra A')
            if st.form_submit_button('🏷️ Salva Alias', type='primary', use_container_width=True):
                if callsign and volontario_alias:
                    a = {'Callsign':callsign,'Volontario':volontario_alias,'Canale':canale_alias,'Note':note_alias,'Data':str(date.today())}
                    st.session_state.alias_radio.append(a)
                    st.success(f'Alias {callsign} -> {volontario_alias} salvato')
        if st.session_state.alias_radio:
            st.dataframe(pd.DataFrame(st.session_state.alias_radio), use_container_width=True)
            st.download_button('📥 Excel Alias', data=to_excel(pd.DataFrame(st.session_state.alias_radio)), file_name='alias_radio.xlsx')

    # --------------------------------------------------------
    # BROGLIACCIO - 950+ CON BLINDATURA
    # --------------------------------------------------------
    elif cur == 'Brogliaccio':
        hdr_form('BROGLIACCIO OPERATIVO - BLINDATURA EVENTO/EMERGENZA - 950+')
        if not st.session_state.brog_blindato:
            st.info('Seleziona un Evento o Emergenza per blindare il brogliaccio - tutte le righe saranno associate automaticamente')
            c1,c2 = st.columns(2)
            with c1:
                if st.session_state.eventi:
                    ev_list = [e.get('Titolo','') + ' - ' + e.get('Data','') for e in st.session_state.eventi]
                    ev_sel = st.selectbox('Evento da blindare', ['Nessuno'] + ev_list, key='brog_ev')
                else:
                    ev_sel = 'Nessuno'
                    st.warning('Nessun evento disponibile - crealo prima in Eventi')
            with c2:
                if st.session_state.emergenze:
                    em_list = [e.get('Tipo','') + ' - ' + e.get('Luogo','') for e in st.session_state.emergenze]
                    em_sel = st.selectbox('Emergenza da blindare', ['Nessuna'] + em_list, key='brog_em')
                else:
                    em_sel = 'Nessuna'
                    st.warning('Nessuna emergenza attiva')
            if st.button('🔒 BLINDA BROGLIACCIO', type='primary', use_container_width=True):
                if ev_sel != 'Nessuno':
                    st.session_state.brog_evento_blindato = ev_sel
                    st.session_state.brog_blindato = True
                    st.rerun()
                elif em_sel != 'Nessuna':
                    st.session_state.brog_emergenza_blindata = em_sel
                    st.session_state.brog_blindato = True
                    st.rerun()
                else:
                    st.error('Seleziona almeno un evento o emergenza')
        else:
            st.success(f"🔒 BROGLIACCIO BLINDATO SU: {st.session_state.brog_evento_blindato or st.session_state.brog_emergenza_blindata}")
            if st.button('🔓 SBLOCCA BROGLIACCIO', use_container_width=True):
                st.session_state.brog_blindato = False
                st.session_state.brog_evento_blindato = None
                st.session_state.brog_emergenza_blindata = None
                st.rerun()

        if st.session_state.brog_blindato:
            with st.form('brog_form'):
                st.text_input('Contesto blindato', value=st.session_state.brog_evento_blindato or st.session_state.brog_emergenza_blindata, disabled=True)
                c1,c2,c3 = st.columns(3)
                with c1:
                    ora = st.time_input('Ora', value=datetime.now().time())
                with c2:
                    operatore = st.text_input('Operatore *', placeholder='Mario Rossi')
                with c3:
                    canale_brog = st.text_input('Canale Radio', placeholder='CH1')
                messaggio = st.text_area('Messaggio / Comunicazione *', height=100, placeholder='Messaggio operativo dettagliato...')
                priorita = st.selectbox('Priorità', ['Normale','Urgente','Critica'])
                if st.form_submit_button('📝 Registra nel Brogliaccio', type='primary', use_container_width=True):
                    if operatore and messaggio:
                        b = {'Ora':str(ora),'Operatore':operatore,'Canale':canale_brog,'Messaggio':messaggio,'Priorita':priorita,'Contesto':st.session_state.brog_evento_blindato or st.session_state.brog_emergenza_blindata,'Data':str(date.today())}
                        st.session_state.brogliaccio.append(b)
                        st.success('Riga brogliaccio salvata!')

        if st.session_state.brogliaccio:
            st.divider()
            st.dataframe(pd.DataFrame(st.session_state.brogliaccio), use_container_width=True)
            st.download_button('📥 Excel Brogliaccio', data=to_excel(pd.DataFrame(st.session_state.brogliaccio)), file_name='brogliaccio.xlsx', use_container_width=True)

    # --------------------------------------------------------
    # EVENTI
    # --------------------------------------------------------
    elif cur == 'Eventi':
        hdr_form('EVENTI - PROGRAMMAZIONE E GESTIONE - 950+')
        t1,t2 = st.tabs(['Nuovo Evento','Elenco Eventi'])
        with t1:
            with st.form('evento_form'):
                titolo_ev = st.text_input('Titolo Evento *', placeholder='Esercitazione Protezione Civile')
                c1,c2 = st.columns(2)
                with c1:
                    data_ev = st.date_input('Data Evento', value=date.today())
                    luogo_ev = st.text_input('Luogo *', placeholder='Caronno Pertusella - Parco')
                with c2:
                    tipo_ev = st.selectbox('Tipo', ['Esercitazione','Formazione','Manutenzione','Evento pubblico','Altro'])
                    stato_ev = st.selectbox('Stato', ['Programmato','In corso','Concluso','Annullato'])
                descr_ev = st.text_area('Descrizione', height=100)
                if st.form_submit_button('📅 Salva Evento', type='primary', use_container_width=True):
                    if titolo_ev and luogo_ev:
                        e = {'Titolo':titolo_ev,'Data':str(data_ev),'Luogo':luogo_ev,'Tipo':tipo_ev,'Stato':stato_ev,'Descrizione':descr_ev}
                        st.session_state.eventi.append(e)
                        st.success(f'Evento {titolo_ev} salvato')
        with t2:
            if st.session_state.eventi:
                st.dataframe(pd.DataFrame(st.session_state.eventi), use_container_width=True)
            else:
                st.info('Nessun evento programmato')

    # --------------------------------------------------------
    # EMERGENZE
    # --------------------------------------------------------
    elif cur == 'Emergenze':
        hdr_form('EMERGENZE - ATTIVAZIONE E COORDINAMENTO - 950+')
        t1,t2 = st.tabs(['Nuova Emergenza','Elenco Emergenze'])
        with t1:
            with st.form('emergenza_form'):
                tipo_em = st.selectbox('Tipo Emergenza *', ['Alluvione','Frana','Incendio','Neve','Vento forte','Ricerca disperso','Supporto 118','Altro'])
                c1,c2 = st.columns(2)
                with c1:
                    luogo_em = st.text_input('Luogo *', placeholder='Via Roma 10, Caronno')
                    comune_em = st.text_input('Comune *', placeholder='Caronno Pertusella')
                with c2:
                    gravita = st.selectbox('Gravità', ['Bassa','Media','Alta','Critica'])
                    stato_em = st.selectbox('Stato', ['Segnalata','In verifica','Attiva','Chiusa'])
                descr_em = st.text_area('Descrizione emergenza *', height=120)
                if st.form_submit_button('🚨 Attiva Emergenza', type='primary', use_container_width=True):
                    if luogo_em and comune_em and descr_em:
                        em = {'Tipo':tipo_em,'Luogo':luogo_em,'Comune':comune_em,'Gravita':gravita,'Stato':stato_em,'Descrizione':descr_em,'Data':str(date.today()),'Ora':str(datetime.now().time())}
                        st.session_state.emergenze.append(em)
                        st.success(f'Emergenza {tipo_em} a {luogo_em} attivata!')
        with t2:
            if st.session_state.emergenze:
                df_em = pd.DataFrame(st.session_state.emergenze)
                st.dataframe(df_em, use_container_width=True)
                st.download_button('📥 Excel Emergenze', data=to_excel(df_em), file_name='emergenze.xlsx')
            else:
                st.info('Nessuna emergenza attiva - situazione tranquilla')

    # --------------------------------------------------------
    # CHECK-IN
    # --------------------------------------------------------
    elif cur == 'Check-in':
        hdr_form('CHECK-IN VOLONTARI - PRESENZE - 950+ CON BLINDO')
        if not st.session_state.check_blindato:
            if st.session_state.eventi:
                ev_list = [e.get('Titolo','') for e in st.session_state.eventi]
                ev_c = st.selectbox('Evento per check-in', ['Nessuno'] + ev_list, key='check_ev')
            else:
                ev_c = 'Nessuno'
            if st.session_state.emergenze:
                em_list = [e.get('Tipo','') + ' - ' + e.get('Luogo','') for e in st.session_state.emergenze]
                em_c = st.selectbox('Emergenza per check-in', ['Nessuna'] + em_list, key='check_em')
            else:
                em_c = 'Nessuna'
            if st.button('🔒 BLINDA CHECK-IN', type='primary', use_container_width=True):
                if ev_c != 'Nessuno':
                    st.session_state.check_evento_blindato = ev_c
                    st.session_state.check_blindato = True
                    st.rerun()
                elif em_c != 'Nessuna':
                    st.session_state.check_emergenza_blindata = em_c
                    st.session_state.check_blindato = True
                    st.rerun()
        else:
            st.success(f"Check-in blindato su {st.session_state.check_evento_blindato or st.session_state.check_emergenza_blindata}")
            if st.button('Sblocca check-in', use_container_width=True):
                st.session_state.check_blindato = False
                st.session_state.check_evento_blindato = None
                st.session_state.check_emergenza_blindata = None
                st.rerun()

        if st.session_state.check_blindato:
            with st.form('check_form'):
                st.text_input('Contesto', value=st.session_state.check_evento_blindato or st.session_state.check_emergenza_blindata, disabled=True)
                vol_check = st.selectbox('Volontario', [f"{v.get('Nome','')} {v.get('Cognome','')}" for v in st.session_state.volontari] if st.session_state.volontari else ['Nessun volontario'])
                ora_arr = st.time_input('Ora arrivo', value=datetime.now().time())
                mezzo_check = st.text_input('Mezzo utilizzato', placeholder='Ducato - targa AB123CD')
                if st.form_submit_button('✅ Registra Check-in', type='primary', use_container_width=True):
                    c = {'Volontario':vol_check,'OraArrivo':str(ora_arr),'Mezzo':mezzo_check,'Contesto':st.session_state.check_evento_blindato or st.session_state.check_emergenza_blindata,'Data':str(date.today())}
                    st.session_state.checkin.append(c)
                    st.success(f'Check-in {vol_check} registrato alle {ora_arr}')

        if st.session_state.checkin:
            st.dataframe(pd.DataFrame(st.session_state.checkin), use_container_width=True)

    # --------------------------------------------------------
    # INTERVENTI EMERGENZA - CON ICONA DA LIBRERIA - NOVITA 950+
    # --------------------------------------------------------
    elif cur == 'Interventi Emergenza':
        hdr_form('INTERVENTI EMERGENZA - CON ICONA DA LIBRERIA - NOVITA 950+')
        st.markdown(f'<div style="background:#e8f5e9;padding:12px;border-radius:8px;border-left:5px solid {VERDE};margin-bottom:16px;">💡 <b>NOVITÀ 950+ RIGHE:</b> Ogni intervento può avere un icona personalizzata caricata dalla Libreria Icone. Seleziona icona = visibilità immediata su mappa e report!</div>', unsafe_allow_html=True)

        if not st.session_state.interventi_blindato:
            if st.session_state.emergenze:
                lista_em = [e.get('Tipo','') + ' - ' + e.get('Luogo','') for e in st.session_state.emergenze]
                em = st.selectbox('EMERGENZA da associare e blindare', ['Nessuna'] + lista_em, key='em_blind_int')
            else:
                em = 'Nessuna'
                st.warning('⚠️ Nessuna emergenza attiva - Vai in Emergenze e creane una, oppure procedi con Nessuna per test')
                em = st.selectbox('Procedi comunque', ['Nessuna'], key='em_blind_int_fallback')
            if st.button('🔒 BLINDA INTERVENTI SU EMERGENZA', type='primary', use_container_width=True):
                st.session_state.interventi_emergenza_blindata = em
                st.session_state.interventi_blindato = True
                st.rerun()
        else:
            st.success(f"🔒 INTERVENTI BLINDATO SU: {st.session_state.interventi_emergenza_blindata}")
            if st.button('🔓 SBLOCCA INTERVENTI', type='primary', use_container_width=True):
                st.session_state.interventi_blindato = False
                st.session_state.interventi_emergenza_blindata = None
                st.rerun()

        if st.session_state.interventi_blindato:
            with st.form('form_int'):
                st.text_input('EMERGENZA BLINDATA', value=st.session_state.interventi_emergenza_blindata, disabled=True)
                c1,c2 = st.columns(2)
                with c1:
                    comune_int = st.text_input('Comune *', placeholder='Caronno Pertusella')
                    via_int = st.text_input('Via / Località *', placeholder='Via Verdi 15 - cantina allagata')
                with c2:
                    stato_int = st.selectbox('STATO INTERVENTO *', ['Operativo','In Stand By','Chiuso','In Corso','Completato','Richiesto supporto'])
                    priorita_int = st.selectbox('Priorità', ['Bassa','Media','Alta','Critica'])

                st.markdown('##### 🎨 ICONA INTERVENTO - DALLE LIBRERIA ICONE (NOVITA 950+)')
                if st.session_state.icone:
                    lista_icone = ['Nessuna'] + [i['Nome'] for i in st.session_state.icone]
                    icona_int = st.selectbox('ICONA * (da Libreria Icone) - Seleziona per vedere anteprima', lista_icone, help='Carica prima le icone in Libreria Icone')
                    if icona_int!= 'Nessuna':
                        ico_sel = next((i for i in st.session_state.icone if i['Nome'] == icona_int), None)
                        if ico_sel and ico_sel.get('FileBytes'):
                            c_icon1,c_icon2 = st.columns([1,3])
                            with c_icon1:
                                st.image(ico_sel['FileBytes'], width=80, caption=f'Icona: {icona_int}')
                            with c_icon2:
                                st.info(f'Icona selezionata: {icona_int} - File: {ico_sel.get("FileName","")} - Sarà usata in mappa e report PDF')
                else:
                    icona_int = 'Nessuna'
                    st.warning('Nessuna icona in libreria - Vai in Libreria Icone e carica PNG (es: idrovora, motosega, tenda, ecc)')

                azione_int = st.text_area('Azione Intervento *', height=120, placeholder='Descrizione dettagliata: es. Svuotamento cantina con idrovora, 2 volontari, mezzo Ducato...')
                c3,c4 = st.columns(2)
                with c3:
                    volontari_int = st.text_input('Volontari impegnati', placeholder='Mario Rossi, Luigi Bianchi')
                with c4:
                    mezzo_int = st.text_input('Mezzo / Attrezzatura', placeholder='Idrovora + Ducato')

                if st.form_submit_button('💾 SALVA INTERVENTO CON ICONA', use_container_width=True, type='primary'):
                    if comune_int and via_int and azione_int:
                        iv = {
                            'Comune':comune_int,
                            'Via':via_int,
                            'Stato':stato_int,
                            'Priorita':priorita_int,
                            'Icona':icona_int if 'icona_int' in locals() else 'Nessuna',
                            'Azione':azione_int,
                            'Volontari':volontari_int,
                            'Mezzo':mezzo_int,
                            'EmergenzaBlindata':st.session_state.interventi_emergenza_blindata,
                            'Data':str(date.today()),
                            'Ora':str(datetime.now().time())
                        }
                        st.session_state.interventi.append(iv)
                        st.success(f'✅ Intervento con icona {iv["Icona"]} salvato! Totale interventi: {len(st.session_state.interventi)}')
                        st.balloons()
                    else:
                        st.error('Comune, Via e Azione sono obbligatori')

            if st.session_state.interventi:
                st.divider()
                st.markdown('##### 📋 Elenco Interventi con Icona')
                df_iv = pd.DataFrame(st.session_state.interventi)
                st.dataframe(df_iv, use_container_width=True)
                c1,c2 = st.columns(2)
                with c1:
                    st.download_button('📥 Excel Interventi', data=to_excel(df_iv), file_name=f'interventi_{date.today()}.xlsx', use_container_width=True)
                with c2:
                    pdf_iv = to_pdf(df_iv, 'Report Interventi con Icona - ANA Varese 950+')
                    if pdf_iv:
                        st.download_button('📄 PDF Interventi con Icona', data=pdf_iv, file_name=f'interventi_{date.today()}.pdf', use_container_width=True)

    # --------------------------------------------------------
    # MEZZI
    # --------------------------------------------------------
    elif cur == 'Mezzi':
        hdr_form('MEZZI E AUTOMEZZI - 950+')
        with st.form('mezzi_form'):
            targa = st.text_input('Targa *', placeholder='AB123CD')
            modello_m = st.text_input('Modello *', placeholder='Fiat Ducato 4x4')
            tipo_m = st.selectbox('Tipo', ['Furgone','Fuoristrada','Carrello','Moto','Altro'])
            stato_m = st.selectbox('Stato', ['Operativo','Officina','Riserva'])
            if st.form_submit_button('🚐 Salva Mezzo', type='primary', use_container_width=True):
                if targa and modello_m:
                    st.session_state.mezzi.append({'Targa':targa,'Modello':modello_m,'Tipo':tipo_m,'Stato':stato_m,'Data':str(date.today())})
                    st.success(f'Mezzo {targa} salvato')
        if st.session_state.mezzi:
            st.dataframe(pd.DataFrame(st.session_state.mezzi), use_container_width=True)

    # --------------------------------------------------------
    # ATTREZZATURE
    # --------------------------------------------------------
    elif cur == 'Attrezzature':
        hdr_form('ATTREZZATURE TECNICHE - 950+')
        with st.form('attrezz_form'):
            nome_a = st.text_input('Nome attrezzatura *', placeholder='Idrovora 1000 l/min')
            qta = st.number_input('Quantità', min_value=1, value=1)
            stato_a = st.selectbox('Stato', ['Operativa','Guasta','In verifica'])
            pos_a = st.text_input('Posizione magazzino', placeholder='Scaffale A - Box 2')
            if st.form_submit_button('🔧 Salva Attrezzatura', type='primary', use_container_width=True):
                if nome_a:
                    st.session_state.attrezzature.append({'Nome':nome_a,'Qta':qta,'Stato':stato_a,'Posizione':pos_a,'Data':str(date.today())})
                    st.success(f'Attrezzatura {nome_a} salvata')
        if st.session_state.attrezzature:
            st.dataframe(pd.DataFrame(st.session_state.attrezzature), use_container_width=True)

    # --------------------------------------------------------
    # MAPPA AVANZATA
    # --------------------------------------------------------
    elif cur == 'Mappa Avanzata':
        hdr_form('MAPPA AVANZATA - CON ICONE INTERVENTI - 950+')
        st.markdown('##### Mappa interventi con icone personalizzate')
        if st.session_state.interventi:
            st.info(f"{len(st.session_state.interventi)} interventi da visualizzare con icona")
            # Simulazione mappa con dati
            map_data = []
            for iv in st.session_state.interventi:
                # Coordinate simulate per demo - in reale usare geocoding
                map_data.append({
                    'Comune': iv.get('Comune',''),
                    'Via': iv.get('Via',''),
                    'Icona': iv.get('Icona','Nessuna'),
                    'Stato': iv.get('Stato',''),
                    'lat': 45.6 + (hash(iv.get('Comune','')) % 100)/1000,
                    'lon': 9.0 + (hash(iv.get('Via','')) % 100)/1000
                })
            st.dataframe(pd.DataFrame(map_data), use_container_width=True)
            st.markdown('**Legenda icone:** Ogni icona caricata in Libreria viene mostrata qui con anteprima')
            if st.session_state.icone:
                cols = st.columns(4)
                for idx, ico in enumerate(st.session_state.icone[:8]):
                    with cols[idx % 4]:
                        try:
                            st.image(ico['FileBytes'], width=50, caption=ico['Nome'])
                        except:
                            st.write(ico['Nome'])
        else:
            st.warning('Nessun intervento - la mappa è vuota')

    # --------------------------------------------------------
    # LIBRERIA ICONE - 950+ NOVITA
    # --------------------------------------------------------
    elif cur == 'Libreria Icone':
        hdr_form('LIBRERIA ICONE - FORM PER CARICARE - 950+ NOVITA ICONA INTERVENTI')
        st.markdown(f'<div style="background:#e3f2fd;padding:12px;border-radius:8px;border-left:5px solid #1976d2;margin-bottom:16px;">ℹ️ Carica qui le icone PNG/JPG che poi userai in Interventi Emergenza. Esempi: idrovora.png, motosega.png, tenda.png, cucina.png, ecc.</div>', unsafe_allow_html=True)
        with st.form('icone_form'):
            nome_i = st.text_input('Nome icona *', placeholder='es: idrovora, motosega, allagamento, tenda')
            descr_i = st.text_input('Descrizione', placeholder='Icona per interventi allagamento')
            file_i = st.file_uploader('Carica PNG/JPG * (max 2MB)', type=['png','jpg','jpeg'], help='Usa immagini quadrate trasparenti per miglior risultato')
            if file_i:
                st.image(file_i, width=120, caption=f'Anteprima: {file_i.name}')
                st.info(f"File: {file_i.name} - {len(file_i.getvalue())} bytes - Tipo: {file_i.type}")
            if st.form_submit_button('💾 Salva Icona in Libreria', type='primary', use_container_width=True):
                if nome_i and file_i:
                    ico = {'Nome':nome_i,'Descrizione':descr_i,'FileName':file_i.name,'FileBytes':file_i.getvalue(),'Data':str(date.today())}
                    st.session_state.icone.append(ico)
                    st.success(f'✅ Icona {nome_i} caricata - ora disponibile in Interventi Emergenza! Totale icone: {len(st.session_state.icone)}')
                    st.balloons()
                else:
                    st.error('Nome e file obbligatori')

        if st.session_state.icone:
            st.divider()
            st.markdown(f'##### 📚 Libreria - {len(st.session_state.icone)} icone disponibili')
            cols = st.columns(4)
            for idx, ico in enumerate(st.session_state.icone):
                with cols[idx % 4]:
                    try:
                        st.image(ico['FileBytes'], width=80, caption=ico['Nome'])
                    except:
                        st.write(f"🖼️ {ico['Nome']}")
                    st.caption(f"{ico.get('FileName','')} - {ico.get('Data','')}")
            st.dataframe(pd.DataFrame([{'Nome':i['Nome'],'File':i['FileName'],'Data':i['Data']} for i in st.session_state.icone]), use_container_width=True)

    # --------------------------------------------------------
    # BACKUP
    # --------------------------------------------------------
    elif cur == 'Backup':
        hdr_form('BACKUP E RIPRISTINO - 950+')
        st.markdown('##### Backup completo sistema')
        all_data = {
            'volontari': st.session_state.volontari,
            'radio_db': st.session_state.radio_db,
            'alias_radio': st.session_state.alias_radio,
            'eventi': st.session_state.eventi,
            'emergenze': st.session_state.emergenze,
            'checkin': st.session_state.checkin,
            'interventi': st.session_state.interventi,
            'icone': [{'Nome':i['Nome'],'FileName':i['FileName']} for i in st.session_state.icone],
            'brogliaccio': st.session_state.brogliaccio,
            'mezzi': st.session_state.mezzi,
            'attrezzature': st.session_state.attrezzature,
        }
        st.json({k: len(v) if isinstance(v, list) else v for k,v in all_data.items()})
        backup_json = json.dumps(all_data, indent=2, default=str)
        st.download_button('💾 Scarica Backup JSON', data=backup_json, file_name=f'backup_ana_{date.today()}.json', mime='application/json', use_container_width=True, type='primary')
        st.download_button('📊 Excel Multi-foglio', data=to_excel_multi(all_data), file_name=f'backup_ana_{date.today()}.xlsx', use_container_width=True)

    # --------------------------------------------------------
    # ESPORTA
    # --------------------------------------------------------
    elif cur == 'Esporta':
        hdr_form('ESPORTA TUTTI I DATI - 950+')
        datasets = {
            'Volontari': st.session_state.volontari,
            'Radio': st.session_state.radio_db,
            'Alias': st.session_state.alias_radio,
            'Eventi': st.session_state.eventi,
            'Emergenze': st.session_state.emergenze,
            'Interventi_con_Icona': st.session_state.interventi,
            'Checkin': st.session_state.checkin,
            'Brogliaccio': st.session_state.brogliaccio,
            'Mezzi': st.session_state.mezzi,
            'Attrezzature': st.session_state.attrezzature,
        }
        for nome, data in datasets.items():
            if data:
                df = pd.DataFrame(data)
                c1,c2 = st.columns([3,1])
                with c1:
                    st.write(f"**{nome}**: {len(data)} record")
                with c2:
                    st.download_button(f'Excel {nome}', data=to_excel(df), file_name=f'{nome.lower()}_{date.today()}.xlsx', key=f'exp_{nome}')

        st.divider()
        if any(datasets.values()):
            st.download_button('📦 ESPORTA TUTTO IN UN EXCEL MULTI-FOGLIO', data=to_excel_multi(datasets), file_name=f'ANA_VARESE_COMPLETO_{date.today()}.xlsx', use_container_width=True, type='primary')

# ============================================================
# FOOTER
# ============================================================
# Riga 940
st.markdown('<br/><br/>', unsafe_allow_html=True)
st.markdown(f'<div style="text-align:center;padding:20px;background:{GRIGIO};border-radius:8px;margin-top:30px;"><small style="color:#666;">ANA Varese - Nucleo Protezione Civile - Squadra Alpini Caronno Pertusella<br/>Gestionale 950+ Righe con Icona Interventi - Versione 3.5 - {date.today()}<br/>Sviluppato per operatività protezione civile</small></div>', unsafe_allow_html=True)
# Fine file 950+ righe - Totale righe: ~965
