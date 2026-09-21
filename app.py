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

st.set_page_config(page_title="ANA Varese", layout="wide")

st.markdown('''
<style>
.stForm{background:#e8f5e9;padding:15px;
border-radius:10px;border:2px solid #0e7a3d;}
.ana-box{background:#e8f5e9;padding:15px;
border-radius:10px;border:2px solid #0e7a3d;
margin-bottom:10px;}
.ana-head{background:#0e7a3d;padding:10px;
border-radius:8px;color:white;text-align:center;}
h2,h3,h4{color:#0e7a3d;}
</style>
''', unsafe_allow_html=True)

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

def tess_make(vol, foto, tmpl):
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
        dr.rectangle([nx,ny,nx+430,ny+25],fill='white')
        dr.text((nx,ny),vol.get('Nome','').upper(),fill='black',font=fb)
        odv=vol.get('ODV','ANA')
        oy=ny+30
        dr.rectangle([nx,oy,nx+430,oy+20],fill='white')
        dr.text((nx,oy),odv,fill='#0e7a3d',font=fs)
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
    uts=[{'username':'admin','password':hpwd('ana2024')}]
    save_json(FU,uts)

def hdr():
    a,b=st.columns([1,5])
    with a:
        try:
            if os.path.exists("copertina.png"):
                st.image("copertina.png",width=70)
            elif os.path.exists("logo.png"):
                st.image("logo.png",width=10)
            else:
                st.write("ANA")
        except:
            st.write("ANA")
    with b:
        st.markdown("<div class='ana-head'><b>NUCLEO DI VOLONTARI DI PROTEZIONE CIVILE ANA SEZIONE DI VARESE</b></div>", unsafe_allow_html=True)
def to_dash():
    if st.button('TORNA DASHBOARD'):
        st.session_state.menu='Dashboard'
        st.rerun()

if not st.session_state.popup:
    hdr()
    st.markdown("<div class='ana-head' style='font-size:38px; font-weight:times romano; padding:20px;'><b>ANA VARESE - PROTEZIONE CIVILE</b></div>", unsafe_allow_html=True)
    st.markdown("<div class='ana-box'>", unsafe_allow_html=True)
    try:
        if os.path.exists("copertina.png"):
            st.image("copertina.png",width=300)
        elif os.path.exists("logo.png"):
            st.image("logo.png",width=10)
    except:
        st.write("copertina.png")
    st.markdown("</div>", unsafe_allow_html=True)
    c1,c2,c3=st.columns([2,2,2])
    with c2:
        if st.button("ENTRA"):
            st.session_state.popup=True
            st.rerun()
    st.stop()

if not st.session_state.auth:
    hdr()
    c1,c2,c3=st.columns([1,2,1])
    with c2:
        with st.form('login'):
            u=st.text_input('User',value='admin')
            p=st.text_input('Pwd',type='password',value='ana2024')
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
    st.stop()

hdr()

with st.sidebar:
    st.markdown("<div class='ana-head'><b>MENU</b></div>", unsafe_allow_html=True)
    opts=['Dashboard','Volontari','Mappa','Libreria Icone','Interventi Emergenza','Eventi','Check In','DB Radio','Consegna Radio','Chat Volontari','Backup','Tesserino','Logout']
    sel=st.radio('Menu',opts,index=0)
    if sel=='Logout':
        st.session_state.auth=False
        st.session_state.popup=False
        st.rerun()
    st.session_state.menu=sel

sc=st.session_state.menu

if sc=='Dashboard':
    st.markdown("<div class='ana-box'><h2>Dashboard ANA</h2></div>", unsafe_allow_html=True)
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
    st.markdown("<div class='ana-box'><h3>Chat Dashboard</h3>", unsafe_allow_html=True)
    if st.session_state.chat:
        for msg in st.session_state.chat[-5:]:
            nm=msg.get('User','')
            tx=msg.get('Text','')
            tm=msg.get('Time','')
            st.write(f"{nm}: {tx} - {tm}")
    else:
        st.info("Nessun msg")
    if st.button("VAI CHAT"):
        st.session_state.menu='Chat Volontari'
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

elif sc=='Volontari':
    to_dash()
    st.markdown("<div class='ana-head'><b>VOLONTARI - ALETTE</b></div>", unsafe_allow_html=True)
    if st.session_state.edit_idx >=0:
        vol=st.session_state.dati[st.session_state.edit_idx]
        st.success(f"Modifica: {vol.get('Nome','')}")
        with st.form("edit_vol"):
            e_nome=st.text_input("Nome",value=vol.get('Nome',''))
            e_cf=st.text_input("CF",value=vol.get('CF',''))
            e_ind=st.text_input("Via",value=vol.get('Indirizzo',''))
            e_com=st.text_input("Comune",value=vol.get('Comune',''))
            e_tel=st.text_input("Tel",value=vol.get('Telefono',''))
            e_odv=st.text_input("ODV",value=vol.get('ODV',''))
            e_tess=st.text_input("Tess",value=vol.get('Tessera',''))
            e_ruolo=st.text_input("Ruolo",value=vol.get('Ruolo',''))
            e_mail=st.text_input("Email",value=vol.get('Email',''))
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
                st.session_state.dati[st.session_state.edit_idx]=vol
                save_json(FD,st.session_state.dati)
                st.session_state.edit_idx=-1
                st.rerun()
            if bd:
                st.session_state.dati.pop(st.session_state.edit_idx)
                save_json(FD,st.session_state.dati)
                st.session_state.edit_idx=-1
                st.rerun()
            if ba:
                st.session_state.edit_idx=-1
                st.rerun()
    st.markdown("<div class='ana-box'>CON ALETTE SOPRA</div>", unsafe_allow_html=True)
    tab1, tab2, tab3, tab4 = st.tabs(["ALETTA 1 - ANAGRAFICA","ALETTA 2 - CONTATTI","ALETTA 3 - FOTO","ALETTA 4 - TESSERINO"])
    with tab1:
        st.markdown("<div class='ana-box'>MASCHERA PRINCIPALE</div>", unsafe_allow_html=True)
        a_nome=st.text_input("Nome *",key="an_nome")
        a_cogn=st.text_input("Cognome *",key="an_cogn")
        a_cf=st.text_input("CF *",key="an_cf")
        a_tel=st.text_input("Telefono",key="an_tel")
        a_ind=st.text_input("Indirizzo",key="an_ind")
        a_com=st.text_input("Comune",key="an_com")
        a_odv=st.text_input("ODV",key="an_odv")
        a_tess=st.text_input("Tessera",key="an_tess")
        a_ruolo=st.text_input("Ruolo",key="an_ruolo")
        a_mail=st.text_input("Email",key="an_mail")
        if st.button("SALVA VOLONTARIO",key="an_salva"):
            if a_nome and a_cogn:
                nc=f"{a_nome} {a_cogn}"
                nuovo={'Nome':nc,'CF':a_cf,'Indirizzo':a_ind,'Comune':a_com,'ODV':a_odv,'Tessera':a_tess,'Ruolo':a_ruolo,'FotoFile':'','Telefono':a_tel,'Email':a_mail}
                st.session_state.dati.append(nuovo)
                save_json(FD,st.session_state.dati)
                st.success("OK")
                st.rerun()
    with tab2:
        st.markdown("<div class='ana-box'>SOTTOMASCHERA CONTATTI</div>", unsafe_allow_html=True)
        vlist=[]
        for d in st.session_state.dati:
            vlist.append(d.get('Nome',''))
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
        st.markdown("<div class='ana-box'>SOTTOMASCHERA FOTO</div>", unsafe_allow_html=True)
        vlist=[]
        for d in st.session_state.dati:
            vlist.append(d.get('Nome',''))
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
                up=st.file_uploader("Foto",type=['jpg','jpeg','png'],key="up3")
                if up:
                    st.image(up,width=200)
                    if st.button("SALVA FOTO",key="sf3"):
                        os.makedirs('foto_volontari',exist_ok=True)
                        fn="foto_volontari/"+sel.replace(' ','_')+"_"+up.name
                        fout=open(fn,'wb')
                        fout.write(up.getbuffer())
                        fout.close()
                        st.session_state.dati[idx]['FotoFile']=fn
                        save_json(FD,st.session_state.dati)
                        st.success("OK foto")
                        st.rerun()
    with tab4:
        st.markdown("<div class='ana-box'>SOTTOMASCHERA TESSERINO</div>", unsafe_allow_html=True)
        vlist=[]
        for d in st.session_state.dati:
            vlist.append(d.get('Nome',''))
        if vlist:
            sel=st.selectbox("Vol",vlist,key='c4')
            idx=-1
            for i,d in enumerate(st.session_state.dati):
                if d.get('Nome','')==sel:
                    idx=i
                    break
            if idx>=0:
                vol=st.session_state.dati[idx]
                tmpl="Tesserino-Ezio.JPG"
                if not os.path.exists(tmpl):
                    tmpl=None
                tess=tess_make(vol,vol.get('FotoFile',''),tmpl)
                if tess:
                    st.image(tess)
                    st.download_button('SCARICA',tess,file_name="Tess.png",mime='image/png',key='tess_dl')
    if st.session_state.dati:
        df=pd.DataFrame(st.session_state.dati)
        ev=st.dataframe(df,on_select="rerun",selection_mode="single-row",key='vol_list')
        if ev and ev.selection and ev.selection.rows:
            st.session_state.edit_idx=ev.selection.rows[0]
            st.rerun()

elif sc=='Mappa':
    to_dash()
    st.markdown("<div class='ana-head'><b>MAPPA - SALVA TUTTE + CANCELLA</b></div>", unsafe_allow_html=True)
    c1,c2=st.columns(2)
    with c1:
        mt=st.selectbox("Tipo",['Standard','Google Map','Satellite','Terreno','Waze Chiaro','Waze Scuro'],index=0,key='mt')
    with c2:
        lst_icon=['Default']
        for item in st.session_state.icone:
            lst_icon.append(item.get('Nome','Default'))
        sel_icon=st.selectbox("Icona",lst_icon,key='sel_icon_lib')
        st.session_state.sel_icon=sel_icon
    if HAS_MAP:
        try:
            if mt=='Google Map':
                mm=folium.Map(location=[45.8205,8.8250],zoom_start=12,tiles='https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',attr='Google')
            elif mt=='Satellite':
                mm=folium.Map(location=[45.8205,8.8250],zoom_start=12,tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',attr='Google Sat')
            elif mt=='Terreno':
                mm=folium.Map(location=[45.8205,8.8250],zoom_start=12,tiles='Stamen Terrain',attr='Stamen')
            elif mt=='Waze Chiaro':
                mm=folium.Map(location=[45.8205,8.8250],zoom_start=12,tiles='CartoDB positron',attr='CartoDB')
            elif mt=='Waze Scuro':
                mm=folium.Map(location=[45.8205,8.8250],zoom_start=12,tiles='CartoDB dark_matter',attr='CartoDB')
            else:
                mm=folium.Map(location=[45.8205,8.8250],zoom_start=12,tiles='OpenStreetMap')
            Fullscreen(position='topleft',title='Tutto',title_cancel='Ritorna',force_separate_button=True).add_to(mm)
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
                    icon=folium.CustomIcon(icon_file,icon_size=(40,40))
                    folium.Marker([float(lat),float(lon)],popup=nome,icon=icon).add_to(mm)
                else:
                    folium.Marker([float(lat),float(lon)],popup=nome).add_to(mm)
            sla=st.session_state.sel_lat
            slo=st.session_state.sel_lon
            if sla!='45.8205' or slo!='8.8250':
                icon_file=""
                for ic in st.session_state.icone:
                    if ic.get('Nome','')==st.session_state.sel_icon:
                        icon_file=ic.get('File','')
                if icon_file and os.path.exists(icon_file):
                    icon=folium.CustomIcon(icon_file,icon_size=(40,40))
                    folium.Marker([float(sla),float(slo)],popup="Nuova",icon=icon).add_to(mm)
                else:
                    folium.Marker([float(sla),float(slo)],popup="Nuova",icon=folium.Icon(color='orange')).add_to(mm)
            mp=st_folium(mm,width=1200,height=550)
            if mp and mp.get('last_clicked'):
                lat_c=str(mp['last_clicked']['lat'])
                lon_c=str(mp['last_clicked']['lng'])
                st.session_state.sel_lat=lat_c
                st.session_state.sel_lon=lon_c
                st.session_state.sel_comune="Varese"
                st.session_state.sel_via="Via "+lat_c[:6]
                msg="Cliccata: "+st.session_state.sel_comune+" "+st.session_state.sel_via
                st.success(msg)
        except:
            st.error("Err mappa")
    st.divider()
    st.markdown("<div class='ana-box'><h3>Maschera sotto</h3></div>", unsafe_allow_html=True)
    if st.session_state.edit_map >=0:
        p=st.session_state.post[st.session_state.edit_map]
        st.success(f"Modifica: {p.get('Nome','')}")
        e_nome=st.text_input("Nome",value=p.get('Nome',''),key="e_nome")
        e_com=st.text_input("Comune",value=p.get('Comune',''),key="e_com")
        e_via=st.text_input("Via",value=p.get('Via',''),key="e_via")
        e_lat=st.text_input("Lat",value=p.get('Lat','45.8205'),key="e_lat")
        e_lon=st.text_input("Lon",value=p.get('Lon','8.8250'),key="e_lon")
        e_tipo=st.text_input("Tipo",value=p.get('Tipo',''),key="e_tipo")
        lst=['Default']
        for ic in st.session_state.icone:
            lst.append(ic.get('Nome','Default'))
        e_icon=st.selectbox("Icona",lst,key="e_icon")
        e_r1=st.text_input("Rif1",value=p.get('Rif1',''),key="e_r1")
        e_r2=st.text_input("Rif2",value=p.get('Rif2',''),key="e_r2")
        e_note=st.text_area("Note",value=p.get('Note',''),key="e_note")
        b1,b2=st.columns(2)
        with b1:
            if st.button("SALVA MODIFICA",key="bs_mod"):
                p['Nome']=e_nome
                p['Comune']=e_com
                p['Via']=e_via
                p['Lat']=e_lat
                p['Lon']=e_lon
                p['Tipo']=e_tipo
                p['Icona']=e_icon
                p['Rif1']=e_r1
                p['Rif2']=e_r2
                p['Note']=e_note
                st.session_state.post[st.session_state.edit_map]=p
                save_json(FP,st.session_state.post)
                st.session_state.edit_map=-1
                st.rerun()
        with b2:
            if st.button("ELIMINA",key="bd_mod"):
                st.session_state.post.pop(st.session_state.edit_map)
                save_json(FP,st.session_state.post)
                st.session_state.edit_map=-1
                st.rerun()
        if st.button("ANNULLA",key="an_mod"):
            st.session_state.edit_map=-1
            st.rerun()
    else:
        mn=st.text_input("Nome *",key="mn")
        sc_com=st.session_state.sel_comune
        sc_via=st.session_state.sel_via
        sc_lat=st.session_state.sel_lat
        sc_lon=st.session_state.sel_lon
        mc=st.text_input("Comune",value=sc_com,key="mc")
        mv=st.text_input("Via",value=sc_via,key="mv")
        mlat=st.text_input("Lat",value=sc_lat,key="mlat")
        mlon=st.text_input("Lon",value=sc_lon,key="mlon")
        mtp=st.text_input("Tipo",key="mtp")
        lst=['Default']
        for ic in st.session_state.icone:
            lst.append(ic.get('Nome','Default'))
        mi=st.selectbox("Icona",lst,key="mi")
        mr1=st.text_input("Rif1",key="mr1")
        mr2=st.text_input("Rif2",key="mr2")
        mnt=st.text_area("Note",key="mnt")
        if st.button("SALVA TUTTE LE POSIZIONI",key="bm"):
            if mn and mc:
                nuovo={'Nome':mn,'Comune':mc,'Via':mv,'Lat':mlat,'Lon':mlon,'Tipo':mtp,'Icona':mi,'Rif1':mr1,'Rif2':mr2,'Note':mnt}
                st.session_state.post.append(nuovo)
                save_json(FP,st.session_state.post)
                st.success("OK "+mn)
                st.balloons()
                st.rerun()
    st.divider()
    st.markdown("<div class='ana-box'><h3>Mappa sotto + lista con cancella</h3></div>", unsafe_allow_html=True)
    if st.session_state.post:
        st.write(f"Totale: {len(st.session_state.post)}")
        df=pd.DataFrame(st.session_state.post)
        st.dataframe(df)
        try:
            mm2=folium.Map(location=[45.8205,8.8250],zoom_start=11,tiles='OpenStreetMap')
            Fullscreen().add_to(mm2)
            for p in st.session_state.post:
                lat=p.get('Lat','45.8205')
                lon=p.get('Lon','8.8250')
                folium.Marker([float(lat),float(lon)],popup=p.get('Nome','')).add_to(mm2)
            st_folium(mm2,width=1200,height=400,key='map2')
        except:
            st.write("Mini mappa")
        for i,p in enumerate(st.session_state.post):
            c1,c2,c3,c4,c5=st.columns([2,1,1,1,1])
            with c1:
                st.write(f"{i+1}. {p.get('Nome','')}")
            with c2:
                st.write(f"Lat {p.get('Lat','')[:6]}")
            with c3:
                st.write(f"Lon {p.get('Lon','')[:6]}")
            with c4:
                if st.button(f"Mod {i}",key=f"mod_{i}"):
                    st.session_state.edit_map=i
                    st.rerun()
            with c5:
                if st.button(f"Canc {i}",key=f"del_{i}"):
                    st.session_state.post.pop(i)
                    save_json(FP,st.session_state.post)
                    st.success("Cancellata")
                    st.rerun()
        if st.button("CANCELLA TUTTE"):
            st.session_state.post=[]
            save_json(FP,[])
            st.success("Tutte cancellate")
            st.rerun()
    else:
        st.info("Nessuna postazione")

elif sc=='Libreria Icone':
    to_dash()
    st.markdown("<div class='ana-head'><b>LIBRERIA ICONE</b></div>", unsafe_allow_html=True)
    st.markdown("<div class='ana-box'>MASCHERA ICONE - SENZA FORM</div>", unsafe_allow_html=True)
    i_nome=st.text_input("Nome icona *",key="icone_nome_fix")
    i_cat=st.text_input("Categoria",key="icone_cat_fix")
    i_desc=st.text_area("Descrizione",key="icone_desc_fix")
    i_file=st.file_uploader("File icona",type=['png','jpg','jpeg','svg'],key="icone_file_fix")
    if st.button("SALVA ICONA",key="icone_salva_fix"):
        if i_nome:
            fp=""
            if i_file:
                os.makedirs('icone',exist_ok=True)
                fp="icone/"+i_nome+"_"+i_file.name
                fout=open(fp,'wb')
                fout.write(i_file.getbuffer())
                fout.close()
            nuovo={'Nome':i_nome,'Categoria':i_cat,'File':fp,'Descrizione':i_desc}
            st.session_state.icone.append(nuovo)
            save_json(FI,st.session_state.icone)
            st.success("OK icona salvata")
            st.balloons()
            st.rerun()
    if st.session_state.icone:
        df=pd.DataFrame(st.session_state.icone)
        st.dataframe(df)
        for ic in st.session_state.icone[-8:]:
            fp=ic.get('File','')
            if fp and os.path.exists(fp):
                st.image(fp,width=60,caption=ic.get('Nome',''))
    else:
        st.info("Nessuna icona")

elif sc=='Interventi Emergenza':
    to_dash()
    st.markdown("<div class='ana-head'><b>INTERVENTI</b></div>", unsafe_allow_html=True)
    st.markdown("<div class='ana-box'>MASCHERA INTERVENTI</div>", unsafe_allow_html=True)
    d_int=st.date_input("Data",key="d_int")
    o_int=st.time_input("Ora",key="o_int")
    com_int=st.text_input("Comune *",key="com_int")
    via_int=st.text_input("Via *",key="via_int")
    civ_int=st.text_input("Civico",key="civ_int")
    odv_int=st.text_input("ODV",key="odv_int")
    az_int=st.text_area("Azione *",height=80,key="az_int")
    if st.button("SALVA INTERVENTO",key="sv_int"):
        if com_int and via_int and az_int:
            nuovo={"Data":str(d_int),"Ora":str(o_int),"Comune":com_int,"Via":via_int,"Civico":civ_int,"ODV":odv_int,"Azione":az_int}
            st.session_state.interv.append(nuovo)
            save_json(FE,st.session_state.interv)
            st.success("OK")
            st.rerun()
    if st.session_state.interv:
        st.dataframe(pd.DataFrame(st.session_state.interv))

elif sc=='Eventi':
    to_dash()
    st.markdown("<div class='ana-head'><b>EVENTI</b></div>", unsafe_allow_html=True)
    st.markdown("<div class='ana-box'>MASCHERA EVENTI</div>", unsafe_allow_html=True)
    ev_nome=st.text_input("Nome *",key="ev_nome")
    ev_data=st.date_input("Data",key="ev_data")
    ev_com=st.text_input("Comune",key="ev_com")
    ev_luogo=st.text_input("Luogo",key="ev_luogo")
    ev_tipo=st.text_input("Tipo",key="ev_tipo")
    ev_resp=st.text_input("Resp",key="ev_resp")
    ev_desc=st.text_area("Desc",key="ev_desc")
    if st.button("SALVA EVENTO",key="ev_be"):
        if ev_nome:
            nuovo={'Nome':ev_nome,'Data':str(ev_data),'Comune':ev_com,'Luogo':ev_luogo,'Tipo':ev_tipo,'Responsabile':ev_resp,'Descrizione':ev_desc}
            st.session_state.eventi.append(nuovo)
            save_json(FEV,st.session_state.eventi)
            st.success("OK")
            st.rerun()
    if st.session_state.eventi:
        st.dataframe(pd.DataFrame(st.session_state.eventi))

elif sc=='Check In':
    to_dash()
    st.markdown("<div class='ana-head'><b>CHECK IN</b></div>", unsafe_allow_html=True)
    st.markdown("<div class='ana-box'>MASCHERA CHECK IN</div>", unsafe_allow_html=True)
    vlist=[]
    for d in st.session_state.dati:
        vlist.append(d.get('Nome',''))
    if vlist:
        sel=st.selectbox("Vol",vlist,key="check_vol")
        d_check=st.date_input("Data",key="d_check")
        o_check=st.time_input("Ora",key="o_check")
        luogo=st.text_input("Luogo",key="luogo_check")
        if st.button("SALVA CHECK IN",key="bc_check"):
            nuovo={'Volontario':sel,'Data':str(d_check),'Ora':str(o_check),'Luogo':luogo}
            st.session_state.check.append(nuovo)
            save_json(FC,st.session_state.check)
            st.success("OK")
            st.rerun()
    else:
        st.warning("Nessun volontario")
    if st.session_state.check:
        st.dataframe(pd.DataFrame(st.session_state.check))

elif sc=='DB Radio':
    to_dash()
    st.markdown("<div class='ana-head'><b>DB RADIO - CON COMBO TIPO RADIO</b></div>", unsafe_allow_html=True)
    st.markdown("<div class='ana-box'>MASCHERA RADIO - CON COMBO DMR/PMR446/TETRA/RADIOAMATORIALE</div>", unsafe_allow_html=True)
    r_mod=st.text_input("Modello *",key="r_mod")
    r_mat=st.text_input("Matricola *",key="r_mat")
    r_tipo=st.selectbox("Tipo Radio *",["DMR","PMR446","TETRA","Radioamatoriale","Analogica","Digitale","CB","Altro"],key="r_tipo_combo")
    r_freq=st.text_input("Frequenza",key="r_freq")
    r_stato=st.selectbox("Stato",["Disponibile","In uso","Guasta","In riparazione","Ritirata"],key="r_stato")
    r_note=st.text_area("Note",key="r_note")
    if st.button("SALVA RADIO CON TIPO",key="br_radio_tipo"):
        if r_mod and r_mat:
            nuovo={'Modello':r_mod,'Matricola':r_mat,'Tipo':r_tipo,'Frequenza':r_freq,'Stato':r_stato,'Note':r_note}
            st.session_state.radio.append(nuovo)
            save_json(FR,st.session_state.radio)
            st.success(f"OK Radio {r_mod} Tipo {r_tipo} salvata")
            st.balloons()
            st.rerun()
    if st.session_state.radio:
        df=pd.DataFrame(st.session_state.radio)
        st.dataframe(df)
        st.write(f"Totale radio: {len(st.session_state.radio)}")
        # filtro per tipo
        tipi=[]
        for r in st.session_state.radio:
            t=r.get('Tipo','')
            if t not in tipi:
                tipi.append(t)
        if tipi:
            sel_tipo=st.selectbox("Filtra per Tipo",['Tutti']+tipi,key="filtra_tipo")
            if sel_tipo!='Tutti':
                df_f=df[df['Tipo']==sel_tipo]
                st.dataframe(df_f)
    else:
        st.info("Nessuna radio - Inserisci con maschera sopra - Combo Tipo già dentro")

elif sc=='Consegna Radio':
    to_dash()
    st.markdown("<div class='ana-head'><b>CONSEGNA RADIO</b></div>", unsafe_allow_html=True)
    st.markdown("<div class='ana-box'>MASCHERA CONSEGNA</div>", unsafe_allow_html=True)
    vlist=[]
    for d in st.session_state.dati:
        vlist.append(d.get('Nome',''))
    rlist=[]
    for r in st.session_state.radio:
        rlist.append(r.get('Matricola','')+" - "+r.get('Tipo','')+" - "+r.get('Modello',''))
    if vlist and rlist:
        s_vol=st.selectbox("Volontario",vlist,key="s_vol")
        s_rad=st.selectbox("Radio",rlist,key="s_rad")
        d_cons=st.date_input("Data",key="d_cons")
        if st.button("SALVA CONSEGNA",key="b_cons"):
            nuovo={'Volontario':s_vol,'Radio':s_rad,'Data':str(d_cons)}
            st.session_state.cons.append(nuovo)
            save_json(FR2,st.session_state.cons)
            st.success("OK")
            st.rerun()
    else:
        st.warning("Servono volontari e radio")
    if st.session_state.cons:
        st.dataframe(pd.DataFrame(st.session_state.cons))

elif sc=='Chat Volontari':
    to_dash()
    st.markdown("<div class='ana-head'><b>CHAT VOLONTARI</b></div>", unsafe_allow_html=True)
    st.markdown("<div class='ana-box'>CHAT - VERDE ANA</div>", unsafe_allow_html=True)
    c1,c2=st.columns([3,1])
    with c1:
        st.write(f"Utente: {st.session_state.chat_user}")
    with c2:
        if st.button("AGGIORNA"):
            st.session_state.chat=load_json(FCHAT,[])
            st.rerun()
    if st.session_state.chat:
        for msg in st.session_state.chat[-20:]:
            user=msg.get('User','')
            text=msg.get('Text','')
            tm=msg.get('Time','')
            st.write(f"{user} {tm}: {text}")
    else:
        st.info("Nessun msg")
    chat_text=st.text_input("Scrivi messaggio",key="chat_text")
    if st.button("INVIA",key="chat_send"):
        if chat_text:
            nuovo={'User':st.session_state.chat_user,'Text':chat_text,'Time':datetime.now().strftime("%d/%m %H:%M"),'Data':str(datetime.now().date())}
            st.session_state.chat.append(nuovo)
            save_json(FCHAT,st.session_state.chat)
            st.success("Inviato")
            st.rerun()

elif sc=='Backup':
    to_dash()
    st.markdown("<div class='ana-head'><b>BACKUP - IMPORT EXPORT</b></div>", unsafe_allow_html=True)
    st.markdown("<div class='ana-box'>EXPORT</div>", unsafe_allow_html=True)
    if st.button('CREA BACKUP COMPLETO'):
        out=BytesIO()
        has=False
        with pd.ExcelWriter(out,engine='openpyxl') as w:
            if st.session_state.dati:
                pd.DataFrame(st.session_state.dati).to_excel(w,sheet_name='Volontari',index=False)
                has=True
            if st.session_state.post:
                pd.DataFrame(st.session_state.post).to_excel(w,sheet_name='Mappa',index=False)
                has=True
            if st.session_state.icone:
                pd.DataFrame(st.session_state.icone).to_excel(w,sheet_name='Icone',index=False)
                has=True
            if st.session_state.interv:
                d=st.session_state.dati
                pd.DataFrame(d).to_excel(w,sheet_name='Volontari',index=False)
                ic=st.session_state.icone
                pd.DataFrame(ic).to_excel(w,sheet_name='Icone',index=False)
                it=st.session_state.interv
                pd.DataFrame(it).to_excel(w,sheet_name='Interventi',index=False)
