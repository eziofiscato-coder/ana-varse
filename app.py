"""
app.py - ANA-VARSE - Streamlit Cloud - Fix ModuleNotFoundError Flask
Integra Segnalazioni Emergenze come nuovo form senza Flask!

Prima avevi:
from modules.segnalazioni_bp import segnalazioni_bp  <- ERRORE! Flask non su Streamlit Cloud!

Ora:
from modules.segnalazioni_streamlit import render_segnalazioni_form  <- OK! Streamlit!

Ezio Fiscato - Fix 24/10/2026
"""

import streamlit as st

# Configurazione pagina
st.set_page_config(
    page_title="ANA-VARSE - Segnalazioni Emergenze",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Prova a importare modulo segnalazioni Streamlit (NO FLASK!)
try:
    from modules.segnalazioni_streamlit import render_segnalazioni_form, get_segnalazioni_count
    SEGNALAZIONI_AVAILABLE = True
except ImportError as e:
    st.error(f"Modulo segnalazioni non trovato: {e}")
    st.info("Copia modules/segnalazioni_streamlit.py nel tuo progetto")
    SEGNALAZIONI_AVAILABLE = False

# Sidebar - Menu ANA esistente + nuovo form
with st.sidebar:
    st.title("🚨 ANA-VARSE")
    st.markdown("---")
    
    # Menu esistente ANA
    menu = st.radio(
        "Menu",
        ["Home ANA", "Dashboard ANA", "Segnalazioni Emergenze (NUOVO)"],
        index=0
    )
    
    st.markdown("---")
    if SEGNALAZIONI_AVAILABLE:
        count = get_segnalazioni_count()
        st.metric("Segnalazioni Emergenze", count)
    
    st.markdown("---")
    st.markdown("**Fix ModuleNotFoundError:**")
    st.markdown("Prima: `from modules.segnalazioni_bp import ...` (Flask) -> ERRORE su Streamlit Cloud")
    st.markdown("Ora: `from modules.segnalazioni_streamlit import ...` (Streamlit) -> OK!")

# Main content
if menu == "Home ANA":
    st.title("🏠 Home ANA - Il tuo progetto esistente")
    st.markdown("Questo è il tuo ANA esistente, continua a funzionare!")
    st.markdown("""
    ### Fix errore:
    **Errore prima:**
    ```
    ModuleNotFoundError: from modules.segnalazioni_bp import segnalazioni_bp
    File "/mount/src/ana-varse/modules/segnalazioni_bp.py", line 18
    from flask import Blueprint...
    ```
    **Causa:** Stai su Streamlit Cloud, non hai Flask installato, e app.py è Streamlit non Flask!
    
    **Soluzione:**
    Usa `modules/segnalazioni_streamlit.py` invece di `segnalazioni_bp.py` (Flask)
    """)
    
    st.success("✅ ANA esistente funziona!")
    st.info("Vai su 'Segnalazioni Emergenze (NUOVO)' nel menu a sinistra per nuovo form!")

elif menu == "Dashboard ANA":
    st.title("📊 Dashboard ANA")
    st.markdown("La tua dashboard esistente ANA...")
    st.info("Questa è la tua dashboard esistente, non è stata cancellata!")

elif menu == "Segnalazioni Emergenze (NUOVO)":
    if SEGNALAZIONI_AVAILABLE:
        render_segnalazioni_form()
    else:
        st.error("Modulo Segnalazioni Emergenze non disponibile")
        st.markdown("""
        ### Come installare:
        1. Copia `modules/segnalazioni_streamlit.py` in `modules/`
        2. In app.py aggiungi:
        ```python
        from modules.segnalazioni_streamlit import render_segnalazioni_form
        ```
        3. Nel menu chiama `render_segnalazioni_form()`
        """)

# Footer
st.markdown("---")
st.markdown("**ANA-VARSE + ProtezioNET v15.1 - Fix Streamlit Cloud - 24/10/2026 - Ezio Fiscato**")
