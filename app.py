
import streamlit as st
import pandas as pd
import os
from io import BytesIO
from datetime import datetime, date
import json
import requests

st.set_page_config(page_title="ANA Varese - Gestionale", page_icon="🎖️", layout="wide")

# SFONDO VERDE CHIARO + LOGHI 80PX
APP_PASSWORD = "ANA2025"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("""<style>[data-testid="stSidebar"]{display:none;}</style>""", unsafe_allow_html=True)
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
    st.markdown("<h2 style='text-align:center; color:#2e7d32;'>🔐 Accesso Riservato<br>ANA Varese</h2>", unsafe_allow_html=True)
    pwd = st.text_input("Password", type="password", placeholder="Inserisci password")
    if st.button("🔓 Accedi", use_container_width=True, type="primary"):
        if pwd == APP_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Password errata!")
    st.stop()

st.markdown("""<style>
.stApp{background-color:#e8f5e9 !important;}
.main .block-container{background-color:rgba(255,255,255,0.93) !important;border-radius:18px;padding:25px !important;box-shadow:0 4px 20px rgba(0,0,0,0.08);}
[data-testid="stSidebar"]{background-color:#a5d6a7 !important;}
h1,h2,h3{color:#2e7d32 !important;}
</style>""", unsafe_allow_html=True)

# STORAGE EVENTI E CHECKIN
if "eventi" not in st.session_state:
    st.session_state.eventi = []
if "checkin" not in st.session_state:
    st.session_state.checkin = {}
if "page_extra" not in st.session_state:
    st.session_state.page_extra = None
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
if "utenti_collegati" not in st.session_state:
    st.session_state.utenti_collegati = {}
if "mio_nome" not in st.session_state:
    st.session_state.mio_nome = ""
if "utente_multi" not in st.session_state:
    st.session_state.utente_multi = ""


def get_pdf_bytes(pdf_obj):
    try:
        out = pdf_obj.output()
        if isinstance(out, str):
            return out.encode("latin-1","ignore")
        return bytes(out)
    except:
        try:
            return pdf_obj.output(dest="S").encode("latin-1","ignore")
        except:
            return b""



# ========== PAGINA EVENTO ==========
def pagina_crea_evento():
    st.title("📅 Crea Nuovo Evento / Servizio")
    if st.button("⬅️ Torna a Dashboard"):
        st.session_state.page_extra = None
        st.rerun()
    st.info("Compila tutti i campi obbligatori *")
    with st.form("form_evento_new", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            tipo = st.selectbox("🔧 TIPO DI SERVIZIO *", ["Seleziona...","Monitoraggio idrogeologico","Antincendio boschivo","Supporto emergenza","Esercitazione","Manifestazione pubblica","Ricerca persone","Alluvione / Esondazione","Neve / Ghiaccio","Assistenza popolazione","Presidio / Sorveglianza","Altro"])
            desc = st.text_area("📝 DESCRIZIONE EVENTO *", height=100)
            comune = st.text_input("🏘️ COMUNE *")
            prov = st.selectbox("📍 PROVINCIA *", ["Seleziona...","VA - Varese","MI - Milano","CO - Como","MB - Monza Brianza","LC - Lecco","LO - Lodi","PV - Pavia","CR - Cremona","MN - Mantova","BG - Bergamo","BS - Brescia","SO - Sondrio","Altra"])
        with c2:
            d_ini = st.date_input("📅 DATA INIZIO *")
            o_ini = st.time_input("⏰ ORA INIZIO *")
            d_fine = st.date_input("📅 DATA FINE *")
            o_fine = st.time_input("⏰ ORA FINE *")
            org = st.text_input("🏢 ORGANIZZAZIONE *")
            resp = st.text_input("👤 RESPONSABILE *")
            cell_resp = st.text_input("📱 CELLULARE RESPONSABILE *")
        salva = st.form_submit_button("💾 SALVA EVENTO", use_container_width=True, type="primary")
        if salva:
            if tipo=="Seleziona..." or not desc or not comune or prov=="Seleziona..." or not org or not resp or not cell_resp:
                st.error("Compila tutti i campi *")
            else:
                ev = {"ID": len(st.session_state.eventi)+1, "Tipo Servizio": tipo, "Descrizione": desc, "Comune": comune, "Provincia": prov, "Data Inizio": str(d_ini), "Ora Inizio": str(o_ini), "Data Fine": str(d_fine), "Ora Fine": str(o_fine), "Organizzazione": org, "Responsabile": resp, "Cellulare Resp": cell_resp, "Creato": datetime.now().strftime("%d/%m/%Y %H:%M"), "Volontari": 0}
                st.session_state.eventi.append(ev)
                sync_eventi()
                st.success(f"Evento {ev['ID']} salvato e condiviso con tutti gli utenti!")
                st.session_state.current_page="📅 Gestione Eventi"
                st.session_state.page_extra=None
                st.rerun()


def pagina_checkin():
    st.title("📝 Check-In Volontari per Evento - Collegato ad Anagrafica")
    if not st.session_state.eventi:
        st.warning("Nessun evento - crea prima un evento")
        if st.button("📅 Crea Evento"):
            st.session_state.current_page="📅 Gestione Eventi"
            st.session_state.page_extra="evento_crea"
            st.rerun()
        return
    
    # Selezione evento
    ids = [f"{e['ID']} - {e['Tipo Servizio']} - {e['Comune']} ({e['Data Inizio']})" for e in st.session_state.eventi]
    sel = st.selectbox("🎯 SELEZIONA EVENTO PER CHECK-IN", ids)
    id_ev = int(sel.split(" - ")[0])
    ev = [x for x in st.session_state.eventi if x["ID"]==id_ev][0]
    st.success(f"Evento: {ev['Tipo Servizio']} - {ev['Comune']} | Resp: {ev['Responsabile']} {ev['Cellulare Resp']}")
    
    # Tabs: Da Anagrafica o Manuale
    tab1, tab2 = st.tabs(["📚 Da Anagrafica Esistente", "✏️ Inserimento Manuale"])
    
    with tab1:
        st.markdown("### 📚 Seleziona Volontario da Anagrafica")
        if not st.session_state.mem_nomi:
            st.warning("Anagrafica vuota! Vai in 👥 Volontari e inserisci volontari prima.")
            if st.button("👥 Vai ad Anagrafica"):
                st.session_state.current_page="👥 Volontari"
                st.rerun()
            return
        
        # Mostra anagrafica con ricerca
        import pandas as pd
        df_anag = pd.DataFrame(st.session_state.mem_nomi)
        # Cerca colonna nome
        st.dataframe(df_anag, use_container_width=True, height=200)
        
        # Crea lista nomi per select
        opzioni = []
        for idx, v in enumerate(st.session_state.mem_nomi):
            # Prova a estrarre nome cognome
            nome = v.get("Nome", v.get("nome", ""))
            cognome = v.get("Cognome", v.get("cognome", ""))
            odv = v.get("ODV", v.get("odv", v.get("Gruppo", "")))
            cell = v.get("Cellulare", v.get("cellulare", v.get("Telefono", "")))
            cf = v.get("Codice Fiscale", v.get("CF", v.get("codice_fiscale", "")))
            if isinstance(v, str):
                opzioni.append((idx, v, "", "", ""))
            else:
                display = f"{nome} {cognome} - {odv} - {cell}"
                opzioni.append((idx, nome, cognome, odv, cell, cf, display))
        
        if opzioni and isinstance(opzioni[0], tuple) and len(opzioni[0])>2:
            sel_vol = st.selectbox("👤 Seleziona Volontario", [o[-1] for o in opzioni], key="sel_anag")
            idx_sel = [o[-1] for o in opzioni].index(sel_vol)
            dati_sel = opzioni[idx_sel]
            nome_s, cognome_s, odv_s, cell_s, cf_s = dati_sel[1], dati_sel[2], dati_sel[3], dati_sel[4], dati_sel[5]
            
            st.markdown(f'<div style="background:#c8e6c9; padding:10px; border-radius:8px;">Selezionato: <b>{nome_s} {cognome_s}</b> - {odv_s} - {cell_s} - CF: {cf_s}</div>', unsafe_allow_html=True)
            
            col_note, col_btn = st.columns([3,1])
            with col_note:
                note_anag = st.text_input("📝 Note Check-In", placeholder="Orario arrivo, mezzi...", key="note_anag")
            with col_btn:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("💾 CHECK-IN DA ANAGRAFICA", use_container_width=True, type="primary", key="btn_anag"):
                    # Verifica non già check-in
                    lista = st.session_state.checkin.get(id_ev, [])
                    gia_presente = any((x["Nome"]==nome_s.upper() and x["Cognome"]==cognome_s.upper()) for x in lista)
                    if gia_presente:
                        st.warning(f"{nome_s} {cognome_s} già in check-in per questo evento!")
                    else:
                        vol = {"Nome": nome_s.upper(), "Cognome": cognome_s.upper(), "ODV": odv_s, "Cellulare": cell_s, "Codice Fiscale": cf_s.upper(), "Note": note_anag, "Check-In": datetime.now().strftime("%d/%m/%Y %H:%M"), "Evento ID": id_ev, "Da Anagrafica": "Si", "Inserito da": st.session_state.get("utente_multi","")}
                        if id_ev not in st.session_state.checkin:
                            st.session_state.checkin[id_ev]=[]
                        st.session_state.checkin[id_ev].append(vol)
                        sync_checkin()
                        for e in st.session_state.eventi:
                            if e["ID"]==id_ev:
                                e["Volontari"]=len(st.session_state.checkin[id_ev])
                        sync_eventi()
                        st.success(f"✅ Check-In {nome_s} {cognome_s} da anagrafica salvato e condiviso!")
                        st.balloons()
        else:
            st.info("Formato anagrafica non standard - usa inserimento manuale o aggiorna anagrafica in formato tabella")
    
    with tab2:
        st.markdown("### ✏️ Inserimento Manuale (se non in anagrafica)")
        with st.form(f"checkin_{id_ev}_manual", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                nome = st.text_input("👤 NOME *", key="man_nome")
                cognome = st.text_input("👤 COGNOME *", key="man_cogn")
                odv = st.text_input("🏢 ODV *", key="man_odv")
            with c2:
                cell = st.text_input("📱 CELLULARE *", key="man_cell")
                cf = st.text_input("🆔 CODICE FISCALE *", max_chars=16, key="man_cf")
                note = st.text_input("Note", key="man_note")
            salva = st.form_submit_button("💾 SALVA CHECK-IN MANUALE", use_container_width=True, type="primary")
            if salva:
                if not nome or not cognome or not odv or not cell or not cf:
                    st.error("Compila tutti i campi *")
                elif len(cf)!=16:
                    st.error("CF 16 caratteri")
                else:
                    vol = {"Nome": nome.upper(), "Cognome": cognome.upper(), "ODV": odv, "Cellulare": cell, "Codice Fiscale": cf.upper(), "Note": note, "Check-In": datetime.now().strftime("%d/%m/%Y %H:%M"), "Evento ID": id_ev, "Da Anagrafica": "No", "Inserito da": st.session_state.get("utente_multi","")}
                    if id_ev not in st.session_state.checkin:
                        st.session_state.checkin[id_ev]=[]
                    st.session_state.checkin[id_ev].append(vol)
                    sync_checkin()
                    for e in st.session_state.eventi:
                        if e["ID"]==id_ev:
                            e["Volontari"]=len(st.session_state.checkin[id_ev])
                    sync_eventi()
                    st.success(f"✅ Check-In manuale {nome} {cognome} salvato!")
    
    # Lista volontari in check-in per evento
    st.divider()
    lista = st.session_state.checkin.get(id_ev, [])
    st.subheader(f"👥 Volontari in Check-In per Evento {id_ev} ({len(lista)}) - Agganciati ad Anagrafica")
    if lista:
        import pandas as pd
        from io import BytesIO
        df = pd.DataFrame(lista)
        st.dataframe(df, use_container_width=True)
        
        c1, c2, c3 = st.columns(3)
        with c1:
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name=f'CheckIn_{id_ev}')
            st.download_button("📥 Excel Check-In", data=output.getvalue(), file_name=f"checkin_evento_{id_ev}_{datetime.now().strftime('%Y%m%d')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        with c2:
            # PDF con loghi 80px
            try:
                from fpdf import FPDF
                import os
                class PDFCheck(FPDF):
                    def header(self):
                        try:
                            self.set_fill_color(232,245,233)
                            self.rect(0,0,210,28,"F")
                            if os.path.exists("logo.png"):
                                self.image("logo.png", x=10, y=5, w=18)
                            if os.path.exists("logo2.png"):
                                self.image("logo2.png", x=182, y=5, w=18)
                            self.set_y(8)
                            self.set_font("Arial","B",11)
                            self.set_text_color(27,94,32)
                            self.cell(0,10,"ANA Varese - Check-In Volontari", align="C", ln=True)
                            self.ln(8)
                        except:
                            pass
                pdf = PDFCheck()
                pdf.add_page()
                pdf.set_font("Arial","B",12)
                pdf.cell(0,10,f"Evento {id_ev} - {ev['Tipo Servizio']} - {ev['Comune']}", ln=True, align="C")
                pdf.set_font("Arial","",10)
                pdf.cell(0,7,f"Data: {ev['Data Inizio']} {ev['Ora Inizio']} - Resp: {ev['Responsabile']}", ln=True, align="C")
                pdf.ln(5)
                pdf.set_font("Arial","B",8)
                pdf.set_fill_color(200,230,201)
                pdf.cell(30,6,"Nome Cognome", border=1, fill=True)
                pdf.cell(25,6,"ODV", border=1, fill=True)
                pdf.cell(25,6,"Cellulare", border=1, fill=True)
                pdf.cell(35,6,"CF", border=1, fill=True)
                pdf.cell(20,6,"Anagrafica", border=1, fill=True)
                pdf.cell(25,6,"Ora", border=1, fill=True, ln=True)
                pdf.set_font("Arial","",7)
                for v in lista:
                    pdf.cell(30,5,f"{v['Nome']} {v['Cognome']}"[:20], border=1)
                    pdf.cell(25,5,v['ODV'][:15], border=1)
                    pdf.cell(25,5,v['Cellulare'], border=1)
                    pdf.cell(35,5,v['Codice Fiscale'], border=1)
                    pdf.cell(20,5,v.get('Da Anagrafica',''), border=1)
                    pdf.cell(25,5,v['Check-In'], border=1, ln=True)
                st.download_button("📄 PDF Check-In con Loghi 80px", data=get_pdf_bytes(pdf), file_name=f"checkin_evento_{id_ev}.pdf", mime="application/pdf", use_container_width=True)
            except Exception as e:
                st.error(f"Errore PDF: {e}")
        with c3:
            if st.button("🗑️ Svuota Check-In Evento", use_container_width=True):
                st.session_state.checkin[id_ev]=[]
                sync_checkin()
                for e in st.session_state.eventi:
                    if e["ID"]==id_ev:
                        e["Volontari"]=0
                sync_eventi()
                st.rerun()
    else:
        st.info("Nessun volontario in check-in. Seleziona da anagrafica o inserisci manualmente.")
    
    if st.button("⬅️ Torna a Dashboard"):
        st.session_state.current_page="🏠 Dashboard"
        st.session_state.page_extra=None
        st.rerun()


# ========== FINE FUNZIONI EVENTO ==========





# ========== CALCOLO CODICE FISCALE ITALIANO ==========
def calcola_cf(nome, cognome, data_nascita, sesso, comune_nascita, codice_catastale_manual=""):
    """
    Calcola Codice Fiscale italiano
    nome, cognome: stringhe
    data_nascita: datetime
    sesso: M/F
    comune_nascita: nome comune
    codice_catastale_manual: se fornito usa questo
    """
    try:
        # Pulisci
        cognome = cognome.upper().replace(" ", "").replace("'", "")
        nome = nome.upper().replace(" ", "").replace("'", "")
        
        # Funzione per codice cognome/nome
        def codice_cognome_nome(s, is_nome=False):
            vocali = "AEIOU"
            consonanti = "".join([c for c in s if c not in vocali and c.isalpha()])
            vocali_s = "".join([c for c in s if c in vocali])
            
            if is_nome and len(consonanti) >= 4:
                # Per nome con 4+ consonanti: 1a, 3a, 4a
                return consonanti[0] + consonanti[2] + consonanti[3]
            else:
                cod = consonanti + vocali_s + "XXX"
                return cod[:3]
        
        cod_cognome = codice_cognome_nome(cognome, False)
        cod_nome = codice_cognome_nome(nome, True)
        
        # Anno
        anno = data_nascita.strftime("%y")
        # Mese
        mesi = "ABCDEHLMPRST"
        mese = mesi[data_nascita.month - 1]
        # Giorno + sesso
        giorno = data_nascita.day
        if sesso.upper() == "F":
            giorno += 40
        giorno_str = f"{giorno:02d}"
        
        # Comune - codice catastale
        codice_comune = codice_catastale_manual.upper() if codice_catastale_manual else "Z000"
        
        # Se non manuale, prova a cercare in dizionario comuni
        if not codice_catastale_manual:
            # Dizionario ridotto comuni più usati Varese + grandi città
            comuni_codici = {
                "VARESE": "L682", "MILANO": "F205", "ROMA": "H501", "TORINO": "L219",
                "BUSTO ARSIZIO": "B300", "GALLARATE": "D869", "SARONNO": "I441",
                "CASSANO MAGNAGO": "B999", "TRADATE": "L319", "MALNATE": "E863",
                "SUMIRAGO": "L003", "VARESE": "L682", "COMO": "C933", "LECCO": "E507",
                "MONZA": "F704", "BERGAMO": "A794", "BRESCIA": "B157", "NAPOLI": "F839",
                "PALERMO": "G273", "GENOVA": "D969", "BOLOGNA": "A944", "FIRENZE": "D612",
                "VENEZIA": "L736", "VERONA": "L781", "MESSINA": "F158", "PADOVA": "G224",
                "TRIESTE": "L424", "TARANTO": "L049", "REGGIO CALABRIA": "H224",
                "CAGLIARI": "B354", "BARI": "A662", "CATANIA": "C351"
            }
            # Cerca comune senza provincia
            comune_pulito = comune_nascita.split("(")[0].strip().upper()
            if comune_pulito in comuni_codici:
                codice_comune = comuni_codici[comune_pulito]
            else:
                # Cerca parziale
                for k, v in comuni_codici.items():
                    if k in comune_pulito or comune_pulito in k:
                        codice_comune = v
                        break
        
        # Codice parziale 15 caratteri
        parziale = f"{cod_cognome}{cod_nome}{anno}{mese}{giorno_str}{codice_comune}"
        
        # Carattere di controllo
        dispari = {
            '0':1,'1':0,'2':5,'3':7,'4':9,'5':13,'6':15,'7':17,'8':19,'9':21,
            'A':1,'B':0,'C':5,'D':7,'E':9,'F':13,'G':15,'H':17,'I':19,'J':21,
            'K':2,'L':4,'M':18,'N':20,'O':11,'P':3,'Q':6,'R':8,'S':12,'T':14,
            'U':16,'V':10,'W':22,'X':25,'Y':24,'Z':23
        }
        pari = {
            '0':0,'1':1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,
            'A':0,'B':1,'C':2,'D':3,'E':4,'F':5,'G':6,'H':7,'I':8,'J':9,
            'K':10,'L':11,'M':12,'N':13,'O':14,'P':15,'Q':16,'R':17,'S':18,'T':19,
            'U':20,'V':21,'W':22,'X':23,'Y':24,'Z':25
        }
        controllo = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        somma = 0
        for i, c in enumerate(parziale):
            if (i+1) % 2 == 0:
                somma += pari.get(c, 0)
            else:
                somma += dispari.get(c, 0)
        cin = controllo[somma % 26]
        
        cf_completo = parziale + cin
        return cf_completo, codice_comune, parziale
    except Exception as e:
        return f"ERRORE: {e}", "", ""

def pagina_calcolo_cf():
    st.title("🆔 Calcolo Codice Fiscale")
    st.markdown('<div style="background:#e8f5e9; padding:15px; border-radius:10px;">Calcolo automatico CF da dati anagrafici - agganciato a comuni italiani</div>', unsafe_allow_html=True)
    
    lista_comuni = get_comuni_italiani()
    
    c1, c2 = st.columns(2)
    with c1:
        cognome = st.text_input("Cognome *", placeholder="Rossi", key="cf_cogn")
        nome = st.text_input("Nome *", placeholder="Mario", key="cf_nome")
        sesso = st.selectbox("Sesso *", ["M", "F"], key="cf_sesso")
        data_nasc = st.date_input("Data Nascita * - Giorno/Mese/Anno", value=datetime(1980,1,15), min_value=datetime(1920,1,1), max_value=datetime(2010,12,31), key="cf_data", format="DD/MM/YYYY")
        st.caption(f"📅 Formato: {data_nasc.strftime('%d/%m/%Y')} - Giorno: {data_nasc.day} Mese: {data_nasc.month} Anno: {data_nasc.year}")
    with c2:
        comune_nasc = st.selectbox("Comune Nascita *", ["--"] + lista_comuni[:1000], key="cf_comune_sel")
        filtro = st.text_input("Filtro Comune (scrivi per cercare)", placeholder="Varese...", key="cf_filtro")
        if filtro:
            risultati = [c for c in lista_comuni if filtro.lower() in c.lower()][:30]
            if risultati:
                comune_nasc = st.selectbox("Risultati filtro", ["--"] + risultati, key="cf_comune_filt")
        
        comune_manual = st.text_input("Oppure scrivi Comune manualmente", placeholder="Varese", key="cf_comune_man")
        codice_cat_man = st.text_input("Codice Catastale (se conosci, es: L682 per Varese)", placeholder="L682", max_chars=4, key="cf_cat")
    
    comune_final = comune_manual if comune_manual else (comune_nasc if comune_nasc != "--" else "")
    
    if st.button("🔍 CALCOLA CODICE FISCALE", use_container_width=True, type="primary"):
        if not cognome or not nome or not comune_final:
            st.error("Compila Cognome, Nome, Comune")
        else:
            cf_calc, cod_com, parz = calcola_cf(nome, cognome, data_nasc, sesso, comune_final, codice_cat_man)
            st.success(f"✅ Codice Fiscale Calcolato")
            
            col_cf1, col_cf2 = st.columns([2,1])
            with col_cf1:
                st.markdown(f'<div style="background:#c8e6c9; padding:20px; border-radius:10px; text-align:center; border:3px solid #2e7d32;"><h1 style="color:#1b5e20; letter-spacing:3px;">{cf_calc}</h1><p>Cognome: {cognome.upper()} - Nome: {nome.upper()}<br>Data: {data_nasc.strftime("%d/%m/%Y")} - Sesso: {sesso}<br>Comune: {comune_final} - Cod.Cat: {cod_com}</p></div>', unsafe_allow_html=True)
            with col_cf2:
                st.markdown("#### Dettaglio")
                st.code(f"Cognome: {cf_calc[:3]}\nNome: {cf_calc[3:6]}\nAnno: {cf_calc[6:8]}\nMese: {cf_calc[8]}\nGiorno: {cf_calc[9:11]}\nComune: {cf_calc[11:15]}\nControllo: {cf_calc[15]}")
                if st.button("📋 Usa questo CF in Anagrafica"):
                    st.session_state.cf_calcolato = cf_calc
                    st.session_state.current_page = "👥 Volontari"
                    st.rerun()
            
            # Barcode del CF
            try:
                import qrcode
                from io import BytesIO
                qr = qrcode.QRCode(version=1, box_size=10, border=2)
                qr.add_data(cf_calc)
                qr.make(fit=True)
                img = qr.make_image(fill='black', back_color='white')
                buf = BytesIO()
                img.save(buf, format='PNG')
                st.image(buf.getvalue(), width=150, caption=f"QR Code CF {cf_calc}")
            except:
                pass

# ========== FINE CALCOLO CF ==========

# ========== SISTEMA MULTI-UTENTE CONDIVISO ==========
import json
import os
import time

DATA_DIR = "data_condivisi"
os.makedirs(DATA_DIR, exist_ok=True)

FILE_EVENTI = os.path.join(DATA_DIR, "eventi.json")
FILE_CHECKIN = os.path.join(DATA_DIR, "checkin.json")
FILE_CHAT = os.path.join(DATA_DIR, "chat.json")
FILE_UTENTI = os.path.join(DATA_DIR, "utenti.json")

def carica_json(path, default):
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except:
        pass
    return default

def salva_json(path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"Errore salvataggio {path}: {e}")
        return False

# Carica dati condivisi all'avvio (se esistono, sovrascrive sessione vuota)
if len(st.session_state.eventi) == 0:
    eventi_shared = carica_json(FILE_EVENTI, [])
    if eventi_shared:
        st.session_state.eventi = eventi_shared

if len(st.session_state.checkin) == 0:
    checkin_shared = carica_json(FILE_CHECKIN, {})
    if checkin_shared:
        # Converti chiavi stringhe in int
        st.session_state.checkin = {int(k): v for k, v in checkin_shared.items()}

if len(st.session_state.chat_messages) == 0:
    chat_shared = carica_json(FILE_CHAT, [])
    if chat_shared:
        st.session_state.chat_messages = chat_shared

if len(st.session_state.utenti_collegati) == 0:
    utenti_shared = carica_json(FILE_UTENTI, {})
    if utenti_shared:
        st.session_state.utenti_collegati = utenti_shared


def pagina_backup():
    st.title("💾 Backup, Export CSV, Import CSV - Tutti i Dati")
    st.markdown('<div style="background:#e8f5e9; padding:15px; border-radius:10px; border-left:5px solid #2e7d32;"><b>💾 Gestione Completa Dati:</b> Esporta in CSV/Excel, Importa da CSV, Backup totale ZIP con nome personalizzato</div>', unsafe_allow_html=True)
    
    tab_exp, tab_imp, tab_backup, tab_restore = st.tabs(["📤 Esporta CSV/Excel", "📥 Importa CSV", "💾 Backup Completo", "♻️ Ripristina Backup"])
    
    with tab_exp:
        st.subheader("📤 Esporta Tutti i Dati in CSV / Excel")
        
        col1, col2 = st.columns(2)
        with col1:
            nome_export = st.text_input("📝 Nome file export", value=f"ANA_Varese_Export_{datetime.now().strftime('%Y%m%d_%H%M')}", help="Nome senza estensione")
        with col2:
            formato = st.selectbox("Formato", ["CSV", "Excel (XLSX)", "JSON", "Tutti in ZIP"])
        
        st.markdown("#### Seleziona cosa esportare:")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            exp_anag = st.checkbox("👥 Anagrafica Volontari", value=True)
            exp_eventi = st.checkbox("📅 Eventi", value=True)
        with c2:
            exp_checkin = st.checkbox("📝 Check-In", value=True)
            exp_radio = st.checkbox("📻 Radio DB", value=True)
        with c3:
            exp_post = st.checkbox("📍 Postazioni Mappa", value=False)
            exp_dist = st.checkbox("📦 Distribuzione Radio", value=False)
        with c4:
            exp_brog = st.checkbox("📒 Brogliaccio", value=False)
            exp_reg = st.checkbox("📋 Registro Radio", value=False)
        
        if st.button("📤 ESPORTA ORA", use_container_width=True, type="primary", key="btn_export"):
            import pandas as pd
            from io import BytesIO
            import json, os, zipfile
            
            files_to_download = []
            
            # Funzione helper export
            def df_from_session(key, filename_base):
                data = []
                if key in st.session_state and st.session_state[key]:
                    if isinstance(st.session_state[key], list):
                        if st.session_state[key] and isinstance(st.session_state[key][0], dict):
                            data = st.session_state[key]
                        else:
                            data = [{"Valore": x} for x in st.session_state[key]]
                # Prova anche da file CSV
                csv_file = f"{key}.csv" if key=="mem_nomi" else f"anagrafica_volontari_completa.csv" if key=="anag_full" else None
                if not data and csv_file and os.path.exists(csv_file):
                    try:
                        df_tmp = pd.read_csv(csv_file)
                        data = df_tmp.to_dict(orient="records")
                    except:
                        pass
                if data:
                    df = pd.DataFrame(data)
                    return df
                return pd.DataFrame()
            
            # Prepara dati
            dati_export = {}
            if exp_anag:
                # Anagrafica completa
                try:
                    if os.path.exists("anagrafica_volontari_completa.csv"):
                        df = pd.read_csv("anagrafica_volontari_completa.csv")
                        # Rimuovi FotoBase64 per export leggero (opzionale)
                        df_no_foto = df.drop(columns=["FotoBase64"], errors="ignore")
                        dati_export["Anagrafica_Volontari"] = df_no_foto
                        dati_export["Anagrafica_Volontari_CON_FOTO"] = df
                except:
                    pass
            if exp_eventi:
                if st.session_state.eventi:
                    dati_export["Eventi"] = pd.DataFrame(st.session_state.eventi)
            if exp_checkin:
                # Unisci tutti i checkin
                tutti_checkin = []
                for id_ev, lista in st.session_state.checkin.items():
                    for v in lista:
                        tutti_checkin.append(v)
                if tutti_checkin:
                    dati_export["CheckIn_Tutti_Eventi"] = pd.DataFrame(tutti_checkin)
                # Anche per evento singolo
                for id_ev, lista in st.session_state.checkin.items():
                    if lista:
                        dati_export[f"CheckIn_Evento_{id_ev}"] = pd.DataFrame(lista)
            
            if formato == "CSV":
                for nome_sheet, df in dati_export.items():
                    if not df.empty:
                        csv_data = df.to_csv(index=False).encode('utf-8')
                        st.download_button(f"📥 Scarica {nome_sheet}.csv", data=csv_data, file_name=f"{nome_export}_{nome_sheet}.csv", mime="text/csv", key=f"dl_csv_{nome_sheet}", use_container_width=True)
            elif formato == "Excel (XLSX)":
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    for nome_sheet, df in dati_export.items():
                        if not df.empty:
                            sheet_name = nome_sheet[:31]  # Excel max 31 char
                            df.to_excel(writer, index=False, sheet_name=sheet_name)
                st.download_button(f"📥 Scarica {nome_export}.xlsx - {len(dati_export)} fogli", data=output.getvalue(), file_name=f"{nome_export}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True, key="dl_excel")
            elif formato == "JSON":
                json_data = {k: v.to_dict(orient="records") for k, v in dati_export.items()}
                json_str = json.dumps(json_data, indent=2, ensure_ascii=False, default=str)
                st.download_button(f"📥 Scarica {nome_export}.json", data=json_str.encode('utf-8'), file_name=f"{nome_export}.json", mime="application/json", use_container_width=True, key="dl_json")
            else:  # ZIP con tutto
                output_zip = BytesIO()
                with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as z:
                    for nome_sheet, df in dati_export.items():
                        csv_bytes = df.to_csv(index=False).encode('utf-8')
                        z.writestr(f"{nome_sheet}.csv", csv_bytes)
                st.download_button(f"📥 Scarica ZIP con {len(dati_export)} CSV - {nome_export}.zip", data=output_zip.getvalue(), file_name=f"{nome_export}.zip", mime="application/zip", use_container_width=True, key="dl_zip")
            
            st.success(f"✅ Export pronto: {len(dati_export)} tabelle")
            for k, v in dati_export.items():
                st.caption(f"{k}: {len(v)} righe")
    
    with tab_imp:
        st.subheader("📥 Importa Dati da CSV")
        st.info("Carica file CSV esportati precedentemente per ripristinare dati")
        
        tipo_import = st.selectbox("Cosa vuoi importare?", ["Anagrafica Volontari", "Eventi", "Check-In", "Altro CSV generico"])
        file_import = st.file_uploader(f"📂 Seleziona CSV per {tipo_import}", type=["csv", "xlsx", "json"], key="import_csv")
        
        if file_import is not None:
            import pandas as pd
            try:
                if file_import.name.endswith('.csv'):
                    df_imp = pd.read_csv(file_import)
                elif file_import.name.endswith('.xlsx'):
                    df_imp = pd.read_excel(file_import)
                else:
                    import json
                    data_json = json.load(file_import)
                    # Se JSON con più tabelle, prendi prima
                    if isinstance(data_json, dict):
                        first_key = list(data_json.keys())[0]
                        df_imp = pd.DataFrame(data_json[first_key])
                    else:
                        df_imp = pd.DataFrame(data_json)
                
                st.success(f"✅ File caricato: {len(df_imp)} righe, {len(df_imp.columns)} colonne")
                st.dataframe(df_imp.head(20), use_container_width=True)
                
                # Anteprima colonne
                st.markdown(f"Colonne: {', '.join(df_imp.columns.tolist())}")
                
                col_imp1, col_imp2 = st.columns(2)
                with col_imp1:
                    modalita = st.selectbox("Modalità import", ["Aggiungi ai esistenti", "Sostituisci tutti", "Aggiorna per CF/ID"])
                with col_imp2:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button(f"📥 IMPORTA {tipo_import} ORA", use_container_width=True, type="primary"):
                        import os
                        if tipo_import == "Anagrafica Volontari":
                            # Salva in file anagrafica completa
                            if modalita == "Sostituisci tutti":
                                df_imp.to_csv("anagrafica_volontari_completa.csv", index=False)
                                st.session_state.mem_nomi = df_imp["Nome e Cognome"].tolist() if "Nome e Cognome" in df_imp.columns else []
                            else:
                                # Aggiungi
                                if os.path.exists("anagrafica_volontari_completa.csv"):
                                    df_exist = pd.read_csv("anagrafica_volontari_completa.csv")
                                    if modalita == "Aggiungi ai esistenti":
                                        df_new = pd.concat([df_exist, df_imp], ignore_index=True)
                                    else:  # Aggiorna per CF
                                        # Rimuovi duplicati per CF
                                        df_combined = pd.concat([df_exist, df_imp])
                                        df_new = df_combined.drop_duplicates(subset=["Codice Fiscale"], keep="last") if "Codice Fiscale" in df_combined.columns else df_combined
                                    df_new.to_csv("anagrafica_volontari_completa.csv", index=False)
                                else:
                                    df_imp.to_csv("anagrafica_volontari_completa.csv", index=False)
                            st.success(f"✅ Anagrafica importata: {len(df_imp)} volontari")
                            st.balloons()
                        
                        elif tipo_import == "Eventi":
                            eventi_list = df_imp.to_dict(orient="records")
                            if modalita == "Sostituisci tutti":
                                st.session_state.eventi = eventi_list
                            else:
                                st.session_state.eventi.extend(eventi_list)
                            sync_eventi()
                            st.success(f"✅ Eventi importati: {len(eventi_list)}")
                        
                        elif tipo_import == "Check-In":
                            # Richiede colonna Evento ID
                            if "Evento ID" in df_imp.columns:
                                for id_ev in df_imp["Evento ID"].unique():
                                    lista_ev = df_imp[df_imp["Evento ID"]==id_ev].to_dict(orient="records")
                                    if modalita == "Sostituisci tutti":
                                        st.session_state.checkin[int(id_ev)] = lista_ev
                                    else:
                                        if int(id_ev) not in st.session_state.checkin:
                                            st.session_state.checkin[int(id_ev)] = []
                                        st.session_state.checkin[int(id_ev)].extend(lista_ev)
                                sync_checkin()
                                st.success(f"✅ Check-In importati: {len(df_imp)}")
                            else:
                                st.error("CSV Check-In deve avere colonna 'Evento ID'")
                        st.rerun()
                        
            except Exception as e:
                st.error(f"Errore import: {e}")
    
    with tab_backup:
        st.subheader("💾 Backup Completo di TUTTI i Dati")
        st.markdown("Crea un backup ZIP con tutti i CSV, Excel, foto, eventi, check-in")
        
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            nome_backup = st.text_input("📝 Nome Backup", value=f"Backup_ANA_Varese_{datetime.now().strftime('%Y%m%d_%H%M%S')}", help="Nome senza estensione - verrà creato ZIP")
        with col_b2:
            st.markdown("**📂 Dove salvare:**")
            luogo = st.selectbox("Scegli", ["Download locale (PC/telefono)", "Google Drive (se collegato)", "Entrambi"], key="luogo_backup")
            include_foto = st.checkbox("📷 Includi foto volontari (più grande)", value=True)
        
        st.markdown("#### Cosa includere nel backup:")
        b1, b2, b3 = st.columns(3)
        with b1:
            bk_anag = st.checkbox("👥 Anagrafica + Foto", value=True, key="bk_anag")
            bk_eventi = st.checkbox("📅 Eventi", value=True, key="bk_eventi")
        with b2:
            bk_checkin = st.checkbox("📝 Check-In", value=True, key="bk_checkin")
            bk_chat = st.checkbox("💬 Chat", value=False, key="bk_chat")
        with b3:
            bk_radio = st.checkbox("📻 Radio + Postazioni", value=True, key="bk_radio")
            bk_tutto = st.checkbox("📦 Tutti i CSV presenti", value=True, key="bk_tutto")
        
        if st.button("💾 CREA BACKUP COMPLETO ORA", use_container_width=True, type="primary", key="btn_backup"):
            import os, zipfile, pandas as pd
            from io import BytesIO
            import json
            
            output_zip = BytesIO()
            file_count = 0
            
            with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as z:
                # 1. Anagrafica
                if bk_anag and os.path.exists("anagrafica_volontari_completa.csv"):
                    try:
                        if include_foto:
                            z.write("anagrafica_volontari_completa.csv")
                        else:
                            df = pd.read_csv("anagrafica_volontari_completa.csv")
                            df_no_foto = df.drop(columns=["FotoBase64"], errors="ignore")
                            z.writestr("anagrafica_volontari_completa.csv", df_no_foto.to_csv(index=False))
                        file_count += 1
                    except:
                        pass
                
                # 2. Tutti i CSV nella cartella
                if bk_tutto:
                    for fname in os.listdir("."):
                        if fname.endswith(".csv") and fname not in ["comuni_italia.csv"]:
                            try:
                                z.write(fname)
                                file_count += 1
                            except:
                                pass
                
                # 3. Eventi e Checkin da session_state
                if bk_eventi and st.session_state.eventi:
                    df_ev = pd.DataFrame(st.session_state.eventi)
                    z.writestr("backup_eventi.csv", df_ev.to_csv(index=False))
                    z.writestr("backup_eventi.json", json.dumps(st.session_state.eventi, indent=2, default=str))
                    file_count += 1
                
                if bk_checkin and st.session_state.checkin:
                    tutti = []
                    for id_ev, lista in st.session_state.checkin.items():
                        tutti.extend(lista)
                    if tutti:
                        df_ck = pd.DataFrame(tutti)
                        z.writestr("backup_checkin_tutti.csv", df_ck.to_csv(index=False))
                        z.writestr("backup_checkin.json", json.dumps(st.session_state.checkin, indent=2, default=str))
                        file_count += 1
                
                # 4. Info backup
                info = {
                    "nome_backup": nome_backup,
                    "data": datetime.now().isoformat(),
                    "utente": st.session_state.get("utente_multi",""),
                    "file_inclusi": file_count,
                    "eventi": len(st.session_state.eventi),
                    "checkin_totali": sum(len(v) for v in st.session_state.checkin.values()),
                    "volontari": len(pd.read_csv("anagrafica_volontari_completa.csv")) if os.path.exists("anagrafica_volontari_completa.csv") else 0
                }
                z.writestr("backup_info.json", json.dumps(info, indent=2, ensure_ascii=False))
                z.writestr("README.txt", f"Backup ANA Varese\nNome: {nome_backup}\nData: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\nFile: {file_count}\nCreato da: {info['utente']}")
            
            st.success(f"✅ Backup creato: {file_count} file - {len(output_zip.getvalue())/1024:.1f} KB")
            st.json(info)
            
            # Download
            st.download_button(
                f"📥 SCARICA BACKUP {nome_backup}.zip",
                data=output_zip.getvalue(),
                file_name=f"{nome_backup}.zip",
                mime="application/zip",
                use_container_width=True,
                type="primary",
                key="dl_backup_final"
            )
            
            if luogo in ["Google Drive (se collegato)", "Entrambi"]:
                st.info("💡 Per salvare su Drive: scarica e carica manualmente su Drive, oppure collega Google Drive nelle impostazioni Streamlit")
    
    with tab_restore:
        st.subheader("♻️ Ripristina da Backup ZIP")
        st.warning("⚠️ Ripristino sovrascrive dati esistenti - fai backup prima!")
        
        file_backup = st.file_uploader("📂 Seleziona file ZIP di backup", type=["zip"], key="restore_zip")
        
        if file_backup is not None:
            import zipfile, os, pandas as pd, json
            from io import BytesIO
            
            try:
                with zipfile.ZipFile(file_backup, 'r') as z:
                    lista_file = z.namelist()
                    st.success(f"✅ Backup ZIP valido: {len(lista_file)} file")
                    st.markdown(f"File nel backup: {', '.join(lista_file[:20])}")
                    
                    if "backup_info.json" in lista_file:
                        info_data = json.loads(z.read("backup_info.json"))
                        st.json(info_data)
                    
                    col_r1, col_r2 = st.columns(2)
                    with col_r1:
                        conferma = st.checkbox("✅ Confermo ripristino - sovrascrivi dati", key="conf_restore")
                    with col_r2:
                        cosa = st.selectbox("Cosa ripristinare", ["Tutto", "Solo Anagrafica", "Solo Eventi e Check-In"])
                    
                    if conferma and st.button("♻️ RIPRISTINA ORA", use_container_width=True, type="primary"):
                        # Estrai tutti
                        for fname in lista_file:
                            if fname.endswith(".csv"):
                                try:
                                    data = z.read(fname)
                                    with open(fname, "wb") as f:
                                        f.write(data)
                                except:
                                    pass
                        
                        # Ripristina anche eventi/checkin da JSON se presenti
                        if "backup_eventi.json" in lista_file:
                            try:
                                eventi_data = json.loads(z.read("backup_eventi.json"))
                                st.session_state.eventi = eventi_data
                                sync_eventi()
                            except:
                                pass
                        
                        if "backup_checkin.json" in lista_file:
                            try:
                                checkin_data = json.loads(z.read("backup_checkin.json"))
                                # JSON chiavi stringa -> int
                                st.session_state.checkin = {int(k): v for k, v in checkin_data.items()}
                                sync_checkin()
                            except:
                                pass
                        
                        st.success("✅ Ripristino completato! Ricarica pagina")
                        st.balloons()
                        st.rerun()
                        
            except Exception as e:
                st.error(f"Errore lettura ZIP: {e}")

def sync_eventi():
    try:
        import pandas as pd
        if st.session_state.eventi:
            pd.DataFrame(st.session_state.eventi).to_csv("eventi_backup.csv", index=False)
    except:
        pass

def sync_checkin():
    try:
        import json
        with open("checkin_backup.json", "w") as f:
            json.dump(st.session_state.checkin, f, default=str)
    except:
        pass


def sync_eventi_OLD():
    salva_json(FILE_EVENTI, st.session_state.eventi)

def sync_checkin():
    # Salva con chiavi stringa per JSON
    salva_json(FILE_CHECKIN, {str(k): v for k, v in st.session_state.checkin.items()})

def sync_chat():
    salva_json(FILE_CHAT, st.session_state.chat_messages[-200:])  # ultimi 200

def sync_utenti():
    salva_json(FILE_UTENTI, st.session_state.utenti_collegati)

# ========== FINE MULTI-UTENTE ==========

# ========== CHAT SISTEMA COLLEGATI ==========

def pagina_chat():
    st.title("💬 Chat - Volontari Collegati")
    
    # Login chat - nome utente
    if not st.session_state.mio_nome:
        st.markdown('<div style="background:#e8f5e9; padding:20px; border-radius:15px; text-align:center;"><h3>👋 Entra in Chat</h3><p>Inserisci il tuo nome per vedere chi e collegato e chattare</p></div>', unsafe_allow_html=True)
        nome = st.text_input("👤 Il tuo Nome e Cognome", placeholder="Es: Ezio Fiscato - ODV Varese")
        odv_chat = st.text_input("🏢 ODV / Gruppo", placeholder="Es: ANA Varese")
        if st.button("💬 Entra in Chat", use_container_width=True, type="primary"):
            if nome:
                st.session_state.mio_nome = nome
                st.session_state.mio_odv = odv_chat
                # Registra utente come collegato
                st.session_state.utenti_collegati[nome] = {
                    "nome": nome,
                    "odv": odv_chat,
                    "ultimo_accesso": datetime.now().strftime("%H:%M:%S"),
                    "data": datetime.now().strftime("%d/%m/%Y")
                }
                # Messaggio sistema
                st.session_state.chat_messages.append({
                    "utente": "SISTEMA",
                    "messaggio": f"{nome} si e collegato alla chat",
                    "ora": datetime.now().strftime("%H:%M"),
                    "odv": odv_chat,
                    "tipo": "sistema"
                })
                sync_utenti()
                sync_chat()
                st.rerun()
        return
    
    # Utente già in chat - mostra interfaccia
    col_chat, col_users = st.columns([3,1])
    
    with col_users:
        st.markdown("### 👥 Collegati")
        st.markdown(f"**Tu:** {st.session_state.mio_nome}")
        if st.button("🔄 Aggiorna"):
            st.rerun()
        if st.button("🚪 Esci da Chat"):
            if st.session_state.mio_nome in st.session_state.utenti_collegati:
                del st.session_state.utenti_collegati[st.session_state.mio_nome]
            st.session_state.chat_messages.append({
                "utente": "SISTEMA",
                "messaggio": f"{st.session_state.mio_nome} si e disconnesso",
                "ora": datetime.now().strftime("%H:%M"),
                "odv": "",
                "tipo": "sistema"
            })
            st.session_state.mio_nome = ""
            st.rerun()
        
        st.divider()
        # Lista utenti collegati
        if st.session_state.utenti_collegati:
            for nome, info in st.session_state.utenti_collegati.items():
                if nome == st.session_state.mio_nome:
                    st.markdown(f"🟢 **{nome}** (tu)<br><small>{info.get('odv','')}</small><br><small>{info['ultimo_accesso']}</small>", unsafe_allow_html=True)
                else:
                    st.markdown(f"🟢 {nome}<br><small>{info.get('odv','')}</small><br><small>{info['ultimo_accesso']}</small>", unsafe_allow_html=True)
                st.markdown("---")
        else:
            st.info("Nessun altro collegato")
        
        st.metric("Messaggi", len(st.session_state.chat_messages))
        st.metric("Utenti Online", len(st.session_state.utenti_collegati))
    
    with col_chat:
        st.markdown(f"### 💬 Chat - Connesso come **{st.session_state.mio_nome}**")
        
        # Container messaggi con sfondo verde chiaro
        st.markdown('<div style="background:#f1f8e9; border-radius:10px; padding:10px; max-height:400px; overflow-y:auto;">', unsafe_allow_html=True)
        
        # Mostra messaggi (ultimi 50)
        for msg in st.session_state.chat_messages[-50:]:
            if msg.get("tipo") == "sistema":
                st.markdown(f'<div style="text-align:center; color:#666; font-style:italic; margin:5px 0;"><small>--- {msg["messaggio"]} - {msg["ora"]} ---</small></div>', unsafe_allow_html=True)
            elif msg["utente"] == st.session_state.mio_nome:
                st.markdown(f'<div style="background:#a5d6a7; padding:8px 12px; border-radius:15px 15px 0 15px; margin:5px 0 5px 40px; text-align:right;"><b>Tu</b><br>{msg["messaggio"]}<br><small>{msg["ora"]}</small></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div style="background:white; padding:8px 12px; border-radius:15px 15px 15px 0; margin:5px 40px 5px 0; border:1px solid #c8e6c9;"><b>{msg["utente"]}</b> <small>({msg.get("odv","")})</small><br>{msg["messaggio"]}<br><small>{msg["ora"]}</small></div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.divider()
        # Input messaggio
        with st.form(f"chat_form_{len(st.session_state.chat_messages)}", clear_on_submit=True):
            col_in, col_btn = st.columns([4,1])
            with col_in:
                nuovo_msg = st.text_input("Scrivi messaggio", placeholder="Scrivi qui...", label_visibility="collapsed")
            with col_btn:
                invia = st.form_submit_button("📤 Invia", use_container_width=True, type="primary")
            
            if invia and nuovo_msg:
                st.session_state.chat_messages.append({
                    "utente": st.session_state.mio_nome,
                    "messaggio": nuovo_msg,
                    "ora": datetime.now().strftime("%H:%M"),
                    "odv": st.session_state.get("mio_odv",""),
                    "tipo": "utente"
                })
                sync_chat()
                # Aggiorna ultimo accesso
                if st.session_state.mio_nome in st.session_state.utenti_collegati:
                    st.session_state.utenti_collegati[st.session_state.mio_nome]["ultimo_accesso"] = datetime.now().strftime("%H:%M:%S")
                st.rerun()
        
        # Pulsanti rapidi messaggi predefiniti per emergenza
        st.markdown("**Messaggi rapidi:**")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            if st.button("✅ Tutto OK", use_container_width=True):
                st.session_state.chat_messages.append({"utente": st.session_state.mio_nome, "messaggio": "✅ Tutto OK nella mia zona", "ora": datetime.now().strftime("%H:%M"), "odv": st.session_state.get("mio_odv",""), "tipo": "utente"})
                st.rerun()
        with c2:
            if st.button("🚨 Emergenza", use_container_width=True):
                st.session_state.chat_messages.append({"utente": st.session_state.mio_nome, "messaggio": "🚨 RICHIESTA SUPPORTO URGENTE!", "ora": datetime.now().strftime("%H:%M"), "odv": st.session_state.get("mio_odv",""), "tipo": "utente"})
                st.rerun()
        with c3:
            if st.button("📍 Posizione", use_container_width=True):
                st.session_state.chat_messages.append({"utente": st.session_state.mio_nome, "messaggio": "📍 Condivido posizione - sono in postazione", "ora": datetime.now().strftime("%H:%M"), "odv": st.session_state.get("mio_odv",""), "tipo": "utente"})
                st.rerun()
        with c4:
            if st.button("🔄 Cambio Turno", use_container_width=True):
                st.session_state.chat_messages.append({"utente": st.session_state.mio_nome, "messaggio": "🔄 Richiesta cambio turno", "ora": datetime.now().strftime("%H:%M"), "odv": st.session_state.get("mio_odv",""), "tipo": "utente"})
                st.rerun()
        
        # Export chat
        if st.session_state.chat_messages:
            if st.button("📥 Esporta Chat in Excel"):
                df_chat = pd.DataFrame(st.session_state.chat_messages)
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df_chat.to_excel(writer, index=False)
                st.download_button("Scarica Excel Chat", data=output.getvalue(), file_name=f"chat_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# ========== FINE CHAT ==========

# --- Presentazione ---
if "entered" not in st.session_state:
    st.session_state.entered = False
if "current_page" not in st.session_state:
    st.session_state.current_page = "🏠 Dashboard"

if not st.session_state.entered:
    st.markdown("""
    <style>
    [data-testid="stSidebar"] {display: none;}
    .main .block-container {max-width: 900px; padding-top: 2rem;}
    </style>
    """, unsafe_allow_html=True)
    # Doppio logo - ANA + secondo logo
    col_logo1, col_logo2 = st.columns(2)
    with col_logo1:
        try:
            st.image("logo.png", width=80)
            st.markdown("<div style='text-align:center;'><b>ANA Varese</b></div>", unsafe_allow_html=True)
        except:
            st.markdown("## 🎖️ ANA Varese")
    with col_logo2:
        try:
            st.image("logo2.png", width=80)
            st.markdown("<div style='text-align:center;'><b>Secondo Logo</b></div>", unsafe_allow_html=True)
        except:
            try:
                st.image("logo_protezione.png", width=80)
            except:
                st.markdown("""
                <div style='border:2px dashed #0e7a3d; border-radius:10px; padding:40px; text-align:center; background:#e8f5e9;'>
                    <p style='font-size:50px; margin:0;'>🛡️</p>
                    <p><b>Secondo Logo qui</b><br>Carica file come:<br><code>logo2.png</code><br>oppure<br><code>logo_protezione.png</code></p>
                </div>
                """, unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align:center; padding:20px;">
        <h1 style="color:#0e7a3d; font-size:42px; margin-bottom:0;">🎖️ ANA - ASSOCIAZIONE NAZIONALE ALPINI</h1>
        <h2 style="color:#333; font-size:28px; margin-top:5px;">Sezione di Varese</h2>
        <h3 style="color:#666; font-size:20px; margin-top:20px;">Sistema Gestione Volontari, Radio e Postazioni</h3>
        <div style="background:#e8f5e9; padding:20px; border-radius:15px; margin:30px 0; border-left:6px solid #0e7a3d; text-align:left;">
            <p style="font-size:16px; color:#333; margin:0;">
            ✅ <b>Dashboard</b> - Riepilogo generale<br>
            👥 <b>Volontari</b> - Anagrafica completa<br>
            📻 <b>DB Radio</b> - Inventario radio<br>
            📦 <b>Distribuzione</b> - Consegna radio con firma<br>
            🗺️ <b>Mappa</b> - Postazioni FULLSCREEN OSM/Google + Navigazione<br>
            📋 <b>Registro</b> - Registro uso radio<br>
            🔗 <b>Link</b> - Condivisione aggiornamenti con QR Code
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    col_a, col_b, col_c = st.columns([1,1,1])
    with col_b:
        if st.button("🚀 ENTRA NEL SISTEMA", use_container_width=True, type="primary"):
            st.session_state.entered = True
            st.rerun()
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align:center; background:#f8f9fa; padding:15px; border-radius:10px; margin-top:30px;">
        <p style="font-size:14px; color:#888; margin:0;">Realizzato con ❤️ per la Sezione ANA Varese</p>
        <p style="font-size:20px; color:#0e7a3d; font-weight:bold; margin:5px 0;">👨‍💻 Realizzato da Ezio Fiscato</p>
        <p style="font-size:12px; color:#aaa; margin:0;">Versione 2025 - Gestionale Volontariato</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# --- Funzioni comuni ---
def combo_memoria(label, opzioni, key_suffix, placeholder=""):
    if not opzioni:
        opzioni = ["Volontario"]
    sel = st.selectbox(label, opzioni + ["-- Nuovo --"], key=f"combo_{key_suffix}")
    if sel == "-- Nuovo --":
        nuovo = st.text_input(f"Nuovo {label}", placeholder=placeholder, key=f"nuovo_{key_suffix}")
        return nuovo if nuovo else ""
    return sel

# Files
FILE_NOMI = "mem_nomi.csv"
FILE_RADIO_DB = "radio_db.csv"
FILE_DIST_RADIO = "distribuzione_radio.csv"
FILE_POSTAZIONI = "postazioni_mappa.csv"
FILE_REGISTRO = "registro_radio.csv"
FILE_BROGLIACCIO = "brogliaccio.csv"
FILE_COMUNICAZIONI = "brogliaccio_comunicazioni.csv"

for f_name, key in [(FILE_NOMI, "mem_nomi"), (FILE_RADIO_DB, "radio_db"), (FILE_DIST_RADIO, "dist_radio"), (FILE_POSTAZIONI, "postazioni"), (FILE_REGISTRO, "registro_radio"), (FILE_BROGLIACCIO, "brogliaccio"), (FILE_COMUNICAZIONI, "comunicazioni")]:
    if key not in st.session_state:
        if os.path.exists(f_name):
            try:
                df_tmp = pd.read_csv(f_name)
                st.session_state[key] = df_tmp.to_dict(orient="records") if not df_tmp.empty else []
            except:
                st.session_state[key] = []
        else:
            st.session_state[key] = []

if "selected_postazione" not in st.session_state:
    st.session_state.selected_postazione = None
if "mem_nomi" not in st.session_state or not st.session_state.mem_nomi:
    st.session_state.mem_nomi = ["Mario Rossi", "Luigi Bianchi", "Giuseppe Verdi"]

def salva_csv(data, filename):
    if data:
        pd.DataFrame(data).to_csv(filename, index=False)


import requests


@st.cache_data(ttl=86400, show_spinner=False)

def formatta_data_it(data_obj):
    """Converte data in formato italiano GG/MM/AAAA"""
    try:
        if isinstance(data_obj, str):
            # Prova a parsare vari formati
            for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"]:
                try:
                    from datetime import datetime as dt
                    d = dt.strptime(data_obj, fmt)
                    return d.strftime("%d/%m/%Y")
                except:
                    continue
            return data_obj
        else:
            return data_obj.strftime("%d/%m/%Y")
    except:
        return str(data_obj)


def get_comuni_italiani():
    """TUTTI i comuni Italia - 7900 comuni con ricerca"""
    comuni = []
    try:
        import os, pandas as pd
        if os.path.exists("comuni_italia.csv"):
            df = pd.read_csv("comuni_italia.csv")
            for _, row in df.iterrows():
                com = str(row.get("Comune","")).strip()
                prov = str(row.get("Provincia","")).strip()
                if com:
                    comuni.append(f"{com} ({prov})" if prov else com)
    except:
        pass
    if len(comuni) < 100:
        try:
            url = "https://comuni-ita.nicolorebaioli.dev/comuni?fields=nome,provincia.nome&sort=nome&pagesize=8000"
            resp = requests.get(url, timeout=8)
            if resp.status_code == 200:
                data = resp.json()
                lista = data if isinstance(data, list) else data.get("data", [])
                for c in lista:
                    nome = c.get("nome","")
                    if nome:
                        prov = c.get("provincia",{}).get("nome","") if isinstance(c.get("provincia"), dict) else ""
                        comuni.append(f"{nome} ({prov})" if prov else nome)
        except:
            pass
    if len(comuni) < 100:
        comuni = [
            "Varese (Varese)", "Milano (Milano)", "Roma (Roma)", "Busto Arsizio (Varese)", "Gallarate (Varese)",
            "Saronno (Varese)", "Como (Como)", "Bergamo (Bergamo)", "Brescia (Brescia)", "Torino (Torino)",
            "Napoli (Napoli)", "Bologna (Bologna)", "Firenze (Firenze)", "Genova (Genova)", "Venezia (Venezia)"
        ]
    return sorted(list(set(comuni)))


def get_vie_comune(comune_pulito):
    """Prende vie di un comune tramite Overpass API"""
    vie = []
    try:
        # Pulisci nome comune da provincia
        comune = comune_pulito.split("(")[0].strip().split("-")[0].strip()
        if not comune:
            return []
        # Overpass query per strade
        overpass_url = "https://overpass-api.de/api/interpreter"
        query = f"""
        [out:json][timeout:25];
        area["name"="{comune}"]["admin_level"~"6|8"]->.searchArea;
        (
          way["highway"]["name"](area.searchArea);
        );
        out tags 200;
        """
        # Prova anche con ricerca più larga se area non trovata
        headers = {"User-Agent": "ANA-Varese-App/1.0"}
        resp = requests.post(overpass_url, data={"data": query}, headers=headers, timeout=20)
        if resp.status_code == 200:
            data = resp.json()
            for el in data.get("elements", []):
                name = el.get("tags", {}).get("name")
                if name and len(name) > 2:
                    vie.append(name)
        # Se poche vie, prova Nominatim streets search alternativa
        if len(vie) < 5:
            # Ricerca vie con Nominatim: cerca vie popolari
            nominatim_url = "https://nominatim.openstreetmap.org/search"
            params = {"q": comune, "format": "json", "addressdetails": 1, "limit": 1}
            r = requests.get(nominatim_url, params=params, headers=headers, timeout=10)
            if r.status_code == 200 and r.json():
                # Non abbiamo lista vie da Nominatim, quindi proponiamo vie comuni
                pass
        vie = sorted(list(set(vie)))[:500]  # max 500
        return vie
    except Exception as e:
        return []

def geocode_comune_via_dettagliato(comune_display, via):
    """Geocoding con comune pulito"""
    try:
        return geocode_comune_via(comune_display, via)
    except Exception as e:
        return None, None, f"Errore: {e}"


def geocode_comune_via(comune, via, civico=""):
    """Cerca lat/lon da comune, via e civico - robusto con fallback multipli per 403"""
    try:
        comune_clean = comune.split("(")[0].strip() if "(" in comune else comune
        # Costruisci query con civico
        via_completa = f"{via} {civico}".strip() if civico else via
        query = f"{via_completa}, {comune_clean}, Italy" if via_completa and comune_clean else f"{comune_clean}, Italy" if comune_clean else via_completa
        if not query or query.strip() == ", Italy" or query.strip() == "" or query.strip() == "Italy":
            return None, None, "Inserisci comune e via"
        
        headers = {
            "User-Agent": "ANA-Varese-App/1.0 (contact: ezio.fiscato@ana.varese.it)",
            "Accept": "application/json",
            "Accept-Language": "it-IT,it;q=0.9"
        }
        
        # TENTATIVO 1: Nominatim OSM
        try:
            url = "https://nominatim.openstreetmap.org/search"
            params = {"q": query, "format": "json", "limit": 1, "countrycodes": "it", "addressdetails": 1, "email": "ezio.fiscato@ana.varese.it"}
            resp = requests.get(url, params=params, headers=headers, timeout=12)
            if resp.status_code == 200:
                data = resp.json()
                if data:
                    lat = data[0].get("lat")
                    lon = data[0].get("lon")
                    display = data[0].get("display_name", "")
                    return lat, lon, display
            elif resp.status_code == 403:
                # 403 - prova con Photon
                pass
            else:
                resp.raise_for_status()
        except Exception as e1:
            # Se Nominatim fallisce, prova Photon
            pass
        
        # TENTATIVO 2: Photon Komoot (fallback per 403)
        try:
            photon_url = "https://photon.komoot.io/api/"
            photon_params = {"q": query, "limit": 1, "lang": "it"}
            resp2 = requests.get(photon_url, params=photon_params, headers=headers, timeout=12)
            if resp2.status_code == 200:
                data2 = resp2.json()
                feats = data2.get("features", [])
                if feats:
                    coords = feats[0].get("geometry", {}).get("coordinates", [])
                    props = feats[0].get("properties", {})
                    if len(coords) >= 2:
                        lon, lat = coords[0], coords[1]
                        display = f"{props.get('name','')} {props.get('street','')} {props.get('city','')} {props.get('country','')}".strip()
                        if not display:
                            display = props.get("name", query)
                        return str(lat), str(lon), display
        except Exception as e2:
            pass
        
        # TENTATIVO 3: Solo comune (senza via) su Nominatim
        try:
            if via and comune_clean:
                # Prova solo comune
                url3 = "https://nominatim.openstreetmap.org/search"
                params3 = {"q": f"{comune_clean}, Italy", "format": "json", "limit": 1, "countrycodes": "it"}
                resp3 = requests.get(url3, params=params3, headers=headers, timeout=10)
                if resp3.status_code == 200:
                    data3 = resp3.json()
                    if data3:
                        lat = data3[0].get("lat")
                        lon = data3[0].get("lon")
                        display = data3[0].get("display_name", "") + f" (centro {comune_clean} - via non trovata, puoi spostare manualmente)"
                        return lat, lon, display
        except:
            pass
        
        return None, None, f"Nessun risultato per '{query}'. Prova con solo Comune o via più semplice (es: Via Roma)"
    except Exception as e:
        return None, None, f"Errore rete: {str(e)} - Prova con solo Comune"

def geocode_comune_via_completo(comune, via, civico=""):
    return geocode_comune_via(comune, via, civico)



def calc_h(text, max_w=35):
    if not text:
        return 8
    t = str(text)
    lines = 1
    for part in t.split("\n"):
        lines += len(part) // max_w
    return min(max(lines * 5, 8), 30)

# --- MENU MULTIPAGINA ---
st.sidebar.image("logo.png", width=120) if os.path.exists("logo.png") else st.sidebar.markdown("### 🎖️ ANA Varese")
st.sidebar.markdown("## 📚 MENU PRINCIPALE")

pagine = {
    "💾 Backup/Export/Import": "Backup",
    "🆔 Calcolo CF": "CF",
    "💬 Chat Collegati": "Chat",
    "📅 Gestione Eventi": "Eventi",
    "📝 Check-In Volontari": "CheckIn",
    "🏠 Dashboard": "Dashboard",
    "👥 Volontari": "Volontari",
    "📝 Brogliaccio": "Brogliaccio",
    "📻 DB Radio Inventario": "DB Radio",
    "📦 Distribuzione Radio": "Distribuzione",
    "🗺️ Mappa Postazioni": "Mappa",
    "📋 Registro Radio": "Registro",
    "🔗 Link & Aggiornamenti": "Link"
}

# Fix navigazione - usa current_page come stato
pagine_list = list(pagine.keys())
try:
    current_idx = pagine_list.index(st.session_state.current_page)
except:
    current_idx = 0
    st.session_state.current_page = pagine_list[0]

# Sidebar radio - sincronizzata con current_page
# Usa callback per evitare loop
def on_sidebar_change():
    pass

scelta_radio = st.sidebar.radio("Vai a:", pagine_list, index=current_idx, key="menu_radio")
# Se utente cambia da sidebar, aggiorna current_page
if scelta_radio != st.session_state.current_page:
    st.session_state.current_page = scelta_radio

scelta = st.session_state.current_page

if st.sidebar.button("🏠 Torna a Presentazione", use_container_width=True):
    st.session_state.entered = False
    st.rerun()

st.sidebar.divider()
if st.sidebar.button("📅 Nuovo Evento", use_container_width=True):
    st.session_state.page_extra="evento_crea"
    st.rerun()
if st.sidebar.button("📝 Check-In", use_container_width=True):
    st.session_state.page_extra="checkin"
    st.rerun()
st.sidebar.caption(f"👤 Realizzato da Ezio Fiscato")
st.sidebar.caption(f"📅 {datetime.now().strftime('%d/%m/%Y')}")

# ROUTING RAPIDO PER TASTI DASHBOARD - DEVE ESSERE QUI
if st.session_state.get("page_extra") == "evento_crea":
    pagina_crea_evento()
    st.stop()


# Titolo pagina
st.markdown(f"## {scelta}")
st.divider()


# === BACKUP ===
if scelta == "💾 Backup/Export/Import":
    pagina_backup()
    st.stop()

# === CALCOLO CF ===
if scelta == "🆔 Calcolo CF":
    pagina_calcolo_cf()
    st.stop()

# === CHAT ===
if scelta == "💬 Chat Collegati":
    pagina_chat()
    st.stop()

# === EVENTI MENU ===
if scelta == "📅 Gestione Eventi":
    st.title("📅 Gestione Eventi")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("➕ Crea Nuovo Evento", use_container_width=True, type="primary"):
            st.session_state.page_extra="evento_crea"
            st.rerun()
    with col2:
        if st.button("📋 Lista Eventi", use_container_width=True):
            if st.session_state.eventi:
                import pandas as pd
                st.dataframe(pd.DataFrame(st.session_state.eventi), use_container_width=True)
            else:
                st.info("Nessun evento")
    with col3:
        if st.button("🔄 Aggiorna da Altri Utenti", use_container_width=True):
            st.session_state.eventi = carica_json(FILE_EVENTI, st.session_state.eventi)
            st.rerun()
    
    st.divider()
    # Mostra lista eventi con azioni
    if st.session_state.eventi:
        import pandas as pd
        df = pd.DataFrame(st.session_state.eventi)
        st.dataframe(df, use_container_width=True)
        
        # Selezione per check-in
        ids = [f"{e['ID']} - {e['Tipo Servizio']} - {e['Comune']}" for e in st.session_state.eventi]
        sel = st.selectbox("Seleziona evento per Check-In", ids, key="sel_evento_menu")
        if st.button("📝 Vai a Check-In per questo evento", use_container_width=True, type="primary"):
            st.session_state.page_extra="checkin"
            st.session_state.evento_selezionato_per_menu = int(sel.split(" - ")[0])
            st.rerun()
    else:
        st.info("Nessun evento creato")
    st.stop()

if scelta == "📝 Check-In Volontari":
    pagina_checkin()
    st.stop()


# === DASHBOARD ===
if scelta == "🏠 Dashboard":
    col1,col2,col3,col4,col5 = st.columns(5)
    with col1:
        st.metric("👥 Volontari", len(st.session_state.mem_nomi))
    with col2:
        st.metric("📝 Brogliaccio", len(st.session_state.brogliaccio) if "brogliaccio" in st.session_state else 0)
    with col3:
        st.metric("📻 Radio in DB", len(st.session_state.radio_db))
    with col4:
        st.metric("📦 Distribuzioni", len(st.session_state.dist_radio))
    with col5:
        st.metric("🗺️ Postazioni", len(st.session_state.postazioni))
    
    st.markdown("### 🚀 Accesso Rapido - TUTTI I TASTI ATTIVI")
    st.success("✅ Tutti i pulsanti sotto sono collegati e funzionanti - clicca per andare alla funzione!")
    
    # Funzione per navigare - robusta
    def set_page(pagina):
        st.session_state.current_page = pagina
    
    # Prima riga - 4 colonne con callback on_click
    c1,c2,c3,c4 = st.columns(4)
    with c1:
        st.markdown("**👥 Anagrafica**")
        st.button("👥 Gestisci Volontari", use_container_width=True, type="primary", key="dash_vol_final", on_click=set_page, args=("👥 Volontari",))
        st.button("📝 Brogliaccio ODV", use_container_width=True, type="primary", key="dash_brog_final", on_click=set_page, args=("📝 Brogliaccio",))
        st.button("📻 DB Radio Inventario", use_container_width=True, key="dash_db_final", on_click=set_page, args=("📻 DB Radio Inventario",))
        st.button("📻 Sottomaschera Comunicazioni", use_container_width=True, key="dash_sotto_final", on_click=set_page, args=("📝 Brogliaccio",))
    
    with c2:
        st.markdown("**📦 Operativo**")
        st.button("📦 Distribuisci Radio", use_container_width=True, type="primary", key="dash_dist_final", on_click=set_page, args=("📦 Distribuzione Radio",))
        st.button("🗺️ Mappa Postazioni", use_container_width=True, type="primary", key="dash_mappa_final", on_click=set_page, args=("🗺️ Mappa Postazioni",))
        st.button("📋 Registro Radio", use_container_width=True, key="dash_reg_final", on_click=set_page, args=("📋 Registro Radio",))
        st.button("🔗 Link & Aggiornamenti", use_container_width=True, key="dash_link_final", on_click=set_page, args=("🔗 Link & Aggiornamenti",))
    
    with c3:
        st.markdown("**⚡ Azioni Rapide**")
        if st.button("🏠 Presentazione", use_container_width=True, key="dash_home_final"):
            st.session_state.entered = False
            st.rerun()
        if st.button("🔄 Aggiorna Dashboard", use_container_width=True, key="dash_refresh_final"):
            st.rerun()
        if st.button("⛶ Espandi Pagina", use_container_width=True, key="dash_expand_final"):
            cur = st.session_state.get("page_expanded", False)
            st.session_state["page_expanded"] = not cur
            st.rerun()
        st.button("📝 Vai a Brogliaccio + Comunicazioni", use_container_width=True, key="dash_brog_com", on_click=set_page, args=("📝 Brogliaccio",))
    
    with c4:
        st.markdown("#### 📊 Riepilogo Live")
        tot_brog = len(st.session_state.brogliaccio) if "brogliaccio" in st.session_state else 0
        tot_com = len(st.session_state.comunicazioni) if "comunicazioni" in st.session_state else 0
        tot_vol = len(st.session_state.mem_nomi)
        tot_radio = len(st.session_state.radio_db)
        tot_dist = len(st.session_state.dist_radio)
        st.metric("👥 Volontari", tot_vol)
        st.metric("📝 Brogliaccio", tot_brog)
        st.metric("📻 Comunicazioni", tot_com)
        st.metric("📦 Radio DB", tot_radio)
        st.metric("Distribuzioni", tot_dist)
    
    st.divider()
    st.markdown("#### 🔗 Navigazione Rapida - Barra Pulsanti Grandi (TUTTI ATTIVI)")
    cc1,cc2,cc3,cc4,cc5,cc6,cc7 = st.columns(7)
    with cc1:
        st.button("👥 VOLONTARI", use_container_width=True, key="big_vol_final", on_click=set_page, args=("👥 Volontari",))
    with cc2:
        st.button("📝 BROGLIACCIO", use_container_width=True, key="big_brog_final", on_click=set_page, args=("📝 Brogliaccio",))
    with cc3:
        st.button("📻 DB RADIO", use_container_width=True, key="big_db_final", on_click=set_page, args=("📻 DB Radio Inventario",))
    with cc4:
        st.button("📦 DISTRIB", use_container_width=True, key="big_dist_final", on_click=set_page, args=("📦 Distribuzione Radio",))
    with cc5:
        st.button("🗺️ MAPPA", use_container_width=True, key="big_mappa_final", on_click=set_page, args=("🗺️ Mappa Postazioni",))
    with cc6:
        st.button("📋 REGISTRO", use_container_width=True, key="big_reg_final", on_click=set_page, args=("📋 Registro Radio",))
    with cc7:
        st.button("🔗 LINK", use_container_width=True, key="big_link_final", on_click=set_page, args=("🔗 Link & Aggiornamenti",))
    
    if st.session_state.dist_radio:
        st.markdown("### 📦 Ultime Distribuzioni")
        st.dataframe(pd.DataFrame(st.session_state.dist_radio).tail(5).iloc[::-1], use_container_width=True, hide_index=True)

# === VOLONTARI - ANAGRAFICA COMPLETA PROFESSIONALE ANA ===
elif scelta == "👥 Volontari":
    FILE_VOLONTARI = "anagrafica_volontari.csv"
    FILE_VOLONTARI_FULL = "anagrafica_volontari_completa.csv"
    
    st.markdown("### 👥 Anagrafica Volontari ANA - Scheda Completa")
    st.caption("Scheda professionale con tutti i dati - agganciata automaticamente a Distribuzione Radio e Mappa")
    
    tab1, tab2, tab3, tab4 = st.tabs(["➕ Nuova Anagrafica Completa", "📋 Lista Volontari", "🔍 Cerca/Modifica", "📊 Statistiche & Export"])
    
    with tab1:
        with st.container(border=True):
            st.markdown("#### 📝 Scheda Anagrafica Volontario - Tutti i campi con Foto + CF Auto")
            st.info("📷 Carica foto SOPRA il form + 🆔 Il CF si calcola da solo se lasci vuoto! Oppure vai in menu 🆔 Calcolo CF")
            
            # CALCOLO CF LIVE FUORI DAL FORM - FUNZIONA 100%
            st.markdown("#### 🆔 Calcolo Codice Fiscale RAPIDO (fuori dal form)")
            col_cf_live1, col_cf_live2, col_cf_live3 = st.columns([2,2,1])
            with col_cf_live1:
                cf_live_nome = st.text_input("Nome per CF", placeholder="Mario", key="cf_live_nome")
                cf_live_cognome = st.text_input("Cognome per CF", placeholder="Rossi", key="cf_live_cognome")
            with col_cf_live2:
                cf_live_data = st.date_input("Data Nascita per CF - GG/MM/AAAA", value=datetime(1980,1,15), key="cf_live_data", format="DD/MM/YYYY")
                st.caption(f"GG/MM/AAAA: {cf_live_data.strftime('%d/%m/%Y')}")
                cf_live_sesso = st.selectbox("Sesso per CF", ["M","F"], key="cf_live_sesso")
                cf_live_comune = st.text_input("Comune Nascita per CF", placeholder="Varese", key="cf_live_comune")
            with col_cf_live3:
                st.markdown("<br><br>", unsafe_allow_html=True)
                if st.button("🆔 CALCOLA CF", use_container_width=True, type="primary", key="btn_calc_cf_live"):
                    if cf_live_nome and cf_live_cognome and cf_live_comune:
                        cf_calc, cod_com, _ = calcola_cf(cf_live_nome, cf_live_cognome, cf_live_data, cf_live_sesso, cf_live_comune, "")
                        st.session_state.cf_calcolato = cf_calc
                        st.session_state.cf_cod_com = cod_com
                        st.success(f"CF: {cf_calc}")
                    else:
                        st.error("Compila Nome, Cognome, Comune")
            
            if "cf_calcolato" in st.session_state and st.session_state.cf_calcolato:
                st.markdown(f'<div style="background:#c8e6c9; padding:15px; border-radius:10px; text-align:center; border:2px solid #2e7d32;"><h3 style="color:#1b5e20;">CF CALCOLATO: {st.session_state.cf_calcolato}</h3><p>Comune cod: {st.session_state.get("cf_cod_com","")} - Verrà inserito automaticamente nel form sotto</p></div>', unsafe_allow_html=True)
                if st.button("❌ Pulisci CF calcolato", key="clear_cf_live"):
                    del st.session_state.cf_calcolato
                    st.rerun()

            
            # Carica comuni per residenza
            lista_comuni_anag = get_comuni_italiani()
            
            # FOTO FUORI DAL FORM per evitare bug Streamlit
            st.markdown("##### 📷 Foto Volontario")
            foto_v_file = st.file_uploader("📷 Allega Foto Volontario (JPG/PNG) - Verrà visualizzata nella scheda", type=["jpg","jpeg","png"], key="foto_upload_global")
            if "foto_base64_temp" not in st.session_state:
                st.session_state.foto_base64_temp = ""
                st.session_state.foto_nome_temp = ""
            
            if foto_v_file is not None:
                import base64
                bytes_data = foto_v_file.getvalue()
                st.session_state.foto_base64_temp = base64.b64encode(bytes_data).decode()
                st.session_state.foto_nome_temp = foto_v_file.name
                st.image(bytes_data, width=150, caption=f"Anteprima: {foto_v_file.name}")
                st.success(f"✅ Foto {foto_v_file.name} pronta - {len(bytes_data)} bytes")
            else:
                if st.session_state.foto_base64_temp:
                    try:
                        import base64
                        img_bytes = base64.b64decode(st.session_state.foto_base64_temp)
                        st.image(img_bytes, width=150, caption=f"Foto in memoria: {st.session_state.foto_nome_temp}")
                    except:
                        pass
            
            with st.form("form_volontari_completa", clear_on_submit=False):
                st.markdown("##### 👤 Dati Personali")
                c1,c2,c3,c4 = st.columns(4)
                with c1:
                    nome_v = st.text_input("Nome *", placeholder="Mario")
                    cognome_v = st.text_input("Cognome *", placeholder="Rossi")
                    sesso_v = st.selectbox("Sesso", ["M", "F", "Altro"])
                with c2:
                    data_nascita_v = st.date_input("Data Nascita - Giorno/Mese/Anno", value=datetime(1980,1,15), min_value=datetime(1930,1,1), max_value=datetime(2010,12,31), format="DD/MM/YYYY")
                    st.caption(f"📅 Selezionato: {data_nascita_v.strftime('%d/%m/%Y')} - Giorno: {data_nascita_v.day} Mese: {data_nascita_v.month} Anno: {data_nascita_v.year}")
                    st.markdown("**🔍 TUTTI i comuni Italia - cerca qui**")
                    filtro_nasc = st.text_input("Scrivi 2+ lettere per cercare comune nascita (es: var, mil, rom)", placeholder="var...", key="filtro_nascita_all")
                    if filtro_nasc and len(filtro_nasc)>=2:
                        lista_filt = [c for c in lista_comuni_anag if filtro_nasc.lower() in c.lower()][:150]
                        st.caption(f"Trovati {len(lista_filt)} comuni")
                        luogo_nascita_v = st.selectbox(f"Comune - {len(lista_filt)} risultati", ["--"] + lista_filt, key="luogo_nascita_filt")
                    else:
                        luogo_nascita_v = st.selectbox("Luogo Nascita (primi 200, usa filtro sopra per tutti i 7900)", ["--"] + lista_comuni_anag[:200], key="luogo_nascita")
                    luogo_nascita_manual = st.text_input("Oppure scrivi luogo nascita", placeholder="Varese")
                with c3:
                    cf_v = st.text_input("Codice Fiscale *", placeholder="RSSMRA80A01L682K", help="16 caratteri", value=st.session_state.get("cf_calcolato",""), key="cf_anag_field")
                    if st.form_submit_button("🆔 CALCOLA CF AUTOMATICO", use_container_width=False):
                        st.session_state.cf_nome_temp = nome_v
                        st.session_state.cf_cognome_temp = cognome_v
                        st.session_state.cf_data_temp = data_nascita_v
                        st.session_state.cf_sesso_temp = sesso_v
                        st.session_state.cf_comune_temp = luogo_nascita_manual if luogo_nascita_manual else luogo_nascita_v
                    # Se CF calcolato da pagina CF, usalo
                    if "cf_calcolato" in st.session_state and st.session_state.cf_calcolato:
                        st.info(f"CF calcolato: {st.session_state.cf_calcolato}")
                    gruppo_sanguigno_v = st.selectbox("Gruppo Sanguigno", ["--", "0+", "0-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
                    taglia_v = st.selectbox("Taglia Vestiario", ["--", "XS", "S", "M", "L", "XL", "XXL", "XXXL"])
                with c4:
                    stato_civile_v = st.selectbox("Stato Civile", ["--", "Celibe/Nubile", "Coniugato/a", "Divorziato/a", "Vedovo/a"])
                    foto_v = st.text_input("Foto (nome file)", placeholder="mario_rossi.jpg")
                
                st.divider()
                st.markdown("##### 🏠 Residenza - con Combo Comuni + Via + Civico")
                c1,c2,c3,c4 = st.columns([2,2,1,1])
                with c1:
                    comune_res_v = st.selectbox("Comune Residenza *", ["-- Seleziona --"] + lista_comuni_anag, key="comune_res")
                    # Filtro rapido
                    filtro_comune_res = st.text_input("Filtro comune", placeholder="Varese...", key="filtro_comune_res")
                    if filtro_comune_res:
                        filt = [c for c in lista_comuni_anag if filtro_comune_res.lower() in c.lower()][:20]
                        if filt:
                            comune_res_v = st.selectbox("Risultati", ["--"] + filt, key="comune_res_filt")
                with c2:
                    via_res_v = st.text_input("Via / Piazza *", placeholder="Via Sacco")
                    if comune_res_v and comune_res_v != "-- Seleziona --":
                        if st.form_submit_button(f"📥 Carica vie di {comune_res_v.split('(')[0][:15]}", use_container_width=False):
                            # Questo non funziona in form, gestito fuori - mostra hint
                            st.info("Salva e usa mappa per cercare vie")
                with c3:
                    civico_res_v = st.text_input("Civico *", placeholder="5, 10/A")
                    cap_res_v = st.text_input("CAP", placeholder="21100")
                with c4:
                    prov_res_v = st.text_input("Prov", placeholder="VA", max_chars=2)
                    # Geocoding automatico residenza
                    lat_res_v = st.text_input("Lat (auto da rete)", placeholder="45.8205")
                    lon_res_v = st.text_input("Lon (auto)", placeholder="8.8255")
                
                st.divider()
                st.markdown("##### 📞 Contatti & Emergenza")
                c1,c2,c3,c4 = st.columns(4)
                with c1:
                    tel_v = st.text_input("Telefono Fisso", placeholder="0332 123456")
                    cell_v = st.text_input("Cellulare *", placeholder="333 1234567")
                with c2:
                    email_v = st.text_input("Email *", placeholder="mario.rossi@ana.it")
                    pec_v = st.text_input("PEC", placeholder="mario@pec.it")
                with c3:
                    contatto_emerg_v = st.text_input("Contatto Emergenza - Nome", placeholder="Maria Rossi - moglie")
                    tel_emerg_v = st.text_input("Tel Emergenza", placeholder="333 7654321")
                with c4:
                    whatsapp_v = st.checkbox("WhatsApp attivo", value=True)
                    privacy_v = st.checkbox("Privacy firmata", value=False)
                
                st.divider()
                st.markdown("##### 🎖️ Dati ANA & Servizio")
                c1,c2,c3,c4 = st.columns(4)
                with c1:
                    sezione_v = st.text_input("Sezione ANA *", value="Varese")
                    gruppo_v = st.text_input("Gruppo ANA", placeholder="Varese Centro")
                    tessera_v = st.text_input("N° Tessera ANA *", placeholder="12345")
                with c2:
                    data_iscrizione_v = st.date_input("Data Iscrizione ANA", value=datetime.now())
                    ruolo_v = st.selectbox("Ruolo *", ["Volontario", "Capo Squadra", "Coordinatore", "Responsabile Magazzino", "Autista", "Operatore Radio", "Sanitario", "Logistica", "Presidente", "Vice Presidente", "Segretario", "Tesoriere", "Consigliere"])
                    stato_servizio_v = st.selectbox("Stato Servizio", ["Attivo", "In prova", "Sospeso", "Non attivo", "Onorario"])
                with c3:
                    specializzazioni_v = st.multiselect("Specializzazioni", ["Guida fuoristrada", "Motosega", "Antincendio", "Primo Soccorso", "Protezione Civile", "Radio", "Cucina campo", "Elettricista", "Idraulico", "Meccanico", "Autista C", "Autista D", "Sub", "Alpinismo"])
                    patente_v = st.selectbox("Patente", ["--", "AM", "A1", "A2", "A", "B", "C1", "C", "D1", "D", "BE", "CE", "DE"])
                with c4:
                    scadenza_patente_v = st.date_input("Scadenza Patente", value=datetime(2030,1,1))
                    abilitazioni_v = st.text_input("Altre abilitazioni", placeholder="Muletto, PLE, ecc")
                    anni_servizio_v = st.number_input("Anni servizio", min_value=0, max_value=60, value=0)
                
                st.divider()
                st.markdown("##### 📋 Note & Disponibilità")
                c1,c2 = st.columns(2)
                with c1:
                    note_v = st.text_area("Note generali", placeholder="Allergie, patologie, disponibilità, competenze...", height=100)
                    note_mediche_v = st.text_area("Note mediche riservate", placeholder="Allergie, farmaci...", height=80)
                with c2:
                    disponibilita_v = st.multiselect("Disponibilità", ["Feriali mattina", "Feriali pomeriggio", "Weekend", "Notte", "Festivi", "Emergenze H24", "Solo su chiamata"])
                    attrezzatura_v = st.text_input("Attrezzatura personale", placeholder="Radio propria, DPI, ecc")
                    assicurazione_v = st.selectbox("Assicurazione", ["--", "ANA base", "ANA + integrativa", "Volontariato PC", "Altra"])
                
                st.divider()
                submitted = st.form_submit_button("💾 SALVA ANAGRAFICA COMPLETA", type="primary", use_container_width=True)
                
                if submitted:
                    if not nome_v or not cognome_v:
                        st.error("❌ Nome e Cognome obbligatori")
                    elif not cf_v or len(cf_v) < 10:
                        st.warning("⚠️ Codice Fiscale incompleto, salva comunque?")
                        # Procedi comunque
                        nome_completo = f"{nome_v} {cognome_v}".strip()
                        # Salva
                        # AUTO CALCOLO CF se vuoto
                        if not cf_v:
                            luogo_calc_auto = luogo_nascita_manual if luogo_nascita_manual else luogo_nascita_v
                            cf_auto, cod_auto, _ = calcola_cf(nome_v, cognome_v, data_nascita_v, sesso_v, luogo_calc_auto, "")
                            cf_v = cf_auto
                        luogo_nascita_final = luogo_nascita_manual if luogo_nascita_manual else luogo_nascita_v
                        comune_res_final = comune_res_v
                        # Crea record completo
                        record = {
                            "Nome": nome_v, "Cognome": cognome_v, "Nome e Cognome": nome_completo,
                            "Sesso": sesso_v, "Data Nascita": data_nascita_v.strftime("%d/%m/%Y"), "Data Nascita ISO": str(data_nascita_v), "Luogo Nascita": luogo_nascita_final,
                            "Codice Fiscale": cf_v.upper(), "Gruppo Sanguigno": gruppo_sanguigno_v, "Taglia": taglia_v,
                            "Comune Residenza": comune_res_v, "Via": via_res_v, "Civico": civico_res_v, "CAP": cap_res_v, "Provincia": prov_res_v,
                            "Lat": lat_res_v, "Lon": lon_res_v, "Indirizzo Completo": f"{via_res_v} {civico_res_v}, {comune_res_v}",
                            "Telefono": tel_v, "Cellulare": cell_v, "Email": email_v, "PEC": pec_v,
                            "Contatto Emergenza": contatto_emerg_v, "Tel Emergenza": tel_emerg_v,
                            "Sezione": sezione_v, "Gruppo": gruppo_v, "Tessera": tessera_v, "Data Iscrizione ANA": str(data_iscrizione_v),
                            "Ruolo": ruolo_v, "Stato Servizio": stato_servizio_v, "Specializzazioni": ", ".join(specializzazioni_v),
                            "Patente": patente_v, "Scadenza Patente": str(scadenza_patente_v), "Abilitazioni": abilitazioni_v, "Anni Servizio": anni_servizio_v,
                            "Note": note_v, "Note Mediche": note_mediche_v, "Disponibilità": ", ".join(disponibilita_v),
                            "Attrezzatura": attrezzatura_v, "Assicurazione": assicurazione_v,
                            "Foto": foto_v if "foto_v" in locals() else st.session_state.get("foto_nome_temp",""), "FotoBase64": foto_base64_v if "foto_base64_v" in locals() else st.session_state.get("foto_base64_temp",""), "Data Inserimento": str(datetime.now().date()), "Stato": "Attivo"
                        }
                        # Salva in lista rapida
                        if nome_completo not in st.session_state.mem_nomi:
                            st.session_state.mem_nomi.append(nome_completo)
                            salva_csv([{"Nome": n} for n in st.session_state.mem_nomi], FILE_NOMI)
                        # Salva anagrafica completa
                        volontari_full = []
                        if os.path.exists(FILE_VOLONTARI_FULL):
                            try:
                                volontari_full = pd.read_csv(FILE_VOLONTARI_FULL).to_dict(orient="records")
                            except:
                                pass
                        # Aggiorna o aggiungi
                        found = False
                        for v in volontari_full:
                            if v.get("Codice Fiscale") == cf_v.upper() or v.get("Nome e Cognome") == nome_completo:
                                v.update(record)
                                found = True
                        if not found:
                            volontari_full.append(record)
                        pd.DataFrame(volontari_full).to_csv(FILE_VOLONTARI_FULL, index=False)
                        # Salva anche vecchio formato per compatibilità
                        pd.DataFrame(volontari_full).to_csv(FILE_VOLONTARI, index=False)
                        st.success(f"✅ Anagrafica completa {nome_completo} salvata! CF: {cf_v} - Tessera: {tessera_v}")
                        st.balloons()
                    else:
                        nome_completo = f"{nome_v} {cognome_v}".strip()
                        luogo_nascita_final = luogo_nascita_manual if luogo_nascita_manual else luogo_nascita_v
                        record = {
                            "Nome": nome_v, "Cognome": cognome_v, "Nome e Cognome": nome_completo,
                            "Sesso": sesso_v, "Data Nascita": data_nascita_v.strftime("%d/%m/%Y"), "Data Nascita ISO": str(data_nascita_v), "Luogo Nascita": luogo_nascita_final,
                            "Codice Fiscale": cf_v.upper(), "Gruppo Sanguigno": gruppo_sanguigno_v, "Taglia": taglia_v, "Stato Civile": stato_civile_v,
                            "Comune Residenza": comune_res_v, "Via": via_res_v, "Civico": civico_res_v, "CAP": cap_res_v, "Provincia": prov_res_v,
                            "Lat": lat_res_v, "Lon": lon_res_v, "Indirizzo Completo": f"{via_res_v} {civico_res_v}, {comune_res_v}",
                            "Telefono": tel_v, "Cellulare": cell_v, "Email": email_v, "PEC": pec_v,
                            "Contatto Emergenza": contatto_emerg_v, "Tel Emergenza": tel_emerg_v, "WhatsApp": whatsapp_v, "Privacy": privacy_v,
                            "Sezione": sezione_v, "Gruppo": gruppo_v, "Tessera": tessera_v, "Data Iscrizione ANA": str(data_iscrizione_v),
                            "Ruolo": ruolo_v, "Stato Servizio": stato_servizio_v, "Specializzazioni": ", ".join(specializzazioni_v),
                            "Patente": patente_v, "Scadenza Patente": str(scadenza_patente_v), "Abilitazioni": abilitazioni_v, "Anni Servizio": anni_servizio_v,
                            "Note": note_v, "Note Mediche": note_mediche_v, "Disponibilità": ", ".join(disponibilita_v),
                            "Attrezzatura": attrezzatura_v, "Assicurazione": assicurazione_v,
                            "Foto": foto_v if "foto_v" in locals() else st.session_state.get("foto_nome_temp",""), "FotoBase64": foto_base64_v if "foto_base64_v" in locals() else st.session_state.get("foto_base64_temp",""), "Data Inserimento": str(datetime.now().date()), "Stato": "Attivo"
                        }
                        if nome_completo not in st.session_state.mem_nomi:
                            st.session_state.mem_nomi.append(nome_completo)
                            salva_csv([{"Nome": n} for n in st.session_state.mem_nomi], FILE_NOMI)
                        volontari_full = []
                        if os.path.exists(FILE_VOLONTARI_FULL):
                            try:
                                volontari_full = pd.read_csv(FILE_VOLONTARI_FULL).to_dict(orient="records")
                            except:
                                pass
                        found = False
                        for v in volontari_full:
                            if v.get("Codice Fiscale") == cf_v.upper() and cf_v.upper() != "":
                                v.update(record)
                                found = True
                            elif v.get("Nome e Cognome") == nome_completo and cf_v == "":
                                v.update(record)
                                found = True
                        if not found:
                            volontari_full.append(record)
                        pd.DataFrame(volontari_full).to_csv(FILE_VOLONTARI_FULL, index=False)
                        pd.DataFrame(volontari_full).to_csv(FILE_VOLONTARI, index=False)
                        st.success(f"✅ {nome_completo} salvato! Tessera {tessera_v} - Ruolo {ruolo_v}")
                        st.info(f"🔗 Ora disponibile in Distribuzione Radio e Mappa - CF: {cf_v.upper()}")
                        st.balloons()
    
    with tab2:
        # Lista completa
        if os.path.exists(FILE_VOLONTARI_FULL):
            try:
                df_full = pd.read_csv(FILE_VOLONTARI_FULL)
                st.markdown(f"### 📋 Anagrafica Completa - {len(df_full)} volontari")
                
                # Filtri
                c1,c2,c3,c4 = st.columns(4)
                with c1:
                    filtro_ruolo = st.selectbox("Filtra per Ruolo", ["Tutti"] + sorted(df_full["Ruolo"].dropna().unique().tolist()) if "Ruolo" in df_full.columns else ["Tutti"])
                with c2:
                    filtro_sezione = st.selectbox("Filtra per Sezione", ["Tutte"] + sorted(df_full["Sezione"].dropna().unique().tolist()) if "Sezione" in df_full.columns else ["Tutte"])
                with c3:
                    filtro_stato = st.selectbox("Filtra per Stato", ["Tutti", "Attivo", "In prova", "Sospeso", "Non attivo"])
                with c4:
                    cerca_nome = st.text_input("🔍 Cerca nome/CF", placeholder="Rossi o RSSMRA...")
                
                df_filtered = df_full.copy()
                if filtro_ruolo != "Tutti" and "Ruolo" in df_filtered.columns:
                    df_filtered = df_filtered[df_filtered["Ruolo"] == filtro_ruolo]
                if filtro_sezione != "Tutte" and "Sezione" in df_filtered.columns:
                    df_filtered = df_filtered[df_filtered["Sezione"] == filtro_sezione]
                if filtro_stato != "Tutti" and "Stato Servizio" in df_filtered.columns:
                    df_filtered = df_filtered[df_filtered["Stato Servizio"] == filtro_stato]
                if cerca_nome:
                    mask = df_filtered.astype(str).apply(lambda x: x.str.contains(cerca_nome, case=False, na=False)).any(axis=1)
                    df_filtered = df_filtered[mask]
                
                st.dataframe(df_filtered.iloc[::-1], use_container_width=True, hide_index=True, height=500)
                
                # Azioni
                c1,c2,c3,c4 = st.columns(4)
                with c1:
                    out = BytesIO()
                    df_filtered.to_excel(out, index=False, engine="openpyxl")
                    st.download_button("📥 Excel Filtrato", out.getvalue(), file_name="anagrafica_volontari_completa.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
                with c2:
                    out_csv = df_filtered.to_csv(index=False).encode('utf-8')
                    st.download_button("📥 CSV", out_csv, file_name="anagrafica_volontari.csv", mime="text/csv", use_container_width=True)
                with c3:
                    if st.button("🔄 Sincronizza nomi distribuzione", use_container_width=True):
                        nomi = df_full["Nome e Cognome"].dropna().tolist() if "Nome e Cognome" in df_full.columns else []
                        st.session_state.mem_nomi = list(dict.fromkeys(nomi + st.session_state.mem_nomi))
                        salva_csv([{"Nome": n} for n in st.session_state.mem_nomi], FILE_NOMI)
                        st.success(f"Sincronizzati {len(nomi)} volontari!")
                with c4:
                    if st.button("🗑️ Cancella Tutto", use_container_width=True, type="secondary"):
                        st.session_state["confirm_delete_vol"] = True
                if st.session_state.get("confirm_delete_vol"):
                    st.warning("⚠️ Sei sicuro? Cancellerà tutta l'anagrafica!")
                    c1,c2 = st.columns(2)
                    with c1:
                        if st.button("✅ Sì, cancella", type="primary", use_container_width=True):
                            if os.path.exists(FILE_VOLONTARI_FULL):
                                os.remove(FILE_VOLONTARI_FULL)
                            if os.path.exists(FILE_VOLONTARI):
                                os.remove(FILE_VOLONTARI)
                            st.session_state.mem_nomi = []
                            salva_csv([], FILE_NOMI)
                            st.session_state["confirm_delete_vol"] = False
                            st.rerun()
                    with c2:
                        if st.button("❌ Annulla", use_container_width=True):
                            st.session_state["confirm_delete_vol"] = False
                            st.rerun()
            except Exception as e:
                st.error(f"Errore lettura: {e}")
        else:
            st.info("Nessun volontario in anagrafica completa. Usa tab 'Nuova Anagrafica Completa'")
            if st.session_state.mem_nomi:
                st.dataframe(pd.DataFrame({"Volontari (vecchia lista)": st.session_state.mem_nomi}), use_container_width=True)
    
    # Mostra scheda dettagliata se selezionata
    if "volontario_scheda" in st.session_state and st.session_state.volontario_scheda:
        st.divider()
        st.markdown("### 👁️ Scheda Volontario Selezionato")
        row = st.session_state.volontario_scheda
        col_f, col_d = st.columns([1,2])
        with col_f:
            if row.get("FotoBase64"):
                try:
                    import base64
                    img_bytes = base64.b64decode(row["FotoBase64"])
                    st.image(img_bytes, width=250, caption=f"{row.get('Nome','')} {row.get('Cognome','')}")
                except:
                    st.info("Foto non disponibile")
            else:
                st.markdown("📷 Nessuna foto allegata")
            if st.button("❌ Chiudi Scheda"):
                st.session_state.volontario_scheda = None
                st.rerun()
        with col_d:
            st.json(row)
    
    with tab3:
        st.markdown("### 🔍 Cerca e Modifica Volontario")
        if os.path.exists(FILE_VOLONTARI_FULL):
            try:
                df_full = pd.read_csv(FILE_VOLONTARI_FULL)
                cerca_edit = st.text_input("🔍 Cerca per Nome, Cognome, CF o Tessera", placeholder="Rossi, RSSMRA80A01L682K, 12345", key="cerca_edit")
                if cerca_edit:
                    mask = df_full.astype(str).apply(lambda x: x.str.contains(cerca_edit, case=False, na=False)).any(axis=1)
                    risultati = df_full[mask]
                    if not risultati.empty:
                        st.success(f"Trovati {len(risultati)} volontari")
                        for idx, row in risultati.iterrows():
                            with st.container(border=True):
                                c1,c2,c3 = st.columns([3,1,1])
                                with c1:
                                    st.markdown(f"**{row.get('Nome e Cognome','')}** - CF: {row.get('Codice Fiscale','')} - Tessera: {row.get('Tessera','')} - Ruolo: {row.get('Ruolo','')}")
                                    st.caption(f"{row.get('Via','')} {row.get('Civico','')}, {row.get('Comune Residenza','')} - Cell: {row.get('Cellulare','')} - {row.get('Email','')}")
                                with c2:
                                    if st.button(f"✏️ Modifica", key=f"mod_{idx}"):
                                        st.session_state["edit_vol_idx"] = idx
                                        st.session_state["edit_vol_data"] = row.to_dict()
                                with c3:
                                    if st.button(f"🗑️ Elimina", key=f"del_{idx}"):
                                        df_full = df_full.drop(idx)
                                        df_full.to_csv(FILE_VOLONTARI_FULL, index=False)
                                        df_full.to_csv(FILE_VOLONTARI, index=False)
                                        # Rimuovi da mem_nomi
                                        nome_del = row.get("Nome e Cognome","")
                                        if nome_del in st.session_state.mem_nomi:
                                            st.session_state.mem_nomi.remove(nome_del)
                                            salva_csv([{"Nome": n} for n in st.session_state.mem_nomi], FILE_NOMI)
                                        st.success(f"Eliminato {nome_del}")
                                        st.rerun()
                        
                        # Form modifica
                        if "edit_vol_idx" in st.session_state:
                            st.divider()
                            st.markdown(f"#### ✏️ Modifica {st.session_state['edit_vol_data'].get('Nome e Cognome','')}")
                            edit_data = st.session_state["edit_vol_data"]
                            with st.form("form_edit_vol"):
                                c1,c2,c3 = st.columns(3)
                                with c1:
                                    edit_nome = st.text_input("Nome", value=edit_data.get("Nome",""))
                                    edit_cognome = st.text_input("Cognome", value=edit_data.get("Cognome",""))
                                    edit_cf = st.text_input("Codice Fiscale", value=edit_data.get("Codice Fiscale",""))
                                with c2:
                                    edit_cell = st.text_input("Cellulare", value=edit_data.get("Cellulare",""))
                                    edit_email = st.text_input("Email", value=edit_data.get("Email",""))
                                    edit_ruolo = st.selectbox("Ruolo", ["Volontario", "Capo Squadra", "Coordinatore", "Responsabile Magazzino", "Autista", "Operatore Radio", "Sanitario", "Logistica", "Presidente", "Segretario"], index=0)
                                with c3:
                                    edit_tessera = st.text_input("Tessera", value=edit_data.get("Tessera",""))
                                    edit_sezione = st.text_input("Sezione", value=edit_data.get("Sezione","Varese"))
                                    edit_stato = st.selectbox("Stato", ["Attivo", "In prova", "Sospeso", "Non attivo"])
                                edit_note = st.text_area("Note", value=edit_data.get("Note",""))
                                c1,c2 = st.columns(2)
                                with c1:
                                    if st.form_submit_button("💾 Salva Modifiche", type="primary", use_container_width=True):
                                        # Aggiorna
                                        df_full.at[st.session_state["edit_vol_idx"], "Nome"] = edit_nome
                                        df_full.at[st.session_state["edit_vol_idx"], "Cognome"] = edit_cognome
                                        df_full.at[st.session_state["edit_vol_idx"], "Nome e Cognome"] = f"{edit_nome} {edit_cognome}"
                                        df_full.at[st.session_state["edit_vol_idx"], "Codice Fiscale"] = edit_cf
                                        df_full.at[st.session_state["edit_vol_idx"], "Cellulare"] = edit_cell
                                        df_full.at[st.session_state["edit_vol_idx"], "Email"] = edit_email
                                        df_full.at[st.session_state["edit_vol_idx"], "Ruolo"] = edit_ruolo
                                        df_full.at[st.session_state["edit_vol_idx"], "Tessera"] = edit_tessera
                                        df_full.at[st.session_state["edit_vol_idx"], "Sezione"] = edit_sezione
                                        df_full.at[st.session_state["edit_vol_idx"], "Stato Servizio"] = edit_stato
                                        df_full.at[st.session_state["edit_vol_idx"], "Note"] = edit_note
                                        df_full.to_csv(FILE_VOLONTARI_FULL, index=False)
                                        df_full.to_csv(FILE_VOLONTARI, index=False)
                                        del st.session_state["edit_vol_idx"]
                                        del st.session_state["edit_vol_data"]
                                        st.success("Modificato!")
                                        st.rerun()
                                with c2:
                                    if st.form_submit_button("❌ Annulla", use_container_width=True):
                                        del st.session_state["edit_vol_idx"]
                                        del st.session_state["edit_vol_data"]
                                        st.rerun()
                    else:
                        st.warning("Nessun risultato")
            except Exception as e:
                st.error(f"Errore: {e}")
        else:
            st.info("Nessuna anagrafica presente")
    
    with tab4:
        st.markdown("### 📊 Statistiche & Export Avanzato")
        if os.path.exists(FILE_VOLONTARI_FULL):
            try:
                df_full = pd.read_csv(FILE_VOLONTARI_FULL)
                c1,c2,c3,c4 = st.columns(4)
                with c1:
                    st.metric("Totale Volontari", len(df_full))
                with c2:
                    attivi = len(df_full[df_full["Stato Servizio"] == "Attivo"]) if "Stato Servizio" in df_full.columns else len(df_full)
                    st.metric("Attivi", attivi)
                with c3:
                    ruoli_count = df_full["Ruolo"].nunique() if "Ruolo" in df_full.columns else 0
                    st.metric("Ruoli diversi", ruoli_count)
                with c4:
                    sezioni_count = df_full["Sezione"].nunique() if "Sezione" in df_full.columns else 0
                    st.metric("Sezioni", sezioni_count)
                
                st.divider()
                c1,c2 = st.columns(2)
                with c1:
                    if "Ruolo" in df_full.columns:
                        st.markdown("**Per Ruolo**")
                        st.bar_chart(df_full["Ruolo"].value_counts())
                with c2:
                    if "Comune Residenza" in df_full.columns:
                        st.markdown("**Per Comune Residenza (top 10)**")
                        st.bar_chart(df_full["Comune Residenza"].value_counts().head(10))
                
                st.divider()
                st.markdown("#### 📥 Export Avanzati")
                c1,c2,c3 = st.columns(3)
                with c1:
                    # Export per ruolo
                    if "Ruolo" in df_full.columns:
                        for ruolo in df_full["Ruolo"].dropna().unique():
                            df_ruolo = df_full[df_full["Ruolo"] == ruolo]
                            out = BytesIO()
                            df_ruolo.to_excel(out, index=False, engine="openpyxl")
                            st.download_button(f"📥 {ruolo} ({len(df_ruolo)})", out.getvalue(), file_name=f"volontari_{ruolo}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True, key=f"exp_{ruolo}")
                with c2:
                    # PDF Tessera
                    st.markdown("**Tessere**")
                    # Genera PDF semplice per tutti
                    if st.button("📄 Genera PDF Tessere Volontari", use_container_width=True):
                        try:
                            from fpdf import FPDF
                            pdf = FPDF(orientation='P', unit='mm', format='A4')
                            pdf.set_auto_page_break(auto=True, margin=15)
                            pdf.add_page()
                            pdf.set_font("Arial", "B", 16)
                            pdf.cell(0, 10, "ANA Varese - Tessere Volontari", ln=True, align="C")
                            pdf.ln(5)
                            for _, row in df_full.iterrows():
                                pdf.set_font("Arial", "B", 12)
                                pdf.cell(0, 8, f"{row.get('Nome e Cognome','')} - Tessera {row.get('Tessera','')} - {row.get('Ruolo','')}", ln=True)
                                pdf.set_font("Arial", "", 10)
                                pdf.cell(0, 6, f"CF: {row.get('Codice Fiscale','')} - Cell: {row.get('Cellulare','')} - {row.get('Comune Residenza','')}", ln=True)
                                pdf.ln(2)
                            # FIX PDF bytearray/str
                            out_pdf = pdf.output()
                            if isinstance(out_pdf, str):
                                out_pdf = out_pdf.encode('latin-1')
                            else:
                                out_pdf = bytes(out_pdf)
                            st.download_button("📥 Scarica PDF Tessere", out_pdf, file_name="tessere_volontari.pdf", mime="application/pdf", use_container_width=True)
                        except Exception as e:
                            st.error(f"Errore PDF: {e}")
                with c3:
                    st.markdown("**QR Code**")
                    if st.button("📱 Genera QR per ogni volontario", use_container_width=True):
                        import qrcode
                        for _, row in df_full.head(5).iterrows():
                            qr_data = f"ANA Varese - {row.get('Nome e Cognome','')} - Tessera {row.get('Tessera','')} - CF {row.get('Codice Fiscale','')}"
                            qr = qrcode.make(qr_data)
                            buf = BytesIO()
                            qr.save(buf, format="PNG")
                            st.image(buf.getvalue(), caption=row.get('Nome e Cognome',''), width=150)
            except Exception as e:
                st.error(f"Errore stats: {e}")
        else:
            st.info("Nessun dato per statistiche")

# === BROGLIACCIO - NUOVA SCHEDA RICHIESTA ===
elif scelta == "📝 Brogliaccio":
    st.markdown("### 📝 Brogliaccio Operativo - Registro Giornaliero Interventi")
    st.caption("Annota Nome e Cognome, Cell, ODV di appartenenza e attività - collegato ad anagrafica volontari")
    
    tab1_brog, tab1b_brog, tab2_brog, tab3_brog = st.tabs(["➕ Nuova Annotazione", "📻 Sottomaschera Comunicazioni", "📋 Registro Brogliaccio", "📊 Export & Stampa"])
    
    with tab1_brog:
        with st.container(border=True):
            st.markdown("#### 📝 Inserisci Annotazione Brogliaccio")
            st.info("Campi richiesti: Nome e Cognome, Cellulare, ODV di Appartenenza")
            
            with st.form("form_brogliaccio", clear_on_submit=True):
                c1,c2,c3,c4 = st.columns(4)
                with c1:
                    # Nome e Cognome da anagrafica
                    if st.session_state.mem_nomi:
                        nome_brog = st.selectbox("Nome e Cognome * (da anagrafica)", ["-- Seleziona --"] + st.session_state.mem_nomi + ["-- Nuovo --"], key="brog_nome")
                        if nome_brog == "-- Nuovo --":
                            nome_brog_new = st.text_input("Nuovo Nome e Cognome *", placeholder="Mario Rossi")
                            nome_brog_final = nome_brog_new
                        elif nome_brog == "-- Seleziona --":
                            nome_brog_final = ""
                        else:
                            nome_brog_final = nome_brog
                            # Auto recupera cell da anagrafica completa se esiste
                            if os.path.exists("anagrafica_volontari_completa.csv"):
                                try:
                                    df_anag = pd.read_csv("anagrafica_volontari_completa.csv")
                                    match = df_anag[df_anag["Nome e Cognome"] == nome_brog_final]
                                    if not match.empty:
                                        cell_auto = match.iloc[0].get("Cellulare","")
                                        st.caption(f"📱 Cell da anagrafica: {cell_auto}")
                                except:
                                    pass
                    else:
                        nome_brog_final = st.text_input("Nome e Cognome *", placeholder="Mario Rossi")
                    
                    cell_brog = st.text_input("Cell *", placeholder="333 1234567", help="Cellulare volontario")
                
                with c2:
                    odv_brog = st.selectbox("ODV di Appartenenza *", ["--", "ANA - Associazione Nazionale Alpini", "ANA - Protezione Civile", "ANA - Antincendio Boschivo", "Protezione Civile Comunale", "Protezione Civile Regionale", "Croce Rossa Italiana", "Misericordia", "ANPAS", "Altra ODV", "Volontario Singolo"], help="Organizzazione di Volontariato di appartenenza")
                    odv_dettaglio = st.text_input("Dettaglio / Sezione ODV", placeholder="Es: Sezione Varese, Gruppo AIB Varese, ecc")
                
                with c3:
                    data_brog = st.date_input("Data *", value=datetime.now())
                    ora_inizio_brog = st.text_input("Ora Inizio *", value=datetime.now().strftime("%H:%M"))
                    ora_fine_brog = st.text_input("Ora Fine", placeholder="18:00")
                
                with c4:
                    postazione_brog = st.selectbox("Postazione", ["--"] + [p.get("Postazione","") for p in st.session_state.postazioni] + ["Sede", "Magazzino", "Esterno"])
                    comune_brog = st.selectbox("Comune Intervento", ["--"] + get_comuni_italiani()[:200], key="brog_comune")
                    stato_brog = st.selectbox("Stato", ["In corso", "Completato", "Sospeso", "Annullato"])
                
                c_full1, c_full2 = st.columns(2)
                with c_full1:
                    attivita_brog = st.text_area("Attività svolta *", placeholder="Descrivi attività, intervento, note operative...", height=100)
                with c_full2:
                    note_brog = st.text_area("Note / Esito", placeholder="Esito, materiali usati, problemi riscontrati...", height=100)
                    firma_brog = st.text_input("Firma / Operatore", placeholder="Chi compila")
                
                submitted_brog = st.form_submit_button("💾 Salva nel Brogliaccio", type="primary", use_container_width=True)
                
                if submitted_brog:
                    if not nome_brog_final or not cell_brog or odv_brog == "--":
                        st.error("❌ Compila Nome e Cognome, Cell ed ODV obbligatori!")
                    else:
                        record_brog = {
                            "Data": str(data_brog),
                            "Ora Inizio": ora_inizio_brog,
                            "Ora Fine": ora_fine_brog,
                            "Nome e Cognome": nome_brog_final,
                            "Cell": cell_brog,
                            "ODV": odv_brog,
                            "Dettaglio ODV": odv_dettaglio,
                            "Postazione": postazione_brog,
                            "Comune": comune_brog,
                            "Attività": attivita_brog,
                            "Note/Esito": note_brog,
                            "Stato": stato_brog,
                            "Firma": firma_brog,
                            "Timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                        }
                        if "brogliaccio" not in st.session_state:
                            st.session_state.brogliaccio = []
                        st.session_state.brogliaccio.append(record_brog)
                        salva_csv(st.session_state.brogliaccio, FILE_BROGLIACCIO)
                        st.success(f"✅ Brogliaccio salvato: {nome_brog_final} - {odv_brog} - {cell_brog}")
                        st.balloons()
    
    with tab1b_brog:
        st.markdown("### 📻 Sottomaschera Comunicazioni Radio - Log Traffico")
        st.caption("Registra ora, giorno, mittente, messaggio, destinatario, messaggio risposta - Tracciamento comunicazioni")
        
        with st.container(border=True):
            st.markdown("#### 📡 Nuova Comunicazione Radio")
            with st.form("form_comunicazione_radio", clear_on_submit=True):
                c1,c2,c3 = st.columns(3)
                with c1:
                    giorno_com = st.date_input("Giorno *", value=datetime.now(), key="com_giorno")
                    ora_com = st.text_input("Ora *", value=datetime.now().strftime("%H:%M:%S"), placeholder="14:30:00", key="com_ora")
                    canale_com = st.selectbox("Canale Radio", ["CH 1 - Emergenza", "CH 2 - Logistica", "CH 3 - Coordinamento", "VHF 145.500", "PMR 446"], key="com_canale")
                with c2:
                    # Mittente da anagrafica
                    if st.session_state.mem_nomi:
                        mittente_com = st.selectbox("Mittente *", ["--"] + st.session_state.mem_nomi, key="com_mittente")
                    else:
                        mittente_com = st.text_input("Mittente *", placeholder="Posto 1 - Mario Rossi", key="com_mittente_manual")
                    messaggio_invio_com = st.text_area("Messaggio Inviato *", placeholder="Es: Richiesta intervento in Via Roma, situazione...", height=100, key="com_msg_invio")
                with c3:
                    # Destinatario da anagrafica o postazioni
                    opzioni_dest = ["--"] + st.session_state.mem_nomi + [p.get("Postazione","") for p in st.session_state.postazioni] + ["Centrale Operativa", "Tutti", "Sede ANA Varese"]
                    destinatario_com = st.selectbox("Destinatario *", opzioni_dest, key="com_destinatario")
                    messaggio_risp_com = st.text_area("Messaggio Ricevuto / Risposta", placeholder="Es: Ricevuto, invio squadra, OK, ecc...", height=100, key="com_msg_risp")
                
                c4,c5 = st.columns(2)
                with c4:
                    tipo_com = st.selectbox("Tipo Comunicazione", ["Chiamata", "Risposta", "Avviso", "Emergenza", "Logistica", "Controllo Radio"], key="com_tipo")
                    priorita_com = st.selectbox("Priorità", ["Normale", "Urgente", "Emergenza"], key="com_priorita")
                with c5:
                    esito_com = st.selectbox("Esito", ["Trasmesso", "Ricevuto", "Confermato", "In attesa risposta", "Non ricevuto"], key="com_esito")
                    note_com = st.text_input("Note", placeholder="Disturbi, batteria scarica, ecc", key="com_note")
                
                submitted_com = st.form_submit_button("📡 Salva Comunicazione", type="primary", use_container_width=True)
                
                if submitted_com:
                    if not mittente_com or mittente_com == "--" or not destinatario_com or destinatario_com == "--" or not messaggio_invio_com:
                        st.error("❌ Compila Mittente, Destinatario e Messaggio Inviato!")
                    else:
                        record_com = {
                            "Giorno": str(giorno_com),
                            "Ora": ora_com,
                            "Canale": canale_com,
                            "Mittente": mittente_com,
                            "Messaggio Inviato": messaggio_invio_com,
                            "Destinatario": destinatario_com,
                            "Messaggio Ricevuto/Risposta": messaggio_risp_com,
                            "Tipo": tipo_com,
                            "Priorità": priorita_com,
                            "Esito": esito_com,
                            "Note": note_com,
                            "Timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                        }
                        if "comunicazioni" not in st.session_state:
                            st.session_state.comunicazioni = []
                        st.session_state.comunicazioni.append(record_com)
                        salva_csv(st.session_state.comunicazioni, FILE_COMUNICAZIONI)
                        st.success(f"✅ Comunicazione salvata: {ora_com} - {mittente_com} → {destinatario_com}")
                        st.balloons()
        
        # Lista comunicazioni
        st.divider()
        if "comunicazioni" in st.session_state and st.session_state.comunicazioni:
            df_com = pd.DataFrame(st.session_state.comunicazioni)
            st.markdown(f"**📻 Registro Comunicazioni - {len(df_com)} messaggi**")
            
            # Filtri comunicazioni
            c1,c2,c3 = st.columns(3)
            with c1:
                filtro_giorno_com = st.date_input("Filtra per giorno", value=None, key="filtro_giorno_com")
            with c2:
                filtro_mitt = st.text_input("Cerca mittente/destinatario", placeholder="Posto 1, Mario...")
            with c3:
                filtro_canale_com = st.selectbox("Canale", ["Tutti"] + sorted(df_com["Canale"].dropna().unique().tolist()) if "Canale" in df_com.columns else ["Tutti"], key="filtro_canale_com2")
            
            df_com_filt = df_com.copy()
            if filtro_giorno_com:
                df_com_filt = df_com_filt[df_com_filt["Giorno"] == str(filtro_giorno_com)]
            if filtro_mitt:
                mask = df_com_filt.astype(str).apply(lambda x: x.str.contains(filtro_mitt, case=False, na=False)).any(axis=1)
                df_com_filt = df_com_filt[mask]
            if filtro_canale_com != "Tutti":
                df_com_filt = df_com_filt[df_com_filt["Canale"] == filtro_canale_com]
            
            st.dataframe(df_com_filt.iloc[::-1], use_container_width=True, hide_index=True, height=400)
            
            # Export comunicazioni
            c1,c2,c3 = st.columns(3)
            with c1:
                out = BytesIO()
                df_com_filt.to_excel(out, index=False, engine="openpyxl")
                st.download_button("📥 Excel Comunicazioni", out.getvalue(), file_name="comunicazioni_radio.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True, key="excel_com")
            with c2:
                if st.button("🗑️ Cancella Comunicazioni", use_container_width=True, key="del_com"):
                    st.session_state.comunicazioni = []
                    salva_csv([], FILE_COMUNICAZIONI)
                    st.rerun()
            with c3:
                if st.button("📄 PDF Traffico Radio", use_container_width=True, key="pdf_com"):
                    try:
                        from fpdf import FPDF
                        pdf = FPDF(orientation='L', unit='mm', format='A4')
                        pdf.set_auto_page_break(auto=True, margin=10)
                        pdf.add_page()
                        pdf.set_font("Arial", "B", 12)
                        pdf.cell(0, 8, f"ANA Varese - Registro Comunicazioni Radio - {datetime.now().strftime('%d/%m/%Y')}", ln=True, align="C")
                        pdf.set_font("Arial", "B", 7)
                        cols = ["Giorno", "Ora", "Mittente", "Messaggio Inviato", "Destinatario", "Messaggio Ricevuto", "Esito"]
                        w = [20, 15, 30, 60, 30, 60, 20]
                        for i, col in enumerate(cols):
                            pdf.cell(w[i], 6, col, border=1)
                        pdf.ln()
                        pdf.set_font("Arial", "", 6)
                        for _, r in df_com_filt.tail(40).iterrows():
                            pdf.cell(w[0], 5, str(r.get("Giorno",""))[:10], border=1)
                            pdf.cell(w[1], 5, str(r.get("Ora",""))[:8], border=1)
                            pdf.cell(w[2], 5, str(r.get("Mittente",""))[:15], border=1)
                            pdf.cell(w[3], 5, str(r.get("Messaggio Inviato",""))[:35], border=1)
                            pdf.cell(w[4], 5, str(r.get("Destinatario",""))[:15], border=1)
                            pdf.cell(w[5], 5, str(r.get("Messaggio Ricevuto/Risposta",""))[:35], border=1)
                            pdf.cell(w[6], 5, str(r.get("Esito",""))[:10], border=1)
                            pdf.ln()
                        out_pdf = pdf.output()
                        if isinstance(out_pdf, str):
                            out_pdf = out_pdf.encode('latin-1')
                        else:
                            out_pdf = bytes(out_pdf)
                        st.download_button("📥 Scarica PDF Comunicazioni", out_pdf, file_name="comunicazioni_radio.pdf", mime="application/pdf", use_container_width=True, key="pdf_com_dl")
                    except Exception as e:
                        st.error(f"Errore PDF: {e}")
        else:
            st.info("Nessuna comunicazione registrata. Inserisci sopra.")
    
    with tab2_brog:
        if "brogliaccio" in st.session_state and st.session_state.brogliaccio:
            df_brog = pd.DataFrame(st.session_state.brogliaccio)
            st.markdown(f"### 📋 Registro Brogliaccio - {len(df_brog)} annotazioni")
            
            # Filtri
            c1,c2,c3,c4 = st.columns(4)
            with c1:
                filtro_data = st.date_input("Filtra per data", value=None, key="filtro_data_brog")
            with c2:
                filtro_odv = st.selectbox("Filtra ODV", ["Tutti"] + sorted(df_brog["ODV"].dropna().unique().tolist()) if "ODV" in df_brog.columns else ["Tutti"])
            with c3:
                filtro_nome_brog = st.text_input("Cerca Nome/Cell", placeholder="Rossi, 333...")
            with c4:
                filtro_stato_brog = st.selectbox("Stato", ["Tutti", "In corso", "Completato", "Sospeso"])
            
            df_filt = df_brog.copy()
            if filtro_data:
                df_filt = df_filt[df_filt["Data"] == str(filtro_data)]
            if filtro_odv != "Tutti":
                df_filt = df_filt[df_filt["ODV"] == filtro_odv]
            if filtro_nome_brog:
                mask = df_filt.astype(str).apply(lambda x: x.str.contains(filtro_nome_brog, case=False, na=False)).any(axis=1)
                df_filt = df_filt[mask]
            if filtro_stato_brog != "Tutti":
                df_filt = df_filt[df_filt["Stato"] == filtro_stato_brog]
            
            st.dataframe(df_filt.iloc[::-1], use_container_width=True, hide_index=True, height=500)
            
            # Azioni su riga
            st.markdown("#### ✏️ Modifica / Elimina")
            for idx, row in df_filt.tail(10).iloc[::-1].iterrows():
                with st.container(border=True):
                    c1,c2,c3 = st.columns([4,1,1])
                    with c1:
                        st.markdown(f"**{row.get('Data','')} {row.get('Ora Inizio','')}** - **{row.get('Nome e Cognome','')}** - 📱 {row.get('Cell','')} - **{row.get('ODV','')}** - {row.get('Postazione','')}")
                        st.caption(f"{row.get('Attività','')[:100]}...")
                    with c2:
                        if st.button(f"🗑️ Elimina", key=f"del_brog_{idx}"):
                            st.session_state.brogliaccio = [r for i,r in enumerate(st.session_state.brogliaccio) if i != idx]
                            salva_csv(st.session_state.brogliaccio, FILE_BROGLIACCIO)
                            st.rerun()
                    with c3:
                        st.caption(row.get('Stato',''))
        else:
            st.info("Nessuna annotazione nel brogliaccio. Usa tab 'Nuova Annotazione'")
    
    with tab3_brog:
        if "brogliaccio" in st.session_state and st.session_state.brogliaccio:
            df_brog = pd.DataFrame(st.session_state.brogliaccio)
            st.markdown("### 📊 Export & Stampa Brogliaccio")
            c1,c2,c3 = st.columns(3)
            with c1:
                out = BytesIO()
                df_brog.to_excel(out, index=False, engine="openpyxl")
                st.download_button("📥 Excel Brogliaccio", out.getvalue(), file_name="brogliaccio.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
            with c2:
                out_csv = df_brog.to_csv(index=False).encode('utf-8')
                st.download_button("📥 CSV Brogliaccio", out_csv, file_name="brogliaccio.csv", mime="text/csv", use_container_width=True)
            with c3:
                if st.button("📄 Genera PDF Brogliaccio Giornaliero", use_container_width=True):
                    try:
                        from fpdf import FPDF
                        pdf = FPDF(orientation='L', unit='mm', format='A4')
                        pdf.set_auto_page_break(auto=True, margin=15)
                        pdf.add_page()
                        pdf.set_font("Arial", "B", 14)
                        pdf.cell(0, 10, f"ANA Varese - Brogliaccio Operativo - {datetime.now().strftime('%d/%m/%Y')}", ln=True, align="C")
                        pdf.set_font("Arial", "", 8)
                        pdf.ln(3)
                        pdf.set_font("Arial", "B", 7)
                        cols = ["Data", "Ora", "Nome e Cognome", "Cell", "ODV", "Postazione", "Attivita", "Stato"]
                        w = [20, 15, 35, 25, 30, 25, 70, 20]
                        for i, col in enumerate(cols):
                            pdf.cell(w[i], 6, col, border=1)
                        pdf.ln()
                        pdf.set_font("Arial", "", 7)
                        for _, r in df_brog.tail(30).iterrows():
                            pdf.cell(w[0], 5, str(r.get("Data",""))[:10], border=1)
                            pdf.cell(w[1], 5, str(r.get("Ora Inizio",""))[:5], border=1)
                            pdf.cell(w[2], 5, str(r.get("Nome e Cognome",""))[:18], border=1)
                            pdf.cell(w[3], 5, str(r.get("Cell",""))[:13], border=1)
                            pdf.cell(w[4], 5, str(r.get("ODV",""))[:15], border=1)
                            pdf.cell(w[5], 5, str(r.get("Postazione",""))[:12], border=1)
                            pdf.cell(w[6], 5, str(r.get("Attività",""))[:35], border=1)
                            pdf.cell(w[7], 5, str(r.get("Stato",""))[:10], border=1)
                            pdf.ln()
                        out_pdf = pdf.output()
                        if isinstance(out_pdf, str):
                            out_pdf = out_pdf.encode('latin-1')
                        else:
                            out_pdf = bytes(out_pdf)
                        st.download_button("📥 Scarica PDF", out_pdf, file_name=f"brogliaccio_{datetime.now().strftime('%Y%m%d')}.pdf", mime="application/pdf", use_container_width=True)
                    except Exception as e:
                        st.error(f"Errore PDF: {e}")
            
            # Statistiche
            st.divider()
            c1,c2,c3 = st.columns(3)
            with c1:
                st.metric("Totale Annotazioni", len(df_brog))
            with c2:
                if "ODV" in df_brog.columns:
                    st.markdown("**Per ODV**")
                    st.bar_chart(df_brog["ODV"].value_counts())
            with c3:
                if "Nome e Cognome" in df_brog.columns:
                    st.markdown("**Top Volontari**")
                    st.bar_chart(df_brog["Nome e Cognome"].value_counts().head(5))
        else:
            st.info("Nessun dato per export")

# === DB RADIO ===
elif scelta == "📻 DB Radio Inventario":
    with st.container(border=True):
        st.markdown("#### 📻 Database Radio - Inventario")
        with st.form("form_radio_db"):
            c1,c2,c3,c4 = st.columns(4)
            with c1:
                radio_id_db = st.text_input("Radio ID *", placeholder="R-01")
                modello_db = st.selectbox("Modello *", ["Baofeng UV-5R", "Motorola T82", "Midland G9", "Altro"])
            with c2:
                seriale = st.text_input("Seriale")
                frequenza = st.text_input("Frequenza", placeholder="145.500 MHz")
            with c3:
                batteria = st.selectbox("Batteria", ["Carica", "Da caricare", "Guasta", "Nuova"])
                accessori = st.text_input("Accessori")
            with c4:
                stato_radio_db = st.selectbox("Stato", ["Disponibile", "In uso", "Guasta", "In riparazione"])
                note_radio_db = st.text_input("Note")
            if st.form_submit_button("💾 Salva Radio nel DB", use_container_width=True, type="primary"):
                if radio_id_db and modello_db:
                    if any(r.get("Radio ID")==radio_id_db for r in st.session_state.radio_db):
                        st.error(f"Radio {radio_id_db} già esistente!")
                    else:
                        st.session_state.radio_db.append({
                            "Radio ID": radio_id_db, "Modello": modello_db, "Seriale": seriale,
                            "Frequenza": frequenza, "Batteria": batteria, "Accessori": accessori,
                            "Stato": stato_radio_db, "Note": note_radio_db, "Data Inserimento": str(datetime.now().date())
                        })
                        salva_csv(st.session_state.radio_db, FILE_RADIO_DB)
                        st.success(f"Radio {radio_id_db} aggiunta!")
                        st.rerun()
                else:
                    st.error("Radio ID e Modello obbligatori")
        if st.session_state.radio_db:
            df_db = pd.DataFrame(st.session_state.radio_db).iloc[::-1]
            st.dataframe(df_db, use_container_width=True, hide_index=True)
            col1,col2 = st.columns(2)
            with col1:
                out = BytesIO()
                df_db.to_excel(out, index=False, engine="openpyxl")
                st.download_button("📥 Excel DB Radio", out.getvalue(), file_name="db_radio.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
            with col2:
                if st.button("🗑️ Cancella DB", use_container_width=True):
                    st.session_state.radio_db = []
                    salva_csv([], FILE_RADIO_DB)
                    st.rerun()

# === DISTRIBUZIONE ===
elif scelta == "📦 Distribuzione Radio":
    with st.container(border=True):
        st.markdown("#### 📦 Distribuzione Radio - Collegata ad Anagrafica Volontari")
        st.caption(f"📋 Volontari disponibili: {len(st.session_state.mem_nomi)} - Agganciati automaticamente dalla scheda Volontari | Se non vedi un nome, vai in 👥 Volontari e aggiungilo")
        if not st.session_state.mem_nomi:
            st.warning("⚠️ Nessun volontario in anagrafica! Vai in 👥 Volontari per aggiungerli prima di distribuire le radio")
        with st.form("form_dist"):
            c1,c2,c3,c4 = st.columns(4)
            with c1:
                data_d = st.date_input("Data", value=datetime.now())
                if st.session_state.radio_db:
                    st.markdown("**📻 Agganciato a DB Radio Inventario**")
                    # Crea lista con info complete - FIX AGGANCIO MODELLO
                    radio_list = []
                    display_to_data = {}
                    for r in st.session_state.radio_db:
                        rid = str(r.get("Radio ID","")).strip()
                        if rid:
                            mod = str(r.get("Modello","")).strip() or "N/D"
                            stato = str(r.get("Stato","")).strip() or "Disponibile"
                            batt = str(r.get("Batteria","")).strip() or "N/D"
                            icon = "🟢" if stato=="Disponibile" else "🔴" if stato in ["Guasta","In riparazione"] else "🟡"
                            display = f"{icon} {rid} | {mod} | {stato} | Batt:{batt}"
                            radio_list.append({"id": rid, "modello": mod, "stato": stato, "batteria": batt, "full": r, "display": display})
                            display_to_data[display] = {"id": rid, "modello": mod, "full": r}
                    
                    # Opzioni con stato
                    opzioni_display = ["-- Seleziona Radio dal DB --"] + [rl["display"] for rl in radio_list]
                    
                    scelta_display = st.selectbox("Radio ID dal DB Inventario *", opzioni_display, key="radio_db_linked")
                    
                    # Inizializza variabili
                    radio_id = ""
                    modello = ""
                    radio_selezionata_full = None
                    
                    if scelta_display == "-- Seleziona Radio dal DB --":
                        st.warning("⚠️ Seleziona una radio dall'inventario")
                    else:
                        # FIX: Usa dizionario mapping invece di split
                        data_sel = display_to_data.get(scelta_display)
                        if data_sel:
                            radio_id = data_sel["id"]
                            modello = data_sel["modello"]
                            radio_selezionata_full = data_sel["full"]
                            st.success(f"✅ **{radio_id}**")
                            st.info(f"📻 Modello: **{modello}** | Stato: {radio_selezionata_full.get('Stato','')} | Batt: {radio_selezionata_full.get('Batteria','')}")
                            if radio_selezionata_full.get("Stato") != "Disponibile":
                                st.warning(f"⚠️ Radio in stato {radio_selezionata_full.get('Stato','')}")
                        else:
                            st.error("Errore parsing radio")
                    
                    # Campo modello BLOCCATO ma con valore agganciato - FIX VISUALIZZAZIONE
                    if modello:
                        st.text_input("Modello (agganciato da DB) *", value=modello, disabled=True, key="modello_locked_ok")
                        st.caption(f"🔗 Modello agganciato automaticamente da DB: {modello}")
                    else:
                        st.text_input("Modello (seleziona radio dal DB)", value="", disabled=True, placeholder="Seleziona radio sopra", key="modello_locked_empty")
                    
                    # Salva in session per uso dopo submit
                    st.session_state["_tmp_radio_id"] = radio_id
                    st.session_state["_tmp_modello"] = modello
                    st.session_state["_tmp_radio_full"] = radio_selezionata_full
                    
                else:
                    st.error("⚠️ DB Radio vuoto! Vai in 📻 DB Radio Inventario e inserisci le radio")
                    radio_id = st.text_input("Radio ID * (manuale - DB vuoto)", placeholder="R-01", key="radio_manual_id")
                    modello = st.text_input("Modello *", placeholder="Baofeng UV-5R", key="radio_manual_modello")
                    st.session_state["_tmp_radio_id"] = radio_id
                    st.session_state["_tmp_modello"] = modello
            with c2:
                assegnatario = combo_memoria("Assegnato A *", st.session_state.mem_nomi, "asseg", "Chi riceve")
                consegnato_da = combo_memoria("Consegnata DA *", st.session_state.mem_nomi, "cons_da", "Chi consegna")
            with c3:
                opzioni_post = ["-- Nuova --"] + [p.get("Postazione","") for p in st.session_state.postazioni]
                scelta_post = st.selectbox("Postazione *", opzioni_post)
                if scelta_post == "-- Nuova --":
                    postazione = st.text_input("Nuova Postazione *", placeholder="Posto 1")
                else:
                    postazione = scelta_post
                canale = st.selectbox("Canale", ["CH 1 - Emergenza", "CH 2 - Logistica", "CH 3 - Coordinamento", "VHF 145.500"])
            with c4:
                ora_cons = st.text_input("Ora consegna", value=datetime.now().strftime("%H:%M"))
                ora_ric = st.text_input("Ora riconsegna", placeholder="Al rientro")
                stato_r = st.selectbox("Stato", ["Consegnata", "Riconsegnata", "Guasta"])
            note_d = st.text_input("Note", placeholder="Con batteria carica")
            if st.form_submit_button("📦 Assegna Radio", use_container_width=True, type="primary"):
                # FIX: Recupera da session tmp per aggancio modello sicuro
                radio_id_final = st.session_state.get("_tmp_radio_id", "") or radio_id if 'radio_id' in locals() else st.session_state.get("_tmp_radio_id", "")
                modello_final = st.session_state.get("_tmp_modello", "") or modello if 'modello' in locals() else st.session_state.get("_tmp_modello", "")
                
                # Se ancora vuoto, prova a recuperare da display
                if not modello_final and st.session_state.radio_db:
                    # Ultimo tentativo: cerca modello da radio_id
                    for r in st.session_state.radio_db:
                        if str(r.get("Radio ID","")).strip() == str(radio_id_final).strip():
                            modello_final = str(r.get("Modello",""))
                            break
                
                if radio_id_final and radio_id_final != "" and assegnatario and postazione and consegnato_da and modello_final:
                    st.session_state.dist_radio.append({
                        "Data": str(data_d), "RadioID": radio_id, "Modello": modello,
                        "Assegnatario": assegnatario, "Consegnata DA": consegnato_da,
                        "Postazione": postazione, "Canale": canale,
                        "OraConsegna": ora_cons, "OraRiconsegna": ora_ric, "Stato": stato_r, "Note": note_d
                    })
                    salva_csv(st.session_state.dist_radio, FILE_DIST_RADIO)
                    st.success(f"Radio {radio_id} consegnata da {consegnato_da} a {assegnatario} in {postazione}")
                    st.rerun()
                else:
                    st.error("Compila Radio ID, Assegnato A, Consegnata DA e Postazione")
        if st.session_state.dist_radio:
            df_dist = pd.DataFrame(st.session_state.dist_radio).iloc[::-1]
            st.markdown("### 🗺️ Vai alle Coordinate - Clicca postazione per navigare")
            
            # Crea mappa nome postazione -> coordinate da DB postazioni
            mappa_coord = {}
            for p in st.session_state.postazioni:
                nome_p = p.get("Postazione","")
                if nome_p:
                    mappa_coord[nome_p] = p
            
            # Mostra cards per ogni distribuzione con pulsanti funzionanti
            for idx, row in df_dist.head(15).iterrows():
                post_nome = str(row.get("Postazione","")).strip()
                radio_id = str(row.get("RadioID",""))
                assegn = str(row.get("Assegnatario",""))
                coord_info = mappa_coord.get(post_nome)
                
                with st.container(border=True):
                    c1,c2,c3,c4,c5 = st.columns([2,2,2,2,2])
                    with c1:
                        st.markdown(f"**📍 {post_nome}**")
                        st.caption(f"Radio: {radio_id} | A: {assegn[:15]}")
                    with c2:
                        if coord_info:
                            try:
                                lat_c = coord_info.get("Latitudine","")
                                lon_c = coord_info.get("Longitudine","")
                                comune_c = coord_info.get("Comune","")
                                via_c = coord_info.get("Via","")
                                st.caption(f"📌 {comune_c} - {via_c} {coord_info.get('Civico','')}")
                                st.caption(f"Lat: {lat_c} Lon: {lon_c}")
                                # Test link rapido
                                st.caption(f"[Test Maps](https://www.google.com/maps/search/?api=1&query={lat_c},{lon_c})")
                            except:
                                st.caption("Coordinate presenti")
                        else:
                            st.warning(f"⚠️ {post_nome} non in mappa")
                    with c3:
                        if coord_info:
                            try:
                                lat_c = coord_info.get("Latitudine")
                                lon_c = coord_info.get("Longitudine")
                                # Link diretti che FUNZIONANO
                                # Link Google Maps con marker visibile
                                st.link_button(f"📱 Google Maps", f"https://www.google.com/maps/search/?api=1&query={lat_c},{lon_c}", use_container_width=True)
                            except:
                                st.caption("No coord")
                        else:
                            if st.button(f"➕ Aggiungi {post_nome} in mappa", key=f"add_map_{idx}", use_container_width=True):
                                st.session_state.current_page = "🗺️ Mappa Postazioni"
                                st.session_state.current_page = "🗺️ Mappa Postazioni"
                                # Non settiamo menu_radio direttamente per evitare errore widget
                                st.rerun()
                    with c4:
                        if coord_info:
                            try:
                                lat_c = coord_info.get("Latitudine")
                                lon_c = coord_info.get("Longitudine")
                                # Waze con nome postazione
                                st.link_button(f"🚗 Waze", f"https://waze.com/ul?ll={lat_c},{lon_c}&navigate=yes&zoom=17", use_container_width=True)
                            except:
                                pass
                    with c5:
                        if st.button(f"🗺️ VAI ALLA MAPPA", key=f"goto_map_{idx}_{post_nome}", use_container_width=True, type="primary"):
                            st.session_state.selected_postazione = post_nome
                            st.session_state.current_page = "🗺️ Mappa Postazioni"
                            st.session_state.geo_lat = coord_info.get("Latitudine","") if coord_info else ""
                            st.session_state.geo_lon = coord_info.get("Longitudine","") if coord_info else ""
                            st.rerun()
            
            st.divider()
            st.dataframe(df_dist, use_container_width=True, hide_index=True)
            out = BytesIO()
            df_dist.to_excel(out, index=False, engine="openpyxl")
            st.download_button("📥 Excel Distribuzione", out.getvalue(), file_name="distribuzione.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)

# === MAPPA ===
elif scelta == "🗺️ Mappa Postazioni":
    with st.container(border=True):
        st.markdown("#### 🗺️ Mappa Postazioni FULLSCREEN")
        if st.session_state.get("selected_postazione"):
            st.success(f"📍 Evidenziata: **{st.session_state.selected_postazione}**")
        with st.expander("➕ Aggiungi Postazione con COMBO Comuni d'Italia + Vie associate (da rete)", expanded=True):
            st.markdown("##### 🌍 COMBO con tutti i Comuni d'Italia + Vie agganciate da rete OSM")
            
            # Carica comuni italiani
            with st.spinner("🌍 Carico comuni italiani da rete..."):
                lista_comuni = get_comuni_italiani()
            
            st.caption(f"📋 {len(lista_comuni)} comuni italiani disponibili - Seleziona comune, poi carica vie")
            
            c_com1, c_com2, c_com3, c_com4 = st.columns([2,2,1,1])
            with c_com1:
                comune_input = st.selectbox("🏘️ Comune * (combo tutti Italia)", ["-- Seleziona Comune --"] + lista_comuni, key="comune_combo", help="Tutti i comuni italiani da ISTAT + rete")
                comune_filtro = st.text_input("🔍 Filtro rapido comune", placeholder="Scrivi Varese, Milano...", key="filtro_comune")
                if comune_filtro:
                    filtrati = [c for c in lista_comuni if comune_filtro.lower() in c.lower()][:50]
                    if filtrati:
                        comune_filtrato_sel = st.selectbox("Risultati filtro", ["--"] + filtrati, key="comune_filtro_sel")
                        if comune_filtrato_sel != "--":
                            comune_input = comune_filtrato_sel
                            st.info(f"✅ Comune filtrato selezionato: {comune_input}")
            
            with c_com2:
                # Vie associate al comune selezionato
                if comune_input and comune_input != "-- Seleziona Comune --":
                    if st.button(f"📥 Carica vie di {comune_input.split('(')[0].strip()}", use_container_width=True, key="carica_vie_btn"):
                        with st.spinner(f"🌐 Cerco vie di {comune_input} da rete OSM (Overpass)..."):
                            vie_trovate = get_vie_comune(comune_input)
                            st.session_state.vie_comune = vie_trovate
                            if vie_trovate:
                                st.success(f"✅ Trovate {len(vie_trovate)} vie!")
                            else:
                                st.warning("⚠️ Nessuna via trovata, puoi inserire manuale")
                    
                    if "vie_comune" in st.session_state and st.session_state.vie_comune:
                        vie_opzioni = ["-- Seleziona Via --", "-- Inserisci manuale --"] + st.session_state.vie_comune[:300]
                        via_selezionata_combo = st.selectbox(f"🛣️ Vie di {comune_input.split('(')[0].strip()} ({len(st.session_state.vie_comune)} trovate)", vie_opzioni, key="via_combo")
                        if via_selezionata_combo == "-- Inserisci manuale --":
                            via_input = st.text_input("Via manuale *", placeholder="Via Sacco", key="via_manuale")
                        elif via_selezionata_combo == "-- Seleziona Via --":
                            via_input = st.text_input("Via *", placeholder="Via Sacco", key="via_input_combo")
                        else:
                            via_input = via_selezionata_combo
                            st.caption(f"Selezionata: {via_input}")
                    else:
                        via_input = st.text_input("🛣️ Via *", placeholder="Via Sacco - oppure carica vie", key="via_input")
                        st.caption("💡 Clicca 'Carica vie' per vedere vie del comune")
                else:
                    via_input = st.text_input("🛣️ Via *", placeholder="Seleziona prima comune", key="via_input_no_comune")
                    st.info("👆 Seleziona comune")
            
            with c_com3:
                civico_input = st.text_input("🏠 Civico *", placeholder="Es: 5, 10/A, 23", key="civico_input", help="Numero civico della via")
                st.caption("Es: 5, 12, 10/A, SNC")
            
            with c_com4:
                st.markdown("<br>", unsafe_allow_html=True)
                cerca_coord = st.button("🔍 Cerca coordinate", use_container_width=True, type="primary", key="cerca_coord_btn", help="Cerca con Comune + Via + Civico da rete")
            
            # Risultato geocoding in session
            if "geo_lat" not in st.session_state:
                st.session_state.geo_lat = ""
                st.session_state.geo_lon = ""
                st.session_state.geo_display = ""
            
            # Recupera civico da session se esiste
            civico_val = st.session_state.get("civico_input", "")
            
            if cerca_coord:
                if comune_input and comune_input != "-- Seleziona Comune --" and via_input:
                    with st.spinner(f"🌐 Cerco {via_input} {civico_val}, {comune_input} su rete OSM/Photon..."):
                        lat_found, lon_found, display = geocode_comune_via(comune_input, via_input, civico_val)
                        if lat_found and lon_found:
                            st.session_state.geo_lat = lat_found
                            st.session_state.geo_lon = lon_found
                            st.session_state.geo_display = display
                            st.success(f"✅ Trovato: {display}")
                            st.success(f"📍 Lat: {lat_found} | Lon: {lon_found}")
                        else:
                            st.error(f"❌ {display}")
                else:
                    st.error("Seleziona Comune e Via")
            
            if st.session_state.geo_display:
                st.info(f"📍 Risultato rete: **{st.session_state.geo_display}** | Lat: {st.session_state.geo_lat} | Lon: {st.session_state.geo_lon}")
            
            st.divider()
            with st.form("form_post"):
                c1,c2,c3 = st.columns(3)
                with c1:
                    nome_post = st.text_input("Nome Postazione *", placeholder="Posto 1 - Ingresso")
                    lat_default = st.session_state.geo_lat if st.session_state.geo_lat else ""
                    lon_default = st.session_state.geo_lon if st.session_state.geo_lon else ""
                    lat = st.text_input("Latitudine *", value=lat_default, placeholder="45.8205")
                    lon = st.text_input("Longitudine *", value=lon_default, placeholder="8.8255")
                    comune_save = st.text_input("Comune (salvato)", value=comune_input if comune_input != "-- Seleziona Comune --" else "", placeholder="Varese")
                    via_save = st.text_input("Via (salvata)", value=via_input, placeholder="Via Sacco")
                    civico_save_form = st.text_input("Civico (salvato)", value=st.session_state.get("civico_input",""), placeholder="5")
                with c2:
                    resp_post = combo_memoria("Responsabile", st.session_state.mem_nomi, "resp_post", "Nome")
                    radio_post = st.text_input("Radio assegnata", placeholder="R-01")
                with c3:
                    tipo_post = st.selectbox("Tipo", ["Controllo accessi", "Viabilita", "Sicurezza", "Logistica", "COC", "Altro"])
                    note_post = st.text_input("Note")
                if st.form_submit_button("📍 Aggiungi alla Mappa", use_container_width=True, type="primary"):
                    if nome_post and lat and lon:
                        try:
                            float(lat); float(lon)
                            civico_save = civico_save_form if 'civico_save_form' in locals() else st.session_state.get("civico_input","")
                            st.session_state.postazioni.append({
                                "Data": str(datetime.now().date()), "Postazione": nome_post,
                                "Comune": comune_save, "Via": via_save, "Civico": civico_save,
                                "Latitudine": lat, "Longitudine": lon,
                                "Responsabile": resp_post, "Radio": radio_post,
                                "Tipo": tipo_post, "Note": note_post,
                                "Indirizzo Completo": st.session_state.geo_display,
                                "Indirizzo": f"{via_save} {civico_save}, {comune_save}".strip()
                            })
                            # Reset geo dopo salvataggio
                            st.session_state.geo_lat = ""
                            st.session_state.geo_lon = ""
                            st.session_state.geo_display = ""
                            salva_csv(st.session_state.postazioni, FILE_POSTAZIONI)
                            st.success(f"{nome_post} aggiunta!")
                            st.rerun()
                        except:
                            st.error("Lat/Lon numeri")
        if st.session_state.postazioni:
            df_post = pd.DataFrame(st.session_state.postazioni)
            if "map_type" not in st.session_state:
                st.session_state.map_type = "OpenStreetMap"
            map_type = st.selectbox("🗺️ Tipo Mappa:", ["OpenStreetMap", "Google Stradale", "Google Satellite", "Google Ibrida", "Google Rilievo"], index=["OpenStreetMap", "Google Stradale", "Google Satellite", "Google Ibrida", "Google Rilievo"].index(st.session_state.map_type))
            st.session_state.map_type = map_type
            
            # Pulsanti navigazione se selezionata
            if st.session_state.get("selected_postazione"):
                for _, r in df_post.iterrows():
                    if r.get("Postazione") == st.session_state.selected_postazione:
                        try:
                            lat_s = r.get("Latitudine"); lon_s = r.get("Longitudine")
                            st.markdown(f"**🧭 Naviga verso: {st.session_state.selected_postazione}** - {lat_s},{lon_s}")
                            c1,c2,c3,c4 = st.columns(4)
                            with c1:
                                # Questo link MOSTRA la postazione con marker rosso
                                st.link_button("📍 Vedi Postazione Google", f"https://www.google.com/maps/search/?api=1&query={lat_s},{lon_s}", use_container_width=True, type="primary")
                            with c2:
                                st.link_button("🧭 Naviga Google", f"https://www.google.com/maps/dir/?api=1&destination={lat_s},{lon_s}", use_container_width=True)
                            with c3:
                                st.link_button("🚗 Waze", f"https://waze.com/ul?ll={lat_s},{lon_s}&navigate=yes&zoom=17", use_container_width=True)
                            with c4:
                                st.link_button("🗺️ OSM", f"https://www.openstreetmap.org/?mlat={lat_s}&mlon={lon_s}#map=18/{lat_s}/{lon_s}", use_container_width=True)
                        except:
                            pass
            
            st.markdown("**🔗 Clicca postazione per centrare:**")
            cols_map = st.columns(3)
            for idx, p in enumerate(st.session_state.postazioni):
                with cols_map[idx % 3]:
                    nome = p.get("Postazione","")
                    is_sel = st.session_state.get("selected_postazione") == nome
                    if st.button(f"{'✅ ' if is_sel else '📍 '}{nome}", key=f"map_sel_{idx}", use_container_width=True, type="primary" if is_sel else "secondary"):
                        st.session_state.selected_postazione = nome
                        st.rerun()
            
            try:
                import folium
                from streamlit_folium import st_folium
                selected = st.session_state.get("selected_postazione")
                center_lat, center_lon = 45.8205, 8.8255
                zoom = 14
                if selected:
                    for _, r in df_post.iterrows():
                        if r.get("Postazione") == selected:
                            try:
                                center_lat = float(r.get("Latitudine")); center_lon = float(r.get("Longitudine")); zoom = 17
                            except:
                                pass
                if map_type == "OpenStreetMap":
                    m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom, tiles="OpenStreetMap")
                elif map_type == "Google Stradale":
                    m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom, tiles=None)
                    folium.TileLayer('https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}', attr='Google', name='Google Stradale', max_zoom=20).add_to(m)
                elif map_type == "Google Satellite":
                    m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom, tiles=None)
                    folium.TileLayer('https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', attr='Google', name='Google Satellite', max_zoom=20).add_to(m)
                elif map_type == "Google Ibrida":
                    m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom, tiles=None)
                    folium.TileLayer('https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr='Google', name='Google Ibrida', max_zoom=20).add_to(m)
                elif map_type == "Google Rilievo":
                    m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom, tiles=None)
                    folium.TileLayer('https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}', attr='Google', name='Google Rilievo', max_zoom=20).add_to(m)
                
                # Pulsante Fullscreen
                try:
                    from folium.plugins import Fullscreen
                    Fullscreen(position="topleft", title="Espandi a tutto schermo", title_cancel="Esci da tutto schermo", force_separate_button=True).add_to(m)
                except:
                    pass
                # Altri plugin utili
                try:
                    from folium.plugins import LocateControl, MeasureControl
                    LocateControl(auto_start=False, position="topleft", strings={"title": "Mostra la mia posizione"}).add_to(m)
                    MeasureControl(position="bottomleft", primary_length_unit="meters", secondary_length_unit="kilometers").add_to(m)
                except:
                    pass
                
                for _, r in df_post.iterrows():
                    try:
                        lat_f = float(r.get("Latitudine")); lon_f = float(r.get("Longitudine"))
                        nome_p = r.get('Postazione','')
                        is_sel = nome_p == selected
                        comune_p = r.get('Comune','')
                        via_p = r.get('Via','')
                        civico_p = r.get('Civico','')
                        # Link Google Maps che mostra marker + navigazione
                        popup = f"<b>{nome_p}</b><br>{via_p} {civico_p}, {comune_p}<br>Resp: {r.get('Responsabile','')}<br>Radio: {r.get('Radio','')}<br>Lat:{lat_f} Lon:{lon_f}<br><a href='https://www.google.com/maps/search/?api=1&query={lat_f},{lon_f}' target='_blank'>📍 Vedi su Google Maps</a> | <a href='https://www.google.com/maps/dir/?api=1&destination={lat_f},{lon_f}' target='_blank'>🧭 Naviga</a> | <a href='https://waze.com/ul?ll={lat_f},{lon_f}&navigate=yes' target='_blank'>🚗 Waze</a>"
                        folium.Marker([lat_f, lon_f], popup=folium.Popup(popup, max_width=250), tooltip=nome_p, icon=folium.Icon(color="red" if is_sel else "green", icon="star" if is_sel else "info-sign")).add_to(m)
                        if is_sel:
                            folium.Circle([lat_f, lon_f], radius=60, color="red", fill=True, fill_opacity=0.3).add_to(m)
                    except:
                        pass
                # Pulsante fullscreen extra sopra mappa
                col_full1, col_full2, col_full3 = st.columns([2,2,6])
                with col_full1:
                    st.markdown("**🗺️ Mappa con pulsante fullscreen in alto a sinistra**")
                with col_full2:
                    # Link per aprire in Google Maps fullscreen
                    if st.session_state.get("selected_postazione"):
                        for _, r in df_post.iterrows():
                            if r.get("Postazione") == st.session_state.get("selected_postazione"):
                                try:
                                    lat_fs = r.get("Latitudine")
                                    lon_fs = r.get("Longitudine")
                                    st.link_button("🔎 Apri Postazione in Google Maps Fullscreen", f"https://www.google.com/maps/search/?api=1&query={lat_fs},{lon_fs}", use_container_width=True)
                                except:
                                    pass
                
                # Mappa con altezza maggiore per effetto fullscreen
                if "map_fullscreen" not in st.session_state:
                    st.session_state.map_fullscreen = False
                
                if st.button("⛶ Attiva Modalità Fullscreen Mappa (800px)", use_container_width=False, key="btn_fullscreen"):
                    st.session_state.map_fullscreen = not st.session_state.map_fullscreen
                
                map_height = 800 if st.session_state.map_fullscreen else 600
                
                st_folium(m, width=1400, height=map_height, use_container_width=True, key=f"folium_{map_type}_{center_lat}_{map_height}")
            except ImportError:
                st.warning("Installa folium")
            except Exception as e:
                st.error(f"Errore mappa: {e}")
            
            st.dataframe(df_post, use_container_width=True, hide_index=True)
        else:
            st.info("Nessuna postazione - Aggiungi la prima!")

# === REGISTRO ===
elif scelta == "📋 Registro Radio":
    st.info("📋 Registro uso radio - qui puoi aggiungere il registro giornaliero")
    with st.container(border=True):
        with st.form("form_registro"):
            c1,c2,c3 = st.columns(3)
            with c1:
                data_reg = st.date_input("Data", value=datetime.now())
                radio_reg = st.text_input("Radio ID")
            with c2:
                volontario_reg = combo_memoria("Volontario", st.session_state.mem_nomi, "vol_reg", "Nome")
                ore_uso = st.text_input("Ore uso", placeholder="08:00-12:00")
            with c3:
                stato_reg = st.selectbox("Stato finale", ["OK", "Batteria scarica", "Guasta", "Persa"])
                note_reg = st.text_input("Note")
            if st.form_submit_button("💾 Salva Registro", type="primary", use_container_width=True):
                st.session_state.registro_radio.append({
                    "Data": str(data_reg), "RadioID": radio_reg, "Volontario": volontario_reg,
                    "OreUso": ore_uso, "Stato": stato_reg, "Note": note_reg
                })
                salva_csv(st.session_state.registro_radio, FILE_REGISTRO)
                st.success("Registro salvato!")
                st.rerun()
        if st.session_state.registro_radio:
            st.dataframe(pd.DataFrame(st.session_state.registro_radio).iloc[::-1], use_container_width=True, hide_index=True)

# === LINK ===
elif scelta == "🔗 Link & Aggiornamenti":
    with st.container(border=True):
        st.markdown("#### 🔗 Link per Inserire Aggiornamenti")
        app_url = st.text_input("🌐 URL della tua app Streamlit", placeholder="https://ana-varse.streamlit.app")
        if app_url:
            st.success(f"Link: {app_url}")
            c1,c2 = st.columns(2)
            with c1:
                msg = f"Aggiorna ANA Varese: {app_url}"
                st.link_button("📱 WhatsApp", f"https://wa.me/?text={msg.replace(' ', '%20')}", use_container_width=True)
            with c2:
                st.link_button("✈️ Telegram", f"https://t.me/share/url?url={app_url}", use_container_width=True)
            try:
                import qrcode
                qr = qrcode.QRCode(version=1, box_size=10, border=4)
                qr.add_data(app_url)
                qr.make(fit=True)
                img = qr.make_image(fill='black', back_color='white')
                buf = BytesIO()
                img.save(buf, format='PNG')
                st.image(buf.getvalue(), caption="QR Code", width=200)
                st.download_button("📥 Scarica QR", buf.getvalue(), file_name="qr_ana.png", mime="image/png", use_container_width=True)
            except:
                st.info("Aggiungi qrcode[pil] ai requirements per QR")
        st.divider()
        st.markdown("#### 📤 Backup & Ripristino")
        c1,c2 = st.columns(2)
        with c1:
            if st.session_state.postazioni or st.session_state.dist_radio:
                all_data = {
                    "postazioni": st.session_state.postazioni,
                    "distribuzione_radio": st.session_state.dist_radio,
                    "radio_db": st.session_state.radio_db,
                    "volontari": st.session_state.mem_nomi,
                    "data_export": str(datetime.now())
                }
                st.download_button("📥 Backup JSON Completo", json.dumps(all_data, indent=2, ensure_ascii=False).encode('utf-8'), file_name=f"backup_{datetime.now().strftime('%Y%m%d')}.json", mime="application/json", use_container_width=True)
        with c2:
            uploaded = st.file_uploader("Carica backup JSON", type=["json"])
            if uploaded:
                try:
                    data = json.loads(uploaded.read().decode('utf-8'))
                    if st.button("🔄 Importa", type="primary", use_container_width=True):
                        if "postazioni" in data:
                            st.session_state.postazioni = data["postazioni"]
                            salva_csv(data["postazioni"], FILE_POSTAZIONI)
                        if "distribuzione_radio" in data:
                            st.session_state.dist_radio = data["distribuzione_radio"]
                            salva_csv(data["distribuzione_radio"], FILE_DIST_RADIO)
                        if "radio_db" in data:
                            st.session_state.radio_db = data["radio_db"]
                            salva_csv(data["radio_db"], FILE_RADIO_DB)
                        st.success("Importato!")
                        st.rerun()
                except Exception as e:
                    st.error(f"Errore: {e}")
