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
except:
    HAS_MAP=False

try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PIL=True
except:
    HAS_PIL=False

st.set_page_config(page_title="ANA Varese", layout="wide")

st.markdown('''
<style>
.stForm{background:#e8f5e9;padding:15px;border-radius:10px;border:2px solid #0e7a3d;}
.ana-box{background:#e8f5e9;padding:15px;border-radius:10px;border:2px solid #0e7a3d;margin-bottom:10px;}
.ana-head{background:#0e7a3d;padding:10px;border-radius:8px;color:white;text-align:center;font-family:"Times New Roman", Times, serif;font-weight:bold;}
h2,h3,h4{color:#0e7a3d;font-family:"Times New Roman", Times, serif;font-weight:bold;}
</style>
''', unsafe_allow_html=True)

def load_json(fn, df):
    try:
        if os.path.exists(fn):
            f=open(fn,'r',encoding='utf-8')
            d=json.load(f)
            f.close()
            return d
    except: pass
    return df

def save_json(fn, d):
    try:
        f=open(fn,'w',encoding='utf-8')
        json.dump(d,f,indent=2)
        f.close()
    except: pass

def hpwd(p):
    return hashlib.sha256(p.encode()).hexdigest()

FD='dati.json'
FU='utenti.json'
FP='post.json'
FI='icone.json'
FE='emerg.json'
FC='check.json'
FR='radio.json'
FR2='cons.json'
FEV='eventi.json'
FCHAT='chat.json'

init=[('dati',[]),('post',[]),('icone',[]),('emerg',[]),('check',[]),('radio',[]),('cons',[]),('eventi',[]),('interv',[]),('chat',[]),('menu','Dashboard'),('auth',False),('popup',False),('edit_idx',-1),('edit_map',-1),('sel_lat','45.8205'),('sel_lon','8.8250'),('sel_comune','Varese'),('sel_via',''),('sel_icon','Default'),('chat_user','')]
for k,v in init:
    if k not in st.session_state:
        st.session_state[k]=v

st.session_state.dati=load_json(FD,[])
st.session_state.post=load_json(FP,[])
st.session_state.icone=load_json(FI,[])
st.session_state.emerg=load_json(FE,[])
st.session_state.check=load_json(FC,[])
st.session_state.radio=load_json(FR,[])
st.session_state.cons=load_json(FR2,[])
st.session_state.eventi=load_json(FEV,[])
st.session_state.interv=load_json(FE,[])
st.session_state.chat=load_json(FCHAT,[])

uts=load_json(FU,[])
if not uts:
    uts=[{'username':'admin','password':hpwd('ana2024')}]
    save_json(FU,uts)

def hdr():
    a,b=st.columns([1,5])
    with a:
        try:
            if os.path.exists("copertina.png"):
                st.image("copertina.png",width=200)
            elif os.path.exists("logo.png"):
                st.image("logo.png",width=100)
        except: st.write("ANA")
    with b:
        st.markdown("<div class='ana-head' style='font-family:\"Times New Roman\", Times, serif;font-weight:bold;font-size:28px;'><b>NUCLEO DI VOLONTARI DI PROTEZIONE CIVILE ANA SEZIONE DI VARESE</b></div>", unsafe_allow_html=True)

def to_dash():
    if st.button('TORNA DASHBOARD'):
        st.session_state.menu='Dashboard'
        st.rerun()

# --- PRIMA MASCHERA SENZA FORM VOLONTARIO - SOLO COPERTINA + ENTRA ---
if not st.session_state.popup:
    hdr()
    st.markdown("<div class='ana-head' style='font-family:\"Times New Roman\", Times, serif;font-weight:bold;font-size:50px;padding:20px;'><b>ANA VARESE - PROTEZIONE CIVILE</b></div>", unsafe_allow_html=True)
    st.markdown("<div class='ana-box'>", unsafe_allow_html=True)
    try:
        if os.path.exists("copertina.png"):
            st.image("copertina.png",width=600)
        elif os.path.exists("logo.png"):
            st.image("logo.png",width=350)
    except:
        st.write("Carica copertina.png")
    st.markdown("</div>", unsafe_allow_html=True)
    c1,c2,c3=st.columns([1,1,1])
    with c2:
        if st.button("ENTRA", use_container_width=True):
            st.session_state.popup=True
            st.rerun()
    st.stop()

if not st.session_state.auth:
    hdr()
    c1,c2,c3=st.columns([1,2,1])
    with c2:
        with st.form('login'):
            u=st.text_input('User',value='admin')
            p=st.text_input('Pwd',type='password',value='ana2024')
            ok=st.form_submit_button('ACCEDI')
            if ok:
                ph=hpwd(p)
                for ut in uts:
                    if ut['username']==u and ut['password']==ph:
                        st.session_state.auth=True
                        st.session_state.menu='Dashboard'
                        st.session_state.popup=True
                        st.session_state.chat_user=u
                        st.rerun()
                st.error('Err')
    st.stop()

hdr()
with st.sidebar:
    st.markdown("<div class='ana-head'><b>MENU</b></div>", unsafe_allow_html=True)
    opts=['Dashboard','Volontari','Mappa','Libreria Icone','Interventi Emergenza','Eventi','Check In','DB Radio','Consegna Radio','Chat Volontari','Backup','Tesserino','Logout']
    sel=st.radio('Menu',opts,index=0)
    if sel=='Logout':
        st.session_state.auth=False
        st.session_state.popup=False
        st.rerun()
    st.session_state.menu=sel

sc=st.session_state.menu

if sc=='Dashboard':
    st.markdown("<div class='ana-box'><h2>Dashboard ANA</h2></div>", unsafe_allow_html=True)
    c1,c2,c3,c4=st.columns(4)
    with c1:
        if st.button('VOLONTARI'): st.session_state.menu='Volontari'; st.rerun()
        if st.button('MAPPA'): st.session_state.menu='Mappa'; st.rerun()
    with c2:
        if st.button('ICONE'): st.session_state.menu='Libreria Icone'; st.rerun()
        if st.button('CHAT'): st.session_state.menu='Chat Volontari'; st.rerun()
    with c3:
        if st.button('INTERVENTI'): st.session_state.menu='Interventi Emergenza'; st.rerun()
        if st.button('EVENTI'): st.session_state.menu='Eventi'; st.rerun()
    with c4:
        if st.button('BACKUP'): st.session_state.menu='Backup'; st.rerun()

elif sc=='Interventi Emergenza':
    to_dash()
    st.markdown("<div class='ana-head'><b>INTERVENTI - DATA GG/MM/AAAA</b></div>", unsafe_allow_html=True)
    d_int=st.date_input("Data", value=datetime.now().date(), format="DD/MM/YYYY", key="d_int")
    o_int=st.time_input("Ora",key="o_int")
    com_int=st.text_input("Comune *",key="com_int")
    via_int=st.text_input("Via *",key="via_int")
    az_int=st.text_area("Azione *",key="az_int")
    if st.button("SALVA INTERVENTO",key="sv_int"):
        if com_int and via_int and az_int:
            nuovo={"Data":d_int.strftime("%d/%m/%Y"),"Ora":str(o_int),"Comune":com_int,"Via":via_int,"Azione":az_int}
            st.session_state.interv.append(nuovo)
            save_json(FE,st.session_state.interv)
            st.success("OK "+d_int.strftime("%d/%m/%Y"))
            st.rerun()
    if st.session_state.interv:
        st.dataframe(pd.DataFrame(st.session_state.interv))

elif sc=='Eventi':
    to_dash()
    ev_nome=st.text_input("Nome *",key="ev_nome")
    ev_data=st.date_input("Data", value=datetime.now().date(), format="DD/MM/YYYY", key="ev_data")
    ev_com=st.text_input("Comune",key="ev_com")
    if st.button("SALVA EVENTO",key="ev_be"):
        if ev_nome:
            nuovo={'Nome':ev_nome,'Data':ev_data.strftime("%d/%m/%Y"),'Comune':ev_com}
            st.session_state.eventi.append(nuovo)
            save_json(FEV,st.session_state.eventi)
            st.success("OK "+ev_data.strftime("%d/%m/%Y"))
            st.rerun()
    if st.session_state.eventi:
        st.dataframe(pd.DataFrame(st.session_state.eventi))