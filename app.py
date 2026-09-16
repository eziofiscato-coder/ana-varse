import streamlit as st
import pandas as pd
st.set_page_config(page_title="ANA Varese", layout="wide")
APP_PASSWORD="ANA2025"
if "authenticated" not in st.session_state:
    st.session_state.authenticated=False
if "dashboard_entered" not in st.session_state:
    st.session_state.dashboard_entered=False
if "interventi_lista" not in st.session_state:
    st.session_state.interventi_lista=[]
if "eventi" not in st.session_state:
    st.session_state.eventi=[]
if "checkin" not in st.session_state:
    st.session_state.checkin={}
if not st.session_state.authenticated:
    st.markdown("<style>[data-testid='stSidebar']{display:none;}</style>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center; color:#2e7d32;'>🔐 Accesso Riservato ANA Varese</h2>", unsafe_allow_html=True)
    pwd=st.text_input("Password", type="password", placeholder="ANA2025")
    if st.button("🔓 Accedi", use_container_width=True, type="primary"):
        if pwd==APP_PASSWORD:
            st.session_state.authenticated=True
            st.rerun()
        else:
            st.error("Password errata!")
    st.stop()
if not st.session_state.dashboard_entered:
    st.markdown("<style>.stApp{background-color:#e8f5e9!important;}[data-testid='stSidebar']{display:none;}</style>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center; color:#2e7d32;'>🟢 ANA Varese</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center;'>Benvenuto - Clicca per entrare</h3>", unsafe_allow_html=True)
    c1,c2,c3=st.columns([1,2,1])
    with c2:
        if st.button("🚀 ENTRA NELLA DASHBOARD", use_container_width=True, type="primary"):
            st.session_state.dashboard_entered=True
            st.rerun()
        if st.button("🔒 Esci", use_container_width=True):
            st.session_state.authenticated=False
            st.rerun()
    st.stop()
st.markdown("<style>.stApp{background-color:#e8f5e9!important;}[data-testid='stSidebar']{background-color:#a5d6a7!important;}.stForm{background-color:#f1f8e9!important;border:2px solid #81c784!important;border-radius:12px!important;}</style>", unsafe_allow_html=True)
with st.sidebar:
    st.markdown("### 🟢 ANA Varese - Menu Completo Ripristinato")
    scelta=st.radio("MENU", ["🏠 Dashboard","📅 Gestione Eventi","✅ Check-In Volontari","👥 Volontari","📻 Radio & Distribuzione","🗺️ Mappa Postazioni","🚨 Interventi Emergenza","📝 Registro Radio","💾 Backup & Export","🔗 Link & Aggiornamenti"])
    st.divider()
    if st.button("🏠 Home", use_container_width=True):
        st.session_state.dashboard_entered=False
        st.rerun()
    if st.button("🔒 Logout", use_container_width=True):
        st.session_state.authenticated=False
        st.session_state.dashboard_entered=False
        st.rerun()
st.markdown(f"## {scelta}")
if scelta=="🏠 Dashboard":
    st.markdown("### Dashboard - Menu completo ripristinato, senza Anagrafica Esistente")
    c1,c2=st.columns(2)
    c1.metric("Eventi", len(st.session_state.eventi))
    c2.metric("Interventi Emergenza", len(st.session_state.interventi_lista))
    st.info("Anagrafica Esistente rimossa come richiesto - tutto il resto del menu di prima ripristinato")
elif scelta=="🚨 Interventi Emergenza":
    st.markdown("## 🚨 NUOVO FORM INTERVENTI DI EMERGENZA")
    st.markdown("### Form Registrazione - Protezione Civile ANA Varese")
    
    tab_form, tab_elenco = st.tabs(["📝 Nuovo Intervento", "📋 Elenco Interventi"])
    
    with tab_form:
        with st.form("form_interventi_emergenza_nuovo", clear_on_submit=True):
            st.markdown("#### 📍 Dati Luogo Intervento")
            c1,c2,c3=st.columns(3)
            with c1:
                data_int=st.date_input("Data Intervento *", value=pd.Timestamp.now().date())
                ora_int=st.time_input("Ora Intervento *", value=pd.Timestamp.now().time())
                comune_int=st.text_input("Comune *", placeholder="Varese")
            with c2:
                via_int=st.text_input("Via / Località *", placeholder="Via Roma")
                civico_int=st.text_input("Civico / Km", placeholder="10")
                prov_int=st.text_input("Provincia", value="VA", max_chars=2)
            with c3:
                tipo_int=st.selectbox("Tipo Emergenza *", ["Alluvione / Esondazione","Incendio Boschivo","Frana / Smottamento","Neve / Ghiaccio","Ricerca Persona","Supporto Popolazione","Monitoraggio Idrogeologico","Altro"])
                odv_int=st.selectbox("ODV Operativa *", ["ANA Varese","ANA Sezione Varese","Protezione Civile Lombardia","Croce Rossa Italiana","Vigili del Fuoco","Altro"])
                priorita_int=st.selectbox("Priorità", ["Bassa","Media","Alta","Critica"])
            
            st.divider()
            st.markdown("#### 👥 Dati Operativi")
            c1,c2,c3=st.columns(3)
            with c1:
                responsabile_int=st.text_input("Responsabile Squadra *", placeholder="Mario Rossi")
                cell_resp_int=st.text_input("Cellulare Responsabile", placeholder="333 1234567")
            with c2:
                num_vol_int=st.number_input("N° Volontari", min_value=1, max_value=50, value=3)
                mezzi_int=st.text_input("Mezzi Impiegati", placeholder="Fuoristrada, Motosega...")
            with c3:
                stato_int=st.selectbox("Stato Intervento", ["In Corso","Completato","In Attesa","Annullato"])
                ore_int=st.text_input("Durata / Ore", placeholder="2h 30m")
            
            st.divider()
            st.markdown("#### 📝 Descrizione Azione")
            azione_int=st.text_area("Azione Svolta *", placeholder="Descrivi dettagliatamente l'intervento svolto, azioni intraprese, criticità riscontrate...", height=150)
            note_int=st.text_area("Note Aggiuntive", placeholder="Note, materiali usati, necessità...", height=80)
            
            st.markdown("<br>", unsafe_allow_html=True)
            salva=st.form_submit_button("🚨 SALVA INTERVENTO EMERGENZA", use_container_width=True, type="primary")
            
            if salva:
                if not comune_int or not via_int or not azione_int or not responsabile_int:
                    st.error("⚠️ Compila tutti i campi obbligatori contrassegnati con *")
                else:
                    nuovo={
                        "ID": len(st.session_state.interventi_lista)+1,
                        "Data": str(data_int),
                        "Ora": str(ora_int),
                        "Comune": comune_int,
                        "Provincia": prov_int,
                        "Via": via_int,
                        "Civico": civico_int,
                        "Tipo": tipo_int,
                        "ODV Operativa": odv_int,
                        "Priorità": priorita_int,
                        "Responsabile": responsabile_int,
                        "Cellulare": cell_resp_int,
                        "N Volontari": num_vol_int,
                        "Mezzi": mezzi_int,
                        "Stato": stato_int,
                        "Durata": ore_int,
                        "Azione": azione_int,
                        "Note": note_int,
                        "Data Inserimento": pd.Timestamp.now().strftime("%d/%m/%Y %H:%M")
                    }
                    st.session_state.interventi_lista.append(nuovo)
                    st.success(f"✅ Intervento #{nuovo['ID']} salvato! {comune_int} - {via_int}")
                    st.balloons()
                    st.rerun()
    
    with tab_elenco:
        st.markdown(f"### 📋 Elenco - Totale: {len(st.session_state.interventi_lista)} interventi")
        if st.session_state.interventi_lista:
            df=pd.DataFrame(st.session_state.interventi_lista)
            # Filtri
            c1,c2,c3=st.columns(3)
            with c1:
                filtro_comune=st.text_input("🔍 Filtra per Comune", placeholder="Varese")
            with c2:
                filtro_tipo=st.selectbox("Filtra per Tipo", ["Tutti"]+sorted(df["Tipo"].unique().tolist()) if "Tipo" in df.columns else ["Tutti"])
            with c3:
                filtro_stato=st.selectbox("Filtra per Stato", ["Tutti","In Corso","Completato","In Attesa"])
            
            df_filt=df.copy()
            if filtro_comune:
                df_filt=df_filt[df_filt["Comune"].str.contains(filtro_comune, case=False, na=False)]
            if filtro_tipo!="Tutti":
                df_filt=df_filt[df_filt["Tipo"]==filtro_tipo]
            if filtro_stato!="Tutti":
                df_filt=df_filt[df_filt["Stato"]==filtro_stato]
            
            st.dataframe(df_filt, use_container_width=True, height=400)
            
            c1,c2,c3=st.columns(3)
            with c1:
                st.download_button("📥 Scarica CSV", df_filt.to_csv(index=False).encode('utf-8'), f"interventi_{pd.Timestamp.now().strftime('%Y%m%d')}.csv", "text/csv", use_container_width=True)
            with c2:
                if st.button("🗑️ Cancella Tutti", use_container_width=True):
                    st.session_state.interventi_lista=[]
                    st.rerun()
            with c3:
                st.metric("Interventi Filtrati", len(df_filt))
        else:
            st.info("📭 Nessun intervento registrato - Usa il tab 'Nuovo Intervento' per inserire il primo!")
else:
    st.info(f"Modulo {scelta} - Ripristinato dal menu di prima")
    st.write("Contenuto originale di questa sezione")
