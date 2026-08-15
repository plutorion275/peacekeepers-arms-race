# Data sources

Raw data is **not redistributed** in this repository. Each source below has its own licensing and attribution terms — download directly from the provider and place files into the paths shown. `notebooks/01_data_acquisition.ipynb` expects this layout and will checkpoint cleaned copies to `data/checkpoints/` as Parquet.

```
data/raw/
├── sipri/      # MILEX + TIV
├── ucdp/       # ACD, GED, BRD, Dyadic
├── vdem/       # V-Dem core
├── worldbank/  # WDI indicators
└── cow/        # CINC, Formal Alliances
```

---

## SIPRI Military Expenditure Database (MILEX)

- **Download:** https://www.sipri.org/databases/milex
- **Format:** Multi-sheet, multi-header XLSX
- **Save to:** `data/raw/sipri/`
- **License:** Free to use with attribution. SIPRI requests citation as: *SIPRI Military Expenditure Database*, Stockholm International Peace Research Institute, https://www.sipri.org/databases/milex

## SIPRI Arms Transfers Database (TIV)

- **Download:** https://www.sipri.org/databases/armstransfers — use the "Importer/Exporter TIV Tables" generator to export the deal-level Transfer Register
- **Note:** not a single static file; you select recipients/suppliers/years/categories and export. Simplest approach: pull all recipients × all categories × 1950–present, then filter downstream in NB01/NB02.
- **Format:** XLSX with weapon-category columns
- **Save to:** `data/raw/sipri/`
- **License:** Free to use with attribution: *SIPRI Arms Transfers Database*, Stockholm International Peace Research Institute, https://www.sipri.org/databases/armstransfers

## UCDP (Uppsala Conflict Data Program)

- **Download:** https://ucdp.uu.se/downloads/
- **Datasets used:**
  - Armed Conflict Dataset (ACD) — conflict-year
  - Georeferenced Event Dataset (GED) — event-level
  - Battle-Related Deaths (BRD) — dyad-year
  - Dyadic Dataset — dyad-year
- **Format:** CSV
- **Save to:** `data/raw/ucdp/`
- **License:** Free for research/educational use with citation. Cite the specific dataset version used (e.g., UCDP/PRIO Armed Conflict Dataset version 25.1) — see https://ucdp.uu.se/downloads/ for the exact citation per dataset.

## World Bank World Development Indicators (WDI)

- **Download:** via the `wbdata` Python package (wraps the WDI API) — no manual download needed:
  ```python
  import wbdata
  wbdata.get_dataframe({'NY.GDP.MKTP.CD': 'gdp_usd', 'SP.POP.TOTL': 'pop', ...})
  ```
  Or browse directly: https://databank.worldbank.org/source/world-development-indicators
- **Save to:** `data/raw/worldbank/`
- **License:** CC BY 4.0 — free to use, share, and adapt with attribution. https://datacatalog.worldbank.org/public-licenses

## V-Dem (Varieties of Democracy) Core Dataset

- **Download:** https://www.v-dem.net/data/the-v-dem-dataset/ (Country-Year: V-Dem Core, v16)
- **Format:** single CSV (~300MB)
- **Save to:** `data/raw/vdem/`
- **License:** Free for non-commercial/academic use with citation. See https://www.v-dem.net/about/citing-v-dem/ for the required citation format.

## Correlates of War — National Material Capabilities (CINC), v6.0

- **Download:** https://correlatesofwar.org/data-sets/national-material-capabilities/
- **Format:** CSV
- **Save to:** `data/raw/cow/`
- **License:** Free for research use with citation. Note CoW CINC coverage truncates at 2016 — this project's primary MTS specification (`mts_pca_3feat`) drops CoW `milper` to extend coverage through 2024.

## Correlates of War — Formal Alliances, v4.1

- **Download:** https://correlatesofwar.org/data-sets/formal-alliances/
- **Format:** CSV
- **Save to:** `data/raw/cow/`
- **License:** Free for research use with citation, same terms as CINC above.

---

## Provenance

`notebooks/01_data_acquisition.ipynb` writes a `_provenance.json` alongside each raw file (download date, source URL, SHA-256 hash) so the exact snapshot used in this project is auditable even though the raw files themselves aren't checked into the repo.

## Reproducing the panel

Once all raw files are in place, run notebooks 01→04 in order to produce the cleaned, ISO3-standardized, merged panel used by RQ1–RQ3 (checkpoints land in `data/checkpoints/`, final analysis-ready output in `data/clean/`).
