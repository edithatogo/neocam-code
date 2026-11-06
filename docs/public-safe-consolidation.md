# Public-safe consolidation

The owner authorised a scoped port from the private research consolidation on
6 November 2026. The public repository retains its clean history. No private
commits are merged or cherry-picked.

## Disposition

| Change group | Public disposition |
|---|---|
| VoI, registry and billing scenarios, geographical decision code and tests | Already present on public main; preserve their existing qualified implementation. |
| Native security engine, complete rule inventory, source projection and diagnostic rejection | Already present; preserve every existing gate and source review. |
| Citation-regex parser repair | Port the generic regex as a native scanner safe control, paired with an unsafe evaluation control. This exercises the repaired syntax and requires the scanner to distinguish safe parsing from code execution. |
| Source-withheld identifiers and privacy coverage oracle | Preserve the public forms; private source names and the older file-count assertion must not replace them. |
| Manuscript authoring, clinical interpretation and editorial assessment | Retain privately, including the authoring scripts and manuscript-specific regression test. |
| Source documents, Word originals, unpublished packet, private evidence and historical logs | Retain privately; no publication through this port. |

The citation control uses explicit punctuation alternatives and possessive
quantifiers. It avoids the character-class spelling that caused the qualified
native scanner to abort on a Unicode dash, while retaining the intended citation
syntax. Both the safe and unsafe fixture must complete all pinned native rules;
scanner warnings, missing rules or missed unsafe evaluation remain failures.

## Acceptance boundary

Use focused local checks, then the four protected required PR checks. No model
recalibration, new estimates, weakened thresholds or duplicate local full run is
needed. Merged-main acceptance is separate from PR checks. Historical full
receipts retain their original commit identity.

The original research repository remains private. The author Word edit is
unchanged. The fiscal evidence track remains open; no clinical or fiscal approval
is implied by this software port.
