# Execution ledger — v14-04 VoI / voiage integration

Owner direction (2026-10-31): **including `voiage` is the priority**; `vop_poc_nz` is not a
dependency and anything it has that voiage lacks must be integrated **into voiage** as
part of this work. `sourceright` is deferred to the roadmap ("do everything else first").

## Verified facts before implementation

1. **voiage is published and installable in principle.** PyPI `voiage==2.2.0`,
   `requires_python >=3.12`, wheel `voiage-2.2.0-cp312-abi3-macosx_11_0_arm64` plus
   manylinux x86_64 and win_amd64. The **abi3** wheel means the extension is
   stable-ABI compatible with 3.15, and GitHub's x86_64 runners are covered. Apache-2.0.

2. **Hard blocker: voiage cannot install on Python 3.15 today.**
   - voiage 2.2.0 declares `pyarrow>=25.0.0,<26`.
   - pyarrow 25.0.0 and 25.0.1 publish **zero** cp315 wheels (measured across all files).
   - pyarrow 26.0.0 publishes cp315 wheels for macosx_12_0_arm64 and
     manylinux_2_28_x86_64.
   - Consequence: `uv run --with voiage==2.2.0` attempts a pyarrow source build (CMake
     failure), and forcing `pyarrow==26.0.0` is unsatisfiable because the cap excludes it.
   - Therefore task 4.1 (widen the cap upstream) is a prerequisite for this project's
     3.15-only policy; the constraint cannot be overridden honestly from here.

3. **voiage already has a perspective module** — `voiage/methods/perspective.py`
   (665 lines, `METHOD_CONTRACT_VERSION = "1.1.0"`, tie policies first/split/error):
   `Perspective`, `PerspectiveSet`, `ValueOfPerspectiveResult`,
   `value_of_perspective(...)`, `perspective_optimal_strategies(...)`, Pareto helpers, and
   Arrow/Parquet/IPC serialisation with schema fingerprints. So the port is a
   capability gap, not a missing module.

4. **Capability gap, voiage vs vop_poc_nz** (both declare contract 1.1.0):
   | Capability | voiage | vop_poc_nz | action |
   |---|---|---|---|
   | value of perspective / optimal strategies | yes | yes (`evop`) | already present |
   | Arrow/Parquet/IPC + schema fingerprint | yes | no | keep voiage's |
   | Pareto strategy indices | yes | no | keep voiage's |
   | acceptability frontier | **no** | yes | port |
   | mixture frontier, exact expected-value frontier | **no** | yes | port |
   | expected-value switch points | **no** | yes | port |
   | weighted perspective | **no** | yes | port |
   | MCDA feature records, `tensor_from_records` | **no** | yes | port |
   | `NetBenefitTensor` container + row/segment/switch dataclasses | **no** | yes | port |

5. **Precedent for cross-repo incorporation in this owner's ecosystem**: voiage itself
   carries `.repo-tools/` submodules (sourceright, authentext, astro-polyglot). That is
   noted for the v14-03 CI/pattern decisions, not as a reason to add submodules here.

## Status

- 4.1 (voiage installable on 3.15) — **CORRECTED BY RECONNAISSANCE**: voiage `main` already
  declares `pyarrow>=26.0.0,<27`, `requires-python = ">=3.15.1,<3.16"`,
  `target-version = "py315"` and builds `cp315-abi3`. The `pyarrow<26` cap survives only in
  the **published 2.2.0 tag** and in frozen historical files (`paper/reproduction-environment/…`,
  `packaging/easybuild/release-pyproject-v2.2.0.toml`, and the upstream-owned, SHA-pinned
  `specs/integration/vop-voiage/compatibility/v1/contract.json`). So this task becomes
  "obtain a voiage release containing main's state", not "widen a cap" — and it is
  **release-gated, not code-gated**. Earlier entries in this ledger that framed it as a cap
  change are superseded by this paragraph.
- 4.2 (capability port) — scope confirmed by the dossier: voiage has **no** naming collisions
  for the seven functions or the dataclasses to port (verified by grep across
  `voiage/ tests/ specs/ scripts/`), but the port must be adapted, not copied:
  - voiage raises through `voiage.exceptions.raise_input_error`, not a local
    `PerspectiveError(ValueError)`;
  - voiage is ndarray-first (`ValueArray`), while `vop_poc_nz` is container-first
    (`NetBenefitTensor`);
  - default tie policy differs (`"first"` vs `SPLIT`) and the tolerance keyword differs
    (`tie_tolerance` vs `atol`);
  - `vop_poc_nz` exposes population scaling, the per-person/population split and
    `discordance_probability`, which voiage's perspective module does not expose at all
    (its `Perspective.population` metadata is currently unused);
  - rank-averaging tie semantics from `vop_poc_nz` (`_tie_mask`, `_dense_descending_ranks`,
    `_select_single`) are not reproduced in voiage.
  Two latent collisions must be resolved deliberately: module-level `evop`, and
  `regret_matrix` (voiage already has an ndarray attribute of that name on
  `ValueOfPerspectiveResult`).
- 4.3 (release) — **owner action likely required**: releases are tag-driven
  (`release.yml` on `push: tags: ["v*"]`) and stage a draft with `publish` defaulting to
  `false`; `changelog.md`/`todo.md` entries are required per change. A voiage release
  containing 4.2 is the gate for 4.4 here.
- 4.4 (consume voiage here, with parity) — not started. Weight to record against the
  design document's "value per dependency" criterion: voiage brings **pyarrow** (large
  binary) plus its own stack into this project's resolved set.
- 4.5 (retire duplicates) — not started; `vop_poc_nz` stays an evidence source.

Governance constraints recorded from the dossier that shape 4.2/4.3:
`specs/frontier/governance/promotion-checklist.json` currently registers
`value_of_perspective` as fixture-backed with `next_gate: cross-language-parity` and
`stable_claim_allowed: false`, so new functions must not claim stability; any new Arrow
output field changes `arrow_schema_fingerprint_sha256` and both golden hashes in
`specs/frontier/perspective/v1/interchange/manifest.json`, and reference fingerprints
accept no globs or automatic refresh, so regeneration is a deliberate reviewed step;
`tox run-parallel -p 2` is voiage's local CI authority, and `sys.version_info[:3]` must be
`(3, 15, 1)`.

## Reconciliation, 1 November 2026

The inspected published 2.2.0 cap and upstream main differ. The cap edit and contribution in 4.1.c/e are superseded on inspected main. Upstream install and test evidence and the capability port remain separate deliverables. Verify the outstanding capabilities against the selected upstream revision before beginning 4.2.

## Upstream port, 1 November 2026

Chat 01a19747-8ce7-7432-b09e-41c74a3da50a owns the isolated clone at
`/Users/doughnut/Documents/voi-perspective-track/voiage` on
`codex/perspective-parity`. No native tenant scope. The comparison used voiage
main `dd94d4e65f56f89029b726d4e68bc8e35c81c0cc` and vop_poc_nz main
`ad84d3090a2d97f2805a86e94a7b9614a3d1ab14`.

Voiage already supplied aggregate directional regret, optimal strategy selection,
Pareto indices, Arrow export and Parquet/IPC. The port adds the labelled tensor
and long-form input, draw discordance, population-scaled pairwise regret,
tie-aware probabilities and dense ranks, weighted lenses, grid and exact
frontiers, switch points, MCDA records, bootstrap intervals and draw-count
convergence. Tensor regret and aggregate regret keep separate return contracts.
The bootstrap estimates Monte Carlo uncertainty.

Upstream commits `4a8bbe0` and `68821b9` are in
[voiage draft PR 1257](https://github.com/edithatogo/voiage/pull/1257).
Before implementation, collection failed on the missing tensor module (two
modules) and diagnostics module (one). On the PR head, the 43 perspective tests
passed on repo-local CPython 3.15.1. The shared conformance fixture was identical
in both repositories. Twelve seeded 16-draw inputs also matched the reference
across nine output groups, including exact and sampled switches, MCDA rows,
bootstrap replicates and convergence. The port adds no dependency on vop_poc_nz.

Final candidate `8c2543e856b0f34b3618c770da9d78dae38de5c1` registers both
experimental modules, tests invalid tensors and all tie-policy paths, and removes
a redundant interval check after tolerance-based deduplication. The original
hosted inventory and patch coverage failures were corrected. Focused results
were 63 passed and 100% coverage of 488 statements and 134 branches across the
two modules. On the same commit all 15 local tox environments passed using
CPython 3.15.1, full Git history and the pinned submodules. The covered suite
reported 5,768 passed, 20 skipped, 46 warnings and 94.83% coverage. The full local
tox result is retained at `/Users/doughnut/Documents/voi-perspective-track/8c2543e8-tox.json`.
[Hosted CI coverage](https://github.com/edithatogo/voiage/actions/runs/41313143855/job/124867648120)
and [operational assurance](https://github.com/edithatogo/voiage/actions/runs/41313143876/job/124867608268)
passed at that head, as did Codecov patch coverage.

Next command: `gh pr view 1257 -R edithatogo/voiage --json state,isDraft,headRefOid,mergeCommit`.
Merge and release are separate from the tested port. Qualify the released wheel
before downstream dependency or model changes.

## Published wheel qualification, 2 November 2026

PR 1257 merged at `9210870a`. Release PR 1258 merged at `d40af027`, the source
for signed tag `v3.1.0`. The release used macOS 15 after GitHub retired the macOS
14 runner. [Staging](https://github.com/edithatogo/voiage/actions/runs/41368617927)
and [publication](https://github.com/edithatogo/voiage/actions/runs/41369657510)
passed. TestPyPI index propagation delayed its first install check.

The isolated CPython 3.15.1 install used the public PyPI file URL and SHA-256
recorded in `verification/voiage/release-3.1.0.json`, checked against the reviewed
GitHub release asset. To reproduce in a fresh 3.15.1 venv, set WHEEL to the
receipt's source URL and SHA to its sha256, then run
`uv pip install --python "$VIRTUAL_ENV/bin/python" --default-index https://pypi.org/simple "$WHEEL#sha256=$SHA"`.
All 29 installed packages passed uv pip check. The receipt records agreement for
all archived choices, the 44 portfolio/scenario combinations, mixed-policy rankings
and eight historical cost-only EVPI results. The largest change in the producer
replay's probability of strictly positive net value was 0.125 percentage points.
The archived draw comparison for optimal choices and probabilities was exact.

Next executable check in that environment:
`"$VIRTUAL_ENV/bin/python" -I verification/voiage/release_parity.py`.
Model wiring and lock changes remain separate tasks 4.4.c onward.

## Runtime adoption, 2 November 2026

Chat 01a19747-8ce7-7432-b09e-41c74a3da50a owns the scoped branch
`codex/neocam-voiage-runtime` at `/Users/doughnut/Documents/neocam-voiage-runtime`,
based on main 8180947. No tenant objects. The frozen dependency set gains 11 lock
entries including voiage and PyArrow 26.0.0. Voiage supplies stable EVPI,
fixed-decision split-tie regret and selection probabilities. Neocam supplies
local tie bounds and retains its historical arm-specific relative tolerance.
The integrated primary, mixed-policy and historical cost-only results are in
`verification/voiage/integrated-3.1.0.json`. Full gate results belong in
`verification/v14/full/receipt.json`.

## Closed on main, 2 November 2026

PR #5 merged the integration at b84a43df74d1b928e474b456a3e5a59545438be0.
The integration handoff at 4afcfba records the two retained seals and the
byte-for-byte replay of the parity receipt, including the disclosed historical
producer difference. See `verification/v15/voiage-handoff.md`.

[Hosted run 41386713617](https://github.com/edithatogo/neocam/actions/runs/41386713617)
passed all 32 gates on Python 3.15.1. Each gate log matched its receipt hash.
The downloaded archive (artifact 13116243740) matched SHA-256
`7ac74a0c64fbff03b8a30434ac3f8e406747346bdd6a823bfeb69aca6bc71bca`.
GitHub CLI verified its provenance against ci.yml, refs/heads/main and the full
merge SHA. The receipt and verification result are retained in
`verification/voiage/hosted-41386713617/`. This chat owns the documentation
closeout on codex/close-voiage-track in the same runtime worktree.
