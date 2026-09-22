import streamlit as st
import pandas as pd
import os
from io import BytesIO
from datetime import date, datetime
import tempfile
import json

st.set_page_config(page_title='ANA Varese', layout='wide')
VERDE = "#1A5D1A"
st.markdown(f"<style>h1,h2,h3{{color:{VERDE}!important;}}.stButton>button{{background:{VERDE}!important;color:white!important;font-weight:bold!important;}}</style>", unsafe_allow_html=True)

def hdr():
    col_logo, col_title = st.columns([1,5])
    with col_logo:
        try:
            st.image('logo.png', width=110)
        except:
            try:
                st.image('copertina.png', width=110)
            except:
                st.markdown('**ANA**')
    with col_title:
        st.markdown(f'<div style="background:{VERDE};padding:12px;border-radius:8px;color:white;font-weight:bold;font-size:18px;">NUCLEO PROT CIVILE ANA VARESE - Squadra Alpini Caronno</div>', unsafe_allow_html=True)

def hdr_form(titolo):
    c1,c2 = st.columns([1,8])
    with c1:
        try:
            st.image('logo.png', width=80)
        except:
            try:
                st.image('copertina.png', width=80)
            except:
                pass
    with c2:
        st.markdown(f'## {titolo}')

def to_excel(df):
    out = BytesIO()
    cols = [c for c in df.columns if c not in ['Foto','FotoBytes']]
    df[cols].to_excel(out, index=False, engine='openpyxl')
    return out.getvalue()

def to_pdf(df, titolo):
    try:
        from reportlab.lib.pagesizes import landscape, A4
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib import colors
        buf = BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=landscape(A4), leftMargin=20, rightMargin=20, topMargin=20, bottomMargin=20)
        styles = getSampleStyleSheet()
        story = []
        story.append(Paragraph(f"<b>{titolo} - ANA Varese - {date.today()}</b>", styles['Title']))
        story.append(Spacer(1, 12))
        if df.empty:
            story.append(Paragraph("Nessun dato", styles['Normal']))
        else:
            cols = [c for c in df.columns if c not in ['Foto','FotoBytes']]
            if not cols:
                cols = list(df.columns[:8])
            data = [cols]
            for _, row in df.iterrows():
                r = []
                for c in cols:
                    v = str(row.get(c,''))[:60]
                    r.append(v)
                data.append(r)
            t = Table(data, repeatRows=1)
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1A5D1A')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,-1), 7),
                ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.whitesmoke, colors.lightgrey])
            ]))
            story.append(t)
        doc.build(story)
        return buf.getvalue()
    except Exception as e:
        return None

def to_excel_multi(datasets):
    out = BytesIO()
    with pd.ExcelWriter(out, engine='openpyxl') as writer:
        for nome, df_list in datasets.items():
            if df_list:
                df = pd.DataFrame(df_list)
                cols = [c for c in df.columns if c not in ['Foto','FotoBytes']]
                df[cols].to_excel(writer, sheet_name=nome[:31], index=False)