# Conformance-surface visual — Nov 2026 contributions

Public, human-facing companion to the **W3C s-agent-comm** and **ITU FG-TIDA**
contributions prepared by **Xinghua Zhao** (individual participant, ORCID
0009-0001-0512-1237). Licence: **CC BY 4.0**.

## What is here
- `S8_visualization.html` — best-quality interactive visual (evidence-grading
  cards, four-checks explorer, 9-step medical-agent lifecycle, S5.1 outsider
  re-run table, red-team top-3, direct references). Theme-aware, fully
  self-contained, works offline. **Open it directly in a browser.**
- `checks.json` — machine-readable dual form of the same material (schema
  `intl-contrib-checks/v1`): evidence grades, the four checks with pass/fail
  criteria, lifecycle, S5.1 results with full SHA-256 digests, red-team log,
  and primary-source reference URLs.

## Why public
Both contributions were produced under the participation pipeline
(research → red team → outsider zero-credential re-run → external-AI review →
visualization → attribution). This repository lets any outside reader
**zero-credential reproduce and inspect** the materials, per the requirement
that all our GitHub-hosted contributions be testable from an outsider view.

## Outsider re-run target
The technical axis is demonstrated on a dependency-free, Apache-2.0 reference
implementation:
https://github.com/zhaoxinghua09-cell/evidence-gated-medical-agent-demo
(standard-library only; `python lgd_medai_demo.py`; observed exit 0, 7/7 SHA
match, receipts DENIED · PAUSE · ROLLBACK · RESUMED). Reproducibility is a
contributor-run demonstration, **not** a third-party attestation.

## Honest scope notes
- Evidence grades (V/S/M/L/P) are an *input* vocabulary adapted from a
  GRADE-style scheme (BMJ 2008); they are not a verdict and not affiliated
  with the GRADE Working Group.
- Checks 3–4 read the group's own enumerated scope vocabularies
  (capability / intent / conformance); they do not propose new normative text.
