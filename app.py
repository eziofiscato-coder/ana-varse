import streamlit as st
import pandas as pd
from io import BytesIO
import os, json, hashlib, requests
from datetime import datetime, date

try:
 import folium
 from streamlit_folium import st_folium
 HAS=True
except:
 HAS=False

st.set_page_config(page_title="ANA Varese", layout="wide")

st.markdown("""
<style>
.block-container{padding-top:50px!important;max-width:100%!important;}
.stForm{background:#e8f5e9!important;border:2px solid #0e7a3d!important;}
.stForm label{color:#000!important;font-weight:bold!important;font-family:Times New Roman!important;}
.stButton>button{background:#0e7a3d!important;color:white!important;font-weight:bold!important;}
.popup-overlay{position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.8);z-index:9999;display:flex;justify-content:center;align-items:center;}
.popup-content{background:white;padding:20px;border-radius:15px;max-width:600px;text-align:center;border:5px solid #0e7a3d;}
</style>
""", unsafe_allow_html=True)

def load(f,d):
 try:
  if os.path.exists(f):
   with open(f,'r',encoding='utf-8') as fh:
    return json.load(fh)
 except:
  pass
 return d

def save(f,d):
 try:
  with open(f,'w',encoding='utf-8') as fh:
   json.dump(d,fh,indent=2)
 except:
  pass

def hp(p):
 return hashlib.sha256(p.encode()).hexdigest()

def gaddr(lat,lon):
 try:
  u=f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=jsonv2&accept-language=it"
  r=requests.get(u,headers={'User-Agent':'ana-varese'},timeout=8)
  if r.status_code==200:
   j=r.json()
   a=j.get('address',{})
   com=a.get('city') or a.get('town') or a.get('village') or a.get('municipality') or ''
   via=a.get('road') or ''
   num=a.get('house_number') or ''
   full_via=(via+' '+num).strip()
   return com,full_via
 except:
  pass
 return '',''

def fmt_date(d):
 if isinstance(d,date):
  return d.strftime("%d/%m/%Y")
 return str(d)

def make_pdf(title, df):
 # FIX PDF - usa SimpleDocTemplate che funziona sempre
 try:
  from reportlab.lib.pagesizes import A4
  from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
  from reportlab.lib.styles import getSampleStyleSheet
  from reportlab.lib import colors
  buf=BytesIO()
  doc=SimpleDocTemplate(buf,pagesize=A4,leftMargin=15,rightMargin=15,topMargin=20,bottomMargin=20)
  styles=getSampleStyleSheet()
  story=[]
  story.append(Paragraph(f"<b>{title}</b>",styles['Title']))
  story.append(Spacer(1,12))
  story.append(Paragraph(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')} - ANA Varese",styles['Normal']))
  story.append(Spacer(1,12))
  if df is not None and not df.empty:
   # Prendi prime 6 colonne
   cols=list(df.columns)[:7]
   data=[cols]
   for _,row in df.head(50).iterrows():
    vals=[str(row.get(c,''))[:25] for c in cols]
    data.append(vals)
   t=Table(data,repeatRows=1)
   t.setStyle(TableStyle([
    ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#0e7a3d')),
    ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
    ('ALIGN',(0,0),(-1,-1),'LEFT'),
    ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
    ('FONTSIZE',(0,0),(-1,-1),7),
    ('GRID',(0,0),(-1,-1),0.5,colors.grey),
   ]))
   story.append(t)
  else:
   story.append(Paragraph("Nessun dato disponibile",styles['Normal']))
  doc.build(story)
  buf.seek(0)
  return buf.getvalue()
 except Exception as e:
  st.error(f"Errore PDF: {e}")
  return None

def export_excel(df):
 out=BytesIO()
 with pd.ExcelWriter(out,engine='openpyxl') as writer:
  df.to_excel(writer,index=False)
 return out.getvalue()

FD='dati.json'
FU='utenti.json'
FP='post.json'
FI='icone.json'
FT='tip.json'
FO='odv.json'
FE='emerg.json'
FC='check.json'
FR='radio.json'
FR2='cons.json'
FPOP='popup.json'

for k,v in [
 ('dati',[]),('post',[]),('icone',[]),
 ('tip',[]),('odv',[]),('emerg',[]),
 ('check',[]),('radio',[]),('cons',[]),
 ('menu','Dashboard'),('auth',False),
 ('lat',45.8205),('lon',8.8250),
 ('com',''),('via',''),
 ('sel',-1),('zoom',16),
 ('clat',None),('clon',None),
 ('prev',-1),('exp1',False),
 ('exp2',False),('exp3',False),
 ('popup_shown',False),
 ('popup_cfg',{'titolo':'ANA VARESE - VOLONTARIATO','sottotitolo':'Sezione di Varese','mostra':True})
]:
 if k not in st.session_state:
  st.session_state[k]=v

st.session_state.dati=load(FD,[])
st.session_state.post=load(FP,[])
st.session_state.icone=load(FI,[])
st.session_state.tip=load(FT,[])
st.session_state.odv=load(FO,[])
st.session_state.emerg=load(FE,[])
st.session_state.check=load(FC,[])
st.session_state.radio=load(FR,[])
st.session_state.cons=load(FR2,[])
st.session_state.popup_cfg=load(FPOP,{'titolo':'ANA VARESE - VOLONTARIATO','sottotitolo':'Sezione di Varese','mostra':True})
uts=load(FU,[])

if not uts:
 uts=[{'username':'admin','password':hp('ana2024')}]
 save(FU,uts)
if not st.session_state.tip:
 st.session_state.tip=['Presidio','Blocco stradale','Punto ritrovo','Parcheggio','Sanitario','Logistica','Altro']
 save(FT,st.session_state.tip)
if not st.session_state.odv:
 st.session_state.odv=['ANA Varese','Protezione Civile Varese','Croce Rossa','Alpini','AIB','Altro']
 save(FO,st.session_state.odv)
if not st.session_state.icone:
 st.session_state.icone=[{'nome':'Presidio','col':'blue','file':''},{'nome':'Blocco','col':'red','file':''}]
 save(FI,st.session_state.icone)

def header():
 c1,c2=st.columns([1,5])
 with c1:
  try:
   st.image("logo.png",width=130)
  except:
   st.write("ANA")
 with c2:
  st.markdown("<div style='background:#a5d6a7;padding:15px;border-radius:8px;border:2px solid #0e7a3d;text-align:center;'><b style='color:#000;font-family:Times New Roman;font-size:28px;'>VOLONTARIATO<br>Sezione di Varese</b></div>", unsafe_allow_html=True)

def torna():
 if st.button('TORNA'):
  st.session_state.menu='Dashboard'
  st.rerun()

# POPUP INIZIALE CON TUA IMMAGINE
@st.dialog("Benvenuto - ANA Varese", width="large")
def popup_welcome():
 st.markdown(f"### {st.session_state.popup_cfg.get('titolo','ANA VARESE')}")
 st.markdown(f"**{st.session_state.popup_cfg.get('sottotitolo','Sezione di Varese')}**")
 st.divider()
 # Cerca immagine popup - copertina.jpg, benvenuto.png, tua foto
 img_found=False
 for img_name in ['copertina.jpg','copertina.png','benvenuto.jpg','benvenuto.png','popup.jpg','popup.png','mia_foto.jpg','Ezio.jpg']:
  if os.path.exists(img_name):
   try:
    st.image(img_name,use_container_width=True)
    img_found=True
    break
   except:
    pass
 if not img_found:
  # Prova logo
  if os.path.exists("logo.png"):
   st.image("logo.png",width=300)
  st.info("Carica la tua immagine come copertina.jpg su GitHub per vederla qui nel popup!")
  st.write("Puoi caricare qualsiasi foto: tua, del gruppo, del logo ANA, ecc.")
  st.write("Rinominala come copertina.jpg e caricala su GitHub")
 # Cerca anche nella cartella icone
 if os.path.exists("icone"):
  for f in os.listdir("icone"):
   if f.lower().endswith(('.jpg','.png','.jpeg')):
    if not img_found:
     try:
      st.image(os.path.join("icone",f),use_container_width=True,caption=f"Immagine: {f}")
      img_found=True
     except:
      pass
 st.divider()
 st.markdown("**Sistema Gestione Volontari ANA Varese**")
 st.write(f"Volontari: {len(st.session_state.dati)} - Postazioni: {len(st.session_state.post)}")
 st.write(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
 if st.button("ENTRA NEL SISTEMA", type="primary", use_container_width=True):
  st.session_state.popup_shown=True
  st.rerun()

if not st.session_state.auth:
 header()
 c1,c2,c3=st.columns([1,2,1])
 with c2:
  with st.form('form_login'):
   u=st.text_input('Username',value='admin')
   p=st.text_input('Password',type='password',value='ana2024')
   ok=st.form_submit_button('ACCEDI')
   if ok:
    ph=hp(p)
    for ut in uts:
     if ut['username']==u and ut['password']==ph:
      st.session_state.auth=True
      st.session_state.popup_shown=False
      st.rerun()
    st.error('Errati')
 st.stop()

# MOSTRA POPUP ALL'INIZIO SE CONFIGURATO
if st.session_state.popup_cfg.get('mostra',True) and not st.session_state.popup_shown:
 popup_welcome()

if st.session_state.exp1 or st.session_state.exp2 or st.session_state.exp3:
 st.markdown("<style>header{visibility:hidden!important;} [data-testid='stSidebar']{display:none!important;}</style>", unsafe_allow_html=True)
 if st.button('TORNA AL FORM',use_container_width=True,type='primary'):
  st.session_state.exp1=False
  st.session_state.exp2=False
  st.session_state.exp3=False
  st.rerun()
 if st.session_state.exp1:
  st.markdown('## MAPPA SCHERMO INTERO')
  lat_c=st.session_state.lat
  lon_c=st.session_state.lon
  zm=st.session_state.zoom
  if HAS:
   m=folium.Map(location=[lat_c,lon_c],zoom_start=zm,tiles='OpenStreetMap')
   for idx,p in enumerate(st.session_state.post):
    try:
     la=float(p.get('Lat','0'))
     lo=float(p.get('Lon','0'))
     ficon=p.get('IconFile','')
     if ficon and os.path.exists(ficon):
      ic=folium.CustomIcon(ficon,icon_size=(40,40))
      folium.Marker([la,lo],icon=ic).add_to(m)
     else:
      col='red' if idx==st.session_state.sel else 'blue'
      folium.Marker([la,lo],icon=folium.Icon(color=col)).add_to(m)
    except:
     pass
   if st.session_state.clat is not None:
    folium.Marker([st.session_state.clat,st.session_state.clon],icon=folium.Icon(color='green')).add_to(m)
   st_folium(m,height=850,width=1600,key='full1')
 if st.session_state.exp2:
  st.markdown('## MAPPA TUTTE SCHERMO INTERO')
  if HAS and st.session_state.post:
   m2=folium.Map(location=[45.8205,8.8250],zoom_start=11,tiles='OpenStreetMap')
   for p in st.session_state.post:
    try:
     la=float(p.get('Lat','0'))
     lo=float(p.get('Lon','0'))
     ficon=p.get('IconFile','')
     if ficon and os.path.exists(ficon):
      ic=folium.CustomIcon(ficon,icon_size=(35,35))
      folium.Marker([la,lo],icon=ic).add_to(m2)
     else:
      folium.Marker([la,lo],icon=folium.Icon(color='blue')).add_to(m2)
    except:
     pass
   st_folium(m2,height=850,width=1600,key='full2')
 if st.session_state.exp3:
  st.markdown('## ANTEPRIMA SCHERMO INTERO')
  if st.session_state.prev>=0:
   try:
    p=st.session_state.post[st.session_state.prev]
    nome=p.get('Postazione','')
    odv=p.get('ODV','')
    com=p.get('Comune','')
    st.success(f"Post: {nome}")
    st.info(f"Comune: {com} - ODV: {odv}")
    la=float(p.get('Lat','0'))
    lo=float(p.get('Lon','0'))
    if HAS:
     m3=folium.Map(location=[la,lo],zoom_start=19,tiles='OpenStreetMap')
     ficon=p.get('IconFile','')
     if ficon and os.path.exists(ficon):
      ic=folium.CustomIcon(ficon,icon_size=(50,50))
      folium.Marker([la,lo],icon=ic).add_to(m3)
     else:
      folium.Marker([la,lo],icon=folium.Icon(color='red')).add_to(m3)
     st_folium(m3,height=850,width=1600,key='full3')
   except:
    pass
  c1,c2=st.columns(2)
  with c1:
   if st.button('TORNA INDIETRO SENZA VISUALIZZARE',use_container_width=True):
    st.session_state.prev=-1
    st
