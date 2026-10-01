import streamlit as st
import pandas as pd, os, io, base64, json
from datetime import datetime, date, time
from io import BytesIO
try:
    import openpyxl
    OPENPYXL_OK=True
except:
    OPENPYXL_OK=False
try:
    from reportlab.lib.pagesizes import landscape, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader
    REPORTLAB_OK=True
except:
    REPORTLAB_OK=False

st.set_page_config(page_title="ANA Varese TUTTO FIX", page_icon="🛡️", layout="wide")
st.markdown("""
<style>
.stTabs [data-baseweb="tab-list"] {gap:6px!important;}
.stTabs [data-baseweb="tab-list"] button:nth-child(1){background:#FFEBCC!important;color:#8a4a00!important;border-color:#ff9800!important}
.stTabs [data-baseweb="tab-list"] button:nth-child(1)[aria-selected="true"]{background:#ff9800!important;color:white!important}
.stTabs [data-baseweb="tab-list"] button:nth-child(2){background:#D6EAF8!important;color:#1a4a7a!important;border-color:#3498db!important}
.stTabs [data-baseweb="tab-list"] button:nth-child(2)[aria-selected="true"]{background:#3498db!important;color:white!important}
.stTabs [data-baseweb="tab-list"] button:nth-child(3){background:#D5F5E3!important;color:#1a5d1a!important;border-color:#27ae60!important}
.stTabs [data-baseweb="tab-list"] button:nth-child(3)[aria-selected="true"]{background:#27ae60!important;color:white!important}
div[data-testid="column"], div[data-testid="stTabContent"] {background-color:#C8E6C9!important;border-radius:10px!important;padding:12px!important;border:2px solid #81C784!important;}
</style>
""", unsafe_allow_html=True)

def load_b64(p):
    for path in p:
        try:
            if os.path.exists(path):
                with open(path,"rb") as f:
                    return base64.b64encode(f.read()).decode()
        except: pass
    return ""

def hdr():
    b64_1=load_b64(["logo.png","logo.png","/home/code-interpreter/logo.png"])
    b64_2=load_b64(["gruppo_CPB.jpeg","gruppo_CPB.jpeg","/home/code-interpreter/gruppo_CPB.jpeg","logo2.png"])
    h1=f'<img src="data:image/png;base64,{b64_1}" style="width:88px;height:88px;border-radius:50%;object-fit:cover;background:white;border:2px solid white;">' if b64_1 else '<div style="width:88px;height:88px;border-radius:50%;background:white;display:flex;align-items:center;justify-content:center;font-weight:bold;color:#1A5D1A;">ANA</div>'
    h2=f'<img src="data:image/jpeg;base64,{b64_2}" style="width:88px;height:88px;border-radius:50%;object-fit:cover;background:white;border:2px solid white;">' if b64_2 else '<div style="width:88px;height:88px;border-radius:50%;background:white;display:flex;align-items:center;justify-content:center;font-weight:bold;color:#1A5D1A;">GRUPPO</div>'
    st.markdown(f"""<div style="background:#d6ecd2;border:2px solid #a5d6a7;border-radius:12px;padding:8px 14px;display:flex;align-items:center;gap:12px;margin-bottom:14px;"><div style="display:flex;gap:10px;">{h1}{h2}</div><div style="flex:1;background:linear-gradient(135deg,#1A5D1A 0%,#2e7d32 100%);border-radius:10px;padding:14px 20px;display:flex;flex-direction:column;justify-content:center;align-items:center;min-height:88px;text-align:center;"><div style="font-family:'Times New Roman',serif;font-weight:bold;font-size:16px;color:white;">Squadra Volontari di protezione civile - Gruppo Alpini di Caronno Pertusella Bariola</div><div style="font-family:'Times New Roman',serif;font-weight:bold;font-size:20px;color:white;margin-top:4px;">NUCLEO VOLONTARI DI P.C. A.N.A. - SEZIONE DI VARESE</div><div style="font-family:'Times New Roman',serif;font-weight:bold;font-size:14px;color:white;margin-top:2px;letter-spacing:1.2px;">ASSOCIAZIONE NAZIONALE ALPINI</div></div></div>""",unsafe_allow_html=True)

def hdr_form(t):
    st.markdown(f"""<h2 style="font-family:Times New Roman;font-weight:bold;color:black;border-bottom:3px solid #1A5D1A;padding-bottom:4px;font-size:22px;">{t}</h2>""", unsafe_allow_html=True)

def to_excel(df):
    if not OPENPYXL_OK: return b''
    buf=io.BytesIO()
    try:
        df.to_excel(buf, index=False, engine="openpyxl")
        buf.seek(0)
        return buf.getvalue()
    except: return b''

defaults={"volontari":[],"radio_db":[],"consegna_radio":[],"alias_radio":[],"brogliaccio":[],"eventi":[],"emergenze":[],"checkin":[],"interventi":[],"mezzi":[],"attrezzature":[],"mappa_avanzata_markers":[],"icone":[],"turni":[],"chat":[],"verbali":[],"archivio_documenti":[],"diplomi":[],"posizioni_pd785":[],"posizioni_anytone":[],"menu":"Dashboard","logged":True}
for k,v in defaults.items():
    if k not in st.session_state:
        st.session_state[k]=v

hdr()
menu_base=["Dashboard","Volontari (con foto)","DB Radio","Consegna Radio","Alias Radio","Brogliaccio","Eventi","Emergenze","Check-in","Interventi Emergenza","Mezzi","Attrezzature","Mappe Postazioni","Libreria Icone","Turni","Chat","Verbali","Archivio Documenti","Diplomi Attestati","Geolocalizzazione Hytera + Anytone","Report Filtro PDF","Backup"]
cur=st.sidebar.radio("Seleziona form", menu_base, index=menu_base.index(st.session_state.menu) if st.session_state.menu in menu_base else 0)
st.session_state.menu=cur

if cur=="Dashboard":
    hdr_form("MENU' - TUTTO FIX - Encoding UTF-8")
    cols=st.columns(3)
    for i,name in enumerate(menu_base[1:]):
        if cols[i%3].button(name, key=f"dash_{name}", use_container_width=True):
            st.session_state.menu=name
            st.rerun()

elif cur=="Volontari (con foto)":
    hdr_form("VOLONTARI (CON FOTO) + Foto")
    c1,c2=st.columns(2)
    with c1:
        nome=st.text_input("Nome *", key="vol_nome")
        cognome=st.text_input("Cognome *", key="vol_cognome")
        comune=st.text_input("Comune","Varese", key="vol_comune")
        capo=st.text_input("Capo ODV *", key="vol_capo")
        cell=st.text_input("Cellulare *", key="vol_cell")
    with c2:
        squadra=st.selectbox("Squadra",["Squadra A","Squadra B"], key="vol_squadra")
        foto_file=st.file_uploader("Foto JPG/PNG", type=["jpg","jpeg","png"], key="vol_foto")
        foto_bytes=None
        if foto_file:
            foto_bytes=foto_file.getvalue()
            st.image(foto_bytes, width=150)
    if st.button("Salva Volontario", type="primary", use_container_width=True):
        if nome and cognome and capo and cell:
            st.session_state.volontari.append({"Nome":nome,"Cognome":cognome,"Comune":comune,"CapoODV":capo,"Cellulare":cell,"Squadra":squadra,"FotoBytes":foto_bytes,"DataIns":datetime.now().strftime("%d/%m/%Y")})
            st.success("Salvato")
            st.rerun()
    if st.session_state.volontari:
        st.dataframe(pd.DataFrame([{k:v for k,v in r.items() if "Bytes" not in k} for r in st.session_state.volontari]), use_container_width=True)
        st.download_button("Excel", to_excel(pd.DataFrame([{k:v for k,v in r.items() if "Bytes" not in k} for r in st.session_state.volontari])), "volontari.xlsx", use_container_width=True)

elif cur=="Mappe Postazioni":
    hdr_form("MAPPE POSTAZIONI - Lat/Lon + Icone + Fullscreen")
    nome_post=st.text_input("Nome Postazione *", key="map_nome")
    c1,c2=st.columns(2)
    with c1:
        comune_post=st.text_input("Comune *","Caronno Pertusella", key="map_comune")
        lat_post=st.text_input("Latitudine *","45.6045", key="map_lat")
    with c2:
        via_post=st.text_input("Via", key="map_via")
        lon_post=st.text_input("Longitudine *","9.0586", key="map_lon")
    if st.button("Salva Postazione", type="primary", use_container_width=True):
        if nome_post and comune_post and lat_post and lon_post:
            st.session_state.mappa_avanzata_markers.append({"Nome":nome_post,"Comune":comune_post,"Via":via_post,"Lat":lat_post,"Lon":lon_post,"DataIns":datetime.now().strftime("%d/%m/%Y")})
            st.success("Salvata")
            st.rerun()
    if st.session_state.mappa_avanzata_markers:
        df=pd.DataFrame(st.session_state.mappa_avanzata_markers)
        st.dataframe(df, use_container_width=True)
        try:
            st.map(pd.DataFrame([{"lat":float(r["Lat"]),"lon":float(r["Lon"])} for r in st.session_state.mappa_avanzata_markers]))
        except: pass

elif cur=="Report Filtro PDF":
    hdr_form("REPORT FILTRO PDF - Crea report con dati che vuoi tu")
    FORM_KEYS={"Volontari (con foto)":"volontari","DB Radio":"radio_db","Consegna Radio":"consegna_radio","Alias Radio":"alias_radio","Brogliaccio":"brogliaccio","Eventi":"eventi","Emergenze":"emergenze","Check-in":"checkin","Interventi Emergenza":"interventi","Mezzi":"mezzi","Attrezzature":"attrezzature","Mappe Postazioni":"mappa_avanzata_markers","Turni":"turni","Diplomi Attestati":"diplomi"}
    c1,c2=st.columns(2)
    with c1:
        sorgente_label=st.selectbox("Sorgente dati *", list(FORM_KEYS.keys()))
        sorgente_key=FORM_KEYS[sorgente_label]
        dati_raw=st.session_state.get(sorgente_key, [])
        st.metric(f"Record in {sorgente_label}", len(dati_raw))
    with c2:
        titolo_report=st.text_input("Titolo Report", value=f"REPORT {sorgente_label.upper()}")
    if not dati_raw:
        st.warning(f"Nessun dato in {sorgente_label}")
        st.stop()
    df_all=pd.DataFrame([{k:v for k,v in r.items() if "Bytes" not in k} for r in dati_raw])
    testo_libero=st.text_input("Cerca testo in TUTTE le colonne")
    df_filt=df_all.copy()
    if testo_libero:
        mask=pd.Series([False]*len(df_filt))
        for col in df_filt.columns:
            try: mask=mask | df_filt[col].astype(str).str.lower().str.contains(testo_libero.lower(), na=False)
            except: pass
        df_filt=df_filt[mask]
    if "Comune" in df_all.columns:
        sel=st.multiselect("Comune", sorted(df_all["Comune"].dropna().unique().astype(str)))
        if sel:
            df_filt=df_filt[df_filt["Comune"].astype(str).isin(sel)]
    if "Squadra" in df_all.columns:
        sel=st.multiselect("Squadra", sorted(df_all["Squadra"].dropna().unique().astype(str)))
        if sel:
            df_filt=df_filt[df_filt["Squadra"].astype(str).isin(sel)]
    st.info(f"Record dopo filtri: {len(df_filt)} / {len(df_all)}")
    sel_cols=st.multiselect("Colonne", list(df_all.columns), default=list(df_all.columns)[:6])
    df_preview=df_filt[sel_cols] if sel_cols else df_filt
    st.dataframe(df_preview, use_container_width=True, height=350)
    st.download_button("Excel Filtrato", to_excel(df_preview), "report.xlsx", use_container_width=True)

elif cur=="Diplomi Attestati":
    hdr_form("DIPLOMI ATTESTATI - 2 Loghi - yf=h-12.5cm")
    nome_dip=st.text_input("Nome Volontario *", value="ALBERTO VIGANO'")
    evento_dip=st.text_input("Evento", value="CAMPO SCUOLA 2026")
    if st.button("Genera PDF Diploma - 2 Loghi", type="primary", use_container_width=True):
        buf=io.BytesIO()
        c=canvas.Canvas(buf, pagesize=A4)
        w,h=A4
        c.setStrokeColor(colors.HexColor("#1a3c6e")); c.setLineWidth(4); c.rect(1*cm,1*cm,w-2*cm,h-2*cm,stroke=1,fill=0)
        c.setFont("Times-Bold",30); c.setFillColor(colors.HexColor("#1A5D1A")); c.drawCentredString(w/2,h-5.8*cm,"ATTESTATO")
        c.setFont("Times-Italic",26); c.setFillColor(colors.HexColor("#1a3c6e")); c.drawCentredString(w/2,h-8*cm,nome_dip.upper())
        yf=h-12.5*cm
        c.setFont("Helvetica",7); c.drawString(1.5*cm,1.5*cm,f"ANA Varese - {evento_dip}")
        c.showPage(); c.save(); buf.seek(0)
        st.download_button(f"Scarica Diploma {nome_dip}", data=buf.getvalue(), file_name=f"Attestato_{nome_dip}.pdf", mime="application/pdf", use_container_width=True, type="primary")

else:
    hdr_form(cur.upper())
    c1,c2=st.columns(2)
    with c1:
        nome=st.text_input(f"Nome {cur} *", key=f"{cur}_nome")
        tipo=st.text_input("Tipo", key=f"{cur}_tipo")
    with c2:
        data_=st.date_input("Data", value=date.today(), key=f"{cur}_data")
        note=st.text_area("Note", key=f"{cur}_note")
    if st.button(f"Salva {cur}", type="primary", use_container_width=True, key=f"save_{cur}"):
        if nome:
            key=cur.lower().replace(" ","_").replace("(con_foto)","").replace("(","").replace(")","").strip()
            kmap={"db_radio":"radio_db","consegna_radio":"consegna_radio","alias_radio":"alias_radio","brogliaccio":"brogliaccio","eventi":"eventi","emergenze":"emergenze","check-in":"checkin","interventi_emergenza":"interventi","mezzi":"mezzi","attrezzature":"attrezzature","libreria_icone":"icone","turni":"turni","chat":"chat","verbali":"verbali","archivio_documenti":"archivio_documenti","geolocalizzazione_hytera_+_anytone":"posizioni_pd785","backup":"backup"}
            k=kmap.get(key, key)
            if k in st.session_state:
                st.session_state[k].append({"Nome":nome,"Tipo":tipo,"Data":str(data_),"Note":note,"DataIns":datetime.now().strftime("%d/%m/%Y")})
                st.success("Salvato")
                st.rerun()
    kmap2={"db radio":"radio_db","consegna radio":"consegna_radio","alias radio":"alias_radio","brogliaccio":"brogliaccio","eventi":"eventi","emergenze":"emergenze","check-in":"checkin","interventi emergenza":"interventi","mezzi":"mezzi","attrezzature":"attrezzature","libreria icone":"icone","turni":"turni","chat":"chat","verbali":"verbali","archivio documenti":"archivio_documenti","geolocalizzazione hytera + anytone":"posizioni_pd785"}
    k2=kmap2.get(cur.lower(), cur.lower().replace(" ","_"))
    if k2 in st.session_state and st.session_state[k2]:
        try:
            df=pd.DataFrame(st.session_state[k2])
            st.dataframe(df, use_container_width=True)
            st.download_button("Excel", to_excel(pd.DataFrame([{kk:vv for kk,vv in r.items() if "Bytes" not in kk} for r in st.session_state[k2]])), f"{k2}.xlsx", use_container_width=True)
        except: pass

st.divider()
st.markdown('<div style="text-align:center;padding:8px;background:linear-gradient(135deg,#1A5D1A,#2e7d32);border-radius:8px;color:white;font-size:12px;">ANA Varese - TUTTO FIX 2026 - By Ezio</div>', unsafe_allow_html=True)