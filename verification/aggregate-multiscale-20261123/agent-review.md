# Aggregate analysis: bounded agent review

Date: 23 November 2026.

## Scope and result

A separate software/methods agent reviewed the new aggregate runner,
configuration and focused tests after implementation by another agent. The
public input ledger was checked for consistency with the runner's mappings by
its author. This is agent advisory review, not independent human clinical
validation, publication approval or full software acceptance.

**One substantive defect was identified and corrected. No other material defect
was found within this bounded review.**

Reviewed `scripts/analyse_aggregate.py`, `config/aggregate-analysis.json`,
`tests/test_aggregate_analysis.py`, `data/aggregate/public-inputs.json` and
`docs/public-inputs-20261123.md`. Inspected the relevant integration behavior in
`src/activity.py`, `src/deployment.py`, `src/pathways_v6.py`,
`src/audit_v7.py`, `src/statewide.py` and `scripts/analyse_refinements.py`.

## Finding and correction

The initial shared sensitivity scenarios used absolute cost overrides while
being named “half” or “double”. This was incorrect for the international setting,
whose reference equipment cost is AUD 5,000 and air multiplier is 0.5:

| Original scenario | Intended comparison | Original result in international setting |
|---|---|---|
| `air_cost_half` | Half the setting's air cost | Multiplier remained 0.5: no change. |
| `air_cost_double` | Double the setting's air cost | Multiplier became 2: four times baseline. |
| `capital_double` | Double the setting's equipment cost | Cost became 20,000: four times baseline. |

The correction adds `parameter_factors` and applies them in `_inputs` after
setting and explicit scenario overrides. The three cases now use factors 0.5,
2 and 2 respectively. Absolute overrides remain explicitly distinguished in the
configuration interpretation. Review confirmed the factor calculation and its
ordering. `test_relative_capital_scenario_scales_each_setting` verifies doubled
purchase capital for both national and international settings across policies.

## Methods checks

- The primary effect uses the reported OR 0.48 and CI 0.26–0.90, reconstructing
  uncertainty on the log scale. Reported-estimate uncertainty and assumed
  transportability/attenuation scenarios are separately identified. Possible
  adverse associations are not clipped out; the null OR is exactly one.
- Effect scenarios share non-effect sampled arrays and structural draws.
  Contacts and clinical episodes remain separate; repeat-contact scenarios
  preserve workload while changing the episode denominator.
- Aggregate hypothetical settings create the declared number of facilities,
  preserving per-facility installation and readiness costs. Named portfolio
  counts are checked rather than collapsing a network into one facility.
- Resource savings and cash expenditure remain separate outputs. Cash rows
  describe assumed capture of transport-resource offsets, with explicit
  fractions and break-even fractions; they do not assert invoice savings.
- National and international settings are labelled hypothetical networks in
  reference AUD, not calibrated national totals or currency conversions.
  Overlapping named portfolios are not additive.
- The source ledger is provenance/context unless explicitly mapped. Maternal
  counts, total births and RSQ diagnostic records do not become eligible
  neonatal contact counts. Other published effect distributions retain their
  native units and are not silently inserted into the OR kernel.

## Focused verification inspected

The implementing agent reported **13 focused tests passed in 2.49 seconds**,
plus passing Ruff, ty and basedpyright checks after the final test annotation.
The reviewer inspected the added relative-capital test, existing episode/contact
and paired-draw tests, and cash-capture/provenance assertions. The reviewer did
not rerun the full suite; this record does not claim full or hosted assurance.
Retained analysis execution and final delivery evidence are separate records.

## Assumptions that remain explicit

1. Haynes measures transfer within 24 hours. Applying the association to eventual
   transfer is a model extrapolation; the initial-endpoint sensitivity does not
   establish clinical equivalence of those endpoints.
2. Baseline contact activity, case mix, transfer probabilities and several costs
   remain labelled model assumptions. CHHHS matched aggregates can refine them;
   patient-level data are not required to start that refinement.
3. Cash-capture fractions are scenarios over modelled transport-resource offsets.
   Current tariffs, cancellations, charged units and inter-organisational fiscal
   settlement remain unresolved inputs.
4. Country settings remain transferability examples. Country-specific service
   coverage, activity and costs are needed before claiming national estimates.
5. Weipa/Cooktown service facts and the other newly recorded public aggregates
   are available scenario evidence; this ledger does not itself update the
   historical baseline or retained manuscript tables. Reported associations
   do not establish mortality, safety or QALY benefits.

## Reviewed source identities

These hashes identify the reviewed files at the end of this bounded review.
Later edits require the corresponding review or check to be reconciled.

| File | SHA-256 |
|---|---|
| `scripts/analyse_aggregate.py` | `d38120ed01da505ec87d3f92125f87be18ca22c8318debd89f0faa9a125f986f` |
| `config/aggregate-analysis.json` | `5d9f4cc95fad647f27f92eba1b714d69d76459944b836d2b2a6b44cbc446bf7f` |
| `tests/test_aggregate_analysis.py` | `207185674e6484e3140dae62ae6473a2cd13893742d86e6bc3072bff49e89fb7` |
| `data/aggregate/public-inputs.json` | `7fe5017e09aa4d16dd4d74b7f87288e3eea34db47b70c2be8621c0c82599e590` |
| `docs/public-inputs-20261123.md` | `7d41dba99edc0a5f3f866a540a9e3062e093a1bab80a095d4ab110326a443be8` |
