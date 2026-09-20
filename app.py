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
                draw.rectangle(
