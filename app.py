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

st.set_page_config(page_title='ANA Varese', layout='wide')

st.markdown("""
<style>
.block-container{padding-top:8px!important; max-width:100%!important;}
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

def get_addr(lat,lon):
 try:
  url='https://nominatim.openstreetmap.org/reverse?lat=' + str(lat) + '&lon=' + str(lon) + '&format=jsonv2&accept-language=it'
  r=requests.get(url,headers={'User-Agent':'ana-varese'},timeout=6)
  if r.status_code==200:
   j=r.json()
   a=j.get('address',{})
   com=a.get('city') or a.get('town') or a.get('village') or a.get('municipality') or ''
   via=a.get('road') or a.get('pedestrian') or ''
   num=a.get('house_number') or ''
   full_via=via + ' ' + num
   return com, full_via
 except:
  pass
 return '',''

FD='dati.json'
FU='utenti.json'
FP='post.json'
FI='icone.json'
FT='tipologie.json'

for k,v in [
 ('dati',[]),('post',[]),('icone',[]),('tipologie',[]),
 ('menu','Dashboard'),('auth',False),
 ('lat_tmp',45.8205),('lon_tmp',8.8250),
 ('com_tmp',''),('via_tmp',''),
 ('map_expand',False),('map_all_expand',False),('sel_idx',-1),
 ('zoom_level',16)
]:
 if k not in st.session_state:
  st.session_state[k]=v

st.session_state.dati=load_json(FD,[])
st.session_state.post=load_json(FP,[])
st.session_state.icone=load_json(FI,[])
st.session_state.utenti=load_json(FU,[])
st.session_state.tipologie=load_json(FT,[])

if not st.session_state.utenti:
 st.session_state.utenti=[{'username':'admin','password':hash_pwd('ana2024')}]
 save_json(FU,st.session_state.utenti)

if not st.session_state.tipologie:
 st.session_state.tipologie=['Presidio','Blocco stradale','Punto ritrovo','Area emergenza','Parcheggio','Sanitario','Logistica','Altro']
 save_json(FT,st.session_state.tipologie)

if not st.session_state.icone:
 st.session_state.icone=[
  {'nome':'Presidio','col':'blue','file':''},
  {'nome':'Blocco','col':'red','file':''},
  {'nome':'Sanitario','col':'green','file':''}
 ]
 save_json(FI,st.session_state.icone)

def header():
 st.markdown("<div style='text-align:center;background:#a5d6a7;padding:5px;border-radius:8px;border:2px solid #2e7d32;'><b style='color:#0e7a3d;'>VOLONTARIATO Varese</b></div>", unsafe_allow_html=True)

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

if not st.session_state.map_expand and not st.session_state.map_all_expand:
 header()

with st.sidebar:
 if not st.session_state.map_expand and not st.session_state.map_all_expand:
  st.markdown('### MENU')
  opts=['Dashboard','Volontari','Mappa','Libreria Icone','Backup']
  sel=st.radio('Vai a',opts,index=0)
  if sel!=st.session_state.menu:
   st.session_state.menu=sel
   st.rerun()
  st.divider()
  if st.button('LOGOUT', use_container_width=True, type='primary'):
   st.session_state.auth=False
   st.rerun()
 else:
  st.markdown('### MAPPA A SCHERMO INTERO')
  if st.button('TORNA AL FORM', use_container_width=True, type='primary'):
   st.session_state.map_expand=False
   st.session_state.map_all_expand=False
   st.rerun()

scelta=st.session_state.menu

if st.session_state.map_expand or st.session_state.map_all_expand:
 st.markdown("""
 <style>
 header{visibility:hidden!important; height:0!important;}
 [data-testid="stSidebar"]{display:none!important;}
.block-container{padding:0!important; margin:0!important; max-width:100%!important;}
 footer{visibility:hidden!important;}
 </style>
 """, unsafe_allow_html=True)

 if st.session_state.map_expand:
  st.markdown('## MAPPA INSERIMENTO - SCHERMO INTERO 100%')
  if st.button('TORNA INDIETRO', use_container_width=True, type='primary', key='close_main_fs'):
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
    st.success('POSTAZIONE INGRANDITA: ' + p_sel.get('Postazione',''))
   except:
    pass
  if HAS_FOLIUM:
   m=folium.Map(location=[lat_c,lon_c], zoom_start=zoom, tiles='OpenStreetMap')
   for idx,p in enumerate(st.session_state.post):
    try:
     la=float(p.get('Lat','0'))
     lo=float(p.get('Lon','0'))
     if idx==st.session_state.sel_idx:
      folium.Marker([la,lo], popup=p.get('Postazione',''), icon=folium.Icon(color='red', icon='star')).add_to(m)
      folium.Circle([la,lo], radius=80, color='red', fill=True, fill_opacity=0.15).add_to(m)
     else:
      folium.Marker([la,lo], popup=p.get('Postazione',''), icon=folium.Icon(color='blue')).add_to(m)
    except:
     pass
   folium.Marker([lat_c,lon_c], popup='Nuova', icon=folium.Icon(color='green', icon='plus')).add_to(m)
   st_folium(m, height=850, width=1600, key='map1_fullscreen')

 if st.session_state.map_all_expand:
  st.markdown('## MAPPA TUTTE POSTAZIONI - SCHERMO INTERO 100%')
  if st.button('TORNA INDIETRO', use_container_width=True, type='primary', key='close_all_fs'):
   st.session_state.map_all_expand=False
   st.rerun()
  if HAS_FOLIUM and st.session_state.post:
   m2=folium.Map(location=[45.8205,8.8250], zoom_start=13, tiles='OpenStreetMap')
   for p in st.session_state.post:
    try:
     la=float(p.get('Lat','0'))
     lo=float(p.get('Lon','0'))
     folium.Marker([la,lo], popup=p.get('Postazione',''), icon=folium.Icon(color='blue')).add_to(m2)
    except:
     pass
   st_folium(m2, height=850, width=1600, key='m2_fullscreen')

else:
 if scelta=='Dashboard':
  st.markdown('#### DASHBOARD - MENU COMPLETO')
  c1,c2=st.columns([3,1])
  with c1:
   st.info('Tutti i form disponibili')
  with c2:
   if st.button('LOGOUT', use_container_width=True):
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
  st.divider()
  c1,c2=st.columns(2)
  c1.metric('Volontari',len(st.session_state.dati))
  c2.metric('Postazioni',len(st.session_state.post))

 elif scelta=='Volontari':
  torna()
  st.markdown('#### VOLONTARI')
  with st.form('vol'):
   c1,c2=st.columns(2)
   with c1:
    a1=st.text_input('Nome *', placeholder='Mario')
    a2=st.text_input('Cognome *', placeholder='Rossi')
   with c2:
    a4=st.text_input('Cellulare *', placeholder='3331234567')
   if st.form_submit_button('SALVA'):
    if a1 and a2 and a4:
     nome_completo=a1 + ' ' + a2
     nuovo={'Nome':nome_completo,'Cellulare':a4}
     st.session_state.dati.append(nuovo)
     save_json(FD,st.session_state.dati)
     st.success('Salvato ' + nome_completo)
     st.rerun()
  if st.session_state.dati:
   st.dataframe(pd.DataFrame(st.session_state.dati), use_container_width=True)

 elif scelta=='Mappa':
  torna()
  st.markdown('#### MAPPA - CON ESPANSIONE A SCHERMO INTERO VERO')
  tipo_map=st.radio('Tipo mappa', ['OpenStreetMap','Google Maps','Google Earth','Waze'], horizontal=True, key='tipo_map')
  icon_names=[]
  for ic in st.session_state.icone:
   icon_names.append(str(ic.get('nome','')) + ' (' + str(ic.get('col','')) + ')')
  sel_idx=0
  if icon_names:
   sel_str=st.selectbox('Icona da libreria', icon_names, index=0, key='icon_main')
   sel_idx=icon_names.index(sel_str)
  sel_tipo=st.selectbox('Tipologia', st.session_state.tipologie, key='sel_tip')
  new_tipo=st.text_input('Nuova tipologia', key='new_tip')
  if st.button('AGGIUNGI TIPOLOGIA'):
   if new_tipo and new_tipo not in st.session_state.tipologie:
    st.session_state.tipologie.append(new_tipo)
    save_json(FT,st.session_state.tipologie)
    st.success('Memorizzata ' + new_tipo)
    st.rerun()
  tipologia_da_usare=new_tipo if new_tipo else sel_tipo

  st.divider()
  st.markdown('##### 1 - MAPPA DOVE INSERISCI POSTAZIONI')
  c1,c2=st.columns([3,1])
  with c1:
   st.caption('Clicca sulla mappa per collegare Comune, Via, Lat, Lon')
  with c2:
   if st.button('ESPANDI A SCHERMO INTERO', use_container_width=True, key='exp_main'):
    st.session_state.map_expand=True
    st.rerun()

  lat_c=st.session_state.lat_tmp
  lon_c=st.session_state.lon_tmp
  zoom=st.session_state.zoom_level
  highlight_post=None
  if st.session_state.sel_idx>=0 and st.session_state.sel_idx<len(st.session_state.post):
   p_sel=st.session_state.post[st.session_state.sel_idx]
   highlight_post=p_sel
   try:
    lat_c=float(p_sel.get('Lat','45.8205'))
    lon_c=float(p_sel.get('Lon','8.8250'))
    zoom=19
    st.success('POSTAZIONE INGRANDITA: ' + p_sel.get('Postazione','') + ' - ' + p_sel.get('Comune',''))
   except:
    pass

  if HAS_FOLIUM and tipo_map=='OpenStreetMap':
   m=folium.Map(location=[lat_c,lon_c], zoom_start=zoom, tiles='OpenStreetMap')
   for idx,p in enumerate(st.session_state.post):
    try:
     la=float(p.get('Lat','0'))
     lo=float(p.get('Lon','0'))
     if idx==st.session_state.sel_idx:
      folium.Marker([la,lo], popup=p.get('Postazione',''), icon=folium.Icon(color='red', icon='star')).add_to(m)
      folium.Circle([la,lo], radius=80, color='red', fill=True, fill_opacity=0.15).add_to(m)
     else:
      folium.Marker([la,lo], popup=p.get('Postazione',''), icon=folium.Icon(color='blue')).add_to(m)
    except:
     pass
   folium.Marker([lat_c,lon_c], popup='Nuova', icon=folium.Icon(color='green', icon='plus')).add_to(m)
   out=st_folium(m, height=500 if highlight_post else 450, width=700, key='map1')
   if out and out.get('last_clicked'):
    nl=out['last_clicked']['lat']
    ng=out['last_clicked']['lng']
    if abs(nl-lat_c)>0.000001:
     st.session_state.lat_tmp=nl
     st.session_state.lon_tmp=ng
     com,via=get_addr(nl,ng)
     st.session_state.com_tmp=com
     st.session_state.via_tmp=via
     st.session_state.sel_idx=-1
     st.session_state.zoom_level=16
     st.rerun()

  st.divider()
  st.markdown('##### 2 - MASCHERA COLLEGATA A MAPPA + RESPONSABILE')
  volontari_nomi=[]
  for d in st.session_state.dati:
   if d.get('Nome',''):
    volontari_nomi.append(d.get('Nome',''))
  if not volontari_nomi:
   volontari_nomi=['Nessun volontario']

  with st.form('g'):
   c1,c2=st.columns(2)
   with c1:
    m1=st.text_input('Nome postazione *', value='', placeholder='Es: Presidio')
    m2=st.text_input('Comune *', value=st.session_state.com_tmp, placeholder='Auto dal click')
    m3=st.text_input('Via *', value=st.session_state.via_tmp, placeholder='Auto dal click')
    m7=st.selectbox('Tipologia *', st.session_state.tipologie, index=0)
    m7_new=st.text_input('Nuova tipologia', value='')
   with c2:
    m5=st.text_input('Latitudine *', value=str(st.session_state.lat_tmp) if st.session_state.com_tmp else '', placeholder='Auto')
    m6=st.text_input('Longitudine *', value=str(st.session_state.lon_tmp) if st.session_state.com_tmp else '', placeholder='Auto')
    m8=st.selectbox('Responsabile *', volontari_nomi, index=0)
    m8_new=st.text_input('Nuovo responsabile', value='')
   if st.form_submit_button('SALVA POSTAZIONE'):
    if m1:
     tipo_finale=m7_new if m7_new else m7
     if tipo_finale not in st.session_state.tipologie and tipo_finale:
      st.session_state.tipologie.append(tipo_finale)
      save_json(FT,st.session_state.tipologie)
     resp_finale=m8_new if m8_new else m8
     if m8_new and m8_new not in volontari_nomi:
      st.session_state.dati.append({'Nome':m8_new,'Cellulare':'','Ruolo':'Volontario'})
      save_json(FD,st.session_state.dati)
     ic=st.session_state.icone[sel_idx] if st.session_state.icone else {'col':'blue','file':''}
     nuovo={'Postazione':m1,'Comune':m2,'Via':m3,'Lat':m5,'Lon':m6,'Tipo':tipo_finale,'Col':ic.get('col','blue'),'IconaFile':ic.get('file',''),'Resp':resp_finale}
     st.session_state.post.append(nuovo)
     save_json(FP,st.session_state.post)
     st.success('Salvata ' + m1)
     st.rerun()

  st.divider()
  st.markdown('##### 3 - MAPPA TUTTE LE POSTAZIONI')
  c1,c2=st.columns([3,1])
  with c1:
   st.caption('Totale: ' + str(len(st.session_state.post)))
  with c2:
   if st.button('ESPANDI A SCHERMO INTERO', use_container_width=True, key='exp_all'):
    st.session_state.map_all_expand=True
    st.rerun()
  if st.session_state.post and HAS_FOLIUM:
   m2=folium.Map(location=[45.8205,8.8250], zoom_start=12, tiles='OpenStreetMap')
   for p in st.session_state.post:
    try:
     la=float(p.get('Lat','0'))
     lo=float(p.get('Lon','0'))
     folium.Marker([la,lo], popup=p.get('Postazione',''), icon=folium.Icon(color='blue')).add_to(m2)
    except:
     pass
   st_folium(m2, height=400, width=700, key='m2')

  st.divider()
  st.markdown('##### 4 - TABELLA VEDI INGRANDITA')
  if st.session_state.post:
   st.dataframe(pd.DataFrame(st.session_state.post), use_container_width=True)
   for i,p in enumerate(st.session_state.post):
    c1,c2,c3=st.columns([2,1,1])
    with c1:
     st.write(p.get('Postazione','') + ' - ' + p.get('Comune',''))
    with c2:
     if st.button('Vedi ingrandita', key=f'vedi_{i}'):
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
     st.link_button('Google', 'https://www.google.com/maps?q=' + str(lat) + ',' + str(lon))

 elif scelta=='Libreria Icone':
  torna()
  st.markdown('#### LIBRERIA ICONE')
  with st.form('lib'):
   n1=st.text_input('Nome icona *')
   n3=st.selectbox('Colore', ['blue','red','green','orange','darkred','purple','black'])
   up=st.file_uploader('PNG', type=['png','jpg','jpeg'])
   icon_path=''
   if up:
    os.makedirs('icone',exist_ok=True)
    icon_path='icone/' + up.name
    with open(icon_path,'wb') as f:
     f.write(up.getbuffer())
    st.image(up,width=50)
   if st.form_submit_button('SALVA'):
    if n1:
     nuovo={'nome':n1,'col':n3,'file':icon_path}
     st.session_state.icone.append(n
