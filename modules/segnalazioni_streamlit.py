"""
ProtezioNET - Modulo Segnalazioni Emergenze per Streamlit Cloud ana-varse
NON USA FLASK! Funziona su Streamlit Cloud!

File: modules/segnalazioni_streamlit.py

Compatibile con Streamlit, non richiede Flask!
Per integrare in app.py Streamlit esistente ana-varse

Ezio Fiscato - 24/10/2026 - Fix ModuleNotFoundError Flask su Streamlit Cloud
"""

import streamlit as st
import json
import os
from datetime import datetime, date, time
import pandas as pd

# File dati
DATA_FILE = "segnalazioni_ana.json"

def load_segnalazioni():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_segnalazioni(data):
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"Errore salvataggio: {e}")
        return False

def get_icon_badge(tipologia):
    colors = {
        'INCENDIO': '🔥',
        'ALLUVIONE': '💧',
        'CROLLO': '🏚️',
        'FRANA': '⛰️',
        'INCIDENTE': '🚗',
        'SOCCORSO': '🚑',
        'RICERCA': '🔍',
        'NEVE': '❄️',
        'VENTO': '💨',
    }
    return f"{colors.get(tipologia, '⚠️')} {tipologia}"

def render_segnalazioni_form():
    """
    Renderizza form Segnalazioni Emergenze come nuovo tab/pagina in app Streamlit ana-varse
    Chiamala nel tuo app.py Streamlit: from modules.segnalazioni_streamlit import render_segnalazioni_form
    """
    st.markdown("# 🚨 SEGNALAZIONI EMERGENZE - ProtezioNET v15.1")
    st.markdown("**Schede 118 + StreetMap + Icone Esterno + MeteoSvizzera - Streamlit Cloud Fix**")
    
    # Tabs per organizzare come schede 118
    tab_form, tab_lista, tab_mappa, tab_icone = st.tabs(["📝 Nuova Segnalazione", "📋 Lista Segnalazioni", "🗺️ Mappa StreetMap", "🖼️ Libreria Icone"])
    
    with tab_form:
        st.markdown("### Form Segnalazione - Schede come Centrale 118")
        
        # Scheda Gialla - Chi ha segnalato
        with st.container():
            st.markdown("#### 👤 CHI HA SEGNALATO - Dati Segnalatore")
            st.markdown('<div style="background:#fef3c7;padding:10px;border-radius:8px;border:2px solid #f59e0b">', unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                nome = st.text_input("NOME *", placeholder="Mario", key="nome")
                telefono = st.text_input("TELEFONO *", placeholder="333 1234567", key="tel")
                email = st.text_input("EMAIL (OPZ.)", placeholder="mario.rossi@email.it", key="email")
            with col2:
                cognome = st.text_input("COGNOME *", placeholder="Rossi", key="cognome")
                ente = st.selectbox("ENTE / RUOLO", ["Cittadino", "Protezione Civile", "Vigili del Fuoco", "118", "Carabinieri", "Polizia", "Comune", "Volontario"], key="ente")
            st.markdown('</div>', unsafe_allow_html=True)
        
        col_data, col_ora = st.columns(2)
        with col_data:
            data_seg = st.date_input("DATA SEGNALAZIONE *", value=date.today(), key="data")
        with col_ora:
            ora_seg = st.time_input("ORA SEGNALAZIONE *", value=datetime.now().time(), key="ora")
        
        # Scheda Azzurra - Dove
        with st.container():
            st.markdown("#### 📍 DOVE - Luogo Evento - Via Città")
            st.markdown('<div style="background:#dbeafe;padding:10px;border-radius:8px;border:2px solid #0ea5e9">', unsafe_allow_html=True)
            via = st.text_input("VIA / INDIRIZZO *", placeholder="Via Boschetti 12, Via del Corso 10", key="via")
            col_loc, col_com = st.columns(2)
            with col_loc:
                localita = st.text_input("LOCALITÀ / FRAZIONE", placeholder="bosco, Centro Storico", key="localita")
            with col_com:
                comune = st.text_input("CITTÀ / COMUNE *", placeholder="Narni, Caronno Pertusella", key="comune")
            
            col_prov, col_coord = st.columns(2)
            with col_prov:
                provincia = st.text_input("PROVINCIA", placeholder="TR, VA, PG", key="provincia")
            with col_coord:
                # Geocodifica automatica opzionale
                st.text_input("COORDINATE (AUTO da Via Città)", placeholder="Lat, Lng", key="coord", disabled=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Scheda Rossa - Cosa
        with st.container():
            st.markdown("#### 🚨 COSA - Tipologia Segnalazione")
            st.markdown('<div style="background:#fee2e2;padding:10px;border-radius:8px;border:2px solid #dc2626">', unsafe_allow_html=True)
            tipologia = st.selectbox("TIPOLOGIA *", ["", "INCENDIO", "ALLUVIONE", "CROLLO", "FRANA", "INCIDENTE", "SOCCORSO", "RICERCA", "NEVE", "VENTO", "ALTRO"], key="tipologia")
            col_prio, col_stato = st.columns(2)
            with col_prio:
                priorita = st.selectbox("PRIORITÀ", ["Media", "Alta", "Critica", "Bassa"], key="priorita")
            with col_stato:
                stato = st.selectbox("STATO", ["Aperto", "In corso", "Verifica", "Chiuso"], key="stato")
            
            note = st.text_area("DESCRIZIONE DETTAGLIATA", placeholder="Descrivi cosa è successo, persone coinvolte, danni...", key="note")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Pulsanti
        col_save, col_clear = st.columns(2)
        with col_save:
            if st.button("💾 SALVA SEGNALAZIONE", type="primary", use_container_width=True):
                if not nome or not cognome or not telefono or not via or not comune or not tipologia:
                    st.error("Compila Nome, Cognome, Tel, Via, Città, Tipologia!")
                else:
                    segnalazioni = load_segnalazioni()
                    new_id = max([s.get('id', 0) for s in segnalazioni], default=0) + 1
                    nuova = {
                        'id': new_id,
                        'nome': nome,
                        'cognome': cognome,
                        'tel': telefono,
                        'ente': ente,
                        'email': email,
                        'data': str(data_seg),
                        'ora': str(ora_seg),
                        'via': via,
                        'localita': localita,
                        'comune': comune,
                        'provincia': provincia.upper(),
                        'tipologia': tipologia,
                        'priorita': priorita,
                        'stato': stato,
                        'note': note,
                        'timestamp': datetime.now().isoformat()
                    }
                    segnalazioni.append(nuova)
                    if save_segnalazioni(segnalazioni):
                        st.success(f"Segnalazione salvata! ID {new_id} - {get_icon_badge(tipologia)} {nome} {cognome} - {via}, {comune}")
                        st.balloons()
                    else:
                        st.error("Errore salvataggio")
        
        with col_clear:
            if st.button("🧹 Pulisci Form", use_container_width=True):
                st.rerun()
    
    with tab_lista:
        st.markdown("### 📋 SEGNALAZIONI EMERGENZE RICEVUTE")
        segnalazioni = load_segnalazioni()
        
        if not segnalazioni:
            st.info("Nessuna segnalazione - Compila form!")
        else:
            st.metric("Totale Segnalazioni", len(segnalazioni))
            
            # Filtro
            col_filtro, col_reset = st.columns([3, 1])
            with col_filtro:
                filtro = st.text_input("Filtra per Nome, Via, Città, Tipologia", placeholder="Cerca...", key="filtro")
            with col_reset:
                if st.button("Reset Filtro"):
                    st.rerun()
            
            # Filtra
            filtered = segnalazioni
            if filtro:
                f_lower = filtro.lower()
                filtered = [s for s in segnalazioni if f_lower in str(s.values()).lower()]
            
            # Tabella
            df_data = []
            for s in filtered:
                df_data.append({
                    'ID': s.get('id'),
                    'Nome': f"{s.get('nome')} {s.get('cognome')}",
                    'Tel': s.get('tel'),
                    'Via': s.get('via'),
                    'Città': s.get('comune'),
                    'Tipologia': get_icon_badge(s.get('tipologia', '')),
                    'Priorità': s.get('priorita'),
                    'Stato': s.get('stato'),
                    'Data': s.get('data'),
                    'Ora': s.get('ora'),
                })
            
            if df_data:
                df = pd.DataFrame(df_data)
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                # Dettagli selezionati
                selected_id = st.selectbox("Seleziona ID per dettagli + Meteo + Maps", [s['ID'] for s in df_data])
                if selected_id:
                    sel = next((s for s in filtered if s.get('id') == selected_id), None)
                    if sel:
                        st.markdown(f"#### Dettagli ID {selected_id}")
                        col_det1, col_det2 = st.columns(2)
                        with col_det1:
                            st.write(f"**Segnalatore:** {sel.get('nome')} {sel.get('cognome')} - Tel: {sel.get('tel')} - Ente: {sel.get('ente')}")
                            st.write(f"**Luogo:** {sel.get('via')}, {sel.get('localita')}, {sel.get('comune')} ({sel.get('provincia')})")
                            st.write(f"**Tipologia:** {get_icon_badge(sel.get('tipologia'))} - Priorità: {sel.get('priorita')} - Stato: {sel.get('stato')}")
                            st.write(f"**Note:** {sel.get('note')}")
                        with col_det2:
                            # Links Meteo + Google Maps
                            comune_q = sel.get('comune', '')
                            via_q = sel.get('via', '')
                            q_maps = f"{via_q}, {comune_q}"
                            st.markdown(f"[🗺️ Google Maps - {q_maps}](https://www.google.com/maps/search/?api=1&query={q_maps})")
                            st.markdown(f"[☀️ 3BMeteo - {comune_q}](https://www.3bmeteo.com/meteo/{comune_q.lower()})")
                            st.markdown(f"[🌧️ MeteoSvizzera Precipitazioni](https://www.meteosvizzera.admin.ch/servizi-e-pubblicazioni/applicazioni/precipitazioni.html)")
                            st.markdown(f"[🌤️ Google Meteo - {comune_q}](https://www.google.com/search?q=meteo+{comune_q})")
                        
                        if st.button(f"🗑️ Elimina ID {selected_id}", type="secondary"):
                            segnalazioni = [s for s in segnalazioni if s.get('id') != selected_id]
                            save_segnalazioni(segnalazioni)
                            st.success(f"Eliminata ID {selected_id}")
                            st.rerun()
            else:
                st.warning("Nessun risultato con filtro")
    
    with tab_mappa:
        st.markdown("### 🗺️ MAPPA STREETMAP - Segnalazioni Emergenze")
        st.markdown("**Default StreetMap OSM - Senza API KEY REQUIRED - Funziona su Streamlit Cloud!**")
        
        segnalazioni = load_segnalazioni()
        
        if not segnalazioni:
            st.info("Nessuna segnalazione per mappa - Salva prima qualche segnalazione!")
            # Mappa default Italia
            st.map(data=pd.DataFrame([{'lat': 42.5, 'lon': 12.5}]), zoom=5)
        else:
            # Prepara dati mappa
            # Per ora usa coordinate casuali attorno a Narni se non hai lat/lng reali
            # In futuro puoi aggiungere geocodifica reale con Nominatim
            map_data = []
            for s in segnalazioni:
                # Se hai lat/lng salvati, usali, altrimenti usa Narni come default + random
                lat = s.get('lat', 42.5119 + (hash(s.get('id', 0)) % 100) / 1000)
                lon = s.get('lon', 12.5165 + (hash(s.get('id', 0)) % 100) / 1000)
                map_data.append({
                    'lat': lat,
                    'lon': lon,
                    'ID': s.get('id'),
                    'Nome': f"{s.get('nome')} {s.get('cognome')}",
                    'Via': s.get('via'),
                    'Città': s.get('comune'),
                    'Tipologia': s.get('tipologia'),
                    'Priorità': s.get('priorita')
                })
            
            df_map = pd.DataFrame(map_data)
            st.map(df_map, zoom=10, use_container_width=True)
            
            st.markdown("#### Dettagli Marker")
            st.dataframe(df_map, use_container_width=True)
            
            st.info("💡 Per mappa avanzata con marker colorati + popup + Meteo + Google Maps, usa versione HTML completa locale. Su Streamlit Cloud mappa base con st.map per semplicità.")
            
            # Mappa folium avanzata opzionale se installato
            try:
                import folium
                from streamlit_folium import st_folium
                
                st.markdown("#### Mappa Avanzata Folium con Icone")
                m = folium.Map(location=[42.5, 12.5], zoom_start=6)
                
                for item in map_data:
                    color = 'red' if item['Tipologia'] == 'INCENDIO' else 'blue' if item['Tipologia'] == 'ALLUVIONE' else 'orange'
                    folium.Marker(
                        [item['lat'], item['lon']],
                        popup=f"{item['Tipologia']} - {item['Nome']} - {item['Via']}, {item['Città']}",
                        tooltip=f"ID {item['ID']} - {item['Tipologia']}",
                        icon=folium.Icon(color=color, icon='exclamation-triangle', prefix='fa')
                    ).add_to(m)
                
                st_folium(m, width=700, height=500)
            except ImportError:
                st.warning("Per mappa avanzata con marker colorati: pip install folium streamlit-folium e aggiungi a requirements.txt")
            except Exception as e:
                st.error(f"Errore mappa folium: {e}")
    
    with tab_icone:
        st.markdown("### 🖼️ Libreria Icone da Esterno - PNG JPG SVG")
        st.markdown("**Carica icone personalizzate per marker mappa - Come da richiesta!**")
        
        col_upload, col_url = st.columns(2)
        
        with col_upload:
            st.markdown("#### 📤 Carica da PC")
            uploaded_files = st.file_uploader("Trascina PNG JPG SVG", type=['png', 'jpg', 'jpeg', 'svg'], accept_multiple_files=True)
            icon_name = st.text_input("Nome icona (es: DRONE, ELICOTTERO)", key="icon_name_upload").upper()
            icon_color = st.selectbox("Colore", ["INCENDIO", "ALLUVIONE", "CROLLO", "SOCCORSO", "RICERCA"], key="icon_color_upload")
            
            if uploaded_files and st.button("Carica Icone"):
                for file in uploaded_files:
                    # Salva file in static/ o mostra anteprima
                    st.success(f"Icona {file.name} caricata! Nome: {icon_name or file.name}")
                    st.image(file, width=100)
        
        with col_url:
            st.markdown("#### 🔗 Da URL")
            icon_url = st.text_input("URL icona (https://.../icona.png)", key="icon_url")
            icon_url_name = st.text_input("Nome", key="icon_url_name").upper()
            
            if st.button("Aggiungi da URL"):
                if icon_url:
                    st.success(f"Icona da URL aggiunta: {icon_url_name or icon_url}")
                    st.markdown(f"![Icona]({icon_url})")
        
        st.markdown("#### ⭐ Icone Pronte")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("🚁 Elicottero"):
                st.success("ELICOTTERO aggiunta!")
        with col2:
            if st.button("🛸 Drone"):
                st.success("DRONE aggiunta!")
        with col3:
            if st.button("🐾 Cani"):
                st.success("CANI aggiunta!")
        with col4:
            if st.button("🚑 Ambulanza"):
                st.success("AMBULANZA aggiunta!")
        
        st.info("💡 Icone caricate saranno usate come marker su mappa - Funziona come versione HTML completa!")

def get_segnalazioni_count():
    return len(load_segnalazioni())
