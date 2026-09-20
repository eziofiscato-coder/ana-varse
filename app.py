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
 border-radius:12px!important; padding:8px!important}
.stButton>button{
 background:#d32f2f!important; color:white!important;
 border:2px solid #b71c1c!important; font-weight:bold!important}
</style>
""", unsafe_allow_html=True)

def load_json(fn, df):
    try:
        if os.path.exists(fn):
            f=open(fn,'r',encoding='utf-8')
            d=json.load(f)
            f.close()
            return d
    except Exception:
        pass
    return df

def save_json(fn, d):
    try:
        f=open(fn,'w',encoding='utf-8')
        json.dump(d,f,indent=2)
        f.close()
    except Exception:
        pass

def hpwd(p):
    return hashlib.sha256(p.encode()).hexdigest()

def exp_excel(df):
    out=BytesIO()
    w=pd.ExcelWriter(out,engine='openpyxl')
    df.to_excel(w,index=False)
    w.close()
    return out.getvalue()

def barcode_gen(cf):
    try:
        import barcode
        from barcode.writer import ImageWriter
        txt=(cf or "0000000000000000")[:16].upper()
        cd=barcode.get('code128',txt,writer=ImageWriter())
        buf=BytesIO()
        cd.write(buf)
        buf.seek(0)
        return buf.getvalue()
    except Exception:
        return None

def tessera_make(vol, foto, tmpl):
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
            dr=ImageDraw.Draw(tess)
        else:
            tess=Image.new('RGB',(W,H),'white')
            dr=ImageDraw.Draw(tess)
            dr.rectangle([0,0,W,H],outline="#0e7a3d",width=8)
        try:
            fb=ImageFont.truetype("arialbd.ttf",22)
            fs=ImageFont.truetype("arial.ttf",16)
        except Exception:
            fb=ImageFont.load_default()
            fs=ImageFont.load_default()
        fx=int(W*0.02)
        fy=int(H*0.18)
        fw=int(W*0.26)
        fh=int(H*0.58)
        if foto and os.path.exists(foto):
            try:
                im=Image.open(foto).convert("RGB")
                im=im.resize((fw,fh),Image.LANCZOS)
                tess.paste(im,(fx,fy))
            except Exception:
                pass
        nx=int(W*0.34)
        ny=int(H*0.32)
        dr.rectangle([nx,ny,nx+int(W*0.5),ny+25],fill='white')
        dr.text((nx,ny),vol.get('Nome','').upper(),fill='black',font=fb)
        odv=vol.get('ODV','A.N.A. Varese')
        oy=ny+30
        dr.rectangle([nx,oy,nx+int(W*0.5),oy+20],fill='white')
        dr.text((nx,oy),odv,fill='#0e7a3d',font=fs)
        bx=int(W*0.62)
        by=int(H*0.70)
        bw=int(W*0.34)
        bh=int(H*0.16)
        dr.rectangle([bx,by,bx+bw,by+bh],fill='white',outline='white')
        cf=vol.get('CF','')
        if not cf:
            cf=vol.get('Nome','').replace(' ','').upper()[:16]
        bc=barcode_gen(cf)
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
        st.error(f"Err: {e}")
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

init=[
    ('dati',[]),('post',[]),('icone',[]),
    ('emerg',[]),('check',[]),('radio',[]),
    ('cons',[]),('eventi',[]),
    ('interventi',[]),('menu','Dashboard'),
    ('auth',False),('popup',False),
    ('edit_idx',-1),('edit_map',-1),
    ('sel_lat',45.8205),('sel_lon',8.8250)
]

for k,v in init:
    if k not in st.session_state:
        st.session_state[k]=v

st.session_state.dati=load_json(FD,[])
st.session_state.post=load_json(FP,[])
st.session_state.icone=load_json(FI,[])
st.session_state.emerg=load_json(FE,[])
st.session_state.check=load_json(FC,[])
st.session_state.radio=load_json(FR,[])
st.session_state.cons=load_json(FR2,[])
st.session_state.eventi=load_json(FEV,[])
st.session_state.interventi=load_json(FE,[])

uts=load_json(FU,[])
if not uts:
    uts=[{'username':'admin','password':hpwd('ana2024')}]
    save_json(FU,uts)

def hdr():
    a,b=st.columns([1,5])
    with a:
        try:
            st.image("logo.png",width=110)
        except Exception:
            st.write("ANA")
    with b:
        st.markdown(
            "<div style='background:#0e7a3d;padding:14px;"
            "border-radius:8px;text-align:center;'>"
            "<b style='color:white;font-size:18px;'>"
            "A.N.A. NUCLEO VOLONTARI<br>"
            "SEZIONE DI VARESE</b></div>",
            unsafe_allow_html=True
        )

def to_dash():
    if st.button('DASHBOARD'):
        st.session_state.menu='Dashboard'
        st.rerun()

if not st.session_state.popup:
    hdr()
    st.markdown("<h3 style='text-align:center;color:#0e7a3d;'>Buon Lavoro!</h3>", unsafe_allow_html=True)
    st.divider()
    c1,c2,c3=st.columns([1,1,1])
    with c2:
        if os.path.exists('copertina.jpg'):
            try:
                st.image('copertina.jpg',width=250)
            except Exception:
                pass
        if st.button("ENTRA",type="primary",use_container_width=True):
            st.session_state.popup=True
            st.rerun()
    st.stop()

if not st.session_state.auth:
    hdr()
    c1,c2,c3=st.columns([1,2,1])
    with c2:
        st.markdown("### LOGIN")
        with st.form('login'):
            u=st.text_input('User',value='admin')
            p=st.text_input('Pwd',type='password',value='ana2024')
            ok=st.form_submit_button('ACCEDI',type="primary")
            if ok:
                ph=hpwd(p)
                for ut in uts:
                    if ut['username']==u and ut['password']==ph:
                        st.session_state.auth=True
                        st.session_state.menu='Dashboard'
                        st.session_state.popup=True
                        st.rerun()
                st.error('Errati')
    st.stop()

hdr()

with st.sidebar:
    st.markdown('**MENU**')
    opts=[
        'Dashboard','Volontari','Mappa',
        'Icone','Interventi','Eventi',
        'Check In','Radio','Consegna',
        'Backup','Tesserino','Logout'
    ]
    sel=st.radio('Vai',opts,index=0)
    if sel=='Logout':
        st.session_state.auth=False
        st.session_state.popup=False
        st.rerun()
    st.session_state.menu=sel

sc=st.session_state.menu

if sc=='Dashboard':
    st.markdown("## Dashboard")
    a,b=st.columns(2)
    with a:
        if st.button('VOLONTARI',use_container_width=True):
            st.session_state.menu='Volontari'
            st.rerun()
        if st.button('MAPPA',use_container_width=True):
            st.session_state.menu='Mappa'
            st.rerun()
        if st.button('BACKUP',use_container_width=True,type="primary"):
            st.session_state.menu='Backup'
            st.rerun()
    with b:
        if st.button('ICONE',use_container_width=True):
            st.session_state.menu='Icone'
            st.rerun()
        if st.button('EVENTI',use_container_width=True):
            st.session_state.menu='Eventi'
            st.rerun()
        if st.button('TESSERINO',use_container_width=True):
            st.session_state.menu='Tesserino'
            st.rerun()

elif sc=='Volontari':
    to_dash()
    st.markdown("## VOLONTARI")
    if st.session_state.edit_idx >=0:
        if st.session_state.edit_idx < len(st.session_state.dati):
            vol=st.session_state.dati[st.session_state.edit_idx]
            st.success(f"Modifica: {vol.get('Nome','')}")
            with st.form("edit_vol"):
                c1,c2=st.columns(2)
                with c1:
                    e_nome=st.text_input("Nome",value=vol.get('Nome',''))
                    e_cf=st.text_input("CF",value=vol.get('CF',''))
                    e_ind=st.text_input("Indirizzo",value=vol.get('Indirizzo',''))
                    e_com=st.text_input("Comune",value=vol.get('Comune',''))
                    e_tel=st.text_input("Tel",value=vol.get('Telefono',''))
                with c2:
                    e_odv=st.text_input("ODV",value=vol.get('ODV',''))
                    e_tess=st.text_input("Tessera",value=vol.get('Tessera',''))
                    e_ruolo=st.selectbox("Ruolo",["Volontario","Caposquadra","Coordinatore","Autista","Radio","Altro"])
                    e