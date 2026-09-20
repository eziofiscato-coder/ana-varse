import streamlit as st
import pandas as pd
from io import BytesIO
import os, json, hashlib
from datetime import datetime, date

try:
    import folium
    from streamlit_folium import st_folium
    HAS=True
except:
    HAS=False

try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PIL=True
except:
    HAS_PIL=False

st.set_page_config(
    page_title="ANA Varese",
    layout="wide"
)

st.markdown("""
<style>
.stApp{background-color:#e8f5e9!important}
.stForm{background-color:#f1f8e9!important;
 border:2px solid #81c784!important;
 border-radius:12px!important;
 padding:20px!important}
.stButton>button{
 background-color:#d32f2f!important;
 color:white!important;
 border:2px solid #b71c1c!important;
 font-weight:bold!important}
</style>
""", unsafe_allow_html=True)

def load(f,d):
    try:
        if os.path.exists(f):
            with open(f,'r',encoding='utf-8') as file:
                return json.load(file)
    except:
        pass
    return d

def save(f,d):
    try:
        with open(f,'w',encoding='utf-8') as file:
            json.dump(d,file,indent=2)
    except:
        pass

def hp(p):
    return hashlib.sha256(p.encode()).hexdigest()

def fmt_date(d):
    if isinstance(d,date):
        return d.strftime("%d/%m/%Y")
    return str(d)

def export_excel(df):
    out=BytesIO()
    with pd.ExcelWriter(out,engine='openpyxl') as w:
        df.to_excel(w,index=False)
    return out.getvalue()

def crea_tesserino(vol,foto_path,template_path):
    try:
        if not HAS_PIL:
            return None
        if template_path and os.path.exists(template_path):
            base=Image.open(template_path)
            base=base.convert("RGB")
            tess=base.copy()
            draw=ImageDraw.Draw(tess)
        else:
            tess=Image.new('RGB',(860,540),'white')
            draw=ImageDraw.Draw(tess)
        try:
            fn=ImageFont.truetype("arialbd.ttf",20)
            fo=ImageFont.truetype("arial.ttf",14)
        except:
            fn=ImageFont.load_default()
            fo=ImageFont.load_default()
        W,H=tess.size
        fx=int(W*0.015)
        fy=int(H*0.22)
        fw=int(W*0.27)
        fh=int(H*0.58)
        if foto_path and os.path.exists(foto_path):
            try:
                foto=Image.open(foto_path)
                foto=foto.convert("RGB")
                foto=foto.resize((fw,fh))
                tess.paste(foto,(fx,fy))
            except:
                pass
        nx=int(W*0.38)
        ny=int(H*0.36)
        draw.rectangle(
            [nx,ny-5,nx+int(W*0.55),ny+int(H*0.15)],
            fill='white'
        )
        draw.text(
            (nx,ny),
            vol.get('Nome','').upper(),
            fill='black',
            font=fn
        )
        odv=vol.get('ODV','A.N.A. Sezione di Varese')
        oy=ny+int(H*0.12)
        draw.rectangle(
            [nx,oy-2,nx+int(W*0.5),oy+int(H*0.08)],
            fill='white'
        )
        draw.text(
            (nx,oy),
            odv,
            fill='black',
            font=fo
        )
        buf=BytesIO()
        tess.save(buf,format='PNG')
        buf.seek(0)
        return buf.getvalue()
    except Exception as e:
        st.error(f"Errore: {e}")
        return None

FD='dati.json'
FU='utenti.json'
FP='post.json'
FI='icone.json'
FE='emerg.json'
FC='check.json'
FR='radio.json'
FR2='cons.json'

for k,v in [
    ('dati',[]),('post',[]),('icone',[]),
    ('emerg',[]),('check',[]),('radio',[]),
    ('cons',[]),('interventi_lista',[]),
    ('menu','Dashboard'),('auth',False),
    ('lat',45.8205),('lon',8.8250),
    ('com',''),('via',''),('zoom',16),
    ('clat',None),('clon',None),
    ('exp1',False),('popup_shown',False)
]:
    if k not in st.session_state:
        st.session_state[k]=v

st.session_state.dati=load(FD,[])
st.session_state.post=load(FP,[])
st.session_state.icone=load(FI,[])
st.session_state.emerg=load(FE,[])
st.session_state.check=load(FC,[])
st.session_state.radio=load(FR,[])
st.session_state.cons=load(FR2,[])
st.session_state.interventi_lista=load(FE,[])

uts=load(FU,[])
if not uts:
    uts=[{
        'username':'admin',
        'password':hp('ana2024')
    }]
    save(FU,uts)

def header():
    c1,c2=st.columns([1,5])
    with c1:
        try:
            st.image("logo.png",width=130)
        except:
            st.write("ANA")
    with c2:
        st.markdown(
            "<div style='background:#a5d6a7;"
            "padding:15px;border-radius:8px;"
            "border:2px solid #0e7a3d;"
            "text-align:center;'>"
            "<b style='color:#000;font-size:26px;'>"
            "VOLONTARIATO<br>Sezione di Varese"
            "</b></div>",
            unsafe_allow_html=True
        )

def torna():
    if st.button('TORNA ALLA DASHBOARD'):
        st.session_state.menu='Dashboard'
        st.rerun()

# PRIMA PAGINA - SOLO FOTO PICCOLA
if not st.session_state.popup_shown:
    st.markdown(
        "<h1 style='text-align:center;color:#0e7a3d;'>"
        "ANA VARESE - VOLONTARIATO</h1>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<h3 style='text-align:center;color:#0e7a3d;'>"
        "Ciao Ragazzi, Buon Lavoro!</h3>",
        unsafe_allow_html=True
    )
    st.divider()
    c1,c2,c3=st.columns([1,1,1])
    with c2:
        found=False
        for img_name in [
            'copertina.jpg',
            'copertina_fumetto.jpg'
        ]:
            if os.path.exists(img_name):
                try:
                    st.image(img_name,width=250)
                    st.success("TUA IMMAGINE PICCOLA")
                    found=True
                    break
                except:
                    pass
        if not found:
            st.warning("Carica copertina.jpg")
        if st.button(
            "ENTRA NEL SISTEMA",
            type="primary",
            use_container_width=True
        ):
            st.session_state.popup_shown=True
            st.rerun()
    st.stop()

# LOGIN - RIPRISTINATO
if not st.session_state.auth:
    header()
    c1,c2,c3=st.columns([1,2,1])
    with c2:
        st.markdown("### LOGIN")
        for img_name in ['copertina.jpg']:
            if os.path.exists(img_name):
                try:
                    st.image(img_name,width=200)
                    break
                except:
                    pass
        with st.form('login'):
            u=st.text_input(
                'Username',
                value='admin'
            )
            p=st.text_input(
                'Password',
                type='password',
                value='ana2024'
            )
            ok=st.form_submit_button('ACCEDI')
            if ok:
                ph=hp(p)
                for ut in uts:
                    if ut['username']==u:
                        if ut['password']==ph:
                            st.session_state.auth=True
                            st.rerun()
                st.error('Errati')
        if st.button('TORNA INIZIO'):
            st.session_state.popup_shown=False
            st.rerun()
    st.stop()

def pagina_interventi():
    st.markdown("## INTERVENTI EMERGENZA")
    with st.form("form_emergenza",clear_on_submit=True):
        c1,c2,c3=st.columns(3)
        with c1:
            data_int=st.date_input("Data *")
            ora_int=st.time_input("Ora *")
        with c2:
            comune_int=st.text_input("Comune *")
            via_int=st.text_input("Via *")
        with c3:
            civico_int=st.text_input("Civico")
            odv_int=st.selectbox(
                "ODV Operativa *",
                ["ANA Varese",
                 "Protezione Civile Lombardia",
                 "Croce Rossa","Altro"]
            )
        azione_int=st.text_area(
            "Azione *",
            height=100
        )
        salva=st.form_submit_button(
            "SALVA INTERVENTO",
            use_container_width=True
        )
        if salva:
            if comune_int and via_int and azione_int:
                nuovo={
                    "Data":str(data_int),
                    "Ora":str(ora_int),
                    "Comune":comune_int,
                    "Via":via_int,
                    "Civico":civico_int,
                    "ODV":odv_int,
                    "Azione":azione_int
                }
                st.session_state.interventi_lista.append(
                    nuovo
                )
                save(
                    FE,
                    st.session_state.interventi_lista
                )
                st.success("Salvato!")
                st.rerun()
    if st.session_state.interventi_lista:
        df=pd.DataFrame(
            st.session_state.interventi_lista
        )
        st.dataframe(df,use_container_width=True)

def pagina_backup():
    st.markdown("## BACKUP - EXPORT IMPORT")
    tab_exp,tab_imp,tab_all=st.tabs([
        "EXPORT","IMPORT","COMPLETO"
    ])
    with tab_exp:
        c1,c2,c3=st.columns(3)
        with c1:
            if st.session_state.dati:
                st.download_button(
                    'EXPORT VOLONTARI',
                    export_excel(
                        pd.DataFrame(st.session_state.dati)
                    ),
                    file_name='Volontari.xlsx',
                    use_container_width=True,
                    key='exp_vol'
                )
            if st.session_state.post:
                st.download_button(
                    'EXPORT MAPPA',
                    export_excel(
                        pd.DataFrame(st.session_state.post)
                    ),
                    file_name='Mappa.xlsx',
                    use_container_width=True,
                    key='exp_mappa'
                )
        with c2:
            if st.session_state.interventi_lista:
                st.download_button(
                    'EXPORT INTERVENTI',
                    export_excel(
                        pd.DataFrame(
                            st.session_state.interventi_lista
                        )
                    ),
                    file_name='Interventi.xlsx',
                    use_container_width=True,
                    key='exp_int'
                )
        with c3:
            if st.session_state.radio:
                st.download_button(
                    'EXPORT RADIO',
                    export_excel(
                        pd.DataFrame(st.session_state.radio)
                    ),
                    file_name='Radio.xlsx',
                    use_container_width=True,
                    key='exp_radio'
                )
    with tab_imp:
        c1,c2=st.columns(2)
        with c1:
            up_vol=st.file_uploader(
                'Import Volontari',
                type=['xlsx'],
                key='up_vol'
            )
            if up_vol:
                df_up=pd.read_excel(up_vol)
                if st.button(
                    '