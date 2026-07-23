"""
Facebook Page Post Performance Dashboard
-----------------------------------------
An interactive Streamlit dashboard built on the real UCI "Facebook metrics"
dataset (Moro, Rita & Vala, 2016) — 500 posts published on a cosmetics
brand's Facebook Page, with reach, impressions, and engagement metrics for
each post.

Data file: dataset_Facebook.csv (bundled in this repo, semicolon-separated).

Also makes one live call to a real external REST API (Open-Meteo, free and
keyless) so the dashboard demonstrates both static-dataset analytics and
live external data in the same app.

### Run locally with:  streamlit run app.py
"""

import pandas as pd
import requests
import streamlit as st
import matplotlib.pyplot as plt

# --------------------------------------------------------------------------
# Page config
# --------------------------------------------------------------------------
st.set_page_config(
    page_title="Facebook Page Post Performance Dashboard",
    page_icon="📘",
    layout="wide",
)

MONTH_NAMES = {
    1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
    7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec",
}
WEEKDAY_NAMES = {1: "Sun", 2: "Mon", 3: "Tue", 4: "Wed", 5: "Thu", 6: "Fri", 7: "Sat"}


# --------------------------------------------------------------------------
# Data loading (cached; reads the bundled CSV — no dependency on any other
# part of the assignment)
# --------------------------------------------------------------------------
@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv("dataset_Facebook.csv", sep=";")

    # Light cleanup: a handful of rows have missing Paid/like/share values
    df["Paid"] = df["Paid"].fillna(0)
    df["like"] = df["like"].fillna(0)
    df["share"] = df["share"].fillna(0)

    df["Paid Label"] = df["Paid"].map({0: "Organic", 1: "Paid"})
    df["Month Name"] = df["Post Month"].map(MONTH_NAMES)
    df["Weekday Name"] = df["Post Weekday"].map(WEEKDAY_NAMES)

    return df


# --------------------------------------------------------------------------
# External API call: live weather (real, keyless, GET request)
# --------------------------------------------------------------------------
CITY_COORDS = {
    "New York":  (40.7128, -74.0060),
    "London":    (51.5074, -0.1278),
    "Singapore": (1.3521, 103.8198),
    "São Paulo": (-23.5505, -46.6333),
    "Dubai":     (25.2048, 55.2708),
}

WEATHER_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Depositing rime fog",
    51: "Light drizzle", 53: "Drizzle", 55: "Dense drizzle",
    61: "Slight rain", 63: "Rain", 65: "Heavy rain",
    71: "Slight snow", 73: "Snow", 75: "Heavy snow",
    80: "Rain showers", 81: "Rain showers", 82: "Violent rain showers",
    95: "Thunderstorm",
}


@st.cache_data(ttl=600)  # refresh at most every 10 minutes per city
def get_current_weather(lat: float, lon: float) -> dict | None:
    """GET current weather from Open-Meteo (free, no API key required)."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {"latitude": lat, "longitude": lon, "current_weather": "true"}
    try:
        resp = requests.get(url, params=params, timeout=8)
        resp.raise_for_status()
        return resp.json().get("current_weather")
    except requests.RequestException:
        return None


# --------------------------------------------------------------------------
# Load data
# --------------------------------------------------------------------------
df = load_data()

# --------------------------------------------------------------------------
# Sidebar — interactive widgets
# --------------------------------------------------------------------------
st.sidebar.header("Filters")

type_choice = st.sidebar.multiselect(
    "Post Type",
    options=sorted(df["Type"].unique()),
    default=sorted(df["Type"].unique()),
)

paid_choice = st.sidebar.selectbox(
    "Paid vs Organic",
    options=["All Posts", "Organic", "Paid"],
    index=0,
)

month_range = st.sidebar.slider(
    "Post Month range",
    min_value=int(df["Post Month"].min()),
    max_value=int(df["Post Month"].max()),
    value=(int(df["Post Month"].min()), int(df["Post Month"].max())),
)

st.sidebar.divider()
st.sidebar.header("Live Weather Demo")
city_choice = st.sidebar.selectbox("Reference city", options=list(CITY_COORDS.keys()))

# --------------------------------------------------------------------------
# Apply filters
# --------------------------------------------------------------------------
filtered = df.copy()

if type_choice:
    filtered = filtered[filtered["Type"].isin(type_choice)]

if paid_choice != "All Posts":
    filtered = filtered[filtered["Paid Label"] == paid_choice]

filtered = filtered[
    (filtered["Post Month"] >= month_range[0]) & (filtered["Post Month"] <= month_range[1])
]

# --------------------------------------------------------------------------
# Header + live KPIs
# --------------------------------------------------------------------------
st.title("📘 Facebook Page Post Performance Dashboard")
st.caption(
    "Real data: 500 posts from a cosmetics brand's Facebook Page (UCI 'Facebook metrics' "
    "dataset, Moro/Rita/Vala 2016). Filter with the sidebar to update every chart and the "
    "table below."
)

k1, k2, k3, k4 = st.columns(4)
k1.metric("Posts in view", f"{len(filtered):,}")
k2.metric("Avg. Reach", f"{filtered['Lifetime Post Total Reach'].mean():,.0f}" if len(filtered) else "—")
k3.metric("Avg. Total Interactions", f"{filtered['Total Interactions'].mean():,.1f}" if len(filtered) else "—")
k4.metric("Avg. Engaged Users", f"{filtered['Lifetime Engaged Users'].mean():,.0f}" if len(filtered) else "—")

st.divider()

# --------------------------------------------------------------------------
# Live external API card
# --------------------------------------------------------------------------
st.subheader("🌦️ Live Weather (external API demo)")
st.caption(
    "Independent of the Facebook data above — this panel makes a live GET request "
    "to the Open-Meteo API to prove the dashboard can reach a real external service."
)

lat, lon = CITY_COORDS[city_choice]
weather = get_current_weather(lat, lon)

w1, w2, w3 = st.columns(3)
if weather:
    condition = WEATHER_CODES.get(weather.get("weathercode"), "Unknown")
    w1.metric("City", city_choice)
    w2.metric("Temperature", f"{weather['temperature']}°C")
    w3.metric("Wind Speed", f"{weather['windspeed']} km/h")
    st.caption(f"Condition: {condition} · Live data by Open-Meteo.com (CC BY 4.0)")
else:
    st.warning("Could not reach the Open-Meteo API right now — showing dashboard data only.")

st.divider()

# --------------------------------------------------------------------------
# Charts (3 different types, all driven by the current filter state)
# --------------------------------------------------------------------------
st.subheader("📊 Visualizations")

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.markdown("**Avg. Total Interactions by Post Type**")
    by_type = filtered.groupby("Type")["Total Interactions"].mean().sort_values(ascending=False)
    st.bar_chart(by_type)

with chart_col2:
    st.markdown("**Avg. Total Interactions by Post Month**")
    by_month = (
        filtered.groupby("Post Month")["Total Interactions"]
        .mean()
        .reindex(range(month_range[0], month_range[1] + 1))
        .rename(index=MONTH_NAMES)
    )
    st.line_chart(by_month)

st.markdown("**Engagement Mix: Comments vs Likes vs Shares**")
totals = filtered[["comment", "like", "share"]].sum()

if totals.sum() > 0:
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.pie(totals.values, labels=totals.index, autopct="%1.1f%%", startangle=90)
    ax.axis("equal")
    st.pyplot(fig)
else:
    st.info("No data for the current filter selection.")

st.divider()

# --------------------------------------------------------------------------
# Live data table
# --------------------------------------------------------------------------
st.subheader("📋 Filtered Data Table")
st.write(f"Showing {len(filtered):,} of {len(df):,} total posts.")
st.dataframe(filtered.reset_index(drop=True), use_container_width=True)

st.download_button(
    "Download filtered data as CSV",
    data=filtered.to_csv(index=False).encode("utf-8"),
    file_name="filtered_facebook_posts.csv",
    mime="text/csv",
)