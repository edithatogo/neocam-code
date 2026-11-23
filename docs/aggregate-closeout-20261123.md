# Aggregate analysis: recommendations and closeout

Closed for now on 23 November 2026 at the owner's request. The aggregate
implementation, analysis, release-format reconciliation and reviewed public
promotion are complete. The remaining evidence, editorial and private hosted
execution work is assigned to the issues below. Closure of this implementation
round does not assert a merge, full release acceptance or clinical validation.

Private authoring: [neocam PR #12](https://github.com/edithatogo/neocam/pull/12),
dependent on the retained private research PR #4. Public delivery:
[neocam-code PR #11](https://github.com/edithatogo/neocam-code/pull/11).
The original private repository remains the authoring source. The public code
repository retains separate history; `neocam-public` is a historical snapshot.

## Every recommendation and its disposition

| Recommendation | Delivered implementation or record | Remaining issue, if applicable |
|---|---|---|
| Start with aggregates; unit records are optional | Configuration-driven decision scenarios and [update rules](aggregate-multiscale-analysis.md) | [CHHHS refinement](https://github.com/edithatogo/neocam/issues/14); [wider calibration](https://github.com/edithatogo/neocam-code/issues/12) |
| Use evidence as currently reported and express its uncertainty | Primary adjusted OR 0.48 and CI 0.26–0.90; log-scale distribution in [configuration](../config/aggregate-analysis.json) | Further source activation belongs to [calibration](https://github.com/edithatogo/neocam-code/issues/12) |
| Preserve evidence scales and dependence | Four estimates registered in the [ledger](../data/aggregate/public-inputs.json); the Haynes OR is active. Albritton, Maddox and stabilisation-time estimates are defined but inactive. Overlapping cohorts are identified. | Native estimand, outcome mapping, probability bounds and cohort dependence must be specified before activation in [calibration](https://github.com/edithatogo/neocam-code/issues/12) |
| Separate sampling uncertainty from applicability and model structure | Reported, transportability, attenuated, skeptical and exact-null scenarios; initial/eventual endpoint and rescue alternatives | [Manuscript interpretation](https://github.com/edithatogo/neocam/issues/15) |
| Include deterministic and probabilistic sensitivity | Central results, 19 perturbations, paired PSA, Monte Carlo uncertainty, policy decisions, regret and cost-only EVPI | Repeat the existing analyses for accepted inputs in [CHHHS refinement](https://github.com/edithatogo/neocam/issues/14) or [calibration](https://github.com/edithatogo/neocam-code/issues/12) |
| Distinguish relevant comparators | Telephone, retained pilot and conditional expansion policies; equivalent device effects and hypothetical eligibility are explicit assumptions | Current usable equipment and capacity in [CHHHS refinement](https://github.com/edithatogo/neocam/issues/14) |
| Keep resource, payer and cash consequences distinct | Seven-year schedules; 0/25/50/100% transport-resource cash-capture scenarios; programme costs and break-even thresholds | Actual charges, fixed/variable terms and budget holders in [CHHHS/fiscal refinement](https://github.com/edithatogo/neocam/issues/14) |
| Support all five geographic levels | Named local/regional portfolios and explicitly illustrative state/country settings; see the scope table below | [Geographic calibration](https://github.com/edithatogo/neocam-code/issues/12) |
| Use relevant public documentation, including RSQ | [Public evidence audit](public-inputs-20261123.md), source ledger and query provenance; records, IDs, age, modes and payment responsibilities remain distinct | Map new public estimates to named inputs under [calibration](https://github.com/edithatogo/neocam-code/issues/12) |
| Account for service and equipment changes | Weipa/Cooktown information is recorded as contextual evidence; it does not silently overwrite the historical baseline | Dated comparator, equipment and activity mapping in [calibration](https://github.com/edithatogo/neocam-code/issues/12) |
| Use available private information and specify useful further queries | Private manuscript aggregates reviewed; a private specification distinguishes inpatient events from eligible consultation episodes. No new query of the unavailable workbook is claimed. | [CHHHS refinement](https://github.com/edithatogo/neocam/issues/14) |
| Add data only where it can improve a decision | Prioritise eligible episodes/contacts, transfer timing, mode/tasking/charges and usable equipment/capacity. Add broad case-mix groups only when decision-relevant. | [CHHHS refinement](https://github.com/edithatogo/neocam/issues/14); [calibration](https://github.com/edithatogo/neocam-code/issues/12) |
| Reuse existing dependencies and projects | Existing model, budget functions and voiage 3.1.0 reused; no runtime dependency added. The guide records conditional mchs export and workforce-converter reuse. | Routine updates stay in [private dependency dashboard](https://github.com/edithatogo/neocam/issues/1) and [public dependency dashboard](https://github.com/edithatogo/neocam-code/issues/2) |
| Keep updates fast and reproducible | Fresh 20,000-draw runs took 15.451 seconds privately and 13.090 seconds publicly in the recorded environment. The small configuration and [update guide](aggregate-multiscale-analysis.md) define the workflow. | No additional framework or orchestration track |
| Preserve historical results and validate new outputs | Existing artifact checker now verifies the fresh aggregate release; the historical ReportLab fixture is explicit. All 51 retained v13 files in each remote were unchanged. | Current checks remain required for a future accepted increment |
| Author privately, then promulgate selectively | Explicit file promotion, six numerical/input files identical, independent public manifests and separate Git ancestry | [Promotion receipt](../verification/aggregate-multiscale-20261123/release-promotion.json) |
| Refresh manuscript and decision communication deliberately | Verified results report is delivered; original manuscripts and author edits are retained | [Private manuscript and briefs](https://github.com/edithatogo/neocam/issues/15) |
| Record actual assurance and unresolved gates | Public release passed all five hosted workflows. Private workflows failed without reported execution steps; cause was not exposed. | [Private Actions execution](https://github.com/edithatogo/neocam/issues/13) |

## Decision use at each level

| Level | Appropriate current use | Next useful aggregate input |
|---|---|---|
| CHHHS district | Conditional deployment decision, resource effects and programme budgets | Matched eligible episodes/contacts and transfers; usable equipment/capacity; actual mode/tasking/charges |
| CHHHS–TCHHS region | Combined-network and shared-capacity scenarios | Current referral paths, activity and equipment. Overlapping portfolios are not additive. |
| Queensland | Illustrative 33-spoke expansion scenario | Covered eligible facilities, current capability, consultation denominators, routing and cost ranges |
| Australia | Explicit ten-facility, 250-contact transferability example | Named jurisdiction/network populations, comparators, activity, baseline risk and costs |
| International | Explicit ten-facility, 250-contact example with declared reference-AUD cost overrides | Country-specific pathways, quantities, wages, price year, currency/conversion and financing assumptions |

The [results report](aggregate-results-20261123.md) contains the numerical decision
results and uncertainty. In CHHHS, the reported-effect expansion scenario has mean
annual resource savings of AUD 80,457 versus telephone and AUD 48,450 versus retaining
the pilot. The probability of positive savings is 88.7%; conditional probability
optimal is 85.5%. These are modelled resource consequences. Gross programme budgets
include the retained pilot and replacements; an incremental funding request must
account for expenditure already funded. Cost-only EVPI is limited to its declared
policy set and does not measure the whole value of clinical research.

## The four follow-ups

| Issue | Resume trigger and completion criterion | Ownership/boundary |
|---|---|---|
| [neocam #13 — private hosted execution](https://github.com/edithatogo/neocam/issues/13) | Inspect actual failure evidence, correct its cause and obtain executed, passing private protected checks at an identified commit. | Engineering delivery; public success is separate evidence. |
| [neocam #14 — CHHHS aggregate/fiscal refinement](https://github.com/edithatogo/neocam/issues/14) | An available defined aggregate return can inform a named parameter/comparator. Reconcile units and uncertainty, rerun existing scenarios, and report whether the decision changes. Record unavailable inputs and their scenario consequences. | Existing fiscal track and owner retained; start with pooled aggregates. |
| [neocam #15 — manuscript and decision briefs](https://github.com/edithatogo/neocam/issues/15) | Deliberately refresh tables, narrative and intended documents from the identified verified release; check citations, numerical agreement and rendering. | Private manuscript owner and author originals retained. |
| [neocam-code #12 — geographic/evidence calibration](https://github.com/edithatogo/neocam-code/issues/12) | A named decision has useful source-backed aggregate inputs. Map and label them, retain uncertainty scenarios and produce a fresh verified result. | Private-first authoring; public sources and approved projections only. |

An unavailable local aggregate is recorded as a parameter limitation with a stated
scenario consequence. It does not automatically expand the task to a registry or
patient-level extraction. A future refinement ends with its defined decision and
evidence record; it does not require every uncertainty to disappear.

## Delivery and restart

The accepted public PR-scope software snapshot is
`60205a54a01f456543b0af826f2b0b62f623ab80`. Its five workflows passed. The corresponding
private release implementation is `bd5506a6b28ba3311ebe547dc399cd4e5414cc9f`, followed by
documentation reconciliation. Later documentation commits retain their own checks;
historical receipts are not silently extended to new commits.

This closeout changes documentation and tracking only. The calculation inputs,
generated values, dependency lock and existing release seals remain unchanged.
The implementation track is closed for now; issues above remain open and the fiscal
track remains active. Both delivery PRs remain drafts and unmerged. No automatic
follow-up work is scheduled.

On resumption, read this index, the relevant issue and the [update guide](aggregate-multiscale-analysis.md).
Confirm current repository/PR state and the private source before changing an input.
Choose a fresh output/evidence location, preserve the declared pytest plugins, and
record actual local and hosted outcomes. Do not reuse the CLI's historical default
evidence directory for a new qualification run.
