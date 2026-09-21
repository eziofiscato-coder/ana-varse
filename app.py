import streamlit as st
import pandas as pd
from io import BytesIO
import os, json, hashlib
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

# PRIMA PAGINA SENZA LOGO PC ANA
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
    st.markdown("<div class='ana-box'><h2>Dashboard ANA</h2></div>", unsafe_allow_html=True)
    c1,c2,c3=st.columns(4)
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
        if st.button('RADIO', use_container_width=True): st.session_state.menu='DB Radio'; st.rerun()
        if st.button('BACKUP', use_container_width=True): st.session_state.menu='Backup'; st.rerun()

elif sc=='Mappa':
    to_dash()
    st.markdown("<div class='ana-head'><b>MAPPA - CLICCA SULLA MAPPA PER POSIZIONARE</b></div>", unsafe_allow_html=True)
    if not HAS_MAP:
        st.error("Manca folium: aggiungi su requirements.txt -> folium, streamlit-folium")
    else:
        col1,col2=st.columns([1,2])
        with col1:
            st.session_state.sel_lat=st.text_input("Lat", value=st.session_state.sel_lat)
            st.session_state.sel_lon=st.text_input("Lon", value=st.session_state.sel_lon)
            st.session_state.sel_comune=st.text_input("Comune", value=st.session_state.sel_comune)
            st.session_state.sel_via=st.text_input("Via", value=st.session_state.sel_via)
            sel_icon=st.selectbox("Icona", ["Default"] + [i.get('Nome','') for i in st.session_state.icone])
            nota=st.text_area("Nota")
            d_map=st.date_input("Data", value=datetime.now().date(), format="DD/MM/YYYY")
            if st.button("SALVA POST MAPPA", use_container_width=True):
                nuovo={"Lat":st.session_state.sel_lat,"Lon":st.session_state.sel_lon,"Comune":st.session_state.sel_comune,"Via":st.session_state.sel_via,"Icona":sel_icon,"Nota":nota,"Data":d_map.strftime("%d/%m/%Y")}
                st.session_state.post.append(nuovo); save_json(FP,st.session_state.post); st.success("Salvato "+d_map.strftime("%d/%m/%Y")); st.rerun()
        with col2:
            m=folium.Map(location=[float(st.session_state.sel_lat), float(st.session_state.sel_lon)], zoom_start=14)
            Fullscreen().add_to(m)
            # Tutti i post salvati
            for p in st.session_state.post:
                try: folium.Marker([float(p.get('Lat','45.82')), float(p.get('Lon','8.82'))], popup=f"{p.get('Comune','')} {p.get('Via','')} {p.get('Data','')}").add_to(m)
                except: pass
            folium.Marker([float(st.session_state.sel_lat), float(st.session_state.sel_lon)], popup="NUOVO", icon=folium.Icon(color='red')).add_to(m)
            out=st_folium(m, width=800, height=600)
            if out and out.get("last_clicked"):
                st.session_state.sel_lat=str(out["last_clicked"]["lat"])
                st.session_state.sel_lon=str(out["last_clicked"]["lng"])
                st.rerun()
        if st.session_state.post:
            st.divider(); st.dataframe(pd.DataFrame(st.session_state.post), use_container_width=True)
            if st.button("CANCELLA TUTTA MAPPA"): st.session_state.post=[]; save_json(FP,[]); st.rerun()

elif sc=='Libreria Icone':
    to_dash()
    st.markdown("<div class='ana-head'><b>LIBRERIA ICONE - CARICA ICONE</b></div>", unsafe_allow_html=True)
    c1,c2=st.columns(2)
    with c1:
        nome_icona=st.text_input("Nome icona *", key="nome_icona")
        # NUOVA FUNZIONE CARICAMENTO ICONE
        uploaded=st.file_uploader("Carica immagine icona (PNG, JPG)", type=["png","jpg","jpeg"])
        url_icona=st.text_input("Oppure URL icona")
        if st.button("SALVA ICONA", use_container_width=True):
            path_icona=url_icona
            if uploaded:
                # Salva file in cartella
                os.makedirs("icone_upload", exist_ok=True)
                path_icona=os.path.join("icone_upload", uploaded.name)
                with open(path_icona,"wb") as f: f.write(uploaded.getbuffer())
                st.success(f"File salvato: {path_icona}")
            if nome_icona:
                st.session_state.icone.append({"Nome":nome_icona,"URL":path_icona,"File":uploaded.name if uploaded else ""})
                save_json(FI,st.session_state.icone)
                st.success(f"Icona {nome_icona} salvata!"); st.rerun()
            else: st.error("Metti nome icona")
    with c2:
        if st.session_state.icone:
            st.write(f"Icone salvate: {len(st.session_state.icone)}")
            for idx, ic in enumerate(st.session_state.icone):
                c_a,c_b=st.columns([3,1])
                with c_a:
                    st.write(f"{ic.get('Nome')} - {ic.get('URL')}")
                    if os.path.exists(ic.get('URL','')):
                        st.image(ic.get('URL'), width=60)
                with c_b:
                    if st.button("Elimina", key=f"del_ic_{idx}"):
                        st.session_state.icone.pop(idx); save_json(FI,st.session_state.icone); st.rerun()
        else: st.info("Nessuna icona ancora")

elif sc=='Interventi Emergenza':
    to_dash(); st.markdown("<div class='ana-head'><b>INTERVENTI - DATA GG/MM/AAAA</b></div>", unsafe_allow_html=True)
    d_int=st.date_input("Data", value=datetime.now().date(), format="DD/MM/YYYY"); o_int=st.time_input("Ora"); com_int=st.text_input("Comune *"); via_int=st.text_input("Via *"); az_int=st.text_area("Azione *")
    if st.button("SALVA INTERVENTO"):
        if com_int and via_int and az_int:
            nuovo={"Data":d_int.strftime("%d/%m/%Y"),"Ora":str(o_int),"Comune":com_int,"Via":via_int,"Azione":az_int}
            st.session_state.interv.append(nuovo); save_json(FE,st.session_state.interv); st.success("OK "+d_int.strftime("%d/%m/%Y")); st.rerun()
    if st.session_state.interv: st.dataframe(pd.DataFrame(st.session_state.interv))

elif sc=='Eventi':
    to_dash(); st.markdown("<div class='ana-head'><b>EVENTI</b></div>", unsafe_allow_html=True)
    ev_nome=st.text_input("Nome *"); ev_data=st.date_input("Data", value=datetime.now().date(), format="DD/MM/YYYY")
    if st.button("SALVA EVENTO"):
        if ev_nome:
            nuovo={'Nome':ev_nome,'Data':ev_data.strftime("%d/%m/%Y")}; st.session_state.eventi.append(nuovo); save_json(FEV,st.session_state.eventi); st.success("OK "+ev_data.strftime("%d/%m/%Y")); st.rerun()
    if st.session_state.eventi: st.dataframe(pd.DataFrame(st.session_state.eventi))

elif sc=='Check In':
    to_dash(); st.markdown("<div class='ana-head'><b>CHECK IN</b></div>", unsafe_allow_html=True)
    vlist=[d.get('Nome','') for d in st.session_state.dati]
    if vlist:
        sel=st.selectbox("Volontario",vlist); d_check=st.date_input("Data", value=datetime.now().date(), format="DD/MM/YYYY"); luogo=st.text_input("Luogo")
        if st.button("SALVA CHECK IN"):
            nuovo={'Volontario':sel,'Data':d_check.strftime("%d/%m/%Y"),'Luogo':luogo}; st.session_state.check.append(nuovo); save_json(FC,st.session_state.check); st.rerun()
    if st.session_state.check: st.dataframe(pd.DataFrame(st.session_state.check))

elif sc=='Backup':
    to_dash(); df=pd.DataFrame(st.session_state.dati)
    if not df.empty:
        output=BytesIO(); df.to_excel(output, index=False, engine="openpyxl")
        st.download_button("📥 Scarica Excel", output.getvalue(), file_name="volontari.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")