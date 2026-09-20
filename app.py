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

st.set_page_config(page_title="ANA Varese", layout="wide")

st.markdown("""
<style>
.block-container{padding-top:50px!important;max-width:100%!important;}
.stForm{background:#e8f5e9!important;border:2px solid #0e7a3d!important;}
.stForm label{color:#000!important;font-weight:bold!important;font-family:Times New Roman!important;}
.stTextInput input{color:#000!important;font-weight:bold!important;font-family:Times New Roman!important;}
.stButton>button{background:#0e7a3d!important;color:white!important;font-weight:bold!important;}
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
  r=requests.get(u,headers={'User-Agent':'ana-varese-app'},timeout=8)
  if r.status_code==200:
   j=r.json()
   a=j.get('address',{})
   # Comune - cerca in tutti i campi possibili
   com=a.get('city') or a.get('town') or a.get('village') or a.get('municipality') or a.get('hamlet') or ''
   # Via + civico
   via=a.get('road') or a.get('pedestrian') or a.get('footway') or a.get('path') or ''
   num=a.get('house_number') or ''
   full=(via+' '+num).strip()
   # Provincia per info extra
   prov=a.get('county') or ''
   if prov and com:
    com_full=com
   else:
    com_full=com
   return com_full,full
 except:
  pass
 return '',''

FD='dati.json'
FU='utenti.json'
FP='post.json'
FI='icone.json'
FT='tip.json'
FO='odv.json'

if 'dati' not in st.session_state: st.session_state.dati=[]
if 'post' not in st.session_state: st.session_state.post=[]
if 'icone' not in st.session_state: st.session_state.icone=[]
if 'tip' not in st.session_state: st.session_state.tip=[]
if 'odv' not in st.session_state: st.session_state.odv=[]
if 'menu' not in st.session_state: st.session_state.menu='Dashboard'
if 'auth' not in st.session_state: st.session_state.auth=False
if 'lat' not in st.session_state: st.session_state.lat=45.8205
if 'lon' not in st.session_state: st.session_state.lon=8.8250
if 'com' not in st.session_state: st.session_state.com=''
if 'via' not in st.session_state: st.session_state.via=''
if 'sel' not in st.session_state: st.session_state.sel=-1
if 'zoom' not in st.session_state: st.session_state.zoom=16
if 'clat' not in st.session_state: st.session_state.clat=None
if 'clon' not in st.session_state: st.session_state.clon=None
if 'prev' not in st.session_state: st.session_state.prev=-1

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
 st.session_state.tip=['Presidio','Blocco stradale','Punto ritrovo','Parcheggio','Sanitario','Logistica','Altro']
 save(FT,st.session_state.tip)
if not st.session_state.odv:
 st.session_state.odv=['ANA Varese','Protezione Civile Varese','Croce Rossa','Alpini','AIB','Altro']
 save(FO,st.session_state.odv)
if not st.session_state.icone:
 st.session_state.icone=[{'nome':'Presidio','col':'blue'},{'nome':'Blocco','col':'red'},{'nome':'Sanitario','col':'green'}]
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
 st.markdown('<b>MENU</b>', unsafe_allow_html=True)
 opts=['Dashboard','Volontari','Mappa','Libreria Icone','Backup']
 sel=st.radio('Vai a',opts,index=0)
 if sel!=st.session_state.menu:
  st.session_state.menu=sel
  st.rerun()
 st.divider()
 if st.button('LOGOUT',use_container_width=True):
  st.session_state.auth=False
  st.rerun()

scelta=st.session_state.menu

if scelta=='Dashboard':
 st.markdown('<h3 style="font-family:Times New Roman;color:#000;font-weight:bold;">DASHBOARD - MENU COMPLETO</h3>', unsafe_allow_html=True)
 c1,c2=st.columns(2)
 with c1:
  if st.button('VOLONTARI',use_container_width=True):
   st.session_state.menu='Volontari'
   st.rerun()
  if st.button('MAPPA',use_container_width=True):
   st.session_state.menu='Mappa'
   st.rerun()
 with c2:
  if st.button('LIBRERIA ICONE',use_container_width=True):
   st.session_state.menu='Libreria Icone'
   st.rerun()
  if st.button('BACKUP',use_container_width=True):
   st.session_state.menu='Backup'
   st.rerun()
 c1,c2=st.columns(2)
 c1.metric('Volontari',len(st.session_state.dati))
 c2.metric('Postazioni',len(st.session_state.post))

elif scelta=='Volontari':
 torna()
 st.markdown('<h3>VOLONTARI</h3>', unsafe_allow_html=True)
 with st.form('vol'):
  c1,c2=st.columns(2)
  with c1:
   a1=st.text_input('Nome *')
   a2=st.text_input('Cognome *')
  with c2:
   a4=st.text_input('Cellulare *')
  if st.form_submit_button('SALVA'):
   if a1 and a2:
    nc=a1+' '+a2
    st.session_state.dati.append({'Nome':nc,'Cellulare':a4})
    save(FD,st.session_state.dati)
    st.success('Salvato '+nc)
    st.rerun()
 if st.session_state.dati:
  st.dataframe(pd.DataFrame(st.session_state.dati),use_container_width=True)

elif scelta=='Mappa':
 torna()
 st.markdown('<h3>MAPPA - CLICCA DOVE VUOI - QUALSIASI COMUNE</h3>', unsafe_allow_html=True)
 st.caption('Clicca mappa - prende Comune/Via giusti dove clicchi, anche altri comuni fuori Varese')

 icon_names=[]
 for it in st.session_state.icone:
  icon_names.append(it.get('nome',''))
 sel_idx=0
 if icon_names:
  sel_str=st.selectbox('Icona libreria',icon_names,index=0)
  sel_idx=icon_names.index(sel_str)

 sel_t=st.selectbox('Tipologia',st.session_state.tip)
 new_t=st.text_input('Nuova tipologia')
 if st.button('AGGIUNGI TIPOLOGIA'):
  if new_t and new_t not in st.session_state.tip:
   st.session_state.tip.append(new_t)
   save(FT,st.session_state.tip)
   st.success('Memorizzata')
   st.rerun()

 st.divider()
 st.markdown('##### 1 - MAPPA - CLICCA - PRENDE COMUNE/VIA GIUSTI')

 lat_c=st.session_state.lat
 lon_c=st.session_state.lon
 zm=st.session_state.zoom

 if st.session_state.sel>=0:
  try:
   p=st.session_state.post[st.session_state.sel]
   lat_c=float(p.get('Lat','45.8205'))
   lon_c=float(p.get('Lon','8.8250'))
   zm=19
   st.success('Postazione: '+p.get('Postazione','')+' - ODV: '+p.get('ODV',''))
  except:
   pass

 if HAS:
  m=folium.Map(location=[lat_c,lon_c],zoom_start=zm,tiles='OpenStreetMap')
  for idx,p in enumerate(st.session_state.post):
   try:
    la=float(p.get('Lat','0'))
    lo=float(p.get('Lon','0'))
    col='red' if idx==st.session_state.sel else 'blue'
    popup_text=p.get('Postazione','')+'<br>ODV: '+p.get('ODV','')+'<br>'+p.get('Comune','')
    folium.Marker([la,lo],popup=popup_text,icon=folium.Icon(color=col)).add_to(m)
   except:
    pass
  if st.session_state.clat is not None:
   folium.Marker([st.session_state.clat,st.session_state.clon],popup='NUOVA',icon=folium.Icon(color='green')).add_to(m)
  out=st_folium(m,height=450,width=700,key='map1')
  if out and out.get('last_clicked'):
   try:
    nl=out['last_clicked']['lat']
    ng=out['last_clicked']['lng']
    st.session_state.lat=nl
    st.session_state.lon=ng
    st.session_state.clat=nl
    st.session_state.clon=ng
    com,via=gaddr(nl,ng)
    st.session_state.com=com
    st.session_state.via=via
    st.session_state.sel=-1
    st.session_state.zoom=16
    st.rerun()
   except:
    pass

 c1,c2,c3=st.columns(3)
 with c1:
  st.write('Lat: '+str(round(st.session_state.lat,6)))
 with c2:
  st.write('Comune: '+st.session_state.com)
 with c3:
  st.write('Via: '+st.session_state.via)

 st.divider()
 st.markdown('##### 2 - MASCHERA - COMUNE/VIA AUTOMATICI DOVE CLICCHI')

 vol_nomi=[]
 for d in st.session_state.dati:
  if d.get('Nome',''):
   vol_nomi.append(d.get('Nome',''))
 if not vol_nomi:
  vol_nomi=['Nessun volontario']

 with st.form('g'):
  c1,c2=st.columns(2)
  with c1:
   m1=st.text_input('Nome postazione *')
   m2=st.text_input('Comune *',value=st.session_state.com)
   m3=st.text_input('Via *',value=st.session_state.via)
   m4=st.selectbox('Tipologia *',st.session_state.tip)
   m4_new=st.text_input('Nuova tipologia extra')
  with c2:
   m5=st.text_input('Latitudine *',value=str(st.session_state.lat))
   m6=st.text_input('Longitudine *',value=str(st.session_state.lon))
   m8=st.selectbox('Responsabile',vol_nomi)
   m9=st.selectbox('ODV operante *',st.session_state.odv)
   m9_new=st.text_input('Nuova ODV operante')
  if st.form_submit_button('SALVA POSTAZIONE CON ICONA'):
   if m1:
    tf=m4_new if m4_new else m4
    if tf not in st.session_state.tip and tf:
     st.session_state.tip.append(tf)
     save(FT,st.session_state.tip)
    odv_f=m9_new if m9_new else m9
    if odv_f not in st.session_state.odv and odv_f:
     st.session_state.odv.append(odv_f)
     save(FO,st.session_state.odv)
    ic=st.session_state.icone[sel_idx] if st.session_state.icone else {'col':'blue'}
    nuovo={'Postazione':m1,'Comune':m2,'Via':m3,'Lat':m5,'Lon':m6,'Tipo':tf,'ODV':odv_f,'Col':ic.get('col','blue')}
    st.session_state.post.append(nuovo)
    save(FP,st.session_state.post)
    st.session_state.clat=None
    st.session_state.clon=None
    st.success('Salvata '+m1+' a '+m2+' - ODV '+odv_f)
    st.rerun()

 st.divider()
 st.markdown('##### 3 - MAPPA TUTTE')

 if st.session_state.post and HAS:
  m2=folium.Map(location=[45.8205,8.8250],zoom_start=11,tiles='OpenStreetMap')
  for p in st.session_state.post:
   try:
    la=float(p.get('Lat','0'))
    lo=float(p.get('Lon','0'))
    popup_text=p.get('Postazione','')+'<br>ODV: '+p.get('ODV','')+'<br>'+p.get('Comune','')
    folium.Marker([la,lo],popup=popup_text,icon=folium.Icon(color='blue')).add_to(m2)
   except:
    pass
  st_folium(m2,height=400,width=700,key='m2')

 st.divider()
 st.markdown('##### 4 - ELENCO - CLICCA VEDI ODV OPERANTE')

 if st.session_state.post:
  st.dataframe(pd.DataFrame(st.session_state.post),use_container_width=True)

  if st.session_state.prev>=0:
   try:
    p_prev=st.session_state.post[st.session_state.prev]
    st.markdown('#### ANTEPRIMA - VEDI ODV OPERANTE')
    st.success('Postazione: '+p_prev.get('Postazione',''))
    st.info('Comune: '+p_prev.get('Comune','')+' - Via: '+p_prev.get('Via','')+' - ODV OPERANTE: '+p_prev.get('ODV','')+' - Tipo: '+p_prev.get('Tipo',''))
    la_prev=float(p_prev.get('Lat','0'))
    lo_prev=float(p_prev.get('Lon','0'))
    if HAS:
     m_prev=folium.Map(location=[la_prev,lo_prev],zoom_start=19,tiles='OpenStreetMap')
     popup_text=p_prev.get('Postazione','')+'<br>ODV: '+p_prev.get('ODV','')+'<br>'+p_prev.get('Comune','')
     folium.Marker([la_prev,lo_prev],popup=popup_text,icon=folium.Icon(color='red',icon='star')).add_to(m_prev)
     st_folium(m_prev,height=350,width=700,key='mprev')
   except:
    pass

  for i,p in enumerate(st.session_state.post):
   c1,c2,c3,c4=st.columns([2,1,1,1])
   with c1:
    st.write(p.get('Postazione','')+' - '+p.get('Comune','')+' - ODV: '+p.get('ODV',''))
   with c2:
    if st.button('Vedi + ODV',key=f'vedi_{i}'):
     st.session_state.sel=i
     st.session_state.prev=i
     try:
      st.session_state.lat=float(p.get('Lat','45.8205'))
      st.session_state.lon=float(p.get('Lon','8.8250'))
      st.session_state.com=p.get('Comune','')
      st.session_state.via=p.get('Via','')
      st.session_state.zoom=19
     except:
      pass
     st.rerun()
   with c3:
    if st.button('Anteprima',key=f'ante_{i}'):
     st.session_state.prev=i
     st.rerun()
   with c4:
    lat=p.get('Lat','')
    lon=p.get('Lon','')
    st.link_button('Google',f'https://www.google.com/maps?q={lat},{lon}')

elif scelta=='Libreria Icone':
 torna()
 st.markdown('#### LIBRERIA ICONE')
 with st.form('lib'):
  n1=st.text_input('Nome icona *')
  n3=st.selectbox('Colore',['blue','red','green','orange','black'])
  if st.form_submit_button('SALVA ICONA'):
   if n1:
    st.session_state.icone.append({'nome':n1,'col':n3})
    save(FI,st.session_state.icone)
    st.success('Salvata')
    st.rerun()
 if st.session_state.icone:
  st.dataframe(pd.DataFrame(st.session_state.icone))

elif scelta=='Backup':
 torna()
 st.markdown('#### BACKUP')
 if st.button('CREA BACKUP'):
  out=BytesIO()
  with pd.ExcelWriter(out,engine='openpyxl') as writer:
   if st.session_state.post:
    pd.DataFrame(st.session_state.post).to_excel(writer,sheet_name='Mappa',index=False)
  st.session_state['bk']=out.getvalue()
 if 'bk' in st.session_state:
  st.download_button('SCARICA',st.session_state['bk'],file_name='BACKUP.xlsx')
