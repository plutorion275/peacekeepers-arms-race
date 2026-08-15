# Changelog

All notable changes to this repository are documented here.

## [v1.0.1] — 2026-08-15

### Added
- **Project website** (`docs/`, served via GitHub Pages): a full multi-page site presenting every finding, hypothesis, regression table, and all 51 committed figures without requiring a notebook re-run.
  - `index.html` — landing page with headline stats and the three RQ summary cards.
  - `data-methods.html` — the nine-dataset source register, MTS construction, participation-vs-location panel logic, and the six-incident data-quality "after-action report."
  - `rq1.html` — H1a–H1e hypothesis-by-hypothesis verdicts, the full primary regression table, and the Africa/regime-type mechanism checks.
  - `rq2.html` — a five-stage case-file narrative walking the Dumitrescu–Hurlin miscalibration from the naive 8/12 result through the circular-shift correction to the independent forecasting corroboration (0/12).
  - `rq3.html` — the four cluster archetypes with real centroid statistics, the silhouette-vs-gap-statistic k-selection disagreement, and the stability-vs-out-of-sample-validity split.
  - `gallery.html` — all 51 figures, filterable by notebook, with a click-to-enlarge lightbox.
  - `paper.html` — the complete manuscript (abstract through references) with section-jump navigation.
  - `about.html` — reproducibility instructions, citation block, and the AI-use disclosure.
  - Design: a dark "command-center" theme (gunmetal base, khaki-parchment alternating sections) with a signal-red / olive / steel-blue / amber accent system mapped to RQ1/RQ2/RQ3, HUD-style corner brackets, a topographic grid texture, and an animated radar sweep in the hero.
- `CHANGELOG.md` (this file).
- Screenshots of the new site embedded in `README.md`.

### Fixed
- Site pages were missing `<meta charset="UTF-8">`, causing browsers without an explicit charset hint to mis-decode UTF-8 punctuation (em dashes, middot separators, arrows) as Windows-1252 mojibake. All eight pages now declare UTF-8 explicitly.

## [v1.0.0] — 2026-08-15

Initial submission-track release: the full 15-notebook analysis pipeline (00–14), `src/` shared modules, committed `figures/` and `tables/`, and the manuscript draft (`reports/draft.md` / `draft.pdf`) archived to Zenodo.
