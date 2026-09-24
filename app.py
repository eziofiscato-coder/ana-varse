# MAPPE_FIX.py - ANA Varese - Patch 30 righe
# Incolla su app_66.py riga 800-950 (sezione mappe fusione)

# --- FIX 1: Vedi su Mappa ---
if st.button("📍 Vedi su Mappa", key=f"vedi_{idx}", use_container_width=True):
    st.session_state.map_center = {"lat": lat, "lon": lon, "comune": comune, "via": via}
    st.session_state.map_zoom = 16
    st.success(f"Centro mappa su {comune} - {via}")
    st.rerun()

# --- FIX 2: Fullscreen 100% ---
st.markdown("""
<style>
[data-testid="stMap"]{height:100vh!important}
iframe[title="streamlit_folium.st_folium"]{height:100vh!important;width:100%!important}
</style>""", unsafe_allow_html=True)

m = folium.Map(location=[lat, lon], zoom_start=st.session_state.get("map_zoom",13))
folium.Marker([lat, lon], popup=f"{comune} - {via}", tooltip="Intervento").add_to(m)
st_folium(m, height=800, width=1400, returned_objects=[])

# Seconda mappa storico
st_folium(m2, height=800, width=1400)
