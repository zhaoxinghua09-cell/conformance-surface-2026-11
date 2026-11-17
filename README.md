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

## Verify it yourself, in one command

Standard library only. No install, no credentials, no network for the offline checks.

```bash
git clone https://github.com/zhaoxinghua09-cell/conformance-surface-2026-11.git
git clone https://github.com/zhaoxinghua09-cell/evidence-gated-medical-agent-demo.git
cd conformance-surface-2026-11
python3 verify_all.py
```

Exit code 0 means every check passed; 1 means at least one did not, and the
failing rows say what was compared.

What it checks, and why each one is there:

| Group | What it asserts | Why |
|---|---|---|
| A structure | the JSON parses and the top-level keys are present | a malformed file fails everything downstream |
| B digests | every recorded SHA-256 matches the file it names | this is the record the material offers as proof |
| C offline | no HTML element pulls a runtime dependency from the network | the README says the visuals work offline |
| D demo | the reference demo runs, and its trajectory produces the stated state, evidence count, log length, model version and chain digest | four words appearing is not the same as the state machine doing what it claims |
| E language | no CJK characters in the English material | readers are told these are English documents |
| F wording | no absolute superiority claim | the material is offered as a draft, not a ranking |

The neighbour repository is optional in principle, but rows B and D cannot be
recomputed without it — `verify_all.py` reports that as a gap rather than as a
pass.

### This checker was tested against deliberate defects

A checker that only ever prints PASS is worthless, so five defects were injected
into copies of the material and the checker was run on each:

| Injected defect | Caught by |
|---|---|
| a digest overwritten with zeros | B, three rows |
| an external `<script src>` added to the visual | C |
| Chinese text appended to the README | E |
| "We are stronger than every competitor" appended to the README | F |
| the silent-failure rule removed **and the digests updated to match** | D — `receipt: PAUSE: absent from output`, `log_entries == 20: got 19` |

The last one is the one worth reading twice. Editing a file and updating its
digest is exactly how an honest correction looks, so a digest check alone cannot
tell a fix from a tamper. That is why group D compares behaviour instead.

### Known limits

- Group D runs one scenario. It does not cover the other three acts independently.
- Group B trusts the neighbour repository to be at the path beside this one; it
does not fetch it.
- Nothing here asserts that a third party did the run. It asserts that a run
  produces the stated result, which is a weaker and more honest claim.
