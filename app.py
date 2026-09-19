import streamlit as st
import pandas as pd
from datetime import date, datetime
from io import BytesIO
import os, json, base64, hashlib

st.set_page_config(
 page_title="ANA Varese",
 layout="wide"
)

st.markdown("""
<style>
.stApp{background:#e8f5e9!important;}
.block-container{
 background:white!important;
 border-radius:18px;
 padding:20px!important;
 padding-bottom:95px!important;
}
[data-testid="stSidebar"]{
 background:#a5d6a7!important;
 border-right:4px solid #2e7d32!important;
}
.stForm{
 background:#c8e6c9!important;
 border:3px solid #2e7d32!important;
 border-radius:15px!important;
}
.stButton>button{
 background:#2e7d32!important;
 color:white!important;
 font-weight:bold!important;
 min-height:50px!important;
 border-radius:10px!important;
}
.foot{
 position:fixed;
 bottom:5px;
 left:10px;
 background:white;
 border:2px solid #2e7d32;
 border-radius:12px;
 padding:5px 12px;
 display:flex;
 align-items:center;
 gap:8px;
 z-index:9999;
}
</style>
""", unsafe_allow_html=True)

def load_json(f,d):
 try:
  if os.path.exists(f):
   with open(f,"r",encoding="utf-8") as fh:
    return json.load(fh)
 except:
  pass
 return d

def save_json(f,d):
 try:
  with open(f,"w",encoding="utf-8") as fh:
   json.dump(d,fh,indent=2)
 except:
  pass

def get_b64(p):
 try:
  if os.path.exists(p):
   with open(p,"rb") as f:
    return base64.b64encode(f.read()).decode()
 except:
  pass
 return ""

def hash_pwd(p):
 return hashlib.sha256(p.encode()).hexdigest()

def footer():
 b=get_b64("ezio.png")
 if not b:
  b=get_b64("logo.png")
 if b:
  img="<img src='data:image/png;base64,"+b+"'>"
 else:
  img="<div style='width:45px;height:45px;background:#2e7d32;border-radius:50%;'></div>"
 st.markdown(
  "<div class='foot'>"+img+"<span>by Ezio F. 2026</span></div>",
  unsafe_allow_html=True
 )

FD="dati.json"
FU="utenti.json"
FP="post.json"
FE="eventi.json"
FR="radio.json"
FC="check.json"
FB="brog.json"
FO="consegna.json"
FM="emerg.json"

if "dati" not in st.session_state:
 st.session_state.dati=[]
if "post" not in st.session_state:
 st.session_state.post=[]
if "eventi" not in st.session_state:
 st.session_state.eventi=[]
if "radio" not in st.session_state:
 st.session_state.radio=[]
if "check" not in st.session_state:
 st.session_state.check=[]
if "brog" not in st.session_state:
 st.session_state.brog=[]
if "consegna" not in st.session_state:
 st.session_state.consegna=[]
if "emerg" not in st.session_state:
 st.session_state.emerg=[]
if "utenti" not in st.session_state:
 st.session_state.utenti=[]
if "menu" not in st.session_state:
 st.session_state.menu="Dashboard"
if "auth" not in st.session_state:
 st.session_state.auth=False
if "lat_tmp" not in st.session_state:
 st.session_state.lat_tmp=45.8205
if "lon_tmp" not in st.session_state:
 st.session_state.lon_tmp=8.8250

st.session_state.dati=load_json(FD,[])
st.session_state.utenti=load_json(FU,[])
st.session_state.post=load_json(FP,[])
st.session_state.eventi=load_json(FE,[])
st.session_state.radio=load_json(FR,[])
st.session_state.check=load_json(FC,[])
st.session_state.brog=load_json(FB,[])
st.session_state.consegna=load_json(FO,[])
st.session_state.emerg=load_json(FM,[])

if not st.session_state.utenti:
 st.session_state.utenti=[
  {"username":"admin","password":hash_pwd("ana2024")},
  {"username":"utente","password":hash_pwd("utente2024")}
 ]
 save_json(FU,st.session_state.utenti)

def header():
 b=get_b64("logo.png")
 if b:
  h="<div style='text-align:center;background:#a5d6a7;padding:15px;border-radius:15px;border:3px solid #2e7d32;'><img src='data:image/png;base64,"+b+"' style='width:80px;border-radius:50%;'><h2 style='color:#0e7a3d;'>VOLONTARIATO Varese</h2></div>"
  st.markdown(h,unsafe_allow_html=True)
 else:
  st.markdown(
   "<h2 style='text-align:center;color:green;'>VOLONTARIATO Varese</h2>",
   unsafe_allow_html=True
  )

def torna():
 if st.button("TORNA"):
  st.session_state.menu="Dashboard"
  st.rerun()

if not st.session_state.auth:
 header()
 st.markdown("## LOGIN")
 c1,c2,c3=st.columns([1,2,1])
 with c2:
  with st.form("login"):
   u=st.text_input("Username",value="admin")
   p=st.text_input("Password",type="password",value="ana2024")
   ok=st.form_submit_button("ACCEDI")
   if ok:
    ph=hash_pwd(p)
    trov=None
    for ut in st.session_state.utenti:
     if ut["username"]==u and ut["password"]==ph:
      trov=ut
    if trov:
     st.session_state.auth=True
     st.rerun()
    else:
     st.error("Errati")
 footer()
 st.stop()

header()
st.divider()

with st.sidebar:
 if os.path.exists("logo.png"):
  st.image("logo.png",width=80)
 opts=[
  "Dashboard",
  "Volontari",
  "Mappa",
  "Eventi",
  "Radio",
  "Check",
  "Brogliaccio",
  "Consegna",
  "Emergenze",
  "Backup"
 ]
 sel=st.radio("Vai a",opts,index=0)
 if sel!=st.session_state.menu:
  st.session_state.menu=sel
  st.rerun()
 if st.button("LOGOUT"):
  st.session_state.auth=False
  st.rerun()

scelta=st.session_state.menu

# DASHBOARD CON TUTTI I TASTI
if scelta=="Dashboard":
 st.markdown("## DASHBOARD")
 st.success("Verde OK - Tutti i tasti")

 c1,c2,c3=st.columns(3)
 with c1:
  if st.button("VOLONTARI"):
   st.session_state.menu="Volontari"
   st.rerun()
  if st.button("EVENTI"):
   st.session_state.menu="Eventi"
   st.rerun()
  if st.button("BROGLIACCIO"):
   st.session_state.menu="Brogliaccio"
   st.rerun()
 with c2:
  if st.button("MAPPA"):
   st.session_state.menu="Mappa"
   st.rerun()
  if st.button("RADIO"):
   st.session_state.menu="Radio"
   st.rerun()
  if st.button("CONSEGNA"):
   st.session_state.menu="Consegna"
   st.rerun()
 with c3:
  if st.button("CHECK-IN"):
   st.session_state.menu="Check"
   st.rerun()
  if st.button("EMERGENZE"):
   st.session_state.menu="Emergenze"
   st.rerun()
  if st.button("BACKUP"):
   st.session_state.menu="Backup"
   st.rerun()

 c1,c2,c3,c4=st.columns(4)
 with c1:
  st.metric("Volontari",len(st.session_state.dati))
 with c2:
  st.metric("Postazioni",len(st.session_state.post))
 with c3:
  st.metric("Check",len(st.session_state.check))
 with c4:
  st.metric("Eventi",len(st.session_state.eventi))

 footer()

# VOLONTARI CON DESCRIZIONE NON NUMERI
elif scelta=="Volontari":
 torna()
 st.markdown("## VOLONTARI")

 # DESCRIZIONE NON NUMERI
 t1,t2,t3,t4,t5=st.tabs([
  "Anagrafica",
  "Residenza",
  "Tesseramento",
  "Abilita",
  "Note"
 ])

 with t1:
  with st.form("f1"):
   st.markdown("**Anagrafica**")
   a1=st.text_input("Nome *",key="a1")
   a2=st.text_input("Cognome *",key="a2")
   a3=st.text_input("CF",key="a3")
   a4=st.date_input("Nascita",value=date(1980,1,1),key="a4")
   a5=st.text_input("Luogo nascita",key="a5")
   if st.form_submit_button("SALVA ANAGRAFICA"):
    st.session_state.s1_nome=a1
    st.session_state.s1_cogn=a2
    st.session_state.s1_cf=a3
    st.session_state.s1_dn=str(a4)
    st.session_state.s1_luogo=a5
    st.success("OK Anagrafica")

 with t2:
  with st.form("f2"):
   st.markdown("**Residenza e Contatti**")
   b1=st.text_input("Via *",key="b1")
   b2=st.text_input("Comune *",value="Varese",key="b2")
   b3=st.text_input("Prov",value="VA",key="b2b")
   b4=st.text_input("Cell *",key="b3")
   b5=st.text_input("Email",key="b4")
   if st.form_submit_button("SALVA RESIDENZA"):
    st.session_state.s2_via=b1
    st.session_state.s2_com=b2
    st.session_state.s2_cell=b4
    st.session_state.s2_mail=b5
    st.success("OK Residenza")

 with t3:
  with st.form("f3"):
   st.markdown("**Tesseramento**")
   c1x=st.text_input("N. Tessera",key="c1")
   c2x=st.date_input("Scadenza",value=date(2026,12,31),key="c2")
   c3x=st.text_input("Ruolo",value="Volontario",key="c3")
   c4x=st.text_input("Sezione",value="Varese",key="c4")
   if st.form_submit_button("SALVA TESSERAMENTO"):
    st.session_state.s3_tess=c1x
    st.session_state.s3_ruolo=c3x
    st.success("OK Tesseramento")

 with t4:
  with st.form("f4"):
   st.markdown("**Abilita e Patenti**")
   d1=st.text_input("Patenti",value="B",key="d1")
   d2=st.text_input("Corso base",value="Si",key="d2")
   d3=st.text_input("Specializ",key="d3")
   d4=st.text_input("Altro",key="d4")
   if st.form_submit_button("SALVA ABILITA"):
    st.session_state.s4_pat=d1
    st.session_state.s4_base=d2
    st.success("OK Abilita")

 with t5:
  with st.form("f5"):
   st.markdown("**Note e Salvataggio Finale**")
   e1=st.text_input("Note brevi",key="e1")
   e2=st.text_area("Note estese",key="e2")
   btn=st.form_submit_button("SALVA VOLONTARIO COMPLETO")
   if btn:
    nome=st.session_state.get("s1_nome","")
    cogn=st.session_state.get("s1_cogn","")
    cell=st.session_state.get("s2_cell","")
    com=st.session_state.get("s2_com","")
    ruolo=st.session_state.get("s3_ruolo","")
    if nome and cell:
     nuovo={}
     nuovo["Nome"]=nome+" "+cogn
     nuovo["Cell"]=cell
     nuovo["Comune"]=com
     nuovo["Ruolo"]=ruolo
     nuovo["Note"]=e2
     st.session_state.dati.append(nuovo)
     save_json(FD,st.session_state.dati)
     st.success("Volontario salvato")
     st.rerun()
    else:
     st.error("Manca nome o cell")

 if st.session_state.dati:
  st.dataframe(pd.DataFrame(st.session_state.dati))

# MAPPA CON ANTEPRIMA E SELEZIONE MAPPA
elif scelta=="Mappa":
 torna()
 st.markdown("## MAPPA POSTAZIONI")

 st.markdown("### SELEZIONE TIPO MAPPA")
 tipo_mappa=st.selectbox(
  "Scegli mappa",
  ["OSM Standard","Satellite","Terreno","Tutte postazioni"],
  key="tipo_mappa"
 )
 st.info("Tipo selezionato: "+tipo_mappa)

 # ANTEPRIMA MAPPA PER INSERIMENTO MANUALE
 st.markdown("### 1 - ANTEPRIMA MAPPA PER INSERIMENTO MANUALE")

 col_a,col_b=st.columns([2,1])
 with col_a:
  st.markdown("**Anteprima mappa**")
  lat_man=st.number_input(
   "Lat",
   value=float(st.session_state.lat_tmp),
   format="%.6f",
   key="lat_man"
  )
  lon_man=st.number_input(
   "Lon",
   value=float(st.session_state.lon_tmp),
   format="%.6f",
   key="lon_man"
  )
  st.session_state.lat_tmp=lat_man
  st.session_state.lon_tmp=lon_man
  df_ante=pd.DataFrame({"lat":[lat_man],"lon":[lon_man]})
  st.map(df_ante,zoom=14)
  st.caption("Anteprima - dentro form - manuale")

 with col_b:
  st.markdown("**Istruzioni**")
  st.write("1 - Scrivi Lat/Lon")
  st.write("2 - Vedi mappa")
  st.write("3 - Salva sotto")
  cerca=st.text_input("Cerca",value="Varese",key="cerca_map")
  if st.button("CENTRA VARESE"):
   st.session_state.lat_tmp=45.8205
   st.session_state.lon_tmp=8.8250
   st.rerun()
  st.markdown("**Tipo mappa**")
  st.write(tipo_mappa)

 st.divider()
 st.markdown("### 2 - INSERIMENTO MANUALE POSTAZIONE")

 with st.form("form_mappa"):
  c1,c2=st.columns(2)
  with c1:
   m1=st.text_input("Nome *",key="m1")
   m2=st.text_input("Comune *",value="Varese",key="m2")
   m3=st.text_input("Via *",key="m3")
   m7=st.text_input("Tipo",value="Presidio",key="m7")
  with c2:
   m5=st.text_input("Lat",value=str(st.session_state.lat_tmp),key="m5")
   m6=st.text_input("Lon",value=str(st.session_state.lon_tmp),key="m6")
   m8=st.text_input("Resp",key="m8")
   m9=st.text_area("Note",key="m9")

  st.markdown("**Icona**")
  icona=st.file_uploader("Icona PNG/JPG",type=["png","jpg","jpeg"],key="icona_map")
  nome_icona=""
  if icona:
   nome_icona=icona.name
   st.image(icona,width=100)

  st.markdown("**Anteprima dentro form**")
  try:
   lat_f=float(m5)
   lon_f=float(m6)
   df_form=pd.DataFrame({"lat":[lat_f],"lon":[lon_f]})
   st.map(df_form)
  except:
   st.info("Inserisci Lat Lon validi")

  ok=st.form_submit_button("SALVA POSTAZIONE")
  if ok and m1:
   nuovo={}
   nuovo["Postazione"]=m1
   nuovo["Comune"]=m2
   nuovo["Via"]=m3
   nuovo["Lat"]=m5
   nuovo["Lon"]=m6
   nuovo["Tipo"]=m7
   nuovo["Icona"]=nome_icona
   nuovo["Note"]=m9
   st.session_state.post.append(nuovo)
   save_json(FP,st.session_state.post)
   st.success("Salvata")
   st.rerun()

 st.divider()
 st.markdown("### 3 - MAPPA CON TUTTE LE POSTAZIONI")

 if st.session_state.post:
  try:
   df_all=pd.DataFrame(st.session_state.post)
   df_all["lat"]=pd.to_numeric(df_all["Lat"],errors="coerce")
   df_all["lon"]=pd.to_numeric(df_all["Lon"],errors="coerce")
   df_all=df_all.dropna(subset=["lat","lon"])
   if not df_all.empty:
    st.map(df_all[["lat","lon"]])
    st.caption("Tutte le postazioni - "+tipo_mappa)
  except:
   pass
  st.dataframe(pd.DataFrame(st.session_state.post))
  # Link mappe come stamattina
  for p in st.session_state.post:
   lat=p.get("Lat","45.8205")
   lon=p.get("Lon","8.8250")
   nome=p.get("Postazione","Post")
   st.write("**"+nome+"**")
   c1,c2,c3=st.columns(3)
   with c1:
    osm="https://www.openstreetmap.org/?mlat="+lat+"&mlon="+lon
    st.link_button("OSM",osm)
   with c2:
    gmap="https://www.google.com/maps?q="+lat+","+lon
    st.link_button("Google",gmap)
   with c3:
    waze="https://waze.com/ul?ll="+lat+","+lon
    st.link_button("Waze",waze)
 else:
  df_def=pd.DataFrame({"lat":[45.8205],"lon":[8.8250]})
  st.map(df_def)
  st.info("Mappa Varese - inserisci postazioni")

elif scelta=="Check":
 torna()
 st.markdown("## CHECK-IN")
 with st.form("form_check"):
  nomi=[d.get("Nome","") for d in st.session_state.dati]
  if not nomi:
   nomi=["Nessun volontario"]
  ch1=st.selectbox("Vol",nomi,key="ch1")
  ch2=st.text_input("Post",key="ch2")
  ch3=st.time_input("Ora",value=datetime.now().time(),key="ch3")
  ch4=st.date_input("Data",value=date.today(),key="ch4")
  ch7=st.text_area("Note",key="ch7")
  ok=st.form_submit_button("SALVA")
  if ok:
   nuovo={}
   nuovo["Vol"]=ch1
   nuovo["Post"]=ch2
   nuovo["Ora"]=str(ch3)
   nuovo["Data"]=str(ch4)
   nuovo["Note"]=ch7
   st.session_state.check.append(nuovo)
   save_json(FC,st.session_state.check)
   st.success("OK")
   st.rerun()
 if st.session_state.check:
  st.dataframe(pd.DataFrame(st.session_state.check))

elif scelta=="Brogliaccio":
 torna()
 st.markdown("## BROGLIACCIO")
 with st.form("form_brog"):
  b1=st.text_input("Mitt *",key="br1")
  b2=st.text_input("Dest *",key="br2")
  b7=st.text_area("Mess *",key="br7")
  b4=st.time_input("Ora",value=datetime.now().time(),key="br4")
  b5=st.date_input("Data",value=date.today(),key="br5")
  ok=st.form_submit_button("SALVA")
  if ok and b1 and b7:
   nuovo={}
   nuovo["Mitt"]=b1
   nuovo["Dest"]=b2
   nuovo["Ora"]=str(b4)
   nuovo["Data"]=str(b5)
   nuovo["Mess"]=b7
   st.session_state.brog.append(nuovo)
   save_json(FB,st.session_state.brog)
   st.success("OK")
   st.rerun()
 if st.session_state.brog:
  st.dataframe(pd.DataFrame(st.session_state.brog))

elif scelta=="Consegna":
 torna()
 st.markdown("## CONSEGNA RADIO")
 with st.form("form_consegna"):
  ids=[r.get("ID","") for r in st.session_state.radio]
  if not ids:
   ids=["RADIO-01"]
  co1=st.selectbox("ID Radio",ids,key="co1")
  nomi=[d.get("Nome","") for d in st.session_state.dati]
  if not nomi:
   nomi=["Nessun volontario"]
  co2=st.selectbox("A",nomi,key="co2")
  co3=st.date_input("Data",value=date.today(),key="co3")
  co4=st.time_input("Ora",value=datetime.now().time(),key="co4")
  ok=st.form_submit_button("SALVA")
  if ok:
   nuovo={}
   nuovo["Radio"]=co1
   nuovo["Vol"]=co2
   nuovo["Data"]=str(co3)
   nuovo["Ora"]=str(co4)
   st.session_state.consegna.append(nuovo)
   save_json(FO,st.session_state.consegna)
   st.success("OK")
   st.rerun()
 if st.session_state.consegna:
  st.dataframe(pd.DataFrame(st.session_state.consegna))

elif scelta=="Eventi":
 torna()
 st.markdown("## EVENTI")
 with st.form("form_ev"):
  e1=st.text_input("Nome *")
  e2=st.date_input("Data",value=date.today())
  e3=st.text_input("Luogo *")
  e4=st.text_area("Desc")
  ok=st.form_submit_button("SALVA")
  if ok and e1:
   nuovo={}
   nuovo["Evento"]=e1
   nuovo["Data"]=str(e2)
   nuovo["Luogo"]=e3
   nuovo["Desc"]=e4
   st.session_state.eventi.append(nuovo)
   save_json(FE,st.session_state.eventi)
   st.success("OK")
   st.rerun()
 if st.session_state.eventi:
  st.dataframe(pd.DataFrame(st.session_state.eventi))

elif scelta=="Radio":
 torna()
 st.markdown("## RADIO")
 with st.form("form_ra"):
  r1=st.text_input("ID *")
  r2=st.text_input("Modello *")
  r3=st.text_input("Freq",value="446.00625")
  ok=st.form_submit_button("SALVA")
  if ok and r1:
   nuovo={}
   nuovo["ID"]=r1
   nuovo["Mod"]=r2
   nuovo["Freq"]=r3
   st.session_state.radio.append(nuovo)
   save_json(FR,st.session_state.radio)
   st.success("OK")
   st.rerun()
 if st.session_state.radio:
  st.dataframe(pd.DataFrame(st.session_state.radio))

elif scelta=="Emergenze":
 torna()
 st.markdown("## EMERGENZE")
 with st.form("form_em"):
  em1=st.text_input("Tipo",value="Alluvione")
  em2=st.text_input("Comune",value="Varese")
  em3=st.text_input("Via *")
  em4=st.text_input("Coord *")
  em5=st.text_area("Desc *")
  ok=st.form_submit_button("SALVA")
  if ok and em3:
   nuovo={}
   nuovo["Tipo"]=em1
   nuovo["Comune"]=em2
   nuovo["Via"]=em3
   nuovo["Coord"]=em4
   nuovo["Desc"]=em5
   st.session_state.emerg.append(nuovo)
   save_json(FM,st.session_state.emerg)
   st.success("OK")
   st.rerun()
 if st.session_state.emerg:
  st.dataframe(pd.DataFrame(st.session_state.emerg))

elif scelta=="Backup":
 torna()
 st.markdown("## BACKUP - SCEGLI DATI")

 st.markdown("### EXPORT")
 c1,c2=st.columns(2)
 with c1:
  exp_vol=st.checkbox("Volontari",value=True)
  exp_mappa=st.checkbox("Mappa",value=True)
  exp_check=st.checkbox("Check",value=True)
  exp_brog=st.checkbox("Brog",value=True)
 with c2:
  exp_cons=st.checkbox("Consegna",value=True)
  exp_eventi=st.checkbox("Eventi",value=True)
  exp_radio=st.checkbox("Radio",value=True)
  exp_emerg=st.checkbox("Emergenze",value=True)

 if st.button("CREA BACKUP"):
  out=BytesIO()
  with pd.ExcelWriter(out,engine="openpyxl") as writer:
   if exp_vol and st.session_state.dati:
    pd.DataFrame(st.session_state.dati).to_excel(writer,sheet_name="Vol",index=False)
   if exp_mappa and st.session_state.post:
    pd.DataFrame(st.session_state.post).to_excel(writer,sheet_name="Mappa",index=False)
   if exp_check and st.session_state.check:
    pd.DataFrame(st.session_state.check).to_excel(writer,sheet_name="Check",index=False)
   if exp_brog and st.session_state.brog:
    pd.DataFrame(st.session_state.brog).to_excel(writer,sheet_name="Brog",index=False)
   if exp_cons and st.session_state.consegna:
    pd.DataFrame(st.session_state.consegna).to_excel(writer,sheet_name="Consegna",index=False)
   if exp_eventi and st.session_state.eventi:
    pd.DataFrame(st.session_state.eventi).to_excel(writer,sheet_name="Eventi",index=False)
   if exp_radio and st.session_state.radio:
    pd.DataFrame(st.session_state.radio).to_excel(writer,sheet_name="Radio",index=False)
   if exp_emerg and st.session_state.emerg:
    pd.DataFrame(st.session_state.emerg).to_excel(writer,sheet_name="Emergenze",index=False)
  st.session_state["bk"]=out.getvalue()
  st.success("Backup OK")

 if "bk" in st.session_state:
  st.download_button(
   "SCARICA BACKUP",
   st.session_state["bk"],
   file_name="BACKUP.xlsx",
   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
  )

 st.divider()
 st.markdown("### IMPORT")
 uploaded=st.file_uploader("Carica Excel",type=["xlsx"])
 if uploaded:
  try:
   xls=pd.ExcelFile(uploaded)
   sheets=xls.sheet_names
   st.write(sheets)
   c1,c2=st.columns(2)
   with c1:
    imp_vol=st.checkbox("Importa Vol",value=True)
    imp_mappa=st.checkbox("Importa Mappa",value=True)
    imp_check=st.checkbox("Importa Check",value=True)
    imp_brog=st.checkbox("Importa Brog",value=True)
   with c2:
    imp_cons=st.checkbox("Importa Consegna",value=True)
    imp_eventi=st.checkbox("Importa Eventi",value=True)
    imp_radio=st.checkbox("Importa Radio",value=True)
    imp_emerg=st.checkbox("Importa Emerg",value=True)
   if st.button("IMPORTA"):
    if imp_vol and "Vol" in sheets:
     df=pd.read_excel(xls,"Vol")
     st.session_state.dati=df.to_dict(orient="records")
     save_json(FD,st.session_state.dati)
    if imp_mappa and "Mappa" in sheets:
     df=pd.read_excel(xls,"Mappa")
     st.session_state.post=df.to_dict(orient="records")
     save_json(FP,st.session_state.post)
    if imp_check and "Check" in sheets:
     df=pd.read_excel(xls,"Check")
     st.session_state.check=df.to_dict(orient="records")
     save_json(FC,st.session_state.check)
    if imp_brog and "Brog" in sheets:
     df=pd.read_excel(xls,"Brog")
     st.session_state.brog=df.to_dict(orient="records")
     save_json(FB,st.session_state.brog)
    if imp_cons and "Consegna" in sheets:
     df=pd.read_excel(xls,"Consegna")
     st.session_state.consegna=df.to_dict(orient="records")
     save_json(FO,st.session_state.consegna)
    if imp_eventi and "Eventi" in sheets:
     df=pd.read_excel(xls,"Eventi")
     st.session_state.eventi=df.to_dict(orient="records")
     save_json(FE,st.session_state.eventi)
    if imp_radio and "Radio" in sheets:
     df=pd.read_excel(xls,"Radio")
     st.session_state.radio=df.to_dict(orient="records")
     save_json(FR,st.session_state.radio)
    if imp_emerg and "Emergenze" in sheets:
     df=pd.read_excel(xls,"Emergenze")
     st.session_state.emerg=df.to_dict(orient="records")
     save_json(FM,st.session_state.emerg)
    st.success("Import OK")
    st.rerun()
  except Exception as e:
   st.error("Errore: "+str(e))