# Phase 3 Checkpoint 2 — Pre-open Privacy Exception Review

## Verdict

**AUTHORIZE OPTION 2 — NARROW LEGACY REVIEW-ARTIFACT EXCLUSION**

Do **not** sanitize or rewrite `thesis-deck-system/reviews/PHASE_3_DESIGN_REVIEW.md` merely to remove the pre-existing exemplar basenames in its D3-2 historical design decision. That file is an audit record and should remain historically intact.

The repository-wide CP2-PRE-1 scanner may apply one narrowly scoped legacy exception, subject to every condition below.

## Authorized exception

- path: `thesis-deck-system/reviews/PHASE_3_DESIGN_REVIEW.md`
- reviewed blob SHA: `1808c054cc2ad5a618a9f19907ef57da79c39973`
- allowed rule exception: `forbidden_private_basename` only
- allowed content scope: only the already-existing exemplar-basename occurrences in section `D3-2 — Private exemplar roles remain asymmetric`
- reason: this pre-existing reviewer record intentionally documented the exemplar-role mapping before the repository-wide scanner became a production pre-open gate; rewriting it would mutate historical review evidence while not removing the value from Git history.

## Non-negotiable limits

1. This is **not** a path exclusion. Absolute paths, WSL paths, UNC paths, URLs/DOIs, notes, media names, OOXML fragments, private renders, or any other forbidden classification in this file must still fail the scanner.
2. This is **not** a directory exclusion. No other file under `thesis-deck-system/reviews/` is exempt.
3. This is **not** a future-content exclusion. If the file blob changes, the exception is invalid until re-reviewed.
4. This is **not** permission to copy those basenames into new reports, tests, schemas, source files, artifacts, profiles, or task files.
5. Production committed artifacts must continue to use only stable aliases such as `private://template_primary_1`, `private://layout_exemplar_2`, and `private://template_primary_3`.
6. The scanner must record that the legacy exception was encountered; it must not silently skip the file.
7. The pre-open QA evidence must include a sanitized exception record containing only the repository-relative path, reviewed blob SHA, rule ID, exception ID, and status. Do not echo the exempted basename value.
8. The exception must be applied after confirming the current blob SHA matches the reviewed blob SHA. A mismatch is a hard failure.
9. CP2-PRE-1 passes only if there are zero unexcepted privacy findings after this exact exception is accounted for.

## Required implementation evidence

Before any production private alias is resolved or opened, add RED/GREEN tests proving:

- the exact reviewed blob + exact `forbidden_private_basename` legacy occurrence is recorded as an approved exception rather than a failure;
- changing the file content/blob invalidates the exception;
- adding an absolute private path to the same file still fails;
- adding another forbidden basename outside the authorized historical occurrence still fails;
- the same basename in any other file fails;
- copied occurrences in new reviewer/report/task files fail;
- the exception record never contains the raw basename;
- zero production alias/source access occurs before the exception-aware repository scan passes.

## Authorization

Codex may proceed with Checkpoint 2 only after implementing and passing this narrow exception mechanism plus all other mandatory CP2 pre-open gates.

No production private PPTX may be resolved/opened before those gates pass.
