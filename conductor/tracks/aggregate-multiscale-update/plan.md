# Aggregate multiscale update

Authority: owner direction, 23 November 2026. This implementation round is closed
for now. The analysis, release-format reconciliation and private-first public
promotion are complete. Public PR #11 passed all five workflows at its recorded
release snapshot. Private execution, optional data calibration and manuscript
refresh remain separately tracked. Preserve existing fiscal ownership and
historical outputs. See the [complete recommendation/issue index](../../../docs/aggregate-closeout-20261123.md).

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
- [x] Promote the explicit reviewed file delta onto the current `neocam-code` branch
  history; verify hashes/numerical parity and record public PR checks separately.
- [x] Reconcile actual outputs, checks and remote identities. Queue deliberate manuscript
  table/report refresh from verified new results; do not claim new Word/PDF delivery.

## Executable next actions

```sh
uv run --frozen --group assurance --extra research python -m pytest -q tests/test_aggregate_analysis.py
uv run --frozen --extra research python -m scripts.analyse_aggregate \
  --config config/aggregate-analysis.json --output outputs/aggregate-NEXT
```

Use a fresh output directory on later runs. Expected outputs: `deterministic.csv`,
`scenarios.csv`, `decisions.csv`, `sensitivity.csv`, `budgets.csv` and
`resolved_inputs.json`. The initial 20,000-draw run took 12.803 seconds; the fresh release run took 15.451 seconds. Actual checks and source identities
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

## Delivered state

Private PR #12 supplies the reviewed implementation; public PR #11 receives the
reviewed delta on separate history. The release promotion verified 23 shared files, including six numerical/input
artifacts. Subsequent documentation changes have separate closeout checks. Source code, declared parameters and
numerical outputs are verified within the retained local-check scope.

- [x] Reconcile the current release using the existing artifact checker, a fresh
  aggregate output directory and an explicit historical ReportLab fixture. Preserve
  all retained v13 artifacts and seals. Validate the inner analysis manifest before
  the final standard release seal, which includes that inner manifest as an artifact.
- [x] Record public PR-scope success at `60205a54a01f456543b0af826f2b0b62f623ab80`;
  this does not claim a merged-main full-release attestation.
- [x] Close the implementation round and cross-reference every recommendation.
- [ ] Resolve private hosted execution through [neocam #13](https://github.com/edithatogo/neocam/issues/13) before private merge.

## Follow-ups retained outside active implementation

| Issue | Acceptance boundary |
|---|---|
| [neocam #13](https://github.com/edithatogo/neocam/issues/13) | Diagnose the actual execution failure and obtain executed, passing private required checks. |
| [neocam #14](https://github.com/edithatogo/neocam/issues/14) | Map targeted CHHHS/fiscal aggregates to named inputs and report their decision impact; preserve the fiscal owner. |
| [neocam #15](https://github.com/edithatogo/neocam/issues/15) | Refresh manuscript/briefs from the verified release, preserving author originals and checking tables, citations and rendering. |
| [neocam-code #12](https://github.com/edithatogo/neocam-code/issues/12) | Calibrate a named regional/state/country decision with useful aggregates, uncertainty and a fresh verified result. |

The closeout index contains the full five-level scope, reported-evidence activation
rules, data priorities, source boundaries and restart instructions. The fiscal
evidence track remains open. No further work is scheduled by this closeout.
