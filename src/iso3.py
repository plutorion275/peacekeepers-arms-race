"""ISO-3166 alpha-3 resolver for the Peacekeepers' Arms Race project.

Three-tier lookup order (ISO3Resolver):
  1. dataset_overrides  — caller-supplied, highest priority
  2. GLOBAL_OVERRIDES   — project-wide manual corrections
  3. pycountry          — exact-field lookups only (no fuzzy)

Gleditsch-Ward numeric resolver (module-level):
  GW_TO_ISO3           — dict mapping GW state codes → ISO3 alpha-3
  gw_to_iso3(code)     — single-code lookup, returns str | None
  gw_to_iso3_set(raw)  — parses raw gwno_loc value → set[str]
"""
import re
import warnings
import pandas as pd
import pycountry


# ── Global overrides ──────────────────────────────────────────────────────────
# Key: name as it appears in source data (case-insensitive match applied below)
# Value: ISO 3166-1 alpha-3, or None for entities that should be dropped

GLOBAL_OVERRIDES: dict[str, str | None] = {

    # ── Historical state succession ───────────────────────────────────────────
    # Policy: map to primary UN-seat successor unless the conflict record clearly
    # belongs to a specific successor state (handle in dataset_overrides).

    # Soviet Union → Russia (UN seat, nuclear succession, 1991)
    "Soviet Union":                          "RUS",
    "USSR":                                  "RUS",
    "Union of Soviet Socialist Republics":   "RUS",

    # Yugoslavia → Serbia (UN seat successor, Badinter Opinion)
    "Yugoslavia":                            "SRB",
    "Socialist Federal Republic of Yugoslavia": "SRB",
    "Federal Republic of Yugoslavia":        "SRB",
    "Serbia and Montenegro":                 "SRB",

    # Czechoslovakia → Czech Republic (larger economy/population; Slovakia = SVK)
    "Czechoslovakia":                        "CZE",
    "Czech Republic":                        "CZE",
    "Czechia":                               "CZE",

    # Germany reunification 1990 — all variants → unified DEU
    "East Germany":                          "DEU",
    "West Germany":                          "DEU",
    "German Democratic Republic":            "DEU",
    "Federal Republic of Germany":           "DEU",
    "Germany, East":                         "DEU",
    "Germany, West":                         "DEU",
    "German Empire":                         "DEU",
    "Prussia":                               "DEU",

    # Yemen unification 1990 — both predecessors → unified YEM
    "North Yemen":                           "YEM",
    "South Yemen":                           "YEM",
    "Yemen Arab Republic":                   "YEM",
    "Yemen, PDR":                            "YEM",
    "Yemen, North":                          "YEM",
    "Yemen, South":                          "YEM",
    "People's Democratic Republic of Yemen": "YEM",

    # Vietnam reunification 1975 → unified VNM
    "North Vietnam":                         "VNM",
    "South Vietnam":                         "VNM",
    "Democratic Republic of Vietnam":        "VNM",
    "Republic of Vietnam":                   "VNM",
    "Viet Nam":                              "VNM",

    # Austria-Hungary 1918 → Austria (COW/Correlates convention)
    "Austria-Hungary":                       "AUT",

    # Ottoman Empire → Turkey (Lausanne Treaty 1923)
    "Ottoman Empire":                        "TUR",
    "Turkey":                                "TUR",   # pre-2022 ISO name; now Türkiye (TUR)
    "Turkiye":                               "TUR",   # ASCII fallback for Türkiye
    "Türkiye":                               "TUR",

    # ── UCDP name variants ────────────────────────────────────────────────────
    # Hyphenation / short-name variants that pycountry does not resolve:
    "Bosnia-Herzegovina":                    "BIH",   # pycountry: "Bosnia and Herzegovina"
    "Brunei":                                "BRN",   # pycountry: "Brunei Darussalam"
    "Kingdom of eSwatini":                   "SWZ",   # pycountry: "Eswatini" (but not "Kingdom of …")
    "Burma":                                 "MMR",
    "Zaire":                                 "COD",
    "DR Congo (Zaire)":                      "COD",
    "DR Congo":                              "COD",
    "Democratic Republic of the Congo":      "COD",
    "Congo, Dem. Rep.":                      "COD",
    "Congo, The Democratic Republic of the": "COD",
    "Ivory Coast":                           "CIV",
    "Congo, Republic":                       "COG",
    "Congo, Rep.":                           "COG",
    "Republic of the Congo":                 "COG",
    "Tanzania":                              "TZA",
    "Tanzania, United Republic of":          "TZA",
    "Macedonia":                             "MKD",
    "North Macedonia":                       "MKD",
    "Former Yugoslav Republic of Macedonia": "MKD",
    "Macedonia, The Former Yugoslav Republic of": "MKD",
    "Gambia":                                "GMB",
    "The Gambia":                            "GMB",
    "Gambia, The":                           "GMB",
    "Myanmar (Burma)":                       "MMR",

    # ── SIPRI name variants ───────────────────────────────────────────────────
    "Korea, South":                          "KOR",
    "Korea, North":                          "PRK",
    "Congo, DR":                             "COD",
    "Cote d'Ivoire":                         "CIV",
    "Côte d'Ivoire":                         "CIV",
    "Laos":                                  "LAO",
    "Lao PDR":                               "LAO",
    "Timor Leste":                           "TLS",
    "Timor-Leste":                           "TLS",
    "East Timor":                            "TLS",
    "Sao Tome and Principe":                 "STP",
    "São Tomé and Príncipe":                 "STP",
    "Bahamas":                               "BHS",
    "Bahamas, The":                          "BHS",
    "Kyrgyz Republic":                       "KGZ",
    "Micronesia (Federated States of)":      "FSM",
    "Federated States of Micronesia":        "FSM",
    "Micronesia":                            "FSM",

    # ── World Bank WDI name variants ──────────────────────────────────────────
    "Iran, Islamic Republic of":             "IRN",
    "Iran (Islamic Rep.)":                   "IRN",
    "Iran, Islamic Rep.":                    "IRN",
    "Korea, Democratic People's Republic of": "PRK",
    "Korea, Republic of":                    "KOR",
    "Moldova, Republic of":                  "MDA",
    "Moldova":                               "MDA",
    "Bolivia (Plurinational State of)":      "BOL",
    "Bolivia, Plurinational State of":       "BOL",
    "Venezuela (Bolivarian Republic of)":    "VEN",
    "Venezuela, Bolivarian Republic of":     "VEN",
    "Syrian Arab Republic":                  "SYR",
    "Egypt, Arab Rep.":                      "EGY",
    "Taiwan, Province of China":             "TWN",
    "Kyrgyz Republic":                       "KGZ",
    "Russia":                                "RUS",   # common name; ISO name = Russian Federation
    "Russian Federation":                    "RUS",
    "United States":                         "USA",
    "United States of America":              "USA",
    "United Kingdom":                        "GBR",
    "Great Britain":                         "GBR",
    "Libya":                                 "LBY",

    # ── Non-ISO recognised states ─────────────────────────────────────────────
    # Kosovo: uses XKX (EC/EULEX/World Bank code; not in ISO 3166-1)
    "Kosovo":                                "XKX",
    "Republic of Kosovo":                    "XKX",
    # Taiwan: ISO 3166-1 entry TWN ("Taiwan, Province of China")
    "Taiwan":                                "TWN",
    "Republic of China":                     "TWN",
    # Palestine: ISO 3166-1 = PSE
    "Palestine":                             "PSE",
    "Palestinian Territories":               "PSE",
    "Palestinian Authority":                 "PSE",
    "West Bank and Gaza":                    "PSE",
    "State of Palestine":                    "PSE",

    # ── Explicit None — never a valid ISO3 country ───────────────────────────
    # Dropped during cleaning; logged to unmatched audit for documentation.
    "Hyderabad":                             None,   # Indian princely state, dissolved 1948
    "Somaliland":                            None,   # unrecognised; subsumed into Somalia 1960
    "European Union":                        None,   # supra-national aggregate

    # ── Non-state armed groups — must NEVER resolve to any sovereign state ────
    # Critical: pycountry.search_fuzzy maps "IS" → ISL (Iceland) via alpha_2
    # match, giving Iceland 200+ false conflict-participations in the panel.
    # Explicit None here short-circuits before any pycountry call.
    "Islamic State":                         None,
    "IS":                                    None,   # matches Iceland alpha_2 "IS" via fuzzy
    "ISIL":                                  None,
    "ISIS":                                  None,
    "Islamic State of Iraq":                 None,
    "Islamic State of Iraq and the Levant":  None,
    "Islamic State of Iraq and Syria":       None,
    "Islamic State - Khorasan Province":     None,
    "Islamic State (Sinai Province)":        None,
    "Daesh":                                 None,
    "Al-Qaeda":                              None,
    "Al-Shabaab":                            None,
    "Hezbollah":                             None,
    "Hamas":                                 None,
    "Taliban":                               None,
    "PKK":                                   None,
    "FARC":                                  None,
    "Lord's Resistance Army":               None,
    "LRA":                                   None,
    "Boko Haram":                            None,
}


# ── COW → ISO3 mapping ────────────────────────────────────────────────────────
# Correlates of War NMC stateabb codes that differ from ISO 3166-1 alpha-3.
# Source: COW NMC v6.0 codebook + standard COW-ISO crosswalks.
# Codes identical to ISO3 are omitted (e.g. AFG, IND, USA, RUS, …).

COW_TO_ISO3: dict[str, str | None] = {
    # ── Europe / Major powers ─────────────────────────────────────────────────
    "UKG": "GBR",   # United Kingdom
    "FRN": "FRA",   # France
    "GMY": "DEU",   # Imperial / Weimar Germany
    "GFR": "DEU",   # West Germany → unified Germany
    "GDR": "DEU",   # East Germany → unified Germany
    "AUH": "AUT",   # Austria-Hungary (COW convention: Austria inherits)
    "AUL": "AUS",   # Australia  (note: AUS = Austria in COW!)
    "AUS": "AUT",   # Austria    (note: AUL = Australia in COW!)
    "NTH": "NLD",   # Netherlands
    "SPN": "ESP",   # Spain
    "SWD": "SWE",   # Sweden
    "CHE": "CHE",   # Switzerland  (ISO3 = CHE; COW uses SWZ for Switzerland — see below)
    "SWZ": "CHE",   # Switzerland (COW SWZ ≠ ISO3 SWZ; ISO3 SWZ = Eswatini)
    "POR": "PRT",   # Portugal
    "DEN": "DNK",   # Denmark
    "NOR": "NOR",   # Norway         (same — kept for completeness)
    "ICE": "ISL",   # Iceland
    "IRE": "IRL",   # Ireland
    "BUL": "BGR",   # Bulgaria
    "ROM": "ROU",   # Romania
    "YUG": "SRB",   # Yugoslavia → Serbia
    "CZR": "CZE",   # Czechoslovakia remnant → Czech Republic
    "SLO": "SVK",   # Slovakia
    "SLV": "SVN",   # Slovenia
    "CRO": "HRV",   # Croatia
    "BOS": "BIH",   # Bosnia-Herzegovina
    "MON": "MNE",   # Montenegro
    "MAC": "MKD",   # North Macedonia
    "KOS": "XKX",   # Kosovo
    "ALB": "ALB",   # Albania         (same)
    "GRC": "GRC",   # Greece          (same)
    "CYP": "CYP",   # Cyprus          (same)
    "MLT": "MLT",   # Malta           (same)
    "LIE": "LIE",   # Liechtenstein   (same)
    "MNC": "MCO",   # Monaco
    "AND": "AND",   # Andorra         (same)
    "LUX": "LUX",   # Luxembourg      (same)
    "FIN": "FIN",   # Finland         (same)
    "POL": "POL",   # Poland          (same)
    "HUN": "HUN",   # Hungary         (same)
    "ITA": "ITA",   # Italy           (same)
    "BEL": "BEL",   # Belgium         (same)
    "EST": "EST",   # Estonia         (same)
    "LAT": "LVA",   # Latvia
    "LIT": "LTU",   # Lithuania
    "BLR": "BLR",   # Belarus         (same)
    "UKR": "UKR",   # Ukraine         (same)
    "MLD": "MDA",   # Moldova
    "GRG": "GEO",   # Georgia
    "ARM": "ARM",   # Armenia         (same)
    "AZE": "AZE",   # Azerbaijan      (same)
    "RUS": "RUS",   # Russia          (same)

    # ── Former Soviet Central Asia ────────────────────────────────────────────
    "KZK": "KAZ",   # Kazakhstan
    "KYR": "KGZ",   # Kyrgyzstan
    "TAJ": "TJK",   # Tajikistan
    "TKM": "TKM",   # Turkmenistan    (same)
    "UZB": "UZB",   # Uzbekistan      (same)

    # ── Historical German micro-states → None (absorbed pre-1871) ─────────────
    "BAD": None,    # Baden
    "BAV": None,    # Bavaria
    "HAN": None,    # Hanover
    "HSE": None,    # Hesse Electoral
    "HSG": None,    # Hesse Grand Ducal
    "SAX": None,    # Saxony
    "WRT": None,    # Württemberg
    "MEC": None,    # Mecklenburg

    # ── Historical Italian micro-states → None (absorbed pre-1870) ────────────
    "MOD": None,    # Modena
    "SIC": None,    # Sicily (Two Sicilies)
    "TUS": None,    # Tuscany
    "PAP": None,    # Papal States

    # ── Middle East ───────────────────────────────────────────────────────────
    "LEB": "LBN",   # Lebanon
    "KUW": "KWT",   # Kuwait
    "BAH": "BHR",   # Bahrain
    "OMA": "OMN",   # Oman
    "UAE": "ARE",   # United Arab Emirates
    "AAB": "ARE",   # Abu Dhabi → UAE (predecessor entity)
    "PAL": "PSE",   # Palestine
    "TAW": "TWN",   # Taiwan
    "YAR": "YEM",   # North Yemen (Yemen Arab Republic)
    "YPR": "YEM",   # South Yemen (PDR)

    # ── Asia-Pacific ──────────────────────────────────────────────────────────
    "INS": "IDN",   # Indonesia
    "SIN": "SGP",   # Singapore
    "PHI": "PHL",   # Philippines
    "CAM": "KHM",   # Cambodia
    "THI": "THA",   # Thailand
    "MYA": "MMR",   # Myanmar
    "BNG": "BGD",   # Bangladesh
    "NEP": "NPL",   # Nepal
    "BHU": "BTN",   # Bhutan
    "SRI": "LKA",   # Sri Lanka
    "BRU": "BRN",   # Brunei
    "MAL": "MYS",   # Malaysia
    "MAS": "MHL",   # Marshall Islands
    "MSI": "FSM",   # Micronesia (Federated States)
    "ETM": "TLS",   # East Timor → Timor-Leste
    "PNG": "PNG",   # Papua New Guinea  (same)
    "ROK": "KOR",   # Republic of Korea (South Korea)
    "DRV": "VNM",   # Democratic Republic of Vietnam (North)
    "RVN": "VNM",   # Republic of Vietnam (South) → unified VNM
    "NEW": "NZL",   # New Zealand
    "FIJ": "FJI",   # Fiji
    "VAN": "VUT",   # Vanuatu
    "SOL": "SLB",   # Solomon Islands
    "NAU": "NRU",   # Nauru
    "WSM": "WSM",   # Samoa          (same)
    "TON": "TON",   # Tonga          (same)
    "TUV": "TUV",   # Tuvalu         (same)
    "KIR": "KIR",   # Kiribati       (same)
    "FSM": "FSM",   # Micronesia     (same)

    # ── Africa ────────────────────────────────────────────────────────────────
    "SAF": "ZAF",   # South Africa
    "ALG": "DZA",   # Algeria
    "MOR": "MAR",   # Morocco
    "MAA": "MRT",   # Mauritania
    "LIB": "LBY",   # Libya
    "EGY": "EGY",   # Egypt          (same)
    "SUD": "SDN",   # Sudan
    "ETH": "ETH",   # Ethiopia       (same)
    "ERI": "ERI",   # Eritrea        (same)
    "SOM": "SOM",   # Somalia        (same)
    "SNM": None,    # Somaliland (unrecognised)
    "DJI": "DJI",   # Djibouti       (same)
    "KEN": "KEN",   # Kenya          (same)
    "UGA": "UGA",   # Uganda         (same)
    "RWA": "RWA",   # Rwanda         (same)
    "BUI": "BDI",   # Burundi
    "TAZ": "TZA",   # Tanzania
    "ZAN": "TZA",   # Zanzibar → Tanzania
    "MAD": "MDG",   # Madagascar
    "MAG": "MDG",   # Malagasy Republic (pre-1975 name)
    "MAW": "MWI",   # Malawi
    "ZAM": "ZMB",   # Zambia
    "ZIM": "ZWE",   # Zimbabwe
    "MOZ": "MOZ",   # Mozambique     (same)
    "MZM": "MOZ",   # Mozambique (alternate COW code)
    "NAM": "NAM",   # Namibia        (same)
    "SWA": "NAM",   # South West Africa → Namibia
    "BOT": "BWA",   # Botswana
    "LES": "LSO",   # Lesotho
    # Eswatini/Swaziland is not in NMC-6; SWZ is COW's code for Switzerland (→ CHE above).
    "ANG": "AGO",   # Angola
    "NIG": "NGA",   # Nigeria
    "NIR": "NER",   # Niger
    "GHA": "GHA",   # Ghana          (same)
    "CAO": "CMR",   # Cameroon
    "CEN": "CAF",   # Central African Republic
    "CHA": "TCD",   # Chad
    "SEN": "SEN",   # Senegal        (same)
    "GUI": "GIN",   # Guinea
    "GNB": "GNB",   # Guinea-Bissau  (same)
    "SIE": "SLE",   # Sierra Leone
    "LBR": "LBR",   # Liberia        (same)
    "CDI": "CIV",   # Côte d'Ivoire
    "BFO": "BFA",   # Burkina Faso (Upper Volta)
    "MLI": "MLI",   # Mali           (same)
    "TOG": "TGO",   # Togo
    "BEN": "BEN",   # Benin          (same)
    "GAM": "GMB",   # Gambia
    "CAP": "CPV",   # Cape Verde
    "GAB": "GAB",   # Gabon          (same)
    "CON": "COG",   # Republic of Congo (Congo-Brazzaville)
    "DRC": "COD",   # DR Congo
    "CAM": "KHM",   # Cambodia (duplicate handled above)
    "COM": "COM",   # Comoros        (same)
    "SEY": "SYC",   # Seychelles
    "STP": "STP",   # São Tomé and Príncipe  (same)
    "SSD": "SSD",   # South Sudan    (same)
    "EQG": "GNQ",   # Equatorial Guinea

    # ── Americas ──────────────────────────────────────────────────────────────
    "CAN": "CAN",   # Canada         (same)
    "MEX": "MEX",   # Mexico         (same)
    "GUA": "GTM",   # Guatemala
    "HON": "HND",   # Honduras
    "SAL": "SLV",   # El Salvador
    "NIC": "NIC",   # Nicaragua      (same)
    "COS": "CRI",   # Costa Rica
    "PAN": "PAN",   # Panama         (same)
    "PMA": "PAN",   # Panama (alternate)
    "CUB": "CUB",   # Cuba           (same)
    "HAI": "HTI",   # Haiti
    "DOM": "DOM",   # Dominican Republic  (same)
    "JAM": "JAM",   # Jamaica        (same)
    "TRI": "TTO",   # Trinidad and Tobago
    "BAR": "BRB",   # Barbados
    "GRN": "GRD",   # Grenada
    "DMA": "DMA",   # Dominica       (same)
    "SKN": "KNA",   # St. Kitts and Nevis
    "SLU": "LCA",   # St. Lucia
    "SVG": "VCT",   # St. Vincent and Grenadines
    "BLZ": "BLZ",   # Belize         (same)
    "COL": "COL",   # Colombia       (same)
    "VEN": "VEN",   # Venezuela      (same)
    "GUY": "GUY",   # Guyana         (same)
    "SUR": "SUR",   # Suriname       (same)
    "ECU": "ECU",   # Ecuador        (same)
    "PER": "PER",   # Peru           (same)
    "BOL": "BOL",   # Bolivia        (same)
    "BRA": "BRA",   # Brazil         (same)
    "PAR": "PRY",   # Paraguay
    "URU": "URY",   # Uruguay
    "ARG": "ARG",   # Argentina      (same)
    "CHL": "CHL",   # Chile          (same)
    "BHM": "BHS",   # Bahamas
}


# ── Gleditsch-Ward numeric code → ISO3 ───────────────────────────────────────
# Source: Gleditsch & Ward (1999) state system + UCDP dyadic gwno_loc column.
# All 123 codes observed in UCDP Dyadic v25.1 are included and verified against
# the location text column. Codes that map to non-sovereign entities are None.
#
# Key corrections relative to COW numbering:
#   483 = Chad (TCD)  [not CAF — cross-checked against UCDP location text]
#   484 = Republic of Congo (COG)  [not DRC — "Government of Congo" vs Ninjas]
#   490 = DR Congo/Zaire (COD)
#   369 = Ukraine  [not Belarus — confirmed from Russia-Ukraine conflict rows]

GW_TO_ISO3: dict[int, str | None] = {

    # ── Americas ──────────────────────────────────────────────────────────────
    2:   "USA",
    20:  "CAN",
    31:  "BHS",   # Bahamas
    40:  "CUB",
    41:  "HTI",
    42:  "DOM",
    51:  "JAM",
    52:  "TTO",
    53:  "BRB",
    54:  "DMA",
    55:  "GRD",
    56:  "LCA",
    57:  "VCT",
    58:  "ATG",
    60:  "KNA",
    70:  "MEX",
    80:  "BLZ",
    90:  "GTM",
    91:  "HND",
    92:  "SLV",
    93:  "NIC",
    94:  "CRI",
    95:  "PAN",
    100: "COL",
    101: "VEN",
    110: "GUY",
    115: "SUR",
    130: "ECU",
    135: "PER",
    140: "BRA",
    145: "BOL",
    150: "PRY",
    155: "CHL",
    160: "ARG",
    165: "URY",

    # ── Western Europe ────────────────────────────────────────────────────────
    200: "GBR",
    205: "IRL",
    210: "NLD",
    211: "BEL",
    212: "LUX",
    220: "FRA",
    225: "CHE",
    230: "ESP",
    232: "AND",
    235: "PRT",
    255: "DEU",
    260: "AUT",
    265: "DEU",   # West Germany → unified DEU
    267: "DEU",   # East Germany → unified DEU
    269: "AUT",   # Austria-Hungary → AUT (COW convention)
    270: "AUT",
    290: "POL",
    305: "AUT",
    310: "HUN",
    316: "CZE",
    317: "SVK",
    325: "ITA",
    327: "SMR",
    329: "MCO",
    338: "MLT",
    339: "ALB",
    343: "MKD",
    344: "HRV",
    345: "SRB",   # Yugoslavia → Serbia (UN-seat successor)
    346: "BIH",
    347: "MNE",
    349: "SVN",
    350: "GRC",
    352: "CYP",
    355: "BGR",
    359: "MDA",
    360: "ROU",
    365: "RUS",   # Russia / Soviet Union (UN-seat successor)
    366: "EST",
    367: "LVA",
    368: "LTU",
    369: "UKR",   # Ukraine (confirmed: 369=UKR in UCDP Russia-Ukraine rows)
    370: "BLR",   # Belarus (GW 370; 369=UKR per UCDP data)
    371: "MDA",   # Moldova alternate code (use 359 as primary)
    372: "GEO",
    373: "AZE",
    374: "ARM",
    375: "FIN",
    380: "SWE",
    385: "NOR",
    390: "DNK",
    395: "ISL",

    # ── Africa ────────────────────────────────────────────────────────────────
    402: "CPV",
    404: "GNB",
    411: "GNQ",
    420: "GMB",
    432: "MLI",
    433: "SEN",
    434: "BEN",
    435: "MRT",
    436: "NER",
    437: "CIV",
    438: "GIN",
    439: "BFA",
    450: "LBR",
    451: "SLE",
    452: "GHA",
    461: "TGO",
    471: "CMR",
    475: "NGA",
    481: "GAB",
    482: "CAF",
    483: "TCD",   # Chad — verified from UCDP location text
    484: "COG",   # Republic of Congo (Brazzaville) — verified from "Government of Congo"
    490: "COD",   # DR Congo / Zaire — verified from "DR Congo (Zaire)"
    500: "UGA",
    501: "KEN",
    510: "TZA",
    516: "BDI",
    517: "RWA",
    520: "SOM",
    522: "DJI",
    530: "ETH",
    531: "ERI",
    540: "AGO",
    541: "MOZ",
    551: "ZMB",
    552: "ZWE",
    553: "MWI",
    560: "ZAF",
    565: "NAM",
    570: "LSO",
    571: "BWA",
    572: "SWZ",
    580: "MDG",
    581: "COM",
    590: "MUS",
    591: "STP",

    # ── North Africa and Middle East ──────────────────────────────────────────
    600: "MAR",
    615: "DZA",
    616: "TUN",
    620: "LBY",
    625: "SDN",
    626: "SSD",   # South Sudan (post-2011)
    630: "IRN",
    640: "TUR",
    645: "IRQ",
    651: "EGY",
    652: "SYR",
    660: "LBN",
    663: "JOR",
    666: "ISR",
    670: "SAU",
    678: "YEM",   # unified Yemen (post-1990)
    680: "YEM",   # South Yemen (PDR) → unified YEM
    690: "KWT",
    694: "QAT",
    696: "BHR",
    698: "OMN",
    699: "ARE",

    # ── Central and South Asia ────────────────────────────────────────────────
    700: "AFG",
    701: "TKM",
    702: "TJK",
    703: "KGZ",
    704: "UZB",
    705: "KAZ",

    # ── East and South-East Asia ──────────────────────────────────────────────
    710: "CHN",
    712: "MNG",
    713: "TWN",   # Taiwan (ISO3 TWN; non-universal recognition — included for completeness)
    730: "KOR",   # South Korea (Republic of Korea)
    731: "PRK",   # North Korea (DPRK)
    732: "KOR",   # South Korea (alternate GW code; primary is 730)
    740: "JPN",
    750: "IND",
    751: None,    # Hyderabad (Indian princely state; dissolved 1948; not sovereign)
    760: "BTN",
    770: "PAK",
    771: "BGD",
    775: "MMR",
    780: "LKA",
    781: "MDV",
    790: "NPL",
    800: "THA",
    811: "KHM",
    812: "LAO",
    816: "VNM",   # Vietnam (unified post-1976 / North Vietnam as predecessor)
    817: "VNM",   # South Vietnam → unified VNM
    820: "MYS",
    830: "SGP",
    835: "BRN",
    840: "IDN",
    850: "PHL",
    860: "TLS",   # East Timor / Timor-Leste (post-2002)

    # ── Oceania ───────────────────────────────────────────────────────────────
    900: "AUS",
    910: "PNG",
    920: "SLB",
    935: "VUT",
    940: "FJI",
    950: "TON",
    955: "WSM",
    970: "KIR",
    971: "NRU",
    972: "TUV",
    983: "FSM",
    986: "MHL",
    990: "PLW",
}


def gw_to_iso3(gwno: int | float | str) -> str | None:
    """Return ISO3 alpha-3 for a single Gleditsch-Ward numeric code.

    Accepts int, float (e.g. 645.0 from pandas NaN-coerced columns), or
    a string that represents a single integer. Returns None and emits a
    warnings.warn() for unrecognised codes so the audit trail stays clean.
    """
    if gwno is None:
        return None
    try:
        code = int(float(str(gwno).strip()))
    except (ValueError, TypeError):
        return None
    result = GW_TO_ISO3.get(code)
    if result is None and code not in GW_TO_ISO3:
        warnings.warn(f"gw_to_iso3: unrecognised GW code {code}", stacklevel=2)
    return result


def gw_to_iso3_set(gwno_raw) -> set[str]:
    """Parse a raw gwno_loc value from UCDP → set of ISO3 alpha-3 codes.

    Handles:
      - Scalar int or float (e.g. 645 or 645.0)
      - Comma-separated string (e.g. "645, 652" or "2, 200, 645, 900")
      - NaN / None / empty string → empty set

    Returns an empty set when gwno_raw is missing or all codes are unresolvable.
    The empty-set case is handled upstream by defaulting is_extraterritorial=False.
    """
    import math
    if gwno_raw is None:
        return set()
    if isinstance(gwno_raw, float) and math.isnan(gwno_raw):
        return set()
    parts = str(gwno_raw).split(",")
    result: set[str] = set()
    for part in parts:
        part = part.strip()
        if not part:
            continue
        iso3 = gw_to_iso3(part)
        if iso3 is not None:
            result.add(iso3)
    return result


# ── ISO3Resolver class ────────────────────────────────────────────────────────

class ISO3Resolver:
    """Resolve country names to ISO 3166-1 alpha-3 codes.

    Lookup order (first hit wins):
      1. dataset_overrides supplied at construction time
      2. GLOBAL_OVERRIDES
      3. pycountry fuzzy search
    """

    def __init__(self, dataset_overrides: dict[str, str | None] | None = None):
        self._dataset_overrides: dict[str, str | None] = dataset_overrides or {}
        self._cache: dict[str, str | None] = {}
        self.unmatched_log: list[dict] = []

    # ── Public API ────────────────────────────────────────────────────────────

    def resolve(self, name: str, dataset: str | None = None) -> str | None:
        """Return ISO3 code for *name*, or None if unresolvable.

        Unresolved names (that are not None-mapped) are recorded in
        unmatched_log for the post-run audit.
        """
        if not isinstance(name, str) or not name.strip():
            return None

        name_clean = name.strip()
        cache_key = (name_clean, dataset)

        if cache_key in self._cache:
            return self._cache[cache_key]

        # Strip UCDP parenthetical historical-name suffix before all lookup tiers.
        # Handles: "Russia (Soviet Union)" → "Russia",
        #           "Serbia (Yugoslavia)" → "Serbia",
        #           "Cambodia (Kampuchea)" → "Cambodia", etc.
        # The original name_clean is preserved in the unmatched log for audit purposes.
        cleaned = re.sub(r"\s*\([^)]*\)\s*$", "", name_clean).strip() or name_clean

        result = self._lookup(cleaned, dataset)
        self._cache[cache_key] = result

        if result is None and not self._is_explicit_none(cleaned):
            self.unmatched_log.append({"dataset": dataset or "", "name": name_clean})

        return result

    def resolve_series(self, series: pd.Series, dataset: str | None = None) -> pd.Series:
        """Vectorised resolve over a pandas Series. Returns a Series of ISO3 or NaN."""
        return series.map(lambda x: self.resolve(x, dataset=dataset))

    def report_unmatched(self) -> pd.DataFrame:
        """Return a DataFrame of unresolved names grouped by (dataset, name), count desc."""
        if not self.unmatched_log:
            return pd.DataFrame(columns=["dataset", "name", "count"])
        df = pd.DataFrame(self.unmatched_log)
        return (
            df.groupby(["dataset", "name"], as_index=False)
              .size()
              .rename(columns={"size": "count"})
              .sort_values("count", ascending=False)
              .reset_index(drop=True)
        )

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _lookup(self, name: str, dataset: str | None) -> str | None:
        # Tier 1: dataset-specific override
        result = self._dataset_overrides.get(name)
        if result is not None or name in self._dataset_overrides:
            return result

        # Tier 2: global override (try exact, then title-case, then lower)
        for variant in (name, name.title(), name.lower()):
            if variant in GLOBAL_OVERRIDES:
                return GLOBAL_OVERRIDES[variant]

        # Tier 3: pycountry exact-only lookups — NO fuzzy matching.
        # search_fuzzy() is banned: it maps "IS" → ISL (Iceland) via alpha_2,
        # corrupting every ISIS dyad in the panel.  Use only exact field lookups.
        if len(name) == 3 and name.isupper():
            country = pycountry.countries.get(alpha_3=name)
            if country:
                return country.alpha_3

        country = (
            pycountry.countries.get(name=name)
            or pycountry.countries.get(common_name=name)
            or pycountry.countries.get(official_name=name)
        )
        if country:
            return country.alpha_3

        return None

    def _is_explicit_none(self, name: str) -> bool:
        """True if *name* is explicitly mapped to None in any override dict."""
        for variant in (name, name.title(), name.lower()):
            if variant in self._dataset_overrides and self._dataset_overrides[variant] is None:
                return True
            if variant in GLOBAL_OVERRIDES and GLOBAL_OVERRIDES[variant] is None:
                return True
        return False


# ── Fix 1 verification — run with: python src/iso3.py ────────────────────────
if __name__ == "__main__":
    _r = ISO3Resolver()
    assert _r.resolve("Islamic State") is None, "Islamic State must be None"
    assert _r.resolve("IS") is None,            "IS must be None (was resolving to ISL)"
    assert _r.resolve("ISIL") is None,          "ISIL must be None"
    assert _r.resolve("ISIS") is None,          "ISIS must be None"
    assert _r.resolve("Iceland") == "ISL",      "Iceland must resolve to ISL"
    assert _r.resolve("ISL") == "ISL",          "ISL alpha_3 must resolve to ISL"
    assert _r.resolve("Burma") == "MMR",        "Burma must resolve to MMR"
    assert _r.resolve("Kosovo") == "XKX",       "Kosovo must resolve to XKX"
    print("Fix 1 assert block: all checks passed.")
