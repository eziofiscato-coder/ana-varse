import streamlit as st
import pandas as pd
from datetime import datetime, date
from io import BytesIO
import base64, os

try:
 from reportlab.lib.pagesizes import landscape, A4
 from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
 from reportlab.lib import colors
 from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
 from reportlab.lib.units import cm
 HAS=True
except:
 HAS=False

st.set_page_config(page_title="ANA Varese", page_icon="🟢", layout="wide")

for k,v in [("authenticated",False),("dashboard_entered",False),("interventi_lista",[]),("eventi",[])]:
 if k not in st.session_state:
  st.session_state[k]=v

ICONE={"🔥 Incendio":"🔥","🌊 Alluvione":"🌊","❄️ Neve":"❄️","⛰️ Frana":"⛰️","🔍 Ricerca":"🔍","👥 Supporto":"👥","👁️ Monitoraggio":"👁️","🚧 Presidio":"🚧","🚨 Altro":"🚨"}

def get_b64(p):
 try:
  if os.path.exists(p):
   import base64
   with open(p,"rb") as f:
    return base64.b64encode(f.read()).decode()
 except:
  pass
 return ""

b64_ana=get_b64("/mnt/data/Green_Alpini_Emblem")
b64_vol=get_b64("/mnt/data/Circular_Volontariato_Emblem")
b64_pc=get_b64("/mnt/data/Protezione_Civile_Lombardia_Emblem")

if b64_ana and b64_vol and b64_pc:
 LOGHI=f"""
 <div style='display:flex; justify-content:center; gap:20px; background:#a5d6a7; padding:15px; border-radius:15px; border:3px solid #2e7d32; margin-bottom:15px; flex-wrap:wrap;'>
  <img src='data:image/jpeg;base64,{b64_vol}' style='width:100px; height:100px; border-radius:50%; border:3px solid #2e7d32; background:white;'>
  <img src='data:image/jpeg;base64,{b64_ana}' style='width:120px; height:120px; border-radius:50%; border:4px solid #1b5e20; background:white;'>
  <img src='data:image/jpeg;base64,{b64_pc}' style='width:100px; height:100px; border-radius:50%; border:3px solid #2e7d32; background:white;'>
 </div>
 """
else:
 LOGHI="<div style='background:#a5d6a7; padding:15px; border-radius:12px; border:3px solid #2e7d32; text-align:center;'><h3 style='color:#1b5e20; margin:0;'>🟢 ANA Varese - Protezione Civile</h3></div>"

st.markdown("""
<style>
.stApp{background:#e8f5e9!important;}
.main .block-container{max-width:100%!important; padding:1% 2%!important;}
[data-testid="stSidebar"]{background:#a5d6a7!important; border-right:3px solid #2e7d32!important;}
.stForm{background:#a5d6a7!important; border:3px solid #2e7d32!important; border-radius:15px!important; padding:20px!important;}
[data-testid="stDataFrame"]{background:white!important; border:3px solid #2e7d32!important;}
.stButton>button{background:#d32f2f!important; color:white!important; border:3px solid #b71c1c!important; font-weight:bold!important; border-radius:10px!important;}
div[data-testid="stFormSubmitButton"]>button{background:#d32f2f!important; color:white!important;}
.stDownloadButton>button{background:#d32f2f!important; color:white!important;}
</style>
""", unsafe_allow_html=True)

def pdf_a4(titolo, df):
 if not HAS or df is None or df.empty:
  return None
 buf=BytesIO()
 from reportlab.lib.pagesizes import landscape, A4
 from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
 from reportlab.lib import colors
 from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
 from reportlab.lib.units import cm
 doc=SimpleDocTemplate(buf, pagesize=landscape(A4), leftMargin=1*cm, rightMargin=1*cm, topMargin=1*cm, bottomMargin=1*cm)
 styles=getSampleStyleSheet()
 title_style=ParagraphStyle('t', parent=styles['Heading1'], fontSize=14, textColor=colors.HexColor('#1b5e20'), alignment=1)
 story=[Paragraph(f"<b>ANA Varese - {titolo}</b>", title_style), Paragraph(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')} - A4 Orizzontale", styles['Normal']), Spacer(1,0.5*cm)]
 d=df.copy()
 for c in d.columns:
  d[c]=d[c].astype(str).apply(lambda x: x[:50])
 data=[d.columns.tolist()]+d.values.tolist()
 w=(27.7*cm)/len(d.columns) if len(d.columns)>0 else 10*cm
 table=Table(data, colWidths=[w]*len(d.columns), repeatRows=1)
 table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#2e7d32')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('FONTSIZE',(0,0),(-1,0),8),('FONTSIZE',(0,1),(-1,-1),7),('GRID',(0,0),(-1,-1),0.5,colors.HexColor('#81c784'))]))
 story.append(table)
 doc.build(story)
 buf.seek(0)
 return buf

# LOGIN SENZA PSW SCRITTA SOTTO
if not st.session_state.authenticated:
 st.markdown(LOGHI, unsafe_allow_html=True)
 st.markdown("<h2 style='text-align:center; color:#1b5e20; background:#a5d6a7; padding:12px; border-radius:12px; border:2px solid #2e7d32;'>🔐 Accesso Riservato</h2>", unsafe_allow_html=True)
 c1,c2,c3=st.columns([1,2,1])
 with c2:
  with st.form("login"):
   pwd=st.text_input("Password *", type="password")
   if st.form_submit_button("🔴 ACCEDI", use_container_width=True, type="primary"):
    if pwd=="ANA2025":
     st.session_state.authenticated=True
     st.rerun()
    else:
     st.error("Password errata")
  # NESSUNA SCRITTA PSW SOTTO - RIMOSSA COME RICHIESTO
 st.stop()

if not st.session_state.dashboard_entered:
 st.markdown(LOGHI, unsafe_allow_html=True)
 st.markdown("<h2 style='text-align:center; color:#1b5e20; background:#a5d6a7; padding:15px; border-radius:15px; border:3px solid #2e7d32;'>🟢 ANA Varese - Protezione Civile<br><small>Sistema Gestionale - PDF A4 Orizzontale - Tutto Schermo</small></h2>", unsafe_allow_html=True)
 c1,c2,c3=st.columns([1,2,1])
 with c2:
  if st.button("🚀 ENTRA NELLA DASHBOARD", use_container_width=True, type="primary"):
   st.session_state.dashboard_entered=True
   st.rerun()
  if st.button("🔒 Logout", use_container_width=True):
   st.session_state.authenticated=False
   st.rerun()
 st.stop()

with st.sidebar:
 st.markdown(LOGHI, unsafe_allow_html=True)
 scelta=st.radio("MENU - CLICCA PER APRIRE", ["🏠 Dashboard","🚨 Interventi Emergenza","📅 Eventi","💾 Backup","🔗 Link PWA"], index=0)
 if st.button("🏠 Home", use_container_width=True):
  st.session_state.dashboard_entered=False
  st.rerun()
 if st.button("🔒 Logout", use_container_width=True):
  st.session_state.authenticated=False
  st.session_state.dashboard_entered=False
  st.rerun()

if scelta=="🏠 Dashboard":
 st.markdown(LOGHI, unsafe_allow_html=True)
 c1,c2=st.columns(2)
 c1.metric("Interventi", len(st.session_state.interventi_lista))
 c2.metric("Eventi", len(st.session_state.eventi))
 if st.session_state.interventi_lista:
  st.dataframe(pd.DataFrame(st.session_state.interventi_lista).tail(5), use_container_width=True)

elif scelta=="🚨 Interventi Emergenza":
 st.markdown(LOGHI, unsafe_allow_html=True)
 st.markdown("#### 🚨 Interventi - Tutti i campi + Via+Civico + Icone")
 with st.form("form_int", clear_on_submit=True):
  c1,c2,c3=st.columns(3)
  with c1:
   data_int=st.date_input("Data *", value=date.today())
   ora_int=st.time_input("Ora *")
   comune=st.text_input("Comune *", placeholder="Varese")
   prov=st.text_input("Prov", value="VA", max_chars=2)
   via_civico=st.text_input("Via + Civico *", placeholder="Via Roma 15")
  with c2:
   tipo=st.selectbox("Tipo con Icona *", list(ICONE.keys()))
   st.markdown(f"<div style='text-align:center; background:#e8f5e9; border:2px solid #2e7d32; padding:8px; border-radius:8px;'><span style='font-size:30px;'>{ICONE[tipo]}</span><br><b>{tipo}</b></div>", unsafe_allow_html=True)
   priorita=st.selectbox("Priorità", ["🟢 Bassa","🟡 Media","🟠 Alta","🔴 Critica"])
   odv=st.selectbox("ODV *", ["ANA Varese","ANA Sezione Varese","PC Lombardia","Croce Rossa","VVF","Altro"])
   stato=st.selectbox("Stato", ["🟡 In Corso","🟢 Completato","🔵 In Attesa"])
  with c3:
   resp=st.text_input("Responsabile *")
   cell=st.text_input("Cellulare")
   nvol=st.number_input("N° Volontari", 1, 50, 3)
   mezzi=st.text_input("Mezzi")
   durata=st.text_input("Durata")
   lat=st.text_input("Lat", placeholder="45.8205")
   lon=st.text_input("Lon", placeholder="8.8255")
  azione=st.text_area("Azione Svolta *", height=100)
  note=st.text_area("Note", height=50)
  if st.form_submit_button("🔴 SALVA INTERVENTO", use_container_width=True, type="primary"):
   if comune and via_civico and azione and resp:
    st.session_state.interventi_lista.append({"ID":len(st.session_state.interventi_lista)+1,"Logo":"ANA Varese","Icona":ICONE[tipo],"Tipo":tipo,"Data":str(data_int),"Ora":str(ora_int),"Comune":comune,"Prov":prov,"Via + Civico":via_civico,"ODV":odv,"Priorità":priorita,"Stato":stato,"Responsabile":resp,"Cell":cell,"N Vol":nvol,"Mezzi":mezzi,"Durata":durata,"Lat":lat,"Lon":lon,"Azione":azione,"Note":note,"Inserito":datetime.now().strftime("%d/%m/%Y %H:%M")})
    st.success(f"{ICONE[tipo]} Salvato in {via_civico}!")
   else:
    st.error("Compila campi *")
 
 st.divider()
 st.markdown("### 📋 Tabella Sotto il Form - Con PDF, Excel, CSV - Tutto Schermo")
 if st.session_state.interventi_lista:
  df=pd.DataFrame(st.session_state.interventi_lista)
  st.success(f"✅ {len(df)} interventi - Tabella visibile")
  st.dataframe(df, use_container_width=True, height=400)
  c1,c2,c3,c4=st.columns(4)
  with c1:
   st.download_button("📥 CSV", df.to_csv(index=False).encode('utf-8'), "interventi.csv", "text/csv", use_container_width=True, key="csv1")
  with c2:
   out=BytesIO()
   with pd.ExcelWriter(out, engine='openpyxl') as writer:
    df.to_excel(writer, index=False)
   st.download_button("📊 Excel", out.getvalue(), "interventi.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True, key="exc1")
  with c3:
   pdf=pdf_a4("Interventi Emergenza", df)
   if pdf:
    st.download_button("📄 PDF A4 Orizz", pdf.getvalue(), "interventi_A4.pdf", "application/pdf", use_container_width=True, key="pdf1")
  with c4:
   if st.button("🗑️ Cancella", use_container_width=True, key="del1"):
    st.session_state.interventi_lista=[]
    st.rerun()
 else:
  st.info("Nessun dato - Inserisci sopra")

elif scelta=="💾 Backup":
 st.markdown(LOGHI, unsafe_allow_html=True)
 st.markdown("#### 💾 Backup - Scelta CSV/Excel/PDF A4")
 dati={"Interventi":st.session_state.interventi_lista,"Eventi":st.session_state.eventi}
 sel=st.multiselect("Scegli Form", list(dati.keys()), default=["Interventi"] if dati["Interventi"] else [])
 fmt=st.radio("Formato", ["CSV","Excel","PDF A4 Orizzontale"])
 if sel and st.button("🔴 GENERA FILE", use_container_width=True, type="primary"):
  for nome in sel:
   if dati[nome]:
    df=pd.DataFrame(dati[nome])
    if fmt=="CSV":
     st.download_button(f"CSV {nome}", df.to_csv(index=False).encode('utf-8'), f"{nome}.csv", use_container_width=True, key=f"c_{nome}")
    elif fmt=="Excel":
     out=BytesIO()
     with pd.ExcelWriter(out, engine='openpyxl') as writer:
      df.to_excel(writer, index=False)
     st.download_button(f"Excel {nome}", out.getvalue(), f"{nome}.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True, key=f"e_{nome}")
    else:
     pdf=pdf_a4(nome, df)
     if pdf:
      st.download_button(f"PDF {nome}", pdf.getvalue(), f"{nome}_A4.pdf", "application/pdf", use_container_width=True, key=f"p_{nome}")

else:
 st.markdown(LOGHI, unsafe_allow_html=True)
 st.info(f"Modulo {scelta} - Con tabella sotto form + PDF + Excel")

st.caption("ANA Varese - Fix PSW nascosta + Loghi ufficiali + Menu funzionante + Tutti campi + Tabella sotto + PDF A4 Orizz + Tasti Rossi + Verde ANA")
