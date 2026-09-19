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
.submask{border:2px solid #2e7d32;border-radius:12px;padding:15px;background:#f1f8e9;margin:10px 0px;}
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
def trova_b64_logo(nome, libreria):
    for ic in libreria:
        if ic.get("nome")==nome and ic.get("b64"):
            return ic.get("b64")
    return None
def salva_icona_temp(b64, nome):
    try:
        data=base64.b64decode(b64)
        tmp=os.path.join(tempfile.gettempdir(), f"icon_{nome}.png")
        with open(tmp,"wb") as f:
            f.write(data)
        return tmp
    except:
        return None
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

for k,v in [("dati",[]),("postazioni",[]),("icone_lib",[]),("utenti",[]),("eventi",[]),("radio",[]),("checkin",[]),("brogliaccio",[]),("consegna",[]),("emergenze",[]),("menu_scelta","Dashboard"),("map_lat",45.8205),("map_lon",8.8250),("map_via",""),("map_comune","Varese"),("map_logo","Default"),("authenticated",False),("ruolo",""),("username",""),("sel_form_backup",""),("sel_import","")]:
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
            st.session_state.menu_scelta="Volontari"; st.rerun()
    with r1c2:
        if st.button("MAPPA POSTAZIONI", use_container_width=True, key="rap_mappa"):
            st.session_state.menu_scelta="Mappa Postazioni"; st.rerun()
    with r1c3:
        if st.button("EVENTI", use_container_width=True, key="rap_eventi"):
            st.session_state.menu_scelta="Eventi"; st.rerun()
    with r1c4:
        if st.button("DB RADIO", use_container_width=True, key="rap_radio"):
            st.session_state.menu_scelta="DB Radio"; st.rerun()
    r2c1, r2c2, r2c3, r2c4 = st.columns(4)
    with r2c1:
        if st.button("CHECK-IN", use_container_width=True, key="rap_check"):
            st.session_state.menu_scelta="Check-In"; st.rerun()
    with r2c2:
        if st.button("BROGLIACCIO", use_container_width=True, key="rap_brog"):
            st.session_state.menu_scelta="Brogliaccio"; st.rerun()
    with r2c3:
        if st.button("CONSEGNA RADIO", use_container_width=True, key="rap_consegna"):
            st.session_state.menu_scelta="Consegna Radio"; st.rerun()
    with r2c4:
        if st.button("EMERGENZE", use_container_width=True, key="rap_emerg"):
            st.session_state.menu_scelta="Emergenze"; st.rerun()
    r3c1, r3c2, r3c3, r3c4 = st.columns(4)
    with r3c1:
        if st.button("BACKUP", use_container_width=True, key="rap_backup"):
            st.session_state.menu_scelta="Backup"; st.rerun()

elif scelta=="Volontari":
    torna_dashboard()
    st.markdown("## FORM VOLONTARI - CON SOTTOMASCHERE")
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["SOTTOMASCHERA 1: ANAGRAFICA","SOTTOMASCHERA 2: RESIDENZA E CONTATTI","SOTTOMASCHERA 3: TESSERAMENTO ANA","SOTTOMASCHERA 4: ABILITAZIONI E CORSI","SOTTOMASCHERA 5: DISPONIBILITA E NOTE"])
    with tab1:
        st.markdown('<div class="submask">', unsafe_allow_html=True)
        st.markdown("### SOTTOMASCHERA 1 - DATI ANAGRAFICI")
        with st.form("form_anagrafica"):
            c1,c2=st.columns(2)
            with c1:
                nome=st.text_input("Nome *",key="vol_nome"); cognome=st.text_input("Cognome *",key="vol_cognome"); cf=st.text_input("Codice Fiscale",key="vol_cf"); data_nascita=st.date_input("Data di Nascita",value=date(1980,1,1),key="vol_datanasc")
            with c2:
                luogo_nascita=st.text_input("Luogo di Nascita",key="vol_luogonasc"); sesso=st.selectbox("Sesso",["M","F"],key="vol_sesso"); stato_civile=st.selectbox("Stato Civile",["Celibe/Nubile","Coniugato/a","Vedovo/a","Separato/a"],key="vol_statociv"); gruppo_sanguigno=st.selectbox("Gruppo Sanguigno",["Non noto","A+","A-","B+","B-","AB+","AB-","0+","0-"],key="vol_grupposang")
            st.session_state["tmp_anagrafica"]={"nome":nome,"cognome":cognome,"cf":cf,"data_nascita":str(data_nascita),"luogo_nascita":luogo_nascita,"sesso":sesso,"stato_civile":stato_civile,"gruppo_sanguigno":gruppo_sanguigno}
            st.form_submit_button("SALVA ANAGRAFICA TEMP")
        st.markdown('</div>', unsafe_allow_html=True)
    with tab2:
        st.markdown('<div class="submask">', unsafe_allow_html=True)
        st.markdown("### SOTTOMASCHERA 2 - RESIDENZA E CONTATTI")
        with st.form("form_residenza"):
            c1,c2=st.columns(2)
            with c1:
                via_res=st.text_input("Via e Numero Civico *",key="vol_via"); comune_res=st.selectbox("Comune Residenza *",COMUNI,index=0,key="vol_comune_res"); cap=st.text_input("CAP",value="21100",key="vol_cap"); provincia=st.text_input("Provincia",value="VA",key="vol_prov")
            with c2:
                cell=st.text_input("Cellulare *",key="vol_cell"); tel_fisso=st.text_input("Telefono Fisso",key="vol_telfisso"); email=st.text_input("Email",key="vol_email"); contatto_emerg=st.text_input("Contatto Emergenza - Nome e Tel",key="vol_cont_emerg")
            st.session_state["tmp_residenza"]={"via":via_res,"comune":comune_res,"cap":cap,"provincia":provincia,"cell":cell,"tel_fisso":tel_fisso,"email":email,"contatto_emerg":contatto_emerg}
            st.form_submit_button("SALVA RESIDENZA TEMP")
        st.markdown('</div>', unsafe_allow_html=True)
    with tab3:
        st.markdown('<div class="submask">', unsafe_allow_html=True)
        st.markdown("### SOTTOMASCHERA 3 - TESSERAMENTO ANA")
        with st.form("form_tesseramento"):
            c1,c2=st.columns(2)
            with c1:
                tessera_ana=st.text_input("Numero Tessera ANA",key="vol_tessera"); sezione=st.text_input("Sezione ANA",value="Varese",key="vol_sezione"); gruppo=st.text_input("Gruppo",key="vol_gruppo"); anno_iscrizione=st.number_input("Anno Iscrizione ANA",min_value=1950,max_value=2030,value=2020,key="vol_annoisc")
            with c2:
                ruolo_ana=st.selectbox("Ruolo ANA",["Alpino","Amico degli Alpini","Aggregato","Volontario PC"],key="vol_ruoloana"); ruolo_pc=st.selectbox("Ruolo Protezione Civile *",["Volontario","Caposquadra","Coordinatore","Autista","Radio","Logistica","Segreteria","Sanitario","Altro"],key="vol_ruolopc"); associazione=st.text_input("Associazione *",value="ANA Varese",key="vol_assoc"); scadenza_visita=st.date_input("Scadenza Visita Medica",value=date.today(),key="vol_scadvisita")
            st.session_state["tmp_tesseramento"]={"tessera":tessera_ana,"sezione":sezione,"gruppo":gruppo,"anno":anno_iscrizione,"ruolo_ana":ruolo_ana,"ruolo_pc":ruolo_pc,"associazione":associazione,"scadenza_visita":str(scadenza_visita)}
            st.form_submit_button("SALVA TESSERAMENTO TEMP")
        st.markdown('</div>', unsafe_allow_html=True)
    with tab4:
        st.markdown('<div class="submask">', unsafe_allow_html=True)
        st.markdown("### SOTTOMASCHERA 4 - ABILITAZIONI E CORSI")
        with st.form("form_abilitazioni"):
            c1,c2=st.columns(2)
            with c1:
                patente=st.multiselect("Patenti",["A","B","C","D","E","BE","CE","CQC","Nautica"],key="vol_patente"); corso_base_pc=st.selectbox("Corso Base PC",["Si - Conseguito","No","In corso"],key="vol_corsobase"); corso_antincendio=st.selectbox("Antincendio Boschivo",["Nessuno","AIB Base","AIB Caposquadra","AIB Coordinatore"],key="vol_aib"); corso_primo_soccorso=st.selectbox("Primo Soccorso",["Nessuno","Base","BLSD","PSTI"],key="vol_ps")
            with c2:
                corso_radio=st.selectbox("Corso Radio",["Nessuno","Base","Avanzato"],key="vol_corsoradio"); corso_motosega=st.selectbox("Motosega",["Nessuno","Base","Avanzato"],key="vol_motosega"); corso_cinofilo=st.selectbox("Unita Cinofila",["No","Si"],key="vol_cinofilo"); altre_abilitazioni=st.text_area("Altre Abilitazioni",key="vol_altreabil")
            st.session_state["tmp_abilitazioni"]={"patente":",".join(patente),"corso_base_pc":corso_base_pc,"aib":corso_antincendio,"primo_soccorso":corso_primo_soccorso,"corso_radio":corso_radio,"motosega":corso_motosega,"cinofilo":corso_cinofilo,"altre":altre_abilitazioni}
            st.form_submit_button("SALVA ABILITAZIONI TEMP")
        st.markdown('</div>', unsafe_allow_html=True)
    with tab5:
        st.markdown('<div class="submask">', unsafe_allow_html=True)
        st.markdown("### SOTTOMASCHERA 5 - DISPONIBILITA E NOTE")
        with st.form("form_disponibilita"):
            disp_settimana=st.multiselect("Disponibilita Settimana",["Lunedi","Martedi","Mercoledi","Giovedi","Venerdi","Sabato","Domenica"],key="vol_disp_sett"); disp_orario=st.selectbox("Fascia Oraria Preferita",["Mattina","Pomeriggio","Sera","Notte","H24"],key="vol_fascia"); disp_emergenza=st.selectbox("Disponibile per Emergenze",["Si - Sempre","Si - Solo locali","No"],key="vol_disp_emerg"); taglia_divisa=st.selectbox("Taglia Divisa",["S","M","L","XL","XXL","XXXL"],key="vol_taglia"); note=st.text_area("Note Aggiuntive",key="vol_note")
            if st.form_submit_button("SALVA VOLONTARIO COMPLETO - UNISCE TUTTE LE SOTTOMASCHERE",use_container_width=True,type="primary"):
                ana=st.session_state.get("tmp_anagrafica",{}); res=st.session_state.get("tmp_residenza",{}); tess=st.session_state.get("tmp_tesseramento",{}); abil=st.session_state.get("tmp_abilitazioni",{})
                if ana.get("nome") and ana.get("cognome") and res.get("cell") and tess.get("associazione"):
                    nuovo={"Nome":f"{ana.get('nome')} {ana.get('cognome')}","Cognome":ana.get("cognome"),"Nome_Batt":ana.get("nome"),"CF":ana.get("cf"),"Data_Nascita":ana.get("data_nascita"),"Luogo_Nascita":ana.get("luogo_nascita"),"Sesso":ana.get("sesso"),"Gruppo_Sanguigno":ana.get("gruppo_sanguigno"),"Via":res.get("via"),"Comune":res.get("comune"),"CAP":res.get("cap"),"Provincia":res.get("provincia"),"Cellulare":res.get("cell"),"Telefono":res.get("tel_fisso"),"Email":res.get("email"),"Contatto_Emergenza":res.get("contatto_emerg"),"Tessera_ANA":tess.get("tessera"),"Sezione":tess.get("sezione"),"Gruppo_ANA":tess.get("gruppo"),"Ruolo":tess.get("ruolo_pc"),"Ruolo_ANA":tess.get("ruolo_ana"),"Associazione":tess.get("associazione"),"Scadenza_Visita":tess.get("scadenza_visita"),"Patenti":abil.get("patente"),"Corso_Base_PC":abil.get("corso_base_pc"),"AIB":abil.get("aib"),"Primo_Soccorso":abil.get("primo_soccorso"),"Corso_Radio":abil.get("corso_radio"),"Motosega":abil.get("motosega"),"Cinofilo":abil.get("cinofilo"),"Altre_Abil":abil.get("altre"),"Disponibilita":",".join(disp_settimana),"Fascia_Oraria":disp_orario,"Disp_Emergenza":disp_emergenza,"Taglia_Divisa":taglia_divisa,"Note":note}
                    st.session_state.dati.append(nuovo); save_json(FILE_DATI,st.session_state.dati); st.success(f"Volontario {ana.get('nome')} {ana.get('cognome')} salvato con tutte le 5 sottomaschere! Dati mantenuti in memoria."); st.rerun()
                else:
                    st.error("Compila almeno Nome, Cognome, Cellulare, Associazione nelle sottomaschere 1-2-3")
        st.markdown('</div>', unsafe_allow_html=True)
    st.divider()
    st.markdown("### ELENCO VOLONTARI - TUTTI I DATI IN MEMORIA")
    if st.session_state.dati:
        df=pd.DataFrame(st.session_state.dati); st.dataframe(df,use_container_width=True)
        out=BytesIO(); df.to_excel(out,index=False,engine="openpyxl")
        st.download_button("SCARICA EXCEL VOLONTARI COMPLETO", out.getvalue(), file_name=f"VOLONTARI_COMPLETO_{date.today()}.xlsx", mime=MIME, use_container_width=True)
    else:
        st.info("Nessun volontario in memoria - i dati precedenti sono mantenuti in memoria se presenti in dati_volontari.json")

elif scelta=="Mappa Postazioni":
    torna_dashboard()
    st.markdown("## FORM MAPPA POSTAZIONI - LIBRERIA CONDIVISA")
    uploaded=st.file_uploader("CARICA LOGO PNG - LIBRERIA CONDIVISA CON EMERGENZE", type=["png","jpg","jpeg"], key="up_logo")
    if uploaded:
        b64=img_to_b64(uploaded); nome_icona=st.text_input("Nome logo", value=uploaded.name.split(".")[0], key="nome_logo_map")
        if st.button("SALVA LOGO IN LIBRERIA CONDIVISA",use_container_width=True,type="primary"):
            st.session_state.icone_lib.append({"nome":nome_icona,"b64":b64}); save_json(FILE_ICONE,st.session_state.icone_lib); st.success(f"Logo {nome_icona} salvato in libreria condivisa! Disponibile anche in Emergenze. Dati mantenuti in memoria."); st.rerun()
    if st.session_state.icone_lib:
        st.markdown("### LIBRERIA ICONE CONDIVISA - MAPPA + EMERGENZE")
        cols=st.columns(6)
        for i, ic in enumerate(st.session_state.icone_lib):
            with cols[i%6]:
                if ic.get("b64"):
                    st.image(f"data:image/png;base64,{ic['b64']}",width=40); st.write(f"{ic['nome']}")
    st.divider()
    c1,c2=st.columns([2,1])
    with c1:
        try:
            import folium
            from streamlit_folium import st_folium
            m=folium.Map(location=[st.session_state.map_lat, st.session_state.map_lon], zoom_start=15)
            for idx_p, p in enumerate(st.session_state.postazioni):
                try:
                    lat_f=float(p.get('Latitudine')); lon_f=float(p.get('Longitudine')); logo_nome=p.get('Icona',''); b64=trova_b64_logo(logo_nome, st.session_state.icone_lib)
                    if b64:
                        tmp_path=salva_icona_temp(b64, f"sel_{logo