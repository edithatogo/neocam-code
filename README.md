# Neocam model code

Reproducible neonatal video-consultation decision modelling with NumPy, voiage and Polars on Python 3.15.1. This repository is private while its release boundary is qualified. Publication has not been authorised.

Project-owned code is Apache-2.0. This licence does not grant rights to external evidence, patient information, manuscripts or institutional artwork. Full research provenance and the clinical publication packet are retained separately, outside this repository.

The code import will be reviewed in a separate pull request. No clinical approval or independent review is implied. All four independent reviews remain pending and fiscal evidence remains open.

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

The imported code snapshot is pending its own acceptance. Historical scientific tables are retained as numerical fixtures, while private source attributions use explicit source-withheld identifiers. The complete original provenance remains private.
