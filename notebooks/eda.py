import pandas as pd
import altair as alt

df = pd.read_csv("data/processed/merged/core_cpi_long.csv", parse_dates=["date"])

chart = alt.Chart(df).mark_line().encode(
    x="date:T",
    y="cpi:Q",
    color="country:N",
    tooltip=["date:T", "country:N", "cpi:Q"]
).properties(
    width=800,
    height=400,
    title="Quarterly Core CPI by Country"
).interactive()

chart.show()
