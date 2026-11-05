# Neocam model code

Reproducible neonatal video-consultation decision modelling with NumPy, voiage and Polars on Python 3.15.1. The code repository was made public with explicit owner approval on 5 November 2026. The original research repository remains private.

Project-owned code is Apache-2.0. This licence does not grant rights to external evidence, patient information, manuscripts or institutional artwork. Full research provenance and the clinical publication packet are retained separately, outside this repository.

The clean code import was reviewed and merged through PR #1. No clinical approval or independent review is implied. All four independent reviews remain pending and fiscal evidence remains open.

## Reproduction and acceptance

Read [the runbook](conductor/runbook.md) and [code release contract](docs/code-release-contract.md). Use the frozen Python 3.15.1 environment. NumPy supplies numerical arrays, voiage 3.1.0 supplies information values, and Polars is the only permitted DataFrame engine. Pandas and xarray are excluded.

The model can be reproduced without the withheld institutional Office templates:

```sh
uv run --frozen --extra tabular --extra research --extra reporting python -m scripts.reproduce --output outputs/reproduction
uv run --frozen python -m quality.artifacts verify --output outputs/reproduction
```

Use a new output directory for each scientific rerun. Then run the complete acceptance profile:

```sh
uv run --frozen --group assurance --extra tabular --extra research --extra reporting python -m quality.cli --profile full --evidence-version v41
```

The imported source at `47e4465` passed all 32 local acceptance gates on Python 3.15.1, including 1,159 tests and 99.44% mutation coverage with zero errors, timeouts or pardons. Merged source `3d69e04` passed all 32 hosted gates; its downloaded evidence archive, receipt log digests and cryptographic attestation were verified. See [the accepted source receipt summary](verification/code-release/accepted-main.json). Later commits require their own hosted verification. Historical scientific tables are retained as numerical fixtures, while private source attributions use explicit source-withheld identifiers. The complete original provenance remains private.
