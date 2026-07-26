"""RQ2 lead-lag panel construction — extracted from NB06 Sections 0–1.

NB06 (notebooks/06_rq2_leadlag.ipynb) remains the historical record; this module
replicates its panel build exactly so NB12+ can reuse it without copy-paste:
weapon-category aggregation into 4 strategic classes, log1p transforms of
treatments and outcomes, and within-country first-differencing.
"""
import numpy as np
import pandas as pd

from src.config import CLEAN_DIR
from src.io_utils import load_checkpoint


# Strategic weapon-class grouping (4 classes from SIPRI TIV categories) — NB06
WEAPON_CLASSES: dict[str, list[str]] = {
    "AIR":      ["tiv_cat_aircraft"],
    "MISSILES": ["tiv_cat_missiles", "tiv_cat_air_defence_systems"],
    "NAVAL":    ["tiv_cat_ships", "tiv_cat_naval_weapons"],
    "GROUND":   ["tiv_cat_armoured_vehicles", "tiv_cat_artillery"],
}

OUTCOMES = ["part_n_minor", "part_n_war", "part_n_extraterritorial"]

ANALYSIS_YEAR_MIN = 1989
ANALYSIS_YEAR_MAX = 2024


def build_rq2_panel() -> pd.DataFrame:
    """Rebuild the NB06 analysis panel: d_log_tiv_{class} treatments and
    d_log_{outcome} outcomes, 1989–2024, first-differenced within country."""
    master = load_checkpoint(CLEAN_DIR / "master_panel.parquet")

    panel = master[
        (master["year"] >= ANALYSIS_YEAR_MIN) & (master["year"] <= ANALYSIS_YEAR_MAX)
    ][["iso3", "year"] + OUTCOMES + sum(WEAPON_CLASSES.values(), [])].copy()

    # Aggregate weapon categories into 4 strategic classes
    for class_name, cat_cols in WEAPON_CLASSES.items():
        panel[f"tiv_{class_name}"] = panel[cat_cols].fillna(0).sum(axis=1)
        # log1p to compress the long right tail of TIV deliveries
        panel[f"log_tiv_{class_name}"] = np.log1p(panel[f"tiv_{class_name}"])

    # log1p outcomes too (count data, right-skewed)
    for outcome in OUTCOMES:
        panel[f"log_{outcome}"] = np.log1p(panel[outcome].fillna(0))

    treatments = [f"log_tiv_{c}" for c in WEAPON_CLASSES]
    log_outcomes = [f"log_{o}" for o in OUTCOMES]

    # First-difference everything within country
    panel = panel.sort_values(["iso3", "year"])
    for col in treatments + log_outcomes:
        panel[f"d_{col}"] = panel.groupby("iso3")[col].diff()

    print(f"[rq2_panel] {len(panel):,} rows, {panel['iso3'].nunique()} countries, "
          f"{panel['year'].min()}–{panel['year'].max()}")
    return panel


def extract_country_data(panel: pd.DataFrame, cols: list[str]) -> dict:
    """Per-country numpy arrays {iso3: {col: np.array}} — NB06 Section 4 pattern."""
    country_data = {}
    for iso3, g in panel.groupby("iso3", sort=False):
        g = g.sort_values("year")
        country_data[iso3] = {col: g[col].values for col in cols}
    return country_data
