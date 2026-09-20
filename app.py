import streamlit as st
import pandas as pd
from io import BytesIO
import os, json, hashlib, requests

try:
 import folium
 from streamlit_folium import st_folium
 HAS_FOLIUM=True
except:
 HAS_FOLIUM=False

st.set_page_config(page_title="ANA Varese", layout="wide")

# FIX INTESTAZIONE TAGLIATA - SPOSTATA IN GIU' + VERDE ANA + TESTO NERO TIMES GRASSETTO
st.markdown("""
<style>
.block-container{padding-top:70px!important; max-width:100%!important;}
.stForm{background:#e8f5e9!important; border:2px solid #0e7a3d!important; border-radius:8px!important;}
.stForm label{color:#000000!important; font-family:"Times New Roman", Times, serif!important; font-weight:bold!important;}
.stButton>button{background:#0e7a3d!important; color:white!important; font-family:"Times New Roman", Times, serif!important; font-weight:bold!important;}
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

def get_addr(lat,lon):
 try:
  url='https://nominatim.openstreetmap.org/reverse?lat='+str(lat)+'&lon='+str(lon)+'&format=jsonv2&accept-language=it'
  r=requests.get(url,headers={'User-Agent':'ana-varese'},timeout=6)
  if r.status_code==200:
   j=r.json()
   a=j.get('address',{})
   com=a.get('city') or a.get('town') or a.get('village') or a.get('municipality') or ''
   via=a.get('road') or a.get('pedestrian') or ''
   num=a.get('house_number') or ''
   full_via=(via+' '+num).strip()
   return com, full_via
 except:
  pass
 return '',''

FD='dati.json'; FU='utenti.json'; FP='post.json'; FI='icone.json'; FT='tipologie.json'; FO='odv.json'

if 'dati' not in st.session_state: st.session_state.dati=[]
if 'post' not in st.session_state: st.session_state.post=[]
if 'icone' not in st.session_state: st.session_state.icone=[]
if 'tipologie' not in st.session_state: st.session_state.tipologie=[]
if 'odv_list' not in st.session_state: st.session_state.odv_list=[]
if 'menu' not in st.session_state: st.session_state.menu='Dashboard'
if 'auth' not in st.session_state: st.session_state.auth=False
if 'lat_tmp' not in st.session_state: st.session_state.lat_tmp=45.8205
if 'lon_tmp' not in st.session_state: st.session_state.lon_tmp=8.8250
if 'com_tmp' not in st.session_state: st.session_state.com_tmp=''
if 'via_tmp' not in st.session_state: st.session_state.via_tmp=''
if 'map_expand' not in st.session_state: st.session_state.map_expand=False
if 'map_all_expand' not in st.session_state: st.session_state.map_all_expand=False
if 'sel_idx' not in st.session_state: st.session_state.sel_idx=-1
if 'zoom_level' not in st.session_state: st.session_state.zoom_level=16
if 'clicked_lat' not in st.session_state: st.session_state.clicked_lat=None
if 'clicked_lon' not in st.session_state: st.session_state.clicked_lon=None

st.session_state.dati=load_json(FD,[])
st.session_state.post=load_json(FP,[])
st.session_state.icone=load_json(FI,[])
st.session_state.utenti=load_json(FU,[])
st.session_state.tipologie=load_json(FT,[])
st.session_state.odv_list=load_json(FO,[])

if not st.session_state.utenti:
 st.session_state.utenti=[{'username':'admin','password':hash_pwd('ana2024')}]
 save_json(FU,st.session_state.utenti)
if not st.session_state.tipologie:
 st.session_state.tipologie=['Presidio','Blocco stradale','Punto ritrovo','Parcheggio','Sanitario','Logistica','Altro']
 save_json(FT,st.session_state.tipologie)
if not st.session_state.odv_list:
 st.session_state.odv_list=['ANA Varese','Protezione Civile Varese','Croce Rossa','Alpini','AIB','Altro']
 save_json(FO,st.session_state.odv_list)
if not st.session_state.icone:
 st.session_state.icone=[{'nome':'Presidio','col':'blue'},{'nome':'Blocco','col':'red'},{'nome':'Sanitario','col':'green'}]
 save_json(FI,st.session_state.icone)

def header():
 # FIX LOGO + INTESTAZIONE SPOSTATA IN GIU' CON MARGINE
 st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
 col1, col2 = st.columns([1,5])
 with col1:
  try:
   st.image("logo.png", width=90)
  except:
   try:
    st.image("logo_ana.png", width=90)
   except:
    st.markdown("<div style='font-size:50px; text-align:center;'>🪖</div>", unsafe_allow_html=True)
 with col2:
  st.markdown("<div style='background:#a5d6a7; padding:12px; border-radius:8px; border:2px solid #0e7a3d; text-align:center; margin-top:5px;'><b style='color:#000000; font-family:\"Times New Roman\", Times, serif; font-size:28px; font-weight:bold;'>VOLONTARIATO<br>Sezione di Varese</b></div>", unsafe_allow_html=True)

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
    ph=hash_pwd(p)
    for ut in st.session_state.utenti:
     if ut['username']==u and ut['password']==ph:
      st.session_state.auth=True
      st.rerun()
    st.error('Errati')
 st.stop()

if not st.session_state.map_expand and not st.session_state.map_all_expand:
 header()

with st.sidebar:
 if not st.session_state.map_expand and not st.session_state.map_all_expand:
  st.markdown('<b style="font-family:Times New Roman; color:#000000;">MENU</b>',unsafe_allow_html=True)
  opts=['Dashboard','Volontari','Mappa','Libreria Icone','Backup']
  sel=st.radio('Vai a',opts,index=0)
  if sel!=st.session_state.menu:
   st.session_state.menu=sel
   st.rerun()
  st.divider()
  if st.button('LOGOUT',use_container_width=True,type='primary'):
   st.session_state.auth=False
   st.rerun()
 else:
  if st.button('TORNA AL FORM',use_container_width=True,type='primary'):
   st.session_state.map_expand=False
   st.session_state.map_all_expand=False
   st.rerun()

scelta=st.session_state.menu

if st.session_state.map_expand or st.session_state.map_all_expand:
 st.markdown("<style>header{visibility:hidden!important;} [data-testid=\"stSidebar\"]{display:none!important;}.block-container{padding-top:10px!important; max-width:100%!important;} footer{visibility:hidden!important;}</style>", unsafe_allow_html=True)
 if st.session_state.map_expand:
  st.markdown('## MAPPA INSERIMENTO - SCHERMO INTERO')
  if st.button('TORNA INDIETRO',use_container_width=True,type='primary',key='c1'):
   st.session_state.map_expand=False
   st.session_state.zoom_level=16
   st.rerun()
  lat_c=st.session_state.lat_tmp
  lon_c=st.session_state.lon_tmp
  zoom=st.session_state.zoom_level
  if st.session_state.sel_idx>=0 and st.session_state.sel_idx<len(st.session_state.post):
   p_sel=st.session_state.post[st.session_state.sel_idx]
   try:
    lat_c=float(p_sel.get('Lat','45.8205'))
    lon_c=float(p_sel.get('Lon','8.8250'))
    zoom=19
    st.success('INGRANDITA: '+p_sel.get('Postazione',''))
   except:
    pass
  if HAS_FOLIUM:
   m=folium.Map(location=[lat_c,lon_c],zoom_start=zoom,tiles='OpenStreetMap')
   for idx in range(len(st.session_state.post)):
    p=st.session_state.post[idx]
    try:
     la=float(p.get('Lat','0'))
     lo=float(p.get('Lon','0'))
     if idx==st.session_state.sel_idx:
      folium.Marker([la,lo],popup=p.get('Postazione',''),icon=folium.Icon(color='red',icon='star')).add_to(m)
     else:
      folium.Marker([la,lo],popup=p.get('Postazione',''),icon=folium.Icon(color='blue')).add_to(m)
    except:
     pass
   # ICONA TEMPORANEA DOVE CLICCHI - LASCIA ICONA!
   if st.session_state.clicked_lat is not None:
    folium.Marker([st.session_state.clicked_lat, st.session_state.clicked_lon], popup='NUOVA POSIZIONE - Compila maschera sotto', icon=folium.Icon(color='green', icon='ok')).add_to(m)
   st_folium(m,height=850,width=1600,key='m1fs')
 if st.session_state.map_all_expand:
  st.markdown('## MAPPA TUTTE - SCHERMO INTERO')
  if st.button('TORNA INDIETRO',use_container_width=True,type='primary',key='c2'):
   st.session_state.map_all_expand=False
   st.rerun()
  if HAS_FOLIUM and st.session_state.post:
   m2=folium.Map(location=[45.8205,8.8250],zoom_start=12,tiles='OpenStreetMap')
   for p in st.session_state.post:
    try:
     la=float(p.get('Lat','0'))
     lo=float(p.get('Lon','0'))
     folium.Marker([la,lo],popup=p.get('Postazione',''),icon=folium.Icon(color='blue')).add_to(m2)
    except:
     pass
   st_folium(m2,height=850,width=1600,key='m2fs')
else:
 if scelta=='Dashboard':
  st.markdown('<h3 style="font-family:Times New Roman; color:#000000; font-weight:bold; margin-top:10px;">DASHBOARD - MENU COMPLETO</h3>',unsafe_allow_html=True)
  c1,c2=st.columns([3,1])
  with c1: st.info('Menu completo - tutti i form')
  with c2:
   if st.button('LOGOUT',use_container_width=True):
    st.session_state.auth=False
    st.rerun()
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
  st.markdown('<h3 style="font-family:Times New Roman; color:#000000; font-weight:bold;">VOLONTARI</h3>',unsafe_allow_html=True)
  with st.form('vol'):
   c1,c2=st.columns(2)
   with c1:
    a1=st.text_input('Nome *',placeholder='Mario')
    a2=st.text_input('Cognome *',placeholder='Rossi')
   with c2:
    a4=st.text_input('Cellulare *',placeholder='3331234567')
   if st.form_submit_button('SALVA'):
    if a1 and a2 and a4:
     nc=a1+' '+a2
     nuovo={'Nome':nc,'Cellulare':a4}
     st.session_state.dati.append(nuovo)
     save_json(FD,st.session_state.dati)
     st.success('Salvato '+nc)
     st.rerun()
  if st.session_state.dati:
   st.dataframe(pd.DataFrame(st.session_state.dati),use_container_width=True)
 elif scelta=='Mappa':
  torna()
  st.markdown('<h3 style="font-family:Times New Roman; color:#000000; font-weight:bold;">MAPPA - DECIDI TU LA POSTAZIONE</h3>',unsafe_allow_html=True)
  st.markdown('<p style="font-family:Times New Roman; color:#000000; font-weight:bold;">Clicca sulla mappa dove vuoi - lascia icona verde e compila automatico Comune/Via/Lat/Lon nella maschera sotto</p>',unsafe_allow_html=True)
  icon_names=[]
  for item in st.session_state.icone:
   icon_names.append(item.get('nome','')+' ('+item.get('col','')+')')
  sel_idx=0
  if icon_names:
   sel_str=st.selectbox('Icona da libreria',icon_names,index=0)
   sel_idx=icon_names.index(sel_str)
  sel_tipo=st.selectbox('Tipologia',st.session_state.tipologie)
  new_tipo=st.text_input('Nuova tipologia')
  if st.button('AGGIUNGI TIPOLOGIA'):
   if new_tipo and new_tipo not in st.session_state.tipologie:
    st.session_state.tipologie.append(new_tipo)
    save_json(FT,st.session_state.tipologie)
    st.success('Memorizzata '+new_tipo)
    st.rerun()
  st.divider()
  st.markdown('##### 1 - MAPPA - CLICCA DOVE VUOI - LASCIA ICONA VERDE + ASSOCIA MASCHERA')
  c1,c2=st.columns([3,1])
  with c1: st.caption('CLICCA SULLA MAPPA - Lascia icona verde e associa Comune Via Lat Lon nella maschera')
  with c2:
   if st.button('ESPANDI A SCHERMO INTERO',use_container_width=True,key='e1'):
    st.session_state.map_expand=True
    st.rerun()
  lat_c=st.session_state.lat_tmp
  lon_c=st.session_state.lon_tmp
  zoom=st.session_state.zoom_level
  if st.session_state.sel_idx>=0 and st.session_state.sel_idx<len(st.session_state.post):
   p_sel=st.session_state.post[st.session_state.sel_idx]
   try:
    lat_c=float(p_sel.get('Lat','45.8205'))
    lon_c=float(p_sel.get('Lon','8.8250'))
    zoom=19
    st.success('INGRANDITA: '+p_sel.get('Postazione',''))
   except:
    pass
  if HAS_FOLIUM:
   m=folium.Map(location=[lat_c,lon_c],zoom_start=zoom,tiles='OpenStreetMap')
   for idx in range(len(st.session_state.post)):
    p=st.session_state.post[idx]
    try:
     la=float(p.get('Lat','0'))
     lo=float(p.get('Lon','0'))
     if idx==st.session_state.sel_idx:
      folium.Marker([la,lo],popup=p.get('Postazione',''),icon=folium.Icon(color='red',icon='star')).add_to(m)
     else:
      folium.Marker([la,lo],popup=p.get('Postazione',''),icon=folium.Icon(color='blue')).add_to(m)
    except:
     pass
   # ICONA TEMPORANEA VERDE DOVE HAI CLICCATO - ORA LASCIA ICONA!
   if st.session_state.clicked_lat is not None:
    folium.Marker([st.session_state.clicked_lat, st.session_state.clicked_lon], popup='NUOVA - Compila maschera sotto e salva', icon=folium.Icon(color='green', icon='ok')).add_to(m)
   out=st_folium(m,height=450,width=700,key='map1')
   if out and out.get('last_clicked'):
    try:
     nl=out['last_clicked']['lat']
     ng=out['last_clicked']['lng']
     # ASSOCIA MASCHERA VIA COMUNE LATITUDINE LONGITUDINE + LASCIA ICONA
     st.session_state.lat_tmp=nl
     st.session_state.lon_tmp=ng
     st.session_state.clicked_lat=nl
     st.session_state.clicked_lon=ng
     com,via=get_addr(nl,ng)
     st.session_state.com_tmp=com
     st.session_state.via_tmp=via
     st.session_state.sel_idx=-1
     st.session_state.zoom_level=16
     st.rerun()
    except:
     pass
  c1,c2,c3=st.columns(3)
  with c1: st.write('Lat: '+str(round(st.session_state.lat_tmp,6)))
  with c2: st.write('Comune: '+st.session_state.com_tmp)
  with c3: st.write('Via: '+st.session_state.via_tmp)
  st.divider()
  st.markdown('##### 2 - MASCHERA VERDE ANA - VIA COMUNE LAT LON ASSOCIATI + ODV')
  st.success('Clicca sulla mappa sopra - si riempiono automatico Comune/Via/Lat/Lon + icona verde in mappa')
  vol_nomi=[]
  for d in st.session_state.dati:
   if d.get('Nome',''):
    vol_nomi.append(d.get('Nome',''))
  if not vol_nomi:
   vol_nomi=['Nessun volontario']
  with st.form('g'):
   c1,c2=st.columns(2)
   with c1:
    m1=st.text_input('Nome postazione *',value='',placeholder='Decidi tu il nome')
    m2=st.text_input('Comune *',value=st.session_state.com_tmp)
    m3=st.text_input('Via *',value=st.session_state.via_tmp)
    m4=st.selectbox('Tipologia *',st.session_state.tipologie,index=0)
    m4_new=st.text_input('Nuova tipologia',value='')
   with c2:
    m5=st.text_input('Latitudine *',value=str(st.session_state.lat_tmp))
    m6=st.text_input('Longitudine *',value=str(st.session_state.lon_tmp))
    m8=st.selectbox('Responsabile *',vol_nomi,index=0)
    m8_new=st.text_input('Nuovo responsabile',value='')
    m9=st.selectbox('ODV operante *',st.session_state.odv_list,index=0)
    m9_new=st.text_input('Nuova ODV operante',value='')
   if st.form_submit_button('SALVA POSTAZIONE CON ICONA'):
    if m1:
     tf=m4_new if m4_new else m4
     if tf not in st.session_state.tipologie and tf:
      st.session_state.tipologie.append(tf)
      save_json(FT,st.session_state.tipologie)
     rf=m8_new if m8_new else m8
     if m8_new and m8_new not in vol_nomi:
      st.session_state.dati.append({'Nome':m8_new,'Cellulare':''})
      save_json(FD,st.session_state.dati)
     odv_f=m9_new if m9_new else m9
     if odv_f not in st.session_state.odv_list and odv_f:
      st.session_state.odv_list.append(odv_f)
      save_json(FO,st.session_state.odv_list)
     ic=st.session_state.icone[sel_idx] if st.session_state.icone else {'col':'blue'}
     nuovo={'Postazione':m1,'Comune':m2,'Via':m3,'Lat':m5,'Lon':m6,'Tipo':tf,'Col':ic.get('col','blue'),'Resp':rf,'ODV':odv_f}
     st.session_state.post.append(nuovo)
     save_json(FP,st.session_state.post)
     # PULISCI CLICK TEMPORANEO
     st.session_state.clicked_lat=None
     st.session_state.clicked_lon=None
     st.success('Salvata '+m1+' ODV:'+odv_f+' - ICONA INSERITA!')
     st.rerun()
  st.divider()
  st.markdown('##### 3 - MAPPA TUTTE LE POSTAZIONI')
  c1,c2=st.columns([3,1])
  with c1: st.caption('Totale: '+str(len(st.session_state.post)))
  with c2:
   if st.button('ESPANDI A SCHERMO INTERO',use_container_width=True,key='e2'):
    st.session_state.map_all_expand=True
    st.rerun()
  if st.session_state.post and HAS_FOLIUM:
   m2=folium.Map(location=[45.8205,8.8250],zoom_start=12,tiles='OpenStreetMap')
   for p in st.session_state.post:
    try:
     la=float(p.get('Lat','0'))
     lo=float(p.get('Lon','0'))
     folium.Marker([la,lo],popup=p.get('Postazione',''),icon=folium.Icon(color='blue')).add_to(m2)
    except:
     pass
   st_folium(m2,height=400,width=700,key='m2')
  st.divider()
  st.markdown('##### 4 - TABELLA VEDI INGRANDITA')
  if st.session_state.post:
   st.dataframe(pd.DataFrame(st.session_state.post),use_container_width=True)
   for i in range(len(st.session_state.post)):
    p=st.session_state.post[i]
    c1,c2,c3=st.columns([2,1,1])
    with c1: st.write(p.get('Postazione','')+' - '+p.get('Comune','')+' - '+p.get('ODV',''))
    with c2:
     if st.button('Vedi ingrandita',key='vedi_'+str(i)):
      st.session_state.sel_idx=i
      try:
       st.session_state.lat_tmp=float(p.get('Lat','45.8205'))
       st.session_state.lon_tmp=float(p.get('Lon','8.8250'))
       st.session_state.com_tmp=p.get('Comune','')
       st.session_state.via_tmp=p.get('Via','')
       st.session_state.zoom_level=19
      except:
       pass
      st.rerun()
    with c3:
     lat=p.get('Lat','')
     lon=p.get('Lon','')
     st.link_button('Google','https://www.google.com/maps?q='+str(lat)+','+str(lon))
 elif scelta=='Libreria Icone':
  torna()
  st.markdown('#### LIBRERIA ICONE')
  with st.form('lib'):
   n1=st.text_input('Nome icona *')
   n3=st.selectbox('Colore',['blue','red','green','orange','black'])
   if st.form_submit_button('SALVA'):
    if n1:
     nuovo={'nome':n1,'col':n3}
     st.session_state.icone.append(nuovo)
     save_json(FI,st.session_state.icone)
     st.success('Icona '+n1+' salvata')
     st.rerun()
 elif scelta=='Volontari':
  torna()
  st.markdown('<h3 style="font-family:Times New Roman; color:#000000; font-weight:bold;">VOLONTARI</h3>',unsafe_allow_html=True)
  if st.session_state.dati:
   st.dataframe(pd.DataFrame(st.session_state.dati))
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
 else:
  torna()
  st.markdown('#### '+scelta)
  st.info('Sezione in sviluppo')
