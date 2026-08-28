# Task — Phase 3 Checkpoint 1 Revision

## Scope

Correct only the remaining Checkpoint 1 safety/evidence blockers from `reviews/PHASE_3_CHECKPOINT_1_REVIEW.md`.

Do **not** begin Checkpoint 2. Do **not** resolve, open, profile, hash, render, or otherwise access the three production private exemplar aliases/files.

## CP1-B1 — execution-derived checkpoint evidence

Replace self-certifying Checkpoint QA with execution-derived evidence.

Required behavior:

1. Add a typed guard/evidence object owned by the Checkpoint execution.
2. Private alias resolution and private source open APIs must record an attempt before any operation occurs.
3. Under Checkpoint 1 policy, any private alias-resolution/open attempt must fail immediately and make checkpoint status fail.
4. `private_source_open_attempts` and `real_private_alias_resolution_attempts` in the committed QA artifact must be derived from the execution evidence object.
5. Privacy/provider/Figure/Observation/fabrication statuses must be computed from owning check results; the QA writer may not literalize PASS.
6. Persist check IDs/evidence refs sufficient to audit how each final status was derived.

Negative tests must prove:

- simulated alias resolution increments evidence then blocks;
- simulated private source open increments evidence then blocks;
- a nonzero attempt count cannot serialize as zero;
- an owning-check failure cannot serialize as PASS;
- a caller cannot manually construct a passing final record that bypasses owning evidence.

## CP1-B2 — private path and basename coverage

Strengthen privacy scanning before private access is authorized.

Required behavior:

- detect Windows drive paths and UNC paths;
- detect WSL mounted-drive paths such as `/mnt/<drive>/...`;
- support configured/local private roots without storing the forbidden raw value in committed findings;
- detect forbidden private source basenames even when no path is present;
- detect private render/media/PPTX basename-only leakage;
- findings expose only rule/classification/location and sanitized identifiers.

Use synthetic canaries in committed tests. Do not place actual private paths/content in fixtures or reports.

Add negative tests for:

- `D:\\...` path;
- `D:/...` path;
- `/mnt/d/...` mounted path;
- UNC path;
- basename-only `.pptx` private canary;
- basename-only private render/media canary;
- nested mapping/list leakage;
- no raw forbidden value echoed in findings.

## CP1-B3 — canonical empirical Observation provenance

Harden Observation evidence validation.

Required behavior:

1. `observation_evidence_ref` must resolve to a canonical validated Evidence/output identity, not an arbitrary embedded origin dictionary.
2. Validation must bind the evidence to provenance and evidence status/type.
3. Concept/generated outputs remain ineligible for empirical Observation evidence regardless of a spoofed origin string.
4. Auxiliary generated concepts are allowed only as separately bound `non_evidence` visuals.

Negative tests must reject generated/concept objects that spoof:

- `origin=measurement`;
- `origin=experimental_photo`;
- `origin=source_derived_scientific_visual`.

Positive synthetic tests must cover a canonical measurement and a canonical real-photo evidence binding.

## Preserve

Do not regress accepted Checkpoint 1 behavior, Phase 1–2 tests, schemas, provider privacy gates, discriminated Figure outputs, fabrication-process routing, or the no-private-access rule.

## Required evidence

Regenerate `artifacts/phase3/checkpoint-1-qa.json` from actual execution evidence.

The QA record must include at least:

- checkpoint ID;
- execution evidence ID/hash;
- private source open attempt count;
- private alias resolution attempt count;
- owning check IDs/results for privacy root, sanitizer/scanner, provider authorization, Figure contracts, Observation evidence, fabrication contracts, and regression suite;
- aggregate checkpoint status.

The artifact must fail schema/QA if any required owning evidence is absent or inconsistent.

## Tests / checks

Run:

- revised Checkpoint 1 suite;
- full Phase 1–2 + Checkpoint 1 suite;
- Phase 3 schema validation and primitive-type audit;
- repository/staged privacy scans;
- checkpoint evidence consistency validation;
- report/footer validation;
- `git diff --check`;
- remote branch/artifact verification.

## Report

Update:

`thesis-deck-system/reports/PHASE_3_CHECKPOINT_1_IMPLEMENTATION_REPORT.md`

Add explicit CP1-B1–CP1-B3 traceability and distinguish reported facts from execution-derived canonical evidence.

## Delivery

Commit and push the revision to `origin/codex/thesis-deck-system` and verify the remote branch/artifacts.

Return:

repository:
branch:
commit SHA:
pushed:
remote verification:

report path:

files added:
files modified:
files deleted:

tests/checks run:
tests passed:
tests failed:

CP1-B1:
CP1-B2:
CP1-B3:

execution evidence ID/hash:
private source open attempts:
private alias resolution attempts:
checkpoint aggregate status:

privacy scanner mounted-path test:
privacy scanner basename-only test:
Observation spoofed-origin tests:
Phase 1–2 regression status:

known failures:
technical debt:
unresolved questions:

READY_FOR_CHECKPOINT_1_REVIEW: yes

Then STOP. Do not begin Checkpoint 2 and do not access the production private exemplars.
