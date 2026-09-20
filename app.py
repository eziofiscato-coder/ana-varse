import streamlit as st
import pandas as pd
from io import BytesIO
import os
import json
import hashlib
import requests

try:
 import folium
 from streamlit_folium import st_folium
 HAS_FOLIUM = True
except:
 HAS_FOLIUM = False

st.set_page_config(page_title="ANA Varese", layout="wide")

st.markdown("""
<style>
.block-container{padding-top:8px!important; max-width:100%!important;}
.stForm{background:#e8f5e9!important; border:2px solid #2e7d32!important;}
.stButton>button{background:#2e7d32!important; color:white!important;}
</style>
""", unsafe_allow_html=True)

def load_json(fname, default):
 try:
  if os.path.exists(fname):
   with open(fname, 'r', encoding='utf-8') as f:
    return json.load(f)
 except:
  pass
 return default

def save_json(fname, data):
 try:
  with open(fname, 'w', encoding='utf-8') as f:
   json.dump(data, f, indent=2)
 except:
  pass

def hash_pwd(pwd):
 return hashlib.sha256(pwd.encode()).hexdigest()

def get_addr(lat, lon):
 try:
  u = 'https://nominatim.openstreetmap.org/reverse?lat=' + str(lat) + '&lon=' + str(lon) + '&format=jsonv2&accept-language=it'
  r = requests.get(u, headers={'User-Agent': 'ana-varese'}, timeout=6)
  if r.status_code == 200:
   j = r.json()
   a = j.get('address', {})
   com = a.get('city') or a.get('town') or a.get('village') or a.get('municipality') or ''
   via = a.get('road') or a.get('pedestrian') or a.get('footway') or ''
   num = a.get('house_number') or ''
   full_via = via + ' ' + num
   full_via = full_via.strip()
   return com, full_via
 except:
  pass
 return '', ''

FD = 'dati.json'
FU = 'utenti.json'
FP = 'post.json'
FI = 'icone.json'
FT = 'tipologie.json'
FO = 'odv.json'

if 'dati' not in st.session_state:
 st.session_state.dati = []
if 'post' not in st.session_state:
 st.session_state.post = []
if 'icone' not in st.session_state:
 st.session_state.icone = []
if 'tipologie' not in st.session_state:
 st.session_state.tipologie = []
if 'odv_list' not in st.session_state:
 st.session_state.odv_list = []
if 'menu' not in st.session_state:
 st.session_state.menu = 'Dashboard'
if 'auth' not in st.session_state:
 st.session_state.auth = False
if 'lat_tmp' not in st.session_state:
 st.session_state.lat_tmp = 45.8205
if 'lon_tmp' not in st.session_state:
 st.session_state.lon_tmp = 8.8250
if 'com_tmp' not in st.session_state:
 st.session_state.com_tmp = ''
if 'via_tmp' not in st.session_state:
 st.session_state.via_tmp = ''
if 'map_expand' not in st.session_state:
 st.session_state.map_expand = False
if 'map_all_expand' not in st.session_state:
 st.session_state.map_all_expand = False
if 'sel_idx' not in st.session_state:
 st.session_state.sel_idx = -1
if 'zoom_level' not in st.session_state:
 st.session_state.zoom_level = 16

st.session_state.dati = load_json(FD, [])
st.session_state.post = load_json(FP, [])
st.session_state.icone = load_json(FI, [])
st.session_state.utenti = load_json(FU, [])
st.session_state.tipologie = load_json(FT, [])
st.session_state.odv_list = load_json(FO, [])

if not st.session_state.utenti:
 st.session_state.utenti = [{'username': 'admin', 'password': hash_pwd('ana2024')}]
 save_json(FU, st.session_state.utenti)

if not st.session_state.tipologie:
 st.session_state.tipologie = ['Presidio', 'Blocco stradale', 'Punto ritrovo', 'Parcheggio', 'Sanitario', 'Logistica', 'Altro']
 save_json(FT, st.session_state.tipologie)

if not st.session_state.odv_list:
 st.session_state.odv_list = ['ANA Varese', 'Protezione Civile Varese', 'Croce Rossa', 'Alpini', 'AIB', 'Altro']
 save_json(FO, st.session_state.odv_list)

if not st.session_state.icone:
 st.session_state.icone = [{'nome': 'Presidio', 'col': 'blue'}, {'nome': 'Blocco', 'col': 'red'}, {'nome': 'Sanitario', 'col': 'green'}]
 save_json(FI, st.session_state.icone)

def header():
 st.markdown("<div style='text-align:center;background:#a5d6a7;padding:5px;border-radius:8px;border:2px solid #2e7d32;'><b style='color:#0e7a3d;'>VOLONTARIATO Varese</b></div>", unsafe_allow_html=True)

def torna():
 if st.button('TORNA'):
  st.session_state.menu = 'Dashboard'
  st.rerun()

if not st.session_state.auth:
 header()
 c1, c2, c3 = st.columns([1, 2, 1])
 with c2:
  with st.form('login'):
   u = st.text_input('Username', value='admin')
   p = st.text_input('Password', type='password', value='ana2024')
   ok = st.form_submit_button('ACCEDI')
   if ok:
    ph = hash_pwd(p)
    for ut in st.session_state.utenti:
     if ut['username'] == u and ut['password'] == ph:
      st.session_state.auth = True
      st.rerun()
    st.error('Errati')
 st.stop()

if not st.session_state.map_expand and not st.session_state.map_all_expand:
 header()

with st.sidebar:
 if not st.session_state.map_expand and not st.session_state.map_all_expand:
  st.markdown('### MENU')
  opts = ['Dashboard', 'Volontari', 'Mappa', 'Libreria Icone', 'Backup']
  sel = st.radio('Vai a', opts, index=0)
  if sel != st.session_state.menu:
   st.session_state.menu = sel
   st.rerun()
  st.divider()
  if st.button('LOGOUT', use_container_width=True, type='primary'):
   st.session_state.auth = False
   st.rerun()
 else:
  st.markdown('### SCHERMO INTERO')
  if st.button('TORNA AL FORM', use_container_width=True, type='primary'):
   st.session_state.map_expand = False
   st.session_state.map_all_expand = False
   st.rerun()

scelta = st.session_state.menu

if st.session_state.map_expand or st.session_state.map_all_expand:
 st.markdown("<style>header{visibility:hidden!important;} [data-testid=\"stSidebar\"]{display:none!important;}.block-container{padding:0!important; max-width:100%!important;} footer{visibility:hidden!important;}</style>", unsafe_allow_html=True)
 if st.session_state.map_expand:
  st.markdown('## MAPPA INSERIMENTO - SCHERMO INTERO 100%')
  if st.button('TORNA INDIETRO', use_container_width=True, type='primary', key='c1'):
   st.session_state.map_expand = False
   st.session_state.zoom_level = 16
   st.rerun()
  lat_c = st.session_state.lat_tmp
  lon_c = st.session_state.lon_tmp
  zoom = st.session_state.zoom_level
  if st.session_state.sel_idx >= 0 and st.session_state.sel_idx < len(st.session_state.post):
   p_sel = st.session_state.post[st.session_state.sel_idx]
   try:
    lat_c = float(p_sel.get('Lat', '45.8205'))
    lon_c = float(p_sel.get('Lon', '8.8250'))
    zoom = 19
    st.success('INGRANDITA: ' + p_sel.get('Postazione', '') + ' - ODV: ' + p_sel.get('ODV', ''))
   except:
    pass
  if HAS_FOLIUM:
   m = folium.Map(location=[lat_c, lon_c], zoom_start=zoom, tiles='OpenStreetMap')
   for idx, p in enumerate(st.session_state.post):
    try:
     la = float(p.get('Lat', '0'))
     lo = float(p.get('Lon', '0'))
     if idx == st.session_state.sel_idx:
      folium.Marker([la, lo], popup=p.get('Postazione', '') + ' ODV:' + p.get('ODV',''), icon=folium.Icon(color='red', icon='star')).add_to(m)
      folium.Circle([la, lo], radius=80, color='red', fill=True, fill_opacity=0.15).add_to(m)
     else:
      folium.Marker([la, lo], popup=p.get('Postazione', ''), icon=folium.Icon(color='blue')).add_to(m)
    except:
     pass
   folium.Marker([lat_c, lon_c], popup='Nuova', icon=folium.Icon(color='green')).add_to(m)
   st_folium(m, height=850, width=1600, key='m1fs')
 if st.session_state.map_all_expand:
  st.markdown('## MAPPA TUTTE POSTAZIONI - SCHERMO INTERO 100%')
  if st.button('TORNA INDIETRO', use_container_width=True, type='primary', key='c2'):
   st.session_state.map_all_expand = False
   st.rerun()
  if HAS_FOLIUM and st.session_state.post:
   m2 = folium.Map(location=[45.8205, 8.8250], zoom_start=12, tiles='OpenStreetMap')
   for p in st.session_state.post:
    try:
     la = float(p.get('Lat', '0'))
     lo = float(p.get('Lon', '0'))
     folium.Marker([la, lo], popup=p.get('Postazione', '') + ' ODV:' + p.get('ODV',''), icon=folium.Icon(color='blue')).add_to(m2)
    except:
     pass
   st_folium(m2, height=850, width=1600, key='m2fs')
else:
 if scelta == 'Dashboard':
  st.markdown('#### DASHBOARD - MENU COMPLETO DI TUTTI I FORM')
  c1, c2 = st.columns([3, 1])
  with c1:
   st.info('Menu completo - tutti i form')
  with c2:
   if st.button('LOGOUT', use_container_width=True):
    st.session_state.auth = False
    st.rerun()
  c1, c2 = st.columns(2)
  with c1:
   if st.button('VOLONTARI', use_container_width=True):
    st.session_state.menu = 'Volontari'
    st.rerun()
   if st.button('MAPPA', use_container_width=True):
    st.session_state.menu = 'Mappa'
    st.rerun()
  with c2:
   if st.button('LIBRERIA ICONE', use_container_width=True):
    st.session_state.menu = 'Libreria Icone'
    st.rerun()
   if st.button('BACKUP', use_container_width=True):
    st.session_state.menu = 'Backup'
    st.rerun()
  st.divider()
  c1, c2 = st.columns(2)
  c1.metric('Volontari', len(st.session_state.dati))
  c2.metric('Postazioni', len(st.session_state.post))
 elif scelta == 'Volontari':
  torna()
  st.markdown('#### VOLONTARI - PER RESPONSABILE MAPPA')
  with st.form('vol'):
   c1, c2 = st.columns(2)
   with c1:
    a1 = st.text_input('Nome *', placeholder='Mario')
    a2 = st.text_input('Cognome *', placeholder='Rossi')
   with c2:
    a4 = st.text_input('Cellulare *', placeholder='3331234567')
   if st.form_submit_button('SALVA'):
    if a1 and a2 and a4:
     nc = a1 + ' ' + a2
     nuovo = {'Nome': nc, 'Cellulare': a4}
     st.session_state.dati.append(nuovo)
     save_json(FD, st.session_state.dati)
     st.success('Salvato ' + nc)
     st.rerun()
  if st.session_state.dati:
   st.dataframe(pd.DataFrame(st.session_state.dati), use_container_width=True)
 elif scelta == 'Mappa':
  torna()
  st.markdown('#### MAPPA - CON ESPANSIONE SCHERMO INTERO + ODV OPERANTE')
  tipo_map = st.radio('Tipo mappa', ['OpenStreetMap', 'Google Maps'], horizontal=True)
  icon_names = []
  for ic
