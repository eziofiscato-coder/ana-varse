import streamlit as st
import pandas as pd
from datetime import date, datetime
from io import BytesIO
import os, json, base64, tempfile, requests, hashlib

st.set_page_config(page_title="ANA Varese", page_icon="🟢", layout="wide")

st.markdown("""
<style>
.stApp{background:#e8f5e9!important;}
.main.block-container{background:white!important;border-radius:18px;padding:20px!important;}
[data-testid="stSidebar"]{background:#a5d6a7!important;border-right:4px solid #2e7d32!important;}
.stForm{background:#c8e6c9!important;border:3px solid #2e7d32!important;border-radius:15px!important;}
.stButton>button{background:#2e7d32!important;color:white!important;font-weight:bold!important;min-height:50px!important;border-radius:10px!important;font-size:16px!important;}
.backup-box{border:3px solid #2e7d32;border-radius:15px;padding:20px;background:#c8e6c9;margin:15px 0px;}
</style>
""", unsafe_allow_html=True)

def load_json(f, default):
    try:
        if os.path.exists(f):
            with open(f,"r",encoding="utf-8") as fh:
                return json.load(fh)
    except:
        pass
    return default

def save_json(f,d):
    try:
        with open(f,"w",encoding="utf-8") as fh:
            json.dump(d,fh,ensure_ascii=False,indent=2)
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

def img_to_b64(file):
    try:
        return base64.b64encode(file.getvalue()).decode()
    except:
        return ""

def reverse_geocode(lat, lon):
    try:
        url=f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=18&addressdetails=1"
        r=requests.get(url, headers={"User-Agent":"ANA-Varese-App"}, timeout=5)
        if r.status_code==200:
            data=r.json()
            addr=data.get("address",{})
            road=addr.get("road","") or ""
            house=addr.get("house_number","")
            via=f"{road} {house}".strip()
            if not via:
                via=data.get("display_name","").split(",")[0]
            comune=addr.get("city","") or addr.get("town","") or ""
            return via, comune
    except:
        pass
    return "", ""

def hash_pwd(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()

FILE_DATI="dati_volontari.json"
FILE_POST="postazioni.json"
FILE_ICONE="libreria_icone_condivisa.json"
FILE_UTENTI="utenti.json"
FILE_EVENTI="eventi.json"
FILE_RADIO="db_radio.json"
FILE_CHECKIN="checkin.json"
FILE_BROGLIACCIO="brogliaccio.json"
FILE_CONSEGNA="consegna_radio.json"
FILE_EMERGENZE="emergenze.json"

COMUNI=["Varese","Busto Arsizio","Gallarate","Saronno","Venegono Superiore","Venegono Inferiore","Castiglione Olona","Lozza","Tradate","Malnate","Luino","Altro"]

for k,v in [("dati",[]),("postazioni",[]),("icone_lib",[]),("utenti",[]),("eventi",[]),("radio",[]),("checkin",[]),("brogliaccio",[]),("consegna",[]),("emergenze",[]),("menu_scelta","Dashboard"),("map_lat",45.8205),("map_lon",8.8250),("map_via",""),("map_comune","Varese"),("map_logo","Default"),("authenticated",False),("ruolo",""),("username","")]:
    if k not in st.session_state:
        st.session_state[k]=v

if not st.session_state.dati: st.session_state.dati=load_json(FILE_DATI,[])
if not st.session_state.postazioni: st.session_state.postazioni=load_json(FILE_POST,[])
if not st.session_state.icone_lib: st.session_state.icone_lib=load_json(FILE_ICONE,[])
if not st.session_state.utenti: st.session_state.utenti=load_json(FILE_UTENTI,[])
if not st.session_state.eventi: st.session_state.eventi=load_json(FILE_EVENTI,[])
if not st.session_state.radio: st.session_state.radio=load_json(FILE_RADIO,[])
if not st.session_state.checkin: st.session_state.checkin=load_json(FILE_CHECKIN,[])
if not st.session_state.brogliaccio: st.session_state.brogliaccio=load_json(FILE_BROGLIACCIO,[])
if not st.session_state.consegna: st.session_state.consegna=load_json(FILE_CONSEGNA,[])
if not st.session_state.emergenze: st.session_state.emergenze=load_json(FILE_EMERGENZE,[])

if not st.session_state.utenti:
    st.session_state.utenti=[
        {"username":"admin","password":hash_pwd("ana2024"),"ruolo":"Amministratore","nome":"Admin"},
        {"username":"utente","password":hash_pwd("utente2024"),"ruolo":"Utente","nome":"Utente"}
    ]
    save_json(FILE_UTENTI,st.session_state.utenti)

def header_loghi():
    b64=get_b64("logo.png")
    if b64:
        st.markdown(f"<div style='display:flex;justify-content:center;align-items:center;gap:25px;background:#a5d6a7;padding:15px;border-radius:15px;border:3px solid #2e7d32;'><img src='data:image/png;base64,{b64}' style='width:80px;height:80px;border-radius:50%;'><h2 style='color:#0e7a3d;margin:0;text-align:center;'>VOLONTARIATO<br>Sezione di Varese</h2><img src='data:image/png;base64,{b64}' style='width:80px;height:80px;border-radius:50%;'></div>", unsafe_allow_html=True)
    else:
        st.markdown("<h2 style='text-align:center;color:#0e7a3d;'>VOLONTARIATO Sezione di Varese</h2>", unsafe_allow_html=True)

def torna_dashboard():
    if st.button("TORNA A DASHBOARD",use_container_width=True):
        st.session_state.menu_scelta="Dashboard"
        st.rerun()

if not st.session_state.authenticated:
    header_loghi()
    st.markdown("## LOGIN")
    st.info("Admin: admin / ana2024 | Utente: utente / utente2024")
    c1,c2,c3=st.columns([1,2,1])
    with c2:
        with st.form("login"):
            u=st.text_input("Username",value="admin")
            p=st.text_input("Password",type="password",value="ana2024")
            if st.form_submit_button("ACCEDI",use_container_width=True,type="primary"):
                pwd_hash=hash_pwd(p)
                trovato=None
                for ut in st.session_state.utenti:
                    if ut["username"]==u and ut["password"]==pwd_hash:
                        trovato=ut
                        break
                if trovato:
                    st.session_state.authenticated=True
                    st.session_state.ruolo=trovato["ruolo"]
                    st.session_state.username=trovato["username"]
                    st.rerun()
                else:
                    st.error("Username o password errati")
    st.stop()

header_loghi()
st.divider()

with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png",width=80)
    st.markdown(f"Ciao {st.session_state.username} | {st.session_state.ruolo}")
    st.markdown("### MENU COMPLETO FORM")
    if st.session_state.ruolo=="Amministratore":
        opzioni=["Dashboard","Volontari","Mappa Postazioni","Eventi","DB Radio","Check-In","Brogliaccio","Consegna Radio","Emergenze","Backup"]
    else:
        opzioni=["Dashboard","Volontari","Mappa Postazioni","Eventi","DB Radio","Check-In","Brogliaccio","Consegna Radio","Emergenze","Backup"]
    sel=st.radio("Vai a",opzioni,index=0)
    if sel!=st.session_state.menu_scelta:
        st.session_state.menu_scelta=sel
        st.rerun()
    st.divider()
    st.metric("Volontari",len(st.session_state.dati))
    st.metric("Postazioni",len(st.session_state.postazioni))
    st.metric("Emergenze",len(st.session_state.emergenze))
    if st.button("LOGOUT",use_container_width=True):
        st.session_state.authenticated=False
        st.rerun()

scelta=st.session_state.menu_scelta
MIME="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

# DASHBOARD SOLO TASTI MENU RAPIDO - SENZA QUADRATI VERDI
if scelta=="Dashboard":
    st.markdown("## DASHBOARD")
    c1,c2=st.columns([3,1])
    with c1:
        st.success(f"Benvenuto {st.session_state.username} | Ruolo: {st.session_state.ruolo}")
    with c2:
        if st.button("LOGOUT",use_container_width=True,type="primary",key="logout_dash"):
            st.session_state.authenticated=False
            st.rerun()
    st.divider()
    st.markdown("### MENU RAPIDO - TASTI")
    r1c1, r1c2, r1c3, r1c4 = st.columns(4)
    with r1c1:
        if st.button("VOLONTARI", use_container_width=True, key="rap_vol"):
            st.session_state.menu_scelta = "Volontari"
            st.rerun()
    with r1c2:
        if st.button("MAPPA POSTAZIONI", use_container_width=True, key="rap_mappa"):
            st.session_state.menu_scelta = "Mappa Postazioni"
            st.rerun()
    with r1c3:
        if st.button("EVENTI", use_container_width=True, key="rap_eventi"):
            st.session_state.menu_scelta = "Eventi"
            st.rerun()
    with r1c4:
        if st.button("DB RADIO", use_container_width=True, key="rap_radio"):
            st.session_state.menu_scelta = "DB Radio"
            st.rerun()
    r2c1, r2c2, r2c3, r2c4 = st.columns(4)
    with r2c1:
        if st.button("CHECK-IN", use_container_width=True, key="rap_check"):
            st.session_state.menu_scelta = "Check-In"
            st.rerun()
    with r2c2:
        if st.button("BROGLIACCIO", use_container_width=True, key="rap_brog"):
            st.session_state.menu_scelta = "Brogliaccio"
            st.rerun()
    with r2c3:
        if st.button("CONSEGNA RADIO", use_container_width=True, key="rap_consegna"):
            st.session_state.menu_scelta = "Consegna Radio"
            st.rerun()
    with r2c4:
        if st.button("EMERGENZE", use_container_width=True, key="rap_emerg"):
            st.session_state.menu_scelta = "Emergenze"
            st.rerun()
    r3c1, r3c2, r3c3, r3c4 = st.columns(4)
    with r3c1:
        if st.button("BACKUP", use_container_width=True, key="rap_backup"):
            st.session_state.menu_scelta = "Backup"
            st.rerun()

elif scelta=="Volontari":
    torna_dashboard()
    st.markdown("## FORM VOLONTARI")
    with st.form("form_vol"):
        c1,c2=st.columns(2)
        with c1:
            nome=st.text_input("Nome *"); cognome=st.text_input("Cognome *"); cell=st.text_input("Cellulare *")
        with c2:
            assoc=st.text_input("Associazione *",value="ANA Varese"); comune=st.selectbox("Comune",COMUNI,index=0); ruolo=st.selectbox("Ruolo *",["Volontario","Caposquadra","Coordinatore"])
        if st.form_submit_button("SALVA VOLONTARIO",use_container_width=True,type="primary"):
            if nome and cognome and cell and assoc:
                st.session_state.dati.append({"Nome":f"{nome} {cognome}","Associazione":assoc,"Cellulare":cell,"Comune":comune,"Ruolo":ruolo})
                save_json(FILE_DATI,st.session_state.dati); st.success(f"Salvato {nome} {cognome}"); st.rerun()
    if st.session_state.dati:
        st.dataframe(pd.DataFrame(st.session_state.dati),use_container_width=True)

elif scelta=="Mappa Postazioni":
    torna_dashboard()
    st.markdown("## FORM MAPPA POSTAZIONI")
    c1,c2=st.columns([2,1])
    with c1:
        try:
            import folium
            from streamlit_folium import st_folium
            m=folium.Map(location=[st.session_state.map_lat, st.session_state.map_lon], zoom_start=15)
            for p in st.session_state.postazioni:
                try:
                    lat_f=float(p.get("Latitudine")); lon_f=float(p.get("Longitudine"))
                    folium.Marker([lat_f, lon_f], popup=p.get("Postazione",""), icon=folium.Icon(color="green")).add_to(m)
                except:
                    pass
            map_data=st_folium(m,width=700,height=400,key="mappa_sel")
            if map_data and map_data.get("last_clicked"):
                lat_c=map_data["last_clicked"]["lat"]
                lon_c=map_data["last_clicked"]["lng"]
                st.session_state.map_lat=lat_c
                st.session_state.map_lon=lon_c
                via_auto, comune_auto=reverse_geocode(lat_c, lon_c)
                st.session_state.map_via=via_auto or f"{lat_c:.6f},{lon_c:.6f}"
                if comune_auto:
                    st.session_state.map_comune=comune_auto
                st.rerun()
        except Exception as e:
            st.error(f"Errore mappa selezione: {e}")
        try:
            import folium
            from streamlit_folium import st_folium
            lat_center=45.8205; lon_center=8.8250
            if st.session_state.postazioni:
                lats=[]; lons=[]
                for p in st.session_state.postazioni:
                    try:
                        lats.append(float(p.get("Latitudine"))); lons.append(float(p.get("Longitudine")))
                    except:
                        pass
                if lats and lons:
                    lat_center=sum(lats)/len(lats); lon_center=sum(lons)/len(lons)
            m2=folium.Map(location=[lat_center, lon_center], zoom_start=13)
            for p in st.session_state.postazioni:
                try:
                    lat_f=float(p.get("Latitudine")); lon_f=float(p.get("Longitudine"))
                    folium.Marker([lat_f, lon_f], popup=p.get("Postazione",""), icon=folium.Icon(color="red")).add_to(m2)
                except:
                    pass
            st_folium(m2,width=1000,height=650,key="mappa_anteprima")
        except Exception as e:
            st.error(f"Errore anteprima: {e}")
    with c2:
        st.info(f"Lat {st.session_state.map_lat:.6f} Lon {st.session_state.map_lon:.6f}")
        if st.session_state.map_via: st.success(f"Via: {st.session_state.map_via}")
        with st.form("form_post"):
            nome_post=st.text_input("Nome Postazione *",value=""); comune_post=st.selectbox("Comune *",COMUNI,index=COMUNI.index(st.session_state.map_comune) if st.session_state.map_comune in COMUNI else 0)
            via_post=st.text_input("Via",value=st.session_state.map_via); lat_post=st.text_input("Latitudine *",value=str(st.session_state.map_lat)); lon_post=st.text_input("Longitudine *",value=str(st.session_state.map_lon))
            if st.form_submit_button("SALVA POSTAZIONE",use_container_width=True,type="primary"):
                if nome_post and lat_post and lon_post:
                    new={"Postazione":nome_post,"Comune":comune_post,"Via":via_post,"Latitudine":lat_post,"Longitudine":lon_post,"Icona":st.session_state.map_logo}
                    st.session_state.postazioni.append(new); save_json(FILE_POST,st.session_state.postazioni); st.success(f"Salvata {nome_post}"); st.rerun()
    if st.session_state.postazioni:
        st.dataframe(pd.DataFrame(st.session_state.postazioni),use_container_width=True)

elif scelta=="Eventi":
    torna_dashboard(); st.markdown("## FORM EVENTI")
    with st.form("form_eventi"):
        nome_evento=st.text_input("Nome Evento *"); data_evento=st.date_input("Data Evento *",value=date.today()); luogo=st.text_input("Luogo *"); descrizione=st.text_area("Descrizione")
        if st.form_submit_button("SALVA EVENTO",use_container_width=True,type="primary"):
            if nome_evento and luogo:
                st.session_state.eventi.append({"Evento":nome_evento,"Data":str(data_evento),"Luogo":luogo,"Descrizione":descrizione}); save_json(FILE_EVENTI,st.session_state.eventi); st.success(f"Evento {nome_evento} salvato"); st.rerun()
    if st.session_state.eventi: st.dataframe(pd.DataFrame(st.session_state.eventi),use_container_width=True)

elif scelta=="DB Radio":
    torna_dashboard(); st.markdown("## FORM DB RADIO")
    with st.form("form_radio"):
        id_radio=st.text_input("ID Radio *"); modello=st.text_input("Modello *"); frequenza=st.text_input("Frequenza"); stato=st.selectbox("Stato",["Disponibile","In uso","In riparazione"])
        if st.form_submit_button("SALVA RADIO",use_container_width=True,type="primary"):
            if id_radio and modello:
                st.session_state.radio.append({"ID":id_radio,"Modello":modello,"Frequenza":frequenza,"Stato":stato}); save_json(FILE_RADIO,st.session_state.radio); st.success(f"Radio {id_radio} salvata"); st.rerun()
    if st.session_state.radio: st.dataframe(pd.DataFrame(st.session_state.radio),use_container_width=True)

elif scelta=="Emergenze":
    torna_dashboard(); st.markdown("## FORM EMERGENZE")
    with st.form("form_emergenze"):
        c1,c2=st.columns(2)
        with c1:
            tipo_emergenza=st.selectbox("Tipo Emergenza *",["Alluvione","Incendio Boschivo","Terremoto","Frana","Neve/Ghiaccio","Ricerca Disperso","Supporto Sanitario","Altro"])
            livello=st.selectbox("Livello *",["Verde - Preallerta","Giallo - Attenzione","Arancione - Preallarme","Rosso - Allarme"])
            data_emerg=st.date_input("Data Emergenza *",value=date.today()); ora_emerg=st.time_input("Ora Segnalazione *",value=datetime.now().time())
        with c2:
            comune_emerg=st.selectbox("Comune *",COMUNI,index=0); via_emerg=st.text_input("Via/Localita *"); coordinatore=st.text_input("Coordinatore *"); squadre=st.number_input("N. Squadre",min_value=1,max_value=50,value=1)
        descrizione_emerg=st.text_area("Descrizione Emergenza *"); azioni=st.text_area("Azioni Intraprese")
        if st.form_submit_button("SALVA EMERGENZA",use_container_width=True,type="primary"):
            if via_emerg and descrizione_emerg and coordinatore:
                st.session_state.emergenze.append({"Tipo":tipo_emergenza,"Livello":livello,"Data":str(data_emerg),"Ora":str(ora_emerg),"Comune":comune_emerg,"Via":via_emerg,"Coordinatore":coordinatore,"Squadre":squadre,"Descrizione":descrizione_emerg,"Azioni":azioni})
                save_json(FILE_EMERGENZE,st.session_state.emergenze); st.success(f"Emergenza {tipo_emergenza} salvata!"); st.rerun()
            else:
                st.error("Compila i campi *")
    if st.session_state.emergenze:
        st.dataframe(pd.DataFrame(st.session_state.emergenze),use_container_width=True)

elif scelta=="Check-In":
    torna_dashboard(); st.markdown("## FORM CHECK-IN")
    with st.form("form_checkin"):
        volontario=st.selectbox("Volontario",[d.get("Nome","") for d in st.session_state.dati] if st.session_state.dati else ["Nessun volontario"])
        postazione=st.selectbox("Postazione",[p.get("Postazione","") for p in st.session_state.postazioni] if st.session_state.postazioni else ["Nessuna postazione"])
        ora_arrivo=st.time_input("Ora Arrivo",value=datetime.now().time()); note=st.text_input("Note")
        if st.form_submit_button("SALVA CHECK-IN",use_container_width=True,type="primary"):
            st.session_state.checkin.append({"Volontario":volontario,"Postazione":postazione,"Ora":str(ora_arrivo),"Note":note,"Data":str(date.today())}); save_json(FILE_CHECKIN,st.session_state.checkin); st.success("Check-In salvato"); st.rerun()
    if st.session_state.checkin: st.dataframe(pd.DataFrame(st.session_state.checkin),use_container_width=True)

elif scelta=="Brogliaccio":
    torna_dashboard(); st.markdown("## FORM BROGLIACCIO")
    with st.form("form_brogliaccio"):
        ora=st.time_input("Ora",value=datetime.now().time()); mittente=st.text_input("Mittente *"); destinatario=st.text_input("Destinatario *"); messaggio=st.text_area("Messaggio *"); priorita=st.selectbox("Priorita",["Normale","Urgente","Emergenza"])
        if st.form_submit_button("SALVA BROGLIACCIO",use_container_width=True,type="primary"):
            if mittente and destinatario and messaggio:
                st.session_state.brogliaccio.append({"Ora":str(ora),"Data":str(date.today()),"Mittente":mittente,"Destinatario":destinatario,"Messaggio":messaggio,"Priorita":priorita}); save_json(FILE_BROGLIACCIO,st.session_state.brogliaccio); st.success("Messaggio salvato"); st.rerun()
    if st.session_state.brogliaccio: st.dataframe(pd.DataFrame(st.session_state.brogliaccio),use_container_width=True)

elif scelta=="Consegna Radio":
    torna_dashboard(); st.markdown("## FORM CONSEGNA RADIO")
    with st.form("form_consegna"):
        radio_id=st.selectbox("ID Radio",[r.get("ID","") for r in st.session_state.radio] if st.session_state.radio else ["Nessuna radio"])
        volontario=st.selectbox("Consegnata a",[d.get("Nome","") for d in st.session_state.dati] if st.session_state.dati else ["Nessun volontario"])
        data_consegna=st.date_input("Data Consegna",value=date.today()); ora_consegna=st.time_input("Ora Consegna",value=datetime.now().time()); stato_consegna=st.selectbox("Stato",["Consegnata","Restituita","Persa"])
        if st.form_submit_button("SALVA CONSEGNA",use