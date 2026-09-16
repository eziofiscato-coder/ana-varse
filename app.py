import streamlit as st
import pandas as pd
from datetime import datetime, date
from io import BytesIO

st.set_page_config(page_title="ANA Varese FIX", layout="wide")
APP_PASSWORD="ANA2025"

for k,v in [("authenticated",False),("dashboard_entered",False),("interventi_lista",[]),("eventi",[]),("mem_nomi",["Mario Rossi"])]:
    if k not in st.session_state:
        st.session_state[k]=v

st.markdown('''
<style>
.stApp{background-color:#e8f5e9!important;}
.stForm{background-color:#a5d6a7!important; border:3px solid #2e7d32!important; border-radius:15px!important; padding:20px!important;}
[data-testid="stDataFrame"]{background-color:white!important; border:3px solid #2e7d32!important; border-radius:12px!important;}
.stButton>button{background-color:#d32f2f!important; color:white!important; border:3px solid #b71c1c!important; font-weight:bold!important; border-radius:10px!important;}
div[data-testid="stFormSubmitButton"]>button{background-color:#d32f2f!important; color:white!important;}
</style>
''', unsafe_allow_html=True)

if not st.session_state.authenticated:
    st.markdown("<h1 style='text-align:center; color:#2e7d32; background:#a5d6a7; padding:15px; border-radius:15px;'>ANA Varese</h1>", unsafe_allow_html=True)
    pwd=st.text_input("Password", type="password")
    if st.button("ACCEDI ROSSO", use_container_width=True):
        if pwd==APP_PASSWORD:
            st.session_state.authenticated=True
            st.rerun()
    st.stop()

if not st.session_state.dashboard_entered:
    st.markdown("<h1 style='text-align:center; color:#2e7d32; background:#a5d6a7; padding:15px; border-radius:15px;'>Dashboard</h1>", unsafe_allow_html=True)
    if st.button("ENTRA", use_container_width=True, type="primary"):
        st.session_state.dashboard_entered=True
        st.rerun()
    st.stop()

st.markdown("## ANA Varese - FIX Visibilita")
if st.button("Home", use_container_width=True):
    st.session_state.dashboard_entered=False
    st.rerun()

if "interventi_lista" not in st.session_state:
    st.session_state.interventi_lista=[]

with st.form("form_em", clear_on_submit=True):
    c1,c2=st.columns(2)
    with c1:
        comune=st.text_input("Comune *")
        via=st.text_input("Via *")
    with c2:
        azione=st.text_area("Azione *")
    if st.form_submit_button("SALVA ROSSO", use_container_width=True):
        if comune and via and azione:
            st.session_state.interventi_lista.append({"Comune":comune,"Via":via,"Azione":azione,"Ora":str(datetime.now())})
            st.success(f"Salvato! Totale: {len(st.session_state.interventi_lista)}")
            # FIX: non fare rerun immediato cosi vedi messaggio
            # st.rerun() rimosso

st.divider()
st.markdown("### Elenco - ORA VISIBILE SU SFONDO BIANCO")
if st.session_state.interventi_lista:
    df=pd.DataFrame(st.session_state.interventi_lista)
    st.success(f"Trovati {len(df)} record")
    st.dataframe(df, use_container_width=True, height=300)
    st.download_button("Scarica CSV", df.to_csv(index=False).encode('utf-8'), "interventi.csv", use_container_width=True)
else:
    st.info("Nessun dato - inserisci sopra e vedrai qui sotto")
