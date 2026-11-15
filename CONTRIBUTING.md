# Contributing to neocam-code

Neocam's code repository supports reproducible neonatal video-consultation decision modelling. Contributions should improve bounded numerical correctness, packaging, reproducibility and documentation while retaining research and publication boundaries.

## Before you start

Read [README.md](README.md), [AGENTS.md](AGENTS.md), [the runbook](conductor/runbook.md), [code release contract](docs/code-release-contract.md) and the active track. Preserve the small model's scope, default-result parity and parameter evidence register. NumPy, voiage and Polars retain their documented roles; do not introduce a parallel numerical implementation.

For bugs, provide the affected version or commit, environment, minimal reproduction, expected result and observed result. For a substantial proposal, describe the use case and compatibility impact before expanding implementation scope. Use existing issue templates when offered.

## Development and validation

Use the frozen Python 3.15.1 environment specified by the project. The authoritative runbook defines quick feedback and full acceptance:

```sh
python -m quality.cli --profile quick
uv run --frozen --group assurance --extra tabular --extra research --extra reporting \
  python -m quality.cli --profile full --evidence-version v41
```

Follow the runbook and README for the current evidence version and additional reproduction extras. Keep outputs in a new directory and verify the resulting artifacts. Use the source-only reproduction route when withheld institutional Office templates are unavailable; do not claim that an unavailable report or converter was exercised.

Reproduce the defect before fixing it, add independently expected numerical or contract cases, and run focused checks during edits. Retain full acceptance gates at integration. Explain any default-result or interface change and preserve scientific limitations. A software pass does not close independent review or fiscal evidence gates. External evidence, manuscripts and institutional artwork retain their own rights and remain separate from the code licence.

## Pull requests

Create a focused branch from the current `main` branch and submit a pull request to this repository. Link the relevant issue or existing project task, explain the resulting behaviour, and update affected examples and documentation. Keep unrelated changes in separate pull requests.

Report executed commands, outcomes and the commit they validate. Identify unavailable checks and remaining limitations explicitly. Follow the repository's existing review and automated-check requirements; retain required gates and current ownership. Address findings and verify the final head before integration. Repository changes do not themselves authorise a release or external operational action.

## Security, rights and conduct

Follow the [security policy](SECURITY.md). Use private vulnerability reporting if available; otherwise request a private contact without publishing vulnerability details. Keep credentials, personal information and restricted source material out of issues, fixtures, logs and artifacts.

Read the [existing licence](LICENSE) and preserve attribution and third-party terms. Follow the [code of conduct](https://github.com/edithatogo/.github/blob/main/CODE_OF_CONDUCT.md) and keep technical discussions respectful.

## Basis for this guide

This guide follows [GitHub's contribution-guideline guidance](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/setting-guidelines-for-repository-contributors) and the contribution-process and testing principles in [OpenSSF Best Practices](https://www.bestpractices.dev/en/criteria). It does not assert certification.
