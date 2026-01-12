import streamlit as st
import duckdb
import pandas as pd

st.set_page_config(page_title="Commodity Dashboard", layout="wide")

@st.cache_resource
def get_connection():
    conn = duckdb.connect(database=":memory:")

    df = pd.read_csv("commodities_dataset.csv", parse_dates=["Date"])

    # Keep only Close columns
    close_cols = [c for c in df.columns if "('Close'" in c]

    long_df = df.melt(
        id_vars=["Date"],
        value_vars=close_cols,
        var_name="Commodity",
        value_name="Close"
    )

    # Clean commodity names
    long_df["Commodity"] = (
        long_df["Commodity"]
        .str.replace("_\\('Close',.*\\)", "", regex=True)
        .str.replace("_", " ")
    )

    conn.execute("CREATE TABLE commodity_prices AS SELECT * FROM long_df")
    return conn

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



