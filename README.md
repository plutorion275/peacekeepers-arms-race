# The Peacekeepers' Arms Race

**Testing the Stability–Instability Paradox with cross-national panel data, 1946–2024**

A quantitative panel-data study asking whether higher military capability shifts conflict composition toward low-intensity forms (the *substitution hypothesis*) or amplifies all conflict types (*amplification*). Originally a course project for PMDS507L (Big Data Analytics), now on a journal-submission track.

**Author:** T Sam Davis (25MDT1140)

---

## Research questions

| RQ | Question | Method |
|----|----------|--------|
| RQ1 | Does military technology predict conflict-type composition? | Panel fixed-effects regression (`linearmodels.PanelOLS`) |
| RQ2 | Do weapon-class acquisitions lead conflict onset/intensity? | Dumitrescu–Hurlin panel Granger causality, lead-lag analysis |
| RQ3 | Do countries cluster into distinct conflict-capability archetypes? | K-Means clustering with bootstrap stability and out-of-sample validation |

## Headline findings

- **RQ1:** Substitution hypothesis is **not supported**. Higher Military Technology Score (MTS) predicts significantly *more* conflict of both types (amplification), most strongly for battle-death intensity (β≈+2.03, p<0.001).
- **RQ2:** The standard Dumitrescu-Hurlin shuffle-null test is mis-specified for these panels (destroys negative serial structure in arms-transfer data → inflated type-I error, 0.32–0.48 against a 5% nominal rate). Under the correct circular-shift null, only 1 of 8 nominally significant cells survives per-cell permutation, and none survive BH correction.
- **RQ3:** Four archetypes identified — Defensive Deterrent, Safe Hegemon, Inert Non-Combatant, Armed Instabilizer — with out-of-sample ANOVA validating predictive power (F=33.575, p<0.0001). Bootstrap Jaccard stability is below the conventional 0.75 threshold, but that threshold is miscalibrated for bootstrap-with-replacement at n=157 (theoretical ceiling ≈0.53 per Ben-Hur et al. 2002); against the correct 0.50 threshold, clusters are stable.

Full detail and diagnostics are in `reports/` and the notebook HTML exports.

## Data sources

| Source | Content | Granularity |
|---|---|---|
| [SIPRI](https://www.sipri.org/databases) MILEX | Military expenditure | Country-year |
| [SIPRI](https://www.sipri.org/databases/armstransfers) TIV Transfer Register | Arms transfers (deal-level deliveries) | Deal-level → country-year |
| [UCDP](https://ucdp.uu.se/downloads/) ACD / GED / BRD / Dyadic | Armed conflict onset, events, battle deaths, dyads | Conflict-year / event / dyad-year |
| [World Bank WDI](https://databank.worldbank.org/source/world-development-indicators) | Economic controls | Country-year |
| [V-Dem](https://www.v-dem.net/data/the-v-dem-dataset/) Core v16 | Institutional/regime controls | Country-year |
| [Correlates of War](https://correlatesofwar.org/data-sets/national-material-capabilities/) NMC v6.0 (CINC) | Material capabilities | State-year |
| [Correlates of War](https://correlatesofwar.org/data-sets/formal-alliances/) Formal Alliances v4.1 | Alliance ties | Dyad/state-year |

Coverage: 192 countries, 1946–2024 (event-level conflict data from 1989 onward). **Raw data is not redistributed in this repository** — each source has its own licensing/attribution terms; see `data/README.md` for direct download links and instructions to reproduce `data/raw/`.

## Repository structure

```
peacekeepers_arms_race/
├── data/
│   ├── raw/              # Original downloads (gitignored — see data/README.md)
│   ├── checkpoints/      # Inter-notebook handoffs (parquet)
│   └── clean/            # Analysis-ready panel datasets
├── notebooks/
│   ├── 01_data_acquisition.ipynb
│   ├── 02_cleaning_iso3.ipynb
│   ├── 03_panel_construction.ipynb
│   ├── 04_mts_construction.ipynb
│   ├── 05_rq1_panel_regression.ipynb
│   ├── 06_rq2_leadlag.ipynb
│   ├── 07_rq3_clustering.ipynb
│   ├── 08_visualization_summary.ipynb
│   ├── 09_secondary_findings.ipynb
│   ├── 10_alliance_grouped_analysis.ipynb
│   ├── 11_mechanisms.ipynb
│   ├── 12_rq2_power_analysis.ipynb
│   ├── 13_forecasting_benchmark.ipynb
│   └── 14_naive_vs_rigorous_comparison.ipynb
├── src/                  # Shared modules imported by all notebooks
│   ├── config.py
│   ├── iso3.py
│   ├── io_utils.py
│   ├── panels.py
│   ├── mts.py
│   ├── stats_panel.py
│   └── viz.py
├── figures/               # Generated plots, by research question
├── tables/                 # Regression/output tables (CSV + LaTeX)
├── reports/                # Writeups and paper drafts
├── requirements.txt
├── LICENSE
└── README.md
```

Notebooks are numbered for execution order; each consumes the previous notebook's parquet checkpoint from `data/checkpoints/` and is independently re-runnable via `jupyter nbconvert --execute`.

## Setup

```bash
git clone https://github.com/<your-username>/peacekeepers-arms-race.git
cd peacekeepers-arms-race
python -m venv .venv
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
```

Then follow `data/README.md` to download raw source files (SIPRI, UCDP, World Bank, V-Dem, CoW) into `data/raw/`, and run notebooks 01→14 in order.

## Key methodological choices

- **MTS construction:** the primary specification (`mts_pca_3feat`) is a three-feature PCA that drops CoW `milper` to extend coverage to 2024 (CoW CINC itself truncates at 2016).
- **RQ2 null model:** a circular-shift null is used in place of the conventional shuffle null, since shuffling destroys the negative serial structure inherent to arms-transfer time series.
- **Panel balance:** a balanced (iso3 × year) grid is used with NaN-tolerant estimators rather than truncating the sample to the shortest-covered source.
- **Cluster stability threshold:** recalibrated to 0.50 (not the conventional 0.75) to reflect the theoretical ceiling for bootstrap-with-replacement resampling at this sample size.

## Reproducibility notes

- Inter-notebook handoffs use Parquet, not Pickle, to avoid breakage across pandas versions.
- Each notebook contains PASS/FAIL sanity-check cells and, where relevant, a regression guard against frozen reference values.
- Custom implementations are used where no maintained Python package exists (e.g., a numpy-based Dumitrescu-Hurlin test, reducing runtime from 60+ minutes to 1–2 minutes versus a naive approach).

## License

Code in this repository is released under the [MIT License](LICENSE) (or update to your preferred license). Third-party data retains the license terms of its original provider — see `data/README.md`.

## Citation

If you use this code or findings, please cite:

```
Davis, T. S. (2026). The Peacekeepers' Arms Race: Testing the Stability-Instability
Paradox in Cross-National Conflict Data, 1946-2024. [Working paper].
```
