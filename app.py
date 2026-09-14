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
    st.warning("logo.png non trovato - carica logo.png su GitHub")

col_tit, col_esci = st.columns([4,1])
with col_tit:
    st.markdown("<h3 style='color:#0e7a3d; margin:0;'>VOLONTARIATO - Sezione di Varese</h3>", unsafe_allow_html=True)
with col_esci:
    if st.button("🚪 ESCI", use_container_width=True):
        st.session_state["uscito"] = True

if st.session_state.get("uscito"):
    st.markdown('<div style="text-align:center; padding:50px; background:#f0f0f0; border-radius:15px; margin-top:20px;"><h1 style="color:#0e7a3d;">Grazie per il servizio!</h1></div>', unsafe_allow_html=True)
    if st.button("🔓 Rientra"):
        st.session_state["uscito"] = False
        st.rerun()
    st.stop()

FILE_DATI = "dati_iscritti.csv"
FILE_RADIO = "radio_log.csv"
FILE_MEM_MITT = "memoria_mittenti.csv"
FILE_MEM_DEST = "memoria_destinatari.csv"
FILE_FIRMA = "firma.png"
FILE_TIMBRO = "timbro.png"

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
    st.session_state.mem_assoc = sorted(list(set([d["Associazione"] for d in st.session_state.dati]))) if st.session_state.dati else ["ANA Varese"]
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

def crea_pdf_con_pillow(df, tipo="radio"):
    try:
        from PIL import Image, ImageDraw, ImageFont
        # A4 a 150dpi = 1240x1754
        W, H = 1240, 1754
        img = Image.new('RGB', (W, H), 'white')
        draw = ImageDraw.Draw(img)
        
        # Font - usa default se non trova arial
        try:
            font_title = ImageFont.truetype("arial.ttf", 40)
            font_sub = ImageFont.truetype("arial.ttf", 24)
            font_small = ImageFont.truetype("arial.ttf", 18)
            font_tiny = ImageFont.truetype("arial.ttf", 14)
        except:
            font_title = ImageFont.load_default()
            font_sub = ImageFont.load_default()
            font_small = ImageFont.load_default()
            font_tiny = ImageFont.load_default()
        
        # Logo
        y = 30
        try:
            if os.path.exists("logo.png"):
                logo = Image.open("logo.png").convert("RGBA")
                logo = logo.resize((200, 200))
                img.paste(logo, (40, y), logo if logo.mode == 'RGBA' else None)
        except:
            pass
        
        # Titoli
        draw.text((280, y+20), "VOLONTARIATO - Sezione di Varese", fill=(14,122,61), font=font_title)
        draw.text((280, y+80), "REGISTRO TELECOMUNICAZIONI - Comunicazioni Radio" if tipo=="radio" else "ELENCO ISCRITTI", fill=(0,0,0), font=font_sub)
        draw.text((280, y+120), f"Stampa: {datetime.now().strftime('%d/%m/%Y %H:%M')} - Tot: {len(df)}", fill=(100,100,100), font=font_small)
        
        y = 250
        draw.line([(40, y), (W-40, y)], fill=(14,122,61), width=3)
        y += 20
        
        # Tabella
        if tipo == "radio":
            # header
            draw.rectangle([(40, y), (W-40, y+35)], fill=(14,122,61))
            draw.text((50, y+8), "Data Ora | Mittente -> Destinatario | Canale | Messaggi", fill="white", font=font_small)
            y += 40
            for _, row in df.iterrows():
                if y > H-200:
                    break
                # riga alternata
                if len(df) % 2 == 0:
                    draw.rectangle([(40, y), (W-40, y+50)], fill=(245,245,245))
                txt = f"{row.get('Data','')} {row.get('Ora','')} | {row.get('Mittente','')[:20]} -> {row.get('Destinatario','')[:20]} | {row.get('Canale','')[:15]}"
                draw.text((50, y+5), txt, fill=(0,0,0), font=font_tiny)
                txt2 = f"R: {str(row.get('Messaggio Ricevuto',''))[:80]}"
                draw.text((50, y+22), txt2, fill=(50,50,50), font=font_tiny)
                txt3 = f"T: {str(row.get('Messaggio Trasmesso',''))[:80]}"
                draw.text((50, y+35), txt3, fill=(0,0,150), font=font_tiny)
                y += 55
        else:
            draw.rectangle([(40, y), (W-40, y+35)], fill=(14,122,61))
            draw.text((50, y+8), "Nome | Associazione | Cell | Ruolo", fill="white", font=font_small)
            y += 40
            for _, row in df.iterrows():
                if y > H-200:
                    break
                draw.text((50, y+5), f"{row.get('Nome','')[:25]} | {row.get('Associazione','')[:20]} | {row.get('Cellulare','')} | {row.get('Ruolo','')}", fill=(0,0,0), font=font_small)
                y += 30
        
        # Firma e timbro in fondo
        y_firma = H - 300
        draw.line([(40, y_firma), (W-40, y_firma)], fill=(200,200,200), width=1)
        draw.text((100, y_firma+20), "Il Coordinatore", fill=(0,0,0), font=font_small)
        draw.text((W-300, y_firma+20), "Timbro Sezione", fill=(0,0,0), font=font_small)
        
        # Firma immagine
        try:
            if os.path.exists(FILE_FIRMA):
                firma = Image.open(FILE_FIRMA).convert("RGBA").resize((250, 100))
                img.paste(firma, (80, y_firma+50), firma if firma.mode == 'RGBA' else None)
        except:
            pass
        try:
            if os.path.exists(FILE_TIMBRO):
                timbro = Image.open(FILE_TIMBRO).convert("RGBA").resize((200, 200))
                img.paste(timbro, (W-300, y_firma+50), timbro if timbro.mode == 'RGBA' else None)
        except:
            pass
        
        draw.text((100, y_firma+170), st.session_state.get("nome_coord", "Coordinatore"), fill=(0,0,0), font=font_small)
        draw.text((100, y_firma+195), "________________________", fill=(0,0,0), font=font_small)
        draw.text((W-300, y_firma+195), "________________________", fill=(0,0,0), font=font_small)
        
        # Salva come PDF
        pdf_buffer = BytesIO()
        img.save(pdf_buffer, "PDF", resolution=150.0)
        return pdf_buffer.getvalue()
    except Exception as e:
        st.error(f"Errore PDF Pillow: {e}")
        return None



def crea_pdf_fpdf(df, tipo="radio"):
    try:
        from fpdf import FPDF
        pdf = FPDF(orientation='L', unit='mm', format='A4')
        pdf.set_auto_page_break(auto=True, margin=20)
        pdf.add_page()
        
        # Logo piccolo
        try:
            if os.path.exists("logo.png"):
                pdf.image("logo.png", x=10, y=6, w=15)
        except:
            pass
        
        pdf.set_xy(28, 8)
        pdf.set_font("Arial", "B", 13)
        pdf.set_text_color(14, 122, 61)
        pdf.cell(0, 7, "VOLONTARIATO - Sezione di Varese", ln=True)
        pdf.set_x(28)
        pdf.set_font("Arial", "B", 10)
        pdf.set_text_color(0,0,0)
        pdf.cell(0, 6, "REGISTRO TELECOMUNICAZIONI" if tipo=="radio" else "ELENCO ISCRITTI", ln=True)
        pdf.set_x(28)
        pdf.set_font("Arial", "", 7)
        pdf.set_text_color(80,80,80)
        pdf.cell(0, 4, f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')} - Tot: {len(df)} - ANA Varese", ln=True)
        pdf.ln(5)
        
        if tipo=="radio":
            col_widths = [18, 10, 18, 24, 24, 85, 85]
            headers = ["Data", "Ora", "Canale", "Mittente", "Destinatario", "RICEVUTO", "TRASMESSO"]
            
            # Header
            pdf.set_fill_color(14, 122, 61)
            pdf.set_text_color(255,255,255)
            pdf.set_font("Arial", "B", 7)
            for i,h in enumerate(headers):
                pdf.cell(col_widths[i], 7, h, border=1, fill=True, align="C")
            pdf.ln()
            
            pdf.set_font("Arial", "", 6.5)
            pdf.set_text_color(0,0,0)
            
            for _, row in df.iterrows():
                ricev = str(row.get("Messaggio Ricevuto",""))
                trasm = str(row.get("Messaggio Trasmesso",""))
                
                # Calcola altezza necessaria - 35 caratteri per riga circa per 85mm con font 6.5
                def calc_h(text, col_w):
                    if not text:
                        return 8
                    # stima caratteri per riga
                    chars_per_line = int(col_w * 2.2)
                    lines = (len(text) // chars_per_line) + 1
                    # conta anche a capo manuali
                    lines += text.count("
")
                    return max(8, lines * 4.5)
                
                h_ricev = calc_h(ricev, col_widths[5])
                h_trasm = calc_h(trasm, col_widths[6])
                h_row = max(8, h_ricev, h_trasm)
                
                # Controllo pagina
                if pdf.get_y() + h_row > 185:
                    pdf.add_page()
                
                y_start = pdf.get_y()
                x_start = pdf.get_x()
                
                # Disegna TUTTE le celle con STESSA ALTEZZA h_row
                # Celle fisse con altezza uguale
                pdf.set_xy(x_start, y_start)
                pdf.cell(col_widths[0], h_row, str(row.get("Data",""))[:10], border=1)
                pdf.cell(col_widths[1], h_row, str(row.get("Ora",""))[:5], border=1, align="C")
                pdf.cell(col_widths[2], h_row, str(row.get("Canale",""))[:16], border=1)
                pdf.cell(col_widths[3], h_row, str(row.get("Mittente",""))[:18], border=1)
                pdf.cell(col_widths[4], h_row, str(row.get("Destinatario",""))[:18], border=1)
                
                # Per i messaggi, creiamo celle con stessa altezza ma testo a capo interno
                x_ricev = x_start + sum(col_widths[:5])
                x_trasm = x_ricev + col_widths[5]
                
                # Rettangoli con stessa altezza
                pdf.rect(x_ricev, y_start, col_widths[5], h_row)
                pdf.rect(x_trasm, y_start, col_widths[6], h_row)
                
                # Testo dentro con margine
                pdf.set_xy(x_ricev+1, y_start+1)
                pdf.multi_cell(col_widths[5]-2, 4, ricev[:400], border=0)
                
                pdf.set_xy(x_trasm+1, y_start+1)
                pdf.multi_cell(col_widths[6]-2, 4, trasm[:400], border=0)
                
                # Vai a fine riga (altezza uguale per tutti)
                pdf.set_y(y_start + h_row)
        else:
            pdf.set_fill_color(14, 122, 61)
            pdf.set_text_color(255,255,255)
            pdf.set_font("Arial", "B", 9)
            pdf.cell(50, 8, "Nome", border=1, fill=True, align="C")
            pdf.cell(50, 8, "Associazione", border=1, fill=True, align="C")
            pdf.cell(35, 8, "Cellulare", border=1, fill=True, align="C")
            pdf.cell(30, 8, "Ruolo", border=1, fill=True, align="C")
            pdf.cell(30, 8, "Note", border=1, fill=True, align="C")
            pdf.ln()
            pdf.set_text_color(0,0,0)
            pdf.set_font("Arial", "", 8)
            for _, row in df.iterrows():
                if pdf.get_y() > 185:
                    pdf.add_page()
                pdf.cell(50, 7, str(row.get("Nome",""))[:25], border=1)
                pdf.cell(50, 7, str(row.get("Associazione",""))[:25], border=1)
                pdf.cell(35, 7, str(row.get("Cellulare",""))[:18], border=1)
                pdf.cell(30, 7, str(row.get("Ruolo",""))[:15], border=1)
                pdf.cell(30, 7, str(row.get("Note",""))[:15], border=1)
                pdf.ln()
        
        # Firma
        pdf.ln(6)
        if pdf.get_y() > 160:
            pdf.add_page()
        yf = pdf.get_y()
        pdf.set_font("Arial", "", 9)
        pdf.set_xy(20, yf)
        pdf.cell(80, 6, "Il Coordinatore", align="C")
        pdf.set_xy(150, yf)
        pdf.cell(80, 6, "Timbro Sezione", align="C")
        try:
            if os.path.exists(FILE_FIRMA):
                pdf.image(FILE_FIRMA, x=25, y=yf+8, w=45)
        except:
            pass
        try:
            if os.path.exists(FILE_TIMBRO):
                pdf.image(FILE_TIMBRO, x=155, y=yf+8, w=40)
        except:
            pass
        pdf.set_xy(20, yf+28)
        pdf.cell(80, 6, "________________________", align="C")
        pdf.set_xy(150, yf+28)
        pdf.cell(80, 6, "________________________", align="C")
        pdf.set_xy(20, yf+34)
        pdf.set_font("Arial", "B", 8)
        pdf.cell(80, 6, st.session_state.get("nome_coord", "Coordinatore"), align="C")
        pdf.set_y(-10)
        pdf.set_font("Arial", "I", 7)
        pdf.cell(0, 10, f"ANA Varese - Pag {pdf.page_no()}", align="C")
        
        out = pdf.output()
        if isinstance(out, bytearray):
            out = bytes(out)
        elif isinstance(out, str):
            out = out.encode("latin-1")
        return out
    except Exception as e:
        st.error(f"Errore PDF: {e}")
        import traceback
        st.code(traceback.format_exc())
        return None

        return out
    except Exception as e:
        st.error(f"Errore PDF: {e}")
        return None


# Sidebar firma
with st.sidebar:
    st.markdown("### Firma e Timbro PDF")
    firma_file = st.file_uploader("Carica Firma PNG/JPG", type=["png","jpg","jpeg"], key="firma_up")
    if firma_file:
        with open(FILE_FIRMA, "wb") as f:
            f.write(firma_file.getbuffer())
        st.success("Firma caricata!")
        st.image(FILE_FIRMA, width=150)
    elif os.path.exists(FILE_FIRMA):
        st.image(FILE_FIRMA, width=150, caption="Firma")
        if st.button("Rimuovi firma"):
            os.remove(FILE_FIRMA)
            st.rerun()
    timbro_file = st.file_uploader("Carica Timbro PNG/JPG", type=["png","jpg","jpeg"], key="timbro_up")
    if timbro_file:
        with open(FILE_TIMBRO, "wb") as f:
            f.write(timbro_file.getbuffer())
        st.success("Timbro caricato!")
        st.image(FILE_TIMBRO, width=150)
    elif os.path.exists(FILE_TIMBRO):
        st.image(FILE_TIMBRO, width=150, caption="Timbro")
        if st.button("Rimuovi timbro"):
            os.remove(FILE_TIMBRO)
            st.rerun()
    st.divider()
    nome_coord = st.text_input("Nome Coordinatore", value=st.session_state.get("nome_coord", "Coordinatore Sezione Varese"))
    st.session_state["nome_coord"] = nome_coord
    st.divider()
    st.write("Se PDF da errore, usa Excel")

# Maschera principale
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
                    st.session_state.mem_mitt.append(nome)
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
        st.download_button("Excel Anagrafica", out.getvalue(), file_name="anagrafica.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
    with col2:
        pdf = crea_pdf_fpdf(df_anag, "anagrafica")
        if pdf is None:
            pdf = crea_pdf_con_pillow(df_anag, "anagrafica")
        if pdf:
            st.download_button("PDF Anagrafica A4 Logo+Firma", pdf, file_name=f"ANA_Anagrafica_{datetime.now().strftime('%Y%m%d')}.pdf", mime="application/pdf", use_container_width=True)

st.divider()
st.markdown("### SOTTOMASCHERA INCORPORATA - Registro Radio")
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
        if st.form_submit_button("REGISTRA", use_container_width=True, type="primary"):
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
        st.write(f"Comunicazioni: {len(df_radio)} | Mittenti: {len(st.session_state.mem_mitt)}")
        st.dataframe(df_radio, use_container_width=True, hide_index=True)
        col1,col2,col3 = st.columns(3)
        with col1:
            out = BytesIO()
            df_radio.to_excel(out, index=False, engine="openpyxl")
            st.download_button("Excel Radio", out.getvalue(), file_name=f"registro_radio_{datetime.now().strftime('%Y%m%d')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        with col2:
            # Prova prima fpdf, se non c'è usa Pillow (che non da mai errore)
            pdf = crea_pdf_fpdf(df_radio, "radio")
            if pdf is None:
                pdf = crea_pdf_con_pillow(df_radio, "radio")
            if pdf:
                st.download_button("PDF A4 Logo+Firma Ufficiale", pdf, file_name=f"ANA_Registro_Radio_{datetime.now().strftime('%Y%m%d')}.pdf", mime="application/pdf", use_container_width=True, type="primary")
            else:
                st.warning("PDF non disponibile, usa Excel")
        with col3:
            csv = df_radio.to_csv(index=False).encode('utf-8')
            st.download_button("CSV", csv, file_name="registro_radio.csv", mime="text/csv", use_container_width=True)
