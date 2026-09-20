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
 from PIL import Image, ImageDraw, ImageFont
 HAS_PIL=True
except:
 HAS_PIL=False

try:
 import qrcode
 HAS_QR=True
except:
 HAS_QR=False

st.set_page_config(page_title="ANA Varese", layout="wide")

st.markdown("""
<style>
.block-container{padding-top:20px!important;max-width:100%!important;}
.stForm{background:#e8f5e9!important;border:2px solid #0e7a3d!important;}
.stForm label{color:#000!important;font-weight:bold!important;font-family:Times New Roman!important;}
.stButton>button{background:#0e7a3d!important;color:white!important;font-weight:bold!important;}
.badge-card{border:3px solid #0e7a3d;border-radius:15px;padding:10px;background:white;text-align:center;}
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

def make_pdf_simple(title, df):
 try:
  lines=[]
  lines.append(title)
  lines.append(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')} - ANA Varese")
  lines.append("")
  lines.append(f"Totale record: {len(df) if df is not None else 0}")
  lines.append("")
  if df is not None and not df.empty:
   cols=list(df.columns)[:6]
   lines.append(" | ".join(cols))
   lines.append("-"*80)
   for _,row in df.head(60).iterrows():
    vals=[str(row.get(c,''))[:20].replace('(','').replace(')','') for c in cols]
    lines.append(" | ".join(vals))
  else:
   lines.append("Nessun dato")
  content="BT\n/F1 9 Tf\n50 800 Td\n"
  for i,line in enumerate(lines):
   safe=line.replace("\\","").replace("(","").replace(")","")[:120]
   if i==0:
    content+=f"({safe}) Tj\n"
   else:
    content+=f"0 -12 Td\n({safe}) Tj\n"
  content+="ET\n"
  content_bytes=content.encode('latin-1', errors='ignore')
  pdf=BytesIO()
  pdf.write(b"%PDF-1.4\n")
  offsets=[]
  offsets.append(pdf.tell())
  pdf.write(b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")
  offsets.append(pdf.tell())
  pdf.write(b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n")
  offsets.append(pdf.tell())
  pdf.write(b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>\nendobj\n")
  offsets.append(pdf.tell())
  pdf.write(b"4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n")
  offsets.append(pdf.tell())
  pdf.write(f"5 0 obj\n<< /Length {len(content_bytes)} >>\nstream\n".encode())
  pdf.write(content_bytes)
  pdf.write(b"\nendstream\nendobj\n")
  xref_pos=pdf.tell()
  pdf.write(f"xref\n0 {len(offsets)+1}\n0000000000 65535 f \n".encode())
  for off in offsets:
   pdf.write(f"{off:010d} 00000 n \n".encode())
  pdf.write(f"trailer\n<< /Size {len(offsets)+1} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF".encode())
  return pdf.getvalue()
 except Exception as e:
  st.error(f"Errore PDF: {e}")
  return None

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
 except ImportError:
  return make_pdf_simple(title, df)
 except Exception as e:
  try:
   return make_pdf_simple(title, df)
  except:
   st.error(f"Errore PDF: {e}")
   return None

def export_excel(df):
 out=BytesIO()
 with pd.ExcelWriter(out,engine='openpyxl') as writer:
  df.to_excel(writer,index=False)
 return out.getvalue()

def crea_badge(vol_data, foto_path=None):
 # Crea badge ANA Varese con foto volontario
 try:
  if not HAS_PIL:
   return None
  W,H=600,380
  badge=Image.new('RGB',(W,H),'white')
  draw=ImageDraw.Draw(badge)
  # Bordo verde ANA
  draw.rectangle([0,0,W-1,H-1], outline='#0e7a3d', width=8)
  # Header verde
  draw.rectangle([0,0,W,70], fill='#0e7a3d')
  # Testo header
  try:
   font_b=ImageFont.truetype("arial.ttf",28)
   font_m=ImageFont.truetype("arial.ttf",18)
   font_s=ImageFont.truetype("arial.ttf",14)
  except:
   font_b=ImageFont.load_default()
   font_m=ImageFont.load_default()
   font_s=ImageFont.load_default()
  draw.text((20,15), "ANA VARESE - VOLONTARIATO", fill='white', font=font_b)
  draw.text((20,45), "Protezione Civile", fill='white', font=font_m)
  # Logo ANA se esiste
  try:
   if os.path.exists("logo.png"):
    logo=Image.open("logo.png").convert("RGBA")
    logo=logo.resize((60,60))
    badge.paste(logo, (W-70,5), logo if logo.mode=='RGBA' else None)
  except:
   pass
  # Foto volontario
  foto_x,foto_y=20,90
  foto_w,foto_h=120,150
  if foto_path and os.path.exists(foto_path):
   try:
    foto=Image.open(foto_path).convert("RGB")
    foto=foto.resize((foto_w,foto_h))
    badge.paste(foto, (foto_x,foto_y))
    draw.rectangle([foto_x,foto_y,foto_x+foto_w,foto_y+foto_h], outline='#0e7a3d', width=3)
   except:
    draw.rectangle([foto_x,foto_y,foto_x+foto_w,foto_y+foto_h], fill='#e0e0e0', outline='#0e7a3d', width=2)
    draw.text((foto_x+10,foto_y+60), "NO FOTO", fill='black', font=font_m)
  else:
   draw.rectangle([foto_x,foto_y,foto_x+foto_w,foto_y+foto_h], fill='#e0e0e0', outline='#0e7a3d', width=2)
   draw.text((foto_x+10,foto_y+60), "NO FOTO", fill='black', font=font_m)
  # Dati volontario
  nome=vol_data.get('Nome','')
  ruolo=vol_data.get('Ruolo','Volontario')
  tessera=vol_data.get('Tessera','')
  gruppo=vol_data.get('Gruppo','')
  cell=vol_data.get('Cellulare','')
  data_iscr=vol_data.get('DataIscrizione','')
  x_text=160
  y_text=100
  draw.text((x_text,y_text), f"{nome}", fill='black', font=font_b)
  y_text+=35
  draw.text((x_text,y_text), f"Ruolo: {ruolo}", fill='#0e7a3d', font=font_m)
  y_text+=25
  if gruppo:
   draw.text((x_text,y_text), f"Gruppo: {gruppo}", fill='black', font=font_s)
   y_text+=20
  if tessera:
   draw.text((x_text,y_text), f"Tessera: {tessera}", fill='black', font=font_s)
   y_text+=20
  if data_iscr:
   draw.text((x_text,y_text), f"Iscritto: {data_iscr}", fill='black', font=font_s)
   y_text+=20
  if cell:
   draw.text((x_text,y_text), f"Cell: {cell}", fill='black', font=font_s)
  # QR Code se disponibile
  if HAS_QR:
   try:
    qr_data=f"ANA Varese - {nome} - {ruolo} - {tessera}"
    qr=qrcode.QRCode(version=1, box_size=3, border=1)
    qr.add_data(qr_data)
    qr.make(fit=True)
    qr_img=qr.make_image(fill_color="#0e7a3d", back_color="white").convert("RGB")
    qr_img=qr_img.resize((80,80))
    badge.paste(qr_img, (W-90, H-90))
   except:
    pass
  # Footer
  draw.rectangle([0,H-30,W,H], fill='#0e7a3d')
  draw.text((20,H-25), f"Badge valido - {datetime.now().strftime('%d/%m/%Y')} - ANA Varese", fill='white', font=font_s)
  # Salva in BytesIO
  buf=BytesIO()
  badge.save(buf, format='PNG')
  buf.seek(0)
  return buf.getvalue()
 except Exception as e:
  st.error(f"Errore creazione badge: {e}")
  return None

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
 ('popup_cfg',{'titolo':'ANA VARESE - VOLONTARIATO','sottotitolo':'Ciao Ragazzi, Buon Lavoro!','mostra':True})
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
st.session_state.popup_cfg=load(FPOP,{'titolo':'ANA VARESE - VOLONTARIATO','sottotitolo':'Ciao Ragazzi, Buon Lavoro!','mostra':True})
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

# POPUP PRIMA DEL LOGIN - SOLO TUA IMMAGINE FUMETTO, NO LOGO PC
if st.session_state.popup_cfg.get('mostra',True) and not st.session_state.popup_shown:
 st.markdown(f"<h1 style='text-align:center;color:#0e7a3d;font-family:Times New Roman;'>{st.session_state.popup_cfg.get('titolo','ANA VARESE')}</h1>", unsafe_allow_html=True)
 st.markdown(f"<h3 style='text-align:center;color:#0e7a3d;'>{st.session_state.popup_cfg.get('sottotitolo','Ciao Ragazzi, Buon Lavoro!')}</h3>", unsafe_allow_html=True)
 st.divider()
 c1,c2,c3=st.columns([1,2,1])
 with c2:
  # CERCA SOLO TUA IMMAGINE CON FUMETTO, NON LOGO ANA
  img_found=False
  for img_name in [
   'copertina.jpg',
   'copertina_fumetto.jpg',
   'mia_immagine_fumetto.jpg',
   'copertina.png',
   'benvenuto.jpg',
   'popup.jpg'
  ]:
   if os.path.exists(img_name):
    try:
     st.image(img_name,use_container_width=True)
     st.success(f"La tua immagine con fumetto: {img_name}")
     img_found=True
     break
    except:
     pass
  if not img_found:
   st.warning("Carica la tua immagine con fumetto 'ciao ragazzi, buon lavoro' come copertina.jpg!")
   st.info("NON verrà mostrato il logo PC, solo la tua immagine con fumetto")
   st.write("Scarica l'immagine che ti ho creato e caricala come copertina.jpg su GitHub")
  st.divider()
  st.markdown("<div style='background:#e8f5e9;padding:15px;border-radius:10px;border:2px solid #0e7a3d;text-align:center;'><b style='font-size:20px;'>ANA Varese - Protezione Civile</b><br><b style='color:#0e7a3d;font-size:18px;'>Ciao Ragazzi, Buon Lavoro!</b><br><br>Volontari: "+str(len(st.session_state.dati))+" - Postazioni: "+str(len(st.session_state.post))+"<br>Data: "+datetime.now().strftime('%d/%m/%Y %H:%M')+"</div>", unsafe_allow_html=True)
  st.divider()
  if st.button("ENTRA NEL SISTEMA", type="primary", use_container_width=True, key="entra_sistema"):
   st.session_state.popup_shown=True
   st.rerun()
 st.stop()

if not st.session_state.auth:
 header()
 c1,c2,c3=st.columns([1,2,1])
 with c2:
  # Mostra tua immagine con fumetto anche nel login, non logo
  for img_name in ['copertina.jpg','copertina_fumetto.jpg']:
   if os.path.exists(img_name):
    try:
     st.image(img_name,width=250)
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
  st.markdown('## MAPPA TUTTE')
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
    com=p.get('Comune','')
    st.success(f"Post: {nome}")
    st.info(f"Comune: {com}")
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
  opts=['Dashboard','Volontari','Mappa','Libreria Icone','Emergenza','Check In','DB Radio','Consegna Radio','Badge Volontari','Backup','Impostazioni Popup']
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
   if st.button('BADGE VOLONTARI',use_container_width=True):
    st.session_state.menu='Badge Volontari'
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
  st.markdown('<h3>VOLONTARI - CON FOTO + SOTTOMASCHERE</h3>', unsafe_allow_html=True)
  tab1,tab2,tab3,tab4,tab5=st.tabs(['Anagrafica + Foto','Contatti','Ruolo e Iscrizione','Documenti','Elenco con Foto'])
  with tab1:
   with st.form('form_vol_anag'):
    c1,c2=st.columns(2)
    with c1:
     a1=st.text_input('Nome *')
     a2=st.text_input('Cognome *')
     a_cf=st.text_input('Codice Fiscale')
     a_nasc=st.date_input('Data Nascita (gg/mm/aaaa)',value=date(1990,1,1),format="DD/MM/YYYY")
     a_luogo=st.text_input('Luogo Nascita')
     a_foto=st.file_uploader('Foto Volontario * (JPG/PNG)',type=['jpg','png','jpeg'],key='foto_vol')
    with c2:
     a_ind=st.text_input('Indirizzo Residenza')
     a_com=st.text_input('Comune Residenza')
     a_prov=st.text_input('Provincia')
     a_cap=st.text_input('CAP')
     if a_foto is not None:
      st.image(a_foto,width=150,caption='Anteprima foto')
    if st.form_submit_button('SALVA ANAGRAFICA + FOTO'):
     if a1 and a2:
      nc=a1+' '+a2
      foto_path=''
      if a_foto is not None:
       os.makedirs('foto_volontari',exist_ok=True)
       foto_path=f"foto_volontari/{nc.replace(' ','_')}_{a_foto.name}"
       with open(foto_path,'wb') as f:
        f.write(a_foto.getbuffer())
      nuovo={'Nome':nc,'NomeSolo':a1,'Cognome':a2,'CF':a_cf,'DataNascita':fmt_date(a_nasc),'LuogoNascita':a_luogo,'Indirizzo':a_ind,'ComuneRes':a_com,'Prov':a_prov,'CAP':a_cap,'FotoFile':foto_path}
      found=False
      for i,d in enumerate(st.session_state.dati):
       if d.get('Nome','')==nc:
        if not foto_path:
         nuovo['FotoFile']=d.get('FotoFile','')
        st.session_state.dati[i].update(nuovo)
        found=True
      if not found:
       st.session_state.dati.append(nuovo)
      save(FD,st.session_state.dati)
      st.success(f"Salvato {nc} con foto!")
      st.rerun()
  with tab2:
   with st.form('form_vol_cont'):
    vol_list=[]
    for d in st.session_state.dati:
     vol_list.append(d.get('Nome',''))
    if not vol_list:
     vol_list=['Nessun volontario']
    sel_vol=st.selectbox('Seleziona Volontario',vol_list,key='sel_vol_cont')
    for d in st.session_state.dati:
     if d.get('Nome','')==sel_vol:
      fp=d.get('FotoFile','')
      if fp and os.path.exists(fp):
       st.image(fp,width=100,caption=f"Foto {sel_vol}")
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
    for d in st.session_state.dati:
     if d.get('Nome','')==sel_vol2:
      fp=d.get('FotoFile','')
      if fp and os.path.exists(fp):
       st.image(fp,width=100)
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
    for d in st.session_state.dati:
     if d.get('Nome','')==sel_vol3:
      fp=d.get('FotoFile','')
      if fp and os.path.exists(fp):
       st.image(fp,width=100)
    d_pat=st.text_input('Patente - Categorie')
    d_scad_pat=st.date_input('Scadenza Patente (gg/mm/aaaa)',value=date.today(),format="DD/MM/YYYY")
    d_note=st.text_area('Note / Certificazioni')
    d_upload=st.file_uploader('Carica Documento',type=['pdf','png','jpg','jpeg'])
    d_foto_new=st.file_uploader('Cambia Foto Volontario',type=['jpg','png','jpeg'],key='foto_change')
    if st.form_submit_button('SALVA DOCUMENTI + FOTO'):
     fname=''
     if d_upload is not None:
      os.makedirs('documenti',exist_ok=True)
      fname=f"documenti/{sel_vol3}_{d_upload.name}"
      with open(fname,'wb') as f:
       f.write(d_upload.getbuffer())
     foto_new_path=''
     if d_foto_new is not None:
      os.makedirs('foto_volontari',exist_ok=True)
      foto_new_path=f"foto_volontari/{sel_vol3.replace(' ','_')}_{d_foto_new.name}"
      with open(foto_new_path,'wb') as f:
       f.write(d_foto_new.getbuffer())
     for i,d in enumerate(st.session_state.dati):
      if d.get('Nome','')==sel_vol3:
       upd={'Patente':d_pat,'ScadenzaPatente':fmt_date(d_scad_pat),'Note':d_note,'DocFile':fname}
       if foto_new_path:
        upd['FotoFile']=foto_new_path
       st.session_state.dati[i].update(upd)
       save(FD,st.session_state.dati)
       st.success(f"Documenti salvati per {sel_vol3}")
       st.rerun()
  with tab5:
   st.markdown('##### ELENCO VOLONTARI CON FOTO')
   if st.session_state.dati:
    for idx,d in enumerate(st.session_state.dati):
     c1,c2,c3=st.columns([1,3,1])
     with c1:
      fp=d.get('FotoFile','')
      if fp and os.path.exists(fp):
       try:
        st.image(fp,width=80)
       except:
        st.write('No foto')
      else:
       st.write('No foto')
     with c2:
      nome=d.get('Nome','')
      ruolo=d.get('Ruolo','')
      cell=d.get('Cellulare','')
      st.write(f"**{nome}** - {ruolo} - Cell: {cell}")
     with c3:
      if st.button('Elimina',key=f'del_vol_{idx}'):
       st.session_state.dati.pop(idx)
       save(FD,st.session_state.dati)
       st.rerun()
    st.divider()
    df=pd.DataFrame(st.session_state.dati)
    st.dataframe(df,use_container_width=True)
    c1,c2=st.columns(2)
    with c1:
     st.download_button('SCARICA EXCEL VOLONTARI',export_excel(df),file_name='Volontari.xlsx')
    with c2:
     if st.button('CREA PDF VOLONTARI',key='pdf_vol_btn'):
      pdf=make_pdf("Volontari ANA Varese con Foto",df)
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
    m2=st.text_input('Com
