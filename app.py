import streamlit as st
import pandas as pd
from io import BytesIO
import os, json, hashlib
from datetime import datetime

try:
    import folium
    from folium.plugins import Fullscreen
    from streamlit_folium import st_folium
    HAS_MAP=True
except:
    HAS_MAP=False

try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PIL=True
except:
    HAS_PIL=False

st.set_page_config(
    page_title="ANA Varese",
    layout="wide"
)

# CSS CORTO - EVITA RIGHE LUNGHE
st.markdown("""
<style>
.ana-box {
 background:#e8f5e9;
 padding:15px;
 border-radius:10px;
 border:2px solid #0e7a3d;
}
.ana-head {
 background:#0e7a3d;
 padding:10px;
 border-radius:8px;
 color:white;
 text-align:center;
}
.stForm {
 background:#e8f5e9;
 border:2px solid #0e7a3d;
 border-radius:10px;
}
h2,h3,h4 { color:#0e7a3d; }
</style>
""", unsafe_allow_html=True)

def load_json(fn, df):
    try:
        if os.path.exists(fn):
            f=open(fn,'r',encoding='utf-8')
            d=json.load(f)
            f.close()
            return d
    except:
        pass
    return df

def save_json(fn, d):
    try:
        f=open(fn,'w',encoding='utf-8')
        json.dump(d,f,indent=2)
        f.close()
    except:
        pass

def hpwd(p):
    return hashlib.sha256(p.encode()).hexdigest()

def exp_excel(df):
    out=BytesIO()
    with pd.ExcelWriter(out,engine='openpyxl') as w:
        df.to_excel(w,index=False)
    return out.getvalue()

def tess_make(vol, foto, tmpl):
    try:
        if not HAS_PIL:
            return None
        W=860
        H=540
        if tmpl and os.path.exists(tmpl):
            base=Image.open(tmpl).convert("RGB")
            if base.size[0] > W:
                base=base.resize(
                    (W,H),Image.LANCZOS
                )
            tess=base.copy()
            if tess.size!= (W,H):
                tess=tess.resize(
                    (W,H),Image.LANCZOS
                )
            dr=ImageDraw.Draw(tess)
        else:
            tess=Image.new('RGB',(W,H),'white')
            dr=ImageDraw.Draw(tess)
            dr.rectangle(
                [0,0,W,H],
                outline="#0e7a3d",
                width=8
            )
        try:
            fb=ImageFont.truetype(
                "arialbd.ttf",22
            )
            fs=ImageFont.truetype(
                "arial.ttf",16
            )
        except:
            fb=ImageFont.load_default()
            fs=ImageFont.load_default()
        fx=20
        fy=100
        fw=220
        fh=310
        if foto and os.path.exists(foto):
            im=Image.open(foto).convert("RGB")
            im=im.resize((fw,fh),Image.LANCZOS)
            tess.paste(im,(fx,fy))
        nx=290
        ny=170
        dr.rectangle(
            [nx,ny,nx+430,ny+25],
            fill='white'
        )
        dr.text(
            (nx,ny),
            vol.get('Nome','').upper(),
            fill='black',
            font=fb
        )
        odv=vol.get('ODV','ANA')
        oy=ny+30
        dr.rectangle(
            [nx,oy,nx+430,oy+20],
            fill='white'
        )
        dr.text(
            (nx,oy),odv,
            fill='#0e7a3d',font=fs
        )
        buf=BytesIO()
        tess.save(buf,format='PNG',dpi=(300,300))
        buf.seek(0)
        return buf.getvalue()
    except:
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
FCHAT='chat.json'

init=[
    ('dati',[]),
    ('post',[]),
    ('icone',[]),
    ('emerg',[]),
    ('check',[]),
    ('radio',[]),
    ('cons',[]),
    ('eventi',[]),
    ('interv',[]),
    ('chat',[]),
    ('menu','Dashboard'),
    ('auth',False),
    ('popup',False),
    ('edit_idx',-1),
    ('edit_map',-1),
    ('sel_lat','45.8205'),
    ('sel_lon','8.8250'),
    ('sel_comune','Varese'),
    ('sel_via',''),
    ('sel_icon','Default'),
    ('chat_user','')
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
st.session_state.interv=load_json(FE,[])
st.session_state.chat=load_json(FCHAT,[])

uts=load_json(FU,[])
if not uts:
    uts=[{
        'username':'admin',
        'password':hpwd('ana2024')
    }]
    save_json(FU,uts)

def hdr():
    a,b=st.columns([1,5])
    with a:
        try:
            if os.path.exists("fumetto.png"):
                st.image("fumetto.png",width=100)
            elif os.path.exists("ezio_fumetto.png"):
                st.image("ezio_fumetto.png",width=100)
            elif os.path.exists("logo.png"):
                st.image("logo.png",width=100)
            else:
                st.write("ANA")
        except:
            st.write("ANA")
    with b:
        st.markdown(
            "<div class='ana-head'>"
            "<b>A.N.A. VARESE</b></div>",
            unsafe_allow_html=True
        )

def to_dash():
    if st.button('TORNA DASHBOARD'):
        st.session_state.menu='Dashboard'
        st.rerun()

if not st.session_state.popup:
    hdr()
    st.markdown(
        "<div class='ana-box'>"
        "<h3 style='text-align:center;'>"
        "Buon Lavoro!</h3></div>",
        unsafe_allow_html=True
    )
    # FUMETTO PRIMA PAGINA
    st.markdown("<div class='ana-box'>", unsafe_allow_html=True)
    try:
        if os.path.exists("fumetto.png"):
            st.image("fumetto.png",width=300)
        elif os.path.exists("ezio_fumetto.png"):
            st.image("ezio_fumetto.png",width=300)
        elif os.path.exists("logo.png"):
            st.image("logo.png",width=250)
    except:
        st.write("Carica fumetto.png")
    st.markdown("</div>", unsafe_allow_html=True)
    c1,c2,c3=st.columns([1,1,1])
    with c2:
        if st.button("ENTRA"):
            st.session_state.popup=True
            st.rerun()
    st.stop()

if not st.session_state.auth:
    hdr()
    c1,c2,c3=st.columns([1,2,1])
    with c2:
        st.markdown(
            "<div class='ana-box'>",
            unsafe_allow_html=True
        )
        with st.form('login'):
            u=st.text_input('User',value='admin')
            p=st.text_input(
                'Pwd',type='password',value='ana2024'
            )
            ok=st.form_submit_button('ACCEDI')
            if ok:
                ph=hpwd(p)
                for ut in uts:
                    if ut['username']==u and ut['password']==ph:
                        st.session_state.auth=True
                        st.session_state.menu='Dashboard'
                        st.session_state.popup=True
                        st.session_state.chat_user=u
                        st.rerun()
                st.error('Err')
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

hdr()

with st.sidebar:
    st.markdown(
        "<div class='ana-head'><b>MENU</b></div>",
        unsafe_allow_html=True
    )
    opts=[
        'Dashboard',
        'Volontari',
        'Mappa',
        'Libreria Icone',
        'Interventi Emergenza',
        'Eventi',
        'Check In',
        'DB Radio',
        'Consegna Radio',
        'Chat Volontari',
        'Backup',
        'Tesserino',
        'Logout'
    ]
    sel=st.radio('Menu',opts,index=0)
    if sel=='Logout':
        st.session_state.auth=False
        st.session_state.popup=False
        st.rerun()
    st.session_state.menu=sel

sc=st.session_state.menu

if sc=='Dashboard':
    st.markdown(
        "<div class='ana-box'><h2>Dashboard ANA</h2></div>",
        unsafe_allow_html=True
    )
    c1,c2,c3,c4=st.columns(4)
    with c1:
        if st.button('VOLONTARI'):
            st.session_state.menu='Volontari'
            st.rerun()
        if st.button('MAPPA'):
            st.session_state.menu='Mappa'
            st.rerun()
    with c2:
        if st.button('ICONE'):
            st.session_state.menu='Libreria Icone'
            st.rerun()
        if st.button('CHAT'):
            st.session_state.menu='Chat Volontari'
            st.rerun()
    with c3:
        if st.button('INTERVENTI'):
            st.session_state.menu='Interventi Emergenza'
            st.rerun()
        if st.button('EVENTI'):
            st.session_state.menu='Eventi'
            st.rerun()
    with c4:
        if st.button('BACKUP'):
            st.session_state.menu='Backup'
            st.rerun()
        if st.button('TESSERINO'):
            st.session_state.menu='Tesserino'
            st.rerun()
    st.divider()
    c1,c2,c3,c4=st.columns(4)
    with c1:
        st.metric('Vol',len(st.session_state.dati))
    with c2:
        st.metric('Post',len(st.session_state.post))
    with c3:
        st.metric('Icone',len(st.session_state.icone))
    with c4:
        st.metric('Chat',len(st.session_state.chat))
    st.markdown(
        "<div class='ana-box'><h3>Chat Dashboard</h3>",
        unsafe_allow_html=True
    )
    if st.session_state.chat:
        for msg in st.session_state.chat[-5:]:
            st.write(
                f"{msg.get('User','')}: "
                f"{msg.get('Text','')} - "
                f"{msg.get('Time','')}"
            )
    else:
        st.info("Nessun msg")
    if st.button("VAI CHAT"):
        st.session_state.menu='Chat Volontari'
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

elif sc=='Volontari':
    to_dash()
    st.markdown(
        "<div class='ana-head'>"
        "<b>VOLONTARI - ALETTE</b></div>",
        unsafe_allow_html=True
    )
    if st.session_state.edit_idx >=0:
        vol=st.session_state.dati[st.session_state.edit_idx]
        st.success(f"Modifica: {vol.get('Nome','')}")
        st.markdown(
            "<div class='ana-box'>",
            unsafe_allow_html=True
        )
        with st.form("edit_vol"):
            e_nome=st.text_input(
                "Nome",value=vol.get('Nome','')
            )
            e_cf=st.text_input(
                "CF",value=vol.get('CF','')
            )
            e_ind=st.text_input(
                "Via",value=vol.get('Indirizzo','')
            )
            e_com=st.text_input(
                "Comune",value=vol.get('Comune','')
            )
            e_tel=st.text_input(
                "Tel",value=vol.get('Telefono','')
            )
            e_odv=st.text_input(
                "ODV",value=vol.get('ODV','')
            )
            e_tess=st.text_input(
                "Tess",value=vol.get('Tessera','')
            )
            e_ruolo=st.text_input(
                "Ruolo",value=vol.get('Ruolo','')
            )
            e_mail=st.text_input(
                "Email",value=vol.get('Email','')
            )
            b1,b2,b3=st.columns(3)
            with b1:
                bs=st.form_submit_button("SALVA")
            with b2:
                ba=st.form_submit_button("ANNULLA")
            with b3:
                bd=st.form_submit_button("ELIMINA")
            if bs:
                vol['Nome']=e_nome
                vol['CF']=e_cf
                vol['Indirizzo']=e_ind
                vol['Comune']=e_com
                vol['ODV']=e_odv
                vol['Tessera']=e_tess
                vol['Ruolo']=e_ruolo
                vol['Telefono']=e_tel
                vol['Email']=e_mail
                st.session_state.dati[
                    st.session_state.edit_idx
                ]=vol
                save_json(FD,st.session_state.dati)
                st.session_state.edit_idx=-1
                st.rerun()
            if bd:
                st.session_state.dati.pop(
                    st.session_state.edit_idx
                )
                save_json(FD,st.session_state.dati)
                st.session_state.edit_idx=-1
                st.rerun()
            if ba:
                st.session_state.edit_idx=-1
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='ana-box'>",
        unsafe_allow_html=True
    )
    st.markdown("#### CON ALETTE SOPRA")
    tab1, tab2, tab3, tab4 = st.tabs([
        "ALETTA 1 - ANAGRAFICA",
        "ALETTA 2 - CONTATTI",
        "ALETTA 3 - FOTO",
        "ALETTA 4 - TESSERINO"
    ])
    with tab1:
        with st.form("anag"):
            a_nome=st.text_input("Nome *")
            a_cogn=st.text_input("Cognome *")
            a_cf=st.text_input("CF *")
            a_tel=st.text_input("Telefono")
            a_ind=st.text_input("Indirizzo")
            a_com=st.text_input("Comune")
            a_odv=st.text_input("ODV")
            a_tess=st.text_input("Tessera")
            a_ruolo=st.text_input("Ruolo")
            a_mail=st.text_input("Email")
            b1=st.form_submit_button("SALVA")
            if b1:
                if a_nome and a_cogn:
                    nc=f"{a_nome} {a_cogn}"
                    nuovo={
                        'Nome':nc,
                        'CF':a_cf,
                        'Indirizzo':a_ind,
                        'Comune':a_com,
                        'ODV':a_odv,
                        'Tessera':a_tess,
                        'Ruolo':a_ruolo,
                        'FotoFile':'',
                        'Telefono':a_tel,
                        'Email':a_mail
                    }
                    st.session_state.dati.append(nuovo)
                    save_json(FD,st.session_state.dati)
                    st.success("OK")
                    st.rerun()
    with tab2:
        vlist=[d.get('Nome','') for d in st.session_state.dati]
        if vlist:
            sel=st.selectbox("Vol",vlist,key='c2')
            idx=-1
            for i,d in enumerate(st.session_state.dati):
                if d.get('Nome','')==sel:
                    idx=i
                    break
            if idx>=0:
                vol=st.session_state.dati[idx]
                st.write(f"Tel: {vol.get('Telefono','')}")
                st.write(f"Email: {vol.get('Email','')}")
    with tab3:
        vlist=[d.get('Nome','') for d in st.session_state.dati]
        if vlist:
            sel=st.selectbox("Vol",vlist,key='c3')
            idx=-1
            for i,d in enumerate(st.session_state.dati):
                if d.get('Nome','')==sel:
                    idx=i
                    break
            if idx>=0:
                fp=st.session_state.dati[idx].get('FotoFile','')
                if fp and os.path.exists(fp):
                    st.image(fp,width=200)
                up=st.file_uploader(
                    "Foto",type=['jpg','jpeg','png']
                )
                if up:
                    st.image(up,width=200)
                    if st.button("SALVA FOTO"):
                        os.makedirs(
                            'foto_volontari',exist_ok=True
                        )
                        fn=f"foto_volontari/{sel.replace(' ','_')}_{up.name}"
                        fout=open(fn,'wb')
                        fout.write(up.getbuffer())
                        fout.close()
                        st.session_state.dati[idx]['FotoFile']=fn
                        save_json(FD,st.session_state.dati)
                        st.success("OK foto")
                        st.rerun()
    with tab4:
        vlist=[d.get('Nome','') for d in st.session_state.dati]
        if vlist:
            sel=st.selectbox("Vol",vlist,key='c4')
            idx=-1
            for i,d in enumerate(st.session_state.dati):
                if d.get('Nome','')==sel:
                    idx=i
                    break
            if idx>=0:
                vol=st.session_state.dati[idx]
                tess=tess_make(
                    vol,vol.get('FotoFile',''),
                    "Tesserino-Ezio.JPG" if os.path.exists(
                        "Tesserino-Ezio.JPG"
                    ) else None
                )
                if tess:
                    st.image(tess)
                    st.download_button(
                        'SCARICA',tess,
                        file_name=f"Tess_{vol.get('Nome','')}.png",
                        mime='image/png',
                        key='tess_dl'
                    )
    st.markdown("</div>", unsafe_allow_html=True)
    if st.session_state.dati:
        df=pd.DataFrame(st.session_state.dati)
        ev=st.dataframe(
            df,on_select="rerun",
            selection_mode="single-row",
            key='vol_list'
        )
        if ev and ev.selection and ev.selection.rows:
            st.session_state.edit_idx=ev.selection.rows[0]
            st.rerun()

elif sc=='Mappa':
    to_dash()
    st.markdown(
        "<div class='ana-head'>"
        "<b>MAPPA - SALVA TUTTE + CANCELLA</b></div>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<div class='ana-box'>",
        unsafe_allow_html=True
    )
    c1,c2=st.columns(2)
    with c1:
        mt=st.selectbox(
            "Tipo mappa",
            ['Standard','Google Map','Satellite',
             'Terreno','Waze Chiaro','Waze Scuro'],
            index=0,key='mt'
        )
    with c2:
        lst_icon=['Default']
        if st.session_state.icone:
            lst_icon=[]
            for it in st.session_state.icone:
                lst_icon.append(it.get('Nome','Default'))
        sel_icon=st.selectbox(
            "Icona",lst_icon,key='sel_icon_lib'
        )
        st.session_state.sel_icon=sel_icon
    st.markdown("</div>", unsafe_allow_html=True)
    if HAS_MAP:
        try:
            if mt=='Google Map':
                mm=folium.Map(
                    location=[45.8205,8.8250],
                    zoom_start=12,
                    tiles='https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',
                    attr='Google'
                )
            elif mt=='Satellite':
                mm=folium.Map(
                    location=[45.8205,8.8250],
                    zoom_start=12,
                    tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
                    attr='Google Sat'
                )
            elif mt=='Terreno':
                mm=folium.Map(
                    location=[45.8205,8.8250],
                    zoom_start=12,
                    tiles='Stamen Terrain',
                    attr='Stamen'
                )
            elif mt=='Waze Chiaro':
                mm=folium.Map(
                    location=[45.8205,8.8250],
                    zoom_start=12,
                    tiles='CartoDB positron',
                    attr='CartoDB'
                )
            elif mt=='Waze Scuro':
                mm=folium.Map(
                    location=[45.8205,8.8250],
                    zoom_start=12,
                    tiles='CartoDB dark_matter',
                    attr='CartoDB'
                )
            else:
                mm=folium.Map(
                    location=[45.8205,8.8250],
                    zoom_start=12,
                    tiles='OpenStreetMap'
                )
            Fullscreen(
                position='topleft',
                title='Tutto schermo',
                title_cancel='Ritorna',
                force_separate_button=True
            ).add_to(mm)
            for p in st.session_state.post:
                lat=p.get('Lat','45.8205')
                lon=p.get('Lon','8.8250')
                nome=p.get('Nome','')
                icona_nome=p.get('Icona','Default')
                icon_file=""
                for ic in st.session_state.icone:
                    if ic.get('Nome','')==icona_nome:
                        icon_file=ic.get('File','')
                if icon_file and os.path.exists(icon_file):
                    icon=folium.CustomIcon(
                        icon_file,icon_size=(40,40)
                    )
                    folium.Marker(
                        [float(lat),float(lon)],
                        popup=nome,icon=icon
                    ).add_to(mm)
                else:
                    folium.Marker(
                        [float(lat),float(lon)],
                        popup=nome
                    ).add_to(mm)
            sla=st.session_state.sel_lat
            slo=st.session_state.sel_lon
            if sla!='45.8205' or slo!='8.8250':
                icon_file=""
                for ic