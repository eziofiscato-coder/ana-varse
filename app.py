import streamlit as st
import pandas as pd
import os
from io import BytesIO
from datetime import date,datetime
import tempfile

st.set_page_config(page_title='ANA Varese',layout='wide')
VERDE="#1A5D1A"
st.markdown(f"<style>h1,h2,h3{{color:{VERDE}!important;}}</style>",unsafe_allow_html=True)

def hdr():
 a=st.columns([1,5])
 with a[0]:
  try:
   st.image('logo.png',width=110)
  except:
   st.markdown('**ANA**')
 with a[1]:
  st.markdown(f'<div style="background:{VERDE};padding:12px;border-radius:8px;color:white;font-weight:bold;">NUCLEO PROT CIVILE ANA VARESE</div>',unsafe_allow_html=True)

def hdr_form(t):
 a=st.columns([1,8])
 with a[1]:
  st.markdown(f'## {t}')

def to_excel(df):
 o=BytesIO()
 k=[]
 for c in df.columns:
  if c not in ['Foto','FotoBytes']:
   k.append(c)
 df[k].to_excel(o,index=False,engine='openpyxl')
 return o.getvalue()

def to_pdf(df,ti):
 try:
  from reportlab.lib.pagesizes import landscape,A4
  from reportlab.platypus import SimpleDocTemplate,Table,TableStyle,Paragraph,Spacer
  from reportlab.lib.styles import getSampleStyleSheet
  from reportlab.lib import colors
  b=BytesIO()
  d=SimpleDocTemplate(b,pagesize=landscape(A4),leftMargin=20,rightMargin=20,topMargin=20,bottomMargin=20)
  s=getSampleStyleSheet()
  r=[]
  r.append(Paragraph(f"<b>{ti} - {date.today()}</b>",s['Title']))
  r.append(Spacer(1,12))
  if not df.empty:
   k=[]
   for c in df.columns:
    if c not in ['Foto','FotoBytes']:
     k.append(c)
   dd=[]
   dd.append(k)
   for _,rw in df.iterrows():
    x=[]
    for c in k:
     x.append(str(rw.get(c,''))[:50])
    dd.append(x)
   t=Table(dd,repeatRows=1)
   t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#1A5D1A')),('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),('ALIGN',(0,0),(-1,-1),'LEFT'),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('FONTSIZE',(0,0),(-1,-1),7),('GRID',(0,0),(-1,-1),0.5,colors.grey),]))
   r.append(t)
  d.build(r)
  return b.getvalue()
 except:
  return None

def to_excel_multi(ds):
 o=BytesIO()
 with pd.ExcelWriter(o,engine='openpyxl') as w:
  for n,dl in ds.items():
   if dl:
    df=pd.DataFrame(dl)
    k=[]
    for c in df.columns:
     if c not in ['Foto','FotoBytes']:
      k.append(c)
    df[k].to_excel(w,sheet_name=n[:31],index=False)
 return o.getvalue()

def save_icon(fb,nm):
 try:
  p=os.path.join(tempfile.gettempdir(),f"icon_{nm}.png")
  open(p,"wb").write(fb)
  return p
 except:
  return None

# INIT
for k in ['page','logged','menu','volontari','radio_db','eventi','emergenze','checkin','icone','postazioni','last_clicked','temp_markers','brogliaccio','mezzi','attrezzature','map_fullscreen','vol_form_data','alias_radio','brog_evento_blindato','brog_emergenza_blindata','brog_blindato','check_evento_blindato','check_emergenza_blindata','check_blindato']:
 if k not in st.session_state:
  if k=='page':
   st.session_state[k]='entra'
  elif k=='logged':
   st.session_state[k]=False
  elif k=='menu':
   st.session_state[k]='Dashboard'
  elif k=='last_clicked':
   st.session_state[k]=None
  elif k=='temp_markers':
   st.session_state[k]=[]
  elif k in ['map_fullscreen','brog_blindato','check_blindato']:
   st.session_state[k]=False
  elif k=='vol_form_data':
   st.session_state[k]={}
  else:
   st.session_state[k]=[]

if st.session_state.page=='entra':
 hdr()
 a=st.columns([1,2,1])
 with a[1]:
  try:
   st.image('copertina.png',width=300)
  except:
   pass
 st.markdown(f'<h2 style="text-align:center;color:{VERDE};">GESTIONALE</h2>',unsafe_allow_html=True)
 if st.button('ENTRA',use_container_width=True,type='primary'):
  st.session_state.page='login'
  st.rerun()

elif st.session_state.page=='login':
 hdr()
 a=st.columns([1,2,1])
 with a[1]:
  u=st.text_input('Utente')
  p=st.text_input('Password',type='password')
  if st.button('Accedi',use_container_width=True,type='primary'):
   if u=='admin' and p=='ana2024':
    st.session_state.logged=True
    st.session_state.page='dashboard'
    st.rerun()
   else:
    st.error('admin / ana2024')

elif st.session_state.page=='dashboard':
 hdr()
 base=['Dashboard','Volontari (con foto)','DB Radio','Alias Radio','Brogliaccio','Eventi','Emergenze','Check-in','Mezzi','Attrezzature','Mappa Avanzata','Libreria Icone','Backup','Esporta']
 tot=base
 with st.sidebar:
  try:
   st.image('logo.png',width=120)
  except:
   pass
  st.markdown('### MENU')
  try:
   idx=tot.index(st.session_state.menu)
  except:
   idx=0
  m=st.radio('Scegli:',tot,index=idx)
  st.session_state.menu=m
  if st.button('Logout',use_container_width=True):
   st.session_state.page='entra'
   st.rerun()
 cur=st.session_state.menu

 if cur=='Dashboard':
  hdr_form('Dashboard - TASTI OK')
  a=st.columns(4)
  a[0].metric('Volontari',len(st.session_state.volontari))
  a[1].metric('Radio',len(st.session_state.radio_db))
  a[2].metric('Alias',len(st.session_state.alias_radio))
  a[3].metric('Eventi',len(st.session_state.eventi))
  b=st.columns(4)
  b[0].metric('Check-in',len(st.session_state.checkin))
  b[1].metric('Brogliaccio',len(st.session_state.brogliaccio))
  b[2].metric('Mezzi',len(st.session_state.mezzi))
  b[3].metric('Emergenze',len(st.session_state.emergenze))
  st.divider()
  a=st.columns(4)
  if a[0].button('VOLONTARI',key='bv',use_container_width=True,type='primary'):
   st.session_state.menu='Volontari (con foto)'
   st.rerun()
  if a[1].button('DB RADIO',key='br',use_container_width=True,type='primary'):
   st.session_state.menu='DB Radio'
   st.rerun()
  if a[2].button('ALIAS RADIO',key='ba',use_container_width=True,type='primary'):
   st.session_state.menu='Alias Radio'
   st.rerun()
  if a[3].button('BROGLIACCIO',key='bb',use_container_width=True,type='primary'):
   st.session_state.menu='Brogliaccio'
   st.rerun()
  a=st.columns(4)
  if a[0].button('EVENTI',key='be',use_container_width=True,type='primary'):
   st.session_state.menu='Eventi'
   st.rerun()
  if a[1].button('EMERGENZE',key='bem',use_container_width=True,type='primary'):
   st.session_state.menu='Emergenze'
   st.rerun()
  if a[2].button('CHECK-IN',key='bc',use_container_width=True,type='primary'):
   st.session_state.menu='Check-in'
   st.rerun()
  if a[3].button('MEZZI',key='bm',use_container_width=True,type='primary'):
   st.session_state.menu='Mezzi'
   st.rerun()

 elif cur=='Volontari (con foto)':
  hdr_form('VOLONTARI - 5 TAB COME IERI OK')
  t=st.tabs(['1.Anagrafica','2.Contatti','3.Ruolo','4.Foto','5.Elenco'])
  with t[0]:
   with st.form('a1'):
    n=st.text_input('Nome *')
    cg=st.text_input('Cognome *')
    co=st.text_input('Comune *')
    if st.form_submit_button('Salva Anagrafica',type='primary',use_container_width=True):
     if n and cg and co:
      st.session_state.vol_form_data['Nome']=n
      st.session_state.vol_form_data['Cognome']=cg
      st.session_state.vol_form_data['Comune']=co
      st.success('Salvata')
  with t[1]:
   with st.form('a2'):
    ce=st.text_input('Cellulare *')
    em=st.text_input('Email')
    if st.form_submit_button('Salva Contatti',type='primary',use_container_width=True):
     if ce:
      st.session_state.vol_form_data['Cellulare']=ce
      st.session_state.vol_form_data['Email']=em
      st.success('Salvati')
  with t[2]:
   with st.form('a3'):
    ru=st.selectbox('Ruolo *',['Volontario','Caposquadra','Coordinatore','Autista','Radio','Logistica','Sanitario','Altro'])
    sq=st.selectbox('Squadra',['Alpini Caronno','Squadra A','Squadra B'])
    sp=st.multiselect('Specializzazioni',['AIB','Idro','Neve','Cinofilo','Motosega','Radio'])
    if st.form_submit_button('Salva Ruolo',type='primary',use_container_width=True):
     st.session_state.vol_form_data['Ruolo']=ru
     st.session_state.vol_form_data['Squadra']=sq
     st.session_state.vol_form_data['Special']=','.join(sp)
     st.success('Salvato')
  with t[3]:
   fo=st.file_uploader('Carica Foto',type=['png','jpg','jpeg'])
   if fo:
    st.image(fo,width=200)
   with st.form('a4'):
    if st.form_submit_button('SALVA VOLONTARIO',type='primary',use_container_width=True):
     if not st.session_state.vol_form_data.get('Nome'):
      st.error('Compila Anagrafica')
     else:
      v={}
      v['Nome']=st.session_state.vol_form_data.get('Nome','')
      v['Cognome']=st.session_state.vol_form_data.get('Cognome','')
      v['Comune']=st.session_state.vol_form_data.get('Comune','')
      v['Cellulare']=st.session_state.vol_form_data.get('Cellulare','')
      v['Ruolo']=st.session_state.vol_form_data.get('Ruolo','')
      v['Squadra']=st.session_state.vol_form_data.get('Squadra','')
      v['Special']=st.session_state.vol_form_data.get('Special','')
      v['FotoBytes']=fo.getvalue() if fo else None
      v['Data']=str(date.today())
      st.session_state.volontari.append(v)
      st.session_state.vol_form_data={}
      st.success('Salvato!')
      st.balloons()
      st.rerun()
  with t[4]:
   if st.session_state.volontari:
    ls=[]
    for x in st.session_state.volontari:
     r={}
     r['Nome']=x.get('Nome','')
     r['Cognome']=x.get('Cognome','')
     r['Comune']=x.get('Comune','')
     r['Cellulare']=x.get('Cellulare','')
     r['Ruolo']=x.get('Ruolo','')
     ls.append(r)
    df=pd.DataFrame(ls)
    st.dataframe(df,use_container_width=True,hide_index=True)
    a=st.columns(2)
    pdf=to_pdf(pd.DataFrame(st.session_state.volontari),'Volontari')
    if pdf:
     a[0].download_button('PDF Volontari',pdf,file_name='volontari.pdf',mime='application/pdf',use_container_width=True)
    a[1].download_button('Excel Volontari',to_excel(pd.DataFrame(st.session_state.volontari)),file_name='volontari.xlsx',mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',use_container_width=True)
   else:
    st.warning('Nessun volontario')

 elif cur=='DB Radio':
  hdr_form('DB RADIO')
  with st.form('r1'):
   mo=st.text_input('Modello *')
   ma=st.text_input('Matricola *')
   ti=st.selectbox('Tipo *',['DMR','PMR446','TETRA','VHF','UHF','CB','Altro'])
   fr=st.text_input('Frequenza')
   ca=st.text_input('Canale')
   sr=st.selectbox('Stato',['Disponibile','In Uso','Manutenzione'])
   if st.form_submit_button('Salva',type='primary',use_container_width=True):
    if mo and ma:
     rr={}
     rr['Modello']=mo
     rr['Matricola']=ma
     rr['Tipo']=ti
     rr['Frequenza']=fr
     rr['Canale']=ca
     rr['Stato']=sr
     st.session_state.radio_db.append(rr)
     st.success('Salvata')
  if st.session_state.radio_db:
   df=pd.DataFrame(st.session_state.radio_db)
   st.dataframe(df,use_container_width=True)
   a=st.columns(2)
   pdf=to_pdf(df,'DB Radio')
   if pdf:
    a[0].download_button('PDF Radio',pdf,file_name='radio.pdf',mime='application/pdf',use_container_width=True)
   a[1].download_button('Excel Radio',to_excel(df),file_name='radio.xlsx',mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',use_container_width=True)

 elif cur=='Alias Radio':
  hdr_form('ALIAS RADIO - EVENTO COMBO OK')
  with st.form('al1'):
   na=st.text_input('NOME ALIAS *')
   if st.session_state.volontari:
    lv=[]
    for v in st.session_state.volontari:
     lv.append(f"{v.get('Nome','')} {v.get('Cognome','')}")
    vs=st.selectbox('VOLONTARIO *',lv)
   else:
    vs=st.text_input('VOLONTARIO *')
   if st.session_state.postazioni:
    lp=['Base','Avanzata']
    for p in st.session_state.postazioni:
     lp.append(p.get('Nome',''))
    ps=st.selectbox('POSTAZIONE',lp)
   else:
    ps=st.selectbox('POSTAZIONE',['Base','Avanzata'])
   if st.session_state.eventi:
    le=['Nessuno']
    for e in st.session_state.eventi:
     ev=e.get('NomeEvento','')
     if ev:
      le.append(ev)
    es=st.selectbox('EVENTO *',le)
   else:
    es=st.text_input('EVENTO')
   if st.session_state.emergenze:
    lem=['Nessuna']
    for e in st.session_state.emergenze:
     lem.append(e.get('Tipo','')+' - '+e.get('Luogo',''))
    ems=st.selectbox('EMERGENZA',lem)
   else:
    ems=st.text_input('EMERGENZA')
   if st.form_submit_button('Salva Alias',type='primary',use_container_width=True):
    if na and vs:
     aa={}
     aa['NomeAlias']=na
     aa['Volontario']=vs
     aa['Postazione']=ps
     aa['Evento']=es
     aa['Emergenza']=ems
     aa['Data']=str(date.today())
     st.session_state.alias_radio.append(aa)
     st.success(f'Alias {na} salvato!')
     st.balloons()
    else:
     st.error('Obbligatori')
  if st.session_state.alias_radio:
   df=pd.DataFrame(st.session_state.alias_radio)
   st.dataframe(df,use_container_width=True,hide_index=True)
   a=st.columns(2)
   pdf=to_pdf(df,'Alias Radio')
   if pdf:
    a[0].download_button('PDF Alias',pdf,file_name='alias.pdf',mime='application/pdf',use_container_width=True)
   a[1].download_button('Excel Alias',to_excel(df),file_name='alias.xlsx',mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',use_container_width=True)

 elif cur=='Brogliaccio':
  hdr_form('BROGLIACCIO BLINDATO')
  if not st.session_state.brog_blindato:
   a=st.columns(2)
   with a[0]:
    if st.session_state.eventi:
     le=['Nessuno']
     for e in st.session_state.eventi:
      le.append(e.get('NomeEvento',''))
     ev=st.selectbox('EVENTO da blindare',le,key='ev_blind')
    else:
     ev='Nessuno'
    if st.button('BLINDA SU EVENTO',type='primary',use_container_width=True):
     if ev!='Nessuno':
      st.session_state.brog_evento_blindato=ev
      st.session_state.brog_emergenza_blindata=None
      st.session_state.brog_blindato=True
      st.rerun()
   with a[1]:
    if st.session_state.emergenze:
     lem=['Nessuna']
     for e in st.session_state.emergenze:
      lem.append(e.get('Tipo','')+' - '+e.get('Luogo',''))
     em=st.selectbox('EMERGENZA da blindare',lem,key='em_blind')
    else:
     em='Nessuna'
    if st.button('BLINDA SU EMERGENZA',type='primary',use_container_width=True):
     if em!='Nessuna':
      st.session_state.brog_emergenza_blindata=em
      st.session_state.brog_evento_blindato=None
      st.session_state.brog_blindato=True
      st.rerun()
  else:
   if st.session_state.brog_evento_blindato:
    st.success(f"BLINDATO EVENTO: {st.session_state.brog_evento_blindato}")
   if st.session_state.brog_emergenza_blindata:
    st.success(f"BLINDATO EMERGENZA: {st.session_state.brog_emergenza_blindata}")
   if st.button('SBLOCCA BROGLIACCIO',type='primary',use_container_width=True):
    st.session_state.brog_blindato=False
    st.session_state.brog_evento_blindato=None
    st.session_state.brog_emergenza_blindata=None
    st.rerun()
  st.divider()
  if not st.session_state.brog_blindato:
   st.warning('Prima BLINDA su Evento o Emergenza')
  else:
   with st.form('b1'):
    if st.session_state.brog_evento_blindato:
     st.text_input('EVENTO BLINDATO',value=st.session_state.brog_evento_blindato,disabled=True)
    if st.session_state.brog_emergenza_blindata:
     st.text_input('EMERGENZA BLINDATA',value=st.session_state.brog_emergenza_blindata,disabled=True)
    if st.session_state.alias_radio:
     la=[]
     for a in st.session_state.alias_radio:
      la.append(a.get('NomeAlias',''))
     mi=st.selectbox('Mittente * (da Alias)',la)
     de=st.selectbox('Destinatario * (da Alias)',la)
    else:
     mi=st.text_input('Mittente *')
     de=st.text_input('Destinatario *')
    ora=st.text_input('Ora',value=datetime.now().strftime('%H:%M'))
    ms=st.text_area('Messaggio *')
    if st.form_submit_button('Salva Brogliaccio',type='primary',use_container_width=True):
     if mi and de and ms:
      b={}
      b['Ora']=ora
      b['Evento']=st.session_state.brog_evento_blindato if st.session_state.brog_evento_blindato else ''
      b['Emergenza']=st.session_state.brog_emergenza_blindata if st.session_state.brog_emergenza_blindata else ''
      b['Mittente']=mi
      b['Destinatario']=de
      b['Messaggio']=ms
      b['Data']=str(date.today())
      st.session_state.brogliaccio.append(b)
      st.success('Salvato')
     else:
      st.error('Compila campi')
  if st.session_state.brogliaccio:
   df=pd.DataFrame(st.session_state.brogliaccio)
   st.dataframe(df,use_container_width=True,hide_index=True)
   a=st.columns(2)
   pdf=to_pdf(df,'Brogliaccio')
   if pdf:
    a[0].download_button('PDF Brogliaccio',pdf,file_name='brogliaccio.pdf',mime='application/pdf',use_container_width=True)
   a[1].download_button('Excel Brogliaccio',to_excel(df),file_name='brogliaccio.xlsx',mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',use_container_width=True)

 elif cur=='Eventi':
  hdr_form('EVENTI')
  with st.form('e1'):
   ne=st.text_input('NOME EVENTO *')
   lu=st.text_input('Luogo *')
   if st.form_submit_button('Crea Evento',type='primary',use_container_width=True):
    if ne and lu:
     ee={}
     ee['NomeEvento']=ne
     ee['Luogo']=lu
     ee['Data']=str(date.today())
     st.session_state.eventi.append(ee)
     st.success(f'Evento {ne} creato')
  if st.session_state.eventi:
   df=pd.DataFrame(st.session_state.eventi)
   st.dataframe(df,use_container_width=True)
   a=st.columns(2)
   pdf=to_pdf(df,'Eventi')
   if pdf:
    a[0].download_button('PDF Eventi',pdf,file_name='eventi.pdf',mime='application/pdf',use_container_width=True)
   a[1].download_button('Excel Eventi',to_excel(df),file_name='eventi.xlsx',mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',use_container_width=True)

 elif cur=='Emergenze':
  hdr_form('EMERGENZE')
  with st.form('em1'):
   ti=st.selectbox('Tipo *',['Alluvione','Frana','Incendio','Terremoto','Neve','Ricerca','Altro'])
   lu=st.text_input('Luogo *')
   de=st.text_area('Descrizione *')
   if st.form_submit_button('Attiva',type='primary',use_container_width=True):
    if lu and de:
     ee={}
     ee['Tipo']=ti
     ee['Luogo']=lu
     ee['Descrizione']=de
     ee['Data']=str(date.today())
     st.session_state.emergenze.append(ee)
     st.success('Attivata')
  if st.session_state.emergenze:
   df=pd.DataFrame(st.session_state.emergenze)
   st.dataframe(df,use_container_width=True)
   a=st.columns(2)
   pdf=to_pdf(df,'Emergenze')
   if pdf:
    a[0].download_button('PDF Emergenze',pdf,file_name='emergenze.pdf',mime='application/pdf',use_container_width=True)
   a[1].download_button('Excel Emergenze',to_excel(df),file_name='emergenze.xlsx',mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',use_container_width=True)

 elif cur=='Check-in':
  hdr_form('CHECK-IN BLINDATO COME BROGLIACCIO OK')
  st.info('Check-in blindato su Evento/Emergenza finche non decidi tu')
  if not st.session_state.check_blindato:
   a=st.columns(2)
   with a[0]:
    if st.session_state.eventi:
     le=['Nessuno']
     for e in st.session_state.eventi:
      le.append(e.get('NomeEvento',''))
     ev=st.selectbox('EVENTO da blindare',['Nessuno']+le,key='ev_blind_check')
    else:
     ev='Nessuno'
    if st.button('BLINDA CHECK-IN SU EVENTO',type='primary',use_container_width=True,key='bce'):
     if ev!='Nessuno':
      st.session_state.check_evento_blindato=ev
      st.session_state.check_emergenza_blindata=None
      st.session_state.check_blindato=True
      st.rerun()
   with a[1]:
    if st.session_state.emergenze:
     lem=['Nessuna']
     for e in st.session_state.emergenze:
      lem.append(e.get('Tipo','')+' - '+e.get('Luogo',''))
     em=st.selectbox('EMERGENZA da blindare',lem,key='em_blind_check')
    else:
     em='Nessuna'
    if st.button('BLINDA CHECK-IN SU EMERGENZA',type='primary',use_container_width=True,key='bcm'):
     if em!='Nessuna':
      st.session_state.check_emergenza_blindata=em
      st.session_state.check_evento_blindato=None
      st.session_state.check_blindato=True
      st.rerun()
  else:
   if st.session_state.check_evento_blindato:
    st.success(f"CHECK-IN BLINDATO EVENTO: {st.session_state.check_evento_blindato}")
   if st.session_state.check_emergenza_blindata:
    st.success(f"CHECK-IN BLINDATO EMERGENZA: {st.session_state.check_emergenza_blindata}")
   if st.button('SBLOCCA CHECK-IN',type='primary',use_container_width=True,key='sbc'):
    st.session_state.check_blindato=False
    st.session_state.check_evento_blindato=None
    st.session_state.check_emergenza_blindata=None
    st.rerun()
  st.divider()
  if not st.session_state.check_blindato:
   st.warning('Prima BLINDA su Evento o Emergenza')
  else:
   if not st.session_state.volontari:
    st.warning('Inserisci prima Volontario')
   else:
    with st.form('c1'):
     if st.session_state.check_evento_blindato:
      st.text_input('EVENTO BLINDATO',value=st.session_state.check_evento_blindato,disabled=True)
     if st.session_state.check_emergenza_blindata:
      st.text_input('EMERGENZA BLINDATA',value=st.session_state.check_emergenza_blindata,disabled=True)
     vs=st.selectbox('Volontario *',['{} {}'.format(v.get('Nome',''),v.get('Cognome','')) for v in st.session_state.volontari])
     ps=st.selectbox('Postazione *',['Base','Avanzata'])
     ora=st.text_input('Ora',value=datetime.now().strftime('%H:%M'))
     if st.form_submit_button('Registra Check-in Blindato',type='primary',use_container_width=True):
      cc={}
      cc['Ora']=ora
      cc['Evento']=st.session_state.check_evento_blindato if st.session_state.check_evento_blindato else ''
      cc['Emergenza']=st.session_state.check_emergenza_blindata if st.session_state.check_emergenza_blindata else ''
      cc['Volontario']=vs
      cc['Postazione']=ps
      cc['Data']=str(date.today())
      st.session_state.checkin.append(cc)
      st.success(f'Check-in {vs} registrato')
  if st.session_state.checkin:
   df=pd.DataFrame(st.session_state.checkin)
   st.dataframe(df,use_container_width=True,hide_index=True)
   a=st.columns(2)
   pdf=to_pdf(df,'Check-in')
   if pdf:
    a[0].download_button('PDF Check-in',pdf,file_name='checkin.pdf',mime='application/pdf',use_container_width=True)
   a[1].download_button('Excel Check-in',to_excel(df),file_name='checkin.xlsx',mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',use_container_width=True)

 elif cur=='Mezzi':
  hdr_form('MEZZI')
  with st.form('mz1'):
   ta=st.text_input('Targa *')
   tm=st.selectbox('Tipo *',['Fuoristrada','Furgone','Autocarro','Ambulanza','Pulmino','Altro'])
   if st.form_submit_button('Salva',type='primary',use_container_width=True):
    if ta and tm:
     mz={}
     mz['Targa']=ta
     mz['Tipo']=tm
     st.session_state.mezzi.append(mz)
     st.success('Salvato')
  if st.session_state.mezzi:
   df=pd.DataFrame(st.session_state.mezzi)
   st.dataframe(df,use_container_width=True)
   a=st.columns(2)
   pdf=to_pdf(df,'Mezzi')
   if pdf:
    a[0].download_button('PDF Mezzi',pdf,file_name='mezzi.pdf',mime='application/pdf',use_container_width=True)
   a[1].download_button('Excel Mezzi',to_excel(df),file_name='mezzi.xlsx',mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',use_container_width=True)

 elif cur=='Attrezzature':
  hdr_form('ATTREZZATURE')
  with st.form('at1'):
   na=st.text_input('Attrezzatura *')
   qu=st.number_input('Quantita *',min_value=1,value=1)
   if st.form_submit_button('Salva',type='primary',use_container_width=True):
    if na:
     at={}
     at['Attrezzatura']=na
     at['Quantita']=qu
     st.session_state.attrezzature.append(at)
     st.success('Salvata')
  if st.session_state.attrezzature:
   df=pd.DataFrame(st.session_state.attrezzature)
   st.dataframe(df,use_container_width=True)
   a=st.columns(2)
   pdf=to_pdf(df,'Attrezzature')
   if pdf:
    a[0].download_button('PDF Attrezzature',pdf,file_name='attrezzature.pdf',mime='application/pdf',use_container_width=True)
   a[1].download_button('Excel Attrezzature',to_excel(df),file_name='attrezzature.xlsx',mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',use_container_width=True)

 elif cur=='Mappa Avanzata':
  hdr_form('MAPPA AVANZATA')
  st.info('OSM default, fullscreen')
  a=st.columns([2,2,1])
  with a[0]:
   mt=st.selectbox('Tipo Mappa',['OpenStreetMap','Google Map','Google Satellite'],index=0)
  with a[1]:
   ic=st.selectbox('Icona',['Nessuna']+[i['Nome'] for i in st.session_state.icone] if st.session_state.icone else ['Nessuna'])
  with a[2]:
   lb='Riduci' if st.session_state.map_fullscreen else 'Espandi'
   if st.button(lb,key='exp1',use_container_width=True):
    st.session_state.map_fullscreen=not st.session_state.map_fullscreen
    st.rerun()
  h=800 if st.session_state.map_fullscreen else 450
  try:
   import folium
   from streamlit_folium import st_folium
   from folium.plugins import Fullscreen
   import requests
   def rev_geo(la,lo):
    try:
     u=f'https://nominatim.openstreetmap.org/reverse?format=json&lat={la}&lon={lo}&zoom=18'
     r=requests.get(u,headers={'User-Agent':'ANA'},timeout=5)
     if r.status_code==200:
      d=r.json()
      aa=d.get('address',{})
      c=aa.get('city') or aa.get('town') or ''
      return c,''
    except:
     pass
    return '',''
   la_c,lo_c=45.65,8.79
   if st.session_state.postazioni:
    s1=0
    s2=0
    for p in st.session_state.postazioni:
     s1=s1+p['Lat']
     s2=s2+p['Log']
    la_c=s1/len(st.session_state.postazioni)
    lo_c=s2/len(st.session_state.postazioni)
   mm=folium.Map(location=[la_c,lo_c],zoom_start=12,tiles=None)
   if mt=='OpenStreetMap':
    folium.TileLayer('openstreetmap').add_to(mm)
   elif mt=='Google Map':
    folium.TileLayer(tiles='https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',attr='Google').add_to(mm)
   else:
    folium.TileLayer(tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',attr='Google').add_to(mm)
   Fullscreen(position='topleft',title='Espandi',title_cancel='Esci ESC',force_separate_button=True).add_to(mm)
   for p in st.session_state.postazioni:
    la_f=p['Lat']
    lo_f=p['Log']
    pp=f"<b>{p['Nome']}</b><br>{p.get('Comune','')}"
    icn=p.get('Icona','Nessuna')
    up=None
    if icn!='Nessuna':
     io=None
     for i in st.session_state.icone:
      if i['Nome']==icn:
       io=i
     if io and io.get('FileBytes'):
      up=save_icon(io['FileBytes'],icn)
    if up:
     folium.Marker([la_f,lo_f],popup=pp,icon=folium.CustomIcon(up,icon_size=(40,40))).add_to(mm)
    else:
     folium.Marker([la_f,lo_f],popup=pp,icon=folium.Icon(color='green')).add_to(mm)
   ip=None
   if ic!='Nessuna':
    io=None
    for i in st.session_state.icone:
     if i['Nome']==ic:
      io=i
    if io and io.get('FileBytes'):
     ip=save_icon(io['FileBytes'],ic)
   for tm in st.session_state.temp_markers:
    if ip:
     folium.Marker([tm['lat'],tm['lon']],icon=folium.CustomIcon(ip,icon_size=(40,40))).add_to(mm)
    else:
     folium.Marker([tm['lat'],tm['lon']],icon=folium.Icon(color='orange')).add_to(mm)
   folium.LayerControl().add_to(mm)
   out=st_folium(mm,width=1400,height=h,use_container_width=True,returned_objects=['last_clicked'],key='map1')
   if out and out.get('last_clicked'):
    la=out['last_clicked']['lat']
    lo=out['last_clicked']['lng']
    co,_=rev_geo(la,lo)
    st.session_state.temp_markers.append({'lat':la,'lon':lo,'icona':ic,'comune':co})
    st.session_state.last_clicked={'lat':la,'lon':lo,'icona':ic,'comune':co}
    st.success(f"Click {la:.5f} {lo:.5f}")
    st.rerun()
  except Exception as e:
   st.error(f"Errore mappa: {e}")
  last=st.session_state.last_clicked
  if last:
   st.info(f"Click: {last['lat']:.6f} {last['lon']:.6f}")
  with st.form('fp'):
   np=st.text_input('Nome Postazione *')
   cp=st.text_input('Comune *',value=last.get('comune','') if last else '')
   la=st.text_input('Lat *',value=str(last['lat']) if last else '')
   lo=st.text_input('Log *',value=str(last['lon']) if last else '')
   li=['Nessuna']
   for i in st.session_state.icone:
    li.append(i['Nome'])
   ip=st.selectbox('Icona',li)
   if st.form_submit_button('Salva Postazione',type='primary',use_container_width=True):
    if np and cp and la and lo:
     try:
      la_v=float(la.replace(',','.'))
      lo_v=float(lo.replace(',','.'))
      nn={}
      nn['Nome']=np
      nn['Comune']=cp
      nn['Icona']=ip
      nn['Lat']=la_v
      nn['Log']=lo_v
      st.session_state.postazioni.append(nn)
      st.session_state.temp_markers=[]
      st.session_state.last_clicked=None
      st.success('Postazione salvata')
      st.rerun()
     except:
      st.error('Lat/Log non validi')

 elif cur=='Libreria Icone':
  hdr_form('LIBRERIA ICONE')
  with st.form('ic1'):
   ni=st.text_input('Nome icona *')
   fi=st.file_uploader('Carica PNG/JPG *',type=['png','jpg','jpeg'])
   if fi:
    st.image(fi,width=120)
   if st.form_submit_button('Salva Icona',type='primary',use_container_width=True):
    if ni and fi:
     nn={}
     nn['Nome']=ni
     nn['FileName']=fi.name
     nn['FileBytes']=fi.getvalue()
     st.session_state.icone.append(nn)
     st.success('Icona caricata')
  if st.session_state.icone:
   cs=st.columns(4)
   for idx,ic in enumerate(st.session_state.icone):
    co=cs[idx%4]
    with co:
     st.write(f"**{ic['Nome']}**")
     if ic.get('FileBytes'):
      st.image(ic['FileBytes'],width=80)
     if st.button('Elimina',key=f"del_{idx}"):
      st.session_state.icone.pop(idx)
      st.rerun()

 elif cur=='Backup':
  hdr_form('BACKUP TUTTI I DATI + PDF')
  ds={}
  ds['Volontari']=st.session_state.volontari
  ds['Radio']=st.session_state.radio_db
  ds['AliasRadio']=st.session_state.alias_radio
  ds['Brogliaccio']=st.session_state.brogliaccio
  ds['Eventi']=st.session_state.eventi
  ds['Emergenze']=st.session_state.emergenze
  ds['Checkin']=st.session_state.checkin
  ds['Mezzi']=st.session_state.mezzi
  ds['Attrezzature']=st.session_state.attrezzature
  ds['Postazioni']=st.session_state.postazioni
  a=st.columns(2)
  with a[0]:
   if any(ds.values()):
    st.download_button('EXPORT TOTALE EXCEL',to_excel_multi(ds),file_name=f'backup_TUTTI_{date.today()}.xlsx',mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',use_container_width=True,type='primary')
  with a[1]:
   fe=st.file_uploader('Carica Excel',type=['xlsx'],key='imp')
   if fe:
    try:
     xls=pd.ExcelFile(fe)
     if st.button('CONFERMA IMPORT',type='primary',use_container_width=True,key='ci'):
      for sh in xls.sheet_names:
       df=pd.read_excel(xls,sheet_name=sh)
       sl=sh.lower()
       if 'volontar' in sl:
        st.session_state.volontari=df.to_dict('records')
       elif 'alias' in sl:
        st.session_state.alias_radio=df.to_dict('records')
       elif 'radio' in sl:
        st.session_state.radio_db=df.to_dict('records')
       elif 'brogliaccio' in sl:
        st.session_state.brogliaccio=df.to_dict('records')
       elif 'event' in sl:
        st.session_state.eventi=df.to_dict('records')
       elif 'emergenz' in sl:
        st.session_state.emergenze=df.to_dict('records')
       elif 'checkin' in sl:
        st.session_state.checkin=df.to_dict('records')
       elif 'mezz' in sl:
        st.session_state.mezzi=df.to_dict('records')
       elif 'attrezz' in sl:
        st.session_state.attrezzature=df.to_dict('records')
       elif 'postaz' in sl:
        st.session_state.postazioni=df.to_dict('records')
      st.success('Import completato!')
      st.rerun()
    except Exception as e:
     st.error(f'Errore: {e}')

 elif cur=='Esporta':
  hdr_form('ESPORTA - EXCEL + PDF')
  for k,ti in [('volontari','Volontari'),('radio_db','Radio'),('alias_radio','Alias Radio'),('brogliaccio','Brogliaccio'),('eventi','Eventi'),('emergenze','Emergenze'),('checkin','Check-in'),('postazioni','Postazioni'),('mezzi','Mezzi'),('attrezzature','Attrezzature')]:
   if st.session_state[k]:
    df=pd.DataFrame(st.session_state[k])
    st.markdown(f'**{ti} - {len(df)} record**')
    a=st.columns(2)
    pdf=to_pdf(df,f'{ti} ANA Varese')
    if pdf:
     a[0].download_button(f"PDF {ti}",pdf,file_name=f"{k}.pdf",mime='application/pdf',key=f"pdf_{k}",use_container_width=True)
    a[1].download_button(f"Excel {ti}",to_excel(df),file_name=f"{k}.xlsx",mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',key=f"ex_{k}",use_container_width=True)
    st.divider()