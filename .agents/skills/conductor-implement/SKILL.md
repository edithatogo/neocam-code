---
name: conductor-implement
description: Use when the user requests Conductor implement for this repository.
---
# Conductor implement: repository adapter
Read conductor/index.md, workflow.md, product-guidelines.md and only the selected track's spec/plan.
Pinned upstream protocol and blob identities: conductor/skill-provenance-v13.json.
This is an explicit local adaptation, not a claim that the Conductor executable/submodule is installed.
Apply the internal-browser-only rule in conductor/runbook.md for sign-in,
reauthentication, opening/loading pages, web interactions and browser QA. Exceptions
need explicit user direction covering the operation; report limitations rather than
substituting an external browser or bypassing authentication.
Select the specified incomplete track; mark [~]; execute tasks in order with reproducing failing tests, minimal implementation, passing scoped tests and separate commits. Reconcile plan/metadata after each task. Review each completed track using conductor-review before marking its implementation complete. Preserve blocked external acceptance. Do not delete history or publish/merge without authority.

## Authored Word deliverables

Follow the repository typography and CLI conversion workflow in
`docs/document-formatting.md`. Use `assets/neocam-document-styles.docx` for current
manuscript documents. Save and close Word documents before editing. Verify the
Normal and Heading 1–3 styles by reading the generated DOCX after conversion.
