"""Panel construction helpers for The Peacekeepers' Arms Race — NB03.

Public API
----------
build_universe, make_spine, aggregate_to_country_year, merge_onto_spine,
audit_balance, add_grouped_rolling, add_log1p_transforms, ISO3_TO_REGION
"""

import itertools
import warnings

import numpy as np
import pandas as pd


# ── ISO3 → UN macro-region map (7 regions + "Other" fallback) ────────────────
# Post-Soviet: former Soviet republics excluding Baltic states (EU/NATO members)
# Middle East: MENA convention — North Africa attributed here per polsci standard

ISO3_TO_REGION: dict[str, str] = {
    # ── Africa (Sub-Saharan) ──────────────────────────────────────────────────
    "AGO": "Africa", "BDI": "Africa", "BEN": "Africa", "BFA": "Africa",
    "BWA": "Africa", "CAF": "Africa", "CMR": "Africa", "COM": "Africa",
    "CPV": "Africa", "CIV": "Africa", "COD": "Africa", "COG": "Africa",
    "DJI": "Africa", "ERI": "Africa", "ETH": "Africa", "GAB": "Africa",
    "GHA": "Africa", "GIN": "Africa", "GMB": "Africa", "GNB": "Africa",
    "GNQ": "Africa", "KEN": "Africa", "LBR": "Africa", "LSO": "Africa",
    "MDG": "Africa", "MLI": "Africa", "MOZ": "Africa", "MRT": "Africa",
    "MUS": "Africa", "MWI": "Africa", "NAM": "Africa", "NER": "Africa",
    "NGA": "Africa", "RWA": "Africa", "SDN": "Africa", "SEN": "Africa",
    "SLE": "Africa", "SOM": "Africa", "SSD": "Africa", "STP": "Africa",
    "SWZ": "Africa", "SYC": "Africa", "TCD": "Africa", "TGO": "Africa",
    "TZA": "Africa", "UGA": "Africa", "ZAF": "Africa", "ZMB": "Africa",
    "ZWE": "Africa",
    # ── Americas ──────────────────────────────────────────────────────────────
    "ARG": "Americas", "ATG": "Americas", "BHS": "Americas", "BLZ": "Americas",
    "BOL": "Americas", "BRB": "Americas", "BRA": "Americas", "CAN": "Americas",
    "CHL": "Americas", "COL": "Americas", "CRI": "Americas", "CUB": "Americas",
    "DMA": "Americas", "DOM": "Americas", "ECU": "Americas", "GRD": "Americas",
    "GTM": "Americas", "GUY": "Americas", "HTI": "Americas", "HND": "Americas",
    "JAM": "Americas", "KNA": "Americas", "LCA": "Americas", "MEX": "Americas",
    "NIC": "Americas", "PAN": "Americas", "PER": "Americas", "PRY": "Americas",
    "SLV": "Americas", "SUR": "Americas", "TTO": "Americas", "URY": "Americas",
    "USA": "Americas", "VCT": "Americas", "VEN": "Americas",
    # ── Asia (East, South, Southeast + Mongolia) ──────────────────────────────
    "AFG": "Asia", "BGD": "Asia", "BRN": "Asia", "BTN": "Asia",
    "CHN": "Asia", "IDN": "Asia", "IND": "Asia", "JPN": "Asia",
    "KHM": "Asia", "KOR": "Asia", "LAO": "Asia", "LKA": "Asia",
    "MDV": "Asia", "MMR": "Asia", "MNG": "Asia", "MYS": "Asia",
    "NPL": "Asia", "PAK": "Asia", "PHL": "Asia", "PRK": "Asia",
    "SGP": "Asia", "THA": "Asia", "TLS": "Asia", "TWN": "Asia",
    "VNM": "Asia",
    # ── Europe (Western + Eastern + Baltic — EU/NATO/EEA members) ────────────
    "ALB": "Europe", "AND": "Europe", "AUT": "Europe", "BEL": "Europe",
    "BGR": "Europe", "BIH": "Europe", "CHE": "Europe", "CYP": "Europe",
    "CZE": "Europe", "DEU": "Europe", "DNK": "Europe", "ESP": "Europe",
    "EST": "Europe", "FIN": "Europe", "FRA": "Europe", "GBR": "Europe",
    "GRC": "Europe", "HRV": "Europe", "HUN": "Europe", "IRL": "Europe",
    "ISL": "Europe", "ITA": "Europe", "LIE": "Europe", "LTU": "Europe",
    "LUX": "Europe", "LVA": "Europe", "MCO": "Europe", "MKD": "Europe",
    "MLT": "Europe", "MNE": "Europe", "NLD": "Europe", "NOR": "Europe",
    "POL": "Europe", "PRT": "Europe", "ROU": "Europe", "SMR": "Europe",
    "SRB": "Europe", "SVK": "Europe", "SVN": "Europe", "SWE": "Europe",
    "VAT": "Europe", "XKX": "Europe",
    # ── Middle East (MENA — North Africa included per polsci convention) ───────
    "ARE": "Middle East", "BHR": "Middle East", "DZA": "Middle East",
    "EGY": "Middle East", "IRN": "Middle East", "IRQ": "Middle East",
    "ISR": "Middle East", "JOR": "Middle East", "KWT": "Middle East",
    "LBN": "Middle East", "LBY": "Middle East", "MAR": "Middle East",
    "OMN": "Middle East", "PSE": "Middle East", "QAT": "Middle East",
    "SAU": "Middle East", "SYR": "Middle East", "TUN": "Middle East",
    "TUR": "Middle East", "YEM": "Middle East",
    # ── Oceania ───────────────────────────────────────────────────────────────
    "AUS": "Oceania", "FJI": "Oceania", "FSM": "Oceania", "KIR": "Oceania",
    "MHL": "Oceania", "NRU": "Oceania", "NZL": "Oceania", "PLW": "Oceania",
    "PNG": "Oceania", "SLB": "Oceania", "TON": "Oceania", "TUV": "Oceania",
    "VUT": "Oceania", "WSM": "Oceania",
    # ── Post-Soviet (former USSR, excluding Baltic EU/NATO members) ───────────
    "ARM": "Post-Soviet", "AZE": "Post-Soviet", "BLR": "Post-Soviet",
    "GEO": "Post-Soviet", "KAZ": "Post-Soviet", "KGZ": "Post-Soviet",
    "MDA": "Post-Soviet", "RUS": "Post-Soviet", "TJK": "Post-Soviet",
    "TKM": "Post-Soviet", "UKR": "Post-Soviet", "UZB": "Post-Soviet",
}


# ── Core helpers ──────────────────────────────────────────────────────────────

def build_universe(dfs: list[pd.DataFrame], iso3_col: str = "iso3") -> list[str]:
    """Union of unique iso3 codes across input dataframes. Drops nulls and empties."""
    codes: set[str] = set()
    for df in dfs:
        if iso3_col not in df.columns:
            continue
        valid = df[iso3_col].dropna()
        valid = valid[valid.astype(str).str.strip() != ""]
        codes.update(valid.unique())
    return sorted(codes)


def make_spine(iso3_list: list[str], year_min: int, year_max: int) -> pd.DataFrame:
    """Balanced (iso3, year) grid via itertools.product.

    Returns exactly len(iso3_list) * (year_max - year_min + 1) rows.
    """
    years = range(year_min, year_max + 1)
    return pd.DataFrame(
        list(itertools.product(iso3_list, years)),
        columns=["iso3", "year"],
    )


def aggregate_to_country_year(
    df: pd.DataFrame,
    group_cols: list[str],
    agg_dict: dict,
) -> pd.DataFrame:
    """Generic groupby aggregator. Resets index.

    NaN handling policy: only pass aggregation functions that produce 0 for
    *missing events* (e.g. count, sum of conflict indicators), not for
    *missing measurements* (e.g. mean GDP). For measurements, preserve NaN
    and document the imputation decision separately at merge time.
    """
    return df.groupby(group_cols).agg(agg_dict).reset_index()


def merge_onto_spine(
    spine: pd.DataFrame,
    source_df: pd.DataFrame,
    prefix: str,
    on: tuple[str, ...] = ("iso3", "year"),
) -> pd.DataFrame:
    """Left-merge source_df onto spine, renaming non-join columns to prefix_colname.

    Emits a UserWarning if the merge produces more rows than spine (fan-out
    caused by duplicate join keys in source_df).
    """
    on_list = list(on)
    rename_map = {c: f"{prefix}_{c}" for c in source_df.columns if c not in on_list}
    source_renamed = source_df.rename(columns=rename_map)

    before = len(spine)
    merged = spine.merge(source_renamed, on=on_list, how="left")
    after = len(merged)

    if after != before:
        warnings.warn(
            f"merge_onto_spine(prefix='{prefix}'): fan-out — "
            f"{before} spine rows expanded to {after} merged rows. "
            "Deduplicate source_df on join keys before merging.",
            stacklevel=2,
        )
    return merged


def audit_balance(master: pd.DataFrame, key_vars: list[str]) -> pd.DataFrame:
    """Returns a year x variable DataFrame of non-null counts (int).

    Columns are key_vars; index is year. Used for _panel_balance_report.csv.
    """
    result = {}
    for var in key_vars:
        if var in master.columns:
            result[var] = (
                master.groupby("year")[var]
                .apply(lambda x: int(x.notna().sum()))
            )
    return pd.DataFrame(result)


def add_grouped_rolling(
    df: pd.DataFrame,
    group_col: str,
    value_col: str,
    window: int,
    stat: str = "mean",
) -> pd.Series:
    """Per-group rolling statistic WITHOUT cross-group leakage.

    Calls groupby(group_col) BEFORE rolling(), so windows are strictly
    contained within each group and never span group boundaries.
    The caller MUST sort df by (group_col, time_col) before calling.

    Raises ValueError if stat not in ['mean', 'sum', 'std'].
    """
    if stat not in ("mean", "sum", "std"):
        raise ValueError(
            f"stat must be one of ['mean', 'sum', 'std'], got {stat!r}"
        )
    return (
        df.groupby(group_col)[value_col]
        .transform(lambda x: getattr(x.rolling(window, min_periods=1), stat)())
    )


def add_log1p_transforms(
    df: pd.DataFrame,
    cols: list[str],
    prefix: str = "log_",
) -> pd.DataFrame:
    """Adds log1p-transformed columns named prefix+col. Originals are unchanged.

    Returns df with new columns appended. Does not modify the original df.
    """
    out = df.copy()
    for col in cols:
        if col in out.columns:
            out[f"{prefix}{col}"] = np.log1p(out[col])
    return out


# ── Self-tests ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=== panels.py self-tests ===\n")

    # 1. make_spine produces correct row count
    iso3s = ["USA", "GBR", "DEU", "FRA", "IND"]
    ymin, ymax = 2000, 2010
    spine = make_spine(iso3s, ymin, ymax)
    expected = len(iso3s) * (ymax - ymin + 1)
    assert len(spine) == expected, f"make_spine: expected {expected}, got {len(spine)}"
    assert list(spine.columns) == ["iso3", "year"]
    print(f"PASS  make_spine: {len(iso3s)} iso3 x {ymax - ymin + 1} years = {expected} rows")

    # 2. add_grouped_rolling — no cross-group leakage
    # Two countries, 5 years each, verify rolling does not bleed across boundary.
    test_df = pd.DataFrame({
        "iso3": ["AAA"] * 5 + ["BBB"] * 5,
        "year": list(range(2000, 2005)) * 2,
        "val":  [10, 20, 30, 40, 50, 100, 200, 300, 400, 500],
    }).sort_values(["iso3", "year"]).reset_index(drop=True)

    test_df["roll5"] = add_grouped_rolling(test_df, "iso3", "val", window=5, stat="sum")

    aaa = test_df[test_df["iso3"] == "AAA"]
    bbb = test_df[test_df["iso3"] == "BBB"]

    # AAA final year: 5-yr sum = 10+20+30+40+50 = 150
    aaa_last = float(aaa.iloc[-1]["roll5"])
    assert aaa_last == 150.0, f"AAA 5-yr sum: expected 150, got {aaa_last}"

    # BBB first year: only 1 obs in window → sum = 100 (not 150 if leaked from AAA)
    bbb_first = float(bbb.iloc[0]["roll5"])
    assert bbb_first == 100.0, f"BBB first sum: expected 100, got {bbb_first}"

    print(f"PASS  add_grouped_rolling: AAA 5yr-sum={aaa_last}, BBB_yr1={bbb_first} (no leakage)")

    # 3. merge_onto_spine — fan-out warning on duplicate join keys
    spine_small = pd.DataFrame({"iso3": ["A", "B"], "year": [2000, 2000]})
    dup_src = pd.DataFrame({
        "iso3": ["A", "A"], "year": [2000, 2000], "value": [1, 2]
    })
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        _ = merge_onto_spine(spine_small, dup_src, prefix="test")
    assert len(caught) == 1, f"Expected 1 warning, got {len(caught)}"
    assert "fan-out" in str(caught[0].message).lower()
    print("PASS  merge_onto_spine: fan-out warning triggered correctly")

    print("\nAll self-tests passed.")
