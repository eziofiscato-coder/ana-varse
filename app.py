import streamlit as st
import pandas as pd
from datetime import datetime
st.set_page_config(page_title="ANA Varese", layout="wide")

# STILE ANA - TASTI ROSSI + SFONDO VERDE
st.markdown("""
<style>
.stApp{background-color:#e8f5e9!important;}
.main .block-container{background-color:#e8f5e9!important;}
.stForm{background-color:#a5d6a7!important; border:3px solid #2e7d32!important; border-radius:15px!important; padding:25px!important;}
[data-testid="stDataFrame"]{background-color:#c8e6c9!important; border:2px solid #81c784!important; border-radius:10px!important;}
.stTabs [data-baseweb="tab-list"]{background-color:#a5d6a7!important; border-radius:10px!important; padding:5px!important;}
.stTabs [data-baseweb="tab"]{background-color:#81c784!important; color:#1b5e20!important; font-weight:bold!important; border-radius:8px!important;}
.stTabs [aria-selected="true"]{background-color:#2e7d32!important; color:white!important;}
.stAlert{background-color:#c8e6c9!important; border:2px solid #2e7d32!important;}
.stButton>button{background-color:#d32f2f!important; color:white!important; border:3px solid #b71c1c!important; font-weight:bold!important; border-radius:10px!important; font-size:16px!important;}
.stButton>button:hover{background-color:#b71c1c!important;}
div[data-testid="stFormSubmitButton"]>button{background-color:#d32f2f!important; color:white!important; border:3px solid #b71c1c!important; font-weight:bold!important;}
.stTextInput>div>div>input, .stTextArea>div>div>textarea{background-color:#f1f8e9!important; border:2px solid #66bb6a!important;}
</style>
""", unsafe_allow_html=True)

if "interventi_lista" not in st.session_state:
    st.session_state.interventi_lista=[]
if "dashboard" not in st.session_state:
    st.session_state.dashboard=True

def tasto_dashboard(key_suffix=""):
    if st.button("🏠 Torna alla Dashboard", use_container_width=True, key=f"dash_{key_suffix}"):
        st.session_state.dashboard=True
        st.rerun()
    st.divider()

if st.session_state.dashboard:
    st.markdown("<h1 style='text-align:center; color:#2e7d32; background-color:#a5d6a7; padding:15px; border-radius:15px; border:3px solid #2e7d32;'>🟢 ANA Varese - Dashboard</h1>", unsafe_allow_html=True)
    c1,c2=st.columns([1,2])
    with c1:
        st.markdown(f"<div style='background-color:#a5d6a7; padding:15px; border-radius:10px; border:2px solid #2e7d32; text-align:center;'><b>Interventi</b><br><span style='font-size:24px;'>{len(st.session_state.interventi_lista)}</span></div>", unsafe_allow_html=True)
    with c2:
        if st.button("🚀 ENTRA NEI FORM OPERATIVI", use_container_width=True, type="primary"):
            st.session_state.dashboard=False
            st.rerun()
    st.divider()
    if st.session_state.interventi_lista:
        st.markdown("### 📋 Anteprima - Foglio Verde ANA")
        st.dataframe(pd.DataFrame(st.session_state.interventi_lista), use_container_width=True)
    else:
        st.info("Nessun intervento - Entra nei form")
    st.stop()

st.markdown("<h2 style='color:#2e7d32; background-color:#a5d6a7; padding:10px; border-radius:10px;'>🟢 ANA Varese - Gestione</h2>", unsafe_allow_html=True)
tasto_dashboard("top")

def pagina_interventi_emergenza():
    st.markdown("<div style='background-color:#a5d6a7; padding:12px; border-radius:10px; border:2px solid #2e7d32;'><h3 style='color:#1b5e20; margin:0;'>🚨 INTERVENTI EMERGENZA - Verde ANA</h3></div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🏠 Torna alla Dashboard", key="dash_em_top"):
        st.session_state.dashboard=True
        st.rerun()
    with st.form("form_emergenza", clear_on_submit=True):
        c1,c2,c3=st.columns(3)
        with c1:
            data_int=st.date_input("Data *")
            ora_int=st.time_input("Ora *")
        with c2:
            comune_int=st.text_input("Comune *", placeholder="Varese")
            via_int=st.text_input("Via *", placeholder="Via Roma")
        with c3:
            civico_int=st.text_input("Civico")
            odv_int=st.selectbox("ODV Operativa *", ["ANA Varese","ANA Sezione Varese","Protezione Civile Lombardia","Croce Rossa","Altro"])
        azione_int=st.text_area("Azione *", height=100)
        salva=st.form_submit_button("🔴 SALVA INTERVENTO - TASTO ROSSO", use_container_width=True)
        if salva:
            if comune_int and via_int and azione_int:
                st.session_state.interventi_lista.append({"Data":str(data_int),"Ora":str(ora_int),"Comune":comune_int,"Via":via_int,"Civico":civico_int,"ODV Operativa":odv_int,"Azione":azione_int})
                st.success("Salvato!")
                st.rerun()
            else:
                st.error("Compila campi *")
    if st.session_state.interventi_lista:
        df=pd.DataFrame(st.session_state.interventi_lista)
        st.markdown("#### 📋 Foglio Verde ANA")
        st.dataframe(df, use_container_width=True)
        st.download_button("📥 Scarica CSV", df.to_csv(index=False).encode('utf-8'), "interventi_emergenza.csv", use_container_width=True)
    st.divider()
    if st.button("🏠 Torna alla Dashboard", key="dash_em_bottom"):
        st.session_state.dashboard=True
        st.rerun()

tab1, tab2, tab3 = st.tabs(["Da Anagrafica Esistente", "Inserimento Manuale", "INTERVENTI EMERGENZA"])
with tab1:
    st.markdown("<div style='background-color:#a5d6a7; padding:10px; border-radius:8px;'><b>📚 Da Anagrafica - Verde ANA</b></div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🏠 Torna alla Dashboard", key="dash_t1_top"):
        st.session_state.dashboard=True
        st.rerun()
    st.info("PRIMA PAGINA COME PRIMA - RIPRISTINATA - Sfondo Verde ANA")
    st.divider()
    tasto_dashboard("t1_bot")
with tab2:
    st.markdown("<div style='background-color:#a5d6a7; padding:10px; border-radius:8px;'><b>✏️ Manuale - Verde ANA</b></div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🏠 Torna alla Dashboard", key="dash_t2_top"):
        st.session_state.dashboard=True
        st.rerun()
    st.info("Form originale - Sfondo Verde ANA")
    st.divider()
    tasto_dashboard("t2_bot")
with tab3:
    pagina_interventi_emergenza()

st.divider()
tasto_dashboard("final")
