import streamlit as st
import pandas as pd
from datetime import datetime, date
from io import BytesIO
import base64, os, json

try:
 from reportlab.lib.pagesizes import landscape, A4
 from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
 from reportlab.lib import colors
 from reportlab.lib.styles import getSampleStyleSheet
 from reportlab.lib.units import cm
 HAS=True
except:
 HAS=False

st.set_page_config(page_title="ANA Varese - Pulito", page_icon="🟢", layout="wide")

for k,v in [("authenticated",False),("dashboard_entered",False),("interventi_lista",[]),("eventi",[]),("mem_nomi",["Mario Rossi","Luigi Bianchi","Giuseppe Verdi"]),("radio_db",[]),("dist_radio",[]),("postazioni",[]),("brogliaccio",[]),("registro_radio",[]),("volontari_full",[]),("checkin",{}),("icone_personalizzate",[])]:
 if k not in st.session_state:
  st.session_state[k]=v

ICONE={"🔥 Incendio Boschivo":"🔥","🌊 Alluvione":"🌊","❄️ Neve":"❄️","⛰️ Frana":"⛰️","🔍 Ricerca Persona":"🔍","👥 Supporto Popolazione":"👥","👁️ Monitoraggio":"👁️","🚧 Presidio":"🚧","🚑 Sanitario":"🚑","🏚️ Crollo":"🏚️","🌲 Antincendio":"🌲","⚡ Blackout":"⚡","🦺 Esercitazione":"🦺","🎪 Manifestazione":"🎪","🚨 Altro":"🚨"}
LIB_ICONE=[{"nome":k,"icona":v} for k,v in ICONE.items()]

try:
 df_com=pd.read_csv("comuni_italiani.csv")
 LISTA_COMUNI=sorted(df_com["Comune"].astype(str).unique().tolist())
except:
 LISTA_COMUNI=["Varese","Busto Arsizio","Gallarate","Saronno","Cassano Magnago","Tradate","Somma Lombardo","Malnate","Luino","Samarate","Venegono Superiore","Venegono Inferiore","Milano","Como"]

try:
 df_vie=pd.read_csv("vie_per_comune.csv")
 VIE_PER_COMUNE={}
 for c in df_vie["Comune"].unique():
  VIE_PER_COMUNE[c]=df_vie[df_vie["Comune"]==c]["Via"].astype(str).unique().tolist()
except:
 VIE_PER_COMUNE={"Varese":["Via Roma","Via Milano","Via Garibaldi","Via Verdi","Via Manzoni","Via Cavour","Via Matteotti","Via Volta"]}

def get_b64(p):
 try:
  if os.path.exists(p):
   with open(p,"rb") as f:
    return base64.b64encode(f.read()).decode()
 except:
  pass
 return ""

b64_vol=get_b64("logo_volontariato_varese.jpg")
b64_ana=get_b64("logo_ana_varese.jpg")
b64_pc=get_b64("logo_protezione_civile_lombardia.jpg")

# LOGHI PULITI - solo titolo, senza scritte lunghe
if b64_vol and b64_ana and b64_pc:
 LOGHI=f"""
<div style='display:flex; justify-content:center; align-items:center; gap:15px; background:#a5d6a7; padding:12px; border-radius:15px; border:3px solid #2e7d32; margin-bottom:12px;'>
  <img src='data:image/jpeg;base64,{b64_vol}' style='width:70px; height:70px; border-radius:50%; border:2px solid #1b5e20; background:white;'>
  <img src='data:image/jpeg;base64,{b64_ana}' style='width:80px; height:80px; border-radius:50%; border:2px solid #1b5e20; background:white;'>
  <img src='data:image/jpeg;base64,{b64_pc}' style='width:70px; height:70px; border-radius:50%; border:2px solid #2e7d32; background:white;'>
  <h3 style='color:#1b5e20; margin:0;'>ANA Varese - Protezione Civile</h3>
</div>
"""
else:
 LOGHI="<div style='background:#a5d6a7; padding:12px; border-radius:12px; border:3px solid #2e7d32; text-align:center;'><h3 style='color:#1b5e20; margin:0;'>ANA Varese - Protezione Civile</h3></div>"

st.markdown("""<style>
.stApp{background:#e8f5e9!important;}
.main .block-container{max-width:100%!important; padding:1% 2%!important;}
[data-testid="stSidebar"]{background:#a5d6a7!important;}
.stForm{background:#a5d6a7!important; border:3px solid #2e7d32!important; border-radius:15px!important; padding:15px!important;}
.stButton>button{background:#d32f2f!important; color:white!important; font-weight:bold!important; border-radius:10px!important;}
</style>""", unsafe_allow_html=True)

# LOGIN
if not st.session_state.authenticated:
 st.markdown(LOGHI, unsafe_allow_html=True)
 st.markdown("<h2 style='text-align:center;'>🔐 Accesso</h2>", unsafe_allow_html=True)
 pwd=st.text_input("Password", type="password")
 if st.button("Accedi", use_container_width=True, type="primary"):
  if pwd=="ANA2025":
   st.session_state.authenticated=True
   st.rerun()
  else:
   st.error("Password errata")
 st.stop()

# MENU
with st.sidebar:
 st.markdown(LOGHI, unsafe_allow_html=True)
 scelta=st.radio("Menu", ["🏠 Dashboard","🚨 Interventi Emergenza","📅 Eventi","👥 Volontari","📻 Radio","🗺️ Postazioni","📝 Brogliaccio","💾 Backup"], index=0)
 if st.button("🔒 Logout", use_container_width=True):
  st.session_state.authenticated=False
  st.rerun()

# FUNZIONE TABELLA PULITA
def tabella_pulita(nome, lista):
 if lista:
  st.dataframe(pd.DataFrame(lista), use_container_width=True, height=300)
  c1,c2=st.columns(2)
  with c1:
   st.download_button(f"📥 CSV {nome}", pd.DataFrame(lista).to_csv(index=False).encode('utf-8'), f"{nome}.csv", "text/csv", use_container_width=True)
  with c2:
   if st.button(f"🗑️ Pulisci {nome}", use_container_width=True):
    lista.clear()
    st.rerun()

# DASHBOARD PULITA
if scelta=="🏠 Dashboard":
 st.markdown(LOGHI, unsafe_allow_html=True)
 c1,c2,c3=st.columns(3)
 c1.metric("Interventi", len(st.session_state.interventi_lista))
 c2.metric("Eventi", len(st.session_state.eventi))
 c3.metric("Volontari", len(st.session_state.mem_nomi))

# INTERVENTI EMERGENZA - VERSIONE PULITA SENZA SCRITTE INUTILI
elif scelta=="🚨 Interventi Emergenza":
 st.markdown(LOGHI, unsafe_allow_html=True)
 
 # Libreria icone nascosta in expander piccolo
 with st.expander("🎨 Libreria icone (opzionale)", expanded=False):
  ups=st.file_uploader("Carica icone da PC", type=["png","jpg","jpeg","ico"], accept_multiple_files=True, key="up_icone")
  if ups:
   for up in ups:
    st.session_state.icone_personalizzate.append({"nome":up.name.split(".")[0],"icona":"🖼️"})
   st.success(f"Caricate {len(ups)} icone")

 # FORM PULITO - SOLO CAMPI ESSENZIALI
 with st.form("form_int", clear_on_submit=True):
  c1,c2=st.columns(2)
  with c1:
   data_int=st.date_input("Data", value=date.today())
   ora_int=st.time_input("Ora")
   comune=st.selectbox("Comune", options=LISTA_COMUNI, index=LISTA_COMUNI.index("Varese") if "Varese" in LISTA_COMUNI else 0)
   vie_list=VIE_PER_COMUNE.get(comune, ["Via Roma","Via Milano","Via Garibaldi"])
   via_sel=st.selectbox("Via", options=vie_list)
   civ=st.text_input("Civico", placeholder="15")
   via_civico=f"{via_sel} {civ}".strip()
  with c2:
   tutte_icone=LIB_ICONE+st.session_state.icone_personalizzate
   opts=[f"{ic.get('icona','🔹')} {ic.get('nome','')}" for ic in tutte_icone]
   tipo=st.selectbox("Tipo intervento", options=opts)
   icona_sel=tipo.split(" ")[0] if tipo else "🚨"
   nome_tipo=" ".join(tipo.split(" ")[1:]) if len(tipo.split(" "))>1 else tipo
   priorita=st.selectbox("Priorità", ["Bassa","Media","Alta","Critica"])
   odv=st.selectbox("ODV", ["ANA Varese","PC Lombardia","Croce Rossa","VVF","Altro"])
   resp=st.text_input("Responsabile *")
  azione=st.text_area("Azione svolta *", height=80)
  note=st.text_area("Note", height=40)
  
  if st.form_submit_button("🔴 SALVA", use_container_width=True, type="primary"):
   if comune and via_civico and azione and resp:
    st.session_state.interventi_lista.append({"ID":len(st.session_state.interventi_lista)+1,"Data":str(data_int),"Ora":str(ora_int),"Comune":comune,"Via":via_civico,"Tipo":nome_tipo,"Icona":icona_sel,"Priorità":priorita,"ODV":odv,"Responsabile":resp,"Azione":azione,"Note":note})
    st.success(f"Salvato {via_civico}, {comune}")
   else:
    st.error("Compila i campi *")

 tabella_pulita("Interventi", st.session_state.interventi_lista)

# ALTRI FORM PULITI
elif scelta=="📅 Eventi":
 st.markdown(LOGHI, unsafe_allow_html=True)
 with st.form("ev_form", clear_on_submit=True):
  c1,c2=st.columns(2)
  with c1:
   titolo=st.text_input("Titolo evento *")
   comune=st.selectbox("Comune", options=LISTA_COMUNI)
  with c2:
   data_ev=st.date_input("Data", value=date.today())
   ora_ev=st.time_input("Ora")
  desc=st.text_area("Descrizione")
  if st.form_submit_button("🔴 SALVA", use_container_width=True, type="primary"):
   if titolo:
    st.session_state.eventi.append({"Titolo":titolo,"Comune":comune,"Data":str(data_ev),"Ora":str(ora_ev),"Descrizione":desc})
    st.success("Evento salvato")
 tabella_pulita("Eventi", st.session_state.eventi)

elif scelta=="👥 Volontari":
 st.markdown(LOGHI, unsafe_allow_html=True)
 with st.form("vol_form", clear_on_submit=True):
  nome=st.text_input("Nome e Cognome *")
  cell=st.text_input("Cellulare")
  if st.form_submit_button("🔴 SALVA", use_container_width=True, type="primary"):
   if nome:
    st.session_state.mem_nomi.append(nome)
    st.session_state.volontari_full.append({"Nome":nome,"Cell":cell})
    st.success(f"Aggiunto {nome}")
 tabella_pulita("Volontari", st.session_state.volontari_full)

elif scelta=="📻 Radio":
 st.markdown(LOGHI, unsafe_allow_html=True)
 with st.form("radio_form", clear_on_submit=True):
  id_r=st.text_input("ID Radio *")
  modello=st.text_input("Modello")
  if st.form_submit_button("🔴 SALVA", use_container_width=True, type="primary"):
   if id_r:
    st.session_state.radio_db.append({"ID":id_r,"Modello":modello})
    st.success("Radio salvata")
 tabella_pulita("Radio", st.session_state.radio_db)

elif scelta=="🗺️ Postazioni":
 st.markdown(LOGHI, unsafe_allow_html=True)
 with st.form("post_form", clear_on_submit=True):
  nome=st.text_input("Postazione *")
  comune=st.selectbox("Comune", options=LISTA_COMUNI)
  via=st.text_input("Via")
  if st.form_submit_button("🔴 SALVA", use_container_width=True, type="primary"):
   if nome:
    st.session_state.postazioni.append({"Postazione":nome,"Comune":comune,"Via":via})
    st.success("Salvata")
 tabella_pulita("Postazioni", st.session_state.postazioni)

elif scelta=="📝 Brogliaccio":
 st.markdown(LOGHI, unsafe_allow_html=True)
 with st.form("brog_form", clear_on_submit=True):
  comune=st.selectbox("Comune", options=LISTA_COMUNI)
  msg=st.text_area("Messaggio *", height=100)
  if st.form_submit_button("🔴 SALVA", use_container_width=True, type="primary"):
   if msg:
    st.session_state.brogliaccio.append({"Comune":comune,"Data":str(date.today()),"Messaggio":msg})
    st.success("Salvato")
 tabella_pulita("Brogliaccio", st.session_state.brogliaccio)

elif scelta=="💾 Backup":
 st.markdown(LOGHI, unsafe_allow_html=True)
 dati={"Interventi":st.session_state.interventi_lista,"Eventi":st.session_state.eventi,"Volontari":st.session_state.volontari_full}
 for k,v in dati.items():
  st.write(f"{k}: {len(v)} record")
  if v:
   st.download_button(f"CSV {k}", pd.DataFrame(v).to_csv(index=False).encode('utf-8'), f"{k}.csv", "text/csv", use_container_width=True, key=f"csv_{k}")

st.caption("ANA Varese - Versione pulita - Solo campi essenziali")
