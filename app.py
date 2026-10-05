
import streamlit as st
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(page_title="ANA Test Geoloc", layout="wide")

if "posizioni_pd785" not in st.session_state:
    st.session_state.posizioni_pd785=[]
if "posizioni_anytone" not in st.session_state:
    st.session_state.posizioni_anytone=[]

st.title("TEST Geoloc - Se vedi questo, Streamlit funziona")

# APRS.fi test
callsign = st.text_input("Callsign", "IU2XYZ-9")
api_key = st.text_input("API Key aprs.fi", type="password")

if st.button("Prendi da aprs.fi"):
    if callsign and api_key:
        url = f"https://api.aprs.fi/api/get?name={callsign}&what=loc&apikey={api_key}&format=json"
        try:
            r = requests.get(url, timeout=10)
            st.json(r.json())
        except Exception as e:
            st.error(str(e))
    else:
        st.warning("Metti callsign e key")

# Mappa demo
df = pd.DataFrame([{"lat":45.8167,"lon":8.8333},{"lat":45.82,"lon":8.84}])
st.map(df)
st.success("OK - app leggera carica")
