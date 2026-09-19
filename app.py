import streamlit as st
import pandas as pd
from io import BytesIO
import os, json, hashlib, requests
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

def get_addr(lat,lon):
 try:
  url=f'https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=jsonv2'
  r=requests.get(url,headers={'User-Agent':'ana-varese-app'},timeout=6)
  if r.status_code==200:
   j=r.json()
   a=j.get('address',{})
   com=a.get('city') or a.get('town') or a.get('village') or a.get('municipality') or ''
   via=a.get('road') or a.get('street') or a.get('footway') or ''
   num=a.get('house_number') or ''
   via_full=f"{via} {num}".strip()
   return com, via_full
 except:
  pass
 return '',''

FD='dati.json'
FU='utenti.json'
FP='post.json'
FI='icone.json'
FT='tipologie.json'

if 'dati' not in st.session_state:
 st.session_state.dati=[]
if 'post' not in st.session_state:
 st.session_state.post=[]
if 'icone' not in st.session_state:
 st.session_state.icone=[]
if 'tipologie' not in st.session_state:
 st.session_state.tipologie=[]
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
if 'clicks' not in st.session_state:
 st.session_state.clicks=[]

st.session_state.dati=load_json(FD,[])
st.session_state.post=load_json(FP,[])
st.session_state.icone=load_json(FI,[])
st.session_state.utenti=load_json(FU,[])
st.session_state.tipologie=load_json(FT,[])

if not st.session_state.utenti:
 st.session_state.utenti=[{'username':'admin','password':hash_pwd('ana2024')}]
 save_json(FU,st.session_state.utenti)

if not st.session_state.tipologie:
 st.session_state.tipologie=[
  'Presidio','Blocco stradale','Punto ritrovo',
  'Area emergenza','Parcheggio','Segreteria',
  'Radio','Sanitario','Logistica','Mensa','Magazzino','Altro'
 ]
 save_json(FT,st.session_state.tipologie)

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

header()
with st.sidebar:
 opts=['Dashboard','Volontari','Mappa','Libreria Icone','Eventi','Radio','Check','Brogliaccio','Consegna','Emergenze','Backup']
 sel=st.radio('Vai a',opts,index=0)
 if sel!=st.session_state.menu:
  st.session_state.menu=sel
  st.rerun()

scelta=st.session_state.menu

if scelta=='Dashboard':
 st.markdown('#### DASHBOARD - TUTTI I FORM')
 st.info('Menu completo di tutti i form')
 c1,c2,c3=st.columns(3)
 with c1:
  if st.button('VOLONTARI',use_container_width=True):
   st.session_state.menu='Volontari'
   st.rerun()
  if st.button('MAPPA',use_container_width=True):
   st.session_state.menu='Mappa'
   st.rerun()
  if st.button('EVENTI',use_container_width=True):
   st.session_state.menu='Eventi'
   st.rerun()
  if st.button('RADIO',use_container_width=True):
   st.session_state.menu='Radio'
   st.rerun()
 with c2:
  if st.button('CHECK-IN',use_container_width=True):
   st.session_state.menu='Check'
   st.rerun()
  if st.button('BROGLIACCIO',use_container_width=True):
   st.session_state.menu='Brogliaccio'
   st.rerun()
  if st.button('CONSEGNA',use_container_width=True):
   st.session_state.menu='Consegna'
   st.rerun()
  if st.button('LIBRERIA ICONE',use_container_width=True):
   st.session_state.menu='Libreria Icone'
   st.rerun()
 with c3:
  if st.button('EMERGENZE',use_container_width=True):
   st.session_state.menu='Emergenze'
   st.rerun()
  if st.button('BACKUP',use_container_width=True):
   st.session_state.menu='Backup'
   st.rerun()

elif scelta=='Mappa':
 torna()
 st.markdown('#### MAPPA - PIU POSTAZIONI CLICCANDO')

 st.markdown('##### TIPOLOGIA COMBO CON MEMORIA')
 sel_tipo=st.selectbox('Seleziona tipologia esistente', st.session_state.tipologie, index=0, key='sel_tipo_exist')
 new_tipo=st.text_input('Oppure scrivi nuova tipologia e premi AGGIUNGI per memorizzarla', value='', key='new_tipo_input')
 c1,c2=st.columns([1,3])
 with c1:
  if st.button('AGGIUNGI TIPOLOGIA'):
   if new_tipo and new_tipo not in st.session_state.tipologie:
    st.session_state.tipologie.append(new_tipo)
    save_json(FT,st.session_state.tipologie)
    st.success(f'Tipologia {new_tipo} memorizzata')
    st.rerun()
 with c2:
  st.write(f"In memoria: {', '.join(st.session_state.tipologie)}")
 tipologia_da_usare=new_tipo if new_tipo else sel_tipo

 st.divider()
 col_a,col_b=st.columns([2,1])
 with col_a:
  lat_c=st.session_state.lat_tmp
  lon_c=st.session_state.lon_tmp
  lat_man=st.number_input('Latitudine',value=float(lat_c),format='%.6f',key='lat1')
  lon_man=st.number_input('Longitudine',value=float(lon_c),format='%.6f',key='lon1')
  com_man=st.text_input('Comune (auto dal click)',value=st.session_state.com_tmp,key='com1')
  via_man=st.text_input('Via (auto dal click)',value=st.session_state.via_tmp,key='via1')
  st.session_state.lat_tmp=lat_man
  st.session_state.lon_tmp=lon_man
  st.session_state.com_tmp=com_man
  st.session_state.via_tmp=via_man

  if HAS_FOLIUM:
   m=folium.Map(location=[lat_man,lon_man],zoom_start=16,tiles='OpenStreetMap')
   folium.Marker([lat_man,lon_man],popup='Nuova',tooltip='Posizione attuale',icon=folium.Icon(color='green',icon='plus')).add_to(m)
   for p in st.session_state.post:
    try:
     la=float(p.get('Lat','0'))
     lo=float(p.get('Lon','0'))
     nome=p.get('Postazione','')
     folium.Marker([la,lo],popup=nome,tooltip=nome,icon=folium.Icon(color='blue')).add_to(m)
    except:
     pass
   for c in st.session_state.clicks:
    try:
     folium.Marker([c['lat'],c['lon']],popup='Temp',icon=folium.Icon(color='orange',icon='info-sign')).add_to(m)
    except:
     pass
   out=st_folium(m,height=450,width=700,key='map1')
   if out and out.get('last_clicked'):
    nl=out['last_clicked']['lat']
    ng=out['last_clicked']['lng']
    if abs(nl-lat_man)>0.000001:
     st.session_state.lat_tmp=nl
     st.session_state.lon_tmp=ng
     com,via=get_addr(nl,ng)
     st.session_state.com_tmp=com if com else st.session_state.com_tmp
     st.session_state.via_tmp=via if via else st.session_state.via_tmp
     st.session_state.clicks.append({'lat':nl,'lon':ng,'com':com,'via':via})
     st.rerun()
  else:
   df=pd.DataFrame({'lat':[lat_man],'lon':[lon_man]})
   st.map(df,zoom=15)

 with col_b:
  st.write('1. Clicca mappa')
  st.write('2. Comune Via Lat Lon auto')
  st.write('3. Salva sotto')
  st.write('4. Clicca ancora per altra')
  st.write(f"Click temp: {len(st.session_state.clicks)}")
  if st.button('CENTRA VARESE'):
   st.session_state.lat_tmp=45.8205
   st.session_state.lon_tmp=8.8250
   st.session_state.com_tmp='Varese'
   st.session_state.via_tmp=''
   st.rerun()
  if st.button('PULISCI TEMP'):
   st.session_state.clicks=[]
   st.rerun()

 st.divider()
 with st.form('g'):
  c1,c2=st.columns(2)
  with c1:
   m1=st.text_input('Nome postazione *')
   m2=st.text_input('Comune *',value=st.session_state.com_tmp)
   m3=st.text_input('Via *',value=st.session_state.via_tmp)
   m7=st.selectbox('Tipologia * (combo con memoria)', st.session_state.tipologie, index=st.session_state.tipologie.index(tipologia_da_usare) if tipologia_da_usare in st.session_state.tipologie else 0)
   m7_new=st.text_input('Nuova tipologia (verra memorizzata)', value='')
  with c2:
   m5=st.text_input('Latitudine *',value=str(st.session_state.lat_tmp))
   m6=st.text_input('Longitudine *',value=str(st.session_state.lon_tmp))
   m8=st.text_input('Responsabile')
  if st.form_submit_button('SALVA POSTAZIONE'):
   if m1:
    tipo_finale=m7_new if m7_new else m7
    if tipo_finale not in st.session_state.tipologie and tipo_finale:
     st.session_state.tipologie.append(tipo_finale)
     save_json(FT,st.session_state.tipologie)
    nuovo={'Postazione':m1,'Comune':m2,'Via':m3,'Lat':m5,'Lon':m6,'Tipo':tipo_finale,'Resp':m8}
    st.session_state.post.append(nuovo)
    save_json(FP,st.session_state.post)
    st.success(f'Salvata {m1} - {m2} {m3} - {tipo_finale}')
    st.rerun()

 if st.session_state.post:
  st.dataframe(pd.DataFrame(st.session_state.post))

elif scelta=='Libreria Icone':
 torna()
 st.markdown('#### LIBRERIA ICONE')
 with st.form('lib'):
  n1=st.text_input('Nome icona *')
  n2=st.selectbox('Tipologia',st.session_state.tipologie)
  n3=st.selectbox('Colore', ['blue','red','green','orange','darkred','purple','black'])
  up=st.file_uploader('PNG',type=['png','jpg'])
  icon_path=''
  if up:
   os.makedirs('icone',exist_ok=True)
   icon_path=f"icone/{up.name}"
   with open(icon_path,'wb') as f:
    f.write(up.getbuffer())
   st.image(up,width=50)
  if st.form_submit_button('SALVA'):
   if n1:
    nuovo={'nome':n1,'tipo':n2,'col':n3,'file':icon_path}
    st.session_state.icone.append(nuovo)
    save_json(FI,st.session_state.icone)
    st.success(f'Aggiunta {n1}')
    st.rerun()

elif scelta=='Backup':
 torna()
 st.markdown('#### BACKUP')
 if st.button('CREA BACKUP'):
  out=BytesIO()
  with pd.ExcelWriter(out,engine='openpyxl') as writer:
   if st.session_state.post:
    pd.DataFrame(st.session_state.post).to_excel(writer,sheet_name='Mappa',index=False)
   if st.session_state.tipologie:
    pd.DataFrame(st.session_state.tipologie,columns=['Tipologia']).to_excel(writer,sheet_name='Tipologie',index=False)
  st.session_state['bk']=out.getvalue()
 if 'bk' in st.session_state:
  st.download_button('SCARICA',st.session_state['bk'],file_name='BACKUP.xlsx')

else:
 torna()
 st.markdown(f'#### {scelta}')
 st.info('Sezione in sviluppo')
