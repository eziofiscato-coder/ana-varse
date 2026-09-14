import streamlit as st
import pandas as pd
from io import BytesIO
import os
from datetime import datetime

st.set_page_config(page_title="ANA Varese", layout="wide")

# Gestione firma
import os
FILE_FIRMA = "firma.png"
FILE_TIMBRO = "timbro.png"


if "uscito" not in st.session_state:
    st.session_state["uscito"] = False

try:
    st.image("logo.png", width=200)
except:
    pass

col_tit, col_esci = st.columns([4,1])
with col_tit:
    st.markdown("<h3 style='color:#0e7a3d; margin:0;'>VOLONTARIATO - Sezione di Varese</h3>", unsafe_allow_html=True)
with col_esci:
    if st.button("🚪 ESCI", use_container_width=True):
        st.session_state["uscito"] = True

if st.session_state.get("uscito"):
    st.markdown('<div style="text-align:center; padding:50px; background:#f0f0f0; border-radius:15px; margin-top:20px;"><h1 style="color:#0e7a3d;">Grazie per il servizio!</h1><h3>Registro chiuso</h3></div>', unsafe_allow_html=True)
    if st.button("🔓 Rientra"):
        st.session_state["uscito"] = False
        st.rerun()
    st.stop()

# Sidebar firma e timbro
with st.sidebar:
    st.markdown("### ✍️ Firma e Timbro PDF")
    firma_file = st.file_uploader("Carica Firma (PNG/JPG)", type=["png","jpg","jpeg"], key="firma_up")
    if firma_file:
        with open(FILE_FIRMA, "wb") as f:
            f.write(firma_file.getbuffer())
        st.success("Firma caricata!")
        st.image(FILE_FIRMA, width=150)
    elif os.path.exists(FILE_FIRMA):
        st.image(FILE_FIRMA, width=150, caption="Firma attuale")
        if st.button("Rimuovi firma"):
            os.remove(FILE_FIRMA)
            st.rerun()
    
    timbro_file = st.file_uploader("Carica Timbro (PNG/JPG)", type=["png","jpg","jpeg"], key="timbro_up")
    if timbro_file:
        with open(FILE_TIMBRO, "wb") as f:
            f.write(timbro_file.getbuffer())
        st.success("Timbro caricato!")
        st.image(FILE_TIMBRO, width=150)
    elif os.path.exists(FILE_TIMBRO):
        st.image(FILE_TIMBRO, width=150, caption="Timbro attuale")
        if st.button("Rimuovi timbro"):
            os.remove(FILE_TIMBRO)
            st.rerun()
    
    st.divider()
    nome_coord = st.text_input("Nome Coordinatore", value="Coordinatore Sezione Varese", key="nome_coord")
    st.session_state["nome_coord"] = nome_coord

FILE_DATI = "dati_iscritti.csv"
FILE_RADIO = "radio_log.csv"
FILE_MEM_MITT = "memoria_mittenti.csv"
FILE_MEM_DEST = "memoria_destinatari.csv"

if "dati" not in st.session_state:
    st.session_state.dati = pd.read_csv(FILE_DATI).to_dict(orient="records") if os.path.exists(FILE_DATI) else []
if "radio_log" not in st.session_state:
    st.session_state.radio_log = pd.read_csv(FILE_RADIO).to_dict(orient="records") if os.path.exists(FILE_RADIO) else []
if "mem_mitt" not in st.session_state:
    base = ["Sala Operativa Varese", "COC Varese", "Prefettura", "Posto Comando", "ANA Varese"]
    if os.path.exists(FILE_MEM_MITT):
        try:
            base = pd.read_csv(FILE_MEM_MITT)["Mittente"].dropna().tolist()
        except:
            pass
    if st.session_state.radio_log:
        extra = [r.get("Mittente","") for r in st.session_state.radio_log if r.get("Mittente")]
        base = sorted(list(set(base + extra)))
    st.session_state.mem_mitt = base
if "mem_dest" not in st.session_state:
    base = ["Squadra 1", "Squadra 2", "Tutte le squadre", "Sala Operativa"]
    if os.path.exists(FILE_MEM_DEST):
        try:
            base = pd.read_csv(FILE_MEM_DEST)["Destinatario"].dropna().tolist()
        except:
            pass
    if st.session_state.radio_log:
        extra = [r.get("Destinatario","") for r in st.session_state.radio_log if r.get("Destinatario")]
        base = sorted(list(set(base + extra)))
    st.session_state.mem_dest = base
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
    opzioni = ["-- Seleziona --"] + sorted([x for x in mem_list if x]) + [f"NUOVO {label.upper()}..."]
    scelta = st.selectbox(f"{label} *", opzioni, key=f"{key_prefix}_sel")
    if scelta == f"NUOVO {label.upper()}...":
        nuovo = st.text_input(f"Scrivi nuovo {label}", key=f"{key_prefix}_new", placeholder=placeholder)
        return nuovo.strip()
    elif scelta == "-- Seleziona --":
        return ""
    else:
        return scelta

def crea_pdf_a4_con_logo(df, tipo="radio"):
    try:
        from fpdf import FPDF
        pdf = FPDF(orientation='P', unit='mm', format='A4')
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        
        # Logo in alto
        try:
            if os.path.exists("logo.png"):
                pdf.image("logo.png", x=10, y=8, w=30)
        except:
            pass
        
        # Intestazione
        pdf.set_xy(45, 10)
        pdf.set_font("Arial", "B", 16)
        pdf.set_text_color(14, 122, 61)
        pdf.cell(0, 10, "VOLONTARIATO - Sezione di Varese", ln=True)
        pdf.set_x(45)
        pdf.set_font("Arial", "B", 12)
        pdf.set_text_color(0,0,0)
        if tipo == "radio":
            pdf.cell(0, 8, "REGISTRO TELECOMUNICAZIONI - Comunicazioni Radio", ln=True)
        else:
            pdf.cell(0, 8, "ELENCO ISCRITTI - Anagrafica Volontari", ln=True)
        
        pdf.set_font("Arial", "", 9)
        pdf.set_x(45)
        pdf.cell(0, 6, f"Data stampa: {datetime.now().strftime('%d/%m/%Y %H:%M')} - Totale: {len(df)} - Documento Ufficiale", ln=True)
        
        pdf.ln(12)
        
        # Tabella
        if tipo == "radio":
            # Header tabella radio
            pdf.set_fill_color(14, 122, 61)
            pdf.set_text_color(255,255,255)
            pdf.set_font("Arial", "B", 8)
            col_widths = [20, 12, 22, 28, 28, 40, 40]
            headers = ["Data", "Ora", "Canale", "Mittente", "Destinatario", "Ricevuto", "Trasmesso"]
            for i, h in enumerate(headers):
                pdf.cell(col_widths[i], 8, h, border=1, fill=True, align="C")
            pdf.ln()
            
            # Righe
            pdf.set_text_color(0,0,0)
            pdf.set_font("Arial", "", 7)
            fill = False
            for _, row in df.iterrows():
                if pdf.get_y() > 270:
                    pdf.add_page()
                if fill:
                    pdf.set_fill_color(240, 240, 240)
                else:
                    pdf.set_fill_color(255,255,255)
                
                # Calcola altezza riga in base al testo piu lungo
                h = 8
                pdf.cell(col_widths[0], h, str(row.get("Data",""))[:10], border=1, fill=fill)
                pdf.cell(col_widths[1], h, str(row.get("Ora",""))[:5], border=1, fill=fill)
                pdf.cell(col_widths[2], h, str(row.get("Canale",""))[:18], border=1, fill=fill)
                pdf.cell(col_widths[3], h, str(row.get("Mittente",""))[:20], border=1, fill=fill)
                pdf.cell(col_widths[4], h, str(row.get("Destinatario",""))[:20], border=1, fill=fill)
                pdf.cell(col_widths[5], h, str(row.get("Messaggio Ricevuto",""))[:35], border=1, fill=fill)
                pdf.cell(col_widths[6], h, str(row.get("Messaggio Trasmesso",""))[:35], border=1, fill=fill)
                pdf.ln()
                fill = not fill
            
            # Footer
            pdf.ln(5)
            pdf.set_font("Arial", "I", 8)
            pdf.cell(0, 5, "Documento generato automaticamente dal sistema ANA Varese - Telecomunicazioni", align="C")
        else:
            # Tabella iscritti
            pdf.set_fill_color(14, 122, 61)
            pdf.set_text_color(255,255,255)
            pdf.set_font("Arial", "B", 9)
            pdf.cell(50, 8, "Nome", border=1, fill=True, align="C")
            pdf.cell(50, 8, "Associazione", border=1, fill=True, align="C")
            pdf.cell(35, 8, "Cellulare", border=1, fill=True, align="C")
            pdf.cell(30, 8, "Ruolo", border=1, fill=True, align="C")
            pdf.cell(25, 8, "Note", border=1, fill=True, align="C")
            pdf.ln()
            pdf.set_text_color(0,0,0)
            pdf.set_font("Arial", "", 8)
            for _, row in df.iterrows():
                if pdf.get_y() > 270:
                    pdf.add_page()
                pdf.cell(50, 7, str(row.get("Nome",""))[:25], border=1)
                pdf.cell(50, 7, str(row.get("Associazione",""))[:25], border=1)
                pdf.cell(35, 7, str(row.get("Cellulare",""))[:18], border=1)
                pdf.cell(30, 7, str(row.get("Ruolo",""))[:15], border=1)
                pdf.cell(25, 7, str(row.get("Note",""))[:15], border=1)
                pdf.ln()
        
        # Spazio firma e timbro in fondo
        pdf.ln(10)
        if pdf.get_y() > 240:
            pdf.add_page()
        
        pdf.set_font("Arial", "", 10)
        pdf.set_text_color(0,0,0)
        y_firma = pdf.get_y()
        
        # Box firma
        pdf.set_xy(20, y_firma)
        pdf.cell(80, 6, "Il Coordinatore", align="C")
        pdf.set_xy(110, y_firma)
        pdf.cell(80, 6, "Timbro Sezione", align="C")
        
        # Immagini firma e timbro
        try:
            if os.path.exists(FILE_FIRMA):
                pdf.image(FILE_FIRMA, x=25, y=y_firma+8, w=60)
        except:
            pass
        try:
            if os.path.exists(FILE_TIMBRO):
                pdf.image(FILE_TIMBRO, x=115, y=y_firma+8, w=50)
        except:
            pass
        
        # Linee firma
        pdf.set_xy(20, y_firma+30)
        pdf.cell(80, 6, "________________________", align="C")
        pdf.set_xy(110, y_firma+30)
        pdf.cell(80, 6, "________________________", align="C")
        
        pdf.set_xy(20, y_firma+36)
        pdf.set_font("Arial", "B", 9)
        nome_c = st.session_state.get("nome_coord", "Coordinatore Sezione Varese")
        pdf.cell(80, 6, nome_c, align="C")
        
        pdf.set_xy(110, y_firma+36)
        pdf.set_font("Arial", "", 8)
        pdf.cell(80, 6, "ANA Varese", align="C")
        
        # Numerazione pagine
        pdf.set_y(-15)
        pdf.set_font("Arial", "I", 8)
        pdf.cell(0, 10, f"Pagina {pdf.page_no()} - Documento ufficiale ANA Varese", align="C")
        
        return pdf.output(dest="S").encode("latin-1")
    except ImportError as e:
        st.error(f"Manca libreria fpdf2: {e} - Carica requirements.txt con fpdf2 e fai Reboot")
        return None
    except Exception as e:
        st.error(f"Errore creazione PDF: {e}")
        return None

# UI
st.markdown("### MASCHERA PRINCIPALE - Anagrafica")
with st.container(border=True):
    with st.form("form_vol"):
        c1,c2,c3 = st.columns(3)
        with c1:
            nome = st.text_input("Nome e Cognome *")
        with c2:
            assoc = combo_memoria("Associazione", st.session_state.mem_assoc, "assoc1", "Es: ANA Varese")
        with c3:
            cell = st.text_input("Cellulare *")
        c4,c5 = st.columns([1,2])
        with c4:
            ruolo = st.selectbox("Ruolo *", ["Volontario", "Caposquadra", "Coordinatore", "Autista", "Radio", "Telecomunicazioni", "Logistica", "Segreteria", "Sanitario", "Altro"])
        with c5:
            note = st.text_input("Note")
        if st.form_submit_button("Salva Volontario", use_container_width=True, type="primary"):
            if nome and assoc and cell:
                if assoc not in st.session_state.mem_assoc:
                    st.session_state.mem_assoc.append(assoc)
                if nome not in st.session_state.mem_nomi:
                    st.session_state.mem_nomi.append(nome)
                    if nome not in st.session_state.mem_mitt:
                        st.session_state.mem_mitt.append(nome)
                    if nome not in st.session_state.mem_dest:
                        st.session_state.mem_dest.append(nome)
                    salva_mem_mitt()
                    salva_mem_dest()
                st.session_state.dati.append({"Nome": nome, "Associazione": assoc, "Cellulare": cell, "Ruolo": ruolo, "Note": note})
                salva_dati()
                st.success(f"Salvato {nome}")
                st.rerun()
            else:
                st.error("Compila *")

if st.session_state.dati:
    df_anag = pd.DataFrame(st.session_state.dati)
    st.dataframe(df_anag, use_container_width=True, hide_index=True, height=150)
    col1,col2 = st.columns(2)
    with col1:
        out = BytesIO()
        df_anag.to_excel(out, index=False, engine="openpyxl")
        st.download_button("📥 Excel Anagrafica", out.getvalue(), file_name="anagrafica.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
    with col2:
        pdf_anag = crea_pdf_a4_con_logo(df_anag, tipo="anagrafica")
        if pdf_anag:
            st.download_button("📄 PDF Anagrafica A4 con Logo", pdf_anag, file_name=f"ANA_Varese_Anagrafica_{datetime.now().strftime('%Y%m%d')}.pdf", mime="application/pdf", use_container_width=True)

st.divider()
st.markdown("### SOTTOMASCHERA INCORPORATA - Registro Radio A4 con Logo")
with st.container(border=True):
    with st.form("form_radio"):
        c1,c2 = st.columns(2)
        with c1:
            st.markdown("**MITTENTE con memoria**")
            mittente = combo_memoria("Mittente", st.session_state.mem_mitt, "mitt_emb", "Es: Sala Operativa...")
            messaggio_ricevuto = st.text_area("Messaggio RICEVUTO *", height=100)
        with c2:
            st.markdown("**DESTINATARIO con memoria**")
            destinatario = combo_memoria("Destinatario", st.session_state.mem_dest, "dest_emb", "Es: Squadra 1...")
            messaggio_trasmesso = st.text_area("Messaggio TRASMESSO *", height=100)
        c3,c4,c5 = st.columns(3)
        with c3:
            canale = st.selectbox("Canale", ["CH 1 - Emergenza", "CH 2 - Logistica", "CH 3 - Coordinamento", "CH 4 - Operativo", "VHF 145.500", "Altro"])
        with c4:
            ora = st.text_input("Ora", value=datetime.now().strftime("%H:%M"))
        with c5:
            data = st.date_input("Data", value=datetime.now())
        if st.form_submit_button("REGISTRA nella Sottomaschera", use_container_width=True, type="primary"):
            if mittente and destinatario and (messaggio_ricevuto or messaggio_trasmesso):
                if mittente not in st.session_state.mem_mitt:
                    st.session_state.mem_mitt.append(mittente)
                    st.session_state.mem_mitt = sorted(st.session_state.mem_mitt)
                    salva_mem_mitt()
                if destinatario not in st.session_state.mem_dest:
                    st.session_state.mem_dest.append(destinatario)
                    st.session_state.mem_dest = sorted(st.session_state.mem_dest)
                    salva_mem_dest()
                st.session_state.radio_log.append({
                    "Data": str(data), "Ora": ora, "Canale": canale,
                    "Mittente": mittente, "Destinatario": destinatario,
                    "Messaggio Ricevuto": messaggio_ricevuto, "Messaggio Trasmesso": messaggio_trasmesso
                })
                salva_radio()
                st.success(f"Registrato: {mittente} -> {destinatario}")
                st.rerun()
            else:
                st.error("Compila Mittente, Destinatario e almeno un messaggio")

    if st.session_state.radio_log:
        df_radio = pd.DataFrame(st.session_state.radio_log).iloc[::-1]
        st.write(f"Comunicazioni: {len(df_radio)} | Mittenti: {len(st.session_state.mem_mitt)} | Destinatari: {len(st.session_state.mem_dest)}")
        st.dataframe(df_radio, use_container_width=True, hide_index=True)
        col1,col2,col3 = st.columns(3)
        with col1:
            out = BytesIO()
            df_radio.to_excel(out, index=False, engine="openpyxl")
            st.download_button("📥 Excel Radio", out.getvalue(), file_name=f"registro_radio_{datetime.now().strftime('%Y%m%d')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        with col2:
            pdf_bytes = crea_pdf_a4_con_logo(df_radio, tipo="radio")
            if pdf_bytes:
                st.download_button("📄 PDF A4 con LOGO Ufficiale", pdf_bytes, file_name=f"ANA_Varese_Registro_Radio_{datetime.now().strftime('%Y%m%d')}.pdf", mime="application/pdf", use_container_width=True, type="primary")
        with col3:
            csv = df_radio.to_csv(index=False).encode('utf-8')
            st.download_button("📥 CSV", csv, file_name="registro_radio.csv", mime="text/csv", use_container_width=True)
