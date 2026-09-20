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
            com=a.get('city') or a.get('town') or a.get('village') or ''
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

def crea_tesserino_regione(vol_data, foto_path=None, template_path=None):
    try:
        if not HAS_PIL:
            return None
        W,H=860,540
        tess=Image.new('RGB',(W,H),'white')
        draw=ImageDraw.Draw(tess)
        header_h=110
        try:
            if template_path and os.path.exists(template_path):
                tmpl=Image.open(template_path).convert("RGB")
                tw,th=tmpl.size
                header_crop=tmpl.crop((0,0,tw,int(th*0.35)))
                header_crop=header_crop.resize((W, header_h))
                tess.paste(header_crop, (0,0))
            else:
                draw.rectangle([0,0,W,header_h], fill='#f0f0f0')
                draw.rectangle([0,0,W,header_h], outline='black', width=1)
        except:
            pass
        draw.rectangle([0,0,W-1,H-1], outline='black', width=2)
        foto_x,foto_y,foto_w,foto_h=15,120,180,220
        if foto_path and os.path.exists(foto_path):
            try:
                foto=Image.open(foto_path).convert("RGB").resize((foto_w,foto_h))
                tess.paste(foto, (foto_x,foto_y))
                draw.rectangle([foto_x,foto_y,foto_x+foto_w,foto_y+foto_h], outline='black', width=2)
            except:
                draw.rectangle([foto_x,foto_y,foto_x+foto_w,foto_y+foto_h], fill='#c0c0c0', outline='black', width=2)
        else:
            draw.rectangle([foto_x,foto_y,foto_x+foto_w,foto_y+foto_h], fill='#c0c0c0', outline='black', width=2)
        try:
            font_name=ImageFont.truetype("arialbd.ttf",22)
            font_b=ImageFont.truetype("arial.ttf",16)
            font_s=ImageFont.truetype("arial.ttf",12)
            font_xs=ImageFont.truetype("arial.ttf",10)
        except:
            font_name=ImageFont.load_default()
            font_b=ImageFont.load_default()
            font_s=ImageFont.load_default()
            font_xs=ImageFont.load_default()
        x_text=220
        y_text=130
        nome=vol_data.get('Nome','').upper()
        draw.text((x_text,y_text), nome, fill='black', font=font_name)
        y_text+=35
        odv=vol_data.get('ODV','A.N.A. Sezione di Varese')
        if not odv or odv=='Altro':
            odv='A.N.A. Sezione di Varese'
        draw.text((x_text,y_text), odv, fill='black', font=font_b)
        y_text+=25
        tessera=vol_data.get('Tessera','')
        if tessera:
            draw.text((x_text,y_text), f"PER {odv} - Tess. {tessera}", fill='black', font=font_s)
        else:
            draw.text((x_text,y_text), f"PER {odv}", fill='black', font=font_s)
        y_text+=20
        cf=vol_data.get('CF','')
        if cf:
            draw.text((x_text,y_text), f"CF: {cf}", fill='black', font=font_s)
            y_text+=18
        draw.text((x_text,y_text), f"Rilasciato: {datetime.now().strftime('%d/%m/%Y')}", fill='black', font=font_xs)
        barcode_x=400
        barcode_y=360
        barcode_w=350
        barcode_h=100
        cf_barcode=vol_data.get('CF','') or vol_data.get('Nome','').replace(' ','').upper()[:16]
        barcode_data=crea_barcode_cf(cf_barcode)
        if barcode_data:
            try:
                bar_img=Image.open(BytesIO(barcode_data)).convert("RGB").resize((barcode_w,barcode_h))
                tess.paste(bar_img, (barcode_x,barcode_y))
            except:
                draw.rectangle([barcode_x,barcode_y,barcode_x+barcode_w,barcode_y+barcode_h], fill='white', outline='black', width=1)
        footer_y=H-25
        draw.rectangle([0,footer_y,W,H], fill='#e0e0e0')
        draw.text((10,footer_y+5), "AD USO ESCLUSIVO PER L'ATTIVITA' DI PROTEZIONE CIVILE", fill='black', font=font_xs)
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
    if st.button('TORNA'):
        st.session_state.menu='Dashboard'
        st.rerun()

if st.session_state.popup_cfg.get('mostra',True) and not st.session_state.popup_shown:
    st.markdown(f"<h1 style='text-align:center;color:#0e7a3d;font-family:Times New Roman;'>{st.session_state.popup_cfg.get('titolo','ANA VARESE')}</h1>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align:center;color:#0e7a3d;'>{st.session_state.popup_cfg.get('sottotitolo','Ciao Ragazzi, Buon Lavoro!')}</h3>", unsafe_allow_html=True)
    st.divider()
    c1,c2,c3=st.columns([1,2,1])
    with c2:
        for img_name in ['copertina.jpg','copertina_fumetto.jpg','mia_immagine_fumetto.jpg','copertina.png']:
            if os.path.exists(img_name):
                try:
                    st.image(img_name,use_container_width=True)
                    break
                except:
                    pass
        st.divider()
        st.markdown("<div style='background:#e8f5e9;padding:15px;border-radius:10px;border:2px solid #0e7a3d;text-align:center;'><b style='font-size:20px;'>ANA Varese - Protezione Civile</b><br><b style='color:#0e7a3d;'>Ciao Ragazzi, Buon Lavoro!</b><br><br>Volontari: "+str(len(st.session_state.dati))+"<br>"+datetime.now().strftime('%d/%m/%Y %H:%M')+"</div>", unsafe_allow_html=True)
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
    opts=['Dashboard','Volontari','Mappa','Tesserino Regionale','Backup','Impostazioni Popup']
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
    st.markdown('<h3>DASHBOARD</h3>', unsafe_allow_html=True)
    c1,c2,c3=st.columns(3)
    with c1:
        if st.button('VOLONTARI',use_container_width=True):
            st.session_state.menu='Volontari'
            st.rerun()
        if st.button('TESSERINO REGIONALE',use_container_width=True):
            st.session_state.menu='Tesserino Regionale'
            st.rerun()
    with c2:
        if st.button('MAPPA',use_container_width=True):
            st.session_state.menu='Mappa'
            st.rerun()
    with c3:
        st.metric('Vol',len(st.session_state.dati))
        st.metric('Post',len(st.session_state.post))

elif scelta=='Volontari':
    torna()
    st.markdown('<h3>VOLONTARI - CON FOTO + TESSERINO</h3>', unsafe_allow_html=True)
    tab1,tab2,tab3,tab4,tab5,tab6=st.tabs(['Anagrafica + Foto e CF','Contatti','Ruolo e ODV','Documenti','Elenco','Tesserino come Esempio'])

    with tab1:
        with st.form('form_vol_anag'):
            c1,c2=st.columns(2)
            with c1:
                a1=st.text_input('Nome *')
                a2=st.text_input('Cognome *')
                a_cf=st.text_input('Codice Fiscale * (per barcode tesserino)')
                a_nasc=st.date_input('Data Nascita',value=date(1990,1,1),format="DD/MM/YYYY")
                a_luogo=st.text_input('Luogo Nascita')
                a_foto=st.file_uploader('Foto Volontario * (JPG/PNG)',type=['jpg','png','jpeg'],key='foto_vol')
            with c2:
                a_ind=st.text_input('Indirizzo')
                a_com=st.text_input('Comune')
                a_prov=st.text_input('Provincia')
                a_cap=st.text_input('CAP')
                if a_foto is not None:
                    st.image(a_foto,width=150)
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
                    st.success(f"Salvato {nc} con CF {a_cf} per barcode!")
                    st.rerun()

    with tab2:
        with st.form('form_vol_cont'):
            vol_list=[d.get('Nome','') for d in st.session_state.dati] or ['Nessun volontario']
            sel_vol=st.selectbox('Seleziona Volontario',vol_list,key='sel_vol_cont')
            for d in st.session_state.dati:
                if d.get('Nome','')==sel_vol:
                    fp=d.get('FotoFile','')
                    if fp and os.path.exists(fp):
                        st.image(fp,width=100)
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
                        st.success(f"Contatti {sel_vol}")
                        st.rerun()

    with tab3:
        with st.form('form_vol_ruolo'):
            vol_list=[d.get('Nome','') for d in st.session_state.dati] or ['Nessun volontario']
            sel_vol2=st.selectbox('Seleziona Volontario',vol_list,key='sel_vol_ruolo')
            c1,c2=st.columns(2)
            with c1:
                c_ruolo=st.selectbox('Ruolo',['Volontario','Caposquadra','Coordinatore','Autista','Radio','Logistica','Segreteria','Sanitario','Altro'])
                c_gruppo=st.text_input('Gruppo / Squadra')
                c_data_iscr=st.date_input('Data Iscrizione',value=date.today(),format="DD/MM/YYYY")
            with c2:
                c_tessera=st.text_input('Numero Tessera')
                c_data_scad=st.date_input('Data Scadenza Tessera',value=date.today(),format="DD/MM/YYYY")
                c_odv=st.selectbox('ODV Appartenenza',['A.N.A. Sezione di Varese','Protezione Civile Varese','ANA Varese','Croce Rossa','Alpini','AIB','Altro'])
            if st.form_submit_button('SALVA RUOLO E ODV'):
                for i,d in enumerate(st.session_state.dati):
                    if d.get('Nome','')==sel_vol2:
                        st.session_state.dati[i].update({'Ruolo':c_ruolo,'Gruppo':c_gruppo,'DataIscrizione':fmt_date(c_data_iscr),'Tessera':c_tessera,'DataScadenza':fmt_date(c_data_scad),'ODV':c_odv})
                        save(FD,st.session_state.dati)
                        st.success(f"Ruolo e ODV {c_odv} salvati")
                        st.rerun()

    with tab5:
        if st.session_state.dati:
            df=pd.DataFrame(st.session_state.dati)
            st.dataframe(df,use_container_width=True)
            st.download_button('SCARICA EXCEL VOLONTARI',export_excel(df),file_name='Volontari.xlsx')
            if st.button('CREA PDF VOLONTARI'):
                pdf=make_pdf("Volontari ANA Varese",df)
                if pdf:
                    st.session_state['pdf_vol']=pdf
                    st.success('PDF creato!')
            if 'pdf_vol' in st.session_state:
                st.download_button('SCARICA PDF VOLONTARI',st.session_state['pdf_vol'],file_name='Volontari.pdf',mime='application/pdf',use_container_width=True)

    with tab6:
        st.markdown('##### TESSERINO REGIONE LOMBARDIA - COME ESEMPIO EZIO')
        st.info("Replica esatta: loghi e intestazione uguali al tuo esempio, nome cognome, ODV, barcode CF")
        vol_list=[d.get('Nome','') for d in st.session_state.dati] or []
        if not vol_list:
            st.warning('Nessun volontario')
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
                    st.image("Tesserino-Ezio.JPG",caption="Template originale",use_container_width=True)
                else:
                    up_tmpl=st.file_uploader('Carica template per loghi uguali',type=['jpg','png','jpeg'],key='tmpl_tess')
                    if up_tmpl is not None:
                        with open("Tesserino-Ezio.JPG",'wb') as f:
                            f.write(up_tmpl.getbuffer())
                        st.success('Template salvato!')
                        st.rerun()
            with c2:
                st.markdown('##### Anteprima Tesserino Regione Lombardia')
                foto_path=vol_data.get('FotoFile','')
                tmpl_path="Tesserino-Ezio.JPG" if os.path.exists("Tesserino-Ezio.JPG") else None
                tess_bytes=crea_tesserino_regione(vol_data, foto_path, tmpl_path)
                if tess_bytes:
                    st.image(tess_bytes,use_container_width=True)
                    st.download_button('SCARICA TESSERINO PNG',tess_bytes,file_name=f"Tesserino_{sel_tess.replace(' ','_')}.png",mime='image/png',use_container_width=True,type='primary')

elif scelta=='Tesserino Regionale':
    torna()
    st.markdown('#### TESSERINO REGIONE LOMBARDIA - COME ESEMPIO')
    st.success("Replica esatta tesserino: loghi e intestazione uguali al tuo esempio, nome cognome, ODV, barcode CF")
    vol_list=[d.get('Nome','') for d in st.session_state.dati] or []
    if not vol_list:
        st.warning('Nessun volontario')
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
            st.write(f"**Nome:** {vol_data.get('Nome','')}")
            st.write(f"**CF:** {vol_data.get('CF','')} (barcode)")
            st.write(f"**ODV:** {vol_data.get('ODV','')}")
            if os.path.exists("Tesserino-Ezio.JPG"):
                st.image("Tesserino-Ezio.JPG",caption="Template originale",use_container_width=True)
        with c2:
            foto_path=vol_data.get('FotoFile','')
            tmpl_path="Tesserino-Ezio.JPG" if os.path.exists("Tesserino-Ezio.JPG") else None
            tess_bytes=crea_tesserino_regione(vol_data, foto_path, tmpl_path)
            if tess_bytes:
                st.image(tess_bytes,use_container_width=True)
                st.download_button('SCARICA TESSERINO PNG',tess_bytes,file_name=f"Tesserino_{sel_tess.replace(' ','_')}.png",mime='image/png',use_container_width=True,type='primary')
                if st.button('GENERA TUTTI I TESSERINI IN ZIP',type='primary',use_container_width=True):
                    import zipfile
                    zip_buf=BytesIO()
                    with zipfile.ZipFile(zip_buf,'w') as zf:
                        tmpl_path="Tesserino-Ezio.JPG" if os.path.exists("Tesserino-Ezio.JPG") else None
                        for d in st.session_state.dati:
                            b=crea_tesserino_regione(d, d.get('FotoFile',''), tmpl_path)
                            if b:
                                zf.writestr(f"Tesserino_{d.get('Nome','').replace(' ','_')}.png", b)
                    zip_buf.seek(0)
                    st.download_button('SCARICA TUTTI I TESSERINI ZIP',zip_buf.getvalue(),file_name='Tesserini_Regione_Lombardia_Tutti.zip',mime='application/zip',use_container_width=True)

elif scelta=='Mappa':
    torna()
    st.markdown('<h3>MAPPA - COMUNE VIA</h3>', unsafe_allow_html=True)
    lat_c=st.session_state.lat
    lon_c=st.session_state.lon
    zm=st.session_state.zoom
    if HAS:
        m=folium.Map(location=[lat_c,lon_c],zoom_start=zm,tiles='OpenStreetMap')
        for idx,p in enumerate(st.session_state.post):
            try:
                la=float(p.get('Lat','0'))
                lo=float(p.get('Lon','0'))
                folium.Marker([la,lo],popup=p.get('Postazione',''),icon=folium.Icon(color='blue')).add_to(m)
            except:
                pass
        if st.session_state.clat is not None:
            folium.Marker([st.session_state.clat,st.session_state.clon],icon=folium.Icon(color='green')).add_to(m)
        out=st_folium(m,height=450,width=700,key='map1')
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
                st.rerun()
            except:
                pass
    c1,c2=st.columns(2)
    with c1:
        st.success(f"Comune: {st.session_state.com}")
        st.write(f"Via: {st.session_state.via}")
    with c2:
        st.write(f"Lat: {round(st.session_state.lat,6)}")
        st.write(f"Lon: {round(st.session_state.lon,6)}")
    vol_nomi=[d.get('Nome','') for d in st.session_state.dati] or ['Nessun volontario']
    with st.form('form_mappa'):
        c1,c2=st.columns(2)
        with c1:
            m1=st.text_input('Nome postazione *')
            m2=st.text_input('Comune *',value=st.session_state.com)
            m3=st.text_input('Via *',value=st.session_state.via)
        with c2:
            m5=st.text_input('Latitudine *',value=str(st.session_state.lat))
            m6=st.text_input('Longitudine *',value=str(st.session_state.lon))
            m8=st.selectbox('Responsabile *',vol_nomi)
            m9=st.selectbox('ODV operante *',st.session_state.odv)
        if st.form_submit_button('SALVA POSTAZIONE'):
            if m1:
                nuovo={'Postazione':m1,'Comune':m2,'Via':m3,'Lat':m5,'Lon':m6,'Responsabile':m8,'ODV':m9}
                st.session_state.post.append(nuovo)
                save(FP,st.session_state.post)
                st.success(f"Salvata {m1}")
                st.rerun()
    if st.session_state.post:
        df_post=pd.DataFrame(st.session_state.post)
        st.dataframe(df_post,use_container_width=True)
        st.download_button('SCARICA EXCEL MAPPA',export_excel(df_post),file_name='Mappa.xlsx')

elif scelta=='Backup':
    torna()
    st.markdown('#### BACKUP')
    if st.session_state.dati:
        df=pd.DataFrame(st.session_state.dati)
        st.download_button('EXPORT VOLONTARI EXCEL',export_excel(df),file_name='Volontari.xlsx',key='exp_vol',use_container_width=True)
        if st.button('CREA PDF VOLONTARI',key='pdf_vol_btn2',use_container_width=True):
            pdf=make_pdf("Volontari ANA Varese",df)
            if pdf:
                st.session_state['pdf_bk_vol']=pdf
                st.success('PDF creato!')
        if 'pdf_bk_vol' in st.session_state:
            st.download_button('SCARICA PDF VOLONTARI',st.session_state['pdf_bk_vol'],file_name='Volontari.pdf',mime='application/pdf',key='pdf_vol_dl',use_container_width=True)

elif scelta=='Impostazioni Popup':
    torna()
    st.markdown('#### IMPOSTAZIONI POPUP - TUA IMMAGINE FUMETTO')
    st.success("Popup con SOLO tua immagine con fumetto - NO logo PC")
    with st.form('form_popup'):
        p_titolo=st.text_input('Titolo Popup',value=st.session_state.popup_cfg.get('titolo','ANA VARESE - VOLONTARIATO'))
        p_sotto=st.text_input('Sottotitolo Popup',value=st.session_state.popup_cfg.get('sottotitolo','Ciao Ragazzi, Buon Lavoro!'))
        p_mostra=st.checkbox('Mostra popup all avvio',value=st.session_state.popup_cfg.get('mostra',True))
        if st.form_submit_button('SALVA IMPOSTAZIONI POPUP'):
            st.session_state.popup_cfg={'titolo':p_titolo,'sottotitolo':p_sotto,'mostra':p_mostra}
            save(FPOP,st.session_state.popup_cfg)
            st.success('Impostazioni salvate')
    up_popup=st.file_uploader('Carica tua immagine con fumetto',type=['jpg','png','jpeg'],key='up_popup')
    if up_popup is not None:
        st.image(up_popup,use_container_width=True)
        if st.button('SALVA COME COPERTINA.JPG',type='primary',use_container_width=True):
            with open('copertina.jpg','wb') as f:
                f.write(up_popup.getbuffer())
            st.success('Salvata!')
    for img_name in ['copertina.jpg','Tesserino-Ezio.JPG','logo.png']:
        if os.path.exists(img_name):
            st.write(f"File: {img_name}")
            try:
                st.image(img_name,width=300)
            except:
                pass
    if st.button('MOSTRA ANTEPRIMA POPUP',type='primary',use_container_width=True):
        st.session_state.popup_shown=False
        st.rerun()
