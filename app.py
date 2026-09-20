import streamlit as st
import pandas as pd
from io import BytesIO
import os, json, hashlib, requests
from datetime import datetime, date

try:
    import folium
    from streamlit_folium import st_folium
    HAS=True
except:
    HAS=False
try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PIL=True
except:
    HAS_PIL=False

st.set_page_config(page_title="ANA Varese", layout="wide")
st.markdown("""<style>.stApp{background-color:#e8f5e9!important}.stForm{background-color:#f1f8e9!important; border:2px solid #81c784!important; border-radius:12px!important; padding:20px!important}.stButton>button{background-color:#d32f2f!important; color:white!important; border:2px solid #b71c1c!important; font-weight:bold!important}</style>""", unsafe_allow_html=True)

def load(f,d):
    try:
        if os.path.exists(f):
            return json.load(open(f,'r',encoding='utf-8'))
    except:
        pass
    return d
def save(f,d):
    try:
        json.dump(d,open(f,'w',encoding='utf-8'),indent=2)
    except:
        pass
def fmt_date(d): return d.strftime("%d/%m/%Y") if isinstance(d,date) else str(d)
def export_excel(df):
    out=BytesIO()
    with pd.ExcelWriter(out,engine='openpyxl') as w:
        df.to_excel(w,index=False)
    return out.getvalue()

# DATI
FD='dati.json'; FP='post.json'; FI='icone.json'; FE='emerg.json'; FC='check.json'; FR='radio.json'; FR2='cons.json'; FPOP='popup.json'
for k,v in [('dati',[]),('post',[]),('icone',[]),('emerg',[]),('check',[]),('radio',[]),('cons',[]),('interventi_lista',[]),('menu','Dashboard'),('lat',45.8205),('lon',8.8250),('com',''),('via',''),('zoom',16),('clat',None),('clon',None),('exp1',False),('popup_shown',False)]:
    if k not in st.session_state:
        st.session_state[k]=v

st.session_state.dati=load(FD,[]); st.session_state.post=load(FP,[]); st.session_state.icone=load(FI,[]); st.session_state.emerg=load(FE,[]); st.session_state.check=load(FC,[]); st.session_state.radio=load(FR,[]); st.session_state.cons=load(FR2,[]); st.session_state.interventi_lista=load(FE,[])

# PRIMA PAGINA - SOLO TUA IMMAGINE FUMETTO PICCOLA 250px
if not st.session_state.popup_shown:
    st.markdown("<h1 style='text-align:center;color:#0e7a3d;'>ANA VARESE - VOLONTARIATO</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center;color:#0e7a3d;'>Ciao Ragazzi, Buon Lavoro!</h3>", unsafe_allow_html=True)
    st.divider()
    c1,c2,c3=st.columns([1,1,1])
    with c2:
        for img_name in ['copertina.jpg','copertina_fumetto.jpg','fumetto.jpg']:
            if os.path.exists(img_name):
                st.image(img_name,width=250)
                st.success(f"TUA IMMAGINE FUMETTO PICCOLA: {img_name} - SOLO PRIMA PAGINA")
                break
        else:
            st.warning("Carica copertina.jpg come tua immagine fumetto piccola 250px")
        if st.button("ENTRA NEL SISTEMA",type="primary",use_container_width=True):
            st.session_state.popup_shown=True; st.rerun()
    st.stop()

def pagina_interventi_emergenza():
    st.markdown("## INTERVENTI EMERGENZA")
    with st.form("form_emergenza", clear_on_submit=True):
        c1,c2,c3=st.columns(3)
        with c1:
            data_int=st.date_input("Data *")
            ora_int=st.time_input("Ora *")
        with c2:
            comune_int=st.text_input("Comune *")
            via_int=st.text_input("Via *")
        with c3:
            civico_int=st.text_input("Civico")
            odv_int=st.selectbox("ODV Operativa *", ["ANA Varese","ANA Sezione Varese","Protezione Civile Lombardia","Croce Rossa","Altro"])
        azione_int=st.text_area("Azione *", height=100)
        salva=st.form_submit_button("SALVA INTERVENTO EMERGENZA", use_container_width=True)
        if salva:
            if comune_int and via_int and azione_int:
                st.session_state.interventi_lista.append({"Data":str(data_int),"Ora":str(ora_int),"Comune":comune_int,"Via":via_int,"Civico":civico_int,"ODV Operativa":odv_int,"Azione":azione_int})
                save(FE,st.session_state.interventi_lista)
                st.success("Salvato!")
                st.rerun()
    if st.session_state.interventi_lista:
        df=pd.DataFrame(st.session_state.interventi_lista)
        st.dataframe(df, use_container_width=True)
        st.download_button("Scarica CSV", df.to_csv(index=False).encode('utf-8'), "interventi_emergenza.csv")

# MENU
with st.sidebar:
    st.markdown('**MENU COMPLETO**')
    opts=['Dashboard','Volontari','Mappa','Libreria Icone','Interventi Emergenza','Check In','DB Radio','Consegna Radio','Backup']
    sel=st.radio('Vai a',opts,index=0)
    st.session_state.menu=sel

scelta=st.session_state.menu

if scelta=='Dashboard':
    st.markdown("## ANA Varese - Dashboard")
    c1,c2=st.columns(2)
    with c1:
        if st.button('VOLONTARI',use_container_width=True): st.session_state.menu='Volontari'; st.rerun()
        if st.button('MAPPA',use_container_width=True): st.session_state.menu='Mappa'; st.rerun()
        if st.button('INTERVENTI EMERGENZA',use_container_width=True): st.session_state.menu='Interventi Emergenza'; st.rerun()
        if st.button('BACKUP IMPORT EXPORT',use_container_width=True,type="primary"): st.session_state.menu='Backup'; st.rerun()
    with c2:
        if st.button('CHECK IN',use_container_width=True): st.session_state.menu='Check In'; st.rerun()
        if st.button('DB RADIO',use_container_width=True): st.session_state.menu='DB Radio'; st.rerun()
        if st.button('CONSEGNA RADIO',use_container_width=True): st.session_state.menu='Consegna Radio'; st.rerun()
    st.divider()
    c1,c2,c3,c4=st.columns(4)
    with c1: st.metric('Volontari',len(st.session_state.dati))
    with c2: st.metric('Postazioni',len(st.session_state.post))
    with c3: st.metric('Interventi',len(st.session_state.interventi_lista))
    with c4: st.metric('Radio',len(st.session_state.radio))
    st.divider()
    tab1, tab2, tab3 = st.tabs(["Da Anagrafica Esistente", "Inserimento Manuale", "INTERVENTI EMERGENZA"])
    with tab1:
        st.markdown("### Da Anagrafica Esistente")
        if st.session_state.dati:
            st.dataframe(pd.DataFrame(st.session_state.dati),use_container_width=True)
    with tab2:
        st.markdown("### Inserimento Manuale")
        with st.form("form_manuale"):
            nome = st.text_input("Nome e Cognome *")
            assoc = st.text_input("Associazione *")
            cell = st.text_input("Cellulare *")
            ruolo = st.selectbox("Ruolo *", ["Volontario", "Caposquadra", "Coordinatore", "Autista", "Radio", "Logistica", "Segreteria", "Sanitario", "Altro"])
            if st.form_submit_button("Salva"):
                if nome:
                    st.session_state.dati.append({"Nome": nome, "Associazione": assoc, "Cellulare": cell, "Ruolo": ruolo})
                    save(FD,st.session_state.dati)
                    st.success(f"Aggiunto {nome}")
                    st.rerun()
    with tab3:
        pagina_interventi_emergenza()

elif scelta=='Backup':
    st.markdown("## BACKUP - EXPORT E IMPORT DATI PER I VARI FORM - SISTEMATO")
    st.info("Qui puoi fare export e import di tutti i form separatamente e backup completo")

    tab_export, tab_import, tab_completo = st.tabs(["📤 EXPORT SINGOLI FORM", "📥 IMPORT SINGOLI FORM", "💾 BACKUP COMPLETO TUTTI I FORM"])

    with tab_export:
        st.markdown("### Export singoli form - Scarica Excel per ogni form")
        c1,c2,c3=st.columns(3)
        with c1:
            st.markdown("**VOLONTARI E MAPPA**")
            if st.session_state.dati:
                st.download_button('📥 EXPORT VOLONTARI',export_excel(pd.DataFrame(st.session_state.dati)),file_name='Volontari.xlsx',use_container_width=True,key='exp_vol')
                st.caption(f"{len(st.session_state.dati)} volontari")
            else:
                st.warning("Nessun volontario")
            if st.session_state.post:
                st.download_button('📥 EXPORT MAPPA POSTAZIONI',export_excel(pd.DataFrame(st.session_state.post)),file_name='Mappa_Postazioni.xlsx',use_container_width=True,key='exp_mappa')
                st.caption(f"{len(st.session_state.post)} postazioni")
            else:
                st.warning("Nessuna postazione")
        with c2:
            st.markdown("**EMERGENZE E CHECK IN**")
            if st.session_state.interventi_lista:
                st.download_button('📥 EXPORT INTERVENTI EMERGENZA',export_excel(pd.DataFrame(st.session_state.interventi_lista)),file_name='Interventi_Emergenza.xlsx',use_container_width=True,key='exp_int')
                st.caption(f"{len(st.session_state.interventi_lista)} interventi")
            else:
                st.warning("Nessun intervento")
            if st.session_state.check:
                st.download_button('📥 EXPORT CHECK IN',export_excel(pd.DataFrame(st.session_state.check)),file_name='CheckIn.xlsx',use_container_width=True,key='exp_check')
                st.caption(f"{len(st.session_state.check)} check in")
            else:
                st.warning("Nessun check in")
        with c3:
            st.markdown("**RADIO**")
            if st.session_state.radio:
                st.download_button('📥 EXPORT DB RADIO',export_excel(pd.DataFrame(st.session_state.radio)),file_name='DB_Radio.xlsx',use_container_width=True,key='exp_radio')
                st.caption(f"{len(st.session_state.radio)} radio")
            else:
                st.warning("Nessuna radio")
            if st.session_state.cons:
                st.download_button('📥 EXPORT CONSEGNA RADIO',export_excel(pd.DataFrame(st.session_state.cons)),file_name='Consegna_Radio.xlsx',use_container_width=True,key='exp_cons')
                st.caption(f"{len(st.session_state.cons)} consegne")
            else:
                st.warning("Nessuna consegna")

    with tab_import:
        st.markdown("### Import singoli form - Carica Excel per ogni form")
        c1,c2,c3=st.columns(3)
        with c1:
            st.markdown("**VOLONTARI E MAPPA**")
            up_vol=st.file_uploader('Import Volontari (Volontari.xlsx)',type=['xlsx'],key='up_vol')
            if up_vol:
                df_up=pd.read_excel(up_vol)
                st.dataframe(df_up.head(),use_container_width=True)
                if st.button(f'IMPORTA {len(df_up)} VOLONTARI',key='imp_vol',use_container_width=True,type="primary"):
                    for _,row in df_up.iterrows():
                        st.session_state.dati.append(row.to_dict())
                    save(FD,st.session_state.dati)
                    st.success(f"Importati {len(df_up)} volontari!"); st.rerun()
            up_mappa=st.file_uploader('Import Mappa (Mappa_Postazioni.xlsx)',type=['xlsx'],key='up_mappa')
            if up_mappa:
                df_up=pd.read_excel(up_mappa)
                st.dataframe(df_up.head(),use_container_width=True)
                if st.button(f'IMPORTA {len(df_up)} POSTAZIONI',key='imp_mappa',use_container_width=True,type="primary"):
                    for _,row in df_up.iterrows():
                        st.session_state.post.append(row.to_dict())
                    save(FP,st.session_state.post)
                    st.success(f"Importate {len(df_up)} postazioni!"); st.rerun()
        with c2:
            st.markdown("**EMERGENZE E CHECK IN**")
            up_int=st.file_uploader('Import Interventi (Interventi_Emergenza.xlsx)',type=['xlsx'],key='up_int')
            if up_int:
                df_up=pd.read_excel(up_int)
                st.dataframe(df_up.head(),use_container_width=True)
                if st.button(f'IMPORTA {len(df_up)} INTERVENTI',key='imp_int',use_container_width=True,type="primary"):
                    for _,row in df_up.iterrows():
                        st.session_state.interventi_lista.append(row.to_dict())
                    save(FE,st.session_state.interventi_lista)
                    st.success(f"Importati {len(df_up)} interventi!"); st.rerun()
            up_check=st.file_uploader('Import Check In (CheckIn.xlsx)',type=['xlsx'],key='up_check')
            if up_check:
                df_up=pd.read_excel(up_check)
                st.dataframe(df_up.head(),use_container_width=True)
                if st.button(f'IMPORTA {len(df_up)} CHECK IN',key='imp_check',use_container_width=True,type="primary"):
                    for _,row in df_up.iterrows():
                        st.session_state.check.append(row.to_dict())
                    save(FC,st.session_state.check)
                    st.success(f"Importati {len(df_up)} check in!"); st.rerun()
        with c3:
            st.markdown("**RADIO**")
            up_radio=st.file_uploader('Import DB Radio (DB_Radio.xlsx)',type=['xlsx'],key='up_radio')
            if up_radio:
                df_up=pd.read_excel(up_radio)
                st.dataframe(df_up.head(),use_container_width=True)
                if st.button(f'IMPORTA {len(df_up)} RADIO',key='imp_radio',use_container_width=True,type="primary"):
                    for _,row in df_up.iterrows():
                        st.session_state.radio.append(row.to_dict())
                    save(FR,st.session_state.radio)
                    st.success(f"Importate {len(df_up)} radio!"); st.rerun()
            up_cons=st.file_uploader('Import Consegna Radio (Consegna_Radio.xlsx)',type=['xlsx'],key='up_cons')
            if up_cons:
                df_up=pd.read_excel(up_cons)
                st.dataframe(df_up.head(),use_container_width=True)
                if st.button(f'IMPORTA {len(df_up)} CONSEGNE',key='imp_cons',use_container_width=True,type="primary"):
                    for _,row in df_up.iterrows():
                        st.session_state.cons.append(row.to_dict())
                    save(FR2,st.session_state.cons)
                    st.success(f"Importate {len(df_up)} consegne!"); st.rerun()

    with tab_completo:
        st.markdown("### Backup completo - Tutti i form in un unico file Excel con più fogli")
        c1,c2=st.columns(2)
        with c1:
            if st.button('🔄 CREA BACKUP COMPLETO TUTTI I FORM',type='primary',use_container_width=True):
                out=BytesIO()
                with pd.ExcelWriter(out,engine='openpyxl') as writer:
                    if st.session_state.dati: pd.DataFrame(st.session_state.dati).to_excel(writer,sheet_name='Volontari',index=False)
                    if st.session_state.post: pd.DataFrame(st.session_state.post).to_excel(writer,sheet_name='Mappa',index=False)
                    if st.session_state.interventi_lista: pd.DataFrame(st.session_state.interventi_lista).to_excel(writer,sheet_name='InterventiEmergenza',index=False)
                    if st.session_state.check: pd.DataFrame(st.session_state.check).to_excel(writer,sheet_name='CheckIn',index=False)
                    if st.session_state.radio: pd.DataFrame(st.session_state.radio).to_excel(writer,sheet_name='DBRadio',index=False)
                    if st.session_state.cons: pd.DataFrame(st.session_state.cons).to_excel(writer,sheet_name='ConsegnaRadio',index=False)
                    if st.session_state.icone: pd.DataFrame(st.session_state.icone).to_excel(writer,sheet_name='Icone',index=False)
                st.session_state['bk_all']=out.getvalue()
                st.success('✅ Backup completo TUTTI I FORM creato! Ora puoi scaricarlo')
                st.balloons()
            if 'bk_all' in st.session_state:
                st.download_button('💾 SCARICA BACKUP COMPLETO TUTTI I FORM',st.session_state['bk_all'],file_name=f'BACKUP_COMPLETO_{datetime.now().strftime("%Y%m%d_%H%M")}.xlsx',use_container_width=True,type='primary')
        with c2:
            st.markdown("**Ripristina da backup completo**")
            up_bk=st.file_uploader('Carica Backup Completo (BACKUP_COMPLETO_*.xlsx)',type=['xlsx'],key='up_bk')
            if up_bk:
                try:
                    xls=pd.ExcelFile(up_bk)
                    st.write(f"Fogli trovati: {xls.sheet_names}")
                    for sheet in xls.sheet_names:
                        df_tmp=pd.read_excel(xls,sheet)
                        st.caption(f"{sheet}: {len(df_tmp)} righe")
                    if st.button('⚠️ RIPRISTINA TUTTI I FORM DA BACKUP - SOVRASCRIVE DATI ATTUALI',type='primary',use_container_width=True):
                        if 'Volontari' in xls.sheet_names:
                            st.session_state.dati=pd.read_excel(xls,'Volontari').to_dict('records'); save(FD,st.session_state.dati)
                        if 'Mappa' in xls.sheet_names:
                            st.session_state.post=pd.read_excel(xls,'Mappa').to_dict('records'); save(FP,st.session_state.post)
                        if 'InterventiEmergenza' in xls.sheet_names:
                            st.session_state.interventi_lista=pd.read_excel(xls,'InterventiEmergenza').to_dict('records'); save(FE,st.session_state.interventi_lista)
                        if 'CheckIn' in xls.sheet_names:
                            st.session_state.check=pd.read_excel(xls,'CheckIn').to_dict('records'); save(FC,st.session_state.check)
                        if 'DBRadio' in xls.sheet_names:
                            st.session_state.radio=pd.read_excel(xls,'DBRadio').to_dict('records'); save(FR,st.session_state.radio)
                        if 'ConsegnaRadio' in xls.sheet_names:
                            st.session_state.cons=pd.read_excel(xls,'ConsegnaRadio').to_dict('records'); save(FR2,st.session_state.cons)
                        if 'Icone' in xls.sheet_names:
                            st.session_state.ic