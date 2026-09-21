import streamlit as st
import pandas as pd
from io import BytesIO
import os, json, hashlib, base64
from datetime import datetime

try:
    import folium
    from folium.plugins import Fullscreen
    from streamlit_folium import st_folium
    HAS_MAP=True
except: HAS_MAP=False

st.set_page_config(page_title="ANA Varese", layout="wide")

st.markdown('''
<style>
.ana-box{background:#e8f5e9;padding:15px;border-radius:10px;border:2px solid #0e7a3d;margin-bottom:10px;}
.ana-head{background:#0e7a3d;padding:15px;border-radius:8px;color:white;text-align:center;font-family:"Times New Roman", Times, serif;font-weight:bold;font-size:26px;}
h2{color:#0e7a3d;font-family:"Times New Roman", Times, serif;font-weight:bold;}
</style>
''', unsafe_allow_html=True)

def load_json(fn, df):
    try:
        if os.path.exists(fn): return json.load(open(fn,'r',encoding='utf-8'))
    except: pass
    return df
def save_json(fn, d):
    try: json.dump(d, open(fn,'w',encoding='utf-8'), indent=2)
    except: pass
def hpwd(p): return hashlib.sha256(p.encode()).hexdigest()

FD='dati.json'; FU='utenti.json'; FP='post.json'; FI='icone.json'; FE='emerg.json'; FC='check.json'; FR='radio.json'; FR2='cons.json'; FEV='eventi.json'; FCHAT='chat.json'

for k,v in [('dati',[]),('post',[]),('icone',[]),('emerg',[]),('check',[]),('radio',[]),('cons',[]),('eventi',[]),('interv',[]),('chat',[]),('menu','Dashboard'),('auth',False),('popup',False),('edit_idx',-1),('edit_map',-1),('sel_lat','45.8205'),('sel_lon','8.8250'),('sel_comune','Varese'),('sel_via',''),('sel_icon','Default'),('chat_user','')]:
    if k not in st.session_state: st.session_state[k]=v

st.session_state.dati=load_json(FD,[]); st.session_state.post=load_json(FP,[]); st.session_state.icone=load_json(FI,[]); st.session_state.emerg=load_json(FE,[]); st.session_state.check=load_json(FC,[]); st.session_state.radio=load_json(FR,[]); st.session_state.cons=load_json(FR2,[]); st.session_state.eventi=load_json(FEV,[]); st.session_state.interv=load_json(FE,[]); st.session_state.chat=load_json(FCHAT,[])
uts=load_json(FU,[])
if not uts:
    uts=[{'username':'admin','password':hpwd('ana2024')}]; save_json(FU,uts)

def hdr():
    a,b=st.columns([1,5])
    with a:
        try:
            if os.path.exists("logo.png"): st.image("logo.png",width=120)
        except: pass
    with b:
        st.markdown("<div class='ana-head'><b>NUCLEO DI VOLONTARI DI PROTEZIONE CIVILE ANA SEZIONE DI VARESE</b></div>", unsafe_allow_html=True)

def to_dash():
    if st.button('TORNA DASHBOARD'): st.session_state.menu='Dashboard'; st.rerun()

# PRIMA PAGINA SENZA LOGO PC ANA - SOLO COPERTINA
if not st.session_state.popup:
    st.markdown("<div class='ana-head' style='font-size:50px;padding:25px;'><b>ANA VARESE - PROTEZIONE CIVILE</b></div>", unsafe_allow_html=True)
    st.markdown("<div class='ana-box' style='text-align:center;'>", unsafe_allow_html=True)
    try:
        if os.path.exists("copertina.png"): st.image("copertina.png", width=700)
        else: st.warning("Carica copertina.png su GitHub!")
    except: st.warning("Carica copertina.png")
    st.markdown("</div>", unsafe_allow_html=True)
    c1,c2,c3=st.columns([1,1,1])
    with c2:
        if st.button("ENTRA", use_container_width=True):
            st.session_state.popup=True; st.rerun()
    st.stop()

if not st.session_state.auth:
    hdr()
    c1,c2,c3=st.columns([1,2,1])
    with c2:
        with st.form('login'):
            u=st.text_input('User',value='admin'); p=st.text_input('Pwd',type='password',value='ana2024')
            ok=st.form_submit_button('ACCEDI')
            if ok:
                ph=hpwd(p)
                for ut in uts:
                    if ut['username']==u and ut['password']==ph:
                        st.session_state.auth=True; st.session_state.menu='Dashboard'; st.session_state.popup=True; st.session_state.chat_user=u; st.rerun()
                st.error('Errore')
    st.stop()

hdr()
with st.sidebar:
    opts=['Dashboard','Volontari','Mappa','Libreria Icone','Interventi Emergenza','Eventi','Check In','DB Radio','Consegna Radio','Chat Volontari','Backup','Tesserino','Logout']
    sel=st.radio('MENU',opts,index=0)
    if sel=='Logout': st.session_state.auth=False; st.session_state.popup=False; st.rerun()
    st.session_state.menu=sel

sc=st.session_state.menu

if sc=='Dashboard':
    st.markdown("<div class='ana-box'><h2>Dashboard - Lavoro di stamattina ripristinato</h2></div>", unsafe_allow_html=True)
    c1,c2,c3,c4=st.columns(4)
    with c1:
        if st.button('VOLONTARI', use_container_width=True): st.session_state.menu='Volontari'; st.rerun()
        if st.button('MAPPA', use_container_width=True): st.session_state.menu='Mappa'; st.rerun()
    with c2:
        if st.button('ICONE', use_container_width=True): st.session_state.menu='Libreria Icone'; st.rerun()
        if st.button('INTERVENTI', use_container_width=True): st.session_state.menu='Interventi Emergenza'; st.rerun()
    with c3:
        if st.button('EVENTI', use_container_width=True): st.session_state.menu='Eventi'; st.rerun()
        if st.button('CHECK IN', use_container_width=True): st.session_state.menu='Check In'; st.rerun()
    with c4:
        if st.button('BACKUP', use_container_width=True): st.session_state.menu='Backup'; st.rerun()

# ========== FORM VOLONTARIO COMPLETO CON MASCHERA E SOTTOMASCHERE ==========
elif sc=='Volontari':
    to_dash()
    st.markdown("<div class='ana-head'><b>VOLONTARI - MASCHERA COMPLETA CON SOTTOMASCHERE</b></div>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["➕ Nuovo Volontario", "📋 Lista Volontari", "🔍 Sottomaschere"])

    with tab1:
        st.markdown("<div class='ana-box'>", unsafe_allow_html=True)
        with st.form("form_vol_completo"):
            c1,c2=st.columns(2)
            with c1:
                nome=st.text_input("Nome e Cognome *")
                assoc=st.text_input("Associazione *")
                cell=st.text_input("Cellulare *")
                ruolo=st.selectbox("Ruolo *", ["Volontario","Caposquadra","Coordinatore","Autista","Radio","Telecomunicazioni","Logistica","Segreteria","Sanitario","Altro"])
            with c2:
                odv=st.text_input("ODV / Sezione")
                gruppo=st.text_input("Gruppo")
                data_nasc=st.date_input("Data Nascita", value=datetime(1980,1,1), format="DD/MM/YYYY")
                data_iscr=st.date_input("Data Iscrizione", value=datetime.now().date(), format="DD/MM/YYYY")
            note=st.text_area("Note")
            foto=st.file_uploader("Foto volontario", type=["png","jpg","jpeg"])
            submitted=st.form_submit_button("✅ Salva Volontario", use_container_width=True)
            if submitted:
                if nome and assoc and cell:
                    foto_path=""
                    if foto:
                        os.makedirs("foto_vol", exist_ok=True)
                        foto_path=os.path.join("foto_vol", f"{nome.replace(' ','_')}.png")
                        with open(foto_path,"wb") as f: f.write(foto.getbuffer())
                    nuovo={"Nome":nome,"Associazione":assoc,"Cellulare":cell,"Ruolo":ruolo,"ODV":odv,"Gruppo":gruppo,"DataNasc":data_nasc.strftime("%d/%m/%Y"),"DataIscr":data_iscr.strftime("%d/%m/%Y"),"Note":note,"Foto":foto_path}
                    st.session_state.dati.append(nuovo); save_json(FD,st.session_state.dati)
                    st.success(f"Aggiunto {nome} - {data_iscr.strftime('%d/%m/%Y')}"); st.rerun()
                else: st.error("Compila i campi *")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab2:
        if st.session_state.dati:
            df=pd.DataFrame(st.session_state.dati)
            st.dataframe(df, use_container_width=True)
            # Edit/Delete
            sel_idx=st.selectbox("Seleziona volontario da modificare/eliminare", range(len(st.session_state.dati)), format_func=lambda x: st.session_state.dati[x].get('Nome',''))
            if st.button("ELIMINA VOLONTARIO"):
                st.session_state.dati.pop(sel_idx); save_json(FD,st.session_state.dati); st.rerun()
        else: st.info("Nessun volontario")

    with tab3:
        st.markdown("**Sottomaschere:**")
        c1,c2,c3=st.columns(3)
        with c1:
            st.markdown("**📄 Documenti**"); st.write("Tesserino, assicurazione, formazione")
            if st.session_state.dati:
                v=st.selectbox("Volontario", [d.get('Nome','') for d in st.session_state.dati], key="sub_doc")
                st.write(f"Documenti di {v}")
        with c2:
            st.markdown("**📻 Radio assegnata**")
            if st.session_state.cons:
                st.dataframe(pd.DataFrame(st.session_state.cons))
        with c3:
            st.markdown("**✅ Check In history**")
            if st.session_state.check:
                st.dataframe(pd.DataFrame(st.session_state.check))

elif sc=='Mappa':
    to_dash()
    st.markdown("<div class='ana-head'><b>MAPPA - MARKER SONO LE ICONE CARICATE</b></div>", unsafe_allow_html=True)
    if not HAS_MAP:
        st.error("Aggiungi su requirements.txt: folium, streamlit-folium")
    else:
        col1,col2=st.columns([1,2])
        with col1:
            st.session_state.sel_lat=st.text_input("Lat", value=st.session_state.sel_lat)
            st.session_state.sel_lon=st.text_input("Lon", value=st.session_state.sel_lon)
            st.session_state.sel_comune=st.text_input("Comune", value=st.session_state.sel_comune)
            st.session_state.sel_via=st.text_input("Via", value=st.session_state.sel_via)
            # Scelta icona caricata
            icone_nomi=["Default"] + [i.get('Nome','') for i in st.session_state.icone]
            sel_icon=st.selectbox("Icona caricata (marker sarà questa icona)", icone_nomi)
            nota=st.text_area("Nota intervento")
            d_map=st.date_input("Data", value=datetime.now().date(), format="DD/MM/YYYY")
            if st.button("SALVA POST MAPPA CON ICONA", use_container_width=True):
                nuovo={"Lat":st.session_state.sel_lat,"Lon":st.session_state.sel_lon,"Comune":st.session_state.sel_comune,"Via":st.session_state.sel_via,"Icona":sel_icon,"Nota":nota,"Data":d_map.strftime("%d/%m/%Y")}
                st.session_state.post.append(nuovo); save_json(FP,st.session_state.post); st.success(f"Salvato con icona {sel_icon}"); st.rerun()
            # Mostra icone disponibili
            if st.session_state.icone:
                st.write("Icone caricate:")
                for ic in st.session_state.icone:
                    if os.path.exists(ic.get('URL','')):
                        st.image(ic.get('URL'), width=50, caption=ic.get('Nome'))

        with col2:
            m=folium.Map(location=[float(st.session_state.sel_lat), float(st.session_state.sel_lon)], zoom_start=14)
            Fullscreen().add_to(m)
            # MARKER CON ICONE CARICATE
            for p in st.session_state.post:
                try:
                    icon_name=p.get('Icona','Default')
                    icon_path=""
                    for ic in st.session_state.icone:
                        if ic.get('Nome')==icon_name:
                            icon_path=ic.get('URL','')
                            break
                    if icon_path and os.path.exists(icon_path):
                        # Marker con icona personalizzata caricata
                        icon=folium.CustomIcon(icon_image=icon_path, icon_size=(40,40), icon_anchor=(20,20))
                        folium.Marker([float(p.get('Lat','45.82')), float(p.get('Lon','8.82'))], popup=f"{p.get('Comune','')} - {p.get('Nota','')} - {p.get('Data','')} - Icona:{icon_name}", icon=icon).add_to(m)
                    else:
                        folium.Marker([float(p.get('Lat','45.82')), float(p.get('Lon','8.82'))], popup=f"{p.get('Comune','')} {p.get('Data','')}", icon=folium.Icon(color='green')).add_to(m)
                except Exception