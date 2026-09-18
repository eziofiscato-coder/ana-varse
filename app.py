import streamlit as st
import pandas as pd
from datetime import datetime, date
from io import BytesIO
import base64, os, json, uuid

st.set_page_config(page_title="ANA Varese - Dashboard + Mappa", page_icon="🟢", layout="wide")

# Session init - COME IERI
for k,v in [("authenticated",False),("dashboard_entered",False),("interventi_lista",[]),("eventi",[]),("mem_nomi",["Mario Rossi","Luigi Bianchi","Giuseppe Verdi"]),("radio_db",[]),("dist_radio",[]),("postazioni",[]),("brogliaccio",[]),("registro_radio",[]),("volontari_full",[]),("checkin",{}),("icone_personalizzate",[]),("menu_scelta","🏠 Dashboard"),("dati",[]) ]:
 if k not in st.session_state:
  st.session_state[k]=v

ICONE={"🔥 Incendio Boschivo":"🔥","🌊 Alluvione":"🌊","❄️ Neve":"❄️","⛰️ Frana":"⛰️","🔍 Ricerca Persona":"🔍","👥 Supporto Popolazione":"👥","👁️ Monitoraggio":"👁️","🚧 Presidio":"🚧","🚑 Sanitario":"🚑","🏚️ Crollo":"🏚️","🌲 Antincendio":"🌲","⚡ Blackout":"⚡","🦺 Esercitazione":"🦺","🎪 Manifestazione":"🎪","🚨 Altro":"🚨","📍 Postazione":"📍","🏕️ Campo":"🏕️","🚒 VVF":"🚒"}
LIB_ICONE=[{"nome":k,"icona":v} for k,v in ICONE.items()]

try:
 df_com=pd.read_csv("comuni_italiani.csv")
 LISTA_COMUNI=sorted(df_com["Comune"].astype(str).unique().tolist())
except:
 try:
  df_com=pd.read_csv("/mnt/data/comuni_italiani.csv")
  LISTA_COMUNI=sorted(df_com["Comune"].astype(str).unique().tolist())
 except:
  LISTA_COMUNI=["Varese","Busto Arsizio","Gallarate","Saronno","Venegono Superiore","Venegono Inferiore","Milano","Como","Tradate","Malnate","Luino"]

def get_b64(p):
 try:
  if os.path.exists(p):
   with open(p,"rb") as f:
    return base64.b64encode(f.read()).decode()
 except:
  pass
 return ""

b64_vol=get_b64("logo_volontariato_varese.jpg") or get_b64("logo.png")
b64_ana=get_b64("logo_ana_varese.jpg") or get_b64("logo.png")
b64_pc=get_b64("logo_protezione_civile_lombardia.jpg") or get_b64("logo_pc_lombardia.png")

if b64_vol and b64_ana and b64_pc:
 LOGHI=f"""<div style='display:flex; justify-content:center; align-items:center; gap:25px; background:#a5d6a7; padding:15px; border-radius:15px; border:3px solid #2e7d32; margin-bottom:15px; flex-wrap:wrap;'>
  <img src='data:image/jpeg;base64,{b64_vol}' style='width:90px; height:90px; border-radius:50%; border:3px solid #1b5e20; background:white; object-fit:cover;'>
  <img src='data:image/jpeg;base64,{b64_ana}' style='width:100px; height:100px; border-radius:50%; border:4px solid #1b5e20; background:white; object-fit:cover;'>
  <img src='data:image/jpeg;base64,{b64_pc}' style='width:90px; height:90px; border-radius:50%; border:3px solid #2e7d32; background:white; object-fit:cover;'>
</div>"""
else:
 LOGHI="<div style='background:#a5d6a7; padding:12px; border-radius:12px; border:3px solid #2e7d32; text-align:center;'><h3 style='color:#1b5e20; margin:0;'>VOLONTARIATO Sezione di Varese</h3></div>"

st.markdown("""<style>
.stApp{background:#e8f5e9!important;}
.main.block-container{max-width:100%!important; padding:1% 2%!important;}
[data-testid="stSidebar"]{background:#a5d6a7!important; border-right:3px solid #2e7d32!important;}
.stForm{background:#a5d6a7!important; border:3px solid #2e7d32!important; border-radius:15px!important; padding:15px!important;}
.stButton>button{background:#d32f2f!important; color:white!important; border:3px solid #b71c1c!important; font-weight:bold!important; border-radius:10px!important; min-height:50px!important;}
.quick-btn>button{background:linear-gradient(135deg,#ff9800,#ef6c00)!important; min-height:90px!important; font-size:16px!important;}
.quick-btn-green>button{background:linear-gradient(135deg,#2e7d32,#1b5e20)!important; min-height:90px!important; font-size:16px!important;}
.quick-btn-red>button{background:linear-gradient(135deg,#c62828,#b71c1c)!important; min-height:90px!important;}
.quick-btn-blue>button{background:linear-gradient(135deg,#1565c0,#0d47a1)!important; min-height:90px!important;}
.vol-selected{background:#fff3e0!important; border:4px solid #ef6c00!important; border-radius:12px!important; padding:15px!important;}
.submask{background:#f1f8e9!important; border:3px solid #2e7d32!important; border-radius:12px!important; padding:15px!important;}
</style>""", unsafe_allow_html=True)

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
  with c4:
   if st.button("🗑️ Cancella", key=f"del_{nome}", use_container_width=True):
    lista.clear()
    st.rerun()
 else:
  st.info(f"Nessun dato in {nome}")

if not st.session_state.authenticated:
 st.markdown(LOGHI, unsafe_allow_html=True)
 c1,c2,c3=st.columns([1,2,1])
 with c2:
  with st.form("login"):
   pwd=st.text_input("Password", type="password")
   if st.form_submit_button("🔴 ACCEDI", use_container_width=True, type="primary"):
    if pwd=="ANA2025" or pwd=="ana2024" or pwd=="admin":
     st.session_state.authenticated=True
     st.rerun()
    else:
     st.error("Password errata")
 st.stop()

if not st.session_state.dashboard_entered:
 st.markdown(LOGHI, unsafe_allow_html=True)
 c1,c2,c3=st.columns([1,2,1])
 with c2:
  st.markdown("<h2 style='text-align:center; color:#0e7a3d;'>VOLONTARIATO<br>Sezione di Varese</h2>", unsafe_allow_html=True)
  if st.button("🏠 ENTRA IN DASHBOARD", use_container_width=True, type="primary"):
   st.session_state.dashboard_entered=True
   st.rerun()
 st.stop()

st.markdown(LOGHI, unsafe_allow_html=True)

with st.sidebar:
 st.markdown("### MENU ANA VARESE")
 opzioni=["🏠 Dashboard","🚨 Interventi Emergenza","📅 Gestione Eventi","👥 Volontari - Anagrafica","📻 DB Radio Inventario","📦 Distribuzione Radio","📝 Brogliaccio ODV","📝 Registro Radio","✅ Check-In Volontari","📍 Mappa Postazioni","💾 Backup Export/Import"]
 sel=st.radio("Seleziona", opzioni, index=opzioni.index(st.session_state.menu_scelta) if st.session_state.menu_scelta in opzioni else 0)
 if sel!= st.session_state.menu_scelta:
  st.session_state.menu_scelta=sel
  st.rerun()
 if st.button("🚪 LOGOUT", use_container_width=True):
  st.session_state.authenticated=False
  st.session_state.dashboard_entered=False
  st.rerun()

scelta=st.session_state.menu_scelta

# DASHBOARD CON MENU VELOCE COMPLETO
if scelta=="🏠 Dashboard":
 st.markdown("## 🏠 DASHBOARD - MENU VELOCE COMPLETO")
 st.markdown("### ⚡ TASTI MENU VELOCE - Clicca per andare subito!")
 c1,c2,c3,c4=st.columns(4)
 with c1:
  st.markdown('<div class="quick-btn-green">', unsafe_allow_html=True)
  if st.button("👥\nVOLONTARI\nAnagrafica", key="q_vol", use_container_width=True):
   st.session_state.menu_scelta="👥 Volontari - Anagrafica"
   st.rerun()
  st.markdown('</div>', unsafe_allow_html=True)
 with c2:
  st.markdown('<div class="quick-btn-red">', unsafe_allow_html=True)
  if st.button("🚨\nEMERGENZA\nIntervento", key="q_em", use_container_width=True):
   st.session_state.menu_scelta="🚨 Interventi Emergenza"
   st.rerun()
  st.markdown('</div>', unsafe_allow_html=True)
 with c3:
  st.markdown('<div class="quick-btn-blue">', unsafe_allow_html=True)
  if st.button("📍\nMAPPA\nPostazioni", key="q_map", use_container_width=True):
   st.session_state.menu_scelta="📍 Mappa Postazioni"
   st.rerun()
  st.markdown('</div>', unsafe_allow_html=True)
 with c4:
  st.markdown('<div class="quick-btn">', unsafe_allow_html=True)
  if st.button("📻\nRADIO\nInventario", key="q_radio", use_container_width=True):
   st.session_state.menu_scelta="📻 DB Radio Inventario"
   st.rerun()
  st.markdown('</div>', unsafe_allow_html=True)
 c5,c6,c7,c8=st.columns(4)
 with c5:
  if st.button("📅\nEVENTI\nGestione", key="q_ev", use_container_width=True):
   st.session_state.menu_scelta="📅 Gestione Eventi"
   st.rerun()
 with c6:
  if st.button("✅\nCHECK-IN\nVolontari", key="q_check", use_container_width=True):
   st.session_state.menu_scelta="✅ Check-In Volontari"
   st.rerun()
 with c7:
  if st.button("📝\nBROGLIACCIO\nODV", key="q_brog", use_container_width=True):
   st.session_state.menu_scelta="📝 Brogliaccio ODV"
   st.rerun()
 with c8:
  if st.button("💾\nBACKUP\nExport/Import", key="q_back", use_container_width=True):
   st.session_state.menu_scelta="💾 Backup Export/Import"
   st.rerun()

 st.divider()
 c1,c2,c3,c4=st.columns(4)
 c1.metric("🚨 Interventi", len(st.session_state.interventi_lista))
 c2.metric("📍 Postazioni", len(st.session_state.postazioni))
 c3.metric("👥 Volontari", len(st.session_state.dati))
 c4.metric("📻 Radio", len(st.session_state.radio_db))

# INTERVENTI EMERGENZA - CON MAPPE E POSIZIONAMENTO MANUALE
elif scelta=="🚨 Interventi Emergenza":
 st.markdown("## 🚨 INTERVENTI EMERGENZA - CON MAPPE")
 with st.form("int_form", clear_on_submit=False):
  c1,c2=st.columns(2)
  with c1:
   data_int=st.date_input("Data *", value=date.today())
   ora_int=st.time_input("Ora *")
   comune=st.selectbox("Comune *", options=LISTA_COMUNI)
   via_input=st.text_input("Via *", placeholder="Via Roma")
   civico=st.text_input("Civico", placeholder="10")
   via_civico=f"{via_input} {civico}".strip()
   st.markdown("#### 📍 Posizionamento Manuale")
   lat=st.text_input("Latitudine *", placeholder="45.8205")
   lon=st.text_input("Longitudine *", placeholder="8.8255")
  with c2:
   tutte_icone=LIB_ICONE+st.session_state.icone_personalizzate
   opts=[f"{ic.get('icona','🔹')} {ic.get('nome','')}" for ic in tutte_icone]
   tipo=st.selectbox("Tipo Intervento *", options=opts)
   icona_sel=tipo.split(" ")[0] if tipo else "🚨"
   nome_tipo=" ".join(tipo.split(" ")[1:]) if len(tipo.split(" "))>1 else tipo
   priorita=st.selectbox("Priorità", ["Bassa","Media","Alta","Critica"])
   odv=st.selectbox("ODV", ["ANA Varese","PC Lombardia","Croce Rossa","VVF","Altro"])
   resp=st.text_input("Responsabile *")
  azione=st.text_area("Azione *", height=80)
  if st.form_submit_button("🔴 SALVA INTERVENTO", use_container_width=True, type="primary"):
   if comune and via_civico and azione and resp:
    st.session_state.interventi_lista.append({"ID":len(st.session_state.interventi_lista)+1,"Data":str(data_int),"Ora":str(ora_int),"Comune":comune,"Via":via_civico,"Tipo":nome_tipo,"Icona":icona_sel,"Priorità":priorita,"ODV":odv,"Responsabile":resp,"Lat":lat,"Lon":lon,"Azione":azione})
    st.success(f"✅ Salvato {via_civico}, {comune}")
    st.rerun()
   else:
    st.error("Compila campi *")
  if st.session_state.interventi_lista:
   ultimo=st.session_state.interventi_lista[-1]
   if ultimo.get("Lat") and ultimo.get("Lon"):
    lat_u=ultimo["Lat"]; lon_u=ultimo["Lon"]
    c1,c2=st.columns(2)
    with c1:
     st.link_button("🗺️ Vedi su OSM", f"https://www.openstreetmap.org/?mlat={lat_u}&mlon={lon_u}#map=16/{lat_u}/{lon_u}", use_container_width=True)
    with c2:
     st.link_button("🔍 Google Maps", f"https://www.google.com/maps/search/?api=1&query={lat_u},{lon_u}", use_container_width=True)
 tabella_import_export("Interventi", st.session_state.interventi_lista)

# MAPPA POSTAZIONI - MASCHERA COMPLETA
elif scelta=="📍 Mappa Postazioni":
 st.markdown("## 📍 MAPPA POSTAZIONI - Maschera Completa con Loghi e Posizionamento Manuale")
 st.info("Form completo come ieri con inserimento postazioni e posizionamento manuale!")
 with st.form("post_form", clear_on_submit=True):
  c1,c2=st.columns(2)
  with c1:
   nome_post=st.text_input("Nome Postazione *", placeholder="Postazione Varese Centro")
   comune=st.selectbox("Comune *", options=LISTA_COMUNI, key="com_post")
   via_post=st.text_input("Via *", placeholder="Via Roma 10")
  with c2:
   st.markdown("#### 📍 Posizionamento Manuale")
   lat_post=st.text_input("Latitudine *", placeholder="45.8205", key="lat_post")
   lon_post=st.text_input("Longitudine *", placeholder="8.8255", key="lon_post")
   tipo_post=st.selectbox("Tipo Postazione", ["Presidio","Campo Base","Magazzino","Sede","Altro"])
  desc_post=st.text_area("Descrizione", placeholder="Descrizione postazione...")
  if st.form_submit_button("📍 SALVA POSTAZIONE", use_container_width=True, type="primary"):
   if nome_post and lat_post and lon_post:
    st.session_state.postazioni.append({"Postazione":nome_post,"Comune":comune,"Via":via_post,"Latitudine":lat_post,"Longitudine":lon_post,"Tipo":tipo_post,"Descrizione":desc_post})
    st.success(f"✅ Postazione {nome_post} salvata!")
    st.rerun()
   else:
    st.error("Compila Nome, Latitudine e Longitudine!")
 if st.session_state.postazioni:
  st.markdown("### 📍 Postazioni Salvate")
  df=pd.DataFrame(st.session_state.postazioni)
  st.dataframe(df, use_container_width=True)
  # Link mappe per ultima postazione
  ultimo=df.iloc[-1]
  if ultimo.get("Latitudine") and ultimo.get("Longitudine"):
   c1,c2=st.columns(2)
   with c1:
    st.link_button("🗺️ OSM", f"https://www.openstreetmap.org/?mlat={ultimo['Latitudine']}&mlon={ultimo['Longitudine']}#map=16/{ultimo['Latitudine']}/{ultimo['Longitudine']}", use_container_width=True)
   with c2:
    st.link_button("🔍 Google", f"https://www.google.com/maps/search/?api=1&query={ultimo['Latitudine']},{ultimo['Longitudine']}", use_container_width=True)
  c1,c2=st.columns(2)
  with c1:
   out=BytesIO()
   df.to_excel(out, index=False, engine='openpyxl')
   st.download_button("📥 Excel Postazioni", out.getvalue(), f"postazioni_{date.today()}.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
  with c2:
   if st.button("🗑️ Cancella Postazioni", use_container_width=True):
    st.session_state.postazioni=[]
    st.rerun()
 else:
  st.info("Nessuna postazione - Inserisci la prima!")

elif scelta=="👥 Volontari - Anagrafica":
 st.markdown("## 👥 VOLONTARI - Anagrafica con Sottomaschere")
 if "dati" not in st.session_state:
  st.session_state.dati=[]
 with st.form("form_vol"):
  c1,c2=st.columns(2)
  with c1:
   nome = st.text_input("Nome e Cognome *")
   cell = st.text_input("Cellulare *")
  with c2:
   assoc = st.text_input("Associazione *", value="ANA Varese")
   ruolo = st.selectbox("Ruolo *", ["Volontario", "Caposquadra", "Coordinatore", "Autista", "Radio", "Logistica", "Segreteria", "Sanitario", "Altro"])
  submitted = st.form_submit_button("✅ Salva", use_container_width=True)
  if submitted:
   if nome and assoc and cell:
    st.session_state.dati.append({"Nome": nome, "Associazione": assoc, "Cellulare": cell, "Ruolo": ruolo})
    st.success(f"Aggiunto {nome}")
    st.rerun()
   else:
    st.error("Compila i campi *")
 if st.session_state.dati:
  df = pd.DataFrame(st.session_state.dati)
  st.divider()
  # Tabella cliccabile che carica form
  st.markdown("### 👥 Clicca sul nome per sottomaschere")
  for idx, vol in enumerate(st.session_state.dati):
   c1,c2,c3,c4=st.columns([3,2,2,2])
   with c1:
    if st.button(f"👤 {vol.get('Nome','')}", key=f"vol_{idx}", use_container_width=True):
     st.session_state.volontario_selezionato=vol
     st.info(f"Selezionato {vol.get('Nome','')} - Sottomaschere attive!")
   with c2:
    st.write(vol.get('Cellulare',''))
   with c3:
    st.write(vol.get('Associazione',''))
   with c4:
    st.write(vol.get('Ruolo',''))
  st.dataframe(df, use_container_width=True, hide_index=True)
  output = BytesIO()
  df.to_excel(output, index=False, engine="openpyxl")
  st.download_button("📥 Scarica Excel", output.getvalue(), file_name="associazioni.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)

elif scelta=="📻 DB Radio Inventario":
 st.markdown("## 📻 DB RADIO")
 with st.form("radio_form", clear_on_submit=True):
  id_r=st.text_input("ID Radio *")
  modello=st.text_input("Modello")
  if st.form_submit_button("🔴 SALVA", use_container_width=True, type="primary"):
   if id_r:
    st.session_state.radio_db.append({"ID":id_r,"Modello":modello})
    st.success("Salvata")
 tabella_import_export("Radio", st.session_state.radio_db)

elif scelta=="💾 Backup Export/Import":
 st.markdown("## 💾 BACKUP")
 dati={"Interventi":st.session_state.interventi_lista,"Postazioni":st.session_state.postazioni,"Volontari":st.session_state.dati}
 for k,v in dati.items():
  st.write(f"{k}: {len(v)} record")
  if v:
   st.download_button(f"CSV {k}", pd.DataFrame(v).to_csv(index=False).encode('utf-8'), f"{k}.csv", "text/csv", use_container_width=True, key=f"csv_{k}")