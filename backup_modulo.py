import streamlit as st
import pandas as pd
from datetime import date, datetime
from io import BytesIO
import json, uuid, os

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
    st.markdown("### 💾 BACKUP - CASELLE SCELTA FORM")
    st.success("✅ Caselle di scelta - Scegli i dati dei form da esportare!")
    MIME_SHORT="application/octet-stream"

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
        if selected_count==0:
            st.warning("Seleziona almeno un form!")
        else:
            st.success(f"✅ Hai selezionato {selected_count} form!")

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
            st.success(f"✅ Excel creato!")

        if "backup_bytes_excel" in st.session_state:
            fname=f"backup_{st.session_state['backup_count_excel']}form_{date.today()}.xlsx"
            st.download_button(f"📥 Scarica Excel {st.session_state['backup_count_excel']} Form",st.session_state["backup_bytes_excel"],file_name=fname,mime=MIME_SHORT,use_container_width=True,key="dl_excel_1")

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
            st.success(f"✅ JSON creato!")

        if "backup_bytes_json" in st.session_state:
            st.download_button(f"📥 Scarica JSON {st.session_state['backup_count_json']} Form",st.session_state["backup_bytes_json"],file_name=f"backup_{st.session_state['backup_count_json']}form_{date.today()}.json",mime="application/json",use_container_width=True,key="dl_json_1")

        if st.button(f"📄 Crea PDF con {selected_count} Form",use_container_width=True,key="btn_pdf_1", disabled=(selected_count==0)):
            try:
                from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
                from reportlab.lib.styles import getSampleStyleSheet
                from reportlab.lib import colors
                from reportlab.lib.pagesizes import A4
                buffer = BytesIO()
                doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=30, rightMargin=30, topMargin=30, bottomMargin=30)
                styles = getSampleStyleSheet()
                elements = []
                elements.append(Paragraph(f"ANA VARESE - Backup {selected_count} Form", styles['Heading1']))
                elements.append(Spacer(1, 20))
                form_map = []
                if chk_vol: form_map.append(("Volontari", st.session_state.dati))
                if chk_post: form_map.append(("Postazioni", st.session_state.postazioni))
                if chk_emer: form_map.append(("Emergenze", st.session_state.emergenze_lista))
                if chk_radio: form_map.append(("DB Radio", st.session_state.radio_db))
                if chk_dist: form_map.append(("Dist Radio", st.session_state.dist_radio))
                if chk_eventi: form_map.append(("Eventi", st.session_state.eventi_lista))
                if chk_check: form_map.append(("Check-in", st.session_state.checkin_lista))
                if chk_nomi: form_map.append(("Mem Nomi", st.session_state.mem_nomi))
                for nome_form, lista_dati in form_map:
                    if lista_dati:
                        elements.append(Paragraph(f"{nome_form} - {len(lista_dati)}", styles['Heading2']))
                        df_temp = pd.DataFrame(lista_dati) if not isinstance(lista_dati[0], str) else pd.DataFrame(lista_dati, columns=["Nome"])
                        for col in list(df_temp.columns):
                            if 'PNG' in col or 'CustomPNG' in col:
                                df_temp = df_temp.drop(columns=[col])
                        if len(df_temp.columns) > 5:
                            df_temp = df_temp.iloc[:, :5]
                        df_temp = df_temp.head(15)
                        data = [list(df_temp.columns)] + df_temp.values.tolist()
                        table = Table(data)
                        table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e7d32')),('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),('FONTSIZE', (0, 0), (-1, -1), 6),('GRID', (0, 0), (-1, -1), 1, colors.black)]))
                        elements.append(table)
                        elements.append(Spacer(1, 20))
                doc.build(elements)
                buffer.seek(0)
                st.session_state["backup_bytes_pdf"] = buffer.getvalue()
                st.session_state["backup_count_pdf"] = selected_count
                st.success(f"✅ PDF creato!")
            except Exception as e:
                st.error(f"Errore PDF: {e}")

        if "backup_bytes_pdf" in st.session_state:
            st.download_button(f"📥 Scarica PDF {st.session_state['backup_count_pdf']} Form", st.session_state["backup_bytes_pdf"], file_name=f"backup_{st.session_state['backup_count_pdf']}form_{date.today()}.pdf", mime="application/pdf", use_container_width=True, key="dl_pdf_1")

    with tab2:
        st.markdown("#### 📋 Singoli Form - Backup separati")
        forms_config = [
            ("👤 Volontari", st.session_state.dati, "volontari", "dati_volontari.json"),
            ("📍 Postazioni", st.session_state.postazioni, "postazioni", "postazioni.json"),
            ("🚨 Emergenze", st.session_state.emergenze_lista, "emergenze", "emergenze.json"),
            ("📻 DB Radio", st.session_state.radio_db, "radio_db", "radio_db.json"),
            ("📡 Dist Radio", st.session_state.dist_radio, "dist_radio", "dist_radio.json"),
            ("📅 Eventi", st.session_state.eventi_lista, "eventi", "eventi.json"),
            ("✅ Check-in", st.session_state.checkin_lista, "checkin", "checkin.json"),
            ("📝 Mem Nomi", st.session_state.mem_nomi, "mem_nomi", "mem_nomi.json"),
        ]
        for nome_form, lista_dati, key_form, file_json in forms_config:
            st.markdown(f"**{nome_form} - {len(lista_dati)} record**")
            c1,c2,c3=st.columns(3)
            with c1:
                if lista_dati:
                    out=BytesIO()
                    if key_form == "mem_nomi":
                        pd.DataFrame(lista_dati, columns=["Nome"]).to_excel(out,index=False,engine="openpyxl")
                    else:
                        pd.DataFrame(lista_dati).to_excel(out,index=False,engine="openpyxl")
                    st.download_button(f"📥 Excel",out.getvalue(),file_name=f"{key_form}_{date.today()}.xlsx",mime="application/octet-stream",use_container_width=True,key=f"dl_single_excel_{key_form}")
            with c2:
                if lista_dati:
                    json_bytes=json.dumps(lista_dati,ensure_ascii=False,indent=2).encode('utf-8')
                    st.download_button(f"📥 JSON",json_bytes,file_name=f"{key_form}_{date.today()}.json",mime="application/json",use_container_width=True,key=f"dl_single_json_{key_form}")
            with c3:
                if lista_dati:
                    out=BytesIO()
                    if key_form == "mem_nomi":
                        pd.DataFrame(lista_dati, columns=["Nome"]).to_excel(out,index=False,engine="openpyxl")
                    else:
                        pd.DataFrame(lista_dati).to_excel(out,index=False,engine="openpyxl")
                    st.download_button(f"📋 Copia",out.getvalue(),file_name=f"{key_form}_{date.today()}.xlsx",mime="application/octet-stream",use_container_width=True,key=f"dl_single_copy_{key_form}")

    with tab3:
        st.markdown("#### 🖨️ PDF con Scelta Form")
        st.markdown('<div style="background-color:#f1f8e9;border:3px solid #2e7d32;border-radius:12px;padding:20px;margin:15px 0;">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            chk_pdf_vol = st.checkbox(f"👤 Volontari", value=True, key="chk_pdf_vol")
            chk_pdf_post = st.checkbox(f"📍 Postazioni", value=True, key="chk_pdf_post")
            chk_pdf_emer = st.checkbox(f"🚨 Emergenze", value=True, key="chk_pdf_emer")
            chk_pdf_radio = st.checkbox(f"📻 DB Radio", value=True, key="chk_pdf_radio")
        with col2:
            chk_pdf_dist = st.checkbox(f"📡 Dist Radio", value=True, key="chk_pdf_dist")
            chk_pdf_eventi = st.checkbox(f"📅 Eventi", value=True, key="chk_pdf_eventi")
            chk_pdf_check = st.checkbox(f"✅ Check-in", value=True, key="chk_pdf_check")
            chk_pdf_nomi = st.checkbox(f"📝 Mem Nomi", value=False, key="chk_pdf_nomi")
        st.markdown('</div>', unsafe_allow_html=True)
        selected_pdf_count = sum([chk_pdf_vol, chk_pdf_post, chk_pdf_emer, chk_pdf_radio, chk_pdf_dist, chk_pdf_eventi, chk_pdf_check, chk_pdf_nomi])
        st.info(f"Form selezionati per PDF: {selected_pdf_count}/8")
        if st.button(f"🖨️ Crea PDF con {selected_pdf_count} Form", use_container_width=True, type="primary", key="btn_pdf_scelta", disabled=(selected_pdf_count==0)):
            try:
                from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
                from reportlab.lib.styles import getSampleStyleSheet
                from reportlab.lib import colors
                from reportlab.lib.pagesizes import A4
                buffer = BytesIO()
                doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=30, rightMargin=30, topMargin=30, bottomMargin=30)
                styles = getSampleStyleSheet()
                elements = []
                elements.append(Paragraph(f"ANA VARESE - PDF {selected_pdf_count} Form", styles['Heading1']))
                elements.append(Spacer(1, 20))
                form_map = []
                if chk_pdf_vol: form_map.append(("Volontari", st.session_state.dati))
                if chk_pdf_post: form_map.append(("Postazioni", st.session_state.postazioni))
                if chk_pdf_emer: form_map.append(("Emergenze", st.session_state.emergenze_lista))
                if chk_pdf_radio: form_map.append(("DB Radio", st.session_state.radio_db))
                if chk_pdf_dist: form_map.append(("Dist Radio", st.session_state.dist_radio))
                if chk_pdf_eventi: form_map.append(("Eventi", st.session_state.eventi_lista))
                if chk_pdf_check: form_map.append(("Check-in", st.session_state.checkin_lista))
                if chk_pdf_nomi: form_map.append(("Mem Nomi", st.session_state.mem_nomi))
                for nome_form, lista_dati in form_map:
                    if lista_dati:
                        elements.append(Paragraph(f"{nome_form} - {len(lista_dati)}", styles['Heading2']))
                        df_temp = pd.DataFrame(lista_dati) if not isinstance(lista_dati[0], str) else pd.DataFrame(lista_dati, columns=["Nome"])
                        if len(df_temp.columns) > 5:
                            df_temp = df_temp.iloc[:, :5]
                        df_temp = df_temp.head(15)
                        data = [list(df_temp.columns)] + df_temp.values.tolist()
                        table = Table(data)
                        table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e7d32')),('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),('FONTSIZE', (0, 0), (-1, -1), 6),('GRID', (0, 0), (-1, -1), 1, colors.black)]))
                        elements.append(table)
                        elements.append(Spacer(1, 20))
                doc.build(elements)
                buffer.seek(0)
                st.session_state["pdf_scelta"] = buffer.getvalue()
                st.session_state["pdf_scelta_count"] = selected_pdf_count
                st.success(f"✅ PDF creato con {selected_pdf_count} form!")
            except Exception as e:
                st.error(f"Errore PDF: {e}")

        if "pdf_scelta" in st.session_state:
            st.download_button(f"📥 Scarica PDF {st.session_state['pdf_scelta_count']} Form", st.session_state["pdf_scelta"], file_name=f"pdf_scelta_{st.session_state['pdf_scelta_count']}form_{date.today()}.pdf", mime="application/pdf", use_container_width=True, key="dl_pdf_scelta")

    with tab4:
        st.markdown("#### 📥 Import - COME VECCHIO APP.PY")
        st.info("✅ Ora puoi selezionare il file da importare come nel vecchio app.py!")

        col_imp1, col_imp2 = st.columns(2)
        with col_imp1:
            import_type=st.selectbox("Tipo Import *",["Volontari","Postazioni Mappa","Emergenze con Loghi","DB Radio","Distribuzione Radio","Eventi","Check-in","Mem Nomi"],key="import_type")
            modo_import=st.selectbox("Modalità *",["Aggiungi","Sovrascrivi"],key="modo_import")
        with col_imp2:
            file_type=st.selectbox("Formato *",["Excel","JSON"],key="file_type")
            st.markdown("---")
            st.markdown("**File da importare:**")

        # QUI C'ERA L'ERRORE - ORA CORRETTO CON FILE UPLOADER
        uploaded_file=st.file_uploader(f"📁 Seleziona file {import_type} ({file_type})",type=["xlsx","xls","json"],key="import_file")

        if uploaded_file is not None:
            st.success(f"✅ File selezionato: {uploaded_file.name} - {uploaded_file.size} bytes")
            st.markdown(f"**Tipo:** {import_type} | **Modalità:** {modo_import} | **Formato:** {file_type}")

            if st.button(f"📥 IMPORTA {import_type}",use_container_width=True,type="primary",key="btn_import"):
                try:
                    if file_type=="Excel":
                        df_import=pd.read_excel(uploaded_file,engine="openpyxl")
                        data_import=df_import.to_dict('records')
                    else:
                        data_import=json.load(uploaded_file)

                    if import_type=="Volontari":
                        if modo_import=="Sovrascrivi":
                            st.session_state.dati=data_import
                        else:
                            st.session_state.dati.extend(data_import)
                        save_json("dati_volontari.json",st.session_state.dati)
                    elif import_type=="Postazioni Mappa":
                        if modo_import=="Sovrascrivi":
                            st.session_state.postazioni=data_import
                        else:
                            st.session_state.postazioni.extend(data_import)
                        save_json("postazioni.json",st.session_state.postazioni)
                    elif import_type=="Emergenze con Loghi":
                        if modo_import=="Sovrascrivi":
                            st.session_state.emergenze_lista=data_import
                        else:
                            st.session_state.emergenze_lista.extend(data_import)
                        save_json("emergenze.json",st.session_state.emergenze_lista)
                    elif import_type=="DB Radio":
                        if modo_import=="Sovrascrivi":
                            st.session_state.radio_db=data_import
                        else:
                            st.session_state.radio_db.extend(data_import)
                        save_json("radio_db.json",st.session_state.radio_db)
                    elif import_type=="Distribuzione Radio":
                        if modo_import=="Sovrascrivi":
                            st.session_state.dist_radio=data_import
                        else:
                            st.session_state.dist_radio.extend(data_import)
                        save_json("dist_radio.json",st.session_state.dist_radio)
                    elif import_type=="Eventi":
                        if modo_import=="Sovrascrivi":
                            st.session_state.eventi_lista=data_import
                        else:
                            st.session_state.eventi_lista.extend(data_import)
                        save_json("eventi.json",st.session_state.eventi_lista)
                    elif import_type=="Check-in":
                        if modo_import=="Sovrascrivi":
                            st.session_state.checkin_lista=data_import
                        else:
                            st.session_state.checkin_lista.extend(data_import)
                        save_json("checkin.json",st.session_state.checkin_lista)
                    elif import_type=="Mem Nomi":
                        if isinstance(data_import, list) and len(data_import)>0 and isinstance(data_import[0], dict):
                            # Se è dict, estrai la colonna Nome
                            nomi=[d.get("Nome", d.get("Nomi", str(d))) for d in data_import]
                        else:
                            nomi=data_import
                        if modo_import=="Sovrascrivi":
                            st.session_state.mem_nomi=nomi if isinstance(nomi[0], str) else [str(x) for x in nomi]
                        else:
                            st.session_state.mem_nomi.extend([n for n in nomi if n not in st.session_state.mem_nomi])
                        save_json("mem_nomi.json",st.session_state.mem_nomi)

                    st.success(f"✅ Import riuscito! {len(data_import)} record importati in {import_type} - Modalità {modo_import}")
                    st.balloons()
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Errore import: {e}")
        else:
            st.warning("⚠️ Seleziona un file Excel o JSON da importare")

        st.divider()
        st.markdown("#### 📋 Anteprima dati attuali")
        col_ant1, col_ant2 = st.columns(2)
        with col_ant1:
            st.metric("Volontari", len(st.session_state.dati))
            st.metric("Postazioni", len(st.session_state.postazioni))
            st.metric("Emergenze", len(st.session_state.emergenze_lista))
            st.metric("Radio", len(st.session_state.radio_db))
        with col_ant2:
            st.metric("Dist Radio", len(st.session_state.dist_radio))
            st.metric("Eventi", len(st.session_state.eventi_lista))
            st.metric("Check-in", len(st.session_state.checkin_lista))
            st.metric("Mem Nomi", len(st.session_state.mem_nomi))

    st.markdown("---")
    st.markdown("### ✅ BACKUP COMPLETO CON IMPORT!")
    st.markdown("- **8 caselle** per scegliere i form da esportare")
    st.markdown("- **Import con selezione file** come vecchio app.py - CORRETTO!")