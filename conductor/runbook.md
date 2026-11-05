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
Use CPython 3.15.1 for qualification. NumPy handles model draws. Voiage 3.1.0 supplies EVPI and perspective decisions. Its runtime includes PyArrow, Polars, SciPy and scikit-learn. Polars is the only permitted DataFrame engine. Declared inputs flow through `src.configuration.load_configuration`; `data/v6/spec.json` is a reference snapshot, not a live configuration input. No new clinical parameter, learned model, orchestrator or output path.

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
python -m quality.artifacts seal --output outputs/v13-primary
python -m quality.artifacts seal --output outputs/v13-refinements
python -m quality.artifacts verify
# then immediately: full profile, and nothing else edits source afterwards
```
Both `sources/manifest.json` (which pins the retrieval tool's own bytes) and the artifact manifests (which pin every calculation input) are invalidated by any later source edit. A mid-wave seal is therefore always stale. Use new output paths for reruns; never overwrite retained analyses. `OAI_IS_JUPYTER_KERNEL=false` avoids irrelevant host initialisation; `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` is ordinary-suite control only, never a substitute for a required gate.

## Boundaries
Read `blockers-v13.json` and `validation-v12.md`. Claim a lock, external tool, gitleaks scan, populated submodule, independent validation or hosted run only when its evidence actually passes. No new patient records, clinical estimates or fabricated observations. Review forms bind source and configuration; their pending records are not clinical approval. Append execution records only under `verification/` and `handoff/`.

## Delivery

The separate code repository is edithatogo/neocam-code and remains **private**. The original edithatogo/neocam research repository and its PR #3 are retained privately and unchanged by this release. A fresh Git root prevents importing that history. Read docs/code-release-contract.md and conductor/tracks/code-release-preparation/plan.md.

Main requires assurance, privacy, dependency review and static application security, including administrators; force pushes and deletion are blocked. Gitleaks and the private-file guard remain enabled. Native secret scanning and hosted assurance are not claimed without exact readback. Local acceptance and merged-main receipts/attestation are separate gates. Publication requires explicit user authority. Four independent clinical reviews remain pending and the fiscal evidence track remains open.
