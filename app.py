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
FI="icone.json"

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
if "icone" not in st.session_state:
    st.session_state.icone={}
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
st.session_state.icone=load_json(FI,{})

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
    opts=["Dashboard","Volontari","Mappa","Eventi","Radio","Check","Brogliaccio","Consegna","Emergenze","Backup"]
    sel=st.radio("Vai a",opts,index=0)
    if sel!=st.session_state.menu:
        st.session_state.menu=sel
        st.rerun()
    if st.button("LOGOUT"):
        st.session_state.auth=False
        st.rerun()

scelta=st.session_state.menu

if scelta=="Dashboard":
    st.markdown("## DASHBOARD")
    st.success("Verde OK")
    if st.button("VOLONTARI"):
        st.session_state.menu="Volontari"
        st.rerun()
    if st.button("MAPPA"):
        st.session_state.menu="Mappa"
        st.rerun()
    if st.button("CHECK"):
        st.session_state.menu="Check"
        st.rerun()
    if st.button("BACKUP"):
        st.session_state.menu="Backup"
        st.rerun()
    footer()

elif scelta=="Volontari":
    torna()
    st.markdown("## VOLONTARI - 5 MASCHERE")
    t1,t2,t3,t4,t5=st.tabs(["1","2","3","4","5"])
    with t1:
        with st.form("f1"):
            a1=st.text_input("Nome *",key="a1")
            a2=st.text_input("Cognome *",key="a2")
            a3=st.text_input("CF",key="a3")
            a4=st.date_input("Nascita",value=date(1980,1,1),key="a4")
            if st.form_submit_button("SALVA"):
                st.session_state.s1_nome=a1
                st.session_state.s1_cogn=a2
                st.session_state.s1_dn=str(a4)
                st.success("OK 1")
    with t2:
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
        with st.form("f3"):
            c1x=st.text_input("Tessera",key="c1")
            c2x=st.text_input("Ruolo",value="Volontario",key="c3")
            if st.form_submit_button("SALVA"):
                st.session_state.s3_tess=c1x
                st.session_state.s3_ruolo=c2x
                st.success("OK 3")
    with t4:
        with st.form("f4"):
            d1=st.text_input("Patenti",value="B",key="d1")
            d2=st.text_input("Base",value="Si",key="d2")
            if st.form_submit_button("SALVA"):
                st.session_state.s4_pat=d1
                st.success("OK 4")
    with t5:
        with st.form("f5"):
            e2=st.text_area("Note",key="e2")
            btn=st.form_submit_button("SALVA")
            if btn:
                nome=st.session_state.get("s1_nome","")
                cogn=st.session_state.get("s1_cogn","")
                cell=st.session_state.get("s2_cell","")
                com=st.session_state.get("s2_com","")
                ruolo=st.session_state.get("s3_ruolo","")
                if nome and cell:
                    r=dict(Nome=nome+" "+cogn,Cell=cell,Comune=com,Ruolo=ruolo,Note=e2)
                    st.session_state.dati.append(r)
                    save_json(FD,st.session_state.dati)
                    st.success("OK")
                    st.rerun()
    if st.session_state.dati:
        st.dataframe(pd.DataFrame(st.session_state.dati))

elif scelta=="Mappa":
    torna()
    st.markdown("## MAPPA - ANTEPRIMA + LOGO")
    st.markdown("### 1 - MAPPA INSERIMENTO")
    col1,col2=st.columns([2,1])
    with col1:
        lat_in=st.number_input("Lat",value=float(st.session_state.lat_tmp),format="%.6f")
        lon_in=st.number_input("Lon",value=float(st.session_state.lon_tmp),format="%.6f")
        st.session_state.lat_tmp=lat_in
        st.session_state.lon_tmp=lon_in
        df_tmp=pd.DataFrame(dict(lat=[lat_in],lon=[lon_in]))
        st.map(df_tmp,zoom=14)
    with col2:
        cerca=st.text_input("Cerca",value="Varese")
        tipo=st.selectbox("Tipo",["OSM","Google","Waze"])
    st.markdown("### 2 - DATI + LOGO")
    with st.form("form_mappa"):
        col1,col2=st.columns(2)
        with col1:
            m1=st.text_input("Nome *",key="m1")
            m2=st.text_input("Comune *",value="Varese",key="m2")
            m3=st.text_input("Via *",key="m3")
            m7=st.text_input("Tipo",value="Presidio",key="m7")
        with col2:
            m5=st.text_input("Lat",value=str(st.session_state.lat_tmp),key="m5")
            m6=st.text_input("Lon",value=str(st.session_state.lon_tmp),key="m6")
            m8=st.text_input("Resp",key="m8")
        m9=st.text_area("Note",key="m9")
        icona=st.file_uploader("Logo",type=["png","jpg","jpeg"])
        nome_icona=""
        b64_icona=""
        if icona:
            nome_icona=icona.name
            b64_icona=base64.b64encode(icona.read()).decode()
            st.image(BytesIO(base64.b64decode(b64_icona)),width=120)
        ok=st.form_submit_button("SALVA CON LOGO")
        if ok and m1:
            r=dict(Postazione=m1,Comune=m2,Via=m3,Lat=m5,Lon=m6,Tipo=m7,Icona=nome_icona)
            st.session_state.post.append(r)
            if b64_icona:
                st.session_state.icone=b64_icona
                save_json(FI,st.session_state.icone)
            save_json(FP,st.session_state.post)
            st.success("OK")
            st.rerun()
    if st.session_state.post:
        st.divider()
        st.markdown("## 3 - ANTEPRIMA CON LOGHI")
        try:
            lat_list=[]
            lon_list=[]
            for p in st.session_state.post:
                lat=float(p.get("Lat","45.8205"))
                lon=float(p.get("Lon","8.8250"))
                lat_list.append(lat)
                lon_list.append(lon)
            if lat_list:
                df_map=pd.DataFrame(dict(lat=lat_list,lon=lon_list))
                st.map(df_map,zoom=11)
        except:
            pass
        df=pd.DataFrame(st.session_state.post)
        st.dataframe(df)
        for p in st.session_state.post:
            lat=p.get("Lat","45.8205")
            lon=p.get("Lon","8.8250")
            nome=p.get("Postazione","Post")
            icona_nome=p.get("Icona","")
            st.markdown("---")
            c1,c2=st.columns([1,2])
            with c1:
                if nome in st.session_state.icone:
                    try:
                        b64=st.session_state.icone[nome]
                        st.image(BytesIO(base64.b64decode(b64)),width=80)
                    except:
                        st.markdown(icona_nome)
                else:
                    st.markdown(icona_nome)
            with c2:
                st.markdown("**"+nome+"**")
                osm="https://www.openstreetmap.org/?mlat="+lat+"&mlon="+lon
                st.link_button("OSM",osm)
                gmap="https://www.google.com/maps?q="+lat+","+lon
                st.link_button("Google",gmap)
                waze="https://waze.com/ul?ll="+lat+","+lon
                st.link_button("Waze",waze)

elif scelta=="Check":
    torna()
    st.markdown("## CHECK-IN")
    with st.form("form_check"):
        nomi=[d.get("Nome","") for d in st.session_state.dati]
        if not nomi:
            nomi=["Nessun volontario"]
        ch1=st.selectbox("Vol",nomi)
        ch2=st.text_input("Post")
        ch3=st.time_input("Ora",value=datetime.now().time())
        ch4=st.date_input("Data",value=date.today())
        ch7=st.text_area("Note")
        ok=st.form_submit_button("SALVA")
        if ok:
            r=dict(Vol=ch1,Post=ch2,Ora=str(ch3),Data=str(ch4),Note=ch7)
            st.session_state.check.append(r)
            save_json(FC,st.session_state.check)
            st.success("OK")
            st.rerun()
    if st.session_state.check:
        st.dataframe(pd.DataFrame(st.session_state.check))

elif scelta=="Brogliaccio":
    torna()
    st.markdown("## BROGLIACCIO")
    with st.form("form_brog"):
        b1=st.text_input("Mitt *")
        b2=st.text_input("Dest *")
        b7=st.text_area("Mess *")
        b4=st.time_input("Ora",value=datetime.now().time())
        b5=st.date_input("Data",value=date.today())
        ok=st.form_submit_button("SALVA")
        if ok and b1 and b7:
            r=dict(Mitt=b1,Dest=b2,Ora=str(b4),Data=str(b5),Mess=b7)
            st.session_state.brog.append(r)
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
        co1=st.selectbox("ID Radio",ids)
        nomi=[d.get("Nome","") for d in st.session_state.dati]
        if not nomi:
            nomi=["Nessun volontario"]
        co2=st.selectbox("A",nomi)
        co3=st.date_input("Data",value=date.today())
        co4=st.time_input("Ora",value=datetime.now().time())
        ok=st.form_submit_button("SALVA")
        if ok:
            r=dict(Radio=co1,Vol=co2,Data=str(co3),Ora=str(co4))
            st.session_state.consegna.append(r)
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
            r=dict(Evento=e1,Data=str(e2),Luogo=e3,Desc=e4)
            st.session_state.eventi.append(r)
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
            r=dict(ID=r1,Mod=r2,Freq=r3)
            st.session_state.radio.append(r)
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
            r=dict(Tipo=em1,Comune=em2,Via=em3,Coord=em4,Desc=em5)
            st.session_state.emerg.append(r)
            save_json(FM,st.session_state.emerg)
            st.success("OK")
            st.rerun()
    if st.session_state.emerg:
        st.dataframe(pd.DataFrame(st.session_state.emerg))

elif scelta=="Backup":
    torna()
    st.markdown("## BACKUP - IMPORT EXPORT PER FORM")

    # BACKUP COMPLETO CON IMPORT EXPORT PER OGNI FORM - COME STAMATTINA
    st.markdown("### 1 - BACKUP COMPLETO")

    if st.button("CREA BACKUP COMPLETO"):
        out=BytesIO()
        with pd.ExcelWriter(out,engine="openpyxl") as writer:
            if st.session_state.dati:
                pd.DataFrame(st.session_state.dati).to_excel(writer,sheet_name="Volontari",index=False)
            if st.session_state.post:
                pd.DataFrame(st.session_state.post).to_excel(writer,sheet_name="Mappa",index=False)
            if st.session_state.check:
                pd.DataFrame(st.session_state.check).to_excel(writer,sheet_name="CheckIn",index=False)
            if st.session_state.brog:
                pd.DataFrame(st.session_state.brog).to_excel(writer,sheet_name="Brogliaccio",index=False)
            if st.session_state.consegna:
                pd.DataFrame(st.session_state.consegna).to_excel(writer,sheet_name="Consegna",index=False)
            if st.session_state.eventi:
                pd.DataFrame(st.session_state.eventi).to_excel(writer,sheet_name="Eventi",index=False)
            if st.session_state.radio:
                pd.DataFrame(st.session_state.radio).to_excel(writer,sheet_name="Radio",index=False)
            if st.session_state.emerg:
                pd.DataFrame(st.session_state.emerg).to_excel(writer,sheet_name="Emergenze",index=False)
        st.session_state["bk"]=out.getvalue()
        st.success("Backup completo OK")

    if "bk" in st.session_state:
        st.download_button("SCARICA BACKUP COMPLETO",st.session_state["bk"],file_name="BACKUP_COMPLETO.xlsx",mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    st.divider()
    st.markdown("### 2 - EXPORT PER FORM")

    c1,c2=st.columns(2)
    with c1:
        if st.session_state.dati:
            out=BytesIO()
            pd.DataFrame(st.session_state.dati).to_excel(out,index=False,engine="openpyxl")
            st.download_button("Export Volontari",out.getvalue(),file_name="volontari.xlsx",mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        if st.session_state.post:
            out=BytesIO()
            pd.DataFrame(st.session_state.post).to_excel(out,index=False,engine="openpyxl")
            st.download_button("Export Mappa",out.getvalue(),file_name="mappa.xlsx",mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        if st.session_state.check:
            out=BytesIO()
            pd.DataFrame(st.session_state.check).to_excel(out,index=False,engine="openpyxl")
            st.download_button("Export CheckIn",out.getvalue(),file_name="checkin.xlsx",mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        if st.session_state.brog:
            out=BytesIO()
            pd.DataFrame(st.session_state.brog).to_excel(out,index=False,engine="openpyxl")
            st.download_button("Export Brogliaccio",out.getvalue(),file_name="brogliaccio.xlsx",mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    with c2:
        if st.session_state.consegna:
            out=BytesIO()
            pd.DataFrame(st.session_state.consegna).to_excel(out,index=False,engine="openpyxl")
            st.download_button("Export Consegna",out.getvalue(),file_name="consegna.xlsx",mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        if st.session_state.eventi:
            out=BytesIO()
            pd.DataFrame(st.session_state.eventi).to_excel(out,index=False,engine="openpyxl")
            st.download_button("Export Eventi",out.getvalue(),file_name="eventi.xlsx",mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        if st.session_state.radio:
            out=BytesIO()
            pd.DataFrame(st.session_state.radio).to_excel(out,index=False,engine="openpyxl")
            st.download_button("Export Radio",out.getvalue(),file_name="radio.xlsx",mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        if st.session_state.emerg:
            out=BytesIO()
            pd.DataFrame(st.session_state.emerg).to_excel(out,index=False,engine="openpyxl")
            st.download_button("Export Emergenze",out.getvalue(),file_name="emergenze.xlsx",mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    st.divider()
    st.markdown("### 3 - IMPORT PER FORM")

    c1,c2=st.columns(2)
    with c1:
        st.markdown("**Import Volontari**")
        up1=st.file_uploader("Import Volontari XLSX",type=["xlsx"],key="up_vol")
        if up1:
            try:
                df=pd.read_excel(up1)
                st.session_state.dati=df.to_dict(orient="records")
                save_json(FD,st.session_state.dati)
                st.success("Import Volontari OK")
            except:
                st.error("Errore import")

        st.markdown("**Import Mappa**")
        up2=st.file_uploader("Import Mappa XLSX",type=["xlsx"],key="up_mappa")
        if up2:
            try:
                df=pd.read_excel(up2)
                st.session_state.post=df.to_dict(orient="records")
                save_json(FP,st.session_state.post)
                st.success("Import Mappa OK")
            except:
                st.error("Errore import")

        st.markdown("**Import CheckIn**")
        up3=st.file_uploader("Import CheckIn XLSX",type=["xlsx"],key="up_check")
        if up3:
            try:
                df=pd.read_excel(up3)
                st.session_state.check=df.to_dict(orient="records")
                save_json(FC,st.session_state.check)
                st.success("Import CheckIn OK")
            except:
                st.error("Errore import")

        st.markdown("**Import Brogliaccio**")
        up4=st.file_uploader("Import Brogliaccio XLSX",type=["xlsx"],key="up_brog")
        if up4:
            try:
                df=pd.read_excel(up4)
                st.session_state.brog=df.to_dict(orient="records")
                save_json(FB,st.session_state.brog)
                st.success("Import Brogliaccio OK")
            except:
                st.error("Errore import")

    with c2:
        st.markdown("**Import Consegna**")
        up5=st.file_uploader("Import Consegna XLSX",type=["xlsx"],key="up_cons")
        if up5:
            try:
                df=pd.read_excel(up5)
                st.session_state.consegna=df.to_dict(orient="records")
                save_json(FO,st.session_state.consegna)
                st.success("Import Consegna OK")
            except:
                st.error("Errore import")

        st.markdown("**Import Eventi**")
        up6=st.file_uploader("Import Eventi XLSX",type=["xlsx"],key="up_ev")
        if up6:
            try:
                df=pd.read_excel(up6)
                st.session_state.eventi=df.to_dict(orient="records")
                save_json(FE,st.session_state.eventi)
                st.success("Import Eventi OK")
            except:
                st.error("Errore import")

        st.markdown("**Import Radio**")
        up7=st.file_uploader("Import Radio XLSX",type=["xlsx"],key="up_radio")
        if up7:
            try:
                df=pd.read_excel(up7)
                st.session_state.radio=df.to_dict(orient="records")
                save_json(FR,st.session_state.radio)
                st.success("Import Radio OK")
            except:
                st.error("Errore import")

        st.markdown("**Import Emergenze**")
        up8=st.file_uploader("Import Emergenze XLSX",type=["xlsx"],key="up_emerg")
        if up8:
            try:
                df=pd.read_excel(up8)
                st.session_state.emerg=df.to_dict(orient="records")
                save_json(FM,st.session_state.emerg)
                st.success("Import Emergenze OK")
            except:
                st.error("Errore import")