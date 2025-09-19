import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

st.title("Waste Tracker Dashboard")

# example dataset
data = {
    "Day": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    "Wet Waste (kg)": [5, 7, 6, 8, 10, 12, 9],
    "Dry Waste (kg)": [3, 4, 2, 5, 6, 4, 3]
}
df = pd.DataFrame(data)

# Calculate stats
total_wet = df["Wet Waste (kg)"].sum()
total_dry = df["Dry Waste (kg)"].sum()
waste_ratio = round(total_wet / total_dry, 2) if total_dry > 0 else "N/A"

df["Total Waste (kg)"] = df["Wet Waste (kg)"] + df["Dry Waste (kg)"]
max_day = df.loc[df["Total Waste (kg)"].idxmax(), "Day"]

# Layout 
left, right = st.columns([2, 1])

with left:
    g1, g2 = st.columns(2)

    with g1:
        st.subheader("Wet Waste")
        fig_wet = px.line(df, x="Day", y="Wet Waste (kg)", markers=True)
        st.plotly_chart(fig_wet, use_container_width=True, height=300)

    with g2:
        st.subheader("Dry Waste")
        fig_dry = px.line(df, x="Day", y="Dry Waste (kg)", markers=True)
        st.plotly_chart(fig_dry, use_container_width=True, height=300)

    # --- File/Camera uploader ---
    uploaded_file = st.file_uploader(
        "Scan Waste",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=False,
    )

    st.markdown("""
        <style>
        /* Style uploader box */
        [data-testid="stFileUploader"] {
            border: 2px solid black;
            padding: 25px;
            border-radius: 12px;
            background-color: white;
            text-align: center;
        }
        /* Center the label + make it black */
        [data-testid="stFileUploader"] label {
            color: black !important;
            font-size: 18px;
            font-weight: bold;
        }
        /* Center the choose file button */
        [data-testid="stFileUploader"] section {
            display: flex;
            justify-content: center;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
        <style>
        [data-testid="stFileUploader"] {
            border: 2px solid black;
            padding: 25px;
            border-radius: 12px;
            background-color: white;
            text-align: center;
        }
        [data-testid="stFileUploader"] section {
            display: flex;
            justify-content: center;
        }
        </style>
    """, unsafe_allow_html=True)

    if uploaded_file is not None:
        st.success(f"✅ File received: {uploaded_file.name}")

with right:
    st.subheader("Waste Statistics")
    st.metric(label="Wet/Dry Ratio", value=waste_ratio)
    st.metric(label="Total Wet Waste (kg)", value=total_wet)
    st.metric(label="Total Dry Waste (kg)", value=total_dry)
    st.metric(label="Day with Most Waste", value=max_day)

# --- Points counter ---
st.markdown("""
    <style>
    .points-counter {
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
    }
    </style>
    <div class="points-counter">
        ⭐ Points: 495
    </div>
""", unsafe_allow_html=True)
