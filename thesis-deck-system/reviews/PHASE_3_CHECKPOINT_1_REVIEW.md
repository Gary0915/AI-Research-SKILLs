# Phase 3 Checkpoint 1 Review

**Reviewed implementation:** `9b4d17544866a2328dbfd6d74f8c3b431728ba71`

**Verdict:** REVISE

Checkpoint 1 made substantial progress and the provider/figure/fabrication contract direction is correct. The full regression result and the no-private-open scope are encouraging. However, Checkpoint 2 is the first stage that is authorized to touch the real private exemplars, so the safety evidence itself must be non-self-certifying before that authorization is granted.

## CP1-B1 — checkpoint QA record is self-certifying

`phase3_checkpoint.py` currently constructs `checkpoint1_qa_record()` with literal values:

- `private_source_open_attempts: 0`
- `real_private_alias_resolution_attempts: 0`
- privacy/provider/figure/Observation/fabrication statuses: `pass`

The function receives only `phase1_phase2_regression_status`. Therefore the committed QA artifact does not derive the zero-attempt counters or the PASS statuses from executed owning checks. If a future code path accidentally opened/resolved a private source, this builder could still emit zero. This is a certification bypass.

Required correction:

1. Introduce an execution-derived Checkpoint evidence object / guard ledger.
2. Private-source open and alias-resolution entry points must increment/record attempted operations before performing the operation.
3. Checkpoint 1 must run with an explicit policy that rejects any such attempt.
4. QA statuses must be derived from persisted owning-check results, not literal `pass` values.
5. A negative test must prove that a simulated private-open or alias-resolution attempt makes Checkpoint 1 QA FAIL and cannot still serialize zero.

Checkpoint 2 may not be authorized until this is corrected.

## CP1-B2 — privacy path/basename detection is incomplete for the real execution environment

The current absolute-path regex catches Windows drive/UNC paths and selected `/home` or `/Users` paths, but does not generically cover mounted Windows paths such as `/mnt/d/...`, which are realistic in WSL/Codex execution. The basename scanner also focuses on synthetic `private-*` canaries; a private source basename by itself can cross the boundary without an absolute path and should still be forbidden.

Required correction:

- add WSL/mounted-drive and generic configured-private-root path canaries;
- make scanner policy accept dynamically supplied forbidden private basenames/fingerprints without committing the private value to findings;
- add tests proving a basename-only private PPTX/render/media leak is rejected;
- findings must record only classification/location/rule ID, never the forbidden value.

## CP1-B3 — empirical Observation validation trusts self-declared origin too much

`validate_observation_visual_binding()` currently accepts an inline evidence-catalog item when its `origin` string is one of the empirical origins. An arbitrary/generated object can therefore masquerade as empirical evidence by self-declaring `origin: measurement` unless the caller separately proves canonical Evidence/FigureOutput provenance.

Required correction:

- Observation evidence must resolve through canonical evidence/output IDs and validated provenance, not an arbitrary embedded dictionary;
- concept/generated outputs must remain ineligible even if a caller falsifies an empirical-looking origin string;
- add cross-contract negative tests for generated/concept output with spoofed `measurement`, `experimental_photo`, or `source_derived_scientific_visual` origin.

## Accepted work to preserve

Preserve the existing Checkpoint 1 work unless required for the fixes above:

- ignored private root and pre-open guard;
- fail-closed whitelist sanitizer;
- provider-neutral `ImageReviewProvider` with private authorization/egress/retention gates;
- `ConceptImageProvider` non-evidence boundary;
- discriminated Figure Output contract;
- fabrication-process contract and routing foundation;
- Phase 1–2 regression compatibility;
- no real private exemplar access during Checkpoint 1.

## Reviewer gate

Checkpoint 1 remains **not approved**. Do not open/profile/resolve the three production private exemplars yet. Submit a narrowly scoped Checkpoint 1 revision addressing CP1-B1 through CP1-B3, with execution-derived QA evidence.
