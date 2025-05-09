import pandas as pd
import numpy as np
import altair as alt
import streamlit as st
from pathlib import Path
from datetime import date

# Load data
DATA_PATH = Path("data/processed/merged/core_cpi_long.csv")

@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH, parse_dates=["date"])

df = load_data()

# App title and tab switcher
st.title("🌍 Core CPI Dashboard")
st.markdown("Visualise quarterly core CPI or Year-on-Year % change across countries (OECD, CPI excluding food and energy).")

tab = st.radio("Select view:", ["📈 CPI Chart", "🧮 OLS Trendline"], horizontal=True)

# ============================
# 📈 Tab 1: CPI Chart
# ============================
if tab == "📈 CPI Chart":
    countries = df["country"].unique()
    selected_countries = st.multiselect("Select countries to compare:", sorted(countries), default=["New Zealand", "United Kingdom"])

    min_date = df["date"].min().date()
    max_date = df["date"].max().date()
    start_date, end_date = st.slider(
        "Select date range:",
        min_value=min_date,
        max_value=max_date,
        value=(min_date, max_date),
        format="YYYY-MM",
        key="chart_slider"
    )

    start_ts = pd.to_datetime(start_date)
    end_ts = pd.to_datetime(end_date)

    metric = st.radio("Select metric to display:", ["CPI", "YoY % change"], horizontal=True)
    y_column = "cpi" if metric == "CPI" else "cpi_yoy"
    y_title = "Core CPI" if y_column == "cpi" else "YoY % Change"

    df_filtered = df[
        (df["country"].isin(selected_countries)) &
        (df["date"] >= start_ts) &
        (df["date"] <= end_ts)
    ]

    hover = alt.selection_single(fields=["date"], nearest=True, on="mouseover", empty="none", clear="mouseout")

    tooltip = [
        alt.Tooltip("date:T", title="Date"),
        alt.Tooltip("country:N", title="Country"),
        alt.Tooltip(
            y_column,
            title="YoY Change (%)" if y_column == "cpi_yoy" else "Core CPI",
            format=".1f" if y_column == "cpi_yoy" else ".2f"
        )
    ]

    line = alt.Chart(df_filtered).mark_line().encode(
        x="date:T",
        y=alt.Y(f"{y_column}:Q", title=y_title),
        color="country:N"
    )

    selectors = alt.Chart(df_filtered).mark_point().encode(
        x="date:T", opacity=alt.value(0),
    ).add_params(hover)

    points = line.mark_circle().encode(
        opacity=alt.condition(hover, alt.value(1), alt.value(0))
    )

    text = line.mark_text(align='left', dx=5, dy=-5).encode(
        text=alt.Text(f"{y_column}:Q", format=".2f"),
        opacity=alt.condition(hover, alt.value(1), alt.value(0))
    )

    chart = alt.layer(line, selectors, points, text).encode(
        tooltip=tooltip
    ).properties(
        width=800,
        height=400,
        title=f"Quarterly {y_title} by Country"
    ).interactive()

    st.altair_chart(chart, use_container_width=True)

# ============================
# 🧮 Tab 2: OLS Trendline
# ============================
elif tab == "🧮 OLS Trendline":
    st.markdown("This section fits a basic linear trend (OLS) to each country's CPI series and compares actual CPI to the fitted trend.")

    all_countries = sorted(df["country"].unique())
    selected_countries = st.multiselect("Select countries:", all_countries, default=["New Zealand", "Australia"])

    if not selected_countries:
        st.warning("Please select at least one country to view the trend.")
    else:
        min_date = df["date"].min().date()
        max_date = df["date"].max().date()
        start_date, end_date = st.slider(
            "Select date range:",
            min_value=min_date,
            max_value=max_date,
            value=(min_date, max_date),
            format="YYYY-MM",
            key="ols_slider"
        )
        start_ts = pd.to_datetime(start_date)
        end_ts = pd.to_datetime(end_date)

        trend_dfs = []

        for country in selected_countries:
            df_country = df[(df["country"] == country)].sort_values("date").copy()
            df_country = df_country[(df_country["date"] >= start_ts) & (df_country["date"] <= end_ts)]

            if len(df_country) < 2:
                continue

            df_country["time_index"] = np.arange(len(df_country))
            X = np.c_[np.ones(len(df_country)), df_country["time_index"]]
            y = df_country["cpi"].values

            beta, _, _, _ = np.linalg.lstsq(X, y, rcond=None)
            df_country["ols_trend"] = X @ beta
            df_country["country"] = country

            trend_dfs.append(df_country[["date", "cpi", "ols_trend", "country"]])

        if trend_dfs:
            df_all = pd.concat(trend_dfs)

            actual = alt.Chart(df_all).mark_line().encode(
                x=alt.X("date:T", title="Date"),
                y=alt.Y("cpi:Q", title="CPI"),
                color="country:N",
                tooltip=["country", "date:T", "cpi"]
            )

            trend = alt.Chart(df_all).mark_line(strokeDash=[5, 3]).encode(
                x="date:T",
                y="ols_trend:Q",
                color="country:N",
                tooltip=["country", "date:T", "ols_trend"]
            )

            combined = (actual + trend).properties(
                width=800,
                height=400,
                title="OLS Regression on CPI (Zoom Enabled)"
            ).interactive()

            st.altair_chart(combined, use_container_width=True)

            # ==================
            # Insights Table
            # ==================
            latest_insights = []
            for country in selected_countries:
                df_country = df_all[df_all["country"] == country]
                latest_row = df_country[df_country["date"] == df_country["date"].max()]
                if not latest_row.empty:
                    actual = latest_row["cpi"].values[0]
                    predicted = latest_row["ols_trend"].values[0]
                    residual = actual - predicted
                    pct_dev = (residual / predicted) * 100 if predicted != 0 else 0

                    # Refit to get slope on trimmed data
                    time_index = np.arange(len(df_country))
                    X = np.c_[np.ones(len(df_country)), time_index]
                    y = df_country["cpi"].values
                    beta, _, _, _ = np.linalg.lstsq(X, y, rcond=None)
                    slope = beta[1] * 4  # quarterly → annual
                    trend_pct = (slope / predicted) * 100 if predicted != 0 else 0

                    latest_insights.append({
                        "Country": country,
                        "Latest CPI": round(actual, 2),
                        "OLS Prediction": round(predicted, 2),
                        "Residual": round(residual, 2),
                        "% Deviation": f"{pct_dev:.1f}%",
                        "Annualised Trend (%/yr)": f"{trend_pct:.2f}%"
                    })

            if latest_insights:
                insights_df = pd.DataFrame(latest_insights)
                st.markdown("### 📊 Current CPI vs OLS Trend")
                st.dataframe(insights_df, use_container_width=True)
        else:
            st.info("No data available for the selected countries and date range.")

# Footer
st.markdown("---")
st.caption("📊 Data from FRED (OECD CPICORQINMEI series) | Built with Streamlit + Altair")
