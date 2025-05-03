import pandas as pd
import altair as alt
import streamlit as st
from pathlib import Path
from datetime import date

# Load data
DATA_PATH = Path("data/processed/merged/core_cpi_long.csv")

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH, parse_dates=["date"])
    return df

df = load_data()

# App title
st.title("🌍 Core CPI Dashboard")
st.markdown("Visualise quarterly core CPI or Year-on-Year % change across countries (OECD, CPI excluding food and energy).")

# Country selector
countries = df["country"].unique()
selected_countries = st.multiselect("Select countries to compare:", sorted(countries), default=["New Zealand", "United Kingdom"])

# Safe date slider using Python native date
min_date = df["date"].min().date()
max_date = df["date"].max().date()
start_date, end_date = st.slider(
    "Select date range:",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date),
    format="YYYY-MM"
)

# Convert back to pandas datetime
start_ts = pd.to_datetime(start_date)
end_ts = pd.to_datetime(end_date)

# View toggle
metric = st.radio("Select metric to display:", ["CPI", "YoY % change"], horizontal=True)
y_column = "cpi" if metric == "CPI" else "cpi_yoy"
y_title = "Core CPI" if y_column == "cpi" else "YoY % Change"

# Filter data
df_filtered = df[
    (df["country"].isin(selected_countries)) &
    (df["date"] >= start_ts) &
    (df["date"] <= end_ts)
]

# Altair hover tooltip logic
hover = alt.selection_single(
    fields=["date"],
    nearest=True,
    on="mouseover",
    empty="none",
    clear="mouseout"
)

# Tooltip config with dynamic label/format
tooltip = [
    alt.Tooltip("date:T", title="Date"),
    alt.Tooltip("country:N", title="Country"),
    alt.Tooltip(
        y_column,
        title="YoY Change (%)" if y_column == "cpi_yoy" else "Core CPI",
        format=".1f" if y_column == "cpi_yoy" else ".2f"
    )
]

# Base line chart
line = alt.Chart(df_filtered).mark_line().encode(
    x="date:T",
    y=alt.Y(f"{y_column}:Q", title=y_title),
    color="country:N"
)

# Transparent selectors
selectors = alt.Chart(df_filtered).mark_point().encode(
    x="date:T",
    opacity=alt.value(0),
).add_selection(hover)

# Circles at hovered point
points = line.mark_circle().encode(
    opacity=alt.condition(hover, alt.value(1), alt.value(0))
)

# Text labels on hover
text = line.mark_text(align='left', dx=5, dy=-5).encode(
    text=alt.Text(f"{y_column}:Q", format=".2f"),
    opacity=alt.condition(hover, alt.value(1), alt.value(0))
)

# Combine layers
chart = alt.layer(line, selectors, points, text).encode(
    tooltip=tooltip
).properties(
    width=800,
    height=400,
    title=f"Quarterly {y_title} by Country"
).interactive()

st.altair_chart(chart, use_container_width=True)

# Footer
st.markdown("---")
st.caption("📊 Data from FRED (OECD CPICORQINMEI series) | Built with Streamlit + Altair")
