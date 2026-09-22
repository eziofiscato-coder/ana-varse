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