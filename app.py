import streamlit as st
import pandas as pd
from io import BytesIO
import os, json, hashlib
from datetime import date

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
            with open(f,'r',encoding='utf-8') as ff:
                return json.load(ff)
    except:
        pass
    return d

def save(f,d):
    try:
        with open(f,'w',encoding='utf-8') as ff:
            json.dump(d,ff,indent=2)
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

def crea_tess(vol,foto_path,tmpl):
    try:
        if not HAS_PIL:
            return None
        if tmpl and os.path.exists(tmpl):
            base=Image.open(tmpl)
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
        odv=vol.get('ODV','ANA Varese')
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

# PRIMA PAGINA - SOLO TUA IMG PICCOLA 250px
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
                    st.success("TUA IMG PICCOLA 250px")
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

# LOGIN
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
    with st.form("form_emerg",clear_on_submit=True):
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
                "ODV *",
                ["ANA Varese","PC Lombardia",
                 "Croce Rossa","Altro"]
            )
        azione_int=st.text_area("Azione *",height=100)
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
                st.session_state.interventi_lista.append(nuovo)
                save(FE,st.session_state.interventi_lista)
                st.success("Salvato!")
                st.rerun()
    if st.session_state.interventi_lista:
        df=pd.DataFrame(st.session_state.interventi_lista)
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
                    'IMPORTA VOLONTARI',
                    key='imp_vol',
                    use_container_width=True,
                    type="primary"
                ):
                    for _,row in df_up.iterrows():
                        st.session_state.dati.append(
                            row.to_dict()
                        )
                    save(FD,st.session_state.dati)
                    st.success("Importati!")
                    st.rerun()
        with c2:
            up_int=st.file_uploader(
                'Import Interventi',
                type=['xlsx'],
                key='up_int'
            )
            if up_int:
                df_up=pd.read_excel(up_int)
                if st.button(
                    'IMPORTA INTERVENTI',
                    key='imp_int',
                    use_container_width=True,
                    type="primary"
                ):
                    for _,row in df_up.iterrows():
                        st.session_state.interventi_lista.append(
                            row.to_dict()
                        )
                    save(FE,st.session_state.interventi_lista)
                    st.success("Importati!")
                    st.rerun()
    with tab_all:
        if st.button(
            'CREA BACKUP COMPLETO',
            type='primary',
            use_container_width=True
        ):
            out=BytesIO()
            with pd.ExcelWriter(
                out,engine='openpyxl'
            ) as writer:
                if st.session_state.dati:
                    pd.DataFrame(
                        st.session_state.dati
                    ).to_excel(
                        writer,
                        sheet_name='Volontari',
                        index=False
                    )
                if st.session_state.post:
                    pd.DataFrame(
                        st.session_state.post
                    ).to_excel(
                        writer,
                        sheet_name='Mappa',
                        index=False
                    )
                if st.session_state.interventi_lista:
                    pd.DataFrame(
                        st.session_state.interventi_lista
                    ).to_excel(
                        writer,
                        sheet_name='Interventi',
                        index=False
                    )
            st.session_state['bk_all']=out.getvalue()
            st.success('Backup creato!')
        if 'bk_all' in st.session_state:
            st.download_button(
                'SCARICA BACKUP',
                st.session_state['bk_all'],
                file_name='BACKUP.xlsx',
                use_container_width=True,
                type='primary'
            )

# MENU
header()
with st.sidebar:
    st.markdown('**MENU COMPLETO**')
    opts=[
        'Dashboard','Volontari','Mappa',
        'Interventi Emergenza',
        'Check In','DB Radio',
        'Consegna Radio','Backup',
        'Tesserino','Logout'
    ]
    sel=st.radio('Vai a',opts,index=0)
    if sel=='Logout':
        st.session_state.auth=False
        st.session_state.popup_shown=False
        st.rerun()
    st.session_state.menu=sel

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
        if st.button('INTERVENTI',use_container_width=True):
            st.session_state.menu='Interventi Emergenza'
            st.rerun()
        if st.button('BACKUP',use_container_width=True,type="primary"):
            st.session_state.menu='Backup'
            st.rerun()
    with c2:
        if st.button('CHECK IN',use_container_width=True):
            st.session_state.menu='Check In'
            st.rerun()
        if st.button('DB RADIO',use_container_width=True):
            st.session_state.menu='DB Radio'
            st.rerun()
        if st.button('TESSERINO',use_container_width=True):
            st.session_state.menu='Tesserino'
            st.rerun()
    st.divider()
    c1,c2,c3,c4=st.columns(4)
    with c1:
        st.metric('Vol',len(st.session_state.dati))
    with c2:
        st.metric('Post',len(st.session_state.post))
    with c3:
        st.metric('Int',len(st.session_state.interventi_lista))
    with c4:
        st.metric('Radio',len(st.session_state.radio))

elif scelta=='Volontari':
    torna()
    st.markdown(
        "## VOLONTARI - TUTTE LE SOTTOMASCHERE"
    )
    # SOTTOMASCHERE COMPLETE
    t1,t2,t3,t4,t5,t6=st.tabs([
        "1.Anagrafica",
        "2.Contatti",
        "3.Foto e Documenti",
        "4.Formazione DPI",
        "5.Disponibilita",
        "6.Elenco Tesserino"
    ])
    with t1:
        st.markdown("### 1 - Anagrafica")
        with st.form("form_anag",clear_on_submit=True):
            c1,c2=st.columns(2)
            with c1:
                a_nome=st.text_input("Nome *")
                a_cogn=st.text_input("Cognome *")
                a_cf=st.text_input("CF *")
                a_nasc=st.date_input("Data nascita")
                a_comune_n=st.text_input("Comune nascita")
            with c2:
                a_ind=st.text_input("Indirizzo")
                a_comune=st.text_input("Comune residenza")
                a_cap=st.text_input("CAP")
                a_prov=st.text_input("Provincia")
                a_odv=st.selectbox(
                    "ODV",
                    ["A.N.A. Sezione di Varese",
                     "Protezione Civile Varese",
                     "ANA Varese","CRI","Altro"]
                )
            c1,c2=st.columns(2)
            with c1:
                a_tess=st.text_input("Tessera ANA")
                a_ruolo=st.selectbox(
                    "Ruolo",
                    ["Volontario","Caposquadra",
                     "Coordinatore","Autista",
                     "Radio","Logistica","Sanitario","Altro"]
                )
            with c2:
                a_data_is=st.date_input("Data iscrizione")
                a_note=st.text_area("Note")
            btn1=st.form_submit_button(
                "SALVA ANAGRAFICA",
                use_container_width=True,
                type="primary"
            )
            if btn1:
                if a_nome and a_cogn:
                    nc=f"{a_nome} {a_cogn}"
                    nuovo={
                        'Nome':nc,
                        'CF':a_cf,
                        'DataNascita':fmt_date(a_nasc),
                        'ComuneNascita':a_comune_n,
                        'Indirizzo':a_ind,
                        'Comune':a_comune,
                        'CAP':a_cap,
                        'Provincia':a_prov,
                        'ODV':a_odv,
                        'Tessera':a_tess,
                        'Ruolo':a_ruolo,
                        'DataIscrizione':fmt_date(a_data_is),
                        'Note':a_note,
                        'FotoFile':''
                    }
                    found=False
                    for i,d in enumerate(st.session_state.dati):
                        if d.get('Nome','')==nc:
                            # mantieni foto
                            nuovo['FotoFile']=d.get('FotoFile','')
                            # mantieni altri campi
                            for k in ['Telefono','Email','DocFile','Formazione','DPI','Disponibilita']:
                                if k in d:
                                    nuovo[k]=d[k]
                            st.session_state.dati[i].update(nuovo)
                            found=True
                    if not found:
                        st.session_state.dati.append(nuovo)
                    save(FD,st.session_state.dati)
                    st.success(f"Salvata anagrafica {nc}!")
                    st.rerun()
    with t2:
        st.markdown("### 2 - Contatti")
        vol_list=[
            d.get('Nome','')
            for d in st.session_state.dati
        ]
        if vol_list:
            sel=st.selectbox(
                "Seleziona volontario",
                vol_list,
                key='cont_sel'
            )
            vol_data={}
            idx_sel=-1
            for i,d in enumerate(st.session_state.dati):
                if d.get('Nome','')==sel:
                    vol_data=d
                    idx_sel=i
                    break
            with st.form("form_cont"):
                c1,c2=st.columns(2)
                with c1:
                    tel=st.text_input(
                        "Cellulare",
                        value=vol_data.get('Telefono','')
                    )
                    tel2=st.text_input(
                        "Altro telefono",
                        value=vol_data.get('Telefono2','')
                    )
                    email=st.text_input(
                        "Email",
                        value=vol_data.get('Email','')
                    )
                with c2:
                    email2=st.text_input(
                        "Email 2",
                        value=vol_data.get('Email2','')
                    )
                    contatto_em=st.text_input(
                        "Contatto emergenza",
                        value=vol_data.get('ContattoEmergenza','')
                    )
                    tel_em=st.text_input(
                        "Tel emergenza",
                        value=vol_data.get('TelEmergenza','')
                    )
                btn2=st.form_submit_button(
                    "SALVA CONTATTI",
                    use_container_width=True,
                    type="primary"
                )
                if btn2:
                    st.session_state.dati[idx_sel]['Telefono']=tel
                    st.session_state.dati[idx_sel]['Telefono2']=tel2
                    st.session_state.dati[idx_sel]['Email']=email
                    st.session_state.dati[idx_sel]['Email2']=email2
                    st.session_state.dati[idx_sel]['ContattoEmergenza']=contatto_em
                    st.session_state.dati[idx_sel]['TelEmergenza']=tel_em
                    save(FD,st.session_state.dati)
                    st.success("Contatti salvati!")
                    st.rerun()
        else:
            st.warning("Nessun volontario")
    with t3:
        st.markdown("### 3 - Foto e Documenti")
        vol_list=[
            d.get('Nome','')
            for d in st.session_state.dati
        ]
        if vol_list:
            sel=st.selectbox(
                "Seleziona volontario",
                vol_list,
                key='foto_sel'
            )
            vol_data={}
            idx_sel=-1
            for i,d in enumerate(st.session_state.dati):
                if d.get('Nome','')==sel:
                    vol_data=d
                    idx_sel=i
                    break
            c1,c2=st.columns([1,2])
            with c1:
                fp=vol_data.get('FotoFile','')
                if fp and os.path.exists(fp):
                    st.image(fp,width=150,caption="Foto attuale")
                else:
                    st.warning("Nessuna foto")
                a_foto=st.file_uploader(
                    "Carica foto",
                    type=['jpg','png','jpeg'],
                    key='foto_vol'
                )
                if a_foto:
                    st.image(a_foto,width=150,caption="Anteprima")
                a_doc=st.file_uploader(
                    "Carica documento CI",
                    type=['jpg','png','pdf'],
                    key='doc_vol'
                )
            with c2:
                with st.form("form_foto"):
                    st.write(f"Volontario: {sel}")
                    btn3=st.form_submit_button(
                        "SALVA FOTO E DOC",
                        use_container_width=True,
                        type="primary"
                    )
                    if btn3:
                        if a_foto:
                            try:
                                os.makedirs(
                                    'foto_volontari',
                                    exist_ok=True
                                )
                                fp_new=f"foto_volontari/{sel.replace(' ','_')}_{a_foto.name}"
                                with open(fp_new,'wb') as f:
                                    f.write(a_foto.getbuffer())
                                st.session_state.dati[idx_sel]['FotoFile']=fp_new
                            except:
                                pass
                        if a_doc:
                            try:
                                os.makedirs(
                                    'foto_volontari',
                                    exist_ok=True
                                )
                                fd_new=f"foto_volontari/DOC_{sel.replace(' ','_')}_{a_doc.name}"
                                with open(fd_new,'wb') as f:
                                    f.write(a_doc.getbuffer())
                                st.session_state.dati[idx_sel]['DocFile']=fd_new
                            except:
                                pass
                        save(FD,st.session_state.dati)
                        st.success("Foto e doc salvati!")
                        st.rerun()
                df_doc=vol_data.get('DocFile','')
                if df_doc and os.path.exists(df_doc):
                    st.success(f"Doc: {df_doc}")
        else:
            st.warning("Nessun volontario")
    with t4:
        st.markdown("### 4 - Formazione e DPI")
        vol_list=[
            d.get('Nome','')
            for d in st.session_state.dati
        ]
        if vol_list:
            sel=st.selectbox(
                "Seleziona volontario",
                vol_list,
                key='form_sel'
            )
            idx_sel=-1
            for i,d in enumerate(st.session_state.dati):
                if d.get('Nome','')==sel:
                    idx_sel=i
                    break
            with st.form("form_formazione"):
                c1,c2=st.columns(2)
                with c1:
                    corso_base=st.checkbox("Corso base PC")
                    corso_antis=st.checkbox("Corso antincendio")
                    corso_ps=st.checkbox("Primo soccorso")
                    corso_radio=st.checkbox("Corso radio")
                    patente=st.text_input("Patenti")
                with c2:
                    dpi_scarpe=st.checkbox("Scarpe antinf.")
                    dpi_casco=st.checkbox("Casco")
                    dpi_gilet=st.checkbox("Gilet alta visib.")
                    dpi_guanti=st.checkbox("Guanti")
                    taglia=st.text_input("Taglia vestiario")
                note_form=st.text_area("Note formazione")
                btn4=st.form_submit_button(
                    "SALVA FORMAZIONE DPI",
                    use_container_width=True,
                    type="primary"
                )
                if btn4:
                    st.session_state.dati[idx_sel]['Formazione']={
                        'Base':corso_base,
                        'Antincendio':corso_antis,
                        'PrimoSoccorso':corso_ps,
                        'Radio':corso_radio,
                        'Patenti':patente
                    }
                    st.session_state.dati[idx_sel]['DPI']={
                        'Scarpe':dpi_scarpe,
                        'Casco':dpi_casco,
                        'Gilet':dpi_gilet,
                        'Guanti':dpi_guanti,
                        'Taglia':taglia,
                        'Note':note_form
                    }
                    save(FD,st.session_state.dati)
                    st.success("Formazione DPI salvati!")
                    st.rerun()
        else:
            st.warning("Nessun volontario")
    with t5:
        st.markdown("### 5 - Disponibilita")
        vol_list=[
            d.get('Nome','')
            for d in st.session_state.dati
        ]
        if vol_list:
            sel=st.selectbox(
                "Seleziona volontario",
                vol_list,
                key='disp_sel'
            )
            idx_sel=-1
            for i,d in enumerate(st.session_state.dati):
                if d.get('Nome','')==sel:
                    idx_sel=i
                    break
            with st.form("form_disp"):
                c1,c2=st.columns(2)
                with c1:
                    lun=st.checkbox("Lunedi")
                    mar=st.checkbox("Martedi")
                    mer=st.checkbox("Mercoledi")
                    gio=st.checkbox("Giovedi")
                    ven=st.checkbox("Venerdi")
                with c2:
                    sab=st.checkbox("Sabato")
                    dom=st.checkbox("Domenica")
                    mattina=st.checkbox("Mattina")
                    pomeriggio=st.checkbox("Pomeriggio")
                    sera=st.checkbox("Sera/notte")
                note_disp=st.text_area("Note disponibilita")
                btn5=st.form_submit_button(
                    "SALVA DISPONIBILITA",
                    use_container_width=True,
                    type="primary"
                )
                if btn5:
                    st.session_state.dati[idx_sel]['Disponibilita']={
                        'Lun':lun,'Mar':mar,'Mer':mer,
                        'Gio':gio,'Ven':ven,
                        'Sab':sab,'Dom':dom,
                        'Mattina':mattina,
                        'Pomeriggio':pomeriggio,
                        'Sera':sera,
                        'Note':note_disp
                    }
                    save(FD,st.session_state.dati)
                    st.success("Disponibilita salvata!")
                    st.rerun()
        else:
            st.warning("Nessun volontario")
    with t6:
        st.markdown("### 6 - Elenco e Tesserino")
        if st.session_state.dati:
            df=pd.DataFrame(st.session_state.dati)
            st.dataframe(df,use_container_width=True)
            st.divider()
            vol_list=[
                d.get('Nome','')
                for d in st.session_state.dati
            ]
            sel=st.selectbox(
                "Seleziona per tesserino",
                vol_list,
                key='tess_sel'
            )
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
                st.write(f"Tessera: {vol_data.get('Tessera','')}")
            with c2:
                tess=crea_tess(
                    vol_data,
                    vol_data.get('FotoFile',''),
                    "Tesserino-Ezio.JPG" if os.path.exists("Tesserino-Ezio.JPG") else None
                )
                if tess:
                    st.image(tess,use_container_width=True)
                    st.download_button(
                        'SCARICA TESSERINO',
                        tess,
                        file_name=f"Tesserino_{sel}.png",
                        mime='image/png',
                        type='primary',
                        use_container_width=True
                    )
                if os.path.exists("Tesserino-Ezio.JPG"):
                    st.image(
                        "Tesserino-Ezio.JPG",
                        caption="Template",
                        use_container_width=True
                    )
        else:
            st.warning("Nessun volontario")

elif scelta=='Backup':
    torna()
    pagina_backup()

elif scelta=='Interventi Emergenza':
    torna()
    pagina_interventi()

elif scelta=='Tesserino':
    torna()
    st.markdown("### TESSERINO REGIONALE")
    vol_list=[
        d.get('Nome','')
        for d in st.session_state.dati
    ]
    if vol_list:
        sel=st.selectbox(
            "Volontario",
            vol_list,
            key='tess_final'
        )
        vol_data={}
        for d in st.session_state.dati:
            if d.get('Nome','')==sel:
                vol_data=d
                break
        tess=crea_tess(
            vol_data,
            vol_data.get('FotoFile',''),
            "Tesserino-Ezio.JPG" if os.path.exists("Tesserino-Ezio.JPG") else None
        )
        if tess:
            st.image(tess,use_container_width=True)
            st.download_button(
                'SCARICA TESSERINO',
                tess,
                file_name=f"Tesserino_{sel}.png",
                mime='image/png',
                type='primary'
            )

else:
    torna()
    st.markdown(f"### {scelta}")
    st.info(f"Form {scelta} - OK")