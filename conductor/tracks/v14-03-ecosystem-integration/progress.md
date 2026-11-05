# Execution ledger — v14-03 ecosystem integration

3.1 Inventory — not started. Known material from the reconnaissance in
`conductor/v14-design.md` and `docs/library-integration.md`:

- Already incorporated: `neocam` itself; `edithatogo/conductor-next` as the pinned
  submodule (`extensions/conductor`, pinned 137c1e41).
- Already documented as deliberate external references: `vop_poc_nz` (method contract
  reimplemented from the inspected commit ad84d30), `mchs` (checked 9fc8d0f, not
  executed), `microcosting_healthworkforce`, `voiage` (deferred).
- Candidates not yet incorporated, with the reason they matter: `template-solo-data`
  (reusable CI/Renovate/OIDC pattern), `careops-rims` (real `privacy.yml` plus secret
  and privacy safeguards), `sourceright` (citation/reference verification, mapping onto
  `sources/` and the citation receipts), `riopa-infrastructure` (provenance-first
  reproducible-research infrastructure).
- Owner decision required per repository: pinned submodule, documented reference, real
  dependency, or CI reuse. Nothing is added before that decision.

3.2–3.3 privacy patterns and CI alignment — not started.

3.4 Canonical VoI alignment with `voiage`/`vop_poc_nz` — GATED. The repository states
"`voiage` deferred until decision utility is credible; current EVPI is explicitly
cost-only". No work starts until the owner confirms credibility; if it proceeds it is a
model track with its own parity suite, because results may legitimately change.

## Reconciliation, 1 November 2026

The v14 design records the sibling inventory and incorporation forms. The library-integration document still needs the accepted inventory. The privacy implementation and synthetic fixture landed in 5089e20, followed by the optimisation in 570f6c2. See verification/v13/burndown/privacy-gate.md and the hosted privacy and full-profile receipts. Task 3.3 remains open. Track 04 owns the former 3.4 scope.

## CI and documentation review, 2 November 2026

Task 3.1 completed in f3b274f. GitHub's commit API resolved all 11 checked objects to the exact inventory SHAs. The local context check returned an empty error list. Technical workflow references stay in the library guide.

Task 3.3 compared template-solo-data at 4abb00d and its reusable workflow at 7e5c4cc. The guide records decisions on CI, OIDC, Codecov, Renovate and Scorecard. f345533 fixed caller permissions and isolated signing. 286ee62 applied review fixes. Task 3.2 reuses its retained evidence. Task 3.4 belongs to track 04. The local workflow inspection cannot establish hosted token issuance or archive signature verification.
