# NB12 pass 5 — recalibrate the omnibus on the circular-shift null, isolate the near-duplicate cell pair, promote the circular-shift size figures

Protocol: the standing NB12 patch protocol applies (locked constants, nbformat transform
with anchor asserts, regression guard, no `git add -A`, branching readings computed not
hardcoded). This spec supplies the tasks only.

Expected: **no new DH calls.** All four caches must report HIT, including
`nb12_perm_circshift_2000.parquet`.

## Context — three loose ends from pass 4

Pass 4 established that the within-country shuffle null is mis-specified: it destroys the
treatments' serial structure (mean lag-1 ACF −0.329 observed, −0.023 shuffled) while the
circular-shift null preserves it (−0.311). The circular-shift null is therefore the better
reference. Three consequences were not carried through.

**1. The omnibus tests are calibrated on the superseded null.** Fisher and Simes were
computed from the shuffle-based `p_cell` and calibrated against shuffle-based leave-one-out
draws. The circular-shift null changes the per-cell p-values materially: MISSILES×part_n_minor
0.0555 → 0.1199, NAVAL×part_n_minor 0.0615 → 0.1439, both more than doubling. So the
reassuring aggregate number (Fisher p=0.0705) and the borderline one (count p=0.0975) come
from different nulls. A referee will notice.

**2. The `max |r| = 0.951` pair was never identified.** Pass 3 measured mean|r| = 0.068 with
max 0.951 and the retraction correctly killed the claim that *average* dependence explains
the count excess. But one near-duplicate pair is not an average-structure fact, and the
eigenvalue estimator cannot see it — M_eff = 11.69 is exactly what a mean-driven estimator
returns for a family with one near-duplicate pair. Corroboration: the leave-one-out Fisher
null sd was 8.607 against the independent-uniform √48 = 6.928, a variance inflation factor
of 1.24 in sd terms and 1.54 in variance terms. Near-independence does not produce that.
The two GROUND cells are the likely pair (near-identical null moments under both schemes)
and they are also the two smallest `p_cell_cs`, so they may be carrying the entire residual
aggregate excess as effectively one test.

**3. The size figures still quote the shuffle null.** Per-cell rejection rates under the
better-specified null are 0.316–0.480 (median 0.400) against nominal 0.05, materially worse
than the 0.235–0.405 currently in the headline. The size finding is being under-reported.

Also unremarked: the circular shift *tightened* both GROUND cells' nulls (sd 7.40 → 6.71,
7.27 → 6.57) while widening nearly every other cell's. That asymmetry is why
GROUND×part_n_war got *more* extreme under the better null (p_cell 0.0420 → 0.0325) while
everything else got less. Given the degeneracy finding it is probably the near-constant-outcome
countries interacting differently with rotation than with shuffling, but it is currently
unexplained in the notebook.

---

## Task A — Recalibrate the omnibus tests on the circular-shift null

New subsection **2g**, after 2f. Reuses `permcs_df`; no DH calls.

Compute both asymptotic and permutation-calibrated Fisher and Simes on the
circular-shift per-cell p-values (`p_cell_cs`), calibrated against circular-shift
leave-one-out draws. Mirror the pass-3 construction exactly, substituting `_p1_cs` for
`_p1_2b` and `cs_df["p_cell_cs"]` for `sec2b_df["p_cell"]`.

Report side by side, both nulls:

- Fisher statistic, asymptotic p, permutation-calibrated p
- Fisher null mean and sd, plus the variance inflation factor against the
  independent-uniform reference (null mean should be ≈ 2M = 24, sd ≈ √48 = 6.928)
- Simes p and its permutation-calibrated p
- binomial and KS
- the count test p under each null, for context

Then this branching reading, on the circular-shift calibrated Fisher (`_fisher_cs_perm_p`):

- if `>= 0.10`: the aggregate picture is unambiguous. Under the better-specified null no
  aggregate diagnostic clears 0.05 (count p=0.0975 borderline, Fisher clear). State that
  the shuffle-null count excess was an artifact of a null that failed to preserve
  regressor persistence, and that the RQ2 null is clean at aggregate and per-cell level.
- elif `< ALPHA`: the aggregate excess strengthens under the better null. Report it as a
  genuine diffuse anomaly and do not claim the aggregate is clean.
- else: still borderline. Report all four aggregate diagnostics (both count tests, both
  Fisher calibrations) as a block and rest the conclusion on per-cell and multiplicity.

Verify and print the Simes identity under the circular-shift null too: Simes global p must
equal the smallest `q_bh_cs`. This is a free check on the second BH run.

Save to `tables/nb12/section2g_omnibus_both_nulls.csv` with one row per test and columns
for the shuffle and circular-shift values.

## Task B — Identify the near-duplicate pair and collapse it

Same subsection. Reuses the cached Z matrices.

1. Build the 12×12 correlation matrix of lag-1 Z under **both** schemes (`_p1_2b` and
   `_p1_cs`). Print the top five most-correlated pairs under each, with their r values.
   Confirm or refute that the max-|r| pair is GROUND×part_n_war and
   GROUND×part_n_extraterritorial. Do not assume it; report what the data says.

2. For the max-|r| pair, print: r under each scheme, both cells' null mean and sd under
   each scheme, both `p_cell` and `p_cell_cs`, both `n_units_dh`, and both `frac_zero_var`
   from the degeneracy table. The question being answered is whether the two cells are
   near-duplicates because they share the same degenerate country set.

3. Recompute the aggregate diagnostics with the pair collapsed to a single test, under the
   circular-shift null. Collapse by taking the more extreme (smaller) `p_cell_cs` of the
   two, giving an 11-cell family. Report: BH over 11 with the new smallest q; Fisher on 11
   with fresh permutation calibration over the same collapsed structure; the count test
   with observed and null both recomputed over 11 cells. If the aggregate excess is being
   carried by the pair, collapsing it should move these materially.

4. Also report the aggregate with **both** GROUND cells dropped entirely (10-cell family),
   as a bound. If the excess disappears under both collapse and drop, the residual anomaly
   is one degenerate treatment-outcome combination, not a lead-lag signal.

Branching reading on whether the collapsed-11 Fisher and count p both exceed 0.10:

- if both do: the residual aggregate excess is attributable to a single near-duplicate
  cell pair sharing a degenerate country set. Name it, state that it is one effective test
  rather than two, and note that its own `q_bh_cs` is far from significance.
- otherwise: the excess is not localised to the pair. Report the collapsed values honestly
  alongside the full-family ones and do not attribute.

Save the pair diagnostics and both collapsed aggregates to
`tables/nb12/section2g_pair_collapse.csv`.

## Task C — Explain the dispersion asymmetry between schemes

Same subsection, short. For each of the 12 cells compute `sd_ratio = cs_null_sd_Z / null_sd_Z`
and Spearman it against `frac_zero_var` and `n_units_dh` from the degeneracy table.

The hypothesis to test: cells with a high fraction of near-constant outcomes get *tighter*
nulls under rotation because rotation preserves each country's value multiset in temporal
order, so a degenerate country stays degenerate and contributes a stable (not explosive)
Wald statistic, whereas shuffling can place its few non-zero values adjacent and manufacture
spurious variance. Cells with well-behaved outcomes get *wider* nulls under rotation because
the preserved negative autocorrelation is itself what inflates DH.

Report the ratio table, both rho values, and a branching reading on whether
`rho(frac_zero_var, sd_ratio)` is negative at p < 0.10. If it is not, say the asymmetry is
observed but unexplained rather than fitting a story to twelve points.

## Task D — Promote the circular-shift size figures

String changes and one gate. No numbers move.

1. Everywhere the notebook states the calibrated size evidence as a headline — the Section
   2b size block, Section 5 item 2b, and the item 4 synthesis — lead with the
   circular-shift figures and give the shuffle figures as secondary:
   rejection rates 0.316–0.480 (median 0.400) against nominal 0.05, null mean Z +0.979 to
   +2.379, and note the shuffle values in parentheses as the serial-structure-destroying
   comparison.

2. Regate `size_ok` onto the circular-shift null, since that is now the reference:
   ```python
   size_ok = bool(n_miscentred_cs == 0 and _cs_rates.max() <= 0.12)
   ```
   where `n_miscentred_cs` counts cells with `cs_null_mean_Z > 0`. Print both the old
   shuffle-based value and the new one, and confirm Section 5 still takes the
   `not size_ok` branch. It should: 12/12 mis-centred and max rate 0.480.

3. Add a caveat to the degeneracy finding in Section 2b. The rho of +0.591 at p = 0.0429
   was one of three predictors tested, so Bonferroni over three gives 0.13 and the rank
   correlation alone is suggestive rather than established. Print that explicitly, and
   state that what carries the finding is the direct evidence — 63 of 192 countries (33%)
   with near-constant differenced outcomes in GROUND×part_n_war, and wald_max = 266.8 —
   not the correlation. Report the direct numbers as primary, the rho as supporting.

4. Add a one-line methods note where the degeneracy diagnostic prints: DH's internal
   `min_obs` filter counts observations, not variation, so a country contributing twelve
   zeros clears the filter and then produces an exploding Wald statistic. This is a general
   caveat for applying DH to sparse count outcomes, independent of this paper's findings.

## Task E — Extend the regression guard and add checks

Add to `FROZEN` (values established in pass 4, to be held from here):

| key | value | tol |
|---|---|---|
| `emp_p_lag1_cs` | 0.0975 | 5e-4 |
| `cs_null_count_mean` | 4.870 | 5e-3 |
| `shuffle_null_count_mean` | 3.554 | 5e-3 |
| `fisher_obs` | 37.665 | 5e-3 |
| `fisher_perm_p_shuffle` | 0.0705 | 5e-4 |
| `simes_obs` | 0.2024 | 2e-4 |
| `acf_observed` | -0.3286 | 5e-4 |
| `acf_shuffled` | -0.0232 | 5e-4 |
| `acf_circular` | -0.3113 | 5e-4 |
| `rho_frac_zero_var` | 0.591 | 5e-3 |
| `wald_max_ground_war` | 266.8 | 0.1 |
| `pcell_cs_ground_war` | 0.0325 | 5e-4 |
| `cs_bh_min_q` | 0.390 | 5e-4 |

New checks, continuing the existing numbering:

- circular-shift omnibus computed, all p-values finite and in (0, 1], table saved
- Simes identity holds under the circular-shift null (equals smallest `q_bh_cs`)
- Fisher null mean under both schemes within 1.0 of the theoretical 2M = 24 (validates the
  leave-one-out construction under both)
- variance inflation factor computed and reported for both schemes
- max-|r| pair identified and its correlation ≥ 0.90 under at least one scheme
- collapsed-11 and dropped-10 aggregates computed and saved
- `sd_ratio` diagnostic computed for all 12 cells
- `size_ok` gated on the circular-shift null, both values printed
- no shuffle-only size figure remains in any headline position: scan the notebook source
  for `"0.235"` and `"0.405"` and require that every surviving occurrence sits in a line
  that also mentions the circular-shift comparison or is explicitly labelled as the
  shuffle null

Report the new total.

## Task F — Section 5

Add item 2g reporting the recalibrated omnibus and the pair-collapse result. Rewrite item
4's `_agg` sentence from the Task A branch outcome rather than the pass-4 count-only
condition. Keep the construction runtime-computed.

Add a final line stating plainly what the RQ2 null now rests on, in one sentence, using
the circular-shift figures.

---

## Report back

Beyond the standard protocol items:

- The omnibus comparison table, both nulls, asymptotic and calibrated.
- Fisher null mean and sd under both schemes, and both variance inflation factors.
- Top five correlated pairs under each scheme, with r values.
- The max-|r| pair's full diagnostic row.
- Collapsed-11 and dropped-10 aggregates: BH smallest q, Fisher p, count p.
- The `sd_ratio` table and both Spearman rho values.
- `size_ok` under both gates.
- Which branch fired for Tasks A, B, and C, verbatim.
