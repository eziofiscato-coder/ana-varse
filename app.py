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

COMUNI_ITALIA = ["Varese","Milano","Roma","Torino","Napoli","Busto Arsizio","Gallarate","Saronno","Tradate","Somma Lombardo","Cassano Magnago","Malnate","Lonate Pozzolo","Sesto Calende","Gavirate","Luino","Laveno-Mombello","Besozzo","Caronno Pertusella","Caronno Varesino","Albizzate","Angera","Arcisate","Azzate","Bardello","Besano","Besnate","Biandronno","Bisuschio","Bodio Lomnago","Brebbia","Brenta","Brinzio","Brusimpiano","Buguggiate","Cadegliano-Viconago","Cairate","Cantello","Caravate","Cardano al Campo","Carnago","Casale Litta","Casalzuigno","Casciago","Casorate Sempione","Cassano Valcuvia","Castellanza","Castelseprio","Castiglione Olona","Castronno","Cavaria con Premezzo","Cazzago Brabbia","Cislago","Cittiglio","Clivio","Cocquio-Trevisago","Comabbio","Comerio","Cugliate-Fabiasco","Cunardo","Cuvio","Daverio","Dumenza","Fagnano Olona","Ferno","Gazzada Schianno","Gemonio","Gerenzano","Germignaga","Golasecca","Gorla Maggiore","Gorla Minore","Gornate-Olona","Inarzo","Induno Olona","Ispra","Jerago con Orago","Lavena Ponte Tresa","Leggiuno","Lonate Ceppino","Lozza","Maccagno con Pino e Veddasca","Malgesso","Marzio","Mercallo","Mesenzana","Monvalle","Morazzone","Mornago","Oggiona con Santo Stefano","Olgiate Olona","Origgio","Orino","Porto Ceresio","Porto Valtravaglia","Rancio Valcuvia","Saltrio","Samarate","Solbiate Arno","Solbiate Olona","Sumirago","Taino","Ternate","Travedona Monate","Uboldo","Valganna","Varano Borghi","Vedano Olona","Venegono Inferiore","Venegono Superiore","Vergiate","Viggiu","Bergamo","Brescia","Como","Lecco","Roma","Torino","Napoli","Genova","Bologna","Firenze","Palermo","Venezia","Verona","Padova","Trieste","Bari","Catania","Cagliari","Perugia","Ancona","Trento","Bolzano","Aosta"]

def get_comuni():
    try:
        r=requests.get("https://raw.githubusercontent.com/matteocontrini/comuni-json/master/comuni.json",timeout=5)
        if r.status_code==200:
            return sorted([c['nome'] for c in r.json()])
    except:
        pass
    return sorted(list(set(COMUNI_ITALIA)))

def get_vie(comune):
    try:
        q=f'[out:json][timeout:10]; area["name"="{comune}"]["admin_level"~"6|7|8"]->.a; (way["highway"](area.a);); out 200;'
        r=requests.post("https://overpass-api.de/api/interpreter",data=q,timeout=10)
        if r.status_code==200:
            vie=[]
            for el in r.json().get('elements',[]):
                n=el.get('tags',{}).get('name')
                if n and n not in vie:
                    vie.append(n)
            return sorted(vie)[:150]
    except:
        pass
    return ["Via Roma","Via Garibaldi","Via Milano","Via Verdi","Via Dante","Via Manzoni","Via Matteotti","Piazza Liberta","Via IV Novembre","Via San Giovanni"]

def hdr():
    c1,c2=st.columns([1,5])
    with c1:
        try: st.image('logo.png',width=110)
        except: st.markdown('**ANA**')
    with c2:
        st.markdown(f'<div style="background:{VERDE};padding:12px;border-radius:8px;color:white;font-weight:bold;font-family:Times New Roman;">NUCLEO PROT CIVILE ANA VARESE - FONT NERO TIMES BOLD + ICONA TABELLA + CHAT - 950+</div>',unsafe_allow_html=True)

def hdr_form(t): st.markdown(f'<h2 style="font-family:Times New Roman;color:black;font-weight:bold;">{t}</h2>',unsafe_allow_html=True)
def to_excel(df):
    out=BytesIO()
    cols=[c for c in df.columns if c not in ['Foto','FotoBytes','FileBytes']]
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
                    cols=[c for c in df.columns if c not in ['Foto','FotoBytes','FileBytes']]
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

for k in ['page','logged','menu','volontari','radio_db','eventi','emergenze','checkin','icone','postazioni','last_clicked','temp_markers','brogliaccio','mezzi','attrezzature','map_fullscreen','vol_form_data','alias_radio','brog_evento_blindato','brog_emergenza_blindata','brog_blindato','check_evento_blindato','check_emergenza_blindata','check_blindato','interventi','interventi_emergenza_blindata','interventi_blindato','chat']:
    if k not in st.session_state:
        if k=='page': st.session_state[k]='entra'
        elif k=='logged': st.session_state[k]=False
        elif k=='menu': st.session_state[k]='Dashboard'
        elif k in ['map_fullscreen','brog_blindato','check_blindato','interventi_blindato']: st.session_state[k]=False
        elif k=='vol_form_data': st.session_state[k]={}
        elif k in ['brog_evento_blindato','brog_emergenza_blindata','check_evento_blindato','check_emergenza_blindata','interventi_emergenza_blindata','last_clicked']: st.session_state[k]=None
        elif k in ['temp_markers','chat']: st.session_state[k]=[]
        else: st.session_state[k]=[]

if st.session_state.page=='entra':
    hdr()
    c1,c2,c3=st.columns([1,2,1])
    with c2:
        try: st.image('copertina.png',width=350)
        except: pass
        st.markdown(f'<h2 style="text-align:center;font-family:Times New Roman;font-weight:bold;color:black;">GESTIONALE 950+ - COME PRIMA - FUNZIONA BENE</h2>',unsafe_allow_html=True)
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
    menu_base=['Dashboard','Volontari (con foto)','DB Radio','Alias Radio','Brogliaccio','Eventi','Emergenze','Check-in','Interventi Emergenza','Mezzi','Attrezzature','Mappa Avanzata','Libreria Icone','Chat','Backup','Esporta']
    with st.sidebar:
        try: st.image('logo.png',width=120)
        except: pass
        st.markdown('<p style="font-family:Times New Roman;font-weight:bold;color:black;">MENU 950+ COME PRIMA - FUNZIONA BENE</p>',unsafe_allow_html=True)
        try: idx=menu_base.index(st.session_state.menu)
        except: idx=0
        m=st.radio('Scegli form:',menu_base,index=idx)
        st.session_state.menu=m
        if st.button('Logout',use_container_width=True):
            st.session_state.page='entra'
            st.rerun()
    cur=st.session_state.menu

    if cur=='Dashboard':
        hdr_form('Dashboard - 950+ - COME PRIMA - FUNZIONA BENE - TUTTI TASTI')
        c1,c2,c3,c4=st.columns(4)
        c1.metric('Volontari',len(st.session_state.volontari))
        c2.metric('Radio',len(st.session_state.radio_db))
        c3.metric('Postazioni',len(st.session_state.postazioni))
        c4.metric('Interventi',len(st.session_state.interventi))
        c1b,c2b,c3b,c4b=st.columns(4)
        c1b.metric('Chat',len(st.session_state.chat))
        c2b.metric('Brogliaccio',len(st.session_state.brogliaccio))
        c3b.metric('Emergenze',len(st.session_state.emergenze))
        c4b.metric('Icone',len(st.session_state.icone))
        st.divider()
        r1=st.columns(4)
        with r1[0]:
            if st.button('VOLONTARI',key='btn_vol',use_container_width=True,type='primary'):
                st.session_state.menu='Volontari (con foto)'
                st.rerun()
        with r1[1]:
            if st.button('DB RADIO',key='btn_radio',use_container_width=True,type='primary'):
                st.session_state.menu='DB Radio'
                st.rerun()
        with r1[2]:
            if st.button('MAPPA',key='btn_mappa',use_container_width=True,type='primary'):
                st.session_state.menu='Mappa Avanzata'
                st.rerun()
        with r1[3]:
            if st.button('INTERVENTI + ICONA',key='btn_interv',use_container_width=True,type='primary'):
                st.session_state.menu='Interventi Emergenza'
                st.rerun()
        r2=st.columns(4)
        with r2[0]:
            if st.button('CHAT',key='btn_chat',use_container_width=True,type='primary'):
                st.session_state.menu='Chat'
                st.rerun()
        with r2[1]:
            if st.button('BACKUP IMPORT EXPORT',key='btn_backup',use_container_width=True,type='primary'):
                st.session_state.menu='Backup'
                st.rerun()
        with r2[2]:
            if st.button('LIBRERIA ICONE',key='btn_icone',use_container_width=True,type='primary'):
                st.session_state.menu='Libreria Icone'
                st.rerun()
        with r2[3]:
            if st.button('EVENTI',key='btn_eventi',use_container_width=True,type='primary'):
                st.session_state.menu='Eventi'
                st.rerun()
        r3=st.columns(4)
        with r3[0]:
            if st.button('EMERGENZE',key='btn_emerg',use_container_width=True,type='primary'):
                st.session_state.menu='Emergenze'
                st.rerun()
        with r3[1]:
            if st.button('BROGLIACCIO',key='btn_brog',use_container_width=True,type='primary'):
                st.session_state.menu='Brogliaccio'
                st.rerun()
        with r3[2]:
            if st.button('CHECK-IN',key='btn_check',use_container_width=True,type='primary'):
                st.session_state.menu='Check-in'
                st.rerun()
        with r3[3]:
            if st.button('ALIAS RADIO',key='btn_alias',use_container_width=True,type='primary'):
                st.session_state.menu='Alias Radio'
                st.rerun()

    elif cur=='Volontari (con foto)':
        hdr_form('VOLONTARI - COMUNE COMBO ITALIA - FONT NERO BOLD TIMES - TABELLA DOPO SALVATAGGIO')
        t1,t2,t3,t4,t5=st.tabs(['1.Anagrafica COMUNE COMBO','2.Contatti','3.Ruolo','4.Foto e Salva','5.Elenco + Tabella'])
        with t1:
            with st.form('vol_anag'):
                nome=st.text_input('Nome *',key='vol_nome')
                cognome=st.text_input('Cognome *',key='vol_cognome')
                comune=combo_comune('Comune Residenza *', 'vol_comune', st.session_state.vol_form_data.get('Comune','Varese'))
                if st.form_submit_button('Salva Anagrafica',type='primary',use_container_width=True):
                    if nome and cognome and comune:
                        st.session_state.vol_form_data['Nome']=nome
                        st.session_state.vol_form_data['Cognome']=cognome
                        st.session_state.vol_form_data['Comune']=comune
                        st.success(f'Anagrafica {comune} salvata')
        with t4:
            foto=st.file_uploader('Carica Foto *',type=['png','jpg','jpeg'],key='vol_foto')
            if foto: st.image(foto,width=200)
            with st.form('vol_foto_form'):
                if st.form_submit_button('SALVA VOLONTARIO COMPLETO',type='primary',use_container_width=True):
                    if not st.session_state.vol_form_data.get('Nome'):
                        st.error('Compila prima Tab 1')
                    else:
                        v={'Nome':st.session_state.vol_form_data.get('Nome',''),'Cognome':st.session_state.vol_form_data.get('Cognome',''),'Comune':st.session_state.vol_form_data.get('Comune',''),'FotoBytes':foto.getvalue() if foto else None,'Data':str(date.today())}
                        st.session_state.volontari.append(v)
                        st.session_state.vol_form_data={}
                        st.success(f"Volontario {v['Nome']} salvato! Vai in Tab 5 per tabella")
                        st.balloons()
                        st.rerun()
        with t5:
            st.markdown('<p style="font-family:Times New Roman;font-weight:bold;color:black;">TABELLA VOLONTARI DOPO SALVATAGGIO - FIX</p>',unsafe_allow_html=True)
            if st.session_state.volontari:
                lista=[]
                for vol in st.session_state.volontari:
                    lista.append({'Nome':vol.get('Nome',''),'Cognome':vol.get('Cognome',''),'Comune':vol.get('Comune',''),'Foto':'SI' if vol.get('FotoBytes') else 'NO','Data':vol.get('Data','')})
                st.dataframe(pd.DataFrame(lista),use_container_width=True,hide_index=True)
                c1,c2=st.columns(2)
                c1.download_button('Excel',to_excel(pd.DataFrame(lista)),file_name='volontari.xlsx',mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',use_container_width=True)
                pdf=to_pdf(pd.DataFrame(lista),'Volontari')
                if pdf: c2.download_button('PDF',pdf,file_name='volontari.pdf',mime='application/pdf',use_container_width=True)
            else:
                st.warning('Nessun volontario')

    elif cur=='Interventi Emergenza':
        hdr_form('INTERVENTI EMERGENZA - COMUNE COMBO + VIA + ICONA - TABELLA CON ICONA VISIBILE - FONT NERO BOLD TIMES')
        if not st.session_state.interventi_blindato:
            if st.session_state.emergenze:
                lista_em=[e.get('Comune','')+' - '+e.get('Tipo','') for e in st.session_state.emergenze]
                em=st.selectbox('EMERGENZA da blindare',['Nessuna']+lista_em,key='em_blind')
            else: em='Nessuna'
            if st.button('BLINDA INTERVENTI SU EMERGENZA',type='primary',use_container_width=True):
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
                    comune_int=combo_comune('Comune Intervento * - COMBO ITALIA', 'int_comune')
                    via_int=combo_vie('Via Intervento * - VIE DEL COMUNE', comune_int, 'int_via')
                with c2:
                    stato_int=st.selectbox('STATO *', ['Operativo','In Stand By','Chiuso','In Corso','Completato'],key='stato_int')
                    priorita_int=st.selectbox('Priorita - URGENTE per tabella urgenti', ['Bassa','Media','Alta','Urgente'],key='prio_int')
                st.markdown('<p style="font-family:Times New Roman;font-weight:bold;color:black;">ICONA LIBRERIA AGGANCIATA</p>',unsafe_allow_html=True)
                if st.session_state.icone:
                    lista_icone=[i['Nome'] for i in st.session_state.icone]
                    icona_int=st.selectbox('ICONA * - DA LIBRERIA - AGGANCIATA',lista_icone,key='icona_int_agg')
                    if icona_int:
                        ico_sel=next((i for i in st.session_state.icone if i['Nome']==icona_int),None)
                        if ico_sel and ico_sel.get('FileBytes'):
                            c1,c2=st.columns([1,3])
                            with c1: st.image(ico_sel['FileBytes'],width=100,caption=icona_int)
                            with c2: st.success(f'Icona {icona_int} agganciata')
                else:
                    icona_int='Nessuna'
                    st.warning('Carica icone in Libreria Icone')
                azione_int=st.text_area('Azione Intervento * - FONT NERO BOLD TIMES',height=120,key='az_int')
                if st.form_submit_button('SALVA INTERVENTO CON ICONA AGGANCIATA',use_container_width=True,type='primary'):
                    if comune_int and via_int and azione_int:
                        iv={'Data':str(date.today()),'Ora':str(datetime.now().time())[:5],'Comune':comune_int,'Via':via_int,'Stato':stato_int,'Priorita':priorita_int,'Icona':icona_int if 'icona_int' in locals() else 'Nessuna','Azione':azione_int,'EmergenzaBlindata':st.session_state.interventi_emergenza_blindata}
                        st.session_state.interventi.append(iv)
                        st.success(f'Intervento {comune_int} - {via_int} icona {iv["Icona"]} salvato!')
                        st.balloons()
                        st.rerun()
        if st.session_state.interventi:
            st.divider()
            st.markdown('<p style="font-family:Times New Roman;font-weight:bold;color:black;font-size:18px;">TABELLA INTERVENTI URGENTI - COLONNA ICONA ASSEGNATA VISIBILE</p>',unsafe_allow_html=True)
            for idx,interv in enumerate(st.session_state.interventi):
                is_urg=interv.get('Priorita','')=='Urgente'
                bg="background-color:#ffcccc;" if is_urg else ""
                c1,c2,c3,c4,c5=st.columns([1,2,2,1,1])
                with c1:
                    icona_nome=interv.get('Icona','Nessuna')
                    st.markdown(f'<p style="font-family:Times New Roman;font-weight:bold;color:black;">ICONA<br>{icona_nome}</p>',unsafe_allow_html=True)
                    if icona_nome!='Nessuna':
                        ico=next((i for i in st.session_state.icone if i['Nome']==icona_nome),None)
                        if ico and ico.get('FileBytes'): st.image(ico['FileBytes'],width=60)
                with c2:
                    st.markdown(f'<div style="{bg}"><p style="font-family:Times New Roman;font-weight:bold;color:black;">{interv.get("Comune","")} - {interv.get("Via","")}</p><p style="font-family:Times New Roman;font-weight:bold;color:black;">{interv.get("Azione","")[:80]}</p></div>',unsafe_allow_html=True)
                with c3:
                    st.markdown(f'<p style="font-family:Times New Roman;font-weight:bold;color:black;">Stato: {interv.get("Stato","")}<br>Priorita: {interv.get("Priorita","")}</p>',unsafe_allow_html=True)
                with c4:
                    st.markdown(f'<p style="font-family:Times New Roman;font-weight:bold;color:black;">{interv.get("Data","")}<br>{interv.get("Ora","")}</p>',unsafe_allow_html=True)
                with c5:
                    if st.button('Elimina',key=f'del_int_{idx}'):
                        st.session_state.interventi.pop(idx)
                        st.rerun()
            st.dataframe(pd.DataFrame(st.session_state.interventi),use_container_width=True)

    elif cur=='Chat':
        hdr_form('CHAT - FORM CHAT - FONT NERO BOLD TIMES - RIPRISTINATO')
        with st.form('chat_form'):
            c1,c2=st.columns(2)
            with c1:
                if st.session_state.alias_radio:
                    lista_alias=[a.get('NomeAlias','') for a in st.session_state.alias_radio]
                    mitt_chat=st.selectbox('Mittente * - da Alias Radio',lista_alias,key='chat_mitt')
                    dest_chat=st.selectbox('Destinatario *',lista_alias,key='chat_dest')
                else:
                    mitt_chat=st.text_input('Mittente *',key='chat_mitt_txt')
                    dest_chat=st.text_input('Destinatario *',key='chat_dest_txt')
            with c2:
                canale_chat=st.text_input('Canale Radio',value='Canale 1',key='chat_can')
                priorita_chat=st.selectbox('Priorita', ['Normale','Alta','Urgenza'],key='chat_prio')
            msg_chat=st.text_area('Messaggio * - FONT NERO BOLD TIMES',height=100,key='chat_msg')
            if st.form_submit_button('Invia Messaggio Chat',type='primary',use_container_width=True):
                if mitt_chat and dest_chat and msg_chat:
                    chat_msg={'Data':str(date.today()),'Ora':datetime.now().strftime('%H:%M:%S'),'Mittente':mitt_chat,'Destinatario':dest_chat,'Canale':canale_chat,'Priorita':priorita_chat,'Messaggio':msg_chat}
                    st.session_state.chat.append(chat_msg)
                    st.success(f'Chat {mitt_chat} -> {dest_chat} inviato!')
                    st.rerun()
        if st.session_state.chat:
            st.divider()
            for idx,msg in enumerate(reversed(st.session_state.chat)):
                c1,c2,c3=st.columns([2,6,2])
                with c1:
                    st.markdown(f'<p style="font-family:Times New Roman;font-weight:bold;color:black;">{msg.get("Data","")} {msg.get("Ora","")}<br>{msg.get("Mittente","")} -> {msg.get("Destinatario","")}</p>',unsafe_allow_html=True)
                with c2:
                    st.markdown(f'<p style="font-family:Times New Roman;font-weight:bold;color:black;background:#e0ffe0;padding:8px;border-radius:5px;">{msg.get("Messaggio","")}</p>',unsafe_allow_html=True)
                with c3:
                    if st.button('Elimina',key=f'del_chat_{idx}'):
                        st.session_state.chat.pop(len(st.session_state.chat)-1-idx)
                        st.rerun()
            st.dataframe(pd.DataFrame(st.session_state.chat),use_container_width=True)

    elif cur=='Mappa Avanzata':
        hdr_form('MAPPA AVANZATA - COMUNI COMBO + VIE + ICONA - CLICK DIRETTO SU MASCHERA + RIEPILOGO - FONT NERO BOLD TIMES')
        c1,c2,c3=st.columns([2,2,1])
        with c1: map_type=st.selectbox('Tipo Mappa',['OpenStreetMap','Google Map','Google Satellite'],index=0,key='map_type')
        with c2: icona_sel=st.selectbox('Icona Marker',['Nessuna']+[i['Nome'] for i in st.session_state.icone] if st.session_state.icone else ['Nessuna'],key='map_icona')
        with c3:
            lab='Riduci' if st.session_state.map_fullscreen else 'Espandi'
            if st.button(lab,key='exp',use_container_width=True,type='primary'):
                st.session_state.map_fullscreen=not st.session_state.map_fullscreen
                st.rerun()
        h1=800 if st.session_state.map_fullscreen else 500
        try:
            import folium
            from streamlit_folium import st_folium
            from folium.plugins import Fullscreen
            def rev_geo(lat,lon):
                try:
                    url=f'https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=18&addressdetails=1'
                    r=requests.get(url,headers={'User-Agent':'ANA'},timeout=5)
                    if r.status_code==200:
                        a=r.json().get('address',{})
                        c=a.get('city') or a.get('town') or a.get('village') or ''
                        v=a.get('road') or ''
                        return c,v
                except: pass
                return '',''
            lat_c,lon_c=45.65,8.79
            if st.session_state.postazioni:
                lat_c=sum([p['Lat'] for p in st.session_state.postazioni])/len(st.session_state.postazioni)
                lon_c=sum([p['Log'] for p in st.session_state.postazioni])/len(st.session_state.postazioni)
            mm=folium.Map(location=[lat_c,lon_c],zoom_start=12,tiles=None)
            if map_type=='OpenStreetMap': folium.TileLayer('openstreetmap').add_to(mm)
            elif map_type=='Google Map': folium.TileLayer(tiles='https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',attr='Google').add_to(mm)
            else: folium.TileLayer(tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',attr='Google').add_to(mm)
            Fullscreen().add_to(mm)
            for p in st.session_state.postazioni:
                popup=f"<b>{p['Nome']}</b><br>Comune: {p.get('Comune','')}<br>Via: {p.get('Via','')}"
                use_path=None
                if p.get('Icona','Nessuna')!='Nessuna':
                    ico=next((i for i in st.session_state.icone if i['Nome']==p.get('Icona')),None)
                    if ico and ico.get('FileBytes'): use_path=salva_icona_temp(ico['FileBytes'],p.get('Icona'))
                if use_path: folium.Marker([p['Lat'],p['Log']],popup=popup,icon=folium.CustomIcon(use_path,icon_size=(40,40))).add_to(mm)
                else: folium.Marker([p['Lat'],p['Log']],popup=popup,icon=folium.Icon(color='green')).add_to(mm)
            out=st_folium(mm,width=1400,height=h1,use_container_width=True,returned_objects=['last_clicked'],key='map_main')
            if out and out.get('last_clicked'):
                lat_c=out['last_clicked']['lat']
                lon_c=out['last_clicked']['lng']
                com,via=rev_geo(lat_c,lon_c)
                st.session_state.last_clicked={'lat':lat_c,'lon':lon_c,'icona':icona_sel,'comune':com,'via':via}
                st.success(f"Click: {lat_c:.6f},{lon_c:.6f} -> {com} {via} -> DIRETTO IN MASCHERA SOTTO")
                st.rerun()
        except Exception as e: st.error(f"Errore mappa: {e}")
        last=st.session_state.last_clicked
        if last: st.success(f"ULTIMO CLICK: {last['lat']:.6f} {last['lon']:.6f} | {last.get('comune','')} {last.get('via','')}")
        st.divider()
        st.markdown('<p style="font-family:Times New Roman;font-weight:bold;color:black;">MASCHERA SOTTO MAPPA - COMUNE COMBO + VIA COMBO + ICONA - FONT NERO BOLD TIMES - DIRETTO DA CLICK</p>',unsafe_allow_html=True)
        with st.form('form_post'):
            c1,c2=st.columns(2)
            with c1:
                nome_p=st.text_input('Nome Postazione * - FONT NERO BOLD TIMES',key='nome_post')
                comune_p=combo_comune('Comune * - COMBO ITALIA', 'comune_post', last.get('comune','') if last else '')
                via_p=combo_vie('Via - VIE COMUNE', comune_p, 'via_post', last.get('via','') if last else '')
            with c2:
                lat_p=st.text_input('Latitudine *',value=str(last['lat']) if last else '',key='lat_post')
                lon_p=st.text_input('Longitudine *',value=str(last['lon']) if last else '',key='lon_post')
                lista_icone=['Nessuna']+[i['Nome'] for i in st.session_state.icone] if st.session_state.icone else ['Nessuna']
                icona_p=st.selectbox('Icona Postazione',lista_icone,key='icona_post')
            note_p=st.text_input('Note - FONT NERO BOLD TIMES',key='note_post')
            if st.form_submit_button('Salva Postazione - FONT NERO BOLD TIMES',type='primary',use_container_width=True):
                if nome_p and comune_p and lat_p and lon_p:
                    try:
                        np={'Nome':nome_p,'Comune':comune_p,'Via':via_p,'Icona':icona_p,'Lat':float(lat_p.replace(',','.')), 'Log':float(lon_p.replace(',','.')), 'Note':note_p,'Data':str(date.today())}
                        st.session_state.postazioni.append(np)
                        st.session_state.last_clicked=None
                        st.success(f'Postazione {nome_p} salvata!')
                        st.rerun()
                    except Exception as e: st.error(f'Errore: {e}')
        st.divider()
        st.markdown('<p style="font-family:Times New Roman;font-weight:bold;color:black;">MAPPA RIEPILOGO SOTTO MASCHERA - TUTTE POSTAZIONI</p>',unsafe_allow_html=True)
        if st.session_state.postazioni:
            try:
                import folium
                from streamlit_folium import st_folium as st_folium2
                mm2=folium.Map(location=[45.65,8.79],zoom_start=11,tiles='openstreetmap')
                for p in st.session_state.postazioni:
                    popup=f"<b>{p['Nome']}</b><br>Comune: {p.get('Comune','')}<br>Via: {p.get('Via','')}<br>Icona: {p.get('Icona','Nessuna')}"
                    use_path=None
                    if p.get('Icona','Nessuna')!='Nessuna':
                        ico=next((i for i in st.session_state.icone if i['Nome']==p.get('Icona')),None)
                        if ico and ico.get('FileBytes'): use_path=salva_icona_temp(ico['FileBytes'],p.get('Icona'))
                    if use_path: folium.Marker([p['Lat'],p['Log']],popup=popup,icon=folium.CustomIcon(use_path,icon_size=(35,35))).add_to(mm2)
                    else: folium.Marker([p['Lat'],p['Log']],popup=popup,icon=folium.Icon(color='red')).add_to(mm2)
                st_folium2(mm2,width=1400,height=400,use_container_width=True,key='map_riep')
                st.dataframe(pd.DataFrame(st.session_state.postazioni),use_container_width=True)
            except Exception as e: st.error(f"Errore riepilogo: {e}")

    elif cur=='Libreria Icone':
        hdr_form('LIBRERIA ICONE - FONT NERO BOLD TIMES - AGGANCIATA IN INTERVENTI')
        with st.form('icone_form'):
            nome_i=st.text_input('Nome icona * - FONT NERO BOLD TIMES')
            file_i=st.file_uploader('Carica PNG/JPG *',type=['png','jpg','jpeg'])
            if file_i: st.image(file_i,width=120)
            if st.form_submit_button('Salva Icona',type='primary',use_container_width=True):
                if nome_i and file_i:
                    st.session_state.icone.append({'Nome':nome_i,'FileName':file_i.name,'FileBytes':file_i.getvalue()})
                    st.success(f'Icona {nome_i} caricata!')
                    st.balloons()
        if st.session_state.icone:
            cols=st.columns(4)
            for idx,ico in enumerate(st.session_state.icone):
                col=cols[idx%4]
                with col:
                    st.markdown(f'<p style="font-family:Times New Roman;font-weight:bold;color:black;">{ico["Nome"]}</p>',unsafe_allow_html=True)
                    if ico.get('FileBytes'): st.image(ico['FileBytes'],width=80)
                    if st.button('Elimina',key=f'del_{idx}'):
                        st.session_state.icone.pop(idx)
                        st.rerun()

    elif cur=='Backup':
        hdr_form('BACKUP - FONT NERO BOLD TIMES + COMUNI + ICONA + CHAT - IMPORT EXPORT TUTTI I FORM')
        datasets={'Volontari':st.session_state.volontari,'Radio':st.session_state.radio_db,'Eventi':st.session_state.eventi,'Emergenze':st.session_state.emergenze,'Interventi':st.session_state.interventi,'Postazioni':st.session_state.postazioni,'Chat':st.session_state.chat,'Brogliaccio':st.session_state.brogliaccio}
        totale=sum([len(v) for v in datasets.values() if v])
        st.info(f'Totale record: {totale}')
        c1,c2=st.columns(2)
        with c1:
            if any(datasets.values()):
                st.download_button('EXPORT TOTALE EXCEL - TUTTI I FORM',to_excel_multi(datasets),file_name=f'backup_TUTTO_{date.today()}.xlsx',mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',use_container_width=True,type='primary')
        with c2:
            backup_json=json.dumps({k:v for k,v in datasets.items()},default=str,indent=2)
            st.download_button('BACKUP JSON COMPLETO',backup_json,file_name=f'backup_JSON_{date.today()}.json',mime='application/json',use_container_width=True)
        st.divider()
        st.markdown('<p style="font-family:Times New Roman;font-weight:bold;color:black;">IMPORT TOTALE - RIPRISTINA TUTTI I DATI</p>',unsafe_allow_html=True)
        up_tot=st.file_uploader('Carica Backup Excel Totale',type=['xlsx'],key='up_backup_tot')
        if up_tot:
            try:
                xls=pd.ExcelFile(up_tot)
                st.write(f'Fogli: {xls.sheet_names}')
                if st.button('IMPORTA TUTTO',type='primary',use_container_width=True):
                    for sheet in xls.sheet_names:
                        df=pd.read_excel(xls,sheet_name=sheet)
                        records=df.to_dict('records')
                        if sheet=='Volontari': st.session_state.volontari=records
                        elif sheet=='Radio': st.session_state.radio_db=records
                        elif sheet=='Eventi': st.session_state.eventi=records
                        elif sheet=='Emergenze': st.session_state.emergenze=records
                        elif sheet=='Interventi': st.session_state.interventi=records
                        elif sheet=='Postazioni': st.session_state.postazioni=records
                        elif sheet=='Chat': st.session_state.chat=records
                        elif sheet=='Brogliaccio': st.session_state.brogliaccio=records
                    st.success('Import totale completato!')
                    st.rerun()
            except Exception as e: st.error(f'Errore import: {e}')
