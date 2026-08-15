"""Tests for src/iso3.py — ISO3Resolver and Gleditsch-Ward code resolution.

Formalizes the __main__ assert block at the bottom of src/iso3.py into
pytest tests and extends coverage to the full lookup-tier priority chain,
GW-code resolution, and the unmatched-name audit log.
"""
import pytest

from src.iso3 import ISO3Resolver, gw_to_iso3, gw_to_iso3_set, GLOBAL_OVERRIDES


class TestIslamicStateRegression:
    # This is the actual bug this file exists to prevent recurring.
    def test_islamic_state_variants_resolve_to_none(self):
        r = ISO3Resolver()
        for name in ["Islamic State", "Islamic State of Iraq",
                     "Islamic State of Iraq and the Levant",
                     "Islamic State of Iraq and Syria",
                     "Islamic State - Khorasan Province",
                     "Islamic State (Sinai Province)"]:
            assert r.resolve(name) is None

    def test_is_acronym_does_not_fuzzy_resolve_to_iceland(self):
        # The actual root cause: search_fuzzy() maps "IS" -> ISL via alpha_2.
        # This must stay None, not silently start resolving to Iceland again
        # if someone re-adds fuzzy search in a future edit.
        r = ISO3Resolver()
        assert r.resolve("IS") is None
        assert r.resolve("ISIL") is None
        assert r.resolve("ISIS") is None

    def test_iceland_itself_still_resolves_correctly(self):
        # Guards against overcorrecting: Iceland must NOT become collateral
        # damage of the IS fix.
        r = ISO3Resolver()
        assert r.resolve("Iceland") == "ISL"
        assert r.resolve("ISL") == "ISL"


class TestHistoricalStateSuccession:
    @pytest.mark.parametrize("name,expected", [
        ("Soviet Union", "RUS"), ("USSR", "RUS"),
        ("Yugoslavia", "SRB"), ("Serbia and Montenegro", "SRB"),
        ("Czechoslovakia", "CZE"),
        ("East Germany", "DEU"), ("West Germany", "DEU"),
        ("North Yemen", "YEM"), ("South Yemen", "YEM"),
        ("North Vietnam", "VNM"), ("South Vietnam", "VNM"),
        ("Ottoman Empire", "TUR"),
    ])
    def test_historical_states_map_to_successor(self, name, expected):
        r = ISO3Resolver()
        assert r.resolve(name) == expected


class TestNameVariants:
    @pytest.mark.parametrize("name,expected", [
        ("Burma", "MMR"), ("Myanmar (Burma)", "MMR"),
        ("Ivory Coast", "CIV"), ("Cote d'Ivoire", "CIV"),
        ("Bosnia-Herzegovina", "BIH"),
        ("Kosovo", "XKX"),
        ("DR Congo", "COD"), ("Congo, Dem. Rep.", "COD"),
        ("Congo, Republic", "COG"),
    ])
    def test_name_variants_resolve_correctly(self, name, expected):
        r = ISO3Resolver()
        assert r.resolve(name) == expected


class TestParentheticalStripping:
    def test_strips_trailing_parenthetical_before_lookup(self):
        r = ISO3Resolver()
        # "Russia (Soviet Union)" -> strips to "Russia" -> pycountry exact match
        assert r.resolve("Russia (Soviet Union)") == "RUS"


class TestOverridePriority:
    def test_dataset_override_beats_global_override(self):
        # Tier 1 (dataset_overrides) must win over Tier 2 (GLOBAL_OVERRIDES)
        # even when GLOBAL_OVERRIDES has an entry for the same name.
        r = ISO3Resolver(dataset_overrides={"Soviet Union": "XYZ_TEST"})
        assert r.resolve("Soviet Union") == "XYZ_TEST"

    def test_dataset_override_can_force_none(self):
        r = ISO3Resolver(dataset_overrides={"Some Coalition": None})
        assert r.resolve("Some Coalition") is None


class TestInputHandling:
    @pytest.mark.parametrize("bad_input", [None, "", "   ", 123, 4.5, []])
    def test_non_string_or_empty_input_returns_none(self, bad_input):
        r = ISO3Resolver()
        assert r.resolve(bad_input) is None

    def test_unresolvable_name_returns_none(self):
        r = ISO3Resolver()
        assert r.resolve("Definitely Not A Real Country Name XYZ123") is None


class TestUnmatchedLog:
    def test_explicit_none_does_not_pollute_unmatched_log(self):
        # Islamic State is explicitly None -- it's a KNOWN non-country, not
        # an unresolved one, and must not show up asking for a manual fix.
        r = ISO3Resolver()
        r.resolve("Islamic State")
        assert not any(e["name"] == "Islamic State" for e in r.unmatched_log)

    def test_genuinely_unresolvable_name_appears_in_unmatched_log(self):
        r = ISO3Resolver()
        r.resolve("Definitely Not A Real Country Name XYZ123", dataset="test")
        assert any(e["name"] == "Definitely Not A Real Country Name XYZ123"
                   for e in r.unmatched_log)

    def test_report_unmatched_returns_dataframe_with_counts(self):
        # resolve() caches by (name_clean, dataset), so two identical resolve()
        # calls only log once -- the second is a cache hit, not a re-miss.
        # Append directly to unmatched_log to test report_unmatched()'s own
        # groupby/count aggregation in isolation from that dedup behaviour.
        r = ISO3Resolver()
        r.unmatched_log.append({"dataset": "test", "name": "Fake Country A"})
        r.unmatched_log.append({"dataset": "test", "name": "Fake Country A"})
        report = r.report_unmatched()
        row = report[report["name"] == "Fake Country A"]
        assert len(row) == 1
        assert row.iloc[0]["count"] == 2


class TestResolveSeries:
    def test_resolve_series_vectorised(self):
        import pandas as pd
        r = ISO3Resolver()
        s = pd.Series(["Burma", "Kosovo", "Islamic State"])
        result = r.resolve_series(s)
        # docstring: "Returns a Series of ISO3 or NaN" -- Series.map coerces
        # the unresolved None to NaN on an object-dtype Series, not None.
        assert result.iloc[0] == "MMR"
        assert result.iloc[1] == "XKX"
        assert pd.isna(result.iloc[2])


class TestGwToIso3:
    # Real entries read directly from GW_TO_ISO3 in src/iso3.py:
    #   2: "USA", 200: "GBR", 645: "IRQ"
    @pytest.mark.parametrize("gwno,expected", [
        (2, "USA"),
        (200, "GBR"),
        (645, "IRQ"),
    ])
    def test_known_gw_codes_resolve(self, gwno, expected):
        assert gw_to_iso3(gwno) == expected

    def test_accepts_int_float_and_string(self):
        # GW 645 = "IRQ" (read from GW_TO_ISO3). Confirm int/float/string
        # forms of the same code all resolve to the same iso3.
        assert gw_to_iso3(645) == "IRQ"
        assert gw_to_iso3(645.0) == "IRQ"
        assert gw_to_iso3("645") == "IRQ"

    def test_none_input_returns_none(self):
        assert gw_to_iso3(None) is None

    def test_unrecognised_code_warns_and_returns_none(self):
        with pytest.warns(UserWarning, match="unrecognised GW code"):
            result = gw_to_iso3(999999)
        assert result is None


class TestGwToIso3Set:
    def test_comma_separated_string(self):
        # GW 2 = "USA", GW 200 = "GBR" (read from GW_TO_ISO3).
        assert gw_to_iso3_set("2,200") == {"USA", "GBR"}

    def test_nan_returns_empty_set(self):
        import math
        assert gw_to_iso3_set(float("nan")) == set()

    def test_none_returns_empty_set(self):
        assert gw_to_iso3_set(None) == set()

    def test_empty_string_returns_empty_set(self):
        assert gw_to_iso3_set("") == set()
