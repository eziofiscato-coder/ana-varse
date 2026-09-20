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

st.set_page_config(page_title="ANA Varese", layout="wide")

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
                st.error('Errate')
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
    sel=st.radio('Vai a',opts,index=0)
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
        if st.button('VOLONTARI'):
            st.session_state.menu='Volontari'
            st.rerun()
        if st.button('MAPPA'):
            st.session_state.menu='Mappa'
            st.rerun()
        if st.button('LIBRERIA ICONE'):
            st.session_state.menu='Libreria Icone'
            st.rerun()
        if st.button('BACKUP'):
            st.session_state.menu='Backup'
            st.rerun()
    with b:
        if st.button('INTERVENTI'):
            st.session_state.menu='Interventi Emergenza'
            st.rerun()
        if st.button('EVENTI'):
            st.session_state.menu='Eventi'
            st.rerun()
        if st.button('RADIO'):
            st.session_state.menu='DB Radio'
            st.rerun()
        if st.button('TESSERINO'):
            st.session_state.menu='Tesserino'
            st.rerun()

elif sc=='Volontari':
    to_dash()
    st.markdown("## VOLONTARIATO - MASCHERA E SOTTOMASCHERA COME PRIMA")
    # MASCHERA AGGIORNAMENTO - QUANDO CLICCHI RIGA
    if st.session_state.edit_idx >=0:
        if st.session_state.edit_idx < len(st.session_state.dati):
            vol=st.session_state.dati[st.session_state.edit_idx]
            st.success(f"MASCHERA: {vol.get('Nome','')}")
            fp=vol.get('FotoFile','')
            if fp and os.path.exists(fp):
                st.image(fp,width=150,caption="Foto volontario")
            with st.form("edit_vol"):
                c1,c2=st.columns(2)
                with c1:
                    e_nome=st.text_input("Nome",value=vol.get('Nome',''))
                    e_cf=st.text_input("CF",value=vol.get('CF',''))
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
            st.divider()
    # SOTTOMASCHERA 1
    with st.expander("SOTTOMASCHERA 1 - ANAGRAFICA", expanded=True):
        with st.form("anag",clear_on_submit=True):
            c1,c2=st.columns(2)
            with c1:
                a_nome=st.text_input("Nome *")
                a_cogn=st.text_input("Cognome *")
                a_cf=st.text_input("CF *")
            with c2:
                a_ind=st.text_input("Indirizzo")
                a_odv=st.selectbox("ODV",['ANA Varese','PC Varese','CRI','Altro'])
                a_tess=st.text_input("Tessera")
            a_ruolo=st.selectbox("Ruolo",['Volontario','Caposquadra','Coordinatore','Autista','Radio','Altro'])
            b1=st.form_submit_button("SALVA ANAGRAFICA")
            if b1:
                if a_nome and a_cogn:
                    nc=f"{a_nome} {a_cogn}"
                    nuovo={'Nome':nc,'CF':a_cf,'Indirizzo':a_ind,'ODV':a_odv,'Tessera':a_tess,'Ruolo':a_ruolo,'FotoFile':'','Telefono':'','Email':'','Comune':''}
                    st.session_state.dati.append(nuovo)
                    save_json(FD,st.session_state.dati)
                    st.success(f"OK {nc}")
                    st.rerun()
    # SOTTOMASCHERA 2
    with st.expander("SOTTOMASCHERA 2 - CONTATTI"):
        vlist=[d.get('Nome','') for d in st.session_state.dati]
        if vlist:
            sel=st.selectbox("Seleziona volontario",vlist,key='c2')
            idx=-1
            for i,d in enumerate(st.session_state.dati):
                if d.get('Nome','')==sel:
                    idx=i
                    break
            if idx>=0:
                with st.form("cont",clear_on_submit=True):
                    tel=st.text_input("Telefono",value=st.session_state.dati[idx].get('Telefono',''))
                    mail=st.text_input("Email",value=st.session_state.dati[idx].get('Email',''))
                    com=st.text_input("Comune",value=st.session_state.dati[idx].get('Comune',''))
                    bc=st.form_submit_button("SALVA CONTATTI")
                    if bc:
                        st.session_state.dati[idx]['Telefono']=tel
                        st.session_state.dati[idx]['Email']=mail
                        st.session_state.dati[idx]['Comune']=com
                        save_json(FD,st.session_state.dati)
                        st.success("Contatti OK")
                        st.rerun()
    # SOTTOMASCHERA 3 - FOTO
    with st.expander("SOTTOMASCHERA 3 - FOTO VOLONTARIO - CARICA FOTO"):
        vlist=[d.get('Nome','') for d in st.session_state.dati]
        if vlist:
            sel=st.selectbox("Seleziona per foto",vlist,key='c3')
            idx=-1
            for i,d in enumerate(st.session_state.dati):
                if d.get('Nome','')==sel:
                    idx=i
                    break
            if idx>=0:
                fp=st.session_state.dati[idx].get('FotoFile','')
                if fp and os.path.exists(fp):
                    st.image(fp,width=200,caption="Foto attuale")
                up=st.file_uploader("Carica foto volontario",type=['jpg','jpeg','png'])
                if up:
                    st.image(up,width=200,caption="Anteprima nuova foto")
                    if st.button("SALVA FOTO VOLONTARIO"):
                        os.makedirs('foto_volontari',exist_ok=True)
                        fn=f"foto_volontari/{sel.replace(' ','_')}_{up.name}"
                        fout=open(fn,'wb')
                        fout.write(up.getbuffer())
                        fout.close()
                        st.session_state.dati[idx]['FotoFile']=fn
                        save_json(FD,st.session_state.dati)
                        st.success(f"Foto salvata per {sel}")
                        st.rerun()
    st.divider()
    if st.session_state.dati:
        df=pd.DataFrame(st.session_state.dati)
        st.markdown("### Elenco - Clicca riga per aprire maschera e sottomaschera")
        ev=st.dataframe(df,hide_index=False,on_select="rerun",selection_mode="single-row",key='vol_list')
        if ev and ev.selection and ev.selection.rows:
            st.session_state.edit_idx=ev.selection.rows[0]
            st.rerun()

elif sc=='Mappa':
    to_dash()
    st.markdown("## MAPPA POSTAZIONI")
    st.markdown("### Clicca su mappa per posizionare - Icona presa da Libreria")
    if HAS_MAP:
        try:
            mm=folium.Map(location=[45.8205,8.8250],zoom_start=12)
            # Mostra icone da libreria su mappa
            for p in st.session_state.post:
                try:
                    lat=p.get('Lat','45.8205')
                    lon=p.get('Lon','8.8250')
                    tp=p.get('Tipo','')
                    nome_icona=p.get('Icona','Default')
                    # Cerca file icona in libreria
                    icon_file=""
                    for ic in st.session_state.icone:
                        if ic.get('Nome','')==nome_icona:
                            icon_file=ic.get('File','')
                            break
                    la=float(lat)
                    lo=float(lon)
                    # Se icona esiste usa CustomIcon
                    if icon_file and os.path.exists(icon_file):
                        try:
                            icon=folium.CustomIcon(icon_file,icon_size=(32,32))
                            folium.Marker([la,lo],popup=f"{p.get('Nome','')} - {nome_icona}",icon=icon).add_to(mm)
                        except:
                            col='green'
                            if tp=='COC':
                                col='red'
                            elif tp=='Campo base':
                                col='blue'
                            folium.Marker([la,lo],popup=f"{p.get('Nome','')} - {nome_icona}",icon=folium.Icon(color=col)).add_to(mm)
                    else:
                        col='green'
                        if tp=='COC':
                            col='red'
                        elif tp=='Campo base':
                            col='blue'
                        folium.Marker([la,lo],popup=f"{p.get('Nome','')} - {nome_icona}",icon=folium.Icon(color=col)).add_to(mm)
                except:
                    pass
            mp=st_folium(mm,width=1100,height=450)
            if mp and mp.get('last_clicked'):
                st.session_state.sel_lat=str(mp['last_clicked']['lat'])
                st.session_state.sel_lon=str(mp['last_clicked']['lng'])
                st.success(f"Posizione cliccata: {st.session_state.sel_lat}, {st.session_state.sel_lon} - Ora scegli icona da libreria sotto e salva")
        except Exception as e:
            st.error(f"Errore mappa: {e}")
    else:
        st.warning("Installa folium per mappa")
    st.divider()
    st.markdown("### Maschera sotto - Icona da Libreria Icone per posizioni")
    if st.session_state.edit_map >=0:
        if st.session_state.edit_map < len(st.session_state.post):
            p=st.session_state.post[st.session_state.edit_map]
            st.success(f"Modifica: {p.get('Nome','')} - Icona: {p.get('Icona','')}")
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
                    # Icona da libreria
                    lst=['Default']
                    if st.session_state.icone:
                        lst=[]
                        for it in st.session_state.icone:
                            lst.append(it.get('Nome','Default'))
                    e_icon=st.selectbox("Icona da Libreria per posizione",lst)
                    # Anteprima icona
                    for ic in st.session_state.icone:
                        if ic.get('Nome','')==e_icon:
                            fp=ic.get('File','')
                            if fp and os.path.exists(fp):
                                st.image(fp,width=50,caption=f"Icona: {e_icon}")
                with c3:
                    e_r1=st.text_input("Rif Coordinatore",value=p.get('Rif1',''))
                    e_r2=st.text_input("Rif Telefono",value=p.get('Rif2',''))
                    e_note=st.text_area("Note",value=p.get('Note',''))
                b1,b2=st.columns(2)
                with b1:
                    bs=st.form_submit_button("SALVA CON ICONA DA LIBRERIA")
                with b2:
                    bd=st.form_submit_button("ELIMINA")
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
            if st.button("ANNULLA"):
                st.session_state.edit_map=-1
                st.rerun()
    else:
        st.markdown("#### Nuova postazione - Prima clicca su mappa sopra poi scegli icona da libreria")
        with st.form("mapa",clear_on_submit=True):
            c1,c2,c3=st.columns(3)
            with c1:
                m_nome=st.text_input("Nome postazione *")
                m_com=st.text_input("Comune *")
                m_via=st.text_input("Via")
            with c2:
                m_lat=st.text_input("Lat - click mappa sopra",value=st.session_state.sel_lat)
                m_lon=st.text_input("Lon - click mappa sopra",value=st.session_state.sel_lon)
                m_tipo=st.selectbox("Tipo postazione",['COC','Campo base','Magazzino','Sede','Punto ritrovo','Altro'])
                lst=['Default','COC','Campo','Magazzino','Sede','Mezzo']
                if st.session_state.icone:
                    lst=[]
                    for it in st.session_state.icone:
                        lst.append(it.get('Nome','Default'))
                m_icon=st.selectbox("SCEGLI ICONA DA LIBRERIA PER POSIZIONE",lst)
            with c3:
                m_r1=st.text_input("Rif Coordinatore")
                m_r2=st.text_input("Rif Telefono")
                m_note=st.text_area("Note")
            # Anteprima icona scelta
            if st.session_state.icone:
                for ic in st.session_state.icone:
                    if ic.get('Nome','')==m_icon:
                        fp=ic.get('File','')
                        if fp and os.path.exists(fp):
                            st.image(fp,width=60,caption=f"Icona scelta: {m_icon} - Verrà lasciata su mappa")
            bm=st.form_submit_button("SALVA POSTAZIONE CON ICONA DA LIBRERIA")
            if bm:
                if m_nome and m_com:
                    nuovo={'Nome':m_nome,'Comune':m_com,'Via':m_via,'Lat':m_lat,'Lon':m_lon,'Tipo':m_tipo,'Icona':m_icon,'Rif1':m_r1,'Rif2':m_r2,'Note':m_note}
                    st.session_state.post.append(nuovo)
                    save_json(FP,st.session_state.post)
                    st.success(f"Postazione {m_nome} salvata con icona {m_icon} da