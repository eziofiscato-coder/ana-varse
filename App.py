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

st.set_page_config(page_title="ANA Varese - Dashboard + Mappa Fix", page_icon="🟢", layout="wide")

for k,v in [("authenticated",False),("dashboard_entered",False),("interventi_lista",[]),("eventi",[]),("mem_nomi",["Mario Rossi","Luigi Bianchi","Giuseppe Verdi"]),("radio_db",[]),("dist_radio",[]),("postazioni",[]),("brogliaccio",[]),("registro_radio",[]),("volontari_full",[]),("checkin",{}),("icone_personalizzate",[]),("menu_scelta","🏠 Dashboard")]:
 if k not in st.session_state:
  st.session_state[k]=v

ICONE={"🔥 Incendio Boschivo":"🔥","🌊 Alluvione":"🌊","❄️ Neve":"❄️","⛰️ Frana":"⛰️","🔍 Ricerca Persona":"🔍","👥 Supporto Popolazione":"👥","👁️ Monitoraggio":"👁️","🚧 Presidio":"🚧","🚑 Sanitario":"🚑","🏚️ Crollo":"🏚️","🌲 Antincendio":"🌲","⚡ Blackout":"⚡","🦺 Esercitazione":"🦺","🎪 Manifestazione":"🎪","🚨 Altro":"🚨"}
LIB_ICONE=[{"nome":k,"icona":v} for k,v in ICONE.items()]

try:
 df_com=pd.read_csv("comuni_italiani.csv")
 LISTA_COMUNI=sorted(df_com["Comune"].astype(str).unique().tolist())
except:
 try:
  df_com=pd.read_csv("/mnt/data/comuni_italiani.csv")
  LISTA_COMUNI=sorted(df_com["Comune"].astype(str).unique().tolist())
 except:
  LISTA_COMUNI=["Varese","Busto Arsizio","Gallarate","Saronno","Venegono Superiore","Venegono Inferiore","Milano","Como","Varese"]

try:
 df_vie=pd.read_csv("vie_per_comune.csv")
 VIE_PER_COMUNE={}
 for c in df_vie["Comune"].unique():
  VIE_PER_COMUNE[c]=df_vie[df_vie["Comune"]==c]["Via"].astype(str).unique().tolist()
except:
 VIE_PER_COMUNE={"Varese":["Via Roma","Via Milano","Via Garibaldi","Via Verdi","Via Manzoni","Via Cavour"]}

def get_b64(p):
 try:
  if os.path.exists(p):
   with open(p,"rb") as f:
    return base64.b64encode(f.read()).decode()
 except:
  pass
 return ""

b64_vol=get_b64("logo_volontariato_varese.jpg") or get_b64("/mnt/data/Circular_Volontariato_Emblem")
b64_ana=get_b64("logo_ana_varese.jpg") or get_b64("/mnt/data/Green_Alpini_Emblem")
b64_pc=get_b64("logo_protezione_civile_lombardia.jpg") or get_b64("/mnt/data/Protezione_Civile_Lombardia_Emblem")

if b64_vol and b64_ana and b64_pc:
 LOGHI=f"""<div style='display:flex; justify-content:center; align-items:center; gap:15px; background:#a5d6a7; padding:12px; border-radius:15px; border:3px solid #2e7d32; margin-bottom:12px; flex-wrap:wrap;'>
  <div style='text-align:center;'><img src='data:image/jpeg;base64,{b64_vol}' style='width:90px; height:90px; border-radius:50%; border:3px solid #1b5e20; background:white;'><br><small style='color:#1b5e20; font-weight:bold; font-size:9px;'>VOLONTARIATO<br>Sezione VARESE</small></div>
  <div style='text-align:center;'><img src='data:image/jpeg;base64,{b64_ana}' style='width:100px; height:100px; border-radius:50%; border:4px solid #1b5e20; background:white;'><br><small style='color:#1b5e20; font-weight:bold; font-size:9px;'>ANA<br>Sezione VARESE</small></div>
  <div style='text-align:center;'><img src='data:image/jpeg;base64,{b64_pc}' style='width:90px; height:90px; border-radius:50%; border:3px solid #2e7d32; background:white;'><br><small style='color:#1b5e20; font-weight:bold; font-size:9px;'>PROTEZIONE CIVILE<br>Regione Lombardia</small></div>
  <div style='text-align:center; flex:1; min-width:200px;'><h3 style='color:#1b5e20; margin:0;'>ANA Varese - Protezione Civile</h3></div>
</div>"""
else:
 LOGHI="<div style='background:#a5d6a7; padding:12px; border-radius:12px; border:3px solid #2e7d32; text-align:center;'><h3 style='color:#1b5e20; margin:0;'>ANA Varese - Protezione Civile</h3></div>"

st.markdown("""<style>
.stApp{background:#e8f5e9!important;}
.main .block-container{max-width:100%!important; padding:1% 2%!important;}
[data-testid="stSidebar"]{background:#a5d6a7!important; border-right:3px solid #2e7d32!important;}
.stForm{background:#a5d6a7!important; border:3px solid #2e7d32!important; border-radius:15px!important; padding:15px!important;}
.stButton>button{background:#d32f2f!important; color:white!important; border:3px solid #b71c1c!important; font-weight:bold!important; border-radius:10px!important;}
div[data-testid="stFormSubmitButton"]>button{background:#d32f2f!important; color:white!important;}
</style>""", unsafe_allow_html=True)

def pdf_a4(titolo, df):
 if not HAS or df is None or df.empty:
  return None
 buf=BytesIO()
 from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
 doc=SimpleDocTemplate(buf, pagesize=landscape(A4))
 styles=getSampleStyleSheet()
 story=[Paragraph(f"<b>{titolo}</b>", styles['Heading1']), Spacer(1,0.2*cm)]
 d=df.copy().astype(str)
 data=[d.columns.tolist()]+d.values.tolist()
 table=Table(data, repeatRows=1)
 table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#2e7d32')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('GRID',(0,0),(-1,-1),0.5,colors.HexColor('#81c784'))]))
 story.append(table)
 doc.build(story)
 buf.seek(0)
 return buf

def tabella_import_export(nome, lista):
 st.divider()
 st.markdown(f"### 📋 {nome}")
 if lista:
  df=pd.DataFrame(lista)
  st.dataframe(df, use_container_width=True, height=320)
  c1,c2,c3,c4=st.columns(4)
  with c1:
   st.download_button("📥 CSV", df.to_csv(index=False).encode('utf-8'), f"{nome}.csv", "text/csv", use_container_width=True, key=f"exp_csv_{nome}")
  with c2:
   out=BytesIO()
   with pd.ExcelWriter(out, engine='openpyxl') as writer:
    df.to_excel(writer, index=False)
   st.download_button("📊 Excel", out.getvalue(), f"{nome}.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True, key=f"exp_xls_{nome}")
  with c3:
   pdf=pdf_a4(nome, df)
   if pdf:
    st.download_button("📄 PDF", pdf.getvalue(), f"{nome}_A4.pdf", "application/pdf", use_container_width=True, key=f"exp_pdf_{nome}")
  with c4:
   if st.button("🗑️ Cancella", key=f"del_{nome}", use_container_width=True):
    lista.clear()
    st.rerun()
 else:
  st.info(f"Nessun dato in {nome}")

# LOGIN
if not st.session_state.authenticated:
 st.markdown(LOGHI, unsafe_allow_html=True)
 st.markdown("<h2 style='text-align:center; color:#1b5e20; background:#a5d6a7; padding:10px; border-radius:12px;'>🔐 Accesso Riservato</h2>", unsafe_allow_html=True)
 c1,c2,c3=st.columns([1,2,1])
 with c2:
  with st.form("login"):
   pwd=st.text_input("Password", type="password")
   if st.form_submit_button("🔴 ACCEDI", use_container_width=True, type="primary"):
    if pwd=="ANA2025":
     st.session_state.authenticated=True
     st.rerun()
    else:
     st.error("Password errata")
 st.stop()

if not st.session_state.dashboard_entered:
 st.markdown(LOGHI, unsafe_allow_html=True)
 st.markdown("<h2 style='text-align:center; color:#1b5e20; background:#a5d6a7; padding:12px; border-radius:15px;'>🟢 ANA Varese - Protezione Civile</h2>", unsafe_allow_html=True)
 c1,c2,c3=st.columns([1,2,1])
 with c2:
  if st.button("🚀 ENTRA DASHBOARD", use_container_width=True, type="primary"):
   st.session_state.dashboard_entered=True
   st.rerun()
  if st.button("🔒 Logout", use_container_width=True):
   st.session_state.authenticated=False
   st.rerun()
 st.stop()

# SIDEBAR
with st.sidebar:
 st.markdown(LOGHI, unsafe_allow_html=True)
 scelta=st.radio("MENU", ["🏠 Dashboard","📅 Gestione Eventi","✅ Check-In Volontari","👥 Volontari - Anagrafica","📻 DB Radio Inventario","📦 Distribuzione Radio","🗺️ Mappa Postazioni","🚨 Interventi Emergenza","📝 Brogliaccio ODV","📝 Registro Radio","💾 Backup Export/Import","🔗 Link & Icona PWA"], index=["🏠 Dashboard","📅 Gestione Eventi","✅ Check-In Volontari","👥 Volontari - Anagrafica","📻 DB Radio Inventario","📦 Distribuzione Radio","🗺️ Mappa Postazioni","🚨 Interventi Emergenza","📝 Brogliaccio ODV","📝 Registro Radio","💾 Backup Export/Import","🔗 Link & Icona PWA"].index(st.session_state.menu_scelta) if st.session_state.menu_scelta in ["🏠 Dashboard","📅 Gestione Eventi","✅ Check-In Volontari","👥 Volontari - Anagrafica","📻 DB Radio Inventario","📦 Distribuzione Radio","🗺️ Mappa Postazioni","🚨 Interventi Emergenza","📝 Brogliaccio ODV","📝 Registro Radio","💾 Backup Export/Import","🔗 Link & Icona PWA"] else 0, key="menu_scelta_radio")
 st.session_state.menu_scelta=scelta
 if st.button("🏠 Home", use_container_width=True):
  st.session_state.dashboard_entered=False
  st.rerun()
 if st.button("🔒 Logout", use_container_width=True):
  st.session_state.authenticated=False
  st.session_state.dashboard_entered=False
  st.rerun()

st.markdown(f"<h2 style='color:#1b5e20; background:#a5d6a7; padding:10px; border-radius:12px; border:3px solid #2e7d32;'>🟢 {st.session_state.menu_scelta} - 3 Loghi</h2>", unsafe_allow_html=True)
scelta=st.session_state.menu_scelta

def dash_btn(k):
 c1,c2=st.columns(2)
 with c1:
  if st.button("🏠 Dashboard", key=f"d_{k}", use_container_width=True):
   st.session_state.menu_scelta="🏠 Dashboard"
   st.rerun()
 with c2:
  if st.button("🏠 Home", key=f"h_{k}", use_container_width=True):
   st.session_state.dashboard_entered=False
   st.rerun()

# DASHBOARD CON TASTI MENU VELOCE - NUOVO
if scelta=="🏠 Dashboard":
 st.markdown(LOGHI, unsafe_allow_html=True)
 c1,c2,c3,c4=st.columns(4)
 c1.metric("Interventi", len(st.session_state.interventi_lista))
 c2.metric("Eventi", len(st.session_state.eventi))
 c3.metric("Volontari", len(st.session_state.mem_nomi))
 c4.metric("Radio", len(st.session_state.radio_db))
 
 st.markdown("### ⚡ MENU VELOCE - Clicca per aprire subito")
 st.info("Tasti rapidi per accedere ai form senza passare dal menu laterale")
 
 # RIGA 1 - 4 tasti grandi
 r1c1,r1c2,r1c3,r1c4=st.columns(4)
 with r1c1:
  if st.button("🚨\nInterventi\nEmergenza", key="quick_int", use_container_width=True, type="primary"):
   st.session_state.menu_scelta="🚨 Interventi Emergenza"
   st.rerun()
 with r1c2:
  if st.button("🗺️\nMappa\nPostazioni", key="quick_mappa", use_container_width=True, type="primary"):
   st.session_state.menu_scelta="🗺️ Mappa Postazioni"
   st.rerun()
 with r1c3:
  if st.button("📅\nGestione\nEventi", key="quick_eventi", use_container_width=True):
   st.session_state.menu_scelta="📅 Gestione Eventi"
   st.rerun()
 with r1c4:
  if st.button("✅\nCheck-In\nVolontari", key="quick_checkin", use_container_width=True):
   st.session_state.menu_scelta="✅ Check-In Volontari"
   st.rerun()
 
 # RIGA 2
 r2c1,r2c2,r2c3,r2c4=st.columns(4)
 with r2c1:
  if st.button("👥\nVolontari\nAnagrafica", key="quick_vol", use_container_width=True):
   st.session_state.menu_scelta="👥 Volontari - Anagrafica"
   st.rerun()
 with r2c2:
  if st.button("📻\nDB Radio\nInventario", key="quick_radio", use_container_width=True):
   st.session_state.menu_scelta="📻 DB Radio Inventario"
   st.rerun()
 with r2c3:
  if st.button("📦\nDistribuzione\nRadio", key="quick_dist", use_container_width=True):
   st.session_state.menu_scelta="📦 Distribuzione Radio"
   st.rerun()
 with r2c4:
  if st.button("📝\nBrogliaccio\nODV", key="quick_brog", use_container_width=True):
   st.session_state.menu_scelta="📝 Brogliaccio ODV"
   st.rerun()
 
 # RIGA 3
 r3c1,r3c2,r3c3,r3c4=st.columns(4)
 with r3c1:
  if st.button("📝\nRegistro\nRadio", key="quick_reg", use_container_width=True):
   st.session_state.menu_scelta="📝 Registro Radio"
   st.rerun()
 with r3c2:
  if st.button("💾\nBackup\nExport", key="quick_backup", use_container_width=True):
   st.session_state.menu_scelta="💾 Backup Export/Import"
   st.rerun()
 with r3c3:
  if st.button("🔗\nLink & Icona\nPWA", key="quick_link", use_container_width=True):
   st.session_state.menu_scelta="🔗 Link & Icona PWA"
   st.rerun()
 with r3c4:
  if st.button("🔄\nAggiorna\nDashboard", key="quick_refresh", use_container_width=True):
   st.rerun()

 st.divider()
 if st.session_state.interventi_lista:
  st.markdown("#### Ultimi 5 interventi")
  st.dataframe(pd.DataFrame(st.session_state.interventi_lista).tail(5), use_container_width=True)

# MAPPA POSTAZIONI CON OPENSTREETMAP + GOOGLE MAPS - FIX
elif scelta=="🗺️ Mappa Postazioni":
 st.markdown(LOGHI, unsafe_allow_html=True)
 st.markdown("### 🗺️ Mappa Postazioni - OpenStreetMap + Google Maps")
 
 with st.form("post_form", clear_on_submit=True):
  c1,c2=st.columns(2)
  with c1:
   nome=st.text_input("Nome Postazione *", placeholder="Postazione 1 - Piazza")
   comune=st.selectbox("Comune * - COMBO", options=LISTA_COMUNI, index=LISTA_COMUNI.index("Varese") if "Varese" in LISTA_COMUNI else 0)
   via_list=VIE_PER_COMUNE.get(comune, ["Via Roma","Via Milano"])
   via=st.selectbox(f"Via * - Vie di {comune}", options=via_list)
  with c2:
   civ=st.text_input("Civico", placeholder="15")
   lat=st.text_input("Latitudine *", placeholder="45.8205 - es. 45.8205")
   lon=st.text_input("Longitudine *", placeholder="8.8255 - es. 8.8255")
   resp=st.text_input("Responsabile")
  if st.form_submit_button("🔴 SALVA POSTAZIONE", use_container_width=True, type="primary"):
   if nome and comune and lat and lon:
    try:
     float(lat); float(lon)
     st.session_state.postazioni.append({"Postazione":nome,"Comune":comune,"Via":via,"Civico":civ,"Latitudine":lat,"Longitudine":lon,"Responsabile":resp,"Data":str(date.today())})
     st.success(f"Salvata {nome}!")
    except:
     st.error("Latitudine e Longitudine devono essere numeri es: 45.8205 e 8.8255")
   else:
    st.error("Compila Nome, Comune, Latitudine, Longitudine *")

 # MAPPA VISUALIZZAZIONE
 if st.session_state.postazioni:
  df_post=pd.DataFrame(st.session_state.postazioni)
  st.markdown(f"#### 📍 {len(df_post)} Postazioni salvate - Mappa")
  
  # Prepara dati per st.map (OpenStreetMap)
  try:
   df_map=df_post.copy()
   df_map["lat"]=pd.to_numeric(df_map["Latitudine"], errors='coerce')
   df_map["lon"]=pd.to_numeric(df_map["Longitudine"], errors='coerce')
   df_map=df_map.dropna(subset=["lat","lon"])
   if not df_map.empty:
    st.markdown("**🗺️ OpenStreetMap - Mappa interattiva**")
    st.map(df_map[["lat","lon"]], zoom=11, use_container_width=True)
   else:
    st.warning("Nessuna coordinata valida per mappa")
  except Exception as e:
   st.error(f"Errore mappa: {e}")

  # GOOGLE MAPS LINKS per ogni postazione
  st.markdown("#### 🌐 Link Google Maps + OpenStreetMap per ogni postazione")
  for idx, row in df_post.iterrows():
   try:
    lat=row.get("Latitudine",""); lon=row.get("Longitudine","")
    nome=row.get("Postazione","")
    comune=row.get("Comune","")
    via=row.get("Via","")
    st.markdown(f"**{nome} - {comune} {via}** - Lat: {lat} Lon: {lon}")
    c1,c2,c3,c4=st.columns(4)
    with c1:
     st.link_button("🔍 Google Maps", f"https://www.google.com/maps/search/?api=1&query={lat},{lon}", use_container_width=True)
    with c2:
     st.link_button("🧭 Naviga Google", f"https://www.google.com/maps/dir/?api=1&destination={lat},{lon}", use_container_width=True)
    with c3:
     st.link_button("🗺️ OpenStreetMap", f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=16/{lat}/{lon}", use_container_width=True)
    with c4:
     st.link_button("🚗 Waze", f"https://waze.com/ul?ll={lat},{lon}&navigate=yes", use_container_width=True)
   except:
    pass
  
  tabella_import_export("Postazioni", st.session_state.postazioni)
 else:
  st.info("📭 Nessuna postazione - Aggiungi la prima sopra!")
  # Mappa di esempio Varese
  st.markdown("#### 🗺️ Mappa di esempio - Varese")
  df_example=pd.DataFrame([{"lat":45.8205,"lon":8.8255}])
  st.map(df_example, zoom=12)
  st.link_button("🔍 Apri Varese su Google Maps", "https://www.google.com/maps/search/?api=1&query=45.8205,8.8255", use_container_width=True)

# ALTRI FORM SEMPLIFICATI
elif scelta=="🚨 Interventi Emergenza":
 st.markdown(LOGHI, unsafe_allow_html=True)
 with st.expander("🎨 Libreria icone", expanded=False):
  ups=st.file_uploader("Carica icone da PC", type=["png","jpg","jpeg","ico"], accept_multiple_files=True, key="up_icone")
  if ups:
   for up in ups:
    st.session_state.icone_personalizzate.append({"nome":up.name.split(".")[0],"icona":"🖼️"})
   st.success(f"Caricate {len(ups)} icone")

 with st.form("form_int", clear_on_submit=True):
  c1,c2=st.columns(2)
  with c1:
   data_int=st.date_input("Data", value=date.today())
   ora_int=st.time_input("Ora")
   comune=st.selectbox("Comune", options=LISTA_COMUNI, index=LISTA_COMUNI.index("Varese") if "Varese" in LISTA_COMUNI else 0)
   vie_list=VIE_PER_COMUNE.get(comune, ["Via Roma","Via Milano"])
   via_sel=st.selectbox("Via", options=vie_list)
   civ=st.text_input("Civico", placeholder="15")
   via_civico=f"{via_sel} {civ}".strip()
   lat=st.text_input("Lat", placeholder="45.8205")
   lon=st.text_input("Lon", placeholder="8.8255")
  with c2:
   tutte_icone=LIB_ICONE+st.session_state.icone_personalizzate
   opts=[f"{ic.get('icona','🔹')} {ic.get('nome','')}" for ic in tutte_icone]
   tipo=st.selectbox("Tipo", options=opts)
   icona_sel=tipo.split(" ")[0] if tipo else "🚨"
   nome_tipo=" ".join(tipo.split(" ")[1:]) if len(tipo.split(" "))>1 else tipo
   priorita=st.selectbox("Priorità", ["Bassa","Media","Alta","Critica"])
   odv=st.selectbox("ODV", ["ANA Varese","PC Lombardia","Croce Rossa","VVF","Altro"])
   resp=st.text_input("Responsabile *")
  azione=st.text_area("Azione *", height=80)
  if st.form_submit_button("🔴 SALVA INTERVENTO", use_container_width=True, type="primary"):
   if comune and via_civico and azione and resp:
    st.session_state.interventi_lista.append({"ID":len(st.session_state.interventi_lista)+1,"Data":str(data_int),"Ora":str(ora_int),"Comune":comune,"Via":via_civico,"Tipo":nome_tipo,"Icona":icona_sel,"Priorità":priorita,"ODV":odv,"Responsabile":resp,"Lat":lat,"Lon":lon,"Azione":azione})
    st.success(f"Salvato {via_civico}, {comune}")
   else:
    st.error("Compila campi *")
  # Link mappa se lat/lon presenti
  if st.session_state.interventi_lista:
   ultimo=st.session_state.interventi_lista[-1]
   if ultimo.get("Lat") and ultimo.get("Lon"):
    lat_u=ultimo["Lat"]; lon_u=ultimo["Lon"]
    c1,c2=st.columns(2)
    with c1:
     st.link_button("🗺️ Vedi su OpenStreetMap", f"https://www.openstreetmap.org/?mlat={lat_u}&mlon={lon_u}#map=16/{lat_u}/{lon_u}", use_container_width=True)
    with c2:
     st.link_button("🔍 Vedi su Google Maps", f"https://www.google.com/maps/search/?api=1&query={lat_u},{lon_u}", use_container_width=True)
 tabella_import_export("Interventi", st.session_state.interventi_lista)

elif scelta=="📅 Gestione Eventi":
 st.markdown(LOGHI, unsafe_allow_html=True)
 with st.form("ev_form", clear_on_submit=True):
  titolo=st.text_input("Titolo *")
  comune=st.selectbox("Comune", options=LISTA_COMUNI)
  data_ev=st.date_input("Data", value=date.today())
  if st.form_submit_button("🔴 SALVA", use_container_width=True, type="primary"):
   if titolo:
    st.session_state.eventi.append({"Titolo":titolo,"Comune":comune,"Data":str(data_ev)})
    st.success("Salvato")
 tabella_import_export("Eventi", st.session_state.eventi)

elif scelta=="👥 Volontari - Anagrafica":
 st.markdown(LOGHI, unsafe_allow_html=True)
 with st.form("vol_form", clear_on_submit=True):
  nome=st.text_input("Nome *")
  cell=st.text_input("Cellulare")
  if st.form_submit_button("🔴 SALVA", use_container_width=True, type="primary"):
   if nome:
    st.session_state.mem_nomi.append(nome)
    st.session_state.volontari_full.append({"Nome":nome,"Cell":cell})
    st.success(f"Aggiunto {nome}")
 tabella_import_export("Volontari", st.session_state.volontari_full)

elif scelta=="📻 DB Radio Inventario":
 st.markdown(LOGHI, unsafe_allow_html=True)
 with st.form("radio_form", clear_on_submit=True):
  id_r=st.text_input("ID Radio *")
  modello=st.text_input("Modello")
  if st.form_submit_button("🔴 SALVA", use_container_width=True, type="primary"):
   if id_r:
    st.session_state.radio_db.append({"ID":id_r,"Modello":modello})
    st.success("Salvata")
 tabella_import_export("Radio", st.session_state.radio_db)

elif scelta=="📦 Distribuzione Radio":
 st.markdown(LOGHI, unsafe_allow_html=True)
 with st.form("dist_form", clear_on_submit=True):
  radio=st.selectbox("Radio", [r["ID"] for r in st.session_state.radio_db] if st.session_state.radio_db else ["RAD-001"])
  vol=st.selectbox("Volontario", st.session_state.mem_nomi)
  if st.form_submit_button("🔴 CONSEGNA", use_container_width=True, type="primary"):
   st.session_state.dist_radio.append({"Radio":radio,"Volontario":vol,"Data":str(date.today())})
   st.success("Consegnata")
 tabella_import_export("Distribuzione", st.session_state.dist_radio)

elif scelta=="📝 Brogliaccio ODV":
 st.markdown(LOGHI, unsafe_allow_html=True)
 with st.form("brog_form", clear_on_submit=True):
  comune=st.selectbox("Comune", options=LISTA_COMUNI)
  msg=st.text_area("Messaggio *", height=100)
  if st.form_submit_button("🔴 SALVA", use_container_width=True, type="primary"):
   if msg:
    st.session_state.brogliaccio.append({"Comune":comune,"Data":str(date.today()),"Messaggio":msg})
    st.success("Salvato")
 tabella_import_export("Brogliaccio", st.session_state.brogliaccio)

elif scelta=="📝 Registro Radio":
 st.markdown(LOGHI, unsafe_allow_html=True)
 with st.form("reg_form", clear_on_submit=True):
  radio=st.selectbox("Radio", [r["ID"] for r in st.session_state.radio_db] if st.session_state.radio_db else ["RAD-001"])
  vol=st.selectbox("Volontario", st.session_state.mem_nomi)
  note=st.text_input("Note")
  if st.form_submit_button("🔴 SALVA", use_container_width=True, type="primary"):
   st.session_state.registro_radio.append({"Radio":radio,"Volontario":vol,"Note":note,"Data":str(date.today())})
   st.success("Salvato")
 tabella_import_export("Registro", st.session_state.registro_radio)

elif scelta=="✅ Check-In Volontari":
 st.markdown(LOGHI, unsafe_allow_html=True)
 if not st.session_state.eventi:
  st.warning("Crea prima un evento")
 else:
  ids=[f"{i} - {e['Comune']}" for i,e in enumerate(st.session_state.eventi)]
  sel=st.selectbox("Evento", ids)
  idx=int(sel.split(" - ")[0])
  vol=st.selectbox("Volontario", st.session_state.mem_nomi)
  if st.button("🔴 CHECK-IN", use_container_width=True, type="primary"):
   if idx not in st.session_state.checkin:
    st.session_state.checkin[idx]=[]
   st.session_state.checkin[idx].append({"Volontario":vol,"Ora":datetime.now().strftime("%H:%M")})
   st.success("Check-In fatto")
  if idx in st.session_state.checkin:
   st.dataframe(pd.DataFrame(st.session_state.checkin[idx]), use_container_width=True)

elif scelta=="💾 Backup Export/Import":
 st.markdown(LOGHI, unsafe_allow_html=True)
 dati={"Interventi":st.session_state.interventi_lista,"Eventi":st.session_state.eventi,"Volontari":st.session_state.volontari_full,"Postazioni":st.session_state.postazioni}
 for k,v in dati.items():
  st.write(f"{k}: {len(v)} record")
  if v:
   st.download_button(f"CSV {k}", pd.DataFrame(v).to_csv(index=False).encode('utf-8'), f"{k}.csv", "text/csv", use_container_width=True, key=f"csv_{k}")

elif scelta=="🔗 Link & Icona PWA":
 st.markdown(LOGHI, unsafe_allow_html=True)
 url=st.text_input("URL App", placeholder="https://ana-varese.streamlit.app")
 if url:
  st.link_button("📱 Condividi WhatsApp", f"https://wa.me/?text=Installa ANA Varese: {url}", use_container_width=True)

st.caption("ANA Varese - Dashboard con tasti menu veloce + Mappa Postazioni OpenStreetMap + Google Maps")
