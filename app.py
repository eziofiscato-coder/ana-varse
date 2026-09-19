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
  url=f'https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json'
  r=requests.get(url,headers={'User-Agent':'ana-varese'},timeout=5)
  if r.status_code==200:
   j=r.json()
   a=j.get('address',{})
   com=a.get('city') or a.get('town') or a.get('village') or ''
   via=a.get('road') or ''
   return com,via
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
 st.session_state.utenti=[{'username':'admin','password':hash_pwd('ana2024')}]
 save_json(FU,st.session_state.utenti)

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
 opts=['Dashboard','Volontari','Mappa','Eventi','Radio','Check','Brogliaccio','Consegna','Emergenze','Backup']
 sel=st.radio('Vai a',opts,index=0)
 if sel!=st.session_state.menu:
  st.session_state.menu=sel
  st.rerun()
 if st.button('LOGOUT'):
  st.session_state.auth=False
  st.rerun()

scelta=st.session_state.menu

if scelta=='Dashboard':
 st.markdown('#### DASHBOARD - MENU RAPIDO')
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
  if st.button('EMERGENZE'):
   st.session_state.menu='Emergenze'
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
  if st.button('BACKUP'):
   st.session_state.menu='Backup'
   st.rerun()
 with c3:
  if st.button('CHECK-IN'):
   st.session_state.menu='Check'
   st.rerun()

 c1,c2,c3,c4=st.columns(4)
 with c1:
  st.metric('Vol',len(st.session_state.dati))
 with c2:
  st.metric('Post',len(st.session_state.post))
 with c3:
  st.metric('Check',len(st.session_state.check))
 with c4:
  st.metric('Eventi',len(st.session_state.eventi))

elif scelta=='Volontari':
 torna()
 st.markdown('#### VOLONTARI - TUTTI I FORM')
 t1,t2,t3,t4,t5=st.tabs(['Anagrafica','Residenza','Tesseramento','Abilita','Note'])
 with t1:
  with st.form('b'):
   a1=st.text_input('Nome *')
   a2=st.text_input('Cognome *')
   a4=st.date_input('Nascita',value=date(1980,1,1))
   if st.form_submit_button('SALVA'):
    st.session_state.s1_nome=a1
    st.session_state.s1_cogn=a2
    st.success('OK')
 with t2:
  with st.form('c'):
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
   c1x=st.text_input('Tessera')
   c2x=st.text_input('Ruolo',value='Volontario')
   if st.form_submit_button('SALVA'):
    st.session_state.s3_tess=c1x
    st.session_state.s3_ruolo=c2x
    st.success('OK')
 with t4:
  with st.form('e'):
   d1=st.text_input('Patenti',value='B')
   if st.form_submit_button('SALVA'):
    st.session_state.s4_pat=d1
    st.success('OK')
 with t5:
  with st.form('f'):
   e2=st.text_area('Note')
   if st.form_submit_button('SALVA VOLONTARIO'):
    nome=st.session_state.get('s1_nome','')
    cogn=st.session_state.get('s1_cogn','')
    cell=st.session_state.get('s2_cell','')
    com=st.session_state.get('s2_com','')
    ruolo=st.session_state.get('s3_ruolo','')
    if nome and cell:
     nuovo={'Nome':nome+' '+cogn,'Cell':cell,'Comune':com,'Ruolo':ruolo,'Note':e2}
     st.session_state.dati.append(nuovo)
     save_json(FD,st.session_state.dati)
     st.success('Salvato')
     st.rerun()
 if st.session_state.dati:
  st.dataframe(pd.DataFrame(st.session_state.dati))

elif scelta=='Mappa':
 torna()
 st.markdown('#### MAPPA - CLICCA PER FISSARE + ICONE + TIPOLOGIA')

 tipi=['Presidio','Blocco stradale','Punto ritrovo','Area emergenza','Parcheggio','Segreteria','Radio','Sanitario','Logistica','Mensa','Altro']
 icons=['Rosso','Blu','Verde','Giallo','Nessuna']

 st.markdown('##### ICONE PNG SEGNA POSTAZIONE - SCARICABILI')
 c1,c2,c3,c4=st.columns(4)
 for i,lab in enumerate(icons[:4]):
  with [c1,c2,c3,c4][i]:
   fn=f'icon_{lab.lower()}.png'
   if os.path.exists(fn):
    st.image(fn,width=40)
    with open(fn,'rb') as f:
     st.download_button(f'Scarica {lab}',f.read(),file_name=fn,key=f'd{i}')
   else:
    st.write(lab)

 st.divider()
 st.markdown('##### 1 - MAPPA CLICCABILE - ANTEPRIMA CON POSTAZIONI')
 st.info('Clicca sulla mappa - Comune Via Lat Lon si riempiono automaticamente')

 tipo_map=st.radio('Mappa', ['OpenStreetMap cliccabile','Google Maps','Waze'], horizontal=True)

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
     folium.Marker([la,lo],popup=nome,tooltip=nome,icon=folium.Icon(color='blue')).add_to(m)
    except:
     pass
   out=st_folium(m,height=420,width=700,key='map1')
   if out and out.get('last_clicked'):
    nl=out['last_clicked']['lat']
    ng=out['last_clicked']['lng']
    if abs(nl-lat_man)>0.000001:
     st.session_state.lat_tmp=nl
     st.session_state.lon_tmp=ng
     com,via=get_addr(nl,ng)
     if com:
      st.session_state.com_tmp=com
     if via:
      st.session_state.via_tmp=via
     st.rerun()
  else:
   df_ante=pd.DataFrame({'lat':[lat_man],'lon':[lon_man]})
   st.map(df_ante,zoom=15)

  if tipo_map=='Google Maps':
   url=f'https://www.google.com/maps?q={lat_man},{lon_man}&z=16&output=embed'
   st.components.v1.iframe(url,height=300)
  elif tipo_map=='Waze':
   url=f'https://embed.waze.com/iframe?zoom=16&lat={lat_man}&lon={lon_man}'
   st.components.v1.iframe(url,height=300)

 with col_b:
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
 st.markdown('##### 2 - MASCHERA - COMUNE VIA LAT LON RIEMPITI + TIPOLOGIA COMBO + ICONA')

 with st.form('g'):
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
  if st.form_submit_button('SALVA POSTAZIONE'):
   if m1:
    nuovo={'Postazione':m1,'Comune':m2,'Via':m3,'Lat':m5,'Lon':m6,'Tipo':m7,'Icona':m9,'Resp':m8,'Note':m10}
    st.session_state.post.append(nuovo)
    save_json(FP,st.session_state.post)
    st.success(f'Salvata {m1}')
    st.rerun()

 st.divider()
 st.markdown('##### 3 - ANTEPRIMA MAPPA TUTTE POSTAZIONI')
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
  st.dataframe(pd.DataFrame(st.session_state.post))
 else:
  st.info('Nessuna postazione')

elif scelta=='Eventi':
 torna()
 st.markdown('#### EVENTI')
 with st.form('h'):
  e1=st.text_input('Nome *')
  e2=st.date_input('Data',value=date.today())
  e3=st.text_input('Luogo *')
  e4=st.text_area('Desc')
  if st.form_submit_button('SALVA'):
   if e1:
    nuovo={'Evento':e1,'Data':str(e2),'Luogo':e3,'Desc':e4}
    st.session_state.eventi.append(nuovo)
    save_json(FE,st.session_state.eventi)
    st.success('OK')
    st.rerun()
 if st.session_state.eventi:
  st.dataframe(pd.DataFrame(st.session_state.eventi))

elif scelta=='Radio':
 torna()
 st.markdown('#### RADIO')
 with st.form('i'):
  r1=st.text_input('ID *')
  r2=st.text_input('Modello *')
  r3=st.text_input('Freq',value='446.00625')
  if st.form_submit_button('SALVA'):
   if r1:
    nuovo={'ID':r1,'Mod':r2,'Freq':r3}
    st.session_state.radio.append(nuovo)
    save_json(FR,st.session_state.radio)
    st.success('OK')
    st.rerun()
 if st.session_state.radio:
  st.dataframe(pd.DataFrame(st.session_state.radio))

elif scelta=='Check':
 torna()
 st.markdown('#### CHECK-IN')
 with st.form('j'):
  nomi=[d.get('Nome','') for d in st.session_state.dati]
  if not nomi:
   nomi=['Nessun volontario']
  ch1=st.selectbox('Vol',nomi)
  ch2=st.text_input('Post')
  ch3=st.time_input('Ora',value=datetime.now().time())
  ch4=st.date_input('Data',value=date.today())
  ch7=st.text_area('Note')
  if st.form_submit_button('SALVA'):
   nuovo={'Vol':ch1,'Post':ch2,'Ora':str(ch3),'Data':str(ch4),'Note':ch7}
   st.session_state.check.append(nuovo)
   save_json(FC,st.session_state.check)
   st.success('OK')
   st.rerun()
 if st.session_state.check:
  st.dataframe(pd.DataFrame(st.session_state.check))

elif scelta=='Brogliaccio':
 torna()
 st.markdown('#### BROGLIACCIO')
 with st.form('k'):
  b1=st.text_input('Mitt *')
  b2=st.text_input('Dest *')
  b7=st.text_area('Mess *')
  b4=st.time_input('Ora',value=datetime.now().time())
  b5=st.date_input('Data',value=date.today())
  if st.form_submit_button('SALVA'):
   if b1 and b7:
    nuovo={'Mitt':b1,'Dest':b2,'Ora':str(b4),'Data':str(b5),'Mess':b7}
    st.session_state.brog.append(nuovo)
    save_json(FB,st.session_state.brog)
    st.success('OK')
    st.rerun()
 if st.session_state.brog:
  st.dataframe(pd.DataFrame(st.session_state.brog))

elif scelta=='Consegna':
 torna()
 st.markdown('#### CONSEGNA')
 with st.form('l'):
  ids=[r.get('ID') for r in st.session_state.radio]
  if not ids or ids==[None]:
   ids=['RADIO-01']
  co1=st.selectbox('ID Radio',ids)
  nomi=[d.get('Nome','') for d in st.session_state.dati]
  if not nomi:
   nomi=['Nessun volontario']
  co2=st.selectbox('A',nomi)
  co3=st.date_input('Data',value=date.today())
  co4=st.time_input('Ora',value=datetime.now().time())
  if st.form_submit_button('SALVA'):
   nuovo={'Radio':co1,'Vol':co2,'Data':str(co3),'Ora':str(co4)}
   st.session_state.consegna.append(nuovo)
   save_json(FO,st.session_state.consegna)
   st.success('OK')
   st.rerun()
 if st.session_state.consegna:
  st.dataframe(pd.DataFrame(st.session_state.consegna))

elif scelta=='Emergenze':
 torna()
 st.markdown('#### EMERGENZE')
 with st.form('m'):
  em1=st.text_input('Tipo',value='Alluvione')
  em2=st.text_input('Comune',value='Varese')
  em3=st.text_input('Via *')
  em4=st.text_input('Coord *')
  em5=st.text_area('Desc *')
  if st.form_submit_button('SALVA'):
   if em3:
    nuovo={'Tipo':em1,'Comune':em2,'Via':em3,'Coord':em4,'Desc':em5}
    st.session_state.emerg.append(nuovo)
    save_json(FM,st.session_state.emerg)
    st.success('OK')
    st.rerun()
 if st.session_state.emerg:
  st.dataframe(pd.DataFrame(st.session_state.emerg))

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
   if st.session_state.check:
    pd.DataFrame(st.session_state.check).to_excel(writer,sheet_name='Check',index=False)
   if st.session_state.eventi:
    pd.DataFrame(st.session_state.eventi).to_excel(writer,sheet_name='Eventi',index=False)
  st.session_state['bk']=out.getvalue()
 if 'bk' in st.session_state:
  st.download_button('SCARICA',st.session_state['bk'],file_name='BACKUP.xlsx')
