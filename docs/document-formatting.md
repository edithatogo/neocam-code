# Word document formatting

Use Times New Roman throughout current authored documents, with proper Word paragraph
styles. Normal is 12 pt. Heading 1 is 14 pt bold, Heading 2 is 12 pt bold, and
Heading 3 is 12 pt italic with bold off. Use heading levels in source Markdown to
produce the corresponding styles and navigation outline.

Before CLI edits save and close open documents in Word. Verify their paths first.
The maintained reference is assets/neocam-document-styles.docx. For the current
manuscript packet run from the repository root:

```sh
pandoc docs/manuscript/manuscript.md --reference-doc=assets/neocam-document-styles.docx -o docs/manuscript/manuscript.docx
pandoc docs/manuscript/cheers-checklist.md --reference-doc=assets/neocam-document-styles.docx -o docs/manuscript/cheers-checklist.docx
pandoc docs/manuscript/panel-response.md --reference-doc=assets/neocam-document-styles.docx -o docs/manuscript/panel-response.docx
```

Neutralise generated metadata with scripts.document_metadata after conversion.
Read back styles and paragraph style IDs with python-docx. Explicit font names
must not retain conflicting theme-font attributes. The active reference Title is
black with no decorative paragraph border. The heading-font regression
checks the maintained reference, and assurance fingerprints its bytes. The current
clinical packet is verified separately outside Git. The older tracked drafts remain
historical source records; do not retrofit their frozen bytes. The Markdown is the
authoritative editable text for these drafts. Apply this workflow to future
authored Word deliverables. Historical retained analyses remain bound to their
frozen manifests; new manuscript drafts are versioned separately.

## Review manuscript spacing — 3 November 2026

Use black Times New Roman, 1.5-spaced ordinary manuscript text, zero ordinary
space-before/after and one paragraph break between ordinary paragraphs. Save
Heading 1–3 space-before as 18 pt (one 12 pt body line at 1.5 spacing), with zero
space-after. This intentional heading gap is not a redundant spacer. Do not add
empty spacer paragraphs, double an existing gap or add a leading blank at page top.

Put each structured-abstract label on its own paragraph, followed immediately by
its text paragraph. Use the proper heading style and preserve the same one-line
gap before the label. In Markdown, use a blank source line before headings and
follow the renderer's required syntax. Preserve citation fields and human edits.

Enable continuous line numbering in review manuscripts; do not restart numbering
at each page or apply it indiscriminately to other document kinds. Verify saved
effective styles and actual rendered separation. Record any journal exception.
The current private packet retains single-spaced editable tables for dense tabular
material; ordinary body paragraphs remain 1.5-spaced. Do not modify retained
historical or author-edited Word files to retrofit the new defaults.
