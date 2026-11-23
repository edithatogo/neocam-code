# Aggregate multiscale update

Authority: owner direction, 23 November 2026. Status: implementation and the new analysis are complete;
focused checks and agent review passed. Private source is committed in PR #12; public validation is complete and its draft PR is pending. Preserve existing fiscal-track
ownership and historical outputs.

## Scope

Use reported evidence and available aggregates to inform CHHHS, CHHHS–Torres and
Cape, Queensland, Australian and international decision scenarios. The primary new
effect scenario uses the published estimate and confidence interval directly.
Transportability, attenuated, skeptical, null, timing and fiscal scenarios remain
separate. Local CHHHS aggregate data can refine named parameters; unit-level data,
a prospective registry and perfect fiscal information are not entry requirements.

Reuse `src.configuration`, the current pathway/deployment kernel, existing sampling,
NumPy and voiage. Add no new modelling framework. Add an input only if it defines
the decision population/comparator, informs a material parameter, or tests a decision
that changes under uncertainty. Preserve the distinction between contextual data and
inputs that actually alter a calculation.

## Ordered tasks

- [x] Reconcile this scope, the current research parent and the public promotion route.
- [x] Record useful public/RSQ estimates in `data/aggregate/public-inputs.json`, with
  units, data periods, provenance and uncertainty; reconcile service/equipment changes.
- [x] Implement `scripts/analyse_aggregate.py` and `config/aggregate-analysis.json`
  as a thin adapter over the current model. Keep published sampling uncertainty
  separate from cross-setting assumptions and preserve shared draws across comparisons.
- [x] Generate central deterministic results, deterministic sensitivity, scenario PSA,
  decision summaries and budget schedules into a new directory; do not overwrite v13.
- [x] Verify probability bounds, denominator consistency, matched effects/scenarios,
  outcome/resource conservation and reproducibility with focused checks; run applicable
  repository assurance and retain actual command/results without inheriting old passes.
- [x] Review and commit the private increment; open a dependent private PR against
  `codex/consolidated-private-packet`.
- [ ] Promote the explicit reviewed file delta onto the current `neocam-code` branch
  history; verify hashes/numerical parity and record public PR checks separately.
- [ ] Reconcile actual outputs, checks and remote identities. Queue deliberate manuscript
  table/report refresh from verified new results; do not claim new Word/PDF delivery.

## Executable next actions

```sh
uv run --frozen --group assurance --extra research python -m pytest -q tests/test_aggregate_analysis.py
uv run --frozen --extra research python -m scripts.analyse_aggregate \
  --config config/aggregate-analysis.json --output outputs/aggregate-20261123
```

Use a fresh output directory on later runs. Expected outputs: `deterministic.csv`,
`scenarios.csv`, `decisions.csv`, `sensitivity.csv`, `budgets.csv` and
`resolved_inputs.json`. The 20,000-draw run completed in 12.803 seconds. Actual checks and source identities
are in `verification/aggregate-multiscale-20261123/focused-checks.json`; results are
summarised in `docs/aggregate-results-20261123.md`. Full release acceptance is separate.

## Acceptance and remaining evidence

Each scenario declares geography, population/activity basis, comparator, perspective,
effect/endpoint, cost basis and source evidence. National/international scenarios may
be illustrative and still useful; labels must identify what is calibrated. No pooled
birth total is silently substituted for a consultation denominator, and overlapping
portfolios are not summed. Missing/suppressed counts differ from observed zero.

Published intervals parameterise sampling uncertainty. Judgement-based distributions
are labelled; no sample size, tariff, causal effect or private publication right is
invented. Present resource offsets, budget transfers and expenditure separately.
The existing fiscal evidence task stays open for actual charging/cash capture.

Private authoring and public promotion use one reviewed delta. No private Git history,
manuscript, patient record, source original, private locator or unreleased local
aggregate is carried to public code. `neocam-public` is not maintained as a third copy.
Follow the [update guide](../../../docs/aggregate-multiscale-analysis.md).
