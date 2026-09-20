import streamlit as st
import pandas as pd
from io import BytesIO
import os, json, hashlib
from datetime import date

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
    except:
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
        except:
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
            except:
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
    st.markdown("## Dashboard - A.N.A. NUCLEO VOLONTARI DI PROTEZIONE CIVILE SEZIONE DI VARESE")
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
    st.divider()
    c1,c2,c3,c4,c5=st.columns(5)
    with c1:
        st.metric('Vol',len(st.session_state.dati))
    with c2:
        st.metric('Post',len(st.session_state.post))
    with c3:
        st.metric('Icone',len(st.session_state.icone))
    with c4:
        st.metric('Interv',len(st.session_state.interventi))
    with c5:
        st.metric('Eventi',len(st.session_state.eventi))

elif sc=='Volontari':
    to_dash()
    st.markdown("## VOLONTARI - CON MASCHERE")
    if st.session_state.edit_idx >=0 and st.session_state.edit_idx < len(st.session_state.dati):
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
                e_mail=st.text_input("Email",value=vol.get('Email',''))
            b1,b2,b3=st.columns(3)
            with b1:
                bs=st.form_submit_button("SALVA",type="primary",use_container_width=True)
            with b2:
                ba=st.form_submit_button("ANNULLA",use_container_width=True)
            with b3:
                bd=st.form_submit_button("ELIMINA",use_container_width=True)
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
                a_odv=st.selectbox("ODV",["A.N.A. Varese","PC Varese","CRI","Altro"])
                a_tess=st.text_input("Tessera")
            a_ruolo=st.selectbox("Ruolo",["Volontario","Caposquadra","Coordinatore","Autista","Radio","Altro"])
            b1=st.form_submit_button("SALVA",use_container_width=True,type="primary")
            if b1:
                if a_nome and a_cogn:
                    nc=f"{a_nome} {a_cogn}"
                    nuovo={'Nome':nc,'CF':a_cf,'Indirizzo':a_ind,'ODV':a_odv,'Tessera':a_tess,'Ruolo':a_ruolo,'FotoFile':''}
                    st.session_state.dati.append(nuovo)
                    save_json(FD,st.session_state.dati)
                    st.success(f"OK {nc}")
                    st.rerun()
    with st.expander("CONTATTI - MASCHERA 2"):
        vlist=[d.get('Nome','') for d in st.session_state.dati]
        if vlist:
            sel=st.selectbox("Seleziona",vlist,key='c2')
            idx=-1
            for i,d in enumerate(st.session_state.dati):
                if d.get('Nome','')==sel:
                    idx=i
                    break
            if idx>=0:
                with st.form("cont"):
                    tel=st.text_input("Tel",value=st.session_state.dati[idx].get('Telefono',''))
                    mail=st.text_input("Email",value=st.session_state.dati[idx].get('Email',''))
                    b=st.form_submit_button("SALVA CONTATTI",type="primary")
                    if b:
                        st.session_state.dati[idx]['Telefono']=tel
                        st.session_state.dati[idx]['Email']=mail
                        save_json(FD,st.session_state.dati)
                        st.success("OK")
                        st.rerun()
    with st.expander("FOTO - MASCHERA 3"):
        vlist=[d.get('Nome','') for d in st.session_state.dati]
        if vlist:
            sel=st.selectbox("Seleziona",vlist,key='c3')
            idx=-1
            for i,d in enumerate(st.session_state.dati):
                if d.get('Nome','')==sel:
                    idx=i
                    break
            if idx>=0:
                fp=st.session_state.dati[idx].get('FotoFile','')
                if fp and os.path.exists(fp):
                    st.image(fp,width=120)
                up=st.file_uploader("Foto",type=['jpg','png','jpeg'])
                if up:
                    st.image(up,width=120)
                    if st.button("SALVA FOTO"):
                        os.makedirs('foto_volontari',exist_ok=True)
                        fn=f"foto_volontari/{sel.replace(' ','_')}_{up.name}"
                        f=open(fn,'wb')
                        f.write(up.getbuffer())
                        f.close()
                        st.session_state.dati[idx]['FotoFile']=fn
                        save_json(FD,st.session_state.dati)
                        st.success("OK")
                        st.rerun()
    st.divider()
    if st.session_state.dati:
        df=pd.DataFrame(st.session_state.dati)
        st.markdown("### ELENCO - CLICCA RIGA PER MASCHERA AGGIORNAMENTO")
        ev=st.dataframe(df,use_container_width=True,hide_index=False,on_select="rerun",selection_mode="single-row",key='tab_vol')
        if ev and ev.selection and ev.selection.rows:
            st.session_state.edit_idx=ev.selection.rows[0]
            st.rerun()

elif sc=='Mappa':
    to_dash()
    st.markdown("## MAPPA - SOPRA MAPPA SOTTO MASCHERA + ICONA")
    if HAS_MAP:
        try:
            mm=folium.Map(location=[st.session_state.sel_lat,st.session_state.sel_lon],zoom_start=12)
            for p in st.session_state.post:
                try:
                    lat=p.get('Lat',45.8205)
                    lon=p.get('Lon',8.8250)
                    tp=p.get('Tipo','')
                    col='green'
                    if tp=='COC':
                        col='red'
                    elif tp=='Campo base':
                        col='blue'
                    folium.Marker([lat,lon],popup=f"{p.get('Nome','')} - {p.get('Icona','')}",icon=folium.Icon(color=col)).add_to(mm)
                except:
                    pass
            mp=st_folium(mm,width=1100,height=400)
            if mp and mp.get('last_clicked'):
                st.session_state.sel_lat=mp['last_clicked']['lat']
                st.session_state.sel_lon=mp['last_clicked']['lng']
                st.success(f"Pos: {st.session_state.sel_lat:.5f} {st.session_state.sel_lon:.5f} - scegli icona sotto")
        except Exception as e:
            st.error(f"Err: {e}")
    st.divider()
    st.markdown("### MASCHERA SOTTO - CON RIFERIMENTI E ICONA")
    if st.session_state.edit_map >=0 and st.session_state.edit_map < len(st.session_state.post):
        p=st.session_state.post[st.session_state.edit_map]
        st.success(f"Modifica: {p.get('Nome','')}")
        with st.form("edit_map"):
            c1,c2,c3=st.columns(3)
            with c1:
                e_nome=st.text_input("Nome",value=p.get('Nome',''))
                e_com=st.text_input("Comune",value=p.get('Comune',''))
                e_via=st.text_input("Via",value=p.get('Via',''))
            with c2:
                e_lat=st.number_input("Lat",value=float(p.get('Lat',45.8205)),format="%.6f")
                e_lon=st.number_input("Lon",value=float(p.get('Lon',8.8250)),format="%.6f")
                e_tipo=st.selectbox("Tipo",["COC","Campo base","Magazzino","Sede","Altro"])
                lst=["Default","COC","Campo","Magazzino","Sede"]
                if st.session_state.icone:
                    lst=[]
                    for it in st.session_state.icone:
                        lst.append(it.get('Nome','Default'))
                e_icon=st.selectbox("Icona",lst)
            with c3:
                e_r1=st.text_input("Rif1",value=p.get('Rif1',''))
                e_r2=st.text_input("Rif2",value=p.get('Rif2',''))
                e_note=st.text_area("Note",value=p.get('Note',''))
            b1,b2=st.columns(2)
            with b1:
                bs=st.form_submit_button("SALVA",type="primary",use_container_width=True)
            with b2:
                bd=st.form_submit_button("ELIMINA",use_container_width=True)
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
        with st.form("mapa",clear_on_submit=True):
            c1,c2,c3=st.columns(3)
            with c1:
                m_nome=st.text_input("Nome *")
                m_com=st.text_input("Comune *")
                m_via=st.text_input("Via")
            with c2:
                m_lat=st.number_input("Lat",value=float(st.session_state.sel_lat),format="%.6f")
                m_lon=st.number_input("Lon",value=float(st.session_state.sel_lon),format="%.6f")
                m_tipo=st.selectbox("Tipo",["COC","Campo base","Magazzino","Sede","Altro"])
                lst=["Default","COC","Campo","Magazzino","Sede","Mezzo"]
                if st.session_state.icone:
                    lst=[]
                    for it in st.session_state.icone:
                        lst.append(it.get('Nome','Default'))
                m_icon=st.selectbox("Icona",lst)
            with c3:
                m_r1=st.text_input("Rif1 Coord")
                m_r2=st.text_input("Rif2 Tel")
                m_note=st.text_area("Note")
            bm=st.form_submit_button("SALVA POSTAZIONE CON ICONA",use_container_width=True,type="primary")
            if bm:
                if m_nome and m_com:
                    nuovo={'Nome':m_nome,'Comune':m_com,'Via':m_via,'Lat':m_lat,'Lon':m_lon,'Tipo':m_tipo,'Icona':m_icon,'Rif1':m_r1,'Rif2':m_r2,'Note':m_note}
                    st.session_state.post.append(nuovo)
                    save_json(FP,st.session_state.post)
                    st.success(f"OK {m_nome} con icona {m_icon}")
                    st.rerun()
    if st.session_state.post:
        st.divider()
        st.markdown("### ANTEPRIMA POSTAZIONI CON TUTTE LE IMPOSTAZIONI")
        df=pd.DataFrame(st.session_state.post)
        st.dataframe(df,use_container_width=True)
        ev=st.dataframe(df,use_container_width=True,hide_index=False,on_select="rerun",selection_mode="single-row",key='tab_mapa')
        if ev and ev.selection and ev.selection.rows:
            st.session_state.edit_map=ev.selection.rows[0]
            st.rerun()

elif sc=='Icone':
    to_dash()
    st.markdown("## LIBRERIA ICONE - MASCHERA")
    c1,c2=st.columns([1,1])
    with c1:
        with st.form("icone",clear_on_submit=True):
            i_nome=st.text_input("Nome icona *")
            i_cat=st.selectbox("Categoria",["COC","Campo base","Magazzino","Sede","Mezzo","Altro"])
            i_file=st.file_uploader("File icona",type=['png','jpg','jpeg','svg'])
            i_desc=st.text_area("Descrizione")
            bi=st.form_submit_button("SALVA ICONA",use_container_width=True,type="primary")
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
                    st.success("OK icona salvata - ora in mappa selezione")
                    st.rerun()
    with c2:
        if st.session_state.icone:
            df=pd.DataFrame(st.session_state.icone)
            st.dataframe(df,use_container_width=True)
            st.markdown("### Anteprima icone")
            for ic in st.session_state.icone[-3:]:
                fp=ic.get('File','')
                if fp and os.path.exists(fp):
                    st.image(fp,width=50,caption=ic.get('Nome',''))

elif sc=='Interventi':
    to_dash()
    st.markdown("## INTERVENTI EMERGENZA - MASCHERA")
    with st.form("emerg",clear_on_submit=True):
        c1,c2,c3=st.columns(3)
        with c1:
            d_int=st.date_input("Data")
            o_int=st.time_input("Ora")
        with c2:
            com_int=st.text_input("Comune *")
            via_int=st.text_input("Via *")
        with c3:
            civ_int=st.text_input("Civico")
            odv_int=st.selectbox("ODV",["A.N.A. Varese","PC Lombardia","CRI","Altro"])
        az_int=st.text_area("Azione *",height=80)
        sv=st.form_submit_button("SALVA INTERVENTO",use_container_width=True,type="primary")
        if sv:
            if com_int and via_int and az_int:
                nuovo={"Data":str(d_int),"Ora":str(o_int),"Comune":com_int,"Via":via_int,"Civico":civ_int,"ODV":odv_int,"Azione":az_int}
                st.session_state.interventi.append(nuovo)
                save_json(FE,st.session_state.interventi)
                st.success("OK salvato")
                st.rerun()
    if st.session_state.interventi:
        df=pd.DataFrame(st.session_state.interventi)
        st.dataframe(df,use_container_width=True)

elif sc=='Eventi':
    to_dash()
    st.markdown("## EVENTI - MASCHERA")
    with st.form("eventi",clear_on_submit=True):
        c1,c2=st.columns(2)
        with c1:
            ev_nome=st.text_input("Nome evento *")
            ev_data=st.date_input("Data")
            ev_com=st.text_input("Comune")
        with c2:
            ev_luogo=st.text_input("Luogo")
            ev_tipo=st.selectbox("Tipo",["Esercitazione","Intervento","Formazione","Riunione","Altro"])
            ev_resp=st.text_input("Responsabile")
        ev_desc=st.text_area("Descrizione")
        be=st.form_submit_button("SALVA EVENTO",use_container_width=True,type="primary")
        if be:
            if ev_nome:
                nuovo={'Nome':ev_nome,'Data':str(ev_data),'Comune':ev_com,'Luogo':ev_luogo,'Tipo':ev_tipo,'Responsabile':ev_resp,'Descrizione':ev_desc}
                st.session_state.eventi.append(nuovo)
                save_json(FEV,st.session_state.eventi)
                st.success("OK")
                st.rerun()
    if st.session_state.eventi:
        df=pd.DataFrame(st.session_state.eventi)
        st.dataframe(df,use_container_width=True)

elif sc=='Check In':
    to_dash()
    st.markdown("## CHECK IN - MASCHERA")
    vlist=[d.get('Nome','') for d in st.session_state.dati]
    if vlist:
        with st.form("check",clear_on_submit=True):
            sel=st.selectbox("Volontario",vlist)
            d_check=st.date_input("Data")
            o_check=st.time_input("Ora")
            bc=st.form_submit_button("SALVA CHECK IN",use_container_width=True,type="primary")
            if bc:
                nuovo={'Volontario':sel,'Data':str(d_check),'Ora':str(o_check)}
                st.session_state.check.append(nuovo)
                save_json(FC,st.session_state.check)
                st.success("OK")
                st.rerun()
    if st.session_state.check:
        df=pd.DataFrame(st.session_state.check)
        st.dataframe(df,use_container_width=True)

elif sc=='Radio':
    to_dash()
    st.markdown("## DB RADIO - MASCHERA