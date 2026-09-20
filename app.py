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

st.set_page_config(page_title="ANA Varese", layout="wide")

st.markdown("""
<style>
.stApp{background-color:#e8f5e9!important}
.stForm{background-color:#f1f8e9!important;
 border:2px solid #81c784!important;
 border-radius:12px!important; padding:20px!important}
.stButton>button{background-color:#d32f2f!important;
 color:white!important; border:2px solid #b71c1c!important;
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
            base=Image.open(template_path).convert("RGB")
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
        fx,fy,fw,fh=int(W*0.015),int(H*0.22),int(W*0.27),int(H*0.58)
        if foto_path and os.path.exists(foto_path):
            try:
                foto=Image.open(foto_path).convert("RGB")
                foto=foto.resize((fw,fh))
                tess.paste(foto,(fx,fy))
            except:
                pass
        nx,ny=int(W*0.38),int(H*0.36)
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
        draw.text((nx,oy),odv,fill='black',font=fo)
        buf=BytesIO()
        tess.save(buf,format='PNG')
        buf.seek(0)
        return buf.getvalue()
    except Exception as e:
        st.error(f"Errore: {e}")
        return None

# DATI
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
    uts=[{'username':'admin','password':hp('ana2024')}]
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
            "<div style='background:#a5d6a7;padding:15px;"
            "border-radius:8px;border:2px solid #0e7a3d;"
            "text-align:center;'>"
            "<b style='color:#000;font-size:26px;'>"
            "VOLONTARIATO<br>Sezione di Varese</b></div>",
            unsafe_allow_html=True
        )

def torna():
    if st.button('TORNA ALLA DASHBOARD'):
        st.session_state.menu='Dashboard'
        st.rerun()

# PRIMA PAGINA - SOLO TUA IMMAGINE PICCOLA 250px
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
            'copertina_fumetto.jpg',
            'fumetto.jpg'
        ]:
            if os.path.exists(img_name):
                try:
                    st.image(img_name,width=250)
                    st.success(
                        f"TUA IMMAGINE PICCOLA: {img_name} "
                        "- SOLO PRIMA PAGINA - NO LOGO PC"
                    )
                    found=True
                    break
                except:
                    pass
        if not found:
            st.warning("Carica copertina.jpg - 250px")
        st.divider()
        if st.button(
            "ENTRA NEL SISTEMA",
            type="primary",
            use_container_width=True
        ):
            st.session_state.popup_shown=True
            st.rerun()
    st.stop()

# PAGINA LOGIN - RIPRISTINATA
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
            u=st.text_input('Username',value='admin')
            p=st.text_input('Password',type='password',value='ana2024')
            ok=st.form_submit_button('ACCEDI')
            if ok:
                ph=hp(p)
                for ut in uts:
                    if ut['username']==u and ut['password']==ph:
                        st.session_state.auth=True
                        st.rerun()
                st.error('Username o password errati')
        if st.button('TORNA ALLA PAGINA INIZIALE'):
            st.session_state.popup_shown=False
            st.rerun()
    st.stop()

def pagina_interventi_emergenza():
    st.markdown("## INTERVENTI EMERGENZA")
    with st.form("form_emergenza", clear_on_submit=True):
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
                ["ANA Varese","ANA Sezione Varese",
                 "Protezione Civile Lombardia",
                 "Croce Rossa","Altro"]
            )
        azione_int=st.text_area("Azione *", height=100)
        salva=st.form_submit_button(
            "SALVA INTERVENTO EMERGENZA",
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
                    "ODV Operativa":odv_int,
                    "Azione":azione_int
                }
                st.session_state.interventi_lista.append(nuovo)
                save(FE,st.session_state.interventi_lista)
                st.success("Salvato!")
                st.rerun()
    if st.session_state.interventi_lista:
        df=pd.DataFrame(st.session_state.interventi_lista)
        st.dataframe(df, use_container_width=True)
        st.download_button(
            "Scarica CSV",
            df.to_csv(index=False).encode('utf-8'),
            "interventi_emergenza.csv"
        )

def pagina_backup():
    st.markdown("## BACKUP - EXPORT E IMPORT PER VARI FORM")
    st.info("Export e import per tutti i form e backup completo")
    tab_exp, tab_imp, tab_all = st.tabs([
        "EXPORT SINGOLI",
        "IMPORT SINGOLI",
        "BACKUP COMPLETO"
    ])
    with tab_exp:
        c1,c2,c3=st.columns(3)
        with c1:
            if st.session_state.dati:
                st.download_button(
                    'EXPORT VOLONTARI',
                    export_excel(pd.DataFrame(st.session_state.dati)),
                    file_name='Volontari.xlsx',
                    use_container_width=True,
                    key='exp_vol'
                )
            if st.session_state.post:
                st.download_button(
                    'EXPORT MAPPA',
                    export_excel(pd.DataFrame(st.session_state.post)),
                    file_name='Mappa.xlsx',
                    use_container_width=True,
                    key='exp_mappa'
                )
        with c2:
            if st.session_state.interventi_lista:
                st.download_button(
                    'EXPORT INTERVENTI',
                    export_excel(pd.DataFrame(st.session_state.interventi_lista)),
                    file_name='Interventi.xlsx',
                    use_container_width=True,
                    key='exp_int'
                )
            if st.session_state.check:
                st.download_button(
                    'EXPORT CHECK IN',
                    export_excel(pd.DataFrame(st.session_state.check)),
                    file_name='CheckIn.xlsx',
                    use_container_width=True,
                    key='exp_check'
                )
        with c3:
            if st.session_state.radio:
                st.download_button(
                    'EXPORT DB RADIO',
                    export_excel(pd.DataFrame(st.session_state.radio)),
                    file_name='DB_Radio.xlsx',
                    use_container_width=True,
                    key='exp_radio'
                )
            if st.session_state.cons:
                st.download_button(
                    'EXPORT CONSEGNA RADIO',
                    export_excel(pd.DataFrame(st.session_state.cons)),
                    file_name='Consegna_Radio.xlsx',
                    use_container_width=True,
                    key='exp_cons'
                )
    with tab_imp:
        c1,c2,c3=st.columns(3)
        with c1:
            up_vol=st.file_uploader('Import Volontari',type=['xlsx'],key='up_vol')
            if up_vol:
                df_up=pd.read_excel(up_vol)
                st.dataframe(df_up.head())
                if st.button(f'IMPORTA {len(df_up)} VOLONTARI',key='imp_vol',use_container_width=True,type="primary"):
                    for _,row in df_up.iterrows():
                        st.session_state.dati.append(row.to_dict())
                    save(FD,st.session_state.dati)
                    st.success("Importati!")
                    st.rerun()
            up_mappa=st.file_uploader('Import Mappa',type=['xlsx'],key='up_mappa')
            if up_mappa:
                df_up=pd.read_excel(up_mappa)
                if st.button(f'IMPORTA {len(df_up)} POSTAZIONI',key='imp_mappa',use_container_width=True,type="primary"):
                    for _,row in df_up.iterrows():
                        st.session_state.post.append(row.to_dict())
                    save(FP,st.session_state.post)
                    st.success("Importate!")
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
            up_check=st.file_uploader('Import Check In',type=['xlsx'],key='up_check')
            if up_check:
                df_up=pd.read_excel(up_check)
                if st.button(f'IMPORTA {len(df_up)} CHECK IN',key='imp_check',use_container_width=True,type="primary"):
                    for _,row in df_up.iterrows():
                        st.session_state.check.append(row.to_dict())
                    save(FC,st.session_state.check)
                    st.success("Importati!")
                    st.rerun()
        with c3:
            up_radio=st.file_uploader('Import DB Radio',type=['xlsx'],key='up_radio')
            if up_radio:
                df_up=pd.read_excel(up_radio)
                if st.button(f'IMPORTA {len(df_up)} RADIO',key='imp_radio',use_container_width=True,type="primary"):
                    for _,row in df_up.iterrows():
                        st.session_state.radio.append(row.to_dict())
                    save(FR,st.session_state.radio)
                    st.success("Importate!")
                    st.rerun()
    with tab_all:
        c1,c2=st.columns(2)
        with c1:
            if st.button('CREA BACKUP COMPLETO',type='primary',use_container_width=True):
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
                st.success('Backup creato!')
            if 'bk_all' in st.session_state:
                st.download_button('SCARICA BACKUP COMPLETO',st.session_state['bk_all'],file_name='BACKUP_COMPLETO.xlsx',use_container_width=True,type='primary')

# MENU
header()
with st.sidebar:
    st.markdown('**MENU COMPLETO**')
    opts=['Dashboard','Volontari','Mappa','Interventi Emergenza','Check In','DB Radio','Consegna Radio','Backup','Tesserino','Logout']
    sel=st.radio('Vai a',opts,index=0)
    if sel=='Logout':
        st.session_state.auth=False
        st.session_state.popup_shown=False
        st.rerun()
    st.session_state.menu=sel
    if st.button('MOSTRA POPUP INIZIALE',use_container_width=True):
        st.session_state.popup_shown=False
        st.rerun()

scelta=st.session_state.menu

if scelta=='Dashboard':
    st.markdown("## ANA Varese - Dashboard")
    c1,c2=st.columns(2)
    with c1:
        if st.button('VOLONTARI',use_container_width=True):
            st.session_state.menu='Volontari'
            st.rerun()
        if st.button('MAPPA',use_container_width=True):
            st.session_state.menu='Mappa'
            st.rerun()
        if st.button('INTERVENTI EMERGENZA',use_container_width=True):
            st.session_state.menu='Interventi Emergenza'
            st.rerun()
        if st.button('BACKUP IMPORT EXPORT',use_container_width=True,type="primary"):
            st.session_state.menu='Backup'
            st.rerun()
    with c2:
        if st.button('CHECK IN',use_container_width=True):
            st.session_state.menu='Check In'
            st.rerun()
        if st.button('DB RADIO',use_container_width=True):
            st.session_state.menu='DB Radio'
            st.rerun()
        if st.button('CONSEGNA RADIO',use_container_width=True):
            st.session_state.menu='Consegna Radio'
            st.rerun()
        if st.button('TESSERINO',use_container_width=True):
            st.session_state.menu='Tesserino'
            st.rerun()
    st.divider()
    c1,c2,c3,c4=st.columns(4)
    with c1: st.metric('Volontari',len(st.session_state.dati))
    with c2: st.metric('Postazioni',len(st.session_state.post))
    with c3: st.metric('Interventi',len(st.session_state.interventi_lista))
    with c4: st.metric('Radio',len(st.session_state.radio))
    st.divider()
    tab1, tab2, tab3 = st.tabs(["Da Anagrafica Esistente","Inserimento Manuale","INTERVENTI EMERGENZA"])
    with tab1:
        st.markdown("### Da Anagrafica Esistente")
        if st.session_state.dati:
            st.dataframe(pd.DataFrame(st.session_state.dati),use_container_width=True)
    with tab2:
        st.markdown("### Inserimento Manuale")
        with st.form("form_manuale"):
            nome = st.text_input("Nome e Cognome *")
            assoc = st.text_input("Associazione *")
            cell = st.text_input("Cellulare *")
            ruolo = st.selectbox("Ruolo *",["Volontario","Caposquadra","Coordinatore"])
            if st.form_submit_button("Salva"):
                if nome:
                    st.session_state.dati.append({"Nome": nome,"Associazione": assoc,"Cellulare": cell,"Ruolo": ruolo})
                    save(FD,st.session_state.dati)
                    st.success(f"Aggiunto {nome}")
                    st.rerun()
    with tab3:
        pagina_interventi_emergenza()

elif scelta=='Volontari':
    torna()
    st.markdown("## VOLONTARI - CON FOTO E SOTTO CARTELLE - RIPRISTINATO")
    # SOTTO CARTELLE PER VOLONTARI
    t1,t2,t3 = st.tabs(["Anagrafica Foto CF ODV","Elenco e Tesserino","Foto Volontari"])
    with t1:
        st.markdown("### Anagrafica con Foto, CF, ODV, Tessera")
        with st.form("form_vol_foto", clear_on_submit=True):
            c1,c2=st.columns(2)
            with c1:
                a1=st.text_input("Nome *")
                a2=st.text_input("Cognome *")
                a_cf=st.text_input("CF * per barcode tesserino")
                a_foto=st.file_uploader("Foto Volontario *",type=['jpg','png','jpeg'],key='foto_vol')
                if a_foto:
                    st.image(a_foto,width=150,caption="Anteprima foto")
            with c2:
                a_odv=st.selectbox("ODV",["A.N.A. Sezione di Varese","Protezione Civile Varese","ANA Varese","Croce Rossa","Alpini","Altro"])
                a_tess=st.text_input("Numero Tessera")
                a_tel=st.text_input("Cellulare")
                a_email=st.text_input("Email")
            salva_vol=st.form_submit_button("SALVA VOLONTARIO CON FOTO",use