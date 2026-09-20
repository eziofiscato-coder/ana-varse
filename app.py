import streamlit as st
import pandas as pd
from io import BytesIO
import os, json, hashlib, requests

try:
 import folium
 from streamlit_folium import st_folium
 HAS=True
except:
 HAS=False

st.set_page_config(
 page_title="ANA Varese",
 layout="wide"
)

st.markdown("""
<style>
.block-container{
 padding-top:50px!important;
}
.stForm{
 background:#e8f5e9!important;
 border:2px solid #0e7a3d!important;
}
.stForm label{
 color:#000!important;
 font-weight:bold!important;
 font-family:Times New Roman!important;
}
.stButton>button{
 background:#0e7a3d!important;
 color:white!important;
 font-weight:bold!important;
}
</style>
""", unsafe_allow_html=True)

def load(f,d):
 try:
  if os.path.exists(f):
   with open(f,'r') as fh:
    return json.load(fh)
 except:
  pass
 return d

def save(f,d):
 try:
  with open(f,'w') as fh:
   json.dump(d,fh,indent=2)
 except:
  pass

def hp(p):
 return hashlib.sha256(p.encode()).hexdigest()

def addr(lat,lon):
 try:
  u=f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=jsonv2&accept-language=it"
  r=requests.get(u,headers={'User-Agent':'ana'},timeout=6)
  if r.status_code==200:
   j=r.json()
   a=j.get('address',{})
   com=a.get('city') or a.get('town') or ''
   via=a.get('road') or ''
   return com,via
 except:
  pass
 return '',''

FD='dati.json'
FU='utenti.json'
FP='post.json'
FI='icone.json'
FT='tip.json'
FO='odv.json'

if 'dati' not in st.session_state:
 st.session_state.dati=[]
if 'post' not in st.session_state:
 st.session_state.post=[]
if 'icone' not in st.session_state:
 st.session_state.icone=[]
if 'tip' not in st.session_state:
 st.session_state.tip=[]
if 'odv' not in st.session_state:
 st.session_state.odv=[]
if 'menu' not in st.session_state:
 st.session_state.menu='Dashboard'
if 'auth' not in st.session_state:
 st.session_state.auth=False
if 'lat' not in st.session_state:
 st.session_state.lat=45.8205
if 'lon' not in st.session_state:
 st.session_state.lon=8.8250
if 'com' not in st.session_state:
 st.session_state.com=''
if 'via' not in st.session_state:
 st.session_state.via=''
if 'sel' not in st.session_state:
 st.session_state.sel=-1
if 'zoom' not in st.session_state:
 st.session_state.zoom=16
if 'clat' not in st.session_state:
 st.session_state.clat=None
if 'clon' not in st.session_state:
 st.session_state.clon=None
if 'prev' not in st.session_state:
 st.session_state.prev=-1

st.session_state.dati=load(FD,[])
st.session_state.post=load(FP,[])
st.session_state.icone=load(FI,[])
st.session_state.tip=load(FT,[])
st.session_state.odv=load(FO,[])
uts=load(FU,[])

if not uts:
 uts=[{'username':'admin','password':hp('ana2024')}]
 save(FU,uts)
if not st.session_state.tip:
 st.session_state.tip=['Presidio','Blocco','Ritrovo','Altro']
 save(FT,st.session_state.tip)
if not st.session_state.odv:
 st.session_state.odv=['ANA Varese','Prot Civile','Altro']
 save(FO,st.session_state.odv)
if not st.session_state.icone:
 st.session_state.icone=[{'nome':'Presidio','col':'blue'}]
 save(FI,st.session_state.icone)

def header():
 c1,c2=st.columns([1,5])
 with c1:
  try:
   st.image("logo.png",width=130)
  except:
   st.write("ANA")
 with c2:
  st.markdown("<div style='background:#a5d6a7;padding:15px;border:2px solid #0e7a3d;text-align:center;'><b style='color:#000;font-family:Times New Roman;font-size:28px;'>VOLONTARIATO<br>Sezione di Varese</b></div>", unsafe_allow_html=True)

def torna():
 if st.button('TORNA'):
  st.session_state.menu='Dashboard'
  st.rerun()

if not st.session_state.auth:
 header()
 c1,c2,c3=st.columns([1,2,1])
 with c2:
  with st.form('login'):
   u=st.text_input('Username',value='admin')
   p=st.text_input('Password',type='password',value='ana2024')
   ok=st.form_submit_button('ACCEDI')
   if ok:
    ph=hp(p)
    for ut in uts:
     if ut['username']==u and ut['password']==ph:
      st.session_state.auth=True
      st.rerun()
    st.error('Errati')
 st.stop()

header()

with st.sidebar:
 st.write('MENU')
 opts=['Dashboard','Volontari','Mappa']
 sel=st.radio('Vai a',opts,index=0)
 if sel!=st.session_state.menu:
  st.session_state.menu=sel
  st.rerun()
 if st.button('LOGOUT'):
  st.session_state.auth=False
  st.rerun()

scelta=st.session_state.menu

if scelta=='Dashboard':
 st.metric('Volontari',len(st.session_state.dati))
 st.metric('Postazioni',len(st.session_state.post))
 if st.button('MAPPA'):
  st.session_state.menu='Mappa'
  st.rerun()

elif scelta=='Volontari':
 torna()
 with st.form('vol'):
  a1=st.text_input('Nome')
  a2=st.text_input('Cognome')
  a4=st.text_input('Cellulare')
  if st.form_submit_button('SALVA'):
   if a1 and a2:
    nc=a1+' '+a2
    st.session_state.dati.append({'Nome':nc})
    save(FD,st.session_state.dati)
    st.success('Salvato')
    st.rerun()
 if st.session_state.dati:
  st.dataframe(pd.DataFrame(st.session_state.dati))

elif scelta=='Mappa':
 torna()
 st.write('CLICCA MAPPA - ASSOCIA VIA COMUNE LAT LON')
 
 tip=st.session_state.tip
 sel_tip=st.selectbox('Tipologia',tip)
 
 lat_c=st.session_state.lat
 lon_c=st.session_state.lon
 zm=st.session_state.zoom
 
 if st.session_state.sel>=0:
  try:
   p=st.session_state.post[st.session_state.sel]
   lat_c=float(p.get('Lat','45.8205'))
   lon_c=float(p.get('Lon','8.8250'))
   zm=19
  except:
   pass

 if HAS:
  m=folium.Map(
   location=[lat_c,lon_c],
   zoom_start=zm,
   tiles='OpenStreetMap'
  )
  for idx,p in enumerate(st.session_state.post):
   try:
    la=float(p.get('Lat','0'))
    lo=float(p.get('Lon','0'))
    col='red' if idx==st.session_state.sel else 'blue'
    folium.Marker(
     [la,lo],
     popup=p.get('Postazione',''),
     icon=folium.Icon(color=col)
    ).add_to(m)
   except:
    pass
  if st.session_state.clat is not None:
   folium.Marker(
    [st.session_state.clat,st.session_state.clon],
    popup='NUOVA',
    icon=folium.Icon(color='green')
   ).add_to(m)
  out=st_folium(m,height=450,width=700,key='map1')
  if out and out.get('last_clicked'):
   try:
    nl=out['last_clicked']['lat']
    ng=out['last_clicked']['lng']
    st.session_state.lat=nl
    st.session_state.lon=ng
    st.session_state.clat=nl
    st.session_state.clon=ng
    com,via=addr(nl,ng)
    st.session_state.com=com
    st.session_state.via=via
    st.session_state.sel=-1
    st.session_state.zoom=16
    st.rerun()
   except:
    pass

 c1,c2,c3=st.columns(3)
 with c1:
  st.write('Lat')
  st.write(str(round(st.session_state.lat,6)))
 with c2:
  st.write('Comune')
  st.write(st.session_state.com)
 with c3:
  st.write('Via')
  st.write(st.session_state.via)

 with st.form('g'):
  m1=st.text_input('Nome postazione')
  m2=st.text_input('Comune',value=st.session_state.com)
  m3=st.text_input('Via',value=st.session_state.via)
  m5=st.text_input('Lat',value=str(st.session_state.lat))
  m6=st.text_input('Lon',value=str(st.session_state.lon))
  m9=st.selectbox('ODV',st.session_state.odv)
  if st.form_submit_button('SALVA'):
   if m1:
    nuovo={
     'Postazione':m1,
     'Comune':m2,
     'Via':m3,
     'Lat':m5,
     'Lon':m6,
     'ODV':m9
    }
    st.session_state.post.append(nuovo)
    save(FP,st.session_state.post)
    st.session_state.clat=None
    st.session_state.clon=None
    st.success('Salvata')
    st.rerun()

 if st.session_state.post:
  st.dataframe(pd.DataFrame(st.session_state.post))
  for i,p in enumerate(st.session_state.post):
   c1,c2=st.columns([3,1])
   with c1:
    st.write(p.get('Postazione',''))
   with c2:
    if st.button('Vedi',key=f'v{i}'):
     st.session_state.sel=i
     try:
      st.session_state.lat=float(p.get('Lat','0'))
      st.session_state.lon=float(p.get('Lon','0'))
      st.session_state.com=p.get('Comune','')
      st.session_state.via=p.get('Via','')
      st.session_state.zoom=19
     except:
      pass
     st.rerun()
