
import streamlit as st
import pandas as pd
from datetime import datetime, date
import json
from io import BytesIO

st.set_page_config(page_title="ANA Varese - Completo", page_icon="🟢", layout="wide")
APP_PASSWORD = "ANA2025"

# INIT SESSION
for k,v in [("authenticated",False),("dashboard_entered",False),("interventi_lista",[]),("eventi",[]),("checkin",{}),("mem_nomi",["Mario Rossi","Luigi Bianchi","Giuseppe Verdi"]),("radio_db",[]),("dist_radio",[]),("postazioni",[]),("registro_radio",[]),("brogliaccio",[]),("volontari_full",[])]:
    if k not in st.session_state:
        st.session_state[k]=v

# STILE COMPLETO - TASTI ROSSI + SFONDO VERDE ANA SU TUTTI I FORM E FOGLI
st.markdown("""
<style>
.stApp{background-color:#e8f5e9!important;}
.main .block-container{background-color:#e8f5e9!important; padding:20px!important; border-radius:15px!important;}
[data-testid="stSidebar"]{background-color:#a5d6a7!important; border-right:3px solid #2e7d32!important;}

/* FORM VERDE ANA - NO BIANCO */
.stForm{background-color:#a5d6a7!important; border:3px solid #2e7d32!important; border-radius:15px!important; padding:25px!important;}
.stForm label{color:#1b5e20!important; font-weight:bold!important;}

/* FOGLI / TABELLE VERDE ANA */
[data-testid="stDataFrame"], [data-testid="stTable"]{background-color:#c8e6c9!important; border:3px solid #2e7d32!important; border-radius:12px!important;}
[data-testid="stDataFrame"] div{background-color:#c8e6c9!important;}
.stDataFrame, .stTable{background-color:#c8e6c9!important;}

/* TAB VERDE ANA */
.stTabs [data-baseweb="tab-list"]{background-color:#a5d6a7!important; border-radius:12px!important; padding:6px!important; border:2px solid #2e7d32!important;}
.stTabs [data-baseweb="tab"]{background-color:#81c784!important; color:#1b5e20!important; font-weight:bold!important; border-radius:8px!important; margin:3px!important; padding:8px 16px!important;}
.stTabs [aria-selected="true"]{background-color:#2e7d32!important; color:white!important;}

/* ALERT VERDE ANA */
.stAlert{background-color:#c8e6c9!important; border:2px solid #2e7d32!important; border-radius:10px!important;}

/* TUTTI I TASTI ROSSI */
.stButton>button{background-color:#d32f2f!important; color:white!important; border:3px solid #b71c1c!important; font-weight:bold!important; border-radius:10px!important; font-size:15px!important; padding:10px!important;}
.stButton>button:hover{background-color:#b71c1c!important; border-color:#8e0000!important;}
div[data-testid="stFormSubmitButton"]>button{background-color:#d32f2f!important; color:white!important; border:3px solid #b71c1c!important; font-weight:bold!important; border-radius:10px!important;}
.stDownloadButton>button{background-color:#d32f2f!important; color:white!important; border:3px solid #b71c1c!important;}

/* INPUT VERDE */
.stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div, .stNumberInput>div>div>input{background-color:#f1f8e9!important; border:2px solid #66bb6a!important; border-radius:8px!important;}
.stDateInput>div>div>input, .stTimeInput>div>div>input{background-color:#f1f8e9!important; border:2px solid #66bb6a!important;}

/* METRIC VERDE ANA */
[data-testid="stMetric"]{background-color:#a5d6a7!important; border:2px solid #2e7d32!important; border-radius:10px!important; padding:10px!important;}
</style>
""", unsafe_allow_html=True)

# PAGINA 1 - PASSWORD
if not st.session_state.authenticated:
    st.markdown("<style>[data-testid='stSidebar']{display:none;}</style>", unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align:center; background-color:#a5d6a7; padding:30px; border-radius:20px; border:4px solid #2e7d32; margin:20px;'>
        <h1 style='color:#1b5e20;'>🟢 ANA Varese</h1>
        <h2 style='color:#2e7d32;'>🔐 Accesso Riservato - Protezione Civile</h2>
        <p style='color:#1b5e20; font-weight:bold;'>Inserisci password per continuare</p>
    </div>
    """, unsafe_allow_html=True)
    c1,c2,c3=st.columns([1,2,1])
    with c2:
        with st.form("login"):
            pwd=st.text_input("Password *", type="password", placeholder="ANA2025")
            if st.form_submit_button("🔴 ACCEDI - TASTO ROSSO", use_container_width=True, type="primary"):
                if pwd==APP_PASSWORD:
                    st.session_state.authenticated=True
                    st.rerun()
                else:
                    st.error("❌ Password errata!")
        st.info("💡 Password: ANA2025")
    st.stop()

# PAGINA 2 - ENTRA IN DASHBOARD
if not st.session_state.dashboard_entered:
    st.markdown("<style>[data-testid='stSidebar']{display:none;}</style>", unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align:center; background-color:#a5d6a7; padding:30px; border-radius:20px; border:4px solid #2e7d32;'>
        <h1 style='color:#1b5e20;'>🟢 ANA Varese - Protezione Civile</h1>
        <h3 style='color:#2e7d32;'>Sistema Gestionale Completo - Verde ANA + Tasti Rossi</h3>
        <p style='color:#1b5e20;'>✅ Tutti i form ripristinati | 🔴 Tasti Rossi | 🟢 Sfondi Verdi ANA</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    c1,c2,c3=st.columns([1,2,1])
    with c2:
        st.success("✅ Accesso autorizzato - Sei pronto per entrare!")
        st.markdown("<div style='background-color:#c8e6c9; padding:15px; border-radius:10px; border:2px solid #2e7d32;'>", unsafe_allow_html=True)
        if st.button("🚀 ENTRA NELLA DASHBOARD - TASTO ROSSO", use_container_width=True, type="primary"):
            st.session_state.dashboard_entered=True
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔒 Logout", use_container_width=True):
            st.session_state.authenticated=False
            st.rerun()
    st.stop()

# DASHBOARD + SIDEBAR CON TUTTI I FORM
with st.sidebar:
    st.markdown("<div style='background-color:#2e7d32; color:white; padding:12px; border-radius:10px; text-align:center;'><h3 style='margin:0; color:white;'>🟢 ANA Varese</h3><p style='margin:0; font-size:12px;'>Verde ANA + Tasti Rossi</p></div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    scelta=st.radio("MENU COMPLETO - 12 FORM", [
        "🏠 Dashboard",
        "📅 Gestione Eventi",
        "✅ Check-In Volontari",
        "👥 Volontari - Anagrafica",
        "📻 DB Radio Inventario",
        "📦 Distribuzione Radio",
        "🗺️ Mappa Postazioni",
        "🚨 Interventi Emergenza",
        "📝 Brogliaccio ODV",
        "📝 Registro Radio",
        "💾 Backup/Export/Import",
        "🔗 Link & Aggiornamenti"
    ])
    st.divider()
    if st.button("🏠 Home - Torna a Entra Dashboard", use_container_width=True):
        st.session_state.dashboard_entered=False
        st.rerun()
    if st.button("🔒 Logout Completo", use_container_width=True):
        st.session_state.authenticated=False
        st.session_state.dashboard_entered=False
        st.rerun()

def tasto_dashboard_su_form(key=""):
    st.markdown("<br>", unsafe_allow_html=True)
    c1,c2=st.columns([1,1])
    with c1:
        if st.button("🏠 Torna alla Dashboard", use_container_width=True, key=f"dash_{key}_1"):
            st.session_state.dashboard_entered=False
            st.session_state.dashboard_entered=True
            # Torna a dashboard principale (simulata con reload menu)
            st.rerun()
    with c2:
        if st.button("🏠 Home Iniziale", use_container_width=True, key=f"home_{key}_2"):
            st.session_state.dashboard_entered=False
            st.rerun()

st.markdown(f"<h2 style='color:#1b5e20; background-color:#a5d6a7; padding:12px; border-radius:12px; border:3px solid #2e7d32;'>🟢 {scelta} - Verde ANA + Tasti Rossi</h2>", unsafe_allow_html=True)
st.divider()

if scelta=="🏠 Dashboard":
    st.markdown("<div style='background-color:#a5d6a7; padding:15px; border-radius:12px; border:2px solid #2e7d32;'><h3 style='color:#1b5e20;'>📊 Dashboard Centrale - Fogli Verdi ANA</h3></div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    c1,c2,c3,c4,c5=st.columns(5)
    c1.metric("Volontari", len(st.session_state.mem_nomi))
    c2.metric("Eventi", len(st.session_state.eventi))
    c3.metric("Radio", len(st.session_state.radio_db))
    c4.metric("Postazioni", len(st.session_state.postazioni))
    c5.metric("Interventi", len(st.session_state.interventi_lista))
    st.divider()
    col1,col2=st.columns(2)
    with col1:
        st.markdown("#### 📋 Ultimi Interventi - Foglio Verde")
        if st.session_state.interventi_lista:
            st.dataframe(pd.DataFrame(st.session_state.interventi_lista).tail(5), use_container_width=True)
        else:
            st.info("Nessun intervento")
    with col2:
        st.markdown("#### 📅 Ultimi Eventi - Foglio Verde")
        if st.session_state.eventi:
            st.dataframe(pd.DataFrame(st.session_state.eventi).tail(5), use_container_width=True)
        else:
            st.info("Nessun evento")
    st.divider()
    if st.button("🏠 Torna a Home Entra Dashboard", use_container_width=True):
        st.session_state.dashboard_entered=False
        st.rerun()

elif scelta=="📅 Gestione Eventi":
    tasto_dashboard_su_form("eventi_top")
    tab1,tab2=st.tabs(["➕ Crea Evento - Form Verde", "📋 Lista Eventi - Foglio Verde"])
    with tab1:
        with st.form("form_evento", clear_on_submit=True):
            st.markdown("#### 📅 Nuovo Evento - Sfondo Verde ANA")
            c1,c2=st.columns(2)
            with c1:
                tipo=st.selectbox("Tipo *", ["Monitoraggio","Antincendio","Supporto emergenza","Esercitazione","Manifestazione","Ricerca persone","Alluvione","Neve","Assistenza","Presidio","Altro"])
                desc=st.text_area("Descrizione *", height=100, placeholder="Descrizione...")
                comune=st.text_input("Comune *", placeholder="Varese")
                prov=st.selectbox("Provincia", ["VA - Varese","MI - Milano","CO - Como","Altra"])
            with c2:
                d_ini=st.date_input("Data Inizio *")
                o_ini=st.time_input("Ora Inizio *")
                d_fine=st.date_input("Data Fine")
                o_fine=st.time_input("Ora Fine")
                org=st.text_input("Organizzazione *", value="ANA Varese")
                resp=st.text_input("Responsabile *")
                cell=st.text_input("Cellulare *")
            if st.form_submit_button("🔴 SALVA EVENTO - TASTO ROSSO", use_container_width=True, type="primary"):
                if not desc or not comune or not resp:
                    st.error("Compila campi *")
                else:
                    ev={"ID":len(st.session_state.eventi)+1,"Tipo":tipo,"Descrizione":desc,"Comune":comune,"Provincia":prov,"Data Inizio":str(d_ini),"Ora Inizio":str(o_ini),"Data Fine":str(d_fine),"Ora Fine":str(o_fine),"Organizzazione":org,"Responsabile":resp,"Cellulare":cell,"Creato":datetime.now().strftime("%d/%m/%Y %H:%M")}
                    st.session_state.eventi.append(ev)
                    st.success(f"Evento {ev['ID']} salvato!")
                    st.rerun()
    with tab2:
        st.markdown("#### 📋 Lista Eventi - Foglio Verde ANA")
        if st.session_state.eventi:
            st.dataframe(pd.DataFrame(st.session_state.eventi), use_container_width=True)
            if st.button("🗑️ Cancella Tutti Eventi - Rosso", use_container_width=True):
                st.session_state.eventi=[]
                st.rerun()
        else:
            st.info("Nessun evento")
    tasto_dashboard_su_form("eventi_bot")

elif scelta=="🚨 Interventi Emergenza":
    tasto_dashboard_su_form("interventi_top")
    tab_form, tab_elenco = st.tabs(["📝 Nuovo Intervento - Form Verde", "📋 Elenco - Foglio Verde"])
    with tab_form:
        with st.form("form_interventi", clear_on_submit=True):
            st.markdown("#### 🚨 Nuovo Intervento - Form Verde ANA - Tutti i tasti Rossi")
            c1,c2,c3=st.columns(3)
            with c1:
                data_int=st.date_input("Data *", value=date.today())
                ora_int=st.time_input("Ora *")
                comune_int=st.text_input("Comune *", placeholder="Varese")
            with c2:
                via_int=st.text_input("Via *", placeholder="Via Roma")
                civico_int=st.text_input("Civico")
                prov_int=st.text_input("Provincia", value="VA", max_chars=2)
            with c3:
                tipo_int=st.selectbox("Tipo *", ["Alluvione","Incendio","Frana","Neve","Ricerca Persona","Supporto Popolazione","Monitoraggio","Altro"])
                odv_int=st.selectbox("ODV *", ["ANA Varese","ANA Sezione Varese","PC Lombardia","Croce Rossa","VVF","Altro"])
                priorita_int=st.selectbox("Priorità", ["Bassa","Media","Alta","Critica"])
            c1,c2,c3=st.columns(3)
            with c1:
                resp_int=st.text_input("Responsabile *")
                cell_int=st.text_input("Cellulare")
            with c2:
                nvol_int=st.number_input("N° Volontari", min_value=1, max_value=50, value=3)
                mezzi_int=st.text_input("Mezzi")
            with c3:
                stato_int=st.selectbox("Stato", ["In Corso","Completato","In Attesa"])
                durata_int=st.text_input("Durata")
            azione_int=st.text_area("Azione Svolta *", height=120, placeholder="Descrizione dettagliata...")
            note_int=st.text_area("Note", height=60)
            if st.form_submit_button("🔴 SALVA INTERVENTO EMERGENZA - TASTO ROSSO", use_container_width=True, type="primary"):
                if not comune_int or not via_int or not azione_int or not resp_int:
                    st.error("Compila campi *")
                else:
                    nuovo={"ID":len(st.session_state.interventi_lista)+1,"Data":str(data_int),"Ora":str(ora_int),"Comune":comune_int,"Provincia":prov_int,"Via":via_int,"Civico":civico_int,"Tipo":tipo_int,"ODV":odv_int,"Priorità":priorita_int,"Responsabile":resp_int,"Cellulare":cell_int,"N Vol":nvol_int,"Mezzi":mezzi_int,"Stato":stato_int,"Durata":durata_int,"Azione":azione_int,"Note":note_int,"Inserito":datetime.now().strftime("%d/%m/%Y %H:%M")}
                    st.session_state.interventi_lista.append(nuovo)
                    st.success(f"Intervento #{nuovo['ID']} salvato!")
                    st.balloons()
                    st.rerun()
    with tab_elenco:
        st.markdown("#### 📋 Elenco Interventi - Foglio Verde ANA")
        if st.session_state.interventi_lista:
            df=pd.DataFrame(st.session_state.interventi_lista)
            st.dataframe(df, use_container_width=True)
            c1,c2=st.columns(2)
            with c1:
                st.download_button("📥 Scarica CSV - Rosso", df.to_csv(index=False).encode('utf-8'), "interventi.csv", use_container_width=True)
            with c2:
                if st.button("🗑️ Cancella Tutti - Rosso", use_container_width=True):
                    st.session_state.interventi_lista=[]
                    st.rerun()
        else:
            st.info("Nessun intervento")
    tasto_dashboard_su_form("interventi_bot")

elif scelta=="✅ Check-In Volontari":
    tasto_dashboard_su_form("checkin_top")
    st.markdown("#### ✅ Check-In - Form Verde ANA")
    if not st.session_state.eventi:
        st.warning("Crea prima un evento in Gestione Eventi")
    else:
        ids=[f"{e['ID']} - {e['Tipo']} - {e['Comune']}" for e in st.session_state.eventi]
        sel=st.selectbox("Seleziona Evento", ids)
        id_ev=int(sel.split(" - ")[0])
        tab1,tab2=st.tabs(["📚 Da Anagrafica - Verde", "✏️ Manuale - Verde"])
        with tab1:
            sel_vol=st.selectbox("Volontario", st.session_state.mem_nomi)
            note=st.text_input("Note")
            if st.button("🔴 Check-In da Anagrafica - Rosso", use_container_width=True, type="primary"):
                if id_ev not in st.session_state.checkin:
                    st.session_state.checkin[id_ev]=[]
                st.session_state.checkin[id_ev].append({"Nome":sel_vol,"Note":note,"Evento ID":id_ev,"Ora":datetime.now().strftime("%H:%M")})
                st.success("Salvato!")
        with tab2:
            with st.form("checkin_man", clear_on_submit=True):
                c1,c2=st.columns(2)
                with c1:
                    nome=st.text_input("Nome *")
                    cognome=st.text_input("Cognome *")
                with c2:
                    note2=st.text_input("Note")
                if st.form_submit_button("🔴 SALVA CHECK-IN - Rosso", use_container_width=True):
                    if nome and cognome:
                        if id_ev not in st.session_state.checkin:
                            st.session_state.checkin[id_ev]=[]
                        st.session_state.checkin[id_ev].append({"Nome":f"{nome} {cognome}","Note":note2,"Evento ID":id_ev})
                        st.success("Salvato!")
        if id_ev in st.session_state.checkin and st.session_state.checkin[id_ev]:
            st.dataframe(pd.DataFrame(st.session_state.checkin[id_ev]), use_container_width=True)
    tasto_dashboard_su_form("checkin_bot")

elif scelta=="👥 Volontari - Anagrafica":
    tasto_dashboard_su_form("vol_top")
    tab1,tab2=st.tabs(["➕ Nuovo - Form Verde", "📋 Lista - Foglio Verde"])
    with tab1:
        with st.form("form_vol", clear_on_submit=True):
            st.markdown("#### 👥 Nuovo Volontario - Form Verde ANA")
            c1,c2,c3=st.columns(3)
            with c1:
                nome_v=st.text_input("Nome *")
                cognome_v=st.text_input("Cognome *")
                cf_v=st.text_input("CF")
            with c2:
                cell_v=st.text_input("Cellulare *")
                via_v=st.text_input("Via")
                comune_v=st.text_input("Comune", value="Varese")
            with c3:
                sezione_v=st.text_input("Sezione", value="Varese")
                tessera_v=st.text_input("Tessera")
                ruolo_v=st.selectbox("Ruolo", ["Volontario","Capo Squadra","Coordinatore","Altro"])
            if st.form_submit_button("🔴 SALVA VOLONTARIO - Rosso", use_container_width=True, type="primary"):
                if nome_v and cognome_v and cell_v:
                    nome_completo=f"{nome_v} {cognome_v}"
                    if nome_completo not in st.session_state.mem_nomi:
                        st.session_state.mem_nomi.append(nome_completo)
                    st.session_state.volontari_full.append({"Nome":nome_v,"Cognome":cognome_v,"Nome Completo":nome_completo,"CF":cf_v,"Cellulare":cell_v,"Via":via_v,"Comune":comune_v,"Sezione":sezione_v,"Tessera":tessera_v,"Ruolo":ruolo_v})
                    st.success("Salvato!")
                    st.rerun()
    with tab2:
        st.markdown("#### 📋 Lista Volontari - Foglio Verde ANA")
        if st.session_state.volontari_full:
            st.dataframe(pd.DataFrame(st.session_state.volontari_full), use_container_width=True)
        else:
            st.dataframe(pd.DataFrame({"Volontari":st.session_state.mem_nomi}), use_container_width=True)
    tasto_dashboard_su_form("vol_bot")

elif scelta=="📻 DB Radio Inventario":
    tasto_dashboard_su_form("radio_top")
    st.markdown("#### 📻 DB Radio - Form Verde ANA")
    with st.form("form_radio", clear_on_submit=True):
        c1,c2,c3=st.columns(3)
        with c1:
            id_r=st.text_input("ID Radio *", placeholder="RAD-001")
            modello=st.text_input("Modello")
        with c2:
            freq=st.text_input("Frequenza", value="446.00625")
            stato=st.selectbox("Stato", ["Operativa","Guasta","OK"])
        with c3:
            note=st.text_input("Note")
        if st.form_submit_button("🔴 SALVA RADIO - Rosso", use_container_width=True, type="primary"):
            if id_r:
                st.session_state.radio_db.append({"ID":id_r,"Modello":modello,"Frequenza":freq,"Stato":stato,"Note":note})
                st.success("Salvata!")
                st.rerun()
    if st.session_state.radio_db:
        st.markdown("#### 📋 Inventario - Foglio Verde ANA")
        st.dataframe(pd.DataFrame(st.session_state.radio_db), use_container_width=True)
    tasto_dashboard_su_form("radio_bot")

elif scelta=="📦 Distribuzione Radio":
    tasto_dashboard_su_form("dist_top")
    st.markdown("#### 📦 Distribuzione - Form Verde ANA")
    with st.form("form_dist", clear_on_submit=True):
        c1,c2,c3=st.columns(3)
        with c1:
            radio_sel=st.selectbox("Radio", [r["ID"] for r in st.session_state.radio_db] if st.session_state.radio_db else ["RAD-001"])
            vol_sel=st.selectbox("Volontario", st.session_state.mem_nomi)
        with c2:
            data_c=st.date_input("Data", value=date.today())
            ora_c=st.time_input("Ora")
        with c3:
            cons_da=st.text_input("Consegnata da")
            note_c=st.text_input("Note")
        if st.form_submit_button("🔴 CONSEGNA RADIO - Rosso", use_container_width=True, type="primary"):
            st.session_state.dist_radio.append({"Radio":radio_sel,"Volontario":vol_sel,"Data":str(data_c),"Ora":str(ora_c),"Consegnata da":cons_da,"Note":note_c})
            st.success("Consegnata!")
            st.rerun()
    if st.session_state.dist_radio:
        st.dataframe(pd.DataFrame(st.session_state.dist_radio).iloc[::-1], use_container_width=True)
    tasto_dashboard_su_form("dist_bot")

elif scelta=="🗺️ Mappa Postazioni":
    tasto_dashboard_su_form("mappa_top")
    st.markdown("#### 🗺️ Mappa Postazioni - Form Verde ANA")
    with st.form("form_post", clear_on_submit=True):
        c1,c2=st.columns(2)
        with c1:
            nome_p=st.text_input("Nome Postazione *")
            comune_p=st.text_input("Comune *", value="Varese")
            via_p=st.text_input("Via *")
        with c2:
            lat_p=st.text_input("Lat", placeholder="45.8205")
            lon_p=st.text_input("Lon", placeholder="8.8255")
            resp_p=st.text_input("Responsabile")
        if st.form_submit_button("🔴 SALVA POSTAZIONE - Rosso", use_container_width=True, type="primary"):
            if nome_p and comune_p:
                st.session_state.postazioni.append({"Postazione":nome_p,"Comune":comune_p,"Via":via_p,"Latitudine":lat_p,"Longitudine":lon_p,"Responsabile":resp_p})
                st.success("Salvata!")
                st.rerun()
    if st.session_state.postazioni:
        st.dataframe(pd.DataFrame(st.session_state.postazioni), use_container_width=True)
    tasto_dashboard_su_form("mappa_bot")

elif scelta=="📝 Brogliaccio ODV":
    tasto_dashboard_su_form("brog_top")
    st.markdown("#### 📝 Brogliaccio - Form Verde ANA")
    with st.form("form_brog", clear_on_submit=True):
        c1,c2=st.columns(2)
        with c1:
            data_b=st.date_input("Data", value=date.today())
            mitt_b=st.selectbox("Mittente", st.session_state.mem_nomi)
        with c2:
            dest_b=st.text_input("Destinatario", placeholder="COC Varese")
            msg_b=st.text_area("Messaggio *", height=100)
        if st.form_submit_button("🔴 SALVA BROGLIACCIO - Rosso", use_container_width=True, type="primary"):
            if msg_b:
                st.session_state.brogliaccio.append({"Data":str(data_b),"Mittente":mitt_b,"Destinatario":dest_b,"Messaggio":msg_b})
                st.success("Salvato!")
                st.rerun()
    if st.session_state.brogliaccio:
        st.dataframe(pd.DataFrame(st.session_state.brogliaccio).iloc[::-1], use_container_width=True)
    tasto_dashboard_su_form("brog_bot")

elif scelta=="📝 Registro Radio":
    tasto_dashboard_su_form("reg_top")
    st.markdown("#### 📝 Registro Radio - Form Verde ANA")
    with st.form("form_reg", clear_on_submit=True):
        c1,c2,c3=st.columns(3)
        with c1:
            data_r=st.date_input("Data", value=date.today())
            radio_r=st.selectbox("Radio", [r["ID"] for r in st.session_state.radio_db] if st.session_state.radio_db else ["RAD-001"])
        with c2:
            vol_r=st.selectbox("Volontario", st.session_state.mem_nomi)
            ore_r=st.text_input("Ore uso", placeholder="08:00-12:00")
        with c3:
            stato_r=st.selectbox("Stato", ["OK","Batteria scarica","Guasta"])
            note_r=st.text_input("Note")
        if st.form_submit_button("🔴 SALVA REGISTRO - Rosso", use_container_width=True, type="primary"):
            st.session_state.registro_radio.append({"Data":str(data_r),"RadioID":radio_r,"Volontario":vol_r,"OreUso":ore_r,"Stato":stato_r,"Note":note_r})
            st.success("Salvato!")
            st.rerun()
    if st.session_state.registro_radio:
        st.dataframe(pd.DataFrame(st.session_state.registro_radio).iloc[::-1], use_container_width=True)
    tasto_dashboard_su_form("reg_bot")

elif scelta=="💾 Backup/Export/Import":
    tasto_dashboard_su_form("backup_top")
    st.markdown("#### 💾 Backup - Fogli Verdi + Tasti Rossi")
    if st.button("📥 ESPORTA TUTTO IN EXCEL - Rosso", use_container_width=True, type="primary"):
        output=BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            if st.session_state.eventi: pd.DataFrame(st.session_state.eventi).to_excel(writer, sheet_name="Eventi", index=False)
            if st.session_state.interventi_lista: pd.DataFrame(st.session_state.interventi_lista).to_excel(writer, sheet_name="Interventi", index=False)
            if st.session_state.volontari_full: pd.DataFrame(st.session_state.volontari_full).to_excel(writer, sheet_name="Volontari", index=False)
            if st.session_state.radio_db: pd.DataFrame(st.session_state.radio_db).to_excel(writer, sheet_name="RadioDB", index=False)
        st.download_button("📥 Scarica Excel Completo - Rosso", output.getvalue(), f"ANA_Varese_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
    st.divider()
    all_data={"eventi":st.session_state.eventi,"interventi":st.session_state.interventi_lista,"volontari":st.session_state.mem_nomi,"radio_db":st.session_state.radio_db,"postazioni":st.session_state.postazioni,"data_export":str(datetime.now())}
    st.download_button("📥 Backup JSON - Rosso", json.dumps(all_data, indent=2, ensure_ascii=False).encode('utf-8'), f"backup_{datetime.now().strftime('%Y%m%d')}.json", "application/json", use_container_width=True)
    tasto_dashboard_su_form("backup_bot")

elif scelta=="🔗 Link & Aggiornamenti":
    tasto_dashboard_su_form("link_top")
    st.markdown("#### 🔗 Link & Aggiornamenti - Form Verde ANA")
    app_url=st.text_input("URL App", placeholder="https://ana-varese.streamlit.app")
    if app_url:
        st.success(f"Link: {app_url}")
        c1,c2=st.columns(2)
        with c1:
            st.link_button("📱 WhatsApp - Rosso", f"https://wa.me/?text={app_url}", use_container_width=True)
        with c2:
            st.link_button("✈️ Telegram - Rosso", f"https://t.me/share/url?url={app_url}", use_container_width=True)
    tasto_dashboard_su_form("link_bot")

st.divider()
st.caption("ANA Varese - Versione Completa | PSW + Dashboard | Tasti Rossi + Verde ANA | By Ezio Fiscato")
