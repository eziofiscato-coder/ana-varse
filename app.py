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
.selezione-box{background-color:#f3e5f5;border:2px solid #7b1fa2;border-radius:12px;padding:15px;margin:10px 0;}
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
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        buffer = BytesIO()
        if len(df.columns) > 6:
            doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), leftMargin=30, rightMargin=30, topMargin=30, bottomMargin=30)
        else:
            doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40)
        styles = getSampleStyleSheet()
        elements = []
        title_style = styles['Heading1']
        title_style.textColor = colors.HexColor('#2e7d32')
        elements.append(Paragraph(title, title_style))
        elements.append(Spacer(1, 12))
        if subtitle:
            elements.append(Paragraph(subtitle, styles['Normal']))
            elements.append(Spacer(1, 12))
        elements.append(Paragraph(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')} - Record: {len(df)} - Colonne: {', '.join(df.columns[:8])}", styles['Normal']))
        elements.append(Spacer(1, 20))
        df_pdf = df.copy()
        for col in list(df_pdf.columns):
            if 'PNG' in col or 'CustomPNG' in col:
                df_pdf = df_pdf.drop(columns=[col])
        for col in df_pdf.columns:
            df_pdf[col] = df_pdf[col].astype(str).apply(lambda x: x[:50] + "..." if len(x) > 50 else x)
        if len(df_pdf) > 50:
            df_pdf = df_pdf.head(50)
        if len(df_pdf.columns) > 8:
            df_pdf = df_pdf.iloc[:, :8]
        data = [list(df_pdf.columns)] + df_pdf.values.tolist()
        col_width = 500 / len(df_pdf.columns) if len(df_pdf.columns) > 0 else 100
        table = Table(data, colWidths=[col_width]*len(df_pdf.columns) if len(df_pdf.columns) > 0 else [100])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e7d32')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 7),
            ('FONTSIZE', (0, 1), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(table)
        if len(df) > 50:
            elements.append(Spacer(1, 20))
            elements.append(Paragraph(f"... altri {len(df)-50} record", styles['Italic']))
        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()
    except Exception as e:
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4
            buffer = BytesIO()
            c = canvas.Canvas(buffer, pagesize=A4)
            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, 800, title)
            c.setFont("Helvetica", 8)
            c.drawString(50, 780, f"Data: {datetime.now()} - Record: {len(df)}")
            y = 750
            for idx, row in df.head(30).iterrows():
                if y < 50:
                    c.showPage()
                    y = 800
                text = " | ".join([str(v)[:25] for v in row.values][:6])
                c.drawString(50, y, text[:130])
                y -= 12
            c.save()
            buffer.seek(0)
            return buffer.getvalue()
        except Exception as e2:
            st.error(f"Errore PDF: {e} / {e2}")
            return None

FILE_DATI="dati_volontari.json"
FILE_POST="postazioni.json"
FILE_EMER="emergenze.json"
FILE_RADIO="radio_db.json"
FILE_DIST="dist_radio.json"
FILE_EVENTI="eventi.json"
FILE_CHECK="checkin.json"
FILE_NOMI="mem_nomi.json"

COMUNI_VARESE=["Varese","Busto Arsizio","Gallarate","Saronno","Cassano Magnago","Tradate","Malnate","Luino","Somma Lombardo","Tradate"]

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
    c5,c6,c7,c8=st.columns(4)
    c5.metric("Eventi",len(st.session_state.eventi_lista))
    c6.metric("Check-in",len(st.session_state.checkin_lista))
    c7.metric("Distr Radio",len(st.session_state.dist_radio))
    c8.metric("Nomi",len(st.session_state.mem_nomi))
    st.info("✅ Sistema completo 900+ righe - Backup con selezione dati!")

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
    st.markdown("#### 🎨 SCEGLI LOGO")
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
            lat_em=st.text_input("Latitudine",placeholder="45.8205")
            lon_em=st.text_input("Longitudine",placeholder="8.8255")
        with cc3:
            volontari_sel=st.multiselect("Volontari",st.session_state.mem_nomi)
            mezzi=st.text_input("Mezzi Utilizzati")
        desc=st.text_area("Descrizione *",value=f"{sel_logo_info['nome']} a {comune} - {via_f}",height=100)
        note=st.text_area("Note",height=80)
        if st.form_submit_button("💾 SALVA EMERGENZA",use_container_width=True,type="primary"):
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
    st.markdown("### 🗺️ MAPPA POSTAZIONI - AGGANCIO EMERGENZA")
    st.markdown("#### 🔗 AGGANCIA EMERGENZA")
    if st.session_state.emergenze_lista:
        emergenze_options=["-- Nessuna --"]+[f"{e.get('ID','')} - {e.get('Data','')} - {e.get('LogoNome','')} - {e.get('Comune','')} {e.get('Via','')}" for e in st.session_state.emergenze_lista]
        sel_em_idx=st.selectbox("Seleziona Emergenza",range(len(emergenze_options)),format_func=lambda i: emergenze_options[i],key="sel_emergenza_aggancio")
        if sel_em_idx>0:
            em_sel=st.session_state.emergenze_lista[sel_em_idx-1]
            st.markdown('<div class="emergenza-box">', unsafe_allow_html=True)
            st.markdown(f"**{em_sel.get('LogoNome','')} - {em_sel.get('Comune','')} {em_sel.get('Via','')}**")
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<div class="aggancia-btn">', unsafe_allow_html=True)
            if st.button(f"🔗 AGGANCIA DATI EMERGENZA AL FORM",use_container_width=True,key="aggancia_btn"):
                st.session_state.emergenza_agganciata=em_sel
                st.session_state.form_comune=em_sel.get("Comune","")
                st.session_state.form_via=em_sel.get("Via","")
                st.session_state.form_lat=em_sel.get("Latitudine","")
                st.session_state.form_lon=em_sel.get("Longitudine","")
                st.session_state.form_desc=f"Postazione per {em_sel.get('LogoNome','')} - {em_sel.get('Descrizione','')}"
                st.success(f"✅ Dati agganciati!")
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    st.divider()
    st.markdown("#### 1️⃣ Puntatore")
    tipo_puntatore=st.selectbox("Tipo Puntatore",["📍 Default Rosso","🚨 Emergenza","🏠 Sede ANA","👤 Volontario","🔥 Incendio","🌊 Alluvione","🚑 Sanitario","📻 Radio","⭐ Personalizzato PNG"],key="pointer_select")
    st.session_state.selected_pointer=tipo_puntatore
    st.markdown("#### 2️⃣ Mappa Click")
    try:
        import folium
        from streamlit_folium import st_folium
        from folium.plugins import Fullscreen
        lat_c=45.8205; lon_c=8.8255; zoom=12
        if st.session_state.form_lat and st.session_state.form_lon:
            try:
                lat_c=float(str(st.session_state.form_lat).replace(",","."))
                lon_c=float(str(st.session_state.form_lon).replace(",","."))
                zoom=15
            except:
                pass
        m_click=folium.Map(location=[lat_c,lon_c],zoom_start=zoom,tiles="OpenStreetMap")
        Fullscreen(position="topleft").add_to(m_click)
        if st.session_state.postazioni:
            for r in st.session_state.postazioni:
                try:
                    la=float(str(r["Latitudine"]).replace(",","."))
                    lo=float(str(r["Longitudine"]).replace(",","."))
                    folium.Marker([la,lo],popup=f"{r['Postazione']}",icon=folium.Icon(color="red",icon="info-sign")).add_to(m_click)
                except:
                    pass
        if st.session_state.clicked_lat and st.session_state.clicked_lon:
            try:
                clat=float(st.session_state.clicked_lat)
                clon=float(st.session_state.clicked_lon)
                folium.Marker([clat,clon],popup=f"🎯 NUOVA",icon=folium.Icon(color="blue",icon="star",prefix="fa")).add_to(m_click)
            except:
                pass
        map_data=st_folium(m_click,width=800,height=400,returned_objects=["last_clicked"])
        if map_data and map_data.get("last_clicked"):
            st.session_state.clicked_lat=str(map_data["last_clicked"]["lat"])
            st.session_state.clicked_lon=str(map_data["last_clicked"]["lng"])
            with st.spinner("Recupero via..."):
                city, road, desc_via_comune, desc_completa, addr_dict=reverse_geocode_dettagliato(float(st.session_state.clicked_lat), float(st.session_state.clicked_lon))
                st.session_state.clicked_comune=city
                st.session_state.clicked_via=road
                st.session_state.clicked_desc_via=desc_via_comune
                st.session_state.clicked_desc_completa=desc_completa
                st.session_state.form_lat=st.session_state.clicked_lat
                st.session_state.form_lon=st.session_state.clicked_lon
                st.session_state.form_comune=city
                st.session_state.form_via=road
                st.session_state.form_desc=desc_completa
            st.success(f"✅ {desc_via_comune}")
            st.rerun()
    except ImportError:
        st.warning("Installa folium")
    if st.session_state.clicked_lat:
        st.info(f"Lat {st.session_state.clicked_lat} Lon {st.session_state.clicked_lon} - {st.session_state.clicked_desc_via}")
        if st.button("🔄 COMPILA MASCHERA",use_container_width=True):
            st.session_state.form_lat=st.session_state.clicked_lat
            st.session_state.form_lon=st.session_state.clicked_lon
            st.session_state.form_comune=st.session_state.clicked_comune
            st.session_state.form_via=st.session_state.clicked_via
            st.session_state.form_desc=st.session_state.clicked_desc_completa
            st.rerun()
    st.divider()
    st.markdown("#### 3️⃣ Maschera Postazione")
    c1,c2=st.columns(2)
    with c1:
        comune=st.selectbox("Comune *",COMUNI_TUTTI,key="comune_map_final",index=COMUNI_TUTTI.index(st.session_state.form_comune) if st.session_state.form_comune in COMUNI_TUTTI else 0)
    with c2:
        via=st.text_input("Via *",value=st.session_state.form_via,key="via_map_final")
    with st.form("form_post_finale"):
        nome=st.text_input("Nome Postazione *",value=f"Postazione {st.session_state.form_comune} {st.session_state.form_via}" if st.session_state.form_comune else "")
        lat_final=st.text_input("Latitudine *",value=st.session_state.form_lat,key="lat_final")
        lon_final=st.text_input("Longitudine *",value=st.session_state.form_lon,key="lon_final")
        desc_via_final=st.text_area("Descrizione",value=st.session_state.form_desc,key="desc_via_final")
        if st.form_submit_button("➕ SALVA POSTAZIONE",use_container_width=True,type="primary"):
            if nome and lat_final and lon_final:
                new_post={"Postazione":nome,"Comune":comune,"Via":via,"Latitudine":lat_final,"Longitudine":lon_final,"DescrizioneVia":desc_via_final,"EmergenzaAbbinata":st.session_state.emergenza_agganciata.get("ID","") if st.session_state.emergenza_agganciata else ""}
                st.session_state.postazioni.append(new_post)
                save_json(FILE_POST,st.session_state.postazioni)
                st.success(f"✅ {nome} salvata!")
                st.rerun()
    if st.session_state.postazioni:
        st.dataframe(pd.DataFrame(st.session_state.postazioni),use_container_width=True)
    torna("bottom_map")

elif scelta=="Volontari":
    torna("top_vol")
    with st.form("form_vol"):
        c1,c2=st.columns(2)
        with c1:
            nome=st.text_input("Nome *")
            cognome=st.text_input("Cognome *")
            cell=st.text_input("Cellulare *")
        with c2:
            comune_cont=st.selectbox("Comune *",COMUNI_TUTTI,key="comune_cont")
            ruolo=st.selectbox("Ruolo *",["Volontario","Caposquadra","Coordinatore","Autista","Radio"],key="ruolo_4")
        if st.form_submit_button("SALVA VOLONTARIO",use_container_width=True,type="primary"):
            if nome and cognome and cell:
                nome_completo=f"{nome} {cognome}"
                st.session_state.dati.append({"Nome":nome_completo,"Cellulare":cell,"Comune":comune_cont,"Ruolo":ruolo})
                save_json(FILE_DATI,st.session_state.dati)
                if nome_completo not in st.session_state.mem_nomi:
                    st.session_state.mem_nomi.append(nome_completo)
                    save_json(FILE_NOMI,st.session_state.mem_nomi)
                st.success(f"Aggiunto {nome_completo}!")
                st.rerun()
    if st.session_state.dati:
        st.dataframe(pd.DataFrame(st.session_state.dati),use_container_width=True)
    torna("bottom_vol")

elif scelta=="DB Radio":
    torna("top_radio")
    st.markdown("### 📻 DB RADIO")
    with st.form("form_radio"):
        marca=st.text_input("Marca *")
        modello=st.text_input("Modello *")
        matricola=st.text_input("Matricola")
        if st.form_submit_button("💾 SALVA RADIO",use_container_width=True,type="primary"):
            if marca and modello:
                new_radio={"ID":str(uuid.uuid4())[:8],"Marca":marca,"Modello":modello,"Matricola":matricola,"Data":str(date.today())}
                st.session_state.radio_db.append(new_radio)
                save_json(FILE_RADIO,st.session_state.radio_db)
                st.success(f"✅ Radio salvata!")
                st.rerun()
    if st.session_state.radio_db:
        st.dataframe(pd.DataFrame(st.session_state.radio_db),use_container_width=True)
    torna("bottom_radio")

elif scelta=="Distribuzione Radio":
    torna("top_dist")
    st.markdown("### 📡 DISTRIBUZIONE RADIO")
    with st.form("form_dist"):
        volontario=st.selectbox("Volontario *",st.session_state.mem_nomi if st.session_state.mem_nomi else ["Nessuno"])
        motivo=st.text_input("Motivo / Evento")
        if st.form_submit_button("📡 ASSEGNA RADIO",use_container_width=True,type="primary"):
            if volontario!="Nessuno":
                new_dist={"ID":str(uuid.uuid4())[:8],"Volontario":volontario,"Motivo":motivo,"Data":str(date.today())}
                st.session_state.dist_radio.append(new_dist)
                save_json(FILE_DIST,st.session_state.dist_radio)
                st.success(f"✅ Assegnata!")
                st.rerun()
    if st.session_state.dist_radio:
        st.dataframe(pd.DataFrame(st.session_state.dist_radio),use_container_width=True)
    torna("bottom_dist")

elif scelta=="Eventi":
    torna("top_eventi")
    st.markdown("### 📅 EVENTI")
    with st.form("form_eventi"):
        nome_ev=st.text_input("Nome Evento *")
        data_ev=st.date_input("Data Evento",value=date.today())
        luogo_ev=st.selectbox("Comune Evento",COMUNI_TUTTI)
        if st.form_submit_button("📅 SALVA EVENTO",use_container_width=True,type="primary"):
            if nome_ev:
                new_ev={"ID":str(uuid.uuid4())[:8],"Nome":nome_ev,"Data":str(data_ev),"Luogo":luogo_ev}
                st.session_state.eventi_lista.append(new_ev)
                save_json(FILE_EVENTI,st.session_state.eventi_lista)
                st.success(f"✅ Evento salvato!")
                st.rerun()
    if st.session_state.eventi_lista:
        st.dataframe(pd.DataFrame(st.session_state.eventi_lista),use_container_width=True)
    torna("bottom_eventi")

elif scelta=="Check-in":
    torna("top_check")
    st.markdown("### ✅ CHECK-IN")
    with st.form("form_checkin"):
        volontario=st.selectbox("Volontario *",st.session_state.mem_nomi if st.session_state.mem_nomi else ["Nessuno"])
        luogo_check=st.selectbox("Luogo",COMUNI_TUTTI)
        if st.form_submit_button("✅ REGISTRA CHECK-IN",use_container_width=True,type="primary"):
            if volontario!="Nessuno":
                new_check={"ID":str(uuid.uuid4())[:8],"Volontario":volontario,"Luogo":luogo_check,"Data":str(date.today())}
                st.session_state.checkin_lista.append(new_check)
                save_json(FILE_CHECK,st.session_state.checkin_lista)
                st.success(f"✅ Check-in registrato!")
                st.rerun()
    if st.session_state.checkin_lista:
        st.dataframe(pd.DataFrame(st.session_state.checkin_lista),use_container_width=True)
    torna("bottom_check")

elif scelta=="Tabella Interventi Emergenza":
    torna("top_tab")
    st.markdown("### 📋 TABELLA INTERVENTI")
    if st.session_state.emergenze_lista:
        df=pd.DataFrame(st.session_state.emergenze_lista)
        st.dataframe(df,use_container_width=True)
        out=BytesIO()
        df.to_excel(out,index=False,engine="openpyxl")
        st.download_button("📥 Scarica Excel",out.getvalue(),file_name=f"emergenze_{date.today()}.xlsx",mime=MIME_SHORT,use_container_width=True)
    torna("bottom_tab")

elif scelta=="Backup":
    torna("top_back")
    st.markdown("### 💾 BACKUP - SCEGLI TU I DATI DEI VARI FORM")
    st.markdown('<div class="selezione-box">', unsafe_allow_html=True)
    st.markdown("**🎯 NOVITA': Ora scegli TU cosa esportare!**")
    st.markdown("- Spunta quali FORM esportare")
    st.markdown("- Scegli quali COLONNE esportare per ogni form")
    st.markdown("- Filtra per COMUNE, DATA, GRAVITA', RUOLO, ecc.")
    st.markdown("- Seleziona i RECORD specifici")
    st.markdown('</div>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📦 Generale con Scelta", "📋 Singoli Form con Filtri", "🔍 Scelta Colonne + Record", "🖨️ PDF con Scelta", "📥 Import"])

    with tab1:
        st.markdown("#### 📦 Backup Generale - SCEGLI TU quali form includere")
        st.markdown('<div class="selezione-box">', unsafe_allow_html=True)
        c1,c2,c3,c4=st.columns(4)
        with c1:
            inc_vol=st.checkbox("👤 Volontari",value=True,key="inc_vol_gen")
            inc_post=st.checkbox("📍 Postazioni",value=True,key="inc_post_gen")
        with c2:
            inc_emer=st.checkbox("🚨 Emergenze",value=True,key="inc_emer_gen")
            inc_radio=st.checkbox("📻 DB Radio",value=True,key="inc_radio_gen")
        with c3:
            inc_dist=st.checkbox("📡 Dist Radio",value=True,key="inc_dist_gen")
            inc_eventi=st.checkbox("📅 Eventi",value=False,key="inc_eventi_gen")
        with c4:
            inc_check=st.checkbox("✅ Check-in",value=False,key="inc_check_gen")
            inc_nomi=st.checkbox("📝 Mem Nomi",value=False,key="inc_nomi_gen")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("**Filtri per data (opzionale)**")
        c1,c2=st.columns(2)
        with c1:
            data_da=st.date_input("Data da (opzionale)",value=None,key="data_da_gen")
        with c2:
            data_a=st.date_input("Data a (opzionale)",value=None,key="data_a_gen")

        if st.button("📦 Crea Backup Generale con SELEZIONE",use_container_width=True,type="primary",key="backup_gen_sel"):
            output=BytesIO()
            with pd.ExcelWriter(output,engine="openpyxl") as writer:
                if inc_vol and st.session_state.dati:
                    df=pd.DataFrame(st.session_state.dati)
                    # Filtro data se presente colonna Data
                    if data_da and data_a and "DataNascita" in df.columns:
                        try:
                            df["DataNascita_dt"]=pd.to_datetime(df["DataNascita"],errors='coerce')
                            df=df[(df["DataNascita_dt"]>=pd.to_datetime(data_da)) & (df["DataNascita_dt"]<=pd.to_datetime(data_a))]
                            df=df.drop(columns=["DataNascita_dt"])
                        except:
                            pass
                    df.to_excel(writer,sheet_name="Volontari",index=False)
                if inc_post and st.session_state.postazioni:
                    df=pd.DataFrame(st.session_state.postazioni)
                    df.to_excel(writer,sheet_name="Postazioni",index=False)
                if inc_emer and st.session_state.emergenze_lista:
                    df=pd.DataFrame(st.session_state.emergenze_lista)
                    if data_da and data_a and "Data" in df.columns:
                        try:
                            df["Data_dt"]=pd.to_datetime(df["Data"],errors='coerce')
                            df=df[(df["Data_dt"]>=pd.to_datetime(data_da)) & (df["Data_dt"]<=pd.to_datetime(data_a))]
                            df=df.drop(columns=["Data_dt"])
                        except:
                            pass
                    df.to_excel(writer,sheet_name="Emergenze",index=False)
                if inc_radio and st.session_state.radio_db:
                    pd.DataFrame(st.session_state.radio_db).to_excel(writer,sheet_name="DB_Radio",index=False)
                if inc_dist and st.session_state.dist_radio:
                    pd.DataFrame(st.session_state.dist_radio).to_excel(writer,sheet_name="Dist_Radio",index=False)
                if inc_eventi and st.session_state.eventi_lista:
                    pd.DataFrame(st.session_state.eventi_lista).to_excel(writer,sheet_name="Eventi",index=False)
                if inc_check and st.session_state.checkin_lista:
                    pd.DataFrame(st.session_state.checkin_lista).to_excel(writer,sheet_name="Checkin",index=False)
                if inc_nomi and st.session_state.mem_nomi:
                    pd.DataFrame(st.session_state.mem_nomi, columns=["Nomi"]).to_excel(writer,sheet_name="Mem_Nomi",index=False)
            st.session_state.backup_bytes_sel=output.getvalue()
            st.success(f"✅ Backup generale con selezione creato! Form inclusi: Vol={inc_vol} Post={inc_post} Emer={inc_emer} Radio={inc_radio} Dist={inc_dist} Eventi={inc_eventi} Check={inc_check} Nomi={inc_nomi}")

        if "backup_bytes_sel" in st.session_state:
            st.download_button("📥 Scarica Excel con SELEZIONE",st.session_state.backup_bytes_sel,file_name=f"backup_selezione_{date.today()}.xlsx",mime=MIME_SHORT,use_container_width=True,key="dl_gen_sel")
            # PDF con selezione
            if st.button("📄 Crea PDF con SELEZIONE",use_container_width=True,key="pdf_gen_sel"):
                try:
                    from reportlab.lib.pagesizes import A4
                    from reportlab.pdfgen import canvas
                    buffer = BytesIO()
                    c = canvas.Canvas(buffer, pagesize=A4)
                    c.setFont("Helvetica-Bold", 16)
                    c.drawString(50, 800, "ANA Varese - Backup con Selezione")
                    c.setFont("Helvetica", 10)
                    c.drawString(50, 780, f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
                    y=750
                    c.drawString(50, y, f"Form selezionati:")
                    y-=15
                    for nome, inc in [("Volontari",inc_vol),("Postazioni",inc_post),("Emergenze",inc_emer),("DB Radio",inc_radio),("Dist Radio",inc_dist),("Eventi",inc_eventi),("Check-in",inc_check)]:
                        if inc:
                            c.drawString(70, y, f"- {nome}")
                            y-=12
                    c.save()
                    buffer.seek(0)
                    st.session_state.pdf_gen_sel=buffer.getvalue()
                    st.success("✅ PDF con selezione creato!")
                except Exception as e:
                    st.error(f"Errore PDF: {e}")
            if "pdf_gen_sel" in st.session_state:
                st.download_button("📥 Scarica PDF con SELEZIONE",st.session_state.pdf_gen_sel,file_name=f"backup_selezione_{date.today()}.pdf",mime="application/pdf",use_container_width=True,key="dl_pdf_gen_sel")

    with tab2:
        st.markdown("#### 📋 Backup Singoli Form - CON FILTRI E SCELTA DATI")
        form_scelta=st.selectbox("Seleziona Form *", ["Volontari","Postazioni Mappa","Emergenze con Loghi","DB Radio","Distribuzione Radio","Eventi","Check-in"], key="form_scelta_filtri")

        # Recupera dati del form scelto
        if form_scelta=="Volontari":
            dati_form=st.session_state.dati
        elif form_scelta=="Postazioni Mappa":
            dati_form=st.session_state.postazioni
        elif form_scelta=="Emergenze con Loghi":
            dati_form=st.session_state.emergenze_lista
        elif form_scelta=="DB Radio":
            dati_form=st.session_state.radio_db
        elif form_scelta=="Distribuzione Radio":
            dati_form=st.session_state.dist_radio
        elif form_scelta=="Eventi":
            dati_form=st.session_state.eventi_lista
        elif form_scelta=="Check-in":
            dati_form=st.session_state.checkin_lista
        else:
            dati_form=[]

        if not dati_form:
            st.warning(f"Nessun dato per {form_scelta}")
        else:
            df_form=pd.DataFrame(dati_form)
            st.markdown(f"**Totale record: {len(df_form)} | Colonne: {list(df_form.columns)}**")

            st.markdown('<div class="selezione-box">', unsafe_allow_html=True)
            st.markdown("**1️⃣ SCEGLI COLONNE DA ESPORTARE**")
            colonne_sel=st.multiselect(f"Colonne di {form_scelta} da esportare", list(df_form.columns), default=list(df_form.columns), key=f"col_sel_{form_scelta}")
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="selezione-box">', unsafe_allow_html=True)
            st.markdown("**2️⃣ FILTRI - SCEGLI DATI**")

            df_filtrato=df_form.copy()

            # Filtri dinamici in base al form
            if form_scelta=="Volontari":
                if "Comune" in df_form.columns:
                    comuni_uniq=sorted(df_form["Comune"].dropna().unique().tolist())
                    comuni_filtro=st.multiselect("Filtra per Comune (scegli tu)", comuni_uniq, default=comuni_uniq, key="filtro_comune_vol")
                    if comuni_filtro:
                        df_filtrato=df_filtrato[df_filtrato["Comune"].isin(comuni_filtro)]
                if "Ruolo" in df_form.columns:
                    ruoli_uniq=sorted(df_form["Ruolo"].dropna().unique().tolist())
                    ruoli_filtro=st.multiselect("Filtra per Ruolo", ruoli_uniq, default=ruoli_uniq, key="filtro_ruolo_vol")
                    if ruoli_filtro:
                        df_filtrato=df_filtrato[df_filtrato["Ruolo"].isin(ruoli_filtro)]
                if "Gruppo" in df_form.columns:
                    gruppi_uniq=sorted(df_form["Gruppo"].dropna().unique().tolist())
                    gruppi_filtro=st.multiselect("Filtra per Gruppo", gruppi_uniq, default=gruppi_uniq, key="filtro_gruppo_vol")
                    if gruppi_filtro:
                        df_filtrato=df_filtrato[df_filtrato["Gruppo"].isin(gruppi_filtro)]

            elif form_scelta=="Emergenze con Loghi":
                if "Comune" in df_form.columns:
                    comuni_uniq=sorted(df_form["Comune"].dropna().unique().tolist())
                    comuni_filtro=st.multiselect("Filtra per Comune", comuni_uniq, default=comuni_uniq, key="filtro_comune_emer")
                    if comuni_filtro:
                        df_filtrato=df_filtrato[df_filtrato["Comune"].isin(comuni_filtro)]
                if "Gravità" in df_form.columns:
                    grav_uniq=sorted(df_form["Gravità"].dropna().unique().tolist())
                    grav_filtro=st.multiselect("Filtra per Gravità", grav_uniq, default=grav_uniq, key="filtro_grav_emer")
                    if grav_filtro:
                        df_filtrato=df_filtrato[df_filtrato["Gravità"].isin(grav_filtro)]
                if "Tipo" in df_form.columns:
                    tipo_uniq=sorted(df_form["Tipo"].dropna().unique().tolist())
                    tipo_filtro=st.multiselect("Filtra per Tipo Emergenza", tipo_uniq, default=tipo_uniq, key="filtro_tipo_emer")
                    if tipo_filtro:
                        df_filtrato=df_filtrato[df_filtrato["Tipo"].isin(tipo_filtro)]
                if "Data" in df_form.columns:
                    c1,c2=st.columns(2)
                    with c1:
                        data_da_f=st.date_input("Data da", value=None, key="data_da_emer")
                    with c2:
                        data_a_f=st.date_input("Data a", value=None, key="data_a_emer")
                    if data_da_f and data_a_f:
                        try:
                            df_filtrato["Data_dt"]=pd.to_datetime(df_filtrato["Data"],errors='coerce')
                            df_filtrato=df_filtrato[(df_filtrato["Data_dt"]>=pd.to_datetime(data_da_f)) & (df_filtrato["Data_dt"]<=pd.to_datetime(data_a_f))]
                            df_filtrato=df_filtrato.drop(columns=["Data_dt"])
                        except:
                            pass

            elif form_scelta=="Postazioni Mappa":
                if "Comune" in df_form.columns:
                    comuni_uniq=sorted(df_form["Comune"].dropna().unique().tolist())
                    comuni_filtro=st.multiselect("Filtra per Comune", comuni_uniq, default=comuni_uniq, key="filtro_comune_post")
                    if comuni_filtro:
                        df_filtrato=df_filtrato[df_filtrato["Comune"].isin(comuni_filtro)]
                if "Puntatore" in df_form.columns:
                    punt_uniq=sorted(df_form["Puntatore"].dropna().unique().tolist())
                    punt_filtro=st.multiselect("Filtra per Puntatore", punt_uniq, default=punt_uniq, key="filtro_punt_post")
                    if punt_filtro:
                        df_filtrato=df_filtrato[df_filtrato["Puntatore"].isin(punt_filtro)]

            # Filtro testo libero per tutti
            testo_libero=st.text_input("🔍 Filtro testo libero (cerca in tutti i campi) - scegli tu cosa cercare", key=f"testo_libero_{form_scelta}")
            if testo_libero:
                df_filtrato=df_filtrato[df_filtrato.apply(lambda row: testo_libero.lower() in str(row.values).lower(), axis=1)]

            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown(f"**Record dopo filtri: {len(df_filtrato)} su {len(df_form)}**")

            # Applica selezione colonne
            if colonne_sel:
                df_filtrato=df_filtrato[colonne_sel]

            st.dataframe(df_filtrato, use_container_width=True)

            st.markdown("**3️⃣ ESPORTA CON SCELTA DATI**")
            c1,c2,c3=st.columns(3)
            with c1:
                out=BytesIO()
                df_filtrato.to_excel(out,index=False,engine="openpyxl")
                st.download_button(f"📥 Excel con SCELTA ({len(df_filtrato)} record)",out.getvalue(),file_name=f"{form_scelta.replace(' ', '_')}_scelta_{date.today()}.xlsx",mime=MIME_SHORT,use_container_width=True,key=f"dl_excel_scelta_{form_scelta}")
            with c2:
                json_bytes=json.dumps(df_filtrato.to_dict('records'),ensure_ascii=False,indent=2).encode('utf-8')
                st.download_button(f"📥 JSON con SCELTA ({len(df_filtrato)})",json_bytes,file_name=f"{form_scelta.replace(' ', '_')}_scelta_{date.today()}.json",mime="application/json",use_container_width=True,key=f"dl_json_scelta_{form_scelta}")
            with c3:
                pdf_bytes=create_pdf_report(df_filtrato, f"ANA Varese - {form_scelta} - Scelta Dati", f"Filtri applicati - {len(df_filtrato)} record")
                if pdf_bytes:
                    st.download_button(f"📄 PDF con SCELTA ({len(df_filtrato)})",pdf_bytes,file_name=f"{form_scelta.replace(' ', '_')}_scelta_{date.today()}.pdf",mime="application/pdf",use_container_width=True,key=f"dl_pdf_scelta_{form_scelta}")

    with tab3:
        st.markdown("#### 🔍 Scelta Colonne + Record Specifici con Checkbox")
        form_scelta2=st.selectbox("Seleziona Form per scelta record *", ["Volontari","Postazioni Mappa","Emergenze con Loghi","DB Radio","Distribuzione Radio"], key="form_scelta_record")

        if form_scelta2=="Volontari":
            dati_form2=st.session_state.dati
        elif form_scelta2=="Postazioni Mappa":
            dati_form2=st.session_state.postazioni
        elif form_scelta2=="Emergenze con Loghi":
            dati_form2=st.session_state.emergenze_lista
        elif form_scelta2=="DB Radio":
            dati_form2=st.session_state.radio_db
        elif form_scelta2=="Distribuzione Radio":
            dati_form2=st.session_state.dist_radio
        else:
            dati_form2=[]

        if dati_form2:
            df_form2=pd.DataFrame(dati_form2)
            st.markdown(f"**Seleziona i record che vuoi esportare - Spunta le righe**")

            # Aggiungi checkbox per selezione record
            df_form2["_Seleziona"]=False
            edited_df=st.data_editor(df_form2, use_container_width=True, key=f"editor_{form_scelta2}", hide_index=True)

            record_sel=edited_df[edited_df["_Seleziona"]==True]
            if "_Seleziona" in record_sel.columns:
                record_sel=record_sel.drop(columns=["_Seleziona"])
            if "_Seleziona" in edited_df.columns:
                edited_df_display=edited_df.drop(columns=["_Seleziona"])
            else:
                edited_df_display=edited_df

            st.markdown(f"**Record selezionati: {len(record_sel)}**")

            if len(record_sel)>0:
                st.markdown('<div class="selezione-box">', unsafe_allow_html=True)
                st.markdown(f"Hai selezionato {len(record_sel)} record - Scegli colonne da esportare")
                colonne_sel2=st.multiselect(f"Colonne da esportare per i {len(record_sel)} record selezionati", list(record_sel.columns), default=list(record_sel.columns), key=f"col_sel_record_{form_scelta2}")
                st.markdown('</div>', unsafe_allow_html=True)

                if colonne_sel2:
                    record_sel_final=record_sel[colonne_sel2]

                    c1,c2,c3=st.columns(3)
                    with c1:
                        out=BytesIO()
                        record_sel_final.to_excel(out,index=False,engine="openpyxl")
                        st.download_button(f"📥 Excel {len(record_sel_final)} selezionati",out.getvalue(),file_name=f"{form_scelta2}_selezionati_{date.today()}.xlsx",mime=MIME_SHORT,use_container_width=True,key=f"dl_excel_sel_{form_scelta2}")
                    with c2:
                        json_bytes=json.dumps(record_sel_final.to_dict('records'),ensure_ascii=False,indent=2).encode('utf-8')
                        st.download_button(f"📥 JSON {len(record_sel_final)} selezionati",json_bytes,file_name=f"{form_scelta2}_selezionati_{date.today()}.json",mime="application/json",use_container_width=True,key=f"dl_json_sel_{form_scelta2}")
                    with c3:
                        pdf_bytes=create_pdf_report(record_sel_final, f"ANA Varese - {form_scelta2} - Record Selezionati")
                        if pdf_bytes:
                            st.download_button(f"📄 PDF {len(record_sel_final)} selezionati",pdf_bytes,file_name=f"{form_scelta2}_selezionati_{date.today()}.pdf",mime="application/pdf",use_container_width=True,key=f"dl_pdf_sel_{form_scelta2}")

    with tab4:
        st.markdown("#### 🖨️ Anteprima PDF con SCELTA DATI")
        st.info("Scegli form, colonne e filtri per creare PDF personalizzato")

        pdf_form_scelta=st.selectbox("Form per PDF con scelta", ["Volontari","Postazioni Mappa","Emergenze con Loghi","DB Radio","Distribuzione Radio","Eventi","Check-in","Tutti i Form con Scelta"], key="pdf_form_scelta")

        # Scelta colonne per PDF
        if pdf_form_scelta!="Tutti i Form con Scelta":
            if pdf_form_scelta=="Volontari":
                df_pdf_base=pd.DataFrame(st.session_state.dati) if st.session_state.dati else pd.DataFrame()
            elif pdf_form_scelta=="Postazioni Mappa":
                df_pdf_base=pd.DataFrame(st.session_state.postazioni) if st.session_state.postazioni else pd.DataFrame()
            elif pdf_form_scelta=="Emergenze con Loghi":
                df_pdf_base=pd.DataFrame(st.session_state.emergenze_lista) if st.session_state.emergenze_lista else pd.DataFrame()
            elif pdf_form_scelta=="DB Radio":
                df_pdf_base=pd.DataFrame(st.session_state.radio_db) if st.session_state.radio_db else pd.DataFrame()
            elif pdf_form_scelta=="Distribuzione Radio":
                df_pdf_base=pd.DataFrame(st.session_state.dist_radio) if st.session_state.dist_radio else pd.DataFrame()
            elif pdf_form_scelta=="Eventi":
                df_pdf_base=pd.DataFrame(st.session_state.eventi_lista) if st.session_state.eventi_lista else pd.DataFrame()
            elif pdf_form_scelta=="Check-in":
                df_pdf_base=pd.DataFrame(st.session_state.checkin_lista) if st.session_state.checkin_lista else pd.DataFrame()
            else:
                df_pdf_base=pd.DataFrame()

            if not df_pdf_base.empty:
                colonne_pdf=st.multiselect(f"Colonne per PDF {pdf_form_scelta} - Scegli tu", list(df_pdf_base.columns), default=list(df_pdf_base.columns)[:6], key=f"col_pdf_{pdf_form_scelta}")
                max_record=st.slider(f"Max record in PDF {pdf_form_scelta}", 5, 100, 30, key=f"slider_pdf_{pdf_form_scelta}")

                if st.button(f"🖨️ Crea PDF con SCELTA - {pdf_form_scelta}", use_container_width=True, type="primary", key=f"btn_pdf_{pdf_form_scelta}"):
                    if colonne_pdf:
                        df_pdf_final=df_pdf_base[colonne_pdf].head(max_record)
                        pdf_bytes=create_pdf_report(df_pdf_final, f"ANA Varese - {pdf_form_scelta} - Scelta Dati", f"Colonne: {', '.join(colonne_pdf)} - {len(df_pdf_final)} record scelti da te")
                        if pdf_bytes:
                            st.session_state[f"pdf_scelta_{pdf_form_scelta}"]=pdf_bytes
                            st.success(f"✅ PDF {pdf_form_scelta} con scelta creato!")

                key_pdf=f"pdf_scelta_{pdf_form_scelta}"
                if key_pdf in st.session_state:
                    st.download_button(f"📥 Scarica PDF {pdf_form_scelta} con SCELTA", st.session_state[key_pdf], file_name=f"{pdf_form_scelta}_scelta_{date.today()}.pdf", mime="application/pdf", use_container_width=True, key=f"dl_pdf_scelta_final_{pdf_form_scelta}")
        else:
            st.markdown("**Tutti i Form con Scelta - Seleziona quali form includere nel PDF unico**")
            c1,c2=st.columns(2)
            with c1:
                inc_vol_pdf=st.checkbox("Volontari in PDF unico",value=True,key="inc_vol_pdf")
                inc_post_pdf=st.checkbox("Postazioni in PDF unico",value=True,key="inc_post_pdf")
                inc_emer_pdf=st.checkbox("Emergenze in PDF unico",value=True,key="inc_emer_pdf")
            with c2:
                inc_radio_pdf=st.checkbox("DB Radio in PDF unico",value=False,key="inc_radio_pdf")
                inc_eventi_pdf=st.checkbox("Eventi in PDF unico",value=False,key="inc_eventi_pdf")
                inc_check_pdf=st.checkbox("Check-in in PDF unico",value=False,key="inc_check_pdf")

            if st.button("🖨️ Crea PDF Unico con SCELTA FORM", use_container_width=True, type="primary", key="btn_pdf_unico_scelta"):
                try:
                    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
                    from reportlab.lib.styles import getSampleStyleSheet
                    from reportlab.lib import colors
                    from reportlab.lib.pagesizes import A4
                    buffer = BytesIO()
                    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=30, rightMargin=30, topMargin=30, bottomMargin=30)
                    styles = getSampleStyleSheet()
                    elements = []
                    elements.append(Paragraph("ANA VARESE - PDF Unico con Scelta Form", styles['Heading1']))
                    elements.append(Spacer(1, 12))
                    elements.append(Paragraph(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')} - Form scelti da te", styles['Normal']))
                    elements.append(Spacer(1, 20))
                    for nome_form, lista_dati, inc_flag in [("Volontari", st.session_state.dati, inc_vol_pdf), ("Postazioni", st.session_state.postazioni, inc_post_pdf), ("Emergenze", st.session_state.emergenze_lista, inc_emer_pdf), ("DB Radio", st.session_state.radio_db, inc_radio_pdf), ("Eventi", st.session_state.eventi_lista, inc_eventi_pdf), ("Check-in", st.session_state.checkin_lista, inc_check_pdf)]:
                        if inc_flag and lista_dati:
                            elements.append(Paragraph(f"{nome_form} - {len(lista_dati)} record scelti", styles['Heading2']))
                            df_temp = pd.DataFrame(lista_dati)
                            for col in list(df_temp.columns):
                                if 'PNG' in col or 'CustomPNG' in col:
                                    df_temp = df_temp.drop(columns=[col])
                            if len(df_temp.columns) > 4:
                                df_temp = df_temp.iloc[:, :4]
                            df_temp = df_temp.head(10)
                            data = [list(df_temp.columns)] + df_temp.values.tolist()
                            table = Table(data)
                            table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e7d32')),('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),('FONTSIZE', (0, 0), (-1, -1), 6),('GRID', (0, 0), (-1, -1), 1, colors.black)]))
                            elements.append(table)
                            elements.append(Spacer(1, 20))
                    doc.build(elements)
                    buffer.seek(0)
                    st.session_state.pdf_unico_scelta=buffer.getvalue()
                    st.success("✅ PDF unico con scelta form creato!")
                except Exception as e:
                    st.error(f"Errore PDF unico: {e}")

            if "pdf_unico_scelta" in st.session_state:
                st.download_button("📥 Scarica PDF Unico con SCELTA FORM", st.session_state.pdf_unico_scelta, file_name=f"pdf_unico_scelta_{date.today()}.pdf", mime="application/pdf", use_container_width=True, key="dl_pdf_unico_scelta")

    with tab5:
        st.markdown("#### 📥 Import Dati - Tutti i Form")
        import_type=st.selectbox("Tipo Import *",["Volontari","Postazioni Mappa","Emergenze con Loghi","DB Radio","Distribuzione Radio","Eventi","Check-in"],key="import_type")
        modo_import=st.selectbox("Modalità *",["Aggiungi ai dati esistenti","Sovrascrivi tutti i dati"],key="modo_import")
        file_type=st.selectbox("Formato *",["Excel (.xlsx)","JSON (.json)"],key="file_type")
        uploaded_file=st.file_uploader(f"Carica file {import_type} - {file_type}",type=["xlsx","json"],key="import_file")
        if uploaded_file:
            if st.button(f"📥 IMPORTA {import_type} - {modo_import}",use_container_width=True,type="primary",key="import_btn"):
                try:
                    if file_type=="Excel (.xlsx)":
                        df_import=pd.read_excel(uploaded_file,engine="openpyxl")
                        data_import=df_import.to_dict('records')
                    else:
                        data_import=json.load(uploaded_file)
                        if isinstance(data_import, dict):
                            key_map={"Volontari":"volontari","Postazioni Mappa":"postazioni","Emergenze con Loghi":"emergenze","DB Radio":"radio_db","Distribuzione Radio":"dist_radio","Eventi":"eventi","Check-in":"checkin"}
                            k=key_map.get(import_type,"volontari")
                            if k in data_import:
                                data_import=data_import[k]
                    if import_type=="Volontari":
                        if modo_import=="Sovrascrivi tutti i dati":
                            st.session_state.dati=data_import
                        else:
                            st.session_state.dati.extend(data_import)
                        save_json(FILE_DATI,st.session_state.dati)
                    elif import_type=="Postazioni Mappa":
                        if modo_import=="Sovrascrivi tutti i dati":
                            st.session_state.postazioni=data_import
                        else:
                            st.session_state.postazioni.extend(data_import)
                        save_json(FILE_POST,st.session_state.postazioni)
                    elif import_type=="Emergenze con Loghi":
                        if modo_import=="Sovrascrivi tutti i dati":
                            st.session_state.emergenze_lista=data_import
                        else:
                            st.session_state.emergenze_lista.extend(data_import)
                        save_json(FILE_EMER,st.session_state.emergenze_lista)
                    elif import_type=="DB Radio":
                        if modo_import=="Sovrascrivi tutti i dati":
                            st.session_state.radio_db=data_import
                        else:
                            st.session_state.radio_db.extend(data_import)
                        save_json(FILE_RADIO,st.session_state.radio_db)
                    elif import_type=="Distribuzione Radio":
                        if modo_import=="Sovrascrivi tutti i dati":
                            st.session_state.dist_radio=data_import
                        else:
                            st.session_state.dist_radio.extend(data_import)
                        save_json(FILE_DIST,st.session_state.dist_radio)
                    elif import_type=="Eventi":
                        if modo_import=="Sovrascrivi tutti i dati":
                            st.session_state.eventi_lista=data_import
                        else:
                            st.session_state.eventi_lista.extend(data_import)
                        save_json(FILE_EVENTI,st.session_state.eventi_lista)
                    elif import_type=="Check-in":
                        if modo_import=="Sovrascrivi tutti i dati":
                            st.session_state.checkin_lista=data_import
                        else:
                            st.session_state.checkin_lista.extend(data_import)
                        save_json(FILE_CHECK,st.session_state.checkin_lista)
                    st.success(f"✅ Import {import_type} riuscito! {len(data_import)} record")
                    st.rerun()
                except Exception as e:
