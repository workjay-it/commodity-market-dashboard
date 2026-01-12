import streamlit as st
import duckdb
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="Commodity Dashboard", layout="wide")

DB_PATH = Path(__file__).resolve().parents[1] / "Analysis" / "commodities.duckdb"

if not DB_PATH.exists():
    st.error(f"Database not found at {DB_PATH}")
    st.stop()

@st.cache_resource
def get_connection():
    return duckdb.connect(DB_PATH, read_only=True)

conn = get_connection()

@st.cache_data
def load_commodities():
    return conn.execute("""
        SELECT DISTINCT Commodity
        FROM commodity_prices
        ORDER BY Commodity
    """).df()

@st.cache_data
def load_price_data(commodity):
    query = f"""
    SELECT
        Date,
        Close,
        AVG(Close) OVER (
            ORDER BY Date
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) AS ma_30,
        AVG(Close) OVER (
            ORDER BY Date
            ROWS BETWEEN 89 PRECEDING AND CURRENT ROW
        ) AS ma_90
    FROM commodity_prices
    WHERE Commodity = '{commodity}'
    ORDER BY Date
    """
    return conn.execute(query).df()

st.title("📈 Commodity Market Dashboard")

commodity = st.selectbox(
    "Select Commodity",
    load_commodities()["Commodity"]
)

df = load_price_data(commodity)
df = df.set_index("Date")

st.line_chart(df[["Close", "ma_30", "ma_90"]])

