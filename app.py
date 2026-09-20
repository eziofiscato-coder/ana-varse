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
  r=requests.get(u,headers={'User-Agent':'ana-varese'},timeout=8)
  if r.status_code==200:
   j=r.json()
   a=j.get('address',{})
   com=a.get('city') or a.get('town') or a.get('village') or a.get('municipality') or ''
   via=a.get('road') or ''
   num=a.get('house_number') or ''
   full=(via+' '+num).strip()
   return com,full
 except:
  pass
 return '',''

FD='dati.json'
FU='utenti.json'
FP='post.json'
FI='icone.json'
FT='tip.json'
FO='odv.json'
FE='emergenze.json'
FC='checkin.json'
FR='radio.json'
FR2='consegna_radio.json'

for k,v in [('dati',[]),('post',[]),('icone',[]),('tip',[]),('odv',[]),('emerg',[]),('checkin',[]),('radio',[]),('consegna',[]),('menu','Dashboard'),('auth',False),('lat',45.8205),('lon',8.8250),('com',''),('via',''),('sel',-1),('zoom',16),('clat',None),('clon',None),('prev',-1),('exp_main',False),('exp_all',False),('exp_prev',False)]:
 if k not in st.session_state:
  st.session_state[k]=v

st.session_state.dati=load(FD,[])
st.session_state.post=load(FP,[])
st.session_state.icone=load(FI,[])
st.session_state.tip=load(FT,[])
st.session_state.odv=load(FO,[])
st.session_state.emerg=load(FE,[])
st.session_state.checkin=load(FC,[])
st.session_state.radio=load(FR,[])
st.session_state.consegna=load(FR2,[])
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

if st.session_state.exp_main or st.session_state.exp_all or st.session_state.exp_prev:
 st.markdown("<style>header{visibility:hidden!important;} [data-testid='stSidebar']{display:none!important;}</style>", unsafe_allow_html=True)
 if st.button('TORNA AL FORM',use_container_width=True,type='primary'):
  st.session_state.exp_main=False
  st.session_state.exp_all=False
  st.session_state.exp_prev=False
  st.rerun()
 if st.session_state.exp_main:
  st.markdown('## MAPPA INSERIMENTO - SCHERMO INTERO')
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
   m=folium.Map(location=[lat_c,lon_c],zoom_start=zm,tiles='OpenStreetMap')
   for idx,p in enumerate(st.session_state.post):
    try:
     la=float(p.get('Lat','0'))
     lo=float(p.get('Lon','0'))
     file_icon=p.get('IconFile','')
     if file_icon and os.path.exists(file_icon):
      icon=folium.CustomIcon(file_icon,icon_size=(40,40))
      folium.Marker([la,lo],popup=p.get('Postazione','')+'<br>ODV: '+p.get('ODV',''),icon=icon).add_to(m)
     else:
      col='red' if idx==st.session_state.sel else 'blue'
      folium.Marker([la,lo],popup=p.get('Postazione',''),icon=folium.Icon(color=col)).add_to(m)
    except:
     pass
   if st.session_state.clat is not None:
    folium.Marker([st.session_state.clat,st.session_state.clon],popup='NUOVA',icon=folium.Icon(color='green')).add_to(m)
   st_folium(m,height=850,width=1600,key='m_main_full')
 if st.session_state.exp_all:
  st.markdown('## MAPPA TUTTE - SCHERMO INTERO')
  if HAS and st.session_state.post:
   m2=folium.Map(location=[45.8205,8.8250],zoom_start=12,tiles='OpenStreetMap')
   for p in st.session_state.post:
    try:
     la=float(p.get('Lat','0'))
     lo=float(p.get('Lon','0'))
     file_icon=p.get('IconFile','')
     if file_icon and os.path.exists(file_icon):
      icon=folium.CustomIcon(file_icon,icon_size=(35,35))
      folium.Marker([la,lo],popup=p.get('Postazione',''),icon=icon).add_to(m2)
     else:
      folium.Marker([la,lo],popup=p.get('Postazione',''),icon=folium.Icon(color='blue')).add_to(m2)
    except:
     pass
   st_folium(m2,height=850,width=1600,key='m_all_full')
 if st.session_state.exp_prev:
  st.markdown('## ANTEPRIMA - SCHERMO INTERO')
  if st.session_state.prev>=0:
   try:
    p=st.session_state.post[st.session_state.prev]
    st.success('Postazione: '+p.get('Postazione','')+' - ODV: '+p.get('ODV',''))
    la=float(p.get('Lat','0'))
    lo=float(p.get('Lon','0'))
    if HAS:
     m3=folium.Map(location=[la,lo],zoom_start=19,tiles='OpenStreetMap')
     file_icon=p.get('IconFile','')
     if file_icon and os.path.exists(file_icon):
      icon=folium.CustomIcon(file_icon,icon_size=(50,50))
      folium.Marker([la,lo],popup=p.get('Postazione',''),icon=icon).add_to(m3)
     else:
      folium.Marker([la,lo],popup=p.get('Postazione',''),icon=folium.Icon(color='red',icon='star')).add_to(m3)
     st_folium(m3,height=850,width=1600,key='m_prev_full')
   except:
    pass
  c1,c2=st.columns(2)
  with c1:
   if st.button('TORNA INDIETRO SENZA VISUALIZZARE',use_container_width=True):
    st.session_state.prev=-1
    st.session_state.sel=-1
    st.session_state.exp_prev=False
    st.rerun()
  with c2:
   if st.button('CHIUDI ANTEPRIMA',use_container_width=True,type='primary'):
    st.session_state.exp_prev=False
    st.rerun()
else:
 header()
 with st.sidebar:
  st.markdown('<b>MENU COMPLETO</b>', unsafe_allow_html=True)
  opts=['Dashboard','Volontari','Mappa','Libreria Icone','Emergenza','Check In','DB Radio','Consegna Radio','Backup']
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
  st.markdown('<h3 style="font-family:Times New Roman;color:#000;font-weight:bold;">DASHBOARD - MENU COMPLETO TUTTI I FORM</h3>', unsafe_allow_html=True)
  st.info('Menu completo emergenza')
  c1,c2,c3=st.columns(3)
  with c1:
   if st.button('VOLONTARI',use_container_width=True):
    st.session_state.menu='Volontari'
    st.rerun()
   if st.button('MAPPA',use_container_width=True):
    st.session_state.menu='Mappa'
    st.rerun()
   if st.button('EMERGENZA',use_container_width=True):
    st.session_state.menu='Emergenza'
    st.rerun()
  with c2:
   if st.button('CHECK IN',use_container_width=True):
    st.session_state.menu='Check In'
    st.rerun()
   if st.button('DB RADIO',use_container_width=True):
    st.session_state.menu='DB Radio'
    st.rerun()
   if st.button('CONSEGNA RADIO',use_container_width=True):
    st.session_state.menu='Consegna Radio'
    st.rerun()
  with c3:
   if st.button('LIBRERIA ICONE',use_container_width=True):
    st.session_state.menu='Libreria Icone'
    st.rerun()
   if st.button('BACKUP',use_container_width=True):
    st.session_state.menu='Backup'
    st.rerun()
   st.metric('Volontari',len(st.session_state.dati))
   st.metric('Postazioni',len(st.session_state.post))
  st.divider()
  st.markdown('### TUTTI I FORM')
  st.write('1. Volontari')
  st.write('2. Mappa - Comune/Via automatici + ODV + Icona PNG su mappa e tabella')
  st.write('3. Libreria Icone - upload PNG')
  st.write('4. Emergenza')
  st.write('5. Check In')
  st.write('6. DB Radio')
  st.write('7. Consegna Radio - consegna radio ai volontari')
  st.write('8. Backup')

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
   if st.form_submit_button('SALVA VOLONTARIO'):
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
  st.markdown('<h3>MAPPA - ICONA PNG SU MAPPA E TABELLA</h3>', unsafe_allow_html=True)

  icon_names=[]
  for it in st.session_state.icone:
   icon_names.append(it.get('nome',''))
  sel_idx=0
  if icon_names:
   sel_str=st.selectbox('Seleziona icona PNG da libreria',icon_names,index=0)
   sel_idx=icon_names.index(sel_str)
   # Mostra anteprima icona selezionata
   try:
    ic_sel=st.session_state.icone[sel_idx]
    if ic_sel.get('file','') and os.path.exists(ic_sel.get('file','')):
     st.image(ic_sel.get('file',''),width=60,caption='Icona selezionata: '+ic_sel.get('nome',''))
    else:
     st.caption('Icona colore: '+ic_sel.get('col',''))
   except:
    pass

  sel_t=st.selectbox('Tipologia',st.session_state.tip)
  new_t=st.text_input('Nuova tipologia')
  if st.button('AGGIUNGI TIPOLOGIA'):
   if new_t and new_t not in st.session_state.tip:
    st.session_state.tip.append(new_t)
    save(FT,st.session_state.tip)
    st.success('Memorizzata')
    st.rerun()

  st.divider()
  st.markdown('##### 1 - MAPPA - CLICCA DOVE VUOI - METTE ICONA PNG SCELTA')
  c1,c2=st.columns([3,1])
  with c2:
   if st.button('ESPANDI SCHERMO INTERO',use_container_width=True,key='e1'):
    st.session_state.exp_main=True
    st.rerun()

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
   m=folium.Map(location=[lat_c,lon_c],zoom_start=zm,tiles='OpenStreetMap')
   for idx,p in enumerate(st.session_state.post):
    try:
     la=float(p.get('Lat','0'))
     lo=float(p.get('Lon','0'))
     file_icon=p.get('IconFile','')
     if file_icon and os.path.exists(file_icon):
      icon=folium.CustomIcon(file_icon,icon_size=(40,40))
      folium.Marker([la,lo],popup=p.get('Postazione','')+'<br>ODV: '+p.get('ODV',''),icon=icon).add_to(m)
     else:
      col='red' if idx==st.session_state.sel else 'blue'
      folium.Marker([la,lo],popup=p.get('Postazione',''),icon=folium.Icon(color=col)).add_to(m)
    except:
     pass
   if st.session_state.clat is not None:
    # Mostra icona selezionata dove clicchi
    try:
     ic_tmp=st.session_state.icone[sel_idx]
     file_tmp=ic_tmp.get('file','')
     if file_tmp and os.path.exists(file_tmp):
      icon=folium.CustomIcon(file_tmp,icon_size=(40,40))
      folium.Marker([st.session_state.clat,st.session_state.clon],popup='NUOVA CON ICONA PNG',icon=icon).add_to(m)
     else:
      folium.Marker([st.session_state.clat,st.session_state.clon],popup='NUOVA',icon=folium.Icon(color='green')).add_to(m)
    except:
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
  st.markdown('##### 2 - MASCHERA - CON ICONA PNG')

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
   with c2:
    m5=st.text_input('Latitudine *',value=str(st.session_state.lat))
    m6=st.text_input('Longitudine *',value=str(st.session_state.lon))
    m8=st.selectbox('Responsabile',vol_nomi)
    m9=st.selectbox('ODV operante *',st.session_state.odv)
    m9_new=st.text_input('Nuova ODV operante')
   if st.form_submit_button('SALVA POSTAZIONE CON ICONA PNG'):
    if m1:
     odv_f=m9_new if m9_new else m9
     if odv_f not in st.session_state.odv and odv_f:
      st.session_state.odv.append(odv_f)
      save(FO,st.session_state.odv)
     ic=st.session_state.icone[sel_idx] if st.session_state.icone else {'col':'blue','file':''}
     nuovo={'Postazione':m1,'Comune':m2,'Via':m3,'Lat':m5,'Lon':m6,'ODV':odv_f,'Col':ic.get('col','blue'),'Icona':ic.get('nome',''),'IconFile':ic.get('file','')}
     st.session_state.post.append(nuovo)
     save(FP,st.session_state.post)
     st.session_state.clat=None
     st.session_state.clon=None
     st.success('Salvata '+m1+' con icona PNG '+ic.get('nome','')+' a '+m2)
     st.rerun()

  st.divider()
  st.markdown('##### 3 - MAPPA TUTTE')
  c1,c2=st.columns([3,1])
  with c2:
   if st.button('ESPANDI SCHERMO INTERO',use_container_width=True,key='e2'):
    st.session_state.exp_all=True
    st.rerun()
  if st.session_state.post and HAS:
   m2=folium.Map(location=[45.8205,8.8250],zoom_start=11,tiles='OpenStreetMap')
   for p in st.session_state.post:
    try:
     la=float(p.get('Lat','0'))
     lo=float(p.get('Lon','0'))
     file_icon=p.get('IconFile','')
     if file_icon and os.path.exists(file_icon):
      icon=folium.CustomIcon(file_icon,icon_size=(35,35))
      folium.Marker([la,lo],popup=p.get('Postazione',''),icon=icon).add_to(m2)
     else:
      folium.Marker([la,lo],popup=p.get('Postazione',''),icon=folium.Icon(color='blue')).add_to(m2)
    except:
     pass
   st_folium(m2,height=400,width=700,key='m2')

  st.divider()
  st.markdown('##### 4 - ELENCO POSTAZIONI - CON ICONA PNG IN TABELLA')

  if st.session_state.post:
   # Tabella con icona
   for idx,p in enumerate(st.session_state.post):
    c1,c2,c3,c4,c5=st.columns([1,2,1,1,1])
    with c1:
     file_icon=p.get('IconFile','')
     if file_icon and os.path.exists(file_icon):
      try:
       st.image(file_icon,width=40)
      except:
       st.write('Icon')
     else:
      st.write(p.get('Icona',''))
    with c2:
     st.write(p.get('Postazione','')+'\n'+p.get('Comune','')+'\nODV: '+p.get('ODV',''))
    with c3:
     if st.button('Vedi + ODV',key=f'vedi_{idx}'):
      st.session_state.sel=idx
      st.session_state.prev=idx
      try:
       st.session_state.lat=float(p.get('Lat','45.8205'))
       st.session_state.lon=float(p.get('Lon','8.8250'))
       st.session_state.com=p.get('Comune','')
       st.session_state.via=p.get('Via','')
       st.session_state.zoom=19
      except:
       pass
      st.rerun()
    with c4:
     if st.button('Anteprima',key=f'ante_{idx}'):
      st.session_state.prev=idx
      st.rerun()
    with c5:
     if st.button('Torna indietro',key=f'back_{idx}'):
      st.session_state.prev=-1
      st.session_state.sel=-1
      st.rerun()

   st.divider()
   st.dataframe(pd.DataFrame(st.session_state.post),use_container_width=True)

   if st.session_state.prev>=0:
    try:
     p_prev=st.session_state.post[st.session_state.prev]
     st.markdown('#### ANTEPRIMA - VEDI ODV E ICONA PNG')
     st.success('Postazione: '+p_prev.get('Postazione','')+' - Icona: '+p_prev
