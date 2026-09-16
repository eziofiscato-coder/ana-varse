import streamlit as st
import pandas as pd

st.set_page_config(page_title="ANA Varese - Gestionale", page_icon="🎖️", layout="wide")

# ===== PAGINA PASSWORD COME PRIMA =====
APP_PASSWORD = "ANA2025"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("""<style>[data-testid="stSidebar"]{display:none;}</style>""", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns([1,1,1,1])
    with c2:
        try:
            st.image("logo.png", width=80)
        except:
            st.markdown("### ANA")
    with c3:
        try:
            st.image("logo2.png", width=80)
        except:
            st.markdown("### Varese")
    st.markdown("<h2 style='text-align:center; color:#2e7d32;'>🔐 Accesso Riservato<br>ANA Varese</h2>", unsafe_allow_html=True)
    pwd = st.text_input("Password", type="password", placeholder="Inserisci password")
    if st.button("🔓 Accedi", use_container_width=True, type="primary"):
        if pwd == APP_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Password errata!")
    st.stop()

# CSS VERDE CHIARO + TASTI ROSSI
st.markdown("""
<style>
.stApp{background-color:#e8f5e9!important;}
.main .block-container{background-color:rgba(255,255,255,0.93)!important;border-radius:18px;padding:25px!important;}
[data-testid="stSidebar"]{background-color:#a5d6a7!important;}
.stForm{background-color:#f1f8e9!important;border:2px solid #81c784!important;border-radius:12px!important;padding:20px!important;}
.stButton>button{background-color:#d32f2f!important;color:white!important;border:2px solid #b71c1c!important;font-weight:bold!important;}
</style>
""", unsafe_allow_html=True)

def header_3_loghi():
    c1,c2,c3=st.columns([1,1,1])
    try:
        import os
        if os.path.exists("logo.png"): c1.image("logo.png", width=80)
        if os.path.exists("logo2.png"): c2.image("logo2.png", width=80)
        if os.path.exists("logo_pc_lombardia.png"): c3.image("logo_pc_lombardia.png", width=80)
    except:
        pass
header_3_loghi()
st.divider()

if "interventi_lista" not in st.session_state:
    st.session_state.interventi_lista=[]

def pagina_interventi_emergenza():
    st.markdown("## 🚨 INTERVENTI EMERGENZA")
    with st.form("form_emergenza", clear_on_submit=True):
        st.markdown("#### 📋 Dati Intervento")
        c1,c2,c3=st.columns(3)
        with c1:
            data_int=st.date_input("Data *")
            ora_int=st.time_input("Ora *")
        with c2:
            comune_int=st.text_input("Comune *", placeholder="Varese")
            via_int=st.text_input("Via *", placeholder="Via Roma")
        with c3:
            civico_int=st.text_input("Civico", placeholder="10")
            odv_int=st.selectbox("ODV Operativa *", ["ANA Varese","ANA Sezione Varese","Protezione Civile Lombardia","Croce Rossa","Altro"])
        azione_int=st.text_area("Azione *", placeholder="Descrivi azione...", height=120)
        salva=st.form_submit_button("🚨 SALVA INTERVENTO EMERGENZA", use_container_width=True)
        if salva:
            if not comune_int or not via_int or not azione_int:
                st.error("Compila campi obbligatori *")
            else:
                st.session_state.interventi_lista.append({"Data":str(data_int),"Ora":str(ora_int),"Comune":comune_int,"Via":via_int,"Civico":civico_int,"ODV Operativa":odv_int,"Azione":azione_int})
                st.success("Intervento salvato!")
                st.rerun()
    st.divider()
    if st.session_state.interventi_lista:
        df=pd.DataFrame(st.session_state.interventi_lista)
        st.dataframe(df, use_container_width=True)
        st.download_button("📥 Scarica CSV", df.to_csv(index=False).encode('utf-8'), "interventi_emergenza.csv")

# SOLO 2 TAB - SECONDA PAGINA TOLTA
tab1, tab2 = st.tabs(["📚 Da Anagrafica Esistente", "🚨 INTERVENTI EMERGENZA"])

with tab1:
    st.markdown("### 📚 Da Anagrafica Esistente")
    st.info("PRIMA PAGINA - come prima con password")
    if st.session_state.interventi_lista:
        st.dataframe(pd.DataFrame(st.session_state.interventi_lista).tail(5))

with tab2:
    pagina_interventi_emergenza()
