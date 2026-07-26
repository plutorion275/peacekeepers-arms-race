"""
Military Technology Score (MTS) construction functions.
Source notebook: notebooks/04_mts_construction.ipynb
Do not edit via %%writefile — edit this file directly.
Imported by: NB04, NB05, NB06, NB07.
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.decomposition import PCA


def compute_mts_milex(df: pd.DataFrame) -> pd.Series:
    """
    mts_milex = MinMax(log1p(sipri_milex_const2024_usd)) per country-year.
    NaN where milex is NaN. Returns a Series indexed like df.
    """
    log_milex = np.log1p(df["sipri_milex_const2024_usd"])
    valid = log_milex.notna()
    result = pd.Series(np.nan, index=df.index, name="mts_milex")
    if valid.sum() > 0:
        scaler = MinMaxScaler()
        result.loc[valid] = scaler.fit_transform(
            log_milex[valid].values.reshape(-1, 1)
        ).ravel()
    return result


def compute_mts_tiv(df: pd.DataFrame) -> pd.Series:
    """
    mts_tiv = MinMax(log1p(rolling 5-year cumulative tiv_imports_total)).
    Rolling window is grouped by iso3 to prevent cross-country leakage.
    min_periods=1 so early years are not dropped.
    Returns a Series indexed like df.

    NOTE: The caller must set mts_tiv = NaN where tiv_imports_5yr_sum == 0
    (no acquisition activity in the 5yr window). Country-years with zero
    cumulative imports should not receive the MinMax floor value — that
    floor contaminates continuous-variation assumptions in OLS/FE regressions.
    Use tiv_ever_imported (binary) to absorb that component separately.
    """
    # Sort ensures temporal order before rolling; result is reindexed back to df's order
    sorted_df = df.sort_values(["iso3", "year"])
    roll_sum = (
        sorted_df.groupby("iso3")["tiv_imports_total"]
        .transform(lambda x: x.rolling(5, min_periods=1).sum())
    )
    roll_sum = roll_sum.where(roll_sum > 0, np.nan)
    log_roll = np.log1p(roll_sum)
    valid = log_roll.notna()
    result = pd.Series(np.nan, index=sorted_df.index, name="mts_tiv")
    if valid.sum() > 0:
        scaler = MinMaxScaler()
        result.loc[valid] = scaler.fit_transform(
            log_roll[valid].values.reshape(-1, 1)
        ).ravel()
    return result.reindex(df.index)


def compute_mts_pca(df: pd.DataFrame) -> pd.Series:
    """
    mts_pca = MinMax(PC1) of four standardised inputs:
      log1p(sipri_milex_const2024_usd)
      log1p(tiv_imports_total)
      log1p(cow_milper)
      log1p(sipri_milex_const2024_usd / wb_gdp_usd * 100)  -- milex % GDP

    Coverage ends at ~2016 because cow_milper (CoW CINC) ends at 2016.
    Use compute_mts_pca_3feat() for 2017–2024 coverage.
    Only rows where ALL four inputs are non-NaN enter the PCA.
    Sign-corrected so PC1 is positively correlated with log_milex.
    PC1 is MinMax-scaled to [0,1] before return.
    Returns a Series (same index as df, NaN for excluded rows).
    """
    milex_gdp_pct = df["sipri_milex_const2024_usd"] / df["wb_gdp_usd"].replace(0, np.nan) * 100
    features = pd.DataFrame(
        {
            "log_milex":     np.log1p(df["sipri_milex_const2024_usd"]),
            "log_tiv":       np.log1p(df["tiv_imports_total"]),
            "log_milper":    np.log1p(df["cow_milper"]),
            "log_milex_gdp": np.log1p(milex_gdp_pct),
        },
        index=df.index,
    )

    valid = features.notna().all(axis=1) & np.isfinite(features.values).all(axis=1)
    result = pd.Series(np.nan, index=df.index, name="mts_pca")

    if valid.sum() < 2:
        print("WARNING: fewer than 2 complete rows — mts_pca returning all NaN")
        return result

    X = features.loc[valid].values
    X_scaled = StandardScaler().fit_transform(X)

    pca = PCA(n_components=1, random_state=42)
    pc1 = pca.fit_transform(X_scaled).ravel()

    evr = pca.explained_variance_ratio_[0]
    print(f"mts_pca PCA explained variance ratio (PC1): {evr:.4f}")
    if evr < 0.60:
        print("WARNING: PC1 explains < 60% of variance — review MTS PCA specification")

    # Sign-correct: PC1 must be positively correlated with log_milex
    _sign_corr = np.corrcoef(pc1, features.loc[valid, "log_milex"].values)[0, 1]
    if np.isfinite(_sign_corr) and _sign_corr < 0:
        pc1 = -pc1

    # MinMax to [0,1] for comparability with mts_milex and mts_tiv
    pc1_scaled = MinMaxScaler().fit_transform(pc1.reshape(-1, 1)).ravel()
    result.loc[valid] = pc1_scaled
    return result


def compute_mts_pca_3feat(df: pd.DataFrame) -> pd.Series:
    """
    mts_pca_3feat = MinMax(PC1) of three standardised inputs:
      log1p(sipri_milex_const2024_usd)
      log1p(tiv_imports_total)
      log1p(sipri_milex_const2024_usd / wb_gdp_usd * 100)  -- milex % GDP

    Drops log_milper (CoW CINC, ends ~2016) to extend coverage through 2024.
    Primary MTS specification for NB05–NB07 regressions and clustering.
    Same pipeline as compute_mts_pca: StandardScaler -> PCA(n_components=1)
    -> sign-correct against log_milex -> MinMax scale to [0,1].
    Returns a Series (same index as df, NaN for excluded rows).
    """
    milex_gdp_pct = df["sipri_milex_const2024_usd"] / df["wb_gdp_usd"].replace(0, np.nan) * 100
    features = pd.DataFrame(
        {
            "log_milex":     np.log1p(df["sipri_milex_const2024_usd"]),
            "log_tiv":       np.log1p(df["tiv_imports_total"]),
            "log_milex_gdp": np.log1p(milex_gdp_pct),
        },
        index=df.index,
    )

    valid = features.notna().all(axis=1) & np.isfinite(features.values).all(axis=1)
    result = pd.Series(np.nan, index=df.index, name="mts_pca_3feat")

    if valid.sum() < 2:
        print("WARNING: fewer than 2 complete rows — mts_pca_3feat returning all NaN")
        return result

    X = features.loc[valid].values
    X_scaled = StandardScaler().fit_transform(X)

    pca = PCA(n_components=1, random_state=42)
    pc1 = pca.fit_transform(X_scaled).ravel()

    evr = pca.explained_variance_ratio_[0]
    print(f"mts_pca_3feat PCA explained variance ratio (PC1): {evr:.4f}")
    if evr < 0.60:
        print("WARNING: PC1 explains < 60% of variance — review mts_pca_3feat specification")

    # Sign-correct: PC1 must be positively correlated with log_milex
    _sign_corr = np.corrcoef(pc1, features.loc[valid, "log_milex"].values)[0, 1]
    if np.isfinite(_sign_corr) and _sign_corr < 0:
        pc1 = -pc1

    # MinMax to [0,1] for comparability
    pc1_scaled = MinMaxScaler().fit_transform(pc1.reshape(-1, 1)).ravel()
    result.loc[valid] = pc1_scaled
    return result
