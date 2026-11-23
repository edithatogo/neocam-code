# Aggregate decision analysis: 23 November 2026

The new analysis uses the published transfer association as its primary effect
distribution, with explicit alternatives for transportability and model structure.
The complete 20,000-draw configuration ran in 12.803 seconds in the recorded
environment. It reuses the current model and voiage; no runtime dependency was added.

Sources: [configuration](../config/aggregate-analysis.json),
[resolved inputs](../outputs/aggregate-20261123/resolved_inputs.json),
[execution receipt](../verification/aggregate-multiscale-20261123/focused-checks.json),
and [agent review](../verification/aggregate-multiscale-20261123/agent-review.md).

## Primary conditional decisions

Annual health-system resource savings below are relative to telephone-only care.
The named portfolios overlap and must not be added. The decision set includes
telephone, retention of existing pilot equipment and conditional expansion options.
Equivalent clinical effects and hypothetical eligibility of expansion devices are
assumptions, so the ranking is not an observed device-effect comparison.

| Setting | Facilities | Policy with highest expected resource saving | Mean annual saving, reference AUD | Probability optimal within this decision set |
|---|---:|---|---:|---:|
| Existing pilot | 3 | Retain pilot equipment | 32,007 | 93.7% |
| CHHHS | 10 | Retain pilot; expand with OBSBOT scenario | 80,457 | 85.5% |
| CHHHS and TCHHS | 14 | Retain pilot; expand with OBSBOT scenario | 79,428 | 78.9% |
| Illustrative Queensland spokes | 33 | Retain pilot; expand with OBSBOT scenario | 877,832 | 95.2% |
| Australian transferability example | 10 assumed | OBSBOT expansion scenario | 220,197 | 94.9% |
| International transferability example | 10 assumed | OBSBOT expansion scenario | 163,825 | 95.1% |

Source: [decision table](../outputs/aggregate-20261123/decisions.csv), base scenario,
reported effect, probabilistic analysis, conditional expansion and health-system
perspective. The Australian and international rows are illustrative networks with
250 annual contacts each; they are not national totals. International cost overrides
remain reference-AUD scenarios, with no exchange-rate or purchasing-power conversion.

For CHHHS, the mean improvement from expansion over retaining the pilot alone is
AUD 48,450 per year. The expansion-versus-telephone PSA has a 95% simulation
interval of approximately minus AUD 25,329 to plus AUD 281,184, and an 88.7%
probability of positive resource savings. Its mean saving has Monte Carlo standard
error AUD 565. The expected reduction is 12.9 eventual transfers per year under
the declared endpoint extrapolation. These are model outputs, not observed effects
or cash receipts. Cost-only annual EVPI across the conditional CHHHS policy set is
AUD 2,073; it is not a total value for all possible clinical research.

## What changes the CHHHS conclusion

| Effect or structural scenario | Mean annual resource saving, AUD | Probability of positive resource saving |
|---|---:|---:|
| Reported association and interval | 80,457 | 88.7% |
| Additional transportability uncertainty | 78,616 | 81.1% |
| Half the reported log effect, with transportability uncertainty | 23,112 | 58.4% |
| Skeptical association centred at no effect | -35,551 | 23.1% |
| Exact null effect | -35,735 | 0.0% |
| Two contacts per episode, holding contact workload fixed | 22,361 | 67.5% |
| Initial rather than eventual endpoint mapping | 72,900 | 87.1% |
| Additional rescue probability of 5 percentage points | 51,453 | 77.5% |

Source: [scenario table](../outputs/aggregate-20261123/scenarios.csv), CHHHS OBSBOT
expansion, `net_saving`. All non-effect assumptions retain their declared priors.
The effect is the reported adjusted association OR 0.48, 95% CI 0.26–0.90;
log-scale standard error is 0.3167635542. The study's outcome is transfer within
24 hours after consultation. Eventual transfer requires the explicit mapping
assumption and later-transfer scenarios. The log-normal approximation reflects
rounding of the published point estimate and limits. No mortality or QALY benefit
is inferred. The other reported evidence parameters are in the
[public input ledger](../data/aggregate/public-inputs.json).

## Cash implications

The deterministic CHHHS expansion scenario requires AUD 48,541 first-year programme
cash expenditure, including AUD 31,500 for seven new installations, and AUD 146,705
over five years. These include the retained pilot and the modelled replacement
schedule. They are not the incremental cost above an already funded pilot budget.

The [cash table](../outputs/aggregate-20261123/budgets.csv) tests 0%, 25%, 50% and
100% capture of the modelled transport-resource offset. At the reported point
estimate, five-year net expenditure is respectively AUD 146,705, AUD 41,630,
minus AUD 63,446 and minus AUD 273,598. First-year break-even requires capture of
57.7% of that all-mode resource offset. The corresponding five-year threshold is
34.9%, with constant activity and the stated replacement schedule.

These capture fractions are financial scenarios, not measured invoice savings.
The public RSQ directive establishes relevant payment responsibilities but does
not provide neonatal tariffs or cancellation charges. Actual CHHHS mode, tasking
and invoice aggregates would refine this part of the decision first.

## Refresh and evidence status

Update the small configuration and rerun into a fresh output directory using the
[update guide](aggregate-multiscale-analysis.md). The outputs include 30 central
deterministic rows, 570 deterministic sensitivity rows, 3,120 PSA metric summaries,
2,240 decision rows and 840 annual cash-scenario rows. The seven output files have
a verified source and artifact manifest. Thirteen focused numerical tests and the
recorded strict static checks passed; broader repository checks are recorded in
the delivery reconciliation rather than inferred from historical receipts.

This increment is a draft scientific update. Existing v13 output bytes and their
historical manifests are retained. Because the existing release gate inventories
all current data/configuration files, the new inputs change its dependency set;
the old manifests therefore do not attest to this increment. Release acceptance
requires explicit reconciliation on the complete repository. This does not change
the new run's separately verified inputs and outputs.
