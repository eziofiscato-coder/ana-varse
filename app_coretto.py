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

try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PIL=True
except: HAS_PIL=False

st.set_page_config(page_title="ANA Varese", layout="wide")

st.markdown('''
<style>
.stForm{background:#e8f5e9;padding:15px;border-radius:10px;border:2px solid #0e7a3d;}
.ana-box{background:#e8f5e9;padding:15px;border-radius:10px;border:2px solid #0e7a3d;margin-bottom:10px;}
.ana-head{background:#0e7a3d;padding:15px;border-radius:8px;color:white;text-align:center;font-family:"Times New Roman", Times, serif;font-weight:bold;font-size:26px;}
h2,h3{color:#0e7a3d;font-family:"Times New Roman", Times, serif;font-weight:bold;}
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

# ============ PRIMA PAGINA - SENZA LOGO PC ANA, SOLO COPERTINA ============
if not st.session_state.popup:
    # QUI HO TOLTO hdr() - niente logo PC ANA in prima pagina
    st.markdown("<div class='ana-head' style='font-size:50px;padding:25px;'><b>ANA VARESE - PROTEZIONE CIVILE</b></div>", unsafe_allow_html=True)
    st.markdown("<div class='ana-box' style='text-align:center;'>", unsafe_allow_html=True)
    try:
        if os.path.exists("copertina.png"):
            st.image("copertina.png", width=700)
        elif os.path.exists("logo.png"):
            st.image("logo.png", width=350)
        else:
            st.warning("Carica copertina.png su GitHub!")
    except:
        st.warning("Carica copertina.png su GitHub!")
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
                st.error('Errore login')
    st.stop()

hdr()
with st.sidebar:
    opts=['Dashboard','Volontari','Mappa','Libreria Icone','Interventi Emergenza','Eventi','Check In','DB Radio','Consegna Radio','Chat Volontari','Backup','Tesserino','Logout']
    sel=st.radio('MENU',opts,index=0)
    if sel=='Logout': st.session_state.auth=False; st.session_state.popup=False; st.rerun()
    st.session_state.menu=sel

sc=st.session_state.menu

if sc=='Dashboard':
    st.markdown("<div class='ana-box'><h2>Dashboard ANA - Tutte le maschere ripristinate</h2></div>", unsafe_allow_html=True)
    c1,c2,c3,c4=st.columns(4)
    with c1:
        if st.button('VOLONTARI', use_container_width=True): st.session_state.menu='Volontari'; st.rerun()
        if st.button('MAPPA', use_container_width=True): st.session_state.menu='Mappa'; st.rerun()
        if st.button('ICONE', use_container_width=True): st.session_state.menu='Libreria Icone'; st.rerun()
    with c2:
        if st.button('INTERVENTI', use_container_width=True): st.session_state.menu='Interventi Emergenza'; st.rerun()
        if st.button('EVENTI', use_container_width=True): st.session_state.menu='Eventi'; st.rerun()
        if st.button('CHECK IN', use_container_width=True): st.session_state.menu='Check In'; st.rerun()
    with c3:
        if st.button('RADIO DB', use_container_width=True): st.session_state.menu='DB Radio'; st.rerun()
        if st.button('CONSEGNA RADIO', use_container_width=True): st.session_state.menu='Consegna Radio'; st.rerun()
        if st.button('CHAT', use_container_width=True): st.session_state.menu='Chat Volontari'; st.rerun()
    with c4:
        if st.button('BACKUP', use_container_width=True): st.session_state.menu='Backup'; st.rerun()
        if st.button('TESSERINO', use_container_width=True): st.session_state.menu='Tesserino'; st.rerun()
    c1,c2,c3,c4=st.columns(4)
    c1.metric('Volontari', len(st.session_state.dati)); c2.metric('Post', len(st.session_state.post)); c3.metric('Icone', len(st.session_state.icone)); c4.metric('Chat', len(st.session_state.chat))

elif sc=='Volontari':
    to_dash(); st.markdown("<div class='ana-head'><b>VOLONTARI</b></div>", unsafe_allow_html=True)
    with st.form("form_vol"):
        nome=st.text_input("Nome e Cognome *"); assoc=st.text_input("Associazione *"); cell=st.text_input("Cellulare *")
        ruolo=st.selectbox("Ruolo *", ["Volontario","Caposquadra","Coordinatore","Autista","Radio","Telecomunicazioni","Logistica","Segreteria","Sanitario","Altro"])
        data=st.date_input("Data iscrizione", value=datetime.now().date(), format="DD/MM/YYYY")
        submitted=st.form_submit_button("✅ Salva", use_container_width=True)
        if submitted:
            if nome and assoc and cell:
                st.session_state.dati.append({"Nome":nome,"Associazione":assoc,"Cellulare":cell,"Ruolo":ruolo,"Data":data.strftime("%d/%m/%Y")})
                save_json(FD,st.session_state.dati); st.success(f"Aggiunto {nome} - {data.strftime('%d/%m/%Y')}"); st.rerun()
            else: st.error("Compila i campi *")
    if st.session_state.dati: st.dataframe(pd.DataFrame(st.session_state.dati), use_container_width=True)

elif sc=='Mappa':
    to_dash(); st.markdown("<div class='ana-head'><b>MAPPA</b></div>", unsafe_allow_html=True)
    if not HAS_MAP:
        st.warning("Installa folium: pip install folium streamlit-folium")
    else:
        lat=st.text_input("Lat", value=st.session_state.sel_lat); lon=st.text_input("Lon", value=st.session_state.sel_lon)
        comune=st.text_input("Comune", value=st.session_state.sel_comune); via=st.text_input("Via", value=st.session_state.sel_via)
        m=folium.Map(location=[float(lat),float(lon)], zoom_start=13); Fullscreen().add_to(m)
        folium.Marker([float(lat),float(lon)], popup=f"{comune} - {via}").add_to(m)
        st_folium(m, width=1200, height=600)
        if st.session_state.post: st.dataframe(pd.DataFrame(st.session_state.post))

elif sc=='Libreria Icone':
    to_dash(); st.markdown("<div class='ana-head'><b>LIBRERIA ICONE</b></div>", unsafe_allow_html=True)
    nome_icona=st.text_input("Nome icona"); url_icona=st.text_input("URL icona")
    if st.button("SALVA ICONA"):
        if nome_icona:
            st.session_state.icone.append({"Nome":nome_icona,"URL":url_icona}); save_json(FI,st.session_state.icone); st.rerun()
    if st.session_state.icone: st.dataframe(pd.DataFrame(st.session_state.icone))

elif sc=='Interventi Emergenza':
    to_dash(); st.markdown("<div class='ana-head'><b>INTERVENTI - DATA GG/MM/AAAA</b></div>", unsafe_allow_html=True)
    d_int=st.date_input("Data", value=datetime.now().date(), format="DD/MM/YYYY", key="d_int")
    o_int=st.time_input("Ora",key="o_int"); com_int=st.text_input("Comune *",key="com_int"); via_int=st.text_input("Via *",key="via_int"); az_int=st.text_area("Azione *",key="az_int")
    if st.button("SALVA INTERVENTO",key="sv_int"):
        if com_int and via_int and az_int:
            nuovo={"Data":d_int.strftime("%d/%m/%Y"),"Ora":str(o_int),"Comune":com_int,"Via":via_int,"Azione":az_int}
            st.session_state.interv.append(nuovo); save_json(FE,st.session_state.interv); st.success("OK "+d_int.strftime("%d/%m/%Y")); st.rerun()
    if st.session_state.interv: st.dataframe(pd.DataFrame(st.session_state.interv))

elif sc=='Eventi':
    to_dash(); st.markdown("<div class='ana-head'><b>EVENTI - DATA GG/MM/AAAA</b></div>", unsafe_allow_html=True)
    ev_nome=st.text_input("Nome *",key="ev_nome"); ev_data=st.date_input("Data", value=datetime.now().date(), format="DD/MM/YYYY", key="ev_data"); ev_com=st.text_input("Comune",key="ev_com")
    if st.button("SALVA EVENTO",key="ev_be"):
        if ev_nome:
            nuovo={'Nome':ev_nome,'Data':ev_data.strftime("%d/%m/%Y"),'Comune':ev_com}
            st.session_state.eventi.append(nuovo); save_json(FEV,st.session_state.eventi); st.success("OK "+ev_data.strftime("%d/%m/%Y")); st.rerun()
    if st.session_state.eventi: st.dataframe(pd.DataFrame(st.session_state.eventi))

elif sc=='Check In':
    to_dash(); st.markdown("<div class='ana-head'><b>CHECK IN - DATA GG/MM/AAAA</b></div>", unsafe_allow_html=True)
    vlist=[d.get('Nome','') for d in st.session_state.dati]
    if vlist:
        sel=st.selectbox("Volontario",vlist,key="check_vol"); d_check=st.date_input("Data", value=datetime.now().date(), format="DD/MM/YYYY", key="d_check")
        o_check=st.time_input("Ora",key="o_check"); luogo=st.text_input("Luogo",key="luogo_check")
        if st.button("SALVA CHECK IN",key="bc_check"):
            nuovo={'Volontario':sel,'Data':d_check.strftime("%d/%m/%Y"),'Ora':str(o_check),'Luogo':luogo}
            st.session_state.check.append(nuovo); save_json(FC,st.session_state.check); st.success("OK "+d_check.strftime("%d/%m/%Y")); st.rerun()
    if st.session_state.check: st.dataframe(pd.DataFrame(st.session_state.check))

elif sc=='DB Radio':
    to_dash(); st.markdown("<div class='ana-head'><b>DB RADIO</b></div>", unsafe_allow_html=True)
    matr=st.text_input("Matricola"); tipo=st.text_input("Tipo")
    if st.button("SALVA RADIO"):
        if matr: st.session_state.radio.append({"Matricola":matr,"Tipo":tipo}); save_json(FR,st.session_state.radio); st.rerun()
    if st.session_state.radio: st.dataframe(pd.DataFrame(st.session_state.radio))

elif sc=='Consegna Radio':
    to_dash(); st.markdown("<div class='ana-head'><b>CONSEGNA RADIO - DATA GG/MM/AAAA</b></div>", unsafe_allow_html=True)
    vlist=[d.get('Nome','') for d in st.session_state.dati]; rlist=[r.get('Matricola','')+" - "+r.get('Tipo','') for r in st.session_state.radio]
    if vlist and rlist:
        s_vol=st.selectbox("Volontario",vlist,key="s_vol"); s_rad=st.selectbox("Radio",rlist,key="s_rad")
        d_cons=st.date_input("Data", value=datetime.now().date(), format="DD/MM/YYYY", key="d_cons")
        if st.button("SALVA CONSEGNA",key="b_cons"):
            nuovo={'Volontario':s_vol,'Radio':s_rad,'Data':d_cons.strftime("%d/%m/%Y")}
            st.session_state.cons.append(nuovo); save_json(FR2,st.session_state.cons); st.success("OK "+d_cons.strftime("%d/%m/%Y")); st.rerun()
    if st.session_state.cons: st.dataframe(pd.DataFrame(st.session_state.cons))

elif sc=='Chat Volontari':
    to_dash(); st.markdown("<div class='ana-head'><b>CHAT VOLONTARI</b></div>", unsafe_allow_html=True)
    msg=st.text_input("Messaggio")
    if st.button("INVIA"):
        if msg: st.session_state.chat.append({"User":st.session_state.chat_user,"Messaggio":msg,"Data":datetime.now().strftime("%d/%m/%Y %H:%M")}); save_json(FCHAT,st.session_state.chat); st.rerun()
    if st.session_state.chat:
        for c in st.session_state.chat[-20:]: st.write(f"{c.get('Data','')} - {c.get('User','')}: {c.get('Messaggio','')}")

elif sc=='Backup':
    to_dash(); st.markdown("<div class='ana-head'><b>BACKUP</b></div>", unsafe_allow_html=True)
    df=pd.DataFrame(st.session_state.dati)
    if not df.empty:
        output=BytesIO(); df.to_excel(output, index=False, engine="openpyxl")
        st.download_button("📥 Scarica Excel Volontari", output.getvalue(), file_name="volontari.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    st.json({"dati":len(st.session_state.dati),"post":len(st.session_state.post),"icone":len(st.session_state.icone)})

elif sc=='Tesserino':
    to_dash(); st.markdown("<div class='ana-head'><b>TESSERINO</b></div>", unsafe_allow_html=True)
    st.write("Maschera tesserino con foto")