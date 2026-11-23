# Public aggregate inputs: audit of 23 November 2026

The [source ledger](../data/aggregate/public-inputs.json) records 12 service/data
inputs and four reported clinical estimates, with their cohorts, periods,
denominators and intended model use. It contains public aggregates and explicit
gaps. Adding this ledger does **not** apply its values to
the model. Parameter and scenario mappings belong in the analysis configuration;
the historical baseline and retained outputs have not been updated by this audit.

## Reported clinical estimates as parameters

The reported estimates can be represented directly with uncertainty in their
native units. In this table, Normal notation gives the mean and **standard
deviation**, and the standard deviations describe uncertainty in the reported
estimate. They are not patient-level outcome distributions.

| Published estimate | Native-unit uncertainty distribution | Current mapping |
|---|---|---|
| [Haynes 2020][haynes-transfer]: adjusted transfer OR **0.48**, 95% CI **0.26–0.90**, video versus telephone. | `log(OR) ~ Normal(log(0.48), 0.3168)`; log SD derived as `log(0.90/0.26)/3.92`. | Primary reported-effect parameter in the aggregate configuration. Endpoint is transfer within 24 hours; mapping it to eventual transfer remains an explicit extrapolation. |
| [Albritton 2018][albritton]: adjusted difference **−0.70 transfers per facility-month**, CI **−1.236 to −0.157**. | `difference ~ Normal(-0.70, 0.2753)`; SD from CI width divided by 3.92. | Distribution defined in native units; inactive in the OR kernel until facility-month, cohort and outcome mapping. The separately reported **29.4% reduction is in odds**, not risk. |
| [Maddox 2021][maddox]: adjusted absolute transfer-risk difference **−0.12**, reported SE **0.05**. | `risk_difference ~ Normal(-0.12, 0.05)` on the probability scale. | Distribution defined; inactive in the OR kernel pending baseline-risk and population mapping. This is **−12 percentage points**, not a relative risk reduction. |
| [Haynes 2021][haynes-time]: adjusted stabilisation difference **−1.80 minutes**, CI **−16.0 to 12.4**, among transferred neonates. | `time_difference ~ Normal(-1.80, 7.2449)`; SD from CI width divided by 3.92. | Distribution defined; inactive until a corresponding time/resource outcome is specified. The interval includes shorter and longer stabilisation. |

Albritton and Maddox concern overlapping Intermountain program periods and must
not be pooled as independent studies. Their populations and estimands also
differ. Native mean differences must not be inserted into the odds-ratio kernel
or converted into unreported OR confidence intervals. Applying a risk difference
later requires a baseline risk and valid probability bounds.

These are reported associations. Preserve their reported centres and uncertainty;
put bias, transportability and endpoint extrapolation in separate named scenarios.
The existing OR calculation can therefore use the published estimate now while
showing the consequences of those assumptions explicitly.

## Inputs worth retaining

| Input | Audited value or rule | Status and use |
|---|---|---|
| CHHHS maternal flow | 2,852 resident mothers; 2,775 delivered in CHHHS and 51 in Townsville; 3,066 mothers delivered in CHHHS regardless of residence. | Observed 2022; catchment context. Mothers are not babies or neonatal consultations. |
| TCHHS maternal flow | 389 resident mothers; 255 delivered in CHHHS, 99 in TCHHS and 19 in Townsville. | Observed 2022; regional context and redistribution scenarios. |
| Queensland birth inventory | 46,711 public-facility babies; 13,741 private; 350 home/freebirths; 602 born before arrival; total 61,404. | Observed 2022; source check for the existing facility inventory. Includes stillbirths. |
| Nursery transfer matrix | 1,508 livebirths transferred; excludes born before arrival. | Observed 2022; state calibration, not eligible consultation incidence. |
| RSQ observation unit | 31,345 records but 30,752 distinct published Unique IDs; age is N/A in every record. | FY2024/25 data-quality context. Repeated IDs have unresolved meaning. |
| RSQ perinatal diagnostic subgroup | 1,136 records, 1,112 distinct IDs; referring CHHHS 76, TCHHS 12 and Townsville 117 records. | Observed FY2024/25; diagnostic subgroup, not an age-defined neonatal cohort. |
| RSQ subgroup mode mix | With retrieval-personnel transfer: road 271, fixed wing 319, rotary wing 121, grouped mode unknown 25. | Conditional descriptive context: 736 records, 711 with known mode. |
| RSQ cost responsibility | Fixed-wing payment follows accepted referral and asset tasking; RSQ coordination and RSQ-provided retrieval medical staff are excluded from HHS charges. | Current policy context, effective 19 June 2026. Not a tariff or avoidable-cost fraction. |
| Weipa activity and video | 32 births in 2025, 14 in 2024; birthing resumed 22 May 2024; installed video capability publicly reported in July 2026. | Observed service facts; candidate estate/volume scenario. Uptime and uptake are unmeasured. |
| Cooktown activity | Birthing resumed 14 September 2026; approximately 40 annual births expected. | Prospective planning scenario, not an observed annual count. |
| Transport marginal costs | Current neonatal tariffs, cancellation charges and avoidable financial/resource costs were not verified publicly. | Missing parameter; high-value CHHHS aggregate request. |
| Eligible CHHHS consultations | Matched eligible-episode, consultation and outcome denominators are not supplied by these public sources. | Missing parameter; high-value CHHHS aggregate request. |

Sources are the [Queensland PDC chapter 8 tables][pdc], [RSQ activity resource][rsq],
[current RSQ directive][directive], [Weipa birth report][weipa-births],
[Weipa video announcement][weipa-video] and [Cooktown reopening announcement][cooktown].
The ledger binds each row to its source and preserves narrower cohort definitions.

## Transfer matrix and denominators

PDC table 8.06 has birth-nursery level as columns and destination-nursery level as
rows. Transposed below for a source-to-destination representation:

| Birth nursery → destination | L1 | L2 | L3 | Other | Total |
|---|---:|---:|---:|---:|---:|
| L1 | 12 | 127 | 142 | 6 | 287 |
| L2 | 113 | 39 | 322 | 65 | 539 |
| L3 | 4 | 344 | 37 | 179 | 564 |
| Other | 5 | 73 | 38 | 2 | 118 |
| **Total** | **134** | **583** | **539** | **252** | **1,508** |

These nursery categories mean basic nursery; nursery plus special care; and
nursery plus special care plus NICU. They are not CSCF levels 1–6. Birth “Other”
includes home and facilities without approved maternity services; destination
“Other” also includes interstate and unstated facilities. The matrix includes
escalation, lateral transfers and stepdown. It does not identify preventable
transfers. The total of 61,404 babies in table 8.09 is not a matched denominator
for livebirth transfers excluding born-before-arrival babies.

Table 8.05 counts mothers. Its printed percentages describe columns: use the
appropriate resident total when deriving a residence-based flow proportion.
New birthing-service scenarios should redistribute regional births, avoiding
double counting births previously occurring at another facility.

## RSQ extraction and uncertainty

The official public CKAN API supplied server-side aggregate counts only. The
ledger retains the resource ID, SQL, retrieval timestamps and response SHA-256
hashes for three saved aggregate responses. Three additional aggregate checks
were observed in tool responses; their raw bytes were not retained and no hash
is asserted. No patient records or identifiers were downloaded.

The audit query's alias `unique_episode_ids` means distinct values of the
published `Unique ID` field; it does not establish that each ID is an episode.
All ages are missing and the perinatal diagnostic subgroup omits neonates
classified under other diagnoses. Neither those records nor their transport
mix automatically replaces neonatal parameters. Earlier datastore years need
coverage checks before trend analysis: FY2023/24 returned 2,000 records and
FY2022/23 included many blank records.

The PDC [native XLSX][pdc-xlsx] is officially linked, but its download returned
HTTP 403 here. The PDF values and transfer-table orientation were verified.
The RSQ original XLSX returned a web challenge; successful aggregate API
responses are the extraction evidence.

Published annual counts are observed for their period. Distributions for a
future year's rates or activity represent future variation or parameter
uncertainty. Beta/binomial or Dirichlet parameterization requires a matched
cohort and denominator. Reported effect-estimate uncertainty, observational bias,
transportability, service-configuration scenarios and cost realization remain
separate. Missing tariffs and cohort definitions are not resolved by assigning
narrow probability distributions.

## Small CHHHS request with the highest decision value

Start with the latest complete 12-month aggregate for the covered CHHHS services;
add up to three annual totals if readily available. The existing
[aggregate request](../conductor/tracks/project-information/aggregate-transfer-request.md)
provides the fuller definitions. Prioritize:

1. Eligible urgent postnatal infant episodes and consultation contacts, separately;
   telephone, attempted video, completed video and unknown counts, with covered
   facilities, inclusion criteria and missing periods.
2. Immediate transfer decision, subsequent transfer within 24 hours, later
   transfer, completed locally and unknown follow-up. Separate urgent escalation
   from planned repatriation.
3. Completed transports and cancellations before/after tasking by road, fixed
   wing, rotary wing and mixed/unknown mode. Separate infants, journeys and legs.
4. Actual attributable charges and cancellation rules; existing equipment,
   implementation and recurring support cost. Separate HHS expenditure from
   health-system resource use.

Broad acuity/gestation bands, receiving bed-days and family travel costs are
optional additions when they could change a decision. Site/month breakdowns
are useful only when available counts and coverage support them. Annual CHHHS
aggregates are a sufficient starting point; patient-level data are not required
to populate this decision model. Use the existing aggregate release process,
keeping suppressed, unknown and zero counts distinct.

Next update: replace the relevant ledger row with a newer verified aggregate,
record its period and denominator, and map it explicitly into the analysis
configuration before rerunning the affected scenarios. No new data service,
framework or dependency is needed for this ledger.

[pdc]: https://www.health.qld.gov.au/__data/assets/pdf_file/0020/1378010/8-fac2022x.pdf
[pdc-xlsx]: https://www.health.qld.gov.au/__data/assets/excel_doc/0022/1378012/8-fac2022x.xlsx
[rsq]: https://www.data.qld.gov.au/dataset/retrieval-services-queensland-rsq-activity/resource/51a298ce-0323-4381-80e9-8beb07f509c9
[directive]: https://www.health.qld.gov.au/system-governance/policies-standards/health-service-directives/retrieval-services
[weipa-births]: https://www.torres-cape.health.qld.gov.au/about-us/news/weipa-maternity-service-celebrates-50th-baby-birth
[weipa-video]: https://www.torres-cape.health.qld.gov.au/about-us/news/new-virtual-care-technology-to-support-birthing-mums-in-weipa
[cooktown]: https://www.health.qld.gov.au/newsroom/news/maternity-services-return-to-biloela-and-cooktown
[haynes-transfer]: https://pubmed.ncbi.nlm.nih.gov/32081766/
[albritton]: https://www.healthaffairs.org/doi/full/10.1377/hlthaff.2018.05133
[maddox]: https://www.frontiersin.org/journals/pediatrics/articles/10.3389/fped.2021.648536/full
[haynes-time]: https://pubmed.ncbi.nlm.nih.gov/33691080/
