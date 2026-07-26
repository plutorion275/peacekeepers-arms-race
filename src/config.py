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

# ── Dependent territories excluded from the panel universe ────────────────────
# Inclusion policy: UN member states + TWN (Taiwan) + XKX (Kosovo) + PSE (Palestine).
# All dependent/non-sovereign territories below are excluded — they have no military,
# no UCDP participation, no V-Dem score, and no CoW membership.
# Note: XKX and VCT are sovereign/contested states and are NOT in this set.
EXCLUDED_TERRITORIES: frozenset[str] = frozenset({
    "ABW",  # Aruba (Dutch territory)
    "AIA",  # Anguilla (British territory)
    "ANT",  # Netherlands Antilles (dissolved 2010)
    "ASM",  # American Samoa
    "BES",  # Bonaire, Sint Eustatius and Saba
    "BLM",  # Saint Barthélemy
    "BMU",  # Bermuda (British territory)
    "COK",  # Cook Islands (free association with NZ, no UN membership)
    "CUW",  # Curaçao
    "CYM",  # Cayman Islands
    "FRO",  # Faroe Islands (Danish territory)
    "GIB",  # Gibraltar (British territory)
    "GLP",  # Guadeloupe (French overseas region)
    "GRL",  # Greenland (Danish territory)
    "GUM",  # Guam (US territory)
    "HKG",  # Hong Kong SAR
    "IMN",  # Isle of Man (British Crown dependency)
    "JEY",  # Jersey (British Crown dependency)
    "MAC",  # Macao SAR
    "MAF",  # Saint Martin, French part
    "MNP",  # Northern Mariana Islands (US territory)
    "MSR",  # Montserrat (British territory)
    "MTQ",  # Martinique (French overseas region)
    "MYT",  # Mayotte (French overseas region)
    "NCL",  # New Caledonia (French territory)
    "NFK",  # Norfolk Island (Australian territory)
    "NIU",  # Niue (free association with NZ, no UN membership)
    "PCN",  # Pitcairn Islands
    "PRI",  # Puerto Rico (US territory)
    "PYF",  # French Polynesia
    "REU",  # Réunion (French overseas region)
    "SGS",  # South Georgia and South Sandwich Islands
    "SHN",  # Saint Helena
    "SJM",  # Svalbard and Jan Mayen
    "SPM",  # Saint Pierre and Miquelon
    "SXM",  # Sint Maarten, Dutch part
    "TCA",  # Turks and Caicos Islands
    "TKL",  # Tokelau (NZ territory)
    "UMI",  # United States Minor Outlying Islands
    "VGB",  # British Virgin Islands
    "VIR",  # U.S. Virgin Islands
    "WLF",  # Wallis and Futuna
})