---
description: Apply a specification-driven patch pass to NB12 under the project's locked-constant and regression-guard protocol
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(python *), Bash(jupyter *), Bash(git *)
---

# NB12 patch protocol

Read the pass specification at `$ARGUMENTS` and execute it under the standing rules below.
The pass spec supplies the tasks. This file supplies the protocol. Where they conflict,
the pass spec wins on *what* to do and this file wins on *how*.

## Repository facts

- Project root: `D:\post graduate\assignments and projects\sem 3\BDA\PeaceMakers' Arms Race\version 2`
- Notebook under edit: `notebooks/12_rq2_power_analysis.ipynb`
- Tables go to `tables/nb12/`, figures to `figures/nb12/`. There is no `outputs/` directory.
- Caches live in `data/interim/`.
- Everything under `src/` is READ ONLY unless the pass spec explicitly says otherwise.

## Editing method

Edit the notebook via an `nbformat` transform script, not a builder script and not by
hand-editing JSON. Every edit must be anchored on an exact source substring, and the
script must `assert` that each anchor matched **before** writing anything back. If any
anchor fails, abort without writing and report which anchor missed.

Do not keep the transform script as the source of truth. The notebook is the artifact;
the script is disposable. Assume the scratchpad will be wiped between sessions.

## Locked by default

Never change these unless the pass spec names them explicitly:

- `dumitrescu_hurlin_fast` and every call signature into it
- `SEED`, `ALPHA`, `N_SIM`, `N_PERM`, `N_PERM_2B`, `N_PERM_CS`, `MAX_OBSERVED_CCF`,
  `PLACEBO_THRESHOLD`, `MIN_OBS_LAG1`, `DEGEN_VAR_TOL`
- Any existing cache in `data/interim/`. All pre-existing caches must report **HIT**.
  A MISS means the panel fingerprint moved: stop and report rather than recomputing.
- Every number already printed by the notebook. Additive passes add columns, sections,
  and diagnostics; they do not move existing results.

## Seed streams

Each new randomised procedure gets a disjoint offset in `np.random.default_rng([SEED, offset + i])`.
Allocated so far: 100000 shuffle 36-cell, 500000 shuffle lag-1, 700000 circular shift,
800000 ACF check, 900000 dependence check. Pick an unused block and record it in a check.

## Regression guard

The `FROZEN` dict in the checks block is authoritative. Extend it with any value the
current pass establishes; never loosen or remove an existing entry. If the guard reports
drift, **stop before committing and before regenerating any export**, then report which
values moved and by how much.

## Sanity checks

Every task adds at least one check. Checks are pass/fail on completeness and internal
consistency, not on whether a result came out favourably: a diagnostic that reveals the
pipeline misbehaving is a reported finding, not a failing gate. Manual attestations are
forbidden — if a check cannot be verified programmatically, make it scan the notebook
source or set it `False`. Report the full check list and the `n/n` total.

## Branching readings

Where the pass spec provides `if/elif/else` branches that select an interpretive string,
never hardcode which branch fires. Compute the condition, let it fire, and report the
resulting string verbatim — including when it contradicts the hypothesis that motivated
the task. A negative result is the deliverable, not a failure.

## Export and commit

1. Restart the kernel.
2. `jupyter nbconvert --to notebook --execute --inplace notebooks/12_rq2_power_analysis.ipynb`
3. Export HTML. The PDF toolchain (pandoc + LaTeX, and Playwright) is absent on this
   machine — do not retry PDF unless the pass spec says it has been installed.
4. Stage only the files this pass touched, enumerated explicitly. Never `git add -A`;
   the working tree carries unrelated prior-session work.
5. Commit with a message describing only this pass.

## Report back

- Cache status and wall time for every cache.
- Every table and scalar the pass spec asks for, in full.
- Which branch fired for each branching reading, verbatim.
- The regression guard's drift list.
- Every check line and the total.
- Any deviation from the spec, disclosed with the reason.
