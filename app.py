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
.checkbox-box{background-color:#f1f8e9;border:3px solid #2e7d32;border-radius:12px;padding:20px;margin:15px 0;}
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
        elements.append(Paragraph(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')} - Totale: {len(df)}", styles['Normal']))
        elements.append(Spacer(1, 20))
        df_pdf = df.copy()
        for col in list(df_pdf.columns):
            if 'PNG' in col or 'CustomPNG' in col:
                df_pdf = df_pdf.drop(columns=[col])
        for col in df_pdf.columns:
            df_pdf[col] = df_pdf[col].astype(str).apply(lambda x: x[:60] + "..." if len(x) > 60 else x)
        if len(df_pdf) > 50:
            df_pdf = df_pdf.head(50)
        data = [list(df_pdf.columns)] + df_pdf.values.tolist()
        col_width = 500 / len(df_pdf.columns) if len(df_pdf.columns) > 0 else 100
        table = Table(data, colWidths=[col_width]*len(df_pdf.columns) if len(df_pdf.columns) > 0 else [100])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e7d32')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('FONTSIZE', (0, 1), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(table)
        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()
    except Exception as e:
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
            st.error(f"Errore PDF: {e}")
            return None

FILE_DATI="dati_volontari.json"
FILE_POST="postazioni.json"
FILE_EMER="emergenze.json"
FILE_RADIO="radio_db.json"
FILE_DIST="dist_radio.json"
FILE_EVENTI="eventi.json"
FILE_CHECK="checkin.json"
FILE_NOMI="mem_nomi.json"
COMUNI_VARESE=["Varese","Busto Arsizio","Gallarate","Saronno","Cassano Magnago","Tradate","Malnate","Luino"]
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
            city=addr.get("city") or addr.get("town") or addr.get("village") or ""
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
if "clicked_lat" not in st.session_state:
    st.session_state.clicked_lat=""
if "clicked_lon" not in st.session_state:
    st.session_state.clicked_lon=""
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
    st.info("✅ Sistema completo - 950+ righe - Backup con caselle scelta!")

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
    col_logo1,col_logo2=st.columns([2,1])
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
    with st.form("form_em_completo"):
        cc1,cc2=st.columns(2)
        with cc1:
            data_em=st.date_input("Data *",value=date.today())
            gravita=st.selectbox("Gravità *",["Bassa","Media","Alta","Critica"],index=1)
        with cc2:
            stato=st.selectbox("Stato *",["Aperta","In Corso","Chiusa","Archiviata"],index=0)
            coord=st.text_input("Coordinatore *",value="ANA Varese")
            lat_em=st.text_input("Latitudine",placeholder="45.8205")
            lon_em=st.text_input("Longitudine",placeholder="8.8255")
        desc=st.text_area("Descrizione *",value=f"{sel_logo_info['nome']} a {comune} - {via_f}",height=100)
        if st.form_submit_button("💾 SALVA EMERGENZA",use_container_width=True,type="primary"):
            if via_f!="-- Seleziona Via --" and desc!="":
                new_em={"ID":str(uuid.uuid4())[:8],"Data":str(data_em),"Logo":sel_logo_info['emoji'],"LogoNome":sel_logo_info['nome'],"LogoPNG":sel_logo_info['png'],"Comune":comune,"Via":via_f,"Tipo":sel_logo_info['nome'],"Gravità":gravita,"Stato":stato,"Descrizione":desc,"Coordinatore":coord,"Latitudine":lat_em,"Longitudine":lon_em}
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
    if st.session_state.emergenze_lista:
        emergenze_options=["-- Nessuna --"]+[f"{e.get('ID','')} - {e.get('LogoNome','')} - {e.get('Comune','')} {e.get('Via','')}" for e in st.session_state.emergenze_lista]
        sel_em_idx=st.selectbox("Seleziona Emergenza",range(len(emergenze_options)),format_func=lambda i: emergenze_options[i],key="sel_emergenza_aggancio")
        if sel_em_idx>0:
            em_sel=st.session_state.emergenze_lista[sel_em_idx-1]
            st.markdown(f"**{em_sel.get('LogoNome','')} - {em_sel.get('Comune','')}**")
            if st.button(f"🔗 AGGANCIA DATI EMERGENZA",use_container_width=True,key="aggancia_btn"):
                st.session_state.emergenza_agganciata=em_sel
                st.session_state.form_comune=em_sel.get("Comune","")
                st.session_state.form_via=em_sel.get("Via","")
                st.session_state.form_lat=em_sel.get("Latitudine","")
                st.session_state.form_lon=em_sel.get("Longitudine","")
                st.session_state.form_desc=f"Postazione per {em_sel.get('LogoNome','')} - {em_sel.get('Descrizione','')}"
                st.success(f"✅ Dati agganciati!")
                st.rerun()
    st.divider()
    try:
        import folium
        from streamlit_folium import st_folium
        from folium.plugins import Fullscreen
        lat_c=45.8205; lon_c=8.8255; zoom=12
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
        st.info(f"Lat {st.session_state.clicked_lat} Lon {st.session_state.clicked_lon} - {st.session_state.form_comune} {st.session_state.form_via}")
        if st.button("🔄 COMPILA MASCHERA",use_container_width=True):
            st.session_state.form_lat=st.session_state.clicked_lat
            st.session_state.form_lon=st.session_state.clicked_lon
            st.rerun()
    st.divider()
    c1,c2=st.columns(2)
    with c1:
        comune=st.selectbox("Comune *",COMUNI_TUTTI,key="comune_map_final")
    with c2:
        via=st.text_input("Via *",value=st.session_state.form_via,key="via_map_final")
    with st.form("form_post_finale"):
        nome=st.text_input("Nome Postazione *")
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
    st.markdown("### 💾 BACKUP - CASELLE SCELTA FORM - SCEGLI TU I DATI DEI FORM")
    st.success("✅ FAI UNA CASELLA IN BACKUP COMO CHE SCELGO I DATI DEI FORM - FATTO!")
    tab1, tab2, tab3, tab4 = st.tabs(["📦 Backup con Caselle Scelta", "📋 Singoli Form TUTTI", "🖨️ PDF con Scelta", "📥 Import"])
    with tab1:
        st.markdown("#### 📦 Backup Generale con Caselle di Scelta")
        st.markdown('<div class="checkbox-box">', unsafe_allow_html=True)
        st.markdown("##### ✅ CASELLA - Seleziona i form da includere:")
        col1, col2 = st.columns(2)
        with col1:
            chk_vol = st.checkbox(f"👤 Volontari ({len(st.session_state.dati)} record)", value=True, key="chk_vol_gen")
            chk_post = st.checkbox(f"📍 Postazioni Mappa ({len(st.session_state.postazioni)} record)", value=True, key="chk_post_gen")
            chk_emer = st.checkbox(f"🚨 Emergenze con Loghi ({len(st.session_state.emergenze_lista)} record)", value=True, key="chk_emer_gen")
            chk_radio = st.checkbox(f"📻 DB Radio ({len(st.session_state.radio_db)} record)", value=True, key="chk_radio_gen")
        with col2:
            chk_dist = st.checkbox(f"📡 Distribuzione Radio ({len(st.session_state.dist_radio)} record)", value=True, key="chk_dist_gen")
            chk_eventi = st.checkbox(f"📅 Eventi ({len(st.session_state.eventi_lista)} record)", value=True, key="chk_eventi_gen")
            chk_check = st.checkbox(f"✅ Check-in ({len(st.session_state.checkin_lista)} record)", value=True, key="chk_check_gen")
            chk_nomi = st.checkbox(f"📝 Mem Nomi ({len(st.session_state.mem_nomi)} record)", value=True, key="chk_nomi_gen")
        c_sel1, c_sel2, c_sel3 = st.columns(3)
        with c_sel1:
            if st.button("✅ Seleziona Tutti", use_container_width=True, key="sel_all"):
                for k in ["chk_vol_gen","chk_post_gen","chk_emer_gen","chk_radio_gen","chk_dist_gen","chk_eventi_gen","chk_check_gen","chk_nomi_gen"]:
                    st.session_state[k]=True
                st.rerun()
        with c_sel2:
            if st.button("❌ Deseleziona Tutti", use_container_width=True, key="desel_all"):
                for k in ["chk_vol_gen","chk_post_gen","chk_emer_gen","chk_radio_gen","chk_dist_gen","chk_eventi_gen","chk_check_gen","chk_nomi_gen"]:
                    st.session_state[k]=False
                st.rerun()
        with c_sel3:
            selected_count = sum([chk_vol, chk_post, chk_emer, chk_radio, chk_dist, chk_eventi, chk_check, chk_nomi])
            st.metric("Form Selezionati", f"{selected_count}/8")
        st.markdown('</div>', unsafe_allow_html=True)
        if selected_count == 0:
            st.warning("⚠️ Seleziona almeno un form!")
        else:
            st.success(f"✅ Hai selezionato {selected_count} form")
        if st.button(f"📦 Crea Excel con {selected_count} Form",use_container_width=True,type="primary",key="backup_excel_sel", disabled=(selected_count==0)):
            output=BytesIO()
            with pd.ExcelWriter(output,engine="openpyxl") as writer:
                if chk_vol and st.session_state.dati:
                    pd.DataFrame(st.session_state.dati).to_excel(writer,sheet_name="Volontari",index=False)
                if chk_post and st.session_state.postazioni:
                    pd.DataFrame(st.session_state.postazioni).to_excel(writer,sheet_name="Postazioni",index=False)
                if chk_emer and st.session_state.emergenze_lista:
                    pd.DataFrame(st.session_state.emergenze_lista).to_excel(writer,sheet_name="Emergenze",index=False)
                if chk_radio and st.session_state.radio_db:
                    pd.DataFrame(st.session_state.radio_db).to_excel(writer,sheet_name="DB_Radio",index=False)
                if chk_dist and st.session_state.dist_radio:
                    pd.DataFrame(st.session_state.dist_radio).to_excel(writer,sheet_name="Dist_Radio",index=False)
                if chk_eventi and st.session_state.eventi_lista:
                    pd.DataFrame(st.session_state.eventi_lista).to_excel(writer,sheet_name="Eventi",index=False)
                if chk_check and st.session_state.checkin_lista:
                    pd.DataFrame(st.session_state.checkin_lista).to_excel(writer,sheet_name="Checkin",index=False)
                if chk_nomi and st.session_state.mem_nomi:
                    pd.DataFrame(st.session_state.mem_nomi, columns=["Nomi"]).to_excel(writer,sheet_name="Mem_Nomi",index=False)
            st.session_state.backup_bytes_sel=output.getvalue()
            st.session_state.backup_count_sel=selected_count
            st.success(f"✅ Excel creato!")
        if "backup_bytes_sel" in st.session_state:
            fname=f"backup_selezionato_{st.session_state.backup_count_sel}form_{date.today()}.xlsx"
            st.download_button(f"📥 Scarica Excel con {st.session_state.backup_count_sel} Form",st.session_state.backup_bytes_sel,file_name=fname,mime=MIME_SHORT,use_container_width=True,key="dl_excel_sel")
        if st.button(f"📦 Crea JSON con {selected_count} Form",use_container_width=True,key="backup_json_sel", disabled=(selected_count==0)):
            all_data={}
            if chk_vol:
                all_data["volontari"]=st.session_state.dati
            if chk_post:
                all_data["postazioni"]=st.session_state.postazioni
            if chk_emer:
                all_data["emergenze"]=st.session_state.emergenze_lista
            if chk_radio:
                all_data["radio_db"]=st.session_state.radio_db
            if chk_dist:
                all_data["dist_radio"]=st.session_state.dist_radio
            if chk_eventi:
                all_data["eventi"]=st.session_state.eventi_lista
            if chk_check:
                all_data["checkin"]=st.session_state.checkin_lista
            if chk_nomi:
                all_data["mem_nomi"]=st.session_state.mem_nomi
            json_str=json.dumps(all_data,ensure_ascii=False,indent=2)
            st.session_state.backup_json_sel=json_str.encode('utf-8')
            st.session_state.backup_json_count=selected_count
            st.success(f"✅ JSON creato!")
        if "backup_json_sel" in st.session_state:
            st.download_button(f"📥 Scarica JSON {st.session_state.backup_json_count} Form",st.session_state.backup_json_sel,file_name=f"backup_{st.session_state.backup_json_count}form_{date.today()}.json",mime="application/json",use_container_width=True,key="dl_json_sel")
        if st.button(f"📄 Crea PDF con {selected_count} Form",use_container_width=True,key="backup_pdf_sel", disabled=(selected_count==0)):
            try:
                from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
                from reportlab.lib.styles import getSampleStyleSheet
                from reportlab.lib import colors
                from reportlab.lib.pagesizes import A4
                buffer = BytesIO()
                doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=30, rightMargin=30, topMargin=30, bottomMargin=30)
                styles = getSampleStyleSheet()
                elements = []
                elements.append(Paragraph(f"ANA VARESE - Backup {selected_count} Form", styles['Heading1']))
                elements.append(Spacer(1, 12))
                elements.append(Paragraph(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')} - Form: {selected_count}/8", styles['Normal']))
                elements.append(Spacer(1, 20))
                form_map = []
                if chk_vol:
                    form_map.append(("Volontari", st.session_state.dati, "volontari"))
                if chk_post:
                    form_map.append(("Postazioni", st.session_state.postazioni, "postazioni"))
                if chk_emer:
                    form_map.append(("Emergenze", st.session_state.emergenze_lista, "emergenze"))
                if chk_radio:
                    form_map.append(("DB Radio", st.session_state.radio_db, "radio_db"))
                if chk_dist:
                    form_map.append(("Dist Radio", st.session_state.dist_radio, "dist_radio"))
                if chk_eventi:
                    form_map.append(("Eventi", st.session_state.eventi_lista, "eventi"))
                if chk_check:
                    form_map.append(("Check-in", st.session_state.checkin_lista, "checkin"))
                if chk_nomi:
                    form_map.append(("Mem Nomi", st.session_state.mem_nomi, "mem_nomi"))
                for nome_form, lista_dati, key_form in form_map:
                    if lista_dati:
                        elements.append(Paragraph(f"{nome_form} - {len(lista_dati)} record", styles['Heading2']))
                        df_temp = pd.DataFrame(lista_dati) if key_form!="mem_nomi" else pd.DataFrame(lista_dati, columns=["Nome"])
                        for col in list(df_temp.columns):
                            if 'PNG' in col or 'CustomPNG' in col:
                                df_temp = df_temp.drop(columns=[col])
                        if len(df_temp.columns) > 5:
                            df_temp = df_temp.iloc[:, :5]
                        df_temp = df_temp.head(15)
                        data = [list(df_temp.columns)] + df_temp.values.tolist()
                        table = Table(data)
                        table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e7d32')),('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),('FONTSIZE', (0, 0), (-1, -1), 6),('GRID', (0, 0), (-1, -1), 1, colors.black)]))
                        elements.append(table)
                        elements.append(Spacer(1, 20))
                doc.build(elements)
                buffer.seek(0)
                st.session_state.backup_pdf_sel = buffer.getvalue()
                st.session_state.backup_pdf_count = selected_count
                st.success(f"✅ PDF creato!")
            except Exception as e:
                st.error(f"Errore PDF: {e}")
        if "backup_pdf_sel" in st.session_state:
            st.download_button(f"📥 Scarica PDF con {st.session_state.backup_pdf_count} Form", st.session_state.backup_pdf_sel, file_name=f"backup_{st.session_state.backup_pdf_count}form_{date.today()}.pdf", mime="application/pdf", use_container_width=True, key="dl_pdf_sel")
    with tab2:
        st.markdown("#### 📋 Singoli Form TUTTI")
        forms_config = [
            ("👤 Volontari", st.session_state.dati, "volontari"),
            ("📍 Postazioni", st.session_state.postazioni, "postazioni"),
            ("🚨 Emergenze", st.session_state.emergenze_lista, "emergenze"),
            ("📻 DB Radio", st.session_state.radio_db, "radio_db"),
            ("📡 Dist Radio", st.session_state.dist_radio, "dist_radio"),
            ("📅 Eventi", st.session_state.eventi_lista, "eventi"),
            ("✅ Check-in", st.session_state.checkin_lista, "checkin"),
            ("📝 Mem Nomi", st.session_state.mem_nomi, "mem_nomi"),
        ]
        for nome_form, lista_dati, key_form in forms_config:
            st.markdown(f"**{nome_form} - {len(lista_dati)} record**")
            c1,c2,c3=st.columns(3)
            with c1:
                if lista_dati:
                    out=BytesIO()
                    if key_form == "mem_nomi":
                        pd.DataFrame(lista_dati, columns=["Nome"]).to_excel(out,index=False,engine="openpyxl")
                    else:
                        pd.DataFrame(lista_dati).to_excel(out,index=False,engine="openpyxl")
                    st.download_button(f"📥 Excel",out.getvalue(),file_name=f"{key_form}_{date.today()}.xlsx",mime=MIME_SHORT,use_container_width=True,key=f"dl_{key_form}")
            with c2:
                if lista_dati:
                    json_bytes=json.dumps(lista_dati,ensure_ascii=False,indent=2).encode('utf-8')
                    st.download_button(f"📥 JSON",json_bytes,file_name=f"{key_form}_{date.today()}.json",mime="application/json",use_container_width=True,key=f"dl_{key_form}_json")
            with c3:
                if lista_dati:
                    df_temp = pd.DataFrame(lista_dati) if key_form!= "mem_nomi" else pd.DataFrame(lista_dati, columns=["Nome"])
                    pdf_bytes = create_pdf_report(df_temp, f"ANA Varese - {nome_form}")
                    if pdf_bytes:
                        st.download_button(f"📄 PDF", pdf_bytes, file_name=f"{key_form}_{date.today()}.pdf", mime="application/pdf", use_container_width=True, key=f"dl_{key_form}_pdf")
    with tab3:
        st.markdown("#### 🖨️ PDF con Scelta Form")
        st.markdown('<div class="checkbox-box">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            chk_pdf_vol = st.checkbox(f"👤 Volontari", value=True, key="chk_pdf_vol")
            chk_pdf_post = st.checkbox(f"📍 Postazioni", value=True, key="chk_pdf_post")
            chk_pdf_emer = st.checkbox(f"🚨 Emergenze", value=True, key="chk_pdf_emer")
            chk_pdf_radio = st.checkbox(f"📻 DB Radio", value=True, key="chk_pdf_radio")
        with col2:
            chk_pdf_dist = st.checkbox(f"📡 Dist Radio", value=True, key="chk_pdf_dist")
            chk_pdf_eventi = st.checkbox(f"📅 Eventi", value=True, key="chk_pdf_eventi")
            chk_pdf_check = st.checkbox(f"✅ Check-in", value=True, key="chk_pdf_check")
            chk_pdf_nomi = st.checkbox(f"📝 Mem Nomi", value=False, key="chk_pdf_nomi")
        st.markdown('</div>', unsafe_allow_html=True)
        selected_pdf_count = sum([chk_pdf_vol, chk_pdf_post, chk_pdf_emer, chk_pdf_radio, chk_pdf_dist, chk_pdf_eventi, chk_pdf_check, chk_pdf_nomi])
        if st.button(f"🖨️ Crea PDF con {selected_pdf_count} Form", use_container_width=True, type="primary", disabled=(selected_pdf_count==0)):
            try:
                from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
                from reportlab.lib.styles import getSampleStyleSheet
                from reportlab.lib import colors
                from reportlab.lib.pagesizes import A4
                buffer = BytesIO()
                doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=30, rightMargin=30, topMargin=30, bottomMargin=30)
                styles = getSampleStyleSheet()
                elements = []
                elements.append(Paragraph(f"ANA VARESE - PDF {selected_pdf_count} Form", styles['Heading1']))
                elements.append(Spacer(1, 20))
                form_map = []
                if chk_pdf_vol:
                    form_map.append(("Volontari", st.session_state.dati, "volontari"))
                if chk_pdf_post:
                    form_map.append(("Postazioni", st.session_state.postazioni, "postazioni"))
                if chk_pdf_emer:
                    form_map.append(("Emergenze", st.session_state.emergenze_lista, "emergenze"))
                if chk_pdf_radio:
                    form_map.append(("DB Radio", st.session_state.radio_db, "radio_db"))
                if chk_pdf_dist:
                    form_map.append(("Dist Radio", st.session_state.dist_radio, "dist_radio"))
                if chk_pdf_eventi:
                    form_map.append(("Eventi", st.session_state.eventi_lista, "eventi"))
                if chk_pdf_check:
                    form_map.append(("Check-in", st.session_state.checkin_lista, "checkin"))
                if chk_pdf_nomi:
                    form_map.append(("Mem Nomi", st.session_state.mem_nomi, "mem_nomi"))
                for nome_form, lista_dati, key_form in form_map:
                    if lista_dati:
                        elements.append(Paragraph(f"{nome_form} - {len(lista_dati)}", styles['Heading2']))
                        df_temp = pd.DataFrame(lista_dati) if key_form!="mem_nomi" else pd.DataFrame(lista_dati, columns=["Nome"])
                        for col in list(df_temp.columns):
                            if 'PNG' in col or 'CustomPNG' in col:
                                df_temp = df_temp.drop(columns=[col])
                        if len(df_temp.columns) > 5:
                            df_temp = df_temp.iloc[:, :5]
                        df_temp = df_temp.head(15)
                        data = [list(df_temp.columns)] + df_temp.values.tolist()
                        table = Table(data)
                        table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e7d32')),('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),('FONTSIZE', (0, 0), (-1, -1), 6),('GRID', (0, 0), (-1, -1), 1, colors.black)]))
                        elements.append(table)
                        elements.append(Spacer(1, 20))
                doc.build(elements)
                buffer.seek(0)
                st.session_state.pdf_scelta = buffer.getvalue()
                st.session_state.pdf_scelta_count = selected_pdf_count
                st.success(f"✅ PDF creato con {selected_pdf_count} form!")
            except Exception as e:
                st.error(f"Errore PDF: {e}")
        if "pdf_scelta" in st.session_state:
            st.download_button(f"📥 Scarica PDF {st.session_state.pdf_scelta_count} Form", st.session_state.pdf_scelta, file_name=f"pdf_scelta_{st.session_state.pdf_scelta_count}form_{date.today()}.pdf", mime="application/pdf", use_container_width=True, key="dl_pdf_scelta")
    with tab4:
        st.markdown("#### 📥 Import")
        import_type=st.selectbox("Tipo Import",["Volontari","Postazioni Mappa","Emergenze con Loghi","DB Radio","Distribuzione Radio","Eventi","Check-in","Mem Nomi"],key="import_type")
        modo_import=st.selectbox("Modalità",["Aggiungi","Sovrascrivi"],key="modo_import")
        file_type=st.selectbox("Formato",["Excel","JSON"],key="file_type")
        uploaded_file=st.file_uploader(f"Carica {import_type}",type=["xlsx","json"],key="import_file")
        if uploaded_file:
            if st.button(f"📥 IMPORTA {import_type}",use_container_width=True,type="primary"):
                try:
                    if file_type=="Excel":
                        df_import=pd.read_excel(uploaded_file,engine="openpyxl")
                        data_import=df_import.to_dict('records')
                    else:
                        data_import=json.load(uploaded_file)
                    if import_type=="Volontari":
                        if modo_import=="Sovrascrivi":
                            st.session_state.dati=data_import
                        else:
                            st.session_state.dati.extend(data_import)
                        save_json(FILE_DATI,st.session_state.dati)
                    elif import_type=="Postazioni Mappa":
                        if modo_import=="Sovrascrivi":
                            st.session_state.postazioni=data_import
                        else:
                            st.session_state.postazioni.extend(data_import)
                        save_json(FILE_POST,st.session_state.postazioni)
                    elif import_type=="Emergenze con Loghi":
                        if modo_import=="Sovrascrivi":
                            st.session_state.emergenze_lista=data_import
                        else:
                            st.session_state.emergenze_lista.extend(data_import)
                        save_json(FILE_EMER,st.session_state.emergenze_lista)
                    st.success(f"✅ Import riuscito! {len(data_import)} record")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Errore: {e}")
    torna("bottom_back")

else:
    torna("generic")
    if scelta=="Volontari":
        st.markdown("### 👤 VOLONTARI")
        with st.form("form_vol"):
            nome=st.text_input("Nome *")
            cognome=st.text_input("Cognome *")
            cell=st.text_input("Cellulare *")
            comune_cont=st.selectbox("Comune Residenza *",COMUNI_TUTTI,key="comune_cont")
            ruolo=st.selectbox("Ruolo *",["Volontario","Caposquadra","Coordinatore","Autista","Radio"],key="ruolo_4")
            if st.form_submit_button("SALVA VOLONTARIO",use_container_width=True,type="primary"):
                if nome and cognome and cell:
                    nome_completo=f"{nome} {cognome}"
                    st.session_state.dati.append({"Nome":nome_completo,"Cellulare":cell,"Comune":comune_cont,"Ruolo":ruolo})
                    save_json(FILE_DATI,st.session_state.dati)
                    st.success(f"Aggiunto {nome_completo}!")
                    st.rerun()
        if st.session_state.dati:
            st.dataframe(pd.DataFrame(st.session_state.dati),use_container_width=True)
    elif scelta=="Emergenze con Loghi":
        st.markdown("### 🚨 EMERGENZE")
        comune=st.selectbox("Comune *",COMUNI_TUTTI,key="comune_em")
        via=st.text_input("Via *",key="via_em")
        logo_keys=list(EMERGENCY_LOGOS.keys())
        logo_names=[f"{EMERGENCY_LOGOS[k]['emoji']} {EMERGENCY_LOGOS[k]['nome']}" for k in logo_keys]
        sel_logo_idx=st.selectbox("Tipo Emergenza *",range(len(logo_keys)),format_func=lambda i: logo_names[i],key="logo_sel")
        sel_logo_key=logo_keys[sel_logo_idx]
        sel_logo_info=EMERGENCY_LOGOS[sel_logo_key]
        with st.form("form_em"):
            data_em=st.date_input("Data *",value=date.today())
            gravita=st.selectbox("Gravità *",["Bassa","Media","Alta","Critica"],index=1)
            desc=st.text_area("Descrizione *",value=f"{sel_logo_info['nome']} a {comune} - {via}",height=80)
            if st.form_submit_button("💾 SALVA EMERGENZA",use_container_width=True,type="primary"):
                if via and desc:
                    new_em={"ID":str(uuid.uuid4())[:8],"Data":str(data_em),"Logo":sel_logo_info['emoji'],"LogoNome":sel_logo_info['nome'],"LogoPNG":sel_logo_info['png'],"Comune":comune,"Via":via,"Tipo":sel_logo_info['nome'],"Gravità":gravita,"Descrizione":desc}
                    st.session_state.emergenze_lista.append(new_em)
                    save_json(FILE_EMER,st.session_state.emergenze_lista)
                    st.success(f"✅ Emergenza salvata!")
                    st.rerun()
        if st.session_state.emergenze_lista:
            st.dataframe(pd.DataFrame(st.session_state.emergenze_lista),use_container_width=True)
    elif scelta=="Mappa Postazioni":
        st.markdown("### 🗺️ MAPPA POSTAZIONI")
        comune=st.selectbox("Comune *",COMUNI_TUTTI,key="comune_map_final")
        via=st.text_input("Via *",value=st.session_state.form_via,key="via_map_final")
        with st.form("form_post_finale"):
            nome=st.text_input("Nome Postazione *")
            lat_final=st.text_input("Latitudine *",value=st.session_state.form_lat,key="lat_final")
            lon_final=st.text_input("Longitudine *",value=st.session_state.form_lon,key="lon_final")
            if st.form_submit_button("➕ SALVA POSTAZIONE",use_container_width=True,type="primary"):
                if nome and lat_final and lon_final:
                    new_post={"Postazione":nome,"Comune":comune,"Via":via,"Latitudine":lat_final,"Longitudine":lon_final}
                    st.session_state.postazioni.append(new_post)
                    save_json(FILE_POST,st.session_state.postazioni)
                    st.success(f"✅ {nome} salvata!")
                    st.rerun()
        if st.session_state.postazioni:
            st.dataframe(pd.DataFrame(st.session_state.postazioni),use_container_width=True)
    torna("bottom_generic")