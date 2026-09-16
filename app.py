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

st.set_page_config(page_title="ANA Varese 12 Form - Logo Default Volontariato", page_icon="🟢", layout="wide")

# Inizializza tutti i form
for k,v in [("authenticated",False),("dashboard_entered",False),("interventi_lista",[]),("eventi",[]),("mem_nomi",["Mario Rossi","Luigi Bianchi","Giuseppe Verdi"]),("radio_db",[]),("dist_radio",[]),("postazioni",[]),("brogliaccio",[]),("registro_radio",[]),("volontari_full",[]),("checkin",{})]:
 if k not in st.session_state:
  st.session_state[k]=v

ICONE={"🔥 Incendio Boschivo":"🔥","🌊 Alluvione":"🌊","❄️ Neve":"❄️","⛰️ Frana":"⛰️","🔍 Ricerca Persona":"🔍","👥 Supporto Popolazione":"👥","👁️ Monitoraggio":"👁️","🚧 Presidio":"🚧","🚑 Sanitario":"🚑","🏚️ Crollo":"🏚️","🌲 Antincendio":"🌲","⚡ Blackout":"⚡","🦺 Esercitazione":"🦺","🎪 Manifestazione":"🎪","🚨 Altro":"🚨"}

def get_b64(p):
 try:
  if os.path.exists(p):
   with open(p,"rb") as f:
    return base64.b64encode(f.read()).decode()
 except:
  pass
 return ""

# LOGO DEFAULT RICHIESTO: Volontariato Sezione di Varese su tutti i fogli e form
b64_vol_default=get_b64("/mnt/data/Circular_Volontariato_Emblem")
b64_ana=get_b64("/mnt/data/Green_Alpini_Emblem")
b64_pc=get_b64("/mnt/data/Protezione_Civile_Lombardia_Emblem")

if b64_vol_default:
 LOGHI=f"""
 <div style='display:flex; justify-content:center; align-items:center; gap:25px; background:#a5d6a7; padding:15px; border-radius:15px; border:3px solid #2e7d32; margin-bottom:15px; flex-wrap:wrap;'>
  <div style='text-align:center;'>
   <img src='data:image/jpeg;base64,{b64_vol_default}' style='width:130px; height:130px; border-radius:50%; border:4px solid #1b5e20; background:white; box-shadow:0 4px 8px rgba(0,0,0,0.2);'>
   <div style='margin-top:6px;'><b style='color:#1b5e20;'>VOLONTARIATO</b><br><small style='color:#2e7d32; font-weight:bold;'>Sezione di VARESE</small></div>
  </div>
  <div style='text-align:center; max-width:450px;'>
   <h3 style='color:#1b5e20; margin:0;'>ANA Varese - Protezione Civile</h3>
   <small style='color:#2e7d32;'>12 Form Completi | PDF A4 Orizzontale | Import/Export Excel CSV | Tabella Sotto Ogni Form<br><b>Logo Default: Volontariato Sezione Varese su tutti i fogli</b></small>
  </div>
 </div>
 """
else:
 LOGHI="<div style='background:#a5d6a7; padding:15px; border-radius:12px; border:3px solid #2e7d32; text-align:center;'><h3 style='color:#1b5e20; margin:0;'>🟢 VOLONTARIATO Sezione di VARESE - Logo Default su tutti i fogli</h3></div>"

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
<link rel="manifest" href="./manifest.json">
<meta name="theme-color" content="#2e7d32">
""", unsafe_allow_html=True)

def pdf_a4(titolo, df):
 if not HAS or df is None or df.empty:
  return None
 buf=BytesIO()
 doc=SimpleDocTemplate(buf, pagesize=landscape(A4), leftMargin=1*cm, rightMargin=1*cm, topMargin=1*cm, bottomMargin=1*cm)
 styles=getSampleStyleSheet()
 title_style=ParagraphStyle('t', parent=styles['Heading1'], fontSize=14, textColor=colors.HexColor('#1b5e20'), alignment=1)
 story=[Paragraph(f"<b>{titolo} - VOLONTARIATO Sezione di VARESE - Logo Default</b>", title_style), Paragraph(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')} - A4 Orizzontale - Logo Default su tutti i fogli", styles['Normal']), Spacer(1,0.5*cm)]
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

def mostra_tabella_con_import_export(nome_form, lista_dati, chiavi_df):
 st.divider()
 st.markdown(f"### 📋 {nome_form} - Tabella + Import/Export Excel e CSV")
 # IMPORT
 c1,c2=st.columns(2)
 with c1:
  f_csv=st.file_uploader(f"📥 Importa CSV - {nome_form}", type=["csv"], key=f"imp_csv_{nome_form}")
  if f_csv:
   try:
    df_imp=pd.read_csv(f_csv)
    if st.button(f"✅ Conferma Importa CSV {nome_form}", key=f"btn_csv_{nome_form}"):
     for _,r in df_imp.iterrows():
      lista_dati.append(r.to_dict())
     st.success(f"Importati {len(df_imp)} da CSV!")
     st.rerun()
   except Exception as e:
    st.error(f"Errore CSV: {e}")
 with c2:
  f_xls=st.file_uploader(f"📥 Importa Excel - {nome_form}", type=["xlsx","xls"], key=f"imp_xls_{nome_form}")
  if f_xls:
   try:
    df_imp=pd.read_excel(f_xls)
    if st.button(f"✅ Conferma Importa Excel {nome_form}", key=f"btn_xls_{nome_form}"):
     for _,r in df_imp.iterrows():
      lista_dati.append(r.to_dict())
     st.success(f"Importati {len(df_imp)} da Excel!")
     st.rerun()
   except Exception as e:
    st.error(f"Errore Excel: {e}")
 # TABELLA SOTTO FORM
 if lista_dati:
  df=pd.DataFrame(lista_dati)
  st.success(f"✅ {len(df)} record in {nome_form} - Tabella visibile - Logo Default Volontariato")
  st.dataframe(df, use_container_width=True, height=350)
  c1,c2,c3,c4=st.columns(4)
  with c1:
   st.download_button(f"📥 Export CSV", df.to_csv(index=False).encode('utf-8'), f"{nome_form.replace(' ','_')}.csv", "text/csv", use_container_width=True, key=f"exp_csv_{nome_form}")
  with c2:
   out=BytesIO()
   with pd.ExcelWriter(out, engine='openpyxl') as writer:
    df.to_excel(writer, index=False)
   st.download_button(f"📊 Export Excel", out.getvalue(), f"{nome_form.replace(' ','_')}.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True, key=f"exp_xls_{nome_form}")
  with c3:
   pdf=pdf_a4(nome_form, df)
   if pdf:
    st.download_button(f"📄 PDF A4 Orizz", pdf.getvalue(), f"{nome_form.replace(' ','_')}_A4.pdf", "application/pdf", use_container_width=True, key=f"exp_pdf_{nome_form}")
  with c4:
   if st.button(f"🗑️ Cancella Tutti", key=f"del_{nome_form}", use_container_width=True):
    lista_dati.clear()
    st.rerun()
 else:
  st.info(f"📭 Nessun dato in {nome_form} - Inserisci sopra e vedrai la tabella qui sotto con Import/Export")

# LOGIN SENZA SCRITTA PSW
if not st.session_state.authenticated:
 st.markdown(LOGHI, unsafe_allow_html=True)
 st.markdown("<h2 style='text-align:center; color:#1b5e20; background:#a5d6a7; padding:12px; border-radius:12px; border:2px solid #2e7d32;'>🔐 Accesso Riservato - Logo Default Volontariato Sezione Varese</h2>", unsafe_allow_html=True)
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
 st.stop()

if not st.session_state.dashboard_entered:
 st.markdown(LOGHI, unsafe_allow_html=True)
 st.markdown("<h2 style='text-align:center; color:#1b5e20; background:#a5d6a7; padding:15px; border-radius:15px; border:3px solid #2e7d32;'>🟢 ANA Varese - Protezione Civile<br><small>12 Form Completi - Logo Default Volontariato su tutti i fogli - PDF A4 Orizz - Import/Export Excel CSV - Tabella Sotto</small></h2>", unsafe_allow_html=True)
 c1,c2,c3=st.columns([1,2,1])
 with c2:
  if st.button("🚀 ENTRA NELLA DASHBOARD - 12 FORM", use_container_width=True, type="primary"):
   st.session_state.dashboard_entered=True
   st.rerun()
  if st.button("🔒 Logout", use_container_width=True):
   st.session_state.authenticated=False
   st.rerun()
 st.stop()

# SIDEBAR 12 FORM FUNZIONANTE
with st.sidebar:
 st.markdown(LOGHI, unsafe_allow_html=True)
 scelta=st.radio("MENU 12 FORM - CLICCA PER APRIRE", ["🏠 Dashboard","📅 Gestione Eventi","✅ Check-In Volontari","👥 Volontari - Anagrafica","📻 DB Radio Inventario","📦 Distribuzione Radio","🗺️ Mappa Postazioni","🚨 Interventi Emergenza","📝 Brogliaccio ODV","📝 Registro Radio","💾 Backup Export/Import","🔗 Link & Icona PWA"], index=0)
 st.divider()
 if st.button("🏠 Torna Entra Dashboard", use_container_width=True):
  st.session_state.dashboard_entered=False
  st.rerun()
 if st.button("🔒 Logout Completo", use_container_width=True):
  st.session_state.authenticated=False
  st.session_state.dashboard_entered=False
  st.rerun()

st.markdown(f"<h2 style='color:#1b5e20; background:#a5d6a7; padding:12px; border-radius:12px; border:3px solid #2e7d32;'>🟢 {scelta} - Logo Default Volontariato Sezione Varese</h2>", unsafe_allow_html=True)

def dash_btn(k):
 c1,c2=st.columns(2)
 with c1:
  if st.button("🏠 Dashboard", key=f"d_{k}", use_container_width=True):
   st.rerun()
 with c2:
  if st.button("🏠 Home Entra", key=f"h_{k}", use_container_width=True):
   st.session_state.dashboard_entered=False
   st.rerun()

if scelta=="🏠 Dashboard":
 st.markdown(LOGHI, unsafe_allow_html=True)
 st.markdown("#### 📋 Dashboard - Elenco 12 Form - Clicca nel menu a sinistra per aprire ogni form - Logo Default Volontariato su tutti i fogli")
 c1,c2,c3,c4=st.columns(4)
 c1.metric("Interventi", len(st.session_state.interventi_lista))
 c2.metric("Eventi", len(st.session_state.eventi))
 c3.metric("Volontari", len(st.session_state.mem_nomi))
 c4.metric("Radio", len(st.session_state.radio_db))
 st.divider()
 st.markdown("### 📋 Elenco Form Disponibili - Clicca sul menu a sinistra:")
 form_list=["📅 Gestione Eventi","✅ Check-In Volontari","👥 Volontari - Anagrafica","📻 DB Radio Inventario","📦 Distribuzione Radio","🗺️ Mappa Postazioni","🚨 Interventi Emergenza","📝 Brogliaccio ODV","📝 Registro Radio","💾 Backup Export/Import","🔗 Link & Icona PWA"]
 for f in form_list:
  st.markdown(f"- **{f}** - Logo Default Volontariato - Import/Export Excel CSV - Tabella sotto form")
 if st.session_state.interventi_lista:
  st.divider()
  st.markdown("#### Ultimi 5 Interventi")
  st.dataframe(pd.DataFrame(st.session_state.interventi_lista).tail(5), use_container_width=True)
 dash_btn("dash")

elif scelta=="🚨 Interventi Emergenza":
 st.markdown(LOGHI, unsafe_allow_html=True)
 st.markdown("#### 🚨 Interventi - Via+Civico + Icone + Tutti campi - Logo Default Volontariato")
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
    st.session_state.interventi_lista.append({"ID":len(st.session_state.interventi_lista)+1,"Logo Default":"VOLONTARIATO Sezione Varese","Icona":ICONE[tipo],"Tipo":tipo,"Data":str(data_int),"Ora":str(ora_int),"Comune":comune,"Prov":prov,"Via + Civico":via_civico,"ODV":odv,"Priorità":priorita,"Stato":stato,"Responsabile":resp,"Cell":cell,"N Vol":nvol,"Mezzi":mezzi,"Durata":durata,"Lat":lat,"Lon":lon,"Azione":azione,"Note":note,"Inserito":datetime.now().strftime("%d/%m/%Y %H:%M")})
    st.success(f"{ICONE[tipo]} Salvato in {via_civico}! Logo Default Volontariato")
   else:
    st.error("Compila campi *")
 mostra_tabella_con_import_export("Interventi Emergenza", st.session_state.interventi_lista, [])
 dash_btn("int")

elif scelta=="📅 Gestione Eventi":
 st.markdown(LOGHI, unsafe_allow_html=True)
 with st.form("ev_form", clear_on_submit=True):
  c1,c2=st.columns(2)
  with c1:
   tipo=st.selectbox("Tipo Evento *", ["Monitoraggio","Antincendio","Alluvione","Esercitazione","Supporto","Altro"])
   desc=st.text_area("Descrizione *", height=80)
   comune=st.text_input("Comune *", value="Varese")
  with c2:
   d_ini=st.date_input("Data Inizio *")
   o_ini=st.time_input("Ora Inizio *")
   resp=st.text_input("Responsabile *")
   cell=st.text_input("Cellulare")
  if st.form_submit_button("🔴 SALVA EVENTO", use_container_width=True, type="primary"):
   if desc and comune and resp:
    st.session_state.eventi.append({"Logo Default":"VOLONTARIATO Sezione Varese","Tipo":tipo,"Descrizione":desc,"Comune":comune,"Data":str(d_ini),"Ora":str(o_ini),"Responsabile":resp,"Cell":cell})
    st.success("Evento salvato! Logo Default Volontariato")
 mostra_tabella_con_import_export("Eventi", st.session_state.eventi, [])
 dash_btn("ev")

elif scelta=="👥 Volontari - Anagrafica":
 st.markdown(LOGHI, unsafe_allow_html=True)
 with st.form("vol_form", clear_on_submit=True):
  c1,c2=st.columns(2)
  with c1:
   nome=st.text_input("Nome *")
   cognome=st.text_input("Cognome *")
   cell=st.text_input("Cellulare *")
  with c2:
   comune=st.text_input("Comune", value="Varese")
   ruolo=st.selectbox("Ruolo", ["Volontario","Capo Squadra","Coordinatore"])
  if st.form_submit_button("🔴 SALVA VOLONTARIO", use_container_width=True, type="primary"):
   if nome and cognome and cell:
    nome_full=f"{nome} {cognome}"
    if nome_full not in st.session_state.mem_nomi:
     st.session_state.mem_nomi.append(nome_full)
    st.session_state.volontari_full.append({"Logo Default":"VOLONTARIATO Sezione Varese","Nome":nome,"Cognome":cognome,"Nome Completo":nome_full,"Cell":cell,"Comune":comune,"Ruolo":ruolo})
    st.success(f"Salvato {nome_full}! Logo Default")
 mostra_tabella_con_import_export("Volontari", st.session_state.volontari_full, [])
 dash_btn("vol")

elif scelta=="📻 DB Radio Inventario":
 st.markdown(LOGHI, unsafe_allow_html=True)
 with st.form("radio_form", clear_on_submit=True):
  c1,c2=st.columns(2)
  with c1:
   id_r=st.text_input("ID Radio *", placeholder="RAD-001")
   modello=st.text_input("Modello", placeholder="Motorola")
  with c2:
   stato=st.selectbox("Stato", ["Operativa","In Carica","Guasta"])
   note=st.text_input("Note")
  if st.form_submit_button("🔴 SALVA RADIO", use_container_width=True, type="primary"):
   if id_r:
    st.session_state.radio_db.append({"Logo Default":"VOLONTARIATO Sezione Varese","ID":id_r,"Modello":modello,"Stato":stato,"Note":note})
    st.success("Radio salvata! Logo Default")
 mostra_tabella_con_import_export("Radio Inventario", st.session_state.radio_db, [])
 dash_btn("radio")

elif scelta=="📦 Distribuzione Radio":
 st.markdown(LOGHI, unsafe_allow_html=True)
 with st.form("dist_form", clear_on_submit=True):
  radio=st.selectbox("Radio", [r["ID"] for r in st.session_state.radio_db] if st.session_state.radio_db else ["RAD-001"])
  vol=st.selectbox("Volontario", st.session_state.mem_nomi)
  if st.form_submit_button("🔴 CONSEGNA RADIO", use_container_width=True, type="primary"):
   st.session_state.dist_radio.append({"Logo Default":"VOLONTARIATO Sezione Varese","Radio":radio,"Volontario":vol,"Data":str(date.today())})
   st.success("Consegnata! Logo Default")
 mostra_tabella_con_import_export("Distribuzione Radio", st.session_state.dist_radio, [])
 dash_btn("dist")

elif scelta=="🗺️ Mappa Postazioni":
 st.markdown(LOGHI, unsafe_allow_html=True)
 with st.form("post_form", clear_on_submit=True):
  nome=st.text_input("Nome Postazione *", placeholder="Postazione 1")
  comune=st.text_input("Comune *", value="Varese")
  via=st.text_input("Via + Civico *", placeholder="Via Roma 15")
  if st.form_submit_button("🔴 SALVA POSTAZIONE", use_container_width=True, type="primary"):
   if nome and comune:
    st.session_state.postazioni.append({"Logo Default":"VOLONTARIATO Sezione Varese","Postazione":nome,"Comune":comune,"Via + Civico":via})
    st.success("Salvata! Logo Default")
 mostra_tabella_con_import_export("Postazioni", st.session_state.postazioni, [])
 dash_btn("post")

elif scelta=="📝 Brogliaccio ODV":
 st.markdown(LOGHI, unsafe_allow_html=True)
 with st.form("brog_form", clear_on_submit=True):
  msg=st.text_area("Messaggio *", height=100)
  if st.form_submit_button("🔴 SALVA BROGLIACCIO", use_container_width=True, type="primary"):
   if msg:
    st.session_state.brogliaccio.append({"Logo Default":"VOLONTARIATO Sezione Varese","Data":str(date.today()),"Ora":str(datetime.now().strftime("%H:%M")),"Messaggio":msg})
    st.success("Salvato! Logo Default")
 mostra_tabella_con_import_export("Brogliaccio ODV", st.session_state.brogliaccio, [])
 dash_btn("brog")

elif scelta=="📝 Registro Radio":
 st.markdown(LOGHI, unsafe_allow_html=True)
 with st.form("reg_form", clear_on_submit=True):
  radio=st.selectbox("Radio", [r["ID"] for r in st.session_state.radio_db] if st.session_state.radio_db else ["RAD-001"])
  vol=st.selectbox("Volontario", st.session_state.mem_nomi)
  note=st.text_input("Note")
  if st.form_submit_button("🔴 SALVA REGISTRO", use_container_width=True, type="primary"):
   st.session_state.registro_radio.append({"Logo Default":"VOLONTARIATO Sezione Varese","Radio":radio,"Volontario":vol,"Note":note,"Data":str(date.today())})
   st.success("Salvato! Logo Default")
 mostra_tabella_con_import_export("Registro Radio", st.session_state.registro_radio, [])
 dash_btn("regradio")

elif scelta=="✅ Check-In Volontari":
 st.markdown(LOGHI, unsafe_allow_html=True)
 if not st.session_state.eventi:
  st.warning("Crea prima un evento in Gestione Eventi")
  mostra_tabella_con_import_export("Check-In", [], [])
 else:
  ids=[f"{i} - {e['Comune']} - {e['Tipo']}" for i,e in enumerate(st.session_state.eventi)]
  sel=st.selectbox("Evento *", ids)
  idx=int(sel.split(" - ")[0])
  vol=st.selectbox("Volontario *", st.session_state.mem_nomi)
  if st.button("🔴 CHECK-IN", use_container_width=True, type="primary"):
   if idx not in st.session_state.checkin:
    st.session_state.checkin[idx]=[]
   st.session_state.checkin[idx].append({"Logo Default":"VOLONTARIATO Sezione Varese","Volontario":vol,"Ora":datetime.now().strftime("%H:%M"),"Data":str(date.today())})
   st.success("Check-In fatto! Logo Default")
  if idx in st.session_state.checkin and st.session_state.checkin[idx]:
   st.dataframe(pd.DataFrame(st.session_state.checkin[idx]), use_container_width=True, height=300)
   c1,c2,c3=st.columns(3)
   df=pd.DataFrame(st.session_state.checkin[idx])
   with c1:
    st.download_button("📥 Export CSV Check-In", df.to_csv(index=False).encode('utf-8'), "checkin.csv", use_container_width=True)
   with c2:
    out=BytesIO()
    with pd.ExcelWriter(out, engine='openpyxl') as writer:
     df.to_excel(writer, index=False)
    st.download_button("📊 Export Excel Check-In", out.getvalue(), "checkin.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
   with c3:
    pdf=pdf_a4("Check-In", df)
    if pdf:
     st.download_button("📄 PDF Check-In", pdf.getvalue(), "checkin_A4.pdf", "application/pdf", use_container_width=True)
 dash_btn("checkin")

elif scelta=="💾 Backup Export/Import":
 st.markdown(LOGHI, unsafe_allow_html=True)
 st.markdown("#### 💾 Backup - Import/Export Excel e CSV per ogni form - 12 Form - Logo Default Volontariato")
 dati={"🚨 Interventi":st.session_state.interventi_lista,"📅 Eventi":st.session_state.eventi,"👥 Volontari":st.session_state.volontari_full,"📻 Radio":st.session_state.radio_db,"📦 Distribuzione":st.session_state.dist_radio,"🗺️ Postazioni":st.session_state.postazioni,"📝 Brogliaccio":st.session_state.brogliaccio,"📝 Registro":st.session_state.registro_radio}
 for k,v in dati.items():
  st.write(f"{k}: {len(v)} record - Logo Default Volontariato")
 sel=st.multiselect("Scegli Form da Esportare", list(dati.keys()), default=["🚨 Interventi"] if dati["🚨 Interventi"] else [])
 fmt=st.radio("Formato Export", ["CSV","Excel","PDF A4 Orizzontale con Logo Default","ZIP Completo"])
 if sel and st.button("🔴 GENERA FILE EXPORT", use_container_width=True, type="primary"):
  for nome in sel:
   if dati[nome]:
    df=pd.DataFrame(dati[nome])
    if "Logo" not in str(df.columns):
     df.insert(0,"Logo Default",["VOLONTARIATO Sezione Varese"]*len(df))
    if fmt=="CSV":
     st.download_button(f"📥 CSV {nome}", df.to_csv(index=False).encode('utf-8'), f"{nome[:10]}.csv", "text/csv", use_container_width=True, key=f"csv_{nome}")
    elif fmt=="Excel":
     out=BytesIO()
     with pd.ExcelWriter(out, engine='openpyxl') as writer:
      df.to_excel(writer, index=False)
     st.download_button(f"📊 Excel {nome}", out.getvalue(), f"{nome[:10]}.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True, key=f"excel_{nome}")
    elif "PDF" in fmt:
     pdf=pdf_a4(nome, df)
     if pdf:
      st.download_button(f"📄 PDF A4 {nome}", pdf.getvalue(), f"{nome[:10]}_A4.pdf", "application/pdf", use_container_width=True, key=f"pdf_{nome}")
 dash_btn("backup")

elif scelta=="🔗 Link & Icona PWA":
 st.markdown(LOGHI, unsafe_allow_html=True)
 st.markdown("""<div style='background:#c8e6c9; padding:15px; border-radius:10px; border:2px solid #2e7d32;'>
 <b>📱 Icona PWA - Logo Default Volontariato Sezione Varese:</b><br>
 1. Apri link app su telefono<br>
 2. Android: Menu ⋮ → Aggiungi a schermata Home → Icona con logo Volontariato appare<br>
 3. iPhone: Condividi → Aggiungi a Home → Icona<br>
 <b>File inclusi:</b> manifest.json + 3 loghi JPG + Logo Default Volontariato su tutti i fogli
 </div>""", unsafe_allow_html=True)
 url=st.text_input("URL App", placeholder="https://ana-varese.streamlit.app")
 if url:
  st.link_button("📱 Condividi su WhatsApp", f"https://wa.me/?text=Installa icona ANA Varese Logo Volontariato: {url}", use_container_width=True)
 dash_btn("link")

st.caption("ANA Varese - 12 Form Completi - Logo Default VOLONTARIATO Sezione Varese su tutti i fogli e form - Import/Export Excel CSV per ogni form - Tabella sotto ogni form - Fix PSW nascosta - Menu funzionante - PDF A4 Orizz - Tasti Rossi - Verde ANA - Tutto Schermo - PWA")
