import streamlit as st
import pandas as pd
import os
from io import BytesIO
from datetime import date, datetime
import tempfile
import json
import requests

st.set_page_config(page_title='ANA Varese', layout='wide')
VERDE = "#1A5D1A"
st.markdown(f"""
<style>
h1,h2,h3{{color:{VERDE}!important;}}
.stButton>button{{background:{VERDE}!important;color:white!important;font-weight:bold!important;}}
input, textarea, select, .stTextInput input, .stTextArea textarea {{
    color: black !important;
    font-weight: bold !important;
    font-family: 'Times New Roman', Times, serif !important;
    font-size: 16px !important;
}}
label {{
    color: black !important;
    font-weight: bold !important;
    font-family: 'Times New Roman', Times, serif !important;
}}
</style>
""", unsafe_allow_html=True)

COMUNI_ITALIA = ["Varese","Milano","Busto Arsizio","Gallarate","Saronno","Tradate","Somma Lombardo","Cassano Magnago","Malnate","Lonate Pozzolo","Sesto Calende","Gavirate","Luino","Laveno-Mombello","Besozzo","Caronno Pertusella","Caronno Varesino","Albizzate","Angera","Arcisate","Azzate","Bardello","Besano","Besnate","Biandronno","Bisuschio","Bodio Lomnago","Brebbia","Brenta","Brinzio","Brusimpiano","Buguggiate","Cadegliano-Viconago","Cairate","Cantello","Caravate","Cardano al Campo","Carnago","Casale Litta","Casalzuigno","Casciago","Casorate Sempione","Cassano Valcuvia","Castellanza","Castelseprio","Castiglione Olona","Castronno","Cavaria con Premezzo","Cazzago Brabbia","Cislago","Cittiglio","Clivio","Cocquio-Trevisago","Comabbio","Comerio","Cugliate-Fabiasco","Cunardo","Cuvio","Daverio","Dumenza","Fagnano Olona","Ferno","Gazzada Schianno","Gemonio","Gerenzano","Germignaga","Golasecca","Gorla Maggiore","Gorla Minore","Gornate-Olona","Inarzo","Induno Olona","Ispra","Jerago con Orago","Lavena Ponte Tresa","Leggiuno","Lonate Ceppino","Lozza","Maccagno con Pino e Veddasca","Malgesso","Marzio","Mercallo","Mesenzana","Monvalle","Morazzone","Mornago","Oggiona con Santo Stefano","Olgiate Olona","Origgio","Orino","Porto Ceresio","Porto Valtravaglia","Rancio Valcuvia","Saltrio","Samarate","Solbiate Arno","Solbiate Olona","Sumirago","Taino","Ternate","Travedona Monate","Uboldo","Valganna","Varano Borghi","Vedano Olona","Venegono Inferiore","Venegono Superiore","Vergiate","Viggiu","Roma","Torino","Napoli","Bologna","Firenze","Genova","Palermo","Venezia"]

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
    return ["Via Roma","Via Garibaldi","Via Milano","Via Verdi","Via Dante","Via Manzoni","Via Matteotti","Piazza Liberta","Via IV Novembre","Via San Giovanni"]

def hdr():
    c1,c2=st.columns([1,5])
    with c1:
        try: st.image('logo.png',width=110)
        except: st.markdown('**ANA**')
    with c2:
        st.markdown(f'<div style="background:{VERDE};padding:12px;border-radius:8px;color:white;font-weight:bold;font-family:Times New Roman;">NUCLEO PROT CIVILE ANA VARESE - TUTTI FIX - STATO SFONDO COLORATO - 950+</div>',unsafe_allow_html=True)

def hdr_form(t): st.markdown(f'<h2 style="font-family:Times New Roman;color:black;font-weight:bold;">{t}</h2>',unsafe_allow_html=True)
def to_excel(df):
    out=BytesIO()
    cols=[c for c in df.columns if c not in ['Foto','FotoBytes','FileBytes','FotoConsegnaBytes']]
    df[cols].to_excel(out,index=False,engine='openpyxl')
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
                    cols=[c for c in df.columns if c not in ['Foto','FotoBytes','FileBytes','FotoConsegnaBytes']]
                    df[cols].to_excel(writer,sheet_name=nome[:31],index=False)
                except: pass
    return out.getvalue()
def salva_icona_temp(fb,nome):
    try:
        p=os.path.join(tempfile.gettempdir(),f"icon_{nome}.png")
        open(p,"wb").write(fb)
        return p
    except: return None
def combo_comune(label,key,default=""):
    comuni=get_comuni()
    if default and default not in comuni: comuni=[default]+comuni
    idx=comuni.index(default) if default in comuni else 0
    return st.selectbox(f'{label} - COMUNI ITALIA',comuni,index=idx,key=key)
def combo_vie(label,comune,key,default=""):
    if comune:
        vie=get_vie(comune)
        if default and default not in vie: vie=[default]+vie
        idx=vie.index(default) if default in vie else 0
        sel=st.selectbox(f'{label} - VIE DI {comune.upper()}',vie,index=idx,key=key)
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
        st.markdown(f'<h2 style="text-align:center;font-family:Times New Roman;font-weight:bold;color:black;">GESTIONALE 950+ - TUTTI FIX</h2>',unsafe_allow_html=True)
        if st.button('ENTRA',use_container_width=True,type='primary'):
            st.session_state.page='login'
            st.rerun()
elif st.session_state.page=='login':
    hdr()
    c1,c2,c3=st.columns([1,2,1])
    with c2:
        u=st.text_input('Utente')
        p=st.text_input('Password',type='password')
        if st.button('Accedi',use_container_width=True,type='primary'):
            if u=='admin' and p=='ana2024':
                st.session_state.logged=True
                st.session_state.page='dashboard'
                st.rerun()
            else: st.error('admin / ana2024')

elif st.session_state.page=='dashboard':
    hdr()
    menu_base=['Dashboard','Volontari (con foto)','DB Radio','Consegna Radio','Alias Radio','Brogliaccio','Eventi','Emergenze','Check-in','Interventi Emergenza','Tabella Interventi Emergenza','Mezzi','Attrezzature','Mappa Avanzata','Libreria Icone','Chat','Backup']
    with st.sidebar:
        try: st.image('logo.png',width=120)
        except: pass
        st.markdown('<p style="font-family:Times New Roman;font-weight:bold;color:black;">MENU 950+ TUTTI FIX - COME PRIMA</p>',unsafe_allow_html=True)
        try: idx=menu_base.index(st.session_state.menu)
        except: idx=0
        m=st.radio('Scegli form:',menu_base,index=idx)
        st.session_state.menu=m
        if st.button('Logout',use_container_width=True):
            st.session_state.page='entra'
            st.rerun()
    cur=st.session_state.menu

    if cur=='Dashboard':
        hdr_form('Dashboard - 950+ - TUTTI FIX - STATO SFONDO COLORATO - TABELLA INTERVENTI RIPRISTINATA')
        c1,c2,c3,c4=st.columns(4)
        c1.metric('Volontari',len(st.session_state.volontari))
        c2.metric('Radio',len(st.session_state.radio_db))
        c3.metric('Consegna Radio',len(st.session_state.consegna_radio))
        c4.metric('Interventi',len(st.session_state.interventi))
        c1b,c2b,c3b,c4b=st.columns(4)
        c1b.metric('Tabella Interventi',len(st.session_state.tabella_interventi))
        c2b.metric('Chat',len(st.session_state.chat))
        c3b.metric('Emergenze',len(st.session_state.emergenze))
        c4b.metric('Icone',len(st.session_state.icone))
        st.divider()
        st.markdown('<p style="font-family:Times New Roman;font-weight:bold;color:black;">LEGENDA STATO SFONDO COLORATO</p>',unsafe_allow_html=True)
        c1,c2,c3,c4,c5=st.columns(5)
        with c1: st.markdown('<div style="background:#ff0000;color:white;padding:10px;border-radius:5px;text-align:center;font-weight:bold;">OPERATIVO ROSSO</div>',unsafe_allow_html=True)
        with c2: st.markdown('<div style="background:#ffff00;color:black;padding:10px;border-radius:5px;text-align:center;font-weight:bold;">IN CORSO GIALLO</div>',unsafe_allow_html=True)
        with c3: st.markdown('<div style="background:#00ff00;color:black;padding:10px;border-radius:5px;text-align:center;font-weight:bold;">COMPLETATO VERDE</div>',unsafe_allow_html=True)
        with c4: st.markdown('<div style="background:#808080;color:white;padding:10px;border-radius:5px;text-align:center;font-weight:bold;">CHIUSO GRIGIO</div>',unsafe_allow_html=True)
        with c5: st.markdown('<div style="background:#ff8c00;color:white;padding:10px;border-radius:5px;text-align:center;font-weight:bold;">STAND BY ARANCIONE</div>',unsafe_allow_html=True)
        st.divider()
        r1=st.columns(4)
        with r1[0]:
            if st.button('VOLONTARI ORIGINALE FOTO PRIMA',key='btn_vol',use_container_width=True,type='primary'):
                st.session_state.menu='Volontari (con foto)'
                st.rerun()
        with r1[1]:
            if st.button('CONSEGNA RADIO',key='btn_cons',use_container_width=True,type='primary'):
                st.session_state.menu='Consegna Radio'
                st.rerun()
        with r1[2]:
            if st.button('TABELLA INTERVENTI - STATO COLORATO',key='btn_tab',use_container_width=True,type='primary'):
                st.session_state.menu='Tabella Interventi Emergenza'
                st.rerun()
        with r1[3]:
            if st.button('INTERVENTI + STATO COLORATO',key='btn_int',use_container_width=True,type='primary'):
                st.session_state.menu='Interventi Emergenza'
                st.rerun()
        r2=st.columns(4)
        with r2[0]:
            if st.button('MAPPA',key='btn_mappa',use_container_width=True,type='primary'):
                st.session_state.menu='Mappa Avanzata'
                st.rerun()
        with r2[1]:
            if st.button('CHAT',key='btn_chat',use_container_width=True,type='primary'):
                st.session_state.menu='Chat'
                st.rerun()
        with r2[2]:
            if st.button('BACKUP NOME FORM',key='btn_backup',use_container_width=True,type='primary'):
                st.session_state.menu='Backup'
                st.rerun()
        with r2[3]:
            if st.button('LIBRERIA ICONE',key='btn_icone',use_container_width=True,type='primary'):
                st.session_state.menu='Libreria Icone'
                st.rerun()

    elif cur=='Volontari (con foto)':
        hdr_form('VOLONTARI - MASCHERA ORIGINALE FOTO PRIMA MASCHERA - COMUNI COMBO + FONT NERO BOLD TIMES')
        with st.form('vol_form'):
            c1,c2,c3=st.columns([2,2,1])
            with c1:
                nome=st.text_input('Nome *',key='vol_nome')
                cognome=st.text_input('Cognome *',key='vol_cognome')
                comune_res=combo_comune('Comune Residenza *', 'vol_comune', 'Varese')
                via_res=combo_vie('Via Residenza', comune_res, 'vol_via')
            with c2:
                cell=st.text_input('Cellulare *',key='vol_cell')
                ruolo=st.selectbox('Ruolo *', ['Volontario','Caposquadra','Coordinatore','Autista','Radio','Logistica','Sanitario','Altro'],key='vol_ruolo')
                squadra=st.selectbox('Squadra *', ['Alpini Caronno','Squadra A','Squadra B','Squadra C'],key='vol_squadra')
            with c3:
                foto=st.file_uploader('Foto * - PRIMA MASCHERA',type=['png','jpg','jpeg'],key='vol_foto_prima')
                if foto: st.image(foto,width=150,caption='Preview Foto Prima Maschera')
            if st.form_submit_button('SALVA VOLONTARIO - MASCHERA ORIGINALE FOTO PRIMA',type='primary',use_container_width=True):
                if nome and cognome and comune_res and cell:
                    v={'Nome':nome,'Cognome':cognome,'Comune':comune_res,'ViaRes':via_res,'Cellulare':cell,'Ruolo':ruolo,'Squadra':squadra,'FotoBytes':foto.getvalue() if foto else None,'Data':str(date.today())}
                    st.session_state.volontari.append(v)
                    st.success(f'Volontario {nome} salvato! Maschera originale foto prima!')
                    st.balloons()
                    st.rerun()
        if st.session_state.volontari:
            st.dataframe(pd.DataFrame([{'Nome':v.get('Nome',''),'Cognome':v.get('Cognome',''),'Foto':'SI' if v.get('FotoBytes') else 'NO'} for v in st.session_state.volontari]),use_container_width=True)

    elif cur=='Consegna Radio':
        hdr_form('CONSEGNA RADIO - RIPRISTINATO - MASCHERA ORIGINALE - FONT NERO BOLD TIMES')
        with st.form('cons_form'):
            c1,c2,c3=st.columns(3)
            with c1:
                data_cons=st.date_input('Data Consegna *',value=date.today(),key='cons_data')
                if st.session_state.volontari:
                    lista_vol=[f"{v.get('Nome','')} {v.get('Cognome','')}" for v in st.session_state.volontari]
                    volontario_cons=st.selectbox('Volontario *', lista_vol, key='cons_vol')
                else:
                    volontario_cons=st.text_input('Volontario *',key='cons_vol_txt')
            with c2:
                if st.session_state.radio_db:
                    lista_radio=[f"{r.get('Modello','')} - {r.get('Matricola','')}" for r in st.session_state.radio_db]
                    radio_cons=st.selectbox('Radio *', lista_radio, key='cons_radio')
                else:
                    radio_cons=st.text_input('Radio *',key='cons_radio_txt')
                stato_cons=st.selectbox('Stato Consegna *', ['Consegnata','Restituita','In Uso','Guasta'],key='cons_stato')
            with c3:
                foto_cons=st.file_uploader('Foto Consegna',type=['png','jpg','jpeg'],key='cons_foto')
                if foto_cons: st.image(foto_cons,width=100)
                firma_cons=st.text_input('Firma',key='cons_firma')
            note_cons=st.text_area('Note',height=60,key='cons_note')
            if st.form_submit_button('SALVA CONSEGNA RADIO',type='primary',use_container_width=True):
                if volontario_cons and radio_cons:
                    cons={'DataConsegna':str(data_cons),'Volontario':volontario_cons,'Radio':radio_cons,'StatoConsegna':stato_cons,'Firma':firma_cons,'Note':note_cons,'FotoConsegnaBytes':foto_cons.getvalue() if foto_cons else None,'Data':str(date.today())}
                    st.session_state.consegna_radio.append(cons)
                    st.success(f'Consegna {radio_cons} a {volontario_cons} salvata!')
                    st.rerun()
        if st.session_state.consegna_radio:
            st.dataframe(pd.DataFrame([{k:v for k,v in c.items() if k not in ['FotoConsegnaBytes']} for c in st.session_state.consegna_radio]),use_container_width=True)

    elif cur=='Interventi Emergenza':
        hdr_form('INTERVENTI EMERGENZA - STATO SFONDO COLORATO - OPERATIVO ROSSO COMPLETATO VERDE - FATTIBILE')
        if not st.session_state.interventi_blindato:
            if st.session_state.emergenze:
                lista_em=[e.get('Comune','')+' - '+e.get('Tipo','') for e in st.session_state.emergenze]
                em=st.selectbox('EMERGENZA da blindare',['Nessuna']+lista_em,key='em_blind')
            else: em='Nessuna'
            if st.button('BLINDA INTERVENTI',type='primary',use_container_width=True):
                if em!='Nessuna':
                    st.session_state.interventi_emergenza_blindata=em
                    st.session_state.interventi_blindato=True
                    st.rerun()
        else:
            st.success(f"BLINDATO SU: {st.session_state.interventi_emergenza_blindata}")
            if st.button('SBLOCCA',type='primary',use_container_width=True):
                st.session_state.interventi_blindato=False
                st.session_state.interventi_emergenza_blindata=None
                st.rerun()
        if st.session_state.interventi_blindato:
            with st.form('form_int'):
                st.text_input('EMERGENZA BLINDATA',value=st.session_state.interventi_emergenza_blindata,disabled=True)
                c1,c2=st.columns(2)
                with c1:
                    comune_int=combo_comune('Comune Intervento *', 'int_comune')
                    via_int=combo_vie('Via Intervento *', comune_int, 'int_via')
                with c2:
                    stato_int=st.selectbox('STATO * - SFONDO COLORATO', ['Operativo','In Corso','Completato','Chiuso','In Stand By','Sospeso','Annullato','In Attesa'],key='stato_int')
                    bg_color, txt_color, label = get_stato_color(stato_int)
                    st.markdown(f'<div style="background:{bg_color};color:{txt_color};padding:15px;border-radius:8px;text-align:center;font-weight:bold;border:3px solid black;">STATO: {label}</div>',unsafe_allow_html=True)
                    priorita_int=st.selectbox('Priorita', ['Bassa','Media','Alta','Urgente','Critica'],key='prio_int')
                if st.session_state.icone:
                    lista_icone=[i['Nome'] for i in st.session_state.icone]
                    icona_int=st.selectbox('ICONA *',lista_icone,key='icona_int')
                    if icona_int:
                        ico_sel=next((i for i in st.session_state.icone if i['Nome']==icona_int),None)
                        if ico_sel and ico_sel.get('FileBytes'): st.image(ico_sel['FileBytes'],width=100,caption=icona_int)
                else: icona_int='Nessuna'
                azione_int=st.text_area('Azione Intervento *',height=120,key='az_int')
                if st.form_submit_button('SALVA INTERVENTO CON STATO SFONDO COLORATO',type='primary',use_container_width=True):
                    if comune_int and via_int and azione_int:
                        iv={'Data':str(date.today()),'Ora':str(datetime.now().time())[:5],'Comune':comune_int,'Via':via_int,'Stato':stato_int,'StatoColoreBg':bg_color,'StatoColoreTxt':txt_color,'Priorita':priorita_int,'Icona':icona_int if 'icona_int' in locals() else 'Nessuna','Azione':azione_int,'EmergenzaBlindata':st.session_state.interventi_emergenza_blindata}
                        st.session_state.interventi.append(iv)
                        st.success(f'Intervento {comune_int} Stato {stato_int} sfondo {bg_color} salvato!')
                        st.balloons()
                        st.rerun()
        if st.session_state.interventi:
            st.divider()
            st.markdown('<p style="font-family:Times New Roman;font-weight:bold;color:black;font-size:18px;">TABELLA INTERVENTI - STATO SFONDO COLORATO</p>',unsafe_allow_html=True)
            for idx,interv in enumerate(st.session_state.interventi):
                bg_color, txt_color, label = get_stato_color(interv.get('Stato',''))
                c1,c2,c3,c4,c5=st.columns([1,2,2,1,1])
                with c1:
                    icona_nome=interv.get('Icona','Nessuna')
                    st.markdown(f'<p style="font-family:Times New Roman;font-weight:bold;color:black;">ICONA {icona_nome}</p>',unsafe_allow_html=True)
                    if icona_nome!='Nessuna':
                        ico=next((i for i in st.session_state.icone if i['Nome']==icona_nome),None)
                        if ico and ico.get('FileBytes'): st.image(ico['FileBytes'],width=60)
                with c2:
                    st.markdown(f'<div style="background:{bg_color};color:{txt_color};padding:8px;border-radius:5px;border:2px solid black;"><p style="font-weight:bold;">STATO: {interv.get("Stato","")}</p><p>{interv.get("Comune","")} - {interv.get("Via","")}</p><p>{interv.get("Azione","")[:80]}</p></div>',unsafe_allow_html=True)
                with c3:
                    st.markdown(f'<p style="font-family:Times New Roman;font-weight:bold;color:black;">Priorita: {interv.get("Priorita","")}</p>',unsafe_allow_html=True)
                with c4:
                    st.markdown(f'<p style="font-family:Times New Roman;font-weight:bold;color:black;">{interv.get("Data","")}<br>{interv.get("Ora","")}</p>',unsafe_allow_html=True)
                with c5:
                    if st.button('Elimina',key=f'del_int_{idx}'):
                        st.session_state.interventi.pop(idx)
                        st.rerun()
            st.dataframe(pd.DataFrame(st.session_state.interventi),use_container_width=True)

    elif cur=='Tabella Interventi Emergenza':
        hdr_form('TABELLA INTERVENTI EMERGENZA - STATO SFONDO COLORATO - RIPRISTINATO - FORM RICHIESTO QUALCHE GIORNO FA')
        with st.form('tab_form'):
            c1,c2,c3=st.columns(3)
            with c1:
                data_tab=st.date_input('Data Intervento *',value=date.today(),key='tab_data')
                comune_tab=combo_comune('Comune *', 'tab_comune')
                via_tab=combo_vie('Via *', comune_tab, 'tab_via')
            with c2:
                tipo_tab=st.selectbox('Tipo *', ['Alluvione','Frana','Incendio','Terremoto','Neve','Ricerca Disperso','Soccorso','Viabilita','Prevenzione','Altro'],key='tab_tipo')
                priorita_tab=st.selectbox('Priorita *', ['Bassa','Media','Alta','Urgente','Critica'],key='tab_prio')
                stato_tab=st.selectbox('Stato * - SFONDO COLORATO', ['Operativo','In Corso','Completato','Chiuso','In Stand By','Sospeso','Annullato','In Attesa'],key='tab_stato')
                bg_color, txt_color, label = get_stato_color(stato_tab)
                st.markdown(f'<div style="background:{bg_color};color:{txt_color};padding:12px;border-radius:8px;text-align:center;font-weight:bold;border:2px solid black;">STATO: {label}</div>',unsafe_allow_html=True)
            with c3:
                if st.session_state.icone:
                    lista_icone=[i['Nome'] for i in st.session_state.icone]
                    icona_tab=st.selectbox('Icona *', lista_icone, key='tab_icona')
                    if icona_tab:
                        ico_sel=next((i for i in st.session_state.icone if i['Nome']==icona_tab),None)
                        if ico_sel and ico_sel.get('FileBytes'): st.image(ico_sel['FileBytes'],width=80,caption=icona_tab)
                else:
                    icona_tab='Nessuna'
                squadra_tab=st.selectbox('Squadra', ['Alpini Caronno','Squadra A','Squadra B','Squadra C'],key='tab_squadra')
            azione_tab=st.text_area('Azione Intervento *',height=100,key='tab_azione')
            if st.form_submit_button('SALVA IN TABELLA CON STATO SFONDO COLORATO',type='primary',use_container_width=True):
                if comune_tab and via_tab and azione_tab:
                    tab={'Data':str(data_tab),'Ora':str(datetime.now().time())[:5],'Comune':comune_tab,'Via':via_tab,'TipoIntervento':tipo_tab,'Priorita':priorita_tab,'Stato':stato_tab,'StatoColoreBg':bg_color,'StatoColoreTxt':txt_color,'Icona':icona_tab if 'icona_tab' in locals() else 'Nessuna','Squadra':squadra_tab,'Azione':azione_tab,'DataInserimento':str(date.today())}
                    st.session_state.tabella_interventi.append(tab)
                    st.success(f'Tabella Interventi - {comune_tab} Stato {stato_tab} sfondo {bg_color} salvato!')
                    st.balloons()
                    st.rerun()
        if st.session_state.tabella_interventi:
            st.divider()
            st.markdown('<p style="font-family:Times New Roman;font-weight:bold;color:black;font-size:18px;">TABELLA URGENTI - STATO SFONDO COLORATO - ICONA VISIBILE</p>',unsafe_allow_html=True)
            for idx,interv in enumerate(st.session_state.tabella_interventi):
                bg_color, txt_color, label = get_stato_color(interv.get('Stato',''))
                c1,c2,c3,c4,c5=st.columns([1,2,2,2,1])
                with c1:
                    st.markdown(f'<p style="font-family:Times New Roman;font-weight:bold;color:black;">ICONA {interv.get("Icona","")}</p>',unsafe_allow_html=True)
                    if interv.get('Icona','Nessuna')!='Nessuna':
                        ico=next((i for i in st.session_state.icone if i['Nome']==interv.get('Icona')),None)
                        if ico and ico.get('FileBytes'): st.image(ico['FileBytes'],width=60)
                with c2:
                    st.markdown(f'<div style="background:{bg_color};color:{txt_color};padding:8px;border-radius:5px;border:2px solid black;"><p style="font-weight:bold;">STATO: {interv.get("Stato","")}</p><p>{interv.get("Comune","")} - {interv.get("Via","")}</p><p>{interv.get("Azione","")[:80]}</p></div>',unsafe_allow_html=True)
                with c3:
                    st.markdown(f'<p style="font-family:Times New Roman;font-weight:bold;color:black;">Tipo: {interv.get("TipoIntervento","")}<br>Priorita: {interv.get("Priorita","")}<br>Squadra: {interv.get("Squadra","")}</p>',unsafe_allow_html=True)
                with c4:
                    st.markdown(f'<p style="font-family:Times New Roman;font-weight:bold;color:black;">{interv.get("Data","")} {interv.get("Ora","")}</p>',unsafe_allow_html=True)
                with c5:
                    if st.button('Elimina',key=f'del_tab_{idx}'):
                        st.session_state.tabella_interventi.pop(idx)
                        st.rerun()
            st.dataframe(pd.DataFrame(st.session_state.tabella_interventi),use_container_width=True)
            c1,c2=st.columns(2)
            c1.download_button('Excel Tabella Stato Colorato',to_excel(pd.DataFrame(st.session_state.tabella_interventi)),file_name='tabella_stato_colorato.xlsx',mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',use_container_width=True)
            pdf=to_pdf(pd.DataFrame(st.session_state.tabella_interventi),'Tabella Interventi Stato Colorato')
            if pdf: c2.download_button('PDF Tabella',pdf,file_name='tabella_stato_colorato.pdf',mime='application/pdf',use_container_width=True)

    elif cur=='Backup':
        hdr_form('BACKUP - CON NOME FORM DOVE CARICARE + VA SU FORM ASSEGNATO + EXPORT SU BACKUP - SENZA ESPORTA - STATO COLORATO')
        datasets={'Volontari':st.session_state.volontari,'DB Radio':st.session_state.radio_db,'Consegna Radio':st.session_state.consegna_radio,'Interventi Emergenza':st.session_state.interventi,'Tabella Interventi Emergenza':st.session_state.tabella_interventi,'Postazioni':st.session_state.postazioni,'Chat':st.session_state.chat}
        totale=sum([len(v) for v in datasets.values() if v])
        st.info(f'Totale: {totale} - con Stato Sfondo Colorato')
        c1,c2=st.columns(2)
        with c1:
            if any(datasets.values()):
                st.download_button('EXPORT TOTALE EXCEL - CON STATO COLORATO - SU BACKUP',to_excel_multi(datasets),file_name=f'backup_STATO_COLORATO_{date.today()}.xlsx',mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',use_container_width=True,type='primary')
        with c2:
            backup_json=json.dumps({k:v for k,v in datasets.items()},default=str,indent=2)
            st.download_button('BACKUP JSON COMPLETO',backup_json,file_name=f'backup_JSON_{date.today()}.json',mime='application/json',use_container_width=True)
        st.divider()
        form_mapping = [
            ('volontari','Volontari (con foto)','Volontari'),
            ('radio_db','DB Radio','DB Radio'),
            ('consegna_radio','Consegna Radio','Consegna Radio'),
            ('interventi','Interventi Emergenza','Interventi Emergenza'),
            ('tabella_interventi','Tabella Interventi Emergenza - STATO COLORATO','Tabella Interventi Emergenza'),
            ('postazioni','Postazioni Mappa','Mappa Avanzata'),
            ('chat','Chat','Chat')
        ]
        for key, titolo_menu, nome_form in form_mapping:
            st.markdown(f'<div style="border:2px solid {VERDE};padding:10px;border-radius:8px;"><p style="font-family:Times New Roman;font-weight:bold;color:black;">📋 FORM: {titolo_menu} - NOME FORM: {nome_form} - {len(st.session_state[key])} record</p></div>',unsafe_allow_html=True)
            c1,c2,c3,c4=st.columns(4)
            with c1:
                if st.session_state[key]:
                    st.download_button(f'📥 Excel {nome_form} - EXPORT SU BACKUP', to_excel(pd.DataFrame(st.session_state[key])), file_name=f"{key}_{date.today()}.xlsx", mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', key=f'excel_{key}', use_container_width=True)
            with c2:
                up=st.file_uploader(f'📤 Carica per FORM: {nome_form} - NOME FORM DOVE CARICARE', type=['xlsx'], key=f'up_{key}')
                if up:
                    try:
                        df_imp=pd.read_excel(up)
                        if st.button(f'✅ Importa {len(df_imp)} in FORM: {nome_form} - VA SU {titolo_menu}', key=f'imp_{key}'):
                            for _,row in df_imp.iterrows():
                                st.session_state[key].append(row.to_dict())
                            st.success(f'Importati in {nome_form} - Vado su {titolo_menu}')
                            st.session_state.menu=titolo_menu
                            st.rerun()
                    except Exception as e: st.error(f'Errore: {e}')
            with c3:
                if st.session_state[key]:
                    if st.button(f'👁️ Vai a FORM: {titolo_menu}', key=f'goto_{key}'):
                        st.session_state.menu=titolo_menu
                        st.rerun()
            with c4:
                if st.session_state[key]:
                    if st.button(f'🗑️ Svuota {nome_form}', key=f'clear_{key}'):
                        st.session_state[key]=[]
                        st.rerun()
            st.divider()
