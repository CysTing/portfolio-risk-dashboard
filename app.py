
import streamlit as st
import pandas as pd
import yfinance as yf

from finance import portfolio_returns, summary_stats


st.set_page_config(
    page_title="Portfolio Risk Dashboard",
    layout="wide"
)

st.title("Portfolio Risk & Return Dashboard")

st.write(
    "Analyze a two-stock portfolio and compare its "
    "historical performance with the S&P 500 ETF (SPY)."
)

TICKERS = ["AAPL", "MSFT", "SPY"]

# User controls
period = st.selectbox(
    "Historical period",
    ["6mo", "1y", "2y", "5y"],
    index=1
)

apple_pct = st.slider(
    "Apple allocation (%)",
    min_value=0,
    max_value=100,
    value=50,
    step=5
)

apple_weight = apple_pct / 100
msft_weight = 1 - apple_weight

st.write(f"Apple: {apple_pct}%")
st.write(f"Microsoft: {100 - apple_pct}%")


@st.cache_data(ttl=3600)
def load_prices(selected_period):
    raw = yf.download(
        tickers=TICKERS,
        period=selected_period,
        interval="1d",
        auto_adjust=True,
        group_by="column",
        multi_level_index=True,
        progress=False
    )

    if raw.empty:
        raise ValueError("No market data was returned.")

    prices = raw["Close"].reindex(columns=TICKERS)
    prices = prices.dropna()

    if len(prices) < 30:
        raise ValueError("Not enough complete price observations.")

    return prices


try:
    prices = load_prices(period)
except Exception as error:
    st.error(f"Could not load market data: {error}")
    st.stop()


# Calculate daily returns
daily_returns = prices.pct_change(fill_method=None).dropna()

portfolio_daily = portfolio_returns(
    daily_returns[["AAPL", "MSFT"]],
    [apple_weight, msft_weight]
)

benchmark_daily = daily_returns["SPY"]

# Portfolio and benchmark statistics
portfolio_stats = summary_stats(portfolio_daily)
benchmark_stats = summary_stats(benchmark_daily)

# Show key performance indicators
col1, col2, col3 = st.columns(3)

col1.metric(
    "Portfolio Total Return",
    f"{portfolio_stats['total_return']:.2%}"
)

col2.metric(
    "Annualized Volatility",
    f"{portfolio_stats['volatility']:.2%}"
)

col3.metric(
    "Maximum Drawdown",
    f"{portfolio_stats['max_drawdown']:.2%}"
)

# Build cumulative performance comparison
comparison = pd.DataFrame({
    "Portfolio": portfolio_daily,
    "SPY Benchmark": benchmark_daily
})

growth = (1 + comparison).cumprod()

st.subheader("Growth of $1 Invested")
st.line_chart(growth)

st.subheader("Portfolio vs Benchmark")

results = pd.DataFrame({
    "Portfolio": portfolio_stats,
    "SPY": benchmark_stats
})

st.dataframe(results.style.format("{:.2%}"))

st.subheader("Historical Adjusted Closing Prices")
st.line_chart(prices[["AAPL", "MSFT"]])

st.caption(
    "Educational analysis only. Assumes daily rebalancing "
    "to constant portfolio weights, no transaction costs, "
    "no taxes, and USD-denominated assets. "
    "Historical performance does not predict future returns."
)
