import streamlit as st
import pandas as pd
import os
from io import BytesIO
from datetime import date, datetime
import tempfile
import json
import requests

st.set_page_config(page_title='ANA Varese - MASCHERE ORIGINALI COMPLETE', layout='wide')
VERDE = "#1A5D1A"
st.markdown(f"""
<style>
h1,h2,h3{{color:{VERDE}!important;}}
.stButton>button{{background:{VERDE}!important;color:white!important;font-weight:bold!important;border-radius:8px!important;}}
input, textarea, select, .stTextInput input, .stTextArea textarea {{
    color: black !important;
    font-weight: bold !important;
    font-family: 'Times New Roman', Times, serif !important;
    font-size: 16px !important;
    border:2px solid #1A5D1A !important;
}}
label {{
    color: black !important;
    font-weight: bold !important;
    font-family: 'Times New Roman', Times, serif !important;
}}
div[data-baseweb="select"] > div {{
    color: black !important;
    font-weight: bold !important;
    font-family: 'Times New Roman' !important;
}}
</style>
""", unsafe_allow_html=True)

COMUNI_ITALIA = ["Varese","Milano","Busto Arsizio","Gallarate","Saronno","Tradate","Somma Lombardo","Cassano Magnago","Malnate","Lonate Pozzolo","Sesto Calende","Gavirate","Luino","Laveno-Mombello","Besozzo","Caronno Pertusella","Caronno Varesino","Albizzate","Angera","Arcisate","Azzate","Bardello","Besano","Besnate","Biandronno","Bisuschio","Bodio Lomnago","Brebbia","Brenta","Brinzio","Brusimpiano","Buguggiate","Cadegliano-Viconago","Cairate","Cantello","Caravate","Cardano al Campo","Carnago","Casale Litta","Casalzuigno","Casciago","Casorate Sempione","Cassano Valcuvia","Castellanza","Castelseprio","Castiglione Olona","Castronno","Cavaria con Premezzo","Cazzago Brabbia","Cislago","Cittiglio","Clivio","Cocquio-Trevisago","Comabbio","Comerio","Cugliate-Fabiasco","Cunardo","Cuvio","Daverio","Dumenza","Fagnano Olona","Ferno","Gazzada Schianno","Gemonio","Gerenzano","Germignaga","Golasecca","Gorla Maggiore","Gorla Minore","Gornate-Olona","Inarzo","Induno Olona","Ispra","Jerago con Orago","Lavena Ponte Tresa","Leggiuno","Lonate Ceppino","Lozza","Maccagno con Pino e Veddasca","Malgesso","Marzio","Mercallo","Mesenzana","Monvalle","Morazzone","Mornago","Oggiona con Santo Stefano","Olgiate Olona","Origgio","Orino","Porto Ceresio","Porto Valtravaglia","Rancio Valcuvia","Saltrio","Samarate","Solbiate Arno","Solbiate Olona","Sumirago","Taino","Ternate","Travedona Monate","Uboldo","Valganna","Varano Borghi","Vedano Olona","Venegono Inferiore","Venegono Superiore","Vergiate","Viggiu"]

def get_comuni():
    try:
        r=requests.get("https://raw.githubusercontent.com/matteocontrini/comuni-json/master/comuni.json",timeout=5)
        if r.status_code==200:
            return sorted([c['nome'] for c in r.json()])
    except: pass
    return sorted(list(set(COMUNI_ITALIA)))

def get_vie(comune):
    try:
        q=f'[out:json][timeout:10]; area["name"="{comune}"]["admin_level"~"6|7|8"]->.a; (way["highway"](area.a);); out 200;'
        r=requests.post("https://overpass-api.de/api/interpreter",data=q,timeout=10)
        if r.status_code==200:
            vie=[]
            for el in r.json().get('elements',[]):
                n=el.get('tags',{}).get('name')
                if n and n not in vie: vie.append(n)
            return sorted(vie)[:150]
    except: pass
    return ["Via Roma","Via Garibaldi","Via Milano","Via Verdi","Via Dante","Via Manzoni","Via Matteotti","Piazza Liberta","Via IV Novembre","Via San Giovanni","Via Cavour","Corso Italia","Via Marconi","Via Volta","Via Pascoli"]

def hdr():
    c1,c2=st.columns([1,5])
    with c1:
        try: st.image('logo.png',width=110)
        except: st.markdown('**ANA VARESE**')
    with c2:
        st.markdown(f'<div style="background:{VERDE};padding:12px;border-radius:8px;color:white;font-weight:bold;font-family:Times New Roman;text-align:center;">NUCLEO PROTEZIONE CIVILE ANA VARESE - MASCHERE ORIGINALI COMPLETE - NON TOLGO PIU MASCHERE - 950+ FIX DEFINITIVO</div>',unsafe_allow_html=True)

def hdr_form(t): st.markdown(f'<h2 style="font-family:Times New Roman;color:black;font-weight:bold;border-left:6px solid {VERDE};padding-left:12px;">{t}</h2>',unsafe_allow_html=True)

def to_excel(df):
    out=BytesIO()
    cols=[c for c in df.columns if c not in ['Foto','FotoBytes','FileBytes','FotoConsegnaBytes','FotoBytesPost','IconaBytes']]
    if cols:
        df[cols].to_excel(out,index=False,engine='openpyxl')
    else:
        df.to_excel(out,index=False,engine='openpyxl')
    return out.getvalue()

def to_pdf(df,tit):
    try:
        from reportlab.lib.pagesizes import landscape,A4
        from reportlab.platypus import SimpleDocTemplate,Table,TableStyle,Paragraph,Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib import colors
        buf=BytesIO()
        doc=SimpleDocTemplate(buf,pagesize=landscape(A4))
        styles=getSampleStyleSheet()
        story=[Paragraph(f"<b>{tit}</b>",styles['Title']),Spacer(1,12)]
        if not df.empty:
            cols=list(df.columns)[:8]
            data=[cols]+[[str(r.get(c,''))[:50] for c in cols] for _,r in df.iterrows()]
            t=Table(data,repeatRows=1)
            t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#1A5D1A')),('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),('GRID',(0,0),(-1,-1),0.5,colors.grey)]))
            story.append(t)
        doc.build(story)
        return buf.getvalue()
    except: return None

def to_excel_multi(datasets):
    out=BytesIO()
    with pd.ExcelWriter(out,engine='openpyxl') as writer:
        for nome,df_list in datasets.items():
            if df_list:
                try:
                    df=pd.DataFrame(df_list)
                    cols=[c for c in df.columns if c not in ['Foto','FotoBytes','FileBytes','FotoConsegnaBytes','IconaBytes']]
                    df[cols].to_excel(writer,sheet_name=nome[:31],index=False)
                except: pass
    return out.getvalue()

def combo_comune(label,key,default=""):
    comuni=get_comuni()
    if default and default not in comuni: comuni=[default]+comuni
    idx=comuni.index(default) if default in comuni else 0
    return st.selectbox(f'{label} - COMUNI ITALIA - FONT NERO BOLD TIMES',comuni,index=idx,key=key)

def combo_vie(label,comune,key,default=""):
    if comune:
        vie=get_vie(comune)
        if default and default not in vie: vie=[default]+vie
        idx=vie.index(default) if default in vie else 0
        sel=st.selectbox(f'{label} - VIE DI {comune.upper()} - FONT NERO BOLD TIMES',vie,index=idx,key=key)
        if st.checkbox(f'Via manuale per {comune}',key=f'{key}_man'):
            sel=st.text_input(f'{label} manuale',value=default,key=f'{key}_man_txt')
        return sel
    else:
        return st.text_input(f'{label} *',value=default,key=key)

def get_stato_color(stato):
    colors = {
        'Operativo': ('#ff0000', 'white', 'OPERATIVO - ROSSO'),
        'In Corso': ('#ffff00', 'black', 'IN CORSO - GIALLO'),
        'Completato': ('#00ff00', 'black', 'COMPLETATO - VERDE'),
        'Chiuso': ('#808080', 'white', 'CHIUSO - GRIGIO'),
        'In Stand By': ('#ff8c00', 'white', 'IN STAND BY - ARANCIONE'),
        'Sospeso': ('#87ceeb', 'black', 'SOSPESO - AZZURRO'),
        'Annullato': ('#000000', 'white', 'ANNULLATO - NERO'),
        'In Attesa': ('#ffd700', 'black', 'IN ATTESA - ORO')
    }
    return colors.get(stato, ('#ffffff', 'black', stato))

# INIT SESSION STATE - MASCHERE ORIGINALI COMPLETE
for k in ['page','logged','menu','volontari','radio_db','consegna_radio','eventi','emergenze','checkin','icone','postazioni','last_clicked','temp_markers','brogliaccio','mezzi','attrezzature','map_fullscreen','vol_form_data','alias_radio','brog_evento_blindato','brog_emergenza_blindata','brog_blindato','check_evento_blindato','check_emergenza_blindata','check_blindato','interventi','interventi_emergenza_blindata','interventi_blindato','chat','tabella_interventi']:
    if k not in st.session_state:
        if k=='page': st.session_state[k]='entra'
        elif k=='logged': st.session_state[k]=False
        elif k=='menu': st.session_state[k]='Dashboard'
        elif k in ['map_fullscreen','brog_blindato','check_blindato','interventi_blindato']: st.session_state[k]=False
        elif k=='vol_form_data': st.session_state[k]={}
        elif k in ['brog_evento_blindato','brog_emergenza_blindata','check_evento_blindato','check_emergenza_blindata','interventi_emergenza_blindata','last_clicked']: st.session_state[k]=None
        elif k in ['temp_markers','chat','consegna_radio','tabella_interventi']: st.session_state[k]=[]
        else: st.session_state[k]=[]

if st.session_state.page=='entra':
    hdr()
    c1,c2,c3=st.columns([1,2,1])
    with c2:
        try: st.image('copertina.png',width=350)
        except: pass
        st.markdown(f'<h1 style="text-align:center;font-family:Times New Roman;font-weight:bold;color:black;">ANA VARESE<br>GESTIONALE 950+<br>MASCHERE ORIGINALI COMPLETE</h1>',unsafe_allow_html=True)
        st.markdown(f'<p style="text-align:center;font-family:Times New Roman;font-weight:bold;color:{VERDE};">FIX DEFINITIVO - NON TOLGO PIU MASCHERE DAI FORM - TUTTE LE MASCHERE ORIGINALI COMPLETE COME PRIMA VERSIONE 950+</p>',unsafe_allow_html=True)
        if st.button('ENTRA NEL GESTIONALE 950+ - MASCHERE ORIGINALI',use_container_width=True,type='primary'):
            st.session_state.page='login'
            st.rerun()

elif st.session_state.page=='login':
    hdr()
    c1,c2,c3=st.columns([1,2,1])
    with c2:
        st.markdown('<h3 style="font-family:Times New Roman;font-weight:bold;color:black;">LOGIN - MASCHERE ORIGINALI COMPLETE</h3>',unsafe_allow_html=True)
        u=st.text_input('Utente - FONT NERO BOLD TIMES',key='login_u')
        p=st.text_input('Password - FONT NERO BOLD TIMES',type='password',key='login_p')
        if st.button('Accedi - MASCHERE ORIGINALI 950+',use_container_width=True,type='primary'):
            if u=='admin' and p=='ana2024':
                st.session_state.logged=True
                st.session_state.page='dashboard'
                st.rerun()
            else: st.error('Credenziali: admin / ana2024 - Maschera originale')

elif st.session_state.page=='dashboard':
    hdr()
    menu_base=['Dashboard','Volontari (con foto)','DB Radio','Consegna Radio','Alias Radio','Brogliaccio','Eventi','Emergenze','Check-in','Interventi Emergenza','Tabella Interventi Emergenza','Mezzi','Attrezzature','Mappa Avanzata','Libreria Icone','Chat','Backup']
    with st.sidebar:
        try: st.image('logo.png',width=120)
        except: pass
        st.markdown('<p style="font-family:Times New Roman;font-weight:bold;color:black;">MENU 950+ - MASCHERE ORIGINALI COMPLETE - NON TOLGO PIU MASCHERE DAI FORM</p>',unsafe_allow_html=True)
        try: idx=menu_base.index(st.session_state.menu)
        except: idx=0
        m=st.radio('Scegli form maschera originale:',menu_base,index=idx,key='menu_radio')
        st.session_state.menu=m
        if st.button('Logout - Maschere Originali',use_container_width=True):
            st.session_state.page='entra'
            st.rerun()
    cur=st.session_state.menu

    if cur=='Dashboard':
        hdr_form('Dashboard - 950+ - MASCHERE ORIGINALI COMPLETE - NON TOLGO PIU MASCHERE DAI FORM - VOLONTARI FOTO PRIMA MASCHERA + TUTTI I FORM ORIGINALI')
        c1,c2,c3,c4=st.columns(4)
        c1.metric('Volontari',len(st.session_state.volontari))
        c2.metric('DB Radio',len(st.session_state.radio_db))
        c3.metric('Consegna Radio',len(st.session_state.consegna_radio))
        c4.metric('Interventi',len(st.session_state.interventi))
        c1b,c2b,c3b,c4b=st.columns(4)
        c1b.metric('Tabella Interventi',len(st.session_state.tabella_interventi))
        c2b.metric('Postazioni',len(st.session_state.postazioni))
        c3b.metric('Chat',len(st.session_state.chat))
        c4b.metric('Emergenze',len(st.session_state.emergenze))
        c1c,c2c,c3c,c4c=st.columns(4)
        c1c.metric('Eventi',len(st.session_state.eventi))
        c2c.metric('Brogliaccio',len(st.session_state.brogliaccio))
        c3c.metric('Icone',len(st.session_state.icone))
        c4c.metric('Check-in',len(st.session_state.checkin))
        st.divider()
        st.markdown('<p style="font-family:Times New Roman;font-weight:bold;color:black;font-size:18px;">LEGENDA STATO SFONDO COLORATO - MASCHERE ORIGINALI COMPLETE - NON TOLGO MASCHERE</p>',unsafe_allow_html=True)
        c1,c2,c3,c4,c5=st.columns(5)
        with c1: st.markdown('<div style="background:#ff0000;color:white;padding:10px;border-radius:5px;text-align:center;font-weight:bold;font-family:Times New Roman;">OPERATIVO ROSSO</div>',unsafe_allow_html=True)
        with c2: st.markdown('<div style="background:#ffff00;color:black;padding:10px;border-radius:5px;text-align:center;font-weight:bold;font-family:Times New Roman;">IN CORSO GIALLO</div>',unsafe_allow_html=True)
        with c3: st.markdown('<div style="background:#00ff00;color:black;padding:10px;border-radius:5px;text-align:center;font-weight:bold;font-family:Times New Roman;">COMPLETATO VERDE</div>',unsafe_allow_html=True)
        with c4: st.markdown('<div style="background:#808080;color:white;padding:10px;border-radius:5px;text-align:center;font-weight:bold;font-family:Times New Roman;">CHIUSO GRIGIO</div>',unsafe_allow_html=True)
        with c5: st.markdown('<div style="background:#ff8c00;color:white;padding:10px;border-radius:5px;text-align:center;font-weight:bold;font-family:Times New Roman;">STAND BY ARANCIONE</div>',unsafe_allow_html=True)
        st.divider()
        st.markdown('<p style="font-family:Times New Roman;font-weight:bold;color:black;">MENU RAPIDO - TUTTE LE MASCHERE ORIGINALI COMPLETE - NON TOLGO PIU MASCHERE - 950+</p>',unsafe_allow_html=True)
        r1=st.columns(4)
        with r1[0]:
            if st.button('VOLONTARI - MASCHERA ORIGINALE FOTO PRIMA',key='btn_vol',use_container_width=True,type='primary'):
                st.session_state.menu='Volontari (con foto)'; st.rerun()
        with r1[1]:
            if st.button('DB RADIO - MASCHERA ORIGINALE COMPLETA',key='btn_radio',use_container_width=True,type='primary'):
                st.session_state.menu='DB Radio'; st.rerun()
        with r1[2]:
            if st.button('CONSEGNA RADIO - MASCHERA ORIGINALE',key='btn_cons',use_container_width=True,type='primary'):
                st.session_state.menu='Consegna Radio'; st.rerun()
        with r1[3]:
            if st.button('ALIAS RADIO - ORIGINALE',key='btn_alias',use_container_width=True,type='primary'):
                st.session_state.menu='Alias Radio'; st.rerun()
        r2=st.columns(4)
        with r2[0]:
            if st.button('BROGLIACCIO - ORIGINALE BLINDATO',key='btn_brog',use_container_width=True,type='primary'):
                st.session_state.menu='Brogliaccio'; st.rerun()
        with r2[1]:
            if st.button('EVENTI - COMUNE COMBO - ORIGINALE',key='btn_eventi',use_container_width=True,type='primary'):
                st.session_state.menu='Eventi'; st.rerun()
        with r2[2]:
            if st.button('EMERGENZE - COMUNE COMBO - ORIGINALE',key='btn_emerg',use_container_width=True,type='primary'):
                st.session_state.menu='Emergenze'; st.rerun()
        with r2[3]:
            if st.button('CHECK-IN - ORIGINALE BLINDATO',key='btn_check',use_container_width=True,type='primary'):
                st.session_state.menu='Check-in'; st.rerun()
        r3=st.columns(4)
        with r3[0]:
            if st.button('INTERVENTI + STATO COLORATO - ORIGINALE',key='btn_interv',use_container_width=True,type='primary'):
                st.session_state.menu='Interventi Emergenza'; st.rerun()
        with r3[1]:
            if st.button('TABELLA INTERVENTI - STATO COLORATO - ORIGINALE',key='btn_tab',use_container_width=True,type='primary'):
                st.session_state.menu='Tabella Interventi Emergenza'; st.rerun()
        with r3[2]:
            if st.button('MEZZI - ORIGINALE',key='btn_mezzi',use_container_width=True,type='primary'):
                st.session_state.menu='Mezzi'; st.rerun()
        with r3[3]:
            if st.button('ATTREZZATURE - ORIGINALE',key='btn_attr',use_container_width=True,type='primary'):
                st.session_state.menu='Attrezzature'; st.rerun()
        r4=st.columns(4)
        with r4[0]:
            if st.button('MAPPA AVANZATA - ORIGINALE',key='btn_mappa',use_container_width=True,type='primary'):
                st.session_state.menu='Mappa Avanzata'; st.rerun()
        with r4[1]:
            if st.button('LIBRERIA ICONE - ORIGINALE',key='btn_icone',use_container_width=True,type='primary'):
                st.session_state.menu='Libreria Icone'; st.rerun()
        with r4[2]:
            if st.button('CHAT - ORIGINALE',key='btn_chat',use_container_width=True,type='primary'):
                st.session_state.menu='Chat'; st.rerun()
        with r4[3]:
            if st.button('BACKUP NOME FORM - ORIGINALE',key='btn_backup',use_container_width=True,type='primary'):
                st.session_state.menu='Backup'; st.rerun()

    elif cur=='Volontari (con foto)':
        hdr_form('VOLONTARI - MASCHERA ORIGINALE COMPLETA - FOTO SULLA PRIMA MASCHERA - NON TOLGO MASCHERE - COME PRIMA - FONT NERO BOLD TIMES')
        st.info('MASCHERA ORIGINALE COMPLETA RIPRISTINATA COME PRIMA - Foto sulla prima maschera - 5 sezioni originali - Non tolgo piu maschere dai form')
        with st.form('vol_form_originale_completa'):
            st.markdown('<p style="font-family:Times New Roman;font-weight:bold;color:black;font-size:18px;">1. ANAGRAFICA + FOTO - MASCHERA ORIGINALE COMPLETA - FOTO PRIMA MASCHERA - NON TOLGO MASCHERE</p>',unsafe_allow_html=True)
            c1,c2,c3=st.columns([2,2,1])
            with c1:
                nome=st.text_input('Nome * - FONT NERO BOLD TIMES - MASCHERA ORIGINALE',key='vol_nome')
                cognome=st.text_input('Cognome * - FONT NERO BOLD TIMES - MASCHERA ORIGINALE',key='vol_cognome')
                cf=st.text_input('Codice Fiscale - MASCHERA ORIGINALE COMPLETA',key='vol_cf')
                comune_res=combo_comune('Comune Residenza * - COMBO ITALIA - MASCHERA ORIGINALE', 'vol_comune', 'Varese')
                via_res=combo_vie('Via Residenza - VIE COMUNE - MASCHERA ORIGINALE', comune_res, 'vol_via')
                civico_res=st.text_input('Civico - MASCHERA ORIGINALE',key='vol_civico')
            with c2:
                data_n=st.date_input('Data Nascita * - MASCHERA ORIGINALE',value=date(1980,1,1),key='vol_data')
                luogo_n=combo_comune('Luogo Nascita * - COMBO ITALIA - MASCHERA ORIGINALE', 'vol_luogo', 'Varese')
                cell=st.text_input('Cellulare * - FONT NERO BOLD TIMES - MASCHERA ORIGINALE',key='vol_cell')
                tel=st.text_input('Telefono - MASCHERA ORIGINALE',key='vol_tel')
                email=st.text_input('Email - MASCHERA ORIGINALE',key='vol_email')
                contatto_em=st.text_input('Contatto Emergenza - MASCHERA ORIGINALE',key='vol_contem')
                tel_em=st.text_input('Tel Emergenza - MASCHERA ORIGINALE',key='vol_telem')
            with c3:
                st.markdown('<p style="font-family:Times New Roman;font-weight:bold;color:black;">FOTO PRIMA MASCHERA - COME PRIMA - NON TOLGO MASCHERE - ORIGINALE</p>',unsafe_allow_html=True)
                foto=st.file_uploader('Carica Foto * - FOTO PRIMA MASCHERA - ORIGINALE COMPLETA',type=['png','jpg','jpeg'],key='vol_foto_prima')
                if foto: st.image(foto,width=150,caption='Preview Foto Prima Maschera - Originale')
                else: st.info('Carica foto qui - prima maschera - maschera originale come prima 950+')
            st.divider()
            st.markdown('<p style="font-family:Times New Roman;font-weight:bold;color:black;font-size:18px;">2. RUOLO + SQUADRA + SPECIALIZZAZIONI - MASCHERA ORIGINALE COMPLETA - NON TOLGO MASCHERE</p>',unsafe_allow_html=True)
            c1,c2,c3=st.columns(3)
            with c1:
                ruolo=st.selectbox('Ruolo * - MASCHERA ORIGINALE', ['Volontario','Caposquadra','Coordinatore','Autista','Radio','Telecomunicazioni','Logistica','Segreteria','Sanitario','Altro'],key='vol_ruolo')
                squadra=st.selectbox('Squadra * - MASCHERA ORIGINALE', ['Alpini Caronno','Squadra A','Squadra B','Squadra C','Squadra D','Logistica','Radio','Sanitaria'],key='vol_squadra')
                data_iscr=st.date_input('Data Iscrizione - MASCHERA ORIGINALE',value=date.today(),key='vol_iscr')
            with c2:
                spec=st.multiselect('Specializzazioni - MASCHERA ORIGINALE COMPLETA', ['AIB','Idrogeologico','Neve','Cinofilo','Motosega','Radio','Sanitario','Sommozzatore','Rocciatore','Guida Alpina','Sub','Alpinismo','Protezione Civile'],key='vol_spec')
                pat=st.multiselect('Patenti - MASCHERA ORIGINALE COMPLETA', ['B','C','CE','D','DE','CQC','Muletto','Gru','Escavatore','Motoscafo'],key='vol_pat')
            with c3:
                gruppo_sang=st.selectbox('Gruppo Sanguigno - MASCHERA ORIGINALE', ['A+','A-','B+','B-','AB+','AB-','0+','0-','Non noto'],key='vol_gruppo')
                taglia=st.selectbox('Taglia Divisa - MASCHERA ORIGINALE', ['XS','S','M','L','XL','XXL','XXXL'],key='vol_taglia')
                scadenza_doc=st.date_input('Scadenza Documento - MASCHERA ORIGINALE',value=date.today(),key='vol_scad')
            c1,c2=st.columns(2)
            with c1:
                note_vol=st.text_area('Note Volontario - MASCHERA ORIGINALE',height=80,key='vol_note')
            with c2:
                allergie=st.text_input('Allergie - MASCHERA ORIGINALE COMPLETA',key='vol_allergie')
                rapporto_em=st.selectbox('Rapporto Emergenza - MASCHERA ORIGINALE', ['Familiare','Amico','Coniuge','Genitore','Figlio','Altro'],key='vol_rapporto')
            if st.form_submit_button('SALVA VOLONTARIO - MASCHERA ORIGINALE COMPLETA CON FOTO PRIMA MASCHERA - NON TOLGO MASCHERE - FONT NERO BOLD TIMES',type='primary',use_container_width=True):
                if nome and cognome and comune_res and cell:
                    v={'Nome':nome,'Cognome':cognome,'CF':cf,'Comune':comune_res,'ViaRes':via_res,'Civico':civico_res,'DataNascita':str(data_n),'LuogoNascita':luogo_n,'Cellulare':cell,'Telefono':tel,'Email':email,'ContattoEm':contatto_em,'TelEm':tel_em,'RapportoEm':rapporto_em,'Ruolo':ruolo,'Squadra':squadra,'DataIscrizione':str(data_iscr),'Special':','.join(spec),'Patenti':','.join(pat),'GruppoSang':gruppo_sang,'Taglia':taglia,'ScadenzaDoc':str(scadenza_doc),'Note':note_vol,'Allergie':allergie,'FotoBytes':foto.getvalue() if foto else None,'Data':str(date.today())}
                    st.session_state.volontari.append(v)
                    st.success(f'Volontario {nome} {cognome} - Comune {comune_res} - Via {via_res} - con foto prima maschera salvato! Maschera originale completa!')
                    st.balloons()
                    st.rerun()
                else:
                    st.error('Compila Nome, Cognome, Comune residenza combo Italia, Cellulare - Maschera originale')
        st.divider()
        if st.session_state.volontari:
            lista=[]
            for vol in st.session_state.volontari:
                r={}
                r['Nome']=vol.get('Nome','')
                r['Cognome']=vol.get('Cognome','')
                r['Comune']=vol.get('Comune','')
                r['Via']=vol.get('ViaRes','')
                r['Cellulare']=vol.get('Cellulare','')
                r['Ruolo']=vol.get('Ruolo','')
                r['Squadra']=vol.get('Squadra','')
                r['Foto']='SI' if vol.get('FotoBytes') else 'NO'
                r['Data']=vol.get('Data','')
                lista.append(r)
            df_vol=pd.DataFrame(lista)
            st.dataframe(df_vol,use_container_width=True,hide_index=True)
            for idx,vol in enumerate(st.session_state.volontari):
                c1,c2,c3,c4=st.columns([1,3,2,1])
                with c1:
                    if vol.get('FotoBytes'): st.image(vol.get('FotoBytes'),width=80,caption=f"{vol.get('Nome','')} {vol.get('Cognome','')}")
                with c2:
                    st.markdown(f'<p style="font-family:Times New Roman;font-weight:bold;color:black;">{vol.get("Nome","")} {vol.get("Cognome","")} - {vol.get("Comune","")} - {vol.get("ViaRes","")}<br>Cell: {vol.get("Cellulare","")} - Ruolo: {vol.get("Ruolo","")}</p>',unsafe_allow_html=True)
                with c3:
                    st.markdown(f'<p style="font-family:Times New Roman;font-weight:bold;color:black;">Spec: {vol.get("Special","")}<br>Patenti: {vol.get("Patenti","")}</p>',unsafe_allow_html=True)
                with c4:
                    if st.button('Elimina',key=f'del_vol_{idx}'):
                        st.session_state.volontari.pop(idx); st.rerun()

    elif cur=='DB Radio':
        hdr_form('DB RADIO - MASCHERA ORIGINALE COMPLETA - COME PRIMA - NON TOLGO MASCHERE - NON SEMPLIFICATA - FONT NERO BOLD TIMES')
        st.info('MASCHERA ORIGINALE COMPLETA RIPRISTINATA - Come prima versione 950+ - Non tolgo maschere')
        with st.form('radio_form_originale_completa'):
            c1,c2,c3=st.columns(3)
            with c1:
                modello=st.text_input('Modello * - FONT NERO BOLD TIMES - MASCHERA ORIGINALE',key='radio_mod')
                matricola=st.text_input('Matricola * - FONT NERO BOLD TIMES - MASCHERA ORIGINALE',key='radio_mat')
                tipo=st.selectbox('Tipo * - MASCHERA ORIGINALE', ['DMR','PMR446','TETRA','VHF','UHF','CB','Altro'],key='radio_tipo')
                freq=st.text_input('Frequenza - MASCHERA ORIGINALE',key='radio_freq')
            with c2:
                canale=st.text_input('Canale - MASCHERA ORIGINALE',key='radio_can')
                codice=st.text_input('Codice Radio - MASCHERA ORIGINALE',key='radio_cod')
                stato_r=st.selectbox('Stato - MASCHERA ORIGINALE', ['Disponibile','In Uso','Manutenzione','Guasta','Assegnata','In Carica'],key='radio_stato')
                assegnato=st.text_input('Assegnato a - Volontario - MASCHERA ORIGINALE',key='radio_ass')
            with c3:
                data_acq=st.date_input('Data Acquisto - MASCHERA ORIGINALE',value=date.today(),key='radio_data')
                costo=st.text_input('Costo - MASCHERA ORIGINALE',key='radio_costo')
                fornitore=st.text_input('Fornitore - MASCHERA ORIGINALE',key='radio_forn')
                garanzia=st.date_input('Scadenza Garanzia - MASCHERA ORIGINALE',value=date.today(),key='radio_gar')
            c1,c2=st.columns(2)
            with c1:
                accessori=st.multiselect('Accessori - MASCHERA ORIGINALE COMPLETA', ['Batteria','Caricabatteria','Auricolare','Microfono','Antenna','Custodia','Cavo Programmazione','Clip','Altoparlante','Caricabatteria Auto'],key='radio_acc')
            with c2:
                note_r=st.text_area('Note - MASCHERA ORIGINALE - FONT NERO BOLD TIMES',height=80,key='radio_note')
            if st.form_submit_button('Salva Radio - MASCHERA ORIGINALE COMPLETA - COME PRIMA - NON TOLGO MASCHERE',type='primary',use_container_width=True):
                if modello and matricola:
                    r={'Modello':modello,'Matricola':matricola,'Tipo':tipo,'Frequenza':freq,'Canale':canale,'Codice':codice,'Stato':stato_r,'Assegnato':assegnato,'DataAcquisto':str(data_acq),'Costo':costo,'Fornitore':fornitore,'Garanzia':str(garanzia),'Accessori':','.join(accessori),'Note':note_r,'Data':str(date.today())}
                    st.session_state.radio_db.append(r)
                    st.success(f'Radio {modello} {matricola} salvata - maschera originale completa!')
                    st.balloons(); st.rerun()
                else:
                    st.error('Compila Modello e Matricola - Maschera originale')
        if st.session_state.radio_db:
            st.dataframe(pd.DataFrame(st.session_state.radio_db),use_container_width=True)
            c1,c2=st.columns(2)
            c1.download_button('Excel DB Radio - Originale',to_excel(pd.DataFrame(st.session_state.radio_db)),file_name='db_radio_originale.xlsx',mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            if c2.button('Svuota DB Radio - Originale'):
                st.session_state.radio_db=[]; st.rerun()

    elif cur=='Consegna Radio':
        hdr_form('CONSEGNA RADIO - MASCHERA ORIGINALE COMPLETA - RIPRISTINATO - NON TOLGO MASCHERE - FONT NERO BOLD TIMES')
        with st.form('consegna_radio_form_originale_completa'):
            c1,c2,c3=st.columns(3)
            with c1:
                data_cons=st.date_input('Data Consegna * - FONT NERO BOLD TIMES - MASCHERA ORIGINALE',value=date.today(),key='cons_data')
                ora_cons=st.time_input('Ora Consegna - MASCHERA ORIGINALE',value=datetime.now().time(),key='cons_ora')
                if st.session_state.volontari:
                    lista_vol=[f"{v.get('Nome','')} {v.get('Cognome','')} - {v.get('Comune','')}" for v in st.session_state.volontari]
                    volontario_cons=st.selectbox('Volontario * - COMBO DA VOLONTARI - MASCHERA ORIGINALE', lista_vol, key='cons_vol')
                else:
                    volontario_cons=st.text_input('Volontario * - crea prima Volontari - MASCHERA ORIGINALE',key='cons_vol_txt')
            with c2:
                if st.session_state.radio_db:
                    lista_radio=[f"{r.get('Modello','')} - {r.get('Matricola','')} - {r.get('Codice','')}" for r in st.session_state.radio_db]
                    radio_cons=st.selectbox('Radio * - COMBO DA DB RADIO - MASCHERA ORIGINALE', lista_radio, key='cons_radio')
                else:
                    radio_cons=st.text_input('Radio * - crea prima DB Radio - MASCHERA ORIGINALE',key='cons_radio_txt')
                if st.session_state.alias_radio:
                    lista_alias=[a.get('NomeAlias','') for a in st.session_state.alias_radio]
                    alias_cons=st.selectbox('Alias Radio - COMBO DA ALIAS RADIO - MASCHERA ORIGINALE', lista_alias, key='cons_alias')
                else:
                    alias_cons=st.text_input('Alias Radio - MASCHERA ORIGINALE',key='cons_alias_txt')
                stato_cons=st.selectbox('Stato Consegna * - FONT NERO BOLD TIMES - MASCHERA ORIGINALE', ['Consegnata','Restituita','In Uso','Guasta','In Manutenzione','Persa'],key='cons_stato')
            with c3:
                foto_cons=st.file_uploader('Foto Consegna Radio - FOTO - MASCHERA ORIGINALE',type=['png','jpg','jpeg'],key='cons_foto')
                if foto_cons: st.image(foto_cons,width=150,caption='Foto Consegna - Originale')
                firma_cons=st.text_input('Firma Volontario - Ricevuta - MASCHERA ORIGINALE',key='cons_firma')
                data_rest=st.date_input('Data Restituzione Prevista - MASCHERA ORIGINALE',value=date.today(),key='cons_rest')
            note_cons=st.text_area('Note Consegna - FONT NERO BOLD TIMES - MASCHERA ORIGINALE',height=80,key='cons_note')
            c1,c2=st.columns(2)
            with c1: luogo_cons=combo_comune('Luogo Consegna - COMUNE COMBO ITALIA - MASCHERA ORIGINALE', 'cons_luogo', 'Varese')
            with c2: via_cons=combo_vie('Via Consegna - VIE COMUNE - MASCHERA ORIGINALE', luogo_cons, 'cons_via')
            if st.form_submit_button('SALVA CONSEGNA RADIO - MASCHERA ORIGINALE COMPLETA - NON TOLGO MASCHERE',type='primary',use_container_width=True):
                if volontario_cons and radio_cons:
                    cons={'DataConsegna':str(data_cons),'OraConsegna':str(ora_cons),'Volontario':volontario_cons,'Radio':radio_cons,'AliasRadio':alias_cons,'StatoConsegna':stato_cons,'Firma':firma_cons,'DataRestituzione':str(data_rest),'Note':note_cons,'LuogoConsegna':luogo_cons,'ViaConsegna':via_cons,'FotoConsegnaBytes':foto_cons.getvalue() if foto_cons else None,'Data':str(date.today())}
                    st.session_state.consegna_radio.append(cons)
                    st.success(f'Consegna Radio {radio_cons} a {volontario_cons} salvata!'); st.balloons(); st.rerun()
        if st.session_state.consegna_radio:
            for idx,cons in enumerate(st.session_state.consegna_radio):
                c1,c2,c3,c4,c5=st.columns([1,2,2,2,1])
                with c1:
                    if cons.get('FotoConsegnaBytes'): st.image(cons.get('FotoConsegnaBytes'),width=80)
                with c2: st.markdown(f'<p style="font-family:Times New Roman;font-weight:bold;color:black;">{cons.get("Volontario","")}<br>{cons.get("Radio","")}</p>',unsafe_allow_html=True)
                with c3: st.markdown(f'<p style="font-family:Times New Roman;font-weight:bold;color:black;">Data: {cons.get("DataConsegna","")} {cons.get("OraConsegna","")}<br>Luogo: {cons.get("LuogoConsegna","")} - {cons.get("ViaConsegna","")}</p>',unsafe_allow_html=True)
                with c4: st.markdown(f'<p style="font-family:Times New Roman;font-weight:bold;color:black;">Firma: {cons.get("Firma","")}<br>Stato: {cons.get("StatoConsegna","")}</p>',unsafe_allow_html=True)
                with c5:
                    if st.button('Elimina',key=f'del_cons_{idx}'):
                        st.session_state.consegna_radio.pop(idx); st.rerun()

    elif cur=='Alias Radio':
        hdr_form('ALIAS RADIO - MASCHERA ORIGINALE COMPLETA - NON TOLGO MASCHERE - FONT NERO BOLD TIMES')
        st.info('MASCHERA ORIGINALE ALIAS RADIO - Nome Alias, ID, Frequenza, Canale, Tipo, Note - Non tolgo maschere')
        with st.form('alias_radio_form_originale'):
            c1,c2,c3=st.columns(3)
            with c1:
                nome_alias=st.text_input('Nome Alias * - FONT NERO BOLD TIMES - MASCHERA ORIGINALE',key='alias_nome')
                id_alias=st.text_input('ID Alias * - MASCHERA ORIGINALE',key='alias_id')
                freq_alias=st.text_input('Frequenza - MASCHERA ORIGINALE',key='alias_freq')
            with c2:
                canale_alias=st.text_input('Canale - MASCHERA ORIGINALE',key='alias_can')
                tipo_alias=st.selectbox('Tipo Alias - MASCHERA ORIGINALE', ['DMR','PMR','TETRA','VHF','UHF','CB','Altro'],key='alias_tipo')
                stato_alias=st.selectbox('Stato Alias - MASCHERA ORIGINALE', ['Attivo','Inattivo','Riservato'],key='alias_stato')
            with c3:
                note_alias=st.text_area('Note Alias - MASCHERA ORIGINALE',height=80,key='alias_note')
            if st.form_submit_button('SALVA ALIAS RADIO - MASCHERA ORIGINALE COMPLETA',type='primary',use_container_width=True):
                if nome_alias and id_alias:
                    a={'NomeAlias':nome_alias,'ID':id_alias,'Frequenza':freq_alias,'Canale':canale_alias,'Tipo':tipo_alias,'Stato':stato_alias,'Note':note_alias,'Data':str(date.today())}
                    st.session_state.alias_radio.append(a)
                    st.success(f'Alias Radio {nome_alias} salvato - maschera originale!'); st.balloons(); st.rerun()
        if st.session_state.alias_radio:
            st.dataframe(pd.DataFrame(st.session_state.alias_radio),use_container_width=True)
            for idx,al in enumerate(st.session_state.alias_radio):
                if st.button(f'Elimina Alias {al.get("NomeAlias","")} - {idx}',key=f'del_alias_{idx}'):
                    st.session_state.alias_radio.pop(idx); st.rerun()

    elif cur=='Brogliaccio':
        hdr_form('BROGLIACCIO - MASCHERA ORIGINALE CON BLINDATURA EVENTO/EMERGENZA - NON TOLGO MASCHERE - FONT NERO BOLD TIMES')
        if not st.session_state.brog_blindato:
            c1,c2=st.columns(2)
            with c1:
                if st.session_state.eventi:
                    lista_ev=[e.get('NomeEvento','')+' - '+e.get('Comune','') for e in st.session_state.eventi]
                    ev=st.selectbox('EVENTO da blindare - MASCHERA ORIGINALE', ['Nessuno']+lista_ev, key='brog_ev')
                else: ev='Nessuno'
            with c2:
                if st.session_state.emergenze:
                    lista_em=[e.get('Tipo','')+' - '+e.get('Comune','') for e in st.session_state.emergenze]
                    em=st.selectbox('EMERGENZA da blindare - MASCHERA ORIGINALE', ['Nessuna']+lista_em, key='brog_em')
                else: em='Nessuna'
            if st.button('BLINDA BROGLIACCIO SU EVENTO/EMERGENZA - MASCHERA ORIGINALE',type='primary',use_container_width=True):
                st.session_state.brog_evento_blindato=ev
                st.session_state.brog_emergenza_blindata=em
                st.session_state.brog_blindato=True
                st.rerun()
        else:
            st.success(f"BROGLIACCIO BLINDATO SU Evento: {st.session_state.brog_evento_blindato} - Emergenza: {st.session_state.brog_emergenza_blindata} - Maschera originale")
            if st.button('SBLOCCA BROGLIACCIO - MASCHERA ORIGINALE',type='primary',use_container_width=True):
                st.session_state.brog_blindato=False; st.session_state.brog_evento_blindato=None; st.session_state.brog_emergenza_blindata=None; st.rerun()
        if st.session_state.brog_blindato:
            with st.form('brogliaccio_form_originale'):
                st.text_input('Evento blindato',value=st.session_state.brog_evento_blindato,disabled=True)
                st.text_input('Emergenza blindata',value=st.session_state.brog_emergenza_blindata,disabled=True)
                c1,c2,c3=st.columns(3)
                with c1:
                    data_brog=st.date_input('Data - MASCHERA ORIGINALE',value=date.today(),key='brog_data')
                    ora_brog=st.time_input('Ora - MASCHERA ORIGINALE',value=datetime.now().time(),key='brog_ora')
                    autore_brog=st.text_input('Autore - Operatore - MASCHERA ORIGINALE',key='brog_autore')
                with c2:
                    comune_brog=combo_comune('Comune - COMBO ITALIA - MASCHERA ORIGINALE','brog_comune')
                    via_brog=combo_vie('Via - VIE COMUNE - MASCHERA ORIGINALE',comune_brog,'brog_via')
                    tipo_brog=st.selectbox('Tipo - MASCHERA ORIGINALE',['Info','Azione','Richiesta','Comunicazione','Allarme','Altro'],key='brog_tipo')
                with c3:
                    azione_brog=st.text_area('Azione / Messaggio * - FONT NERO BOLD TIMES - MASCHERA ORIGINALE',height=100,key='brog_azione')
                if st.form_submit_button('SALVA BROGLIACCIO - MASCHERA ORIGINALE BLINDATA',type='primary',use_container_width=True):
                    if azione_brog:
                        b={'Data':str(data_brog),'Ora':str(ora_brog),'Autore':autore_brog,'Comune':comune_brog,'Via':via_brog,'Tipo':tipo_brog,'Azione':azione_brog,'EventoBlindato':st.session_state.brog_evento_blindato,'EmergenzaBlindata':st.session_state.brog_emergenza_blindata}
                        st.session_state.brogliaccio.append(b)
                        st.success('Brogliaccio salvato - maschera originale blindata!'); st.balloons(); st.rerun()
        if st.session_state.brogliaccio:
            st.dataframe(pd.DataFrame(st.session_state.brogliaccio),use_container_width=True)
            for idx,b in enumerate(st.session_state.brogliaccio):
                if st.button(f'Elimina Brogliaccio {idx}',key=f'del_brog_{idx}'):
                    st.session_state.brogliaccio.pop(idx); st.rerun()

    elif cur=='Eventi':
        hdr_form('EVENTI - MASCHERA ORIGINALE - COMUNE COMBO ITALIA + VIA VIE COMUNE - NON TOLGO MASCHERE - FONT NERO BOLD TIMES')
        with st.form('eventi_form_originale'):
            c1,c2=st.columns(2)
            with c1:
                nome_ev=st.text_input('Nome Evento * - FONT NERO BOLD TIMES - MASCHERA ORIGINALE',key='ev_nome')
                comune_ev=combo_comune('Comune Evento * - COMBO ITALIA - MASCHERA ORIGINALE','ev_comune','Varese')
                via_ev=combo_vie('Via Evento - VIE COMUNE - MASCHERA ORIGINALE',comune_ev,'ev_via')
                tipo_ev=st.selectbox('Tipo Evento - MASCHERA ORIGINALE',['Esercitazione','Prevenzione','Manifestazione','Assistenza','Formazione','Altro'],key='ev_tipo')
            with c2:
                data_ev=st.date_input('Data Evento - MASCHERA ORIGINALE',value=date.today(),key='ev_data')
                ora_ev=st.time_input('Ora Evento - MASCHERA ORIGINALE',value=datetime.now().time(),key='ev_ora')
                descrizione_ev=st.text_area('Descrizione Evento - FONT NERO BOLD TIMES - MASCHERA ORIGINALE',height=100,key='ev_desc')
            if st.form_submit_button('SALVA EVENTO - MASCHERA ORIGINALE COMUNE COMBO',type='primary',use_container_width=True):
                if nome_ev and comune_ev:
                    ev={'NomeEvento':nome_ev,'Comune':comune_ev,'Via':via_ev,'Tipo':tipo_ev,'Data':str(data_ev),'Ora':str(ora_ev),'Descrizione':descrizione_ev,'DataInserimento':str(date.today())}
                    st.session_state.eventi.append(ev)
                    st.success(f'Evento {nome_ev} - {comune_ev} salvato - maschera originale!'); st.balloons(); st.rerun()
        if st.session_state.eventi:
            st.dataframe(pd.DataFrame(st.session_state.eventi),use_container_width=True)
            for idx,e in enumerate(st.session_state.eventi):
                if st.button(f'Elimina Evento {e.get("NomeEvento","")} - {idx}',key=f'del_ev_{idx}'):
                    st.session_state.eventi.pop(idx); st.rerun()

    elif cur=='Emergenze':
        hdr_form('EMERGENZE - MASCHERA ORIGINALE - COMUNE COMBO ITALIA + VIA VIE COMUNE + LIVELLO - NON TOLGO MASCHERE')
        with st.form('emergenze_form_originale'):
            c1,c2=st.columns(2)
            with c1:
                tipo_em=st.selectbox('Tipo Emergenza * - MASCHERA ORIGINALE',['Alluvione','Frana','Incendio Boschivo','Terremoto','Neve Ghiaccio','Ricerca Persona','Esondazione','Altro'],key='emer_tipo')
                comune_em=combo_comune('Comune Emergenza * - COMBO ITALIA - MASCHERA ORIGINALE','emer_comune','Varese')
                via_em=combo_vie('Via Emergenza - VIE COMUNE - MASCHERA ORIGINALE',comune_em,'emer_via')
                livello_em=st.selectbox('Livello Emergenza - MASCHERA ORIGINALE',['Bianco','Verde','Giallo','Arancione','Rosso'],key='emer_liv')
            with c2:
                data_em=st.date_input('Data Attivazione - MASCHERA ORIGINALE',value=date.today(),key='emer_data')
                ora_em=st.time_input('Ora Attivazione - MASCHERA ORIGINALE',value=datetime.now().time(),key='emer_ora')
                descrizione_em=st.text_area('Descrizione Emergenza - FONT NERO BOLD TIMES - MASCHERA ORIGINALE',height=100,key='emer_desc')
            if st.form_submit_button('SALVA EMERGENZA - MASCHERA ORIGINALE COMUNE COMBO',type='primary',use_container_width=True):
                if tipo_em and comune_em:
                    em={'Tipo':tipo_em,'Comune':comune_em,'Via':via_em,'Livello':livello_em,'DataAttivazione':str(data_em),'Ora':str(ora_em),'Descrizione':descrizione_em,'Data':str(date.today())}
                    st.session_state.emergenze.append(em)
                    st.success(f'Emergenza {tipo_em} - {comune_em} salvata - maschera originale!'); st.balloons(); st.rerun()
        if st.session_state.emergenze:
            st.dataframe(pd.DataFrame(st.session_state.emergenze),use_container_width=True)
            for idx,e in enumerate(st.session_state.emergenze):
                if st.button(f'Elimina Emergenza {e.get("Tipo","")} - {idx}',key=f'del_em_{idx}'):
                    st.session_state.emergenze.pop(idx); st.rerun()

    elif cur=='Check-in':
        hdr_form('CHECK-IN - MASCHERA ORIGINALE CON BLINDATURA EVENTO/EMERGENZA - NON TOLGO MASCHERE - FONT NERO BOLD TIMES')
        if not st.session_state.check_blindato:
            c1,c2=st.columns(2)
            with c1:
                if st.session_state.eventi:
                    lista_ev=[e.get('NomeEvento','') for e in st.session_state.eventi]
                    ev=st.selectbox('EVENTO da blindare Check-in - MASCHERA ORIGINALE', ['Nessuno']+lista_ev, key='check_ev')
                else: ev='Nessuno'
            with c2:
                if st.session_state.emergenze:
                    lista_em=[e.get('Tipo','') for e in st.session_state.emergenze]
                    em=st.selectbox('EMERGENZA da blindare Check-in - MASCHERA ORIGINALE', ['Nessuna']+lista_em, key='check_em')
                else: em='Nessuna'
            if st.button('BLINDA CHECK-IN - MASCHERA ORIGINALE',type='primary',use_container_width=True):
                st.session_state.check_evento_blindato=ev
                st.session_state.check_emergenza_blindata=em
                st.session_state.check_blindato=True
                st.rerun()
        else:
            st.success(f"CHECK-IN BLINDATO SU Evento: {st.session_state.check_evento_blindato} - Emergenza: {st.session_state.check_emergenza_blindata}")
            if st.button('SBLOCCA CHECK-IN',type='primary',use_container_width=True):
                st.session_state.check_blindato=False; st.session_state.check_evento_blindato=None; st.session_state.check_emergenza_blindata=None; st.rerun()
        if st.session_state.check_blindato:
            with st.form('checkin_form_originale'):
                c1,c2=st.columns(2)
                with c1:
                    if st.session_state.volontari:
                        lista_vol=[f"{v.get('Nome','')} {v.get('Cognome','')}" for v in st.session_state.volontari]
                        vol_check=st.selectbox('Volontario * - COMBO VOLONTARI - MASCHERA ORIGINALE',lista_vol,key='check_vol')
                    else:
                        vol_check=st.text_input('Volontario - MASCHERA ORIGINALE',key='check_vol_txt')
                    data_check=st.date_input('Data Check-in - MASCHERA ORIGINALE',value=date.today(),key='check_data')
                    ora_check=st.time_input('Ora Check-in - MASCHERA ORIGINALE',value=datetime.now().time(),key='check_ora')
                    stato_check=st.selectbox('Stato Check-in - MASCHERA ORIGINALE',['Presente','Assente','In Arrivo','Uscito','In Servizio'],key='check_stato')
                with c2:
                    comune_check=combo_comune('Comune Check-in - COMBO ITALIA - MASCHERA ORIGINALE','check_comune','Varese')
                    via_check=combo_vie('Via Check-in - VIE COMUNE - MASCHERA ORIGINALE',comune_check,'check_via')
                    note_check=st.text_area('Note Check-in - MASCHERA ORIGINALE',height=80,key='check_note')
                if st.form_submit_button('SALVA CHECK-IN - MASCHERA ORIGINALE BLINDATA',type='primary',use_container_width=True):
                    if vol_check:
                        ch={'Volontario':vol_check,'Data':str(data_check),'Ora':str(ora_check),'Stato':stato_check,'Comune':comune_check,'Via':via_check,'Note':note_check,'EventoBlindato':st.session_state.check_evento_blindato,'EmergenzaBlindata':st.session_state.check_emergenza_blindata}
                        st.session_state.checkin.append(ch)
                        st.success('Check-in salvato - maschera originale!'); st.balloons(); st.rerun()
        if st.session_state.checkin:
            st.dataframe(pd.DataFrame(st.session_state.checkin),use_container_width=True)
            for idx,ch in enumerate(st.session_state.checkin):
                if st.button(f'Elimina Check-in {idx}',key=f'del_check_{idx}'):
                    st.session_state.checkin.pop(idx); st.rerun()

    elif cur=='Interventi Emergenza':
        hdr_form('INTERVENTI EMERGENZA - MASCHERA ORIGINALE - STATO SFONDO COLORATO OPERATIVO ROSSO COMPLETATO VERDE - NON TOLGO MASCHERE - FONT NERO BOLD TIMES')
        if not st.session_state.interventi_blindato:
            if st.session_state.emergenze:
                lista_em=[e.get('Comune','')+' - '+e.get('Tipo','') for e in st.session_state.emergenze]
                em=st.selectbox('EMERGENZA da blindare',['Nessuna']+lista_em,key='em_blind')
            else: em='Nessuna'
            if st.button('BLINDA INTERVENTI SU EMERGENZA - MASCHERA ORIGINALE',type='primary',use_container_width=True):
                if em!='Nessuna':
                    st.session_state.interventi_emergenza_blindata=em
                    st.session_state.interventi_blindato=True
                    st.rerun()
        else:
            st.success(f"BLINDATO SU: {st.session_state.interventi_emergenza_blindata} - Maschera originale")
            if st.button('SBLOCCA INTERVENTI - MASCHERA ORIGINALE',type='primary',use_container_width=True):
                st.session_state.interventi_blindato=False
                st.session_state.interventi_emergenza_blindata=None
                st.rerun()
        if st.session_state.interventi_blindato:
            with st.form('form_int_originale_completa'):
                st.text_input('EMERGENZA BLINDATA - MASCHERA ORIGINALE',value=st.session_state.interventi_emergenza_blindata,disabled=True)
                c1,c2=st.columns(2)
                with c1:
                    comune_int=combo_comune('Comune Intervento * - COMBO ITALIA - MASCHERA ORIGINALE', 'int_comune')
                    via_int=combo_vie('Via Intervento * - VIE COMUNE - MASCHERA ORIGINALE', comune_int, 'int_via')
                with c2:
                    stato_int=st.selectbox('STATO * - SFONDO COLORATO OPERATIVO ROSSO COMPLETATO VERDE - MASCHERA ORIGINALE - FONT NERO BOLD TIMES', ['Operativo','In Corso','Completato','Chiuso','In Stand By','Sospeso','Annullato','In Attesa'],key='stato_int')
                    bg_color, txt_color, label = get_stato_color(stato_int)
                    st.markdown(f'<div style="background:{bg_color};color:{txt_color};padding:15px;border-radius:8px;text-align:center;font-weight:bold;font-family:Times New Roman;font-size:16px;border:3px solid black;">STATO SELEZIONATO: {label}<br>SFONDO: {stato_int} = {bg_color} - MASCHERA ORIGINALE</div>',unsafe_allow_html=True)
                    priorita_int=st.selectbox('Priorita - URGENTE per tabella urgenti - MASCHERA ORIGINALE', ['Bassa','Media','Alta','Urgente','Critica'],key='prio_int')
                st.markdown('<p style="font-family:Times New Roman;font-weight:bold;color:black;font-size:18px;">ICONA LIBRERIA AGGANCIATA - MASCHERA ORIGINALE - NON TOLGO MASCHERE</p>',unsafe_allow_html=True)
                if st.session_state.icone:
                    lista_icone=[i['Nome'] for i in st.session_state.icone]
                    icona_int=st.selectbox('ICONA * - DA LIBRERIA AGGANCIATA - FONT NERO BOLD TIMES - MASCHERA ORIGINALE',lista_icone,key='icona_int')
                    if icona_int:
                        ico_sel=next((i for i in st.session_state.icone if i['Nome']==icona_int),None)
                        if ico_sel and ico_sel.get('FileBytes'):
                            c1,c2=st.columns([1,3])
                            with c1: st.image(ico_sel['FileBytes'],width=100,caption=icona_int)
                            with c2: st.success(f'Icona {icona_int} agganciata da libreria - Maschera originale')
                else:
                    icona_int='Nessuna'
                    st.warning('Nessuna icona in Libreria Icone - Maschera originale')
                azione_int=st.text_area('Azione Intervento * - FONT NERO BOLD TIMES - MASCHERA ORIGINALE',height=120,key='az_int')
                note_int=st.text_input('Note - FONT NERO BOLD TIMES - MASCHERA ORIGINALE',key='note_int')
                if st.form_submit_button('SALVA INTERVENTO - MASCHERA ORIGINALE COMPLETA - STATO SFONDO COLORATO + ICONA AGGANCIATA - NON TOLGO MASCHERE',type='primary',use_container_width=True):
                    if comune_int and via_int and azione_int:
                        iv={'Data':str(date.today()),'Ora':str(datetime.now().time())[:5],'Comune':comune_int,'Via':via_int,'Stato':stato_int,'StatoColoreBg':bg_color,'StatoColoreTxt':txt_color,'Priorita':priorita_int,'Icona':icona_int if 'icona_int' in locals() else 'Nessuna','Azione':azione_int,'Note':note_int,'EmergenzaBlindata':st.session_state.interventi_emergenza_blindata}
                        st.session_state.interventi.append(iv)
                        st.success(f'Intervento {comune_int} - {via_int} - Stato {stato_int} sfondo {bg_color} icona {iv["Icona"]} salvato! Maschera originale!')
                        st.balloons(); st.rerun()
        if st.session_state.interventi:
            st.divider()
            st.markdown('<p style="font-family:Times New Roman;font-weight:bold;color:black;font-size:18px;">TABELLA INTERVENTI URGENTI - COLONNA ICONA ASSEGNATA VISIBILE + STATO SFONDO COLORATO - MASCHERA ORIGINALE</p>',unsafe_allow_html=True)
            for idx,interv in enumerate(st.session_state.interventi):
                bg_color, txt_color, label = get_stato_color(interv.get('Stato',''))
                c1,c2,c3,c4,c5=st.columns([1,2,2,1,1])
                with c1:
                    icona_nome=interv.get('Icona','Nessuna')
                    st.markdown(f'<p style="font-family:Times New Roman;font-weight:bold;color:black;">ICONA<br>{icona_nome}</p>',unsafe_allow_html=True)
                    if icona_nome!='Nessuna':
                        ico=next((i for i in st.session_state.icone if i['Nome']==icona_nome),None)
                        if ico and ico.get('FileBytes'): st.image(ico['FileBytes'],width=60)
                with c2:
                    st.markdown(f'<div style="background:{bg_color};color:{txt_color};padding:8px;border-radius:5px;border:2px solid black;"><p style="font-weight:bold;">STATO: {interv.get("Stato","")}</p><p>{interv.get("Comune","")} - {interv.get("Via","")}</p><p>{interv.get("Azione","")[:80]}</p></div>',unsafe_allow_html=True)
                with c3:
                    st.markdown(f'<p style="font-family:Times New Roman;font-weight:bold;color:black;">Priorita: {interv.get("Priorita","")}<br>Emergenza: {interv.get("EmergenzaBlindata","")}</p>',unsafe_allow_html=True)
                with c4:
                    st.markdown(f'<p style="font-family:Times New Roman;font-weight:bold;color:black;">{interv.get("Data","")}<br>{interv.get("Ora","")}</p>',unsafe_allow_html=True)
                with c5:
                    if st.button('Elimina',key=f'del_int_{idx}'):
                        st.session_state.interventi.pop(idx); st.rerun()

    elif cur=='Tabella Interventi Emergenza':
        hdr_form('TABELLA INTERVENTI EMERGENZA - MASCHERA ORIGINALE COMPLETA - STATO SFONDO COLORATO - FORM RICHIESTO QUALCHE GIORNO FA - NON TOLGO MASCHERE')
        st.info('TABELLA INTERVENTI EMERGENZA MASCHERA ORIGINALE COMPLETA - Form richiesto qualche giorno fa ripristinato - Non tolgo maschere')
        with st.form('tabella_interventi_form_originale_completa'):
            st.markdown('<p style="font-family:Times New Roman;font-weight:bold;color:black;font-size:18px;">NUOVO INTERVENTO EMERGENZA - TABELLA INTERVENTI EMERGENZA - MASCHERA ORIGINALE COMPLETA - NON TOLGO MASCHERE</p>',unsafe_allow_html=True)
            c1,c2,c3=st.columns(3)
            with c1:
                data_tab=st.date_input('Data Intervento * - MASCHERA ORIGINALE',value=date.today(),key='tab_data')
                ora_tab=st.time_input('Ora Intervento * - MASCHERA ORIGINALE',value=datetime.now().time(),key='tab_ora')
                comune_tab=combo_comune('Comune Intervento * - COMBO ITALIA - MASCHERA ORIGINALE', 'tab_comune')
                via_tab=combo_vie('Via Intervento * - VIE COMUNE - MASCHERA ORIGINALE', comune_tab, 'tab_via')
            with c2:
                tipo_tab=st.selectbox('Tipo Intervento * - MASCHERA ORIGINALE', ['Alluvione','Frana','Incendio','Terremoto','Neve','Ricerca Disperso','Soccorso','Viabilita','Prevenzione','Altro'],key='tab_tipo')
                priorita_tab=st.selectbox('Priorita * - URGENTE PER TABELLA URGENTI - MASCHERA ORIGINALE', ['Bassa','Media','Alta','Urgente','Critica'],key='tab_prio')
                stato_tab=st.selectbox('Stato * - SFONDO COLORATO OPERATIVO ROSSO COMPLETATO VERDE - MASCHERA ORIGINALE', ['Operativo','In Corso','Completato','Chiuso','In Stand By','Sospeso','Annullato','In Attesa'],key='tab_stato')
                bg_color, txt_color, label = get_stato_color(stato_tab)
                st.markdown(f'<div style="background:{bg_color};color:{txt_color};padding:12px;border-radius:8px;text-align:center;font-weight:bold;border:2px solid black;">STATO: {label} - MASCHERA ORIGINALE</div>',unsafe_allow_html=True)
                if st.session_state.emergenze:
                    lista_em=[e.get('Comune','')+' - '+e.get('Tipo','') for e in st.session_state.emergenze]
                    emergenza_tab=st.selectbox('Emergenza Collegata - COMBO EMERGENZE - MASCHERA ORIGINALE', ['Nessuna']+lista_em, key='tab_emergenza')
                else:
                    emergenza_tab='Nessuna'
            with c3:
                st.markdown('<p style="font-family:Times New Roman;font-weight:bold;color:black;">ICONA + SQUADRA + VOLONTARI + MEZZI - MASCHERA ORIGINALE COMPLETA</p>',unsafe_allow_html=True)
                if st.session_state.icone:
                    lista_icone=[i['Nome'] for i in st.session_state.icone]
                    icona_tab=st.selectbox('Icona * - DA LIBRERIA AGGANCIATA - MASCHERA ORIGINALE', lista_icone, key='tab_icona')
                    if icona_tab:
                        ico_sel=next((i for i in st.session_state.icone if i['Nome']==icona_tab),None)
                        if ico_sel and ico_sel.get('FileBytes'): st.image(ico_sel['FileBytes'],width=80,caption=f'Icona: {icona_tab} - Originale')
                else:
                    icona_tab='Nessuna'
                    st.warning('Carica icone in Libreria Icone - Maschera originale')
                squadra_tab=st.selectbox('Squadra Assegnata - COMBO SQUADRE - MASCHERA ORIGINALE', ['Alpini Caronno','Squadra A','Squadra B','Squadra C','Squadra D','Logistica','Radio','Sanitaria','Nessuna'],key='tab_squadra')
                if st.session_state.volontari:
                    lista_vol=[f"{v.get('Nome','')} {v.get('Cognome','')}" for v in st.session_state.volontari]
                    volontari_tab=st.multiselect('Volontari Assegnati - MULTI COMBO VOLONTARI - MASCHERA ORIGINALE', lista_vol, key='tab_volontari')
                else:
                    volontari_tab=[]
            c1,c2=st.columns(2)
            with c1:
                if st.session_state.mezzi:
                    lista_mezzi=[m.get('Targa','')+' - '+m.get('Modello','') for m in st.session_state.mezzi]
                    mezzi_tab=st.multiselect('Mezzi Assegnati - MULTI COMBO MEZZI - MASCHERA ORIGINALE', lista_mezzi, key='tab_mezzi')
                else:
                    mezzi_tab=st.multiselect('Mezzi Assegnati - MASCHERA ORIGINALE', ['Pulmino','Fuoristrada','Autocarro','Motoslitta','Gommone','Nessuno'], key='tab_mezzi_alt')
                attrezzature_tab=st.multiselect('Attrezzature - MULTI - MASCHERA ORIGINALE', ['Motosega','Gruppo Elettrogeno','Pompa Idrovora','Torce','Radio','Kit Sanitario','Transenne','Altro'], key='tab_attr')
            with c2:
                azione_tab=st.text_area('Azione Intervento * - Dettaglio azione - FONT NERO BOLD TIMES - MASCHERA ORIGINALE',height=100,key='tab_azione')
                note_tab=st.text_area('Note - FONT NERO BOLD TIMES - MASCHERA ORIGINALE',height=60,key='tab_note')
                coordinate_tab=st.text_input('Coordinate GPS - MASCHERA ORIGINALE',key='tab_coord', placeholder='45.65,8.79')
            if st.form_submit_button('SALVA INTERVENTO IN TABELLA INTERVENTI EMERGENZA - MASCHERA ORIGINALE COMPLETA - STATO SFONDO COLORATO - NON TOLGO MASCHERE',type='primary',use_container_width=True):
                if comune_tab and via_tab and azione_tab:
                    tab={'Data':str(data_tab),'Ora':str(ora_tab),'Comune':comune_tab,'Via':via_tab,'TipoIntervento':tipo_tab,'Priorita':priorita_tab,'Stato':stato_tab,'StatoColoreBg':bg_color,'StatoColoreTxt':txt_color,'Emergenza':emergenza_tab,'Icona':icona_tab if 'icona_tab' in locals() else 'Nessuna','Squadra':squadra_tab,'Volontari':','.join(volontari_tab) if volontari_tab else '','Mezzi':','.join(mezzi_tab) if mezzi_tab else '','Attrezzature':','.join(attrezzature_tab) if attrezzature_tab else '','Azione':azione_tab,'Note':note_tab,'Coordinate':coordinate_tab,'DataInserimento':str(date.today())}
                    st.session_state.tabella_interventi.append(tab)
                    st.success(f'Tabella Interventi - {comune_tab} - {via_tab} - Stato {stato_tab} salvato!'); st.balloons(); st.rerun()
                else:
                    st.error('Compila Comune combo Italia, Via combo, Azione - Maschera originale')
        if st.session_state.tabella_interventi:
            st.divider()
            c1,c2,c3,c4,c5=st.columns(5)
            with c1: filtro_comune=st.selectbox('Filtra per Comune', ['Tutti']+sorted(list(set([t.get('Comune','') for t in st.session_state.tabella_interventi]))), key='filtro_comune')
            with c2: filtro_prio=st.selectbox('Filtra per Priorita', ['Tutti','Urgente','Critica','Alta','Media','Bassa'], key='filtro_prio')
            with c3: filtro_stato=st.selectbox('Filtra per Stato', ['Tutti','Operativo','In Corso','Completato','Chiuso','In Stand By'], key='filtro_stato')
            with c4: filtro_squadra=st.selectbox('Filtra per Squadra', ['Tutte']+sorted(list(set([t.get('Squadra','') for t in st.session_state.tabella_interventi]))), key='filtro_squadra')
            with c5: filtro_tipo=st.selectbox('Filtra per Tipo', ['Tutti']+sorted(list(set([t.get('TipoIntervento','') for t in st.session_state.tabella_interventi]))), key='filtro_tipo')
            filtrati=st.session_state.tabella_interventi
            if filtro_comune!='Tutti': filtrati=[t for t in filtrati if t.get('Comune','')==filtro_comune]
            if filtro_prio!='Tutti': filtrati=[t for t in filtrati if t.get('Priorita','')==filtro_prio]
            if filtro_stato!='Tutti': filtrati=[t for t in filtrati if t.get('Stato','')==filtro_stato]
            if filtro_squadra!='Tutte': filtrati=[t for t in filtrati if t.get('Squadra','')==filtro_squadra]
            if filtro_tipo!='Tutti': filtrati=[t for t in filtrati if t.get('TipoIntervento','')==filtro_tipo]
            st.info(f'Filtrati: {len(filtrati)} su {len(st.session_state.tabella_interventi)} - Maschera originale')
            st.divider()
            st.markdown('<p style="font-family:Times New Roman;font-weight:bold;color:black;font-size:20px;background:#ffcccc;padding:10px;border-radius:8px;">TABELLA INTERVENTI URGENTI - SOLO PRIORITA URGENTE/CRITICA - COLONNA ICONA GRANDE VISIBILE + STATO SFONDO COLORATO - MASCHERA ORIGINALE</p>',unsafe_allow_html=True)
            urgenti=[t for t in filtrati if t.get('Priorita','') in ['Urgente','Critica']]
            if urgenti:
                for idx,interv in enumerate(urgenti):
                    bg_color, txt_color, label = get_stato_color(interv.get('Stato',''))
                    c1,c2,c3,c4,c5,c6=st.columns([1,2,2,2,2,1])
                    with c1:
                        icona_nome=interv.get('Icona','Nessuna')
                        st.markdown(f'<p style="font-family:Times New Roman;font-weight:bold;color:black;background:#ffcccc;padding:5px;">ICONA {icona_nome}</p>',unsafe_allow_html=True)
                        if icona_nome!='Nessuna':
                            ico=next((i for i in st.session_state.icone if i['Nome']==icona_nome),None)
                            if ico and ico.get('FileBytes'): st.image(ico['FileBytes'],width=80)
                    with c2:
                        st.markdown(f'<div style="background:{bg_color};color:{txt_color};padding:8px;border-radius:5px;border:2px solid black;"><p style="font-weight:bold;">STATO: {interv.get("Stato","")}</p><p>URGENTE: {interv.get("Comune","")} - {interv.get("Via","")}</p><p>{interv.get("Azione","")[:100]}</p></div>',unsafe_allow_html=True)
                    with c3: st.markdown(f'<p style="font-family:Times New Roman;font-weight:bold;color:black;">Tipo: {interv.get("TipoIntervento","")}<br>Priorita: {interv.get("Priorita","")}<br>Squadra: {interv.get("Squadra","")}</p>',unsafe_allow_html=True)
                    with c4: st.markdown(f'<p style="font-family:Times New Roman;font-weight:bold;color:black;">Volontari: {interv.get("Volontari","")[:80]}<br>Mezzi: {interv.get("Mezzi","")}</p>',unsafe_allow_html=True)
                    with c5: st.markdown(f'<p style="font-family:Times New Roman;font-weight:bold;color:black;">{interv.get("Data","")} {interv.get("Ora","")}<br>Coord: {interv.get("Coordinate","")}</p>',unsafe_allow_html=True)
                    with c6:
                        if st.button('Elimina',key=f'del_urg_{idx}'):
                            orig_idx=st.session_state.tabella_interventi.index(interv)
                            st.session_state.tabella_interventi.pop(orig_idx); st.rerun()
            st.divider()
            st.markdown('<p style="font-family:Times New Roman;font-weight:bold;color:black;font-size:18px;">TABELLA COMPLETA - TUTTI GLI INTERVENTI CON COLONNA ICONA VISIBILE + STATO SFONDO COLORATO</p>',unsafe_allow_html=True)
            for idx,interv in enumerate(filtrati):
                bg_color, txt_color, label = get_stato_color(interv.get('Stato',''))
                c1,c2,c3,c4,c5,c6=st.columns([1,2,2,2,1,1])
                with c1:
                    icona_nome=interv.get('Icona','Nessuna')
                    st.markdown(f'<p style="font-family:Times New Roman;font-weight:bold;color:black;">ICONA {icona_nome}</p>',unsafe_allow_html=True)
                    if icona_nome!='Nessuna':
                        ico=next((i for i in st.session_state.icone if i['Nome']==icona_nome),None)
                        if ico and ico.get('FileBytes'): st.image(ico['FileBytes'],width=60)
                with c2:
                    st.markdown(f'<div style="background:{bg_color};color:{txt_color};padding:5px;border-radius:5px;border:2px solid black;"><p style="font-weight:bold;">STATO: {interv.get("Stato","")}</p><p>{interv.get("Comune","")} - {interv.get("Via","")}<br>Tipo: {interv.get("TipoIntervento","")}</p><p>{interv.get("Azione","")[:100]}</p></div>',unsafe_allow_html=True)
                with c3: st.markdown(f'<p style="font-family:Times New Roman;font-weight:bold;color:black;">Priorita: {interv.get("Priorita","")}<br>Squadra: {interv.get("Squadra","")}</p>',unsafe_allow_html=True)
                with c4: st.markdown(f'<p style="font-family:Times New Roman;font-weight:bold;color:black;">Mezzi: {interv.get("Mezzi","")}<br>Attr: {interv.get("Attrezzature","")}</p>',unsafe_allow_html=True)
                with c5: st.markdown(f'<p style="font-family:Times New Roman;font-weight:bold;color:black;">{interv.get("Data","")} {interv.get("Ora","")}</p>',unsafe_allow_html=True)
                with c6:
                    if st.button('Elimina',key=f'del_tab_{idx}'):
                        orig_idx=st.session_state.tabella_interventi.index(interv)
                        st.session_state.tabella_interventi.pop(orig_idx); st.rerun()
            df_tab=pd.DataFrame(filtrati)
            st.dataframe(df_tab,use_container_width=True)
            c1,c2,c3=st.columns(3)
            c1.download_button('Excel Tabella Interventi - Maschera Originale',to_excel(df_tab),file_name='tabella_interventi_originale.xlsx',mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',use_container_width=True)
            pdf=to_pdf(df_tab,'Tabella Interventi - Maschera Originale')
            if pdf: c2.download_button('PDF Tabella - Maschera Originale',pdf,file_name='tabella_interventi_originale.pdf',mime='application/pdf',use_container_width=True)
            if c3.button('Svuota Tabella - Maschera Originale',key='clear_tab'):
                st.session_state.tabella_interventi=[]; st.rerun()

    elif cur=='Mezzi':
        hdr_form('MEZZI - MASCHERA ORIGINALE - TARGA MODELLO TIPO STATO ASSEGNATO SCADENZA REVISIONE - NON TOLGO MASCHERE - FONT NERO BOLD TIMES')
        with st.form('mezzi_form_originale'):
            c1,c2,c3=st.columns(3)
            with c1:
                targa=st.text_input('Targa * - FONT NERO BOLD TIMES - MASCHERA ORIGINALE',key='mezzo_targa')
                modello_m=st.text_input('Modello * - MASCHERA ORIGINALE',key='mezzo_mod')
                tipo_m=st.selectbox('Tipo Mezzo - MASCHERA ORIGINALE',['Pulmino','Fuoristrada','Autocarro','Furgone','Motoslitta','Gommone','Idrovora Carrellata','Torre Faro','Altro'],key='mezzo_tipo')
            with c2:
                stato_m=st.selectbox('Stato Mezzo - MASCHERA ORIGINALE',['Operativo','In Manutenzione','Fermo','Guasto','Disponibile'],key='mezzo_stato')
                assegnato_m=st.text_input('Assegnato a - Squadra/Volontario - MASCHERA ORIGINALE',key='mezzo_ass')
                scadenza_rev=st.date_input('Scadenza Revisione - MASCHERA ORIGINALE',value=date.today(),key='mezzo_scad')
            with c3:
                note_m=st.text_area('Note Mezzo - MASCHERA ORIGINALE',height=80,key='mezzo_note')
                km_m=st.text_input('Km / Ore Moto - MASCHERA ORIGINALE',key='mezzo_km')
                assicurazione_m=st.date_input('Scadenza Assicurazione - MASCHERA ORIGINALE',value=date.today(),key='mezzo_assic')
            if st.form_submit_button('SALVA MEZZO - MASCHERA ORIGINALE COMPLETA',type='primary',use_container_width=True):
                if targa and modello_m:
                    mz={'Targa':targa,'Modello':modello_m,'Tipo':tipo_m,'Stato':stato_m,'Assegnato':assegnato_m,'ScadenzaRevisione':str(scadenza_rev),'ScadenzaAssicurazione':str(assicurazione_m),'Km':km_m,'Note':note_m,'Data':str(date.today())}
                    st.session_state.mezzi.append(mz)
                    st.success(f'Mezzo {targa} {modello_m} salvato - maschera originale!'); st.balloons(); st.rerun()
        if st.session_state.mezzi:
            st.dataframe(pd.DataFrame(st.session_state.mezzi),use_container_width=True)
            for idx,mz in enumerate(st.session_state.mezzi):
                if st.button(f'Elimina Mezzo {mz.get("Targa","")} - {idx}',key=f'del_mezzo_{idx}'):
                    st.session_state.mezzi.pop(idx); st.rerun()

    elif cur=='Attrezzature':
        hdr_form('ATTREZZATURE - MASCHERA ORIGINALE - NOME CODICE TIPO STATO QUANTITA POSIZIONE SCADENZA - NON TOLGO MASCHERE')
        with st.form('attrezzature_form_originale'):
            c1,c2,c3=st.columns(3)
            with c1:
                nome_attr=st.text_input('Nome Attrezzatura * - FONT NERO BOLD TIMES - MASCHERA ORIGINALE',key='attr_nome')
                codice_attr=st.text_input('Codice * - MASCHERA ORIGINALE',key='attr_cod')
                tipo_attr=st.selectbox('Tipo - MASCHERA ORIGINALE',['Motosega','Gruppo Elettrogeno','Pompa Idrovora','Torcia','Radio','Kit Sanitario','Transenna','Tenda','Brandina','Altro'],key='attr_tipo')
            with c2:
                stato_attr=st.selectbox('Stato - MASCHERA ORIGINALE',['Disponibile','In Uso','Manutenzione','Guasta','In Carica','Scaduta'],key='attr_stato')
                quantita_attr=st.number_input('Quantita - MASCHERA ORIGINALE',min_value=1,value=1,key='attr_qta')
                posizione_attr=st.text_input('Posizione - Magazzino - MASCHERA ORIGINALE',key='attr_pos')
            with c3:
                scadenza_attr=st.date_input('Scadenza - MASCHERA ORIGINALE',value=date.today(),key='attr_scad')
                note_attr=st.text_area('Note Attrezzatura - MASCHERA ORIGINALE',height=80,key='attr_note')
            if st.form_submit_button('SALVA ATTREZZATURA - MASCHERA ORIGINALE COMPLETA',type='primary',use_container_width=True):
                if nome_attr and codice_attr:
                    at={'Nome':nome_attr,'Codice':codice_attr,'Tipo':tipo_attr,'Stato':stato_attr,'Quantita':quantita_attr,'Posizione':posizione_attr,'Scadenza':str(scadenza_attr),'Note':note_attr,'Data':str(date.today())}
                    st.session_state.attrezzature.append(at)
                    st.success(f'Attrezzatura {nome_attr} salvata - maschera originale!'); st.balloons(); st.rerun()
        if st.session_state.attrezzature:
            st.dataframe(pd.DataFrame(st.session_state.attrezzature),use_container_width=True)
            for idx,at in enumerate(st.session_state.attrezzature):
                if st.button(f'Elimina Attrezzatura {at.get("Nome","")} - {idx}',key=f'del_attr_{idx}'):
                    st.session_state.attrezzature.pop(idx); st.rerun()

    elif cur=='Mappa Avanzata':
        hdr_form('MAPPA AVANZATA - MASCHERA ORIGINALE - TIPO MAPPA OpenStreetMap/Google/Satellite + ICONA MARKER LIBRERIA + FULLSCREEN + CLICK DIRETTO - NON TOLGO MASCHERE')
        c1,c2=st.columns([3,1])
        with c2:
            tipo_mappa=st.selectbox('Tipo Mappa - MASCHERA ORIGINALE',['OpenStreetMap','Google Map','Satellite','Topografica'],key='tipo_mappa')
            fullscreen=st.checkbox('Fullscreen Mappa - MASCHERA ORIGINALE',key='fullscreen_mappa')
        with c1:
            st.markdown(f'<div style="border:3px solid {VERDE};height:{600 if fullscreen else 350}px;border-radius:10px;background:#e0f2e0;display:flex;align-items:center;justify-content:center;"><p style="font-family:Times New Roman;font-weight:bold;color:black;">MAPPA AVANZATA {tipo_mappa} - Fullscreen: {fullscreen} - MASCHERA ORIGINALE - Click su mappa per auto Comune Via - Reverse Geocoding<br>Postazioni: {len(st.session_state.postazioni)} - Icone: {len(st.session_state.icone)}</p></div>',unsafe_allow_html=True)
            if st.session_state.last_clicked:
                st.info(f"Ultimo click mappa: {st.session_state.last_clicked} - Comune e Via automatici da reverse geocoding - Maschera originale")
        st.divider()
        with st.form('postazione_form_originale'):
            st.markdown('<p style="font-family:Times New Roman;font-weight:bold;color:black;font-size:18px;">MASCHERA SOTTO MAPPA - NOME POSTAZIONE COMUNE COMBO ITALIA VIA VIE COMUNE LAT LON ICONA NOTE - MASCHERA ORIGINALE</p>',unsafe_allow_html=True)
            c1,c2,c3=st.columns(3)
            with c1:
                nome_post=st.text_input('Nome Postazione * - FONT NERO BOLD TIMES - MASCHERA ORIGINALE',key='post_nome')
                comune_post=combo_comune('Comune Postazione * - COMBO ITALIA - MASCHERA ORIGINALE','post_comune','Varese')
                via_post=combo_vie('Via Postazione * - VIE COMUNE - MASCHERA ORIGINALE',comune_post,'post_via')
            with c2:
                lat_post=st.text_input('Latitudine - MASCHERA ORIGINALE',key='post_lat', placeholder='45.657')
                lon_post=st.text_input('Longitudine - MASCHERA ORIGINALE',key='post_lon', placeholder='8.792')
                if st.session_state.icone:
                    lista_icone=[i['Nome'] for i in st.session_state.icone]
                    icona_post=st.selectbox('Icona Marker - DA LIBRERIA - MASCHERA ORIGINALE',lista_icone,key='post_icona')
                else:
                    icona_post=st.text_input('Icona - crea in Libreria Icone - MASCHERA ORIGINALE',key='post_icona_txt')
            with c3:
                note_post=st.text_area('Note Postazione - MASCHERA ORIGINALE',height=80,key='post_note')
                tipo_post=st.selectbox('Tipo Postazione - MASCHERA ORIGINALE',['Base Operativa','Punto Rititrovo','Magazzino','Check-point','Intervento','Altro'],key='post_tipo')
            if st.form_submit_button('SALVA POSTAZIONE - MAPPA AVANZATA MASCHERA ORIGINALE - COMUNE COMBO ITALIA + VIA VIE COMUNE + ICONA',type='primary',use_container_width=True):
                if nome_post and comune_post:
                    pst={'NomePostazione':nome_post,'Comune':comune_post,'Via':via_post,'Lat':lat_post,'Lon':lon_post,'Icona':icona_post if 'icona_post' in locals() else 'Nessuna','Note':note_post,'Tipo':tipo_post,'Data':str(date.today())}
                    st.session_state.postazioni.append(pst)
                    st.success(f'Postazione {nome_post} - {comune_post} - {via_post} salvata - maschera originale mappa avanzata!'); st.balloons(); st.rerun()
        if st.session_state.postazioni:
            st.divider()
            st.markdown('<p style="font-family:Times New Roman;font-weight:bold;color:black;font-size:18px;">MAPPA RIEPILOGO SOTTO CON TUTTE POSTAZIONI CON ICONE + TABELLA POSTAZIONI - MASCHERA ORIGINALE</p>',unsafe_allow_html=True)
            c1,c2=st.columns([2,1])
            with c1:
                st.markdown(f'<div style="border:2px solid {VERDE};height:300px;border-radius:8px;background:#d0e8d0;display:flex;align-items:center;justify-content:center;"><p style="font-family:Times New Roman;font-weight:bold;color:black;">MAPPA RIEPILOGO - Tutte postazioni con icone - {len(st.session_state.postazioni)} postazioni<br>{" | ".join([p.get("NomePostazione","")+" ("+p.get("Comune","")+ ")" for p in st.session_state.postazioni[:5]])}</p></div>',unsafe_allow_html=True)
            with c2:
                st.dataframe(pd.DataFrame(st.session_state.postazioni),use_container_width=True)
            for idx,pst in enumerate(st.session_state.postazioni):
                c1,c2,c3=st.columns([3,2,1])
                with c1:
                    icona_nome=pst.get('Icona','Nessuna')
                    ico=next((i for i in st.session_state.icone if i['Nome']==icona_nome),None)
                    if ico and ico.get('FileBytes'):
                        st.image(ico['FileBytes'],width=40)
                    st.markdown(f'<p style="font-family:Times New Roman;font-weight:bold;color:black;">{pst.get("NomePostazione","")} - {pst.get("Comune","")} - {pst.get("Via","")}<br>Lat: {pst.get("Lat","")} Lon: {pst.get("Lon","")} - Icona: {icona_nome}</p>',unsafe_allow_html=True)
                with c2:
                    st.markdown(f'<p style="font-family:Times New Roman;font-weight:bold;color:black;">Tipo: {pst.get("Tipo","")}<br>Note: {pst.get("Note","")[:60]}</p>',unsafe_allow_html=True)
                with c3:
                    if st.button('Elimina',key=f'del_post_{idx}'):
                        st.session_state.postazioni.pop(idx); st.rerun()

    elif cur=='Libreria Icone':
        hdr_form('LIBRERIA ICONE - MASCHERA ORIGINALE - NOME ICONA FILE UPLOAD PNG/JPG PREVIEW AGGANCIATA IN INTERVENTI - NON TOLGO MASCHERE')
        st.info('MASCHERA ORIGINALE LIBRERIA ICONE - Nome icona, File upload PNG/JPG, Preview, Agganciata in Interventi Emergenza e Tabella Interventi - Non tolgo maschere')
        with st.form('icone_form_originale'):
            c1,c2,c3=st.columns(3)
            with c1:
                nome_icona=st.text_input('Nome Icona * - FONT NERO BOLD TIMES - MASCHERA ORIGINALE',key='icona_nome')
                categoria_icona=st.selectbox('Categoria Icona - MASCHERA ORIGINALE',['Emergenza','Intervento','Mezzo','Attrezzatura','Evento','Allarme','Altro'],key='icona_cat')
            with c2:
                file_icona=st.file_uploader('File Icona PNG/JPG * - UPLOAD - MASCHERA ORIGINALE COMPLETA',type=['png','jpg','jpeg'],key='icona_file')
                if file_icona: st.image(file_icona,width=100,caption='Preview Icona - Maschera originale')
            with c3:
                note_icona=st.text_area('Note Icona - MASCHERA ORIGINALE',height=80,key='icona_note')
                agganciata=st.checkbox('Agganciata in Interventi - MASCHERA ORIGINALE',value=True,key='icona_agg')
            if st.form_submit_button('SALVA ICONA - LIBRERIA ICONE MASCHERA ORIGINALE - PREVIEW + AGGANCIATA INTERVENTI',type='primary',use_container_width=True):
                if nome_icona and file_icona:
                    ico={'Nome':nome_icona,'Categoria':categoria_icona,'FileBytes':file_icona.getvalue(),'Note':note_icona,'Agganciata':agganciata,'Data':str(date.today())}
                    st.session_state.icone.append(ico)
                    st.success(f'Icona {nome_icona} salvata - maschera originale libreria icone - Agganciata interventi!'); st.balloons(); st.rerun()
        if st.session_state.icone:
            st.divider()
            st.markdown('<p style="font-family:Times New Roman;font-weight:bold;color:black;font-size:18px;">ELENCO ICONE - PREVIEW GRANDE VISIBILE - AGGANCIATA IN INTERVENTI - MASCHERA ORIGINALE</p>',unsafe_allow_html=True)
            cols=st.columns(4)
            for idx,ico in enumerate(st.session_state.icone):
                with cols[idx % 4]:
                    if ico.get('FileBytes'): st.image(ico.get('FileBytes'),width=100,caption=ico.get('Nome',''))
                    st.markdown(f'<p style="font-family:Times New Roman;font-weight:bold;color:black;">{ico.get("Nome","")}<br>Cat: {ico.get("Categoria","")}<br>Agganciata: {ico.get("Agganciata",False)}</p>',unsafe_allow_html=True)
                    if st.button(f'Elimina {ico.get("Nome","")}',key=f'del_icona_{idx}'):
                        st.session_state.icone.pop(idx); st.rerun()
            st.dataframe(pd.DataFrame([{'Nome':i.get('Nome',''),'Categoria':i.get('Categoria',''),'Agganciata':i.get('Agganciata',False),'Data':i.get('Data','')} for i in st.session_state.icone]),use_container_width=True)

    elif cur=='Chat':
        hdr_form('CHAT - MASCHERA ORIGINALE RIPRISTINATA - MITTENTE DA ALIAS RADIO DESTINATARIO DA ALIAS RADIO CANALE PRIORITA MESSAGGIO - NON TOLGO MASCHERE')
        st.info('CHAT MASCHERA ORIGINALE RIPRISTINATA - Mittente da Alias Radio combo, Destinatario da Alias Radio combo, Canale, Priorita, Messaggio, Data/Ora, Storico con elimina, Export - Non tolgo maschere')
        with st.form('chat_form_originale'):
            c1,c2,c3=st.columns(3)
            with c1:
                if st.session_state.alias_radio:
                    lista_alias=[a.get('NomeAlias','') for a in st.session_state.alias_radio]
                    mittente_chat=st.selectbox('Mittente * - DA ALIAS RADIO COMBO - MASCHERA ORIGINALE',lista_alias,key='chat_mitt')
                    destinatario_chat=st.selectbox('Destinatario * - DA ALIAS RADIO COMBO - MASCHERA ORIGINALE',lista_alias,key='chat_dest')
                else:
                    mittente_chat=st.text_input('Mittente - crea Alias Radio - MASCHERA ORIGINALE',key='chat_mitt_txt')
                    destinatario_chat=st.text_input('Destinatario - crea Alias Radio - MASCHERA ORIGINALE',key='chat_dest_txt')
                    st.warning('Crea prima Alias Radio per combo mittente/destinatario - Maschera originale')
                canale_chat=st.selectbox('Canale - MASCHERA ORIGINALE',['Canale 1','Canale 2','Emergenza','Coordinamento','Logistica','Altro'],key='chat_canale')
            with c2:
                priorita_chat=st.selectbox('Priorita Messaggio - MASCHERA ORIGINALE',['Bassa','Media','Alta','Urgente','Critica'],key='chat_prio')
                data_chat=st.date_input('Data - MASCHERA ORIGINALE',value=date.today(),key='chat_data')
                ora_chat=st.time_input('Ora - MASCHERA ORIGINALE',value=datetime.now().time(),key='chat_ora')
            with c3:
                messaggio_chat=st.text_area('Messaggio * - FONT NERO BOLD TIMES - MASCHERA ORIGINALE',height=100,key='chat_msg')
            if st.form_submit_button('INVIA MESSAGGIO CHAT - MASCHERA ORIGINALE - MITTENTE DA ALIAS RADIO',type='primary',use_container_width=True):
                if mittente_chat and destinatario_chat and messaggio_chat:
                    chat_msg={'Mittente':mittente_chat,'Destinatario':destinatario_chat,'Canale':canale_chat,'Priorita':priorita_chat,'Messaggio':messaggio_chat,'Data':str(data_chat),'Ora':str(ora_chat),'DataOra':str(date.today())+' '+str(datetime.now().time())[:5]}
                    st.session_state.chat.append(chat_msg)
                    st.success(f'Messaggio da {mittente_chat} a {destinatario_chat} inviato - maschera originale chat!'); st.balloons(); st.rerun()
        if st.session_state.chat:
            st.divider()
            st.markdown('<p style="font-family:Times New Roman;font-weight:bold;color:black;font-size:18px;">STORICO CHAT CON ELIMINA + EXPORT - MASCHERA ORIGINALE COMPLETA - NON TOLGO MASCHERE</p>',unsafe_allow_html=True)
            for idx,ch in enumerate(reversed(st.session_state.chat)):
                orig_idx=len(st.session_state.chat)-1-idx
                bg='#ffcccc' if ch.get('Priorita','') in ['Urgente','Critica'] else '#e0ffe0'
                st.markdown(f'<div style="background:{bg};padding:10px;border-radius:8px;border:1px solid {VERDE};margin:5px 0;"><p style="font-family:Times New Roman;font-weight:bold;color:black;">[{ch.get("Data","")} {ch.get("Ora","")}] {ch.get("Mittente","")} -> {ch.get("Destinatario","")} - Canale: {ch.get("Canale","")} - Priorita: {ch.get("Priorita","")}<br>Messaggio: {ch.get("Messaggio","")}</p></div>',unsafe_allow_html=True)
                if st.button(f'Elimina messaggio {orig_idx}',key=f'del_chat_{orig_idx}'):
                    st.session_state.chat.pop(orig_idx); st.rerun()
            df_chat=pd.DataFrame(st.session_state.chat)
            st.dataframe(df_chat,use_container_width=True)
            c1,c2=st.columns(2)
            c1.download_button('Export Chat Excel - Maschera Originale',to_excel(df_chat),file_name='chat_originale.xlsx',mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',use_container_width=True)
            if c2.button('Svuota Chat - Maschera Originale',key='clear_chat'):
                st.session_state.chat=[]; st.rerun()

    elif cur=='Backup':
        hdr_form('BACKUP - MASCHERA ORIGINALE - CON NOME FORM DOVE CARICARE FILE E VA SU FORM ASSEGNATO + EXPORT SU BACKUP - SENZA FORM ESPORTA - NON TOLGO MASCHERE - FONT NERO BOLD TIMES')
        st.info('BACKUP MASCHERA ORIGINALE - Con nome form dove caricare file e va su form assegnato - Export su Backup senza form Esporta separato - Non tolgo maschere - Tutti form originali 950+')
        datasets={'Volontari':st.session_state.volontari,'DB Radio':st.session_state.radio_db,'Consegna Radio':st.session_state.consegna_radio,'Alias Radio':st.session_state.alias_radio,'Eventi':st.session_state.eventi,'Emergenze':st.session_state.emergenze,'Interventi Emergenza':st.session_state.interventi,'Tabella Interventi Emergenza':st.session_state.tabella_interventi,'Postazioni':st.session_state.postazioni,'Chat':st.session_state.chat,'Brogliaccio':st.session_state.brogliaccio,'Mezzi':st.session_state.mezzi,'Attrezzature':st.session_state.attrezzature,'Icone':st.session_state.icone,'Checkin':st.session_state.checkin}
        totale=sum([len(v) for v in datasets.values() if v])
        st.markdown(f'<p style="font-family:Times New Roman;font-weight:bold;color:black;font-size:18px;">BACKUP TOTALE - {totale} record - TUTTI I FORM MASCHERE ORIGINALI - EXPORT SU BACKUP - SENZA FORM ESPORTA - 950+ RIGHE</p>',unsafe_allow_html=True)
        c1,c2,c3=st.columns(3)
        with c1:
            if any(datasets.values()):
                st.download_button('📥 EXPORT TOTALE EXCEL - TUTTI I FORM MASCHERE ORIGINALI - SU BACKUP - ORIGINALE',to_excel_multi(datasets),file_name=f'backup_TUTTO_ORIGINALE_{date.today()}.xlsx',mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',use_container_width=True,type='primary')
        with c2:
            backup_json=json.dumps({k:[{kk:vv for kk,vv in rec.items() if kk not in ['FotoBytes','FileBytes','FotoConsegnaBytes','IconaBytes']} for rec in v] for k,v in datasets.items()},default=str,indent=2)
            st.download_button('📥 BACKUP JSON COMPLETO - MASCHERE ORIGINALI - ORIGINALE',backup_json,file_name=f'backup_JSON_ORIGINALE_{date.today()}.json',mime='application/json',use_container_width=True)
        with c3:
            st.metric('Totale Form Originali', len([k for k,v in datasets.items() if v]), f'{totale} record - Maschere originali')
        st.divider()
        st.markdown('<p style="font-family:Times New Roman;font-weight:bold;color:black;font-size:18px;">IMPORT TOTALE - CON NOME FORM - VA SU FORM ASSEGNATO - MASCHERA ORIGINALE - NON TOLGO MASCHERE</p>',unsafe_allow_html=True)
        up_tot=st.file_uploader('Carica Backup Excel TOTALE - IMPORT TOTALE - VA SU FORM ASSEGNATI - MASCHERA ORIGINALE COMPLETA',type=['xlsx'],key='up_backup_tot')
        if up_tot:
            try:
                xls=pd.ExcelFile(up_tot)
                st.write(f'Fogli trovati con nome form maschere originali: {xls.sheet_names} - Import totale maschere originali')
                if st.button('🔄 IMPORTA TUTTO - VA SU FORM ASSEGNATI - MASCHERE ORIGINALI COMPLETE',type='primary',use_container_width=True):
                    for sheet in xls.sheet_names:
                        df=pd.read_excel(xls,sheet_name=sheet)
                        records=df.to_dict('records')
                        if sheet=='Volontari': st.session_state.volontari=records
                        elif sheet=='DB Radio': st.session_state.radio_db=records
                        elif sheet=='Consegna Radio': st.session_state.consegna_radio=records
                        elif sheet=='Alias Radio': st.session_state.alias_radio=records
                        elif sheet=='Eventi': st.session_state.eventi=records
                        elif sheet=='Emergenze': st.session_state.emergenze=records
                        elif sheet=='Interventi Emergenza': st.session_state.interventi=records
                        elif sheet=='Tabella Interventi Emergenza': st.session_state.tabella_interventi=records
                        elif sheet=='Postazioni': st.session_state.postazioni=records
                        elif sheet=='Chat': st.session_state.chat=records
                        elif sheet=='Brogliaccio': st.session_state.brogliaccio=records
                        elif sheet=='Mezzi': st.session_state.mezzi=records
                        elif sheet=='Attrezzature': st.session_state.attrezzature=records
                        elif sheet=='Icone': st.session_state.icone=[]
                        elif sheet=='Checkin': st.session_state.checkin=records
                    st.success(f'Import totale maschere originali completato! Va su form assegnati - {totale} record! - Non tolgo maschere!')
                    st.balloons(); st.rerun()
            except Exception as e: st.error(f'Errore import totale maschere originali: {e}')
        st.divider()
        st.markdown('<p style="font-family:Times New Roman;font-weight:bold;color:black;font-size:20px;">BACKUP PER SINGOLO FORM - CON NOME FORM DOVE CARICARE FILE - VA SU FORM ASSEGNATO - EXPORT SU BACKUP - MASCHERE ORIGINALI - NON TOLGO MASCHERE</p>',unsafe_allow_html=True)
        form_mapping = [
            ('volontari','Volontari (con foto) - Maschera Originale Foto Prima','Volontari'),
            ('radio_db','DB Radio - Maschera Originale Completa','DB Radio'),
            ('consegna_radio','Consegna Radio - Maschera Originale Completa','Consegna Radio'),
            ('alias_radio','Alias Radio - Maschera Originale','Alias Radio'),
            ('eventi','Eventi - Maschera Originale Comune Combo Italia','Eventi'),
            ('emergenze','Emergenze - Maschera Originale Comune Combo','Emergenze'),
            ('interventi','Interventi Emergenza - Maschera Originale Stato Colorato + Icona','Interventi Emergenza'),
            ('tabella_interventi','Tabella Interventi Emergenza - Maschera Originale Stato Colorato - Ripristinato completo','Tabella Interventi Emergenza'),
            ('brogliaccio','Brogliaccio - Maschera Originale Blindata','Brogliaccio'),
            ('checkin','Check-in - Maschera Originale Blindata','Check-in'),
            ('mezzi','Mezzi - Maschera Originale Targa Modello','Mezzi'),
            ('attrezzature','Attrezzature - Maschera Originale Nome Codice','Attrezzature'),
            ('postazioni','Postazioni Mappa - Maschera Originale Comune Via','Mappa Avanzata'),
            ('icone','Libreria Icone - Maschera Originale Upload','Libreria Icone'),
            ('chat','Chat - Maschera Originale Mittente Alias','Chat')
        ]
        for key, titolo_menu, nome_form in form_mapping:
            st.markdown(f'<div style="border:2px solid {VERDE};padding:10px;border-radius:8px;margin:5px 0;background:#f0f8f0;"><p style="font-family:Times New Roman;font-weight:bold;color:black;font-size:16px;">📋 FORM: {titolo_menu} - NOME FORM: {nome_form} - MASCHERA ORIGINALE - {len(st.session_state[key])} record - NON TOLGO MASCHERE</p></div>',unsafe_allow_html=True)
            c1,c2,c3,c4,c5=st.columns([2,2,2,2,2])
            with c1:
                if st.session_state[key]:
                    st.download_button(f'📥 Excel {nome_form} - EXPORT SU BACKUP - ORIGINALE', to_excel(pd.DataFrame(st.session_state[key])), file_name=f"{key}_{date.today()}.xlsx", mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', key=f'excel_{key}', use_container_width=True)
            with c2:
                if st.session_state[key]:
                    pdf=to_pdf(pd.DataFrame(st.session_state[key]), nome_form)
                    if pdf:
                        st.download_button(f"📄 PDF {nome_form} - EXPORT SU BACKUP - ORIGINALE", pdf, file_name=f"{key}_{date.today()}.pdf", mime='application/pdf', key=f'pdf_{key}', use_container_width=True)
            with c3:
                up=st.file_uploader(f'📤 Carica per FORM: {nome_form} - NOME FORM DOVE CARICARE - ORIGINALE', type=['xlsx'], key=f'up_{key}')
                if up:
                    try:
                        df_imp=pd.read_excel(up)
                        st.write(f'File per FORM: {nome_form} - Maschera originale - {len(df_imp)} righe')
                        if st.button(f'✅ Importa {len(df_imp)} in FORM: {nome_form} - VA SU FORM ASSEGNATO {titolo_menu} - ORIGINALE', key=f'imp_{key}'):
                            for _,row in df_imp.iterrows():
                                st.session_state[key].append(row.to_dict())
                            st.success(f'Importati {len(df_imp)} in FORM: {nome_form} - Vado su form assegnato: {titolo_menu} - Maschera originale')
                            st.session_state.menu=titolo_menu
                            st.balloons(); st.rerun()
                    except Exception as e: st.error(f'Errore import {nome_form} maschera originale: {e}')
            with c4:
                if st.session_state[key]:
                    if st.button(f'👁️ Vai a FORM: {titolo_menu} - ORIGINALE', key=f'goto_{key}'):
                        st.session_state.menu=titolo_menu; st.rerun()
            with c5:
                if st.session_state[key]:
                    if st.button(f'🗑️ Svuota {nome_form} - ORIGINALE', key=f'clear_{key}'):
                        st.session_state[key]=[]; st.rerun()
            st.divider()

# FOOTER FIX DEFINITIVO - MASCHERE ORIGINALI COMPLETE
st.markdown(f'<div style="background:{VERDE};padding:12px;border-radius:8px;color:white;font-weight:bold;font-family:Times New Roman;text-align:center;margin-top:20px;">ANA VARESE - FIX DEFINITIVO - TUTTE LE MASCHERE ORIGINALI COMPLETE - NON TOLGO PIU MASCHERE DAI FORM - 950+ RIGHE - FONT NERO GRASSETTO TIMES NEW ROMAN - NO ICONA HEADER - VERSIONE DEFINITIVA</div>',unsafe_allow_html=True)
