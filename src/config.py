"""Project configuration: paths, constants, reproducibility."""
from pathlib import Path

# ── Reproducibility ───────────────────────────────────────────────────────────
SEED = 42

# ── Paths ─────────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR        = PROJECT_ROOT / "data"
RAW_DIR         = DATA_DIR / "raw"
CHECKPOINT_DIR  = DATA_DIR / "checkpoints"
CLEAN_DIR       = DATA_DIR / "clean"

SIPRI_DIR       = RAW_DIR / "sipri"
UCDP_DIR        = RAW_DIR / "ucdp"
VDEM_DIR        = RAW_DIR / "vdem"
WORLDBANK_DIR   = RAW_DIR / "worldbank"
COW_DIR         = RAW_DIR / "cow"

FIGURES_DIR     = PROJECT_ROOT / "figures"
TABLES_DIR      = PROJECT_ROOT / "tables"

# ── Analytical scope ──────────────────────────────────────────────────────────
YEAR_MIN        = 1946
YEAR_MIN_EVENT  = 1989
YEAR_MAX        = 2024

HEADLINE_COUNTRIES = ["USA", "RUS", "CHN", "IND", "GBR", "FRA", "DEU",
                      "ISR", "IRN", "TUR", "PAK", "SAU"]

COLD_WAR_END    = 1989
POST_911_START  = 2002