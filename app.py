import streamlit as st
import pandas as pd
from io import BytesIO
import os, json, hashlib
from datetime import date

try:
    import folium
    from streamlit_folium import st_folium
    HAS_MAP=True
except Exception:
    HAS_MAP=False

try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PIL=True
except Exception:
    HAS_PIL=False

st.set_page_config(page_title="ANA Varese", layout="wide")

st.markdown("""
<style>
.stApp{background:#e8f5e9!important}
.stForm{background:#f1f8e9!important;
 border:2px solid #81c784!important;
 border-radius:12px!important; padding:10px!important}
.stButton>button{
 background:#d32f2f!important; color:white!important;
 border:2px solid #b71c1c!important; font-weight:bold!important}
</style>
""", unsafe_allow_html=True)

def load_json(fname, default):
    try:
        if os.path.exists(fname):
            f=open(fname,'r',encoding='utf-8')
            data=json.load(f)
            f.close()
            return data
    except Exception:
        pass
    return default

def save_json(fname, data):
    try:
        f=open(fname,'w',encoding='utf-8')
        json.dump(data,f,indent=2)
        f.close()
    except Exception:
        pass

def hpwd(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()

def export_excel(df):
    out=BytesIO()
    writer=pd.ExcelWriter(out,engine='openpyxl')
    df.to_excel(writer,index=False)
    writer.close()
    return out.getvalue()

def make_barcode(cf):
    try:
        import barcode
        from barcode.writer import ImageWriter
        txt=(cf or "0000000000000000")[:16].upper()
        code=barcode.get('code128',txt,writer=ImageWriter())
        buf=BytesIO()
        code.write(buf)
        buf.seek(0)
        return buf.getvalue()
    except Exception:
        return None

def make_tessera(vol, foto_path, tmpl):
    try:
        if not HAS_PIL:
            return None
        W=860
        H=540
        if tmpl and os.path.exists(tmpl):
            base=Image.open(tmpl).convert("RGB")
            if base.size[0] > W:
                base=base.resize((W,H),Image.LANCZOS)
            tess=base.copy()
            if tess.size!= (W,H):
                tess=tess.resize((W,H),Image.LANCZOS)
            draw=ImageDraw.Draw(tess)
        else:
            tess=Image.new('RGB',(W,H),'white')
            draw=ImageDraw.Draw(tess)
            draw.rectangle([0,0,W,H],outline="#0e7a3d",width=8)
        try:
            font_big=ImageFont.truetype("arialbd.ttf",22)
            font_small=ImageFont.truetype("arial.ttf",16)
        except Exception:
            font_big=ImageFont.load_default()
            font_small=ImageFont.load_default()
        fx=int(W*0.02)
        fy=int(H*0.18)
        fw=int(W*0.26)
        fh=int(H*0.58)
        if foto_path and os.path.exists(foto_path):
            try:
                foto=Image.open(foto_path).convert("RGB")
                foto=foto.resize((fw,fh),Image.LANCZOS)
                tess.paste(foto,(fx,fy))
            except Exception:
                pass
        nx=int(W*0.34)
        ny=int(H*0.32)
        draw.rectangle([nx,ny,nx+int(W*0.5),ny+25],fill='white')
        draw.text((nx,ny),vol.get('Nome','').upper(),fill='black',font=font_big)
        odv=vol.get('ODV','A.N.A. NUCLEO VOLONTARI DI PROTEZIONE CIVILE SEZIONE DI VARESE')
        oy=ny+30
        draw.rectangle([nx,oy,nx+int(W*0.5),oy+20],fill='white')
        draw.text((nx,oy),odv,fill='#0e7a3d',font=font_small)
        bx=int(W*0.62)
        by=int(H*0.70)
        bw=int(W*0.34)
        bh=int(H*0.16)
        draw.rectangle([bx,by,bx+bw,by+bh],fill='white',outline='white')
        cf=vol.get('CF','')
        if not cf:
            cf=vol.get('Nome','').replace(' ','').upper()[:16]
        bc=make_barcode(cf)
        if bc:
            try:
                bi=Image.open(BytesIO(bc)).convert("RGB")
                bi=bi.resize((bw,bh),Image.LANCZOS)
                tess.paste(bi,(bx,by))
            except Exception:
                pass
        buf=BytesIO()
        tess.save(buf,format='PNG',dpi=(300,300))
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
FEV='eventi.json'

init_vals=[
    ('dati',[]),('post',[]),('icone',[]),
    ('emerg',[]),('check',[]),('radio',[]),
    ('cons',[]),('eventi',[]),
    ('interventi_lista',[]),('menu','Dashboard'),
    ('auth',False),('popup_shown',False),
    ('edit_idx',-1),('edit_map_idx',-1),
    ('sel_lat',45.8205),('sel_lon',8.8250)
]

for key,val in init_vals:
    if key not in st.session_state:
        st.session_state[key]=val

st.session_state.dati=load_json(FD,[])
st.session_state.post=load_json(FP,[])
st.session_state.icone=load_json(FI,[])
st.session_state.emerg=load_json(FE,[])
st.session_state.check=load_json(FC,[])
st.session_state.radio=load_json(FR,[])
st.session_state.cons=load_json(FR2,[])
st.session_state.eventi=load_json(FEV,[])
st.session_state.interventi_lista=load_json(FE,[])

uts=load_json(FU,[])
if not uts:
    uts=[{'username':'admin','password':hpwd('ana2024')}]
    save_json(FU,uts)

def header_box():
    colA,colB=st.columns([1,5])
    with colA:
        try:
            st.image("logo.png",width=110)
        except Exception:
            st.write("ANA")
    with colB:
        st.markdown(
            "<div style='background:#0e7a3d;padding:14px;"
            "border-radius:8px;text-align:center;'>"
            "<b style='color:white;font-size:18px;'>"
            "A.N.A. NUCLEO VOLONTARI DI PROTEZIONE CIVILE<br>"
            "SEZIONE DI VARESE</b></div>",
            unsafe_allow_html=True
        )

def go_dashboard():
    if st.button('TORNA ALLA DASHBOARD'):
        st.session_state.menu='Dashboard'
        st.rerun()

if not st.session_state.popup_shown:
    header_box()
    st.markdown("<h3 style='text-align:center;color:#0e7a3d;'>Ciao Ragazzi, Buon Lavoro!</h3>", unsafe_allow_html=True)
    st.divider()
    c1,c2,c3=st.columns([1,1,1])
    with c2:
        if os.path.exists('copertina.jpg'):
            try:
                st.image('copertina.jpg',width=250)
            except Exception:
                pass
        if st.button("ENTRA NEL SISTEMA",type="primary",use_container_width=True):
            st.session_state.popup_shown=True
            st.rerun()
    st.stop()

if not st.session_state.auth:
    header_box()
    c1,c2,c3=st.columns([1,2,1])
    with c2:
        st.markdown("### LOGIN")
        with st.form('login'):
            u=st.text_input('Username',value='admin')
            p=st.text_input('Password',type='password',value='ana2024')
            ok=st.form_submit_button('ACCEDI',type="primary")
            if ok:
                ph=hpwd(p)
                for ut in uts:
                    if ut['username']==u and ut['password']==ph:
                        st.session_state.auth=True
                        st.session_state.menu='Dashboard'
                        st.session_state.popup_shown=True
                        st.rerun()
                st.error('Errati')
    st.stop()

header_box()

with st.sidebar:
    st.markdown('**MENU COMPLETO**')
    opts=['Dashboard','Volontari','Mappa','Libreria Icone','Interventi Emergenza','Eventi','Check In','DB Radio','Consegna Radio','Backup','Tesserino','Logout']
    sel=st.radio('Vai a',opts,index=0)
    if sel=='Logout':
        st.session_state.auth=False
        st.session_state.popup_shown=False
        st.rerun()
    st.session_state.menu=sel

scelta=st.session_state.menu

if scelta=='Dashboard':
    st.markdown("## Dashboard - A.N.A. NUCLEO VOLONTARI DI PROTEZIONE CIVILE SEZIONE DI VARESE")
    col1,col2=st.columns(2)
    with col1:
        if st.button('VOLONTARI',use_container_width=True):
            st.session_state.menu='Volontari'
            st.rerun()
        if st.button('MAPPA',use_container_width=True):
            st.session_state.menu='Mappa'
            st.rerun()
        if st.button('BACKUP',use_container_width=True,type="primary"):
            st.session_state.menu='Backup'
            st.rerun()
    with col2:
        if st.button('LIBRERIA ICONE',use_container_width=True):
            st.session_state.menu='Libreria Icone'
            st.rerun()
        if st.button('EVENTI',use_container_width=True):
            st.session_state.menu='Eventi'
            st.rerun()
        if st.button('TESSERINO NITIDO',use_container_width=True):
            st.session_state.menu='Tesserino'
            st.rerun()

elif scelta=='Volontari':
    go_dashboard()
    st.markdown("## VOLONTARI")
    if st.session_state.edit_idx >=0 and st.session_state.edit_idx < len(st.session_state.dati):
        vol=st.session_state.dati[st.session_state.edit_idx]
        st.success(f"VOLONTARIO SELEZIONATO: {vol.get('Nome','')} - MODIFICA IN MASCHERA")
        with st.form("form_edit_vol"):
            c1,c2=st.columns(2)
            with c1:
                e_nome=st.text_input("Nome",value=vol.get('Nome',''))
                e_cf=st.text_input("CF",value=vol.get('CF',''))
                e_ind=st.text_input("Indirizzo",value=vol.get('Indirizzo',''))
                e_comune=st.text_input("Comune",value=vol.get('Comune',''))
                e_tel=st.text_input("Telefono",value=vol.get('Telefono',''))
            with c2:
                e_odv=st.text_input("ODV",value=vol.get('ODV',''))
                e_tess=st.text_input("Tessera