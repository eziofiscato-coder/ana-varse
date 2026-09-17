import streamlit as st
import pandas as pd
from datetime import datetime, date
from io import BytesIO
import base64, os

st.set_page_config(page_title="ANA Varese - Verde ANA", page_icon="🟢", layout="wide")

st.markdown("""
<style>
.stApp{background-color:#e8f5e9!important;}
.main.block-container{background-color:rgba(255,255,255,0.93)!important; border-radius:18px; padding:25px!important;}
[data-testid="stSidebar"]{background-color:#a5d6a7!important; border-right:4px solid #2e7d32!important;}
.stForm{background-color:#c8e6c9!important; border:3px solid #2e7d32!important; border-radius:15px!important; padding:20px!important;}
.stButton>button{background-color:#2e7d32!important; color:white!important; border:2px solid #1b5e20!important; font-weight:bold!important; border-radius:12px!important; min-height:60px!important;}
div[data-testid="stFormSubmitButton"]>button{background-color:#d32f2f!important; border:3px solid #b71c1c!important; color:white!important;}
h1,h2,h3{color:#1b5e20!important;}
</style>
""", unsafe_allow_html=True)

ICONS = {
 "volontario": {"nome":"Volontario","icon":"👤"}, "sede": {"nome":"Sede","icon":"🏠"},
 "radio": {"nome":"Radio","icon":"📻"}, "emergenza": {"nome":"Emergenza","icon":"🚨"},
 "protezione_civile": {"nome":"Prot Civile","icon":"🛡️"}, "ospedale": {"nome":"Ospedale","icon":"🏥"},
 "postazione": {"nome":"Postazione","icon":"📍"}, "auto": {"nome":"Auto","icon":"🚗"},
 "elicottero": {"nome":"Elicottero","icon":"🚁"}, "incendio": {"nome":"Incendio","icon":"🔥"},
 "alluvione": {"nome":"Alluvione","icon":"🌊"}, "campo_base": {"nome":"Campo Base","icon":"⛺"},
}

for k,v in [("authenticated",False),("emergenze_lista",[]),("interventi_lista",[]),("dati",[]),("mem_nomi",["Mario Rossi","Luigi Bianchi","Giuseppe Verdi"]),("postazioni",[]),("menu_scelta","🏠 Dashboard")]:
    if k not in st.session_state:
        st.session_state[k]=v

def get_b64(p):
    try:
        if os.path.exists(p):
            with open(p,"rb") as f: return base64.b64encode(f.read()).decode()
    except: pass
    return ""

def torna_dashboard():
    if st.button("Torna Dashboard", use_container_width=True, key=f"back_{datetime.now().microsecond}"):
        st.session_state.menu_scelta="🏠 Dashboard"; st.rerun()

LOGHI="<div style='background:#a5d6a7; padding:12px; border-radius:12px; border:3px solid #2e7d32; text-align:center;'><h3 style='color:#1b5e20; margin:0;'>ANA Varese - Protezione Civile</h3></div>"

if not st.session_state.authenticated:
    st.markdown(LOGHI, unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center; color:#1b5e20; background:#a5d6a7; padding:15px; border-radius:12px; border:3px solid #2e7d32;'>Accesso Riservato - admin / ana2024</h2>", unsafe_allow_html=True)
    c1,c2,c3=st.columns([1,2,1])
    with c2:
        with st.form("login"):
            u=st.text_input("Username", value="admin"); p=st.text_input("Password", type="password", value="ana2024")
            if st.form_submit_button("ENTRA", use_container_width=True, type="primary"):
                if u=="admin" and p=="ana2024":
                    st.session_state.authenticated=True; st.rerun()
                else: st.error("admin / ana2024")
    st.stop()

with st.sidebar:
    st.markdown(LOGHI, unsafe_allow_html=True)
    opzioni=["🏠 Dashboard","🚨 Emergenze con Loghi","🗺️ Mappa Postazioni","🚨 Interventi Emergenza","👥 Volontari","💾 Backup"]
    idx = opzioni.index(st.session_state.menu_scelta) if st.session_state.menu_scelta in opzioni else 0
    sel=st.radio("MENU", opzioni, index=idx)
    if sel!=st.session_state.menu_scelta:
        st.session_state.menu_scelta=sel; st.rerun()
    if st.button("Logout", use_container_width=True, type="primary"):
        st.session_state.authenticated=False; st.rerun()

scelta=st.session_state.menu_scelta

if scelta=="🏠 Dashboard":
    st.markdown(LOGHI, unsafe_allow_html=True)
    st.markdown("<h2 style='color:#1b5e20; background:#a5d6a7; padding:15px; border-radius:12px; border:3px solid #2e7d32; text-align:center;'>Dashboard ANA Varese</h2>", unsafe_allow_html=True)
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Interventi", len(st.session_state.interventi_lista))
    c2.metric("Emergenze", len(st.session_state.emergenze_lista))
    c3.metric("Volontari", len(st.session_state.mem_nomi))
    c4.metric("Postazioni", len(st.session_state.postazioni))
    st.markdown("### MENU SCELTA RAPIDA - ORA FUNZIONA")
    r1c1,r1c2,r1c3,r1c4=st.columns(4)
    with r1c1:
        if st.button("Emergenze con Loghi", key="q1", use_container_width=True):
            st.session_state.menu_scelta="🚨 Emergenze con Loghi"; st.rerun()
    with r1c2:
        if st.button("Interventi", key="q2", use_container_width=True):
            st.session_state.menu_scelta="🚨 Interventi Emergenza"; st.rerun()
    with r1c3:
        if st.button("Mappa", key="q3", use_container_width=True):
            st.session_state.menu_scelta="🗺️ Mappa Postazioni"; st.rerun()
    with r1c4:
        if st.button("Volontari", key="q4", use_container_width=True):
            st.session_state.menu_scelta="👥 Volontari"; st.rerun()

elif scelta=="🚨 Emergenze con Loghi":
    st.markdown(LOGHI, unsafe_allow_html=True)
    torna_dashboard()
    st.markdown("#### Libreria Loghi")
    cols=st.columns(6)
    for i,(k,v) in enumerate(ICONS.items()):
        with cols[i%6]:
            st.markdown(f"<div style='background:white; border:2px solid #2e7d32; border-radius:10px; padding:8px; text-align:center;'><div style='font-size:28px;'>{v['icon']}</div><div style='font-size:10px;'>{v['nome']}</div></div>", unsafe_allow_html=True)
    st.divider()
    with st.form("form_em", clear_on_submit=True):
        c1,c2,c3=st.columns(3)
        with c1: data_em=st.date_input("Data *", value=date.today()); comune=st.text_input("Comune *", value="Varese")
        with c2: via=st.text_input("Via *"); tipo_key=st.selectbox("Tipo + Logo *", list(ICONS.keys()), format_func=lambda x: f"{ICONS[x]['icon']} {ICONS[x]['nome']}")
        with c3: odv=st.selectbox("ODV", ["ANA Varese","Prot Civile","Altro"]); st.markdown(f"<div style='background:#c8e6c9; border:3px solid #2e7d32; border-radius:12px; padding:10px; text-align:center;'><div style='font-size:40px;'>{ICONS[tipo_key]['icon']}</div><b>{ICONS[tipo_key]['nome']}</b></div>", unsafe_allow_html=True)
        desc=st.text_area("Descrizione *", height=80)
        if st.form_submit_button("SALVA CON LOGO", use_container_width=True, type="primary"):
            if comune and via and desc:
                st.session_state.emergenze_lista.append({"Data":str(data_em),"Logo":ICONS[tipo_key]['icon'],"Tipo":ICONS[tipo_key]['nome'],"Comune":comune,"Via":via,"ODV":odv,"Descrizione":desc})
                st.success(f"Salvata {ICONS[tipo_key]['icon']}!"); st.rerun()
    if st.session_state.emergenze_lista:
        df=pd.DataFrame(st.session_state.emergenze_lista)
        st.markdown(f"### Tabella {len(df)} Emergenze con colonna Logo")
        for idx,row in df.iterrows():
            with st.container(border=True):
                cL,cI=st.columns([1,4])
                with cL: st.markdown(f"<div style='font-size:45px; text-align:center; background:#e8f5e9; border:2px solid #2e7d32; border-radius:12px; padding:10px;'>{row['Logo']}</div>", unsafe_allow_html=True)
                with cI: st.markdown(f"**{row['Logo']} {row['Tipo']}** | {row['Comune']} {row['Via']} | {row['Data']}"); st.write(row['Descrizione'])
        st.dataframe(df, use_container_width=True)
    torna_dashboard()

elif scelta=="🗺️ Mappa Postazioni":
    st.markdown(LOGHI, unsafe_allow_html=True)
    st.markdown("<h2 style='color:#1b5e20; background:#a5d6a7; padding:12px; border-radius:12px; border:3px solid #2e7d32;'>Mappa Postazioni - Aggancio Google / OSM / Waze</h2>", unsafe_allow_html=True)
    torna_dashboard()
    with st.form("post_form", clear_on_submit=True):
        c1,c2=st.columns(2)
        with c1:
            nome=st.text_input("Nome Postazione *", placeholder="Posto 1 - Ingresso")
            comune=st.text_input("Comune *", value="Varese")
            via=st.text_input("Via *", placeholder="Via Sacco")
        with c2:
            lat=st.text_input("Latitudine *", placeholder="45.8205")
            lon=st.text_input("Longitudine *", placeholder="8.8255")
            civico=st.text_input("Civico")
        note_post=st.text_area("Note", height=60)
        if st.form_submit_button("SALVA POSTAZIONE", use_container_width=True, type="primary"):
            if nome and lat and lon:
                st.session_state.postazioni.append({"Postazione":nome,"Comune":comune,"Via":via,"Civico":civico,"Latitudine":lat,"Longitudine":lon,"Note":note_post,"Data":str(date.today())})
                st.success(f"Salvata {nome}!"); st.rerun()
    if st.session_state.postazioni:
        dfp=pd.DataFrame(st.session_state.postazioni)
        try:
            dfm=dfp.copy()
            dfm["lat"]=pd.to_numeric(dfm["Latitudine"].astype(str).str.replace(",","."), errors='coerce')
            dfm["lon"]=pd.to_numeric(dfm["Longitudine"].astype(str).str.replace(",","."), errors='coerce')
            dfm=dfm.dropna(subset=["lat","lon"])
            if not dfm.empty: st.map(dfm[["lat","lon"]], zoom=11)
        except: pass
        st.divider()
        st.markdown("### Vai alle coordinate - Clicca per navigare")
        for _,r in dfp.iterrows():
            with st.container(border=True):
                c1,c2,c3,c4=st.columns([2,2,2,2])
                with c1: st.markdown(f"**{r['Postazione']}**"); st.caption(f"{r['Comune']} - {r['Via']} {r['Civico']}")
                with c2: st.link_button("Google Map", f"https://www.google.com/maps/search/?api=1&query={r['Latitudine']},{r['Longitudine']}", use_container_width=True)
                with c3: st.link_button("Street Map OSM", f"https://www.openstreetmap.org/?mlat={r['Latitudine']}&mlon={r['Longitudine']}#map=17/{r['Latitudine']}/{r['Longitudine']}", use_container_width=True)
                with c4: st.link_button("Waze", f"https://waze.com/ul?ll={r['Latitudine']},{r['Longitudine']}&navigate=yes", use_container_width=True)
        st.dataframe(dfp, use_container_width=True)
    torna_dashboard()

elif scelta=="👥 Volontari":
    st.markdown(LOGHI, unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center; color:#0e7a3d;'>VOLONTARIATO Sezione di Varese - Sottomaschere</h2>", unsafe_allow_html=True)
    torna_dashboard()
    tab1, tab2, tab3, tab4 = st.tabs(["Nuova Anagrafica Completa", "Lista Volontari", "Cerca/Modifica", "Statistiche & Export"])
    with tab1:
        with st.container(border=True):
            st.markdown("#### Scheda Anagrafica Completa con Sottomaschere")
            with st.form("form_vol_completa", clear_on_submit=False):
                st.markdown("##### Dati Personali")
                c1,c2,c3,c4=st.columns(4)
                with c1:
                    nome_v=st.text_input("Nome *"); cognome_v=st.text_input("Cognome *"); sesso_v=st.selectbox("Sesso", ["M","F","Altro"])
                with c2:
                    data_nascita_v=st.date_input("Data Nascita", value=datetime(1980,1,15)); luogo_nascita_v=st.text_input("Luogo Nascita"); cf_v=st.text_input("Codice Fiscale *", placeholder="RSSMRA80A01L682K")
                with c3:
                    gruppo_sang=st.selectbox("Gruppo Sanguigno", ["--","0+","0-","A+","A-","B+","B-","AB+","AB-"]); taglia_v=st.selectbox("Taglia", ["--","XS","S","M","L","XL","XXL"])
                with c4:
                    stato_civ=st.selectbox("Stato Civile", ["--","Celibe","Coniugato","Divorziato","Vedovo"])
                st.divider()
                st.markdown("##### Residenza")
                c1,c2,c3,c4=st.columns(4)
                with c1: comune_res=st.text_input("Comune Residenza *", value="Varese"); via_res=st.text_input("Via *")
                with c2: civico_res=st.text_input("Civico *"); cap_res=st.text_input("CAP")
                with c3: prov_res=st.text_input("Prov", value="VA"); lat_res=st.text_input("Lat", placeholder="45.8205")
                with c4: lon_res=st.text_input("Lon", placeholder="8.8255")
                st.divider()
                st.markdown("##### Contatti & Emergenza")
                c1,c2,c3=st.columns(3)
                with c1: cell_v=st.text_input("Cellulare *"); tel_v=st.text_input("Telefono")
                with c2: email_v=st.text_input("Email *"); contatto_em=st.text_input("Contatto Emergenza - Nome")
                with c3: tel_em=st.text_input("Tel Emergenza")
                st.divider()
                st.markdown("##### Dati ANA")
                c1,c2,c3=st.columns(3)
                with c1: sezione_v=st.text_input("Sezione", value="Varese"); gruppo_v=st.text_input("Gruppo"); tessera_v=st.text_input("Tessera *")
                with c2: ruolo_v=st.selectbox("Ruolo *", ["Volontario","Capo Squadra","Coordinatore","Autista","Radio","Logistica","Sanitario","Altro"]); stato_serv=st.selectbox("Stato Servizio", ["Attivo","In prova","Sospeso","Non attivo"])
                with c3: patente_v=st.selectbox("Patente", ["--","B","C","D","BE","CE"]); anni_serv=st.number_input("Anni servizio",0,60,0)
                note_v=st.text_area("Note generali", height=80)
                if st.form_submit_button("SALVA ANAGRAFICA COMPLETA", type="primary", use_container_width=True):
                    if nome_v and cognome_v and cf_v and cell_v:
                        nome_completo=f"{nome_v} {cognome_v}"
                        record={"Nome":nome_v,"Cognome":cognome_v,"Nome e Cognome":nome_completo,"Sesso":sesso_v,"Data Nascita":str(data_nascita_v),"Luogo Nascita":luogo_nascita_v,"Codice Fiscale":cf_v.upper(),"Gruppo Sanguigno":gruppo_sang,"Taglia":taglia_v,"Stato Civile":stato_civ,"Comune Residenza":comune_res,"Via":via_res,"Civico":civico_res,"CAP":cap_res,"Provincia":prov_res,"Lat":lat_res,"Lon":lon_res,"Cellulare":cell_v,"Telefono":tel_v,"Email":email_v,"Contatto Emergenza":contatto_em,"Tel Emergenza":tel_em,"Sezione":sezione_v,"Gruppo":gruppo_v,"Tessera":tessera_v,"Ruolo":ruolo_v,"Stato Servizio":stato_serv,"Patente":patente_v,"Anni Servizio":anni_serv,"Note":note_v,"Data Inserimento":str(date.today())}
                        st.session_state.dati.append(record)
                        if nome_completo not in st.session_state.mem_nomi:
                            st.session_state.mem_nomi.append(nome_completo)
                        st.success(f"Salvato {nome_completo} CF {cf_v}"); st.balloons(); st.rerun()
                    else:
                        st.error("Nome, Cognome, CF, Cellulare obbligatori")
    with tab2:
        if st.session_state.dati:
            df=pd.DataFrame(st.session_state.dati)
            st.dataframe(df.iloc[::-1], use_container_width=True, hide_index=True)
            output=BytesIO()
            df.to_excel(output, index=False, engine="openpyxl")
            st.download_button("Scarica Excel", output.getvalue(), file_name="anagrafica_completa.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        else:
            st.info("Nessun volontario")
    with tab3:
        cerca=st.text_input("Cerca per Nome, CF o Tessera", placeholder="Rossi, RSSMRA...")
        if cerca and st.session_state.dati:
            df=pd.DataFrame(st.session_state.dati)
            mask=df.astype(str).apply(lambda x: x.str.contains(cerca, case=False, na=False)).any(axis=1)
            risultati=df[mask]
            st.dataframe(risultati, use_container_width=True)
            for idx,row in risultati.iterrows():
                if st.button(f"Elimina {row['Nome e Cognome']}", key=f"del_{idx}"):
                    st.session_state.dati=[r for r in st.session_state.dati if r["Nome e Cognome"]!=row["Nome e Cognome"]]
                    st.rerun()
    with tab4:
        if st.session_state.dati:
            df=pd.DataFrame(st.session_state.dati)
            c1,c2,c3=st.columns(3)
            c1.metric("Totale", len(df))
            if "Ruolo" in df.columns:
                c2.metric("Ruoli diversi", df["Ruolo"].nunique())
                c3.metric("Attivi", len(df[df["Stato Servizio"]=="Attivo"]) if "Stato Servizio" in df.columns else len(df))
                st.bar_chart(df["Ruolo"].value_counts())
    torna_dashboard()

else:
    st.markdown(LOGHI, unsafe_allow_html=True)
    torna_dashboard()
    st.info(f"Sezione {scelta}")
    torna_dashboard()