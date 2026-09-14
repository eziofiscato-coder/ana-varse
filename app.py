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




FILE_DIST_RADIO = "distribuzione_radio.csv"
FILE_POSTAZIONI = "postazioni_mappa.csv"

if "dist_radio" not in st.session_state:
    st.session_state.dist_radio = pd.read_csv(FILE_DIST_RADIO).to_dict(orient="records") if os.path.exists(FILE_DIST_RADIO) else []
if "postazioni" not in st.session_state:
    st.session_state.postazioni = pd.read_csv(FILE_POSTAZIONI).to_dict(orient="records") if os.path.exists(FILE_POSTAZIONI) else []

def salva_dist_radio():
    if st.session_state.dist_radio:
        pd.DataFrame(st.session_state.dist_radio).to_csv(FILE_DIST_RADIO, index=False)
def salva_postazioni():
    if st.session_state.postazioni:
        pd.DataFrame(st.session_state.postazioni).to_csv(FILE_POSTAZIONI, index=False)

def crea_pdf_distribuzione(df):
    try:
        from fpdf import FPDF
        pdf = FPDF(orientation='L', unit='mm', format='A4')
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        try:
            if os.path.exists("logo.png"):
                pdf.image("logo.png", x=8, y=6, w=14)
        except:
            pass
        pdf.set_xy(25, 8)
        pdf.set_font("Arial", "B", 12)
        pdf.set_text_color(14, 122, 61)
        pdf.cell(0, 7, "VOLONTARIATO - Sezione di Varese - DISTRIBUZIONE RADIO", ln=True)
        pdf.set_x(25)
        pdf.set_font("Arial", "", 7)
        pdf.set_text_color(0,0,0)
        pdf.cell(0, 4, f"Data stampa: {datetime.now().strftime('%d/%m/%Y %H:%M')} - Tot: {len(df)}", ln=True)
        pdf.ln(5)
        
        pdf.set_fill_color(14, 122, 61)
        pdf.set_text_color(255,255,255)
        pdf.set_font("Arial", "B", 6.5)
        cols = [18, 22, 20, 30, 28, 18, 18, 15, 20, 35]
        heads = ["Data","Radio ID","Modello","Assegnatario","Postazione","Consegna","Riconsegna","Stato","Canale","Note"]
        for i,h in enumerate(heads):
            pdf.cell(cols[i], 7, h, border=1, fill=True, align="C")
        pdf.ln()
        
        pdf.set_text_color(0,0,0)
        pdf.set_font("Arial", "", 6)
        for _, r in df.iterrows():
            if pdf.get_y() > 180:
                pdf.add_page()
            # Tutte celle stessa altezza
            h_row = 8
            pdf.cell(cols[0], h_row, str(r.get("Data",""))[:10], border=1)
            pdf.cell(cols[1], h_row, str(r.get("RadioID",""))[:12], border=1)
            pdf.cell(cols[2], h_row, str(r.get("Modello",""))[:12], border=1)
            pdf.cell(cols[3], h_row, str(r.get("Assegnatario",""))[:18], border=1)
            pdf.cell(cols[4], h_row, str(r.get("Postazione",""))[:16], border=1)
            pdf.cell(cols[5], h_row, str(r.get("OraConsegna",""))[:8], border=1, align="C")
            pdf.cell(cols[6], h_row, str(r.get("OraRiconsegna",""))[:8], border=1, align="C")
            pdf.cell(cols[7], h_row, str(r.get("Stato",""))[:8], border=1, align="C")
            pdf.cell(cols[8], h_row, str(r.get("Canale",""))[:10], border=1)
            pdf.cell(cols[9], h_row, str(r.get("Note",""))[:20], border=1)
            pdf.ln()
        
        pdf.ln(6)
        yf = pdf.get_y()
        pdf.set_xy(20, yf)
        pdf.cell(60, 6, "Consegnato da", align="C")
        pdf.set_xy(100, yf)
        pdf.cell(60, 6, "Ricevuto da", align="C")
        pdf.set_xy(180, yf)
        pdf.cell(60, 6, "Timbro", align="C")
        try:
            if os.path.exists(FILE_FIRMA):
                pdf.image(FILE_FIRMA, x=25, y=yf+6, w=40)
        except:
            pass
        try:
            if os.path.exists(FILE_TIMBRO):
                pdf.image(FILE_TIMBRO, x=185, y=yf+6, w=35)
        except:
            pass
        pdf.set_xy(20, yf+22)
        pdf.cell(60, 6, "___________________", align="C")
        pdf.set_xy(100, yf+22)
        pdf.cell(60, 6, "___________________", align="C")
        pdf.set_xy(180, yf+22)
        pdf.cell(60, 6, "___________________", align="C")
        pdf.set_y(-10)
        pdf.set_font("Arial", "I", 6)
        pdf.cell(0, 10, f"ANA Varese - Distribuzione Radio - Pag {pdf.page_no()}", align="C")
        out = pdf.output()
        if isinstance(out, bytearray):
            out = bytes(out)
        elif isinstance(out, str):
            out = out.encode("latin-1")
        return out
    except Exception as e:
        st.error(f"Errore PDF: {e}")
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
                    lines += text.count(chr(10))
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



st.divider()
st.markdown("## 📋 2 SCHEDE RICHIESTE")
st.caption("1. Distribuzione Radio - 2. Mappa Postazioni con OpenStreetMap")

tab_dist, tab_mappa = st.tabs(["📻 SCHEDA 1 - Distribuzione Radio", "🗺️ SCHEDA 2 - Mappa Postazioni OSM"])

with tab_dist:
    with st.container(border=True):
        st.markdown("#### 📻 Scheda Distribuzione Radio ai Volontari")
        with st.form("form_dist_radio"):
            c1,c2,c3,c4 = st.columns(4)
            with c1:
                data_d = st.date_input("Data", value=datetime.now(), key="data_dist")
                radio_id = st.text_input("Radio ID *", placeholder="Es: R-01, R-02")
            with c2:
                modello = st.selectbox("Modello", ["Baofeng UV-5R", "Motorola T82", "Midland G9", "Intek MT-5050", "Altro"])
                assegnatario = combo_memoria("Assegnatario", st.session_state.mem_nomi if st.session_state.mem_nomi else ["Volontario"], "asseg_radio", "Nome volontario")
            with c3:
                postazione = st.text_input("Postazione *", placeholder="Es: Cancello 1, Posto 3, COC")
                canale = st.selectbox("Canale assegnato", ["CH 1 - Emergenza", "CH 2 - Logistica", "CH 3 - Coordinamento", "CH 4 - Operativo", "VHF 145.500"])
            with c4:
                ora_cons = st.text_input("Ora consegna", value=datetime.now().strftime("%H:%M"))
                ora_ric = st.text_input("Ora riconsegna", placeholder="Da compilare al rientro")
            c5,c6 = st.columns(2)
            with c5:
                stato_r = st.selectbox("Stato Radio", ["Consegnata", "Riconsegnata", "Guasta", "Smarrimento", "Batteria scarica"])
            with c6:
                note_d = st.text_input("Note", placeholder="Es: Con batteria carica, con auricolare")
            if st.form_submit_button("📻 Assegna Radio", use_container_width=True, type="primary"):
                if radio_id and assegnatario and postazione:
                    st.session_state.dist_radio.append({
                        "Data": str(data_d), "RadioID": radio_id, "Modello": modello,
                        "Assegnatario": assegnatario, "Postazione": postazione, "Canale": canale,
                        "OraConsegna": ora_cons, "OraRiconsegna": ora_ric, "Stato": stato_r, "Note": note_d
                    })
                    salva_dist_radio()
                    st.success(f"Radio {radio_id} assegnata a {assegnatario} in {postazione}")
                    st.rerun()
                else:
                    st.error("Compila Radio ID, Assegnatario e Postazione")
        
        if st.session_state.dist_radio:
            df_dist = pd.DataFrame(st.session_state.dist_radio).iloc[::-1]
            st.dataframe(df_dist, use_container_width=True, hide_index=True)
            c1,c2,c3 = st.columns(3)
            with c1:
                out = BytesIO()
                df_dist.to_excel(out, index=False, engine="openpyxl")
                st.download_button("📥 Excel Distribuzione", out.getvalue(), file_name="distribuzione_radio.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
            with c2:
                pdf_d = crea_pdf_distribuzione(df_dist)
                if pdf_d:
                    st.download_button("📄 PDF A4 Distribuzione con Firma", pdf_d, file_name=f"Distribuzione_Radio_{datetime.now().strftime('%Y%m%d')}.pdf", mime="application/pdf", use_container_width=True, type="primary")
            with c3:
                # Pulsante riconsegna rapida
                if st.button("🔄 Segna tutte come Riconsegnate", use_container_width=True):
                    for r in st.session_state.dist_radio:
                        if r["Stato"] == "Consegnata":
                            r["Stato"] = "Riconsegnata"
                            r["OraRiconsegna"] = datetime.now().strftime("%H:%M")
                    salva_dist_radio()
                    st.rerun()

with tab_mappa:
    with st.container(border=True):
        st.markdown("#### 🗺️ Mappa Postazioni - OpenStreetMap con Assegnazione")
        
        # Form aggiunta postazione con coordinate
        with st.expander("➕ Aggiungi Nuova Postazione sulla Mappa", expanded=False):
            with st.form("form_postazione"):
                c1,c2,c3 = st.columns(3)
                with c1:
                    nome_post = st.text_input("Nome Postazione *", placeholder="Es: Posto 1 - Ingresso, Cancello A")
                    lat = st.text_input("Latitudine *", placeholder="Es: 45.8205")
                    lon = st.text_input("Longitudine *", placeholder="Es: 8.8255")
                with c2:
                    resp_post = combo_memoria("Responsabile", st.session_state.mem_nomi if st.session_state.mem_nomi else ["Volontario"], "resp_post", "Nome responsabile")
                    radio_post = st.text_input("Radio assegnata", placeholder="Es: R-01")
                with c3:
                    tipo_post = st.selectbox("Tipo Postazione", ["Controllo accessi", "Viabilità", "Sicurezza", "Logistica", "COC", "Primo soccorso", "Altro"])
                    note_post = st.text_area("Note postazione", placeholder="Compiti, orari, ecc.", height=80)
                
                st.markdown("💡 **Come trovare coordinate:** Vai su https://www.openstreetmap.org → cerca luogo → click destro → Mostra indirizzo → copia lat/lon")
                
                if st.form_submit_button("📍 Aggiungi alla Mappa", use_container_width=True, type="primary"):
                    if nome_post and lat and lon:
                        try:
                            float(lat)
                            float(lon)
                            st.session_state.postazioni.append({
                                "Data": str(datetime.now().date()),
                                "Postazione": nome_post,
                                "Latitudine": lat,
                                "Longitudine": lon,
                                "Responsabile": resp_post,
                                "Radio": radio_post,
                                "Tipo": tipo_post,
                                "Note": note_post
                            })
                            salva_postazioni()
                            st.success(f"Postazione {nome_post} aggiunta!")
                            st.rerun()
                        except:
                            st.error("Latitudine e Longitudine devono essere numeri (es: 45.8205)")
                    else:
                        st.error("Nome, Latitudine e Longitudine obbligatori")
        
        if st.session_state.postazioni:
            df_post = pd.DataFrame(st.session_state.postazioni)
            
            # Mappa con folium se disponibile, altrimenti st.map
            try:
                import folium
                from streamlit_folium import st_folium
                
                # Centro mappa su Varese
                m = folium.Map(location=[45.8205, 8.8255], zoom_start=13, tiles="OpenStreetMap")
                
                for _, r in df_post.iterrows():
                    try:
                        lat_f = float(r.get("Latitudine", 0))
                        lon_f = float(r.get("Longitudine", 0))
                        popup_html = f"""
                        <b>{r.get('Postazione','')}</b><br>
                        Resp: {r.get('Responsabile','')}<br>
                        Radio: {r.get('Radio','')}<br>
                        Tipo: {r.get('Tipo','')}<br>
                        Note: {r.get('Note','')}
                        """
                        folium.Marker(
                            [lat_f, lon_f],
                            popup=folium.Popup(popup_html, max_width=250),
                            tooltip=r.get('Postazione',''),
                            icon=folium.Icon(color="green", icon="info-sign")
                        ).add_to(m)
                    except:
                        pass
                
                st_folium(m, width=1200, height=500)
                
            except ImportError:
                st.info("Per mappa interattiva OSM installa: pip install folium streamlit-folium - Uso mappa base per ora")
                # Fallback st.map
                try:
                    map_data = []
                    for _, r in df_post.iterrows():
                        try:
                            map_data.append({"lat": float(r.get("Latitudine")), "lon": float(r.get("Longitudine"))})
                        except:
                            pass
                    if map_data:
                        st.map(pd.DataFrame(map_data), zoom=13)
                except:
                    pass
            except Exception as e:
                st.error(f"Errore mappa: {e}")
                # Fallback
                try:
                    map_data = []
                    for _, r in df_post.iterrows():
                        try:
                            map_data.append({"lat": float(r.get("Latitudine")), "lon": float(r.get("Longitudine"))})
                        except:
                            pass
                    if map_data:
                        st.map(pd.DataFrame(map_data), zoom=13)
                except:
                    pass
            
            st.dataframe(df_post, use_container_width=True, hide_index=True)
            
            c1,c2,c3 = st.columns(3)
            with c1:
                out = BytesIO()
                df_post.to_excel(out, index=False, engine="openpyxl")
                st.download_button("📥 Excel Postazioni", out.getvalue(), file_name="postazioni_mappa.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
            with c2:
                # PDF postazioni
                try:
                    from fpdf import FPDF
                    pdf = FPDF(orientation='L', unit='mm', format='A4')
                    pdf.add_page()
                    try:
                        if os.path.exists("logo.png"):
                            pdf.image("logo.png", x=8, y=6, w=14)
                    except:
                        pass
                    pdf.set_xy(25, 8)
                    pdf.set_font("Arial", "B", 12)
                    pdf.set_text_color(14, 122, 61)
                    pdf.cell(0, 7, "VOLONTARIATO Varese - MAPPA POSTAZIONI", ln=True)
                    pdf.set_x(25)
                    pdf.set_font("Arial", "", 7)
                    pdf.cell(0, 4, f"Data: {datetime.now().strftime('%d/%m/%Y')} - Tot postazioni: {len(df_post)}", ln=True)
                    pdf.ln(5)
                    pdf.set_fill_color(14, 122, 61)
                    pdf.set_text_color(255,255,255)
                    pdf.set_font("Arial", "B", 7)
                    cols = [30, 25, 25, 25, 20, 25, 50]
                    heads = ["Postazione","Lat","Lon","Resp.","Radio","Tipo","Note"]
                    for i,h in enumerate(heads):
                        pdf.cell(cols[i], 7, h, border=1, fill=True, align="C")
                    pdf.ln()
                    pdf.set_text_color(0,0,0)
                    pdf.set_font("Arial", "", 6)
                    for _, r in df_post.iterrows():
                        pdf.cell(cols[0], 7, str(r.get("Postazione",""))[:18], border=1)
                        pdf.cell(cols[1], 7, str(r.get("Latitudine",""))[:12], border=1)
                        pdf.cell(cols[2], 7, str(r.get("Longitudine",""))[:12], border=1)
                        pdf.cell(cols[3], 7, str(r.get("Responsabile",""))[:14], border=1)
                        pdf.cell(cols[4], 7, str(r.get("Radio",""))[:10], border=1)
                        pdf.cell(cols[5], 7, str(r.get("Tipo",""))[:14], border=1)
                        pdf.cell(cols[6], 7, str(r.get("Note",""))[:28], border=1)
                        pdf.ln()
                    out_pdf = pdf.output()
                    if isinstance(out_pdf, bytearray):
                        out_pdf = bytes(out_pdf)
                    elif isinstance(out_pdf, str):
                        out_pdf = out_pdf.encode("latin-1")
                    st.download_button("📄 PDF Mappa Postazioni", out_pdf, file_name=f"Mappa_Postazioni_{datetime.now().strftime('%Y%m%d')}.pdf", mime="application/pdf", use_container_width=True)
                except Exception as e:
                    st.error(f"PDF: {e}")
            with c3:
                if st.button("🗑️ Cancella tutte le postazioni", use_container_width=True):
                    st.session_state.postazioni = []
                    salva_postazioni()
                    st.rerun()
        else:
            st.info("Nessuna postazione ancora. Aggiungi la prima postazione con coordinate!")
            # Mappa di esempio centrata su Varese
            st.map(pd.DataFrame([{"lat": 45.8205, "lon": 8.8255}]), zoom=12)
            st.caption("Mappa centrata su Varese - Aggiungi postazioni per vederle qui")

# Mantieni anche le vecchie sezioni radio e anagrafica prima
