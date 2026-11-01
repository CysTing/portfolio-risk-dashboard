
import numpy as np
import pandas as pd


def portfolio_returns(daily_returns, weights):
    """Calculate weighted portfolio daily returns."""

    weights = np.asarray(weights, dtype=float)

    if len(weights) != daily_returns.shape[1]:
        raise ValueError("Number of weights must match assets.")

    if np.any(weights < 0) or not np.isclose(weights.sum(), 1):
        raise ValueError("Weights must be nonnegative and sum to 1.")

    return daily_returns.dot(weights)


def summary_stats(daily_returns):
    """Calculate return, volatility and maximum drawdown."""

    if len(daily_returns) < 2:
        raise ValueError("Not enough returns to calculate statistics.")

    wealth = (1 + daily_returns).cumprod()

    total_return = wealth.iloc[-1] - 1

    annual_volatility = (
        daily_returns.std(ddof=1) * np.sqrt(252)
    )

    running_peak = wealth.cummax().clip(lower=1.0)
    drawdown = wealth / running_peak - 1
    max_drawdown = drawdown.min()

    return {
        "total_return": total_return,
        "volatility": annual_volatility,
        "max_drawdown": max_drawdown
    }

