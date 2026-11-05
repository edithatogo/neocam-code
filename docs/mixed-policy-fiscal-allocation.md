# Who uses the resources under each mixed policy?

The v13 refinements compare each deployment with telephone in the same portfolio and activity scenario. The tables below distinguish the service using a resource from the organisation paying for it. “Unknown” means the retained evidence does not identify the budget holder or its share. Zero means a modelled incremental amount of zero.

| Policy | Origin provider and equipment | Consulting hub | Destination and retrieval |
|---|---|---|---|
| `telephone` | Comparator at every site. No incremental video equipment, readiness or coordination charge. | Zero incremental video hours and capacity. | Telephone transfers and hospital care form the baseline. Incremental offsets are zero. |
| `retain_pilot_only` | Retain Panda at Atherton, Innisfail and Mareeba. Charge video readiness and coordination there. Other included sites continue telephone. | Pilot video workload only. | Count changes in pilot transfers, rescues and local care against telephone. |
| `retain_pilot_expand_panda` | Retain pilot Panda and assign Panda to every other included site. Apply Panda capital and local running costs where applicable. | Pool video workload across all assigned sites. | Apply the Panda pathway at each assigned site. |
| `retain_pilot_expand_obsbot` | Retain pilot Panda. Assign OBSBOT at other included sites and use its equipment and workflow assumptions. | Pool Panda and OBSBOT workload. | Combine site-group changes under their assigned pathways. |
| `retain_pilot_expand_mobile` | Retain pilot Panda. Assign mobile at other included sites and use its equipment and workflow assumptions. | Pool Panda and mobile workload. | Combine site-group changes under their assigned pathways. |
| `retain_pilot_expand_fixed` | Retain pilot Panda. Assign fixed at other included sites and use its equipment and workflow assumptions. | Pool Panda and fixed workload. | Combine site-group changes under their assigned pathways. |

Each row follows the [retained site assignments](../outputs/v13-refinements/policy_assignments.csv) and the [catalogue and grouped evaluation](../src/deployment.py). The pilot portfolio has only two distinct policies. CHHHS, CHHHS plus TCHHS, and spokes each have six. The four expansions have conditional eligibility. The [estate register](../config/equipment_estate.json) lists three compatible pilot assets and assumes two remaining years. It does not identify who funds replacements.

## Costs and offsets within each row

| Component | Resource assignment and sign | Fiscal assignment and evidence |
|---|---|---|
| Installed equipment and replacements | Origin site uses the assigned device. The economic ledger annualises attributed capital. The cash schedule charges purchases and replacements in the due year, with credit only for compatible retained equipment. | Purchasing organisation, grant contribution and any shared-use recharge **unknown**. The equipment source is a price estimate. [Parameter audit](../evidence/v7/parameter_audit.csv), [estate accounting](../src/equipment.py), [retained cash schedule](../outputs/v13-refinements/policy_budget.csv). |
| Weekly checks, support, training and consultation coordination | Origin provider incurs readiness per equipped site and workflow per contact. These are programme costs. | Employing or reimbursing budget and recoverable cash **unknown**. Inputs mix documented checks with assumed times and unit costs. [Parameter audit](../evidence/v7/parameter_audit.csv), [pathway calculation](../src/pathways_v6.py). |
| Specialist time and capacity | Consulting hub uses specialist hours. Charge hourly opportunity cost in the economic ledger. In the cash schedule apply spare hours and additional staffing blocks once to pooled workload. Hub cash capacity is already included in cash running costs. | Hub budget holder, spoke recharge and actual staffing commitment **unknown**. [Pathway assumptions](../config/pathways.json), [network pooling and budget](../src/deployment.py). |
| Origin care, local completion and pre-rescue care | Origin provider supplies the origin component for transfers, local episode care for cases remaining local, and extra pre-rescue care for delayed rescues. Additional local care can consume part of a transfer offset. | Origin resource location is identifiable. Provider payment and cash released **unknown**. Hospital benchmarks are scaled to marginal resources. [Disjoint pathway costs](../src/pathways_v6.py), [parameter audit](../evidence/v7/parameter_audit.csv). |
| Transport | Retrieval service supplies transport for immediate transfers and delayed rescues. Fewer journeys can save marginal resources, more journeys consume them. | For qualifying fixed-wing assets, QH-HSD-005 v4 assigns liability to the HHS whose referral RSQ accepts once the asset is tasked. RSQ clinical coordination and RSQ-provided medical staff are excluded. This does not establish an avoided invoice or a combined-mode CHHHS share. Road/rotary charging details and historical applicability remain **unknown**. The uniform scenario’s combined-mode CHHHS retrieval share is an assumption. [Transport calculation](../src/pathways_v6.py), [retrieval share evidence](../evidence/v7/parameter_audit.csv). |
| Receiving care and rescue premium | Destination supplies receiving care once per eventual transfer. The separate receiving premium for delayed rescue is zero in the reference configuration. Changes in either direction enter the system comparison. | Receiving facility, inter-provider settlement and fraction released as cash **unknown**. A consulting hub need not be the receiving facility. [Pathway costs](../src/pathways_v6.py), [reference premium](../config/pathways.json), [receiver share audit](../evidence/v7/parameter_audit.csv). |
| Family travel and time | Assign the gross assumed burden to families. Multiply telephone-minus-policy eventual transfers by the family cost per transfer. Add this once to system net saving for the bounded societal result. | Family out-of-pocket amount, subsidy eligibility and paying agency **unknown**. [Family delta and subsidy audit](../evidence/v7/parameter_audit.csv), [family extension](../src/pathways_v6.py). |
| Government transfers and funding response | Funding transfers redistribute the burden between budgets. No mixed-policy payment is identified for provider, hub or destination. | State and Commonwealth marginal funding and inter-HHS flows **unknown**. The uniform analysis uses illustrative funding and receiver shares. [Fiscal assumptions](../evidence/v7/parameter_audit.csv), [perspective identities](../src/perspectives_v7.py). |

## Reporting decision

Report **health_system** net resource saving: telephone care resources less policy care resources, less incremental programme cost. Report **societal_bounded**: the same amount plus the gross family extension. The retained PSA gives the mean, interval, median and probability of resource saving. Within each retained decision set, the rankings give expected net value, probability optimal and expected regret for those two perspectives. Positive values favour the policy on the stated cost measure. [PSA](../outputs/v13-refinements/policy_psa.csv) · [Rankings](../outputs/v13-refinements/policy_rankings.csv) · [Output driver](../scripts/analyse_refinements.py)

Report the seven-year programme cash schedule separately as modelled expenditure, including pooled hub capacity. Avoided hospital or retrieval resources do not fund that schedule automatically. Without explicitly assumed financing and cash-release terms, the mixed-policy outputs do not establish provider CHHHS net budget impact, separate hub or destination net savings, state or Commonwealth net fiscal impact, or patient/family net-of-subsidy results. Conditional six-perspective scenarios below are reportable as scenarios. An evidence-based fiscal ranking or value-of-perspective estimate requires those missing allocations. The [six-perspective uniform analysis](../outputs/v13-primary/psa_perspectives.csv) remains specific to its original strategies and assumptions.

## Retrieval payer sensitivity

Use CHHHS as the assumed default payer. For the CHHHS portfolio with one contact per episode (`contacts_1`), the annual deterministic retrieval resource offset relative to telephone is allocated as follows (AUD, rounded). The split columns are independently rounded.

| Deployment | System retrieval offset | CHHHS if sole payer | CHHHS if 50% payer | CHHHS if retrieval funder or destination pays all |
|---|---:|---:|---:|---:|
| Telephone | 0 | 0 | 0 | 0 |
| Retain pilot only | 14,999 | 14,999 | 7,499 | 0 |
| Retain pilot and expand Panda | 42,786 | 42,786 | 21,393 | 0 |
| Retain pilot and expand OBSBOT | 42,786 | 42,786 | 21,393 | 0 |
| Retain pilot and expand mobile | 42,786 | 42,786 | 21,393 | 0 |
| Retain pilot and expand fixed | 42,786 | 42,786 | 21,393 | 0 |

If the separate retrieval funder or destination bears the full marginal cost, that party receives the whole offset. Switching payer leaves the system and bounded societal results unchanged. The four expansion options have equal deterministic retrieval offsets here; their programme costs can differ. The amounts indicate potential exposure to retrieval costs. Actual cash released depends on the contract and billing basis, and total CHHHS net impact still depends on the other unresolved components.

[All four payer scenarios across the retained portfolios and activity settings](../verification/mixed-policy-fiscal/retrieval-payers.csv) · [Assumptions, calculation and reproduction](../verification/mixed-policy-fiscal/README.md) · [Existing retrieval share assumption](../evidence/v7/parameter_audit.csv)

## CHHHS district and perspective scenarios

For one contact per episode in the CHHHS portfolio, assign all marginal retrieval costs, local operating costs and annualised equipment to CHHHS. Assign half the receiving-care change to CHHHS, and charge the consulting hub centrally. District origin care is valued at the modelled marginal resource fraction. Use fixed Commonwealth funding and state subsidy of half the travel component (travel is 40% of gross family burden). Retrieval follows the owner’s default assumption. Receiving shares, travel, subsidy and funding scenarios follow the [parameter audit](../evidence/v7/parameter_audit.csv) and [uniform ledger](../scripts/analyse_v7.py). The other cost assignments are explicit financing scenarios.

Annual deterministic saving relative to telephone (AUD, rounded):

| Policy | Origin sites combined | District | State | Health system | Societal, bounded | Consumer/family |
|---|---:|---:|---:|---:|---:|---:|
| Telephone | 0 | 0 | 0 | 0 | 0 | 0 |
| Retain pilot | −8,211 | 12,054 | 16,177 | 15,445 | 19,107 | 2,930 |
| Expand Panda | −41,663 | 16,146 | 27,909 | 25,820 | 36,266 | 8,357 |
| Expand OBSBOT | −32,771 | 25,038 | 36,802 | 34,712 | 45,159 | 8,357 |
| Expand mobile | −98,252 | −40,443 | −28,680 | −30,769 | −20,323 | 8,357 |
| Expand fixed | −101,486 | −43,677 | −31,913 | −34,003 | −23,556 | 8,357 |

All expansions retain the pilot. Site totals exclude centrally held offsets. State consolidates public health resources, subsidies and Commonwealth transfers. Consumer includes time and unsubsidised travel. Societal combines health resources and gross family burden. These are overlapping views. The model assigns equal deterministic transfer benefits to the four expansions. The lower OBSBOT programme cost distinguishes them for the district and health system; families receive the same modelled benefit.

**Decision switches.** Varying only the share of marginal retrieval offsets captured by CHHHS, telephone maximises district saving below 19.6%, pilot alone from 19.6% to 53.3%, and OBSBOT expansion above 53.3% (ties at the unrounded boundaries). A full external capital grant makes all expansions tie for the district. With full retrieval exposure, moving all receiving benefits outside the district and charging the full hub cost to CHHHS together favour pilot alone. Adding a fully passed-through loss of Commonwealth funding at the illustrative 40.5% benchmark then favours telephone. Varying the subsidy alone changes the split between families and state without changing their ranking here.

**Cash timing.** Under a variable retrieval bill and zero realised hospital cash offsets, year-one district cash changes are AUD +9,751 for pilot, −44,255 for Panda, −5,755 for OBSBOT, −289,255 for mobile and −303,255 for fixed (telephone zero). This uses the retained cash purchase and operating schedule with central hub funding. A fixed retrieval bill removes even that offset. The annualised district resource ranking and first-year cash ranking therefore answer different budget questions.

[Perspective scenarios](../verification/mixed-policy-fiscal/chhhs-perspectives.csv) · [Individual sites](../verification/mixed-policy-fiscal/chhhs-sites.csv) · [Joint assumptions](../verification/mixed-policy-fiscal/chhhs-joint-sensitivity.csv) · [Seven-year cash scenarios](../verification/mixed-policy-fiscal/chhhs-cash.csv) · [Reproduction and reconciliation checks](../verification/mixed-policy-fiscal/chhhs-reproduction.md)

## Sensitivity to uncertain estimates

At the default fiscal shares, 20,000 paired draws per effect model propagate the existing parameter and pathway uncertainty through each perspective. For CHHHS with one contact per episode, OBSBOT expansion under the attenuated effect has a mean district saving of AUD 15,157, a central 95% simulation range of −79,929 to +164,121, a 53.0% probability of saving relative to telephone, and a 48.0% probability of being best among the six policies. The published-effect scenario raises its mean to +57,482. The skeptical and null scenarios give means of −30,097 and −29,831, respectively. The payer scenarios are conditional alternatives with no probabilities assigned to them.

[All policy and perspective estimates](../verification/mixed-policy-fiscal/chhhs-estimate-sensitivity.csv) · [Replication and checks against retained rankings](../verification/mixed-policy-fiscal/chhhs-reproduction.md)


## Fiscal evidence reconciliation — 3 November 2026

The [evidence register](../config/fiscal-evidence.json) separates a documented
liability rule from uncertain marginal payment and cash release. The current
[QH-HSD-005 v4 directive](https://www.health.qld.gov.au/system-governance/policies-standards/health-service-directives/retrieval-services),
effective 19 June 2026, gives the accepted-referral/tasking rule in Outcomes.
Its Efficiency principle describes user-pays arrangements more broadly; it does
not supply mode-specific tariffs, cancellation charges or the avoidable fraction.
Do not infer zero road/rotary liability from the narrower fixed-wing statement.
The historical activity predates this version; contemporaneous terms remain to
be verified. Central invoice processing does not establish which budget finally
bears a charge. Consultation, acceptance, tasking and eventual transfer are
separate events. A clinical decision to keep an infant local must remain subject
to clinical appropriateness, regardless of the apparent fiscal incentive.

CHHHS payment remains the default **scenario** for CHHHS combined-mode results.
In wider portfolios, the documented referring-HHS rule cannot be replaced by
assigning every origin's liability to CHHHS. Preserve the old all-CHHHS allocation
as a labelled sensitivity only. A destination or external payer scenario is a
counterfactual unless an applicable agreement supports it; it does not override
the directive for qualifying fixed-wing cases.

| Decision | Options | Recommendation and completion evidence |
|---|---|---|
| Retrieval cash | Treat all resource savings as cash; retain fixed/shared/variable cases; obtain charged-unit reconciliation | Retain scenarios and prioritise a non-patient aggregate mode-by-referring-HHS invoice reconciliation, including fixed availability and cancellation terms. Do not convert resource offsets into cash automatically. |
| Other fiscal components | Assume existing shares; exclude them; obtain the actual agreements | Keep explicit existing shares for sensitivity, and seek asset/grant records, hub recharge/capacity and receiving-care settlement records. Exclusion is not evidence of zero. |
| Publication | Report conditional fiscal results; claim verified CHHHS savings; defer all modelling | Report conditional results with health-system resource and bounded societal results separately. Verified district/state/consumer cash claims wait for applicable ledger evidence. |
| Track disposition | Archive now; retain the outstanding evidence task | Keep open. Archive only after the listed evidence resolves fiscal incidence and its reporting implications have been reviewed. |

No frozen parameter, simulation, retained numerical output or payer probability
was changed by this reconciliation. Fiscal assignments are not additive across
perspectives. Four independent reviews remain pending. See the
[scoped author review](../verification/v13/fiscal-reconciliation/review.md).


### SharePoint and local-document follow-up

On 3 November 2026, read-only SharePoint searches and local document discovery
identified no applicable charging schedule or aggregate transport invoice
reconciliation. Fifteen queries returned 514 unique indexed records for metadata
screening. Several broad queries reached the 100-result cap; negative Path filters
also returned excluded-site hits. This is a bounded, permission-trimmed search,
not evidence that the records do not exist. Local filename discovery covered
Documents, Downloads and CloudStorage; no patient extracts were searched.

The hash-verified internal **RSQ Overview GM001 v2 (10 January 2025), p.11**
explicitly assigns RFDS and air-ambulance transport costs to the sending/referring
service. It describes RSQ GaP invoicing and revenue recovery, and pp.11–12 describe
activity reporting and cost-allocation systems. This supports referring-service
attribution beyond a claim based only on central invoice processing. It supplies
neither a charging schedule nor the amount saved by avoiding a journey. It does
not resolve road/rotary rates, excluded crew, fixed availability, cancellations or
historical applicability. The current directive remains the cited public rule;
the internal overview is supporting administrative evidence, with source rights
and publication permission unresolved.

**RSQ Governance Framework GF001 v2 (24 July 2026), section 6 and p.12** identifies
financial/contractual oversight and provider contract-management meetings. These
are plausible record custodians, not proof that an applicable tariff or ledger has
been obtained. The September 2026 RRS performance pack concerns RFDS services at
remote primary-health clinics; that separate agreement issue was screened out of
retrieval-price inference. No performance-pack amounts enter this model.

The evidence register pins the two source PDFs; both PDFs, the performance pack,
extracted text, search results and checksum inventory remain in the external
ClinicalResearchEvidence vault. No cash-capture distribution or model input was
recalibrated. Health-system resources and conditional district cash scenarios
remain distinct. Fiscal evidence remains open and four reviews remain pending.
