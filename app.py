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
  url=f'https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=jsonv2&accept-language=it'
  r=requests.get(url,headers={'User-Agent':'ana-varese'},timeout=6)
  if r.status_code==200:
   j=r.json()
   a=j.get('address',{})
   com=a.get('city') or a.get('town') or a.get('village') or a.get('municipality') or ''
   via=a.get('road') or a.get('pedestrian') or a.get('footway') or ''
   num=a.get('house_number') or ''
   return com, f"{via} {num}".strip()
 except:
  pass
 return '',''

FD='dati.json'; FU='utenti.json'; FP='post.json'
FI='icone.json'; FT='tipologie.json'
FE='eventi.json'; FR='radio.json'
FC='check.json'; FB='brog.json'
FO='consegna.json'; FM='emerg.json'

for k,v in [
 ('dati',[]),('post',[]),('icone',[]),('tipologie',[]),
 ('eventi',[]),('radio',[]),('check',[]),('brog',[]),
 ('consegna',[]),('emerg',[]),('menu','Dashboard'),
 ('auth',False),('lat_tmp',45.8205),('lon_tmp',8.8250),
 ('com_tmp',''),('via_tmp',''),('clicks',[])
]:
 if k not in st.session_state:
  st.session_state[k]=v

st.session_state.dati=load_json(FD,[])
st.session_state.post=load_json(FP,[])
st.session_state.icone=load_json(FI,[])
st.session_state.utenti=load_json(FU,[])
st.session_state.tipologie=load_json(FT,[])
st.session_state.eventi=load_json(FE,[])
st.session_state.radio=load_json(FR,[])
st.session_state.check=load_json(FC,[])
st.session_state.brog=load_json(FB,[])
st.session_state.consegna=load_json(FO,[])
st.session_state.emerg=load_json(FM,[])

if not st.session_state.utenti:
 st.session_state.utenti=[{'username':'admin','password':hash_pwd('ana2024')}]
 save_json(FU,st.session_state.utenti)

if not st.session_state.tipologie:
 st.session_state.tipologie=['Presidio','Blocco stradale','Punto ritrovo','Area emergenza','Parcheggio','Sanitario','Logistica','Radio','Mensa','Altro']
 save_json(FT,st.session_state.tipologie)

if not st.session_state.icone:
 st.session_state.icone=[
  {'nome':'Presidio','tipo':'Presidio','col':'blue','file':''},
  {'nome':'Blocco','tipo':'Blocco stradale','col':'red','file':''},
  {'nome':'Sanitario','tipo':'Sanitario','col':'green','file':''},
  {'nome':'Logistica','tipo':'Logistica','col':'orange','file':''}
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
 c1,c2,c3=st.columns(3)
 with c1:
  if st.button('VOLONTARI',use_container_width=True):
   st.session_state.menu='Volontari'; st.rerun()
  if st.button('MAPPA',use_container_width=True):
   st.session_state.menu='Mappa'; st.rerun()
  if st.button('LIBRERIA ICONE',use_container_width=True):
   st.session_state.menu='Libreria Icone'; st.rerun()
  if st.button('EVENTI',use_container_width=True):
   st.session_state.menu='Eventi'; st.rerun()
 with c2:
  if st.button('RADIO',use_container_width=True):
   st.session_state.menu='Radio'; st.rerun()
  if st.button('CHECK-IN',use_container_width=True):
   st.session_state.menu='Check'; st.rerun()
  if st.button('BROGLIACCIO',use_container_width=True):
   st.session_state.menu='Brogliaccio'; st.rerun()
  if st.button('CONSEGNA',use_container_width=True):
   st.session_state.menu='Consegna'; st.rerun()
 with c3:
  if st.button('EMERGENZE',use_container_width=True):
   st.session_state.menu='Emergenze'; st.rerun()
  if st.button('BACKUP',use_container_width=True):
   st.session_state.menu='Backup'; st.rerun()
 st.divider()
 c1,c2,c3,c4=st.columns(4)
 c1.metric('Vol',len(st.session_state.dati))
 c2.metric('Post',len(st.session_state.post))
 c3.metric('Icone',len(st.session_state.icone))
 c4.metric('Tipi',len(st.session_state.tipologie))

elif scelta=='Mappa':
 torna()
 st.markdown('#### MAPPA - CLICCA PER FISSARE POSTAZIONE')
 st.info('Clicca sulla mappa: Comune, Via, Latitudine, Longitudine vanno in automatico nella maschera sotto. Puoi mettere piu postazioni.')

 st.markdown('##### ICONA DA LIBRERIA')
 icon_names=[f"{ic.get('nome','')} - {ic.get('tipo','')} ({ic.get('col','')})" for ic in st.session_state.icone]
 sel_icon_idx=0
 if icon_names:
  sel_icon_str=st.selectbox('Seleziona icona da libreria', icon_names, index=0)
  sel_icon_idx=icon_names.index(sel_icon_str)
  ic=st.session_state.icone[sel_icon_idx]
  c1,c2=st.columns([1,4])
  with c1:
   fp=ic.get('file','')
   if fp and os.path.exists(fp):
    st.image(fp,width=50)
   else:
    st.write(f"Colore: {ic.get('col','')}")
  with c2:
   st.write(f"**{ic.get('nome','')}** - Tipo: {ic.get('tipo','')}")
 else:
  st.warning('Libreria vuota - vai in Libreria Icone')

 st.markdown('##### TIPOLOGIA COMBO CON MEMORIA')
 c1,c2=st.columns([2,1])
 with c1:
  sel_tipo=st.selectbox('Tipologia esistente', st.session_state.tipologie, key='sel_tip')
 with c2:
  new_tipo=st.text_input('Nuova tipologia', key='new_tip')
  if st.button('AGGIUNGI TIPOLOGIA'):
   if new_tipo and new_tipo not in st.session_state.tipologie:
    st.session_state.tipologie.append(new_tipo)
    save_json(FT,st.session_state.tipologie)
    st.success(f'Memorizzata {new_tipo}')
    st.rerun()
 tipologia_da_usare=new_tipo if new_tipo else sel_tipo

 st.divider()
 col_a,col_b=st.columns([2,1])
 with col_a:
  lat_c=st.session_state.lat_tmp
  lon_c=st.session_state.lon_tmp

  if HAS_FOLIUM:
   m=folium.Map(location=[lat_c,lon_c], zoom_start=16, tiles='OpenStreetMap')
   ic=st.session_state.icone[sel_icon_idx] if st.session_state.icone else {'col':'green','file':''}
   fp=ic.get('file','') if st.session_state.icone else ''
   if fp and os.path.exists(fp):
    folium.Marker([lat_c,lon_c], popup='Nuova', tooltip='Clicca per spostare', icon=folium.CustomIcon(fp, icon_size=(32,32))).add_to(m)
   else:
    col=ic.get('col','green') if st.session_state.icone else 'green'
    folium.Marker([lat_c,lon_c], popup='Nuova', tooltip='Clicca per spostare', icon=folium.Icon(color=col, icon='plus')).add_to(m)
   for p in st.session_state.post:
    try:
     la=float(p.get('Lat','0')); lo=float(p.get('Lon','0'))
     nome=p.get('Postazione',''); fp2=p.get('IconaFile',''); col2=p.get('Col','blue')
     if fp2 and os.path.exists(fp2):
      folium.Marker([la,lo], popup=nome, tooltip=nome, icon=folium.CustomIcon(fp2, icon_size=(28,28))).add_to(m)
     else:
      folium.Marker([la,lo], popup=nome, tooltip=nome, icon=folium.Icon(color=col2)).add_to(m)
    except:
     pass
   out=st_folium(m, height=480, width=700, key='map1')
   if out and out.get('last_clicked'):
    nl=out['last_clicked']['lat']; ng=out['last_clicked']['lng']
    if abs(nl-lat_c)>0.000001:
     st.session_state.lat_tmp=nl; st.session_state.lon_tmp=ng
     com,via=get_addr(nl,ng)
     st.session_state.com_tmp=com; st.session_state.via_tmp=via
     st.session_state.clicks.append({'lat':nl,'lon':ng,'com':com,'via':via})
     st.rerun()
  else:
   df=pd.DataFrame({'lat':[lat_c],'lon':[lon_c]})
   st.map(df, zoom=15)

 with col_b:
  st.write('1. Seleziona icona libreria')
  st.write('2. Clicca mappa')
  st.write('3. Comune Via Lat Lon auto')
  st.write('4. Salva sotto')
  st.write('5. Clicca ancora per altre')
  st.metric('Click temp', len(st.session_state.clicks))
  if st.button('CENTRA VARESE'):
   st.session_state.lat_tmp=45.8205; st.session_state.lon_tmp=8.8250
   st.session_state.com_tmp=''; st.session_state.via_tmp=''; st.rerun()
  if st.button('PULISCI TEMP'):
   st.session_state.clicks=[]; st.rerun()

 st.divider()
 st.markdown('##### MASCHERA - AGGANCIA AUTOMATICAMENTE')
 with st.form('g'):
  st.markdown('**Campi si riempiono da soli quando clicchi**')
  c1,c2=st.columns(2)
  with c1:
   m1=st.text_input('Nome postazione *', value='', placeholder='Es: Presidio Piazza Monte Grappa')
   m2=st.text_input('Comune *', value=st.session_state.com_tmp, placeholder='Si riempie dal click')
   m3=st.text_input('Via *', value=st.session_state.via_tmp, placeholder='Si riempie dal click')
   m7=st.selectbox('Tipologia *', st.session_state.tipologie, index=st.session_state.tipologie.index(tipologia_da_usare) if tipologia_da_usare in st.session_state.tipologie else 0)
   m7_new=st.text_input('Nuova tipologia (memorizza al salvataggio)', value='')
  with c2:
   m5=st.text_input('Latitudine *', value=str(st.session_state.lat_tmp) if st.session_state.com_tmp else '', placeholder='Click su mappa')
   m6=st.text_input('Longitudine *', value=str(st.session_state.lon_tmp) if st.session_state.com_tmp else '', placeholder='Click su mappa')
   m8=st.text_input('Responsabile')
   ic_sel=st.session_state.icone[sel_icon_idx] if st.session_state.icone else {'nome':'Nessuna','col':'blue','file':''}
   st.write(f"Icona: {ic_sel.get('nome','')} - {ic_sel.get('col','')}")
   m10=st.text_area('Note')
  if st.form_submit_button('SALVA POSTAZIONE CON ICONA LIBRERIA'):
   if m1:
    tipo_finale=m7_new if m7_new else m7
    if tipo_finale not in st.session_state.tipologie and tipo_finale:
     st.session_state.tipologie.append(tipo_finale)
     save_json(FT,st.session_state.tipologie)
    ic=st.session_state.icone[sel_icon_idx] if st.session_state.icone else {'col':'blue','file':''}
    nuovo={'Postazione':m1,'Comune':m2,'Via':m3,'Lat':m5,'Lon':m6,'Tipo':tipo_finale,'Col':ic.get('col','blue'),'IconaFile':ic.get('file',''),'IconaNome':ic.get('nome',''),'Resp':m8,'Note':m10}
    st.session_state.post.append(nuovo)
    save_json(FP,st.session_state.post)
    st.success(f'Salvata {m1} - {m2} {m3} con icona {ic.get("nome","")}')
    st.rerun()

 st.divider()
 if st.session_state.post:
  st.dataframe(pd.DataFrame(st.session_state.post))

elif scelta=='Libreria Icone':
 torna()
 st.markdown('#### LIBRERIA ICONE')
 with st.form('lib'):
  c1,c2=st.columns(2)
  with c1:
   n1=st.text_input('Nome icona *')
   n2=st.selectbox('Tipologia', st.session_state.tipologie)
   n3=st.selectbox('Colore', ['blue','red','green','orange','darkred','purple','black'])
  with c2:
   up=st.file_uploader('Carica PNG', type=['png','jpg','jpeg'])
   icon_path=''
   if up:
    os.makedirs('icone',exist_ok=True)
    icon_path=f"icone/{up.name}"
    with open(icon_path,'wb') as f:
     f.write(up.getbuffer())
    st.image(up,width=60)
  if st.form_submit_button('SALVA IN LIBRERIA'):
   if n1:
    nuovo={'nome':n1,'tipo':n2,'col':n3,'file':icon_path}
    st.session_state.icone.append(nuovo)
    save_json(FI,st.session_state.icone)
    st.success(f'Icona {n1} salvata')
    st.rerun()
 if st.session_state.icone:
  cols=st.columns(4)
  for i,ic in enumerate(st.session_state.icone):
   with cols[i%4]:
    fp=ic.get('file','')
    if fp and os.path.exists(fp):
     st.image(fp,width=50)
    st.write(f"**{ic.get('nome','')}**")
    st.caption(f"{ic.get('tipo','')} - {ic.get('col','')}")
    if st.button('Elimina', key=f'del{i}'):
     st.session_state.icone.pop(i)
     save_json(FI,st.session_state.icone)
     st.rerun()

elif scelta=='Volontari':
 torna()
 st.markdown('#### VOLONTARI')
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
   if st.session_state.tipologie:
    pd.DataFrame(st.session_state.tipologie,columns=['Tipologia']).to_excel(writer,sheet_name='Tipologie',index=False)
  st.session_state['bk']=out.getvalue()
 if 'bk' in st.session_state:
  st.download_button('SCARICA',st.session_state['bk'],file_name='BACKUP.xlsx')

else:
 torna()
 st.markdown(f'#### {scelta}')
 st.info('Sezione in sviluppo - tutti i form presenti in Dashboard')
