import streamlit as st
import pandas as pd
from io import BytesIO
import os, json, hashlib
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

FD='dati.json'
FU='utenti.json'
FP='post.json'
FI='icone.json'

if 'dati' not in st.session_state:
 st.session_state.dati=[]
if 'post' not in st.session_state:
 st.session_state.post=[]
if 'icone' not in st.session_state:
 st.session_state.icone=[]
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
if 'icon_sel' not in st.session_state:
 st.session_state.icon_sel='Presidio'

st.session_state.dati=load_json(FD,[])
st.session_state.post=load_json(FP,[])
st.session_state.icone=load_json(FI,[])
st.session_state.utenti=load_json(FU,[])

if not st.session_state.utenti:
 st.session_state.utenti=[{'username':'admin','password':hash_pwd('ana2024')}]
 save_json(FU,st.session_state.utenti)

if not st.session_state.icone:
 st.session_state.icone=[
  {'nome':'Presidio','file':'','tipo':'Presidio','col':'blue'},
  {'nome':'Blocco','file':'','tipo':'Blocco stradale','col':'red'},
  {'nome':'Sanitario','file':'','tipo':'Sanitario','col':'green'},
  {'nome':'Logistica','file':'','tipo':'Logistica','col':'orange'},
  {'nome':'Emergenza','file':'','tipo':'Area emergenza','col':'darkred'}
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
 opts=['Dashboard','Volontari','Mappa','Libreria Icone','Emergenze','Backup']
 sel=st.radio('Vai a',opts,index=0)
 if sel!=st.session_state.menu:
  st.session_state.menu=sel
  st.rerun()

scelta=st.session_state.menu

if scelta=='Dashboard':
 st.markdown('#### DASHBOARD - MENU RAPIDO')
 c1,c2=st.columns(2)
 with c1:
  if st.button('MAPPA'):
   st.session_state.menu='Mappa'
   st.rerun()
  if st.button('LIBRERIA ICONE'):
   st.session_state.menu='Libreria Icone'
   st.rerun()
 with c2:
  if st.button('EMERGENZE'):
   st.session_state.menu='Emergenze'
   st.rerun()
  if st.button('BACKUP'):
   st.session_state.menu='Backup'
   st.rerun()
 st.metric('Postazioni',len(st.session_state.post))
 st.metric('Icone libreria',len(st.session_state.icone))

elif scelta=='Libreria Icone':
 torna()
 st.markdown('#### LIBRERIA ICONE - USABILE PER POSTAZIONI ED EMERGENZE')
 st.info('Qui crei la libreria - poi la usi in Mappa ed Emergenze')

 with st.form('lib'):
  st.markdown('**Nuova icona libreria**')
  c1,c2=st.columns(2)
  with c1:
   n1=st.text_input('Nome icona *',value='')
   n2=st.selectbox('Tipologia', ['Presidio','Blocco stradale','Sanitario','Logistica','Area emergenza','Parcheggio','Radio','Mensa','Altro'], index=0)
   n3=st.selectbox('Colore marker', ['blue','red','green','orange','darkred','purple','black'], index=0)
  with c2:
   n4=st.text_area('Descrizione')
   up=st.file_uploader('Carica PNG (opzionale)',type=['png','jpg'])
   icon_file=''
   if up:
    os.makedirs('icone',exist_ok=True)
    icon_file=f"icone/{up.name}"
    with open(icon_file,'wb') as f:
     f.write(up.getbuffer())
    st.image(up,width=60)
    st.success(f'Salvata {icon_file}')

  if st.form_submit_button('SALVA IN LIBRERIA'):
   if n1:
    nuovo={'nome':n1,'file':icon_file,'tipo':n2,'col':n3,'desc':n4}
    st.session_state.icone.append(nuovo)
    save_json(FI,st.session_state.icone)
    st.success(f'Icona {n1} aggiunta')
    st.rerun()

 st.divider()
 st.markdown('##### LIBRERIA ATTUALE')
 if st.session_state.icone:
  cols=st.columns(3)
  for i,ic in enumerate(st.session_state.icone):
   with cols[i%3]:
    st.write(f"**{ic.get('nome','')}** - {ic.get('tipo','')}")
    fp=ic.get('file','')
    if fp and os.path.exists(fp):
     st.image(fp,width=50)
    else:
     st.write(f"Colore: {ic.get('col','blue')}")
    st.caption(ic.get('desc',''))
    if st.button(f"Elimina {ic.get('nome','')}",key=f"del_{i}"):
     st.session_state.icone.pop(i)
     save_json(FI,st.session_state.icone)
     st.rerun()
 else:
  st.info('Libreria vuota - aggiungi icone sopra')

elif scelta=='Mappa':
 torna()
 st.markdown('#### MAPPA - CLICCA PER FISSARE CON ICONA PNG LIBRERIA')

 # Seleziona icona dalla libreria
 st.markdown('##### SELEZIONA ICONA DALLA LIBRERIA')
 icon_names=[f"{ic.get('nome','')} ({ic.get('tipo','')})" for ic in st.session_state.icone]
 if icon_names:
  sel_icon=st.selectbox('Icona da usare per fissare', icon_names, index=0, key='sel_lib')
  idx=icon_names.index(sel_icon)
  icone_sel=st.session_state.icone[idx]
  st.write(f"Usi: {icone_sel.get('nome','')} - Colore: {icone_sel.get('col','')}")
  fp=icone_sel.get('file','')
  if fp and os.path.exists(fp):
   st.image(fp,width=40)
   st.session_state.icon_sel=fp
  else:
   st.session_state.icon_sel=icone_sel.get('col','blue')
 else:
  st.warning('Vai in Libreria Icone e crea icone')

 st.divider()
 st.markdown('##### MAPPA CLICCABILE - CLICCA PER FISSARE')

 col_a,col_b=st.columns([2,1])
 with col_a:
  lat_c=st.session_state.lat_tmp
  lon_c=st.session_state.lon_tmp
  lat_man=st.number_input('Lat',value=float(lat_c),format='%.6f',key='la')
  lon_man=st.number_input('Lon',value=float(lon_c),format='%.6f',key='lo')
  st.session_state.lat_tmp=lat_man
  st.session_state.lon_tmp=lon_man

  if HAS_FOLIUM:
   m=folium.Map(location=[lat_man,lon_man],zoom_start=16,tiles='OpenStreetMap')
   # Marker nuova con icona libreria
   ic_sel=st.session_state.icon_sel
   if isinstance(ic_sel,str) and ic_sel.endswith('.png') and os.path.exists(ic_sel):
    folium.Marker([lat_man,lon_man],popup='Nuova',tooltip='Nuova - clicca per spostare',icon=folium.CustomIcon(ic_sel,icon_size=(32,32))).add_to(m)
   else:
    folium.Marker([lat_man,lon_man],popup='Nuova',tooltip='Clicca per spostare',icon=folium.Icon(color='green',icon='plus')).add_to(m)

   # Postazioni esistenti con icone libreria
   for p in st.session_state.post:
    try:
     la=float(p.get('Lat','0'))
     lo=float(p.get('Lon','0'))
     nome=p.get('Postazione','')
     ico=p.get('IconaFile','')
     col=p.get('IconaCol','blue')
     if ico and os.path.exists(ico):
      folium.Marker([la,lo],popup=nome,tooltip=nome,icon=folium.CustomIcon(ico,icon_size=(32,32))).add_to(m)
     else:
      folium.Marker([la,lo],popup=nome,tooltip=nome,icon=folium.Icon(color=col)).add_to(m)
    except:
     pass

   out=st_folium(m,height=420,width=700,key='m1')
   if out and out.get('last_clicked'):
    nl=out['last_clicked']['lat']
    ng=out['last_clicked']['lng']
    if abs(nl-lat_man)>0.000001:
     st.session_state.lat_tmp=nl
     st.session_state.lon_tmp=ng
     st.rerun()
  else:
   df=pd.DataFrame({'lat':[lat_man],'lon':[lon_man]})
   st.map(df,zoom=15)

 with col_b:
  st.write(f"Lat: {lat_man:.6f}")
  st.write(f"Lon: {lon_man:.6f}")
  if st.button('CENTRA VARESE'):
   st.session_state.lat_tmp=45.8205
   st.session_state.lon_tmp=8.8250
   st.rerun()

 st.divider()
 st.markdown('##### MASCHERA - COMUNE VIA LAT LON + ICONA LIBRERIA')

 with st.form('b'):
  c1,c2=st.columns(2)
  with c1:
   m1=st.text_input('Nome postazione *')
   m2=st.text_input('Comune *',value=st.session_state.com_tmp)
   m3=st.text_input('Via *',value=st.session_state.via_tmp)
   m7=st.text_input('Tipologia',value=icone_sel.get('tipo','') if 'icone_sel' in locals() else 'Presidio')
  with c2:
   m5=st.text_input('Lat *',value=str(st.session_state.lat_tmp))
   m6=st.text_input('Lon *',value=str(st.session_state.lon_tmp))
   m8=st.text_input('Resp')
   m9=st.text_input('Icona file',value=icone_sel.get('file','') if 'icone_sel' in locals() else '')
   m10=st.text_input('Icona colore',value=icone_sel.get('col','blue') if 'icone_sel' in locals() else 'blue')

  if st.form_submit_button('SALVA POSTAZIONE CON ICONA'):
   if m1:
    nuovo={'Postazione':m1,'Comune':m2,'Via':m3,'Lat':m5,'Lon':m6,'Tipo':m7,'IconaFile':m9,'IconaCol':m10,'Resp':m8}
    st.session_state.post.append(nuovo)
    save_json(FP,st.session_state.post)
    st.success(f'Salvata {m1} con icona')
    st.rerun()

 st.divider()
 st.markdown('##### ANTEPRIMA MAPPA CON ICONE LIBRERIA')
 if st.session_state.post:
  if HAS_FOLIUM:
   m2=folium.Map(location=[45.8205,8.8250],zoom_start=12,tiles='OpenStreetMap')
   for p in st.session_state.post:
    try:
     la=float(p.get('Lat','0'))
     lo=float(p.get('Lon','0'))
     folium.Marker([la,lo],popup=p.get('Postazione','')).add_to(m2)
    except:
     pass
   st_folium(m2,height=380,width=700,key='m2')
  st.dataframe(pd.DataFrame(st.session_state.post))
 else:
  st.info('Nessuna postazione')

elif scelta=='Emergenze':
 torna()
 st.markdown('#### EMERGENZE - USA LIBRERIA ICONE')
 icon_names=[f"{ic.get('nome','')} ({ic.get('tipo','')})" for ic in st.session_state.icone]
 with st.form('em'):
  e1=st.text_input('Tipo emergenza *',value='Alluvione')
  e2=st.selectbox('Icona libreria', icon_names if icon_names else ['Nessuna'])
  e3=st.text_input('Comune',value='Varese')
  e4=st.text_input('Via *')
  e5=st.text_area('Descrizione *')
  if st.form_submit_button('SALVA EMERGENZA CON ICONA'):
   if e4:
    st.success(f'Emergenza {e1} con icona {e2} salvata')

elif scelta=='Backup':
 torna()
 st.markdown('#### BACKUP')
 if st.button('CREA BACKUP'):
  out=BytesIO()
  with pd.ExcelWriter(out,engine='openpyxl') as writer:
   if st.session_state.post:
    pd.DataFrame(st.session_state.post).to_excel(writer,sheet_name='Mappa',index=False)
   if st.session_state.icone:
    pd.DataFrame(st.session_state.icone).to_excel(writer,sheet_name='Icone',index=False)
  st.session_state['bk']=out.getvalue()
 if 'bk' in st.session_state:
  st.download_button('SCARICA',st.session_state['bk'],file_name='BACKUP.xlsx')
