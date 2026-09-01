# Latest High-Priority Body Composition and Incremental Deck Analysis

Date: 2026-09-01

Baseline production commit reviewed: `94060296906ad91dd34fac8495578a383e87c26d`

## 1. Purpose and source boundary

This analysis adds a new evidence layer for the Thesis Deck System: recent user-supplied presentation lineages that demonstrate both (a) body composition and (b) how a research deck grows over time.

The raw PDF/PPTX binaries are **not committed**. They remain local/user-supplied reference material. Only sanitized structural observations, temporal recurrence, page-family mappings, and controlled body-composition findings are recorded here.

Sanitized source IDs used in this document:

- `JDP-TSMC-2026-0525` — 8-slide early report.
- `JDP-TSMC-2026-0604` — 13-slide expanded report; PDF and PPTX supplied.
- `JDP-TSMC-2026-0617` — 6-slide focused meeting report.
- `JDP-TSMC-2026-0730` — 13-slide later report; PDF and PPTX supplied.
- `JDP-TSMC-2026-0814` — 15-slide latest report; PDF and PPTX supplied.

These exemplars are **not shell/template authority**. The current thesis sanitized template / professor shell remains authoritative for canvas, background, master/layout shell, footer, and shell-level style. These exemplars are high-priority evidence only for body composition, evidence placement, information density, figure/caption grammar, and incremental deck behavior.

## 2. Central finding: this is a deck lineage, not independent decks

The strongest longitudinal pattern is cumulative research storytelling.

Observed sequence:

```text
2026-05-25: 8 slides
problem framing → two technical directions → early principle / observation

2026-06-04: 13 slides
retains early core + adds checkpoint, deeper principle, preliminary experiment,
preliminary result, planning, references

2026-06-17: 6 slides
focused meeting view: common context + currently active laser-tilt topic + next plan

2026-07-30: 13 slides
focused topic grows into literature → method → safety threshold → principle →
feasibility → formal platform → physical platform → precision improvement → next step

2026-08-14: 15 slides
large portions of 07-30 remain stable; new production-line blueprint and new
triangulation validation evidence are inserted at semantically appropriate locations
```

This confirms the intended Thesis Deck behavior:

> A canonical research deck grows with the research. Previously accepted material is reused when its scientific dependencies are unchanged. New material is inserted after its semantic parent. Current-state maps/plans may create a new revision. A meeting deck may be a focused view without deleting canonical history.

## 3. Longitudinal recurrence evidence

### 3.1 Stable body families retained across versions

High-confidence recurrent families include:

1. `BODY-TEXT-TOP-DUAL-VISUAL`
   - concise explanatory text in the upper body;
   - two large technical visuals beneath or beside it;
   - light neutral caption strips below images.

2. `BODY-PRINCIPLE-EQUIPMENT-SPLIT`
   - equipment/specification evidence on one side;
   - geometric principle, equation, and definitions on the other;
   - multiple controlled evidence regions rather than decorative cards.

3. `BODY-FEASIBILITY-EVIDENCE-MATRIX`
   - short numbered explanation plus a 2×2-ish matrix of setup photo, hardware arrangement, live/3D output, or measurement result;
   - evidence-heavy composition; captions identify each visual.

4. `BODY-HARDWARE-DESIGN-PROCEDURE`
   - dominant CAD/hardware visual;
   - experiment purpose, specifications, and procedure in a structured text block.

5. `BODY-PHYSICAL-VALIDATION-MATRIX`
   - real apparatus photo(s) on the left/center;
   - plot(s) / system feedback on the right;
   - evidence labels/captions directly attached to the visual rather than separated in a legend-only structure.

6. `BODY-TECHNOLOGY-COMPARISON`
   - two technical approaches presented as a structured comparison;
   - quantitative table plus mechanism schematics;
   - explicit limitation / reason for switching strategy.

7. `BODY-PROBLEM-TO-SOLUTION`
   - existing-method limitations in the upper body;
   - proposed method and simplified measurement geometry in the lower body;
   - accent color used for semantic emphasis, not decoration.

8. `BODY-REAL-RESULT-VALIDATION`
   - setup geometry / physical hardware;
   - measured resolution or performance values;
   - real photograph / UI / geometry result / time-series evidence in the same slide;
   - the slide tells a measurement chain rather than only showing one chart.

### 3.2 Strong same-family temporal recurrence

The most useful repeated slide families are:

- ToF principle/equipment: `0617 p4 → 0730 p8 → 0814 p9`.
- Preliminary tilt feasibility: `0617 p5 → 0730 p9 → 0814 p10`.
- Tilt platform design: `0730 p10 → 0814 p11`.
- Physical platform/feedback evidence: `0730 p11 → 0814 p12`.
- Precision-improvement comparison: `0730 p12 → 0814 p13`.

These are higher-confidence layout evidence than one-off synthetic archetype examples because the same research team continued using them across later decks.

## 4. Body visual grammar

### 4.1 Information density

The exemplars are not minimalist commercial decks. They are structured engineering progress slides with relatively high information density.

Preferred body behavior:

- multiple evidence items on one slide are acceptable;
- every evidence item should have a clear role;
- a slide can combine text, photo, CAD, equation, table, and plot when they form one scientific argument;
- density is acceptable when alignment and hierarchy remain clear.

This matches the existing advisor-preference analysis: the target is structured high-density scientific communication, not large-empty-space minimalism.

### 4.2 Image/figure dominance

A recurring pattern is figure-led explanation:

- real photographs occupy large visual regions;
- technical drawings and CAD are often primary evidence;
- equations are paired with geometry diagrams rather than isolated text;
- literature slides prioritize published figures and small citations over long abstract summaries;
- result/validation slides show setup → output → interpretation in one visual chain.

### 4.3 Captions

Light neutral caption strips directly under images are highly recurrent. They should be treated as a body-composition grammar element, not a one-off style feature.

Recommended controlled role:

`evidence_caption`

Properties:

- directly attached to its image/figure;
- short, object-specific label;
- low visual salience relative to title/takeaway;
- neutral fill; no decorative card treatment.

### 4.4 Accent semantics

Color is restrained:

- black/white dominate;
- red is the main attention/accent color;
- light gray and soft pink are used as neutral grouping/highlight aids;
- green/red may encode Pass/No-Pass semantics;
- blue is often measurement/technical geometry rather than a decorative palette.

The system should model accent as a semantic role. It should not copy the source deck's exact shell colors into the thesis template.

### 4.5 Red outlines and callouts

Red outlines are frequently used for:

- current focus;
- enlarged detail;
- critical physical interference;
- important result region.

They are not generic panel borders. Treat them as `focus_annotation` / `critical_callout`.

### 4.6 Arrow hierarchy

Observed convention:

- heavy black arrows: process / causality / major flow;
- red arrows: warning / critical location / emphasized transition;
- dashed or thin reference lines: measurement geometry, alignment, reference axes.

This is more informative than a single generic connector style.

## 5. Incremental deck behavior

### 5.1 Not simply append-to-end

New content is often inserted after its semantic parent.

Example pattern:

```text
literature limitations
→ proposed solution
→ NEW production-line application blueprint
→ safety threshold / measurement requirement
```

Likewise, new precision-validation results belong after the precision-improvement method, before future planning.

Required behavior:

`APPEND_AFTER_SEMANTIC_PARENT`

not merely:

`APPEND_TO_END`.

### 5.2 Historical stable content

When upstream scientific dependencies are unchanged, completed literature, experiment setup, feasibility evidence, physical platform, and prior results should be reused instead of reauthored.

### 5.3 Versioned current-state slides

Fishbone is not the only versioned family. Other likely versioned snapshots include:

- research map / system blueprint;
- current integrated summary;
- future plan / schedule;
- progress roadmap;
- threshold/evaluation overview when authoritative dimensions or limits change.

A new snapshot does not erase historical truth.

### 5.4 Meeting view vs canonical master deck

The short 06-17 deck demonstrates that a meeting export may show:

- common context;
- current active topic;
- latest evidence;
- next plan;

without implying that omitted historical slides were deleted from the canonical research deck.

The architecture should distinguish:

`CanonicalResearchDeck`

from:

`MeetingDeckView`.

## 6. Critical dependency lesson from the lineage

A later threshold/evaluation slide demonstrates a classic incremental-update hazard: some geometry/table values were updated to a newer wafer-box specification and an approximately 1.88° calculation, while retained explanatory text still referenced earlier 1.04° / 1.06° limits.

This is valuable evidence for the Thesis Deck System:

> Reuse is allowed only while dependencies are unchanged. If an upstream scientific dependency changes, all dependent visible fields/figures/equations/summary annotations must be invalidated together.

Therefore the correct rule is not "old slides never change". It is:

```text
unchanged dependency hash → reuse accepted slide
new child evidence → append after semantic parent
versioned current-state object changed → create new snapshot revision
upstream scientific dependency changed → rebuild dependent slide atomically
```

This dependency-aware behavior is essential to prevent stale mixed-state slides.

## 7. Reference authority model

### 7.1 Shell authority

Highest authority remains the existing sanitized thesis/professor shell for:

- slide size;
- background;
- master/layout shell;
- footer/header;
- shell typography/color roles;
- template topology.

The JDP/TSMC shell is not to be copied.

### 7.2 Body-composition authority

For body layout/composition only, recommended priority is:

1. `JDP-TSMC-2026-0814` — latest/highest priority.
2. `JDP-TSMC-2026-0730` — very high; strong direct predecessor to 08-14.
3. `JDP-TSMC-2026-0617` — high for focused experimental/laser-layout families.
4. `JDP-TSMC-2026-0604` — high for principle / imaging / preliminary experiment families.
5. `JDP-TSMC-2026-0525` — supporting historical evidence for early technical layout families.

Recency does not delete an older unique archetype. It only resolves conflicts within the same recurrent body family.

### 7.3 Scientific truth authority

Scientific content remains:

```text
canonical scientific objects
→ append-only Ledger
→ cursor materialization
→ SlideSpec
→ presentation semantic projection
```

No reference deck may override scientific truth.

## 8. Implications for current Phase 3 implementation

The current `PHASE_3_FINAL_VISUAL_COMPOSITION_CLOSURE_DESIGN` already establishes source-bound projection and governed figure placement. The missing addition is temporal deck lineage and body-reference authority.

The current A01–A18 calibration is still provisional structural evidence. The new reference set should not blindly replace A01–A18. Instead:

- retain archetype identity/contract;
- attach newer body-composition evidence to appropriate families;
- calibrate normalized body regions and evidence capacity from recurring latest exemplars;
- preserve shell authority from the thesis template;
- use recency only within equivalent body-composition families.

## 9. Minimum implementation target before final deck review

Do not build a full general-purpose BuildGraph now. Implement a narrow incremental contract sufficient for real research usage:

- stable slide identity;
- topic identity;
- semantic parent;
- lifecycle policy;
- source cursor;
- dependency hash;
- composition family;
- body-reference evidence ID;
- artifact hash;
- reuse/rebuild/new-revision decision;
- canonical master ordering;
- meeting-view selection.

Required lifecycle states should cover at least:

- `historical_stable`;
- `append_after_semantic_parent`;
- `versioned_snapshot`.

Required materialization decisions should cover at least:

- `reuse_exact`;
- `append_new`;
- `new_revision`;
- `rebuild_dependency_changed`;
- `exclude_from_meeting_view_only`.

## 10. Final design principle

The system should optimize for this research workflow:

> Build a research block once, preserve it when its evidence remains valid, insert new evidence where it belongs scientifically, version changing research maps/plans, and export focused meeting views without deleting canonical history.

This is more faithful to the observed advisor/lab practice than regenerating an entire presentation from zero for every meeting.
