import streamlit as st
import pandas as pd
from io import BytesIO
import os, json, hashlib, requests
from datetime import datetime, date

try:
    import folium
    from streamlit_folium import st_folium
    HAS = True
except:
    HAS = False

try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PIL = True
except:
    HAS_PIL = False

st.set_page_config(page_title="ANA Varese", layout="wide")

st.markdown("""
<style>
.block-container{padding-top:20px!important;max-width:100%!important;}
.stForm{background:#e8f5e9!important;border:2px solid #0e7a3d!important;}
.stForm label{color:#000!important;font-weight:bold!important;font-family:Times New Roman!important;}
.stButton>button{background:#0e7a3d!important;color:white!important;font-weight:bold!important;}
</style>
""", unsafe_allow_html=True)

def load(f,d):
    try:
        if os.path.exists(f):
            with open(f,'r',encoding='utf-8') as fh:
                return json.load(fh)
    except:
        pass
    return d

def save(f,d):
    try:
        with open(f,'w',encoding='utf-8') as fh:
            json.dump(d,fh,indent=2)
    except:
        pass

def hp(p):
    return hashlib.sha256(p.encode()).hexdigest()

def gaddr(lat,lon):
    try:
        u=f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=jsonv2&accept-language=it"
        r=requests.get(u,headers={'User-Agent':'ana-varese'},timeout=8)
        if r.status_code==200:
            j=r.json()
            a=j.get('address',{})
            com=a.get('city') or a.get('town') or a.get('village') or a.get('municipality') or ''
            via=a.get('road') or ''
            num=a.get('house_number') or ''
            return com,(via+' '+num).strip()
    except:
        pass
    return '',''

def fmt_date(d):
    if isinstance(d,date):
        return d.strftime("%d/%m/%Y")
    return str(d)

def make_pdf_simple(title, df):
    try:
        lines=[]
        lines.append(title)
        lines.append(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')} - ANA Varese")
        lines.append("")
        lines.append(f"Totale: {len(df) if df is not None else 0}")
        lines.append("")
        if df is not None and not df.empty:
            cols=list(df.columns)[:6]
            lines.append(" | ".join(cols))
            lines.append("-"*80)
            for _,row in df.head(60).iterrows():
                vals=[str(row.get(c,''))[:20].replace('(','').replace(')','') for c in cols]
                lines.append(" | ".join(vals))
        content="BT\n/F1 9 Tf\n50 800 Td\n"
        for i,line in enumerate(lines):
            safe=line.replace("\\","").replace("(","").replace(")","")[:120]
            if i==0:
                content+=f"({safe}) Tj\n"
            else:
                content+=f"0 -12 Td\n({safe}) Tj\n"
        content+="ET\n"
        cb=content.encode('latin-1', errors='ignore')
        pdf=BytesIO()
        pdf.write(b"%PDF-1.4\n")
        offs=[]
        offs.append(pdf.tell())
        pdf.write(b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")
        offs.append(pdf.tell())
        pdf.write(b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n")
        offs.append(pdf.tell())
        pdf.write(b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>\nendobj\n")
        offs.append(pdf.tell())
        pdf.write(b"4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n")
        offs.append(pdf.tell())
        pdf.write(f"5 0 obj\n<< /Length {len(cb)} >>\nstream\n".encode())
        pdf.write(cb)
        pdf.write(b"\nendstream\nendobj\n")
        xref=pdf.tell()
        pdf.write(f"xref\n0 {len(offs)+1}\n0000000000 65535 f \n".encode())
        for off in offs:
            pdf.write(f"{off:010d} 00000 n \n".encode())
        pdf.write(f"trailer\n<< /Size {len(offs)+1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF".encode())
        return pdf.getvalue()
    except Exception as e:
        st.error(f"Errore PDF: {e}")
        return None

def make_pdf(title, df):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib import colors
        buf=BytesIO()
        doc=SimpleDocTemplate(buf,pagesize=A4,leftMargin=15,rightMargin=15,topMargin=20,bottomMargin=20)
        styles=getSampleStyleSheet()
        story=[]
        story.append(Paragraph(f"<b>{title}</b>",styles['Title']))
        story.append(Spacer(1,12))
        story.append(Paragraph(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')} - ANA Varese",styles['Normal']))
        story.append(Spacer(1,12))
        if df is not None and not df.empty:
            cols=list(df.columns)[:7]
            data=[cols]
            for _,row in df.head(50).iterrows():
                data.append([str(row.get(c,''))[:25] for c in cols])
            t=Table(data,repeatRows=1)
            t.setStyle(TableStyle([
                ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#0e7a3d')),
                ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
                ('ALIGN',(0,0),(-1,-1),'LEFT'),
                ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
                ('FONTSIZE',(0,0),(-1,-1),7),
                ('GRID',(0,0),(-1,-1),0.5,colors.grey),
            ]))
            story.append(t)
        else:
            story.append(Paragraph("Nessun dato",styles['Normal']))
        doc.build(story)
        buf.seek(0)
        return buf.getvalue()
    except ImportError:
        return make_pdf_simple(title, df)
    except:
        return make_pdf_simple(title, df)

def export_excel(df):
    out=BytesIO()
    with pd.ExcelWriter(out,engine='openpyxl') as writer:
        df.to_excel(writer,index=False)
    return out.getvalue()

def crea_barcode_cf(cf):
    try:
        import barcode
        from barcode.writer import ImageWriter
        if not cf:
            cf="0000000000000000"
        cf_clean=cf.replace(" ","").upper()[:16]
        code=barcode.get('code128', cf_clean, writer=ImageWriter())
        buf=BytesIO()
        code.write(buf)
        buf.seek(0)
        return buf.getvalue()
    except:
        try:
            from PIL import Image, ImageDraw
            W,H=300,80
            img=Image.new('RGB',(W,H),'white')
            d=ImageDraw.Draw(img)
            if not cf:
                cf="0000000000000000"
            x=5
            for c in cf[:16]:
                w=ord(c)%5+1
                w=w*2
                if x+w<W-5:
                    d.rectangle([x,5,x+w,H-20], fill='black')
                x+=w+2
            buf=BytesIO()
            img.save(buf,format='PNG')
            buf.seek(0)
            return buf.getvalue()
        except:
            return None

def crea_tesserino_identico(vol_data, foto_path=None, template_path=None):
    try:
        if not HAS_PIL:
            return None
        if template_path and os.path.exists(template_path):
            base=Image.open(template_path).convert("RGB")
            W,H=base.size
            tess=base.copy()
            draw=ImageDraw.Draw(tess)
        else:
            W,H=860,540
            tess=Image.new('RGB',(W,H),'white')
            draw=ImageDraw.Draw(tess)
            draw.rectangle([0,0,W-1,H-1], outline='black', width=2)
        try:
            font_name=ImageFont.truetype("arialbd.ttf",20)
            font_odv=ImageFont.truetype("arial.ttf",14)
            font_small=ImageFont.truetype("arial.ttf",11)
        except:
            font_name=ImageFont.load_default()
            font_odv=ImageFont.load_default()
            font_small=ImageFont.load_default()
        W,H=tess.size
        foto_x=int(W*0.015)
        foto_y=int(H*0.22)
        foto_w=int(W*0.27)
        foto_h=int(H*0.58)
        if foto_path and os.path.exists(foto_path):
            try:
                draw.rectangle([foto_x,foto_y,foto_x+foto_w,foto_y+foto_h], fill='white', outline='black', width=2)
                foto=Image.open(foto_path).convert("RGB").resize((foto_w,foto_h))
                tess.paste(foto, (foto_x,foto_y))
                draw.rectangle([foto_x,foto_y,foto_x+foto_w,foto_y+foto_h], outline='black', width=2)
            except:
                pass
        nome_x=int(W*0.38)
        nome_y=int(H*0.36)
        draw.rectangle([nome_x,nome_y-5,nome_x+int(W*0.55),nome_y+int(H*0.15)], fill='white')
        nome_completo=vol_data.get('Nome','').upper()
        draw.text((nome_x,nome_y), nome_completo, fill='black', font=font_name)
        odv=vol_data.get('ODV','A.N.A. Sezione di Varese')
        if not odv or odv=='Altro':
            odv='A.N.A. Sezione di Varese'
        odv_y=nome_y+int(H*0.12)
        draw.rectangle([nome_x,odv_y-2,nome_x+int(W*0.5),odv_y+int(H*0.08)], fill='white')
        draw.text((nome_x,odv_y), odv, fill='black', font=font_odv)
        tessera=vol_data.get('Tessera','')
        if tessera:
            tess_y=odv_y+int(H*0.07)
            draw.rectangle([nome_x,tess_y-2,nome_x+int(W*0.5),tess_y+int(H*0.06)], fill='white')
            draw.text((nome_x,tess_y), f"PER {odv} - {tessera}", fill='black', font=font_small)
        barcode_x=int(W*0.62)
        barcode_y=int(H*0.73)
        barcode_w=int(W*0.35)
        barcode_h=int(H*0.15)
        draw.rectangle([barcode_x,barcode_y,barcode_x+barcode_w,barcode_y+barcode_h], fill='white', outline='white')
        cf_barcode=vol_data.get('CF','')
        if not cf_barcode:
            cf_barcode=vol_data.get('Nome','').replace(' ','').upper()[:16]
        barcode_data=crea_barcode_cf(cf_barcode)
        if barcode_data:
            try:
                bar_img=Image.open(BytesIO(barcode_data)).convert("RGB").resize((barcode_w,barcode_h))
                tess.paste(bar_img, (barcode_x,barcode_y))
            except:
                pass
        buf=BytesIO()
        tess.save(buf, format='PNG')
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
    ('dati',[]),('post',[]),('icone',[]),
    ('tip',[]),('odv',[]),('emerg',[]),
    ('check',[]),('radio',[]),('cons',[]),
    ('menu','Dashboard'),('auth',False),
    ('lat',45.8205),('lon',8.8250),
    ('com',''),('via',''),
    ('sel',-1),('zoom',16),
    ('clat',None),('clon',None),
    ('prev',-1),('exp1',False),
    ('exp2',False),('exp3',False),
    ('popup_shown',False),
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
    st.session_state.icone=[{'nome':'Presidio','col':'blue','file':''},{'nome':'Blocco','col':'red','file':''}]
    save(FI,st.session_state.icone)

def header():
    c1,c2=st.columns([1,5])
    with c1:
        try:
            st.image("logo.png",width=130)
        except:
            st.write("ANA")
    with c2:
        st.markdown("<div style='background:#a5d6a7;padding:15px;border-radius:8px;border:2px solid #0e7a3d;text-align:center;'><b style='color:#000;font-family:Times New Roman;font-size:28px;'>VOLONTARIATO<br>Sezione di Varese</b></div>", unsafe_allow_html=True)

def torna():
    if st.button('TORNA ALLA DASHBOARD'):
        st.session_state.menu='Dashboard'
        st.rerun()

# POPUP INIZIALE - SOLO TUA IMMAGINE FUMETTO
if st.session_state.popup_cfg.get('mostra',True) and not st.session_state.popup_shown:
    st.markdown(f"<h1 style='text-align:center;color:#0e7a3d;font-family:Times New Roman;'>{st.session_state.popup_cfg.get('titolo','ANA VARESE - VOLONTARIATO')}</h1>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align:center;color:#0e7a3d;'>{st.session_state.popup_cfg.get('sottotitolo','Ciao Ragazzi, Buon Lavoro!')}</h3>", unsafe_allow_html=True)
    st.divider()
    c1,c2,c3=st.columns([1,2,1])
    with c2:
        img_found=False
        for img_name in ['copertina.jpg','copertina_fumetto.jpg','mia_immagine_fumetto.jpg','benvenuto.jpg','copertina.png','logo.png']:
            if os.path.exists(img_name):
                try:
                    st.image(img_name,use_container_width=True)
                    if 'copertina' in img_name:
                        st.success(f"La tua immagine con fumetto: {img_name} - NO logo PC")
                    else:
                        st.warning(f"Trovato {img_name} - carica copertina.jpg con tua immagine fumetto")
                    img_found=True
                    if 'copertina' in img_name:
                        break
                except:
                    pass
        if not img_found:
            st.error("MANCA IMMAGINE PRIMA PAGINA!")
            st.warning("Carica la tua immagine con fumetto come copertina.jpg")
            st.markdown("<div style='background:#e8f5e9;padding:20px;border-radius:10px;text-align:center;border:2px dashed #0e7a3d;'><h3>QUI VA LA TUA IMMAGINE FUMETTO</h3><p>Carica copertina.jpg su GitHub</p></div>", unsafe_allow_html=True)
        st.divider()
        st.markdown(f"<div style='background:#e8f5e9;padding:15px;border-radius:10px;border:2px solid #0e7a3d;text-align:center;'><b style='font-size:20px;'>ANA Varese - Protezione Civile</b><br><b style='color:#0e7a3d;font-size:18px;'>Ciao Ragazzi, Buon Lavoro!</b><br><br>Volontari: {len(st.session_state.dati)} - Postazioni: {len(st.session_state.post)}<br>Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}</div>", unsafe_allow_html=True)
        st.divider()
        if st.button("ENTRA NEL SISTEMA", type="primary", use_container_width=True, key="entra_sistema"):
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
        with st.form('form_login'):
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
    st.markdown('<b>MENU COMPLETO</b>', unsafe_allow_html=True)
    opts=['Dashboard','Volontari','Mappa','Libreria Icone','Emergenza','Check In','DB Radio','Consegna Radio','Tesserino Regionale','Backup','Impostazioni Popup']
    sel=st.radio('Vai a',opts,index=0)
    if sel!=st.session_state.menu:
        st.session_state.menu=sel
        st.rerun()
    st.divider()
    if st.button('MOSTRA POPUP INIZIALE',use_container_width=True):
        st.session_state.popup_shown=False
        st.rerun()
    if st.button('LOGOUT',use_container_width=True):
        st.session_state.auth=False
        st.session_state.popup_shown=False
        st.rerun()

scelta=st.session_state.menu

if scelta=='Dashboard':
    st.markdown('<h3>DASHBOARD MENU COMPLETO - TUTTI I FORM</h3>', unsafe_allow_html=True)
    st.info("Clicca i tasti qui sotto per aprire i form - ora funzionano tutti!")
    c1,c2,c3=st.columns(3)
    with c1:
        st.markdown("**PRINCIPALI**")
        if st.button('VOLONTARI',use_container_width=True,key='dash_vol'):
            st.session_state.menu='Volontari'
            st.rerun()
        if st.button('MAPPA',use_container_width=True,key='dash_mappa'):
            st.session_state.menu='Mappa'
            st.rerun()
        if st.button('TESSERINO REGIONALE',use_container_width=True,key='dash_tess',type="primary"):
            st.session_state.menu='Tesserino Regionale'
            st.rerun()
        if st.button('LIBRERIA ICONE',use_container_width=True,key='dash_icone'):
            st.session_state.menu='Libreria Icone'
            st.rerun()
    with c2:
        st.markdown("**OPERATIVI**")
        if st.button('EMERGENZA',use_container_width=True,key='dash_emerg'):
            st.session_state.menu='Emergenza'
            st.rerun()
        if st.button('CHECK IN',use_container_width=True,key='dash_check'):
            st.session_state.menu='Check In'
            st.rerun()
        if st.button('DB RADIO',use_container_width=True,key='dash_radio'):
            st.session_state.menu='DB Radio'
            st.rerun()
        if st.button('CONSEGNA RADIO',use_container_width=True,key='dash_cons'):
            st.session_state.menu='Consegna Radio'
            st.rerun()
    with c3:
        st.markdown("**SISTEMA**")
        if st.button('BACKUP',use_container_width=True,key='dash_backup'):
            st.session_state.menu='Backup'
            st.rerun()
        if st.button('IMPOSTAZIONI POPUP',use_container_width=True,key='dash_popup'):
            st.session_state.menu='Impostazioni Popup'
            st.rerun()
        st.divider()
        st.metric('Volontari',len(st.session_state.dati))
        st.metric('Postazioni',len(st.session_state.post))
        st.metric('Emergenze',len(st.session_state.emerg))
        st.metric('Radio',len(st.session_state.radio))
    st.divider()
    st.markdown("**Anteprima immagine prima pagina (popup):**")
    for img_name in ['copertina.jpg','copertina_fumetto.jpg']:
        if os.path.exists(img_name):
            st.image(img_name,width=300,caption=f"{img_name} - tua immagine fumetto per prima pagina")
            break

elif scelta=='Volontari':
    torna()
    st.markdown('<h3>VOLONTARI - CON FOTO + CF + ODV + TESSERINO</h3>', unsafe_allow_html=True)
    tab1,tab2,tab3,tab4,tab5,tab6=st.tabs(['Anagrafica + Foto e CF','Contatti','Ruolo e ODV','Documenti','Elenco con Foto','Tesserino come Esempio'])
    with tab1:
        with st.form('form_vol_anag'):
            c1,c2=st.columns(2)
            with c1:
                a1=st.text_input('Nome *')
                a2=st.text_input('Cognome *')
                a_cf=st.text_input('Codice Fiscale * (per barcode tesserino)')
                a_nasc=st.date_input('Data Nascita (gg/mm/aaaa)',value=date(1990,1,1),format="DD/MM/YYYY")
                a_luogo=st.text_input('Luogo Nascita')
                a_foto=st.file_uploader('Foto Volontario * (JPG/PNG)',type=['jpg','png','jpeg'],key='foto_vol')
            with c2:
                a_ind=st.text_input('Indirizzo Residenza')
                a_com=st.text_input('Comune Residenza')
                a_prov=st.text_input('Provincia')
                a_cap=st.text_input('CAP')
                if a_foto is not None:
                    st.image(a_foto,width=150,caption='Anteprima foto')
            if st.form_submit_button('SALVA ANAGRAFICA + FOTO + CF'):
                if a1 and a2:
                    nc=a1+' '+a2
                    foto_path=''
                    if a_foto is not None:
                        os.makedirs('foto_volontari',exist_ok=True)
                        foto_path=f"foto_volontari/{nc.replace(' ','_')}_{a_foto.name}"
                        with open(foto_path,'wb') as f:
                            f.write(a_foto.getbuffer())
                    nuovo={'Nome':nc,'NomeSolo':a1,'Cognome':a2,'CF':a_cf,'DataNascita':fmt_date(a_nasc),'LuogoNascita':a_luogo,'Indirizzo':a_ind,'ComuneRes':a_com,'Prov':a_prov,'CAP':a_cap,'FotoFile':foto_path}
                    found=False
                    for i,d in enumerate(st.session_state.dati):
                        if d.get('Nome','')==nc:
                            if not foto_path:
                                nuovo['FotoFile']=d.get('FotoFile','')
                            st.session_state.dati[i].update(nuovo)
                            found=True
                    if not found:
                        st.session_state.dati.append(nuovo)
                    save(FD,st.session_state.dati)
                    st.success(f"Salvato {nc} con CF {a_cf} per barcode tesserino!")
                    st.rerun()
    with tab2:
        with st.form('form_vol_cont'):
            vol_list=[d.get('Nome','') for d in st.session_state.dati] or ['Nessun volontario']
            sel_vol=st.selectbox('Seleziona Volontario',vol_list,key='sel_vol_cont')
            for d in st.session_state.dati:
                if d.get('Nome','')==sel_vol:
                    fp=d.get('FotoFile','')
                    if fp and os.path.exists(fp):
                        st.image(fp,width=100,caption=f"Foto {sel_vol}")
            c1,c2=st.columns(2)
            with c1:
                b_cell=st.text_input('Cellulare *')
                b_tel=st.text_input('Telefono Fisso')
            with c2:
                b_email=st.text_input('Email')
                b_emerg=st.text_input('Contatto Emergenza')
            if st.form_submit_button('SALVA CONTATTI'):
                for i,d in enumerate(st.session_state.dati):
                    if d.get('Nome','')==sel_vol:
                        st.session_state.dati[i].update({'Cellulare':b_cell,'Telefono':b_tel,'Email':b_email,'ContEmerg':b_emerg})
                        save(FD,st.session_state.dati)
                        st.success(f"Contatti salvati per {sel_vol}")
                        st.rerun()
    with tab3:
        with st.form('form_vol_ruolo'):
            vol_list=[d.get('Nome','') for d in st.session_state.dati] or ['Nessun volontario']
            sel_vol2=st.selectbox('Seleziona Volontario',vol_list,key='sel_vol_ruolo')
            for d in st.session_state.dati:
                if d.get('Nome','')==sel_vol2:
                    fp=d.get('FotoFile','')
                    if fp and os.path.exists(fp):
                        st.image(fp,width=100)
            c1,c2=st.columns(2)
            with c1:
                c_ruolo=st.selectbox('Ruolo',['Volontario','Caposquadra','Coordinatore','Autista','Radio','Logistica','Segreteria','Sanitario','Altro'])
                c_gruppo=st.text_input('Gruppo / Squadra')
                c_data_iscr=st.date_input('Data Iscrizione (gg/mm/aaaa)',value=date.today(),format="DD/MM/YYYY")
            with c2:
                c_tessera=st.text_input('Numero Tessera')
                c_data_scad=st.date_input('Data Scadenza Tessera (gg/mm/aaaa)',value=date.today(),format="DD/MM/YYYY")
                c_disp=st.selectbox('Disponibilita',['Sempre','Weekend','Serale','Su chiamata'])
                c_odv=st.selectbox('ODV Appartenenza',['A.N.A. Sezione di Varese','Protezione Civile Varese','ANA Varese','Croce Rossa','Alpini','AIB','Altro'])
            if st.form_submit_button('SALVA RUOLO E ODV'):
                for i,d in enumerate(st.session_state.dati):
                    if d.get('Nome','')==sel_vol2:
                        st.session_state.dati[i].update({'Ruolo':c_ruolo,'Gruppo':c_gruppo,'DataIscrizione':fmt_date(c_data_iscr),'Tessera':c_tessera,'DataScadenza':fmt_date(c_data_scad),'Disponibilita':c_disp,'ODV':c_odv})
                        save(FD,st.session_state.dati)
                        st.success(f"Ruolo e ODV {c_odv} salvati per {sel_vol2}")
                        st.rerun()
    with tab4:
        with st.form('form_vol_doc'):
            vol_list=[d.get('Nome','') for d in st.session_state.dati] or ['Nessun volontario']
            sel_vol3=st.selectbox('Seleziona Volontario',vol_list,key='sel_vol_doc')
            for d in st.session_state.dati:
                if d.get('Nome','')==sel_vol3:
                    fp=d.get('FotoFile','')
                    if fp and os.path.exists(fp):
                        st.image(fp,width=100)
            d_pat=st.text_input('Patente - Categorie')
            d_scad_pat=st.date_input('Scadenza Patente (gg/mm/aaaa)',value=date.today(),format="DD/MM/YYYY")
            d_note=st.text_area('Note / Certificazioni')
            d_upload=st.file_uploader('Carica Documento',type=['pdf','png','jpg','jpeg'])
            d_foto_new=st.file_uploader('Cambia Foto Volontario',type=['jpg','png','jpeg'],key='foto_change')
            if st.form_submit_button('SALVA DOCUMENTI + FOTO'):
                fname=''
                foto_new_path=''
                if d_upload is not None:
                    os.makedirs('documenti',exist_ok=True)
                    fname=f"documenti/{sel_vol3}_{d_upload.name}"
                    with open(fname,'wb') as f:
                        f.write(d_upload.getbuffer())
                if d_foto_new is not None:
                    os.makedirs('foto_volontari',exist_ok=True)
                    foto_new_path=f"foto_volontari/{sel_vol3.replace(' ','_')}_{d_foto_new.name}"
                    with open(foto_new_path,'wb') as f:
                        f.write(d_foto_new.getbuffer())
                for i,d in enumerate(st.session_state.dati):
                    if d.get('Nome','')==sel_vol3:
                        upd={'Patente':d_pat,'ScadenzaPatente':fmt_date(d_scad_pat),'Note':d_note,'DocFile':fname}
                        if foto_new_path:
                            upd['FotoFile']=foto_new_path
                        st.session_state.dati[i].update(upd)
                        save(FD,st.session_state.dati)
                        st.success(f"Documenti salvati per {sel_vol3}")
                        st.rerun()
    with tab5:
        st.markdown('##### ELENCO VOLONTARI CON FOTO')
        if st.session_state.dati:
            for idx,d in enumerate(st.session_state.dati):
                c1,c2,c3=st.columns([1,3,1])
                with c1:
                    fp=d.get('FotoFile','')
                    if fp and os.path.exists(fp):
                        try:
                            st.image(fp,width=80)
                        except:
                            st.write('No foto')
                    else:
                        st.write('No foto')
                with c2:
                    nome=d.get('Nome','')
                    ruolo=d.get('Ruolo','')
                    odv=d.get('ODV','')
                    cf=d.get('CF','')
                    st.write(f"**{nome}** - {ruolo} - ODV: {odv} - CF: {cf}")
                with c3:
                    if st.button('Elimina',key=f'del_vol_{idx}'):
                        st.session_state.dati.pop(idx)
                        save(FD,st.session_state.dati)
                        st.rerun()
            st.divider()
            df=pd.DataFrame(st.session_state.dati)
            st.dataframe(df,use_container_width=True)
            c1,c2=st.columns(2)
            with c1:
                st.download_button('SCARICA EXCEL VOLONTARI',export_excel(df),file_name='Volontari.xlsx')
            with c2:
                if st.button('CREA PDF VOLONTARI',key='pdf_vol_btn'):
                    pdf=make_pdf("Volontari ANA Varese con Foto e CF",df)
                    if pdf:
                        st.session_state['pdf_vol']=pdf
                        st.success('PDF creato!')
            if 'pdf_vol' in st.session_state:
                st.download_button('SCARICA PDF VOLONTARI',st.session_state['pdf_vol'],file_name='Volontari_ANA_Varese.pdf',mime='application/pdf',use_container_width=True)
    with tab6:
        st.markdown('##### TESSERINO REGIONE LOMBARDIA - IDENTICO AL TUO ESEMPIO')
        st.info("Replica esatta: loghi e intestazione UGUALI, cambiano solo nome cognome, ODV, foto, barcode CF")
        vol_list=[d.get('Nome','') for d in st.session_state.dati] or []
        if not vol_list:
            st.warning('Nessun volontario - inserisci prima con foto e CF')
        else:
            sel_tess=st.selectbox('Seleziona Volontario per Tesserino',vol_list,key='sel_tess_vol')
            vol_data={}
            for d in st.session_state.dati:
                if d.get('Nome','')==sel_tess:
                    vol_data=d
                    break
            c1,c2=st.columns([1,2])
            with c1:
                fp=vol_data.get('FotoFile','')
                if fp and os.path.exists(fp):
                    st.image(fp,width=150,caption=f"Foto {sel_tess}")
                st.write(f"**Nome:** {vol_data.get('Nome','')}")
                st.write(f"**CF:** {vol_data.get('CF','')} (barcode)")
                st.write(f"**ODV:** {vol_data.get('ODV','A.N.A. Sezione di Varese')}")
                if os.path.exists("Tesserino-Ezio.JPG"):
                    st.image("Tesserino-Ezio.JPG",caption="Template originale con loghi UGUALI",use_container_width=True)
                else:
                    st.warning("Carica Tesserino-Ezio.JPG per loghi UGUALI")
                    up_tmpl=st.file_uploader('Carica template tesserino per loghi uguali',type=['jpg','png','jpeg'],key='tmpl_tess')
                    if up_tmpl is not None:
                        with open("Tesserino-Ezio.JPG",'wb') as f:
                            f.write(up_tmpl.getbuffer())
                        st.success('Template salvato!')
                        st.rerun()
            with c2:
                st.markdown('##### Anteprima Tesserino - IDENTICO')
                foto_path=vol_data.get('FotoFile','')
                tmpl_path="Tesserino-Ezio.JPG" if os.path.exists("Tesserino-Ezio.JPG") else None
                tess_bytes=crea_tesserino_identico(vol_data, foto_path, tmpl_path)
                if tess_bytes:
                    st.image(tess_bytes,use_container_width=True)
                    st.download_button('SCARICA TESSERINO PNG',tess_bytes,file_name=f"Tesserino_{sel_tess.replace(' ','_')}.png",mime='image/png',use_container_width=True,type='primary')

elif scelta=='Mappa':
    torna()
    st.markdown('<h3>MAPPA - CLICCA SU MAPPA PER INSERIRE VIA COMUNE LAT LON + MAPPA SOTTO CON POSTAZIONI + TASTI VAI</h3>', unsafe_allow_html=True)
    st.markdown("##### 1. CLICCA SULLA MAPPA PER SCEGLIERE POSTAZIONE - TI RIEMPIE VIA COMUNE LAT LON")
    icon_names=[it.get('nome','') for it in st.session_state.icone]
    sel_idx=0
    if icon_names:
        sel_str=st.selectbox('Icona PNG da libreria per questa postazione',icon_names,index=0)
        sel_idx=icon_names.index(sel_str)
        try:
            ic_sel=st.session_state.icone[sel_idx]
            fsel=ic_sel.get('file','')
            if fsel and os.path.exists(fsel):
                st.image(fsel,width=60,caption=f"Icona: {sel_str}")
        except:
            pass
    lat_c=st.session_state.lat
    lon_c=st.session_state.lon
    zm=st.session_state.zoom
    if HAS:
        m=folium.Map(location=[lat_c,lon_c],zoom_start=zm,tiles='OpenStreetMap')
        for idx,p in enumerate(st.session_state.post):
            try:
                la=float(p.get('Lat','0'))
                lo=float(p.get('Lon','0'))
                ficon=p.get('IconFile','')
                if ficon and os.path.exists(ficon):
                    ic=folium.CustomIcon(ficon,icon_size=(40,40))
                    folium.Marker([la,lo],popup=f"{p.get('Postazione','')} - {p.get('Comune','')}",icon=ic).add_to(m)
                else:
                    col='red' if idx==st.session_state.sel else 'blue'
                    folium.Marker([la,lo],popup=f"{p.get('Postazione','')} - {p.get('Comune','')}",icon=folium.Icon(color=col)).add_to(m)
            except:
                pass
        if st.session_state.clat is not None:
            folium.Marker([st.session_state.clat,st.session_state.clon],icon=folium.Icon(color='green',icon='plus')).add_to(m)
        out=st_folium(m,height=500,width=900,key='map_top')
        if out and out.get('last_clicked'):
            try:
                nl=out['last_clicked']['lat']
                ng=out['last_clicked']['lng']
                st.session_state.lat=nl
                st.session_state.lon=ng
                st.session_state.clat=nl
                st.session_state.clon=ng
                com,via=gaddr(nl,ng)
                st.session_state.com=com
                st.session_state.via=via
                st.session_state.sel=-1
                st.session_state.zoom=16
                st.rerun()
            except:
                pass
    c1,c2,c3,c4=st.columns(4)
    with c1:
        st.success(f"Comune: {st.session_state.com}")
    with c2:
        st.success(f"Via: {st.session_state.via}")
    with c3:
        st.info(f"Lat: {round(st.session_state.lat,6)}")
    with c4:
        st.info(f"Lon: {round(st.session_state.lon,6)}")
    st.divider()
    st.markdown("##### 2. MASCHERA - INSERISCI DATI POSTAZIONE (via comune lat lon gia compilati dopo click mappa)")
    vol_nomi=[d.get('Nome','') for d in st.session_state.dati] or ['Nessun volontario']
    with st.form('form_mappa'):
        c1,c2=st.columns(2)
        with c1:
            m1=st.text_input('Nome postazione *',placeholder='Es: Presidio 1 - Piazza Varese')
            m2=st.text_input('Comune *',value=st.session_state.com,help='Si compila automatico dopo click su mappa')
            m3=st.text_input('Via *',value=st.session_state.via,help='Si compila automatico dopo click su mappa')
            m4=st.selectbox('Tipologia *',st.session_state.tip)
            m_data=st.date_input('Data Attivazione (gg/mm/aaaa)',value=date.today(),format="DD/MM/YYYY")
        with c2:
            m5=st.text_input('Latitudine *',value=str(st.session_state.lat),help='Si compila automatico dopo click su mappa')
            m6=st.text_input('Longitudine *',value=str(st.session_state.lon),help='Si compila automatico dopo click su mappa')
            m8=st.selectbox('Responsabile *',vol_nomi)
            for d in st.session_state.dati:
                if d.get('Nome','')==m8:
                    fp=d.get('FotoFile','')
                    if fp and os.path.exists(fp):
                        st.image(fp,width=80,caption=f"Foto {m8}")
            m9=st.selectbox('ODV operante *',st.session_state.odv)
            m9_new=st.text_input('Nuova ODV se non in lista')
        if st.form_submit_button('SALVA POSTAZIONE',type="primary",use_container_width=True):
            if m1:
                odv_f=m9_new if m9_new else m9
                if odv_f not in st.session_state.odv and odv_f:
                    st.session_state.odv.append(odv_f)
                    save(FO,st.session_state.odv)
                ic=st.session_state.icone[sel_idx] if st.session_state.icone else {'col':'blue','file':'','nome':''}
                nuovo={'Postazione':m1,'Comune':m2,'Via':m3,'Lat':m5,'Lon':m6,'Responsabile':m8,'ODV':odv_f,'Tipo':m4,'DataAttivazione':fmt_date(m_data),'Icona':ic.get('nome',''),'IconFile':ic.get('file',''),'Col':ic.get('col','blue')}
                st.session_state.post.append(nuovo)
                save(FP,st.session_state.post)
                st.session_state.clat=None
                st.session_state.clon=None
                st.success(f"Salvata postazione {m1} a {m2} - {m3} - Lat {m5} Lon {m6}")
                st.rerun()
    st.divider()
    st.markdown("##### 3. MAPPA SOTTO CON TUTTE LE POSTAZIONI + TASTI CHE APRONO MAPPA NEL PUNTO GIUSTO")
    if st.session_state.post:
        if HAS:
            m2=folium.Map(location=[45.8205,8.8250],zoom_start=11,tiles='OpenStreetMap')
            for p in st.session_state.post:
                try:
                    la=float(p.get('Lat','0'))
                    lo=float(p.get('Lon','0'))
                    ficon=p.get('IconFile','')
                    if ficon and os.path.exists(ficon):
                        ic=folium.CustomIcon(ficon,icon_size=(40,40))
                        folium.Marker([la,lo],popup=f"{p.get('Postazione','')} - {p.get('Comune','')} {p.get('Via','')}",icon=ic).add_to(m2)
                    else:
                        folium.Marker([la,lo],popup=f"{p.get('Postazione','')} - {p.get('Comune','')}",icon=folium.Icon(color='blue')).add_to(m2)
                except:
                    pass
            st_folium(m2,height=450,width=900,key='map_all_postazioni')
        st.markdown("**Elenco postazioni - clicca VAI per centrare mappa sul punto giusto:**")
        for idx,p in enumerate(st.session_state.post):
            c1,c2,c3,c4,c5=st.columns([2,2,2,2,3])
            with c1:
                st.write(f"**{p.get('Postazione','')}**")
                st.caption(f"{p.get('Comune','')} - {p.get('Via','')}")
            with c2:
                st.write(f"Lat: {p.get('Lat','')}")
                st.write(f"Lon: {p.get('Lon','')}")
            with c3:
                st.write(f"Resp: {p.get('Responsabile','')}")
                for d in st.session_state.dati:
                    if d.get('Nome','')==p.get('Responsabile',''):
                        fp=d.get('FotoFile','')
                        if fp and os.path.exists(fp):
                            st.image(fp,width=50)
            with c4:
                st.write(f"ODV: {p.get('ODV','')}")
                st.write(f"Tipo: {p.get('Tipo','')}")
            with c5:
                col1,col2=st.columns(2)
                with col1:
                    if st.button('VAI',key=f'vai_{idx}',use_container_width=True):
                        try:
                            st.session_state.lat=float(p.get('Lat','0'))
                            st.session_state.lon=float(p.get('Lon','0'))
                            st.session_state.clat=float(p.get('Lat','0'))
                            st.session_state.clon=float(p.get('Lon','0'))
                            st.session_state.com=p.get('Comune','')
                            st.session_state.via=p.get('Via','')
                            st.session_state.sel=idx
                            st.session_state.zoom=18
                            st.rerun()
                        except:
                            st.error("Coordinate non valide")
                with col2:
                    if st.button('Elimina',key=f'del_post_{idx}',use_container_width=True):
                        st.session_state.post.pop(idx)
                        save(FP,st.session_state.post)
                        st.rerun()
            st.divider()
        df_post=pd.DataFrame(st.session_state.post)
        st.dataframe(df_post,use_container_width=True)
        c1,c2=st.columns(2)
        with c1:
            st.download_button('SCARICA EXCEL MAPPA',export_excel(df_post),file_name='Mappa_Postazioni.xlsx')
        with c2:
            if st.button('CREA PDF MAPPA',key='pdf_mappa_btn'):
                pdf=make_pdf("Mappa Postazioni ANA Varese - Con Via Comune Lat Lon",df_post)
                if pdf:
                    st.session_state['pdf_mappa']=pdf
                    st.success('PDF mappa creato!')
        if 'pdf_mappa' in st.session_state:
            st.download_button('SCARICA PDF MAPPA',st.session_state['pdf_mappa'],file_name='Mappa_Postazioni.pdf',mime='application/pdf')
    else:
        st.warning("Nessuna postazione - clicca sulla mappa in alto per iniziare")

elif scelta=='Libreria Icone':
    torna()
    st.markdown('#### LIBRERIA ICONE - UPLOAD PNG')
    with st.form('form_icone'):
        c1,c2=st.columns(2)
        with c1:
            n1=st.text_input('Nome icona *')
            n3=st.selectbox('Colore',['blue','red','green','orange','black'])
        with c2:
            up_file=st.file_uploader('Carica PNG',type=['png','jpg','jpeg'],key='single_png')
        if st.form_submit_button('SALVA ICONA'):
            if n1:
                fname=''
                if up_file is not None:
                    os.makedirs('icone',exist_ok=True)
                    fname=f"icone/{n1}_{up_file.name}"
                    with open(fname,'wb') as f:
                        f.write(up_file.getbuffer())
                nuovo={'nome':n1,'col':n3,'file':fname}
                st.session_state.icone.append(nuovo)
                save(FI,st.session_state.icone)
                st.success('Salvata')
                st.rerun()
    if st.session_state.icone:
        for idx,ic in enumerate(st.session_state.icone):
            c1,c2,c3,c4=st.columns([2,1,2,1])
            with c1:
                st.write(f"{ic.get('nome','')}")
            with c2:
                f=ic.get('file','')
                if f and os.path.exists(f):
                    try:
                        st.image(f,width=50)
                    except:
                        st.write('Img')
            with c3:
                st.write(ic.get('file',''))
            with c4:
                if st.button('Elimina',key=f'del_{idx}'):
                    st.session_state.icone.pop(idx)
                    save(FI,st.session_state.icone)
                    st.rerun()

elif scelta=='Emergenza':
    torna()
    st.markdown('#### EMERGENZA - DATA GG/MM/AAAA')
    with st.form('form_emerg'):
        c1,c2=st.columns(2)
        with c1:
            e1=st.text_input('Nome emergenza *')
            e2=st.text_input('Luogo *')
            e3=st.selectbox('Tipo',['Alluvione','Terremoto','Incendio','Neve','Altro'])
        with c2:
            e_data=st.date_input('Data Emergenza (gg/mm/aaaa)',value=date.today(),format="DD/MM/YYYY")
            e_data_fine=st.date_input('Data Fine Prevista (gg/mm/aaaa)',value=date.today(),format="DD/MM/YYYY")
            e_desc=st.text_area('Descrizione')
        if st.form_submit_button('SALVA EMERGENZA'):
            if e1:
                nuovo={'Emergenza':e1,'Luogo':e2,'Tipo':e3,'DataEmergenza':fmt_date(e_data),'DataFine':fmt_date(e_data_fine),'Desc':e_desc}
                st.session_state.emerg.append(nuovo)
                save(FE,st.session_state.emerg)
                st.success(f"Salvata {e1}")
                st.rerun()
    if st.session_state.emerg:
        df_emerg=pd.DataFrame(st.session_state.emerg)
        st.dataframe(df_emerg,use_container_width=True)
        st.download_button('SCARICA EXCEL EMERGENZE',export_excel(df_emerg),file_name='Emergenze.xlsx')

elif scelta=='Check In':
    torna()
    st.markdown('#### CHECK IN - DATA GG/MM/AAAA CON FOTO')
    vol_list=[d.get('Nome','') for d in st.session_state.dati] or ['Nessuno']
    with st.form('form_checkin'):
        c1,c2=st.columns(2)
        with c1:
            ch_data=st.date_input('Data Check In (gg/mm/aaaa)',value=date.today(),format="DD/MM/YYYY")
            ch_ora=st.time_input('Ora Check In')
        with c2:
            c2_sel=st.selectbox('Volontario',vol_list)
            for d in st.session_state.dati:
                if d.get('Nome','')==c2_sel:
                    fp=d.get('FotoFile','')
                    if fp and os.path.exists(fp):
                        st.image(fp,width=60)
            c3=st.selectbox('Stato',['Presente','Assente','In servizio','Fuori servizio'])
            c4=st.text_input('Luogo Servizio')
        if st.form_submit_button('REGISTRA CHECK IN'):
            nuovo={'Data':fmt_date(ch_data),'Ora':str(ch_ora),'Vol':c2_sel,'Stato':c3,'Luogo':c4}
            st.session_state.check.append(nuovo)
            save(FC,st.session_state.check)
            st.success(f"Check In {fmt_date(ch_data)} per {c2_sel}")
            st.rerun()
    if st.session_state.check:
        df_check=pd.DataFrame(st.session_state.check)
        st.dataframe(df_check,use_container_width=True)
        st.download_button('SCARICA EXCEL CHECK IN',export_excel(df_check),file_name='CheckIn.xlsx')

elif scelta=='DB Radio':
    torna()
    st.markdown('#### DB RADIO - TIPO DMR ANALOGICA TETRA')
    with st.form('form_radio'):
        c1,c2=st.columns(2)
        with c1:
            r1=st.text_input('Nome radio *')
            r2=st.text_input('Frequenza *')
            r_tipo=st.selectbox('Tipo Radio *',['ANALOGICA','DMR','TETRA','PMR','Altro'])
            r3=st.text_input('Canale')
        with c2:
            r_data=st.date_input('Data Acquisto (gg/mm/aaaa)',value=date.today(),format="DD/MM/YYYY")
            r_mod=st.text_input('Modello Radio')
            r4=st.text_input('Note')
        if st.form_submit_button('SALVA RADIO'):
            if r1:
                nuovo={'Radio':r1,'Freq':r2,'TipoRadio':r_tipo,'Canale':r3,'Modello':r_mod,'DataAcquisto':fmt_date(r_data),'Note':r4}
                st.session_state.radio.append(nuovo)
                save(FR,st.session_state.radio)
                st.success(f"Salvata radio {r1} Tipo {r_tipo}")
                st.rerun()
    if st.session_state.radio:
        df_radio=pd.DataFrame(st.session_state.radio)
        st.dataframe(df_radio,use_container_width=True)
        st.download_button('SCARICA EXCEL RADIO',export_excel(df_radio),file_name='DB_Radio.xlsx')

elif scelta=='Consegna Radio':
    torna()
    st.markdown('#### CONSEGNA RADIO - CON CAMPO CANALE + FOTO')
    vol_list=[d.get('Nome','') for d in st.session_state.dati] or ['Nessuno']
    radio_list=[r.get('Radio','') for r in st.session_state.radio] or ['Nessuna radio']
    with st.form('form_consegna'):
        c1,c2=st.columns(2)
        with c1:
            cr1=st.selectbox('Volontario',vol_list)
            for d in st.session_state.dati:
                if d.get('Nome','')==cr1:
                    fp=d.get('FotoFile','')
                    if fp and os.path.exists(fp):
                        st.image(fp,width=60)
            cr2=st.selectbox('Radio',radio_list)
            cr_canale=st.text_input('Canale *',placeholder='Es: CH 1 - Emergenza')
            cr_freq=st.text_input('Frequenza')
        with c2:
            cr3=st.date_input('Data Consegna (gg/mm/aaaa)',value=date.today(),format="DD/MM/YYYY")
            cr4=st.date_input('Data Riconsegna Prevista (gg/mm/aaaa)',value=date.today(),format="DD/MM/YYYY")
            cr5=st.selectbox('Stato',['Consegnata','Riconsegnata','In uso','Guasta'])
            cr6=st.text_area('Note')
        if st.form_submit_button('SALVA CONSEGNA RADIO'):
            nuovo={'Vol':cr1,'Radio':cr2,'Canale':cr_canale,'Frequenza':cr_freq,'DataConsegna':fmt_date(cr3),'DataRiconsegna':fmt_date(cr4),'Stato':cr5,'Note':cr6}
            st.session_state.cons.append(nuovo)
            save(FR2,st.session_state.cons)
            st.success(f"Radio {cr2} Canale {cr_canale} consegnata a {cr1}")
            st.rerun()
    if st.session_state.cons:
        df_cons=pd.DataFrame(st.session_state.cons)
        st.dataframe(df_cons,use_container_width=True)
        st.download_button('SCARICA EXCEL CONSEGNE',export_excel(df_cons),file_name='ConsegnaRadio.xlsx')

elif scelta=='Tesserino Regionale':
    torna()
    st.markdown('#### TESSERINO REGIONE LOMBARDIA - IDENTICO AL TUO ESEMPIO')
    st.success("Replica esatta: loghi e intestazione UGUALI al tuo esempio, cambiano solo nome cognome, ODV, foto e barcode CF")
    vol_list=[d.get('Nome','') for d in st.session_state.dati] or []
    if not vol_list:
        st.warning('Nessun volontario - inserisci prima in Volontari con foto e CF')
    else:
        sel_tess=st.selectbox('Seleziona Volontario per Tesserino Regionale',vol_list,key='sel_tess_reg2')
        vol_data={}
        for d in st.session_state.dati:
            if d.get('Nome','')==sel_tess:
                vol_data=d
                break
        c1,c2=st.columns([1,2])
        with c1:
            fp=vol_data.get('FotoFile','')
            if fp and os.path.exists(fp):
                st.image(fp,width=150,caption=f"Foto {sel_tess}")
            else:
                st.warning('Carica foto per tesserino identico')
            st.write(f"**Nome:** {vol_data.get('Nome','')}")
            st.write(f"**CF:** {vol_data.get('CF','')} (per barcode)")
            st.write(f"**ODV:** {vol_data.get('ODV','A.N.A. Sezione di Varese')}")
            if os.path.exists("Tesserino-Ezio.JPG"):
                st.image("Tesserino-Ezio.JPG",caption="Template originale con loghi UGUALI",use_container_width=True)
            else:
                st.warning("Carica Tesserino-Ezio.JPG per mantenere loghi e intestazione UGUALI identici")
        with c2:
            st.markdown('##### Anteprima Tesserino - IDENTICO al tuo esempio')
            st.caption("Loghi e intestazione UGUALI, cambiano solo: nome cognome, ODV, foto, barcode CF")
            foto_path=vol_data.get('FotoFile','')
            tmpl_path="Tesserino-Ezio.JPG" if os.path.exists("Tesserino-Ezio.JPG") else None
            tess_bytes=crea_tesserino_identico(vol_data, foto_path, tmpl_path)
            if tess_bytes:
                st.image(tess_bytes,use_container_width=True)
                st.download_button('SCARICA TESSERINO PNG',tess_bytes,file_name=f"Tesserino_{sel_tess.replace(' ','_')}_Regione_Lombardia.png",mime='image/png',use_container_width=True,type='primary')
        st.divider()
        if st.button('GENERA TUTTI I TESSERINI IN ZIP',type='primary',use_container_width=True):
            import zipfile
            zip_buf=BytesIO()
            with zipfile.ZipFile(zip_buf,'w') as zf:
                tmpl_path="Tesserino-Ezio.JPG" if os.path.exists("Tesserino-Ezio.JPG") else None
                for d in st.session_state.dati:
                    b=crea_tesserino_identico(d, d.get('FotoFile',''), tmpl_path)
                    if b:
                        zf.writestr(f"Tesserino_{d.get('Nome','').replace(' ','_')}.png", b)
            zip_buf.seek(0)
            st.download_button('SCARICA TUTTI I TESSERINI ZIP',zip_buf.getvalue(),file_name='Tesserini_Regione_Lombardia_Tutti.zip',mime='application/zip',use_container_width=True)

elif scelta=='Backup':
    torna()
    st.markdown('#### BACKUP - EXPORT SINGOLI + IMPORT TUTTI I FORM')
    if st.session_state.dati:
        df=pd.DataFrame(st.session_state.dati)
        st.download_button('EXPORT VOLONTARI EXCEL',export_excel(df),file_name='Volontari.xlsx',key='exp_vol',use_container_width=True)
        if st.button('CREA PDF VOLONTARI',key='pdf_vol_btn2',use_container_width=True):
            pdf=make_pdf("Volontari ANA Varese con Foto e CF",df)
            if pdf:
                st.session_state['pdf_bk_vol']=pdf
                st.success('PDF creato!')
        if 'pdf_bk_vol' in st.session_state:
            st.download_button('SCARICA PDF VOLONTARI',st.session_state['pdf_bk_vol'],file_name='Volontari.pdf',mime='application/pdf',key='pdf_vol_dl',use_container_width=True)
    st.divider()
    st.markdown("**IMPORT VOLONTARI con CF per barcode**")
    up_vol=st.file_uploader('Carica Excel Volontari',type=['xlsx'],key='up_vol')
    if up_vol is not None:
        try:
            df_up=pd.read_excel(up_vol)
            st.write(f"Trovati {len(df_up)} record")
            if st.button('IMPORTA VOLONTARI',key='imp_vol_btn',use_container_width=True):
                for _,row in df_up.iterrows():
                    st.session_state.dati.append(row.to_dict())
                save(FD,st.session_state.dati)
                st.success(f"Importati {len(df_up)} volontari")
                st.rerun()
        except Exception as e:
            st.error(f"Errore: {e}")

elif scelta=='Impostazioni Popup':
    torna()
    st.markdown('#### IMPOSTAZIONI POPUP - TUA IMMAGINE FUMETTO SOLO, NO LOGO PC')
    st.success("Popup con SOLO tua immagine con fumetto 'ciao ragazzi, buon lavoro' - NO logo PC")
    with st.form('form_popup'):
        p_titolo=st.text_input('Titolo Popup',value=st.session_state.popup_cfg.get('titolo','ANA VARESE - VOLONTARIATO'))
        p_sotto=st.text_input('Sottotitolo Popup',value=st.session_state.popup_cfg.get('sottotitolo','Ciao Ragazzi, Buon Lavoro!'))
        p_mostra=st.checkbox('Mostra popup all avvio',value=st.session_state.popup_cfg.get('mostra',True))
        if st.form_submit_button('SALVA IMPOSTAZIONI POPUP'):
            st.session_state.popup_cfg={'titolo':p_titolo,'sottotitolo':p_sotto,'mostra':p_mostra}
            save(FPOP,st.session_state.popup_cfg)
            st.success('Impostazioni salvate')
    st.divider()
    st.markdown('##### CARICA TUA IMMAGINE CON FUMETTO PER PRIMA PAGINA - POPUP INIZIALE')
    st.info("Questa immagine apparirà nella prima pagina (popup) - SOLO questa, NO logo PC")
    up_popup=st.file_uploader('Carica tua immagine con fumetto (JPG/PNG) - per prima pagina',type=['jpg','png','jpeg'],key='up_popup')
    if up_popup is not None:
        st.image(up_popup,use_container_width=True,caption="Anteprima tua immagine con fumetto - per prima pagina")
        if st.button('SALVA COME COPERTINA.JPG - SOLO TUA IMMAGINE FUMETTO',type='primary',use_container_width=True):
            with open('copertina.jpg','wb') as f:
                f.write(up_popup.getbuffer())
            st.success('Salvata come copertina.jpg! Ora prima pagina mostra SOLO tua immagine con fumetto, NO logo PC')
    st.divider()
    st.markdown("**File presenti:**")
    for img_name in ['copertina.jpg','copertina_fumetto.jpg','Tesserino-Ezio.JPG','logo.png']:
        if os.path.exists(img_name):
            st.write(f"✅ {img_name}")
            try:
                if 'copertina' in img_name:
                    st.image(img_name,width=400,caption=f"{img_name} - TUA IMMAGINE FUMETTO per prima pagina (NO logo PC)")
                elif 'Tesserino' in img_name:
                    st.image(img_name,width=400,caption=f"{img_name} - Template tesserino con loghi UGUALI")
                else:
                    st.image(img_name,width=200)
            except:
                pass
        else:
            st.write(f"❌ {img_name} mancante")
    if st.button('MOSTRA ANTEPRIMA POPUP CON TUA IMMAGINE FUMETTO',type='primary',use_container_width=True):
        st.session_state.popup_shown=False
        st.rerun()

else:
    torna()
    st.markdown(f"### {scelta} - IN COSTRUZIONE")
    st.info("Sezione in aggiornamento")
