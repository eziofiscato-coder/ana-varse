    elif m == 'Interventi Emergenza':
        hdr_form('INTERVENTI EMERGENZA - COLLEGATO A EMERGENZA BLINDATA')
        if not st.session_state.interventi_blindato:
            if st.session_state.emergenze:
                lista_em = [e.get('Tipo','') + ' - ' + e.get('Luogo','') for e in st.session_state.emergenze]
                em = st.selectbox('EMERGENZA da associare e blindare', ['Nessuna'] + lista_em, key='em_blind_int')
            else:
                st.warning('Nessuna Emergenza - crea prima in Emergenze')
                em = 'Nessuna'
            if st.button('BLINDA INTERVENTI SU EMERGENZA', type='primary', use_container_width=True):
                if em!= 'Nessuna':
                    st.session_state.interventi_emergenza_blindata = em
                    st.session_state.interventi_blindato = True
                    st.rerun()
        else:
            st.success(f"INTERVENTI BLINDATO SU: {st.session_state.interventi_emergenza_blindata}")
            if st.button('SBLOCCA INTERVENTI', type='primary', use_container_width=True):
                st.session_state.interventi_blindato = False
                st.session_state.interventi_emergenza_blindata = None
                st.rerun()
        st.divider()
        if st.session_state.interventi_blindato:
            with st.form('form_int'):
                st.text_input('EMERGENZA BLINDATA', value=st.session_state.interventi_emergenza_blindata, disabled=True)
                c1,c2,c3 = st.columns(3)
                with c1:
                    data_int = st.date_input('Data *', value=date.today())
                    ora_int = st.time_input('Ora *', value=datetime.now().time())
                with c2:
                    comune_int = st.text_input('Comune *')
                    via_int = st.text_input('Via *')
                with c3:
                    civico_int = st.text_input('Civico')
                    odv_int = st.selectbox('ODV Operativa *', ['ANA Varese','ANA Sezione Varese','Protezione Civile Lombardia','Croce Rossa','Altro'])
                # CAMPO STATO INTERVENTO AGGIUNTO QUI
                c4,c5 = st.columns(2)
                with c4:
                    stato_int = st.selectbox('STATO INTERVENTO *', ['Operativo','In Stand By','Chiuso','In Corso','Completato','Annullato','Sospeso','In Attesa'])
                with c5:
                    priorita_int = st.selectbox('Priorita', ['Bassa','Media','Alta','Urgente'])
                azione_int = st.text_area('Azione Intervento *', height=120)
                note_int = st.text_input('Note')
                if st.form_submit_button('SALVA INTERVENTO COLLEGATO A EMERGENZA BLINDATA', use_container_width=True, type='primary'):
                    if comune_int and via_int and azione_int:
                        iv = {}
                        iv['Data'] = str(data_int)
                        iv['Ora'] = str(ora_int)
                        iv['EmergenzaBlindata'] = st.session_state.interventi_emergenza_blindata
                        iv['Comune'] = comune_int
                        iv['Via'] = via_int
                        iv['Civico'] = civico_int
                        iv['ODV'] = odv_int
                        iv['Stato'] = stato_int
                        iv['Priorita'] = priorita_int
                        iv['Azione'] = azione_int
                        iv['Note'] = note_int
                        st.session_state.interventi.append(iv)
                        st.success(f'Intervento {stato_int} salvato collegato a {st.session_state.interventi_emergenza_blindata}')
                        st.balloons()
                    else:
                        st.error('Compila Comune, Via, Azione')
        if st.session_state.interventi:
            st.divider()
            st.markdown(f"### Elenco Interventi - {len(st.session_state.interventi)} interventi")
            df_show = pd.DataFrame(st.session_state.interventi)
            st.dataframe(df_show, use_container_width=True, hide_index=True)
            c1,c2 = st.columns(2)
            pdf = to_pdf(df_show, 'Interventi Emergenza ANA Varese')
            if pdf:
                c1.download_button('PDF Interventi', pdf, file_name='interventi_emergenza.pdf', mime='application/pdf', use_container_width=True)
            c2.download_button('Excel Interventi', to_excel(df_show), file_name='interventi_emergenza.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', use_container_width=True)
