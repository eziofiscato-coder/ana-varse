import streamlit as st
import pandas as pd
from io import BytesIO
import os, json, hashlib
from datetime import date, datetime

try:
    import folium
    from streamlit_folium import st_folium
    HAS_MAP=True
except Exception:
    HAS_MAP=False

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
 border-radius:12px!important; padding:12px!important}
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
        code=barcode.get('code128',(cf or "0000000000000000")[:16].upper(),writer=ImageWriter())
        buf=BytesIO()
        code.write(buf)
        buf.seek(0)
        return buf.getvalue()
    except Exception:
        return None

def crea_tess(vol,foto_path,tmpl):
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
        odv=vol.get('ODV','A.N.A. NUCLEO VOLONTARI DI PROTEZIONE CIVILE SEZIONE DI VARESE')
        oy=ny+30
        draw.rectangle([nx,oy,nx+int(W*0.5),oy+20],fill='white')
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
FEV='eventi.json'

for k,v in [
    ('dati',[]),('post',[]),('icone',[]),
    ('emerg',[]),('check',[]),('radio',[]),
    ('cons',[]),('eventi',[]),
    ('interventi_lista',[]),('menu','Dashboard'),
    ('auth',False),('popup_shown',False),
    ('edit_idx',-1),('edit_map_idx',-1),
    ('sel_lat',45.8205),('sel_lon',8.8250),
    ('map_full',False)
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
st.session_state.eventi=load(FEV,[])
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
            "<div style='background:#0e7a3d;padding:14px;"
            "border-radius:8px;border:2px solid #0e7a3d;"
            "text-align:center;'>"
            "<b style='color:white;font-size:18px;'>"
            "A.N.A. NUCLEO VOLONTARI DI PROTEZIONE CIVILE<br>"
            "SEZIONE DI VARESE</b></div>",
            unsafe_allow_html=True
        )

def torna():
    if st.button('TORNA ALLA DASHBOARD'):
        st.session_state.menu='Dashboard'
        st.rerun()

if not st.session_state.popup_shown:
    header()
    st.markdown(
        "<h3 style='text-align:center;color:#0e7a3d;'>"
        "Ciao Ragazzi, Buon Lavoro!</h3>",
        unsafe_allow_html=True
    )
    st.divider()
    c1,c2,c3=st.columns([1,1,1])
    with c2:
        for img_name in ['copertina.jpg']:
            if os.path.exists(img_name):
                try:
                    st.image(img_name,width=250)
                    break
                except Exception:
                    pass
        if st.button(
            "ENTRA NEL SISTEMA",
            type="primary",
            use_container_width=True
        ):
            st.session_state.popup_shown=True
            st.rerun()
    st.stop()

if not st.session_state.auth:
    header()
    c1,c2,c3=st.columns([1,2,1])
    with c2:
        st.markdown("### LOGIN")
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
                st.error('Errati')
        if st.button('TORNA INIZIO'):
            st.session_state.popup_shown=False
            st.rerun()
    st.stop()

header()
with st.sidebar:
    st.markdown('**MENU COMPLETO**')
    opts=[
        'Dashboard','Volontari','Mappa',
        'Libreria Icone','Interventi Emergenza',
        'Eventi','Check In',
        'DB Radio','Consegna Radio',
        'Backup','Tesserino','Logout'
    ]
    sel=st.radio('Vai a',opts,index=0)
    if sel=='Logout':
        st.session_state.auth=False
        st.session_state.popup_shown=False
        st.rerun()
    st.session_state.menu=sel
    if st.button('MOSTRA POPUP',use_container_width=True):
        st.session_state.popup_shown=False
        st.rerun()

scelta=st.session_state.menu

if scelta=='Dashboard':
    st.markdown("## Dashboard - A.N.A. NUCLEO VOLONTARI DI PROTEZIONE CIVILE SEZIONE DI VARESE")
    c1,c2=st.columns(2)
    with c1:
        if st.button('VOLONTARI',use_container_width=True):
            st.session_state.menu='Volontari'
            st.rerun()
        if st.button('MAPPA FULL SCREEN',use_container_width=True):
            st.session_state.menu='Mappa'
            st.rerun()
        if st.button('LIBRERIA ICONE',use_container_width=True):
            st.session_state.menu='Libreria Icone'
            st.rerun()
        if st.button('INTERVENTI',use_container_width=True):
            st.session_state.menu='Interventi Emergenza'
            st.rerun()
        if st.button('EVENTI',use_container_width=True):
            st.session_state.menu='Eventi'
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
        if st.button('CONSEGNA RADIO',use_container_width=True):
            st.session_state.menu='Consegna Radio'
            st.rerun()
        if st.button('TESSERINO NITIDO',use_container_width=True):
            st.session_state.menu='Tesserino'
            st.rerun()
    st.divider()
    c1,c2,c3,c4,c5=st.columns(5)
    with c1: st.metric('Volontari',len(st.session_state.dati))
    with c2: st.metric('Postazioni',len(st.session_state.post))
    with c3: st.metric('Icone',len(st.session_state.icone))
    with c4: st.metric('Interventi',len(st.session_state.interventi_lista))
    with c5: st.metric('Eventi',len(st.session_state.eventi))
    st.divider()
    if st.session_state.dati:
        df=pd.DataFrame(st.session_state.dati)
        st.markdown("### CLICCA RIGA VOLONTARIO PER MODIFICARE SU MASCHERA")
        event=st.dataframe(df,use_container_width=True,hide_index=False,on_select="rerun",selection_mode="single-row")
        if event and event.selection and event.selection.rows:
            idx=event.selection.rows[0]
            st.session_state.edit_idx=idx
            st.session_state.menu='Volontari'
            st.rerun()

elif scelta=='Volontari':
    torna()
    st.markdown("## VOLONTARI - A.N.A. NUCLEO VOLONTARI DI PROTEZIONE CIVILE SEZIONE DI VARESE")
    if st.session_state.edit_idx >=0 and st.session_state.edit_idx < len(st.session_state.dati):
        vol=st.session_state.dati[st.session_state.edit_idx]
        st.success(f"Modifica dati per: {vol.get('Nome','')}")
        with st.form("form_edit"):
            c1,c2=st.columns(2)
            with c1:
                e_nome=st.text_input("Nome",value=vol.get('Nome',''))
                e_cf=st.text_input("CF",value=vol.get('CF',''))
                e_ind=st.text_input("Indirizzo",value=vol.get('Indirizzo',''))
                e_comune=st.text_input("Comune",value=vol.get('Comune',''))
            with c2:
                e_odv=st.text_input("ODV",value=vol.get('ODV',''))
                e_tess=st.text_input("Tessera",value=vol.get('Tessera',''))
                e_ruolo=st.selectbox("Ruolo",["Volontario","Caposquadra","Coordinatore","Autista","Radio","Altro"])
                e_tel=st.text_input("Telefono",value=vol.get('Telefono',''))
                e_email=st.text_input("Email",value=vol.get('Email',''))
            cA,cB=st.columns(2)
            with cA:
                btn_save=st.form_submit_button("SALVA MODIFICHE",type="primary",use_container_width=True)
            with cB:
                btn_del=st.form_submit_button("ELIMINA",use_container_width=True)
            if btn_save:
                vol['Nome']=e_nome
                vol['CF']=e_cf
                vol['Indirizzo']=e_ind
                vol['Comune']=e_comune
                vol['ODV']=e_odv
                vol['Tessera']=e_tess
                vol['Ruolo']=e_ruolo
                vol['Telefono']=e_tel
                vol['Email']=e_email
                st.session_state.dati[st.session_state.edit_idx]=vol
                save(FD,st.session_state.dati)
                st.success("Modificati!")
                st.session_state.edit_idx=-1
                st.rerun()
            if btn_del:
                st.session_state.dati.pop(st.session_state.edit_idx)
                save(FD,st.session_state.dati)
                st.session_state.edit_idx=-1
                st.rerun()
        if st.button("ANNULLA"):
            st.session_state.edit_idx=-1
            st.rerun()
        st.divider()
    t1,t2,t3,t4,t5,t6=st.tabs(["1.Anagrafica","2.Contatti","3.Foto","4.Formazione","5.Disp","6.Elenco + Click"])
    with t1:
        with st.form("form_anag",clear_on_submit=True):
            c1,c2=st.columns(2)
            with c1:
                a_nome=st.text_input("Nome *")
                a_cogn=st.text_input("Cognome *")
                a_cf=st.text_input("CF *")
            with c2:
                a_ind=st.text_input("Indirizzo")
                a_comune=st.text_input("Comune")
                a_odv=st.selectbox("ODV",["A.N.A. NUCLEO VOLONTARI DI PROTEZIONE CIVILE SEZIONE DI VARESE","A.N.A. Sezione di Varese","PC Varese","CRI","Altro"])
                a_tess=st.text_input("Tessera")
            a_ruolo=st.selectbox("Ruolo",["Volontario","Caposquadra","Coordinatore","Autista","Radio","Altro"])
            btn1=st.form_submit_button("SALVA",use_container_width=True,type="primary")
            if btn1:
                if a_nome and a_cogn:
                    nc=f"{a_nome} {a_cogn}"
                    nuovo={'Nome':nc,'CF':a_cf,'Indirizzo':a_ind,'Comune':a_comune,'ODV':a_odv,'Tessera':a_tess,'Ruolo':a_ruolo,'FotoFile':''}
                    st.session_state.dati.append(nuovo)
                    save(FD,st.session_state.dati)
                    st.success(f"Salvata {nc}!")
                    st.rerun()
    with t6:
        if st.session_state.dati:
            df=pd.DataFrame(st.session_state.dati)
            st.info("CLICCA RIGA PER MODIFICARE SU MASCHERA")
            event=st.dataframe(df,use_container_width=True,hide_index=False,on_select="rerun",selection_mode="single-row",key='tab_vol')
            if event and event.selection and event.selection.rows:
                idx=event.selection.rows[0]
                st.session_state.edit_idx=idx
                st.rerun()

elif scelta=='Mappa':
    torna()
    st.markdown("## MAPPA POSTAZIONI - A.N.A. NUCLEO VOLONTARI DI PROTEZIONE CIVILE SEZIONE DI VARESE")
    # MAPPA FULL SCREEN TOGGLE
    c1,c2=st.columns([3,1])
    with c1:
        st.markdown("### PROGRAMMAZIONE COME STAMATTINA - CLICK PER POSTAZIONI + RIFERIMENTI IN MASCHERA")
    with c2:
        if st.button("ESTENDI MAPPA FULL SCREEN" if not st.session_state.map_full else "RIDUCI MAPPA"):
            st.session_state.map_full=not st.session_state.map_full
            st.rerun()
    # FORM CON RIFERIMENTI - COME STAMATTINA
    if st.session_state.edit_map_idx >=0 and st.session_state.edit_map_idx < len(st.session_state.post):
        p=st.session_state.post[st.session_state.edit_map_idx]
        st.success(f"Modifica postazione: {p.get('Nome','')}")
        with st.form("form_edit_map"):
            c1,c2=st.columns(2)
            with c1:
                e_nome=st.text_input("Nome postazione",value=p.get('Nome',''))
                e_comune=st.text_input("Comune",value=p.get('Comune',''))
                e_via=st.text_input("Via",value=p.get('Via',''))
                e_ref1=st.text_input("Riferimento 1 (es. Coordinatore)",value=p.get('Rif1',''))
                e_ref2=st.text_input("Riferimento 2 (es. Telefono)",value=p.get('Rif2',''))
            with c2:
                e_lat=st.number_input("Latitudine",value=float(p.get('Lat',45.8205)),format="%.6f")
                e_lon=st.number_input("Longitudine",value=float(p.get('Lon',8.8250)),format="%.6f")
                e_tipo=st.selectbox("Tipo",["COC","Campo base","Magazzino","Sede","Punto ritrovo","Altro"],index=0)
                e_icona=st.selectbox("Icona",["Default","COC","Campo","Magazzino","Sede"],index=0)
                e_note=st.text_area("Note postazione",value=p.get('Note',''))
            cA,cB=st.columns(2)
            with cA:
                btn_save=st.form_submit_button("SALVA MODIFICHE POSTAZIONE",type="primary",use_container_width=True)
            with cB:
                btn_del=st.form_submit_button("ELIMINA POSTAZIONE",use_container_width=True)
            if btn_save:
                p['Nome']=e_nome
                p['Comune']=e_comune
                p['Via']=e_via
                p['Lat']=e_lat
                p['Lon']=e_lon
                p['Tipo']=e_tipo
                p['Icona']=e_icona
                p['Rif1']=e_ref1
                p['Rif2']=e_ref2
                p['Note']=e_note
                st.session_state.post[st.session_state.edit_map_idx]=p
                save(FP,st.session_state.post)
                st.success("Postazione modificata!")
                st.session_state.edit_map_idx=-1
                st.rerun()
            if btn_del:
                st.session_state.post.pop(st.session_state.edit_map_idx)
                save(FP,st.session_state.post)
                st.session_state.edit_map_idx=-1
                st.rerun()
        if st.button("ANNULLA MODIFICA"):
            st.session_state.edit_map_idx=-1
            st.rerun()
        st.divider()
    # LAYOUT MAPPA + FORM - FULL SCREEN
    if st.session_state.map_full:
        # MAPPA FULL SCREEN
        st.markdown("### MAPPA FULL SCREEN - CLICCA PER POSTAZIONI")
        if HAS_MAP:
            try:
                m=folium.Map(location=[st.session_state.sel_lat,st.session_state.sel_lon],zoom_start=13)
                for p in st.session_state.post:
                    try:
                        lat=p.get('Lat',45.8205)
                        lon=p.get('Lon',8.8250)
                        folium.Marker([lat,lon],popup=f"{p.get('Nome','')} - {p.get('Comune','')} - Rif: {p.get('Rif1','')}",icon=folium.Icon(color='green')).add_to(m)
                    except Exception:
                        pass
                map_data=st_folium(m,width=1200,height=700)
                if map_data and map_data.get('last_clicked'):
                    st.session_state.sel_lat=map_data['last_clicked']['lat']
                    st.session_state.sel_lon=map_data['last_clicked']['lng']
                    st.info(f"Click rilevato: Lat {st.session_state.sel_lat} Lon {st.session_state.sel_lon} - Inseriti in maschera")
            except Exception as e:
                st.error(f"Errore mappa: {e}")
        # FORM SOTTO MAPPA FULL
        with st.form("form_mappa_full",clear_on_submit=True):
            c1,c2,c3=st.columns(3)
            with c1:
                m_nome=st.text_input("Nome postazione *")
                m_comune=st.text_input("Comune *")
                m_via=st.text_input("Via *")
            with c2:
                m_lat=st.number_input("Latitudine",value=float(st.session_state.sel_lat),format="%.6f")
                m_lon=st.number_input("Longitudine",value=float(st.session_state.sel_lon),format="%.6f")
                m_tipo=st.selectbox("Tipo",["COC","Campo base","Magazzino","Sede","Punto ritrovo","Altro"])
            with c3:
                m_rif1=st.text_input("Riferimento 1 - Coordinatore / Responsabile")
                m_rif2=st.text_input("Riferimento 2 - Telefono / Radio")
                m_note=st.text_area("Note")
                m_icona=st.selectbox("Icona",["Default","COC","Campo","Magazzino"])
            btn_m=st.form_submit_button("SALVA POSTAZIONE CON RIFERIMENTI",use_container_width=True,type="primary")
            if btn_m:
                if m_nome and m_comune:
                    nuovo={'Nome':m_nome,'Comune':m_comune,'Via':m_via,'Lat':m_lat,'Lon':m_lon,'Tipo':m_tipo,'Rif1':m_rif1,'Rif2':m_rif2,'Note':m_note,'Icona':m_icona}
                    st.session_state.post.append(nuovo)
                    save(FP,st.session_state.post)
                    st.success(f"Postazione {m_nome} salvata! Anteprima mappa con impostazioni visibile sotto")
                    st.rerun()
        # ANTEPRIMA POSTAZIONE SALVATA SULLA MAPPA CON TUTTE LE IMPOSTAZIONI
        if st.session_state.post:
            st.markdown("### ANTEPRIMA POSTAZIONI SALVATE SULLA MAPPA CON TUTTE LE IMPOSTAZIONI")
            df=pd.DataFrame(st.session_state.post)
            st.dataframe(df,use_container_width=True)
            st.markdown("### Dettaglio postazione salvata:")
            for p in st.session_state.post[-3:]:
                with st.expander(f"{p.get('Nome','')} - {p.get('Comune','')}"):
                    st.write(f"Via: {p.get('Via','')}")
                    st.write(f"Lat: {p.get('Lat','')} Lon: {p.get('Lon','')}")
                    st.write(f"Tipo: {p.get('Tipo','')} Icona: {p.get('Icona','')}")
                    st.write(f"Rif1: {p.get('Rif1','')} Rif2: {p.get('Rif2','')}")
                    st.write(f"Note: {p.get('Note','')}")
    else:
        # LAYOUT NORMALE - FORM + MAPPA AFFIANCATE
        c1,c2=st.columns([1,1])
        with c1:
            st.markdown("### Form postazione con riferimenti - Click mappa per lat/lon")
            with st.form("form_mappa",clear_on_submit=True):
                m_nome=st.text_input("Nome postazione *")
                m_comune=st.text_input("Comune *")
                m_via=st.text_input("Via *")
                m_lat=st.number_input("Latitudine (click su mappa)",value=float(st.session_state.sel_lat),format="%.6f")
                m_lon=st.number_input("Longitudine (click su mappa)",value=float(st.session_state.sel_lon),format="%.6f")
                m_tipo=st.selectbox("Tipo",["COC","Campo base","Magazzino","Sede","Punto ritrovo","Altro"])
                m_rif1=st.text_input("Riferimento 1 - Coordinatore")
                m_rif2=st.text_input("Riferimento 2 - Telefono")
                m_note=st.text_area("Note")
                m_icona=st.selectbox("Icona",["Default","COC","Campo","Magazzino"])
                btn_m=st.form_submit_button("SALVA POSTAZIONE",use_container_width=True,type="primary")
                if btn_m:
                    if m_nome and m_comune:
                        nuovo={'Nome':m_nome,'Comune':m_comune,'Via':m_via,'Lat':m_lat,'Lon':m_lon,'Tipo':m_tipo,'Rif1':m_rif1,'Rif2':m_rif2,'Note':m_note,'Icona':m_icona}
                        st.session_state.post.append(nuovo)
                        save(FP,st.session_state.post)
                        st.success(f"Salvata! Anteprima sotto")
                        st.rerun()
            if st.session_state.post:
                df=pd.DataFrame(st.session_state.post)
                st.markdown("### Elenco - Clicca riga per modificare maschera")
                event=st.dataframe(df,use_container_width=True,hide_index=False,on_select="rerun",selection_mode="single-row",key='tab_mappa')
                if event and event.selection and event.selection.rows:
                    idx=event.selection.rows[0]
                    st.session_state.edit_map_idx=idx
                    st.rerun()
        with c2:
            st.markdown("### Mappa - Clicca per impostare lat/lon nella maschera")
            if HAS_MAP:
                try:
                    m=folium.Map(location=[st.session_state.sel_lat,st.session_state.sel_lon],zoom_start=12)
                    for p in st.session_state.post:
                        try:
                            lat=p.get('Lat',45.8205)
                            lon=p.get('Lon',8.8250)
                            folium.Marker([lat,lon],popup=f"{p.get('Nome','')} - {p.get('Comune','')} - Rif:{p.get('Rif1','')}",icon=folium.Icon(color='green')).add_to(m)
                        except Exception:
                            pass
                    map_data=st_folium(m,width=500,height=500)
                    if map_data and map_data.get('last_clicked'):
                        st.session_state.sel_lat=map_data['last_clicked']['lat']
                        st.session_state.sel_lon=map_data['last_clicked']['lng']
                        st.info(f"Click: {st.session_state.sel_lat:.6f}, {st.session_state.sel_lon:.6f} - Inseriti in form a sinistra")
                    # ANTEPRIMA POSTAZIONE SALVATA
                    if st.session_state.post:
                        st.markdown("### Anteprima postazioni salvate")
                        last=st.session_state.post[-1]
                        st.success(f"Ultima: {last.get('Nome','')} - {last.get('Comune','')} - Tipo: {last.get('Tipo','')} - Rif: {last.get('Rif1','')}")
                except Exception as e:
                    st.error(f"Errore: {e}")
            else:
                st.warning("Manca folium - carica requirements.txt")
                if st.session_state.post:
                    try:
                        df_map=pd.DataFrame([{'lat':p.get('Lat',45.8205),'lon':p.get('Lon',8.8250)} for p in st.session_state.post])
                        st.map(df_map)
                    except Exception:
                        pass

elif scelta=='Libreria Icone':
    torna()
    st.markdown("## LIBRERIA ICONE - A.N.A. NUCLEO VOLONTARI DI PROTEZIONE CIVILE SEZIONE DI VARESE")
    st.info("Form ripristinato come stamattina")
    c1,c2=st.columns([1,1])
    with c1:
        with st.form("form_icone",clear_on_submit=True):
            i_nome=st.text_input("Nome icona *")
            i_cat=st.selectbox("Categoria",["COC","Campo base","Magazzino","Sede","Mezzo","Volontario","Altro"])
            i_file=st.file_uploader("Carica icona",type=['png','jpg','jpeg','svg'])
            i_colore=st.color_picker("Colore",value="#0e7a3d")
            i_desc=st.text_area("Descrizione")
            btn_i=st.form_submit_button("SALVA ICONA",use_container_width=True,type="primary")
            if btn_i:
                if i_nome:
                    fp_icona=""
                    if i_file:
                        try:
                            os.makedirs('icone',exist_ok=True)
                            fp_icona=f"icone/{i_nome.replace(' ','_')}_{i_file.name}"
                            with open(fp_icona,'wb') as f:
                                f.write(i_file.getbuffer())
                        except Exception:
                            pass
                    nuovo={'Nome':i_nome,'Categoria':i_cat,'File':fp_icona,'Colore':i_colore,'Descrizione':i_desc}
                    st.session_state.icone.append(nuovo)
                    save(FI,st.session_state.icone)
                    st.success(f"Icona {i_nome} salvata!")
                    st.rerun()
    with c2:
        if st.session_state.icone:
            df=pd.DataFrame(st.session_state.icone)
            st.markdown("### Elenco icone")
            event=st.dataframe(df,use_container_width=True,hide_index=False,on_select="rerun",selection_mode="single-row",key='tab_icone')
            if event and event.selection and event.selection.rows:
                idx=event.selection.rows[0]
                ico=st.session_state.icone[idx]
                st.markdown(f"### Dettaglio icona: {ico.get('Nome','')}")
                fp=ico.get('File','')
                if fp and os.path.exists(fp):
                    st.image(fp,width=100)
                st.write(f"Categoria: {ico.get('Categoria','')}")
                st.write(f"Colore: {ico.get('Colore','')}")
                st.write(f"Descrizione: {ico.get('Descrizione','')}")
                if st.button("ELIMINA ICONA"):
                    st.session_state.icone.pop(idx)
                    save(FI,st.session_state.icone)
                    st.rerun()
        else:
            st.info("Nessuna icona - Carica icone per mappa")

elif scelta=='Interventi Emergenza':
    torna()
    st.markdown("## INTERVENTI EMERGENZA - A.N.A. NUCLEO VOLONTARI DI PROTEZIONE CIVILE SEZIONE DI VARESE")
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
            odv_int=st.selectbox("ODV *",["A.N.A. NUCLEO VOLONTARI DI PROTEZIONE CIVILE SEZIONE DI VARESE","ANA Varese","PC Lombardia","CRI","Altro"])
        azione_int=st.text_area("Azione *",height=100)
        salva=st.form_submit_button("SALVA INTERVENTO",use_container_width=True,type="primary")
        if salva:
            if comune_int and via_int and azione_int:
                nuovo={"Data":str(data_int),"Ora":str(ora_int),"Comune":comune_int,"Via":via_int,"Civico":civico_int,"ODV":odv_int,"Azione":azione_int}
                st.session_state.interventi_lista.append(nuovo)
                save(FE,st.session_state.interventi_lista)
                st.success("Salvato!")
                st.rerun()
    if st.session_state.interventi_lista:
        df=pd.DataFrame(st.session_state.interventi_lista)
        st.dataframe(df,use_container_width=True,on_select="rerun",selection_mode="single-row",key='tab_int')

elif scelta=='Eventi':
    torna()
    st.markdown("## EVENTI - A.N.A. NUCLEO VOLONTARI DI PROTEZIONE CIVILE SEZIONE DI VARESE")
    st.info("Form Eventi ripristinato - mancava")
    c1,c2=st.columns([1,1])
    with c1:
        with st.form("form_eventi",clear_on_submit=True):
            ev_nome=st.text_input("Nome evento *")
            ev_data=st.date_input("Data evento")
            ev_comune=st.text_input("Comune")
            ev_luogo=st.text_input("Luogo")
            ev_tipo=st.selectbox("Tipo",["Esercitazione","Intervento","Formazione","Riunione","Altro"])
            ev_resp=st.text_input("Responsabile")
            ev_desc=st.text_area("Descrizione")
            btn_ev=st.form_submit_button("SALVA EVENTO",use_container_width=True,type="primary")
            if btn_ev:
                if ev_nome:
                    nuovo={'Nome':ev_nome,'Data':str(ev_data),'Comune':ev_comune,'Luogo':ev_luogo,'Tipo':ev_tipo,'Responsabile':ev_resp,'Descrizione':ev_desc}
                    st.session_state.eventi.append(nuovo)
                    save(FEV,st.session_state.eventi)
                    st.success(f"Evento {ev_nome} salvato!")
                    st.rerun()
    with c2:
        if st.session_state.eventi:
            df=pd.DataFrame(st.session_state.eventi)
            st.markdown("### Elenco eventi - Clicca riga per modificare")
            event=st.dataframe(df,use_container_width=True,hide_index=False,on_select="rerun",selection_mode="single-row",key='tab_eventi')
            if event and event.selection and event.selection.rows:
                idx=event.selection.rows[0]
                ev=st.session_state.eventi[idx]
                with st.expander(f"Dettaglio: {ev.get('Nome','')}",expanded=True):
                    st.write(f"Data: {ev.get('Data','')}")
                    st.write(f"Comune: {ev.get('Comune','')} Luogo: {ev.get('Luogo','')}")
                    st.write(f"Tipo: {ev.get('Tipo','')} Resp: {ev.get('Responsabile','')}")
                    st.write(f"Descrizione: {ev.get('Descrizione','')}")
                    if st.button("ELIMINA EVENTO",key='del_ev'):
                        st.session_state.eventi.pop(idx)
                        save(FEV,st.session_state.eventi)
                        st.rerun()
        else:
            st.info("Nessun evento")

elif scelta=='Check In':
    torna()
    st.markdown("## CHECK IN - A.N.A. NUCLEO VOLONTARI DI PROTEZIONE CIVILE SEZIONE DI VARESE")
    vol_list=[d.get('Nome','') for d in st.session_state.dati]
    if vol_list:
        with st.form("form_check",clear_on_submit=True):
            sel=st.selectbox("Volontario",vol_list)
            data_check=st.date_input("Data")
            ora_check=st.time_input("Ora")
            btn_c=st.form_submit_button("SALVA CHECK IN",use_container_width=True,type="primary")
            if btn_c:
                nuovo={'Volontario':sel,'Data':str(data_check),'Ora':str(ora_check)}
                st.session_state.check.append(nuovo)
                save(FC,st.session_state.check)
                st.success("Salvato!")
                st.rerun()
    if st.session_state.check:
        df=pd.DataFrame(st.session_state.check)
        st.dataframe(df,use_container_width=True)

elif scelta=='DB Radio':
    torna()
    st.markdown("## DB RADIO - A.N.A. NUCLEO VOLONTARI DI PROTEZIONE CIVILE SEZIONE DI VARESE")
    with st.form("form_radio",clear_on_submit=True):
        c1,c2=st.columns(2)
        with c1:
            r_modello=st.text_input("Modello *")
            r_matricola=st.text_input("Matricola *")
        with c2:
            r_freq=st.text_input("Frequenza")
            r_stato=st.selectbox("Stato",["Disponibile","In uso","Guasta"])
        btn_r=st.form_submit_button("SALVA RADIO",use_container_width=True,type="primary")
        if btn_r:
            if r_modello and r_matricola:
                nuovo={'Modello':r_modello,'Matricola':r_matricola,'Frequenza':r_freq,'Stato':r_stato}
                st.session_state.radio.append(nuovo)
                save(FR,st.session_state.radio)
                st.success("Salvata!")
                st.rerun()
    if st.session_state.radio:
        df=pd.DataFrame(st.session_state.radio)
        st.dataframe(df,use_container_width=True)

elif scelta=='Consegna Radio':
    torna()
    st.markdown("## CONSEGNA RADIO - A.N.A. NUCLEO VOLONTARI DI PROTEZIONE CIVILE SEZIONE DI VARESE")
    vol_list=[d.get('Nome','') for d in st.session_state.dati]
    radio_list=[r.get('Matricola','') for r in st.session_state.radio]
    if vol_list and radio_list:
        with st.form("form_cons",clear_on_submit=True):
            sel_vol=st.selectbox("Volontario",vol_list)
            sel_radio=st.selectbox("Radio",radio_list)
            data_cons=st.date_input("Data consegna")
            btn_cons=st.form_submit_button("SALVA CONSEGNA",use_container_width=True,type="primary")
            if btn_cons:
                nuovo={'Volontario':sel_vol,'Radio':sel_radio,'Data':str(data_cons)}
                st.session_state.cons.append(nuovo)
                save(FR2,st.session_state.cons)
                st.success("Salvata!")
                st.rerun()
    if st.session_state.cons:
        df=pd.DataFrame(st.session_state.cons)
        st.dataframe(df,use_container_width=True)

elif scelta=='Backup':
    torna()
    st.markdown("## BACKUP - A.N.A. NUCLEO VOLONTARI DI PROTEZIONE CIVILE SEZIONE DI VARESE")
    st.warning("Seleziona i dati dei vari form per export/import")
    tab_exp,tab_imp,tab_all=st.tabs(["EXPORT SELEZIONE","IMPORT SELEZIONE","COMPLETO"])
    with tab_exp:
        st.markdown("### Seleziona i form da esportare")
        c1,c2,c3=st.columns(3)
        with c1:
            exp_vol=st.checkbox("Volontari",value=True,key='exp_c_vol')
            exp_post=st.checkbox("Postazioni Mappa",value=True,key='exp_c_post')
            exp_icone=st.checkbox("Libreria Icone",value=True,key='exp_c_icone')
        with c2:
            exp_int=st.checkbox("Interventi Emergenza",value=True,key='exp_c_int')
            exp_eventi=st.checkbox("Eventi",value=True,key='exp_c_eventi')
            exp_check=st.checkbox("Check In",value=True,key='exp_c_check')
        with c3:
            exp_radio=st.checkbox("DB Radio",value=True,key='exp_c_radio')
            exp_cons=st.checkbox("Consegna Radio",value=True,key='exp_c_cons')
        st.divider()
        c1,c2,c3=st.columns(3)
        with c1:
            if exp_vol and st.session_state.dati:
                st.download_button('EXPORT VOLONTARI',export_excel(pd.DataFrame(st.session_state.dati)),file_name='Volontari.xlsx',use_container_width=True,key='exp_vol')
                st.caption(f"{len(st.session_state.dati)} volontari")
            if exp_post and st.session_state.post:
                st.download_button('EXPORT MAPPA',export_excel(pd.DataFrame(st.session_state.post)),file_name='Mappa.xlsx',use_container_width=True,key='exp_mappa')
        with c2:
            if exp_icone and st.session_state.icone:
                st.download_button('EXPORT ICONE',export_excel(pd.DataFrame(st.session_state.icone)),file_name='Icone.xlsx',use_container_width=True,key='exp_icone')
            if exp_int and st.session_state.interventi_lista:
                st.download_button('EXPORT INTERVENTI',export_excel(pd.DataFrame(st.session_state.interventi_lista)),file_name='Interventi.xlsx',use_container_width=True,key='exp_int')
            if exp_eventi and st.session_state.eventi:
                st.download_button('EXPORT EVENTI',export_excel(pd.DataFrame(st.session_state.eventi)),file_name='Eventi.xlsx',use_container_width=True,key='exp_eventi')
        with c3:
            if exp_check and st.session_state.check:
                st.download_button('EXPORT CHECK IN',export_excel(pd.DataFrame(st.session_state.check)),file_name='CheckIn.xlsx',use_container_width=True,key='exp_check')
            if exp_radio and st.session_state.radio:
                st.download_button('EXPORT RADIO',export_excel(pd.DataFrame(st.session_state.radio)),file_name='Radio.xlsx',use_container_width=True,key='exp_radio')
            if exp_cons and st.session_state.cons:
                st.download_button('EXPORT CONSEGNA',export_excel(pd.DataFrame(st.session_state.cons)),file_name='Consegna.xlsx',use_container_width=True,key='exp_cons')
    with tab_imp:
        st.markdown("### Seleziona i form da importare")
        c1,c2=st.columns(2)
        with c1:
            up_vol=st.file_uploader('Import Volontari',type=['xlsx'],key='up_vol')
            if up_vol:
                df_up=pd.read_excel(up_vol)
                st.dataframe(df_up.head(),use_container_width=True)
                if st.button(f'IMPORTA {len(df_up)} VOLONTARI',key='imp_vol',use_container_width=True,type="primary"):
                    for _,row in df_up.iterrows():
                        st.session_state.dati.append(row.to_dict())
                    save(FD,st.session_state.dati)
                    st.success("Importati!")
                    st.rerun()
            up_post=st.file_uploader('Import Mappa Postazioni',type=['xlsx'],key='up_post')
            if up_post:
                df_up=pd.read_excel(up_post)
                if st.button(f'IMPORTA {len(df_up)} POSTAZIONI',key='imp_post',use_container_width=True,type="primary"):
                    for _,row in df_up.iterrows():
                        st.session_state.post.append(row.to_dict())
                    save(FP,st.session_state.post)
                    st.success("Importate!")
                    st.rerun()
            up_icone=st.file_uploader('Import Icone',type=['xlsx'],key='up_icone')
            if up_icone:
                df_up=pd.read_excel(up_icone)
                if st.button(f'IMPORTA {len(df_up)} ICONE',key='imp_icone',use_container_width=True,type="primary"):
                    for _,row in df_up.iterrows():
                        st.session_state.icone.append(row.to_dict())
                    save(FI,st.session_state.icone)
                    st.success("Importate!")
                    st.rerun()
            up_int=st.file_uploader('Import Interventi',type=['xlsx'],key='up_int')
            if up_int:
                df_up=pd.read_excel(up_int)
                if st.button(f'IMPORTA {len(df_up)} INTERVENTI',key='imp_int',use_container_width=True,type="primary"):
                    for _,row in df_up.iterrows():
                        st.session_state.interventi_lista.append(row.to_dict())
                    save(FE,st.session_state.interventi_lista)
                    st.success("Importati!")
                    st.rerun()
        with c2:
            up_eventi=st.file_uploader('Import Eventi',type=['xlsx'],key='up_eventi')
            if up_eventi:
                df_up=pd.read_excel(up_eventi)
                st.dataframe(df_up.head(),use_container_width=True)
                if st.button(f'IMPORTA {len(df_up)} EVENTI',key='imp_eventi',use_container_width=True,type="primary"):
                    for _,row in df_up.iterrows():
                        st.session_state.eventi.append(row.to_dict())
                    save(FEV,st.session_state.eventi)
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
            up_radio=st.file_uploader('Import DB Radio',type=['xlsx'],key='up_radio')
            if up_radio:
                df_up=pd.read_excel(up_radio)
                if st.button(f'IMPORTA {len(df_up)} RADIO',key='imp_radio',use_container_width=True,type="primary"):
                    for _,row in df_up.iterrows():
                        st.session_state.radio.append(row.to_dict())
                    save(FR,st.session_state.radio)
                    st.success("Importate!")
                    st.rerun()
            up_cons=st.file_uploader('Import Consegna Radio',type=['xlsx'],key='up_cons')
            if up_cons:
                df_up=pd.read_excel(up_cons)
                if st.button(f'IMPORTA {len(df_up)} CONSEGNE',key='imp_cons',use_container_width=True,type="primary"):
                    for _,row in df_up.iterrows():
                        st.session_state.cons.append(row.to_dict())
                    save(FR2,st.session_state.cons)
                    st.success("Importate!")
                    st.rerun()
    with tab_all:
        st.markdown("### Backup completo con selezione")
        c1,c2=st.columns(2)
        with c1:
            sel_vol=st.checkbox("Volontari",value=True,key='all_vol')
            sel_post=st.checkbox("Mappa",value=True,key='all_post')
            sel_icone=st.checkbox("Icone",value=True,key='all_icone')
            sel_int=st.checkbox("Interventi",value=True,key='all_int')
        with c2:
            sel_eventi=st.checkbox("Eventi",value=True,key='all_eventi')
            sel_check=st.checkbox("Check In",value=True,key='all_check')
            sel_radio=st.checkbox("Radio",value=True,key='all_radio')
            sel_cons=st.checkbox("Consegna",value=True,key='all_cons')
        if st.button('CREA BACKUP COMPLETO SELEZIONATO',type='primary',use_container_width=True):
            out=BytesIO()
            with pd.ExcelWriter(out,engine='openpyxl') as writer:
                if sel_vol and st.session_state.dati:
                    pd.DataFrame(st.session_state.dati).to_excel(writer,sheet_name='Volontari',index=False)
                if sel_post and st.session_state.post:
                    pd.DataFrame(st.session_state.post).to_excel(writer,sheet_name='Mappa',index=False)
                if sel_icone and st.session_state.icone:
                    pd.DataFrame(st.session_state.icone).to_excel(writer,sheet_name='Icone',index=False)
                if sel_int and st.session_state.interventi_lista:
                    pd.DataFrame(st.session_state.interventi_lista).to_excel(writer,sheet_name='Interventi',index=False)
                if sel_eventi and st.session_state.eventi:
                    pd.DataFrame(st.session_state.eventi).to_excel(writer,sheet_name='Eventi',index=False)
                if sel_check and st.session_state.check:
                    pd.DataFrame(st.session_state.check).to_excel(writer,sheet_name='CheckIn',index=False)
                if sel_radio and st.session_state.radio:
                    pd.DataFrame(st.session_state.radio).to_excel(writer,sheet_name='DBRadio',index=False)
                if sel_cons and st.session_state.cons:
                    pd.DataFrame(st.session_state.cons).to_excel(writer,sheet_name='ConsegnaRadio',index=False)
            st.session_state['bk_all']=out.getvalue()
            st.success('Backup creato con selezione!')
            st.balloons()
        if 'bk_all' in st.session_state:
            st.download_button('SCARICA BACKUP COMPLETO SELEZIONATO',st.session_state['bk_all'],file_name='BACKUP_COMPLETO_SELEZIONATO.xlsx',use_container_width=True,type='primary')

elif scelta=='Tesserino':
    torna()
    st.markdown("## TESSERINO - A.N.A. NUCLEO VOLONTARI DI PROTEZIONE CIVILE SEZIONE DI VARESE")
    st.info("NITIDO PICCOLO 860x540 - Foto + ODV + Barcode CF")
    vol_list=[d.get('Nome','') for d in st.session_state.dati]
    if vol_list:
        df=pd.DataFrame(st.session_state.dati)
        st.markdown("**CLICCA RIGA PER GENERARE TESSERINO NITIDO**")
        event=st.dataframe(df,use_container_width=True,on_select="rerun",selection_mode="single-row",key='tab_tess')
        if event and event.selection and event.selection.rows:
            idx=event.selection.rows[0]
            vol=st.session_state.dati[idx]
            st.divider()
            c1,c2=st.columns([1,2])
            with c1:
                fp=vol.get('FotoFile','')
                if fp and os.path.exists(fp):
                    st.image(fp,width=200)
            with c2:
                tess=crea_tess(vol,vol.get('FotoFile',''),"Tesserino-Ezio.JPG" if os.path.exists("Tesserino-Ezio.JPG") else None)
                if tess:
                    st.image(tess,use_container_width=True)
                    st.download_button('SCARICA TESSERINO NITIDO PICCOLO',tess,file_name=f"Tesserino_{vol.get('Nome','')}_NITIDO.png",mime='image/png',type='primary',use_container_width=True)
                    st.download_button('SCARICA QUELLO SOTTO OK',tess,file_name=f"Tesserino_{vol.get('Nome','')}_SOTTO.png",mime='image/png',use_container_width=True,key='sotto2')
    else:
        st.warning("Nessun volontario")

else:
    torna()
    st.markdown(f"### {scelta} - A.N.A. NUCLEO VOLONTARI DI PROTEZIONE CIVILE SEZIONE DI VARESE")
    st.info(f"Form {scelta} OK")