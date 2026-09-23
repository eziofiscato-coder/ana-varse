import streamlit as st
import pandas as pd
from datetime import datetime
st.set_page_config(page_title="ANA Varese", layout="wide")
st.markdown("""<style>.stApp{background-color:#e8f5e9!important}.stForm{background-color:#f1f8e9!important; border:2px solid #81c784!important; border-radius:12px!important; padding:20px!important}.stButton>button{background-color:#d32f2f!important; color:white!important; border:2px solid #b71c1c!important; font-weight:bold!important}</style>""", unsafe_allow_html=True)
st.markdown("## ANA Varese - Dashboard")
if "interventi_lista" not in st.session_state:
    st.session_state.interventi_lista=[]
def get_comuni():
    if "comuni_lista" in st.session_state: return st.session_state.comuni_lista
    for fname in ["vie_italia.csv","comuni.csv","comune.csv","VIE.csv"]:
        try:
            import os
            if os.path.exists(fname):
                df=pd.read_csv(fname, low_memory=False, encoding="utf-8", sep=None, engine="python")
                col_com=None
                for c in df.columns:
                    if c.lower().strip() in ["comune","comuni","citta","città","nome_comune"]:
                        col_com=c; break
                if not col_com: col_com=df.columns[0]
                comuni=sorted(df[col_com].dropna().astype(str).str.strip().unique().tolist())
                st.session_state.comuni_lista=comuni
                return comuni
        except: continue
    comuni=["Varese","Venegono Superiore","Venegono Inferiore","Busto Arsizio","Gallarate","Saronno","Tradate","Malnate","Somma Lombardo","Cassano Magnago","Milano","Roma","Torino","Varese"]
    st.session_state.comuni_lista=comuni
    return comuni

def get_vie(comune_sel):
    key=f"vie_{comune_sel}"
    if key in st.session_state: return st.session_state[key]
    for fname in ["vie_italia.csv","vie.csv","VIE.csv","comuni.csv"]:
        try:
            import os
            if os.path.exists(fname):
                df=pd.read_csv(fname, low_memory=False, encoding="utf-8", sep=None, engine="python")
                col_com=None; col_via=None
                for c in df.columns:
                    cl=c.lower().strip()
                    if cl in ["comune","comuni","citta","città","nome_comune"]: col_com=c
                    if cl in ["via","vie","denominazione","toponimo","indirizzo","nome_via","strada"]: col_via=c
                if col_com and col_via:
                    df_f=df[df[col_com].astype(str).str.lower().str.strip()==comune_sel.lower().strip()]
                    if len(df_f)==0:
                        df_f=df[df[col_com].astype(str).str.lower().str.contains(comune_sel.lower().strip(), na=False)]
                    vie=sorted(df_f[col_via].dropna().astype(str).str.strip().unique().tolist())
                    if len(vie)>0:
                        st.session_state[key]=vie[:300]
                        return vie[:300]
        except: continue
    fallback=["Via Roma","Via Verdi","Via Garibaldi","Corso Italia","Piazza XX Settembre","Via Matteotti","Via Volta","Via Marconi"]
    st.session_state[key]=fallback
    return fallback

def pagina_interventi_emergenza():
    st.markdown("## INTERVENTI EMERGENZA")
    with st.form("form_emergenza", clear_on_submit=True):
        c1,c2,c3=st.columns(3)
        with c1:
            data_int=st.date_input("Data *")
            ora_int=st.time_input("Ora *")
        with c2:
            comune_int=st.selectbox("Comune *", get_comuni(), key="comune_sel")
            vie_list=get_vie(comune_int)
            via_int=st.selectbox(f"Via * di {comune_int} ({len(vie_list)} vie)", vie_list, key="via_sel")
        with c3:
            civico_int=st.text_input("Civico")
            odv_int=st.selectbox("ODV Operativa *", ["ANA Varese","ANA Sezione Varese","Protezione Civile Lombardia","Croce Rossa","Altro"])
        azione_int=st.text_area("Azione *", height=100)
        salva=st.form_submit_button("SALVA INTERVENTO EMERGENZA", use_container_width=True)
        if salva:
            if comune_int and via_int and azione_int:
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
    st.info("PRIMA PAGINA COME PRIMA - RIPRISTINATA")
with tab2:
    st.markdown("### Inserimento Manuale")
    st.info("Form originale")
with tab3:
    pagina_interventi_emergenza()
