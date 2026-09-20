import streamlit as st
import pandas as pd
from io import BytesIO
import os, json, hashlib
from datetime import date

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
    except:
        return None

def crea_tesserino_nitido_piccolo(vol,foto_path,tmpl):
    """
    TESSERINO NITIDO PICCOLO - NON SFUOCATO
    Dimensione nativa 860x540 - 300 DPI
    Cambio solo: foto, nome ODV, barcode CF
    """
    try:
        if not HAS_PIL:
            return None
        # DIMENSIONE NATIVA PICCOLA - NITIDA
        W,H=860,540
        if tmpl and os.path.exists(tmpl):
            base=Image.open(tmpl).convert("RGB")
            # NON ingrandire - usa dimensione originale
            if base.size[0] > W:
                base=base.resize((W,H),Image.LANCZOS)
            tess=base.copy()
            # Se template più grande, riduci a W,H
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
        except