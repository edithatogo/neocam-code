# Library and workflow integration

The checked revisions identify the material reviewed. Only the Conductor entry is a Git submodule. The model uses a year gate for NWAU and NEP. Routine GEN_WAU exports can supply the NWAU and QWAU measures separately. Aggregate scenarios run without raw records.

| Repository and checked revision | Use in Neocam |
|---|---|
| neocam [d7e438a09](https://github.com/edithatogo/neocam/commit/d7e438a098a5c8b5f4c8a86bd68836228c1efa5b) | Subject repository. The revision identifies the enumerated default branch. |
| conductor-next [137c1e41f](https://github.com/edithatogo/conductor-next/commit/137c1e41ff9c1dc75ff277b9582460a0bd8c4768) | Workflow submodule. The Git link pins the implement and review protocol. |
| mchs [9fc8d0f33](https://github.com/edithatogo/mchs/commit/9fc8d0f33df2aabaef8d4a10f25df12d41ff033e) | Methods reference for NWAU and NEP. The reference review involved no execution or copying of mchs code. NEP26 parity awaits validation. QWAU and QEP are accounted for separately. |
| microcosting_healthworkforce [dd61438f1](https://github.com/edithatogo/microcosting_healthworkforce/commit/dd61438f15db91a0cb51e403f9ec137c7e589b2d) | Methods reference for rate conversion and indexation. Salary values require their own sources. |
| vop_poc_nz [ad84d3090](https://github.com/edithatogo/vop_poc_nz/commit/ad84d3090a2d97f2805a86e94a7b9614a3d1ab14) | Methods provenance for the fixed-decision comparison now executed by voiage. |
| voiage [3.1.0](https://pypi.org/project/voiage/3.1.0/) | Runtime engine for cost-only EVPI, directional regret and tie-aware selection. Neocam supplies network-year units, eligibility and tie bounds. |
| reimbursement-atlas [a93516ed4](https://github.com/edithatogo/reimbursement-atlas/commit/a93516ed416118bc51c1db2b71ab540fa4d0fe52) | Provenance reference for workbook entry G2. |
| template-solo-data [4abb00d24](https://github.com/edithatogo/template-solo-data/commit/4abb00d24ec2738da7b23dfb2c6e5eeaf03bed97) | CI pattern comparison for workflows, dependency updates and OIDC. |
| careops-rims [8fdc68f09](https://github.com/edithatogo/careops-rims/commit/8fdc68f09a2bdbb9dc1ab0bc39743e810fef6714) | Privacy workflow reference. Neocam tests its own scanner against synthetic identifiers and aggregate data. |
| sourceright [6e2a69cba](https://github.com/edithatogo/sourceright/commit/6e2a69cba6bf65c35bef65c193b3e91b46df5c91) | Candidate citation-verification source. Existing citation receipts retain their original verification status. |
| riopa-infrastructure [da1fc847a](https://github.com/edithatogo/riopa-infrastructure/commit/da1fc847a92cfa5b41e2dae01812554c10eba74e) | Documented reference for provenance and reproducibility patterns. |

The design records the adjacent repositories and the reasons for excluding them. [Design inventory](../conductor/v14-design.md)

## CI decisions

The solo-maintainer template delegates to the pinned repository-standards data workflow. Its defaults use Python 3.14, an editable pip install, a covered pytest run and a required Codecov OIDC upload. Neocam keeps its frozen Python 3.15 environment, one covered suite and the project-specific assurance gates. Adding an external coverage upload would introduce a new recipient without filling an acceptance requirement. [Template workflow](https://github.com/edithatogo/template-solo-data/blob/4abb00d24ec2738da7b23dfb2c6e5eeaf03bed97/.github/workflows/ci.yml) · [Delegated workflow](https://github.com/edithatogo/repository-standards/blob/7e5c4cc2ae02d8a2cb0cf911a7d4bb6eb890d5ff/.github/workflows/data-ci.yml)

The template explicitly grants the reusable workflow the OIDC permission it needs. Neocam applies that pattern to the manual release caller. The assurance job has read-only repository access. After a successful non-PR run, a separate job signs the uploaded archive digest without checking out or executing project code.

The template extends a shared Renovate preset. Neocam keeps its explicit weekly Brisbane schedule, digest pinning, release-age policy, security priority and manual merge decisions. Both projects already run Scorecard with pinned actions and publish SARIF. Neocam keeps its hardened runner and bounded evidence retention. [Template Renovate settings](https://github.com/edithatogo/template-solo-data/blob/4abb00d24ec2738da7b23dfb2c6e5eeaf03bed97/renovate.json) · [Template Scorecard](https://github.com/edithatogo/template-solo-data/blob/4abb00d24ec2738da7b23dfb2c6e5eeaf03bed97/.github/workflows/scorecard.yml)
