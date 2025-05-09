import pandas as pd
import numpy as np
import altair as alt
import streamlit as st
from pathlib import Path

# Load data
DATA_PATH = Path("data/processed/merged/core_cpi_long.csv")

@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH, parse_dates=["date"])

df = load_data()

# Select countries to compare
all_countries = df["country"].unique()
selected_countries = st.multiselect("Select countries", sorted(all_countries), default=["New Zealand", "Australia"])

# Prepare container for trend data
trend_dfs = []

# Loop through selected countries
for country in selected_countries:
    df_country = df[df["country"] == country].sort_values("date").copy()
    df_country["time_index"] = np.arange(len(df_country))

    X = np.c_[np.ones(len(df_country)), df_country["time_index"]]
    y = df_country["cpi"].values  # 🔄 REPLACED 'value' with 'cpi'

    beta, residuals, rank, s = np.linalg.lstsq(X, y, rcond=None)
    df_country["ols_trend"] = X @ beta
    df_country["country"] = country

    trend_dfs.append(df_country[["date", "cpi", "ols_trend", "country"]])

# Combine all into one dataframe
df_all = pd.concat(trend_dfs)

# Plot actual and OLS lines
actual = alt.Chart(df_all).mark_line().encode(
    x="date:T", y="cpi:Q", color="country:N", tooltip=["country", "date", "cpi"]
).properties(title="Actual CPI")

trend = alt.Chart(df_all).mark_line(strokeDash=[5, 3], color='gray').encode(
    x="date:T", y="ols_trend:Q", color="country:N", tooltip=["country", "date", "ols_trend"]
).properties(title="OLS Trend")

st.altair_chart(actual + trend, use_container_width=True)
