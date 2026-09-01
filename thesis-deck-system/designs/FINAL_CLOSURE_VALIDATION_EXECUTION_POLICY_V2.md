# Final Closure Validation Execution Policy V2

## Purpose

This policy reduces repeated Codex interruptions and long validation cycles without weakening acceptance evidence. It governs the final closure sprint only unless later adopted more broadly.

## Core rule

A result is acceptance-eligible only when it is bound to one frozen candidate and has durable completion evidence. A test run is **not** rejected merely because it ran outside a single monolithic process; it is rejected when candidate identity, collection coverage, completion status, or privacy evidence cannot be proven.

## Candidate freeze

Before any acceptance-eligible focused or full validation:

1. capture the candidate-state hash using the existing authoritative candidate hash function for the affected scope;
2. capture `git status --short`, tracked/staged diff summary, and current HEAD;
3. persist these facts before launching the long-running process;
4. do not modify candidate-affecting files while the run is active;
5. after the run, recompute the same candidate hash and require PRE == POST == CURRENT.

If the final candidate hash is not known before a run starts, that run is preliminary only and must not be repeated accidentally as final evidence.

## Durable process evidence

Every long-running validation process must persist:

- command/argv or a stable runner action ID;
- candidate hash captured before start;
- start timestamp;
- stdout log path;
- stderr log path;
- exit-status path/value;
- end timestamp;
- post-run candidate hash;
- collection/test counts when available.

The runner should write the exit status in a `finally`/wrapper path so a completed process cannot be discarded solely because Codex lost the interactive shell output.

Do not poll aggressively. Launch once, allow the process to run, and inspect the durable result files when tool access is available.

## Validation tiers

### Tier 0 — preflight

Cheap checks only:

- authorized-diff/workspace classification;
- `git diff --check`;
- schema syntax/closure for directly touched schemas;
- candidate hash computability;
- privacy config/attestation interface availability.

Purpose: reject obvious blockers before spending minutes on tests.

### Tier 1 — targeted RED→GREEN

Run only tests directly proving the implementation change. Keep each correction loop narrow.

A failed targeted test may be corrected and rerun without invoking broader suites.

### Tier 2 — focused closure suite

Run the affected checkpoint/final-composition/privacy/native-parity suites plus essential cross-gate invariants.

This is the last stage at which implementation changes should normally occur.

### Freeze boundary

After Tier 2 passes:

- freeze the candidate;
- capture the acceptance candidate hash;
- regenerate only execution-derived evidence that is explicitly excluded from candidate identity, if the existing contract permits it;
- do not make implementation changes unless the definitive regression finds a real defect.

### Tier 3 — definitive full regression

Run exactly once against the frozen candidate, except when it finds a real defect or the run itself is environment-invalid/incomplete.

A real product/test defect requires correction, a new candidate hash, focused revalidation, and one new definitive regression. Missing durable evidence is prevented by the runner and should not trigger a blind rerun.

## Full regression sharding

The authoritative full regression may use shards if sharding is available without a risky infrastructure rewrite.

Requirements:

1. collect the complete authoritative test node list for the package;
2. deterministically assign every node to one shard;
3. all shards use the exact same candidate hash/commit;
4. persist per-shard node lists, logs, and exit codes;
5. aggregate the union of executed node IDs;
6. require `executed_union == authoritative_collection`;
7. require no omitted nodes;
8. duplicates must be zero, or explicitly normalized with proof that every authoritative node ran at least once and duplicate execution is not counted as extra coverage;
9. every shard exits 0;
10. candidate hash is unchanged after all shards.

Recommended logical shards if local/CI concurrency is practical:

- core + Phase 1/2 unit contracts;
- Phase 2 integration/build/PPTX;
- CP1–CP5-G;
- CP5-H/I + final composition + privacy/release.

If parallel sharding is not practical, the same manifest can still run shards sequentially to gain durable restartability and better diagnostics; however, do not claim wall-clock acceleration unless measured.

## Expensive fixture reuse

Within a pytest process:

- expensive immutable acceptance builds should be session/module-scoped where isolation allows;
- each production pipeline retains at least one true clean rebuild test;
- dependent QA tests consume the frozen build read-only;
- mutation tests copy structured objects or use copy-on-write temp directories;
- no test may mutate a shared fixture in place.

## Timing evidence

For performance work:

- run `pytest --durations=25` (or equivalent runner timing capture) before optimization when feasible;
- record the same metric after optimization;
- report absolute wall-clock and top slow nodes;
- do not state percentage speedups from intuition.

If a pre-change timing run would consume excessive time, use the most recent completed acceptance run as baseline and state the limitation explicitly.

## Privacy execution order

Privacy should not be the first expensive step, but privacy interface availability must be preflighted.

Recommended order:

1. Tier 0 privacy-config/attestation interface preflight;
2. implementation/focused tests;
3. candidate freeze;
4. definitive full regression;
5. execution-owned generated-PPTX attestation;
6. authoritative repository + staged privacy scan;
7. report/commit/push/remote verification.

If the privacy adjudicator itself affects candidate identity, it must be implemented and tested before the freeze and only its final execution evidence may be generated afterward if the existing candidate-hash policy permits that.

## Commit policy

To minimize lost work without polluting accepted history:

- local bounded gate commits are allowed after focused GREEN if the workspace policy permits them;
- do not push a final review-ready commit before the definitive regression and privacy gates pass;
- do not rewrite or clean unrelated paths;
- do not create cleanup commits for generated artifacts unless the path is explicitly authorized.

## Stop policy

A Codex session may stop because of tool/usage limits without invalidating already persisted evidence.

When tool access is close to exhaustion:

- do not start a new expensive phase;
- persist a compact recovery record containing candidate hash, completed tiers, active process/log paths, and next action;
- leave the workspace unchanged;
- do not claim readiness.

When resumed, inspect durable evidence first. Do not rerun completed acceptance-eligible work merely because the previous chat/session ended.

## Anti-loop rules

The following are prohibited because they caused repeated wasted runs in prior checkpoints:

- starting a long run before capturing the tested candidate hash;
- relying only on terminal text without an exit-status artifact;
- rerunning a completed suite because stdout was lost;
- running the full regression after every small correction;
- running privacy only after all other work when the privacy interface itself is unknown;
- letting a test write generated previews into source/fixture directories;
- broad cleanup/restoration without an explicit allowlist;
- modifying the candidate while a definitive process is still running.

## Acceptance summary format

The final report should state:

- candidate hash;
- focused tests pass/fail;
- authoritative full collection count;
- full regression execution model;
- per-shard or single-process pass/fail and exit status;
- collection coverage equality;
- pre/post/current hash equality;
- duration evidence;
- repository/staged privacy findings;
- generated-PPTX attestation count/status;
- private access counters;
- commit/push/remote verification;
- truthful blocked/not-run release dimensions.
