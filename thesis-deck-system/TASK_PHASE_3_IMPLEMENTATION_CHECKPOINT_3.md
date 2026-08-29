# TASK — Phase 3 Implementation Checkpoint 3

## Status

Authorized after approval of Phase 3 Checkpoint 2.

This checkpoint implements the **Professor Visual Grammar Resolver + Visual Style Governor calibration boundary only**.

It must consume committed sanitized CP2 descriptors and must not reopen the production private PPTX files.

## Authoritative inputs

Read completely before implementation:

1. `thesis-deck-system/reviews/PHASE_3_CHECKPOINT_2_FINAL_REVIEW.md`
2. `thesis-deck-system/designs/PHASE_3_VISUAL_FIDELITY_DESIGN.md`
3. `thesis-deck-system/plans/PHASE_3_TDD_IMPLEMENTATION_PLAN.md`
4. `thesis-deck-system/reviews/PHASE_3_DESIGN_FINAL_REVIEW.md`
5. `thesis-deck-system/reports/PHASE_3_CHECKPOINT_2_IMPLEMENTATION_REPORT.md`
6. `thesis-deck-system/REVIEW_PROTOCOL.md`

Canonical committed structural inputs:

- `thesis-deck-system/artifacts/phase3/sanitized-exemplar-manifest.json`
- `thesis-deck-system/artifacts/phase3/sanitized-shell-structural-descriptors.json`
- `thesis-deck-system/artifacts/phase3/sanitized-body-structural-descriptors.json`
- `thesis-deck-system/artifacts/phase3/checkpoint-2-qa.json`

## Critical access boundary

Checkpoint 3 is a **sanitized-domain-only checkpoint**.

Do NOT:

- resolve production private aliases to local paths;
- reopen any private PPTX;
- hash any production private PPTX again;
- render any private exemplar;
- inspect ignored raw CP2 profiles;
- use local private screenshots;
- use private text/notes/media;
- infer style from any source outside committed sanitized CP2 artifacts.

Checkpoint 3 execution evidence must prove:

- production private alias resolution attempts = 0
- production private source open attempts = 0
- private render attempts = 0

If any such attempt occurs, Checkpoint 3 fails.

---

# CP3-1 — Canonical resolver contracts

Implement strongly typed, fail-closed contracts/schemas for at least:

1. resolved professor shell/template profile;
2. body-composition grammar profile;
3. Professor Visual Grammar V3;
4. Visual Style Governor profile/tokens;
5. resolver conflict records;
6. resolver evidence / rule-decision records;
7. Checkpoint 3 QA / report-facts object.

Suggested committed outputs:

- `thesis-deck-system/artifacts/phase3/professor-template-resolved.json`
- `thesis-deck-system/artifacts/phase3/body-composition-profile.json`
- `thesis-deck-system/artifacts/phase3/professor-visual-grammar-v3.json`
- `thesis-deck-system/artifacts/phase3/visual-style-profile.json`
- `thesis-deck-system/artifacts/phase3/resolver-evidence.json`
- `thesis-deck-system/artifacts/phase3/checkpoint-3-qa.json`

Equivalent names are acceptable only if traceability remains explicit.

All nested objects must be strongly typed with `additionalProperties: false`.

No free-form private-derived text is allowed.

---

# CP3-2 — Fixed asymmetric exemplar authority

The resolver MUST enforce the design's fixed authority matrix.

## Exemplar 1 — content/formal working shell

`P3-TEMPLATE-PRIMARY-1` governs:

- working canvas when compatible with overall shell;
- content-slide master/layout topology;
- content-page title grid;
- formal academic content shell;
- Hypothesis/research-history shell motifs;
- content/Hypothesis typography role evidence.

## Exemplar 3 — defense/formal hierarchy shell

`P3-TEMPLATE-PRIMARY-3` governs:

- cover/title-page treatment;
- chapter/section divider treatment;
- footer;
- page number;
- navigation grammar;
- defense-style formal hierarchy;
- cover/divider/footer typography role evidence.

## Exemplar 2 — body and scientific composition only

`P3-LAYOUT-EXEMPLAR-2` governs:

- body composition;
- scientific figure dominance;
- figure/text ratios;
- comparisons;
- matrices;
- annotations/callouts;
- caption/body scale ratios;
- body density;
- whitespace/gutters;
- panel structure;
- scientific-figure composition grammar.

Exemplar 2 MUST NOT write or override:

- master identity;
- shell canvas authority;
- formal title shell;
- footer;
- page number;
- navigation;
- cover/divider shell.

Add hard negative tests proving shell contamination fails.

---

# CP3-3 — Evidence tiers and non-overclaiming

Every resolved grammar/token must carry an evidence tier from a controlled enum:

- `recurring_pattern`
- `single_example_provisional`
- `indirect_supported`
- `insufficient_evidence`

At minimum record:

- resolved token/rule ID;
- source exemplar role;
- source profile ID;
- supporting sanitized descriptor IDs/object/measurement IDs;
- supporting descriptor/container count;
- evidence tier;
- confidence/status;
- resolver rule ID;
- authority family.

## Recurring-pattern minimum

A single slide/descriptor MUST NOT become `recurring_pattern` merely because it is structurally supported.

For slide/body composition grammar, `recurring_pattern` requires at least two independent supporting descriptors from the authorized source family unless a stronger explicit recurring structure exists (for example a recurring Master/Layout shell structure).

One structurally supported descriptor is at most:

`single_example_provisional`.

A source classification already marked `provisional` cannot be upgraded to `recurring_pattern` without additional independent support.

Unreferenced theme existence never counts toward recurrence.

---

# CP3-4 — Shell resolver and conflict governance

Implement the design's shell resolver and conflict rules.

## Required token-family rules

1. Canvas/aspect ratio:
   - verify compatible shell evidence;
   - no arithmetic averaging of incompatible canvases;
   - incompatible canvas is a blocking conflict.

2. Safe content bounds:
   - use geometric intersection only when both shell exemplars contain compatible defensible bounds;
   - empty or impractically small intersection = blocking conflict;
   - if evidence is missing, mark `insufficient_evidence`; do not invent bounds.

3. Content-page title geometry:
   - Exemplar 1 authority.

4. Cover/divider title geometry:
   - Exemplar 3 authority.

5. Footer/page-number/navigation:
   - Exemplar 3 authority;
   - Exemplar 1 fallback only when the equivalent token is absent in Exemplar 3 and the fallback is explicitly recorded.

6. Hypothesis/history shell motifs:
   - Exemplar 1 authority.

7. Typography:
   - content/Hypothesis roles from Exemplar 1;
   - cover/divider/footer roles from Exemplar 3;
   - body/caption scale ratios from Exemplar 2 only as body evidence constrained by shell hierarchy.

8. Theme/colors:
   - semantic role mapping only;
   - never average/blend conflicting colors into a new professor color;
   - preserve distinct semantic role tokens when sources disagree.

## Conflict record

Every competing shell token must produce an auditable record containing equivalent fields:

- conflict_id;
- token_family;
- selected_value;
- winning_profile_id;
- winning_source_role;
- losing_alternative(s);
- losing_profile_id(s);
- conflict_rule_id;
- conflict_classification = `soft_resolved | hard_blocking`;
- evidence tier/status.

No unordered-set/dictionary iteration may decide a winner.

Unmapped conflict = hard failure.

---

# CP3-5 — Theme and typography authority truth

Resolver inputs must respect CP2 truth exactly.

## Themes

Only theme profiles with:

- `usage_state = referenced`
- `authority_state = active_professor_style`

may contribute active Professor Visual Grammar.

`unreferenced / reference_only` themes may be retained only as audit evidence and MUST NOT influence resolved color/font tokens.

Theme identity must remain descriptor-qualified:

`(profile_id, theme_profile_id)`.

Never globally merge all local `T001` values.

## Typography

The following MUST NOT become professor font-family preferences:

- `script_role = unspecified`
- `font_evidence_state = inherited_unresolved`
- `family = unknown`

Supplemental theme font mappings are reference metadata; they do not prove run-level use.

An exact font family may become a resolved token only when supported by allowable explicit/resolved evidence and the correct source authority.

If typography evidence is insufficient, preserve:

`insufficient_evidence`

rather than selecting a convenient default and labeling it professor-derived.

Fallback fonts used later for technical rendering must be distinctly labeled `implementation_fallback`, not professor preference.

---

# CP3-6 — Body-composition grammar resolver

Resolve Exemplar 2 structural evidence conservatively.

The resolver may produce grammar for families only when supported by sanitized CP2 evidence, including where available:

- photo + schematic;
- Control vs Proposed/Treatment;
- result single;
- result comparison;
- result + discussion;
- image matrix;
- experiment schematic;
- fabrication/process flow;
- Fishbone/research map;
- figure-first scientific pages;
- high-density annotation/callout composition.

Do NOT invent a family that CP2 cannot structurally support.

## Range model

When multiple independently supported descriptors exist for one family:

preserve:

- bounded observed range;
- median/robust central tendency where useful;
- preferred/medoid sanitized descriptor ID;
- outlier IDs;
- sample count;
- evidence tier.

Do NOT collapse all observations to one unconstrained average.

## Metric truth

Unavailable CP2 metrics remain unavailable.

Do not convert `null / unavailable` to 0.

Do not impute missing comparison symmetry, caption, matrix, photo/schematic or annotation metrics and call them professor-derived.

---

# CP3-7 — Figure grammar structural layer

Create a resolver-facing structural `figure_grammar` section for later specialist Skills.

Allowed structural grammar may include only evidence-backed generic properties such as:

- primitive-language recurrence;
- connector/arrow geometry classes;
- line-width ranges;
- general accent/red-emphasis recurrence;
- panel/matrix spacing;
- comparison geometry;
- annotation density;
- figure/text dominance;
- photo/vector spatial relation;
- callout geometry;
- caption-region geometry where supported.

Do NOT infer private scientific semantics from geometry.

Specifically, do NOT create professor-derived material tokens such as:

- hydrogel color;
- electrode color;
- heater color;
- sensor color;
- contact-interface color;

unless later scientific-content-aware evidence explicitly supports them.

Those semantic material tokens should remain unresolved/default-unassigned at this checkpoint.

Fishbone style must also remain `insufficient_evidence` or provisional unless CP2 supplies structurally adequate direct evidence. Do not fabricate a recurring Fishbone grammar from a weak/provisional family classification.

---

# CP3-8 — Visual Style Governor profile

Implement a repo-local Visual Style Governor data layer/profile, not yet full figure production.

It should expose reusable controlled tokens derived from Professor Visual Grammar, such as:

## Shell tokens

- canvas;
- content title region;
- cover/divider title region;
- footer/page-number/navigation region;
- content bounds/alignment grid where supported;
- active shell colors;
- formal typography roles where supported.

## Generic scientific-visual tokens

- generic line widths;
- generic arrow/connector visual roles;
- accent/emphasis roles;
- red callout role where supported;
- panel gutter/spacing;
- caption/body scale ratio where supported;
- figure/text dominance ranges;
- matrix spacing.

Every token must include provenance/evidence tier.

No arbitrary hard-coded value may be labeled professor-derived.

A practical fallback may exist only if clearly separated:

- `professor_derived`
- `phase2_fallback`
- `implementation_fallback`
- `unresolved`

Fallback values do not count toward professor-fidelity coverage.

---

# CP3-9 — Resolver determinism and mutation tests

Add RED tests proving at minimum:

1. Exemplar 2 cannot alter shell/footer/navigation tokens.
2. Exemplar 1 cannot silently replace Exemplar 3 cover/divider authority.
3. competing Exemplar 1/3 shell measurements generate conflict evidence.
4. unmapped hard conflict blocks output.
5. source input ordering does not change resolved output.
6. one descriptor cannot become recurring body grammar.
7. two independent compatible descriptors may become recurring grammar.
8. provisional source evidence cannot auto-upgrade to recurring.
9. unreferenced theme cannot become active grammar.
10. supplemental theme font cannot become run-level font preference.
11. unspecified/inherited font cannot become professor font preference.
12. local `T001` collisions across descriptors remain isolated.
13. unavailable metric remains unavailable.
14. body metric mutation changes only the dependent grammar token/range.
15. shell descriptor mutation cannot mutate body-only grammar families unless a documented cross-constraint exists.
16. body descriptor mutation cannot mutate formal shell token values.
17. color conflict is not numerically blended.
18. material-specific semantic colors are not inferred from generic structural color evidence.
19. single provisional Fishbone evidence cannot become recurring Fishbone grammar.
20. fallback value cannot increase professor-derived calibration coverage.

---

# CP3-10 — Status model and honesty

Checkpoint 3 must report separate statuses at minimum:

- `private_exemplar_ingestion`
- `sanitized_structural_evidence`
- `shell_resolver_status`
- `body_composition_resolver_status`
- `figure_grammar_structural_status`
- `visual_style_governor_status`
- `professor_visual_grammar_structural_status`
- `private_qualitative_visual_review`
- `acceptance_deck_visual_fidelity`
- `archetype_library_calibration_coverage`
- `native_powerpoint_acceptance`
- `production_group_meeting_ready`

At Checkpoint 3:

- private ingestion may remain `pass` from CP2;
- structural resolver statuses may pass if all owning checks pass;
- private qualitative visual review remains `blocked_visual_review`;
- acceptance-deck fidelity = `not_run`;
- A01–A18 calibration = `not_run`;
- native PowerPoint acceptance = `not_run`;
- production readiness = `false`.

Do NOT emit global `professor_visual_fidelity = pass` from structural resolution alone.

---

# CP3-11 — Execution-derived QA

Create a Checkpoint 3 execution-evidence object and derive final QA from owning checks.

Required owning QA includes at least:

- CP2 input artifact/schema/hash validation;
- exact three exemplar profile identities;
- no private-access attempts;
- asymmetric source authority;
- shell contamination prevention;
- conflict completeness;
- hard-conflict behavior;
- evidence-tier correctness;
- recurring-pattern minimum support;
- active-theme-only authority;
- descriptor-local theme identity;
- unresolved typography exclusion;
- supplemental font authority exclusion;
- body range/sample-count reconciliation;
- unavailable metric preservation;
- Figure grammar semantic non-invention;
- Visual Style Governor provenance coverage;
- fallback/professor-derived separation;
- deterministic resolver output;
- privacy scan;
- schema closure;
- Phase 1–2 + CP1/CP2 regression.

No QA status may be literalized without owning evidence.

---

# CP3-12 — Privacy

Checkpoint 3 consumes only sanitized committed artifacts.

Still run repository/staged privacy scanning.

No committed artifact may contain:

- actual private source path;
- private source basename;
- slide text;
- notes;
- URLs/DOIs from private sources;
- media names;
- private screenshots/renders;
- private OOXML/package names;
- raw local profile references.

Do not add new legacy privacy exceptions without reviewer authorization.

---

# Not authorized in Checkpoint 3

Do NOT implement or generate:

- A01–A18 production calibration;
- reconstructed native professor template;
- PPTX output;
- reconstruction benchmark slides;
- scientific plots/figures for production;
- full Figure Router production routing;
- Mechanism Diagram production renderer;
- Experiment Schematic production renderer;
- Fabrication Process production renderer;
- Photo Annotation production workflow;
- Literature Figure production workflow;
- Concept image generation;
- Fishbone production-style calibration beyond evidence-status resolution;
- acceptance deck;
- Phase 4;
- public/global Skill registration.

`PythonPptxAssembler` remains untouched except for regression compatibility; no second backend is permitted.

---

# TDD and validation

Follow RED → GREEN.

Run at minimum:

1. focused Checkpoint 3 tests;
2. CP1 + CP2 + CP3 tests;
3. complete Phase 1–2 + CP1 + CP2 + CP3 regression in a disposable detached worktree;
4. input CP2 artifact/schema validation;
5. all new Phase 3 schema + `FormatChecker` validation;
6. recursive `additionalProperties:false` audit;
7. resolver determinism/mutation tests;
8. conflict-record consistency QA;
9. evidence-tier/sample-count QA;
10. source-authority contamination tests;
11. theme/font authority tests;
12. Visual Style Governor provenance coverage;
13. repository/staged privacy scan;
14. `git diff --check`;
15. remote branch/artifact verification.

If the full regression regenerates unrelated historical artifacts, use the already-approved disposable-worktree discipline. Do not widen cleanup authorization silently.

---

# Report

Create:

`thesis-deck-system/reports/PHASE_3_CHECKPOINT_3_IMPLEMENTATION_REPORT.md`

Include explicit CP3-1 through CP3-12 traceability.

Report at minimum:

- resolved shell token count by authority/evidence tier;
- shell conflict count: soft/hard;
- body grammar families resolved/provisional/insufficient;
- recurring body patterns vs single-example provisional patterns;
- active vs reference-only theme inputs consumed;
- resolved vs unresolved typography token counts;
- Figure grammar structural token count by evidence tier;
- Visual Style Governor professor-derived/fallback/unresolved token counts;
- private-access attempt counts;
- all separate final status dimensions;
- known failures/blocked states.

---

# Delivery

Commit and push authorized Checkpoint 3 work to:

`origin/codex/thesis-deck-system`

Verify the remote branch head and required artifact blobs.

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

CP3-1 through CP3-12 traceability:

private alias resolution attempts:
private source open attempts:
private render attempts:

resolved shell tokens by evidence tier:
shell conflicts soft/hard:
body grammar family summary:
recurring vs provisional body patterns:
active/reference-only themes consumed:
typography resolved/unresolved summary:
figure grammar structural summary:
Visual Style Governor token summary:

shell resolver status:
body composition resolver status:
figure grammar structural status:
Visual Style Governor status:
private qualitative visual review:
acceptance deck visual fidelity:
archetype library calibration coverage:
native PowerPoint acceptance:
production Group Meeting ready:

known failures:
technical debt:
unresolved questions:

READY_FOR_CHECKPOINT_3_REVIEW: yes

Only write `READY_FOR_CHECKPOINT_3_REVIEW: yes` after push and remote verification.

Then STOP.

Do not begin A01–A18 calibration, Figure Skill production, template reconstruction, or the acceptance deck.
