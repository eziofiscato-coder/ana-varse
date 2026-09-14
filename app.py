import streamlit as st
import pandas as pd
from io import BytesIO
import os
from datetime import datetime

st.set_page_config(page_title="ANA Varese - Telecomunicazioni", layout="wide")

if "uscito" not in st.session_state:
    st.session_state["uscito"] = False

try:
    st.image("logo.png", width=200)
except:
    pass

# TASTO ESCI in alto
col_logo, col_esci = st.columns([4,1])
with col_esci:
    if st.button("🚪 ESCI", use_container_width=True, type="secondary"):
        st.session_state["uscito"] = True

if st.session_state.get("uscito", False):
    st.markdown('''
    <div style='text-align:center; padding:50px; background-color:#f0f0f0; border-radius:15px; margin-top:30px;'>
        <h1 style='color:#0e7a3d;'>👋 Grazie per il servizio!</h1>
        <h3>Hai chiuso correttamente il registro ANA Varese</h3>
        <p>Puoi chiudere questa scheda del browser.</p>
        <br>
        <p style='font-size:14px; color:gray;'>I dati restano salvati in memoria</p>
    </div>
    ''', unsafe_allow_html=True)
    if st.button("🔓 Rientra nel sistema", use_container_width=True):
        st.session_state["uscito"] = False
        st.rerun()
    st.stop()

st.markdown("<h2 style='text-align:center; color:#0e7a3d;'>VOLONTARIATO - Sezione di Varese<br><small>Registro Telecomunicazioni</small></h2>", unsafe_allow_html=True)

FILE_DATI = "dati_iscritti.csv"
FILE_RADIO = "radio_log.csv"
FILE_MEM_MITT = "memoria_mittenti.csv"
FILE_MEM_DEST = "memoria_destinatari.csv"

# Carica dati
if "dati" not in st.session_state:
    if os.path.exists(FILE_DATI):
        try:
            st.session_state.dati = pd.read_csv(FILE_DATI).to_dict(orient="records")
        except:
            st.session_state.dati = []
    else:
        st.session_state.dati = []

if "radio_log" not in st.session_state:
    if os.path.exists(FILE_RADIO):
        try:
            st.session_state.radio_log = pd.read_csv(FILE_RADIO).to_dict(orient="records")
        except:
            st.session_state.radio_log = []
    else:
        st.session_state.radio_log = []

# Memoria Mittenti - LEGGE DA FILE SEPARATO e tiene tutto
if "mem_mitt" not in st.session_state:
    lista = ["Sala Operativa Varese", "COC Varese", "Prefettura", "Posto Comando", "ANA Varese", "Protezione Civile"]
    if os.path.exists(FILE_MEM_MITT):
        try:
            df = pd.read_csv(FILE_MEM_MITT)
            lista = df["Mittente"].dropna().unique().tolist()
        except:
            pass
    # aggiungi anche da radio_log
    if st.session_state.radio_log:
        da_log = [r.get("Mittente","") for r in st.session_state.radio_log if r.get("Mittente")]
        lista = sorted(list(set(lista + da_log)))
    st.session_state.mem_mitt = lista

if "mem_dest" not in st.session_state:
    lista = ["Squadra 1", "Squadra 2", "Tutte le squadre", "Sala Operativa", "COC"]
    if os.path.exists(FILE_MEM_DEST):
        try:
            df = pd.read_csv(FILE_MEM_DEST)
            lista = df["Destinatario"].dropna().unique().tolist()
        except:
            pass
    if st.session_state.radio_log:
        da_log = [r.get("Destinatario","") for r in st.session_state.radio_log if r.get("Destinatario")]
        lista = sorted(list(set(lista + da_log)))
    st.session_state.mem_dest = lista

if "mem_assoc" not in st.session_state:
    st.session_state.mem_assoc = sorted(list(set([d["Associazione"] for d in st.session_state.dati]))) if st.session_state.dati else ["ANA Varese", "Protezione Civile Varese"]
if "mem_nomi" not in st.session_state:
    st.session_state.mem_nomi = sorted(list(set([d["Nome"] for d in st.session_state.dati]))) if st.session_state.dati else []

def salva_dati():
    if st.session_state.dati:
        pd.DataFrame(st.session_state.dati).to_csv(FILE_DATI, index=False)

def salva_radio():
    if st.session_state.radio_log:
        pd.DataFrame(st.session_state.radio_log).to_csv(FILE_RADIO, index=False)

def salva_mem_mitt():
    pd.DataFrame({"Mittente": st.session_state.mem_mitt}).to_csv(FILE_MEM_MITT, index=False)

def salva_mem_dest():
    pd.DataFrame({"Destinatario": st.session_state.mem_dest}).to_csv(FILE_MEM_DEST, index=False)

def combo_memoria(label, mem_list, key_prefix, placeholder=""):
    opzioni = ["-- Seleziona --"] + sorted([x for x in mem_list if x]) + [f"➕ NUOVO {label.upper()}..."]
    scelta = st.selectbox(f"{label} *", opzioni, key=f"{key_prefix}_sel")
    if scelta == f"➕ NUOVO {label.upper()}...":
        nuovo = st.text_input(f"Scrivi nuovo {label} *", key=f"{key_prefix}_new", placeholder=placeholder)
        return nuovo.strip()
    elif scelta == "-- Seleziona --":
        return ""
    else:
        return scelta

# Funzione PDF
def crea_pdf_radio(df):
    try:
        from fpdf import FPDF
        pdf = FPDF(orientation='L', unit='mm', format='A4')
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "ANA VARESE - REGISTRO TELECOMUNICAZIONI", ln=True, align="C")
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 8, f"Data stampa: {datetime.now().strftime('%d/%m/%Y %H:%M')} - Totale comunicazioni: {len(df)}", ln=True, align="C")
        pdf.ln(5)
        
        # Tabella header
        pdf.set_font("Arial", "B", 8)
        col_widths = [25, 15, 30, 35, 35, 70, 70]
        headers = ["Data", "Ora", "Canale", "Mittente", "Destinatario", "Messaggio Ricevuto", "Messaggio Trasmesso"]
        for i, h in enumerate(headers):
            pdf.cell(col_widths[i], 8, h, border=1, align="C")
        pdf.ln()
        
        # Righe
        pdf.set_font("Arial", "", 7)
        for _, row in df.iterrows():
            # controlla se serve nuova pagina
            if pdf.get_y() > 180:
                pdf.add_page()
            pdf.cell(col_widths[0], 8, str(row.get("Data",""))[:10], border=1)
            pdf.cell(col_widths[1], 8, str(row.get("Ora",""))[:5], border=1)
            pdf.cell(col_widths[2], 8, str(row.get("Canale",""))[:20], border=1)
            pdf.cell(col_widths[3], 8, str(row.get("Mittente",""))[:22], border=1)
            pdf.cell(col_widths[4], 8, str(row.get("Destinatario",""))[:22], border=1)
            # messaggi troncati per PDF
            pdf.cell(col_widths[5], 8, str(row.get("Messaggio Ricevuto",""))[:50], border=1)
            pdf.cell(col_widths[6], 8, str(row.get("Messaggio Trasmesso",""))[:50], border=1)
            pdf.ln()
        
        return pdf.output(dest="S").encode("latin-1")
    except Exception as e:
        st.error(f"Errore PDF: {e}")
        return None

tab1, tab2 = st.tabs(["📋 ANAGRAFICA VOLONTARI", "📻 REGISTRO RADIO - MITTENTE/DESTINATARIO/MESSAGGI + PDF"])

with tab1:
    st.subheader("Maschera Principale - Iscrizione")
    with st.form("form_vol"):
        c1,c2 = st.columns(2)
        with c1:
            nome = st.text_input("Nome e Cognome *")
            assoc = combo_memoria("Associazione", st.session_state.mem_assoc, "assoc1", "Es: ANA Sezione Varese")
            cell = st.text_input("Cellulare *")
        with c2:
            ruolo = st.selectbox("Ruolo *", ["Volontario", "Caposquadra", "Coordinatore", "Autista", "Radio", "Telecomunicazioni", "Logistica", "Segreteria", "Sanitario", "Altro"])
            note = st.text_input("Note")
        
        if st.form_submit_button("✅ Salva Volontario", use_container_width=True):
            if nome and assoc and cell:
                if assoc not in st.session_state.mem_assoc:
                    st.session_state.mem_assoc.append(assoc)
                if nome not in st.session_state.mem_nomi:
                    st.session_state.mem_nomi.append(nome)
                st.session_state.dati.append({"Nome": nome, "Associazione": assoc, "Cellulare": cell, "Ruolo": ruolo, "Note": note})
                salva_dati()
                st.success(f"Salvato {nome}")
                st.rerun()
            else:
                st.error("Compila *")
    
    if st.session_state.dati:
        st.dataframe(pd.DataFrame(st.session_state.dati), use_container_width=True, hide_index=True)

with tab2:
    st.subheader("Sottomaschera - Registro Telecomunicazioni con Memoria Mittenti")
    st.info("💾 Ogni nuovo Mittente/Destinatario che scrivi viene memorizzato automaticamente e resta nel menu")
    
    with st.form("form_radio"):
        c1,c2 = st.columns(2)
        with c1:
            mittente = combo_memoria("Mittente", st.session_state.mem_mitt + st.session_state.mem_nomi, "mitt", "Es: Sala Operativa Varese, Prefettura, COC...")
            messaggio_ricevuto = st.text_area("Messaggio RICEVUTO *", placeholder="Es: Richiesta intervento in Via...", height=100)
        with c2:
            destinatario = combo_memoria("Destinatario", st.session_state.mem_dest + st.session_state.mem_nomi, "dest", "Es: Squadra 1, Tutte le squadre...")
            messaggio_trasmesso = st.text_area("Messaggio TRASMESSO *", placeholder="Es: Ricevuto, squadra in partenza...", height=100)
        
        c3,c4,c5 = st.columns(3)
        with c3:
            canale = st.selectbox("Canale", ["CH 1 - Emergenza", "CH 2 - Logistica", "CH 3 - Coordinamento", "CH 4 - Operativo", "VHF 145.500", "Altro"])
        with c4:
            ora = st.text_input("Ora", value=datetime.now().strftime("%H:%M"))
        with c5:
            data = st.date_input("Data", value=datetime.now())
        
        if st.form_submit_button("📻 REGISTRA COMUNICAZIONE", use_container_width=True, type="primary"):
            if mittente and destinatario and (messaggio_ricevuto or messaggio_trasmesso):
                # MEMORIZZA NUOVI MITTENTI/DESTINATARI
                nuovo_mitt = False
                nuovo_dest = False
                if mittente not in st.session_state.mem_mitt:
                    st.session_state.mem_mitt.append(mittente)
                    st.session_state.mem_mitt = sorted(st.session_state.mem_mitt)
                    salva_mem_mitt()
                    nuovo_mitt = True
                if destinatario not in st.session_state.mem_dest:
                    st.session_state.mem_dest.append(destinatario)
                    st.session_state.mem_dest = sorted(st.session_state.mem_dest)
                    salva_mem_dest()
                    nuovo_dest = True
                
                st.session_state.radio_log.append({
                    "Data": str(data),
                    "Ora": ora,
                    "Canale": canale,
                    "Mittente": mittente,
                    "Destinatario": destinatario,
                    "Messaggio Ricevuto": messaggio_ricevuto,
                    "Messaggio Trasmesso": messaggio_trasmesso
                })
                salva_radio()
                if nuovo_mitt or nuovo_dest:
                    st.success(f"✅ Registrato e NUOVI mittenti/destinatari memorizzati! {mittente} -> {destinatario}")
                else:
                    st.success(f"✅ Registrato: {mittente} -> {destinatario}")
                st.rerun()
            else:
                st.error("Compila Mittente, Destinatario e almeno un messaggio")
    
    if st.session_state.radio_log:
        st.divider()
        df_radio = pd.DataFrame(st.session_state.radio_log).iloc[::-1]
        
        st.write(f"**Totale comunicazioni: {len(df_radio)} | Mittenti in memoria: {len(st.session_state.mem_mitt)} | Destinatari: {len(st.session_state.mem_dest)}**")
        
        with st.expander(f"📋 Vedi {len(st.session_state.mem_mitt)} Mittenti e {len(st.session_state.mem_dest)} Destinatari memorizzati"):
            c1,c2 = st.columns(2)
            with c1:
                st.write("**MITTENTI IN MEMORIA:**")
                for m in sorted(st.session_state.mem_mitt):
                    st.write(f"• {m}")
                if st.button("Pulisci memoria Mittenti"):
                    st.session_state.mem_mitt = ["Sala Operativa Varese", "COC Varese", "Prefettura"]
                    salva_mem_mitt()
                    st.rerun()
            with c2:
                st.write("**DESTINATARI IN MEMORIA:**")
                for d in sorted(st.session_state.mem_dest):
                    st.write(f"• {d}")
                if st.button("Pulisci memoria Destinatari"):
                    st.session_state.mem_dest = ["Squadra 1", "Squadra 2", "Tutte le squadre"]
                    salva_mem_dest()
                    st.rerun()
        
        st.dataframe(df_radio, use_container_width=True, hide_index=True)
        
        col1,col2,col3,col4 = st.columns(4)
        with col1:
            output = BytesIO()
            df_radio.to_excel(output, index=False, engine="openpyxl")
            st.download_button("📥 Excel", output.getvalue(), file_name=f"registro_radio_{datetime.now().strftime('%Y%m%d')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        with col2:
            csv = df_radio.to_csv(index=False).encode('utf-8')
            st.download_button("📥 CSV", csv, file_name="registro_radio.csv", mime="text/csv", use_container_width=True)
        with col3:
            pdf_bytes = crea_pdf_radio(df_radio)
            if pdf_bytes:
                st.download_button("📄 PDF Registro", pdf_bytes, file_name=f"registro_radio_{datetime.now().strftime('%Y%m%d')}.pdf", mime="application/pdf", use_container_width=True)
        with col3:
            pass
        with col4:
            if st.button("🗑️ Svuota Registro", use_container_width=True):
                st.session_state.radio_log = []
                if os.path.exists(FILE_RADIO):
                    os.remove(FILE_RADIO)
                st.rerun()
    else:
        st.warning("Nessuna comunicazione registrata")
