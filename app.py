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
 k=[c for c in df.columns if c not in ['Foto','FotoBytes']]
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
   k=[c for c in df.columns if c not in ['Foto','FotoBytes']]
   dd=[k]
   for _,rw in df.iterrows():
    x=[str(rw.get(c,''))[:50] for c in k]
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
    k=[c for c in df.columns if c not in ['Foto','FotoBytes']]
    df[k].to_excel(w,sheet_name=n[:31],index=False)
 return o.getvalue()

def save_icon(fb,nm):
 try:
  p=os.path.join(tempfile.gettempdir(),f"icon_{nm}.png")
  open(p,"wb").write(fb)
  return p
 except:
  return None

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
 tot=base+list(st.session_state.get('custom_defs',{}).keys())
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
    lv=[f"{v.get('Nome','')} {v.get('Cognome','')}" for v in st.session_state.volontari]
    vs=st.selectbox('VOLONTARIO *',lv)
   else:
    vs=st.text_input('VOLONTARIO *')
   if st.session_state.postazioni:
    lp=['Base','Avanzata']+[p.get('Nome','') for p in st.session_state.postazioni]
    ps=st.selectbox('POSTAZIONE',lp)
   else:
    ps=st.selectbox('POSTAZIONE',['Base','Avanzata'])
   if st.session_state.eventi:
    le=[e.get('NomeEvento','') for
