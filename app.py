def crea_tess(vol,foto_path,tmpl):
    try:
        from PIL import Image, ImageDraw, ImageFont
        W,H=1720,1080  # Doppia risoluzione per nitidezza
        if tmpl and os.path.exists(tmpl):
            base=Image.open(tmpl).convert("RGB")
            base=base.resize((W,H), Image.LANCZOS)
            tess=base.copy()
            draw=ImageDraw.Draw(tess)
        else:
            tess=Image.new('RGB',(W,H),'white')
            draw=ImageDraw.Draw(tess)
        try:
            fn=ImageFont.truetype("arialbd.ttf",45)
            fo=ImageFont.truetype("arial.ttf",32)
        except:
            fn=ImageFont.load_default()
            fo=ImageFont.load_default()
        fx=int(W*0.015); fy=int(H*0.22)
        fw=int(W*0.27); fh=int(H*0.58)
        if foto_path and os.path.exists(foto_path):
            try:
                foto=Image.open(foto_path).convert("RGB")
                foto=foto.resize((fw,fh), Image.LANCZOS)
                tess.paste(foto,(fx,fy))
            except:
                pass
        nx=int(W*0.38); ny=int(H*0.36)
        draw.rectangle([nx,ny-5,nx+int(W*0.55),ny+int(H*0.15)],fill='white')
        draw.text((nx,ny),vol.get('Nome','').upper(),fill='black',font=fn)
        odv=vol.get('ODV','A.N.A. Sezione di Varese')
        oy=ny+int(H*0.12)
        draw.rectangle([nx,oy-2,nx+int(W*0.5),oy+int(H*0.08)],fill='white')
        draw.text((nx,oy),odv,fill='black',font=fo)
        # BARCODE NITIDO DA CF
        bx=int(W*0.62); by=int(H*0.73); bw=int(W*0.35); bh=int(H*0.18)
        draw.rectangle([bx,by,bx+bw,by+bh],fill='white',outline='white')
        cf=vol.get('CF','') or vol.get('Nome','').replace(' ','').upper()[:16]
        bc=crea_barcode(cf)
        if bc:
            try:
                bi=Image.open(BytesIO(bc)).convert("RGB")
                bi=bi.resize((bw,bh), Image.LANCZOS)
                tess.paste(bi,(bx,by))
            except:
                pass
        buf=BytesIO()
        tess.save(buf,format='PNG',dpi=(300,300))
        buf.seek(0)
        return buf.getvalue()
    except Exception as e:
        st.error(f"Errore: {e}")
        return None