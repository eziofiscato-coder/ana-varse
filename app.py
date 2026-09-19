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
    st.markdown("<div class='foot'>"+img+"<span>by Ezio F. vers. 1.0 2026</span></div>",unsafe_allow_html=True)

FD="dati.json"
FU="utenti.json"
FP="post.json"
FE="eventi.json"
FR="radio.json"
FC="check.json"
FB="brog.json"
FO="consegna.json"
FM="emerg.json"
COM=["Varese","Busto Arsizio","Gallarate","Saronno","Venegono","Altro"]

for k in ["dati","post","eventi","radio","check","brog","consegna","emerg"]:
    if k not in st.session_state:
        st.session_state[k]=[]

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
        h="<div style='text-align:center;background:#a5d6a7;padding:15px;border-radius:15px;border:3px solid #2e7d32;'><img src='data:image/png;base64,"+b+"' style='width:80px;border-radius:50%;'><h2 style='color:#0e7a3d;'>VOLONTARIATO<br>Sezione di Varese</h2></div>"
        st.markdown(h,unsafe_allow_html=True)
    else:
        st.markdown("<h2 style='text-align:center;color:#0e7a3d;'>VOLONTARIATO Varese</h2>",unsafe_allow_html=True)

def torna():
    if st.button("TORNA A DASHBOARD",use_container_width=True):
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
    opts=["Dashboard","Volontari","Mappa Postazioni","Eventi","DB Radio","Check-In","Brogliaccio","Consegna Radio","Emergenze","Backup"]
    sel=st.radio("Vai a",opts,index=0)
    if sel!=st.session_state.menu:
        st.session_state.menu=sel
        st.rerun()
    if st.button("LOGOUT",use_container_width=True):
        st.session_state.auth=False
        st.rerun()

scelta=st.session_state.menu

if scelta=="Dashboard":
    st.markdown("## DASHBOARD - MENU RAPIDO")
    st.success("Benvenuto")
    c1,c2,c3,c4=st.columns(4)
    with c1:
        if st.button("VOLONTARI",use_container_width=True,key="d1"):
            st.session_state.menu="Volontari"
            st.rerun()
    with c2:
        if st.button("MAPPA",use_container_width=True,key="d2"):
            st.session_state.menu="Mappa Postazioni"
            st.rerun()
    with c3:
        if st.button("EVENTI",use_container_width=True,key="d3"):
            st.session_state.menu="Eventi"
            st.rerun()
    with c4:
        if st.button("RADIO",use_container_width=True,key="d4"):
            st.session_state.menu="DB Radio"
            st.rerun()
    c1,c2,c3,c4=st.columns(4)
    with c1:
        if st.button("CHECK-IN",use_container_width=True,key="d5"):
            st.session_state.menu="Check-In"
            st.rerun()
    with c2:
        if st.button("BROGLIACCIO",use_container_width=True,key="d6"):
            st.session_state.menu="Brogliaccio"
            st.rerun()
    with c3:
        if st.button("CONSEGNA",use_container_width=True,key="d7"):
            st.session_state.menu="Consegna Radio"
            st.rerun()
    with c4:
        if st.button("EMERGENZE",use_container_width=True,key="d8"):
            st.session_state.menu="Emergenze"
            st.rerun()
    if st.button("BACKUP",use_container_width=True,key="d9"):
        st.session_state.menu="Backup"
        st.rerun()
    footer()

elif scelta=="Volontari":
    torna()
    st.markdown("## VOLONTARI - 5 SOTTOMASCHERE")
    t1,t2,t3,t4,t5=st.tabs(["1 ANAGRAFICA","2 RESIDENZA","3 TESSERA","4 ABILIT","5 NOTE"])
    with t1:
        st.markdown('<div class="sub">',unsafe_allow_html=True)
        with st.form("f1"):
            a1=st.text_input("Nome *",key="a1")
            a2=st.text_input("Cognome *",key="a2")
            a3=st.text_input("CF",key="a3")
            a4=st.date_input("Data Nascita",value=date(1980,1,1),key="a4")
            st.session_state["s1"]={"nome":a1,"cogn":a2,"cf":a3,"dn":str(a4)}
            st.form_submit_button("SALVA 1")
        st.markdown('</div>',unsafe_allow_html=True)
    with t2:
        st.markdown('<div class="sub">',unsafe_allow_html=True)
        with st.form("f2"):
            b1=st.text_input("Via *",key="b1")
            b2=st.selectbox("Comune",COM,key="b2")
            b3=st.text_input("Cell *",key="b3")
            b4=st.text_input("Email",key="b4")
            st.session_state["s2"]={"via":b1,"com":b2,"cell":b3,"email":b4}
            st.form_submit_button("SALVA 2")
        st.markdown('</div>',unsafe_allow_html=True)
    with t3:
        st.markdown('<div class="sub">',unsafe_allow_html=True)
        with st.form("f3"):
            c1x=st.text_input("Tessera ANA",key="c1")
            c2x=st.text_input("Sezione",value="Varese",key="c2")
            c3x=st.selectbox("Ruolo",["Volontario","Caposquadra","Coordinatore"],key="c3")
            c4x=st.text_input("Associazione",value="ANA Varese",key="c4")
            st.session_state["s3"]={"tess":c1x,"ruolo":c3x,"ass":c4x}
            st.form_submit_button("SALVA 3")
        st.markdown('</div>',unsafe_allow_html=True)
    with t4:
        st.markdown('<div class="sub">',unsafe_allow_html=True)
        with st.form("f4"):
            d1=st.multiselect("Patenti",["A","B","C","D"],key="d1x")
            d2=st.selectbox("Corso Base",["Si","No"],key="d2x")
            d3=st.selectbox("Radio",["Nessuno","Base","Avanzato"],key="d3x")
            st.session_state["s4"]={"pat":",".join(d1),"base":d2,"radio":d3}
            st.form_submit_button("SALVA 4")
        st.markdown('</div>',unsafe_allow_html=True)
    with t5:
        st.markdown('<div class="sub">',unsafe_allow_html=True)
        with st.form("f5"):
            e1=st.multiselect("Disp",["Lun","Mar","Mer","Gio","Ven","Sab","Dom"],key="e1")
            e2=st.text_area("Note",key="e2")
            btn=st.form_submit_button("SALVA COMPLETO",use_container_width=True)
            if btn:
                s1=st.session_state.get("s1",{})
                s2=st.session_state.get("s2",{})
                s3=st.session_state.get("s3",{})
                if s1.get("nome") and s2.get("cell"):
                    nuovo={
                        "Nome":s1.get("nome")+" "+s1.get("cogn"),
                        "Cell":s2.get("cell"),
                        "Comune":s2.get("com"),
                        "Ruolo":s3.get("ruolo"),
                        "Ass":s3.get("ass"),
                        "Note":e2
                    }
                    st.session_state.dati.append(nuovo)
                    save_json(FD,st.session_state.dati)
                    st.success("Salvato")
                    st.rerun()
        st.markdown('</div>',unsafe_allow_html=True)
    if st.session_state.dati:
        st.dataframe(pd.DataFrame(st.session_state.dati),use_container_width=True)

elif scelta=="Mappa Postazioni":
    torna()
    st.markdown("## FORM MAPPA POSTAZIONI")
    with st.form("form_post"):
        p1=st.text_input("Nome Postazione *")
        p2=st.selectbox("Comune",COM)
        p3=st.text_input("Via")
        p4=st.text_input("Latitudine",value="45.8205")
        p5=st.text_input("Longitudine",value="8.8250")
        ok=st.form_submit_button("SALVA POSTAZIONE",use_container_width=True)
        if ok and p1:
            nuovo={"Postazione":p1,"Comune":p2,"Via":p3,"Lat":p4,"Lon":p5}
            st.session_state.post.append(nuovo)
            save_json(FP,st.session_state.post)
            st.success("Salvata")
            st.rerun()
    if st.session_state.post:
        st.dataframe(pd.DataFrame(st.session_state.post),use_container_width=True)

elif scelta=="Eventi":
    torna()
    st.markdown("## FORM EVENTI")
    with st.form("form_eventi"):
        e1=st.text_input("Nome Evento *")
        e2=st.date_input("Data",value=date.today())
        e3=st.text_input("Luogo *")
        e4=st.text_area("Descrizione")
        ok=st.form_submit_button("SALVA EVENTO",use_container_width=True)
        if ok and e1:
            nuovo={"Evento":e1,"Data":str(e2),"Luogo":e3,"Desc":e4}
            st.session_state.eventi.append(nuovo)
            save_json(FE,st.session_state.eventi)
            st.success("Salvato")
            st.rerun()
    if st.session_state.eventi:
        st.dataframe(pd.DataFrame(st.session_state.eventi),use_container_width=True)

elif scelta=="DB Radio":
    torna()
    st.markdown("## FORM DB RADIO")
    with st.form("form_radio"):
        r1=st.text_input("ID Radio *")
        r2=st.text_input("Modello *")
        r3=st.text_input("Frequenza")
        r4=st.selectbox("Stato",["Disponibile","In uso","Riparazione"])
        ok=st.form_submit_button("SALVA RADIO",use_container_width=True)
        if ok and r1:
            nuovo={"ID":r1,"Modello":r2,"Freq":r3,"Stato":r4}
            st.session_state.radio.append(nuovo)
            save_json(FR,st.session_state.radio)
            st.success("Salvata")
            st.rerun()
    if st.session_state.radio:
        st.dataframe(pd.DataFrame(st.session_state.radio),use_container_width=True)

elif scelta=="Check-In":
    torna()
    st.markdown("## FORM CHECK-IN")
    with st.form("form_check"):
        nomi=[d.get("Nome","") for d in st.session_state.dati]
        if not nomi:
            nomi=["Nessun volontario"]
        v1=st.selectbox("Volontario",nomi)
        p1=st.text_input("Postazione")
        ora=st.time_input("Ora Arrivo",value=datetime.now().time())
        ok=st.form_submit_button("SALVA CHECK-IN",use_container_width=True)
        if ok:
            nuovo={"Volontario":v1,"Postazione":p1,"Ora":str(ora),"Data":str(date.today())}
            st.session_state.check.append(nuovo)
            save_json(FC,st.session_state.check)
            st.success("Salvato")
            st.rerun()
    if st.session_state.check:
        st.dataframe(pd.DataFrame(st.session_state.check),use_container_width=True)

elif scelta=="Brogliaccio":
    torna()
    st.markdown("## FORM BROGLIACCIO")
    with st.form("form_brog"):
        b1=st.text_input("Mittente *")
        b2=st.text_input("Destinatario *")
        b3=st.text_area("Messaggio *")
        ok=st.form_submit_button("SALVA BROGLIACCIO",use_container_width=True)
        if ok and b1 and b3:
            nuovo={"Mittente":b1,"Dest":b2,"Mess":b3,"Data":str(date.today())}
            st.session_state.brog.append(nuovo)
            save_json(FB,st.session_state.brog)
            st.success("Salvato")
            st.rerun()
    if st.session_state.brog:
        st.dataframe(pd.DataFrame(st.session_state.brog),use_container_width=True)

elif scelta=="Consegna Radio":
    torna()
    st.markdown("## FORM CONSEGNA RADIO")
    with st.form("form_consegna"):
        ids=[r.get("ID","") for r in st.session_state.radio]
        if not ids:
            ids=["Nessuna radio"]
        c1=st.selectbox("ID Radio",ids)
        nomi=[d.get("Nome","") for d in st.session_state.dati]
        if not nomi:
            nomi=["Nessun volontario"]
        c2=st.selectbox("Consegnata a",nomi)
        ok=st.form_submit_button("SALVA CONSEGNA",use_container_width=True)
        if ok:
            nuovo={"Radio":c1,"Volontario":c2,"Data":str(date.today())}
            st.session_state.consegna.append(nuovo)
            save_json(FO,st.session_state.consegna)
            st.success("Salvata")
            st.rerun()
    if st.session_state.consegna:
        st.dataframe(pd.DataFrame(st.session_state.consegna),use_container_width=True)

elif scelta=="Emergenze":
    torna()
    st.markdown("## FORM EMERGENZE")
    with st.form("form_emerg"):
        em1=st.selectbox("Tipo",["Alluvione","Incendio","Terremoto","Frana","Neve","Ricerca","Altro"])
        em2=st.selectbox("Comune",COM)
        em3=st.text_input("Via/Localita *")
        em4=st.text_input("Coordinatore *")
        em5=st.text_area("Descrizione *")
        ok=st.form_submit_button("SALVA EMERGENZA",use_container_width=True)
        if ok and em3 and em5:
            nuovo={"Tipo":em1,"Comune":em2,"Via":em3,"Coord":em4,"Desc":em5}
            st.session_state.emerg.append(nuovo)
            save_json(FM,st.session_state.emerg)
            st.success("Salvata")
            st.rerun()
    if st.session_state.emerg:
        st.dataframe(pd.DataFrame(st.session_state.emerg),use_container_width=True)

elif scelta=="Backup":
    torna()
    st.markdown("## BACKUP")
    if st.button("CREA BACKUP GENERALE",use_container_width=True):
        out=BytesIO()
        with pd.ExcelWriter(out,engine="openpyxl") as writer:
            pd.DataFrame(st.session_state.dati).to_excel(writer,sheet_name="Volontari",index=False)
            pd.DataFrame(st.session_state.post).to_excel(writer,sheet_name="Postazioni",index=False)
            pd.DataFrame(st.session_state.eventi).to_excel(writer,sheet_name="Eventi",index=False)
            pd.DataFrame(st.session_state.radio).to_excel(writer,sheet_name="Radio",index=False)
        st.session_state["bk"]=out.getvalue()
        st.success("Backup creato")
    if "bk" in st.session_state:
        st.download_button("SCARICA BACKUP",st.session_state["bk"],file_name="BACKUP.xlsx",mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",use_container_width=True)