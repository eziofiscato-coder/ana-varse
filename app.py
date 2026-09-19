import streamlit as st
import pandas as pd
from io import BytesIO
import os, json, hashlib
from datetime import date, datetime

try:
 import folium
 from streamlit_folium import st_folium
 HAS_FOLIUM=True
except:
 HAS_FOLIUM=False

st.set_page_config(page_title='ANA Varese', layout='wide')

st.markdown("""
<style>
.block-container{padding-top:8px!important;}
.stForm{
 background:#e8f5e9!important;
 border:2px solid #2e7d32!important;
 border-radius:8px!important;
 padding:8px!important;
}
.stButton>button{
 background:#2e7d32!important;
 color:white!important;
}
</style>
""", unsafe_allow_html=True)

def load_json(f,d):
 try:
  if os.path.exists(f):
   with open(f,'r',encoding='utf-8') as fh:
    return json.load(fh)
 except:
  pass
 return d

def save_json(f,d):
 try:
  with open(f,'w',encoding='utf-8') as fh:
   json.dump(d,fh,indent=2)
 except:
  pass

def hash_pwd(p):
 return hashlib.sha256(p.encode()).hexdigest()

FD='dati.json'
FU='utenti.json'
FP='post.json'

if 'dati' not in st.session_state:
 st.session_state.dati=[]
if 'post' not in st.session_state:
 st.session_state.post=[]
if 'menu' not in st.session_state:
 st.session_state.menu='Dashboard'
if 'auth' not in st.session_state:
 st.session_state.auth=False
if 'lat_tmp' not in st.session_state:
 st.session_state.lat_tmp=45.8205
if 'lon_tmp' not in st.session_state:
 st.session_state.lon_tmp=8.8250
if 'com_tmp' not in st.session_state:
 st.session_state.com_tmp='Varese'
if 'via_tmp' not in st.session_state:
 st.session_state.via_tmp=''

st.session_state.dati=load_json(FD,[])
st.session_state.post=load_json(FP,[])
st.session_state.utenti=load_json(FU,[])

if not st.session_state.utenti:
 st.session_state.utenti=[
  {'username':'admin','password':hash_pwd('ana2024')}
 ]
 save_json(FU,st.session_state.utenti)

def header():
 st.markdown(
  "<div style='text-align:center;background:#a5d6a7;padding:5px;border-radius:8px;border:2px solid #2e7d32;'><b style='color:#0e7a3d;'>VOLONTARIATO Varese</b></div>",
  unsafe_allow_html=True
 )

def torna():
 if st.button('TORNA'):
  st.session_state.menu='Dashboard'
  st.rerun()

if not st.session_state.auth:
 header()
 c1,c2,c3=st.columns([1,2,1])
 with c2:
  with st.form('a'):
   u=st.text_input('Username',value='admin')
   p=st.text_input('Password',type='password',value='ana2024')
   ok=st.form_submit_button('ACCEDI')
   if ok:
    ph=hash_pwd(p)
    for ut in st.session_state.utenti:
     if ut['username']==u and ut['password']==ph:
      st.session_state.auth=True
      st.rerun()
    st.error('Errati')
 st.stop()

header()

with st.sidebar:
 opts=['Dashboard','Volontari','Mappa','Backup']
 sel=st.radio('Vai a',opts,index=0)
 if sel!=st.session_state.menu:
  st.session_state.menu=sel
  st.rerun()

scelta=st.session_state.menu

if scelta=='Dashboard':
 st.markdown('#### DASHBOARD')
 if st.button('MAPPA'):
  st.session_state.menu='Mappa'
  st.rerun()

elif scelta=='Volontari':
 torna()
 st.markdown('#### VOLONTARI')
 if st.session_state.dati:
  st.dataframe(pd.DataFrame(st.session_state.dati))

elif scelta=='Mappa':
 torna()
 st.markdown('#### MAPPA - CLICCA PER FISSARE')

 tipi=[
  'Presidio',
  'Blocco stradale',
  'Punto ritrovo',
  'Area emergenza',
  'Parcheggio',
  'Segreteria',
  'Radio',
  'Sanitario',
  'Logistica',
  'Mensa',
  'Altro'
 ]

 icons=['Rosso','Blu','Verde','Giallo','Nessuna']

 st.markdown('##### ICONE PNG')
 c1,c2,c3,c4=st.columns(4)
 for i,lab in enumerate(icons[:4]):
  with [c1,c2,c3,c4][i]:
   fn=f'icon_{lab.lower()}.png'
   if os.path.exists(fn):
    st.image(fn,width=40)
    with open(fn,'rb') as f:
     st.download_button(f'Scarica {lab}',f.read(),file_name=fn,key=f'd{i}')

 st.divider()
 st.markdown('##### 1 - MAPPA CLICCABILE - ANTEPRIMA')
 st.info('Clicca sulla mappa - Comune Via Lat Lon si riempiono')

 col_a,col_b=st.columns([2,1])
 with col_a:
  lat_c=st.session_state.lat_tmp
  lon_c=st.session_state.lon_tmp

  lat_man=st.number_input('Lat',value=float(lat_c),format='%.6f',key='lat1')
  lon_man=st.number_input('Lon',value=float(lon_c),format='%.6f',key='lon1')
  st.session_state.lat_tmp=lat_man
  st.session_state.lon_tmp=lon_man

  if HAS_FOLIUM:
   m=folium.Map(location=[lat_man,lon_man],zoom_start=16,tiles='OpenStreetMap')
   folium.Marker([lat_man,lon_man],popup='Nuova',tooltip='Clicca per spostare',icon=folium.Icon(color='green',icon='plus')).add_to(m)
   for p in st.session_state.post:
    try:
     la=float(p.get('Lat','0'))
     lo=float(p.get('Lon','0'))
     nome=p.get('Postazione','')
     tipo=p.get('Tipo','')
     folium.Marker([la,lo],popup=f'{nome} {tipo}',tooltip=nome,icon=folium.Icon(color='blue')).add_to(m)
    except:
     pass
   out=st_folium(m,height=400,width=700,key='map1')
   if out and out.get('last_clicked'):
    new_lat=out['last_clicked']['lat']
    new_lon=out['last_clicked']['lng']
    if abs(new_lat-lat_man)>0.000001:
     st.session_state.lat_tmp=new_lat
     st.session_state.lon_tmp=new_lon
     st.rerun()
  else:
   df_ante=pd.DataFrame({'lat':[lat_man],'lon':[lon_man]})
   st.map(df_ante,zoom=15)

 with col_b:
  st.write('1 - Clicca mappa')
  st.write('2 - Campi si riempiono')
  st.write('3 - Salva sotto')
  if st.button('CENTRA VARESE'):
   st.session_state.lat_tmp=45.8205
   st.session_state.lon_tmp=8.8250
   st.session_state.com_tmp='Varese'
   st.session_state.via_tmp=''
   st.rerun()

 st.divider()
 st.markdown('##### 2 - MASCHERA - RIEMPIE DA MAPPA')

 with st.form('b'):
  c1,c2=st.columns(2)
  with c1:
   m1=st.text_input('Nome postazione *')
   m2=st.text_input('Comune *',value=st.session_state.com_tmp)
   m3=st.text_input('Via *',value=st.session_state.via_tmp)
   m7=st.selectbox('Tipologia *',tipi,index=0)
  with c2:
   m5=st.text_input('Latitudine *',value=str(st.session_state.lat_tmp))
   m6=st.text_input('Longitudine *',value=str(st.session_state.lon_tmp))
   m8=st.text_input('Responsabile')
   m9=st.selectbox('Icona PNG',icons,index=0)
   m10=st.text_area('Note')

  up=st.file_uploader('Carica PNG icona',type=['png'])
  if up:
   st.image(up,width=60)

  ok=st.form_submit_button('SALVA POSTAZIONE')
  if ok and m1:
   nuovo={}
   nuovo['Postazione']=m1
   nuovo['Comune']=m2
   nuovo['Via']=m3
   nuovo['Lat']=m5
   nuovo['Lon']=m6
   nuovo['Tipo']=m7
   nuovo['Icona']=m9
   nuovo['Resp']=m8
   nuovo['Note']=m10
   st.session_state.post.append(nuovo)
   save_json(FP,st.session_state.post)
   st.success(f'Salvata {m1}')
   st.rerun()

 st.divider()
 st.markdown('##### 3 - ANTEPRIMA MAPPA CON POSTAZIONI')

 if st.session_state.post:
  if HAS_FOLIUM:
   m2=folium.Map(location=[45.8205,8.8250],zoom_start=12,tiles='OpenStreetMap')
   for p in st.session_state.post:
    try:
     la=float(p.get('Lat','0'))
     lo=float(p.get('Lon','0'))
     nome=p.get('Postazione','')
     folium.Marker([la,lo],popup=nome,tooltip=nome).add_to(m2)
    except:
     pass
   st_folium(m2,height=400,width=700,key='map2')
  else:
   try:
    df_all=pd.DataFrame(st.session_state.post)
    df_all['lat']=pd.to_numeric(df_all['Lat'],errors='coerce')
    df_all['lon']=pd.to_numeric(df_all['Lon'],errors='coerce')
    df_all=df_all.dropna(subset=['lat','lon'])
    if not df_all.empty:
     st.map(df_all[['lat','lon']])
   except:
    pass
  st.dataframe(pd.DataFrame(st.session_state.post))
 else:
  st.info('Nessuna postazione')

elif scelta=='Backup':
 torna()
 st.markdown('#### BACKUP')
 if st.button('CREA BACKUP'):
  out=BytesIO()
  with pd.ExcelWriter(out,engine='openpyxl') as writer:
   if st.session_state.dati:
    pd.DataFrame(st.session_state.dati).to_excel(writer,sheet_name='Vol',index=False)
   if st.session_state.post:
    pd.DataFrame(st.session_state.post).to_excel(writer,sheet_name='Mappa',index=False)
  st.session_state['bk']=out.getvalue()
 if 'bk' in st.session_state:
  st.download_button('SCARICA',st.session_state['bk'],file_name='BACKUP.xlsx')
