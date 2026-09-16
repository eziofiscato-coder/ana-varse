import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="ANA Varese - Gestione", layout="wide")

st.markdown("""
<style>
.stApp, .main, [data-testid="stAppViewContainer"], .block-container { background-color: #e8f5e9!important; }
.stForm { background-color: #f1f8e9!important; border: 2px solid #81c784!important; border-radius: 12px!important; padding: 20px!important; }
[data-testid="stSidebar"] { background-color: #c8e6c9!important; }
.stButton > button, button { background-color: #d32f2f!important; color: white!important; border: 2px solid #b71c1c!important; font-weight: bold!important; border-radius: 8px!important; }
.stButton > button:hover { background-color: #b71c1c!important; }
input, textarea, select { background-color: white!important; }
h1,h2,h3 { color: #2e7d32!important; }
</style>
""", unsafe_allow_html=True)

def header_3_loghi():
    c1,c2,c3,c4=st.columns([1,1,1,3])
    with c1: st.markdown("### 🟢 ANA")
    with c2: st.markdown("### 🔴 PC")
    with c3: st.markdown("### 🇮🇹")
    with c4: st.markdown("## ANA Varese - Gestione Interventi")

header_3_loghi()
st.divider()

def pagina_interventi():
    st.markdown("## INTERVENTI")
    st.markdown("### Registrazione Interventi Protezione Civile")
    if "interventi_lista" not in st.session_state:
        st.session_state.interventi_lista=[]
    with st.form("form_intervento", clear_on_submit=True):
        st.markdown("#### Nuovo Intervento")
        col1,col2=st.columns(2)
        with col1:
            data_int=st.date_input("Data *", value=datetime.now())
            ora_int=st.time_input("Ora *")
            comune_int=st.text_input("Comune *", placeholder="Varese")
        with col2:
            via_int=st.text_input("Via *", placeholder="Via Roma")
            civico_int=st.text_input("Civico", placeholder="10")
            odv_int=st.selectbox("ODV Operativa *", ["ANA Varese","ANA Sezione Varese","Protezione Civile Lombardia","Croce Rossa","Vigili del Fuoco Volontari","Altro"])
        azione_int=st.text_area("Azione *", placeholder="Descrivi azione...", height=120)
        salva=st.form_submit_button("SALVA INTERVENTO", use_container_width=True)
        if salva:
            if not comune_int or not via_int or not azione_int:
                st.error("Compila campi *")
            else:
                st.session_state.interventi_lista.append({"Data":str(data_int),"Ora":str(ora_int),"Comune":comune_int,"Via":via_int,"Civico":civico_int,"ODV Operativa":odv_int,"Azione":azione_int})
                st.success(f"Salvato! Totale: {len(st.session_state.interventi_lista)}")
                st.rerun()
    st.divider()
    st.markdown("### Elenco Interventi")
    if st.session_state.interventi_lista:
        df=pd.DataFrame(st.session_state.interventi_lista)
        st.dataframe(df, use_container_width=True)
        csv=df.to_csv(index=False).encode('utf-8')
        st.download_button("Scarica CSV", csv, "interventi.csv", "text/csv", use_container_width=True)
        if st.button("Cancella Tutti"):
            st.session_state.interventi_lista=[]
            st.rerun()
    else:
        st.info("Nessun intervento")

tabs=st.tabs(["INTERVENTI","Da Anagrafica Esistente","Inserimento Manuale"])
with tabs[0]:
    pagina_interventi()
with tabs[1]:
    st.markdown("## Da Anagrafica Esistente")
    st.info("Contenuto originale")
with tabs[2]:
    st.markdown("## Inserimento Manuale")
    st.info("Contenuto originale")
