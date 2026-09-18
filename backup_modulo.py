import streamlit as st
import pandas as pd
from datetime import date, datetime
from io import BytesIO
import json, uuid, os, zipfile

def load_json(f, default):
    try:
        if os.path.exists(f):
            with open(f,"r",encoding="utf-8") as fh:
                d=json.load(fh)
                if isinstance(d,list): return d
    except: pass
    return default

def save_json(f,d):
    try:
        with open(f,"w",encoding="utf-8") as fh: json.dump(d,fh,ensure_ascii=False,indent=2)
    except: pass

def mostra_backup():
    st.markdown("### 💾 BACKUP - UNICO BACKUP DI TUTTI I FORM")
    st.success("✅ NOVITA': Un unico backup di tutti i form in un solo file!")
    MIME_SHORT="application/octet-stream"

    # ==========================================
    # NUOVO: BACKUP UNICO DI TUTTI I FORM
    # ==========================================
    st.markdown("## 📦 BACKUP UNICO DI TUTTI I FORM - TUTTO INSIEME")
    st.markdown('<div style="background-color:#fff3e0;border:4px solid #ef6c00;border-radius:15px;padding:25px;margin:15px 0;">', unsafe_allow_html=True)
    st.markdown("### 🚀 Un unico file con TUTTI i form dentro!")

    col_tot1, col_tot2, col_tot3, col_tot4 = st.columns(4)
    with col_tot1: st.metric("Volontari", len(st.session_state.dati))
    with col_tot2: st.metric("Postazioni", len(st.session_state.postazioni))
    with col_tot3: st.metric("Emergenze", len(st.session_state.emergenze_lista))
    with col_tot4: st.metric("Radio", len(st.session_state.radio_db))

    col_tot5, col_tot6, col_tot7, col_tot8 = st.columns(4)
    with col_tot5: st.metric("Dist Radio", len(st.session_state.dist_radio))
    with col_tot6: st.metric("Eventi", len(st.session_state.eventi_lista))
    with col_tot7: st.metric("Check-in", len(st.session_state.checkin_lista))
    with col_tot8: st.metric("Mem Nomi", len(st.session_state.mem_nomi))

    totale_record = len(st.session_state.dati) + len(st.session_state.postazioni) + len(st.session_state.emergenze_lista) + len(st.session_state.radio_db) + len(st.session_state.dist_radio) + len(st.session_state.eventi_lista) + len(st.session_state.checkin_lista) + len(st.session_state.mem_nomi)
    st.metric(f"📊 TOTALE RECORD TUTTI I FORM", f"{totale_record} record - 8 form")

    c_uni1, c_uni2, c_uni3 = st.columns(3)
    with c_uni1:
        if st.button("📦 CREA EXCEL UNICO\nTUTTI I FORM", use_container_width=True, type="primary", key="btn_excel_unico_tutti"):
            output=BytesIO()
            with pd.ExcelWriter(output,engine="openpyxl") as writer:
                if st.session_state.dati:
                    pd.DataFrame(st.session_state.dati).to_excel(writer,sheet_name="Volontari",index=False)
                if st.session_state.postazioni:
                    pd.DataFrame(st.session_state.postazioni).to_excel(writer,sheet_name="Postazioni",index=False)
                if st.session_state.emergenze_lista:
                    pd.DataFrame(st.session_state.emergenze_lista).to_excel(writer,sheet_name="Emergenze",index=False)
                if st.session_state.radio_db:
                    pd.DataFrame(st.session_state.radio_db).to_excel(writer,sheet_name="DB_Radio",index=False)
                if st.session_state.dist_radio:
                    pd.DataFrame(st.session_state.dist_radio).to_excel(writer,sheet_name="Dist_Radio",index=False)
                if st.session_state.eventi_lista:
                    pd.DataFrame(st.session_state.eventi_lista).to_excel(writer,sheet_name="Eventi",index=False)
                if st.session_state.checkin_lista:
                    pd.DataFrame(st.session_state.checkin_lista).to_excel(writer,sheet_name="Checkin",index=False)
                if st.session_state.mem_nomi:
                    pd.DataFrame(st.session_state.mem_nomi, columns=["Nomi"]).to_excel(writer,sheet_name="Mem_Nomi",index=False)
                # Foglio riepilogo
                riepilogo = [
                    {"Form": "Volontari", "Record": len(st.session_state.dati)},
                    {"Form": "Postazioni", "Record": len(st.session_state.postazioni)},
                    {"Form": "Emergenze", "Record": len(st.session_state.emergenze_lista)},
                    {"Form": "DB Radio", "Record": len(st.session_state.radio_db)},
                    {"Form": "Dist Radio", "Record": len(st.session_state.dist_radio)},
                    {"Form": "Eventi", "Record": len(st.session_state.eventi_lista)},
                    {"Form": "Check-in", "Record": len(st.session_state.checkin_lista)},
                    {"Form": "Mem Nomi", "Record": len(st.session_state.mem_nomi)},
                ]
                pd.DataFrame(riepilogo).to_excel(writer,sheet_name="RIEPILOGO",index=False)
            st.session_state["backup_unico_excel"] = output.getvalue()
            st.success(f"✅ Excel UNICO creato con tutti i {totale_record} record di 8 form!")

    with c_uni2:
        if st.button("📦 CREA JSON UNICO\nTUTTI I FORM", use_container_width=True, key="btn_json_unico_tutti"):
            all_data={
                "volontari": st.session_state.dati,
                "postazioni": st.session_state.postazioni,
                "emergenze": st.session_state.emergenze_lista,
                "radio_db": st.session_state.radio_db,
                "dist_radio": st.session_state.dist_radio,
                "eventi": st.session_state.eventi_lista,
                "checkin": st.session_state.checkin_lista,
                "mem_nomi": st.session_state.mem_nomi,
                "riepilogo": {
                    "data_backup": str(datetime.now()),
                    "totale_record": totale_record,
                    "dettaglio": {
                        "volontari": len(st.session_state.dati),
                        "postazioni": len(st.session_state.postazioni),
                        "emergenze": len(st.session_state.emergenze_lista),
                        "radio_db": len(st.session_state.radio_db),
                        "dist_radio": len(st.session_state.dist_radio),
                        "eventi": len(st.session_state.eventi_lista),
                        "checkin": len(st.session_state.checkin_lista),
                        "mem_nomi": len(st.session_state.mem_nomi)
                    }
                }
            }
            json_str=json.dumps(all_data,ensure_ascii=False,indent=2)
            st.session_state["backup_unico_json"] = json_str.encode('utf-8')
            st.success(f"✅ JSON UNICO creato!")

    with c_uni3:
        if st.button("📄 CREA PDF UNICO\nTUTTI I FORM", use_container_width=True, key="btn_pdf_unico_tutti"):
            try:
                from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
                from reportlab.lib.styles import getSampleStyleSheet
                from reportlab.lib import colors
                from reportlab.lib.pagesizes import A4
                buffer = BytesIO()
                doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=30, rightMargin=30, topMargin=30, bottomMargin=30)
                styles = getSampleStyleSheet()
                elements = []
                elements.append(Paragraph(f"ANA VARESE - BACKUP UNICO TUTTI I FORM", styles['Heading1']))
                elements.append(Spacer(1, 12))
                elements.append(Paragraph(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')} - Totale: {totale_record} record - 8 form", styles['Normal']))
                elements.append(Spacer(1, 20))

                # Tabella riepilogo
                riepilogo_data = [["Form", "Record"]] + [[f, len(getattr(st.session_state, f"{k}_lista" if k not in ['dati','postazioni','mem_nomi'] else k))] for f,k in [("Volontari","dati"),("Postazioni","postazioni"),("Emergenze","emergenze"),("DB Radio","radio_db"),("Dist Radio","dist_radio"),("Eventi","eventi"),("Check-in","checkin"),("Mem Nomi","mem_nomi")]]
                # Correzione conteggi
                riepilogo_data = [
                    ["Form", "Record"],
                    ["Volontari", str(len(st.session_state.dati))],
                    ["Postazioni", str(len(st.session_state.postazioni))],
                    ["Emergenze", str(len(st.session_state.emergenze_lista))],
                    ["DB Radio", str(len(st.session_state.radio_db))],
                    ["Dist Radio", str(len(st.session_state.dist_radio))],
                    ["Eventi", str(len(st.session_state.eventi_lista))],
                    ["Check-in", str(len(st.session_state.checkin_lista))],
                    ["Mem Nomi", str(len(st.session_state.mem_nomi))],
                    ["TOTALE", str(totale_record)],
                ]
                table_riep = Table(riepilogo_data)
                table_riep.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e7d32')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#ffeb3b')),
                    ('FONTSIZE', (0, 0), (-1, -1), 8),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                elements.append(table_riep)
                elements.append(Spacer(1, 20))

                # Per ogni form, prima 10 righe
                for nome_form, lista_dati in [("Volontari", st.session_state.dati), ("Postazioni", st.session_state.postazioni), ("Emergenze", st.session_state.emergenze_lista), ("DB Radio", st.session_state.radio_db), ("Dist Radio", st.session_state.dist_radio), ("Eventi", st.session_state.eventi_lista), ("Check-in", st.session_state.checkin_lista), ("Mem Nomi", st.session_state.mem_nomi)]:
                    if lista_dati:
                        elements.append(Paragraph(f"{nome_form} - {len(lista_dati)} record", styles['Heading2']))
                        df_temp = pd.DataFrame(lista_dati) if not isinstance(lista_dati[0], str) else pd.DataFrame(lista_dati, columns=["Nome"])
                        for col in list(df_temp.columns):
                            if 'PNG' in col or 'CustomPNG' in col:
                                df_temp = df_temp.drop(columns=[col])
                        if len(df_temp.columns) > 4:
                            df_temp = df_temp.iloc[:, :4]
                        df_temp = df_temp.head(8)
                        data = [list(df_temp.columns)] + df_temp.values.tolist()
                        table = Table(data)
                        table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e7d32')),('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),('FONTSIZE', (0, 0), (-1, -1), 6),('GRID', (0, 0), (-1, -1), 1, colors.black)]))
                        elements.append(table)
                        elements.append(Spacer(1, 15))

                doc.build(elements)
                buffer.seek(0)
                st.session_state["backup_unico_pdf"] = buffer.getvalue()
                st.success(f"✅ PDF UNICO creato con tutti i form!")
            except Exception as e:
                st.error(f"Errore PDF: {e}")

    st.markdown('</div>', unsafe_allow_html=True)

    # Download bottoni per backup unico
    d1, d2, d3 = st.columns(3)
    with d1:
        if "backup_unico_excel" in st.session_state:
            st.download_button(f"📥 SCARICA EXCEL UNICO\nTUTTI I {totale_record} RECORD",st.session_state["backup_unico_excel"],file_name=f"BACKUP_UNICO_TUTTI_I_FORM_{date.today()}.xlsx",mime=MIME_SHORT,use_container_width=True,key="dl_excel_unico_tutti")
    with d2:
        if "backup_unico_json" in st.session_state:
            st.download_button(f"📥 SCARICA JSON UNICO\nTUTTI I FORM",st.session_state["backup_unico_json"],file_name=f"BACKUP_UNICO_TUTTI_I_FORM_{date.today()}.json",mime="application/json",use_container_width=True,key="dl_json_unico_tutti")
    with d3:
        if "backup_unico_pdf" in st.session_state:
            st.download_button(f"📥 SCARICA PDF UNICO\nTUTTI I FORM",st.session_state["backup_unico_pdf"],file_name=f"BACKUP_UNICO_TUTTI_I_FORM_{date.today()}.pdf",mime="application/pdf",use_container_width=True,key="dl_pdf_unico_tutti")

    st.divider()
    st.markdown("---")

    # ==========================================
    # VECCHIO: BACKUP CON CASELLE (come prima)
    # ==========================================
    st.markdown("## 📋 Backup con scelta (opzionale)")
    tab1, tab2, tab3, tab4 = st.tabs(["📦 Backup con Caselle", "📋 Singoli Form", "🖨️ PDF con Scelta", "📥 Import"])

    with tab1:
        st.markdown("#### 📦 CASELLE - Scegli i dati dei form da esportare")
        st.markdown('<div style="background-color:#f1f8e9;border:3px solid #2e7d32;border-radius:12px;padding:20px;margin:15px 0;">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            chk_vol = st.checkbox(f"👤 Volontari ({len(st.session_state.dati)})", value=True, key="chk_vol_1")
            chk_post = st.checkbox(f"📍 Postazioni ({len(st.session_state.postazioni)})", value=True, key="chk_post_1")
            chk_emer = st.checkbox(f"🚨 Emergenze ({len(st.session_state.emergenze_lista)})", value=True, key="chk_emer_1")
            chk_radio = st.checkbox(f"📻 DB Radio ({len(st.session_state.radio_db)})", value=True, key="chk_radio_1")
        with col2:
            chk_dist = st.checkbox(f"📡 Distribuzione ({len(st.session_state.dist_radio)})", value=True, key="chk_dist_1")
            chk_eventi = st.checkbox(f"📅 Eventi ({len(st.session_state.eventi_lista)})", value=True, key="chk_eventi_1")
            chk_check = st.checkbox(f"✅ Check-in ({len(st.session_state.checkin_lista)})", value=True, key="chk_check_1")
            chk_nomi = st.checkbox(f"📝 Mem Nomi ({len(st.session_state.mem_nomi)})", value=True, key="chk_nomi_1")
        selected_count = sum([chk_vol, chk_post, chk_emer, chk_radio, chk_dist, chk_eventi, chk_check, chk_nomi])
        st.metric("Form Selezionati", f"{selected_count}/8")
        st.markdown('</div>', unsafe_allow_html=True)

        if st.button(f"📦 Crea Excel con {selected_count} Form",use_container_width=True,type="primary",key="btn_excel_1", disabled=(selected_count==0)):
            output=BytesIO()
            with pd.ExcelWriter(output,engine="openpyxl") as writer:
                if chk_vol and st.session_state.dati:
                    pd.DataFrame(st.session_state.dati).to_excel(writer,sheet_name="Volontari",index=False)
                if chk_post and st.session_state.postazioni:
                    pd.DataFrame(st.session_state.postazioni).to_excel(writer,sheet_name="Postazioni",index=False)
                if chk_emer and st.session_state.emergenze_lista:
                    pd.DataFrame(st.session_state.emergenze_lista).to_excel(writer,sheet_name="Emergenze",index=False)
                if chk_radio and st.session_state.radio_db:
                    pd.DataFrame(st.session_state.radio_db).to_excel(writer,sheet_name="DB_Radio",index=False)
                if chk_dist and st.session_state.dist_radio:
                    pd.DataFrame(st.session_state.dist_radio).to_excel(writer,sheet_name="Dist_Radio",index=False)
                if chk_eventi and st.session_state.eventi_lista:
                    pd.DataFrame(st.session_state.eventi_lista).to_excel(writer,sheet_name="Eventi",index=False)
                if chk_check and st.session_state.checkin_lista:
                    pd.DataFrame(st.session_state.checkin_lista).to_excel(writer,sheet_name="Checkin",index=False)
                if chk_nomi and st.session_state.mem_nomi:
                    pd.DataFrame(st.session_state.mem_nomi, columns=["Nomi"]).to_excel(writer,sheet_name="Mem_Nomi",index=False)
            st.session_state["backup_bytes_excel"] = output.getvalue()
            st.session_state["backup_count_excel"] = selected_count

        if "backup_bytes_excel" in st.session_state:
            st.download_button(f"📥 Scarica Excel {st.session_state['backup_count_excel']} Form",st.session_state["backup_bytes_excel"],file_name=f"backup_{st.session_state['backup_count_excel']}form_{date.today()}.xlsx",mime=MIME_SHORT,use_container_width=True,key="dl_excel_1")

        if st.button(f"📦 Crea JSON con {selected_count} Form",use_container_width=True,key="btn_json_1", disabled=(selected_count==0)):
            all_data={}
            if chk_vol: all_data["volontari"]=st.session_state.dati
            if chk_post: all_data["postazioni"]=st.session_state.postazioni
            if chk_emer: all_data["emergenze"]=st.session_state.emergenze_lista
            if chk_radio: all_data["radio_db"]=st.session_state.radio_db
            if chk_dist: all_data["dist_radio"]=st.session_state.dist_radio
            if chk_eventi: all_data["eventi"]=st.session_state.eventi_lista
            if chk_check: all_data["checkin"]=st.session_state.checkin_lista
            if chk_nomi: all_data["mem_nomi"]=st.session_state.mem_nomi
            json_str=json.dumps(all_data,ensure_ascii=False,indent=2)
            st.session_state["backup_bytes_json"] = json_str.encode('utf-8')
            st.session_state["backup_count_json"] = selected_count

        if "backup_bytes_json" in st.session_state:
            st.download_button(f"📥 Scarica JSON {st.session_state['backup_count_json']} Form",st.session_state["backup_bytes_json"],file_name=f"backup_{st.session_state['backup_count_json']}form_{date.today()}.json",mime="application/json",use_container_width=True,key="dl_json_1")

    with tab2:
        st.markdown("#### 📋 Singoli Form")
        for nome_form, lista_dati, key_form in [("Volontari", st.session_state.dati, "volontari"), ("Postazioni", st.session_state.postazioni, "postazioni"), ("Emergenze", st.session_state.emergenze_lista, "emergenze"), ("DB Radio", st.session_state.radio_db, "radio_db")]:
            if lista_dati:
                out=BytesIO()
                pd.DataFrame(lista_dati).to_excel(out,index=False,engine="openpyxl")
                st.download_button(f"📥 Excel {nome_form} - {len(lista_dati)}",out.getvalue(),file_name=f"{key_form}_{date.today()}.xlsx",mime="application/octet-stream",use_container_width=True,key=f"dl_single_{key_form}")

    with tab3:
        st.markdown("#### 🖨️ PDF con Scelta Form")
        st.info("Usa il backup unico sopra per PDF completo!")

    with tab4:
        st.markdown("#### 📥 Import - COME VECCHIO APP.PY")
        import_type=st.selectbox("Tipo Import *",["Volontari","Postazioni Mappa","Emergenze con Loghi","DB Radio","Distribuzione Radio","Eventi","Check-in","Mem Nomi"],key="import_type")
        modo_import=st.selectbox("Modalità *",["Aggiungi","Sovrascrivi"],key="modo_import")
        file_type=st.selectbox("Formato *",["Excel","JSON"],key="file_type")
        uploaded_file=st.file_uploader(f"📁 Seleziona file {import_type} ({file_type})",type=["xlsx","xls","json"],key="import_file")
        if uploaded_file is not None:
            st.success(f"✅ File: {uploaded_file.name}")
            if st.button(f"📥 IMPORTA {import_type}",use_container_width=True,type="primary",key="btn_import"):
                try:
                    if file_type=="Excel":
                        df_import=pd.read_excel(uploaded_file,engine="openpyxl")
                        data_import=df_import.to_dict('records')
                    else:
                        data_import=json.load(uploaded_file)
                        # Se JSON unico con tutti i form
                        if isinstance(data_import, dict) and "volontari" in data_import:
                            # Import unico!
                            if "volontari" in data_import:
                                st.session_state.dati = data_import["volontari"] if modo_import=="Sovrascrivi" else st.session_state.dati + data_import["volontari"]
                                save_json("dati_volontari.json",st.session_state.dati)
                            if "postazioni" in data_import:
                                st.session_state.postazioni = data_import["postazioni"] if modo_import=="Sovrascrivi" else st.session_state.postazioni + data_import["postazioni"]
                                save_json("postazioni.json",st.session_state.postazioni)
                            if "emergenze" in data_import:
                                st.session_state.emergenze_lista = data_import["emergenze"] if modo_import=="Sovrascrivi" else st.session_state.emergenze_lista + data_import["emergenze"]
                                save_json("emergenze.json",st.session_state.emergenze_lista)
                            if "radio_db" in data_import:
                                st.session_state.radio_db = data_import["radio_db"] if modo_import=="Sovrascrivi" else st.session_state.radio_db + data_import["radio_db"]
                                save_json("radio_db.json",st.session_state.radio_db)
                            if "dist_radio" in data_import:
                                st.session_state.dist_radio = data_import["dist_radio"] if modo_import=="Sovrascrivi" else st.session_state.dist_radio + data_import["dist_radio"]
                                save_json("dist_radio.json",st.session_state.dist_radio)
                            if "eventi" in data_import:
                                st.session_state.eventi_lista = data_import["eventi"] if modo_import=="Sovrascrivi" else st.session_state.eventi_lista + data_import["eventi"]
                                save_json("eventi.json",st.session_state.eventi_lista)
                            if "checkin" in data_import:
                                st.session_state.checkin_lista = data_import["checkin"] if modo_import=="Sovrascrivi" else st.session_state.checkin_lista + data_import["checkin"]
                                save_json("checkin.json",st.session_state.checkin_lista)
                            if "mem_nomi" in data_import:
                                st.session_state.mem_nomi = data_import["mem_nomi"] if modo_import=="Sovrascrivi" else st.session_state.mem_nomi + data_import["mem_nomi"]
                                save_json("mem_nomi.json",st.session_state.mem_nomi)
                            st.success(f"✅ Import UNICO di tutti i form riuscito!")
                            st.rerun()
                            return

                    # Import singolo form
                    if import_type=="Volontari":
                        st.session_state.dati = data_import if modo_import=="Sovrascrivi" else st.session_state.dati + data_import
                        save_json("dati_volontari.json",st.session_state.dati)
                    elif import_type=="Postazioni Mappa":
                        st.session_state.postazioni = data_import if modo_import=="Sovrascrivi" else st.session_state.postazioni + data_import
                        save_json("postazioni.json",st.session_state.postazioni)
                    elif import_type=="Emergenze con Loghi":
                        st.session_state.emergenze_lista = data_import if modo_import=="Sovrascrivi" else st.session_state.emergenze_lista + data_import
                        save_json("emergenze.json",st.session_state.emergenze_lista)
                    st.success(f"✅ Import {import_type} riuscito! {len(data_import)} record")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Errore: {e}")
        else:
            st.warning("⚠️ Seleziona un file")

    st.markdown("---")
    st.markdown("### ✅ BACKUP UNICO + CASELLE!")