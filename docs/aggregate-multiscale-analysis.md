# Updating the aggregate analysis

The private `neocam` repository is the authoring source; `neocam-code` receives the
reviewed public-safe delta. `neocam-public` is a historical snapshot. This increment
adds aggregate decision scenarios through the existing model and does not require
unit-level data or a new registry.

## Quick update

1. Update a source-backed row in `data/aggregate/public-inputs.json` and its applicable
   scenario in `config/aggregate-analysis.json`. Record the population, unit, period,
   estimate/interval and whether uncertainty is reported or assumed. Context-only
   evidence must not be described as an executed model input.
2. Choose a fresh output directory and set `current_output` in
   `config/assurance.json` to it before running. Keep `historical_report_output` fixed
   for the retained report schema. Run the focused check and analysis in the frozen
   environment, then create the standard release seal as the last source-bound step:

   ```sh
   uv run --frozen --group assurance --extra research python -m pytest -q tests/test_aggregate_analysis.py
   uv run --frozen --extra research python -m scripts.analyse_aggregate \
     --config config/aggregate-analysis.json --output outputs/aggregate-NEXT
   uv run --frozen python -m quality.artifacts seal --output outputs/aggregate-NEXT
   uv run --frozen python -m quality.artifacts verify
   ```

   The runner writes an analysis manifest. If using its standalone verifier, run it
   before the final seal: the final `release_manifest.json` is the authoritative
   directory check and pins the inner manifest too. Do not reseal historical outputs.

3. Read deterministic results, sensitivity, PSA, decisions and budget schedules together.
   Reconcile the exact output/source identities and applicable assurance before delivery.
   Retained v13 results and manuscript tables keep their original meaning and values.

The published effect and reported confidence interval are primary in the new analysis.
Transportability and attenuated/skeptical/null effects remain explicit scenarios.
Use matched numerator/denominator aggregates for baseline rates; preserve mothers,
babies, episodes, contacts, transfers and legs as distinct units. Do not sum overlapping
portfolios or label a payer perspective as a wider population estimate.

The [23 November results](aggregate-results-20261123.md) provide the executed
20,000-draw example and show which assumptions change the CHHHS decision.

## Reuse decisions

The runner calls the existing configuration, deployment, activity, cash-budget and
voiage decision functions. NumPy and the standard library handle the small input
tables; the existing optional Polars dependency remains available for larger aggregates.
No runtime dependency or new numerical model is introduced.

The owner's [mchs project](https://github.com/edithatogo/mchs) can supply a validated
aggregate funding export when relevant; its current Python/pandas path and unverified
2026 pricing parity do not justify adding it to this runtime. The existing
[workforce rate converter](https://github.com/edithatogo/microcosting_healthworkforce/blob/895115fc038b63d09b3b56194f29cb95c05a05b9/microcosting_healthworkforce/rate_converter.py)
is the reuse point if a later update requires salary-to-hourly-rate conversion.
Actual salary rates still need a source. The installed voiage 3.1.0 already handles
cost-only EVPI, regret and tie-aware policy selection in this increment.

## Choose the next data addition

Add data when it changes the eligible population, current comparator, a material cost
or effect, or the policy preferred under uncertainty. Public perinatal/RSQ inputs are
the starting point. CHHHS aggregate counts may refine demand, routes, mode mix or
costs; record their definition, period, missingness and permitted use. Query existing
private material for a named uncertainty rather than building a broad new collection.
Actual tariffs, charged units and fixed/variable payment terms refine the existing
fiscal track. A distribution can express uncertainty without waiting for perfect data.

National and international settings can use public aggregates and explicit adaptation
assumptions. Local clinical data are an opportunity to improve precision and validity,
not a prerequisite to publishing useful conditional decisions at each level.

## Private-to-public promotion

Commit and review the private source first. Record the explicit allowed paths and
their hashes, then copy those files onto the current public history. Document any
source-withheld projection and check numeric parity for shared inputs. Public commits
must not merge or cherry-pick private history. Keep unpublished manuscripts, source
originals, private locators, corporate assets and unreleased local aggregates private.
Record private/public commits or PRs and actual local/hosted checks separately; never
inherit historical acceptance as acceptance of new bytes.

Manuscript/report regeneration is a deliberate follow-up after the new results are
verified. This update does not claim refreshed Word/PDF files or empirical validation.

## Closeout and issue references

This implementation round is closed for now. The
[complete recommendation/issue index](aggregate-closeout-20261123.md)
maps delivered work and the four open follow-ups. Future data additions,
manuscript work and private hosted qualification remain explicitly tracked.
