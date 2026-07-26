"""Alliance-membership helpers for the Peacekeepers' Arms Race project.

Exports:
  NATO_ACCESSION                 — {iso3: accession_year} for all 32 members
  is_nato(iso3, year)            — 1 if member in that year, else 0
  MAJOR_POWERS                   — the five P5-style major powers
  load_cow_alliances(path)       — CoW Formal Alliances v4.1 → long iso3-year df
  build_alliance_country_year()  — long df → one row per (iso3, year)

CoW alliance coverage ends in 2012 (v4.1); callers must not forward-fill
alliance variables past that year.
"""
import pandas as pd
from pathlib import Path

from src.config import CLEAN_DIR
from src.iso3 import ISO3Resolver


# ── NATO accession years (all 32 members as of 2024) ─────────────────────────
# West Germany joined 1955; the panel maps historical Germany to unified DEU,
# so DEU carries the 1955 accession year.

NATO_ACCESSION: dict[str, int] = {
    # 1949 founders
    "USA": 1949, "CAN": 1949, "GBR": 1949, "FRA": 1949, "ITA": 1949,
    "BEL": 1949, "NLD": 1949, "LUX": 1949, "DNK": 1949, "NOR": 1949,
    "ISL": 1949, "PRT": 1949,
    # Cold-War enlargements
    "GRC": 1952, "TUR": 1952,
    "DEU": 1955,
    "ESP": 1982,
    # Post-Cold-War enlargements
    "CZE": 1999, "HUN": 1999, "POL": 1999,
    "BGR": 2004, "EST": 2004, "LVA": 2004, "LTU": 2004,
    "ROU": 2004, "SVK": 2004, "SVN": 2004,
    "ALB": 2009, "HRV": 2009,
    "MNE": 2017,
    "MKD": 2020,
    "FIN": 2023,
    "SWE": 2024,
}


def is_nato(iso3: str, year: int) -> int:
    """Return 1 if *iso3* was a NATO member in *year*, else 0."""
    accession = NATO_ACCESSION.get(iso3)
    return int(accession is not None and year >= accession)


# ── Major powers (UN P5) ──────────────────────────────────────────────────────

MAJOR_POWERS: frozenset[str] = frozenset({"USA", "RUS", "CHN", "GBR", "FRA"})


# ── CoW Formal Alliances v4.1 (by-member yearly) ─────────────────────────────
# state_name variants that the shared resolver tiers do not cover.
# Historical-state successions (Soviet Union→RUS, Yugoslavia→SRB,
# Czechoslovakia→CZE, …) are already in iso3.GLOBAL_OVERRIDES.

COW_ALLIANCE_OVERRIDES: dict[str, str | None] = {
    "Antigua & Barbuda":              "ATG",
    "Cape Verde":                     "CPV",
    "German Federal Republic":        "DEU",   # West Germany → unified DEU
    "St. Kitts and Nevis":            "KNA",
    "St. Lucia":                      "LCA",
    "St. Vincent and the Grenadines": "VCT",
    "Swaziland":                      "SWZ",   # renamed Eswatini 2018
    "Yemen People's Republic":        "YEM",   # South Yemen → unified YEM
}

_DOWNLOAD_INSTRUCTION = (
    "download alliance_v4.1_by_member_yearly.csv from correlatesofwar.org "
    "-> Data Sets -> Formal Alliances v4.1, place in data/raw/cow/"
)


def load_cow_alliances(path: Path) -> pd.DataFrame:
    """Load CoW Formal Alliances v4.1 by-member-yearly → long ISO3-year frame.

    Returns columns: iso3, year, version4id, defense, neutrality,
    nonaggression, entente. Filtered to year >= 1946. Unmatched state names
    are logged to data/clean/_alliance_unmatched.csv and dropped.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"{path} not found — {_DOWNLOAD_INSTRUCTION}")

    df = pd.read_csv(path, low_memory=False)
    df = df[df["year"] >= 1946].copy()

    resolver = ISO3Resolver(dataset_overrides=COW_ALLIANCE_OVERRIDES)
    df["iso3"] = resolver.resolve_series(df["state_name"], dataset="cow_alliance")

    unmatched = resolver.report_unmatched()
    if len(unmatched) > 0:
        audit_path = CLEAN_DIR / "_alliance_unmatched.csv"
        audit_path.parent.mkdir(parents=True, exist_ok=True)
        unmatched.to_csv(audit_path, index=False)
        print(f"[alliances] {len(unmatched)} unmatched state names dropped "
              f"→ logged to {audit_path.name}")
        print(unmatched.to_string(index=False))
    else:
        print("[alliances] all state names resolved to ISO3")

    df = df.dropna(subset=["iso3"])
    out = df[["iso3", "year", "version4id",
              "defense", "neutrality", "nonaggression", "entente"]].copy()
    # Historical-state mapping (e.g. GDR and FRG both → DEU) can duplicate a
    # membership-year within one alliance; keep one row per member-alliance-year.
    out = out.drop_duplicates(subset=["iso3", "year", "version4id"])
    print(f"[alliances] long table: {len(out):,} rows, "
          f"{out['year'].min()}–{out['year'].max()}, "
          f"{out['iso3'].nunique()} countries")
    return out.reset_index(drop=True)


def build_alliance_country_year(long_df: pd.DataFrame) -> pd.DataFrame:
    """Collapse the long alliance table to one row per (iso3, year).

    n_defense_pacts      — distinct alliances (version4id) with defense==1
    has_major_power_ally — 1 if the country shares any defense pact-year with a
                           MAJOR_POWERS member other than itself (major powers
                           are scored against the other four the same way)
    """
    dfn = long_df[long_df["defense"] == 1]

    counts = (
        dfn.groupby(["iso3", "year"])["version4id"]
           .nunique()
           .rename("n_defense_pacts")
           .reset_index()
    )

    # Self-join on alliance-year to find defense-pact partners, then flag
    # rows whose partner (not the country itself) is a major power.
    pairs = dfn[["iso3", "year", "version4id"]].merge(
        dfn[["iso3", "year", "version4id"]].rename(columns={"iso3": "partner_iso3"}),
        on=["version4id", "year"],
    )
    pairs = pairs[pairs["iso3"] != pairs["partner_iso3"]]
    major = (
        pairs.assign(has_major_power_ally=pairs["partner_iso3"].isin(MAJOR_POWERS).astype(int))
             .groupby(["iso3", "year"])["has_major_power_ally"]
             .max()
             .reset_index()
    )

    out = counts.merge(major, on=["iso3", "year"], how="left")
    out["has_major_power_ally"] = out["has_major_power_ally"].fillna(0).astype(int)

    print(f"[alliances] country-year table: {len(out):,} rows, "
          f"{out['year'].min()}–{out['year'].max()}, "
          f"{out['iso3'].nunique()} countries")

    usa_ok = (out.loc[out["iso3"] == "USA", "n_defense_pacts"] > 0).any()
    deu_1990 = out.loc[(out["iso3"] == "DEU") & (out["year"] == 1990),
                       "has_major_power_ally"]
    deu_ok = (not deu_1990.empty) and deu_1990.iloc[0] == 1
    print(f"[alliances] spot check — USA n_defense_pacts > 0: "
          f"{'PASS' if usa_ok else 'FAIL'}; "
          f"DEU 1990 has_major_power_ally == 1: {'PASS' if deu_ok else 'FAIL'}")
    return out
