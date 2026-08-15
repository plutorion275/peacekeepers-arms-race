# Citation Map — `draft.md`

Every substantive numeric claim in `draft.md`, traced to its exact source. Built as a submission-readiness check and as viva/defense prep material: every number in the paper should be one click from its source. Notebook numbers (NB05, NB12, etc.) are intentionally used here — they are the pointer the manuscript itself deliberately omits.

Format: **"claim as it appears in the paper"** → source file, column/filter.

---

## Abstract / Introduction

- **"192-country panel"** → `data/clean/rq1_panel.parquet`, `iso3.nunique()` = 192 (the RQ1/RQ2 merged panel; NB05 source panel). Not the RQ3 clustering sample: `tables/nb07/section5_cluster_assignments.csv` shows the archetype clustering itself draws on 157 countries (`iso3.nunique()` = 157) across 4 epochs (`epoch.nunique()` = 4), yielding 610 country-epoch rows (`len(df)` = 610); the 610 figure in `section5_centroids_annotated.csv`'s `n_countries` sum (85+118+282+125) is a count of country-epoch assignments, not of distinct countries, and should not be read as evidence of a 192-country cross-section.
- **"1989–2024"** → `data/clean/rq1_panel.parquet`, `year.min()`/`year.max()` = 1989 / 2024.
- **"nine open ... datasets from five independent providers"** → `reports/draft.md` Section 3.1 table itself (9 rows: SIPRI MILEX, SIPRI TIV, UCDP ACD, UCDP GED, UCDP Dyadic, UCDP BRD, V-Dem, WDI, CoW CINC+Alliances), sourced from BDA_Project_Plan.docx "Datasets" table and `data/README.md` (5 providers: SIPRI, UCDP, V-Dem, World Bank, CoW).
- **"eight of twelve pre-specified weapon-outcome pairs"** → `tables/nb06/section3_dumitrescu_hurlin.csv`, filtered `lag==1`, count of `p < 0.05` = 8 of 12 rows.
- **"zero pairs survive"** → `tables/nb12/section2f_circular_shift.csv`, count of `q_bh_cs < 0.05` = 0 of 12.
- **"four data-driven archetypes"** → `tables/nb07/section5_centroids_annotated.csv`, row count = 4 (index = `archetype`).
- **"only half are statistically stable"** → `tables/nb07/section3_bootstrap_summary.csv`, `mean_jaccard >= 0.50` (corrected threshold, reasoning in Section 4.3) → 2 of 4 rows True.

## Section 3 — Data and Measures

- **"192 countries"** → `data/clean/rq1_panel.parquet` and `data/clean/rq3_cross_section.parquet`, `iso3.nunique()` = 192 (both).
- **"1989–2024" effective window** → `data/clean/rq1_panel.parquet`, `year` range; reasoning (GED/BRD start 1989, V-Dem/TIV coverage gaps pre-1989) → `notebooks/08_visualization_summary.ipynb`, Section 6 limitations bullet (itself derived from source dataset coverage documented in `data/README.md`).
- **"1946" nominal UCDP ACD start** → `data/clean/master_panel.parquet`, `year.min()` = 1946; also BDA_Project_Plan.docx dataset table ("UCDP/PRIO Armed Conflict Dataset ... 1946–present").
- **"6,912 country-year observations"** → `data/clean/rq1_panel.parquet`, `.shape` = (6912, 23).
- **"4,896 country-years"** (count-based outcomes) → `tables/nb05/section2_primary_regression.csv`, `N` column, rows `part_n_war`/`part_n_minor`/`part_n_extraterritorial`/`log_brd` = 4896.
- **"1,846"** (ratio-based outcomes) → `tables/nb05/section2_primary_regression.csv`, `N` column, rows `war_minor_ratio`/`extraterritorial_share` = 1846.
- **UCDP data collection began in 1979, formalised mid-1980s** → BDA_Project_Plan.docx, "Other Information / On the UCDP" paragraph.
- **Six data-quality bugs** (Iceland/ISL, SIPRI export/import, UCDP coalition coding, mean-vs-sum, TIV zero/missing, NB06 "trustworthy" post-save bug) → `tables/nb09/bug_catalog.csv`, all 6 rows (`Bug`, `Caught Via`, `Consequence if Missed` columns).
- **"2003 Iraq War" spot-check (UCDP coalition-coding bug)** → `tables/nb09/bug_catalog.csv`, row 3 ("UCDP folds multi-state coalitions..."), `Caught Via` column (exact source text: "NB02 Iraq-2003 spot-check (USA/UK/Australia)").
- **"roughly 5,400 country-years"** (TIV zero/missing bug) → `tables/nb09/bug_catalog.csv`, row 5 "Consequence if Missed" column (exact source text: "~5,397 country-years").

## Section 4 — Empirical Strategy

- **"192 countries"**, **model equation terms** (α_i, γ_t, X_{i,t}) → BDA_Project_Plan.docx, "RQ1 — Panel Fixed-Effects Regression" paragraph (model equation given verbatim in source document).
- **"four weapon classes"** (aircraft/unmanned, missiles, naval, ground) → `src/rq2_panel.py`, `WEAPON_CLASSES` dict keys (AIR, MISSILES, NAVAL, GROUND); also BDA_Project_Plan.docx "RQ2" paragraph.
- **"lags of 0–36 months"** → BDA_Project_Plan.docx, "RQ2 — Cross-Correlation and Panel Granger Causality" paragraph.
- **"lag 1 ... only lag with positive signal; lags 2–3 uninformative"** → `tables/nb06/section3_dumitrescu_hurlin.csv`, compare mean `Z` by `lag` (lag 1 positive/mixed, lags 2–3 negative — the negative-Z artifact documented in `notebooks/12_rq2_power_analysis.ipynb` Section 3).
- **"twelve pre-specified weapon-by-outcome cells"** → `src/rq2_panel.py`, `WEAPON_CLASSES` (4) × `OUTCOMES` (3) = 12; confirmed row count in `tables/nb12/section2f_circular_shift.csv` (12 rows).
- **negative lag-1 autocorrelation ("−0.33 observed")** → `tables/nb12/section2f_null_comparison.csv`, `metric == "acf_observed"`, `value` = −0.3286.
- **within-country shuffle destroys structure ("−0.02 shuffled")** → `tables/nb12/section2f_null_comparison.csv`, `metric == "acf_shuffled"`, `value` = −0.0232.
- **"2,000 circular-shift permutations"** → `tables/nb12/section2f_null_comparison.csv`, `metric == "n_perm"`, `value` = 2000; row count of `data/interim/nb12_perm_circshift_2000.parquet` = 24,000 = 2000 × 12 cells.
- **Benjamini-Hochberg FDR across 12 cells** → `tables/nb12/section2f_circular_shift.csv`, `q_bh_cs` column (BH-adjusted q-values, 12 rows).
- **"K-Means and Ward ... k from 2 to 10"**, **"2019–2024" OOS holdout**, **"100 times" bootstrap resampling** → BDA_Project_Plan.docx, "RQ3 — Clustering with Stability Validation" paragraph.
- **k = 2–8 tested range (silhouette peak)** → `tables/nb07/section2_k_selection.csv`, `k` column range (2–8, 7 rows).
- **"0.75" conventional threshold / "0.50" corrected threshold** → Ben-Hur, Elisseeff & Guyon (2002) reasoning, restated in `notebooks/08_visualization_summary.ipynb` Section 1 (`JACCARD_THRESHOLD_CORRECTED = 0.50` comment) and `notebooks/09_secondary_findings.ipynb` Section 2.4.

## Section 5.1 — RQ1 Results

- **part_n_war primary: β=0.30, SE=0.14, p=.037, N=4,896** → `tables/nb05/section2_primary_regression.csv`, row `Outcome=="part_n_war"`, columns `β (MTS)`, `SE`, `p`, `N`.
- **part_n_minor primary: β=0.54, SE=0.17, p=.002, N=4,896** → `tables/nb05/section2_primary_regression.csv`, row `Outcome=="part_n_minor"`.
- **war_minor_ratio primary: β=0.23, SE=0.22, p=.294, N=1,846** → `tables/nb05/section2_primary_regression.csv`, row `Outcome=="war_minor_ratio"`.
- **part_n_extraterritorial primary: β=0.16, p=.427** → `tables/nb05/section2_primary_regression.csv`, row `Outcome=="part_n_extraterritorial"`.
- **extraterritorial_share primary: β=−0.51, p=.124** → `tables/nb05/section2_primary_regression.csv`, row `Outcome=="extraterritorial_share"`.
- **log_brd primary: β=2.03, SE=0.59, p=.001, N=4,896, R²_within=.44** → `tables/nb05/section2_primary_regression.csv`, row `Outcome=="log_brd"`, incl. `R²_within` column.
- **LOO jackknife: 193 single-country drops, β range [1.82, 2.16], all significant/positive** → `tables/nb11/section1_loo_jackknife.csv`, `len(df)`=193, `β.min()`=1.8185, `β.max()`=2.1574, `(p<0.05).all()`=True, `(β>0).all()`=True.
- **part_n_minor across specs: PCA p=.002, MILEX p=.017, TIV p=.091** → `tables/nb05/section3_robustness_all_specs.csv`, rows `Outcome=="part_n_minor"`, filtered by `MTS`.
- **part_n_minor Poisson FE p=.048** → `tables/nb05/section3b_poisson_fe.csv`, row `Outcome=="part_n_minor"`, column `p`.
- **part_n_war across specs: PCA p=.037, MILEX p=.851, TIV p=.127** → `tables/nb05/section3_robustness_all_specs.csv`, rows `Outcome=="part_n_war"`, filtered by `MTS`.
- **log_brd across specs: PCA p=.001, TIV p=.014, MILEX p=.316** → `tables/nb05/section3_robustness_all_specs.csv`, rows `Outcome=="log_brd"`, filtered by `MTS`.
- **Subperiod part_n_extraterritorial: post_cw β=−0.43, SE=0.25, p=.089, N=1,572 (1989–2001); post_911 β=0.38, SE=0.46, p=.409, N=3,324 (2002–2024)** → `tables/nb05/section4_subperiod_heterogeneity.csv`, rows `Outcome=="part_n_extraterritorial"`, filtered by `Period` (`post_cw`, `post_911`).
- **Regional decomposition: log_brd marginal β=4.95 (Africa), p<.001** → `tables/nb10/section3_region_interaction.csv`, row `Outcome=="log_brd"` & `Region=="Africa"`, columns `marginal_β`, `p`.
- **Africa leave-one-out jackknife: 34 in-sample single-country drops + 1 joint 3-country drop, β range [4.49, 5.41], all p<.05** → `tables/nb11/section2_africa_jackknife.csv`, 36 rows total (1 baseline "(none)" + 34 single drops + 1 joint drop), `in_sample==True` count = 35 (34 single + 1 joint); `africa_β.min()`=4.4868, `africa_β.max()`=5.4121, `(p<0.05).all()`=True.
- **No regime-type moderation: continuous polyarchy interaction p=.497, democracy/autocracy dummy interaction p=.687 (log_brd)** → `tables/nb11/section3_polyarchy_interaction.csv`, rows `Outcome=="log_brd"` & `quantity` contains "interaction", columns `spec`, `p` (continuous: 0.4974; dummy: 0.6867).

## Section 5.2 — RQ2 Results

- **"8 of 12 cells ... nominally significant"** → `tables/nb06/section3_dumitrescu_hurlin.csv`, filtered `lag==1`, count `p<0.05` = 8/12; cross-checked against `tables/nb12/section2b_percell_permutation.csv`, `nominal_sig` column (8 True).
- **Placebo significance rate 16%–50% at lag 1** → `tables/nb06/section4_placebo_comparison.csv`, filtered `lag==1`, `placebo_sig_rate` column, min=0.16, max=0.50.
- **GROUND→part_n_war: Z=6.42, p<.001** → `tables/nb06/section3_dumitrescu_hurlin.csv`, row `weapon=="GROUND"` & `outcome=="part_n_war"` & `lag==1`.
- **GROUND→part_n_extraterritorial: Z=4.93, p<.001** → `tables/nb06/section3_dumitrescu_hurlin.csv`, row `weapon=="GROUND"` & `outcome=="part_n_extraterritorial"` & `lag==1`.
- **MISSILES→part_n_minor: Z=3.64, p<.001** → `tables/nb06/section3_dumitrescu_hurlin.csv`, row `weapon=="MISSILES"` & `outcome=="part_n_minor"` & `lag==1`.
- **Observed ACF = −0.33** → `tables/nb12/section2f_null_comparison.csv`, `metric=="acf_observed"`, value −0.3286.
- **Shuffled ACF = −0.02** → `tables/nb12/section2f_null_comparison.csv`, `metric=="acf_shuffled"`, value −0.0232.
- **Circular-shift ACF = −0.31** → `tables/nb12/section2f_null_comparison.csv`, `metric=="acf_circular"`, value −0.3113.
- **"nominal 5 percent rate" (test's own advertised error rate)** → definitional (ALPHA=0.05 convention used throughout NB12/13/14, e.g. `notebooks/12_rq2_power_analysis.ipynb` `ALPHA = 0.05`).
- **"2,000 circular-shift permutations"** → `tables/nb12/section2f_null_comparison.csv`, `metric=="n_perm"`, value 2000.
- **"zero of twelve cells survive"** → `tables/nb12/section2f_circular_shift.csv`, count `q_bh_cs<0.05` = 0/12.
- **Per-cell rejection rate under circular-shift null: 32%–48%, 6–10x nominal** → `data/interim/nb12_perm_circshift_2000.parquet`, filtered `lag==1`, grouped by `(weapon, outcome)`, fraction of `p<0.05` per cell; min=0.316, max=0.4805 (min/max ÷ 0.05 = 6.32×–9.61×). Read-only aggregation of an already-computed NB12 cache, no new permutations run.
- **GROUND→part_n_war: p_cell_cs=.032, q_bh_cs=.390** → `tables/nb12/section2f_circular_shift.csv`, row `weapon=="GROUND"` & `outcome=="part_n_war"`, columns `p_cell_cs`, `q_bh_cs` (0.03248, 0.3898).
- **Forecast skill differential: range +0.02% (GROUND, part_n_war) to −0.06% (AIR, part_n_minor)** → `tables/nb13/section2_skill_by_cell.csv`, `skill_M3_vs_M2` column, max=0.000211 (GROUND/part_n_war), min=−0.000561 (AIR/part_n_minor).
- **Forecast origins "2005 and 2023" (yearly rolling-origin), four models (naive-zero, historical-mean, AR(1), treatment-augmented)** → `notebooks/13_rq2_forecasting_benchmark.ipynb`, Section 0 locked constants (`ORIGIN_START=2005`, `ORIGIN_END=2023`) and Section 1 model ladder (M0–M3).
- **"zero survivors" (forecast permutation)** → `tables/nb13/section3_percell_permutation.csv`, count `survives_bh==True` = 0/12.
- **"8 of 12 ... 0 of 12" (naive-vs-rigorous, DH side)** → `tables/nb14/section1_dh_naive_vs_rigorous.csv`, `naive_sig.sum()`=8, `rigorous_sig_bh.sum()`=0.

## Section 5.3 — RQ3 Results

- **Archetype names and counts: Safe Hegemon (118), Armed Instabilizer (125), Defensive Deterrent (85), Inert Non-Combatant (282)** → `tables/nb07/section5_centroids_annotated.csv`, `archetype` index and `n_countries` column.
- **Archetype centroid profiles (MTS composite mean, war-to-minor ratio mean, log_brd mean, minor-conflict mean, extraterritorial-share mean, conflict-active-pct)** → `tables/nb07/section5_centroids_annotated.csv`, columns `mts_pca_3feat_mean`, `war_minor_ratio_mean`, `log_brd_mean`, `part_n_minor_mean`, `extraterritorial_share_mean`, `conflict_active_pct`, one row per archetype. Exact values (rounded form used in `draft.md` in parentheses): Safe Hegemon `mts_pca_3feat_mean`=0.2765 (0.28), `war_minor_ratio_mean`=0.1976 (0.20), `log_brd_mean`=5.8978 (5.90); Armed Instabilizer `mts_pca_3feat_mean`=0.3010 (0.30), `part_n_minor_mean`=1.9721 (1.97), `extraterritorial_share_mean`=1.2886 (1.29); Defensive Deterrent `mts_pca_3feat_mean`=0.2627 (0.26); Inert Non-Combatant `mts_pca_3feat_mean`=0.1796 (0.18), `conflict_active_pct`=0.1000 (10 percent).
- **Silhouette peak at k=4 (silhouette=0.293), range k=2–8** → `tables/nb07/section2_k_selection.csv`, `silhouette` column, `idxmax()` row (`k`=4, `silhouette`=0.293189).
- **Gap statistic favors k=8 (gap=1.136)** → `tables/nb07/section2_k_selection.csv`, `gap` column, `idxmax()` row within tested range (`k`=8, `gap`=1.135582).
- **Ward silhouette: k=8 (0.243) vs k=4 (0.181)** → `tables/nb07/section2b_ward_vs_kmeans.csv`, `ward_silhouette` column, rows `k==8` (0.243144) and `k==4` (0.181445).
- **"0.50" corrected threshold, "0.75" conventional threshold** → Ben-Hur, Elisseeff & Guyon (2002); applied threshold value restated in `notebooks/08_visualization_summary.ipynb` Section 1 (`JACCARD_THRESHOLD_CORRECTED = 0.50`).
- **Safe Hegemon mean Jaccard = 0.58** → `tables/nb07/section3_bootstrap_summary.csv`, row `cluster==1`, `mean_jaccard` = 0.581, joined to archetype name via `section5_centroids_annotated.csv` (`cluster 1 = Safe Hegemon`).
- **Inert Non-Combatant mean Jaccard = 0.54** → `tables/nb07/section3_bootstrap_summary.csv`, row `cluster==2`, `mean_jaccard` = 0.538 (`cluster 2 = Inert Non-Combatant`).
- **Defensive Deterrent mean Jaccard = 0.46** → `tables/nb07/section3_bootstrap_summary.csv`, row `cluster==0`, `mean_jaccard` = 0.4576 (`cluster 0 = Defensive Deterrent`).
- **Armed Instabilizer mean Jaccard = 0.42** → `tables/nb07/section3_bootstrap_summary.csv`, row `cluster==3`, `mean_jaccard` = 0.419 (`cluster 3 = Armed Instabilizer`).
- **"2 of 4 archetypes clear the corrected bar"** → `tables/nb07/section3_bootstrap_summary.csv`, `mean_jaccard >= 0.50` computed on all 4 rows → 2 True (clusters 1, 2), 2 False (clusters 0, 3).
- **OOS ANOVA: F=33.6, p<.001, four groups** → `tables/nb07/section4_anova_result.csv`, columns `F_stat` (33.575488), `p_val` (1.100291e-16), `n_groups` (4).
- **"100 of 157 countries (64%) appear in more than one archetype"** → `tables/nb07/section5_cluster_assignments.csv`, `df.groupby("iso3")["archetype"].nunique()`, count of `> 1` = 100 of `iso3.nunique()` = 157 (100/157 = 63.7%, rounds to 64%).

## Section 7 — Limitations

- **"25-battle-death-per-year floor"** → BDA_Project_Plan.docx, "Robustness and Limitations" section ("UCDP captures organised armed violence with a 25-deaths-per-year floor").
- **"1989–2024" vs "1946–2024"** → `data/clean/rq1_panel.parquet` (1989–2024) vs `data/clean/master_panel.parquet` (1946–2024), `year.min()`/`year.max()` in both.
- **"one to three years" lag window, "four broad weapon-class aggregates"** → `src/rq2_panel.py`, `WEAPON_CLASSES` (4 keys); `tables/nb06/section3_dumitrescu_hurlin.csv`, `lag` column values {1,2,3}.

## References — dataset citations

- SIPRI Military Expenditure Database / Arms Transfers Database citation text → `data/README.md`, "SIPRI Military Expenditure Database (MILEX)" and "SIPRI Arms Transfers Database (TIV)" sections (exact attribution strings given verbatim in source).
- UCDP, V-Dem, WDI, CoW — no exact citation string available → `data/README.md` (each points to the provider's own citation page rather than giving a citable string directly); marked `[ADD CITATION]` in References per task instruction.

---

## Notes on claims *not* individually cited

Hypothesis-direction statements (e.g., "H1a predicted β < 0") are theoretical predictions stated in Section 2.4, not empirical findings, and are not separately sourced — they are cross-referenced against the empirical estimate immediately alongside them in Section 5.1, which *is* cited above. Publication years appearing only inside APA in-text citations (e.g., "Snyder, 1965"; "Kapur, 2008"; "Rauchhaus, 2009"; "Dumitrescu and Hurlin's (2012)"; "Benjamini and Hochberg's (1995)"; "Ben-Hur, Elisseeff, and Guyon (2002)") are bibliographic, not data claims, and are not listed separately here.

The self-check regex used to build this map also flags several tokens that are not numeric data claims at all, listed here explicitly so the self-check count reconciles cleanly rather than silently dropping them: section cross-references written as decimals — Section 2.2, Section 2.3, Section 3.1, Section 3.2, Section 3.3, Section 3.4, Section 4.1, Section 4.2 — none of which are data values; "ISO 3166-1 alpha-3" (an ISO standard identifier, not a finding); "9/11" and "post-9/11" (calendar shorthand for the September 2001 attacks, matched by a fraction-pattern regex as if it were a data ratio); and "the 2020 Nagorno-Karabakh war" (a general historical fact used for scene-setting in Section 2.2's discussion of the "Drone Effect" examples, not a value pulled from any project table — the underlying event is well-documented public history, not a claim requiring dataset traceability).
