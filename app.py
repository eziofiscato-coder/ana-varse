import streamlit as st
import pandas as pd
from io import BytesIO
import os, json, hashlib

try:
    import folium
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

st.markdown("""
<style>
.stApp{background:#e8f5e9!important}
.stForm{background:#f1f8e9!important;
 border:2px solid #81c784!important;
 border-radius:12px!important;
 padding:10px!important}
.stButton>button{
 background:#d32f2f!important;
 color:white!important;
 font-weight:bold!important}
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
    w=pd.ExcelWriter(out,engine='openpyxl')
    df.to_excel(w,index=False)
    w.close()
    return out.getvalue()

def bcode(cf):
    try:
        import barcode
        from barcode.writer import ImageWriter
        t=(cf or "0"*16)[:16].upper()
        cd=barcode.get('code128',t,writer=ImageWriter())
        buf=BytesIO()
        cd.write(buf)
        buf.seek(0)
        return buf.getvalue()
    except:
        return None

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
        fx=int(W*0.02)
        fy=int(H*0.18)
        fw=int(W*0.26)
        fh=int(H*0.58)
        if foto and os.path.exists(foto):
            try:
                im=Image.open(foto).convert("RGB")
                im=im.resize((fw,fh),Image.LANCZOS)
                tess.paste(im,(fx,fy))
            except:
                pass
        nx=int(W*0.34)
        ny=int(H*0.32)
        dr.rectangle([nx,ny,nx+int(W*0.5),ny+25],fill='white')
        dr.text((nx,ny),vol.get('Nome','').upper(),fill='black',font=fb)
        odv=vol.get('ODV','ANA Varese')
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
        bc=bcode(cf)
        if bc:
            try:
                bi=Image.open(BytesIO(bc)).convert("RGB")
                bi=bi.resize((bw,bh),Image.LANCZOS)
                tess.paste(bi,(bx,by))
            except:
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
    ('dati',[]),
    ('post',[]),
    ('icone',[]),
    ('emerg',[]),
    ('check',[]),
    ('radio',[]),
    ('cons',[]),
    ('eventi',[]),
    ('interv',[]),
    ('menu','Dashboard'),
    ('auth',False),
    ('popup',False),
    ('edit_idx',-1),
    ('edit_map',-1),
    ('sel_lat','45.8205'),
    ('sel_lon','8.8250')
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

uts=load_json(FU,[])
if not uts:
    uts=[{'username':'admin','password':hpwd('ana2024')}]
    save_json(FU,uts)

def hdr():
    a,b=st.columns([1,5])
    with a:
        try:
            st.image("logo.png",width=110)
        except:
            st.write("ANA")
    with b:
        st.markdown(
            "<div style='background:#0e7a3d;"
            "padding:12px;border-radius:8px;"
            "text-align:center;'>"
            "<b style='color:white;font-size:18px;'>"
            "A.N.A. NUCLEO VOLONTARI DI PROTEZIONE CIVILE<br>"
            "SEZIONE DI VARESE</b></div>",
            unsafe_allow_html=True
        )

def to_dash():
    if st.button('TORNA ALLA DASHBOARD'):
        st.session_state.menu='Dashboard'
        st.rerun()

if not st.session_state.popup:
    hdr()
    st.markdown(
        "<h3 style='text-align:center;color:#0e7a3d;'>"
        "Ciao Ragazzi, Buon Lavoro!</h3>",
        unsafe_allow_html=True
    )
    st.divider()
    c1,c2,c3=st.columns([1,1,1])
    with c2:
        if os.path.exists('copertina.jpg'):
            try:
                st.image('copertina.jpg',width=250)
            except:
                pass
        if st.button("ENTRA NEL SISTEMA"):
            st.session_state.popup=True
            st.rerun()
    st.stop()

if not st.session_state.auth:
    hdr()
    c1,c2,c3=st.columns([1,2,1])
    with c2:
        st.markdown("### LOGIN")
        with st.form('login'):
            u=st.text_input('Username',value='admin')
            p=st.text_input('Password',type='password',value='ana2024')
            ok=st.form_submit_button('ACCEDI')
            if ok:
                ph=hpwd(p)
                for ut in uts:
                    if ut['username']==u and ut['password']==ph:
                        st.session_state.auth=True
                        st.session_state.menu='Dashboard'
                        st.session_state.popup=True
                        st.rerun()
                st.error('Credenziali errate')
    st.stop()

hdr()

with st.sidebar:
    st.markdown('**MENU COMPLETO**')
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
        'Backup',
        'Tesserino',
        'Logout'
    ]
    sel=st.radio('Seleziona',opts,index=0)
    if sel=='Logout':
        st.session_state.auth=False
        st.session_state.popup=False
        st.rerun()
    st.session_state.menu=sel

sc=st.session_state.menu

if sc=='Dashboard':
    st.markdown("## Dashboard")
    st.markdown("### A.N.A. NUCLEO VOLONTARI DI PROTEZIONE CIVILE SEZIONE DI VARESE")
    a,b=st.columns(2)
    with a:
        if st.button('VOLONTARI'):
            st.session_state.menu='Volontari'
            st.rerun()
        if st.button('MAPPA POSTAZIONI'):
            st.session_state.menu='Mappa'
            st.rerun()
        if st.button('LIBRERIA ICONE'):
            st.session_state.menu='Libreria Icone'
            st.rerun()
        if st.button('BACKUP'):
            st.session_state.menu='Backup'
            st.rerun()
    with b:
        if st.button('INTERVENTI EMERGENZA'):
            st.session_state.menu='Interventi Emergenza'
            st.rerun()
        if st.button('EVENTI'):
            st.session_state.menu='Eventi'
            st.rerun()
        if st.button('DB RADIO'):
            st.session_state.menu='DB Radio'
            st.rerun()
        if st.button('TESSERINO NITIDO'):
            st.session_state.menu='Tesserino'
            st.rerun()
    st.divider()
    c1,c2,c3,c4,c5=st.columns(5)
    with c1:
        st.metric('Volontari',len(st.session_state.dati))
    with c2:
        st.metric('Postazioni',len(st.session_state.post))
    with c3:
        st.metric('Icone',len(st.session_state.icone))
    with c4:
        st.metric('Interventi',len(st.session_state.interv))
    with c5:
        st.metric('Eventi',len(st.session_state.eventi))

elif sc=='Volontari':
    to_dash()
    st.markdown("## VOLONTARI")
    st.markdown("### Maschera Anagrafica Completa")
    if st.session_state.edit_idx >=0:
        if st.session_state.edit_idx < len(st.session_state.dati):
            vol=st.session_state.dati[st.session_state.edit_idx]
            st.success(f"Selezionato: {vol.get('Nome','')}")
            st.markdown("### MASCHERA AGGIORNAMENTO")
            with st.form("edit_vol"):
                c1,c2=st.columns(2)
                with c1:
                    e_nome=st.text_input("Nome e Cognome",value=vol.get('Nome',''))
                    e_cf=st.text_input("Codice Fiscale",value=vol.get('CF',''))
                    e_ind=st.text_input("Indirizzo",value=vol.get('Indirizzo',''))
                    e_com=st.text_input("Comune",value=vol.get('Comune',''))
                    e_tel=st.text_input("Telefono",value=vol.get('Telefono',''))
                with c2:
                    e_odv=st.text_input("ODV",value=vol.get('ODV',''))
                    e_tess=st.text_input("Tessera",value=vol.get('Tessera',''))
                    e_ruolo=st.selectbox("Ruolo",['Volontario','Caposquadra','Coordinatore','Autista','Radio','Altro'])
                    e_mail=st.text_input("Email",value=vol.get('Email',''))
                b1,b2,b3=st.columns(3)
                with b1:
                    bs=st.form_submit_button("SALVA AGGIORNAMENTI")
                with b2:
                    ba=st.form_submit_button("ANNULLA")
                with b3:
                    bd=st.form_submit_button("ELIMINA VOLONTARIO")
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
            st.divider()
    with st.expander("NUOVO VOLONTARIO - MASCHERA 1"):
        with st.form("anag",clear_on_submit=True):
            c1,c2=st.columns(2)
            with c1:
                a_nome=st.text_input("Nome *")
                a_cogn=st.text_input("Cognome *")
                a_cf=st.text_input("CF *")
            with c2:
                a_ind=st.text_input("Indirizzo")
                a_odv=st.selectbox("ODV",['A.N.A. Sezione Varese','PC Varese','CRI','Altro'])
                a_tess=st.text_input("Tessera")
            a_ruolo=st.selectbox("Ruolo",['Volontario','Caposquadra','Coordinatore','Autista','Radio','Altro'])
            b1=st.form_submit_button("SALVA NUOVO VOLONTARIO")
            if b1:
                if a_nome and a_cogn:
                    nc=f"{a_nome} {a_cogn}"
                    nuovo={'Nome':nc,'CF':a_cf,'Indirizzo':a_ind,'ODV':a_odv,'Tessera':a_tess,'Ruolo':a_ruolo,'FotoFile':''}
                    st.session_state.dati.append(nuovo)
                    save_json(FD,st.session_state.dati)
                    st.success(f"Salvato {nc}")
                    st.rerun()
    if st.session_state.dati:
        df=pd.DataFrame(st.session_state.dati)
        st.markdown("### Elenco - Clicca riga per maschera aggiornamento")
        ev=st.dataframe(df,hide_index=False,on_select="rerun",selection_mode="single-row",key='tab_vol')
        if ev and ev.selection and ev.selection.rows:
            st.session_state.edit_idx=ev.selection.rows[0]
            st.rerun()

elif sc=='Mappa':
    to_dash()
    st.markdown("## MAPPA POSTAZIONI")
    st.markdown("### Mappa sopra - Maschera sotto - Selezione icona")
    if HAS_MAP:
        try:
            mm=folium.Map(location=[45.8205,8.8250],zoom_start=12)
            for p in st.session_state.post:
                try:
                    lat=p.get('Lat','45.8205')
                    lon=p.get('Lon','8.8250')
                    tp=p.get('Tipo','')
                    col='green'
                    if tp=='COC':
                        col='red'
                    elif tp=='Campo base':
                        col='blue'
                    la=float(lat)
                    lo=float(lon)
                    folium.Marker([la,lo],popup=f"{p.get('Nome','')} - {p.get('Icona','')}",icon=folium.Icon(color=col)).add_to(mm)
                except:
                    pass
            mp=st_folium(mm,width=1100,height=400)
            if mp and mp.get('last_clicked'):
                st.session_state.sel_lat=str(mp['last_clicked']['lat'])
                st.session_state.sel_lon=str(mp['last_clicked']['lng'])
                st.success("Posizione selezionata - scegli icona sotto")
        except Exception as e:
            st.error(f"Errore mappa: {e}")
    st.divider()
    st.markdown("### Maschera sotto - Con riferimenti e icona")
    if st.session_state.edit_map >=0:
        if st.session_state.edit_map < len(st.session_state.post):
            p=st.session_state.post[st.session_state.edit_map]
            st.success(f"Modifica postazione: {p.get('Nome','')}")
            with st.form("edit_map"):
                c1,c2,c3=st.columns(3)
                with c1:
                    e_nome=st.text_input("Nome postazione",value=p.get('Nome',''))
                    e_com=st.text_input("Comune",value=p.get('Comune',''))
                    e_via=st.text_input("Via",value=p.get('Via',''))
                with c2:
                    e_lat=st.text_input("Latitudine",value=p.get('Lat','45.8205'))
                    e_lon=st.text_input("Longitudine",value=p.get('Lon','8.8250'))
                    e_tipo=st.selectbox("Tipo",['COC','Campo base','Magazzino','Sede','Punto ritrovo','Altro'])
                    lst=['Default','COC','Campo','Magazzino','Sede']
                    if st.session_state.icone:
                        lst=[]
                        for it in st.session_state.icone:
                            lst.append(it.get('Nome','Default'))
                    e_icon=st.selectbox("Scegli icona per posizione",lst)
                with c3:
                    e_r1=st.text_input("Rif Coordinatore",value=p.get('Rif1',''))
                    e_r2=st.text_input("Rif Telefono",value=p.get('Rif2',''))
                    e_note=st.text_area("Note postazione",value=p.get('Note',''))
                b1,b2=st.columns(2)
                with b1:
                    bs=st.form_submit_button("SALVA MODIFICHE")
                with b2:
                    bd=st.form_submit_button("ELIMINA POSTAZIONE")
                if bs:
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
                if bd:
                    st.session_state.post.pop(st.session_state.edit_map)
                    save_json(FP,st.session_state.post)
                    st.session_state.edit_map=-1
                    st.rerun()
            if st.button("ANNULLA MODIFICA"):
                st.session_state.edit_map=-1
                st.rerun()
    else:
        with st.form("mapa",clear_on_submit=True):
            c1,c2,c3=st.columns(3)
            with c1:
                m_nome=st.text_input("Nome postazione *")
                m_com=st.text_input("Comune *")
                m_via=st.text_input("Via")
            with c2:
                m_lat=st.text_input("Latitudine",value=st.session_state.sel_lat)
                m_lon=st.text_input("Longitudine",value=st.session_state.sel_lon)
                m_tipo=st.selectbox("Tipo postazione",['COC','Campo base','Magazzino','Sede','Punto ritrovo','Altro'])
                lst=['Default','COC','Campo','Magazzino','Sede','Mezzo']
                if st.session_state.icone:
                    lst=[]
                    for it in st.session_state.icone:
                        lst.append(it.get('Nome','Default'))
                m_icon=st.selectbox("Scegli icona per posizione selezionata",lst)
            with c3:
                m_r1=st.text_input("Riferimento 1 Coordinatore")
                m_r2=st.text_input("Riferimento 2 Telefono")
                m_note=st.text_area("Note postazione")
            bm=st.form_submit_button("SALVA POSTAZIONE CON ICONA")
            if bm:
                if m_nome and m_com:
                    nuovo={'Nome':m_nome,'Comune':m_com,'Via':m_via,'Lat':m_lat,'Lon':m_lon,'Tipo':m_tipo,'Icona':m_icon,'Rif1':m_r1,'Rif2':m_r2,'Note':m_note}
                    st.session_state.post.append(nuovo)
                    save_json(FP,st.session_state.post)
                    st.success(f"Salvata {m_nome} con icona {m_icon}")
                    st.rerun()
    if st.session_state.post:
        st.divider()
        st.markdown("### Anteprima postazioni con tutte le impostazioni")
        df=pd.DataFrame(st.session_state.post)
        st.dataframe(df)
        ev=st.dataframe(df,hide_index=False,on_select="rerun",selection_mode="single-row",key='tab_mapa')
        if ev and ev.selection and ev.selection.rows:
            st.session_state.edit_map=ev.selection.rows[0]
            st.rerun()

elif sc=='Libreria Icone':
    to_dash()
    st.markdown("## LIBRERIA ICONE")
    st.markdown("### Maschera icone per mappa")
    c1,c2=st.columns([1,1])
    with c1:
        with st.form("icone",clear_on_submit=True):
            i_nome=st.text_input("Nome icona *")
            i_cat=st.selectbox("Categoria",['COC','Campo base','Magazzino','Sede','Mezzo','Volontario','Altro'])
            i_file=st.file_uploader("Carica icona file",type=['png','jpg','jpeg','svg'])
            i_desc=st.text_area("Descrizione icona")
            bi=st.form_submit_button("SALVA ICONA")
            if bi:
                if i_nome:
                    fp=""
                    if i_file:
                        try:
                            os.makedirs('icone',exist_ok=True)
                            fp=f"icone/{i_nome}_{i_file.name}"
                            fout=open(fp,'wb')
                            fout.write(i_file.getbuffer())
                            fout.close()
                        except:
                            pass
                    nuovo={'Nome':i_nome,'Categoria':i_cat,'File':fp,'Descrizione':i_desc}
                    st.session_state.icone.append(nuovo)
                    save_json(FI,st.session_state.icone)
                    st.success(f"Icona {i_nome} salvata - ora in mappa")
                    st.rerun()
    with c2:
        if st.session_state.icone:
            df=pd.DataFrame(st.session_state.icone)
            st.dataframe(df)
            st.markdown("### Anteprima icone salvate")
            for ic in st.session_state.icone[-5:]:
                fp=ic.get('File','')
                if fp and os.path.exists(fp):
                    st.image(fp,width=60,caption=ic.get('Nome',''))

elif sc=='Interventi Emergenza':
    to_dash()
    st.markdown("## INTERVENTI EMERGENZA")
    st.markdown("### Maschera intervento completa")
    with st.form("emerg",clear_on_submit=True):
        c1,c2,c3=st.columns(3)
        with c1:
            d_int=st.date_input("Data intervento *")
            o_int=st.time_input("Ora intervento *")
        with c2:
            com_int=st.text_input("Comune *")
            via_int=st.text_input("Via *")
        with c3:
            civ_int=st.text_input("Civico")
            odv_int=st.selectbox("ODV",['A.N.A. Sezione Varese','PC Lombardia','CRI','Altro'])
        az_int=st.text_area("Azione svolta *",height=100)
        sv=st.form_submit_button("SALVA INTERVENTO")
        if sv:
            if com_int and via_int and az_int:
                nuovo={"Data":str(d_int),"Ora":str(o_int),"Comune":com_int,"Via":via_int,"Civico":civ_int,"ODV":odv_int,"Azione":az_int}
                st.session_state.interv.append(nuovo)
                save_json(FE,st.session_state.interv)
                st.success("Intervento salvato")
                st.rerun()
    if st.session_state.interv:
        df=pd.DataFrame(st.session_state.interv)
        st.dataframe(df)

elif sc=='Eventi':
    to_dash()
    st.markdown("## EVENTI")
    st.markdown("### Maschera eventi")
    with st.form("eventi",clear_on_submit=True):
        c1,c2=st.columns(2)
        with c1:
            ev_nome=st.text_input("Nome evento *")
            ev_data=st.date_input("Data evento")
            ev_com=st.text_input("Comune evento")
        with c2:
            ev_luogo=st.text_input("Luogo evento")
            ev_tipo=st.selectbox("Tipo evento",['Esercitazione','Intervento','Formazione','Riunione','Altro'])
            ev_resp=st.text_input("Responsabile")
        ev_desc=st.text_area("Descrizione evento")
        be=st.form_submit_button("SALVA EVENTO")
        if be:
            if ev_nome:
                nuovo={'Nome':ev_nome,'Data':str(ev_data),'Comune':ev_com,'Luogo':ev_luogo,'Tipo':ev_tipo,'Responsabile':ev_resp,'Descrizione':ev_desc}
                st.session_state.eventi.append(nuovo)
                save_json(FEV,st.session_state.eventi)
                st.success("Evento salvato")
                st.rerun()
    if st.session_state.eventi:
        df=pd.DataFrame(st.session_state.eventi)
        st.dataframe(df)

elif sc=='Check In':
    to_dash()
    st.markdown("## CHECK IN VOLONTARI")
    vlist=[d.get('Nome','') for d in st.session_state.dati]
    if vlist:
        with st.form("check",clear_on_submit=True):
            sel=st.selectbox("Seleziona volontario",vlist)
            d_check=st.date_input("Data check in")
            o_check=st.time_input("Ora check in")
            bc=st.form_submit_button("SALVA CHECK IN")
            if bc:
                nuovo={'Volontario':sel,'Data':str(d_check),'Ora':str(o_check)}
                st.session_state.check.append(nuovo)
                save_json(FC,st.session_state.check)
                st.success("Check in salvato")
                st.rerun()
    if st.session_state.check:
        df=pd.DataFrame(st.session_state.check)
        st.dataframe(df)

elif sc=='DB Radio':
    to_dash()
    st.markdown("## DB RADIO")
    st.markdown("### Maschera radio")
    with st.form("radio",clear_on_submit=True):
        c1,c2=st.columns(2)
        with c1:
            r_mod=st.text_input("Modello radio *")
            r_mat=st.text_input("Matricola *")
        with c2:
            r_freq=st.text_input("Frequenza")
            r_stato=st.selectbox("Stato radio",['Disponibile','In uso','Guasta','In riparazione'])
        br=st.form_submit_button("SALVA RADIO")
        if br:
            if r_mod and r_mat:
                nuovo={'Modello':r_mod,'Matricola':r_mat,'Frequenza':r_freq,'Stato':r_stato}
                st.session_state.radio.append(nuovo)
                save_json(FR,st.session_state.radio)
                st.success("Radio salvata")
                st.rerun()
    if st.session_state.radio:
        df=pd.DataFrame(st.session_state.radio)
        st.dataframe(df)

elif sc=='Consegna Radio':
    to_dash()
    st.markdown("## CONSEGNA RADIO")
    st.markdown("### Maschera consegna")
    vlist=[d.get('Nome','') for d in st.session_state.dati]
    rlist=[r.get('Matricola','') for r in st.session_state.radio]
    if vlist and rlist:
        with st.form("cons",clear_on_submit=True):
            s_vol=st.selectbox("Seleziona volontario",vlist)
            s_rad=st.selectbox("Seleziona radio",rlist)
            d_cons=st.date_input("Data consegna")
            b_cons=st.form_submit_button("SALVA CONSEGNA RADIO")
            if b_cons:
                nuovo={'Volontario':s_vol,'Radio':s_rad,'Data':str(d_cons)}
                st.session_state.cons.append(nuovo)
                save_json(FR2,st.session_state.cons)
                st.success("Consegna salvata")
                st.rerun()
    if st.session_state.cons:
        df=pd.DataFrame(st.session_state.cons)
        st.dataframe(df)

elif sc=='Backup':
    to_dash()
    st.markdown("## BACKUP E RIPRISTINO")
    st.markdown("### Export import con selezione form")
    t1,t2,t3=st.tabs(["EXPORT SELEZIONE","IMPORT SELEZIONE","BACKUP COMPLETO"])
    with t1:
        st.markdown("#### Seleziona form da esportare")
        c1,c2,c3=st.columns(3)
        with c1:
            ev=st.checkbox("Volontari",value=True,key='ev')
            ep=st.checkbox("Mappa postazioni",value=True,key='ep')
            ei=st.checkbox("Libreria icone",value=True,key='ei')
        with c2:
            e_int=st.checkbox("Interventi emergenza",value=True,key='eint')
            e_ev=st.checkbox("Eventi",value=True,key='eev')
            e_ch=st.checkbox("Check in",value=True,key='ech')
        with c3:
            e_ra=st.checkbox("DB Radio",value=True,key='era')
            e_co=st.checkbox("Consegna radio",value=True,key='eco')
        st.divider()
        if ev and st.session_state.dati:
            st.download_button('SCARICA VOLONTARI',exp_excel(pd.DataFrame(st.session_state.dati)),file_name='Volontari.xlsx',key='exv')
        if ep and st.session_state.post:
            st.download_button('SCARICA MAPPA',exp_excel(pd.DataFrame(st.session_state.post)),file_name='Mappa.xlsx',key='exm')
        if ei and st.session_state.icone:
            st.download_button('SCARICA ICONE',exp_excel(pd.DataFrame(st.session_state.icone)),file_name='Icone.xlsx',key='exi')
        if e_int and st.session_state.interv:
            st.download_button('SCARICA INTERVENTI',exp_excel(pd.DataFrame(st.session_state.interv)),file_name='Interventi.xlsx',key='exint')
        if e_ev and st.session_state.eventi:
            st.download_button('SCARICA EVENTI',exp_excel(pd.DataFrame(st.session_state.eventi)),file_name='Eventi.xlsx',key='exev')
        if e_ch and st.session_state.check:
            st.download_button('SCARICA CHECK IN',exp_excel(pd.DataFrame(st.session_state.check)),file_name='CheckIn.xlsx',key='exch')
        if e_ra and st.session_state.radio:
            st.download_button('SCARICA RADIO',exp_excel(pd.DataFrame(st.session_state.radio)),file_name='Radio.xlsx',key='exra')
        if e_co and st.session_state.cons:
            st.download_button('SCARICA CONSEGNA',exp_excel(pd.DataFrame(st.session_state.cons)),file_name='Consegna.xlsx',key='exco')
    with t2:
        st.markdown("#### Import selezione form")
        c1,c2=st.columns(2)
        with c1:
            up_v=st.file_uploader('Import Volontari',type=['xlsx'],key='upv')
            if up_v:
                df_up=pd.read_excel(up_v)
                if st.button(f'IMPORTA {len(df_up)} VOLONTARI',key='imv'):
                    for _,r in df_up.iterrows():
                        st.session_state.dati.append(r.to_dict())
                    save_json(FD,st.session_state.dati)
                    st.success("Volontari importati")
                    st.rerun()
            up_p=st.file_uploader('Import Mappa postazioni',type=['xlsx'],key='upp')
            if up_p:
                df_up=pd.read_excel(up_p)
                if st.button(f'IMPORTA {len(df_up)} POSTAZIONI',key='imp'):
                    for _,r in df_up.iterrows():
                        st.session_state.post.append(r.to_dict())
                    save_json(FP,st.session_state.post)
                    st.success("Postazioni importate")
                    st.rerun()
            up_e=st.file_uploader('Import Eventi',type=['xlsx'],key='upe')
            if up_e:
                df_up=pd.read_excel(up_e)
                if st.button(f'IMPORTA {len(df_up)} EVENTI',key='ime'):
                    for _,r in df_up.iterrows():
                        st.session_state.eventi.append(r.to_dict())
                    save_json(FEV,st.session_state.eventi)
                    st.success("Eventi importati")
                    st.rerun()
        with c2:
            up_i=st.file_uploader('Import Interventi',type=['xlsx'],key='upi')
            if up_i:
                df_up=pd.read_excel(up_i)
                if st.button(f'IMPORTA {len(df_up)} INTERVENTI',key='imi'):
                    for _,r in df_up.iterrows():
                        st.session_state.interv.append(r.to_dict())
                    save_json(FE,st.session_state.interv)
                    st.success("Interventi importati")
                    st.rerun()
            up_r=st.file_uploader('Import Radio',type=['xlsx'],key='upr')
            if up_r:
                df_up=pd.read_excel(up_r)
                if st.button(f'IMPORTA {len(df_up)} RADIO',key='imr'):
                    for _,r in df_up.iterrows():
                        st.session_state.radio.append(r.to_dict())
                    save_json(FR,st.session_state.radio)
                    st.success("Radio importate")
                    st.rerun()
    with t3:
        if st.button('CREA BACKUP COMPLETO DI TUTTI I FORM'):
            out=BytesIO()
            w=pd.ExcelWriter(out,engine='openpyxl')
            if st.session_state.dati:
                pd.DataFrame(st.session_state.dati).to_excel(w,sheet_name='Volontari',index=False)
            if st.session_state.post:
                pd.DataFrame(st.session_state.post).to_excel(w,sheet_name='Mappa',index=False)
            if st.session_state.icone:
                pd.DataFrame(st.session_state.icone).to_excel(w,sheet_name='Icone',index=False)
            if st.session_state.interv:
                pd.DataFrame(st.session_state.interv).to_excel(w,sheet_name='Interventi',index=False)
            if st.session_state.eventi:
                pd.DataFrame(st.session_state.eventi).to_excel(w,sheet_name='Eventi',index=False)
            if st.session_state.check:
                pd.DataFrame(st.session_state.check).to_excel(w,sheet_name='CheckIn',index=False)
            if st.session_state.radio:
                pd.DataFrame(st.session_state.radio).to_excel(w,sheet_name='Radio',index=False)
            if st.session_state.cons:
                pd.DataFrame(st.session_state.cons).to_excel(w,sheet_name='Consegna',index=False)
            w.close()
            st.session_state['bk']=out.getvalue()
            st.success('Backup completo creato')
            st.balloons()
        if 'bk' in st.session_state:
            st.download_button('SCARICA BACKUP COMPLETO',st.session_state['bk'],file_name='BACKUP_COMPLETO.xlsx',key='bkt')

elif sc=='Tesserino':
    to_dash()
    st.markdown("## TESSERINO NITIDO PICCOLO")
    st.markdown("### 860x540 - Foto + ODV + Barcode CF")
    if st.session_state.dati:
        df=pd.DataFrame(st.session_state.dati)
        st.markdown("### Clicca riga volontario per generare tesserino")
        ev=st.dataframe(df,on_select="rerun",selection_mode="single-row",key='tt')
        if ev and ev.selection and ev.selection.rows:
            idx=ev.selection.rows[0]
            vol=st.session_state.dati[idx]
            st.divider()
            c1,c2=st.columns([1,2])
            with c1:
                fp=vol.get('FotoFile','')
                if fp and os.path.exists(fp):
                    st.image(fp,width=200)
            with c2:
                tess=tess_make(vol,vol.get('FotoFile',''),"Tesserino-Ezio.JPG" if os.path.exists("Tesserino-Ezio.JPG") else None)
                if tess:
                    st.image(tess)
                    st.download_button('SCARICA TESSERINO NITIDO PICCOLO',tess,file_name=f"Tesserino_{vol.get('Nome','')}_NITIDO.png",mime='image/png',key='t1')
                    st.download_button('SCARICA QUELLO SOTTO OK',tess,file_name=f"Tesserino_{vol.get('Nome','')}_SOTTO.png",mime='image/png',key='t2')
    else:
        st.warning("Nessun volontario presente")

else:
    to_dash()
    st.markdown(f"### {sc} - Form in preparazione")