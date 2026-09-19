import streamlit as st
import pandas as pd
from io import BytesIO
import os, json, hashlib
from datetime import date, datetime

# FOLIUM PER MAPPA CLICCABILE
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
  if st.button('EVENTI'):
   st.session_state.menu='Eventi'
   st.rerun()
  if st.button('BROGLIACCIO'):
   st.session_state.menu='Brogliaccio'
   st.rerun()
 with c2:
  if st.button('MAPPA'):
   st.session_state.menu='Mappa'
   st.rerun()
  if st.button('RADIO'):
   st.session_state.menu='Radio'
   st.rerun()
  if st.button('CONSEGNA'):
   st.session_state.menu='Consegna'
   st.rerun()
 with c3:
  if st.button('CHECK-IN'):
   st.session_state.menu='Check'
   st.rerun()
  if st.button('EMERGENZE'):
   st.session_state.menu='Emergenze'
   st.rerun()
  if st.button('BACKUP'):
   st.session_state.menu='Backup'
   st.rerun()

elif scelta=='Volontari':
 torna()
 st.markdown('#### VOLONTARI')
 t1,t2,t3,t4,t5=st.tabs([
  'Anagrafica',
  'Residenza',
  'Tesseramento',
  'Abilita',
  'Note'
 ])
 with t1:
  with st.form('b'):
   st.markdown('**Anagrafica**')
   a1=st.text_input('Nome *')
   a2=st.text_input('Cognome *')
   a4=st.date_input('Nascita',value=date(1980,1,1))
   if st.form_submit_button('SALVA'):
    st.session_state.s1_nome=a1
    st.session_state.s1_cogn=a2
    st.session_state.s1_dn=str(a4)
    st.success('OK')
 with t2:
  with st.form('c'):
   st.markdown('**Residenza**')
   b1=st.text_input('Via *')
   b2=st.text_input('Comune *',value='Varese')
   b3=st.text_input('Cell *')
   if st.form_submit_button('SALVA'):
    st.session_state.s2_via=b1
    st.session_state.s2_com=b2
    st.session_state.s2_cell=b3
    st.success('OK')
 with t3:
  with st.form('d'):
   st.markdown('**Tesseramento**')
   c1x=st.text_input('Tessera')
   c2x=st.text_input('Ruolo',value='Volontario')
   if st.form_submit_button('SALVA'):
    st.session_state.s3_tess=c1x
    st.session_state.s3_ruolo=c2x
    st.success('OK')
 with t4:
  with st.form('e'):
   st.markdown('**Abilita**')
   d1=st.text_input('Patenti',value='B')
   if st.form_submit_button('SALVA'):
    st.session_state.s4_pat=d1
    st.success('OK')
 with t5:
  with st.form('f'):
   st.markdown('**Note**')
   e2=st.text_area('Note')
   btn=st.form_submit_button('SALVA VOLONTARIO')
   if btn:
    nome=st.session_state.get('s1_nome','')
    cogn=st.session_state.get('s1_cogn','')
    cell=st.session_state.get('s2_cell','')
    com=st.session_state.get('s2_com','')
    ruolo=st.session_state.get('s3_ruolo','')
    if nome and cell:
     nuovo={}
     nuovo['Nome']=nome+' '+cogn
     nuovo['Cell']=cell
     nuovo['Comune']=com
     nuovo['Ruolo']=ruolo
     nuovo['Note']=e2
     st.session_state.dati.append(nuovo)
     save_json(FD,st.session_state.dati)
     st.success('Salvato')
     st.rerun()
 if st.session_state.dati:
  st.dataframe(pd.DataFrame(st.session_state.dati))

elif scelta=='Mappa':
 torna()
 st.markdown('#### MAPPA - CLICCABILE PER FISSARE')

 # SELEZIONE OSM GOOGLE WAZE
 tipo=st.radio(
  'Seleziona mappa',
  ['OpenStreetMap cliccabile','Google Maps','Waze'],
  horizontal=True
 )

 st.markdown('##### 1 - MAPPA PER INSERIRE - CLICCA PER FISSARE')
 st.info('Clicca sulla mappa OSM per fissare la postazione')

 col_a,col_b=st.columns([2,1])
 with col_a:
  st.markdown('**Mappa OSM cliccabile**')
  lat_man=st.number_input(
   'Lat',
   value=float(st.session_state.lat_tmp),
   format='%.6f',
   key='lat1'
  )
  lon_man=st.number_input(
   'Lon',
   value=float(st.session_state.lon_tmp),
   format='%.6f',
   key='lon1'
  )

  # MAPPA CLICCABILE - OSM
  if HAS_FOLIUM:
   m=folium.Map(
    location=[lat_man,lon_man],
    zoom_start=16,
    tiles='OpenStreetMap'
   )
   folium.Marker(
    [lat_man,lon_man],
    popup='Postazione',
    tooltip='Clicca per spostare'
   ).add_to(m)
   # Aggiungi postazioni salvate
   for p in st.session_state.post:
    try:
     la=float(p.get('Lat','0'))
     lo=float(p.get('Lon','0'))
     folium.Marker(
      [la,lo],
      popup=p.get('Postazione',''),
      icon=folium.Icon(color='red')
     ).add_to(m)
    except:
     pass

   out=st_folium(m,height=400,width=700)
   if out and out.get('last_clicked'):
    new_lat=out['last_clicked']['lat']
    new_lon=out['last_clicked']['lng']
    if abs(new_lat-lat_man)>0.00001:
     st.session_state.lat_tmp=new_lat
     st.session_state.lon_tmp=new_lon
     st.rerun()
  else:
   # Fallback se no folium
   df_ante=pd.DataFrame({'lat':[lat_man],'lon':[lon_man]})
   st.map(df_ante,zoom=15)
   st.warning('Installa folium per cliccare')

  st.caption('OSM - Clicca sulla mappa per fissare')

  # ANTEPRIMA GOOGLE/WAZE SE SELEZIONATO
  if tipo=='Google Maps':
   st.markdown('**Anteprima Google Maps**')
   url='https://www.google.com/maps?q='+str(lat_man)+','+str(lon_man)+'&z=16&output=embed'
   st.components.v1.iframe(url,height=300)
  elif tipo=='Waze':
   st.markdown('**Anteprima Waze**')
   url='https://embed.waze.com/iframe?zoom=16&lat='+str(lat_man)+'&lon='+str(lon_man)
   st.components.v1.iframe(url,height=300)

 with col_b:
  st.markdown('**Istruzioni**')
  st.write('1 - Clicca sulla mappa OSM')
  st.write('2 - Lat/Lon si aggiorna')
  st.write('3 - Salva sotto')
  st.write('')
  st.write('**Lat/Lon attuali:**')
  st.code(str(round(lat_man,6))+','+str(round(lon_man,6)))
  if st.button('CENTRA VARESE'):
   st.session_state.lat_tmp=45.8205
   st.session_state.lon_tmp=8.8250
   st.rerun()
  st.write('')
  st.write('**Tipo:** '+tipo)

 st.divider()
 st.markdown('##### 2 - INSERIMENTO MANUALE')

 with st.form('g'):
  c1,c2=st.columns(2)
  with c1:
   m1=st.text_input('Nome postazione *')
   m2=st.text_input('Comune *',value='Varese')
   m3=st.text_input('Via *')
   m7=st.text_input('Tipo',value='Presidio')
  with c2:
   m5=st.text_input('Lat',value=str(st.session_state.lat_tmp))
   m6=st.text_input('Lon',value=str(st.session_state.lon_tmp))
   m8=st.text_input('Resp')
   m9=st.text_area('Note')
  ok=st.form_submit_button('SALVA POSTAZIONE')
  if ok and m1:
   nuovo={}
   nuovo['Postazione']=m1
   nuovo['Comune']=m2
   nuovo['Via']=m3
   nuovo['Lat']=m5
   nuovo['Lon']=m6
   nuovo['Tipo']=m7
   nuovo['Note']=m9
   st.session_state.post.append(nuovo)
   save_json(FP,st.session_state.post)
   st.success('Salvata '+m1)
   st.rerun()

 st.divider()
 st.markdown('##### 3 - TUTTE LE POSTAZIONI')

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
     folium.Marker(
      [la,lo],
      popup=p.get('Postazione',''),
      tooltip=p.get('Comune','')
     ).add_to(m2)
    except:
     pass
   st_folium(m2,height=400,width=700)
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
   st.write('**'+nome+'** - '+lat+','+lon)
   c1,c2,c3=st.columns(3)
   with c1:
    osm='https://www.openstreetmap.org/?mlat='+lat+'&mlon='+lon
    st.link_button('OSM',osm)
   with c2:
    gmap='https://www.google.com/maps?q='+lat+','+lon
    st.link_button('Google',gmap)
   with c3:
    waze='https://waze.com/ul?ll='+lat+','+lon
    st.link_button('Waze',waze)
 else:
  st.info('Nessuna postazione - clicca sulla mappa sopra per fissarne una')

elif scelta=='Backup':
 torna()
 st.markdown('#### BACKUP')
 c1,c2=st.columns(2)
 with c1:
  exp_vol=st.checkbox('Volontari',value=True)
  exp_mappa=st.checkbox('Mappa',value=True)
  exp_check=st.checkbox('Check',value=True)
 with c2:
  exp_eventi=st.checkbox('Eventi',value=True)
  exp_radio=st.checkbox('Radio',value=True)
  exp_emerg=st.checkbox('Emergenze',value=True)
 if st.button('CREA BACKUP'):
  out=BytesIO()
  with pd.ExcelWriter(out,engine='openpyxl') as writer:
   if exp_vol and st.session_state.dati:
    pd.DataFrame(st.session_state.dati).to_excel(writer,sheet_name='Vol',index=False)
   if exp_mappa and st.session_state.post:
    pd.DataFrame(st.session_state.post).to_excel(writer,sheet_name='Mappa',index=False)
   if exp_check and st.session_state.check:
    pd.DataFrame(st.session_state.check).to_excel(writer,sheet_name='Check',index=False)
   if exp_eventi and st.session_state.eventi:
    pd.DataFrame(st.session_state.eventi).to_excel(writer,sheet_name='Eventi',index=False)
   if exp_radio and st.session_state.radio:
    pd.DataFrame(st.session_state.radio).to_excel(writer,sheet_name='Radio',index=False)
   if exp_emerg and st.session_state.emerg:
    pd.DataFrame(st.session_state.emerg).to_excel(writer,sheet_name='Emergenze',index=False)
  st.session_state['bk']=out.getvalue()
  st.success('OK')
 if 'bk' in st.session_state:
  st.download_button(
   'SCARICA',
   st.session_state['bk'],
   file_name='BACKUP.xlsx',
   mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
  )

else:
 torna()
 st.markdown('#### '+scelta)
 st.info('Sezione '+scelta)
