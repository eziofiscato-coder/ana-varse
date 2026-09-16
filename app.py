import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="ANA Varese", layout="wide")

st.markdown("""
<style>
.stApp{background-color:#e8f5e9!important}
.stForm{background-color:#f1f8e9!important; border:2px solid #81c784!important; border-radius:12px!important; padding:20px!important}
.stButton>button{background-color:#d32f2f!important; color:white!important; border:2px solid #b71c1c!important; font-weight:bold!important}
</style>
""", unsafe_allow_html=True)

st.markdown("## ANA Varese - Dashboard")
st.divider()

if "interventi_lista" not in st.session_state:
    st.session_state.interventi_lista=[]

def pagina_interventi_emergenza():
    st.markdown("## INTERVENTI EMERGENZA")
    with st.form("form_emergenza", clear_on_submit=True):
        c1,c2,c3=st.columns(3)
        with c1:
            data_int=st.date_input("Data *")
            ora_int=st.time_input("Ora *")
        with c2:
            comune_int=st.text_input("Comune *")
            via_int=st.text_input("Via *")
        with c3:
            civico_int=st.text_input("Civico")
            odv_int=st.selectbox("ODV Operativa *", ["ANA Varese","ANA Sezione Varese","Protezione Civile Lombardia","Croce Rossa","Altro"])
        azione_int=st.text_area("Azione *", height=100)
        salva=st.form_submit_button("SALVA INTERVENTO EMERGENZA", use_container_width=True)
        if salva:
            if not comune_int or not via_int or not azione_int:
                st.error("Compila campi *")
            else:
                st.session_state.interventi_lista.append({"Data":str(data_int),"Ora":str(ora_int),"Comune":comune_int,"Via":via_int,"Civico":civico_int,"ODV Operativa":odv_int,"Azione":azione_int})
                st.success("Salvato!")
                st.rerun()
    if st.session_state.interventi_lista:
        df=pd.DataFrame(st.session_state.interventi_lista)
        st.dataframe(df, use_container_width=True)
        st.download_button("Scarica CSV", df.to_csv(index=False).encode('utf-8'), "interventi_emergenza.csv")

tab1, tab2, tab3 = st.tabs(["Da Anagrafica Esistente", "Inserimento Manuale", "INTERVENTI EMERGENZA"])
with tab1:
    st.markdown("### Da Anagrafica Esistente")
    st.info("PRIMA PAGINA COME PRIMA")
with tab2:
    st.markdown("### Inserimento Manuale")
    st.info("Form originale")
with tab3:
    pagina_interventi_emergenza()
