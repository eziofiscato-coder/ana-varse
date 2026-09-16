import streamlit as st
import pandas as pd
from datetime import datetime, date
from io import BytesIO
import base64, os, json

try:
 from reportlab.lib.pagesizes import landscape, A4
 from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
 from reportlab.lib import colors
 from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
 from reportlab.lib.units import cm
 HAS=True
except:
 HAS=False

st.set_page_config(page_title="ANA Varese 12 Form - Icone Libreria + Comuni + Vie", page_icon="🟢", layout="wide")

for k,v in [("authenticated",False),("dashboard_entered",False),("interventi_lista",[]),("eventi",[]),("mem_nomi",["Mario Rossi","Luigi Bianchi","Giuseppe Verdi"]),("radio_db",[]),("dist_radio",[]),("postazioni",[]),("brogliaccio",[]),("registro_radio",[]),("volontari_full",[]),("checkin",{}),("icone_personalizzate",[])]:
 if k not in st.session_state:
  st.session_state[k]=v

ICONE={"🔥 Incendio Boschivo":"🔥","🌊 Alluvione":"🌊","❄️ Neve":"❄️","⛰️ Frana":"⛰️","🔍 Ricerca Persona":"🔍","👥 Supporto Popolazione":"👥","👁️ Monitoraggio":"👁️","🚧 Presidio":"🚧","🚑 Sanitario":"🚑","🏚️ Crollo":"🏚️","🌲 Antincendio":"🌲","⚡ Blackout":"⚡","🦺 Esercitazione":"🦺","🎪 Manifestazione":"🎪","🚨 Altro":"🚨"}

# Libreria icone default + caricabili da PC
try:
 df_ic=pd.read_json("/mnt/data/libreria_icone_default.json")
 LIB_ICONE=df_ic.to_dict(orient="records")
except:
 LIB_ICONE=[{"nome":k,"icona":v,"categoria":"Default"} for k,v in ICONE.items()]

# Comuni italiani - lista
try:
 df_com=pd.read_csv("/mnt/data/comuni_italiani.csv")
 LISTA_COMUNI=sorted(df_comuni["Comune"].astype(str).unique().tolist())
except:
 LISTA_COMUNI=["Varese","Busto Arsizio","Gallarate","Saronno","Cassano Magnago","Tradate","Somma Lombardo","Malnate","Luino","Samarate","Lonate Pozzolo","Castellanza","Fagnano Olona","Caronno Pertusella","Venegono Superiore","Venegono Inferiore","Gavirate","Milano","Roma","Torino","Napoli","Firenze","Bologna","Genova","Venezia","Verona","Como","Lecco","Monza","Bergamo","Brescia"]

# Vie per comune
try:
 df_vie=pd.read_csv("/mnt/data/vie_per_comune.csv")
 VIE_PER_COMUNE={}
 for c in df_vie["Comune"].unique():
  VIE_PER_COMUNE[c]=df_vie[df_vie["Comune"]==c]["Via"].astype(str).unique().tolist()
except:
 VIE_PER_COMUNE={"Varese":["Via Roma","Via Milano","Via Garibaldi","Via Verdi","Via Manzoni","Via Cavour","Via Matteotti","Via Volta","Via San Michele","Via XXV Aprile","Via Marconi","Via Dante"]}

def get_b64(p):
 try:
  if os.path.exists(p):
   with open(p,"rb") as f:
    return base64.b64encode(f.read()).decode()
 except:
  pass
 return ""

b64_vol=get_b64("/mnt/data/Circular_Volontariato_Emblem")
if b64_vol:
 LOGHI=f"""<div style='display:flex; justify-content:center; align-items:center; gap:20px; background:#a5d6a7; padding:12px; border-radius:15px; border:3px solid #2e7d32; margin-bottom:12px; flex-wrap:wrap;'><img src='data:image/jpeg;base64,{b64_vol}' style='width:110px; height:110px; border-radius:50%; border:3px solid #1b5e20; background:white;'><div><h3 style='color:#1b5e20; margin:0;'>ANA Varese - VOLONTARIATO Sezione Varese</h3><small style='color:#2e7d32;'>12 Form - Icone Libreria da PC - Comuni Combo - Vie Combo Agganciate - Logo Default</small></div></div>"""
else:
 LOGHI="<div style='background:#a5d6a7; padding:12px; border-radius:12px; border:3px solid #2e7d32; text-align:center;'><h3 style='color:#1b5e20; margin:0;'>VOLONTARIATO Sezione di VARESE - Logo Default</h3></div>"

st.markdown("""<style>
.stApp{background:#e8f5e9!important;}
.main .block-container{max-width:100%!important; padding:1% 2%!important;}
[data-testid="stSidebar"]{background:#a5d6a7!important; border-right:3px solid #2e7d32!important;}
.stForm{background:#a5d6a7!important; border:3px solid #2e7d32!important; border-radius:15px!important; padding:15px!important;}
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
 title_style=ParagraphStyle('t', parent=styles['Heading1'], fontSize=12, textColor=colors.HexColor('#1b5e20'), alignment=1)
 story=[Paragraph(f"<b>{titolo} - VOLONTARIATO Sezione di VARESE</b>", title_style), Paragraph(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')} - A4 Orizzontale", styles['Normal']), Spacer(1,0.3*cm)]
 d=df.copy()
 for c in d.columns:
  d[c]=d[c].astype(str).apply(lambda x: x[:40])
 data=[d.columns.tolist()]+d.values.tolist()
 w=(27.7*cm)/len(d.columns) if len(d.columns)>0 else 10*cm
 table=Table(data, colWidths=[w]*len(d.columns), repeatRows=1)
 table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#2e7d32')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('FONTSIZE',(0,0),(-1,0),7),('FONTSIZE',(0,1),(-1,-1),6),('GRID',(0,0),(-1,-1),0.5,colors.HexColor('#81c784'))]))
 story.append(table)
 doc.build(story)
 buf.seek(0)
 return buf

def tabella_import_export(nome, lista):
 st.divider()
 st.markdown(f"### 📋 {nome} - Tabella + Import/Export Excel CSV")
 c1,c2=st.columns(2)
 with c1:
  f_csv=st.file_uploader(f"📥 Importa CSV - {nome}", type=["csv"], key=f"imp_csv_{nome}")
  if f_csv:
   try:
    df_imp=pd.read_csv(f_csv)
    if st.button(f"✅ Importa CSV {nome}", key=f"btn_csv_{nome}"):
     for _,r in df_imp.iterrows():
      lista.append(r.to_dict())
     st.success(f"Importati {len(df_imp)}")
     st.rerun()
   except Exception as e:
    st.error(f"Err CSV: {e}")
 with c2:
  f_xls=st.file_uploader(f"📥 Importa Excel - {nome}", type=["xlsx","xls"], key=f"imp_xls_{nome}")
  if f_xls:
   try:
    df_imp=pd.read_excel(f_xls)
    if st.button(f"✅ Importa Excel {nome}", key=f"btn_xls_{nome}"):
     for _,r in df_imp.iterrows():
      lista.append(r.to_dict())
     st.success(f"Importati {len(df_imp)}")
     st.rerun()
   except Exception as e:
    st.error(f"Err Excel: {e}")
 if lista:
  df=pd.DataFrame(lista)
  st.success(f"✅ {len(df)} record - Tabella visibile - Logo Default Volontariato")
  st.dataframe(df, use_container_width=True, height=300)
  c1,c2,c3,c4=st.columns(4)
  with c1:
   st.download_button("📥 Export CSV", df.to_csv(index=False).encode('utf-8'), f"{nome}.csv", "text/csv", use_container_width=True, key=f"exp_csv_{nome}")
  with c2:
   out=BytesIO()
   with pd.ExcelWriter(out, engine='openpyxl') as writer:
    df.to_excel(writer, index=False)
   st.download_button("📊 Export Excel", out.getvalue(), f"{nome}.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True, key=f"exp_xls_{nome}")
  with c3:
   pdf=pdf_a4(nome, df)
   if pdf:
    st.download_button("📄 PDF A4", pdf.getvalue(), f"{nome}_A4.pdf", "application/pdf", use_container_width=True, key=f"exp_pdf_{nome}")
  with c4:
   if st.button("🗑️ Cancella", key=f"del_{nome}", use_container_width=True):
    lista.clear()
    st.rerun()
 else:
  st.info(f"📭 Nessun dato in {nome} - Inserisci sopra")

if not st.session_state.authenticated:
 st.markdown(LOGHI, unsafe_allow_html=True)
 st.markdown("<h2 style='text-align:center; color:#1b5e20; background:#a5d6a7; padding:10px; border-radius:12px; border:2px solid #2e7d32;'>🔐 Accesso Riservato - Logo Default Volontariato</h2>", unsafe_allow_html=True)
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
 st.markdown("<h2 style='text-align:center; color:#1b5e20; background:#a5d6a7; padding:12px; border-radius:15px; border:3px solid #2e7d32;'>🟢 ANA Varese - 12 Form - Libreria Icone da PC + Comuni Italia Combo + Vie Combo</h2>", unsafe_allow_html=True)
 c1,c2,c3=st.columns([1,2,1])
 with c2:
  if st.button("🚀 ENTRA DASHBOARD 12 FORM", use_container_width=True, type="primary"):
   st.session_state.dashboard_entered=True
   st.rerun()
  if st.button("🔒 Logout", use_container_width=True):
   st.session_state.authenticated=False
   st.rerun()
 st.stop()

with st.sidebar:
 st.markdown(LOGHI, unsafe_allow_html=True)
 scelta=st.radio("MENU 12 FORM - Clicca per aprire", ["🏠 Dashboard","📅 Gestione Eventi","✅ Check-In Volontari","👥 Volontari - Anagrafica","📻 DB Radio Inventario","📦 Distribuzione Radio","🗺️ Mappa Postazioni","🚨 Interventi Emergenza","📝 Brogliaccio ODV","📝 Registro Radio","💾 Backup Export/Import","🔗 Link & Icona PWA"], index=0)
 if st.button("🏠 Home", use_container_width=True):
  st.session_state.dashboard_entered=False
  st.rerun()
 if st.button("🔒 Logout", use_container_width=True):
  st.session_state.authenticated=False
  st.session_state.dashboard_entered=False
  st.rerun()

st.markdown(f"<h2 style='color:#1b5e20; background:#a5d6a7; padding:10px; border-radius:12px; border:3px solid #2e7d32;'>🟢 {scelta}</h2>", unsafe_allow_html=True)

def dash_btn(k):
 c1,c2=st.columns(2)
 with c1:
  if st.button("🏠 Dashboard", key=f"d_{k}", use_container_width=True):
   st.rerun()
 with c2:
  if st.button("🏠 Home", key=f"h_{k}", use_container_width=True):
   st.session_state.dashboard_entered=False
   st.rerun()

if scelta=="🏠 Dashboard":
 st.markdown(LOGHI, unsafe_allow_html=True)
 st.markdown("#### Dashboard - 12 Form - Libreria Icone da PC + Comuni Combo + Vie Combo Agganciate")
 c1,c2,c3,c4=st.columns(4)
 c1.metric("Interventi", len(st.session_state.interventi_lista))
 c2.metric("Eventi", len(st.session_state.eventi))
 c3.metric("Volontari", len(st.session_state.mem_nomi))
 c4.metric("Radio", len(st.session_state.radio_db))
 st.markdown("**Form disponibili:** 📅 Eventi, ✅ Check-In, 👥 Volontari, 📻 Radio, 📦 Distribuzione, 🗺️ Postazioni, 🚨 Interventi Emergenza (Icone Libreria + Comuni Combo + Vie Combo), 📝 Brogliaccio, 📝 Registro, 💾 Backup, 🔗 PWA")
 if st.session_state.interventi_lista:
  st.dataframe(pd.DataFrame(st.session_state.interventi_lista).tail(5), use_container_width=True)
 dash_btn("dash")

elif scelta=="🚨 Interventi Emergenza":
 st.markdown(LOGHI, unsafe_allow_html=True)
 st.markdown("#### 🚨 Interventi Emergenza - Logo Default Volontariato - Libreria Icone da PC + Icona Associata + Comuni Italia Combo + Vie Combo Agganciate")
 with st.expander("🎨 Libreria Icone - Carica icone da PC - Icona associata all'intervento", expanded=True):
  c1,c2=st.columns([2,1])
  with c1:
   ups=st.file_uploader("📁 Carica icone da PC (PNG/JPG/ICO)", type=["png","jpg","jpeg","ico"], accept_multiple_files=True, key="up_icone")
   if ups:
    for up in ups:
     st.session_state.icone_personalizzate.append({"nome":up.name.split(".")[0],"icona":"🖼️","file_name":up.name,"categoria":"Personalizzata"})
    st.success(f"Caricate {len(ups)} icone nella libreria!")
  with c2:
   st.markdown("**Icone disponibili:**")
   tutte=LIB_ICONE+st.session_state.icone_personalizzate
   for ic in tutte[:8]:
    st.write(f"{ic.get('icona','🔹')} {ic.get('nome','')}")
 
 with st.form("form_int", clear_on_submit=True):
  c1,c2,c3=st.columns(3)
  with c1:
   data_int=st.date_input("Data *", value=date.today())
   ora_int=st.time_input("Ora *")
   # COMUNE COMBO - Tutti comuni Italia
   comune=st.selectbox("Comune * - Combo Tutti Comuni Italia", options=LISTA_COMUNI, index=LISTA_COMUNI.index("Varese") if "Varese" in LISTA_COMUNI else 0, help="Combo con tutti i comuni d'Italia - Importa lista completa ISTAT via CSV")
   prov=st.text_input("Prov", value="VA", max_chars=2)
   # VIE COMBO - Agganciato a comune
   vie_list=VIE_PER_COMUNE.get(comune, ["Via Roma","Via Milano","Via Garibaldi","Via Verdi","Via Manzoni","Via Cavour","Via Matteotti","Via Volta","Via San Michele","Via XXV Aprile"])
   via_sel=st.selectbox(f"Via * - Combo vie di {comune} (agganciato a comune)", options=vie_list+["-- Nuova via --"], help=f"Vie associate a {comune} - Combo agganciata al campo comune")
   if via_sel=="-- Nuova via --":
    via_custom=st.text_input("Nuova Via *", placeholder="Via Roma")
    civ=st.text_input("Civico *", placeholder="15")
    via_civico=f"{via_custom} {civ}".strip()
   else:
    civ=st.text_input(f"Civico per {via_sel} *", placeholder="15")
    via_civico=f"{via_sel} {civ}".strip() if civ else via_sel
  with c2:
   # ICONA CON LIBRERIA - Icona associata
   tutte_icone=LIB_ICONE+st.session_state.icone_personalizzate
   opts=[f"{ic.get('icona','🔹')} {ic.get('nome','')}" for ic in tutte_icone]
   tipo=st.selectbox("Icona Intervento * - Libreria da PC + Icona associata", options=opts, help="Seleziona icona - Libreria caricabile da PC - Icona associata all'intervento")
   icona_sel=tipo.split(" ")[0] if tipo else "🚨"
   nome_tipo=" ".join(tipo.split(" ")[1:]) if len(tipo.split(" "))>1 else tipo
   st.markdown(f"<div style='text-align:center; background:#e8f5e9; border:3px solid #2e7d32; padding:10px; border-radius:12px;'><span style='font-size:35px;'>{icona_sel}</span><br><b>{nome_tipo}</b><br><small>Icona associata - Libreria da PC</small></div>", unsafe_allow_html=True)
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
  azione=st.text_area("Azione Svolta *", height=80)
  note=st.text_area("Note", height=40)
  if st.form_submit_button("🔴 SALVA INTERVENTO", use_container_width=True, type="primary"):
   if comune and via_civico and azione and resp:
    st.session_state.interventi_lista.append({"ID":len(st.session_state.interventi_lista)+1,"Logo Default":"VOLONTARIATO Varese","Icona":icona_sel,"Tipo":nome_tipo,"Icona File":tipo,"Data":str(data_int),"Ora":str(ora_int),"Comune":comune,"Prov":prov,"Via + Civico":via_civico,"ODV":odv,"Priorità":priorita,"Stato":stato,"Responsabile":resp,"Cell":cell,"N Vol":nvol,"Mezzi":mezzi,"Durata":durata,"Lat":lat,"Lon":lon,"Azione":azione,"Note":note,"Inserito":datetime.now().strftime("%d/%m/%Y %H:%M")})
    st.success(f"{icona_sel} Salvato {via_civico}, {comune}! Icona associata")
   else:
    st.error("Compila Comune, Via, Azione, Responsabile *")
 
 st.divider()
 with st.expander("➕ Aggiungi Comune o Via alla Combo"):
  c1,c2=st.columns(2)
  with c1:
   nuovo_com=st.text_input("Nuovo Comune per combo")
   if st.button("Aggiungi Comune alla combo"):
    if nuovo_com and nuovo_com not in LISTA_COMUNI:
     LISTA_COMUNI.append(nuovo_com)
     LISTA_COMUNI.sort()
     st.success(f"Comune {nuovo_com} aggiunto!")
  with c2:
   com_per_via=st.selectbox("Comune per nuova via", options=LISTA_COMUNI, key="com_via_add")
   nuova_via=st.text_input("Nuova Via per comune")
   if st.button("Aggiungi Via agganciata a comune"):
    if nuova_via and com_per_via:
     if com_per_via not in VIE_PER_COMUNE:
      VIE_PER_COMUNE[com_per_via]=[]
     VIE_PER_COMUNE[com_per_via].append(nuova_via)
     st.success(f"Via {nuova_via} aggiunta a {com_per_via}!")

 tabella_import_export("Interventi Emergenza - Con Icone Libreria + Comuni + Vie", st.session_state.interventi_lista)
 dash_btn("int")

elif scelta=="📅 Gestione Eventi":
 st.markdown(LOGHI, unsafe_allow_html=True)
 with st.form("ev_form", clear_on_submit=True):
  c1,c2=st.columns(2)
  with c1:
   tipo=st.selectbox("Tipo Evento *", ["Monitoraggio","Antincendio","Alluvione","Esercitazione","Supporto","Altro"])
   desc=st.text_area("Descrizione *", height=80)
   comune=st.selectbox("Comune * - Combo Comuni Italia", options=LISTA_COMUNI, index=LISTA_COMUNI.index("Varese") if "Varese" in LISTA_COMUNI else 0)
  with c2:
   d_ini=st.date_input("Data Inizio *")
   o_ini=st.time_input("Ora Inizio *")
   resp=st.text_input("Responsabile *")
   cell=st.text_input("Cellulare")
  if st.form_submit_button("🔴 SALVA EVENTO", use_container_width=True, type="primary"):
   if desc and comune and resp:
    st.session_state.eventi.append({"Logo Default":"VOLONTARIATO Varese","Tipo":tipo,"Descrizione":desc,"Comune":comune,"Data":str(d_ini),"Ora":str(o_ini),"Responsabile":resp,"Cell":cell})
    st.success("Evento salvato!")
 tabella_import_export("Eventi", st.session_state.eventi)
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
   comune=st.selectbox("Comune", options=LISTA_COMUNI, index=LISTA_COMUNI.index("Varese") if "Varese" in LISTA_COMUNI else 0)
   ruolo=st.selectbox("Ruolo", ["Volontario","Capo Squadra","Coordinatore"])
  if st.form_submit_button("🔴 SALVA VOLONTARIO", use_container_width=True, type="primary"):
   if nome and cognome and cell:
    nf=f"{nome} {cognome}"
    if nf not in st.session_state.mem_nomi:
     st.session_state.mem_nomi.append(nf)
    st.session_state.volontari_full.append({"Logo Default":"VOLONTARIATO Varese","Nome":nome,"Cognome":cognome,"Nome Completo":nf,"Cell":cell,"Comune":comune,"Ruolo":ruolo})
    st.success(f"Salvato {nf}!")
 tabella_import_export("Volontari", st.session_state.volontari_full)
 dash_btn("vol")

elif scelta in ["📻 DB Radio Inventario","📦 Distribuzione Radio","🗺️ Mappa Postazioni","📝 Brogliaccio ODV","📝 Registro Radio","✅ Check-In Volontari"]:
 st.markdown(LOGHI, unsafe_allow_html=True)
 st.info(f"Modulo {scelta} - Con tabella sotto + Import/Export Excel CSV + Logo Default + Comuni Combo")
 if scelta=="📻 DB Radio Inventario":
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
     st.session_state.radio_db.append({"Logo Default":"VOLONTARIATO Varese","ID":id_r,"Modello":modello,"Stato":stato,"Note":note})
     st.success("Radio salvata!")
  tabella_import_export("Radio Inventario", st.session_state.radio_db)
 elif scelta=="📦 Distribuzione Radio":
  with st.form("dist_form", clear_on_submit=True):
   radio=st.selectbox("Radio", [r["ID"] for r in st.session_state.radio_db] if st.session_state.radio_db else ["RAD-001"])
   vol=st.selectbox("Volontario", st.session_state.mem_nomi)
   if st.form_submit_button("🔴 CONSEGNA RADIO", use_container_width=True, type="primary"):
    st.session_state.dist_radio.append({"Logo Default":"VOLONTARIATO Varese","Radio":radio,"Volontario":vol,"Data":str(date.today())})
    st.success("Consegnata!")
  tabella_import_export("Distribuzione Radio", st.session_state.dist_radio)
 elif scelta=="🗺️ Mappa Postazioni":
  with st.form("post_form", clear_on_submit=True):
   nome=st.text_input("Nome Postazione *", placeholder="Postazione 1")
   comune=st.selectbox("Comune * - Combo", options=LISTA_COMUNI, index=LISTA_COMUNI.index("Varese") if "Varese" in LISTA_COMUNI else 0)
   via_list=VIE_PER_COMUNE.get(comune, ["Via Roma","Via Milano"])
   via=st.selectbox(f"Via * - Vie di {comune}", options=via_list)
   if st.form_submit_button("🔴 SALVA POSTAZIONE", use_container_width=True, type="primary"):
    if nome and comune:
     st.session_state.postazioni.append({"Logo Default":"VOLONTARIATO Varese","Postazione":nome,"Comune":comune,"Via + Civico":via})
     st.success("Salvata!")
  tabella_import_export("Postazioni", st.session_state.postazioni)
 elif scelta=="📝 Brogliaccio ODV":
  with st.form("brog_form", clear_on_submit=True):
   comune=st.selectbox("Comune - Combo", options=LISTA_COMUNI, index=LISTA_COMUNI.index("Varese") if "Varese" in LISTA_COMUNI else 0)
   msg=st.text_area("Messaggio *", height=100)
   if st.form_submit_button("🔴 SALVA BROGLIACCIO", use_container_width=True, type="primary"):
    if msg:
     st.session_state.brogliaccio.append({"Logo Default":"VOLONTARIATO Varese","Comune":comune,"Data":str(date.today()),"Ora":str(datetime.now().strftime("%H:%M")),"Messaggio":msg})
     st.success("Salvato!")
  tabella_import_export("Brogliaccio ODV", st.session_state.brogliaccio)
 elif scelta=="📝 Registro Radio":
  with st.form("reg_form", clear_on_submit=True):
   radio=st.selectbox("Radio", [r["ID"] for r in st.session_state.radio_db] if st.session_state.radio_db else ["RAD-001"])
   vol=st.selectbox("Volontario", st.session_state.mem_nomi)
   note=st.text_input("Note")
   if st.form_submit_button("🔴 SALVA REGISTRO", use_container_width=True, type="primary"):
    st.session_state.registro_radio.append({"Logo Default":"VOLONTARIATO Varese","Radio":radio,"Volontario":vol,"Note":note,"Data":str(date.today())})
    st.success("Salvato!")
  tabella_import_export("Registro Radio", st.session_state.registro_radio)
 elif scelta=="✅ Check-In Volontari":
  if not st.session_state.eventi:
   st.warning("Crea prima un evento")
  else:
   ids=[f"{i} - {e['Comune']}" for i,e in enumerate(st.session_state.eventi)]
   sel=st.selectbox("Evento *", ids)
   idx=int(sel.split(" - ")[0])
   vol=st.selectbox("Volontario *", st.session_state.mem_nomi)
   if st.button("🔴 CHECK-IN", use_container_width=True, type="primary"):
    if idx not in st.session_state.checkin:
     st.session_state.checkin[idx]=[]
    st.session_state.checkin[idx].append({"Logo Default":"VOLONTARIATO Varese","Volontario":vol,"Ora":datetime.now().strftime("%H:%M"),"Data":str(date.today())})
    st.success("Check-In fatto!")
   if idx in st.session_state.checkin and st.session_state.checkin[idx]:
    st.dataframe(pd.DataFrame(st.session_state.checkin[idx]), use_container_width=True, height=300)
 dash_btn("other")

elif scelta=="💾 Backup Export/Import":
 st.markdown(LOGHI, unsafe_allow_html=True)
 st.markdown("#### 💾 Backup - Import/Export Excel e CSV per ogni form - 12 Form - Logo Default + Icone Libreria + Comuni")
 dati={"🚨 Interventi":st.session_state.interventi_lista,"📅 Eventi":st.session_state.eventi,"👥 Volontari":st.session_state.volontari_full,"📻 Radio":st.session_state.radio_db,"📦 Distribuzione":st.session_state.dist_radio,"🗺️ Postazioni":st.session_state.postazioni,"📝 Brogliaccio":st.session_state.brogliaccio,"📝 Registro":st.session_state.registro_radio}
 for k,v in dati.items():
  st.write(f"{k}: {len(v)} record")
 sel=st.multiselect("Scegli Form da Esportare", list(dati.keys()), default=["🚨 Interventi"] if dati["🚨 Interventi"] else [])
 fmt=st.radio("Formato Export", ["CSV","Excel","PDF A4 Orizzontale con Logo Default"])
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
    else:
     pdf=pdf_a4(nome, df)
     if pdf:
      st.download_button(f"📄 PDF A4 {nome}", pdf.getvalue(), f"{nome[:10]}_A4.pdf", "application/pdf", use_container_width=True, key=f"pdf_{nome}")
 dash_btn("backup")

elif scelta=="🔗 Link & Icona PWA":
 st.markdown(LOGHI, unsafe_allow_html=True)
 st.markdown("""<div style='background:#c8e6c9; padding:12px; border-radius:10px; border:2px solid #2e7d32;'><b>📱 Icona PWA - Logo Default Volontariato + Icone Libreria + Comuni Combo:</b><br>1. Apri link app su telefono/pc<br>2. Android: Menu ⋮ → Aggiungi a Home → Icona Volontariato<br>3. PC: Chrome Menu ⋮ → Salva e condividi → Crea collegamento → Apri come finestra<br>4. Icona con logo Volontariato + libreria icone da PC + comuni Italia combo + vie combo</div>""", unsafe_allow_html=True)
 url=st.text_input("URL App", placeholder="https://ana-varese.streamlit.app")
 if url:
  st.link_button("📱 Condividi su WhatsApp", f"https://wa.me/?text=Installa icona ANA Varese: {url}", use_container_width=True)
 dash_btn("link")

st.caption("ANA Varese - 12 Form - Logo Default VOLONTARIATO - Libreria Icone da PC + Icona Associata + Comuni Italia Combo + Vie Combo Agganciate a Comune + Import/Export Excel CSV per ogni form + Tabella sotto ogni form - Icona PC e Mobile")
