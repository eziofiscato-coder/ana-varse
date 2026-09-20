import streamlit as st
import pandas as pd
from io import BytesIO
import os, json, hashlib, requests
from datetime import datetime, date

try:
 import folium
 from streamlit_folium import st_folium
 HAS=True
except:
 HAS=False

try:
 from reportlab.lib.pagesizes import A4
 from reportlab.pdfgen import canvas
 from reportlab.lib.units import mm
 HAS_PDF=True
except:
 HAS_PDF=False

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
   full_via=(via+' '+num).strip()
   return com,full_via
 except:
  pass
 return '',''

def fmt_date(d):
 if isinstance(d,date):
  return d.strftime("%d/%m/%Y")
 return str(d)

def make_pdf(title, df):
 if not HAS_PDF:
  return None
 buf=BytesIO()
 c=canvas.Canvas(buf,pagesize=A4)
 w,h=A4
 c.setFont("Helvetica-Bold",16)
 c.drawString(20*mm,h-20*mm,title)
 c.setFont("Helvetica",9)
 y=h-30*mm
 if df is not None and not df.empty:
  cols=list(df.columns)[:6]
  header=" | ".join(cols)
  c.drawString(10*mm,y,header[:120])
  y-=8*mm
  for idx,row in df.head(40).iterrows():
   if y<20*mm:
    c.showPage()
    y=h-20*mm
    c.setFont("Helvetica",9)
   txt=" | ".join([str(row.get(col,''))[:20] for col in cols])
   c.drawString(10*mm,y,txt[:130])
   y-=6*mm
 c.showPage()
 c.save()
 buf.seek(0)
 return buf.getvalue()

def export_excel(df):
 out=BytesIO()
 with pd.ExcelWriter(out,engine='openpyxl') as writer:
  df.to_excel(writer,index=False)
 return out.getvalue()

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
  with st.form('form_login'):
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
  st.markdown('<h3>VOLONTARI - SOTTOMASCHERE + DATA GG/MM/AAAA</h3>', unsafe_allow_html=True)
  # SOTTOMASCHERE CON TABS
  tab1,tab2,tab3,tab4=st.tabs(['Anagrafica','Contatti','Ruolo e Iscrizione','Documenti e Note'])
  with tab1:
   with st.form('form_vol_anag'):
    c1,c2=st.columns(2)
    with c1:
     a1=st.text_input('Nome *')
     a2=st.text_input('Cognome *')
     a_cf=st.text_input('Codice Fiscale')
     a_nasc=st.date_input('Data Nascita (gg/mm/aaaa)',value=date(1990,1,1),format="DD/MM/YYYY")
     a_luogo=st.text_input('Luogo Nascita')
    with c2:
     a_ind=st.text_input('Indirizzo Residenza')
     a_com=st.text_input('Comune Residenza')
     a_prov=st.text_input('Provincia')
     a_cap=st.text_input('CAP')
    if st.form_submit_button('SALVA ANAGRAFICA'):
     if a1 and a2:
      nc=a1+' '+a2
      nuovo={
       'Nome':nc,'NomeSolo':a1,'Cognome':a2,
       'CF':a_cf,'DataNascita':fmt_date(a_nasc),
       'LuogoNascita':a_luogo,'Indirizzo':a_ind,
       'ComuneRes':a_com,'Prov':a_prov,'CAP':a_cap
      }
      # Se esiste gia, aggiorna, altrimenti aggiungi
      found=False
      for i,d in enumerate(st.session_state.dati):
       if d.get('Nome','')==nc:
        st.session_state.dati[i].update(nuovo)
        found=True
      if not found:
       st.session_state.dati.append(nuovo)
      save(FD,st.session_state.dati)
      st.success(f"Salvato anagrafica {nc} - Data Nascita {fmt_date(a_nasc)}")
      st.rerun()

  with tab2:
   with st.form('form_vol_cont'):
    vol_list=[]
    for d in st.session_state.dati:
     vol_list.append(d.get('Nome',''))
    if not vol_list:
     vol_list=['Nessun volontario - inserisci in Anagrafica']
    sel_vol=st.selectbox('Seleziona Volontario',vol_list,key='sel_vol_cont')
    c1,c2=st.columns(2)
    with c1:
     b_cell=st.text_input('Cellulare *')
     b_tel=st.text_input('Telefono Fisso')
    with c2:
     b_email=st.text_input('Email')
     b_emerg=st.text_input('Contatto Emergenza - Nome e Tel')
    if st.form_submit_button('SALVA CONTATTI'):
     for i,d in enumerate(st.session_state.dati):
      if d.get('Nome','')==sel_vol:
       st.session_state.dati[i].update({'Cellulare':b_cell,'Telefono':b_tel,'Email':b_email,'ContEmerg':b_emerg})
       save(FD,st.session_state.dati)
       st.success(f"Contatti salvati per {sel_vol}")
       st.rerun()

  with tab3:
   with st.form('form_vol_ruolo'):
    vol_list2=[]
    for d in st.session_state.dati:
     vol_list2.append(d.get('Nome',''))
    if not vol_list2:
     vol_list2=['Nessun volontario']
    sel_vol2=st.selectbox('Seleziona Volontario',vol_list2,key='sel_vol_ruolo')
    c1,c2=st.columns(2)
    with c1:
     c_ruolo=st.selectbox('Ruolo',['Volontario','Caposquadra','Coordinatore','Autista','Radio','Logistica','Segreteria','Sanitario','Altro'])
     c_gruppo=st.text_input('Gruppo / Squadra')
     c_data_iscr=st.date_input('Data Iscrizione (gg/mm/aaaa)',value=date.today(),format="DD/MM/YYYY")
    with c2:
     c_tessera=st.text_input('Numero Tessera')
     c_data_scad=st.date_input('Data Scadenza Tessera (gg/mm/aaaa)',value=date.today(),format="DD/MM/YYYY")
     c_disp=st.selectbox('Disponibilita',['Sempre','Weekend','Serale','Su chiamata'])
    if st.form_submit_button('SALVA RUOLO E ISCRIZIONE'):
     for i,d in enumerate(st.session_state.dati):
      if d.get('Nome','')==sel_vol2:
       st.session_state.dati[i].update({
        'Ruolo':c_ruolo,'Gruppo':c_gruppo,
        'DataIscrizione':fmt_date(c_data_iscr),
        'Tessera':c_tessera,
        'DataScadenza':fmt_date(c_data_scad),
        'Disponibilita':c_disp
       })
       save(FD,st.session_state.dati)
       st.success(f"Ruolo salvato per {sel_vol2} - Iscrizione {fmt_date(c_data_iscr)}")
       st.rerun()

  with tab4:
   with st.form('form_vol_doc'):
    vol_list3=[]
    for d in st.session_state.dati:
     vol_list3.append(d.get('Nome',''))
    if not vol_list3:
     vol_list3=['Nessun volontario']
    sel_vol3=st.selectbox('Seleziona Volontario',vol_list3,key='sel_vol_doc')
    d_pat=st.text_input('Patente - Categorie')
    d_scad_pat=st.date_input('Scadenza Patente (gg/mm/aaaa)',value=date.today(),format="DD/MM/YYYY")
    d_note=st.text_area('Note / Certificazioni')
    d_upload=st.file_uploader('Carica Documento (PDF/JPG)',type=['pdf','png','jpg','jpeg'])
    if st.form_submit_button('SALVA DOCUMENTI'):
     fname=''
     if d_upload is not None:
      os.makedirs('documenti',exist_ok=True)
      fname=f"documenti/{sel_vol3}_{d_upload.name}"
      with open(fname,'wb') as f:
       f.write(d_upload.getbuffer())
     for i,d in enumerate(st.session_state.dati):
      if d.get('Nome','')==sel_vol3:
       st.session_state.dati[i].update({
        'Patente':d_pat,
        'ScadenzaPatente':fmt_date(d_scad_pat),
        'Note':d_note,
        'DocFile':fname
       })
       save(FD,st.session_state.dati)
       st.success(f"Documenti salvati per {sel_vol3}")
       st.rerun()

  st.divider()
  if st.session_state.dati:
   df=pd.DataFrame(st.session_state.dati)
   st.dataframe(df,use_container_width=True)
   # PDF Volontari
   if st.button('CREA PDF VOLONTARI'):
    pdf_bytes=make_pdf("Volontari ANA Varese",df)
    if pdf_bytes:
     st.session_state['pdf_vol']=pdf_bytes
     st.success('PDF creato')
   if 'pdf_vol' in st.session_state:
    st.download_button('SCARICA PDF VOLONTARI',st.session_state['pdf_vol'],file_name='Volontari_ANA_Varese.pdf',mime='application/pdf')
   # Excel Volontari
   st.download_button('SCARICA EXCEL VOLONTARI',export_excel(df),file_name='Volontari.xlsx')

 elif scelta=='Mappa':
  torna()
  st.markdown('<h3>MAPPA - COMUNE VIA ECC COME PRIMA</h3>', unsafe_allow_html=True)

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
     st.image(fsel,width=60)
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
  st.markdown('##### 1 - MAPPA - COMUNE/VIA ESATTI')
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
      folium.Marker([st.session_state.clat,st.session_state.clon],icon=ic).add_to(m)
     else:
      folium.Marker([st.session_state.clat,st.session_state.clon],icon=folium.Icon(color='green')).add_to(m)
    except:
     folium.Marker([st.session_state.clat,st.session_state.clon],icon=folium.Icon(color='green')).add_to(m)
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

  c1,c2=st.columns(2)
  with c1:
   st.success(f"Comune: {st.session_state.com}")
   st.write(f"Via: {st.session_state.via}")
  with c2:
   st.write(f"Lat: {round(st.session_state.lat,6)}")
   st.write(f"Lon: {round(st.session_state.lon,6)}")

  st.divider()
  st.markdown('##### 2 - MASCHERA - COMUNE VIA + RESPONSABILE + DATA GG/MM/AAAA')

  vol_nomi=[]
  for d in st.session_state.dati:
   nome_completo=d.get('Nome','')
   if nome_completo:
    vol_nomi.append(nome_completo)
  if not vol_nomi:
   vol_nomi=['Nessun volontario']

  with st.form('form_mappa'):
   c1,c2=st.columns(2)
   with c1:
    m1=st.text_input('Nome postazione *')
    m2=st.text_input('Comune *',value=st.session_state.com)
    m3=st.text_input('Via *',value=st.session_state.via)
    m4=st.selectbox('Tipologia *',st.session_state.tip)
    m_data=st.date_input('Data Attivazione (gg/mm/aaaa)',value=date.today(),format="DD/MM/YYYY")
   with c2:
    m5=st.text_input('Latitudine *',value=str(st.session_state.lat))
    m6=st.text_input('Longitudine *',value=str(st.session_state.lon))
    m8=st.selectbox('Responsabile * (da Volontari)',vol_nomi)
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
      'DataAttivazione':fmt_date(m_data),
      'Icona':ic.get('nome',''),
      'IconFile':ic.get('file',''),
      'Col':ic.get('col','blue')
     }
     st.session_state.post.append(nuovo)
     save(FP,st.session_state.post)
     st.session_state.clat=None
     st.session_state.clon=None
     st.success(f"Salvata {m1} a {m2} il {fmt_date(m_data)}")
     st.rerun()

  st.divider()
  st.markdown('##### 3 - MAPPA TUTTE')
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
      folium.Marker([la,lo],popup=p.get('Postazione',''),icon=ic).add_to(m2)
     else:
      folium.Marker([la,lo],popup=p.get('Postazione',''),icon=folium.Icon(color='blue')).add_to(m2)
    except:
     pass
   st_folium(m2,height=400,width=700,key='m2')

  st.divider()
  st.markdown('##### 4 - ELENCO POSTAZIONI CON ICONA PNG E DATA')

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
     odv=p.get('ODV','')
     resp=p.get('Responsabile','')
     datt=p.get('DataAttivazione','')
     st.write(f"{nome} - {com} - ODV {odv} - Resp {resp} - Data {datt}")
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
   df_post=pd.DataFrame(st.session_state.post)
   st.dataframe(df_post,use_container_width=True)
   c1,c2=st.columns(2)
   with c1:
    st.download_button('SCARICA EXCEL MAPPA',export_excel(df_post),file_name='Mappa.xlsx')
   with c2:
    if st.button('CREA PDF MAPPA'):
     pdf=make_pdf("Mappa Postazioni ANA Varese",df_post)
     if pdf:
      st.session_state['pdf_mappa']=pdf
   if 'pdf_mappa' in st.session_state:
    st.download_button('SCARICA PDF MAPPA',st.session_state['pdf_mappa'],file_name='Mappa_ANA_Varese.pdf',mime='application/pdf')

   if st.session_state.prev>=0:
    try:
     p=st.session_state.post[st.session_state.prev]
     nome=p.get('Postazione','')
     com=p.get('Comune','')
     via=p.get('Via','')
     odv=p.get('ODV','')
     resp=p.get('Responsabile','')
     datt=p.get('DataAttivazione','')
     st.success(f"Postazione: {nome} - Data: {datt}")
     st.info(f"Comune: {com} - Via: {via} - ODV: {odv} - Resp: {resp}")
     fprev=p.get('IconFile','')
     if fprev and os.path.exists(fprev):
      st.image(fprev,width=80)

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
  with st.form('form_icone'):
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
   df_icone=pd.DataFrame(st.session_state.icone)
   st.dataframe(df_icone,use_container_width=True)
   c1,c2=st.columns(2)
   with c1:
    st.download_button('SCARICA EXCEL ICONE',export_excel(df_icone),file_name='Icone.xlsx')
   with c2:
    if st.button('CREA PDF ICONE'):
     pdf=make_pdf("Libreria Icone ANA",df_icone)
     if pdf:
      st.session_state['pdf_icone']=pdf
   if 'pdf_icone' in st.session_state:
    st.download_button('SCARICA PDF ICONE',st.session_state['pdf_icone'],file_name='Icone.pdf',mime='application/pdf')
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
  st.markdown('#### EMERGENZA - DATA GG/MM/AAAA')
  with st.form('form_emerg'):
   c1,c2=st.columns(2)
   with c1:
    e1=st.text_input('Nome emergenza *')
    e2=st.text_input('Luogo *')
    e3=st.selectbox('Tipo',['Alluvione','Terremoto','Incendio','Neve','Altro'])
   with c2:
    e_data=st.date_input('Data Emergenza (gg/mm/aaaa)',value=date.today(),format="DD/MM/YYYY")
    e_data_fine=st.date_input('Data Fine Prevista (gg/mm/aaaa)',value=date.today(),format="DD/MM/YYYY")
    e_desc=st.text_area('Descrizione')
   if st.form_submit_button('SALVA EMERGENZA'):
    if e1:
     nuovo={'Emergenza':e1,'Luogo':e2,'Tipo':e3,'DataEmergenza':fmt_date(e_data),'DataFine':fmt_date(e_data_fine),'Desc':e_desc}
     st.session_state.emerg.append(nuovo)
     save(FE,st.session_state.emerg)
     st.success(f"Salvata emergenza {e1} del {fmt_date(e_data)}")
     st.rerun()
  if st.session_state.emerg:
   df_emerg=pd.DataFrame(st.session_state.emerg)
   st.dataframe(df_emerg,use_container_width=True)
   c1,c2=st.columns(2)
   with c1:
    st.download_button('SCARICA EXCEL EMERGENZE',export_excel(df_emerg),file_name='Emergenze.xlsx')
   with c2:
    if st.button('CREA PDF EMERGENZE'):
     pdf=make_pdf("Emergenze ANA Varese",df_emerg)
     if pdf:
      st.session_state['pdf_emerg']=pdf
   if 'pdf_emerg' in st.session_state:
    st.download_button('SCARICA PDF EMERGENZE',st.session_state['pdf_emerg'],file_name='Emergenze.pdf',mime='application/pdf')

 elif scelta=='Check In':
  torna()
  st.markdown('#### CHECK IN - DATA GG/MM/AAAA')
  vol_list=[]
  for d in st.session_state.dati:
   vol_list.append(d.get('Nome',''))
  if not vol_list:
   vol_list=['Nessuno']
  with st.form('form_checkin'):
   c1,c2=st.columns(2)
   with c1:
    ch_data=st.date_input('Data Check In (gg/mm/aaaa)',value=date.today(),format="DD/MM/YYYY")
    ch_ora=st.time_input('Ora Check In')
   with c2:
    c2_sel=st.selectbox('Volontario',vol_list)
    c3=st.selectbox('Stato',['Presente','Assente','In servizio','Fuori servizio'])
    c4=st.text_input('Luogo Servizio')
   if st.form_submit_button('REGISTRA CHECK IN'):
    nuovo={'Data':fmt_date(ch_data),'Ora':str(ch_ora),'Vol':c2_sel,'Stato':c3,'Luogo':c4}
    st.session_state.check.append(nuovo)
    save(FC,st.session_state.check)
    st.success(f"Check In {fmt_date(ch_data)} per {c2_sel}")
    st.rerun()
  if st.session_state.check:
   df_check=pd.DataFrame(st.session_state.check)
   st.dataframe(df_check,use_container_width=True)
   c1,c2=st.columns(2)
   with c1:
    st.download_button('SCARICA EXCEL CHECK IN',export_excel(df_check),file_name='CheckIn.xlsx')
   with c2:
    if st.button('CREA PDF CHECK IN'):
     pdf=make_pdf("Check In ANA Varese",df_check)
     if pdf:
      st.session_state['pdf_check']=pdf
   if 'pdf_check' in st.session_state:
    st.download_button('SCARICA PDF CHECK IN',st.session_state['pdf_check'],file_name='CheckIn.pdf',mime='application/pdf')

 elif scelta=='DB Radio':
  torna()
  st.markdown('#### DB RADIO - DATA GG/MM/AAAA')
  with st.form('form_radio'):
   c1,c2=st.columns(2)
   with c1:
    r1=st.text_input('Nome radio *')
    r2=st.text_input('Frequenza *')
    r3=st.text_input('Canale')
   with c2:
    r_data=st.date_input('Data Acquisto (gg/mm/aaaa)',value=date.today(),format="DD/MM/YYYY")
    r4=st.text_input('Note')
   if st.form_submit_button('SALVA RADIO'):
    if r1:
     nuovo={'Radio':r1,'Freq':r2,'Canale':r3,'DataAcquisto':fmt_date(r_data),'Note':r4}
     st.session_state.radio.append(nuovo)
     save(FR,st.session_state.radio)
     st.success(f"Salvata radio {r1} del {fmt_date(r_data)}")
     st.rerun()
  if st.session_state.radio:
   df_radio=pd.DataFrame(st.session_state.radio)
   st.dataframe(df_radio,use_container_width=True)
   c1,c2=st.columns(2)
   with c1:
    st.download_button('SCARICA EXCEL RADIO',export_excel(df_radio),file_name='DB_Radio.xlsx')
   with c2:
    if st.button('CREA PDF RADIO'):
     pdf=make_pdf("DB Radio ANA Varese",df_radio)
     if pdf:
      st.session_state['pdf_radio']=pdf
   if 'pdf_radio' in st.session_state:
    st.download_button('SCARICA PDF RADIO',st.session_state['pdf_radio'],file_name='DB_Radio.pdf',mime='application/pdf')

 elif scelta=='Consegna Radio':
  torna()
  st.markdown('#### CONSEGNA RADIO - DATA GG/MM/AAAA')
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
  with st.form('form_consegna'):
   c1,c2=st.columns(2)
   with c1:
    cr1=st.selectbox('Volontario',vol_list)
    cr2=st.selectbox('Radio',radio_list)
    cr3=st.date_input('Data Consegna (gg/mm/aaaa)',value=date.today(),format="DD/MM/YYYY")
   with c2:
    cr4=st.date_input('Data Riconsegna Prevista (gg/mm/aaaa)',value=date.today(),format="DD/MM/YYYY")
    cr5=st.selectbox('Stato',['Consegnata','Riconsegnata','In uso','Guasta'])
    cr6=st.text_area('Note')
   if st.form_submit_button('SALVA CONSEGNA RADIO'):
    nuovo={'Vol':cr1,'Radio':cr2,'DataConsegna':fmt_date(cr3),'DataRiconsegna':fmt_date(cr4),'Stato':cr5,'Note':cr6}
    st.session_state.cons.append(nuovo)
    save(FR2,st.session_state.cons)
    st.success(f"Radio {cr2} consegnata a {cr1} il {fmt_date(cr3)}")
    st.rerun()
  if st.session_state.cons:
   df_cons=pd.DataFrame(st.session_state.cons)
   st.dataframe(df_cons,use_container_width=True)
   c1,c2=st.columns(2)
   with c1:
    st.download_button('SCARICA EXCEL CONSEGNE',export_excel(df_cons),file_name='ConsegnaRadio.xlsx')
   with c2:
    if st.button('CREA PDF CONSEGNE'):
     pdf=make_pdf("Consegna Radio ANA Varese",df_cons)
     if pdf:
      st.session_state['pdf_cons']=pdf
   if 'pdf_cons' in st.session_state:
    st.download_button('SCARICA PDF CONSEGNE',st.session_state['pdf_cons'],file_name='ConsegnaRadio.pdf',mime='application/pdf')

 elif scelta=='Backup':
  torna()
  st.markdown('#### BACKUP - IMPORT/EXPORT SINGOLI EXCEL + PDF TUTTI I FORM')

  st.divider()
  st.markdown('##### IMPORT EXCEL SINGOLI FORM')

  c1,c2=st.columns(2)
  with c1:
   st.markdown('**Import Volontari Excel**')
   up_vol=st.file_uploader('Carica Excel Volontari',type=['xlsx'],key='up_vol')
   if up_vol is not None:
    try:
     df_up=pd.read_excel(up_vol)
     if st.button('IMPORTA VOLONTARI DA EXCEL'):
      for _,row in df_up.iterrows():
       st.session_state.dati.append(row.to_dict())
      save(FD,st.session_state.dati)
      st.success(f"Importati {len(df_up)} volontari")
      st.rerun()
    except Exception as e:
     st.error(f"Errore import: {e}")

   st.markdown('**Import Mappa Excel**')
   up_mappa=st.file_uploader('Carica Excel Mappa',type=['xlsx'],key='up_mappa')
   if up_mappa is not None:
    try:
     df_up=pd.read_excel(up_mappa)
     if st.button('IMPORTA MAPPA DA EXCEL'):
      for _,row in df_up.iterrows():
       st.session_state.post.append(row.to_dict())
      save(FP,st.session_state.post)
      st.success(f"Importate {len(df_up)} postazioni")
      st.rerun()
    except Exception as e:
     st.error(f"Errore import: {e}")

  with c2:
   st.markdown('**Import Emergenze Excel**')
   up_emerg=st.file_uploader('Carica Excel Emergenze',type=['xlsx'],key='up_emerg')
   if up_emerg is not None:
    try:
     df_up=pd.read_excel(up_emerg)
     if st.button('IMPORTA EMERGENZE DA EXCEL'):
      for _,row in df_up.iterrows():
       st.session_state.emerg.append(row.to_dict())
      save(FE,st.session_state.emerg)
      st.success(f"Importate {len(df_up)} emergenze")
      st.rerun()
    except Exception as e:
     st.error(f"Errore: {e}")

   st.markdown('**Import Check In Excel**')
   up_check=st.file_uploader('Carica Excel Check In',type=['xlsx'],key='up_check')
   if up_check is not None:
    try:
     df_up=pd.read_excel(up_check)
     if st.button('IMPORTA CHECK IN DA EXCEL'):
      for _,row in df_up.iterrows():
       st.session_state.check.append(row.to_dict())
      save(FC,st.session_state.check)
      st.success(f"Importati {len(df_up)} check in")
      st.rerun()
    except Exception as e:
     st.error(f"Errore: {e}")

  st.divider()
  st.markdown('##### EXPORT EXCEL SINGOLI FORM')

  c1,c2,c3=st.columns(3)
  with c1:
   if st.session_state.dati:
    df=pd.DataFrame(st.session_state.dati)
    st.download_button('EXPORT VOLONTARI EXCEL',export_excel(df),file_name='Volontari.xlsx',key='exp_vol')
    if st.button('PDF VOLONTARI',key='pdf_vol_btn'):
     pdf=make_pdf("Volontari",df)
     if pdf:
      st.session_state['pdf_bk_vol']=pdf
    if 'pdf_bk_vol' in st.session_state:
     st.download_button('PDF VOLONTARI',st.session_state['pdf_bk_vol'],file_name='Volontari.pdf',mime='application/pdf',key='pdf_vol_dl')

  with c2:
   if st.session_state.post:
    df=pd.DataFrame(st.session_state.post)
    st.download_button('EXPORT MAPPA EXCEL',export_excel(df),file_name='Mappa.xlsx',key='exp_mappa')
    if st.button('PDF MAPPA',key='pdf_mappa_btn'):
     pdf=make_pdf("Mappa Postazioni",df)
     if pdf:
      st.session_state['pdf_bk_mappa']=pdf
    if 'pdf_bk_mappa' in st.session_state:
     st.download_button('PDF MAPPA',st.session_state['pdf_bk_mappa'],file_name='Mappa.pdf',mime='application/pdf',key='pdf_mappa_dl')

  with c3:
   if st.session_state.emerg:
    df=pd.DataFrame(st.session_state.emerg)
    st.download_button('EXPORT EMERGENZE EXCEL',export_excel(df),file_name='Emergenze.xlsx',key='exp_emerg')
    if st.button('PDF EMERGENZE',key='pdf_emerg_btn'):
     pdf=make_pdf("Emergenze",df)
     if pdf:
      st.session_state['pdf_bk_emerg']=pdf
    if 'pdf_bk_emerg' in st.session_state:
     st.download_button('PDF EMERGENZE',st.session_state['pdf_bk_emerg'],file_name='Emergenze.pdf',mime='application/pdf',key='pdf_emerg_dl')

  c1,c2,c3=st.columns(3)
  with c1:
   if st.session_state.check:
    df=pd.DataFrame(st.session_state.check)
    st.download_button('EXPORT CHECK IN EXCEL',export_excel(df),file_name='CheckIn.xlsx',key='exp_check')
    if st.button('PDF CHECK IN',key='pdf_check_btn'):
     pdf=make_pdf("Check In",df)
     if pdf:
      st.session_state['pdf_bk_check']=pdf
    if 'pdf_bk_check' in st.session_state:
     st.download_button('PDF CHECK IN',st.session_state['pdf_bk_check'],file_name='CheckIn.pdf',mime='application/pdf',key='pdf_check_dl')
  with c2:
   if st.session_state.radio:
    df=pd.DataFrame(st.session_state.radio)
    st.download_button('EXPORT DB RADIO EXCEL',export_excel(df),file_name='DB_Radio.xlsx',key='exp_radio')
    if st.button('PDF DB RADIO',key='pdf_radio_btn'):
     pdf=make_pdf("DB Radio",df)
     if pdf:
      st.session_state['pdf_bk_radio']=pdf
    if 'pdf_bk_radio' in st.session_state:
     st.download_button('PDF DB RADIO',st.session_state['pdf_bk_radio'],file_name='DB_Radio.pdf',mime='application/pdf',key='pdf_radio_dl')
  with c3:
   if st.session_state.cons:
    df=pd.DataFrame(st.session_state.cons)
    st.download_button('EXPORT CONSEGNA RADIO EXCEL',export_excel(df),file_name='ConsegnaRadio.xlsx',key='exp_cons')
    if st.button('PDF CONSEGNA RADIO',key='pdf_cons_btn'):
     pdf=make_pdf("Consegna Radio",df)
     if pdf:
      st.session_state['pdf_bk_cons']=pdf
    if 'pdf_bk_cons' in st.session_state:
     st.download_button('PDF CONSEGNA RADIO',st.session_state['pdf_bk_cons'],file_name='ConsegnaRadio.pdf',mime='application/pdf',key='pdf_cons_dl')

  st.divider()
  st.markdown('##### BACKUP COMPLETO TUTTI I FORM')

  if st.button('CREA BACKUP COMPLETO EXCEL + PDF'):
   out=BytesIO()
   with pd.ExcelWriter(out,engine='openpyxl') as writer:
    if st.session_state.dati:
     pd.DataFrame(st.session_state.dati).to_excel(writer,sheet_name='Volontari',index=False)
    if st.session_state.post:
     pd.DataFrame(st.session_state.post).to_excel(writer,sheet_name='Mappa',index=False)
    if st.session_state.icone:
     pd.DataFrame(st.session_state.icone).to_excel(writer,sheet_name='Icone',index=False)
    if st.session_state.emerg:
     pd.DataFrame(st.session_state.emerg).to_excel(writer,sheet_name='Emergenze',index=False)
    if st.session_state.check:
     pd.DataFrame(st.session_state.check).to_excel(writer,sheet_name='CheckIn',index=False)
    if st.session_state.radio:
     pd.DataFrame(st.session_state.radio).to_excel(writer,sheet_name='DBRadio',index=False)
    if st.session_state.cons:
     pd.DataFrame(st.session_state.cons).to_excel(writer,sheet_name='ConsegnaRadio',index=False)
   st.session_state['bk_all']=out.getvalue()
   st.success('Backup completo creato con tutti i form')

  if 'bk_all' in st.session_state:
   c1,c2=st.columns(2)
   with c1:
    st.download_button('SCARICA BACKUP COMPLETO EXCEL',st.session_state['bk_all'],file_name='BACKUP_COMPLETO_ANA_VARESE.xlsx',use_container_width=True)
   with c2:
    if st.button('CREA PDF BACKUP COMPLETO',use_container_width=True):
     # PDF con riepilogo
     if HAS_PDF:
      buf=BytesIO()
      c=canvas.Canvas(buf,pagesize=A4)
      w,h=A4
      c.setFont("Helvetica-Bold",18)
      c.drawString(20*mm,h-20*mm,"BACKUP COMPLETO ANA VARESE")
      c.setFont("Helvetica",12)
      y=h-35*mm
      c.drawString(20*mm,y,f"Data Backup: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
      y-=10*mm
      c.drawString(20*mm,y,f"Volontari: {len(st.session_state.dati)}")
      y-=10*mm
      c.drawString(20*mm,y,f"Postazioni Mappa: {len(st.session_state.post)}")
      y-=10*mm
      c.drawString(20*mm,y,f"Emergenze: {len(st.session_state.emerg)}")
      y-=10*mm
      c.drawString(20*mm,y,f"Check In: {len(st.session_state.check)}")
      y-=10*mm
      c.drawString(20*mm,y,f"DB Radio: {len(st.session_state.radio)}")
      y-=10*mm
      c.drawString(20*mm,y,f"Consegna Radio: {len(st.session_state.cons)}")
      c.showPage()
      c.save()
      buf.seek(0)
      st.session_state['pdf_bk_all']=buf.getvalue()
      st.success('PDF backup creato')
   if 'pdf_bk_all' in st.session_state:
    st.download_button('SCARICA PDF BACKUP COMPLETO',st.session_state['pdf_bk_all'],file_name='BACKUP_COMPLETO_ANA_VARESE.pdf',mime='application/pdf',use_container_width=True)
