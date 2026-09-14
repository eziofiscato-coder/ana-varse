import streamlit as st
import pandas as pd
from io import BytesIO
import os

st.set_page_config(page_title="ANA Varese", layout="centered")

try:
    st.image("logo.png", width=250)
except:
    pass

st.markdown("<h2 style='text-align:center; color:#0e7a3d;'>VOLONTARIATO<br>Sezione di Varese</h2>", unsafe_allow_html=True)

FILE_DATI = "dati_iscritti.csv"
FILE_MEM = "memoria_combo.csv"

# Carica dati iscritti
if "dati" not in st.session_state:
    if os.path.exists(FILE_DATI):
        try:
            st.session_state.dati = pd.read_csv(FILE_DATI).to_dict(orient="records")
        except:
            st.session_state.dati = []
    else:
        st.session_state.dati = []

# Carica memoria combo
if "mem_nomi" not in st.session_state:
    if os.path.exists(FILE_MEM):
        try:
            dfm = pd.read_csv(FILE_MEM)
            st.session_state.mem_nomi = dfm["Nome"].dropna().unique().tolist() if "Nome" in dfm.columns else []
            st.session_state.mem_assoc = dfm["Associazione"].dropna().unique().tolist() if "Associazione" in dfm.columns else []
            st.session_state.mem_ruoli = dfm["Ruolo"].dropna().unique().tolist() if "Ruolo" in dfm.columns else []
        except:
            st.session_state.mem_nomi = []
            st.session_state.mem_assoc = ["ANA Varese", "Protezione Civile Varese"]
            st.session_state.mem_ruoli = ["Volontario", "Caposquadra", "Coordinatore", "Autista", "Radio", "Telecomunicazioni", "Logistica", "Segreteria", "Sanitario"]
    else:
        st.session_state.mem_nomi = sorted(list(set([d["Nome"] for d in st.session_state.dati]))) if st.session_state.dati else []
        st.session_state.mem_assoc = sorted(list(set([d["Associazione"] for d in st.session_state.dati]))) if st.session_state.dati else ["ANA Varese", "Protezione Civile Varese"]
        st.session_state.mem_ruoli = ["Volontario", "Caposquadra", "Coordinatore", "Autista", "Radio", "Telecomunicazioni", "Logistica", "Segreteria", "Sanitario", "Altro"]

def salva_tutto():
    if st.session_state.dati:
        pd.DataFrame(st.session_state.dati).to_csv(FILE_DATI, index=False)
    # salva memoria combo
    max_len = max(len(st.session_state.mem_nomi), len(st.session_state.mem_assoc), len(st.session_state.mem_ruoli))
    mem_df = pd.DataFrame({
        "Nome": st.session_state.mem_nomi + [""]*(max_len-len(st.session_state.mem_nomi)),
        "Associazione": st.session_state.mem_assoc + [""]*(max_len-len(st.session_state.mem_assoc)),
        "Ruolo": st.session_state.mem_ruoli + [""]*(max_len-len(st.session_state.mem_ruoli))
    })
    mem_df.to_csv(FILE_MEM, index=False)

# FUNZIONE COMBO CON MEMORIA
def combo_memoria(label, mem_list, key_prefix):
    opzioni = ["-- Seleziona --"] + sorted(mem_list) + [f"➕ NUOVO {label.upper()}..."]
    scelta = st.selectbox(f"{label} *", opzioni, key=f"{key_prefix}_select")
    if scelta == f"➕ NUOVO {label.upper()}...":
        nuovo = st.text_input(f"Scrivi nuovo {label} *", key=f"{key_prefix}_new", placeholder=f"Es: nuovo {label}")
        return nuovo.strip()
    elif scelta == "-- Seleziona --":
        return ""
    else:
        return scelta

with st.form("form"):
    st.write("**I campi ricordano tutto quello che hai già scritto**")
    
    nome_finale = combo_memoria("Nome e Cognome", st.session_state.mem_nomi, "nome")
    assoc_finale = combo_memoria("Associazione", st.session_state.mem_assoc, "assoc")
    cell = st.text_input("Cellulare *", placeholder="Es: 333 1234567")
    ruolo_finale = combo_memoria("Ruolo", st.session_state.mem_ruoli, "ruolo")
    
    submitted = st.form_submit_button("✅ Salva e Memorizza", use_container_width=True)
    if submitted:
        if nome_finale and assoc_finale and cell and ruolo_finale:
            # Aggiungi a memorie se nuovi
            if nome_finale not in st.session_state.mem_nomi:
                st.session_state.mem_nomi.append(nome_finale)
            if assoc_finale not in st.session_state.mem_assoc:
                st.session_state.mem_assoc.append(assoc_finale)
            if ruolo_finale not in st.session_state.mem_ruoli:
                st.session_state.mem_ruoli.append(ruolo_finale)
            
            st.session_state.dati.append({"Nome": nome_finale, "Associazione": assoc_finale, "Cellulare": cell, "Ruolo": ruolo_finale})
            salva_tutto()
            st.success(f"Salvato {nome_finale} - Ora in memoria!")
            st.rerun()
        else:
            st.error("Compila tutti i campi * - se hai scelto NUOVO, scrivilo sotto")

if st.session_state.dati:
    df = pd.DataFrame(st.session_state.dati)
    st.divider()
    st.write(f"**Iscritti: {len(df)} | Nomi in memoria: {len(st.session_state.mem_nomi)} | Associazioni: {len(st.session_state.mem_assoc)} | Ruoli: {len(st.session_state.mem_ruoli)}**")
    
    with st.expander("📋 Vedi memorie salvate"):
        c1,c2,c3 = st.columns(3)
        with c1:
            st.write("**Nomi:**")
            for n in sorted(st.session_state.mem_nomi): st.write(f"• {n}")
        with c2:
            st.write("**Associazioni:**")
            for a in sorted(st.session_state.mem_assoc): st.write(f"• {a}")
        with c3:
            st.write("**Ruoli:**")
            for r in sorted(st.session_state.mem_ruoli): st.write(f"• {r}")
    
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    col1, col2 = st.columns(2)
    with col1:
        output = BytesIO()
        df.to_excel(output, index=False, engine="openpyxl")
        st.download_button("📥 Excel", output.getvalue(), file_name="associazioni.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
    with col2:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 CSV", csv, file_name="associazioni.csv", mime="text/csv", use_container_width=True)
    
    if st.button("🗑️ Svuota tutto", use_container_width=True):
        st.session_state.dati = []
        st.session_state.mem_nomi = []
        st.session_state.mem_assoc = []
        st.session_state.mem_ruoli = ["Volontario", "Caposquadra", "Coordinatore", "Autista", "Radio", "Telecomunicazioni", "Logistica", "Segreteria", "Sanitario", "Altro"]
        for f in [FILE_DATI, FILE_MEM]:
            if os.path.exists(f): os.remove(f)
        st.rerun()
