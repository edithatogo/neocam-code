# Conductor tracks — current v14 work

Implementation completion is not external acceptance. Historical tracks remain unchanged under their original folders.

Design authority for the current tracks: [./v14-design.md](./v14-design.md).

## v13 — closed history (unchanged)

---
## [x] Track: Episode/contact semantics
Link: [./tracks/v13-01-contacts/](./tracks/v13-01-contacts/)

---
## [x] Track: Eligible mixed deployment and shared capacity
Link: [./tracks/v13-02-policies/](./tracks/v13-02-policies/)

---
## [x] Track: Clinical plausibility packet and unresolved evidence
Link: [./tracks/v13-03-review/](./tracks/v13-03-review/)

---
## Active work

## [~] Track: Mixed-policy fiscal allocation
Link: [track plan](tracks/mixed-policy-fiscal-allocation/). Fiscal shares await payment, routing and subsidy evidence.

## Archived tracks, 2 November 2026

| Track | Disposition |
|---|---|
| [v13-04 Delivery](tracks/v13-04-release/) | Delivered on main at 8180947. PR #3 closed as superseded. |
| [v14-02 Acceptance integrity](tracks/v14-02-acceptance-integrity/) | All 32 gates passed locally and on GitHub at 8180947. Both receipts and the verified signature are in verification/v14/delivery. |
| [v14-01 Engineering](tracks/v14-01-engineering-rigour/) | Reviewed fixes delivered. Original ReportLab red output and historical trial chronology are unavailable. |
| [v14-03 Ecosystem integration](tracks/v14-03-ecosystem-integration/) | Inventory and CI review complete. The hosted signing job succeeded and the downloaded archive verified. |
| [v13-03 Full-text appraisal and review packet](tracks/v13-03-review/) | Four articles appraised. Independent review of the frozen packet remains open. |
| [v14-04 VoI integration](tracks/v14-04-voi-voiage-integration/) | Voiage 3.1.0 integrated. Retained-scenario parity and hosted assurance verified on b84a43d. |

## Archived implementation scopes — 4 November 2026

| Track | Disposition |
|---|---|
| [x] [Project-wide VoI and geographical decisions](tracks/project-information/) | Implementation reviewed and archived against the verified 32-gate local receipt. Final Word/Excel packet hashes verified. Four independent reviews and fiscal evidence remain open. |
| [x] [Neonatology manuscript preparation](tracks/neonatology-article-contract/) | Editorial implementation reviewed and archived against the same local receipt and final ridgeplot packet verification. Submission acceptance remains open for author declarations and four independent returns. |

Terminal local evidence is in `verification/v13/manuscript-preparation/terminal-verification.json` and `final-packet-assurance.json`. Hosted assurance on the merged commit is a separate delivery gate. The fiscal allocation track remains active.

## Separate code release — 5 November 2026

[x] Archived implementation: [code-release-preparation](tracks/code-release-preparation/plan.md). PR #1 merged as `3d69e04`; all 32 exact-main gates, receipt log digests, archive digest and cryptographic attestation verified (run 41959741259). The code repository is public with explicit owner approval; the original research repository and its open PR #3 remain private. Documentation closeout receives separate exact-main verification. Four independent reviews remain pending; fiscal evidence remains open.
