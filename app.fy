import streamlit as st
import pandas as pd
from io import BytesIO
import os, json, hashlib
from datetime import date, datetime

try:
 import folium
 from streamlit_folium import st_folium
 from geopy.geocoders import Nominatim
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

def reverse_geo(lat,lon):
 try:
  geo=Nominatim(user_agent='ana_varese')
  loc=geo.reverse(f'{lat},{lon}',language='it',timeout=10)
  if loc:
   addr=loc.raw.get('address',{})
   comune=addr.get('city') or addr.get('town') or addr.get('village') or ''
   via=addr.get('road') or addr.get('street') or ''
   return comune,via
 except:
  pass
 return '',''

FD='dati.json'
FU='utenti.json'
FP='post.json'
FE='eventi.json'
FR='radio.json'
FC='check.json'
FB='brog.json'
FO='consegna.json'
FM='emerg.json'

if 'dati' not in st.session_state:
 st.session_state.dati=[]
if 'post' not in st.session_state:
 st.session_state.post=[]
if 'eventi' not in st.session_state:
 st.session_state.eventi=[]
if 'radio' not in st.session_state:
 st.session_state.radio=[]
if 'check' not in st.session_state:
 st.session_state.check=[]
if 'brog' not in st.session_state:
 st.session_state.brog=[]
if 'consegna' not in st.session_state:
 st.session_state.consegna=[]
if 'emerg' not in st.session_state:
 st.session_state.emerg=[]
if 'utenti' not in st.session_state:
 st.session_state.utenti=[]
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
if 'tipo_tmp' not in st.session_state:
 st.session_state.tipo_tmp='Presidio'

st.session_state.dati=load_json(FD,[])
st.session_state.utenti=load_json(FU,[])
st.session_state.post=load_json(FP,[])
st.session_state.eventi=load_json(FE,[])
st.session_state.radio=load_json(FR,[])
st.session_state.check=load_json(FC,[])
st.session_state.brog=load_json(FB,[])
st.session_state.consegna=load_json(FO,[])
st.session_state.emerg=load_json(FM,[])

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
 st.markdown('### LOGIN')
 c1,c2,c3=st.columns([1,2,1])
 with c2:
  with st.form('a'):
   u=st.text_input('Username',value='admin')
   p=st.text_input('Password',type='password',value='ana2024')
   ok=st.form_submit_button('ACCEDI')
   if ok:
    ph=hash_pwd(p)
    trov=None
    for ut in st.session_state.utenti:
     if ut['username']==u and ut['password']==ph:
      trov=ut
    if trov:
     st.session_state.auth=True
     st.rerun()
    else:
     st.error('Errati')
 st.stop()

header()

with st.sidebar:
 opts=[
  'Dashboard',
  'Volontari',
  'Mappa',
  'Eventi',
  'Radio',
  'Check',
  'Brogliaccio',
  'Consegna',
  'Emergenze',
  'Backup'
 ]
 sel=st.radio('Vai a',opts,index=0)
 if sel!=st.session_state.menu:
  st.session_state.menu=sel
  st.rerun()
 if st.button('LOGOUT'):
  st.session_state.auth=False
  st.rerun()

scelta=st.session_state.menu

if scelta=='Dashboard':
 st.markdown('#### DASHBOARD')
 c1,c2,c3=st.columns(3)
 with c1:
  if st.button('VOLONTARI'):
   st.session_state.menu='Volontari'
   st.rerun()
  if st.button('MAPPA'):
   st.session_state.menu='Mappa'
   st.rerun()
 with c2:
  if st.button('EVENTI'):
   st.session_state.menu='Eventi'
   st.rerun()
  if st.button('RADIO'):
   st.session_state.menu='Radio'
   st.rerun()
 with c3:
  if st.button('BACKUP'):
   st.session_state.menu='Backup'
   st.rerun()

elif scelta=='Mappa':
 torna()
 st.markdown('#### MAPPA - CLICCA PER FISSARE POSTAZIONE')

 # TIPOLOGIE COMBO
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
  'Magazzino',
  'Mensa',
  'Altro'
 ]

 # ICONE PNG
 st.markdown('##### ICONE PNG SEGNA POSTAZIONE')
 ic1,ic2,ic3,ic4=st.columns(4)
 icon_files=[
  'icon_rosso.png',
  'icon_blu.png',
  'icon_verde.png',
  'icon_giallo.png'
 ]
 icon_labels=[
  'Rosso Emergenza',
  'Blu Presidio',
  'Verde Logistica',
  'Giallo Check'
 ]

 # Crea icone di default se non esistono
 # Mostra icone scaricabili
 for i,fn in enumerate(icon_files):
  with [ic1,ic2,ic3,ic4][i]:
   if os.path.exists(fn):
    st.image(fn,width=50)
    with open(fn,'rb') as f:
     st.download_button(
      f'Scarica {icon_labels[i]}',
      f.read(),
      file_name=fn,
      mime='image/png',
      key=f'dl_{i}'
     )
   else:
    st.write(icon_labels[i])
    st.write('(carica PNG)')

 st.divider()

 st.markdown('##### 1 - MAPPA CLICCABILE - ANTEPRIMA POSTAZIONI')
 st.info('Clicca sulla mappa per fissare - Comune, Via, Lat, Lon si riempiono da soli')

 col_a,col_b=st.columns([2,1])

 with col_a:
  lat_c=st.session_state.lat_tmp
  lon_c=st.session_state.lon_tmp

  if HAS_FOLIUM:
   m=folium.Map(
    location=[lat_c,lon_c],
    zoom_start=15,
    tiles='OpenStreetMap'
   )
   # Marker posizione attuale
   folium.Marker(
    [lat_c,lon_c],
    popup='Nuova postazione',
    tooltip='Posizione attuale - clicca per spostare',
    icon=folium.Icon(color='green',icon='plus')
   ).add_to(m)

   # Tutte le postazioni salvate - ANTEPRIMA
   for p in st.session_state.post:
    try:
     la=float(p.get('Lat','0'))
     lo=float(p.get('Lon','0'))
     tipo=p.get('Tipo','Presidio')
     nome=p.get('Postazione','Post')
     icona_file=p.get('Icona','')
     # Colore in base a tipologia
     col='blue'
     if tipo=='Presidio':
      col='blue'
     elif tipo=='Blocco stradale':
      col='red'
     elif tipo=='Sanitario':
      col='green'
     elif tipo=='Logistica':
      col='orange'
     folium.Marker(
      [la,lo],
      popup=f"{nome} - {tipo}",
      tooltip=f"{nome} ({tipo})",
      icon=folium.Icon(color=col)
     ).add_to(m)
    except:
     pass

   out=st_folium(m,height=450,width=700,key='map1')

   if out and out.get('last_clicked'):
    new_lat=out['last_clicked']['lat']
    new_lon=out['last_clicked']['lng']
    if abs(new_lat-lat_c)>0.000001 or abs(new_lon-lon_c)>0.000001:
     st.session_state.lat_tmp=new_lat
     st.session_state.lon_tmp=new_lon
     # Reverse geocoding per Comune e Via
     com,via=reverse_geo(new_lat,new_lon)
     if com:
      st.session_state.com_tmp=com
     if via:
      st.session_state.via_tmp=via
     st.rerun()
  else:
   st.warning('Manca folium - installa da requirements.txt')
   df_ante=pd.DataFrame({'lat':[lat_c],'lon':[lon_c]})
   st.map(df_ante,zoom=15)

 with col_b:
  st.markdown('**Dati dal click**')
  st.write('Clicca sulla mappa OSM')
  st.write('I campi si riempiono sotto')
  st.divider()
  st.write(f"Lat: {st.session_state.lat_tmp:.6f}")
  st.write(f"Lon: {st.session_state.lon_tmp:.6f}")
  st.write(f"Comune: {st.session_state.com_tmp}")
  st.write(f"Via: {st.session_state.via_tmp}")
  if st.button('CENTRA VARESE'):
   st.session_state.lat_tmp=45.8205
   st.session_state.lon_tmp=8.8250
   st.session_state.com_tmp='Varese'
   st.session_state.via_tmp=''
   st.rerun()

 st.divider()
 st.markdown('##### 2 - MASCHERA - CAMPI RIEMPITI AUTOMATICAMENTE')

 with st.form('g'):
  st.markdown('**Dati postazione - si riempiono dal click**')
  c1,c2=st.columns(2)
  with c1:
   m1=st.text_input('Nome postazione *',value='')
   m2=st.text_input('Comune *',value=st.session_state.com_tmp,key='com')
   m3=st.text_input('Via *',value=st.session_state.via_tmp,key='via')
   # TIPOLOGIA COMBO
   m7=st.selectbox('Tipologia *',tipi,index=0,key='tipo_sel')
  with c2:
   m5=st.text_input('Latitudine *',value=str(st.session_state.lat_tmp),key='lat')
   m6=st.text_input('Longitudine *',value=str(st.session_state.lon_tmp),key='lon')
   m8=st.text_input('Responsabile',value='')
   # ICONA PNG SELEZIONE
   icon_choice=st.selectbox('Icona PNG',icon_labels+['Nessuna','Carica PNG'],key='icon_sel')
   m9=st.text_area('Note',value='')

  st.markdown('**Carica icona PNG personalizzata**')
  up_icon=st.file_uploader('Carica PNG per segna postazione',type=['png','jpg','jpeg'],key='up_icon')
  icon_name=''
  if up_icon:
   icon_name=up_icon.name
   st.image(up_icon,width=60)
   # Salva icona
   with open(icon_name,'wb') as f:
    f.write(up_icon.getbuffer())
   st.success(f'Icona {icon_name} salvata')

  ok=st.form_submit_button('SALVA POSTAZIONE')
  if ok and m1:
   nuovo={}
   nuovo['Postazione']=m1
   nuovo['Comune']=m2
   nuovo['Via']=m3
   nuovo['Lat']=m5
   nuovo['Lon']=m6
   nuovo['Tipo']=m7
   nuovo['Icona']=icon_choice
   if icon_name:
    nuovo['Icona']=icon_name
   nuovo['Resp']=m8
   nuovo['Note']=m9
   st.session_state.post.append(nuovo)
   save_json(FP,st.session_state.post)
   st.success(f'Salvata {m1} - {m2} {m3}')
   st.rerun()

 st.divider()
 st.markdown('##### 3 - ANTEPRIMA MAPPA CON TUTTE LE POSTAZIONI')

 if st.session_state.post:
  if HAS_FOLIUM:
   m2=folium.Map(
    location=[45.8205,8.8250],
    zoom_start=12,
    tiles='OpenStreetMap'
   )
   for p in st.session_state.post:
    try:
     la=float(p.get('Lat','0'))
     lo=float(p.get('Lon','0'))
     nome=p.get('Postazione','')
     tipo=p.get('Tipo','')
     folium.Marker(
      [la,lo],
      popup=f"{nome} - {tipo}",
      tooltip=nome
     ).add_to(m2)
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

  for p in st.session_state.post:
   lat=p.get('Lat','45.8205')
   lon=p.get('Lon','8.8250')
   nome=p.get('Postazione','Post')
   st.write(f"**{nome}** {lat},{lon}")
   c1,c2,c3=st.columns(3)
   with c1:
    osm=f'https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=18/{lat}/{lon}'
    st.link_button('OSM',osm)
   with c2:
    gmap=f'https://www.google.com/maps?q={lat},{lon}'
    st.link_button('Google',gmap)
   with c3:
    waze=f'https://waze.com/ul?ll={lat},{lon}'
    st.link_button('Waze',waze)
 else:
  st.info('Nessuna postazione - clicca sulla mappa sopra')

elif scelta=='Volontari':
 torna()
 st.markdown('#### VOLONTARI')
 if st.session_state.dati:
  st.dataframe(pd.DataFrame(st.session_state.dati))

else:
 torna()
 st.markdown(f'#### {scelta}')
 st.info(f'Sezione {scelta}')
