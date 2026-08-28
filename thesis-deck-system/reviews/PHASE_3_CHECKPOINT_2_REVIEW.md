# Phase 3 Checkpoint 2 — Reviewer Review

## Verdict

**REVISE**

Checkpoint 2 successfully crossed the private boundary without exposing the three source paths/basenames, processed exactly the three authorized aliases, retained zero private renders, and preserved the reviewer-authorized legacy exception. The private-access/privacy-control direction is accepted.

However, the committed structural-profile boundary is not yet sufficient or fail-closed enough to authorize the Professor Visual Grammar resolver/calibration checkpoint.

## CP2-B1 — Structural profiler is materially underpowered for the approved calibration design

The current shell profiler records slide size, master/layout counts, per-slide shape count, and a constant `safe_content_bounds` value. It does not measure the required shell evidence such as master→layout topology, title/header/footer/page-number/navigation geometry, recurring shell-object geometry, actual safe bounds, margins/gutters, typography hierarchy, font family/size/weight/style roles, theme/fill/stroke roles, or sanitized master/layout relationships.

The current body profiler reduces objects primarily to `text_region`, `picture`, `table_or_chart`, and `line` bounding boxes. Candidate classification is effectively `photo_schematic` whenever a slide has a picture plus text; otherwise `other_insufficient_structural_evidence`. It does not yet provide enough evidence for the approved Figure Skill / VisualStyleGovernor calibration work, including grouped-object structure, primitive type, arrow direction/endpoints, panel/matrix structure, comparison symmetry, red-callout geometry, caption-region geometry, annotation density, dominant-figure ratio, photo/schematic relation, whitespace/gutter, or permitted font/color/line roles.

The constant shell safe bounds must not be presented as a measured private-derived descriptor.

Required correction:

- extract data-minimized but actually measured shell/body structural evidence sufficient for the next resolver;
- preserve sanitized IDs and no private content;
- distinguish `measured`, `derived`, and `not_observable_structurally` fields;
- do not invent/default professor measurements when the source was not measured;
- improve candidate-family structural classification beyond the current two-class heuristic, while allowing `insufficient_structural_evidence` when evidence is genuinely ambiguous.

## CP2-B2 — Nested sanitized descriptor contracts are not fail-closed

The committed shell schema currently types `shell_primitives` only as `{"type":"array"}`. The body schema similarly types `candidate_families` and `body_measurements` only as arrays. The runtime sanitizer allowlists only top-level keys and then deep-copies the nested structures.

Therefore an unapproved nested key/string can cross inside one of those approved top-level arrays without being rejected by schema or sanitizer. A generic private slide-text string that does not resemble a path/URL/canary is not guaranteed to be detected.

This violates the approved whitelist sanitizer requirement.

Required correction:

- fully type every committed nested descriptor object with `additionalProperties:false`;
- bound strings to controlled enums/IDs/approved font names only;
- reject arbitrary free text inside committed structural descriptors;
- validate the fully constructed sanitized object against the canonical schema before write;
- add recursive sanitizer/schema negative tests proving arbitrary nested text, notes-like strings, basename/path values, raw XML fragments, unexpected nested keys, and package-part identifiers cannot cross.

## CP2-B3 — Private source-session execution evidence must record start/outcome before source access

`open_read_only()` records an `open:<alias>` string in `alias_attempts`, while the structured `source_sessions` record is created only after successful profiling. This is not a sufficient owning event model for failed or partial private-source sessions.

Required correction:

- introduce structured source-session attempt records with sanitized session ID, alias, `started`, validation result, profiling result, and closed/outcome state;
- record the session start before `Path.is_file`, ZIP validation, hashing, or OOXML reads;
- a malformed/failed authorized source must remain visible in execution evidence;
- final authorized session count must be derived from successful closed sessions, while attempts/failures remain separately auditable;
- QA must reject inconsistent session attempt/result counts.

## CP2-B4 — `private_render_review()` may not fabricate a visual review lifecycle

When a provider passes preflight, the current method increments `private_renders_created` and `private_renders_deleted` and sets `reviewed_ephemerally` without performing an actual render, hash-bound image review, or deletion operation.

Checkpoint 2 production used the blocked provider path, so no private render was exposed; nevertheless this API is a certification bypass and must be corrected before later private visual review is authorized.

Required correction:

- provider preflight may only authorize a future render operation;
- `reviewed_ephemerally` requires actual render creation, render hash, image-capable review evidence, and confirmed deletion, all local-only;
- if those operations are not implemented/authorized, return `blocked_visual_review` or `not_run` and keep counters at zero;
- add a negative test proving provider capability alone cannot create review PASS/counters.

## CP2-B5 — Checkpoint QA must own descriptor-quality and sanitizer-boundary checks

The current aggregate QA can pass as long as three aliases were processed, access/privacy counters are clean, and pre-open gates passed. It does not establish that the committed descriptors contain the minimum structural evidence required by CP2 or that nested sanitizer/schema contracts are fully closed.

Required correction:

Add execution-derived owning checks for at least:

- shell structural descriptor completeness/measurement provenance;
- body structural descriptor completeness/measurement provenance;
- nested sanitizer/schema boundary;
- authority separation / shell contamination;
- descriptor source-count/slide-count consistency.

Checkpoint aggregate PASS must require these owning checks.

## Preserve

Do not regress:

- exactly three stable private aliases;
- no committed private paths/basenames/content;
- blob-bound legacy exception;
- repository/staged privacy scanning;
- production empirical Observation policy;
- read-only private source usage;
- zero private renders retained;
- private qualitative review currently `blocked_visual_review`;
- Exemplar 1/3 shell authority and Exemplar 2 body authority;
- no resolver/calibration/template reconstruction/acceptance deck yet;
- all Phase 1–2 and Checkpoint 1 accepted behavior.

## Reviewer decision

Checkpoint 2 is **not approved** for progression to the Professor Visual Grammar resolver/calibration checkpoint until CP2-B1 through CP2-B5 are corrected and remotely verified.
