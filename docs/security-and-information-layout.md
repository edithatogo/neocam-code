# Security and information separation

The owner approved publishing only `edithatogo/neocam-code` on 5 November 2026.
The original `edithatogo/neocam` research repository remains private. No original
research history was imported into the new code repository.

| Material | Location | Control |
|---|---|---|
| Model and developer source | `src/`, `scripts/`, `quality/`, `tools/`, `.agents/` | Versioned source, exact-source security review and numerical assurance. |
| Model inputs and simulation fixtures | `data/`, `config/`, `evidence/`, `sources/`, `outputs/`, `verification/` | Provenance manifests; withheld source identifiers; simulations distinguished from patient observations. |
| Generic Word styles | `assets/neocam-document-styles.docx` | Reviewed generic template; institutional artwork and inherited staff metadata excluded. |
| Current clinical manuscript, supplement, checklist and workbook | External clinical publication workspace | Current external publication copy excluded from this release; earlier drafts remain in the original private research history. |
| Patient extracts and private source originals | External private evidence workspace | Outside repositories; no repository symlink or automatic upload. |
| Original research history and author Word edit | Original private research workspace | Retained separately; author edit unchanged and uncommitted. |

The code publication audit covered the complete selected history and all reviewed
binary identities. The 31 NumPy archives contain 418 numeric arrays loaded without
pickle. The 105 reviewed binary paths include generated plots, a generic style
file and an unbranded model report. They contain simulation fixtures, not patient
extracts. Private source locators and personal-communication identities are withheld;
the complete source mapping remains private. Existing numerical results are unchanged.

An ignored directory inside a checkout does not provide the protection of keeping
patient files outside the repository. Local guards additionally reject known
confidential paths, hashes, removed ancestry and links into private storage. Known
private history backup hashes are registered too, so renaming a backup does not
make it eligible for a commit. Private guard rules and findings stay outside Git.

## Privacy checks and their limits

Commit and push guards reject known confidential paths, source hashes, removed
confidential ancestry and links into private storage. Gitleaks scans staged content
and complete Git history. The repository privacy gate scans supported text and
document containers and proves rejection with synthetic fixtures. A supplementary
local pattern scan flags candidate emails and financial identifiers for review.

These checks do not prove that disclosure never occurred. Historical sanitation
records describe previously removed material. Pattern scanners cannot establish
consent, publication rights, clinical context or the identity of every name in free
text. Opaque images and binary records require provenance and, where applicable,
visual inspection. Report actual scan scopes and unresolved findings explicitly.

## GitHub controls

Main branch protection requires assurance, privacy, dependency review and static
application security. It applies to administrators and rejects force pushes and
deletion. Actions use a selected SHA-pinned allowlist, least-privilege token permissions
and egress auditing. Dependency alerts are enabled.

Native GitHub secret scanning and push protection were enabled and read back after
the approved public visibility change. No native secret alerts were reported at the
5 November 2026 readback. Local Gitleaks and identifier checks remain mandatory.
The qualified OpenGrep/Bandit scanner remains required; making the repository public
does not substitute a different, unqualified analysis engine.

Four independent reviews remain pending. The fiscal evidence track remains open.

## Free scanner qualification

The replacement uses the unchanged stable OpenGrep 1.33.1 native core, Bandit
1.9.4 and all 378 pinned upstream Python-folder rules, including generic and regex
rules. The isolated Python 3.15.1 environment contains Bandit, PyYAML and their
resolved dependencies. It rejects pandas, xarray and the Semgrep Python CLI, MCP
and OpenTelemetry packages. Native archives, executables and the retained upstream
LGPL licence are digest-verified. The native engine itself has no Python dependency
graph. The root lock, isolated lock and native upstream commit are audited for
known vulnerabilities without advisory exclusions.

The Semgrep Python CLI was rejected after its pinned dependencies produced five
advisories. Its native engine was also rejected after reproducible fixpoint
timeouts. An experimental OpenGrep interfile build was rejected for parser and
inventory failures. These trials remain external qualification evidence and are
not the accepted runtime. The stable native core passes the project inventory and
synthetic controls. Its algorithms differ from CodeQL and do not provide an
identical automatic interfile query engine.

Every tracked Python file is parsed by Python 3.15. The scanner makes temporary
syntax-compatible copies. Lazy imports become ordinary imports; optional exception
tuple parentheses are restored; simple type aliases retain their complete value
expression as assignments; unbounded generic declarations retain their complete
function or class bodies and annotations. No expression may be removed. Native AST
equality is checked after these explicit declaration normalizations. Bounds,
defaults, generic aliases and unsupported spellings fail closed. Source line counts
are retained. Original source remains the Bandit input. The evidence records both
source and projection hashes. Twenty-two positive/safe controls include calls inside
generic declarations, deferred aliases and exception handlers. Both engines must
independently detect every positive case; safe controls must remain nonblocking.

All configured rule identities and all source files must appear in their expected
inventories. Skipped rules, unsupported syntax, scanner errors and warning diagnostics
are blocking, including warnings absent from the JSON error list. Suppression
comments are disabled and explicitly tested. Medium/high-confidence native security
findings require correction. Bandit retains all severities and blocks medium/high
findings. Low-confidence audit/style suggestions require an exact rule, location
and full-file hash in the reviewed inventory. Every added, removed or modified
Python file invalidates the software source review, even without a scanner finding.
The ordinary assurance fingerprint binds scanner code, dependencies, licence, rules
and review inventory. This source review is separate from the four pending clinical
reviews. It is a bounded software assurance claim, not proof that no vulnerability
can exist.

The upstream rule bundle is downloaded, digest-verified and used internally. Its
licence prohibits redistribution, so the bundle is excluded from Git and retained
reports. Native scans run locally without a cloud token or code upload. Original
and projected source are processed in the local checkout or GitHub CI without a
Semgrep cloud token. The upstream rules are excluded from Git and retained reports.
Software verification receipts and logs for this public code repository are public
GitHub artifacts; private evidence and clinical files are not included.

The new code history audit found no registered confidential source bytes or blocked
paths. The original research history remains private; this code audit does not
establish that historical copies or provider caches of other repositories have been erased. The local guard covers the current external
ClinicalResearchEvidence vault and registered private source files. Synthetic
exact-hash and private-symlink controls were rejected. Current clinical publication
drafts and original uncommitted author documents are protected by exact hash.

Installed GitHub Apps operate under account-level permissions. This repository audit
does not certify their complete installation scope or data-handling terms. Automated
syntax comments were checked against the required Python 3.15.1 compiler and executed
tests; they were older-runtime false positives and required no source changes.

All four independent reviews remain pending. The fiscal evidence track stays open.
