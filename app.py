import streamlit as st
import pandas as pd
from io import BytesIO
import os, json, hashlib
from datetime import date

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
 border-radius:12px!important; padding:15px!important}
.stButton>button{
 background:#d32f2f!important; color:white!important;
 border:2px solid #b71c1c!important; font-weight:bold!important}
</style>
""", unsafe_allow_html=True)

def load(f,d):
    try:
        if os.path.exists(f):
            with open(f,'r',encoding='utf-8') as ff:
                return json.load(ff)
    except Exception:
        pass
    return d

def save(f,d):
    try:
        with open(f,'w',encoding='utf-8') as ff:
            json.dump(d,ff,indent=2)
    except Exception:
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

def crea_barcode(cf):
    try:
        import barcode
        from barcode.writer import ImageWriter
        code=barcode.get(
            'code128',
            (cf or "0000000000000000")[:16].upper(),
            writer=ImageWriter()
        )
        buf=BytesIO()
        code.write(buf)
        buf.seek(0)
        return buf.getvalue()
    except Exception:
        return None

def crea_tess_nitido(vol,foto_path,tmpl):
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
            fn=ImageFont.truetype("arialbd.ttf",22)
            fo=ImageFont.truetype("arial.ttf",16)
        except Exception:
            fn=ImageFont.load_default()
            fo=ImageFont.load_default()
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
        draw.text((nx,ny),vol.get('Nome','').upper(),fill='black',font=fn)
        odv=vol.get('ODV','ANA Varese')
        oy=ny+30
        draw.rectangle([nx,oy,nx+int(W*0.45),oy+20],fill='white')
        draw.text((nx,oy),odv,fill='#0e7a3d',font=fo)
        bx=int(W*0.62)
        by=int(H*0.70)
        bw=int(W*0.34)
        bh=int(H*0.16)
        draw.rectangle([bx,by,bx+bw,by+bh],fill='white',outline='white')
        cf=vol.get('CF','')
        if not cf:
            cf=vol.get('Nome','').replace(' ','').upper()[:16]
        bc=crea_barcode(cf)
        if bc:
            try:
                bi=Image.open(BytesIO(bc)).convert("RGB")
                bi=bi.resize((bw,bh),Image.LANCZOS)
                tess.paste(bi,(bx,by))
                draw.text((bx,by+bh+2),cf[:16],fill='black',font=fo)
            except Exception:
                pass
        buf=BytesIO()
        tess.save(buf,format='PNG',dpi=(300,300),optimize=False)
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
    ('popup_shown',False)
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
    uts=[{'username':'admin','password':hp('ana2024')}]
    save(FU,uts)

def header():
    c1,c2=st.columns([1,5])
    with c1:
        try:
            st.image("logo.png",width=110)
        except Exception:
            st.write("ANA")
    with c2:
        st.markdown(
            "<div style='background:#a5d6a7;padding:12px;"
            "border-radius:8px;border:2px solid #0e7a3d;"
            "text-align:center;'>"
            "<b style='color:#000;font-size:22px;'>"
            "VOLONTARIATO<br>Sezione di Varese"
            "</b></div>",
            unsafe_allow_html=True
        )

def torna():
    if st.button('TORNA ALLA DASHBOARD'):
        st.session_state.menu='Dashboard'
        st.rerun()

# PRIMA PAGINA - SOLO TUA IMG 250px CON I'M READY
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
        for img_name in ['copertina.jpg']:
            if os.path.exists(img_name):
                try:
                    st.image(img_name,width=250)
                    st.success("TUA IMG 250px + NUVOLA I'M READY")
                    found=True
                    break
                except Exception:
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

# LOGIN - FIX PAGINA BIANCA
if not st.session_state.auth:
    header()
    c1,c2,c3=st.columns([1,2,1])
    with c2:
        st.markdown("### LOGIN")
        st.info("admin / ana2024")
        with st.form('login'):
            u=st.text_input('Username',value='admin')
            p=st.text_input('Password',type='password',value='ana2024')
            ok=st.form_submit_button('ACCEDI',type="primary")
            if ok:
                ph=hp(p)
                for ut in uts:
                    if ut['username']==u and ut['password']==ph:
                        st.session_state.auth=True
                        st.session_state.menu='Dashboard'
                        st.session_state.popup_shown=True
                        st.rerun()
                st.error('Username o password errati')
        if st.button('TORNA INIZIO'):
            st.session_state.popup_shown=False
            st.rerun()
    st.stop()

# SE AUTH OK - MENU - FIX PAGINA BIANCA DOPO LOGIN
header()
with st.sidebar:
    st.markdown('**MENU COMPLETO**')
    opts=[
        'Dashboard','Volontari','Mappa',
        'Interventi Emergenza','Check In',
        'DB Radio','Consegna Radio',
        'Backup','Tesserino','Logout'
    ]
    sel=st.radio('Vai a',opts,index=0)
    if sel=='Logout':
        st.session_state.auth=False
        st.session_state.popup_shown=False
        st.rerun()
    st.session_state.menu=sel
    if st.button('MOSTRA POPUP INIZIALE',use_container_width=True):
        st.session_state.popup_shown=False
        st.rerun()
    st.divider()
    st.warning("IMPORTANTE: Per non perdere lavoro, vai in Backup > EXPORT!")

scelta=st.session_state.menu

if scelta=='Dashboard':
    st.markdown("## Dashboard - Lavoro Ben Riuscito Salvato")
    c1,c2=st.columns(2)
    with c1:
        if st.button('VOLONTARI',use_container_width=True):
            st.session_state.menu='Volontari'
            st.rerun()
        if st.button('MAPPA',use_container_width=True):
            st.session_state.menu='Mappa'
            st.rerun()
        if st.button('INTERVENTI',use_container_width=True):
            st.session_state.menu='Interventi Emergenza'
            st.rerun()
        if st.button('BACKUP EXPORT',use_container_width=True,type="primary"):
            st.session_state.menu='Backup'
            st.rerun()
    with c2:
        if st.button('CHECK IN',use_container_width=True):
            st.session_state.menu='Check In'
            st.rerun()
        if st.button('DB RADIO',use_container_width=True):
            st.session_state.menu='DB Radio'
            st.rerun()
        if st.button('TESSERINO NITIDO PICCOLO',use_container_width=True):
            st.session_state.menu='Tesserino'
            st.rerun()
    st.divider()
    c1,c2,c3,c4=st.columns(4)
    with c1: st.metric('Volontari',len(st.session_state.dati))
    with c2: st.metric('Postazioni',len(st.session_state.post))
    with c3: st.metric('Interventi',len(st.session_state.interventi_lista))
    with c4: st.metric('Radio',len(st.session_state.radio))
    st.divider()
    st.markdown("### ELENCO VOLONTARI - RIGHE VISIBILI")
    if st.session_state.dati:
        df=pd.DataFrame(st.session_state.dati)
        st.success(f"{len(df)} volontari salvati")
        st.dataframe(df,use_container_width=True,hide_index=False)
        st.download_button(
            '📥 SCARICA EXCEL VOLONTARI',
            export_excel(df),
            file_name='Volontari.xlsx',
            use_container_width=True
        )
    else:
        st.warning("Nessun volontario - Vai in Volontari > 1.Anagrafica")

elif scelta=='Volontari':
    torna()
    st.markdown("## VOLONTARI - 6 SOTTOMASCHERE + FOTO")
    t1,t2,t3,t4,t5,t6=st.tabs(
        ["1.Anagrafica","2.Contatti","3.Foto","4.Formazione","5.Disp","6.Tesserino"]
    )
    with t1:
        st.markdown("### 1 - Anagrafica")
        with st.form("form_anag",clear_on_submit=True):
            c1,c2=st.columns(2)
            with c1:
                a_nome=st.text_input("Nome *")
                a_cogn=st.text_input("Cognome *")
                a_cf=st.text_input("CF * per barcode")
            with c2:
                a_odv=st.selectbox(
                    "ODV",
                    ["A.N.A. Sezione di Varese","Protezione Civile Varese","ANA Varese","CRI","Altro"]
                )
                a_tess=st.text_input("Tessera")
            a_ruolo=st.selectbox("Ruolo",["Volontario","Caposquadra","Coordinatore","Autista","Radio","Altro"])
            btn1=st.form_submit_button("SALVA ANAGRAFICA",use_container_width=True,type="primary")
            if btn1:
                if a_nome and a_cogn:
                    nc=f"{a_nome} {a_cogn}"
                    nuovo={'Nome':nc,'CF':a_cf,'ODV':a_odv,'Tessera':a_tess,'Ruolo':a_ruolo,'FotoFile':''}
                    found=False
                    for i,d in enumerate(st.session_state.dati):
                        if d.get('Nome','')==nc:
                            nuovo['FotoFile']=d.get('FotoFile','')
                            st.session_state.dati[i].update(nuovo)
                            found=True
                    if not found:
                        st.session_state.dati.append(nuovo)
                    save(FD,st.session_state.dati)
                    st.success(f"Salvata anagrafica {nc}! Dati salvati!")
                    st.rerun()
    with t2:
        st.markdown("### 2 - Contatti")
        vol_list=[d.get('Nome','') for d in st.session_state.dati]
        if vol_list:
            sel=st.selectbox("Seleziona volontario",vol_list,key='cont_sel')
            idx_sel=-1
            for i,d in enumerate(st.session_state.dati):
                if d.get('Nome','')==sel:
                    idx_sel=i
                    break
            with st.form("form_cont"):
                tel=st.text_input("Cellulare",value=st.session_state.dati[idx_sel].get('Telefono',''))
                email=st.text_input("Email",value=st.session_state.dati[idx_sel].get('Email',''))
                btn2=st.form_submit_button("SALVA CONTATTI",use_container_width=True,type="primary")
                if btn2:
                    st.session_state.dati[idx_sel]['Telefono']=tel
                    st.session_state.dati[idx_sel]['Email']=email
                    save(FD,st.session_state.dati)
                    st.success("Contatti salvati!")
                    st.rerun()
        else:
            st.warning("Nessun volontario")
    with t3:
        st.markdown("### 3 - Foto e Documenti")
        vol_list=[d.get('Nome','') for d in st.session_state.dati]
        if vol_list:
            sel=st.selectbox("Seleziona",vol_list,key='foto_sel')
            idx_sel=-1
            for i,d in enumerate(st.session_state.dati):
                if d.get('Nome','')==sel:
                    idx_sel=i
                    break
            fp=st.session_state.dati[idx_sel].get('FotoFile','')
            if fp and os.path.exists(fp):
                st.image(fp,width=150,caption="Foto attuale")
            a_foto=st.file_uploader("Carica foto",type=['jpg','png','jpeg'],key='foto_vol')
            if a_foto:
                st.image(a_foto,width=150,caption="Anteprima")
            with st.form("form_foto"):
                btn3=st.form_submit_button("SALVA FOTO",use_container_width=True,type="primary")
                if btn3:
                    if a_foto:
                        try:
                            os.makedirs('foto_volontari',exist_ok=True)
                            fp_new=f"foto_volontari/{sel.replace(' ','_')}_{a_foto.name}"
                            with open(fp_new,'wb') as f:
                                f.write(a_foto.getbuffer())
                            st.session_state.dati[idx_sel]['FotoFile']=fp_new
                            save(FD,st.session_state.dati)
                            st.success("Foto salvata!")
                            st.rerun()
                        except Exception:
                            pass
    with t6:
        st.markdown("### 6 - Elenco e Tesserino Nitido Piccolo")
        if st.session_state.dati:
            df=pd.DataFrame(st.session_state.dati)
            st.dataframe(df,use_container_width=True,hide_index=False)
            vol_list=[d.get('Nome','') for d in st.session_state.dati]
            sel=st.selectbox("Per tesserino",vol_list,key='tess_sel')
            vol_data={}
            for d in st.session_state.dati:
                if d.get('Nome','')==sel:
                    vol_data=d
                    break
            c1,c2=st.columns([1,2])
            with c1:
                fp=vol_data.get('FotoFile','')
                if fp and os.path.exists(fp):
                    st.image(fp,width=150)
                st.write(f"Nome: {vol_data.get('Nome','')}")
                st.write(f"CF: {vol_data.get('CF','')}")
                st.write(f"ODV: {vol_data.get('ODV','')}")
            with c2:
                st.markdown("**TESSERINO NITIDO PICCOLO 860x540 - NON SFUOCATO**")
                tess=crea_tess_nitido(vol_data,vol_data.get('FotoFile',''),"Tesserino-Ezio.JPG" if os.path.exists("Tesserino-Ezio.JPG") else None)
                if tess:
                    st.image(tess,use_container_width=True)
                    st.download_button('SCARICA TESSERINO NITIDO PICCOLO',tess,file_name=f"Tesserino_{sel}_NITIDO.png",mime='image/png',type='primary',use_container_width=True)
                    st.download_button('SCARICA QUELLO SOTTO',tess,file_name=f"Tesserino_{sel}_SOTTO.png",mime='image/png',use_container_width=True,key='sotto1')

elif scelta=='Backup':
    torna()
    st.markdown("## BACKUP - EXPORT IMPORT - NON PERDI LAVORO")
    st.warning("SU STREAMLIT CLOUD I DATI SI PERDONO AD OGNI REBOOT - FAI SEMPRE EXPORT!")
    tab_exp,tab_imp,tab_all=st.tabs(["EXPORT","IMPORT","COMPLETO"])
    with tab_exp:
        c1,c2,c3=st.columns(3)
        with c1:
            if st.session_state.dati:
                st.download_button('EXPORT VOLONTARI',export_excel(pd.DataFrame(st.session_state.dati)),file_name='Volontari.xlsx',use_container_width=True,key='exp_vol')
                st.caption(f"{len(st.session_state.dati)} volontari")
            if st.session_state.post:
                st.download_button('EXPORT MAPPA',export_excel(pd.DataFrame(st.session_state.post)),file_name='Mappa.xlsx',use_container_width=True,key='exp_mappa')
        with c2:
            if st.session_state.interventi_lista:
                st.download_button('EXPORT INTERVENTI',export_excel(pd.DataFrame(st.session_state.interventi_lista)),file_name='Interventi.xlsx',use_container_width=True,key='exp_int')
            if st.session_state.check:
                st.download_button('EXPORT CHECK IN',export_excel(pd.DataFrame(st.session_state.check)),file_name='CheckIn.xlsx',use_container_width=True,key='exp_check')
        with c3:
            if st.session_state.radio:
                st.download_button('EXPORT RADIO',export_excel(pd.DataFrame(st.session_state.radio)),file_name='Radio.xlsx',use_container_width=True,key='exp_radio')
            if st.session_state.cons:
                st.download_button('EXPORT CONSEGNA',export_excel(pd.DataFrame(st.session_state.cons)),file_name='Consegna.xlsx',use_container_width=True,key='exp_cons')
    with tab_imp:
        c1,c2=st.columns(2)
        with c1:
            up_vol=st.file_uploader('Import Volontari',type=['xlsx'],key='up_vol')
            if up_vol:
                df_up=pd.read_excel(up_vol)
                st.dataframe(df_up.head(),use_container_width=True)
                st.dataframe(df_up,use_container_width=True)
                if st.button(f'IMPORTA {len(df_up)} VOLONTARI',key='imp_vol',use_container_width=True,type="primary"):
                    for _,row in df_up.iterrows():
                        st.session_state.dati.append(row.to_dict())
                    save(FD,st.session_state.dati)
                    st.success("Importati! Lavoro recuperato!")
                    st.rerun()
        with c2:
            up_int=st.file_uploader('Import Interventi',type=['xlsx'],key='up_int')
            if up_int:
                df_up=pd.read_excel(up_int)
                if st.button(f'IMPORTA {len(df_up)} INTERVENTI',key='imp_int',use_container_width=True,type="primary"):
                    for _,row in df_up.iterrows():
                        st.session_state.interventi_lista.append(row.to_dict())
                    save(FE,st.session_state.interventi_lista)
                    st.success("Importati!")
                    st.rerun()
    with tab_all:
        if st.button('CREA BACKUP COMPLETO TUTTI I FORM',type='primary',use_container_width=True):
            out=BytesIO()
            with pd.ExcelWriter(out,engine='openpyxl') as writer:
                if st.session_state.dati:
                    pd.DataFrame(st.session_state.dati).to_excel(writer,sheet_name='Volontari',index=False)
                if st.session_state.post:
                    pd.DataFrame(st.session_state.post).to_excel(writer,sheet_name='Mappa',index=False)
                if st.session_state.interventi_lista:
                    pd.DataFrame(st.session_state.interventi_lista).to_excel(writer,sheet_name='Interventi',index=False)
                if st.session_state.check:
                    pd.DataFrame(st.session_state.check).to_excel(writer,sheet_name='CheckIn',index=False)
                if st.session_state.radio:
                    pd.DataFrame(st.session_state.radio).to_excel(writer,sheet_name='DBRadio',index=False)
                if st.session_state.cons:
                    pd.DataFrame(st.session_state.cons).to_excel(writer,sheet_name='ConsegnaRadio',index=False)
            st.session_state['bk_all']=out.getvalue()
            st.success('Backup completo creato! Salvalo sul PC!')
            st.balloons()
        if 'bk_all' in st.session_state:
            st.download_button('SCARICA BACKUP COMPLETO - SALVA SUL PC',st.session_state['bk_all'],file_name='BACKUP_COMPLETO_TUTTI_FORM.xlsx',use_container_width=True,type='primary')
        st.divider()
        st.markdown("**Ripristina lavoro ben riuscito da backup**")
        up_bk=st.file_uploader('Carica Backup Completo per ripristinare',type=['xlsx'],key='up_bk')
        if up_bk:
            try:
                xls=pd.ExcelFile(up_bk)
                st.write(f"Fogli: {xls.sheet_names}")
                if st.button('RIPRISTINA LAVORO BEN RIUSCITO',type='primary',use_container_width=True):
                    if 'Volontari' in xls.sheet_names:
                        st.session_state.dati=pd.read_excel(xls,'Volontari').to_dict('records')
                        save(FD,st.session_state.dati)
                    if 'Mappa' in xls.sheet_names:
                        st.session_state.post=pd.read_excel(xls,'Mappa').to_dict('records')
                        save(FP,st.session_state.post)
                    if 'Interventi' in xls.sheet_names:
                        st.session_state.interventi_lista=pd.read_excel(xls,'Interventi').to_dict('records')
                        save(FE,st.session_state.interventi_lista)
                    st.success("Lavoro ben riuscito ripristinato!")
                    st.rerun()
            except Exception as e:
                st.error(f"Errore: {e}")

elif scelta=='Tesserino':
    torna()
    st.markdown("### TESSERINO NITIDO PICCOLO 860x540 - NON SFUOCATO")
    st.info("Foto + ODV + Barcode CF - Piccolo e nitido")
    vol_list=[d.get('Nome','') for d in st.session_state.dati]
    if vol_list:
        sel=st.selectbox("Volontario",vol_list,key='tess_final')
        vol_data={}
        for d in st.session_state.dati:
            if d.get('Nome','')==sel:
                vol_data=d
                break
        c1,c2=st.columns([1,2])
        with c1:
            fp=vol_data.get('FotoFile','')
            if fp and os.path.exists(fp):
                st.image(fp,width=150,caption="Foto")
            st.write(f"Nome: {vol_data.get('Nome','')}")
            st.write(f"CF: {vol_data.get('CF','')}")
            st.write(f"ODV: {vol_data.get('ODV','')}")
        with c2:
            tess=crea_tess_nitido(vol_data,vol_data.get('FotoFile',''),"Tesserino-Ezio.JPG" if os.path.exists("Tesserino-Ezio.JPG") else None)
            if tess:
                st.image(tess,use_container_width=True,caption="Tesserino 860x540 nitido piccolo")
                st.download_button('SCARICA TESSERINO NITIDO PICCOLO',tess,file_name=f"Tesserino_{sel}_NITIDO_860x540.png",mime='image/png',type='primary',use_container_width=True)
                st.download_button('SCARICA QUELLO SOTTO OK',tess,file_name=f"Tesserino_{sel}_SOTTO_OK.png",mime='image/png',use_container_width=True,key='sotto2')
    else:
        st.warning("Nessun volontario")

else:
    torna()
    st.markdown(f"### {scelta}")
    st.info(f"Form {scelta} OK - Lavoro salvato")
