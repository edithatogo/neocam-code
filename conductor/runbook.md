# Neocam v14: engineering rigour and acceptance integrity

Design authority: `conductor/v14-design.md`. Track register: `conductor/tracks.md`. This runbook remains the authoritative workflow.

## Browser and authentication

Use the Codex internal browser only for sign-in, reauthentication, opening/loading
pages, web interactions and browser-based QA, unless the user explicitly states
otherwise for the operation. A generic tool preference is not an exception to this
browser rule. If the internal browser is unavailable or cannot complete a required
step, report the specific limitation instead of launching or controlling an external
browser. This grants no authentication bypass, credential change, new consent or
broader access. Preserve native-operation and authentication ownership.

## Numerical scope
Use CPython 3.15.1 for qualification. NumPy handles model draws. Voiage 3.1.0 supplies EVPI and perspective decisions. Its runtime includes PyArrow, Polars, SciPy and scikit-learn. Polars is the only permitted DataFrame engine. Declared reference inputs flow through `src.configuration.load_configuration`; `data/v6/spec.json` is a reference snapshot, not a live configuration input.

### Authorised aggregate update — 23 November 2026

The active [aggregate multiscale track](tracks/aggregate-multiscale-update/plan.md)
adds reported-evidence parameters, aggregate scenarios and new outputs through the
existing model. This narrowly supersedes the assurance-era parameter/output freeze
and the original release's no-new-parameter scope; retained v13 inputs and results
remain unchanged. The published estimate and its reported confidence interval define
the primary new evidence scenario. Transportability, attenuated, skeptical, null,
timing and fiscal assumptions remain explicit alternatives. Aggregate inputs support
CHHHS, regional, Queensland, Australian and international decision scenarios.
Patient-level data and a prospective registry are optional refinements, not execution
prerequisites. No new framework, learned surrogate or orchestration layer is required.

The reviewed private implementation has been promoted. To refresh it, update
`data/aggregate/public-inputs.json` and `config/aggregate-analysis.json`, then use a
**new** output directory:

```sh
uv run --frozen --group assurance --extra research python -m pytest -q tests/test_aggregate_analysis.py
uv run --frozen --extra research python -m scripts.analyse_aggregate \
  --config config/aggregate-analysis.json --output outputs/aggregate-NEXT
```

Private PR #12 and public PR #11 contain the executed increment and its recorded
checks. Later runs must use a fresh output directory and a new source-bound seal. See [the update guide](../docs/aggregate-multiscale-analysis.md).

## Strictness and quality settings
ruff `select = ["ALL"]` with preview rules; ty `all = "error"` plus `--error-on-warning`; basedpyright `all` with experimental features, blanket `# type: ignore` banned, ignore comments must name their rule; pytest strict markers/config, warnings-as-errors and `xfail_strict`. No global lint ignore beyond the two documented formatter conflicts, no type-checker baseline file, no lowered threshold. The mutation floor is 90%. Read the mutation result from the exact-commit full receipt; historical scores do not qualify this separate code snapshot.

## Reproduction
```
python -m quality.cli --profile quick
uv run --frozen --group assurance --extra tabular --extra research --extra reporting \
  python -m quality.cli --profile full --evidence-version v41
```
Ordering rule — the artifact re-seal must be the **last** mutation before acceptance:
```
python -m quality.artifacts seal --output outputs/aggregate-NEXT
python -m quality.artifacts verify
# then immediately: full profile, and nothing else edits source afterwards
```
Retained v13 artifacts and their manifests are historical; do not reseal them.
Set `config/assurance.json` to the new output directory before running the analysis.
The final `release_manifest.json` pins the analysis manifest as an artifact; it is the
authoritative final-directory check. Validate the inner manifest before this final seal.
Both `sources/manifest.json` (which pins the retrieval tool's own bytes) and the artifact manifests (which pin every calculation input) are invalidated by any later source edit. A mid-wave seal is therefore always stale. Use new output paths for reruns; never overwrite retained analyses. `OAI_IS_JUPYTER_KERNEL=false` avoids irrelevant host initialisation; `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` is ordinary-suite control only, never a substitute for a required gate.

## Boundaries
Read `blockers-v13.json` and `validation-v12.md`. Claim a lock, external tool, gitleaks scan, populated submodule, independent validation or hosted run only when its evidence actually passes. No patient records or fabricated observations enter this project. The active track may parameterise reported estimates and documented aggregate scenarios. Preserve the public source-withheld identifiers and their interpretation. The owner-authorised agent advisory policy of 5 November 2026 supersedes mandatory human advisory returns; historical pending forms do not establish human approval. Append execution records only under `verification/` and `handoff/`.

## Delivery

The separate code repository is edithatogo/neocam-code and is **public**, following explicit owner approval on 5 November 2026. The original edithatogo/neocam research repository remains private; its PR #4 is the research parent for the new aggregate increment. The public repository retains its separate Git history. Read docs/code-release-contract.md and conductor/tracks/code-release-preparation/plan.md as the original release contract, together with the current amendment in docs/public-safe-consolidation.md.

Main requires assurance, privacy, dependency review and static application security, including administrators; force pushes and deletion are blocked. Gitleaks and the private-file guard remain enabled. Native secret scanning and hosted assurance are not claimed without exact readback. Local acceptance and merged-main receipts/attestation are separate gates. The code publication authority does not extend to the original research repository, clinical packet or private evidence. Agent advisory review is the current owner-authorised policy; independent human validation is not claimed. The fiscal evidence track remains open with its existing owner.

Commit and review the private implementation first, then copy only the explicit
reviewed public-safe delta onto this repository's own history. Do not merge or
cherry-pick private commits. Record the allowed paths, hashes and any source-withheld
projection; verify shared-input numerical parity. Private manuscripts, source
originals, records, locators and unreleased local aggregates remain withheld.
`neocam-public` is a historical snapshot, not a third active copy. Promotion and local checks are recorded in the current track; hosted acceptance
retains its exact commit and workflow identity. Existing receipts
qualify only their original commits; no refreshed manuscript or Word/PDF is claimed.

## Executed aggregate increment

The 23 November 2026 reported-evidence analysis is at `outputs/aggregate-20261123-release`.
The fresh public 20,000-draw release run took 13.090 seconds and reproduced all
six private numerical/input artifacts byte-for-byte. See [the results](../docs/aggregate-results-20261123.md)
and `verification/aggregate-multiscale-20261123/public-checks.json`. One broad suite
was followed by targeted privacy repairs; historical failures and successful checks
are retained. The existing release checker now targets a fresh aggregate release. Historical
v13 output bytes and seals remain unchanged; the ReportLab fixture explicitly uses
its retained historical schema. See `verification/aggregate-multiscale-20261123/release-reconciliation.json`.
