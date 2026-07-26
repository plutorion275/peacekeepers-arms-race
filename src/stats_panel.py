"""Panel statistics and causality tests for The Peacekeepers' Arms Race.

Provides functions to run the Dumitrescu-Hurlin (2012) panel Granger
non-causality test, using both standard statsmodels OLS and a fast NumPy-based
implementation.
"""

from typing import Any, Dict, Tuple, Union
import numpy as np
import pandas as pd
from scipy.stats import norm
import statsmodels.api as sm


def dumitrescu_hurlin(
    panel_df: pd.DataFrame,
    x_col: str,
    y_col: str,
    lag: int,
    min_obs: int = 12
) -> Dict[str, Union[float, int]]:
    """Perform the Dumitrescu-Hurlin (2012) panel Granger non-causality test.

    Parameters
    ----------
    panel_df : pd.DataFrame
        Panel data containing `iso3`, `year`, and the columns for x and y.
    x_col : str
        The treatment/independent variable column name.
    y_col : str
        The outcome/dependent variable column name.
    lag : int
        The lag order for the Granger test.
    min_obs : int, default 12
        Minimum observations per country after lagging/differencing.

    Returns
    -------
    Dict[str, Union[float, int]]
        A dictionary containing:
        - "Z": Standardized Z-statistic.
        - "p": One-sided p-value.
        - "n_countries": Number of countries included in the final statistic.
        - "W_bar": Mean of individual Wald statistics.
    """
    countries = panel_df["iso3"].unique()
    W_stats = []

    for iso3 in countries:
        sub = panel_df[panel_df["iso3"] == iso3].sort_values("year").reset_index(drop=True)
        sub = sub.dropna(subset=[x_col, y_col]).copy()
        
        # Construct lagged regressors
        for k in range(1, lag + 1):
            sub[f"_ylag{k}"] = sub[y_col].shift(k)
            sub[f"_xlag{k}"] = sub[x_col].shift(k)
        sub = sub.dropna()
        
        if len(sub) < min_obs:
            continue
            
        y_lags = [f"_ylag{k}" for k in range(1, lag + 1)]
        x_lags = [f"_xlag{k}" for k in range(1, lag + 1)]
        
        Xr = sm.add_constant(sub[y_lags])
        Xu = sm.add_constant(sub[y_lags + x_lags])
        y_vec = sub[y_col]
        
        # Skip if treatment series has no variation (constant)
        if sub[x_lags].std().sum() == 0:
            continue
            
        try:
            res_r = sm.OLS(y_vec, Xr).fit()
            res_u = sm.OLS(y_vec, Xu).fit()
            T = len(sub)
            K = Xu.shape[1]
            rss_r, rss_u = res_r.ssr, res_u.ssr
            
            # Numerical-stability guard: skip pathological near-zero RSS_u
            # (happens when sparse outcome + lagged regressors achieve near-perfect fit)
            y_var = float(np.var(y_vec.values))
            if rss_u <= 0 or (T - K) <= 0 or rss_u < 1e-8 * y_var * T:
                continue
                
            W = ((rss_r - rss_u) / lag) / (rss_u / (T - K))
            
            # Cap individual W contributions to prevent one country from dominating the mean
            if np.isfinite(W) and 0 <= W <= 1000:
                W_stats.append(W)
        except Exception:
            continue

    N = len(W_stats)
    if N < 5:
        return {"Z": np.nan, "p": np.nan, "n_countries": N, "W_bar": np.nan}
        
    W_bar = float(np.mean(W_stats))
    Z = np.sqrt(N / (2 * lag)) * (W_bar - lag) / np.sqrt(lag)
    p = 1.0 - norm.cdf(Z)  # one-sided: H1 is positive Granger causation
    
    return {"Z": Z, "p": p, "n_countries": N, "W_bar": W_bar}


def dumitrescu_hurlin_fast(
    country_dict: Dict[str, Dict[str, np.ndarray]],
    treat_col: str,
    outcome_col: str,
    lag: int,
    min_obs: int = 12
) -> Tuple[float, float, int]:
    """Fast Dumitrescu-Hurlin test using NumPy lstsq instead of statsmodels OLS.

    Parameters
    ----------
    country_dict : Dict[str, Dict[str, np.ndarray]]
        A dictionary mapping country ISO3 code to a dict of column-name array pairs.
    treat_col : str
        The treatment column name.
    outcome_col : str
        The outcome column name.
    lag : int
        The lag order for the Granger test.
    min_obs : int, default 12
        Minimum observations per country after lagging/differencing.

    Returns
    -------
    Tuple[float, float, int]
        A tuple of (Z, p_value, n_countries).
    """
    W_stats = []
    for arrs in country_dict.values():
        x_full = arrs[treat_col]
        y_full = arrs[outcome_col]
        mask = np.isfinite(x_full) & np.isfinite(y_full)
        
        if mask.sum() < min_obs + lag + 1:
            continue
            
        x = x_full[mask]
        y = y_full[mask]
        T = len(x) - lag
        
        if T < min_obs:
            continue
            
        y_t = y[lag:]
        y_lag = np.column_stack([y[lag - k : len(y) - k] for k in range(1, lag + 1)])
        x_lag = np.column_stack([x[lag - k : len(x) - k] for k in range(1, lag + 1)])
        
        Xr = np.column_stack([np.ones(T), y_lag])
        Xu = np.column_stack([np.ones(T), y_lag, x_lag])
        
        if x_lag.std() == 0:
            continue
            
        try:
            cr, *_ = np.linalg.lstsq(Xr, y_t, rcond=None)
            cu, *_ = np.linalg.lstsq(Xu, y_t, rcond=None)
            rss_r = ((y_t - Xr @ cr) ** 2).sum()
            rss_u = ((y_t - Xu @ cu) ** 2).sum()
            K = Xu.shape[1]
            y_var = float(np.var(y_t))
            
            if rss_u <= 0 or (T - K) <= 0 or rss_u < 1e-8 * y_var * T:
                continue
                
            W = ((rss_r - rss_u) / lag) / (rss_u / (T - K))
            if np.isfinite(W) and 0 <= W <= 1000:
                W_stats.append(W)
        except (np.linalg.LinAlgError, ValueError):
            continue
            
    N = len(W_stats)
    if N < 5:
        return np.nan, np.nan, N

    W_bar = float(np.mean(W_stats))
    Z = np.sqrt(N / (2 * lag)) * (W_bar - lag) / np.sqrt(lag)
    p = 1.0 - norm.cdf(Z)

    return Z, p, N


# ══════════════════════════════════════════════════════════════════════════════
# Two-way FE panel estimators — extracted from NB10 so NB11+ can import them.
# Estimator settings (NB05 convention, do not change): PanelOLS.from_formula,
# EntityEffects + TimeEffects, SEs clustered by entity and time,
# drop_absorbed=True, lagged DV auto-included when {outcome}_lag1 exists.
# ══════════════════════════════════════════════════════════════════════════════

from scipy import stats
from linearmodels.panel import PanelOLS


def run_panel_fe(df, outcome, mts, controls, clusters=True, interaction=None):
    """Two-way FE panel regression (NB05 estimator), optionally extended with an
    MTS × moderator interaction. Returns (result, interaction_col_name)."""
    lagged_dv = f"{outcome}_lag1"
    cols_needed = [outcome, mts] + controls
    if lagged_dv in df.columns:
        cols_needed.append(lagged_dv)
        all_controls = controls + [lagged_dv]
    else:
        all_controls = controls
    if interaction is not None:
        cols_needed.append(interaction)
    sub = df.dropna(subset=cols_needed).copy()
    rhs = [mts]
    int_col = None
    if interaction is not None:
        int_col = f"{mts}_x_{interaction}"
        sub[int_col] = sub[mts] * sub[interaction]
        # moderator main effect stays in the formula; drop_absorbed removes it
        # when time-invariant (absorbed by EntityEffects)
        rhs += [int_col, interaction]
    rhs += all_controls
    sub = sub.set_index(["iso3", "year"])
    formula = (
        f"{outcome} ~ 1 + " + " + ".join(rhs)
        + " + EntityEffects + TimeEffects"
    )
    model = PanelOLS.from_formula(formula, data=sub, drop_absorbed=True)
    if clusters:
        return model.fit(cov_type="clustered", cluster_entity=True, cluster_time=True), int_col
    return model.fit(), int_col


def marginal_effect(res, mts, int_col):
    """β_mts + β_int with SE = sqrt(V[mts] + V[int] + 2*Cov) from res.cov."""
    me = res.params[mts] + res.params[int_col]
    V = res.cov
    se = float(np.sqrt(V.loc[mts, mts] + V.loc[int_col, int_col] + 2 * V.loc[mts, int_col]))
    p = 2 * (1 - stats.norm.cdf(abs(me / se)))
    return me, se, p


def run_panel_fe_interactions(df, outcome, mts, controls, moderator_dummies):
    """NB05 estimator with explicit MTS × moderator interactions.

    Generalizes NB10's run_panel_fe_region: *moderator_dummies* is a
    {label: column} dict instead of a module-level region dict, and moderator
    columns may be 0/1 dummies or continuous (the interaction is a plain
    product sub[mts] * sub[col]). Moderator columns join the dropna subset.
    Returns (result, {label: interaction_col}).
    """
    lagged_dv = f"{outcome}_lag1"
    cols_needed = [outcome, mts] + controls + list(moderator_dummies.values())
    if lagged_dv in df.columns:
        cols_needed.append(lagged_dv)
        all_controls = controls + [lagged_dv]
    else:
        all_controls = controls
    # dedupe, preserving order — a moderator column may also be a control
    cols_needed = list(dict.fromkeys(cols_needed))
    sub = df.dropna(subset=cols_needed).copy()
    rhs = [mts]
    int_cols = {}
    for label, col in moderator_dummies.items():
        icol = f"{mts}_x_{col}"
        sub[icol] = sub[mts] * sub[col]
        int_cols[label] = icol
        rhs += [icol, col]   # time-invariant main effects absorb into EntityEffects
    rhs += all_controls
    rhs = list(dict.fromkeys(rhs))
    sub = sub.set_index(["iso3", "year"])
    formula = (
        f"{outcome} ~ 1 + " + " + ".join(rhs)
        + " + EntityEffects + TimeEffects"
    )
    model = PanelOLS.from_formula(formula, data=sub, drop_absorbed=True)
    return model.fit(cov_type="clustered", cluster_entity=True, cluster_time=True), int_cols


def joint_wald_interactions(res, int_cols):
    """Joint Wald test that all interaction coefficients are zero."""
    names = list(res.params.index)
    present = [c for c in int_cols.values() if c in names]
    R = np.zeros((len(present), len(names)))
    for i, c in enumerate(present):
        R[i, names.index(c)] = 1.0
    wt = res.wald_test(restriction=R)
    return float(wt.stat), float(wt.pval)
