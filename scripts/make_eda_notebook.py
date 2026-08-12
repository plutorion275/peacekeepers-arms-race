"""Generate notebooks/00_eda_overview.ipynb for The Peacekeepers' Arms Race."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import nbformat as nbf

nb = nbf.v4.new_notebook()
nb.metadata["kernelspec"] = {
    "display_name": "Python 3",
    "language": "python",
    "name": "python3",
}
nb.metadata["language_info"] = {
    "codemirror_mode": {"name": "ipython", "version": 3},
    "file_extension": ".py",
    "mimetype": "text/x-python",
    "name": "python",
    "pygments_lexer": "ipython3",
    "version": "3.11.0",
}

md = nbf.v4.new_markdown_cell
code = nbf.v4.new_code_cell
cells = []

# ══════════════════════════════════════════════════════════════════════════════
# TITLE
# ══════════════════════════════════════════════════════════════════════════════
cells.append(md(
    "# NB-00 — Exploratory Data Analysis Overview\n"
    "## The Peacekeepers' Arms Race: Testing the Stability–Instability Paradox\n\n"
    "**Purpose:** This notebook documents all nine datasets used in the study — where "
    "they come from, how they were cleaned, and what the master analytical panel looks "
    "like. It is structured as a walkthrough for a lecturer unfamiliar with the pipeline.\n\n"
    "---"
))

# ══════════════════════════════════════════════════════════════════════════════
# CELL: Setup
# ══════════════════════════════════════════════════════════════════════════════
cells.append(code(
"""import sys
sys.path.insert(0, '..')

import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from pathlib import Path
from IPython.display import display

from src.config import CLEAN_DIR, FIGURES_DIR

EDA_DIR = FIGURES_DIR / 'eda'
EDA_DIR.mkdir(parents=True, exist_ok=True)

sns.set_theme(style='whitegrid')
pd.set_option('display.max_columns', 60)
pd.set_option('display.max_rows', 50)

PROVIDER_COLORS = {
    'UCDP':       '#2196F3',
    'SIPRI':      '#FF5722',
    'World Bank': '#4CAF50',
    'V-Dem':      '#9C27B0',
    'CoW':        '#FF9800',
}

REGION_PAL = {
    'Africa':      '#E74C3C',
    'Americas':    '#3498DB',
    'Asia':        '#2ECC71',
    'Europe':      '#9B59B6',
    'Middle East': '#E67E22',
    'Oceania':     '#1ABC9C',
    'Post-Soviet': '#95A5A6',
    'Other':       '#BDC3C7',
}

def _load(fname):
    \"\"\"Load a clean parquet with a clear error if missing.\"\"\"
    path = CLEAN_DIR / fname
    try:
        df = pd.read_parquet(path)
        print(f'  loaded {fname}  {df.shape}')
        return df
    except FileNotFoundError:
        print(f'  MISSING: {path}  --  run NB01-NB03 first')
        return None

print('Setup complete.')
print(f'Clean dir  : {CLEAN_DIR}')
print(f'EDA figures: {EDA_DIR}')
"""
))

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — Project Overview
# ══════════════════════════════════════════════════════════════════════════════
cells.append(md(
    "---\n"
    "## Section 1 — Project Overview\n\n"
    "### Research Question\n\n"
    "This study tests the **Stability-Instability Paradox** (SIP): the theory that "
    "nuclear deterrence between adversaries stabilises full-scale war (because the threat "
    "of nuclear escalation is too great) but simultaneously *enables* limited proxy wars "
    "and conventional skirmishes below the nuclear threshold (because neither side can "
    "escalate without risking annihilation). If the paradox holds, we should see nuclear "
    "states fighting *more* small-scale conflicts abroad while fighting *fewer* "
    "full-scale wars at home.\n\n"
    "### Three Research Questions\n\n"
    "| RQ | Question | Method |\n"
    "|----|----------|--------|\n"
    "| **RQ1** | Do countries with higher military spending and arms imports fight more "
    "extraterritorial small wars? | Panel regression (country-year, 1989–2024) |\n"
    "| **RQ2** | Do arms transfers to a country predict an increase in conflict events "
    "in the following months? | Time-series lead-lag analysis (monthly GED events) |\n"
    "| **RQ3** | Can countries be clustered by their conflict profiles and military "
    "posture? Do nuclear/allied states form distinct clusters? | Dimensionality reduction "
    "+ k-means clustering (cross-section) |\n\n"
    "### The Nine Datasets\n\n"
    "The study integrates nine public datasets from five providers. Together they give a "
    "79-year panel (1946–2024) of conflict events, military spending, arms transfers, "
    "economic controls, democracy scores, and military capabilities for up to 192 countries."
))

cells.append(code(
"""sources = pd.DataFrame({
    'Source': [
        'UCDP ACD', 'UCDP GED', 'UCDP BRD', 'UCDP Dyadic',
        'SIPRI MILEX', 'SIPRI TIV Register',
        'World Bank WDI', 'V-Dem', 'CoW CINC',
    ],
    'Provider': [
        'Uppsala Conflict Data Program', 'Uppsala', 'Uppsala', 'Uppsala',
        'Stockholm International Peace Research Institute', 'SIPRI',
        'World Bank', 'V-Dem Institute', 'Correlates of War',
    ],
    'Granularity': [
        'Conflict-year', 'Event (geocoded)', 'Conflict-year', 'Dyad-year',
        'Country-year', 'Transfer-year',
        'Country-year', 'Country-year', 'Country-year',
    ],
    'Years': [
        '1946-2024', '1989-2024', '1989-2024', '1946-2024',
        '1949-2025', '1950-2025',
        '1960-2024', '1946-2024', '1816-2016',
    ],
    'Role in analysis': [
        'Conflict counts at location (acd_* cols)',
        'Monthly events for RQ2 outcome variable',
        'Battle deaths at conflict location (brd_* cols)',
        'Participation panel + is_extraterritorial flag (part_* cols)',
        'Military expenditure treatment variable',
        'Arms transfer treatment variable (TIV)',
        'GDP, population, per-capita income controls (wb_* cols)',
        'Electoral democracy index (vdem_v2x_polyarchy)',
        'CINC military capability index (cutoff 2016)',
    ],
})

display(sources.set_index('Source').style.set_table_styles([
    {'selector': 'th', 'props': [('font-weight', 'bold'), ('background', '#f0f0f0')]},
    {'selector': 'td', 'props': [('text-align', 'left'), ('white-space', 'normal')]},
]))
"""
))

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — Raw Dataset Shapes
# ══════════════════════════════════════════════════════════════════════════════
cells.append(md(
    "---\n"
    "## Section 2 — Raw Dataset Shapes (Before Cleaning)\n\n"
    "The nine datasets vary enormously in scale. The UCDP Georeferenced Event Dataset "
    "(GED) alone has 385,918 rows (one per geocoded conflict event), while the UCDP "
    "Battle-Related Deaths dataset has just 1,586 rows (one per conflict-year dyad). "
    "A log scale is necessary to show all sources on the same axis.\n\n"
    "The colour coding groups datasets by provider: UCDP (blue), SIPRI (orange), "
    "World Bank (green), V-Dem (purple), Correlates of War (amber). Understanding which "
    "source each column in the master panel comes from is important for interpreting "
    "coverage patterns — a CoW CINC variable will be NaN after 2016 not because of a "
    "pipeline bug, but because the source dataset stops there."
))

cells.append(code(
"""raw_counts = [
    ('UCDP ACD',       'UCDP',         2_752),
    ('UCDP GED',       'UCDP',       385_918),
    ('UCDP BRD',       'UCDP',         1_586),
    ('UCDP Dyadic',    'UCDP',         3_432),
    ('SIPRI MILEX',    'SIPRI',        8_435),
    ('SIPRI TIV',      'SIPRI',       60_789),
    ('World Bank WDI', 'World Bank',  17_195),
    ('V-Dem',          'V-Dem',       13_080),
    ('CoW CINC',       'CoW',         15_951),
]

labels    = [r[0] for r in raw_counts]
providers = [r[1] for r in raw_counts]
rows      = [r[2] for r in raw_counts]
colors    = [PROVIDER_COLORS[p] for p in providers]

fig, ax = plt.subplots(figsize=(12, 5))
bars = ax.barh(labels, rows, color=colors, edgecolor='white', linewidth=0.5)
ax.set_xscale('log')
ax.set_xlabel('Number of rows (log scale)', fontsize=12)
ax.set_title('Raw Dataset Sizes Before Cleaning', fontsize=14, fontweight='bold')

for bar, count in zip(bars, rows):
    ax.text(bar.get_width() * 1.08, bar.get_y() + bar.get_height() / 2,
            f'{count:,}', va='center', fontsize=9)

legend_patches = [
    mpatches.Patch(color=c, label=p) for p, c in PROVIDER_COLORS.items()
]
ax.legend(handles=legend_patches, loc='lower right', framealpha=0.9)
ax.set_xlim(100, 2_000_000)
fig.tight_layout()
fig.savefig(EDA_DIR / 'sec2_raw_row_counts.png', dpi=150, bbox_inches='tight')
plt.show()
print('Figure saved to', EDA_DIR / 'sec2_raw_row_counts.png')
"""
))

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — How Each Dataset Changed After Cleaning
# ══════════════════════════════════════════════════════════════════════════════
cells.append(md(
    "---\n"
    "## Section 3 — How Each Dataset Changed After Cleaning (NB-02)\n\n"
    "### Why ISO3 standardisation is necessary\n\n"
    "Nine datasets from five different providers use inconsistent country names. "
    "UCDP uses 'Syrian Arab Republic', SIPRI uses 'Syria', the World Bank uses "
    "'Syrian Arab Republic', and V-Dem uses its own three-letter codes. Without a "
    "common key, no cross-source joins are possible.\n\n"
    "The cleaning notebook (NB-02) runs every country name through an `ISO3Resolver` — "
    "a three-tier lookup that tries dataset-specific overrides first, then project-wide "
    "`GLOBAL_OVERRIDES` (handling 'USSR'→'RUS', 'Yugoslavia'→'SRB', historical "
    "parenthetical names like 'Russia (Soviet Union)'→'RUS', etc.), then pycountry "
    "exact-field lookups. Names that cannot be matched (non-state actors like 'ABSDF', "
    "pre-1870 micro-states like 'Bavaria') are dropped and logged to "
    "`_unmatched_audit.csv` for review.\n\n"
    "The table below summarises what happened to each dataset. **Note for UCDP ACD:** "
    "the row count appears to *increase* because multi-country conflict entries "
    "('India, Pakistan') are exploded into one row per country — 2,752 input rows "
    "become 2,917 after the explode, with 2,914 resolving to a valid ISO3."
))

cells.append(code(
"""cleaning = pd.DataFrame({
    'Source': [
        'UCDP ACD', 'UCDP GED', 'UCDP BRD', 'UCDP Dyadic',
        'SIPRI MILEX', 'SIPRI TIV', 'World Bank WDI', 'V-Dem', 'CoW CINC',
    ],
    'Raw rows': [2752, 385918, 1586, 3432, 8435, 60789, 17195, 13080, 15951],
    'ISO3-matched': [2914, 385918, 1536, 3279, 8362, 59897, 13035, 12787, 15166],
    'Match %': [99.9, 100.0, 96.8, 95.5, 100.0, 99.6, 100.0, 100.0, 100.0],
    'Dropped / delta': ['*+165 added', 0, 0, 0, 73, 624, 4160, 293, 785],
    'Reason': [
        '*Multi-country explode adds rows; 3 unresolvable',
        'All resolved',
        'Multi-country location_inc (e.g. India-Pakistan)',
        'Non-state actors (ABSDF, PKK, FARC) unresolvable',
        'Suppressed values + EU aggregate dropped',
        'Non-state recipients (asterisk notation)',
        'Regional aggregates (World, High income, East Asia...)',
        '214 state-transition duplicates + 79 unresolvable codes',
        'Pre-1870 German/Italian micro-states (Bavaria, Hanover...)',
    ],
})

def _match_color(val):
    if not isinstance(val, float):
        return ''
    if val < 95:
        return 'background-color: #f4cccc; color: #7f0000'
    if val < 99:
        return 'background-color: #fce8b2; color: #7f4f00'
    return 'background-color: #d9ead3; color: #1b4f19'

display(
    cleaning.set_index('Source')
    .style
    .map(_match_color, subset=['Match %'])
    .format({'Raw rows': '{:,}', 'ISO3-matched': '{:,}', 'Match %': '{:.1f}%'})
    .set_table_styles([
        {'selector': 'th', 'props': [('background', '#f0f0f0'), ('font-weight', 'bold')]},
        {'selector': 'td', 'props': [('text-align', 'left')]},
    ])
)
"""
))

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — Key Cleaning Decisions
# ══════════════════════════════════════════════════════════════════════════════
cells.append(md(
    "---\n"
    "## Section 4 — Key Cleaning Decisions\n\n"
    "Three design choices in NB-02 have a large impact on downstream analysis. "
    "Each is documented here with a concrete example so that a reviewer can "
    "understand the reasoning without reading the full cleaning code."
))

# 4a — Zero vs NaN
cells.append(code(
"""# ── 4.1  Zero vs NaN distinction ──────────────────────────────────────────────
# The wrong fill policy silently biases regression coefficients. Two mutually
# exclusive lists of columns are defined in NB-02 with explicit rationale.

print('=== Zero-fill vs NaN-preserve distinction ===\\n')

example = pd.DataFrame({
    'iso3':  ['CRI', 'CRI', 'USA', 'SOM', 'SOM'],
    'year':  [2000,  2001,  2000,  2000,  2001],
    'part_n_conflicts': [0, 0, 3, 2, 1],
    'sipri_milex_usd':  [0.0, 0.0, 640_000.0, float('nan'), float('nan')],
})

print('Example rows (CRI = Costa Rica, USA, SOM = Somalia):\\n')
display(example.set_index(['iso3', 'year']).style.highlight_null(color='#ffe0e0'))

print()
print('ZERO-FILL columns  (no record = zero events, not missing data)')
zero_cols = [
    'acd_n_conflicts   — no UCDP location record means zero conflicts at that site',
    'part_n_extraterritorial — no dyadic record means no foreign intervention',
    'ged_n_events      — no GED event means zero georeferenced events',
    'tiv_imports_total — no SIPRI TIV record means zero arms imported',
    'brd_deaths_best   — no BRD record means zero battle deaths logged',
]
for c in zero_cols:
    print(f'  [0]  {c}')

print()
print('NaN-PRESERVE columns  (no record = unobserved or suppressed, NOT zero)')
nan_cols = [
    'sipri_milex_const2024_usd — NaN = data suppressed; 0 = genuine zero (e.g. Costa Rica)',
    'wb_gdp_usd                — NaN = WDI did not report for that year',
    'vdem_v2x_polyarchy        — NaN = outside V-Dem observation window',
    'cow_cinc                  — NaN for all years > 2016 (NMC v6.0 ends there)',
]
for c in nan_cols:
    print(f'  [?]  {c}')

print()
print('Costa Rica has milex=0 (constitutional ban on standing army since 1948).')
print('Somalia has milex=NaN — SIPRI suppresses the data. Imputing 0 would be wrong.')
"""
))

# 4b — Historical state mappings
cells.append(code(
"""# ── 4.2  Historical state succession mappings ──────────────────────────────────
# The panel spans 1946-2024. Many states ceased to exist within that window.
# To include Cold War era data without creating phantom entities, each predecessor
# is mapped to a single modern successor ISO3 following principled rules documented
# in GLOBAL_OVERRIDES (src/iso3.py).

state_mappings = pd.DataFrame({
    'Historical entity': [
        'Soviet Union / USSR',
        'Yugoslavia / SFR Yugoslavia',
        'Czechoslovakia',
        'West Germany + East Germany',
        'North Yemen + South Yemen',
        'North Vietnam + South Vietnam',
    ],
    'ISO3': ['RUS', 'SRB', 'CZE', 'DEU', 'YEM', 'VNM'],
    'Modern name': [
        'Russia', 'Serbia', 'Czech Republic',
        'Germany', 'Yemen', 'Vietnam',
    ],
    'Treatment': [
        'UN-seat successor; nuclear weapons succession (1991)',
        'UN-seat successor by Badinter Commission (1992)',
        'Larger economy/population; Slovakia coded as SVK separately',
        'Reunification 1990: milper/milex/CINC summed; GDP summed',
        'Unification 1990: predecessors merged into single YEM entity',
        'Reunification 1975: predecessors merged into unified VNM',
    ],
    'Cold-War years affected': [
        '1946-1991 (45 yrs)', '1946-1991 (45 yrs)',
        '1946-1992 (46 yrs)', '1946-1990 (44 yrs)',
        '1967-1990 (23 yrs)', '1946-1975 (29 yrs)',
    ],
})

print('Historical state succession mappings used in GLOBAL_OVERRIDES:\\n')
display(state_mappings.set_index('Historical entity').style.set_table_styles([
    {'selector': 'th', 'props': [('background', '#f0f0f0'), ('font-weight', 'bold')]},
    {'selector': 'td', 'props': [('text-align', 'left'), ('white-space', 'normal')]},
]))
print()
print('Why this matters for a 1946-2024 panel:')
print('  Without these mappings, the Soviet Union would have 45 years of missing data')
print('  for every variable, and the panel would systematically undercount Cold-War-era')
print('  conflict participation by Russia, military spending by Germany, etc.')
"""
))

# 4c — WDI pie
cells.append(code(
"""# ── 4.3  WDI regional aggregate drop ──────────────────────────────────────────
# The World Bank WDI download bundles sovereign-state rows with 64 regional
# and income-group aggregates ("World", "High income", "East Asia & Pacific" etc.).
# Aggregates fail ISO3 resolution and are automatically excluded — they have no
# conflict history, no democracy score, and no military spending equivalent.

sovereign  = 13_035
aggregates = 4_160
total_wdi  = sovereign + aggregates

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Left: pie chart
axes[0].pie(
    [sovereign, aggregates],
    labels=[
        f'Sovereign states\\n{sovereign:,} rows ({100*sovereign/total_wdi:.1f}%)',
        f'Regional aggregates\\n{aggregates:,} rows ({100*aggregates/total_wdi:.1f}%)',
    ],
    colors=['#4CAF50', '#EF9A9A'],
    startangle=90,
    wedgeprops={'edgecolor': 'white', 'linewidth': 2},
    textprops={'fontsize': 11},
)
axes[0].set_title('World Bank WDI: Raw Row Composition', fontsize=12, fontweight='bold')

# Right: example aggregate names that were dropped
agg_names = [
    'World', 'High income', 'East Asia & Pacific',
    'OECD members', 'Latin America & Caribbean',
    'Sub-Saharan Africa', 'Europe & Central Asia',
    'Low income',
]
axes[1].barh(agg_names, [65]*8, color='#EF9A9A', edgecolor='white', linewidth=0.5)
axes[1].set_xlabel('Rows in raw WDI (one per year: 65 years each)', fontsize=10)
axes[1].set_title('Sample Dropped Aggregate Groups', fontsize=12, fontweight='bold')
axes[1].set_xlim(0, 85)
for i in range(len(agg_names)):
    axes[1].text(66, i, '65', va='center', fontsize=9)

fig.suptitle(
    'Why 4,160 of 17,195 WDI rows were dropped: regional aggregates, not sovereign states',
    fontsize=11, y=1.01,
)
fig.tight_layout()
fig.savefig(EDA_DIR / 'sec4_wdi_aggregate_drop.png', dpi=150, bbox_inches='tight')
plt.show()
print('Figure saved to', EDA_DIR / 'sec4_wdi_aggregate_drop.png')
"""
))

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — Master Panel Overview
# ══════════════════════════════════════════════════════════════════════════════
cells.append(md(
    "---\n"
    "## Section 5 — Master Panel Overview\n\n"
    "After all cleaning and merging, the result is a **balanced panel** of "
    "192 countries × 79 years (1946–2024) = 15,168 country-year rows. Every "
    "(iso3, year) combination exists — countries with zero conflict events appear "
    "explicitly with zero counts rather than being absent from the data. This matters "
    "for regression: treating absent rows as missing data would bias conflict-frequency "
    "estimates upward (the zeros are just as informative as the positive counts).\n\n"
    "The panel has 56 columns grouped by source. Coverage is uneven: UCDP conflict "
    "variables and V-Dem democracy scores span 1946–2024 (or 1989–2024 for GED), "
    "while World Bank GDP data starts in 1960 and CoW CINC ends in 2016. These gaps "
    "are structural limitations of the source data, not pipeline errors."
))

# 5a — Load master panel + column groups
cells.append(code(
"""master = _load('master_panel.parquet')
if master is None:
    raise RuntimeError('master_panel.parquet not found — run NB03 first.')

print(f'\\nMaster panel: {master.shape}')
print(f'Countries:    {master["iso3"].nunique()} unique ISO3 codes')
print(f'Years:        {int(master["year"].min())}-{int(master["year"].max())} ({master["year"].nunique()} years)')
print(f'Balanced:     {master["iso3"].nunique()} x {master["year"].nunique()} = {len(master):,} rows')
print()

col_groups = {
    'Panel spine':         ['iso3', 'year', 'region'],
    'UCDP ACD (location)': [c for c in master.columns if c.startswith('acd_')],
    'UCDP participation':  [c for c in master.columns if c.startswith('part_')],
    'UCDP BRD (deaths)':   [c for c in master.columns if c.startswith('brd_')],
    'UCDP GED (events)':   [c for c in master.columns if c.startswith('ged_')],
    'SIPRI MILEX':         [c for c in master.columns if 'milex' in c and not c.startswith('log')],
    'SIPRI TIV':           [c for c in master.columns if c.startswith('tiv_')],
    'World Bank WDI':      [c for c in master.columns if c.startswith('wb_')],
    'V-Dem':               [c for c in master.columns if c.startswith('vdem_')],
    'CoW CINC':            [c for c in master.columns if c.startswith('cow_')],
    'Derived':             [c for c in master.columns if c.startswith('log_') or
                            c in ('war_minor_ratio', 'milex_pct_gdp', 'extraterritorial_share',
                                  'tiv_imports_5yr_sum', 'milex_5yr_mean', 'has_military',
                                  'era_cold_war', 'era_post_cw', 'era_post_911')],
}

for group, cols in col_groups.items():
    existing = [c for c in cols if c in master.columns]
    if existing:
        cols_str = ', '.join(existing)
        print(f'{group:>28}  ({len(existing):>2} cols): {cols_str}')
"""
))

# 5b — Region distribution
cells.append(code(
"""# Region distribution is hardcoded from the master panel region value_counts,
# confirmed by the NB03 Section 5 output.
region_counts = pd.Series({
    'Africa':      3871,
    'Europe':      3239,
    'Americas':    2528,
    'Asia':        1975,
    'Middle East': 1580,
    'Oceania':     1027,
    'Post-Soviet':  948,
}, name='Country-year rows')

fig, ax = plt.subplots(figsize=(12, 5))
bar_colors = [REGION_PAL.get(r, '#BDC3C7') for r in region_counts.index]
bars = ax.bar(region_counts.index, region_counts.values,
              color=bar_colors, edgecolor='white', linewidth=0.8)

for bar in bars:
    ax.text(bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 40,
            f'{int(bar.get_height()):,}',
            ha='center', va='bottom', fontsize=10)

ax.set_ylabel('Country-year rows', fontsize=12)
ax.set_title(
    'Master Panel: Country-Year Distribution by Region\\n'
    '(192 countries x 79 years = 15,168 rows total)',
    fontsize=13, fontweight='bold',
)
ax.set_ylim(0, region_counts.max() * 1.14)
fig.tight_layout()
fig.savefig(EDA_DIR / 'sec5_region_distribution.png', dpi=150, bbox_inches='tight')
plt.show()
print('Figure saved to', EDA_DIR / 'sec5_region_distribution.png')
"""
))

# 5c — Panel coverage line chart
cells.append(code(
"""# ── Panel Coverage by Variable Over Time ─────────────────────────────────────
# The balance report CSV (from NB03) records how many of the 192 countries have
# non-null values for each key variable in each year. This reveals structural
# gaps: World Bank GDP starts in 1960, CoW CINC ends in 2016.

KEY_VARS = [
    'sipri_milex_const2024_usd',
    'tiv_imports_total',
    'wb_gdp_usd',
    'vdem_v2x_polyarchy',
    'cow_cinc',
    'part_n_conflicts',
]

VAR_LABELS = {
    'sipri_milex_const2024_usd': 'SIPRI MILEX',
    'tiv_imports_total':         'SIPRI TIV imports',
    'wb_gdp_usd':                'WB GDP',
    'vdem_v2x_polyarchy':        'V-Dem polyarchy',
    'cow_cinc':                  'CoW CINC (ends 2016)',
    'part_n_conflicts':          'UCDP participation (events)',
}

VAR_STYLES = {
    'cow_cinc': '--',
}

try:
    balance = pd.read_csv(CLEAN_DIR / '_panel_balance_report.csv', index_col='year')
    balance.index = balance.index.astype(int)
    coverage_pct = (balance[KEY_VARS] / 192 * 100).clip(upper=100)

    fig, ax = plt.subplots(figsize=(14, 6))
    for col in KEY_VARS:
        if col in coverage_pct.columns:
            ax.plot(
                coverage_pct.index,
                coverage_pct[col],
                label=VAR_LABELS[col],
                linewidth=2.2,
                linestyle=VAR_STYLES.get(col, '-'),
            )

    ax.axvline(2016, color='#888', linestyle=':', linewidth=1.5,
               label='CoW CINC cutoff (2016)')
    ax.axvline(1989, color='#aaddff', linestyle=':', linewidth=1.5,
               label='GED / RQ analysis scope start (1989)')

    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('% of 192 countries with non-null data', fontsize=12)
    ax.set_title('Panel Coverage by Variable Over Time', fontsize=14, fontweight='bold')
    ax.legend(loc='lower right', framealpha=0.9, fontsize=10)
    ax.set_ylim(0, 112)
    ax.set_xlim(1946, 2024)

    fig.tight_layout()
    fig.savefig(EDA_DIR / 'sec5_panel_coverage.png', dpi=150, bbox_inches='tight')
    plt.show()
    print('Figure saved to', EDA_DIR / 'sec5_panel_coverage.png')
except Exception as exc:
    print(f'Could not plot coverage: {exc}')
    print('Ensure _panel_balance_report.csv exists in data/clean/')
"""
))

# 5d — Summary stat
cells.append(code(
"""# ── Effective regression sample ───────────────────────────────────────────────
n_rq1 = master[
    master['wb_gdp_usd'].notna() &
    master['sipri_milex_const2024_usd'].notna() &
    master['vdem_v2x_polyarchy'].notna() &
    (master['year'] >= 1989)
].shape[0]

n_full_cov = 82  # countries with non-zero rows in all 9 sources (from NB02 coverage matrix)

print('=' * 56)
print('  MASTER PANEL SUMMARY STATISTICS')
print('=' * 56)
print(f'  Total rows (balanced grid): {len(master):,}')
print(f'  Countries in universe:      {master["iso3"].nunique()}')
print(f'  Years covered:              {int(master["year"].min())}-{int(master["year"].max())} ({master["year"].nunique()} years)')
print(f'  Total columns:              {master.shape[1]}')
print()
print(f'  Countries with full 9-source coverage:  {n_full_cov} of 192')
print()
print(f'  Effective RQ1 regression sample')
print(f'  (GDP + MILEX + V-Dem all non-null, 1989-2024):')
print(f'    {n_rq1:,} country-years')
print()
print('  Only 82 of 192 countries have full coverage across all 9 sources.')
print('  This is the effective analytical N for main regressions.')
print('  The full 192-country spine ensures zero-conflict years appear')
print('  explicitly rather than as missing rows -- critical for unbiased')
print('  conflict-frequency estimates.')
print('=' * 56)
"""
))

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 6 — Sub-Panels
# ══════════════════════════════════════════════════════════════════════════════
cells.append(md(
    "---\n"
    "## Section 6 — Sub-Panels Built for Each Research Question\n\n"
    "NB-03 produces six output parquets from the master panel, each scoped to the "
    "analytical requirements of one research question. Using separate sub-panels rather "
    "than subsetting inside each modelling notebook avoids accidental scope drift and "
    "makes the row-count logic auditable.\n\n"
    "The critical design choice is the **attribution policy** for conflict events:\n\n"
    "- `acd_*` columns attribute conflict to the **location** (where fighting happened) "
    "— used for the location panel and BRD deaths.\n"
    "- `part_*` columns attribute conflict to the **participant** (who was involved) "
    "— used for RQ1 regressions. A country that sends troops abroad shows "
    "`part_n_extraterritorial > 0`.\n\n"
    "These are different questions. A country can appear in RQ1 as an active participant "
    "in many foreign conflicts while having zero conflicts on its own territory."
))

cells.append(code(
"""subpanels = pd.DataFrame({
    'File': [
        'master_panel.parquet',
        'location_panel.parquet',
        'rq1_panel.parquet',
        'rq2_outcome_monthly.parquet',
        'rq2_treatment_annual.parquet',
        'rq3_cross_section.parquet',
    ],
    'Shape': [
        '15,168 x 56', '15,168 x 9', '6,912 x 18',
        '82,944 x 4',  '6,912 x 13', '192 x 10',
    ],
    'Scope': [
        '192 iso3 x 79 years (1946-2024)',
        '192 iso3 x 79 years (1946-2024)',
        '192 iso3 x 36 years (1989-2024)',
        '192 iso3 x 432 months (1989-01 to 2024-12)',
        '192 iso3 x 36 years (1989-2024)',
        '192 countries (averages over 1989-2024)',
    ],
    'Purpose': [
        'Full analytical panel -- all 9 sources merged',
        'Robustness comparison: location-based vs participation-based attribution',
        'RQ1 panel regression: conflict type vs military spending / arms imports',
        'RQ2 outcome: monthly GED event counts for lead-lag analysis',
        'RQ2 treatment: annual TIV imports by weapon category',
        'RQ3 clustering: country-level aggregates for dimensionality reduction',
    ],
})

display(subpanels.set_index('File').style.set_table_styles([
    {'selector': 'th', 'props': [('background', '#f0f0f0'), ('font-weight', 'bold')]},
    {'selector': 'td', 'props': [('text-align', 'left'), ('white-space', 'normal')]},
]))
"""
))

# 6b — RQ3 scatter
cells.append(code(
"""# ── RQ3 Preview: Military Spending vs Conflict Participation ──────────────────
# Load the cross-section panel that RQ3 clustering will operate on.
# The scatter gives an intuitive preview: high-spending states in the top right,
# peaceful small states in the bottom left.

rq3 = _load('rq3_cross_section.parquet')
if rq3 is not None:
    rq3 = rq3.copy()
    rq3['log_milex'] = np.log1p(rq3['mean_milex'].fillna(0))

    fig, ax = plt.subplots(figsize=(12, 5))

    for region, grp in rq3.groupby('region'):
        color = REGION_PAL.get(region, '#BDC3C7')
        ax.scatter(
            grp['log_milex'], grp['total_conflicts'],
            c=color, label=region,
            alpha=0.75, s=45,
            edgecolors='white', linewidth=0.5,
        )

    # Label the top 20 countries by total conflict participations
    top20 = rq3.nlargest(20, 'total_conflicts')
    for _, row in top20.iterrows():
        ax.annotate(
            row['iso3'],
            xy=(row['log_milex'], row['total_conflicts']),
            xytext=(4, 3), textcoords='offset points',
            fontsize=7.5, fontweight='bold', alpha=0.9,
        )

    ax.set_xlabel('log(1 + Mean Military Spending USD, 1989-2024)', fontsize=11)
    ax.set_ylabel('Total conflict participations (sum 1989-2024)', fontsize=11)
    ax.set_title(
        'RQ3 Preview: Military Spending vs Conflict Participation\\n'
        '(colour = region; ISO3 labels on top 20 countries by conflict count)',
        fontsize=12, fontweight='bold',
    )
    ax.legend(loc='upper left', framealpha=0.9, fontsize=9, ncol=2)
    fig.tight_layout()
    fig.savefig(EDA_DIR / 'sec6_rq3_scatter.png', dpi=150, bbox_inches='tight')
    plt.show()
    print('Figure saved to', EDA_DIR / 'sec6_rq3_scatter.png')
else:
    print('rq3_cross_section.parquet not found -- run NB03 first.')
"""
))

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 7 — Known Gaps and Limitations
# ══════════════════════════════════════════════════════════════════════════════
cells.append(md(
    "---\n"
    "## Section 7 — Known Data Gaps and Limitations\n\n"
    "No dataset covering 192 countries and 79 years is complete. The gaps below are "
    "structural — they arise from political decisions by data providers (World Bank "
    "excluding Taiwan), reporting lags (UCDP coding rules), or dataset version cutoffs "
    "(CoW CINC ending at 2016). Each gap is documented here so that a reviewer can "
    "judge whether it affects the specific analysis they are scrutinising.\n\n"
    "The most analytically significant gaps are:\n"
    "- **CoW CINC cutoff (2016):** military capability cannot be controlled for "
    "post-2016, limiting some robustness checks.\n"
    "- **Taiwan WDI exclusion:** Taiwan is included in the participation panel (it "
    "appears in UCDP and SIPRI data) but cannot be included in GDP-controlled "
    "regressions."
))

cells.append(code(
"""gaps = pd.DataFrame({
    'Country / Variable': [
        'Taiwan (TWN)',
        'Palestine (PSE)',
        'Kosovo (XKX)',
        'South Sudan (SSD)',
        'CoW CINC (all countries)',
        'Multi-country BRD rows',
    ],
    'Gap': [
        '0 WDI rows',
        'WDI data from 1994 only',
        'Pre-2008 rows attributed to SRB',
        'Pre-2011 rows attributed to SDN',
        'NaN for all years > 2016',
        '~50 conflict dyads span 2+ countries',
    ],
    'Root cause': [
        'World Bank excludes Taiwan for political reasons (PRC position in UN)',
        'Palestinian Authority data begins 1994; no pre-Oslo Accords records',
        'Kosovo declared independence Feb 2008; prior records under Serbia (SRB)',
        'South Sudan gained independence Jul 2011; prior records under Sudan (SDN)',
        'NMC v6.0 dataset ends at 2016; no subsequent v7.0 release as of 2025',
        'UCDP BRD location_inc lists multiple countries for cross-border dyads',
    ],
    'Impact on analysis': [
        'TWN in participation panel but excluded from GDP-controlled regressions',
        'PSE included from 1994; pre-1994 years have NaN GDP, zero-fill conflict counts',
        'XKX post-2008 correctly attributed; pre-2008 merged with SRB history',
        'SSD post-2011 correctly attributed; pre-2011 merged with SDN history',
        'cow_cinc NaN-preserved for 2017-2024; RQ post-2016 regressions omit CINC',
        'BRD deaths attributed to first listed country; ~50 dyads have partial coverage',
    ],
})

display(gaps.set_index('Country / Variable').style.set_table_styles([
    {'selector': 'th', 'props': [
        ('background', '#f0f0f0'), ('font-weight', 'bold'),
    ]},
    {'selector': 'td', 'props': [
        ('text-align', 'left'), ('white-space', 'normal'), ('font-size', '11px'),
    ]},
]))
"""
))

# ══════════════════════════════════════════════════════════════════════════════
# FINAL SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
cells.append(md(
    "---\n"
    "## What This EDA Established\n\n"
    "This notebook documented nine datasets from five providers, spanning 1946–2024, "
    "cleaned and merged into a balanced panel of **192 countries × 79 years "
    "(15,168 rows)**. Key findings:\n\n"
    "1. **Scale heterogeneity** — datasets range from 1,586 rows (UCDP BRD) to "
    "385,918 rows (UCDP GED). A log scale is always needed to compare sources.\n\n"
    "2. **ISO3 resolution** — all nine sources share a common `iso3` key after the "
    "resolver normalised ~30 historical state names (USSR→RUS, etc.) and stripped "
    "UCDP parenthetical suffixes (e.g. 'Russia (Soviet Union)'→'RUS'). Unresolvable "
    "names (non-state actors, pre-1870 micro-states) were dropped and logged.\n\n"
    "3. **Fill policy matters** — UCDP event counts are zero-filled (no record = zero "
    "events), while SIPRI MILEX and WDI GDP are NaN-preserved (no record = unobserved, "
    "not zero). Confusing these two silently biases regressions.\n\n"
    "4. **Coverage gaps are structural** — CoW CINC stops in 2016, Taiwan is excluded "
    "from WDI, and multi-country BRD rows cannot be attributed to a single country. "
    "All are source-data constraints, not pipeline errors.\n\n"
    "5. **Effective N** — only 82 of 192 countries have full 9-source coverage. "
    "The effective RQ1 regression sample (GDP + MILEX + V-Dem non-null, 1989–2024) "
    "is approximately **5,007 country-years**.\n\n"
    "### What Comes Next\n\n"
    "| Notebook | Task |\n"
    "|----------|------|\n"
    "| **NB-04** | MTS (Military Threat Signal) construction — composite indicator "
    "from MILEX, TIV, CINC and growth rates |\n"
    "| **NB-05** | RQ1 regressions — panel fixed-effects models of conflict type on MTS |\n"
    "| **NB-06** | RQ2 lead-lag analysis — time-series tests of arms transfers → "
    "conflict events |\n"
    "| **NB-07** | RQ3 clustering — k-means + PCA on the cross-section panel |\n"
    "| **NB-08** | Results synthesis and report generation |"
))

# ══════════════════════════════════════════════════════════════════════════════
# COMPILE AND SAVE
# ══════════════════════════════════════════════════════════════════════════════
nb.cells = cells

out_path = Path('notebooks/00_eda_overview.ipynb')
out_path.parent.mkdir(parents=True, exist_ok=True)
with open(out_path, 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print(f'Wrote {out_path} with {len(cells)} cells.')
