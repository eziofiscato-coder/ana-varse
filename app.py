
import streamlit as st
import pandas as pd
import os
from datetime import datetime, date
from fpdf import FPDF
from io import BytesIO

st.set_page_config(page_title="ANA Varese - Protezione Civile", page_icon="🎖️", layout="wide")

# SFONDO VERDE CHIARO
st.markdown("""<style>
.stApp{background-color:#e8f5e9 !important;}
.main .block-container{background-color:rgba(255,255,255,0.93) !important;border-radius:18px;padding:25px !important;box-shadow:0 4px 20px rgba(0,0,0,0.08);}
[data-testid="stSidebar"]{background-color:#a5d6a7 !important;}
h1,h2,h3{color:#2e7d32 !important;}
</style>""", unsafe_allow_html=True)

# --- PDF CON LOGHI 80px equivalenti ---
class PDFConLogo(FPDF):
    def header(self):
        try:
            self.set_fill_color(232, 245, 233)
            self.rect(0, 0, 210, 28, "F")
            if os.path.exists("logo.png"):
                self.image("logo.png", x=10, y=5, w=18)
            if os.path.exists("logo2.png"):
                self.image("logo2.png", x=182, y=5, w=18)
            self.set_y(8)
            self.set_font("Arial", "B", 11)
            self.set_text_color(27, 94, 32)
            self.cell(0, 10, "ANA Varese - Protezione Civile", align="C", ln=True)
            self.ln(8)
        except:
            pass
    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Pagina {self.page_no()} - Generato {datetime.now().strftime('%d/%m/%Y %H:%M')}", align="C")

# --- SESSION STATE ---
if "entered" not in st.session_state:
    st.session_state.entered = False
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "page" not in st.session_state:
    st.session_state.page = "dashboard"
if "eventi" not in st.session_state:
    st.session_state.eventi = []
if "checkin" not in st.session_state:
    st.session_state.checkin = {}  # key: evento_id -> list volontari
if "volontari" not in st.session_state:
    st.session_state.volontari = []

APP_PASSWORD = "ANA2025"

# --- LOGIN ---
if not st.session_state.authenticated:
    st.markdown("<style>[data-testid='stSidebar']{display:none;}</style>", unsafe_allow_html=True)
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
    st.markdown("<h2 style='text-align:center; color:#2e7d32;'>🔐 Accesso Riservato<br>ANA Varese - Protezione Civile</h2>", unsafe_allow_html=True)
    pwd = st.text_input("Password", type="password", placeholder="Inserisci password")
    if st.button("🔓 Accedi", use_container_width=True, type="primary"):
        if pwd == APP_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Password errata!")
    st.stop()

# --- SIDEBAR ---
st.sidebar.markdown("### 🎖️ ANA Varese")
if st.sidebar.button("🔒 Logout", use_container_width=True):
    st.session_state.authenticated = False
    st.session_state.entered = False
    st.rerun()
st.sidebar.divider()
if st.sidebar.button("🏠 Dashboard", use_container_width=True):
    st.session_state.page = "dashboard"
    st.rerun()
if st.sidebar.button("📅 Gestione Eventi", use_container_width=True):
    st.session_state.page = "evento_lista"
    st.rerun()
if st.sidebar.button("📝 Check-In Volontari", use_container_width=True):
    st.session_state.page = "checkin"
    st.rerun()

# --- PAGINA PRESENTAZIONE ---
if not st.session_state.entered:
    col1, col2, col3, col4 = st.columns([1,1,1,1])
    with col2:
        try:
            st.image("logo.png", width=80)
        except:
            pass
    with col3:
        try:
            st.image("logo2.png", width=80)
        except:
            pass
    st.markdown("<h1 style='text-align:center; color:#1b5e20;'>🎖️ ANA - ASSOCIAZIONE NAZIONALE ALPINI<br>Sezione di Varese<br><small style='color:#388e3c;'>Protezione Civile</small></h1>", unsafe_allow_html=True)
    st.markdown('<div style="background:#c8e6c9; padding:20px; border-radius:15px; text-align:center;"><h3>Sistema Gestione Volontari, Eventi e Check-In</h3><p>Gestione completa servizi, radio, distribuzione, mappa e volontari</p></div>', unsafe_allow_html=True)
    if st.button("🚀 ENTRA NEL SISTEMA", use_container_width=True, type="primary"):
        st.session_state.entered = True
        st.rerun()
    st.stop()

# --- PAGINA EVENTO FORM ---
def pagina_crea_evento():
    st.title("📅 Crea Nuovo Evento / Servizio")
    if st.button("⬅️ Torna a Lista Eventi"):
        st.session_state.page = "evento_lista"
        st.rerun()
    
    st.markdown('<div style="background:#e8f5e9; padding:12px; border-radius:8px; border-left:5px solid #2e7d32;">Compila tutti i campi obbligatori *</div>', unsafe_allow_html=True)
    
    with st.form("form_evento", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            tipo_servizio = st.selectbox("🔧 TIPO DI SERVIZIO *", ["Seleziona...","Monitoraggio idrogeologico","Antincendio boschivo","Supporto emergenza","Esercitazione","Manifestazione pubblica","Ricerca persone","Alluvione / Esondazione","Neve / Ghiaccio","Assistenza popolazione","Presidio / Sorveglianza","Altro"])
            descrizione = st.text_area("📝 DESCRIZIONE EVENTO *", height=120, placeholder="Dettagli evento...")
            comune = st.text_input("🏘️ COMUNE *", placeholder="Es: Varese")
            provincia = st.selectbox("📍 PROVINCIA *", ["Seleziona...","VA - Varese","MI - Milano","CO - Como","MB - Monza Brianza","LC - Lecco","LO - Lodi","PV - Pavia","CR - Cremona","MN - Mantova","BG - Bergamo","BS - Brescia","SO - Sondrio","Altra"])
        with col2:
            data_inizio = st.date_input("📅 DATA INIZIO *", value=date.today())
            ora_inizio = st.time_input("⏰ ORA INIZIO *")
            data_fine = st.date_input("📅 DATA FINE *", value=date.today())
            ora_fine = st.time_input("⏰ ORA FINE *")
            organizzazione = st.text_input("🏢 ORGANIZZAZIONE *", placeholder="Es: ANA Varese - Nucleo PC")
            responsabile = st.text_input("👤 RESPONSABILE *", placeholder="Nome Cognome")
            cellulare_resp = st.text_input("📱 CELLULARE RESPONSABILE *", placeholder="347 1234567")
        
        salva = st.form_submit_button("💾 SALVA EVENTO", use_container_width=True, type="primary")
        
        if salva:
            if tipo_servizio == "Seleziona..." or not descrizione or not comune or provincia == "Seleziona..." or not organizzazione or not responsabile or not cellulare_resp:
                st.error("Compila tutti i campi obbligatori")
            else:
                evento = {
                    "ID": len(st.session_state.eventi) + 1,
                    "Tipo Servizio": tipo_servizio,
                    "Descrizione": descrizione,
                    "Comune": comune,
                    "Provincia": provincia,
                    "Data Inizio": str(data_inizio),
                    "Ora Inizio": str(ora_inizio),
                    "Data Fine": str(data_fine),
                    "Ora Fine": str(ora_fine),
                    "Organizzazione": organizzazione,
                    "Responsabile": responsabile,
                    "Cellulare Resp": cellulare_resp,
                    "Creato": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "Volontari Check-In": 0
                }
                st.session_state.eventi.append(evento)
                st.success(f"Evento salvato! ID {evento['ID']}")
                st.session_state.page = "evento_lista"
                st.rerun()

def pagina_lista_eventi():
    st.title("📋 Lista Eventi")
    col_a, col_b = st.columns([3,1])
    with col_a:
        st.markdown(f"Totale eventi: **{len(st.session_state.eventi)}**")
    with col_b:
        if st.button("➕ Nuovo Evento", use_container_width=True, type="primary"):
            st.session_state.page = "evento_crea"
            st.rerun()
    
    if not st.session_state.eventi:
        st.info("Nessun evento creato. Clicca su Nuovo Evento.")
        return
    
    df = pd.DataFrame(st.session_state.eventi)
    st.dataframe(df, use_container_width=True)
    
    # Selezione evento per check-in
    st.divider()
    st.subheader("📝 Azioni Evento")
    ids = [f"{e['ID']} - {e['Tipo Servizio']} - {e['Comune']} {e['Data Inizio']}" for e in st.session_state.eventi]
    sel = st.selectbox("Seleziona Evento per Check-In Volontari", ids)
    if sel:
        id_sel = int(sel.split(" - ")[0])
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📝 Check-In Volontari per questo Evento", use_container_width=True):
                st.session_state.evento_selezionato = id_sel
                st.session_state.page = "checkin"
                st.rerun()
        with col2:
            if st.button("📄 PDF Evento", use_container_width=True):
                # genera PDF singolo evento
                ev = [e for e in st.session_state.eventi if e["ID"]==id_sel][0]
                pdf = PDFConLogo()
                pdf.add_page()
                pdf.set_font("Arial","B",12)
                pdf.cell(0,10,f"EVENTO {ev['ID']} - {ev['Tipo Servizio']}", ln=True, align="C")
                pdf.ln(5)
                pdf.set_font("Arial","",10)
                for k,v in ev.items():
                    pdf.set_font("Arial","B",10)
                    pdf.cell(50,7,f"{k}:")
                    pdf.set_font("Arial","",10)
                    pdf.multi_cell(0,7,str(v))
                    pdf.ln(1)
                # checkin volontari
                check = st.session_state.checkin.get(id_sel, [])
                if check:
                    pdf.ln(5)
                    pdf.set_font("Arial","B",11)
                    pdf.cell(0,8,f"Volontari Check-In ({len(check)})", ln=True)
                    pdf.set_font("Arial","",9)
                    for vol in check:
                        pdf.cell(0,6,f"- {vol['Nome']} {vol['Cognome']} - {vol['ODV']} - {vol['Cellulare']} - CF: {vol['Codice Fiscale']}", ln=True)
                b = pdf.output(dest='S').encode('latin-1','ignore')
                st.download_button("📥 Scarica PDF", data=b, file_name=f"evento_{id_sel}.pdf", mime="application/pdf")
        with col3:
            if st.button("🗑️ Elimina Evento", use_container_width=True):
                st.session_state.eventi = [e for e in st.session_state.eventi if e["ID"]!=id_sel]
                st.rerun()

# --- PAGINA CHECK-IN VOLONTARI PER EVENTO ---
def pagina_checkin():
    st.title("📝 Check-In Volontari per Evento")
    
    if not st.session_state.eventi:
        st.warning("Nessun evento disponibile. Crea prima un evento.")
        if st.button("📅 Crea Evento"):
            st.session_state.page = "evento_crea"
            st.rerun()
        return
    
    # Seleziona evento
    ids = [f"{e['ID']} - {e['Tipo Servizio']} - {e['Comune']} ({e['Data Inizio']})" for e in st.session_state.eventi]
    default_idx = 0
    if "evento_selezionato" in st.session_state:
        for i, e in enumerate(st.session_state.eventi):
            if e["ID"] == st.session_state.evento_selezionato:
                default_idx = i
                break
    
    sel = st.selectbox("🎯 SELEZIONA EVENTO PER CHECK-IN", ids, index=default_idx)
    id_evento = int(sel.split(" - ")[0])
    evento = [e for e in st.session_state.eventi if e["ID"]==id_evento][0]
    
    st.markdown(f'<div style="background:#c8e6c9; padding:15px; border-radius:10px;"><b>Evento:</b> {evento["Tipo Servizio"]} - {evento["Comune"]} ({evento["Provincia"]})<br><b>Data:</b> {evento["Data Inizio"]} {evento["Ora Inizio"]} - {evento["Data Fine"]} {evento["Ora Fine"]}<br><b>Responsabile:</b> {evento["Responsabile"]} - {evento["Cellulare Resp"]}</div>', unsafe_allow_html=True)
    
    st.divider()
    st.subheader("➕ Nuovo Check-In Volontario")
    
    # FORM CHECK-IN con campi richiesti: NOME, COGNOME, ODV, CELLULARE, CODICE FISCALE, TASTO SALVA
    with st.form(f"form_checkin_{id_evento}", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("👤 NOME *", placeholder="Mario")
            cognome = st.text_input("👤 COGNOME *", placeholder="Rossi")
            odv = st.text_input("🏢 ODV *", placeholder="Es: ANA Varese, Gruppo Milano...")
        with col2:
            cellulare = st.text_input("📱 CELLULARE *", placeholder="347 1234567")
            codice_fiscale = st.text_input("🆔 CODICE FISCALE *", placeholder="RSSMRA80A01H501Z", max_chars=16)
            # Validazione CF basilare
            note = st.text_input("📝 Note (opzionale)", placeholder="Patente, attestati...")
        
        col_save, col_info = st.columns([2,1])
        with col_save:
            salva_vol = st.form_submit_button("💾 SALVA CHECK-IN", use_container_width=True, type="primary")
        with col_info:
            st.markdown("<small>* campi obbligatori</small>", unsafe_allow_html=True)
        
        if salva_vol:
            if not nome or not cognome or not odv or not cellulare or not codice_fiscale:
                st.error("Compila tutti i campi obbligatori (*)")
            elif len(codice_fiscale) != 16:
                st.error("Codice Fiscale deve essere di 16 caratteri")
            else:
                volontario = {
                    "Nome": nome.strip().upper(),
                    "Cognome": cognome.strip().upper(),
                    "ODV": odv,
                    "Cellulare": cellulare,
                    "Codice Fiscale": codice_fiscale.upper(),
                    "Note": note,
                    "Check-In": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "Evento ID": id_evento
                }
                if id_evento not in st.session_state.checkin:
                    st.session_state.checkin[id_evento] = []
                st.session_state.checkin[id_evento].append(volontario)
                # aggiorna conteggio in evento
                for e in st.session_state.eventi:
                    if e["ID"] == id_evento:
                        e["Volontari Check-In"] = len(st.session_state.checkin[id_evento])
                st.success(f"✅ Check-In salvato: {nome} {cognome}")
                st.balloons()
    
    # Lista volontari check-in per evento
    st.divider()
    lista = st.session_state.checkin.get(id_evento, [])
    st.subheader(f"👥 Volontari in Check-In per questo Evento ({len(lista)})")
    
    if lista:
        df = pd.DataFrame(lista)
        st.dataframe(df, use_container_width=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            # Excel
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name=f'CheckIn_Evento_{id_evento}')
            st.download_button("📥 Excel Check-In", data=output.getvalue(), file_name=f"checkin_evento_{id_evento}_{datetime.now().strftime('%Y%m%d')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        with col2:
            # PDF con loghi 80px
            pdf = PDFConLogo()
            pdf.add_page()
            pdf.set_font("Arial","B",12)
            pdf.cell(0,10,f"Check-In Volontari - Evento {id_evento}", ln=True, align="C")
            pdf.set_font("Arial","",10)
            pdf.cell(0,7,f"{evento['Tipo Servizio']} - {evento['Comune']} - {evento['Data Inizio']}", ln=True, align="C")
            pdf.ln(5)
            pdf.set_font("Arial","B",9)
            pdf.set_fill_color(200,230,201)
            # Header tabella
            pdf.cell(35,7,"Nome Cognome", border=1, fill=True)
            pdf.cell(35,7,"ODV", border=1, fill=True)
            pdf.cell(30,7,"Cellulare", border=1, fill=True)
            pdf.cell(45,7,"Codice Fiscale", border=1, fill=True)
            pdf.cell(35,7,"Check-In", border=1, fill=True, ln=True)
            pdf.set_font("Arial","",8)
            for v in lista:
                pdf.cell(35,6,f"{v['Nome']} {v['Cognome']}"[:18], border=1)
                pdf.cell(35,6,v['ODV'][:18], border=1)
                pdf.cell(30,6,v['Cellulare'], border=1)
                pdf.cell(45,6,v['Codice Fiscale'], border=1)
                pdf.cell(35,6,v['Check-In'], border=1, ln=True)
            b = pdf.output(dest='S').encode('latin-1','ignore')
            st.download_button("📄 PDF Check-In con Loghi", data=b, file_name=f"checkin_evento_{id_evento}.pdf", mime="application/pdf", use_container_width=True)
        with col3:
            if st.button("🗑️ Cancella Tutti Check-In Evento", use_container_width=True):
                st.session_state.checkin[id_evento] = []
                for e in st.session_state.eventi:
                    if e["ID"] == id_evento:
                        e["Volontari Check-In"] = 0
                st.rerun()
    else:
        st.info("Nessun volontario in check-in per questo evento.")

# --- ROUTING ---
if st.session_state.page == "evento_crea":
    pagina_crea_evento()
elif st.session_state.page == "evento_lista":
    pagina_lista_eventi()
elif st.session_state.page == "checkin":
    pagina_checkin()
else:
    # DASHBOARD PRINCIPALE con loghi 80px
    c1, c2, c3, c4 = st.columns([1,1,1,1])
    with c2:
        try:
            st.image("logo.png", width=80)
        except:
            st.write("ANA")
    with c3:
        try:
            st.image("logo2.png", width=80)
        except:
            st.write("Varese")
    st.markdown("### 📊 Dashboard Operativa")
    
    # Tasto evento grande
    if st.button("📅 GESTIONE EVENTO - Crea Nuovo Servizio / Evento", use_container_width=True, type="primary"):
        st.session_state.page = "evento_lista"
        st.rerun()
    
    # Dati riepilogo
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📅 Eventi Totali", len(st.session_state.eventi))
    with col2:
        tot_check = sum(len(v) for v in st.session_state.checkin.values())
        st.metric("👥 Check-In Totali", tot_check)
    with col3:
        st.metric("🏘️ Comuni Coinvolti", len(set(e["Comune"] for e in st.session_state.eventi)) if st.session_state.eventi else 0)
    
    st.divider()
    st.markdown("#### 🔧 Funzioni Operative")
    b1, b2, b3 = st.columns(3)
    with b1:
        if st.button("👥 Volontari", use_container_width=True):
            st.info("Gestione volontari - usa Check-In per evento")
        if st.button("📻 Comunicazioni", use_container_width=True):
            st.info("Modulo comunicazioni")
    with b2:
        if st.button("📝 Brogliaccio", use_container_width=True):
            st.info("Brogliaccio operativo")
        if st.button("📦 Distribuzione", use_container_width=True):
            st.info("Distribuzione materiali")
    with b3:
        if st.button("🗺️ Mappa", use_container_width=True):
            st.info("Mappa interventi")
        if st.button("📋 Registro", use_container_width=True):
            if st.session_state.eventi:
                st.dataframe(pd.DataFrame(st.session_state.eventi), use_container_width=True)
            else:
                st.warning("Nessun evento")

