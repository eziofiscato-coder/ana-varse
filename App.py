"""
ANA Varese - PATCH BASE 2032 + CSV comune/via
Da integrare in app_66.py

Logica richiesta: base 2032 + patch CSV comune via
- BASE 2032 = dataset base comuni/vie (file base_2032.csv oppure lista interna + GitHub)
- PATCH CSV = file con colonne 'comune','via' (opzionale 'cap','frazione','note') che integra/sovrascrive la base

Uso:
1. Metti base_2032.csv in /mnt/data/ (opzionale) con colonne comune,via
2. Metti patch_comune_via.csv in /mnt/data/ oppure caricalo da UI
3. Sostituisci le funzioni get_comuni() e get_vie() in app_66.py con queste sotto
"""

import streamlit as st
import pandas as pd
import os
import requests

# === CONFIG PERCORSI ===
BASE_2032_PATHS = [
    "/mnt/data/base_2032.csv",
    "/mnt/data/base2032.csv",
    "base_2032.csv",
    "base2032.csv"
]
PATCH_PATHS = [
    "/mnt/data/patch_comune_via.csv",
    "/mnt/data/patch_comuni_vie.csv",
    "patch_comune_via.csv"
]

COMUNI_ITALIA_FALLBACK = [
    "Varese", "Busto Arsizio", "Gallarate", "Saronno", "Cassano Magnago",
    "Tradate", "Malnate", "Somma Lombardo", "Gavirate", "Laveno-Mombello",
    "Luino", "Sesto Calende", "Samarate", "Lonate Pozzolo", "Fagnano Olona",
    "Castellanza", "Caronno Pertusella", "Gerenzano", "Origgio", "Uboldo",
    "Cislago", "Gorla Minore", "Gorla Maggiore", "Marnate", "Olgiate Olona",
    "Venegono Inferiore", "Venegono Superiore", "Vergiate", "Viggiu"
]

VIE_STANDARD_FALLBACK = [
    "Via Roma", "Via Garibaldi", "Via Matteotti", "Via Verdi",
    "Via Manzoni", "Via Milano", "Via Varese", "Via Dante",
    "Via Mazzini", "Via Cavour", "Corso Italia", "Piazza Libertà"
]

@st.cache_data(ttl=3600)
def load_base_2032_df():
    """Carica BASE 2032 se esiste, altrimenti None"""
    for p in BASE_2032_PATHS:
        if os.path.exists(p):
            try:
                df = pd.read_csv(p, dtype=str, keep_default_na=False)
                # normalizza colonne
                df.columns = [c.strip().lower() for c in df.columns]
                # cerca colonna comune
                # supporta formati diversi
                if 'comune' in df.columns:
                    return df
            except Exception as e:
                print(f"Errore lettura base {p}: {e}")
    return None

def load_patch_df():
    """Carica patch da session_state o da file"""
    # 1. da session_state se caricato da UI
    if "patch_df" in st.session_state and st.session_state.patch_df is not None:
        return st.session_state.patch_df
    
    # 2. da file su disco
    for p in PATCH_PATHS:
        if os.path.exists(p):
            try:
                df = pd.read_csv(p, dtype=str, keep_default_na=False)
                df.columns = [c.strip().lower() for c in df.columns]
                if 'comune' in df.columns:
                    return df
            except:
                pass
    return None

def get_comuni_base2032_patch():
    """
    NUOVA get_comuni() con logica BASE 2032 + PATCH
    Priorità: PATCH (aggiunge/sovrascrive) > BASE_2032.csv > GitHub comuni.json > fallback locale
    """
    comuni_set = set()
    
    # 1. BASE 2032
    base_df = load_base_2032_df()
    if base_df is not None and 'comune' in base_df.columns:
        for c in base_df['comune'].dropna().unique():
            c = str(c).strip()
            if c:
                comuni_set.add(c)
    else:
        # se non c'è file base, prova GitHub (logica originale)
        try:
            url = "https://raw.githubusercontent.com/matteocontrini/comuni-json/master/comuni.json"
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                for c in data:
                    nome = c.get("nome","")
                    if nome:
                        comuni_set.add(nome)
        except:
            pass
        # se ancora vuoto, usa fallback
        if not comuni_set:
            comuni_set.update(COMUNI_ITALIA_FALLBACK)
    
    # 2. PATCH - aggiunge nuovi comuni
    patch_df = load_patch_df()
    if patch_df is not None and 'comune' in patch_df.columns:
        for c in patch_df['comune'].dropna().unique():
            c = str(c).strip()
            if c:
                comuni_set.add(c.title() if c.isupper() else c)

    # Garantisci 2032 come base minima se richiesto
    # se base_df esiste e ha 2032 righe, usiamo quello come verità
    return sorted(list(comuni_set))

@st.cache_data(ttl=600)
def get_vie_base2032_patch(comune: str):
    """
    NUOVA get_vie(comune) con logica BASE 2032 + PATCH
    Priorità: PATCH (per quel comune) > BASE_2032.csv > Overpass API > standard
    """
    vie = []
    comune_norm = comune.strip().lower() if comune else ""

    patch_df = load_patch_df()
    if patch_df is not None and 'comune' in patch_df.columns and 'via' in patch_df.columns:
        mask = patch_df['comune'].astype(str).str.strip().str.lower() == comune_norm
        vie_patch = patch_df[mask]['via'].dropna().astype(str).str.strip().unique().tolist()
        vie_patch = [v for v in vie_patch if v]
        if vie_patch:
            # se patch trovata, ritorna subito patch + eventualmente base
            vie.extend(vie_patch)

    # BASE 2032 - vie per comune
    base_df = load_base_2032_df()
    if base_df is not None and 'comune' in base_df.columns and 'via' in base_df.columns:
        mask = base_df['comune'].astype(str).str.strip().str.lower() == comune_norm
        vie_base = base_df[mask]['via'].dropna().astype(str).str.strip().unique().tolist()
        for v in vie_base:
            if v not in vie:
                vie.append(v)
        if vie:
            return sorted(vie)[:150]

    # se patch ha già dato risultati, restituisci
    if vie:
        return sorted(list(set(vie)))[:150]

    # FALLBACK Overpass API (originale)
    if comune:
        try:
            query = f"""
            [out:json][timeout:10];
            area["name"="{comune}"]->.a;
            way(area.a)["highway"]["name"];
            out tags;
            """
            overpass_url = "https://overpass-api.de/api/interpreter"
            resp = requests.get(overpass_url, params={"data": query}, timeout=8)
            if resp.status_code == 200:
                data = resp.json()
                for el in data.get("elements", []):
                    nome_via = el.get("tags", {}).get("name","")
                    if nome_via and nome_via not in vie:
                        vie.append(nome_via)
                if len(vie) > 3:
                    return sorted(vie[:80])
        except:
            pass

    # ULTIMO fallback
    if not vie:
        pref = f"Via {comune} Centro"
        return VIE_STANDARD_FALLBACK + [f"Via {comune} Centro", f"Via {comune} Nord"]

    return sorted(vie)[:150]

# === UI PER CARICARE PATCH IN APP_66.py ===
def ui_patch_loader_sidebar():
    """
    Inserisci questa chiamata nella sidebar di app_66.py:
    ui_patch_loader_sidebar()
    """
    with st.sidebar.expander("🛠️ BASE 2032 + PATCH CSV", expanded=False):
        st.caption("Carica patch comune/via. Formato CSV: colonne `comune,via`")
        
        up_base = st.file_uploader("BASE 2032 (opzionale)", type=["csv"], key="up_base_2032")
        if up_base:
            try:
                df = pd.read_csv(up_base, dtype=str, keep_default_na=False)
                df.to_csv("/mnt/data/base_2032.csv", index=False)
                st.success(f"Base 2032 caricata: {len(df)} righe")
                st.cache_data.clear()
            except Exception as e:
                st.error(f"Errore base: {e}")

        up_patch = st.file_uploader("PATCH comune via", type=["csv"], key="up_patch_comune_via")
        if up_patch:
            try:
                df = pd.read_csv(up_patch, dtype=str, keep_default_na=False)
                # salva per persistenza
                df.to_csv("/mnt/data/patch_comune_via.csv", index=False, encoding='utf-8-sig')
                # salva in session
                df.columns = [c.strip().lower() for c in df.columns]
                st.session_state.patch_df = df
                st.success(f"Patch caricata: {len(df)} righe - {df['comune'].nunique() if 'comune' in df.columns else '?'} comuni")
                st.cache_data.clear()
            except Exception as e:
                st.error(f"Errore patch: {e}")

        patch_df = load_patch_df()
        base_df = load_base_2032_df()
        
        c1,c2 = st.columns(2)
        with c1:
            st.metric("Base", f"{len(base_df) if base_df is not None else 0} righe")
        with c2:
            st.metric("Patch", f"{len(patch_df) if patch_df is not None else 0} righe")

        if patch_df is not None:
            st.dataframe(patch_df.head(20), use_container_width=True)
            if st.button("❌ Rimuovi patch"):
                if os.path.exists("/mnt/data/patch_comune_via.csv"):
                    os.remove("/mnt/data/patch_comune_via.csv")
                st.session_state.patch_df = None
                st.cache_data.clear()
                st.rerun()

# === ESEMPIO DI SOSTITUZIONE IN app_66.py ===
# Sostituisci:
# def get_comuni(): ... con get_comuni_base2032_patch
# def get_vie(comune): ... con get_vie_base2032_patch
# e rinomina:
# get_comuni = get_comuni_base2032_patch
# get_vie = get_vie_base2032_patch
#
# Aggiungi nella sidebar dopo st.sidebar:
# ui_patch_loader_sidebar()

# Per test standalone
if __name__ == "__main__":
    st.title("Test BASE 2032 + PATCH")
    ui_patch_loader_sidebar()
    comuni = get_comuni_base2032_patch()
    st.write(f"Comuni totali: {len(comuni)}")
    sel = st.selectbox("Seleziona comune", comuni[:200])
    vie = get_vie_base2032_patch(sel)
    st.write(f"Vie per {sel}: {len(vie)}")
    st.write(vie[:50])
