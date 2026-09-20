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
   # FIX - Comune esatto dove clicchi
   com=a.get('city') or a.get('town') or a.get('village') or a.get('municipality') or a.get('hamlet') or ''
   via=a.get('road') or a.get('pedestrian') or a.get('footway') or ''
   num=a.get('house_number') or ''
   full_via=(via+' '+num).strip()
   return com,full_via
 except:
  pass
 return '',''

FD='dati.json'
FU='utenti.json'
FP='post.json'
FI='icone.json'
FT='tip.json'
FO='odv.json'
FE='emerg.json'
FC='check.json'
FR='radio.json'
FR2='cons.json'

for k,v in [
 ('dati',[]),('post',[]),('icone',[]),
 ('tip',[]),('odv',[]),('emerg',[]),
 ('check',[]),('radio',[]),('cons',[]),
 ('menu','Dashboard'),('auth',False),
 ('lat',45.8205),('lon',8.8250),
 ('com',''),('via',''),
 ('sel',-1),('zoom',16),
 ('clat',None),('clon',None),
 ('prev',-1),('exp1',False),
 ('exp2',False),('exp3',False)
]:
 if k not in st.session_state:
  st.session_state[k]=v

st.session_state.dati=load(FD,[])
st.session_state.post=load(FP,[])
st.session_state.icone=load(FI,[])
st.session_state.tip=load(FT,[])
st.session_state.odv=load(FO,[])
st.session_state.emerg=load(FE,[])
st.session_state.check=load(FC,[])
st.session_state.radio=load(FR,[])
st.session_state.cons=load(FR2,[])
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

if st.session_state.exp1 or st.session_state.exp2 or st.session_state.exp3:
 st.markdown("<style>header{visibility:hidden!important;} [data-testid='stSidebar']{display:none!important;}</style>", unsafe_allow_html=True)
 if st.button('TORNA AL FORM',use_container_width=True,type='primary'):
  st.session_state.exp1=False
  st.session_state.exp2=False
  st.session_state.exp3=False
  st.rerun()
 if st.session_state.exp1:
  st.markdown('## MAPPA SCHERMO INTERO')
  lat_c=st.session_state.lat
  lon_c=st.session_state.lon
  zm=st.session_state.zoom
  if HAS:
   m=folium.Map(location=[lat_c,lon_c],zoom_start=zm,tiles='OpenStreetMap')
   for idx,p in enumerate(st.session_state.post):
    try:
     la=float(p.get('Lat','0'))
     lo=float(p.get('Lon','0'))
     ficon=p.get('IconFile','')
     if ficon and os.path.exists(ficon):
      ic=folium.CustomIcon(ficon,icon_size=(40,40))
      folium.Marker([la,lo],icon=ic).add_to(m)
     else:
      col='red' if idx==st.session_state.sel else 'blue'
      folium.Marker([la,lo],icon=folium.Icon(color=col)).add_to(m)
    except:
     pass
   if st.session_state.clat is not None:
    folium.Marker([st.session_state.clat,st.session_state.clon],icon=folium.Icon(color='green')).add_to(m)
   st_folium(m,height=850,width=1600,key='full1')
 if st.session_state.exp2:
  st.markdown('## MAPPA TUTTE SCHERMO INTERO')
  if HAS and st.session_state.post:
   m2=folium.Map(location=[45.8205,8.8250],zoom_start=11,tiles='OpenStreetMap')
   for p in st.session_state.post:
    try:
     la=float(p.get('Lat','0'))
     lo=float(p.get('Lon','0'))
     ficon=p.get('IconFile','')
     if ficon and os.path.exists(ficon):
      ic=folium.CustomIcon(ficon,icon_size=(35,35))
      folium.Marker([la,lo],icon=ic).add_to(m2)
     else:
      folium.Marker([la,lo],icon=folium.Icon(color='blue')).add_to(m2)
    except:
     pass
   st_folium(m2,height=850,width=1600,key='full2')
 if st.session_state.exp3:
  st.markdown('## ANTEPRIMA SCHERMO INTERO')
  if st.session_state.prev>=0:
   try:
    p=st.session_state.post[st.session_state.prev]
    nome=p.get('Postazione','')
    odv=p.get('ODV','')
    com=p.get('Comune','')
    st.success(f"Post: {nome}")
    st.info(f"Comune: {com} - ODV: {odv}")
    la=float(p.get('Lat','0'))
    lo=float(p.get('Lon','0'))
    if HAS:
     m3=folium.Map(location=[la,lo],zoom_start=19,tiles='OpenStreetMap')
     ficon=p.get('IconFile','')
     if ficon and os.path.exists(ficon):
      ic=folium.CustomIcon(ficon,icon_size=(50,50))
      folium.Marker([la,lo],icon=ic).add_to(m3)
     else:
      folium.Marker([la,lo],icon=folium.Icon(color='red')).add_to(m3)
     st_folium(m3,height=850,width=1600,key='full3')
   except:
    pass
  c1,c2=st.columns(2)
  with c1:
   if st.button('TORNA INDIETRO SENZA VISUALIZZARE',use_container_width=True):
    st.session_state.prev=-1
    st.session_state.sel=-1
    st.session_state.exp3=False
    st.rerun()
  with c2:
   if st.button('CHIUDI',use_container_width=True):
    st.session_state.exp3=False
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
  st.markdown('<h3>DASHBOARD MENU COMPLETO</h3>', unsafe_allow_html=True)
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
   st.metric('Vol',len(st.session_state.dati))
   st.metric('Post',len(st.session_state.post))

 elif scelta=='Volontari':
  torna()
  st.markdown('<h3>VOLONTARI - NOME E COGNOME</h3>', unsafe_allow_html=True)
  with st.form('vol'):
   c1,c2=st.columns(2)
   with c1:
    a1=st.text_input('Nome *',placeholder='Mario')
    a2=st.text_input('Cognome *',placeholder='Rossi')
   with c2:
    a4=st.text_input('Cellulare *',placeholder='3331234567')
    a3=st.selectbox('Ruolo',['Volontario','Caposquadra','Coordinatore','Autista','Radio','Logistica','Segreteria','Sanitario','Altro'])
   if st.form_submit_button('SALVA VOLONTARIO'):
    if a1 and a2:
     nc=a1+' '+a2
     nuovo={'Nome':nc,'NomeSolo':a1,'Cognome':a2,'Cellulare':a4,'Ruolo':a3}
     st.session_state.dati.append(nuovo)
     save(FD,st.session_state.dati)
     st.success(f"Salvato {nc}")
     st.rerun()
  if st.session_state.dati:
   st.dataframe(pd.DataFrame(st.session_state.dati),use_container_width=True)

 elif scelta=='Mappa':
  torna()
  st.markdown('<h3>MAPPA - COMUNE/VIA ESATTI + RESPONSABILE DA VOLONTARI</h3>', unsafe_allow_html=True)

  icon_names=[]
  for it in st.session_state.icone:
   icon_names.append(it.get('nome',''))
  sel_idx=0
  if icon_names:
   sel_str=st.selectbox('Icona PNG da libreria',icon_names,index=0)
   sel_idx=icon_names.index(sel_str)
   try:
    ic_sel=st.session_state.icone[sel_idx]
    fsel=ic_sel.get('file','')
    if fsel and os.path.exists(fsel):
     st.image(fsel,width=60,caption=f"Icona: {ic_sel.get('nome','')}")
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
  st.markdown('##### 1 - MAPPA - CLICCA DOVE VUOI')
  c1,c2=st.columns([3,1])
  with c2:
   if st.button('ESPANDI SCHERMO INTERO',use_container_width=True,key='e1'):
    st.session_state.exp1=True
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
     ficon=p.get('IconFile','')
     if ficon and os.path.exists(ficon):
      ic=folium.CustomIcon(ficon,icon_size=(40,40))
      folium.Marker([la,lo],popup=p.get('Postazione',''),icon=ic).add_to(m)
     else:
      col='red' if idx==st.session_state.sel else 'blue'
      folium.Marker([la,lo],popup=p.get('Postazione',''),icon=folium.Icon(color=col)).add_to(m)
    except:
     pass
   if st.session_state.clat is not None:
    try:
     ic_tmp=st.session_state.icone[sel_idx]
     ftmp=ic_tmp.get('file','')
     if ftmp and os.path.exists(ftmp):
      ic=folium.CustomIcon(ftmp,icon_size=(40,40))
      folium.Marker([st.session_state.clat,st.session_state.clon],popup='NUOVA CON ICONA',icon=ic).add_to(m)
     else:
      folium.Marker([st.session_state.clat,st.session_state.clon],popup='NUOVA',icon=folium.Icon(color='green')).add_to(m)
    except:
     folium.Marker([st.session_state.clat,st.session_state.clon],popup='NUOVA',icon=folium.Icon(color='green')).add_to(m)
   out=st_folium(m,height=450,width=700,key='map1')
   if out and out.get('last_clicked'):
    try:
     nl=out['last_clicked']['lat']
     ng=out['last_clicked']['lng']
     # FIX - Lat/Lon esatti dove clicchi
     st.session_state.lat=nl
     st.session_state.lon=ng
     st.session_state.clat=nl
     st.session_state.clon=ng
     # FIX - Comune/Via esatti dove clicchi
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
   st.write(f"Lat esatto: {round(st.session_state.lat,6)}")
  with c2:
   st.write(f"Lon esatto: {round(st.session_state.lon,6)}")
  with c3:
   st.write(f"Comune esatto: {st.session_state.com}")
  c1,c2=st.columns(2)
  with c1:
   st.write(f"Via esatta: {st.session_state.via}")
  with c2:
   st.caption('Clicca su mappa per aggiornare')

  st.divider()
  st.markdown('##### 2 - MASCHERA - CON RESPONSABILE DA VOLONTARI + COMUNE/VIA ESATTI')

  # FIX - Responsabile agganciato a Volontariato Nome e Cognome
  vol_nomi=[]
  for d in st.session_state.dati:
   nome_completo=d.get('Nome','')
   if nome_completo:
    vol_nomi.append(nome_completo)
  if not vol_nomi:
   vol_nomi=['Nessun volontario - vai in Volontari e inserisci Nome e Cognome']

  with st.form('g'):
   c1,c2=st.columns(2)
   with c1:
    m1=st.text_input('Nome postazione *',placeholder='Es: Presidio centro')
    # FIX - Comune/Via/Lat/Lon esatti
    m2=st.text_input('Comune *',value=st.session_state.com,help='Si compila automatico dove clicchi su mappa')
    m3=st.text_input('Via *',value=st.session_state.via,help='Si compila automatico dove clicchi')
    m4=st.selectbox('Tipologia *',st.session_state.tip)
   with c2:
    m5=st.text_input('Latitudine *',value=str(st.session_state.lat),help='Esatta dove clicchi')
    m6=st.text_input('Longitudine *',value=str(st.session_state.lon),help='Esatta dove clicchi')
    # FIX - Responsabile agganciato a form volontariato
    m8=st.selectbox('Responsabile * (da Volontari Nome e Cognome)',vol_nomi)
    m9=st.selectbox('ODV operante *',st.session_state.odv)
    m9_new=st.text_input('Nuova ODV se non in lista')
   if st.form_submit_button('SALVA POSTAZIONE CON ICONA PNG'):
    if m1:
     odv_f=m9_new if m9_new else m9
     if odv_f not in st.session_state.odv and odv_f:
      st.session_state.odv.append(odv_f)
      save(FO,st.session_state.odv)
     ic=st.session_state.icone[sel_idx] if st.session_state.icone else {'col':'blue','file':'','nome':''}
     nuovo={
      'Postazione':m1,
      'Comune':m2,
      'Via':m3,
      'Lat':m5,
      'Lon':m6,
      'Responsabile':m8,
      'ODV':odv_f,
      'Tipo':m4,
      'Icona':ic.get('nome',''),
      'IconFile':ic.get('file',''),
      'Col':ic.get('col','blue')
     }
     st.session_state.post.append(nuovo)
     save(FP,st.session_state.post)
     st.session_state.clat=None
     st.session_state.clon=None
     st.success(f"Salvata {m1} a {m2} Resp {m8}")
     st.rerun()

  st.divider()
  st.markdown('##### 3 - MAPPA TUTTE LE POSTAZIONI')
  c1,c2=st.columns([3,1])
  with c2:
   if st.button('ESPANDI SCHERMO INTERO',use_container_width=True,key='e2'):
    st.session_state.exp2=True
    st.rerun()
  if st.session_state.post and HAS:
   m2=folium.Map(location=[45.8205,8.8250],zoom_start=11,tiles='OpenStreetMap')
   for p in st.session_state.post:
    try:
     la=float(p.get('Lat','0'))
     lo=float(p.get('Lon','0'))
     ficon=p.get('IconFile','')
     if ficon and os.path.exists(ficon):
      ic=folium.CustomIcon(ficon,icon_size=(35,35))
      folium.Marker([la,lo],popup=p.get('Postazione','')+'<br>ODV: '+p.get('ODV',''),icon=ic).add_to(m2)
     else:
      folium.Marker([la,lo],popup=p.get('Postazione',''),icon=folium.Icon(color='blue')).add_to(m2)
    except:
     pass
   st_folium(m2,height=400,width=700,key='m2')

  st.divider()
  st.markdown('##### 4 - ELENCO POSTAZIONI CON ICONA PNG E RESPONSABILE')

  if st.session_state.post:
   for idx,p in enumerate(st.session_state.post):
    c1,c2,c3,c4,c5=st.columns([1,2,1,1,1])
    with c1:
     ficon=p.get('IconFile','')
     if ficon and os.path.exists(ficon):
      try:
       st.image(ficon,width=40)
      except:
       st.write('Icon')
     else:
      st.write(p.get('Icona',''))
    with c2:
     nome=p.get('Postazione','')
     com=p.get('Comune','')
     via=p.get('Via','')
     odv=p.get('ODV','')
     resp=p.get('Responsabile','')
     st.write(f"{nome} - {com} - {via} - ODV {odv} - Resp {resp}")
    with c3:
     if st.button('Vedi',key=f'vedi_{idx}'):
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
     if st.button('Ante',key=f'ante_{idx}'):
      st.session_state.prev=idx
      st.rerun()
    with c5:
     if st.button('Indietro',key=f'back_{idx}'):
      st.session_state.prev=-1
      st.session_state.sel=-1
      st.rerun()

   st.divider()
   st.dataframe(pd.DataFrame(st.session_state.post),use_container_width=True)

   if st.session_state.prev>=0:
    try:
     p=st.session_state.post[st.session_state.prev]
     nome=p.get('Postazione','')
     icona=p.get('Icona','')
     com=p.get('Comune','')
     via=p.get('Via','')
     odv=p.get('ODV','')
     resp=p.get('Responsabile','')
     lat=p.get('Lat','')
     lon=p.get('Lon','')
     st.success(f"Postazione: {nome} - Icona: {icona}")
     st.info(f"Comune: {com} - Via: {via}")
     st.info(f"Lat: {lat} - Lon: {lon} - ODV: {odv} - Responsabile: {resp}")
     fprev=p.get('IconFile','')
     if fprev and os.path.exists(fprev):
      st.image(fprev,width=80,caption=f"Icona: {icona}")

     c1,c2,c3=st.columns(3)
     with c1:
      if st.button('ESPANDI ANTEPRIMA',use_container_width=True,key='exp_prev'):
       st.session_state.exp3=True
       st.rerun()
     with c2:
      if st.button('TORNA INDIETRO SENZA VISUALIZZARE',use_container_width=True,key='back_no'):
       st.session_state.prev=-1
       st.session_state.sel=-1
       st.rerun()
     with c3:
      if st.button('CHIUDI',use_container_width=True,key='close_prev'):
       st.session_state.prev=-1
       st.rerun()

     la=float(p.get('Lat','0'))
     lo=float(p.get('Lon','0'))
     if HAS:
      m_prev=folium.Map(location=[la,lo],zoom_start=19,tiles='OpenStreetMap')
      if fprev and os.path.exists(fprev):
       ic=folium.CustomIcon(fprev,icon_size=(50,50))
       folium.Marker([la,lo],icon=ic).add_to(m_prev)
      else:
       folium.Marker([la,lo],icon=folium.Icon(color='red')).add_to(m_prev)
      st_folium(m_prev,height=350,width=700,key='mprev')
    except:
     pass

 elif scelta=='Libreria Icone':
  torna()
  st.markdown('#### LIBRERIA ICONE - UPLOAD PNG')
  with st.form('lib_form'):
   c1,c2=st.columns(2)
   with c1:
    n1=st.text_input('Nome icona *')
    n3=st.selectbox('Colore',['blue','red','green','orange','black'])
   with c2:
    up_file=st.file_uploader('Carica PNG',type=['png','jpg','jpeg'],key='single_png')
   if st.form_submit_button('SALVA ICONA'):
    if n1:
     fname=''
     if up_file is not None:
      os.makedirs('icone',exist_ok=True)
      fname=f"icone/{n1}_{up_file.name}"
      with open(fname,'wb') as f:
       f.write(up_file.getbuffer())
     nuovo={'nome':n1,'col':n3,'file':fname}
     st.session_state.icone.append(nuovo)
     save(FI,st.session_state.icone)
     st.success('Salvata')
     st.rerun()
  st.divider()
  st.markdown('##### CARICA MULTIPLA PNG')
  multi=st.file_uploader('Carica piu PNG',type=['png','jpg','jpeg'],accept_multiple_files=True,key='multi_png')
  if multi:
   if st.button('CARICA TUTTE'):
    os.makedirs('icone',exist_ok=True)
    for mf in multi:
     fname=f"icone/{mf.name}"
     with open(fname,'wb') as f:
      f.write(mf.getbuffer())
     nome=mf.name.split('.')[0]
     st.session_state.icone.append({'nome':nome,'col':'blue','file':fname})
    save(FI,st.session_state.icone)
    st.success('Caricate')
    st.rerun()
  st.divider()
  if st.session_state.icone:
   for idx,ic in enumerate(st.session_state.icone):
    c1,c2,c3,c4=st.columns([2,1,2,1])
    with c1:
     st.write(f"{ic.get('nome','')}")
    with c2:
     f=ic.get('file','')
     if f and os.path.exists(f):
      try:
       st.image(f,width=50)
      except:
       st.write('Img')
    with c3:
     st.write(ic.get('file',''))
    with c4:
     if st.button('Elimina',key=f'del_{idx}'):
      st.session_state.icone.pop(idx)
      save(FI,st.session_state.icone)
      st.rerun()

 elif scelta=='Emergenza':
  torna()
  st.markdown('#### EMERGENZA')
  with st.form('emerg'):
   e1=st.text_input('Nome emergenza *')
   e2=st.text_input('Luogo *')
   e3=st.selectbox('Tipo',['Alluvione','Terremoto','Incendio','Neve','Altro'])
   if st.form_submit_button('SALVA'):
    if e1:
     nuovo={'Emergenza':e1,'Luogo':e2,'Tipo':e3}
     st.session_state.emerg.append(nuovo)
     save(FE,st.session_state.emerg)
     st.success('Salvata')
     st.rerun()
  if st.session_state.emerg:
   st.dataframe(pd.DataFrame(st.session_state.emerg))

 elif scelta=='Check In':
  torna()
  st.markdown('#### CHECK IN')
  vol_list=[]
  for d in st.session_state.dati:
   vol_list.append(d.get('Nome',''))
  if not vol_list:
   vol_list=['Nessuno']
  with st.form('check'):
   c1=st.text_input('Data',value='2026-05-13')
   c2=st.selectbox('Volontario',vol_list)
   c3=st.selectbox('Stato',['Presente','Assente','In servizio'])
   if st.form_submit_button('REGISTRA'):
    nuovo={'Data':c1,'Vol':c2,'Stato':c3}
    st.session_state.check.append(nuovo)
    save(FC,st.session_state.check)
    st.success('Registrato')
    st.rerun()
  if st.session_state.check:
   st.dataframe(pd.DataFrame(st.session_state.check))

 elif scelta=='DB Radio':
  torna()
  st.markdown('#### DB RADIO')
  with st.form('radio'):
   r1=st.text_input('Nome radio *')
   r2=st.text_input('Frequenza *')
   if st.form_submit_button('SALVA'):
    if r1:
     nuovo={'Radio':r1,'Freq':r2}
     st.session_state.radio.append(nuovo)
     save(FR,st.session_state.radio)
     st.success('Salvata')
     st.rerun()
  if st.session_state.radio:
   st.dataframe(pd.DataFrame(st.session_state.radio))

 elif scelta=='Consegna Radio':
  torna()
  st.markdown('#### CONSEGNA RADIO')
  vol_list=[]
  for d in st.session_state.dati:
   vol_list.append(d.get('Nome',''))
  if not vol_list:
   vol_list=['Nessuno']
  radio_list=[]
  for r in st.session_state.radio:
   radio_list.append(r.get('Radio',''))
  if not radio_list:
   radio_list=['Nessuna radio']
  with st.form('cons'):
   cr1=st.selectbox('Volontario',vol_list)
   cr2=st.selectbox('Radio',radio_list)
   cr3=st.text_input('Data',value='2026-05-13')
   cr5=st.selectbox('Stato',['Consegnata','Riconsegnata','In uso'])
   if st.form_submit_button('SALVA CONSEGNA'):
    nuovo={'Vol':cr1,'Radio':cr2,'Data':cr3,'Stato':cr5}
    st.session_state.cons.append(nuovo)
    save(FR2,st.session_state.cons)
    st.success('Consegnata')
    st.rerun()
  if st.session_state.cons:
   st.dataframe(pd.DataFrame(st.session_state.cons))

 elif scelta=='Backup':
  torna()
  st.markdown('#### BACKUP')
  if st.button('CREA BACKUP'):
   out=BytesIO()
   with pd.ExcelWriter(out,engine='openpyxl') as writer:
    if st.session_state.post:
     pd.DataFrame(st.session_state.post).to_excel(writer,sheet_name='Mappa',index=False)
    if st.session_state.dati:
     pd.DataFrame(st.session_state.dati).to_excel(writer,sheet_name='Volontari',index=False)
    if st.session_state.cons:
     pd.DataFrame(st.session_state.cons).to_excel(writer,sheet_name='ConsegnaRadio',index=False)
   st.session_state['bk']=out.getvalue()
  if 'bk' in st.session_state:
   st.download_button('SCARICA',st.session_state['bk'],file_name='BACKUP.xlsx')
