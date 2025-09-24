import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image
from ai_logic import predict
import requests
import pydeck as pdk
import os

st.set_page_config(layout="wide")

port = int(os.environ.get("PORT", 10000))

tab1, tab2 = st.tabs(["Dashboard", "Map"])

# Tab 1 - Waste Tracker Dashboard
with tab1:
    st.title("Waste Tracker Dashboard")

    if "points" not in st.session_state:
        st.session_state.points = 0

    # --- Clear any existing data to start fresh ---
    if "df" in st.session_state:
        # Remove any existing data in session state to reset to empty
        del st.session_state.df

    # Initialize an empty DataFrame (no sample data)
    st.session_state.df = pd.DataFrame(columns=["Day", "Wet Waste (kg)", "Dry Waste (kg)"])
    df = st.session_state.df

    # --- Calculate stats only if data exists ---
    if not df.empty:
        df["Total Waste (kg)"] = df["Wet Waste (kg)"] + df["Dry Waste (kg)"]
        total_wet = df["Wet Waste (kg)"].sum()
        total_dry = df["Dry Waste (kg)"].sum()
        waste_ratio = round(total_wet / total_dry, 2) if total_dry > 0 else "N/A"
        max_day = df.loc[df["Total Waste (kg)"].idxmax(), "Day"]
    else:
        total_wet, total_dry, waste_ratio, max_day = 0, 0, "N/A", "N/A"

    # --- Layout: Graphs + Stats ---
    left, right = st.columns([2, 1])

    with left:
        g1, g2 = st.columns(2)

        with g1:
            st.subheader("Wet Waste")
            if not df.empty:
                fig_wet = px.line(df, x="Day", y="Wet Waste (kg)", markers=True)
                st.plotly_chart(fig_wet, config={"responsive": True}, use_container_width=True)
            else:
                st.info("No wet waste data yet. Scan to add entries.")

        with g2:
            st.subheader("Dry Waste")
            if not df.empty:
                fig_dry = px.line(df, x="Day", y="Dry Waste (kg)", markers=True)
                st.plotly_chart(fig_dry, config={"responsive": True}, use_container_width=True)
            else:
                st.info("No dry waste data yet. Scan to add entries.")

    with right:
        st.subheader("Waste Statistics")
        st.metric(label="Wet/Dry Ratio", value=waste_ratio)
        st.metric(label="Total Wet Waste (kg)", value=total_wet)
        st.metric(label="Total Dry Waste (kg)", value=total_dry)
        st.metric(label="Day with Most Waste", value=max_day)

    # --- Scan Section (always below everything) ---
    st.divider()

    st.subheader("Scan Waste")
    uploaded_file = st.file_uploader(
        label="Scan Waste",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=False,
        key="file_uploader"
    )

    if uploaded_file is not None:
        # Prevent duplicate scan entries by checking last processed file
        if "last_uploaded_filename" not in st.session_state or uploaded_file.name != st.session_state["last_uploaded_filename"]:
            image = Image.open(uploaded_file)
            st.image(image, caption="Scanned Image", use_container_width=False)

            label, confidence = predict(image)
            st.success(f"Prediction: {label} ({confidence*100:.2f}% confidence)")

            # --- Use fixed average mass for each waste type
            if label == "Wet":
                estimated_mass = 0.15  # e.g., average wet waste item mass in kg
            elif label == "Dry":
                estimated_mass = 0.05  # e.g., average dry waste item mass in kg
            else:
                estimated_mass = 0.1   # fallback average

            # --- Add to dataframe ---
            new_row = {
                "Day": pd.Timestamp.now().strftime("%a"),
                "Wet Waste (kg)": estimated_mass if label == "Wet" else 0,
                "Dry Waste (kg)": estimated_mass if label == "Dry" else 0,
            }
            st.session_state.df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

            # --- Append to CSV log ---
            import csv
            from datetime import datetime
            log_row = {
                "timestamp": datetime.now().isoformat(),
                "date": datetime.now().date(),
                "day": pd.Timestamp.now().strftime("%a"),
                "label": uploaded_file.name + ": " + label,
                "mass_kg": estimated_mass
            }
            file_exists = False
            try:
                with open("waste_log.csv", "r", newline="") as f:
                    file_exists = True
            except FileNotFoundError:
                pass
            with open("waste_log.csv", "a", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["timestamp", "date", "day", "label", "mass_kg"])
                if not file_exists:
                    writer.writeheader()
                writer.writerow(log_row)

            st.session_state["last_uploaded_filename"] = uploaded_file.name
            st.session_state.points += 10
            st.rerun()
        else:
            st.info("This file has already been processed. Upload a new file to add more data.")

    # --- Points counter (fixed for now) ---
    st.markdown(f"""
        <style>
        .points-counter {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #2E86C1;
            color: white;
            padding: 15px 25px;
            border-radius: 12px;
            font-size: 18px;
            font-weight: bold;
            box-shadow: 0px 4px 6px rgba(0,0,0,0.2);
        }}
        </style>
        <div class="points-counter">
            ⭐ Points: {st.session_state.points}
        </div>
    """, unsafe_allow_html=True)

# Tab 2 - Smart Bin Map
with tab2:
    import time

    API_URL = "https://sih-h85i.onrender.com/bins"
    st.header("Smart Bin Map")

    max_retries = 5
    bins = None
    for i in range(max_retries):
        response = requests.get(API_URL)
        try:
            bins = response.json()
            break  # Success!
        except Exception:
            st.warning("Backend waking up, retrying in 3 seconds...")
            time.sleep(3)
    else:
        st.error("Could not fetch bin data after several tries.")
        st.stop()

    df = pd.DataFrame(bins)

    if df.empty:
        st.info("No bin data available.")
    else:
        def get_color(row):
            if row["status"] == "FULL":
                return [255, 0, 0]
            else:
                return [0, 200, 0]
        df["color"] = df.apply(get_color, axis=1)

        st.pydeck_chart(pdk.Deck(
            map_style="dark",
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
            tooltip={"text": "Bin {bin_id} ({type})\\nStatus: {status}\\nLast: {last_update}"}
        ))
