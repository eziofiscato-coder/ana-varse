import streamlit as st
import pandas as pd
from io import BytesIO
import os
from datetime import datetime

st.set_page_config(page_title="ANA Varese - Telecomunicazioni", layout="wide")

try:
    st.image("logo.png", width=200)
except:
    pass

st.markdown("<h2 style='text-align:center; color:#0e7a3d;'>VOLONTARIATO - Sezione di Varese<br><small>Registro Telecomunicazioni</small></h2>", unsafe_allow_html=True)

FILE_DATI = "dati_iscritti.csv"
FILE_RADIO = "radio_log.csv"
FILE_MEM = "memoria_combo.csv"

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

if "mem_assoc" not in st.session_state:
    st.session_state.mem_assoc = sorted(list(set([d["Associazione"] for d in st.session_state.dati]))) if st.session_state.dati else ["ANA Varese", "Protezione Civile Varese", "Sala Radio Varese"]
    st.session_state.mem_nomi = sorted(list(set([d["Nome"] for d in st.session_state.dati]))) if st.session_state.dati else []
    st.session_state.mem_mitt = sorted(list(set([r.get("Mittente","") for r in st.session_state.radio_log]))) if st.session_state.radio_log else ["Sala Operativa Varese", "COC Varese", "Prefettura", "Posto Comando"]
    st.session_state.mem_dest = sorted(list(set([r.get("Destinatario","") for r in st.session_state.radio_log]))) if st.session_state.radio_log else ["Squadra 1", "Squadra 2", "Tutte le squadre"]

def salva_dati():
    if st.session_state.dati:
        pd.DataFrame(st.session_state.dati).to_csv(FILE_DATI, index=False)

def salva_radio():
    if st.session_state.radio_log:
        pd.DataFrame(st.session_state.radio_log).to_csv(FILE_RADIO, index=False)

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

tab1, tab2 = st.tabs(["📋 ANAGRAFICA VOLONTARI (Maschera Principale)", "📻 SOTTOMASCHERA - REGISTRO RADIO (Mittente/Destinatario/Messaggi)"])

with tab1:
    st.subheader("Maschera Principale - Iscrizione Volontari")
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
    st.subheader("Sottomaschera - Registro Telecomunicazioni")
    st.info("Qui registri tutte le comunicazioni radio: chi trasmette, chi riceve, cosa è stato detto")
    
    with st.form("form_radio"):
        st.write("**COMUNICAZIONE RADIO - tiene in memoria Mittente e Destinatario**")
        c1,c2 = st.columns(2)
        with c1:
            mittente = combo_memoria("Mittente", st.session_state.mem_mitt + st.session_state.mem_nomi, "mitt", "Es: Sala Operativa")
            messaggio_ricevuto = st.text_area("Messaggio RICEVUTO *", placeholder="Es: Richiesta intervento in Via...", height=100)
        with c2:
            destinatario = combo_memoria("Destinatario", st.session_state.mem_dest + st.session_state.mem_nomi, "dest", "Es: Squadra 1")
            messaggio_trasmesso = st.text_area("Messaggio TRASMESSO *", placeholder="Es: Ricevuto, squadra in partenza...", height=100)
        
        c3,c4,c5 = st.columns(3)
        with c3:
            canale = st.selectbox("Canale/Frequenza", ["CH 1 - Emergenza", "CH 2 - Logistica", "CH 3 - Coordinamento", "CH 4 - Operativo", "VHF 145.500", "Altro"])
        with c4:
            ora = st.text_input("Ora", value=datetime.now().strftime("%H:%M"), placeholder="14:30")
        with c5:
            data = st.date_input("Data", value=datetime.now())
        
        if st.form_submit_button("📻 REGISTRA COMUNICAZIONE", use_container_width=True, type="primary"):
            if mittente and destinatario and (messaggio_ricevuto or messaggio_trasmesso):
                if mittente not in st.session_state.mem_mitt:
                    st.session_state.mem_mitt.append(mittente)
                if destinatario not in st.session_state.mem_dest:
                    st.session_state.mem_dest.append(destinatario)
                
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
                st.success(f"Registrato: {mittente} -> {destinatario}")
                st.rerun()
            else:
                st.error("Compila Mittente, Destinatario e almeno un messaggio")
    
    if st.session_state.radio_log:
        st.divider()
        df_radio = pd.DataFrame(st.session_state.radio_log)
        # ordina per data ora decrescente
        df_radio = df_radio.iloc[::-1]
        
        st.write(f"**Totale comunicazioni registrate: {len(df_radio)}**")
        
        # Filtri
        c_f1,c_f2 = st.columns(2)
        with c_f1:
            filtro_mitt = st.selectbox("Filtra per Mittente", ["Tutti"] + sorted(df_radio["Mittente"].unique().tolist()))
        with c_f2:
            filtro_dest = st.selectbox("Filtra per Destinatario", ["Tutti"] + sorted(df_radio["Destinatario"].unique().tolist()))
        
        df_show = df_radio.copy()
        if filtro_mitt != "Tutti":
            df_show = df_show[df_show["Mittente"] == filtro_mitt]
        if filtro_dest != "Tutti":
            df_show = df_show[df_show["Destinatario"] == filtro_dest]
        
        st.dataframe(df_show, use_container_width=True, hide_index=True)
        
        col1,col2,col3 = st.columns(3)
        with col1:
            output = BytesIO()
            df_radio.to_excel(output, index=False, engine="openpyxl")
            st.download_button("📥 Scarica Registro Radio Excel", output.getvalue(), file_name=f"registro_radio_{datetime.now().strftime('%Y%m%d')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        with col2:
            csv = df_radio.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Scarica CSV", csv, file_name="registro_radio.csv", mime="text/csv", use_container_width=True)
        with col3:
            if st.button("🗑️ Svuota Registro Radio", use_container_width=True):
                st.session_state.radio_log = []
                if os.path.exists(FILE_RADIO):
                    os.remove(FILE_RADIO)
                st.rerun()
    else:
        st.warning("Nessuna comunicazione registrata. Usa il form sopra per registrare la prima comunicazione radio.")
