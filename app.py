import streamlit as st
import pandas as pd
from datetime import date, datetime
from io import BytesIO
import os, uuid, requests, json, base64

st.set_page_config(page_title="ANA Varese", page_icon="🟢", layout="wide")

st.markdown("""
<style>
.stApp{background-color:#e8f5e9!important;}
.main.block-container{background-color:white!important;border-radius:18px;padding:25px!important;}
[data-testid="stSidebar"]{background-color:#a5d6a7!important;border-right:4px solid #2e7d32!important;}
.stForm{background-color:#c8e6c9!important;border:3px solid #2e7d32!important;border-radius:15px!important;}
.stButton>button{background-color:#2e7d32!important;color:white!important;font-weight:bold!important;min-height:55px!important;}
div[data-testid="stFormSubmitButton"]>button{background-color:#d32f2f!important;}
.logout-btn>button{background-color:#b71c1c!important;}
.torna-btn>button{background-color:#1565c0!important;}
.compila-btn>button{background-color:#ff9800!important;color:white!important;font-weight:bold!important;border:3px solid #e65100!important;}
.aggancia-btn>button{background-color:#6a1b9a!important;color:white!important;font-weight:bold!important;border:3px solid #4a148c!important;}
.logo-box{border:2px solid #2e7d32;border-radius:10px;padding:10px;text-align:center;background:#f1f8e9;}
.via-desc{background-color:#e3f2fd;border:2px solid #1976d2;border-radius:10px;padding:15px;margin:10px 0;}
.emergenza-box{background-color:#fce4ec;border:3px solid #c62828;border-radius:12px;padding:15px;margin:10px 0;}
.pdf-box{background-color:#fff3e0;border:2px solid #ef6c00;border-radius:10px;padding:15px;margin:10px 0;}
</style>
""", unsafe_allow_html=True)

def load_json(f, default):
    try:
        if os.path.exists(f):
            with open(f,"r",encoding="utf-8") as fh:
                d=json.load(fh)
                if isinstance(d,list):
                    return d
    except:
        pass
    return default

def save_json(f,d):
    try:
        with open(f,"w",encoding="utf-8") as fh:
            json.dump(d,fh,ensure_ascii=False,indent=2)
    except Exception as e:
        st.error(f"Errore {f}: {e}")

def create_pdf_report(df, title, subtitle=""):
    """Crea PDF con anteprima stampa per singolo form"""
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import inch

        buffer = BytesIO()
        # Usa landscape se molte colonne
        if len(df.columns) > 6:
            doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), leftMargin=30, rightMargin=30, topMargin=30, bottomMargin=30)
        else:
            doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40)

        styles = getSampleStyleSheet()
        elements = []

        # Titolo
        title_style = styles['Heading1']
        title_style.textColor = colors.HexColor('#2e7d32')
        elements.append(Paragraph(title, title_style))
        elements.append(Spacer(1, 12))

        if subtitle:
            elements.append(Paragraph(subtitle, styles['Normal']))
            elements.append(Spacer(1, 12))

        elements.append(Paragraph(f"Data stampa: {datetime.now().strftime('%d/%m/%Y %H:%M')} - Totale record: {len(df)}", styles['Normal']))
        elements.append(Spacer(1, 20))

        # Prepara dati per tabella - limita colonne per PDF
        df_pdf = df.copy()
        # Rimuovi colonne troppo lunghe per PDF
        for col in df_pdf.columns:
            if 'PNG' in col or 'Dati' in col or 'CustomPNG' in col:
                df_pdf = df_pdf.drop(columns=[col])

        # Tronca testi lunghi
        for col in df_pdf.columns:
            df_pdf[col] = df_pdf[col].astype(str).apply(lambda x: x[:60] + "..." if len(x) > 60 else x)

        # Limita righe per anteprima PDF (max 50)
        if len(df_pdf) > 50:
            df_pdf = df_pdf.head(50)

        data = [list(df_pdf.columns)] + df_pdf.values.tolist()

        # Crea tabella
        col_width = 500 / len(df_pdf.columns) if len(df_pdf.columns) > 0 else 100
        table = Table(data, colWidths=[col_width]*len(df_pdf.columns) if len(df_pdf.columns) > 0 else [100])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e7d32')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('FONTSIZE', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#e8f5e9')]),
        ]))
        elements.append(table)

        if len(df) > 50:
            elements.append(Spacer(1, 20))
            elements.append(Paragraph(f"... e altri {len(df)-50} record (vedi Excel per completo)", styles['Italic']))

        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()
    except Exception as e:
        # Fallback se reportlab non disponibile - crea PDF semplice con testo
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4
            buffer = BytesIO()
            c = canvas.Canvas(buffer, pagesize=A4)
            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, 800, title)
            c.setFont("Helvetica", 10)
            c.drawString(50, 780, f"Data: {datetime.now().strftime('%d/%m/%Y')} - Record: {len(df)}")
            y = 750
            for idx, row in df.head(30).iterrows():
                if y < 50:
                    c.showPage()
                    y = 800
                text = " | ".join([str(v)[:30] for v in row.values][:5])
                c.drawString(50, y, text[:120])
                y -= 15
            c.save()
            buffer.seek(0)
            return buffer.getvalue()
        except Exception as e2:
            st.error(f"Errore creazione PDF: {e} / {e2}")
            return None

FILE_DATI="dati_volontari.json"
FILE_POST="postazioni.json"
FILE_EMER="emergenze.json"
FILE_RADIO="radio_db.json"
FILE_DIST="dist_radio.json"
FILE_EVENTI="eventi.json"
FILE_CHECK="checkin.json"
FILE_NOMI="mem_nomi.json"

COMUNI_VARESE=["Varese","Busto Arsizio","Gallarate","Saronno","Cassano Magnago","Tradate"]

EMERGENCY_LOGOS = {
 "incendio_boschivo": {"nome": "Incendio Boschivo","emoji": "🔥","png": "https://cdn-icons-png.flaticon.com/512/206/206887.png"},
 "frana": {"nome": "Frana / Smottamento","emoji": "⛰️","png": "https://cdn-icons-png.flaticon.com/512/2942/2942041.png"},
 "caduta_albero": {"nome": "Caduta Albero","emoji": "🌳","png": "https://cdn-icons-png.flaticon.com/512/740/740934.png"},
 "esondazione": {"nome": "Esondazione / Alluvione","emoji": "🌊","png": "https://cdn-icons-png.flaticon.com/512/210/210543.png"},
 "auto_polizia": {"nome": "Auto Polizia","emoji": "🚓","png": "https://cdn-icons-png.flaticon.com/512/3774/3774091.png"},
 "polizia_locale": {"nome": "Polizia Locale","emoji": "👮","png": "https://cdn-icons-png.flaticon.com/512/3106/3106091.png"},
 "vvff": {"nome": "VVFF Vigili del Fuoco","emoji": "🚒","png": "https://cdn-icons-png.flaticon.com/512/599/599502.png"},
 "protezione_civile": {"nome": "Mezzi Protezione Civile","emoji": "🦺","png": "https://cdn-icons-png.flaticon.com/512/599/599505.png"},
 "ambulanza": {"nome": "Ambulanza 118","emoji": "🚑","png": "https://cdn-icons-png.flaticon.com/512/2751/2751790.png"},
 "prima_accoglienza": {"nome": "Area Prima Accoglienza","emoji": "⛺","png": "https://cdn-icons-png.flaticon.com/512/109/109345.png"},
}

@st.cache_data(ttl=86400)
def load_comuni_italia():
    try:
        url="https://raw.githubusercontent.com/matteocontrini/comuni-json/master/comuni.json"
        r=requests.get(url,timeout=10)
        if r.status_code==200:
            data=r.json()
            comuni=sorted([c["nome"] for c in data])
            top=[c for c in COMUNI_VARESE if c in comuni]
            altri=[c for c in comuni if c not in top]
            return top+altri
    except:
        pass
    return sorted(list(set(COMUNI_VARESE)))

@st.cache_data(ttl=3600, show_spinner=False)
def get_vie_comune(comune):
    headers={"User-Agent":"ANA-Varese-App"}
    try:
        nom_url="https://nominatim.openstreetmap.org/search"
        params={"q":f"{comune}, Italy","format":"json","limit":3}
        r=requests.get(nom_url,params=params,headers=headers,timeout=10)
        if r.status_code==200 and r.json():
            for res in r.json():
                osm_type=res.get("osm_type")
                osm_id=res.get("osm_id")
                if osm_type=="relation" and osm_id:
                    area_id=3600000000+int(osm_id)
                    try:
                        q=f'[out:json][timeout:30];area({area_id})->.a;(way(area.a)["highway"]["name"];);out 3000;'
                        url="https://overpass-api.de/api/interpreter"
                        r2=requests.post(url,data={"data":q},timeout=30)
                        if r2.status_code==200:
                            data=r2.json()
                            vie=[]
                            for el in data.get("elements",[]):
                                if "tags" in el and "name" in el["tags"]:
                                    nome=el["tags"]["name"]
                                    if 2<len(nome)<80:
                                        vie.append(nome.strip())
                            vie=sorted(list(set(vie)))
                            if len(vie)>=5:
                                return ["-- Seleziona Via --"]+vie
                    except:
                        pass
    except:
        pass
    return ["-- Seleziona Via --","Via Roma","Via Garibaldi","Via Milano","Via Sacco","Via Verdi","Via Dante"]

def reverse_geocode_dettagliato(lat, lon):
    try:
        url=f"https://nominatim.openstreetmap.org/reverse"
        params={"format":"json","lat":lat,"lon":lon,"zoom":18,"addressdetails":1}
        headers={"User-Agent":"ANA-Varese-App"}
        r=requests.get(url,params=params,headers=headers,timeout=10)
        if r.status_code==200:
            data=r.json()
            display_name=data.get("display_name","")
            addr=data.get("address",{})
            road=addr.get("road") or addr.get("pedestrian") or ""
            house=addr.get("house_number") or ""
            city=addr.get("city") or addr.get("town") or addr.get("village") or ""
            postcode=addr.get("postcode") or ""
            county=addr.get("county") or ""
            if road and city:
                if house:
                    desc_via_comune=f"{road}, {house} - {postcode} {city} ({county})"
                else:
                    desc_via_comune=f"{road} - {postcode} {city} ({county})"
                desc_completa=f"📍 {display_name}"
                return city, road, desc_via_comune, desc_completa, addr
            else:
                return city, road, display_name, display_name, addr
    except:
        pass
    return "", "", "", "", {}

if "authenticated" not in st.session_state:
    st.session_state.authenticated=False
if "dati" not in st.session_state:
    st.session_state.dati=load_json(FILE_DATI,[])
if "postazioni" not in st.session_state:
    st.session_state.postazioni=load_json(FILE_POST,[])
if "emergenze_lista" not in st.session_state:
    st.session_state.emergenze_lista=load_json(FILE_EMER,[])
if "radio_db" not in st.session_state:
    st.session_state.radio_db=load_json(FILE_RADIO,[])
if "dist_radio" not in st.session_state:
    st.session_state.dist_radio=load_json(FILE_DIST,[])
if "eventi_lista" not in st.session_state:
    st.session_state.eventi_lista=load_json(FILE_EVENTI,[])
if "checkin_lista" not in st.session_state:
    st.session_state.checkin_lista=load_json(FILE_CHECK,[])
if "mem_nomi" not in st.session_state:
    st.session_state.mem_nomi=load_json(FILE_NOMI,["Mario Rossi","Luigi Bianchi"])
if "menu_scelta" not in st.session_state:
    st.session_state.menu_scelta="Dashboard"
if "last_postazione" not in st.session_state:
    st.session_state.last_postazione=None
if "clicked_lat" not in st.session_state:
    st.session_state.clicked_lat=""
if "clicked_lon" not in st.session_state:
    st.session_state.clicked_lon=""
if "clicked_comune" not in st.session_state:
    st.session_state.clicked_comune=""
if "clicked_via" not in st.session_state:
    st.session_state.clicked_via=""
if "clicked_desc_via" not in st.session_state:
    st.session_state.clicked_desc_via=""
if "clicked_desc_completa" not in st.session_state:
    st.session_state.clicked_desc_completa=""
if "selected_pointer" not in st.session_state:
    st.session_state.selected_pointer="📍 Default Rosso"
if "selected_custom_b64" not in st.session_state:
    st.session_state.selected_custom_b64=""
if "form_lat" not in st.session_state:
    st.session_state.form_lat=""
if "form_lon" not in st.session_state:
    st.session_state.form_lon=""
if "form_comune" not in st.session_state:
    st.session_state.form_comune=""
if "form_via" not in st.session_state:
    st.session_state.form_via=""
if "form_desc" not in st.session_state:
    st.session_state.form_desc=""
if "emergenza_agganciata" not in st.session_state:
    st.session_state.emergenza_agganciata=None

def torna(suffix=""):
    st.markdown('<div class="torna-btn">', unsafe_allow_html=True)
    k=f"back_{suffix}_{uuid.uuid4().hex[:6]}"
    if st.button("🏠 Torna alla Dashboard",key=k,use_container_width=True):
        st.session_state.menu_scelta="Dashboard"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

def header_loghi():
    c1,c2,c3=st.columns(3)
    if os.path.exists("logo.png"):
        c1.image("logo.png",width=80)
    if os.path.exists("logo2.png"):
        c2.image("logo2.png",width=80)
    if os.path.exists("logo_pc_lombardia.png"):
        c3.image("logo_pc_lombardia.png",width=80)

if not st.session_state.authenticated:
    st.markdown("<style>[data-testid='stSidebar']{display:none;}</style>", unsafe_allow_html=True)
    header_loghi()
    st.markdown("<h2 style='text-align:center; color:#2e7d32;'>Accesso - admin / ana2024</h2>", unsafe_allow_html=True)
    c1,c2,c3=st.columns([1,2,1])
    with c2:
        with st.form("login"):
            u=st.text_input("Username",value="admin")
            p=st.text_input("Password",type="password",value="ana2024")
            if st.form_submit_button("Accedi",use_container_width=True):
                if u=="admin" and p=="ana2024":
                    st.session_state.authenticated=True
                    st.rerun()
    st.stop()

header_loghi()
st.divider()

with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png",width=80)
    st.markdown("### MENU ANA VARESE")
    opzioni=["Dashboard","Emergenze con Loghi","Mappa Postazioni","Volontari","DB Radio","Distribuzione Radio","Eventi","Check-in","Tabella Interventi Emergenza","Backup"]
    sel=st.radio("Seleziona",opzioni,index=opzioni.index(st.session_state.menu_scelta) if st.session_state.menu_scelta in opzioni else 0)
    if sel!=st.session_state.menu_scelta:
        st.session_state.menu_scelta=sel
        st.rerun()
    st.divider()
    st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
    if st.button("🚪 LOGOUT - Esci",use_container_width=True,key="logout_btn"):
        st.session_state.authenticated=False
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.divider()
    st.caption("💾 Dati memorizzati!")

scelta=st.session_state.menu_scelta
st.markdown(f"## {scelta}")
st.divider()
COMUNI_TUTTI=load_comuni_italia()
MIME_SHORT="application/octet-stream"

if scelta=="Dashboard":
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Emergenze",len(st.session_state.emergenze_lista))
    c2.metric("Postazioni",len(st.session_state.postazioni))
    c3.metric("Volontari",len(st.session_state.dati))
    c4.metric("Radio",len(st.session_state.radio_db))
    st.info("✅ Dati memorizzati su disco!")

elif scelta=="Emergenze con Loghi":
    torna("top_em")
    st.markdown("### 🚨 EMERGENZA CON LOGHI VERI PNG")
    c1,c2=st.columns(2)
    with c1:
        comune=st.selectbox("Comune *",COMUNI_TUTTI,key="comune_em")
    with c2:
        with st.spinner(f"Carico vie di {comune}..."):
            vie=get_vie_comune(comune)
        via=st.selectbox(f"Via * ({len(vie)-1} vie)",vie,key="via_em")
        if via=="-- Seleziona Via --":
            via_man=st.text_input("Via manuale",key="via_man_em")
            via_f=via_man if via_man else via
        else:
            via_f=via
    st.markdown("#### 🎨 SCEGLI LOGO VERO PNG")
    col_logo1,col_logo2,col_logo3=st.columns([2,1,1])
    with col_logo1:
        logo_keys=list(EMERGENCY_LOGOS.keys())
        logo_names=[f"{EMERGENCY_LOGOS[k]['emoji']} {EMERGENCY_LOGOS[k]['nome']}" for k in logo_keys]
        sel_logo_idx=st.selectbox("Tipo Emergenza *",range(len(logo_keys)),format_func=lambda i: logo_names[i],key="logo_sel")
        sel_logo_key=logo_keys[sel_logo_idx]
        sel_logo_info=EMERGENCY_LOGOS[sel_logo_key]
    with col_logo2:
        st.markdown('<div class="logo-box">', unsafe_allow_html=True)
        try:
            st.image(sel_logo_info['png'],width=80)
        except:
            st.markdown(f"# {sel_logo_info['emoji']}")
        st.markdown('</div>', unsafe_allow_html=True)
    with col_logo3:
        custom_logo_upload=st.file_uploader("Carica PNG",type=["png","jpg","jpeg"],key="custom_logo")
        custom_b64=""
        if custom_logo_upload:
            st.image(custom_logo_upload,width=80)
            custom_b64=base64.b64encode(custom_logo_upload.getvalue()).decode()
    with st.form("form_em_completo"):
        cc1,cc2,cc3=st.columns(3)
        with cc1:
            data_em=st.date_input("Data *",value=date.today())
            ora_em=st.time_input("Ora *",value=datetime.now().time())
            gravita=st.selectbox("Gravità *",["Bassa","Media","Alta","Critica"],index=1)
        with cc2:
            stato=st.selectbox("Stato *",["Aperta","In Corso","Chiusa","Archiviata"],index=0)
            civico=st.text_input("Civico")
            coord=st.text_input("Coordinatore *",value="ANA Varese")
            lat_em=st.text_input("Latitudine (per mappa)",placeholder="45.8205")
            lon_em=st.text_input("Longitudine (per mappa)",placeholder="8.8255")
        with cc3:
            volontari_sel=st.multiselect("Volontari",st.session_state.mem_nomi)
            mezzi=st.text_input("Mezzi Utilizzati")
        desc=st.text_area("Descrizione *",value=f"{sel_logo_info['nome']} a {comune} - {via_f}",height=100)
        note=st.text_area("Note",height=80)
        if st.form_submit_button("💾 SALVA EMERGENZA E AGGANCIA A MAPPA",use_container_width=True,type="primary"):
            if via_f!="-- Seleziona Via --" and via_f!="" and desc!="":
                if custom_b64:
                    logo_png_to_save=f"data:image/png;base64,{custom_b64}"
                else:
                    logo_png_to_save=sel_logo_info['png']
                new_em={"ID":str(uuid.uuid4())[:8],"Data":str(data_em),"Ora":str(ora_em),"Logo":sel_logo_info['emoji'],"LogoNome":sel_logo_info['nome'],"LogoPNG":logo_png_to_save,"Comune":comune,"Via":via_f,"Civico":civico,"Tipo":sel_logo_info['nome'],"Gravità":gravita,"Stato":stato,"Descrizione":desc,"Volontari":", ".join(volontari_sel),"Mezzi":mezzi,"Coordinatore":coord,"Note":note,"Latitudine":lat_em,"Longitudine":lon_em}
                st.session_state.emergenze_lista.append(new_em)
                save_json(FILE_EMER,st.session_state.emergenze_lista)
                st.success(f"✅ Emergenza salvata!")
                st.rerun()
    if st.session_state.emergenze_lista:
        st.dataframe(pd.DataFrame(st.session_state.emergenze_lista),use_container_width=True)
    torna("bottom_em")

elif scelta=="Mappa Postazioni":
    torna("top_map")
    st.markdown("### 🗺️ MAPPA - AGGANCIO EMERGENZA CON DATI")
    st.info("Seleziona emergenza: dati si agganciano in automatico al form mappa!")
    st.markdown("#### 🔗 AGGANCIA EMERGENZA ESISTENTE")
    if st.session_state.emergenze_lista:
        emergenze_options=["-- Nessuna --"]+[f"{e.get('ID','')} - {e.get('Data','')} - {e.get('LogoNome','')} - {e.get('Comune','')} {e.get('Via','')} - {e.get('Gravità','')}" for e in st.session_state.emergenze_lista]
        sel_em_idx=st.selectbox("Seleziona Emergenza",range(len(emergenze_options)),format_func=lambda i: emergenze_options[i],key="sel_emergenza_aggancio")
        if sel_em_idx>0:
            em_sel=st.session_state.emergenze_lista[sel_em_idx-1]
            st.markdown('<div class="emergenza-box">', unsafe_allow_html=True)
            c1,c2=st.columns([1,3])
            with c1:
                try:
                    st.image(em_sel.get("LogoPNG",""),width=70)
                except:
                    st.markdown(f"## {em_sel.get('Logo','🚨')}")
            with c2:
                st.markdown(f"**{em_sel.get('LogoNome','')} - {em_sel.get('Comune','')} {em_sel.get('Via','')}**")
                st.caption(f"{em_sel.get('Data','')} | {em_sel.get('Gravità','')} | {em_sel.get('Descrizione','')[:100]}")
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<div class="aggancia-btn">', unsafe_allow_html=True)
            if st.button(f"🔗 AGGANCIA DATI EMERGENZA AL FORM MAPPA",use_container_width=True,key="aggancia_btn"):
                st.session_state.emergenza_agganciata=em_sel
                st.session_state.form_comune=em_sel.get("Comune","")
                st.session_state.form_via=em_sel.get("Via","")
                st.session_state.form_lat=em_sel.get("Latitudine","") or st.session_state.clicked_lat
                st.session_state.form_lon=em_sel.get("Longitudine","") or st.session_state.clicked_lon
                st.session_state.form_desc=f"Postazione per emergenza {em_sel.get('LogoNome','')} - {em_sel.get('Descrizione','')} - {em_sel.get('Comune','')} {em_sel.get('Via','')}"
                tipo_em=em_sel.get("Tipo","").lower()
                if "incendio" in tipo_em:
                    st.session_state.selected_pointer="🔥 Incendio"
                elif "frana" in tipo_em:
                    st.session_state.selected_pointer="🚨 Emergenza"
                elif "alluvione" in tipo_em or "esondazione" in tipo_em:
                    st.session_state.selected_pointer="🌊 Alluvione"
                elif "ambulanza" in tipo_em:
                    st.session_state.selected_pointer="🚑 Sanitario"
                else:
                    st.session_state.selected_pointer="🚨 Emergenza"
                st.success(f"✅ Dati emergenza agganciati!")
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.warning("Nessuna emergenza - Crea prima emergenza")
    if st.session_state.emergenza_agganciata:
        st.markdown('<div class="emergenza-box">', unsafe_allow_html=True)
        em=st.session_state.emergenza_agganciata
        st.markdown(f"**🔗 Emergenza agganciata:** {em.get('Logo','')} {em.get('LogoNome','')} - ID {em.get('ID','')}")
        st.markdown('</div>', unsafe_allow_html=True)
    st.divider()
    st.markdown("#### 1️⃣ Scegli il puntatore PNG")
    cc1,cc2,cc3=st.columns([2,1,1])
    with cc1:
        tipo_puntatore=st.selectbox("Tipo Puntatore *",["📍 Default Rosso","🚨 Emergenza","🏠 Sede ANA","👤 Volontario","🔥 Incendio","🌊 Alluvione","🚑 Sanitario","📻 Radio","⭐ Personalizzato PNG"],key="pointer_select")
        st.session_state.selected_pointer=tipo_puntatore
    with cc2:
        st.markdown('<div class="logo-box">', unsafe_allow_html=True)
        st.markdown(f"**{tipo_puntatore}**")
        if tipo_puntatore=="⭐ Personalizzato PNG" and st.session_state.selected_custom_b64:
            st.image(f"data:image/png;base64,{st.session_state.selected_custom_b64}",width=60)
        else:
            st.markdown(f"# {tipo_puntatore[:2]}")
        st.markdown('</div>', unsafe_allow_html=True)
    with cc3:
        png_upload=st.file_uploader("Carica PNG tuo",type=["png","jpg","jpeg"],key="png_up")
        if png_upload:
            st.image(png_upload,width=60)
            b64=base64.b64encode(png_upload.getvalue()).decode()
            st.session_state.selected_custom_b64=b64
            st.session_state["custom_png_b64"]=b64
    st.divider()
    st.markdown("#### 2️⃣ Clicca sulla mappa")
    try:
        import folium
        from streamlit_folium import st_folium
        from folium.plugins import Fullscreen
        if st.session_state.last_postazione:
            try:
                lat_c=float(str(st.session_state.last_postazione["Latitudine"]).replace(",","."))
                lon_c=float(str(st.session_state.last_postazione["Longitudine"]).replace(",","."))
                zoom=14
            except:
                lat_c=45.8205; lon_c=8.8255; zoom=12
        elif st.session_state.form_lat and st.session_state.form_lon:
            try:
                lat_c=float(str(st.session_state.form_lat).replace(",","."))
                lon_c=float(str(st.session_state.form_lon).replace(",","."))
                zoom=15
            except:
                lat_c=45.8205; lon_c=8.8255; zoom=12
        else:
            lat_c=45.8205; lon_c=8.8255; zoom=12
        m_click=folium.Map(location=[lat_c,lon_c],zoom_start=zoom,tiles="OpenStreetMap")
        Fullscreen(position="topleft").add_to(m_click)
        if st.session_state.postazioni:
            df_temp=pd.DataFrame(st.session_state.postazioni)
            for idx, r in df_temp.iterrows():
                try:
                    la=float(str(r["Latitudine"]).replace(",","."))
                    lo=float(str(r["Longitudine"]).replace(",","."))
                    punt=r.get("Puntatore","📍 Default Rosso")
                    cb64=r.get("CustomPNG","")
                    em_abb=r.get("EmergenzaAbbinata","")
                    if punt=="⭐ Personalizzato PNG" and cb64:
                        icon_url=f"data:image/png;base64,{cb64}"
                        icon=folium.CustomIcon(icon_url,icon_size=(40,40),icon_anchor=(20,40))
                        folium.Marker([la,lo],popup=f"{r['Postazione']}<br>Emerg: {em_abb}",icon=icon).add_to(m_click)
                    else:
                        color_map={"📍 Default Rosso":"red","🚨 Emergenza":"red","🏠 Sede ANA":"green","👤 Volontario":"blue","🔥 Incendio":"orange","🌊 Alluvione":"blue","🚑 Sanitario":"white","📻 Radio":"cadetblue"}
                        color=color_map.get(punt,"red")
                        folium.Marker([la,lo],popup=f"{r['Postazione']}<br>Emerg: {em_abb}",icon=folium.Icon(color=color,icon="info-sign")).add_to(m_click)
                except:
                    pass
        if st.session_state.clicked_lat and st.session_state.clicked_lon:
            try:
                clat=float(st.session_state.clicked_lat)
                clon=float(st.session_state.clicked_lon)
                sel_ptr=st.session_state.selected_pointer
                sel_b64=st.session_state.selected_custom_b64
                if sel_ptr=="⭐ Personalizzato PNG" and sel_b64:
                    icon_url=f"data:image/png;base64,{sel_b64}"
                    icon=folium.CustomIcon(icon_url,icon_size=(50,50),icon_anchor=(25,50))
                    folium.Marker([clat,clon],popup=f"🎯 NUOVA",icon=icon).add_to(m_click)
                else:
                    color_map={"📍 Default Rosso":"red","🚨 Emergenza":"red","🏠 Sede ANA":"green","👤 Volontario":"blue","🔥 Incendio":"orange","🌊 Alluvione":"blue","🚑 Sanitario":"white","📻 Radio":"cadetblue"}
                    color=color_map.get(sel_ptr,"red")
                    folium.Marker([clat,clon],popup=f"🎯 NUOVA",icon=folium.Icon(color=color,icon="star",prefix="fa")).add_to(m_click)
                folium.CircleMarker([clat,clon],radius=25,color="yellow",fill=False,weight=4).add_to(m_click)
            except:
                pass
        if st.session_state.emergenza_agganciata and st.session_state.emergenza_agganciata.get("Latitudine") and st.session_state.emergenza_agganciata.get("Longitudine"):
            try:
                em_lat=float(str(st.session_state.emergenza_agganciata.get("Latitudine")).replace(",","."))
                em_lon=float(str(st.session_state.emergenza_agganciata.get("Longitudine")).replace(",","."))
                em=st.session_state.emergenza_agganciata
                folium.Marker([em_lat,em_lon],popup=f"🚨 EMERGENZA: {em.get('LogoNome','')}",icon=folium.Icon(color="red",icon="warning-sign")).add_to(m_click)
                folium.Circle([em_lat,em_lon],radius=100,color="red",fill=True,fill_opacity=0.2).add_to(m_click)
            except:
                pass
        st.markdown("**Clicca dove vuoi - Appare PNG scelto! ⛶ fullscreen**")
        map_data=st_folium(m_click,width=800,height=600,returned_objects=["last_clicked"])
        if map_data and map_data.get("last_clicked"):
            clicked_lat=map_data["last_clicked"]["lat"]
            clicked_lon=map_data["last_clicked"]["lng"]
            st.session_state.clicked_lat=str(clicked_lat)
            st.session_state.clicked_lon=str(clicked_lon)
            with st.spinner("Recupero via + comune..."):
                city, road, desc_via_comune, desc_completa, addr_dict=reverse_geocode_dettagliato(clicked_lat, clicked_lon)
                st.session_state.clicked_comune=city
                st.session_state.clicked_via=road
                st.session_state.clicked_desc_via=desc_via_comune
                st.session_state.clicked_desc_completa=desc_completa
                st.session_state.form_lat=str(clicked_lat)
                st.session_state.form_lon=str(clicked_lon)
                st.session_state.form_comune=city
                st.session_state.form_via=road
                st.session_state.form_desc=desc_completa
            st.success(f"✅ {desc_via_comune}")
            st.rerun()
    except ImportError:
        st.warning("Installa folium")
    if st.session_state.clicked_lat and st.session_state.clicked_lon:
        st.divider()
        st.markdown("#### 📍 Dati presi da mappa o emergenza")
        st.markdown('<div class="via-desc">', unsafe_allow_html=True)
        st.markdown(f"**Via + Comune:** {st.session_state.clicked_desc_via or st.session_state.form_desc}")
        st.markdown(f"**Coordinate:** Lat {st.session_state.clicked_lat} Lon {st.session_state.clicked_lon}")
        if st.session_state.emergenza_agganciata:
            st.markdown(f"**Emergenza:** {st.session_state.emergenza_agganciata.get('LogoNome','')} ID {st.session_state.emergenza_agganciata.get('ID','')}")
        st.markdown('</div>', unsafe_allow_html=True)
        c_info1,c_info2,c_info3,c_info4=st.columns(4)
        c_info1.metric("Lat",st.session_state.clicked_lat)
        c_info2.metric("Lon",st.session_state.clicked_lon)
        c_info3.metric("Comune",st.session_state.clicked_comune or st.session_state.form_comune or "Non rilevato")
        c_info4.metric("Via",st.session_state.clicked_via or st.session_state.form_via or "Non rilevata")
        st.markdown('<div class="compila-btn">', unsafe_allow_html=True)
        if st.button("🔄 COMPILA MASCHERA CON DATI MAPPA/EMERGENZA",use_container_width=True,key="compila_maschera"):
            st.session_state.form_lat=st.session_state.clicked_lat
            st.session_state.form_lon=st.session_state.clicked_lon
            st.session_state.form_comune=st.session_state.clicked_comune
            st.session_state.form_via=st.session_state.clicked_via
            st.session_state.form_desc=st.session_state.clicked_desc_completa
            st.success("✅ Maschera compilata!")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.divider()
    st.markdown("#### 3️⃣ Maschera Postazione - Dati agganciati da Emergenza")
    c1,c2=st.columns(2)
    with c1:
        if st.session_state.form_comune:
            comune_val=st.session_state.form_comune
            if comune_val in COMUNI_TUTTI:
                idx_com=COMUNI_TUTTI.index(comune_val)
                comune=st.selectbox("Comune * (agganciato)",COMUNI_TUTTI,index=idx_com,key="comune_map_final")
            else:
                comune=st.selectbox("Comune *",COMUNI_TUTTI,key="comune_map_final")
                if comune_val:
                    comune=comune_val
        else:
            comune=st.selectbox("Comune *",COMUNI_TUTTI,key="comune_map_final")
    with c2:
        with st.spinner(f"Carico vie di {comune}..."):
            vie=get_vie_comune(comune)
        if st.session_state.form_via and st.session_state.form_via in vie:
            idx_via=vie.index(st.session_state.form_via)
            via=st.selectbox(f"Via * ({len(vie)-1} vie) - agganciata",vie,index=idx_via,key="via_map_final")
        else:
            via=st.selectbox(f"Via * ({len(vie)-1} vie)",vie,key="via_map_final")
        if via=="-- Seleziona Via --":
            via_man=st.text_input("Via manuale (agganciata)",value=st.session_state.form_via,key="via_man_map_final")
            via_f=via_man if via_man else via
        else:
            via_f=via
    if st.session_state.form_desc:
        st.markdown('<div class="via-desc">', unsafe_allow_html=True)
        st.markdown(f"**Descrizione:** {st.session_state.form_desc}")
        st.markdown('</div>', unsafe_allow_html=True)
    with st.form("form_post_finale"):
        st.markdown("#### Dati Postazione + Emergenza Agganciata")
        nome=st.text_input("Nome Postazione *",value=f"Postazione per {st.session_state.form_comune} {st.session_state.form_via}" if st.session_state.form_comune else "",placeholder="Es. Postazione 1")
        cc1,cc2=st.columns(2)
        with cc1:
            lat_final=st.text_input("Latitudine * (agganciata)",value=st.session_state.form_lat,placeholder="Da emergenza o click",key="lat_final")
            lon_final=st.text_input("Longitudine * (agganciata)",value=st.session_state.form_lon,placeholder="Da emergenza o click",key="lon_final")
        with cc2:
            resp=st.text_input("Responsabile",placeholder="Nome responsabile")
            st.markdown(f"**Puntatore:** {st.session_state.selected_pointer}")
            if st.session_state.emergenza_agganciata:
                st.markdown(f"**Emergenza:** {st.session_state.emergenza_agganciata.get('LogoNome','')}")
        desc_via_final=st.text_area("Descrizione Via + Comune + Emergenza",value=st.session_state.form_desc,height=80,key="desc_via_final")
        st.info(f"Comune: {comune} | Via: {via_f} | Lat: {lat_final} | Lon: {lon_final}")
        if st.form_submit_button("➕ SALVA POSTAZIONE AGGANCIATA AD EMERGENZA",use_container_width=True,type="primary"):
            final_lat=lat_final or st.session_state.form_lat or st.session_state.clicked_lat
            final_lon=lon_final or st.session_state.form_lon or st.session_state.clicked_lon
            final_comune=comune or st.session_state.form_comune or st.session_state.clicked_comune
            final_via=via_f or st.session_state.form_via or st.session_state.clicked_via
            final_desc=desc_via_final or st.session_state.form_desc or st.session_state.clicked_desc_completa
            if nome and final_lat and final_lon:
                custom_b64=st.session_state.selected_custom_b64 if st.session_state.selected_pointer=="⭐ Personalizzato PNG" else ""
                emergenza_id=""
                emergenza_nome=""
                if st.session_state.emergenza_agganciata:
                    emergenza_id=st.session_state.emergenza_agganciata.get("ID","")
                    emergenza_nome=st.session_state.emergenza_agganciata.get("LogoNome","")+" - "+st.session_state.emergenza_agganciata.get("Comune","")+" "+st.session_state.emergenza_agganciata.get("Via","")
                new_post={"Postazione":nome,"Comune":final_comune,"Via":final_via,"Latitudine":final_lat,"Longitudine":final_lon,"Responsabile":resp,"Puntatore":st.session_state.selected_pointer,"CustomPNG":custom_b64,"DescrizioneVia":final_desc,"EmergenzaAbbinata":emergenza_id,"EmergenzaNome":emergenza_nome}
                st.session_state.postazioni.append(new_post)
                save_json(FILE_POST,st.session_state.postazioni)
                st.session_state.last_postazione=new_post
                st.session_state.clicked_lat=""; st.session_state.clicked_lon=""; st.session_state.clicked_comune=""; st.session_state.clicked_via=""
                st.session_state.clicked_desc_via=""; st.session_state.clicked_desc_completa=""
                st.session_state.form_lat=""; st.session_state.form_lon=""; st.session_state.form_comune=""; st.session_state.form_via=""; st.session_state.form_desc=""
                st.session_state.emergenza_agganciata=None
                st.success(f"✅ {nome} salvata agganciata a emergenza {emergenza_id}!")
                st.rerun()
            else:
                st.error("Compila Nome e Lat/Lon!")
    if st.session_state.postazioni:
        df=pd.DataFrame(st.session_state.postazioni)
        st.markdown(f"### 📍 Mappa Finale - {len(df)} Postazioni")
        tipo_mappa=st.selectbox("Tipo Mappa",["OpenStreetMap","Google Stradale","Google Satellite"],key="tipo_mappa")
        try:
            import folium
            from streamlit_folium import st_folium
            from folium.plugins import Fullscreen
            if st.session_state.last_postazione:
                try:
                    lat_c=float(str(st.session_state.last_postazione["Latitudine"]).replace(",","."))
                    lon_c=float(str(st.session_state.last_postazione["Longitudine"]).replace(",","."))
                    zoom=15
                except:
                    lat_c=45.8205; lon_c=8.8255; zoom=12
            else:
                lat_c=45.8205; lon_c=8.8255; zoom=12
            if tipo_mappa=="OpenStreetMap":
                m=folium.Map(location=[lat_c,lon_c],zoom_start=zoom,tiles="OpenStreetMap")
            else:
                m=folium.Map(location=[lat_c,lon_c],zoom_start=zoom,tiles=None)
                if tipo_mappa=="Google Stradale":
                    url="https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}"
                    nome_t="Google Stradale"
                else:
                    url="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}"
                    nome_t="Google Satellite"
                folium.TileLayer(url,attr="Google",name=nome_t,max_zoom=20).add_to(m)
            Fullscreen(position="topleft").add_to(m)
            for idx, r in df.iterrows():
                try:
                    la=float(str(r["Latitudine"]).replace(",","."))
                    lo=float(str(r["Longitudine"]).replace(",","."))
                    popup_text=f"<b>{r['Postazione']}</b><br>{r['Comune']} - {r['Via']}<br>Emerg: {r.get('EmergenzaNome','Nessuna')}"
                    puntatore=r.get("Puntatore","📍 Default Rosso")
                    custom
