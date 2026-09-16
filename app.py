
import streamlit as st
import pandas as pd
from datetime import datetime, date
import json
from io import BytesIO
import zipfile
st.set_page_config(page_title="ANA Varese 12 Form + Loghi", layout="wide")
APP_PASSWORD="ANA2025"
for k,v in [("authenticated",False),("dashboard_entered",False),("interventi_lista",[]),("eventi",[]),("mem_nomi",["Mario Rossi","Luigi Bianchi"]),("radio_db",[]),("dist_radio",[]),("postazioni",[]),("brogliaccio",[]),("registro_radio",[]),("volontari_full",[]),("checkin",{})]:
    if k not in st.session_state:
        st.session_state[k]=v

# LOGO ANA + STILE
LOGO_HTML = '''
<div style='display:flex; align-items:center; background:#a5d6a7; padding:10px; border-radius:12px; border:3px solid #2e7d32; margin-bottom:10px;'>
<div style='background:#2e7d32; color:white; width:60px; height:60px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-weight:bold; font-size:24px; margin-right:15px;'>ANA</div>
<div><h2 style='margin:0; color:#1b5e20;'>ANA Varese - Protezione Civile</h2><small style='color:#2e7d32;'>Sezione Varese | Volontariato Alpino | Sistema Gestionale</small></div>
</div>
'''

st.markdown('''
<style>
.stApp{background-color:#e8f5e9!important;}
.stForm{background-color:#a5d6a7!important; border:3px solid #2e7d32!important; border-radius:15px!important; padding:20px!important;}
[data-testid="stDataFrame"]{background:white!important; border:3px solid #2e7d32!important; border-radius:12px!important;}
.stButton>button{background:#d32f2f!important; color:white!important; border:3px solid #b71c1c!important; font-weight:bold!important; border-radius:10px!important;}
div[data-testid="stFormSubmitButton"]>button{background:#d32f2f!important; color:white!important;}
</style>
''', unsafe_allow_html=True)

if not st.session_state.authenticated:
    st.markdown(LOGO_HTML, unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center; color:#2e7d32;'>🔐 Accesso Riservato</h3>", unsafe_allow_html=True)
    c1,c2,c3=st.columns([1,2,1])
    with c2:
        with st.form("login"):
            pwd=st.text_input("Password", type="password", placeholder="ANA2025")
            if st.form_submit_button("ACCEDI", use_container_width=True, type="primary"):
                if pwd==APP_PASSWORD:
                    st.session_state.authenticated=True
                    st.rerun()
                else:
                    st.error("Errata")
        st.info("Password: ANA2025")
    st.stop()

if not st.session_state.dashboard_entered:
    st.markdown(LOGO_HTML, unsafe_allow_html=True)
    c1,c2,c3=st.columns([1,2,1])
    with c2:
        st.success("Accesso autorizzato")
        if st.button("ENTRA IN DASHBOARD", use_container_width=True, type="primary"):
            st.session_state.dashboard_entered=True
            st.rerun()
    st.stop()

with st.sidebar:
    st.markdown(LOGO_HTML, unsafe_allow_html=True)
    scelta=st.radio("MENU 12 FORM", ["Dashboard","Eventi","Check-In","Volontari","Radio DB","Distribuzione","Postazioni","Interventi","Brogliaccio","📝 Registro Radio","💾 Backup","🔗 Link"])
    st.divider()
    if st.button("Home", use_container_width=True):
        st.session_state.dashboard_entered=False
        st.rerun()
    if st.button("Logout", use_container_width=True):
        st.session_state.authenticated=False
        st.session_state.dashboard_entered=False
        st.rerun()

def header_con_logo(titolo):
    st.markdown(LOGO_HTML, unsafe_allow_html=True)
    st.markdown(f"<h3 style='color:#1b5e20; background:#a5d6a7; padding:10px; border-radius:10px; border:2px solid #2e7d32;'>{titolo} - Loghi su tutti i fogli</h3>", unsafe_allow_html=True)

def tasto_dash(k):
    c1,c2=st.columns(2)
    with c1:
        if st.button("Dashboard", key=f"d_{k}", use_container_width=True):
            st.rerun()
    with c2:
        if st.button("Home", key=f"h_{k}", use_container_width=True):
            st.session_state.dashboard_entered=False
            st.rerun()

if scelta=="🏠 Dashboard":
    header_con_logo("🏠 Dashboard Centrale")
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Interventi", len(st.session_state.interventi_lista))
    c2.metric("Eventi", len(st.session_state.eventi))
    c3.metric("Volontari", len(st.session_state.mem_nomi))
    c4.metric("Radio", len(st.session_state.radio_db))
    if st.session_state.interventi_lista:
        st.markdown("#### 📋 Interventi con Logo")
        df=pd.DataFrame(st.session_state.interventi_lista)
        # Aggiungi colonna logo
        df.insert(0, "Logo ANA", ["🟢 ANA" for _ in range(len(df))])
        st.dataframe(df, use_container_width=True)
    tasto_dash("dash")

elif scelta=="Interventi":
    header_con_logo("Interventi Emergenza")
    ICONE={"🔥 Incendio":"🔥","🌊 Alluvione":"🌊","❄️ Neve":"❄️","⛰️ Frana":"⛰️","🔍 Ricerca":"🔍","👥 Supporto":"👥","👁️ Monitoraggio":"👁️","🚨 Altro":"🚨"}
    t1,t2=st.tabs(["📝 Nuovo - Via+Civico + Icona","Elenco con Loghi"])
    with t1:
        with st.form("form_int", clear_on_submit=True):
            st.markdown(LOGO_HTML, unsafe_allow_html=True)
            c1,c2=st.columns(2)
            with c1:
                comune=st.text_input("Comune *", placeholder="Varese")
                via_civico=st.text_input("Via + Civico *", placeholder="Via Roma 15")
                resp=st.text_input("Responsabile *")
            with c2:
                tipo_icona=st.selectbox("Tipo con Icona *", list(ICONE.keys()))
                priorita=st.selectbox("Priorità", ["Bassa","Media","Alta","Critica"])
                stato=st.selectbox("Stato", ["In Corso","Completato","In Attesa"])
            azione=st.text_area("Azione *", height=100)
            if st.form_submit_button("SALVA CON ICONA", use_container_width=True, type="primary"):
                if comune and via_civico and azione and resp:
                    icona=ICONE[tipo_icona]
                    st.session_state.interventi_lista.append({
                        "ID":len(st.session_state.interventi_lista)+1,
                        "Logo":"ANA Varese",
                        "Icona":icona,
                        "Tipo":tipo_icona,
                        "Comune":comune,
                        "Via + Civico":via_civico,
                        "Responsabile":resp,
                        "Priorità":priorita,
                        "Stato":stato,
                        "Azione":azione,
                        "Data":str(datetime.now().strftime("%d/%m/%Y %H:%M"))
                    })
                    st.success(f"{icona} Salvato in {via_civico}!")
                else:
                    st.error("Compila *")
    with t2:
        st.markdown(LOGO_HTML, unsafe_allow_html=True)
        if st.session_state.interventi_lista:
            df=pd.DataFrame(st.session_state.interventi_lista)
            st.dataframe(df, use_container_width=True, height=400)
            c1,c2=st.columns(2)
            with c1:
                st.download_button("CSV con Loghi", df.to_csv(index=False).encode('utf-8'), "interventi_loghi.csv", use_container_width=True)
            with c2:
                if st.button("Cancella", use_container_width=True):
                    st.session_state.interventi_lista=[]
                    st.rerun()
        else:
            st.info("Nessun intervento")
    tasto_dash("int")

elif scelta=="Backup":
    header_con_logo("💾 Backup Import/Export Vecchio Completo")
    t1,t2=st.tabs(["📤 Export","📥 Import"])
    with t1:
        st.markdown(LOGO_HTML, unsafe_allow_html=True)
        st.markdown("**Export come vecchio form**")
        if st.button("Excel Completo 12 Form - Rosso", use_container_width=True, type="primary"):
            out=BytesIO()
            has=False
            with pd.ExcelWriter(out, engine='openpyxl') as writer:
                if st.session_state.eventi:
                    df=pd.DataFrame(st.session_state.eventi)
                    df.insert(0,"Logo","ANA")
                    df.to_excel(writer, sheet_name="Eventi", index=False)
                    has=True
                if st.session_state.interventi_lista:
                    pd.DataFrame(st.session_state.interventi_lista).to_excel(writer, sheet_name="Interventi", index=False)
                    has=True
                if st.session_state.mem_nomi:
                    pd.DataFrame({"Logo":["ANA"]*len(st.session_state.mem_nomi),"Volontari":st.session_state.mem_nomi}).to_excel(writer, sheet_name="Volontari", index=False)
                    has=True
                if not has:
                    pd.DataFrame({"Logo":["ANA"],"Info":["Nessun dato"]}).to_excel(writer, sheet_name="Info", index=False)
            st.download_button("📥 Scarica Excel con Loghi", out.getvalue(), "ANA_Varese_Loghi.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        if st.session_state.interventi_lista:
            df=pd.DataFrame(st.session_state.interventi_lista)
            st.download_button("📥 CSV Interventi con Loghi", df.to_csv(index=False).encode('utf-8'), "interventi_loghi.csv", use_container_width=True)
        all_data={"interventi":st.session_state.interventi_lista,"eventi":st.session_state.eventi,"volontari":st.session_state.mem_nomi,"data":str(datetime.now())}
        st.download_button("📥 JSON Backup", json.dumps(all_data, indent=2, ensure_ascii=False).encode('utf-8'), "backup.json", "application/json", use_container_width=True)
    with t2:
        st.markdown(LOGO_HTML, unsafe_allow_html=True)
        up=st.file_uploader("Carica JSON Backup", type=["json"])
        if up:
            try:
                data=json.load(up)
                st.success("File caricato")
                st.json({k:len(v) if isinstance(v,list) else v for k,v in data.items()})
                if st.button("🔴 Ripristina Tutto", use_container_width=True, type="primary"):
                    if "interventi" in data: st.session_state.interventi_lista=data["interventi"]
                    if "eventi" in data: st.session_state.eventi=data["eventi"]
                    if "volontari" in data: st.session_state.mem_nomi=data["volontari"]
                    st.success("Ripristinato!")
                    st.rerun()
            except Exception as e:
                st.error(str(e))
        csv_up=st.file_uploader("Carica CSV", type=["csv"])
        if csv_up:
            df=pd.read_csv(csv_up)
            st.dataframe(df.head())
            if st.button("📥 Importa CSV"):
                for _,r in df.iterrows():
                    st.session_state.interventi_lista.append(r.to_dict())
                st.success("Importato")
    tasto_dash("backup")

else:
    header_con_logo(f"{scelta}")
    st.info(f"Modulo {scelta} - Con logo ANA su tutti i fogli")
    # Mostra tabella con logo se presente
    if scelta=="📅 Eventi" and st.session_state.eventi:
        df=pd.DataFrame(st.session_state.eventi)
        df.insert(0,"Logo ANA",["ANA" for _ in range(len(df))])
        st.dataframe(df, use_container_width=True)
    elif scelta=="👥 Volontari":
        df=pd.DataFrame({"Logo ANA":["🟢 ANA"]*len(st.session_state.mem_nomi),"Volontari":st.session_state.mem_nomi})
        st.dataframe(df, use_container_width=True)
    elif scelta=="📻 Radio DB" and st.session_state.radio_db:
        df=pd.DataFrame(st.session_state.radio_db)
        df.insert(0,"Logo",["ANA"]*len(df))
        st.dataframe(df, use_container_width=True)
    elif scelta=="📦 Distribuzione" and st.session_state.dist_radio:
        df=pd.DataFrame(st.session_state.dist_radio)
        df.insert(0,"Logo",["ANA"]*len(df))
        st.dataframe(df, use_container_width=True)
    elif scelta=="🗺️ Postazioni" and st.session_state.postazioni:
        df=pd.DataFrame(st.session_state.postazioni)
        df.insert(0,"Logo",["ANA"]*len(df))
        st.dataframe(df, use_container_width=True)
    elif scelta=="📝 Brogliaccio" and st.session_state.brogliaccio:
        df=pd.DataFrame(st.session_state.brogliaccio)
        df.insert(0,"Logo",["ANA"]*len(df))
        st.dataframe(df, use_container_width=True)
    elif scelta=="📝 Registro Radio" and st.session_state.registro_radio:
        df=pd.DataFrame(st.session_state.registro_radio)
        df.insert(0,"Logo",["ANA"]*len(df))
        st.dataframe(df, use_container_width=True)
    else:
        # Form generici per altri moduli
        with st.form(f"form_{scelta}", clear_on_submit=True):
            st.markdown(LOGO_HTML, unsafe_allow_html=True)
            nome=st.text_input("Nome *")
            desc=st.text_area("Descrizione *")
            if st.form_submit_button("🔴 SALVA", use_container_width=True, type="primary"):
                if nome and desc:
                    st.success(f"Salvato {nome}!")
    tasto_dash("other")

st.caption('ANA Varese - 12 Form + Loghi + Via+Civico + Icone + Backup Import/Export')
