from numpy import where
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from sqlalchemy import create_engine, text

# --- Page Config ---
st.set_page_config(layout="wide")
st.title("Fund vs Benchmark Performance Analyzer")

# --- DB Config ---
if st.secrets.env == 'LOCAL':
    server = st.secrets.SERVER["HOST"]
    username = st.secrets.SERVER["USER"]
    password = st.secrets.SERVER["PWD"]
    database = st.secrets.SERVER["DATABASE"]
else:
    server = st.secrets.LOCAL["HOST"]
    username = st.secrets.LOCAL["USER"]
    password = st.secrets.LOCAL["PWD"]
    database = st.secrets.LOCAL["DATABASE"]

conn_string = f"mssql+pyodbc://{username}:{password}@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server"
conn_engine = create_engine(conn_string)

# --- Sidebar Filters ---
st.sidebar.header("Select Period")
with st.sidebar.form(key="date_filter"):
    start_date = st.date_input("Start Date", value=pd.to_datetime("2018-01-31"))
    end_date = st.date_input("End Date", value=pd.to_datetime("2024-08-31"))
    submit = st.form_submit_button("Apply Filter")

# --- Validate Dates ---
if start_date > end_date:
    st.error(" Start date must be before end date.")
    st.stop()

# --- Load & Filter Data ---
with conn_engine.begin() as conn:
    df = pd.read_sql(text("SELECT * FROM dbo.tcs"), conn)

    df["asofmonth"] = pd.to_datetime(df["asofmonth"])
    df = df.sort_values("asofmonth")

    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    df_filtered = df[(df["asofmonth"] >= start_date) & (df["asofmonth"] <= end_date)].copy()

    if df_filtered.empty:
        st.warning("No data found for selected date range.")
        st.stop()

    # --- Return Calculations ---
    df_filtered["cum_fund"] = (1 + df_filtered["tcs"]).cumprod() - 1
    df_filtered["cum_benchmark"] = (1 + df_filtered["nifty50"]).cumprod() - 1

    months = len(df_filtered)
    years = months / 12

    cumulative_fund = df_filtered["cum_fund"].iloc[-1]
    cumulative_benchmark = df_filtered["cum_benchmark"].iloc[-1]
    ann_fund = (1 + cumulative_fund) ** (1 / years) - 1
    ann_benchmark = (1 + cumulative_benchmark) ** (1 / years) - 1
    excess_ann = ann_fund - ann_benchmark

    # --- Summary Table ---
    st.header("Fund vs Benchmark Summary for the Selected Period")
    
    summary_df = pd.DataFrame({
        "Metric": [
            "Cumulative Fund Return (%)",
            "Cumulative Benchmark Return (%)",
            "Annualized Fund Return (%)",
            "Annualized Benchmark Return (%)",
            "Excess Annualized Return (%)"
        ],
        "Value": [
            round(cumulative_fund * 100, 2),
            round(cumulative_benchmark * 100, 2),
            round(ann_fund * 100, 2),
            round(ann_benchmark * 100, 2),
            round(excess_ann * 100, 2)
        ]
    })
    st.dataframe(summary_df, use_container_width=True)

    # --- Line Chart: Cumulative Return ---
    st.subheader("Cumulative Return Over Time")
    fig_cum = go.Figure()
    fig_cum.add_trace(go.Scatter(
        x=df_filtered["asofmonth"],
        y=df_filtered["cum_fund"] * 100,
        name="Fund",
        line=dict(color="blue")
    ))
    fig_cum.add_trace(go.Scatter(
        x=df_filtered["asofmonth"],
        y=df_filtered["cum_benchmark"] * 100,
        name="Benchmark",
        line=dict(color="orange")
    ))
    fig_cum.update_layout(
        yaxis_title="Cumulative Return (%)",
        xaxis_title="Date",
        title="Cumulative Return Comparison",
        legend_title="Index"
    )
    st.plotly_chart(fig_cum, use_container_width=True)

    # --- Bar Chart: Annualized Return ---
    st.subheader("Annualized Return Comparison")
    fig_bar = go.Figure(data=[
        go.Bar(name='Fund', x=["Annualized Return"], y=[round(ann_fund * 100, 2)], marker_color="blue"),
        go.Bar(name='Benchmark', x=["Annualized Return"], y=[round(ann_benchmark * 100, 2)], marker_color="orange"),
        go.Bar(name='Excess Return', x=["Annualized Return"], y=[round(excess_ann * 100, 2)], marker_color="green"),
    ])
    fig_bar.update_layout(barmode='group', yaxis_title="Return (%)", title="Annualized Return Comparison")
    st.plotly_chart(fig_bar, use_container_width=True)