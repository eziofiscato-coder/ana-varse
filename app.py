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

st.set_page_config(page_title="ANA Varese", layout="wide")

st.markdown("""
<style>
.block-container{padding-top:20px!important;max-width:100%!important;}
.stForm{background:#e8f5e9!important;border:2px solid #0e7a3d!important;}
.stForm label{color:#000!important;font-weight:bold!important;font-family:Times New Roman!important;}
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
 try:
  from reportlab.lib.pagesizes import A4
  from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
  from reportlab.lib.styles import getSampleStyleSheet
  from reportlab.lib import colors
  buf=BytesIO()
  doc=SimpleDocTemplate(buf,pagesize=A4,leftMargin=15,rightMargin=15,topMargin=20,bottomMargin=20)
  styles=getSampleStyleSheet()
  story=[]
  story.append(Paragraph(f"<b>{title}</b>",styles['Title']))
  story.append(Spacer(1,12))
  story.append(Paragraph(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')} - ANA Varese",styles['Normal']))
  story.append(Spacer(1,12))
  if df is not None and not df.empty:
   cols=list(df.columns)[:7]
   data=[cols]
   for _,row in df.head(50).iterrows():
    vals=[str(row.get(c,''))[:25] for c in cols]
    data.append(vals)
   t=Table(data,repeatRows=1)
   t.setStyle(TableStyle([
    ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#0e7a3d')),
    ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
    ('ALIGN',(0,0),(-1,-1),'LEFT'),
    ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
    ('FONTSIZE',(0,0),(-1,-1),7),
    ('GRID',(0,0),(-1,-1),0.5,colors.grey),
   ]))
   story.append(t)
  else:
   story.append(Paragraph("Nessun dato",styles['Normal']))
  doc.build(story)
  buf.seek(0)
  return buf.getvalue()
 except Exception as e:
  st.error(f"Errore PDF: {e}")
  return None

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
FPOP='popup.json'

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
 ('exp2',False),('exp3',False),
 ('popup_shown',False),
 ('popup_cfg',{'titolo':'ANA VARESE - VOLONTARIATO','sottotitolo':'Sezione di Varese - Protezione Civile','mostra':True})
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
st.session_state.popup_cfg=load(FPOP,{'titolo':'ANA VARESE - VOLONTARIATO','sottotitolo':'Sezione di Varese - Protezione Civile','mostra':True})
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

# POPUP PRIMA DEL LOGIN - TASTO FUNZIONANTE
if st.session_state.popup_cfg.get('mostra',True) and not st.session_state.popup_shown:
 st.markdown(f"<h1 style='text-align:center;color:#0e7a3d;font-family:Times New Roman;'>{st.session_state.popup_cfg.get('titolo','ANA VARESE')}</h1>", unsafe_allow_html=True)
 st.markdown(f"<h3 style='text-align:center;color:#000;'>{st.session_state.popup_cfg.get('sottotitolo','Sezione di Varese')}</h3>", unsafe_allow_html=True)
 st.divider()
 c1,c2,c3=st.columns([1,2,1])
 with c2:
  img_found=False
  for img_name in ['copertina.jpg','copertina.png','benvenuto.jpg','benvenuto.png','popup.jpg','logo.png']:
   if os.path.exists(img_name):
    try:
     st.image(img_name,use_container_width=True)
     img_found=True
     break
    except:
     pass
  if not img_found:
   st.info("Carica copertina.jpg su GitHub con immagine fumetto")
  st.divider()
  st.markdown("<div style='background:#e8f5e9;padding:15px;border-radius:10px;border:2px solid #0e7a3d;text-align:center;'><b style='font-size:20px;'>Sistema Gestione Volontari<br>ANA Varese - Protezione Civile</b><br><br>Volontari: "+str(len(st.session_state.dati))+" - Postazioni: "+str(len(st.session_state.post))+"<br>Data: "+datetime.now().strftime('%d/%m/%Y %H:%M')+"</div>", unsafe_allow_html=True)
  st.divider()
  if st.button("ENTRA NEL SISTEMA", type="primary", use_container_width=True, key="entra_sistema"):
   st.session_state.popup_shown=True
   st.rerun()
 st.stop()

if not st.session_state.auth:
 header()
 c1,c2,c3=st.columns([1,2,1])
 with c2:
  for img_name in ['copertina.jpg','copertina.png']:
   if os.path.exists(img_name):
    try:
     st.image(img_name,width=200)
     break
    except:
     pass
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
  if st.button('TORNA ALLA PAGINA INIZIALE POPUP'):
   st.session_state.popup_shown=False
   st.rerun()
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
  opts=['Dashboard','Volontari','Mappa','Libreria Icone','Emergenza','Check In','DB Radio','Consegna Radio','Backup','Impostazioni Popup']
  sel=st.radio('Vai a',opts,index=0)
  if sel!=st.session_state.menu:
   st.session_state.menu=sel
   st.rerun()
  st.divider()
  if st.button('MOSTRA POPUP INIZIALE',use_container_width=True):
   st.session_state.popup_shown=False
   st.rerun()
  if st.button('LOGOUT',use_container_width=True):
   st.session_state.auth=False
   st.session_state.popup_shown=False
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
   if st.button('POPUP INIZIALE',use_container_width=True):
    st.session_state.menu='Impostazioni Popup'
    st.rerun()
   st.metric('Vol',len(st.session_state.dati))
   st.metric('Post',len(st.session_state.post))

 elif scelta=='Volontari':
  torna()
  st.markdown('<h3>VOLONTARI - SOTTOMASCHERE + DATA GG/MM/AAAA</h3>', unsafe_allow_html=True)
  tab1,tab2,tab3,tab4=st.tabs(['Anagrafica','Contatti','Ruolo e Iscrizione','Documenti'])
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
      nuovo={'Nome':nc,'NomeSolo':a1,'Cognome':a2,'CF':a_cf,'DataNascita':fmt_date(a_nasc),'LuogoNascita':a_luogo,'Indirizzo':a_ind,'ComuneRes':a_com,'Prov':a_prov,'CAP':a_cap}
      found=False
      for i,d in enumerate(st.session_state.dati):
       if d.get('Nome','')==nc:
        st.session_state.dati[i].update(nuovo)
        found=True
      if not found:
       st.session_state.dati.append(nuovo)
      save(FD,st.session_state.dati)
      st.success(f"Salvato {nc}")
      st.rerun()
  with tab2:
   with st.form('form_vol_cont'):
    vol_list=[]
    for d in st.session_state.dati:
     vol_list.append(d.get('Nome',''))
    if not vol_list:
     vol_list=['Nessun volontario']
    sel_vol=st.selectbox('Seleziona Volontario',vol_list,key='sel_vol_cont')
    c1,c2=st.columns(2)
    with c1:
     b_cell=st.text_input('Cellulare *')
     b_tel=st.text_input('Telefono Fisso')
    with c2:
     b_email=st.text_input('Email')
     b_emerg=st.text_input('Contatto Emergenza')
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
    if st.form_submit_button('SALVA RUOLO'):
     for i,d in enumerate(st.session_state.dati):
      if d.get('Nome','')==sel_vol2:
       st.session_state.dati[i].update({'Ruolo':c_ruolo,'Gruppo':c_gruppo,'DataIscrizione':fmt_date(c_data_iscr),'Tessera':c_tessera,'DataScadenza':fmt_date(c_data_scad),'Disponibilita':c_disp})
       save(FD,st.session_state.dati)
       st.success(f"Ruolo salvato per {sel_vol2}")
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
    d_upload=st.file_uploader('Carica Documento',type=['pdf','png','jpg','jpeg'])
    if st.form_submit_button('SALVA DOCUMENTI'):
     fname=''
     if d_upload is not None:
      os.makedirs('documenti',exist_ok=True)
      fname=f"documenti/{sel_vol3}_{d_upload.name}"
      with open(fname,'wb') as f:
       f.write(d_upload.getbuffer())
     for i,d in enumerate(st.session_state.dati):
      if d.get('Nome','')==sel_vol3:
       st.session_state.dati[i].update({'Patente':d_pat,'ScadenzaPatente':fmt_date(d_scad_pat),'Note':d_note,'DocFile':fname})
       save(FD,st.session_state.dati)
       st.success(f"Documenti salvati per {sel_vol3}")
       st.rerun()
  st.divider()
  if st.session_state.dati:
   df=pd.DataFrame(st.session_state.dati)
   st.dataframe(df,use_container_width=True)
   c1,c2=st.columns(2)
   with c1:
    st.download_button('SCARICA EXCEL VOLONTARI',export_excel(df),file_name='Volontari.xlsx')
   with c2:
    if st.button('CREA PDF VOLONTARI',key='pdf_vol_btn'):
     pdf=make_pdf("Volontari ANA Varese",df)
     if pdf:
      st.session_state['pdf_vol']=pdf
      st.success('PDF creato!')
   if 'pdf_vol' in st.session_state:
    st.download_button('SCARICA PDF VOLONTARI',st.session_state['pdf_vol'],file_name='Volontari_ANA_Varese.pdf',mime='application/pdf',use_container_width=True)

 elif scelta=='Mappa':
  torna()
  st.markdown('<h3>MAPPA - COMUNE VIA ECC</h3>', unsafe_allow_html=True)
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
  st.markdown('##### 2 - MASCHERA')
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
    m8=st.selectbox('Responsabile *',vol_nomi)
    m9=st.selectbox('ODV operante *',st.session_state.odv)
    m9_new=st.text_input('Nuova ODV se non in lista')
   if st.form_submit_button('SALVA POSTAZIONE'):
    if m1:
     odv_f=m9_new if m9_new else m9
     if odv_f not in st.session_state.odv and odv_f:
      st.session_state.odv.append(odv_f)
      save(FO,st.session_state.odv)
     ic=st.session_state.icone[sel_idx] if st.session_state.icone else {'col':'blue','file':'','nome':''}
     nuovo={'Postazione':m1,'Comune':m2,'Via':m3,'Lat':m5,'Lon':m6,'Responsabile':m8,'ODV':odv_f,'Tipo':m4,'DataAttivazione':fmt_date(m_data),'Icona':ic.get('nome',''),'IconFile':ic.get('file',''),'Col':ic.get('col','blue')}
     st.session_state.post.append(nuovo)
     save(FP,st.session_state.post)
     st.session_state.clat=None
     st.session_state.clon=None
     st.success(f"Salvata {m1} a {m2}")
     st.rerun()
  st.divider()
  if st.session_state.post:
   df_post=pd.DataFrame(st.session_state.post)
   st.dataframe(df_post,use_container_width=True)
   c1,c2=st.columns(2)
   with c1:
    st.download_button('SCARICA EXCEL MAPPA',export_excel(df_post),file_name='Mappa.xlsx')
   with c2:
    if st.button('CREA PDF MAPPA',key='pdf_mappa_btn'):
     pdf=make_pdf("Mappa Postazioni ANA Varese",df_post)
     if pdf:
      st.session_state['pdf_mappa']=pdf
      st.success('PDF mappa creato!')
   if 'pdf_mappa' in st.session_state:
    st.download_button('SCARICA PDF MAPPA',st.session_state['pdf_mappa'],file_name='Mappa.pdf',mime='application/pdf')

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
     st.success(f"Salvata {e1}")
     st.rerun()
  if st.session_state.emerg:
   df_emerg=pd.DataFrame(st.session_state.emerg)
   st.dataframe(df_emerg,use_container_width=True)
   c1,c2=st.columns(2)
   with c1:
    st.download_button('SCARICA EXCEL EMERGENZE',export_excel(df_emerg),file_name='Emergenze.xlsx')
   with c2:
    if st.button('CREA PDF EMERGENZE',key='pdf_emerg_btn'):
     pdf=make_pdf("Emergenze ANA Varese",df_emerg)
     if pdf:
      st.session_state['pdf_emerg']=pdf
      st.success('PDF creato!')
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
    if st.button('CREA PDF CHECK IN',key='pdf_check_btn'):
     pdf=make_pdf("Check In ANA Varese",df_check)
     if pdf:
      st.session_state['pdf_check']=pdf
      st.success('PDF creato!')
   if 'pdf_check' in st.session_state:
    st.download_button('SCARICA PDF CHECK IN',st.session_state['pdf_check'],file_name='CheckIn.pdf',mime='application/pdf')

 elif scelta=='DB Radio':
  torna()
  st.markdown('#### DB RADIO - TIPO DMR ANALOGICA TETRA + DATA')
  with st.form('form_radio'):
   c1,c2=st.columns(2)
   with c1:
    r1=st.text_input('Nome radio *')
    r2=st.text_input('Frequenza *')
    r_tipo=st.selectbox('Tipo Radio *',['ANALOGICA','DMR','TETRA','PMR','Altro'])
    r3=st.text_input('Canale')
   with c2:
    r_data=st.date_input('Data Acquisto (gg/mm/aaaa)',value=date.today(),format="DD/MM/YYYY")
    r_mod=st.text_input('Modello Radio')
    r4=st.text_input('Note')
   if st.form_submit_button('SALVA RADIO'):
    if r1:
     nuovo={'Radio':r1,'Freq':r2,'TipoRadio':r_tipo,'Canale':r3,'Modello':r_mod,'DataAcquisto':fmt_date(r_data),'Note':r4}
     st.session_state.radio.append(nuovo)
     save(FR,st.session_state.radio)
     st.success(f"Salvata radio {r1} Tipo {r_tipo}")
     st.rerun()
  if st.session_state.radio:
   df_radio=pd.DataFrame(st.session_state.radio)
   st.dataframe(df_radio,use_container_width=True)
   c1,c2=st.columns(2)
   with c1:
    st.download_button('SCARICA EXCEL RADIO',export_excel(df_radio),file_name='DB_Radio.xlsx')
   with c2:
    if st.button('CREA PDF RADIO',key='pdf_radio_btn'):
     pdf=make_pdf("DB Radio ANA Varese",df_radio)
     if pdf:
      st.session_state['pdf_radio']=pdf
      st.success('PDF creato!')
   if 'pdf_radio' in st.session_state:
    st.download_button('SCARICA PDF RADIO',st.session_state['pdf_radio'],file_name='DB_Radio.pdf',mime='application/pdf')

 elif scelta=='Consegna Radio':
  torna()
  st.markdown('#### CONSEGNA RADIO - CON CAMPO CANALE')
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
    cr_canale=st.text_input('Canale *',placeholder='Es: CH 1 - Emergenza')
    cr_freq=st.text_input('Frequenza')
   with c2:
    cr3=st.date_input('Data Consegna (gg/mm/aaaa)',value=date.today(),format="DD/MM/YYYY")
    cr4=st.date_input('Data Riconsegna Prevista (gg/mm/aaaa)',value=date.today(),format="DD/MM/YYYY")
    cr5=st.selectbox('Stato',['Consegnata','Riconsegnata','In uso','Guasta'])
    cr6=st.text_area('Note')
   if st.form_submit_button('SALVA CONSEGNA RADIO'):
    nuovo={'Vol':cr1,'Radio':cr2,'Canale':cr_canale,'Frequenza':cr_freq,'DataConsegna':fmt_date(cr3),'DataRiconsegna':fmt_date(cr4),'Stato':cr5,'Note':cr6}
    st.session_state.cons.append(nuovo)
    save(FR2,st.session_state.cons)
    st.success(f"Radio {cr2} Canale {cr_canale} consegnata a {cr1}")
    st.rerun()
  if st.session_state.cons:
   df_cons=pd.DataFrame(st.session_state.cons)
   st.dataframe(df_cons,use_container_width=True)
   c1,c2=st.columns(2)
   with c1:
    st.download_button('SCARICA EXCEL CONSEGNE',export_excel(df_cons),file_name='ConsegnaRadio.xlsx')
   with c2:
    if st.button('CREA PDF CONSEGNE',key='pdf_cons_btn'):
     pdf=make_pdf("Consegna Radio ANA Varese",df_cons)
     if pdf:
      st.session_state['pdf_cons']=pdf
      st.success('PDF creato!')
   if 'pdf_cons' in st.session_state:
    st.download_button('SCARICA PDF CONSEGNE',st.session_state['pdf_cons'],file_name='ConsegnaRadio.pdf',mime='application/pdf')

 elif scelta=='Backup':
  torna()
  st.markdown('#### BACKUP - EXPORT SINGOLI + IMPORT TUTTI I FORM - FIXATO')

  tab_exp,tab_imp,tab_all=st.tabs(['EXPORT SINGOLI FORM','IMPORT TUTTI I FORM','BACKUP COMPLETO'])

  with tab_exp:
   st.markdown('##### EXPORT EXCEL PER SINGOLI FORM - TUTTI I FORM')
   c1,c2,c3=st.columns(3)
   with c1:
    st.markdown('**VOLONTARI**')
    if st.session_state.dati:
     df=pd.DataFrame(st.session_state.dati)
     st.write(f"Record: {len(df)}")
     st.download_button('EXPORT VOLONTARI EXCEL',export_excel(df),file_name='Volontari.xlsx',key='exp_vol',use_container_width=True)
     if st.button('CREA PDF VOLONTARI',key='pdf_vol_btn2',use_container_width=True):
      pdf=make_pdf("Volontari ANA Varese",df)
      if pdf:
       st.session_state['pdf_bk_vol']=pdf
       st.success('PDF creato!')
     if 'pdf_bk_vol' in st.session_state:
      st.download_button('SCARICA PDF VOLONTARI',st.session_state['pdf_bk_vol'],file_name='Volontari.pdf',mime='application/pdf',key='pdf_vol_dl',use_container_width=True)
    else:
     st.warning('Nessun volontario')

   with c2:
    st.markdown('**MAPPA POSTAZIONI**')
    if st.session_state.post:
     df=pd.DataFrame(st.session_state.post)
     st.write(f"Record: {len(df)}")
     st.download_button('EXPORT MAPPA EXCEL',export_excel(df),file_name='Mappa_Postazioni.xlsx',key='exp_mappa',use_container_width=True)
     if st.button('CREA PDF MAPPA',key='pdf_mappa_btn2',use_container_width=True):
      pdf=make_pdf("Mappa Postazioni ANA Varese",df)
      if pdf:
       st.session_state['pdf_bk_mappa']=pdf
       st.success('PDF creato!')
     if 'pdf_bk_mappa' in st.session_state:
      st.download_button('SCARICA PDF MAPPA',st.session_state['pdf_bk_mappa'],file_name='Mappa.pdf',mime='application/pdf',key='pdf_mappa_dl',use_container_width=True)
    else:
     st.warning('Nessuna postazione')

   with c3:
    st.markdown('**EMERGENZE**')
    if st.session_state.emerg:
     df=pd.DataFrame(st.session_state.emerg)
     st.write(f"Record: {len(df)}")
     st.download_button('EXPORT EMERGENZE EXCEL',export_excel(df),file_name='Emergenze.xlsx',key='exp_emerg',use_container_width=True)
     if st.button('CREA PDF EMERGENZE',key='pdf_emerg_btn2',use_container_width=True):
      pdf=make_pdf("Emergenze ANA Varese",df)
      if pdf:
       st.session_state['pdf_bk_emerg']=pdf
       st.success('PDF creato!')
     if 'pdf_bk_emerg' in st.session_state:
      st.download_button('SCARICA PDF EMERGENZE',st.session_state['pdf_bk_emerg'],file_name='Emergenze.pdf',mime='application/pdf',key='pdf_emerg_dl',use_container_width=True)
    else:
     st.warning('Nessuna emergenza')

   st.divider()
   c1,c2,c3=st.columns(3)
   with c1:
    st.markdown('**CHECK IN**')
    if st.session_state.check:
     df=pd.DataFrame(st.session_state.check)
     st.write(f"Record: {len(df)}")
     st.download_button('EXPORT CHECK IN EXCEL',export_excel(df),file_name='CheckIn.xlsx',key='exp_check',use_container_width=True)
     if st.button('CREA PDF CHECK IN',key='pdf_check_btn2',use_container_width=True):
      pdf=make_pdf("Check In ANA Varese",df)
      if pdf:
       st.session_state['pdf_bk_check']=pdf
       st.success('PDF creato!')
     if 'pdf_bk_check' in st.session_state:
      st.download_button('SCARICA PDF CHECK IN',st.session_state['pdf_bk_check'],file_name='CheckIn.pdf',mime='application/pdf',key='pdf_check_dl',use_container_width=True)
    else:
     st.warning('Nessun check in')

   with c2:
    st.markdown('**DB RADIO - DMR ANALOGICA TETRA**')
    if st.session_state.radio:
     df=pd.DataFrame(st.session_state.radio)
     st.write(f"Record: {len(df)}")
     st.download_button('EXPORT DB RADIO EXCEL',export_excel(df),file_name='DB_Radio.xlsx',key='exp_radio',use_container_width=True)
     if st.button('CREA PDF DB RADIO',key='pdf_radio_btn2',use_container_width=True):
      pdf=make_pdf("DB Radio ANA Varese - DMR ANALOGICA TETRA",df)
      if pdf:
       st.session_state['pdf_bk_radio']=pdf
       st.success('PDF creato!')
     if 'pdf_bk_radio' in st.session_state:
      st.download_button('SCARICA PDF DB RADIO',st.session_state['pdf_bk_radio'],file_name='DB_Radio.pdf',mime='application/pdf',key='pdf_radio_dl',use_container_width=True)
    else:
     st.warning('Nessuna radio')

   with c3:
    st.markdown('**CONSEGNA RADIO - CON CANALE**')
    if st.session_state.cons:
     df=pd.DataFrame(st.session_state.cons)
     st.write(f"Record: {len(df)}")
     st.download_button('EXPORT CONSEGNA RADIO EXCEL',export_excel(df),file_name='ConsegnaRadio.xlsx',key='exp_cons',use_container_width=True)
     if st.button('CREA PDF CONSEGNA RADIO',key='pdf_cons_btn2',use_container_width=True):
      pdf=make_pdf("Consegna Radio ANA Varese - Con Canale",df)
      if pdf:
       st.session_state['pdf_bk_cons']=pdf
       st.success('PDF creato!')
     if 'pdf_bk_cons' in st.session_state:
      st.download_button('SCARICA PDF CONSEGNA RADIO',st.session_state['pdf_bk_cons'],file_name='ConsegnaRadio.pdf',mime='application/pdf',key='pdf_cons_dl',use_container_width=True)
    else:
     st.warning('Nessuna consegna')

   st.divider()
   c1,c2,c3=st.columns(3)
   with c1:
    st.markdown('**LIBRERIA ICONE**')
    if st.session_state.icone:
     df=pd.DataFrame(st.session_state.icone)
     st.write(f"Record: {len(df)}")
     st.download_button('EXPORT ICONE EXCEL',export_excel(df),file_name='Libreria_Icone.xlsx',key='exp_icone',use_container_width=True)
     if st.button('CREA PDF ICONE',key='pdf_icone_btn',use_container_width=True):
      pdf=make_pdf("Libreria Icone ANA Varese",df)
      if pdf:
       st.session_state['pdf_bk_icone']=pdf
       st.success('PDF creato!')
     if 'pdf_bk_icone' in st.session_state:
      st.download_button('SCARICA PDF ICONE',st.session_state['pdf_bk_icone'],file_name='Icone.pdf',mime='application/pdf',key='pdf_icone_dl',use_container_width=True)
    else:
     st.warning('Nessuna icona')
   with c2:
    st.markdown('**TIPOLOGIE**')
    if st.session_state.tip:
     df=pd.DataFrame(st.session_state.tip,columns=['Tipologia'])
     st.write(f"Record: {len(df)}")
     st.download_button('EXPORT TIPOLOGIE EXCEL',export_excel(df),file_name='Tipologie.xlsx',key='exp_tip',use_container_width=True)
   with c3:
    st.markdown('**ODV**')
    if st.session_state.odv:
     df=pd.DataFrame(st.session_state.odv,columns=['ODV'])
     st.write(f"Record: {len(df)}")
     st.download_button('EXPORT ODV EXCEL',export_excel(df),file_name='ODV.xlsx',key='exp_odv',use_container_width=True)

  with tab_imp:
   st.markdown('##### IMPORT EXCEL PER TUTTI I FORM - FIXATO')

   c1,c2=st.columns(2)
   with c1:
    st.markdown('**IMPORT VOLONTARI**')
    up_vol=st.file_uploader('Carica Excel Volontari',type=['xlsx'],key='up_vol')
    if up_vol is not None:
     try:
      df_up=pd.read_excel(up_vol)
      st.write(f"Trovati {len(df_up)} record")
      if st.button('IMPORTA VOLONTARI',key='imp_vol_btn',use_container_width=True):
       for _,row in df_up.iterrows():
        st.session_state.dati.append(row.to_dict())
       save(FD,st.session_state.dati)
       st.success(f"Importati {len(df_up)} volontari")
       st.rerun()
     except Exception as e:
      st.error(f"Errore: {e}")

    st.markdown('**IMPORT MAPPA POSTAZIONI**')
    up_mappa=st.file_uploader('Carica Excel Mappa',type=['xlsx'],key='up_mappa')
    if up_mappa is not None:
     try:
      df_up=pd.read_excel(up_mappa)
      st.write(f"Trovati {len(df_up)} record")
      if st.button('IMPORTA MAPPA',key='imp_mappa_btn',use_container_width=True):
       for _,row in df_up.iterrows():
        st.session_state.post.append(row.to_dict())
       save(FP,st.session_state.post)
       st.success(f"Importate {len(df_up)} postazioni")
       st.rerun()
     except Exception as e:
      st.error(f"Errore: {e}")

    st.markdown('**IMPORT EMERGENZE**')
    up_emerg=st.file_uploader('Carica Excel Emergenze',type=['xlsx'],key='up_emerg')
    if up_emerg is not None:
     try:
      df_up=pd.read_excel(up_emerg)
      st.write(f"Trovati {len(df_up)} record")
      if st.button('IMPORTA EMERGENZE',key='imp_emerg_btn',use_container_width=True):
       for _,row in df_up.iterrows():
        st.session_state.emerg.append(row.to_dict())
       save(FE,st.session_state.emerg)
       st.success(f"Importate {len(df_up)} emergenze")
       st.rerun()
     except Exception as e:
      st.error(f"Errore: {e}")

    st.markdown('**IMPORT CHECK IN**')
    up_check=st.file_uploader('Carica Excel Check In',type=['xlsx'],key='up_check')
    if up_check is not None:
     try:
      df_up=pd.read_excel(up_check)
      st.write(f"Trovati {len(df_up)} record")
      if st.button('IMPORTA CHECK IN',key='imp_check_btn',use_container_width=True):
       for _,row in df_up.iterrows():
        st.session_state.check.append(row.to_dict())
       save(FC,st.session_state.check)
       st.success(f"Importati {len(df_up)} check in")
       st.rerun()
     except Exception as e:
      st.error(f"Errore: {e}")

   with c2:
    st.markdown('**IMPORT DB RADIO - DMR ANALOGICA TETRA**')
    up_radio=st.file_uploader('Carica Excel DB Radio',type=['xlsx'],key='up_radio')
    if up_radio is not None:
     try:
      df_up=pd.read_excel(up_radio)
      st.write(f"Trovati {len(df_up)} record")
      if st.button('IMPORTA DB RADIO',key='imp_radio_btn',use_container_width=True):
       for _,row in df_up.iterrows():
        st.session_state.radio.append(row.to_dict())
       save(FR,st.session_state.radio)
       st.success(f"Importate {len(df_up)} radio Tipo DMR ANALOGICA TETRA")
       st.rerun()
     except Exception as e:
      st.error(f"Errore: {e}")

    st.markdown('**IMPORT CONSEGNA RADIO - CON CANALE**')
    up_cons=st.file_uploader('Carica Excel Consegna Radio',type=['xlsx'],key='up_cons')
    if up_cons is not None:
     try:
      df_up=pd.read_excel(up_cons)
      st.write(f"Trovati {len(df_up)} record")
      if st.button('IMPORTA CONSEGNA RADIO',key='imp_cons_btn',use_container_width=True):
       for _,row in df_up.iterrows():
        st.session_state.cons.append(row.to_dict())
       save(FR2,st.session_state.cons)
       st.success(f"Importate {len(df_up)} consegne con Canale")
       st.rerun()
     except Exception as e:
      st.error(f"Errore: {e}")

    st.markdown('**IMPORT LIBRERIA ICONE**')
    up_icone=st.file_uploader('Carica Excel Icone',type=['xlsx'],key='up_icone')
    if up_icone is not None:
     try:
      df_up=pd.read_excel(up_icone)
      st.write(f"Trovati {len(df_up)} record")
      if st.button('IMPORTA ICONE',key='imp_icone_btn',use_container_width=True):
       for _,row in df_up.iterrows():
        st.session_state.icone.append(row.to_dict())
       save(FI,st.session_state.icone)
       st.success(f"Importate {len(df_up)} icone")
       st.rerun()
     except Exception as e:
      st.error(f"Errore: {e}")

    st.markdown('**IMPORT TIPOLOGIE / ODV**')
    up_tip=st.file_uploader('Carica Excel Tipologie',type=['xlsx'],key='up_tip')
    if up_tip is not None:
     try:
      df_up=pd.read_excel(up_tip)
      if st.button('IMPORTA TIPOLOGIE',key='imp_tip_btn',use_container_width=True):
       for _,row in df_up.iterrows():
        val=row.iloc[0]
        if val not in st.session_state.tip:
         st.session_state.tip.append(str(val))
       save(FT,st.session_state.tip)
       st.success(f"Importate tipologie")
       st.rerun()
     except Exception as e:
      st.error(f"Errore: {e}")

    up_odv=st.file_uploader('Carica Excel ODV',type=['xlsx'],key='up_odv')
    if up_odv is not None:
     try:
      df_up=pd.read_excel(up_odv)
      if st.button('IMPORTA ODV',key='imp_odv_btn',use_container_width=True):
       for _,row in df_up.iterrows():
        val=row.iloc[0]
        if val not in st.session_state.odv:
         st.session_state.odv.append(str(val))
       save(FO,st.session_state.odv)
       st.success(f"Importate ODV")
       st.rerun()
     except Exception as e:
      st.error(f"Errore: {e}")

  with tab_all:
   st.markdown('##### BACKUP COMPLETO TUTTI I FORM')
   st.info("Backup completo di tutti i form in un unico file Excel + PDF riepilogo")

   if st.button('CREA BACKUP COMPLETO EXCEL TUTTI I FORM',type='primary',use_container_width=True):
    out=BytesIO()
    with pd.ExcelWriter(out,engine='openpyxl') as writer:
     if st.session_state.dati:
      pd.DataFrame(st.session_state.dati).to_excel(writer,sheet_name='Volontari',index=False)
     if st.session_state.post:
      pd.DataFrame(st.session_state.post).to_excel(writer,sheet_name='Mappa',index=False)
     if st.session_state.icone:
      pd.DataFrame(st.session_state.icone).to_excel(writer,sheet_name='Icone',index=False)
     if st.session_state.tip:
      pd.DataFrame(st.session_state.tip,columns=['Tipologia']).to_excel(writer,sheet_name='Tipologie',index=False)
     if st.session_state.odv:
      pd.DataFrame(st.session_state.odv,columns=['ODV']).to_excel(writer,sheet_name='ODV',index=False)
     if st.session_state.emerg:
      pd.DataFrame(st.session_state.emerg).to_excel(writer,sheet_name='Emergenze',index=False)
     if st.session_state.check:
      pd.DataFrame(st.session_state.check).to_excel(writer,sheet_name='CheckIn',index=False)
     if st.session_state.radio:
      pd.DataFrame(st.session_state.radio).to_excel(writer,sheet_name='DBRadio_DMR_ANALOGICA_TETRA',index=False)
     if st.session_state.cons:
      pd.DataFrame(st.session_state.cons).to_excel(writer,sheet_name='ConsegnaRadio_ConCanale',index=False)
    st.session_state['bk_all']=out.getvalue()
    st.success('Backup completo creato con tutti i form!')

   if 'bk_all' in st.session_state:
    c1,c2=st.columns(2)
    with c1:
     st.download_button('SCARICA BACKUP COMPLETO EXCEL',st.session_state['bk_all'],file_name='BACKUP_COMPLETO_ANA_VARESE_TUTTI_FORM.xlsx',use_container_width=True,type='primary')
    with c2:
     if st.button('CREA PDF BACKUP COMPLETO',use_container_width=True):
      df_all=pd.DataFrame([
       {'Form':'Volontari (Sottomaschere)','Num':len(st.session_state.dati)},
       {'Form':'Mappa (Comune Via Lat Lon)','Num':len(st.session_state.post)},
       {'Form':'Libreria Icone PNG','Num':len(st.session_state.icone)},
       {'Form':'Tipologie','Num':len(st.session_state.tip)},
       {'Form':'ODV','Num':len(st.session_state.odv)},
       {'Form':'Emergenze (gg/mm/aaaa)','Num':len(st.session_state.emerg)},
       {'Form':'Check In (gg/mm/aaaa)','Num':len(st.session_state.check)},
       {'Form':'DB Radio DMR ANALOGICA TETRA','Num':len(st.session_state.radio)},
       {'Form':'Consegna Radio Con Canale','Num':len(st.session_state.cons)}
      ])
      pdf=make_pdf("BACKUP COMPLETO ANA VARESE - TUTTI I FORM",df_all)
      if pdf:
       st.session_state['pdf_bk_all']=pdf
       st.success('PDF backup completo creato!')
    if 'pdf_bk_all' in st.session_state:
     st.download_button('SCARICA PDF BACKUP COMPLETO',st.session_state['pdf_bk_all'],file_name='BACKUP_COMPLETO_ANA_VARESE.pdf',mime='application/pdf',use_container_width=True)

   st.divider()
   st.markdown('##### RIPRISTINO BACKUP COMPLETO')
   up_all=st.file_uploader('Carica Backup Completo Excel per ripristinare tutto',type=['xlsx'],key='up_all')
   if up_all is not None:
    try:
     xls=pd.ExcelFile(up_all)
     st.write(f"Fogli trovati: {xls.sheet_names}")
     if st.button('RIPRISTINA TUTTO DA BACKUP COMPLETO',type='primary',use_container_width=True):
      for sheet in xls.sheet_names:
       df_sheet=pd.read_excel(up_all,sheet_name=sheet)
       if 'Volontari' in sheet:
        st.session_state.dati=df_sheet.to_dict('records')
        save(FD,st.session_state.dati)
       elif 'Mappa' in sheet:
        st.session_state.post=df_sheet.to_dict('records')
        save(FP,st.session_state.post)
       elif 'Icone' in sheet:
        st.session_state.icone=df_sheet.to_dict('records')
        save(FI,st.session_state.icone)
       elif 'Emergenze' in sheet:
        st.session_state.emerg=df_sheet.to_dict('records')
        save(FE,st.session_state.emerg)
       elif 'CheckIn' in sheet:
        st.session_state.check=df_sheet.to_dict('records')
        save(FC,st.session_state.check)
       elif 'DBRadio' in sheet or 'Radio' in sheet:
        st.session_state.radio=df_sheet.to_dict('records')
        save(FR,st.session_state.radio)
       elif 'ConsegnaRadio' in sheet or 'Consegna' in sheet:
        st.session_state.cons=df_sheet.to_dict('records')
        save(FR2,st.session_state.cons)
      st.success('Ripristino completo completato!')
      st.rerun()
    except Exception as e:
     st.error(f"Errore ripristino: {e}")

 elif scelta=='Impostazioni Popup':
  torna()
  st.markdown('#### IMPOSTAZIONI PAGINA INIZIALE POPUP')
  st.info("Popup prima del login - con tua immagine copertina.jpg con fumetto ciao ragazzi buon lavoro")
  with st.form('form_popup'):
   p_titolo=st.text_input('Titolo Popup',value=st.session_state.popup_cfg.get('titolo','ANA VARESE - VOLONTARIATO'))
   p_sotto=st.text_input('Sottotitolo Popup',value=st.session_state.popup_cfg.get('sottotitolo','Sezione di Varese - Protezione Civile'))
   p_mostra=st.checkbox('Mostra popup all avvio',value=st.session_state.popup_cfg.get('mostra',True))
   if st.form_submit_button('SALVA IMPOSTAZIONI POPUP'):
    st.session_state.popup_cfg={'titolo':p_titolo,'sottotitolo':p_sotto,'mostra':p_mostra}
    save(FPOP,st.session_state.popup_cfg)
    st.success('Impostazioni salvate')
  st.divider()
  st.markdown('##### CARICA IMMAGINE POPUP')
  st.write("Carica immagine come copertina.jpg - quella con fumetto ciao ragazzi buon lavoro")
  up_popup=st.file_uploader('Carica immagine popup',type=['jpg','png','jpeg'],key='up_popup')
  if up_popup is not None:
   if st.button('SALVA IMMAGINE POPUP COME COPERTINA.JPG'):
    with open('copertina.jpg','wb') as f:
     f.write(up_popup.getbuffer())
    st.success('Immagine salvata come copertina.jpg!')
    st.image(up_popup,use_container_width=True)
  st.divider()
  for img_name in ['copertina.jpg','copertina.png','benvenuto.jpg','logo.png']:
   if os.path.exists(img_name):
    st.write(f"File trovato: {img_name}")
    try:
     st.image(img_name,width=300)
    except:
     pass
  if st.button('MOSTRA ANTEPRIMA POPUP',type='primary',use_container_width=True):
   st.session_state.popup_shown=False
   st.rerun()
