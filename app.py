import streamlit as st
import pandas as pd
from io import BytesIO
import os, json, hashlib, requests
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

st.set_page_config(page_title="ANA Varese",layout="wide")

st.markdown("""
<style>
.block-container{padding-top:10px!important}
.stForm{background:#e8f5e9!important;border:2px solid #0e7a3d!important}
.stButton>button{background:#0e7a3d!important;color:white!important;font-weight:bold!important}
</style>
""",unsafe_allow_html=True)

def load(f,d):
    try:
        if os.path.exists(f):
            return json.load(open(f,'r',encoding='utf-8'))
    except:
        pass
    return d

def save(f,d):
    try:
        json.dump(d,open(f,'w',encoding='utf-8'),indent=2)
    except:
        pass

def hp(p):
    return hashlib.sha256(p.encode()).hexdigest()

def gaddr(lat,lon):
    try:
        u=f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=jsonv2&accept-language=it"
        r=requests.get(u,headers={'User-Agent':'ana-varese'},timeout=8)
        if r.status_code==200:
            a=r.json().get('address',{})
            com=a.get('city') or a.get('town') or a.get('village') or ''
            via=a.get('road') or ''
            num=a.get('house_number') or ''
            return com,f"{via} {num}".strip()
    except:
        pass
    return '',''

def fmt_date(d):
    if isinstance(d,date):
        return d.strftime("%d/%m/%Y")
    return str(d)

def export_excel(df):
    out=BytesIO()
    with pd.ExcelWriter(out,engine='openpyxl') as w:
        df.to_excel(w,index=False)
    return out.getvalue()

def crea_barcode(cf):
    try:
        import barcode
        from barcode.writer import ImageWriter
        if not cf:
            cf="0000000000000000"
        code=barcode.get('code128',cf[:16].upper(),writer=ImageWriter())
        buf=BytesIO()
        code.write(buf)
        buf.seek(0)
        return buf.getvalue()
    except:
        try:
            W,H=300,80
            img=Image.new('RGB',(W,H),'white')
            d=ImageDraw.Draw(img)
            x=5
            for c in (cf or "0"*16)[:16]:
                w=ord(c)%5+1
                w*=2
                if x+w<W-5:
                    d.rectangle([x,5,x+w,H-20],fill='black')
                x+=w+2
            buf=BytesIO()
            img.save(buf,format='PNG')
            buf.seek(0)
            return buf.getvalue()
        except:
            return None

def crea_tesserino(vol,foto_path,template_path):
    try:
        if not HAS_PIL:
            return None
        if template_path and os.path.exists(template_path):
            base=Image.open(template_path).convert("RGB")
            tess=base.copy()
            draw=ImageDraw.Draw(tess)
        else:
            tess=Image.new('RGB',(860,540),'white')
            draw=ImageDraw.Draw(tess)
            draw.rectangle([0,0,859,539],outline='black',width=2)
        try:
            fn=ImageFont.truetype("arialbd.ttf",20)
            fo=ImageFont.truetype("arial.ttf",14)
        except:
            fn=ImageFont.load_default()
            fo=ImageFont.load_default()
        W,H=tess.size
        fx,fy,fw,fh=int(W*0.015),int(H*0.22),int(W*0.27),int(H*0.58)
        if foto_path and os.path.exists(foto_path):
            try:
                foto=Image.open(foto_path).convert("RGB").resize((fw,fh))
                tess.paste(foto,(fx,fy))
                draw.rectangle([fx,fy,fx+fw,fy+fh],outline='black',width=2)
            except:
                pass
        nx,ny=int(W*0.38),int(H*0.36)
        draw.rectangle([nx,ny-5,nx+int(W*0.55),ny+int(H*0.15)],fill='white')
        draw.text((nx,ny),vol.get('Nome','').upper(),fill='black',font=fn)
        odv=vol.get('ODV','A.N.A. Sezione di Varese')
        oy=ny+int(H*0.12)
        draw.rectangle([nx,oy-2,nx+int(W*0.5),oy+int(H*0.08)],fill='white')
        draw.text((nx,oy),odv,fill='black',font=fo)
        bx,by,bw,bh=int(W*0.62),int(H*0.73),int(W*0.35),int(H*0.15)
        draw.rectangle([bx,by,bx+bw,by+bh],fill='white',outline='white')
        cf=vol.get('CF','') or vol.get('Nome','').replace(' ','').upper()[:16]
        bc=crea_barcode(cf)
        if bc:
            try:
                bi=Image.open(BytesIO(bc)).convert("RGB").resize((bw,bh))
                tess.paste(bi,(bx,by))
            except:
                pass
        buf=BytesIO()
        tess.save(buf,format='PNG')
        buf.seek(0)
        return buf.getvalue()
    except Exception as e:
        st.error(f"Errore tesserino: {e}")
        return None

FD='dati.json'
FU='utenti.json'
FP='post.json'
FI='icone.json'
FT='tip.json'
FO='odv.json'
FE='emerg.json'
FC='check.json'
FR='radio.json'
FR2='cons.json'
FPOP='popup.json'

for k,v in [
    ('dati',[]),('post',[]),('icone',[]),('tip',[]),('odv',[]),('emerg',[]),('check',[]),('radio',[]),('cons',[]),
    ('menu','Dashboard'),('auth',False),('lat',45.8205),('lon',8.8250),('com',''),('via',''),('sel',-1),('zoom',16),
    ('clat',None),('clon',None),('exp1',False),('popup_shown',False),
    ('popup_cfg',{'titolo':'ANA VARESE - VOLONTARIATO','sottotitolo':'Ciao Ragazzi, Buon Lavoro!','mostra':True})
]:
    if k not in st.session_state:
        st.session_state[k]=v

st.session_state.dati=load(FD,[])
st.session_state.post=load(FP,[])
st.session_state.icone=load(FI,[])
st.session_state.tip=load(FT,[])
st.session_state.odv=load(FO,[])
st.session_state.emerg=load(FE,[])
st.session_state.check=load(FC,[])
st.session_state.radio=load(FR,[])
st.session_state.cons=load(FR2,[])
st.session_state.popup_cfg=load(FPOP,{'titolo':'ANA VARESE - VOLONTARIATO','sottotitolo':'Ciao Ragazzi, Buon Lavoro!','mostra':True})
uts=load(FU,[])

if not uts:
    uts=[{'username':'admin','password':hp('ana2024')}]
    save(FU,uts)
if not st.session_state.tip:
    st.session_state.tip=['Presidio','Blocco stradale','Punto ritrovo','Parcheggio','Sanitario','Logistica','Altro']
    save(FT,st.session_state.tip)
if not st.session_state.odv:
    st.session_state.odv=['ANA Varese','Protezione Civile Varese','Croce Rossa','Alpini','AIB','Altro']
    save(FO,st.session_state.odv)
if not st.session_state.icone:
    st.session_state.icone=[{'nome':'Presidio','col':'blue','file':''}]
    save(FI,st.session_state.icone)

def header():
    c1,c2=st.columns([1,5])
    with c1:
        try:
            st.image("logo.png",width=130)
        except:
            st.write("ANA")
    with c2:
        st.markdown("<div style='background:#a5d6a7;padding:15px;border-radius:8px;border:2px solid #0e7a3d;text-align:center;'><b style='color:#000;font-size:26px;'>VOLONTARIATO<br>Sezione di Varese</b></div>",unsafe_allow_html=True)

def torna():
    if st.button('TORNA ALLA DASHBOARD'):
        st.session_state.menu='Dashboard'
        st.rerun()

# SCHERMO INTERO MAPPA
if st.session_state.exp1:
    if st.button('TORNA AL FORM',use_container_width=True,type='primary'):
        st.session_state.exp1=False
        st.rerun()
    st.markdown('## MAPPA SCHERMO INTERO - CLICCA PER VIA COMUNE LAT LON')
    if HAS:
        m=folium.Map(location=[st.session_state.lat,st.session_state.lon],zoom_start=st.session_state.zoom,tiles='OpenStreetMap')
        for p in st.session_state.post:
            try:
                la=float(p.get('Lat','0'))
                lo=float(p.get('Lon','0'))
                folium.Marker([la,lo],popup=p.get('Postazione','')).add_to(m)
            except:
                pass
        if st.session_state.clat is not None:
            folium.Marker([st.session_state.clat,st.session_state.clon],icon=folium.Icon(color='green')).add_to(m)
        out=st_folium(m,height=800,width=1400,key='full')
        if out and out.get('last_clicked'):
            st.session_state.lat=out['last_clicked']['lat']
            st.session_state.lon=out['last_clicked']['lng']
            st.session_state.clat=out['last_clicked']['lat']
            st.session_state.clon=out['last_clicked']['lng']
            com,via=gaddr(st.session_state.lat,st.session_state.lon)
            st.session_state.com=com
            st.session_state.via=via
            st.rerun()
    st.stop()

# POPUP INIZIALE - SOLO TUA IMMAGINE FUMETTO - NO LOGO PC
if st.session_state.popup_cfg.get('mostra',True) and not st.session_state.popup_shown:
    st.markdown(f"<h1 style='text-align:center;color:#0e7a3d;'>{st.session_state.popup_cfg.get('titolo','ANA VARESE - VOLONTARIATO')}</h1>",unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align:center;color:#0e7a3d;'>{st.session_state.popup_cfg.get('sottotitolo','Ciao Ragazzi, Buon Lavoro!')}</h3>",unsafe_allow_html=True)
    st.divider()
    c1,c2,c3=st.columns([1,2,1])
    with c2:
        # SOLO TUA IMMAGINE FUMETTO - MAI LOGO PC
        img_found=False
        for img_name in ['copertina.jpg','copertina_fumetto.jpg','mia_immagine_fumetto.jpg']:
            if os.path.exists(img_name):
                try:
                    st.image(img_name,use_container_width=True)
                    st.success(f"TUA IMMAGINE CON FUMETTO: {img_name} - PRIMA PAGINA OK - NO LOGO PC")
                    img_found=True
                    break
                except:
                    pass
        if not img_found:
            st.error("MANCA LA TUA IMMAGINE CON FUMETTO!")
            st.warning("Carica copertina.jpg con la TUA immagine con fumetto 'ciao ragazzi, buon lavoro'")
            st.info("NON deve essere logo PC - deve essere la TUA immagine con fumetto!")
            st.markdown("<div style='background:#e8f5e9;padding:20px;border-radius:10px;text-align:center;border:2px dashed #0e7a3d;'><h3>QUI VA LA TUA IMMAGINE CON FUMETTO</h3><p>Ciao Ragazzi, Buon Lavoro!</p><p>Carica copertina.jpg</p></div>",unsafe_allow_html=True)
        st.divider()
        st.markdown(f"<div style='background:#e8f5e9;padding:15px;border-radius:10px;border:2px solid #0e7a3d;text-align:center;'><b>ANA Varese - Protezione Civile</b><br><b style='color:#0e7a3d;'>Ciao Ragazzi, Buon Lavoro!</b><br><br>Volontari: {len(st.session_state.dati)} Postazioni: {len(st.session_state.post)}<br>{datetime.now().strftime('%d/%m/%Y %H:%M')}</div>",unsafe_allow_html=True)
        st.divider()
        if st.button("ENTRA NEL SISTEMA",type="primary",use_container_width=True):
            st.session_state.popup_shown=True
            st.rerun()
    st.stop()

if not st.session_state.auth:
    header()
    c1,c2,c3=st.columns([1,2,1])
    with c2:
        # Login con TUA immagine fumetto se presente
        for img_name in ['copertina.jpg','copertina_fumetto.jpg']:
            if os.path.exists(img_name):
                try:
                    st.image(img_name,width=250)
                    break
                except:
                    pass
        with st.form('login'):
            u=st.text_input('Username',value='admin')
            p=st.text_input('Password',type='password',value='ana2024')
            ok=st.form_submit_button('ACCEDI')
            if ok:
                ph=hp(p)
                for ut in uts:
                    if ut['username']==u and ut['password']==ph:
                        st.session_state.auth=True
                        st.rerun()
                st.error('Errati')
        if st.button('TORNA ALLA PAGINA INIZIALE POPUP'):
            st.session_state.popup_shown=False
            st.rerun()
    st.stop()

header()
with st.sidebar:
    opts=['Dashboard','Volontari','Mappa','Libreria Icone','Emergenza','Check In','DB Radio','Consegna Radio','Tesserino Regionale','Backup','Impostazioni Popup']
    sel=st.radio('MENU',opts,index=0)
    if sel!=st.session_state.menu:
        st.session_state.menu=sel
        st.rerun()
    if st.button('MOSTRA POPUP INIZIALE',use_container_width=True):
        st.session_state.popup_shown=False
        st.rerun()
    if st.button('LOGOUT',use_container_width=True):
        st.session_state.auth=False
        st.session_state.popup_shown=False
        st.rerun()

scelta=st.session_state.menu

if scelta=='Dashboard':
    st.markdown('### DASHBOARD')
    c1,c2,c3=st.columns(3)
    with c1:
        if st.button('VOLONTARI',use_container_width=True,key='d1'):
            st.session_state.menu='Volontari'
            st.rerun()
        if st.button('MAPPA',use_container_width=True,key='d2'):
            st.session_state.menu='Mappa'
            st.rerun()
        if st.button('TESSERINO REGIONALE',use_container_width=True,key='d3',type="primary"):
            st.session_state.menu='Tesserino Regionale'
            st.rerun()
        if st.button('LIBRERIA ICONE',use_container_width=True,key='d4'):
            st.session_state.menu='Libreria Icone'
            st.rerun()
    with c2:
        if st.button('EMERGENZA',use_container_width=True,key='d5'):
            st.session_state.menu='Emergenza'
            st.rerun()
        if st.button('CHECK IN',use_container_width=True,key='d6'):
            st.session_state.menu='Check In'
            st.rerun()
        if st.button('DB RADIO',use_container_width=True,key='d7'):
            st.session_state.menu='DB Radio'
            st.rerun()
        if st.button('CONSEGNA RADIO',use_container_width=True,key='d8'):
            st.session_state.menu='Consegna Radio'
            st.rerun()
    with c3:
        if st.button('BACKUP IMPORT EXPORT TUTTI I FORM',use_container_width=True,key='d9',type="primary"):
            st.session_state.menu='Backup'
            st.rerun()
        if st.button('IMPOSTAZIONI POPUP - TUA IMMAGINE FUMETTO',use_container_width=True,key='d10'):
            st.session_state.menu='Impostazioni Popup'
            st.rerun()
        st.metric('Volontari',len(st.session_state.dati))
        st.metric('Postazioni',len(st.session_state.post))
    st.divider()
    st.markdown("**PRIMA PAGINA - TUA IMMAGINE CON FUMETTO (NO LOGO PC):**")
    for img_name in ['copertina.jpg','copertina_fumetto.jpg']:
        if os.path.exists(img_name):
            st.image(img_name,width=350,caption=f"{img_name} - TUA IMMAGINE FUMETTO PER PRIMA PAGINA - OK")
            st.success("PRIMA PAGINA OK - TUA IMMAGINE CON FUMETTO - NO LOGO PC")
            break
    else:
        st.error("MANCA copertina.jpg - Carica la TUA immagine con fumetto!")
        st.warning("Prima pagina deve avere TUA immagine fumetto, NON logo PC!")

elif scelta=='Volontari':
    torna()
    st.markdown('### VOLONTARI CON FOTO E CF')
    t1,t2,t3=st.tabs(['Anagrafica Foto CF ODV','Elenco','Tesserino'])
    with t1:
        with st.form('vol1'):
            c1,c2=st.columns(2)
            with c1:
                a1=st.text_input('Nome *')
                a2=st.text_input('Cognome *')
                a_cf=st.text_input('CF * per barcode')
                a_foto=st.file_uploader('Foto JPG PNG',type=['jpg','png','jpeg'],key='f1')
            with c2:
                a_odv=st.selectbox('ODV',['A.N.A. Sezione di Varese','Protezione Civile Varese','ANA Varese','Croce Rossa','Alpini','Altro'])
                a_tess=st.text_input('Tessera')
                if a_foto:
                    st.image(a_foto,width=120)
            if st.form_submit_button('SALVA VOLONTARIO CON FOTO E CF'):
                if a1 and a2:
                    nc=f"{a1} {a2}"
                    fp=''
                    if a_foto:
                        os.makedirs('foto_volontari',exist_ok=True)
                        fp=f"foto_volontari/{nc.replace(' ','_')}_{a_foto.name}"
                        open(fp,'wb').write(a_foto.getbuffer())
                    nuovo={'Nome':nc,'CF':a_cf,'ODV':a_odv,'Tessera':a_tess,'FotoFile':fp}
                    found=False
                    for i,d in enumerate(st.session_state.dati):
                        if d.get('Nome','')==nc:
                            if not fp:
                                nuovo['FotoFile']=d.get('FotoFile','')
                            st.session_state.dati[i].update(nuovo)
                            found=True
                    if not found:
                        st.session_state.dati.append(nuovo)
                    save(FD,st.session_state.dati)
                    st.success(f"Salvato {nc}")
                    st.rerun()
    with t2:
        if st.session_state.dati:
            df=pd.DataFrame(st.session_state.dati)
            st.dataframe(df,use_container_width=True)
    with t3:
        vol_list=[d.get('Nome','') for d in st.session_state.dati]
        if vol_list:
            sel=st.selectbox('Seleziona Volontario',vol_list,key='tess1')
            vol_data={}
            for d in st.session_state.dati:
                if d.get('Nome','')==sel:
                    vol_data=d
                    break
            tess=crea_tesserino(vol_data,vol_data.get('FotoFile',''),"Tesserino-Ezio.JPG" if os.path.exists("Tesserino-Ezio.JPG") else None)
            if tess:
                st.image(tess,use_container_width=True)
                st.download_button('SCARICA TESSERINO PNG',tess,file_name=f"Tesserino_{sel.replace(' ','_')}.png",mime='image/png',type='primary')

elif scelta=='Mappa':
    torna()
    st.markdown('### MAPPA - VIA COMUNE LAT LON + ESPANDI + GOOGLE MAPS WAZE')
    icon_names=[it.get('nome','') for it in st.session_state.icone]
    sel_idx=0
    if icon_names:
        sel_str=st.selectbox('Icona PNG libreria',icon_names,index=0)
        sel_idx=icon_names.index(sel_str)
    c1,c2=st.columns([3,1])
    with c1:
        st.info("Clicca sulla mappa per via comune lat lon automatici")
    with c2:
        if st.button('ESPANDI SCHERMO INTERO',use_container_width=True):
            st.session_state.exp1=True
            st.rerun()
    if HAS:
        m=folium.Map(location=[st.session_state.lat,st.session_state.lon],zoom_start=st.session_state.zoom,tiles='OpenStreetMap')
        for p in st.session_state.post:
            try:
                la=float(p.get('Lat','0'))
                lo=float(p.get('Lon','0'))
                folium.Marker([la,lo],popup=p.get('Postazione','')).add_to(m)
            except:
                pass
        if st.session_state.clat is not None:
            folium.Marker([st.session_state.clat,st.session_state.clon],icon=folium.Icon(color='green')).add_to(m)
        out=st_folium(m,height=400,width=800,key='m1')
        if out and out.get('last_clicked'):
            st.session_state.lat=out['last_clicked']['lat']
            st.session_state.lon=out['last_clicked']['lng']
            st.session_state.clat=out['last_clicked']['lat']
            st.session_state.clon=out['last_clicked']['lng']
            com,via=gaddr(st.session_state.lat,st.session_state.lon)
            st.session_state.com=com
            st.session_state.via=via
            st.rerun()
    c1,c2,c3,c4=st.columns(4)
    with c1:
        st.success(f"Comune: {st.session_state.com}")
    with c2:
        st.success(f"Via: {st.session_state.via}")
    with c3:
        st.info(f"Lat: {st.session_state.lat}")
    with c4:
        st.info(f"Lon: {st.session_state.lon}")
    vol_nomi=[d.get('Nome','') for d in st.session_state.dati] or ['Nessun volontario']
    with st.form('mappa_form'):
        c1,c2=st.columns(2)
        with c1:
            m1=st.text_input('Nome postazione *')
            m2=st.text_input('Comune *',value=st.session_state.com)
            m3=st.text_input('Via *',value=st.session_state.via)
            m4=st.selectbox('Tipologia',st.session_state.tip)
        with c2:
            m5=st.text_input('Latitudine *',value=str(st.session_state.lat))
            m6=st.text_input('Longitudine *',value=str(st.session_state.lon))
            m8=st.selectbox('Responsabile',vol_nomi)
            m9=st.selectbox('ODV',st.session_state.odv)
        if st.form_submit_button('SALVA POSTAZIONE',type='primary',use_container_width=True):
            if m1:
                ic=st.session_state.icone[sel_idx] if st.session_state.icone else {'col':'blue','file':'','nome':''}
                nuovo={'Postazione':m1,'Comune':m2,'Via':m3,'Lat':m5,'Lon':m6,'Responsabile':m8,'ODV':m9,'Tipo':m4,'IconFile':ic.get('file','')}
                st.session_state.post.append(nuovo)
                save(FP,st.session_state.post)
                st.success(f"Salvata {m1}")
                st.rerun()
    st.divider()
    st.markdown("#### MAPPA SOTTO CON TUTTE LE POSTAZIONI + GOOGLE MAPS + WAZE + TASTI VAI")
    if HAS and st.session_state.post:
        m2=folium.Map(location=[45.8205,8.8250],zoom_start=11,tiles='OpenStreetMap')
        for p in st.session_state.post:
            try:
                la=float(p.get('Lat','0'))
                lo=float(p.get('Lon','0'))
                folium.Marker([la,lo],popup=f"{p.get('Postazione','')}").add_to(m2)
            except:
                pass
        st_folium(m2,height=400,width=800,key='m2')
    if st.session_state.post:
        for idx,p in enumerate(st.session_state.post):
            c1,c2,c3=st.columns([2,2,4])
            with c1:
                st.write(f"**{p.get('Postazione','')}**")
                st.caption(f"{p.get('Comune','')} {p.get('Via','')} - Lat {p.get('Lat','')} Lon {p.get('Lon','')}")
            with c2:
                la=p.get('Lat','')
                lo=p.get('Lon','')
                st.link_button('Google Maps',f"https://www.google.com/maps/search/?api=1&query={la},{lo}",use_container_width=True)
                st.link_button('Waze',f"https://waze.com/ul?ll={la},{lo}&navigate=yes",use_container_width=True)
            with c3:
                col1,col2=st.columns(2)
                with col1:
                    if st.button('VAI MAPPA',key=f'vai{idx}',use_container_width=True):
                        st.session_state.lat=float(p.get('Lat','0'))
                        st.session_state.lon=float(p.get('Lon','0'))
                        st.session_state.clat=float(p.get('Lat','0'))
                        st.session_state.clon=float(p.get('Lon','0'))
                        st.session_state.com=p.get('Comune','')
                        st.session_state.via=p.get('Via','')
                        st.session_state.zoom=18
                        st.rerun()
                with col2:
                    if st.button('Elimina',key=f'del{idx}',use_container_width=True):
                        st.session_state.post.pop(idx)
                        save(FP,st.session_state.post)
                        st.rerun()
            st.divider()
        df=pd.DataFrame(st.session_state.post)
        st.dataframe(df,use_container_width=True)
        st.download_button('EXCEL MAPPA',export_excel(df),file_name='Mappa.xlsx')

elif scelta=='Tesserino Regionale':
    torna()
    st.markdown('### TESSERINO REGIONALE IDENTICO - LOGHI UGUALI')
    vol_list=[d.get('Nome','') for d in st.session_state.dati]
    if vol_list:
        sel=st.selectbox('Volontario',vol_list,key='tess_final')
        vol_data={}
        for d in st.session_state.dati:
            if d.get('Nome','')==sel:
                vol_data=d
                break
        c1,c2=st.columns([1,2])
        with c1:
            fp=vol_data.get('FotoFile','')
            if fp and os.path.exists(fp):
                st.image(fp,width=120)
            st.write(f"Nome: {vol_data.get('Nome','')}")
            st.write(f"CF: {vol_data.get('CF','')}")
            st.write(f"ODV: {vol_data.get('ODV','')}")
            if os.path.exists("Tesserino-Ezio.JPG"):
                st.image("Tesserino-Ezio.JPG",caption="Template UGUALE",use_container_width=True)
        with c2:
            tess=crea_tesserino(vol_data,vol_data.get('FotoFile',''),"Tesserino-Ezio.JPG" if os.path.exists("Tesserino-Ezio.JPG") else None)
            if tess:
                st.image(tess,use_container_width=True)
                st.download_button('SCARICA TESSERINO PNG',tess,file_name=f"Tesserino_{sel.replace(' ','_')}.png",mime='image/png',type='primary',use_container_width=True)

elif scelta=='Backup':
    torna()
    st.markdown('### BACKUP - IMPORT ED EXPORT TUTTI I FORM')
    st.success("EXPORT E IMPORT PER TUTTI I FORM - VOLONTARI, MAPPA, EMERGENZA, CHECK IN, RADIO, CONSEGNA RADIO, ICONE")

    tab1,tab2,tab3=st.tabs(['EXPORT SINGOLI FORM','IMPORT TUTTI I FORM','BACKUP COMPLETO'])

    with tab1:
        st.markdown("#### EXPORT EXCEL SINGOLI FORM")
        c1,c2,c3=st.columns(3)
        with c1:
            st.markdown("**VOLONTARI CON FOTO E CF**")
            if st.session_state.dati:
                df=pd.DataFrame(st.session_state.dati)
                st.write(f"Record: {len(df)}")
                st.download_button('EXPORT VOLONTARI EXCEL',export_excel(df),file_name='Volontari.xlsx',key='exp_vol',use_container_width=True)
            else:
                st.warning("Nessun volontario")

            st.markdown("**LIBRERIA ICONE**")
            if st.session_state.icone:
                df=pd.DataFrame(st.session_state.icone)
                st.download_button('EXPORT ICONE EXCEL',export_excel(df),file_name='Icone.xlsx',key='exp_icone',use_container_width=True)

        with c2:
            st.markdown("**MAPPA POSTAZIONI CON VIA COMUNE LAT LON**")
            if st.session_state.post:
                df=pd.DataFrame(st.session_state.post)
                st.write(f"Record: {len(df)}")
                st.download_button('EXPORT MAPPA EXCEL',export_excel(df),file_name='Mappa_Postazioni.xlsx',key='exp_mappa',use_container_width=True)
            else:
                st.warning("Nessuna postazione")

            st.markdown("**EMERGENZA**")
            if st.session_state.emerg:
                df=pd.DataFrame(st.session_state.emerg)
                st.download_button('EXPORT EMERGENZE EXCEL',export_excel(df),file_name='Emergenze.xlsx',key='exp_emerg',use_container_width=True)
            else:
                st.warning("Nessuna emergenza")

        with c3:
            st.markdown("**CHECK IN**")
            if st.session_state.check:
                df=pd.DataFrame(st.session_state.check)
                st.download_button('EXPORT CHECK IN EXCEL',export_excel(df),file_name='CheckIn.xlsx',key='exp_check',use_container_width=True)
            else:
                st.warning("Nessun check in")

            st.markdown("**DB RADIO**")
            if st.session_state.radio:
                df=pd.DataFrame(st.session_state.radio)
                st.download_button('EXPORT DB RADIO EXCEL',export_excel(df),file_name='DB_Radio.xlsx',key='exp_radio',use_container_width=True)
            else:
                st.warning("Nessuna radio")

            st.markdown("**CONSEGNA RADIO CON CANALE**")
            if st.session_state.cons:
                df=pd.DataFrame(st.session_state.cons)
                st.download_button('EXPORT CONSEGNA RADIO EXCEL',export_excel(df),file_name='ConsegnaRadio.xlsx',key='exp_cons',use_container_width=True)
            else:
                st.warning("Nessuna consegna")

    with tab2:
        st.markdown("#### IMPORT EXCEL TUTTI I FORM")
        st.info("Carica Excel per importare dati in ogni form - TUTTI I FORM SUPPORTATI")

        c1,c2,c3=st.columns(3)
        with c1:
            st.markdown("**IMPORT VOLONTARI CON CF**")
            up_vol=st.file_uploader('Carica Excel Volontari',type=['xlsx'],key='up_vol')
            if up_vol is not None:
                try:
                    df_up=pd.read_excel(up_vol)
                    st.write(f"Trovati {len(df_up)} record")
                    st.dataframe(df_up.head(),use_container_width=True)
                    if st.button('IMPORTA VOLONTARI',key='imp_vol_btn',use_container_width=True,type='primary'):
                        for _,row in df_up.iterrows():
                            st.session_state.dati.append(row.to_dict())
                        save(FD,st.session_state.dati)
                        st.success(f"Importati {len(df_up)} volontari con CF per barcode")
                        st.rerun()
                except Exception as e:
                    st.error(f"Errore: {e}")

            st.markdown("**IMPORT ICONE**")
            up_icone=st.file_uploader('Carica Excel Icone',type=['xlsx'],key='up_icone')
            if up_icone is not None:
                try:
                    df_up=pd.read_excel(up_icone)
                    if st.button('IMPORTA ICONE',key='imp_icone_btn',use_container_width=True):
                        for _,row in df_up.iterrows():
                            st.session_state.icone.append(row.to_dict())
                        save(FI,st.session_state.icone)
                        st.success(f"Importate {len(df_up)} icone")
                        st.rerun()
                except Exception as e:
                    st.error(f"Errore: {e}")

        with c2:
            st.markdown("**IMPORT MAPPA POSTAZIONI**")
            up_mappa=st.file_uploader('Carica Excel Mappa',type=['xlsx'],key='up_mappa')
            if up_mappa is not None:
                try:
                    df_up=pd.read_excel(up_mappa)
                    st.write(f"Trovati {len(df_up)} record")
                    st.dataframe(df_up.head(),use_container_width=True)
                    if st.button('IMPORTA MAPPA',key='imp_mappa_btn',use_container_width=True,type='primary'):
                        for _,row in df_up.iterrows():
                            st.session_state.post.append(row.to_dict())
                        save(FP,st.session_state.post)
                        st.success(f"Importate {len(df_up)} postazioni con via comune lat lon")
                        st.rerun()
                except Exception as e:
                    st.error(f"Errore: {e}")

            st.markdown("**IMPORT EMERGENZE**")
            up_emerg=st.file_uploader('Carica Excel Emergenze',type=['xlsx'],key='up_emerg')
            if up_emerg is not None:
                try:
                    df_up=pd.read_excel(up_emerg)
                    if st.button('IMPORTA EMERGENZE',key='imp_emerg_btn',use_container_width=True):
                        for _,row in df_up.iterrows():
                            st.session_state.emerg.append(row.to_dict())
                        save(FE,st.session_state.emerg)
                        st.success(f"Importate {len(df_up)} emergenze")
                        st.rerun()
                except Exception as e:
                    st.error(f"Errore: {e}")

        with c3:
            st.markdown("**IMPORT CHECK IN**")
            up_check=st.file_uploader('Carica Excel Check In',type=['xlsx'],key='up_check')
            if up_check is not None:
                try:
                    df_up=pd.read_excel(up_check)
                    if st.button('IMPORTA CHECK IN',key='imp_check_btn',use_container_width=True):
                        for _,row in df_up.iterrows():
                            st.session_state.check.append(row.to_dict())
                        save(FC,st.session_state.check)
                        st.success(f"Importati {len(df_up)} check in")
                        st.rerun()
                except Exception as e:
                    st.error(f"Errore: {e}")

            st.markdown("**IMPORT DB RADIO**")
            up_radio=st.file_uploader('Carica Excel DB Radio',type=['xlsx'],key='up_radio')
            if up_radio is not None:
                try:
                    df_up=pd.read_excel(up_radio)
                    if st.button('IMPORTA RADIO',key='imp_radio_btn',use_container_width=True):
                        for _,row in df_up.iterrows():
                            st.session_state.radio.append(row.to_dict())
                        save(FR,st.session_state.radio)
                        st.success(f"Importate {len(df_up)} radio DMR ANALOGICA TETRA")
                        st.rerun()
                except Exception as e:
                    st.error(f"Errore: {e}")

            st.markdown("**IMPORT CONSEGNA RADIO**")
            up_cons=st.file_uploader('Carica Excel Consegna Radio',type=['xlsx'],key='up_cons')
            if up_cons is not None:
                try:
                    df_up=pd.read_excel(up_cons)
                    if st.button('IMPORTA CONSEGNA RADIO',key='imp_cons_btn',use_container_width=True):
                        for _,row in df_up.iterrows():
                            st.session_state.cons.append(row.to_dict())
                        save(FR2,st.session_state.cons)
                        st.success(f"Importate {len(df_up)} consegne con canale")
                        st.rerun()
                except Exception as e:
                    st.error(f"Errore: {e}")

    with tab3:
        st.markdown("#### BACKUP COMPLETO TUTTI I FORM")
        st.success("Backup completo di TUTTI I FORM in un unico file Excel con piu fogli")
        if st.button('CREA BACKUP COMPLETO EXCEL TUTTI I FORM',type='primary',use_container_width=True):
            out=BytesIO()
            with pd.ExcelWriter(out,engine='openpyxl') as writer:
                if st.session_state.dati:
                    pd.DataFrame(st.session_state.dati).to_excel(writer,sheet_name='Volontari',index=False)
                if st.session_state.post:
                    pd.DataFrame(st.session_state.post).to_excel(writer,sheet_name='Mappa',index=False)
                if st.session_state.emerg:
                    pd.DataFrame(st.session_state.emerg).to_excel(writer,sheet_name='Emergenze',index=False)
                if st.session_state.check:
                    pd.DataFrame(st.session_state.check).to_excel(writer,sheet_name='CheckIn',index=False)
                if st.session_state.radio:
                    pd.DataFrame(st.session_state.radio).to_excel(writer,sheet_name='DBRadio',index=False)
                if st.session_state.cons:
                    pd.DataFrame(st.session_state.cons).to_excel(writer,sheet_name='ConsegnaRadio',index=False)
                if st.session_state.icone:
                    pd.DataFrame(st.session_state.icone).to_excel(writer,sheet_name='Icone',index=False)
            st.session_state['bk_all']=out.getvalue()
            st.success('Backup completo TUTTI I FORM creato!')
        if 'bk_all' in st.session_state:
            st.download_button('SCARICA BACKUP COMPLETO EXCEL TUTTI I FORM',st.session_state['bk_all'],file_name='BACKUP_COMPLETO_ANA_VARESE_TUTTI_FORM.xlsx',use_container_width=True,type='primary')

        st.divider()
        st.markdown("#### RIPRISTINA DA BACKUP COMPLETO")
        up_bk=st.file_uploader('Carica Backup Completo Excel',type=['xlsx'],key='up_bk_all')
        if up_bk is not None:
            try:
                xls=pd.ExcelFile(up_bk)
                st.write(f"Fogli trovati: {xls.sheet_names}")
                if st.button('RIPRISTINA TUTTI I FORM DA BACKUP',type='primary',use_container_width=True):
                    if 'Volontari' in xls.sheet_names:
                        df=pd.read_excel(xls,'Volontari')
                        st.session_state.dati=df.to_dict('records')
                        save(FD,st.session_state.dati)
                    if 'Mappa' in xls.sheet_names:
                        df=pd.read_excel(xls,'Mappa')
                        st.session_state.post=df.to_dict('records')
                        save(FP,st.session_state.post)
                    if 'Emergenze' in xls.sheet_names:
                        df=pd.read_excel(xls,'Emergenze')
                        st.session_state.emerg=df.to_dict('records')
                        save(FE,st.session_state.emerg)
                    if 'CheckIn' in xls.sheet_names:
                        df=pd.read_excel(xls,'CheckIn')
                        st.session_state.check=df.to_dict('records')
                        save(FC,st.session_state.check)
                    if 'DBRadio' in xls.sheet_names:
                        df=pd.read_excel(xls,'DBRadio')
                        st.session_state.radio=df.to_dict('records')
                        save(FR,st.session_state.radio)
                    if 'ConsegnaRadio' in xls.sheet_names:
                        df=pd.read_excel(xls,'ConsegnaRadio')
                        st.session_state.cons=df.to_dict('records')
                        save(FR2,st.session_state.cons)
                    if 'Icone' in xls.sheet_names:
                        df=pd.read_excel(xls,'Icone')
                        st.session_state.icone=df.to_dict('records')
                        save(FI,st.session_state.icone)
                    st.success("RIPRISTINO COMPLETO TUTTI I FORM ESEGUITO!")
                    st.rerun()
            except Exception as e:
                st.error(f"Errore backup: {e}")

elif scelta=='Impostazioni Popup':
    torna()
    st.markdown('### IMPOSTAZIONI POPUP - TUA IMMAGINE CON FUMETTO - NO LOGO PC')
    st.success("PRIMA PAGINA DEVE AVERE SOLO TUA IMMAGINE CON FUMETTO 'ciao ragazzi, buon lavoro' - NO LOGO PC!")

    with st.form('popup_form'):
        p_titolo=st.text_input('Titolo',value=st.session_state.popup_cfg.get('titolo','ANA VARESE - VOLONTARIATO'))
        p_sotto=st.text_input('Sottotitolo',value=st.session_state.popup_cfg.get('sottotitolo','Ciao Ragazzi, Buon Lavoro!'))
        p_mostra=st.checkbox('Mostra popup',value=st.session_state.popup_cfg.get('mostra',True))
        if st.form_submit_button('SALVA IMPOSTAZIONI POPUP'):
            st.session_state.popup_cfg={'titolo':p_titolo,'sottotitolo':p_sotto,'mostra':p_mostra}
            save(FPOP,st.session_state.popup_cfg)
            st.success('Salvato')

    st.divider()
    st.markdown("### CARICA TUA IMMAGINE CON FUMETTO PER PRIMA PAGINA")
    st.error("ATTENZIONE: PRIMA PAGINA DEVE MOSTRARE TUA IMMAGINE CON FUMETTO, NON LOGO PC!")
    st.info("Carica qui la tua immagine con fumetto 'ciao ragazzi, buon lavoro' - questa apparira nella prima pagina")

    up=st.file_uploader('Carica TUA IMMAGINE CON FUMETTO per prima pagina (JPG/PNG)',type=['jpg','png','jpeg'],key='up_fumetto')
    if up:
        st.image(up,use_container_width=True,caption="Anteprima TUA IMMAGINE CON FUMETTO - PER PRIMA PAGINA - NO LOGO PC")
        if st.button('SALVA COME copertina.jpg - TUA IMMAGINE FUMETTO PER PRIMA PAGINA',type='primary',use_container_width=True):
            open('copertina.jpg','wb').write(up.getbuffer())
            st.success('SALVATA! Ora prima pagina mostra SOLO TUA IMMAGINE CON FUMETTO - NO LOGO PC!')
            st.balloons()

    st.divider()
    st.markdown("**FILE PRESENTI - CONTROLLO PRIMA PAGINA:**")
    for img_name in ['copertina.jpg','copertina_fumetto.jpg','mia_immagine_fumetto.jpg']:
        if os.path.exists(img_name):
            st.success(f"✅ {img_name} PRESENTE - TUA IMMAGINE CON FUMETTO PER PRIMA PAGINA OK - NO LOGO PC")
            st.image(img_name,width=400,caption=f"{img_name} - TUA IMMAGINE FUMETTO PER PRIMA PAGINA")
        else:
            st.error(f"❌ {img_name} MANCANTE - PRIMA PAGINA MOSTRERA ERRORE - CARICA TUA IMMAGINE FUMETTO!")

    st.divider()
    st.markdown("**ALTRI FILE (NON PER PRIMA PAGINA):**")
    for img_name in ['Tesserino-Ezio.JPG','logo.png']:
        if os.path.exists(img_name):
            if 'logo' in img_name:
                st.warning(f"⚠️ {img_name} - QUESTO E LOGO - NON VA IN PRIMA PAGINA - PRIMA PAGINA DEVE AVERE TUA IMMAGINE FUMETTO!")
                st.image(img_name,width=200,caption=f"{img_name} - LOGO - NON PER PRIMA PAGINA")
            else:
                st.info(f"ℹ️ {img_name} - Template tesserino")
                st.image(img_name,width=300)

    st.divider()
    if st.button('MOSTRA ANTEPRIMA POPUP CON TUA IMMAGINE FUMETTO',type='primary',use_container_width=True):
        st.session_state.popup_shown=False
        st.rerun()

else:
    torna()
    st.markdown(f"### {scelta}")
    st.info("Sezione in aggiornamento - funzioni principali in Volontari, Mappa, Tesserino Regionale, Backup")
