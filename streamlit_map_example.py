import streamlit as st
import requests
import pandas as pd
import pydeck as pdk

st.title("Smart Bin Map Dashboard")

# Backend API URL
API_URL = "http://localhost:8000/bins"

# Fetch bin data from FastAPI
try:
    bins = requests.get(API_URL).json()
    df = pd.DataFrame(bins)
except Exception as e:
    st.error(f"Could not fetch bin data: {e}")
    st.stop()

if df.empty:
    st.info("No bin data available.")
    st.stop()

# Color bins by status
def get_color(row):
    if row["status"] == "FULL":
        return [255, 0, 0]  # Red
    else:
        return [0, 200, 0]  # Green

df["color"] = df.apply(get_color, axis=1)

# Show map with bins
st.pydeck_chart(pdk.Deck(
    map_style="mapbox://styles/mapbox/streets-v11",
    initial_view_state=pdk.ViewState(
        latitude=df["lat"].mean(),
        longitude=df["lon"].mean(),
        zoom=14,
        pitch=0,
    ),
    layers=[
        pdk.Layer(
            "ScatterplotLayer",
            data=df,
            get_position="[lon, lat]",
            get_color="color",
            get_radius=30,
            pickable=True,
        ),
    ],
    tooltip={"text": "Bin {bin_id} ({type})\nStatus: {status}\nLast: {last_update}"}
))
