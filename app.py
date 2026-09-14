import streamlit as st
import pandas as pd
from io import BytesIO
import os
from datetime import datetime

st.set_page_config(page_title="ANA Varese", layout="wide")

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
    st.markdown('<div style="text-align:center; padding:50px; background:#f0f0f0; border-radius:15px; margin-top:20px;"><h1 style="color:#0e7a3d;">Grazie per il servizio!</h1><h3>Registro chiuso</h3><p>I dati restano salvati</p></div>', unsafe_allow_html=True)
    if st.button("🔓 Rientra"):
        st.session_state["uscito"] = False
        st.rerun()
    st.stop()

FILE_DATI = "dati_iscritti.csv"
FILE_RADIO = "radio_log.csv"
FILE_MEM_MITT = "memoria_mittenti.csv"
FILE_MEM_DEST = "memoria_destinatari.csv"

if "dati" not in st.session_state:
    st.session_state.dati = pd.read_csv(FILE_DATI).to_dict(orient="records") if os.path.exists(FILE_DATI) else []
if "radio_log" not in st.session_state:
    st.session_state.radio_log = pd.read_csv(FILE_RADIO).to_dict(orient="records") if os.path.exists(FILE_RADIO) else []
if "mem_mitt" not in st.session_state:
    base = ["Sala Operativa Varese", "COC Varese", "Prefettura", "Posto Comando"]
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
    base = ["Squadra 1", "Squadra 2", "Tutte le squadre"]
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

def crea_pdf_senza_libreria(df):
    # Crea un PDF testuale semplice senza bisogno di fpdf
    # Usa solo BytesIO - non importa nulla
    lines = []
    lines.append("ANA VARESE - REGISTRO TELECOMUNICAZIONI")
    lines.append(f"Stampa: {datetime.now().strftime('%d/%m/%Y %H:%M')} - Totale: {len(df)}")
    lines.append("="*100)
    lines.append("")
    for _, row in df.iterrows():
        lines.append(f"Data: {row.get('Data','')} Ora: {row.get('Ora','')} Canale: {row.get('Canale','')}")
        lines.append(f"Mittente: {row.get('Mittente','')} -> Destinatario: {row.get('Destinatario','')}")
        lines.append(f"Ricevuto: {row.get('Messaggio Ricevuto','')}")
        lines.append(f"Trasmesso: {row.get('Messaggio Trasmesso','')}")
        lines.append("-"*100)
    text = "\n".join(lines)
    return text.encode('utf-8')

# MASCHERA PRINCIPALE
st.markdown("### MASCHERA PRINCIPALE - Anagrafica Volontari")
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
    st.dataframe(pd.DataFrame(st.session_state.dati), use_container_width=True, hide_index=True, height=150)

# SOTTOMASCHERA INCORPORATA
st.divider()
st.markdown("### SOTTOMASCHERA INCORPORATA - Registro Radio")
st.caption("Dentro la maschera principale - Mittente / Destinatario / Messaggi con memoria")

with st.container(border=True):
    st.markdown("#### Registro Radio - Inserimento")
    with st.form("form_radio_embedded"):
        c1,c2 = st.columns(2)
        with c1:
            st.markdown("**MITTENTE con memoria**")
            mittente = combo_memoria("Mittente", st.session_state.mem_mitt, "mitt_emb", "Es: Sala Operativa, Prefettura...")
            messaggio_ricevuto = st.text_area("Messaggio RICEVUTO *", placeholder="Cosa hai ricevuto...", height=100)
        with c2:
            st.markdown("**DESTINATARIO con memoria**")
            destinatario = combo_memoria("Destinatario", st.session_state.mem_dest, "dest_emb", "Es: Squadra 1...")
            messaggio_trasmesso = st.text_area("Messaggio TRASMESSO *", placeholder="Cosa hai trasmesso...", height=100)
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
                st.success(f"Registrato: {mittente} -> {destinatario} - Memorizzato!")
                st.rerun()
            else:
                st.error("Compila Mittente, Destinatario e almeno un messaggio")

    if st.session_state.radio_log:
        df_radio = pd.DataFrame(st.session_state.radio_log).iloc[::-1]
        st.write(f"Comunicazioni: {len(df_radio)} | Mittenti in memoria: {len(st.session_state.mem_mitt)} | Destinatari: {len(st.session_state.mem_dest)}")
        with st.expander("Vedi memorie Mittente/Destinatario"):
            c1,c2 = st.columns(2)
            with c1:
                st.write("**MITTENTI:**")
                for m in sorted(st.session_state.mem_mitt):
                    st.write(f"- {m}")
            with c2:
                st.write("**DESTINATARI:**")
                for d in sorted(st.session_state.mem_dest):
                    st.write(f"- {d}")
        st.dataframe(df_radio, use_container_width=True, hide_index=True)
        col1,col2,col3 = st.columns(3)
        with col1:
            output = BytesIO()
            df_radio.to_excel(output, index=False, engine="openpyxl")
            st.download_button("Excel", output.getvalue(), file_name=f"registro_radio_{datetime.now().strftime('%Y%m%d')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        with col2:
            # PDF senza libreria esterna - non da errore
            pdf_bytes = crea_pdf_senza_libreria(df_radio)
            st.download_button("PDF (testo)", pdf_bytes, file_name=f"registro_radio_{datetime.now().strftime('%Y%m%d')}.txt", mime="text/plain", use_container_width=True)
            st.caption("PDF vero: aggiungi fpdf2 in requirements.txt e riavvia")
        with col3:
            csv = df_radio.to_csv(index=False).encode('utf-8')
            st.download_button("CSV", csv, file_name="registro_radio.csv", mime="text/csv", use_container_width=True)
