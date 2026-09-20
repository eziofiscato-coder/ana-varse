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
def hp(p): return hashlib.sha256(p.encode()).hexdigest()
def gaddr(lat,lon):
    try:
        u=f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=jsonv2&accept-language=it"
        r=requests.get(u,headers={'User-Agent':'ana-varese'},timeout=8)
        if r.status_code==200:
            a=r.json().get('address',{})
            com=a.get('city') or a.get('town') or a.get('village') or ''
            via=a.get('road') or ''
            return com,via
    except:
        pass
    return '',''
def fmt_date(d): return d.strftime("%d/%m/%Y") if isinstance(d,date) else str(d)
def export_excel(df):
    out=BytesIO()
    with pd.ExcelWriter(out,engine='openpyxl') as w:
        df.to_excel(w,index=False)
    return out.getvalue()
def crea_barcode(cf):
    try:
        import barcode
        from barcode.writer import ImageWriter
        code=barcode.get('code128', (cf or "0000000000000000")[:16].upper(), writer=ImageWriter())
        buf=BytesIO(); code.write(buf); buf.seek(0); return buf.getvalue()
    except:
        return None
def crea_tesserino(vol,foto_path,template_path):
    try:
        if not HAS_PIL: return None
        if template_path and os.path.exists(template_path):
            base=Image.open(template_path).convert("RGB")
            tess=base.copy(); draw=ImageDraw.Draw(tess)
        else:
            tess=Image.new('RGB',(860,540),'white'); draw=ImageDraw.Draw(tess)
        try:
            fn=ImageFont.truetype("arialbd.ttf",20); fo=ImageFont.truetype("arial.ttf",14)
        except:
            fn=ImageFont.load_default(); fo=ImageFont.load_default()
        W,H=tess.size
        fx,fy,fw,fh=int(W*0.015),int(H*0.22),int(W*0.27),int(H*0.58)
        if foto_path and os.path.exists(foto_path):
            try:
                foto=Image.open(foto_path).convert("RGB").resize((fw,fh))
                tess.paste(foto,(fx,fy))
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
        buf=BytesIO(); tess.save(buf,format='PNG'); buf.seek(0); return buf.getvalue()
    except Exception as e:
        st.error(f"Errore: {e}")
        return None

FD='dati.json'; FU='utenti.json'; FP='post.json'; FI='icone.json'; FT='tip.json'; FO='odv.json'; FE='emerg.json'; FC='check.json'; FR='radio.json'; FR2='cons.json'; FPOP='popup.json'
for k,v in [('dati',[]),('post',[]),('icone',[]),('tip',[]),('odv',[]),('emerg',[]),('check',[]),('radio',[]),('cons',[]),('menu','Dashboard'),('auth',False),('lat',45.8205),('lon',8.8250),('com',''),('via',''),('sel',-1),('zoom',16),('clat',None),('clon',None),('exp1',False),('popup_shown',False),('popup_cfg',{'titolo':'ANA VARESE - VOLONTARIATO','sottotitolo':'Ciao Ragazzi, Buon Lavoro!','mostra':True})]:
    if k not in st.session_state:
        st.session_state[k]=v

st.session_state.dati=load(FD,[]); st.session_state.post=load(FP,[]); st.session_state.icone=load(FI,[]); st.session_state.tip=load(FT,[]); st.session_state.odv=load(FO,[]); st.session_state.emerg=load(FE,[]); st.session_state.check=load(FC,[]); st.session_state.radio=load(FR,[]); st.session_state.cons=load(FR2,[]); st.session_state.popup_cfg=load(FPOP,{'titolo':'ANA VARESE - VOLONTARIATO','sottotitolo':'Ciao Ragazzi, Buon Lavoro!','mostra':True})
uts=load(FU,[])
if not uts:
    uts=[{'username':'admin','password':hp('ana2024')}]
    save(FU,uts)
if not st.session_state.tip:
    st.session_state.tip=['Presidio','Blocco stradale','Punto ritrovo','Parcheggio','Sanitario','Logistica','Altro']; save(FT,st.session_state.tip)
if not st.session_state.odv:
    st.session_state.odv=['ANA Varese','Protezione Civile Varese','Croce Rossa','Alpini','AIB','Altro']; save(FO,st.session_state.odv)
if not st.session_state.icone:
    st.session_state.icone=[{'nome':'Presidio','col':'blue','file':''}]; save(FI,st.session_state.icone)

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

# POPUP PRIMA PAGINA - SOLO TUA IMMAGINE FUMETTO - MAI LOGO PC
if st.session_state.popup_cfg.get('mostra',True) and not st.session_state.popup_shown:
    st.markdown(f"<h1 style='text-align:center;color:#0e7a3d;'>{st.session_state.popup_cfg.get('titolo','ANA VARESE - VOLONTARIATO')}</h1>",unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align:center;color:#0e7a3d;'>{st.session_state.popup_cfg.get('sottotitolo','Ciao Ragazzi, Buon Lavoro!')}</h3>",unsafe_allow_html=True)
    st.divider()
    c1,c2,c3=st.columns([1,2,1])
    with c2:
        # CERCA SOLO TUA IMMAGINE FUMETTO - MAI LOGO PC
        img_found=False
        for img_name in ['copertina.jpg','copertina_fumetto.jpg','mia_immagine_fumetto.jpg','fumetto.jpg']:
            if os.path.exists(img_name):
                try:
                    st.image(img_name,use_container_width=True)
                    st.success(f"✅ TUA IMMAGINE FUMETTO TROVATA: {img_name} - PRIMA PAGINA OK! - NO LOGO PC")
                    img_found=True
                    break
                except:
                    pass
        if not img_found:
            st.error("❌ MANCA LA TUA IMMAGINE CON FUMETTO SULLA PRIMA PAGINA!")
            st.warning("Non vedo copertina.jpg su GitHub!")
            st.info("Carica la TUA immagine con fumetto 'Ciao Ragazzi, Buon Lavoro!' come copertina.jpg")
            st.markdown("<div style='background:#ffebee;padding:20px;border-radius:10px;text-align:center;border:3px dashed red;'><h2>MANCA TUA IMMAGINE FUMETTO</h2><p>Carica copertina.jpg su GitHub</p><p>NON deve essere logo PC</p></div>",unsafe_allow_html=True)
        st.divider()
        st.markdown(f"<div style='background:#e8f5e9;padding:15px;border-radius:10px;border:2px solid #0e7a3d;text-align:center;'><b>ANA Varese - Protezione Civile</b><br><b style='color:#0e7a3d;'>Ciao Ragazzi, Buon Lavoro!</b><br><br>Volontari: {len(st.session_state.dati)} Postazioni: {len(st.session_state.post)}</div>",unsafe_allow_html=True)
        st.divider()
        if st.button("ENTRA NEL SISTEMA",type="primary",use_container_width=True):
            st.session_state.popup_shown=True
            st.rerun()
    st.stop()

if not st.session_state.auth:
    header()
    c1,c2,c3=st.columns([1,2,1])
    with c2:
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
            st.session_state.menu='Volontari'; st.rerun()
        if st.button('MAPPA',use_container_width=True,key='d2'):
            st.session_state.menu='Mappa'; st.rerun()
        if st.button('TESSERINO REGIONALE',use_container_width=True,key='d3',type="primary"):
            st.session_state.menu='Tesserino Regionale'; st.rerun()
    with c2:
        if st.button('BACKUP IMPORT EXPORT TUTTI I FORM',use_container_width=True,key='d9',type="primary"):
            st.session_state.menu='Backup'; st.rerun()
        if st.button('IMPOSTAZIONI POPUP - TUA IMMAGINE FUMETTO',use_container_width=True,key='d10'):
            st.session_state.menu='Impostazioni Popup'; st.rerun()
    with c3:
        st.metric('Volontari',len(st.session_state.dati))
        st.metric('Postazioni',len(st.session_state.post))
    st.divider()
    st.markdown("**PRIMA PAGINA - TUA IMMAGINE CON FUMETTO (NO LOGO PC):**")
    found=False
    for img_name in ['copertina.jpg','copertina_fumetto.jpg','mia_immagine_fumetto.jpg','fumetto.jpg']:
        if os.path.exists(img_name):
            st.image(img_name,width=400,caption=f"{img_name} - TUA IMMAGINE FUMETTO - PRIMA PAGINA OK - NO LOGO PC")
            st.success("✅ PRIMA PAGINA OK - TUA IMMAGINE FUMETTO TROVATA!")
            found=True
            break
    if not found:
        st.error("❌ MANCA copertina.jpg - NON VEDI TUA IMMAGINE FUMETTO PERCHE MANCA FILE!")
        st.warning("Carica la TUA immagine con fumetto come copertina.jpg su GitHub!")

elif scelta=='Volontari':
    torna()
    st.markdown('### VOLONTARI')
    t1,t2=st.tabs(['Anagrafica Foto CF ODV','Elenco e Tesserino'])
    with t1:
        with st.form('vol1'):
            c1,c2=st.columns(2)
            with c1:
                a1=st.text_input('Nome *')
                a2=st.text_input('Cognome *')
                a_cf=st.text_input('CF * per barcode')
                a_foto=st.file_uploader('Foto',type=['jpg','png','jpeg'],key='f1')
            with c2:
                a_odv=st.selectbox('ODV',['A.N.A. Sezione di Varese','Protezione Civile Varese','ANA Varese','Croce Rossa','Alpini','Altro'])
                a_tess=st.text_input('Tessera')
                if a_foto:
                    st.image(a_foto,width=120)
            if st.form_submit_button('SALVA VOLONTARIO'):
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
            st.dataframe(pd.DataFrame(st.session_state.dati),use_container_width=True)
            vol_list=[d.get('Nome','') for d in st.session_state.dati]
            sel=st.selectbox('Seleziona per Tesserino',vol_list,key='tess1')
            vol_data={}
            for d in st.session_state.dati:
                if d.get('Nome','')==sel:
                    vol_data=d
                    break
            tess=crea_tesserino(vol_data,vol_data.get('FotoFile',''),"Tesserino-Ezio.JPG" if os.path.exists("Tesserino-Ezio.JPG") else None)
            if tess:
                st.image(tess,use_container_width=True)
                st.download_button('SCARICA TESSERINO',tess,file_name=f"Tesserino_{sel}.png",mime='image/png',type='primary')

elif scelta=='Mappa':
    torna()
    st.markdown('### MAPPA - VIA COMUNE LAT LON + ESPANDI + GOOGLE MAPS WAZE')
    c1,c2=st.columns([3,1])
    with c1:
        st.info("Clicca sulla mappa per via comune lat lon automatici")
    with c2:
        if st.button('ESPANDI SCHERMO INTERO',use_container_width=True):
            st.session_state.exp1=True
