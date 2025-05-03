import pandas as pd
import altair as alt
import streamlit as st
from pathlib import Path

# Load data
DATA_PATH = Path("data/processed/merged/core_cpi_long.csv")

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH, parse_dates=["date"])
    return df

df = load_data()

# App title and intro
st.title("🌍 Core CPI Dashboard")
st.markdown("Visualise quarterly core CPI across countries (OECD, CPI excluding food and energy).")

# Sidebar: Date filter
min_date = df["date"].min().date()
max_date = df["date"].max().date()

date_range = st.slider(
    "Select date range:",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date),
    format="YYYY-MM"
)

# Filter by date range
df = df[(df["date"] >= pd.to_datetime(date_range[0])) & (df["date"] <= pd.to_datetime(date_range[1]))]

# Country selector
countries = df["country"].unique()
selected_countries = st.multiselect(
    "Select countries to compare:",
    sorted(countries),
    default=["New Zealand", "United Kingdom"]
)

# Filter by country
df_filtered = df[df["country"].isin(selected_countries)]

# Altair chart
chart = alt.Chart(df_filtered).mark_line().encode(
    x="date:T",
    y="cpi:Q",
    color="country:N",
    tooltip=["date:T", "country:N", "cpi:Q"]
).properties(
    width=800,
    height=400,
    title="Quarterly Core CPI by Country"
).interactive()

st.altair_chart(chart, use_container_width=True)

# Footer
st.markdown("---")
st.caption("📊 Data from FRED (OECD CPICORQINMEI series) | Built with Streamlit + Altair")
