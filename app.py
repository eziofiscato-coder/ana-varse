import streamlit as st
import pandas as pd

st.set_page_config(page_title="ANA Varese", layout="wide")

APP_PASSWORD = "ANA2025"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "dashboard_entered" not in st.session_state:
    st.session_state.dashboard_entered = False
if "interventi_lista" not in st.session_state:
    st.session_state.interventi_lista = []

# === 1. PAGINA PASSWORD COME PRIMA ===
if not st.session_state.authenticated:
    st.markdown("""<style>[data-testid="stSidebar"]{display:none;}</style>""", unsafe_allow_html=True)
    c1,c2,c3,c4 = st.columns([1,1,1,1])
    with c2:
        try: st.image("logo.png", width=100)
        except: st.markdown("### ANA")
    with c3:
        try: st.image("logo2.png", width=100)
        except: st.markdown("### Varese")
    st.markdown("<h2 style='text-align:center; color:#2e7d32;'>🔐 Accesso Riservato<br>ANA Varese</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>Inserisci password per continuare</p>", unsafe_allow_html=True)
    pwd = st.text_input("Password", type="password", placeholder="Inserisci password")
    col1,col2,col3 = st.columns([1,2,1])
    with col2:
        if st.button("🔓 Accedi", use_container_width=True, type="primary"):
            if pwd == APP_PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Password errata!")
    st.stop()

# === 2. PAGINA INTERMEDIA CHE FA ENTRARE IN DASHBOARD ===
if not st.session_state.dashboard_entered:
    st.markdown("""
    <style>
    .stApp{background-color:#e8f5e9!important;}
    [data-testid="stSidebar"]{display:none;}
    </style>
    """, unsafe_allow_html=True)
    
    # Loghi
    c1,c2,c3 = st.columns([1,1,1])
    try:
        import os
        if os.path.exists("logo.png"): c1.image("logo.png", width=120)
        if os.path.exists("logo2.png"): c2.image("logo2.png", width=120)
        if os.path.exists("logo_pc_lombardia.png"): c3.image("logo_pc_lombardia.png", width=120)
    except:
        pass
    
    st.divider()
    st.markdown("<h1 style='text-align:center; color:#2e7d32;'>🟢 ANA Varese - Protezione Civile</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center;'>Benvenuto! Sei autenticato.</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; font-size:18px;'>Clicca sul pulsante per entrare nella Dashboard operativa</p>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    col1,col2,col3 = st.columns([1,2,1])
    with col2:
        st.markdown("""
        <div style='background-color:white; padding:20px; border-radius:12px; border:2px solid #81c784; text-align:center;'>
        <h4>📋 Cosa troverai in Dashboard:</h4>
        <p>✅ Anagrafica Volontari<br>✅ Interventi Emergenza<br>✅ Gestione Eventi</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 ENTRA NELLA DASHBOARD", use_container_width=True, type="primary"):
            st.session_state.dashboard_entered = True
            st.rerun()
        
        if st.button("🔒 Esci", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()
    st.stop()

# === 3. DASHBOARD VERA ===
st.markdown("""
<style>
.stApp{background-color:#e8f5e9!important;}
.main .block-container{background-color:rgba(255,255,255,0.93)!important;border-radius:18px;padding:25px!important;}
[data-testid="stSidebar"]{background-color:#a5d6a7!important;}
.stForm{background-color:#f1f8e9!important;border:2px solid #81c784!important;border-radius:12px!important;padding:20px!important;}
.stButton>button{background-color:#d32f2f!important;color:white!important;border:2px solid #b71c1c!important;font-weight:bold!important;}
</style>
""", unsafe_allow_html=True)

# Sidebar con logout
with st.sidebar:
    st.markdown("### 🟢 ANA Varese")
    st.markdown(f"Utente autenticato ✅")
    if st.button("🔒 Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.dashboard_entered = False
        st.rerun()
    if st.button("🏠 Torna a Home", use_container_width=True):
        st.session_state.dashboard_entered = False
        st.rerun()

# Header loghi dashboard
c1,c2,c3 = st.columns([1,1,1])
try:
    import os
    if os.path.exists("logo.png"): c1.image("logo.png", width=80)
    if os.path.exists("logo2.png"): c2.image("logo2.png", width=80)
    if os.path.exists("logo_pc_lombardia.png"): c3.image("logo_pc_lombardia.png", width=80)
except:
    pass

st.markdown("## 🟢 Dashboard - ANA Varese")
st.divider()

def pagina_anagrafica():
    st.markdown("### 📚 Da Anagrafica Esistente")
    st.markdown("**PRIMA PAGINA DASHBOARD**")
    st.info("Qui va il tuo form anagrafica originale")
    if st.session_state.interventi_lista:
        st.markdown("#### Ultimi Interventi Emergenza:")
        st.dataframe(pd.DataFrame(st.session_state.interventi_lista).tail(5), use_container_width=True)

def pagina_interventi_emergenza():
    st.markdown("## 🚨 INTERVENTI EMERGENZA")
    st.markdown("### Elenco Interventi - Protezione Civile")
    # SOLO VISUALIZZAZIONE, NO FORM INSERIMENTO MANUALE (cancellato come richiesto)
    if st.session_state.interventi_lista:
        df = pd.DataFrame(st.session_state.interventi_lista)
        st.dataframe(df, use_container_width=True)
        st.download_button("📥 Scarica CSV", df.to_csv(index=False).encode('utf-8'), "interventi_emergenza.csv", use_container_width=True)
        st.success(f"Totale interventi: {len(st.session_state.interventi_lista)}")
    else:
        st.info("Nessun intervento emergenza registrato")
        st.markdown("Gli interventi verranno visualizzati qui automaticamente.")

# DASHBOARD CON 2 PAGINE - INSERIMENTO MANUALE CANCELLATO
tab1, tab2 = st.tabs(["📚 Da Anagrafica Esistente", "🚨 INTERVENTI EMERGENZA"])

with tab1:
    pagina_anagrafica()

with tab2:
    pagina_interventi_emergenza()

st.divider()
st.caption("ANA Varese | Password: ANA2025 | Dashboard senza inserimento manuale")
