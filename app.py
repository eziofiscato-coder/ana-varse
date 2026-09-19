import streamlit as st
import pandas as pd
from datetime import date, datetime
from io import BytesIO
import os, json, base64, hashlib

st.set_page_config(page_title="ANA Varese", layout="wide")

st.markdown("""
<style>
.stApp{background:#e8f5e9!important;}
.block-container{background:white!important;border-radius:18px;padding:20px!important;padding-bottom:95px!important;}
[data-testid="stSidebar"]{background:#a5d6a7!important;border-right:4px solid #2e7d32!important;}
.stForm{background:#c8e6c9!important;border:3px solid #2e7d32!important;border-radius:15px!important;}
.stButton>button{background:#2e7d32!important;color:white!important;font-weight:bold!important;min-height:50px!important;border-radius:10px!important;}
.sub{border:2px solid #2e7d32;border-radius:12px;padding:15px;background:#f1f8e9;margin:10px 0px;}
.foot{position:fixed;bottom:5px;left:10px;background:white;border:2px solid #2e7d32;border-radius:12px;padding:5px 12px;display:flex;align-items:center;gap:8px;z-index:9999;}
.foot img{width:45px;height:45px;border-radius:50%;border:2px solid #2e7d32;}
.foot span{font-size:13px;font-weight:bold;color:#2e7d32;}
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
    st.markdown("<div class='foot'>"+img+"<span>by Ezio F. 2026</span></div>",unsafe_allow_html=True)

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
        st.markdown("<h2 style='text-align:center;color:green;'>VOLONTARIATO Varese</h2>",unsafe_allow_html=True)

def torna():
    if st.button("TORNA",use_container_width=True):
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
            ok=st.form_submit_button("ACCEDI",use_container_width=True)
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
    opts=["Dashboard","Volontari","Mappa","Eventi","Radio","Check","Brogliaccio","Consegna","Emergenze","Backup"]
    sel=st.radio("Vai a",opts,index=0)
    if sel!=st.session_state.menu:
        st.session_state.menu=sel
        st.rerun()
    if st.button("LOGOUT",use_container_width=True):
        st.session_state.auth=False
        st.rerun()

scelta=st.session_state.menu

if scelta=="Dashboard":
    st.markdown("## DASHBOARD")
    st.success("Verde OK")
    if st.button("VOLONTARI",use_container_width=True,key="d1"):
        st.session_state.menu="Volontari"
        st.rerun()
    if st.button("MAPPA",use_container_width=True,key="d2"):
        st.session_state.menu="Mappa"
        st.rerun()
    if st.button("EVENTI",use_container_width=True,key="d3"):
        st.session_state.menu="Eventi"
        st.rerun()
    if st.button("RADIO",use_container_width=True,key="d4"):
        st.session_state.menu="Radio"
        st.rerun()
    if st.button("CHECK-IN",use_container_width=True,key="d5"):
        st.session_state.menu="Check"
        st.rerun()
    if st.button("BROGLIACCIO",use_container_width=True,key="d6"):
        st.session_state.menu="Brogliaccio"
        st.rerun()
    if st.button("CONSEGNA",use_container_width=True,key="d7"):
        st.session_state.menu="Consegna"
        st.rerun()
    if st.button("EMERGENZE",use_container_width=True,key="d8"):
        st.session_state.menu="Emergenze"
        st.rerun()
    if st.button("BACKUP",use_container_width=True,key="d9"):
        st.session_state.menu="Backup"
        st.rerun()
    footer()

elif scelta=="Volontari":
    torna()
    st.markdown("## VOLONTARI")
    t1,t2,t3,t4,t5=st.tabs(["1","2","3","4","5"])
    with t1:
        st.markdown("### 1 ANAGRAFICA")
        with st.form("f1"):
            a1=st.text_input("Nome *",key="a1")
            a2=st.text_input("Cognome *",key="a2")
            a3=st.text_input("CF",key="a3")
            a4=st.date_input("Nascita",value=date(1980,1,1),key="a4")
            if st.form_submit_button("SALVA"):
                st.session_state.s1_nome=a1
                st.session_state.s1_cogn=a2
                st.session_state.s1_cf=a3
                st.session_state.s1_dn=str(a4)
                st.success("OK 1")
    with t2:
        st.markdown("### 2 RESIDENZA")
        with st.form("f2"):
            b1=st.text_input("Via *",key="b1")
            b2=st.text_input("Comune *",value="Varese",key="b2")
            b3=st.text_input("Cell *",key="b3")
            if st.form_submit_button("SALVA"):
                st.session_state.s2_via=b1
                st.session_state.s2_com=b2
                st.session_state.s2_cell=b3
                st.success("OK 2")
    with t3:
        st.markdown("### 3 TESSERA")
        with st.form("f3"):
            c1x=st.text_input("Tessera",key="c1")
            c2x=st.text_input("Ruolo",value="Volontario",key="c3")
            if st.form_submit_button("SALVA"):
                st.session_state.s3_tess=c1x
                st.session_state.s3_ruolo=c2x
                st.success("OK 3")
    with t4:
        st.markdown("### 4 ABILIT")
        with st.form("f4"):
            d1=st.text_input("Patenti",value="B",key="d1")
            d2=st.text_input("Base",value="Si",key="d2")
            if st.form_submit_button("SALVA"):
                st.session_state.s4_pat=d1
                st.success("OK 4")
    with t5:
        st.markdown("### 5 NOTE")
        with st.form("f5"):
            e2=st.text_area("Note",key="e2")
            btn=st.form_submit_button("SALVA COMPLETO",use_container_width=True)
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
                    st.success("OK")
                    st.rerun()
    if st.session_state.dati:
        st.dataframe(pd.DataFrame(st.session_state.dati),use_container_width=True)

elif scelta=="Mappa":
    torna()
    st.markdown("## MAPPA - OSM GOOGLE WAZE")
    with st.form("form_mappa"):
        m1=st.text_input("Nome *",key="m1")
        m2=st.text_input("Comune *",value="Varese",key="m2")
        m3=st.text_input("Via *",key="m3")
        m5=st.text_input("Lat",value="45.8205",key="m5")
        m6=st.text_input("Lon",value="8.8250",key="m6")
        m7=st.text_input("Tipo",value="Presidio",key="m7")
        m9=st.text_area("Note",key="m9")
        st.markdown("### ICONA")
        icona=st.file_uploader("Icona PNG/JPG",type=["png","jpg","jpeg"])
        nome_icona=""
        if icona:
            nome_icona=icona.name
            st.image(icona,width=100)
        cerca=st.text_input("Cerca",value="Varese",key="cerca")
        ok=st.form_submit_button("SALVA",use_container_width=True)
        if ok and m1:
            nuovo={}
            nuovo["Postazione"]=m1
            nuovo["Comune"]=m2
            nuovo["Via"]=m3
            nuovo["Lat"]=m5
            nuovo["Lon"]=m6
            nuovo["Tipo"]=m7
            nuovo["Icona"]=nome_icona
            st.session_state.post.append(nuovo)
            save_json(FP,st.session_state.post)
            st.success("OK")
            st.rerun()
    if st.session_state.post:
        df=pd.DataFrame(st.session_state.post)
        st.dataframe(df,use_container_width=True)
        for p in st.session_state.post:
            lat=p.get("Lat","45.8205")
            lon=p.get("Lon","8.8250")
            nome=p.get("Postazione","Post")
            st.markdown("**"+nome+"**")
            c1,c2,c3=st.columns(3)
            with c1:
                osm="https://www.openstreetmap.org/?mlat="+lat+"&mlon="+lon
                st.link_button("OSM",osm,use_container_width=True)
            with c2:
                gmap="https://www.google.com/maps?q="+lat+","+lon
                st.link_button("Google",gmap,use_container_width=True)
            with c3:
                waze="https://waze.com/ul?ll="+lat+","+lon
                st.link_button("Waze",waze,use_container_width=True)
        try:
            lat_list=[]
            lon_list=[]
            for p in st.session_state.post:
                lat=float(p.get("Lat","45.8205"))
                lon=float(p.get("Lon","8.8250"))
                lat_list.append(lat)
                lon_list.append(lon)
            if lat_list:
                df_map=pd.DataFrame({"lat":lat_list,"lon":lon_list})
                st.map(df_map)
        except:
            pass

elif scelta=="Check":
    torna()
    st.markdown("## CHECK-IN")
    with st.form("form_check"):
        nomi=[d.get("Nome","") for d in st.session_state.dati]
        if not nomi:
            nomi=["Nessun volontario"]
        ch1=st.selectbox("Volontario",nomi,key="ch1")
        ch2=st.text_input("Postazione",key="ch2")
        ch3=st.time_input("Ora",value=datetime.now().time(),key="ch3")
        ch4=st.date_input("Data",value=date.today(),key="ch4")
        ch5=st.text_input("Mezzo",key="ch5")
        ch6=st.text_input("Radio",key="ch6")
        ch7=st.text_area("Note",key="ch7")
        ok=st.form_submit_button("SALVA",use_container_width=True)
        if ok:
            nuovo={}
            nuovo["Vol"]=ch1
            nuovo["Post"]=ch2
            nuovo["Ora"]=str(ch3)
            nuovo["Data"]=str(ch4)
            nuovo["Mezzo"]=ch5
            nuovo["Radio"]=ch6
            nuovo["Note"]=ch7
            st.session_state.check.append(nuovo)
            save_json(FC,st.session_state.check)
            st.success("OK")
            st.rerun()
    if st.session_state.check:
        st.dataframe(pd.DataFrame(st.session_state.check),use_container_width=True)

elif scelta=="Brogliaccio":
    torna()
    st.markdown("## BROGLIACCIO")
    with st.form("form_brog"):
        b1=st.text_input("Mittente *",key="br1")
        b2=st.text_input("Dest *",key="br2")
        b3=st.text_input("Canale",key="br3")
        b4=st.time_input("Ora",value=datetime.now().time(),key="br4")
        b5=st.date_input("Data",value=date.today(),key="br5")
        b7=st.text_area("Messaggio *",key="br7")
        b8=st.text_area("Risposta",key="br8")
        ok=st.form_submit_button("SALVA",use_container_width=True)
        if ok and b1 and b7:
            nuovo={}
            nuovo["Mitt"]=b1
            nuovo["Dest"]=b2
            nuovo["Canale"]=b3
            nuovo["Ora"]=str(b4)
            nuovo["Data"]=str(b5)
            nuovo["Mess"]=b7
            nuovo["Risp"]=b8
            st.session_state.brog.append(nuovo)
            save_json(FB,st.session_state.brog)
            st.success("OK")
            st.rerun()
    if st.session_state.brog:
        st.dataframe(pd.DataFrame(st.session_state.brog),use_container_width=True)

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
        co5=st.text_input("Stato",value="Consegnata",key="co5")
        co7=st.text_area("Note",key="co7")
        ok=st.form_submit_button("SALVA",use_container_width=True)
        if ok:
            nuovo={}
            nuovo["Radio"]=co1
            nuovo["Vol"]=co2
            nuovo["Data"]=str(co3)
            nuovo["Ora"]=str(co4)
            nuovo["Stato"]=co5
            nuovo["Note"]=co7
            st.session_state.consegna.append(nuovo)
            save_json(FO,st.session_state.consegna)
            st.success("OK")
            st.rerun()
    if st.session_state.consegna:
        st.dataframe(pd.DataFrame(st.session_state.consegna),use_container_width=True)

elif scelta=="Eventi":
    torna()
    st.markdown("## EVENTI")
    with st.form("form_ev"):
        e1=st.text_input("Nome *")
        e2=st.date_input("Data",value=date.today())
        e3=st.text_input("Luogo *")
        e4=st.text_area("Desc")
        ok=st.form_submit_button("SALVA",use_container_width=True)
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
        st.dataframe(pd.DataFrame(st.session_state.eventi),use_container_width=True)

elif scelta=="Radio":
    torna()
    st.markdown("## RADIO")
    with st.form("form_ra"):
        r1=st.text_input("ID *")
        r2=st.text_input("Modello *")
        r3=st.text_input("Freq",value="446.00625")
        ok=st.form_submit_button("SALVA",use_container_width=True)
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
        st.dataframe(pd.DataFrame(st.session_state.radio),use_container_width=True)

elif scelta=="Emergenze":
    torna()
    st.markdown("## EMERGENZE")
    with st.form("form_em"):
        em1=st.text_input("Tipo",value="Alluvione")
        em2=st.text_input("Comune",value="Varese")
        em3=st.text_input("Via *")
        em4=st.text_input("Coord *")
        em5=st.text_area("Desc *")
        ok=st.form_submit_button("SALVA",use_container_width=True)
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
        st.dataframe(pd.DataFrame(st.session_state.emerg),use_container_width=True)

elif scelta=="Backup":
    torna()
    st.markdown("## BACKUP")
    if st.button("CREA BACKUP",use_container_width=True):
        out=BytesIO()
        with pd.ExcelWriter(out,engine="openpyxl") as writer:
            if st.session_state.dati:
                pd.DataFrame(st.session_state.dati).to_excel(writer,sheet_name="Vol",index=False)
            if st.session_state.post:
                pd.DataFrame(st.session_state.post).to_excel(writer,sheet_name="Mappa",index=False)
            if st.session_state.check:
                pd.DataFrame(st.session_state.check).to_excel(writer,sheet_name="Check",index=False)
            if st.session_state.brog:
                pd.DataFrame(st.session_state.brog).to_excel(writer,sheet_name="Brog",index=False)
            if st.session_state.consegna:
                pd.DataFrame(st.session_state.consegna).to_excel(writer,sheet_name="Consegna",index=False)
        st.session_state["bk"]=out.getvalue()
        st.success("OK")
    if "bk" in st.session_state:
        st.download_button("SCARICA",st.session_state["bk"],file_name="BACKUP.xlsx",mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",use_container_width=True)