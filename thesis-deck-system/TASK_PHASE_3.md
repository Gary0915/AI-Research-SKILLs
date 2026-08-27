# TASK — Phase 3

## Title

Professor Visual Fidelity Calibration + Private Template / Exemplar Integration

## Authorization

Phase 2 core architecture is approved.

Read first:

1. `thesis-deck-system/REVIEW_PROTOCOL.md`
2. `thesis-deck-system/reviews/PHASE_1_FINAL_REVIEW.md`
3. `thesis-deck-system/reviews/PHASE_2_FINAL_REVIEW.md`
4. `thesis-deck-system/reports/PHASE_2_IMPLEMENTATION_REPORT.md`
5. `thesis-deck-system/TASK_PHASE_2.md`
6. `thesis-deck-system/TASK_PHASE_2_REVISION_4.md`
7. this file

Do **not** alter the approved scientific/history architecture unless a concrete private-template incompatibility requires an adapter-level correction.

Do **not** start Phase 4.

Do **not** globally/publicly register Skills.

Do **not** claim production Group Meeting readiness unless every acceptance gate explicitly required below passes.

---

# 0. Phase 3 objective

Phase 1–2 proved the scientific/history/layout-engine mechanics with synthetic fixtures.

Phase 3 must answer a different question:

> Does the generated deck actually look and behave like the professor's preferred presentation system?

The authoritative style roles are:

- **Exemplar 1**: formal shell / template / Master reference; Hypothesis and research-history presentation may be secondary references.
- **Exemplar 2**: **primary body-content composition and scientific-figure layout reference**.
- **Exemplar 3**: formal shell / template / Master reference.

Final rule:

`MASTER / SHELL / TEMPLATE = Exemplar 1 + Exemplar 3`

`BODY CONTENT COMPOSITION = primarily Exemplar 2`

`RESEARCH STORY = approved Hypothesis-Layer + Scientific Method architecture`

The current synthetic `visual-grammar.json` is NOT professor-fidelity evidence.

---

# 1. Private fixture aliases

Support these authoritative aliases:

- `private://template_primary_1`
- `private://layout_exemplar_2`
- `private://template_primary_3`

The user's local/private environment must map each alias to the actual PPTX file.

Do not commit the private PPTX files unless the user explicitly authorizes that.

Do not commit private scientific slide text, images, data, notes, author metadata, or laboratory-sensitive content.

If any required alias is unavailable:

- finish only non-private code that is independently implementable;
- set `private_fixture_acceptance: blocked_fixture`;
- do not fabricate measurements;
- do not claim professor visual fidelity;
- stop before production acceptance.

No silent fallback to synthetic fixtures is allowed when a private alias was explicitly requested.

---

# 2. Private-data handling contract

Create a strict sanitizer / profiler boundary.

Allowed committed information derived from private exemplar decks includes only non-sensitive structural/style descriptors needed to reproduce presentation style, such as:

- slide dimensions;
- slide Master/Layout IDs represented by sanitized local identities;
- relative geometry ratios;
- placeholder classes;
- font family names and sizes if permitted by the user environment;
- theme color values;
- line widths;
- corner radii;
- alignment patterns;
- recurring footer/header geometry;
- navigation-zone geometry;
- caption geometry;
- archetype classification;
- normalized spacing ratios;
- image/text area proportions;
- anonymized slide-role labels;
- numeric visual metrics.

Do NOT commit:

- private slide body text;
- private figure pixels;
- paper screenshots copied from private decks;
- experimental data;
- speaker notes;
- personal names unless structurally unavoidable and explicitly approved;
- full local filesystem paths.

All committed private-derived records must pass a privacy/sanitization QA scan.

---

# 3. Real native template profiling — Exemplar 1 + Exemplar 3

Profile the actual PPTX structures from Exemplar 1 and Exemplar 3.

Extract and compare at least:

## 3.1 Canvas and Master system

- slide width / height;
- Master count;
- Layout count;
- slide → Layout → Master relationships;
- title placeholders;
- body/content placeholders;
- footer placeholders;
- slide-number placeholders;
- date placeholders if present;
- section-divider layouts;
- notes-master relationships where relevant.

## 3.2 Formal visual shell

Measure and sanitize:

- title-zone position and size;
- top-left Roman numeral / chapter marker geometry if present;
- gray diagonal / angled chapter-label geometry if present;
- chapter-divider geometry;
- bottom navigation geometry;
- footer geometry;
- page-number geometry;
- AMPL/lab identifier geometry if structurally present and permitted;
- safe-content bounds;
- recurring alignment grid;
- margin system.

## 3.3 Typography

Extract:

- title font family;
- body font family;
- English/CJK fallback behavior;
- title sizes;
- body sizes;
- caption sizes;
- footer/page sizes;
- bold/regular usage;
- line spacing;
- paragraph spacing;
- bullet indentation;
- Chinese/English mixed-text behavior.

Do not hard-code a final type system until these real profiles exist.

## 3.4 Theme

Extract:

- theme colors;
- background colors;
- primary text colors;
- secondary gray tones;
- accent/red highlight colors;
- border colors;
- line widths;
- shape fills.

Produce sanitized profile artifacts for Exemplar 1 and Exemplar 3 plus a resolved professor-template profile.

---

# 4. Body-content reverse engineering — Exemplar 2

Exemplar 2 is the primary body-composition reference.

Do NOT reduce this to generic labels such as `two-column` or `image + text`.

For every useful reference slide, extract a normalized composition descriptor.

At minimum classify and measure examples for:

- observation / problem;
- experiment photo + schematic;
- control vs treatment / proposed;
- phenomenon / mechanism / solution;
- literature + mechanism;
- table + schematic;
- main image + small image matrix;
- EDS / OM / microscopy matrix;
- experiment setup;
- process flow;
- result single;
- result comparison;
- result + discussion;
- failure analysis;
- red-box take-home message;
- annotated physical-interface / arrow callout;
- progress / To-do if present.

For each reference composition record sanitized numeric metrics such as:

- title baseline;
- dominant visual bbox ratio;
- secondary visual bbox ratio;
- text-region bbox ratio;
- image:text area ratio;
- inter-column gap;
- top/bottom margins;
- caption position;
- annotation density;
- red-box position / size;
- table-to-diagram proportion;
- image matrix rows/columns;
- comparison-panel symmetry;
- alignment axes;
- whitespace fraction;
- visual-center location.

Also capture qualitative-but-sanitized rules:

- when arrows are used;
- when labels sit directly on physical interfaces;
- when red boxes are used;
- when captions use gray backgrounds;
- when Control/Treatment is horizontal;
- when a main image dominates over small images;
- when one page should be split.

Do not copy the private slide's scientific content.

---

# 5. Professor visual grammar V3

Replace the synthetic visual grammar with a calibrated professor grammar.

Produce a versioned committed artifact similar to:

`thesis-deck-system/profiles/professor-visual-grammar-v3.json`

It must identify provenance at the alias/deck-role level without private text.

Required sections:

- formal shell rules derived from Exemplar 1/3;
- body-composition rules derived primarily from Exemplar 2;
- typography tokens;
- spacing tokens;
- highlight tokens;
- caption tokens;
- comparison tokens;
- scientific annotation tokens;
- image matrix tokens;
- fishbone tokens;
- density ranges;
- do-not-use rules;
- archetype-to-reference-composition mapping.

Do not simply copy current synthetic A01–A18 coordinates into a new file.

The calibrated grammar must contain measured evidence from the private exemplar profiling step.

---

# 6. Archetype calibration

Keep the approved A01–A18 semantic archetype taxonomy unless real exemplar evidence justifies an extension.

Calibrate the actual geometry for at least:

- A01 hypothesis_title
- A02 problem_definition
- A03 fishbone_locator
- A04 observation_problem
- A05 literature_mechanism
- A07 photo_schematic
- A08 control_vs_proposed
- A09 experiment_design
- A10 result_single
- A11 result_comparison
- A12 image_matrix
- A14 layer_integrated_discussion
- A15 layer_summary_decision
- A16 hypothesis_transition
- A17 progress_todo
- A18 schedule_next_step

For every calibrated archetype persist:

- semantic role;
- preferred native Layout/Master role;
- slot geometry;
- slot hierarchy;
- visual-weight targets;
- typography tokens;
- border/fill/highlight tokens;
- caption tokens;
- minimum / maximum density;
- split thresholds;
- reference-composition descriptors;
- rationale.

Do not force all archetypes to look identical merely because they share the same Master.

---

# 7. Required professor-specific visual behaviors

The calibrated system must reproduce these project rules where supported by the exemplar analysis:

- white-background formal academic visual language;
- figure-first scientific pages;
- high information density with structure;
- one dominant problem/question per slide;
- real photos paired with simplified schematics when appropriate;
- horizontal Control / Treatment or Control / Proposed comparison;
- arrows/labels point directly to the physical interface or changed region;
- table + schematic, not spreadsheet-screenshot style;
- large main image + smaller image matrix where appropriate;
- red highlight box reserved for actual take-home interpretation;
- gray caption strip / caption treatment where supported by exemplar;
- microscopy / mapping figures readable at presentation scale;
- Result page dominated by evidence, with concise interpretation;
- Hypothesis and Problem always separate;
- historical Fishbone appears once per Hypothesis Layer and highlights the current branch;
- previous/failed layers remain visually reachable.

---

# 8. Fishbone visual calibration

Do not keep the synthetic fishbone style automatically.

Calibrate Fishbone / Thesis Research Map rendering to the professor's exemplar language while preserving the approved versioned hierarchy model.

Required behavior:

- fixed branch IDs;
- hierarchical parent-child geometry;
- stable positions across revisions where unchanged;
- CURRENT branch obvious within 3–5 seconds;
- completed/partial/failed/future states visibly distinct but not visually noisy;
- editable canonical SVG / Draw.io source;
- no generated-raster canonical source.

Use the formal template shell from Exemplar 1/3 around the Fishbone page.

---

# 9. Style-calibration acceptance corpus

Create a sanitized synthetic content corpus specifically designed to exercise the real professor visual grammar.

Do not use actual private scientific content.

The acceptance deck should contain at least these generated pages:

1. Progress / previous commitments
2. Hypothesis
3. Problem
4. Historical Fishbone
5. Observation + problem with image
6. Literature + mechanism
7. Photo + schematic
8. Control vs Proposed
9. Experiment Design
10. Result single
11. Result comparison
12. Image/microscopy matrix
13. Integrated Discussion
14. Summary / Decision
15. Hypothesis Transition
16. Next Step / Schedule

Use Traditional Chinese as the primary language with representative English technical terms.

Use realistic synthetic scientific density rather than lorem ipsum.

---

# 10. Reconstruction benchmark against exemplar geometry

For each selected private exemplar reference slide, perform a local-only reconstruction benchmark.

The benchmark should compare the private reference composition and the system-generated sanitized reconstruction at the geometry/style level.

Where private pixels cannot be committed, persist only sanitized metrics and hashes.

Measure where practical:

- title-zone delta;
- content-bound delta;
- dominant-visual bbox delta;
- image:text ratio delta;
- panel alignment delta;
- margin delta;
- caption delta;
- highlight-box delta;
- font-size delta;
- line-width delta;
- color-distance delta;
- whitespace fraction delta.

Define acceptance tolerances per metric.

Do not use one global pixel similarity score as the sole criterion.

---

# 11. Image-capable visual review

The final Phase 3 professor-fidelity verdict must include actual image-capable review of:

- private reference renders locally;
- sanitized system reconstructions;
- final acceptance deck renders.

The reviewer must judge slide-specific issues such as:

- does it visually resemble the professor's established body composition?
- is the hierarchy equivalent?
- is the page too sparse or too dense relative to the exemplar?
- is the figure dominant enough?
- are arrows/callouts located appropriately?
- is the red-box emphasis overused or underused?
- is Control/Proposed comparison balanced?
- is the Fishbone location immediately obvious?
- does Traditional Chinese wrap correctly?

If no image-capable review can be executed in the environment, mark:

`professor_visual_review: blocked_environment`

Do not manufacture PASS from metadata.

---

# 12. Template preservation acceptance

Using the real private template shell, prove:

- generated slides preserve native slide → Layout → Master relationships;
- recurring footer/page-number/navigation objects remain correct;
- title positions match calibrated template bounds;
- no unexpected synthetic-template object remains;
- no private scientific content leaks into generated acceptance slides;
- PPTX remains editable;
- SVG scientific assets remain relationship-bound to owning slides;
- notes provenance remains correct.

If native Microsoft PowerPoint remains unavailable, keep Stage 8 blocked.

LibreOffice is compatibility evidence only.

---

# 13. Visual QA V3

Add professor-calibrated visual checks.

Separate:

1. structural geometry QA
2. render-pixel QA
3. exemplar-calibration metric QA
4. qualitative image-capable professor visual review

Required automated evidence should include at least:

- slot geometry against calibrated archetype;
- title bounds;
- safe-content bounds;
- minimum font;
- Chinese wrapping / overflow;
- image/text ratio;
- dominant visual ratio;
- comparison symmetry;
- edge/clipping proximity;
- whitespace fraction;
- caption size/placement;
- highlight-box frequency;
- line/arrow visibility proxies;
- visual-density bounds.

Professor-style PASS must consume the calibrated grammar, not synthetic defaults.

---

# 14. Skill routing calibration

Update the repo-local Skills so they understand the professor-calibrated visual system.

At minimum update:

- `thesis-deck-router`
- `hypothesis-layer-planner`
- `fishbone-director`
- `layout-director`
- `professor-qa`

The Skills should route to the calibrated professor visual grammar/profile rather than hard-coded synthetic geometry.

Do not globally install/register them yet.

---

# 15. Phase 3 required artifacts

Where privacy permits, commit sanitized artifacts such as:

- `profiles/template-primary-1.sanitized.json`
- `profiles/template-primary-3.sanitized.json`
- `profiles/layout-exemplar-2.sanitized.json`
- `profiles/professor-template-resolved.json`
- `profiles/professor-visual-grammar-v3.json`
- archetype calibration records
- private-fixture acceptance status
- sanitizer QA
- exemplar-metric calibration report
- acceptance Slide Specs
- calibrated Layout Plans
- acceptance Deck Manifest
- acceptance PPTX generated with the private shell if permitted locally
- structural audit
- render-pixel QA
- professor visual QA
- visual review summary
- implementation report

Do not commit local-only private renders if that violates fixture policy.

A local-only evidence manifest may use private aliases + hashes instead of paths.

---

# 16. Required tests

Add positive and negative tests for at least:

1. missing requested private alias fails instead of synthetic fallback;
2. sanitized profiler contains no private slide text;
3. sanitized profiler contains no absolute private paths;
4. Exemplar 1/3 shell resolver selects the expected Master/Layout identities;
5. Exemplar 2 body-composition descriptor extraction succeeds;
6. calibrated archetype differs from the old synthetic geometry where exemplar evidence differs;
7. title-zone tolerance test;
8. safe-content-bound tolerance test;
9. Control/Proposed symmetry test;
10. dominant-visual-ratio test;
11. image-matrix geometry test;
12. red-highlight governance test;
13. Fishbone current-focus visibility test;
14. Traditional Chinese wrapping/overflow test;
15. private-content leakage negative test;
16. wrong template Layout/Master relationship negative test;
17. synthetic template object leakage negative test;
18. professor visual QA cannot PASS when private calibration is blocked;
19. professor visual QA cannot PASS when image-capable review is blocked;
20. all Phase 1–2 tests remain green.

---

# 17. Phase 3 acceptance states

Use explicit status dimensions.

## Core architecture

Already approved from Phase 2.

## Private fixture ingestion

One of:

- `pass`
- `blocked_fixture`
- `fail`

## Professor template fidelity

One of:

- `pass`
- `blocked_fixture`
- `fail`

## Professor body-layout fidelity

One of:

- `pass`
- `blocked_fixture`
- `fail`

## Professor visual review

One of:

- `pass`
- `blocked_environment`
- `fail`

## Native PowerPoint

One of:

- `pass`
- `blocked_environment`
- `fail`

## Production Group Meeting readiness

May be `pass` ONLY if all required professor/private/native gates defined by the reviewer are satisfied.

Do not infer readiness from unit tests alone.

---

# 18. Implementation report

Write:

`thesis-deck-system/reports/PHASE_3_IMPLEMENTATION_REPORT.md`

Traceability:

- P3-R1 private fixture ingestion/sanitization
- P3-R2 Exemplar 1/3 template profiling
- P3-R3 Exemplar 2 body-composition profiling
- P3-R4 professor visual grammar V3
- P3-R5 calibrated archetypes
- P3-R6 fishbone visual calibration
- P3-R7 reconstruction benchmark
- P3-R8 professor-calibrated visual QA
- P3-R9 private-template PPTX preservation
- P3-R10 skill-routing calibration
- P3-R11 Traditional Chinese typography
- P3-R12 production-readiness honesty

For every item include:

- implementation files;
- tests;
- local/private evidence status;
- committed sanitized evidence;
- limitations;
- verdict.

---

# 19. Final Codex response

Return:

```text
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

P3-R1–P3-R12 traceability:

private aliases:
- template_primary_1:
- layout_exemplar_2:
- template_primary_3:

sanitization QA:

Exemplar 1/3 template profiling:
Exemplar 2 body-layout profiling:
professor visual grammar:
calibrated archetypes:
fishbone calibration:

reconstruction benchmark:
- reference slides profiled:
- metric checks passed/failed:
- major deviations:

acceptance PPTX:
render paths:
montage paths:

professor template fidelity:
professor body-layout fidelity:
professor visual review:
Traditional Chinese QA:
native PowerPoint status:
production Group Meeting readiness:

known failures:
technical debt:
unresolved questions:

READY_FOR_REVIEW: yes
```

Only return `READY_FOR_REVIEW: yes` after the pushed remote implementation and all available evidence have been verified.

If private fixtures are unavailable, returning `READY_FOR_REVIEW: yes` is allowed only for a **blocked-fixture implementation review**, and the response must clearly state that professor visual fidelity was not accepted.

Then STOP.

Do not begin Phase 4.
