import streamlit as st
import pandas as pd
import os
from io import BytesIO
from datetime import date,datetime
import tempfile

st.set_page_config(page_title='ANA Varese',layout='wide')
VERDE="#1A5D1A"

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

# PAGINA ENTRA - CON AVANTI CHE VA AVANTI
if st.session_state.page=='entra':
 hdr()
 a=st.columns([1,2,1])
 with a[1]:
  try:
   st.image('copertina.png',width=350)
  except:
   try:
    st.image('logo.png',width=250)
   except:
    pass
  st.markdown(f'<h2 style="text-align:center;color:{VERDE};">GESTIONALE VOLONTARIATO<br>Sezione Varese</h2>',unsafe_allow_html=True)
  st.markdown('<br>',unsafe_allow_html=True)
  # BOTTONE AVANTI SISTEMATO
  if st.button('AVANTI - ENTRA',use_container_width=True,type='primary',key='btn_avanti_entra'):
   st.session_state.page='login'
   st.rerun()

# PAGINA LOGIN - CON AVANTI CHE VA AVANTI
elif st.session_state.page=='login':
 hdr()
 a=st.columns([1,2,1])
 with a[1]:
  st.markdown('### LOGIN')
  u=st.text_input('Utente',key='user_login')
  p=st.text_input('Password',type='password',key='pwd_login')
  c=st.columns(2)
  with c[0]:
   if st.button('INDIETRO',use_container_width=True,key='btn_indietro'):
    st.session_state.page='entra'
    st.rerun()
  with c[1]:
   if st.button('AVANTI - ACCEDI',use_container_width=True,type='primary',key='btn_avanti_login'):
    if u=='admin' and p=='ana2024':
     st.session_state.logged=True
     st.session_state.page='dashboard'
     st.success('Login OK - vado avanti...')
     st.rerun()
    else:
     st.error('Utente: admin - Password: ana2024')
  st.info('Usa admin / ana2024')

# DASHBOARD
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
   st.session_state.logged=False
   st.rerun()
 cur=st.session_state.menu

 if cur=='Dashboard':
  hdr_form('Dashboard')
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

 elif cur=='Volontari (con foto)':
  hdr_form('VOLONTARI - MASCHERA COMPLETA COME PRIMA OK')
  t=st.tabs(['1.Anagrafica Completa','2.Contatti','3.Ruolo','4.Foto','5.Elenco'])
  with t[0]:
   st.markdown('### 1. Anagrafica - TUTTI I CAMPI COME PRIMA')
   with st.form('a1'):
    n=st.text_input('Nome *')
    cg=st.text_input('Cognome *')
    cf=st.text_input('Codice Fiscale')
    dn=st.date_input('Data Nascita',value=date(1980,1,1))
    ln=st.text_input('Luogo Nascita')
    co=st.text_input('Comune Residenza *')
    ind=st.text_input('Indirizzo')
    cap=st.text_input('CAP')
    prov=st.text_input('Provincia')
    tess=st.text_input('Tessera ANA N.')
    grup=st.text_input('Gruppo Alpini')
    if st.form_submit_button('Salva Anagrafica Completa',type='primary',use_container_width=True):
     if n and cg and co:
      st.session_state.vol_form_data['Nome']=n
      st.session_state.vol_form_data['Cognome']=cg
      st.session_state.vol_form_data['CodFisc']=cf
      st.session_state.vol_form_data['DataNasc']=str(dn)
      st.session_state.vol_form_data['LuogoNasc']=ln
      st.session_state.vol_form_data['Comune']=co
      st.session_state.vol_form_data['Indirizzo']=ind
      st.session_state.vol_form_data['CAP']=cap
      st.session_state.vol_form_data['Prov']=prov
      st.session_state.vol_form_data['Tessera']=tess
      st.session_state.vol_form_data['Gruppo']=grup
      st.success('Anagrafica completa salvata - vai in Contatti!')
     else:
      st.error('Nome, Cognome, Comune obbligatori')
  with t[1]:
   with st.form('a2'):
    ce=st.text_input('Cellulare *')
    ce2=st.text_input('Cellulare 2')
    em=st.text_input('Email')
    tel=st.text_input('Telefono Fisso')
    cont=st.text_input('Contatto Emergenza')
    tel_em=st.text_input('Tel Emergenza')
    if st.form_submit_button('Salva Contatti',type='primary',use_container_width=True):
     if ce:
      st.session_state.vol_form_data['Cellulare']=ce
      st.session_state.vol_form_data['Cell2']=ce2
      st.session_state.vol_form_data['Email']=em
      st.session_state.vol_form_data['TelFisso']=tel
      st.session_state.vol_form_data['ContEmerg']=cont
      st.session_state.vol_form_data['TelEmerg']=tel_em
      st.success('Contatti salvati - vai in Ruolo!')
     else:
      st.error('Cellulare obbligatorio')
  with t[2]:
   with st.form('a3'):
    ru=st.selectbox('Ruolo *',['Volontario','Caposquadra','Coordinatore','Autista','Radio','Logistica','Sanitario','Segreteria','Telecomunicazioni','Altro'])
    sq=st.selectbox('Squadra',['Alpini Caronno','Squadra A','Squadra B'])
    sp=st.multiselect('Specializzazioni',['AIB','Idro','Neve','Cinofilo','Motosega','Radio'])
    abi=st.multiselect('Abilitazioni',['BLSD','Primo Soccorso','Motosega','Patente C'])
    tag=st.text_input('Taglia Vestiario')
    note=st.text_area('Note')
    if st.form_submit_button('Salva Ruolo',type='primary',use_container_width=True):
     st.session_state.vol_form_data['Ruolo']=ru
     st.session_state.vol_form_data['Squadra']=sq
     st.session_state.vol_form_data['Special']=','.join(sp)
     st.session_state.vol_form_data['Abilit']=','.join(abi)
     st.session_state.vol_form_data['Taglia']=tag
     st.session_state.vol_form_data['Note']=note
     st.success('Ruolo salvato - vai in Foto!')
  with t[3]:
   fo=st.file_uploader('Carica Foto',type=['png','jpg','jpeg'])
   if fo:
    st.image(fo,width=200)
   with st.form('a4'):
    if st.form_submit_button('SALVA VOLONTARIO COMPLETO',type='primary',use_container_width=True):
     if not st.session_state.vol_form_data.get('Nome'):
      st.error('Compila prima Anagrafica!')
     else:
      v={}
      v['Nome']=st.session_state.vol_form_data.get('Nome','')
      v['Cognome']=st.session_state.vol_form_data.get('Cognome','')
      v['CodFisc']=st.session_state.vol_form_data.get('CodFisc','')
      v['DataNasc']=st.session_state.vol_form_data.get('DataNasc','')
      v['LuogoNasc']=st.session_state.vol_form_data.get('LuogoNasc','')
      v['Comune']=st.session_state.vol_form_data.get('Comune','')
      v['Indirizzo']=st.session_state.vol_form_data.get('Indirizzo','')
      v['CAP']=st.session_state.vol_form_data.get('CAP','')
      v['Cellulare']=st.session_state.vol_form_data.get('Cellulare','')
      v['Ruolo']=st.session_state.vol_form_data.get('Ruolo','')
      v['Squadra']=st.session_state.vol_form_data.get('Squadra','')
      v['Special']=st.session_state.vol_form_data.get('Special','')
      v['FotoBytes']=fo.getvalue() if fo else None
      v['Data']=str(date.today())
      st.session_state.volontari.append(v)
      st.session_state.vol_form_data={}
      st.success('Volontario completo salvato!')
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
    pdf=to_pdf(pd.DataFrame(st.session_state.volontari),'Volontari Completo')
    if pdf:
     a[0].download_button('PDF Volontari',pdf,file_name='volontari.pdf',mime='application/pdf',use_container_width=True)
    a[1].download_button('Excel Volontari',to_excel(pd.DataFrame(st.session_state.volontari)),file_name='volontari.xlsx',mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',use_container_width=True)
   else:
    st.warning('Nessun volontario')

 elif cur=='Alias Radio':
  hdr_form('ALIAS RADIO - EVENTO COMBO DA FORM EVENTO OK')
  with st.form('al1'):
   na=st.text_input('NOME ALIAS *')
   if st.session_state.volontari:
    lv=[]
    for v in st.session_state.volontari:
     lv.append(f"{v.get('Nome','')} {v.get('Cognome','')}")
    vs=st.selectbox('VOLONTARIO *',lv)
   else:
    vs=st.text_input('VOLONTARIO *')
   if st.session_state.eventi:
    le=['Nessuno']
    for e in st.session_state.eventi:
     ev=e.get('NomeEvento','')
     if ev:
      le.append(ev)
    es=st.selectbox('EVENTO *',le)
   else:
    es=st.text_input('EVENTO')
   if st.form_submit_button('Salva Alias',type='primary',use_container_width=True):
    if na and vs:
     aa={}
     aa['NomeAlias']=na
     aa['Volontario']=vs
     aa['Evento']=es
     aa['Data']=str(date.today())
     st.session_state.alias_radio.append(aa)
     st.success(f'Alias {na} salvato!')
     st.balloons()
  if st.session_state.alias_radio:
   df=pd.DataFrame(st.session_state.alias_radio)
   st.dataframe(df,use_container_width=True)

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
      st.session_state.brog_blindato=True
      st.rerun()
   with a[1]:
    if st.session_state.emergenze:
     lem=['Nessuna']
     for e in st.session_state.emergenze:
      lem.append(e.get('Tipo','')+' - '+e.get('Luogo',''))
     em=st.selectbox('EMERGENZA da blindare',lem,key='em_blind')
    else:
     em='Ness